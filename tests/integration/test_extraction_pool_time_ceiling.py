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

R-112 ADDED THE SECOND ATTEMPT. The kill was final and the file was written off, and
eleven runs of the product over one pinned 263-file corpus showed that is the wrong
answer: the same PNG, content hash `782ff3d1...`, was read completely in ten of them
and wedged its worker in the eleventh -- the run that cost 626.4 seconds against 20 to
26 for the rest, which is the whole of the "620 second cold path" this was first
reported as. Sampled at the wedge, the worker was waiting on `CI::KernelCompileQueue`,
which was blocked in `flock()` inside `MTLCompilerFSCache::openSync`: the Metal shader
compiler's on-disk cache lock, shared by every process on the machine. So the file was
never unreadable, and it is retried once, in the same run, before it is failed.

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

#: What the ceiling is set to in the tests that still run on the REAL clock. It was
#: 1.5, chosen tight so that three 1.0s neighbours on two workers would exceed it and
#: catch a ceiling measured from submit. That relationship made this number a guard
#: and also made it a race: at load 13, with eight suites running, the neighbours
#: overran 1.5s on CPU contention and two tests failed with `01-alpha.pdf was failed
#: by its neighbour` -- a true sentence about the machine and a false one about the
#: code. The guard moved to `_ScriptedClock`, where fake time cannot be slowed down
#: by anything, so this number is now free to be generous: eight times the 1.0s a
#: neighbour needs, and still under `_HANG_SECONDS` so the hang is stopped.
_CEILING_SECONDS = 8.0

#: Longer than the ceiling by enough that no scheduling jitter can make the reader
#: finish first, and short enough to be a slow failure rather than a hung suite.
#:
#: R-112 RAISED IT, because a file may now cost TWO ceilings rather than one. The
#: number's job is to be unreachable when the ceiling works and reached when it does
#: not, and a permanently hung file is now killed twice before it is failed -- so a
#: number that only cleared one ceiling would stop separating the two answers.
_HANG_SECONDS = 90.0

#: The ceiling the fake-clock tests run under, in FAKE seconds. Large on purpose:
#: under a driven clock the only wait that ends at a ceiling is the one the script
#: sends past it, so every other wait has headroom no machine load can eat.
_FAKE_CEILING_SECONDS = 60.0

#: How far the scripted clock jumps. Past `_FAKE_CEILING_SECONDS` by a wide margin,
#: so the crossing is unambiguous rather than a subtraction that lands near zero.
_FAKE_JUMP_SECONDS = 10_000.0


class _ScriptedClock:
    """A monotonic source in fake seconds, driven rather than observed.

    WHY THESE TESTS STOPPED USING THE REAL ONE. The defect this file guards is a
    ceiling measured from SUBMIT rather than from the moment the consuming loop
    begins waiting for a file. Expressed in real seconds that is a race -- sleeping
    neighbours against a wall clock -- and a race is decided by the machine. Both
    of the tests below failed at load 13 while eight suites ran, with `01-alpha.pdf
    was failed by its neighbour`, on CPU contention and not on the clock. The
    semantics are what the guard is about, so the clock is what the test drives.

    `jump_after` counts CALLS, not files, because that is what `ProcessPool.result`
    actually does: one read to set the deadline, then one per wait. With
    `jump_after=1` the first wait of the first `result()` finds the ceiling already
    crossed and nothing else ever does.

    `jumps` BOUNDS HOW MANY LEAPS THERE ARE, and R-112's retry is why it exists. A
    file the ceiling kills is now tried a second time, and `result` reads the clock
    three more times to do it: the wait that expires, the retry's deadline, and the
    retry's own wait. So a file that must exhaust BOTH of its attempts needs
    `jumps=3`, and after the budget is spent fake time stands still -- which is what
    keeps every neighbour's fresh ceiling uncrossable, the property the test below
    exists to hold. An unbounded clock would expire the neighbours too and prove the
    opposite of what it was written to prove.
    """

    def __init__(self, *, jump_after: int, jumps: int = 1) -> None:
        self.calls = 0
        self._jump_after = jump_after
        self._budget = jumps
        self._now = 0.0

    def __call__(self) -> float:
        self.calls += 1
        if self.calls > self._jump_after and self._budget:
            self._budget -= 1
            self._now += _FAKE_JUMP_SECONDS
        return self._now

