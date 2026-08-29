# tests/p15/test_p15_store.py
"""Recording a question, answering it, and finding the answer again NEXT RUN.

The property this file exists for is the one `66` §12 asks for and that nothing in
the product had: an answer that **outlives the run that asked for it**. A question
re-asked every time is a questionnaire, which §12 rejects by name, and a product
that forgets what it was told is worse than one that never asked.
"""
from __future__ import annotations

import sqlite3

import pytest

from questions.records import QuestionOption, StructuralAnswer, StructuralQuestion
from questions.schema import create_questions_schema
from questions.store import (
    AnswerConflict, answered_options, live_answer, open_questions, record_answer,
    record_question,
)
from questions.vocabulary import CONFIRMED, NOT_APPLICABLE, REVOKED, SKIPPED, STRUCTURAL

CLOCK = "2026-08-29T12:00:00+00:00"
LATER = "2026-08-30T09:00:00+00:00"
REF = "sha256:" + "ab" * 32


@pytest.fixture()
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    return connection


def a_question(question_id="relationship.organization:columbia",
               scope="organization:columbia") -> StructuralQuestion:
    return StructuralQuestion(
        question_id=question_id, answer_class=STRUCTURAL,
        prompt="Which describes your relationship to Columbia?",
        evidence_context="We found files connected to Columbia.",
        unlocks="This helps distinguish coursework from professional material.",
        will_not_do="It will not create or move folders by itself.",
        scope=scope,
        options=(
            QuestionOption("study", "I study there", activates_schema="academic"),
            QuestionOption("not_mine", "It is not about me"),
        ),
        evidence_refs=(REF,))


def an_answer(**overrides) -> StructuralAnswer:
    fields = dict(question_id="relationship.organization:columbia",
                  option_id="study", state=CONFIRMED,
                  scope="organization:columbia", user_id="jy",
                  recorded_at=CLOCK, inferred=False)
    fields.update(overrides)
    return StructuralAnswer(**fields)


# --- the loop that has to close ----------------------------------------------------


def test_an_answer_survives_the_run_that_asked_for_it(conn):
    """The whole point. A question asked in one run and answered by the person is
    still answered on the next run, without being asked again."""
    record_question(conn, a_question(), asked_at=CLOCK)
    assert open_questions(conn), "the question was not recorded as open"

    record_answer(conn, an_answer())

    assert not open_questions(conn), (
        "the question is still open after being answered; the person would be "
        "asked the same thing on every run, which is the questionnaire §12 rejects")
    assert live_answer(conn, question_id="relationship.organization:columbia",
                       scope="organization:columbia").option_id == "study"


def test_a_question_nobody_answered_stays_open(conn):
    """The negative twin. Recording a question must not look like answering it."""
    record_question(conn, a_question(), asked_at=CLOCK)
    assert [q.question_id for q in open_questions(conn)] == [
        "relationship.organization:columbia"]


def test_asking_the_same_question_twice_does_not_duplicate_it(conn):
    """A second run over the same corpus raises the same question from the same
    evidence. It is one question, asked once and still open -- not two."""
    record_question(conn, a_question(), asked_at=CLOCK)
    record_question(conn, a_question(), asked_at=LATER)

    assert len(open_questions(conn)) == 1
    row = conn.execute(
        "SELECT first_asked_at FROM structural_questions").fetchone()
    assert row["first_asked_at"] == CLOCK, (
        "re-asking overwrote when it was first asked; the person's own history "
        "of being asked is part of what §12's revocation story reads")


# --- skip, decline, and revoke are all real answers --------------------------------


def test_a_skipped_question_is_answered_and_does_not_come_back(conn):
    """§14: "skip for now" is FIRST-CLASS. A skip that left the question open
    would re-ask it every run, which is exactly the pressure §12 forbids."""
    record_question(conn, a_question(), asked_at=CLOCK)
    record_answer(conn, an_answer(option_id=None, state=SKIPPED))

    assert not open_questions(conn)
    assert live_answer(conn, question_id="relationship.organization:columbia",
                       scope="organization:columbia").state == SKIPPED


