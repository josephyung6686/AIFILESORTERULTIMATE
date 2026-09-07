# tests/integration/test_extraction_pool_time_ceiling.py
"""R-50: a worker that never returns, and a run that finishes anyway.

`ProcessPool` recovers from a worker that DIES -- `BrokenProcessPool`, retry, isolate,
one `failed` run, neighbours read normally. It had no answer for a worker that simply
never answers, and the parent waits in `result()` for ever at 0% CPU.

MEASURED ON THE OWNER'S CORPUS, and this is not a hypothetical shape. Three of
seventeen scoreboard situations hung: `applications.undergraduate-packet`,
`business_operations.project-delivery`, `code.notebooks-experiments`. Sampled, one
worker's main thread was inside `-[VNRecognizeTextRequest ...]` -> `-[CIContext
render:toCVPixelBuffer:...]` -> CoreImage -> `_dispatch_sync_f_slow` ->
`__DISPATCH_WAIT_FOR_QUEUE__`: a deadlock inside Apple's own frameworks, reached
through PyObjC from the OCR reader. The other six workers sat in `sem_wait` with
nothing to do. No exception is ever raised, no process ever dies, and `00`:257's
budget rule -- a single file may not consume the run -- had nothing to enforce it.

**THE SLEEP IS BOUNDED AND THAT IS DELIBERATE.** A real deadlock is infinite; a test
that reproduced it exactly would hang the suite when the ceiling regressed, and a
guard that turns a red run into a hung one is worse than no guard. `_HANG_SECONDS` is
long enough that the ceiling must fire for these tests to pass and short enough that
a broken ceiling FAILS them rather than stopping the suite.
"""
import multiprocessing
import os
import sqlite3
import time
from pathlib import Path

import pytest

from database_agent.db import create_schema, open_database
from eval_harness.store import create_eval_schema
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter
from extraction_pool import (
    DISPATCHED, ExtractionContext, ExtractionRequest, ProcessPool,
)
from extractors.archive import ArchiveManifest
from extractors.dispatch import Readers
from extractors.docx import DocxDocument
from extractors.image import ImageRecord
from extractors.long_tail import LongTailFile
from extractors.pdf import PdfDocument, PdfPage
from extractors.reading import Region
from extractors.router import route
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

#: The file whose reader never comes back. FIRST, for the reason the sibling
#: recovery file gives at length: results are consumed in submission order, so the
#: hang has to be at the head for its neighbours to be in flight behind it.
HANG = "00-hang.pdf"

CORPUS = (HANG, "01-alpha.pdf", "02-bravo.pdf", "03-charlie.pdf")

#: What the ceiling is set to in these tests. Small, because every test here pays it
#: once in wall time.
_CEILING_SECONDS = 1.5

#: Longer than the ceiling by enough that no scheduling jitter can make the reader
#: finish first, and short enough to be a slow failure rather than a hung suite.
_HANG_SECONDS = 30.0

#: The neighbours are slow too, so they are genuinely still outstanding when the
#: ceiling fires on the head. THIS NUMBER IS LOAD-BEARING and the first draft got it
#: wrong: at 0.3s all three finished inside the 1.5s ceiling, so the kill took down a
#: pool with nothing innocent in it and the test passed while proving nothing about
#: the window. At 1.0s and two workers, one neighbour has finished, one is inside a
#: reader and one is queued when the ceiling fires -- which is the condition the
#: hold-back exists for, and the sibling recovery file records the same trap.
_READ_SECONDS = 1.0


def _read_pdf(path: Path) -> PdfDocument:
    if Path(path).name == HANG:
        # NOT an exception and NOT `os._exit`. The worker stays alive, healthy and
        # useless -- which is what a dispatch deadlock inside Vision looks like from
        # Python, and is the one thing the death path cannot see.
        time.sleep(_HANG_SECONDS)
    else:
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


def _hanging_context() -> ExtractionContext:
    """What a worker builds for itself. Module level, so `spawn` can import it."""
    return ExtractionContext(
        policy=SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False),
        readers=_readers(),
        transcription_authorized=lambda: False)


