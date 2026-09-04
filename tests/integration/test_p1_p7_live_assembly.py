"""The live caller crosses P1 through P7 in the design's required order."""
from pathlib import Path
import json

import pytest

from database_agent.db import create_schema
from eval_harness.bundle import (
    bundle_files, extraction_outputs as bundle_outputs,
    extraction_runs as bundle_runs, text_units as bundle_text_units,
)
from eval_harness.store import create_eval_schema
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter, observation_keys_for_run, result_for_run
from extractors.archive import ArchiveManifest
from extractors.dispatch import Readers
from extractors.failure import ContractViolation
from extractors.docx import DocxDocument
from extractors.image import ImageRecord
from extractors.long_tail import LongTailFile
from extractors.ocr import OcrOutput, OcrRegion
from extractors.pdf import PdfDocument, PdfPage
from extractors.reading import Region, StructuredString
from extractors.safety import SafetyPolicy
from extractors.sink import ExtractionResult
from extractors.schema import create_extraction_schema
from extractors.structured_text import TextDocument
from facts.schema import create_facts_schema
from facts.usable import passes_for, record_pass, targeted_ocr_needed_for
from extraction_pool import ExtractionContext, InlinePool
from orchestrator import P1P7Run, run_p1_p7
from privacy.classification import ClassificationRecord
from privacy.authorship import CLASSIFICATION_ASSIGNED
from privacy.classification_store import ClassificationStore
from privacy.schema import create_privacy_schema
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection


CLOCK = "2026-08-25T12:00:00+00:00"


@pytest.fixture()
def live_db(conn):
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_facts_schema(conn)
    create_privacy_schema(conn)
    create_eval_schema(conn)
    return conn


def _readers(ocr_calls, *, pdf_text="broken text", ocr_error=None,
             structured=False, ocr_available=True):
    pages = ((PdfPage(
        number=1, text=pdf_text,
        regions=(Region(zone="body", start=0, end=len(pdf_text)),)),)
             if pdf_text else ())

    def run_ocr(path, config):
        ocr_calls.append(path)
        if ocr_error is not None:
            raise ocr_error
        return OcrOutput(
            provider="test", provider_version="1",
            regions=(OcrRegion(page=1, region=1, text="usable OCR"),),
            pages_processed=1, pages_total=1)

    return Readers(
        read_pdf=lambda path: PdfDocument(
            metadata={}, pages=pages),
        read_docx=lambda path: DocxDocument(core_properties={}),
        read_text_document=lambda path: TextDocument(text="text"),
        read_long_tail=lambda path, transcribe=False: LongTailFile(),
        read_manifest=lambda path: ArchiveManifest(archive_type="zip"),
        read_image=lambda path: ImageRecord(
            image_format="PNG", dimensions="1x1", width=1, height=1),
        find_structured_strings=lambda text: (
            (StructuredString(kind="identifier", start=0, end=6),)
            if structured and text else ()),
        recognize_markers=lambda names: (),
        dimension_signal=lambda width, height: None,
        filename_pattern=lambda name: None,
        ocr_engine=run_ocr if ocr_available else None,
    )


#: Nothing is protected and nothing is dataless: these two tests are about
#: ORDER, and a refusal here would stop the run before the order was visible.
_open_policy = SafetyPolicy(is_protected_container=lambda path: False,
                            is_dataless=lambda path: False)


def _call(live_db, root, *, supplied_readers, resolve_native,
          targeted_ocr_needed, resolve_with_ocr, classify, policy=None):
    selection = record_selection(
        live_db, sources=[root], candidate_roots=[], cross_folder_moves=False,
        selected_by=None)
    policy = policy or SafetyPolicy(
        is_protected_container=lambda path: False,
        is_dataless=lambda path: False)
    return run_p1_p7(
        live_db, selection, source=FilesystemCorpusSource(),
        mime_type_for=lambda path: "application/pdf", scan_state="scanned",
        budget_exhausted=lambda: False, detect_format=lambda path: "pdf",
        policy=policy,
        # This thread, the same call order, and the SAME policy object -- so the
        # protected-container predicate a test installs is the one the extraction
        # actually runs under, not a second one that agrees today.
        pool=InlinePool(ExtractionContext(
            policy=policy, readers=supplied_readers,
            transcription_authorized=lambda: False)),
        readers=supplied_readers, sink=RunWriter(live_db, author="P5"),
        now=lambda: CLOCK, context_window=40,
        transcription_authorized=lambda: False, corpus_form="snapshot",
        policy_settings={}, file_entry_body=lambda row: {"payload_ref": "blob"},
        resolve_native=resolve_native,
        targeted_ocr_needed=targeted_ocr_needed,
        resolve_with_ocr=resolve_with_ocr, classify=classify,
        classification_store=ClassificationStore(live_db),
        p7_component_version="0.1.0")


