"""Contract out §4 — supersede-never-overwrite (§8.2).

P1 publishes three column names so that no part re-spells them (M1). The fourth,
`preferred`, is NOT in the shared set: §8.2 says the resolver may mark the newer
value, and §3.2 places the resolver after extraction, so it sits on P6's
`file_facts` only. P1 creates no `preferred` column.
"""
from __future__ import annotations

import sqlite3

SUPERSEDE_COLUMNS: tuple[str, str, str] = (
    "supersedes", "superseded_by", "supersede_reason",
)


def supersede_ddl(table: str) -> str:
    """The three shared columns, for a table that adopts the set."""
    return ("supersedes TEXT, superseded_by TEXT, supersede_reason TEXT")


def mark_superseded(conn: sqlite3.Connection, table: str, *,
                    old_id: str, new_id: str, reason: str) -> None:
    """Link a supersede chain. The old row stays readable and unmutated."""
    if not reason:
        raise ValueError("supersede_reason is required (§8.2)")
    conn.execute(
        f"UPDATE {table} SET superseded_by = ?, supersede_reason = ? WHERE record_id = ?",
        (new_id, reason, old_id),
    )
    conn.execute(
        f"UPDATE {table} SET supersedes = ? WHERE record_id = ?", (old_id, new_id)
    )


def chain(conn: sqlite3.Connection, table: str, record_id: str) -> list[sqlite3.Row]:
    """The full supersede chain, oldest first. Every link remains available (§8.2)."""
    rows, current = [], record_id
    while current is not None:
        row = conn.execute(
            f"SELECT * FROM {table} WHERE record_id = ?", (current,)
        ).fetchone()
        if row is None:
            break
        rows.append(row)
        current = row["superseded_by"]
    return rows
