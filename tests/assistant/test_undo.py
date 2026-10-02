"""Undo reverses apply under the same env gate."""
from __future__ import annotations

import hashlib
from pathlib import Path

from assistant.apply import apply_plan
from assistant.plans import PlanOp, approve_plan, create_draft_plan
from assistant.undo import undo_plan


def test_undo_roundtrip(conn, tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    src = tmp_path / "a.txt"
    dst = tmp_path / "box" / "a.txt"
    src.write_text("roundtrip", encoding="utf-8")
    h = hashlib.sha256(src.read_bytes()).hexdigest()
    plan = create_draft_plan(conn, ops=(
        PlanOp(item_id="i1", src=str(src), dst=str(dst), content_hash=h),
    ))
    approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=3000,
        full_list_viewed=True)
    assert apply_plan(conn, plan.plan_id, full_list_viewed=True).moved
    assert not src.exists() and dst.exists()
    und = undo_plan(conn, plan.plan_id)
    assert und.ok and und.moved
    assert src.read_text(encoding="utf-8") == "roundtrip"
    assert not dst.exists()
