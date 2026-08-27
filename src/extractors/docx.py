# src/extractors/docx.py
"""E2 - DOCX extraction (section 2.3).

"DOCX extraction should preserve the FULL SEMANTIC STRUCTURE of a document rather than
reading only its first few paragraphs... core properties, all paragraphs in order,
heading levels, tables and table-cell text, headers and footers where feasible,
hyperlinks, document relationships, and available revision or comment metadata."

Two requirements are load-bearing and shape everything here:

  Tables are mandatory. "Resumes, forms, applications, invoices, and administrative
  documents often place their most useful information in cells rather than body
  paragraphs." A cell locates as table=T/row=R/column=C (section 2.8's own example).

  Zones must stay distinct. "The extractor must preserve the difference between a
  heading, a table label, a filename, and ordinary body text, because those locations
  carry different evidentiary weight." Section 2.3's own case is `Wash U.docx`: an
  unhelpful filename and a decisive heading. Flatten the zone here and no later part
  can recover it.

Heading LEVEL is the container path's depth, not a new field: P4 has one `heading`
zone ("a heading at any level") and addresses `heading` by "ordinal within parent", so
an H2 under an H1 is heading=1/heading=2.
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors.reading import ZONE_BY_STRUCTURED_KIND, StructuredString
from extractors.failure import unsupported_result
from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import (
    context_for, location, normalize_mechanical, observation, run, segment, text_unit,
)
from extractors.sink import ExtractionResult

VERSION = "0.1.0"
EXTRACTOR_NAME = "docx.structure"
SOURCE_TYPE = "text_document"
ANALYSIS_TIER = "native"

#: The core property that is its own zone (P4: `title` is "the document title").
TITLE_PROPERTIES: tuple[str, ...] = ("title",)


@dataclass(frozen=True)
class DocxParagraph:
    """One paragraph, in order.

    `zone` is one of P4's: `heading`, `body` or `header_footer`. `heading_path` is the
    paragraph's heading ancestry as (ordinal, label) pairs, outermost first; for a
    heading paragraph its LAST element is that heading.
    """
    index: int
    text: str
    zone: str
    heading_path: tuple[tuple[int, str], ...] = ()


@dataclass(frozen=True)
class DocxCell:
    table: int
    row: int
    column: int
    text: str
    column_header: str | None = None


@dataclass(frozen=True)
class DocxLink:
    target: str
    paragraph: int | None = None


@dataclass(frozen=True)
class DocxAnnotation:
    """Section 2.3's "available revision or comment metadata"."""
    name: str
    text: str
    paragraph: int | None = None


@dataclass(frozen=True)
class DocxDocument:
    """What an injected `read_docx` returns."""
    core_properties: Mapping[str, str]
    paragraphs: tuple[DocxParagraph, ...] = ()
    cells: tuple[DocxCell, ...] = ()
    links: tuple[DocxLink, ...] = ()
    relationships: tuple[str, ...] = ()
    annotations: tuple[DocxAnnotation, ...] = ()
    iso_dates: Mapping[str, str] = dataclass_field(default_factory=dict)


def _heading_segments(paragraph: DocxParagraph) -> tuple:
    return tuple(segment("heading", index=ordinal, label=label)
                 for ordinal, label in paragraph.heading_path)


def _paragraph_path(paragraph: DocxParagraph) -> tuple:
    """A heading paragraph IS its innermost heading segment; anything else hangs off
    the heading ancestry as a `paragraph` segment (P4 names the kind at section 2.3)."""
    if paragraph.zone == "heading":
        return _heading_segments(paragraph)
    return _heading_segments(paragraph) + (segment("paragraph", index=paragraph.index),)


