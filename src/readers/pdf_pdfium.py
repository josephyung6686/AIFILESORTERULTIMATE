# src/readers/pdf_pdfium.py
"""`read_pdf` backed by pdfium, for the runs where pdfminer's speed is the product.

**Why a second PDF reader exists.** `pdf_pdfminer.py` states its own cost -- *"Its
known cost is speed on large documents. That is the trade, and this module is exactly
the seam to swap at"* -- and a whole-run profile turned that sentence into the
product's largest single number: over eighteen of the owner's real files, 55.0 of 72.0
seconds were inside `read_pdf`, essentially all of it in `pdfminer.psparser.nexttoken`.
pdfminer.six is a pure-Python parser and that IS the cost; no amount of tuning around
it moves a run from hours to minutes.

Measured on those same seventeen PDFs, one interpreter, back to back, under the
product's own 50-page ceiling:

    pdfminer.six (layout)   30.98s   176 pages     5.7 pages/s
    pypdf 4.3.1             16.23s   176 pages    10.8 pages/s
    PyMuPDF 1.28.2           3.74s   176 pages    47.0 pages/s   AGPL-3.0
    pypdfium2 5.13.0         2.02s   176 pages    87.0 pages/s   Apache-2.0/BSD-3

**There is no speed-versus-licence trade here, which is the only reason this module
is pdfium and not MuPDF.** The AGPL option is also the slower one. pypdfium2 wraps
Google's pdfium (BSD-3-Clause) under Apache-2.0 OR BSD-3-Clause and ships a prebuilt
binary wheel, so a deployment that ships this file ships no copyleft obligation and
no build toolchain.

**It has to earn the swap on fidelity, not on speed.** `Region`'s contract is why
pdfminer was chosen: *"a library that returns only page text cannot produce an honest
`Region` at all"*. Zones need per-character font size and position. pdfium exposes
both -- `FPDFText_GetFontSize` and `FPDFText_GetLooseCharBox` -- so the zone rule
below is `pdf_pdfminer.py`'s rule transcribed, not a new one, and
`tests/readers/test_pdf_pdfium.py` puts one document through both readers and
compares the zones and the heading labels rather than the prose.

Measured over 91 real PDFs of the owner's, 1,111 pages, the same 50-page ceiling:
pdfium is 11.8x faster, agrees on the page count and on `pages_total` for 91 of 91,
returns byte-identical metadata and ISO dates for 91 of 91, and reaches a page-text
similarity of 1.000 at the median with 82 of 91 above 0.95. It disagrees about
headings -- 3,194 against 2,195 -- and that difference is CONCENTRATED: eight long
table-heavy documents account for 683 of the 821 distinct labels that differ, and on
several of those the two libraries disagree about how much of the page is text at all,
with pdfium reading MORE (one file: 3,986 characters against 58,501). On the owner's
own seventeen-file corpus the same comparison is 172 against 181.

**The Info dictionary is still pdfminer's.** pdfium's `FPDF_GetMetaText` answers a
key it is HANDED and cannot enumerate the dictionary, so a pure-pdfium reader would
silently drop every slot outside the nine standard ones. Measured over 91 real PDFs,
fifteen carry one: `Company`, `SourceModified`, `PTEX.Fullbanner`, and on one file six
`MSIP_Label_*` keys -- a Microsoft sensitivity label, on a document this product is
meant to be careful with. Parsing the trailer costs 2.5 ms per file against a page
read of tens of milliseconds, so keeping it buys full P4 D7 fidelity for 0.3 % of the
time. That is a deployment's choice to make and this is the deployment layer.

**The thresholds are `pdf_pdfminer.py`'s, deliberately identical.** `heading_ratio`
and `margin_fraction` are adapter policy -- statements about how a library's numbers
map onto P4's zones -- and giving the two readers different ones would mean the
product recognised a document differently depending on which library shipped.
"""
from __future__ import annotations

import ctypes
from collections import Counter
from pathlib import Path
from typing import Callable

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c

from extractors.pdf import PdfDocument as P5PdfDocument
from extractors.pdf import PdfPage
from extractors.reading import Region

# The Info dictionary, from the library that can enumerate one. Imported rather than
# copied: two parsers for one format's date syntax is how the two readers would come
# to disagree about a `CreationDate` while both looked right.
from readers.pdf_pdfminer import _metadata

#: pdfium separates its lines with these, as real characters in the character stream
#: (index i of the stream is character i of `get_text_range()`, verified by execution).
#: They end a line and belong to no region.
_BREAKS = "\r\n"


