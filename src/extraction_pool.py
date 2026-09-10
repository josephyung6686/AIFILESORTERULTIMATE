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

**And a worker that never returns gets the same second chance.** R-50's ceiling kills
one, and until R-112 the kill was final: one attempt, one `failed` run. Measured over
eleven runs of one pinned 263-file corpus, the same PNG was read completely in ten of
them and wedged its worker in the eleventh -- inside the first Vision call that worker
made, on `flock()` in the Metal shader compiler's machine-wide on-disk cache. A wedge
that turns on the state of a lock is not a property of the file, so the ceiling now
rebuilds and retries exactly as the death path does, and only a file that fails twice
is written off -- and the row NAMES EACH ATTEMPT'S END IN ORDER, because sharing the
counter means a file can die once and wedge once, and a reason written by whichever
path arrived last describes half of what happened (R-120).

**And a worker must not outlive the run that started it.** The paragraph above is
about a worker dying; this one is about one that refuses to. `close()` used to call
`shutdown(wait=False)`, which returns before any worker has been told to stop, and a
run that ends without reaching `close()` at all -- a segfault, a signal -- left them
with nobody to tell. A worker waiting for work blocks in `sem_wait` for ever and goes
on holding the descriptors it inherited, so a caller reading the run's output through
a pipe waits for an end-of-file its dead run's children are holding open. That is a
silent forty-minute hang with no error message, and forty-seven such orphans were
counted on the owner's machine. `_shutdown` now waits, and `_watch_the_parent` covers
the exits that never get there; both are proved by
`tests/integration/test_extraction_pool_lifecycle.py`, which counts operating-system
processes rather than method calls.

The first draft of that recovery resubmitted the whole window together with every
request's retry count bumped, and it was wrong in the direction that matters: the
next death landed on whichever request the caller happened to be waiting on, so a
crash at position fifty would have recorded `failed` runs for the innocent files
ahead of it. `_rebuild` says why culpability has to be established rather than
inferred from position, and the sabotage that restores the old shape fails with
"01-alpha.pdf was failed by its neighbour's crash".
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors import ocr
from extractors.dispatch import (
    Dispatched, extract_initial, perform_targeted_ocr,
)
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
    #: WHETHER THIS SCAN'S OCR BUDGET IS ALREADY SPENT (`104` §18.2 gap 22).
    #:
    #: The ANSWER travels, not the question: §8.6's `ocr.max_time_per_scan` is a
    #: per-SCAN ceiling and a worker sees one file, so the total and the ceiling
    #: both stay with the caller and what crosses is one boolean. It also has to
    #: cross as data rather than be re-read in the worker, because a spawned
    #: worker holds no connection.
    #:
    #: Defaulted, like `Dispatched.ocr_seconds`, so every existing construction
    #: means what it meant: no ceiling stored is no ceiling.
    ocr_budget_spent: bool = False


@dataclass(frozen=True)
class TargetedOcrRequest:
    """§2.7's post-P6 OCR pass for one PDF, as data. R-138.

    **IT CARRIES NO PRIOR RESULT AND NO VERSION TABLE, and both absences are the
    point.** `extract_targeted_ocr` takes a `native_result` and a database-backed
    predicate, and neither can cross a process boundary usefully: the predicate
    holds a connection, and the prior result is the file's whole native reading,
    which would be pickled in full to be looked at once. `dispatch.targeted_ocr_wanted`
    spends both on the calling thread and what is left is this -- a path, a stamp
    and the row -- which is everything `perform_targeted_ocr` needs.

    No `versions` either, because the run this can fail into is an OCR run and
    `ocr.VERSION` is a constant this deployment does not vary. `ExtractionRequest`
    needs the table because the extractor it fails into is whichever one the router
    named.
    """
    file_id: str
    file_row: Mapping[str, Any]
    path: Path
    now: str
    context_window: int
    #: `ExtractionRequest.ocr_budget_spent`'s twin, and it is asked separately
    #: because this pass runs LATER: the initial loop may have spent the rest of
    #: §8.6's OCR clock between the two, and a flag computed once at submission
    #: would let the targeted pass overspend a ceiling the scan had already met.
    ocr_budget_spent: bool = False


@dataclass(frozen=True)
class ExtractionOutcome:
    """What `perform` decided, in a form that survives a process boundary."""
    kind: str
    dispatched: Dispatched | None = None
    message: str = ""


