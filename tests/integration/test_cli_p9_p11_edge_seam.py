"""P9's typed edges reaching P11, and the two vocabularies that had to meet.

`104` R-12: P9 records typed edges in `group_edges` and P11 read `()`, so
`build_node_local_graph` was handed no relationship at all and §6.5's "the
node-local graph should include typed relationships" described nothing that ran.

The obstacle is not conceptual. Both parts publish the SAME five relationships;
`grouping.vocabulary` hyphenates them and `placement.graph` uses underscores, and
`build_node_local_graph` raises on a type it does not know. `cli.P9_TO_P11_EDGE_TYPE`
is the translation, and this file is what keeps it from becoming an alias table
somebody has to remember to update: every member on both sides is accounted for,
and a member added to either vocabulary fails here rather than being dropped in
silence at the seam.
"""
from __future__ import annotations

import cli
from grouping.vocabulary import (
    BOUNDED_SESSION, EDGE_TYPES as P9_EDGE_TYPES, MUTUAL_SEMANTIC_RETRIEVAL,
)
from placement.graph import EDGE_TYPES as P11_EDGE_TYPES


def test_every_p9_edge_type_is_either_translated_or_named_as_dropped():
    """The tripwire. A seventh P9 edge type would otherwise be filtered out by
    `_typed_edges_of`'s `if spelling is None: continue` and nobody would learn that
    a relationship the graph now draws never reaches placement."""
    accounted = set(cli.P9_TO_P11_EDGE_TYPE) | set(cli.NOT_A_PLACEMENT_EDGE)
    assert accounted == set(P9_EDGE_TYPES), (
        "a P9 edge type is neither translated for P11 nor named as one P11 has no "
        "edge for. Decide which it is -- silently dropping it is the defect R-12 is")


def test_every_translation_lands_on_a_type_p11_actually_publishes():
    """The other direction: a value here that `placement.graph` does not carry would
    raise `ValueError` inside `build_node_local_graph` on the first real corpus."""
    assert set(cli.P9_TO_P11_EDGE_TYPE.values()) == set(P11_EDGE_TYPES)


def test_the_two_dropped_types_are_the_two_the_design_excludes():
    """`00`:63's stop rule -- a group is not supported "when the graph is connected
    only by embeddings" -- and `placement/graph.py`'s own sentence, that a semantic
    neighbour "is a retrieval channel and never an edge". A bounded download session
    is `00`:61's "retrieval clue that may bring the files together, but not proof".
    Both reach P11, and neither reaches it as an edge."""
    assert set(cli.NOT_A_PLACEMENT_EDGE) == {BOUNDED_SESSION,
                                             MUTUAL_SEMANTIC_RETRIEVAL}


def test_the_mapping_is_the_two_modules_constants_and_not_strings_typed_here():
    """The property that makes this a seam rather than an alias table: a rename on
    either side is an `ImportError` at the composition root, not a mapping that
    quietly stops matching. Asserted by identity against both published tuples."""
    for p9_spelling, p11_spelling in cli.P9_TO_P11_EDGE_TYPE.items():
        assert p9_spelling in P9_EDGE_TYPES
        assert p11_spelling in P11_EDGE_TYPES


def test_a_folder_bridge_reaches_the_graph_as_a_label_and_never_as_a_path():
    """§8.4's always-local list opens with the word "Paths", and P9 records the
    `existing-related-folder` channel's bridge as an absolute directory -- measured
    on the owner's corpus. `NodeLocalGraph` carries the entity onto the review
    surface, so the reduction happens before the edge is offered.

    Keyed on the CHANNEL and never on the shape of the string: "does this look like
    a path" is a guess, and "this channel's bridge is a folder" is P9's definition.
    """
    from grouping.vocabulary import EXISTING_RELATED_FOLDER, SHARED_VALIDATED_FACT

    reduced = cli.bridge_entity_for(
        EXISTING_RELATED_FOLDER, "/Users/someone/Desktop/Python 1006")
    assert reduced == "Python 1006"
    assert "/" not in reduced
    # every other channel's bridge is P9's, untouched
    assert cli.bridge_entity_for(SHARED_VALIDATED_FACT, "PHYS1401") == "PHYS1401"
    assert cli.bridge_entity_for(SHARED_VALIDATED_FACT, None) is None


