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
