"""P3 spine: plan objects + undo journal. Apply still refused."""
from __future__ import annotations

from assistant.journal import entries_for_plan, record_planned
from assistant.plans import (
    PlanOp,
    create_draft_plan,
    refuse_apply_without_approval,
)
from assistant.tools import ToolRuntime


def test_draft_plan_and_journal_without_move(conn):
    ops = (
        PlanOp(item_id="i1", src="/a/x.pdf", dst="/b/x.pdf", file_id="f1"),
        PlanOp(item_id="i2", src="/a/y.pdf", dst="/b/y.pdf", file_id="f2"),
    )
    plan = create_draft_plan(conn, ops=ops, risk_tier="T1")
    assert plan.state == "draft"
    assert plan.summary["count"] == 2
    assert plan.summary["reversible"] is True

    for op in ops:
        record_planned(
            conn, plan_id=plan.plan_id, item_id=op.item_id,
            src=op.src, dst=op.dst, file_id=op.file_id,
        )
    entries = entries_for_plan(conn, plan.plan_id)
    assert len(entries) == 2
    assert all(e.state == "planned" for e in entries)

    msg = refuse_apply_without_approval(conn, plan.plan_id)
    assert "approved" in msg
    assert "Nothing moved" in msg

    # Forging plan state without matching approval plan_hash → refuse (A3).
    conn.execute(
        "UPDATE assistant_plans SET state='approved' WHERE plan_id=?",
        (plan.plan_id,),
    )
    msg2 = refuse_apply_without_approval(conn, plan.plan_id)
    assert "Nothing moved" in msg2
    assert "plan_hash mismatch" in msg2 or "not enabled" in msg2

    # Proper approve + full list → still no apply executor in this build.
    from assistant.plans import approve_plan
    ok = approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=5000,
        full_list_viewed=True)
    assert ok.ok is True
    msg3 = refuse_apply_without_approval(conn, plan.plan_id)
    assert "not enabled" in msg3
    assert "Nothing moved" in msg3

    rt = ToolRuntime(conn)
    out = rt.execute("apply_moves", {"plan_id": plan.plan_id})
    assert out.ok is False
    assert out.payload.get("moved") is False


def test_egress_persists(conn):
    from assistant.egress import PersistentEgress
    led = PersistentEgress(conn, session_id="sess-test")
    led.add(provider="deepseek", model="m", item_ids=["a", "b"], bytes_out=12,
            question="where is cv?")
    rows = led.session_rows()
    assert len(rows) == 1
    assert rows[0]["item_ids"] == ["a", "b"]
    assert rows[0]["bytes"] == 12
    assert rows[0]["question"] == "where is cv?"
