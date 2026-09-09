"""§6.10 recorded, not merely applied — including the degenerate one-node case."""
from __future__ import annotations

import pytest

from placement import vocabulary as v
from placement.config import ConfigurationRequired, PlacementLimits, SupportPolicy
from placement.graph import NodeLocalGraph, build_node_local_graph
from placement.index import build_destination_index, entry_for
from placement.records import ConflictConsidered, GraphAnchor, MatchingFact, Subject
from placement.retrieval import (
    ACCEPTED_GROUP, CHANNELS, CURATED_FOLDER, Candidate, DIRECT_FACT,
    GRAPH_RELATIONSHIP, PRODUCED_CHANNELS, Retrieval, SEMANTIC_NEIGHBOUR,
    retrieve,
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

# THE FIXTURE POLICY IS THE DEPLOYMENT'S OWN, and `104` §18.2 gap 13 is why it
# can be. It used to be 0.4 against `cli.py`'s 0.5, and the old comment said
# exactly why: `assess` divided by `_MAX_WEIGHT = 3 + 2 + 1 + 1 = 7` while
# `retrieve` produced two of those four channels, so the strongest evidence this
# module's `_candidate()` carries -- a direct fact and nothing else -- reached
# `1.0 * 3 / 7 = 0.4285…` and a 0.5 bar made every placement test here
# arithmetically impossible. A fixture that has to lower the product's threshold
# to see the product place anything is a fixture reporting a defect.
#
# `scoring.producible_weight` now derives the denominator from what the retrieval
# declares it produces, so over `PRODUCED_CHANNELS` the attainable set is
# {0, .4, .6, 1.0}: a direct fact alone is 0.6 and clears, an accepted group
# alone is 0.4 and falls short, semantic-only is 0. The fixture and the product
# now run the SAME numbers, which is the only way a test here says anything about
# a real run.
POLICY = SupportPolicy(policy_id="fixture-v2", support_scale_max=1.0,
                       minimum_support_threshold=0.50, margin_threshold=0.20)

# THE RELEASE-2 SCALE, for the three tests that exercise a channel nothing
# produces yet. `GRAPH_RELATIONSHIP` has no producer until §18.2 gap 12 lands and
# `STRUCTURAL_RELATIONSHIP` none until gap 14 does, so `score_candidates` refuses
# a candidate carrying either against a retrieval declaring `PRODUCED_CHANNELS`.
# A test about what a graph edge is WORTH still has to be able to say so, and it
# says so by declaring a retrieval that produces all six -- which is exactly the
# shape those two gaps will create, denominator 7 and all. The threshold goes
# back to 0.4 for the same arithmetic reason the whole module used to: over seven
# a direct fact alone is 0.4285.
POLICY_OVER_ALL_SIX = SupportPolicy(
    policy_id="fixture-release2-v1", support_scale_max=1.0,
    minimum_support_threshold=0.40, margin_threshold=0.20)


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
        neighbourhood_size=anchors, cluster_size=anchors,
        reduced_to_strongest=False,
    )


def _retrieval(candidates, conflicts=(), semantic_only=frozenset(),
               producible=PRODUCED_CHANNELS):
    return Retrieval(subject_ref="file:f1:h1", plan_version="plan-1",
                     candidates=tuple(candidates), conflicts=tuple(conflicts),
                     semantic_only_node_ids=semantic_only,
                     producible_channels=producible)


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
    """A margin failure with ONE supported candidate is `low_margin`, not two homes.

    ON THE RELEASE-2 SCALE, and `104` §18.2 gap 13 is why it had to move there.
    Over `PRODUCED_CHANNELS` the attainable weights are 0, 2, 3 and 5 over a
    denominator of 5, so the smallest non-zero margin is `(3 - 2) / 5 = 0.2` --
    exactly the threshold, which it clears. Every non-zero margin this deployment
    can produce is therefore decisive, and a failing NON-ZERO margin needs a finer
    scale to exist at all. Over all six channels it does: a direct fact
    (3/7 = 0.4286) against an accepted group alone (2/7 = 0.2857) is 1/7 = 0.1429,
    inside the 0.2 band, with only the best one clearing the 0.4 bar.

    This is the negative twin of `test_two_supported_homes_...` below. A fix that
    renamed EVERY margin failure "two homes" would pass that test and destroy this
    signal, so the two are read together or neither means anything.

    SABOTAGE: name the pair against `POLICY` and `PRODUCED_CHANNELS` instead --
    the margin comes out 0.2, clears, and the assessment places the file rather
    than leaving it unresolved.
    """
    two = [_candidate(),
           _candidate(node_id="n-course-alt", channels=(ACCEPTED_GROUP,),
                      facts=())]
    result = assess(_retrieval(two, producible=CHANNELS),
                    {"n-course": _graph(), "n-course-alt": _graph("n-course-alt")},
                    policy=POLICY_OVER_ALL_SIX)
    assert result.two_condition.margin_over_next == pytest.approx(1 / 7)
    assert result.two_condition.meets_margin == v.MARGIN_FALSE
    assert result.two_condition.verdict == "weak"
    assert result.two_condition.requires_review is True
    assert result.abstention_reason == v.LOW_MARGIN


