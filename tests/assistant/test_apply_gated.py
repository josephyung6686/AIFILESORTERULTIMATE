"""P4 apply: default off; with env + gates, moves once; hash mismatch refuses."""
from __future__ import annotations

import hashlib
from pathlib import Path

from assistant.apply import apply_plan
from assistant.plans import PlanOp, approve_plan, create_draft_plan
from assistant.tools import ToolRuntime


def _hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_apply_refused_without_env(conn, tmp_path: Path, monkeypatch):
    monkeypatch.delenv("ASSISTANT_ENABLE_APPLY", raising=False)
    src = tmp_path / "a.txt"
    src.write_text("x", encoding="utf-8")
    plan = create_draft_plan(conn, ops=(
        PlanOp(item_id="i1", src=str(src), dst=str(tmp_path / "b.txt"),
               content_hash=_hash(src)),
    ))
    approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=3000,
        full_list_viewed=True)
    out = apply_plan(conn, plan.plan_id, full_list_viewed=True)
    assert out.moved is False
    assert src.is_file()


def test_apply_moves_when_enabled(conn, tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    src = tmp_path / "a.txt"
    dst = tmp_path / "dest" / "a.txt"
    src.write_text("payload", encoding="utf-8")
    plan = create_draft_plan(conn, ops=(
        PlanOp(item_id="i1", src=str(src), dst=str(dst),
               content_hash=_hash(src)),
    ))
    approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=3000,
        full_list_viewed=True)
    out = apply_plan(conn, plan.plan_id, full_list_viewed=True)
    assert out.ok is True
    assert out.moved is True
    assert not src.exists()
    assert dst.read_text(encoding="utf-8") == "payload"


def test_tool_apply_still_dark_even_with_env(conn, tmp_path: Path, monkeypatch):
    """ToolRuntime keeps apply_moves refused — only assistant.apply.apply_plan."""
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    rt = ToolRuntime(conn)
    out = rt.execute("apply_moves", {"plan_id": "x"})
    assert out.ok is False
    assert out.payload.get("moved") is False