def perform(request: ExtractionRequest | TargetedOcrRequest,
            context: ExtractionContext) -> ExtractionOutcome:
    """`extract_initial` plus the caller's inner `except`, named rather than raised.

    The two blocks this mirrors live in `orchestrator.run_p1_p7` and this function is
    a transcription of them, deliberately: a second, differently-shaped copy of §2.4's
    failure contract is how the parallel path and the serial path would come to
    disagree about one corrupt PDF. `InlinePool` below runs this same function, so
    a pool that reads on the calling thread and every worker execute one body.

    **BOTH REQUEST KINDS ARRIVE HERE, and that is why the dispatch is one line at
    the top rather than a second entry point.** `InlinePool.result` and
    `_perform_in_worker` are the only two callers, so a second `perform_*` would
    have to be reached by both, through a pool that had learned to tell them apart
    -- and the pool's whole shape is that a handle is a handle. The request knows
    what it is; nothing else has to.
    """
    if isinstance(request, TargetedOcrRequest):
        return _perform_targeted(request, context)
    try:
        dispatched = extract_initial(
            file_row=request.file_row, decision=request.decision, path=request.path,
            policy=context.policy, readers=context.readers, now=request.now,
            context_window=request.context_window,
            transcription_authorized=context.transcription_authorized,
            ocr_budget_spent=request.ocr_budget_spent)
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


def _perform_targeted(request: TargetedOcrRequest,
                      context: ExtractionContext) -> ExtractionOutcome:
    """`perform`, for the pass `targeted_ocr_wanted` already authorized.

    The three refusals come back as the kinds the caller re-raises, exactly as they
    do above, because `orchestrator.run_p1_p7` let them propagate out of
    `extract_targeted_ocr` before this pass moved off its thread and a pool that
    swallowed them would change what a run does about a protected path.

    The catch-all is reached only by something outside `_ocr`, which has its own:
    "an engine that RAISES is a runtime event", turned into a `failed` OCR run
    there rather than allowed to discard the native result the caller is holding.
    Kept anyway, because a worker cannot raise into its caller and an outcome is
    the only way anything gets back.
    """
    try:
        dispatched = perform_targeted_ocr(
            file_row=request.file_row, path=request.path, policy=context.policy,
            readers=context.readers, now=request.now,
            context_window=request.context_window,
            ocr_budget_spent=request.ocr_budget_spent)
    except ProtectedContainerRefused as refusal:
        return ExtractionOutcome(PROTECTED, message=str(refusal))
    except DatalessRefused as refusal:
        return ExtractionOutcome(DATALESS, message=str(refusal))
    except ContractViolation as violation:
        return ExtractionOutcome(CONTRACT, message=str(violation))
    except Exception as error:                       # noqa: BLE001 -- §2.4's rule
        return ExtractionOutcome(
            DISPATCHED, Dispatched((_targeted_failure(request, error),)))
    return ExtractionOutcome(DISPATCHED, dispatched)