class _Line:
    """One line of a page: its characters, its extent and its sizes.

    A class and not a tuple because building it is the hot loop -- one `FPDFText_`
    call per character over a whole corpus -- and every attribute here is written
    once per character.
    """

    __slots__ = ("chars", "x0", "y0", "y1", "size", "sizes", "height", "heights")

    def __init__(self) -> None:
        self.chars: list[str] = []
        self.x0 = float("inf")
        self.y0 = float("inf")
        self.y1 = float("-inf")
        #: The font's declared size, which is what pdfminer's `LTChar.size` is.
        self.size = 0.0
        self.sizes: Counter = Counter()
        #: The em box's height in PAGE space. The same number when the text matrix
        #: does no scaling, and the only usable one when it does. `_size_signal`
        #: chooses; both are collected because the choice is per page.
        self.height = 0.0
        self.heights: Counter = Counter()

    def text(self) -> str:
        return "".join(self.chars)


def _lines(textpage) -> list[_Line]:
    """Every line on the page, in pdfium's own order.

    pdfium has already done the line grouping -- `FPDFText_GetText` inserts the break
    -- so this walks the character stream once and closes a line at each break. The
    alternative, `FPDFText_CountRects`/`GetRect`, gives the same rectangles but no
    way back to the character indices, and without those there is no font size, which
    is half of what a zone is decided by.
    """
    stream = textpage.get_text_range()
    handle = textpage.raw
    font_size = pdfium_c.FPDFText_GetFontSize
    loose_box = pdfium_c.FPDFText_GetLooseCharBox
    rect = pdfium_c.FS_RECTF()
    into = ctypes.byref(rect)

    found: list[_Line] = []
    line = _Line()
    for index, character in enumerate(stream):
        if character in _BREAKS:
            if line.chars:
                found.append(line)
            line = _Line()
            continue
        line.chars.append(character)
        # THE LOOSE box and not `FPDFText_GetCharBox`: the loose one is the em box,
        # ascent to descent, which is the box pdfminer's `LTChar` reports and the
        # box the margin test was written against. The tight box is the ink, so a
        # line of lower-case letters would sit lower in its own bounding box than
        # the same line with one capital in it, and a running foot would drift in
        # and out of the margin band depending on its spelling.
        loose_box(handle, index, into)
        height = rect.top - rect.bottom
        if not height:
            # pdfium reports a zero-height box for a space. It has no size and no
            # extent, and counting it would let the whitespace of a sparse page
            # outvote its type for what "the body size" means.
            continue
        size = font_size(handle, index)
        line.sizes[round(size, 1)] += 1
        line.heights[round(height, 1)] += 1
        if size > line.size:
            line.size = size
        if height > line.height:
            line.height = height
        if rect.left < line.x0:
            line.x0 = rect.left
        if rect.bottom < line.y0:
            line.y0 = rect.bottom
        if rect.top > line.y1:
            line.y1 = rect.top
    if line.chars:
        found.append(line)
    return found


def _size_signal(lines: list[_Line]) -> str:
    """Which of the two size numbers this page's zones may be decided by.

    **`FPDFText_GetFontSize` is right until it is 1.0, and then it is useless.** It
    returns the size from the TEXT STATE without the text matrix, and a PDF is
    perfectly entitled to declare a 1-point font and scale it by twelve. Every
    document LaTeX produces does exactly that: measured on the owner's own
    `PHYS1401_Lecture11_002.pdf` and `exam2 2.pdf`, every character on the page
    reports 1.0, so no line is ever large relative to any other and all 31 of their
    headings disappeared -- a silent loss, because the pages still read perfectly.

    **The em box's height is the fallback and not the default, and that ordering is
    the whole of this function.** The box is proportional to the rendered size, which
    is what the ratio needs, but it is also proportional to the FONT's ascent and
    descent -- so two faces at one point size give two heights, and using it
    everywhere turned 172 headings into 269 across the same seventeen files, inventing
    74 in a document that has none. Measured both ways on the owner's corpus:

        signal              headings   labels kept   lost   gained
        GetFontSize            123          86        44       0
        loose box height       269         127         3      60
        this function          181         126         4      13

    -- against pdfminer's 172 on the same seventeen files.

    So: the declared size, unless this page declares one size and that size is 1.0,
    which is the signature of a page whose type is scaled entirely by its matrix.
    """
    declared = Counter()
    for line in lines:
        declared.update(line.sizes)
    if len(declared) == 1 and next(iter(declared)) == 1:
        return "height"
    return "size"


