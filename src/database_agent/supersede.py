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
    """Link a supersede chain. The old row stays readable; the first reason sticks."""
    if not reason:
        raise ValueError("supersede_reason is required (§8.2)")
    if old_id == new_id:
        raise ValueError("a record cannot supersede itself")
    old = conn.execute(
        f"SELECT superseded_by FROM {table} WHERE record_id = ?", (old_id,)
    ).fetchone()
    if old is None:
        raise KeyError(f"unknown record {old_id!r} in {table}")
    if old["superseded_by"] is not None:
        raise ValueError(
            f"{old_id} is already superseded by {old['superseded_by']}; "
            "the first supersede_reason is never overwritten (§8.2)"
        )
    seen = {old_id}
    cursor = new_id
    while cursor is not None:
        if cursor in seen:
            raise ValueError("supersede chain would cycle")
        seen.add(cursor)
        nxt = conn.execute(
            f"SELECT superseded_by FROM {table} WHERE record_id = ?", (cursor,)
        ).fetchone()
        cursor = None if nxt is None else nxt["superseded_by"]
    conn.execute(
        f"UPDATE {table} SET superseded_by = ?, supersede_reason = ? WHERE record_id = ?",
        (new_id, reason, old_id),
    )
    conn.execute(
        f"UPDATE {table} SET supersedes = ? WHERE record_id = ?", (old_id, new_id)
    )


def chain(conn: sqlite3.Connection, table: str, record_id: str) -> list[sqlite3.Row]:
    """The full supersede chain, oldest first. Every link remains available (§8.2)."""
    rows, current, seen = [], record_id, set()
    while current is not None:
        if current in seen:
            break
        seen.add(current)
        row = conn.execute(
            f"SELECT * FROM {table} WHERE record_id = ?", (current,)
        ).fetchone()
        if row is None:
            break
        rows.append(row)
        current = row["superseded_by"]
    return rows
