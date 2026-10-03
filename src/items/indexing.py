"""Index a folder in one fast pass, and count what the person has.

The sorter's own sequence -- R1 selection, P3 scan, item projection -- then the
search tables. No cloud call. Every file ends up indexed, set aside (counted)
or protected (counted); `counts` reads those totals back from the database.
"""
from __future__ import annotations

import os
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
    #: Files whose reading was tried and gave no text (a reader failed, took
    #: too long, or there is no reader for the kind); found by name only.
    unreadable_documents: int = 0


#: How long one file may take to read before it is skipped and counted as
#: unreadable. The pool kills a worker at this ceiling and gives the file one
#: more try, so a wedged file costs at most twice this.
READ_SECONDS_PER_FILE: float = 60.0


class ReadOutcome(int):
    """How many files `read_document_text` finished -- an int, so a caller
    that only counts keeps working -- plus how many of those gave no text and
    how many turned out to be personal once read."""

    unreadable: int
    protected_newly_found: int
    #: The items found personal once read, so the person can be told which.
    protected_items: tuple[str, ...]

    def __new__(cls, read: int, *, unreadable: int = 0,
                protected_items: tuple[str, ...] = ()) -> "ReadOutcome":
        made = super().__new__(cls, read)
        made.unreadable = unreadable
        made.protected_items = tuple(protected_items)
        made.protected_newly_found = len(made.protected_items)
        return made


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
                       limit: int | None = None) -> ReadOutcome:
    """Read the text of indexed files that have only been seen by name.

    The sorter's own reading, file by file: its readers in its extraction pool
    (PDF, Word, text; Apple Vision OCR for images and scans), then its
    classifier and `assign`, and only then the file's text goes into search.
    So a file whose text says it is an identity document is protected before
    anything can find it by that text. Files already protected are not opened.

    Every file ends: read, or counted unreadable with a reason. One file's
    failure never stops the rest, a file gets `READ_SECONDS_PER_FILE` (and one
    retry) before it is skipped, and each file is committed as it finishes, so
    a later call carries on where this one stopped.
    """
    from dataclasses import replace

    from cli import (EXTRACTION_LOOKAHEAD_PER_WORKER, EXTRACTION_WORKERS,
                     extraction_context)
    import extraction_pool
    from evidence_shape.store import RunWriter
    from extraction_pool import CONTRACT, DATALESS, PROTECTED, ExtractionRequest
    from extractors.authorship import SUBSYSTEM as P5
    from extractors.dispatch import current_versions
    from extractors.long_tail import record_sensitivity_signals
    from extractors.router import record_routing_decision, route
    from extractors.runs import extraction_status_by_tier
    from database_agent.files_table import set_extraction_status
    from evidence_shape.store import observation_keys_for_run
    from extractors.authorship import COMPONENT_VERSION as P5_VERSION
    from items.file_identity import item_is_sensitive
    from items.hot_index import _text_was_read
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
        return ReadOutcome(0)
    pool = extraction_pool.ProcessPool(
        workers=EXTRACTION_WORKERS, context_factory=extraction_context,
        lookahead_per_worker=EXTRACTION_LOOKAHEAD_PER_WORKER,
        seconds_per_extraction=READ_SECONDS_PER_FILE)
    authorities = replace(_authorities(conn), pool=pool)
    sink = RunWriter(conn, author=P5)
    store = ClassificationStore(conn)
    versions = current_versions()
    done = unreadable = 0
    newly_protected: list[str] = []

    def submit(item_id: str, file_row: dict):
        path = Path(file_row["current_path"])
        try:
            decision = route(
                file_id=file_row["file_id"],
                content_hash=file_row["content_hash"], path=path,
                extension=file_row["extension"],
                detect_format=authorities.detect_format)
            stamp = authorities.now()
            handle = pool.submit(ExtractionRequest(
                file_id=file_row["file_id"], file_row=file_row,
                decision=decision, path=path, now=stamp,
                context_window=authorities.context_window, versions=versions))
        except Exception as error:                   # noqa: BLE001
            return item_id, file_row, None, None, error
        return item_id, file_row, decision, stamp, handle

    def judge(item_id: str, file_row: dict, decision, stamp: str, handle):
        """Write one file's reading, judge it, then make it searchable.
        Returns why it gave no text, or None when it was read."""
        if isinstance(handle, Exception):
            raise handle
        file_id, content_hash = file_row["file_id"], file_row["content_hash"]
        outcome = pool.result(handle)
        if outcome.kind == CONTRACT:
            raise RuntimeError(outcome.message)
        if outcome.kind in (PROTECTED, DATALESS):
            return ("inside a protected folder" if outcome.kind == PROTECTED
                    else "not downloaded to this Mac")
        record_routing_decision(conn, decision)
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
        return None if _text_was_read(conn, content_hash) else "no text"

    def consume(item_id: str, file_row: dict, decision, stamp, handle):
        nonlocal done, unreadable
        try:
            reason = judge(item_id, file_row, decision, stamp, handle)
        except Exception as error:                   # noqa: BLE001
            conn.rollback()
            reason = f"{type(error).__name__}: {error}"[:300]
            _note_unreadable(conn, file_row["content_hash"], reason)
        else:
            if reason is not None and reason != "no text":
                _note_unreadable(conn, file_row["content_hash"], reason)
        if reason is not None:
            unreadable += 1
        if item_is_sensitive(conn, item_id):
            newly_protected.append(item_id)
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
    return ReadOutcome(done, unreadable=unreadable,
                       protected_items=newly_protected)


