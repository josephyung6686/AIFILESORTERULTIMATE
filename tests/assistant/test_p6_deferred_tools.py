"""P6 deferred tools unlock after request_tools."""
from __future__ import annotations

from pathlib import Path

from assistant.tools import ToolRuntime
from items.identity import reconcile_tree
from items.schema import create_items_schema


def test_propose_tree_after_request(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.pdf").write_bytes(b"x")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rt = ToolRuntime(conn)
    locked = rt.execute("propose_tree", {})
    assert locked.ok is False
    req = rt.execute("request_tools", {"group": "organize_propose"})
    assert req.ok is True
    item_id = conn.execute("SELECT item_id FROM items").fetchone()[0]
    out = rt.execute("propose_tree", {"item_ids": [item_id]})
    assert out.ok is True
    assert out.payload.get("moved") is False
    assert out.payload["source"] == "type_buckets"
    shown = rt.execute("show_tree", {})
    assert shown.ok is True and shown.payload["plan_version"] is None


def test_apply_still_needs_env(conn, tmp_path: Path, monkeypatch):
    monkeypatch.delenv("ASSISTANT_ENABLE_APPLY", raising=False)
    rt = ToolRuntime(conn)
    rt.execute("request_tools", {"group": "organize_apply"})
    out = rt.execute("apply_moves", {"plan_id": "x", "full_list_viewed": True})
    assert out.ok is False
    assert out.payload.get("moved") is False
