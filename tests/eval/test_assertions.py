# tests/eval/test_assertions.py
import pytest

from eval_harness.assertions import (
    PASSING_VERDICTS, assert_run, assertions, verdict_counts, verdict_for,
)
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.replay import ReplayContext, StageResult, replay_bundle
from eval_harness.stage_output import DimensionValue
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import DIMENSIONS, VERDICTS


def _tuple():
    return dict(extractor_versions={}, graph_algorithm_version=None,
                prompt_fingerprint=None, model_identifier=None,
                template_library_version=None, placement_scorer_version=None,
                analysis_tiers_enabled=["filesystem"])


def _settings():
    return {"model_enabled": False, "embeddings_enabled": False}


def _v(expected_kind, expected, observed_outcome, observed):
    return verdict_for(expected_outcome_kind=expected_kind, expected_value=expected,
                       observed_outcome=observed_outcome, observed_value=observed)


def test_a_matching_produced_value_is_a_match():
    assert _v("produced", {"a": 1}, "produced", {"a": 1}) == ("match", None)


def test_key_order_does_not_make_a_divergence():
    assert _v("produced", {"a": 1, "b": 2}, "produced", {"b": 2, "a": 1})[0] == "match"


def test_a_different_produced_value_is_divergent():
    assert _v("produced", {"a": 1}, "produced", {"a": 2}) == ("divergent", None)


def test_correct_abstention_is_a_passing_verdict():
    # §6.10: "correct abstention is a successful outcome."
    assert _v("abstained", None, "abstained", None) == ("abstained_correctly", None)
    assert "abstained_correctly" in PASSING_VERDICTS
    assert PASSING_VERDICTS == frozenset({"match", "abstained_correctly"})


def test_the_two_wrong_abstention_directions_are_distinct():
    assert _v("produced", {"a": 1}, "abstained", None)[0] == "abstained_incorrectly"
    assert _v("abstained", None, "produced", {"a": 1})[0] == "asserted_incorrectly"


def test_a_deferral_is_deferred_for_every_expectation_kind():
    # §8.6: cost exhaustion must never turn into a quality judgement.
    for kind in ("produced", "abstained"):
        assert _v(kind, {"a": 1}, "deferred", None) == ("deferred", None)


def test_not_implemented_is_not_run():
    assert _v("produced", {"a": 1}, "not_implemented", None) == ("not_run", None)


def test_a_stage_error_gets_no_verdict_and_p2_mints_no_eighth_name():
    verdict, reason = _v("produced", {"a": 1}, "error", None)
    assert verdict is None
    assert reason == "stage_error"
    assert len(VERDICTS) == 7


def test_a_not_applicable_expectation_gets_no_verdict():
    verdict, reason = _v("not-applicable", None, "produced", {"a": 1})
    assert verdict is None
    assert reason == "expectation_not_applicable"


def test_verdict_for_takes_no_tolerance_argument():
    # SPEC Open question 2 is OPEN: §8.5 states no threshold and §6.10's
    # two-condition rule is a placement rule, not an eval threshold.
    import inspect
    params = set(inspect.signature(verdict_for).parameters)
    assert params == {"expected_outcome_kind", "expected_value",
                      "observed_outcome", "observed_value"}


def _run_with(eval_conn, *, expectation, adapter):
    create_eval_schema(eval_conn)
    bundle_id = open_bundle(eval_conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    add_expectation(eval_conn, bundle_id, **expectation)
    seal_bundle(eval_conn, bundle_id)
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters=adapter)
    return bundle_id, run_id


def test_assert_run_writes_one_assertion_per_expectation(eval_conn):
    def adapter(ctx: ReplayContext):
        return [StageResult(subject_ref="20047214e6930e1557c8bbd7f229baaf1e671e86f2640ac0520e4e7dfbe7d00a", outcome="produced",
                            payload=None, inputs=[], budget_state="within_ceiling",
                            values=[DimensionValue("extraction", "20047214e6930e1557c8bbd7f229baaf1e671e86f2640ac0520e4e7dfbe7d00a",
                                                   "produced", {"text": "COMS 4995"})])]

    _, run_id = _run_with(
        eval_conn,
        expectation=dict(dimension="extraction", subject_ref="20047214e6930e1557c8bbd7f229baaf1e671e86f2640ac0520e4e7dfbe7d00a",
                         expected_value={"text": "COMS 4995"},
                         expected_outcome_kind="produced", source="hand-labelled"),
        adapter={"extraction": adapter})
    assert assert_run(eval_conn, run_id) == 1
    row = assertions(eval_conn, run_id)[0]
    assert row["dimension"] == "extraction"
    assert row["verdict"] == "match"
    assert row["expected"] == '{"text":"COMS 4995"}'
    assert row["observed"] == '{"text":"COMS 4995"}'