def test_live_assembly_orders_both_fact_passes_before_authoritative_p7_and_bundle(
        live_db, tmp_path):
    root = tmp_path / "corpus"
    root.mkdir()
    (root / "broken.pdf").write_bytes(b"%PDF broken")
    selection = record_selection(
        live_db, sources=[root], candidate_roots=[], cross_folder_moves=False,
        selected_by=None)
    calls = []
    ocr_calls = []
    store = ClassificationStore(live_db)

    def resolve_native(conn, file_id, content_hash):
        tiers = [r["analysis_tier"] for r in conn.execute(
            "SELECT analysis_tier FROM extraction_runs WHERE file_id = ?",
            (file_id,))]
        assert tiers.count("native") == 1 and "ocr" not in tiers
        calls.append(("facts-native", file_id))
        return "native-facts"

    def targeted(file_id, content_hash):
        assert calls[-1] == ("facts-native", file_id)
        calls.append(("targeted-predicate", file_id))
        return True

    def resolve_ocr(conn, file_id, content_hash):
        assert conn.execute(
            "SELECT count(*) FROM extraction_runs "
            "WHERE file_id = ? AND analysis_tier = 'ocr'", (file_id,)
        ).fetchone()[0] == 1
        calls.append(("facts-ocr", file_id))
        return "ocr-facts"

    def classify(conn, file_id, content_hash):
        assert calls[-1] == ("facts-ocr", file_id)
        calls.append(("classify", file_id))
        run_id = conn.execute(
            "SELECT run_id FROM extraction_runs WHERE file_id = ? "
            "ORDER BY rowid LIMIT 1", (file_id,)).fetchone()[0]
        evidence_refs = (observation_keys_for_run(conn, run_id)[0],)
        # A stronger prior can exist when a detector re-runs. The candidate is not
        # automatically authoritative; the caller must re-read P7 after assign().
        store.write(ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class="personal_non_sensitive", protected=False,
            basis="user", evidence_refs=evidence_refs,
            reliability_state="user_confirmed", observed_at=CLOCK))
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class="sensitive_personal", protected=True,
            basis="detector",
            evidence_refs=evidence_refs,
            reliability_state="direct", observed_at=CLOCK)

    result = run_p1_p7(
        live_db, selection, source=FilesystemCorpusSource(),
        mime_type_for=lambda path: "application/pdf", scan_state="scanned",
        budget_exhausted=lambda: False,
        detect_format=lambda path: "pdf", policy=_open_policy,
        pool=InlinePool(ExtractionContext(
            policy=_open_policy, readers=_readers(ocr_calls, structured=True),
            transcription_authorized=lambda: False)),
        readers=_readers(ocr_calls, structured=True),
        sink=RunWriter(live_db, author="P5"),
        now=lambda: CLOCK, context_window=40,
        transcription_authorized=lambda: False,
        corpus_form="snapshot", policy_settings={},
        file_entry_body=lambda row: {"payload_ref": "blob"},
        resolve_native=resolve_native, targeted_ocr_needed=targeted,
        resolve_with_ocr=resolve_ocr, classify=classify,
        classification_store=store, p7_component_version="0.1.0")

    assert isinstance(result, P1P7Run)
    assert [name for name, _ in calls] == [
        "facts-native", "targeted-predicate", "facts-ocr", "classify"]
    assert len(ocr_calls) == 1
    file_row = live_db.execute("SELECT file_id, content_hash FROM files").fetchone()
    assert store.current(file_row["file_id"], file_row["content_hash"]).handling_class \
        == "personal_non_sensitive"
    assert bundle_files(live_db, result.bundle_id)[0]["handling_class"] \
        == "personal_non_sensitive"
    assert result.fact_results == (("native-facts", "ocr-facts"),)


