# tests/readers/test_readers_doc_cocoa.py
"""The legacy `.doc` reader. Two files on the owner's disk, 1,290 words each, unread.

`.groundtruth/baseline/scorecard.txt`, 2026-09-04: `.doc  0 of 2  0.0%`, recorded
`unsupported`. That word was TRUE -- no reader existed -- and it was not the whole
truth, because this deployment is a macOS deployment and Cocoa reads this format.
`unsupported` is a statement about the DEPLOYMENT, and a deployment that declines to
use a framework it already links is choosing the word rather than earning it.

The two files are `1403.Sample.Exam.1.No.2.w.Key_revised.doc` and
`1403.Sample.Exam2.No.2.Revised.doc` -- General Chemistry practice exams whose labels
want them under `PHYS1403/practice test`. A course code in the first line is what
would put them there and it was on disk, unreachable, the whole time.

A `.doc` is NOT a `.docx`: it is an OLE compound document, so E2's zip-based reader
cannot open it and neither can anything in the standard library.

**Why `NSAttributedString` and not `/usr/bin/textutil`.** The first version of this
reader shelled out to `textutil`, and `tests/integration/test_single_egress.py` was
right to refuse it: `subprocess` is on `NETWORK_MODULES` (added 2026-09-02 --
"Handing the bytes to `curl` is not a future-SDK gap; it is the oldest way out of a
process there is"), and `readers/doc_cocoa.py` is not a provider module. Cocoa is
what `textutil` is a wrapper around, it needs no second process, and it is measurably
STRICTER: `textutil` exits 0 on a truncated OLE document and prints its raw bytes
back, where `NSAttributedString` returns nil and an error.

The fixtures are built by `textutil` -- in the TEST, where a subprocess is an ordinary
thing -- so the reader is tested against a real legacy `.doc` rather than a hand-rolled
OLE blob that would prove only that the blob was hand-rolled.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

pytest.importorskip("AppKit", reason="pyobjc-framework-Cocoa is a `readers` extra")

from readers.doc_cocoa import ConversionFailed, cocoa_doc_reader  # noqa: E402

TEXTUTIL = "/usr/bin/textutil"

read = cocoa_doc_reader()


@pytest.fixture()
def exam(tmp_path: Path) -> Path:
    """A real legacy `.doc`, written by the converter Cocoa sits under."""
    if not Path(TEXTUTIL).exists():
        pytest.skip(f"{TEXTUTIL} builds this fixture; it ships with macOS")
    source = tmp_path / "exam.txt"
    source.write_text("General Chemistry I 1403\n\n"
                      "Sample Exam 1 - No. 2\n\n"
                      "Provide the best possible answer to the question.\n",
                      encoding="utf-8")
    path = tmp_path / "1403.Sample.Exam.1.No.2.doc"
    subprocess.run([TEXTUTIL, "-convert", "doc", "-output", str(path), str(source)],
                   check=True, capture_output=True)
    return path


def test_a_legacy_doc_yields_its_prose(exam):
    document = read(exam)

    assert document is not None, "the reader still declines the format"
    assert "General Chemistry I 1403" in document.text
    assert "Provide the best possible answer" in document.text


def test_the_prose_is_a_document_and_not_a_pile_of_control_words(exam):
    """The failure `readers/text_documents.py` was built to stop, in a new format.

    A `.rtf` once stored `\\rtf1\\ansi\\ansicpg1252` as a letter's prose: "not
    missing information -- false information, stored as complete". A `.doc` read by
    scraping printable runs out of an OLE stream fails the same way, so this asserts
    the absence of the wrapper as well as the presence of the words.
    """
    document = read(exam)
    assert document is not None

    assert "\\rtf" not in document.text
    assert "\x00" not in document.text
    assert document.headings == ()   # Cocoa reports none here, so none is claimed
    assert document.language is None


def test_a_file_that_is_not_an_ole_document_is_unsupported(tmp_path):
    """§2.4's `unsupported`: not this format, so no reader for it exists here.

    The signature is checked BEFORE Cocoa is asked, and that is what separates the
    two answers below: `unsupported` means the bytes are not a legacy Word document
    at all, and `failed` means they are one and could not be read. Without the check
    both would arrive as the same nil.
    """
    path = tmp_path / "renamed.doc"
    path.write_bytes(b"This is a plain text file somebody renamed.\n")

    assert read(path) is None


def test_an_empty_file_is_unsupported_rather_than_an_empty_document(tmp_path):
    path = tmp_path / "empty.doc"
    path.write_bytes(b"")

    assert read(path) is None


def test_a_damaged_word_document_is_failed_and_not_unsupported(tmp_path):
    """§2.4's two outcomes, kept apart. `unsupported` means no reader exists and the
    bytes were never looked at; `failed` means a reader ran and could not. These
    bytes ARE an OLE compound document -- truncated -- so reporting them
    `unsupported` would file a damaged file under "we do not read this format"."""
    path = tmp_path / "truncated.doc"
    path.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 512)

    with pytest.raises(ConversionFailed):
        read(path)


def test_a_truncated_document_is_never_returned_as_prose(tmp_path):
    """The measured reason this reader is Cocoa and not `textutil`.

    Measured 2026-09-04: `head -c 2000 <a real .doc> > trunc.doc` converts through
    `textutil` with exit status 0 and yields 2,579 characters of transcoded binary.
    Recorded `complete`, that is a file the product claims to have read and has not
    -- §2.4's exact prohibition. Cocoa returns nil for the same bytes, which is why
    the raise above is reachable at all.
    """
    path = tmp_path / "truncated.doc"
    path.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 512)

    try:
        result = read(path)
    except ConversionFailed:
        return
    assert result is None or result.text == "", (
        f"a truncated document came back as {result.text[:80]!r} of prose")
