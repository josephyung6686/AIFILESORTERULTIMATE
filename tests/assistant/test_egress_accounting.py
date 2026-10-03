"""Egress bytes from serialized envelopes; one ledger row per provider request."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from assistant.chat import ask
from assistant.egress import PersistentEgress
from assistant.policy import classify_egress, envelope_bytes, is_loopback_url
from assistant.provider import ProviderConfig
from database_agent.db import open_database
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema


def _db(tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_text("hello", encoding="utf-8")
    db = tmp_path / "t.sqlite"
    conn = open_database(db, scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    return conn


def test_envelope_bytes_from_serialized_payload():
    req = {"messages": [{"role": "user", "content": "hi"}], "tools": []}
    resp = {"role": "assistant", "content": "ok"}
    assert envelope_bytes(req) == len(
        json.dumps(req, ensure_ascii=False).encode("utf-8"))
    assert envelope_bytes(resp) > 0


def test_one_ledger_row_per_provider_request(tmp_path: Path):
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
                        "name": "find_files",
                        "arguments": '{"query":"a","limit":3}',
                    },
                }],
            }
        return {"role": "assistant", "content": "Found it."}

    cfg = ProviderConfig(
        api_key="t", base_url="https://api.deepseek.com", model="m",
        provider="deepseek")
    with patch("assistant.chat.resolve_provider", return_value=cfg), \
            patch("assistant.chat.chat_turn", side_effect=fake_turn):
        answer = ask(conn, "where is a?", session_id="acct-1")

    rows = conn.execute(
        "SELECT bytes FROM egress_ledger WHERE session_id='acct-1' "
        "ORDER BY ts"
    ).fetchall()
    # Exactly one row per provider round (tool round + final) — not per tool.
    assert len(rows) == 2
    assert all(r["bytes"] > 0 for r in rows)
    assert answer.egress_bytes == sum(r["bytes"] for r in rows)
    # Session summary derives from rows
    led = PersistentEgress(conn, session_id="acct-1")
    # new object won't have in-memory rows; total from DB:
    assert led.session_summary()["request_count"] == 2
    assert led.session_summary()["total_bytes"] == answer.egress_bytes
    conn.close()


def test_add_provider_request_uses_envelope_sizes(conn):
    led = PersistentEgress(conn, session_id="env-1")
    req = {"messages": [{"role": "user", "content": "q"}], "tools": [{"a": 1}]}
    resp = {"role": "assistant", "content": "answer text"}
    row = led.add_provider_request(
        provider="deepseek",
        model="m",
        request_envelope=req,
        response_envelope=resp,
        item_ids=["i1"],
        question="q",
        egress_class="cloud",
    )
    assert row.bytes == envelope_bytes(req) + envelope_bytes(resp)
    assert row.bytes_in == envelope_bytes(req)
    assert row.bytes_out == envelope_bytes(resp)
    assert led.total_bytes() == row.bytes


def test_classify_egress_local_vs_cloud():
    assert is_loopback_url("http://127.0.0.1:11434/v1")
    assert is_loopback_url("http://localhost:8080")
    assert not is_loopback_url("https://api.together.xyz/v1")
    assert classify_egress(provider="deepseek") == "cloud"
    assert classify_egress(
        base_url="http://127.0.0.1:11434/v1", local_only=True) == "local"
    assert classify_egress(
        base_url="https://api.together.xyz/v1", local_only=True) == "cloud"