def _targeted_failure(request: TargetedOcrRequest,
                      error: BaseException) -> ExtractionResult:
    """The `failed` run a lost targeted OCR pass gets, ON THE OCR TIER.

    **THE TIER IS THE WHOLE OF THIS FUNCTION.** The obvious thing -- reuse
    `_failure_outcome`, which names `request.decision.extractor_name` -- would write
    a second `pdf.text native failed` run beside the `pdf.text native complete` run
    this file already has, because the native pass SUCCEEDED and it is the optional
    second pass that was lost. Three things then read that row and all three read it
    wrongly: `WORST_FIRST` reports the file as failed when its text was recovered,
    `set_extraction_status` marks the native tier failed for a tier that finished,
    and `authoritative_result` meets two native runs for one content hash and raises
    `AmbiguousAuthoritativeRun` on the NEXT run over the same corpus.

    So the attribution is `_ocr`'s own, unchanged: the unreported provider name, the
    OCR version, the OCR source type and the OCR tier. That is the row a person can
    act on -- the text was read, the picture of it was not.
    """
    return failed_result(
        file_row=request.file_row, error=error,
        extractor_name=ocr.UNREPORTED_PROVIDER_NAME,
        extractor_version=ocr.VERSION,
        source_type=ocr.SOURCE_TYPE, now=request.now,
        analysis_tier=ocr.ANALYSIS_TIER)


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

    **NO DEPLOYMENT REACHES IT SINCE R-138, and that is the point of this note.**
    `cli.extraction_pool` returned this for `workers == 1`, and a reader that runs on
    the calling thread cannot be given a deadline -- a Python timeout does not
    interrupt a C dispatch wait on the thread doing the waiting. So the composition
    root now builds a `ProcessPool` at every worker count and this class survives as
    what the suite drives: a pool double with no processes, which is why a test that
    wants to assert about extraction rather than about concurrency can use it.
    """
    lookahead = 1

    def __init__(self, context: ExtractionContext) -> None:
        self._context = context

    def submit(self, request: ExtractionRequest | TargetedOcrRequest) -> Any:
        return request

    def result(self, handle: Any) -> ExtractionOutcome:
        return perform(handle, self._context)

    def close(self) -> None:
        return None


class ProcessPool:
    """`extract_initial` in worker processes, results taken back in submission order.

    **Spawn, explicitly, and not the platform default by accident.** `readers` reaches
    into Apple's Vision and Quartz frameworks through PyObjC, and a forked child that
    inherits an initialised CoreFoundation is the classic macOS crash. `spawn` is
    already Python's default on darwin; naming it here is what makes that a decision
    rather than a version's behaviour, and it is what makes the reader closures
    tractable at all -- a fresh interpreter runs `context_factory` and builds its own.

    **EVERY REQUEST GOES TO A WORKER, and that is R-138's ruling rather than an
    oversight.** There was a floor: below the `floor`-th submission a request was
    performed on the calling thread, exactly as `InlinePool` does, because a spawned
    worker re-imports the composition root and Apple's Vision framework and small
    folders are the owner's ORDINARY case. The ceiling below could not reach a
    request performed there. A Python timeout cannot interrupt a C dispatch wait on
    its own thread -- that is the whole reason the ceiling kills a PROCESS -- so a
    file read below the floor ran with no deadline at all, and this module's own
    history says what that costs: `_watch_the_parent` records a segfault taken on a
    file read below the floor.

    R-138's own hang was NOT this path, and the correction is kept because the row
    reads otherwise. Sampled, r6's main thread was inside
    `-[VNImageRequestHandler performRequests:]` with no Python thread alive in the
    process, which places it after `pool.close()` in `orchestrator`'s fact loop --
    the targeted OCR pass, now submitted here like any other reading. The floor was
    the second unbounded path of the same class, found while looking for the first,
    and a bound that holds for one and not the other is not a bound.

    **The alternative was a list, and a list is the thing that silently omits.**
    Keeping the floor means naming which requests may run here, and on this
    deployment's wiring that name cannot be written: `.doc` and `.txt` share the
    source type `text_document`, and `readers/deployment.py` wires the first to
    AppKit and the second to the standard library. A predicate over the family
    either leaves the Cocoa reader unbounded or excludes plain text, notes and
    Markdown -- the light files the floor was measured to win on -- so the floor's
    own case does not survive its own safety condition. A bound that holds for every
    reader by construction is worth more than one that holds for the readers
    somebody remembered.

    **What it costs, re-measured on 2026-09-07.** The floor's old table timed whole
    runs; this times the pool alone over synthetic text files, which is the part the
    floor actually changed. Wall seconds, warm machine, three repeats:

        files    inline    workers=1    workers=7
            4      0.00      1.2-1.7      1.2-2.2
           12      0.01      1.4-5.4      2.0-3.6
           24      0.02      1.2-1.7      1.9-4.1

    It is a per-RUN cost and not a per-file one -- what is bought is the
    interpreters, and they are started once -- so it does not grow with the corpus,
    and the folder it is largest against is the smallest. One to four seconds, for a
    run that cannot hang.

    **A run that reads nothing still starts nothing.** The executor is built on the
    first submission and `started` says whether it ever was, so a ten-thousand-file
    corpus that is entirely cached submits nothing and pays none of the above. What
    costs money is reading, so what starts interpreters is reads.
    """

    def __init__(self, *, workers: int,
                 context_factory: Callable[[], ExtractionContext],
                 lookahead_per_worker: int,
                 seconds_per_extraction: float,
                 now: Callable[[], float] = time.monotonic) -> None:
        if workers < 1:
            raise ValueError(f"a pool needs at least one worker, not {workers}")
        #: R-50. HOW LONG ONE EXTRACTION MAY TAKE BEFORE ITS WORKER IS KILLED.
        #:
        #: The recovery above answers a worker that DIES. This answers one that never
        #: returns, which is a different failure and was unanswerable: no exception is
        #: raised, no process exits, and the parent waits in `result()` for ever at 0%
        #: CPU. Measured on the owner's corpus, three of seventeen situations hung --
        #: `applications.undergraduate-packet`, `business_operations.project-delivery`,
        #: `code.notebooks-experiments`. Sampled, one worker's main thread was inside
        #: `-[VNRecognizeTextRequest ...]` -> `-[CIContext render:toCVPixelBuffer:...]`
        #: -> CoreImage -> `_dispatch_sync_f_slow` -> `__DISPATCH_WAIT_FOR_QUEUE__`: a
        #: dispatch deadlock inside Apple's frameworks, reached through PyObjC from the
        #: OCR reader. The other six workers sat in `sem_wait`.
        #:
        #: `00`:257 is the rule it enforces -- a single file may not consume the run --
        #: and until now nothing could enforce it against a file that consumes the run
        #: by doing nothing at all.
        #:
        #: NO DEFAULT, for the reason `workers` and `lookahead_per_worker` each
        #: give: it is a number, `cli.py` is the only file that picks one, and a
        #: pool that defaulted the ceiling at which it kills a worker would be a part
        #: choosing a policy with teeth.
        if seconds_per_extraction <= 0:
            raise ValueError(
                f"a ceiling of {seconds_per_extraction} would fail every file "
                "before it started; a ceiling is how long an extraction may take")
        self._ceiling = float(seconds_per_extraction)
        #: THE CLOCK THE CEILING IS MEASURED ON, and the one thing here that DOES
        #: carry a default. `seconds_per_extraction` is a policy with teeth and
        #: refuses one; a monotonic source is not a policy, `time.monotonic` is the
        #: only real answer, and requiring every caller to pass it would be
        #: ceremony rather than a decision.
        #:
        #: It is injectable because the guard that protects this ceiling's SEMANTICS
        #: could not be written against the real clock. What the guard has to prove
        #: is that the ceiling starts when the consuming loop begins waiting for a
        #: file and not when the file was submitted -- and expressing that in real
        #: seconds means a sleeping neighbour racing a wall clock, which fails on a
        #: loaded machine for a reason that has nothing to do with the defect.
        #: Observed: two of these tests failed at load 13 with "01-alpha.pdf was
        #: failed by its neighbour" while eight suites ran, on CPU contention rather
        #: than on the clock. Driven by a test, fake time can pass between submit
        #: and the first wait, which is exactly the condition a submit-measured
        #: ceiling gets wrong, and no amount of machine load changes the answer.
        self._now = now
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
        #: handle -> (what it was asked to do, how many times it has been asked,
        #: how each earlier attempt ENDED, in order). R-120: the third element is
        #: what lets a file that died once and wedged once say so, rather than be
        #: reported by whichever of the two paths happened to arrive last.
        self._outstanding: dict[
            Any, tuple[ExtractionRequest, int, tuple[str, ...]]] = {}
        #: The caller keeps the handle it was GIVEN, so a resubmitted request needs a
        #: forwarding address. Without one, recovery hands back a future the caller
        #: never sees and the caller waits on a cancelled one for ever.
        self._replaced: dict[Any, Any] = {}
        #: The window a pool death took down, held back until the suspect has been
        #: tried alone. See `_rebuild`.
        self._deferred: list[
            tuple[Any, ExtractionRequest, int, tuple[str, ...]]] = []
        #: Whether an executor was ever built. NOT `self._pool is not None`, which
        #: `close()` resets: the caller closes the pool on its way out, so after a run
        #: the two are indistinguishable and a test asking the wrong one passes
        #: whether or not seven interpreters were started.
        #:
        #: It is still worth asking after R-138 removed the floor, and for the reason
        #: the floor's last paragraph gave: an executor is built on the first SUBMIT,
        #: so a corpus that is entirely cached starts no interpreter at all. What
        #: costs money is reading, and a run that reads nothing pays nothing.
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

    def submit(self, request: ExtractionRequest | TargetedOcrRequest) -> Any:
        # EVERY request, and R-138 is why. A handle this method returned without a
        # worker behind it was a wait the ceiling in `result()` could not bound, and
        # a reader wedged inside Apple's frameworks on the calling thread is a run
        # that never ends. The class docstring holds the measurement.
        return self._submit(request, attempts=0)

    def _submit(self, request: ExtractionRequest | TargetedOcrRequest, *,
                attempts: int,
                ends: tuple[str, ...] = ()) -> Any:
        future = self._executor().submit(_perform_in_worker, request)
        self._outstanding[future] = (request, attempts + 1, ends)
        return future

    def result(self, handle: Any) -> ExtractionOutcome:
        from concurrent.futures import TimeoutError as FuturesTimeout
        from concurrent.futures.process import BrokenProcessPool
        #: THE CLOCK STARTS WHEN THE CALLER STARTS WAITING FOR THIS FILE, not when
        #: the request was submitted, and that is a correction with a measurement
        #: behind it. Submitted-at was the first draft and the full suite failed it
        #: within the hour: the hung file burned the ceiling while its neighbours
        #: sat in the queue, so when their turn came they were already over it and
        #: `01-alpha.pdf` and `02-bravo.pdf` were both marked timed out having done
        #: nothing wrong. One deadlock would have failed the entire look-ahead
        #: window on the owner's corpus -- the precise failure the death path's
        #: `_rebuild` exists to prevent, reintroduced by this recovery.
        #:
        #: Results are consumed in submission order, so what this measures is "how
        #: long has this file been the one holding up the run", which is the
        #: question `00`:257 actually asks and the only one whose answer is not
        #: distorted by the queue. The run still cannot hang: every wait is bounded.
        deadline = self._now() + self._ceiling
        while True:
            current = handle
            while current in self._replaced:
                current = self._replaced[current]
            request, attempts, ends = self._outstanding.get(
                current, (None, 0, ()))
            try:
                outcome = current.result(
                    timeout=max(0.0, deadline - self._now()))
            except FuturesTimeout:
                # R-50/R-112. NOBODY DIED AND NOBODY ANSWERED, and the file gets a
                # second attempt for the same reason a segfault does: the wedge is
                # not a property of the bytes.
                #
                # THE FIRST RULING HERE SAID THE OPPOSITE -- "a deadlock reached
                # through the same bytes and the same framework will be reached
                # again" -- and R-112 measured it false. Eleven runs of the product
                # over one pinned 263-file corpus: the same PNG, content hash
                # `782ff3d1...`, read completely in ten of them and wedged its worker
                # in the eleventh, which cost that run 626.4 seconds against 20 to 26
                # for the others. Sampled at the wedge, the worker's main thread was
                # in `-[VNImageRequestHandler performRequests:]` ->
                # `-[CIContext render:toCVPixelBuffer:]` ->
                # `CI::ProgramNode::mainProgram` -> `__DISPATCH_WAIT_FOR_QUEUE__`,
                # waiting on `CI::KernelCompileQueue`; that queue was blocked in
                # `flock()` inside `MTLCompilerFSCache::openSync` -- the Metal shader
                # compiler's on-disk cache lock, which every process on the machine
                # shares. Six of the seven workers took that lock and released it in
                # about three seconds. The seventh never came back.
                #
                # So what wedged was the state of a machine-wide lock at the instant
                # one worker made its first Vision call, and the file was read a
                # second later by the next run over identical bytes. Writing it off
                # after one attempt sent a person away with a file that was never
                # unreadable, to get it back only by running the scan again.
                #
                # The retry is ONE, and `attempts` is the same counter the death path
                # keeps: a file may cost this run two ceilings and no more, which is
                # `00`:257's rule surviving the recovery written to keep it.
                if request is None:                  # pragma: no cover -- not ours
                    raise
                # R-120. HOW THIS ATTEMPT ENDED, named here where it is known,
                # because two lines from now it is the only place that knows. The
                # branch below and `_rebuild` both take it from this one variable,
                # so the sentence a file gets is assembled from the ends it
                # actually had rather than from the path that reached the end.
                ended = f"no result within the {self._ceiling}s ceiling"
                if attempts > 1:
                    self._outstanding.pop(current, None)
                    # THE WINDOW IS HELD BACK FIRST, which is `_rebuild`'s rule
                    # reached by a different road. Killing the pool takes down every
                    # worker, including the ones reading innocent files, so anything
                    # still in flight has to be resubmitted rather than failed --
                    # surviving somebody else's deadlock is not an attempt, and
                    # `_release` restores the count. A future that has already
                    # FINISHED keeps its result and its bookkeeping: it is not in
                    # flight, nothing was lost, and resubmitting it would write a
                    # second run row for a file the caller has not consumed yet.
                    lost = [(stale, held)
                            for stale, held in self._outstanding.items()
                            if not stale.done()]
                    # KILL BEFORE SHUTDOWN, and the order is the whole of it. A
                    # worker deadlocked inside a framework will not answer a stop
                    # sentinel, so `_shutdown`'s `wait=True` would wait on it for
                    # ever -- the hang this fix exists to end, moved into the
                    # recovery for it.
                    self._kill_workers()
                    self._shutdown()
                    for stale, _held in lost:
                        self._outstanding.pop(stale, None)
                    # EXTENDED, NEVER ASSIGNED, and the difference is a lost window.
                    # This branch is reachable while a REBUILD's window is already
                    # deferred: a pool death isolates the suspect, `_outstanding`
                    # holds only that suspect, and the suspect then hangs. `lost` is
                    # empty there, and assigning would wipe the held-back window --
                    # whose callers are holding handles whose futures were cancelled,
                    # so the run stops on the next file with nothing to say.
                    # `_release` below drains both.
                    self._deferred.extend(
                        (stale, held, count, seen)
                        for stale, (held, count, seen) in lost)
                    self._release()
                    return _failure_outcome(
                        request, RuntimeError(
                            _both_attempts_failed(request, ends + (ended,))))
                # KILLED BEFORE THE REBUILD, and for the reason the branch above
                # gives: `_rebuild` shuts the executor down with `wait=True`, and a
                # worker wedged inside a framework answers no stop sentinel. Without
                # the kill the recovery inherits the hang it was written to end.
                self._kill_workers()
                # `_rebuild` READS `current` OUT OF `_outstanding`, so it is not
                # popped first. The suspect goes into a pool holding nothing but
                # itself and the rest of the window is held back until it answers --
                # the death path's shape exactly, and it is what makes the second
                # attempt's first framework call uncontended by anything this run is
                # doing.
                self._rebuild(suspect=current, ended=ended)
                # A NEW CLOCK, for the reason the death path's retry gives one line
                # further down: the file is being read again from the start, and
                # charging the second attempt the time the first one's wedge cost
                # would kill it for having survived.
                deadline = self._now() + self._ceiling
                continue
            except BrokenProcessPool as death:
                if request is None:                  # pragma: no cover -- not ours
                    raise
                # R-120, and the same move the ceiling branch makes above.
                ended = f"the worker process died ({type(death).__name__})"
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
                    return _failure_outcome(
                        request, RuntimeError(
                            _both_attempts_failed(request, ends + (ended,))))
                self._rebuild(suspect=current, ended=ended)
                # A NEW CLOCK, because a rebuild means this file is being read
                # again from the start. Charging the retry the time its own
                # predecessor's death cost would kill a file for surviving a
                # segfault, which is the same unfairness the paragraph above is
                # about, one exception further along.
                deadline = self._now() + self._ceiling
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

    def _kill_workers(self) -> None:
        """SIGKILL every worker, because one of them is not answering anything else.

        `Process.terminate()` is SIGTERM and a process wedged in
        `__DISPATCH_WAIT_FOR_QUEUE__` inside CoreImage does not run a Python signal
        handler to see it -- Python's handler runs on the main thread between
        bytecodes, and the main thread is inside the framework. `kill()` is the
        signal the kernel delivers without asking the process.

        The whole pool goes, not the one worker. `ProcessPoolExecutor` gives no way
        to say which worker holds a given future, and killing the pool is what the
        death path already does by other means: `_rebuild` replaces the executor and
        the held-back window is resubmitted. The innocent workers lose at most the
        extraction they were in, which is resubmitted with its attempt count
        unchanged -- surviving somebody else's deadlock is not an attempt.

        `_processes` is private and there is no public equivalent. Read defensively
        so a future CPython that renames it degrades to the old behaviour -- a slow
        `shutdown` -- rather than an AttributeError in the recovery path.
        """
        pool = self._pool
        if pool is None:                             # pragma: no cover -- not ours
            return
        workers = list(getattr(pool, "_processes", {}).values())
        for worker in workers:
            try:
                worker.kill()
            except (OSError, ValueError):            # pragma: no cover -- raced
                continue
        for worker in workers:
            worker.join(timeout=self._ceiling)

    def _rebuild(self, *, suspect: Any, ended: str) -> None:
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

        `ended` is how the suspect's attempt just finished, and it travels with the
        retry. Both callers reach here having ended an attempt in a way only they
        can name -- one a death, one a ceiling -- and a file may reach its second
        attempt through either. Carrying the words rather than a flag is what lets
        the reason for a file that died once and wedged once name both, which is
        R-120. The held-back window carries whatever ends its files already had:
        surviving somebody else's failure is not an attempt and adds nothing.
        """
        pending = list(self._outstanding.items())
        self._shutdown()
        self._outstanding = {}
        request, attempts, ends = dict(pending)[suspect]
        self._replaced[suspect] = self._submit(
            request, attempts=attempts, ends=ends + (ended,))
        self._deferred = [(stale, held, count, seen)
                          for stale, (held, count, seen) in pending
                          if stale is not suspect]

    def _release(self) -> None:
        """Resubmit the window a rebuild held back, now that the suspect has answered.

        Their counts are unchanged: surviving somebody else's segfault is not an
        attempt, and counting it as one is what would fail them on the next death.
        """
        if not self._deferred:
            return
        held, self._deferred = self._deferred, []
        for stale, request, attempts, ends in held:
            self._replaced[stale] = self._submit(
                request, attempts=attempts - 1, ends=ends)

    def _shutdown(self) -> None:
        """Stop the pool, WAIT for it, and stop waiting at the ceiling.

        `wait=True` and `cancel_futures` do different jobs. `cancel_futures` drops
        the QUEUED window, which is what keeps a raise prompt; `wait` governs
        whether the worker PROCESSES are still running when this returns. It was
        False, and False meant `shutdown` returned before a single stop-sentinel had
        been sent -- leaving the reaping to `concurrent.futures.process._python_exit`,
        an interpreter-shutdown hook that a run killed by a signal never reaches. So
        what is waited for here is at most one extraction per worker, the ones
        already in a reader, never the queued window.

        **AND THE WAIT IS BOUNDED, because "at most one extraction per worker" was an
        assumption about workers that answer.** A worker wedged inside Apple's
        frameworks answers no stop sentinel -- the ceiling branch and `_rebuild` both
        say so, and both call `_kill_workers` before they come here. This method was
        the third caller and it killed nothing, so the one path that reaches it with
        a wedge still live -- a `ContractViolation` raised while a worker is inside a
        reader, out through `run_p1_p7`'s `finally` -- joined the executor manager
        thread with no bound at all. That is the silent hang the ceiling exists to
        end, moved into the exit from the run.

        So the join is given the pool's own ceiling, and then the workers are killed.
        NO SECOND CONSTANT: the number that says how long one extraction may take is
        the number that says how long stopping one may take, and a run that has
        already decided to leave has nothing to gain by waiting longer than it would
        have waited for the reading itself.

        `Executor.shutdown` blocks and takes no timeout, so the bound is a thread.
        It is a daemon because a run whose interpreter is going down must not be held
        open by the helper that was cleaning up after it.
        """
        pool, self._pool = self._pool, None
        if pool is None:
            return
        import threading

        stopping = threading.Thread(
            target=pool.shutdown, kwargs={"wait": True, "cancel_futures": True},
            daemon=True)
        stopping.start()
        stopping.join(self._ceiling)
        if stopping.is_alive():
            # Nothing answered the sentinel. `_kill_workers` reads `self._pool`, so
            # it is put back for the length of that call and taken away again: the
            # attribute is what `close()` and `_executor` read to decide whether a
            # pool exists, and a half-shut one must look alive to neither.
            self._pool = pool
            try:
                self._kill_workers()
            finally:
                self._pool = None
            # Bounded as well. The workers are dead by now -- `_kill_workers` joins
            # each one -- so what is left is the manager thread noticing, and a wait
            # that could not end is the defect this method has just stopped having.
            stopping.join(self._ceiling)

    def close(self) -> None:
        """Cancel the window and stop, and BE STOPPED when this returns.

        Called on the way out, INCLUDING the way out through a `ContractViolation`:
        without `cancel_futures` the caller's raise would wait on every in-flight
        extraction before surfacing. It waits for the handful still inside a reader,
        because a worker this run has finished with must not still be alive when the
        run ends -- see `_watch_the_parent` for what a surviving one costs.

        **AND IT RETURNS WHETHER OR NOT THEY ANSWER.** That `ContractViolation` exit
        is the one path in this class that can reach a shutdown with a WEDGED worker
        still live, because every other path that meets a wedge kills first. So
        `_shutdown` waits one ceiling and then kills, and this method's promise --
        be stopped when it returns -- is now true of a reader that has stopped
        answering as well as of one that is merely slow.
        """
        self._shutdown()
        self._outstanding = {}
        self._replaced = {}
        self._deferred = []


