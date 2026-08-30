# src/questions/explanation.py
"""§13:453 -- what one answer controls, said in the person's own terms.

> A user should be able to inspect a structural answer and see: what it controls,
> where it applies, when it was supplied, whether it was inferred or explicitly
> confirmed, and how to change it.

Five things. `StructuralAnswer` has held all five since P15 shipped and nothing
printed any of them, so a person could answer a question, watch the tree change,
and have no way to ask what their answer had done. `61` A.5 states the stake:
"An answer that quietly rewrote a tree the user could not trace is the defect this
whole design exists to avoid."

**Where `controls` comes from, and why it matters.** From the OPTION the person
chose, through the registry, and never from the question's prose. The dangerous
failure here is not silence -- it is an explanation that claims more than the
answer did, because that is the one a person acts on. "It is not about me" is a
first-class answer that changes nothing, and describing it in the words of the
question it answered would tell somebody their answer did something it did not.

Reading through `QUESTION_KINDS` also means the OTHER failure is a test failure
rather than a silence: a consequence added without a sentence here refuses loudly
instead of being quietly left out of the explanation.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from questions.records import QuestionOption, StructuralQuestion
from questions.registry import QUESTION_KINDS
from questions.store import live_answer, questions_for
from questions.vocabulary import (
    CONFIRMED, NOT_APPLICABLE, REVOKED, SKIPPED,
)


class ExplanationRefused(ValueError):
    """A consequence this module has no way to describe."""


#: One sentence per consequence a `QuestionOption` may carry, keyed by the field.
#: Closed, and checked against the registry: absent means refuse, never guess, so a
#: consequence added without a sentence stops the explanation rather than being
#: dropped from it. A person reading a short list would have no way to know it was
#: short.
CONSEQUENCE_WORDS: dict[str, str] = {
    "activates_schema": "It turns on the `{value}` schema.",
    "gates_template": "It sets the folders inside this branch to `{value}`.",
    "selects_situation": (
        "It makes this branch `{value}`, instead of the situation the rest of the "
        "run was given."),
}

#: How each answer state came about, in `66` §12's own distinction between an
#: answer somebody gave and one nobody has been shown. `inferred` is handled
#: separately: `StructuralAnswer` refuses to hold it, and §13 still requires the
#: person to be TOLD which it was, so the words exist for a state the record makes
#: unreachable.
SETTLEMENT_WORDS: dict[str, str] = {
    CONFIRMED: "you confirmed it",
    SKIPPED: "you skipped it",
    NOT_APPLICABLE: "you said it is not about you",
    REVOKED: "you withdrew it",
}

UNANSWERED: str = "you have not answered it yet"


@dataclass(frozen=True, slots=True)
class AnswerExplanation:
    """§13:453's five things, and the question they are about."""

    question_id: str
    prompt: str
    #: The option's own label, or None where nothing was chosen.
    chosen: str | None
    #: 1. What it controls -- one sentence per consequence actually carried.
    controls: tuple[str, ...]
    #: 2. Where it applies.
    applies_to: str
    #: 3. When it was supplied. `None` where nobody has answered.
    supplied_at: str | None
    #: 4. Whether it was inferred or explicitly confirmed.
    how_it_was_settled: str
    #: 5. How to change it.
    how_to_change: str
    #: The person's own words, where the answer was theirs rather than a pick from
    #: a list. NOT one of §13:453's five: it is `80` §4 (R5), which requires that
    #: "the raw sentence stays recorded and visible rather than discarded". Recorded
    #: it already was -- `StructuralAnswer.raw_wording` since A3 -- and visible it
    #: was not, anywhere, which made "we kept your words" a claim with no surface
    #: behind it. `None` on every answer that chose an option, because the two answer
    #: types are alternatives and a record may not hold both.
    your_words: str | None = None


