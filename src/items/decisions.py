"""Approve, reject, and undo a relationship without touching recognition.

Decisions are exact on `basis_key`. A reject suppresses re-proposal of that
basis until an undo. It does not change a file's schema and does not suppress
a different pair that shares only `rel_type`.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

from items.schema import create_items_schema

POLARITY_ACCEPT = "accept"
POLARITY_REJECT = "reject"
POLARITY_UNDO = "undo"

STATE_APPROVED = "approved"
STATE_REJECTED = "rejected"
STATE_PROPOSED = "proposed"
STATE_WITHDRAWN = "withdrawn"


class UnknownRelationship(LookupError):
    """No live relationship row for that id."""


def accept_link(conn: sqlite3.Connection, relationship_id: str, *,
                user_id: str) -> None:
    _decide(conn, relationship_id, polarity=POLARITY_ACCEPT, user_id=user_id,
            new_state=STATE_APPROVED)


def reject_link(conn: sqlite3.Connection, relationship_id: str, *,
                user_id: str) -> None:
    _decide(conn, relationship_id, polarity=POLARITY_REJECT, user_id=user_id,
            new_state=STATE_REJECTED)


def undo_link(conn: sqlite3.Connection, relationship_id: str, *,
              user_id: str) -> None:
    """Reverse the latest accept/reject. History stays in `relationship_decisions`."""
    create_items_schema(conn)
    row = _live(conn, relationship_id)
    latest = _latest_polarity(conn, row["basis_key"])
    if latest is None:
        raise UnknownRelationship(
            f"nothing to undo for relationship {relationship_id!r}")
    # After undo of accept or reject, the projection returns to proposed so a
    # person can decide again. The prior events remain.
    _record(conn, basis_key=row["basis_key"], polarity=POLARITY_UNDO,
            relationship_id=relationship_id, user_id=user_id)
    conn.execute(
        "UPDATE relationships SET state = ? WHERE relationship_id = ?",
        (STATE_PROPOSED, relationship_id),
    )


def basis_is_rejected(conn: sqlite3.Connection, basis_key: str) -> bool:
    """True when the newest polarity for this basis is reject."""
    return _latest_polarity(conn, basis_key) == POLARITY_REJECT


def _decide(conn: sqlite3.Connection, relationship_id: str, *,
            polarity: str, user_id: str, new_state: str) -> None:
    create_items_schema(conn)
    if not user_id:
        raise ValueError("user_id is required for a link decision")
    row = _live(conn, relationship_id)
    _record(conn, basis_key=row["basis_key"], polarity=polarity,
            relationship_id=relationship_id, user_id=user_id)
    conn.execute(
        "UPDATE relationships SET state = ? WHERE relationship_id = ?",
        (new_state, relationship_id),
    )


def _live(conn: sqlite3.Connection, relationship_id: str) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM relationships WHERE relationship_id = ? "
        "AND superseded_by IS NULL",
        (relationship_id,),
    ).fetchone()
    if row is None:
        raise UnknownRelationship(relationship_id)
    return row


def _record(conn: sqlite3.Connection, *, basis_key: str, polarity: str,
            relationship_id: str, user_id: str) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    conn.execute(
        "INSERT INTO relationship_decisions ("
        "decision_id, basis_key, polarity, relationship_id, user_id, created_at"
        ") VALUES (?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), basis_key, polarity, relationship_id, user_id, now),
    )


def _latest_polarity(conn: sqlite3.Connection, basis_key: str) -> str | None:
    if not _decisions_installed(conn):
        return None
    row = conn.execute(
        "SELECT polarity FROM relationship_decisions WHERE basis_key = ? "
        "ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (basis_key,),
    ).fetchone()
    return None if row is None else row["polarity"]


def _decisions_installed(conn: sqlite3.Connection) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' "
        "AND name = 'relationship_decisions'"
    ).fetchone() is not None
