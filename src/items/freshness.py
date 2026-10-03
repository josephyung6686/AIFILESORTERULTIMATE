"""Durable item freshness: disk identity vs indexed evidence.

Freshness is derived working memory. The filesystem remains source of truth;
SQLite records what we last saw and whether the index matches that observation.

States:
  fresh       — last_indexed_hash matches current content_hash
  dirty       — disk content changed (or never indexed) relative to the index
  missing     — path is absent on disk
  conflicted  — identity cannot be reconciled safely (replacement race, etc.)
  indexing    — a refresh is in progress for this item
  error       — last refresh failed; still retryable / not silently fresh
"""
from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from database_agent.identity import hash_file
from items.file_identity import read_file_identity

FRESH = "fresh"
DIRTY = "dirty"
MISSING = "missing"
CONFLICTED = "conflicted"
INDEXING = "indexing"
ERROR = "error"

FRESHNESS_STATES = frozenset({
    FRESH, DIRTY, MISSING, CONFLICTED, INDEXING, ERROR,
})


@dataclass(frozen=True)
class DiskIdentity:
    path: str
    size: int
    mtime_ns: int
    st_dev: int
    st_ino: int
    content_hash: str | None = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def observe_disk(
        path: Path,
        *,
        content_hash: str | None = None,
        hash_bytes: bool = False,
) -> DiskIdentity | None:
    """Read durable identity fields from disk. None if the path is absent."""
    meta = read_file_identity(path)
    if meta is None:
        return None
    digest = content_hash
    if digest is None and hash_bytes:
        digest = hash_file(path, materialized=True)
    return DiskIdentity(
        path=str(path),
        size=meta.size,
        mtime_ns=meta.mtime_ns,
        st_dev=meta.st_dev,
        st_ino=meta.st_ino,
        content_hash=digest,
    )


def current_state(conn: sqlite3.Connection, item_id: str) -> str | None:
    row = conn.execute(
        "SELECT freshness_state FROM items WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    if row is None:
        return None
    return row["freshness_state"] if "freshness_state" in row.keys() else None


def record_identity_event(
        conn: sqlite3.Connection,
        item_id: str,
        *,
        from_state: str | None,
        to_state: str,
        reason: str,
        path: str | None = None,
        content_hash: str | None = None,
        st_dev: int | None = None,
        st_ino: int | None = None,
        details: str | None = None,
        observed_at: str | None = None,
) -> str:
    """Append one identity event. Never updates or deletes prior rows."""
    event_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO item_identity_events ("
        "event_id, item_id, from_state, to_state, reason, path, "
        "content_hash, st_dev, st_ino, details, observed_at"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            event_id, item_id, from_state, to_state, reason, path,
            content_hash, st_dev, st_ino, details, observed_at or _now(),
        ),
    )
    return event_id


def transition(
        conn: sqlite3.Connection,
        item_id: str,
        to_state: str,
        *,
        reason: str,
        path: str | None = None,
        content_hash: str | None = None,
        st_dev: int | None = None,
        st_ino: int | None = None,
        details: str | None = None,
        force_event: bool = False,
) -> str:
    """Set freshness_state and append an event when the state changes."""
    if to_state not in FRESHNESS_STATES:
        raise ValueError(f"unknown freshness_state: {to_state!r}")
    prior = current_state(conn, item_id)
    if prior != to_state or force_event:
        record_identity_event(
            conn, item_id,
            from_state=prior, to_state=to_state, reason=reason,
            path=path, content_hash=content_hash,
            st_dev=st_dev, st_ino=st_ino, details=details,
        )
    conn.execute(
        "UPDATE items SET freshness_state = ? WHERE item_id = ?",
        (to_state, item_id),
    )
    return to_state


