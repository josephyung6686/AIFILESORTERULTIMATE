# tests/eval/test_driver.py
"""The replay driver — one bundle in, one evaluated run out.

Before this module existed, `replay_bundle`, `assert_run` and `attribute_run`
were three separate entry points with no caller in `src/` that joined them, so
every scored run in this repository was assembled inside a test. These tests
pin the join, and each guard has the negative half that shows it measures
something.
"""
from __future__ import annotations

import inspect

import pytest

from eval_harness.assertions import assertions
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.driver import EvaluationRun, evaluate_bundle
from eval_harness.replay import StageResult
from eval_harness.stage_output import DimensionValue, stage_outputs
from eval_harness.store import create_eval_schema

#: Same list as tests/eval/test_no_aggregate.py's, applied to what the driver
#: RETURNS rather than to what it is named. §8.5 forbids the single number.
FORBIDDEN_PARTS = {
    "accuracy", "score", "aggregate", "overall", "rate", "percent", "grade",
    "f1", "precision", "recall", "total",
}


def _tuple(**overrides):
    fields = dict(
        extractor_versions={}, graph_algorithm_version=None,
        prompt_fingerprint=None, model_identifier=None,
        template_library_version=None, placement_scorer_version=None,
        analysis_tiers_enabled=[],
    )
    fields.update(overrides)
    return fields


SETTINGS = {"model_enabled": False, "embeddings_enabled": False}


