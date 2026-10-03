"""Search refreshes the folders the person chose, not folders guessed from items."""
from __future__ import annotations

import io
from pathlib import Path

from database_agent.db import open_database
from grouping.vocabulary import P1_INCLUDED_SCAN_STATE
from items.commands import search_main
from items.identity import project_after_scan
from items.refresh import discover_roots
from items.schema import create_items_schema
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.scan import scan
from scan_agent.selection import record_selection


def test_a_new_file_at_the_top_of_the_chosen_folder_is_found(tmp_path: Path):
    root = tmp_path / "corpus"
    (root / "Foo.app").mkdir(parents=True)
    (root / "notes").mkdir()
    (root / "notes" / "todo.txt").write_text("todo list")
    db = tmp_path / "agent.sqlite"
    conn = open_database(db, scan_roots=[])
    create_items_schema(conn)
    selection_id = record_selection(
        conn, sources=[root], candidate_roots=[], cross_folder_moves=False,
        selected_by=None)
    scan(conn, selection_id, source=FilesystemCorpusSource(),
         mime_type_for=lambda _path: None, scan_state=P1_INCLUDED_SCAN_STATE,
         budget_exhausted=lambda: False)
    project_after_scan(conn, [root], P1_INCLUDED_SCAN_STATE)
    assert discover_roots(conn) == [root]
    conn.close()

    (root / "budget.txt").write_text("quarterly budget")
    out = io.StringIO()
    search_main(["budget", "--database", str(db)], out=out)
    assert str(root / "budget.txt") in out.getvalue()

    conn = open_database(db, scan_roots=[])
    runs = conn.execute(
        "SELECT r.scan_run_id FROM scan_runs r WHERE r.selection_id = ? "
        "AND r.completed_at IS NOT NULL ORDER BY r.started_at",
        (selection_id,)).fetchall()
    assert len(runs) == 2
    verdicts = conn.execute(
        "SELECT path FROM exclusion_verdicts WHERE scan_run_id = ?",
        (runs[-1][0],)).fetchall()
    assert [v[0] for v in verdicts] == [str(root / "Foo.app")]
    conn.close()


def test_without_a_selection_roots_are_still_inferred(conn, tmp_path: Path):
    from database_agent.files_table import record_file
    lib = tmp_path / "lib"
    lib.mkdir()
    note = lib / "a.txt"
    note.write_text("a")
    record_file(
        conn, note, filename=note.name, normalized_filename=note.name,
        extension=".txt", observed_size=1, observed_timestamps="{}",
        parent_folder_context=str(lib), mime_type=None, detected_format=None,
        scan_state="included", materialized=True)
    create_items_schema(conn)
    project_after_scan(conn, [lib], "included")
    assert discover_roots(conn) == [lib]
