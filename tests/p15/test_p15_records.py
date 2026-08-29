# tests/p15/test_p15_records.py
"""P15's vocabulary and records, and the boundaries `66` §13 makes non-negotiable.

`66` §13 draws one line and calls crossing it "a defect rather than a feature":

> If age range, time availability, broad profession description, or a similar
> CONTEXTUAL answer ever determines whether a folder exists, what a file is
> called, where a file is placed, or what data is exposed, that is a defect.

So the difference between a structural and a contextual answer is not a label on a
record — it is a constraint the record itself refuses to violate. Every test below
that names a contextual answer is testing that refusal, and each has the positive
twin showing a structural answer may do the same thing.
"""
from __future__ import annotations

import pytest

from questions.records import (
    AnswerNotPermitted, QuestionOption, StructuralAnswer, StructuralQuestion,
)
from questions.vocabulary import (
    ANSWER_CLASSES, ANSWER_STATES, CONFIRMED, CONTEXTUAL, NOT_APPLICABLE,
    OutOfVocabulary, REVOKED, SCOPES, SKIPPED, STRUCTURAL,
)

CLOCK = "2026-08-29T12:00:00+00:00"


def a_question(**overrides) -> StructuralQuestion:
    """`66` §14's own worked example, which is the shape every question must take."""
    fields = dict(
        question_id="relationship.organization:columbia",
        answer_class=STRUCTURAL,
        prompt="Which describes your relationship to Columbia?",
        evidence_context="We found files connected to Columbia.",
        unlocks="This helps distinguish coursework from professional material.",
        will_not_do="It will not create or move folders by itself.",
        scope="organization:columbia",
        options=(
            QuestionOption("study", "I study there", activates_schema="academic"),
            QuestionOption("teach", "I teach or work there",
                           activates_schema="academic"),
            QuestionOption("not_mine", "It is not about me"),
        ),
        evidence_refs=("sha256:" + "ab" * 32,),
    )
    fields.update(overrides)
    return StructuralQuestion(**fields)


# --- the shape `66` §12 requires of every question ---------------------------------


def test_a_question_names_the_decision_it_unlocks_and_what_it_will_not_do():
    """§12: ask "only when a specific decision is blocked, EXPLAIN THE EXACT
    DECISION IT UNLOCKS, STATE WHAT IT WILL NOT AFFECT, allow the user to skip it,
    record the scope of the answer".

    All four are required fields rather than optional ones, because a question
    missing any of them is the "generic list of questions such as 'What do you
    do?'" that §12 exists to forbid.
    """
    question = a_question()
    assert question.unlocks and question.will_not_do
    assert question.evidence_context and question.scope

    for missing in ("unlocks", "will_not_do", "evidence_context", "scope", "prompt"):
        with pytest.raises(AnswerNotPermitted, match=missing):
            a_question(**{missing: ""})


def test_a_question_is_asked_from_evidence_the_user_can_see():
    """§14: "the user can see WHY the question arose". A question with no evidence
    behind it is a profile interview, which is the thing §12 rejects by name."""
    with pytest.raises(AnswerNotPermitted, match="evidence"):
        a_question(evidence_refs=())


def test_skip_and_not_applicable_are_first_class_answers():
    """§14: "It must preserve 'not about me' and 'skip for now' as FIRST-CLASS
    answers." First-class means they are answer STATES, not the absence of one --
    a skipped question and an unasked one are different facts about the user."""
    assert SKIPPED in ANSWER_STATES and NOT_APPLICABLE in ANSWER_STATES
    assert CONFIRMED in ANSWER_STATES and REVOKED in ANSWER_STATES


# --- §13's boundary, in both directions --------------------------------------------


def test_a_contextual_answer_may_not_activate_a_schema():
    """§13's table, verbatim: a contextual answer may influence "ordering, examples,
    wording, and non-binding recommendations" and must not "create, remove, hide, or
    rename folders; gate placement; authorize movement; change privacy state; or
    SILENTLY BECOME A STRUCTURAL RULE".

    Activating a schema is the most consequential of those: it changes which
    templates exist, so it changes which folders exist.
    """
    with pytest.raises(AnswerNotPermitted, match="contextual"):
        a_question(
            answer_class=CONTEXTUAL,
            options=(QuestionOption("study", "I study there",
                                    activates_schema="academic"),))


