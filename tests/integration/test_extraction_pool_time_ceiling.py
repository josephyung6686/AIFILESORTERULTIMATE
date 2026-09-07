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
from dataclasses import replace
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
from extractors.ocr import OcrOutput, OcrRegion
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
from review_run.progress import progress_lines
from review_surface.progress import progress_line
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

#: The ceiling for the ONE test that has to let the first attempt reach the reader.
#: Generous where `_CEILING_SECONDS` is tight, because the window it bounds contains a
#: worker spawn -- a fresh interpreter re-importing the composition root -- and this
#: file already records two tests failing at load 13 for exactly that reason. A run
#: that pays it is paying the ceiling itself: the wedged reader is killed the moment
#: it expires, so the number is the test's cost and not a sleep.
_REACHED_CEILING_SECONDS = 20.0

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


#: Where the readers below record that one attempt has already been made. A FILE and
#: not a variable, because the two attempts happen in two different processes: the
#: pool kills every worker before it retries, so nothing in the first worker's memory
#: survives to tell the second one anything. Three readers share it -- one that wedges
#: once, and R-120's two that end their attempts differently from each other.
_FIRST_ATTEMPT_MARKER = "GRAPH_AGENT_TEST_FIRST_ATTEMPT_MARKER"


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
    marker = Path(os.environ[_FIRST_ATTEMPT_MARKER])
    if Path(path).name == HANG and not marker.exists():
        # Written BEFORE the sleep, so the mark exists no matter when this worker is
        # killed. A worker killed with SIGKILL runs nothing on its way out.
        marker.write_text("one attempt has been made")
        time.sleep(_HANG_SECONDS)
    return _readable(path)


def _read_pdf_dying_then_hanging(path: Path) -> PdfDocument:
    """R-120. The first attempt dies; the second never answers.

    A file can end its two attempts in two different ways, because R-112 gave the
    ceiling path and the death path one shared counter. This reader is one of the
    two mixed orders, and it exists so the run row can be read for what it claims:
    a reason written by the path that arrived last calls this file "killed both
    times", which is a false sentence about the segfault that started it.

    `os._exit(1)` and not an exception, for the sibling recovery file's reason: an
    exception is a result the pool delivers, and what breaks a pool is a worker that
    stops existing mid-call.
    """
    marker = Path(os.environ[_FIRST_ATTEMPT_MARKER])
    if Path(path).name == HANG:
        if not marker.exists():
            # Written BEFORE the exit, so the mark survives a process that runs
            # nothing on its way out.
            marker.write_text("one attempt has been made")
            os._exit(1)
        time.sleep(_HANG_SECONDS)
    else:
        time.sleep(_READ_SECONDS)
    return _readable(path)


def _read_pdf_hanging_then_dying(path: Path) -> PdfDocument:
    """R-120, the other order. The first attempt wedges; the second dies.

    The mirror of the reader above, and it is kept separately rather than
    parameterised because the two orders reach the pool through different code and
    fail differently when the fix is wrong: this one is the order a reason written
    by the death path calls "died twice", which is false about the wedge.

    The first attempt never reaches `os._exit` -- the pool SIGKILLs it inside the
    sleep -- so the marker is what tells the second worker it is the second.
    """
    marker = Path(os.environ[_FIRST_ATTEMPT_MARKER])
    if Path(path).name == HANG:
        if not marker.exists():
            marker.write_text("one attempt has been made")
            time.sleep(_HANG_SECONDS)
        os._exit(1)
    else:
        time.sleep(_READ_SECONDS)
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


def _dying_then_hanging_context() -> ExtractionContext:
    """R-120's first mixed order. Module level, for `spawn`."""
    return ExtractionContext(
        policy=SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False),
        readers=_readers(_read_pdf_dying_then_hanging),
        transcription_authorized=lambda: False)


def _hanging_then_dying_context() -> ExtractionContext:
    """R-120's other mixed order. Module level, for `spawn`."""
    return ExtractionContext(
        policy=SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False),
        readers=_readers(_read_pdf_hanging_then_dying),
        transcription_authorized=lambda: False)


# --------------------------------------------------------------------------
# R-138: the corpus that is far too small for the pool the floor used to allow.
# --------------------------------------------------------------------------

#: The file whose reader never comes back, IN THE MIDDLE this time. `HANG` above is
#: first, because the tests it serves are about the window in flight BEHIND a wedge
#: and results are consumed in submission order. R-138 asks the other question --
#: does the run go on to the file AFTER the one it gave up on -- and a wedge at the
#: head cannot answer it, because there is nothing after it that was not already
#: submitted before it failed.
MIDDLE_HANG = "02-hang.pdf"

#: Three files and a fourth this deployment's policy will not open. Four is a
#: EIGHTH of the floor that used to keep a corpus this size on the calling thread,
#: which is the whole point: this is the size of folder R-138 was measured on.
VAULT = "04-vault.pdf"
MIDDLE_CORPUS = ("01-alpha.pdf", MIDDLE_HANG, "03-charlie.pdf")


