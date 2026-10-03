"""Index a folder in one fast pass, and count what the person has.

The sorter's own sequence -- R1 selection, P3 scan, item projection -- then the
search tables. No cloud call. Every file ends up indexed, set aside (counted)
or protected (counted); `counts` reads those totals back from the database.
"""
from __future__ import annotations

import sqlite3
from collections import deque
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
    #: Files whose text has not been read yet; they are found by name only.
    unread_documents: int = 0


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
    _classify_by_name(conn, root)
    rebuild_fts(conn)
    _index_projects(conn)
    conn.commit()
    report("done", source.files, source.files)
    return counts(conn)


def _authorities(conn: sqlite3.Connection):
    """The sorter's own P1--P7 wiring: its detector, classifier and readers.

    Built, not run: the extraction pool starts no process until a file is
    submitted to it.
    """
    from datetime import datetime, timezone

    from cli import _RECOGNITION_MANIFEST, build_detector, p1_p7_authorities
    from recognition.rules import load_rules

    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

    detector = build_detector(
        conn, load_rules(_RECOGNITION_MANIFEST.read_text), now=now)
    return p1_p7_authorities(now=now, detector=detector)


def _classify_by_name(conn: sqlite3.Connection, root: Path) -> None:
    """The sorter's local sensitivity pass over what a name already says.

    For each file under `root` whose bytes have no reading yet: the sorter's
    filesystem record (name, folder; the file is not opened), then its
    classifier, then `assign` -- the order `orchestrator.run_p1_p7` uses. A file
    with only this record is one the sorter's next run still reads in full.
    """
    from evidence_shape.store import RunWriter, runs_for_content
    from extractors.authorship import SUBSYSTEM as P5
    from extractors.filesystem import extract_filesystem
    from extractors.safety import ProtectedContainerRefused
    from items.identity import _under_any
    from privacy.classification_store import ClassificationStore
    from privacy.learning_seam import assign

    # The pass needs the sorter's tables; a database that only has items (the
    # pilot's fast path) gets them here rather than skipping the protection.
    from cli import _bootstrap
    _bootstrap(conn)
    authorities = _authorities(conn)
    sink = RunWriter(conn, author=P5)
    store = ClassificationStore(conn)
    rows = conn.execute(
        "SELECT * FROM files WHERE scan_state = ?",
        (P1_INCLUDED_SCAN_STATE,)).fetchall()
    for row in rows:
        if not _under_any(row["current_path"], [root]):
            continue
        file_id, content_hash = row["file_id"], row["content_hash"]
        if not runs_for_content(conn, content_hash):
            try:
                sink.write(extract_filesystem(
                    file_row=dict(row), path=Path(row["current_path"]),
                    policy=authorities.policy, now=authorities.now(),
                    context_window=authorities.context_window))
            except ProtectedContainerRefused:
                continue
        if store.current(file_id, content_hash) is not None:
            continue
        candidate = authorities.classify(conn, file_id, content_hash)
        if candidate is not None:
            assign(conn, candidate, store=store,
                   component_version=authorities.p7_component_version)


def _index_projects(conn: sqlite3.Connection) -> None:
    """One item per software project the scan set aside, never one per file.

    Searchable by the folder name, the first 2 KB of its README and its
    top-level file names. Code inside is never read; nothing inside is an item.
    """
    import uuid
    from datetime import datetime, timezone

    from items.hot_index import cjk_bigrams, write_chunks_for_item
    from items.identity import excluded_areas
    from items.project import project_body
    from scan_agent.exclusion import RULE_PROJECT_ROOT_DESCENDANT

    from items.project import retire_missing_projects
    retire_missing_projects(conn)
    for area in excluded_areas(conn):
        if area["rule"] != RULE_PROJECT_ROOT_DESCENDANT:
            continue
        folder = Path(area["folder"])
        if not folder.is_dir():
            continue
        key = f"project_root:{folder}"
        row = conn.execute(
            "SELECT item_id FROM items WHERE external_key = ? "
            "AND superseded_by IS NULL", (key,)).fetchone()
        if row is None:
            item_id = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO items (item_id, item_type, display_label, "
                "open_target, external_key, presence, typing_state, created_at, "
                "freshness_state) VALUES (?, 'project', ?, ?, ?, 'live', "
                "'unplaced', ?, 'fresh')",
                (item_id, folder.name, str(folder), key,
                 datetime.now(timezone.utc).isoformat()))
        else:
            item_id = row["item_id"]
        body = project_body(folder)
        conn.execute("DELETE FROM item_fts WHERE item_id = ?", (item_id,))
        conn.execute("DELETE FROM item_chunk_fts WHERE item_id = ?", (item_id,))
        conn.execute("DELETE FROM item_chunks WHERE item_id = ?", (item_id,))
        conn.execute(
            "INSERT INTO item_fts (item_id, label, path, body) VALUES (?,?,?,?)",
            (item_id, f"{folder.name} {cjk_bigrams(folder.name)}".strip(),
             str(folder), body))
        write_chunks_for_item(conn, item_id, body, label=folder.name)


