"""Surfaces share one projection helper (T6)."""
from __future__ import annotations

from pathlib import Path

from grouping.schema import create_grouping_schema
from items.identity import reconcile_tree
from items.relationship_service import accept_link, project_relationships
from items.relationships import project_witnessed_links
from items.schema import create_items_schema


def test_graph_and_list_related_agree_on_approved(conn, tmp_path: Path):
    create_items_schema(conn)
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.bin").write_bytes(b"twins")
    (root / "b.bin").write_bytes(b"twins")
    reconcile_tree(conn, root)
    create_grouping_schema(conn)
    project_witnessed_links(conn)
    row = conn.execute(
        "SELECT relationship_id FROM relationships "
        "WHERE superseded_by IS NULL LIMIT 1"
    ).fetchone()
    accept_link(conn, row["relationship_id"], user_id="u")
    graph_ids = {
        e["relationship_id"]
        for e in project_relationships(conn, surface="graph")
    }
    list_ids = {
        e["relationship_id"]
        for e in project_relationships(conn, surface="list_related")
    }
    assert row["relationship_id"] in graph_ids
    assert row["relationship_id"] in list_ids
