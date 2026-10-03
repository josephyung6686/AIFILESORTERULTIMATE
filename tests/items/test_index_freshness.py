"""Index refresh: edit/rename/delete/offline reflected before next search."""
from __future__ import annotations

import time
from pathlib import Path

from items.freshness import DIRTY, ERROR, FRESH, MISSING, mark_indexed
from items.hot_index import find_files
from items.identity import reconcile_tree
from items.index_refresh import (
    CATCHING_UP,
    DEGRADED,
    READY,
    STARTING,
    catch_up,
    enqueue,
    enqueue_dirty,
    ensure_search_ready,
    get_index_state,
    index_status,
    process_queue,
    set_index_state,
    startup_reconcile,
    upsert_item_index,
)
from items.path_watch import PathWatcher
from items.schema import create_items_schema


def _labels(result) -> list[str]:
    return [h.display_label for h in result.hits]


def test_edit_reflected_in_search_before_next_query(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "notes.txt"
    path.write_text("alpha unique token", encoding="utf-8")
    reconcile_tree(conn, root)
    ensure_search_ready(conn)

    hit = find_files(conn, "alpha unique")
    assert any("notes" in lab for lab in _labels(hit))

    path.write_text("beta revised token", encoding="utf-8")
    reconcile_tree(conn, root)
    row = conn.execute("SELECT * FROM items").fetchone()
    assert row["freshness_state"] == DIRTY

    # Next query must catch up — no silent stale "alpha" as fresh.
    after = find_files(conn, "beta revised")
    assert any("notes" in lab for lab in _labels(after))
    stale = find_files(conn, "alpha unique")
    # Body no longer contains alpha; filename still may match nothing useful.
    bodies = conn.execute(
        "SELECT body FROM item_fts WHERE item_id = ?", (row["item_id"],)
    ).fetchone()
    assert bodies is not None
    assert "beta revised" in bodies["body"]
    assert "alpha unique" not in bodies["body"]
    assert conn.execute(
        "SELECT freshness_state FROM items WHERE item_id = ?",
        (row["item_id"],),
    ).fetchone()[0] == FRESH


def test_rename_reflected_in_search(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    src = root / "essay.txt"
    src.write_text("rename body marker", encoding="utf-8")
    reconcile_tree(conn, root)
    ensure_search_ready(conn)
    row = conn.execute("SELECT item_id FROM items").fetchone()
    item_id = row["item_id"]

    dst = root / "essay-final.txt"
    src.rename(dst)
    reconcile_tree(conn, root)
    ensure_search_ready(conn)

    result = find_files(conn, "essay-final")
    assert any(h.item_id == item_id for h in result.hits)
    path_row = conn.execute(
        "SELECT open_target FROM items WHERE item_id = ?", (item_id,)
    ).fetchone()
    assert Path(path_row["open_target"]) == dst


def test_delete_removed_from_search(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "gone.txt"
    path.write_text("vanishing content xyzzy", encoding="utf-8")
    reconcile_tree(conn, root)
    ensure_search_ready(conn)
    assert find_files(conn, "xyzzy").hits

    path.unlink()
    reconcile_tree(conn, root)
    ensure_search_ready(conn)

    row = conn.execute("SELECT presence, freshness_state FROM items").fetchone()
    assert row["presence"] == "missing" or row["freshness_state"] == MISSING
    result = find_files(conn, "xyzzy")
    assert result.hits == ()


def test_offline_change_caught_on_startup_reconcile(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "offline.txt"
    path.write_text("before downtime", encoding="utf-8")
    reconcile_tree(conn, root)
    ensure_search_ready(conn)
    row = conn.execute("SELECT item_id, content_hash FROM items").fetchone()
    mark_indexed(conn, row["item_id"], row["content_hash"])

    # Simulate watcher downtime: edit with no tick.
    path.write_text("after downtime unique", encoding="utf-8")

    status = startup_reconcile(conn, [root])
    assert status.state in (READY, CATCHING_UP, DEGRADED)
    assert get_watch_cursor_ok(conn, root)
    result = find_files(conn, "after downtime unique")
    assert any("offline" in lab for lab in _labels(result))
    after = conn.execute(
        "SELECT freshness_state, last_indexed_hash, content_hash FROM items"
    ).fetchone()
    assert after["freshness_state"] == FRESH
    assert after["last_indexed_hash"] == after["content_hash"]


def get_watch_cursor_ok(conn, root) -> bool:
    from items.index_refresh import get_watch_cursor
    return get_watch_cursor(conn, root) > 0


def test_index_state_startup_catchup_ready(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_text("hello state", encoding="utf-8")
    create_items_schema(conn)
    set_index_state(conn, STARTING)
    assert get_index_state(conn) == STARTING

    watcher = PathWatcher(root, prefer_fsevents=False)
    result = watcher.tick(conn)
    assert result.index_state in (READY, CATCHING_UP)
    assert result.full_rebuild is False
    status = index_status(conn)
    assert status.state in (READY, CATCHING_UP, DEGRADED)
    assert status.pending == 0 or status.state == CATCHING_UP


def test_idle_tick_does_not_full_rebuild(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_text("idle", encoding="utf-8")
    watcher = PathWatcher(root, prefer_fsevents=False)
    first = watcher.tick(conn)
    assert first.full_rebuild is False
    idle = watcher.tick(conn)
    assert idle.full_rebuild is False
    assert idle.accepted == 0


def test_failure_leaves_dirty_retryable_with_error(conn, tmp_path: Path, monkeypatch):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "bad.txt"
    path.write_text("will fail", encoding="utf-8")
    reconcile_tree(conn, root)
    item_id = conn.execute("SELECT item_id FROM items").fetchone()["item_id"]
    digest = conn.execute(
        "SELECT content_hash FROM items WHERE item_id = ?", (item_id,)
    ).fetchone()["content_hash"]

    import items.index_refresh as ir

    real_upsert = ir.upsert_item_index

    def boom(*_a, **_k):
        raise RuntimeError("inject index failure")

    monkeypatch.setattr(ir, "upsert_item_index", boom)
    enqueue(conn, item_id, digest)
    process_queue(conn, limit=5)

    row = conn.execute(
        "SELECT freshness_state FROM items WHERE item_id = ?", (item_id,)
    ).fetchone()
    assert row["freshness_state"] == ERROR
    q = conn.execute(
        "SELECT status, last_error FROM index_refresh_queue "
        "WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    assert q is not None
    assert q["status"] == "failed"
    assert "inject index failure" in (q["last_error"] or "")
    # Not silently fresh.
    assert row["freshness_state"] != FRESH

    # Retry after fix.
    monkeypatch.setattr(ir, "upsert_item_index", real_upsert)
    enqueue_dirty(conn)
    catch_up(conn)
    after = conn.execute(
        "SELECT freshness_state FROM items WHERE item_id = ?", (item_id,)
    ).fetchone()
    assert after["freshness_state"] == FRESH


def test_rapid_edits_index_latest_content(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "burst.txt"
    path.write_text("v0", encoding="utf-8")
    reconcile_tree(conn, root)
    for i in range(1, 6):
        path.write_text(f"version-{i}-marker", encoding="utf-8")
        time.sleep(0.01)
    reconcile_tree(conn, root)
    ensure_search_ready(conn)
    body = conn.execute("SELECT body FROM item_fts").fetchone()["body"]
    assert "version-5-marker" in body
    assert "version-1-marker" not in body


def test_queue_keyed_by_item_and_content_hash(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "q.txt"
    path.write_text("one", encoding="utf-8")
    reconcile_tree(conn, root)
    item_id = conn.execute("SELECT item_id FROM items").fetchone()["item_id"]
    h1 = conn.execute(
        "SELECT content_hash FROM items"
    ).fetchone()["content_hash"]
    enqueue(conn, item_id, h1)
    enqueue(conn, item_id, h1)  # duplicate
    n = conn.execute("SELECT COUNT(*) FROM index_refresh_queue").fetchone()[0]
    assert n == 1
    path.write_text("two", encoding="utf-8")
    reconcile_tree(conn, root)
    h2 = conn.execute(
        "SELECT content_hash FROM items"
    ).fetchone()["content_hash"]
    assert h1 != h2
    enqueue(conn, item_id, h2)
    n2 = conn.execute("SELECT COUNT(*) FROM index_refresh_queue").fetchone()[0]
    assert n2 == 2
