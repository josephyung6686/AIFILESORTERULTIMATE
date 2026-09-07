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
from grouping.graph import (
    EDGE_TYPE_BY_CHANNEL, LocalEvidenceGraph, anchor_observation_keys,
    anchoring_files, build_graph,
)
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
              evidence_ref="sha256:edge-evidence", bridge_entity=None) -> Neighbor:
    """`bridge_entity` is passed only where the channel genuinely has one.

    It defaults to `None` on purpose: giving every neighbour a bridge entity is
    exactly the conflation that made the group's own basis a hub, and a helper
    that supplied one by default would hide the fix it is here to guard.
    """
    return Neighbor(
        file_id=file_id, content_hash=f"h-{file_id}", channel=channel,
        anchors=anchors, evidence_ref=evidence_ref, detail=detail,
        bridge_entity=bridge_entity,
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
    """Three fields, three meanings. `evidence_ref` is what a later reader
    resolves to prove the edge existed; `bridge_entity_ref` is the named third
    thing the edge runs THROUGH; `detail` is prose describing why the channel
    returned the file. The graph once read `detail` as the entity, which made the
    group's own basis a hub as soon as enough files corroborated it."""
    graph = _build(_hood(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True,
                  evidence_ref="sha256:the-observation",
                  detail="subject=BUSIB 4300"),
        _neighbor("file-b", EXISTING_RELATED_FOLDER, evidence_ref=None,
                  detail="Downloads/Spring", bridge_entity="Downloads/Spring"),
    ))
    anchor = next(e for e in graph.edges if e.to_file_id == "file-a")
    assert anchor.evidence_ref == "sha256:the-observation"
    # The graph records what the CHANNEL named and never reads `detail`. This
    # neighbour names no bridge, so the edge carries none -- and the three fields
    # stay three. (`104` R-59's third finding is that the shared-fact channel now
    # names one; that is a decision in `retrieval`, not a reading here, and the
    # exemption below is what makes it safe.)
    assert anchor.bridge_entity_ref is None

    folder = next(e for e in graph.edges if e.to_file_id == "file-b")
    assert folder.bridge_entity_ref == "Downloads/Spring"
    assert folder.evidence_ref != folder.bridge_entity_ref


def test_a_channel_with_no_evidence_reference_is_addressed_by_the_edge_itself():
    """`compatible-document-type` and `existing-related-folder` cite no observation.
    An edge still has to be resolvable, so its own id is what a `Support` cites."""
    graph = _build(_hood(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True),
        _neighbor("file-b", EXISTING_RELATED_FOLDER, evidence_ref=None,
                  detail="Downloads/Spring", bridge_entity="Downloads/Spring"),
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
            _neighbor(f"file-{n}", EXISTING_RELATED_FOLDER,
                      detail="columbia.edu", bridge_entity="columbia.edu")
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
            _neighbor(f"file-{n}", EXISTING_RELATED_FOLDER,
                      detail="columbia.edu", bridge_entity="columbia.edu")
            for n in range(2)
        ], _neighbor("file-anchor", SHARED_VALIDATED_FACT, anchors=True)),
        limits=_limits(generic_hub_frequency=3),
    )
    assert not any(e.hub_suppressed for e in graph.edges)


# --- the seed's own basis is exempt from its own hub count (`104` R-59) ----------
#
# §4.3's count exists "to find an entity that bridges UNRELATED groups". The value
# a group was seeded on is what makes these files ONE group, so counting it made a
# group suppress every edge it had the moment enough files corroborated it -- which
# is why the shared-fact channel used to record no entity at all. It records one
# now, and the exemption is what keeps the old sentence true.


