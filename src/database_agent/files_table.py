"""Contract out §2 — the `files` row: the union of §8.2's file record and §1.2's per-file record."""
from __future__ import annotations

import json
import os
import sqlite3
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

#: OQ1 — P1's own write into `scan_state` when a path's bytes change. Not a
#: value P3 may supply: this column is otherwise P3's vocabulary (Contract in).
SUPERSEDED_CONTENT = "superseded_content"


class ReservedScanState(Exception):
    """P3 owns `scan_state` except for P1's R3 sentinel, which P1 writes itself."""


# NOTE: P1 deliberately has no timestamp/filename derivation helper. P3 computes
# the R2 record once (O5) and hands it over; a helper here would be an invitation
# to re-derive it, which is the contract violation P3's drift test exists to catch.


def _is_same_file(recorded: str, observed: Path) -> bool:
    """Do these two path spellings name the same file on this filesystem?

    Asked of the filesystem, never guessed. On APFS and HFS+ the NFC and NFD
    spellings of one name open the same inode, so comparing `current_path` as a
    Python string mints a second `files` row for one file — and §8.3's collision
    policy, seeing two rows whose hashes "prove the files are identical", would
    offer to delete one copy and delete the only copy. Normalising the string
    instead would be wrong on a filesystem that does not fold, where the two
    spellings really are two files. The filesystem is asked instead.
    Compared with `lstat`, which does NOT follow symlinks, so a symlink and its
    target stay two records: the link has its own directory entry and its own
    inode, and §8.3 must be able to move one without touching the other. Two
    spellings of a single entry share one inode and are one record.

    This is a live comparison of two paths in one process, not a stored value:
    P1 OQ9 is about persisting a volume identifier, and nothing here is persisted.
    """
    try:
        a, b = os.lstat(recorded), os.lstat(observed)
    except OSError:
        return False        # one of them is gone: not the same file, possibly a move
    return (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)


def _require_caller_scan_state(scan_state: str) -> None:
    if scan_state == SUPERSEDED_CONTENT:
        raise ReservedScanState(
            f"{SUPERSEDED_CONTENT!r} is P1's R3 sentinel (OQ1); a caller cannot supply it"
        )


