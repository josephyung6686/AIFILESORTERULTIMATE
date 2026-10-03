"""Index a folder in one fast pass, and count what the person has.

The sorter's own sequence -- R1 selection, P3 scan, item projection -- then the
search tables. No cloud call. Every file ends up indexed, set aside (counted)
or protected (counted); `counts` reads those totals back from the database.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from grouping.vocabulary import P1_INCLUDED_SCAN_STATE
from scan_agent.corpus_source import KIND_FILE, FilesystemCorpusSource

Progress = Callable[[str, int, int], None]


@dataclass(frozen=True)
class IndexCounts:
    indexed: int
    set_aside: int
    set_aside_folders: int
    protected: int
    held: int
    open_questions: int


def index_folder(conn: sqlite3.Connection, root: Path, *,
                 on_progress: Progress | None = None) -> IndexCounts:
    """Scan `root` as the sorter does, project items, rebuild search."""
    from cli import _bootstrap
    from items.hot_index import rebuild_fts
    from items.identity import _selection_for
    from items.project import project_context_graph
    from scan_agent.scan import scan
    from scan_agent.selection import selection_sources

    report = on_progress or (lambda _stage, _done, _total: None)
    root = Path(root).expanduser().resolve()
    _bootstrap(conn)
    selection_id = _selection_for(conn, root)
    source = _CountingSource(FilesystemCorpusSource(), report)
    scan(conn, selection_id, source=source, mime_type_for=lambda _p: None,
         scan_state=P1_INCLUDED_SCAN_STATE, budget_exhausted=lambda: False)
    project_context_graph(conn, selection_sources(conn, selection_id),
                          P1_INCLUDED_SCAN_STATE)
    rebuild_fts(conn)
    conn.commit()
    report("done", source.files, source.files)
    return counts(conn)


class _CountingSource:
    """The live filesystem, reporting each file the walk lists."""

    def __init__(self, inner, report: Progress):
        self._inner = inner
        self._report = report
        self.has_bytes = inner.has_bytes
        self.files = 0

    def entries(self, directory):
        found = self._inner.entries(directory)
        for entry in found:
            if entry.kind == KIND_FILE:
                self.files += 1
                # The total is not known until the walk ends.
                self._report("scan", self.files, 0)
        return found


def counts(conn: sqlite3.Connection) -> IndexCounts:
    """Indexed, set aside, protected, held and open questions, from the DB."""
    from items.file_identity import item_is_sensitive
    from items.identity import excluded_areas

    if not _has_table(conn, "items"):
        return IndexCounts(0, 0, 0, 0, 0, 0)
    live = conn.execute(
        "SELECT item_id, typing_state FROM items WHERE presence = 'live' "
        "AND superseded_by IS NULL AND item_type = 'file'").fetchall()
    sensitive = [row for row in live if item_is_sensitive(conn, row["item_id"])]
    areas = excluded_areas(conn)
    set_aside = [a for a in areas if not a["protected"]]
    protected_areas = [a for a in areas if a["protected"]]
    return IndexCounts(
        indexed=len(live),
        set_aside=sum(a["paths"] for a in set_aside),
        set_aside_folders=len(set_aside),
        protected=len(protected_areas) + len(sensitive),
        held=sum(1 for row in live if row["typing_state"] == "held"),
        open_questions=_open_questions(conn),
    )


def _open_questions(conn: sqlite3.Connection) -> int:
    if not _has_table(conn, "structural_questions"):
        return 0
    from questions.store import open_questions
    return len(open_questions(conn))


def _has_table(conn: sqlite3.Connection, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (name,)).fetchone() is not None
