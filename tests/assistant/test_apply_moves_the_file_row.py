"""An assistant move updates the sorter's file row, and undo puts it back."""
from __future__ import annotations

import hashlib
from pathlib import Path

from assistant.apply import apply_plan
from assistant.plans import PlanOp, approve_plan, create_draft_plan
from assistant.undo import undo_plan
from items.identity import reconcile_tree


def _current_path(conn, file_id: str) -> Path:
    row = conn.execute(
        "SELECT current_path FROM files WHERE file_id = ?", (file_id,)
    ).fetchone()
    return Path(row["current_path"])


def test_apply_and_undo_move_files_current_path(
        conn, tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    lib = tmp_path / "lib"
    lib.mkdir()
    src = lib / "note.txt"
    src.write_text("body", encoding="utf-8")
    reconcile_tree(conn, lib)
    item = conn.execute(
        "SELECT item_id, open_target, file_id FROM items "
        "WHERE display_label = 'note.txt'").fetchone()
    dst = lib / "filed" / "note.txt"
    plan = create_draft_plan(conn, ops=(
        PlanOp(item_id=item["item_id"], src=item["open_target"], dst=str(dst),
               file_id=item["file_id"],
               content_hash=hashlib.sha256(src.read_bytes()).hexdigest(),
               root_scope=str(tmp_path.resolve())),
    ))
    approve_plan(conn, plan.plan_id, actor="user", approve_ms=3000,
                 full_list_viewed=True)

    assert apply_plan(conn, plan.plan_id, full_list_viewed=True).ok
    assert _current_path(conn, item["file_id"]) == dst.resolve()

    assert undo_plan(conn, plan.plan_id).ok
    assert _current_path(conn, item["file_id"]) == src.resolve()
    back = conn.execute("SELECT open_target FROM items WHERE item_id = ?",
                        (item["item_id"],)).fetchone()
    assert Path(back["open_target"]) == src.resolve()
