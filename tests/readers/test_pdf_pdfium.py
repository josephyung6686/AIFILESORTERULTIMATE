# tests/readers/test_pdf_pdfium.py
"""The pdfium adapter — the same `PdfDocument` shape, from a library that is not pure
Python.

**Why a second PDF reader exists at all.** `readers/deployment.py` says WHICH
libraries a deployment ships is a deployment fact, and `pdf_pdfminer.py`'s own
docstring names its cost: *"Its known cost is speed on large documents. That is the
trade, and this module is exactly the seam to swap at."* Measured on the owner's own
seventeen PDFs, 50-page ceiling, one interpreter, back to back:

    pdfminer.six (layout)   30.98s   176 pages     5.7 pages/s
    pypdf 4.3.1             16.23s   176 pages    10.8 pages/s
    PyMuPDF 1.28.2           3.74s   176 pages    47.0 pages/s   AGPL-3.0
    pypdfium2 5.13.0         2.02s   176 pages    87.0 pages/s   Apache-2.0/BSD-3

So this is not a swap that trades fidelity for speed, and the tests below are what
say so: every one of them is the pdfminer adapter's own test, asked of this reader,
plus a cross-reader test that puts one file through both and compares the zones. A
reader that is fifteen times faster and loses a heading makes the detector worse, and
the detector is the product's narrowest place.

Nothing is mocked, for the reason `test_pdf_pdfminer.py` gives: the whole point of an
adapter is that the library really behaves the way the shape assumes.
"""
from pathlib import Path

import pytest

pytest.importorskip("pypdfium2", reason="pypdfium2 is an optional `readers` extra")

from evidence_shape.vocabulary import ZONES
from pdf_bytes import build_pdf
from readers.pdf_pdfium import pdfium_reader


@pytest.fixture()
def syllabus(tmp_path: Path) -> Path:
    return build_pdf(tmp_path / "syllabus.pdf")


@pytest.fixture()
def eight_pages(tmp_path: Path) -> Path:
    return build_pdf(tmp_path / "long.pdf", pages=8)


# --------------------------------------------------------------------------
# The shape. Every assertion here is `test_pdf_pdfminer.py`'s, unchanged.
# --------------------------------------------------------------------------

def test_it_fills_the_shape_p5_expects(syllabus):
    from extractors.pdf import PdfDocument, PdfPage

    doc = pdfium_reader()(syllabus)
    assert isinstance(doc, PdfDocument)
    assert len(doc.pages) == 1
    assert isinstance(doc.pages[0], PdfPage)
    assert doc.pages[0].number == 1                     # 1-based, P4 D3


def test_metadata_slot_names_are_the_formats_own_verbatim(syllabus):
    """P4 D7 again. pdfium's `FPDF_GetMetaText` answers a key it is GIVEN and cannot
    enumerate the Info dictionary, so a pure-pdfium reader would silently drop every
    slot outside the nine standard ones. Measured over 91 real PDFs, fifteen of them
    carry a non-standard slot -- `Company`, `SourceModified`, `PTEX.Fullbanner` and,
    on one file, six `MSIP_Label_*` keys, which is a Microsoft sensitivity label on a
    document this product is supposed to be careful with. So the Info dictionary is
    still parsed by the library that can enumerate it."""
    doc = pdfium_reader()(syllabus)
    assert doc.metadata["Title"] == "BUSIB 4300 Syllabus"
    assert doc.metadata["Author"] == "Registrar"
    assert doc.metadata["Creator"] == "hand"
    assert all(isinstance(v, str) for v in doc.metadata.values())


def test_the_pdf_date_syntax_is_rendered_by_the_library_that_knows_it(syllabus):
    doc = pdfium_reader()(syllabus)
    assert doc.iso_dates["CreationDate"].startswith("2026-08-21T12:00:00")
    assert "D:" not in doc.iso_dates["CreationDate"]


