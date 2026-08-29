"""Public P5 passes keep P6 between native PDF extraction and targeted OCR."""
from pathlib import Path

import pytest

import extractors.dispatch as dispatch_module
from extractors.dispatch import Readers, extract_initial, extract_targeted_ocr
from extractors.failure import ContractViolation
from extractors.image import ImageRecord
from extractors.ocr import OcrOutput, OcrRegion
from extractors.pdf import PdfDocument, PdfPage
from extractors.reading import Region
from extractors.router import route
from extractors.safety import SafetyPolicy

from conftest import FIXED_CLOCK


HASH = "5f7b1a1c9d4e6f2a3b8c0d1e2f3a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c"
POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                      is_dataless=lambda path: False)


def row(name: str) -> dict:
    return {"file_id": "f1", "content_hash": HASH, "filename": name,
            "extension": Path(name).suffix, "mime_type": None,
            "detected_format": Path(name).suffix.lstrip(".")}


def decision(name: str):
    return route(file_id="f1", content_hash=HASH, path=Path("/c") / name,
                 extension=Path(name).suffix,
                 detect_format=lambda path: Path(name).suffix.lstrip("."))


def readers(*, pdf_text: str = "BUSIB 4300", ocr_calls: list | None = None,
            image_record: ImageRecord | None = None) -> Readers:
    from extractors.archive import ArchiveManifest
    from extractors.docx import DocxDocument
    from extractors.long_tail import LongTailFile
    from extractors.structured_text import TextDocument

    calls = ocr_calls if ocr_calls is not None else []
    pages = ((PdfPage(number=1, text=pdf_text,
                      regions=(Region(zone="body", start=0, end=len(pdf_text)),)),)
             if pdf_text else ())

    def ocr_engine(path, config):
        calls.append(path)
        return OcrOutput(
            provider="apple-vision", provider_version="19.1",
            regions=(OcrRegion(page=1, region=1, text="Columbia"),),
            pages_processed=1, pages_total=1)

    return Readers(
        read_pdf=lambda path: PdfDocument(metadata={}, pages=pages),
        read_docx=lambda path: DocxDocument(core_properties={}),
        read_text_document=lambda path: TextDocument(text="text"),
        read_long_tail=lambda path, transcribe=False: LongTailFile(),
        read_manifest=lambda path: ArchiveManifest(archive_type="zip"),
        read_image=lambda path: image_record or ImageRecord(
            image_format="PNG", dimensions="2880x1800", width=2880, height=1800),
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda width, height: None,
        filename_pattern=lambda name: None,
        ocr_engine=ocr_engine,
    )


def initial(name: str, supplied_readers: Readers):
    return extract_initial(
        file_row=row(name), decision=decision(name), path=Path("/c") / name,
        policy=POLICY, readers=supplied_readers, now=FIXED_CLOCK,
        context_window=40, transcription_authorized=lambda: False)


def targeted(name: str, native_result, supplied_readers: Readers,
             no_usable_facts=lambda file_id, content_hash: True):
    return extract_targeted_ocr(
        file_row=row(name), decision=decision(name), path=Path("/c") / name,
        policy=POLICY, readers=supplied_readers, now=FIXED_CLOCK,
        context_window=40, native_result=native_result,
        no_usable_facts=no_usable_facts)


def test_initial_text_pdf_emits_native_without_consulting_p6_or_ocr():
    calls = []
    result = initial("notes.pdf", readers(ocr_calls=calls))
    assert [item.run["analysis_tier"] for item in result.results] == ["native"]
    assert calls == []


def test_module_describes_both_ordered_passes_and_the_compatibility_entry_point():
    doc = dispatch_module.__doc__ or ""
    assert "extract_initial" in doc
    assert "extract_targeted_ocr" in doc
    assert "compatib" in doc.lower()
    assert "One entry point per file" not in doc


def test_initial_scanned_pdf_runs_direct_ocr_without_a_p6_verdict():
    calls = []
    result = initial("scan.pdf", readers(pdf_text="", ocr_calls=calls))
    assert [item.run["analysis_tier"] for item in result.results] == ["native", "ocr"]
    assert len(calls) == 1


def test_initial_image_keeps_p5_owned_ocr_policy():
    result = initial("Screenshot.png", readers())
    assert [item.run["analysis_tier"] for item in result.results] == ["native", "ocr"]