def write_identity_fields(
        conn: sqlite3.Connection,
        item_id: str,
        disk: DiskIdentity,
        *,
        content_hash: str | None = None,
        last_seen_at: str | None = None,
) -> None:
    digest = content_hash if content_hash is not None else disk.content_hash
    conn.execute(
        "UPDATE items SET "
        "content_hash = ?, size = ?, mtime_ns = ?, st_dev = ?, st_ino = ?, "
        "last_seen_at = ? WHERE item_id = ?",
        (
            digest, disk.size, disk.mtime_ns, disk.st_dev, disk.st_ino,
            last_seen_at or _now(), item_id,
        ),
    )


def mark_indexed(
        conn: sqlite3.Connection,
        item_id: str,
        content_hash: str,
        *,
        reason: str = "indexed",
) -> str:
    """Record that the index matches this content version."""
    conn.execute(
        "UPDATE items SET last_indexed_hash = ?, content_hash = ? "
        "WHERE item_id = ?",
        (content_hash, content_hash, item_id),
    )
    row = conn.execute(
        "SELECT open_target, st_dev, st_ino FROM items WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    return transition(
        conn, item_id, FRESH, reason=reason,
        path=None if row is None else row["open_target"],
        content_hash=content_hash,
        st_dev=None if row is None else row["st_dev"],
        st_ino=None if row is None else row["st_ino"],
    )


def mark_indexing(conn: sqlite3.Connection, item_id: str) -> str:
    row = conn.execute(
        "SELECT open_target, content_hash, st_dev, st_ino FROM items "
        "WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    return transition(
        conn, item_id, INDEXING, reason="indexing_started",
        path=None if row is None else row["open_target"],
        content_hash=None if row is None else row["content_hash"],
        st_dev=None if row is None else row["st_dev"],
        st_ino=None if row is None else row["st_ino"],
    )


def mark_error(
        conn: sqlite3.Connection,
        item_id: str,
        *,
        reason: str = "index_error",
        details: str | None = None,
) -> str:
    row = conn.execute(
        "SELECT open_target, content_hash, st_dev, st_ino FROM items "
        "WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    return transition(
        conn, item_id, ERROR, reason=reason, details=details,
        path=None if row is None else row["open_target"],
        content_hash=None if row is None else row["content_hash"],
        st_dev=None if row is None else row["st_dev"],
        st_ino=None if row is None else row["st_ino"],
    )


def mark_missing(
        conn: sqlite3.Connection,
        item_id: str,
        *,
        reason: str = "path_absent",
        path: str | None = None,
) -> str:
    row = conn.execute(
        "SELECT open_target, content_hash, st_dev, st_ino, presence "
        "FROM items WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    target = path if path is not None else (
        None if row is None else row["open_target"]
    )
    conn.execute(
        "UPDATE items SET presence = 'missing', last_seen_at = ? "
        "WHERE item_id = ?",
        (_now(), item_id),
    )
    return transition(
        conn, item_id, MISSING, reason=reason, path=target,
        content_hash=None if row is None else row["content_hash"],
        st_dev=None if row is None else row["st_dev"],
        st_ino=None if row is None else row["st_ino"],
    )


def mark_conflicted(
        conn: sqlite3.Connection,
        item_id: str,
        *,
        reason: str = "identity_conflict",
        disk: DiskIdentity | None = None,
        details: str | None = None,
) -> str:
    if disk is not None:
        write_identity_fields(conn, item_id, disk)
    row = conn.execute(
        "SELECT open_target, content_hash, st_dev, st_ino FROM items "
        "WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    return transition(
        conn, item_id, CONFLICTED, reason=reason, details=details,
        path=disk.path if disk is not None else (
            None if row is None else row["open_target"]
        ),
        content_hash=(
            disk.content_hash if disk is not None and disk.content_hash
            else (None if row is None else row["content_hash"])
        ),
        st_dev=disk.st_dev if disk is not None else (
            None if row is None else row["st_dev"]
        ),
        st_ino=disk.st_ino if disk is not None else (
            None if row is None else row["st_ino"]
        ),
    )


def _same_inode(row, disk: DiskIdentity) -> bool:
    if row["st_dev"] is None or row["st_ino"] is None:
        return False
    return int(row["st_dev"]) == disk.st_dev and int(row["st_ino"]) == disk.st_ino


