"""`104` §11.2 step 4's interim guard, measured against the detector it would use.

Step 4 proposes, until R-37's per-branch situation exists, "the detector's per-file
schema candidates in place of `signal_evaluator_for=lambda domain: True`, so a file
the recogniser reads as `career` is not asked `subject`". Two things had to be true
for that to help. Both were measured on 2026-09-06, offline and with no model, over
the owner's `sample/Desktop` and over the three-file corpus below, and NEITHER IS.

* THE RECOGNISER ABSTAINS ON THE FILE THE STEP WAS WRITTEN FOR. A résumé comes back
  an `Abstention`, `ambiguous`, tied between `career` and `college_applications`.
  The guard's own third case keeps the run's situation for a file with no
  recognition -- coverage is sacred and an abstention is not evidence of anything --
  so the guard does not fire and the résumé is still offered `subject`.
* AND IT ABSTAINS ON THE NOTEBOOKS TOO -- WHICH THIS FILE USED TO DENY. The
  paragraph here read "the recogniser FIRES on the files the run gets right: four of
  the five `Python 1006` lecture notebooks come back `Recognition(code)` on the
  authored term `notebook`." **That measurement was an artifact of how a notebook
  was serialised, and R-166 measured it away.** Before `104` R-160 the extractor
  stored a `.ipynb` as its raw JSON, and `code`'s authored terms include `cell`,
  `source`, `kernel` and `notebook` -- which a notebook's JSON carries as DICTIONARY
  KEYS (`"cells"`, `"source"`, `"kernelspec"`) whether or not one word of the
  document says anything about code. Four keys is four matches, `code` cleared
  `never_alone` on punctuation, and won. R-160 made a notebook's cells be read as
  their own text; the keys went with the braces; and what is left is one real term
  on each side -- `lecture` in the markdown cell, `import` in the code cell. The
  verdict today is `Abstention(no_corroboration, tied=(academic, code))`.

  THAT ABSTENTION IS THE CORRECT ANSWER AND NOT A REGRESSION. A course notebook IS
  a lecture and IS Python, its own words say both exactly once, and `00`:39 gives
  a file that "remains ambiguous" or has "multiple plausible domains" to the model
  rather than to a rule. What the four notebooks lost is not a recognition; it is
  a win that was never about the document. `tests/recognition/
  test_recognition_serialisation_is_not_evidence.py` is the guard that would have
  caught it, and it is a guard rather than a repair: the fix is NOT to give `code`
  more terms until it wins again.

THE DETECTOR IS NOT WRONG, AND IT IS WRONG ABOUT NOTHING NOW THAT THE FIRST BULLET
IS HONEST. It answers "what is this file made of"; the guard needs "which situation
is this file part of". A Jupyter notebook of a Python course is honestly both, and
no reading of the file settles which one the person meant. That is R-37's question,
and R-37 is the fix step 4 called itself the interim for. Step 4's guard is dead
either way -- it now has no file in this corpus to fire on at all.

`00`:41 IS NOT A ROUTE PAST IT. Writing the recognition as a file fact so the gate
can read it needs a field for it, and there is none: `fields.py` ships 56 rows,
`tests/p6/test_p6_fields.py` asserts that count three ways, and the row would be the
twin of the one that catalogue deliberately withholds (`sensitivity_status`, NEEDS-
JOSEPH C5, "do not close it by adding the row") -- P7's conclusion written into P6's
catalogue. The last test here is that gap, measured rather than argued: the schema
the detector settled on reaches no column any per-file gate could read.

Every test drives `cli.main` over a synthetic corpus. No model is configured
(`conftest` sets `GRAPH_AGENT_NO_DOTENV=1`) and nothing here reaches the network.
"""
from __future__ import annotations

import io
import json
import sqlite3

import pytest

import cli
from facts.domains import (
    ActivationSignal, ActivationSignals, active_field_allowlist,
)
from questions.store import activated_schemas
from recognition.detector import Abstention, Detector, Recognition
from recognition.rules import load_rules

SITUATION = "academic.coursework"
LABEL = "Coursework"

#: The schema `academic.coursework` resolves to, and the ONE signal
#: `fact_call_authorities` builds today: `activates` answers `True` for it and the
#: question is never asked about any other schema.
RUN_SCHEMA = "academic"

RESUME = "Jane Doe resume.txt"
LECTURE = "PHYS 1401 lecture 08.txt"
NOTEBOOK = "lecture01_introduction.ipynb"


def _notebook_bytes() -> str:
    """A course notebook: lecture prose in a markdown cell, Python in a code cell.

    The real files are `lecture01_introduction.ipynb` and its four neighbours. This
    is the same shape and it reproduces the same verdict, which is what makes it a
    fixture rather than an illustration.
    """
    return json.dumps({
        "cells": [
            {"cell_type": "markdown", "metadata": {},
             "source": ["# Lecture 01 Introduction\n",
                        "PYTHON 1006 Spring 2026 lecture notes.\n"]},
            {"cell_type": "code", "execution_count": 1, "metadata": {},
             "outputs": [],
             "source": ["import numpy as np\n", "def main():\n", "    return 42\n"]},
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.12.0"},
        },
        "nbformat": 4, "nbformat_minor": 5,
    })


