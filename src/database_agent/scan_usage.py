"""Contract out §10 — the §8.6 per-scan resource observability record (D1).

§8.6's first sentence names six resources: elapsed time, memory, CPU or accelerator
usage, storage, network use, and LLM cost. P1 records all six because it is the part
every other part already writes through. P13 renders them.

Recording is not bounding. §8.6 names a configurable ceiling for NONE of these six.
This module holds no threshold, rejects no operation, and derives no quality signal.
Absence reads as unknown: a counter that could not be sampled is NULL, never 0.
"""
from __future__ import annotations

import json
import resource
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

#: §8.6's six, in the order the design names them.
RESOURCE_COUNTERS: tuple[str, ...] = (
    "elapsed_time", "memory", "cpu_accelerator", "storage", "network", "llm_cost",
)


def _cpu_seconds() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


def _database_bytes(conn: sqlite3.Connection) -> int | None:
    """The database and its WAL/SHM sidecars. This is the storage P1 can count."""
    row = conn.execute("PRAGMA database_list").fetchone()
    path = Path(row["file"]) if row and row["file"] else None
    if path is None:
        return None
    return sum(p.stat().st_size for p in
               (path, path.with_name(path.name + "-wal"), path.with_name(path.name + "-shm"))
               if p.exists())


def start_scan(conn: sqlite3.Connection) -> str:
    """Mint the scan identifier and open its row. §8.6 says "every scan" and no part
    publishes a scan id, so P1 mints one locally. Whether it should become shared
    identity is SPEC OQ19 and is not decided here."""
    scan_id = str(uuid.uuid4())
    baseline = json.dumps({
        "monotonic": time.monotonic(),
        "cpu_seconds": _cpu_seconds(),
    })
    conn.execute(
        "INSERT INTO scan_resource_usage (scan_id, started_at, baseline) VALUES (?, ?, ?)",
        (scan_id, datetime.now(timezone.utc).isoformat(), baseline),
    )
    return scan_id


def sample_scan_resources(conn: sqlite3.Connection, scan_id: str) -> None:
    """Sample the five counters P1 can observe. `llm_cost` is P8's (O9).

    Sub-values the standard library cannot supply are recorded as null: there is no
    network byte counter, no portable current-RSS reading, and no accelerator time.
    They are unavailable, which is not the same as zero (§8.6).
    """
    row = conn.execute(
        "SELECT baseline FROM scan_resource_usage WHERE scan_id = ?", (scan_id,)
    ).fetchone()
    baseline = json.loads(row["baseline"])
    # ru_maxrss is BYTES on macOS (v1 is macOS-only) and kilobytes on Linux.
    peak_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    conn.execute(
        "UPDATE scan_resource_usage SET elapsed_time = ?, memory = ?, "
        "cpu_accelerator = ?, storage = ?, network = ?, observed_at = ? "
        "WHERE scan_id = ?",
        (
            json.dumps({"seconds": time.monotonic() - baseline["monotonic"]}),
            json.dumps({"peak_bytes": peak_bytes, "current_bytes": None}),
            json.dumps({"cpu_seconds": _cpu_seconds() - baseline["cpu_seconds"],
                        "accelerator_seconds": None}),
            json.dumps({"database_bytes": _database_bytes(conn),
                        "log_bytes": None, "derived_artifact_bytes": None}),
            None,                       # unavailable, not zero
            datetime.now(timezone.utc).isoformat(),
            scan_id,
        ),
    )


def record_llm_cost(conn: sqlite3.Connection, scan_id: str, cost, *, author: str) -> None:
    """P8 is the single egress point and the only part that can know this (O9).
    P1 stores the value opaquely and compares it to nothing."""
    cursor = conn.execute(
        "UPDATE scan_resource_usage SET llm_cost = ?, observed_at = ? WHERE scan_id = ?",
        (json.dumps(cost), datetime.now(timezone.utc).isoformat(), scan_id),
    )
    if cursor.rowcount == 0:
        raise KeyError(f"unknown scan_id {scan_id!r}")


def scan_resource_usage(conn: sqlite3.Connection, scan_id: str) -> sqlite3.Row:
    """One row per scan, updated as the scan runs (Contract out §10)."""
    return conn.execute(
        "SELECT * FROM scan_resource_usage WHERE scan_id = ?", (scan_id,)
    ).fetchone()
