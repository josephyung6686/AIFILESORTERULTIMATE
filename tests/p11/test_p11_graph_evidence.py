"""`104` §18.2 gap 12 — the node-local typed graph reaching the score and the model.

`00`:109 asks the node-local graph to carry typed relationships, and `00`:110
lists "graph anchor evidence" among the things a placement dossier contains. The
graph was built at §6.12 step 4, read for two flags, written onto the decision --
and never scored, never shown. So a file whose relationship to another file IS the
reason it belongs somewhere was placed as though that relationship did not exist,
and the model could not have cited it if it had wanted to.

Two halves, pinned here. The SCORE: `graph_relationship` gains a producer and the
denominator gains its weight, for a subject that has a typed edge and for no
other. The DOSSIER: one reference-only item per surviving edge, naming the other
file by its accepted facts, gated per file it describes.
"""
from __future__ import annotations

import pytest

from llm_harness.records import EvidenceItem
from placement import vocabulary as v
from placement.graph import build_node_local_graph
from placement.index import entry_for
from placement.pipeline import _with_the_graphs_own_channel
from placement.records import MatchingFact, Subject
from placement.retrieval import (
    ACCEPTED_GROUP, DIRECT_FACT, GRAPH_RELATIONSHIP, PRODUCED_CHANNELS,
    SEMANTIC_NEIGHBOUR, Candidate, Retrieval,
)
from placement.scoring import assess, producible_weight

from p11.test_p11_pipeline import (
    AMBIGUOUS, CLOUD_TARGET, OBS, _asked, _classify, _evidence, _items_of,
    _model_inputs, _place, skeleton,  # noqa: F401  (a fixture, used by name)
)

#: The one file `p10_fixtures.FROZEN_TREE` already lists as `n-course`'s
#: representative, which is what makes an edge to it survive §6.4's community
#: filter. Its own classification is written per test, because whether a
#: NEIGHBOUR may be described is the thing half of these pins measure.
NEIGHBOUR: str = "f-syllabus"
NEIGHBOUR_HASH: str = "h-syllabus"


def _edge(edge_type="version_family", describes="subject = PHYS1401",
          other=NEIGHBOUR, entity="PHYS1401"):
    """One `cli.evidence_for` related-file row, in the shape P11 is handed."""
    return {"edge_type": edge_type, "to_file_id": other,
            "anchor_file_id": other, "weight": 1.0, "entity": entity,
            "to_content_hash": NEIGHBOUR_HASH, "to_describes": describes}


def _graph_evidence(**overrides):
    """`AMBIGUOUS`'s two accepted groups, plus a typed edge into `n-course`."""
    values = dict(AMBIGUOUS)
    values["related_files"] = (_edge(),)
    values["evidence_items"] = (EvidenceItem(
        evidence_ref=OBS, kind="fact", location="page-1", excerpt_span=(0, 8),
        reliability_state="direct", basis="direct-anchor"),)
    values.update(overrides)
    return _evidence(**values)


# --- the score: §6.3's sixth channel, produced at last ---------------------------


def _candidate(node_id="n-course", channels=(DIRECT_FACT,)):
    return Candidate(node_id=node_id, channels=channels,
                     matching_facts=(MatchingFact(
                         file_fact_id="ff1", field="subject", value="PHYS1401",
                         reliability=v.DIRECT, evidence_ref=OBS),),
                     group_ids=())


def _retrieval(candidates, **overrides):
    values = dict(subject_ref="file:f1", plan_version="plan-1",
                  candidates=tuple(candidates), conflicts=(),
                  semantic_only_node_ids=frozenset(),
                  producible_channels=PRODUCED_CHANNELS)
    values.update(overrides)
    return Retrieval(**values)


class _Graph:
    """A `NodeLocalGraph` as `is_typed_support` reads one: entities and hubs."""

    def __init__(self, *, informative=True, anchors=(("shared_validated_fact",),)):
        self.anchors = anchors
        self.distinct_entities = frozenset({"PHYS1401"} if informative else {"x"})
        self.high_frequency_entities = frozenset(() if informative else {"x"})


