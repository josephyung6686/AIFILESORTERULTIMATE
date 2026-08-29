# tests/p15/test_p15_consumption.py
"""The half that makes P15 a mechanism rather than a table: what an answer DOES.

`66` §21's warning is the reason this file exists:

> Questions must be wired into those mechanisms INTENTIONALLY. They must not be
> introduced as recurring engagement prompts or asked weekly because the product
> wants more profile data.

A registry nothing consumes is a questionnaire with extra steps. So every test
here is about a decision that CHANGES because a person answered, and every one has
the twin showing it does not change when they did not.
"""
from __future__ import annotations

import pytest

from questions.records import QuestionOption, StructuralAnswer
from questions.schema import create_questions_schema
from questions.store import activated_schemas, record_answer, record_question
from questions.triggers import question_for_tied_reading, tied_readings
from questions.vocabulary import CONFIRMED, NOT_APPLICABLE, SKIPPED

CLOCK = "2026-08-29T12:00:00+00:00"


@pytest.fixture()
def conn():
    import sqlite3

    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    return connection


# --- the question is derived from evidence, never written down ---------------------


def test_the_options_are_exactly_the_readings_the_files_own_words_support():
    """§14: the question is "narrow, evidence-linked". Offering a reading the
    evidence does not support would be guessing on the person's behalf about what
    their own file might be; offering fewer would hide a reading the product
    itself produced."""
    question = question_for_tied_reading(
        subject_value="CV20261234", tied_schema_ids=("law_practice", "finance"),
        file_count=3, evidence_refs=("subject:CV20261234",))

    activating = {option.activates_schema for option in question.options
                  if option.activates_schema}
    assert activating == {"law_practice", "finance"}
    assert "CV20261234" in question.prompt
    assert "3 files" in question.evidence_context


def test_not_about_me_is_always_offered_and_activates_nothing():
    """§14: "It must preserve 'not about me' ... as first-class." It is the answer
    a person gives when the product has guessed wrong about whose material this
    is, and it must never be the thing that turns a schema on."""
    question = question_for_tied_reading(
        subject_value="X12345678", tied_schema_ids=("identity", "creative"),
        file_count=1, evidence_refs=("subject:X12345678",))

    not_mine = [o for o in question.options if o.option_id == "not_mine"]
    assert not_mine and not_mine[0].activates_schema is None


def test_one_reading_is_not_an_ambiguity_and_asks_nothing():
    """The negative twin, and the guard against a product that asks to be asking.
    §12: ask "only when a specific decision is BLOCKED"."""
    with pytest.raises(ValueError, match="one reading is not an ambiguity"):
        question_for_tied_reading(
            subject_value="PHYS1401", tied_schema_ids=("academic",),
            file_count=2, evidence_refs=("subject:PHYS1401",))


def test_four_files_of_one_course_tying_the_same_way_ask_once(conn):
    """§14 asks on a "repeated ambiguity" -- and four files tying identically are
    ONE ambiguity. A person answering the same question four times would rightly
    conclude the product was not listening."""

    class Tied:
        tied_schema_ids = ("academic", "creative")
        evidence_refs = ()

    files = [(f"file-{n}", "hash") for n in range(4)]
    questions = tied_readings(
        conn, explain=lambda c, f, h: Tied(), files=files,
        subject_of={f"file-{n}": "PHYS1401" for n in range(4)})

    assert len(questions) == 1
    assert "4 files" in questions[0].evidence_context


def test_a_corpus_with_nothing_ambiguous_asks_nothing(conn):
    """The twin that matters most for §12's promise not to interrogate anybody:
    a run where the evidence settled everything raises no question at all."""

    class Settled:
        tied_schema_ids = ()
        evidence_refs = ()

    questions = tied_readings(
        conn, explain=lambda c, f, h: Settled(), files=[("file-0", "hash")],
        subject_of={"file-0": "PHYS1401"})

    assert questions == ()


# --- what a confirmed answer actually changes --------------------------------------


def test_a_confirmed_answer_activates_the_schema_it_names(conn):
    """§13: a structural answer "may ACTIVATE A SCHEMA". This is that consequence,
    and it is the one the whole loop exists to deliver."""
    question = question_for_tied_reading(
        subject_value="PHYS1401", tied_schema_ids=("academic", "creative"),
        file_count=2, evidence_refs=("subject:PHYS1401",))
    record_question(conn, question, asked_at=CLOCK)
    record_answer(conn, StructuralAnswer(
        question_id=question.question_id, option_id="academic", state=CONFIRMED,
        scope=question.scope, user_id="jy", recorded_at=CLOCK))

    assert activated_schemas(conn) == frozenset({"academic"})


@pytest.mark.parametrize("state", [SKIPPED, NOT_APPLICABLE])
def test_a_declined_question_activates_nothing(conn, state):
    """Both twins at once. A skip and a "not about me" are real, recorded answers
    -- the question does not come back -- and neither turns a schema on.

    This is the property that lets §14 offer them honestly. An option that
    silently did something would make declining a decision, and a person who
    cannot decline is being pressured, which is what §12 forbids.
    """
    question = question_for_tied_reading(
        subject_value="PHYS1401", tied_schema_ids=("academic", "creative"),
        file_count=2, evidence_refs=("subject:PHYS1401",))
    record_question(conn, question, asked_at=CLOCK)
    record_answer(conn, StructuralAnswer(
        question_id=question.question_id, option_id=None, state=state,
        scope=question.scope, user_id="jy", recorded_at=CLOCK))

    assert activated_schemas(conn) == frozenset()


def test_an_answer_activates_nothing_outside_its_own_scope(conn):
    """§13: an answer must not be "reused outside its stated scope". Telling the
    product that PHYS1401 is coursework says nothing about a matter number."""
    question = question_for_tied_reading(
        subject_value="PHYS1401", tied_schema_ids=("academic", "creative"),
        file_count=2, evidence_refs=("subject:PHYS1401",))
    record_question(conn, question, asked_at=CLOCK)
    record_answer(conn, StructuralAnswer(
        question_id=question.question_id, option_id="academic", state=CONFIRMED,
        scope=question.scope, user_id="jy", recorded_at=CLOCK))

    assert activated_schemas(conn, scope="organization:CV20261234") == frozenset()
    assert activated_schemas(conn, scope="organization:PHYS1401") == frozenset(
        {"academic"})
