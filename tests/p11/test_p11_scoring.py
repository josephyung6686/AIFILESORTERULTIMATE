"""§6.10 recorded, not merely applied — including the degenerate one-node case."""
from __future__ import annotations

import pytest

from placement import vocabulary as v
from placement.config import ConfigurationRequired, PlacementLimits, SupportPolicy
from placement.graph import NodeLocalGraph, build_node_local_graph
from placement.index import build_destination_index, entry_for
from placement.records import ConflictConsidered, GraphAnchor, MatchingFact, Subject
from placement.retrieval import (
    ACCEPTED_GROUP, Candidate, DIRECT_FACT, GRAPH_RELATIONSHIP, Retrieval,
    SEMANTIC_NEIGHBOUR, retrieve,
)
from placement.scoring import assess, needs_model_call
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE

LIMITS = PlacementLimits(
    max_retrieved_neighbors=4, max_local_graph_neighborhood=8,
    max_candidate_cluster_size=6, max_residual_files_per_batch=50,
    max_dossier_tokens=4000, max_llm_calls_per_thousand_files=100,
    max_cost_per_scan=5,
)

# The threshold is 0.4, and the number is derived rather than picked. `assess`
# normalises by `_MAX_WEIGHT = 3 + 2 + 1 + 1 = 7`, so the highest score a
# candidate carrying ONLY the direct-fact channel can reach is
# `1.0 * 3 / 7 = 0.4285714…`. `_candidate()`'s default channels are
# `(DIRECT_FACT,)`, so a threshold of 0.5 would make every test in this module
# that expects a placement arithmetically impossible: the strongest evidence the
# fixture carries would still abstain. 0.4 sits below 3/7 and above the
# accepted-group-only score of `2/7 = 0.2857…`, so `test_one_high_frequency_
# entity_stays_uncertain` and the two semantic-only tests still fail the
# threshold, which is what they exist to prove.
POLICY = SupportPolicy(policy_id="fixture-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.4, margin_threshold=0.2)


def _fact(value="PHYS1401"):
    return MatchingFact(file_fact_id="ff1", field="subject", value=value,
                        reliability=v.DIRECT, evidence_ref="obs-1")


def _candidate(node_id="n-course", channels=(DIRECT_FACT,), facts=None):
    return Candidate(node_id=node_id, channels=channels,
                     matching_facts=(_fact(),) if facts is None else facts,
                     group_ids=())


def _graph(node_id="n-course", anchors=1, informative=True):
    edges = tuple(
        GraphAnchor(edge_type="shared_validated_fact", from_file_id="f1",
                    to_file_id=f"f-{i}", anchor_file_id=f"f-{i}")
        for i in range(anchors)
    )
    return NodeLocalGraph(
        subject_ref="file:f1:h1", node_id=node_id, anchors=edges,
        distinct_entities=frozenset({"PHYS1401"}) if anchors else frozenset(),
        high_frequency_entities=frozenset() if informative else frozenset({"PHYS1401"}),
        neighbourhood_size=anchors, reduced_to_strongest=False,
    )


def _retrieval(candidates, conflicts=(), semantic_only=frozenset()):
    return Retrieval(subject_ref="file:f1:h1", plan_version="plan-1",
                     candidates=tuple(candidates), conflicts=tuple(conflicts),
                     semantic_only_node_ids=semantic_only)


def test_a_unique_direct_match_needs_no_model_and_says_so():
    # Done-means 6, §6.6: the LLM is not called for direct unique matches.
    result = assess(_retrieval([_candidate()]),
                    {"n-course": _graph()}, policy=POLICY)
    assert result.unique_direct_match is True
    assert result.confidence_class == v.EXACT_FACT_MATCH
    assert result.two_condition.verdict == "accept_direct"
    assert needs_model_call(result) is False


def test_the_degenerate_case_records_a_vacuous_margin_and_places():
    result = assess(_retrieval([_candidate()]),
                    {"n-course": _graph()}, policy=POLICY)
    assert result.two_condition.margin_over_next is None
    assert result.two_condition.meets_margin == v.MARGIN_TRUE_VACUOUS
    assert result.two_condition.margin_threshold == POLICY.margin_threshold
    assert result.two_condition.meets_threshold is True


def test_the_degenerate_case_still_abstains_when_support_is_short():
    # 10b's second half, and the only half that proves the threshold stayed
    # binding: one destination must not become a funnel.
    weak = _candidate(channels=(SEMANTIC_NEIGHBOUR,), facts=())
    result = assess(_retrieval([weak], semantic_only=frozenset({"n-course"})),
                    {"n-course": _graph(anchors=0)}, policy=POLICY)
    assert result.two_condition.meets_threshold is False
    assert result.two_condition.meets_margin == v.MARGIN_TRUE_VACUOUS
    assert result.abstention_reason == v.SEMANTIC_ONLY
    assert result.confidence_class == v.ABSTAIN_NO_SUPPORTED_DESTINATION


def test_a_low_margin_between_two_candidates_is_unresolved():
    two = [_candidate(), _candidate(node_id="n-course-alt")]
    result = assess(_retrieval(two),
                    {"n-course": _graph(), "n-course-alt": _graph("n-course-alt")},
                    policy=POLICY)
    assert result.two_condition.margin_over_next is not None
    assert result.two_condition.meets_margin == v.MARGIN_FALSE
    assert result.two_condition.verdict == "weak"
    assert result.abstention_reason == v.LOW_MARGIN


def test_a_measured_margin_over_the_threshold_reads_true_not_vacuous():
    # The third `meets_margin` value has to be reachable or the three-valued
    # field is two-valued with a spare name. DIRECT_FACT (3/7 = 0.4285…) against
    # ACCEPTED_GROUP alone (2/7 = 0.2857…) is a margin of 1/7 = 0.1428…, so the
    # runner-up is pushed to GRAPH_RELATIONSHIP alone (1/7 = 0.1428…) for a
    # margin of 2/7 = 0.2857… -- above the 0.2 the policy calls meaningful.
    two = [_candidate(),
           _candidate(node_id="n-course-alt", channels=(GRAPH_RELATIONSHIP,),
                      facts=())]
    result = assess(_retrieval(two),
                    {"n-course": _graph(), "n-course-alt": _graph("n-course-alt")},
                    policy=POLICY)
    assert result.two_condition.meets_margin == v.MARGIN_TRUE
    assert result.two_condition.margin_over_next == pytest.approx(2 / 7)
    assert result.unique_direct_match is True


def test_a_semantic_embedding_alone_never_produces_a_place():
    # §6.5, and Done-means 5's second clause.
    result = assess(
        _retrieval([_candidate(channels=(SEMANTIC_NEIGHBOUR,), facts=())],
                   semantic_only=frozenset({"n-course"})),
        {"n-course": _graph(anchors=0)}, policy=POLICY)
    assert result.abstention_reason == v.SEMANTIC_ONLY
    assert result.two_condition.verdict in {"weak", "abstain"}


def test_one_high_frequency_entity_stays_uncertain():
    result = assess(
        _retrieval([_candidate(channels=(ACCEPTED_GROUP,), facts=())]),
        {"n-course": _graph(informative=False)}, policy=POLICY)
    assert result.abstention_reason == v.GENERIC_HUB_ONLY


def test_a_group_supported_acceptance_is_context_supported_and_reviewed():
    # ACCEPTED_GROUP (2) + GRAPH_RELATIONSHIP (1) = 3/7 = 0.4285…, the same score
    # a lone direct fact reaches. It clears the threshold on group and
    # relationship evidence with no direct fact anywhere, so §6.6's deterministic
    # path does not apply and the verdict must say `accept_context_supported`.
    # Recording `accept_direct` here would name a fact match that never happened.
    candidate = _candidate(channels=(ACCEPTED_GROUP, GRAPH_RELATIONSHIP), facts=())
    result = assess(_retrieval([candidate]), {"n-course": _graph()}, policy=POLICY)
    assert result.abstention_reason is None
    assert result.unique_direct_match is False
    assert result.confidence_class == v.CONTEXT_SUPPORTED_GROUP_MATCH
    assert result.two_condition.verdict == v.ACCEPT_CONTEXT_SUPPORTED
    assert result.two_condition.requires_review is True


def test_conflicting_facts_that_left_no_candidate_name_that_reason():
    conflict = ConflictConsidered(kind="subject", conflicting_value="PHYS1402",
                                  suppressed_node_ids=("n-course",),
                                  evidence_ref="obs-2")
    result = assess(_retrieval([], conflicts=[conflict]), {}, policy=POLICY)
    assert result.abstention_reason == v.CONFLICTING_FACTS
    assert result.two_condition.verdict == "abstain"


def test_no_candidates_and_no_conflicts_is_no_supported_destination():
    result = assess(_retrieval([]), {}, policy=POLICY)
    assert result.abstention_reason == v.NO_SUPPORTED_DESTINATION


def test_both_thresholds_are_on_every_assessment_however_it_ended():
    # Done-means 10: recorded, not just applied, so a reviewer can see WHY.
    for retrieval, graphs in (
        (_retrieval([_candidate()]), {"n-course": _graph()}),
        (_retrieval([]), {}),
    ):
        result = assess(retrieval, graphs, policy=POLICY)
        assert result.two_condition.support_threshold == POLICY.minimum_support_threshold
        assert result.two_condition.margin_threshold == POLICY.margin_threshold


def test_every_candidate_is_ranked_as_an_alternative_strongest_first():
    # SPEC's `alternatives[]`: the review surface answers "why not that one?"
    # from the same numbers the decision used, so every candidate is ranked --
    # not only the ones that lost by a little.
    two = [_candidate(node_id="n-course-alt", channels=(ACCEPTED_GROUP,), facts=()),
           _candidate()]
    result = assess(_retrieval(two),
                    {"n-course": _graph(), "n-course-alt": _graph("n-course-alt")},
                    policy=POLICY)
    assert [(a.node_id, a.rank) for a in result.alternatives] == [
        ("n-course", 1), ("n-course-alt", 2)]


def test_a_support_policy_is_required_and_never_defaulted():
    # SPEC Open question 1: the two thresholds are unsettled by the design and
    # are injected. Absent means refuse, not guess -- a scoring run under a
    # threshold nobody chose is the failure that leaves nothing to say so.
    with pytest.raises(ConfigurationRequired):
        assess(_retrieval([_candidate()]), {"n-course": _graph()}, policy=None)


def test_several_plausible_nodes_ask_for_a_model_rather_than_guessing():
    two = [_candidate(), _candidate(node_id="n-course-alt",
                                    channels=(ACCEPTED_GROUP,), facts=())]
    result = assess(_retrieval(two),
                    {"n-course": _graph(), "n-course-alt": _graph("n-course-alt")},
                    policy=POLICY)
    assert result.unique_direct_match is False
    assert needs_model_call(result) is True


def test_the_three_stages_bind_end_to_end_against_the_frozen_tree(p11_conn):
    """§6.2 -> §6.4 -> §6.10, with no hand-built record anywhere in the chain.

    Every other test in this module hands `assess` a `NodeLocalGraph` it built
    itself, which proves the scoring rules and nothing about the seams. This one
    runs the real `retrieve`, the real `build_node_local_graph` and the real
    `assess` over P10's frozen tree: a reference chain between three modules is
    not a seam, and only a run through all three catches an argument bound
    against a signature that moved.
    """
    build_destination_index(p11_conn, FROZEN_TREE, component_version="P11-test",
                            observed_at=FIXED_CLOCK)
    subject = Subject(kind=v.FILE, file_id="f1", content_hash="h1",
                      group_id=None, member_file_ids=())
    retrieval = retrieve(
        p11_conn, subject=subject, plan_version="plan-1", limits=LIMITS,
        facts=(MatchingFact(file_fact_id="ff1", field="subject", value="PHYS1401",
                            reliability=v.DIRECT, evidence_ref="obs-1"),),
        group_ids=(), curated_folder_labels=(), semantic_neighbours=(),
        component_version="P11-test", observed_at=FIXED_CLOCK)
    graphs = {
        candidate.node_id: build_node_local_graph(
            subject=subject, candidate=candidate,
            entry=entry_for(p11_conn, plan_version="plan-1",
                            node_id=candidate.node_id),
            related_files=({"edge_type": "shared_validated_fact",
                            "to_file_id": "f-syllabus", "entity": "PHYS1401",
                            "anchor_file_id": "f-syllabus", "weight": 1},),
            limits=LIMITS, entity_frequency={"PHYS1401": 6},
            generic_entity_frequency=200)
        for candidate in retrieval.candidates
    }
    result = assess(retrieval, graphs, policy=POLICY)

    assert [s.node_id for s in result.scored] == ["n-course"]
    assert result.scored[0].typed_support is True
    assert result.unique_direct_match is True
    assert result.two_condition.verdict == v.ACCEPT_DIRECT
    assert needs_model_call(result) is False
    # And §6.3's suppression survived the whole chain: `n-course-alt` was ruled
    # out and recorded, not merely left unranked.
    assert retrieval.conflicts[0].suppressed_node_ids == ("n-course-alt",)
