"""Contract out §2 — the `files` row: the union of §8.2's file record and §1.2's per-file record."""
from __future__ import annotations

import json
import sqlite3
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path

from database_agent.identity import HASH_ALGORITHM, hash_file, volume_id_for

FILES_COLUMNS: tuple[str, ...] = (
    "file_id", "current_path", "filename", "normalized_filename", "extension",
    "directory_position", "volume_id", "content_hash", "hash_algorithm",
    "observed_size", "observed_timestamps", "mime_type", "detected_format",
    "scan_state", "extraction_status_by_tier", "sensitivity_state",
)


def _timestamps(path: Path) -> str:
    stat = path.stat()
    return json.dumps({
        "mtime": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "ctime": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
    })


def record_file(conn: sqlite3.Connection, path: Path, *,
                parent_folder_context: str | None,
                mime_type: str | None,
                detected_format: str | None,
                scan_state: str,
                materialized: bool) -> str:
    """Create the `files` row (Contract out §2).

    `mime_type`, `detected_format` and `scan_state` are P3's (Contract in: "store
    them"). They are required with no default: P1 does not sniff a MIME type, does
    not detect a format, and does not invent a scan state. `parent_folder_context`
    is §2.9's published name, stored in the `directory_position` column (§1.2's
    word) — one field, not two (MINOR 11).

    `materialized` is passed through to `hash_file` (11-ops-runtime.md §5).
    """
    file_id = str(uuid.uuid4())
    stat = path.stat()
    conn.execute(
        f"INSERT INTO files ({','.join(FILES_COLUMNS)}) "
        f"VALUES ({','.join('?' * len(FILES_COLUMNS))})",
        (
            file_id, str(path), path.name,
            unicodedata.normalize("NFC", path.name), path.suffix,
            parent_folder_context, volume_id_for(path),
            hash_file(path, materialized=materialized), HASH_ALGORITHM,
            stat.st_size, _timestamps(path),
            mime_type, detected_format,
            scan_state, "{}", None,
        ),
    )
    return file_id


def get_file(conn: sqlite3.Connection, file_id: str) -> sqlite3.Row:
    return conn.execute("SELECT * FROM files WHERE file_id = ?", (file_id,)).fetchone()


from database_agent.events import append_event


def invalidate_extraction_state(conn: sqlite3.Connection, file_id: str, *,
                                author: str, component_version: str) -> None:
    """R3 — mark the file's extraction state invalid so the relevant extractors
    re-run. P1 does not run them; that is P5.

    `author` is the part that observed the change. Mutating the current projection
    on `files` without the authoring part's event is not accepted, so the caller
    appends its event and P1 records the invalidation under that author.
    """
    conn.execute(
        "UPDATE files SET extraction_status_by_tier = '{}' WHERE file_id = ?",
        (file_id,),
    )


def observe_path(conn: sqlite3.Connection, path: Path, *,
                 author: str,
                 component_version: str,
                 parent_folder_context: str | None,
                 mime_type: str | None,
                 detected_format: str | None,
                 scan_state: str,
                 materialized: bool) -> str:
    """R2/R3 — resolve a path observation to a file version (§8.2).

    Write-only helper: `author` is the part making the observation (P3 in the
    running system) and is what lands in `subsystem`. P1 appends no event on its
    own initiative (M8) and originates none of the scan types (Contract in).

    Same bytes at a new path where the old path is gone: same file version, path
    updated, history retained (a move).
    Same bytes at a new path where BOTH are live: two records sharing one
    content_hash (I1) — §2.9's duplicate family and §8.3's identical-file collision
    both require the two copies to remain distinguishable.
    New bytes: a new version; the prior row is superseded and its extraction state
    invalidated, under the caller's event.
    """
    content_hash = hash_file(path, materialized=materialized)
    now = datetime.now(timezone.utc).isoformat()

    # I1: a prior row for this hash is only the SAME file version if its recorded
    # path is no longer live. Two live copies are two records (§2.9, §8.3).
    existing = None
    for candidate in conn.execute(
        "SELECT * FROM files WHERE content_hash = ? AND scan_state != 'superseded_content' "
        "ORDER BY rowid", (content_hash,)
    ).fetchall():
        if candidate["current_path"] == str(path) or not Path(candidate["current_path"]).exists():
            existing = candidate
            break

    if existing is not None:
        if existing["current_path"] != str(path):
            append_event(
                conn, event_type="stat observation", file_id=existing["file_id"],
                content_hash=content_hash, old_path=existing["current_path"],
                new_path=str(path), subsystem=author,
                component_version=component_version, observed_at=now,
                explanation="same content observed at a new path (R2)",
            )
            conn.execute(
                "UPDATE files SET current_path = ? WHERE file_id = ?",
                (str(path), existing["file_id"]),
            )
        return existing["file_id"]

    prior = conn.execute(
        "SELECT file_id FROM files WHERE current_path = ? AND scan_state != 'superseded_content'",
        (str(path),),
    ).fetchone()
    if prior is not None:
        append_event(
            conn, event_type="external modification detection",
            file_id=prior["file_id"], content_hash=content_hash,
            old_path=str(path), new_path=str(path), subsystem=author,
            component_version=component_version, observed_at=now,
            explanation="content at this path changed; this version is superseded (R3)",
        )
        conn.execute(
            "UPDATE files SET scan_state = 'superseded_content' WHERE file_id = ?",
            (prior["file_id"],),
        )
        invalidate_extraction_state(conn, prior["file_id"], author=author,
                                    component_version=component_version)

    file_id = record_file(
        conn, path, parent_folder_context=parent_folder_context,
        mime_type=mime_type, detected_format=detected_format,
        scan_state=scan_state, materialized=materialized,
    )
    append_event(
        conn, event_type="hashing", file_id=file_id, content_hash=content_hash,
        new_path=str(path), subsystem=author, component_version=component_version,
        observed_at=now, explanation="new content hash recorded (R1, R3)",
    )
    return file_id


def file_path_history(conn: sqlite3.Connection, file_id: str) -> list[sqlite3.Row]:
    """§8.2 'Path history' — a projection over events carrying old/new paths.

    SPEC Contract out §2's shape is (path, volume_id, observed_at, event_id). No
    per-observation volume value is recorded: `events` has no volume column and
    P1 OQ9 is open, so the column is published as NULL — unknown, never a value
    a consumer could mistake for the volume this path was observed on.
    """
    return conn.execute(
        "SELECT COALESCE(new_path, old_path) AS path, NULL AS volume_id, "
        "observed_at, event_id "
        "FROM events WHERE file_id = ? AND (new_path IS NOT NULL OR old_path IS NOT NULL) "
        "ORDER BY event_id",
        (file_id,),
    ).fetchall()
