"""L2/L3 playbook Markdown rollups."""
from __future__ import annotations

from pathlib import Path

from assistant.memory_v1 import add_rule
from assistant.memory_v2 import add_atom
from assistant.playbook_rollups import write_rollups


def test_write_rollups(conn, tmp_path: Path):
    add_rule(conn, rule_text="PDFs → Coursework", kind="route")
    add_atom(conn, claim="tax → Finance/Tax", source_ids=["d1"])
    out = write_rollups(conn, root=tmp_path / "playbook")
    assert out["ok"] is True
    assert (tmp_path / "playbook" / "clusters" / "route.md").is_file()
    assert (tmp_path / "playbook" / "profiles" / "default.md").is_file()
    text = (tmp_path / "playbook" / "profiles" / "default.md").read_text()
    assert "PDFs" in text
    assert "tax" in text