def _dominant_size(lines: list[_Line], signal: str) -> float:
    """The page's body size, weighted by CHARACTER COUNT rather than by line.

    `pdf_pdfminer._dominant_size`'s reasoning, unchanged: a page whose only large
    line is its title has one heading line and many body lines, but a page of large
    type with a single small footnote has the opposite shape. Counting characters is
    what makes "large relative to this page" mean the same thing on both.
    """
    sizes: Counter = Counter()
    for line in lines:
        sizes.update(line.heights if signal == "height" else line.sizes)
    if not sizes:
        return 0.0
    return sizes.most_common(1)[0][0]


def pdfium_reader(*, heading_ratio: float = 1.15,
                  margin_fraction: float = 0.08,
                  max_pages: int | None = None) -> Callable[[Path], P5PdfDocument]:
    """Build the `read_pdf` callable `extractors.dispatch.Readers` takes.

    A factory for `pdf_pdfminer.pdfminer_reader`'s reasons: the two adapter policies
    stay visible and tunable, and nothing here holds process state.

    `max_pages` is §8.6's page cap and `None` reads the whole document. The NUMBER is
    not chosen here -- `cli.py` is the only file that picks one and passes this reader
    in through `macos_readers(read_pdf=...)`.
    """

    def read_pdf(path: Path) -> P5PdfDocument:
        # §2.4: an unreadable file must never be "silently treated as an empty
        # document". Nothing here catches -- pdfium reports a load failure as
        # `PdfiumError` and P5's catcher turns that into one `failed` run, which is a
        # true statement about the file.
        metadata, iso_dates = _metadata(Path(path))
        document = pdfium.PdfDocument(path)
        try:
            total = len(document)
            ceiling = total if max_pages is None else min(max_pages, total)
            pages: list[PdfPage] = []

            for number in range(1, ceiling + 1):
                page = document[number - 1]
                textpage = page.get_textpage()
                lines = _lines(textpage)
                signal = _size_signal(lines)
                body_size = _dominant_size(lines, signal)
                # pdfium reports a page's size in its own page space, whose origin is
                # the bottom-left corner and whose y grows upward -- the same
                # convention `pdf_pdfminer` reads off `page.bbox`.
                height = page.get_size()[1] or 1.0
                margin = height * margin_fraction
                top, bottom = height - margin, margin

                # Reading order: top of the page first, exactly as the pdfminer
                # adapter sorts, so a document does not change shape when a
                # deployment changes library.
                lines.sort(key=lambda line: (-line.y1, line.x0))

                text_parts: list[str] = []
                regions: list[Region] = []
                cursor = 0
                heading_ordinal = 0

                for line in lines:
                    rendered = line.text() + "\n"
                    stripped = rendered.strip()
                    if not stripped:
                        text_parts.append(rendered)
                        cursor += len(rendered)
                        continue

                    # The span covers the line's TEXT, not its trailing newline, so a
                    # slice of `page.text` by these offsets is the evidence itself.
                    lead = len(rendered) - len(rendered.lstrip())
                    start = cursor + lead
                    end = start + len(stripped)

                    zone = "body"
                    ordinal = label = None
                    if line.y1 > top or line.y0 < bottom:
                        # Bottom or top margin band: a running head or foot. Geometry
                        # only -- a page number and a chapter title look identical
                        # here and both belong to the same zone.
                        zone = "header_footer"
                    elif body_size and (
                            line.height if signal == "height" else line.size
                    ) >= body_size * heading_ratio:
                        zone = "heading"
                        heading_ordinal += 1
                        ordinal = heading_ordinal      # 1-based, P4 D3
                        label = stripped               # descriptive only, P4 rule 2

                    regions.append(Region(zone=zone, start=start, end=end,
                                          ordinal=ordinal, label=label))
                    text_parts.append(rendered)
                    cursor += len(rendered)

                pages.append(PdfPage(number=number, text="".join(text_parts),
                                     regions=tuple(regions)))
        finally:
            document.close()

        # `total` is the document's real length, which pdfium knows without laying a
        # page out -- so unlike the pdfminer adapter there is no second pass to pay
        # for, and the count is reported whether or not a ceiling was set.
        return P5PdfDocument(metadata=metadata, pages=tuple(pages),
                             iso_dates=iso_dates, pages_total=total,
                             capped=len(pages) < total)

    return read_pdf
