"""Shared refresh queue across roots; concurrent enqueue/process safety."""
from __future__ import annotations

import threading
from pathlib import Path

from items.freshness import FRESH
from items.hot_index import find_files, rebuild_fts
from items.identity import reconcile_tree
from items.index_refresh import (
    enqueue,
    enqueue_dirty,
    ensure_refresh_schema,
    ensure_search_ready,
    process_queue,
)
from items.path_watch import PathWatcher


def test_two_roots_share_one_queue_no_full_rebuild_per_idle(conn, tmp_path: Path):
    r1 = tmp_path / "r1"
    r2 = tmp_path / "r2"
    r1.mkdir()
    r2.mkdir()
    (r1 / "one.txt").write_text("shared-queue-one", encoding="utf-8")
    (r2 / "two.txt").write_text("shared-queue-two", encoding="utf-8")

    w1 = PathWatcher(r1, prefer_fsevents=False)
    w2 = PathWatcher(r2, prefer_fsevents=False)
    t1 = w1.tick(conn)
    t2 = w2.tick(conn)
    assert t1.full_rebuild is False
    assert t2.full_rebuild is False

    idle1 = w1.tick(conn)
    idle2 = w2.tick(conn)
    assert idle1.full_rebuild is False
    assert idle2.full_rebuild is False
    assert idle1.accepted == 0
    assert idle2.accepted == 0

    assert find_files(conn, "shared-queue-one").hits
    assert find_files(conn, "shared-queue-two").hits


def test_concurrent_enqueue_and_process(conn, tmp_path: Path):
    from database_agent.db import open_database

    root = tmp_path / "lib"
    root.mkdir()
    for i in range(20):
        p = root / f"f{i}.txt"
        p.write_text(f"content-{i}-needle", encoding="utf-8")
    reconcile_tree(conn, root)
    ensure_refresh_schema(conn)
    enqueue_dirty(conn)
    conn.commit()
    db_path = tmp_path / "agent.sqlite"

    errors: list[BaseException] = []
    barrier = threading.Barrier(3)

    def worker_enqueue():
        c = open_database(db_path)
        try:
            c.execute("PRAGMA busy_timeout = 5000")
            barrier.wait(timeout=5)
            rows = c.execute(
                "SELECT item_id, content_hash FROM items"
            ).fetchall()
            for row in rows:
                enqueue(c, row["item_id"], row["content_hash"])
            c.commit()
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)
        finally:
            c.close()

    def worker_process():
        c = open_database(db_path)
        try:
            c.execute("PRAGMA busy_timeout = 5000")
            barrier.wait(timeout=5)
            for _ in range(5):
                process_queue(c, limit=8)
                c.commit()
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)
        finally:
            c.close()

    threads = [
        threading.Thread(target=worker_enqueue),
        threading.Thread(target=worker_process),
        threading.Thread(target=worker_process),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert not errors, errors

    # Refresh the fixture connection's view after concurrent writers.
    ensure_search_ready(conn)
    fresh = conn.execute(
        "SELECT COUNT(*) FROM items WHERE freshness_state = ?", (FRESH,)
    ).fetchone()[0]
    assert fresh == 20
    assert find_files(conn, "content-7-needle").hits


def test_rebuild_fts_still_works_as_explicit_path(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "x.txt").write_text("explicit rebuild path", encoding="utf-8")
    reconcile_tree(conn, root)
    n = rebuild_fts(conn)
    assert n == 1
    assert find_files(conn, "explicit rebuild").hits


def test_debounce_by_inode_not_only_path(tmp_path: Path):
    from items.fsevents_feed import ChangeFeedPolicy, FsEvent

    pol = ChangeFeedPolicy(debounce_ms=500)
    t0 = 1000.0
    ev1 = FsEvent("/tmp/a.txt", st_dev=1, st_ino=42, seq=1)
    ev2 = FsEvent("/tmp/a-renamed.txt", st_dev=1, st_ino=42, seq=2)
    assert pol.accept(ev1, now=t0) is True
    # Same inode, different path, within debounce → collapsed.
    assert pol.accept(ev2, now=t0 + 0.1) is False
    # After debounce window, accepted; latest retained by identity.
    assert pol.accept(ev2, now=t0 + 0.6) is True
    latest = pol.take_latest(ev2.identity_key())
    assert latest is not None
    assert latest.path.endswith("a-renamed.txt")