_UNREADABLE_DDL = """
CREATE TABLE IF NOT EXISTS unreadable_documents (
    content_hash TEXT PRIMARY KEY,
    reason TEXT NOT NULL,
    noted_at TEXT NOT NULL
);
"""


def _note_unreadable(conn: sqlite3.Connection, content_hash: str,
                     reason: str) -> None:
    """A file the reading pass gave up on outside a reader's own failed run,
    so it is counted and not owed again. Never raises: a database that will
    not take the note leaves the file owed, which is the safe direction."""
    from datetime import datetime, timezone
    try:
        conn.execute(_UNREADABLE_DDL)
        conn.execute(
            "INSERT OR REPLACE INTO unreadable_documents VALUES (?, ?, ?)",
            (content_hash, reason, datetime.now(timezone.utc).isoformat()))
    except sqlite3.Error:
        conn.rollback()


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
        + ("AND f.content_hash NOT IN (SELECT content_hash FROM "
           "unreadable_documents) " if _has_table(conn, "unreadable_documents")
           else "")
        + "ORDER BY f.current_path", (P1_INCLUDED_SCAN_STATE,)).fetchall()
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
    """Indexed, set aside, protected, held and open questions, from the DB.

    Every number is FILES, and indexed + set aside + protected is every file
    under the chosen folders: indexed never includes a protected file, set
    aside counts the files inside each set-aside folder (listed, never read),
    and a protected container counts as one thing because it is never opened.
    """
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
        indexed=len(live) - len(sensitive),
        set_aside=sum(_files_under(Path(a["folder"])) for a in set_aside),
        set_aside_folders=len(set_aside),
        protected=len(protected_areas) + len(sensitive),
        held=sum(1 for row in live if row["typing_state"] == "held"),
        open_questions=_open_questions(conn),
        unread_documents=len(_unread(conn)),
        unreadable_documents=_unreadable(conn),
    )


def _files_under(path: Path) -> int:
    """Files at or under `path`, listed with scandir and never opened.
    Symlinks are not followed; a protected container (an app) inside counts
    as one thing and is not listed; a folder that cannot be listed counts 0."""
    try:
        if not path.is_dir() or path.is_symlink():
            return 1 if path.is_file() else 0
    except OSError:
        return 0
    from scan_agent.exclusion import is_protected_container

    total, folders = 0, [path]
    while folders:
        try:
            with os.scandir(folders.pop()) as entries:
                for entry in entries:
                    if entry.is_dir(follow_symlinks=False):
                        if is_protected_container(entry.path):
                            total += 1           # one thing, never listed
                        else:
                            folders.append(Path(entry.path))
                    elif entry.is_file(follow_symlinks=False):
                        total += 1
        except OSError:
            continue
    return total


#: The detector's safety domain, in a person's words.
_DOMAIN_REASONS = {
    "identity": "looks like an ID document",
    "medical": "health record",
    "finance": "money or bank record",
    "legal": "legal document",
}