def test_a_typed_edge_becomes_the_graph_channel_on_the_candidate_it_reaches():
    """§6.3's `graph_relationship`, produced for the first time.

    `00`:107: *"Graph relationships should retrieve nodes containing the group's
    anchor files or related accepted members."* `scoring._CHANNEL_WEIGHT` has
    weighed this channel at 1 since the module was written and nothing put it on
    a candidate, so `retrieval.PRODUCED_CHANNELS` truthfully declared four
    channels and a node whose whole case was a typed relationship scored zero for
    it. Measurement: the candidate whose graph gives typed support carries the
    channel, the one whose graph does not carries nothing new, and the retrieval
    that put it there declares it -- which is the invariant `score_candidates`
    refuses a candidate for breaking.

    SABOTAGE: declare the channel without putting it on a candidate -- the
    denominator rises for a file that cannot reach the numerator, which is gap
    13's defect wearing gap 12's name.
    """
    two = (_candidate(), _candidate(node_id="n-general", channels=(
        SEMANTIC_NEIGHBOUR,)))
    after = _with_the_graphs_own_channel(_retrieval(two), {
        "n-course": _Graph(), "n-general": _Graph(informative=False)})

    by_id = {c.node_id: c.channels for c in after.candidates}
    assert GRAPH_RELATIONSHIP in by_id["n-course"]
    assert GRAPH_RELATIONSHIP not in by_id["n-general"]
    assert GRAPH_RELATIONSHIP in after.producible_channels
    assert producible_weight(after.producible_channels) == 6


def test_a_subject_with_no_typed_edge_is_scored_on_exactly_the_old_scale():
    """`104` §18.2 gap 13 does not reopen, and the arithmetic is why it cannot.

    Declaring `graph_relationship` run-wide would move every file's denominator
    from 5 to 6, and `(3 - 2) / 6 = 0.1667` is under `cli-support-v2`'s 0.20
    margin -- so a file whose direct facts match one node, against a rival
    reached by an accepted group alone, would abstain `low_margin`. That is
    `scoring._exact_margin`'s own worked example and the pair
    `test_a_measured_margin_over_the_threshold_reads_true_not_vacuous` pins. No
    positive weight avoids it: `(3 - 2) / (5 + w) >= 0.20` has no solution for
    `w > 0`.

    So the declaration is the RETRIEVAL's, and a subject with no typed edge gets
    the object it came in with, unchanged and by identity.

    SABOTAGE: put `GRAPH_RELATIONSHIP` in `retrieval.PRODUCED_CHANNELS` -- this
    passes (nothing here reads the constant) and gap 13's headline pin in
    `test_p11_scoring.py` goes red, which is the point of keeping both.
    """
    before = _retrieval((_candidate(),))
    after = _with_the_graphs_own_channel(before, {"n-course": _Graph(
        informative=False)})
    assert after is before
    assert producible_weight(after.producible_channels) == 5


