# tests/p15/test_p15_situation_question.py
"""§13's THIRD consequence: an answer resolves role ambiguity, per branch.

`66` §13 permits a structural answer five things. Two were wired (activate a
schema, gate a template) and this is the third: "resolve role ambiguity".

**What consumes it, and why it had to be per branch.** `--situation` takes ONE
string for a whole corpus and derives the schema from it. `68` F6 measured what
that costs a real person: Priya's whole disk is `academic.coursework` "including
the material that is `academic.teaching`, a situation the shipped library now
carries". She is a graduate student who also teaches. The product made her choose
which of her two lives to file, once, for every file she owns.

§16:543 says the same thing from the other end -- "being more than one thing is
normal" -- and that is why this and §16 are one mechanism rather than two.

**The trap this deliberately avoids.** `CompositionOverride.role_choices` is about a
TEMPLATE DIMENSION role (`subject_anchor`, `holder_institution`). §13's "role
ambiguity" is the USER's role: student or teacher, litigator or parent. They are
different nouns, and wiring the first to the second would be a category error that
typechecks. This consequence goes to the situation and never to C4.
"""
from __future__ import annotations

import sqlite3

import pytest

from questions.records import (
    AnswerNotPermitted, QuestionOption, StructuralQuestion,
)
from questions.records import StructuralAnswer
from questions.registry import QUESTION_KINDS, SITUATION_KIND, kind_of
from questions.schema import create_questions_schema
from questions.store import record_answer, record_question, selected_situation
from questions.triggers import question_for_situation
from questions.vocabulary import (
    CONFIRMED, CONTEXTUAL, NOT_APPLICABLE, SKIPPED, STRUCTURAL,
)

CLOCK = "2026-08-31T09:00:00+00:00"

#: `68` F6's own case, in the shipped library's own names.
PRIYAS_TWO_LIVES = ("academic.coursework", "academic.teaching")


@pytest.fixture()
def qconn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    yield connection
    connection.close()


def a_situation_question(**overrides) -> StructuralQuestion:
    fields = dict(branch_label="Teaching", situations=PRIYAS_TWO_LIVES,
                  file_count=1)
    fields.update(overrides)
    return question_for_situation(**fields)


# --- B1: the trigger ---------------------------------------------------------------


def test_two_situations_firing_on_one_branch_raise_one_question():
    """`68` F6. Both rows are carried by the shipped library, both fire on this
    branch's evidence, and the evidence cannot say which Priya meant."""
    question = a_situation_question(file_count=9)

    assert question.answer_class == STRUCTURAL
    assert question.scope == "branch:Teaching"
    assert kind_of(question.question_id) is SITUATION_KIND
    chosen = {option.selects_situation for option in question.options
              if option.selects_situation}
    assert chosen == set(PRIYAS_TWO_LIVES)
    # §12: the question names the decision it unlocks and what it will not do.
    assert question.unlocks and question.will_not_do
    assert "Teaching" in question.evidence_context


def test_one_situation_is_not_an_ambiguity_and_asks_nothing():
    """The negative twin, and the shape `question_for_nesting` already uses.

    One situation is an answer, not a question. Asking anyway would be the
    "generic list of questions" §12 rejects, arriving one branch at a time.
    """
    with pytest.raises(ValueError, match="one situation"):
        a_situation_question(situations=("academic.coursework",))
    with pytest.raises(ValueError, match="one situation"):
        a_situation_question(situations=())


def test_the_same_situation_named_twice_is_still_one_situation():
    """Two library rows may carry the same detection signal. That is one reading
    of the branch, not two, and a question offering the same answer twice would
    tell the person the product cannot read its own catalogue."""
    with pytest.raises(ValueError, match="one situation"):
        a_situation_question(
            situations=("academic.coursework", "academic.coursework"))


# --- B2: the consequence, and its read surface -------------------------------------


def test_a_confirmed_answer_selects_the_situation_for_that_branch_only(qconn):
    """Scoped, and required to be. §13 forbids an answer being "reused outside its
    stated scope", and a corpus-wide read is exactly what `--situation` already is
    and what this exists to replace."""
    question = a_situation_question()
    record_question(qconn, question, asked_at=CLOCK)
    record_answer(qconn, StructuralAnswer(
        question_id=question.question_id, option_id="academic.teaching",
        state=CONFIRMED, scope=question.scope, user_id="jy", recorded_at=CLOCK))

    assert selected_situation(qconn, scope="branch:Teaching") == "academic.teaching"
    assert selected_situation(qconn, scope="branch:Coursework") is None
    assert selected_situation(qconn, scope="corpus") is None


@pytest.mark.parametrize("state", [SKIPPED, NOT_APPLICABLE])
def test_an_unanswered_or_declined_branch_selects_no_situation(qconn, state):
    """The negative twin: asking must stay free.

    `None` for unanswered AND for declined -- different facts about the person and
    the same fact about the tree: neither chose a situation, so the caller keeps
    the one the run was given. `store.gated_template` states the same property for
    the nesting question, and it is what makes a new question safe to raise.
    """
    question = a_situation_question()
    record_question(qconn, question, asked_at=CLOCK)
    assert selected_situation(qconn, scope="branch:Teaching") is None

    record_answer(qconn, StructuralAnswer(
        question_id=question.question_id, option_id=None, state=state,
        scope=question.scope, user_id="jy", recorded_at=CLOCK))
    assert selected_situation(qconn, scope="branch:Teaching") is None


def test_the_situation_reader_requires_a_scope():
    """No default, for the reason `gated_template` has none: a corpus-wide read
    would let the situation somebody chose for their teaching decide the shape of
    their legal matters."""
    with pytest.raises(TypeError):
        selected_situation(sqlite3.connect(":memory:"))


def test_a_contextual_question_may_not_select_a_situation():
    """The third refusal, beside the two `records.py` already carries.

    A situation decides which applicability rows are eligible, which decides which
    templates are available, which decides which folders exist -- and §13 forbids a
    contextual answer to "create, remove, hide, or rename folders".
    """
    with pytest.raises(AnswerNotPermitted, match="situation"):
        StructuralQuestion(
            question_id="situation:X", answer_class=CONTEXTUAL, prompt="p",
            evidence_context="e", unlocks="u", will_not_do="w",
            scope="branch:X", handling_class="personal_non_sensitive",
            evidence_refs=("ref",),
            options=(QuestionOption("a", "A", selects_situation="academic.teaching"),
                     QuestionOption("b", "B")))


def test_the_situation_kind_is_registered_with_the_reader_that_consumes_it():
    """A1's ratchet, met rather than worked around: this consequence was added
    together with the mechanism that reads it, in one commit."""
    assert SITUATION_KIND in QUESTION_KINDS
    assert SITUATION_KIND.consequence_field == "selects_situation"
    assert SITUATION_KIND.reader is selected_situation
    assert SITUATION_KIND.scope_kind == "branch"
