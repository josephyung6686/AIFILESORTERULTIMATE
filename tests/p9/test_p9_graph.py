# tests/p9/test_p9_graph.py
"""P9 Task 7 — typed edges over a bounded neighbourhood, with hubs suppressed.

Retrieval publishes six CHANNELS; the graph publishes seven EDGE TYPES, because
`duplicate-or-version-link` is one way of finding a neighbour and a `duplicate` is
not a `version-family`. Which of the two an edge is, is not something P9 can read
off a channel name, so the discriminator is injected: absent means the channel is
omitted, never guessed.

An edge stores its evidence reference and its bridge entity SEPARATELY. The
evidence reference is what a later reader resolves to prove the edge existed; the
bridge entity is what the edge runs THROUGH, and it is the thing §4.3 suppresses
when it turns out to be a generic hub.

The cap is applied by retaining direct anchors first. Dropping an anchor to keep a
semantic edge would leave a graph that reads as connected while the evidence that
made it a group is gone.
"""
from __future__ import annotations

import pytest

from grouping.config import ConfigurationRequired, GroupingLimits
from grouping.graph import EDGE_TYPE_BY_CHANNEL, LocalEvidenceGraph, build_graph
from grouping.retrieval import Neighbor, Neighborhood
from grouping.seeds import Seed
from grouping.vocabulary import (
    BOUNDED_SESSION,
    COMPATIBLE_DOCUMENT_TYPE,
    DUPLICATE,
    DUPLICATE_OR_VERSION_LINK,
    EDGE_TYPES,
    EXISTING_RELATED_FOLDER,
    MUTUAL_SEMANTIC_RETRIEVAL,
    SHARED_VALIDATED_FACT,
    STRONGLY_IDENTIFIED_FILE,
    VERSION_FAMILY,
)

T0 = "2026-08-27T00:00:00Z"
SEED_FILE = "file-seed"


def _limits(**overrides) -> GroupingLimits:
    values = dict(
        max_retrieved_neighbors=50,
        max_graph_nodes=10,
        max_candidate_members=10,
        max_dossier_tokens=4000,
        generic_hub_frequency=3,
        minimum_independent_anchors=1, max_excerpt_characters=240,
    )
    values.update(overrides)
    return GroupingLimits(**values)


def _seed(**overrides) -> Seed:
    values = dict(
        seed_kind=STRONGLY_IDENTIFIED_FILE,
        file_id=SEED_FILE,
        content_hash="h-seed",
        field_key="subject",
        value="BUSIB 4300",
        reliability_state="validated",
        observation_key="sha256:seed-fact",
        basis=None,
    )
    values.update(overrides)
    return Seed(**values)


def _neighbor(file_id, channel, *, anchors=False, detail="subject=BUSIB 4300",
              evidence_ref="sha256:edge-evidence") -> Neighbor:
    return Neighbor(
        file_id=file_id, content_hash=f"h-{file_id}", channel=channel,
        anchors=anchors, evidence_ref=evidence_ref, detail=detail,
    )


def _hood(*neighbors, seed=None) -> Neighborhood:
    return Neighborhood(seed=seed or _seed(), neighbors=tuple(neighbors))


def _build(neighborhood=None, **overrides):
    values = dict(
        group_id="group-1",
        neighborhood=neighborhood if neighborhood is not None else _hood(
            _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True)),
        limits=_limits(),
        duplicate_or_version=lambda a, b: DUPLICATE,
        created_at=T0,
    )
    values.update(overrides)
    return build_graph(**values)


# --- the channel-to-edge-type map is total, and one entry needs an authority ----


def test_every_edge_type_is_reachable_and_no_channel_is_unmapped():
    from grouping.vocabulary import SUPPORT_KINDS

    assert set(EDGE_TYPE_BY_CHANNEL) == set(SUPPORT_KINDS) - {
        DUPLICATE_OR_VERSION_LINK,
    }
    assert set(EDGE_TYPE_BY_CHANNEL.values()) | {DUPLICATE, VERSION_FAMILY} == set(
        EDGE_TYPES)


@pytest.mark.parametrize("verdict", [DUPLICATE, VERSION_FAMILY])
def test_the_duplicate_or_version_split_comes_from_the_injected_authority(verdict):
    graph = _build(
        _hood(
            _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True),
            _neighbor("file-b", DUPLICATE_OR_VERSION_LINK),
        ),
        duplicate_or_version=lambda a, b: verdict,
    )
    kinds = {edge.to_file_id: edge.edge_type for edge in graph.edges}
    assert kinds["file-b"] == verdict


def test_a_duplicate_channel_with_no_authority_is_configuration_required():
    """P9 cannot read a duplicate off a channel name, and a wrong answer here puts
    two revisions of one document into a group as two documents."""
    with pytest.raises(ConfigurationRequired):
        _build(
            _hood(
                _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True),
                _neighbor("file-b", DUPLICATE_OR_VERSION_LINK),
            ),
            duplicate_or_version=None,
        )


def test_an_authority_returning_a_value_outside_the_two_is_refused():
    with pytest.raises(ConfigurationRequired):
        _build(
            _hood(
                _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True),
                _neighbor("file-b", DUPLICATE_OR_VERSION_LINK),
            ),
            duplicate_or_version=lambda a, b: "near-duplicate",
        )


# --- evidence reference and bridge entity are two fields -------------------------


