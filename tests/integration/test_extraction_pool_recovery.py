# tests/integration/test_extraction_pool_recovery.py
"""A worker really dies, and the run really continues.

`ProcessPool`'s docstring makes a promise with a history behind it: commit 446d7f3
fixed exactly this shape at file level -- one zip with duplicate member names unwound
a 5,760-file run -- and a process pool reintroduces it one level up, because a
`BrokenProcessPool` fails EVERY future in flight and not only the one whose worker
died. So the promise is that a file which kills a worker becomes one `failed` run and
its neighbours are read normally.

**This file kills a worker for real.** `os._exit(1)` inside the reader, in a spawned
child, on one file of four. Nothing here simulates a crash by raising an exception:
an exception is caught by `perform` and turned into a `failed` run on the worker's own
thread, which is the path the OTHER tests cover and is not this one. The failure this
file is about is the one where the interpreter is gone and there is nobody left to
catch anything.

**Why a module-level factory.** `spawn` re-imports rather than inheriting, so what
crosses the boundary is a NAME. `_poisoned_context` is importable by the child from
this module; a closure or a fixture-built object would not be, and the test would
fail on pickling rather than on the thing it is about.
"""
import os
import sqlite3
import time
from pathlib import Path

import pytest

from database_agent.db import create_schema, open_database
from eval_harness.store import create_eval_schema
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter
from extraction_pool import ExtractionContext, ProcessPool
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

CLOCK = "2026-09-04T00:00:00+00:00"

#: The file that kills whichever worker opens it. Named, not chosen by content,
#: because the worker must die BEFORE it has read anything -- a crash after a partial
#: read is a different and easier failure.
POISON = "00-poison.pdf"

#: FIRST, and its neighbours are SLOW, and both of those are load-bearing. The first
#: version of this file put the poison in the middle of four instant readers, and it
#: passed while proving almost nothing: every innocent file had already finished
#: before the crash, so no neighbour was ever in flight and the recovery never had a
#: window to hold back or lose. Two sabotages of the recovery code left it green.
#:
#: The condition the recovery exists for is a crash WHILE OTHER FILES ARE BEING READ,
#: and a test has to arrange that rather than hope for it. Files are consumed in
#: submission order, so the poison goes first; the readers sleep so that the rest of
#: the look-ahead window is still outstanding when the worker dies.
CORPUS = (POISON, "01-alpha.pdf", "02-bravo.pdf", "03-charlie.pdf",
          "04-delta.pdf", "05-echo.pdf")

#: Long enough that a neighbour is certainly still running when the poison's worker
#: dies, short enough that the whole file costs a couple of seconds.
_READ_SECONDS = 0.5


def _read_pdf(path: Path) -> PdfDocument:
    if Path(path).name == POISON:
        # NOT an exception. `os._exit` skips every handler, flushes nothing and
        # leaves the executor with a worker that never answers -- which is what a
        # segfault inside Apple's Vision framework looks like from Python.
        os._exit(1)
    time.sleep(_READ_SECONDS)
    text = f"{Path(path).stem} is readable"
    return PdfDocument(metadata={}, pages=(PdfPage(
        number=1, text=text,
        regions=(Region(zone="body", start=0, end=len(text)),)),))


def _readers() -> Readers:
    return Readers(
        read_pdf=_read_pdf,
        read_docx=lambda path: DocxDocument(core_properties={}),
        read_text_document=lambda path: TextDocument(text="text"),
        read_long_tail=lambda path, transcribe=False: LongTailFile(),
        read_manifest=lambda path: ArchiveManifest(archive_type="zip"),
        read_image=lambda path: ImageRecord(image_format="PNG", dimensions="1x1",
                                            width=1, height=1),
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda width, height: None,
        filename_pattern=lambda name: None,
        ocr_engine=None,
    )


def _poisoned_context() -> ExtractionContext:
    """What a worker builds for itself. Named at module level so `spawn` can find it."""
    return ExtractionContext(
        policy=SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False),
        readers=_readers(),
        transcription_authorized=lambda: False)


@pytest.fixture()
def live_db(tmp_path: Path):
    conn = open_database(tmp_path / "recovery.sqlite")
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_facts_schema(conn)
    create_privacy_schema(conn)
    create_eval_schema(conn)
    yield conn
    conn.close()


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    root.mkdir()
    for index, name in enumerate(CORPUS):
        (root / name).write_bytes(b"%PDF-1.4 " + str(index).encode() * 8)
    return root


