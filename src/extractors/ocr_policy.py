# src/extractors/ocr_policy.py
"""When OCR may run (sections 2.2 and 2.7). One signal, and no quality heuristic.

Section 2.2 requires the system to distinguish a PDF with NO text layer from one with
a BROKEN text layer:

    text_layer_absent   no text at all      route DIRECTLY to OCR
    text_layer_broken   text, but the stored evidence yields no usable facts
                                            TARGETED OCR, and only after P6 says so
    text_layer_usable   text and facts      no OCR

The state is not an observation and not a run field. "No text layer" is an ABSENCE,
and P4 is explicit that an extractor "may not write an 'EXIF absent', 'no text layer'
or 'metadata stripped' observation; the run record already says it, and an absence
written as evidence is a value P6 can rank." Section 2.2's requirement that the two be
DISTINGUISHED is met by the two paths behaving differently.

Section 2.2 forbids the alternative trigger outright: "The system should not use
unreliable global language-quality checks that incorrectly punish multilingual or
mathematics-heavy documents", and section 2.7 repeats it - not "because a broad
quality heuristic says the text looks unusual". So the only input about a non-empty
text layer is P6's `no_usable_facts` verdict (M11), injected with no default, and the
threshold behind that verdict is SPEC Open question 1 and is not answered here.
"""
from __future__ import annotations

import re

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from extractors.sink import ExtractionResult

#: Section 2.2's own three.
TEXT_LAYER_STATES: tuple[str, str, str] = (
    "text_layer_usable", "text_layer_absent", "text_layer_broken",
)


@dataclass(frozen=True)
class OcrDecision:
    """Whether E6 may run, and on what footing.

    `state` is section 2.2's text-layer state for a document and is None for an
    image, which has no text layer to have a state about.
    """
    state: str | None
    run_ocr: bool
    targeted: bool
    reason: str


def _has_text(result: ExtractionResult) -> bool:
    """Did this run store any text at all? Reads the run's own units, nothing else."""
    return any(unit["text"].strip() for unit in result.text_units)


def direct_document_ocr_needed(*, result: ExtractionResult) -> bool:
    """Whether a PDF must go directly to OCR before P6 can evaluate evidence.

    A non-empty text layer is deliberately left alone AT THE FILE LEVEL.  Whether its
    stored evidence yields usable facts is knowable only after P6 completes, through
    :func:`document_ocr_decision`.  `sparse_pages` below is the per-page reading of
    the same rule, and it is what the dispatcher asks now.
    """
    return not _has_text(result)


def _page_of(unit) -> int | None:
    for segment in unit["container_path"]:
        if segment.get("kind") == "page":
            return segment.get("index")
    return None


def _words(text: str) -> int:
    """Alphabetic tokens of two or more letters. Not a language-quality check: it does
    not judge the words, it notices whether the page has any."""
    return sum(1 for _ in re.finditer(r"[^\W\d_]{2,}", text))


def sparse_pages(*, result: ExtractionResult,
                 word_floor: int | None) -> tuple[int, ...] | None:
    """The pages of a document whose text layer is absent, read PER PAGE.

    11 Sep 2026, the owner's second corpus (`104` §18.53): a fourteen-page homework
    set had one typed cover page and thirteen photographed pages; a scanned volunteer
    file carried a scanner's garbage text layer ("tle Jes,", "Says esmsis") on every
    page. Both had "a text layer", so `direct_document_ocr_needed` said no and P6,
    finding a date on the cover, said the layer was usable. §2.2's rule -- no text
    layer routes to OCR -- is right; applying it to the whole file when the file is
    a stack of pages was the defect. 88 of 130 PDFs on that corpus have pages with
    fewer than three words.

    Returns None when the whole document has no text (the file-level route: OCR
    every page, as before); otherwise the page numbers whose text layer is absent.
    A page is absent when it stores no non-blank text, or, when the deployment
    supplies `word_floor` (`readers/deployment.py`, `cli.OCR_SPARSE_PAGE_WORDS`),
    when it carries fewer words than that. The NUMBER lives with the deployment,
    which is what SPEC Open question 1 asks: a deferred configuration value, not a
    constant in this module. A page the reader reported in `coverage.total` but
    stored no unit for is absent.
    """
    if not _has_text(result):
        return None
    words: dict[int, int] = {}
    for unit in result.text_units:
        page = _page_of(unit)
        if page is None:
            continue
        words[page] = words.get(page, 0) + _words(unit["text"])
    coverage = result.run.get("coverage") or {}
    total = coverage.get("processed") if coverage.get("units") == "pages" else None
    numbers = range(1, (total or 0) + 1) if total else sorted(words)
    floor = 1 if word_floor is None else word_floor
    return tuple(n for n in numbers if words.get(n, 0) < floor)


