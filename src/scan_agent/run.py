# src/scan_agent/run.py
"""P3's scan-run handle — minted here, published, adopted by P1.

**SPEC OQ16 closed, ratified 2026-08-20.** §8.6 says "every scan", and P3 owns the
scan (§1.1), so P3 owns its name. `scan_run_id` is minted here and handed to P1's
`start_scan(conn, *, scan_run_id)`, which keys `scan_resource_usage` on it and mints
nothing of its own (P1 OQ19, settled the same day).

The identity is published; it is still not an event field. §8.2's record keeps its
eleven fields (MINOR 1) — two different claims, and only the first was ratified.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

from database_agent.scan_usage import sample_scan_resources, start_scan

RUN_DDL = """
CREATE TABLE IF NOT EXISTS scan_runs (
    scan_run_id  TEXT PRIMARY KEY,
    selection_id TEXT NOT NULL REFERENCES corpus_selections(selection_id),
    started_at   TEXT NOT NULL,
    completed_at TEXT
);
"""


def start_scan_run(conn: sqlite3.Connection, selection_id: str) -> str:
    """Open a scan run against one R1 selection and register it with P1.

    P3's own INSERT runs first, deliberately: `selection_id` is a foreign key, so a
    selection that does not exist must fail here rather than after P1 has already
    opened a counter row for a scan that never starts.
    """
    scan_run_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO scan_runs (scan_run_id, selection_id, started_at) VALUES (?, ?, ?)",
        (scan_run_id, selection_id, datetime.now(timezone.utc).isoformat()),
    )
    start_scan(conn, scan_run_id=scan_run_id)
    return scan_run_id


def finish_scan_run(conn: sqlite3.Connection, scan_run_id: str) -> None:
    """Close the run and take P1's final sample of §8.6's counters.

    `completed_at` brackets the run for P3's own reads. §8.6's `elapsed_time` is
    measured by P1 against the baseline it took at `start_scan` — not recomputed
    here, because two subtractions of two clocks is two answers to one question.
    """
    conn.execute(
        "UPDATE scan_runs SET completed_at = ? WHERE scan_run_id = ?",
        (datetime.now(timezone.utc).isoformat(), scan_run_id),
    )
    sample_scan_resources(conn, scan_run_id)


def get_scan_run(conn: sqlite3.Connection, scan_run_id: str) -> sqlite3.Row:
    return conn.execute(
        "SELECT * FROM scan_runs WHERE scan_run_id = ?", (scan_run_id,)
    ).fetchone()
