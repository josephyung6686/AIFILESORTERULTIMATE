"""Project recognition and classification onto file items.

Plan §9: typed / unplaced / held. Held wins over typed. Abstention never
writes a near-miss into `type_schema`. When declared lives are non-empty,
only those schemas may become ``typed`` (photos capture must not bypass).
This package does not move files.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from typing import Any

from items.schema import create_items_schema
from recognition.detector import Recognition

TYPING_TYPED = "typed"
TYPING_UNPLACED = "unplaced"
TYPING_HELD = "held"

ExplainFn = Callable[[sqlite3.Connection, str, str], Any]
ClassifyFn = Callable[[sqlite3.Connection, str, str], Any]


def project_typing(
        conn: sqlite3.Connection, *,
        explain: ExplainFn,
        classify: ClassifyFn | None = None) -> int:
    """Update live file items from recognition/classification. Returns updates."""
    if not _items_installed(conn):
        return 0
    create_items_schema(conn)
    try:
        from questions.store import declared_lives
        lives = declared_lives(conn)
    except Exception:
        lives = frozenset()
    rows = conn.execute(
        "SELECT i.item_id, i.file_id, f.content_hash FROM items i "
        "JOIN files f ON f.file_id = i.file_id "
        "WHERE i.item_type = 'file' AND i.presence = 'live' "
        "AND i.superseded_by IS NULL AND i.file_id IS NOT NULL"
    ).fetchall()
    updated = 0
    for row in rows:
        file_id = row["file_id"]
        content_hash = row["content_hash"]
        outcome = explain(conn, file_id, content_hash)
        record = classify(conn, file_id, content_hash) if classify else None
        state, schema = _map(outcome, record, lives=lives)
        conn.execute(
            "UPDATE items SET typing_state = ?, type_schema = ? "
            "WHERE item_id = ?",
            (state, schema, row["item_id"]),
        )
        updated += 1
    return updated


def _map(outcome: Any, record: Any, *,
         lives: frozenset[str]) -> tuple[str, str | None]:
    schema: str | None = None
    if isinstance(outcome, Recognition):
        schema = outcome.schema_id
        state = TYPING_TYPED
        # Capture-path photos (and any other undeclared Recognition) must not
        # become a life type when the person named an allow-list.
        if lives and schema not in lives:
            state = TYPING_UNPLACED
            schema = None
    else:
        state = TYPING_UNPLACED
        schema = None
    protected = bool(getattr(record, "protected", False))
    basis = getattr(record, "basis", None)
    if protected or basis == "safety_domain":
        # Held wins. Keep the recognised schema beside it when present.
        held_schema = schema
        if held_schema is None and isinstance(outcome, Recognition):
            held_schema = outcome.schema_id
        return TYPING_HELD, held_schema
    return state, schema


def _items_installed(conn: sqlite3.Connection) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'items'"
    ).fetchone() is not None