def record_file(conn: sqlite3.Connection, path: Path, *,
                filename: str,
                normalized_filename: str,
                extension: str,
                observed_size: int,
                observed_timestamps: str,
                parent_folder_context: str | None,
                mime_type: str | None,
                detected_format: str | None,
                scan_state: str,
                materialized: bool,
                content_hash: str | None = None) -> str:
    """Create the `files` row (Contract out §2).

    `mime_type`, `detected_format` and `scan_state` are P3's (Contract in: "store
    them"). They are required with no default: P1 does not sniff a MIME type, does
    not detect a format, and does not invent a scan state. `parent_folder_context`
    is §2.9's published name, stored in the `directory_position` column (§1.2's
    word) — one field, not two (MINOR 11).

    **P1 derives none of the R2 record.** Contract in: P3 hands P1 "its stat result
    (size, timestamps) ... and the §1.2 per-file fields — filename, normalized
    filename, extension", and P1's obligation is "store them". P3 SPEC O5 makes
    that exclusive: R2 is "the only computation of this record", and P3's plan has
    a drift test that a second derivation fails. So `filename`,
    `normalized_filename`, `extension`, `observed_size` and `observed_timestamps`
    are required keywords with no default — a default would let a caller omit one
    and silently get P1's derivation, which is the same violation wearing a
    friendlier face. P1 still computes the CONTENT HASH, because Contract in hands
    it "its bytes to hash" and R1 identity is P1's.

    `materialized` is passed through to `hash_file` (11-ops-runtime.md §5).
    `content_hash` is P1's: when the caller has already hashed this path (R1),
    pass it so the row is keyed on the digest identity resolution used. A second
    read between those two would let a sync agent change the bytes underneath
    the file_id.
    """
    _require_caller_scan_state(scan_state)
    digest = (
        content_hash if content_hash is not None
        else hash_file(path, materialized=materialized)
    )
    file_id = str(uuid.uuid4())
    conn.execute(
        f"INSERT INTO files ({','.join(FILES_COLUMNS)}) "
        f"VALUES ({','.join('?' * len(FILES_COLUMNS))})",
        (
            file_id, str(path), filename,
            normalized_filename, extension,
            parent_folder_context, volume_id_for(path),
            digest, HASH_ALGORITHM,
            observed_size, observed_timestamps,
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


def set_extraction_status(conn: sqlite3.Connection, file_id: str, *,
                          status_by_tier: dict, author: str,
                          component_version: str) -> None:
    """Record the per-tier extraction status a caller computed (§1.2, R3).

    The column has existed since the first schema and `invalidate_extraction_state`
    has always reset it, but nothing could ever SET it — so a real extraction left
    `files` reading `{}` forever and §8.6's progress line had no per-tier state to
    render. Found while planning P5, which computes this map and had nowhere to put it.

    **P1 holds no tier vocabulary.** I4's four analysis tiers are P4's, so the map is
    stored opaquely, exactly as `sensitivity_state` is: validating the keys here would
    put one vocabulary in two homes, which is this project's most expensive defect.
    A key P1 has never heard of round-trips unchanged.

    `author` and `component_version` name the part that did the extracting. As with
    `invalidate_extraction_state`, P1 appends no event of its own (M8): the acting
    part authors its `extraction` or `OCR` event and P1 records the status under it.
    """
    conn.execute(
        "UPDATE files SET extraction_status_by_tier = ? WHERE file_id = ?",
        (json.dumps(status_by_tier, sort_keys=True), file_id),
    )


def observe_path(conn: sqlite3.Connection, path: Path, *,
                 author: str,
                 component_version: str,
                 filename: str,
                 normalized_filename: str,
                 extension: str,
                 observed_size: int,
                 observed_timestamps: str,
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
    _require_caller_scan_state(scan_state)
    content_hash = hash_file(path, materialized=materialized)
    now = datetime.now(timezone.utc).isoformat()
    observed = str(path)

    # I1: a prior row for this hash is only the SAME file version if its recorded
    # path is no longer live. Two live copies are two records (§2.9, §8.3).
    # Exact path wins first: otherwise a deleted twin (earlier rowid, dead path)
    # would steal the still-live copy's identity on re-observation.
    same_hash = conn.execute(
        "SELECT * FROM files WHERE content_hash = ? AND scan_state != ? "
        "ORDER BY rowid", (content_hash, SUPERSEDED_CONTENT),
    ).fetchall()
    existing = next((row for row in same_hash if row["current_path"] == observed), None)
    # Same file under a different spelling of its name is the same file version,
    # not a duplicate. Checked before the dead-path branch so it can never be
    # mistaken for a move.
    if existing is None:
        existing = next(
            (row for row in same_hash if _is_same_file(row["current_path"], path)), None
        )
    if existing is None:
        path_taken = conn.execute(
            "SELECT 1 FROM files WHERE current_path = ? AND scan_state != ?",
            (observed, SUPERSEDED_CONTENT),
        ).fetchone()
        if path_taken is None:
            existing = next(
                (row for row in same_hash if not Path(row["current_path"]).exists()),
                None,
            )

    if existing is not None:
        if existing["current_path"] != observed:
            append_event(
                conn, event_type="stat observation", file_id=existing["file_id"],
                content_hash=content_hash, old_path=existing["current_path"],
                new_path=observed, subsystem=author,
                component_version=component_version, observed_at=now,
                explanation="same content observed at a new path (R2)",
            )
            conn.execute(
                "UPDATE files SET current_path = ? WHERE file_id = ?",
                (observed, existing["file_id"]),
            )
        return existing["file_id"]

    prior = conn.execute(
        "SELECT file_id FROM files WHERE current_path = ? AND scan_state != ?",
        (observed, SUPERSEDED_CONTENT),
    ).fetchone()
    if prior is not None:
        append_event(
            conn, event_type="external modification detection",
            file_id=prior["file_id"], content_hash=content_hash,
            old_path=observed, new_path=observed, subsystem=author,
            component_version=component_version, observed_at=now,
            explanation="content at this path changed; this version is superseded (R3)",
        )
        conn.execute(
            "UPDATE files SET scan_state = ? WHERE file_id = ?",
            (SUPERSEDED_CONTENT, prior["file_id"]),
        )
        invalidate_extraction_state(conn, prior["file_id"], author=author,
                                    component_version=component_version)

    file_id = record_file(
        conn, path, filename=filename, normalized_filename=normalized_filename,
        extension=extension, observed_size=observed_size,
        observed_timestamps=observed_timestamps,
        parent_folder_context=parent_folder_context,
        mime_type=mime_type, detected_format=detected_format,
        scan_state=scan_state, materialized=materialized,
        content_hash=content_hash,
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
