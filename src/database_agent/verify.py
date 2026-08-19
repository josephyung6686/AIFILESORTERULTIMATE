"""Contract out §5 — the four checksum verification points (§8.2).

P12 (§8.3) is the only caller (MINOR 5). §6 decides where a file should go and never
touches bytes. P1 performs and records; it decides nothing about what a mismatch means —
§8.3's stale and undo decisions belong to P12.

Authorship: the `hashing` event for a verification is authored by the calling part,
with `subsystem` naming P1 as the performer (SPEC, Cross-cutting answers →
Provenance). P1 never originates a verification, so `author` has no default.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from database_agent.events import append_event
from database_agent.files_table import get_file
from database_agent.identity import hash_file


class VerificationPoint(Enum):
    V1 = "before preparing a filesystem action"
    V2 = "immediately before executing a move or copy"
    V3 = "after completing the action"
    V4 = "cross-volume copy-and-delete destination confirmation"


def _explanation(point: VerificationPoint, author: str, result: str, **extra) -> str:
    """§8.2's 'structured explanation'. It names who asked; `subsystem` names who performed."""
    return json.dumps({"point": point.name, "description": point.value,
                       "requested_by": author, "result": result, **extra})


def verify_content(conn: sqlite3.Connection, file_id: str, expected_hash: str, *,
                   point: VerificationPoint, author: str, component_version: str,
                   materialized: bool) -> str:
    """Return 'match' or 'mismatch'. Records the check; interprets nothing."""
    row = get_file(conn, file_id)
    actual = hash_file(Path(row["current_path"]), materialized=materialized)
    result = "match" if actual == expected_hash else "mismatch"
    append_event(
        conn, event_type="hashing", file_id=file_id, content_hash=actual,
        subsystem="P1", component_version=component_version,
        observed_at=datetime.now(timezone.utc).isoformat(),
        explanation=_explanation(point, author, result),
    )
    return result


def confirm_cross_volume_copy(conn: sqlite3.Connection, *, source: Path,
                              destination: Path, expected_hash: str, author: str,
                              component_version: str, materialized: bool) -> bool:
    """V4 — the destination copy is hashed and confirmed BEFORE the source may be
    removed (§8.2). P1 never removes the source; it only answers whether it may be."""
    confirmed = (destination.exists()
                 and hash_file(destination, materialized=materialized) == expected_hash)
    append_event(
        conn, event_type="hashing", content_hash=expected_hash,
        old_path=str(source), new_path=str(destination), subsystem="P1",
        component_version=component_version,
        observed_at=datetime.now(timezone.utc).isoformat(),
        explanation=_explanation(VerificationPoint.V4, author,
                                 "confirmed" if confirmed else "refused"),
    )
    return confirmed
