# tests/p5/test_p5_archive.py
"""E4 - §2.5. Done-means 7: "No archive fixture writes a byte outside the process,
and the bomb/protected/nested fixtures all terminate in a marked state."
"""
import zipfile
from pathlib import Path

import pytest

from extractors.archive import (
    ARCHIVE_TYPE_FIELD, ArchiveManifest, ArchiveMarker, ArchiveMember,
    EXTRACTOR_NAME, MARKER_KINDS, UNCOMPRESSED_SIZE_FIELD, UnknownMarkerKind,
    extract_archive,
)
from extractors.safety import DatalessRefused, ProtectedContainerRefused, SafetyPolicy

from conftest import FIXED_CLOCK
from p4_stub import locator_for

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-zip", "content_hash": "be0cf129543c52347040cf761dcc995196f5a6a073c67e7bb336731a4c95ef50",
            "filename": "submission.zip"}

PACKET = ("transcript.pdf", "personal-statement.docx", "resume.pdf",
          "certificate.pdf", "form.pdf")


def a_submission_zip() -> ArchiveManifest:
    members = tuple(ArchiveMember(path=name, uncompressed_size=100)
                    for name in PACKET)
    return ArchiveManifest(archive_type="ZIP", members=members,
                           uncompressed_size=500, inspected=len(members),
                           total=len(members))


def no_markers(member_paths):
    return ()


def run_it(manifest=None, markers=no_markers, path=Path("/corpus/submission.zip")):
    calls = []

    def reader(target):
        calls.append(target)
        return manifest if manifest is not None else a_submission_zip()

    result = extract_archive(file_row=FILE_ROW, path=path, policy=OPEN_POLICY,
                             read_manifest=reader, recognize_markers=markers,
                             now=FIXED_CLOCK, context_window=20)
    return result, calls


def test_every_observation_conforms_to_p4s_shape(sink):
    result, _ = run_it()
    sink.write(result)
    sink.conforms()


def test_the_five_member_names_are_five_located_values(sink):
    # §2.5's own example: transcript, personal statement, resume, certificate, form.
    result, _ = run_it()
    run_id = sink.write(result)
    located = {o["raw_value"]: locator_for(o["location"])
               for o in sink.observations_for(run_id)
               if o["location"]["zone"] == "manifest"}
    for name in PACKET:
        assert located[name] == f"manifest:entry={name}#0-{len(name)}"


def test_p5_concludes_nothing_about_the_packet(sink):
    # "Application packet" is a fact (§3.2) and belongs to P6.
    result, _ = run_it()
    run_id = sink.write(result)
    values = " ".join(o["raw_value"] for o in sink.observations_for(run_id))
    assert "packet" not in values and "application" not in values.lower()


def test_the_archive_type_and_uncompressed_size_are_metadata(sink):
    result, _ = run_it()
    run_id = sink.write(result)
    slots = {o["location"]["container_path"][0]["label"]: o["raw_value"]
             for o in sink.observations_for(run_id)
             if o["location"]["zone"] == "metadata"}
    assert slots[ARCHIVE_TYPE_FIELD] == "ZIP"
    assert slots[UNCOMPRESSED_SIZE_FIELD] == "500"


def test_the_file_count_lives_on_coverage_and_nowhere_else(sink):
    result, _ = run_it()
    run_id = sink.write(result)
    assert sink.run_for(run_id)["coverage"] == {"units": "entries", "processed": 5,
                                                "total": 5}
    assert not [o for o in sink.observations_for(run_id)
                if o["raw_value"] == "5"]


def test_folder_names_and_extensions_are_spans_of_the_member_path(sink):
    manifest = ArchiveManifest(
        archive_type="ZIP",
        members=(ArchiveMember(path="project/src/main.py"),
                 ArchiveMember(path="project/src/util.py"),
                 ArchiveMember(path="project/", is_directory=True)),
        inspected=3, total=3)
    result, _ = run_it(manifest=manifest)
    run_id = sink.write(result)
    manifest_rows = {o["raw_value"]: o for o in sink.observations_for(run_id)
                     if o["location"]["zone"] == "manifest"}
    assert set(manifest_rows) == {"project/src/main.py", "project/src/util.py",
                                  "project/", "main.py", "util.py", ".py",
                                  "project", "src"}
    # D10: one row per (zone, raw); `src` appears in two members and counts twice.
    assert manifest_rows["src"]["occurrence_count"] == 2
    assert manifest_rows[".py"]["occurrence_count"] == 2
    # And the span really indexes the member path it names (P4 rule 5).
    sink.conforms()


def test_recognizable_markers_come_from_the_caller_not_from_p5(sink):
    seen = {}

    def recognizer(member_paths):
        seen["paths"] = tuple(member_paths)
        return (ArchiveMarker(member_path="project/package.json",
                              kind="source-code manifest"),)

    manifest = ArchiveManifest(
        archive_type="ZIP",
        members=(ArchiveMember(path="project/package.json"),),
        inspected=1, total=1)
    result, _ = run_it(manifest=manifest, markers=recognizer)
    run_id = sink.write(result)
    assert seen["paths"] == ("project/package.json",)
    marker = [o for o in sink.observations_for(run_id)
              if o["location"]["container_path"]
              and o["location"]["container_path"][0]["label"] in MARKER_KINDS][0]
    assert marker["raw_value"] == "project/package.json"
    assert marker["reliability"] == "direct"


def test_a_marker_class_section_2_5_does_not_name_is_refused():
    manifest = ArchiveManifest(archive_type="ZIP",
                               members=(ArchiveMember(path="a"),),
                               inspected=1, total=1)
    with pytest.raises(UnknownMarkerKind):
        run_it(manifest=manifest,
               markers=lambda paths: (ArchiveMarker(member_path="a",
                                                    kind="vibe"),))


