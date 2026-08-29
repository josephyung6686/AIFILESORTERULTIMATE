"""§6.3 — six channels drive retrieval and conflicting evidence suppresses."""
from __future__ import annotations

import dataclasses

import pytest

from placement import vocabulary as v
from placement.config import PlacementLimits
from placement.index import build_destination_index
from placement.records import MatchingFact, Subject
from placement.retrieval import CHANNELS, retrieve
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE, ExpectedValue, tree_with

LIMITS = PlacementLimits(
    max_retrieved_neighbors=4, max_local_graph_neighborhood=8,
    max_candidate_cluster_size=6, max_residual_files_per_batch=50,
    max_dossier_tokens=4000, max_llm_calls_per_thousand_files=100,
    max_cost_per_scan=5,
)
SUBJECT = Subject(kind=v.FILE, file_id="f1", content_hash="h1",
                  group_id=None, member_file_ids=())


def _fact(field="subject", value="PHYS1401", reliability=v.DIRECT, ref="obs-1"):
    return MatchingFact(file_fact_id=f"ff-{field}-{value}", field=field,
                        value=value, reliability=reliability, evidence_ref=ref)


def _retrieve(conn, **overrides):
    values = dict(
        subject=SUBJECT, plan_version="plan-1", limits=LIMITS,
        facts=(_fact(),), group_ids=(), curated_folder_labels=(),
        semantic_neighbours=(), component_version="P11-test",
        observed_at=FIXED_CLOCK,
    )
    values.update(overrides)
    return retrieve(conn, **values)


@pytest.fixture()
def indexed(p11_conn):
    build_destination_index(p11_conn, FROZEN_TREE,
                            component_version="P11-test", observed_at=FIXED_CLOCK)
    return p11_conn


@pytest.fixture()
def indexed_with_an_ineligible_dimension(p11_conn):
    """A tree carrying a node whose expected value is on a field §3.8 excludes.

    It lives here rather than in `p10_fixtures` because it exists to prove ONE
    §6.3 rule and would change every other module's index. Without a node that
    expects an ineligible field, "an ineligible fact drives nothing" is true
    whatever `_eligible_facts` does, and the assertion proves nothing.

    `instructor` is P6's own `destination_eligible = False` (`facts/fields.py`:
    §3.11's Academic template is school -> term -> course -> work type, and §3.8
    disfavours person-identity collectors). Every record below is P10's own,
    reached by `dataclasses.replace` on the shipped fixture rather than rebuilt.
    """
    origin = FROZEN_TREE.nodes[0]
    node = dataclasses.replace(
        origin, node_id="n-instructor", origin_node_id="n-instructor",
        display_label="Dr. Ives", ordinal=4, associated_group_ids=(),
        dimension="instructor", dimension_role="instructor",
        expected_values=(ExpectedValue(field="instructor", value="Dr. Ives"),),
        explanation="Four files name instructor = Dr. Ives.",
    )
    profile = dataclasses.replace(
        FROZEN_TREE.profiles[0], node_id=node.node_id,
        display_label=node.display_label, expected_values=node.expected_values,
        accepted_group_ids=(), group_labels=(), anchor_excerpts=(),
    )
    nodes = FROZEN_TREE.nodes + (node,)
    tree = tree_with(
        nodes=nodes, profiles=FROZEN_TREE.profiles + (profile,),
        freeze_record=dataclasses.replace(
            FROZEN_TREE.freeze_record,
            node_ids=tuple(n.node_id for n in nodes),
            legal_destination_ids=frozenset(
                n.node_id for n in nodes if n.accepts_placement)),
    )
    build_destination_index(p11_conn, tree, component_version="P11-test",
                            observed_at=FIXED_CLOCK)
    return p11_conn


def test_the_six_channels_are_63s_own_list():
    assert len(CHANNELS) == 6
    assert set(CHANNELS) == {
        "direct_fact", "accepted_group", "graph_relationship",
        "structural_relationship", "semantic_neighbour", "curated_folder",
    }


def test_a_direct_fact_retrieves_the_node_whose_expected_value_it_matches(indexed):
    result = _retrieve(indexed)
    assert [c.node_id for c in result.candidates] == ["n-course"]
    assert result.candidates[0].channels == ("direct_fact",)


def test_a_conflicting_direct_fact_suppresses_and_the_suppression_is_recorded(indexed):
    # Done-means 4: a direct `subject = PHYS1402` does not retrieve the PHYS1401
    # node as a top candidate, and the review surface can show why not.
    result = _retrieve(indexed, facts=(_fact(value="PHYS1402", ref="obs-2"),))
    assert [c.node_id for c in result.candidates] == ["n-course-alt"]
    suppressed = {n for conflict in result.conflicts
                  for n in conflict.suppressed_node_ids}
    assert "n-course" in suppressed
    assert result.conflicts[0].conflicting_value == "PHYS1402"
    assert result.conflicts[0].evidence_ref == "obs-2"


