# tests/eval/test_bundle_learning.py
import pytest
from database_agent.db import create_schema
from database_agent.events import append_event
from database_agent.learning import SCOPES, reset_preferences

from eval_harness.bundle import (
    LEARNING_RECORD_FIELDS, bundle_learning_records, capture_learning_records,
    open_bundle, seal_bundle,
)
from eval_harness.store import create_eval_schema


def _reject(conn, *, subject, basis_key, proposal_class="group"):
    """A user rejection, authored by the acting part (M8: P1 only writes)."""
    return append_event(
        conn, event_type="user group decision", subsystem="P9",
        component_version="p9-fixture", observed_at="2026-08-19T00:00:00+00:00",
        explanation="fixture rejection", user_id="u1",
        correction_scope="group", correction_subject=subject,
        polarity="reject", proposal_class=proposal_class, basis_key=basis_key,
    )


def _bundle(conn):
    return open_bundle(conn, corpus_form="snapshot", source_scan_ref="scan-fixture",
                       pinned_plan_id="plan-fixture", pinned_plan_version="1",
                       policy_settings={})


def test_the_five_named_fields():
    # SPEC Contract out §3: "scope, subject_id, proposal_class, basis_key,
    # polarity, evidence refs."
    assert LEARNING_RECORD_FIELDS == (
        "scope", "subject_id", "polarity", "proposal_class", "basis_key",
    )


def test_a_rejection_is_captured_with_all_three_opaque_fields(eval_conn):
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    _reject(eval_conn, subject="group-7", basis_key="anchor-a|anchor-b")
    bundle_id = _bundle(eval_conn)
    assert capture_learning_records(eval_conn, bundle_id, scope="group",
                                    subject_id="group-7") == 1
    row = bundle_learning_records(eval_conn, bundle_id)[0]
    assert row["scope"] == "group"
    assert row["subject_id"] == "group-7"
    assert row["polarity"] == "reject"
    assert row["proposal_class"] == "group"
    assert row["basis_key"] == "anchor-a|anchor-b"
    # §8.2's "structured explanation or evidence reference" survives verbatim.
    assert row["row"]["explanation"] == "fixture rejection"


def test_p2_applies_no_suppression_rule(eval_conn):
    # Query-before-propose is the ACTING part's rule (10-i4-learning-ops.md).
    # P2 carries the rows; it never decides that a reject means "do not emit".
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness"
    for path in src.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "polarity ==" not in text, path.name
        assert 'polarity") ==' not in text, path.name


def test_a_sealed_bundle_keeps_the_records_a_later_reset_removed(eval_conn):
    # Two runs over one bundle must see the same negative examples, or the
    # comparison measures the store instead of the algorithm.
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    _reject(eval_conn, subject="group-7", basis_key="anchor-a")
    bundle_id = _bundle(eval_conn)
    capture_learning_records(eval_conn, bundle_id, scope="group", subject_id="group-7")
    seal_bundle(eval_conn, bundle_id)
    reset_preferences(eval_conn, "group", "group-7", author="P13",
                      component_version="p13-fixture", user_id="u1")
    assert len(bundle_learning_records(eval_conn, bundle_id)) == 1


def test_an_empty_capture_is_recorded_as_empty_not_as_missing(eval_conn):
    # A bundle with no negative example is a legal bundle. What must never happen
    # is a bundle that silently omits one that existed.
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    assert capture_learning_records(eval_conn, bundle_id, scope="group",
                                    subject_id="group-nothing") == 0
    assert bundle_learning_records(eval_conn, bundle_id) == []


def test_scope_is_p1s_and_is_exact(eval_conn):
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    assert set(SCOPES) == {"file", "group", "node", "template", "domain", "corpus"}
    with pytest.raises(ValueError):
        capture_learning_records(eval_conn, bundle_id, scope="destination node",
                                 subject_id="n1")


def test_a_file_scoped_record_is_not_returned_by_a_corpus_scoped_read(eval_conn):
    # §8.7 scope discipline: one transcript belonging in a Columbia packet "should
    # not teach the engine that all transcripts belong there." P2 reads scope; it
    # never assigns or widens it.
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    append_event(eval_conn, event_type="user group decision", subsystem="P9",
                 component_version="p9-fixture",
                 observed_at="2026-08-19T00:00:00+00:00",
                 explanation="file-scoped", user_id="u1",
                 correction_scope="file", correction_subject="file-1",
                 polarity="reject", proposal_class="membership",
                 basis_key="group-1|file-1")
    bundle_id = _bundle(eval_conn)
    assert capture_learning_records(eval_conn, bundle_id, scope="corpus",
                                    subject_id="file-1") == 0
