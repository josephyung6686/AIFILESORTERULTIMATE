# tests/p5/test_p5_filesystem.py
"""O5 - P3's §1.2 record, re-emitted as citable evidence. P4 fixtures 11, 18, 19."""
from pathlib import Path

import pytest

from extractors.filesystem import EXTRACTOR_NAME, extract_filesystem, unrouted_result
from extractors.router import route
from extractors.safety import SafetyPolicy

from conftest import FIXED_CLOCK
from p4_stub import locator_for

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)

FILE_ROW = {
    "file_id": "f1",
    "content_hash": "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
    "filename": "Wash U.docx",
    "normalized_filename": "wash u.docx",
    "extension": ".docx",
    "directory_position": "/Users/jy/Downloads",
    "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "observed_size": 18240,
    "observed_timestamps": "2026-07-17T14:03:22+00:00",
}


def run_it(row=None, **kwargs):
    return extract_filesystem(file_row=row or FILE_ROW,
                              path=Path("/Users/jy/Downloads/Wash U.docx"),
                              policy=OPEN_POLICY, now=FIXED_CLOCK,
                              context_window=40, **kwargs)


def test_the_filename_is_citable_evidence_with_a_span_into_its_own_unit(sink):
    # P4 fixture 11: `filesystem` | `filename#0-6` | `Wash U` | `possible`.
    result = run_it()
    sink.write(result)
    sink.conforms()
    filename = [o for o in sink.observations if o["location"]["zone"] == "filename"]
    assert len(filename) == 1
    assert filename[0]["raw_value"] == "Wash U.docx"
    assert filename[0]["reliability"] == "possible"
    assert locator_for(filename[0]["location"]) == "filename#0-11"
    unit = sink.units_for(filename[0]["run_id"])[0]
    assert unit["container_path"] == ()
    assert unit["text"] == "Wash U.docx"


def test_the_parent_folder_context_is_emitted_under_2_9s_name(sink):
    # MINOR 11: "P5 calls it 'parent-folder context'; P3 calls it 'directory
    # position'. §2.9 says 'parent-folder context'. Ground truth wins."
    result = run_it()
    sink.write(result)
    path_rows = [o for o in sink.observations if o["location"]["zone"] == "path"]
    assert len(path_rows) == 1
    assert path_rows[0]["raw_value"] == "/Users/jy/Downloads"
    assert path_rows[0]["location"]["text_span"] is None    # P4 segment rule 4
    assert locator_for(path_rows[0]["location"]) == "path"


def test_the_named_slots_are_direct_and_the_free_positions_are_possible(sink):
    # P4: "`direct` ... an explicit, labeled, machine-structured slot"; "`possible`
    # ... a filename, or any unlabeled position."
    sink.write(run_it())
    by_locator = {locator_for(o["location"]): o for o in sink.observations}
    assert by_locator["metadata:field=extension"]["reliability"] == "direct"
    assert by_locator["metadata:field=mime_type"]["reliability"] == "direct"
    # `metadata:field=normalized_filename` is GONE, removed against CR-05: it was a
    # second home for the filename, in a releasable zone, and P7 released it in full
    # from there while refusing it from the `filename` address in the same run.
    assert "metadata:field=normalized_filename" not in by_locator
    assert by_locator["filename#0-11"]["reliability"] == "possible"
    assert by_locator["path"]["reliability"] == "possible"


def test_size_timestamps_and_content_hash_are_not_re_emitted(sink):
    # G5 gives duplicate and version-family signals to P6 "from P1's content hashes";
    # G6 gives the bounded download session to P6 "computed from P3 timestamps". P6
    # reads them from `files`, so a second copy here would be two homes for one value.
    sink.write(run_it())
    emitted = {locator_for(o["location"]) for o in sink.observations}
    for absent in ("metadata:field=observed_size", "metadata:field=observed_timestamps",
                   "metadata:field=content_hash", "metadata:field=version_family",
                   "metadata:field=duplicate_family"):
        assert absent not in emitted


def test_a_null_mime_type_produces_no_row_rather_than_an_empty_one(sink):
    # An observation records presence, never absence (§2.6, P4). A file P3 could not
    # type has no mime_type row, and the `complete` run IS the record of that.
    sink.write(run_it({**FILE_ROW, "mime_type": None}))
    emitted = {locator_for(o["location"]) for o in sink.observations}
    assert "metadata:field=mime_type" not in emitted
    assert sink.runs[0]["completeness"] == "complete"
    sink.conforms()


