from __future__ import annotations

import json
import sqlite3

import pytest

from database_agent.privacy import (
    LocalAuthRequired,
    create_privacy_schema,
    encryption_capability,
    export_database,
    held_item_fields,
    delete_item,
)
from items.schema import create_items_schema


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_items_schema(conn)
    create_privacy_schema(conn)
    return conn


def test_plain_sqlite_is_reported_as_unencrypted():
    report = encryption_capability(sqlite3.connect(":memory:"))
    assert report.encrypted is False
    assert report.mechanism == "plain-sqlite"
    assert report.warning


def test_held_item_refuses_without_local_auth_and_allows_with_auth():
    conn = _db()
    conn.execute(
        "INSERT INTO items(item_id,item_type,display_label,presence,typing_state,"
        "created_at,freshness_state) VALUES ('x','file','secret','live','held',"
        "'now','clean')"
    )
    with pytest.raises(LocalAuthRequired):
        held_item_fields(conn, "x")
    assert held_item_fields(conn, "x", authenticate=lambda: True)["item_id"] == "x"


def test_export_excludes_secret_columns_and_is_audited(tmp_path):
    conn = _db()
    conn.execute("CREATE TABLE secret_fixture (body TEXT, access_token TEXT, label TEXT)")
    conn.execute("INSERT INTO secret_fixture VALUES ('body','token','ok')")
    destination = tmp_path / "export.json"
    result = export_database(conn, destination, user_id="u")
    payload = json.loads(destination.read_text())
    assert result["audited"] is True
    rendered = json.dumps(payload)
    assert "body" not in rendered
    assert "token" not in rendered
    assert conn.execute("SELECT action FROM privacy_audit_events").fetchone()[0] == "export"


def test_delete_item_removes_index_tables_and_is_audited():
    conn = _db()
    conn.execute("INSERT INTO items(item_id,item_type,display_label,presence,typing_state,created_at,freshness_state) VALUES ('x','file','x','live','unplaced','now','clean')")
    conn.execute("CREATE VIRTUAL TABLE item_fts USING fts5(item_id, display_label, text)")
    conn.execute("INSERT INTO item_fts VALUES ('x','x','x')")
    conn.execute("CREATE TABLE item_chunks (chunk_id TEXT, item_id TEXT)")
    conn.execute("INSERT INTO item_chunks VALUES ('c','x')")
    delete_item(conn, "x", user_id="u")
    assert conn.execute("SELECT 1 FROM items WHERE item_id='x'").fetchone() is None
    assert conn.execute("SELECT 1 FROM item_fts WHERE item_id='x'").fetchone() is None
    assert conn.execute("SELECT 1 FROM item_chunks WHERE item_id='x'").fetchone() is None
    assert conn.execute("SELECT action FROM privacy_audit_events").fetchone()[0] == "delete"
