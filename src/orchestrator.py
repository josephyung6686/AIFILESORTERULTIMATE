# src/orchestrator.py
"""Wave 2's caller: P3 scan -> P5 route/extract -> P4 record -> P1 status -> P2 bundle.

**Not a part.** It owns no design section, publishes no vocabulary, and adds no table.
`02-segmentation-map.md` says the walking skeleton "stays in the repository as the
integration test every later part must keep green"; this module makes the Wave-2 half
of it ONE path rather than four separate stories. P1, P2 and P3 shipped, P4 and P5
went green, and nothing called them in sequence: `scan()` returned a `scan_run_id`
and stopped.

What it owns:

1. **Order.** Once per scan run.
2. **The exception contract** -- which refusal produces a run row and which produces
   nothing.
3. **The two joins each part half-published** -- `source_scan_ref = scan_run_id` and
   `files.extraction_status_by_tier`.
4. **Passing `author` through.** M8, §8.2: the acting part authors, P1 stores.

What it does not own: no vocabulary (it spells no `completeness`, `source_type`,
`analysis_tier`, zone or event type -- every such value reaches P1/P4 inside a record
a part constructed), no derivation (`extraction_status_by_tier` is P5's,
`bundle_counts` P2's), no ceiling enforcement, no refusal of its own, and no
authorship: it never appears in an event's `subsystem`. §8.2's reconstruction
requirement is unmeetable from a log whose author field names the thing that merely
arranged the work.
"""
from __future__ import annotations

import json
import sqlite3
from collections import deque
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping, NamedTuple, Sequence

from database_agent.files_table import get_file as _get_file_row, set_extraction_status

from eval_harness.bundle import (
    add_expectation, add_extraction_output, add_extraction_run, add_file_entry,
    add_text_unit, canonical_json, open_bundle, seal_bundle,
)

from evidence_shape.store import (
    AmbiguousAuthoritativeRun, authoritative_result, observation_keys_for_run,
    observations_for_run, runs_for_content, runs_for_file, text_units_for_run,
)

from extractors.authorship import COMPONENT_VERSION, SUBSYSTEM
from extractors import image, ocr, pdf
from extractors.budgets import (
    DEFERRED_COMPLETENESS as _P5_DEFERRED_COMPLETENESS,
    deferred_result, p5_ceilings,
)
from extractors.dispatch import (
    current_versions, extract, extract_initial, extract_targeted_ocr,
    targeted_ocr_wanted,
)
from extraction_pool import (
    CONTRACT, DATALESS, PROTECTED, ExtractionRequest, TargetedOcrRequest,
)
from extractors.failure import ContractViolation, failed_result
from extractors.filesystem import dataless_result, extract_filesystem
from extractors.long_tail import record_sensitivity_signals
from extractors.router import record_routing_decision, route
from extractors.runs import extraction_status_by_tier
from extractors.safety import DatalessRefused, ProtectedContainerRefused
from extractors.sink import ExtractionResult

from scan_agent.dataless import dataless_detections
from scan_agent.scan import scan
from scan_agent.stat_cache import VERDICT_RECOMPUTE, cache_verdicts

from privacy.classification import ClassificationRecord, resolve_class
from privacy.classification_store import ClassificationStore
from privacy.learning_seam import assign

_add_file_entry = add_file_entry

#: P4's word for a run a budget stopped, spelled ONCE here. This module "spells no
#: `completeness`" by its own docstring, so it does not author this one either --
#: `extractors/budgets.DEFERRED_COMPLETENESS` is P5's published pair of the two
#: states §8.6 counts as deferred, and `deferred` is the member of it that means
#: "stopped before it started" rather than "read something and stopped". The
#: membership check below fails at import if P5 ever renames it.
DEFERRED_COMPLETENESS: str = "deferred"
if DEFERRED_COMPLETENESS not in _P5_DEFERRED_COMPLETENESS:
    raise ImportError(
        f"P5 no longer counts {DEFERRED_COMPLETENESS!r} among its deferred states "
        f"({_P5_DEFERRED_COMPLETENESS}); §8.6's per-scan ceilings write that word "
        "and this module reads it back, so a rename has to break here rather than "
        "silently stop every deferral being recognised as one."
    )


def TARGETED_OCR_UNAVAILABLE(file_id: str, content_hash: str) -> bool:
    """Legacy Wave 2 has not run P6, so its broken-text route is unavailable.

    §2.2 names three text-layer states and the broken one is reachable only from P6's
    `no_usable_facts` verdict — "targeted OCR on a PDF with a non-empty but broken
    text layer only when its stored evidence yields no usable facts". `run_wave2`
    predates P6, so it has no verdict to give. `run_p1_p7` binds the real persisted
    predicate after its first fact pass.

    **This says nothing about OCR being unavailable.** `src/readers/` wires Apple
    Vision, and §2.2's OTHER route — *"A file with no text should route directly to
    OCR"* — needs no verdict at all: `ocr_policy.text_layer_state` asks P6 only about
    a NON-EMPTY text layer, because a document with no text has no stored evidence P6
    could have failed to make facts from. Scanned PDFs are read today; only the
    broken-text-layer route waits.

    An earlier version of this docstring said *"no OCR engine is wired"*, which was
    true when round 5 argued D5 and stopped being true when the readers landed. The
    historical D5 conclusion kept this legacy path cut, but the production caller now
    implements the required reordered passes. The second half of the old argument had
    expired, and a
    stale reason left in place is how a decision gets re-litigated from a premise
    nobody rechecked. **This function remains only for `run_wave2`.**

    Callers passed `lambda f, h: False` for this, and that is not the same statement.
    `False` from P6 means *"I examined this file's stored facts and the text layer is
    fine."* Every text-bearing PDF in a real corpus received that answer from a
    function that had examined nothing. The behaviour is right — no targeted OCR
    without P6 — and the claim was wrong, which is the same shape as an OCR path no
    real image could reach: a value that looks like a verdict and is an absence.

    §8.6's rule is that unfinished work stays visible as unfinished. This is that
    rule applied to a callable: the answer is still `False`, and now the call site
    says why. **When P6 lands this is deleted, not edited** — and note the ordering
    constraint it must be replaced under: P6's verdict is defined only after P6's
    deterministic pass for that content hash has completed, so wiring a real P6 into
    the single-loop caller runs targeted OCR over every text-bearing PDF. See
    `planning/22-p1-p7-connection-contract.md` §4.
    """
    return False


@dataclass(frozen=True)
class Wave2:
    """What one pass produced. Handles, not counts: the counts are P2's."""
    scan_run_id: str
    bundle_id: str
    run_ids: tuple[str, ...]


@dataclass(frozen=True)
class FileFactResults:
    """P6 results attributed to the exact immutable file version they describe."""
    file_id: str
    content_hash: str
    results: tuple[Any, ...]


@dataclass(frozen=True)
class P1P7Run:
    """Handles returned by one live P1-through-P7 assembly."""
    scan_run_id: str
    bundle_id: str
    run_ids: tuple[str, ...]
    fact_results: tuple[tuple[Any, ...], ...]
    fact_results_by_file: tuple[FileFactResults, ...] = ()