def test_live_assembly_bundles_unclassified_as_gate_outcome(live_db, tmp_path):
    root = tmp_path / "corpus"
    root.mkdir()
    (root / "known.pdf").write_bytes(b"%PDF known")
    selection = record_selection(
        live_db, sources=[root], candidate_roots=[], cross_folder_moves=False,
        selected_by=None)
    result = run_p1_p7(
        live_db, selection, source=FilesystemCorpusSource(),
        mime_type_for=lambda path: "application/pdf", scan_state="scanned",
        budget_exhausted=lambda: False, detect_format=lambda path: "pdf",
        policy=_open_policy,
        pool=InlinePool(ExtractionContext(
            policy=_open_policy, readers=_readers([]),
            transcription_authorized=lambda: False)),
        readers=_readers([]), sink=RunWriter(live_db, author="P5"),
        now=lambda: CLOCK, context_window=40,
        transcription_authorized=lambda: False, corpus_form="snapshot",
        policy_settings={}, file_entry_body=lambda row: {"payload_ref": "blob"},
        resolve_native=lambda conn, file_id, content_hash: "native",
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda conn, file_id, content_hash: pytest.fail(
            "no OCR pass means no second P6 pass"),
        classify=lambda conn, file_id, content_hash: None,
        classification_store=ClassificationStore(live_db),
        p7_component_version="0.1.0")
    assert bundle_files(live_db, result.bundle_id)[0]["handling_class"] \
        == "unreadable_unclassified"


def test_fact_results_are_attributable_to_each_exact_file_version(live_db, tmp_path):
    root = tmp_path / "two-files"
    root.mkdir()
    (root / "a.pdf").write_bytes(b"%PDF a")
    (root / "b.pdf").write_bytes(b"%PDF b")

    def resolve_native(conn, file_id, content_hash):
        return f"facts:{file_id}:{content_hash}"

    result = _call(
        live_db, root, supplied_readers=_readers([]),
        resolve_native=resolve_native,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda conn, file_id, content_hash: pytest.fail(
            "no targeted OCR was requested"),
        classify=lambda conn, file_id, content_hash: None)

    expected_versions = {
        (row["file_id"], row["content_hash"])
        for row in live_db.execute("SELECT file_id, content_hash FROM files")
    }
    assert {
        (item.file_id, item.content_hash)
        for item in result.fact_results_by_file
    } == expected_versions
    assert all(
        item.results == (f"facts:{item.file_id}:{item.content_hash}",)
        for item in result.fact_results_by_file)
    assert result.fact_results == tuple(
        item.results for item in result.fact_results_by_file)


def test_content_change_creates_new_version_and_reuse_preserves_p6_p7_history(
        live_db, tmp_path):
    root = tmp_path / "versioned"
    root.mkdir()
    document = root / "document.pdf"
    document.write_bytes(b"%PDF first")
    store = ClassificationStore(live_db)
    native = frozenset(("filesystem", "native"))

    def resolve_native(conn, file_id, content_hash):
        record_pass(conn, file_id=file_id, content_hash=content_hash,
                    analysis_tiers=native)
        return content_hash

    def classify(conn, file_id, content_hash):
        evidence_ref = conn.execute(
            "SELECT observation_key FROM evidence WHERE file_id = ? "
            "ORDER BY rowid LIMIT 1", (file_id,)).fetchone()[0]
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class="personal_non_sensitive", protected=False,
            basis="detector", evidence_refs=(evidence_ref,),
            reliability_state="direct", observed_at=CLOCK)

    first = _call(
        live_db, root, supplied_readers=_readers([]),
        resolve_native=resolve_native,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda *args: pytest.fail("OCR was not requested"),
        classify=classify)
    old = dict(live_db.execute(
        "SELECT file_id, content_hash FROM files").fetchone())

    document.write_bytes(b"%PDF second version")
    second = _call(
        live_db, root, supplied_readers=_readers([]),
        resolve_native=resolve_native,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda *args: pytest.fail("OCR was not requested"),
        classify=classify)
    current = dict(live_db.execute(
        "SELECT file_id, content_hash FROM files "
        "WHERE scan_state <> 'superseded_content'").fetchone())
    assert current != old

    third = _call(
        live_db, root, supplied_readers=_readers([]),
        resolve_native=resolve_native,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda *args: pytest.fail("OCR was not requested"),
        classify=classify)

    assert live_db.execute("SELECT count(*) FROM fact_passes").fetchone()[0] == 2
    assert passes_for(live_db, **old) == (native,)
    assert passes_for(live_db, **current) == (native,)
    assert store.current(**old).content_hash == old["content_hash"]
    assert store.current(**current).content_hash == current["content_hash"]
    assert len(store.history(old["file_id"])) == 1
    assert len(store.history(current["file_id"])) == 2
    assert json.loads(live_db.execute(
        "SELECT sensitivity_state FROM files WHERE file_id = ?",
        (current["file_id"],)).fetchone()[0])["content_hash"] \
        == current["content_hash"]
    assert {(row["file_id"], row["content_hash"])
            for row in bundle_files(live_db, first.bundle_id)} == {
                (old["file_id"], old["content_hash"])}
    for result in (second, third):
        assert {(row["file_id"], row["content_hash"])
                for row in bundle_files(live_db, result.bundle_id)} == {
                    (current["file_id"], current["content_hash"])}
        assert {row["content_hash"] for row in bundle_runs(live_db, result.bundle_id)} \
            == {current["content_hash"]}
        assert {row["content_hash"] for row in bundle_outputs(
            live_db, result.bundle_id)} == {current["content_hash"]}


