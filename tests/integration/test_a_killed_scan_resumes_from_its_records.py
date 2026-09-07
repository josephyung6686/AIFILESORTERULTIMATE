# tests/integration/test_a_killed_scan_resumes_from_its_records.py
"""Phase 4 (b) -- a scan killed mid-extraction, and the run that comes after it.

`00`:136-153 is the contract this holds: a run is resumable because its records
say what happened, not because the disk can be re-read cheaply. A person whose
laptop slept during a two-hundred-file scan should not pay for the first hundred
twice, and should not end up with two answers about any of them.

**Two hundred files, because the failure is a counting failure.** With four files
a double-count is a typo you would see; at two hundred it is a number in a report
that nobody can check by eye. The corpus here is two hundred synthetic PDFs read
by an injected reader that parses nothing, so what is measured is the
orchestrator's bookkeeping and not a PDF library's throughput.

**The kill is the sink, and that is the honest place for it.** A reader that
raised would be a FAILED file -- P5 catches that and records it, which is a
different thing entirely and is already tested. A run that stops has its earlier
rows committed and its later ones never written, which is what a power cut or a
`kill -9` leaves behind, and the sink is the last thing standing between a
finished extraction and its row.

**Three assertions, and the third is the one `00`:136-153 actually asks for.**
The finished files are not read again; no file ends with two current answers; and
the number of files indexed equals the number reachable through the terminal
outcomes, so nothing has fallen between the two runs.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from database_agent.db import create_schema, open_database
from eval_harness.store import create_eval_schema
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter
from extraction_pool import ExtractionContext, InlinePool
from extractors.archive import ArchiveManifest
from extractors.dispatch import Readers
from extractors.docx import DocxDocument
from extractors.image import ImageRecord
from extractors.long_tail import LongTailFile
from extractors.pdf import PdfDocument, PdfPage
from extractors.reading import Region
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from extractors.structured_text import TextDocument
from facts.schema import create_facts_schema
from orchestrator import run_p1_p7
from privacy.classification_store import ClassificationStore
from privacy.schema import create_privacy_schema
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection

CLOCK = "2026-09-07T12:00:00+00:00"

#: Two hundred, per the item. Large enough that a double-count is a number rather
#: than something a reader would notice, small enough to stay a unit test.
CORPUS_SIZE = 200

#: Where the first run dies. Off a round number on purpose: a kill at exactly half
#: would pass a resumption that hardcoded the halfway point, which is not a thing
#: anybody would write but is the kind of thing a coincidence writes for you.
KILL_AFTER = 83


class _Killed(RuntimeError):
    """The machine stopped. Not a failure of any file -- a failure of the run."""


def _pdf(path: Path) -> PdfDocument:
    text = f"{path.stem} is readable"
    return PdfDocument(metadata={}, pages=(PdfPage(
        number=1, text=text,
        regions=(Region(zone="body", start=0, end=len(text)),)),))


class _CountingReaders:
    """`Readers`, with a tally of which files the PDF reader was handed.

    The tally is what proves the second run did not re-read: an assertion on
    elapsed time would prove the same thing on a fast machine and nothing on a
    slow one.
    """

    def __init__(self) -> None:
        self.read: list[str] = []

    def __call__(self) -> Readers:
        def read_pdf(path: Path) -> PdfDocument:
            self.read.append(Path(path).name)
            return _pdf(path)

        return Readers(
            read_pdf=read_pdf,
            read_docx=lambda path: DocxDocument(core_properties={}),
            read_text_document=lambda path: TextDocument(text="text"),
            read_long_tail=lambda path, transcribe=False: LongTailFile(),
            read_manifest=lambda path: ArchiveManifest(archive_type="zip"),
            read_image=lambda path: ImageRecord(image_format="PNG",
                                                dimensions="1x1", width=1, height=1),
            find_structured_strings=lambda text: (),
            recognize_markers=lambda names: (),
            dimension_signal=lambda width, height: None,
            filename_pattern=lambda name: None,
            ocr_engine=None)


class _SinkThatStops(RuntimeError):
    """Unused sentinel kept out of the way; the raise is `_Killed`."""


class _StoppingWriter:
    """`RunWriter`, until the nth run, and then the machine stops."""

    def __init__(self, inner: RunWriter, *, after: int) -> None:
        self._inner = inner
        self._after = after
        self.written = 0

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def write(self, *args, **kwargs):
        self.written += 1
        if self.written > self._after:
            raise _Killed(f"the machine stopped after {self._after} runs")
        return self._inner.write(*args, **kwargs)


@pytest.fixture()
def db(tmp_path: Path):
    conn = open_database(tmp_path / "resume.sqlite")
    for create in (create_schema, create_scan_schema, create_evidence_schema,
                   create_extraction_schema, create_facts_schema,
                   create_privacy_schema, create_eval_schema):
        create(conn)
    yield conn
    conn.close()


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    root.mkdir()
    for index in range(CORPUS_SIZE):
        (root / f"{index:03d}-paper.pdf").write_bytes(
            b"%PDF-1.4 " + str(index).encode() * 8)
    return root


def _context(readers_factory) -> ExtractionContext:
    return ExtractionContext(
        policy=SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False),
        readers=readers_factory(),
        transcription_authorized=lambda: False)


def _run(conn: sqlite3.Connection, root: Path, *, readers_factory, sink):
    """One scan. `InlinePool` on purpose: the reader's tally has to be readable
    from this process, and a spawned worker's counter is not."""
    selection = record_selection(conn, sources=[root], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return run_p1_p7(
        conn, selection, source=FilesystemCorpusSource(),
        mime_type_for=lambda path: "application/pdf", scan_state="scanned",
        budget_exhausted=lambda: False, detect_format=lambda path: "pdf",
        policy=SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False),
        readers=readers_factory(), sink=sink,
        now=lambda: CLOCK, context_window=40,
        transcription_authorized=lambda: False, corpus_form="snapshot",
        policy_settings={}, file_entry_body=lambda row: {"payload_ref": "blob"},
        resolve_native=lambda db, file_id, content_hash: None,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda db, file_id, content_hash: None,
        classify=lambda db, file_id, content_hash: None,
        classification_store=ClassificationStore(conn),
        p7_component_version="0.1.0",
        pool=InlinePool(_context(readers_factory)))


