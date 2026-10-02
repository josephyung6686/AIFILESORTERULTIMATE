"""apply_moves/undo_moves via ToolRuntime when ASSISTANT_ENABLE_APPLY=1."""
from __future__ import annotations

import hashlib
from pathlib import Path

from assistant.plans import PlanOp, approve_plan, create_draft_plan
from assistant.tools import ToolRuntime


def test_apply_undo_through_tools(conn, tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    src = tmp_path / "a.txt"
    dst = tmp_path / "box" / "a.txt"
    src.write_text("via-tools", encoding="utf-8")
    h = hashlib.sha256(src.read_bytes()).hexdigest()
    plan = create_draft_plan(conn, ops=(
        PlanOp(item_id="i1", src=str(src), dst=str(dst), content_hash=h),
    ))
    approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=3000,
        full_list_viewed=True)

    rt = ToolRuntime(conn)
    # Must request organize_apply first
    req = rt.execute("request_tools", {"group": "organize_apply"})
    assert req.ok is True
    assert req.payload.get("write_enabled") is True

    out = rt.execute("apply_moves", {
        "plan_id": plan.plan_id,
        "full_list_viewed": True,
    })
    assert out.ok is True
    assert out.payload.get("moved") is True
    assert not src.exists() and dst.exists()

    und = rt.execute("undo_moves", {"plan_id": plan.plan_id})
    assert und.ok is True
    assert und.payload.get("moved") is True
    assert src.read_text(encoding="utf-8") == "via-tools"


def test_apply_still_dark_without_env(conn, tmp_path: Path, monkeypatch):
    monkeypatch.delenv("ASSISTANT_ENABLE_APPLY", raising=False)
    rt = ToolRuntime(conn)
    rt.execute("request_tools", {"group": "organize_apply"})
    out = rt.execute("apply_moves", {"plan_id": "x", "full_list_viewed": True})
    assert out.ok is False
    assert out.payload.get("moved") is False
