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

from readers.archive_zipfile import manifest_marker_recognizer, zipfile_reader
from readers.capture import make_dimension_signal, make_filename_pattern
from readers.doc_cocoa import cocoa_doc_reader
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
                  spreadsheet_cell_ceiling: int,
                  ocr_page_ceiling: int, ocr_seconds_per_file: int,
                  **overrides: Any) -> Readers:
    """The wired `Readers`. Pass `**overrides` to swap any single reader.

    `overrides` is how the PDF library gets swapped without touching this module --
    `macos_readers(find_structured_strings=..., read_pdf=other_reader())` -- which is
    the seam the injected-reader design exists to provide.

    **`spreadsheet_cell_ceiling` is REQUIRED and has no default.** It is §8.6's kind
    of number -- a ceiling that trades completeness for cost -- and this deployment
    is not where such a number is chosen. `cli.py` is the sole composition root and
    holds every one of them beside the measurement that earned it; a default here
    would be a second ceiling nobody tuned, quietly governing behaviour while the
    documented one governed nothing. Absent means refuse, never guess.

    It is a plain argument rather than an override of `read_long_tail` because the
    reader it configures is THIS module's choice: swapping the whole reader out is
    what `overrides` is for, and handing a ceiling to the one already wired is not
    the same act. `SENSOR_RATIO_TOLERANCE` above is the shape this deliberately does
    NOT take -- a number living in `readers/` with a comment explaining that it
    should not.

    **`ocr_page_ceiling` and `ocr_seconds_per_file` are required on the same terms**,
    and they are §8.6's `ocr.max_pages_per_file` and `ocr.max_time_per_file`. They go
    into `ocr_config` rather than into the engine's constructor because that mapping
    is stored on the run and folded into §3.4's cache key: a ceiling outside the key
    would let two runs at different bounds look identical to the cache, so raising
    the limit would leave the capped results from the lower one in place. `vision_ocr`
    has read `page_cap` and `time_limit_seconds` since it was written; until now
    nothing supplied either, so §8.6's most expensive operation ran unbounded.
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
        # `read_doc` WAS EMPTY, and §2.4's `unsupported` is a statement about this
        # module: "no extractor exists for this format in this deployment". A `.doc`
        # is an OLE compound document -- the format `.docx` replaced -- so
        # `text_documents.py` cannot open one and neither can `python_docx_reader`
        # above, which opens a ZIP of XML parts. Measured over the owner's 199-file
        # corpus on 2026-09-04: `.doc  0 of 2  0.0%`, two General Chemistry practice
        # exams of 1,290 words each, recorded `unsupported` while AppKit -- already
        # linked here for Vision and Quartz -- reads the format.
        #
        # `readers/doc_cocoa.py` says why it is Cocoa and not `/usr/bin/textutil`:
        # `subprocess` is on `test_single_egress.NETWORK_MODULES` and a reader is not
        # a provider module. The in-process route is also the stricter one.
        "read_text_document": stdlib_text_document_reader(
            read_doc=cocoa_doc_reader()),
        "ocr_engine": vision_ocr(),
        "ocr_config": {**VISION_CONFIG,
                       "page_cap": ocr_page_ceiling,
                       "time_limit_seconds": ocr_seconds_per_file},
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
        #
        # AND IT NOW ARRIVES WITH A CEILING. Reading every spreadsheet was the fix;
        # reading every CELL of every spreadsheet without a limit was the cost of it.
        # Measured on the owner's 199-file corpus, 2026-09-04: spreadsheet cells were
        # 58% of all text units and 3.5% of all text. A cell is two database rows, so
        # a data export outweighs everything a person has written. `max_cells` bounds
        # that, and the run says `capped` when it bites.
        "read_long_tail": stdlib_long_tail_reader(
            max_cells=spreadsheet_cell_ceiling),
        # §2.6's container header, from the standard library. Wired 2026-08-31: it
        # was `_no_reader`, so `extract_image` returned `unsupported` on its second
        # line and the two catalogue-fed keywords below were never called at all.
        # This reader carries no EXIF, so §2.6's tier-1 band stays unavailable --
        # `readers/image_headers.py` says why that is a stated limit and not a trap.
        "read_image": header_image_reader(),
        # ANSWERS NOW, and `104` §18.2 gap 17 is why. It was `lambda names: ()` --
        # reached on every archive, returning nothing on every archive -- and its
        # stated reason was that §2.5's marker set is Deferred in P5's SPEC, so "a
        # list invented here would be this deployment authoring the open half of
        # somebody else's section". True, and it overlooked that no list needs
        # inventing for §2.5's FIRST class: `text_documents.filename_marker_kind`
        # is catalogue 05, already shipped, already deciding what a package
        # manifest and a repository marker are for every loose file on the disk.
        # `manifest_marker_recognizer` asks that same table about a member path and
        # re-kinds its answer to §2.5's vocabulary; §2.5's `document name` class
        # stays deferred, and that module says at length why and what it costs.
        "recognize_markers": manifest_marker_recognizer(),
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