def test_the_seeds_own_basis_is_never_a_hub_however_many_files_state_it():
    """A group of twenty files that all state `subject = BUSIB 4300` is a group
    with twenty corroborations, not a group held together by a generic entity.
    Before the exemption this suppressed all twenty edges at a ceiling of three."""
    basis = "subject=BUSIB 4300"
    graph = _build(
        _hood(*[
            _neighbor(f"file-{n}", SHARED_VALIDATED_FACT, anchors=True,
                      detail=basis, bridge_entity=basis)
            for n in range(20)
        ]),
        limits=_limits(generic_hub_frequency=3),
    )
    assert len(graph.edges) >= 1
    assert not any(e.hub_suppressed for e in graph.edges)
    assert {e.bridge_entity_ref for e in graph.edges} == {basis}


def test_a_value_that_is_not_the_seeds_basis_is_a_hub_at_the_ceiling():
    """The exemption names ONE value in ONE graph. Another entity bridging at the
    ceiling is suppressed exactly as before, and being a fact rather than a folder
    buys it nothing.

    P9's retrieval cannot PRODUCE this case today: `_shared_fact_neighbors` returns
    files sharing the seed's fact, so the only fact bridge in a seed's graph is the
    seed's own. This is a test of the rule, not of a case the owner's corpus makes,
    and the corpus-wide version of it is P11's `entity_frequency` -- which counts
    every file rather than one neighbourhood, and is where an entity that bridges
    UNRELATED groups can actually be seen (`104` R-59)."""
    graph = _build(
        _hood(
            _neighbor("file-anchor", SHARED_VALIDATED_FACT, anchors=True,
                      detail="subject=BUSIB 4300",
                      bridge_entity="subject=BUSIB 4300"),
            *[
                _neighbor(f"file-{n}", EXISTING_RELATED_FOLDER,
                          detail="authored_by=the university",
                          bridge_entity="authored_by=the university")
                for n in range(3)
            ]),
        limits=_limits(generic_hub_frequency=3),
    )
    suppressed = {e.bridge_entity_ref for e in graph.edges if e.hub_suppressed}
    assert suppressed == {"authored_by=the university"}


def test_a_value_shared_by_three_below_the_ceiling_is_not_a_hub():
    """The lower half of the same rule, on a value that is not the basis."""
    graph = _build(
        _hood(
            _neighbor("file-anchor", SHARED_VALIDATED_FACT, anchors=True,
                      detail="subject=BUSIB 4300",
                      bridge_entity="subject=BUSIB 4300"),
            *[
                _neighbor(f"file-{n}", EXISTING_RELATED_FOLDER,
                          detail="Downloads", bridge_entity="Downloads")
                for n in range(3)
            ]),
        limits=_limits(generic_hub_frequency=9),
    )
    assert not any(e.hub_suppressed for e in graph.edges)


def test_a_seed_with_no_basis_exempts_nothing():
    """A user-created starting point and a structural family carry no field and no
    value, so there is no basis to exempt -- and an exemption of `None` must not
    exempt every edge that names no entity."""
    graph = _build(
        _hood(*[
            _neighbor(f"file-{n}", EXISTING_RELATED_FOLDER,
                      detail="Downloads", bridge_entity="Downloads")
            for n in range(3)
        ], _neighbor("file-anchor", SHARED_VALIDATED_FACT, anchors=True),
              seed=_seed(seed_kind="user-created-starting-point",
                         field_key=None, value=None, reliability_state=None,
                         observation_key=None, basis="the person said so")),
        limits=_limits(generic_hub_frequency=3),
    )
    assert {e.bridge_entity_ref for e in graph.edges if e.hub_suppressed} == {
        "Downloads"}


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


# --- `104` R-97: which file cites what, and it was never asked ---------------------
#
# `AnchorFact` carried ONE observation key for a group of four, so three of the
# four were recorded as citing the first file's observation. The per-file key was
# never missing: `retrieval._shared_fact_neighbors` reads the CANDIDATE's own
# `evidence_refs[0]` and `build_graph` carries it onto the edge. What was missing
# was the read.