def _read_pdf_hanging_in_the_middle(path: Path) -> PdfDocument:
    """Wedged for ever on the middle file of three. Module level, for `spawn`."""
    if Path(path).name == MIDDLE_HANG:
        # `_read_pdf`'s reason, unchanged: not an exception and not `os._exit`. The
        # worker stays alive, healthy and useless, which is what a dispatch deadlock
        # inside Vision looks like from Python.
        time.sleep(_HANG_SECONDS)
    else:
        time.sleep(_READ_SECONDS)
    return _readable(path)


def _vault_policy() -> SafetyPolicy:
    """This deployment's policy: `04-vault.pdf` is inside a protected container."""
    return SafetyPolicy(is_protected_container=lambda path: Path(path).name == VAULT,
                        is_dataless=lambda path: False)


def _middle_hang_context() -> ExtractionContext:
    """What a worker builds for itself. Module level, so `spawn` can import it.

    It carries the VAULT policy and not the open one, so the caller's half of the
    run and the worker's half are wired by one rule. Nothing here relies on the
    worker refusing the protected file -- the assertion below is that no request for
    it is ever made -- but a worker whose policy disagreed with its caller's would be
    a second answer to the standing rule living in a test fixture.
    """
    return ExtractionContext(
        policy=_vault_policy(), readers=_readers(_read_pdf_hanging_in_the_middle),
        transcription_authorized=lambda: False)


