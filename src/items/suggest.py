"""Local suggestions: counted facts the model words in chat. Nothing is moved.

They lead with the person's own clutter (loose screenshots, same-content
copies, installers), then set-aside projects and open questions, then nudges.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from items.nudge import warnings
from items.profile_loader import load_profile

_SCREENSHOT = re.compile(
    r"^(screenshot|screen shot|cleanshot|截屏|屏幕快照|螢幕快照|スクリーンショット)",
    re.IGNORECASE)
_IMAGES = {".png", ".jpg", ".jpeg", ".heic", ".gif", ".webp"}
_COPY = re.compile(r"\(\d+\)|\bcopy\b|副本", re.IGNORECASE)
_INSTALLERS = {".dmg", ".pkg"}


def _live_files(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT item_id, file_id, display_label, open_target, content_hash "
        "FROM items "
        "WHERE presence = 'live' AND item_type = 'file' "
        "AND superseded_by IS NULL AND open_target IS NOT NULL").fetchall()


def _plural(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


KINDS = ("screenshots", "copies", "installers")


def files_for(conn: sqlite3.Connection, kind: str) -> list[sqlite3.Row]:
    """The files a suggestion counts: one predicate for the greeting's number
    and for a sort of the whole set. Rows carry item_id, file_id,
    display_label, open_target and content_hash."""
    files = _live_files(conn)
    if kind == "screenshots":
        from items.refresh import discover_roots
        roots = {str(r) for r in discover_roots(conn)}
        return [f for f in files
                if _SCREENSHOT.match(f["display_label"] or "")
                and Path(f["open_target"]).suffix.lower() in _IMAGES
                and str(Path(f["open_target"]).parent) in roots]
    if kind == "copies":
        by_hash: dict[str, list[sqlite3.Row]] = {}
        for f in files:
            if f["content_hash"]:
                by_hash.setdefault(f["content_hash"], []).append(f)
        return [f for group in by_hash.values() if len(group) > 1
                for f in group if _COPY.search(f["display_label"] or "")]
    if kind == "installers":
        return [f for f in files
                if Path(f["open_target"]).suffix.lower() in _INSTALLERS]
    raise ValueError(kind)


def suggestions(conn: sqlite3.Connection,
                profile_name: str = "student") -> list[dict]:
    """Read items. Write nothing. Each: {kind, text, action}."""
    out: list[dict] = []
    shots = files_for(conn, "screenshots")
    if shots:
        out.append({"kind": "screenshots", "action": "sort screenshots",
                    "text": _plural(len(shots), "loose screenshot is",
                                    "loose screenshots are")
                            + " at the top of a chosen folder."})
    copies = len(files_for(conn, "copies"))
    if copies:
        out.append({"kind": "copies", "action": "review copies",
                    "text": _plural(copies, "file is a copy",
                                    "files are copies")
                            + " of another file with the same content."})
    installers = files_for(conn, "installers")
    if installers:
        out.append({"kind": "installers", "action": "review installers",
                    "text": _plural(len(installers), "installer (.dmg or .pkg)",
                                    "installers (.dmg or .pkg)")
                            + " found."})

    from items.identity import excluded_areas
    from scan_agent.exclusion import RULE_PROJECT_ROOT_DESCENDANT
    projects = [a for a in excluded_areas(conn)
                if a["rule"] == RULE_PROJECT_ROOT_DESCENDANT]
    if projects:
        out.append({"kind": "set_aside_projects",
                    "action": "show set-aside projects",
                    "text": _plural(len(projects), "coding project is",
                                    "coding projects are")
                            + " set aside; each is kept as one item."})

    questions = _open_questions(conn)
    if questions:
        out.append({"kind": "open_questions", "action": "answer questions",
                    "text": _plural(questions, "question is", "questions are")
                            + " waiting for an answer."})

    try:
        profile = load_profile(profile_name)
    except Exception:
        profile = None
    for row in warnings(conn, profile=profile):
        out.append({"kind": row["kind"], "text": row["message"],
                    "action": "link a file"})
    return out


def _open_questions(conn: sqlite3.Connection) -> int:
    """The questions a person can answer: the chat's own count."""
    have = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    if "structural_questions" not in have:
        return 0
    from assistant.engine_tools import open_questions
    return len(open_questions(conn))