def _key(tag: str) -> str:
    """A well-shaped P4 key. `is_observation_key` checks the digest WIDTH, so
    `sha256:edge-evidence` -- the helper's default above -- is not one, and a test
    that used it would be asserting the fallback branch by accident."""
    return "sha256:" + (tag * 64)[:64]


def test_each_anchoring_file_is_paired_with_its_own_observation():
    seed_key, a_key, b_key = _key("a"), _key("b"), _key("c")
    graph = _build(_hood(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True,
                  evidence_ref=a_key),
        _neighbor("file-b", SHARED_VALIDATED_FACT, anchors=True,
                  evidence_ref=b_key),
        seed=_seed(observation_key=seed_key),
    ))
    files = anchoring_files(graph, seed_anchors=True)
    keys = anchor_observation_keys(graph, seed_anchors=True,
                                   seed_observation_key=seed_key)

    assert len(keys) == len(files)
    assert dict(zip(files, keys)) == {
        SEED_FILE: seed_key, "file-a": a_key, "file-b": b_key}
    # Three anchors, three DIFFERENT citations. One key repeated three times is
    # the record R-97 is about.
    assert len(set(keys)) == 3


def test_the_seed_is_answered_from_its_own_seed_and_never_from_an_edge():
    """`build_graph` writes edges FROM the seed, so no edge carries the seed's
    citation and the seed's key has to arrive with the question."""
    graph = _build(_hood(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True,
                  evidence_ref=_key("b")),
        seed=_seed(observation_key=_key("a")),
    ))
    paired = dict(zip(anchoring_files(graph, seed_anchors=True),
                      anchor_observation_keys(graph, seed_anchors=True,
                                              seed_observation_key=_key("a"))))
    assert paired[SEED_FILE] == _key("a")
    assert SEED_FILE not in {edge.to_file_id for edge in graph.edges}


def test_a_seed_that_does_not_anchor_is_not_given_a_citation():
    graph = _build(_hood(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True,
                  evidence_ref=_key("b")),
        seed=_seed(observation_key=_key("a")),
    ))
    assert anchoring_files(graph, seed_anchors=False) == ("file-a",)
    assert anchor_observation_keys(
        graph, seed_anchors=False, seed_observation_key=_key("a")) == (_key("b"),)


def test_an_edge_that_cites_no_observation_answers_none_rather_than_its_own_id():
    """`build_graph` falls back to the edge's own id when a channel cites nothing
    -- "a channel that cites no observation is still addressable" -- and a
    `user_confirmed` anchor genuinely cites nothing. The fallback is an edge
    address, not a P4 handle, and offering it as a citation would send the model
    to an observation that does not exist."""
    graph = _build(_hood(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True,
                  evidence_ref=None),
        seed=_seed(observation_key=_key("a")),
    ))
    paired = dict(zip(anchoring_files(graph, seed_anchors=True),
                      anchor_observation_keys(graph, seed_anchors=True,
                                              seed_observation_key=_key("a"))))
    assert paired["file-a"] is None
    edge = next(e for e in graph.edges if e.to_file_id == "file-a")
    assert edge.evidence_ref == edge.edge_id


def test_the_two_reads_select_the_same_edges_and_stay_the_same_length():
    """One filter, read twice. A suppressed hub edge does not anchor, so it may
    not contribute a key either -- and the two functions share
    `_anchoring_edges` so they cannot disagree about which edges those are."""
    graph = _build(_hood(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True,
                  evidence_ref=_key("b")),
        _neighbor("file-b", MUTUAL_SEMANTIC_RETRIEVAL, evidence_ref=_key("c")),
        seed=_seed(observation_key=_key("a")),
    ))
    for seed_anchors in (True, False):
        files = anchoring_files(graph, seed_anchors=seed_anchors)
        keys = anchor_observation_keys(graph, seed_anchors=seed_anchors,
                                       seed_observation_key=_key("a"))
        assert len(files) == len(keys), seed_anchors
        assert "file-b" not in files, seed_anchors
