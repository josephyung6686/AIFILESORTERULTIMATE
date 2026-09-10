"""`104` §18.2 gap 22, the OCR half -- `00`:247's "Maximum OCR time per scan".

The integration test beside this one drives the IMAGE ceiling through a real
scan, because that ceiling can be decided before a file is submitted: the router
names `image.metadata` in advance. The OCR ceiling cannot -- whether a PDF runs
OCR at all is decided inside `extract_initial` by `direct_document_ocr_needed` --
so the answer travels into the dispatcher as a flag and the dispatcher is where
this half is measured.

`00`:258: *"If the budget is exhausted, the product should retain extracted
evidence, mark the deferred stage, and leave the file or group in review rather
than guessing."* Both halves of that sentence are pinned here: the deferred mark
IS written, and the native reading beside it is NOT touched.

What was measured before this patch: `dispatch._ocr` had no notion of a budget,
`extractors/budgets.deferred_result` had no caller anywhere in `src/`, and
`cli.py` said in a comment that the ceiling had no enforcement point.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from extractors.archive import ArchiveManifest
from extractors.dispatch import Readers, extract_initial
from extractors.docx import DocxDocument
from extractors.image import ImageRecord
from extractors.long_tail import LongTailFile
from extractors.ocr import OcrOutput, OcrRegion
from extractors.pdf import PdfDocument, PdfPage
from extractors.router import route
from extractors.safety import SafetyPolicy

FIXED_CLOCK = "2026-09-10T00:00:00Z"

FILE_ROW = {
    "file_id": "f-scan",
    "content_hash":
        "c4b68614329771504e26f782d73842637dfa7ece1ad2bc377faae5c296806a0b",
    "filename": "Scanned.pdf",
    "extension": ".pdf",
}

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)

#: PAGES WITH NO TEXT LAYER, which is §2.2's "A file with no text should route
#: directly to OCR" -- the one route that needs no P6 verdict, so this fixture
#: reaches `_ocr` from `extract_initial` alone.
NO_TEXT_LAYER = PdfDocument(
    metadata={"Title": "Scanned"},
    pages=tuple(PdfPage(number=n, text="", regions=()) for n in range(1, 10)))


def _engine(target, *, config) -> OcrOutput:
    """An engine that would succeed. Present so that a missing OCR run in the
    deferred case can only be the ceiling and never an absent engine."""
    return OcrOutput(
        provider="fixture", provider_version="1.0",
        pages_processed=9, pages_total=9,
        regions=(OcrRegion(page=1, region=1, text="scanned words",
                           box={"x": 0.1, "y": 0.2, "w": 0.8, "h": 0.05,
                                "unit": "norm"},
                           confidence=0.9),))


def _readers(*, engine=_engine) -> Readers:
    return Readers(
        read_pdf=lambda path: NO_TEXT_LAYER,
        read_docx=lambda path: DocxDocument(core_properties={}),
        read_text_document=lambda path: None,
        read_long_tail=lambda path, transcribe=False: LongTailFile(),
        read_manifest=lambda path: ArchiveManifest(archive_type="zip"),
        read_image=lambda path: ImageRecord(image_format="PNG", dimensions="1x1",
                                            width=1, height=1),
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda width, height: None,
        filename_pattern=lambda name: None,
        ocr_engine=engine,
        ocr_config={},
    )


def _dispatch(*, ocr_budget_spent: bool):
    path = Path("/corpus/Scanned.pdf")
    decision = route(file_id=FILE_ROW["file_id"],
                     content_hash=FILE_ROW["content_hash"], path=path,
                     extension=".pdf", detect_format=lambda p: "pdf")
    return extract_initial(
        file_row=FILE_ROW, decision=decision, path=path, policy=OPEN_POLICY,
        readers=_readers(), now=FIXED_CLOCK, context_window=40,
        transcription_authorized=lambda: False,
        ocr_budget_spent=ocr_budget_spent)


def _by_tier(dispatched, tier):
    return [result for result in dispatched.results
            if result.run["analysis_tier"] == tier]


def test_within_the_budget_the_scan_runs_ocr():
    """The baseline, pinned FIRST so the deferral below cannot pass vacuously.

    A scanned PDF with no text layer runs OCR, the run is `complete`, and the
    dispatcher reports the seconds it spent so a caller has something to charge
    the scan's clock with.
    """
    dispatched = _dispatch(ocr_budget_spent=False)

    ocr_runs = _by_tier(dispatched, "ocr")
    assert len(ocr_runs) == 1
    assert ocr_runs[0].run["completeness"] == "complete"
    assert ocr_runs[0].run["observation_count"] > 0
    assert dispatched.ocr_seconds >= 0.0


def test_past_the_budget_the_ocr_run_is_deferred():
    """The item: `00`:247's ceiling, and P4's word for having met it.

    Measured: the same file, with the scan's OCR clock reported spent, produces
    an OCR run at `completeness = deferred` carrying zero observations -- the
    engine above would have succeeded, so nothing but the ceiling can explain it.

    `deferred` and not `capped`: `capped` means an extractor read something and
    stopped; this one never started, which is exactly what
    `budgets.deferred_result`'s docstring says the value is for.
    """
    dispatched = _dispatch(ocr_budget_spent=True)

    ocr_runs = _by_tier(dispatched, "ocr")
    assert len(ocr_runs) == 1
    assert ocr_runs[0].run["completeness"] == "deferred"
    assert ocr_runs[0].run["observation_count"] == 0
    assert ocr_runs[0].observations == ()
    assert ocr_runs[0].text_units == ()


def test_the_deferred_run_names_how_much_it_did_not_read():
    """`runs.coverage`: "a run may not claim more progress than the work it was
    given", and §8.6 needs the count computable rather than estimated.

    Measured: the deferred OCR run reads `0 of 9 pages` -- the file's REAL page
    count, taken from the native result it would have run beside, not a total
    invented to match a zero. A total of 0 would be the ceiling wearing a full
    count, and `00`:259's line would then say a nine-page scan was fully handled.
    """
    ocr_run = _by_tier(_dispatch(ocr_budget_spent=True), "ocr")[0]
    assert ocr_run.run["coverage"] == {
        "units": "pages", "processed": 0, "total": 9}


def test_the_native_reading_below_the_ceiling_is_untouched():
    """`00`:258: "the product should retain extracted evidence."

    A ceiling on the OCR pass refuses the OCR pass and nothing else. Measured:
    the native PDF run is present and identical whether the OCR budget is spent
    or not, so the title, the page count and every metadata observation the file
    gave up before the ceiling survive it.
    """
    within = _by_tier(_dispatch(ocr_budget_spent=False), "native")[0]
    past = _by_tier(_dispatch(ocr_budget_spent=True), "native")[0]

    assert within.run == past.run
    assert within.observations == past.observations
    assert past.run["completeness"] == "complete"


def test_a_deferred_run_costs_the_clock_nothing():
    """The budget charges for work, and a deferral did none.

    Measured: `ocr_seconds` is 0.0 for the deferred dispatch. A deferral that
    charged the clock would make every later file in the scan more expensive for
    a pass that never ran.
    """
    assert _dispatch(ocr_budget_spent=True).ocr_seconds == 0.0


def test_a_deployment_with_no_engine_still_writes_no_ocr_run():
    """The pre-existing contract, pinned because the new branch sits beside it.

    `_ocr`'s own rule: "No engine is a DEPLOYMENT state, known before the call,
    and §2.2's and §2.7's routes simply stop -- no run, by design." A ceiling
    must not turn that silence into a deferral: a deployment without OCR has not
    run out of budget, and saying it had would name the wrong cause on `00`:259's
    line.
    """
    path = Path("/corpus/Scanned.pdf")
    decision = route(file_id=FILE_ROW["file_id"],
                     content_hash=FILE_ROW["content_hash"], path=path,
                     extension=".pdf", detect_format=lambda p: "pdf")
    dispatched = extract_initial(
        file_row=FILE_ROW, decision=decision, path=path, policy=OPEN_POLICY,
        readers=_readers(engine=None), now=FIXED_CLOCK, context_window=40,
        transcription_authorized=lambda: False, ocr_budget_spent=True)

    assert _by_tier(dispatched, "ocr") == []
    assert len(_by_tier(dispatched, "native")) == 1