def _both_attempts_failed(request: ExtractionRequest | TargetedOcrRequest,
                          ends: tuple[str, ...]) -> str:
    """The reason for a file that has spent both of its attempts without a reading.

    **EACH ATTEMPT IS NAMED BY ITS OWN END, IN ORDER, and R-120 is why.** The two
    paths that can end an attempt -- a worker that dies and a worker that never
    answers -- share the one `attempts` counter, so a file can arrive here having
    done one of each. The reason used to be written by whichever path happened to
    arrive last: a file that segfaulted and then wedged was recorded as "killed
    both times", one that wedged and then segfaulted as "died twice". Each sentence
    is false about half of what the run did, and it is the expensive half -- a
    person reading the row was told the run met a repeat of a failure it had met
    once, and sent to look for a defect in the file that reproduces rather than for
    the machine state that does not.

    The exception TYPE is the same for both branches for the same reason.
    `failed_result` writes `failure_reason` as `f"{type(error).__name__}: {error}"`,
    so a `TimeoutError` on a file that died first would put the last attempt's mode
    back at the front of the row that this sentence exists to keep honest.

    The bound is untouched: this is reached only at two attempts, and `ends` holds
    one entry per attempt that has already finished.
    """
    named = "; ".join(f"attempt {number}: {end}"
                      for number, end in enumerate(ends, start=1))
    return (f"two attempts at {_reader_named(request)} for this file, "
            f"neither of which returned a reading -- {named}; the pool was rebuilt "
            "after each, so the rest of the run continues")