FactPass = Callable[[sqlite3.Connection, str, str], Any]
ClassificationProducer = Callable[
    [sqlite3.Connection, str, str], ClassificationRecord | None]


def get_file(conn: sqlite3.Connection, file_id: str) -> dict:
    """P1's row as a plain mapping.

    `sqlite3.Row` supports indexing and not `.get`, and P5's constructors ask a row
    for optional fields -- `dataless_result` checks `file_row.get("file_id")` before
    it will build a run at all. Converting once here beats every extractor learning
    which row type it was handed, and it is the same reason the readers are injected:
    P5 should not know where its `file_row` came from.
    """
    return dict(_get_file_row(conn, file_id))


def _extraction_is_stale(conn: sqlite3.Connection, content_hash: str,
                        versions: Mapping[str, str]) -> bool:
    """Has any extractor that already ran on this content been upgraded since?

    §3.4 puts the extractor version in the cache key so that "stale results" do not
    survive and "model or prompt changes" stay auditable. §1.2's stat-cache verdict
    keys on path, mtime and size and holds no version, so REUSE alone would mean a bug
    shipped in `pdf.text 0.1.0` stays in the database for the life of the corpus --
    two caches, and the outer one wins.

    An extractor with no published version -- OCR, whose version is the provider's --
    is never called stale here. Guessing would be worse than the gap.
    """
    for run in runs_for_content(conn, content_hash):
        current = versions.get(run.extractor_name)
        if current is not None and current != run.extractor_version:
            return True
    return False


def _already_extracted(conn: sqlite3.Connection, content_hash: str,
                       extractor_name: str | None) -> bool:
    """Does this content already have the run the router says it is owed?

    Not "does it have any run": `extract_filesystem` writes one for every file
    before the routed extractor is called, so a run killed between the two leaves
    a file with a filesystem record and no reading of its contents. Asking for the
    NAMED extractor is what makes that file resumable rather than permanently
    half-done.

    A file the router names no extractor for is owed nothing further -- §2.4's
    `unsupported` is its terminal answer -- so any run at all settles it, and the
    filesystem record is the one it will have.

    **A `deferred` RUN DOES NOT SETTLE ANYTHING, and `104` §18.2 gap 22 is why.**
    A deferral is the record that the work did NOT happen: P4 lists `deferred` in
    `ZERO_OBSERVATION_COMPLETENESS`, and §8.6's whole purpose is that "unfinished
    work must stay visible AS unfinished". Counting one as the run this file is
    owed would make a scan's own budget a permanent verdict -- the file would be
    `reused` on every later scan, including the one with the ceiling raised or
    removed, and nobody would ever be told why their images were never read. So a
    ceiling costs a file this scan and never the next one.
    """
    runs = runs_for_content(conn, content_hash)
    settled = [run for run in runs
               if run.completeness != DEFERRED_COMPLETENESS]
    if extractor_name is None:
        return bool(settled)
    return any(run.extractor_name == extractor_name for run in settled)


def _has_successful_ocr_coverage(
        conn: sqlite3.Connection, *, file_id: str, content_hash: str) -> bool:
    """Whether this exact file version already has completed OCR evidence.

    This is a coverage membership test, not an authoritative-result selector: no
    run is chosen and chronology is irrelevant. Any exact-hash OCR run completed
    without failure means P6's first pass must include OCR and OCR must not rerun.

    A run §8.6's budget DEFERRED is not coverage and is excluded: it has no
    observations by construction, so "OCR evidence exists for this file version"
    would be false, and the word this function's own name uses is `successful`.
    """
    return any(
        run.content_hash == content_hash
        and run.analysis_tier == ocr.ANALYSIS_TIER
        and run.finished_at is not None
        and run.failure_reason is None
        and run.completeness != DEFERRED_COMPLETENESS
        for run in runs_for_file(conn, file_id))


def _write(sink, result, written: list[str]) -> str:
    run_id = sink.write(result)
    written.append(run_id)
    return run_id


def _targeted(outcome) -> tuple:
    """The targeted OCR pass's results, with its three refusals raised again.

    **THE OLD BEHAVIOUR, PRESERVED EXACTLY.** Before R-138 this pass ran on the
    calling thread with nothing catching it, so a `ProtectedContainerRefused`, a
    `DatalessRefused` or a `ContractViolation` from inside it propagated out of
    `run_p1_p7` and ended the run. A pool cannot raise across a process boundary and
    names the outcome instead, so the raise has to be put back here -- and putting
    back something weaker would be a silent change to what a run does about a
    protected path, decided by where the work happens rather than by anybody.

    `_consume` above answers the same three kinds differently, and the difference is
    not an inconsistency: that loop is P5's FIRST pass, where §2.4 gives a refused
    file a `dataless` run or no run at all. This is the optional second pass over a
    file that already has its native run, and it had no such contract.
    """
    if outcome.kind == PROTECTED:
        raise ProtectedContainerRefused(outcome.message)
    if outcome.kind == DATALESS:
        raise DatalessRefused(outcome.message)
    if outcome.kind == CONTRACT:
        raise ContractViolation(outcome.message)
    return tuple(outcome.dispatched.results) if outcome.dispatched else ()


def _landed(result: ExtractionResult, when: str) -> ExtractionResult:
    """The same run, with `finished_at` taken when its result reached this thread.

    **Every extraction run in this product recorded a duration of exactly zero.**
    The loop below takes ONE stamp per file, on the calling thread, BEFORE the file
    is read, and hands that one string to the extractor as `now`; all eleven
    extractors then write `started_at=now, finished_at=now`. `database_agent/db.py`
    says of that pair, in a comment on the column, "(mechanics) so elapsed_time is
    computable" -- and it was not computable, for any file, in any run ever made.
    `00`:245-259 wants elapsed time observable, and the consequence of it not being
    is concrete: a 5,000-file scale run could say the run was slow and could not say
    which files made it so, because the only per-file timing anywhere was whatever a
    profiler attached to the whole process happened to attribute.

    **Here, and not in the worker.** `extraction_pool.perform` is where extraction
    genuinely ends, and stamping there would measure the read alone rather than the
    read plus its queueing -- but a spawned worker cannot be handed the caller's
    `now`, so the parallel path would take its stamp from a wall clock while the
    serial path took a test's frozen one, and the two would stop writing the same
    rows. `test_p1_p7_parallel.py` compares those two databases row for row, and
    that comparison is worth more than the queueing time it costs to keep.

    **Here, and not in each extractor.** Eleven extractors would then each hold a
    clock; the pair of stamps would be eleven decisions instead of one.

    So `started_at` keeps exactly the meaning it had -- the moment this loop decided
    to extract this file -- and `finished_at` is the moment its result was in hand.
    The difference is submission-to-landing, which is what a person waiting for a
    scan actually experiences, and it is honest about including queue time because
    the file really was outstanding for all of it.

    Only results that CROSSED the pool are re-stamped. `extract_filesystem` and
    `dataless_result` are built on this thread within microseconds of `stamp`; their
    equal pair is already true.
    """
    return replace(result, run={**result.run, "finished_at": when})