def test_bundle_filters_stale_same_file_runs_but_keeps_versions_of_current_hash(
        live_db, tmp_path):
    root = tmp_path / "bundle-version-join"
    root.mkdir()
    (root / "document.pdf").write_bytes(b"%PDF current")
    first = _call(
        live_db, root, supplied_readers=_readers([], structured=True),
        resolve_native=lambda conn, file_id, content_hash: None,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda *args: pytest.fail("OCR was not requested"),
        classify=lambda conn, file_id, content_hash: None)
    file_row = dict(live_db.execute(
        "SELECT file_id, content_hash FROM files").fetchone())
    native_id = next(
        run_id for run_id in first.run_ids
        if live_db.execute(
            "SELECT analysis_tier FROM extraction_runs WHERE run_id = ?",
            (run_id,)).fetchone()[0] == "native")
    original = result_for_run(live_db, native_id)

    def clone(*, content_hash, extractor_version):
        run = dict(original.run)
        run.pop("run_id")
        run["content_hash"] = content_hash
        run["extractor_version"] = extractor_version
        observations = []
        for original_observation in original.observations:
            observation = dict(original_observation)
            for key in ("observation_id", "record_id", "observation_key", "run_id"):
                observation.pop(key, None)
            observation["content_hash"] = content_hash
            observation["extractor_version"] = extractor_version
            observations.append(observation)
        units = []
        for original_unit in original.text_units:
            unit = dict(original_unit)
            unit.pop("run_id", None)
            units.append(unit)
        return RunWriter(live_db, author="P5").write(ExtractionResult(
            run=run, observations=tuple(observations), text_units=tuple(units)))

    stale_id = clone(content_hash="0" * 64, extractor_version="0.1.0")
    current_v2_id = clone(
        content_hash=file_row["content_hash"], extractor_version="fixture-v2")

    bundled = _call(
        live_db, root, supplied_readers=_readers([], structured=True),
        resolve_native=lambda conn, file_id, content_hash: None,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda *args: pytest.fail("OCR was not requested"),
        classify=lambda conn, file_id, content_hash: None)
    runs = bundle_runs(live_db, bundled.bundle_id)
    included_ids = {row["run_id"] for row in runs}
    assert stale_id not in included_ids
    assert {native_id, current_v2_id} <= included_ids
    assert {row["content_hash"] for row in runs} == {file_row["content_hash"]}
    assert {row["content_hash"] for row in bundle_outputs(
        live_db, bundled.bundle_id)} == {file_row["content_hash"]}
    assert {row["run_id"] for row in bundle_text_units(
        live_db, bundled.bundle_id)} == included_ids


