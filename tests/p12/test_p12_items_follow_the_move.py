"""A sorter move re-points the person's item, and an undo points it back.

`search` reads `items.open_target`. Before this, a move updated
`files.current_path` only, so search cited a path the move had just emptied.
"""
from __future__ import annotations

from pathlib import Path

from items.identity import project_after_scan
from items.schema import create_items_schema
from items.search import meaning_search
from mutation import vocabulary as v
from mutation.undo import entry_by_id

from .test_p12_undo import _apply, _entry_id, _undo


def _open_target(conn, file_id: str) -> Path:
    row = conn.execute(
        "SELECT open_target FROM items WHERE file_id = ?", (file_id,)
    ).fetchone()
    return Path(row["open_target"])


def test_a_sorter_move_and_its_undo_move_the_item(
        p12_conn, planned, fixture_root, clock, ids):
    plan, source = planned
    create_items_schema(p12_conn)
    project_after_scan(p12_conn, [fixture_root], "included")
    assert _open_target(p12_conn, plan.file_id) == source

    record = _apply(p12_conn, plan, fixture_root, clock, ids)
    assert record.result == v.APPLIED
    moved = Path(record.final_destination_path)
    assert _open_target(p12_conn, plan.file_id) == moved
    hits = meaning_search(p12_conn, "Syllabus", limit=5).hits
    assert [h.open_target for h in hits] == [str(moved)]

    entry = entry_by_id(p12_conn, _entry_id(p12_conn, plan.plan_id))
    assert _undo(p12_conn, entry.entry_id, clock, ids).verdict == v.REVERSED
    assert _open_target(p12_conn, plan.file_id) == source


def test_a_sorter_move_without_item_tables_still_applies(
        p12_conn, planned, fixture_root, clock, ids):
    plan, _ = planned
    assert _apply(p12_conn, plan, fixture_root, clock, ids).result == v.APPLIED