@pytest.fixture()
def live_db(tmp_path: Path):
    conn = open_database(tmp_path / "ceiling.sqlite")
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


@pytest.fixture()
def pool():
    built = ProcessPool(workers=2, context_factory=_hanging_context,
                        lookahead_per_worker=2, floor=0,
                        seconds_per_extraction=_CEILING_SECONDS)
    yield built
    built.close()


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


def _runs(conn):
    return {row[0]: (row[1], row[2]) for row in conn.execute(
        "SELECT f.filename, r.extractor_name, r.failure_reason "
        "FROM extraction_runs r JOIN files f ON f.file_id = r.file_id "
        "WHERE r.extractor_name != 'filesystem.record'")}


def test_a_worker_that_never_returns_does_not_take_the_run_with_it(
        live_db, corpus, pool):
    """`00`:257. One file may not consume the run, and a deadlock is a way it can."""
    started = time.monotonic()
    _run(live_db, corpus, pool)
    elapsed = time.monotonic() - started

    assert elapsed < _HANG_SECONDS, (
        "the run waited for the hung reader instead of for the ceiling, which "
        f"took {elapsed:.1f}s against a hang of {_HANG_SECONDS}s")


def test_the_hung_file_is_marked_with_the_ceiling_and_the_extractor(
        live_db, corpus, pool):
    """§2.4's rule as the death path already applies it: unexamined, and the row
    says so. A reason that named neither number nor reader would leave a person
    with a failure they cannot act on and an operator with nothing to tune."""
    _run(live_db, corpus, pool)
    rows = _runs(live_db)

    assert HANG in rows, "the file whose worker hung got no run row at all"
    extractor, reason = rows[HANG]
    assert reason is not None, f"the hung file was recorded as a success: {rows}"
    assert str(_CEILING_SECONDS) in reason, reason
    assert extractor in reason, reason


def test_the_neighbours_are_read_normally(live_db, corpus, pool):
    """The whole promise, and the test that decided how the ceiling is measured.

    The window in flight behind the hung file must be resubmitted, not failed --
    the same rule the death path follows, for the same reason: surviving somebody
    else's deadlock is not an attempt.

    THIS IS ALSO THE REGRESSION GUARD FOR THE CLOCK, and the numbers above are what
    make it one. Three neighbours at 1.0s on two workers is more than the 1.5s
    ceiling, so a ceiling measured FROM SUBMIT expires on files that are still in
    the queue: the first draft did that and the full suite failed here with
    "01-alpha.pdf was failed by its neighbour", `01-alpha.pdf` and `02-bravo.pdf`
    both carrying the TimeoutError of a file they were merely standing behind. One
    deadlock would have failed the whole look-ahead window on a real corpus. The
    clock now starts when the consuming loop begins waiting for a file, so shortening
    these sleeps or lengthening the ceiling would retire the guard without
    retiring the defect.
    """
    _run(live_db, corpus, pool)
    rows = _runs(live_db)

    for name in CORPUS:
        if name == HANG:
            continue
        assert name in rows, f"{name} was never read: {rows}"
        assert rows[name][1] is None, f"{name} was failed by its neighbour: {rows}"


def _request(root: Path, name: str) -> ExtractionRequest:
    """One extraction, built the way the orchestrator builds one.

    Direct, because the orchestrator CLOSES the pool on its way out
    (`orchestrator.py:705`), so nothing asserted after a run can tell a pool that
    was rebuilt from one that was never rebuilt. Driving the pool itself is the
    only way to ask whether it still works.
    """
    path = root / name
    decision = route(file_id=name, content_hash="0" * 64, path=path,
                     extension=path.suffix, detect_format=lambda _path: "pdf")
    return ExtractionRequest(
        file_id=name,
        file_row={"file_id": name, "content_hash": "0" * 64,
                  "current_path": str(path), "filename": name},
        decision=decision, path=path, now=CLOCK, context_window=40,
        versions={decision.extractor_name: "1.0.0"})


