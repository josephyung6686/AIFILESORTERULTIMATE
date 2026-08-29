# tests/eval/test_attribution.py
from eval_harness.assertions import assert_run, assertions
from eval_harness.attribution import (
    ANCESTOR_VERDICTS, FAILING_VERDICTS, attribute_run, attribution_histogram,
)
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.replay import ReplayContext, StageResult, replay_bundle
from eval_harness.stage_output import DimensionValue
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import STAGE_IDS


def _tuple():
    return dict(extractor_versions={}, graph_algorithm_version=None,
                prompt_fingerprint=None, model_identifier=None,
                template_library_version=None, placement_scorer_version=None,
                analysis_tiers_enabled=["filesystem"])


def _settings():
    return {"model_enabled": False, "embeddings_enabled": False}


def _emit(subject_ref, dimension, value, inputs=(), outcome="produced"):
    def adapter(ctx: ReplayContext):
        return [StageResult(subject_ref=subject_ref, outcome=outcome, payload=None,
                            inputs=list(inputs), budget_state="within_ceiling",
                            values=[DimensionValue(dimension, subject_ref, outcome,
                                                   value)])]
    return adapter


def _bundle(conn, expectations):
    bundle_id = open_bundle(conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    for e in expectations:
        add_expectation(conn, bundle_id, **e)
    seal_bundle(conn, bundle_id)
    return bundle_id


def test_the_two_verdict_sets():
    # SPEC Contract out §6, verbatim: the ancestor criterion is divergent /
    # asserted_incorrectly. Done-means 4 attributes every wrong terminal outcome.
    assert ANCESTOR_VERDICTS == frozenset({"divergent", "asserted_incorrectly"})
    assert FAILING_VERDICTS == frozenset({"divergent", "asserted_incorrectly",
                                          "abstained_incorrectly"})


def test_a_wrong_placement_attributes_to_the_earliest_divergent_stage(eval_conn):
    # extraction produced the wrong text; the fact and the placement are wrong in
    # consequence. §8.5: name where the error BEGAN.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="extraction", subject_ref="file-1",
             expected_value={"text": "COMS 4995"}, expected_outcome_kind="produced",
             source="hand-labelled"),
        dict(dimension="fact", subject_ref="file-1",
             expected_value={"course": "COMS 4995"},
             expected_outcome_kind="produced", source="hand-labelled"),
        dict(dimension="placement", subject_ref="file-1",
             expected_value={"node_id": "n-coms"}, expected_outcome_kind="produced",
             source="hand-labelled"),
    ])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "extraction": _emit("file-1", "extraction", {"text": "COMS 4996"}),
        "factual_validation": _emit("file-1", "fact", {"course": "COMS 4996"},
                                    inputs=["file-1"]),
        "placement_scoring": _emit("file-1", "placement", {"node_id": "n-other"},
                                   inputs=["file-1"]),
    })
    assert_run(eval_conn, run_id)
    assert attribute_run(eval_conn, run_id) == 3
    by_dimension = {r["dimension"]: r for r in assertions(eval_conn, run_id)}
    assert by_dimension["placement"]["verdict"] == "divergent"
    assert by_dimension["placement"]["attributed_stage"] == "extraction"
    assert by_dimension["fact"]["attributed_stage"] == "extraction"
    assert by_dimension["extraction"]["attributed_stage"] == "extraction"


def test_exactly_one_stage_is_named_and_it_is_one_of_the_ten(eval_conn):
    # Done-means 4.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="placement", subject_ref="file-1",
             expected_value={"node_id": "n1"}, expected_outcome_kind="produced",
             source="hand-labelled")])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "placement_scoring": _emit("file-1", "placement", {"node_id": "n2"})})
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)
    row = assertions(eval_conn, run_id)[0]
    assert row["attributed_stage"] in STAGE_IDS
    assert isinstance(row["attributed_stage"], str)


