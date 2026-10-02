"""Declared courses and projects mint items. Empty profile mints nothing."""
from __future__ import annotations

from pathlib import Path

from database_agent.db import open_database
from items.profile_items import mint_declared_items
from items.schema import create_items_schema
from questions.profile import apply_profile
from questions.schema import create_questions_schema


def _conn(tmp_path: Path):
    root = tmp_path / "corpus"
    root.mkdir()
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[str(root)])
    create_items_schema(conn)
    create_questions_schema(conn)
    return conn


def test_empty_profile_mints_nothing(tmp_path: Path):
    conn = _conn(tmp_path)
    assert mint_declared_items(conn) == 0
    assert conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0


def test_named_course_and_project_mint_once(tmp_path: Path):
    conn = _conn(tmp_path)
    apply_profile(
        conn, user_id="ada", recorded_at="2026-10-02T00:00:00+00:00",
        courses=("transport=CHEN 3120",),
        projects=("hackathon=treehacks",),
    )
    n = mint_declared_items(conn, profile_id="student")
    assert n == 2
    types = {r["item_type"]: r["display_label"] for r in conn.execute(
        "SELECT item_type, display_label FROM items")}
    assert types["course"] == "CHEN 3120"
    assert types["project"] == "treehacks"
    assert mint_declared_items(conn, profile_id="student") == 0
