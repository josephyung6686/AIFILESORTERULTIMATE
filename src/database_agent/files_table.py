"""Contract out §2 — the `files` row: the union of §8.2's file record and §1.2's per-file record."""
from __future__ import annotations

import json
import os
import sqlite3
import stat
import uuid
from datetime import datetime, timezone
from pathlib import Path

from database_agent.identity import HASH_ALGORITHM, hash_file, volume_id_for

FILES_COLUMNS: tuple[str, ...] = (
    "file_id", "current_path", "filename", "normalized_filename", "extension",
    "directory_position", "volume_id", "content_hash", "hash_algorithm",
    "observed_size", "observed_timestamps", "mime_type", "detected_format",
    "scan_state", "extraction_status_by_tier", "sensitivity_state",
    "st_dev", "st_ino",
)

#: OQ1 — P1's own write into `scan_state` when a path's bytes change. Not a
#: value P3 may supply: this column is otherwise P3's vocabulary (Contract in).
SUPERSEDED_CONTENT = "superseded_content"


class ReservedScanState(Exception):
    """P3 owns `scan_state` except for P1's R3 sentinel, which P1 writes itself."""


# NOTE: P1 deliberately has no timestamp/filename derivation helper. P3 computes
# the R2 record once (O5) and hands it over; a helper here would be an invitation
# to re-derive it, which is the contract violation P3's drift test exists to catch.


def _lstat_or_none(recorded: str) -> os.stat_result | None:
    """The identity of a recorded path spelling, or None if it names nothing.

    `observe_path` compares two path spellings by inode, asked of the filesystem
    and never guessed. On APFS and HFS+ the NFC and NFD spellings of one name open
    the same inode, so comparing `current_path` as a Python string mints a second
    `files` row for one file — and §8.3's collision policy, seeing two rows whose
    hashes "prove the files are identical", would offer to delete one copy and
    delete the only copy. Normalising the string instead would be wrong on a
    filesystem that does not fold, where the two spellings really are two files.
    The filesystem is asked instead.

    `lstat`, which does NOT follow symlinks, so a symlink and its target stay two
    records: the link has its own directory entry and its own inode, and §8.3 must
    be able to move one without touching the other. Two spellings of a single entry
    share one inode and are one record.

    This is a live comparison of two paths in one process, not a stored value:
    P1 OQ9 is about persisting a volume identifier, and nothing here is persisted.

    None means gone, or unreachable — either way not the same file, possibly a
    move. It also settles the dead-path question for free: if `lstat` fails then
    `stat` fails too, so `Path(recorded).exists()` is False without asking again.
    """
    try:
        return os.lstat(recorded)
    except OSError:
        return None


def _inode_of(path: Path) -> tuple[int | None, int | None]:
    """`(st_dev, st_ino)` for the row, or `(None, None)` if the path names nothing.

    `lstat`, for the reason `_lstat_or_none` gives: a symlink's own inode, so a link
    and its target are two rows rather than one. NULL when the path cannot be stat'd,
    which is the honest value and also the safe one -- SQL equality never matches
    NULL, so a row with no recorded inode can never be mistaken for the file being
    observed.
    """
    recorded = _lstat_or_none(str(path))
    return (None, None) if recorded is None else (recorded.st_dev, recorded.st_ino)


def _same_inode(recorded: os.stat_result | None,
                observed: os.stat_result | None) -> bool:
    return (recorded is not None and observed is not None
            and (recorded.st_dev, recorded.st_ino)
            == (observed.st_dev, observed.st_ino))


def _home_is_gone(recorded_stat: os.stat_result | None, recorded: str) -> bool:
    """Is the path a row records no longer there?

    `lstat` failing settles it. A live path settles it too, with one exception the
    walk already paid for: a symlink can `lstat` and still not `exists()`, and a
    dangling link is not a home. Guarded by `S_ISLNK` so a regular file never buys
    the second syscall.
    """
    if recorded_stat is None:
        return True
    return stat.S_ISLNK(recorded_stat.st_mode) and not Path(recorded).exists()


def _path_is_taken(conn: sqlite3.Connection, observed: str) -> bool:
    """Is some live row already sitting at the path being observed?

    Asked before any row is relocated onto `observed`. Without it a row whose home
    went missing would be moved on top of a live row recording different bytes at
    this path, leaving two live rows at one path instead of superseding the one that
    is there (R3).
    """
    return conn.execute(
        "SELECT 1 FROM files WHERE current_path = ? AND scan_state != ?",
        (observed, SUPERSEDED_CONTENT),
    ).fetchone() is not None


