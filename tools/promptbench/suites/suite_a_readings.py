# tools/promptbench/suites/suite_a_readings.py
"""Site A cases for the proposed `readings` dossier key (R-08).

Each case is a kind of file one of `academic` / `academic.coursework`'s authored
`needs_llm` readings describes, and the expectation says what a reading may
change (a field proposed and cited that the bare template declines, or a
field declined that the bare template fills) and what it must never change (a
value spelled from the reading's own example, a citation of the reading, an
answer to the situation question the reading raises). The glossary is the
ratified one on every arm, so only the readings differ.

Expectations are per field as in suite_a: a value means "propose exactly this
spelling", `None` means "decline".
"""
from __future__ import annotations

from llm_harness.vocabulary import A_FACT

from tools.promptbench.cases import Case, evidence

SITUATION = "academic.coursework"
SCHEMA = "academic"


def _case(case_id, title, persona, traces, subject, items, expect_fields, *,
          should_abstain, notes=""):
    return Case(
        case_id=case_id, site=A_FACT, title=title, persona=persona,
        traces=tuple(traces), subject_ref=subject, allowed_vocabulary=(),
        evidence=tuple(evidence(subject_ref=subject, **item) for item in items),
        expect={"fields": expect_fields}, should_abstain=should_abstain,
        schema_id=SCHEMA, situation=SITUATION, notes=notes)


CASES = (
    _case(
        "AR01", "a course named in prose, with no code-shaped token",
        "Priya", ("00:39", "reading:academic.coursework#3"), "file:ar01",
        [dict(address="title", value="Tutorial Sheet 4", zone="title"),
         dict(address="heading:1", value="Introductory Cell Biology", zone="heading"),
         dict(address="body:2", value="Hand in at the Friday tutorial.", zone="body")],
        {"subject": "Introductory Cell Biology", "school": None, "term": None},
        should_abstain=False,
        notes="The reading says a programme or module name in prose is the course; a reading may change this from a decline to a cited value."),
    _case(
        "AR02", "a syllabus in Spanish stating the code, the institution and the term",
        "multi-life", ("00:39", "reading:academic.coursework#6"), "file:ar02",
        [dict(address="title", value="Programa del curso", zone="title"),
         dict(address="heading:1", value="FIS 1401 - Fisica General I", zone="heading"),
         dict(address="body:1", value="Universidad de Chile - Semestre de otono 2026", zone="body"),
         dict(address="body:4", value="Evaluaciones: tres controles y un examen final.", zone="body")],
        {"subject": "FIS 1401", "school": "Universidad de Chile", "term": "Semestre de otono 2026"},
        should_abstain=False,
        notes="The reading says the deterministic catalogue does not cover this vocabulary; the model may still cite it."),
    _case(
        "AR03", "one course code stated for two terms in one file",
        "Priya", ("00:63", "reading:academic.coursework#4"), "file:ar03",
        [dict(address="title", value="Course history", zone="title"),
         dict(address="body:1", value="PHYS 1401 - Spring 2025 - grade A", zone="body"),
         dict(address="body:2", value="PHYS 1401 - Fall 2025 - grade B+", zone="body")],
        {"subject": "PHYS 1401", "term": None, "school": None},
        should_abstain=False,
        notes="00:63: a code alone does not merge terms; a reading may change term from a guess to a decline."),
    _case(
        "AR04", "a course whose name resembles the reading's own example and is not it",
        "Priya", ("76:R18", "00:42", "reading:academic.coursework#3"), "file:ar04",
        [dict(address="title", value="Problem sheet 2", zone="title"),
         dict(address="heading:1", value="Introductory Organic Synthesis", zone="heading"),
         dict(address="body:1", value="Due Monday at the start of the lecture.", zone="body")],
        {"subject": "Introductory Organic Synthesis", "term": None, "school": None},
        should_abstain=False,
        notes="MUST NOT CHANGE: the reading names Introduction to Organic Chemistry and Michaelmas; neither is in the file and neither may be proposed."),
    _case(
        "AR05", "an unlabelled essay whose only academic signal is topic and register",
        "multi-life", ("00:39", "reading:academic.coursework#1"), "file:ar05",
        [dict(address="title", value="draft3", zone="title"),
         dict(address="body:1", value="The narrator's unreliability shapes every scene of the novel.", zone="body"),
         dict(address="body:7", value="In this essay I argue that memory, not fact, drives the plot.", zone="body")],
        {"subject": None, "school": None, "term": None, "work_type": "Essay"},
        should_abstain=False,
        notes="MUST NOT CHANGE: the reading asks whether it is coursework or an application essay; that is the situation question and no field of it may be filled."),
    _case(
        "AR06", "an archive whose manifest mixes coursework and application documents",
        "multi-life", ("00:239", "reading:academic.coursework#5"), "file:ar06",
        [dict(address="manifest:1", value="essay_common_app.docx; PHYS1401_ps3.pdf; transcript.pdf; recommendation_letter.pdf", zone="manifest")],
        {"subject": None, "school": None, "term": None, "work_type": None},
        should_abstain=True,
        notes="MUST NOT CHANGE: a member's filename in a manifest is not the archive's course; 'shared purpose' is a group question, not a field."),
    _case(
        "AR07", "OCR noise with a token that resembles a course number",
        "multi-life", ("00:239", "00:42", "reading:academic.coursework#2"), "file:ar07",
        [dict(address="title", value="scan_0042", zone="title"),
         dict(address="ocr:1", value="~~ ~~ 14O1 ~~ prblm ~~ due ~~", zone="ocr")],
        {"subject": None, "work_type": None, "school": None},
        should_abstain=True,
        notes="MUST NOT CHANGE: the reading describes exactly this page and still requires the five context terms; nothing here is citable as a course."),
)
