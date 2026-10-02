"""Point a durable item at the file index.

Reused, unchanged:

- `files`, `content_hash`, and `observe_path` (through `record_basic_record`)
  for a rename or move of the same bytes, for an edit that supersedes a
  `file_id`, and for two live copies remaining two file rows. Inode confirmation
  stays inside `observe_path`.
- `reconcile_disappearances`, which calls `set_path_no_longer_exists` and
  deletes nothing.
- `traversal.walk` over `FilesystemCorpusSource`, after `require_access`.
- `SessionWatch` is still only a detection. It does not rewrite `files`.

Added here:

- `item_id`, which stays put when an edit mints a new `file_id`, with the old
  and new ids on `item_versions`.
- `presence = missing` when that disappearance pass retires the path.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePath

from database_agent.files_table import (
    PATH_NO_LONGER_EXISTS, SUPERSEDED_CONTENT, get_file,
)
from grouping.vocabulary import P1_INCLUDED_SCAN_STATE
from items.schema import create_items_schema
from scan_agent.access import require_access
from scan_agent.basic_record import record_basic_record
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.disappearance import _is_absent, reconcile_disappearances
from scan_agent.exclusion import APPLIES_TO_SCANNED_SOURCE
from scan_agent.traversal import ObservedFile, walk

ITEM_TYPE_FILE = "file"
PRESENCE_LIVE = "live"
PRESENCE_MISSING = "missing"
TYPING_UNPLACED = "unplaced"


def reconcile_tree(conn: sqlite3.Connection, root: Path) -> None:
    """Walk `root`, resolve each file through `observe_path`, and refresh items.

    This is the pass a session watch schedules after `poll`. The watch records
    that a path appeared or disappeared; this pass is what re-finds the bytes.
    """
    create_items_schema(conn)
    root = Path(root)
    require_access([root])
    for item in walk(
            FilesystemCorpusSource(), sources=[root], candidate_roots=[],
            budget_exhausted=lambda: False):
        if not isinstance(item, ObservedFile):
            continue
        if item.applies_to != APPLIES_TO_SCANNED_SOURCE or item.dataless:
            continue
        file_id = record_basic_record(
            conn, item, mime_type_for=lambda _path: None,
            scan_state=P1_INCLUDED_SCAN_STATE)
        _attach_live_file(conn, file_id)
    reconcile_disappearances(
        conn, str(uuid.uuid4()), sources=[root],
        scan_state=P1_INCLUDED_SCAN_STATE)
    _mark_missing_under(conn, [root])


def project_after_scan(conn: sqlite3.Connection, sources, scan_state: str) -> None:
    """Point items at file rows a scan has already resolved.

    The live scan has already called `observe_path` and
    `reconcile_disappearances`. This does not hash and does not walk. When the
    item tables are absent, it returns; `_bootstrap` is what installs them, and
    a scan that never bootstrapped keeps today's behaviour.
    """
    if not _items_installed(conn):
        return
    roots = [Path(source) for source in sources]
    rows = conn.execute(
        "SELECT file_id, current_path FROM files WHERE scan_state = ?",
        (scan_state,),
    ).fetchall()
    for row in rows:
        if _under_any(row["current_path"], roots):
            _attach_live_file(conn, row["file_id"])
    # `observe_path` re-finds a retired row and does not clear
    # `path_no_longer_exists`. The bytes are back; the item is live. The
    # corpus flag stays retired, which is the sorter's rule.
    retired = conn.execute(
        "SELECT file_id, current_path FROM files WHERE scan_state = ?",
        (PATH_NO_LONGER_EXISTS,),
    ).fetchall()
    for row in retired:
        path = row["current_path"]
        if _under_any(path, roots) and not _is_absent(path):
            _attach_live_file(conn, row["file_id"])
    _mark_missing_under(conn, roots)


def _items_installed(conn: sqlite3.Connection) -> bool:
    found = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'items'"
    ).fetchone()
    return found is not None


def _attach_live_file(conn: sqlite3.Connection, file_id: str) -> None:
    row = get_file(conn, file_id)
    path = row["current_path"]
    content_hash = row["content_hash"]
    now = datetime.now(timezone.utc).isoformat()
    label = Path(path).name
    existing = conn.execute(
        "SELECT item_id FROM items WHERE file_id = ? AND item_type = ?",
        (file_id, ITEM_TYPE_FILE),
    ).fetchone()
    if existing is not None:
        _point(conn, existing["item_id"], file_id, path, label)
        _ensure_version(conn, existing["item_id"], file_id, content_hash, now)
        return

    # An edit supersedes the file_id and leaves the path in place. The item
    # still points at that superseded id; the new id joins the same item.
    prior = conn.execute(
        "SELECT i.item_id FROM items i "
        "JOIN files f ON f.file_id = i.file_id "
        "WHERE i.item_type = ? AND i.open_target = ? AND f.scan_state = ? "
        "AND i.superseded_by IS NULL "
        "ORDER BY i.created_at LIMIT 1",
        (ITEM_TYPE_FILE, path, SUPERSEDED_CONTENT),
    ).fetchone()
    if prior is not None:
        _point(conn, prior["item_id"], file_id, path, label)
        _ensure_version(conn, prior["item_id"], file_id, content_hash, now)
        return

    item_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, external_key, "
        "presence, typing_state, type_schema, profile_id, created_at, superseded_by"
        ") VALUES (?, ?, ?, ?, ?, NULL, ?, ?, NULL, NULL, ?, NULL)",
        (item_id, ITEM_TYPE_FILE, label, file_id, path,
         PRESENCE_LIVE, TYPING_UNPLACED, now),
    )
    _ensure_version(conn, item_id, file_id, content_hash, now)


def _point(conn: sqlite3.Connection, item_id: str, file_id: str,
           path: str, label: str) -> None:
    conn.execute(
        "UPDATE items SET file_id = ?, open_target = ?, display_label = ?, "
        "presence = ? WHERE item_id = ?",
        (file_id, path, label, PRESENCE_LIVE, item_id),
    )


def _ensure_version(conn: sqlite3.Connection, item_id: str, file_id: str,
                    content_hash: str, now: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO item_versions "
        "(item_id, file_id, content_hash, became_live_at) VALUES (?, ?, ?, ?)",
        (item_id, file_id, content_hash, now),
    )


def _mark_missing_under(conn: sqlite3.Connection, roots) -> None:
    rows = conn.execute(
        "SELECT i.item_id, i.open_target FROM items i "
        "JOIN files f ON f.file_id = i.file_id "
        "WHERE i.item_type = ? AND i.presence = ? AND f.scan_state = ?",
        (ITEM_TYPE_FILE, PRESENCE_LIVE, PATH_NO_LONGER_EXISTS),
    ).fetchall()
    for row in rows:
        target = row["open_target"]
        # `path_no_longer_exists` is not cleared when the same bytes return at
        # the same path (`observe_path` keeps that row). Absence is the
        # filesystem, using the same errors `reconcile_disappearances` uses, so
        # a file a later pass finds is live again.
        if target and _under_any(target, roots) and _is_absent(target):
            conn.execute(
                "UPDATE items SET presence = ? WHERE item_id = ?",
                (PRESENCE_MISSING, row["item_id"]),
            )


def _under_any(path: str, roots) -> bool:
    candidate = PurePath(path)
    for root in roots:
        source = PurePath(root)
        if candidate == source or source in candidate.parents:
            return True
    return False
