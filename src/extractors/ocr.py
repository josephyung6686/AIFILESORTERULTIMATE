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


def extractor_name_for(provider: str) -> str:
    """Section 2.7's first persisted field, as P4's `extractor_name`."""
    return f"{EXTRACTOR_NAME_PREFIX}{provider}"


def extract_ocr(*, file_row: Mapping[str, Any], path: Path, policy: SafetyPolicy,
                ocr_engine: Callable[..., OcrOutput],
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
    name = extractor_name_for(output.provider)

    observations: list[Mapping[str, Any]] = []
    units: list[Mapping[str, Any]] = []

    for recognized in output.regions:
        container = ((segment("page", index=recognized.page),)
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

    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=name, extractor_version=output.provider_version,
                source_type=SOURCE_TYPE, analysis_tier=ANALYSIS_TIER,
                config=config,
                completeness="capped" if output.capped else "complete",
                coverage=coverage("pages", output.pages_processed,
                                  output.pages_total),
                observation_count=len(observations), started_at=now,
                finished_at=now),
        observations=tuple(observations),
        text_units=tuple(units),
    )
