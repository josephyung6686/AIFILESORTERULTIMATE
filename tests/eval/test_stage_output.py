# tests/eval/test_stage_output.py
import pytest

from eval_harness.run import record_version_tuple, start_run
from eval_harness.stage_output import (
    ENVELOPE_FIELDS, DimensionValue, ForeignVocabulary, dimension_values,
    record_stage_output, stage_outputs, stage_payload,
)
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import UnknownStage


@pytest.fixture()
def run(eval_conn):
    create_eval_schema(eval_conn)
    ref = record_version_tuple(
        eval_conn, extractor_versions={}, graph_algorithm_version=None,
        prompt_fingerprint=None, model_identifier=None,
        template_library_version=None, placement_scorer_version=None,
        analysis_tiers_enabled=["filesystem"],
    )
    return start_run(eval_conn, bundle_id="b1", run_kind="replay",
                     version_tuple_ref=ref, budget_ceilings={},
                     run_settings={"model_enabled": False, "embeddings_enabled": False},
                     pinned_plan_id="plan-fixture", pinned_plan_version="1"), ref


def _emit(conn, run_id, ref, **overrides):
    fields = dict(run_id=run_id, stage_id="extraction", subject_ref="sha256:aa",
                  outcome="produced", payload='{"opaque": true}',
                  version_tuple_ref=ref, inputs=[], budget_state="within_ceiling")
    fields.update(overrides)
    return record_stage_output(conn, **fields)


def test_the_envelope_has_exactly_the_nine_contract_fields():
    assert ENVELOPE_FIELDS == (
        "run_id", "stage_id", "subject_ref", "outcome", "payload",
        "version_tuple_ref", "inputs", "budget_state", "produced_at",
    )


def test_every_envelope_field_is_stored(eval_conn, run):
    run_id, ref = run
    _emit(eval_conn, run_id, ref, inputs=["sha256:bb"])
    row = stage_outputs(eval_conn, run_id)[0]
    assert row["stage_id"] == "extraction"
    assert row["subject_ref"] == "sha256:aa"
    assert row["outcome"] == "produced"
    assert row["version_tuple_ref"] == ref
    assert row["inputs"] == '["sha256:bb"]'
    assert row["budget_state"] == "within_ceiling"
    assert row["produced_at"]


def test_payload_is_opaque_and_is_never_parsed(eval_conn, run):
    # Contract out §4: "payload  opaque to P2; shape owned by the producing part."
    # Not valid JSON on purpose: a store that round-trips only well-formed JSON
    # has acquired an opinion about another part's shape.
    run_id, ref = run
    blob = "this is not JSON \x00 and it has a NUL and a }brace"
    output_id = _emit(eval_conn, run_id, ref, payload=blob)
    assert stage_payload(eval_conn, output_id) == blob


def test_a_stage_id_outside_the_ten_is_rejected(eval_conn, run):
    run_id, ref = run
    with pytest.raises(UnknownStage):
        _emit(eval_conn, run_id, ref, stage_id="residual")


def test_a_producing_parts_own_vocabulary_is_refused_in_the_envelope(eval_conn, run):
    # P11 SPEC: "none of them is an envelope value, and none may be written into
    # stage_output." Refused at the writer, not discovered during comparison.
    run_id, ref = run
    for foreign in ("place", "abstain", "return_to_placement", "mark_review_later",
                    "leave_in_place", "mark_state", "ask_user"):
        with pytest.raises(ForeignVocabulary):
            _emit(eval_conn, run_id, ref, outcome=foreign)


def test_an_outcome_outside_the_five_is_rejected(eval_conn, run):
    run_id, ref = run
    with pytest.raises(ValueError):
        _emit(eval_conn, run_id, ref, outcome="succeeded")


def test_deferred_and_ceiling_reached_are_bound_together(eval_conn, run):
    # §8.6: a budget deferral must not be scorable as an evidence judgement.
    run_id, ref = run
    _emit(eval_conn, run_id, ref, outcome="deferred", budget_state="ceiling_reached")
    with pytest.raises(ValueError):
        _emit(eval_conn, run_id, ref, outcome="deferred", budget_state="within_ceiling")
    with pytest.raises(ValueError):
        _emit(eval_conn, run_id, ref, outcome="abstained", budget_state="ceiling_reached")


def test_not_implemented_is_a_legal_output(eval_conn, run):
    # 02-segmentation-map.md, Order: the harness runs before the stages exist.
    run_id, ref = run
    _emit(eval_conn, run_id, ref, stage_id="placement_scoring",
          outcome="not_implemented", payload="")
    row = stage_outputs(eval_conn, run_id, stage_id="placement_scoring")[0]
    assert row["outcome"] == "not_implemented"


def test_a_stage_output_may_carry_several_dimension_values(eval_conn, run):
    # One `fact` stage output about one file, three fields, one abstention.
    run_id, ref = run
    _emit(eval_conn, run_id, ref, stage_id="factual_validation",
          subject_ref="file-1",
          dimension_values=[
              DimensionValue("fact", "file-1::field-a", "produced", {"value": "A"}),
              DimensionValue("fact", "file-1::field-b", "produced", {"value": "B"}),
              DimensionValue("fact", "file-1::field-c", "abstained", None),
          ])
    rows = dimension_values(eval_conn, run_id, dimension="fact")
    assert len(rows) == 3
    assert {r["outcome"] for r in rows} == {"produced", "abstained"}
    assert [r["stage_id"] for r in rows] == ["factual_validation"] * 3


def test_the_emitting_stage_names_itself_for_any_dimension(eval_conn, run):
    # SPEC Open question 1 is open: `residual` has no same-named attribution stage,
    # so whichever stage emits it says so. P2 holds no dimension->stage table.
    run_id, ref = run
    _emit(eval_conn, run_id, ref, stage_id="placement_scoring", subject_ref="file-9",
          dimension_values=[DimensionValue("residual", "file-9", "produced",
                                           {"outcome": "leave_in_place"})])
    row = dimension_values(eval_conn, run_id, dimension="residual")[0]
    assert row["stage_id"] == "placement_scoring"


def test_a_dimension_outside_the_ten_is_rejected(eval_conn, run):
    from eval_harness.vocabulary import UnknownDimension
    run_id, ref = run
    with pytest.raises(UnknownDimension):
        _emit(eval_conn, run_id, ref,
              dimension_values=[DimensionValue("factual_validation", "x",
                                               "produced", None)])
