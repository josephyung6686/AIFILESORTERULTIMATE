"""Incremental, restart-safe index refresh queue.

The filesystem is source of truth; SQLite is derived. This module owns:

- a durable refresh queue keyed by ``(item_id, content_hash)``
- ``index_state``: ``starting`` | ``catching_up`` | ``ready`` | ``degraded``
- per-root durable event cursors / scan watermarks so a restart cannot skip work
- incremental FTS upserts (no full ``rebuild_fts`` on every idle tick)

Failures leave the item ``error`` / retryable with a recorded message — never
silently treat stale indexed bytes as ``fresh``.
"""
from __future__ import annotations

import sqlite3
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from items.freshness import (
    DIRTY,
    ERROR,
    FRESH,
    INDEXING,
    MISSING,
    mark_error,
    mark_indexed,
    mark_indexing,
)

STARTING = "starting"
CATCHING_UP = "catching_up"
READY = "ready"
DEGRADED = "degraded"

INDEX_STATES = frozenset({STARTING, CATCHING_UP, READY, DEGRADED})

QUEUE_PENDING = "pending"
QUEUE_PROCESSING = "processing"
QUEUE_FAILED = "failed"

DEFAULT_PROCESS_LIMIT = 64
DEFAULT_RECONCILE_BUDGET = 500
BODY_FILE_CHARS = 4000
_TEXT_SUFFIXES = frozenset({
    ".txt", ".md", ".markdown", ".rst", ".csv", ".tsv", ".json", ".yaml",
    ".yml", ".py", ".js", ".ts", ".html", ".htm", ".css", ".xml", ".log",
})

_LOCK = threading.RLock()