class _RecordsWhatItSubmitted(ProcessPool):
    """A real pool that also writes down every path it was handed.

    A REAL one, subclassed rather than replaced, because the property under test is
    about the pool the product actually builds: a double would prove the orchestrator
    calls `submit` in the right order and prove nothing about the ceiling, the kill
    or the rebuild that this file's other tests drive.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.submitted: list[str] = []

    def submit(self, request):
        self.submitted.append(str(request.path))
        return super().submit(request)


@pytest.fixture(scope="module")
def middle_hang_run(tmp_path_factory):
    """One run of the R-138 corpus, at ONE worker, kept for the questions below.

    Module-scoped, and the cost is the reason: the wedged file spends both of its
    attempts, so the run pays two ceilings and two worker spawns. Five tests ask
    different questions of the same run -- did it finish, was the third file read,
    is the order still the roster's, was the protected file submitted, does the
    report count the loss -- and running it five times would add two minutes to the
    suite to produce five identical databases.

    ONE WORKER, which is the count `cli.extraction_pool` used to answer with
    `InlinePool`: the same thread, no spawn, and therefore no ceiling, because a
    Python timeout does not interrupt a C dispatch wait on the thread that is doing
    the waiting. This fixture is that deployment, and every assertion below is what
    it could not have made.
    """
    root = tmp_path_factory.mktemp("r138") / "corpus"
    root.mkdir()
    for index, name in enumerate((*MIDDLE_CORPUS, VAULT)):
        (root / name).write_bytes(b"%PDF-1.4 " + str(index).encode() * 8)

    conn = open_database(tmp_path_factory.mktemp("r138db") / "middle.sqlite")
    for schema in (create_schema, create_scan_schema, create_evidence_schema,
                   create_extraction_schema, create_facts_schema,
                   create_privacy_schema, create_eval_schema):
        schema(conn)

    pool = _RecordsWhatItSubmitted(
        workers=1, context_factory=_middle_hang_context, lookahead_per_worker=2,
        seconds_per_extraction=_CEILING_SECONDS)
    started = time.monotonic()
    try:
        _run(conn, root, pool, policy=_vault_policy())
    finally:
        pool.close()
    yield conn, pool, time.monotonic() - started
    conn.close()


def test_the_run_finishes_at_one_worker_instead_of_waiting_for_the_reader(
        middle_hang_run):
    """R-138. The measured defect, at the worker count that had no answer for it.

    r6 of the owner's scoreboard hung one minute into the scan: both run processes
    at 0 % CPU for ten minutes, no socket open, no database write. Sampled, the
    thread was inside CoreImage's `CI::Context::recursive_render` waiting on a
    dispatch group -- Apple's image pipeline under the Vision OCR reader, deadlocked
    -- and nothing in the product could end that wait, because the file was being
    read on the calling thread. The person saw a run that never ended and no reason.

    `_HANG_SECONDS` is the reader that never comes back. A run that waits for it has
    the defect; a run that finishes in two ceilings does not.
    """
    _conn, _pool, elapsed = middle_hang_run

    assert elapsed < _HANG_SECONDS, (
        "the run waited for the wedged reader rather than for the ceiling, which "
        f"took {elapsed:.1f}s against a hang of {_HANG_SECONDS}s")


def test_the_middle_file_is_recorded_unread_and_the_row_says_why(middle_hang_run):
    """§2.4's rule, at the point R-138 makes it reachable: unexamined, never omitted.

    Coverage is sacred. A file the product could not read is marked and counted,
    and the vocabulary for it already exists -- P4's `failed` completeness, whose
    `failure_reason` carries the exception's type and message and nothing else. The
    reason has to name the CEILING and the READER, because a person reading a row
    that says only "this failed" has been told nothing they can act on, and an
    operator has nothing to tune.
    """
    conn, _pool, _elapsed = middle_hang_run
    rows = _runs(conn)

    assert MIDDLE_HANG in rows, "the wedged file got no run row at all"
    extractor, reason = rows[MIDDLE_HANG]
    assert reason is not None, f"the wedged file was recorded as a success: {rows}"
    assert str(_CEILING_SECONDS) in reason, reason
    assert extractor in reason, reason
    assert _both_ends(_ceiling_end(_CEILING_SECONDS),
                      _ceiling_end(_CEILING_SECONDS)) in reason, reason

    completeness = {row[0]: row[1] for row in conn.execute(
        "SELECT f.filename, r.completeness FROM extraction_runs r "
        "JOIN files f ON f.file_id = r.file_id "
        "WHERE r.extractor_name != 'filesystem.record'")}
    assert completeness[MIDDLE_HANG] == "failed", completeness


def test_the_file_after_the_wedged_one_is_still_read(middle_hang_run):
    """The half a wedge at the HEAD of a corpus cannot prove: the run goes ON.

    `00`:257 is that a single file may not consume the run. The two neighbours
    bracket the wedge -- one submitted before it, one after it was given up on --
    and both have to come back with a reading and no failure of their own. A
    recovery that failed the file behind the wedge would satisfy every assertion
    about the wedge itself and still lose a file for standing next to it.
    """
    conn, _pool, _elapsed = middle_hang_run
    rows = _runs(conn)

    for name in MIDDLE_CORPUS:
        if name == MIDDLE_HANG:
            continue
        assert name in rows, f"{name} was never read: {rows}"
        assert rows[name][1] is None, (
            f"{name} was failed by its neighbour's wedge: {rows[name][1]}")


def test_the_rows_are_still_in_submission_order_around_the_timed_out_file(
        middle_hang_run):
    """§3.4's caching and §8.5's replay both need a stable order, and a recovery is
    where it is most at risk.

    The wedged file is killed, its pool is rebuilt, and the window behind it is held
    back and resubmitted -- so its row is written LAST in real time and must still
    be written SECOND. `evidence_shape/store.py`'s `_ordered` exists because P4's
    `rowid` order is a property of the database and reverses when the same runs are
    written in the opposite sequence, so a recovery that appended by completion
    would change every cache key in the product.
    """
    conn, _pool, _elapsed = middle_hang_run

    written = [row[0] for row in conn.execute(
        "SELECT f.filename FROM extraction_runs r "
        "JOIN files f ON f.file_id = r.file_id "
        "WHERE r.extractor_name != 'filesystem.record' ORDER BY r.rowid")]
    assert written == list(MIDDLE_CORPUS), (
        f"the rows are in completion order rather than roster order: {written}")


def test_the_protected_path_is_still_never_submitted(middle_hang_run):
    """THE standing rule, re-asserted where R-138 could have broken it.

    Marked and counted, never opened. It is kept by the CALL ORDER and not by a
    check: `extract_filesystem`, whose first statement is `admit()`, runs on the
    calling thread, and a path that refuses there is never submitted to anything.
    R-138 moved every OTHER path off that thread, so this is the assertion that the
    gate is still upstream of the move rather than something a worker now performs.

    The list is the pool's own record of what it was handed, so this is a claim
    about a list and not a claim in a docstring.
    """
    conn, pool, _elapsed = middle_hang_run

    assert pool.submitted, "nothing was submitted at all; this proves nothing"
    assert not [path for path in pool.submitted if Path(path).name == VAULT], (
        f"a protected path was submitted to a worker: {pool.submitted}")
    assert sorted(Path(path).name for path in pool.submitted) == \
        sorted(MIDDLE_CORPUS), (
            f"the unprotected files were not all read: {pool.submitted}")

    names = {row[0] for row in conn.execute("SELECT filename FROM files")}
    assert VAULT in names, "the protected file was omitted from the corpus entirely"
    assert VAULT not in _runs(conn), "a protected file was extracted"


def test_the_report_line_counts_the_file_that_timed_out(middle_hang_run):
    """§8.6's line, which is where the person actually meets the loss.

    A run row nobody prints is a row nobody reads. §8.6 requires the difference
    between completed work and deferred work on screen so that an unprocessed file
    is not taken for one that was understood and found unimportant, and P13 refuses
    to render a line that leaves an indexed file out of every entry.

    IT PRINTS AS `unreadable` AND NOT AS `failed`, and that is P5's published
    mapping rather than a loss of detail: `review_surface.progress.UNREADABLE_STATES`
    folds `unreadable` and `failed` into one entry because both mean the product
    could not obtain usable content, and the PAIR is taken rather than `unreadable`
    alone precisely so that a `failed` run appears in no entry at all. So the count
    is asserted alongside the FILE BEHIND IT: a line saying "1 unreadable" is worth
    nothing here if the one it counts is a neighbour.

    `WORST_FIRST` is imported from `cli` rather than respelled, because the
    arbitration is the composition root's stated choice under P13's Open question 4
    and a copy here could agree with a broken one. It is imported INSIDE the test:
    a spawned worker imports this module to reach `_middle_hang_context`, and a
    module-level `import cli` would make every worker pay for the composition root
    and Apple's Vision framework.
    """
    from cli import WORST_FIRST

    conn, _pool, _elapsed = middle_hang_run
    indexed = {row[0]: row[1] for row in conn.execute(
        "SELECT file_id, content_hash FROM files")}
    wedged = conn.execute("SELECT file_id FROM files WHERE filename = ?",
                          (MIDDLE_HANG,)).fetchone()[0]

    asked = dict(scan_ref="scan-1", plan_version="plan_0", rendered_at=CLOCK,
                 indexed_files=indexed, precedence=WORST_FIRST,
                 awaiting_model_review=tuple, flagged_by_model_review=tuple,
                 cause_for=lambda label: None)
    lines = progress_lines(conn, **asked)
    entries = {entry.label: entry for entry in progress_line(conn, **asked).entries}

    assert any(line.startswith("  1 unreadable  (blocked)") for line in lines), (
        f"the file the ceiling stopped is in no line of the report: {lines}")
    assert entries["unreadable"].file_ids == (wedged,), (
        "the report's blocked count is not the file the ceiling stopped: "
        f"{entries['unreadable'].file_ids} against {wedged}")
    assert any("2 fully extracted" in line for line in lines), (
        f"the two files that were read are not counted as read: {lines}")


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
                        lookahead_per_worker=2,
                        seconds_per_extraction=_CEILING_SECONDS)
    yield built
    built.close()


def _open_policy() -> SafetyPolicy:
    """Nothing on this corpus is protected. What every test here used implicitly."""
    return SafetyPolicy(is_protected_container=lambda path: False,
                        is_dataless=lambda path: False)


def _run(conn: sqlite3.Connection, root: Path, pool, *, policy=None,
         readers=None, targeted_ocr_needed=lambda file_id, content_hash: False):
    selection = record_selection(conn, sources=[root], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return run_p1_p7(
        conn, selection, source=FilesystemCorpusSource(),
        mime_type_for=lambda path: "application/pdf", scan_state="scanned",
        budget_exhausted=lambda: False, detect_format=lambda path: "pdf",
        policy=policy if policy is not None else _open_policy(),
        readers=readers if readers is not None else _readers(),
        sink=RunWriter(conn, author="P5"),
        now=lambda: CLOCK, context_window=40,
        transcription_authorized=lambda: False, corpus_form="snapshot",
        policy_settings={}, file_entry_body=lambda row: {"payload_ref": "blob"},
        resolve_native=lambda db, file_id, content_hash: None,
        targeted_ocr_needed=targeted_ocr_needed,
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
    # R-112/R-120. The row has to say the run tried again, because it did -- and it
    # has to say so by naming HOW EACH ATTEMPT ENDED rather than by asserting one
    # mode happened twice. This reader wedges both times, so both halves read the
    # same; the two mixed orders below are where that stops being free.
    assert _both_ends(_ceiling_end(_CEILING_SECONDS),
                      _ceiling_end(_CEILING_SECONDS)) in reason, reason


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
                       lookahead_per_worker=2,
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
                       lookahead_per_worker=2,
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


#: How the pool names an attempt a dead worker ended. Written out here rather than
#: imported, so the test pins the sentence a PERSON reads and cannot pass by sharing
#: a formatting mistake with the code that produces it.
_DEATH_END = "the worker process died (BrokenProcessPool)"


def _ceiling_end(ceiling: float) -> str:
    """How the pool names an attempt the ceiling ended."""
    return f"no result within the {ceiling}s ceiling"


def _both_ends(first: str, second: str) -> str:
    """R-120. Each attempt named by its own end, in the order they happened.

    THE ORDER IS THE ASSERTION. Checking only that both phrases appear would pass on
    a reason that listed them backwards, which is a different false sentence about
    the same run -- and it would pass on the old code for the two same-mode orders,
    where the two halves are identical anyway.
    """
    return f"attempt 1: {first}; attempt 2: {second}"


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
    monkeypatch.setenv(_FIRST_ATTEMPT_MARKER, str(marker))
    # THE REAL CLOCK, and this is the one test in the file that needs it. A driven
    # clock's first wait expires with a timeout of zero, so the worker is killed
    # before it has entered the reader at all -- and a first attempt that never
    # reached the wedge cannot show that the SECOND one gets past it. What has to
    # fit inside the ceiling is a worker spawn and the reader's first statement, so
    # the number is `_REACHED_CEILING_SECONDS` and not the tight one: a machine slow
    # enough to miss it would fail this test for a true sentence about the load and
    # a false one about the code.
    pool = ProcessPool(workers=2, context_factory=_hanging_once_context,
                       lookahead_per_worker=2,
                       seconds_per_extraction=_REACHED_CEILING_SECONDS)
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
                       lookahead_per_worker=2,
                       seconds_per_extraction=_FAKE_CEILING_SECONDS, now=clock)
    try:
        handles = [pool.submit(_request(corpus, name)) for name in CORPUS]
        outcomes = {name: pool.result(handle)
                    for name, handle in zip(CORPUS, handles)}

        reason = _failure_reason(outcomes[HANG])
        assert reason is not None, "a file that never comes back was never failed"
        assert _both_ends(_ceiling_end(_FAKE_CEILING_SECONDS),
                          _ceiling_end(_FAKE_CEILING_SECONDS)) in reason, (
            "the row does not name both attempts and how each of them ended, so a "
            f"person reading it cannot tell what the run actually did: {reason}")
        assert str(_FAKE_CEILING_SECONDS) in reason, reason
        for name in CORPUS:
            if name == HANG:
                continue
            assert _failure_reason(outcomes[name]) is None, (
                f"{name} was failed by the retry of its neighbour: "
                f"{_failure_reason(outcomes[name])}")
    finally:
        pool.close()


def test_a_file_that_dies_and_then_wedges_names_both_ends_in_order(
        tmp_path, corpus, monkeypatch):
    """R-120. One counter, two ways to spend it, and the row must say which was which.

    R-112 made the ceiling path and the death path share `attempts`, which is what
    bounds a file at two tries however they end. What it did not do is make the
    REASON share: whichever path arrived second wrote the sentence, so a file that
    segfaulted and then wedged was recorded as "killed both times" -- the ceiling's
    words applied to a segfault nobody was told about. A person reading that row goes
    looking for a timeout that happens twice, when what actually started it was a
    worker that stopped existing, and those two have nothing in common to fix.

    THE CLOCK IS DRIVEN AND THE COUNT IS THE WHOLE OF IT. `result` reads it once for
    the head's deadline, once for the wait the death ends, and once for the retry's
    fresh deadline -- calls 1, 2 and 3 -- so `jump_after=3` puts the leap on call 4,
    the retry's own wait, which then finds a ceiling 10,000 fake seconds behind it.
    `jumps=1`, so fake time stands still afterwards and no neighbour's own ceiling
    can be crossed. The second attempt cannot end any other way: the reader has
    already died once, so on the retry it sleeps, and a sleeping worker cannot break
    a pool.
    """
    marker = tmp_path / "one-attempt-was-made"
    monkeypatch.setenv(_FIRST_ATTEMPT_MARKER, str(marker))
    clock = _ScriptedClock(jump_after=3, jumps=1)
    pool = ProcessPool(workers=2, context_factory=_dying_then_hanging_context,
                       lookahead_per_worker=2,
                       seconds_per_extraction=_FAKE_CEILING_SECONDS, now=clock)
    try:
        handles = [pool.submit(_request(corpus, name)) for name in CORPUS]
        outcomes = {name: pool.result(handle)
                    for name, handle in zip(CORPUS, handles)}

        assert marker.exists(), (
            "the reader never died, so this proved nothing about the order")
        reason = _failure_reason(outcomes[HANG])
        assert reason is not None, "a file that died and then wedged was not failed"
        assert _both_ends(_DEATH_END,
                          _ceiling_end(_FAKE_CEILING_SECONDS)) in reason, (
            "the row names one mode for two attempts that ended differently, so it "
            f"reports a failure this run never had: {reason}")
        for name in CORPUS:
            if name == HANG:
                continue
            assert _failure_reason(outcomes[name]) is None, (
                f"{name} was failed by its neighbour: {_failure_reason(outcomes[name])}")
    finally:
        pool.close()


def test_a_file_that_wedges_and_then_dies_names_both_ends_in_order(
        tmp_path, corpus, monkeypatch):
    """R-120, the other order, where the false sentence was "died twice".

    Kept as a second test rather than a parameter of the one above, because the two
    orders are not each other's mirror in the code: this one leaves the ceiling
    branch and enters the death branch, and a fix that carried the end forward in
    only one direction passes the other test and fails here.

    THE REAL CLOCK, and this is the second test in the file that needs it, for the
    retry test's reason one step further on. A driven clock's first wait expires with
    a timeout of zero, so the first worker is killed before it has entered the reader
    at all -- and a first attempt that never ran writes no marker, so the SECOND
    attempt would be the one that wedges and the order this test is named for would
    never happen. What has to fit inside the ceiling is a worker spawn and the
    reader's first statement, so the number is `_REACHED_CEILING_SECONDS`.
    """
    marker = tmp_path / "one-attempt-was-made"
    monkeypatch.setenv(_FIRST_ATTEMPT_MARKER, str(marker))
    pool = ProcessPool(workers=2, context_factory=_hanging_then_dying_context,
                       lookahead_per_worker=2,
                       seconds_per_extraction=_REACHED_CEILING_SECONDS)
    try:
        handles = [pool.submit(_request(corpus, name)) for name in CORPUS]
        outcomes = {name: pool.result(handle)
                    for name, handle in zip(CORPUS, handles)}

        assert marker.exists(), (
            "the reader never wedged, so this proved nothing about the order")
        reason = _failure_reason(outcomes[HANG])
        assert reason is not None, "a file that wedged and then died was not failed"
        assert _both_ends(_ceiling_end(_REACHED_CEILING_SECONDS),
                          _DEATH_END) in reason, (
            "the row names one mode for two attempts that ended differently, so it "
            f"reports a failure this run never had: {reason}")
        for name in CORPUS:
            if name == HANG:
                continue
            assert _failure_reason(outcomes[name]) is None, (
                f"{name} was failed by its neighbour: {_failure_reason(outcomes[name])}")
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

    `workers` and `lookahead_per_worker` both have no default and the
    reason is written beside each: a part that defaults its own policy is a part
    choosing one, and a number nobody reviewed is a number nobody owns. A ceiling
    that kills a worker is the last number that should acquire a quiet default.
    """
    with pytest.raises(TypeError):
        ProcessPool(workers=2, context_factory=_hanging_context,
                    lookahead_per_worker=2)


