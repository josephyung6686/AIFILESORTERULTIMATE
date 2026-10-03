"""Witnessed links only. Semantic and session edges never become life links."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from grouping.schema import create_grouping_schema
from grouping.vocabulary import (
    BOUNDED_SESSION, DUPLICATE, MUTUAL_SEMANTIC_RETRIEVAL, VERSION_FAMILY,
)
from items.identity import reconcile_tree
from items.relationships import project_witnessed_links
from items.schema import create_items_schema


def _now() -> str:
    return "2026-10-02T12:00:00+00:00"


def _edge(conn, *, edge_id, from_id, to_id, edge_type, evidence_ref):
    conn.execute(
        "INSERT INTO group_edges ("
        "edge_id, from_file_id, to_file_id, edge_type, evidence_ref, weight, "
        "bridge_entity_ref, hub_suppressed, created_at, supersedes, "
        "superseded_by, supersede_reason"
        ") VALUES (?, ?, ?, ?, ?, NULL, NULL, 0, ?, NULL, NULL, NULL)",
        (edge_id, from_id, to_id, edge_type, evidence_ref, _now()),
    )


def _live_file_items(conn):
    return conn.execute(
        "SELECT item_id, file_id, open_target FROM items "
        "WHERE item_type = 'file' AND presence = 'live' "
        "ORDER BY open_target"
    ).fetchall()


def _rels(conn):
    return conn.execute(
        "SELECT * FROM relationships WHERE superseded_by IS NULL "
        "ORDER BY rel_type, from_item_id, to_item_id"
    ).fetchall()


def test_equal_hash_on_two_live_items_is_one_witnessed_duplicate(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    a = root / "a.bin"
    b = root / "b.bin"
    a.write_bytes(b"same-bytes")
    b.write_bytes(b"same-bytes")
    (root / "other.txt").write_bytes(b"different")
    reconcile_tree(conn, root)
    create_grouping_schema(conn)

    n = project_witnessed_links(conn)
    rows = _rels(conn)
    # `reconcile_tree` is the sorter's scan + projection now, which already
    # projected the duplicate; a second projection adds nothing.
    assert n == 0
    assert len(rows) == 1
    row = rows[0]
    assert row["rel_type"] == "duplicate-of"
    assert row["confidence"] == "witnessed"
    assert row["source"] == "scan"
    assert row["state"] == "proposed"
    refs = json.loads(row["evidence_refs"])
    assert refs
    assert all(refs)
    items = {r["item_id"] for r in _live_file_items(conn)}
    assert {row["from_item_id"], row["to_item_id"]} <= items
    other = conn.execute(
        "SELECT item_id FROM items WHERE display_label = 'other.txt'"
    ).fetchone()["item_id"]
    assert other not in {row["from_item_id"], row["to_item_id"]}


def test_group_edge_duplicate_and_version_project_when_evidence_present(
        conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    first = root / "v1.txt"
    second = root / "v2.txt"
    first.write_bytes(b"one")
    second.write_bytes(b"two")
    reconcile_tree(conn, root)
    create_grouping_schema(conn)
    items = {Path(r["open_target"]).name: r for r in _live_file_items(conn)}
    _edge(
        conn, edge_id="e-dup", from_id=items["v1.txt"]["file_id"],
        to_id=items["v2.txt"]["file_id"], edge_type=DUPLICATE,
        evidence_ref="hash:abc",
    )
    _edge(
        conn, edge_id="e-ver", from_id=items["v1.txt"]["file_id"],
        to_id=items["v2.txt"]["file_id"], edge_type=VERSION_FAMILY,
        evidence_ref="name:v1-v2",
    )

    project_witnessed_links(conn)
    by_type = {r["rel_type"]: r for r in _rels(conn)}
    assert by_type["duplicate-of"]["source"] == "grouping"
    assert by_type["version-of"]["source"] == "grouping"
    assert by_type["duplicate-of"]["confidence"] == "witnessed"
    assert by_type["version-of"]["confidence"] == "witnessed"


def test_empty_evidence_and_semantic_edges_are_never_projected(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    a = root / "a.txt"
    b = root / "b.txt"
    a.write_bytes(b"x")
    b.write_bytes(b"y")
    reconcile_tree(conn, root)
    create_grouping_schema(conn)
    items = list(_live_file_items(conn))
    _edge(
        conn, edge_id="e-empty", from_id=items[0]["file_id"],
        to_id=items[1]["file_id"], edge_type=DUPLICATE, evidence_ref="",
    )
    _edge(
        conn, edge_id="e-sem", from_id=items[0]["file_id"],
        to_id=items[1]["file_id"], edge_type=MUTUAL_SEMANTIC_RETRIEVAL,
        evidence_ref="sim:0.9",
    )
    _edge(
        conn, edge_id="e-ses", from_id=items[0]["file_id"],
        to_id=items[1]["file_id"], edge_type=BOUNDED_SESSION,
        evidence_ref="session:1",
    )

    project_witnessed_links(conn)
    assert _rels(conn) == []


def test_projection_is_idempotent_on_basis_key(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.bin").write_bytes(b"twin")
    (root / "b.bin").write_bytes(b"twin")
    reconcile_tree(conn, root)
    create_grouping_schema(conn)
    project_witnessed_links(conn)
    project_witnessed_links(conn)
    assert len(_rels(conn)) == 1


def test_missing_items_schema_is_a_no_op():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    assert project_witnessed_links(conn) == 0
