"""Excluded areas are marked and counted, never silently omitted."""
from __future__ import annotations

import io
from pathlib import Path

from assistant.gaps import list_gaps
from items.commands import search_main
from items.identity import excluded_areas, reconcile_tree


def _library(tmp_path: Path) -> Path:
    root = tmp_path / "lib"
    project = root / "ThirdEye"
    project.mkdir(parents=True)
    (project / "requirements.txt").write_text("flask\n", encoding="utf-8")
    (project / "NOTES.md").write_text("project notes", encoding="utf-8")
    (root / "essay.txt").write_text("an essay", encoding="utf-8")
    return root


def test_reconcile_records_a_skipped_project_folder(conn, tmp_path: Path):
    root = _library(tmp_path)
    reconcile_tree(conn, root)
    areas = excluded_areas(conn)
    assert [a["folder"] for a in areas] == [str((root / "ThirdEye").resolve())]
    assert areas[0]["rule"] == "software project root descendant"
    labels = {r[0] for r in conn.execute("SELECT display_label FROM items")}
    assert "essay.txt" in labels and "NOTES.md" not in labels


def test_a_removed_project_is_no_longer_reported(conn, tmp_path: Path):
    root = _library(tmp_path)
    reconcile_tree(conn, root)
    (root / "ThirdEye" / "requirements.txt").unlink()
    reconcile_tree(conn, root)
    assert excluded_areas(conn) == []


def test_gaps_name_the_skipped_folder(conn, tmp_path: Path):
    root = _library(tmp_path)
    reconcile_tree(conn, root)
    gaps = list_gaps(conn)
    assert gaps["excluded_areas"][0]["folder"].endswith("ThirdEye")


def test_search_says_what_it_did_not_read(tmp_path: Path):
    from database_agent.db import open_database
    root = _library(tmp_path)
    db = tmp_path / "agent.sqlite"
    conn = open_database(db, scan_roots=[])
    reconcile_tree(conn, root)
    conn.commit()
    conn.close()
    out = io.StringIO()
    search_main(["essay", "--database", str(db)], out=out)
    text = out.getvalue()
    assert "Set aside by rule: 2" in text
    assert "ThirdEye" in text
