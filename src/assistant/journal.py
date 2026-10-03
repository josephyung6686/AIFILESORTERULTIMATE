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
    updated_ts TEXT NOT NULL,
    root_scope TEXT,
    protected_snapshot TEXT
);
CREATE INDEX IF NOT EXISTS assistant_journal_by_plan
    ON assistant_journal(plan_id, state);
CREATE INDEX IF NOT EXISTS assistant_journal_by_state
    ON assistant_journal(state);
"""

JOURNAL_STATES = frozenset({
    "planned",
    "moving",
    "moved_uncommitted",
    "applied",
    "undo_planned",
    "undone",
    "conflicted",
    "failed",
})

TERMINAL_STATES = frozenset({
    "applied", "undone", "conflicted", "failed",
})

NONTERMINAL_STATES = frozenset({
    "planned", "moving", "moved_uncommitted", "undo_planned",
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
    root_scope: str | None = None
    protected_snapshot: str | None = None


def ensure_journal_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(JOURNAL_DDL)
    cols = {
        r[1] for r in conn.execute("PRAGMA table_info(assistant_journal)")
    }
    if "root_scope" not in cols:
        try:
            conn.execute(
                "ALTER TABLE assistant_journal ADD COLUMN root_scope TEXT"
            )
        except sqlite3.OperationalError:
            pass
    if "protected_snapshot" not in cols:
        try:
            conn.execute(
                "ALTER TABLE assistant_journal ADD COLUMN "
                "protected_snapshot TEXT"
            )
        except sqlite3.OperationalError:
            pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_planned(
        conn: sqlite3.Connection,
        *,
        plan_id: str,
        item_id: str,
        src: str,
        dst: str,
        file_id: str | None = None,
        content_hash: str | None = None,
        root_scope: str | None = None,
        protected_snapshot: str | None = None,
) -> JournalEntry:
    """Stage a planned op. Does not touch the filesystem."""
    ensure_journal_schema(conn)
    ts = _now()
    journal_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO assistant_journal ("
        "journal_id, plan_id, item_id, file_id, content_hash, src, dst, "
        "state, created_ts, updated_ts, root_scope, protected_snapshot) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (journal_id, plan_id, item_id, file_id, content_hash, src, dst,
         "planned", ts, ts, root_scope, protected_snapshot),
    )
    return JournalEntry(
        journal_id=journal_id, plan_id=plan_id, item_id=item_id,
        src=src, dst=dst, state="planned",
        file_id=file_id, content_hash=content_hash,
        root_scope=root_scope, protected_snapshot=protected_snapshot,
    )


def set_journal_state(
        conn: sqlite3.Connection,
        journal_id: str,
        state: str,
) -> None:
    if state not in JOURNAL_STATES:
        raise ValueError(f"unknown journal state: {state}")
    ensure_journal_schema(conn)
    conn.execute(
        "UPDATE assistant_journal SET state=?, updated_ts=? "
        "WHERE journal_id=?",
        (state, _now(), journal_id),
    )


def entries_for_plan(conn: sqlite3.Connection, plan_id: str) -> list[JournalEntry]:
    ensure_journal_schema(conn)
    rows = conn.execute(
        "SELECT journal_id, plan_id, item_id, file_id, content_hash, "
        "src, dst, state, root_scope, protected_snapshot "
        "FROM assistant_journal WHERE plan_id = ? "
        "ORDER BY created_ts",
        (plan_id,),
    ).fetchall()
    return [_row_to_entry(r) for r in rows]


def nonterminal_entries(conn: sqlite3.Connection) -> list[JournalEntry]:
    ensure_journal_schema(conn)
    placeholders = ",".join("?" for _ in NONTERMINAL_STATES)
    rows = conn.execute(
        "SELECT journal_id, plan_id, item_id, file_id, content_hash, "
        "src, dst, state, root_scope, protected_snapshot "
        "FROM assistant_journal WHERE state IN (" + placeholders + ") "
        "ORDER BY created_ts",
        tuple(sorted(NONTERMINAL_STATES)),
    ).fetchall()
    return [_row_to_entry(r) for r in rows]


def _row_to_entry(r: sqlite3.Row) -> JournalEntry:
    keys = set(r.keys())
    return JournalEntry(
        journal_id=r["journal_id"], plan_id=r["plan_id"],
        item_id=r["item_id"], src=r["src"], dst=r["dst"],
        state=r["state"], file_id=r["file_id"],
        content_hash=r["content_hash"],
        root_scope=r["root_scope"] if "root_scope" in keys else None,
        protected_snapshot=(
            r["protected_snapshot"] if "protected_snapshot" in keys else None
        ),
    )
