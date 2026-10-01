# src/onboarding/ask.py
"""Ask the profile in the terminal and store a record the scan accepts.

`--answers FILE` stays the non-interactive path. This command is the one a
person can run without a pre-filled JSON file. The name and the wording stay
in the plan database. Neither is printed back, and neither is put in the
sentence a model sees.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from facts.domains import SCHEMA_IDS
from onboarding.answers import problems_in
from onboarding.gate import OPTIONAL_ENV, onboarding_optional

_SKIP = "skip"
_DEFAULT_PRIVATE = ("medical", "identity", "legal", "finance")


class OnboardingStopped(Exception):
    """The person stopped, or a required answer never arrived."""

    def __init__(self, message: str, code: int) -> None:
        super().__init__(message)
        self.code = code


def default_ask(prompt: str) -> str:
    """One line from the terminal. A pipe is not a conversation."""
    if not sys.stdin.isatty():
        raise EOFError(prompt)
    return input("")


def _line(out, ask, prompt: str) -> str:
    print(prompt, file=out)
    try:
        return ask(prompt).strip()
    except EOFError as closed:
        raise OnboardingStopped(
            "Onboarding needs a terminal, or pass --answers FILE. "
            "Nothing was stored.", 2) from closed


def _required(out, ask, prompt: str) -> str:
    for _ in range(8):
        answer = _line(out, ask, prompt)
        if answer.lower() == _SKIP:
            if onboarding_optional():
                raise OnboardingStopped(
                    f"Onboarding skipped because {OPTIONAL_ENV}=1. "
                    "A scan may proceed without a profile. Nothing was stored.",
                    0)
            raise OnboardingStopped(
                "Skipping onboarding is refused. Answer the questions, or "
                f"set {OPTIONAL_ENV}=1. Nothing was stored.",
                2)
        if answer and "TODO" not in answer:
            return answer
        print("That still needs an answer. TODO is not an answer.", file=out)
    raise OnboardingStopped(
        "Onboarding stopped: a required answer was not given. Nothing was stored.",
        2)


def _optional(out, ask, prompt: str) -> str:
    answer = _line(out, ask, prompt)
    if answer.lower() == _SKIP:
        if onboarding_optional():
            raise OnboardingStopped(
                f"Onboarding skipped because {OPTIONAL_ENV}=1. "
                "A scan may proceed without a profile. Nothing was stored.",
                0)
        raise OnboardingStopped(
            "Skipping onboarding is refused. Answer the questions, or "
            f"set {OPTIONAL_ENV}=1. Nothing was stored.",
            2)
    if "TODO" in answer:
        raise OnboardingStopped(
            "TODO is not an answer. Nothing was stored.", 2)
    return answer


def _schema_list(raw: str) -> tuple[list[str], str]:
    if not raw or raw.lower() == "none":
        return [], ""
    found = []
    for part in raw.split(","):
        name = part.strip()
        if not name:
            continue
        if name not in SCHEMA_IDS:
            return [], (
                f"{name!r} is not a life this product knows. "
                "Business is not a fallback.")
        if name not in found:
            found.append(name)
    return found, ""


def _schema_answers(out, ask, prompt: str, *, required: bool) -> list[str]:
    for _ in range(8):
        raw = _required(out, ask, prompt) if required else _optional(out, ask, prompt)
        found, problem = _schema_list(raw)
        if problem:
            print(problem, file=out)
            continue
        if required and not found:
            print("lives must be a non-empty list of schema ids.", file=out)
            continue
        return found
    raise OnboardingStopped(
        "Onboarding stopped: a life was not a schema this product knows. "
        "Nothing was stored.", 2)


def collect_answers(out, ask) -> dict:
    """The completed document. Raises OnboardingStopped instead of storing."""
    print("Onboarding for this folder. Nothing here is sent off the device.",
          file=out)
    print("Lives this product knows: " + ", ".join(SCHEMA_IDS), file=out)
    person = _required(out, ask, "Your name (stays on this computer):")
    lives = _schema_answers(
        out, ask, "Lives, comma-separated schema ids:", required=True)
    refused = _schema_answers(
        out, ask, "Lives to refuse, comma-separated, or none:", required=False)
    overlap = [name for name in refused if name in lives]
    if overlap:
        raise OnboardingStopped(
            f"{overlap[0]!r} is both a life and a refusal. Nothing was stored.",
            2)
    situations = {}
    for life in lives:
        situation = _optional(out, ask, f"Situation for {life} (blank to skip):")
        if situation:
            situations[life] = situation
    school = _required(out, ask, "School:")
    courses = []
    while True:
        code = _optional(out, ask, "Course code (blank when the list is done):")
        if not code:
            break
        name = _required(out, ask, "Course name:")
        term = _required(out, ask, "Term:")
        courses.append({"code": code, "name": name, "term": term})
    companies = _schemas_free(_optional(
        out, ask, "Companies, comma-separated, or none:"))
    leave_alone = []
    while True:
        left = _optional(out, ask, "Leave-alone name (blank when the list is done):")
        if not left:
            break
        leave_alone.append(left)
    wording = _optional(
        out, ask, "Wording to remember on this computer (blank to skip):")
    private_raw = _optional(
        out, ask,
        "Private areas, comma-separated "
        "(blank keeps medical, identity, legal, finance):")
    if not private_raw:
        private = list(_DEFAULT_PRIVATE)
    elif private_raw.lower() == "none":
        private = []
    else:
        private = [part.strip() for part in private_raw.split(",") if part.strip()]
    confirm = _required(out, ask, "Type yes to store this profile:")
    if confirm.lower() != "yes":
        raise OnboardingStopped(
            "The profile was not confirmed. Nothing was stored.", 2)
    data = {
        "person_name": person,
        "lives": lives,
        "not_lives": refused,
        "situations": situations,
        "school": school,
        "courses": courses,
        "companies": companies,
        "projects": [],
        "leave_alone": leave_alone,
        "private_areas": private,
        "wording": wording,
        "confirmed": True,
    }
    problems = problems_in(data)
    if problems:
        raise OnboardingStopped(
            "; ".join(problems) + " Nothing was stored.", 2)
    return data


def _schemas_free(raw: str) -> list[str]:
    if not raw or raw.lower() == "none":
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def _next_step(out, conn, *, folder: Path, database: Path) -> None:
    from providers.record import load_provider_choice
    print(f"Profile stored for {folder}.", file=out)
    choice = load_provider_choice(conn)
    if choice and choice.get("lane") not in (None, "none"):
        print(
            f"Stored provider: {choice.get('provider')} ({choice.get('lane')}).",
            file=out)
        print("Next: the scan.", file=out)
    else:
        print("Next: filesorter providers", file=out)
        print(f"  filesorter providers --database {database}", file=out)
        print("Then the scan. --understand needs a stored lane, or "
              "DEEPSEEK_API_KEY and DEEPSEEK_MODEL_FAST.", file=out)
    print(f"  database-agent {folder} --database {database}", file=out)


def main(argv: list[str] | None = None, *, out=None, ask=None) -> int:
    import argparse

    out = out if out is not None else sys.stdout
    reader = ask or default_ask
    parser = argparse.ArgumentParser(prog="filesorter onboard")
    parser.add_argument("--folder", type=Path, required=True,
                        help="the folder this profile is for")
    parser.add_argument("--database", type=Path, default=None)
    parser.add_argument("--user", default="local")
    parser.add_argument("--write", type=Path, default=None,
                        help="also write the completed answers JSON here")
    args = parser.parse_args(argv)
    folder = args.folder.expanduser().resolve()
    if not folder.is_dir():
        print(f"{folder} is not a folder. Nothing was stored.", file=out)
        return 2
    database = (args.database.expanduser().resolve() if args.database
                else Path.cwd() / "database-agent-plan.sqlite")
    try:
        data = collect_answers(out, reader)
    except OnboardingStopped as stopped:
        print(str(stopped), file=out)
        return stopped.code
    from database_agent.db import DatabaseInsideCorpus, open_database
    from questions.schema import create_questions_schema
    from onboarding.answers import apply_answers
    try:
        conn = open_database(database, scan_roots=[folder])
    except DatabaseInsideCorpus as refusal:
        print(str(refusal), file=out)
        return 2
    try:
        create_questions_schema(conn)
        apply_answers(
            conn, data, user_id=args.user,
            recorded_at=datetime.now(timezone.utc).isoformat(),
            corpus_root=str(folder))
        if args.write is not None:
            target = args.write.expanduser().resolve()
            target.write_text(
                json.dumps(data, indent=2, sort_keys=True) + "\n",
                encoding="utf-8")
            print(f"Answers file: {target}", file=out)
        _next_step(out, conn, folder=folder, database=database)
    finally:
        conn.close()
    return 0
