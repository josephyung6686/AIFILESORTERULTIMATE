# tests/integration/test_extraction_pool_lifecycle.py
"""`close()` returns and the worker processes are GONE, counted one operating-system
process at a time.

**What went wrong on a real folder.** A run over the owner's 215-file corpus stalled
twice at the byte-identical database size, the parent sitting at 0.0 % CPU with no
child at all -- blocked, not looping -- and forty-seven `multiprocessing.spawn`
workers were found re-parented to PID 1, left behind by earlier runs. A live specimen
was sampled while it sat there: it was blocked in `sem_wait` inside
`_multiprocessing_SemLock_acquire_impl`, which is `call_queue.get()` waiting for a
sentinel that was never sent, and its file descriptors 1 and 2 were PIPES WITH A PEER
STILL ATTACHED -- the `capture_output=True` pipes it inherited from
`tools/groundtruth/run.py`. That is the whole stall in one process listing: a worker
nobody told to stop holds the write end of the pipe its grandparent is reading, so
the grandparent's read never reaches end-of-file and waits for ever.

**Why no existing test saw it.** `ProcessPoolExecutor.shutdown(wait=False)` returns
before a single sentinel has been sent, and CPython then joins the manager thread from
`concurrent.futures.process._python_exit`, an interpreter-shutdown hook. So a test that
counts processes after `pytest` exits finds none: the leak is invisible from outside the
process, because the process cleaning up on its way out is exactly what hides it. Both
existing pool suites were measured that way and came back with a delta of zero while the
bug was live.

So these tests count from INSIDE, at the only instant that matters: the moment `close()`
returns. Everything after that instant is a bet that the run will be allowed to die
politely, and a run killed by a signal, by a second Ctrl-C during shutdown, or by the
crash the pool exists to survive is not. `close()` has to be finished when it returns,
not merely started.

**PIDs, and `os.kill(pid, 0)`.** Asking the pool whether it called `shutdown()` proves
nothing -- it did, with the argument that made it a no-op. These tests take the real
process identifiers while the pool is alive and then ask the kernel about each one.
They have to be taken WHILE it is alive because `shutdown` sets `_processes` to None
on its way through, and because `run_p1_p7` closes the pool inside its own `finally`
where no test can reach; hence `_RemembersItsWorkers`.

The second test is the one that matters. The happy path drains its look-ahead window
before closing, so nothing is running by then and almost any shutdown would look
clean. A `ContractViolation` leaves the window in flight and goes out through the
`finally` -- workers mid-read, the queue full of work nobody will collect -- and that
is the shape that was orphaning processes on the owner's machine.
"""
import os
import signal
import sqlite3
import subprocess
import sys
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
from extractors.failure import ContractViolation
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

#: The file whose reader raises the one exception `perform` does NOT turn into a
#: `failed` run. It comes back as a `CONTRACT` outcome, `_consume` re-raises it, and
#: `run_p1_p7` leaves through the `finally` that closes the pool -- which is the exit
#: this file is really about.
VIOLATOR = "00-contract.pdf"

#: FIRST, and its neighbours SLOW, for `test_extraction_pool_recovery.py`'s reason:
#: the interesting close is the one that happens while other files are still being
#: read. A violator at the end would find an empty pool and prove nothing.
CORPUS = ("01-alpha.pdf", "02-bravo.pdf", "03-charlie.pdf",
          "04-delta.pdf", "05-echo.pdf", "06-foxtrot.pdf")
VIOLATING_CORPUS = (VIOLATOR,) + CORPUS

#: Long enough that neighbours are certainly still in a worker when the violator's
#: outcome reaches the caller, short enough to keep the file cheap.
_READ_SECONDS = 0.5


def _read_pdf(path: Path) -> PdfDocument:
    if Path(path).name == VIOLATOR:
        raise ContractViolation(
            "the router named an extractor `current_versions()` has no entry for")
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


def _context() -> ExtractionContext:
    """What a worker builds for itself. Module level so `spawn` can name it."""
    return ExtractionContext(
        policy=SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False),
        readers=_readers(),
        transcription_authorized=lambda: False)