def test_an_expectation_no_stage_answered_is_not_run(eval_conn):
    # Done-means 7: nine absent stages yield not_run verdicts, not failures.
    _, run_id = _run_with(
        eval_conn,
        expectation=dict(dimension="placement", subject_ref="file-1",
                         expected_value={"node_id": "n1"},
                         expected_outcome_kind="produced", source="hand-labelled"),
        adapter={})
    assert_run(eval_conn, run_id)
    assert assertions(eval_conn, run_id)[0]["verdict"] == "not_run"


def test_the_columbia_screenshot_in_a_residual_folder_is_divergent(eval_conn):
    # Done-means 12's second half (§7.8, §7.9): landing in a generic residual
    # folder instead of returning to placement is divergent, not a match.
    def adapter(ctx: ReplayContext):
        return [StageResult(
            subject_ref="file-screenshot", outcome="produced", payload=None,
            inputs=[], budget_state="within_ceiling",
            values=[DimensionValue("residual", "file-screenshot", "produced",
                                   {"outcome": "place",
                                    "destination": {"node_role": "residual"}})])]

    _, run_id = _run_with(
        eval_conn,
        expectation=dict(dimension="residual", subject_ref="file-screenshot",
                         expected_value={"outcome": "return_to_placement",
                                         "return_target": {"kind": "confirmed_domain_group",
                                                           "id": "g-columbia"}},
                         expected_outcome_kind="produced", source="hand-labelled"),
        adapter={"placement_scoring": adapter})
    assert_run(eval_conn, run_id)
    assert assertions(eval_conn, run_id)[0]["verdict"] == "divergent"


def test_verdict_counts_separates_passes_deferrals_and_unverdicted(eval_conn):
    def adapter(ctx: ReplayContext):
        return [StageResult(subject_ref="s", outcome="deferred", payload=None,
                            inputs=[], budget_state="ceiling_reached",
                            values=[DimensionValue("extraction", "20047214e6930e1557c8bbd7f229baaf1e671e86f2640ac0520e4e7dfbe7d00a",
                                                   "deferred", None)])]

    _, run_id = _run_with(
        eval_conn,
        expectation=dict(dimension="extraction", subject_ref="20047214e6930e1557c8bbd7f229baaf1e671e86f2640ac0520e4e7dfbe7d00a",
                         expected_value={"text": "x"},
                         expected_outcome_kind="produced", source="hand-labelled"),
        adapter={"extraction": adapter})
    assert_run(eval_conn, run_id)
    counts = verdict_counts(eval_conn, run_id)
    assert counts["deferred"] == 1
    assert counts.get("divergent", 0) == 0
    assert set(counts) <= set(VERDICTS) | {"unverdicted"}


def test_every_dimension_has_its_own_assertion_record(eval_conn):
    # Done-means 2: none is collapsed into another.
    create_eval_schema(eval_conn)
    bundle_id = open_bundle(eval_conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    for dimension in DIMENSIONS:
        add_expectation(eval_conn, bundle_id, dimension=dimension,
                        subject_ref=f"s-{dimension}", expected_value={"d": dimension},
                        expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(eval_conn, bundle_id)
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={})
    assert assert_run(eval_conn, run_id) == 10
    assert {r["dimension"] for r in assertions(eval_conn, run_id)} == set(DIMENSIONS)


def test_an_evidence_ref_that_looks_like_an_observation_id_is_refused(eval_conn):
    # §8.7 / SPEC Cross-cutting answers: a bundle expectation cited by
    # observation_id would decay silently across exactly the version change §8.5
    # exists to measure.
    from eval_harness.assertions import ObservationIdRefused, write_assertion
    create_eval_schema(eval_conn)
    with pytest.raises(ObservationIdRefused):
        write_assertion(eval_conn, run_id="r1", dimension="extraction",
                        subject_ref="s", expected=None, observed=None,
                        verdict="not_run", no_verdict_reason=None,
                        evidence_ref="observation_id:12345")
