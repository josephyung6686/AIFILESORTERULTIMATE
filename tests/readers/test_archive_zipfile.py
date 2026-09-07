# tests/readers/test_archive_zipfile.py
"""`read_manifest` backed by the standard library's `zipfile`.

`deployment.py` wired `read_manifest = _no_reader`, whose docstring says "this
deployment ships no library for the format". For archives that sentence was never
true: `zipfile` is in the standard library and always has been. The cost was the
same as the `.docx` gap -- every `.zip` on a person's disk recorded §2.4's
`unsupported`, which means "no reader exists and THE BYTES WERE NEVER LOOKED AT",
and every count downstream agreed the file carried nothing.

§2.5 is explicit that an archive should "yield their manifests WITHOUT
EXTRACTION", and that is also what makes this safe to ship: `namelist` and
`infolist` read the central directory only. Nothing is decompressed, so a
password-protected member is never a decryption attempt and a zip bomb is never
expanded -- the sizes come from the header the archive states about itself.
"""
from __future__ import annotations

import zipfile

import pytest

from readers.archive_zipfile import zipfile_reader


def make_zip(tmp_path, entries, name="bundle.zip"):
    path = tmp_path / name
    with zipfile.ZipFile(path, "w") as archive:
        for member, body in entries.items():
            archive.writestr(member, body)
    return path


def test_the_manifest_names_every_member_without_extracting_anything(tmp_path):
    """§2.5's whole point. The member PATHS are the evidence an archive carries
    -- filenames, folder names and extensions -- and they are in the central
    directory, so nothing has to be decompressed to read them."""
    path = make_zip(tmp_path, {
        "PHYS1401/Problem Set 2.pdf": "x", "PHYS1401/notes.txt": "y"})

    manifest = zipfile_reader()(path)

    assert manifest.archive_type == "zip"
    assert {member.path for member in manifest.members} == {
        "PHYS1401/Problem Set 2.pdf", "PHYS1401/notes.txt"}
    assert manifest.total == 2
    assert manifest.inspected == 2
    assert manifest.unreadable_reason is None


def test_a_directory_entry_is_marked_as_one(tmp_path):
    """`ArchiveMember.is_directory` changes how `_name_spans` reads the path --
    a directory has no extension to split off -- so getting it from the archive
    rather than guessing at a trailing slash is the reader's job."""
    path = tmp_path / "dirs.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("Coursework/", "")
        archive.writestr("Coursework/a.txt", "a")

    members = {member.path: member for member in zipfile_reader()(path).members}

    assert members["Coursework/"].is_directory is True
    assert members["Coursework/a.txt"].is_directory is False


def test_a_malformed_archive_is_named_unreadable_rather_than_raising(tmp_path):
    """§2.5's malformed case, and §2.4's distinction doing its work: a reader that
    RAN and could not read is `failed`, which is a different fact from
    `unsupported`. Returning a manifest that says why keeps the file in the record
    with its reason attached instead of dropping it."""
    path = tmp_path / "broken.zip"
    path.write_bytes(b"PK\x03\x04 this is not really a zip")

    manifest = zipfile_reader()(path)

    assert manifest.archive_type == "zip"
    assert manifest.members == ()
    assert manifest.unreadable_reason


def test_an_encrypted_member_is_listed_and_never_decrypted(tmp_path):
    """The security half. A password-protected member's NAME is in the central
    directory in clear, so it is listed; its content is not read, not attempted,
    and not reported as missing.

    This is the archive form of the standing rule that protected material is
    marked and counted and never opened.
    """
    path = tmp_path / "locked.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("secret.txt", "hidden")
    _claim_encrypted(path)

    manifest = zipfile_reader()(path)

    assert [member.path for member in manifest.members] == ["secret.txt"]
    # And MARKED, in the reader's own words. `infolist` read the flag from the
    # central directory and decrypted nothing; the manifest says so, and P5 turns
    # the reason into an `unreadable` run (`test_p5_archive`). Before this line
    # the manifest was `complete`, so a locked archive on a person's disk was
    # indexed exactly like an open one and nothing downstream could tell.
    assert manifest.unreadable_reason == (
        "password-protected: 1 of 1 member(s) are encrypted; names listed, "
        "contents not read")
    assert manifest.total == 1 and manifest.inspected == 1


def _claim_encrypted(path) -> None:
    """Set bit 0 of the general-purpose flag in EVERY header of the archive.

    Both the local file header (`PK\\x03\\x04`, flag at +6) and the central
    directory entry (`PK\\x01\\x02`, flag at +8): `zipfile.infolist` reads the
    central directory, so flipping the local header alone -- which this test
    once did -- claimed encryption where the reader never looks and asserted
    nothing about the bit it does read. The bytes are otherwise untouched: the
    header now claims encryption and any attempt to decrypt would fail, which is
    exactly the state a reader must survive without trying.
    """
    raw = bytearray(path.read_bytes())
    for signature, offset in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
        start = 0
        while (at := raw.find(signature, start)) != -1:
            raw[at + offset] |= 0x01
            start = at + 1
    path.write_bytes(bytes(raw))


def test_an_open_archive_beside_a_locked_one_is_not_marked(tmp_path):
    """The negative twin: the mark fires on the bit and on nothing else."""
    manifest = zipfile_reader()(make_zip(tmp_path, {"notes.txt": "plain"}))
    assert manifest.unreadable_reason is None


def test_an_archive_larger_than_the_ceiling_is_partial_and_says_so(tmp_path):
    """§2.5's oversized case. The ceiling is the CALLER's, injected, because how
    many members are worth listing is a deployment budget and not format
    knowledge -- the same reason no other number in this project is written into
    a reader."""
    path = make_zip(tmp_path, {f"file-{n}.txt": "x" for n in range(10)})

    manifest = zipfile_reader(max_members=4)(path)

    assert len(manifest.members) == 4
    assert manifest.inspected == 4
    assert manifest.total == 10
    assert manifest.partial_reason
