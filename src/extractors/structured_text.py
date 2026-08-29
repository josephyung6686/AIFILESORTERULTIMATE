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

#: Of the two, the one whose text is written to be READ. The whole-text observation
#: below is emitted for this family and not for code -- §2.4's own distinction.
PROSE_SOURCE_TYPE: str = "text_document"

#: What the whole-text observation is addressed AS. Not cosmetic: it keeps the
#: locator out of the `body#...` space a deployment's direct slot claims, so the
#: document can be read without the document becoming a folder name.
PROSE_FIELD: str = "prose"

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

    # §2.4 and `00`:35 -- a text document "should yield full text, headings,
    # metadata, links, and structural information". The full text reached
    # `text_units` and nothing else, which meant the words in the document were
    # stored and unreachable by anything that reads EVIDENCE.
    #
    # The recogniser is the reader that matters. It holds 8,907 authored terms and
    # scans observations only, on purpose (`recognition/detector.py`: "a detector
    # that pulled whole text units would be a second materialisation locus"). So on
    # every live run it saw a filename, a path, an extension, a MIME type and one
    # identifier, matched one term from the FILENAME, and abstained under its own
    # `never_alone` rule -- one signal never activates a schema. The corroboration
    # it needed was in the file the whole time.
    #
    # Addressed `body` with NO container, which is what keeps this safe: a
    # deployment turns an observation into a FACT by claiming its locator, and a
    # fact is what a folder is named after. The shipped slot claims `body#...` and
    # `heading...`, so the product can now READ the document without gaining the
    # power to NAME a folder after it. That is the distinction `65` §2.2 missed
    # when it recorded this as one privacy trade-off instead of two knobs.
    #
    # PROSE ONLY, and the exclusion is §2.4's own: code yields structural evidence
    # "rather than forcing semantic analysis to infer a project from arbitrary code
    # text". A syllabus is prose that says what it is; a Python file is not, and
    # `test_e3_reads_no_code_and_infers_no_project` is the guard that says so.
    if document.text and source_type == PROSE_SOURCE_TYPE:
        # Addressed `body`, with no span, and BOTH halves of that are load-bearing.
        #
        # No container, because P4 rule 10 anchors a span-carrying observation to a
        # text unit at exactly its path, and the whole text is a unit at the empty
        # path. Giving it a container to hide in would mean duplicating the entire
        # document as a second unit.
        #
        # No span, because a span serialises INTO the locator: `body#0-60` starts
        # with `body#`, which is the space the shipped deployment's direct slot
        # claims -- and the whole document would have become a `subject` fact, which
        # is to say a FOLDER NAME. `test_the_readable_text_does_not_become_a_folder_name`
        # caught precisely that before it shipped.
        #
        # The cost is real and is the right one to pay: a span-less observation is
        # not model-releasable (P7 will not release an excerpt it cannot locate).
        # This observation exists to be READ BY THE RECOGNISER ON THIS DEVICE, and
        # the language and marker observations beside it carry no span either.
        emit(zone="body", raw=document.text, container_path=(), span=None,
             unit_text=None, reliability="possible")

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
