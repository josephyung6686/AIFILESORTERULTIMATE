"""P2 owns the envelope; P11 owns the record; the mapping is the whole task.

The row that must not collapse is `deferred` into `abstained`. It is kept apart
STRUCTURALLY -- three named P11 results, three envelopes, and a module-level
assertion that the three are three -- rather than by the order of two `if`s,
because an ordering is something a later edit can silently reverse.
"""
from __future__ import annotations

import pytest

from eval_harness.stage_output import ForeignVocabulary, record_stage_output
from eval_harness.vocabulary import DIMENSIONS, STAGE_IDS as P2_STAGE_IDS

from placement import vocabulary as v
from placement.records import ResidualContext
from placement.stage_output import (
    BUDGET_DEFERRAL, DECISION_WRITTEN, EVIDENTIAL_ABSTENTION, P11_RESULTS,
    UnknownP11Result, dimension_for, envelope_for, envelope_of, result_of,
)
from p11.test_p11_records import _decision


def _residual(outcome):
    return _decision(
        origin_stage=v.RESIDUAL, outcome=outcome, destination=None,
        residual=ResidualContext(set_id="s1", set_decision=v.REVIEW_WITH_MODEL,
                                 lifecycle_policy_ref=None))


def _deferred():
    return _decision(outcome=v.ABSTAIN, destination=None,
                     abstention_reason=v.BUDGET_DEFERRED,
                     deferred_stage=v.PLACEMENT_SCORING)


# --- the two vocabularies ------------------------------------------------------------

def test_p11_emits_only_two_of_p2s_ten_stages():
    assert set(v.STAGE_IDS) <= set(P2_STAGE_IDS)
    assert v.STAGE_IDS == ("candidate_node_retrieval", "placement_scoring")
    assert "P11" not in P2_STAGE_IDS


def test_p11s_own_outcome_can_never_reach_the_envelope(p11_conn, p2_run_id,
                                                       p11_version_tuple):
    with pytest.raises(ForeignVocabulary):
        record_stage_output(
            p11_conn, run_id=p2_run_id, stage_id=v.PLACEMENT_SCORING,
            subject_ref="file:f1:h1", outcome=v.PLACE, payload=None,
            version_tuple_ref=p11_version_tuple, inputs=(),
            budget_state="within_ceiling")


def test_no_p11_outcome_is_ever_an_envelope_value():
    # The negative twin of the refusal above, stated over the whole vocabulary
    # rather than one value: the mapping below is a FUNCTION between two closed
    # sets, and it would be a copy of one of them if the sets overlapped.
    from eval_harness.vocabulary import OUTCOMES as P2_OUTCOMES
    assert set(v.OUTCOMES).isdisjoint(P2_OUTCOMES)


# --- the mapping, and the row that must not collapse ----------------------------------

def test_the_three_p11_results_map_to_three_distinct_envelopes():
    # SPEC:280-288 made structural. Two results sharing one envelope is exactly
    # the collapse the design forbids, and it is refused here by counting rather
    # than described in a comment.
    envelopes = {result: envelope_of(result) for result in P11_RESULTS}
    assert len(P11_RESULTS) == 3
    assert len(set(envelopes.values())) == 3
    with pytest.raises(UnknownP11Result):
        envelope_of("nearly_deferred")


def test_a_placement_is_produced_within_ceiling():
    assert result_of(_decision()) == DECISION_WRITTEN
    assert envelope_for(_decision()) == ("produced", "within_ceiling")


def test_an_evidential_abstention_is_abstained_within_ceiling():
    for reason in (v.NO_SUPPORTED_DESTINATION, v.LOW_MARGIN, v.SEMANTIC_ONLY,
                   v.GENERIC_HUB_ONLY, v.CONFLICTING_FACTS, v.NO_SHARED_BRANCH,
                   v.PRIVACY_BLOCKED):
        decision = _decision(outcome=v.ABSTAIN, destination=None,
                             abstention_reason=reason)
        assert result_of(decision) == EVIDENTIAL_ABSTENTION, reason
        assert envelope_for(decision) == ("abstained", "within_ceiling"), reason


def test_a_budget_deferral_is_deferred_and_never_abstained():
    # SPEC:280-288 and Done-means 14. Scored as `abstained`, P2 would grade a
    # ceiling-truncated run as a judgement about evidence when none was made.
    decision = _deferred()
    assert result_of(decision) == BUDGET_DEFERRAL
    assert envelope_for(decision) == ("deferred", "ceiling_reached")
    assert envelope_for(decision) != envelope_for(
        _decision(outcome=v.ABSTAIN, destination=None,
                  abstention_reason=v.NO_SUPPORTED_DESTINATION))


