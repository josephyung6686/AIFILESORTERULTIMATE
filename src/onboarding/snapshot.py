"""Map a setup snapshot onto the answers file a scan already reads.

`setupSnapshot()` is the onboarding screen's proposed model. It is not an
engine API. This module writes that model with the keys `load_answers`
already accepts, and only after the snapshot is finished and folder access
was granted. It does not start a scan and it does not move a file.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from facts.domains import SCHEMA_IDS
from onboarding.answers import problems_in

# Finance, identity, medical, and legal stay held. A confirmed label with
# one of these names is still not a life a model is allowed to see.
_HELD = ("medical", "identity", "legal", "finance")

# Work-area labels the screen offers, and the life the recogniser already
# knows. Projects stay a list of names; they are not a life.
_AREA_LIFE = {
    "Courses": "academic",
    "Applications": "college_applications",
    "Recruiting": "career",
}


class ScanRefused(Exception):
    """Onboarding is unfinished, or the chosen folders were not opened."""


def _clean(value: object) -> str:
    if not isinstance(value, str):
        return ""
    text = value.strip()
    if not text or "TODO" in text:
        return ""
    return text


def _split_names(value: object) -> list[str]:
    if not isinstance(value, str):
        return []
    found: list[str] = []
    for part in re.split(r"[\n,]", value):
        text = _clean(part)
        if text and text not in found:
            found.append(text)
    return found


def _labels(snapshot: dict, key: str) -> list[str]:
    rows = snapshot.get(key) or []
    if not isinstance(rows, list):
        return []
    names: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = _clean(row.get("name"))
        if name and name not in names:
            names.append(name)
    return names


def _schema_for(name: str) -> str | None:
    mapped = _AREA_LIFE.get(name)
    if mapped is not None:
        return mapped
    if name in SCHEMA_IDS:
        return name
    return None


def folder_access_refusal(snapshot: dict) -> str | None:
    """None when the person granted access to at least one folder."""
    access = snapshot.get("folderAccess")
    if not isinstance(access, dict):
        return "Allow folder access before scanning"
    if access.get("state") == "denied":
        return "Folder access was denied"
    folders = access.get("folders")
    if not isinstance(folders, list):
        folders = []
    named = [folder for folder in folders if _clean(folder)]
    if access.get("state") == "granted" and named:
        return None
    return "Allow folder access before scanning"


def answers_from_snapshot(snapshot: dict) -> dict:
    """The existing answers-file object. It may still be unfinished."""
    if not isinstance(snapshot, dict):
        snapshot = {}
    confirmed_names = _labels(snapshot, "categories")
    refused_names = _labels(snapshot, "refusedCategories")
    lives: list[str] = []
    for name in confirmed_names:
        schema = _schema_for(name)
        if schema is None or schema in _HELD or schema in lives:
            continue
        lives.append(schema)
    not_lives: list[str] = [schema for schema in _HELD if schema not in lives]
    for name in refused_names:
        schema = _schema_for(name)
        if schema is None or schema in lives or schema in not_lives:
            continue
        not_lives.append(schema)
    context = snapshot.get("context")
    if not isinstance(context, dict):
        context = {}
    courses = (
        [{"code": "", "name": name, "term": ""} for name in _split_names(context.get("courses"))]
        if "academic" in lives else []
    )
    companies = _split_names(context.get("companies")) if "career" in lives else []
    projects = (
        _split_names(context.get("projects")) if "Projects" in confirmed_names else []
    )
    leave_raw = snapshot.get("leaveAlone") or []
    leave_alone: list[str] = []
    if isinstance(leave_raw, list):
        for item in leave_raw:
            text = _clean(item)
            if text and text not in leave_alone:
                leave_alone.append(text)
    return {
        "person_name": _clean(snapshot.get("personName")),
        "lives": lives,
        "not_lives": not_lives,
        "situations": {},
        "school": _clean(snapshot.get("school")),
        "courses": courses,
        "companies": companies,
        "projects": projects,
        "leave_alone": leave_alone,
        "private_areas": list(_HELD),
        "confirmed": snapshot.get("finished") is True,
    }


def _atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def prepare_engine_scan(snapshot: dict, path: Path) -> dict:
    """Write finished answers atomically. Refuse before any scan.

    A string from `folder_access_refusal`, or answers that are not finished,
    raises `ScanRefused` and leaves `path` untouched. This does not read a
    folder and does not call the scan.
    """
    if not isinstance(snapshot, dict) or snapshot.get("finished") is not True:
        raise ScanRefused("Finish onboarding before scanning")
    missing = folder_access_refusal(snapshot)
    if missing:
        raise ScanRefused(missing)
    data = answers_from_snapshot(snapshot)
    problems = problems_in(data)
    if problems:
        raise ScanRefused("; ".join(problems))
    _atomic_write(Path(path), data)
    return data
