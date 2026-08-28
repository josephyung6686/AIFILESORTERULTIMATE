"""P8 Task 10: map P8 results onto live P2 llm_interpretation envelopes."""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

from eval_harness.assertions import assert_run, assertions
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.run import VERSION_TUPLE_FIELDS, get_version_tuple, start_run
from eval_harness.stage_output import (
    dimension_values, record_stage_output, stage_outputs, stage_payload,
)
from eval_harness.store import create_eval_schema
from llm_harness.records import CallFailed, CheckedCitation, Refusal
from llm_harness.stage_output import (
    DIMENSION, emit_stage_output, record_p8_version_tuple,
)
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    BUDGET_EXHAUSTED,
    CITATION_NOT_IN_DOSSIER,
    NOT_ELIGIBLE_FOR_MODEL,
    REJECT,
    REJECTED,
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
        validator_version="P8/0.1.0",
        policy_version="policy-1",
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


def test_version_tuple_must_match_the_run_manifest(stage_conn):
    run_id, manifest_ref, _ = _open_run(stage_conn)
    other_ref = record_p8_version_tuple(
        stage_conn, **_axes(prompt_fingerprint="fp-from-another-run"),
    )
    assert other_ref != manifest_ref

    with pytest.raises(ValueError, match="run_manifest"):
        emit_stage_output(
            stage_conn, run_id=run_id, subject_ref="file-1",
            result=make_verdict(), inputs=("obs-key-1",),
            version_tuple_ref=other_ref,
        )

    assert stage_outputs(stage_conn, run_id) == []


def test_run_manifest_version_tuple_must_still_exist(stage_conn):
    run_id, ref, _ = _open_run(stage_conn)
    stage_conn.execute("PRAGMA foreign_keys = OFF")
    stage_conn.execute(
        "DELETE FROM version_tuple WHERE version_tuple_ref = ?", (ref,),
    )

    with pytest.raises(KeyError, match="version_tuple"):
        emit_stage_output(
            stage_conn, run_id=run_id, subject_ref="file-1",
            result=make_verdict(), inputs=("obs-key-1",), version_tuple_ref=ref,
        )

    assert stage_outputs(stage_conn, run_id) == []


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


def test_every_p2_payload_carries_the_p8_versions_including_the_terminals():
    """R1: the P8 versions ride in every opaque payload, *including* refusal and
    failure measurements. `emit_stage_output` serialises the result dataclass
    verbatim, so a `Refusal` or `CallFailed` that carries neither produced an
    `abstained` or `error` P2 row with no validator version and no policy version
    -- a row nobody can later attribute to a validator build.
    """
    import dataclasses

    from llm_harness.records import CallFailed, P8Verdict, Refusal

    for record in (P8Verdict, Refusal, CallFailed):
        names = {field.name for field in dataclasses.fields(record)}
        assert "validator_version" in names, record.__name__
        assert "policy_version" in names, record.__name__


# --- §8.5's `llm_grounding` dimension, and the join P2 exists to make -------------

def _grounding_rows(conn, run_id):
    return dimension_values(conn, run_id, dimension=DIMENSION)


def test_the_dimension_p8_measures_is_llm_grounding_and_not_its_stage_id():
    """Two vocabularies that look like one: P8's STAGE is `llm_interpretation`,
    P8's DIMENSION is `llm_grounding`, and each raises under the other's checker."""
    from eval_harness.vocabulary import (
        DIMENSIONS, STAGE_IDS, UnknownDimension, UnknownStage, check_dimension,
        check_stage,
    )

    assert DIMENSION == "llm_grounding"
    assert DIMENSION in DIMENSIONS
    assert DIMENSION not in STAGE_IDS
    with pytest.raises(UnknownStage):
        check_stage(DIMENSION)
    with pytest.raises(UnknownDimension):
        check_dimension("llm_interpretation")


