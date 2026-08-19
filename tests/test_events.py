import sqlite3

import pytest

from database_agent.db import create_schema
from database_agent.events import CORRECTION_FIELDS, EVENT_FIELDS, append_event


def _minimal(**overrides):
    row = dict(
        event_type="discovery", file_id="f1", content_hash="abc",
        subsystem="P3", component_version="p3-fixture",
        observed_at="2026-08-19T00:00:00+00:00", explanation="fixture",
    )
    row.update(overrides)
    return row


def test_there_are_exactly_eleven_event_fields():
    # §8.2's event record, MINOR 1. The §8.7 columns are separate and do not count.
    assert len(EVENT_FIELDS) == 11
    assert not set(EVENT_FIELDS) & set(CORRECTION_FIELDS)


def test_event_carries_the_eleven_fields(conn):
    create_schema(conn)
    event_id = append_event(conn, **_minimal())
    row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    for field in EVENT_FIELDS:
        assert field in row.keys()
    # "where applicable" fields legitimately empty (Done-means 7) ...
    assert row["old_path"] is None
    assert row["new_path"] is None
    assert row["prompt_fingerprint"] is None
    assert row["user_id"] is None
    # ... and every other field populated. component_version is not optional.
    for field in EVENT_FIELDS:
        if field in ("old_path", "new_path", "prompt_fingerprint", "user_id"):
            continue
        assert row[field] is not None, f"Done-means 7: {field} must be populated"


def test_update_against_events_fails(conn):
    create_schema(conn)
    append_event(conn, **_minimal())
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE events SET explanation = 'rewritten'")


def test_delete_against_events_fails(conn):
    create_schema(conn)
    append_event(conn, **_minimal())
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM events")


def test_a_correction_is_a_new_event_not_an_edit(conn):
    create_schema(conn)
    append_event(conn, **_minimal(explanation="first"))
    append_event(conn, **_minimal(explanation="corrected"))
    rows = conn.execute("SELECT explanation FROM events ORDER BY event_id").fetchall()
    assert [r["explanation"] for r in rows] == ["first", "corrected"]
