# src/scan_agent/stat_cache.py
"""Contract out R4 — §1.2's stat-based cache.

§1.2: "It uses a stat-based cache: if a file's size and modification time have not
changed, the engine reuses its existing extraction results. If either changes, it
recomputes the relevant information instead of assuming that time only moves forward.
This protects against restores, migrations, and other filesystem changes that can
alter state unexpectedly."

Disjunctive (size OR mtime) and a DIFFERENCE test, never a newer-than test: an mtime
that moves backwards is a change. `recompute` includes recomputing the content hash,
because §8.2 makes the hash the thing that decides whether a new version exists.

This cache decides whether P3 re-READS. §3.4's cache key — content hash + extractor
version + analysis tier + model identifier + prompt fingerprint — decides whether an
extraction RESULT is reused, and belongs to P6. Nothing here touches it.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

#: R4's two verdicts, the SPEC's words.
VERDICT_REUSE = "reuse"
VERDICT_RECOMPUTE = "recompute"

#: R4's four reasons, the SPEC's words, and no fifth.
REASON_FIRST_OBSERVATION = "first observation"
REASON_UNCHANGED = "unchanged"
REASON_SIZE_CHANGED = "size changed"
REASON_MODIFICATION_TIME_CHANGED = "modification time changed"


@dataclass(frozen=True)
class CacheVerdict:
    observed_size: int
    observed_modification_time: float
    prior_observed_size: int | None
    prior_observed_modification_time: float | None
    verdict: str
    reason: str


def cache_verdict(observed, prior) -> CacheVerdict:
    """§1.2's verdict for one observed file. `prior` is P3's previous R4 row or None.

    Size is compared first so that a file whose size AND mtime both changed reports
    one deterministic reason — R4's `reason` is a single value and the SPEC supplies
    no compound one. Both observed and both prior values are on the record either way.
    """
    if prior is None:
        return CacheVerdict(observed.size, observed.mtime, None, None,
                            VERDICT_RECOMPUTE, REASON_FIRST_OBSERVATION)

    prior_size = prior["observed_size"]
    prior_mtime = prior["observed_modification_time"]
    if observed.size != prior_size:
        reason = REASON_SIZE_CHANGED
    elif observed.mtime != prior_mtime:
        # A difference test. Backwards is a change (§1.2: "instead of assuming that
        # time only moves forward"), which is what protects restores and migrations.
        reason = REASON_MODIFICATION_TIME_CHANGED
    else:
        return CacheVerdict(observed.size, observed.mtime, prior_size, prior_mtime,
                            VERDICT_REUSE, REASON_UNCHANGED)
    return CacheVerdict(observed.size, observed.mtime, prior_size, prior_mtime,
                        VERDICT_RECOMPUTE, reason)


STAT_CACHE_DDL = """
CREATE TABLE IF NOT EXISTS stat_cache_verdicts (
    verdict_id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id                      TEXT NOT NULL REFERENCES scan_runs(scan_run_id),
    file_id                          TEXT,     -- identity as resolved by P1; NULL when
                                               -- §8.5's metadata-safe form has no bytes
    observed_path                    TEXT NOT NULL,   -- mechanics: the pre-hash key
    observed_size                    INTEGER NOT NULL,
    observed_modification_time       REAL NOT NULL,
    prior_observed_size              INTEGER,
    prior_observed_modification_time REAL,
    verdict                          TEXT NOT NULL,
    reason                           TEXT NOT NULL,
    observed_at                      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS stat_cache_by_path
    ON stat_cache_verdicts (observed_path, verdict_id);
"""


def prior_observation(conn: sqlite3.Connection, path) -> sqlite3.Row | None:
    """P3's most recent R4 row for this path, while its file still lives there.

    The join on `files.current_path` is what stops a verdict left behind by a file
    that has since moved away from being reused for a different file that later
    appears at the old path.
    """
    return conn.execute(
        "SELECT v.* FROM stat_cache_verdicts v "
        "JOIN files f ON f.file_id = v.file_id AND f.current_path = v.observed_path "
        "WHERE v.observed_path = ? ORDER BY v.verdict_id DESC LIMIT 1",
        (str(Path(path)),),
    ).fetchone()


def record_cache_verdict(conn: sqlite3.Connection, scan_run_id: str, path,
                         file_id: str | None, verdict: CacheVerdict) -> int:
    conn.execute(
        "INSERT INTO stat_cache_verdicts "
        "(scan_run_id, file_id, observed_path, observed_size, "
        " observed_modification_time, prior_observed_size, "
        " prior_observed_modification_time, verdict, reason, observed_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (scan_run_id, file_id, str(Path(path)), verdict.observed_size,
         verdict.observed_modification_time, verdict.prior_observed_size,
         verdict.prior_observed_modification_time, verdict.verdict, verdict.reason,
         datetime.now(timezone.utc).isoformat()),
    )
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]


def cache_verdicts(conn: sqlite3.Connection, scan_run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM stat_cache_verdicts WHERE scan_run_id = ? ORDER BY verdict_id",
        (scan_run_id,),
    ).fetchall()