def text_layer_state(*, result: ExtractionResult, file_id: str, content_hash: str,
                     no_usable_facts: Callable[[str, str], bool]) -> str:
    """Section 2.2's state for a document run.

    P6 is asked ONLY about a non-empty text layer: a document with no text has no
    stored evidence P6 could have failed to make facts from, so its verdict there
    could not mean what it means in the broken case.
    """
    if not _has_text(result):
        return "text_layer_absent"
    if no_usable_facts(file_id, content_hash):
        return "text_layer_broken"
    return "text_layer_usable"


def document_ocr_decision(*, result: ExtractionResult, file_id: str,
                          content_hash: str,
                          no_usable_facts: Callable[[str, str], bool]) -> OcrDecision:
    """Section 2.2's OCR route for a document."""
    state = text_layer_state(result=result, file_id=file_id,
                             content_hash=content_hash,
                             no_usable_facts=no_usable_facts)
    if state == "text_layer_absent":
        return OcrDecision(state=state, run_ocr=True, targeted=False,
                           reason="no text layer; section 2.2 routes directly to OCR")
    if state == "text_layer_broken":
        return OcrDecision(
            state=state, run_ocr=True, targeted=True,
            reason=("P6 reported no usable facts from the stored evidence; "
                    "section 2.2 allows targeted OCR only on that verdict"))
    return OcrDecision(state=state, run_ocr=False, targeted=False,
                       reason="the text layer produced usable facts")


def metadata_words(result: ExtractionResult) -> int:
    """Words already stored on this image's metadata observations.

    A camera tag such as `Canon` is one word. A caption that is already a sentence
    is many. The count uses the same word rule as a PDF page, and the floor that
    decides "enough" is the caller's.
    """
    total = 0
    for item in result.observations:
        raw = item.get("raw_value") if isinstance(item, Mapping) else None
        if raw:
            total += _words(str(raw))
    return total


def text_meets_word_floor(*, result: ExtractionResult,
                          word_floor: int | None) -> bool:
    """Whether the text layer already has a page the deployment can classify from.

    `word_floor` is the caller's (`cli.OCR_SPARSE_PAGE_WORDS` on the product path).
    None keeps the bare rule: one page with a word. A document with no text at all
    is not classifiable from the text layer, and OCR remains the route for it.
    """
    if not _has_text(result):
        return False
    floor = 1 if word_floor is None else word_floor
    words: dict[int, int] = {}
    loose = 0
    for unit in result.text_units:
        page = _page_of(unit)
        if page is None:
            loose += _words(unit["text"])
            continue
        words[page] = words.get(page, 0) + _words(unit["text"])
    if words:
        return any(count >= floor for count in words.values())
    return loose >= floor


def image_ocr_decision(*, result: ExtractionResult,
                       word_floor: int | None = None) -> OcrDecision:
    """Whether an image still needs OCR.

    §2.7 wrote the trigger as "no usable text AND no usable metadata", and the owner
    ruled it away on 11 Sep 2026 (`00` amendment 6, `104` §18.52-§18.53) after
    reading the second corpus: four designed graphics were filed with nothing
    extracted, and camera photographs of a book page (11,000 characters of words)
    and of a printed passage were skipped because their EXIF said "photograph". A
    photograph of a page IS words. A camera tag does not hold OCR back.

    A caption that already meets `word_floor` is the text. OCR is not the default
    for that file. The floor is the caller's; None keeps the 11 Sep rule and a
    camera tag still goes to the engine.
    """
    if _has_text(result):
        return OcrDecision(state=None, run_ocr=False, targeted=False,
                           reason="the file yielded usable text")
    if word_floor is not None and metadata_words(result) >= word_floor:
        return OcrDecision(
            state=None, run_ocr=False, targeted=False,
            reason=("image metadata already has enough words to classify; "
                    "OCR was not run"))
    return OcrDecision(
        state=None, run_ocr=True, targeted=False,
        reason=("every image without enough metadata text is read "
                "(owner's ruling of 11 Sep 2026): the words on a graphic or a "
                "photographed page are the file"))
