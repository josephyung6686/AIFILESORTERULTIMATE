# tests/readers/test_docx_python_docx.py
"""`read_docx` backed by python-docx, against files it actually wrote.

Real `.docx` bytes rather than a stub: the whole point of a reader is what a
library does with a real file, and a fake `read_docx` proves only that the fake
agrees with itself. `65` and `69` both record that every defect this project has
found came from running over real files, and none from the suite.
"""
from __future__ import annotations

import pytest

docx_lib = pytest.importorskip("docx")

from readers.docx_python_docx import python_docx_reader


@pytest.fixture
def written(tmp_path):
    """One document carrying every zone this reader claims to tell apart."""
    document = docx_lib.Document()
    document.core_properties.title = "Motion to Compel"
    document.core_properties.author = "Mara Ellison"
    document.add_heading("Background", level=1)
    document.add_paragraph("The deposition was noticed for PHYS 1401.")
    document.add_heading("Argument", level=2)
    document.add_paragraph("Production remains incomplete.")
    table = document.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Item"
    table.cell(0, 1).text = "Status"
    table.cell(1, 0).text = "Exhibit A"
    table.cell(1, 1).text = "Withheld"
    path = tmp_path / "motion.docx"
    document.save(path)
    return path


def test_a_real_docx_is_read_into_the_document_p5_expects(written):
    read = python_docx_reader()
    document = read(written)

    assert document is not None, (
        "python-docx is installed and this deployment wired `_no_reader`, so "
        "every .docx on a person's disk recorded `unsupported` -- a missing "
        "library reported where there is none")
    assert document.core_properties["title"] == "Motion to Compel"
    assert document.core_properties["author"] == "Mara Ellison"


def test_headings_are_a_zone_and_body_text_is_not(written):
    document = python_docx_reader()(written)
    zones = {paragraph.text: paragraph.zone for paragraph in document.paragraphs}

    assert zones["Background"] == "heading"
    assert zones["Argument"] == "heading"
    assert zones["The deposition was noticed for PHYS 1401."] == "body"
    assert zones["Production remains incomplete."] == "body"


def test_a_paragraph_carries_the_heading_ancestry_above_it(written):
    document = python_docx_reader()(written)
    by_text = {paragraph.text: paragraph for paragraph in document.paragraphs}

    # A heading paragraph's own last segment IS that heading (P5 `docx.py`).
    assert by_text["Background"].heading_path[-1][1] == "Background"
    # Body under a heading hangs off it.
    assert [label for _, label in
            by_text["The deposition was noticed for PHYS 1401."].heading_path
            ] == ["Background"]
    # A level-2 heading nests under the level-1 above it.
    assert [label for _, label in by_text["Argument"].heading_path] == [
        "Background", "Argument"]


def test_table_cells_are_read_with_their_column_header(written):
    document = python_docx_reader()(written)
    body = {(cell.row, cell.column): cell for cell in document.cells}

    # 1-based throughout: P4 D3 refuses a container-path index of 0.
    assert body[(2, 1)].text == "Exhibit A"
    assert body[(2, 1)].column_header == "Item"
    assert body[(2, 2)].column_header == "Status"
    assert min(cell.row for cell in document.cells) == 1
    assert min(cell.column for cell in document.cells) == 1


def test_paragraph_indexes_are_the_order_they_appear_in(written):
    document = python_docx_reader()(written)
    indexes = [paragraph.index for paragraph in document.paragraphs]

    assert indexes == sorted(indexes), "P4 anchors spans to a paragraph ordinal"
    assert len(set(indexes)) == len(indexes), "two paragraphs cannot share an anchor"
    assert min(indexes) == 1, (
        "P4 D3 refuses a container-path index of 0, and a 0 here made the whole "
        "extraction `failed` -- a real document reported as a damaged one")
