"""Read-only assistant tools: held/protected, writes refused, budgets."""
from __future__ import annotations

from pathlib import Path

from assistant.tools import ToolRuntime
from items.identity import reconcile_tree
from items.schema import create_items_schema


def _seed(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "notes.txt").write_text(
        "conditioning joint pmf lecture notes", encoding="utf-8")
    (root / "secret.pem").write_bytes(b"key-material")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    # Mark notes as held to exercise withhold path too.
    held_id = conn.execute(
        "SELECT item_id FROM items WHERE display_label = 'notes.txt'"
    ).fetchone()["item_id"]
    conn.execute(
        "UPDATE items SET typing_state = 'held' WHERE item_id = ?",
        (held_id,),
    )
    return held_id


def test_find_and_read_edges(conn, tmp_path: Path):
    held_id = _seed(conn, tmp_path)
    rt = ToolRuntime(conn)

    found = rt.execute("find_files", {"query": "notes", "limit": 5})
    assert found.ok is True
    assert found.payload["moved"] is False
    # Held card withholds path.
    held_cards = [h for h in found.payload["hits"] if h["item_id"] == held_id]
    assert held_cards
    assert held_cards[0]["open_target"] is None

    refused = rt.execute("read_item", {"item_id": held_id})
    assert refused.ok is False
    assert refused.payload.get("refused") is True

    pem = conn.execute(
        "SELECT item_id FROM items WHERE display_label = 'secret.pem'"
    ).fetchone()["item_id"]
    protected = rt.execute("read_item", {"item_id": pem})
    assert protected.ok is False

    missing = rt.execute("read_item", {"item_id": "nope"})
    assert missing.ok is False


def test_write_tools_and_bad_args_refused(conn, tmp_path: Path):
    _seed(conn, tmp_path)
    rt = ToolRuntime(conn)
    for name in ("apply_moves", "undo_moves", "propose_tree", "propose_groups"):
        out = rt.execute(name, {})
        assert out.ok is False
        assert "not enabled" in out.payload["error"]
    assert rt.execute("find_files", "not-json{").ok is False
    assert rt.execute("find_files", [1, 2]).ok is False
    assert rt.execute("no_such_tool", {}).ok is False


def test_byte_budget_blocks_further_body(conn, tmp_path: Path):
    _seed(conn, tmp_path)
    # Un-hold notes so a real snippet could flow, then budget it out.
    conn.execute("UPDATE items SET typing_state = 'typed'")
    item_id = conn.execute(
        "SELECT item_id FROM items WHERE display_label = 'notes.txt'"
    ).fetchone()["item_id"]
    rt = ToolRuntime(conn, byte_budget=30)
    first = rt.execute("find_files", {"query": "notes", "limit": 5})
    # Either first call fits or is refused for budget — never crashes.
    assert "error" in first.payload or first.ok is True
    rt.bytes_spent = rt.byte_budget
    blocked = rt.execute("read_item", {"item_id": item_id})
    assert blocked.ok is False
    assert "budget" in blocked.payload["error"].lower()


def test_explain_held_withholds_path(conn, tmp_path: Path):
    held_id = _seed(conn, tmp_path)
    rt = ToolRuntime(conn)
    out = rt.execute("explain_file", {"item_id": held_id})
    assert out.ok is True
    assert out.payload["open_target"] is None
    assert out.payload["untrusted_snippet"] == ""