def test_the_run_is_the_filesystem_tier(sink):
    sink.write(run_it())
    row = sink.runs[0]
    assert row["extractor_name"] == EXTRACTOR_NAME == "filesystem.record"
    assert row["source_type"] == "filesystem"
    assert row["analysis_tier"] == "filesystem"
    assert row["completeness"] == "complete"
    assert row["coverage"] == {"units": "files", "processed": 1, "total": 1}


def test_this_module_recomputes_none_of_p3s_ten_fields():
    # O5: "A second derivation of any of them - including a second MIME-type
    # determination or a second hash - is a contract violation, not an optimization."
    import extractors.filesystem as module
    source = Path(module.__file__).read_text()
    for forbidden in ("hashlib", "mimetypes", "os.stat", "unicodedata", "casefold",
                      "read_bytes", "open("):
        assert forbidden not in source, forbidden


def test_an_unsupported_format_carries_zero_observations(sink):
    # §2.4: "an empty extraction result is different from an extractor that does not
    # yet exist." P4 conformance rule 9.
    decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     path=Path("/corpus/thing.qqq"), extension=".qqq",
                     detect_format=lambda path: None)
    sink.write(unrouted_result(file_row={**FILE_ROW, "filename": "thing.qqq"},
                               decision=decision, now=FIXED_CLOCK))
    assert sink.runs[0]["completeness"] == "unsupported"
    assert sink.observations == []
    sink.conforms()


def test_a_disk_image_stops_at_metadata_only_and_is_still_indexed(sink):
    # P4 fixture 19: "run: `completeness: metadata_only` ... The file is still
    # indexed through its `filesystem` observations (fixture 11)."
    decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     path=Path("/corpus/archive.dmg"), extension=".dmg",
                     detect_format=lambda path: "dmg")
    row = {**FILE_ROW, "filename": "archive.dmg", "extension": ".dmg",
           "mime_type": None}
    sink.write(extract_filesystem(file_row=row, path=Path("/corpus/archive.dmg"),
                                  policy=OPEN_POLICY, now=FIXED_CLOCK,
                                  context_window=40))
    sink.write(unrouted_result(file_row=row, decision=decision, now=FIXED_CLOCK))
    opaque = [r for r in sink.runs if r["source_type"] == "opaque_binary"][0]
    assert opaque["completeness"] == "metadata_only"
    assert sink.observations_for(opaque["run_id"]) == []
    indexed = [r for r in sink.runs if r["source_type"] == "filesystem"][0]
    assert sink.observations_for(indexed["run_id"])
    sink.conforms()


def test_a_psd_is_indexed_but_unreadable_and_never_zero_rows(sink):
    # SPEC fixture: "`design.psd` | §2.9 | `unreadable` carrying metadata-level
    # observations (M3) - indexed-but-unreadable, never zero rows."
    decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     path=Path("/corpus/design.psd"), extension=".psd",
                     detect_format=lambda path: "psd")
    row = {**FILE_ROW, "filename": "design.psd", "extension": ".psd",
           "mime_type": "image/vnd.adobe.photoshop"}
    sink.write(unrouted_result(file_row=row, decision=decision, now=FIXED_CLOCK))
    assert sink.runs[0]["completeness"] == "unreadable"
    assert sink.runs[0]["source_type"] == "design_creative"
    assert sink.runs[0]["extractor_name"] == "format.unrouted"
    assert sink.runs[0]["failure_reason"]
    emitted = {locator_for(o["location"]): o["raw_value"] for o in sink.observations}
    assert emitted["filename"] == "design.psd"
    assert emitted["metadata:field=format"] == "psd"
    assert {o["extractor_name"] for o in sink.observations} == {"format.unrouted"}
    sink.conforms()


def test_the_extractor_refuses_a_protected_path_before_reading_the_row():
    from extractors.safety import ProtectedContainerRefused
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_filesystem(file_row=FILE_ROW,
                           path=Path("/Applications/Thing.app/Wash U.docx"),
                           policy=policy, now=FIXED_CLOCK, context_window=40)
