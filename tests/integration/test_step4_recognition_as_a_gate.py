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
* AND THE NOTEBOOKS WERE NEVER RECOGNISED AS `code` BY ANYTHING THEY SAID -- WHICH
  THIS FILE USED TO DENY, AND WHICH THE FIRST R-166 COMMIT GOT WRONG TOO. The
  paragraph here read "the recogniser FIRES on the files the run gets right: four of
  the five `Python 1006` lecture notebooks come back `Recognition(code)` on the
  authored term `notebook`." The term is real; where it came from is not the
  document.

  MEASURED 2026-09-08, at `5ff35c0` and identically at `8eb41e0`.
  `extractors.structured_text` emits the reader's `document.language` -- §2.4's
  "language where relevant" -- as an observation of its own, and for a notebook the
  reader fills it with the string `Jupyter notebook`. `code` ships `notebook` as a
  WORK TYPE. So every `.ipynb` in existence carried a `code` term before one word of
  it was read, an empty one included. The SECOND signal `never_alone` requires came
  from the corroboration gate, which seconded that one term with `PYTHON 1006` and
  `Spring 2026` -- a course code and an academic term, which are evidence of
  coursework. A file was recognised as a code project by its file format plus its
  course number, and the four notebooks the run placed were placed on that.

  (The first R-166 commit reported the mechanism as four JSON dictionary keys read
  as four terms before `104` R-160, and reported a surviving `academic`/`code` tie.
  Both were wrong: the raw JSON matched `code` on the single word `code`, out of
  `"cell_type": "code"`, and the tie was the format's name against the heading. The
  measurement above replaces that account.)

  `recognition.detector._matches` now refuses a term match on that slot, for the
  reason it already refuses the `path` locator -- the name of the file's format is
  no more one of its words than the name of its directory is -- and for `_decide`'s
  own rule that `file_kind_plausible` "is a constraint and never a signal". With the
  container's name no longer voting, the same notebook is `Recognition(academic)` on
  `lecture` in its own first heading, corroborated by its own course code. That is
  what the file is.
  `tests/recognition/test_recognition_serialisation_is_not_evidence.py` holds it.

THE DETECTOR IS NOT WRONG, AND STEP 4'S GUARD IS DEAD FOR A DIFFERENT REASON NOW.
The finding above inverts the second bullet's argument: the guard would fire on the
notebook and it would AGREE with the run, because the schema the recogniser settles
on is `academic`, which is the run's own. It costs nothing here and it buys nothing
here. What is left of step 4 is the first bullet -- the résumé, which still abstains
tied between `career` and `college_applications`, is still the file the step was
written for, and is still the file the guard cannot reach. That is R-37's question,
and R-37 is the fix step 4 called itself the interim for.

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


def test_a_course_notebook_is_academic_once_the_containers_name_stops_voting(
        measured):
    """THE FILE THAT WAS NEVER RECOGNISED AS `code` BY ANYTHING IT SAID.

    This test used to assert `Recognition(code)` and it passed for a reason that
    was not about the document: `extractors.structured_text` stores the reader's
    `document.language` as an observation, for a notebook that value is the string
    `Jupyter notebook`, and `code` ships `notebook` as a work type. Every `.ipynb`
    carried that term, an empty one included, and the corroboration gate seconded
    it with `PYTHON 1006` -- a course code -- to reach `never_alone`'s arity.

    With the format's name refused (`_matches`, for the reason it already refuses
    the `path` locator), what is left is what the file says: `lecture`, in its own
    first heading, corroborated by its own course code. The verdict is `academic`,
    which is the run's own schema and the situation these files are placed under.
    `tests/recognition/test_recognition_serialisation_is_not_evidence.py` is the
    guard that keeps the container out of it.
    """
    outcome = _verdict(measured, NOTEBOOK)

    assert isinstance(outcome, Recognition), (
        "a course notebook stopped being recognised at all. Check first that its "
        "heading is still an observation: that is the only thing the document "
        "itself contributes: " + repr(outcome))
    assert outcome.schema_id == RUN_SCHEMA, (
        "if this says `code`, the container's own name is voting again: "
        + repr(outcome))


def test_every_term_behind_the_notebooks_verdict_is_one_the_document_carries(
        measured):
    """PROVENANCE, at the matches rather than at the verdict.

    The point of R-166's measurement is that the term `code` won on was the
    reader's word for the FORMAT, not the document's. So the terms that remain
    have to be the document's own, and the zone is what says so: `heading` is SPEC
    2.2's "page-one heading" and is in `NAMING_ZONES`; `metadata:field=language` is
    where the format's name sat.
    """
    outcome = _verdict(measured, NOTEBOOK)

    assert isinstance(outcome, Recognition), repr(outcome)
    assert outcome.matches, repr(outcome)
    for match in outcome.matches:
        assert match.zone != "metadata", (
            "a term behind this verdict came out of the metadata zone, which is "
            "where the container describes itself: " + repr(match))
    # `104` R-160 (cluster D, 10 Sep): a notebook's markdown cells are body units,
    # so the cell's second line -- "... lecture notes." -- is now the document's
    # own text too, and `notes` is a word a schema authored. Both terms are words
    # the document carries, which is what this test's name asserts; the term that
    # must NOT appear is still the reader's word for the format, `code`.
    assert {match.term for match in outcome.matches} == {"lecture", "notes"}, (
        "the words of this notebook that any schema authored are `lecture` and "
        "`notes`, both in its markdown cell: " + repr(outcome.matches))


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
