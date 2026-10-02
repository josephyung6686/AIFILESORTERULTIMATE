"""Read-only hybrid search. Protected paths counted, not opened. No moves."""
from __future__ import annotations

from pathlib import Path

from grouping.schema import create_grouping_schema
from grouping.vocabulary import MUTUAL_SEMANTIC_RETRIEVAL
from items.identity import reconcile_tree
from items.relationships import project_witnessed_links
from items.search import meaning_search


def test_text_search_finds_label_and_moves_nothing(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "PHYS1401_syllabus.txt").write_text("syllabus", encoding="utf-8")
    (root / "receipt.txt").write_text("store", encoding="utf-8")
    reconcile_tree(conn, root)
    before = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
    result = meaning_search(conn, "PHYS1401 syllabus")
    assert result.moved is False
    assert result.hits
    assert any("PHYS1401" in h.display_label for h in result.hits)
    after = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
    assert after == before


def test_protected_hit_is_counted_without_open_target(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    secret = root / "secret.pem"
    secret.write_bytes(b"not-a-key")
    reconcile_tree(conn, root)
    result = meaning_search(conn, "secret.pem")
    assert result.protected_count >= 1
    assert any(h.protected and h.open_target is None for h in result.hits)


def test_group_edge_never_becomes_life_link_and_search_still_readonly(
        conn, tmp_path: Path):
    """Semantic group edges must not become relationships; search writes nothing.

    Hot-path find uses FTS(+vectors), not group_edges — so a neighbour boost via
    mutual-semantic edges is no longer required for product find.
    """
    root = tmp_path / "lib"
    root.mkdir()
    a = root / "lecture_notes.txt"
    b = root / "problem_set.txt"
    a.write_text("lecture", encoding="utf-8")
    b.write_text("problems", encoding="utf-8")
    reconcile_tree(conn, root)
    create_grouping_schema(conn)
    items = {
        Path(r["open_target"]).name: r
        for r in conn.execute(
            "SELECT item_id, file_id, open_target FROM items WHERE item_type='file'"
        )
    }
    conn.execute(
        "INSERT INTO group_edges ("
        "edge_id, from_file_id, to_file_id, edge_type, evidence_ref, weight, "
        "bridge_entity_ref, hub_suppressed, created_at, supersedes, "
        "superseded_by, supersede_reason"
        ") VALUES ('sem-1', ?, ?, ?, 'sim', 0.8, NULL, 0, "
        "'2026-10-02T00:00:00+00:00', NULL, NULL, NULL)",
        (items["lecture_notes.txt"]["file_id"],
         items["problem_set.txt"]["file_id"], MUTUAL_SEMANTIC_RETRIEVAL),
    )
    before = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
    result = meaning_search(conn, "lecture_notes")
    labels = {h.display_label for h in result.hits}
    assert "lecture_notes.txt" in labels
    assert result.moved is False
    after = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
    assert after == before
    project_witnessed_links(conn)
    assert conn.execute(
        "SELECT COUNT(*) FROM relationships WHERE evidence_refs LIKE '%sem-1%'"
    ).fetchone()[0] == 0


def test_empty_and_special_queries_do_not_crash(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "notes.txt").write_text("hello", encoding="utf-8")
    reconcile_tree(conn, root)
    assert meaning_search(conn, "").hits == ()
    assert meaning_search(conn, "   ").hits == ()
    for q in ('OR OR', '""""', "'; DROP TABLE items;--", "中文", "***"):
        result = meaning_search(conn, q)
        assert result.moved is False