def _finished(conn) -> set[str]:
    """The filenames that have an extraction row right now.

    Not "the files a reader was handed": the kill lands between a read and its
    row, so exactly one file per interrupted run was read and never recorded. That
    file is owed a read and re-reading it is correct. `00`:136-153 asks that
    FINISHED files are not read again, and finished means recorded.
    """
    return {row[0] for row in conn.execute(
        "SELECT f.filename FROM extraction_runs r JOIN files f "
        "ON f.file_id = r.file_id WHERE r.extractor_name != 'filesystem.record'")}


def _kill_then_resume(conn, root):
    """The first run dies part way; the second finishes.

    Returns the second run's tally and what the first had FINISHED when it died.
    """
    first = _CountingReaders()
    stopping = _StoppingWriter(RunWriter(conn, author="P5"), after=KILL_AFTER)
    with pytest.raises(_Killed):
        _run(conn, root, readers_factory=first, sink=stopping)
    conn.commit()
    finished = _finished(conn)

    second = _CountingReaders()
    _run(conn, root, readers_factory=second, sink=RunWriter(conn, author="P5"))
    conn.commit()
    return finished, second


def _extraction_rows(conn):
    """One row per (file, extractor), with how many runs stand for it.

    `extraction_runs` carries no `superseded_by`: §8.2 makes a re-run at the same
    key legal and supersession is by `config_fingerprint`, latest wins. So the
    double-count this asks about is not a schema violation, it is the resumption
    doing work it did not need to -- a second row for a file the first run had
    already finished.
    """
    return conn.execute(
        "SELECT file_id, extractor_name, COUNT(*) FROM extraction_runs "
        "WHERE extractor_name != 'filesystem.record' "
        "GROUP BY file_id, extractor_name").fetchall()


# --- the run that died ---------------------------------------------------------

def test_the_first_run_really_did_die_part_way(db, corpus):
    """The guard on the guard. A kill that never fired would make every assertion
    below a statement about two identical complete runs."""
    stopping = _StoppingWriter(RunWriter(db, author="P5"), after=KILL_AFTER)
    with pytest.raises(_Killed):
        _run(db, corpus, readers_factory=_CountingReaders(), sink=stopping)
    db.commit()

    indexed = db.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    assert indexed > 0, "the killed run recorded no files at all"
    assert stopping.written > KILL_AFTER, "the kill never fired"


# --- what the second run does about it -----------------------------------------

def test_the_second_run_does_not_read_a_file_the_first_one_finished(db, corpus):
    """§1.2's stat cache, doing resumption's work without being called that.

    `orchestrator.py` says it: "on REUSE, P5 is not invoked and prior results
    stand". The tally is the proof -- a file whose bytes, size and mtime are
    unchanged and whose extraction already has a row is not handed to a reader a
    second time.
    """
    finished, second = _kill_then_resume(db, corpus)

    assert finished, "the first run finished nothing, so there is nothing to reuse"
    repeated = finished & set(second.read)
    assert not repeated, (
        f"{len(repeated)} file(s) the first run had already finished were read "
        f"again: {sorted(repeated)[:5]}")
    # And the resumption did real work rather than skipping everything, which is
    # the failure this whole file exists to have caught.
    assert second.read, "the second run read nothing at all"


def test_no_file_ends_with_two_current_answers(db, corpus):
    """The double-count. Two live rows for one file and one extractor is two
    answers to one question, and every count a person is shown downstream is a
    query against these rows."""
    _kill_then_resume(db, corpus)

    doubled = [(file_id, extractor, count)
               for file_id, extractor, count in _extraction_rows(db) if count > 1]
    assert not doubled, f"files with more than one live run: {doubled[:5]}"


def test_the_corpus_is_indexed_exactly_once_across_the_two_runs(db, corpus):
    """Two runs over one folder are one corpus, not two. A second `files` row for
    the same path would double every count the report prints."""
    _kill_then_resume(db, corpus)

    indexed = db.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    distinct = db.execute("SELECT COUNT(DISTINCT current_path) FROM files").fetchone()[0]
    assert indexed == CORPUS_SIZE, f"{indexed} rows for {CORPUS_SIZE} files"
    assert distinct == indexed, "one path is recorded twice"


def test_every_indexed_file_is_reachable_through_a_terminal_outcome(db, corpus):
    """`00`:136-153's own arithmetic, and the assertion the item asks for.

    The file count must equal the union of the terminal outcomes: a file that
    finished, a file that failed and a file nothing reached are three different
    answers and every indexed file has exactly one of them. A file in none of them
    is the silent omission `84` §1 forbids -- it was read, it is in the database,
    and no line a person sees would mention it.
    """
    _kill_then_resume(db, corpus)

    indexed = {row[0] for row in db.execute("SELECT file_id FROM files")}
    with_a_run = {row[0] for row in db.execute(
        "SELECT DISTINCT file_id FROM extraction_runs")}
    unaccounted = indexed - with_a_run

    assert not unaccounted, (
        f"{len(unaccounted)} indexed file(s) reached no terminal outcome across "
        f"either run: {sorted(unaccounted)[:5]}")
    assert len(indexed) == CORPUS_SIZE