def _row_for_this_inode(conn: sqlite3.Connection, content_hash: str, observed: str,
                        observed_stat: os.stat_result) -> sqlite3.Row | None:
    """The recorded row that IS the file being observed, or None.

    This is the question the old family walk existed to answer, and it answered it by
    `lstat`ing every member of the duplicate family to find at most one match: O(k)
    syscalls per file admitted, O(k^2) to admit a family of k. Empty files,
    `.DS_Store`, stub configs and repeated downloads make families that size on a real
    disk, so the walk is gone and the same question is asked of an index.

    **A row is a CANDIDATE, never an answer.** `st_dev`/`st_ino` are what the
    filesystem said when the row last wrote its path, and inodes are recycled: the
    file that owned that pair may have been deleted and the number handed to another.
    So every candidate is confirmed against what the filesystem says NOW, and there
    are exactly two ways a candidate confirms:

    * its recorded path is still there and IS this inode -- one file under two
      spellings of its name, which is one record; or
    * its recorded path is GONE. A rename is the whole reason this index exists, and
      a rename necessarily leaves the old name behind: the row remembers an inode
      that is no longer reachable by the name the row records. Demanding that the old
      name still resolve would reject every rename, which is precisely the case the
      index was built to catch.

    The second is strictly MORE evidence than the walk required. The walk relocated
    any family member whose path had gone missing, on no inode evidence at all --
    which of k identical copies had moved was a guess it settled by rowid. Here the
    filesystem itself says this row's remembered inode is the file now being looked
    at.

    A candidate whose recorded path is live but is a DIFFERENT inode is rejected, and
    that is the recycled-inode case: the number has been handed to another file and
    the row's own home says so
    (test_a_recycled_inode_is_a_candidate_and_never_an_answer).

    Rowid order, and the first confirmed row wins, because the walk took the first
    match in rowid order too. The live match is settled across the whole candidate
    set before any vanished home is used, so the same file under a different spelling
    can never be mistaken for a move.
    """
    vanished: sqlite3.Row | None = None
    for row in conn.execute(
        "SELECT file_id, current_path FROM files "
        "WHERE st_dev = ? AND st_ino = ? AND content_hash = ? AND scan_state != ? "
        "ORDER BY rowid",
        (observed_stat.st_dev, observed_stat.st_ino, content_hash,
         SUPERSEDED_CONTENT),
    ):
        recorded_stat = _lstat_or_none(row["current_path"])
        if _same_inode(recorded_stat, observed_stat):
            return row
        if vanished is None and _home_is_gone(recorded_stat, row["current_path"]):
            vanished = row
    if vanished is None or _path_is_taken(conn, observed):
        return None
    return vanished


def _relocated_row(conn: sqlite3.Connection, content_hash: str, observed: str,
                   observed_stat: os.stat_result | None) -> sqlite3.Row | None:
    """R2's move: same bytes at a new path where the recorded home is gone.

    Reached only after the inode question above has been answered NO, which keeps the
    original ordering: same file under a different spelling of its name is the same
    file version, not a duplicate, and is settled before this so it can never be
    mistaken for a move.

    A same-volume rename keeps its inode and never gets here. What does is a
    cross-volume move and a copy-then-delete, where the file that arrives is a
    genuinely new inode and the only evidence of the move is that a recorded copy of
    these bytes has gone missing.

    **Deletion leaves nothing in the database**, so no index can answer "is any
    recorded copy of these bytes missing?" -- only one filesystem call per recorded
    copy can, which is the O(k^2) this whole change exists to remove. So the question
    asked here is narrower and answerable in one call: *is the OLDEST recorded home of
    these bytes gone?* It is the same answer the walk gave whenever the family has one
    recorded home -- the case §8.2's move rule is written for, and the case where the
    answer is not a guess -- and whenever the oldest home is the one that went missing.

    Inside a family with several live copies whose oldest member is still live, a
    cross-volume move is now recorded as a new file rather than as a relocation of an
    arbitrary member. That is a deliberate narrowing and it errs in the safe
    direction: it can only ever mint an extra record, never merge two files into one.
    The walk's answer there was a guess anyway -- which of k identical copies moved is
    not knowable, and it always named the earliest rowid.

    The oldest home is `lstat`ed rather than trusted, so a stale stored inode cannot
    hide a file from itself: if the filesystem says that path is the file being
    observed, it is, whatever the row remembers.
    """
    oldest = conn.execute(
        "SELECT file_id, current_path FROM files "
        "WHERE content_hash = ? AND scan_state != ? ORDER BY rowid LIMIT 1",
        (content_hash, SUPERSEDED_CONTENT),
    ).fetchone()
    if oldest is None:
        return None
    recorded_stat = _lstat_or_none(oldest["current_path"])
    if _same_inode(recorded_stat, observed_stat):
        return oldest
    if not _home_is_gone(recorded_stat, oldest["current_path"]):
        return None
    return None if _path_is_taken(conn, observed) else oldest


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
            *_inode_of(path),
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


