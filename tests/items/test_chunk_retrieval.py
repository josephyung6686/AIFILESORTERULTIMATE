"""Task 4: real chunk retrieval with honest filename vs body citations."""
from __future__ import annotations

from pathlib import Path

from items.hot_index import CHUNK_CHARS, find_files, rebuild_fts
from items.identity import reconcile_tree
from items.index_refresh import ensure_search_ready
from items.schema import create_items_schema


def test_marker_after_char_4000_found_with_chunk_citation(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    marker = "UNIQUE_LATE_MARKER_zeta9"
    # Prefix longer than the historical 4k body cap.
    prefix = ("Corporate briefing filler paragraph. ") * 140
    assert len(prefix) > 4000
    body = prefix + f" {marker} finds the buried escrow clause."
    path = root / "long_briefing.txt"
    path.write_text(body, encoding="utf-8")

    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()

    result = find_files(conn, marker, limit=10, mode="fts")
    assert result.hits, "late marker must be findable"
    hit = result.hits[0]
    assert hit.claims_body_match is True
    assert hit.best_chunk_id is not None
    assert hit.best_chunk_id in hit.citations
    assert "chunk" in hit.match_fields

    crow = conn.execute(
        "SELECT text, char_start, char_end FROM item_chunks WHERE chunk_id = ?",
        (hit.best_chunk_id,),
    ).fetchone()
    assert crow is not None
    assert marker in crow["text"]
    assert int(crow["char_start"]) >= 4000
    # Chunking uses CHUNK_CHARS; marker should land in a later ordinal.
    assert int(crow["char_start"]) // CHUNK_CHARS >= 5


def test_chunk_fts_aggregates_to_item_and_keeps_best_chunk(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "notes_a.txt").write_text(
        ("alpha " * 200) + " shared_token_zz " + ("beta " * 200),
        encoding="utf-8",
    )
    (root / "notes_b.txt").write_text("unrelated content only", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)

    result = find_files(conn, "shared_token_zz", limit=5, mode="fts")
    labels = [h.display_label for h in result.hits]
    assert any("notes_a" in lab for lab in labels)
    hit = next(h for h in result.hits if "notes_a" in h.display_label)
    assert hit.best_chunk_id is not None
    assert hit.best_chunk_id.startswith(hit.item_id + ":")


def test_filename_only_match_does_not_claim_body(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "Annual Report Q4.txt").write_text(
        "Office hours and grading policy only.", encoding="utf-8")
    (root / "other.txt").write_text("completely different body", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)

    result = find_files(conn, "Annual Report", limit=10, mode="fts")
    hit = next(h for h in result.hits if "Annual" in h.display_label)
    assert "filename" in hit.match_fields
    assert hit.claims_body_match is False
    assert hit.best_chunk_id is None
    assert "chunk" not in hit.match_fields


def test_ensure_search_ready_indexes_chunks_past_4k(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    marker = "CATCHUP_LATE_MARKER_qq"
    body = ("pad paragraph for length. ") * 200 + marker
    assert len(body) > 4000
    (root / "catchup.txt").write_text(body, encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    ensure_search_ready(conn)
    result = find_files(conn, marker, limit=5, mode="fts")
    assert result.hits
    assert result.hits[0].best_chunk_id is not None
