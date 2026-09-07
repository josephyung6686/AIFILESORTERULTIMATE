"""`104` R-D: a password-protected archive is on the screen, not only in the record.

`03938ae` taught the zip reader to read bit 0 of the general-purpose flag, so the
manifest now says *"password-protected: 2 of 2 member(s) are encrypted; names
listed, contents not read"* and P5 records the extraction `unreadable`. The person
still read *"This file has not been classified"*, folded in with twelve other
files, and `--show-protected` did not count it -- the record knew and the screen
did not.

§2.5 marks a locked archive rather than forcing it open, and the standing rule is
that what is marked is counted, never opened, never silently omitted. Counted
means counted where a person reads.

The archive here is built the way `tests/readers/test_archive_zipfile.py` builds
one -- a real zip whose headers are then flipped to claim encryption -- because
`zipfile` cannot write an encrypted member and nothing in this repository should
carry a password to one.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import cli

SITUATION = "academic.coursework"
LABEL = "Coursework"


def _claim_encrypted(path: Path) -> None:
    """Set bit 0 of the general-purpose flag in every header of the archive.

    Local file header (`PK\\x03\\x04`, flag at +6) and central directory entry
    (`PK\\x01\\x02`, flag at +8). `zipfile.infolist` reads the central directory,
    and the reader reads `infolist`, so both are set and neither is decryptable --
    which is exactly the state a reader must survive without trying.
    """
    raw = bytearray(path.read_bytes())
    for signature, offset in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
        start = 0
        while (at := raw.find(signature, start)) != -1:
            raw[at + offset] |= 0x01
            start = at + 1
    path.write_bytes(bytes(raw))


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS1401 Syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee.\n")
    archive = corpus / "submission_backup.zip"
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr("essay.docx", "draft")
        zipped.writestr("figures.png", "bytes")
    _claim_encrypted(archive)
    return corpus


def _run(corpus: Path, database: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                     "--user", "jy", "--database", str(database), *extra],
                    out=out)
    return code, out.getvalue()


def test_the_locked_archive_is_counted_on_the_plain_screen(tmp_path):
    corpus = _corpus(tmp_path)
    code, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")

    assert code == 0, report
    assert "Password-protected containers: 1, never opened" in report, report
    assert "submission_backup.zip" in report, report
    flat = " ".join(report.split())
    # Both halves of §2.5's sentence: the names are known, the contents are not.
    assert "names listed, contents not read" in flat, report


def test_the_locked_archive_says_what_it_is_where_the_file_is_listed(tmp_path):
    """Its own group, and its own sentence.

    It used to sit inside "Waiting for you to say what these are -- 13 files"
    under one shared reason, which is true of every one of those files and says
    nothing about the one thing this file's record actually knows.
    """
    corpus = _corpus(tmp_path)
    _, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")

    # BELOW the block at the top, which is where the file itself is listed. The
    # split is on "Files:", the report's own heading for the per-file half, so
    # this cannot pass on the summary it already asserted elsewhere.
    body = report.split("\nFiles:", 1)[1]
    flat = " ".join(body.split())
    assert "submission_backup.zip is password-protected" in flat, report
    assert "2 of 2 member(s) are encrypted" in flat, report
    assert "counted with the protected material at the top" in flat, report
    # And the member names never appear: a locked archive's members can be
    # somebody's passport scan.
    assert "essay.docx" not in report, report
    assert "figures.png" not in report, report


def test_show_protected_counts_the_locked_archive_too(tmp_path):
    corpus = _corpus(tmp_path)
    _, report = _run(corpus, tmp_path / "holder" / "plan.sqlite",
                     "--show-protected")

    assert "Password-protected containers: 1, never opened" in report, report
    assert "submission_backup.zip" in report, report


def test_an_open_archive_is_not_counted_as_a_container(tmp_path):
    """The negative twin: the count fires on the encryption bit and nothing else."""
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS1401 Syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee.\n")
    with zipfile.ZipFile(corpus / "handouts.zip", "w") as zipped:
        zipped.writestr("week1.txt", "plain")

    _, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")

    assert "Password-protected containers" not in report, report
    assert "Protected: 0 marked and counted" in report, report