@pytest.fixture(scope="module")
def measured(tmp_path_factory):
    """One offline run over three files, read back by every test in this file.

    Module scope because the run is the expensive part and no test here writes to
    the database: each asks the same finished run a different question.
    """
    root = tmp_path_factory.mktemp("step4")
    corpus = root / "corpus"
    corpus.mkdir()
    (corpus / RESUME).write_text(
        "Jane Doe\nCurriculum Vitae / Resume\n\n"
        "Work experience\n"
        "2024-2026  Software Engineer, Acme Corp. Job title: Software Engineer.\n"
        "2022-2024  Intern, Beta Ltd.\n\n"
        "Education\nBSc Computer Science, Columbia University, 2022\n\n"
        "Cover letter enclosed. Applying for the Senior Engineer role.\n"
        "References available on request.\n")
    (corpus / LECTURE).write_text(
        "PHYS 1401 Lecture 08\n"
        "Spring 2026 semester. Instructor: Dr. Ramirez.\n"
        "Syllabus reference: credits 4. Course lecture notes for PHYS 1401.\n"
        "Homework 3 is due next week. Problem set covered in this lecture.\n")
    (corpus / NOTEBOOK).write_text(_notebook_bytes())

    database = root / "plan.sqlite"
    out = io.StringIO()
    assert cli.main(
        [str(corpus), "--situation", SITUATION, "--label", LABEL,
         "--user", "t", "--database", str(database)], out=out) == 0, out.getvalue()

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _version(conn, filename: str) -> tuple[str, str]:
    row = conn.execute(
        "SELECT file_id, content_hash FROM files WHERE filename = ?",
        (filename,)).fetchone()
    assert row is not None, f"{filename!r} is not in the run"
    return row["file_id"], row["content_hash"]


def _verdict(conn, filename: str):
    """What the detector concluded about one file, built as `cli.run` builds it.

    SPELLED OUT RATHER THAN IMPORTED, and the duplication is part of the finding.
    `cli.run` composes this detector at its composition root and hands it to
    `classify`; `fact_call_authorities` is handed a connection and a schema and
    nothing else, so an interim guard living there would have to compose a second
    one exactly like this. There is no third option, because the verdict is not
    written anywhere it could be read back from instead -- which is the last test
    in this file.
    """
    rules = load_rules(cli._RECOGNITION_MANIFEST.read_text)
    detector = Detector(
        rules, handling_for=cli.HANDLING_POLICY,
        now=lambda: "2026-09-06T00:00:00+00:00",
        is_protected=cli.is_protected_container,
        corroborating_observations=cli._identifier_observations,
        settled_by_user=lambda: activated_schemas(conn))
    return detector.explain(conn, *_version(conn, filename))


def _allowlist(conn, filename: str, schema_id: str) -> tuple[str, ...]:
    """§3.5's closed vocabulary for one file, with exactly one schema active.

    P6's own function, not a copy: what the guard would change is which schema is
    handed to it, and this is the object that changes when it does.
    """
    file_id, content_hash = _version(conn, filename)
    return active_field_allowlist(
        conn, file_id=file_id, content_hash=content_hash,
        activation_signals=ActivationSignals(signals=(
            ActivationSignal(schema_id=schema_id, activates=lambda facts: True),)))


# --- what the recogniser says about the two files step 4 is about -----------------


def test_the_recogniser_abstains_on_a_resume_so_the_guard_never_fires_for_it(
        measured):
    """THE FILE STEP 4 WAS WRITTEN FOR, and the guard does not reach it.

    "A file the recogniser reads as `career` is not asked `subject`." It does not
    read this one as `career`. It reads it as two schemas at once and declines, and
    an abstention is the input the guard's third case keeps the run's situation for.
    """
    outcome = _verdict(measured, RESUME)

    assert isinstance(outcome, Abstention), (
        "the recogniser settled a résumé after all, which would make step 4's "
        "first case reachable for the file it was written for: " + repr(outcome))
    assert outcome.schema_id is None
    assert "career" in outcome.tied_schema_ids, outcome.tied_schema_ids
    assert "college_applications" in outcome.tied_schema_ids, outcome.tied_schema_ids


