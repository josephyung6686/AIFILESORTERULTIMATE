# tests/readers/test_pdf_page_ceiling.py
"""§8.6's page cap, for PDFs.

`extractors/ocr.py:206` has read a capped page range honestly since it was written:
`completeness="capped" if output.capped else "complete"`, with
`coverage("pages", pages_processed, pages_total)` beside it. `OcrOutput`'s own
docstring names where that comes from -- *"the engine was given section 8.6's page
cap and run-time limits and reports that it reached one"*.

The PDF path never got one. `extract_pdf` reported `coverage("pages", pages, pages)`
-- processed and total read off the SAME number -- so a document could only ever be
`complete`, and there was no shape in which a partial read could be stated.

Measured on a real corpus (2026-09-03): one 642-page `rp2040-datasheet.pdf`, vendored
inside `~/Documents/Arduino/libraries/`, took 332 seconds of a 705-second run over 639
files. The first 20 pages of that same file take 1.3 seconds and yield 93,531
characters. The cost is pages, and nothing needed page 500 to know what the document
was.

The danger this file exists to rule out is not slowness, it is a LIE: a ceiling that
reports `complete` would claim a 642-page datasheet had been read in full, which is
exactly the silent-empty-document failure §2.4 forbids. So every test below asserts
the honesty half, not just the stopping half.
"""
from pathlib import Path

import pytest

pytest.importorskip("pdfminer", reason="pdfminer.six is an optional `readers` extra")

from pdf_bytes import build_pdf
from readers.pdf_pdfminer import pdfminer_reader


@pytest.fixture()
def eight_pages(tmp_path: Path) -> Path:
    return build_pdf(tmp_path / "long.pdf", pages=8)


# --------------------------------------------------------------------------
# The reader half: does it stop, and does it say so?
# --------------------------------------------------------------------------

def test_without_a_ceiling_every_page_is_read(eight_pages):
    """The control. A reader given no ceiling behaves exactly as it always did."""
    document = pdfminer_reader()(eight_pages)
    assert len(document.pages) == 8


def test_a_ceiling_stops_the_read_at_the_ceiling(eight_pages):
    document = pdfminer_reader(max_pages=3)(eight_pages)
    assert len(document.pages) == 3


def test_a_capped_read_still_says_how_many_pages_the_document_has(eight_pages):
    """The honesty half. Three were read; the document is still eight long."""
    document = pdfminer_reader(max_pages=3)(eight_pages)
    assert document.pages_total == 8


def test_a_capped_read_marks_itself_capped(eight_pages):
    assert pdfminer_reader(max_pages=3)(eight_pages).capped is True


def test_a_read_that_did_not_reach_the_ceiling_is_not_marked_capped(eight_pages):
    """The negative twin. A ceiling ABOVE the page count is not a partial read.

    Without this, `capped=True` could be hard-wired to "a ceiling was configured"
    and every test above would still pass while the product told a person their
    four-page bank statement had been truncated.
    """
    document = pdfminer_reader(max_pages=20)(eight_pages)
    assert document.capped is False
    assert len(document.pages) == 8
    assert document.pages_total == 8


def test_a_ceiling_equal_to_the_page_count_is_not_a_partial_read(eight_pages):
    """The boundary. Eight pages read under a ceiling of eight is complete."""
    document = pdfminer_reader(max_pages=8)(eight_pages)
    assert document.capped is False
    assert document.pages_total == 8


# --------------------------------------------------------------------------
# The extractor half: does the RUN carry the truth into the database?
# --------------------------------------------------------------------------

def _run_for(document):
    """`extract_pdf`'s run row for an already-read document."""
    from extractors.pdf import extract_pdf
    from extractors.safety import SafetyPolicy

    file_row = {"file_id": "f1",
                "content_hash": "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c9"
                                "9f077c3583b39b48aebb124",
                "filename": "long.pdf"}
    result = extract_pdf(
        file_row=file_row, path=Path("/corpus/long.pdf"),
        policy=SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False),
        read_pdf=lambda path: document,
        find_structured_strings=lambda text: (),
        now="2026-09-03T00:00:00+00:00", context_window=40)
    return result.run


def test_a_capped_document_is_recorded_as_capped_not_complete(eight_pages):
    run = _run_for(pdfminer_reader(max_pages=3)(eight_pages))
    assert run["completeness"] == "capped"


def test_a_capped_run_reports_the_pages_it_read_against_the_pages_there_are(
        eight_pages):
    """`coverage` read both numbers off `len(document.pages)`, so it could not
    state a partial read even in principle. Three of eight is the whole point."""
    run = _run_for(pdfminer_reader(max_pages=3)(eight_pages))
    assert run["coverage"] == {"processed": 3, "total": 8, "units": "pages"}


def test_an_uncapped_run_is_still_recorded_as_complete(eight_pages):
    """The negative twin for the run row."""
    run = _run_for(pdfminer_reader()(eight_pages))
    assert run["completeness"] == "complete"
    assert run["coverage"] == {"processed": 8, "total": 8, "units": "pages"}
