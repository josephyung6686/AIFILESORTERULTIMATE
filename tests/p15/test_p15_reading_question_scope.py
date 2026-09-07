# tests/p15/test_p15_reading_question_scope.py
"""`104` R-90: a reading question asked under a situation the person typed.

Measured on a real 52-file corpus, offline, with `--situation academic.coursework`
on the command line (verifier report of 2026-09-07, defect 7):

    What kind of material is ECON2010?
      4 files mention ECON2010, and their own words support 7 readings equally.
        --answer reading.organization:ECON2010=academic
        --answer reading.organization:ECON2010=business_operations
        --answer reading.organization:ECON2010=clinical_practice
        --answer reading.organization:ECON2010=construction_property
        --answer reading.organization:ECON2010=engineering
        --answer reading.organization:ECON2010=research
        --answer reading.organization:ECON2010=retail_hospitality

The person had already said, on the command line, what kind of life these files
belong to. The question is load-bearing -- answering the three of them `academic`
moved that run from 7 files ready to file to 10 -- so it is the PRESENTATION that
is wrong, and this file holds it to two properties that have to hold together:

* the readings the typed situation's own family carries come FIRST, and the rest
  are folded behind a command printed beside them, so a person filing a course is
  not asked to choose between clinical practice and retail hospitality;
* nothing is removed. `--explain` still lists every reading the evidence
  produced, and an `--answer` naming a folded one is still accepted -- the closed
  vocabulary is the evidence's answer and this changes only what a screen shows.

The corpus is `test_cli._ambiguous_corpus`'s, spelled here rather than imported
so this file names the material it is asserting about. Its two BUSIB 4300 files
tie seven ways -- `academic`, `business_operations`, `college_applications`,
`creative`, `engineering`, `law_practice`, `manufacturing` -- and exactly one of
those seven is in `academic.coursework`'s family, which is what makes it the case
worth pinning.
"""
from __future__ import annotations

import io
import sqlite3

import pytest

import cli
from production import (
    load_shipped_catalogue, read_packaged_library_file, shipped_situations,
    situation_schema_family,
)

QUESTION = "reading.organization:BUSIB4300"

#: The seven readings the two files' own words support, read off the recorded
#: question rather than guessed: `test_offers_every_reading_through_explain`
#: asserts the record still carries all of them.
TIED = ("academic", "business_operations", "college_applications", "creative",
        "engineering", "law_practice", "manufacturing")

#: The one of the seven that `academic.coursework` is among. Not a constant of
#: the library -- `situation_schema_family` is asked for it below -- but named
#: here because it is what the reader of this file needs to see.
IN_FAMILY = "academic"


def _corpus(tmp_path):
    corpus = tmp_path / "corpus"
    if corpus.is_dir():
        # A second gesture over the SAME folder and the same plan database, which
        # is what `--explain` and `--answer` are: a question exists only once a
        # run has found the ambiguity it is about.
        return corpus
    corpus.mkdir()
    (corpus / "Deposition.txt").write_text(
        "BUSIB 4300 Deposition Transcript\n\n"
        "Transcript of the witness in the seminar. Instructor: Dr. Ramirez. "
        "Credits: 3.\n")
    (corpus / "Second Deposition.txt").write_text(
        "BUSIB 4300 Deposition Transcript\n\n"
        "Second transcript of a witness. Instructor: Dr. Ramirez. Credits: 3.\n")
    (corpus / "Notes.txt").write_text(
        "Lecture Notes\n\nLecture notes for PHYS1401. Instructor office hours.\n")
    return corpus


def _run(tmp_path, *extra):
    out = io.StringIO()
    code = cli.main([str(_corpus(tmp_path)), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(tmp_path / "plan.sqlite"), *extra],
                    out=out)
    return code, out.getvalue()


def _answer_lines(printed: str) -> list[str]:
    return [line.strip() for line in printed.splitlines()
            if line.strip().startswith(f"--answer {QUESTION}=")]


def test_the_readings_the_typed_situation_is_among_are_offered_first(tmp_path):
    """The person said `academic.coursework`; `academic` leads the list.

    Ordering and not selection: the product does not answer the question, it
    stops making the person look for their own answer in a list of domains they
    never named.
    """
    _code, printed = _run(tmp_path)
    offered = _answer_lines(printed)
    assert offered, printed
    assert offered[0].startswith(f"--answer {QUESTION}={IN_FAMILY} "), printed


