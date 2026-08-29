# src/readers/deployment.py
"""One `Readers` for a macOS deployment: pdfminer.six for PDFs, Apple Vision for OCR.

This is the object that gets passed into `run_wave2`. It is assembled here rather
than in the caller because WHICH libraries a deployment ships is a deployment fact,
and `src/extractors/` is not allowed to know it.

**A format with no library returns `None`, never an exception.** §2.4 gives those two
outcomes different names: `unsupported` means no reader exists and the bytes were
never looked at; `failed` means a reader ran and raised. A deployment that ships PDF
and not DOCX is the ordinary case, and recording its .docx files as unreadable would
report a missing library as a corrupt corpus.

**`find_structured_strings` has no default and is required.** §2.2 names the classes
-- *"URLs, email addresses, DOI values, citations, identifiers"* -- and P5's SPEC puts
the PATTERNS in the Deferred table: they are not settled, so no pattern lives in
`src/extractors/` and none is invented here either. A default returning `()` would be
worse than no default: it silently claims a file contains no URLs, no emails and no
identifiers, and every downstream count would agree with it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from extractors.dispatch import Readers
from extractors.structured_text import TextDocument

from readers.ocr_vision import vision_ocr
from readers.pdf_pdfminer import pdfminer_reader

#: §2.7's three explicit Vision settings, as a `config` mapping. It is passed through
#: to `extract_ocr`, stored on the run, and folded into §3.4's cache key -- so
#: changing a setting here makes stale OCR results fall out of the cache, which is
#: the whole reason these are configuration rather than constructor arguments.
VISION_CONFIG: dict[str, Any] = {
    "languages": ["en-US"],
    "dpi": 200,
    "recognition_level": "accurate",
}


def _no_reader(*args: Any, **kwargs: Any) -> None:
    """This deployment ships no library for the format (§2.4 `unsupported`)."""
    return None


def read_text_file(path: Path) -> TextDocument:
    """Plain text, with the one thing that is genuinely format knowledge: encoding.

    No heading detection. Markdown's `#` really is library knowledge and a Markdown
    reader could legitimately supply headings, but this one does not claim to be a
    Markdown reader, and inventing a heading zone from a character would be the exact
    thing `Region`'s contract forbids a caller from doing.
    """
    return TextDocument(text=Path(path).read_text(encoding="utf-8", errors="replace"))


def macos_readers(*, find_structured_strings: Callable[[str], tuple],
                  **overrides: Any) -> Readers:
    """The wired `Readers`. Pass `**overrides` to swap any single reader.

    `overrides` is how the PDF library gets swapped without touching this module --
    `macos_readers(find_structured_strings=..., read_pdf=other_reader())` -- which is
    the seam the injected-reader design exists to provide.
    """
    wired: dict[str, Any] = {
        "read_pdf": pdfminer_reader(),
        "read_text_document": read_text_file,
        "ocr_engine": vision_ocr(),
        "ocr_config": dict(VISION_CONFIG),
        # No library shipped for these yet -- `None` is §2.4's `unsupported`.
        "read_docx": _no_reader,
        "read_long_tail": _no_reader,
        "read_manifest": _no_reader,
        "read_image": _no_reader,
        # Reached only after their own reader returned a record, which cannot happen
        # while these formats are unwired. They are the honest "no signal" answer and
        # must be replaced along with the reader they belong to.
        "recognize_markers": lambda names: (),
        "dimension_signal": lambda width, height: None,
        "filename_pattern": lambda name: None,
        "find_structured_strings": find_structured_strings,
    }
    wired.update(overrides)
    return Readers(**wired)