def test_a_matching_verdict_is_attributed_to_nothing(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="placement", subject_ref="file-1",
             expected_value={"node_id": "n1"}, expected_outcome_kind="produced",
             source="hand-labelled")])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "placement_scoring": _emit("file-1", "placement", {"node_id": "n1"})})
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)
    row = assertions(eval_conn, run_id)[0]
    assert row["verdict"] == "match"
    assert row["attributed_stage"] is None


def test_a_deferral_is_attributed_to_nothing(eval_conn):
    # §8.6: a deferral is not a wrong outcome, so it has no origin to name.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="placement", subject_ref="file-1",
             expected_value={"node_id": "n1"}, expected_outcome_kind="produced",
             source="hand-labelled")])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "placement_scoring": lambda ctx: [StageResult(
            subject_ref="file-1", outcome="deferred", payload=None, inputs=[],
            budget_state="ceiling_reached",
            values=[DimensionValue("placement", "file-1", "deferred", None)])]})
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)
    row = assertions(eval_conn, run_id)[0]
    assert row["verdict"] == "deferred"
    assert row["attributed_stage"] is None


def test_attribution_follows_a_cross_subject_edge_when_one_is_emitted(eval_conn):
    # SPEC Open question 3 is OPEN. P2 walks the edges it is given: a wrong
    # placement for file A originating in a wrong fact on file B is attributed
    # across subjects ONLY because the emitting part recorded that edge.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="fact", subject_ref="file-B", expected_value={"v": 1},
             expected_outcome_kind="produced", source="hand-labelled"),
        dict(dimension="placement", subject_ref="file-A", expected_value={"n": 1},
             expected_outcome_kind="produced", source="hand-labelled"),
    ])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "factual_validation": _emit("file-B", "fact", {"v": 2}),
        "placement_scoring": _emit("file-A", "placement", {"n": 2},
                                   inputs=["file-B"]),
    })
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)
    placement = [r for r in assertions(eval_conn, run_id)
                 if r["dimension"] == "placement"][0]
    assert placement["attributed_stage"] == "factual_validation"


def test_without_a_cross_subject_edge_attribution_stays_within_the_subject(eval_conn):
    # The same code, the same two wrong values, no recorded edge between them.
    # Nothing in P2 requires the edge to exist — that is what OQ3 asks.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="fact", subject_ref="file-B", expected_value={"v": 1},
             expected_outcome_kind="produced", source="hand-labelled"),
        dict(dimension="placement", subject_ref="file-A", expected_value={"n": 1},
             expected_outcome_kind="produced", source="hand-labelled"),
    ])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "factual_validation": _emit("file-B", "fact", {"v": 2}),
        "placement_scoring": _emit("file-A", "placement", {"n": 2}, inputs=[]),
    })
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)
    placement = [r for r in assertions(eval_conn, run_id)
                 if r["dimension"] == "placement"][0]
    assert placement["attributed_stage"] == "placement_scoring"


def test_a_cycle_in_inputs_terminates(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="grouping", subject_ref="g-1", expected_value={"m": 1},
             expected_outcome_kind="produced", source="hand-labelled")])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "retrieval": _emit("g-1", "retrieval", {"x": 1}, inputs=["g-1"]),
        "grouping": _emit("g-1", "grouping", {"m": 2}, inputs=["g-1"]),
    })
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)      # must return, not hang
    assert assertions(eval_conn, run_id)[0]["attributed_stage"] in STAGE_IDS


def test_the_histogram_counts_stages_and_totals_nothing(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="fact", subject_ref="file-1", expected_value={"v": 1},
             expected_outcome_kind="produced", source="hand-labelled"),
        dict(dimension="placement", subject_ref="file-1", expected_value={"n": 1},
             expected_outcome_kind="produced", source="hand-labelled"),
    ])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "factual_validation": _emit("file-1", "fact", {"v": 2}),
        "placement_scoring": _emit("file-1", "placement", {"n": 2},
                                   inputs=["file-1"]),
    })
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)
    histogram = attribution_histogram(eval_conn, run_id)
    assert histogram == {"factual_validation": 2}
    assert set(histogram) <= set(STAGE_IDS)
