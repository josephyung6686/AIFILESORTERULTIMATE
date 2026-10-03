"""Apply state machine is transactional across journal + filesystem."""
from __future__ import annotations

import hashlib
from pathlib import Path

from assistant.apply import apply_plan
from assistant.identity_commit import commit_item_path
from assistant.journal import entries_for_plan
from assistant.plans import PlanOp, approve_plan, create_draft_plan
from assistant.undo import undo_plan
from items.identity import reconcile_tree
from items.schema import create_items_schema


def _hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_journal_states_progress_planned_to_applied(
        conn, tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    src = tmp_path / "a.txt"
    dst = tmp_path / "filed" / "a.txt"
    src.write_text("x", encoding="utf-8")
    plan = create_draft_plan(conn, ops=(
        PlanOp(
            item_id="i1", src=str(src), dst=str(dst),
            file_id="f1", content_hash=_hash(src),
            root_scope=str(tmp_path.resolve()),
        ),
    ))
    approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=3000, full_list_viewed=True
    )
    out = apply_plan(conn, plan.plan_id, full_list_viewed=True)
    assert out.ok and out.moved
    entries = entries_for_plan(conn, plan.plan_id)
    assert len(entries) == 1
    assert entries[0].state == "applied"
    assert entries[0].content_hash == _hash(dst)
    assert entries[0].file_id == "f1"
    assert entries[0].root_scope == str(tmp_path.resolve())


def test_apply_updates_identity_after_success(
        conn, tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    lib = tmp_path / "lib"
    lib.mkdir()
    src = lib / "note.txt"
    src.write_text("body", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, lib)
    row = conn.execute(
        "SELECT item_id, open_target, file_id FROM items "
        "WHERE display_label='note.txt'"
    ).fetchone()
    dst = tmp_path / "out" / "note.txt"
    plan = create_draft_plan(conn, ops=(
        PlanOp(
            item_id=row["item_id"], src=row["open_target"],
            dst=str(dst), file_id=row["file_id"],
            content_hash=_hash(src),
            root_scope=str(tmp_path.resolve()),
        ),
    ))
    approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=3000, full_list_viewed=True
    )
    assert apply_plan(conn, plan.plan_id, full_list_viewed=True).ok
    updated = conn.execute(
        "SELECT open_target FROM items WHERE item_id=?", (row["item_id"],)
    ).fetchone()
    assert Path(updated["open_target"]) == dst.resolve()
    und = undo_plan(conn, plan.plan_id)
    assert und.ok
    back = conn.execute(
        "SELECT open_target FROM items WHERE item_id=?", (row["item_id"],)
    ).fetchone()
    assert Path(back["open_target"]).name == "note.txt"


def test_missing_content_hash_refuses(conn, tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    src = tmp_path / "a.txt"
    src.write_text("x", encoding="utf-8")
    plan = create_draft_plan(conn, ops=(
        PlanOp(
            item_id="i1", src=str(src), dst=str(tmp_path / "b.txt"),
            file_id="f1", content_hash=None,
            root_scope=str(tmp_path.resolve()),
        ),
    ))
    approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=3000, full_list_viewed=True
    )
    out = apply_plan(conn, plan.plan_id, full_list_viewed=True)
    assert out.ok is False
    assert src.is_file()


def test_undo_uses_undo_planned_then_undone(
        conn, tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    src = tmp_path / "a.txt"
    dst = tmp_path / "box" / "a.txt"
    src.write_text("z", encoding="utf-8")
    h = _hash(src)
    plan = create_draft_plan(conn, ops=(
        PlanOp(
            item_id="i1", src=str(src), dst=str(dst),
            file_id="f1", content_hash=h,
            root_scope=str(tmp_path.resolve()),
        ),
    ))
    approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=3000, full_list_viewed=True
    )
    assert apply_plan(conn, plan.plan_id, full_list_viewed=True).ok
    assert undo_plan(conn, plan.plan_id).ok
    entries = entries_for_plan(conn, plan.plan_id)
    assert entries[0].state == "undone"
