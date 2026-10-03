"""Held/protected paths and bodies never enter egress ledger payloads."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from assistant.chat import ask
from assistant.egress import PersistentEgress
from assistant.provider import ProviderConfig
from assistant.tools import ToolRuntime
from database_agent.db import open_database
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema


def _seed(tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "open.txt").write_text("public notes", encoding="utf-8")
    (root / "secret.pem").write_bytes(b"KEYMATERIAL")
    (root / "tax.pdf").write_text("SSN 000-00-0000", encoding="utf-8")
    db = tmp_path / "t.sqlite"
    conn = open_database(db, scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    conn.execute(
        "UPDATE items SET typing_state='held' "
        "WHERE display_label IN ('tax.pdf')"
    )
    # evidence for open file
    conn.execute(
        "CREATE TABLE IF NOT EXISTS evidence ("
        "evidence_id TEXT PRIMARY KEY, file_id TEXT, raw_value TEXT, "
        "superseded_by TEXT)"
    )
    for label, text in (("open.txt", "public notes body"),):
        fid = conn.execute(
            "SELECT file_id FROM items WHERE display_label=?", (label,)
        ).fetchone()["file_id"]
        conn.execute(
            "INSERT INTO evidence VALUES (?, ?, ?, NULL)",
            (f"e-{label}", fid, text),
        )
    rebuild_fts(conn)
    conn.commit()
    return conn


def test_held_read_refused_and_find_withholds_path(tmp_path: Path):
    conn = _seed(tmp_path)
    rt = ToolRuntime(conn)
    held = conn.execute(
        "SELECT item_id, open_target FROM items WHERE display_label='tax.pdf'"
    ).fetchone()
    pem = conn.execute(
        "SELECT item_id FROM items WHERE display_label='secret.pem'"
    ).fetchone()["item_id"]

    found = rt.execute("find_files", {"query": "tax", "limit": 5})
    # Spec §3: the model gets a count line; no name, path or id.
    blob = json.dumps(found.payload)
    assert held["item_id"] not in blob and "tax.pdf" not in blob
    assert held["open_target"] not in blob
    assert "protected file" in found.payload["protected"]
    assert held["item_id"] in rt.protected_hits

    assert rt.execute("read_item", {"item_id": held["item_id"]}).ok is False
    assert rt.execute("read_item", {"item_id": pem}).ok is False
    conn.close()


def test_egress_ledger_never_stores_held_body(tmp_path: Path):
    conn = _seed(tmp_path)
    held_id = conn.execute(
        "SELECT item_id FROM items WHERE display_label='tax.pdf'"
    ).fetchone()["item_id"]
    open_id = conn.execute(
        "SELECT item_id FROM items WHERE display_label='open.txt'"
    ).fetchone()["item_id"]

    calls = {"n": 0}

    def fake_turn(*, messages, tools, config, temperature=0.2):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "c1",
                        "type": "function",
                        "function": {
                            "name": "read_item",
                            "arguments": json.dumps({"item_id": held_id}),
                        },
                    },
                    {
                        "id": "c2",
                        "type": "function",
                        "function": {
                            "name": "read_item",
                            "arguments": json.dumps({"item_id": open_id}),
                        },
                    },
                ],
            }
        # Inspect tool messages — held must not carry snippet
        for m in messages:
            if m.get("role") == "tool":
                blob = m.get("content") or ""
                assert "SSN" not in blob
                assert "000-00-0000" not in blob
        return {"role": "assistant", "content": "Held exists; open notes cited."}

    cfg = ProviderConfig(
        api_key="t", base_url="https://api.deepseek.com", model="m",
        provider="deepseek")
    with patch("assistant.chat.resolve_provider", return_value=cfg), \
            patch("assistant.chat.chat_turn", side_effect=fake_turn):
        answer = ask(conn, "what is in tax?", session_id="held-sess")
    assert answer.moved is False
    # Ledger rows must not contain held body text
    for row in conn.execute(
        "SELECT item_ids_json, question FROM egress_ledger "
        "WHERE session_id='held-sess'"
    ):
        assert "SSN" not in (row["question"] or "")
        assert "000-00" not in (row["item_ids_json"] or "")
    # Held read failed → should not be cited as open body
    assert "SSN" not in answer.text
    conn.close()
