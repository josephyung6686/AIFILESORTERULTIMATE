# tests/p5/test_p5_dispatch.py
"""OQ2 -- the per-file dispatcher, closed as ONE `extract(file_row, decision, ...)`.

18-wave2-orchestrator.md: "One P5 `extract(file_row, decision, ...)` that may return
two runs (E5+E6). Orchestrator does not dispatch by name." The orchestrator owns
order, not routing, and a caller that switched on `extractor_name` would be a second
copy of the routing table living outside P5.

The join this closes, executed 2026-08-21: the router labels EIGHT source types
`text.structured`, and `extract_structured_text` accepts only two of them --
`text_document` and `code_structured` -- raising `WrongFamily` on the other six.
That is not a router bug. `long_tail.py` deliberately shares the `text.structured`
family name, because §2.9's long-tail families are the same extractor family with a
second half. Nothing had ever had to pick the half, because nothing dispatched. A
real corpus would have raised on its first .xlsx, .pptx, .eml, .ics or .vcf.
"""
from pathlib import Path

import pytest

from extractors.dispatch import Readers, extract
from extractors.router import route
from extractors.safety import SafetyPolicy
from extractors.structured_text import STRUCTURED_TEXT_SOURCE_TYPES
from extractors.long_tail import LONG_TAIL_SOURCE_TYPES

from conftest import FIXED_CLOCK

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
HASH = "5f7b1a1c9d4e6f2a3b8c0d1e2f3a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c"


def a_row(name: str) -> dict:
    return {"file_id": "f1", "content_hash": HASH, "filename": name,
            "extension": Path(name).suffix, "mime_type": None,
            "detected_format": Path(name).suffix.lstrip(".")}


def a_decision(name: str):
    return route(file_id="f1", content_hash=HASH, path=Path("/c") / name,
                 extension=Path(name).suffix,
                 detect_format=lambda p: Path(name).suffix.lstrip("."))


def readers(**over) -> Readers:
    """Every reader is injected; P5 opens nothing on its own."""
    from extractors.pdf import PdfDocument, PdfPage
    from extractors.docx import DocxDocument
    from extractors.reading import Region
    from extractors.archive import ArchiveManifest
    from extractors.image import ImageRecord
    from extractors.structured_text import TextDocument
    from extractors.long_tail import LongTailFile

    base = dict(
        read_pdf=lambda p: PdfDocument(
            metadata={}, iso_dates={},
            pages=(PdfPage(number=1, text="BUSIB 4300",
                           regions=(Region(zone="body", start=0, end=10),)),)),
        read_docx=lambda p: DocxDocument(core_properties={}),
        read_text_document=lambda p: TextDocument(text="BUSIB 4300"),
        read_long_tail=lambda p, transcribe=False: LongTailFile(),
        read_manifest=lambda p: ArchiveManifest(archive_type="zip"),
        read_image=lambda p: ImageRecord(image_format="PNG",
                                         dimensions="2880x1800",
                                         width=2880, height=1800),
        ocr_engine=None,
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda w, h: None,
        filename_pattern=lambda name: None,
    )
    base.update(over)
    return Readers(**base)


def run_it(name: str, **over):
    return extract(file_row=a_row(name), decision=a_decision(name),
                   path=Path("/c") / name, policy=OPEN_POLICY,
                   readers=readers(**over.pop("readers", {})),
                   now=FIXED_CLOCK, context_window=40,
                   no_usable_facts=lambda f, h: False,
                   transcription_authorized=lambda: False, **over)


# --------------------------------------------- the break this exists to close
@pytest.mark.parametrize("name", ["book.xlsx", "deck.pptx", "note.eml",
                                  "term.ics", "card.vcf"])
def test_the_six_long_tail_families_reach_e3_and_not_the_wrong_half(name):
    """Each of these routes to `text.structured` and would raise `WrongFamily` if the
    dispatcher picked the half by name instead of by source type."""
    dispatched = run_it(name)
    assert dispatched.results, name


def test_the_two_structured_text_families_reach_the_other_half():
    for name in ("readme.md", "main.py"):
        assert run_it(name).results, name