def test_zones_come_from_font_and_geometry_not_from_the_words(syllabus):
    """The claim that decides whether this reader may ship. 24pt is a heading
    because it is large relative to the page's dominant size; the 9pt line is a
    footer because it sits in the bottom margin. Both judgements need per-character
    font size and position, which is the reason `pdf_pdfminer.py` gives for choosing
    pdfminer at all -- *"a library that returns only page text cannot produce an
    honest `Region`"*. pdfium exposes both through `FPDFText_GetFontSize` and
    `FPDFText_GetLooseCharBox`, and this test is the evidence."""
    page = pdfium_reader()(syllabus).pages[0]
    zones = {r.zone: page.text[r.start:r.end] for r in page.regions}

    assert "BUSIB 4300 Course Information" in zones["heading"]
    assert "This syllabus covers" in zones["body"]
    assert "page 1 of 1" in zones["header_footer"]


def test_every_zone_is_one_of_p4s_fifteen(syllabus):
    page = pdfium_reader()(syllabus).pages[0]
    assert page.regions
    for region in page.regions:
        assert region.zone in ZONES, f"{region.zone!r} is not one of P4's fifteen"


def test_region_offsets_index_into_that_pages_text(syllabus):
    """§2.2 requires a text offset per observation and P5 slices the page text with
    it. This reader builds its own page text out of pdfium's character stream, so an
    off-by-one here is not hypothetical -- it is the most likely defect in the file."""
    page = pdfium_reader()(syllabus).pages[0]
    for region in page.regions:
        assert 0 <= region.start < region.end <= len(page.text)
        assert page.text[region.start:region.end].strip(), "an empty span"


def test_a_regions_span_is_the_text_it_claims_to_be(syllabus):
    """Stronger than the bounds check above, and the one an off-by-one fails: the
    heading region's slice must BE the heading, not a window near it."""
    page = pdfium_reader()(syllabus).pages[0]
    heading = next(r for r in page.regions if r.zone == "heading")
    assert page.text[heading.start:heading.end] == "BUSIB 4300 Course Information"
    assert heading.label == page.text[heading.start:heading.end]


def test_headings_are_numbered_and_labelled(syllabus):
    page = pdfium_reader()(syllabus).pages[0]
    headings = [r for r in page.regions if r.zone == "heading"]
    assert [h.ordinal for h in headings] == list(range(1, len(headings) + 1))
    assert headings[0].label == "BUSIB 4300 Course Information"


def test_an_encrypted_or_broken_file_raises_rather_than_returning_empty(tmp_path):
    """§2.4: an unreadable file must never be "silently treated as an empty
    document". pdfium reports a load failure as `PdfiumError`; nothing here catches
    it, so P5's catcher turns it into the one `failed` run that is a true statement
    about the file."""
    broken = tmp_path / "broken.pdf"
    broken.write_bytes(b"%PDF-1.4\nnot actually a pdf\n")
    with pytest.raises(Exception):
        pdfium_reader()(broken)


