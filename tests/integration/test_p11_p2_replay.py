"""P11 -> P2, through the live writer. Replay only; there is no live run kind.

Every assertion here is about a row P2's own `record_stage_output` accepted, so a
mis-mapped envelope fails at the writer rather than during comparison.
"""
from __future__ import annotations

import json

import pytest

from eval_harness.stage_output import (
    DimensionValue, dimension_values, record_stage_output, stage_outputs,
)

from placement import vocabulary as v
from placement.records import ConflictConsidered
from placement.retrieval import Candidate, Retrieval
from placement.stage_output import emit_retrieval_stage, emit_scoring_stage
from p11.conftest import (  # noqa: F401  -- fixtures, bound into this module
    FIXED_CLOCK, p11_conn, p11_version_tuple, p2_run_id,
)
from p11.test_p11_records import _decision


@pytest.fixture
def a_retrieval():
    """One candidate set, keyed on the same subject the decision below uses."""
    return Retrieval(subject_ref="file:f1:h1", plan_version="plan-1",
                     candidates=(), conflicts=(),
                     semantic_only_node_ids=frozenset())


@pytest.fixture
def a_full_retrieval():
    """A SECOND subject, with candidates and a recorded suppression.

    A second subject and not the same one: `stage_dimension_value` is keyed
    `(run_id, dimension, subject_ref)`, so two candidate sets for one file in one
    run are one contested row, and the writer says so.
    """
    return Retrieval(
        subject_ref="file:f2:h2", plan_version="plan-1",
        candidates=(Candidate(node_id="n-course", channels=("direct_fact",),
                              matching_facts=(), group_ids=("g-phys1401",)),),
        conflicts=(ConflictConsidered(
            kind="contradicted_expected_value", conflicting_value="PHYS1402",
            suppressed_node_ids=("n-course-alt",), evidence_ref="obs-1"),),
        semantic_only_node_ids=frozenset({"n-general"}))


def test_a_placement_stage_round_trips_with_its_dimension(p11_conn, p2_run_id,
                                                          p11_version_tuple):
    emit_scoring_stage(p11_conn, run_id=p2_run_id, decision=_decision(),
                       version_tuple_ref=p11_version_tuple,
                       inputs=("group:g1", "tree:plan-1"))
    rows = stage_outputs(p11_conn, p2_run_id, stage_id=v.PLACEMENT_SCORING)
    assert len(rows) == 1
    assert rows[0]["outcome"] == "produced"
    values = dimension_values(p11_conn, p2_run_id, dimension=v.DIMENSION_PLACEMENT)
    assert len(values) == 1


def test_the_retrieval_stage_is_attributable_at_all(p11_conn, p2_run_id,
                                                    p11_version_tuple,
                                                    a_retrieval):
    # `eval_harness/attribution.py` reads ONLY `stage_dimension_value` rows, both
    # to name the stage that emitted a failing assertion and to qualify ancestors.
    # A retrieval stage with no dimension row is invisible to both, so a placement
    # error that began in retrieval could never be measured as one. This is the
    # test that fails if the DimensionValue is dropped.
    emit_retrieval_stage(p11_conn, run_id=p2_run_id, retrieval=a_retrieval,
                         version_tuple_ref=p11_version_tuple, inputs=())
    values = dimension_values(p11_conn, p2_run_id, dimension=v.DIMENSION_RETRIEVAL)
    assert len(values) == 1
    assert values[0]["subject_ref"] == "candidates:plan-1:file:f1:h1"


def test_the_envelope_and_the_dimension_share_one_subject_ref(p11_conn, p2_run_id,
                                                              p11_version_tuple,
                                                              a_retrieval):
    # `_stage_verdicts` keys on the dimension row's subject_ref while `_edges`
    # keys on the envelope's. Unequal, the stage is measured and unreachable.
    emit_retrieval_stage(p11_conn, run_id=p2_run_id, retrieval=a_retrieval,
                         version_tuple_ref=p11_version_tuple, inputs=())
    rows = stage_outputs(p11_conn, p2_run_id, stage_id=v.CANDIDATE_NODE_RETRIEVAL)
    values = dimension_values(p11_conn, p2_run_id, dimension=v.DIMENSION_RETRIEVAL)
    assert rows[0]["subject_ref"] == values[0]["subject_ref"]