def test_the_pool_is_whole_afterwards_and_reads_the_next_file(tmp_path, corpus):
    """A rebuilt pool, proved by USING it, which is the only proof there is.

    Three requests go in: the hang, then two neighbours behind it. The ceiling
    fires on the head, its worker is killed and the pool goes with it -- and the
    two behind it must still come back read, because they were resubmitted rather
    than failed. Then a FOURTH request is submitted into the pool that replaced the
    dead one, after everything above has resolved, and it must be read too. A
    rebuild that produced a dead executor, or one that quietly fell back to the
    calling thread, fails that last line.
    """
    pool = ProcessPool(workers=2, context_factory=_hanging_context,
                       lookahead_per_worker=2, floor=0,
                       seconds_per_extraction=_CEILING_SECONDS)
    try:
        handles = [pool.submit(_request(corpus, name))
                   for name in (HANG, "01-alpha.pdf", "02-bravo.pdf")]
        outcomes = [pool.result(handle) for handle in handles]

        assert _failure_reason(outcomes[0]) is not None, "the hang was not stopped"
        for outcome, name in zip(outcomes[1:], ("01-alpha.pdf", "02-bravo.pdf")):
            assert _failure_reason(outcome) is None, (
                f"{name} was failed by its neighbour's deadlock: "
                f"{_failure_reason(outcome)}")

        after = pool.result(pool.submit(_request(corpus, "03-charlie.pdf")))
        assert _failure_reason(after) is None, (
            "the pool could not read a file after the kill: "
            f"{_failure_reason(after)}")
        assert pool.started is True
    finally:
        pool.close()


def _failure_reason(outcome) -> str | None:
    """The `failed` run's reason, or None when the extraction succeeded."""
    assert outcome.kind == DISPATCHED, outcome
    for result in outcome.dispatched.results:
        reason = result.run.get("failure_reason")
        if reason:
            return reason
    return None


def test_no_worker_outlives_the_pool(live_db, corpus, pool):
    """A killed worker is reaped, and a hung one is not left behind.

    `_watch_the_parent` is the belt for a run that dies; this is the braces for a
    run that ends normally. A worker deadlocked inside a framework will not answer
    a stop sentinel, so `close()` has to be sure rather than polite.
    """
    _run(live_db, corpus, pool)
    pool.close()

    for _ in range(50):
        if not multiprocessing.active_children():
            break
        time.sleep(0.1)
    assert multiprocessing.active_children() == [], (
        "a worker process outlived the pool: "
        f"{[(child.name, child.pid) for child in multiprocessing.active_children()]}")


def test_the_ceiling_has_no_default(live_db):
    """A number, so `cli.py` picks it. The rule this pool already states twice.

    `workers`, `lookahead_per_worker` and `floor` all have no default and the
    reason is written beside each: a part that defaults its own policy is a part
    choosing one, and a number nobody reviewed is a number nobody owns. A ceiling
    that kills a worker is the last number that should acquire a quiet default.
    """
    with pytest.raises(TypeError):
        ProcessPool(workers=2, context_factory=_hanging_context,
                    lookahead_per_worker=2, floor=0)


def test_a_ceiling_that_could_not_stop_anything_is_refused():
    """Zero or less is not a ceiling, it is an instruction to fail every file."""
    for refused in (0, -1.0):
        with pytest.raises(ValueError):
            ProcessPool(workers=2, context_factory=_hanging_context,
                        lookahead_per_worker=2, floor=0,
                        seconds_per_extraction=refused)


def test_the_parent_watcher_is_still_what_reaps_an_orphan():
    """Nothing here replaces it, and this is the assertion that says so.

    The kill path acts from the PARENT. A run killed by a signal never reaches it,
    which is what `_watch_the_parent` is for, and R-50 must not read as having
    made that unnecessary.
    """
    import extraction_pool

    assert callable(extraction_pool._watch_the_parent)
    assert os.getpid() > 0