def _reader_named(request: ExtractionRequest | TargetedOcrRequest) -> str:
    """Which reader spent the two attempts, for the sentence a person reads.

    A targeted pass has no routing decision -- `targeted_ocr_wanted` spent it on the
    calling thread -- so it names the engine `_ocr` names. Reading
    `request.decision` here would be an `AttributeError` inside the recovery path,
    which is the one place in this module that must not raise.
    """
    if isinstance(request, TargetedOcrRequest):
        return ocr.UNREPORTED_PROVIDER_NAME
    return request.decision.extractor_name


def _failure_outcome(request: ExtractionRequest | TargetedOcrRequest,
                     error: BaseException) -> ExtractionOutcome:
    """The `failed` run for a request the pool gave up on, attributed to its tier.

    A targeted pass fails on the OCR tier and never on the native one, and
    `_targeted_failure` says at length what writing it natively would break: this
    file's native run SUCCEEDED, and a second native row for the same content hash
    is a file reported unread, a tier marked failed, and `AmbiguousAuthoritativeRun`
    on the next run over the same corpus.
    """
    if isinstance(request, TargetedOcrRequest):
        return ExtractionOutcome(
            DISPATCHED, Dispatched((_targeted_failure(request, error),)))
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
    _watch_the_parent()
    _CONTEXT = factory()


