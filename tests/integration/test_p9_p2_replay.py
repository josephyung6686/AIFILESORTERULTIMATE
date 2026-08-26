# tests/integration/test_p9_p2_replay.py
"""P9 Task 12b — P9's three P2 stages, against the live eval harness.

P9 emits `retrieval`, `graph_construction` and `grouping`. It does not emit
`llm_interpretation`: that stage measures the model call, P8 makes the call, and a
second emitter would double-count every call in the replay.

The mapping is pinned to three exact pairs. §8.6 requires a budget deferral to be
`deferred` with `ceiling_reached` and never `abstained`, because P2's Done-means 6
needs a run whose only change is a lower ceiling to produce zero new divergences --
which is only true if a deferral never reaches a quality verdict. P2 enforces the
pairing too, and these tests prove P9 hands over a pair P2 accepts rather than one
it has to correct.
"""
from __future__ import annotations

import json

import pytest

from database_agent.db import create_schema
from eval_harness.run import start_run
from eval_harness.stage_output import dimension_values, stage_outputs
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import STAGE_IDS
from grouping.stage_output import (
    BUDGET_DEFERRED,
    EVIDENCE_REFUSAL,
    GRAPH_STAGE,
    GROUPING_STAGE,
    P9_STAGES,
    RECORD_WRITTEN,
    RETRIEVAL_STAGE,
    UnknownP9Result,
    emit_graph_stage,
    emit_grouping_stage,
    emit_retrieval_stage,
    map_result,
)

GROUP = "group-1"


@pytest.fixture()
def replay_conn(conn):
    create_schema(conn)
    create_eval_schema(conn)
    return conn