def test_late_failure_keeps_part_evidence_and_new_reuse_scan_finishes_cleanly(
        live_db, tmp_path):
    root = tmp_path / "resume"
    root.mkdir()
    (root / "a.pdf").write_bytes(b"%PDF a")
    (root / "b.pdf").write_bytes(b"%PDF b")
    native = frozenset(("filesystem", "native"))
    attempts = 0

    def resolve_native(conn, file_id, content_hash):
        record_pass(conn, file_id=file_id, content_hash=content_hash,
                    analysis_tiers=native)
        return content_hash

    def candidate(conn, file_id, content_hash):
        nonlocal attempts
        attempts += 1
        if attempts == 2:
            raise RuntimeError("late detector failure")
        evidence_ref = conn.execute(
            "SELECT observation_key FROM evidence WHERE file_id = ? "
            "ORDER BY rowid LIMIT 1", (file_id,)).fetchone()[0]
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class="personal_non_sensitive", protected=False,
            basis="detector", evidence_refs=(evidence_ref,),
            reliability_state="direct", observed_at=CLOCK)

    with pytest.raises(RuntimeError, match="late detector failure"):
        _call(
            live_db, root, supplied_readers=_readers([]),
            resolve_native=resolve_native,
            targeted_ocr_needed=lambda file_id, content_hash: False,
            resolve_with_ocr=lambda *args: pytest.fail("OCR was not requested"),
            classify=candidate)

    assert live_db.execute("SELECT count(*) FROM extraction_runs").fetchone()[0] == 4
    assert live_db.execute("SELECT count(*) FROM fact_passes").fetchone()[0] == 2
    assert live_db.execute("SELECT count(*) FROM classifications").fetchone()[0] == 1
    assert live_db.execute("SELECT count(*) FROM bundle_manifest").fetchone()[0] == 0

    attempts = 100
    resumed = _call(
        live_db, root, supplied_readers=_readers([]),
        resolve_native=resolve_native,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda *args: pytest.fail("OCR was not requested"),
        classify=candidate)

    assert resumed.run_ids == ()
    assert live_db.execute("SELECT count(*) FROM extraction_runs").fetchone()[0] == 4
    assert live_db.execute("SELECT count(*) FROM fact_passes").fetchone()[0] == 2
    assert live_db.execute("SELECT count(*) FROM classifications").fetchone()[0] == 3
    assert live_db.execute(
        "SELECT count(*) FROM events WHERE event_type = ?",
        (CLASSIFICATION_ASSIGNED,)).fetchone()[0] == 3
    assert live_db.execute(
        "SELECT count(*) FROM bundle_manifest WHERE sealed_at IS NOT NULL"
    ).fetchone()[0] == 1
    assert len(bundle_files(live_db, resumed.bundle_id)) == 2
    for row in live_db.execute(
            "SELECT file_id, content_hash, sensitivity_state FROM files"):
        assert ClassificationStore(live_db).current(
            row["file_id"], row["content_hash"]) is not None
        assert json.loads(row["sensitivity_state"])["content_hash"] \
            == row["content_hash"]


def test_direct_ocr_is_part_of_the_first_p6_pass_only(live_db, tmp_path):
    root = tmp_path / "direct"
    root.mkdir()
    (root / "scan.pdf").write_bytes(b"%PDF scan")
    calls = []
    _call(
        live_db, root, supplied_readers=_readers([], pdf_text=""),
        resolve_native=lambda conn, file_id, content_hash: pytest.fail(
            "successful direct OCR must use the OCR-covered P6 resolver"),
        targeted_ocr_needed=lambda file_id, content_hash: pytest.fail(
            "direct OCR must not ask the targeted predicate"),
        resolve_with_ocr=lambda conn, file_id, content_hash: calls.append("first"),
        classify=lambda conn, file_id, content_hash: calls.append("classify"))
    assert calls == ["first", "classify"]


def test_failed_direct_ocr_uses_native_pass_without_claiming_ocr_coverage(
        live_db, tmp_path):
    root = tmp_path / "failed-direct"
    root.mkdir()
    (root / "scan.pdf").write_bytes(b"%PDF scan")
    calls = []
    _call(
        live_db, root,
        supplied_readers=_readers([], pdf_text="", ocr_error=RuntimeError("down")),
        resolve_native=lambda conn, file_id, content_hash: calls.append("native"),
        targeted_ocr_needed=lambda file_id, content_hash: pytest.fail(
            "a direct-OCR route must not become targeted OCR"),
        resolve_with_ocr=lambda conn, file_id, content_hash: pytest.fail(
            "failed OCR must not claim OCR-covered facts"),
        classify=lambda conn, file_id, content_hash: calls.append("classify"))
    assert calls == ["native", "classify"]


