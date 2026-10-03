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


def _events(out) -> list[dict]:
    return [json.loads(line) for line in out.getvalue().splitlines()]


def test_the_app_is_greeted_without_sending_an_action(conn):
    import io
    from assistant.terminal import run_events
    out = io.StringIO()
    run_events(conn, stdin=io.StringIO(""), stdout=out,
               provider_turn=lambda *a, **k: None)
    events = _events(out)
    assert events and "which folder" in events[-1]["text"].lower()


def test_an_extra_open_action_is_harmless(conn):
    import io
    from assistant.terminal import run_events
    out = io.StringIO()
    run_events(conn, stdin=io.StringIO(json.dumps({"action": "open"}) + "\n"),
               stdout=out, provider_turn=lambda *a, **k: None)
    events = _events(out)
    asked = [e for e in events if "which folder" in e.get("text", "").lower()]
    assert len(asked) == 1
    assert not [e for e in events if e["type"] == "error"]
