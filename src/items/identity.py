"""Point a durable item at the file index.

Reused, unchanged:

- `files`, `content_hash`, and `observe_path` (through `record_basic_record`)
  for a rename or move of the same bytes, for an edit that supersedes a
  `file_id`, and for two live copies remaining two file rows. Inode confirmation
  stays inside `observe_path`.
- `reconcile_disappearances`, which calls `set_path_no_longer_exists` and
  deletes nothing.
- P3's `scan` over `FilesystemCorpusSource`, so the folders it does not read
  are `exclusion_verdicts`, the sorter's record.
- `SessionWatch` is still only a detection. It does not rewrite `files`.

Added here:

- `item_id`, which stays put when an edit mints a new `file_id`, with the old
  and new ids on `item_versions`.
- `presence = missing` when that disappearance pass retires the path.
- Durable freshness fields and append-only identity events via `items.freshness`.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePath

from database_agent.files_table import (
    PATH_NO_LONGER_EXISTS, SUPERSEDED_CONTENT, get_file,
)
from grouping.vocabulary import P1_INCLUDED_SCAN_STATE
from items.freshness import (
    DIRTY,
    observe_disk,
    mark_missing,
    reconcile_live_identity,
    seed_new_item_identity,
    transition,
)
from items.schema import create_items_schema
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.disappearance import _is_absent
from scan_agent.exclusion import (
    APPLIES_TO_SCANNED_SOURCE, RULE_PROJECT_ROOT_DESCENDANT,
    RULE_PROTECTED_CONTAINER, exclusion_verdicts,
)
from scan_agent.scan import scan
from scan_agent.selection import record_selection

ITEM_TYPE_FILE = "file"
PRESENCE_LIVE = "live"
PRESENCE_MISSING = "missing"
TYPING_UNPLACED = "unplaced"


def reconcile_tree(conn: sqlite3.Connection, root: Path) -> None:
    """Scan `root` the way the sorter does, then point items at the result.

    This is the pass a session watch schedules after `poll`. The watch records
    that a path appeared or disappeared; this pass is what re-finds the bytes.
    It is the orchestrator's sequence -- R1 selection, P3 `scan`, projection --
    so the folders it does not read land in `exclusion_verdicts`, one record
    for the sorter and the assistant.
    """
    create_items_schema(conn)
    root = Path(root)
    scan(conn, _selection_for(conn, root), source=FilesystemCorpusSource(),
         mime_type_for=lambda _path: None, scan_state=P1_INCLUDED_SCAN_STATE,
         budget_exhausted=lambda: False)
    project_after_scan(conn, [root], P1_INCLUDED_SCAN_STATE)


def refresh_tree(conn: sqlite3.Connection, root: Path) -> bool:
    """Record only what changed under `root` since it was last scanned.

    P3's own walk, compared with P3's stat cache, writes nothing. When no file
    is new, changed or gone, nothing is written and this returns False. When
    some are, one scan run records those files -- plus the walk's exclusion
    verdicts, so the folders set aside stay counted -- and items follow.
    """
    from database_agent.db import batched_writes
    from scan_agent.run import finish_scan_run, start_scan_run
    # The scan's own per-item writer, so this records exactly as a scan does.
    from scan_agent.scan import SCAN_COMMIT_BATCH, _record
    from scan_agent.stat_cache import VERDICT_REUSE, cache_verdict, prior_observation
    from scan_agent.traversal import ObservedDirectory, ObservedFile, walk
    from scan_agent.disappearance import reconcile_disappearances

    create_items_schema(conn)
    root = Path(root)
    kept: list = []
    changed = False
    for item in walk(FilesystemCorpusSource(), sources=[root],
                     candidate_roots=[], budget_exhausted=lambda: False):
        if isinstance(item, ObservedDirectory):
            continue
        if isinstance(item, ObservedFile):
            prior = prior_observation(conn, item.path)
            if (prior is not None
                    and cache_verdict(item, prior).verdict == VERDICT_REUSE):
                continue
            changed = True
        kept.append(item)
    gone = any(
        _under_any(row["current_path"], [root]) and _is_absent(row["current_path"])
        for row in conn.execute("SELECT current_path FROM files WHERE scan_state = ?",
                                (P1_INCLUDED_SCAN_STATE,)))
    if not changed and not gone:
        return False
    scan_run_id = start_scan_run(conn, _selection_for(conn, root))
    with batched_writes(conn, size=SCAN_COMMIT_BATCH) as item_recorded:
        for item in kept:
            _record(conn, scan_run_id, item, mime_type_for=lambda _path: None,
                    scan_state=P1_INCLUDED_SCAN_STATE)
            item_recorded()
    reconcile_disappearances(conn, scan_run_id, sources=[root],
                             scan_state=P1_INCLUDED_SCAN_STATE)
    finish_scan_run(conn, scan_run_id)
    project_after_scan(conn, [root], P1_INCLUDED_SCAN_STATE)
    return True


def _selection_for(conn: sqlite3.Connection, root: Path) -> str:
    """The selection already recorded for exactly this folder, or a new one."""
    row = conn.execute(
        "SELECT selection_id FROM corpus_selections "
        "WHERE sources = ? AND candidate_roots = '[]' "
        "ORDER BY selected_at DESC LIMIT 1",
        (json.dumps([str(root)]),),
    ).fetchone()
    if row is not None:
        return row["selection_id"]
    return record_selection(conn, sources=[root], candidate_roots=[],
                            cross_folder_moves=False, selected_by=None)


def excluded_areas(conn: sqlite3.Connection) -> list[dict]:
    """Folders the latest scan of each selection did not read, with the rule.

    Read from `exclusion_verdicts`, newest completed run per selected source
    set. A project-root verdict names a child of the project, so the project
    folder is its parent; every other verdict names the folder itself.
    `protected` marks containers that are never opened.
    """
    if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' "
                    "AND name='exclusion_verdicts'").fetchone() is None:
        return []
    runs = conn.execute(
        "SELECT r.scan_run_id, s.sources FROM scan_runs r "
        "JOIN corpus_selections s ON s.selection_id = r.selection_id "
        "WHERE r.completed_at IS NOT NULL "
        "ORDER BY r.started_at DESC").fetchall()
    latest: dict[str, str] = {}
    for run in runs:
        latest.setdefault(run["sources"], run["scan_run_id"])
    seen: set[str] = set()
    folders: dict[tuple[str, str], dict] = {}
    for run_id in latest.values():
        for row in exclusion_verdicts(conn, run_id):
            if row["applies_to"] != APPLIES_TO_SCANNED_SOURCE:
                continue
            if row["path"] in seen:
                continue
            seen.add(row["path"])
            folder = (str(Path(row["path"]).parent)
                      if row["rule"] == RULE_PROJECT_ROOT_DESCENDANT
                      else row["path"])
            entry = folders.setdefault((folder, row["rule"]), {
                "folder": folder, "rule": row["rule"],
                "rule_subject": row["rule_subject"], "paths": 0,
                "protected": row["rule"] == RULE_PROTECTED_CONTAINER})
            entry["paths"] += 1
    return sorted(folders.values(), key=lambda a: a["folder"])


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
            follow_move(conn, row["file_id"])
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
            follow_move(conn, row["file_id"])
    _mark_missing_under(conn, roots)
    # Witnessed duplicates from live hashes. Semantic edges are never projected.
    from items.relationships import project_witnessed_links
    project_witnessed_links(conn)


def _items_installed(conn: sqlite3.Connection) -> bool:
    found = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'items'"
    ).fetchone()
    return found is not None


def follow_move(conn: sqlite3.Connection, file_id: str) -> None:
    """Point the item at the file row's current path, minting one if none.

    Called after anything that moved a file through `observe_path`, so the
    item a person searches follows the move. No item tables, no work.
    """
    if not _items_installed(conn):
        return
    row = get_file(conn, file_id)
    path = row["current_path"]
    content_hash = row["content_hash"]
    now = datetime.now(timezone.utc).isoformat()
    label = Path(path).name
    disk = observe_disk(Path(path), content_hash=content_hash)
    existing = conn.execute(
        "SELECT item_id FROM items WHERE file_id = ? AND item_type = ?",
        (file_id, ITEM_TYPE_FILE),
    ).fetchone()
    if existing is not None:
        _point(conn, existing["item_id"], file_id, path, label)
        _ensure_version(
            conn, existing["item_id"], file_id, content_hash, now, disk=disk)
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
        _ensure_version(
            conn, prior["item_id"], file_id, content_hash, now, disk=disk)
        return

    # Rename / relocate: same bytes already attached to a live item under a
    # different path — prefer inode match, then content hash on a missing path.
    if disk is not None:
        by_inode = conn.execute(
            "SELECT item_id FROM items "
            "WHERE item_type = ? AND superseded_by IS NULL "
            "AND st_dev = ? AND st_ino = ? "
            "ORDER BY created_at LIMIT 1",
            (ITEM_TYPE_FILE, disk.st_dev, disk.st_ino),
        ).fetchone()
        if by_inode is not None:
            _point(conn, by_inode["item_id"], file_id, path, label)
            _ensure_version(
                conn, by_inode["item_id"], file_id, content_hash, now, disk=disk)
            return

    by_hash = conn.execute(
        "SELECT item_id, open_target, presence FROM items "
        "WHERE item_type = ? AND content_hash = ? AND superseded_by IS NULL "
        "ORDER BY created_at",
        (ITEM_TYPE_FILE, content_hash),
    ).fetchall()
    for candidate in by_hash:
        old_path = candidate["open_target"]
        if old_path and old_path != path and _is_absent(old_path):
            _point(conn, candidate["item_id"], file_id, path, label)
            _ensure_version(
                conn, candidate["item_id"], file_id, content_hash, now, disk=disk)
            return

    item_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, external_key, "
        "presence, typing_state, type_schema, profile_id, created_at, superseded_by, "
        "freshness_state"
        ") VALUES (?, ?, ?, ?, ?, NULL, ?, ?, NULL, NULL, ?, NULL, ?)",
        (item_id, ITEM_TYPE_FILE, label, file_id, path,
         PRESENCE_LIVE, TYPING_UNPLACED, now, DIRTY),
    )
    _ensure_version(
        conn, item_id, file_id, content_hash, now, disk=disk, new_item=True)
    if disk is not None:
        seed_new_item_identity(conn, item_id, disk, content_hash=content_hash)
    else:
        transition(
            conn, item_id, DIRTY, reason="created_without_stat",
            path=path, content_hash=content_hash, force_event=True,
        )


def _sync_freshness(conn, item_id: str, disk, content_hash: str) -> None:
    if disk is None:
        mark_missing(conn, item_id, reason="attach_path_absent")
        return
    reconcile_live_identity(
        conn, item_id, disk, content_hash=content_hash,
        reason_prefix="reconcile",
    )


def _point(conn: sqlite3.Connection, item_id: str, file_id: str,
           path: str, label: str) -> None:
    conn.execute(
        "UPDATE items SET file_id = ?, open_target = ?, display_label = ?, "
        "presence = ? WHERE item_id = ?",
        (file_id, path, label, PRESENCE_LIVE, item_id),
    )


def _ensure_version(conn: sqlite3.Connection, item_id: str, file_id: str,
                    content_hash: str, now: str, *, disk, new_item: bool = False) -> None:
    prior = conn.execute(
        "SELECT content_hash FROM items WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    prior_hash = None if prior is None else prior["content_hash"]
    existing = conn.execute(
        "SELECT 1 FROM item_versions WHERE item_id = ? AND file_id = ?",
        (item_id, file_id),
    ).fetchone()
    conn.execute(
        "INSERT OR IGNORE INTO item_versions "
        "(item_id, file_id, content_hash, became_live_at) VALUES (?, ?, ?, ?)",
        (item_id, file_id, content_hash, now),
    )
    # Compare against the old identity before persisting the new hash.
    if not new_item:
        _sync_freshness(conn, item_id, disk, content_hash)
    # Persist the live content hash on the item row for decision binding.
    conn.execute(
        "UPDATE items SET content_hash = ? WHERE item_id = ?",
        (content_hash, item_id),
    )
    changed = (
        existing is None
        or (prior_hash is not None and prior_hash != content_hash)
    )
    if changed and content_hash:
        from items.relationship_service import revalidate_for_item_version
        revalidate_for_item_version(
            conn, item_id, content_hash=content_hash)


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
            mark_missing(conn, row["item_id"], reason="reconcile_absent",
                         path=target)


def _under_any(path: str, roots) -> bool:
    candidate = PurePath(path)
    for root in roots:
        source = PurePath(root)
        if candidate == source or source in candidate.parents:
            return True
    return False
