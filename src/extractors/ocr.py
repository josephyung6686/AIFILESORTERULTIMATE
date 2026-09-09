# src/extractors/ocr.py
"""E6 - OCR (section 2.7).

"OCR is not merely a rescue tool for scanned PDFs. It is the main way screenshots and
opaque loose images become understandable to the pre-sorting engine."

WHEN it runs is ocr_policy.py's (section 2.2's three text-layer states and section
2.7's no-usable-text-and-no-usable-metadata trigger). This module is the run.

Section 2.7's nine persisted fields all land on records P4 already publishes, which
is what closed P5 Open question 2. FIELD_HOMES is that mapping; there is no
OCR-specific record and nothing OCR-specific on an observation.

P5 spells no provider name. Section 2.7 names Apple Vision and S1 makes it the whole
of v1's scope, but section 2.7's first persisted field is that the provider reports
its own name and version, so `extractor_name` is built from what the engine returns.

P5 holds no number. Section 2.7's language list is Deferred and its "practical
rendering resolution such as 200 DPI" is an example; section 8.6's page cap and
run-time limits are configuration P1 owns (G4). The engine is given them and reports
that it stopped; nothing here decides to stop.
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors.failure import unsupported_result
from extractors.reading import StructuredString
from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import (
    context_for, location, normalize_mechanical, observation, run, segment, text_unit,
)
from extractors.sink import ExtractionResult

VERSION = "0.1.0"

#: `runs.analysis_tier_for` keys the `ocr` tier on this prefix rather than on a name,
#: so a second provider needs no edit there and P5 spells no provider.
EXTRACTOR_NAME_PREFIX = "ocr."
SOURCE_TYPE = "ocr"
ANALYSIS_TIER = "ocr"

#: The name an OCR run carries when the engine never reported its own -- because
#: it raised, or because it declined the format outright.
#:
#: `extractor_name_for` builds every real name from `output.provider`, and an
#: engine that crashed or returned `None` reports no provider, so there is none
#: to fold. This is the family with
#: the provider left off -- it cannot collide with any `ocr.<provider>` (no dot), it
#: is non-empty as P4 requires, and it invents neither a provider nor a provider
#: version. The run's `extractor_version` is `VERSION`, P5's OCR ADAPTER version:
#: that is the code which ran and failed. Section 2.7's first two persisted fields
#: are the provider's and stay genuinely unknown rather than being guessed.
#:
#: Whether this is the right spelling is a vocabulary question -- see NEEDS-JOSEPH.
UNREPORTED_PROVIDER_NAME = "ocr"

#: Section 2.7's own list: "the OCR provider and version, languages, configuration,
#: page or image reference, raw recognized text, locations or bounding boxes where
#: available, confidence information, and whether extraction was complete or capped."
PERSISTED_FIELDS: tuple[str, ...] = (
    "OCR provider", "version", "languages", "configuration",
    "page or image reference", "raw recognized text",
    "locations or bounding boxes", "confidence information",
    "complete or capped",
)

#: Where each of the nine lives (B1). Every one of them is a field P4 already
#: publishes: this is the mapping that closed P5 Open question 2, and it is here so a
#: test can walk it rather than a reviewer having to trust prose.
FIELD_HOMES: dict[str, str] = {
    "OCR provider": "extraction_runs.extractor_name",
    "version": "extraction_runs.extractor_version",
    "languages": "extraction_runs.config",
    "configuration": "extraction_runs.config_fingerprint",
    "page or image reference": "location.container_path",
    "raw recognized text": "text_units.text",
    "locations or bounding boxes": "location.region",
    "confidence information": "evidence.confidence",
    "complete or capped": "extraction_runs.completeness",
}


@dataclass(frozen=True)
class OcrRegion:
    """One recognized page or image region.

    `page` is section 2.7's "page or image reference" for a paged document and is
    None for a loose image, which has a region and no page. `box` is section 2.7's
    "locations or bounding boxes, where available" and lands on P4's
    `location.region`.
    """
    page: int | None
    region: int
    text: str
    box: Mapping[str, float] | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class OcrOutput:
    """What an injected `ocr_engine` returns.

    `capped` is section 2.7's partial-read state: the engine was given section 8.6's
    page cap and run-time limits and reports that it reached one.
    """
    provider: str
    provider_version: str
    regions: tuple[OcrRegion, ...] = ()
    pages_processed: int = 0
    pages_total: int = 0
    capped: bool = False


#: The characters a provider may spell a word break with. Folded to `_` so that one
#: engine has one name.
_WORD_BREAKS = (" ", "-", ".")


def extractor_name_for(provider: str) -> str:
    """Section 2.7's first persisted field, as P4's `extractor_name`.

    The provider reports its own name (section 2.7) and P5 spells none. What P5 does
    own is IDENTITY: `extractor_name` is an input to `observation_key`, to section
    3.4's cache key and to conformance rule 8's replay key, so an engine reporting
    `apple-vision` on one machine and `Apple Vision` on another would be two citation
    handles, two cache entries and two replay sets for one engine. That is the
    `config_fingerprint` break one layer up.

    Word breaks fold to `_` and case folds down. Nothing else is touched, so two
    genuinely different engines stay two names -- this collapses spellings, not
    providers.
    """
    token = provider.strip().casefold()
    for character in _WORD_BREAKS:
        token = token.replace(character, "_")
    return f"{EXTRACTOR_NAME_PREFIX}{token}"


def extract_ocr(*, file_row: Mapping[str, Any], path: Path, policy: SafetyPolicy,
                ocr_engine: Callable[..., OcrOutput | None],
                config: Mapping[str, Any],
                find_structured_strings: Callable[[str],
                                                  tuple[StructuredString, ...]],
                now: str, context_window: int) -> ExtractionResult:
    """Section 2.7's run, as P4 records.

    The recognized text is a `text_units` row per page or region (G1); the
    observations are the structured strings found in it, with spans that index into
    the unit their container path names.
    """
    admit(path, policy=policy)
    output = ocr_engine(path, config=config)
    if output is None:
        # §2.4's second outcome, at the seam every other extractor has had since it
        # was written and E6 did not. `extract_pdf`, `extract_docx`,
        # `extract_structured_text`, `extract_long_tail` and `extract_image` all read
        # `None` from their reader as "no reader exists for this format in this
        # deployment" and record `unsupported`. E6 had no such branch, so an engine
        # that could not decode a format had exactly one way to say so -- raise --
        # and the dispatcher's catch turned it into `failed`, which asserts the file
        # is DAMAGED.
        #
        # Measured on the owner's 199-file corpus, 2026-09-04: seven undamaged SVG
        # logos recorded `ocr · failed · "no image could be decoded from ..."`. The
        # bytes were fine; this deployment's image stack ships no vector decoder.
        # That is a statement about the deployment, and §8.6's "18 files remain
        # unreadable" sentence is computed straight off this column.
        #
        # The name is the family with the provider left off: an engine that declined
        # reported no provider and no provider version (§2.7's first two persisted
        # fields), and neither is invented. The VERSION is P5's own OCR adapter
        # version, which is the code that actually ran -- the same pairing
        # `dispatch._ocr` already uses for an engine that raised.
        return unsupported_result(
            file_row=file_row, extractor_name=UNREPORTED_PROVIDER_NAME,
            extractor_version=VERSION, source_type=SOURCE_TYPE,
            analysis_tier=ANALYSIS_TIER, now=now)
    name = extractor_name_for(output.provider)

    observations: list[Mapping[str, Any]] = []
    units: list[Mapping[str, Any]] = []

    for recognized in output.regions:
        # PAGE AND REGION, because a page is not an address on its own. Apple
        # Vision returns one region per line of text, so every region of page 1
        # was addressed `page[1]`, three text units were stored under one name,
        # and each observation's span -- which indexes into "the unit their
        # container path names", this function's own promise -- resolved against
        # whichever unit happened to be stored last.
        #
        # It did not misfile anything. `validate_run` caught it and raised
        # `NonConforming`, so ONE scanned page failed the entire corpus run. It
        # went unseen because every fixture used `region=1`: one region per page
        # is the single shape that cannot expose it, and no real scan has it.
        #
        # `SEGMENT_KINDS` has carried `region` all along and D3's own example is a
        # multi-segment address (`sheet=2/row=7/column=3`), so this is the shape
        # the design already describes. A loose image keeps its bare `region`: it
        # has no page, and inventing `page[1]` for a screenshot would make it
        # indistinguishable from a one-page scan.
        container = ((segment("page", index=recognized.page),
                      segment("region", index=recognized.region))
                     if recognized.page is not None
                     else (segment("region", index=recognized.region),))
        units.append(text_unit(text=recognized.text, container_path=container))
        for found in find_structured_strings(recognized.text):
            raw = recognized.text[found.start:found.end]
            before, after, truncated = context_for(recognized.text, found.start,
                                                   found.end, window=context_window)
            observations.append(observation(
                file_id=file_row["file_id"],
                content_hash=file_row["content_hash"],
                extractor_name=name, extractor_version=output.provider_version,
                source_type=SOURCE_TYPE, raw_value=raw,
                normalized_value=normalize_mechanical(raw),
                location=location(zone="ocr", container_path=container,
                                  text_span={"start": found.start,
                                             "end": found.end},
                                  region=recognized.box),
                context_before=before, context_after=after,
                context_truncated=truncated, observed_at=now,
                reliability="possible", confidence=recognized.confidence,
            ))

    # §2.4's prose-as-evidence, which was built in E3, then in E1 and E2, and never
    # here. Measured over the owner's 199-file corpus on 2026-09-04: OCR ran on 52
    # files and wrote 2,192 text units for one PDF alone against 17 observations, and
    # eleven IMAGE files -- regression-line charts, WhatsApp saves, screen captures --
    # carried 14 to 27 recognised units each and emitted ZERO evidence. §2.7 opens
    # "OCR is not merely a rescue tool for scanned PDFs. It is the main way
    # screenshots and opaque loose images become understandable to the pre-sorting
    # engine", and the engine reads OBSERVATIONS: `recognition/detector.py` scans
    # evidence only, on purpose, because "a detector that pulled whole text units
    # would be a second materialisation locus". So the words Apple Vision read off
    # the pixels were stored and unreachable, and the file was then filed as though
    # nothing had been read.
    #
    # ONE PASSAGE FOR THE WHOLE FILE, not one per region, and that is the difference
    # from E1. `pdf.py` emits per PAGE because a page is what §2.2's ranking argument
    # is about. Apple Vision returns ONE REGION PER LINE -- the comment above says so
    # and `test_each_region_on_a_page_is_separately_addressable` pins it -- so a row
    # per region would give the recogniser twenty one-line strings in which a term
    # like `vaccination record` is never adjacent to itself. This is E2's shape, for
    # E2's reason.
    #
    # NO CONTAINER AND NO SPAN, both load-bearing, and `docx.py` sets them out at
    # length. No container because P4 rule 10 anchors a span-carrying observation to a
    # unit at exactly its path and this passage is a unit at no path. No span because
    # an excerpt P7 can locate is an excerpt P7 can release.
    #
    # ZONE `ocr`, AND THAT IS THE SECURITY-BEARING LINE. §8.4 member 3 is
    # `ocr_output` and it never leaves the device;
    # `privacy.vocabulary.ALWAYS_LOCAL_ZONES` gained `"ocr"` on 2026-09-04 and every
    # release door reads it -- `privacy/items.py` refuses to construct an excerpt
    # addressing one, `model_facts.py` and `model_placement.py` both check before
    # sending. Emitting this as `body`, which is what E1 and E2 use for their own
    # prose, would put a scanned identity document into a cloud dossier through a
    # door that was already shut. The whole point of this row is to be READ BY THE
    # RECOGNISER ON THIS DEVICE, and `ocr` is the zone that says exactly that.
    #
    # NO CONFIDENCE. Every region carries its own and P4 publishes the field, but a
    # confidence for the whole passage would be an aggregate of them -- a mean, a
    # minimum, a weighting -- and choosing which is a policy with a number in it. P5
    # holds no number (`test_p5_holds_no_dpi_no_language_and_no_confidence_threshold`).
    # The per-region rows above keep theirs.
    passage = "\n".join(recognized.text for recognized in output.regions)
    if passage.strip():
        # `104` R-171 (9 Sep 2026): THE PASSAGE'S OWN TEXT UNIT, at its own
        # container path, which is SF-1's docx shape (`extractors/docx.py`:
        # `units.append(text_unit(text=whole_body))`) and what this extractor
        # never wrote. Without it `resolve.materialise` reports no length for
        # the passage, `items.check_item`'s whole-document arm cannot bound it
        # at any ceiling, and `opening_reading_for` has nothing to cut an
        # opening from, so a scanned page longer than the ceiling reached the
        # model as nothing. It costs a second copy of the passage in
        # `text_units`, the price docx already pays for the same reason.
        units.append(text_unit(text=passage))
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=name, extractor_version=output.provider_version,
            source_type=SOURCE_TYPE, raw_value=passage,
            normalized_value=normalize_mechanical(passage),
            location=location(zone="ocr", container_path=(), text_span=None),
            context_before="", context_after="", context_truncated=False,
            observed_at=now, reliability="possible",
        ))

    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=name, extractor_version=output.provider_version,
                source_type=SOURCE_TYPE, analysis_tier=ANALYSIS_TIER,
                config={**config, "context_window": context_window},
                completeness="capped" if output.capped else "complete",
                coverage=coverage("pages", output.pages_processed,
                                  output.pages_total),
                observation_count=len(observations), started_at=now,
                finished_at=now),
        observations=tuple(observations),
        text_units=tuple(units),
    )
