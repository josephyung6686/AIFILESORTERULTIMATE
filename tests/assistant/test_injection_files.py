"""Load on-disk injection corpus and prove writes stay refused."""
from __future__ import annotations

from pathlib import Path

from assistant.tools import ToolRuntime
from items.identity import reconcile_tree
from items.schema import create_items_schema

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "injection"
WRITE = (
    "apply_moves", "undo_moves", "propose_tree", "accept_link",
    "freeze", "propose_groups",
)


def test_disk_fixtures_exist_and_never_enable_writes(conn, tmp_path: Path):
    assert FIX.is_dir()
    files = list(FIX.iterdir())
    assert len(files) >= 8
    root = tmp_path / "lib"
    root.mkdir()
    for src in files:
        if src.is_file():
            (root / src.name).write_bytes(src.read_bytes())
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rt = ToolRuntime(conn)
    # Read the INJ-01 body
    row = conn.execute(
        "SELECT item_id FROM items WHERE display_label LIKE 'INJ-01%'"
    ).fetchone()
    assert row is not None
    read = rt.execute("read_item", {"item_id": row["item_id"]})
    # May be empty snippet without evidence table — still must not enable writes
    for name in WRITE:
        out = rt.execute(name, {"from_fixture": "INJ-01"})
        assert out.ok is False
        assert out.payload.get("moved") is False
