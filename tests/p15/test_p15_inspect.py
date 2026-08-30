# tests/p15/test_p15_inspect.py
"""§13:453 -- five things a person must be able to see about an answer they gave.

> A user should be able to inspect a structural answer and see: what it controls,
> where it applies, when it was supplied, whether it was inferred or explicitly
> confirmed, and how to change it.

The record has held all five since P15 shipped. Nothing printed them, so in
practice a person could give an answer, watch the tree change, and have no way to
ask what their answer had done. §13 calls that visibility a requirement, and `61`
A.5 says why in the strongest terms available: "An answer that quietly rewrote a
tree the user could not trace is the defect this whole design exists to avoid."

**The failure mode this file is really about is the opposite one.** An explanation
that claims MORE than the answer did is worse than none, because it is the one a
person acts on. So `controls` is derived from the registry -- from the consequence
fields the chosen option actually carries -- and never from the question's prose.
"""
from __future__ import annotations

import sqlite3

import pytest

from questions.explanation import explain_answer, render_explanation
from questions.records import QuestionOption, StructuralAnswer, StructuralQuestion
from questions.schema import create_questions_schema
from questions.store import record_answer, record_question
from questions.triggers import NestingChoice, question_for_nesting
from questions.vocabulary import CONFIRMED, REVOKED, SKIPPED, STRUCTURAL

CLOCK = "2026-08-31T09:30:00+00:00"
REF = "sha256:" + "ef" * 32


@pytest.fixture()
def qconn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    yield connection
    connection.close()


def a_question(**overrides) -> StructuralQuestion:
    fields = dict(
        question_id="reading.organization:columbia", answer_class=STRUCTURAL,
        prompt="What kind of material is Columbia?",
        evidence_context="Four files mention Columbia.",
        unlocks="This decides which folder layout is offered for these files.",
        will_not_do="It will not move, rename or delete anything.",
        scope="organization:columbia",
        handling_class="personal_non_sensitive",
        options=(QuestionOption("study", "I study there",
                                activates_schema="academic"),
                 QuestionOption("not_mine", "It is not about me")),
        evidence_refs=(REF,))
    fields.update(overrides)
    return StructuralQuestion(**fields)


def _answered(conn, question, option_id, state=CONFIRMED):
    record_question(conn, question, asked_at=CLOCK)
    record_answer(conn, StructuralAnswer(
        question_id=question.question_id, option_id=option_id, state=state,
        scope=question.scope, user_id="jy", recorded_at=CLOCK))


def test_the_inspection_shows_all_five_things_13_requires(qconn):
    question = a_question()
    _answered(qconn, question, "study")

    seen = explain_answer(qconn, question_id=question.question_id,
                          scope=question.scope)
    assert seen is not None
    # 1. what it controls
    assert seen.controls == ("It turns on the `academic` schema.",)
    # 2. where it applies
    assert seen.applies_to == "organization:columbia"
    # 3. when it was supplied
    assert seen.supplied_at == CLOCK
    # 4. whether it was inferred or explicitly confirmed
    assert seen.how_it_was_settled == "you confirmed it"
    # 5. how to change it
    assert "--answer reading.organization:columbia=" in seen.how_to_change
    assert "revoke" in seen.how_to_change


def test_the_inspection_claims_no_consequence_the_chosen_option_does_not_carry(qconn):
    """The negative twin, and the one that matters.

    "It is not about me" is a first-class answer that changes nothing. An
    explanation that described it in the words of the question it answered --
    "this decides which folder layout is offered" -- would be telling the person
    their answer did something it did not do. `controls` is read from the OPTION,
    through the registry, so there is nowhere for the question's prose to leak in.
    """
    question = a_question()
    _answered(qconn, question, "not_mine")

    seen = explain_answer(qconn, question_id=question.question_id,
                          scope=question.scope)
    assert seen.controls == ()
    rendered = render_explanation(seen)
    assert "academic" not in rendered
    assert "folder layout" not in rendered