#: The neighbours are slow too, so they are genuinely still outstanding when the
#: ceiling fires on the head. THIS NUMBER IS LOAD-BEARING and the first draft got it
#: wrong: at 0.3s all three finished inside the 1.5s ceiling, so the kill took down a
#: pool with nothing innocent in it and the test passed while proving nothing about
#: the window. At 1.0s and two workers, one neighbour has finished, one is inside a
#: reader and one is queued when the ceiling fires -- which is the condition the
#: hold-back exists for, and the sibling recovery file records the same trap.
_READ_SECONDS = 1.0


def _readable(path: Path) -> PdfDocument:
    text = f"{Path(path).stem} is readable"
    return PdfDocument(metadata={}, pages=(PdfPage(
        number=1, text=text,
        regions=(Region(zone="body", start=0, end=len(text)),)),))


def _read_pdf(path: Path) -> PdfDocument:
    if Path(path).name == HANG:
        # NOT an exception and NOT `os._exit`. The worker stays alive, healthy and
        # useless -- which is what a dispatch deadlock inside Vision looks like from
        # Python, and is the one thing the death path cannot see.
        time.sleep(_HANG_SECONDS)
    else:
        time.sleep(_READ_SECONDS)
    return _readable(path)


#: Where the reader below records that one attempt has already been made. A FILE and
#: not a variable, because the two attempts happen in two different processes: the
#: pool kills every worker before it retries, so nothing in the first worker's memory
#: survives to tell the second one anything.
_HANG_ONCE_MARKER = "GRAPH_AGENT_TEST_HANG_ONCE_MARKER"


def _read_pdf_hanging_once(path: Path) -> PdfDocument:
    """Wedged on the first attempt, readable on the second. R-112's measured shape.

    Not a weaker version of `_read_pdf` but a truer one. Measured over eleven runs of
    the product on one 263-file corpus: the same PNG, byte for byte, was read
    completely in ten of them and wedged its worker in the eleventh, inside the FIRST
    Vision call that worker made -- `CI::ProgramNode::mainProgram` waiting on
    `CI::KernelCompileQueue`, which was itself blocked in `flock()` inside
    `MTLCompilerFSCache::openSync`. That is machine state, not the file's bytes, and
    a second attempt does not meet it. `_read_pdf` is the other half of the same
    truth -- a file whose reader never comes back at all -- and both are kept.
    """
    marker = Path(os.environ[_HANG_ONCE_MARKER])
    if Path(path).name == HANG and not marker.exists():
        # Written BEFORE the sleep, so the mark exists no matter when this worker is
        # killed. A worker killed with SIGKILL runs nothing on its way out.
        marker.write_text("one attempt has been made")
        time.sleep(_HANG_SECONDS)
    return _readable(path)