def test_scoring_names_the_retrieval_stage_as_an_input(p11_conn, p2_run_id,
                                                       p11_version_tuple,
                                                       a_retrieval):
    # The ancestor walk reaches a stage only through `inputs[]`. Without this,
    # a retrieval-origin error would attribute to `placement_scoring` (order 9)
    # rather than `candidate_node_retrieval` (order 8).
    emit_retrieval_stage(p11_conn, run_id=p2_run_id, retrieval=a_retrieval,
                         version_tuple_ref=p11_version_tuple, inputs=())
    emit_scoring_stage(p11_conn, run_id=p2_run_id, decision=_decision(),
                       version_tuple_ref=p11_version_tuple, inputs=("group:g1",))
    rows = stage_outputs(p11_conn, p2_run_id, stage_id=v.PLACEMENT_SCORING)
    assert "candidates:plan-1:file:f1:h1" in json.loads(rows[0]["inputs"])
    # The caller's own inputs survive: appending must not replace the grouping,
    # tree and validation refs the attribution walk also needs.
    assert "group:g1" in json.loads(rows[0]["inputs"])


def test_the_two_stages_do_not_collide_on_one_subject(p11_conn, p2_run_id,
                                                      p11_version_tuple,
                                                      a_retrieval):
    # `stage_dimension_value` is keyed (run_id, dimension, subject_ref). Both P11
    # stages measuring the same subject under one dimension would make the second
    # write raise, so the namespacing is what lets a run measure both at all.
    emit_retrieval_stage(p11_conn, run_id=p2_run_id, retrieval=a_retrieval,
                         version_tuple_ref=p11_version_tuple, inputs=())
    emit_scoring_stage(p11_conn, run_id=p2_run_id, decision=_decision(),
                       version_tuple_ref=p11_version_tuple, inputs=())
    retrieval_row = dimension_values(p11_conn, p2_run_id,
                                     dimension=v.DIMENSION_RETRIEVAL)[0]
    scoring_row = dimension_values(p11_conn, p2_run_id,
                                   dimension=v.DIMENSION_PLACEMENT)[0]
    assert retrieval_row["subject_ref"] != scoring_row["subject_ref"]
    assert scoring_row["subject_ref"] == "file:f1:h1"


def test_p9_and_p11_retrieval_rows_coexist_in_one_run(p11_conn, p2_run_id,
                                                      p11_version_tuple,
                                                      a_retrieval):
    # `stage_dimension_value` is keyed (run_id, dimension, subject_ref) and P9
    # already writes `retrieval` rows keyed on the bare file. Un-namespaced, this
    # second write raises IntegrityError in every full-pipeline replay.
    record_stage_output(
        p11_conn, run_id=p2_run_id, stage_id="retrieval",
        subject_ref="file:f1:h1", outcome="produced", payload=None,
        version_tuple_ref=p11_version_tuple, inputs=(),
        budget_state="within_ceiling",
        dimension_values=(DimensionValue(dimension="retrieval",
                                         subject_ref="file:f1:h1",
                                         outcome="produced", value={}),))
    emit_retrieval_stage(p11_conn, run_id=p2_run_id, retrieval=a_retrieval,
                         version_tuple_ref=p11_version_tuple, inputs=())
    assert len(dimension_values(p11_conn, p2_run_id, dimension="retrieval")) == 2


def test_two_plan_versions_of_one_subject_are_two_measurements(p11_conn, p2_run_id,
                                                               p11_version_tuple,
                                                               a_retrieval):
    # `retrieval` sits in P2's SHARED_EVIDENCE_DIMENSIONS while P11's candidate
    # retrieval is plan-scoped by construction: it retrieves only the legal
    # destinations of one frozen version. Without the version in the key the
    # second version's row would contest the first's instead of joining it.
    from dataclasses import replace

    emit_retrieval_stage(p11_conn, run_id=p2_run_id, retrieval=a_retrieval,
                         version_tuple_ref=p11_version_tuple, inputs=())
    emit_retrieval_stage(p11_conn, run_id=p2_run_id,
                         retrieval=replace(a_retrieval, plan_version="plan-2"),
                         version_tuple_ref=p11_version_tuple, inputs=())
    assert len(dimension_values(p11_conn, p2_run_id,
                                dimension=v.DIMENSION_RETRIEVAL)) == 2