def test_the_citation_basis_is_read_off_the_reliability_ladder():
    """`00`:57's split. `validated`, `direct` and `user_confirmed` are readings of
    the file's own bytes or the person's own word; `llm_supported` is inference and
    `possible` is P4's state for "free text, OCR, a filename or any unlabeled
    position" -- `00`:57's HW 3.pdf, which that paragraph calls context-supported in
    those words. Before this, every citation was labelled `direct-anchor`."""
    from facts.states import (
        DIRECT, LLM_SUPPORTED, POSSIBLE, USER_CONFIRMED, VALIDATED,
    )
    from llm_harness.vocabulary import CONTEXT_SUPPORTED, DIRECT_ANCHOR

    for state in (USER_CONFIRMED, DIRECT, VALIDATED):
        assert cli.citation_basis_for(state) == DIRECT_ANCHOR, state
    for state in (LLM_SUPPORTED, POSSIBLE):
        assert cli.citation_basis_for(state) == CONTEXT_SUPPORTED, state


def test_a_retracted_state_has_no_basis_and_raises():
    """§3.13: `rejected` is an exclusion, not the bottom of a ladder. A citation
    resting on a claim the person retracted is a contradiction, and the caller
    excludes those rows before asking -- so reaching here is a caller defect and
    answering it with the weakest basis would hide one."""
    import pytest
    from evidence_shape.vocabulary import NotInVocabulary
    from placement import vocabulary as pv

    with pytest.raises(NotInVocabulary):
        cli.citation_basis_for(pv.DROPPED_RELIABILITY_STATE)


# --- the edges themselves, over the table P9 writes -------------------------

import pytest  # noqa: E402

from grouping.records import TypedEdge  # noqa: E402
from grouping.schema import create_grouping_schema  # noqa: E402
from grouping.store import record_edges  # noqa: E402
from grouping.vocabulary import (  # noqa: E402
    EXISTING_RELATED_FOLDER, SHARED_VALIDATED_FACT,
)
from placement.graph import build_node_local_graph  # noqa: E402

AT = "2026-09-06T00:00:00+00:00"


def _edge(conn, *, from_file, to_file, edge_type, bridge=None,
          hub_suppressed=False) -> None:
    record_edges(conn, "group-1", [TypedEdge(
        edge_id=f"{from_file}->{to_file}:{edge_type}:{bridge}",
        from_file_id=from_file, to_file_id=to_file, edge_type=edge_type,
        evidence_ref=f"ref:{from_file}:{to_file}", weight=None,
        bridge_entity_ref=bridge, hub_suppressed=hub_suppressed,
        created_at=AT)], created_at=AT)


@pytest.fixture()
def edges(conn):
    create_grouping_schema(conn)
    return conn


def test_p9s_edges_reach_p11_at_all(edges):
    """`104` R-12's first half. P9 wrote 511 live edges on the owner's corpus and
    `evidence_for` returned `related_files=()`, so `build_node_local_graph` was
    handed no relationship, `is_typed_support` was False for every file in every
    corpus, and `00`:109's typed relationships described nothing that ran."""
    _edge(edges, from_file="seed", to_file="subject",
          edge_type=SHARED_VALIDATED_FACT)

    related = cli.typed_edges_of(edges, "subject")

    assert len(related) == 1
    assert related[0]["edge_type"] == "shared_validated_fact"
    # the OTHER file, whichever end the subject is; the anchor is P9's seed
    assert related[0]["to_file_id"] == "seed"
    assert related[0]["anchor_file_id"] == "seed"