def test_the_graph_channel_carries_a_group_supported_node_over_the_bar():
    """`00`:109's own example, in the arithmetic that used to refuse it.

    *"A sparse file such as HW 3.pdf may not contain PHYS1401 or Spring 2026
    directly, but it can be compared against the PHYS1401 node's syllabus,
    lectures, midterm, accepted problem sets ... If the file ... connects to
    several direct anchors ... the engine can propose the PHYS1401 Homework
    node."* An accepted group alone is 2/6 and does not clear the 0.50 bar; the
    same node with a typed edge to a file already accepted in it is 3/6 and does.
    A typed edge ALONE is 1/6 and still cannot place, which is §6.5's "a target
    file connected only by generic similarity or one high-frequency entity must
    remain uncertain".

    SABOTAGE: raise the channel's weight to the accepted group's 2 -- this still
    passes, and a direct fact alone falls to 3/7 = 0.43, under the same bar. The
    weight is `_CHANNEL_WEIGHT`'s and §3.13's ordering, not a knob.
    """
    from p11.test_p11_pipeline import POLICY

    sparse = _candidate(node_id="n-course", channels=(ACCEPTED_GROUP,))
    edged = _with_the_graphs_own_channel(
        _retrieval((sparse,)), {"n-course": _Graph()})
    scored = assess(edged, {"n-course": _Graph()}, policy=POLICY)
    assert scored.two_condition.support_score == pytest.approx(3 / 6)
    assert scored.two_condition.meets_threshold is True

    alone = _with_the_graphs_own_channel(
        _retrieval((_candidate(node_id="n-course", channels=()),)),
        {"n-course": _Graph()})
    only = assess(alone, {"n-course": _Graph()}, policy=POLICY)
    assert only.two_condition.support_score == pytest.approx(1 / 6)
    assert only.two_condition.meets_threshold is False


def test_an_edge_reaching_only_a_third_folder_turns_a_placement_into_a_question():
    """THE ONE COST OF THE GRAPH CHANNEL, measured rather than argued away.

    Direct fact reaches A, an accepted group reaches B, and the typed edge
    reaches neither -- it reaches C. Before the channel: A = 3/5, B = 2/5, margin
    exactly 0.2, a deterministic placement at A. After: the subject HAS a typed
    edge, so its denominator is 6, A = 3/6, B = 2/6, C = 1/6, and the margin is
    1/6 -- under `cli-support-v2`'s 0.20, so `low_margin`.

    Both readings are true and the owner is owed both. With a model configured
    this is a site-C call with the edge in the dossier, which is `00`:110's own
    trigger ("several legal nodes remain plausible") and the graph is WHY a third
    folder is plausible. With no model configured (§6.6's legal run) it is an
    abstention where there used to be a placement, and the file goes to review.

    The run-wide alternative is worse and `test_a_subject_with_no_typed_edge_...`
    is the pin for it: it does this to every file in the corpus, including the
    ones with no relationship at all. The number that would remove the cost
    entirely is `cli-support-v2`'s margin, and it is the owner's.

    SABOTAGE: assert `MARGIN_TRUE` here -- the assertion passes the day somebody
    declares the channel run-wide, and gap 13's headline pair goes red instead
    with nothing left saying the two are the same trade.
    """
    from p11.test_p11_pipeline import POLICY

    three = (_candidate(node_id="n-a", channels=(DIRECT_FACT,)),
             _candidate(node_id="n-b", channels=(ACCEPTED_GROUP,)),
             _candidate(node_id="n-c", channels=()))
    graphs = {"n-c": _Graph()}
    result = assess(_with_the_graphs_own_channel(_retrieval(three), graphs),
                    graphs, policy=POLICY)

    assert result.two_condition.meets_threshold is True
    assert result.two_condition.margin_over_next == pytest.approx(1 / 6)
    assert result.two_condition.meets_margin == v.MARGIN_FALSE
    assert result.abstention_reason == v.LOW_MARGIN


# --- the dossier: `00`:110's graph anchor evidence -------------------------------


def test_an_edge_to_a_placed_file_reaches_the_dossier_as_a_reference_item(
        skeleton, monkeypatch):
    """`00`:110's "graph anchor evidence", which the dossier never carried.

    A file with a `version_family` edge to `f-syllabus` -- already accepted in
    `n-course`, which is on the shortlist -- gets one item saying so: the
    relationship's type, the other file's accepted facts, the offered folder it
    is accepted in, and what produced the edge. `00`:112's group dossier names a
    member by its accepted facts and this names a neighbour the same way, because
    site C releases no filename (`model_facts.may_be_released` refuses a
    `filename`-zone reading to both localities) and an opaque `file_id` tells a
    model nothing.

    SABOTAGE: drop the `where` clause -- the model learns that the file is
    related to some other file and not that the other file is already accepted in
    a folder it is being asked to choose, which is the whole of `00`:109's
    argument for a NODE-LOCAL graph.
    """
    _classify(skeleton, file_id=NEIGHBOUR, content_hash=NEIGHBOUR_HASH)
    seen = _asked(monkeypatch)
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_graph_evidence())

    edges = _items_of(seen, "graph_edge")
    assert len(edges) == 1
    (location,) = edges.values()
    assert "version family relationship" in location
    assert "subject = PHYS1401" in location
    assert "already accepted in n-course" in location
    assert "the version-family detection" in location


