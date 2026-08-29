# src/extractors/pdf.py
"""E1 - PDF extraction (section 2.2).

"For PDFs with usable text layers, the engine should extract the complete document
rather than only a first-page preview... Crucially, it must preserve WHERE each
important piece of evidence appears."

Three homes, one per kind of thing:
    metadata slots      -> observations, zone `title` for the title and `metadata`
                           for the rest, `field=<the format's own slot name>` (D7)
    complete text       -> text_units, one row per page (G1)
    structured strings  -> observations, spans into the unit their container names

Section 2.2's metadata rule is carried by emitting the value VERBATIM and marking
nothing: "a value such as python-docx, Mozilla/5.0, or a browser-generated producer
string should not be mistaken for meaningful content" is a DISCOUNT RULE, and M4 puts
it in P6, keyed on `zone = metadata` plus a list that is Deferred and is not here.

There is no global language-quality check in this module or anywhere else in P5:
section 2.2 forbids one because it "incorrectly punishes multilingual or
mathematics-heavy documents".
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors.reading import ZONE_BY_STRUCTURED_KIND, Region, StructuredString
from extractors.failure import unsupported_result
from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import (
    context_for, location, normalize_mechanical, observation, run, segment, text_unit,
)
from extractors.sink import ExtractionResult

VERSION = "0.1.0"
EXTRACTOR_NAME = "pdf.text"
SOURCE_TYPE = "text_document"
ANALYSIS_TIER = "native"

#: The one metadata slot that is its own zone. P4's zone table gives `title` as "the
#: document title", named at section 2.2 and section 3.2 ("the PDF title"). Every
#: other slot is `metadata`.
TITLE_SLOTS: tuple[str, ...] = ("Title",)


@dataclass(frozen=True)
class PdfPage:
    number: int                                  # 1-based (P4 D3)
    text: str
    regions: tuple[Region, ...] = ()


@dataclass(frozen=True)
class PdfDocument:
    """What an injected `read_pdf` returns.

    `metadata` maps the format's own slot names to their values, verbatim (P4 D7).
    `iso_dates` carries the ISO-8601 rendering of any slot the reader recognised as a
    structured date - P4 D8's fourth mechanical transform. The PDF date syntax is a
    format detail, so the library that knows it does the rendering, and P5 never
    parses a date out of free text (section 3.10).
    """
    metadata: Mapping[str, str]
    pages: tuple[PdfPage, ...]
    iso_dates: Mapping[str, str] = dataclass_field(default_factory=dict)


@dataclass(frozen=True)
class _Candidate:
    zone: str
    raw: str
    container_path: tuple
    span: dict | None
    unit_text: str | None
    reliability: str
    normalized: str | None


def _region_at(page: PdfPage, offset: int) -> Region | None:
    """The innermost region containing this offset, preferring an addressable one."""
    containing = [r for r in page.regions if r.start <= offset < r.end]
    if not containing:
        return None
    headings = [r for r in containing if r.zone == "heading"]
    return headings[0] if headings else containing[0]


def extract_pdf(*, file_row: Mapping[str, Any], path: Path, policy: SafetyPolicy,
                read_pdf: Callable[[Path], PdfDocument],
                find_structured_strings: Callable[[str], tuple[StructuredString, ...]],
                now: str, context_window: int) -> ExtractionResult:
    """Section 2.2's complete document, as P4 records.

    Document order, which P4 D10 says `location` addresses the first occurrence in:
    metadata slots sorted by slot name (metadata has no document order, and section
    3.4's caching and section 8.5's replay both require a STABLE one), then pages in
    page order, then within a page the reader's regions and the found strings by
    offset.
    """
    admit(path, policy=policy)
    document = read_pdf(path)
    if document is None:
        # §2.4: no reader for this format in this deployment. `unsupported`, never
        # `failed` -- the bytes were never looked at, so a `failed` run would report
        # a missing library as a corrupt file.
        return unsupported_result(
            file_row=file_row, extractor_name=EXTRACTOR_NAME,
            extractor_version=VERSION, source_type=SOURCE_TYPE,
            analysis_tier=ANALYSIS_TIER, now=now)


    candidates: list[_Candidate] = []
    units: list[Mapping[str, Any]] = []

    for slot in sorted(document.metadata):
        value = document.metadata[slot]
        if not value:
            continue                      # presence only; an absence is never a row
        candidates.append(_Candidate(
            zone="title" if slot in TITLE_SLOTS else "metadata",
            raw=value,
            container_path=(segment("field", label=slot),),
            span=None, unit_text=None, reliability="direct",
            normalized=document.iso_dates.get(slot) or normalize_mechanical(value),
        ))

    for page in document.pages:
        page_path = (segment("page", index=page.number),)
        units.append(text_unit(text=page.text, container_path=page_path))

        heading_paths: dict[int, tuple] = {}
        for region in page.regions:
            if region.zone != "heading":
                continue                  # `body` and `reference_list` are zones, not
                                          # addresses: P4 publishes no such segment kind
            heading_path = page_path + (segment("heading", index=region.ordinal,
                                                label=region.label),)
            heading_paths[region.start] = heading_path
            heading_text = page.text[region.start:region.end]
            units.append(text_unit(text=heading_text, container_path=heading_path))
            candidates.append(_Candidate(
                zone="heading", raw=heading_text, container_path=heading_path,
                span={"start": 0, "end": len(heading_text)}, unit_text=heading_text,
                reliability="possible", normalized=normalize_mechanical(heading_text),
            ))

        for found in find_structured_strings(page.text):
            region = _region_at(page, found.start)
            zone = ZONE_BY_STRUCTURED_KIND.get(
                found.kind, region.zone if region is not None else "body")
            if region is not None and region.zone == "heading":
                container = heading_paths[region.start]
                unit_text = page.text[region.start:region.end]
                start, end = found.start - region.start, found.end - region.start
            else:
                container = page_path
                unit_text = page.text
                start, end = found.start, found.end
            raw = unit_text[start:end]
            candidates.append(_Candidate(
                zone=zone, raw=raw, container_path=container,
                span={"start": start, "end": end}, unit_text=unit_text,
                reliability="possible", normalized=normalize_mechanical(raw),
            ))

    observations = _collapse(candidates, file_row=file_row, now=now,
                             context_window=context_window)
    pages = len(document.pages)
    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=SOURCE_TYPE, analysis_tier=ANALYSIS_TIER,
                config={"reader": "injected",
                        "context_window": context_window},
                completeness="complete", coverage=coverage("pages", pages, pages),
                observation_count=len(observations), started_at=now, finished_at=now),
        observations=observations,
        text_units=tuple(units),
    )


def _collapse(candidates, *, file_row: Mapping[str, Any], now: str,
              context_window: int) -> tuple[Mapping[str, Any], ...]:
    """P4 D10: one observation per (run, exact raw value, zone).

    "`occurrence_count` counts within that zone; `location` addresses the FIRST
    occurrence in document order." Collapsing is on EXACT raw match, because P4 makes
    no normalization judgement: `Columbia` and `columbia` are two observations, and
    cross-form aggregation is P6's (section 3.7).
    """
    first: dict[tuple[str, str], _Candidate] = {}
    counts: dict[tuple[str, str], int] = {}
    order: list[tuple[str, str]] = []
    for candidate in candidates:
        key = (candidate.zone, candidate.raw)
        if key not in first:
            first[key] = candidate
            counts[key] = 0
            order.append(key)
        counts[key] += 1

    observations = []
    for key in order:
        candidate = first[key]
        before = after = ""
        truncated = False
        if candidate.span is not None and candidate.unit_text is not None:
            before, after, truncated = context_for(
                candidate.unit_text, candidate.span["start"], candidate.span["end"],
                window=context_window)
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=SOURCE_TYPE, raw_value=candidate.raw,
            normalized_value=candidate.normalized,
            location=location(zone=candidate.zone,
                              container_path=candidate.container_path,
                              text_span=candidate.span),
            context_before=before, context_after=after, context_truncated=truncated,
            occurrence_count=counts[key], observed_at=now,
            reliability=candidate.reliability,
        ))
    return tuple(observations)
