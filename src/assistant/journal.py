"""Write-ahead undo journal. Schema + record helpers; no filesystem moves."""
from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

# Named assistant_journal — must never collide with sorter move_journal.
JOURNAL_DDL = """
CREATE TABLE IF NOT EXISTS assistant_journal (
    journal_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    file_id TEXT,
    content_hash TEXT,
    src TEXT NOT NULL,
    dst TEXT NOT NULL,
    state TEXT NOT NULL,
    created_ts TEXT NOT NULL,
    updated_ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS assistant_journal_by_plan
    ON assistant_journal(plan_id, state);
"""

JOURNAL_STATES = frozenset({
    "planned", "applying", "applied", "undoing", "undone", "conflict",
})


@dataclass(frozen=True)
class JournalEntry:
    journal_id: str
    plan_id: str
    item_id: str
    src: str
    dst: str
    state: str
    file_id: str | None = None
    content_hash: str | None = None


def ensure_journal_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(JOURNAL_DDL)


def record_planned(
        conn: sqlite3.Connection,
        *,
        plan_id: str,
        item_id: str,
        src: str,
        dst: str,
        file_id: str | None = None,
        content_hash: str | None = None,
) -> JournalEntry:
    """Stage a planned op. Does not touch the filesystem."""
    ensure_journal_schema(conn)
    ts = datetime.now(timezone.utc).isoformat()
    journal_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO assistant_journal ("
        "journal_id, plan_id, item_id, file_id, content_hash, src, dst, "
        "state, created_ts, updated_ts) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (journal_id, plan_id, item_id, file_id, content_hash, src, dst,
         "planned", ts, ts),
    )
    return JournalEntry(
        journal_id=journal_id, plan_id=plan_id, item_id=item_id,
        src=src, dst=dst, state="planned",
        file_id=file_id, content_hash=content_hash,
    )


def entries_for_plan(conn: sqlite3.Connection, plan_id: str) -> list[JournalEntry]:
    ensure_journal_schema(conn)
    rows = conn.execute(
        "SELECT journal_id, plan_id, item_id, file_id, content_hash, "
        "src, dst, state FROM assistant_journal WHERE plan_id = ? "
        "ORDER BY created_ts",
        (plan_id,),
    ).fetchall()
    return [
        JournalEntry(
            journal_id=r["journal_id"], plan_id=r["plan_id"],
            item_id=r["item_id"], src=r["src"], dst=r["dst"],
            state=r["state"], file_id=r["file_id"],
            content_hash=r["content_hash"],
        )
        for r in rows
    ]
