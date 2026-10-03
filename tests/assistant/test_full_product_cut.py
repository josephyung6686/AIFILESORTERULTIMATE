"""Full product cut: truth loop, grounding, held-local, gaps, connectors."""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from assistant.apply import apply_plan
from assistant.gaps import list_gaps
from assistant.plans import PlanOp, approve_plan, create_draft_plan
from assistant.session_surface import note_surfaced, surfaced_ids
from assistant.tools import ToolRuntime
from assistant.undo import undo_plan
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema


def _hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_apply_updates_items_open_target(conn, tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ASSISTANT_ENABLE_APPLY", "1")
    lib = tmp_path / "lib"
    lib.mkdir()
    src = lib / "essay.txt"
    src.write_text("body", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, lib)
    row = conn.execute(
        "SELECT item_id, open_target, file_id FROM items "
        "WHERE display_label='essay.txt'"
    ).fetchone()
    assert row is not None
    dst = tmp_path / "filed" / "essay-renamed.txt"
    plan = create_draft_plan(conn, ops=(
        PlanOp(
            item_id=row["item_id"], src=row["open_target"],
            dst=str(dst), file_id=row["file_id"],
            content_hash=_hash(src),
        ),
    ))
    approve_plan(
        conn, plan.plan_id, actor="user", approve_ms=3000,
        full_list_viewed=True)
    out = apply_plan(conn, plan.plan_id, full_list_viewed=True)
    assert out.ok and out.moved
    updated = conn.execute(
        "SELECT open_target, display_label FROM items WHERE item_id=?",
        (row["item_id"],),
    ).fetchone()
    assert Path(updated["open_target"]) == dst.resolve()
    assert updated["display_label"] == "essay-renamed.txt"
    undo = undo_plan(conn, plan.plan_id)
    assert undo.ok
    back = conn.execute(
        "SELECT open_target, display_label FROM items WHERE item_id=?",
        (row["item_id"],),
    ).fetchone()
    assert Path(back["open_target"]).name == "essay.txt"


def test_grounded_plan_requires_surface(conn, tmp_path: Path):
    src = tmp_path / "a.txt"
    src.write_text("x")
    with pytest.raises(PermissionError, match="ungrounded"):
        create_draft_plan(
            conn,
            ops=(PlanOp(
                item_id="never-found", src=str(src),
                dst=str(tmp_path / "b.txt")),),
            require_grounded=True,
        )
    note_surfaced(conn, ["never-found"], source="find")
    plan = create_draft_plan(
        conn,
        ops=(PlanOp(
            item_id="never-found", src=str(src),
            dst=str(tmp_path / "b.txt")),),
        require_grounded=True,
    )
    assert plan.plan_id
    assert "never-found" in surfaced_ids(conn)


def test_find_surfaces_for_grounding(conn, tmp_path: Path):
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "Joint PMFs.pdf").write_bytes(b"%PDF")
    create_items_schema(conn)
    reconcile_tree(conn, lib)
    rebuild_fts(conn)
    rt = ToolRuntime(conn)
    out = rt.execute("find_files", {"query": "Joint", "limit": 5})
    assert out.ok
    ids = surfaced_ids(conn)
    assert ids


def test_held_body_cloud_vs_local(conn, tmp_path: Path):
    create_items_schema(conn)
    item_id = "held-1"
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, "
        "external_key, presence, typing_state, type_schema, profile_id, "
        "created_at, superseded_by) VALUES ("
        "?,?,?,?,?,?, 'live', 'held', NULL, NULL, datetime('now'), NULL)",
        (item_id, "file", "secret.pdf", "f1", str(tmp_path / "secret.pdf"),
         None),
    )
    cloud = ToolRuntime(conn, allow_held_body=False)
    refused = cloud.execute("read_item", {"item_id": item_id})
    assert refused.ok is False
    assert refused.payload.get("refused")
    local = ToolRuntime(conn, allow_held_body=True)
    # May still have empty snippet without evidence — but must not refuse held.
    allowed = local.execute("read_item", {"item_id": item_id})
    assert allowed.payload.get("refused") is not True
    assert allowed.payload.get("held_body_via_local") is True


def test_list_gaps_and_connectors_disabled(conn, tmp_path: Path):
    create_items_schema(conn)
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, "
        "external_key, presence, typing_state, type_schema, profile_id, "
        "created_at, superseded_by) VALUES ("
        "?,?,?,?,NULL,NULL,'live','unplaced',NULL,NULL,datetime('now'),NULL)",
        ("g1", "file", "loose.txt", None),
    )
    gaps = list_gaps(conn, limit=10)
    assert any(g["kind"] == "typing" for g in gaps["gaps"])
    rt = ToolRuntime(conn)
    rt.execute("request_tools", {"group": "connectors"})
    mail = rt.execute("sync_mail", {})
    assert mail.ok is False
    assert mail.payload.get("disabled") is True
    assert "scratched" in (mail.payload.get("error") or "").lower()
    gaps_tool = rt.execute("list_gaps", {"limit": 10})
    assert gaps_tool.ok