def test_the_deferral_is_read_off_the_field_that_exists_to_show_it():
    # SPEC:734: "`deferred_stage` exists specifically so the interface can
    # distinguish deferred work from completed work". The record enforces the
    # biconditional with `abstention_reason = budget_deferred`, so reading either
    # is reading the same fact -- and this pins that, so a record that ever let
    # the two drift apart breaks here rather than silently downgrading a deferral
    # to an abstention in the replay.
    from placement.records import MalformedPlacementRecord

    assert _deferred().deferred_stage == v.PLACEMENT_SCORING
    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=v.ABSTAIN, destination=None,
                  abstention_reason=v.BUDGET_DEFERRED, deferred_stage=None)
    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=v.ABSTAIN, destination=None,
                  abstention_reason=v.LOW_MARGIN,
                  deferred_stage=v.PLACEMENT_SCORING)


def test_a_non_place_non_abstain_outcome_is_still_produced():
    # SPEC:274: a record written with any outcome other than `abstain` is
    # `produced`. `leave_in_place` is a decision, not a failure to decide.
    for outcome in (v.LEAVE_IN_PLACE, v.MARK_REVIEW_LATER):
        assert envelope_for(_residual(outcome))[0] == "produced"


# --- the dimensions ---------------------------------------------------------------------

def test_a_correct_abstention_is_a_pass_on_its_dimension():
    # Done-means 11: P2's placement and residual assertions score a correct
    # abstention as success, not as a miss. `abstained` is P2's own success
    # outcome for that case; `divergent` would be the miss.
    decision = _decision(outcome=v.ABSTAIN, destination=None,
                         abstention_reason=v.NO_SUPPORTED_DESTINATION)
    value = dimension_for(decision)
    assert value.dimension == v.DIMENSION_PLACEMENT
    assert value.outcome == "abstained"


def test_a_residual_decision_carries_the_residual_dimension():
    # `residual` is a P2 dimension with no same-named stage
    # (eval_harness/vocabulary.py:6-7). P11 attaches it to `placement_scoring`
    # rather than inventing an eleventh stage.
    value = dimension_for(_residual(v.LEAVE_IN_PLACE))
    assert value.dimension == v.DIMENSION_RESIDUAL
    assert value.dimension in DIMENSIONS


def test_a_placement_decision_never_carries_the_residual_dimension():
    # The negative twin: a `dimension_for` that always answered `residual` would
    # pass the test above and silently move every §6 measurement onto §7's metric.
    assert dimension_for(_decision()).dimension == v.DIMENSION_PLACEMENT
    assert v.DIMENSION_PLACEMENT != v.DIMENSION_RESIDUAL


def test_a_deferred_decision_reaches_no_quality_verdict_on_its_dimension():
    # P2 Done-means 6: a run whose only change is a lower ceiling produces zero
    # new divergences. That is only true if the DIMENSION value carries
    # `deferred` too -- an envelope that deferred while its dimension said
    # `abstained` would be graded as a judgement about evidence after all.
    assert dimension_for(_deferred()).outcome == "deferred"


# --- the gap this task leaves open, tracked rather than described -----------------------

def test_the_two_stages_are_emitted_from_somewhere_in_placement():
    """`emit_retrieval_stage` and `emit_scoring_stage` have no caller.

    Their owed consumer is the §6.12 pipeline, which is not built. Until it is,
    two of §8.5's ten stages have a producer that nothing runs -- and a stage with
    no emitter is exactly the "not_implemented" hole P2 carries a value for. The
    mapping is tested here and against P2's live writer in
    `tests/integration/test_p11_p2_replay.py`; what is missing is the call.

    The gap is CLOSED: `placement/pipeline.py` emits the retrieval stage from
    `place_file` and the scoring stage from every decision writer, whenever the
    caller supplied a `P2Run`. The `xfail(strict=True)` marker that reported the
    gap is gone, removed by the XPASS it was written to produce.
    """
    from p11.test_p11_groups import _placement_sources_calling

    for entry_point in ("emit_retrieval_stage", "emit_scoring_stage"):
        assert _placement_sources_calling(entry_point) - {"stage_output.py"}, (
            entry_point)



