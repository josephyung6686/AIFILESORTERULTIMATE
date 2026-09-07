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
from evidence_shape.observation import is_observation_key

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
    fact_bridge_ref,
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


def _hub_entities(edges: Sequence[TypedEdge], frequency: int, *,
                  exempt: str | None = None) -> frozenset[str]:
    """Entities bridging at or above the injected frequency.

    The rule is a count, not a list of domains. A hard-coded university suffix or
    mail provider here would be P9 authoring a policy that belongs to
    configuration, and the corpus it was tuned on is not this user's.

    `exempt` is THE SEED'S OWN BASIS and is §4.3 read literally (`104` R-59's
    third finding). §4.3's count exists "to find an entity that bridges UNRELATED
    groups", and the value this group was seeded on is by definition not that: it
    is what makes these files one group. Counting it made a group of ten files
    seeded on `work_type = photograph` suppress every edge it had, which is why
    the shared-fact channel used to record no entity at all. The exemption is by
    NAME and applies to one value in one graph, so an entity that is a hub for
    some other seed is still a hub there.
    """
    counts: dict[str, int] = {}
    for edge in edges:
        if edge.bridge_entity_ref is None or edge.bridge_entity_ref == exempt:
            continue
        counts[edge.bridge_entity_ref] = counts.get(edge.bridge_entity_ref, 0) + 1
    return frozenset(
        entity for entity, count in counts.items() if count >= frequency
    )


