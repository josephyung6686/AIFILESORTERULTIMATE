"""Round-3 engine follow-ups: reads that never commit, the app's opening,
plain words, encrypted databases, protection before organising, freeze."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from assistant import events as ev
from assistant.session import Session
from database_agent.db import open_database


def _uncommitted_row_survives_rollback(conn, read) -> bool:
    conn.execute("CREATE TABLE IF NOT EXISTS probe (v TEXT)")
    conn.execute("BEGIN")
    conn.execute("INSERT INTO probe VALUES ('x')")
    read(conn)
    conn.execute("ROLLBACK")
    return conn.execute("SELECT COUNT(*) FROM probe").fetchone()[0] == 1


def test_reading_a_setting_never_commits_the_callers_transaction(conn):
    from assistant.engine_tools import get_setting
    assert not _uncommitted_row_survives_rollback(
        conn, lambda c: get_setting(c, "permission_level", "1"))


def test_reading_recent_conversations_never_commits(conn):
    from assistant.conversation_store import recent
    assert not _uncommitted_row_survives_rollback(conn, recent)