def test_a_structural_answer_may_activate_a_schema():
    """The twin. §13: a structural answer "may activate a schema, gate a template,
    resolve role ambiguity, allow or prohibit a category of folder label, or require
    review" -- because it "resolves a real ambiguity"."""
    question = a_question()
    assert any(option.activates_schema for option in question.options)


def test_an_answer_class_outside_the_two_is_refused():
    """Two classes and no third. A record that could carry `probably_structural`
    would let the boundary §13 draws be blurred one deployment at a time."""
    assert set(ANSWER_CLASSES) == {STRUCTURAL, CONTEXTUAL}
    with pytest.raises(OutOfVocabulary):
        a_question(answer_class="probably_structural")


def test_an_option_naming_a_schema_the_product_does_not_have_is_refused():
    """A typo in an activation must not read as a policy, which is the same rule
    `recognition.detector` applies to its handling policy."""
    with pytest.raises(AnswerNotPermitted, match="not one of"):
        a_question(options=(QuestionOption("x", "X", activates_schema="astrology"),))


# --- the answer itself -------------------------------------------------------------


def test_an_answer_records_whether_it_was_confirmed_or_inferred():
    """§13: a user "should be able to inspect a structural answer and see ... WHETHER
    IT WAS INFERRED OR EXPLICITLY CONFIRMED".

    §12 forbids the other direction outright -- a structural answer must never "be
    inferred silently from weak evidence" -- so `inferred` exists to be recorded
    and refused, not to be a second way of answering.
    """
    answer = StructuralAnswer(
        question_id="relationship.organization:columbia", option_id="study",
        state=CONFIRMED, scope="organization:columbia", user_id="jy",
        recorded_at=CLOCK, inferred=False)
    assert answer.inferred is False

    with pytest.raises(AnswerNotPermitted, match="inferred"):
        StructuralAnswer(
            question_id="relationship.organization:columbia", option_id="study",
            state=CONFIRMED, scope="organization:columbia", user_id="jy",
            recorded_at=CLOCK, inferred=True)


def test_a_skipped_answer_names_no_option():
    """Skipping is not choosing. An option beside a `skipped` state would make the
    two indistinguishable in the record, and §14 makes skip a real answer."""
    answer = StructuralAnswer(
        question_id="q", option_id=None, state=SKIPPED, scope="corpus",
        user_id="jy", recorded_at=CLOCK, inferred=False)
    assert answer.option_id is None

    with pytest.raises(AnswerNotPermitted, match="skip"):
        StructuralAnswer(
            question_id="q", option_id="study", state=SKIPPED, scope="corpus",
            user_id="jy", recorded_at=CLOCK, inferred=False)


def test_a_confirmed_answer_must_name_an_option():
    """The twin of the one above, in the other direction."""
    with pytest.raises(AnswerNotPermitted, match="option"):
        StructuralAnswer(
            question_id="q", option_id=None, state=CONFIRMED, scope="corpus",
            user_id="jy", recorded_at=CLOCK, inferred=False)


def test_a_scope_is_required_and_is_where_the_answer_applies():
    """§12: "record the SCOPE of the answer", and §13: an answer must not be
    "reused outside its stated scope". A scopeless answer is a global rule, which
    is exactly what a corpus-level fact about one organization is not."""
    assert "corpus" in SCOPES
    # `OutOfVocabulary`, not `AnswerNotPermitted`: an empty scope is a vocabulary
    # violation before it is a permission one, and both are `ValueError`.
    with pytest.raises(OutOfVocabulary, match="scope"):
        StructuralAnswer(
            question_id="q", option_id="study", state=CONFIRMED, scope="",
            user_id="jy", recorded_at=CLOCK, inferred=False)