def test_two_supported_homes_are_named_as_two_homes_not_as_weak_evidence():
    """The owner's own nuance case: a research paper that is also homework.

    Both destinations are reached by a direct fact on a DIFFERENT field --
    `subject = PHYS1401` and `project = PVA-RDP` -- so §6.3's suppression
    correctly suppresses neither, and both score 3/5 = 0.6, above the 0.5
    threshold. The margin is exactly 0.0.

    The routing is already right: verdict `weak`, `requires_review` true, nothing
    moves. What was wrong is the SENTENCE. `low_margin` is a complaint about the
    quality of the evidence, and a user told that will distrust the extraction.
    The truth is that this file has two correct homes and the choice is theirs.
    """
    two = [_candidate(), _candidate(node_id="n-project")]
    result = assess(_retrieval(two),
                    {"n-course": _graph(), "n-project": _graph("n-project")},
                    policy=POLICY)
    assert result.scored[0].support_score == result.scored[1].support_score
    assert result.two_condition.margin_over_next == 0.0
    assert result.two_condition.meets_margin == v.MARGIN_FALSE
    # The routing is UNCHANGED. Only the account of it moves.
    assert result.two_condition.verdict == "weak"
    assert result.two_condition.requires_review is True
    assert result.abstention_reason == v.MULTIPLE_SUPPORTED_HOMES
    assert result.abstention_reason != v.LOW_MARGIN


def test_a_third_supported_home_reads_the_same_as_two():
    # The name is not "two homes" and the count is not two. Three tied direct
    # matches are the same sentence to a user: several right answers, pick one.
    three = [_candidate(), _candidate(node_id="n-project"),
             _candidate(node_id="n-reading")]
    result = assess(_retrieval(three),
                    {name: _graph(name)
                     for name in ("n-course", "n-project", "n-reading")},
                    policy=POLICY)
    assert result.abstention_reason == v.MULTIPLE_SUPPORTED_HOMES


def test_a_tie_nothing_supports_is_not_two_homes():
    # The other half of the threshold half. Two candidates tie exactly at 2/5 =
    # 0.4, and NEITHER clears the 0.5 support threshold -- accepted-group
    # evidence alone on both sides. There are no supported homes here at all, so
    # calling it "two homes" would promise the user a choice between two
    # destinations the evidence never backed.
    two = [_candidate(channels=(ACCEPTED_GROUP,), facts=()),
           _candidate(node_id="n-course-alt", channels=(ACCEPTED_GROUP,),
                      facts=())]
    result = assess(_retrieval(two),
                    {"n-course": _graph(), "n-course-alt": _graph("n-course-alt")},
                    policy=POLICY)
    assert result.two_condition.meets_threshold is False
    assert result.two_condition.margin_over_next == 0.0
    assert result.abstention_reason == v.LOW_MARGIN


