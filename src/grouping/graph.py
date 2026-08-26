# src/grouping/graph.py
"""The bounded local evidence graph, and the stop rules that run before a model.

Retrieval publishes six CHANNELS; the graph publishes seven EDGE TYPES, because
`duplicate-or-version-link` is one way of finding a neighbour and a `duplicate` is
not a `version-family`. Which of the two an edge is cannot be read off a channel
name, so the discriminator is injected — absent means the channel is omitted, and
never guessed. Getting it wrong puts two revisions of one document into a group as
two documents, or two different documents into one version family.

An edge stores its evidence reference and its bridge entity separately. The
evidence reference is what a later reader resolves to prove the edge existed; the
bridge entity is what the edge runs THROUGH, and it is the thing §4.3 suppresses
once it turns out to bridge half the corpus.

Five of the six stop rules run here, before a dossier is assembled and before a
model is called. SR5 is not one of them: it means P8 could not explain the group
with valid citations, which is only knowable after `run_call` returns.
"""
from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from database_agent.learning import learning_records

from grouping.config import ConfigurationRequired, GroupingLimits
from grouping.records import Conflict, StopRuleOutcome, TypedEdge
from grouping.retrieval import Neighborhood
from grouping.vocabulary import (
    BOUNDED_SESSION,
    COMPATIBLE_DOCUMENT_TYPE,
    DUPLICATE,
    DUPLICATE_OR_VERSION_LINK,
    EXISTING_RELATED_FOLDER,
    GROUP_PROPOSAL_CLASS,
    MUTUAL_SEMANTIC_RETRIEVAL,
    NO_GROUP,
    SHARED_VALIDATED_FACT,
    SR1,
    SR2,
    SR3,
    SR4,
    SR5,
    SR6,
    TENTATIVE_DISCOVERY,
    VERSION_FAMILY,
)

#: Five channels name their edge type directly. The sixth does not, and that is
#: the whole reason `duplicate_or_version` is an injected authority.
EDGE_TYPE_BY_CHANNEL: Mapping[str, str] = {
    SHARED_VALIDATED_FACT: SHARED_VALIDATED_FACT,
    COMPATIBLE_DOCUMENT_TYPE: COMPATIBLE_DOCUMENT_TYPE,
    EXISTING_RELATED_FOLDER: EXISTING_RELATED_FOLDER,
    BOUNDED_SESSION: BOUNDED_SESSION,
    MUTUAL_SEMANTIC_RETRIEVAL: MUTUAL_SEMANTIC_RETRIEVAL,
}

DuplicateOrVersion = Callable[[str, str], str]


@dataclass(frozen=True)
class LocalEvidenceGraph:
    """The bounded neighbourhood as a graph.

    `file_ids` and not `nodes`: a graph node here is a file version, and a P10
    node is a destination in the tree. One word for two concepts, and P9 must
    never name the second -- so it does not name it at all.
    """

    group_id: str
    seed_file_id: str
    file_ids: tuple[str, ...]
    edges: tuple[TypedEdge, ...]
    capped: bool
    omissions: tuple[str, ...]


