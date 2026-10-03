"""Suggestions are local warnings. They do not approve a link or move a file."""
from __future__ import annotations

import http.client
import io
import uuid

from items.schema import create_items_schema
from items.suggest import suggestions

from database_agent.entrypoint import main


def _counts(conn):
    items = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    links = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
    approved = conn.execute(
        "SELECT COUNT(*) FROM relationships WHERE state = 'approved'"
    ).fetchone()[0]
    return items, links, approved


def _course(conn):
    create_items_schema(conn)
    course = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, external_key, "
        "presence, typing_state, type_schema, profile_id, created_at, superseded_by"
        ") VALUES (?, 'course', 'CHEM 101', NULL, NULL, NULL, 'live', 'typed', "
        "'academic', NULL, 't', NULL)",
        (course,),
    )
    return course


def test_a_course_with_no_file_is_one_warning(conn, tmp_path, monkeypatch):
    def boom(*_args, **_kwargs):
        raise AssertionError("network")

    monkeypatch.setattr(http.client.HTTPConnection, "request", boom)
    course = _course(conn)
    before = _counts(conn)
    rows = suggestions(conn)
    assert len(rows) == 1
    assert rows[0]["kind"] == "missing_member_of"
    assert "CHEM 101" in rows[0]["text"]
    assert _counts(conn) == before
    out = io.StringIO()
    code = main([
        "suggest", "--database", str(tmp_path / "agent.sqlite"),
    ], out=out)
    text = out.getvalue()
    assert code == 0, text
    assert "CHEM 101" in text
    assert "Nothing was moved" in text
    assert _counts(conn) == before
    refused = io.StringIO()
    assert main([
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
    assert suggestions(conn) == []
