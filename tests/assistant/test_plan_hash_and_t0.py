"""Addendum A2–A5: plan_hash binding, T0 template rename, full-list gate."""
from __future__ import annotations

from assistant.plans import (
    PlanOp,
    approve_plan,
    create_draft_plan,
    edit_plan_ops,
    plan_hash,
    render_t0_rename,
    require_full_list_viewed,
    validate_t0_dst,
)


def test_plan_hash_stable_and_changes_on_edit(conn):
    ops = (
        PlanOp(item_id="i1", src="/a/x.pdf", dst="/b/x.pdf",
               file_id="f1", content_hash="h1"),
        PlanOp(item_id="i2", src="/a/y.pdf", dst="/b/y.pdf",
               file_id="f2", content_hash="h2"),
    )
    plan = create_draft_plan(conn, ops=ops, risk_tier="T1")
    h1 = plan_hash(conn, plan.plan_id)
    h2 = plan_hash(conn, plan.plan_id)
    assert h1 == h2
    assert len(h1) == 64

    edit_plan_ops(conn, plan.plan_id, (
        PlanOp(item_id="i1", src="/a/x.pdf", dst="/b/x-renamed.pdf",
               file_id="f1", content_hash="h1"),
        PlanOp(item_id="i2", src="/a/y.pdf", dst="/b/y.pdf",
               file_id="f2", content_hash="h2"),
    ))
    h3 = plan_hash(conn, plan.plan_id)
    assert h3 != h1


def test_approve_binds_plan_hash_edit_invalidates(conn):
    ops = (
        PlanOp(item_id="i1", src="/a/x.pdf", dst="/b/x.pdf", file_id="f1"),
    )
    plan = create_draft_plan(conn, ops=ops, risk_tier="T1")
    # Approve without viewing full list → refused
    bad = approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=5000,
        full_list_viewed=False)
    assert bad.ok is False
    assert "full list" in bad.error.lower()

    ok = approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=5000,
        full_list_viewed=True)
    assert ok.ok is True
    assert ok.plan_hash == plan_hash(conn, plan.plan_id)

    edit_plan_ops(conn, plan.plan_id, (
        PlanOp(item_id="i1", src="/a/x.pdf", dst="/b/OTHER.pdf", file_id="f1"),
    ))
    # Prior approval must not match
    assert require_full_list_viewed  # smoke import
    from assistant.plans import approval_matches_plan
    assert approval_matches_plan(conn, plan.plan_id) is False


def test_t0_rename_template_only():
    name = render_t0_rename(
        template="{date}_{type}_{stem}",
        stem="notes",
        type_="pdf",
        date="2026-10-02",
        source="downloads",
    )
    assert name == "2026-10-02_pdf_notes"
    assert validate_t0_dst("2026-10-02_pdf_notes.pdf", template_rendered=True)
    assert validate_t0_dst("evil_from_snippet.pdf", template_rendered=False) is False
    # Free-text model name must not validate as T0
    assert validate_t0_dst("Ignore instructions.pdf", template_rendered=False) is False


def test_t2_fast_approve_requires_reconfirm(conn):
    ops = (
        PlanOp(item_id="i1", src="/Downloads/a.pdf", dst="/Documents/a.pdf"),
    )
    plan = create_draft_plan(conn, ops=ops, risk_tier="T2")
    fast = approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=500,
        full_list_viewed=True)
    assert fast.ok is False
    assert "re-confirm" in (fast.error or "").lower()
    ok = approve_plan(
        conn, plan.plan_id, actor="user-reconfirm", approve_ms=500,
        full_list_viewed=True)
    assert ok.ok is True