def test_a_retrieval_that_found_nothing_is_an_abstention_not_a_production(
        p11_conn, p2_run_id, p11_version_tuple, a_retrieval, a_full_retrieval):
    # SPEC:275: "retrieval returned no legal candidate" is `abstained`. Reporting
    # it as `produced` would make an empty candidate set indistinguishable from a
    # full one in the replay, which is the measurement §8.5 asks for.
    emit_retrieval_stage(p11_conn, run_id=p2_run_id, retrieval=a_retrieval,
                         version_tuple_ref=p11_version_tuple, inputs=())
    emit_retrieval_stage(p11_conn, run_id=p2_run_id, retrieval=a_full_retrieval,
                         version_tuple_ref=p11_version_tuple, inputs=())
    outcomes = {row["subject_ref"]: row["outcome"] for row in stage_outputs(
        p11_conn, p2_run_id, stage_id=v.CANDIDATE_NODE_RETRIEVAL)}
    assert outcomes["candidates:plan-1:file:f1:h1"] == "abstained"
    assert outcomes["candidates:plan-1:file:f2:h2"] == "produced"


def test_the_retrieval_payload_carries_what_was_ruled_out(p11_conn, p2_run_id,
                                                          p11_version_tuple,
                                                          a_full_retrieval):
    # §8.2 and SPEC:502-504: a review surface that cannot show what was ruled out
    # cannot answer "why not that folder?", and a replay that cannot see the
    # suppression cannot tell a retrieval miss from a deliberate exclusion.
    emit_retrieval_stage(p11_conn, run_id=p2_run_id, retrieval=a_full_retrieval,
                         version_tuple_ref=p11_version_tuple, inputs=())
    row = stage_outputs(p11_conn, p2_run_id,
                        stage_id=v.CANDIDATE_NODE_RETRIEVAL)[0]
    payload = json.loads(row["payload"])
    assert payload["retrieved"] == ["n-course"]
    assert payload["suppressed"] == ["n-course-alt"]
    assert payload["semantic_only"] == ["n-general"]


def test_a_lower_ceiling_produces_deferrals_and_no_divergences(
        p11_conn, p2_run_id, p11_version_tuple):
    # P2 Done-means 6: a run whose only change is a lower budget ceiling must
    # produce zero new divergences, which is only true if a deferral never
    # reaches a quality verdict.
    deferred = _decision(outcome=v.ABSTAIN, destination=None,
                         abstention_reason=v.BUDGET_DEFERRED,
                         deferred_stage=v.PLACEMENT_SCORING)
    emit_scoring_stage(p11_conn, run_id=p2_run_id, decision=deferred,
                       version_tuple_ref=p11_version_tuple, inputs=())
    rows = stage_outputs(p11_conn, p2_run_id, stage_id=v.PLACEMENT_SCORING)
    assert rows[0]["outcome"] == "deferred"
    assert rows[0]["budget_state"] == "ceiling_reached"
    assert dimension_values(p11_conn, p2_run_id,
                            dimension=v.DIMENSION_PLACEMENT)[0]["outcome"] == (
        "deferred")


def test_an_abstention_is_written_within_ceiling_and_p2_would_refuse_otherwise(
        p11_conn, p2_run_id, p11_version_tuple):
    # The negative twin of the deferral. P2 refuses `abstained` with
    # `ceiling_reached` outright, so the pairing is proved by the write
    # succeeding -- and by P2 rejecting the collapsed version.
    emit_scoring_stage(
        p11_conn, run_id=p2_run_id, version_tuple_ref=p11_version_tuple,
        inputs=(),
        decision=_decision(outcome=v.ABSTAIN, destination=None,
                           abstention_reason=v.NO_SUPPORTED_DESTINATION))
    row = stage_outputs(p11_conn, p2_run_id, stage_id=v.PLACEMENT_SCORING)[0]
    assert (row["outcome"], row["budget_state"]) == ("abstained",
                                                     "within_ceiling")
    with pytest.raises(ValueError):
        record_stage_output(
            p11_conn, run_id=p2_run_id, stage_id=v.PLACEMENT_SCORING,
            subject_ref="file:f2:h2", outcome="abstained", payload=None,
            version_tuple_ref=p11_version_tuple, inputs=(),
            budget_state="ceiling_reached")
