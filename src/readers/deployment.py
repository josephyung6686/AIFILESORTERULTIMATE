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

import sys
from pathlib import Path
from typing import Any, Callable

from extractors.archive import ArchiveManifest
from extractors.dispatch import Readers
from extractors.structured_text import TextDocument

from readers.archive_tarfile import tarfile_reader
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

#: §2.7's explicit Vision settings, as a `config` mapping. It is passed through
#: to `extract_ocr`, stored on the run, and folded into §3.4's cache key -- so
#: changing a setting here makes stale OCR results fall out of the cache, which is
#: the whole reason these are configuration rather than constructor arguments.
#:
#: **`languages` IS NOT HERE ANY MORE, and `104` §18.2 gap 19 is why.** It read
#: `["en-US"]`, which is a list this deployment typed about a corpus it had not seen,
#: and §2.7 asks for "appropriate language support INCLUDING CJK WHERE REQUIRED".
#: The owner's own disk holds Chinese-titled documents whose OCR came back empty.
#: The third persisted field is still recorded -- `macos_readers` asks
#: `recognition_languages` for Vision's OWN published set and puts THAT in
#: `ocr_config` -- so the run says which languages were available, and no list in
#: this product decides it. Every stored OCR fingerprint changes with this, which is
#: exactly what a cache key exists to do when the configuration really did change.
#: The classification pass uses Vision's fast level. The engine still accepts
#: `accurate`; a later pass that needs it passes that level in `config`. Fast is
#: the level Apple documents as the smaller model. Label agreement between the
#: two levels is not measured on this machine.
VISION_CONFIG: dict[str, Any] = {
    "dpi": 200,
    "recognition_level": "fast",
}


def _no_reader(*args: Any, **kwargs: Any) -> None:
    """This deployment ships no library for the format (§2.4 `unsupported`)."""
    return None


def _archive_reader(*, zip_reader: Callable[[Path], ArchiveManifest],
                    tar_reader: Callable[[Path], ArchiveManifest],
                    ) -> Callable[[Path], ArchiveManifest]:
    """One `read_manifest` for both archive families router.py now sends it.

    `104` §18.2 gap 14, item 2. `extract_archive` takes exactly one injected
    `read_manifest`; the router routes `zip` and the four tar tokens to the same
    `archive.manifest` handler, so the two per-family readers need a caller that
    picks between them. BY BYTES, never by the path's extension -- gap 21's rule
    applies here as much as it does at the router: `PK\x03\x04` is ZIP's own
    four-byte magic, read directly rather than re-derived from
    `readers.signatures` (that module answers a ROUTING question and importing it
    from a reader would be the reader asking the router's own question a second
    way); anything else is handed to `tarfile`'s own `mode="r:*"` auto-detection,
    the same one `readers.signatures._tar_format` already confirmed at routing
    time. Four bytes are read and nothing else -- no member of either archive is
    opened by this function.
    """
    def read_manifest(path: Path) -> ArchiveManifest:
        with open(path, "rb") as handle:
            head = handle.read(4)
        if head.startswith(b"PK\x03\x04"):
            return zip_reader(path)
        return tar_reader(path)

    return read_manifest


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
                  ocr_sparse_page_words: int | None = None,
                  ocr_image_long_edge: int | None = None,
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
    # Imported HERE and not at module scope, and only on macOS. `readers.ocr_vision`
    # pulls in Apple's Vision and Quartz frameworks. On darwin that cost is paid
    # when a scan is wired, not when `cli` is imported. On Linux those frameworks
    # do not exist: importing them refused every scan, including a folder of text
    # files, with `No module named 'Quartz'`. OCR and legacy `.doc` are then
    # absent (`ocr_engine is None`, `read_doc is None`), which §2.4 calls
    # `unsupported`. A missing wheel on darwin is not caught: the import raises
    # by name.
    if sys.platform == "darwin":
        from readers.ocr_vision import recognition_languages, vision_ocr
        ocr_engine = vision_ocr()
        ocr_languages = list(recognition_languages(
            recognition_level=VISION_CONFIG["recognition_level"]))
        read_doc = cocoa_doc_reader()
    else:
        ocr_engine = None
        ocr_languages = []
        read_doc = None

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
        "read_text_document": stdlib_text_document_reader(read_doc=read_doc),
        "ocr_engine": ocr_engine,
        # §2.7's third persisted field, asked of the recogniser rather than typed.
        # It is asked AT THE CONFIGURED LEVEL because Vision publishes the set per
        # level, and it is asked HERE rather than inside the engine so that the run's
        # `config` -- which `extract_ocr` stores verbatim and §3.4 fingerprints --
        # records the languages that were actually available on this machine.
        "ocr_config": {**VISION_CONFIG,
                       "languages": ocr_languages,
                       "page_cap": ocr_page_ceiling,
                       "time_limit_seconds": ocr_seconds_per_file,
                       # `ocr_policy.sparse_pages`' floor: a page with fewer words
                       # than this has no text layer and is read. None keeps the
                       # bare rule (a page with no words at all); the product
                       # passes `cli.OCR_SPARSE_PAGE_WORDS`. SPEC OQ1's deferred
                       # configuration value, held here and not in the policy.
                       "sparse_page_words": ocr_sparse_page_words,
                       # None leaves a loose image at its own pixel size. The
                       # product passes `cli.OCR_IMAGE_LONG_EDGE_PX`.
                       **({} if ocr_image_long_edge is None else
                          {"max_long_edge_px": ocr_image_long_edge})},
        "read_docx": python_docx_reader(),
        # §2.5's manifest, from the standard library. No ceiling: how many members
        # are worth listing is a deployment budget, and this deployment would
        # rather carry a long manifest than a truncated one it has to explain.
        #
        # `104` §18.2 gap 14, item 2: TWO READERS NOW, not one -- the tar family
        # beside zip -- so the single `read_manifest` key `extract_archive` takes
        # is `_archive_reader`'s dispatch between them, by the file's own first
        # bytes.
        "read_manifest": _archive_reader(
            zip_reader=zipfile_reader(), tar_reader=tarfile_reader()),
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
        #
        # AND IT CARRIES EXIF NOW (`104` §18.2 gap 18). The sentence here used to
        # read "This reader carries no EXIF, so §2.6's tier-1 band stays
        # unavailable", which meant a photograph could not be "stated by its capture
        # metadata" anywhere in the product. The reader reaches ImageIO through
        # `Quartz` -- already shipped for Vision above, so nothing is added -- and
        # HEIC, HEIF, AVIF, TIFF and BMP have branches, which §2.6 requires by name
        # for the first of them.
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
