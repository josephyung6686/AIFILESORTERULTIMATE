# src/extractors/dispatch.py
"""One entry point per file: `extract(file_row, decision, ...)`. SPEC Open question 2.

18-wave2-orchestrator.md closes OQ2 as "One P5 `extract(file_row, decision, …)` that
may return two runs (E5+E6). Orchestrator does not dispatch by name." The orchestrator
owns ORDER; routing is §2.9's and lives in `router.py`. A caller that switched on
`extractor_name` itself would be a second copy of the routing table living outside P5,
which is how one concept ends up with two homes.

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

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors.archive import extract_archive
from extractors.docx import extract_docx
from extractors.filesystem import unrouted_result
from extractors.image import extract_image
from extractors.long_tail import LONG_TAIL_SOURCE_TYPES, extract_long_tail
from extractors.ocr import extract_ocr
from extractors.ocr_policy import document_ocr_decision, image_ocr_decision
from extractors.pdf import extract_pdf
from extractors.sink import ExtractionResult
from extractors.structured_text import (
    STRUCTURED_TEXT_SOURCE_TYPES, extract_structured_text,
)
from extractors import archive, docx, filesystem, image, pdf, structured_text


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


def _ocr(*, file_row, path, policy, readers, now, context_window) -> ExtractionResult | None:
    if readers.ocr_engine is None:
        return None
    return extract_ocr(
        file_row=file_row, path=path, policy=policy, ocr_engine=readers.ocr_engine,
        config=dict(readers.ocr_config or {}),
        find_structured_strings=readers.find_structured_strings,
        now=now, context_window=context_window)


def extract(*, file_row: Mapping[str, Any], decision, path: Path, policy,
            readers: Readers, now: str, context_window: int,
            no_usable_facts: Callable[[str, str], bool],
            transcription_authorized: Callable[[], bool]) -> Dispatched:
    """Every run the router's decision calls for, in the order they were produced.

    A refusal from `admit()` -- `ProtectedContainerRefused` or `DatalessRefused` --
    propagates unchanged. The gate keeps one job (C4) and the catcher is the caller's:
    one of the two produces a `dataless` run and the other produces nothing at all,
    and that asymmetry is the orchestrator's contract, not this function's.
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
        # §2.2's three text-layer states, and B7: P5 wires the switch and never
        # invents the threshold. `no_usable_facts` is P6's verdict, injected.
        decision_ocr = document_ocr_decision(
            result=first, file_id=file_row["file_id"],
            content_hash=file_row["content_hash"], no_usable_facts=no_usable_facts)
        if decision_ocr.run_ocr:
            second = _ocr(readers=readers, **common)
            if second is not None:
                return Dispatched((first, second))
        return Dispatched((first,))

    if decision.extractor_name == docx.EXTRACTOR_NAME:
        # No OCR route. §2.2 names three text-layer states for PDFs and §2.3 names
        # none for DOCX; wiring one here would be P5 inventing a route.
        return Dispatched((extract_docx(
            read_docx=readers.read_docx,
            find_structured_strings=readers.find_structured_strings, **common),))

    if decision.extractor_name == archive.EXTRACTOR_NAME:
        return Dispatched((extract_archive(
            read_manifest=readers.read_manifest,
            recognize_markers=readers.recognize_markers, **common),))

    if decision.extractor_name == image.EXTRACTOR_NAME:
        first = extract_image(read_image=readers.read_image,
                              dimension_signal=readers.dimension_signal,
                              filename_pattern=readers.filename_pattern, **common)
        # §2.7's trigger: no usable text AND no usable metadata.
        if image_ocr_decision(result=first).run_ocr:
            second = _ocr(readers=readers, **common)
            if second is not None:
                return Dispatched((first, second))
        return Dispatched((first,))

    if decision.extractor_name == structured_text.EXTRACTOR_NAME:
        # The half-pick. By SOURCE TYPE, because both halves answer to this name.
        if source_type in LONG_TAIL_SOURCE_TYPES:
            produced = extract_long_tail(
                source_type=source_type, read_long_tail=readers.read_long_tail,
                find_structured_strings=readers.find_structured_strings,
                transcription_authorized=transcription_authorized, **common)
            return Dispatched((produced.extraction,), produced.sensitivity)
        if source_type in STRUCTURED_TEXT_SOURCE_TYPES:
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


class UnknownFamily(Exception):
    """The router named a handler nothing implements, or a family neither half of
    `text.structured` claims. Raised rather than swallowed: a silently skipped file is
    the one outcome §2.4 rules out absolutely."""


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
