"""L2/L3 playbook Markdown rollups."""
from __future__ import annotations

from pathlib import Path

from assistant.memory_l0 import capture_accept_correction
from assistant.memory_v1 import add_rule
from assistant.memory_v2 import add_atom
from assistant.playbook_rollups import write_rollups
from items.identity import reconcile_tree


def test_write_rollups(conn, tmp_path: Path):
    add_rule(conn, rule_text="PDFs → Coursework", kind="route")
    # Atoms require resolvable, version-bound L0 provenance.
    root = tmp_path / "files"
    root.mkdir()
    (root / "tax.txt").write_text("tax")
    reconcile_tree(conn, root)
    item_id = conn.execute("SELECT item_id FROM items").fetchone()[0]
    diff = capture_accept_correction(
        conn, ai_proposal={"route": "Finance/Tax"}, item_ids=[item_id])
    add_atom(conn, claim="tax → Finance/Tax", source_ids=[diff.diff_id])
    out = write_rollups(conn, root=tmp_path / "playbook")
    assert out["ok"] is True
    assert (tmp_path / "playbook" / "clusters" / "route.md").is_file()
    assert (tmp_path / "playbook" / "profiles" / "default.md").is_file()
    text = (tmp_path / "playbook" / "profiles" / "default.md").read_text()
    assert "PDFs" in text
    assert "tax" in text
