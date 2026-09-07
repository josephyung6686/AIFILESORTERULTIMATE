# tests/p15/test_p15_a_promised_gesture_is_offered.py
"""`104` R-92: "once you say what these are" with nothing to say it with.

Measured on a 52-file folder, offline, after every question the report printed
had been answered (verifier report of 2026-09-07, defect 9):

      Would go into lecture, once you say what these are -- 5 files
        Econ lecture 3 slides.pdf
        Lecture 05 - Newtons Laws.pdf
        Lecture 06 - Work and Energy.pdf
        cs3134_lecture_04_hashing (1).pdf
        cs3134_lecture_04_hashing.pdf

No `--answer` anywhere on that screen reached three of those five. `84` §6's
standing ruling is that what the screen tells a person to type has to be true,
and this is the worst way to break it: the person goes looking for the gesture,
does not find it, and concludes the fault is theirs.

Two properties, and the second is what makes the first honest:

* a blocked group that a printed question WOULD settle names that question and
  prints the answers themselves, and every `--answer` it prints is one the
  question list on the same screen offers;
* a blocked group nothing reaches says so instead of promising a gesture, and
  prints no `--answer` at all.

The corpus is three files and it produces one group of each kind: two BUSIB 4300
transcripts whose own words tie seven ways, and one starter script that carries
the same course code and no reading of its own. That difference is the whole
defect -- a subject in common is not a question in common -- so the fixture is
built around it rather than around a mock.
"""
from __future__ import annotations

import io
import re
import shlex

import pytest

import cli

#: A heading is two spaces and a capital; everything under it is indented four or
#: more. Parsed rather than asserted line by line because the point of this file
#: is that EVERY such block holds, not that three named ones do.
HEADING = re.compile(r"^  ([A-Z].*?) -- \d+ files?$")
#: A GESTURE AND NOT THE WORD. `QUESTION=OPTION` is what `--answer` takes, so the
#: `=` is in the pattern -- a sentence that mentions the flag in prose ("no
#: `--answer` here reaches them") is not a command and must not be read as one.
GESTURE = re.compile(r"--answer (\S+=\S*|'[^']*=[^']*')")

#: The sentences `cli.PLACEMENT_WORDS`, `cli.SAME_FOLDER` and `cli.ALREADY_THERE`
#: carry for `blocked_pending_user`, and the three `cli.NOTHING_SAYS_WHAT_THESE_
#: ARE` carries instead. A heading holding any of them is a group whose files are
#: waiting on somebody saying what they are, which is what this file is about.
BLOCKED = ("once you say what these are", "to say what these are",
           "once something can say what these are")


def _corpus(tmp_path):
    corpus = tmp_path / "corpus"
    if corpus.is_dir():
        return corpus
    corpus.mkdir()
    (corpus / "Deposition.txt").write_text(
        "BUSIB 4300 Deposition Transcript\n\n"
        "Transcript of the witness in the seminar. Instructor: Dr. Ramirez. "
        "Credits: 3.\n")
    (corpus / "Second Deposition.txt").write_text(
        "BUSIB 4300 Deposition Transcript\n\n"
        "Second transcript of a witness. Instructor: Dr. Ramirez. Credits: 3.\n")
    # The same course code and nothing that reads as anything: no reading ties
    # about it, so no question is raised about it, so no answer reaches it.
    (corpus / "starter.py").write_text(
        '"""BUSIB 4300 Homework 2 starter: implement a stack using two '
        'queues."""\n\nfrom collections import deque\n\n\nclass Stack:\n'
        "    def __init__(self):\n        self._in = deque()\n")
    return corpus


def _run(tmp_path, *extra) -> str:
    out = io.StringIO()
    code = cli.main([str(_corpus(tmp_path)), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(tmp_path / "plan.sqlite"), *extra],
                    out=out)
    assert code == 0, out.getvalue()
    return out.getvalue()


def _blocks(printed: str) -> dict[str, list[str]]:
    """Every file group on the screen: its heading, and the lines under it.

    Stops at the question list, so a gesture printed with a QUESTION is never
    counted as one a file group promised.
    """
    body = printed.split("\nQuestions only you can answer:")[0]
    body = body.split("\nYou can change how this is organised")[0]
    blocks: dict[str, list[str]] = {}
    current: list[str] | None = None
    for line in body.splitlines():
        found = HEADING.match(line)
        if found:
            current = blocks.setdefault(found.group(1), [])
        elif current is not None and line.startswith("    "):
            current.append(line)
        elif not line.strip():
            continue
        else:
            current = None
    return blocks


def _offered(printed: str) -> set[str]:
    """Every `QUESTION=OPTION` the report's question list actually offers."""
    tail = printed.split("\nQuestions only you can answer:", 1)
    offered: set[str] = set()
    for chunk in tail[1:]:
        for found in GESTURE.finditer(chunk):
            offered.add(shlex.split(found.group(0))[1])
    return offered


