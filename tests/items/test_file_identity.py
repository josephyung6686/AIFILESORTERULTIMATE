"""A file item follows the bytes when the path changes outside the app.

Finder is not on this machine. A rename or move is `Path.rename` or a copy
onto a new inode followed by deleting the old path. The watch is
`SessionWatch.poll`, the stdlib stand-in for a folder watch, and the index
update is `reconcile_tree`.
"""
from pathlib import Path
import shutil

from database_agent.files_table import PATH_NO_LONGER_EXISTS, get_file
from database_agent.identity import hash_file
from grouping.vocabulary import P1_INCLUDED_SCAN_STATE
from items.identity import project_after_scan, reconcile_tree
from scan_agent.basic_record import record_basic_record
from scan_agent.disappearance import reconcile_disappearances
from scan_agent.exclusion import APPLIES_TO_SCANNED_SOURCE
from scan_agent.traversal import ObservedFile
from scan_agent.watch import SessionWatch


def _items(conn):
    return conn.execute(
        "SELECT * FROM items ORDER BY display_label, item_id").fetchall()


def _version_ids(conn, item_id):
    return {row["file_id"] for row in conn.execute(
        "SELECT file_id FROM item_versions WHERE item_id = ?", (item_id,))}


def test_a_file_renamed_or_moved_outside_the_app_is_found_by_fingerprint(
        conn, tmp_path: Path):
    root = tmp_path / "library"
    root.mkdir()
    original = root / "essay.txt"
    original.write_bytes(b"same bytes")
    reconcile_tree(conn, root)
    reconcile_tree(conn, root)
    assert len(_items(conn)) == 1
    before = _items(conn)[0]

    watch = SessionWatch(conn)
    watch.open([root])
    moved = root / "notes" / "essay-final.txt"
    moved.parent.mkdir()
    original.rename(moved)
    watch.poll()
    reconcile_tree(conn, root)

    rows = _items(conn)
    assert len(rows) == 1
    after = rows[0]
    assert after["item_id"] == before["item_id"]
    assert after["file_id"] == before["file_id"]
    assert after["presence"] == "live"
    assert Path(after["open_target"]) == moved
    assert get_file(conn, after["file_id"])["content_hash"] == hash_file(
        moved, materialized=True)


def test_a_move_onto_a_new_inode_is_found_by_the_content_fingerprint(
        conn, tmp_path: Path):
    root = tmp_path / "library"
    root.mkdir()
    original = root / "essay.txt"
    original.write_bytes(b"same bytes")
    reconcile_tree(conn, root)
    before = _items(conn)[0]

    dest = root / "elsewhere" / "essay.txt"
    dest.parent.mkdir()
    shutil.copyfile(original, dest)
    original.unlink()
    reconcile_tree(conn, root)

    rows = _items(conn)
    assert len(rows) == 1
    after = rows[0]
    assert after["item_id"] == before["item_id"]
    assert after["file_id"] == before["file_id"]
    assert after["presence"] == "live"
    assert Path(after["open_target"]) == dest
    assert get_file(conn, after["file_id"])["content_hash"] == hash_file(
        dest, materialized=True)


def test_an_edited_file_keeps_its_item_through_the_version_chain(
        conn, tmp_path: Path):
    root = tmp_path / "library"
    root.mkdir()
    original = root / "essay.txt"
    original.write_bytes(b"first draft")
    reconcile_tree(conn, root)
    before = _items(conn)[0]

    original.write_bytes(b"revised bytes")
    reconcile_tree(conn, root)

    rows = _items(conn)
    assert len(rows) == 1
    after = rows[0]
    assert after["item_id"] == before["item_id"]
    assert after["file_id"] != before["file_id"]
    assert after["presence"] == "live"
    assert Path(after["open_target"]) == original
    assert _version_ids(conn, after["item_id"]) == {
        before["file_id"], after["file_id"]}


