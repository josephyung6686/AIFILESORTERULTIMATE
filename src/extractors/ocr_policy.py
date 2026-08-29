# src/extractors/ocr_policy.py
"""When OCR may run (sections 2.2 and 2.7). One signal, and no quality heuristic.

Section 2.2 requires the system to distinguish a PDF with NO text layer from one with
a BROKEN text layer:

    text_layer_absent   no text at all      route DIRECTLY to OCR
    text_layer_broken   text, but the stored evidence yields no usable facts
                                            TARGETED OCR, and only after P6 says so
    text_layer_usable   text and facts      no OCR

The state is not an observation and not a run field. "No text layer" is an ABSENCE,
and P4 is explicit that an extractor "may not write an 'EXIF absent', 'no text layer'
or 'metadata stripped' observation; the run record already says it, and an absence
written as evidence is a value P6 can rank." Section 2.2's requirement that the two be
DISTINGUISHED is met by the two paths behaving differently.

Section 2.2 forbids the alternative trigger outright: "The system should not use
unreliable global language-quality checks that incorrectly punish multilingual or
mathematics-heavy documents", and section 2.7 repeats it - not "because a broad
quality heuristic says the text looks unusual". So the only input about a non-empty
text layer is P6's `no_usable_facts` verdict (M11), injected with no default, and the
threshold behind that verdict is SPEC Open question 1 and is not answered here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from extractors.sink import ExtractionResult

#: Section 2.2's own three.
TEXT_LAYER_STATES: tuple[str, str, str] = (
    "text_layer_usable", "text_layer_absent", "text_layer_broken",
)


@dataclass(frozen=True)
class OcrDecision:
    """Whether E6 may run, and on what footing.

    `state` is section 2.2's text-layer state for a document and is None for an
    image, which has no text layer to have a state about.
    """
    state: str | None
    run_ocr: bool
    targeted: bool
    reason: str


def _has_text(result: ExtractionResult) -> bool:
    """Did this run store any text at all? Reads the run's own units, nothing else."""
    return any(unit["text"].strip() for unit in result.text_units)


def direct_document_ocr_needed(*, result: ExtractionResult) -> bool:
    """Whether a PDF must go directly to OCR before P6 can evaluate evidence.

    A non-empty text layer is deliberately left alone.  Whether its stored evidence
    yields usable facts is knowable only after P6 completes, through
    :func:`document_ocr_decision`.
    """
    return not _has_text(result)


#: §2.6's hierarchy, read at the level that decides. "Camera EXIF is strong photo
#: evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact
#: display resolutions, PNG format, and software metadata may support a screenshot
#: hypothesis." Tiers 1 and 2 are evidence ABOUT the image; tier 3 is what every
#: image has, which is why it appears in the design as support for the SCREENSHOT
#: hypothesis rather than against it.
USABLE_METADATA_TIERS: frozenset[int] = frozenset({1, 2})


def _has_metadata_observation(result: ExtractionResult) -> bool:
    """Did this run find metadata that says anything about the image?

    This counted ANY `zone=metadata` row, and §2.7's main path was dead as a result.
    E5 emits `format` and `pixel dimensions` for every image, both at `zone=metadata`,
    so an opaque PNG screenshot with no EXIF -- §2.7's own named example -- always had
    "usable metadata" and never reached OCR. Executed 2026-08-21: no real image could
    reach E6 at all. §2.7 opens by saying OCR "is the main way screenshots and opaque
    loose images become understandable to the pre-sorting engine", so that path being
    unreachable is not a small gap.

    §2.6's hierarchy is the fix and it is already on the record: M2 puts `signal_tier`
    on the observation precisely so it is "carried on the record and never re-derived
    downstream". Reading it here uses that hierarchy; it does not build a second one.

    A tier-3-only image is one the design says "may support a screenshot hypothesis",
    and §2.6 also warns the system "must not mistake the absence of EXIF for proof
    that an image is a screenshot" -- which is why the answer is to READ it, not to
    classify it. Running OCR on a photograph a messaging platform stripped is exactly
    right: nothing is being classified, the pixels are being read.
    """
    return any(o["location"]["zone"] == "metadata"
               and o.get("signal_tier") in USABLE_METADATA_TIERS
               for o in result.observations)


def text_layer_state(*, result: ExtractionResult, file_id: str, content_hash: str,
                     no_usable_facts: Callable[[str, str], bool]) -> str:
    """Section 2.2's state for a document run.

    P6 is asked ONLY about a non-empty text layer: a document with no text has no
    stored evidence P6 could have failed to make facts from, so its verdict there
    could not mean what it means in the broken case.
    """
    if not _has_text(result):
        return "text_layer_absent"
    if no_usable_facts(file_id, content_hash):
        return "text_layer_broken"
    return "text_layer_usable"


def document_ocr_decision(*, result: ExtractionResult, file_id: str,
                          content_hash: str,
                          no_usable_facts: Callable[[str, str], bool]) -> OcrDecision:
    """Section 2.2's OCR route for a document."""
    state = text_layer_state(result=result, file_id=file_id,
                             content_hash=content_hash,
                             no_usable_facts=no_usable_facts)
    if state == "text_layer_absent":
        return OcrDecision(state=state, run_ocr=True, targeted=False,
                           reason="no text layer; section 2.2 routes directly to OCR")
    if state == "text_layer_broken":
        return OcrDecision(
            state=state, run_ocr=True, targeted=True,
            reason=("P6 reported no usable facts from the stored evidence; "
                    "section 2.2 allows targeted OCR only on that verdict"))
    return OcrDecision(state=state, run_ocr=False, targeted=False,
                       reason="the text layer produced usable facts")


def image_ocr_decision(*, result: ExtractionResult) -> OcrDecision:
    """Section 2.7's trigger for an image: "when a file yields no usable text AND no
    usable metadata, including scanned PDFs, confirmed screenshots, and opaque images
    without EXIF."

    Reading an absence to make a routing decision is allowed; WRITING one as an
    observation is not (M2), and nothing here writes anything.
    """
    if _has_text(result) or _has_metadata_observation(result):
        return OcrDecision(state=None, run_ocr=False, targeted=False,
                           reason="the file yielded usable text or usable metadata")
    return OcrDecision(
        state=None, run_ocr=True, targeted=False,
        reason=("no usable text and no usable metadata (section 2.7); an opaque "
                "image is how a screenshot becomes understandable at all"))