def test_a_graph_item_is_uncitable_exactly_as_an_accepted_group_is(
        skeleton, monkeypatch):
    """Gap 12 item 4: a citation of a graph item resolves like any other
    reference-only item, and P8 gains no check.

    The ratified C text says the rule in its own words -- *"Cite only keys that
    appear in released_evidence: a candidate, a group or a conflict is not
    evidence and cannot be cited"* -- and `validation._check_citation` enforces
    it for anything whose `evidence_ref` is in the items and not in
    `released_evidence`. So the graph item joins `UNCITABLE_ITEM_KINDS` beside
    the folders and the groups, and the evidence snapshot addresses what the
    dossier CITES and not what it carries: a relationship's id in a citation
    record is the same defect as a plan id in one.

    **The owner is owed one sentence of the C text** naming this fourth kind. It
    is written in the report and not applied here; the dossier's own inventory of
    KEYS is unchanged, which is what the text closes.

    SABOTAGE: leave `GRAPH_EDGE_ITEM` out of `UNCITABLE_ITEM_KINDS` -- the
    snapshot id starts moving with a neighbour's relationships, so two dossiers
    over one file's own unchanged evidence stop being recognisable as replays.
    """
    from placement.p8_seam import (
        GRAPH_EDGE_ITEM, UNCITABLE_ITEM_KINDS, snapshot_observation_keys,
    )

    assert GRAPH_EDGE_ITEM in UNCITABLE_ITEM_KINDS
    _classify(skeleton, file_id=NEIGHBOUR, content_hash=NEIGHBOUR_HASH)
    seen = _asked(monkeypatch)
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_graph_evidence())

    (edge_ref,) = _items_of(seen, "graph_edge")
    assert edge_ref not in snapshot_observation_keys(seen["items"])
    # And nothing about it was released, which is what makes the refusal above
    # the same refusal a group gets rather than a second rule.
    released = {item.observation_key
                for item in seen["request"].model_call_request.requested_items}
    assert edge_ref not in released


def test_a_protected_neighbour_is_never_described_to_a_cloud_target(
        skeleton, monkeypatch):
    """The gate is asked per FILE the dossier describes (§8.4, `104` §18.7).

    A graph item describes somebody else's file, so the question "may this file
    be described to this target" is asked about the NEIGHBOUR and against the
    target this call was actually routed to -- the same two lines
    `_one_destination_every_member_may_use` runs per group member. A protected
    file reaches no model on any locality, so it is described to none: the item
    is not written, and the file being placed still gets its call.

    SABOTAGE: ask the subject's own privacy state instead -- the subject is
    ordinary here, every assertion below flips, and a protected file's facts
    cross inside another file's dossier.
    """
    _classify(skeleton, file_id=NEIGHBOUR, content_hash=NEIGHBOUR_HASH,
              protected=True)
    seen = _asked(monkeypatch)
    _place(skeleton, inputs=_model_inputs(
        skeleton, model_target=CLOUD_TARGET,
        route_for=lambda _f: (object(), CLOUD_TARGET)),
        evidence=_graph_evidence())

    assert _items_of(seen, "graph_edge") == {}
    # The CALL still happened: a neighbour that may not be described is not a
    # reason to stop asking about the file in front of the person.
    assert seen["request"].call_site == "C_placement"


