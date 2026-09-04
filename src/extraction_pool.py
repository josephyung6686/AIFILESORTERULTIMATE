# src/extraction_pool.py
"""Where `extract_initial` may run somewhere other than the calling thread.

**The whole product had no concurrency.** `grep -rn "multiprocessing\\|concurrent"
src/` returned nothing, on a machine with eight cores. A whole-run profile of a real
413-file folder attributes 476.6 of 636.6 profiled seconds -- 75 % -- to
`extract_initial`, and 405.2 of those to `extract_pdf` alone over 40 PDFs. The rest
of the pipeline is sqlite, and sqlite is a serial writer. So there is exactly one
place worth widening, and this module is the seam that widens it.

**It moves one call and nothing else.** `extract_initial` takes `file_row`,
`decision`, `path`, `policy`, `readers`, `now` and `context_window` and returns
results; it opens no connection and writes no row. Every database write stays in
`orchestrator.run_p1_p7`, on its own thread, in roster order. A pool changes WHERE
the reading happens and never WHEN the writing happens.

**Order is a property of the corpus, not of the run.** §3.4's caching and §8.5's
replay both need a stable order, and `evidence_shape/store.py`'s `_ordered` exists
because "P4's `rowid` order is a property of the database and reverses when the same
three runs are written in the opposite sequence (verified by execution)". So the
consumption loop takes results back in the order it submitted them, whatever order
they finish in -- `tests/integration/test_p1_p7_parallel.py` drives it with a pool
that deliberately finishes every batch backwards, and the two databases still match
row for row.

**The protected-container rule is enforced before a request exists.** The caller
runs `extract_filesystem` -- whose first statement is `admit()` -- on its own thread,
and a path that refuses there is never submitted. No worker is ever handed a path
inside a protected container. That is structural, not a check some worker performs.

**Exceptions keep their meaning across the boundary.** A worker cannot raise into the
caller, so `perform()` names the outcome instead: the two §4b/§5 refusals and
`ContractViolation` come back as `ExtractionOutcome` kinds the caller re-raises, and
the ordinary reader crash that §2.4 turns into one `failed` run is turned into that
run INSIDE the worker. That last one is not a shortcut, it is the fix for a real
hazard: `failed_result` records `f"{type(error).__name__}: {error}"` and nothing
else, so the string is identical either side -- while shipping the live exception
object across a process boundary would ask `pickle` to reconstruct whatever a
truncated PDF made pdfminer raise, and a pickling failure there loses the run for a
file whose only crime was being corrupt.

**A worker that dies must not take the run with it.** Commit 446d7f3 fixed exactly
this shape at file level -- one zip with duplicate member names unwound a 5,760-file
run -- and a process pool reintroduces it one level up: a segfault inside Apple's
Vision framework breaks the pool and fails every request in flight. `ProcessPool`
rebuilds the pool and retries the suspect ALONE, holding the rest of the window back
until it answers; a file that kills a pool it is alone in becomes a `failed` run and
the run continues. `tests/integration/test_extraction_pool_recovery.py` calls
`os._exit(1)` inside a real worker to prove it.

The first draft of that recovery resubmitted the whole window together with every
request's retry count bumped, and it was wrong in the direction that matters: the
next death landed on whichever request the caller happened to be waiting on, so a
crash at position fifty would have recorded `failed` runs for the innocent files
ahead of it. `_rebuild` says why culpability has to be established rather than
inferred from position, and the sabotage that restores the old shape fails with
"01-alpha.pdf was failed by its neighbour's crash".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors.dispatch import Dispatched, extract_initial
from extractors.failure import ContractViolation, failed_result
from extractors.safety import DatalessRefused, ProtectedContainerRefused
from extractors.sink import ExtractionResult

#: The four things a request can come back as. `DISPATCHED` carries results; the other
#: three carry a message and are re-raised by the caller as the exception they name.
DISPATCHED = "dispatched"
PROTECTED = "protected"
DATALESS = "dataless"
CONTRACT = "contract"


@dataclass(frozen=True)
class ExtractionContext:
    """Everything `extract_initial` needs that cannot cross a process boundary.

    `policy` holds predicates, `readers` is a dataclass of closures and
    `transcription_authorized` is a nullary callable -- `pdfminer_reader()` RETURNS
    the function it wires, so there is no name for `pickle` to write down. They are
    therefore never sent: a worker builds its own from a factory the composition root
    names, and the caller builds one from the same factory, so both halves of a run
    are wired by one function rather than by two that agree today.
    """
    policy: Any
    readers: Any
    transcription_authorized: Callable[[], bool]


@dataclass(frozen=True)
class ExtractionRequest:
    """One file's extraction, as data.

    `file_row` is a plain mapping and not P1's `sqlite3.Row`: a Row is a cursor's
    view and does not pickle. `versions` rides along rather than being recomputed in
    the worker because `_failed_version` reads it, and a version table that differed
    between caller and worker would stamp a `failed` run with a number the caller
    never held -- which lands in §3.4's cache key and rule 8's replay key.
    """
    file_id: str
    file_row: Mapping[str, Any]
    decision: Any
    path: Path
    now: str
    context_window: int
    versions: Mapping[str, str]


@dataclass(frozen=True)
class ExtractionOutcome:
    """What `perform` decided, in a form that survives a process boundary."""
    kind: str
    dispatched: Dispatched | None = None
    message: str = ""


def perform(request: ExtractionRequest,
            context: ExtractionContext) -> ExtractionOutcome:
    """`extract_initial` plus the caller's inner `except`, named rather than raised.

    The two blocks this mirrors live in `orchestrator.run_p1_p7` and this function is
    a transcription of them, deliberately: a second, differently-shaped copy of §2.4's
    failure contract is how the parallel path and the serial path would come to
    disagree about one corrupt PDF. The inline pool below runs this same function, so
    the serial default and every worker execute one body.
    """
    try:
        dispatched = extract_initial(
            file_row=request.file_row, decision=request.decision, path=request.path,
            policy=context.policy, readers=context.readers, now=request.now,
            context_window=request.context_window,
            transcription_authorized=context.transcription_authorized)
    except ProtectedContainerRefused as refusal:
        return ExtractionOutcome(PROTECTED, message=str(refusal))
    except DatalessRefused as refusal:
        return ExtractionOutcome(DATALESS, message=str(refusal))
    except ContractViolation as violation:
        return ExtractionOutcome(CONTRACT, message=str(violation))
    except Exception as error:                       # noqa: BLE001 -- §2.4's rule
        # §2.4: "a reader that raises becomes one `failed` run rather than the end of
        # the scan". Built HERE and not in the caller, so the exception object never
        # has to be pickled -- see the module docstring.
        try:
            version = _failed_version(request.decision, request.versions)
        except ContractViolation as violation:
            return ExtractionOutcome(CONTRACT, message=str(violation))
        return ExtractionOutcome(DISPATCHED, Dispatched((failed_result(
            file_row=request.file_row, error=error,
            extractor_name=request.decision.extractor_name,
            extractor_version=version,
            source_type=request.decision.source_type, now=request.now),)))
    return ExtractionOutcome(DISPATCHED, dispatched)


def _failed_version(decision, versions: Mapping[str, str]) -> str:
    """The extractor's version, never the router's. `orchestrator._failed_version`'s
    reasoning, applied on whichever side of the boundary the failure happened."""
    version = versions.get(decision.extractor_name)
    if version is None:
        raise ContractViolation(
            f"the router named {decision.extractor_name!r} and `current_versions()` "
            "has no entry for it, so this run cannot be honestly versioned. The two "
            "tables have drifted; §2.9's routing table is router.py's."
        )
    return version


class InlinePool:
    """No concurrency at all, and the shape of every other pool.

    It computes at `result()` rather than at `submit()`, so with `lookahead = 1` the
    caller's loop makes exactly the calls it made before this module existed, in
    exactly the same order. That is why the parallel path and the serial path are one
    loop: the 7,491 tests that already pass drive this class, so the loop's shape is
    verified by all of them rather than by the handful written for a second one.
    """
    lookahead = 1

    def __init__(self, context: ExtractionContext) -> None:
        self._context = context

    def submit(self, request: ExtractionRequest) -> Any:
        return request

    def result(self, handle: Any) -> ExtractionOutcome:
        return perform(handle, self._context)

    def close(self) -> None:
        return None


@dataclass(frozen=True)
class _Here:
    """A request the pool decided to run on the calling thread. See `ProcessPool`."""
    request: ExtractionRequest


class ProcessPool:
    """`extract_initial` in worker processes, results taken back in submission order.

    **Spawn, explicitly, and not the platform default by accident.** `readers` reaches
    into Apple's Vision and Quartz frameworks through PyObjC, and a forked child that
    inherits an initialised CoreFoundation is the classic macOS crash. `spawn` is
    already Python's default on darwin; naming it here is what makes that a decision
    rather than a version's behaviour, and it is what makes the reader closures
    tractable at all -- a fresh interpreter runs `context_factory` and builds its own.

    **Started on the `floor`-th submit, and not on the first.** A spawned worker
    re-imports the composition root and Apple's Vision framework, which costs about
    five seconds of CPU EACH, so seven workers cost thirty-five CPU-seconds before one
    file is read. Measured on the owner's real files, quiet machine, wall seconds:

        files    workers=1   workers=7
            4       1.0         3.4
           12       2.7         8.2
           24       5.5         6.7

    Small folders are the owner's ORDINARY case -- one course's material, the loose
    files at the top of Documents -- so a pool that pays for seven interpreters to
    read four files is wrong for the product and not merely wasteful. Below the floor
    every request is performed on the calling thread, exactly as `InlinePool` does;
    above it the pool is built and everything after goes to a worker.

    **The floor counts SUBMISSIONS, not files in the folder.** A ten-thousand-file
    corpus that is entirely cached submits nothing and stays inline; four fresh PDFs
    in a folder of ten thousand cached ones also stay inline. What costs money is
    reading, so what is counted is reads.
    """

    def __init__(self, *, workers: int,
                 context_factory: Callable[[], ExtractionContext],
                 lookahead_per_worker: int, floor: int) -> None:
        if workers < 1:
            raise ValueError(f"a pool needs at least one worker, not {workers}")
        self._workers = workers
        self._factory = context_factory
        #: How far the caller reads ahead. Deep enough that a worker is never idle
        #: waiting for the next submit, shallow enough that a 5,760-file run holds a
        #: handful of extraction batches in memory rather than all of them.
        #:
        #: It has NO DEFAULT, and neither does `workers`. Both are numbers, and
        #: `cli.py` is the only file in this product that picks one -- a pool that
        #: defaulted its own depth would be a part choosing a policy, and the reason
        #: the rule exists is that a number nobody reviewed is a number nobody owns.
        self.lookahead = workers * lookahead_per_worker
        self._pool: Any = None
        #: handle -> (what it was asked to do, how many times it has been asked).
        self._outstanding: dict[Any, tuple[ExtractionRequest, int]] = {}
        #: The caller keeps the handle it was GIVEN, so a resubmitted request needs a
        #: forwarding address. Without one, recovery hands back a future the caller
        #: never sees and the caller waits on a cancelled one for ever.
        self._replaced: dict[Any, Any] = {}
        #: The window a pool death took down, held back until the suspect has been
        #: tried alone. See `_rebuild`.
        self._deferred: list[tuple[Any, ExtractionRequest, int]] = []
        #: How many reads a run must want before seven interpreters are worth
        #: starting. No default, for `lookahead_per_worker`'s reason: it is a number.
        if floor < 0:
            raise ValueError(f"a floor is a count of submissions, not {floor}")
        self._floor = floor
        self._submitted = 0
        #: The caller's own context, built from the same factory the workers use, and
        #: only when a request is actually going to run here. A run that crosses the
        #: floor immediately never builds one.
        self._local: ExtractionContext | None = None
        #: Whether an executor was ever built. NOT `self._pool is not None`, which
        #: `close()` resets: the caller closes the pool on its way out, so after a run
        #: the two are indistinguishable and a test asking the wrong one passes
        #: whether or not seven interpreters were started.
        self.started = False

    # -- the pool itself -------------------------------------------------------

    def _executor(self):
        if self._pool is None:
            self.started = True
            import multiprocessing
            from concurrent.futures import ProcessPoolExecutor
            self._pool = ProcessPoolExecutor(
                max_workers=self._workers,
                mp_context=multiprocessing.get_context("spawn"),
                initializer=_install_context, initargs=(self._factory,))
        return self._pool

    def submit(self, request: ExtractionRequest) -> Any:
        self._submitted += 1
        if self._submitted <= self._floor:
            # Below the floor. `_Here` is a handle like any other and `result()`
            # honours it in submission order, so the caller's loop cannot tell which
            # side of the floor a file fell on -- which is what keeps the serial and
            # the parallel path one loop rather than two.
            return _Here(request)
        return self._submit(request, attempts=0)

    def _submit(self, request: ExtractionRequest, *, attempts: int) -> Any:
        future = self._executor().submit(_perform_in_worker, request)
        self._outstanding[future] = (request, attempts + 1)
        return future

    def result(self, handle: Any) -> ExtractionOutcome:
        from concurrent.futures.process import BrokenProcessPool
        if isinstance(handle, _Here):
            if self._local is None:
                self._local = self._factory()
            return perform(handle.request, self._local)
        while True:
            current = handle
            while current in self._replaced:
                current = self._replaced[current]
            request, attempts = self._outstanding.get(current, (None, 0))
            try:
                outcome = current.result()
            except BrokenProcessPool as death:
                if request is None:                  # pragma: no cover -- not ours
                    raise
                if attempts > 1:
                    # It has now killed a pool that held nothing but itself, so it
                    # is this file and not its neighbours. §2.4's rule holds one
                    # level up: the file is unexamined, the run row says so, and the
                    # other 5,759 files still get scanned.
                    self._outstanding.pop(current, None)
                    # SHUT DOWN BEFORE RELEASING, and the order is the whole of it:
                    # the executor that just died is still `self._pool`, and
                    # `_release` submits into whatever `_executor()` returns. Without
                    # this line the held-back window is submitted to the broken pool,
                    # `submit` raises `BrokenProcessPool` out of `result`, and one
                    # segfault ends the run -- which is the exact failure the retry
                    # exists to prevent, reintroduced by the recovery itself.
                    self._shutdown()
                    self._release()
                    return _failure_outcome(request, RuntimeError(
                        "the worker process handling this file died twice; "
                        f"{type(death).__name__}"))
                self._rebuild(suspect=current)
                continue
            except Exception as error:               # noqa: BLE001
                # Never delivered at all -- an argument that would not pickle, a
                # worker the OS killed between submit and run. Same rule, same row.
                self._outstanding.pop(current, None)
                if request is None:                  # pragma: no cover -- not ours
                    raise
                # Released here too. This branch can fire on the ISOLATED suspect --
                # its result may be the thing that would not pickle -- and a window
                # left in `_deferred` is never resubmitted, so the caller waits on a
                # handle whose future was cancelled and the run stops on the next
                # file rather than on this one.
                self._release()
                return _failure_outcome(request, error)
            self._outstanding.pop(current, None)
            self._release()
            return outcome

    def _rebuild(self, *, suspect: Any) -> None:
        """Replace the pool and put the suspect into it ALONE.

        A broken pool fails every future in it, not only the one whose worker died,
        so resubmitting just the offender would turn one segfault into `failed` runs
        for the whole look-ahead window -- files whose only involvement was being next.

        But resubmitting the whole window TOGETHER cannot tell the offender from its
        neighbours either, and that is the trap this shape was written into: the next
        death lands on whichever request the caller is waiting on, so a segfault at
        position fifty would record `failed` runs for the forty-nine innocent files
        ahead of it, one per rebuild. Culpability has to be established rather than
        inferred from position. So the request the caller is waiting on -- which is
        always the head, because results are consumed in submission order -- is
        retried in a pool holding only itself, and the rest of the window is held in
        `_deferred` until it resolves. A file that kills a pool it is alone in is the
        file.

        Each old handle gets a forwarding address, because the caller is holding it.
        """
        pending = list(self._outstanding.items())
        self._shutdown()
        self._outstanding = {}
        request, attempts = dict(pending)[suspect]
        self._replaced[suspect] = self._submit(request, attempts=attempts)
        self._deferred = [(stale, held, count)
                          for stale, (held, count) in pending if stale is not suspect]

    def _release(self) -> None:
        """Resubmit the window a rebuild held back, now that the suspect has answered.

        Their counts are unchanged: surviving somebody else's segfault is not an
        attempt, and counting it as one is what would fail them on the next death.
        """
        if not self._deferred:
            return
        held, self._deferred = self._deferred, []
        for stale, request, attempts in held:
            self._replaced[stale] = self._submit(request, attempts=attempts - 1)

    def _shutdown(self) -> None:
        if self._pool is not None:
            self._pool.shutdown(wait=False, cancel_futures=True)
            self._pool = None

    def close(self) -> None:
        """Cancel the window and stop. Called on the way out, INCLUDING the way out
        through a `ContractViolation`: without `cancel_futures` the caller's raise
        would wait on every in-flight extraction before surfacing."""
        self._shutdown()
        self._outstanding = {}
        self._replaced = {}
        self._deferred = []


def _failure_outcome(request: ExtractionRequest,
                     error: BaseException) -> ExtractionOutcome:
    try:
        version = _failed_version(request.decision, request.versions)
    except ContractViolation as violation:
        return ExtractionOutcome(CONTRACT, message=str(violation))
    return ExtractionOutcome(DISPATCHED, Dispatched((failed_result(
        file_row=request.file_row, error=error,
        extractor_name=request.decision.extractor_name, extractor_version=version,
        source_type=request.decision.source_type, now=request.now),)))


# -- the worker side -----------------------------------------------------------
#
# A module global because `ProcessPoolExecutor`'s initializer has no other way to
# hand something to the calls that follow it, and because the point of the
# initializer is that the readers are built ONCE per worker rather than once per
# file: `pdfminer_reader()` compiles nothing expensive, but `vision_ocr()` reaches
# into a framework that costs 4.6 seconds to import.
_CONTEXT: ExtractionContext | None = None


def _install_context(factory: Callable[[], ExtractionContext]) -> None:
    global _CONTEXT
    _CONTEXT = factory()


def _perform_in_worker(request: ExtractionRequest) -> ExtractionOutcome:
    if _CONTEXT is None:                             # pragma: no cover -- initializer
        raise ContractViolation(
            "a worker ran an extraction before its context was installed")
    return perform(request, _CONTEXT)