def test_an_ignored_node_never_appears_even_as_a_suppressed_candidate(indexed):
    # It is not in the index at all, so §5.10's guarantee needs no second rule.
    result = _retrieve(indexed, curated_folder_labels=("Old Downloads",))
    assert "n-ignored" not in {c.node_id for c in result.candidates}
    assert "n-ignored" not in {n for conflict in result.conflicts
                               for n in conflict.suppressed_node_ids}


def test_a_semantic_only_neighbour_is_retrieved_and_marked_as_such(indexed):
    # §6.5: it may improve recall; it may never be the sole support. Marking it
    # here keeps it visible to review; dropping it would hide that it was
    # considered.
    result = _retrieve(indexed, facts=(), semantic_neighbours=("n-course",))
    assert [c.node_id for c in result.candidates] == ["n-course"]
    assert result.semantic_only_node_ids == frozenset({"n-course"})


def test_a_contradicted_node_is_suppressed_even_when_another_channel_reaches_it(indexed):
    # This is the whole purchase of §6.3's word "actively". A node the subject's
    # own direct fact rules out must not come back through the accepted-group
    # door: `n-course-alt` expects `subject = PHYS1402`, the subject holds
    # PHYS1401, and it is a member of `g-phys1402`. Without the suppression the
    # group channel alone would make it a candidate the user has to argue with.
    result = _retrieve(indexed, group_ids=("g-phys1402",))
    assert [c.node_id for c in result.candidates] == ["n-course"]
    assert result.conflicts[0].suppressed_node_ids == ("n-course-alt",)
    assert result.conflicts[0].conflicting_value == "PHYS1401"


def test_a_fact_on_a_field_that_is_not_destination_eligible_drives_nothing(
        indexed_with_an_ineligible_dimension):
    # §3.8: authorship and creator identity are not destination dimensions, and
    # P6 already publishes the answer, so P11 asks rather than deciding.
    #
    # `n-instructor` expects exactly this field and value, so the fact WOULD
    # retrieve it if `_eligible_facts` let it through -- which is what makes the
    # empty result evidence of the filter rather than of an absent node.
    conn = indexed_with_an_ineligible_dimension
    result = _retrieve(conn, facts=(_fact(field="instructor", value="Dr. Ives"),))
    assert result.candidates == ()
    # And it cannot suppress either: an ineligible field is not a destination
    # dimension in EITHER direction, so disagreeing with one is not a conflict.
    other = _retrieve(conn, facts=(_fact(field="instructor", value="Dr. Nam"),))
    assert other.candidates == ()
    assert other.conflicts == ()
    # §3.8's own headline field, on a node that expects nothing of it.
    assert _retrieve(conn, facts=(_fact(field="authored_by", value="J. Yung"),)
                     ).candidates == ()


def test_retrieval_is_bounded_and_the_cut_keeps_the_strongest_channel(indexed):
    # §8.6 bounds the neighbourhood, so the CUT decides what the user ever sees.
    # `n-academics` sorts before `n-course` by node id and is reached only by a
    # curated folder label; `n-course` is reached by a direct fact. A cut that
    # took insertion order -- which `entries_for_plan` has already sorted by node
    # id -- would keep the weaker one and silently drop the fact match, which is
    # why the ordering is by channel strength first and node id only to break a
    # genuine tie.
    limits = dataclasses.replace(LIMITS, max_retrieved_neighbors=1)
    result = _retrieve(indexed, limits=limits, curated_folder_labels=("Academics",))
    assert [c.node_id for c in result.candidates] == ["n-course"]


def test_the_tie_break_is_stable_across_input_order(indexed):
    limits = dataclasses.replace(LIMITS, max_retrieved_neighbors=1)
    result = _retrieve(indexed, facts=(), limits=limits,
                       semantic_neighbours=("n-course-alt", "n-course"))
    assert len(result.candidates) == 1
    again = _retrieve(indexed, facts=(), limits=limits,
                      semantic_neighbours=("n-course", "n-course-alt"))
    assert [c.node_id for c in result.candidates] == [c.node_id for c in again.candidates]


def test_retrieval_appends_its_event_with_both_lists(indexed):
    _retrieve(indexed, facts=(_fact(value="PHYS1402", ref="obs-2"),))
    row = indexed.execute(
        "SELECT explanation FROM events WHERE event_type = ? "
        "ORDER BY event_id DESC LIMIT 1", (v.CANDIDATE_RETRIEVAL,)).fetchone()
    assert "n-course-alt" in row["explanation"]
    assert "n-course" in row["explanation"]
