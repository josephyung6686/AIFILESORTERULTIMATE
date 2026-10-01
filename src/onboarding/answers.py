# src/onboarding/answers.py
"""A completed answers file is the profile a scan is allowed to use.

The file is JSON the person filled in. `confirmed` must be true, and a
field that still says TODO is not an answer. The person's name stays in
the plan database. It is not part of the sentence a model is shown.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from facts.domains import SCHEMA_IDS

RECORD_DDL = """
CREATE TABLE IF NOT EXISTS onboarding_record (
    corpus_root  TEXT PRIMARY KEY,
    answers_json TEXT NOT NULL,
    completed    INTEGER NOT NULL,
    recorded_at  TEXT NOT NULL
);
"""

_TODO = "TODO"


class AnswersNotReady(ValueError):
    """The file is not a completed profile. The message names the gaps."""


def _is_todo(value) -> bool:
    return isinstance(value, str) and _TODO in value


def problems_in(data: object) -> list[str]:
    """Why this document cannot authorise a scan. Empty means it can."""
    if not isinstance(data, dict):
        return ["the answers file must be a JSON object"]
    problems: list[str] = []
    if data.get("confirmed") is not True:
        problems.append(
            "confirmed must be true. A template is not a completed profile.")
    lives = data.get("lives")
    if not isinstance(lives, list) or not lives:
        problems.append("lives must be a non-empty list of schema ids")
    else:
        for life in lives:
            if not isinstance(life, str) or life not in SCHEMA_IDS:
                problems.append(
                    f"{life!r} is not a life this product knows. "
                    f"Business is not a fallback.")
            if _is_todo(life):
                problems.append("a life still says TODO")
    refused = data.get("not_lives") or []
    if not isinstance(refused, list):
        problems.append("not_lives must be a list")
    else:
        for life in refused:
            if not isinstance(life, str) or life not in SCHEMA_IDS:
                problems.append(f"{life!r} is not a schema that can be refused")
    for key in ("person_name", "school"):
        value = data.get(key)
        if _is_todo(value) or not isinstance(value, str) or not value.strip():
            problems.append(f"{key} still needs an answer (it says TODO or is empty)")
    courses = data.get("courses")
    if not isinstance(courses, list):
        problems.append("courses must be a list")
    else:
        for course in courses:
            if not isinstance(course, dict):
                problems.append("each course must be an object")
                continue
            for field in ("code", "name", "term"):
                if _is_todo(course.get(field)):
                    problems.append(f"a course {field} still says TODO")
    companies = data.get("companies")
    if not isinstance(companies, list):
        problems.append("companies must be a list")
    else:
        for company in companies:
            if _is_todo(company):
                problems.append("a company still says TODO")
    if "wording" in data:
        wording = data.get("wording")
        if not isinstance(wording, str):
            problems.append("wording must be a string")
        elif _is_todo(wording):
            problems.append("wording still says TODO")
    return problems


def load_answers(path: Path) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as problem:
        raise AnswersNotReady(
            "the answers file could not be read as JSON") from problem
    problems = problems_in(data)
    if problems:
        raise AnswersNotReady("; ".join(problems))
    return data


def model_context(data: dict) -> str:
    """Life areas, school, courses, companies. Not the person's name."""
    parts: list[str] = []
    lives = [life for life in data.get("lives") or [] if isinstance(life, str)]
    if lives:
        parts.append("Declared life areas: " + ", ".join(lives) + ".")
    situations = data.get("situations") or {}
    if isinstance(situations, dict) and situations:
        shown = ", ".join(f"{key}={value}" for key, value in sorted(situations.items()))
        parts.append("Situations: " + shown + ".")
    school = data.get("school")
    if isinstance(school, str) and school.strip() and not _is_todo(school):
        parts.append("School: " + school.strip() + ".")
    courses: list[str] = []
    for course in data.get("courses") or []:
        if not isinstance(course, dict):
            continue
        bits = [course.get("code"), course.get("name"), course.get("term")]
        text = " ".join(
            bit.strip() for bit in bits
            if isinstance(bit, str) and bit.strip() and not _is_todo(bit))
        if text:
            courses.append(text)
    if courses:
        parts.append("Courses: " + "; ".join(courses) + ".")
    companies = [
        company.strip() for company in data.get("companies") or []
        if isinstance(company, str) and company.strip() and not _is_todo(company)]
    if companies:
        parts.append("Companies: " + ", ".join(companies) + ".")
    parts.append("Choose a declared life area or needs_review. Do not invent one.")
    return " ".join(parts)


def ensure_record(conn: sqlite3.Connection) -> None:
    conn.executescript(RECORD_DDL)


def store_answers(conn: sqlite3.Connection, *, corpus_root: str, data: dict,
                  recorded_at: str) -> None:
    ensure_record(conn)
    conn.execute(
        "INSERT OR REPLACE INTO onboarding_record "
        "(corpus_root, answers_json, completed, recorded_at) VALUES (?, ?, 1, ?)",
        (corpus_root, json.dumps(data, sort_keys=True), recorded_at),
    )


def stored_answers(conn: sqlite3.Connection, corpus_root: str) -> dict | None:
    try:
        ensure_record(conn)
        row = conn.execute(
            "SELECT answers_json, completed FROM onboarding_record "
            "WHERE corpus_root = ?",
            (corpus_root,),
        ).fetchone()
    except sqlite3.OperationalError:
        return None
    if row is None or not row[1]:
        return None
    data = json.loads(row[0])
    return data if isinstance(data, dict) else None


def apply_answers(conn: sqlite3.Connection, data: dict, *, user_id: str,
                  recorded_at: str, corpus_root: str) -> None:
    """Write the closed lives the recogniser already reads, then the record."""
    from questions.profile import apply_profile
    lives = [f"{life}={life}" for life in data["lives"]]
    refused = [f"{life}={life}" for life in data.get("not_lives") or []]
    courses = []
    for index, course in enumerate(data.get("courses") or []):
        if not isinstance(course, dict):
            continue
        label = " ".join(
            str(course.get(field) or "").strip()
            for field in ("code", "name", "term")).strip()
        if label:
            courses.append(f"course-{index}={label}")
    projects = [
        f"project-{index}={name}"
        for index, name in enumerate(data.get("projects") or [])
        if isinstance(name, str) and name.strip()]
    leave = [
        f"leave-{index}={name}"
        for index, name in enumerate(data.get("leave_alone") or [])
        if isinstance(name, str) and name.strip()]
    wording_rows = []
    wording = data.get("wording")
    if isinstance(wording, str) and wording.strip() and not _is_todo(wording):
        wording_rows.append("note=" + wording.strip())
    apply_profile(
        conn, user_id=user_id, recorded_at=recorded_at,
        lives=lives, refused=refused, courses=courses,
        projects=projects, leave_alone=leave, wording=wording_rows)
    store_answers(conn, corpus_root=corpus_root, data=data, recorded_at=recorded_at)