def test_a_neighbour_with_nothing_describable_gets_no_item(
        skeleton, monkeypatch):
    """A reference to a file the dossier may not describe is a reference to
    nothing.

    `cli.evidence_for` answers `to_describes = None` for a neighbour whose every
    accepted fact is either not a destination dimension (§3.8) or has no citation
    the door would release under the strictest target. The item is then not
    written at all, rather than written naming an opaque `file_id` the model can
    do nothing with.

    SABOTAGE: fall back to the `file_id` -- the dossier gains an item that says
    a relationship exists to a file it cannot name, which is a `uuid4` crossing
    for no purpose.
    """
    _classify(skeleton, file_id=NEIGHBOUR, content_hash=NEIGHBOUR_HASH)
    seen = _asked(monkeypatch)
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_graph_evidence(related_files=(_edge(describes=None),)))

    assert _items_of(seen, "graph_edge") == {}


def test_one_edge_in_two_neighbourhoods_is_one_item_naming_both_folders(
        skeleton, monkeypatch):
    """One edge, one item, and the folders collected into it.

    An edge survives in every candidate whose approved community it touches, and
    the model does not need the same relationship told twice; what it needs is
    which of the offered folders the other file is already accepted in. Those ids
    are already on `allowed_vocabulary` and already described by a `candidate`
    item, so the item adds a relationship and no new vocabulary.

    SABOTAGE: key the items on `(node_id, edge)` -- the dossier repeats one
    relationship once per candidate and §8.6's byte ceiling pays for it.
    """
    _classify(skeleton, file_id=NEIGHBOUR, content_hash=NEIGHBOUR_HASH)
    seen = _asked(monkeypatch)
    _place(skeleton, inputs=_model_inputs(skeleton),
           evidence=_graph_evidence(related_files=(_edge(), _edge())))

    edges = _items_of(seen, "graph_edge")
    assert len(edges) == 1
    # `p10_fixtures` gives every node the same profile, so `f-syllabus` is a
    # representative of several offered folders and one edge reaches several
    # neighbourhoods. All of them are named, inside the one item.
    (location,) = edges.values()
    named = location.split("already accepted in ")[1].split(" | ")[0]
    assert len(named.split(", ")) >= 2, named
    assert set(named.split(", ")) <= set(seen["allowed"])


def test_the_group_call_declares_no_graph_channel_and_carries_no_edge_item(
        skeleton):
    """`104` §18.2 gap 14's refusal, unchanged by gap 12.

    `build_node_local_graph` refuses a group subject by name -- every
    `GraphAnchor` names the file the edge came FROM, and a group of four files
    has four originating files -- so `_the_groups_own_answer` builds `{}`. Both
    halves of gap 12 read that map: an empty one declares no `graph_relationship`
    (the group's denominator stays 5) and produces no edge item. The MEMBERS
    still get theirs, on their own calls.

    SABOTAGE: pass the first member's `file_id` as the anchor -- the group's
    dossier gains edges belonging to one member and the score gains a channel the
    subject cannot produce, which is a placeholder satisfying a type recorded as
    evidence.
    """
    subject = Subject(kind=v.GROUP, file_id=None, content_hash=None,
                      group_id="g-packet", member_file_ids=("f1", "f2"))
    with pytest.raises((AttributeError, TypeError, ValueError)):
        build_node_local_graph(
            subject=subject,
            candidate=_candidate(), entry=entry_for(
                skeleton, plan_version="plan-1", node_id="n-course"),
            related_files=(_edge(),),
            limits=type("L", (), {"max_candidate_cluster_size": 6,
                                  "max_local_graph_neighborhood": 3})(),
            entity_frequency={}, generic_entity_frequency=200)
    # And the empty map is what the two halves read.
    before = _retrieval((_candidate(),))
    assert _with_the_graphs_own_channel(before, {}) is before
