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

#: BUMPED 0.1.0 -> 0.2.0 BY `104` R-164, AND THE BUMP IS THE POINT OF THE RULE.
#: This reader now splits a plain-text document into paragraph units where it used
#: to emit one span-less body observation over the whole file, so the SAME bytes
#: now produce different evidence. `00`:44 says the cache key exists so that "an
#: upgraded reader invalidates the answers that rested on its output", and
#: `model_facts.call_identity_dimensions` reads `extractor_versions` as a set of
#: `(name, version)` pairs -- WHICH readers ran, never what they produced. So the
#: version string is the only signal a changed output has, and leaving it at 0.1.0
#: after R-164 would have let `--reuse-answers-from` answer from a prior run's
#: cache for files whose evidence had completely changed, and report it as a
#: saving. `104` §17.11 records the trap in full.
#:
#: BUMPED 0.2.0 -> 0.3.0 BY `104` §18.2 GAP 17, under the same rule. E3 IS TWO
#: HALVES AND ONE VERSION -- `long_tail.py` imports this name, because the router
#: dispatches both halves to `text.structured` and one extractor may not have two
#: numbers -- and the long-tail half now emits a span-less whole-unit observation
#: for every bulk-text zone. A `.pptx` and an `.eml` extracted before this carry no
#: row for their own content; the number is what says so.
# `104` R-164's rule, applied 10 Sep 2026 for R-160: a notebook's markdown cells
# are now body units, so what E3 emits for `.ipynb` changed and the cache key
# must move with it, or the owner's cached notebooks are never re-read.
VERSION = "0.4.0"

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
    #: The document's own CELLS, when the format has them and the reader read them --
    #: `104` R-160, and today a notebook's markdown cells are the only producer.
    #: Each is a stretch of `text`, carrying the format's own 1-based cell number as
    #: its `ordinal` and saying its OWN zone, because which kind of place a cell is
    #: is library knowledge (`Region`'s docstring) and E3 has no way to tell prose
    #: from source by looking. Absent everywhere else, so a `.txt` and a `.md` are
    #: read exactly as they were.
    cells: tuple[Region, ...] = ()