def test_a_produced_verdict_hands_p2_an_llm_grounding_measurement(stage_conn):
    """§8.5 decomposes evaluation by stage, and that decomposition is only real if
    the stage emits the row `assert_run` reads. Before this, `emit_stage_output`
    passed no `dimension_values`, so the stage that ran and produced a verdict left
    `stage_dimension_value` empty and scored `not_run` -- §8.5's word for the stage
    that did NOT run."""
    checked = (
        CheckedCitation("c-1", resolved=True, span_matched=True),
        CheckedCitation("c-2", resolved=True, span_matched=False),
        CheckedCitation("c-3", resolved=False, span_matched=False),
    )
    *_, run_id, _ = _emit(stage_conn, make_verdict(citations_checked=checked))

    rows = _grounding_rows(stage_conn, run_id)
    assert [row["stage_id"] for row in rows] == ["llm_interpretation"]
    assert [row["subject_ref"] for row in rows] == ["file-1"]
    assert [row["outcome"] for row in rows] == ["produced"]
    assert json.loads(rows[0]["value"]) == {
        "outcome": ACCEPT_DIRECT,
        "citations_checked": 3,
        "citations_resolved": 2,
        "citations_span_matched": 1,
    }


def test_the_measurement_is_derived_from_the_verdict_not_asserted(stage_conn):
    """§8.6: degradation must never quietly become a lower-quality classification
    reported as a good one. A dimension that always reads the same is worse than
    none, so a rejected verdict whose citations resolved to nothing must not
    produce the same measurement as an accepted one whose citations all held."""
    grounded = make_verdict(
        citations_checked=(CheckedCitation("c-1", resolved=True, span_matched=True),))
    ungrounded = make_verdict(
        outcome=REJECT, disposition=REJECTED, reasons=(CITATION_NOT_IN_DOSSIER,),
        citations_checked=(CheckedCitation("c-1", resolved=False, span_matched=False),))

    *_, grounded_run, _ = _emit(stage_conn, grounded)
    *_, ungrounded_run, _ = _emit(stage_conn, ungrounded)

    good = json.loads(_grounding_rows(stage_conn, grounded_run)[0]["value"])
    bad = json.loads(_grounding_rows(stage_conn, ungrounded_run)[0]["value"])
    assert good != bad
    assert good["citations_resolved"] == 1 and bad["citations_resolved"] == 0
    assert good["citations_span_matched"] == 1 and bad["citations_span_matched"] == 0
    assert good["outcome"] == ACCEPT_DIRECT and bad["outcome"] == REJECT


def test_the_measurement_carries_no_minted_id_that_moves_between_runs(stage_conn):
    """§8.5 diffs stored forms across two runs of one corpus, and `verdict_id` is a
    fresh uuid per call. Serialising the whole verdict into `value` -- which is what
    P9 does with its payload -- would make every replay divergent on identity alone."""
    verdict = make_verdict(
        citations_checked=(CheckedCitation("c-1", resolved=True, span_matched=True),))
    *_, run_id, _ = _emit(stage_conn, verdict)

    value = json.loads(_grounding_rows(stage_conn, run_id)[0]["value"])
    assert verdict.verdict_id not in json.dumps(value)
    assert verdict.dossier_id not in json.dumps(value)


@pytest.mark.parametrize("result_name", ["model_unknown", "refusal", "call_failed"])
def test_a_stage_that_ran_and_produced_nothing_still_says_so(stage_conn, result_name):
    """A row with a NULL value, not an absent row. `assert_run` reads absence as
    `not_run`, so an abstention with no row would report the stage never ran --
    and §8.5's llm_grounding question is exactly "did the model return unknown?"."""
    results = {
        "model_unknown": (make_verdict(outcome=ABSTAIN, disposition=ABSTAIN),
                          "abstained"),
        "refusal": (make_refusal(), "abstained"),
        "call_failed": (CallFailed(request_identity="req-1", release_id="rel-1",
                                   audit_id=None, explanation="boom",
                                   validator_version="P8/0.1.0",
                                   policy_version="policy-1"), "error"),
    }
    result, expected_outcome = results[result_name]
    *_, run_id, _ = _emit(stage_conn, result)

    rows = _grounding_rows(stage_conn, run_id)
    assert len(rows) == 1, "the stage ran; an absent row would read as not_run"
    assert rows[0]["outcome"] == expected_outcome
    assert rows[0]["value"] is None


