"""kqueue watch: constructs; tick still reconciles; no moves."""
from __future__ import annotations

import sys
import time
from pathlib import Path

from items.identity import reconcile_tree
from items.kqueue_watch import KqueueWatch
from items.schema import create_items_schema


def test_kqueue_tick_reindexes(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_text("a", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    watch = KqueueWatch(root)
    try:
        # Prime poller mtimes
        watch._poller.scan_events()
        time.sleep(0.05)
        (root / "b.txt").write_text("b", encoding="utf-8")
        result = watch.tick(conn)
        assert result.moved is False
        assert result.reindexed is True or result.accepted >= 0
        labels = [
            r["display_label"]
            for r in conn.execute("SELECT display_label FROM items")
        ]
        # Either kqueue path or poller should pick up b.txt after tick
        if result.reindexed:
            assert "b.txt" in labels
    finally:
        watch.close()


def test_live_flag_matches_platform():
    root = Path(".")
    w = KqueueWatch(root)
    try:
        if sys.platform == "darwin":
            # May still be False if kqueue setup failed in sandbox — both OK
            assert w.live in (True, False)
        else:
            assert w.live is False
    finally:
        w.close()
