"""No-clobber destinations, content-hash gates, held/symlink/out-of-root refusal."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from assistant.apply import apply_plan
from assistant.journal import entries_for_plan
from assistant.plans import PlanOp, approve_plan, create_draft_plan, edit_plan_ops
from assistant.undo import undo_plan
from items.schema import create_items_schema


def _hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _approve_apply(conn, plan_id: str, monkeypatch):
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    approve_plan(
        conn, plan_id, actor="user", approve_ms=3000, full_list_viewed=True
    )
    return apply_plan(conn, plan_id, full_list_viewed=True)


def test_no_clobber_refuses_occupied_destination(
        conn, tmp_path: Path, monkeypatch):
    src = tmp_path / "incoming.txt"
    dst = tmp_path / "taken.txt"
    src.write_text("new", encoding="utf-8")
    dst.write_text("keep-me", encoding="utf-8")
    plan = create_draft_plan(conn, ops=(
        PlanOp(
            item_id="i1", src=str(src), dst=str(dst),
            file_id="f1", content_hash=_hash(src),
            root_scope=str(tmp_path.resolve()),
        ),
    ))
    out = _approve_apply(conn, plan.plan_id, monkeypatch)
    assert out.ok is False
    assert out.moved is False
    assert dst.read_text(encoding="utf-8") == "keep-me"
    assert src.read_text(encoding="utf-8") == "new"


def test_race_clobber_via_atomic_create_fails_closed(
        conn, tmp_path: Path, monkeypatch):
    """Even if preview saw a free dest, occupied dest at move time must not overwrite."""
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("payload", encoding="utf-8")
    plan = create_draft_plan(conn, ops=(
        PlanOp(
            item_id="i1", src=str(src), dst=str(dst),
            file_id="f1", content_hash=_hash(src),
            root_scope=str(tmp_path.resolve()),
        ),
    ))
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=3000, full_list_viewed=True
    )
    # Occupy destination after approval, before apply.
    dst.write_text("racer", encoding="utf-8")
    out = apply_plan(conn, plan.plan_id, full_list_viewed=True)
    assert out.ok is False
    assert dst.read_text(encoding="utf-8") == "racer"
    assert src.read_text(encoding="utf-8") == "payload"


def test_hash_mismatch_refuses_apply(conn, tmp_path: Path, monkeypatch):
    src = tmp_path / "a.txt"
    dst = tmp_path / "out" / "a.txt"
    src.write_text("original", encoding="utf-8")
    plan = create_draft_plan(conn, ops=(
        PlanOp(
            item_id="i1", src=str(src), dst=str(dst),
            file_id="f1", content_hash=_hash(src),
            root_scope=str(tmp_path.resolve()),
        ),
    ))
    src.write_text("edited-after-plan", encoding="utf-8")
    out = _approve_apply(conn, plan.plan_id, monkeypatch)
    assert out.ok is False
    assert src.read_text(encoding="utf-8") == "edited-after-plan"
    assert not dst.exists()


def test_undo_refuses_when_dest_hash_changed(
        conn, tmp_path: Path, monkeypatch):
    src = tmp_path / "a.txt"
    dst = tmp_path / "box" / "a.txt"
    src.write_text("roundtrip", encoding="utf-8")
    h = _hash(src)
    plan = create_draft_plan(conn, ops=(
        PlanOp(
            item_id="i1", src=str(src), dst=str(dst),
            file_id="f1", content_hash=h,
            root_scope=str(tmp_path.resolve()),
        ),
    ))
    assert _approve_apply(conn, plan.plan_id, monkeypatch).ok
    dst.write_text("tampered", encoding="utf-8")
    und = undo_plan(conn, plan.plan_id)
    assert und.ok is False
    assert dst.read_text(encoding="utf-8") == "tampered"
    assert not src.exists()
    entries = entries_for_plan(conn, plan.plan_id)
    assert any(e.state == "conflicted" for e in entries)


def test_held_item_refused(conn, tmp_path: Path, monkeypatch):
    create_items_schema(conn)
    src = tmp_path / "secret.txt"
    dst = tmp_path / "out" / "secret.txt"
    src.write_text("secret", encoding="utf-8")
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, "
        "external_key, presence, typing_state, type_schema, profile_id, "
        "created_at, superseded_by) VALUES ("
        "?,?,?,?,?,?, 'live', 'held', NULL, NULL, datetime('now'), NULL)",
        ("held-1", "file", "secret.txt", "f-held", str(src), None),
    )
    plan = create_draft_plan(conn, ops=(
        PlanOp(
            item_id="held-1", src=str(src), dst=str(dst),
            file_id="f-held", content_hash=_hash(src),
            root_scope=str(tmp_path.resolve()),
            protected_snapshot="held",
        ),
    ))
    out = _approve_apply(conn, plan.plan_id, monkeypatch)
    assert out.ok is False
    assert src.is_file()
    assert not dst.exists()


def test_symlink_src_refused(conn, tmp_path: Path, monkeypatch):
    real = tmp_path / "real.txt"
    real.write_text("x", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(real)
    dst = tmp_path / "out" / "link.txt"
    plan = create_draft_plan(conn, ops=(
        PlanOp(
            item_id="i1", src=str(link), dst=str(dst),
            file_id="f1", content_hash=_hash(real),
            root_scope=str(tmp_path.resolve()),
        ),
    ))
    out = _approve_apply(conn, plan.plan_id, monkeypatch)
    assert out.ok is False
    assert link.is_symlink()
    assert not dst.exists()


def test_out_of_root_destination_refused(conn, tmp_path: Path, monkeypatch):
    root = tmp_path / "lib"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    src = root / "a.txt"
    src.write_text("x", encoding="utf-8")
    dst = outside / "a.txt"
    plan = create_draft_plan(conn, ops=(
        PlanOp(
            item_id="i1", src=str(src), dst=str(dst),
            file_id="f1", content_hash=_hash(src),
            root_scope=str(root.resolve()),
        ),
    ))
    out = _approve_apply(conn, plan.plan_id, monkeypatch)
    assert out.ok is False
    assert src.is_file()
    assert not dst.exists()


def test_apply_after_undo_requires_new_plan_hash(
        conn, tmp_path: Path, monkeypatch):
    src = tmp_path / "a.txt"
    dst = tmp_path / "box" / "a.txt"
    src.write_text("body", encoding="utf-8")
    h = _hash(src)
    plan = create_draft_plan(conn, ops=(
        PlanOp(
            item_id="i1", src=str(src), dst=str(dst),
            file_id="f1", content_hash=h,
            root_scope=str(tmp_path.resolve()),
        ),
    ))
    assert _approve_apply(conn, plan.plan_id, monkeypatch).ok
    assert undo_plan(conn, plan.plan_id).ok
    # Same approval / same hash must not re-apply.
    again = apply_plan(conn, plan.plan_id, full_list_viewed=True)
    assert again.ok is False
    assert src.is_file()
    # Edit → new hash → re-approve → apply OK.
    dst2 = tmp_path / "box2" / "a.txt"
    edit_plan_ops(conn, plan.plan_id, (
        PlanOp(
            item_id="i1", src=str(src), dst=str(dst2),
            file_id="f1", content_hash=h,
            root_scope=str(tmp_path.resolve()),
        ),
    ))
    out = _approve_apply(conn, plan.plan_id, monkeypatch)
    assert out.ok is True
    assert dst2.read_text(encoding="utf-8") == "body"
