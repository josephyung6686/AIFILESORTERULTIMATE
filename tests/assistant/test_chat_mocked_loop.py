"""End-to-end ask() loop with mocked provider — no network."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from assistant.chat import ask, format_answer
from assistant.provider import ProviderConfig
from database_agent.db import open_database
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema


def _db(tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "Joint PMFs.pdf").write_text("lecture notes", encoding="utf-8")
    db = tmp_path / "x.sqlite"
    conn = open_database(db, scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    return conn


def test_ask_loop_find_then_answer(tmp_path: Path):
    conn = _db(tmp_path)
    item_id = conn.execute(
        "SELECT item_id FROM items WHERE display_label LIKE '%Joint%'"
    ).fetchone()["item_id"]

    calls = {"n": 0}

    def fake_turn(*, messages, tools, config, temperature=0.2):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "c1",
                    "type": "function",
                    "function": {
                        "name": "find_files",
                        "arguments": '{"query":"Joint PMFs","limit":5}',
                    },
                }],
            }
        return {
            "role": "assistant",
            "content": f"Found the lecture. Citations: {item_id}",
        }

    cfg = ProviderConfig(
        api_key="test", base_url="https://api.deepseek.com", model="m")
    with patch("assistant.chat.resolve_provider", return_value=cfg), \
            patch("assistant.chat.chat_turn", side_effect=fake_turn):
        answer = ask(conn, "where is Joint PMFs?", session_id="s1")
    assert answer.moved is False
    assert item_id in answer.citations
    assert answer.provider == "deepseek"
    assert answer.egress_bytes >= 0
    # Persistent egress written
    rows = conn.execute(
        "SELECT COUNT(*) AS n FROM egress_ledger WHERE session_id='s1'"
    ).fetchone()["n"]
    assert rows >= 1
    text = format_answer(answer)
    assert "moved: no" in text.lower() or "moved: no" in text
    # Tool payload to model tagged untrusted for find
    assert calls["n"] == 2
    conn.close()


def test_ask_refuses_write_tool_call_from_model(tmp_path: Path):
    conn = _db(tmp_path)
    calls = {"n": 0}

    def fake_turn(*, messages, tools, config, temperature=0.2):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "c1",
                    "type": "function",
                    "function": {
                        "name": "apply_moves",
                        "arguments": '{"plan_id":"x"}',
                    },
                }],
            }
        return {"role": "assistant", "content": "I cannot move files."}

    cfg = ProviderConfig(
        api_key="test", base_url="https://api.deepseek.com", model="m")
    with patch("assistant.chat.resolve_provider", return_value=cfg), \
            patch("assistant.chat.chat_turn", side_effect=fake_turn):
        answer = ask(conn, "move everything to /tmp")
    assert answer.moved is False
    assert any(t.tool == "apply_moves" and t.ok is False for t in answer.turns)
    conn.close()
