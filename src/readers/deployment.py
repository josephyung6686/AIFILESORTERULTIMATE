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

from readers.archive_zipfile import zipfile_reader
from readers.capture import make_dimension_signal, make_filename_pattern
from readers.docx_python_docx import python_docx_reader
from readers.image_headers import header_image_reader
from readers.long_tail_stdlib import stdlib_long_tail_reader
from readers.pdf_pdfminer import pdfminer_reader
from readers.text_documents import stdlib_text_document_reader

#: Catalogue 03's proposed tolerance, and the only number this module chooses beyond
#: Vision's. It is a **proposal**, recorded as one in the catalogue's own
#: `unc-tolerance-value`: 0.5 % relative clears the widest real sensor deviation found
#: (the Pixel-class 4080x3072, 0.39 % off nominal 4:3) with margin, while staying far
#: inside the 6.7 % gap between 4:3 and 5:4 -- and it has never been measured against
#: a real corpus. It lives here rather than in `src/readers/library/` because the
#: catalogue says of it "it is a number, so it must not live inside `src/extractors/`
#: either", and rather than being defaulted inside `make_dimension_signal` because a
#: number with a default is a number nobody reviewed. NEEDS JOSEPH.
SENSOR_RATIO_TOLERANCE: float = 0.005

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
    # Imported HERE and not at module scope. `readers.ocr_vision` pulls in
    # Apple's Vision and Quartz frameworks, which cost 4.6s of `import cli`'s
    # 7.3s warm and about 75 of 77 seconds cold -- before one character of
    # output. A person typing `--list-situations`, or any run over a corpus with
    # no image in it, waited all of that for a framework their run never used.
    # The module still imports it eagerly relative to THIS call, so nothing about
    # when OCR is available changes; only the moment the cost is paid does.
    from readers.ocr_vision import vision_ocr

    wired: dict[str, Any] = {
        "read_pdf": pdfminer_reader(),
        # Was `read_text_file`, which decoded any of §2.9's eight text formats as
        # UTF-8 and returned the bytes. Right for `.txt` and for source code, and
        # measurably wrong for the rest: a `.rtf` stored its own control words as
        # the document's prose, a `.html` stored its `<script>` and `<style>`
        # bodies, and a `.md` yielded no headings at all. `readers/text_documents.py`
        # reads each format as the format it is; `read_text_file` below is kept
        # because it is still the whole of the plain-text answer.
        "read_text_document": stdlib_text_document_reader(),
        "ocr_engine": vision_ocr(),
        "ocr_config": dict(VISION_CONFIG),
        "read_docx": python_docx_reader(),
        # §2.5's manifest, from the standard library. No ceiling: how many members
        # are worth listing is a deployment budget, and this deployment would
        # rather carry a long manifest than a truncated one it has to explain.
        "read_manifest": zipfile_reader(),
        # WAS `_no_reader`, and that one line was the largest single loss of
        # information measured in this product. §2.9 gives spreadsheets,
        # presentations, email, calendar, contacts and audio/video a field list
        # each; every one of those files recorded `unsupported` with
        # `coverage {"processed": 0, "total": 1}` -- the bytes never looked at --
        # and nothing downstream could tell that from an empty file. Measured over
        # a real folder on 2026-09-03, seven of seventeen files yielded zero
        # observations for this reason, `grades.csv` among them.
        #
        # `readers/long_tail_stdlib.py` reads eight of those formats with the
        # standard library and returns `None` for the rest, which keeps §2.4's
        # `unsupported` meaning what it says for `.xls`, `.ppt`, `.msg`, `.ods`,
        # `.odp`, `.numbers` and `.mp3`.
        "read_long_tail": stdlib_long_tail_reader(),
        # §2.6's container header, from the standard library. Wired 2026-08-31: it
        # was `_no_reader`, so `extract_image` returned `unsupported` on its second
        # line and the two catalogue-fed keywords below were never called at all.
        # This reader carries no EXIF, so §2.6's tier-1 band stays unavailable --
        # `readers/image_headers.py` says why that is a stated limit and not a trap.
        "read_image": header_image_reader(),
        # REACHED NOW, and still empty -- for a reason that has changed. It used to
        # be unreachable because `read_manifest` was unwired. It is now reached on
        # every archive and answers `()` because §2.5's marker set is DEFERRED in
        # P5's SPEC ("Archive recognizable markers beyond the above | The marker
        # set"): which filenames count as a source-code manifest is unsettled, and
        # a list invented here would be this deployment authoring the open half of
        # somebody else's section. The member paths themselves are already recorded
        # by `extract_archive`, so nothing is lost but the labelling.
        "recognize_markers": lambda names: (),
        # REACHED NOW. Both are catalogues 02, 03 and 04, finished on 2026-08-20 in
        # `planning/deferred-catalogues/` and read by nothing until 2026-08-31:
        # `grep -rn "deferred-catalogues" src` returned nothing at all, so a macOS
        # screenshot was not recognised as a screen capture on any path, including
        # under the situation literally named `photos.screenshot-captures`. The rows
        # now ship in `readers/library/` and `readers/capture.py` compiles them; the
        # catalogues' own `injection` fields are why they live here and never under
        # `src/extractors/`, where Task 20 fails the build by runtime introspection.
        "dimension_signal": make_dimension_signal(
            tolerance=SENSOR_RATIO_TOLERANCE),
        "filename_pattern": make_filename_pattern(),
        "find_structured_strings": find_structured_strings,
    }
    wired.update(overrides)
    return Readers(**wired)
