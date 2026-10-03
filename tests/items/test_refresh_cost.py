"""A question does not re-scan the folder when nothing on disk changed."""
from __future__ import annotations

import io
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from database_agent.db import open_database
from items.commands import search_main
from items.indexing import index_folder, read_document_text

TABLES = ("scan_runs", "events", "stat_cache_verdicts")


def _corpus(tmp_path: Path, n: int = 600) -> Path:
    root = tmp_path / "home"
    for i in range(n):
        folder = root / f"folder{i % 20}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"note{i}.txt").write_text(f"note number {i}", encoding="utf-8")
    return root


def _rows(conn) -> dict[str, int]:
    return {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in TABLES}


def _search(db: Path, query: str) -> str:
    out = io.StringIO()
    search_main([query, "--database", str(db)], out=out)
    return out.getvalue()


def test_a_second_search_with_no_change_writes_nothing_and_is_fast(tmp_path):
    db = tmp_path / "a.sqlite"
    conn = open_database(db, scan_roots=[])
    index_folder(conn, _corpus(tmp_path))
    _search(db, "note")
    before = _rows(conn)
    started = time.perf_counter()
    _search(db, "note")
    elapsed = time.perf_counter() - started
    assert _rows(conn) == before
    # Measured 0.039 s on an idle machine (3 Oct 2026); the bound leaves room
    # for concurrent load. The zero-rows assertion above is the strict one.
    assert elapsed < 1.5, elapsed


def test_a_touched_file_is_reindexed_and_only_it_is_recorded(tmp_path):
    db = tmp_path / "a.sqlite"
    conn = open_database(db, scan_roots=[])
    root = _corpus(tmp_path)
    index_folder(conn, root)
    _search(db, "note")
    before = _rows(conn)
    last_verdict = conn.execute(
        "SELECT MAX(verdict_id) FROM stat_cache_verdicts").fetchone()[0]
    touched = root / "folder3" / "note3.txt"
    touched.write_text("note number 3 now mentions zeppelin", encoding="utf-8")
    later = time.time() + 5
    os.utime(touched, (later, later))

    _search(db, "note")

    after = _rows(conn)
    assert after["scan_runs"] - before["scan_runs"] <= 1
    paths = {row[0] for row in conn.execute(
        "SELECT observed_path FROM stat_cache_verdicts WHERE verdict_id > ?",
        (last_verdict,))}
    assert paths == {str(touched.resolve())}
    assert after["events"] - before["events"] < 10
    # The new version is indexed by name and owed a reading; once read, its
    # new words are found.
    item = conn.execute(
        "SELECT i.content_hash, i.last_indexed_hash, f.content_hash AS disk "
        "FROM items i JOIN files f ON f.file_id = i.file_id "
        "WHERE i.display_label = 'note3.txt'").fetchone()
    assert item["content_hash"] == item["last_indexed_hash"] == item["disk"]
    assert read_document_text(conn) >= 1
    assert "note3.txt" in _search(db, "zeppelin")


def test_with_no_recorded_selection_a_search_records_none(tmp_path):
    from items.schema import create_items_schema
    db = tmp_path / "a.sqlite"
    conn = open_database(db, scan_roots=[])
    create_items_schema(conn)
    note = tmp_path / "home" / "essay.txt"
    note.parent.mkdir()
    note.write_text("an essay", encoding="utf-8")
    conn.execute(
        "INSERT INTO items (item_id, item_type, display_label, open_target, "
        "presence, typing_state, created_at) VALUES "
        "('i1', 'file', 'essay.txt', ?, 'live', 'unplaced', ?)",
        (str(note), datetime.now(timezone.utc).isoformat()))
    conn.commit()

    _search(db, "essay")

    assert conn.execute(
        "SELECT COUNT(*) FROM corpus_selections").fetchone()[0] == 0


def test_the_sorters_nothing_read_screen_reads_the_sorters_run(
        tmp_path, monkeypatch):
    import cli
    from grouping.vocabulary import P1_INCLUDED_SCAN_STATE
    from scan_agent.corpus_source import FilesystemCorpusSource
    from scan_agent.scan import scan
    from scan_agent.selection import record_selection

    sorted_folder = tmp_path / "sorted"
    sorted_folder.mkdir()
    (sorted_folder / "a.txt").write_text("a", encoding="utf-8")
    other = tmp_path / "other"
    other.mkdir()
    (other / "b.txt").write_text("b", encoding="utf-8")
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    cli._bootstrap(conn)
    selection_id = record_selection(
        conn, sources=[sorted_folder], candidate_roots=[],
        cross_folder_moves=False, selected_by="person")
    sorter_run = scan(conn, selection_id, source=FilesystemCorpusSource(),
                      mime_type_for=lambda _p: None,
                      scan_state=P1_INCLUDED_SCAN_STATE,
                      budget_exhausted=lambda: False)
    index_folder(conn, other)               # the assistant's run, newer
    asked: list[str] = []
    monkeypatch.setattr(cli, "corpus_roster",
                        lambda _conn, run_id: asked.append(run_id) or ())

    cli._nothing_could_be_read_report(
        conn, directory=sorted_folder, also_read=(),
        now=lambda: datetime.now(timezone.utc).isoformat())

    assert asked == [sorter_run]
