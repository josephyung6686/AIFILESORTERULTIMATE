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

from extractors.archive import MARKER_KINDS, extract_archive
from extractors.safety import SafetyPolicy
from readers.archive_zipfile import (
    SOURCE_CODE_MANIFEST, manifest_marker_recognizer, zipfile_reader,
)


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


# --------------------------------------------------------------------------- #
# `104` §18.2 gap 17, loss (c): the marker recognizer that returned nothing
# --------------------------------------------------------------------------- #

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
ARCHIVE_ROW = {"file_id": "f-arc", "content_hash": "c" * 64,
               "filename": "bundle.zip"}


def extracted(path):
    manifest = zipfile_reader(max_members=None)(path)
    return extract_archive(
        file_row=ARCHIVE_ROW, path=path, policy=OPEN_POLICY,
        read_manifest=lambda _: manifest,
        recognize_markers=manifest_marker_recognizer(),
        now="2026-09-09T00:00:00Z", context_window=20)


def test_a_source_code_manifest_inside_an_archive_is_recognized(tmp_path):
    """`104` §18.2 gap 17, loss (c). `recognize_markers` was `lambda names: ()`.

    §2.5: "A source-code archive may reveal a `README.md`, `package.json`, `src`
    directory, or Python package layout and can be recognized as a code project."
    `extract_archive` has taken a caller-supplied `recognize_markers` for exactly
    that since it was written, and `readers/deployment.py` wired it to a lambda
    returning `()`. Its stated reason -- §2.5's marker set is Deferred in P5's SPEC,
    so a list invented in the deployment "would be this deployment authoring the open
    half of somebody else's section" -- was true, and overlooked that the answer for
    §2.5's FIRST class was already shipped one module away in
    `text_documents._MARKERS_BY_FILENAME`.

    SABOTAGE: put `lambda names: ()` back in `deployment.py`, or give
    `manifest_marker_recognizer` a filename table of its own. The first makes the
    marker arm dead again; the second is two lists that will drift, which is what
    `filename_marker_kind` being ONE definition with two callers prevents.
    """
    recognize = manifest_marker_recognizer()
    markers = recognize([
        "project/package.json", "project/src/index.js",
        "project/README.md", "project/.gitignore",
        "project/notes.txt",            # not a marker of anything
    ])
    assert {marker.member_path for marker in markers} == {
        "project/package.json", "project/README.md", "project/.gitignore"}
    # §2.5 offers TWO classes where §2.4 offers four, and `MARKER_KINDS` is the
    # vocabulary `extract_archive` validates against -- so a package manifest, a
    # repository marker and a README all arrive re-kinded rather than as a third
    # class, which would be `UnknownMarkerKind` at run time.
    assert {marker.kind for marker in markers} == {SOURCE_CODE_MANIFEST}
    assert SOURCE_CODE_MANIFEST in MARKER_KINDS


def test_the_marker_reaches_the_evidence_table_as_the_member_path(tmp_path):
    """The whole loss, end to end: reader to extractor to observation.

    P5 PLAN Task 13 and catalogue 07 both say the `raw_value` is THE MEMBER PATH and
    not the marker word -- "this is what keeps the observation a READING rather than
    a conclusion" -- and the kind goes in the field label.

    SABOTAGE: return `ArchiveMarker(member_path=basename, ...)` and the observation
    stops naming where in the archive the marker sits.
    """
    path = make_zip(tmp_path, {"submission/pyproject.toml": "[project]\n",
                               "submission/essay.docx": "x"})
    marked = [observation for observation in extracted(path).observations
              if observation["location"]["container_path"]
              and observation["location"]["container_path"][-1].get("label")
              == SOURCE_CODE_MANIFEST]
    assert [observation["raw_value"] for observation in marked] == [
        "submission/pyproject.toml"]
    assert marked[0]["reliability"] == "direct"
    assert marked[0]["location"]["zone"] == "metadata"


def test_a_document_name_is_not_yet_a_marker_and_the_path_is_still_recorded(tmp_path):
    """§2.5's SECOND class stays deferred, and the deferral costs no evidence.

    `document name` would be §2.5's five English words -- transcript, personal
    statement, resume, certificate, form -- matched against member basenames. That is
    a word list deciding an outcome, and catalogue 07 rates the last of the five
    `high` false-positive risk on its own (`form` is inside `format`, `formula`,
    `information`, `transformation`). What §18.2 calls a silent loss is a READING
    that never reaches the record; this is a LABEL that does not, while the member
    path it would label is on the record either way -- which is what makes it a
    deferral and not a loss.

    SABOTAGE: add the five words to `manifest_marker_recognizer`.
    """
    path = make_zip(tmp_path, {"submission/transcript.pdf": "x"})
    manifest = zipfile_reader(max_members=None)(path)
    assert manifest_marker_recognizer()([m.path for m in manifest.members]) == ()
    assert any(observation["raw_value"] == "submission/transcript.pdf"
               for observation in extracted(path).observations)
