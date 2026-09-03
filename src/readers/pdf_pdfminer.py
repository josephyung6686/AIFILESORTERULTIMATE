# src/readers/pdf_pdfminer.py
"""`read_pdf` backed by pdfminer.six.

**Why this library and not another.** `Region`'s contract decides it: *"the reader
says WHAT KIND OF PLACE this is, because that is library knowledge (a heading style,
a table cell, a footer)"*, and §2.2 requires the reader preserve *"headings"* and
*"a document zone, page number, text offset"*. That needs per-character font size and
position. pdfminer exposes both on `LTChar`; a library that returns only page text
cannot produce an honest `Region` at all, and inferring zones from the words would
put structural judgement in a place that is supposed to have none.

Its known cost is speed on large documents. That is the trade, and this module is
exactly the seam to swap at — which is what an injected reader is for.

**Thresholds live here, not in the product.** `heading_ratio` and `margin_fraction`
are ADAPTER policy: statements about how this library's numbers map onto P4's zones,
not product thresholds. They are constructor parameters so they are visible and
tunable rather than buried, and P5 never sees them.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTChar, LTTextContainer, LTTextLine
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from extractors.pdf import PdfDocument as P5PdfDocument
from extractors.pdf import PdfPage
from extractors.reading import Region

#: Slots whose value is a PDF date string, rendered into `iso_dates` (P4 D8).
_DATE_SLOTS = ("CreationDate", "ModDate")

#: `D:YYYYMMDDHHmmSSOHH'mm'` — PDF 32000-1 §7.9.4. Everything after the year is
#: optional, which is why this is a parser and not a `strptime` format.
_PDF_DATE = re.compile(
    r"D:(?P<year>\d{4})(?P<month>\d{2})?(?P<day>\d{2})?"
    r"(?P<hour>\d{2})?(?P<minute>\d{2})?(?P<second>\d{2})?"
    r"(?P<tz>[+\-Z])?(?P<tzh>\d{2})?'?(?P<tzm>\d{2})?"
)


def _text(value: Any) -> str | None:
    """A metadata value as a string, verbatim (P4 D7).

    pdfminer hands back `bytes` for most slots and `PSLiteral` for some. Decoding is
    the library's business: UTF-16 with a BOM and PDFDocEncoding are both legal in
    the same file, and P5 stores strings.
    """
    if isinstance(value, bytes):
        if value[:2] in (b"\xfe\xff", b"\xff\xfe"):
            return value.decode("utf-16", errors="replace")
        return value.decode("utf-8", errors="replace")
    if value is None:
        return None
    name = getattr(value, "name", None)
    return name if isinstance(name, str) else str(value)


def _iso_date(raw: str) -> str | None:
    """PDF date syntax to ISO-8601. Returns None rather than guessing."""
    match = _PDF_DATE.match(raw.strip())
    if match is None:
        return None
    part = match.groupdict()
    stamp = (f"{part['year']}-{part['month'] or '01'}-{part['day'] or '01'}"
             f"T{part['hour'] or '00'}:{part['minute'] or '00'}"
             f":{part['second'] or '00'}")
    if part["tz"] == "Z":
        return stamp + "+00:00"
    if part["tz"] and part["tzh"]:
        return f"{stamp}{part['tz']}{part['tzh']}:{part['tzm'] or '00'}"
    return stamp


def _metadata(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    with open(path, "rb") as handle:
        document = PDFDocument(PDFParser(handle))
        info = document.info[0] if document.info else {}
        metadata: dict[str, str] = {}
        iso_dates: dict[str, str] = {}
        for slot, value in info.items():
            rendered = _text(value)
            if rendered is None:
                continue
            metadata[slot] = rendered
            if slot in _DATE_SLOTS:
                stamp = _iso_date(rendered)
                if stamp is not None:
                    iso_dates[slot] = stamp
        return metadata, iso_dates


def _lines(page) -> list[LTTextLine]:
    found: list[LTTextLine] = []
    for element in page:
        if isinstance(element, LTTextContainer):
            found.extend(line for line in element if isinstance(line, LTTextLine))
    # Reading order: top of the page first. pdfminer's y grows upward.
    return sorted(found, key=lambda line: (-line.y1, line.x0))


def _dominant_size(lines) -> float:
    """The page's body size, weighted by CHARACTER COUNT rather than by line.

    A page whose only large line is its title has one heading line and many body
    lines, but a page of large type with a single small footnote has the opposite
    shape. Counting characters is what makes "large relative to this page" mean the
    same thing on both, and it is the number a human reads as the body size.
    """
    sizes = Counter()
    for line in lines:
        for char in line:
            if isinstance(char, LTChar):
                sizes[round(char.size, 1)] += 1
    if not sizes:
        return 0.0
    return sizes.most_common(1)[0][0]


def _page_count(path: Path) -> int:
    """How long the document is, without laying a single page out.

    The count a capped run reports as its `total`. Walking the page tree is the
    cheap half of what `extract_pages` does; the expensive half is the layout
    analysis a ceiling exists to skip.
    """
    with open(path, "rb") as handle:
        return sum(1 for _ in PDFPage.get_pages(handle))


def pdfminer_reader(*, heading_ratio: float = 1.15,
                    margin_fraction: float = 0.08,
                    max_pages: int | None = None,
                    laparams: LAParams | None = None) -> Callable[[Path], P5PdfDocument]:
    """Build the `read_pdf` callable `extractors.dispatch.Readers` takes.

    A factory rather than a bare function so a deployment can tune the two adapter
    policies without editing the module, and so nothing here holds process state.

    `max_pages` is §8.6's page cap. `None` -- the default -- reads the whole
    document, which is what every caller written before the ceiling existed means.
    The NUMBER is not chosen here: `cli.py` is the only file that picks one, and it
    passes this reader in through `macos_readers(read_pdf=...)`, which is the
    override seam that module's docstring exists to offer.

    Layout analysis is the cost, and it is per page. Measured 2026-09-03 on
    `rp2040-datasheet.pdf` (642 pages, vendored inside a user's Arduino libraries):
    the whole document takes 332 seconds, its first 20 pages take 1.3 and yield
    93,531 characters. A ceiling is not a degradation of that read, it is the
    difference between reading a document and re-typesetting a datasheet.
    """
    params = laparams or LAParams()

    def read_pdf(path: Path) -> P5PdfDocument:
        # §2.4: an unreadable file must never be "silently treated as an empty
        # document". Nothing here catches — a raise becomes P5's one `failed` run,
        # which is a true statement about the file; an empty PdfDocument would be a
        # `complete` run with no observations, which is the lie §2.4 names.
        metadata, iso_dates = _metadata(Path(path))
        pages: list[PdfPage] = []

        # pdfminer spells "no limit" as 0, and `None` is this module's spelling of
        # the same thing. Translated here rather than at the boundary so no caller
        # has to know that 0 is a sentinel in one vocabulary and a real count in
        # the other.
        ceiling = 0 if max_pages is None else max_pages

        for number, page in enumerate(
                extract_pages(str(path), laparams=params, maxpages=ceiling), 1):
            lines = _lines(page)
            body_size = _dominant_size(lines)
            height = (page.bbox[3] - page.bbox[1]) or 1.0
            margin = height * margin_fraction
            top, bottom = page.bbox[3] - margin, page.bbox[1] + margin

            text_parts: list[str] = []
            regions: list[Region] = []
            cursor = 0
            heading_ordinal = 0

            for line in lines:
                rendered = line.get_text()
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

                sizes = [c.size for c in line if isinstance(c, LTChar)]
                size = max(sizes) if sizes else 0.0
                zone = "body"
                ordinal = label = None
                if line.y1 > top or line.y0 < bottom:
                    # Bottom or top margin band: a running head or foot. Geometry
                    # only -- a page number and a chapter title look identical here
                    # and both belong to the same zone.
                    zone = "header_footer"
                elif body_size and size >= body_size * heading_ratio:
                    zone = "heading"
                    heading_ordinal += 1
                    ordinal = heading_ordinal          # 1-based, P4 D3
                    label = stripped                   # descriptive only, P4 rule 2

                regions.append(Region(zone=zone, start=start, end=end,
                                      ordinal=ordinal, label=label))
                text_parts.append(rendered)
                cursor += len(rendered)

            pages.append(PdfPage(number=number, text="".join(text_parts),
                                 regions=tuple(regions)))

        # Counted only when a ceiling was set. Without one the read is exhaustive,
        # so the pages produced ARE the total and a second pass over the file would
        # buy a number already in hand. `get_pages` walks the page tree without
        # laying any page out, which is why this is affordable at all.
        total = _page_count(Path(path)) if max_pages is not None else len(pages)

        return P5PdfDocument(metadata=metadata, pages=tuple(pages),
                             iso_dates=iso_dates, pages_total=total,
                             capped=len(pages) < total)

    return read_pdf