def test_a_missing_file_is_reported_missing_and_not_dropped(conn, tmp_path: Path):
    root = tmp_path / "library"
    root.mkdir()
    original = root / "essay.txt"
    original.write_bytes(b"keep this row")
    reconcile_tree(conn, root)
    before = _items(conn)[0]

    original.unlink()
    reconcile_tree(conn, root)

    rows = _items(conn)
    assert len(rows) == 1
    after = rows[0]
    assert after["item_id"] == before["item_id"]
    assert after["presence"] == "missing"
    recorded = get_file(conn, before["file_id"])
    assert recorded is not None
    assert recorded["scan_state"] == PATH_NO_LONGER_EXISTS


def test_a_file_that_comes_back_is_live_again(conn, tmp_path: Path):
    root = tmp_path / "library"
    root.mkdir()
    original = root / "essay.txt"
    payload = b"keep this row"
    original.write_bytes(payload)
    reconcile_tree(conn, root)
    before = _items(conn)[0]

    original.unlink()
    reconcile_tree(conn, root)
    assert _items(conn)[0]["presence"] == "missing"

    original.write_bytes(payload)
    reconcile_tree(conn, root)

    rows = _items(conn)
    assert len(rows) == 1
    after = rows[0]
    assert after["item_id"] == before["item_id"]
    assert after["file_id"] == before["file_id"]
    assert after["presence"] == "live"
    assert Path(after["open_target"]) == original


def test_the_live_scan_projection_follows_a_rename_and_a_return(conn, tmp_path: Path):
    """`project_after_scan` is what a person's scan runs after `observe_path`.

    It does not walk. The file index has already resolved the path.
    """
    root = tmp_path / "library"
    root.mkdir()
    original = root / "essay.txt"
    payload = b"same bytes"
    original.write_bytes(payload)
    reconcile_tree(conn, root)
    before = _items(conn)[0]

    moved = root / "essay-renamed.txt"
    original.rename(moved)
    _observe(conn, moved)
    reconcile_disappearances(
        conn, "live-scan", sources=[root], scan_state=P1_INCLUDED_SCAN_STATE)
    project_after_scan(conn, [root], P1_INCLUDED_SCAN_STATE)

    renamed = _items(conn)
    assert len(renamed) == 1
    assert renamed[0]["item_id"] == before["item_id"]
    assert renamed[0]["file_id"] == before["file_id"]
    assert renamed[0]["presence"] == "live"
    assert Path(renamed[0]["open_target"]) == moved

    moved.unlink()
    reconcile_disappearances(
        conn, "live-scan-gone", sources=[root], scan_state=P1_INCLUDED_SCAN_STATE)
    project_after_scan(conn, [root], P1_INCLUDED_SCAN_STATE)
    assert _items(conn)[0]["presence"] == "missing"

    moved.write_bytes(payload)
    _observe(conn, moved)
    project_after_scan(conn, [root], P1_INCLUDED_SCAN_STATE)
    restored = _items(conn)
    assert len(restored) == 1
    assert restored[0]["item_id"] == before["item_id"]
    assert restored[0]["presence"] == "live"


def _observe(conn, path: Path) -> None:
    stat = path.stat()
    record_basic_record(
        conn,
        ObservedFile(str(path), stat.st_size, stat.st_mtime, False,
                     APPLIES_TO_SCANNED_SOURCE),
        mime_type_for=lambda _path: None,
        scan_state=P1_INCLUDED_SCAN_STATE,
    )


def test_two_live_copies_stay_two_items(conn, tmp_path: Path):
    root = tmp_path / "library"
    root.mkdir()
    original = root / "essay.txt"
    original.write_bytes(b"same bytes")
    reconcile_tree(conn, root)

    copy = root / "essay-copy.txt"
    copy.write_bytes(b"same bytes")
    reconcile_tree(conn, root)

    rows = _items(conn)
    assert len(rows) == 2
    assert len({row["item_id"] for row in rows}) == 2
    assert len({row["file_id"] for row in rows}) == 2
    assert {row["presence"] for row in rows} == {"live"}
