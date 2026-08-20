# src/scan_agent/deferrals.py
"""Paths P3 did not index and no §1.1 rule rejected.

§8.6: "The user should be able to see what is running, what has been deferred, and
why", and "the difference between completed work and deferred work" must be visible
"so that no unscanned file reads as one that was understood and found unimportant."

Every reason below names the design rule or the open question that produced it. None
of them is a judgement about the file, and none is a status from P4's closed
vocabulary — that vocabulary is P4's and P3 writes no extraction run.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

#: §8.6's budget exhaustion. This is the ONLY reason R5's deferred counter reports,
#: because R5's counter is spelled "files deferred (scan budget exhausted)".
DEFERRED_BUDGET = "scan budget exhausted"

#: SPEC Q7 is OPEN — scan-time traversal of symlinks, aliases, macOS packages and
#: application bundles, network mounts, removable storage and cloud-synced
#: directories is unstated. P3 records the case rather than inventing a rule.
DEFERRED_TRAVERSAL_UNRESOLVED = "traversal behaviour unresolved (SPEC Q7)"

#: SPEC Q14 is OPEN — what happens to a record whose path no longer exists is not
#: settled. P3 records that the path was gone and decides nothing else.
DEFERRED_PATH_ABSENT = "path absent at scan time (SPEC Q14)"

#: §8.6 — a directory below a selected root that this process could not list.
#: `11` §1's Full Disk Access check covers the selected ROOTS (access.py) and says
#: nothing about what sits below one; an unrecorded refusal down there is exactly
#: §8.6's "no unscanned file reads as one that was understood and found
#: unimportant". The record carries the directory's own path and nothing from
#: inside it — nothing was listed — and says only that it could not be read.
DEFERRED_DIRECTORY_UNREADABLE = "directory not readable at scan time"

DEFERRALS_DDL = """
CREATE TABLE IF NOT EXISTS scan_deferrals (
    deferral_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id  TEXT NOT NULL REFERENCES scan_runs(scan_run_id),
    path         TEXT NOT NULL,
    is_directory INTEGER NOT NULL,
    reason       TEXT NOT NULL,
    observed_at  TEXT NOT NULL
);
"""


def record_deferral(conn: sqlite3.Connection, scan_run_id: str, deferred) -> int:
    conn.execute(
        "INSERT INTO scan_deferrals "
        "(scan_run_id, path, is_directory, reason, observed_at) VALUES (?, ?, ?, ?, ?)",
        (scan_run_id, deferred.path, int(deferred.is_directory), deferred.reason,
         datetime.now(timezone.utc).isoformat()),
    )
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]


def scan_deferrals(conn: sqlite3.Connection, scan_run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM scan_deferrals WHERE scan_run_id = ? ORDER BY deferral_id",
        (scan_run_id,),
    ).fetchall()