def test_the_readings_the_situation_is_not_among_are_folded_behind_explain(tmp_path):
    """Six of seven are not printed on the plain report, and the command that
    prints them is -- on its own line, so it survives being pasted."""
    _code, printed = _run(tmp_path)
    offered = " ".join(_answer_lines(printed))
    for reading in TIED:
        if reading == IN_FAMILY:
            continue
        assert f"{QUESTION}={reading}" not in offered, (
            f"{reading} is not the kind of material this person named and the "
            f"report still asks them to choose it:\n{printed}")
    assert f"      --explain {QUESTION}" in printed.splitlines(), printed


def test_every_reading_the_evidence_produced_is_still_offered_by_explain(tmp_path):
    """The fold is presentation. `--explain` is the command printed beside it and
    it lists all seven, so nothing the file's own words support is lost."""
    # The plain run first: a question exists only once a run has found the
    # ambiguity it is about, which is what `--explain` refuses without.
    _run(tmp_path)
    _code, printed = _run(tmp_path, "--explain", QUESTION)
    for reading in TIED:
        assert f"--answer {QUESTION}={reading}" in printed, (
            f"{reading} was folded out of the report and --explain does not "
            f"bring it back:\n{printed}")


def test_a_folded_reading_is_still_an_answer_the_product_accepts(tmp_path):
    """`00`'s closed vocabulary is the evidence's answer, not the screen's. A
    person who read `--explain` and typed the reading it named must be answered,
    not refused for having found an option the shorter list did not print."""
    _run(tmp_path)
    code, printed = _run(tmp_path, "--answer", f"{QUESTION}=law_practice")
    assert code == 0, printed
    conn = sqlite3.connect(tmp_path / "plan.sqlite")
    rows = conn.execute(
        "SELECT option_id, state FROM structural_answers "
        "WHERE question_id = ?", (QUESTION,)).fetchall()
    conn.close()
    assert rows == [("law_practice", "confirmed")], printed


def test_the_first_class_answers_are_never_folded(tmp_path):
    """`66` §14 keeps "It is not about me" and "skip for now" first-class, and an
    answer a person has to run a second command to find is not first-class."""
    _code, printed = _run(tmp_path)
    offered = " ".join(_answer_lines(printed))
    assert f"{QUESTION}=not_mine" in offered, printed
    assert f"{QUESTION}=skip" in offered, printed


def test_the_family_narrows_every_shipped_situation_and_empties_none():
    """The library's own hierarchy, asked of all 208 situations at once.

    A family that returned all twenty-three would fold nothing and a family that
    returned none would fold everything; the measurement that made this the rule
    is that 194 situations name one domain, 7 name two and 7 name three.
    """
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    names = sorted({row.name for row in shipped_situations(catalogue)})
    assert len(names) == 208, len(names)
    for name in names:
        family = situation_schema_family(catalogue, name)
        assert family, name
        assert len(family) <= 3, (name, family)
        assert len(set(family)) == len(family), (name, family)
    assert situation_schema_family(catalogue, "academic.coursework") == (
        "academic", "research", "code"), (
        "`def.subject-work-record` is what makes these three one family, and it "
        "is the library's statement rather than this test's")


def test_a_report_with_no_family_prints_what_it_always_printed(tmp_path):
    """The default. Hundreds of callers pass no family, and a fold they did not
    ask for would be this change reaching them by omission."""
    from questions.records import QuestionOption, StructuralQuestion
    from questions.vocabulary import STRUCTURAL

    question = StructuralQuestion(
        question_id=QUESTION, answer_class=STRUCTURAL,
        prompt="What kind of material is BUSIB4300?",
        evidence_context="2 files mention BUSIB4300.",
        unlocks="This decides which folder layout is offered.",
        will_not_do="It will not move, rename or delete anything.",
        scope="organization:BUSIB4300", handling_class="personal_non_sensitive",
        options=tuple(QuestionOption(reading, f"{reading} material",
                                     activates_schema=reading)
                      for reading in TIED),
        evidence_refs=("subject:BUSIB4300",))
    lines = cli._option_lines(question, ())
    for reading in TIED:
        assert any(f"{QUESTION}={reading} " in f"{line} " for line in lines), (
            reading, lines)
    assert not any("--explain" in line for line in lines), lines


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__]))