def _readers(read_pdf=_read_pdf) -> Readers:
    return Readers(
        read_pdf=read_pdf,
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


def _hanging_once_context() -> ExtractionContext:
    """The same, with the reader that wedges once. Module level, for `spawn`."""
    return ExtractionContext(
        policy=SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False),
        readers=_readers(_read_pdf_hanging_once),
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
    # R-112. The row has to say the run tried again, because it did: a file the
    # ceiling kills is retried once, and a reason that named one ceiling would
    # describe half of what happened to this file.
    assert "twice" in reason, reason


def test_a_ceiling_measured_from_submit_would_fail_the_queued_neighbours(
        tmp_path, corpus):
    """The whole promise, and the test that decided how the ceiling is measured.

    The window in flight behind the hung file must be resubmitted, not failed --
    the same rule the death path follows, for the same reason: surviving somebody
    else's deadlock is not an attempt.

    THE CLOCK IS DRIVEN, AND THAT IS WHAT MAKES THIS A GUARD RATHER THAN A RACE.
    The script sends fake time 10,000 seconds past a 60-second ceiling during the
    hung file's wait. Every neighbour was submitted BEFORE that jump, so a ceiling
    measured from submit finds all of them expired the moment it looks -- which is
    exactly what the first draft did, and the full suite failed here with
    `01-alpha.pdf was failed by its neighbour`, alpha and bravo both carrying the
    TimeoutError of a file they were merely standing behind. One deadlock would
    have failed the whole look-ahead window on a real corpus. Measured from the
    moment the loop begins waiting for each file, every neighbour gets a fresh
    60 fake seconds and none of them can expire. No sleep in this test races
    anything, so a loaded machine changes the timings and not the answer.
    """
    # `jumps=3`: the wait that expires, the retry's deadline, and the retry's
    # own wait. A file the ceiling kills is tried twice now, and this hang
    # never comes back, so both attempts have to reach the ceiling for the
    # row this test reads to exist at all.
    clock = _ScriptedClock(jump_after=1, jumps=3)
    pool = ProcessPool(workers=2, context_factory=_hanging_context,
                       lookahead_per_worker=2, floor=0,
                       seconds_per_extraction=_FAKE_CEILING_SECONDS, now=clock)
    try:
        handles = [pool.submit(_request(corpus, name)) for name in CORPUS]
        outcomes = {name: pool.result(handle)
                    for name, handle in zip(CORPUS, handles)}

        assert _failure_reason(outcomes[HANG]) is not None, "the hang was not stopped"
        for name in CORPUS:
            if name == HANG:
                continue
            assert _failure_reason(outcomes[name]) is None, (
                f"{name} was failed by its neighbour: {_failure_reason(outcomes[name])}")
    finally:
        pool.close()


def test_the_neighbours_are_read_normally(live_db, corpus, pool):
    """The same promise through a whole run, on the real clock, with real margins.

    One real-time test is kept because a driven clock cannot prove the pool works
    when nobody is driving it: the production ceiling is `time.monotonic` and a
    default that had drifted would pass every test above. What this asserts is only
    that a run over a corpus containing a hang finishes with its neighbours read --
    no timing relationship between the sleeps and the ceiling is claimed here, and
    that is deliberate. The relationship is the test above's, where it cannot be
    decided by CPU contention.
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
    # `jumps=3`: the wait that expires, the retry's deadline, and the retry's
    # own wait. A file the ceiling kills is tried twice now, and this hang
    # never comes back, so both attempts have to reach the ceiling for the
    # row this test reads to exist at all.
    clock = _ScriptedClock(jump_after=1, jumps=3)
    pool = ProcessPool(workers=2, context_factory=_hanging_context,
                       lookahead_per_worker=2, floor=0,
                       seconds_per_extraction=_FAKE_CEILING_SECONDS, now=clock)
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


def _completeness(outcome) -> list[str]:
    """What each run in the batch says about how much of the file it read."""
    assert outcome.kind == DISPATCHED, outcome
    return [result.run["completeness"] for result in outcome.dispatched.results]


def test_a_file_the_ceiling_killed_is_read_on_the_retry_in_the_same_run(
        tmp_path, corpus, monkeypatch):
    """R-112. The ceiling ends a wedge; it does not decide the file is unreadable.

    MEASURED, over eleven runs of the product on one pinned 263-file corpus. The
    same PNG -- content hash `782ff3d1...` -- was read completely in ten runs and
    wedged its worker in the eleventh, which cost that run 626.4 seconds against
    20 to 26 for every other. Sampled at the wedge, the worker's main thread was in
    `-[VNImageRequestHandler performRequests:]` -> `-[CIContext
    render:toCVPixelBuffer:]` -> `CI::ProgramNode::mainProgram` ->
    `__DISPATCH_WAIT_FOR_QUEUE__`, waiting on `CI::KernelCompileQueue`, which was
    itself blocked in `flock()` inside `MTLCompilerFSCache::openSync` -- the Metal
    shader compiler's on-disk cache lock, which is shared by every process on the
    machine. Six of the seven workers took that lock and released it in about three
    seconds; the seventh never came back.

    So the thing that wedged was NOT the file. It was the state of a machine-wide
    lock at the moment one worker made its first Vision call, and the very next run
    over the identical bytes read it in a second. The old ruling -- "a deadlock
    reached through the same bytes and the same framework will be reached again" --
    is what that measurement refutes, and this test is the refutation: the file the
    ceiling killed comes back READ, in the same run, without a person rerunning
    anything.
    """
    marker = tmp_path / "one-attempt-was-made"
    monkeypatch.setenv(_HANG_ONCE_MARKER, str(marker))
    # THE REAL CLOCK, and this is the one test in the file that needs it. A driven
    # clock's first wait expires with a timeout of zero, so the worker is killed
    # before it has entered the reader at all -- and a first attempt that never
    # reached the wedge cannot show that the SECOND one gets past it. Eight real
    # seconds against a mark written in the reader's first statement is not a race:
    # the mark is there long before the ceiling looks.
    pool = ProcessPool(workers=2, context_factory=_hanging_once_context,
                       lookahead_per_worker=2, floor=0,
                       seconds_per_extraction=_CEILING_SECONDS)
    try:
        handles = [pool.submit(_request(corpus, name)) for name in CORPUS]
        outcomes = {name: pool.result(handle)
                    for name, handle in zip(CORPUS, handles)}

        assert marker.exists(), (
            "the reader never wedged, so this proved nothing about the retry")
        assert _failure_reason(outcomes[HANG]) is None, (
            "the file the ceiling killed was written off instead of retried: "
            f"{_failure_reason(outcomes[HANG])}")
        assert _completeness(outcomes[HANG]) == ["complete"], (
            "the retry produced no reading of its own -- a file that came back "
            "without the content it was killed for is a silent loss: "
            f"{_completeness(outcomes[HANG])}")
        for name in CORPUS:
            assert _failure_reason(outcomes[name]) is None, (
                f"{name} was failed by the retry: {_failure_reason(outcomes[name])}")
    finally:
        pool.close()


def test_the_retry_is_one_and_a_file_that_wedges_twice_is_failed(
        tmp_path, corpus):
    """The bound. One retry, not a loop, and the second ceiling ends it.

    A retry with no bound would let one wedged file spend the whole run a ceiling at
    a time, which is `00`:257's rule broken by the recovery written to keep it. Two
    attempts is the same bound the death path already allows a file that segfaults,
    and it is reached here by a reader that never comes back at all.
    """
    clock = _ScriptedClock(jump_after=1, jumps=3)
    pool = ProcessPool(workers=2, context_factory=_hanging_context,
                       lookahead_per_worker=2, floor=0,
                       seconds_per_extraction=_FAKE_CEILING_SECONDS, now=clock)
    try:
        handles = [pool.submit(_request(corpus, name)) for name in CORPUS]
        outcomes = {name: pool.result(handle)
                    for name, handle in zip(CORPUS, handles)}

        reason = _failure_reason(outcomes[HANG])
        assert reason is not None, "a file that never comes back was never failed"
        assert "twice" in reason, (
            "the row does not say the file was tried more than once, so a person "
            f"reading it cannot tell what the run actually did: {reason}")
        assert str(_FAKE_CEILING_SECONDS) in reason, reason
        for name in CORPUS:
            if name == HANG:
                continue
            assert _failure_reason(outcomes[name]) is None, (
                f"{name} was failed by the retry of its neighbour: "
                f"{_failure_reason(outcomes[name])}")
    finally:
        pool.close()


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
