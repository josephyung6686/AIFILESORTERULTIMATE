"""The production composition root supplies plumbing, never domain authority."""
from pathlib import Path

import pytest

from eval_harness.bundle import bundle_files
from extractors.archive import ArchiveManifest
from extractors.dispatch import Readers
from extractors.docx import DocxDocument
from extractors.image import ImageRecord
from extractors.long_tail import LongTailFile
from extractors.ocr import OcrOutput, OcrRegion
from extractors.pdf import PdfDocument, PdfPage
from extractors.reading import Region, StructuredString
from extractors.safety import SafetyPolicy
from extractors.structured_text import TextDocument
from facts.file_facts import DETERMINISTIC_EXTRACTOR, write_fact
from facts.resolver import FactResolver
from facts.states import DIRECT
from facts.usable import record_pass
from facts.values import ensure_value
from privacy.classification import ClassificationRecord
from privacy.authorship import CLASSIFICATION_ASSIGNED
from production import (
    MissingClassificationAuthority,
    P1P7Authorities,
    bootstrap_p1_p7,
    run_production_p1_p7,
)
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.selection import record_selection


CLOCK = "2026-08-25T12:00:00+00:00"


def _readers(ocr_calls):
    text = "broken text"

    def ocr_engine(path, config):
        ocr_calls.append(path)
        return OcrOutput(
            provider="test", provider_version="1",
            regions=(OcrRegion(page=1, region=1, text="pdf"),),
            pages_processed=1, pages_total=1)

    return Readers(
        read_pdf=lambda path: PdfDocument(
            metadata={}, pages=(PdfPage(
                number=1, text=text,
                regions=(Region(zone="body", start=0, end=len(text)),)),)),
        read_docx=lambda path: DocxDocument(core_properties={}),
        read_text_document=lambda path: TextDocument(text="text"),
        read_long_tail=lambda path, transcribe=False: LongTailFile(),
        read_manifest=lambda path: ArchiveManifest(archive_type="zip"),
        read_image=lambda path: ImageRecord(
            image_format="PNG", dimensions="1x1", width=1, height=1),
        find_structured_strings=lambda text: (
            (StructuredString(kind="identifier", start=0, end=len(text)),)
            if text else ()),
        recognize_markers=lambda names: (),
        dimension_signal=lambda width, height: None,
        filename_pattern=lambda name: None, ocr_engine=ocr_engine)


def _resolver(*, tiers, cache_key):
    def stage(conn, file_id, content_hash):
        evidence_ref = conn.execute(
            "SELECT observation_key FROM evidence WHERE file_id = ? "
            "ORDER BY rowid LIMIT 1", (file_id,)).fetchone()[0]
        value_id = ensure_value(
            conn, field_key="file_type", canonical_value="pdf",
            first_evidence_ref=evidence_ref, origin="automatic")
        return (write_fact(
            conn, file_id=file_id, content_hash=content_hash,
            field_key="file_type", value_id=value_id,
            reliability_state=DIRECT, origin=DETERMINISTIC_EXTRACTOR,
            evidence_refs=(evidence_ref,), cache_key=cache_key, active=True),)

    return FactResolver(
        stages={"direct": stage, "rule": None, "llm": None},
        pending_fields=lambda conn, file_id, content_hash: (),
        budget_exhausted=lambda ceiling: False,
        model_route_permitted=lambda file_id: False,
        record_pass=lambda conn, file_id, content_hash: record_pass(
            conn, file_id=file_id, content_hash=content_hash,
            analysis_tiers=tiers),
        cache_key_for=lambda file_id, content_hash: cache_key,
        screen_metadata=lambda conn, file_id, content_hash: ())


def _authorities(*, readers, classify):
    return P1P7Authorities(
        native_resolver=_resolver(
            tiers=frozenset(("filesystem", "native")), cache_key="native-v1"),
        ocr_resolver=_resolver(
            tiers=frozenset(("filesystem", "native", "ocr")),
            cache_key="ocr-v1"),
        usable_threshold=lambda facts, unresolved: False,
        classify=classify, source=FilesystemCorpusSource(),
        mime_type_for=lambda path: "application/pdf", scan_state="scanned",
        scan_budget_exhausted=lambda: False,
        detect_format=lambda path: "pdf",
        policy=SafetyPolicy(
            is_protected_container=lambda path: False,
            is_dataless=lambda path: False),
        readers=readers, now=lambda: CLOCK, context_window=40,
        transcription_authorized=lambda: False, corpus_form="snapshot",
        policy_settings={}, file_entry_body=lambda row: {"payload_ref": "blob"},
        p7_component_version="0.1.0")


def test_production_root_runs_real_p1_through_p7_and_bundles_authoritative_class(
        conn, tmp_path):
    bootstrap_p1_p7(conn)
    root = tmp_path / "corpus"
    root.mkdir()
    (root / "broken.pdf").write_bytes(b"%PDF broken")
    selection_id = record_selection(
        conn, sources=[root], candidate_roots=[], cross_folder_moves=False,
        selected_by=None)

    def classify(db, file_id, content_hash):
        evidence_ref = db.execute(
            "SELECT observation_key FROM evidence WHERE file_id = ? "
            "ORDER BY rowid LIMIT 1", (file_id,)).fetchone()[0]
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class="personal_non_sensitive", protected=False,
            basis="detector", evidence_refs=(evidence_ref,),
            reliability_state="direct", observed_at=CLOCK)

    ocr_calls = []
    result = run_production_p1_p7(
        conn, selection_id,
        authorities=_authorities(
            readers=_readers(ocr_calls), classify=classify))

    assert len(ocr_calls) == 1
    assert len(result.fact_results) == 1
    assert len(result.fact_results[0]) == 2
    assert conn.execute("SELECT count(*) FROM file_facts").fetchone()[0] == 2
    assert conn.execute("SELECT count(*) FROM fact_passes").fetchone()[0] == 2
    file_row = conn.execute(
        "SELECT sensitivity_state FROM files").fetchone()
    assert "personal_non_sensitive" in file_row[0]
    assert conn.execute(
        "SELECT count(*) FROM events WHERE event_type = ?",
        (CLASSIFICATION_ASSIGNED,)).fetchone()[0] == 1
    assert bundle_files(conn, result.bundle_id)[0]["handling_class"] \
        == "personal_non_sensitive"


def test_missing_classification_authority_fails_before_scan_or_run_rows(
        conn, tmp_path):
    bootstrap_p1_p7(conn)
    root = tmp_path / "corpus"
    root.mkdir()
    (root / "file.pdf").write_bytes(b"%PDF")
    selection_id = record_selection(
        conn, sources=[root], candidate_roots=[], cross_folder_moves=False,
        selected_by=None)
    kwargs = dict(_authorities(readers=_readers([]), classify=lambda *args: None).__dict__)
    kwargs["classify"] = None

    with pytest.raises(MissingClassificationAuthority):
        run_production_p1_p7(
            conn, selection_id, authorities=P1P7Authorities(**kwargs))

    assert conn.execute("SELECT count(*) FROM scan_runs").fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM extraction_runs").fetchone()[0] == 0
