"""OCR cost on the first scan, exercised with a fake engine so Linux runs it.

The owner's Mac is the only machine that has Vision. These tests are the
contract that run can still check: a page cap that leaves the classification
unchanged when the first pages already name the file, a skip that is stored
as a capped run, and the production config the next Mac scan will use.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import record_file
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter
from extractors.dispatch import Readers, extract
from extractors.image import ExifValue, ImageRecord
from extractors.ocr import OcrOutput, OcrRegion, pages_within_cap
from extractors.pdf import PdfDocument, PdfPage
from extractors.router import route
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from readers.ocr_vision import fitted_pixel_size
from recognition.detector import (
    SAFETY_DOMAIN_HANDLING, Detector, Handling, Recognition,
)
from recognition.rules import load_rules
from recognition.vocabulary import MANIFEST_VERSION

import cli

CLOCK = "2026-09-30T12:00:00+00:00"
HASH = "5f7b1a1c9d4e6f2a3b8c0d1e2f3a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c"
OPEN = SafetyPolicy(is_protected_container=lambda path: False,
                    is_dataless=lambda path: False)

#: Page 1 names the file. Page 2 is the second signal the detector needs.
#: Pages 3 and 4 continue the same document and add no second schema.
PAGE_TEXT = {
    1: "syllabus",
    2: "problem set",
    3: "the numbered working continues on this page",
    4: "the same numbers are copied out again below",
}


def _rules():
    entry = {
        "schema_id": "academic",
        "context_terms": ["office hours", "syllabus"],
        "work_type_terms": ["problem set"],
        "source_types": ["text_document"],
        "extensions": [".pdf"],
        "file_kind_never_alone": True,
        "rows": ["academic.row"],
        "refused_rows": [],
        "needs_llm": [],
        "never_alone_rows": [],
    }
    payload = {"manifest_version": MANIFEST_VERSION, "compiled_rows": 1,
               "refused_rows": 0, "schemas": {"academic": entry}}
    return load_rules(lambda: json.dumps(payload))


def _detector():
    return Detector(
        _rules(),
        handling_for={**SAFETY_DOMAIN_HANDLING,
                      "academic": Handling("personal_non_sensitive", False,
                                           "detector")},
        now=lambda: CLOCK)


def _row(name: str, *, file_id: str = "f1", content_hash: str = HASH) -> dict:
    return {"file_id": file_id, "content_hash": content_hash, "filename": name,
            "extension": Path(name).suffix, "mime_type": None,
            "detected_format": Path(name).suffix.lstrip(".")}


def _decision(name: str, *, file_id: str = "f1", content_hash: str = HASH):
    return route(file_id=file_id, content_hash=content_hash,
                 path=Path("/c") / name, extension=Path(name).suffix,
                 detect_format=lambda p: Path(name).suffix.lstrip("."))


def _readers(**over) -> Readers:
    base = dict(
        read_pdf=lambda p: PdfDocument(metadata={}, iso_dates={}, pages=()),
        read_docx=lambda p: None,
        read_text_document=lambda p: None,
        read_long_tail=lambda p, transcribe=False: None,
        read_manifest=lambda p: None,
        read_image=lambda p: ImageRecord(
            image_format="PNG", dimensions="1x1", width=1, height=1),
        ocr_engine=None,
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda w, h: None,
        filename_pattern=lambda name: None,
    )
    base.update(over)
    return Readers(**base)


def _extract(name: str, **over):
    readers = over.pop("readers", {})
    file_id = over.pop("file_id", "f1")
    content_hash = over.pop("content_hash", HASH)
    return extract(file_row=_row(name, file_id=file_id,
                                 content_hash=content_hash),
                   decision=_decision(name, file_id=file_id,
                                      content_hash=content_hash),
                   path=Path("/c") / name, policy=OPEN,
                   readers=_readers(**readers), now=CLOCK, context_window=40,
                   no_usable_facts=lambda f, h: False,
                   transcription_authorized=lambda: False, **over)


def _engine(calls, *, pages=4):
    def engine(path, config):
        calls.append(dict(config or {}))
        cap = (config or {}).get("page_cap")
        chosen, left = pages_within_cap(tuple(range(1, pages + 1)), cap)
        return OcrOutput(
            provider="test", provider_version="1",
            regions=tuple(OcrRegion(page=number, region=1, text=PAGE_TEXT[number])
                          for number in chosen),
            pages_processed=len(chosen), pages_total=pages, capped=left)
    return engine


def test_pages_within_cap_keeps_the_front_and_says_when_it_stopped():
    chosen, left = pages_within_cap((1, 2, 3, 4), 2)
    assert chosen == (1, 2)
    assert left is True
    everything, untouched = pages_within_cap((1, 2), None)
    assert everything == (1, 2)
    assert untouched is False


def test_a_letter_page_is_left_alone_and_a_camera_frame_is_shrunk():
    width, height, scaled = fitted_pixel_size(4032, 3024, 2200)
    assert (width, height, scaled) == (2200, 1650, True)
    assert fitted_pixel_size(100, 50, 2200) == (100, 50, False)


def test_the_product_ocr_config_is_the_classification_pass():
    readers = cli.extraction_context().readers
    config = readers.ocr_config
    assert config["page_cap"] == cli.FIRST_SCAN_OCR_PAGES == 2
    assert config["time_limit_seconds"] == cli.OCR_SECONDS_PER_FILE
    assert config["recognition_level"] == "fast"
    assert config["max_long_edge_px"] == cli.OCR_IMAGE_LONG_EDGE_PX == 2200
    assert config["sparse_page_words"] == cli.OCR_SPARSE_PAGE_WORDS
    # This machine has no Vision. The config is still the one a Mac scan uses.
    assert readers.ocr_engine is None


def test_capped_ocr_classifies_the_same_file_as_reading_every_page(conn, tmp_path):
    """The first two pages already carry both terms. Later pages do not add one."""
    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    det = _detector()
    labels = {}
    for name, cap in (("full.pdf", None), ("capped.pdf", 2)):
        path = tmp_path / name
        path.write_bytes(b"%PDF-" + name.encode())
        file_id = record_file(
            conn, path, filename=name, normalized_filename=name.casefold(),
            extension=".pdf", observed_size=path.stat().st_size,
            observed_timestamps="{}", parent_folder_context=str(tmp_path),
            mime_type=None, detected_format="pdf", scan_state="scanned",
            materialized=True)
        content_hash = conn.execute(
            "SELECT content_hash FROM files WHERE file_id = ?", (file_id,)
        ).fetchone()["content_hash"]
        calls = []
        dispatched = _extract(
            name, file_id=file_id, content_hash=content_hash,
            readers={"ocr_engine": _engine(calls),
                     "ocr_config": {"page_cap": cap}})
        ocr = dispatched.results[1]
        RunWriter(conn, author="P5").write(ocr)
        outcome = det.explain(conn, file_id, content_hash)
        labels[name] = (outcome, ocr, calls)

    full, full_run, full_calls = labels["full.pdf"]
    capped, capped_run, capped_calls = labels["capped.pdf"]
    assert isinstance(full, Recognition)
    assert isinstance(capped, Recognition)
    assert full.schema_id == capped.schema_id == "academic"
    assert {m.term for m in full.matches} == {m.term for m in capped.matches}
    assert full_run.run["completeness"] == "complete"
    assert full_run.run["coverage"]["processed"] == 4
    assert capped_run.run["completeness"] == "capped"
    assert capped_run.run["coverage"] == {"units": "pages", "processed": 2,
                                           "total": 4}
    assert capped_calls[0]["page_cap"] == 2
    assert len(full_calls) == len(capped_calls) == 1


def test_a_text_layer_that_already_classifies_is_recorded_and_not_read(tmp_path):
    calls = []

    def engine(path, config):
        calls.append(config)
        raise AssertionError("the engine was called")

    cover = ("This honors precalculus homework covers power functions and "
             "their graphs and is due on Thursday of next week in class")
    dispatched = _extract("homework.pdf", readers={
        "read_pdf": lambda p: PdfDocument(metadata={}, iso_dates={}, pages=(
            PdfPage(number=1, text=cover),
            PdfPage(number=2, text=""),
            PdfPage(number=3, text="1"))),
        "ocr_engine": engine,
        "ocr_config": {"sparse_page_words": 20}})
    assert calls == []
    assert [r.run["analysis_tier"] for r in dispatched.results] == ["native", "ocr"]
    skipped = dispatched.results[1].run
    assert skipped["completeness"] == "capped"
    assert skipped["extractor_name"] == "ocr.not_called"
    assert "not OCR'd" in skipped["config"]["not_called"]
    assert skipped["config"]["pages_not_read"] == [2, 3]


def test_an_image_caption_that_already_classifies_is_recorded_and_not_read():
    calls = []

    def engine(path, config):
        calls.append(config)
        raise AssertionError("the engine was called")

    caption = " ".join(["lecture", "notes"] * 10)
    dispatched = _extract("board.png", readers={
        "read_image": lambda p: ImageRecord(
            image_format="PNG", dimensions="1x1", width=1, height=1,
            exif=(ExifValue(name="ImageDescription", value=caption),)),
        "ocr_engine": engine,
        "ocr_config": {"sparse_page_words": 20}})
    assert calls == []
    assert [r.run["analysis_tier"] for r in dispatched.results] == ["native", "ocr"]
    skipped = dispatched.results[1].run
    assert skipped["completeness"] == "capped"
    assert skipped["extractor_name"] == "ocr.not_called"
    assert skipped["config"]["not_called"]
    assert skipped["config"]["pages_not_read"] == []


def test_a_camera_tag_still_reaches_ocr_when_the_caption_is_short():
    calls = []

    def engine(path, config):
        calls.append(config)
        return OcrOutput(provider="test", provider_version="1",
                         regions=(OcrRegion(page=None, region=1,
                                            text="syllabus problem set"),),
                         pages_processed=1, pages_total=1)

    dispatched = _extract("photo.heic", readers={
        "read_image": lambda p: ImageRecord(
            image_format="HEIC", dimensions="4032x3024", width=4032, height=3024,
            exif=(ExifValue(name="Make", value="Canon", kind="camera EXIF"),)),
        "ocr_engine": engine,
        "ocr_config": {"sparse_page_words": 20}})
    assert len(calls) == 1
    assert [r.run["analysis_tier"] for r in dispatched.results] == ["native", "ocr"]
    assert dispatched.results[1].run["completeness"] == "complete"
    assert "not_called" not in dispatched.results[1].run["config"]