def test_every_consequence_the_option_carries_is_named(qconn):
    """The other direction: an explanation that silently omitted a consequence
    would be the same defect wearing the opposite sign. Derived from the registry,
    so a consequence added without a line here is a test failure, not a silence."""
    question = question_for_nesting(
        branch_label="Coursework",
        choices=(NestingChoice(("subject",), "by subject", (), ()),
                 NestingChoice(("work_type",), "by work type", (), ())),
        file_count=4)
    _answered(qconn, question, "subject")

    seen = explain_answer(qconn, question_id=question.question_id,
                          scope=question.scope)
    assert len(seen.controls) == 1
    assert "subject" in seen.controls[0]


def test_a_skipped_answer_says_it_was_skipped_and_controls_nothing(qconn):
    """§14 keeps "skip for now" first-class, and first-class means it has its own
    explanation rather than being rendered as an absence."""
    question = a_question()
    _answered(qconn, question, None, state=SKIPPED)

    seen = explain_answer(qconn, question_id=question.question_id,
                          scope=question.scope)
    assert seen.controls == ()
    assert seen.how_it_was_settled == "you skipped it"
    assert "--answer" in seen.how_to_change


def test_a_revoked_answer_says_so_and_controls_nothing(qconn):
    question = a_question()
    _answered(qconn, question, None, state=REVOKED)

    seen = explain_answer(qconn, question_id=question.question_id,
                          scope=question.scope)
    assert seen.controls == ()
    assert seen.how_it_was_settled == "you withdrew it"


def test_a_question_nobody_has_answered_explains_that_rather_than_nothing(qconn):
    """A person who asks about a question they have not answered gets the question
    and an empty answer, not `None` -- "we asked and you have not said" is a state,
    and printing nothing would read as "no such question"."""
    question = a_question()
    record_question(qconn, question, asked_at=CLOCK)

    seen = explain_answer(qconn, question_id=question.question_id,
                          scope=question.scope)
    assert seen is not None
    assert seen.controls == ()
    assert seen.how_it_was_settled == "you have not answered it yet"
    assert seen.supplied_at is None


def test_a_question_this_database_never_asked_is_refused_not_invented(qconn):
    """The same treatment `apply_answers` gives an unknown question id: a person
    who mistypes must be told, not handed an explanation of nothing."""
    assert explain_answer(qconn, question_id="reading.organization:nowhere",
                          scope="organization:nowhere") is None


def test_the_rendering_carries_the_five_headings_and_the_persons_own_question(qconn):
    question = a_question()
    _answered(qconn, question, "study")
    rendered = render_explanation(
        explain_answer(qconn, question_id=question.question_id,
                       scope=question.scope))

    assert question.prompt in rendered
    assert "I study there" in rendered
    for heading in ("controls", "applies", "supplied", "change"):
        assert heading in rendered.lower()


def test_a_consequence_with_no_sentence_refuses_rather_than_being_left_out():
    """The ratchet. It fails the day a consequence is added without the words that
    describe it -- because an explanation that quietly dropped one would be read as
    a complete list, and a person would act on the short version."""
    import dataclasses

    from questions.explanation import (
        CONSEQUENCE_WORDS, ExplanationRefused, consequences_of,
    )
    from questions.registry import QUESTION_KINDS

    described = set(CONSEQUENCE_WORDS)
    carried = {kind.consequence_field for kind in QUESTION_KINDS}
    assert carried <= described, f"undescribed consequences: {sorted(carried - described)}"

    @dataclasses.dataclass(frozen=True)
    class SabotagedOption:
        option_id: str = "x"
        label: str = "X"
        activates_schema: str | None = None
        gates_template: str | None = None
        selects_situation: str | None = None

    monkey = dict(CONSEQUENCE_WORDS)
    CONSEQUENCE_WORDS.pop("activates_schema")
    try:
        with pytest.raises(ExplanationRefused, match="activates_schema"):
            consequences_of(SabotagedOption(activates_schema="academic"))
    finally:
        CONSEQUENCE_WORDS.clear()
        CONSEQUENCE_WORDS.update(monkey)