def test_a_real_zip_is_read_and_not_one_byte_is_written(tmp_path, sink):
    # Done-means 7, and §2.5's absolute prohibition. The one test in this file that
    # touches a disk, and it builds its own tree under tmp_path.
    archive_path = tmp_path / "submission.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        for name in PACKET:
            archive.writestr(name, b"fixture bytes")

    def real_reader(target: Path) -> ArchiveManifest:
        with zipfile.ZipFile(target) as opened:
            infos = opened.infolist()
        return ArchiveManifest(
            archive_type="ZIP",
            members=tuple(ArchiveMember(path=i.filename, is_directory=i.is_dir(),
                                        uncompressed_size=i.file_size)
                          for i in infos),
            uncompressed_size=sum(i.file_size for i in infos),
            inspected=len(infos), total=len(infos))

    before = {p: p.stat().st_size for p in sorted(tmp_path.rglob("*"))}
    result = extract_archive(file_row=FILE_ROW, path=archive_path,
                             policy=OPEN_POLICY, read_manifest=real_reader,
                             recognize_markers=no_markers, now=FIXED_CLOCK,
                             context_window=20)
    after = {p: p.stat().st_size for p in sorted(tmp_path.rglob("*"))}

    assert after == before, "E4 wrote to the filesystem"
    run_id = sink.write(result)
    names = {o["raw_value"] for o in sink.observations_for(run_id)}
    assert set(PACKET) <= names
    assert sink.run_for(run_id)["completeness"] == "complete"


def test_a_password_protected_archive_is_unreadable_and_still_indexed(sink):
    # §2.5 + M3: "indexed-but-unreadable, never zero rows".
    manifest = ArchiveManifest(archive_type="ZIP", members=(), inspected=0, total=0,
                               unreadable_reason="password-protected")
    result, _ = run_it(manifest=manifest)
    run_id = sink.write(result)
    row = sink.run_for(run_id)
    assert row["completeness"] == "unreadable"
    assert "password-protected" in row["failure_reason"]
    assert [o["raw_value"] for o in sink.observations_for(run_id)] == ["ZIP"]
    sink.conforms()


def test_a_malformed_archive_is_unreadable_with_its_reason(sink):
    manifest = ArchiveManifest(archive_type="ZIP", members=(), inspected=0, total=0,
                               unreadable_reason="malformed central directory")
    result, _ = run_it(manifest=manifest)
    row = sink.run_for(sink.write(result))
    assert row["completeness"] == "unreadable"


def test_an_oversized_archive_is_partial_and_declares_its_size(sink):
    # The bomb signal is the DECLARED uncompressed size, read from the manifest.
    # P5 holds no ceiling: the reader was given §8.6's and reports that it stopped.
    manifest = ArchiveManifest(
        archive_type="ZIP",
        members=(ArchiveMember(path="huge.bin", uncompressed_size=10 ** 12),),
        uncompressed_size=10 ** 12, inspected=1, total=90000,
        partial_reason="stopped at the configured entry ceiling")
    result, _ = run_it(manifest=manifest)
    run_id = sink.write(result)
    row = sink.run_for(run_id)
    assert row["completeness"] == "partial"
    assert row["coverage"] == {"units": "entries", "processed": 1, "total": 90000}
    sizes = [o["raw_value"] for o in sink.observations_for(run_id)
             if o["location"]["container_path"]
             and o["location"]["container_path"][0]["label"] == UNCOMPRESSED_SIZE_FIELD]
    assert sizes == [str(10 ** 12)]
    sink.conforms()


def test_a_nested_archive_is_one_entry_and_the_manifest_is_read_once(sink):
    # SPEC Open question 8 is OPEN: whether an inner manifest may be read one level
    # down, in memory, is unsettled. E4 reads one manifest and recurses never.
    manifest = ArchiveManifest(
        archive_type="ZIP",
        members=(ArchiveMember(path="inner.zip", uncompressed_size=42),),
        inspected=1, total=2, partial_reason="contains a nested archive")
    result, calls = run_it(manifest=manifest)
    run_id = sink.write(result)
    assert len(calls) == 1
    assert sink.run_for(run_id)["completeness"] == "partial"
    inner = [o for o in sink.observations_for(run_id)
             if o["raw_value"] == "inner.zip"]
    assert inner[0]["location"]["zone"] == "manifest"


def test_the_same_manifest_produces_the_same_observations(sink):
    first = sink.write(run_it()[0])
    second = sink.write(run_it()[0])
    strip = lambda rows: [{k: v for k, v in r.items() if k != "run_id"} for r in rows]
    assert strip(sink.observations_for(first)) == strip(sink.observations_for(second))


def test_no_extractor_is_reachable_inside_a_protected_container():
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_archive(file_row=FILE_ROW,
                        path=Path("/Applications/Thing.app/Contents/a.zip"),
                        policy=policy,
                        read_manifest=lambda target: pytest.fail("reader reached"),
                        recognize_markers=no_markers, now=FIXED_CLOCK,
                        context_window=20)


def test_a_dataless_archive_is_never_materialized():
    policy = SafetyPolicy(is_protected_container=lambda path: False,
                          is_dataless=lambda path: True)
    with pytest.raises(DatalessRefused):
        extract_archive(file_row=FILE_ROW, path=Path("/corpus/submission.zip"),
                        policy=policy,
                        read_manifest=lambda target: pytest.fail("reader reached"),
                        recognize_markers=no_markers, now=FIXED_CLOCK,
                        context_window=20)