def test_targeted_pdf_uses_p6_verdict_and_emits_at_most_one_ocr_run():
    seen = []
    supplied = readers()
    native = initial("notes.pdf", supplied).results[0]
    result = targeted(
        "notes.pdf", native, supplied,
        no_usable_facts=lambda file_id, content_hash:
        seen.append((file_id, content_hash)) or True)
    assert [item.run["analysis_tier"] for item in result.results] == ["ocr"]
    assert seen == [("f1", HASH)]


def test_targeted_pdf_emits_nothing_when_p6_reports_usable_facts():
    supplied = readers()
    native = initial("notes.pdf", supplied).results[0]
    result = targeted("notes.pdf", native, supplied,
                      no_usable_facts=lambda file_id, content_hash: False)
    assert result.results == ()


def test_targeted_non_pdf_is_a_noop_and_does_not_ask_p6():
    asked = []
    supplied = readers()
    native = initial("Screenshot.png", supplied).results[0]
    result = targeted(
        "Screenshot.png", native, supplied,
        no_usable_facts=lambda file_id, content_hash: asked.append(file_id) or True)
    assert result.results == ()
    assert asked == []


def test_targeted_pdf_refuses_a_wrong_family_native_result():
    supplied = readers()
    image_native = initial("Screenshot.png", supplied).results[0]
    with pytest.raises(ContractViolation):
        targeted("notes.pdf", image_native, supplied)


def test_targeted_pdf_refuses_a_native_result_for_a_different_file_id():
    supplied = readers()
    native = initial("notes.pdf", supplied).results[0]
    wrong_row = {**row("notes.pdf"), "file_id": "f-other"}
    with pytest.raises(ContractViolation, match="file_id"):
        extract_targeted_ocr(
            file_row=wrong_row, decision=decision("notes.pdf"),
            path=Path("/c/notes.pdf"), policy=POLICY, readers=supplied,
            now=FIXED_CLOCK, context_window=40, native_result=native,
            no_usable_facts=lambda file_id, content_hash: True)


def test_targeted_pdf_refuses_a_native_result_for_a_different_content_hash():
    supplied = readers()
    native = initial("notes.pdf", supplied).results[0]
    wrong_row = {**row("notes.pdf"), "content_hash": "0" * 64}
    with pytest.raises(ContractViolation, match="content_hash"):
        extract_targeted_ocr(
            file_row=wrong_row, decision=decision("notes.pdf"),
            path=Path("/c/notes.pdf"), policy=POLICY, readers=supplied,
            now=FIXED_CLOCK, context_window=40, native_result=native,
            no_usable_facts=lambda file_id, content_hash: True)


def test_targeted_pdf_refuses_an_ocr_result_as_its_native_input():
    supplied = readers()
    native = initial("notes.pdf", supplied).results[0]
    ocr_result = targeted("notes.pdf", native, supplied).results[0]
    with pytest.raises(ContractViolation):
        targeted("notes.pdf", ocr_result, supplied)


def test_targeted_scanned_pdf_does_not_duplicate_its_direct_ocr():
    calls = []
    supplied = readers(pdf_text="", ocr_calls=calls)
    produced = initial("scan.pdf", supplied)
    result = targeted(
        "scan.pdf", produced.results[0], supplied,
        no_usable_facts=lambda file_id, content_hash:
        pytest.fail("P6 must not be asked about an absent text layer"))
    assert result.results == ()
    assert len(calls) == 1


def test_targeted_pdf_without_an_ocr_engine_emits_no_run():
    supplied = readers()
    supplied = Readers(**{**supplied.__dict__, "ocr_engine": None})
    native = initial("notes.pdf", supplied).results[0]
    assert targeted("notes.pdf", native, supplied).results == ()


def test_targeted_pdf_with_a_raising_engine_preserves_a_failed_ocr_run():
    supplied = readers()

    def raising_engine(path, config):
        raise RuntimeError("engine unavailable")

    supplied = Readers(**{**supplied.__dict__, "ocr_engine": raising_engine})
    native = initial("notes.pdf", supplied).results[0]
    result = targeted("notes.pdf", native, supplied)
    assert len(result.results) == 1
    assert result.results[0].run["analysis_tier"] == "ocr"
    assert result.results[0].run["completeness"] == "failed"
