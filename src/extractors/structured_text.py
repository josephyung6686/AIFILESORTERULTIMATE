# src/extractors/structured_text.py
"""E3 - structured text and code (section 2.4).

"Text-bearing files such as Markdown, plain text, JSON, CSV, source code, notebooks,
and configuration files should be handled through a lighter structured-text
extractor. The engine should store their text, filename, extension, language where
relevant, headings, and structural indicators such as repository markers, package
manifests, notebook metadata, and README files."

Filename and extension are NOT emitted here. They are P3's section 1.2 record and O5
gives them to the `filesystem` run, which is what makes a filename citable evidence;
a second emission would be two homes for one value.

Section 2.4's two outcomes, and the third it forbids:

    reader returns a document      -> `complete`, even with zero observations
    reader returns None            -> `unsupported`; no extractor exists for this
                                      format in this deployment

"The system should never silently treat an unsupported format as an empty document,
because an empty extraction result is different from an extractor that does not yet
exist."

E3 reads no code. Section 2.4 requires code files to "rely heavily on local
structural evidence ... rather than forcing semantic analysis to infer a project from
arbitrary code text", so there is no import parser and no project inference here: the
reader reports markers, the injected finder reports strings, and P5 places them.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors.failure import unsupported_result
from extractors.reading import ZONE_BY_STRUCTURED_KIND, Region, StructuredString
from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import (
    context_for, location, normalize_mechanical, observation, run, segment, text_unit,
)
from extractors.sink import ExtractionResult

VERSION = "0.1.0"

#: One family name for both halves of E3: the router dispatches eight `source_type`s
#: here and `runs.ANALYSIS_TIER_BY_EXTRACTOR` keys the tier on the family.
EXTRACTOR_NAME = "text.structured"
ANALYSIS_TIER = "native"

#: Section 2.4's own families, in P4's `source_type` vocabulary. The remaining six the
#: router sends to `text.structured` are section 2.9's and live in long_tail.py.
STRUCTURED_TEXT_SOURCE_TYPES: tuple[str, ...] = ("text_document", "code_structured")

#: Section 2.4's four classes of "structural indicators", in section 2.4's words.
#: WHICH FILES ARE MEMBERS of each class is Deferred - the SPEC's Deferred table says
#: section 1.1's four are P3's and "Everything else" is unsettled - so no member name
#: appears in this module and the reader supplies them.
STRUCTURAL_MARKER_KINDS: tuple[str, ...] = (
    "repository marker", "package manifest", "notebook metadata", "README file",
)

#: The slot section 2.4's "language where relevant" occupies. The VALUE is the
#: reader's; P5 detects no language and holds no language list.
LANGUAGE_FIELD = "language"


class WrongFamily(Exception):
    """A `source_type` this half of E3 does not handle."""


class UnknownMarkerKind(Exception):
    """A structural-indicator class section 2.4 does not name."""


@dataclass(frozen=True)
class StructuralMarker:
    """One of section 2.4's structural indicators, as the reader found it.

    `kind` is one of section 2.4's four classes; `value` is the marker itself - a
    file name, a manifest name, a notebook metadata key - verbatim.
    """
    kind: str
    value: str


@dataclass(frozen=True)
class TextDocument:
    """What an injected `read_text_document` returns, or None when this deployment
    ships no reader for the format (section 2.4's `unsupported` outcome)."""
    text: str
    language: str | None = None
    headings: tuple[Region, ...] = ()
    markers: tuple[StructuralMarker, ...] = ()


def extract_structured_text(
        *, file_row: Mapping[str, Any], path: Path, policy: SafetyPolicy,
        source_type: str,
        read_text_document: Callable[[Path], TextDocument | None],
        find_structured_strings: Callable[[str], tuple[StructuredString, ...]],
        now: str, context_window: int) -> ExtractionResult:
    """Section 2.4's lighter structured-text extractor, as P4 records."""
    if source_type not in STRUCTURED_TEXT_SOURCE_TYPES:
        raise WrongFamily(
            f"{source_type!r} is one of section 2.9's long-tail families; E3 handles "
            f"it in long_tail.py. This half handles {STRUCTURED_TEXT_SOURCE_TYPES}."
        )
    admit(path, policy=policy)
    document = read_text_document(path)
    if document is None:
        return unsupported_result(
            file_row=file_row, extractor_name=EXTRACTOR_NAME,
            extractor_version=VERSION, source_type=source_type,
            analysis_tier=ANALYSIS_TIER, now=now)

    observations: list[Mapping[str, Any]] = []
    units: list[Mapping[str, Any]] = [text_unit(text=document.text)]

    def emit(*, zone, raw, container_path, span, unit_text, reliability):
        before = after = ""
        truncated = False
        if span is not None and unit_text is not None:
            before, after, truncated = context_for(unit_text, span["start"],
                                                   span["end"], window=context_window)
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=source_type, raw_value=raw,
            normalized_value=normalize_mechanical(raw),
            location=location(zone=zone, container_path=container_path,
                              text_span=span),
            context_before=before, context_after=after, context_truncated=truncated,
            observed_at=now, reliability=reliability,
        ))

    if document.language:
        emit(zone="metadata", raw=document.language,
             container_path=(segment("field", label=LANGUAGE_FIELD),), span=None,
             unit_text=None, reliability="direct")

    for marker in document.markers:
        if marker.kind not in STRUCTURAL_MARKER_KINDS:
            raise UnknownMarkerKind(
                f"{marker.kind!r} is not one of section 2.4's four structural-"
                f"indicator classes {STRUCTURAL_MARKER_KINDS}"
            )
        emit(zone="metadata", raw=marker.value,
             container_path=(segment("field", label=marker.kind),), span=None,
             unit_text=None, reliability="direct")

    heading_paths: dict[int, tuple] = {}
    for region in document.headings:
        heading_path = (segment("heading", index=region.ordinal, label=region.label),)
        heading_paths[region.start] = heading_path
        heading_text = document.text[region.start:region.end]
        units.append(text_unit(text=heading_text, container_path=heading_path))
        emit(zone="heading", raw=heading_text, container_path=heading_path,
             span={"start": 0, "end": len(heading_text)}, unit_text=heading_text,
             reliability="possible")

    for found in find_structured_strings(document.text):
        inside = next((r for r in document.headings
                       if r.start <= found.start < r.end), None)
        if inside is not None:
            container = heading_paths[inside.start]
            unit_text = document.text[inside.start:inside.end]
            start, end = found.start - inside.start, found.end - inside.start
            zone = ZONE_BY_STRUCTURED_KIND.get(found.kind, "heading")
        else:
            container = ()
            unit_text = document.text
            start, end = found.start, found.end
            zone = ZONE_BY_STRUCTURED_KIND.get(found.kind, "body")
        emit(zone=zone, raw=unit_text[start:end], container_path=container,
             span={"start": start, "end": end}, unit_text=unit_text,
             reliability="possible")

    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=source_type, analysis_tier=ANALYSIS_TIER,
                config={"reader": "injected",
                        "context_window": context_window},
                completeness="complete",
                coverage=coverage("files", 1, 1),
                observation_count=len(observations), started_at=now, finished_at=now),
        observations=tuple(observations),
        text_units=tuple(units),
    )
