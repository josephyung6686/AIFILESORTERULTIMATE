"""The seam, bound rather than assumed.

This project's rule: *a seam is verified when the caller's arguments have been bound
against the callee's live signature, or when a test drives the real callee end to
end — never when a reference chain exists between them.* So this file does not mock
`run_p1_p7`. It composes the REAL `production.P1P7Authorities` with the real
detector as its `classify`, runs the real pipeline over a real corpus on disk, and
reads what P7's own store holds afterwards.

Before this package existed, `P1P7Authorities.__post_init__` raised
`MissingClassificationAuthority` — *"P7 classification requires an explicit
producer; no detector or domain default exists"* — and every file failed at
construction. `test_production_still_refuses_to_run_without_a_classification_authority`
keeps that refusal alive, because the fix is a supplier, not a default.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from extractors.archive import ArchiveManifest
from extractors.dispatch import Readers
from extractors.docx import DocxDocument
from extractors.image import ImageRecord
from extractors.long_tail import LongTailFile
from extractors.pdf import PdfDocument, PdfPage
from extractors.reading import Region
from extractors.safety import SafetyPolicy
from extractors.structured_text import TextDocument
from facts.resolver import FactResolver
from facts.usable import record_pass
from privacy.classification import UNREADABLE_UNCLASSIFIED, resolve_class
from privacy.classification_store import ClassificationStore
from production import (
    InvalidP1P7Authority, MissingClassificationAuthority, P1P7Authorities,
    bootstrap_p1_p7, run_production_p1_p7,
)
from recognition.detector import Detector, SAFETY_DOMAIN_HANDLING
from recognition.rules import load_rules
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.exclusion import is_protected_container
from scan_agent.selection import record_selection

CLOCK = "2026-08-28T12:00:00+00:00"
COMPONENT = "0.1.0"
MANIFEST_PATH = (Path(__file__).resolve().parents[2] / "src" / "recognition"
                 / "library" / "recognition.json")
BUNDLE_MARKER = "BUNDLE-INTERIOR-MUST-NOT-BE-READ"

#: Two authored `finance` terms in one filename. Neither is enough on its own --
#: that is what `never_alone` means -- and the pair is what `00`'s co-occurrence
#: rule asks for.
FINANCE_FILE = "Bank statement - account number and closing balance.pdf"
#: A file whose filename carries nothing any schema authored.
SILENT_FILE = "IMG_5512.pdf"


def _rules():
    return load_rules(MANIFEST_PATH.read_text)


def _readers(page_text: str = "") -> Readers:
    pages = ((PdfPage(number=1, text=page_text,
                      regions=(Region(zone="body", start=0, end=len(page_text)),)),)
             if page_text else ())
    return Readers(
        read_pdf=lambda path: PdfDocument(metadata={}, pages=pages),
        read_docx=lambda path: DocxDocument(core_properties={}),
        read_text_document=lambda path: TextDocument(text="text"),
        read_long_tail=lambda path, transcribe=False: LongTailFile(),
        read_manifest=lambda path: ArchiveManifest(archive_type="zip"),
        read_image=lambda path: ImageRecord(image_format="PNG", dimensions="1x1",
                                            width=1, height=1),
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda width, height: None,
        filename_pattern=lambda name: None,
        ocr_engine=None,
    )


def _resolver(*, tiers: frozenset[str], cache_key: str) -> FactResolver:
    return FactResolver(
        stages={"direct": lambda conn, file_id, content_hash: (),
                "rule": None, "llm": None},
        pending_fields=lambda conn, file_id, content_hash: (),
        budget_exhausted=lambda ceiling: False,
        model_route_permitted=lambda file_id: False,
        record_pass=lambda conn, file_id, content_hash: record_pass(
            conn, file_id=file_id, content_hash=content_hash, analysis_tiers=tiers),
        cache_key_for=lambda file_id, content_hash: f"{cache_key}:{content_hash}",
        screen_metadata=lambda conn, file_id, content_hash: ())


def _authorities(classify) -> P1P7Authorities:
    return P1P7Authorities(
        native_resolver=_resolver(tiers=frozenset(("filesystem", "native")),
                                  cache_key="native-v1"),
        ocr_resolver=_resolver(tiers=frozenset(("filesystem", "native", "ocr")),
                               cache_key="ocr-v1"),
        usable_threshold=lambda facts, unresolved: True,
        classify=classify,
        source=FilesystemCorpusSource(),
        mime_type_for=lambda path: (
            "application/pdf" if Path(path).suffix == ".pdf" else None),
        scan_state="scanned",
        scan_budget_exhausted=lambda: False,
        detect_format=lambda path: (
            "pdf" if Path(path).suffix == ".pdf" else None),
        # The REAL protected-container predicate, through the real pipeline.
        policy=SafetyPolicy(is_protected_container=is_protected_container,
                            is_dataless=lambda path: False),
        readers=_readers(), now=lambda: CLOCK, context_window=64,
        transcription_authorized=lambda: False, corpus_form="snapshot",
        policy_settings={}, file_entry_body=lambda row: {"payload_ref": "blob"},
        p7_component_version=COMPONENT)


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    root.mkdir()
    (root / FINANCE_FILE).write_bytes(b"%PDF-1.4 finance")
    (root / SILENT_FILE).write_bytes(b"%PDF-1.4 silent")
    (root / "Numbers.app" / "Contents").mkdir(parents=True)
    (root / "Numbers.app" / "Contents" / "sheet.numbers").write_text(BUNDLE_MARKER)
    return root


@pytest.fixture()
def live(conn):
    bootstrap_p1_p7(conn)
    return conn


def _run(live, corpus, classify):
    selection = record_selection(live, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return run_production_p1_p7(live, selection, authorities=_authorities(classify))


# --- the gap this package closes ----------------------------------------------

def test_production_still_refuses_to_run_without_a_classification_authority():
    # The refusal is not removed by supplying a detector; it is what makes the
    # detector an explicit authority instead of a default nobody chose.
    with pytest.raises(MissingClassificationAuthority):
        _authorities(None)
    with pytest.raises(InvalidP1P7Authority):
        _authorities("a detector")


def test_the_detector_satisfies_the_live_ClassificationProducer_signature(
        live, corpus):
    """One real file, classified, through `production.run_production_p1_p7`.

    Nothing is mocked between this test and P7's store: the record read back at the
    end was written by `orchestrator.assign` from the candidate the detector
    returned when the orchestrator called it."""
    detector = Detector(_rules(), handling_for=SAFETY_DOMAIN_HANDLING,
                        now=lambda: CLOCK)
    result = _run(live, corpus, detector)

    store = ClassificationStore(live)
    classified = {}
    for row in live.execute("SELECT file_id, filename, content_hash FROM files"):
        record = store.current(row["file_id"], row["content_hash"])
        if record is not None:
            classified[row["filename"]] = record

    assert FINANCE_FILE in classified, "the finance file was not classified"
    record = classified[FINANCE_FILE]
    assert record.handling_class == "sensitive_personal"
    assert record.protected is True
    assert record.basis == "safety_domain"
    assert record.reliability_state == "possible"
    assert record.evidence_refs
    assert result.bundle_id


def test_the_silent_file_is_left_unclassified_rather_than_guessed(live, corpus):
    """The negative twin, in the live pipeline. A detector that classified
    everything would pass the test above and this is what catches it."""
    detector = Detector(_rules(), handling_for=SAFETY_DOMAIN_HANDLING,
                        now=lambda: CLOCK)
    _run(live, corpus, detector)

    store = ClassificationStore(live)
    row = live.execute("SELECT file_id, content_hash FROM files WHERE filename = ?",
                       (SILENT_FILE,)).fetchone()
    assert row is not None, "the silent file must still be indexed"
    assert store.current(row["file_id"], row["content_hash"]) is None
    # §8.6/§8.4: absence resolves to the gate outcome, never down to `public_low`.
    assert resolve_class(store.current(row["file_id"], row["content_hash"])) == (
        UNREADABLE_UNCLASSIFIED)


def test_the_protected_bundle_is_never_opened_and_never_classified(live, corpus):
    """P3 never creates a `files` row inside a protected container, so the
    detector is never asked about one -- and the interior bytes are nowhere in the
    database. Asserted here rather than trusted, because a detector is exactly the
    part that would be tempted to open it."""
    detector = Detector(_rules(), handling_for=SAFETY_DOMAIN_HANDLING,
                        now=lambda: CLOCK)
    _run(live, corpus, detector)

    paths = [row["current_path"] for row in live.execute(
        "SELECT current_path FROM files")]
    assert not [path for path in paths if ".app" in path], paths
    assert not list(live.execute(
        "SELECT 1 FROM evidence WHERE raw_value LIKE ?", (f"%{BUNDLE_MARKER}%",)))
    # Marked and counted, not silently omitted: P3's own exclusion verdict is on
    # the record with the label the design gives it.
    verdicts = [dict(row) for row in live.execute(
        "SELECT path, rule, label FROM exclusion_verdicts")]
    assert [v for v in verdicts if v["label"] == "untouched_protected"], verdicts


def test_a_second_run_over_the_same_corpus_writes_no_second_live_record(
        live, corpus):
    """§8.2 supersedes rather than duplicates, and `strongest` raises on a tie at
    one rank. A detector that re-emitted the same candidate on every scan would
    make `current` unreadable, so the re-run is asserted rather than assumed."""
    detector = Detector(_rules(), handling_for=SAFETY_DOMAIN_HANDLING,
                        now=lambda: CLOCK)
    _run(live, corpus, detector)
    _run(live, corpus, detector)

    store = ClassificationStore(live)
    row = live.execute("SELECT file_id, content_hash FROM files WHERE filename = ?",
                       (FINANCE_FILE,)).fetchone()
    # `current` raises `AmbiguousCurrentClassification` on two live rows at one
    # rank, so simply calling it is the assertion.
    assert store.current(row["file_id"], row["content_hash"]).protected is True
