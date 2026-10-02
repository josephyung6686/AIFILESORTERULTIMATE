"""Mint course and project items from declared profile answers.

Empty named lists mint nothing. Recognition is unchanged by this module.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

from items.schema import create_items_schema
from questions.store import named_courses, named_projects

PRESENCE_LIVE = "live"
TYPING_UNPLACED = "unplaced"


def mint_declared_items(
        conn: sqlite3.Connection, *, profile_id: str | None = None) -> int:
    """Create missing course/project items for confirmed names. Returns inserts."""
    if not _items_installed(conn):
        return 0
    create_items_schema(conn)
    now = datetime.now(timezone.utc).isoformat()
    written = 0
    for name in named_courses(conn):
        if _ensure(conn, item_type="course", label=name,
                   external_key=f"course:{name.casefold()}",
                   profile_id=profile_id, now=now):
            written += 1
    for name in named_projects(conn):
        if _ensure(conn, item_type="project", label=name,
                   external_key=f"project:{name.casefold()}",
                   profile_id=profile_id, now=now):
            written += 1
    return written


def _ensure(conn, *, item_type: str, label: str, external_key: str,
            profile_id: str | None, now: str) -> bool:
    existing = conn.execute(
        "SELECT item_id FROM items WHERE external_key = ? "
        "AND superseded_by IS NULL",
        (external_key,),
    ).fetchone()
    if existing is not None:
        return False
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, external_key, "
        "presence, typing_state, type_schema, profile_id, created_at, superseded_by"
        ") VALUES (?, ?, ?, NULL, NULL, ?, ?, ?, NULL, ?, ?, NULL)",
        (str(uuid.uuid4()), item_type, label, external_key,
         PRESENCE_LIVE, TYPING_UNPLACED, profile_id, now),
    )
    return True


def _items_installed(conn: sqlite3.Connection) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'items'"
    ).fetchone() is not None