def set_sensitivity_state(conn: sqlite3.Connection, file_id: str, *,
                          state: dict, author: str,
                          component_version: str) -> None:
    """Record the §8.4 sensitivity state a caller classified (D2).

    The exact twin of `set_extraction_status`, and it exists for the identical
    reason: `sensitivity_state` has been a column on `files` since the first schema
    with **nothing able to write it**. Every reader saw NULL and could not tell *not
    yet classified* from *classified as carrying nothing* -- and the Wave-2 caller,
    reaching for a value, passed this NULL into the bundle's `handling_class`, which
    is a different field on a different record. One concept with no writer produced a
    second concept with a wrong one.

    **P1 holds no handling-class vocabulary.** §8.4's classes are P7's, so the state
    is stored opaquely exactly as `extraction_status_by_tier` is. A class P1 has
    never heard of round-trips unchanged; validating it here would put one vocabulary
    in two homes, which is this project's most expensive defect.

    D2, ratified 2026-08-21: P7's `ClassificationRecord`, keyed `(file_id,
    content_hash)`, is authoritative. This column is its PROJECTION onto the current
    file row -- the same relationship P5's runs have to the tier map. A reader
    needing the classification's provenance reads P7's record; a reader needing
    "what is this file right now" reads here.

    `author` and `component_version` name the classifying part. As with
    `set_extraction_status`, P1 appends no event of its own (M8): P7 authors its
    §8.4 audit record and P1 records the state under it. P1 minting an event here
    would name the storage substrate as the thing that classified the file, which is
    exactly what §8.2's reconstruction requirement cannot survive.
    """
    conn.execute(
        "UPDATE files SET sensitivity_state = ? WHERE file_id = ?",
        (json.dumps(state, sort_keys=True), file_id),
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
    # The exact-path case is answered by an index, not by reading the family. A
    # re-scan of an unchanged corpus takes this branch for every file, so a
    # duplicate family of any size costs nothing to re-observe.
    existing = conn.execute(
        "SELECT file_id, current_path FROM files WHERE current_path = ? "
        "AND content_hash = ? AND scan_state != ? ORDER BY rowid LIMIT 1",
        (observed, content_hash, SUPERSEDED_CONTENT),
    ).fetchone()
    observed_stat: os.stat_result | None = None
    if existing is None:
        # The family is no longer read at all. Both questions left -- is one of these
        # rows this very inode, and has the oldest recorded home of these bytes gone
        # -- are answered without materialising a single duplicate.
        observed_stat = _lstat_or_none(observed)
        if observed_stat is not None:
            existing = _row_for_this_inode(conn, content_hash, observed,
                                           observed_stat)
        if existing is None:
            existing = _relocated_row(conn, content_hash, observed, observed_stat)

    if existing is not None:
        if existing["current_path"] != observed:
            append_event(
                conn, event_type="stat observation", file_id=existing["file_id"],
                content_hash=content_hash, old_path=existing["current_path"],
                new_path=observed, subsystem=author,
                component_version=component_version, observed_at=now,
                explanation="same content observed at a new path (R2)",
            )
            # The inode moves with the path: a row whose remembered inode belongs
            # to the path it no longer has is a row the index would answer with.
            if observed_stat is not None:
                conn.execute(
                    "UPDATE files SET current_path = ?, st_dev = ?, st_ino = ? "
                    "WHERE file_id = ?",
                    (observed, observed_stat.st_dev, observed_stat.st_ino,
                     existing["file_id"]),
                )
            else:
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
