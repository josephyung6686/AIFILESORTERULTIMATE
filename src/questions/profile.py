"""The corpus profile: who this folder is for, stored as structural answers.

Stage 2. Readers live in `questions.store`. This module only records. It does
not call the recogniser, and it does not build a model request. A typed
sentence is a free-text answer (`raw_wording`), which is a user edit and stays
in this database.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence

from facts.domains import SCHEMA_IDS

from questions.records import (
    AnswerNotPermitted, QuestionOption, StructuralAnswer, StructuralQuestion,
)
from questions.store import live_answer_id, record_answer, record_question
from questions.vocabulary import (
    CHOICE, CONFIRMED, FREE_TEXT, NOT_APPLICABLE, REVOKED, SCOPE_CORPUS,
    SKIPPED, STRUCTURAL,
)

_HANDLING = "public_low"


def _split(raw: str, *, flag: str) -> tuple[str, str]:
    name, separator, value = raw.partition("=")
    if not name or not separator or not value:
        raise AnswerNotPermitted(
            f"{raw!r} is not a {flag}. The form is `{flag} <name>=<value>`.")
    return name, value


def _question(kind: str, name: str, prompt: str, option: QuestionOption
              ) -> StructuralQuestion:
    return StructuralQuestion(
        question_id=f"{kind}:{name}",
        answer_class=STRUCTURAL,
        prompt=prompt,
        evidence_context="You described this folder. Nothing in the files asked.",
        unlocks="This records what the folder is for. It does not move a file.",
        will_not_do=(
            "It will not move, rename, or delete anything, and it will not "
            "send what you typed off this device."),
        scope=SCOPE_CORPUS,
        handling_class=_HANDLING,
        options=(option,),
        evidence_refs=(f"declared:{SCOPE_CORPUS}",))


def _confirm(conn, question: StructuralQuestion, *, option_id: str | None,
             answer_type: str, raw_wording: str | None, user_id: str,
             recorded_at: str) -> None:
    record_question(conn, question, asked_at=recorded_at)
    previous = live_answer_id(conn, question_id=question.question_id,
                              scope=question.scope)
    record_answer(conn, StructuralAnswer(
        question_id=question.question_id, option_id=option_id,
        answer_type=answer_type, raw_wording=raw_wording,
        state=CONFIRMED, scope=question.scope, user_id=user_id,
        recorded_at=recorded_at, supersedes=previous,
        supersede_reason="the person corrected this profile entry"
        if previous else None))


def _schema(value: str, *, flag: str) -> str:
    if value not in SCHEMA_IDS:
        raise AnswerNotPermitted(
            f"{value!r} is not a life this product knows. `{flag}` takes one "
            f"of {len(SCHEMA_IDS)} schema ids.")
    return value


def apply_profile(conn: sqlite3.Connection, *, user_id: str, recorded_at: str,
                  lives: Sequence[str] = (), refused: Sequence[str] = (),
                  projects: Sequence[str] = (), leave_alone: Sequence[str] = (),
                  courses: Sequence[str] = (), wording: Sequence[str] = ()
                  ) -> None:
    """Record confirmed profile entries. Each string is `name=value`."""
    for raw in lives:
        name, value = _split(raw, flag="life")
        schema = _schema(value, flag="life")
        _confirm(conn, _question(
            "life", name, f"Is {schema} a life of this folder?",
            QuestionOption(schema, schema, declares_life=schema)),
            option_id=schema, answer_type=CHOICE, raw_wording=None,
            user_id=user_id, recorded_at=recorded_at)
    for raw in refused:
        name, value = _split(raw, flag="not_life")
        schema = _schema(value, flag="not_life")
        _confirm(conn, _question(
            "not_life", name, f"Is {schema} refused for this folder?",
            QuestionOption(schema, schema, refuses_life=schema)),
            option_id=schema, answer_type=CHOICE, raw_wording=None,
            user_id=user_id, recorded_at=recorded_at)
    for raw in projects:
        name, value = _split(raw, flag="project")
        _confirm(conn, _question(
            "project", name, f"Treat {value} as one project?",
            QuestionOption(name, value, names_project=value)),
            option_id=name, answer_type=CHOICE, raw_wording=None,
            user_id=user_id, recorded_at=recorded_at)
    for raw in leave_alone:
        name, value = _split(raw, flag="leave")
        _confirm(conn, _question(
            "leave", name, f"Leave {value} alone?",
            QuestionOption(name, value, leaves_alone=value)),
            option_id=name, answer_type=CHOICE, raw_wording=None,
            user_id=user_id, recorded_at=recorded_at)
    for raw in courses:
        name, value = _split(raw, flag="course")
        _confirm(conn, _question(
            "course", name, f"Record the course {value}?",
            QuestionOption(name, value, names_course=value)),
            option_id=name, answer_type=CHOICE, raw_wording=None,
            user_id=user_id, recorded_at=recorded_at)
    for raw in wording:
        name, value = _split(raw, flag="wording")
        _confirm(conn, _question(
            "wording", name, "What should be remembered about this folder?",
            QuestionOption("kept", "Keep the sentence on this device",
                           keeps_local_wording="kept-on-device")),
            option_id=None, answer_type=FREE_TEXT, raw_wording=value,
            user_id=user_id, recorded_at=recorded_at)


def withdraw_profile(conn: sqlite3.Connection, question_id: str, *,
                     state: str, user_id: str, recorded_at: str) -> None:
    """Supersede one profile answer with skip, revoke, or not-about-me."""
    if state not in (SKIPPED, REVOKED, NOT_APPLICABLE):
        raise AnswerNotPermitted(
            f"{state!r} is not a withdrawal. Use skipped, revoked, or "
            "not_applicable.")
    previous = live_answer_id(conn, question_id=question_id, scope=SCOPE_CORPUS)
    if previous is None:
        raise AnswerNotPermitted(
            f"{question_id!r} has no answer to withdraw.")
    record_answer(conn, StructuralAnswer(
        question_id=question_id, option_id=None, state=state,
        scope=SCOPE_CORPUS, user_id=user_id, recorded_at=recorded_at,
        supersedes=previous,
        supersede_reason="the person withdrew this profile entry"))