def test_not_about_me_is_recorded_as_its_own_answer(conn):
    """§14: "It must preserve 'not about me' ... as first-class." It is not a skip
    and not a choice; it is the person telling the product it guessed wrong about
    whose material this is."""
    record_question(conn, a_question(), asked_at=CLOCK)
    record_answer(conn, an_answer(option_id=None, state=NOT_APPLICABLE))

    assert live_answer(conn, question_id="relationship.organization:columbia",
                       scope="organization:columbia").state == NOT_APPLICABLE


def test_an_answer_can_be_changed_and_the_old_one_is_kept(conn):
    """§12: an answer must be "edited, revoked, or re-run". Kept, not overwritten:
    a plan was frozen under the old answer and the record of why must survive."""
    record_question(conn, a_question(), asked_at=CLOCK)
    first = record_answer(conn, an_answer())
    record_answer(conn, an_answer(
        option_id="not_mine", recorded_at=LATER, supersedes=first,
        supersede_reason="the user corrected this at review"))

    live = live_answer(conn, question_id="relationship.organization:columbia",
                       scope="organization:columbia")
    assert live.option_id == "not_mine"
    assert conn.execute("SELECT COUNT(*) FROM structural_answers").fetchone()[0] == 2


def test_a_revoked_answer_decides_nothing_and_stays_on_disk(conn):
    """Revocation is not deletion. The answer stops governing; the fact that it was
    once given does not stop being true."""
    record_question(conn, a_question(), asked_at=CLOCK)
    first = record_answer(conn, an_answer())
    record_answer(conn, an_answer(
        option_id=None, state=REVOKED, recorded_at=LATER, supersedes=first,
        supersede_reason="the user withdrew this"))

    assert answered_options(conn, scope="organization:columbia") == (), (
        "a revoked answer is still activating a schema")
    assert conn.execute("SELECT COUNT(*) FROM structural_answers").fetchone()[0] == 2
    assert [q.question_id for q in open_questions(conn)] == [
        "relationship.organization:columbia"], (
        "a revoked answer left the question closed, so the person could never be "
        "asked again about a decision they explicitly reopened")


# --- scope, which is what stops an answer leaking --------------------------------


def test_an_answer_does_not_apply_outside_its_scope(conn):
    """§13: an answer must not be "reused outside its stated scope". The person
    said what Columbia is to them. They said nothing about NYU."""
    record_question(conn, a_question(), asked_at=CLOCK)
    record_answer(conn, an_answer())

    assert live_answer(conn, question_id="relationship.organization:columbia",
                       scope="organization:nyu") is None


def test_two_scopes_of_one_question_are_answered_independently(conn):
    """A person may study at one institution and work at another. One question
    text, two scopes, two answers, and neither speaks for the other."""
    record_question(conn, a_question(question_id="relationship.organization:columbia"),
                    asked_at=CLOCK)
    record_question(conn, a_question(question_id="relationship.organization:nyu",
                                     scope="organization:nyu"), asked_at=CLOCK)
    record_answer(conn, an_answer())
    record_answer(conn, an_answer(question_id="relationship.organization:nyu",
                                  option_id="not_mine", scope="organization:nyu"))

    assert live_answer(conn, question_id="relationship.organization:columbia",
                       scope="organization:columbia").option_id == "study"
    assert live_answer(conn, question_id="relationship.organization:nyu",
                       scope="organization:nyu").option_id == "not_mine"


def test_an_answer_to_a_question_nobody_asked_is_refused(conn):
    """An answer with no question is an assertion about the user that nothing
    prompted -- the profile data §12 refuses to collect, arriving through the back
    door."""
    with pytest.raises(AnswerConflict, match="no question"):
        record_answer(conn, an_answer())


def test_an_answer_naming_an_option_the_question_does_not_offer_is_refused(conn):
    """A typo in an answer must not read as a choice, and a caller must not be able
    to widen the option set by answering."""
    record_question(conn, a_question(), asked_at=CLOCK)
    with pytest.raises(AnswerConflict, match="does not offer"):
        record_answer(conn, an_answer(option_id="teach"))