def test_a_ceiling_that_could_not_stop_anything_is_refused():
    """Zero or less is not a ceiling, it is an instruction to fail every file."""
    for refused in (0, -1.0):
        with pytest.raises(ValueError):
            ProcessPool(workers=2, context_factory=_hanging_context,
                        lookahead_per_worker=2,
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


# --------------------------------------------------------------------------
# R-138: §2.7's post-P6 pass, which is where r6 actually hung.
# --------------------------------------------------------------------------

#: The file whose OCR ENGINE never comes back, in the middle of three. Its PDF text
#: layer reads normally: what wedges is the second, optional pass over the same file,
#: which is the pass `extract_targeted_ocr` performs and which ran on the calling
#: thread until R-138.
OCR_HANG = "02-ocr.pdf"
OCR_CORPUS = ("01-alpha.pdf", OCR_HANG, "03-charlie.pdf")


def _read_pdf_quickly(path: Path) -> PdfDocument:
    """A text layer, immediately. Nothing in this section is about the native read."""
    return _readable(path)


def _hanging_ocr_engine(path, config=None):
    """Apple Vision, as r6 met it. Module level, for `spawn`.

    The sample is the specification for this function: the run process's main thread
    inside `-[VNImageRequestHandler performRequests:gatheredForensics:error:]` ->
    `VNRecognizeTextRequest` -> `VNDetector`, 726 samples of 770, at 0 % CPU. No
    exception, no exit, no progress -- so this sleeps rather than raising, exactly as
    `_read_pdf` does one section above and for the same reason.
    """
    if Path(path).name == OCR_HANG:
        time.sleep(_HANG_SECONDS)
    text = f"{Path(path).stem} was recognised"
    # `region=1` and not 0: P4 D3 makes container-path indices 1-based and refuses
    # a zero, which is a `failed` OCR run for a page that was recognised perfectly.
    return OcrOutput(provider="Test Vision", provider_version="1",
                     regions=(OcrRegion(page=1, region=1, text=text),),
                     pages_processed=1, pages_total=1)


def _readers_whose_ocr_hangs() -> Readers:
    """The wiring above, with an OCR engine. `ocr_engine=None` everywhere else in
    this file is what keeps its other runs off §2.7 entirely."""
    return replace(_readers(_read_pdf_quickly),
                   ocr_engine=_hanging_ocr_engine, ocr_config={})


def _hanging_ocr_context() -> ExtractionContext:
    """What a worker builds for itself. Module level, so `spawn` can import it."""
    return ExtractionContext(
        policy=_open_policy(), readers=_readers_whose_ocr_hangs(),
        transcription_authorized=lambda: False)


#: P6's verdict, forced. `document_ocr_decision` calls a text layer BROKEN -- and
#: therefore eligible for the targeted pass -- when the native run produced text and
#: P6 reports no usable facts from it. Every file here has text, so this one answer
#: puts all three on §2.2's targeted route.
def _no_usable_facts(file_id: str, content_hash: str) -> bool:
    return True


@pytest.fixture(scope="module")
def targeted_ocr_run(tmp_path_factory):
    """One run whose MIDDLE file's OCR engine never returns, at ONE worker.

    Module-scoped for the reason the sibling fixture gives: the wedged pass spends
    both of its attempts, so the run pays two ceilings and two spawns, and five
    tests ask different questions of one database.
    """
    root = tmp_path_factory.mktemp("r138-ocr") / "corpus"
    root.mkdir()
    for index, name in enumerate(OCR_CORPUS):
        (root / name).write_bytes(b"%PDF-1.4 " + str(index).encode() * 8)

    conn = open_database(tmp_path_factory.mktemp("r138-ocr-db") / "ocr.sqlite")
    for schema in (create_schema, create_scan_schema, create_evidence_schema,
                   create_extraction_schema, create_facts_schema,
                   create_privacy_schema, create_eval_schema):
        schema(conn)

    pool = ProcessPool(workers=1, context_factory=_hanging_ocr_context,
                       lookahead_per_worker=2,
                       seconds_per_extraction=_CEILING_SECONDS)
    started = time.monotonic()
    try:
        _run(conn, root, pool, readers=_readers_whose_ocr_hangs(),
             targeted_ocr_needed=_no_usable_facts)
    finally:
        pool.close()
    yield conn, time.monotonic() - started
    conn.close()


def _tiered(conn):
    """Every run, keyed by file and analysis tier."""
    return {(row[0], row[1]): (row[2], row[3]) for row in conn.execute(
        "SELECT f.filename, r.analysis_tier, r.completeness, r.failure_reason "
        "FROM extraction_runs r JOIN files f ON f.file_id = r.file_id "
        "WHERE r.extractor_name != 'filesystem.record'")}


def test_a_targeted_ocr_pass_that_never_returns_does_not_hang_the_run(
        targeted_ocr_run):
    """R-138's measured defect, at the call the samples actually caught.

    `extract_targeted_ocr` ran on the calling thread after `pool.close()`, so no
    ceiling could reach it. Sampled at the hang, the run process held NO
    Python-created thread -- no executor manager, no queue feeder -- while its main
    thread sat inside Vision through PyObjC: the pool had been built and closed, and
    this was the only framework call left here. A run that waits for the engine has
    the defect; a run that finishes in two ceilings does not.
    """
    _conn, elapsed = targeted_ocr_run

    assert elapsed < _HANG_SECONDS, (
        "the run waited for the wedged OCR engine rather than for the ceiling, "
        f"which took {elapsed:.1f}s against a hang of {_HANG_SECONDS}s")


def test_the_lost_pass_is_recorded_on_the_ocr_tier_and_not_the_native_one(
        targeted_ocr_run):
    """The row this file gets, and the three things a native row would break.

    The native pass SUCCEEDED -- the text layer was read -- and it is the optional
    second pass that was lost, so the `failed` run belongs to the OCR tier. Written
    natively instead it would be a second `pdf.text` run beside a complete one, and
    then `WORST_FIRST` reports a file as failed whose text was recovered,
    `set_extraction_status` marks a tier failed that finished, and
    `authoritative_result` meets two native runs for one content hash and raises
    `AmbiguousAuthoritativeRun` on the NEXT run over the same corpus.
    """
    conn, _elapsed = targeted_ocr_run
    runs = _tiered(conn)

    completeness, reason = runs[(OCR_HANG, "ocr")]
    assert completeness == "failed", runs
    assert reason is not None, f"the wedged pass was recorded as a success: {runs}"
    assert str(_CEILING_SECONDS) in reason, reason
    assert _both_ends(_ceiling_end(_CEILING_SECONDS),
                      _ceiling_end(_CEILING_SECONDS)) in reason, reason

    native_completeness, native_reason = runs[(OCR_HANG, "native")]
    assert native_completeness == "complete", (
        f"the native read was marked by its OCR pass's failure: {runs}")
    assert native_reason is None, native_reason


def test_the_file_keeps_exactly_one_native_run(targeted_ocr_run):
    """The half the assertion above cannot make from a dictionary.

    `_tiered` keys on file and tier, so a SECOND native row for the same file would
    overwrite the first and the test above would still pass. This counts them, which
    is what `authoritative_result` does before it raises.
    """
    conn, _elapsed = targeted_ocr_run

    natives = conn.execute(
        "SELECT COUNT(*) FROM extraction_runs r JOIN files f "
        "ON f.file_id = r.file_id "
        "WHERE f.filename = ? AND r.analysis_tier = 'native'", (OCR_HANG,)
    ).fetchone()[0]
    assert natives == 1, (
        f"{natives} native runs for one file version; the ceiling wrote its failure "
        "on the native tier and the next run over this corpus will not be able to "
        "choose an authoritative one")


def test_the_files_either_side_are_still_recognised(targeted_ocr_run):
    """The run goes ON, through the pass that wedged and out the other side.

    One neighbour was submitted before the wedge and one after it was given up on.
    Both have to come back with a reading of their own, on both tiers.
    """
    conn, _elapsed = targeted_ocr_run
    runs = _tiered(conn)

    for name in OCR_CORPUS:
        if name == OCR_HANG:
            continue
        assert runs[(name, "native")][1] is None, runs[(name, "native")]
        assert runs[(name, "ocr")] == ("complete", None), (
            f"{name} lost its OCR pass to its neighbour's wedge: {runs}")


def test_no_worker_outlives_the_run(targeted_ocr_run):
    """The pool now spans the fact loop, so it is closed later -- but still closed.

    `pool.close()` moved below the fact loop so the targeted pass has something to
    run in. A close that moved and stopped working would leave workers in `sem_wait`
    holding this process's descriptors, which is the forty-minute hang
    `_watch_the_parent` records. Counted in operating-system processes, not in
    method calls.
    """
    targeted_ocr_run  # the run has finished by the time this fixture yields

    assert multiprocessing.active_children() == [], (
        "a worker process outlived the run: "
        f"{[(child.name, child.pid) for child in multiprocessing.active_children()]}")


# --------------------------------------------------------------------------
# R-138: the same pass, when its worker DIES rather than wedges.
# --------------------------------------------------------------------------

#: The file whose OCR engine kills its worker outright. A different file from
#: `OCR_HANG` and a different module-level engine, because the two paths reach
#: `_failure_outcome` through different branches of `result()` -- a ceiling and a
#: `BrokenProcessPool` -- and a fix that attributed one correctly could still get
#: the other wrong.
OCR_CRASH = "02-crash.pdf"
CRASH_CORPUS = ("01-alpha.pdf", OCR_CRASH, "03-charlie.pdf")


def _crashing_ocr_engine(path, config=None):
    """`os._exit(1)` inside the OCR pass, in a spawned worker, every time.

    The recovery suite's reader, pointed at the engine instead of the PDF reader.
    NOT an exception: `os._exit` skips every handler, flushes nothing and leaves the
    executor with a worker that never answers, which is what a segfault inside
    Apple's Vision framework looks like from Python. `_ocr` catches exceptions and
    turns them into a `failed` OCR run all by itself, so an exception here would
    never reach the pool at all and would prove nothing about the death path.

    It crashes on BOTH attempts, with no marker, because a file is written off only
    after two. One attempt would be retried and read.
    """
    if Path(path).name == OCR_CRASH:
        os._exit(1)
    text = f"{Path(path).stem} was recognised"
    return OcrOutput(provider="Test Vision", provider_version="1",
                     regions=(OcrRegion(page=1, region=1, text=text),),
                     pages_processed=1, pages_total=1)


def _readers_whose_ocr_crashes() -> Readers:
    return replace(_readers(_read_pdf_quickly),
                   ocr_engine=_crashing_ocr_engine, ocr_config={})


def _crashing_ocr_context() -> ExtractionContext:
    """What a worker builds for itself. Module level, so `spawn` can import it."""
    return ExtractionContext(
        policy=_open_policy(), readers=_readers_whose_ocr_crashes(),
        transcription_authorized=lambda: False)


@pytest.fixture(scope="module")
def crashed_ocr_run(tmp_path_factory):
    """One run whose middle file's OCR pass kills its worker twice, at ONE worker."""
    root = tmp_path_factory.mktemp("r138-crash") / "corpus"
    root.mkdir()
    for index, name in enumerate(CRASH_CORPUS):
        (root / name).write_bytes(b"%PDF-1.4 " + str(index).encode() * 8)

    conn = open_database(tmp_path_factory.mktemp("r138-crash-db") / "crash.sqlite")
    for schema in (create_schema, create_scan_schema, create_evidence_schema,
                   create_extraction_schema, create_facts_schema,
                   create_privacy_schema, create_eval_schema):
        schema(conn)

    pool = ProcessPool(workers=1, context_factory=_crashing_ocr_context,
                       lookahead_per_worker=2,
                       seconds_per_extraction=_CEILING_SECONDS)
    try:
        _run(conn, root, pool, readers=_readers_whose_ocr_crashes(),
             targeted_ocr_needed=_no_usable_facts)
    finally:
        pool.close()
    yield conn
    conn.close()


def test_a_targeted_pass_whose_worker_dies_is_recorded_on_the_ocr_tier(
        crashed_ocr_run):
    """The death path's half of R-138's attribution, which no test drove.

    A wedged targeted pass and a crashed one reach `_failure_outcome` through
    different branches of `result()` -- one from `FuturesTimeout`, one from
    `BrokenProcessPool` -- and share only the function that writes the row. The
    ceiling's half is asserted above; this is the other, and it is here because
    "correct by construction" is a claim about today's branches.

    The row must name the DEATH and not a ceiling, because the two are different
    facts about the machine and R-120 is the whole argument for keeping them apart:
    a person told a run met a repeat of a failure it never met is sent to look for
    a defect in the file rather than for the state that produced it.
    """
    runs = _tiered(crashed_ocr_run)

    completeness, reason = runs[(OCR_CRASH, "ocr")]
    assert completeness == "failed", runs
    assert reason is not None, f"the crashed pass was recorded as a success: {runs}"
    assert _both_ends(_DEATH_END, _DEATH_END) in reason, reason
    assert str(_CEILING_SECONDS) not in reason, (
        "the row blames a ceiling for a worker that died: " + reason)


def test_the_crashed_pass_leaves_the_native_reading_alone(crashed_ocr_run):
    """The same guard the ceiling half makes, against the other branch.

    `_failure_outcome` names `request.decision.extractor_name` for an extraction
    request, and a `TargetedOcrRequest` carries no decision at all -- reading one
    would be an `AttributeError` inside the recovery path, which is the one place
    in the pool that must not raise. So this asserts both that the native run
    survived and that there is exactly ONE of it, which is what
    `authoritative_result` counts before it refuses to choose.
    """
    conn = crashed_ocr_run
    runs = _tiered(conn)

    assert runs[(OCR_CRASH, "native")] == ("complete", None), (
        f"the native read was marked by its OCR pass's crash: {runs}")

    natives = conn.execute(
        "SELECT COUNT(*) FROM extraction_runs r JOIN files f "
        "ON f.file_id = r.file_id "
        "WHERE f.filename = ? AND r.analysis_tier = 'native'", (OCR_CRASH,)
    ).fetchone()[0]
    assert natives == 1, (
        f"{natives} native runs for one file version after an OCR worker died")


def test_the_neighbours_of_a_crashed_pass_are_read_and_recognised(crashed_ocr_run):
    """A pool death fails EVERY future in flight, not only the guilty one.

    That is the shape `_rebuild` exists for, one level up from where the recovery
    suite proves it: the window is held back and resubmitted rather than failed, so
    surviving somebody else's crash costs a file nothing. Both neighbours have to
    come back whole on both tiers.
    """
    runs = _tiered(crashed_ocr_run)

    for name in CRASH_CORPUS:
        if name == OCR_CRASH:
            continue
        assert runs[(name, "native")] == ("complete", None), runs[(name, "native")]
        assert runs[(name, "ocr")] == ("complete", None), (
            f"{name} lost its OCR pass to its neighbour's crash: {runs}")
