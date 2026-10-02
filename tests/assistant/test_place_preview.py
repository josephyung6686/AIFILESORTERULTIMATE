"""P3 place_preview: full list + hash checks; never moves."""
from __future__ import annotations

from pathlib import Path

from assistant.place_preview import place_preview, preview_as_dict
from assistant.plans import PlanOp, approve_plan, create_draft_plan


def test_tool_runtime_place_preview(conn, tmp_path: Path):
    from assistant.tools import ToolRuntime
    src = tmp_path / "t.pdf"
    src.write_bytes(b"data")
    plan = create_draft_plan(conn, ops=(
        PlanOp(item_id="i1", src=str(src), dst=str(tmp_path / "z.pdf")),
    ))
    approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=3000,
        full_list_viewed=True)
    rt = ToolRuntime(conn)
    out = rt.execute("place_preview", {
        "plan_id": plan.plan_id, "full_list_viewed": True})
    assert out.ok is True
    assert out.payload["moved"] is False
    assert out.payload["can_apply"] is False


def test_preview_never_moves_and_lists_all_ops(conn, tmp_path: Path):
    src = tmp_path / "a.pdf"
    src.write_bytes(b"%PDF-1.4 preview")
    dst = tmp_path / "out" / "a.pdf"
    ops = (
        PlanOp(
            item_id="i1", src=str(src), dst=str(dst),
            file_id="f1", content_hash=None,
        ),
        PlanOp(
            item_id="i2", src=str(tmp_path / "missing.pdf"),
            dst=str(tmp_path / "out" / "m.pdf"),
        ),
    )
    plan = create_draft_plan(conn, ops=ops, risk_tier="T1")
    approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=3000,
        full_list_viewed=True)
    prev = place_preview(conn, plan.plan_id, full_list_viewed=True)
    assert prev.moved is False
    assert prev.can_apply is False
    assert len(prev.ops) == 2
    assert any("missing" in b for b in prev.blockers)
    assert any("ASSISTANT_ENABLE_APPLY" in b for b in prev.blockers)
    d = preview_as_dict(prev)
    assert d["moved"] is False
    assert len(d["ops"]) == 2