def read_document_text(conn: sqlite3.Connection, *,
                       on_progress: Progress | None = None,
                       limit: int | None = None) -> int:
    """Read the text of indexed files that have only been seen by name.

    The sorter's own reading, file by file: its readers in its extraction pool
    (PDF, Word, text; Apple Vision OCR for images and scans), then its
    classifier and `assign`, and only then the file's text goes into search.
    So a file whose text says it is an identity document is protected before
    anything can find it by that text. Files already protected are not opened.
    Returns how many files were read.
    """
    from evidence_shape.store import RunWriter
    from extraction_pool import CONTRACT, DATALESS, PROTECTED, ExtractionRequest
    from extractors.authorship import SUBSYSTEM as P5
    from extractors.dispatch import current_versions
    from extractors.failure import ContractViolation
    from extractors.long_tail import record_sensitivity_signals
    from extractors.router import record_routing_decision, route
    from extractors.runs import extraction_status_by_tier
    from database_agent.files_table import set_extraction_status
    from evidence_shape.store import observation_keys_for_run
    from extractors.authorship import COMPONENT_VERSION as P5_VERSION
    from items.index_refresh import upsert_item_index
    from privacy.classification_store import ClassificationStore
    from privacy.learning_seam import assign

    report = on_progress or (lambda _stage, _done, _total: None)
    owed = _unread(conn)
    if limit is not None:
        owed = owed[:limit]
    total = len(owed)
    report("read", 0, total)
    if not owed:
        return 0
    authorities = _authorities(conn)
    pool = authorities.pool
    sink = RunWriter(conn, author=P5)
    store = ClassificationStore(conn)
    versions = current_versions()
    done = 0

    def submit(item_id: str, file_row: dict):
        path = Path(file_row["current_path"])
        decision = route(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            path=path, extension=file_row["extension"],
            detect_format=authorities.detect_format)
        stamp = authorities.now()
        return item_id, file_row, decision, stamp, pool.submit(ExtractionRequest(
            file_id=file_row["file_id"], file_row=file_row, decision=decision,
            path=path, now=stamp, context_window=authorities.context_window,
            versions=versions))

    def consume(item_id: str, file_row: dict, decision, stamp: str, handle):
        nonlocal done
        file_id, content_hash = file_row["file_id"], file_row["content_hash"]
        outcome = pool.result(handle)
        if outcome.kind == CONTRACT:
            raise ContractViolation(outcome.message)
        record_routing_decision(conn, decision)
        if outcome.kind not in (PROTECTED, DATALESS):
            results = outcome.dispatched.results
            signals = outcome.dispatched.sensitivity
            target = (results[outcome.dispatched.sensitivity_target]
                      if results else None)
            for result in results:
                run_id = sink.write(result)
                if signals and result is target:
                    record_sensitivity_signals(
                        conn, run_id=run_id, signals=signals,
                        observation_keys=observation_keys_for_run(conn, run_id),
                        now=stamp)
            set_extraction_status(
                conn, file_id, status_by_tier=extraction_status_by_tier(
                    [result.run for result in results]),
                author=P5, component_version=P5_VERSION)
        candidate = authorities.classify(conn, file_id, content_hash)
        if candidate is not None:
            assign(conn, candidate, store=store,
                   component_version=authorities.p7_component_version)
        # Judged first; searchable second.
        upsert_item_index(conn, item_id)
        conn.commit()
        done += 1
        report("read", done, total)

    # Submitted ahead, written in order: the pool's workers read in parallel,
    # and every database write stays on this thread.
    window: deque = deque()
    try:
        for item_id, file_row in owed:
            window.append(submit(item_id, file_row))
            while len(window) >= pool.lookahead:
                consume(*window.popleft())
        while window:
            consume(*window.popleft())
    finally:
        pool.close()
    return done


def _unread(conn: sqlite3.Connection) -> list[tuple[str, dict]]:
    """Live, unprotected files whose bytes have no reading beyond their name."""
    from items.file_identity import item_is_sensitive

    if not _has_table(conn, "extraction_runs"):
        return []
    rows = conn.execute(
        "SELECT i.item_id, f.* FROM items i JOIN files f ON f.file_id = i.file_id "
        "WHERE i.presence = 'live' AND i.superseded_by IS NULL "
        "AND i.item_type = 'file' AND f.scan_state = ? "
        "AND NOT EXISTS (SELECT 1 FROM extraction_runs r "
        "WHERE r.content_hash = f.content_hash "
        "AND r.analysis_tier != 'filesystem') "
        "ORDER BY f.current_path", (P1_INCLUDED_SCAN_STATE,)).fetchall()
    out = []
    for row in rows:
        if item_is_sensitive(conn, row["item_id"]):
            continue
        file_row = dict(row)
        out.append((file_row.pop("item_id"), file_row))
    return out


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
        unread_documents=len(_unread(conn)),
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
