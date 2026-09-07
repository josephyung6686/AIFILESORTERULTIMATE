"""`104` R-M: the person's screen says why, in words, and never cites a section.

Measured on a 52-file corpus by a fresh session reading its own terminal: 31
occurrences of "§6.10's" and 20 of "§8.4" on one report. *"No legal destination
cleared §6.10's conditions (conflicting_facts)"* and *"§8.4 did not clear this
file for a model call"* are the two the verifier wrote down, and both are the same
mistake -- the sentence names the paragraph of the design that governs the
decision instead of naming the decision.

The section reference is not lost, and that is why it can come off the screen. It
is in the RECORD, structurally and not as prose: `PlacementDecision.two_condition`
is §6.10's measurement (support, margin, threshold, the policy that set them),
`PlacementDecision.privacy` is §8.4's class, and `abstention_reason` is the closed
code for which condition failed. A person reads the sentence; a lead reads the row.

The assertion is over the whole report rather than over a list of known sentences,
because a list would have to be extended by whoever adds the next one -- and
nobody adds a section number on purpose.
"""
from __future__ import annotations

import io
from pathlib import Path

import cli

SITUATION = "academic.coursework"
LABEL = "Coursework"


def _corpus(root: Path) -> Path:
    """One file per outcome the report has a sentence for.

    A syllabus that places, two lecture notes that make a course branch, a file
    nothing can read a fact out of, and a passport -- so the run produces a
    placement, an abstention and a protected withholding on one screen.
    """
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS1401 Syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    (corpus / "Lecture 08.txt").write_text(
        "Lecture 08 - Rotational Dynamics\nPHYS 1401\nTorque and angular "
        "momentum.\n")
    (corpus / "HW 3.txt").write_text(
        "Homework 3\n\nProblem 1. A ball is thrown upward...\n")
    (corpus / "untitled.txt").write_text("...\n")
    (corpus / "Passport scan.txt").write_text(
        "Passport\nHong Kong Special Administrative Region\n"
        "Passport No. K12345678\nDate of birth: 1 January 1990\n")
    return corpus


def _run(corpus: Path, database: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                     "--user", "jy", "--database", str(database), *extra],
                    out=out)
    return code, out.getvalue()


def _sections(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if "§" in line]


def test_a_plain_run_cites_no_section_of_the_design(tmp_path):
    corpus = _corpus(tmp_path)
    code, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")

    assert code == 0, report
    # The screen really did reach the sentences under test.
    assert "Files:" in report and "Waiting for you" in report, report
    assert _sections(report) == [], _sections(report)


def test_show_protected_and_freeze_cite_no_section_either(tmp_path):
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(corpus, database)

    _, shown = _run(corpus, database, "--show-protected")
    assert _sections(shown) == [], _sections(shown)

    _, frozen = _run(corpus, database, "--freeze")
    assert _sections(frozen) == [], _sections(frozen)


def test_the_reason_the_person_reads_says_what_happened(tmp_path):
    """Not merely "no section number": the sentence has to carry the reason.

    A run that answered every abstention with "nothing matched" would pass the
    test above and be worse than what it replaced.
    """
    corpus = _corpus(tmp_path)
    _, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")

    flat = " ".join(report.split())
    assert "protected material" in flat, report
    # And the engine's own code word is not the sentence.
    assert "(no_supported_destination)" not in flat, report
    assert "(conflicting_facts)" not in flat, report