def test_a_measured_margin_over_the_threshold_reads_true_not_vacuous():
    """The third `meets_margin` value is reachable, and on THIS deployment's scale.

    `104` §18.2 gap 13's headline pair, and the one the arithmetic used to lose.
    A file whose direct facts match one node (3/5 = 0.6) against a node reached by
    an accepted group alone (2/5 = 0.4) is a margin of exactly 0.2, which is the
    threshold and clears it. The old fixture could not use this pair -- over seven
    it was 1/7 = 0.1429 and failed -- so it reached for `GRAPH_RELATIONSHIP`, a
    channel nothing produces, to manufacture a margin the product could not.

    THE FLOAT MATTERS HERE AND IS WHY `_exact_margin` EXISTS. `0.6 - 0.4` is
    `0.19999999999999996` in IEEE 754, below the threshold by one part in 10^17;
    `1.0 * (3 - 2) / 5` is exactly 0.2. Same rule, one division instead of the
    difference of two roundings.

    SABOTAGE: compute the margin as `best.support_score - runner_up.support_score`
    again -- `meets_margin` flips to `false`, `unique_direct_match` to False, and
    gap 13's unique direct match is unreachable in exactly the case a person meets.
    """
    two = [_candidate(),
           _candidate(node_id="n-course-alt", channels=(ACCEPTED_GROUP,),
                      facts=())]
    result = assess(_retrieval(two),
                    {"n-course": _graph(), "n-course-alt": _graph("n-course-alt")},
                    policy=POLICY)
    assert result.two_condition.meets_margin == v.MARGIN_TRUE
    assert result.two_condition.margin_over_next == 0.2
    assert result.two_condition.meets_threshold is True
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
    #
    # ON THE RELEASE-2 SCALE, because `GRAPH_RELATIONSHIP` has no producer until
    # `104` §18.2 gap 12 lands and `score_candidates` refuses a candidate carrying
    # a channel its retrieval says it cannot produce. The rule under test is what
    # a graph edge is WORTH, which is gap 12's question and survives the wait.
    candidate = _candidate(channels=(ACCEPTED_GROUP, GRAPH_RELATIONSHIP), facts=())
    result = assess(_retrieval([candidate], producible=CHANNELS),
                    {"n-course": _graph()}, policy=POLICY_OVER_ALL_SIX)
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
    # TWO DIRECT-FACT CANDIDATES, and `104` §18.2 gap 13 is why the fixture had to
    # change. It used to pair a direct fact against an accepted group alone, which
    # was ambiguous only because the old denominator kept the direct match below
    # the bar; on the producible scale that pair is a decisive 0.6 against 0.4 and
    # asking a model about it would be the round trip §6.6 forbids. Genuine
    # ambiguity is two candidates the SAME evidence reaches equally, which is what
    # `unique_direct_match` is a property of: the facts, not the candidate count.
    two = [_candidate(), _candidate(node_id="n-project")]
    result = assess(_retrieval(two),
                    {"n-course": _graph(), "n-project": _graph("n-project")},
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


# --- R-19 (Q-A): when a model decides, every placeable file is asked ---------------
#
# `104` §13.5 and `00`'s placement amendment: "Every placement goes through the
# model. Deterministic scores rank and shortlist the candidates the model is
# shown... A unique direct match is the top-ranked candidate, not a bypass. This
# governs whenever a model is configured; with no model configured, the
# deterministic path remains the fallback."
#
# So the two clauses that used to END the question -- a unique direct match, and a
# file already sitting where the answer says it belongs -- become reasons the
# model's answer is CHEAP to get right, not reasons to skip asking. What survives
# untouched is the offline path: the argument defaults to False, and every caller
# that does not pass it gets exactly the routing it had.


def test_r19_a_unique_direct_match_is_asked_when_a_model_decides():
    result = assess(_retrieval([_candidate()]), {"n-course": _graph()},
                    policy=POLICY)
    assert result.unique_direct_match is True
    # The fallback, unchanged: no model configured, no call, §6.6 as written.
    assert needs_model_call(result) is False
    assert needs_model_call(result, model_decides=True) is True


def test_r19_a_file_already_where_it_belongs_is_asked_when_a_model_decides():
    own = _candidate("n-own", channels=(DIRECT_FACT, CURATED_FOLDER))
    rival = _candidate("n-proposed", channels=(DIRECT_FACT,))
    result = assess(_retrieval([own, rival]), {}, policy=POLICY,
                    their_own_folder_node_ids=frozenset({"n-own"}))
    assert result.stays_put is True
    assert result.abstention_reason is None
    assert needs_model_call(result) is False
    assert needs_model_call(result, model_decides=True) is True


def test_r19_a_file_with_no_candidate_at_all_is_asked_of_nobody():
    """The one clause that does NOT move. `00`:106 forbids inventing a
    destination after freeze, so a file with no legal candidate has nothing for
    a model to choose between and asking one would be inviting it to invent."""
    result = assess(_retrieval([]), {}, policy=POLICY)
    assert result.scored == ()
    assert needs_model_call(result) is False
    assert needs_model_call(result, model_decides=True) is False


def test_r19_an_ambiguous_file_is_asked_either_way():
    # Two direct-fact homes, for the reason
    # `test_several_plausible_nodes_ask_for_a_model_rather_than_guessing` gives.
    two = [_candidate(), _candidate(node_id="n-project")]
    result = assess(_retrieval(two),
                    {"n-course": _graph(), "n-project": _graph("n-project")},
                    policy=POLICY)
    assert needs_model_call(result) is True
    assert needs_model_call(result, model_decides=True) is True


def test_r19_the_ranking_is_what_shortlists_and_the_winner_is_the_top_of_it():
    """"Scores rank and shortlist the candidates the model is shown" -- the
    deterministic winner is `scored[0]` and stays recorded in rank order, which
    is what makes a unique direct match the top candidate rather than a bypass."""
    two = [_candidate(), _candidate(node_id="n-course-alt",
                                    channels=(ACCEPTED_GROUP,), facts=())]
    result = assess(_retrieval(two),
                    {"n-course": _graph(), "n-course-alt": _graph("n-course-alt")},
                    policy=POLICY)
    assert [s.node_id for s in result.scored] == ["n-course", "n-course-alt"]
    assert [(a.node_id, a.rank) for a in result.alternatives] == [
        ("n-course", 1), ("n-course-alt", 2)]
    assert result.scored[0].support_score > result.scored[1].support_score