def test_every_answer_a_file_group_prints_is_one_the_questions_offer(tmp_path):
    """THE WALK. Not three named groups -- every group on the screen.

    A `--answer` printed beside a list of files is a promise that typing it does
    something to those files. The report may only make it about a question it is
    also printing, and this reads both halves off one screen.
    """
    printed = _run(tmp_path)
    offered = _offered(printed)
    assert offered, printed
    for heading, lines in _blocks(printed).items():
        for line in lines:
            for found in GESTURE.finditer(line):
                gesture = shlex.split(found.group(0))[1]
                assert gesture in offered, (
                    f"{heading!r} tells the person to type {gesture!r} and no "
                    f"question on this screen offers it:\n{printed}")


def test_every_group_waiting_on_a_classification_says_what_reaches_it(tmp_path):
    """A group counted and then abandoned is the other half of the same defect.

    Every blocked heading carries either the answers that settle it or the
    sentence saying nothing here does -- never a count with silence under it.
    """
    printed = _run(tmp_path)
    blocked = {heading: lines for heading, lines in _blocks(printed).items()
               if any(phrase in heading for phrase in BLOCKED)}
    assert blocked, printed
    for heading, lines in blocked.items():
        said = "\n".join(lines)
        assert (GESTURE.search(said) or "--list-residuals" in said), (
            f"{heading!r} says these files are waiting on somebody saying what "
            f"they are and says nothing about how:\n{printed}")


def test_a_group_a_question_settles_names_that_question_and_its_answers(tmp_path):
    """The two transcripts tie, so the reading question is theirs to answer."""
    printed = _run(tmp_path)
    blocked = [(heading, lines) for heading, lines in _blocks(printed).items()
               if "once you say what these are" in heading]
    assert len(blocked) == 1, printed
    heading, lines = blocked[0]
    said = "\n".join(lines)
    assert "Deposition.txt" in said and "Second Deposition.txt" in said, printed
    assert "starter.py" not in said, (
        "the file no question reaches is under the heading that promises one:\n"
        + printed)
    assert "What kind of material is BUSIB4300?" in said, printed
    assert "--answer reading.organization:BUSIB4300=academic" in said, printed


def test_a_group_no_question_reaches_promises_nothing_and_says_why(tmp_path):
    """`starter.py` carries the course code and no reading of its own.

    A subject in common is not a question in common, which is the distinction the
    old sentence collapsed: five files under one promise, three of them unreachable.
    """
    printed = _run(tmp_path)
    blocked = [(heading, lines) for heading, lines in _blocks(printed).items()
               if "once something can say what these are" in heading]
    assert len(blocked) == 1, printed
    heading, lines = blocked[0]
    said = "\n".join(lines)
    assert "starter.py" in said, printed
    assert not GESTURE.search(said), (
        "a group nothing reaches is still offering an answer:\n" + printed)
    assert "--list-residuals" in said, printed
    assert "what kind of material they are" in " ".join(said.split()), printed


def test_the_answer_the_screen_named_settles_the_files_it_named(tmp_path):
    """AND IT HAS TO WORK. The screen said typing this reaches these files; this
    types it and reads the next screen.

    Both halves: the two the sentence named stop waiting, and the one it did not
    name is still waiting -- which is the sentence being right about both.
    """
    _run(tmp_path)
    printed = _run(tmp_path, "--answer", "reading.organization:BUSIB4300=academic")
    assert "Ready to file into Coursework -- 2 files" in printed, printed
    settled = _blocks(printed)["Ready to file into Coursework"]
    assert "Deposition.txt" in "\n".join(settled), printed
    still = [heading for heading in _blocks(printed)
             if "once something can say what these are" in heading]
    assert len(still) == 1, printed
    assert "starter.py" in "\n".join(_blocks(printed)[still[0]]), printed


def test_a_report_told_of_no_question_promises_no_gesture():
    """The default, and it fails the safe way.

    `report`'s `reaching` is empty for every caller that passes none, and an
    empty one means no group may claim a gesture: what is printed is the
    sentence saying nothing reaches these files, never an `--answer`. The defect
    was claiming one, so silence about a question has to fall on this side.
    """
    said = cli._how_to_say_what_these_are((), ("academic",))
    assert said, "a blocked group was left with nothing said under it"
    assert not any(GESTURE.search(line) for line in said), said
    assert any("--list-residuals" in line for line in said), said
    # And the inversion the report reads, which is what an empty mailbox empties.
    assert cli._questions_by_file({"reading.organization:X": ("f1", "f2")}) == {
        "f1": ("reading.organization:X",),
        "f2": ("reading.organization:X",)}
    assert cli._questions_by_file({}) == {}


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__]))
