# tests/p15/test_p15_answer_types.py
"""§21's fourth obligation: what SHAPE an answer may take, not only which value.

Until now every answer P15 could hold was a pick-one from a list the product
authored. That is one answer type, and `66` names two more requirements the shape
could not express:

> §16:555 -- it "should store the raw user wording"
> §16:543 -- "multiple roles, each with A SCOPE AND POSSIBLY A TIME PERIOD"

**The bound that makes free text safe.** §16:547 is categorical: "An unmatched
answer must remain unmatched. 'I'm a sound engineer' must not silently activate an
engineering or software-project schema merely because the words are superficially
similar." That could be a downstream policy somebody remembers to apply. Here it is
the data model: a free-text answer names no option, `answered_options` returns
options a confirmed answer SELECTED, and so a free-text answer reaches
`activated_schemas` and `gated_template` never. There is no path to write down.

Every test below is either that bound or the shape §16 asks for.
"""
from __future__ import annotations

import sqlite3

import pytest

from questions.records import (
    AnswerNotPermitted, QuestionOption, StructuralAnswer, StructuralQuestion,
)
from questions.schema import create_questions_schema
from questions.store import (
    activated_schemas, answered_options, gated_template, live_answer,
    record_answer, record_question,
)
from questions.vocabulary import (
    ANSWER_TYPES, CHOICE, CONFIRMED, FREE_TEXT, OutOfVocabulary, STRUCTURAL,
)

CLOCK = "2026-08-30T12:00:00+00:00"
REF = "sha256:" + "cd" * 32


@pytest.fixture()
def qconn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    yield connection
    connection.close()


def a_question(**overrides) -> StructuralQuestion:
    fields = dict(
        question_id="reading.organization:columbia",
        answer_class=STRUCTURAL,
        prompt="What kind of material is Columbia?",
        evidence_context="Four files mention Columbia.",
        unlocks="This decides which folder layout is offered.",
        will_not_do="It will not move, rename or delete anything.",
        scope="organization:columbia",
        handling_class="personal_non_sensitive",
        options=(QuestionOption("study", "I study there",
                                activates_schema="academic"),
                 QuestionOption("not_mine", "It is not about me")),
        evidence_refs=(REF,))
    fields.update(overrides)
    return StructuralQuestion(**fields)


def an_answer(**overrides) -> StructuralAnswer:
    fields = dict(question_id="reading.organization:columbia", option_id="study",
                  state=CONFIRMED, scope="organization:columbia", user_id="jy",
                  recorded_at=CLOCK)
    fields.update(overrides)
    return StructuralAnswer(**fields)


# --- the two types, closed ---------------------------------------------------------


def test_the_answer_types_are_two_and_the_default_is_the_one_that_shipped():
    """`CHOICE` is what every answer P15 has ever stored is, so it is the default
    and no existing row changes meaning."""
    assert ANSWER_TYPES == (CHOICE, FREE_TEXT)
    assert an_answer().answer_type == CHOICE


def test_an_answer_type_outside_the_two_is_refused():
    with pytest.raises(OutOfVocabulary):
        an_answer(answer_type="dictated")


# --- §16:555, the person's own words -----------------------------------------------


def test_a_free_text_answer_keeps_the_persons_own_words(qconn):
    """§16:555: the matcher "should store the raw user wording".

    Their words, byte for byte, through the store and back -- not a normalised,
    lowercased, or nearest-matched version of them. `4333227` already made this the
    house rule for a person's words elsewhere in the product.
    """
    record_question(qconn, a_question(), asked_at=CLOCK)
    record_answer(qconn, an_answer(
        option_id=None, answer_type=FREE_TEXT,
        raw_wording="I'm a sound engineer, and I teach one evening class"))

    live = live_answer(qconn, question_id="reading.organization:columbia",
                       scope="organization:columbia")
    assert live is not None
    assert live.answer_type == FREE_TEXT
    assert live.raw_wording == (
        "I'm a sound engineer, and I teach one evening class")


def test_a_free_text_answer_with_no_wording_is_refused():
    """Free text whose text is absent is a confirmed answer that says nothing, and
    it would sit in the store looking like a settled decision."""
    with pytest.raises(AnswerNotPermitted, match="raw_wording"):
        an_answer(option_id=None, answer_type=FREE_TEXT, raw_wording="")


def test_a_choice_answer_may_not_smuggle_raw_wording():
    """The two types are alternatives. A choice carrying wording as well would let
    a reader take the wording as the answer and the option as the answer, and the
    two need never agree."""
    with pytest.raises(AnswerNotPermitted, match="raw_wording"):
        an_answer(raw_wording="actually I meant something else")


# --- the bound: §16:547 enforced by the data model ---------------------------------


def test_a_free_text_answer_activates_no_schema_and_gates_no_template(qconn):
    """The negative twin, and the reason this task is safe.

    §16:547: "An unmatched answer must remain unmatched." A free-text answer
    selects no option, so it is not in `answered_options`, so it cannot reach
    either consequence. Nothing downstream has to remember this.
    """
    record_question(qconn, a_question(), asked_at=CLOCK)
    record_answer(qconn, an_answer(
        option_id=None, answer_type=FREE_TEXT, raw_wording="I'm a sound engineer"))

    assert answered_options(qconn, scope="organization:columbia") == ()
    assert activated_schemas(qconn) == frozenset()
    assert gated_template(qconn, scope="organization:columbia") is None


def test_a_free_text_answer_naming_an_option_is_refused():
    """The one path by which free text could reach a consequence, closed at the
    record. This is the guard the test above depends on."""
    with pytest.raises(AnswerNotPermitted, match="free text"):
        an_answer(option_id="study", answer_type=FREE_TEXT,
                  raw_wording="I study there")


def test_a_choice_answer_still_names_the_option_the_person_chose():
    """The positive twin: making free text possible must not make a choice
    optional, or a confirmed answer could name nothing at all."""
    with pytest.raises(AnswerNotPermitted, match="option"):
        an_answer(option_id=None)


# --- §16:543, a scope and possibly a time period -----------------------------------


def test_an_answer_may_carry_the_period_it_applies_to(qconn):
    """§16:543: "multiple roles, each with a scope and possibly a time period,
    rather than forcing one permanent profession". A person stops teaching."""
    record_question(qconn, a_question(), asked_at=CLOCK)
    record_answer(qconn, an_answer(
        applies_from="2024-09-01", applies_until="2026-06-30"))

    live = live_answer(qconn, question_id="reading.organization:columbia",
                       scope="organization:columbia")
    assert live.applies_from == "2024-09-01"
    assert live.applies_until == "2026-06-30"


def test_a_period_with_no_end_is_a_role_the_person_still_holds(qconn):
    record_question(qconn, a_question(), asked_at=CLOCK)
    record_answer(qconn, an_answer(applies_from="2024-09-01"))
    live = live_answer(qconn, question_id="reading.organization:columbia",
                       scope="organization:columbia")
    assert live.applies_from == "2024-09-01"
    assert live.applies_until is None


def test_a_period_that_ends_before_it_starts_is_refused():
    """A period nothing can be inside is not a period, and it would silently
    disable an answer the person believes they gave."""
    with pytest.raises(AnswerNotPermitted, match="period"):
        an_answer(applies_from="2026-06-30", applies_until="2024-09-01")