def test_the_adapter_holds_no_product_vocabulary():
    """`src/readers/` fills shapes; it does not decide meaning."""
    import ast
    import inspect

    import readers.pdf_pdfium as module

    tree = ast.parse(inspect.getsource(module))
    strings = {n.value for n in ast.walk(tree)
               if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    for forbidden in ("text_document", "native", "complete", "pdf.text", "possible"):
        assert forbidden not in strings, (
            f"{forbidden!r} is P5's vocabulary and must not be spelled in an adapter")


# --------------------------------------------------------------------------
# §8.6's ceiling, which this reader must honour identically or the run rows lie.
# --------------------------------------------------------------------------

def test_without_a_ceiling_every_page_is_read(eight_pages):
    assert len(pdfium_reader()(eight_pages).pages) == 8


def test_a_ceiling_stops_the_read_at_the_ceiling(eight_pages):
    assert len(pdfium_reader(max_pages=3)(eight_pages).pages) == 3


def test_a_capped_read_still_says_how_many_pages_the_document_has(eight_pages):
    assert pdfium_reader(max_pages=3)(eight_pages).pages_total == 8


def test_a_capped_read_marks_itself_capped(eight_pages):
    assert pdfium_reader(max_pages=3)(eight_pages).capped is True


def test_a_read_that_did_not_reach_the_ceiling_is_not_marked_capped(eight_pages):
    document = pdfium_reader(max_pages=20)(eight_pages)
    assert document.capped is False
    assert len(document.pages) == 8
    assert document.pages_total == 8


def test_a_ceiling_equal_to_the_page_count_is_not_a_partial_read(eight_pages):
    document = pdfium_reader(max_pages=8)(eight_pages)
    assert document.capped is False
    assert document.pages_total == 8


# --------------------------------------------------------------------------
# The two readers, on one file. This is the test that makes the swap reviewable.
# --------------------------------------------------------------------------

def test_the_two_readers_agree_about_the_same_document(syllabus):
    """A swap is only safe if the thing downstream reads does not change.

    P5 stores the page text and P4 stores the zones; the detector reads the zones.
    So the comparison that matters is not "similar text" -- it is the same page
    count, the same zone for each of the three lines, and the same heading LABEL,
    because a heading label is what the recogniser sees.
    """
    pytest.importorskip("pdfminer", reason="the comparison needs both libraries")
    from readers.pdf_pdfminer import pdfminer_reader

    old = pdfminer_reader()(syllabus)
    new = pdfium_reader()(syllabus)

    assert len(new.pages) == len(old.pages)
    assert new.metadata == old.metadata
    assert new.iso_dates == old.iso_dates

    def zoned(document):
        page = document.pages[0]
        return {page.text[r.start:r.end].strip(): r.zone for r in page.regions}

    assert zoned(new) == zoned(old)

    def labels(document):
        return [r.label for r in document.pages[0].regions if r.zone == "heading"]

    assert labels(new) == labels(old)


# --------------------------------------------------------------------------
# The one defect that was invisible: a page whose type is scaled by its matrix.
# --------------------------------------------------------------------------

@pytest.fixture()
def latex_shaped(tmp_path: Path) -> Path:
    """The same syllabus, written the way LaTeX writes one: `1 Tf` and a matrix."""
    return build_pdf(tmp_path / "matrix.pdf", matrix_scaled=True)


def test_a_page_whose_type_is_scaled_by_its_matrix_still_has_a_heading(latex_shaped):
    """The failure this catches lost 31 headings on the owner's own lecture slides
    and left no trace: the text was perfect, the page count was right, the metadata
    was right, and every heading was gone.

    `FPDFText_GetFontSize` reports the size from the TEXT STATE, before the text
    matrix. A PDF may declare a 1-point font and scale it by 24, and every document
    LaTeX produces does exactly that -- so the call returns 1.0 for every character
    on the page and no line is ever large relative to any other. `_size_signal`
    notices a page that declares one size and that size is 1.0, and decides that
    page's zones by the em box's height instead.
    """
    page = pdfium_reader()(latex_shaped).pages[0]
    zones = {r.zone: page.text[r.start:r.end] for r in page.regions}

    assert "BUSIB 4300 Course Information" in zones.get("heading", ""), (
        "the 24pt heading was read as body text: every character on this page "
        f"declares the same size, so the declared size cannot decide. {zones}")
    assert "This syllabus covers" in zones["body"]
    assert "page 1 of 1" in zones["header_footer"]


def test_the_ordinary_page_is_still_decided_by_its_declared_size(syllabus):
    """The negative twin, and the reason `_size_signal` is a choice and not a swap.

    The em box's height is proportional to the FONT's ascent and descent as well as
    to its size, so two faces at one point size give two heights. Deciding every page
    by the box turned 172 headings into 269 across seventeen real files and invented
    74 in a document that has none. This asserts the ordinary page still takes the
    declared size, which is the number pdfminer uses.
    """
    from readers.pdf_pdfium import _lines, _size_signal
    import pypdfium2

    document = pypdfium2.PdfDocument(syllabus)
    try:
        assert _size_signal(_lines(document[0].get_textpage())) == "size"
    finally:
        document.close()
