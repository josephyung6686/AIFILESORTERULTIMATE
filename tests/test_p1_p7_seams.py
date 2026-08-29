"""Live P1–P7 name-level joins.

This is the connection gate for the first shipped P6/P7 slice. It does not
implement a detector, does not wire Wave-2, and does not import planning/domains.
It asserts that the packages that exist today attach to P1–P5 under the ratified
decisions (D2, D5, D6, D7).
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

from database_agent.events import REGISTERED_EVENT_TYPES, RESERVED_EVENT_TYPES
from database_agent.files_table import get_file, record_file, set_sensitivity_state
from evidence_shape.observation import observation_key
from evidence_shape.vocabulary import RELIABILITY_STATES as P4_STATES
from extractors.long_tail import sensitivity_signals_for
from orchestrator import TARGETED_OCR_UNAVAILABLE, run_wave2

from facts.authorship import AUTHORED_EVENT_TYPES
from facts.states import STATES as P6_STATES, STRENGTH_ORDER

from privacy.authorship import P7_EVENT_TYPES, SUBSYSTEM
from privacy.classification import (
    UNREADABLE_UNCLASSIFIED, ClassificationRecord, resolve_class,
    sensitivity_signal_keys,
)
from privacy.classification_store import (
    ClassificationStore, RELIABILITY_ORDER, mirror,
)
from privacy.schema import create_privacy_schema
from privacy.vocabulary import DETECTOR, REJECTED, RELIABILITY_STATES as P7_STATES
from privacy.vocabulary import USER, USER_CONFIRMED

SRC = Path(__file__).resolve().parents[1] / "src"


def _imports_of(package_dir: Path) -> set[str]:
    roots: set[str] = set()
    for path in package_dir.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    roots.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".")[0])
    return roots


def test_p6_states_are_p4s_tuple_by_identity():
    assert P6_STATES is P4_STATES


def test_p7_reliability_states_are_p4s_tuple_by_identity():
    assert P7_STATES is P4_STATES


def test_p6_ladder_is_p7s_order_reversed():
    # P6 ranks weakest-first so a larger number is stronger. P7 ranks
    # strongest-first because that is P4's published order with rejected removed.
    # Same five states, opposite direction — a file of one must not silently
    # invert the other.
    assert tuple(reversed(STRENGTH_ORDER)) == RELIABILITY_ORDER
    assert REJECTED not in STRENGTH_ORDER
    assert REJECTED not in RELIABILITY_ORDER


def test_privacy_does_not_import_facts():
    # D7: P7 reads no P6 surface.
    assert "facts" not in _imports_of(SRC / "privacy")


def test_facts_does_not_import_privacy():
    assert "privacy" not in _imports_of(SRC / "facts")


def test_p7_event_types_are_registered_with_p1():
    for name in P7_EVENT_TYPES:
        assert name in REGISTERED_EVENT_TYPES, name


def test_p6_event_types_are_reserved_with_spaces():
    assert AUTHORED_EVENT_TYPES == ("fact creation", "fact rejection")
    for name in AUTHORED_EVENT_TYPES:
        assert name in RESERVED_EVENT_TYPES, name
        assert "_" not in name


def test_set_sensitivity_state_has_one_privacy_caller():
    callers = []
    for path in (SRC / "privacy").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = getattr(func, "id", None) or getattr(func, "attr", None)
                if name == "set_sensitivity_state":
                    callers.append(path.name)
    assert callers == ["classification_store.py"]


def test_absence_resolves_to_unreadable_never_public_low():
    assert resolve_class(None) == UNREADABLE_UNCLASSIFIED
    assert UNREADABLE_UNCLASSIFIED != "public_low"


def test_observation_key_is_accepted_as_evidence_ref():
    key = observation_key(
        content_hash="a" * 64, extractor_name="pdf_text",
        locator="zone=body/page=1", raw_value="PASSPORT",
    )
    record = ClassificationRecord(
        file_id="file-1", content_hash="a" * 64,
        handling_class="highly_sensitive_credential_bearing",
        protected=True, basis=DETECTOR, evidence_refs=(key,),
        reliability_state="validated", observed_at="2026-08-22T12:00:00+00:00",
    )
    assert record.evidence_refs == (key,)
    assert record.basis == DETECTOR


def test_mirror_projects_through_p1_setter(conn, tmp_path):
    create_privacy_schema(conn)
    path = tmp_path / "passport.pdf"
    path.write_bytes(b"scanned passport")
    file_id = record_file(
        conn, path, filename="passport.pdf", normalized_filename="passport",
        extension=".pdf", observed_size=path.stat().st_size,
        observed_timestamps="{}", parent_folder_context=None, mime_type=None,
        detected_format=None, scan_state="seen", materialized=True,
        content_hash="a" * 64,
    )
    key = observation_key(
        content_hash="a" * 64, extractor_name="pdf_text",
        locator="zone=ocr/page=1", raw_value="P<GBR",
    )
    record = ClassificationRecord(
        file_id=file_id, content_hash="a" * 64,
        handling_class="highly_sensitive_credential_bearing",
        protected=True, basis=DETECTOR, evidence_refs=(key,),
        reliability_state="validated", observed_at="2026-08-22T12:00:00+00:00",
    )
    store = ClassificationStore(conn)
    store.write(record)
    mirror(conn, record, component_version="P7/0.1.0")
    state = get_file(conn, file_id)["sensitivity_state"]
    assert '"handling_class": "highly_sensitive_credential_bearing"' in state
    assert '"protected": true' in state
    assert UNREADABLE_UNCLASSIFIED not in state


def test_unreadable_is_never_mirrored(conn, tmp_path):
    create_privacy_schema(conn)
    from privacy.classification_store import GateOutcomeNotAFileFact
    path = tmp_path / "x.pdf"
    path.write_bytes(b"x")
    file_id = record_file(
        conn, path, filename="x.pdf", normalized_filename="x",
        extension=".pdf", observed_size=1, observed_timestamps="{}",
        parent_folder_context=None, mime_type=None, detected_format=None,
        scan_state="seen", materialized=True, content_hash="b" * 64,
    )
    key = observation_key(
        content_hash="b" * 64, extractor_name="pdf_text",
        locator="zone=body/page=1", raw_value="?",
    )
    record = ClassificationRecord(
        file_id=file_id, content_hash="b" * 64,
        handling_class=UNREADABLE_UNCLASSIFIED, protected=False,
        basis=USER, evidence_refs=(), reliability_state=USER_CONFIRMED,
        observed_at="2026-08-22T12:00:00+00:00",
    )
    store = ClassificationStore(conn)
    try:
        store.write(record)
        raised = False
    except GateOutcomeNotAFileFact:
        raised = True
    assert raised
    try:
        mirror(conn, record, component_version="P7/0.1.0")
        mirrored = False
    except GateOutcomeNotAFileFact:
        mirrored = True
    assert mirrored
    assert get_file(conn, file_id)["sensitivity_state"] in (None, "")


def test_sensitivity_signals_for_is_keyed_by_run_id_only():
    assert list(inspect.signature(sensitivity_signals_for).parameters) == [
        "conn", "run_id",
    ]
    assert list(inspect.signature(sensitivity_signal_keys).parameters) == [
        "conn", "file_id",
    ]


def test_run_wave2_is_seventeen_params_with_no_gate():
    parameters = inspect.signature(run_wave2).parameters
    assert len(parameters) == 17
    for forbidden in ("gate", "release", "classifier", "detector",
                      "handling_class", "privacy_policy", "classification"):
        assert forbidden not in parameters, forbidden
    assert "no_usable_facts" in parameters


def test_targeted_ocr_stub_is_still_the_wave2_verdict():
    assert TARGETED_OCR_UNAVAILABLE("file-1", "a" * 64) is False
    assert "P6" in (TARGETED_OCR_UNAVAILABLE.__doc__ or "")


def test_orchestrator_still_passes_literal_none_for_handling_class():
    source = Path(inspect.getsourcefile(run_wave2)).read_text(encoding="utf-8")
    assert "handling_class=None" in source


def test_mirror_author_is_p7_not_a_caller_parameter():
    source = inspect.getsource(mirror)
    assert "author=SUBSYSTEM" in source
    assert SUBSYSTEM == "P7"
    # P1 still requires author=; P7 binds it. A caller of mirror cannot lie.
    assert "author" not in inspect.signature(mirror).parameters
    assert "author" in inspect.signature(set_sensitivity_state).parameters
