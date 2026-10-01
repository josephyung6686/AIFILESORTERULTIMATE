"""Fixture mail and calendar stay on this machine. No body, no token, no network."""
from __future__ import annotations

import http.client
import io
import json
import sqlite3
from pathlib import Path

from database_agent.identity import hash_file
from items.identity import reconcile_tree
from items.mailbox import ingest_fixture, model_fields

import cli

BODY = "this body must not be stored"
DESCRIPTION = "this description must not be stored"
TOKEN = "refresh-token-must-not-be-stored"


def _forbid_network(monkeypatch):
    def boom(*_args, **_kwargs):
        raise AssertionError("network")

    monkeypatch.setattr(http.client.HTTPConnection, "request", boom)
    monkeypatch.setattr(http.client.HTTPSConnection, "request", boom)


def _library(conn, tmp_path: Path):
    root = tmp_path / "library"
    root.mkdir()
    notes = root / "notes.txt"
    notes.write_bytes(b"lab notes")
    secret = root / "secret.pem"
    secret.write_bytes(b"not a key")
    loose = root / "loose.txt"
    loose.write_bytes(b"no message points here")
    reconcile_tree(conn, root)
    return {
        "notes": hash_file(notes, materialized=True),
        "secret": hash_file(secret, materialized=True),
    }


def _fixture(hashes) -> dict:
    return {
        "refresh_token": TOKEN,
        "messages": [{
            "message_id": "msg-1",
            "thread_id": "thread-1",
            "internal_date": "2026-10-02T15:00:00+00:00",
            "from": "lab@example.com",
            "to": ["ada@example.com"],
            "subject": "Lab notes",
            "body": BODY,
            "attachments": [
                {"filename": "notes.txt", "sha256": hashes["notes"]},
                {"filename": "secret.pem", "sha256": hashes["secret"]},
            ],
        }, {
            "message_id": "msg-2",
            "thread_id": "thread-2",
            "internal_date": "2026-10-02T16:00:00+00:00",
            "from": "other@example.com",
            "to": ["ada@example.com"],
            "subject": "Unmatched",
            "body": BODY,
            "attachments": [{"filename": "missing.txt", "sha256": "a" * 64}],
        }],
        "events": [{
            "event_id": "evt-1",
            "calendar_id": "primary",
            "start": "2026-10-03T15:00:00+00:00",
            "end": "2026-10-03T16:00:00+00:00",
            "title": "Office hours",
            "status": "confirmed",
            "description": DESCRIPTION,
        }],
    }


def _text(conn) -> str:
    chunks = []
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    for (name,) in tables:
        columns = conn.execute(f"PRAGMA table_info({name})").fetchall()
        for column in columns:
            assert column[1] not in {
                "body", "description", "token", "refresh_token", "access_token"}
        for row in conn.execute(f"SELECT * FROM {name}"):
            chunks.append(" ".join("" if value is None else str(value) for value in row))
    return "\n".join(chunks)


def test_a_fixture_message_and_event_are_local_items_without_a_body(conn, tmp_path, monkeypatch):
    _forbid_network(monkeypatch)
    hashes = _library(conn, tmp_path)
    data = _fixture(hashes)
    mail = ingest_fixture(conn, data, kind="gmail")
    event = ingest_fixture(conn, data, kind="calendar")
    stored = _text(conn)
    assert BODY not in stored
    assert DESCRIPTION not in stored
    assert TOKEN not in stored
    assert "msg-1" in stored
    assert hashes["notes"] in stored
    assert "evt-1" in stored
    assert "Office hours" in stored
    assert mail["approved"] == 0
    assert event["approved"] == 0
    held = conn.execute(
        "SELECT typing_state FROM items WHERE item_type = 'email' AND display_label = ?",
        ("Lab notes",),
    ).fetchone()
    assert held["typing_state"] == "held"
    unmatched = conn.execute(
        "SELECT file_id, typing_state FROM items WHERE display_label = ?",
        ("Unmatched",),
    ).fetchone()
    assert unmatched["file_id"] is None
    assert unmatched["typing_state"] == "unplaced"
    email = conn.execute(
        "SELECT item_id FROM items WHERE display_label = ?",
        ("Lab notes",),
    ).fetchone()
    assert model_fields(conn, email["item_id"]) == {}
    approved = conn.execute(
        "SELECT COUNT(*) FROM relationships WHERE state = 'approved'"
    ).fetchone()[0]
    assert approved == 0


def test_sync_dry_run_stores_nothing_and_opens_no_socket(tmp_path, monkeypatch):
    _forbid_network(monkeypatch)
    out = io.StringIO()
    code = cli.main(["sync", "gmail", "--dry-run"], out=out)
    text = out.getvalue()
    assert code == 0, text
    assert "nothing was stored" in text
    assert "No network call was made" in text
    assert not list(Path.cwd().glob("database-agent-plan.sqlite"))
    fixture = tmp_path / "mail.json"
    fixture.write_text(json.dumps(_fixture({"notes": "abc", "secret": "def"})),
                       encoding="utf-8")
    preview = io.StringIO()
    code = cli.main(
        ["sync", "calendar", "--dry-run", "--fixture", str(fixture)], out=preview)
    printed = preview.getvalue()
    assert code == 0, printed
    assert "Would store: 1." in printed
    assert "event_id" in printed
    assert "description" in printed
    assert DESCRIPTION not in printed
    assert TOKEN not in printed
    database = tmp_path / "plan.sqlite"
    stored = io.StringIO()
    code = cli.main([
        "sync", "gmail", "--database", str(database), "--fixture", str(fixture),
    ], out=stored)
    assert code == 0, stored.getvalue()
    assert "Nothing was sent" in stored.getvalue()
    assert BODY not in stored.getvalue()
    conn = sqlite3.connect(database)
    try:
        dumped = " ".join(
            str(value) for row in conn.execute("SELECT * FROM item_headers")
            for value in row)
    finally:
        conn.close()
    assert BODY not in dumped
    assert TOKEN not in dumped