def _edge_id(group_id: str, from_file: str, to_file: str, edge_type: str,
             bridge: str | None) -> str:
    """A stable address for one edge.

    A replay re-derives the graph, and a `Support.edge_ref` recorded yesterday has
    to resolve to the same edge today. A uuid would make every replay a different
    graph over the same evidence.
    """
    body = "\x1f".join(
        (group_id, from_file, to_file, edge_type, bridge or ""),
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _edge_type(neighbor, duplicate_or_version: DuplicateOrVersion | None,
               seed_file_id: str) -> str:
    if neighbor.channel != DUPLICATE_OR_VERSION_LINK:
        return EDGE_TYPE_BY_CHANNEL[neighbor.channel]
    if duplicate_or_version is None:
        raise ConfigurationRequired(
            "a duplicate-or-version-link edge is either a duplicate or a version "
            "family, and P9 cannot tell which from the channel. Without the "
            "authority the channel is omitted, never guessed: the wrong answer "
            "puts two revisions of one document into a group as two documents."
        )
    verdict = duplicate_or_version(seed_file_id, neighbor.file_id)
    if verdict not in (DUPLICATE, VERSION_FAMILY):
        raise ConfigurationRequired(
            f"duplicate_or_version returned {verdict!r}; the two legal answers are "
            f"{DUPLICATE!r} and {VERSION_FAMILY!r}"
        )
    return verdict


def _hub_entities(edges: Sequence[TypedEdge], frequency: int) -> frozenset[str]:
    """Entities bridging at or above the injected frequency.

    The rule is a count, not a list of domains. A hard-coded university suffix or
    mail provider here would be P9 authoring a policy that belongs to
    configuration, and the corpus it was tuned on is not this user's.
    """
    counts: dict[str, int] = {}
    for edge in edges:
        if edge.bridge_entity_ref is None:
            continue
        counts[edge.bridge_entity_ref] = counts.get(edge.bridge_entity_ref, 0) + 1
    return frozenset(
        entity for entity, count in counts.items() if count >= frequency
    )


def _rank(edge: TypedEdge, anchoring: frozenset[str]) -> tuple[int, str]:
    """Direct anchors first, then everything else by a stable address.

    Dropping an anchor to keep a semantic edge leaves a graph that still reads as
    connected while the evidence that made it a group is gone.
    """
    return (0 if edge.edge_id in anchoring else 1, edge.edge_id)


def build_graph(
    *,
    group_id: str,
    neighborhood: Neighborhood,
    limits: GroupingLimits,
    duplicate_or_version: DuplicateOrVersion | None,
    created_at: str,
) -> LocalEvidenceGraph:
    """One typed, hub-suppressed, bounded graph over one retrieved neighbourhood."""
    seed_file_id = neighborhood.seed.file_id
    built: list[TypedEdge] = []
    anchoring: set[str] = set()
    for neighbor in neighborhood.neighbors:
        if neighbor.file_id == seed_file_id:
            # An edge from a file to itself relates nothing, and the record
            # refuses one; retrieval can legitimately return the seed.
            continue
        edge_type = _edge_type(neighbor, duplicate_or_version, seed_file_id)
        bridge = neighbor.detail
        edge_id = _edge_id(group_id, seed_file_id, neighbor.file_id, edge_type, bridge)
        built.append(TypedEdge(
            edge_id=edge_id,
            from_file_id=seed_file_id,
            to_file_id=neighbor.file_id,
            edge_type=edge_type,
            # A channel that cites no observation is still addressable: the edge
            # is its own evidence, and that is what a `Support.edge_ref` resolves.
            evidence_ref=neighbor.evidence_ref or edge_id,
            weight=None,
            bridge_entity_ref=bridge,
            hub_suppressed=False,
            created_at=created_at,
        ))
        if neighbor.anchors:
            anchoring.add(edge_id)

    hubs = _hub_entities(built, limits.generic_hub_frequency)
    suppressed = tuple(
        TypedEdge(
            edge_id=edge.edge_id, from_file_id=edge.from_file_id,
            to_file_id=edge.to_file_id, edge_type=edge.edge_type,
            evidence_ref=edge.evidence_ref, weight=edge.weight,
            bridge_entity_ref=edge.bridge_entity_ref,
            hub_suppressed=edge.bridge_entity_ref in hubs,
            created_at=edge.created_at,
        )
        for edge in built
    )

    ordered = sorted(suppressed, key=lambda edge: _rank(edge, frozenset(anchoring)))
    kept: list[TypedEdge] = []
    reached: list[str] = [seed_file_id]
    dropped: list[str] = []
    for edge in ordered:
        if edge.to_file_id in reached:
            kept.append(edge)
            continue
        if len(reached) >= limits.max_graph_nodes:
            dropped.append(edge.to_file_id)
            continue
        reached.append(edge.to_file_id)
        kept.append(edge)
    return LocalEvidenceGraph(
        group_id=group_id,
        seed_file_id=seed_file_id,
        file_ids=tuple(reached),
        edges=tuple(sorted(kept, key=lambda edge: edge.edge_id)),
        capped=bool(dropped),
        omissions=tuple(
            f"max_graph_nodes={limits.max_graph_nodes}: {file_id}"
            for file_id in sorted(set(dropped))
        ),
    )


ConflictsFor = Callable[[Sequence[str]], Sequence[Conflict]]

#: The rejection polarity P1 stores. Matching it is what "already rejected" means.
_REJECT: str = "reject"

def _standing_reject(
    conn: sqlite3.Connection, *, group_id: str, basis_key: str,
) -> bool:
    """A current P1 reject of this exact equivalent.

    P1 owns the query and drops rows at or below a reset cutoff; this matches
    `proposal_class` and `basis_key` exactly and treats only `reject` as
    suppression. P8's `suppressed_by_learning` reads the same rows the same way --
    two readings that disagreed would mean a proposal P8 refuses to call about and
    P9 keeps surfacing.
    """
    for row in learning_records(conn, GROUP_PROPOSAL_CLASS, group_id):
        if row["proposal_class"] != GROUP_PROPOSAL_CLASS:
            continue
        if row["basis_key"] != basis_key:
            continue
        if row["polarity"] == _REJECT:
            return True
    return False


def anchoring_files(
    graph: LocalEvidenceGraph, *, seed_anchors: bool,
) -> frozenset[str]:
    """Every file that states the group's basis DIRECTLY.

    The seed is one of them when its own fact is validated: a group of one, seeded
    by a direct fact, has an anchor even though no edge points at it. Counting only
    edge endpoints would say a file cannot anchor itself, which is the opposite of
    what a strongly-identified seed is.
    """
    reached = {
        edge.to_file_id for edge in graph.edges
        if edge.edge_type == SHARED_VALIDATED_FACT and not edge.hub_suppressed
    }
    if seed_anchors:
        reached.add(graph.seed_file_id)
    return frozenset(reached)


def meets_support_bar(
    graph: LocalEvidenceGraph, *, limits: GroupingLimits, seed_anchors: bool,
) -> bool:
    """Whether the group has enough INDEPENDENT anchors to be `supported`.

    Not a stop rule, and deliberately separate from SR1. SR1 is "no valid anchor"
    -- zero of them -- and it stops the group forming at all. This is §4.9's
    minimum independent anchor count, which decides whether a formed group may
    become `supported` rather than staying a candidate. Conflating the two made a
    one-anchor group vanish instead of waiting for confirmation.
    """
    return len(anchoring_files(graph, seed_anchors=seed_anchors)) >= (
        limits.minimum_independent_anchors)


def evaluate_stop_rules(
    conn: sqlite3.Connection,
    graph: LocalEvidenceGraph,
    *,
    limits: GroupingLimits,
    conflicts_for: ConflictsFor,
    basis_key: str,
    seed_anchors: bool,
) -> StopRuleOutcome | None:
    """The five stop rules decidable before a dossier and before a model call.

    Returns `None` when nothing fired. SR5 is absent by construction: it means P8
    could not explain the group with valid citations, and deciding that here would
    be P9 predicting what P8 was going to say.
    """
    live = [edge for edge in graph.edges if not edge.hub_suppressed]
    fired: list[str] = []
    evidence: list[str] = []

    if not anchoring_files(graph, seed_anchors=seed_anchors):
        # SR1 is zero anchors, not "fewer than the support bar". The bar is
        # `meets_support_bar`, and it decides `supported` rather than existence.
        fired.append(SR1)
        evidence.extend(edge.evidence_ref for edge in live)

    if live and all(edge.edge_type == MUTUAL_SEMANTIC_RETRIEVAL for edge in live):
        # An embedding can propose a neighbour and can never establish membership.
        fired.append(SR2)
        evidence.extend(edge.evidence_ref for edge in live)

    bridging = [edge for edge in graph.edges if edge.bridge_entity_ref is not None]
    if bridging and all(edge.hub_suppressed for edge in bridging):
        fired.append(SR3)
        evidence.extend(edge.evidence_ref for edge in bridging)

    found = conflicts_for(graph.file_ids)
    if found:
        fired.append(SR4)
        evidence.extend(
            f"{conflict.kind}:{'|'.join(conflict.competing_values)}"
            for conflict in found
        )

    if _standing_reject(conn, group_id=graph.group_id, basis_key=basis_key):
        fired.append(SR6)
        evidence.append(basis_key)

    if not fired:
        return None
    return StopRuleOutcome(
        group_id=graph.group_id,
        rules_fired=tuple(fired),
        evidence_refs=tuple(dict.fromkeys(evidence)),
        # SS4.9 permits an anchorless group to be shown "only as tentative
        # discovery candidates, if at all". That permission is for SR1 ALONE:
        # every other rule is a positive reason not to form the group, and one
        # of those outranks a permission to show it hesitantly.
        outcome=TENTATIVE_DISCOVERY if fired == [SR1] else NO_GROUP,
    )
