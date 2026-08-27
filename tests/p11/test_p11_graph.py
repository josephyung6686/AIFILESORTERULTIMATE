"""§6.4/§6.5 — a graph local to one node, with typed edges and no reclustering."""
from __future__ import annotations

import dataclasses

import pytest

from placement import vocabulary as v
from placement.config import PlacementLimits
from placement.graph import (
    EDGE_TYPES, WholeCorpusReclusteringRefused, build_node_local_graph,
    is_typed_support,
)
from placement.index import build_destination_index, entry_for
from placement.records import MatchingFact, Subject
from placement.retrieval import Candidate, DIRECT_FACT, SEMANTIC_NEIGHBOUR
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE

LIMITS = PlacementLimits(
    max_retrieved_neighbors=4, max_local_graph_neighborhood=3,
    max_candidate_cluster_size=6, max_residual_files_per_batch=50,
    max_dossier_tokens=4000, max_llm_calls_per_thousand_files=100,
    max_cost_per_scan=5,
)
SUBJECT = Subject(kind=v.FILE, file_id="f1", content_hash="h1",
                  group_id=None, member_file_ids=())


@pytest.fixture()
def entry(p11_conn):
    build_destination_index(p11_conn, FROZEN_TREE,
                            component_version="P11-test", observed_at=FIXED_CLOCK)
    return entry_for(p11_conn, plan_version="plan-1", node_id="n-course")


def _related(edge_type="shared_validated_fact", other="f-syllabus",
             entity="PHYS1401", weight=1):
    return {"edge_type": edge_type, "to_file_id": other, "entity": entity,
            "anchor_file_id": other, "weight": weight}


def _candidate(channels=(DIRECT_FACT,)):
    return Candidate(node_id="n-course", channels=channels,
                     matching_facts=(MatchingFact(
                         file_fact_id="ff1", field="subject", value="PHYS1401",
                         reliability=v.DIRECT, evidence_ref="obs-1"),),
                     group_ids=("g-phys1401",))


def _build(entry, **overrides):
    values = dict(
        subject=SUBJECT, candidate=_candidate(), entry=entry,
        related_files=(_related(),), limits=LIMITS,
        entity_frequency={"PHYS1401": 6}, generic_entity_frequency=200,
    )
    values.update(overrides)
    return build_node_local_graph(**values)


def test_the_five_edge_types_are_typed_and_closed():
    assert set(EDGE_TYPES) == {
        "shared_validated_fact", "duplicate", "version_family",
        "compatible_document_type", "existing_related_folder",
    }
    with pytest.raises(ValueError):
        build_node_local_graph(
            subject=SUBJECT, candidate=_candidate(), entry=None,
            related_files=(_related(edge_type="vibes"),), limits=LIMITS,
            entity_frequency={}, generic_entity_frequency=200)


def test_the_graph_only_ever_names_files_related_to_this_one_node(entry):
    # §6.4: compare the target against the node's approved COMMUNITY. A file that
    # is in neither the node's representatives nor the subject's relations is not
    # in the neighbourhood, so whole-corpus reclustering has no entry point.
    graph = _build(entry, related_files=(_related(), _related(other="f-stranger",
                                                             entity="PHYS9999")))
    assert graph.node_id == "n-course"
    assert {a.anchor_file_id for a in graph.anchors} == {"f-syllabus"}
    # And the stranger's entity never reaches the support judgement either: an
    # edge dropped from the anchors but counted in the entities would let a file
    # outside the community carry the "two independent entities" bar.
    assert graph.distinct_entities == frozenset({"PHYS1401"})


def test_a_node_with_no_approved_community_anchors_nothing(entry):
    # §6.4 compares the target against the node's approved COMMUNITY. A node that
    # has none has nothing to compare against, so the honest answer is no anchors
    # -- not every related file the caller happened to hand over, which is the
    # reclustering §6.5 forbids arriving through the back door.
    bare = dataclasses.replace(entry, representative_files=())
    graph = _build(bare)
    assert graph.anchors == ()
    assert is_typed_support(graph) is False


def test_a_neighbourhood_over_its_ceiling_reduces_to_the_strongest(entry):
    # §8.6: reduce BEFORE the dossier is built, not by truncating it afterwards.
    related = tuple(_related(other=f"f-{i}", weight=i) for i in range(1, 8))
    wide = dataclasses.replace(
        entry, representative_files=tuple(f"f-{i}" for i in range(1, 8)))
    graph = _build(wide, related_files=related)
    assert graph.neighbourhood_size == LIMITS.max_local_graph_neighborhood
    assert graph.reduced_to_strongest is True
    assert [a.anchor_file_id for a in graph.anchors] == ["f-7", "f-6", "f-5"]


def test_a_neighbourhood_inside_its_ceiling_says_it_was_not_reduced(entry):
    # The flag means what it says in both directions. A `reduced_to_strongest`
    # that were always true would tell a reviewer nothing, and §8.6 renders a
    # bounded neighbourhood differently from a complete one.
    graph = _build(entry)
    assert graph.reduced_to_strongest is False
    assert graph.neighbourhood_size == 1


def test_one_high_frequency_entity_is_not_typed_support(entry):
    # §6.5: "a file connected only by ... one high-frequency entity stays
    # uncertain". The frequency is injected; P11 chooses no cut-off.
    graph = _build(entry, entity_frequency={"PHYS1401": 900},
                   generic_entity_frequency=200)
    assert graph.high_frequency_entities == frozenset({"PHYS1401"})
    assert is_typed_support(graph) is False


def test_two_independent_entities_are_typed_support(entry):
    # Both files are in the node's approved community, and they are connected by
    # two DIFFERENT entities, so neither is carrying the other.
    wide = dataclasses.replace(entry,
                               representative_files=("f-syllabus", "f-lab"))
    graph = _build(wide,
                   related_files=(_related(),
                                  _related(other="f-lab", entity="Fall 2026")),
                   entity_frequency={"PHYS1401": 6, "Fall 2026": 4})
    assert len(graph.distinct_entities) == 2
    assert is_typed_support(graph) is True


def test_a_semantic_only_candidate_produces_no_anchors_at_all(entry):
    # An embedding is not a typed relationship, so it contributes no edge and the
    # graph reports honestly that there is nothing to compare against.
    graph = _build(entry, candidate=_candidate(channels=(SEMANTIC_NEIGHBOUR,)),
                   related_files=())
    assert graph.anchors == ()
    assert is_typed_support(graph) is False


def test_the_graph_refuses_a_neighbourhood_that_spans_two_nodes(entry):
    with pytest.raises(WholeCorpusReclusteringRefused):
        _build(entry, related_files=(_related(),
                                     _related(other="f-other", entity="X")),
               foreign_node_ids=("n-course-alt",))
