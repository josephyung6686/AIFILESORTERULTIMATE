"""Document text is read after the fast index, and judged before it is searchable."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import docx

from database_agent.db import open_database
from items.file_identity import item_is_sensitive
from items.hot_index import find_files
from items.indexing import counts, index_folder, read_document_text
from test_indexing_sensitivity import text_pdf


def _corpus(tmp_path: Path) -> Path:
    root = tmp_path / "home"
    root.mkdir()
    document = docx.Document()
    document.add_paragraph("Fundraiser approval for the spring bake sale")
    document.save(root / "club_letter.docx")
    (root / "club_form.pdf").write_bytes(
        text_pdf("Fundraiser approval signed by the treasurer"))
    (root / "scan_0042.pdf").write_bytes(
        text_pdf("Hong Kong Identity Card HKID A123456(3)"))
    return root


def _label(conn, item_id: str) -> str:
    return conn.execute("SELECT display_label FROM items WHERE item_id = ?",
                        (item_id,)).fetchone()["display_label"]


def test_document_text_becomes_searchable_after_reading(tmp_path):
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, _corpus(tmp_path))

    before = find_files(conn, "club", limit=5).hits
    assert before and all(h.matched_by == "name" for h in before)
    assert not find_files(conn, "fundraiser approval", limit=5).hits
    assert counts(conn).unread_documents == 3

    seen = []
    read = read_document_text(conn, on_progress=lambda s, d, t: seen.append(
        (s, d, t)))

    assert read == 3
    assert seen[-1] == ("read", 3, 3)
    assert counts(conn).unread_documents == 0
    found = {_label(conn, h.item_id): h
             for h in find_files(conn, "fundraiser approval", limit=5).hits}
    assert {"club_letter.docx", "club_form.pdf"} <= set(found)
    assert found["club_form.pdf"].matched_by == "content"


def test_limit_reads_only_that_many(tmp_path):
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, _corpus(tmp_path))
    assert read_document_text(conn, limit=1) == 1
    assert counts(conn).unread_documents == 2


def test_an_id_card_is_protected_before_its_text_is_searchable(tmp_path):
    from assistant.chat import ask
    from assistant.provider import ProviderConfig

    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, _corpus(tmp_path))
    card = conn.execute("SELECT item_id FROM items WHERE display_label = ?",
                        ("scan_0042.pdf",)).fetchone()["item_id"]
    assert not item_is_sensitive(conn, card)

    read_document_text(conn)

    assert item_is_sensitive(conn, card)
    sent: list[str] = []

    def fake_turn(*, messages, tools, config, temperature=0.2):
        # What the tools returned: the model's own query is not file content.
        sent.append(json.dumps([m for m in messages if m["role"] == "tool"]))
        if len(sent) == 1:
            return {"role": "assistant", "content": None, "tool_calls": [
                {"id": "c1", "type": "function", "function": {
                    "name": "find_files",
                    "arguments": json.dumps({"query": "A123456", "limit": 5})}},
                {"id": "c2", "type": "function", "function": {
                    "name": "read_item",
                    "arguments": json.dumps({"item_id": card})}},
            ]}
        return {"role": "assistant", "content": "One protected file matched."}

    cfg = ProviderConfig(api_key="t", base_url="https://api.deepseek.com",
                         model="m", provider="deepseek")
    with patch("assistant.chat.resolve_provider", return_value=cfg), \
            patch("assistant.chat.chat_turn", side_effect=fake_turn):
        ask(conn, "what is my id number?", session_id="id-sess")
    assert len(sent) == 2 and "find_files" not in sent[0] and sent[1] != "[]"
    assert not any("A123456" in envelope for envelope in sent)


def test_an_edited_file_is_owed_a_reading_and_its_old_text_stops_matching(
        tmp_path):
    import os
    import time

    from items.refresh import refresh_index

    root = tmp_path / "home"
    root.mkdir()
    note = root / "essay.txt"
    note.write_text("alpha alpha alpha", encoding="utf-8")
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, root)
    read_document_text(conn)
    assert [h.matched_by for h in find_files(conn, "alpha", limit=5).hits] \
        == ["content"]
    assert counts(conn).unread_documents == 0

    note.write_text("beta beta beta", encoding="utf-8")
    later = time.time() + 5
    os.utime(note, (later, later))
    assert refresh_index(conn, roots=[root]).reindexed
    conn.commit()

    assert counts(conn).unread_documents == 1
    assert not find_files(conn, "alpha", limit=5).hits
    assert not [h for h in find_files(conn, "beta", limit=5).hits
                if h.matched_by == "content"]

    assert read_document_text(conn) == 1
    assert counts(conn).unread_documents == 0
    assert not find_files(conn, "alpha", limit=5).hits
    hits = find_files(conn, "beta", limit=5).hits
    assert [h.matched_by for h in hits] == ["content"]
