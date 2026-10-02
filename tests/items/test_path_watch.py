"""PathWatcher: reindex on change; ignore own-move echoes."""
from __future__ import annotations

import time
from pathlib import Path

from items.fsevents_feed import FsEvent
from items.identity import reconcile_tree
from items.path_watch import PathWatcher
from items.schema import create_items_schema


def test_tick_reindexes_on_new_file(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_text("one", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    watcher = PathWatcher(root)
    # Prime mtime index
    watcher.scan_events()
    time.sleep(0.02)
    (root / "b.txt").write_text("two new", encoding="utf-8")
    result = watcher.tick(conn)
    assert result.moved is False
    # accepted>=1 from feed, or drift catch when FSEvents/debounce races
    assert result.reindexed is True
    labels = [
        r["display_label"]
        for r in conn.execute("SELECT display_label FROM items")
    ]
    assert "b.txt" in labels


def test_tick_reindexes_via_drift_when_feed_quiet(conn, tmp_path: Path):
    """Even if the change feed misses a create, disk≠DB forces reindex."""
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_text("one", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    watcher = PathWatcher(root, prefer_fsevents=False)
    watcher.scan_events()
    (root / "sneaky.txt").write_text("hidden create", encoding="utf-8")
    # Poison the mtime index so polling thinks sneaky was already seen.
    key = str(root / "sneaky.txt")
    watcher._mtime_index[key] = (root / "sneaky.txt").stat().st_mtime
    result = watcher.tick(conn)
    assert result.reindexed is True
    labels = {
        r["display_label"]
        for r in conn.execute("SELECT display_label FROM items")
    }
    assert "sneaky.txt" in labels


def test_own_move_echo_skipped(tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    target = root / "c.txt"
    target.write_text("c", encoding="utf-8")
    watcher = PathWatcher(root)
    watcher.policy.note_own_move(str(target), str(root / "d.txt"))
    assert watcher.policy.accept(FsEvent(str(target))) is False
    watcher.policy.clear_own_move(str(target), str(root / "d.txt"))
    assert watcher.policy.accept(FsEvent(str(target))) is True


def test_tick_follows_inode_rename(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    src = root / "essay.pdf"
    src.write_text("same inode body", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    watcher = PathWatcher(root)
    watcher.scan_events()  # prime
    # Bookmarks after first tick with a noop change
    (root / "touch.txt").write_text("x", encoding="utf-8")
    watcher.tick(conn)
    row = conn.execute(
        "SELECT item_id, open_target FROM items "
        "WHERE display_label='essay.pdf'"
    ).fetchone()
    assert row is not None
    item_id = row["item_id"]
    dst = root / "essay-renamed.pdf"
    src.rename(dst)
    result = watcher.tick(conn)
    assert result.renames_followed >= 1 or result.reindexed is True
    updated = conn.execute(
        "SELECT open_target FROM items WHERE item_id=?", (item_id,)
    ).fetchone()
    assert updated is not None
    assert Path(updated["open_target"]) == dst
