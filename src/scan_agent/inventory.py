# src/scan_agent/inventory.py
"""Contract out R6 — the directory inventory and its curation signal (§1.1, §5.10).

§1.1 requires the engine to "understand the current folder landscape and to show
where a proposed branch could eventually live". §5.10 requires the canvas to show
"where a current folder sits in the filesystem, how many files it contains" and
"whether it appears to be curated or merely incidental".

P3 COMPUTES this signal; it acts on nothing. Preserve versus adopt, attach versus
merge versus leave untouched, and §5.10's prohibition on flattening, renaming or
reorganizing are all P10's.
"""
from __future__ import annotations

import json
import sqlite3

#: §5.10's three values. `undetermined` is a real value, not a failure: §8.6 requires
#: the product to "leave the file or group in review rather than guessing".
CURATION_CURATED = "curated"
CURATION_INCIDENTAL = "incidental"
CURATION_UNDETERMINED = "undetermined"
CURATION_SIGNAL_VALUES: tuple[str, str, str] = (
    CURATION_CURATED, CURATION_INCIDENTAL, CURATION_UNDETERMINED,
)


def curation_evidence(observed) -> dict:
    """The observations behind the signal (§8.2's "structured explanation").

    R3 records the one project-root marker that fired a verdict; this records every
    marker observed in the directory itself, so nothing is lost.
    """
    return {
        "file_count": observed.file_count,
        "subdirectory_count": observed.subdirectory_count,
        "extension_mix": dict(observed.extension_mix),
        "project_root_markers": list(observed.project_root_markers),
    }


def curation_signal(evidence: dict) -> str:
    """§5.10's "curated or merely incidental".

    DEFERRED — and deliberately not guessed. §1.1 gives one worked case ("a lot of
    files such as JSON and other software material") and no number, no ratio, and no
    list of which extensions read as software material. Until that threshold is
    hand-authored, the honest value is `undetermined` for every directory, and a
    directory whose evidence supports neither reading is never rounded to
    `incidental`. The evidence above is complete now, so authoring the threshold is
    a change to this one function and to nothing else.
    """
    return CURATION_UNDETERMINED


INVENTORY_DDL = """
CREATE TABLE IF NOT EXISTS directory_inventory (
    inventory_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id        TEXT NOT NULL REFERENCES scan_runs(scan_run_id),
    directory_path     TEXT NOT NULL,
    parent_directory   TEXT,                -- NULL at a scan root: the top of the
                                            -- observed landscape
    file_count         INTEGER NOT NULL,    -- non-excluded, directly inside
    subdirectory_count INTEGER NOT NULL,    -- non-excluded, directly inside
    extension_mix      TEXT NOT NULL,       -- JSON: extension -> count
    curation_signal    TEXT NOT NULL,
    curation_evidence  TEXT NOT NULL,       -- JSON
    applies_to         TEXT NOT NULL        -- mechanics: which side of the scan
);
"""


def record_directory(conn: sqlite3.Connection, scan_run_id: str, observed) -> int:
    evidence = curation_evidence(observed)
    conn.execute(
        "INSERT INTO directory_inventory "
        "(scan_run_id, directory_path, parent_directory, file_count, "
        " subdirectory_count, extension_mix, curation_signal, curation_evidence, "
        " applies_to) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (scan_run_id, observed.directory_path, observed.parent_directory,
         observed.file_count, observed.subdirectory_count,
         json.dumps(dict(observed.extension_mix)), curation_signal(evidence),
         json.dumps(evidence), observed.applies_to),
    )
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]


def directory_inventory(conn: sqlite3.Connection, scan_run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM directory_inventory WHERE scan_run_id = ? ORDER BY inventory_id",
        (scan_run_id,),
    ).fetchall()
