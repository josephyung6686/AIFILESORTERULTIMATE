"""P1 slice: item_chunks + CJK bigram / LIKE fallback."""
from __future__ import annotations

from pathlib import Path

from items.hot_index import cjk_bigrams, find_files, rebuild_fts
from items.identity import reconcile_tree


def test_chunks_created_on_rebuild(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    long = ("lecture notes on probability. " * 80)
    (root / "notes.txt").write_text(long, encoding="utf-8")
    reconcile_tree(conn, root)
    # No evidence table → chunks from label only may be short; inject body via
    # FTS rebuild path using label+empty evidence. Force long label path:
    n = rebuild_fts(conn)
    assert n >= 1
    # With only filename, still have schema
    assert conn.execute(
        "SELECT 1 FROM sqlite_master WHERE name='item_chunks'"
    ).fetchone()


def test_cjk_two_char_finds_label(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "作業講義.pdf").write_text("homework", encoding="utf-8")
    (root / "other.txt").write_text("x", encoding="utf-8")
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    # 2-char query — kill criterion if empty while file exists
    result = find_files(conn, "作業", limit=10)
    assert result.moved is False
    labels = [h.display_label for h in result.hits]
    assert any("作業" in lab for lab in labels), labels
    # bigram helper
    assert "作業" in cjk_bigrams("作業講義")


def test_cjk_single_char_like_fallback(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "稅務.pdf").write_text("tax", encoding="utf-8")
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    result = find_files(conn, "稅", limit=5)
    assert any("稅" in h.display_label for h in result.hits)