def _failed_version(decision, versions: Mapping[str, str]) -> str:
    """The version to stamp on a `failed` run: the EXTRACTOR's, never the router's.

    `decision.router_version` versions §2.9's routing table -- the thing that chose
    the handler. Stamping it on the run made the row say `pdf.text` ran at `0.2.0`
    when `pdf.text` has only ever been at `0.1.0`: one value with two computations,
    and the false one lands in §3.4's cache key and conformance rule 8's replay key.
    A replay would then look for a version that never existed.

    A name P5 cannot version is a router/dispatcher drift -- `UnknownFamily`'s
    territory -- and is raised rather than papered over with the router's number.
    """
    version = versions.get(decision.extractor_name)
    if version is None:
        raise ContractViolation(
            f"the router named {decision.extractor_name!r} and `current_versions()` "
            "has no entry for it, so this run cannot be honestly versioned. The two "
            "tables have drifted; §2.9's routing table is router.py's."
        )
    return version


def _assemble_bundle(
        conn: sqlite3.Connection, *, scan_run_id: str, roster: list[str],
        corpus_form: str, policy_settings: Mapping[str, Any],
        file_entry_body: Callable[[Mapping[str, Any]], Mapping[str, str]],
        handling_class_for: Callable[[Mapping[str, Any]], str | None] | None,
        expectations: Sequence[Mapping[str, Any]] = (),
        content: bool = True) -> str:
    """Build P2's immutable envelope from the current selected corpus.

    `expectations` is the hand-authored expected side of §8.5's assertions, applied
    BEFORE the seal because P2's SPEC §3 says a bundle is immutable once CREATED and
    lists `bundle_expectation[]` among its contents -- there is no lawful moment at
    which a created bundle lacks its labels and later gains them. Without this the
    only code that builds a real bundle sealed first, so P2 SPEC Done-means 1 -- a
    bundle built "with every field in §8.5's contents list present" -- could not be
    met by any real run, and `assert_run` over one could only ever write zero
    assertions.

    Nothing here authors a label: each mapping is passed verbatim to P2's own
    `add_expectation`, which owns the validation. P2 SPEC's Deferred table is
    explicit that "the corpus selection, the labelling, and the per-subject expected
    values are hand work. P2 publishes `bundle_expectation`; it does not fill it."
    Each mapping names its own `subject_ref`, so §8.7's scope discipline holds: this
    is a sequence of per-subject labels, never one label widened over many subjects.
    """
    bundle_id = open_bundle(
        conn, corpus_form=corpus_form, source_scan_ref=scan_run_id,
        pinned_plan_id=None, pinned_plan_version=None,
        policy_settings=dict(policy_settings))
    seen: set[tuple[str, str, str]] = set()
    for file_id in roster:
        file_row = get_file(conn, file_id)
        common = dict(
            file_id=file_id, content_hash=file_row["content_hash"],
            hash_algorithm=file_row["hash_algorithm"], **file_entry_body(file_row))
        if handling_class_for is None:
            # Keep the legacy caller's pre-P7 contract explicit and unchanged.
            add_file_entry(conn, bundle_id, handling_class=None, **common)
        else:
            _add_file_entry(
                conn, bundle_id, handling_class=handling_class_for(file_row),
                **common)
        for run in runs_for_file(conn, file_id):
            # A file_id is a convenience handle on P4 rows; P2's immutable bundle
            # entry is the exact (file_id, content_hash) version. Historical or
            # malformed same-file rows must not leak across that join. Keep every
            # extractor/version for the selected hash so cross-version diffs remain
            # possible; filter on identity, never chronology.
            if run.content_hash != file_row["content_hash"]:
                continue
            row = conn.execute(
                "SELECT * FROM extraction_runs WHERE run_id = ?", (run.run_id,)
            ).fetchone()
            add_extraction_run(conn, bundle_id, row=dict(row))
            if not content:
                # The manifest, the file entries and the runs are the audit half
                # and are cheap. What is skipped is the second copy of the text.
                continue
            for unit in text_units_for_run(conn, run.run_id):
                add_text_unit(conn, bundle_id, row=unit.to_mapping())
            for observation in observations_for_run(conn, run.run_id):
                key = (run.content_hash, run.extractor_version,
                       observation.observation_key)
                if key in seen:
                    continue
                seen.add(key)
                add_extraction_output(
                    conn, bundle_id, content_hash=run.content_hash,
                    extractor_version=run.extractor_version,
                    observation_key=observation.observation_key,
                    payload=canonical_json(observation.to_mapping()))
    for expectation in expectations:
        add_expectation(conn, bundle_id, **expectation)
    seal_bundle(conn, bundle_id)
    return bundle_id


def _extract_one(*, file_row, path, decision, policy, readers, now, context_window,
                 no_usable_facts, transcription_authorized, versions):
    """Every run this file's routing decision calls for, or the run its failure is.

    A reader that raises becomes one `failed` run rather than the end of the scan.
    §2.4's rule is that an unreadable file must never be "silently treated as an empty
    document", and a crashed scan is a worse version of the same lie: the file is not
    empty, it is unexamined. The exception is the signal -- there is no threshold here
    for "too corrupt" and no retry count.

    The two refusals from `admit()` are NOT caught here. They are the caller's, and
    they are the one place the two differ: see `run_wave2`.
    """
    try:
        dispatched = extract(
            file_row=file_row, decision=decision, path=path, policy=policy,
            readers=readers, now=now, context_window=context_window,
            no_usable_facts=no_usable_facts,
            transcription_authorized=transcription_authorized)
        return (dispatched.results, dispatched.sensitivity,
                dispatched.sensitivity_target)
    except (ProtectedContainerRefused, DatalessRefused, ContractViolation):
        # The refusals are the caller's to handle per 11 §4b/§5. A ContractViolation
        # is not about this file at all, so recording it as the file's failure would
        # be a false statement about the corpus AND would hide the defect it exists
        # to surface.
        raise
    except Exception as error:                       # noqa: BLE001 -- see docstring
        # No signals on a failed run -- there are no observations to index into --
        # so the target is 0 and names nothing, which `Dispatched.__post_init__`
        # only checks when signals are present.
        return (failed_result(
            file_row=file_row, error=error,
            extractor_name=decision.extractor_name,
            extractor_version=_failed_version(decision, versions),
            source_type=decision.source_type, now=now),), (), 0


