# src/scan_agent/dataless.py
"""11-ops-runtime.md §5 — detect a dataless iCloud item BEFORE hashing.

"macOS 'Optimize Mac Storage' presents Finder entries that are not on disk. Hashing
or opening them downloads the file. P3 detects a dataless / not-downloaded ubiquitous
item before hashing. Detection is a filesystem observation, not a handling class. Do
not materialize, hash, or extract."

This module reads `stat` and nothing else: `os.stat` does not download, `open` does.
P3 records the detection and writes NO extraction run — that record is P4's and P5 is
its writer, and which of P4's eight closed status values such a file eventually
carries is P4 Open question 6, which nothing here resolves. P3 names none of them.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

#: macOS `sys/stat.h`. Marks a ubiquitous item whose bytes are not on this machine.
#: Python's `stat` module does not publish the constant, so it is named here with
#: its source. It is outside macOS's SF_SETTABLE mask, so it cannot be set by a test.
SF_DATALESS = 0x40000000


def is_dataless(stat_result) -> bool:
    """True when the stat result says the bytes are not on this machine.

    `st_flags` exists on BSD-family systems including macOS (v1 is macOS-only per
    11-ops-runtime.md). A platform without it reads as not dataless, which is the
    honest answer: P3 has observed nothing that says otherwise.
    """
    return bool(getattr(stat_result, "st_flags", 0) & SF_DATALESS)


DATALESS_DDL = """
CREATE TABLE IF NOT EXISTS dataless_detections (
    detection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id  TEXT NOT NULL REFERENCES scan_runs(scan_run_id),
    path         TEXT NOT NULL,
    observed_at  TEXT NOT NULL
);
"""


def record_dataless_detection(conn: sqlite3.Connection, scan_run_id: str, path) -> int:
    """Record that a path was observed dataless and skipped before hashing.

    This is the record §8.6's progress line reads so that these files can be NAMED
    rather than folded into OCR-capped or unreadable (11 §5). It is not an extraction
    run and carries no status from P4's closed vocabulary.
    """
    conn.execute(
        "INSERT INTO dataless_detections (scan_run_id, path, observed_at) "
        "VALUES (?, ?, ?)",
        (scan_run_id, str(Path(path)), datetime.now(timezone.utc).isoformat()),
    )
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]


def dataless_detections(conn: sqlite3.Connection, scan_run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM dataless_detections WHERE scan_run_id = ? ORDER BY detection_id",
        (scan_run_id,),
    ).fetchall()
