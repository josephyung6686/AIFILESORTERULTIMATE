# tests/integration/test_cli_protected_summary_covers_only_protected_files.py
"""An ordinary file is never summarised away under the protected sentence.

Found by RUNNING `cli.main` over a synthetic Downloads (2026-09-07, offline).
The person answered the folder question the run had asked --
`--answer home:.=Coursework` -- and the next report read:

    Ready for you to approve, then file into Coursework -- 13 files
      13 protected files, marked and counted, and none of them opened. Their
      names are not printed here ...

Four of the thirteen were protected (receipts, a boarding pass). The other
nine were a syllabus, a homework sheet, two cover letters and a zip -- named on
the previous screen, now hidden behind a sentence that called them protected.
`--show-protected` printed all thirteen under the same heading.

**The mechanism.** `report` groups decisions by a key of (outcome, destination,
reason, review sets, policy, ...) and ORs each group's `shielded` flag over its
members, so one protected file in a group hid the whole group. The two halves
each pass their own tests: a protected decision is shielded, an ordinary one is
listed. The pair was wrong because they shared a key. The fix puts the
decision's own protection into the key, so protected and ordinary files never
share a heading -- which is also what the standing rule says: protected
material is marked and counted as ITSELF, never by taking its neighbours with it.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: The north star's own person: a real disk has one of these, and
#: `recognition.detector` marks it protected from its own words.
PASSPORT_NAME = "passport scan.txt"
PASSPORT_BODY = ("Passport number X12345678. Client identity document.\n"
                 "Passport scan, identity document, date of birth "
                 "and nationality.\n")

#: Two readable kinds of coursework, so the plan has two folders and the
#: unreadable file below raises the folder question at all (one destination is
#: not a choice).
COURSEWORK = {
    "PHYS 1401 syllabus.txt":
        "PHYS 1401 syllabus. Columbia University, Spring 2026 term.\n"
        "Course syllabus for PHYS 1401. Weekly readings and problem sets.\n",
    "PHYS 1401 lecture 08.txt":
        "PHYS 1401 lecture 08 notes. Columbia University, Spring 2026 term.\n"
        "Lecture notes for the eighth week of PHYS 1401.\n",
}


def _corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "holder" / "Downloads"
    corpus.mkdir(parents=True)
    for name, body in COURSEWORK.items():
        (corpus / name).write_text(body)
    (corpus / PASSPORT_NAME).write_text(PASSPORT_BODY)
    # Opened, nothing readable came out: the file the folder question is about.
    (corpus / "data.bin").write_bytes(bytes(range(256)) * 16)
    return corpus


def _run(corpus: Path, *extra: str) -> str:
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(corpus.parent / "plan.sqlite"), *extra], out=out)
    return out.getvalue()


def test_answering_the_folder_question_does_not_hide_ordinary_files_as_protected(tmp_path):
    corpus = _corpus(tmp_path)
    first = _run(corpus)
    assert "--answer home:.=" in " ".join(first.split()), first

    printed = _run(corpus, "--answer", "home:.=Coursework")
    collapsed = " ".join(printed.split())

    # The passport is still marked, counted once, and not named.
    assert "1 protected file, marked and counted, and none of them opened" \
        in collapsed, printed
    assert PASSPORT_NAME not in printed, printed
    # And its neighbours are named, not counted as protected beside it.
    for name in COURSEWORK:
        assert name in printed, (name, printed)
    assert "protected files" not in collapsed, printed


def test_show_protected_names_the_passport_under_its_own_heading(tmp_path):
    """`--show-protected` widens what is on the SCREEN to the protected names,
    and the names must arrive under a heading that says what they are -- not
    under one shared with a syllabus."""
    corpus = _corpus(tmp_path)
    _run(corpus)
    printed = _run(corpus, "--answer", "home:.=Coursework", "--show-protected")

    assert PASSPORT_NAME in printed, printed
    lines = printed.splitlines()
    at = next(i for i, line in enumerate(lines) if PASSPORT_NAME in line)
    heading = next(line for line in reversed(lines[:at]) if line.startswith("  ")
                   and not line.startswith("    "))
    assert heading.strip().endswith("-- 1 file"), (heading, printed)
