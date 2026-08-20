# src/scan_agent/basic_record.py
"""Contract out R2 — the §1.2 per-file-version basic record.

§1.2: "For every file, the engine records path, filename, normalized filename,
extension, MIME type, size, timestamps, directory position, content hash, and scan
state."

R2 is the ONLY computation of this record (O5): P5's `source_type: filesystem`
observations cite this row and recompute none of its ten fields. P3 does not insert
into `files` — P1 owns identity resolution (§8.2) — so every field arrives through
P1's `observe_path`, which is also what makes the events P3-authored and P1-written.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from pathlib import Path, PurePath

from database_agent.events import append_event
from database_agent.files_table import get_file, observe_path

from scan_agent.authorship import COMPONENT_VERSION, SUBSYSTEM, event_defaults


def parent_folder_context(path) -> str:
    """§2.9's published name for §1.2's "directory position" — one field (MINOR 11).

    The value is the parent directory's path and nothing more. MINOR 11: "What the
    value contains is still only what §1.2 and §2.9 say — P3 invents no structure
    for it." No depth number, no ancestor list, no computed role.
    """
    return str(PurePath(path).parent)


def _already_discovered(conn: sqlite3.Connection, file_id: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM events WHERE file_id = ? AND event_type = 'discovery' LIMIT 1",
        (file_id,),
    ).fetchone() is not None


def record_basic_record(conn: sqlite3.Connection, observed, *,
                        mime_type_for: Callable[[Path], str | None],
                        scan_state: str) -> str:
    """Write one R2 row through P1 and append P3's events. Returns the file_id.

    `mime_type_for` is the caller's strategy: SPEC Q6 is OPEN on whether P3 sniffs a
    signature or records an extension-derived type P5 later corrects, and this plan
    answers neither. `scan_state` is the caller's value: SPEC Q4 is OPEN on the
    enumeration, and P3 invents none.
    """
    path = Path(observed.path)
    file_id = observe_path(
        conn, path,
        author=SUBSYSTEM,                # M8: the acting part authors, P1 writes
        component_version=COMPONENT_VERSION,
        # R2 is computed once, HERE (O5). P1 stores these and derives none of them:
        # a second derivation is the contract violation Task 10's drift test exists
        # to catch, and P1's `record_file` now requires them with no default so the
        # violation cannot happen silently.
        filename=path.name,
        # SPEC Q1 is OPEN: Unicode form, case folding, whitespace and separator
        # collapse, extension retention and diacritic handling are all unstated.
        # P3 therefore passes the name through UNCHANGED. This is not a
        # normalization and must not be read as one — it is the only value that
        # adds no information and answers nothing. Choosing a Unicode form here
        # would close Q1 inside an implementation, and §3.7's word-boundary
        # matching would then run over a form nobody ratified. Task 17 greps this
        # source for the names of the standard normalization calls and for the
        # short names of the Unicode forms, and fails if one appears — including
        # in a comment, so this note deliberately spells none of them.
        normalized_filename=path.name,
        extension=path.suffix,
        observed_size=observed.size,
        # SPEC Q2 is OPEN on timestamp representation. P3 records the stat value
        # it observed and invents no format — an ISO string would be a choice of
        # precision, timezone and which of mtime/ctime/birthtime matters.
        observed_timestamps=json.dumps({"mtime": observed.mtime}),
        parent_folder_context=parent_folder_context(path),
        mime_type=mime_type_for(path),
        detected_format=None,        # not one of R2's ten; §2.9's determination is P5's
        scan_state=scan_state,
        materialized=not observed.dataless,
    )
    content_hash = get_file(conn, file_id)["content_hash"]

    if not _already_discovered(conn, file_id):
        append_event(conn, **event_defaults(
            event_type="discovery", file_id=file_id, content_hash=content_hash,
            new_path=observed.path,
            explanation=json.dumps({"rule": "§1.1 corpus selection",
                                    "applies_to": observed.applies_to}),
        ))

    append_event(conn, **event_defaults(
        event_type="stat observation", file_id=file_id, content_hash=content_hash,
        new_path=observed.path,
        explanation=json.dumps({"observed_size": observed.size,
                                "observed_modification_time": observed.mtime}),
    ))
    return file_id
    append_stat_observation(conn, file_id, observed)
    return file_id


def append_stat_observation(conn: sqlite3.Connection, file_id: str, observed) -> None:
    """§8.2's `stat observation` — "size/timestamps observed; the §1.2 stat cache
    reads it". Appended on EVERY scan, reuse and recompute alike, so that a second
    scan adds one and leaves the earlier intact (Done-means 11)."""
    append_event(conn, **event_defaults(
        event_type="stat observation", file_id=file_id,
        content_hash=get_file(conn, file_id)["content_hash"],
        new_path=str(observed.path),
        explanation=json.dumps({"observed_size": observed.size,
                                "observed_modification_time": observed.mtime}),
    ))


def append_external_modification_detection(conn: sqlite3.Connection, file_id: str,
                                           observed, verdict) -> None:
    """§8.2's `external modification detection` — "a re-scan finds a recorded file's
    size or modification time changed underneath the product" (§1.2).

    P3 is one of this type's TWO authors (M8); P12's half is §8.3's staleness
    triggers and sync conflicts, and the two are separable by `subsystem`.

    `content_hash` is the hash the file was RECORDED under: the event says that the
    version P3 knows as X has changed on disk, and at detection time the new hash has
    not been taken — §1.2 requires the detection before the recompute. Recording a
    hash P3 has not computed would be a fabrication.
    """
    append_event(conn, **event_defaults(
        event_type="external modification detection", file_id=file_id,
        content_hash=get_file(conn, file_id)["content_hash"],
        old_path=str(observed.path), new_path=str(observed.path),
        explanation=json.dumps({
            "reason": verdict.reason,
            "prior_observed_size": verdict.prior_observed_size,
            "observed_size": verdict.observed_size,
            "prior_observed_modification_time": verdict.prior_observed_modification_time,
            "observed_modification_time": verdict.observed_modification_time,
        }),
    ))