def run_wave2(conn: sqlite3.Connection, selection_id: str, *,
              source, mime_type_for: Callable[[Path], str | None],
              scan_state: str, budget_exhausted: Callable[[], bool],
              detect_format: Callable[[Path], str | None],
              policy, readers, sink, now: Callable[[], str],
              context_window: int,
              no_usable_facts: Callable[[str, str], bool],
              transcription_authorized: Callable[[], bool],
              corpus_form: str, policy_settings: Mapping[str, Any],
              file_entry_body: Callable[[Mapping[str, Any]],
                                        Mapping[str, str]]) -> Wave2:
    """One scan, extracted, recorded and bundled.

    Every value passed on came from the part that owns it. `sink`, `policy`,
    `readers`, `detect_format`, `now`, `corpus_form` and `policy_settings` are
    caller-supplied; `scan_state` is P3's (SPEC Q4 is open) and `mime_type_for`
    answers P3's Q6. None is a value this module names.

    `file_entry_body` returns the kwargs for one `bundle_file_entry` -- either
    `{"payload_ref": ...}` for a snapshot bundle or `{"metadata_only": ...}` for a
    metadata-safe one. It is injected because WHERE a bundle keeps its payloads is
    the caller's, and because §8.4 requires the privacy gate to decide what a bundle
    may carry before anything is written into one. This legacy path predates P7 and
    therefore carries no class; `run_p1_p7` uses P7's authoritative current record.
    P2 enforces the exactly-one rule and the corpus_form
    match, so an inconsistent caller is refused there rather than half-written here.
    """
    # 1 -- P3. Full Disk Access is checked INSIDE scan(), before the run row exists
    #      (11 §1), so a refused scan leaves no partial corpus and no run to mistake
    #      for one.
    scan_run_id = scan(conn, selection_id, source=source,
                       mime_type_for=mime_type_for, scan_state=scan_state,
                       budget_exhausted=budget_exhausted)
    written: list[str] = []

    # 2 -- the roster. §1.2's stat cache: on REUSE, P5 is not invoked and prior
    #      results stand. That is resumption's work done without being called that.
    versions = current_versions()
    # The roster is every file THIS scan saw, collected before the skips below.
    # §8.5's envelope describes a corpus, and a REUSE file is in the corpus even
    # though this pass re-extracts nothing for it.
    roster: list[str] = []
    # 11 §5: "P3 detects a dataless / not-downloaded ubiquitous item before hashing
    # ... Do not materialize, hash, or extract." P3 made that observation during the
    # scan and P5's `SafetyPolicy.is_dataless` refuses the read -- two predicates for
    # one question, and this module is the only place that sees both. It wired
    # neither to the other, so a caller passing the usual `is_dataless=lambda p:
    # False` re-extracted an evicted file whose size had changed: P5's gate said
    # "local", P3's detection said "evicted", the native extractor opened it, and on
    # a real machine iCloud would have downloaded the file 11 §5 exists to protect.
    # P3's observation wins here because it is the one made BEFORE any read.
    evicted = {row["path"] for row in dataless_detections(conn, scan_run_id)}
    for verdict in cache_verdicts(conn, scan_run_id):
        if verdict["file_id"] is None:
            continue
        roster.append(verdict["file_id"])
        file_row = get_file(conn, verdict["file_id"])
        # `current_path`, not `path`. The live column is `current_path` and the
        # sketch on 18-wave2-orchestrator.md would KeyError on the first file.
        path = Path(file_row["current_path"])
        if str(path) in evicted:
            continue                      # 2b owns it, and owns it exactly once
        # Routed BEFORE the skip, because the skip now needs to know which
        # extractor this file is owed. `route` is a pure function over the row and
        # writes nothing, so asking early costs a dictionary lookup.
        decision = route(file_id=file_row["file_id"],
                         content_hash=file_row["content_hash"], path=path,
                         extension=file_row["extension"],
                         detect_format=detect_format)
        # A FILE THAT WAS NEVER EXTRACTED IS NOT A CACHED FILE, and that third
        # clause is Phase 4 (b)'s finding. §1.2's stat verdict keys on path, mtime
        # and size, and `_extraction_is_stale` only compares versions of runs that
        # EXIST -- with no run at all its loop body never executes and it answers
        # False. So a scan killed part way left every file it had indexed and not
        # yet reached looking exactly like a file already done, and no later run
        # ever read one: measured on a synthetic 200-file corpus, a run killed
        # after 83 writes left 158 files indexed with no extraction, and the next
        # run read ZERO of them. Resumption was resuming from the stat cache; it
        # now resumes from the records, which is what `00`:136-153 asks for.
        if (verdict["verdict"] != VERDICT_RECOMPUTE
                and not _extraction_is_stale(conn, file_row["content_hash"], versions)
                and _already_extracted(conn, file_row["content_hash"],
                                       decision.extractor_name)):
            continue
        stamp = now()
        try:
            results = [extract_filesystem(file_row=file_row, path=path, policy=policy,
                                          now=stamp, context_window=context_window)]
            routed, signals, signal_index = _extract_one(
                file_row=file_row, path=path, decision=decision, policy=policy,
                readers=readers, now=stamp, context_window=context_window,
                no_usable_facts=no_usable_facts,
                transcription_authorized=transcription_authorized,
                versions=versions)
            results.extend(routed)
            # The signals index into the ROUTED batch, never the indexer's. Compared
            # by identity because `results` is filesystem-first and the filesystem
            # run always has observations -- the filename is one -- so a "first
            # result with observations" test matched the wrong run every time.
            #
            # WHICH routed batch is `Dispatched.sensitivity_target`, which used to be
            # an unwritten `[0]`. E5 became a second emitter with a two-result branch
            # (CR-05b), so the batch is now named rather than assumed.
            signal_target = routed[signal_index] if routed else None
        except ProtectedContainerRefused:
            # 11 §4b, ratified 2026-08-20. NOTHING: no run row, no observation, no
            # status write for anything inside. `continue` the outer loop and never
            # `break` the inner one -- a `break` falls through to the status write
            # below, which is a P1 write authored "P5" against a file the product is
            # forbidden to have touched. P3's exclusion verdict on the CONTAINER,
            # reason `protected_container`, is the whole record, and P13 presents
            # those as their own inspectable list.
            continue
        except DatalessRefused as refusal:
            # 11 §5, and the asymmetry is not an inconsistency. Both refusals protect
            # a read; they differ in what the product is permitted to KNOW. Nothing
            # inside a protected container ever acquires a file_id or a content_hash,
            # so a run row there is unconstructible. A dataless file's identity is
            # already known, and §8.6 requires it to stay visible AS unfinished.
            results = [dataless_result(file_row=file_row, error=refusal,
                                       source_type=decision.source_type, now=stamp)]
            signals, signal_target = (), None

        # §2.9: "Every file leaves the router with exactly one routing decision."
        # The decision existed in memory for one loop iteration and was never stored,
        # so §8.2's reconstruction requirement could not be met for a routing choice.
        record_routing_decision(conn, decision)

        for result in results:
            run_id = _write(sink, result, written)
            # §2.9's "addresses and message content as potentially sensitive". E3
            # raises these per located value and they ride beside the batch, because
            # P4 rule 6 forbids an extractor-private column on an observation. The
            # caller kept only the runs, so on a real scan the signal never reached
            # the database and P7 would have had nothing to redact against. Keyed on
            # P4's handle, in emit order -- which is only trustworthy since
            # `observation_keys_for_run` stopped ordering by a uuid4 -- and only
            # correct at all since the target became the run that RAISED them.
            if signals and result is signal_target:
                record_sensitivity_signals(
                    conn, run_id=run_id, signals=signals,
                    observation_keys=observation_keys_for_run(conn, run_id),
                    now=stamp)
                signals = ()

        # 3 -- P1. The map is P5's; P1 stores it opaquely and interprets no key.
        set_extraction_status(
            conn, file_row["file_id"],
            status_by_tier=extraction_status_by_tier([r.run for r in results]),
            author=SUBSYSTEM, component_version=COMPONENT_VERSION)

    # 2b -- the evicted files. A file scanned while local and since moved to iCloud
    #       usually keeps its size and mtime, so its verdict is REUSE and the loop
    #       above skips it -- which is right for its CONTENT and wrong for its state.
    #       C4's ninth `completeness` value exists so §8.6's line can say "31 files
    #       are in iCloud", and it is reachable only from here. A file dataless at
    #       first sight has no `files` row (OQ3) and `dataless_result` refuses it.
    for detection in dataless_detections(conn, scan_run_id):
        row = conn.execute(
            "SELECT file_id FROM files WHERE current_path = ?",
            (detection["path"],)).fetchone()
        if row is None:
            continue
        file_row = get_file(conn, row["file_id"])
        decision = route(file_id=file_row["file_id"],
                         content_hash=file_row["content_hash"],
                         path=Path(file_row["current_path"]),
                         extension=file_row["extension"],
                         detect_format=detect_format)
        result = dataless_result(
            file_row=file_row,
            error=DatalessRefused(f"{detection['path']} is a dataless item"),
            source_type=decision.source_type, now=now())
        _write(sink, result, written)
        # Composed over what the file already had, not written on top of it. This
        # passed ONLY the dataless run, so a file that had
        # `{filesystem: complete, native: complete}` five seconds earlier became
        # `{native: dataless}` -- the finished filesystem tier erased, and §8.6's
        # progress line then reporting an extracted file as un-extracted. The merge
        # spells no tier: the newer run's statement about its OWN tier replaces the
        # older statement about that tier, and every other tier stands. Composing
        # over `runs_for_file` instead would hand `extraction_status_by_tier` this
        # file's earlier native run AND this dataless one -- two runs at one tier --
        # and P5 refuses to pick a winner there, correctly.
        set_extraction_status(
            conn, file_row["file_id"],
            status_by_tier={**json.loads(
                get_file(conn, file_row["file_id"])["extraction_status_by_tier"]
                or "{}"),
                **extraction_status_by_tier([result.run])},
            author=SUBSYSTEM, component_version=COMPONENT_VERSION)

    # 4 -- P2. Legacy Wave 2 intentionally predates P7 and therefore carries NULL.
    bundle_id = _assemble_bundle(
        conn, scan_run_id=scan_run_id, roster=roster, corpus_form=corpus_form,
        policy_settings=policy_settings, file_entry_body=file_entry_body,
        handling_class_for=None)

    return Wave2(scan_run_id=scan_run_id, bundle_id=bundle_id,
                 run_ids=tuple(written))


