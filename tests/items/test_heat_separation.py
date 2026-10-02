"""Heat: agent read_item must not inflate user_heat."""
from __future__ import annotations

from pathlib import Path

from assistant.tools import ToolRuntime
from items.heat import bump_user_heat, user_heat
from items.identity import reconcile_tree
from items.schema import create_items_schema


def test_agent_read_does_not_bump_user_heat(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "notes.txt").write_text("hello heat", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    item_id = conn.execute(
        "SELECT item_id FROM items WHERE display_label='notes.txt'"
    ).fetchone()["item_id"]

    # Seed evidence so read_item has a body
    conn.execute(
        "CREATE TABLE IF NOT EXISTS evidence ("
        "evidence_id TEXT PRIMARY KEY, file_id TEXT, raw_value TEXT, "
        "superseded_by TEXT)"
    )
    fid = conn.execute(
        "SELECT file_id FROM items WHERE item_id=?", (item_id,)
    ).fetchone()["file_id"]
    conn.execute(
        "INSERT INTO evidence VALUES ('e1', ?, 'hello heat body text', NULL)",
        (fid,),
    )

    rt = ToolRuntime(conn)
    # ToolRuntime should bump agent_touch only (wired below)
    out = rt.execute("read_item", {"item_id": item_id})
    assert out.ok is True
    assert user_heat(conn, item_id) == 0

    bump_user_heat(conn, item_id)
    assert user_heat(conn, item_id) == 1
