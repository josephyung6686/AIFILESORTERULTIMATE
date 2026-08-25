"""P8 Task 10: map P8 results onto live P2 llm_interpretation envelopes."""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

from eval_harness.run import VERSION_TUPLE_FIELDS, get_version_tuple, start_run
from eval_harness.stage_output import record_stage_output, stage_outputs, stage_payload
from eval_harness.store import create_eval_schema
from llm_harness.records import CallFailed, Refusal
from llm_harness.stage_output import emit_stage_output, record_p8_version_tuple
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    BUDGET_EXHAUSTED,
    NOT_ELIGIBLE_FOR_MODEL,
    REJECT,
    USER_REJECTED_EQUIVALENT,
    WEAK,
)
from p8.conftest import make_refusal, make_verdict
from privacy.consent import ConsentRequirement
from privacy.release import NeedsConsent

SRC = Path(__file__).resolve().parents[2] / "src" / "llm_harness" / "stage_output.py"

STALE_FOUR = {
    "model_id": "stale-model",
    "prompt_fingerprint": "stale-fp",
    "validator_version": "P8/stale",
    "policy_version": "policy-stale",
}


def _axes(**overrides):
    fields = dict(
        extractor_versions={},
        graph_algorithm_version=None,
        prompt_fingerprint="fp-p8",
        model_identifier="model-p8",
        template_library_version=None,
        placement_scorer_version=None,
        analysis_tiers_enabled=["llm"],
    )
    fields.update(overrides)
    return fields


@pytest.fixture()
def stage_conn(p8_conn):
    create_eval_schema(p8_conn)
    return p8_conn


def _open_run(conn, **axes):
    fields = _axes(**axes)
    ref = record_p8_version_tuple(conn, **fields)
    run_id = start_run(
        conn, bundle_id="bundle-p8", run_kind="replay", version_tuple_ref=ref,
        budget_ceilings={},
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1",
    )
    return run_id, ref, fields


def _emit(conn, result, *, inputs=("obs-key-1",), **axes):
    run_id, ref, fields = _open_run(conn, **axes)
    output_id = emit_stage_output(
        conn, run_id=run_id, subject_ref="file-1", result=result,
        inputs=inputs, version_tuple_ref=ref,
    )
    row = stage_outputs(conn, run_id, stage_id="llm_interpretation")[0]
    return output_id, row, fields, run_id, ref


def test_live_version_tuple_fields_are_exactly_seven():
    assert VERSION_TUPLE_FIELDS == (
        "extractor_versions",
        "graph_algorithm_version",
        "prompt_fingerprint",
        "model_identifier",
        "template_library_version",
        "placement_scorer_version",
        "analysis_tiers_enabled",
    )


def test_emit_signature_is_keyword_only_and_omits_produced_at():
    parameters = inspect.signature(emit_stage_output).parameters
    assert tuple(parameters) == (
        "conn", "run_id", "subject_ref", "result", "inputs", "version_tuple_ref",
    )
    for name in ("run_id", "subject_ref", "result", "inputs", "version_tuple_ref"):
        assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY
        assert parameters[name].default is inspect.Parameter.empty
    assert "produced_at" not in parameters
    assert "produced_at" not in inspect.signature(record_stage_output).parameters


@pytest.mark.parametrize(
    "outcome",
    [ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED, WEAK, REJECT],
)
def test_quality_verdicts_are_produced_within_ceiling(stage_conn, outcome):
    extra = {}
    if outcome == ACCEPT_CONTEXT_SUPPORTED:
        extra["requires_review"] = True
    if outcome == WEAK:
        extra["may_propose"] = False
    _, row, *_ = _emit(stage_conn, make_verdict(outcome=outcome, **extra))
    assert row["stage_id"] == "llm_interpretation"
    assert row["outcome"] == "produced"
    assert row["budget_state"] == "within_ceiling"
    assert row["subject_ref"] == "file-1"


def test_model_unknown_is_abstained_within_ceiling(stage_conn):
    _, row, *_ = _emit(stage_conn, make_verdict(outcome=ABSTAIN, disposition=ABSTAIN))
    assert row["outcome"] == "abstained"
    assert row["budget_state"] == "within_ceiling"


def test_gate_refusal_is_abstained_within_ceiling(stage_conn):
    _, row, *_ = _emit(stage_conn, make_refusal())
    assert isinstance(make_refusal(), Refusal)
    assert row["outcome"] == "abstained"
    assert row["budget_state"] == "within_ceiling"


@pytest.mark.parametrize("reason", [NOT_ELIGIBLE_FOR_MODEL, USER_REJECTED_EQUIVALENT])
def test_ordinary_pre_call_abstention_is_abstained_within_ceiling(stage_conn, reason):
    verdict = make_verdict(outcome=ABSTAIN, disposition=ABSTAIN, reasons=(reason,))
    _, row, *_ = _emit(stage_conn, verdict)
    assert row["outcome"] == "abstained"
    assert row["budget_state"] == "within_ceiling"


def test_budget_exhausted_is_deferred_ceiling_reached(stage_conn):
    verdict = make_verdict(
        outcome=ABSTAIN, disposition=ABSTAIN, reasons=(BUDGET_EXHAUSTED,),
    )
    _, row, *_ = _emit(stage_conn, verdict)
    assert row["outcome"] == "deferred"
    assert row["budget_state"] == "ceiling_reached"