class _Submitted(NamedTuple):
    """One file, between the moment its extraction was asked for and the moment its
    rows are written.

    It carries `stamp` and `decision` because both were computed on the caller's
    thread BEFORE the request existed and both are wanted after it comes back -- and
    recomputing either on the way out would make a run's timestamps depend on how
    long a worker took. `refusal` is set only for a file `extract_filesystem` refused
    as dataless: it never became a request, and it still has to be written in roster
    order, so it waits in the same queue.
    """
    file_id: str
    file_row: Mapping[str, Any]
    decision: Any
    stamp: str
    filesystem: tuple
    handle: Any
    refusal: Exception | None


def run_p1_p7(
        conn: sqlite3.Connection, selection_id: str, *,
        source, mime_type_for: Callable[[Path], str | None], scan_state: str,
        budget_exhausted: Callable[[], bool],
        detect_format: Callable[[Path], str | None], policy, readers, sink,
        now: Callable[[], str], context_window: int,
        transcription_authorized: Callable[[], bool], corpus_form: str,
        policy_settings: Mapping[str, Any],
        file_entry_body: Callable[[Mapping[str, Any]], Mapping[str, str]],
        resolve_native: FactPass,
        targeted_ocr_needed: Callable[[str, str], bool],
        resolve_with_ocr: FactPass,
        classify: ClassificationProducer,
        classification_store: ClassificationStore,
        p7_component_version: str,
        pool,
        bundle_expectations: Sequence[Mapping[str, Any]] = (),
        bundle_content: bool = True) -> P1P7Run:
    """Run the live local pipeline without inventing any domain authority.

    The caller supplies both fact passes, the persisted targeted-OCR predicate and
    the P7 candidate producer. This function owns only their order. A REUSE file is
    resolved and classified from stored evidence. Targeted OCR may use either this
    invocation's native result or P4's sole exact current authoritative result;
    historical ambiguity is refused rather than resolved by guessing "latest".

    `pool` is WHERE `extract_initial` runs, and it has no default: a pool is chosen
    by the composition root or it is not chosen at all. `extraction_pool.ProcessPool`
    runs it in worker processes and is what every deployment builds since R-138, at
    every worker count, because a reader on the calling thread cannot be given a
    deadline; `InlinePool` runs it on this thread and is the serial shape the suite
    drives. Neither changes WHEN a row is written -- every database write stays here,
    on this thread, in roster order.

    **THE TARGETED OCR PASS IS UNDER IT TOO, and it is where r6 actually hung.**
    That pass used to run on this thread, after `pool.close()`, reaching the same
    Vision engine the pool exists to bound. Sampled at the hang, the run process's
    MAIN thread was inside `-[VNImageRequestHandler performRequests:]` through
    PyObjC, and the process held no Python-created thread at all -- no executor
    manager, no queue feeder -- so the pool had been built and closed and this was
    the only Vision call left here. `dispatch.targeted_ocr_wanted` now decides on
    this thread, where P6's persisted pass lives, and the reading is submitted;
    `pool.close()` therefore moved below the fact loop.
    """
    scan_run_id = scan(
        conn, selection_id, source=source, mime_type_for=mime_type_for,
        scan_state=scan_state, budget_exhausted=budget_exhausted)
    # The scan already resolved renames through `observe_path` and retired
    # gone paths. Point durable items at those rows. No second walk, no hash.
    # Absent item tables mean this connection never bootstrapped them.
    # Identity + profile mint only. Typing and the inferred connector need
    # extracted evidence and run later via `items.project.project_after_recognition`
    # (after the gist / recognition path in cli). Running them here typed files
    # from filenames alone and lied about the graph.
    from items.project import project_context_graph
    from scan_agent.selection import selection_sources
    project_context_graph(
        conn, selection_sources(conn, selection_id), scan_state,
        run_typing=False, run_connector=False)
    versions = current_versions()
    written: list[str] = []
    roster: list[str] = []
    # Fresh native results authorize directly; REUSE authority is resolved later by
    # P4's exact selector rather than put into this invocation-owned map.
    native_results: dict[str, tuple[Any, Any]] = {}
    initial_ocr_completed: set[str] = set()
    protected_refused: set[str] = set()
    reused: set[str] = set()
    evicted = {row["path"] for row in dataless_detections(conn, scan_run_id)}

    # --- §8.6's TWO PER-SCAN CEILINGS, and their one enforcement point ---------
    #
    # `104` §18.2 gap 22: "Two declared ceilings have no enforcement point and the
    # deferral rung is dead." `00`:243-258 declares `Maximum OCR time per scan` and
    # `Maximum image-analysis operations per scan`; P1 published the keys, P5 named
    # them in `extractors/budgets.py`, and nothing anywhere in `src/` obeyed either.
    # `cli.py` said so in a comment beside the two `set_ceiling` calls it does make.
    #
    # **HERE, BECAUSE HERE IS WHERE A SCAN EXISTS.** Both are per-SCAN totals. A
    # worker sees one file; an extractor sees one file; this loop is the only place
    # that sees all of them, and it is also where the text units are produced -- the
    # runs, the units and the observations are all written on this thread, in roster
    # order. So the running total lives here and the workers are handed the answer.
    #
    # **NEITHER VALUE IS CHOSEN HERE OR ANYWHERE ELSE IN `src/`.** `None` from P1
    # means no ceiling and the scan is unbounded, which is what every run this
    # product has ever made did and what every run still does until an owner stores
    # a number. `00`:243 calls these "configurable ceilings"; gap 22 is about the
    # enforcement point, not about the numbers.
    ceilings = p5_ceilings(conn)
    ocr_seconds_ceiling = ceilings["ocr.max_time_per_scan"]
    image_ops_ceiling = ceilings["image.max_analysis_ops_per_scan"]
    #: What the scan has spent, counted from what actually happened rather than
    #: estimated: OCR seconds measured around the engine call (`Dispatched.
    #: ocr_seconds`), image operations counted one per image extraction performed.
    #: `00`:248 names the unit "image-analysis operations" and §2.6 gives an image
    #: exactly one analysis, so one file analysed is one operation.
    ocr_seconds_spent = 0.0
    image_ops_spent = 0
    #: The files whose OCR a ceiling stopped. Deliberately NOT `initial_ocr_
    #: completed`: that set means "this file has real OCR evidence", it is what
    #: `_has_successful_ocr_coverage` and P6's second pass read, and a deferred run
    #: carries no observations at all (P4's `ZERO_OBSERVATION_COMPLETENESS` lists
    #: `deferred`). A deferred file is not covered and is not owed a retry inside
    #: the same scan either, so the targeted pass skips it rather than spending the
    #: ceiling it just refused.
    initial_ocr_deferred: set[str] = set()

    def _ocr_budget_spent() -> bool:
        return (ocr_seconds_ceiling is not None
                and ocr_seconds_spent >= ocr_seconds_ceiling)

    def _image_budget_spent() -> bool:
        return (image_ops_ceiling is not None
                and image_ops_spent >= image_ops_ceiling)

    def _consume(entry: _Submitted) -> None:
        """Write one file's extraction, in the order the roster asked for it.

        Everything here ran on THIS thread before `extraction_pool` existed and still
        does; what changed is only that `extract_initial` may have run somewhere else
        and finished at some other time. The write order is the SUBMISSION order,
        because §3.4's caching and §8.5's replay both need a stable one --
        `evidence_shape/store.py`'s `_ordered` exists because P4's `rowid` order
        reverses when the same runs are written in the opposite sequence.
        """
        file_id, file_row, decision, stamp, filesystem, handle, refusal = entry
        signals: Any = ()
        signal_target = None
        if refusal is not None:
            # `extract_filesystem` refused on this thread, before any request
            # existed. The filesystem result it did NOT return is discarded here for
            # the same reason the serial path discarded it: a dataless item's one run
            # is the `dataless` run.
            results = [dataless_result(file_row=file_row, error=refusal,
                                       source_type=decision.source_type, now=stamp)]
        elif handle is None:
            # NOTHING WAS SUBMITTED, and the whole batch is already in hand. This
            # is §8.6's per-scan image ceiling: the loop below built the deferred
            # run on this thread beside the filesystem one and queued the pair, so
            # that a deferred file is still written in ROSTER order among the files
            # that were read. A ceiling that reordered the database would make
            # §3.4's caching and §8.5's replay depend on how full a budget was.
            results = list(filesystem)
        else:
            outcome = pool.result(handle)
            if outcome.kind == PROTECTED:
                # Unreachable by construction -- `extract_filesystem` runs `admit()`
                # on this thread and a protected path is never submitted -- and kept
                # because "unreachable" is a claim about today's call order.
                protected_refused.add(file_id)
                return
            if outcome.kind == DATALESS:
                results = [dataless_result(
                    file_row=file_row, error=DatalessRefused(outcome.message),
                    source_type=decision.source_type, now=stamp)]
            elif outcome.kind == CONTRACT:
                raise ContractViolation(outcome.message)
            else:
                # THE SECOND STAMP, and the only one this loop takes after the work.
                # `stamp` was read before the file was submitted; this is read now
                # that its result is in hand, so `finished_at - started_at` is a real
                # number rather than zero. See `_landed`. Taken ONCE for the whole
                # batch a file produced, because a PDF's native run and its OCR run
                # landed together and pretending otherwise would invent an ordering
                # between them that nothing measured.
                landed = now()
                routed = [_landed(result, landed)
                          for result in outcome.dispatched.results]
                signals = outcome.dispatched.sensitivity
                signal_target = (routed[outcome.dispatched.sensitivity_target]
                                 if routed else None)
                results = list(filesystem) + routed
                # §8.6's OCR clock, charged with what the engine actually spent.
                # `nonlocal` because this closure is the only writer and the
                # submission loop below is the only reader.
                nonlocal ocr_seconds_spent, image_ops_spent
                ocr_seconds_spent += outcome.dispatched.ocr_seconds
                for result in routed:
                    tier = result.run["analysis_tier"]
                    completeness = result.run["completeness"]
                    if tier == pdf.ANALYSIS_TIER:
                        native_results[file_id] = (decision, result)
                    elif (tier == ocr.ANALYSIS_TIER
                          and result.run.get("finished_at") is not None
                          and result.run.get("failure_reason") is None):
                        # A DEFERRED OCR RUN IS NOT COVERAGE, and without this
                        # clause it would read as some: `deferred_result` stamps
                        # `finished_at` and carries no `failure_reason` -- both
                        # deliberately, because a deferral is not a failure -- so
                        # the two tests above pass for a run that read nothing.
                        # The file would then be marked OCR-complete, P6's second
                        # pass would be told OCR evidence exists, and the targeted
                        # retry would be skipped for a file that never ran.
                        if completeness == DEFERRED_COMPLETENESS:
                            initial_ocr_deferred.add(file_id)
                        else:
                            initial_ocr_completed.add(file_id)
                    if (result.run["extractor_name"] == image.EXTRACTOR_NAME
                            and completeness != DEFERRED_COMPLETENESS):
                        # `00`:248's unit, counted after the fact: an operation
                        # this scan actually performed. A deferred image run
                        # performed none and is not charged for one.
                        image_ops_spent += 1

        record_routing_decision(conn, decision)
        for result in results:
            run_id = _write(sink, result, written)
            if signals and result is signal_target:
                record_sensitivity_signals(
                    conn, run_id=run_id, signals=signals,
                    observation_keys=observation_keys_for_run(conn, run_id),
                    now=stamp)
                signals = ()
        set_extraction_status(
            conn, file_id,
            status_by_tier=extraction_status_by_tier([r.run for r in results]),
            author=SUBSYSTEM, component_version=COMPONENT_VERSION)

    window: deque[_Submitted] = deque()
    try:
        for verdict in cache_verdicts(conn, scan_run_id):
            file_id = verdict["file_id"]
            if file_id is None:
                continue
            roster.append(file_id)
            file_row = get_file(conn, file_id)
            path = Path(file_row["current_path"])
            if str(path) in evicted:
                continue
            # Routed BEFORE the skip, because the skip needs to know which
            # extractor this file is owed. `route` is pure over the row and writes
            # nothing, so asking early costs a dictionary lookup.
            decision = route(
                file_id=file_id, content_hash=file_row["content_hash"], path=path,
                extension=file_row["extension"], detect_format=detect_format)
            # A FILE THAT WAS NEVER EXTRACTED IS NOT A REUSED FILE, and the third
            # clause is Phase 4 (b)'s finding. §1.2's stat verdict keys on path,
            # mtime and size, and `_extraction_is_stale` only compares versions of
            # runs that EXIST -- with no run at all its loop body never executes
            # and it answers False. So a scan killed part way left every file it
            # had indexed and not yet reached looking exactly like a finished one,
            # and no later run read any of them. Measured on a synthetic 200-file
            # corpus: a run killed after 83 writes left 158 files indexed with no
            # extraction, and the next run read ZERO of them and counted all 158
            # as `reused`. Resumption was resuming from the stat cache; it now
            # resumes from the records, which is what `00`:136-153 asks for.
            if (verdict["verdict"] != VERDICT_RECOMPUTE
                    and not _extraction_is_stale(
                        conn, file_row["content_hash"], versions)
                    and _already_extracted(conn, file_row["content_hash"],
                                           decision.extractor_name)):
                reused.add(file_id)
                continue
            stamp = now()
            # `extract_filesystem` FIRST, and on this thread, because its first
            # statement is `admit()`. A path inside a protected container refuses
            # here and is therefore never submitted to anything: no worker is ever
            # handed it, which is a property of the call order rather than a check
            # somebody remembered to write. `stamp` is taken on this thread too, so
            # the timestamps stay in roster order however the work is distributed.
            try:
                filesystem = (extract_filesystem(
                    file_row=file_row, path=path, policy=policy, now=stamp,
                    context_window=context_window),)
            except ProtectedContainerRefused:
                protected_refused.add(file_id)
                continue
            except DatalessRefused as refusal:
                window.append(_Submitted(file_id, file_row, decision, stamp,
                                         (), None, refusal))
                continue
            if (decision.extractor_name == image.EXTRACTOR_NAME
                    and _image_budget_spent()):
                # §8.6's `image.max_analysis_ops_per_scan`, enforced BEFORE the
                # operation rather than after it -- which is what makes
                # `budgets.deferred_result` the right record: "the run for an
                # extractor the budget stopped before it started".
                #
                # DECIDED HERE AND NOT IN THE WORKER, unlike the OCR ceiling,
                # because this one can be: the router names `image.metadata`
                # before anything is submitted, so the operation is knowable in
                # advance. OCR is not -- whether a PDF runs OCR is decided inside
                # `extract_initial` by `direct_document_ocr_needed` -- which is
                # why that ceiling travels as a flag and this one does not.
                #
                # NOTHING ALREADY READ IS DELETED: `filesystem` was extracted on
                # this thread a few lines up and is written beside the deferral,
                # so the file stays indexed, named and citable. `00`:258: "the
                # product should retain extracted evidence, mark the deferred
                # stage, and leave the file or group in review rather than
                # guessing."
                window.append(_Submitted(
                    file_id, file_row, decision, stamp,
                    filesystem + (deferred_result(
                        file_row=file_row, source_type=image.SOURCE_TYPE,
                        extractor_name=image.EXTRACTOR_NAME,
                        extractor_version=image.VERSION,
                        analysis_tier=image.ANALYSIS_TIER,
                        # `extract_image`'s own coverage unit, so the deferred run
                        # and the run it replaces count the same thing.
                        units="images", total=1, now=stamp),),
                    None, None))
            else:
                window.append(_Submitted(
                    file_id, file_row, decision, stamp, filesystem,
                    pool.submit(ExtractionRequest(
                        file_id=file_id, file_row=dict(file_row),
                        decision=decision, path=path, now=stamp,
                        context_window=context_window, versions=versions,
                        # READ AT SUBMISSION, which is the latest this thread can
                        # answer for a file it is about to hand away. The window
                        # is bounded (`pool.lookahead`), so the total this is
                        # measured against lags by at most that many files -- an
                        # honest accumulate-as-you-go rather than a promise of
                        # exactness a parallel pool cannot keep.
                        ocr_budget_spent=_ocr_budget_spent())),
                    None))
            # A bounded look-ahead, not an unbounded one: a 5,760-file run holds a
            # handful of extraction batches in memory rather than all of them.
            while len(window) >= pool.lookahead:
                _consume(window.popleft())
        while window:
            _consume(window.popleft())
        # Preserve the dataless state transition even when P3's stat cache says REUSE.
        for detection in dataless_detections(conn, scan_run_id):
            row = conn.execute(
                "SELECT file_id FROM files WHERE current_path = ?", (detection["path"],)
            ).fetchone()
            if row is None:
                continue
            file_row = get_file(conn, row["file_id"])
            decision = route(
                file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                path=Path(file_row["current_path"]), extension=file_row["extension"],
                detect_format=detect_format)
            result = dataless_result(
                file_row=file_row,
                error=DatalessRefused(f"{detection['path']} is a dataless item"),
                source_type=decision.source_type, now=now())
            _write(sink, result, written)
            set_extraction_status(
                conn, file_row["file_id"],
                status_by_tier={**json.loads(
                    get_file(conn, file_row["file_id"])["extraction_status_by_tier"]
                    or "{}"), **extraction_status_by_tier([result.run])},
                author=SUBSYSTEM, component_version=COMPONENT_VERSION)

        fact_results: list[tuple[Any, ...]] = []
        fact_results_by_file: list[FileFactResults] = []
        for file_id in roster:
            if file_id in protected_refused:
                continue
            file_row = get_file(conn, file_id)
            content_hash = file_row["content_hash"]
            if (file_id in reused and _has_successful_ocr_coverage(
                    conn, file_id=file_id, content_hash=content_hash)):
                initial_ocr_completed.add(file_id)
            if file_id in initial_ocr_completed:
                per_file = [resolve_with_ocr(conn, file_id, content_hash)]
            else:
                per_file = [resolve_native(conn, file_id, content_hash)]

            native = native_results.get(file_id)
            if (native is None and file_id in reused
                    and file_id not in initial_ocr_completed):
                decision = route(
                    file_id=file_id, content_hash=content_hash,
                    path=Path(file_row["current_path"]),
                    extension=file_row["extension"], detect_format=detect_format)
                if decision.extractor_name == pdf.EXTRACTOR_NAME:
                    try:
                        persisted = authoritative_result(
                            conn, file_id=file_id, content_hash=content_hash,
                            extractor_name=pdf.EXTRACTOR_NAME,
                            extractor_version=versions[pdf.EXTRACTOR_NAME],
                            analysis_tier=pdf.ANALYSIS_TIER)
                    except AmbiguousAuthoritativeRun as error:
                        raise ContractViolation(
                            "targeted OCR cannot choose an authoritative persisted "
                            f"native run: {error}") from error
                    if persisted is not None:
                        native = (decision, persisted)
            targeted_completed = False
            targeted_results: tuple = ()
            # `initial_ocr_deferred` bars the retry for the reason its own comment
            # gives: this scan's OCR ceiling already refused this file once, and a
            # pass that ran anyway would spend past a budget the product had just
            # told the person it stopped at. It is a separate set from
            # `initial_ocr_completed` because the two mean opposite things --
            # covered, and refused for cost -- and folding them would tell P6 that
            # OCR evidence exists for a file that has none.
            if (native is not None and file_id not in initial_ocr_completed
                    and file_id not in initial_ocr_deferred):
                decision, native_result = native
                # THE DECISION HERE AND THE READING SOMEWHERE KILLABLE, which is
                # R-138 and the reason `extract_targeted_ocr` was split. This half
                # asks P6's persisted pass -- `targeted_ocr_needed` holds the
                # connection and cannot leave this thread -- and it is asked exactly
                # when it was asked before, so a deployment with no engine still
                # reaches the raise that `no_usable_facts` makes when §2.2's verdict
                # is consulted too early.
                #
                # `ocr_engine is not None` is tested AFTER the decision and not
                # before it, and the order is deliberate: `_ocr` returns None for a
                # deployment with no engine, so the pass produced no results either
                # way, and moving the test earlier would skip a question this loop
                # has always asked.
                if (targeted_ocr_wanted(
                        file_row=file_row, decision=decision,
                        native_result=native_result,
                        no_usable_facts=targeted_ocr_needed)
                        and readers.ocr_engine is not None):
                    # BOUNDED, and this is the call r6 hung inside. Sampled at the
                    # hang, the run process's MAIN thread was in
                    # `-[VNImageRequestHandler performRequests:]` through PyObjC with
                    # no Python thread alive anywhere in the process -- the executor
                    # had been built and closed, so this was the only Vision call
                    # left on the calling thread. One request, consumed immediately:
                    # the pass is per file and there is nothing to read ahead of.
                    targeted_outcome = pool.result(pool.submit(
                        TargetedOcrRequest(
                            file_id=file_id, file_row=dict(file_row),
                            path=Path(file_row["current_path"]), now=now(),
                            context_window=context_window,
                            # ASKED AGAIN, HERE. The initial loop may have spent
                            # the rest of §8.6's OCR clock after this file went
                            # through it, and this pass is the more expensive of
                            # the two.
                            ocr_budget_spent=_ocr_budget_spent())))
                    if targeted_outcome.dispatched is not None:
                        # The same clock the initial pass charges. A targeted read
                        # that spends four minutes has spent four minutes of the
                        # scan's OCR budget, whichever loop asked for it.
                        ocr_seconds_spent += targeted_outcome.dispatched.ocr_seconds
                    targeted_results = _targeted(targeted_outcome)
                for result in targeted_results:
                    _write(sink, result, written)
                    # A successful OCR run completes the second P6 pass even when its
                    # finder emits zero structured observations: the persisted OCR-tier
                    # pass is also the termination record. A failed OCR run is persisted
                    # but must not pretend that OCR evidence was successfully covered.
                    # ... and neither must a run a ceiling deferred, for the reason
                    # the initial loop's own clause gives: `deferred_result` stamps
                    # `finished_at` and carries no failure reason, so both tests
                    # below pass for a run that read nothing and P6 would be sent
                    # to resolve OCR evidence that does not exist.
                    targeted_completed = (
                        targeted_completed
                        or (result.run.get("finished_at") is not None
                            and result.run.get("failure_reason") is None
                            and result.run["completeness"]
                            != DEFERRED_COMPLETENESS))
                if targeted_results:
                    prior = json.loads(
                        get_file(conn, file_id)["extraction_status_by_tier"] or "{}")
                    set_extraction_status(
                        conn, file_id,
                        status_by_tier={**prior, **extraction_status_by_tier(
                            [result.run for result in targeted_results])},
                        author=SUBSYSTEM, component_version=COMPONENT_VERSION)
            if targeted_completed:
                per_file.append(resolve_with_ocr(conn, file_id, content_hash))
            per_file_results = tuple(per_file)
            fact_results.append(per_file_results)
            fact_results_by_file.append(FileFactResults(
                file_id=file_id, content_hash=content_hash,
                results=per_file_results))

            candidate = classify(conn, file_id, content_hash)
            if candidate is not None:
                if (candidate.file_id != file_id
                        or candidate.content_hash != content_hash):
                    raise ContractViolation(
                        "classifier candidate does not match the requested file version: "
                        f"requested {(file_id, content_hash)!r}, got "
                        f"{(candidate.file_id, candidate.content_hash)!r}")
                assign(
                    conn, candidate, store=classification_store,
                    component_version=p7_component_version)

    finally:
        # AFTER THE FACT LOOP AND NOT AFTER THE EXTRACTION LOOP, which is R-138.
        # `extract_targeted_ocr` is submitted above, so a pool closed at the end of
        # the extraction loop would be closed before the pass that needs it -- and
        # that pass reaches Vision, which is where r6 hung. The cost is that seven
        # workers stay alive, idle, through P4's resolution and P7's classification;
        # the alternative is a second pool built for one loop, which pays a second
        # round of interpreter starts to save memory this machine has.
        #
        # It still covers the way out through a `ContractViolation`: without
        # `cancel_futures` the raise would wait on every in-flight extraction
        # before surfacing.
        pool.close()
    # THE ENVELOPE ALWAYS; ITS BULK ONLY WHEN SOMETHING WILL READ IT.
    #
    # `bundle_manifest` is an AUDIT RECORD, not an optimisation: it carries
    # `policy_settings`, and `tests/test_cli_cloud_consent.py` calls it one of "the
    # two places a later reader can learn what this run was permitted to do". It is
    # one row. It is always written.
    #
    # `bundle_text_unit` and `bundle_extraction_output` are the bulk, and on an
    # ordinary run they are dead weight: measured on a real 413-file folder they
    # held 192,221 rows and 230 MB -- half a 466 MB database -- duplicating
    # `text_units` and `evidence` row for row. Only `evaluate_bundle` reads them,
    # and `run_production_p1_p7` calls it just when an evaluation is declared;
    # `--record` is the other consumer. A run that is neither built the whole copy
    # and never opened it, and could not have: `--replay` resolves a bundle by NAME
    # and only `--record` gives it one.
    bundle_id = _assemble_bundle(
        conn, scan_run_id=scan_run_id, roster=roster, corpus_form=corpus_form,
        policy_settings=policy_settings, file_entry_body=file_entry_body,
        handling_class_for=lambda row: resolve_class(classification_store.current(
            row["file_id"], row["content_hash"])),
        expectations=bundle_expectations, content=bundle_content)
    return P1P7Run(
        scan_run_id=scan_run_id, bundle_id=bundle_id,
        run_ids=tuple(written), fact_results=tuple(fact_results),
        fact_results_by_file=tuple(fact_results_by_file))