@pytest.fixture()
def bundle(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = open_bundle(
        eval_conn, corpus_form="snapshot", source_scan_ref="scan-1",
        pinned_plan_id="plan-1", pinned_plan_version="1", policy_settings={})
    add_expectation(
        eval_conn, bundle_id, dimension="fact", subject_ref="file-1",
        expected_value={"field": "school", "value": "Columbia"},
        expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(eval_conn, bundle_id)
    return bundle_id


def _stage(dimension, value, *, stage_inputs=()):
    def adapter(ctx):
        return [StageResult(
            subject_ref="file-1", outcome="produced", payload=None,
            inputs=list(stage_inputs), budget_state="within_ceiling",
            values=(DimensionValue(dimension=dimension, subject_ref="file-1",
                                   outcome="produced", value=value),))]
    return adapter


def _drive(conn, bundle_id, adapters):
    return evaluate_bundle(
        conn, bundle_id, version_tuple=_tuple(), budget_ceilings={},
        run_settings=SETTINGS, adapters=adapters)


def test_the_driver_asserts_the_run_it_replayed(eval_conn, bundle):
    """The join P2 exists to make, reachable from `src/` for the first time."""
    driven = _drive(eval_conn, bundle, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Columbia"})})

    assert isinstance(driven, EvaluationRun)
    assert driven.bundle_id == bundle
    assert driven.assertions_written == 1
    rows = assertions(eval_conn, driven.run_id, dimension="fact")
    assert [row["verdict"] for row in rows] == ["match"]
    assert driven.verdicts == {"match": 1}


def test_replaying_without_the_driver_leaves_the_run_unasserted(eval_conn, bundle):
    """The negative twin. `replay_bundle` alone writes stage outputs and NO
    assertion, which is exactly the state every P2 run in `src/` was in."""
    from eval_harness.replay import replay_bundle

    run_id = replay_bundle(
        eval_conn, bundle, version_tuple=_tuple(), budget_ceilings={},
        run_settings=SETTINGS, adapters={"factual_validation": _stage(
            "fact", {"field": "school", "value": "Columbia"})})

    assert stage_outputs(eval_conn, run_id, stage_id="factual_validation")
    assert assertions(eval_conn, run_id) == []


def test_a_divergence_is_attributed_to_exactly_one_stage(eval_conn, bundle):
    """Done-means 4, driven rather than hand-assembled. `attribute_run` had no
    caller in `src/` either, so `attributed_stage` was never filled in
    production."""
    driven = _drive(eval_conn, bundle, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Cornell"})})

    assert driven.verdicts == {"divergent": 1}
    assert driven.attributed == 1
    assert driven.attribution == {"factual_validation": 1}
    assert [row["attributed_stage"] for row in assertions(
        eval_conn, driven.run_id)] == ["factual_validation"]


def test_attribution_names_the_earliest_divergent_stage_not_the_last(eval_conn):
    """The other half: with one divergence the histogram cannot tell whether the
    driver attributes or merely echoes the emitting stage."""
    create_eval_schema(eval_conn)
    bundle_id = open_bundle(
        eval_conn, corpus_form="snapshot", source_scan_ref="scan-1",
        pinned_plan_id="plan-1", pinned_plan_version="1", policy_settings={})
    for dimension in ("extraction", "fact"):
        add_expectation(
            eval_conn, bundle_id, dimension=dimension, subject_ref="file-1",
            expected_value={"expected": dimension},
            expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(eval_conn, bundle_id)

    driven = _drive(eval_conn, bundle_id, {
        "extraction": _stage("extraction", {"expected": "wrong"}),
        # The fact stage consumed the extraction stage's subject, so §8.5's
        # "where the error BEGAN" is extraction for both rows.
        "factual_validation": _stage("fact", {"expected": "wrong"},
                                     stage_inputs=("file-1",)),
    })

    assert driven.attribution == {"extraction": 2}
    assert "factual_validation" not in driven.attribution


def test_a_stage_with_no_adapter_completes_the_run_as_not_run(eval_conn, bundle):
    """Done-means 7: a run in which a stage reports `not_implemented` completes
    and yields `not_run`, rather than failing the run."""
    driven = _drive(eval_conn, bundle, {})

    assert driven.verdicts == {"not_run": 1}
    assert driven.attributed == 0, "a not_run is not a wrong terminal outcome"
    assert driven.attribution == {}
    outcomes = {row["stage_id"]: row["outcome"]
                for row in stage_outputs(eval_conn, driven.run_id)}
    assert len(outcomes) == 10
    assert set(outcomes.values()) == {"not_implemented"}


def test_the_driver_returns_the_bundle_counts_it_did_not_recompute(eval_conn, bundle):
    """§8.6's legibility line travels with the run that was evaluated, so a
    partial evaluation is reported as partial."""
    driven = _drive(eval_conn, bundle, {})
    assert driven.counts["files_indexed"] == 0
    assert driven.counts["files_requiring_model_review"] is None


def test_the_driver_reports_no_single_number(eval_conn, bundle):
    """Done-means 3, applied to the driver's own return value. Per-verdict and
    per-stage counts, never one number over them."""
    driven = _drive(eval_conn, bundle, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Cornell"})})

    names = set(vars(driven)) | set(driven.verdicts) | set(driven.attribution)
    names |= set(driven.counts)
    for name in names:
        parts = {part.lower() for part in str(name).split("_") if part}
        assert not parts & FORBIDDEN_PARTS, name
    for value in vars(driven).values():
        assert not isinstance(value, float), driven


def test_every_policy_bearing_dependency_is_injected(eval_conn):
    """`run_p1_p7`'s discipline, which this driver mirrors: the version tuple,
    the ceilings, the stage disables and the stage set are the caller's. A
    default here would make the driver an authority on one of them."""
    parameters = inspect.signature(evaluate_bundle).parameters
    for name in ("version_tuple", "budget_ceilings", "run_settings", "adapters"):
        assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY
        assert parameters[name].default is inspect.Parameter.empty, name
    assert "threshold" not in parameters
    assert "tolerance" not in parameters
    assert "now" not in parameters


def test_the_driver_refuses_a_bundle_that_does_not_exist(eval_conn):
    create_eval_schema(eval_conn)
    with pytest.raises(KeyError):
        _drive(eval_conn, "no-such-bundle", {})


def test_the_driver_is_the_only_place_the_three_steps_are_ordered():
    """A boundary guard, not a regression test: it passed the moment it was
    written. `run_shadow` spelled out replay -> assert -> attribute a second
    time, which is how a shadow run and the live run it is compared against
    could come to be scored by two pieces of code. One ordering, one module.
    """
    import ast
    from pathlib import Path

    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness"
    driver = src / "driver.py"
    for path in src.rglob("*.py"):
        if path == driver:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        called = {node.func.id for node in ast.walk(tree)
                  if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        assert "assert_run" not in called, path.name
        assert "attribute_run" not in called, path.name
