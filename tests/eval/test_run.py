# tests/eval/test_run.py
import pytest
from database_agent.budget import CEILING_KEYS, all_ceilings, set_ceiling
from database_agent.db import create_schema

from eval_harness.run import (
    ANALYSIS_TIERS, RUN_SETTING_KEYS, VERSION_AXES, VERSION_TUPLE_FIELDS,
    UnknownAnalysisTier, UnknownRunSetting, finish_run, get_run, get_version_tuple,
    record_version_tuple, run_ceilings, start_run,
)
from eval_harness.store import create_eval_schema


def _tuple_fields(**overrides):
    fields = dict(
        extractor_versions={"e1": "0.0.0-fixture"},
        graph_algorithm_version="graph-fixture",
        prompt_fingerprint=None,
        model_identifier=None,
        template_library_version="templates-fixture",
        placement_scorer_version="scorer-fixture",
        analysis_tiers_enabled=["filesystem", "native"],
    )
    fields.update(overrides)
    return fields


def test_the_six_8_5_axes_and_the_seventh_i4_field():
    # §8.5: "a new extractor version, graph algorithm, LLM prompt, model,
    # template library, or placement scorer". Six.
    assert VERSION_AXES == (
        "extractor_versions", "graph_algorithm_version", "prompt_fingerprint",
        "model_identifier", "template_library_version", "placement_scorer_version",
    )
    # 10-i4-learning-ops.md adds the tier set. Seven fields, six named axes.
    assert VERSION_TUPLE_FIELDS == VERSION_AXES + ("analysis_tiers_enabled",)


def test_analysis_tiers_enabled_is_a_subset_of_the_four(eval_conn):
    create_eval_schema(eval_conn)
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")
    ref = record_version_tuple(eval_conn, **_tuple_fields())
    assert get_version_tuple(eval_conn, ref)["analysis_tiers_enabled"] == \
        ["filesystem", "native"]


def test_a_tier_outside_the_four_is_rejected(eval_conn):
    create_eval_schema(eval_conn)
    with pytest.raises(UnknownAnalysisTier):
        record_version_tuple(eval_conn,
                             **_tuple_fields(analysis_tiers_enabled=["deep"]))


def test_the_same_tuple_yields_the_same_reference(eval_conn):
    create_eval_schema(eval_conn)
    a = record_version_tuple(eval_conn, **_tuple_fields())
    b = record_version_tuple(eval_conn, **_tuple_fields())
    c = record_version_tuple(eval_conn, **_tuple_fields(model_identifier="m2"))
    assert a == b
    assert a != c


def test_run_settings_are_exactly_two_and_are_not_version_axes(eval_conn):
    create_eval_schema(eval_conn)
    assert RUN_SETTING_KEYS == ("model_enabled", "embeddings_enabled")
    assert not set(RUN_SETTING_KEYS) & set(VERSION_TUPLE_FIELDS)
    ref = record_version_tuple(eval_conn, **_tuple_fields())
    with pytest.raises(UnknownRunSetting):
        start_run(eval_conn, bundle_id="b1", run_kind="replay", version_tuple_ref=ref,
                  budget_ceilings={}, run_settings={"ocr_enabled": True},
                  pinned_plan_id="plan-fixture", pinned_plan_version="1")


def test_a_run_snapshots_the_ceiling_set_it_was_given(eval_conn):
    # SPEC Contract out §5: "Two runs are only comparable when they were given the
    # same budget_ceilings". The numbers below are fixture values, not design values.
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    set_ceiling(eval_conn, "ocr.max_pages_per_file", 40)
    set_ceiling(eval_conn, "model.max_cost_per_scan", 7)
    ref = record_version_tuple(eval_conn, **_tuple_fields())
    run_id = start_run(
        eval_conn, bundle_id="b1", run_kind="replay", version_tuple_ref=ref,
        budget_ceilings=all_ceilings(eval_conn),
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1",
    )
    assert run_ceilings(eval_conn, run_id) == {"ocr.max_pages_per_file": 40,
                                               "model.max_cost_per_scan": 7}
    # A later change to the live config does not rewrite a completed run.
    set_ceiling(eval_conn, "ocr.max_pages_per_file", 5)
    assert run_ceilings(eval_conn, run_id)["ocr.max_pages_per_file"] == 40


def test_a_ceiling_key_outside_p1s_fifteen_is_rejected(eval_conn):
    create_eval_schema(eval_conn)
    ref = record_version_tuple(eval_conn, **_tuple_fields())
    with pytest.raises(KeyError):
        start_run(eval_conn, bundle_id="b1", run_kind="replay", version_tuple_ref=ref,
                  budget_ceilings={"made.up_ceiling": 5},
                  run_settings={"model_enabled": False, "embeddings_enabled": False},
                  pinned_plan_id="plan-fixture", pinned_plan_version="1")


def test_p2_stores_no_ceiling_value_of_its_own():
    # §8.6's ceilings are configurable and hand-authored. P2 holds keys.
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness"
    for path in src.rglob("*.py"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if "max_" in line and "=" in line and "CEILING" not in line:
                assert not any(ch.isdigit() for ch in line.split("=", 1)[1]), \
                    f"{path.name}: {line.strip()}"


def test_run_kind_is_one_of_three(eval_conn):
    create_eval_schema(eval_conn)
    ref = record_version_tuple(eval_conn, **_tuple_fields())
    with pytest.raises(ValueError):
        start_run(eval_conn, bundle_id="b1", run_kind="production",
                  version_tuple_ref=ref, budget_ceilings={},
                  run_settings={"model_enabled": False, "embeddings_enabled": False},
                  pinned_plan_id="plan-fixture", pinned_plan_version="1")


def test_a_run_records_its_pinned_plan_version_and_finishes(eval_conn):
    create_eval_schema(eval_conn)
    ref = record_version_tuple(eval_conn, **_tuple_fields())
    run_id = start_run(
        eval_conn, bundle_id="b1", run_kind="replay", version_tuple_ref=ref,
        budget_ceilings={},
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1",
    )
    row = get_run(eval_conn, run_id)
    assert row["pinned_plan_id"] == "plan-fixture"
    assert row["pinned_plan_version"] == "1"
    assert row["started_at"] and row["finished_at"] is None
    finish_run(eval_conn, run_id)
    assert get_run(eval_conn, run_id)["finished_at"]


def test_a_run_carries_no_session_id(eval_conn):
    # 11-ops-runtime.md §3: "P2 replay is not a session; it is a harness run."
    create_eval_schema(eval_conn)
    cols = {r["name"] for r in eval_conn.execute("PRAGMA table_info(run_manifest)")}
    assert "session_id" not in cols