def test_call_failed_is_error(stage_conn):
    failed = CallFailed(
        request_identity="req-1", release_id="rel-1",
        audit_id=17, explanation="transport raised",
    )
    _, row, *_ = _emit(stage_conn, failed)
    assert row["outcome"] == "error"
    assert row["budget_state"] == "within_ceiling"


def test_needs_consent_writes_no_row(stage_conn):
    run_id, ref, _ = _open_run(stage_conn)
    needs = NeedsConsent(
        consent_request_id="consent-1",
        requirement=ConsentRequirement(
            file_ids=("file-1",),
            handling_class="public_low",
            items=(("obs-key-1", "0:4"),),
            why="sensitive text",
        ),
    )
    with pytest.raises(TypeError):
        emit_stage_output(
            stage_conn, run_id=run_id, subject_ref="file-1", result=needs,
            inputs=("obs-key-1",), version_tuple_ref=ref,
        )
    assert stage_outputs(stage_conn, run_id) == []


def test_payload_is_opaque_canonical_and_carries_p8_versions(stage_conn):
    verdict = make_verdict(validator_version="P8/0.1.0", policy_version="policy-1")
    output_id, row, fields, _, ref = _emit(stage_conn, verdict)
    payload = stage_payload(stage_conn, output_id)
    assert payload == row["payload"]
    parsed = json.loads(payload)
    assert parsed["validator_version"] == "P8/0.1.0"
    assert parsed["policy_version"] == "policy-1"
    assert parsed["outcome"] == ACCEPT_DIRECT
    assert payload == json.dumps(parsed, sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False)
    stored = get_version_tuple(stage_conn, ref)
    assert set(stored) == set(VERSION_TUPLE_FIELDS)
    assert "validator_version" not in stored
    assert "policy_version" not in stored
    assert stored["prompt_fingerprint"] == fields["prompt_fingerprint"]
    assert stored["model_identifier"] == fields["model_identifier"]


def test_inputs_are_stored_as_canonical_subject_refs(stage_conn):
    _, row, *_ = _emit(stage_conn, make_verdict(), inputs=("obs-a", "obs-b"))
    assert row["inputs"] == '["obs-a","obs-b"]'


def test_empty_caller_axis_is_authored_not_a_p8_default(stage_conn):
    _, _, fields, _, ref = _emit(
        stage_conn, make_verdict(),
        extractor_versions={},
        graph_algorithm_version=None,
        template_library_version=None,
        placement_scorer_version=None,
        analysis_tiers_enabled=["llm"],
    )
    stored = get_version_tuple(stage_conn, ref)
    assert stored["extractor_versions"] == {}
    assert stored["graph_algorithm_version"] is None
    assert stored["template_library_version"] is None
    assert stored["placement_scorer_version"] is None
    parameters = inspect.signature(record_p8_version_tuple).parameters
    for axis in VERSION_TUPLE_FIELDS:
        if axis in parameters:
            assert parameters[axis].default is inspect.Parameter.empty, axis


def test_extra_version_tuple_keys_are_refused(stage_conn):
    with pytest.raises(ValueError):
        record_p8_version_tuple(
            stage_conn, **_axes(), validator_version="P8/0.1.0",
        )
    with pytest.raises(ValueError):
        record_p8_version_tuple(
            stage_conn, **_axes(), policy_version="policy-1",
        )


def test_stale_four_field_tuple_is_refused(stage_conn):
    with pytest.raises(ValueError):
        record_p8_version_tuple(stage_conn, **STALE_FOUR)


def test_omitted_caller_axis_is_refused_not_defaulted(stage_conn):
    fields = _axes()
    del fields["graph_algorithm_version"]
    with pytest.raises(ValueError):
        record_p8_version_tuple(stage_conn, **fields)


def test_missing_run_manifest_is_refused(stage_conn):
    ref = record_p8_version_tuple(stage_conn, **_axes())
    with pytest.raises(Exception):
        emit_stage_output(
            stage_conn, run_id="missing-run", subject_ref="file-1",
            result=make_verdict(), inputs=("obs-key-1",), version_tuple_ref=ref,
        )
    assert stage_conn.execute("SELECT count(*) AS c FROM stage_output").fetchone()["c"] == 0


def test_emit_calls_live_record_stage_output_without_produced_at():
    tree = ast.parse(SRC.read_text(encoding="utf-8"))
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "record_stage_output"
    ]
    assert calls, "emit_stage_output must call live record_stage_output"
    for call in calls:
        keywords = {keyword.arg for keyword in call.keywords}
        assert "produced_at" not in keywords
        assert "run_id" in keywords
        assert "stage_id" in keywords
        assert "subject_ref" in keywords
        assert "outcome" in keywords
        assert "payload" in keywords
        assert "version_tuple_ref" in keywords
        assert "inputs" in keywords
        assert "budget_state" in keywords
        stage = next(keyword.value for keyword in call.keywords if keyword.arg == "stage_id")
        assert isinstance(stage, ast.Constant) and stage.value == "llm_interpretation"


def test_produced_at_is_stamped_by_p2(stage_conn):
    _, row, *_ = _emit(stage_conn, make_verdict())
    assert row["produced_at"]
