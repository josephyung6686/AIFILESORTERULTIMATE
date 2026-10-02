"""Hint is advisory only — never gates tools."""
from __future__ import annotations

from assistant.model_hint import hint_for_question
from assistant.tools import ToolRuntime


def test_hint_does_not_block_find_tools(conn):
    from items.schema import create_items_schema
    create_items_schema(conn)
    h = hint_for_question("please organize my Downloads")
    assert h.tier == "frontier"
    assert h.preload_group == "organize_propose"
    # Tools still work regardless of hint
    rt = ToolRuntime(conn)
    out = rt.execute("find_files", {"query": "x", "limit": 3})
    assert out.ok is True
    assert out.payload["moved"] is False


def test_find_hint_is_fast():
    h = hint_for_question("where is my resume?")
    assert h.tier == "fast"
    assert h.preload_group is None