def _run(conn: sqlite3.Connection, root: Path, pool):
    selection = record_selection(conn, sources=[root], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return run_p1_p7(
        conn, selection, source=FilesystemCorpusSource(),
        mime_type_for=lambda path: "application/pdf", scan_state="scanned",
        budget_exhausted=lambda: False, detect_format=lambda path: "pdf",
        policy=SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False),
        readers=_readers(), sink=RunWriter(conn, author="P5"),
        now=lambda: CLOCK, context_window=40,
        transcription_authorized=lambda: False, corpus_form="snapshot",
        policy_settings={}, file_entry_body=lambda row: {"payload_ref": "blob"},
        resolve_native=lambda db, file_id, content_hash: None,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda db, file_id, content_hash: None,
        classify=lambda db, file_id, content_hash: None,
        classification_store=ClassificationStore(conn),
        p7_component_version="0.1.0", pool=pool)


@pytest.fixture()
def pool():
    #: Two workers and a look-ahead of two, so the poisoned file is genuinely in
    #: flight ALONGSIDE its neighbours when it kills its worker. One worker with a
    #: look-ahead of one would never put an innocent file at risk, and the innocent
    #: files are the point.
    #: `floor=0`, so every request really does go to a worker. The floor exists to
    #: keep small folders off the pool entirely, and a small folder is exactly what
    #: this corpus is -- with the shipped floor nothing here would ever cross a
    #: process boundary and the crash this file is about could not happen.
    built = ProcessPool(workers=2, context_factory=_poisoned_context,
                        lookahead_per_worker=2, floor=0)
    yield built
    built.close()


def _runs(conn):
    return {row[0]: (row[1], row[2]) for row in conn.execute(
        "SELECT f.filename, r.extractor_name, r.failure_reason "
        "FROM extraction_runs r JOIN files f ON f.file_id = r.file_id "
        "WHERE r.extractor_name != 'filesystem.record'")}


def test_a_file_that_kills_its_worker_becomes_one_failed_run(live_db, corpus, pool):
    """§2.4's rule, one level up. The file is unexamined and the row says so."""
    _run(live_db, corpus, pool)
    rows = _runs(live_db)
    assert POISON in rows, "the file that killed the worker got no run row at all"
    _, reason = rows[POISON]
    assert reason is not None, f"the poisoned file was recorded as a success: {rows}"
    assert "died twice" in reason, reason


def test_the_other_three_files_are_read_normally(live_db, corpus, pool):
    """The whole promise. One segfault must not cost the other files their reads --
    which is exactly what happens if the recovery resubmits the window with everybody's
    retry count bumped, or submits it back into the executor that just died."""
    _run(live_db, corpus, pool)
    rows = _runs(live_db)
    innocent = [name for name in CORPUS if name != POISON]
    assert sorted(rows) == sorted(CORPUS)
    for name in innocent:
        extractor, reason = rows[name]
        assert reason is None, f"{name} was failed by its neighbour's crash: {reason}"
        assert extractor == "pdf.text"


def test_their_evidence_is_really_there_and_is_their_own(live_db, corpus, pool):
    """A `complete` run with no observations would pass the test above and still be
    the silent-empty-document lie §2.4 forbids."""
    _run(live_db, corpus, pool)
    values = {row[0] for row in live_db.execute(
        "SELECT raw_value FROM evidence WHERE extractor_name = 'pdf.text'")}
    assert "01-alpha is readable" in values
    assert "03-charlie is readable" in values
    assert "05-echo is readable" in values
    assert not [v for v in values if "poison" in v], (
        "content was recorded for a file whose reader never returned")


def test_the_window_is_not_left_held_back_after_the_crash(live_db, corpus, pool):
    """`_rebuild` holds the rest of the window in `_deferred` while the suspect is
    retried alone, and `_release` puts it back. A path out that forgets to release
    leaves the caller waiting on a cancelled future, and the run stops on the file
    AFTER the crash rather than on the one that caused it."""
    _run(live_db, corpus, pool)
    assert pool._deferred == [], (
        "the look-ahead window was never resubmitted after the pool was rebuilt")