def paragraph_spans(text: str) -> tuple[tuple[int, int], ...]:
    """The document's OWN paragraphs, as half-open spans into `text`.

    The separator is a run of one or more blank lines -- a line that is empty or
    holds only whitespace -- which is the only paragraph boundary a plain text file
    has and the one every writer of one already uses. Nothing else is consulted:
    no length, no count, no vocabulary, and no opinion about what a paragraph ought
    to look like. A file that runs its prose together is one paragraph and is not
    cut up on this module's guess at a good size.

    The spans are exact and exhaustive. A paragraph runs from the first character
    of its first non-blank line to the last character of its last one, keeping that
    line's own terminator and any leading indentation, so `text[start:end]` is the
    paragraph verbatim and the paragraphs and the blank runs between them
    concatenate back to `text` character for character. That is what lets a
    paragraph be a text UNIT: P4 rule 10 measures a reading against the unit at its
    path, and a unit whose text was trimmed would be measuring against something
    the file does not contain.

    What counts as a line is whatever `str.splitlines` counts as one, which is to
    say the document's own terminators rather than a newline named here.
    """
    spans: list[tuple[int, int]] = []
    start: int | None = None
    end = offset = 0
    for line in text.splitlines(keepends=True):
        stop = offset + len(line)
        if line.strip():
            if start is None:
                start = offset
            end = stop
        elif start is not None:
            spans.append((start, end))
            start = None
        offset = stop
    if start is not None:
        spans.append((start, end))
    return tuple(spans)


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
        # No span, because a span serialises INTO the locator: `body#0-60` starts
        # with `body#`, which is the space the shipped deployment's direct slot
        # claims -- and the whole document would have become a `subject` fact, which
        # is to say a FOLDER NAME. `test_the_readable_text_does_not_become_a_folder_name`
        # caught precisely that before it shipped. A paragraph is addressed
        # `body:paragraph=N`, which carries no `#` either, and
        # `test_a_paragraph_reading_does_not_become_a_folder_name` asks the same
        # question of the new locator.
        #
        # THE CONTAINER IS WHAT `104` R-164 CHANGED, and only for the reading that
        # has one. The whole-document reading carries no container because P4 rule
        # 10 anchors a reading to a text unit at exactly its path, and the whole
        # text is the unit at the empty path; giving THAT reading a container would
        # have meant storing the entire document a second time for it to sit in. A
        # paragraph's container is not a hiding place: a unit stands at exactly
        # `paragraph=N` holding exactly those characters, so rule 10 is satisfied by
        # construction and `store.unit_length_for_observation` measures the reading
        # against the paragraph it is the whole of -- the same lookup, by the same
        # serialized path, that already answers for a `.docx` paragraph.
        #
        # AND THAT IS WHAT MAKES THE SECOND COPY WORTH ITS COST. `104` R-159 made a
        # whole UNIT releasable to a local target; a whole DOCUMENT is releasable to
        # nothing, and rightly. One unit per file therefore meant a 39,000-character
        # `.txt` that no dossier ceiling could ever admit -- `104` §16.1 measured the
        # result, a model shown a document's headings and its file extension while
        # every word of it sat extracted and stored. A paragraph-sized unit is a
        # reading the ceiling can admit. Nothing on this device loses anything by the
        # split: the recogniser scans raw values, needs no span, and sees the same
        # characters spread over the paragraphs that it saw in one reading.
        #
        # The split is the DOCUMENT'S OWN -- `paragraph_spans`: its blank lines, in
        # its order, with its whitespace kept. No length, no count, no preference.
        paragraphs = paragraph_spans(document.text)
        if len(paragraphs) > 1:
            for index, (start, end) in enumerate(paragraphs, start=1):
                paragraph = document.text[start:end]
                container = (segment("paragraph", index=index),)
                units.append(text_unit(text=paragraph, container_path=container))
                emit(zone="body", raw=paragraph, container_path=container, span=None,
                     unit_text=None, reliability="possible")
        else:
            # One paragraph -- or none at all, which is a file of whitespace. The
            # document IS the paragraph, the unit at the empty path is already
            # standing, and a `paragraph=1` beside it would be the same characters
            # stored twice and offered twice.
            emit(zone="body", raw=document.text, container_path=(), span=None,
                 unit_text=None, reliability="possible")

    # `104` R-160, and it stands OUTSIDE the prose gate above on purpose. A notebook
    # is `code_structured`, so the whole-text reading is rightly withheld from it --
    # and the consequence measured on the owner's eleven notebooks was a file that
    # produced its headings, its three metadata markers and not one word of what its
    # author actually wrote. A markdown cell is not "arbitrary code text": it is the
    # prose a person typed into a prose cell, and §2.4's exclusion is about the
    # other kind. The READER decides which cells are which and reports only those it
    # can name a zone for; this loop asks nothing about the format.
    #
    # ADDRESSED `cell=N`, WHICH IS THE NOTEBOOK'S OWN ADDRESS (P4 D3 rule 3), and
    # `cell` has been in `INDEXED_SEGMENT_KINDS` all along -- no vocabulary is added
    # here. It carries no `#`, so a cell cannot become a `subject` fact and cannot
    # name a folder, which is the same guard `body:paragraph=N` above is built on.
    # NO SPAN, for that reason exactly.
    #
    # The unit stands at exactly that path holding exactly those characters, so P4
    # rule 10 is satisfied by construction and `store.unit_length_for_observation`
    # measures the reading against the cell it is the whole of -- a cell-sized unit
    # is a reading §8.6's ceiling can admit, where the 118,000-character notebook
    # `104` §16.1 measured was a reading nothing could.
    for cell in document.cells:
        cell_text = document.text[cell.start:cell.end]
        container = (segment("cell", index=cell.ordinal),)
        units.append(text_unit(text=cell_text, container_path=container))
        emit(zone=cell.zone, raw=cell_text, container_path=container, span=None,
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