def test_direct_ocr_reuse_uses_persisted_ocr_coverage_as_single_p6_pass(
        live_db, tmp_path):
    root = tmp_path / "direct-reuse"
    root.mkdir()
    (root / "scan.pdf").write_bytes(b"%PDF scan")
    first = _call(
        live_db, root, supplied_readers=_readers([], pdf_text=""),
        resolve_native=lambda *args: pytest.fail(
            "successful direct OCR is already OCR-covered"),
        targeted_ocr_needed=lambda *args: pytest.fail(
            "direct OCR must not ask the targeted predicate"),
        resolve_with_ocr=lambda conn, file_id, content_hash: "initial-ocr",
        classify=lambda conn, file_id, content_hash: None)
    assert first.fact_results_by_file[0].results == ("initial-ocr",)

    second_ocr_calls = []
    second = _call(
        live_db, root,
        supplied_readers=_readers(second_ocr_calls, pdf_text=""),
        resolve_native=lambda *args: pytest.fail(
            "persisted successful OCR must not regress to native-only facts"),
        targeted_ocr_needed=lambda *args: pytest.fail(
            "persisted direct OCR must not become targeted OCR"),
        resolve_with_ocr=lambda conn, file_id, content_hash: "reuse-ocr",
        classify=lambda conn, file_id, content_hash: None)
    assert second.run_ids == ()
    assert second_ocr_calls == []
    assert second.fact_results_by_file[0].results == ("reuse-ocr",)


def test_failed_targeted_ocr_does_not_trigger_second_p6_pass(live_db, tmp_path):
    root = tmp_path / "failed-targeted"
    root.mkdir()
    (root / "broken.pdf").write_bytes(b"%PDF broken")
    calls = []
    _call(
        live_db, root,
        supplied_readers=_readers([], ocr_error=RuntimeError("vision failed")),
        resolve_native=lambda conn, file_id, content_hash: calls.append("first"),
        targeted_ocr_needed=lambda file_id, content_hash: True,
        resolve_with_ocr=lambda conn, file_id, content_hash: pytest.fail(
            "a failed zero-observation OCR run added no evidence"),
        classify=lambda conn, file_id, content_hash: calls.append("classify"))
    assert calls == ["first", "classify"]


def test_classifier_candidate_must_match_requested_file_version(live_db, tmp_path):
    root = tmp_path / "mismatch"
    root.mkdir()
    (root / "known.pdf").write_bytes(b"%PDF known")

    def wrong_candidate(conn, file_id, content_hash):
        run_id = conn.execute(
            "SELECT run_id FROM extraction_runs WHERE file_id = ? LIMIT 1",
            (file_id,)).fetchone()[0]
        return ClassificationRecord(
            file_id="another-file", content_hash=content_hash,
            handling_class="sensitive_personal", protected=True,
            basis="detector",
            evidence_refs=(observation_keys_for_run(conn, run_id)[0],),
            reliability_state="direct", observed_at=CLOCK)

    with pytest.raises(ContractViolation, match="candidate.*file version"):
        _call(
            live_db, root, supplied_readers=_readers([]),
            resolve_native=lambda conn, file_id, content_hash: None,
            targeted_ocr_needed=lambda file_id, content_hash: False,
            resolve_with_ocr=lambda conn, file_id, content_hash: None,
            classify=wrong_candidate)
    assert live_db.execute(
        "SELECT count(*) FROM classifications").fetchone()[0] == 0


def test_targeted_ocr_runs_at_most_once(live_db, tmp_path):
    root = tmp_path / "once"
    root.mkdir()
    (root / "broken.pdf").write_bytes(b"%PDF broken")
    ocr_calls = []
    predicate_calls = []
    _call(
        live_db, root, supplied_readers=_readers(ocr_calls),
        resolve_native=lambda conn, file_id, content_hash: None,
        targeted_ocr_needed=lambda file_id, content_hash:
        predicate_calls.append(file_id) or True,
        resolve_with_ocr=lambda conn, file_id, content_hash: None,
        classify=lambda conn, file_id, content_hash: None)
    assert len(predicate_calls) == len(ocr_calls) == 1


