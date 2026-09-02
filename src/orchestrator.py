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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

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
from extractors import ocr, pdf
from extractors.dispatch import (
    current_versions, extract, extract_initial, extract_targeted_ocr,
)
from extractors.failure import ContractViolation, failed_result
from extractors.filesystem import dataless_result, extract_filesystem
from extractors.long_tail import record_sensitivity_signals
from extractors.router import record_routing_decision, route
from extractors.runs import extraction_status_by_tier
from extractors.safety import DatalessRefused, ProtectedContainerRefused

from scan_agent.dataless import dataless_detections
from scan_agent.scan import scan
from scan_agent.stat_cache import VERDICT_RECOMPUTE, cache_verdicts

from privacy.classification import ClassificationRecord, resolve_class
from privacy.classification_store import ClassificationStore
from privacy.learning_seam import assign

_add_file_entry = add_file_entry


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


def _has_successful_ocr_coverage(
        conn: sqlite3.Connection, *, file_id: str, content_hash: str) -> bool:
    """Whether this exact file version already has completed OCR evidence.

    This is a coverage membership test, not an authoritative-result selector: no
    run is chosen and chronology is irrelevant. Any exact-hash OCR run completed
    without failure means P6's first pass must include OCR and OCR must not rerun.
    """
    return any(
        run.content_hash == content_hash
        and run.analysis_tier == ocr.ANALYSIS_TIER
        and run.finished_at is not None
        and run.failure_reason is None
        for run in runs_for_file(conn, file_id))


def _write(sink, result, written: list[str]) -> str:
    run_id = sink.write(result)
    written.append(run_id)
    return run_id


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
        expectations: Sequence[Mapping[str, Any]] = ()) -> str:
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
        if verdict["verdict"] != VERDICT_RECOMPUTE and not _extraction_is_stale(
                conn, file_row["content_hash"], versions):
            continue
        decision = route(file_id=file_row["file_id"],
                         content_hash=file_row["content_hash"], path=path,
                         extension=file_row["extension"],
                         detect_format=detect_format)
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
        bundle_expectations: Sequence[Mapping[str, Any]] = ()) -> P1P7Run:
    """Run the live local pipeline without inventing any domain authority.

    The caller supplies both fact passes, the persisted targeted-OCR predicate and
    the P7 candidate producer. This function owns only their order. A REUSE file is
    resolved and classified from stored evidence. Targeted OCR may use either this
    invocation's native result or P4's sole exact current authoritative result;
    historical ambiguity is refused rather than resolved by guessing "latest".
    """
    scan_run_id = scan(
        conn, selection_id, source=source, mime_type_for=mime_type_for,
        scan_state=scan_state, budget_exhausted=budget_exhausted)
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

    for verdict in cache_verdicts(conn, scan_run_id):
        file_id = verdict["file_id"]
        if file_id is None:
            continue
        roster.append(file_id)
        file_row = get_file(conn, file_id)
        path = Path(file_row["current_path"])
        if str(path) in evicted:
            continue
        if verdict["verdict"] != VERDICT_RECOMPUTE and not _extraction_is_stale(
                conn, file_row["content_hash"], versions):
            reused.add(file_id)
            continue
        decision = route(
            file_id=file_id, content_hash=file_row["content_hash"], path=path,
            extension=file_row["extension"], detect_format=detect_format)
        stamp = now()
        try:
            results = [extract_filesystem(
                file_row=file_row, path=path, policy=policy, now=stamp,
                context_window=context_window)]
            try:
                dispatched = extract_initial(
                    file_row=file_row, decision=decision, path=path, policy=policy,
                    readers=readers, now=stamp, context_window=context_window,
                    transcription_authorized=transcription_authorized)
                routed = list(dispatched.results)
                signals = dispatched.sensitivity
                signal_index = dispatched.sensitivity_target
            except (ProtectedContainerRefused, DatalessRefused, ContractViolation):
                raise
            except Exception as error:                 # noqa: BLE001
                routed = [failed_result(
                    file_row=file_row, error=error,
                    extractor_name=decision.extractor_name,
                    extractor_version=_failed_version(decision, versions),
                    source_type=decision.source_type, now=stamp)]
                signals = ()
                signal_index = 0
            signal_target = routed[signal_index] if routed else None
            results.extend(routed)
            for result in routed:
                tier = result.run["analysis_tier"]
                if tier == pdf.ANALYSIS_TIER:
                    native_results[file_id] = (decision, result)
                elif (tier == ocr.ANALYSIS_TIER
                      and result.run.get("finished_at") is not None
                      and result.run.get("failure_reason") is None):
                    initial_ocr_completed.add(file_id)
        except ProtectedContainerRefused:
            protected_refused.add(file_id)
            continue
        except DatalessRefused as refusal:
            results = [dataless_result(
                file_row=file_row, error=refusal,
                source_type=decision.source_type, now=stamp)]
            signals, signal_target = (), None
        except ContractViolation:
            raise

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
        if native is not None and file_id not in initial_ocr_completed:
            decision, native_result = native
            targeted = extract_targeted_ocr(
                file_row=file_row, decision=decision,
                path=Path(file_row["current_path"]), policy=policy,
                readers=readers, now=now(), context_window=context_window,
                native_result=native_result,
                no_usable_facts=targeted_ocr_needed)
            for result in targeted.results:
                _write(sink, result, written)
                # A successful OCR run completes the second P6 pass even when its
                # finder emits zero structured observations: the persisted OCR-tier
                # pass is also the termination record. A failed OCR run is persisted
                # but must not pretend that OCR evidence was successfully covered.
                targeted_completed = (
                    targeted_completed
                    or (result.run.get("finished_at") is not None
                        and result.run.get("failure_reason") is None))
            if targeted.results:
                prior = json.loads(
                    get_file(conn, file_id)["extraction_status_by_tier"] or "{}")
                set_extraction_status(
                    conn, file_id,
                    status_by_tier={**prior, **extraction_status_by_tier(
                        [result.run for result in targeted.results])},
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

    bundle_id = _assemble_bundle(
        conn, scan_run_id=scan_run_id, roster=roster, corpus_form=corpus_form,
        policy_settings=policy_settings, file_entry_body=file_entry_body,
        handling_class_for=lambda row: resolve_class(classification_store.current(
            row["file_id"], row["content_hash"])),
        expectations=bundle_expectations)
    return P1P7Run(
        scan_run_id=scan_run_id, bundle_id=bundle_id,
        run_ids=tuple(written), fact_results=tuple(fact_results),
        fact_results_by_file=tuple(fact_results_by_file))
