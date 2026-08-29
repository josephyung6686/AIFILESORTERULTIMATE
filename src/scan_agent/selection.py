# src/scan_agent/selection.py
"""Contract out R1 — the corpus selection record (§1.1).

§1.1: "The user first chooses which folders should be analyzed and which high-level
locations may serve as roots for a future file tree… The user can also select whether
files may move across high-level folders."

Three selections, and P3 owns no others. Roots are CONTEXT, not permission: "At this
stage, roots are context for the proposal canvas, not permission to move files."
This module grants nothing, targets nothing, and approves nothing.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

SELECTION_COLUMNS: tuple[str, ...] = (
    "selection_id", "sources", "candidate_roots", "cross_folder_moves",
    "selected_at", "selected_by",
)

SELECTION_DDL = """
CREATE TABLE IF NOT EXISTS corpus_selections (
    selection_id       TEXT PRIMARY KEY,
    sources            TEXT NOT NULL,     -- JSON array of paths (§1.1)
    candidate_roots    TEXT NOT NULL,     -- JSON array of paths (§1.1) -- context only
    cross_folder_moves INTEGER NOT NULL,  -- the user's selection (§1.1); enforced
                                          -- nowhere in P3 -- SPEC Q12 is OPEN
    selected_at        TEXT NOT NULL,
    selected_by        TEXT               -- nullable: §8.2 records identity only on
                                          -- an explicit user action (MINOR 10)
);
"""


def record_selection(conn: sqlite3.Connection, *,
                     sources: Iterable[Path],
                     candidate_roots: Iterable[Path],
                     cross_folder_moves: bool,
                     selected_by: str | None) -> str:
    """Record one corpus selection (R1). Returns its `selection_id`.

    All four keywords are required. §1.1 assigns the choice to the user, so P3 has
    no source set and no root set until one is supplied and must not derive either
    from the machine's layout. `selected_by` may be None — an R1 not authored by a
    user leaves the field empty, which is a correct value, not a missing one.
    """
    selection_id = str(uuid.uuid4())
    conn.execute(
        f"INSERT INTO corpus_selections ({','.join(SELECTION_COLUMNS)}) "
        f"VALUES ({','.join('?' * len(SELECTION_COLUMNS))})",
        (
            selection_id,
            json.dumps([str(Path(p)) for p in sources]),
            json.dumps([str(Path(p)) for p in candidate_roots]),
            int(bool(cross_folder_moves)),
            datetime.now(timezone.utc).isoformat(),
            selected_by,
        ),
    )
    return selection_id


def get_selection(conn: sqlite3.Connection, selection_id: str) -> sqlite3.Row:
    return conn.execute(
        "SELECT * FROM corpus_selections WHERE selection_id = ?", (selection_id,)
    ).fetchone()


def selection_sources(conn: sqlite3.Connection, selection_id: str) -> list[Path]:
    """The folders the user chose to analyze (§1.1). Empty is a real answer."""
    return [Path(p) for p in json.loads(get_selection(conn, selection_id)["sources"])]


def selection_candidate_roots(conn: sqlite3.Connection, selection_id: str) -> list[Path]:
    """The high-level locations that may serve as roots for a future file tree.

    Context for the proposal canvas (§1.1). This list is not an authorization and
    is consumable by P11 or P12 as nothing.
    """
    return [Path(p) for p in
            json.loads(get_selection(conn, selection_id)["candidate_roots"])]


def selection_payload(conn: sqlite3.Connection, selection_id: str) -> dict:
    """R1, serialized for a §8.5 replay bundle.

    SPEC Serialization: "R1–R4 and R6 must serialize into and re-assert from a P2
    replay bundle." These are R1's published fields and no others — `selection_id`
    is P3's local key for the row, not part of the record, so it does not travel.
    """
    row = get_selection(conn, selection_id)
    payload = {name: row[name] for name in SELECTION_COLUMNS if name != "selection_id"}
    payload["sources"] = json.loads(payload["sources"])
    payload["candidate_roots"] = json.loads(payload["candidate_roots"])
    return payload


def record_selection_from_payload(conn: sqlite3.Connection, payload: dict) -> str:
    """Re-assert R1 from a serialized payload (§8.5). Returns the new selection_id.

    The three §1.1 choices and §8.2's user identity are the user's and travel with
    the bundle. `selected_at` does not: the row is stamped when it is written, and
    `11` §3 says "P2 replay is not a session; it is a harness run" — writing the
    original time onto a harness row would record that a user chose again at that
    moment. The original stays readable in the payload.
    """
    return record_selection(
        conn,
        sources=payload["sources"],
        candidate_roots=payload["candidate_roots"],
        cross_folder_moves=payload["cross_folder_moves"],
        selected_by=payload["selected_by"],
    )
