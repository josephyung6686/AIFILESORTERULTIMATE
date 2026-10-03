"""Canonical relationship approval machine (T6)."""
from __future__ import annotations

from pathlib import Path

import pytest

from grouping.schema import create_grouping_schema
from items.identity import reconcile_tree
from items.relationship_service import (
    InvalidTransition,
    accept_link,
    project_relationships,
    reject_link,
)
from items.relationships import project_witnessed_links
from items.schema import create_items_schema


def _pair(conn, tmp_path: Path):
    create_items_schema(conn)
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.bin").write_bytes(b"same")
    (root / "b.bin").write_bytes(b"same")
    reconcile_tree(conn, root)
    create_grouping_schema(conn)
    project_witnessed_links(conn)
    return conn.execute(
        "SELECT * FROM relationships WHERE superseded_by IS NULL"
    ).fetchone()


def test_accept_binds_approval_hash(conn, tmp_path: Path):
    row = _pair(conn, tmp_path)
    out = accept_link(conn, row["relationship_id"], user_id="ada", session_id="s1")
    assert out["state"] == "approved"
    dec = conn.execute(
        "SELECT approval_hash, evidence_ids, session_id, polarity "
        "FROM relationship_decisions WHERE relationship_id=? "
        "ORDER BY rowid DESC LIMIT 1",
        (row["relationship_id"],),
    ).fetchone()
    assert dec["polarity"] == "accept"
    assert dec["approval_hash"]
    assert dec["session_id"] == "s1"


def test_reject_from_approved_invalid(conn, tmp_path: Path):
    row = _pair(conn, tmp_path)
    accept_link(conn, row["relationship_id"], user_id="ada")
    with pytest.raises(InvalidTransition):
        reject_link(conn, row["relationship_id"], user_id="ada")


def test_inferred_hidden_until_approved(conn, tmp_path: Path):
    create_items_schema(conn)
    # Mint two items and an inferred proposed edge manually.
    a = "ia"
    b = "ib"
    for iid, label in ((a, "A"), (b, "B")):
        conn.execute(
            "INSERT INTO items ("
            "item_id, item_type, display_label, file_id, open_target, "
            "external_key, presence, typing_state, type_schema, profile_id, "
            "created_at, superseded_by) VALUES ("
            "?,?,?,?,NULL,NULL,'live','typed',NULL,NULL,datetime('now'),NULL)",
            (iid, "file", label, None),
        )
    rid = "rel-inf"
    conn.execute(
        "INSERT INTO relationships ("
        "relationship_id, from_item_id, to_item_id, rel_type, confidence, "
        "source, state, evidence_refs, basis_key, created_at, supersedes, "
        "superseded_by) VALUES ("
        "?,?,?,?, 'inferred', 'test', 'proposed', '[]', 'bk', "
        "datetime('now'), NULL, NULL)",
        (rid, a, b, "about"),
    )
    graph = project_relationships(conn, surface="graph")
    assert not any(e["relationship_id"] == rid for e in graph)
    accept_link(conn, rid, user_id="ada")
    graph2 = project_relationships(conn, surface="graph")
    assert any(e["relationship_id"] == rid for e in graph2)
