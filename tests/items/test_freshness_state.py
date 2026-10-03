"""Freshness state machine and durable field behaviour."""
from __future__ import annotations

from pathlib import Path

import pytest

from items.freshness import (
    CONFLICTED,
    DIRTY,
    ERROR,
    FRESH,
    INDEXING,
    MISSING,
    identity_events,
    mark_conflicted,
    mark_error,
    mark_indexed,
    mark_indexing,
    mark_missing,
    observe_disk,
    reconcile_live_identity,
    seed_new_item_identity,
)
from items.identity import reconcile_tree
from items.schema import create_items_schema


def _one(conn):
    rows = conn.execute("SELECT * FROM items").fetchall()
    assert len(rows) == 1
    return rows[0]


def test_observe_disk_reads_inode_size_mtime(tmp_path: Path):
    path = tmp_path / "a.txt"
    path.write_bytes(b"abc")
    st = path.lstat()
    disk = observe_disk(path, hash_bytes=True)
    assert disk is not None
    assert disk.size == 3
    assert disk.mtime_ns == st.st_mtime_ns
    assert disk.st_dev == st.st_dev
    assert disk.st_ino == st.st_ino
    assert disk.content_hash
    assert observe_disk(tmp_path / "missing.txt") is None


def test_mark_indexed_makes_fresh(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_bytes(b"body")
    reconcile_tree(conn, root)
    row = _one(conn)
    assert row["freshness_state"] == DIRTY
    mark_indexed(conn, row["item_id"], row["content_hash"])
    after = _one(conn)
    assert after["freshness_state"] == FRESH
    assert after["last_indexed_hash"] == after["content_hash"]


def test_indexing_and_error_states(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_bytes(b"body")
    reconcile_tree(conn, root)
    item_id = _one(conn)["item_id"]
    assert mark_indexing(conn, item_id) == INDEXING
    assert _one(conn)["freshness_state"] == INDEXING
    assert mark_error(conn, item_id, details="boom") == ERROR
    assert _one(conn)["freshness_state"] == ERROR
    reasons = [e["reason"] for e in identity_events(conn, item_id)]
    assert "indexing_started" in reasons
    assert "index_error" in reasons


def test_path_match_changed_hash_is_dirty_not_fresh(conn, tmp_path: Path):
    create_items_schema(conn)
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "a.txt"
    path.write_bytes(b"one")
    reconcile_tree(conn, root)
    row = _one(conn)
    mark_indexed(conn, row["item_id"], row["content_hash"])

    path.write_bytes(b"two")
    disk = observe_disk(path, hash_bytes=True)
    assert disk is not None
    state = reconcile_live_identity(
        conn, row["item_id"], disk, content_hash=disk.content_hash,
    )
    assert state == DIRTY
    after = _one(conn)
    assert after["freshness_state"] == DIRTY
    assert after["last_indexed_hash"] == row["content_hash"]
    assert after["content_hash"] != row["content_hash"]


def test_missing_marks_presence_and_freshness(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "a.txt"
    path.write_bytes(b"x")
    reconcile_tree(conn, root)
    item_id = _one(conn)["item_id"]
    mark_missing(conn, item_id, path=str(path))
    row = _one(conn)
    assert row["presence"] == "missing"
    assert row["freshness_state"] == MISSING


def test_conflicted_state_recorded(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "a.txt"
    path.write_bytes(b"x")
    reconcile_tree(conn, root)
    item_id = _one(conn)["item_id"]
    disk = observe_disk(path, hash_bytes=True)
    assert mark_conflicted(conn, item_id, disk=disk, details="race") == CONFLICTED
    assert _one(conn)["freshness_state"] == CONFLICTED
    assert identity_events(conn, item_id)[-1]["to_state"] == CONFLICTED


def test_seed_new_item_writes_all_fields(conn, tmp_path: Path):
    create_items_schema(conn)
    path = tmp_path / "solo.txt"
    path.write_bytes(b"solo")
    disk = observe_disk(path, hash_bytes=True)
    assert disk is not None
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, "
        "presence, typing_state, created_at, freshness_state"
        ") VALUES ('i1', 'file', 'solo.txt', NULL, ?, 'live', 'unplaced', "
        "'t0', 'dirty')",
        (str(path),),
    )
    seed_new_item_identity(conn, "i1", disk, content_hash=disk.content_hash)
    row = conn.execute("SELECT * FROM items WHERE item_id='i1'").fetchone()
    assert row["content_hash"] == disk.content_hash
    assert row["size"] == disk.size
    assert row["mtime_ns"] == disk.mtime_ns
    assert row["st_dev"] == disk.st_dev
    assert row["st_ino"] == disk.st_ino
    assert row["last_seen_at"]
    assert row["freshness_state"] == DIRTY


def test_open_database_migrates_existing_items(tmp_path: Path):
    """db.create_schema migrates items columns when the table already exists."""
    from database_agent.db import open_database

    db_path = tmp_path / "agent.sqlite"
    conn = open_database(db_path)
    create_items_schema(conn)
    # Simulate a downgrade of metadata + drop new columns by rebuilding v3 shape.
    conn.executescript(
        """
        DROP TABLE item_identity_events;
        DROP TABLE items;
        DROP TABLE items_meta;
        CREATE TABLE items_meta (version INTEGER NOT NULL);
        INSERT INTO items_meta (version) VALUES (3);
        CREATE TABLE items (
            item_id TEXT PRIMARY KEY,
            item_type TEXT NOT NULL,
            display_label TEXT NOT NULL,
            file_id TEXT,
            open_target TEXT,
            external_key TEXT,
            presence TEXT NOT NULL,
            typing_state TEXT NOT NULL,
            type_schema TEXT,
            profile_id TEXT,
            created_at TEXT NOT NULL,
            superseded_by TEXT
        );
        INSERT INTO items VALUES (
            'x', 'file', 'a.txt', NULL, '/tmp/a.txt', NULL,
            'live', 'unplaced', NULL, NULL, 't0', NULL
        );
        """
    )
    conn.close()

    conn2 = open_database(db_path)
    try:
        cols = {row[1] for row in conn2.execute("PRAGMA table_info(items)")}
        assert "freshness_state" in cols
        assert "content_hash" in cols
        version = conn2.execute("SELECT version FROM items_meta").fetchone()[0]
        assert version >= 4
    finally:
        conn2.close()