REFRESH_DDL = """
CREATE TABLE IF NOT EXISTS index_refresh_queue (
    item_id      TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    enqueued_at  TEXT NOT NULL,
    attempts     INTEGER NOT NULL DEFAULT 0,
    last_error   TEXT,
    status       TEXT NOT NULL DEFAULT 'pending',
    PRIMARY KEY (item_id, content_hash)
);
CREATE INDEX IF NOT EXISTS index_refresh_queue_status
    ON index_refresh_queue(status, enqueued_at);

CREATE TABLE IF NOT EXISTS index_watch_cursors (
    root_key          TEXT PRIMARY KEY,
    last_cursor       INTEGER NOT NULL DEFAULT 0,
    scan_generation   INTEGER NOT NULL DEFAULT 0,
    last_reconcile_at TEXT
);

CREATE TABLE IF NOT EXISTS index_runtime (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class IndexStatus:
    state: str
    pending: int
    dirty: int
    error: int
    indexing: int
    missing: int
    fresh: int
    cursor_roots: int

    def as_dict(self) -> dict:
        return {
            "index_state": self.state,
            "pending": self.pending,
            "dirty": self.dirty,
            "error": self.error,
            "indexing": self.indexing,
            "missing": self.missing,
            "fresh": self.fresh,
            "cursor_roots": self.cursor_roots,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_refresh_schema(conn: sqlite3.Connection) -> None:
    from items.hot_index import ensure_fts

    conn.executescript(REFRESH_DDL)
    ensure_fts(conn)
    row = conn.execute(
        "SELECT value FROM index_runtime WHERE key = 'state'"
    ).fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO index_runtime (key, value) VALUES ('state', ?)",
            (STARTING,),
        )


def get_index_state(conn: sqlite3.Connection) -> str:
    ensure_refresh_schema(conn)
    row = conn.execute(
        "SELECT value FROM index_runtime WHERE key = 'state'"
    ).fetchone()
    if row is None:
        return STARTING
    return row[0] if not hasattr(row, "keys") else row["value"]


def set_index_state(conn: sqlite3.Connection, state: str) -> str:
    if state not in INDEX_STATES:
        raise ValueError(f"unknown index_state: {state!r}")
    ensure_refresh_schema(conn)
    conn.execute(
        "INSERT INTO index_runtime (key, value) VALUES ('state', ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (state,),
    )
    return state


def _count_freshness(conn: sqlite3.Connection, state: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM items WHERE freshness_state = ? "
        "AND superseded_by IS NULL",
        (state,),
    ).fetchone()
    return int(row[0] if not hasattr(row, "keys") else row["n"])


def index_status(conn: sqlite3.Connection) -> IndexStatus:
    ensure_refresh_schema(conn)
    pending = conn.execute(
        "SELECT COUNT(*) FROM index_refresh_queue "
        "WHERE status IN (?, ?)",
        (QUEUE_PENDING, QUEUE_PROCESSING),
    ).fetchone()[0]
    failed = conn.execute(
        "SELECT COUNT(*) FROM index_refresh_queue WHERE status = ?",
        (QUEUE_FAILED,),
    ).fetchone()[0]
    cursors = conn.execute(
        "SELECT COUNT(*) FROM index_watch_cursors"
    ).fetchone()[0]
    dirty = _count_freshness(conn, DIRTY)
    error = _count_freshness(conn, ERROR)
    indexing = _count_freshness(conn, INDEXING)
    missing = _count_freshness(conn, MISSING)
    fresh = _count_freshness(conn, FRESH)
    state = get_index_state(conn)
    # Counts can force degraded even if runtime says ready.
    if state == READY and (pending or failed or dirty or error or indexing):
        state = CATCHING_UP if (pending or dirty or indexing) else DEGRADED
    return IndexStatus(
        state=state,
        pending=int(pending),
        dirty=int(dirty),
        error=int(error) + int(failed),
        indexing=int(indexing),
        missing=int(missing),
        fresh=int(fresh),
        cursor_roots=int(cursors),
    )


def get_watch_cursor(conn: sqlite3.Connection, root: Path | str) -> int:
    ensure_refresh_schema(conn)
    key = _root_key(root)
    row = conn.execute(
        "SELECT last_cursor FROM index_watch_cursors WHERE root_key = ?",
        (key,),
    ).fetchone()
    return 0 if row is None else int(row[0])


def advance_watch_cursor(
        conn: sqlite3.Connection,
        root: Path | str,
        cursor: int,
        *,
        reconciled: bool = False,
) -> int:
    """Advance durable watermark; never moves backward."""
    ensure_refresh_schema(conn)
    key = _root_key(root)
    prior = get_watch_cursor(conn, root)
    nxt = max(prior, int(cursor))
    now = _now() if reconciled else None
    row = conn.execute(
        "SELECT scan_generation, last_reconcile_at FROM index_watch_cursors "
        "WHERE root_key = ?",
        (key,),
    ).fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO index_watch_cursors ("
            "root_key, last_cursor, scan_generation, last_reconcile_at"
            ") VALUES (?, ?, 1, ?)",
            (key, nxt, now if reconciled else _now()),
        )
        return nxt
    gen = int(row[0] if not hasattr(row, "keys") else row["scan_generation"])
    reconcile_at = (
        now if reconciled
        else (row[1] if not hasattr(row, "keys") else row["last_reconcile_at"])
    )
    if reconciled:
        gen += 1
    conn.execute(
        "UPDATE index_watch_cursors SET last_cursor = ?, "
        "scan_generation = ?, last_reconcile_at = ? WHERE root_key = ?",
        (nxt, gen, reconcile_at, key),
    )
    return nxt


def _root_key(root: Path | str) -> str:
    try:
        return str(Path(root).resolve())
    except Exception:
        return str(root)


def enqueue(
        conn: sqlite3.Connection,
        item_id: str,
        content_hash: str | None,
        *,
        reason: str | None = None,
) -> bool:
    """Enqueue one (item_id, content_hash). Returns True if newly inserted."""
    ensure_refresh_schema(conn)
    if not item_id:
        return False
    digest = content_hash or ""
    now = _now()
    with _LOCK:
        cur = conn.execute(
            "INSERT INTO index_refresh_queue ("
            "item_id, content_hash, enqueued_at, attempts, last_error, status"
            ") VALUES (?, ?, ?, 0, NULL, ?) "
            "ON CONFLICT(item_id, content_hash) DO UPDATE SET "
            "status = CASE "
            "  WHEN index_refresh_queue.status = ? THEN "
            "    index_refresh_queue.status "
            "  ELSE ? END, "
            "last_error = CASE "
            "  WHEN index_refresh_queue.status = ? THEN "
            "    index_refresh_queue.last_error "
            "  ELSE NULL END, "
            "enqueued_at = CASE "
            "  WHEN index_refresh_queue.status = ? THEN "
            "    index_refresh_queue.enqueued_at "
            "  ELSE excluded.enqueued_at END",
            (
                item_id, digest, now, QUEUE_PENDING,
                QUEUE_PROCESSING, QUEUE_PENDING,
                QUEUE_PROCESSING,
                QUEUE_PROCESSING,
            ),
        )
        return cur.rowcount > 0


def _fts_path_label_stale(conn: sqlite3.Connection, item_id: str,
                          open_target: str | None,
                          display_label: str | None) -> bool:
    """True when FTS still carries a prior path/label after rename."""
    from items.hot_index import ensure_fts

    ensure_fts(conn)
    row = conn.execute(
        "SELECT path, label FROM item_fts WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    if row is None:
        return True
    fts_path = row["path"] or ""
    fts_label = row["label"] or ""
    if open_target and open_target not in fts_path:
        return True
    if display_label and display_label not in fts_label:
        return True
    return False


def enqueue_dirty(conn: sqlite3.Connection) -> int:
    """Enqueue items that need index work (hash freshness or FTS path drift)."""
    ensure_refresh_schema(conn)
    rows = conn.execute(
        "SELECT item_id, content_hash, last_indexed_hash, freshness_state, "
        "open_target, display_label, presence "
        "FROM items WHERE superseded_by IS NULL AND item_type = 'file'"
    ).fetchall()
    n = 0
    for row in rows:
        state = row["freshness_state"]
        digest = row["content_hash"]
        indexed = row["last_indexed_hash"]
        if state == MISSING or row["presence"] != "live":
            # Still enqueue so FTS row can be removed.
            if enqueue(conn, row["item_id"], digest or "", reason="missing"):
                n += 1
            continue
        needs = (
            state in (DIRTY, ERROR, INDEXING)
            or indexed != digest
            or digest is None
            or _fts_path_label_stale(
                conn, row["item_id"], row["open_target"], row["display_label"],
            )
        )
        if needs:
            if enqueue(conn, row["item_id"], digest or "", reason=state or "drift"):
                n += 1
    return n


def _read_file_body(path: str | None, *, limit: int = BODY_FILE_CHARS) -> str:
    if not path:
        return ""
    p = Path(path)
    if not p.is_file():
        return ""
    if p.suffix.lower() not in _TEXT_SUFFIXES and p.suffix != "":
        # Allow extensionless small text; skip obvious binaries by suffix.
        if p.suffix.lower() not in {"", ".txt"}:
            return ""
    try:
        data = p.read_bytes()[:limit]
    except OSError:
        return ""
    if b"\x00" in data:
        return ""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return data.decode("utf-8", errors="replace")
        except Exception:
            return ""


def _body_for_item(conn: sqlite3.Connection, row, *, evidence_chars: int) -> str:
    from items.hot_index import _evidence_snippet

    body = ""
    if row["file_id"]:
        body = _evidence_snippet(conn, row["file_id"], evidence_chars)
    if not body:
        body = _read_file_body(row["open_target"], limit=evidence_chars)
    return body


def delete_item_from_index(conn: sqlite3.Connection, item_id: str) -> None:
    from items.hot_index import ensure_fts

    ensure_fts(conn)
    conn.execute("DELETE FROM item_fts WHERE item_id = ?", (item_id,))
    conn.execute("DELETE FROM item_chunks WHERE item_id = ?", (item_id,))


def upsert_item_index(
        conn: sqlite3.Connection,
        item_id: str,
        *,
        evidence_chars: int = BODY_FILE_CHARS,
) -> str:
    """Index one item incrementally. Returns new freshness state."""
    from items.hot_index import _chunk_text, cjk_bigrams, ensure_fts

    ensure_fts(conn)
    row = conn.execute(
        "SELECT item_id, display_label, open_target, file_id, content_hash, "
        "presence, freshness_state FROM items WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    if row is None:
        delete_item_from_index(conn, item_id)
        return MISSING

    if row["presence"] != "live" or row["freshness_state"] == MISSING:
        delete_item_from_index(conn, item_id)
        return MISSING

    mark_indexing(conn, item_id)
    delete_item_from_index(conn, item_id)

    body = _body_for_item(conn, row, evidence_chars=evidence_chars)
    label = row["display_label"] or ""
    path = row["open_target"] or ""
    cjk_extra = cjk_bigrams(f"{label} {path} {body}")
    indexed_body = body
    if cjk_extra:
        indexed_body = f"{body}\n{cjk_extra}".strip()
    conn.execute(
        "INSERT INTO item_fts (item_id, label, path, body) VALUES (?,?,?,?)",
        (
            item_id,
            f"{label} {cjk_bigrams(label)}".strip(),
            f"{path} {cjk_bigrams(path)}".strip(),
            indexed_body,
        ),
    )
    for ordinal, (start, end, piece) in enumerate(_chunk_text(body or label)):
        chunk_id = f"{item_id}:{ordinal}"
        conn.execute(
            "INSERT INTO item_chunks ("
            "chunk_id, item_id, ordinal, text, char_start, char_end) "
            "VALUES (?,?,?,?,?,?)",
            (chunk_id, item_id, ordinal, piece, start, end),
        )

    digest = row["content_hash"]
    if not digest:
        # Re-hash from disk when missing so we never mark fresh with NULL.
        from database_agent.identity import hash_file
        if path and Path(path).is_file():
            digest = hash_file(Path(path), materialized=True)
            conn.execute(
                "UPDATE items SET content_hash = ? WHERE item_id = ?",
                (digest, item_id),
            )
        else:
            mark_error(conn, item_id, reason="index_error",
                       details="missing content_hash")
            return ERROR
    return mark_indexed(conn, item_id, digest, reason="indexed")


def process_queue(
        conn: sqlite3.Connection,
        *,
        limit: int = DEFAULT_PROCESS_LIMIT,
) -> int:
    """Process pending queue rows. Returns number successfully indexed."""
    ensure_refresh_schema(conn)
    with _LOCK:
        rows = conn.execute(
            "SELECT item_id, content_hash FROM index_refresh_queue "
            "WHERE status IN (?, ?) ORDER BY enqueued_at LIMIT ?",
            (QUEUE_PENDING, QUEUE_FAILED, limit),
        ).fetchall()
        done = 0
        for row in rows:
            item_id = row["item_id"]
            content_hash = row["content_hash"]
            conn.execute(
                "UPDATE index_refresh_queue SET status = ?, attempts = attempts + 1 "
                "WHERE item_id = ? AND content_hash = ?",
                (QUEUE_PROCESSING, item_id, content_hash),
            )
            try:
                # Skip stale queue rows when item moved to a newer hash.
                live = conn.execute(
                    "SELECT content_hash, freshness_state, presence "
                    "FROM items WHERE item_id = ?",
                    (item_id,),
                ).fetchone()
                if live is None:
                    delete_item_from_index(conn, item_id)
                    conn.execute(
                        "DELETE FROM index_refresh_queue "
                        "WHERE item_id = ? AND content_hash = ?",
                        (item_id, content_hash),
                    )
                    done += 1
                    continue
                current = live["content_hash"] or ""
                if content_hash and current and content_hash != current:
                    # Superseded by a newer enqueue; drop this row.
                    conn.execute(
                        "DELETE FROM index_refresh_queue "
                        "WHERE item_id = ? AND content_hash = ?",
                        (item_id, content_hash),
                    )
                    continue
                state = upsert_item_index(conn, item_id)
                if state == ERROR:
                    conn.execute(
                        "UPDATE index_refresh_queue SET status = ?, "
                        "last_error = COALESCE(last_error, 'index_error') "
                        "WHERE item_id = ? AND content_hash = ?",
                        (QUEUE_FAILED, item_id, content_hash),
                    )
                else:
                    conn.execute(
                        "DELETE FROM index_refresh_queue "
                        "WHERE item_id = ? AND content_hash = ?",
                        (item_id, content_hash),
                    )
                    done += 1
            except Exception as exc:  # noqa: BLE001 — must not leave silent stale
                details = f"{type(exc).__name__}: {exc}"
                try:
                    mark_error(conn, item_id, reason="index_error",
                               details=details)
                except Exception:
                    pass
                conn.execute(
                    "UPDATE index_refresh_queue SET status = ?, last_error = ? "
                    "WHERE item_id = ? AND content_hash = ?",
                    (QUEUE_FAILED, details, item_id, content_hash),
                )
        _recompute_runtime_state(conn)
        return done


def _recompute_runtime_state(conn: sqlite3.Connection) -> str:
    pending = conn.execute(
        "SELECT COUNT(*) FROM index_refresh_queue "
        "WHERE status IN (?, ?, ?)",
        (QUEUE_PENDING, QUEUE_PROCESSING, QUEUE_FAILED),
    ).fetchone()[0]
    dirty = _count_freshness(conn, DIRTY)
    error = _count_freshness(conn, ERROR)
    indexing = _count_freshness(conn, INDEXING)
    prior = get_index_state(conn)
    if prior == STARTING and (pending or dirty or indexing):
        return set_index_state(conn, CATCHING_UP)
    if pending or dirty or indexing:
        return set_index_state(conn, CATCHING_UP)
    if error:
        return set_index_state(conn, DEGRADED)
    return set_index_state(conn, READY)


def catch_up(
        conn: sqlite3.Connection,
        *,
        limit: int = DEFAULT_PROCESS_LIMIT,
        max_passes: int = 8,
) -> IndexStatus:
    """Enqueue dirty items and drain until ready, degraded, or budget exhausted."""
    ensure_refresh_schema(conn)
    set_index_state(conn, CATCHING_UP)
    enqueue_dirty(conn)
    for _ in range(max_passes):
        n = process_queue(conn, limit=limit)
        status = index_status(conn)
        if status.pending == 0 and status.dirty == 0 and status.indexing == 0:
            break
        if n == 0:
            break
    status = index_status(conn)
    if status.pending == 0 and status.dirty == 0 and status.indexing == 0:
        if status.error:
            set_index_state(conn, DEGRADED)
        else:
            set_index_state(conn, READY)
    else:
        set_index_state(conn, CATCHING_UP)
    return index_status(conn)


def startup_reconcile(
        conn: sqlite3.Connection,
        roots: list[Path] | list[str],
        *,
        budget: int = DEFAULT_RECONCILE_BUDGET,
) -> IndexStatus:
    """Bounded reconcile of roots, then catch-up, before declaring ready."""
    from items.identity import reconcile_tree

    ensure_refresh_schema(conn)
    set_index_state(conn, STARTING)
    cursor_base = int(time.time() * 1000)
    for i, root in enumerate(roots):
        path = Path(root)
        if not path.is_dir():
            continue
        # Prefer durable watermark: always reconcile on startup so offline edits
        # cannot be skipped even when the in-memory event queue is empty.
        prior = get_watch_cursor(conn, path)
        reconcile_tree(conn, path)
        advance_watch_cursor(
            conn, path, max(prior, cursor_base + i), reconciled=True,
        )
    # Bound catch-up work.
    return catch_up(conn, limit=min(budget, DEFAULT_PROCESS_LIMIT), max_passes=16)


def ensure_search_ready(
        conn: sqlite3.Connection,
        *,
        limit: int = DEFAULT_PROCESS_LIMIT,
) -> IndexStatus:
    """Make search reflect disk before the next query returns."""
    from items.hot_index import ensure_fts

    ensure_refresh_schema(conn)
    # Bootstrap: empty FTS with live items → enqueue + process (not silent stale).
    ensure_fts(conn)
    fts_n = conn.execute("SELECT COUNT(*) FROM item_fts").fetchone()[0]
    live_n = conn.execute(
        "SELECT COUNT(*) FROM items WHERE presence = 'live' "
        "AND superseded_by IS NULL AND item_type = 'file'"
    ).fetchone()[0]
    if fts_n == 0 and live_n > 0:
        enqueue_dirty(conn)
    return catch_up(conn, limit=limit)


def note_event_cursor(
        conn: sqlite3.Connection,
        root: Path | str,
        seq: int | None,
) -> int:
    """Persist the highest observed event sequence for a root."""
    if seq is None:
        return get_watch_cursor(conn, root)
    return advance_watch_cursor(conn, root, int(seq))