def test_the_two_halves_partition_every_family_the_router_labels_text_structured():
    """A family in neither set would fall through the dispatcher silently."""
    from extractors.router import HANDLER_BY_SOURCE_TYPE
    labelled = {source for source, handler in HANDLER_BY_SOURCE_TYPE.items()
                if handler == "text.structured"}
    assert labelled <= set(STRUCTURED_TEXT_SOURCE_TYPES) | set(LONG_TAIL_SOURCE_TYPES)
    assert not set(STRUCTURED_TEXT_SOURCE_TYPES) & set(LONG_TAIL_SOURCE_TYPES)


# ------------------------------------------------------ the ordinary families
def test_a_pdf_reaches_e1():
    result = run_it("syllabus.pdf").results[0]
    assert result.run["extractor_name"] == "pdf.text"


def test_an_archive_reaches_e4():
    assert run_it("bundle.zip").results[0].run["extractor_name"] == "archive.manifest"


def test_an_unrouted_file_becomes_the_stopped_run_and_not_an_exception():
    """§2.4: never silently an empty document, and never a crash either."""
    result = run_it("thing.qqq").results[0]
    assert result.run["completeness"] in ("unsupported", "unreadable", "metadata_only")
    assert result.run["extractor_name"] == "format.unrouted"


# ------------------------------------------------------------ two runs, E5+E6
def test_an_opaque_image_produces_the_image_run_and_then_the_ocr_run():
    """§2.7: "when a file yields no usable text AND no usable metadata". The image
    reader returns nothing, so E6 follows E5 -- the two-run case OQ2 names."""
    from extractors.ocr import OcrOutput, OcrRegion

    def engine(path, config):
        return OcrOutput(provider="apple-vision", provider_version="19.1",
                         regions=(OcrRegion(page=1, region=1, text="Columbia"),),
                         pages_processed=1, pages_total=1)

    dispatched = run_it("Screenshot.png", readers={"ocr_engine": engine})
    tiers = [r.run["analysis_tier"] for r in dispatched.results]
    assert tiers == ["native", "ocr"]


def test_an_image_with_metadata_does_not_reach_ocr():
    from extractors.image import ExifValue, ImageRecord
    dispatched = run_it("photo.heic", readers={
        "read_image": lambda p: ImageRecord(
            image_format="HEIC", dimensions="4032x3024", width=4032, height=3024,
            exif=(ExifValue(name="Make", value="Apple", kind="camera EXIF"),))})
    assert [r.run["analysis_tier"] for r in dispatched.results] == ["native"]


def test_a_pdf_with_no_text_layer_reaches_ocr():
    """§2.2's `text_layer_absent`, which routes directly to OCR (B7: P5 wires the
    switch and never invents the threshold)."""
    from extractors.pdf import PdfDocument
    from extractors.ocr import OcrOutput, OcrRegion

    def engine(path, config):
        return OcrOutput(provider="apple-vision", provider_version="19.1",
                         regions=(OcrRegion(page=1, region=1, text="Columbia"),),
                         pages_processed=1, pages_total=1)

    dispatched = run_it("scanned.pdf", readers={
        "read_pdf": lambda p: PdfDocument(metadata={}, iso_dates={}, pages=()),
        "ocr_engine": engine})
    assert [r.run["analysis_tier"] for r in dispatched.results] == ["native", "ocr"]


def test_a_pdf_whose_text_layer_yields_facts_does_not_reach_ocr():
    assert [r.run["analysis_tier"] for r in run_it("syllabus.pdf").results] == ["native"]


# ------------------------------------------------------------ what it must not do
def test_the_sensitivity_signals_e3_raises_are_carried_and_not_dropped():
    """P4 rule 6 forbids an extractor-private field on an observation, so the signal
    travels beside the batch. A dispatcher that returned only runs would lose it."""
    dispatched = run_it("note.eml")
    assert hasattr(dispatched, "sensitivity")


def test_the_dispatcher_names_no_format_and_no_source_type():
    """The routing table is §2.9's and lives in router.py. A second copy here is the
    defect this project has paid for most often."""
    import ast
    from pathlib import Path as P
    import extractors.dispatch as module
    tree = ast.parse(P(module.__file__).read_text())
    docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                  if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef))
                  and n.body and isinstance(n.body[0], ast.Expr)
                  and isinstance(n.body[0].value, ast.Constant)
                  and isinstance(n.body[0].value.value, str)}
    held = {n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and id(n) not in docstrings}
    for token in ("pdf", "docx", "png", "heic", "zip", "xlsx", "eml",
                  "text_document", "spreadsheet", "image", "email"):
        assert token not in held, token
