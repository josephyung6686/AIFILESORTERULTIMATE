"""A life that expects nothing ranks below the folder the file is already in.

A candidate with no expected value is a life or a pile with no claim. When the
file already sits in a folder, that life stays on the list and ranks below the
folder and below a child inside it. A proposed node that states an expected
value keeps the rank its score earned. Two real claims that tie stay in the
order they arrived in.
"""
from __future__ import annotations

from placement import vocabulary as v
from placement.config import SupportPolicy
from placement.records import MatchingFact
from placement.retrieval import (
    ACCEPTED_GROUP, CURATED_FOLDER, Candidate, DIRECT_FACT, PRODUCED_CHANNELS,
    Retrieval,
)
from placement.scoring import (
    Scored, assess, rank_an_empty_life_below_the_folder_the_file_is_in,
)

POLICY = SupportPolicy(policy_id="fixture-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.50, margin_threshold=0.20)

EMPTY = frozenset({"Life"})


def _scored(node_id, score, *, already_there=False):
    return Scored(node_id=node_id, support_score=score, typed_support=False,
                  semantic_only=False, generic_hub=False, support_weight=1,
                  producible_weight=1, already_there=already_there)


def _ids(scored):
    return [item.node_id for item in scored]


def _rank(scored, empty=EMPTY, descendants=frozenset()):
    return rank_an_empty_life_below_the_folder_the_file_is_in(
        tuple(scored), empty, descendants=descendants)


def test_an_empty_life_ranks_below_the_folder_the_file_is_in():
    ordered = _rank([
        _scored("Life", 1.0),
        _scored("Inbox", 0.6, already_there=True),
    ])
    assert _ids(ordered) == ["Inbox", "Life"]


def test_an_empty_life_ranks_below_a_child_inside_that_folder():
    ordered = _rank([
        _scored("Life", 1.0),
        _scored("Inbox", 0.6, already_there=True),
        _scored("lecture", 0.6),
    ], descendants=frozenset({"lecture"}))
    assert _ids(ordered) == ["Inbox", "lecture", "Life"]


def test_an_empty_life_between_the_folder_and_its_child_moves_below_the_child():
    ordered = _rank([
        _scored("Inbox", 0.6, already_there=True),
        _scored("Life", 0.6),
        _scored("lecture", 0.6),
    ], descendants=frozenset({"lecture"}))
    assert _ids(ordered) == ["Inbox", "lecture", "Life"]


def test_a_proposed_node_that_states_an_expected_value_keeps_its_rank():
    ordered = _rank([
        _scored("Life", 1.0),
        _scored("Course", 0.8),
        _scored("Inbox", 0.4, already_there=True),
    ])
    assert _ids(ordered) == ["Course", "Inbox", "Life"]


def test_two_real_claims_keep_the_order_they_arrived_in():
    """The later real claim sorts first by id. The rank leaves that pair alone."""
    ordered = _rank([
        _scored("lecture", 0.6),
        _scored("Course", 0.6),
        _scored("Life", 0.8),
        _scored("Inbox", 0.4, already_there=True),
    ])
    assert _ids(ordered) == ["lecture", "Course", "Inbox", "Life"]


def test_the_empty_life_stays_on_the_list():
    ordered = _rank([
        _scored("Life", 1.0),
        _scored("Inbox", 0.6, already_there=True),
    ])
    assert _ids(ordered) == ["Inbox", "Life"]
    assert len(ordered) == 2


def test_two_empty_lives_keep_their_order_below_the_folder():
    ordered = _rank([
        _scored("Life", 1.0),
        _scored("Pile", 0.8),
        _scored("Inbox", 0.4, already_there=True),
    ], empty=frozenset({"Life", "Pile"}))
    assert _ids(ordered) == ["Inbox", "Life", "Pile"]


def test_the_folder_the_file_is_in_is_not_demoted_when_it_expects_nothing():
    ordered = _rank([
        _scored("Life", 0.8),
        _scored("Inbox", 0.4, already_there=True),
    ], empty=frozenset({"Life", "Inbox"}))
    assert _ids(ordered) == ["Inbox", "Life"]


def test_with_no_folder_and_no_child_the_life_stays_where_it_scored():
    ordered = _rank([_scored("Life", 1.0), _scored("Course", 0.6)])
    assert _ids(ordered) == ["Life", "Course"]


def test_an_empty_set_of_ids_leaves_the_order_unchanged():
    arrived = (
        _scored("Life", 1.0),
        _scored("Inbox", 0.6, already_there=True),
    )
    assert _rank(arrived, empty=frozenset()) == arrived


# --- the same order through `assess`, so the tie rules still see it ------------


def _fact():
    return MatchingFact(file_fact_id="ff-1", field="subject", value="note",
                        reliability=v.DIRECT, evidence_ref="obs-1")


def _candidate(node_id, channels):
    return Candidate(
        node_id=node_id, channels=channels,
        matching_facts=(_fact(),) if DIRECT_FACT in channels else (),
        group_ids=("g-1",) if ACCEPTED_GROUP in channels else ())


def _retrieval(*candidates):
    return Retrieval(subject_ref="file:f1:h1", plan_version="plan-1",
                     candidates=tuple(candidates), conflicts=(),
                     semantic_only_node_ids=frozenset(),
                     producible_channels=PRODUCED_CHANNELS)


def _assess(*candidates, empty=EMPTY, refinements=frozenset(),
            theirs=("Inbox",)):
    return assess(
        _retrieval(*candidates), {}, policy=POLICY,
        their_own_folder_node_ids=frozenset(theirs),
        refinements=refinements,
        empty_expectation_node_ids=empty)


def test_assess_ranks_the_empty_life_below_the_folder_and_stays_put():
    result = _assess(
        _candidate("Life", (DIRECT_FACT, ACCEPTED_GROUP)),
        _candidate("Inbox", (DIRECT_FACT, CURATED_FOLDER)))
    assert _ids(result.scored) == ["Inbox", "Life"]
    assert result.stays_put is True
    assert result.abstention_reason is None
    assert result.two_condition.meets_margin == v.MARGIN_TRUE_VACUOUS


def test_assess_ranks_the_empty_life_below_the_child_and_the_child_wins_the_tie():
    result = _assess(
        _candidate("Life", (DIRECT_FACT, ACCEPTED_GROUP)),
        _candidate("Inbox", (DIRECT_FACT, CURATED_FOLDER)),
        _candidate("lecture", (DIRECT_FACT,)),
        refinements=frozenset({"lecture"}))
    assert _ids(result.scored) == ["lecture", "Inbox", "Life"]
    assert result.stays_put is False


def test_assess_leaves_a_proposed_node_that_states_a_value_above_the_folder():
    result = _assess(
        _candidate("Course", (DIRECT_FACT, ACCEPTED_GROUP)),
        _candidate("Life", (DIRECT_FACT,)),
        _candidate("Inbox", (DIRECT_FACT, CURATED_FOLDER)))
    assert _ids(result.scored) == ["Course", "Inbox", "Life"]
    assert result.stays_put is False
    assert result.scored[0].node_id == "Course"


def test_assess_still_stays_put_against_a_real_proposal_when_a_life_scores_higher():
    result = _assess(
        _candidate("Life", (DIRECT_FACT, ACCEPTED_GROUP)),
        _candidate("Course", (DIRECT_FACT,)),
        _candidate("Inbox", (DIRECT_FACT, CURATED_FOLDER)))
    assert result.scored[0].node_id == "Inbox"
    assert result.stays_put is True
    assert result.scored[-1].node_id == "Life"
    assert result.abstention_reason is None


def test_a_tie_between_two_folders_the_person_made_is_still_a_tie():
    result = _assess(
        _candidate("Life", (DIRECT_FACT, ACCEPTED_GROUP)),
        _candidate("Course", (DIRECT_FACT,)),
        _candidate("Inbox", (DIRECT_FACT, CURATED_FOLDER)),
        theirs=("Inbox", "Course"))
    assert result.stays_put is False
    assert result.two_condition.meets_margin == v.MARGIN_FALSE
    assert result.two_condition.margin_over_next == 0.0
    assert result.scored[-1].node_id == "Life"
    assert result.abstention_reason == v.MULTIPLE_SUPPORTED_HOMES


def test_without_the_empty_ids_the_higher_score_still_ranks_first():
    """The rank waits on the caller. An empty set is the old order."""
    result = _assess(
        _candidate("Life", (DIRECT_FACT, ACCEPTED_GROUP)),
        _candidate("Inbox", (DIRECT_FACT, CURATED_FOLDER)),
        empty=frozenset())
    assert result.scored[0].node_id == "Life"
    assert result.stays_put is False
