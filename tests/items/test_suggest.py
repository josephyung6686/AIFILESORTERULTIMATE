"""Suggestions are local warnings. They do not approve a link or move a file."""
from __future__ import annotations

import http.client
import io
import uuid

from items.schema import create_items_schema
from items.suggest import proposals

import cli


def _counts(conn):
    items = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    links = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
    approved = conn.execute(
        "SELECT COUNT(*) FROM relationships WHERE state = 'approved'"
    ).fetchone()[0]
    return items, links, approved


def _course_and_event(conn):
    create_items_schema(conn)
    course = str(uuid.uuid4())
    event = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, external_key, "
        "presence, typing_state, type_schema, profile_id, created_at, superseded_by"
        ") VALUES (?, 'course', 'CHEM 101', NULL, NULL, NULL, 'live', 'typed', "
        "'academic', NULL, 't', NULL)",
        (course,),
    )
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, external_key, "
        "presence, typing_state, type_schema, profile_id, created_at, superseded_by"
        ") VALUES (?, 'event', 'Office hours', NULL, NULL, 'evt', 'live', "
        "'unplaced', NULL, NULL, 't', NULL)",
        (event,),
    )
    conn.execute(
        "INSERT INTO item_headers ("
        "item_id, kind, external_id, thread_id, account_label, happened_at, "
        "ended_at, address_from, address_to, calendar_id, status, "
        "attachment_names, attachment_hashes"
        ") VALUES (?, 'event', 'evt-1', '', 'local', '2026-10-03T15:00:00+00:00', "
        "'', '', '', 'primary', 'confirmed', '[]', '[]')",
        (event,),
    )
    return course, event


def test_a_course_with_an_event_and_no_file_is_one_warning(conn, tmp_path, monkeypatch):
    def boom(*_args, **_kwargs):
        raise AssertionError("network")

    monkeypatch.setattr(http.client.HTTPConnection, "request", boom)
    course, event = _course_and_event(conn)
    before = _counts(conn)
    rows = proposals(conn, now="2026-10-01T00:00:00+00:00")
    assert len(rows) == 1
    assert rows[0]["course"] == "CHEM 101"
    assert rows[0]["event"] == "Office hours"
    assert rows[0]["action"] == "none"
    assert _counts(conn) == before
    out = io.StringIO()
    code = cli.main([
        "suggest", "--database", str(tmp_path / "agent.sqlite"),
    ], out=out)
    text = out.getvalue()
    assert code == 0, text
    assert "CHEM 101" in text
    assert "Nothing was moved" in text
    assert "No network call was made" in text
    assert _counts(conn) == before
    refused = io.StringIO()
    assert cli.main([
        "suggest", "--database", str(tmp_path / "agent.sqlite"), "--apply",
    ], out=refused) == 2
    assert "does not move" in refused.getvalue()
    assert _counts(conn) == before
    file_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, external_key, "
        "presence, typing_state, type_schema, profile_id, created_at, superseded_by"
        ") VALUES (?, 'file', 'syllabus.txt', 'file-1', '/tmp/syllabus.txt', NULL, "
        "'live', 'typed', 'academic', NULL, 't', NULL)",
        (file_id,),
    )
    conn.execute(
        "INSERT INTO relationships ("
        "relationship_id, rel_type, from_item_id, to_item_id, confidence, source, "
        "state, evidence_refs, basis_key, created_at, supersedes, superseded_by"
        ") VALUES (?, 'member-of', ?, ?, 'witnessed', 'person', 'proposed', '[]', "
        "'member', 't', NULL, NULL)",
        (str(uuid.uuid4()), file_id, course),
    )
    assert proposals(conn, now="2026-10-01T00:00:00+00:00") == []
    assert event
