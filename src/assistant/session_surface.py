"""Session-surfaced item_ids for grounded plan ops (T-P3-01)."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

SURFACE_DDL = """
CREATE TABLE IF NOT EXISTS assistant_session_surface (
    session_key TEXT NOT NULL,
    item_id TEXT NOT NULL,
    source TEXT NOT NULL,
    ts TEXT NOT NULL,
    PRIMARY KEY (session_key, item_id)
);
"""


def ensure_surface_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SURFACE_DDL)


def note_surfaced(
        conn: sqlite3.Connection,
        item_ids: list[str] | tuple[str, ...],
        *,
        session_key: str = "default",
        source: str = "find",
) -> None:
    ensure_surface_schema(conn)
    ts = datetime.now(timezone.utc).isoformat()
    for item_id in item_ids:
        if not item_id:
            continue
        conn.execute(
            "INSERT INTO assistant_session_surface ("
            "session_key, item_id, source, ts) VALUES (?,?,?,?) "
            "ON CONFLICT(session_key, item_id) DO UPDATE SET "
            "source=excluded.source, ts=excluded.ts",
            (session_key, item_id, source, ts),
        )


def surfaced_ids(
        conn: sqlite3.Connection, *, session_key: str = "default",
) -> set[str]:
    ensure_surface_schema(conn)
    rows = conn.execute(
        "SELECT item_id FROM assistant_session_surface WHERE session_key=?",
        (session_key,),
    ).fetchall()
    return {r["item_id"] for r in rows}


def assert_ops_grounded(
        conn: sqlite3.Connection,
        item_ids: list[str],
        *,
        session_key: str = "default",
        extra_allowed: set[str] | None = None,
) -> list[str]:
    """Return ungrounded item_ids (empty = all ok)."""
    allowed = surfaced_ids(conn, session_key=session_key)
    if extra_allowed:
        allowed |= extra_allowed
    return [i for i in item_ids if i not in allowed]