def extract_docx(*, file_row: Mapping[str, Any], path: Path, policy: SafetyPolicy,
                 read_docx: Callable[[Path], DocxDocument],
                 find_structured_strings: Callable[[str], tuple[StructuredString, ...]],
                 now: str, context_window: int) -> ExtractionResult:
    """Section 2.3's full semantic structure, as P4 records."""
    admit(path, policy=policy)
    document = read_docx(path)
    if document is None:
        # §2.4: no reader for this format in this deployment. `unsupported`, never
        # `failed` -- the bytes were never looked at, so a `failed` run would report
        # a missing library as a corrupt file.
        return unsupported_result(
            file_row=file_row, extractor_name=EXTRACTOR_NAME,
            extractor_version=VERSION, source_type=SOURCE_TYPE,
            analysis_tier=ANALYSIS_TIER, now=now)


    observations: list[Mapping[str, Any]] = []
    units: list[Mapping[str, Any]] = []

    def emit(*, zone, raw, container_path, span, unit_text, reliability,
             normalized=None):
        before = after = ""
        truncated = False
        if span is not None and unit_text is not None:
            before, after, truncated = context_for(unit_text, span["start"],
                                                   span["end"], window=context_window)
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=SOURCE_TYPE, raw_value=raw,
            normalized_value=normalized if normalized is not None
            else normalize_mechanical(raw),
            location=location(zone=zone, container_path=container_path,
                              text_span=span),
            context_before=before, context_after=after, context_truncated=truncated,
            observed_at=now, reliability=reliability,
        ))

    for name in sorted(document.core_properties):
        value = document.core_properties[name]
        if not value:
            continue                     # presence only; an absence is never a row
        emit(zone="title" if name in TITLE_PROPERTIES else "metadata",
             raw=value, container_path=(segment("field", label=name),), span=None,
             unit_text=None, reliability="direct",
             normalized=document.iso_dates.get(name))

    for paragraph in document.paragraphs:
        if not paragraph.text:
            continue
        container = _paragraph_path(paragraph)
        units.append(text_unit(text=paragraph.text, container_path=container))
        whole = {"start": 0, "end": len(paragraph.text)}
        if paragraph.zone in ("heading", "header_footer"):
            # A heading and a running footer are short, labelled positions and are
            # values in their own right (section 2.3; section 3.7 weights "a footer").
            emit(zone=paragraph.zone, raw=paragraph.text, container_path=container,
                 span=whole, unit_text=paragraph.text, reliability="possible")
        for found in find_structured_strings(paragraph.text):
            raw = paragraph.text[found.start:found.end]
            emit(zone=ZONE_BY_STRUCTURED_KIND.get(found.kind, paragraph.zone),
                 raw=raw, container_path=container,
                 span={"start": found.start, "end": found.end},
                 unit_text=paragraph.text, reliability="possible")

    for cell in document.cells:
        if not cell.text:
            continue
        container = (segment("table", index=cell.table),
                     segment("row", index=cell.row),
                     segment("column", index=cell.column, label=cell.column_header))
        units.append(text_unit(text=cell.text, container_path=container))
        emit(zone="table", raw=cell.text, container_path=container,
             span={"start": 0, "end": len(cell.text)}, unit_text=cell.text,
             reliability="possible")

    for link in document.links:
        container = ((segment("paragraph", index=link.paragraph),)
                     if link.paragraph is not None else ())
        emit(zone="link", raw=link.target, container_path=container, span=None,
             unit_text=None, reliability="direct")

    for target in document.relationships:
        emit(zone="metadata", raw=target,
             container_path=(segment("field", label="relationship"),), span=None,
             unit_text=None, reliability="direct")

    for annotation in document.annotations:
        container = ((segment("paragraph", index=annotation.paragraph),)
                     if annotation.paragraph is not None
                     else (segment("field", label=annotation.name),))
        emit(zone="annotation", raw=annotation.text, container_path=container,
             span=None, unit_text=None, reliability="direct")

    paragraphs = len(document.paragraphs)
    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=SOURCE_TYPE, analysis_tier=ANALYSIS_TIER,
                config={"reader": "injected",
                        "context_window": context_window},
                completeness="complete",
                coverage=coverage("paragraphs", paragraphs, paragraphs),
                observation_count=len(observations), started_at=now, finished_at=now),
        observations=tuple(observations),
        text_units=tuple(units),
    )
