"""Nudge reads required pairs. No moves. No auto-approve."""
from __future__ import annotations

from pathlib import Path

from database_agent.db import open_database
from items.nudge import warnings as nudge_warnings
from items.profile_items import mint_declared_items
from items.profile_loader import load_profile
from items.schema import create_items_schema
from questions.profile import apply_profile
from questions.schema import create_questions_schema


def test_missing_academic_member_warns_once(tmp_path: Path):
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[str(tmp_path / "c")])
    (tmp_path / "c").mkdir()
    create_items_schema(conn)
    create_questions_schema(conn)
    apply_profile(
        conn, user_id="ada", recorded_at="2026-10-02T00:00:00+00:00",
        courses=("transport=CHEN 3120",),
    )
    mint_declared_items(conn, profile_id="student")
    # Future event with no linked academic file.
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, external_key, "
        "presence, typing_state, type_schema, profile_id, created_at, superseded_by"
        ") VALUES ('ev1', 'event', 'Midterm', NULL, NULL, 'event:1', "
        "'live', 'unplaced', NULL, NULL, '2026-10-02T00:00:00+00:00', NULL)")
    conn.execute(
        "INSERT INTO item_headers ("
        "item_id, kind, external_id, happened_at, status"
        ") VALUES ('ev1', 'event', 'e1', '2099-01-01T12:00:00+00:00', 'confirmed')")
    profile = load_profile("student")
    rows = nudge_warnings(conn, profile=profile, now="2026-10-02T00:00:00+00:00")
    assert len(rows) == 1
    assert rows[0]["kind"] == "missing_member_of"
    assert "CHEN 3120" in rows[0]["message"]
    assert conn.execute(
        "SELECT COUNT(*) FROM relationships WHERE state = 'approved'"
    ).fetchone()[0] == 0
