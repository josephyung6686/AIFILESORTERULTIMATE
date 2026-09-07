# tests/readers/test_readers_doc_reader_is_wired.py
"""The `.doc` reader is not just written -- the deployment's `Readers` reaches it.

`84` §5 names this project's dominant defect: a part that is complete, well-tested and
connected to nothing. `readers/doc_cocoa.py` is exactly that shape. It has its own
passing file of tests and would keep passing forever with nothing on the reading path
ever calling it -- the two `.doc` files on the owner's disk would stay at `0 of 2` and
the suite would stay green.

That is not hypothetical here. `read_long_tail` sat wired to `_no_reader` while
`readers/long_tail_stdlib.py` existed and passed its own tests, and seven of seventeen
files in a real folder yielded zero observations for a week because of it.

So this asserts the WIRING, by building the deployment's real `Readers` and handing it
a real legacy `.doc`.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

pytest.importorskip("pdfminer", reason="pdfminer.six is an optional `readers` extra")
pytest.importorskip("Vision", reason="pyobjc-framework-Vision is a `readers` extra")
pytest.importorskip("Quartz", reason="pyobjc-framework-Quartz is a `readers` extra")
pytest.importorskip("AppKit", reason="pyobjc-framework-Cocoa is a `readers` extra")

from readers.deployment import macos_readers  # noqa: E402

#: A cell ceiling high enough that no fixture here reaches it. `macos_readers`
#: refuses to pick one -- it is a policy and `cli.SPREADSHEET_CELL_CEILING` is
#: where the product picks it -- so every caller states the one it means.
CELL_CEILING_UNREACHED = 1_000_000

#: OCR ceilings high enough that no fixture here reaches either. Same terms as
#: the cell ceiling above: `macos_readers` refuses to pick §8.6's numbers, so
#: every caller states the ones it means.
OCR_CEILING_UNREACHED = 1_000_000

TEXTUTIL = "/usr/bin/textutil"


@pytest.fixture()
def exam(tmp_path: Path) -> Path:
    if not Path(TEXTUTIL).exists():
        pytest.skip(f"{TEXTUTIL} builds this fixture; it ships with macOS")
    source = tmp_path / "exam.txt"
    source.write_text("General Chemistry I 1403 Dr. Beer\n", encoding="utf-8")
    path = tmp_path / "1403.Sample.Exam.1.No.2.w.Key_revised.doc"
    subprocess.run([TEXTUTIL, "-convert", "doc", "-output", str(path), str(source)],
                   check=True, capture_output=True)
    return path


def test_the_deployments_text_reader_reads_a_legacy_doc(exam):
    readers = macos_readers(find_structured_strings=lambda text: (),
                            spreadsheet_cell_ceiling=CELL_CEILING_UNREACHED,
        ocr_page_ceiling=OCR_CEILING_UNREACHED,
        ocr_seconds_per_file=OCR_CEILING_UNREACHED)

    document = readers.read_text_document(exam)

    assert document is not None, (
        "`macos_readers` hands `read_text_document` no `read_doc`, so every legacy "
        "Word document on the disk is back to §2.4's `unsupported`.")
    assert "General Chemistry I 1403" in document.text


def test_wiring_it_changed_nothing_for_the_formats_that_already_read(tmp_path):
    """A socket filled badly is worse than one left empty."""
    readers = macos_readers(find_structured_strings=lambda text: (),
                            spreadsheet_cell_ceiling=CELL_CEILING_UNREACHED,
        ocr_page_ceiling=OCR_CEILING_UNREACHED,
        ocr_seconds_per_file=OCR_CEILING_UNREACHED)
    (tmp_path / "syllabus.txt").write_text("PHYS 1403\n", encoding="utf-8")
    (tmp_path / "notes.md").write_text("# Lab 4\n\nAir track.\n", encoding="utf-8")

    assert readers.read_text_document(tmp_path / "syllabus.txt").text == "PHYS 1403\n"
    assert readers.read_text_document(tmp_path / "notes.md").headings != ()


def test_the_override_seam_still_wins_over_the_wired_reader(tmp_path):
    """`macos_readers(**overrides)` is the seam the injected-reader design exists to
    provide, and a wired default that could not be replaced would close it."""
    readers = macos_readers(find_structured_strings=lambda text: (),
                            spreadsheet_cell_ceiling=CELL_CEILING_UNREACHED,
        ocr_page_ceiling=OCR_CEILING_UNREACHED,
        ocr_seconds_per_file=OCR_CEILING_UNREACHED,
                            read_text_document=lambda path: None)

    assert readers.read_text_document(tmp_path / "anything.txt") is None