def test_reuse_uses_the_only_authoritative_persisted_native_result_once(
        live_db, tmp_path):
    root = tmp_path / "reuse"
    root.mkdir()
    (root / "broken.pdf").write_bytes(b"%PDF broken")
    first_ocr = []
    _call(
        live_db, root, supplied_readers=_readers(first_ocr, structured=True),
        resolve_native=lambda conn, file_id, content_hash: None,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda conn, file_id, content_hash: None,
        classify=lambda conn, file_id, content_hash: None)
    assert first_ocr == []

    second_ocr = []
    predicates = []
    second_fact_passes = []
    _call(
        live_db, root, supplied_readers=_readers(second_ocr, structured=True),
        resolve_native=lambda conn, file_id, content_hash: None,
        targeted_ocr_needed=lambda file_id, content_hash:
        predicates.append(file_id) or True,
        resolve_with_ocr=lambda conn, file_id, content_hash:
        second_fact_passes.append(file_id),
        classify=lambda conn, file_id, content_hash: None)
    assert len(predicates) == len(second_ocr) == len(second_fact_passes) == 1

    third_ocr = []
    third_fact_passes = []
    third = _call(
        live_db, root, supplied_readers=_readers(third_ocr, structured=True),
        resolve_native=lambda *args: pytest.fail(
            "persisted OCR coverage must use the OCR-covered resolver"),
        targeted_ocr_needed=lambda *args: pytest.fail(
            "persisted OCR coverage must terminate targeted OCR"),
        resolve_with_ocr=lambda conn, file_id, content_hash:
        third_fact_passes.append(file_id) or "persisted-ocr",
        classify=lambda conn, file_id, content_hash: None)
    assert third_ocr == []
    assert len(third_fact_passes) == 1
    assert third.fact_results_by_file[0].results == ("persisted-ocr",)


def test_reuse_refuses_ambiguous_native_authority_instead_of_choosing_latest(
        live_db, tmp_path):
    root = tmp_path / "ambiguous-reuse"
    root.mkdir()
    (root / "broken.pdf").write_bytes(b"%PDF broken")
    _call(
        live_db, root, supplied_readers=_readers([], structured=True),
        resolve_native=lambda conn, file_id, content_hash: None,
        targeted_ocr_needed=lambda file_id, content_hash: False,
        resolve_with_ocr=lambda conn, file_id, content_hash: None,
        classify=lambda conn, file_id, content_hash: None)
    original_run_id = live_db.execute(
        "SELECT run_id FROM extraction_runs WHERE extractor_name = 'pdf.text'"
    ).fetchone()[0]
    original = result_for_run(live_db, original_run_id)
    duplicate_run = dict(original.run)
    duplicate_run.pop("run_id")
    RunWriter(live_db, author="P5").write(ExtractionResult(
        run=duplicate_run, observations=original.observations,
        text_units=original.text_units))

    with pytest.raises(ContractViolation, match="authoritative.*persisted.*run"):
        _call(
            live_db, root, supplied_readers=_readers([], structured=True),
            resolve_native=lambda conn, file_id, content_hash: None,
            targeted_ocr_needed=lambda file_id, content_hash: True,
            resolve_with_ocr=lambda conn, file_id, content_hash: None,
            classify=lambda conn, file_id, content_hash: None)


