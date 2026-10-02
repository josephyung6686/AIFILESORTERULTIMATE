"""P4 product path: approve → apply → undo on real temp files."""
from __future__ import annotations

import os
from pathlib import Path

from assistant.apply import apply_plan
from assistant.plans import PlanOp, approve_plan, create_draft_plan
from assistant.undo import undo_plan
from items.identity import reconcile_tree
from items.schema import create_items_schema


def test_apply_undo_roundtrip(conn, tmp_path: Path, monkeypatch):
    root = tmp_path / "lib"
    root.mkdir()
    src = root / "notes.txt"
    src.write_text("hello", encoding="utf-8")
    dest_dir = tmp_path / "sorted"
    dest_dir.mkdir()
    dst = dest_dir / "notes.txt"
    create_items_schema(conn)
    reconcile_tree(conn, root)
    item = conn.execute(
        "SELECT item_id, open_target, file_id FROM items "
        "WHERE display_label='notes.txt'"
    ).fetchone()
    plan = create_draft_plan(conn, ops=[PlanOp(
        item_id=item["item_id"], src=str(src.resolve()),
        dst=str(dst), file_id=item["file_id"],
    )])
    # Without env / approval — refuse
    monkeypatch.delenv("ASSISTANT_ENABLE_APPLY", raising=False)
    bad = apply_plan(conn, plan.plan_id, full_list_viewed=True)
    assert bad.ok is False and bad.moved is False
    assert src.is_file()

    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    # approve without full list — refuse
    ar = approve_plan(conn, plan.plan_id, full_list_viewed=False)
    assert ar.ok is False
    ar = approve_plan(conn, plan.plan_id, full_list_viewed=True)
    assert ar.ok is True
    ok = apply_plan(conn, plan.plan_id, full_list_viewed=True)
    assert ok.ok is True and ok.moved is True
    assert dst.is_file() and not src.exists()

    und = undo_plan(conn, plan.plan_id)
    assert und.ok is True and und.moved is True
    assert src.is_file() and not dst.exists()
