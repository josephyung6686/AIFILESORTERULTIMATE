# tests/readers/test_pdf_pdfminer.py
"""The pdfminer.six adapter — a real library filling P5's `PdfDocument` shape.

`src/readers/` is a DEPLOYMENT layer, not a part. P5's SPEC says the readers are
parameters and *"a real deployment must choose"*; `src/extractors/` stays stdlib-only
and this is where a third-party library is allowed to live.

Every test here runs against a real PDF built byte by byte in this file, parsed by
real pdfminer. Nothing is mocked: the whole point of an adapter is that the library
actually behaves the way the shape assumes, and a mocked library cannot show that.
"""
from pathlib import Path

import pytest

pytest.importorskip("pdfminer", reason="pdfminer.six is an optional `readers` extra")

from evidence_shape.vocabulary import ZONES
from pdf_bytes import build_pdf
from readers.pdf_pdfminer import pdfminer_reader


@pytest.fixture()
def syllabus(tmp_path: Path) -> Path:
    return build_pdf(tmp_path / "syllabus.pdf")


def test_it_fills_the_shape_p5_expects(syllabus):
    """The adapter's whole job: return P5's dataclass, not pdfminer's objects."""
    from extractors.pdf import PdfDocument, PdfPage

    doc = pdfminer_reader()(syllabus)
    assert isinstance(doc, PdfDocument)
    assert len(doc.pages) == 1
    assert isinstance(doc.pages[0], PdfPage)
    assert doc.pages[0].number == 1                     # 1-based, P4 D3


def test_metadata_slot_names_are_the_formats_own_verbatim(syllabus):
    """P4 D7: the format's own slot names, not product field names. `Title` stays
    `Title` — renaming it here would be P5 inventing a field, which §3.12 forbids."""
    doc = pdfminer_reader()(syllabus)
    assert doc.metadata["Title"] == "BUSIB 4300 Syllabus"
    assert doc.metadata["Author"] == "Registrar"
    assert doc.metadata["Creator"] == "hand"
    assert all(isinstance(v, str) for v in doc.metadata.values()), (
        "pdfminer returns bytes; the adapter decodes, because P5 stores strings")


def test_the_pdf_date_syntax_is_rendered_by_the_library_that_knows_it(syllabus):
    """P4 D8's fourth mechanical transform, and `PdfDocument.iso_dates` exists for it.

    `D:20260821120000+00'00'` is PDF syntax. §3.10 forbids P5 parsing dates out of
    free text, so the reader — which knows the format — renders it and P5 stores it.
    """
    doc = pdfminer_reader()(syllabus)
    assert doc.iso_dates["CreationDate"].startswith("2026-08-21T12:00:00")
    assert "D:" not in doc.iso_dates["CreationDate"]


def test_zones_come_from_font_and_geometry_not_from_the_words(syllabus):
    """`Region`'s own contract: *"the reader says WHAT KIND OF PLACE this is, because
    that is library knowledge (a heading style, a table cell, a footer)"*.

    24pt is a heading because it is large relative to the page's dominant size; the
    9pt line is a footer because it sits in the bottom margin. Neither judgement
    reads the text — that is what keeps zone assignment out of P5 and out of regex.
    """
    page = pdfminer_reader()(syllabus).pages[0]
    zones = {r.zone: page.text[r.start:r.end] for r in page.regions}

    assert "BUSIB 4300 Course Information" in zones["heading"]
    assert "This syllabus covers" in zones["body"]
    assert "page 1 of 1" in zones["header_footer"]


def test_every_zone_is_one_of_p4s_fifteen(syllabus):
    """The adapter may not invent a zone. P4 publishes the vocabulary and adding one
    is a contract revision plus a shape-version bump."""
    page = pdfminer_reader()(syllabus).pages[0]
    assert page.regions
    for region in page.regions:
        assert region.zone in ZONES, f"{region.zone!r} is not one of P4's fifteen"


def test_region_offsets_index_into_that_pages_text(syllabus):
    """§2.2 requires a "text offset" per observation, and P5 slices the page text
    with it. An off-by-one here silently mislabels every span downstream."""
    page = pdfminer_reader()(syllabus).pages[0]
    for region in page.regions:
        assert 0 <= region.start < region.end <= len(page.text)
        assert page.text[region.start:region.end].strip(), "an empty span"


def test_headings_are_numbered_and_labelled(syllabus):
    """`heading` is one of P4's INDEXED segment kinds, so it carries a 1-based
    ordinal; `label` is descriptive only and stays out of the locator (P4 rule 2)."""
    page = pdfminer_reader()(syllabus).pages[0]
    headings = [r for r in page.regions if r.zone == "heading"]
    assert [h.ordinal for h in headings] == list(range(1, len(headings) + 1))
    assert headings[0].label == "BUSIB 4300 Course Information"


def test_an_encrypted_or_broken_file_raises_rather_than_returning_empty(tmp_path):
    """§2.4: an unreadable file must never be "silently treated as an empty
    document". The adapter raises and P5's catcher turns that into one `failed` run —
    returning an empty `PdfDocument` would produce a `complete` run with no
    observations, which is the lie §2.4 names."""
    broken = tmp_path / "broken.pdf"
    broken.write_bytes(b"%PDF-1.4\nnot actually a pdf\n")
    with pytest.raises(Exception):
        pdfminer_reader()(broken)


def test_the_adapter_holds_no_product_vocabulary():
    """`src/readers/` fills shapes; it does not decide meaning. No source type, no
    completeness, no analysis tier, no field name."""
    import ast
    import inspect

    import readers.pdf_pdfminer as module

    tree = ast.parse(inspect.getsource(module))
    strings = {n.value for n in ast.walk(tree)
               if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    for forbidden in ("text_document", "native", "complete", "pdf.text", "possible"):
        assert forbidden not in strings, (
            f"{forbidden!r} is P5's vocabulary and must not be spelled in an adapter")
