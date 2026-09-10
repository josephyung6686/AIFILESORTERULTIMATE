# src/extractors/dispatch.py
"""P5 family dispatch through two ordered passes and one compatibility entry point.

`extract_initial(...)` performs the family extraction and any P5-owned direct OCR.
`extract_targeted_ocr(...)` is the separate PDF-only operation that may run after P6
has evaluated the stored native evidence. The original `extract(...)` remains the
backward-compatible composition of those operations.

18-wave2-orchestrator.md closes OQ2 by keeping dispatch inside P5: the orchestrator
owns ORDER; routing is §2.9's and lives in `router.py`. A caller that switched on
`extractor_name` itself would be a second copy of the routing table living outside
P5, which is how one concept ends up with two homes.

**The half-picking this exists to do.** The router labels eight source types
`text.structured`, and `structured_text.extract_structured_text` accepts two of them.
The other six -- spreadsheet, presentation, email, calendar, contacts, audio_video --
are §2.9's long-tail families, handled by `long_tail.py`, which deliberately shares
the `text.structured` extractor name because it is the same family's second half. The
name therefore cannot pick the half and the SOURCE TYPE must. Executed 2026-08-21:
without this, a real corpus raises `WrongFamily` on its first .xlsx, .pptx, .eml,
.ics or .vcf, and every unit test still passed because nothing dispatched.

**It reads nothing.** Every reader is injected through `Readers` and every ceiling and
predicate arrives from the caller. P5 opens no file here, names no format, spells no
source type and holds no threshold.

**It does not index.** `extract_filesystem` is not a routed family -- it is P3's row
made citable, and it runs for every file whether or not one was routed. The caller
runs the indexer; this dispatches what the ROUTER decided.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors import budgets
from extractors.archive import extract_archive
from extractors.docx import extract_docx
from extractors.failure import ContractViolation, failed_result
from extractors.filesystem import unrouted_result
from extractors.image import extract_image
from extractors.long_tail import LONG_TAIL_SOURCE_TYPES, extract_long_tail
from extractors.ocr import extract_ocr
from extractors.ocr_policy import (
    direct_document_ocr_needed, document_ocr_decision, image_ocr_decision,
)
from extractors.pdf import extract_pdf
from extractors.safety import DatalessRefused, ProtectedContainerRefused
from extractors.sink import ExtractionResult
from extractors.structured_text import (
    STRUCTURED_TEXT_SOURCE_TYPES, extract_structured_text,
)
from extractors import archive, docx, filesystem, image, ocr, pdf, structured_text


@dataclass(frozen=True)
class Readers:
    """Everything that touches a file, injected.

    §2.9 puts the MIME/signature mapping in the reader and the same reasoning applies
    to every library: `read_pdf`, `read_docx` and the rest are external, versioned and
    replaceable, and naming one here would bind P5 to it. `ocr_engine` may be None --
    a deployment without OCR is a deployment where §2.2's and §2.7's routes stop, not
    one where they crash.
    """
    read_pdf: Callable[[Path], Any]
    read_docx: Callable[[Path], Any]
    read_text_document: Callable[[Path], Any]
    read_long_tail: Callable[..., Any]
    read_manifest: Callable[[Path], Any]
    read_image: Callable[[Path], Any]
    find_structured_strings: Callable[[str], tuple]
    recognize_markers: Callable[[Any], Any]
    dimension_signal: Callable[[int, int], str | None]
    filename_pattern: Callable[[str], str | None]
    ocr_engine: Callable[..., Any] | None = None
    ocr_config: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class Dispatched:
    """Every run this file produced, and the signals raised while producing them.

    `sensitivity` is here because P4 conformance rule 6 forbids an extractor-private
    field on an observation and the signal is per located value, so it cannot ride on
    the run either -- `long_tail.LongTailResult` carries it for the same reason. A
    dispatcher that returned only runs would drop it silently, and §2.9's "treating
    addresses and message content as potentially sensitive" would stop at E3.
    """
    results: tuple[ExtractionResult, ...]
    sensitivity: tuple = ()
    #: WHICH of `results` the signals index into. Was implicit -- the caller keyed
    #: them to `results[0]` and nothing said so -- until CR-05b gave the image branch
    #: a second result: an image that also runs OCR returns two, and a signal raised
    #: on the image batch had no way to say which. Zero is what the caller already
    #: assumed, so nothing changes for E3; what changes is that it is now written
    #: down and checked.
    sensitivity_target: int = 0
    #: HOW LONG THE OCR ENGINE ACTUALLY RAN, in seconds, or 0.0 when it did not.
    #:
    #: §8.6's `ocr.max_time_per_scan` is a budget in seconds and something has to
    #: measure the seconds. It is measured HERE, around the engine call, and not
    #: read off the run's own `started_at`/`finished_at`: `orchestrator._landed`
    #: sets that pair to submission-to-landing and says so ("honest about
    #: including queue time because the file really was outstanding for all of
    #: it"), which is the right number for what a person waits and the wrong one
    #: for a budget -- seven workers make it about seven times the OCR that ran.
    #:
    #: It rides on `Dispatched` and NOT on the run, because P4's
    #: `extraction_runs` has the columns it has and a per-run seconds field would
    #: be P5 adding one. Nothing writes it to the database; the caller adds it to
    #: a scan-level total and forgets it, so two runs of one corpus still produce
    #: byte-identical rows (`test_p1_p7_parallel` compares them row for row).
    ocr_seconds: float = 0.0

    def __post_init__(self) -> None:
        """A signal indexes into ONE batch, so it may only ride with one.

        `SensitivitySignal.observation_index` is a position in the emitting
        extractor's observation list. If a `Dispatched` carried signals alongside two
        results there would be no way to say which batch the position counts in, and
        a caller would have to guess -- which is exactly the defect this invariant
        exists to prevent: the Wave-2 caller resolved E3's signals against the
        FILESYSTEM run's keys for a day, so §2.9's "addresses and message content as
        potentially sensitive" was recorded against a filename.

        E3 was the only emitter and returned exactly one result, so a bare "exactly
        one result" assertion held. E5 is the second emitter and does NOT: §2.7 runs
        OCR after an image with no usable metadata, and that branch returns two. So
        the invariant is now that the signals NAME their batch, which is the thing
        the old assertion was protecting by making the ambiguous case impossible.
        """
        if self.sensitivity and not 0 <= self.sensitivity_target < len(self.results):
            raise ValueError(
                f"{len(self.sensitivity)} sensitivity signals name result "
                f"{self.sensitivity_target} of {len(self.results)}; a signal's "
                "observation_index is a position in ONE batch and the batch it "
                "counts in has to exist")


def _ocr(*, file_row, path, policy, readers, now, context_window,
         budget_spent: bool, alongside: ExtractionResult | None
         ) -> tuple[ExtractionResult | None, float]:
    """The OCR run and the seconds it took; or the run its failure is; or the run
    the scan's OCR budget stopped before it started; or None when no engine is
    wired.

    The first three outcomes are different facts and only two of them existed. No
    engine is a DEPLOYMENT state, known before the call, and §2.2's and §2.7's routes
    simply stop -- no run, by design. An engine that RAISES is a runtime event, and
    letting it propagate from here discarded the finished native result that
    `extract()` was holding: a completed extraction thrown away because a second,
    optional pass failed. Executed 2026-08-21 against a `pages=()` PDF with a raising
    engine -- the database kept a `pdf.text failed` row and no native run at all, for
    a file whose native pass had already returned.

    The refusals and contract violations still propagate: they are not this file's
    failure.

    **`budget_spent` IS `104` §18.2 GAP 22, AND P5 STILL HOLDS NO THRESHOLD.** §8.6
    declares `ocr.max_time_per_scan` and until now nothing in `src/` obeyed it; the
    ceiling and the running total both live with the caller, which is the only place
    that can see a whole scan, and what arrives here is the answer rather than the
    question. So this module still "holds no number", exactly as its docstring says.

    A spent budget produces `budgets.deferred_result` -- P4's `completeness:
    deferred`, which §8.6 calls the mark for work a budget stopped -- and NOT a
    truncated read and NOT silence. `00`:258: *"If the budget is exhausted, the
    product should retain extracted evidence, mark the deferred stage, and leave the
    file or group in review rather than guessing."* The native result the caller
    already holds is untouched; only the second, optional pass is refused.

    `alongside` is the result OCR would have run beside, and it supplies the
    deferred run's coverage UNITS AND TOTAL rather than a unit invented here: a
    nine-page PDF's deferred OCR reads `0 of 9 pages` and an image's reads
    `0 of 1 images`, because those are the words those two extractors already use
    for the thing OCR would have processed. A total of the ceiling wearing a full
    count is exactly what `coverage`'s own docstring refuses.
    """
    if readers.ocr_engine is None:
        return None, 0.0
    if budget_spent:
        # `alongside is None` is the TARGETED pass, which by design carries no
        # prior result across the process boundary (`TargetedOcrRequest`: "it
        # carries no prior result and no version table, and both absences are the
        # point"). So nothing here knows the file's page count, and the coverage
        # says `0 of 0 pages` rather than guessing a total -- which is what
        # `runs.coverage` refuses in its own words: "a run may not claim more
        # progress than the work it was given."
        units, total = (("pages", 0) if alongside is None else
                        (alongside.run["coverage"]["units"],
                         alongside.run["coverage"]["total"]))
        return budgets.deferred_result(
            file_row=file_row, source_type=ocr.SOURCE_TYPE,
            extractor_name=ocr.UNREPORTED_PROVIDER_NAME,
            extractor_version=ocr.VERSION,
            analysis_tier=ocr.ANALYSIS_TIER,
            units=units, total=total, now=now), 0.0
    started = time.monotonic()
    try:
        return extract_ocr(
            file_row=file_row, path=path, policy=policy,
            ocr_engine=readers.ocr_engine,
            config=dict(readers.ocr_config or {}),
            find_structured_strings=readers.find_structured_strings,
            now=now, context_window=context_window), time.monotonic() - started
    except ContractViolation:
        raise
    except (ProtectedContainerRefused, DatalessRefused):
        raise
    except Exception as error:                       # noqa: BLE001 -- see docstring
        # THE SECONDS COUNT EVEN THOUGH THE RUN FAILED. An engine that spent four
        # minutes and then raised spent four minutes of the scan's OCR budget, and
        # a budget that only charged for successes would let a failing engine run
        # for ever.
        return failed_result(
            file_row=file_row, error=error,
            extractor_name=ocr.UNREPORTED_PROVIDER_NAME,
            extractor_version=ocr.VERSION,
            source_type=ocr.SOURCE_TYPE, now=now,
            analysis_tier=ocr.ANALYSIS_TIER), time.monotonic() - started


def extract_initial(*, file_row: Mapping[str, Any], decision, path: Path, policy,
                    readers: Readers, now: str, context_window: int,
                    transcription_authorized: Callable[[], bool],
                    ocr_budget_spent: bool = False) -> Dispatched:
    """Run P5 extraction that is knowable before P6 evaluates stored evidence.

    A refusal from `admit()` -- `ProtectedContainerRefused` or `DatalessRefused` --
    propagates unchanged. The gate keeps one job (C4) and the catcher is the caller's:
    one of the two produces a `dataless` run and the other produces nothing at all,
    and that asymmetry is the orchestrator's contract, not this function's.

    `ocr_budget_spent` is the caller's answer to §8.6's `ocr.max_time_per_scan` --
    see `_ocr`, which says why the question is asked there and not here, and why P5
    still holds no number. It DEFAULTS to False so that every existing caller,
    including every test in `tests/p5/`, means exactly what it meant before: a
    deployment that never mentions the ceiling is a deployment with no ceiling, and
    §8.6's own words are that a published number nothing obeys is worse than an
    absent one.
    """
    if decision.extractor_name is None:
        return Dispatched((unrouted_result(file_row=file_row, decision=decision,
                                           now=now),))

    common = dict(file_row=file_row, path=path, policy=policy, now=now,
                  context_window=context_window)
    source_type = decision.source_type

    if decision.extractor_name == pdf.EXTRACTOR_NAME:
        first = extract_pdf(read_pdf=readers.read_pdf,
                            find_structured_strings=readers.find_structured_strings,
                            **common)
        # `104` R-161: the format's own person-valued fields, signalled by the FIELD.
        # The signals index into the NATIVE batch, which is result 0 whether or not
        # OCR runs beside it -- the same naming CR-05b gave the image branch.
        signals = pdf.person_field_signals(first)
        # Before P6, only an absent text layer authorizes OCR. A non-empty layer is
        # persisted first so P6 can evaluate the evidence rather than a preview.
        if direct_document_ocr_needed(result=first):
            second, seconds = _ocr(readers=readers, budget_spent=ocr_budget_spent,
                                   alongside=first, **common)
            if second is not None:
                return Dispatched((first, second), signals, 0, seconds)
        return Dispatched((first,), signals, 0)

    if decision.extractor_name == docx.EXTRACTOR_NAME:
        # No OCR route. §2.2 names three text-layer states for PDFs and §2.3 names
        # none for DOCX; wiring one here would be P5 inventing a route.
        produced = extract_docx(
            read_docx=readers.read_docx,
            find_structured_strings=readers.find_structured_strings, **common)
        return Dispatched((produced,), docx.person_field_signals(produced), 0)

    if decision.extractor_name == archive.EXTRACTOR_NAME:
        return Dispatched((extract_archive(
            read_manifest=readers.read_manifest,
            recognize_markers=readers.recognize_markers, **common),))

    if decision.extractor_name == image.EXTRACTOR_NAME:
        produced = extract_image(read_image=readers.read_image,
                                 dimension_signal=readers.dimension_signal,
                                 filename_pattern=readers.filename_pattern, **common)
        first = produced.extraction
        # §2.7's trigger: no usable text AND no usable metadata.
        if image_ocr_decision(result=first).run_ocr:
            second, seconds = _ocr(readers=readers, budget_spent=ocr_budget_spent,
                                   alongside=first, **common)
            if second is not None:
                # The signals index into the IMAGE batch, which is result 0. An
                # image with no usable metadata rarely carries EXIF, so this pairing
                # is uncommon -- and dropping the signals here rather than naming
                # the batch is exactly how a GPS tag would go unmarked on the one
                # file that had both.
                return Dispatched((first, second), produced.sensitivity, 0, seconds)
        return Dispatched((first,), produced.sensitivity, 0)

    if decision.extractor_name == structured_text.EXTRACTOR_NAME:
        # The half-pick. By SOURCE TYPE, because both halves answer to this name.
        if source_type in LONG_TAIL_SOURCE_TYPES:
            produced = extract_long_tail(
                source_type=source_type, read_long_tail=readers.read_long_tail,
                find_structured_strings=readers.find_structured_strings,
                transcription_authorized=transcription_authorized, **common)
            return Dispatched((produced.extraction,), produced.sensitivity)
        if source_type in STRUCTURED_TEXT_SOURCE_TYPES:
            # NO `104` R-161 signal, and the absence is the finding rather than an
            # omission: this half emits exactly two metadata fields -- §2.4's
            # `language` and its four structural-indicator classes -- and neither
            # names a person. Signalling anything a plain text document says would
            # need a body-text detector, which the ruling explicitly does not cover.
            return Dispatched((extract_structured_text(
                source_type=source_type,
                read_text_document=readers.read_text_document,
                find_structured_strings=readers.find_structured_strings,
                **common),))
        raise UnknownFamily(
            f"the router routed {source_type!r} to {structured_text.EXTRACTOR_NAME!r} "
            "and neither half claims it. A family in neither set would otherwise fall "
            "through this dispatcher and produce no run at all, which §2.4 forbids "
            "more strongly than it forbids an error."
        )

    raise UnknownFamily(
        f"the router named {decision.extractor_name!r} and no extractor answers to "
        "it. The two tables have drifted; §2.9's routing table is router.py's."
    )


def targeted_ocr_wanted(
        *, file_row: Mapping[str, Any], decision,
        native_result: ExtractionResult,
        no_usable_facts: Callable[[str, str], bool]) -> bool:
    """Whether this file has earned a post-P6 OCR pass. Decides; reads nothing.

    **THE HALF THAT NEEDS THE DATABASE, SEPARATED FROM THE HALF THAT NEEDS THE
    FILE, and R-138 is why.** `no_usable_facts` is P6's persisted pass and holds a
    connection, so it cannot cross a process boundary; `_ocr` reaches Apple's Vision
    framework through PyObjC, where a dispatch deadlock is measured, so it must not
    run on a thread nothing can interrupt. Those two facts pull in opposite
    directions and the only way to satisfy both is to ask the question here, on the
    caller's thread, and do the work somewhere killable.

    It is a SPLIT and not a change: `extract_targeted_ocr` below is these two
    functions composed, with the signature it has always had, so every existing
    caller is untouched. P5 still decides -- the orchestrator asks and does not
    reason -- which is the rule this module's docstring states about routing and
    which a caller that inlined `document_ocr_decision` would break.
    """
    if decision.extractor_name != pdf.EXTRACTOR_NAME:
        return False

    run = native_result.run
    expected = {
        "file_id": file_row["file_id"],
        "content_hash": file_row["content_hash"],
        "extractor_name": pdf.EXTRACTOR_NAME,
        "analysis_tier": pdf.ANALYSIS_TIER,
    }
    mismatches = {name: (run.get(name), value) for name, value in expected.items()
                  if run.get(name) != value}
    if mismatches:
        raise ContractViolation(
            "targeted PDF OCR requires this file version's native pdf.text result; "
            f"mismatched fields: {mismatches}")

    return document_ocr_decision(
        result=native_result, file_id=file_row["file_id"],
        content_hash=file_row["content_hash"],
        no_usable_facts=no_usable_facts).targeted


def perform_targeted_ocr(*, file_row: Mapping[str, Any], path: Path, policy,
                         readers: Readers, now: str,
                         context_window: int,
                         ocr_budget_spent: bool = False) -> Dispatched:
    """The OCR pass `targeted_ocr_wanted` authorized. Reads; decides nothing.

    Every reason not to run is already spent by the time this is called, which is
    what lets it run in a worker process: it takes a path and the wiring, no
    connection and no prior result. `_ocr` keeps its own contract -- no engine is a
    deployment state and produces no run at all, and an engine that RAISES becomes
    the `failed` OCR run rather than the end of the file.
    """
    produced, seconds = _ocr(
        file_row=file_row, path=path, policy=policy, readers=readers, now=now,
        context_window=context_window, budget_spent=ocr_budget_spent,
        alongside=None)
    return (Dispatched((produced,), (), 0, seconds) if produced is not None
            else Dispatched(()))


def extract_targeted_ocr(
        *, file_row: Mapping[str, Any], decision, path: Path, policy,
        readers: Readers, now: str, context_window: int,
        native_result: ExtractionResult,
        no_usable_facts: Callable[[str, str], bool]) -> Dispatched:
    """Run at most one post-P6 OCR pass for a prior native PDF result.

    Other routed families have no targeted-document route and are a no-op. For a
    PDF, the supplied prior result is contract input: guessing when it belongs to a
    different file, family, or analysis tier would let unrelated evidence authorize
    OCR for this file version.

    The decision and the reading are separately callable above, because R-138 needs
    them on different threads. This composition is what `extract()` uses and what a
    caller with no pool still gets.
    """
    if not targeted_ocr_wanted(
            file_row=file_row, decision=decision, native_result=native_result,
            no_usable_facts=no_usable_facts):
        return Dispatched(())
    return perform_targeted_ocr(
        file_row=file_row, path=path, policy=policy, readers=readers, now=now,
        context_window=context_window)


def extract(*, file_row: Mapping[str, Any], decision, path: Path, policy,
            readers: Readers, now: str, context_window: int,
            no_usable_facts: Callable[[str, str], bool],
            transcription_authorized: Callable[[], bool]) -> Dispatched:
    """Backward-compatible composition of initial and post-P6 P5 passes."""
    initial = extract_initial(
        file_row=file_row, decision=decision, path=path, policy=policy,
        readers=readers, now=now, context_window=context_window,
        transcription_authorized=transcription_authorized)
    if (decision.extractor_name != pdf.EXTRACTOR_NAME
            or any(result.run["analysis_tier"] == ocr.ANALYSIS_TIER
                   for result in initial.results)):
        return initial
    targeted = extract_targeted_ocr(
        file_row=file_row, decision=decision, path=path, policy=policy,
        readers=readers, now=now, context_window=context_window,
        native_result=initial.results[0], no_usable_facts=no_usable_facts)
    return Dispatched(initial.results + targeted.results,
                      initial.sensitivity + targeted.sensitivity)


class UnknownFamily(ContractViolation):
    """The router named a handler nothing implements, or a family neither half of
    `text.structured` claims. Raised rather than swallowed: a silently skipped file is
    the one outcome §2.4 rules out absolutely.

    A `ContractViolation` because it is a statement about the CALL: §2.9's routing
    table and this dispatcher have drifted, which is a defect in P5 and not a fact
    about the bytes. As a plain `Exception` the caller's catch-all turned it into
    that FILE's `failed` run, with `failure_reason` reading like the file was
    corrupt -- filing a P5 defect under the corpus's name and hiding it in exactly
    the way `ContractViolation` was introduced to stop. Every routed file in a
    drifted deployment would have been recorded unreadable."""


def current_versions() -> dict[str, str]:
    """Every extractor this module can run, at the version it is at right now.

    §3.4's cache key is "content hash, extractor version, analysis tier, model
    identifier when relevant, and prompt fingerprint", and it exists so that a change
    "makes model or prompt changes auditable" and stale results do not survive. P3's
    §1.2 stat-cache verdict keys on path, mtime and size and carries no version at
    all -- so a caller that trusts the stat cache alone never re-runs an upgraded
    extractor over an unchanged corpus, and the stat cache is the OUTER one.

    Published here rather than assembled by the caller because this module is what
    decides which extractor runs; a second list somewhere else would go stale the
    first time a seventh extractor is added.

    **OCR is deliberately absent.** Its `extractor_name` is `ocr.` plus whatever the
    engine reports, and its version is the PROVIDER's (§2.7's first two persisted
    fields), so P5 cannot state it without asking an engine that may not be installed.
    A caller sees no entry and therefore never calls an OCR run stale, which is the
    honest answer rather than a guessed one.
    """
    return {
        pdf.EXTRACTOR_NAME: pdf.VERSION,
        docx.EXTRACTOR_NAME: docx.VERSION,
        archive.EXTRACTOR_NAME: archive.VERSION,
        image.EXTRACTOR_NAME: image.VERSION,
        # `long_tail` imports its name and version from `structured_text`: one family,
        # two halves, one version.
        structured_text.EXTRACTOR_NAME: structured_text.VERSION,
        filesystem.EXTRACTOR_NAME: filesystem.VERSION,
        filesystem.STOPPED_EXTRACTOR_NAME: filesystem.VERSION,
    }
