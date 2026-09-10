# src/readers/docx_python_docx.py
"""`read_docx` backed by python-docx.

**Why this exists at all.** `deployment.py` wired `read_docx = _no_reader`, whose
docstring says *"this deployment ships no library for the format"*. That sentence
was true when it was written and is not true now: `python-docx` is installed in
this interpreter. The consequence of leaving it was not a missing feature but a
LIE IN THE RECORD -- every `.docx` on a person's disk recorded `unsupported`,
which §2.4 defines as *"no reader exists and the bytes were never looked at"*, and
downstream every count agreed that those files carried nothing. On a real human's
disk that is most of the writing they have ever done.

**What is library knowledge and what is not.** `Region`'s contract: *"the reader
says WHAT KIND OF PLACE this is, because that is library knowledge (a heading
style, a table cell, a footer)"*. python-docx exposes the paragraph STYLE, which is
what Word itself uses to mean "this is a heading", and the outline LEVEL that goes
with it. So the zone here is read from the style, never guessed from the text --
no "short line in title case is probably a heading", which would be exactly the
structural judgement P4 forbids a reader to invent.

**LINKS AND RELATIONSHIPS ARE NOW READ, and that paragraph is `104` §18.2 gap 17.**
What stood here said they were *"the honest next increment, not a gap hidden behind
a default"*, and it stayed the next increment while `extractors/docx.py` carried two
`emit` arms for them -- `zone="link"` at `reliability: direct` and a
`relationship`-labelled metadata field -- that no document could ever reach. That is
the shape §18.2 calls a SILENT LOSS: not a feature nobody built, but a reading the
extractor already knows how to record and the reader never hands it. §2.3 lists
*"hyperlinks, document relationships"* in the same sentence as the tables and the
headers this module already recovers, and the URL a `.docx` points at is often the
most specific thing in it -- an application portal, a course page, a journal article.

**The two are DIFFERENT READINGS and the split is the document's own.** A
`w:hyperlink` sits INSIDE a paragraph, so it has an address in P4's sense and travels
as a `DocxLink` carrying that paragraph's ordinal. A relationship is declared by the
document PART and anchored to nothing, so it travels as a bare target. A URL that is
both -- and every paragraph hyperlink is, because the anchor is a relationship
reference -- is reported ONCE, as the link, because the link is the more located of
the two readings and G1 keys a citation by where it stands.

**Only EXTERNAL relationships, and `is_external` is python-docx's own reading of
OOXML's `TargetMode` rather than a judgement here.** An internal relationship names a
part every Word document has: an empty one this module just wrote declares eight of
them -- `styles.xml`, `stylesWithEffects.xml`, `settings.xml`, `webSettings.xml`,
`fontTable.xml`, `theme/theme1.xml`, `numbering.xml`, `customXml/item1.xml` -- and
storing those would put eight rows of Word's own boilerplate into the evidence table
for every `.docx` on a person's disk, at `reliability: direct`, for the recogniser to
be starved past. What §2.3 asks to preserve is what the document POINTS AT.

**The limit that remains, stated rather than silent.** Only the document part's own
relationships are read. A hyperlink that lives in a header, a footer or a comment is
declared by THAT part and does not appear here -- the same boundary
`_running_paragraphs` crosses for text and this does not, because reaching a header
part's rels is a second walk and P4 would have no ordinal to address it by.

**Headers, footers and comments WERE on that list and are now read.** §2.3 asks for
*"headers and footers where feasible ... and available revision or comment
metadata"*, and `extractors/docx.py` has carried the `header_footer` zone and
`DocxAnnotation` since it was written -- both reachable, both permanently empty,
because nothing produced them. Measured over the owner's 199-file corpus on
2026-09-05: 371,345 `<w:t>` characters live in `word/document.xml`, of which this
reader already recovered 100%; 3,913 live in `word/header*.xml`, `word/footer*.xml`
and `word/comments.xml`, of which it recovered none. Small in characters and not
small in content -- the running header of every résumé in that corpus is the
person's name, address and telephone number, and the body says none of it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import docx
from docx.document import Document as _Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from extractors.docx import (
    DocxAnnotation, DocxCell, DocxDocument, DocxLink, DocxParagraph,
)

#: The core properties P4 keeps as strings. `title` is its own zone (P5
#: `docx.py`'s `TITLE_PROPERTIES`); the rest travel as document metadata. Read by
#: NAME rather than by iterating the object, because python-docx exposes a fixed
#: set of attributes and a `dir()` walk would pick up methods.
_CORE_PROPERTIES: tuple[str, ...] = (
    "title", "author", "subject", "keywords", "category", "comments",
    "last_modified_by", "content_status", "identifier", "language", "version",
)

#: The core properties whose value is a datetime rather than a string. §2.3 keeps
#: them apart from the text slots, and P4 D8 wants them ISO-8601.
_DATE_PROPERTIES: tuple[str, ...] = ("created", "modified", "last_printed")

#: Word's own names for the built-in heading styles, and the only thing consulted
#: to decide that a paragraph is a heading. A document that renames them loses the
#: zone rather than gaining a guessed one.
_HEADING_STYLE = "heading"
_TITLE_STYLE = "title"


def _zone(paragraph: Paragraph) -> tuple[str, int | None]:
    """P4's zone for this paragraph, and its outline depth if it is a heading.

    `style.name` rather than the raw style id: python-docx resolves the id through
    the document's style table, so a document that inherits `Heading 1` from a
    template still reads as a heading. A paragraph inside a header or footer part
    never reaches this function -- python-docx exposes those on a different object
    and this reader does not walk them, which is why `header_footer` is not
    produced here rather than being produced wrongly.
    """
    name = (paragraph.style.name or "").strip().lower() if paragraph.style else ""
    if name.startswith(_HEADING_STYLE):
        suffix = name[len(_HEADING_STYLE):].strip()
        # `Heading 1` -> 1. An unnumbered `Heading` is still a heading; it sits at
        # the outermost level, which is what Word renders it as.
        return "heading", int(suffix) if suffix.isdigit() else 1
    if name == _TITLE_STYLE:
        return "heading", 1
    return "body", None


#: The header and footer a section can define, in `python-docx`'s own attribute
#: names. Four of the six are Word's optional first-page and even-page variants; a
#: section that does not define one reports the inherited text, which
#: `_running_paragraphs` drops by identity. Named here rather than reached for by a
#: pattern over `dir()`, because which parts a section has is library knowledge.
_RUNNING_PARTS: tuple[str, ...] = (
    "header", "footer",
    "first_page_header", "first_page_footer",
    "even_page_header", "even_page_footer",
)


def _running_paragraphs(document: _Document) -> list[str]:
    """Every distinct line of running matter, in section order.

    THE UNIT OF IDENTITY IS THE TEXT, and that is the whole of the deduplication.
    Word LINKS a section's header to the previous one unless it is overridden, and
    python-docx reports the inherited text on every section -- so a plain walk stores
    one running head once per section. That is two observations of one value and,
    worse, two `text_units` at two different addresses holding one piece of text,
    which is the collision G1's uniqueness rule exists to prevent.

    `is_linked_to_previous` was the obvious guard and is NOT used, because it is
    strictly weaker than this one and would have been an untested line beside it:
    inherited text is identical text, so the check below already covers it, and it
    ALSO covers the case the flag misses -- a first-page footer a document repeats as
    its running footer, which is not linked to anything and is still one line.
    """
    seen: set[str] = set()
    lines: list[str] = []
    for section in document.sections:
        for name in _RUNNING_PARTS:
            part = getattr(section, name, None)
            if part is None:
                continue
            for paragraph in part.paragraphs:
                text = paragraph.text
                if not text.strip() or text in seen:
                    continue
                seen.add(text)
                lines.append(text)
    return lines


#: The slot an annotation is addressed by, in E2's own spelling
#: (`tests/p5/test_p5_docx.py`). A SLOT NAME, never a value -- see
#: `_annotations` below for why the comment's author may not go here.
_ANNOTATION_SLOT = "comment"


def _annotations(document: _Document) -> list[DocxAnnotation]:
    """§2.3's "available revision or comment metadata", as far as the library goes.

    `name` IS A SLOT NAME AND NOT THE AUTHOR. `extractors/docx.py` renders it as
    `segment("field", label=annotation.name)` and P4 D7 defines a field label as "the
    format's own slot name, verbatim"; E2's own fixture spells it `name="comment"`.
    `w:comment/@w:author` is the slot and "Mara Ellison" is its value, so putting the
    author here would have produced the locator `annotation:field[Mara Ellison]` -- a
    person's name inside a citation string. The author is therefore DROPPED: three
    fields, none of them an author, and adding one is an extractor contract change
    rather than a reader's decision.

    `paragraph` is left None -- python-docx exposes a comment's text and author but
    not, on this version, a stable ordinal for the run it anchors to, and
    `extractors/docx.py` addresses an unanchored annotation by field name rather than
    by a paragraph it would have had to guess.

    REVISIONS ARE STILL ABSENT and stay honestly so: tracked insertions and deletions
    are `w:ins`/`w:del` elements the library does not surface, and reporting comments
    as though they were the whole of §2.3's clause would be the same overclaim this
    module's docstring refuses everywhere else.
    """
    found: list[DocxAnnotation] = []
    for comment in getattr(document, "comments", ()) or ():
        text = (comment.text or "").strip()
        if not text:
            continue
        found.append(DocxAnnotation(name=_ANNOTATION_SLOT, text=text))
    return found


def _external_relationships(document: _Document) -> list[str]:
    """Every target the document part points OUT of itself at, in the part's order.

    `104` §18.2 gap 17. `rel.is_external` is python-docx's reading of the
    relationship's `TargetMode="External"` attribute -- OOXML's own statement that
    the target is a URI and not a part of this package -- so nothing here inspects
    the string to decide what kind of thing it is. See the module docstring for why
    the internal ones are left out: eight of Word's own part names, on every
    document, at `reliability: direct`.

    ORDER IS THE PART'S OWN and duplicates collapse to the first occurrence. The
    relationship table is keyed by `rId`, and one URL may be referenced twice (a
    heading and a footer citing the same portal); two rows would be one located
    value stored twice, which is the collision G1's uniqueness rule exists to
    prevent -- and it is the same argument `_running_paragraphs` makes about an
    inherited header, made about a target instead of a line.
    """
    seen: set[str] = set()
    targets: list[str] = []
    for relationship in document.part.rels.values():
        if not relationship.is_external:
            continue
        target = str(relationship.target_ref or "").strip()
        if not target or target in seen:
            continue
        seen.add(target)
        targets.append(target)
    return targets


def _body_blocks(document: _Document):
    """Paragraphs and tables in the order the document lays them out.

    python-docx's `document.paragraphs` skips everything inside a table and
    `document.tables` loses where each table sat, so neither alone can say what
    came before what. The body element's own child order is the only place that
    ordering exists, and P4 anchors spans to a paragraph ordinal -- an ordinal
    assigned in the wrong order would point every citation at the wrong text.
    """
    body = document.element.body
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, document)
        elif child.tag == qn("w:tbl"):
            yield Table(child, document)


def _read(path: Path) -> DocxDocument | None:
    document = docx.Document(str(path))

    core = document.core_properties
    properties: dict[str, str] = {}
    for name in _CORE_PROPERTIES:
        value = getattr(core, name, None)
        if value:
            properties[name] = str(value)
    iso_dates: dict[str, str] = {}
    for name in _DATE_PROPERTIES:
        value = getattr(core, name, None)
        if value is not None:
            iso_dates[name] = value.isoformat()

    paragraphs: list[DocxParagraph] = []
    cells: list[DocxCell] = []
    links: list[DocxLink] = []
    #: The heading ancestry as (ordinal, label) pairs, outermost first. A heading
    #: at level N replaces everything from N down, which is what nesting means.
    ancestry: list[tuple[int, int, str]] = []  # (level, ordinal, label)
    #: ONE-BASED, because P4 D3 says container-path indices are: a `paragraph`
    #: segment at index 0 raises `container-path indices are 1-based`, and the
    #: whole extraction is recorded `failed` -- a real document reported as a
    #: damaged one. Every ordinal below is derived from this counter, so the
    #: heading ancestry is 1-based with it and no second convention exists.
    index = 1
    table_index = 1

    for block in _body_blocks(document):
        if isinstance(block, Table):
            #: Row 0 is the header row. That is a convention rather than a fact
            #: Word records -- `w:tblHeader` marks a REPEATING header and most
            #: documents that have a header row do not set it -- so it is applied
            #: only to name the column, never to drop the row: row 0 is emitted as
            #: a cell like any other and a caller that disagrees still has it.
            rows = block.rows
            headers: list[str | None] = []
            if rows:
                headers = [cell.text.strip() or None for cell in rows[0].cells]
            for row_index, row in enumerate(rows, start=1):
                for column_index, cell in enumerate(row.cells, start=1):
                    header = (headers[column_index - 1]
                              if column_index <= len(headers) else None)
                    cells.append(DocxCell(
                        table=table_index, row=row_index, column=column_index,
                        text=cell.text,
                        # A header row is not its own column header.
                        column_header=None if row_index == 1 else header))
            table_index += 1
            continue

        text = block.text
        if not text.strip():
            # An empty paragraph is layout, not content. It still consumes no
            # ordinal, so the ordinals stay dense and a person counting
            # paragraphs in Word and a citation here agree about which is which.
            continue
        zone, level = _zone(block)
        if zone == "heading" and level is not None:
            ancestry = [entry for entry in ancestry if entry[0] < level]
            ancestry.append((level, index, text))
        paragraphs.append(DocxParagraph(
            index=index, text=text, zone=zone,
            heading_path=tuple((ordinal, label)
                               for _, ordinal, label in ancestry)))
        # `104` §18.2 gap 17, ANCHORED TO THE ORDINAL THIS PARAGRAPH JUST TOOK.
        # Collected here rather than from a second pass over `document.paragraphs`
        # for the reason `_body_blocks` exists at all: that property skips
        # everything inside a table and loses the layout order, so a second walk
        # would hand P4 an ordinal that addresses a different paragraph.
        #
        # `address` is the external URI; an anchor into the same document (a
        # cross-reference, a bookmark) has none and is skipped, because P4 would
        # store an empty `raw_value` for it and an observation records presence,
        # never absence.
        for hyperlink in block.hyperlinks:
            target = (hyperlink.address or "").strip()
            if target:
                links.append(DocxLink(target=target, paragraph=index))
        index += 1

    #: AFTER the body, and that ordering is load-bearing. A paragraph ordinal is an
    #: ADDRESS (P4 D3) and every stored citation into this document names one, so
    #: numbering the running matter first would silently move every existing
    #: citation by however many header lines the document happens to have.
    for text in _running_paragraphs(document):
        paragraphs.append(DocxParagraph(index=index, text=text,
                                        zone="header_footer"))
        index += 1

    # The relationships a paragraph already claimed are NOT repeated here. Every
    # `w:hyperlink` is a relationship reference, so an unfiltered list would report
    # each linked URL twice -- once located at its paragraph and once at no
    # address -- and the unlocated copy is the strictly worse of the two readings.
    linked = {link.target for link in links}
    relationships = tuple(target for target in _external_relationships(document)
                          if target not in linked)

    return DocxDocument(
        core_properties=properties, paragraphs=tuple(paragraphs),
        cells=tuple(cells), links=tuple(links), relationships=relationships,
        annotations=tuple(_annotations(document)), iso_dates=iso_dates)


def python_docx_reader() -> Callable[[Path], DocxDocument | None]:
    """The wired `read_docx`.

    A factory for the same reason `pdfminer_reader` is one: it is the seam a
    deployment swaps, and a bare function would make the call site look like it
    had chosen a library rather than been given one.
    """

    def read_docx(path: Path, **_: Any) -> DocxDocument | None:
        return _read(Path(path))

    return read_docx