def test_a_course_notebook_reads_two_ways_and_that_is_the_models_question(
        measured):
    """THE FILE THAT WAS NEVER RECOGNISED, only serialised in `code`'s favour.

    This test used to assert `Recognition(code)` and it passed for a reason that
    was not about the document: the extractor stored the whole `.ipynb` as JSON,
    and `code` ships `cell`, `source`, `kernel` and `notebook` as authored terms,
    which the container's own dictionary keys supply. `104` R-160 made the cells
    be read as their own text and the four free matches went away with the braces.

    What the file itself says is one term each: `lecture` in the markdown cell and
    `import` in the code cell. Two readings, one signal apiece, neither outranking
    the other -- `never_alone` refuses to conclude, and `00`:39 hands exactly this
    file to the model: one that "remains ambiguous" and has "multiple plausible
    domains". The assertions below are that shape, not a schema.

    DO NOT REPAIR THIS BY MAKING `code` WIN. Adding terms until the old verdict
    comes back would re-author the artifact by hand, and the notebook would still
    be a lecture. The repair is that the tie becomes a question -- R-166 -- and
    `tests/recognition/test_recognition_serialisation_is_not_evidence.py` is what
    stops a container's punctuation standing in for an answer again.
    """
    outcome = _verdict(measured, NOTEBOOK)

    assert isinstance(outcome, Abstention), (
        "a course notebook was settled by a rule. Check first that it was not "
        "settled by the container's own keys, which is how this read `code` "
        "until 2026-09-08: " + repr(outcome))
    assert outcome.reason == "no_corroboration", outcome.reason
    assert set(outcome.tied_schema_ids) == {"academic", "code"}, (
        "the two readings a course notebook honestly has are the lecture in its "
        "markdown cell and the Python in its code cell: " + repr(outcome))
    assert outcome.deferred_readings, (
        "the abstention arrived with no authored reading attached, so there is "
        "nothing to put the question to a model in")


def test_the_notebooks_two_readings_are_each_one_term_of_the_documents_own_text(
        measured):
    """WHY IT IS A TIE, at the terms rather than at the verdict.

    The point of R-166's measurement is that the four matches `code` used to win on
    were the container's, so the ones that remain have to be the document's. Each
    side has exactly one, and each is a word a person wrote: `lecture` in the prose
    cell, `import` in the code cell. A tie at one term each is `never_alone`
    refusing on arity, which is why the reason is `no_corroboration` and not
    `ambiguous`.
    """
    outcome = _verdict(measured, NOTEBOOK)

    assert isinstance(outcome, Abstention), repr(outcome)
    assert "2 readings matched one term each" in outcome.detail, outcome.detail
    for structural in ("cells", "kernelspec", "nbformat", "cell_type"):
        assert structural not in outcome.detail, (
            f"{structural!r} is a notebook's JSON key, not something the document "
            "says, and it is deciding a reading again: " + outcome.detail)


def test_a_lecture_in_prose_is_recognised_academic_and_the_guard_would_agree(
        measured):
    """The harmless case, and it is why the defect is not "the detector is bad".

    The same corpus, the same detector, a lecture written as prose: `academic`, the
    run's own schema, so the guard's second case fires and nothing changes. What
    separates it from the notebook is the file's FORMAT, not its subject.
    """
    outcome = _verdict(measured, LECTURE)

    assert isinstance(outcome, Recognition), repr(outcome)
    assert outcome.schema_id == RUN_SCHEMA


# --- what firing would cost ------------------------------------------------------


def test_the_guard_would_take_subject_off_the_notebook_and_offer_it_a_repository(
        measured):
    """THE COST, at P6's own function rather than in prose.

    COUNTERFACTUAL SINCE R-166, AND KEPT FOR IT. The notebook abstains, so step 4's
    first case never reaches this file and the swap measured here never happens.
    What the numbers still say is what the swap WOULD cost if a rule ever settled a
    course notebook as `code` -- which is the outcome the old serialisation produced
    and the outcome nobody may restore by adding terms.

    `104` §11.2 step 3 and this branch's P10 rule both turn on `subject`: a level is
    minted from a value some file states, and the notebook is one of the files that
    states `E1006`. Swapping the active schema does not make the model answer
    better; it removes the question whose answer the tree is built from and asks a
    question no level in this template expects.
    """
    as_the_run_asks = _allowlist(measured, NOTEBOOK, RUN_SCHEMA)
    as_the_guard_would = _allowlist(measured, NOTEBOOK, "code")

    assert "subject" in as_the_run_asks and "work_type" in as_the_run_asks
    assert "subject" not in as_the_guard_would, (
        "the guard was expected to remove `subject` from a file the run places "
        "on it; if it no longer does, this measurement needs redoing")
    assert "repository" in as_the_guard_would
    assert not (set(as_the_guard_would) & {"school", "term", "subject",
                                           "instructor", "work_type"}), (
        "the guard left one of the coursework levels in the allowlist, which "
        "would make the cost measured here smaller than it is")


# --- and why it cannot simply be read back ---------------------------------------


def test_the_schema_the_detector_settled_on_is_not_written_down_anywhere(measured):
    """`Detector.__call__` indexes its handling policy with `schema_id` and drops it.

    The row it writes carries a handling class, a protected flag, a basis and the
    evidence refs; `basis` is the deployment's word for how the class was reached
    and is the same word for every ordinary schema. So a per-file gate has nothing
    to read, which is why `_verdict` above has to compose a second detector, and
    why the "write it as a file fact" route needs a 57th row in a catalogue pinned
    at 56.
    """
    rows = measured.execute("SELECT * FROM classifications").fetchall()
    assert rows, "the run classified nothing, so this proves nothing"

    columns = set(rows[0].keys())
    assert not (columns & {"schema_id", "schema", "situation", "domain"}), columns
    assert {row["basis"] for row in rows} == {"detector_no_safety_evidence"}, (
        "`basis` started telling the schemas apart, which would make it a place "
        "a per-file gate could read the verdict from")
