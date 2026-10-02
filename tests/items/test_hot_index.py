"""Edge cases for FTS5 + vector + RRF hot index."""
from __future__ import annotations

from pathlib import Path

import pytest

from items.hot_index import find_files, rebuild_fts
from items.identity import reconcile_tree


def test_rebuild_fts_without_evidence_table(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "PHYS1401_syllabus.txt").write_text("syllabus body", encoding="utf-8")
    reconcile_tree(conn, root)
    # Fresh items DB often has no evidence table — must not crash.
    n = rebuild_fts(conn)
    assert n == 1
    result = find_files(conn, "PHYS1401 syllabus")
    assert result.fts_used is True
    assert any("PHYS1401" in h.display_label for h in result.hits)
    assert result.moved is False


def test_empty_query_and_limit_validation(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_text("a", encoding="utf-8")
    reconcile_tree(conn, root)
    assert find_files(conn, "").hits == ()
    assert find_files(conn, "\n\t ").hits == ()
    with pytest.raises(ValueError):
        find_files(conn, "a", limit=0)
    with pytest.raises(ValueError):
        find_files(conn, "a", limit=-3)


def test_fts_special_characters_do_not_crash(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "report.txt").write_text("annual report", encoding="utf-8")
    reconcile_tree(conn, root)
    for q in (
        'OR OR OR',
        '""""',
        '***',
        'title:foo',
        'NEAR/3',
        "'; DROP TABLE items;--",
        "中文文件",
        "日本語テスト",
        "a" * 500,
    ):
        result = find_files(conn, q, limit=5)
        assert result.moved is False


def test_protected_path_withheld_in_hits(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "secret.pem").write_bytes(b"x")
    (root / "open.txt").write_text("open", encoding="utf-8")
    reconcile_tree(conn, root)
    result = find_files(conn, "secret.pem")
    assert result.protected_count >= 1
    for hit in result.hits:
        if hit.protected:
            assert hit.open_target is None


def test_rebuild_is_idempotent(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "one.txt").write_text("one", encoding="utf-8")
    (root / "two.txt").write_text("two", encoding="utf-8")
    reconcile_tree(conn, root)
    assert rebuild_fts(conn) == 2
    assert rebuild_fts(conn) == 2
    assert conn.execute("SELECT COUNT(*) FROM item_fts").fetchone()[0] == 2