def consequences_of(option: QuestionOption) -> tuple[str, ...]:
    """Every consequence this option actually carries, in one sentence each.

    Walked over `QUESTION_KINDS` rather than over the option's fields, so the
    registry stays the single place that knows what a consequence is.
    """
    out: list[str] = []
    seen: set[str] = set()
    for kind in QUESTION_KINDS:
        # BY FIELD, not by kind. Two kinds may share one consequence -- a reading
        # question and a role declaration both activate a schema, deliberately, so
        # that `activated_schemas` stays the one place a schema is turned on. A
        # walk over kinds told the person twice that their answer turned on
        # `academic`, which reads as two separate things having happened.
        if kind.consequence_field in seen:
            continue
        seen.add(kind.consequence_field)
        value = getattr(option, kind.consequence_field, None)
        if not value:
            continue
        words = CONSEQUENCE_WORDS.get(kind.consequence_field)
        if words is None:
            raise ExplanationRefused(
                f"{kind.consequence_field!r} is a consequence this deployment can "
                "set and cannot describe. §13 requires a person to see what their "
                "answer controls; an explanation that silently omitted one would "
                "be read as a complete list")
        out.append(words.format(value=value))
    return tuple(out)


def _how_to_change(question: StructuralQuestion) -> str:
    """The exact words a person types, with their own options in them.

    §13 asks for "how to change it" and a person reading "you can change this"
    still cannot. `apply_answers` already accepts all three forms.
    """
    offered = " | ".join(option.option_id for option in question.options)
    return (f"--answer {question.question_id}=<{offered}> to change it, "
            f"--answer {question.question_id}=skip to put it aside, "
            f"--answer {question.question_id}=revoke to take it back.")


def explain_answer(conn: sqlite3.Connection, *, question_id: str,
                   scope: str) -> AnswerExplanation | None:
    """§13:453's five things for one question and scope, or `None` if unasked.

    `None` only for a question this database never raised -- the same treatment
    `apply_answers` gives an unknown id, and for the same reason: a person who
    mistyped must be told rather than handed an explanation of nothing.

    A question raised and NOT answered returns an explanation, not `None`. "We
    asked and you have not said" is a state §14 makes first-class, and printing
    nothing for it would read as "no such question".
    """
    asked = questions_for(conn, (question_id,))
    if not asked:
        return None
    question = asked[0]
    answer = live_answer(conn, question_id=question_id, scope=scope)
    chosen: QuestionOption | None = None
    if answer is not None and answer.option_id:
        chosen = next((option for option in question.options
                       if option.option_id == answer.option_id), None)
    binding = answer is not None and answer.state == CONFIRMED
    return AnswerExplanation(
        question_id=question.question_id,
        prompt=question.prompt,
        chosen=chosen.label if chosen else None,
        controls=consequences_of(chosen) if (chosen and binding) else (),
        applies_to=scope,
        supplied_at=answer.recorded_at if answer is not None else None,
        how_it_was_settled=(
            UNANSWERED if answer is None
            else SETTLEMENT_WORDS[answer.state]),
        how_to_change=_how_to_change(question),
        your_words=answer.raw_wording if answer is not None else None)


def explain_question(conn: sqlite3.Connection,
                     question_id: str) -> AnswerExplanation | None:
    """`explain_answer` for a caller that has only the question id.

    The scope is READ from the question rather than asked for, because that is
    where `apply_answers` already gets it: every answer P15 writes carries the
    scope of the question it answers. A command-line flag that made the person
    supply the scope as well would be asking them to repeat something the product
    already knows, and to get it exactly right or be told their question does not
    exist.
    """
    asked = questions_for(conn, (question_id,))
    if not asked:
        return None
    return explain_answer(conn, question_id=question_id, scope=asked[0].scope)


def render_explanation(explanation: AnswerExplanation) -> str:
    """The five things as lines a person reads, in §13's own order."""
    lines = [explanation.prompt]
    if explanation.chosen:
        lines.append(f"  You answered: {explanation.chosen}")
    # Before the consequences, not after, because there are none: a free-text answer
    # activates nothing, and a person reading "What it controls: nothing" without
    # first seeing their own sentence would read it as their words having been lost.
    if explanation.your_words:
        lines.append(f"  You answered, in your own words: {explanation.your_words}")
    if explanation.controls:
        lines.append("  What it controls:")
        lines.extend(f"    - {sentence}" for sentence in explanation.controls)
    else:
        lines.append("  What it controls: nothing. This answer changes no folder, "
                     "no name and no placement.")
    lines.append(f"  Where it applies: {explanation.applies_to}")
    lines.append(
        f"  When it was supplied: {explanation.supplied_at}"
        if explanation.supplied_at else "  When it was supplied: never")
    lines.append(f"  How it was settled: {explanation.how_it_was_settled}")
    lines.append(f"  How to change it: {explanation.how_to_change}")
    return "\n".join(lines)