def test_a_budget_deferral_is_measured_as_deferred_and_never_as_a_quality_verdict(
        stage_conn):
    """§8.6: a deferral is a budget event. `verdict_for` turns `deferred` into the
    `deferred` verdict, which is neither a pass nor a divergence."""
    *_, run_id, _ = _emit(stage_conn, make_verdict(
        outcome=ABSTAIN, disposition=ABSTAIN, reasons=(BUDGET_EXHAUSTED,)))

    rows = _grounding_rows(stage_conn, run_id)
    assert [row["outcome"] for row in rows] == ["deferred"]
    assert rows[0]["value"] is None


def _sealed_bundle(conn, *, expected_value, expected_outcome_kind="produced"):
    bundle_id = open_bundle(
        conn, corpus_form="snapshot", source_scan_ref="p8-seam",
        pinned_plan_id="plan-fixture", pinned_plan_version="1", policy_settings={})
    add_expectation(conn, bundle_id, dimension=DIMENSION, subject_ref="file-1",
                    expected_value=expected_value,
                    expected_outcome_kind=expected_outcome_kind,
                    source="hand-labelled")
    seal_bundle(conn, bundle_id)
    return bundle_id


def _run_against(conn, bundle_id, result):
    ref = record_p8_version_tuple(conn, **_axes())
    run_id = start_run(
        conn, bundle_id=bundle_id, run_kind="replay", version_tuple_ref=ref,
        budget_ceilings={},
        run_settings={"model_enabled": True, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1")
    emit_stage_output(conn, run_id=run_id, subject_ref="file-1", result=result,
                      inputs=("obs-key-1",), version_tuple_ref=ref)
    return run_id


def test_assert_run_scores_the_real_producers_output_rather_than_not_run(stage_conn):
    """The cross-part join P2 exists to make, exercised against a real producer for
    the first time. `assert_run` reads `stage_dimension_value` and nothing else."""
    verdict = make_verdict(
        citations_checked=(CheckedCitation("c-1", resolved=True, span_matched=True),))
    bundle_id = _sealed_bundle(stage_conn, expected_value={
        "outcome": ACCEPT_DIRECT, "citations_checked": 1,
        "citations_resolved": 1, "citations_span_matched": 1})
    run_id = _run_against(stage_conn, bundle_id, verdict)

    assert assert_run(stage_conn, run_id) == 1
    row = assertions(stage_conn, run_id, dimension=DIMENSION)[0]
    assert row["verdict"] != "not_run", (
        "the llm_interpretation stage ran and produced a verdict; `not_run` is "
        "§8.5's word for the stage that did not")
    assert row["verdict"] == "match"


def test_assert_run_reports_a_divergence_when_the_citations_did_not_hold(stage_conn):
    """The other half of the join: the measurement must be able to FAIL, or a
    passing verdict proves nothing."""
    bundle_id = _sealed_bundle(stage_conn, expected_value={
        "outcome": ACCEPT_DIRECT, "citations_checked": 1,
        "citations_resolved": 1, "citations_span_matched": 1})
    run_id = _run_against(stage_conn, bundle_id, make_verdict(
        outcome=REJECT, disposition=REJECTED, reasons=(CITATION_NOT_IN_DOSSIER,),
        citations_checked=(CheckedCitation("c-1", resolved=False,
                                           span_matched=False),)))

    assert assert_run(stage_conn, run_id) == 1
    assert assertions(stage_conn, run_id, dimension=DIMENSION)[0]["verdict"] == (
        "divergent")


def test_an_abstention_the_label_expected_is_a_pass_not_a_miss(stage_conn):
    """Done-means 5 / §6.10: `abstained_correctly` is reported as a pass. Reachable
    only because the abstaining stage writes a row at all."""
    bundle_id = _sealed_bundle(stage_conn, expected_value=None,
                               expected_outcome_kind="abstained")
    run_id = _run_against(stage_conn, bundle_id,
                          make_verdict(outcome=ABSTAIN, disposition=ABSTAIN))

    assert assert_run(stage_conn, run_id) == 1
    assert assertions(stage_conn, run_id, dimension=DIMENSION)[0]["verdict"] == (
        "abstained_correctly")


def test_validation_unavailable_is_an_error_row_not_an_absent_one(stage_conn):
    """P8 was called, reached a missing capability, and reached no judgement.

    `ValidationUnavailable` is one of `dispatch`'s eight returns -- missing
    `conn`, missing per-site dependencies, an unknown call site -- so a replay
    driver meets it on ordinary paths, not only in a fixture. Left unmapped it
    fell through `_envelope`'s catch-all `TypeError`, which inside
    `eval_harness.replay.replay_bundle` collapses the whole
    `llm_interpretation` stage into ONE `error` row keyed on the bundle id, and
    every other subject's row in that stage is then absent -- `verdict_for`'s
    `not_run`, which is §8.5's word for the stage that did not run at all.

    `error` and not one of the other four: `abstained` is refused by the record
    itself ("Never an abstain outcome") and would score `abstained_correctly`,
    a PASSING verdict, whenever the label expected an abstention -- §8.6's
    "false impression that an unprocessed file was understood". `deferred`
    requires `budget_state = ceiling_reached` and a missing capability is not a
    budget event. `not_implemented` is the harness's word for a stage with no
    adapter and scores `not_run`, which is the absent row this fix exists to
    stop writing. `produced` asserts a measurement that does not exist.
    """
    from llm_harness.records import ValidationUnavailable

    unavailable = ValidationUnavailable(missing=("fact_dependencies",))
    _, row, _, run_id, _ = _emit(stage_conn, unavailable)
    assert row["outcome"] == "error"
    assert row["budget_state"] == "within_ceiling"
    assert json.loads(row["payload"])["missing"] == ["fact_dependencies"]

    values = dimension_values(stage_conn, run_id, dimension=DIMENSION)
    assert len(values) == 1, "the stage ran; an absent row would read as not_run"
    assert values[0]["outcome"] == "error"
    assert values[0]["value"] is None, (
        "§8.6 forbids reporting a degraded or absent measurement as a good one")


def test_a_run_without_the_unavailable_row_scores_differently(stage_conn):
    """The negative twin. Writing the row only means something if its absence
    scores differently -- otherwise the row is decoration."""
    from llm_harness.records import ValidationUnavailable

    bundle_id = _sealed_bundle(stage_conn, expected_value={
        "outcome": ACCEPT_DIRECT, "citations_checked": 1,
        "citations_resolved": 1, "citations_span_matched": 1})

    with_row = _run_against(stage_conn, bundle_id,
                            ValidationUnavailable(missing=("site_validator",)))
    assert assert_run(stage_conn, with_row) == 1
    scored = assertions(stage_conn, with_row, dimension=DIMENSION)[0]

    # The same bundle, the same expectation, and no row from the stage at all.
    ref = record_p8_version_tuple(stage_conn, **_axes())
    without_row = start_run(
        stage_conn, bundle_id=bundle_id, run_kind="replay", version_tuple_ref=ref,
        budget_ceilings={},
        run_settings={"model_enabled": True, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1")
    assert assert_run(stage_conn, without_row) == 1
    absent = assertions(stage_conn, without_row, dimension=DIMENSION)[0]

    assert absent["verdict"] == "not_run"
    assert scored["verdict"] != absent["verdict"]
    assert scored["verdict"] is None
    assert scored["no_verdict_reason"] == "stage_error"
    assert absent["no_verdict_reason"] is None


def test_the_unavailable_row_is_not_scored_as_a_pass(stage_conn):
    """The other substitution the positive half cannot see: had the mapping been
    `abstained`, a label expecting an abstention would score
    `abstained_correctly` -- a PASS for a call that reached no judgement."""
    from eval_harness.assertions import PASSING_VERDICTS
    from llm_harness.records import ValidationUnavailable

    bundle_id = _sealed_bundle(stage_conn, expected_value=None,
                               expected_outcome_kind="abstained")
    run_id = _run_against(stage_conn, bundle_id,
                          ValidationUnavailable(missing=("conn",)))
    assert assert_run(stage_conn, run_id) == 1
    row = assertions(stage_conn, run_id, dimension=DIMENSION)[0]
    assert row["verdict"] not in PASSING_VERDICTS
    assert row["verdict"] is None
