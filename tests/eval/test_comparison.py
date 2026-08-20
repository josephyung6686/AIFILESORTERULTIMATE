# tests/eval/test_comparison.py
import pytest

from eval_harness.assertions import assert_run
from eval_harness.attribution import attribute_run
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.comparison import DifferentBundles, compare_runs, get_comparison
from eval_harness.replay import ReplayContext, StageResult, replay_bundle
from eval_harness.stage_output import DimensionValue
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import DIMENSIONS


def _tuple(**overrides):
    fields = dict(extractor_versions={"pdf.native": "1.0.0"},
                  graph_algorithm_version=None, prompt_fingerprint=None,
                  model_identifier=None, template_library_version=None,
                  placement_scorer_version=None,
                  analysis_tiers_enabled=["filesystem", "native"])
    fields.update(overrides)
    return fields


def _settings():
    return {"model_enabled": False, "embeddings_enabled": False}


def _bundle(conn):
    bundle_id = open_bundle(conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    add_expectation(conn, bundle_id, dimension="extraction", subject_ref="file-1",
                    expected_value={"text": "COMS 4995"},
                    expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(conn, bundle_id)
    return bundle_id


def _producing(value):
    def adapter(ctx: ReplayContext):
        return [StageResult(subject_ref="file-1", outcome="produced", payload=None,
                            inputs=[], budget_state="within_ceiling",
                            values=[DimensionValue("extraction", "file-1",
                                                   "produced", value)])]
    return adapter


def _deferring(ctx: ReplayContext):
    return [StageResult(subject_ref="file-1", outcome="deferred", payload=None,
                        inputs=[], budget_state="ceiling_reached",
                        values=[DimensionValue("extraction", "file-1", "deferred",
                                               None)])]


def _run(conn, bundle_id, *, adapters, version_tuple=None, ceilings=None):
    run_id = replay_bundle(conn, bundle_id,
                           version_tuple=version_tuple or _tuple(),
                           budget_ceilings=ceilings or {},
                           run_settings=_settings(), adapters=adapters)
    assert_run(conn, run_id)
    attribute_run(conn, run_id)
    return run_id


def test_two_runs_over_different_bundles_are_refused(eval_conn):
    create_eval_schema(eval_conn)
    first, second = _bundle(eval_conn), _bundle(eval_conn)
    a = _run(eval_conn, first, adapters={})
    b = _run(eval_conn, second, adapters={})
    with pytest.raises(DifferentBundles):
        compare_runs(eval_conn, a, b)


def test_a_changed_axis_is_named_and_labelled_as_one_of_the_six(eval_conn):
    # Done-means 8.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    baseline = _run(eval_conn, bundle_id,
                    adapters={"extraction": _producing({"text": "COMS 4996"})})
    candidate = _run(eval_conn, bundle_id,
                     adapters={"extraction": _producing({"text": "COMS 4995"})},
                     version_tuple=_tuple(extractor_versions={"pdf.native": "2.0.0"}))
    comparison = get_comparison(eval_conn, compare_runs(eval_conn, baseline, candidate))
    delta = comparison["version_tuple_delta"]
    assert set(delta) == {"extractor_versions"}
    assert delta["extractor_versions"]["baseline"] == {"pdf.native": "1.0.0"}
    assert delta["extractor_versions"]["candidate"] == {"pdf.native": "2.0.0"}
    assert delta["extractor_versions"]["is_8_5_axis"] is True


def test_a_changed_tier_set_is_reported_and_not_claimed_as_an_8_5_axis(eval_conn):
    # analysis_tiers_enabled comes from 10-i4-learning-ops.md, not from §8.5's six.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    baseline = _run(eval_conn, bundle_id, adapters={})
    candidate = _run(eval_conn, bundle_id, adapters={},
                     version_tuple=_tuple(
                         analysis_tiers_enabled=["filesystem", "native", "ocr"]))
    delta = get_comparison(
        eval_conn, compare_runs(eval_conn, baseline, candidate))["version_tuple_delta"]
    assert set(delta) == {"analysis_tiers_enabled"}
    assert delta["analysis_tiers_enabled"]["is_8_5_axis"] is False


def test_newly_matching_and_newly_divergent_are_per_dimension(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    baseline = _run(eval_conn, bundle_id,
                    adapters={"extraction": _producing({"text": "COMS 4996"})})
    candidate = _run(eval_conn, bundle_id,
                     adapters={"extraction": _producing({"text": "COMS 4995"})})
    comparison = get_comparison(eval_conn, compare_runs(eval_conn, baseline, candidate))
    block = comparison["per_dimension"]["extraction"]
    assert block["newly_matching"] == ["file-1"]
    assert block["newly_divergent"] == []
    assert comparison["disagreements"][0]["baseline_verdict"] == "divergent"
    assert comparison["disagreements"][0]["candidate_verdict"] == "match"


def test_every_dimension_gets_a_block_even_an_empty_one(eval_conn):
    # Done-means 2: "None is collapsed into another." A ten-row table with three
    # rows present reads as three dimensions mattering.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    a = _run(eval_conn, bundle_id, adapters={})
    b = _run(eval_conn, bundle_id, adapters={})
    comparison = get_comparison(eval_conn, compare_runs(eval_conn, a, b))
    assert set(comparison["per_dimension"]) == set(DIMENSIONS)
    for block in comparison["per_dimension"].values():
        assert set(block) == {"newly_matching", "newly_divergent", "unchanged_count",
                              "deferral_changed", "attribution_histogram"}


def test_a_ceiling_only_change_produces_zero_new_divergences(eval_conn):
    # Done-means 6, and §8.6: "cost exhaustion must never turn into lower-quality
    # automatic classification." The numbers are fixture values.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    baseline = _run(eval_conn, bundle_id,
                    adapters={"extraction": _producing({"text": "COMS 4995"})},
                    ceilings={"ocr.max_pages_per_file": 100})
    candidate = _run(eval_conn, bundle_id, adapters={"extraction": _deferring},
                     ceilings={"ocr.max_pages_per_file": 1})
    comparison = get_comparison(eval_conn, compare_runs(eval_conn, baseline, candidate))
    assert comparison["ceilings_differ"] is True
    assert comparison["ceilings_differing_keys"] == ["ocr.max_pages_per_file"]
    for dimension, block in comparison["per_dimension"].items():
        assert block["newly_divergent"] == [], dimension
    assert comparison["per_dimension"]["extraction"]["deferral_changed"] == ["file-1"]


def test_the_attribution_histogram_is_carried_per_dimension(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    baseline = _run(eval_conn, bundle_id,
                    adapters={"extraction": _producing({"text": "COMS 4995"})})
    candidate = _run(eval_conn, bundle_id,
                     adapters={"extraction": _producing({"text": "wrong"})})
    comparison = get_comparison(eval_conn, compare_runs(eval_conn, baseline, candidate))
    assert comparison["per_dimension"]["extraction"]["attribution_histogram"] == \
        {"extraction": 1}


def test_the_comparison_has_no_aggregate_field(eval_conn):
    # §8.5: "A single overall 'accuracy' number hides the mechanism that needs
    # repair." Done-means 3, asserted again over the whole record in Task 16.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    a = _run(eval_conn, bundle_id, adapters={})
    b = _run(eval_conn, bundle_id, adapters={})
    comparison = get_comparison(eval_conn, compare_runs(eval_conn, a, b))

    def walk(node, path=""):
        if isinstance(node, dict):
            for key, value in node.items():
                for part in str(key).split("_"):
                    assert part not in {"accuracy", "score", "aggregate", "overall",
                                        "rate", "percent", "grade", "f1", "precision",
                                        "recall"}, f"{path}.{key}"
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for item in node:
                walk(item, path)

    walk(comparison)