@pytest.fixture()
def run(replay_conn):
    from llm_harness.stage_output import record_p8_version_tuple

    ref = record_p8_version_tuple(replay_conn, **_axes())
    run_id = start_run(
        replay_conn, bundle_id="bundle-p9", run_kind="replay",
        version_tuple_ref=ref, budget_ceilings={},
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1")
    return run_id, ref


def _axes():
    return dict(
        extractor_versions={},
        graph_algorithm_version="p9-graph-1",
        prompt_fingerprint="sha256:fp-group",
        model_identifier="fixture-model",
        template_library_version=None,
        placement_scorer_version=None,
        analysis_tiers_enabled=["llm"],
    )


def _emit(conn, emitter, run, *, result=RECORD_WRITTEN, payload=None):
    run_id, ref = run
    return emitter(
        conn, run_id=run_id, subject_ref=GROUP, result=result,
        payload=payload if payload is not None else {"anchors": 2},
        version_tuple_ref=ref, inputs=("file-1", "file-2"))


# --- the mapping, pinned ---------------------------------------------------------


def test_the_three_results_map_to_exactly_these_pairs():
    assert map_result(RECORD_WRITTEN) == ("produced", "within_ceiling")
    assert map_result(EVIDENCE_REFUSAL) == ("abstained", "within_ceiling")
    assert map_result(BUDGET_DEFERRED) == ("deferred", "ceiling_reached")


def test_a_result_p9_does_not_produce_is_refused_not_approximated():
    with pytest.raises(UnknownP9Result):
        map_result("nearly_a_group")


def test_a_deferral_is_never_an_abstention(replay_conn, run):
    """A deferral that reached `abstained` would make a lower ceiling look like a
    quality regression, and P2's Done-means 6 depends on it not doing that."""
    _emit(replay_conn, emit_grouping_stage, run, result=BUDGET_DEFERRED)
    row = stage_outputs(replay_conn, run[0], stage_id=GROUPING_STAGE)[0]
    assert row["outcome"] == "deferred"
    assert row["budget_state"] == "ceiling_reached"


def test_an_evidence_refusal_is_an_abstention_within_the_ceiling(replay_conn, run):
    """A stop rule fired, or coherence abstained, or retrieval found no plausible
    anchor. That is a measured quality verdict, not a budget event."""
    _emit(replay_conn, emit_grouping_stage, run, result=EVIDENCE_REFUSAL)
    row = stage_outputs(replay_conn, run[0], stage_id=GROUPING_STAGE)[0]
    assert row["outcome"] == "abstained"
    assert row["budget_state"] == "within_ceiling"


# --- the three stages, and only the three ----------------------------------------


def test_p9_emits_the_three_stages_the_design_gives_it(replay_conn, run):
    _emit(replay_conn, emit_retrieval_stage, run)
    _emit(replay_conn, emit_graph_stage, run)
    _emit(replay_conn, emit_grouping_stage, run)
    emitted = {
        row["stage_id"] for row in stage_outputs(replay_conn, run[0])
    }
    assert emitted == set(P9_STAGES)
    assert P9_STAGES == (RETRIEVAL_STAGE, GRAPH_STAGE, GROUPING_STAGE)
    assert set(P9_STAGES) <= set(STAGE_IDS)


def test_p9_publishes_no_emitter_for_the_model_call_stage():
    """`llm_interpretation` measures the model call. P8 makes the call, and two
    emitters would double-count every one of them in the replay."""
    import grouping.stage_output as module

    assert "llm_interpretation" not in module.P9_STAGES
    text = open(module.__file__).read()
    assert "llm_interpretation" in text  # named, so the exclusion is legible
    assert not any(
        name.startswith("emit_") and "interpretation" in name
        for name in dir(module))


def test_each_stage_hands_over_its_own_measured_dimension(replay_conn, run):
    _emit(replay_conn, emit_retrieval_stage, run)
    _emit(replay_conn, emit_graph_stage, run)
    _emit(replay_conn, emit_grouping_stage, run)
    measured = {
        row["dimension"] for row in dimension_values(replay_conn, run[0])
    }
    assert measured == {"retrieval", "graph", "grouping"}


# --- the payload is opaque and canonical -----------------------------------------


def test_the_payload_is_canonical_so_two_equal_measurements_serialise_once(
    replay_conn, run,
):
    """A replay diff should be about the measurement, not about key order."""
    from eval_harness.stage_output import stage_payload

    # Two subjects, because P2 admits one measurement per subject per dimension
    # per run -- a second row for one subject would be two answers to one question.
    run_id, ref = run
    first = emit_grouping_stage(
        replay_conn, run_id=run_id, subject_ref="group-1",
        result=RECORD_WRITTEN, payload={"b": 2, "a": 1},
        version_tuple_ref=ref, inputs=())
    second = emit_grouping_stage(
        replay_conn, run_id=run_id, subject_ref="group-2",
        result=RECORD_WRITTEN, payload={"a": 1, "b": 2},
        version_tuple_ref=ref, inputs=())
    assert stage_payload(replay_conn, first) == stage_payload(replay_conn, second)
    assert json.loads(stage_payload(replay_conn, first)) == {"a": 1, "b": 2}


def test_the_inputs_are_the_stable_subject_refs_the_stage_consumed(
    replay_conn, run,
):
    output_id = _emit(replay_conn, emit_grouping_stage, run)
    row = stage_outputs(replay_conn, run[0], stage_id=GROUPING_STAGE)[0]
    assert row["stage_output_id"] == output_id
    assert json.loads(row["inputs"]) == ["file-1", "file-2"]


def test_an_emission_without_a_run_is_refused(replay_conn, run):
    _run_id, ref = run
    with pytest.raises(Exception):
        emit_grouping_stage(
            replay_conn, run_id="no-such-run", subject_ref=GROUP,
            result=RECORD_WRITTEN, payload={}, version_tuple_ref=ref,
            inputs=())


def test_p9_adds_no_live_run_kind():
    """Replay only. Emitting from ordinary ingestion would put a measurement in
    the harness for a run nobody asked to evaluate."""
    import pathlib

    import grouping.stage_output as module

    text = pathlib.Path(module.__file__).read_text()
    assert '"live"' not in text
    assert "run_kind" not in text
