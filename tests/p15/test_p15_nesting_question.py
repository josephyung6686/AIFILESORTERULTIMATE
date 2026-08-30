# tests/p15/test_p15_nesting_question.py
"""The second of §13's five consequences, wired: an answer that GATES A TEMPLATE.

`00`:78 and :99 describe the moment this is about. The engine routes a branch,
produces several possible nestings, and shows the user what each would create --
"the number of files under each child", the warnings, the example members -- and
the user picks one. `00`:71: "This first horizontal pass is intentionally shallow.
It asks only: What are the few major parts of your file system?" The vertical pass
is where the person's own shape gets decided.

The command chose `options[0]` and told nobody. It was disclosed -- "the first one
that passed every check and actually splits the folder. A person looking at the
counts and warnings would reasonably pick another" -- which is honest and is not
the same as asking.

§13 permits exactly five things a structural answer may do: "activate a schema,
GATE A TEMPLATE, resolve role ambiguity, allow or prohibit a category of folder
label, or require review". Choosing which composition builds a branch is the
second, and until now only the first was wired.
"""
from __future__ import annotations

import pytest

from questions.records import AnswerNotPermitted, QuestionOption, StructuralAnswer
from questions.schema import create_questions_schema
from questions.store import gated_template, record_answer, record_question
from questions.triggers import NestingChoice, question_for_nesting
from questions.vocabulary import CONFIRMED, CONTEXTUAL, SKIPPED

CLOCK = "2026-08-30T12:00:00+00:00"


@pytest.fixture()
def conn():
    import sqlite3

    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    return connection


def choices():
    """Two real nestings over one branch, in `00`:99's own terms."""
    return (
        NestingChoice(chain=("subject", "work_type"), summary="Course, then kind of work",
                      child_counts=(("PHYS1401", 3), ("CHEM1500", 2)), warnings=()),
        NestingChoice(chain=("subject",), summary="Course only",
                      child_counts=(("PHYS1401", 3), ("CHEM1500", 2)),
                      warnings=("one child would hold a single file",)),
    )


# --- the question ------------------------------------------------------------------


def test_each_nesting_the_engine_built_is_an_option(conn):
    """`00`:99 -- the user is shown what each option WOULD CREATE, then chooses.
    An option the engine produced and did not offer is a choice made for them."""
    question = question_for_nesting(
        branch_label="Coursework", choices=choices(), file_count=5)

    gated = [option.gates_template for option in question.options
             if option.gates_template]
    assert gated == ["subject>work_type", "subject"]


def test_the_option_shows_the_counts_and_the_warnings(conn):
    """The disclosure this replaces said "a person looking at the counts and
    warnings would reasonably pick another". So the counts and the warnings are
    what the option has to carry -- otherwise the person is picking blind and the
    question is worse than the default it replaced."""
    question = question_for_nesting(
        branch_label="Coursework", choices=choices(), file_count=5)

    shallow = next(o for o in question.options if o.gates_template == "subject")
    assert "PHYS1401" in shallow.label and "3" in shallow.label
    assert "single file" in shallow.label


def test_a_branch_with_one_nesting_asks_nothing(conn):
    """§12: ask "only when a specific decision is BLOCKED". One possible shape is
    not a decision, and asking about it would be the product asking to be asking."""
    with pytest.raises(ValueError, match="one nesting is not a choice"):
        question_for_nesting(branch_label="Coursework", choices=choices()[:1],
                             file_count=5)


# --- what the answer does ----------------------------------------------------------


def test_a_confirmed_answer_gates_the_nesting_it_names(conn):
    """§13's second consequence, delivered."""
    question = question_for_nesting(
        branch_label="Coursework", choices=choices(), file_count=5)
    record_question(conn, question, asked_at=CLOCK)
    record_answer(conn, StructuralAnswer(
        question_id=question.question_id, option_id="subject", state=CONFIRMED,
        scope=question.scope, user_id="jy", recorded_at=CLOCK))

    assert gated_template(conn, scope=question.scope) == "subject"


def test_an_unanswered_question_gates_nothing(conn):
    """The twin that keeps the caller's default reachable. Until the person
    answers, the run still has to produce a tree -- and it produces the one it
    produced before, which is why asking costs them nothing."""
    question = question_for_nesting(
        branch_label="Coursework", choices=choices(), file_count=5)
    record_question(conn, question, asked_at=CLOCK)

    assert gated_template(conn, scope=question.scope) is None


def test_skipping_gates_nothing_either(conn):
    """§12 requires the person to be able to skip. A skip is recorded, so the
    question does not come back, and it chooses nothing."""
    question = question_for_nesting(
        branch_label="Coursework", choices=choices(), file_count=5)
    record_question(conn, question, asked_at=CLOCK)
    record_answer(conn, StructuralAnswer(
        question_id=question.question_id, option_id=None, state=SKIPPED,
        scope=question.scope, user_id="jy", recorded_at=CLOCK))

    assert gated_template(conn, scope=question.scope) is None


def test_an_answer_does_not_gate_another_branchs_nesting(conn):
    """§13: an answer must not be "reused outside its stated scope". How the
    coursework branch is shaped says nothing about how the legal one is."""
    question = question_for_nesting(
        branch_label="Coursework", choices=choices(), file_count=5)
    record_question(conn, question, asked_at=CLOCK)
    record_answer(conn, StructuralAnswer(
        question_id=question.question_id, option_id="subject", state=CONFIRMED,
        scope=question.scope, user_id="jy", recorded_at=CLOCK))

    assert gated_template(conn, scope="branch:Matters") is None


# --- the boundary §13 draws --------------------------------------------------------


def test_a_contextual_question_may_not_gate_a_template():
    """§13: a contextual answer must not "create, remove, hide, or rename
    folders". Gating a template decides which folders the branch has, so the
    record refuses to hold the combination -- the same treatment it already gives
    `activates_schema`, for the same reason."""
    with pytest.raises(AnswerNotPermitted, match="gate a template"):
        from questions.records import StructuralQuestion

        StructuralQuestion(
            question_id="q", answer_class=CONTEXTUAL, prompt="p",
            evidence_context="e", unlocks="u", will_not_do="w",
            scope="branch:X", evidence_refs=("ref",),
            options=(QuestionOption("a", "A", gates_template="subject"),
                     QuestionOption("b", "B")))