def protected_reasons(conn: sqlite3.Connection) -> list[dict]:
    """Each protected thing counted in `counts().protected`, and why, in
    plain words: name, folder, reason. Nothing is opened to answer."""
    from datetime import datetime, timezone

    from cli import _RECOGNITION_MANIFEST, build_detector
    from items.file_identity import _PROTECTED_EXTENSIONS, _PROTECTED_PARTS
    from items.file_identity import item_is_sensitive
    from items.identity import excluded_areas
    from privacy.classification_store import ClassificationStore
    from recognition.rules import load_rules
    from scan_agent.exclusion import is_protected_container

    if not _has_table(conn, "items"):
        return []
    out = [{"name": Path(a["folder"]).name,
            "folder": str(Path(a["folder"]).parent),
            "reason": "app or system item"}
           for a in excluded_areas(conn) if a["protected"]]
    detector = None
    store = ClassificationStore(conn) if _has_table(
        conn, "classifications") else None
    rows = conn.execute(
        "SELECT i.item_id, i.display_label, i.open_target, i.file_id, "
        "f.content_hash FROM items i LEFT JOIN files f ON f.file_id = i.file_id "
        "WHERE i.presence = 'live' AND i.superseded_by IS NULL "
        "AND i.item_type = 'file'").fetchall()
    for row in rows:
        if not item_is_sensitive(conn, row["item_id"]):
            continue
        target = row["open_target"] or ""
        lower = target.casefold()
        parts = {part.casefold() for part in Path(target).parts}
        try:
            record = (store.current(row["file_id"], row["content_hash"])
                      if store is not None and row["content_hash"] else None)
        except Exception:                            # noqa: BLE001
            record = None
        if record is not None and record.basis == "user":
            reason = "you protected it"
        elif target and is_protected_container(target):
            reason = "app or system item"
        elif parts & _PROTECTED_PARTS or any(
                lower.endswith(ext) for ext in _PROTECTED_EXTENSIONS):
            reason = "key or password file"
        else:
            if detector is None:
                detector = build_detector(
                    conn, load_rules(_RECOGNITION_MANIFEST.read_text),
                    now=lambda: datetime.now(timezone.utc).isoformat())
            reason = _domain_reason(conn, detector, row["file_id"],
                                    row["content_hash"])
        out.append({"name": row["display_label"],
                    "folder": str(Path(target).parent) if target else "",
                    "reason": reason})
    return sorted(out, key=lambda r: (r["folder"], r["name"]))


def _domain_reason(conn, detector, file_id: str, content_hash: str) -> str:
    """Which safety domain the rules held the file under, in plain words."""
    try:
        report = detector.precaution_report(
            conn, detector.explain(conn, file_id, content_hash),
            file_id=file_id, content_hash=content_hash)
    except Exception:                                # noqa: BLE001
        report = None
    if report is None:
        return "looks personal"
    return _DOMAIN_REASONS.get(report.schema_id, "looks personal")


def _unreadable(conn: sqlite3.Connection) -> int:
    """Live files whose reading was tried and gave no text."""
    if not _has_table(conn, "extraction_runs"):
        return 0
    noted = ("OR f.content_hash IN (SELECT content_hash FROM "
             "unreadable_documents)" if _has_table(conn, "unreadable_documents")
             else "")
    return conn.execute(
        "SELECT COUNT(*) FROM items i JOIN files f ON f.file_id = i.file_id "
        "WHERE i.presence = 'live' AND i.superseded_by IS NULL "
        "AND i.item_type = 'file' AND f.scan_state = ? AND (("
        "EXISTS (SELECT 1 FROM extraction_runs r WHERE r.content_hash = "
        "f.content_hash AND r.analysis_tier != 'filesystem') "
        "AND NOT EXISTS (SELECT 1 FROM extraction_runs r WHERE r.content_hash "
        "= f.content_hash AND r.analysis_tier != 'filesystem' "
        "AND r.completeness NOT IN ('failed', 'unsupported'))) " + noted + ")",
        (P1_INCLUDED_SCAN_STATE,)).fetchone()[0]


def _open_questions(conn: sqlite3.Connection) -> int:
    if not _has_table(conn, "structural_questions"):
        return 0
    from questions.store import open_questions
    return len(open_questions(conn))


def _has_table(conn: sqlite3.Connection, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (name,)).fetchone() is not None
