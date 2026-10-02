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
    assert result.accepted >= 1
    assert result.reindexed is True
    labels = [
        r["display_label"]
        for r in conn.execute("SELECT display_label FROM items")
    ]
    assert "b.txt" in labels


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