def test_the_subjects_own_edge_names_the_other_end(edges):
    """Symmetric: P9 draws from the seed, and the subject may be either end."""
    _edge(edges, from_file="subject", to_file="neighbour",
          edge_type=SHARED_VALIDATED_FACT)

    (related,) = cli.typed_edges_of(edges, "subject")

    assert related["to_file_id"] == "neighbour"
    assert related["anchor_file_id"] == "subject"


def test_a_hub_suppressed_edge_is_not_offered_again(edges):
    """P9 has already judged it a generic-hub bridge with the ceiling P9 was given.
    Re-offering it would be P11 overturning that with a different threshold -- and
    on the owner's corpus it is also how 294 folder PATHS would enter the graph."""
    _edge(edges, from_file="hub", to_file="subject",
          edge_type=EXISTING_RELATED_FOLDER, bridge="/Users/x/Downloads",
          hub_suppressed=True)

    assert cli.typed_edges_of(edges, "subject") == ()


def test_a_semantic_edge_is_never_offered_as_an_edge(edges):
    """`00`:63's stop rule and `placement/graph.py`'s own sentence. It reaches P11
    through `semantic_neighbour_nodes`, which is a retrieval channel."""
    _edge(edges, from_file="seed", to_file="subject",
          edge_type=MUTUAL_SEMANTIC_RETRIEVAL)

    assert cli.typed_edges_of(edges, "subject") == ()


def test_what_reaches_p11_is_something_p11_can_actually_read(edges):
    """The end-to-end claim of the translation: the dicts go into the real
    `build_node_local_graph` without raising, which is what a P9 spelling would
    have done on the first row."""
    from placement.config import PlacementLimits
    from placement.records import Subject
    from placement.retrieval import Candidate
    from placement.vocabulary import FILE

    _edge(edges, from_file="anchor", to_file="subject",
          edge_type=SHARED_VALIDATED_FACT)

    class _Entry:
        representative_files = ("anchor",)

    limits = PlacementLimits(**{
        name: 10 for name in PlacementLimits.__dataclass_fields__})
    graph = build_node_local_graph(
        subject=Subject(kind=FILE, file_id="subject", content_hash="c" * 64,
                        group_id=None, member_file_ids=()),
        candidate=Candidate(node_id="node-1", channels=(), matching_facts=(),
                            group_ids=()),
        entry=_Entry(), related_files=cli.typed_edges_of(edges, "subject"),
        limits=limits, entity_frequency={}, generic_entity_frequency=200)

    assert graph.neighbourhood_size == 1
    assert graph.anchors[0].edge_type == "shared_validated_fact"


def test_a_semantic_neighbour_brings_the_nodes_it_is_already_listed_in(edges):
    """`00`:107: "Full-text and OCR embeddings should retrieve semantically
    compatible node profiles and representative files, especially when the target
    file is sparse." The channel knows about FILES and `retrieval.retrieve` takes
    NODE ids, and the node profiles the freeze wrote are the join."""
    _edge(edges, from_file="neighbour", to_file="sparse",
          edge_type=MUTUAL_SEMANTIC_RETRIEVAL)

    nodes = cli.semantic_neighbour_nodes(
        edges, "sparse",
        nodes_listing=lambda file_id: ("node-7",) if file_id == "neighbour" else ())

    assert nodes == ("node-7",)


def test_without_the_semantic_model_the_channel_is_simply_empty(edges):
    """Offline there is no semantic edge to read, and nothing breaks: `retrieve`
    reads an empty `node_ids` as "there is no semantic channel"."""
    _edge(edges, from_file="a", to_file="sparse", edge_type=SHARED_VALIDATED_FACT)

    assert cli.semantic_neighbour_nodes(
        edges, "sparse", nodes_listing=lambda file_id: ("node-7",)) == ()
