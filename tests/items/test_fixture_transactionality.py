from __future__ import annotations

import sqlite3

import pytest

from items.mailbox import MailboxRefused, ingest_fixture
from items.schema import create_items_schema


def test_fixture_rejects_bad_row_without_storing_previous_rows():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_items_schema(conn)
    fixture = {"messages": [{"message_id": "good", "subject": "ok"}, {"subject": "bad"}]}
    with pytest.raises(MailboxRefused):
        ingest_fixture(conn, fixture, kind="gmail")
    assert conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0


def test_fixture_rejects_non_object_rows_without_partial_write():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_items_schema(conn)
    with pytest.raises(MailboxRefused):
        ingest_fixture(conn, {"events": [{"event_id": "a"}, "bad"]}, kind="calendar")
    assert conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0