class _RemembersItsWorkers(ProcessPool):
    """A pool that writes down the operating-system processes it started.

    `close()` is both the thing under test and the thing that erases the evidence:
    `ProcessPoolExecutor.shutdown` sets `_processes` to None on its way through, and
    `run_p1_p7` calls `close()` inside a `finally` no test can reach into. So the
    identifiers are collected as the run goes, from `multiprocessing.active_children()`
    -- the public list of processes THIS process created -- and read back afterwards.

    It overrides nothing that decides anything. `submit` and `result` do their own
    work and then look around.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.worker_pids: set[int] = set()

    def submit(self, request):
        handle = super().submit(request)
        self._remember()
        return handle

    def result(self, handle):
        outcome = super().result(handle)
        self._remember()
        return outcome

    def _remember(self) -> None:
        import multiprocessing
        self.worker_pids.update(
            child.pid for child in multiprocessing.active_children()
            if child.pid is not None)


def _live_children() -> set[int]:
    """Every child this process already has, so the assertions can ignore them."""
    import multiprocessing
    return {child.pid for child in multiprocessing.active_children()
            if child.pid is not None}


def _still_alive(pids: set[int]) -> set[int]:
    """Which of these processes the kernel still knows about.

    Signal 0 is the standard existence probe: it delivers nothing and raises
    `ProcessLookupError` for a process that has been reaped. This is asked of the
    KERNEL rather than of the pool, because the pool's own opinion of its workers is
    what was wrong.
    """
    alive = set()
    for pid in pids:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            continue
        except PermissionError:                      # pragma: no cover -- not ours
            alive.add(pid)
        else:
            alive.add(pid)
    return alive


@pytest.fixture()
def live_db(tmp_path: Path):
    conn = open_database(tmp_path / "lifecycle.sqlite")
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_facts_schema(conn)
    create_privacy_schema(conn)
    create_eval_schema(conn)
    yield conn
    conn.close()


def _corpus(tmp_path: Path, name: str, files) -> Path:
    root = tmp_path / name
    root.mkdir()
    for index, filename in enumerate(files):
        (root / filename).write_bytes(b"%PDF-1.4 " + str(index).encode() * 8)
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


def _pool() -> _RemembersItsWorkers:
    #: `floor=0` so every request really crosses a process boundary -- with the
    #: shipped floor this corpus would stay on the calling thread and no worker would
    #: exist to leak. Two workers and a look-ahead of two, so the window is genuinely
    #: in flight when the violating run leaves through its `finally`.
    #: R-50's ceiling, required and with no default. Generous, because nothing in
    #: this file is about the ceiling: what it counts is operating-system processes
    #: after a run ends, and a ceiling that fired would be a different test.
    return _RemembersItsWorkers(workers=2, context_factory=_context,
                                lookahead_per_worker=2, floor=0,
                                seconds_per_extraction=300.0)


def test_a_finished_run_leaves_no_worker_process_alive(live_db, tmp_path):
    """The ordinary way out. Every file read, the window drained, `close()` called by
    `run_p1_p7` on its way out -- and when it returns there is nothing left running.

    This is the easy half and it is here for the negative it rules out: a fix that
    only drains when something went wrong would leave the ordinary run, which is
    every run the owner actually makes, orphaning workers on each pass.
    """
    pool = _pool()
    before = _live_children()
    root = _corpus(tmp_path, "clean", CORPUS)

    _run(live_db, root, pool)

    started = pool.worker_pids - before
    assert started, (
        "no worker process was ever started, so this test proves nothing about "
        "shutting one down")
    assert _still_alive(started) == set(), (
        f"{len(_still_alive(started))} of {len(started)} worker processes were still "
        "alive when the run returned. They hold this process's stdout and stderr "
        "pipes, so a parent reading that output waits for end-of-file for ever.")


def test_a_run_that_raises_partway_leaves_no_worker_process_alive(live_db, tmp_path):
    """THE case. A `ContractViolation` mid-window, workers still reading, out through
    the `finally`.

    `close()`'s docstring names this exit by name -- "INCLUDING the way out through a
    `ContractViolation`" -- and it was the exit that leaked, because cancelling the
    queued work says nothing about the processes waiting to be told to stop. The
    caller gets its exception promptly either way; the difference this asserts is
    whether it leaves two live interpreters behind while it does.
    """
    pool = _pool()
    before = _live_children()
    root = _corpus(tmp_path, "violating", VIOLATING_CORPUS)

    with pytest.raises(ContractViolation):
        _run(live_db, root, pool)

    started = pool.worker_pids - before
    assert started, (
        "no worker process was ever started, so this test proves nothing about "
        "shutting one down")
    assert _still_alive(started) == set(), (
        f"{len(_still_alive(started))} of {len(started)} worker processes survived a "
        "run that raised partway through. This is how the owner's machine came to "
        "hold forty-seven of them.")


# --------------------------------------------------------------------------
# The run that never reaches `close()` at all.
# --------------------------------------------------------------------------

#: How long to wait for a killed run's output to reach end-of-file. Generous: the
#: passing case takes about a second, and the failing case does not finish at all --
#: the real one was still waiting after forty minutes.
_EOF_SECONDS = 60.0

#: How often the child looks to see whether its workers exist yet. It is about to
#: kill itself and the interval only decides how soon.
_POLL_SECONDS = 0.05


def _child_that_is_killed_mid_run() -> None:
    """A real run, killed outright while its workers are reading.

    Not a simulation of the crash: `SIGKILL` cannot be caught, handled or deferred,
    so the interpreter stops between two instructions with `close()` unreached and
    every exit handler unrun -- which is what `pdfium` did to this product on the
    owner's corpus, and what a signal does to any run.

    It prints the worker identifiers BEFORE dying, because after dying it cannot, and
    those identifiers are the whole of what the test has to go on.
    """
    import tempfile
    import threading

    root = Path(tempfile.mkdtemp(prefix="pool-lifecycle-"))
    pool = _pool()

    def kill_once_the_workers_are_up() -> None:
        while not pool.worker_pids:
            time.sleep(_POLL_SECONDS)
        print(" ".join(str(pid) for pid in sorted(pool.worker_pids)), flush=True)
        os.kill(os.getpid(), signal.SIGKILL)

    threading.Thread(target=kill_once_the_workers_are_up, daemon=True).start()

    conn = open_database(root / "killed.sqlite")
    for create in (create_schema, create_scan_schema, create_evidence_schema,
                   create_extraction_schema, create_facts_schema,
                   create_privacy_schema, create_eval_schema):
        create(conn)
    _run(conn, _corpus(root, "corpus", CORPUS), pool)


def test_a_run_killed_outright_leaves_no_worker_process_alive():
    """The stall, in the suite.

    This is the one the product actually hit. `pdfium` segfaulted the run on a real
    199-file corpus and the workers already spawned had nobody left to stop them; they
    blocked in `sem_wait` for ever while still holding descriptors 1 and 2, which were
    this call's `stdout=PIPE` and `stderr=PIPE`. The reader then waited for an
    end-of-file that a dead run's surviving children were holding open: forty minutes
    on the owner's machine, released instantly when they were killed by hand.

    So the assertion is `communicate()` RETURNING. Nothing is mocked and no exit code
    is checked -- the child is killed and has none. What is being asked is only
    whether a run that dies without warning lets go of its own output, and a run whose
    children outlive it never does.
    """
    root = Path(__file__).resolve().parents[2]
    child = subprocess.Popen(
        [sys.executable, __file__], cwd=str(root),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        env={**os.environ, "PYTHONPATH": str(root / "src")})
    try:
        printed, _ = child.communicate(timeout=_EOF_SECONDS)
    except subprocess.TimeoutExpired as stalled:
        # The bug. Clean up after it, or the orphans stay on the machine and the
        # next reader of this pipe waits as long as this one did.
        survivors = _pids_in(stalled.output)
        for pid in survivors:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:               # pragma: no cover -- raced
                pass
        child.kill()
        pytest.fail(
            f"the killed run's output never reached end-of-file in {_EOF_SECONDS}s. "
            f"{len(survivors)} worker processes outlived it and are holding the pipe "
            "open; this is the stall, and it does not end on its own.")

    workers = _pids_in(printed)
    assert workers, (
        f"the child printed no worker identifiers, so it never got a pool up and "
        f"this test proves nothing. It said: {printed!r}")
    assert _still_alive(workers) == set(), (
        f"{len(_still_alive(workers))} of {len(workers)} workers are still alive "
        "after the run that started them was killed. They were reaped only because "
        "this test process is not reading their pipes; a caller that is would wait.")


def _pids_in(printed: str | None) -> set[int]:
    return {int(word) for word in (printed or "").split() if word.isdigit()}


if __name__ == "__main__":
    # Reached only by `test_a_run_killed_outright_leaves_no_worker_process_alive`,
    # which runs this file as a program. `spawn` re-imports it as `__mp_main__` and
    # therefore never comes through here.
    _child_that_is_killed_mid_run()
