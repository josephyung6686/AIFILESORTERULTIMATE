# src/questions/store.py
"""Writing and reading P15's questions and answers.

The one property everything here serves: **an answer outlives the run that asked
for it**. `66` §12 rejects "a weekly questionnaire" and requires the product to
"ask a question only when a specific decision is blocked" -- and a product that
forgot the answer would block on the same decision, and ask again, on every run.
That is what makes this a store rather than a value passed down a call stack.

Append-only, with supersession, for the reason §12 gives: an answer must be
"edited, revoked, or re-run". An edit that overwrote the row would lose that the
person once said something else, and a plan frozen under the old answer would have
no record of why it looks the way it does.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
import uuid
from collections.abc import Sequence

from evidence_shape.canonical import canonical_json

from questions.records import QuestionOption, StructuralAnswer, StructuralQuestion
from questions.vocabulary import BINDING_STATES, REVOKED


class AnswerConflict(ValueError):
    """An answer that does not belong to the question it names."""


def record_question(conn: sqlite3.Connection, question: StructuralQuestion, *,
                    asked_at: str) -> str:
    """Record that the product raised this question. Idempotent by question id.

    A second run over the same corpus raises the same question from the same
    evidence, and that is ONE question asked twice -- not two. `first_asked_at` is
    preserved on the re-ask, because when the person was first asked something is
    part of the history §12's revocation story reads, and a product that keeps
    resetting it cannot tell a question it has raised once from one it has raised
    for the fortieth time.
    """
    conn.execute(
        "INSERT INTO structural_questions "
        "(question_id, answer_class, prompt, evidence_context, unlocks, "
        " will_not_do, scope, options, evidence_refs, first_asked_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT (question_id) DO NOTHING",
        (question.question_id, question.answer_class, question.prompt,
         question.evidence_context, question.unlocks, question.will_not_do,
         question.scope,
         # `asdict`, not a hand-written field list. The list was here first and
         # dropped `gates_template` silently the day it was added: the question
         # stored fine, rehydrated fine, and simply gated nothing. Any field this
         # record gains now round-trips, and `_question_of` already reconstructs
         # with `QuestionOption(**option)`, so the two halves cannot drift apart.
         canonical_json([asdict(option) for option in question.options]),
         canonical_json(list(question.evidence_refs)), asked_at))
    return question.question_id


def _question_row(conn: sqlite3.Connection, question_id: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM structural_questions WHERE question_id = ?",
        (question_id,)).fetchone()


def _question_of(row: sqlite3.Row) -> StructuralQuestion:
    return StructuralQuestion(
        question_id=row["question_id"], answer_class=row["answer_class"],
        prompt=row["prompt"], evidence_context=row["evidence_context"],
        unlocks=row["unlocks"], will_not_do=row["will_not_do"],
        scope=row["scope"],
        options=tuple(QuestionOption(**option)
                      for option in json.loads(row["options"])),
        evidence_refs=tuple(json.loads(row["evidence_refs"])))


def record_answer(conn: sqlite3.Connection, answer: StructuralAnswer) -> str:
    """Record one answer, and return its id so a later edit can supersede it."""
    row = _question_row(conn, answer.question_id)
    if row is None:
        raise AnswerConflict(
            f"{answer.question_id!r} names no question this run asked. An answer "
            "with no question is an assertion about the user that nothing "
            "prompted, which is the profile data §12 declines to collect")
    question = _question_of(row)
    if (answer.option_id is not None
            and answer.option_id not in {option.option_id
                                         for option in question.options}):
        raise AnswerConflict(
            f"{question.question_id!r} does not offer {answer.option_id!r}; it "
            f"offers {sorted(option.option_id for option in question.options)}. "
            "A caller must not widen the option set by answering")
    answer_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO structural_answers "
        "(answer_id, question_id, option_id, state, scope, user_id, "
        " recorded_at, inferred, supersedes, supersede_reason) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (answer_id, answer.question_id, answer.option_id, answer.state,
         answer.scope, answer.user_id, answer.recorded_at,
         1 if answer.inferred else 0, answer.supersedes, answer.supersede_reason))
    return answer_id


def _answer_of(row: sqlite3.Row) -> StructuralAnswer:
    return StructuralAnswer(
        question_id=row["question_id"], option_id=row["option_id"],
        state=row["state"], scope=row["scope"], user_id=row["user_id"],
        recorded_at=row["recorded_at"], inferred=bool(row["inferred"]),
        supersedes=row["supersedes"], supersede_reason=row["supersede_reason"])


def _live_row(conn: sqlite3.Connection, *, question_id: str,
              scope: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT a.* FROM structural_answers AS a "
        "WHERE a.question_id = ? AND a.scope = ? AND NOT EXISTS ("
        "  SELECT 1 FROM structural_answers AS later "
        "  WHERE later.supersedes = a.answer_id) "
        "ORDER BY a.recorded_at DESC, a.answer_id DESC LIMIT 1",
        (question_id, scope)).fetchone()


def live_answer(conn: sqlite3.Connection, *, question_id: str,
                scope: str) -> StructuralAnswer | None:
    """The answer that governs this question in this scope, or None.

    The live one is the one nothing supersedes. Ordered by `recorded_at` as the
    tie-break so a database written by two processes in one clock tick still has a
    deterministic answer rather than an arbitrary one.
    """
    row = _live_row(conn, question_id=question_id, scope=scope)
    return None if row is None else _answer_of(row)


def live_answer_id(conn: sqlite3.Connection, *, question_id: str,
                   scope: str) -> str | None:
    """The id of the answer `live_answer` returns, so an edit can supersede it.

    `StructuralAnswer` carries no `answer_id` -- the id is minted at write time by
    `record_answer`, which returns it "so a later edit can supersede it". A caller
    holding only the record therefore has the answer and not its name, and a caller
    that wants to supersede needs the name. This is that reader, over the SAME row
    `live_answer` selects, so the two can never disagree about which answer is live.

    Without it the tie-break above is doing work it was never meant to do. It exists
    so two processes in one clock tick still resolve deterministically; it is not a
    way to choose between two answers ONE person gave, and it decides at random
    which correction the product obeys when it is asked to.
    """
    row = _live_row(conn, question_id=question_id, scope=scope)
    return None if row is None else row["answer_id"]


def open_questions(conn: sqlite3.Connection) -> tuple[StructuralQuestion, ...]:
    """Every question the product has raised and the person has not settled.

    A REVOKED answer reopens its question. That is the point of revocation: the
    person has withdrawn what they said, and a question that stayed closed would
    leave them unable ever to be asked again about a decision they deliberately
    reopened.
    """
    out: list[StructuralQuestion] = []
    for row in conn.execute(
            "SELECT * FROM structural_questions ORDER BY first_asked_at, "
            "question_id"):
        answer = live_answer(conn, question_id=row["question_id"],
                             scope=row["scope"])
        if answer is None or answer.state == REVOKED:
            out.append(_question_of(row))
    return tuple(out)


def answered_options(conn: sqlite3.Connection, *,
                     scope: str | None = None) -> tuple[QuestionOption, ...]:
    """Every option a BINDING answer selected, with what that option does.

    This is the seam the rest of the product consumes: a caller asks what the
    person has actually settled and gets back the options, not the raw rows. Only
    `confirmed` answers are binding -- a skip, a "not about me" and a revocation
    all decide nothing, which is what makes them safe to offer.
    """
    out: list[QuestionOption] = []
    for row in conn.execute("SELECT * FROM structural_questions "
                            "ORDER BY question_id"):
        if scope is not None and row["scope"] != scope:
            continue
        answer = live_answer(conn, question_id=row["question_id"],
                             scope=row["scope"])
        if answer is None or answer.state not in BINDING_STATES:
            continue
        for option in _question_of(row).options:
            if option.option_id == answer.option_id:
                out.append(option)
    return tuple(out)


def activated_schemas(conn: sqlite3.Connection, *,
                      scope: str | None = None) -> frozenset[str]:
    """The schemas the person's own confirmed answers activate.

    `66` §13: a structural answer "may ACTIVATE A SCHEMA". This is the whole of
    that consequence, in one place, so a reader can see every schema the user
    turned on and where it came from.
    """
    return frozenset(
        option.activates_schema
        for option in answered_options(conn, scope=scope)
        if option.activates_schema)


def gated_template(conn: sqlite3.Connection, *, scope: str) -> str | None:
    """The nesting the person chose for ONE branch, or `None` if they have not.

    `66` §13: a structural answer "may ... GATE A TEMPLATE". This is the whole of
    that consequence, in one place, for the same reason `activated_schemas` is.

    Scoped, and required to be -- `scope` has no default here where it does on
    `activated_schemas`, because a nesting answer is about one branch and §13
    forbids reusing an answer "outside its stated scope". A corpus-wide read would
    let the shape somebody chose for their coursework decide the shape of their
    legal matters.

    `None` for unanswered AND for skipped, which are different facts about the
    person and the same fact about the tree: neither chose a nesting, so the
    caller keeps whatever default it would have used. That is what makes asking
    free -- the run still produces the tree it produced before.
    """
    chosen = [option.gates_template
              for option in answered_options(conn, scope=scope)
              if option.gates_template]
    return chosen[0] if chosen else None


def questions_for(conn: sqlite3.Connection,
                  question_ids: Sequence[str]) -> tuple[StructuralQuestion, ...]:
    """The named questions, for a caller that already knows which it wants."""
    out: list[StructuralQuestion] = []
    for question_id in question_ids:
        row = _question_row(conn, question_id)
        if row is not None:
            out.append(_question_of(row))
    return tuple(out)