def test_the_edge_stores_its_evidence_and_its_bridge_entity_separately():
    graph = _build(_hood(_neighbor(
        "file-a", SHARED_VALIDATED_FACT, anchors=True,
        evidence_ref="sha256:the-observation", detail="subject=BUSIB 4300")))
    edge = graph.edges[0]
    assert edge.evidence_ref == "sha256:the-observation"
    assert edge.bridge_entity_ref == "subject=BUSIB 4300"
    assert edge.evidence_ref != edge.bridge_entity_ref


def test_a_channel_with_no_evidence_reference_is_addressed_by_the_edge_itself():
    """`compatible-document-type` and `existing-related-folder` cite no observation.
    An edge still has to be resolvable, so its own id is what a `Support` cites."""
    graph = _build(_hood(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True),
        _neighbor("file-b", EXISTING_RELATED_FOLDER,
                  evidence_ref=None, detail="Downloads/Spring"),
    ))
    folder_edge = next(e for e in graph.edges if e.to_file_id == "file-b")
    assert folder_edge.evidence_ref == folder_edge.edge_id
    assert folder_edge.bridge_entity_ref == "Downloads/Spring"


def test_edge_ids_are_stable_across_two_builds_of_the_same_neighbourhood():
    """A replay that re-derives the graph must produce the same edge ids, or a
    `Support.edge_ref` recorded yesterday resolves to nothing today."""
    hood = _hood(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True),
        _neighbor("file-b", BOUNDED_SESSION),
    )
    first = _build(hood)
    second = _build(hood)
    assert [e.edge_id for e in first.edges] == [e.edge_id for e in second.edges]


def test_no_edge_runs_from_the_seed_to_itself():
    graph = _build(_hood(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True),
        _neighbor(SEED_FILE, COMPATIBLE_DOCUMENT_TYPE),
    ))
    assert all(e.from_file_id != e.to_file_id for e in graph.edges)
    assert SEED_FILE not in {e.to_file_id for e in graph.edges}


# --- generic-hub suppression -----------------------------------------------------


def test_an_entity_bridging_at_or_above_the_frequency_is_suppressed():
    """§4.3: a personal email address or a broad university domain bridges half the
    corpus and means nothing. The threshold is injected; P9 embeds no heuristic."""
    graph = _build(
        _hood(*[
            _neighbor(f"file-{n}", COMPATIBLE_DOCUMENT_TYPE, detail="columbia.edu")
            for n in range(3)
        ], _neighbor("file-anchor", SHARED_VALIDATED_FACT, anchors=True)),
        limits=_limits(generic_hub_frequency=3),
    )
    hub_edges = [e for e in graph.edges if e.bridge_entity_ref == "columbia.edu"]
    assert len(hub_edges) == 3
    assert all(e.hub_suppressed for e in hub_edges)
    assert not any(
        e.hub_suppressed for e in graph.edges
        if e.bridge_entity_ref != "columbia.edu")


def test_an_entity_below_the_frequency_is_not_suppressed():
    graph = _build(
        _hood(*[
            _neighbor(f"file-{n}", COMPATIBLE_DOCUMENT_TYPE, detail="columbia.edu")
            for n in range(2)
        ], _neighbor("file-anchor", SHARED_VALIDATED_FACT, anchors=True)),
        limits=_limits(generic_hub_frequency=3),
    )
    assert not any(e.hub_suppressed for e in graph.edges)


def test_no_generic_hub_literal_is_written_into_p9():
    """The rule is a frequency, not a list of domains. A hard-coded `.edu` or a
    mail provider would be P9 authoring a policy that belongs to configuration,
    tuned on a corpus that is not this user's."""
    import ast
    import pathlib
    import re

    import grouping.graph as module

    domainish = re.compile(r"@|\b[a-z0-9-]+\.(com|edu|org|net|co\.uk)\b")
    offenders = []
    tree = ast.parse(pathlib.Path(module.__file__).read_text())
    docstrings = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in docstrings and domainish.search(node.value)):
            offenders.append(f"{node.lineno}:{node.value!r}")
    assert offenders == [], offenders


# --- the cap keeps anchors ------------------------------------------------------


def test_the_cap_retains_direct_anchors_before_any_other_edge():
    graph = _build(
        _hood(
            *[_neighbor(f"weak-{n}", MUTUAL_SEMANTIC_RETRIEVAL, detail=f"sem-{n}")
              for n in range(6)],
            _neighbor("anchor-1", SHARED_VALIDATED_FACT, anchors=True),
            _neighbor("anchor-2", SHARED_VALIDATED_FACT, anchors=True),
        ),
        limits=_limits(max_graph_nodes=3),
    )
    kept = {e.to_file_id for e in graph.edges}
    assert {"anchor-1", "anchor-2"} <= kept
    assert len(graph.file_ids) == 3
    assert graph.capped is True
    assert graph.omissions


def test_an_uncapped_graph_says_so_and_omits_nothing():
    graph = _build(_hood(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True),
        _neighbor("file-b", BOUNDED_SESSION),
    ), limits=_limits(max_graph_nodes=10))
    assert graph.capped is False
    assert graph.omissions == ()


def test_the_graph_is_a_frozen_record_with_no_setter():
    import dataclasses

    graph = _build()
    assert isinstance(graph, LocalEvidenceGraph)
    assert graph.__dataclass_params__.frozen
    with pytest.raises(dataclasses.FrozenInstanceError):
        graph.capped = True  # type: ignore[misc]