def test_a_native_pass_with_no_citable_strings_reuses_and_terminates(
        live_db, tmp_path):
    root = tmp_path / "real-predicate-reuse"
    root.mkdir()
    (root / "broken.pdf").write_bytes(b"%PDF broken")
    native = frozenset({"native"})
    with_ocr = frozenset({"native", "ocr"})
    predicate = targeted_ocr_needed_for(
        live_db, usable_threshold=lambda facts, unresolved: False)

    def resolve_native(conn, file_id, content_hash):
        record_pass(conn, file_id=file_id, content_hash=content_hash,
                    analysis_tiers=native)

    def resolve_ocr(conn, file_id, content_hash):
        record_pass(conn, file_id=file_id, content_hash=content_hash,
                    analysis_tiers=with_ocr)

    # ONE OBSERVATION, AND IT WAS ZERO UNTIL `acb462a`. This fixture builds a page
    # with nonblank text whose finder emits no structured strings, and that used to
    # be a run with nothing to cite. `acb462a` made a page's PROSE an observation in
    # its own right, so the same page now carries exactly one.
    #
    # The count is a premise here and not the subject: what this test guards is that
    # the real P6 native-pass decision persists and that the OCR retry terminates,
    # and both are unchanged -- the assertion moved from 0 to 1 and every other
    # assertion below passed untouched.
    #
    # WHAT IS NO LONGER COVERED, said plainly rather than left as a stale name: a
    # genuinely zero-observation run. That shape still exists and still matters --
    # `cli.files_with_observations` keys on `observation_count > 0`, and a scanned
    # PDF renders pages, stores their empty text and has nothing to cite. Three of
    # the owner's own homework PDFs are photographs that do exactly this. Building it
    # here needs a page whose text is blank, which changes what the OCR predicate
    # does and is a different test rather than a smaller edit to this one.
    #
    # OCR is unavailable in this invocation, leaving the real P6 native-pass
    # decision persisted for REUSE.
    first_ocr = []
    _call(
        live_db, root,
        supplied_readers=_readers(first_ocr, structured=False,
                                  ocr_available=False),
        resolve_native=resolve_native, targeted_ocr_needed=predicate,
        resolve_with_ocr=resolve_ocr,
        classify=lambda conn, file_id, content_hash: None)
    assert first_ocr == []
    native_run = live_db.execute(
        "SELECT run_id, observation_count FROM extraction_runs "
        "WHERE extractor_name = 'pdf.text'"
    ).fetchone()
    assert native_run["observation_count"] == 1

    second_ocr = []
    _call(
        live_db, root, supplied_readers=_readers(second_ocr, structured=False),
        resolve_native=resolve_native, targeted_ocr_needed=predicate,
        resolve_with_ocr=resolve_ocr,
        classify=lambda conn, file_id, content_hash: None)
    assert len(second_ocr) == 1
    file_version = live_db.execute(
        "SELECT file_id, content_hash FROM files").fetchone()
    assert with_ocr in passes_for(
        live_db, file_id=file_version["file_id"],
        content_hash=file_version["content_hash"])

    third_ocr = []
    third_fact_passes = []
    third = _call(
        live_db, root, supplied_readers=_readers(third_ocr, structured=False),
        resolve_native=lambda *args: pytest.fail(
            "persisted OCR coverage must use the OCR-covered resolver"),
        targeted_ocr_needed=lambda *args: pytest.fail(
            "the persisted OCR-covered pass must terminate retries"),
        resolve_with_ocr=lambda conn, file_id, content_hash:
        third_fact_passes.append(file_id) or resolve_ocr(
            conn, file_id, content_hash),
        classify=lambda conn, file_id, content_hash: None)
    assert third_ocr == []
    assert len(third_fact_passes) == 1
    assert len(third.fact_results_by_file) == 1


def test_protected_refusal_never_reaches_facts_or_classification(live_db, tmp_path):
    root = tmp_path / "protected"
    root.mkdir()
    (root / "protected.pdf").write_bytes(b"%PDF protected")
    _call(
        live_db, root, supplied_readers=_readers([]),
        policy=SafetyPolicy(is_protected_container=lambda path: True,
                            is_dataless=lambda path: False),
        resolve_native=lambda conn, file_id, content_hash: pytest.fail(
            "protected refusal must not reach P6"),
        targeted_ocr_needed=lambda file_id, content_hash: pytest.fail(
            "protected refusal must not reach targeted OCR"),
        resolve_with_ocr=lambda conn, file_id, content_hash: pytest.fail(
            "protected refusal must not reach P6"),
        classify=lambda conn, file_id, content_hash: pytest.fail(
            "protected refusal must not reach P7"))
    assert live_db.execute(
        "SELECT count(*) FROM extraction_runs").fetchone()[0] == 0
    assert live_db.execute(
        "SELECT extraction_status_by_tier FROM files").fetchone()[0] == "{}"
