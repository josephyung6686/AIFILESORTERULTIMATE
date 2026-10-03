"""Approve, reject, and undo a relationship without touching recognition.

Decisions are exact on `basis_key`. A reject suppresses re-proposal of that
basis until an undo. It does not change a file's schema and does not suppress
a different pair that shares only `rel_type`.

Captures L0 DiffEvents for correction memory (atoms stay dark until release).
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

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


def accept_link(
        conn: sqlite3.Connection,
        relationship_id: str,
        *,
        user_id: str,
        session_id: str | None = None,
        session_read_untrusted: bool = False,
) -> dict[str, Any]:
    return _decide(
        conn, relationship_id,
        polarity=POLARITY_ACCEPT, user_id=user_id,
        new_state=STATE_APPROVED,
        session_id=session_id,
        session_read_untrusted=session_read_untrusted,
    )


def reject_link(
        conn: sqlite3.Connection,
        relationship_id: str,
        *,
        user_id: str,
        session_id: str | None = None,
        session_read_untrusted: bool = False,
) -> dict[str, Any]:
    return _decide(
        conn, relationship_id,
        polarity=POLARITY_REJECT, user_id=user_id,
        new_state=STATE_REJECTED,
        session_id=session_id,
        session_read_untrusted=session_read_untrusted,
    )


def undo_link(
        conn: sqlite3.Connection,
        relationship_id: str,
        *,
        user_id: str,
        session_id: str | None = None,
) -> dict[str, Any]:
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
    return {
        "relationship_id": relationship_id,
        "state": STATE_PROPOSED,
        "polarity": POLARITY_UNDO,
        "user_id": user_id,
        "session_id": session_id or user_id,
        "item_content_versions": {},
    }


def basis_is_rejected(conn: sqlite3.Connection, basis_key: str) -> bool:
    """True when the newest polarity for this basis is reject."""
    return _latest_polarity(conn, basis_key) == POLARITY_REJECT


def _decide(
        conn: sqlite3.Connection,
        relationship_id: str,
        *,
        polarity: str,
        user_id: str,
        new_state: str,
        session_id: str | None = None,
        session_read_untrusted: bool = False,
) -> dict[str, Any]:
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
    versions = _item_versions(
        conn, [row["from_item_id"], row["to_item_id"]])
    result = {
        "relationship_id": relationship_id,
        "state": new_state,
        "polarity": polarity,
        "user_id": user_id,
        "session_id": session_id or user_id,
        "item_content_versions": versions,
    }
    _capture_decision(
        conn, result, session_read_untrusted=session_read_untrusted)
    return result


def _capture_decision(
        conn: sqlite3.Connection,
        result: dict[str, Any],
        *,
        session_read_untrusted: bool = False,
) -> None:
    try:
        from assistant.memory_l0 import capture_relationship_decision
        versions = result.get("item_content_versions") or {}
        item_ids = list(versions.keys())
        if not item_ids:
            row = conn.execute(
                "SELECT from_item_id, to_item_id FROM relationships "
                "WHERE relationship_id = ?",
                (result["relationship_id"],),
            ).fetchone()
            if row is not None:
                item_ids = [row["from_item_id"], row["to_item_id"]]
        capture_relationship_decision(
            conn,
            relationship_id=result["relationship_id"],
            polarity=result.get("polarity") or "decision",
            item_ids=item_ids,
            item_versions=versions,
            user_id=result.get("user_id") or "local-user",
            session_read_untrusted=session_read_untrusted,
        )
    except Exception:
        pass


def _item_versions(
        conn: sqlite3.Connection, item_ids: list[str],
) -> dict[str, str]:
    out: dict[str, str] = {}
    for item_id in item_ids:
        try:
            row = conn.execute(
                "SELECT content_hash, file_id FROM items WHERE item_id = ?",
                (item_id,),
            ).fetchone()
        except sqlite3.OperationalError:
            continue
        if row is None:
            continue
        digest = row["content_hash"]
        if not digest and row["file_id"]:
            try:
                frow = conn.execute(
                    "SELECT content_hash FROM files WHERE file_id = ?",
                    (row["file_id"],),
                ).fetchone()
            except sqlite3.OperationalError:
                frow = None
            digest = None if frow is None else frow["content_hash"]
        if digest:
            out[str(item_id)] = str(digest)
    return out


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
    cols = {
        r[1] for r in conn.execute("PRAGMA table_info(relationship_decisions)")
    }
    decision_id = str(uuid.uuid4())
    if "item_content_versions" in cols and "session_id" in cols:
        conn.execute(
            "INSERT INTO relationship_decisions ("
            "decision_id, basis_key, polarity, relationship_id, user_id, "
            "created_at, evidence_ids, item_content_versions, session_id, "
            "approval_hash) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                decision_id, basis_key, polarity, relationship_id, user_id,
                now, "[]", "{}", user_id, "",
            ),
        )
    else:
        conn.execute(
            "INSERT INTO relationship_decisions ("
            "decision_id, basis_key, polarity, relationship_id, user_id, "
            "created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (decision_id, basis_key, polarity, relationship_id, user_id, now),
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
