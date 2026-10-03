"""Item identity lifecycle: create, edit, rename, delete, replace, offline."""
from __future__ import annotations

import random
from pathlib import Path

import pytest

from items.freshness import (
    DIRTY,
    FRESH,
    MISSING,
    identity_events,
    mark_indexed,
)
from items.identity import reconcile_tree
from items.schema import ITEMS_SCHEMA_VERSION, create_items_schema


def _item(conn):
    rows = conn.execute("SELECT * FROM items").fetchall()
    assert len(rows) == 1
    return rows[0]


def _events(conn, item_id):
    return identity_events(conn, item_id)


def test_create_records_durable_identity_and_dirty_state(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "essay.txt"
    path.write_bytes(b"first draft")
    st = path.lstat()

    reconcile_tree(conn, root)

    row = _item(conn)
    assert row["presence"] == "live"
    assert row["freshness_state"] == DIRTY
    assert row["content_hash"]
    assert row["size"] == st.st_size
    assert row["mtime_ns"] == st.st_mtime_ns
    assert row["st_dev"] == st.st_dev
    assert row["st_ino"] == st.st_ino
    assert row["last_seen_at"]
    assert row["last_indexed_hash"] is None
    ev = _events(conn, row["item_id"])
    assert ev
    assert ev[0]["to_state"] == DIRTY
    assert ev[0]["reason"] == "created"


def test_content_edit_marks_dirty_and_keeps_item_id(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "essay.txt"
    path.write_bytes(b"first draft")
    reconcile_tree(conn, root)
    before = _item(conn)
    mark_indexed(conn, before["item_id"], before["content_hash"])
    assert _item(conn)["freshness_state"] == FRESH

    path.write_bytes(b"revised bytes")
    reconcile_tree(conn, root)

    after = _item(conn)
    assert after["item_id"] == before["item_id"]
    assert after["content_hash"] != before["content_hash"]
    assert after["freshness_state"] == DIRTY
    assert after["last_indexed_hash"] == before["content_hash"]
    assert after["st_ino"] == before["st_ino"]
    reasons = [e["reason"] for e in _events(conn, after["item_id"])]
    assert any("content_edit" in r for r in reasons)


def test_rename_same_inode_keeps_item_and_updates_path(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "essay.txt"
    path.write_bytes(b"same bytes")
    reconcile_tree(conn, root)
    before = _item(conn)
    mark_indexed(conn, before["item_id"], before["content_hash"])

    dest = root / "notes" / "essay-final.txt"
    dest.parent.mkdir()
    path.rename(dest)
    reconcile_tree(conn, root)

    after = _item(conn)
    assert after["item_id"] == before["item_id"]
    assert after["file_id"] == before["file_id"]
    assert after["st_ino"] == before["st_ino"]
    assert after["st_dev"] == before["st_dev"]
    assert Path(after["open_target"]) == dest
    assert after["freshness_state"] == FRESH
    assert after["presence"] == "live"


def test_delete_marks_missing_immediately(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "essay.txt"
    path.write_bytes(b"keep this row")
    reconcile_tree(conn, root)
    before = _item(conn)

    path.unlink()
    reconcile_tree(conn, root)

    after = _item(conn)
    assert after["item_id"] == before["item_id"]
    assert after["presence"] == "missing"
    assert after["freshness_state"] == MISSING
    reasons = [e["reason"] for e in _events(conn, after["item_id"])]
    assert any("absent" in r for r in reasons)


def test_replacement_at_same_path_is_dirty_new_version(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "essay.txt"
    path.write_bytes(b"original payload")
    reconcile_tree(conn, root)
    before = _item(conn)
    mark_indexed(conn, before["item_id"], before["content_hash"])
    old_ino = before["st_ino"]

    path.unlink()
    path.write_bytes(b"brand new replacement")
    new_st = path.lstat()
    assert new_st.st_ino != old_ino

    reconcile_tree(conn, root)

    after = _item(conn)
    assert after["item_id"] == before["item_id"]
    assert after["content_hash"] != before["content_hash"]
    assert after["st_ino"] == new_st.st_ino
    assert after["freshness_state"] == DIRTY
    assert after["last_indexed_hash"] == before["content_hash"]
    assert after["presence"] == "live"
    reasons = [e["reason"] for e in _events(conn, after["item_id"])]
    assert any("replacement" in r or "content_edit" in r for r in reasons)


def test_edit_while_offline_surfaces_as_dirty(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "essay.txt"
    path.write_bytes(b"before offline")
    reconcile_tree(conn, root)
    before = _item(conn)
    mark_indexed(conn, before["item_id"], before["content_hash"])

    # Simulate watcher downtime: mutate disk with no reconcile in between.
    path.write_bytes(b"changed while offline")
    assert _item(conn)["freshness_state"] == FRESH  # DB not yet aware

    reconcile_tree(conn, root)
    after = _item(conn)
    assert after["item_id"] == before["item_id"]
    assert after["freshness_state"] == DIRTY
    assert after["content_hash"] != before["content_hash"]


def test_identity_events_are_append_only(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "essay.txt"
    path.write_bytes(b"x")
    reconcile_tree(conn, root)
    item_id = _item(conn)["item_id"]
    ev = _events(conn, item_id)[0]
    with pytest.raises(Exception):
        conn.execute(
            "UPDATE item_identity_events SET reason = 'mutated' "
            "WHERE event_id = ?",
            (ev["event_id"],),
        )
    with pytest.raises(Exception):
        conn.execute(
            "DELETE FROM item_identity_events WHERE event_id = ?",
            (ev["event_id"],),
        )


def test_schema_migration_from_v3_is_idempotent(conn):
    """Checked-in prior items schema was version 3 without freshness columns."""
    conn.executescript(
        """
        DROP TABLE IF EXISTS item_identity_events;
        DROP TABLE IF EXISTS items_meta;
        DROP TABLE IF EXISTS items;
        CREATE TABLE items_meta (version INTEGER NOT NULL);
        INSERT INTO items_meta (version) VALUES (3);
        CREATE TABLE items (
            item_id        TEXT PRIMARY KEY,
            item_type      TEXT NOT NULL,
            display_label  TEXT NOT NULL,
            file_id        TEXT,
            open_target    TEXT,
            external_key   TEXT,
            presence       TEXT NOT NULL,
            typing_state   TEXT NOT NULL,
            type_schema    TEXT,
            profile_id     TEXT,
            created_at     TEXT NOT NULL,
            superseded_by  TEXT
        );
        """
    )
    create_items_schema(conn)
    create_items_schema(conn)  # idempotent

    cols = {row[1] for row in conn.execute("PRAGMA table_info(items)")}
    for name in (
        "content_hash", "size", "mtime_ns", "st_dev", "st_ino",
        "last_seen_at", "last_indexed_hash", "freshness_state",
    ):
        assert name in cols
    version = conn.execute("SELECT version FROM items_meta").fetchone()[0]
    assert version == ITEMS_SCHEMA_VERSION
    assert conn.execute(
        "SELECT 1 FROM sqlite_master WHERE name = 'item_identity_events'"
    ).fetchone()


def _scenario_create(conn, root: Path) -> None:
    path = root / "essay.txt"
    path.write_bytes(b"first draft")
    reconcile_tree(conn, root)
    row = conn.execute("SELECT * FROM items").fetchone()
    assert row["freshness_state"] == DIRTY
    assert row["st_ino"] == path.lstat().st_ino


def _scenario_edit(conn, root: Path) -> None:
    path = root / "essay.txt"
    path.write_bytes(b"first draft")
    reconcile_tree(conn, root)
    before = conn.execute("SELECT * FROM items").fetchone()
    mark_indexed(conn, before["item_id"], before["content_hash"])
    path.write_bytes(b"revised")
    reconcile_tree(conn, root)
    after = conn.execute("SELECT * FROM items").fetchone()
    assert after["item_id"] == before["item_id"]
    assert after["freshness_state"] == DIRTY


def _scenario_rename(conn, root: Path) -> None:
    path = root / "essay.txt"
    path.write_bytes(b"same bytes")
    reconcile_tree(conn, root)
    before = conn.execute("SELECT * FROM items").fetchone()
    dest = root / "moved.txt"
    path.rename(dest)
    reconcile_tree(conn, root)
    after = conn.execute("SELECT * FROM items").fetchone()
    assert after["item_id"] == before["item_id"]
    assert after["st_ino"] == before["st_ino"]
    assert Path(after["open_target"]) == dest


def _scenario_delete(conn, root: Path) -> None:
    path = root / "essay.txt"
    path.write_bytes(b"gone")
    reconcile_tree(conn, root)
    path.unlink()
    reconcile_tree(conn, root)
    after = conn.execute("SELECT * FROM items").fetchone()
    assert after["freshness_state"] == MISSING
    assert after["presence"] == "missing"


def _scenario_replace(conn, root: Path) -> None:
    path = root / "essay.txt"
    path.write_bytes(b"original")
    reconcile_tree(conn, root)
    before = conn.execute("SELECT * FROM items").fetchone()
    mark_indexed(conn, before["item_id"], before["content_hash"])
    path.unlink()
    path.write_bytes(b"replacement")
    reconcile_tree(conn, root)
    after = conn.execute("SELECT * FROM items").fetchone()
    assert after["item_id"] == before["item_id"]
    assert after["freshness_state"] == DIRTY
    assert after["st_ino"] != before["st_ino"]


@pytest.mark.parametrize("seed", [1, 2, 3, 7, 11])
def test_lifecycle_order_independent(conn, tmp_path: Path, seed: int):
    """Isolated lifecycle scenarios in shuffled order stay consistent."""
    scenarios = [
        ("create", _scenario_create),
        ("edit", _scenario_edit),
        ("rename", _scenario_rename),
        ("delete", _scenario_delete),
        ("replace", _scenario_replace),
    ]
    rng = random.Random(seed)
    rng.shuffle(scenarios)
    for name, fn in scenarios:
        root = tmp_path / f"{seed}-{name}"
        root.mkdir()
        # Fresh item tables per scenario share one DB; wipe items between runs.
        create_items_schema(conn)
        # Append-only trigger blocks DELETE; drop it briefly for test isolation.
        conn.executescript(
            """
            DROP TRIGGER IF EXISTS item_identity_events_no_delete;
            DROP TRIGGER IF EXISTS item_identity_events_no_update;
            DELETE FROM item_identity_events;
            DELETE FROM item_versions;
            DELETE FROM items;
            DELETE FROM files;
            """
        )
        create_items_schema(conn)  # restore triggers
        fn(conn, root)