def _rank(edge: TypedEdge, anchoring: frozenset[str]) -> int:
    """Direct anchors first, then everything else in the order retrieval ranked it.

    Dropping an anchor to keep a semantic edge leaves a graph that still reads as
    connected while the evidence that made it a group is gone. That is the whole
    of the rule; WITHIN each of the two classes the order is retrieval's, kept by
    a stable sort, which is why this returns one number and not a pair.

    **IT USED TO RETURN `(class, edge_id)`, AND THAT WAS `104` R-78.** `_edge_id`
    hashes the group id and both file ids, and a `file_id` is a `uuid4` minted
    when P1 first indexes the path -- so on two runs over one folder from an empty
    database the edges of one graph sort into an unrelated order. `build_graph`
    does not merely PRINT in this order, it CUTS in it: `max_graph_nodes` keeps
    the first N files reached, so which files were in the graph -- and therefore
    which files anchored the group, and which edges were stored at all -- was a
    fresh draw every run. Measured on a 63-file synthetic corpus, two runs of
    identical code over identical bytes gave 574 and 573 edges; the owner's 199
    files gave 511 and 510.

    `_edge_id` itself is untouched. It is a content address WITHIN one database,
    which is what `record_edges`'s supersession (`104` R-67) and a stored
    `Support.edge_ref` need it to be. What changed is that no decision is taken by
    it: an address is for finding a thing again, not for choosing between things.
    """
    return 0 if edge.edge_id in anchoring else 1


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
        # The neighbour's own bridge entity, NOT its `detail`. `detail` describes
        # why the channel returned the file; reading it here promoted every
        # description to an entity identity, so the group's own basis became a
        # "hub" the moment enough files corroborated it -- and §4.3's count, which
        # exists to find an entity that bridges UNRELATED groups, punished the
        # corroboration §4.3 asks the rules to make.
        #
        # STILL TRUE, AND THE SHARED-FACT CHANNEL NOW NAMES ONE (`104` R-59's
        # third finding). What changed is not this line: the channel decides at
        # `retrieval._shared_fact_neighbors` that it has an entity to name, and
        # `_hub_entities` below is told to EXEMPT the seed's own basis by name. So
        # the group's own basis still cannot make the group a hub, and every other
        # channel's description is still not promoted to an identity here.
        bridge = neighbor.bridge_entity
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

    # The seed's own basis, spelled by `vocabulary.fact_bridge_ref` -- the one
    # place the channel, this exemption and P11's frequency lookup all read it
    # from -- so the exemption names one value rather than a channel. A seed with no field and
    # no value (a user-created starting point, a structural family) exempts nothing.
    seed = neighborhood.seed
    seed_basis = (fact_bridge_ref(seed.field_key, seed.value)
                  if seed.field_key and seed.value else None)
    hubs = _hub_entities(built, limits.generic_hub_frequency, exempt=seed_basis)
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

    # `suppressed` is in `neighborhood.neighbors` order, which retrieval ranked by
    # channel weight and then by content; a STABLE sort on the anchor class alone
    # therefore promotes the anchors and leaves that order otherwise intact.
    anchors = frozenset(anchoring)
    ordered = sorted(suppressed, key=lambda edge: _rank(edge, anchors))
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
        # In the order they were kept, which is retrieval's content order with the
        # anchors first. Re-sorting by `edge_id` here was the second half of
        # `104` R-78: it decided nothing, and it made the stored row order of one
        # graph a per-run permutation, so no two runs could be compared row for
        # row. Dropping it removes an ordering by a minted id and adds none.
        edges=tuple(kept),
        capped=bool(dropped),
        omissions=tuple(
            f"max_graph_nodes={limits.max_graph_nodes}: {file_id}"
            for file_id in dict.fromkeys(dropped)
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


def _anchoring_edges(graph: LocalEvidenceGraph) -> tuple[TypedEdge, ...]:
    """The edges that make a file an anchor, and the ONE place that filter lives.

    `anchoring_files` and `anchor_observation_keys` have to select the same edges
    in the same order -- the second answers, per file, what the first returned --
    and two copies of `edge_type == SHARED_VALIDATED_FACT and not hub_suppressed`
    is how they would drift the day a third edge type may anchor.
    """
    return tuple(
        edge for edge in graph.edges
        if edge.edge_type == SHARED_VALIDATED_FACT and not edge.hub_suppressed
    )


def anchoring_files(
    graph: LocalEvidenceGraph, *, seed_anchors: bool,
) -> tuple[str, ...]:
    """Every file that states the group's basis DIRECTLY, in the graph's own order.

    The seed is one of them when its own fact is validated: a group of one, seeded
    by a direct fact, has an anchor even though no edge points at it. Counting only
    edge endpoints would say a file cannot anchor itself, which is the opposite of
    what a strongly-identified seed is.

    **A TUPLE AND NOT A SET (`104` R-78).** `Group.anchor_facts` stores this list
    and the record is compared between runs; a set had to be put in SOME order to
    be stored, the order taken was `sorted()` over the `file_id`s, and a `file_id`
    is a per-run `uuid4`, so the same group's anchors were written in an unrelated
    order every run. `graph.file_ids` is the graph's node order, which retrieval
    ranked by content, so ordering by it is ordering by content. Deduplicated, so
    `len()` still counts files and not edges -- `meets_support_bar` reads it as a
    count of INDEPENDENT anchors.
    """
    reached = {edge.to_file_id for edge in _anchoring_edges(graph)}
    if seed_anchors:
        reached.add(graph.seed_file_id)
    ordered = [file_id for file_id in graph.file_ids if file_id in reached]
    # A file that anchors and is not a graph node cannot exist -- `build_graph`
    # adds every edge's target to `reached` before keeping the edge -- and if one
    # ever did, dropping it silently would understate the group's own support.
    ordered.extend(sorted(reached.difference(ordered)))
    return tuple(ordered)


def anchor_observation_keys(
    graph: LocalEvidenceGraph, *, seed_anchors: bool,
    seed_observation_key: str | None,
) -> tuple[str | None, ...]:
    """One P4 key per anchoring file, aligned with `anchoring_files`' order.

    `104` R-97. `AnchorFact` carried one key for the whole group, the seed's, and
    every other stating file was recorded as citing it -- an observation of
    another file's bytes, which P7 refuses to resolve into a request that does not
    name that file. The per-file key was never missing: the shared-fact channel
    already reads it. `retrieval._shared_fact_neighbors` sets
    `evidence_ref=_first_ref(match)` from the CANDIDATE's own fact row, and
    `build_graph` carries it onto the edge. This function is the read that had not
    been written.

    **The edge's `evidence_ref` is not always a citation.** `build_graph` falls
    back to the edge's own id when a channel cites no observation -- "a channel
    that cites no observation is still addressable" -- and a `user_confirmed`
    anchor genuinely has none, because the value is the person's answer rather
    than an extractor's reading. `is_observation_key` is what tells the two apart,
    asked of the key by the module that mints one rather than by a prefix match
    written here, and the answer for a fallback id is `None`: this file cites
    nothing of its own, which is a true thing to record and a safe one to carry.
    """
    by_file: dict[str, str | None] = {}
    for edge in _anchoring_edges(graph):
        by_file.setdefault(edge.to_file_id, edge.evidence_ref)
    if seed_anchors:
        # The seed's own, and never an edge's: `build_graph` writes edges FROM the
        # seed, so no edge carries the seed's citation.
        by_file[graph.seed_file_id] = seed_observation_key
    return tuple(
        by_file[file_id] if is_observation_key(by_file.get(file_id)) else None
        for file_id in anchoring_files(graph, seed_anchors=seed_anchors)
    )


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

    suppressed = [edge for edge in graph.edges if edge.hub_suppressed]
    if suppressed and not live:
        # SR3 is "one high-frequency entity acts as the ONLY bridge": a hub was
        # suppressed and nothing else is left holding the graph together. Asking
        # instead whether every ENTITY-BEARING edge was suppressed says the same
        # thing only while every edge carries an entity, which stopped being true
        # when `bridge_entity` became its own field -- and would then fire on a
        # graph whose anchors are perfectly alive, destroying the group for having
        # sat in a busy folder.
        fired.append(SR3)
        evidence.extend(edge.evidence_ref for edge in suppressed)

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
