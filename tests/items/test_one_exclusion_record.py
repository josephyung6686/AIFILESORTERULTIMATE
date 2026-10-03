"""The sorter and the assistant report the folders they did not read from one record.

Both walks write `exclusion_verdicts`; `search` prints protected containers in
the sorter's words and the rest as set aside by rule.
"""
from __future__ import annotations

import io
from pathlib import Path

from database_agent.db import open_database
from grouping.vocabulary import P1_INCLUDED_SCAN_STATE
from items.commands import search_main
from items.identity import excluded_areas, project_after_scan, reconcile_tree
from items.schema import create_items_schema
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.scan import scan
from scan_agent.selection import record_selection, selection_sources


def _corpus(tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    (root / "Foo.app" / "Contents").mkdir(parents=True)
    (root / "Foo.app" / "Contents" / "Info.plist").write_text("a")
    (root / "node_modules" / "x").mkdir(parents=True)
    (root / "node_modules" / "x" / "i.js").write_text("b")
    (root / "proj" / "src").mkdir(parents=True)
    (root / "proj" / "package.json").write_text("{}")
    (root / "proj" / "src" / "main.js").write_text("c")
    (root / "notes").mkdir()
    (root / "notes" / "todo.txt").write_text("todo list")
    (root / "essay.txt").write_text("an essay")
    return root


def _sorter_scan(conn, root: Path) -> None:
    """The orchestrator's sequence: R1 selection, P3 scan, item projection.

    `project_after_scan` is the identity half of `project_context_graph`; the
    profile mint needs the sorter's question tables, which this DB lacks.
    """
    create_items_schema(conn)
    selection_id = record_selection(
        conn, sources=[root], candidate_roots=[], cross_folder_moves=False,
        selected_by=None)
    scan(conn, selection_id, source=FilesystemCorpusSource(),
         mime_type_for=lambda _path: None, scan_state=P1_INCLUDED_SCAN_STATE,
         budget_exhausted=lambda: False)
    project_after_scan(conn, selection_sources(conn, selection_id),
                       P1_INCLUDED_SCAN_STATE)


def _search(db: Path) -> str:
    out = io.StringIO()
    search_main(["essay", "--database", str(db)], out=out)
    return out.getvalue()


def _assert_reported(text: str) -> None:
    assert "Protected: 1 marked and counted" in text
    assert "never opened" in text and "Foo.app" in text
    assert "Set aside by rule: 3" in text
    assert "node_modules" in text and "proj" in text
    assert "notes" not in text.split("Set aside by rule")[1].splitlines()[0]


def test_assistant_walk_writes_the_sorters_verdicts(tmp_path: Path):
    root = _corpus(tmp_path)
    db = tmp_path / "agent.sqlite"
    conn = open_database(db, scan_roots=[])
    reconcile_tree(conn, root)
    rules = sorted(r[0] for r in conn.execute(
        "SELECT rule FROM exclusion_verdicts"))
    assert rules == ["literal directory name", "protected container",
                     "software project root descendant",
                     "software project root descendant"]
    areas = excluded_areas(conn)
    assert [a["folder"] for a in areas if a["protected"]] == [
        str(root / "Foo.app")]
    assert sum(a["paths"] for a in areas if not a["protected"]) == 3
    assert conn.execute(
        "SELECT 1 FROM sqlite_master WHERE name = 'excluded_areas'"
    ).fetchone() is None
    conn.close()
    _assert_reported(_search(db))


def test_a_sorter_run_then_search_reports_the_same(tmp_path: Path):
    root = _corpus(tmp_path)
    db = tmp_path / "agent.sqlite"
    conn = open_database(db, scan_roots=[])
    _sorter_scan(conn, root)
    assert [a["protected"] for a in excluded_areas(conn)].count(True) == 1
    conn.close()
    _assert_reported(_search(db))


def test_reconcile_reuses_one_selection_per_root(conn, tmp_path: Path):
    root = _corpus(tmp_path)
    reconcile_tree(conn, root)
    reconcile_tree(conn, root)
    assert conn.execute(
        "SELECT count(*) FROM corpus_selections").fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM scan_runs").fetchone()[0] == 2
    assert sum(a["paths"] for a in excluded_areas(conn)) == 4
