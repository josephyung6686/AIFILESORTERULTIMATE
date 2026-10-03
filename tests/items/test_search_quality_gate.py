"""Task 4: honest search quality gate — no deleted/missing/stale hits."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from items.bakeoff import quality_gate
from items.freshness import MISSING, mark_missing
from items.hot_index import find_files, rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
GOLDEN = ROOT / "fixtures" / "search_golden_real.json"


def _load_golden_corpus(conn, tmp_path: Path) -> dict[str, str]:
    data = json.loads(GOLDEN.read_text(encoding="utf-8"))
    root = tmp_path / "lib"
    root.mkdir()
    key_to_name = {}
    for item in data["corpus_items"]:
        name = item["filename"]
        key_to_name[item["key"]] = name
        if "body_prefix" in item:
            body = item["body_prefix"] * int(item.get("body_prefix_repeat") or 1)
            body += item.get("body_suffix") or ""
        else:
            body = item.get("body") or ""
        (root / name).write_text(body, encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    conn.commit()
    return key_to_name


def test_deleted_item_not_returned_as_live_hit(conn, tmp_path: Path, monkeypatch):
    root = tmp_path / "lib"
    root.mkdir()
    path = root / "doomed.txt"
    path.write_text("unique_doomed_token_xyz", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    item_id = conn.execute(
        "SELECT item_id FROM items WHERE display_label = ?",
        ("doomed.txt",),
    ).fetchone()["item_id"]

    path.unlink()
    reconcile_tree(conn, root)
    # Leave / restore orphan index rows that refresh failed to scrub.
    has_fts = conn.execute(
        "SELECT 1 FROM item_fts WHERE item_id = ?", (item_id,),
    ).fetchone()
    if not has_fts:
        conn.execute(
            "INSERT INTO item_fts (item_id, label, path, body) VALUES (?,?,?,?)",
            (item_id, "doomed.txt", str(path), "unique_doomed_token_xyz"),
        )
    has_chunk = conn.execute(
        "SELECT 1 FROM item_chunks WHERE item_id = ?", (item_id,),
    ).fetchone()
    if not has_chunk:
        conn.execute(
            "INSERT INTO item_chunks ("
            "chunk_id, item_id, ordinal, text, char_start, char_end) "
            "VALUES (?,?,?,?,?,?)",
            (f"{item_id}:0", item_id, 0, "unique_doomed_token_xyz", 0, 22),
        )
        try:
            conn.execute(
                "INSERT INTO item_chunk_fts (chunk_id, item_id, text) "
                "VALUES (?,?,?)",
                (f"{item_id}:0", item_id, "unique_doomed_token_xyz"),
            )
        except Exception:
            pass
    conn.commit()

    import items.index_refresh as refresh
    monkeypatch.setattr(
        refresh, "ensure_search_ready",
        lambda conn, **kwargs: refresh.index_status(conn),
    )
    result = find_files(conn, "unique_doomed_token_xyz", limit=10, mode="fts")
    assert all(h.item_id != item_id for h in result.hits)
    row = conn.execute(
        "SELECT presence, freshness_state FROM items WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    assert row["presence"] != "live" or row["freshness_state"] == MISSING


def test_missing_freshness_not_returned(conn, tmp_path: Path, monkeypatch):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "ghost.txt").write_text("ghost_token_abc", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    item_id = conn.execute(
        "SELECT item_id FROM items WHERE display_label = ?",
        ("ghost.txt",),
    ).fetchone()["item_id"]
    mark_missing(conn, item_id, reason="test_force_missing")
    conn.commit()

    import items.index_refresh as refresh
    monkeypatch.setattr(
        refresh, "ensure_search_ready",
        lambda conn, **kwargs: refresh.index_status(conn),
    )
    result = find_files(conn, "ghost_token_abc", limit=10, mode="fts")
    assert all(h.item_id != item_id for h in result.hits)


def test_stale_hash_mismatch_not_returned(conn, tmp_path: Path, monkeypatch):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "stale.txt").write_text("stale_token_abc live body", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    item_id = conn.execute(
        "SELECT item_id FROM items WHERE display_label = ?",
        ("stale.txt",),
    ).fetchone()["item_id"]
    # Force stale evidence while keeping presence live; skip catch-up.
    conn.execute(
        "UPDATE items SET last_indexed_hash = ?, freshness_state = 'fresh' "
        "WHERE item_id = ?",
        ("deadbeef" * 8, item_id),
    )
    conn.commit()

    import items.index_refresh as refresh

    monkeypatch.setattr(
        refresh, "ensure_search_ready",
        lambda conn, **kwargs: refresh.index_status(conn),
    )
    result = find_files(conn, "stale_token_abc", limit=10, mode="fts")
    assert all(h.item_id != item_id for h in result.hits)


def test_quality_gate_on_golden_corpus(conn, tmp_path: Path):
    _load_golden_corpus(conn, tmp_path)
    failures = quality_gate(conn)
    assert failures == [], failures


def test_evaluate_search_metrics_and_decision(tmp_path: Path):
    """Run evaluate_search against the golden; must pass the quality gate."""
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    import tools.evaluate_search as ev

    out = tmp_path / "decision.json"
    rc = ev.main([
        "--golden", str(GOLDEN),
        "--out", str(out),
        "--no-embed-chunks",
    ])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["quality_gate_pass"] is True
    assert data["winner"] in ("hybrid", "fts")
    assert "recall_at_10" in data["fts"]
    assert "mrr" in data["fts"]
    assert "ndcg_at_10" in data["fts"]
    assert "abstention" in data["fts"]
    assert "citation_correctness" in data["fts"]


def test_filename_only_never_claims_body(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    # Words appear only in the filename, not the body.
    (root / "Annual Report Q4.txt").write_text(
        "Office hours and grading policy only.", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)

    result = find_files(conn, "Annual Report", limit=10, mode="fts")
    assert result.hits, "filename tokens must still be findable"
    hit = next(h for h in result.hits if "Annual" in (h.display_label or ""))
    assert "filename" in hit.match_fields
    assert hit.claims_body_match is False
    assert hit.best_chunk_id is None
    assert "chunk" not in hit.match_fields
