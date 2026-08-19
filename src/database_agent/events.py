"""Contract out §3 — the append-only provenance log (§8.2).

Append-only means INSERT only: no UPDATE, no DELETE, no row rewrite, no truncation,
no compaction that drops rows (R6). Enforced by trigger, not by convention.
"""
from __future__ import annotations

import sqlite3

#: §8.2's eleven event-record fields. Exactly eleven, forever (MINOR 1).
EVENT_FIELDS: tuple[str, ...] = (
    "event_type", "file_id", "content_hash", "old_path", "new_path",
    "subsystem", "component_version", "prompt_fingerprint", "user_id",
    "observed_at", "explanation",
)

#: §8.7 columns, carried beside the eleven on user-action events. P1 stores them
#: opaquely: it derives no polarity, compares no basis_key, interprets no
#: proposal_class. polarity ∈ accept | reject and is supplied by the acting part.
CORRECTION_FIELDS: tuple[str, ...] = (
    "correction_scope", "correction_subject", "polarity", "proposal_class", "basis_key",
)

_WRITABLE = (*EVENT_FIELDS, *CORRECTION_FIELDS, "base_event_type")


def append_event(conn: sqlite3.Connection, **fields) -> int:
    """Append one event. Returns its monotonic event_id.

    `subsystem` is the authoring part (§8.2 "the responsible subsystem"). P1 never
    fills it in: the acting part authors, P1 writes (M8).
    """
    columns = [k for k in fields if k in _WRITABLE]
    values = [fields[k] for k in columns]
    cursor = conn.execute(
        f"INSERT INTO events ({','.join(columns)}) VALUES ({','.join('?' * len(columns))})",
        values,
    )
    return cursor.lastrowid