def reconcile_live_identity(
        conn: sqlite3.Connection,
        item_id: str,
        disk: DiskIdentity,
        *,
        content_hash: str,
        reason_prefix: str = "reconcile",
) -> str:
    """Compare inode first, then hash/metadata; update fields and freshness.

    A path match with a changed hash becomes dirty — never silently fresh against
    old evidence. Same inode + same hash stays fresh only when last_indexed_hash
    already matches.
    """
    row = conn.execute(
        "SELECT content_hash, size, mtime_ns, st_dev, st_ino, "
        "last_indexed_hash, freshness_state, open_target, presence "
        "FROM items WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    if row is None:
        raise KeyError(item_id)

    prior_hash = row["content_hash"]
    prior_indexed = row["last_indexed_hash"]
    inode_match = _same_inode(row, disk)
    hash_match = prior_hash is not None and prior_hash == content_hash

    write_identity_fields(conn, item_id, disk, content_hash=content_hash)
    conn.execute(
        "UPDATE items SET presence = 'live' WHERE item_id = ?",
        (item_id,),
    )

    if not inode_match and prior_hash is not None and not hash_match:
        # Different inode and different bytes at the path we track: replacement.
        # Mark dirty (index must catch up). If we still believe another live
        # identity for these bytes elsewhere, callers may escalate to conflicted.
        return transition(
            conn, item_id, DIRTY,
            reason=f"{reason_prefix}:replacement",
            path=disk.path, content_hash=content_hash,
            st_dev=disk.st_dev, st_ino=disk.st_ino,
            details=(
                f"inode {row['st_dev']}:{row['st_ino']} -> "
                f"{disk.st_dev}:{disk.st_ino}; hash changed"
            ),
            force_event=True,
        )

    if inode_match and not hash_match:
        return transition(
            conn, item_id, DIRTY,
            reason=f"{reason_prefix}:content_edit",
            path=disk.path, content_hash=content_hash,
            st_dev=disk.st_dev, st_ino=disk.st_ino,
            force_event=True,
        )

    if not inode_match and hash_match:
        # Same bytes, new inode (copy-replace) or first durable inode write.
        if prior_indexed == content_hash:
            return transition(
                conn, item_id, FRESH,
                reason=f"{reason_prefix}:inode_refresh",
                path=disk.path, content_hash=content_hash,
                st_dev=disk.st_dev, st_ino=disk.st_ino,
            )
        return transition(
            conn, item_id, DIRTY,
            reason=f"{reason_prefix}:inode_change",
            path=disk.path, content_hash=content_hash,
            st_dev=disk.st_dev, st_ino=disk.st_ino,
        )

    # Same inode (or first observation) and same hash.
    if prior_indexed == content_hash:
        return transition(
            conn, item_id, FRESH,
            reason=f"{reason_prefix}:unchanged",
            path=disk.path, content_hash=content_hash,
            st_dev=disk.st_dev, st_ino=disk.st_ino,
        )
    return transition(
        conn, item_id, DIRTY,
        reason=f"{reason_prefix}:awaiting_index",
        path=disk.path, content_hash=content_hash,
        st_dev=disk.st_dev, st_ino=disk.st_ino,
    )


def seed_new_item_identity(
        conn: sqlite3.Connection,
        item_id: str,
        disk: DiskIdentity,
        *,
        content_hash: str,
) -> str:
    """First observation of a new item: durable fields + dirty until indexed."""
    write_identity_fields(conn, item_id, disk, content_hash=content_hash)
    conn.execute(
        "UPDATE items SET last_indexed_hash = NULL, presence = 'live' "
        "WHERE item_id = ?",
        (item_id,),
    )
    return transition(
        conn, item_id, DIRTY,
        reason="created",
        path=disk.path, content_hash=content_hash,
        st_dev=disk.st_dev, st_ino=disk.st_ino,
        force_event=True,
    )


def identity_events(
        conn: sqlite3.Connection,
        item_id: str,
) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM item_identity_events WHERE item_id = ? "
        "ORDER BY rowid",
        (item_id,),
    ).fetchall()
