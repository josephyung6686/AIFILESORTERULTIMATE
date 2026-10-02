"""Five view queries. Cap respected. No mutation imports. Semantic edges never drawn."""
from __future__ import annotations

import ast
import json
from pathlib import Path

from grouping.schema import create_grouping_schema
from grouping.vocabulary import DUPLICATE, MUTUAL_SEMANTIC_RETRIEVAL
from items.identity import reconcile_tree
from items.profile_loader import load_profile
from items.relationships import project_witnessed_links
from items.schema import create_items_schema
from items.views import (
    board_view, folder_view, graph_view, paths_match_files_table, table_view,
    timeline_view,
)


def _seed_files(conn, root: Path, n: int = 20):
    root.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        (root / f"f{i:03d}.txt").write_bytes(f"body-{i}".encode())
    # ten duplicate pairs among them would be denser; add explicit twins
    for i in range(10):
        (root / f"twin-{i}-a.bin").write_bytes(f"twin-{i}".encode())
        (root / f"twin-{i}-b.bin").write_bytes(f"twin-{i}".encode())
    reconcile_tree(conn, root)
    create_grouping_schema(conn)
    project_witnessed_links(conn)


def test_folder_paths_equal_files_current_path(conn, tmp_path: Path):
    root = tmp_path / "lib"
    _seed_files(conn, root, n=5)
    assert paths_match_files_table(conn)
    rows = folder_view(conn)
    assert rows
    assert all(r["open_target"] for r in rows)


def test_graph_caps_and_hides_inferred_and_ignores_semantic(conn, tmp_path: Path):
    root = tmp_path / "lib"
    _seed_files(conn, root, n=30)
    # Dense semantic edges must not appear as relationship rows or drawn edges.
    items = conn.execute(
        "SELECT item_id, file_id FROM items WHERE item_type = 'file' LIMIT 40"
    ).fetchall()
    for i, left in enumerate(items):
        for right in items[i + 1:i + 4]:
            conn.execute(
                "INSERT INTO group_edges ("
                "edge_id, from_file_id, to_file_id, edge_type, evidence_ref, "
                "weight, bridge_entity_ref, hub_suppressed, created_at, "
                "supersedes, superseded_by, supersede_reason"
                ") VALUES (?, ?, ?, ?, 'sim', 0.9, NULL, 0, "
                "'2026-10-02T00:00:00+00:00', NULL, NULL, NULL)",
                (f"sem-{left['file_id']}-{right['file_id']}",
                 left["file_id"], right["file_id"], MUTUAL_SEMANTIC_RETRIEVAL),
            )
    # Three project hubs.
    create_items_schema(conn)
    for name in ("Course A", "Course B", "Course C"):
        conn.execute(
            "INSERT INTO items ("
            "item_id, item_type, display_label, file_id, open_target, "
            "external_key, presence, typing_state, type_schema, profile_id, "
            "created_at, superseded_by"
            ") VALUES (?, 'course', ?, NULL, NULL, NULL, 'live', 'typed', "
            "'academic', 'student', '2026-10-02T00:00:00+00:00', NULL)",
            (f"course-{name}", name),
        )
    # Inferred proposed links between hubs should be hidden (not drawn).
    conn.execute(
        "INSERT INTO relationships ("
        "relationship_id, rel_type, from_item_id, to_item_id, confidence, "
        "source, state, evidence_refs, basis_key, created_at, supersedes, "
        "superseded_by"
        ") VALUES ('inf-1', 'about', 'course-Course A', 'course-Course B', "
        "'inferred', 'connector', 'proposed', "
        "'[\"topic\"]', '{\"rel_type\":\"about\"}', "
        "'2026-10-02T00:00:00+00:00', NULL, NULL)"
    )
    profile = load_profile("student")
    view = graph_view(conn, profile=profile)
    assert len(view.nodes) <= profile.graph_cap
    assert view.hidden_count > 0
    assert all(e["confidence"] != "inferred" for e in view.edges)
    assert all(e["rel_type"] != MUTUAL_SEMANTIC_RETRIEVAL for e in view.edges)


def test_board_has_unplaced_column(conn, tmp_path: Path):
    root = tmp_path / "lib"
    _seed_files(conn, root, n=3)
    create_items_schema(conn)
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, external_key, "
        "presence, typing_state, type_schema, profile_id, created_at, superseded_by"
        ") VALUES ('course-1', 'course', 'Physics', NULL, NULL, NULL, 'live', "
        "'typed', 'academic', 'student', '2026-10-02T00:00:00+00:00', NULL)"
    )
    board = board_view(conn)
    assert "Unplaced" in board
    assert "Physics" in board


def test_table_and_timeline_smoke(conn, tmp_path: Path):
    root = tmp_path / "lib"
    _seed_files(conn, root, n=2)
    create_items_schema(conn)
    item = conn.execute(
        "SELECT item_id FROM items WHERE item_type = 'file' LIMIT 1"
    ).fetchone()["item_id"]
    conn.execute(
        "INSERT INTO item_headers ("
        "item_id, kind, external_id, thread_id, account_label, happened_at, "
        "ended_at, address_from, address_to, calendar_id, status, "
        "attachment_names, attachment_hashes"
        ") VALUES (?, 'event', 'e1', NULL, NULL, ?, NULL, NULL, NULL, "
        "'primary', 'confirmed', NULL, NULL)",
        (item, "2026-10-01T12:00:00+00:00"),
    )
    assert table_view(conn)
    assert timeline_view(conn, days=90)


def test_views_module_never_imports_mutation():
    path = Path(__file__).resolve().parents[2] / "src" / "items" / "views.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert not node.module.startswith("mutation")
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith("mutation")
