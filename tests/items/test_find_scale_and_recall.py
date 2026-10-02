"""P1 gates: synthetic scale latency + hybrid recall beats FTS-only on CJK."""
from __future__ import annotations

import statistics
from pathlib import Path

from items.hot_index import find_files, rebuild_fts, _fts_search
from items.identity import reconcile_tree
from items.schema import create_items_schema

# Absolute p95 caps (T-P1-02) for synthetic corpora on CI machines.
P95_2K_MS = 200.0       # soft absolute for 2k (harder machines OK under 500)
P95_2K_HARD_MS = 800.0  # fail CI if catastrophically slow


def _build_corpus(conn, root: Path, n: int, *, cjk: bool = True):
    root.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        if cjk and i % 17 == 0:
            name = f"作業講義_{i:05d}.txt"
            body = f"課程 作業 概率 lecture {i}"
        elif i % 11 == 0:
            name = f"Joint_PMFs_{i:05d}.txt"
            body = f"joint probability mass function lecture {i}"
        else:
            name = f"doc_{i:05d}.txt"
            body = f"generic document number {i} notes"
        (root / name).write_text(body, encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)


def test_p95_at_2k_synthetic(conn, tmp_path: Path):
    root = tmp_path / "lib"
    _build_corpus(conn, root, 2000, cjk=True)
    samples = []
    for q in ("probability lecture", "Joint PMFs", "作業", "generic document"):
        for _ in range(5):
            samples.append(find_files(conn, q, limit=10).total_ms)
    samples.sort()
    p95 = samples[int(0.95 * (len(samples) - 1))]
    med = statistics.median(samples)
    assert p95 < P95_2K_HARD_MS, f"p95={p95:.1f}ms med={med:.1f}ms at 2k"
    # Document soft target (does not fail CI alone)
    _ = P95_2K_MS


def test_hybrid_recall_beats_fts_only_on_cjk(conn, tmp_path: Path):
    """Naive unicode61 FTS (no bigrams/LIKE) misses 2-char ZH; find_files hits."""
    root = tmp_path / "lib"
    root.mkdir()
    (root / "作業講義.pdf").write_text("homework lecture", encoding="utf-8")
    (root / "other.txt").write_text("x", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)

    # Naive FTS-only index: whole label as one Han run, no bigram expansion.
    from items.hot_index import ensure_fts
    ensure_fts(conn)
    conn.execute("DELETE FROM item_fts")
    for row in conn.execute(
        "SELECT item_id, display_label, open_target FROM items "
        "WHERE presence='live'"
    ):
        conn.execute(
            "INSERT INTO item_fts (item_id, label, path, body) VALUES (?,?,?,?)",
            (row["item_id"], row["display_label"] or "",
             row["open_target"] or "", ""),
        )

    # Default FTS5 unicode61 keeps 作業講義 as one token → MATCH "作業" empty.
    try:
        naive = conn.execute(
            "SELECT item_id FROM item_fts WHERE item_fts MATCH ? LIMIT 10",
            ('"作業"',),
        ).fetchall()
    except Exception:
        naive = []
    naive_ids = {r["item_id"] for r in naive}

    # Product path: bigrams + LIKE fallback via rebuild + find_files.
    rebuild_fts(conn)
    hybrid = find_files(conn, "作業", limit=10)
    hybrid_ids = {
        h.item_id for h in hybrid.hits if "作業" in h.display_label
    }
    assert hybrid.moved is False
    assert hybrid_ids, "hybrid must recall 作業講義 for query 作業"
    # Kill criterion / P1 exit: naive FTS-only misses; hybrid recalls.
    assert not naive_ids, (
        f"expected naive FTS miss for 2-char ZH, got {naive_ids}"
    )
    assert any("作業講義" in h.display_label for h in hybrid.hits)
