"""Thin inferred connector: proposed about/member-of only; never auto-approve."""
from __future__ import annotations

import json
from pathlib import Path

from database_agent.db import open_database
from items.connector import propose_inferred_links
from items.identity import reconcile_tree
from items.profile_items import mint_declared_items
from items.schema import create_items_schema
from items.views import graph_view
from questions.profile import apply_profile
from questions.schema import create_questions_schema


def _setup(tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "CHEN 3120 homework.pdf").write_bytes(b"hw")
    (root / "other.pdf").write_bytes(b"other")
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[str(root)])
    create_items_schema(conn)
    create_questions_schema(conn)
    reconcile_tree(conn, root)
    apply_profile(
        conn, user_id="ada", recorded_at="2026-10-02T00:00:00+00:00",
        lives=("coursework=academic", "recruiting=career"),
        courses=("transport=CHEN 3120",),
    )
    mint_declared_items(conn, profile_id="student")
    # Type the homework as academic; leave other unplaced.
    conn.execute(
        "UPDATE items SET typing_state = 'typed', type_schema = 'academic' "
        "WHERE display_label = 'CHEN 3120 homework.pdf'")
    return conn


def test_course_id_in_filename_proposes_member_of(tmp_path: Path):
    conn = _setup(tmp_path)
    n = propose_inferred_links(conn)
    assert n >= 1
    row = conn.execute(
        "SELECT rel_type, confidence, state, evidence_refs FROM relationships "
        "WHERE rel_type = 'member-of' AND superseded_by IS NULL"
    ).fetchone()
    assert row is not None
    assert row["confidence"] in ("inferred", "witnessed")
    assert row["state"] == "proposed"
    assert json.loads(row["evidence_refs"])


def test_inferred_links_hidden_on_default_graph(tmp_path: Path):
    conn = _setup(tmp_path)
    propose_inferred_links(conn)
    conn.execute(
        "UPDATE relationships SET confidence = 'inferred' "
        "WHERE rel_type = 'member-of'")
    from items.profile_loader import load_profile
    course = conn.execute(
        "SELECT item_id FROM items WHERE item_type = 'course'").fetchone()
    view = graph_view(
        conn, center_item_id=course["item_id"],
        profile=load_profile("student"))
    assert all(e.get("confidence") != "inferred" for e in view.edges)
    assert view.hidden_count >= 1


def test_never_writes_approved(tmp_path: Path):
    conn = _setup(tmp_path)
    propose_inferred_links(conn)
    approved = conn.execute(
        "SELECT COUNT(*) FROM relationships WHERE state = 'approved'"
    ).fetchone()[0]
    assert approved == 0