def _watch_the_parent() -> None:
    """Die when the run does, however the run goes.

    **A worker outliving its parent is not untidy, it is a hang.** `close()` shuts
    the pool down properly now, but `close()` is only reached by a run that gets to
    the end of a `try`. A run killed by a signal does not, and neither does one whose
    interpreter is gone: `pdfium` segfaulted the product on a real 199-file corpus
    (`FPDF_LoadPage` -> `CPDF_ColorSpace::CreateBufAndSetDefaultColor`, on a file
    read below the floor there was then and therefore on the calling thread), and
    the workers already spawned were left with nobody to stop them. R-138 has since
    removed that floor and every read is a worker's, which takes the crash off the
    calling thread and changes nothing about this: a worker still outlives a parent
    that dies, and a parent can still die.

    What they then do is the part that turns a leak into a deadlock. A worker waiting
    for work blocks in `sem_wait` on the call queue for ever -- every sibling holds
    that queue's writer, so the queue never reaches end-of-file the way a pipe would.
    Meanwhile it still holds the file descriptors it inherited, and descriptors 1 and
    2 are the run's stdout and stderr. When those are pipes -- `tools/groundtruth`
    reads its runs through `subprocess.run(capture_output=True)`, and so does every
    caller who captures output -- the reader waits for an end-of-file that a dead
    run's surviving children are still holding open. Observed: a parent at 0.0 % CPU
    with no child of its own, stalled forty minutes, released INSTANTLY when the
    orphans were killed by hand. Forty-seven of them had accumulated on the machine.

    So each worker watches for its parent's death directly. `parent_process()` in a
    spawned child carries the read end of the pipe the parent alone holds the writer
    for -- not the call queue, which every sibling can write, and not `getppid()`,
    which has to be polled on an interval nobody chose. `join()` blocks on that
    descriptor and returns the moment the parent stops existing, by exit, by
    exception, by `SIGKILL` or by segmentation fault alike. Then `os._exit`, which is
    the only correct ending here: `sys.exit` would unwind one daemon thread and leave
    the process running, and a normal exit would run handlers that flush queues whose
    other end is dead.
    """
    import multiprocessing
    import threading

    parent = multiprocessing.parent_process()
    if parent is None:                               # pragma: no cover -- not spawned
        # Not a spawned child, so there is no parent to outlive. `InlinePool` runs
        # `perform` on the calling thread and must not install anything.
        return

    def until_the_parent_is_gone() -> None:
        parent.join()
        os._exit(1)

    threading.Thread(target=until_the_parent_is_gone, daemon=True).start()


def _perform_in_worker(
        request: ExtractionRequest | TargetedOcrRequest) -> ExtractionOutcome:
    if _CONTEXT is None:                             # pragma: no cover -- initializer
        raise ContractViolation(
            "a worker ran an extraction before its context was installed")
    return perform(request, _CONTEXT)
