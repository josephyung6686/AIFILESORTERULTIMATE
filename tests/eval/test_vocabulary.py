# tests/eval/test_vocabulary.py
import pytest

from eval_harness import vocabulary as V


def test_there_are_exactly_ten_attribution_stages_in_8_5_order():
    assert V.STAGE_IDS == (
        "extraction", "factual_validation", "retrieval", "graph_construction",
        "llm_interpretation", "grouping", "template_generation", "tree_design",
        "candidate_node_retrieval", "placement_scoring",
    )
    assert len(V.STAGE_IDS) == len(set(V.STAGE_IDS)) == 10


def test_there_are_exactly_ten_measured_dimensions():
    assert V.DIMENSIONS == (
        "extraction", "fact", "retrieval", "graph", "llm_grounding",
        "grouping", "template", "tree", "placement", "residual",
    )
    assert len(V.DIMENSIONS) == len(set(V.DIMENSIONS)) == 10


def test_the_two_lists_are_not_the_same_list():
    # SPEC Contract out §2: a SEPARATE ten-item list. Done-means 2: none is
    # collapsed into another.
    assert set(V.STAGE_IDS) != set(V.DIMENSIONS)


def test_the_two_asymmetries_are_recorded_as_found_not_resolved():
    # SPEC Open question 1 is OPEN. These three names are the whole of it, and
    # this test is the standing record: it fails the day someone quietly adds a
    # `residual` stage or a `factual_validation` dimension to close the gap in
    # code instead of in the design.
    assert "factual_validation" in V.STAGE_IDS and "factual_validation" not in V.DIMENSIONS
    assert "candidate_node_retrieval" in V.STAGE_IDS and "candidate_node_retrieval" not in V.DIMENSIONS
    assert "residual" in V.DIMENSIONS and "residual" not in V.STAGE_IDS


def test_no_dimension_to_stage_mapping_exists_anywhere_in_p2():
    # Answering OQ1 in code would look exactly like this mapping appearing.
    # The emitting stage names itself (Task 9); P2 never looks a dimension up.
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness"
    for path in src.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "STAGE_FOR_DIMENSION" not in text, path.name
        assert "DIMENSION_TO_STAGE" not in text, path.name


def test_five_dimensions_are_plan_scoped_and_five_are_not():
    # SPEC Cross-cutting answers → Plan versioning (§8.8): the evidence database
    # remains shared across plan versions, so five dimensions move with the
    # pinned plan version and five do not.
    assert V.PLAN_SCOPED_DIMENSIONS == frozenset(
        {"grouping", "template", "tree", "placement", "residual"})
    assert V.SHARED_EVIDENCE_DIMENSIONS == frozenset(
        {"extraction", "fact", "retrieval", "graph", "llm_grounding"})
    assert V.PLAN_SCOPED_DIMENSIONS | V.SHARED_EVIDENCE_DIMENSIONS == set(V.DIMENSIONS)
    assert not (V.PLAN_SCOPED_DIMENSIONS & V.SHARED_EVIDENCE_DIMENSIONS)


def test_the_five_envelope_outcomes():
    assert V.OUTCOMES == ("produced", "abstained", "deferred", "not_implemented", "error")
    assert V.BUDGET_STATES == ("within_ceiling", "ceiling_reached")


def test_the_seven_verdicts():
    assert V.VERDICTS == (
        "match", "divergent", "abstained_correctly", "abstained_incorrectly",
        "asserted_incorrectly", "deferred", "not_run",
    )


def test_the_remaining_closed_vocabularies():
    assert V.RUN_KINDS == ("replay", "shadow", "adversarial")
    assert V.CORPUS_FORMS == ("snapshot", "metadata_safe")
    assert V.EXPECTED_OUTCOME_KINDS == ("produced", "abstained", "not-applicable")
    assert V.EXPECTATION_SOURCES == ("hand-labelled", "captured-from-accepted-user-decision")


def test_an_unknown_stage_or_dimension_is_rejected():
    with pytest.raises(V.UnknownStage):
        V.check_stage("residual")            # a dimension, not a stage — OQ1
    with pytest.raises(V.UnknownDimension):
        V.check_dimension("factual_validation")   # a stage, not a dimension — OQ1
    V.check_stage("placement_scoring")
    V.check_dimension("placement")


def test_stage_order_is_the_pipeline_order_used_for_attribution():
    assert V.stage_order("extraction") == 0
    assert V.stage_order("placement_scoring") == 9
    assert V.stage_order("grouping") < V.stage_order("tree_design")
