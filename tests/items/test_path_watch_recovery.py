"""Watcher downtime, duplicate events, and process-restart recovery."""
from __future__ import annotations

import time
from pathlib import Path

from items.fsevents_feed import ChangeFeedPolicy, FsEvent
from items.freshness import FRESH
from items.hot_index import find_files
from items.identity import reconcile_tree
from items.index_refresh import (
    READY,
    advance_watch_cursor,
    ensure_search_ready,
    get_watch_cursor,
    startup_reconcile,
)
from items.path_watch import PathWatcher


def test_watcher_downtime_then_restart_catches_edits(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "doc.txt"
    path.write_text("start body", encoding="utf-8")

    w1 = PathWatcher(root, prefer_fsevents=False)
    r1 = w1.tick(conn)
    assert r1.index_state in (READY, "catching_up")
    cursor1 = get_watch_cursor(conn, root)
    assert cursor1 > 0
    w1.stop_live()

    # Downtime: rename + edit with no watcher.
    path.write_text("mid edit while down", encoding="utf-8")
    renamed = root / "doc-renamed.txt"
    path.rename(renamed)
    renamed.write_text("final after restart UNIQUE99", encoding="utf-8")

    # New process: fresh PathWatcher, durable cursor present.
    w2 = PathWatcher(root, prefer_fsevents=False)
    r2 = w2.tick(conn)
    assert get_watch_cursor(conn, root) >= cursor1
    assert r2.full_rebuild is False
    result = find_files(conn, "UNIQUE99")
    assert any("doc-renamed" in h.display_label for h in result.hits)
    row = conn.execute("SELECT freshness_state FROM items").fetchone()
    assert row["freshness_state"] == FRESH
    w2.stop_live()


def test_duplicate_event_delivery_is_idempotent(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "dup.txt"
    path.write_text("dup body", encoding="utf-8")
    reconcile_tree(conn, root)
    ensure_search_ready(conn)
    st = path.stat()

    pol = ChangeFeedPolicy(debounce_ms=0)
    events = [
        FsEvent(str(path), flags="modified",
                st_dev=st.st_dev, st_ino=st.st_ino, seq=1),
        FsEvent(str(path), flags="modified",
                st_dev=st.st_dev, st_ino=st.st_ino, seq=2),
        FsEvent(str(path), flags="modified",
                st_dev=st.st_dev, st_ino=st.st_ino, seq=3),
    ]
    accepted = pol.filter_batch(events)
    # Coalesced to one latest event per identity.
    assert len(accepted) == 1
    assert accepted[0].seq == 3

    watcher = PathWatcher(root, prefer_fsevents=False, policy=pol)
    watcher._startup_done = True
    watcher._primed = True
    watcher._mtime_index[str(path)] = path.stat().st_mtime
    # Feed duplicates through tick by injecting via scan override.
    watcher.scan_events = lambda: events  # type: ignore[method-assign]
    result = watcher.tick(conn)
    assert result.full_rebuild is False
    assert result.reindexed is True
    # Second identical delivery should not break state.
    result2 = watcher.tick(conn)
    assert result2.full_rebuild is False
    row = conn.execute(
        "SELECT freshness_state, last_indexed_hash, content_hash FROM items"
    ).fetchone()
    assert row["freshness_state"] == FRESH
    assert row["last_indexed_hash"] == row["content_hash"]


def test_rename_plus_edit_during_recovery(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    src = root / "paper.txt"
    src.write_text("draft one", encoding="utf-8")
    w = PathWatcher(root, prefer_fsevents=False)
    w.tick(conn)
    item_id = conn.execute("SELECT item_id FROM items").fetchone()["item_id"]

    dst = root / "paper-v2.txt"
    src.rename(dst)
    dst.write_text("draft two SEARCHME", encoding="utf-8")
    # Process "restart": new watcher instance.
    w.stop_live()
    w2 = PathWatcher(root, prefer_fsevents=False)
    w2.tick(conn)
    result = find_files(conn, "SEARCHME")
    assert any(h.item_id == item_id for h in result.hits)
    open_target = conn.execute(
        "SELECT open_target FROM items WHERE item_id = ?", (item_id,)
    ).fetchone()["open_target"]
    assert Path(open_target) == dst


def test_watermark_never_moves_backward(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_text("x", encoding="utf-8")
    startup_reconcile(conn, [root])
    c1 = get_watch_cursor(conn, root)
    advance_watch_cursor(conn, root, c1 + 100)
    c2 = get_watch_cursor(conn, root)
    assert c2 == c1 + 100
    advance_watch_cursor(conn, root, c1)  # attempt regress
    assert get_watch_cursor(conn, root) == c2


def test_two_roots_independent_cursors_shared_queue(conn, tmp_path: Path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    (a / "a.txt").write_text("root-a-token", encoding="utf-8")
    (b / "b.txt").write_text("root-b-token", encoding="utf-8")

    wa = PathWatcher(a, prefer_fsevents=False)
    wb = PathWatcher(b, prefer_fsevents=False)
    wa.tick(conn)
    wb.tick(conn)

    ca = get_watch_cursor(conn, a)
    cb = get_watch_cursor(conn, b)
    assert ca > 0 and cb > 0
    # Independent watermarks.
    advance_watch_cursor(conn, a, ca + 50)
    assert get_watch_cursor(conn, a) == ca + 50
    assert get_watch_cursor(conn, b) == cb

    assert find_files(conn, "root-a-token").hits
    assert find_files(conn, "root-b-token").hits
    pending = conn.execute(
        "SELECT COUNT(*) FROM index_refresh_queue "
        "WHERE status IN ('pending', 'processing')"
    ).fetchone()[0]
    assert pending == 0
