# tests/readers/test_archive_tarfile.py
"""`read_manifest` backed by the standard library's `tarfile`.

`104` §18.2 gap 14, item 2 -- the tar twin of `tests/readers/
test_archive_zipfile.py`. §2.5's own sentence -- "Archives should yield their
manifests without extraction" -- makes no format distinction, and `tarfile` has
been in the standard library exactly as long as `zipfile` has.
"""
from __future__ import annotations

import io
import tarfile

import zipfile

from extractors.archive import extract_archive
from extractors.safety import SafetyPolicy
from readers.archive_tarfile import tarfile_reader
from readers.archive_zipfile import manifest_marker_recognizer, zipfile_reader
from readers.deployment import _archive_reader


def make_tar(tmp_path, entries, *, mode="w", name="bundle.tar"):
    path = tmp_path / name
    with tarfile.open(path, mode) as archive:
        for member, body in entries.items():
            data = body.encode() if isinstance(body, str) else body
            info = tarfile.TarInfo(name=member)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    return path


def test_the_manifest_names_every_member_without_extracting_anything(tmp_path):
    """The member PATHS are the evidence -- filenames, folder names, extensions
    -- and `getmembers()` reads them off the header blocks, never a member's
    data (`extractfile`/`extract` are never called)."""
    path = make_tar(tmp_path, {
        "PHYS1401/Problem Set 2.pdf": "x", "PHYS1401/notes.txt": "y"})

    manifest = tarfile_reader()(path)

    assert manifest.archive_type == "tar"
    assert {member.path for member in manifest.members} == {
        "PHYS1401/Problem Set 2.pdf", "PHYS1401/notes.txt"}
    assert manifest.total == 2
    assert manifest.inspected == 2
    assert manifest.unreadable_reason is None


def test_a_directory_entry_is_marked_as_one(tmp_path):
    """`ArchiveMember.is_directory` comes from the archive's own header flag
    (`TarInfo.isdir()`), not from guessing at a trailing slash -- tar strips the
    trailing slash from a directory's own name on write, unlike zip, so a check
    against the NAME would miss every directory a tar carries."""
    path = tmp_path / "dirs.tar"
    with tarfile.open(path, "w") as archive:
        directory = tarfile.TarInfo(name="Coursework")
        directory.type = tarfile.DIRTYPE
        archive.addfile(directory)
        data = b"a"
        info = tarfile.TarInfo(name="Coursework/a.txt")
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))

    members = {member.path: member for member in tarfile_reader()(path).members}

    assert members["Coursework"].is_directory is True
    assert members["Coursework/a.txt"].is_directory is False


def test_a_malformed_archive_is_named_unreadable_rather_than_raising(tmp_path):
    """§2.5's malformed case, and §2.4's distinction doing its work here exactly
    as it does for `zipfile_reader`: a reader that RAN and could not read is
    `failed`, a different fact from `unsupported`."""
    path = tmp_path / "broken.tar"
    path.write_bytes(b"not a tar header at all, just some bytes")

    manifest = tarfile_reader()(path)

    assert manifest.archive_type == "tar"
    assert manifest.members == ()
    assert manifest.unreadable_reason


def test_a_gzip_compressed_tar_is_read_without_a_dedicated_key(tmp_path):
    """`mode="r:*"` auto-detects the codec from the stream, so the SAME reader
    that lists a plain tar also lists a `w:gz` one -- no second reader, no
    dependency on the router having already named the compression."""
    path = make_tar(tmp_path, {"report.pdf": "x"}, mode="w:gz", name="bundle.tar.gz")

    manifest = tarfile_reader()(path)

    assert manifest.archive_type == "tar"
    assert [member.path for member in manifest.members] == ["report.pdf"]
    assert manifest.unreadable_reason is None


def test_an_archive_larger_than_the_ceiling_is_partial_and_says_so(tmp_path):
    """§2.5's oversized case, injected exactly as `zipfile_reader`'s is: how
    many members are worth listing is a deployment budget, not format
    knowledge."""
    path = make_tar(tmp_path, {f"file-{n}.txt": "x" for n in range(10)})

    manifest = tarfile_reader(max_members=4)(path)

    assert len(manifest.members) == 4
    assert manifest.inspected == 4
    assert manifest.total == 10
    assert manifest.partial_reason


OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
ARCHIVE_ROW = {"file_id": "f-tar", "content_hash": "c" * 64,
              "filename": "bundle.tar"}


def test_the_shared_extractor_reads_a_tar_manifest_exactly_as_it_reads_a_zip_one(
        tmp_path):
    """`extractors.archive.extract_archive` takes any `read_manifest` of the
    right shape -- this is the tar reader through that same shared extractor,
    with the same marker recognizer zip already uses (the recognizer reads
    member PATHS, not archive bytes, so it is format-agnostic by construction)."""
    path = make_tar(tmp_path, {"project/package.json": "{}",
                               "project/essay.docx": "x"})
    manifest = tarfile_reader(max_members=None)(path)
    result = extract_archive(
        file_row=ARCHIVE_ROW, path=path, policy=OPEN_POLICY,
        read_manifest=lambda _: manifest,
        recognize_markers=manifest_marker_recognizer(),
        now="2026-09-11T00:00:00Z", context_window=20)

    assert result.run["completeness"] == "complete"
    assert any(observation["raw_value"] == "project/package.json"
              for observation in result.observations)


# --------------------------------------------------------------------------- #
# `104` §18.2 gap 14, item 2: the ONE `read_manifest` key dispatches by bytes
# --------------------------------------------------------------------------- #

def test_the_combined_reader_dispatches_a_zip_to_the_zip_reader(tmp_path):
    """`readers.deployment._archive_reader` is what `extract_archive`'s single
    `read_manifest` key is bound to now that two families share it. A ZIP's own
    four-byte magic sends it to `zipfile_reader`."""
    path = tmp_path / "bundle.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("notes.txt", "x")

    combined = _archive_reader(
        zip_reader=zipfile_reader(), tar_reader=tarfile_reader())
    manifest = combined(path)

    assert manifest.archive_type == "zip"
    assert [m.path for m in manifest.members] == ["notes.txt"]


def test_the_combined_reader_dispatches_a_misnamed_tar_by_its_bytes(tmp_path):
    """The path says nothing -- `.zip` on a real tar -- and the dispatch still
    lands on the tar reader, because it reads the file's own first four bytes
    and never the extension (gap 21's rule inside the dispatcher too)."""
    path = tmp_path / "bundle.zip"
    with tarfile.open(path, "w") as archive:
        data = b"hello"
        info = tarfile.TarInfo(name="notes.txt")
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))

    combined = _archive_reader(
        zip_reader=zipfile_reader(), tar_reader=tarfile_reader())
    manifest = combined(path)

    assert manifest.archive_type == "tar"
    assert [m.path for m in manifest.members] == ["notes.txt"]
