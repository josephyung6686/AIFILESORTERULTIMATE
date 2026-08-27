"""§6.3's bounded candidate retrieval, and §6.3's active suppression.

Six channels drive retrieval and none of them decides. A candidate is a node the
evidence gives a reason to consider; whether it becomes a placement is §6.10's
question, asked one task later. Keeping the two apart is what lets a semantic
neighbour improve recall (§6.5) without ever becoming the sole reason for a move.

Suppression is recorded, not silent. §6.3 says conflicting evidence "actively
suppresses" nodes, and SPEC:502-504 requires the suppression to reach
`conflicts_considered` so the review interface can show what was ruled out and
why. A node dropped without a record is a question the user cannot ask.

An `ignored` node needs no rule here at all: it never entered the index, so it can
neither be retrieved nor suppressed, and §5.10 holds without a second mechanism.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from facts.read_surface import is_destination_eligible

from placement import events as placement_events
from placement.index import entries_for_plan
from placement.records import ConflictConsidered, MatchingFact
from placement.store import subject_ref_of

DIRECT_FACT: str = "direct_fact"
ACCEPTED_GROUP: str = "accepted_group"
GRAPH_RELATIONSHIP: str = "graph_relationship"
STRUCTURAL_RELATIONSHIP: str = "structural_relationship"
SEMANTIC_NEIGHBOUR: str = "semantic_neighbour"
CURATED_FOLDER: str = "curated_folder"

#: §6.3's own list of what drives retrieval. Six, and a seventh would be a
#: contract revision rather than an implementation decision.
CHANNELS: tuple[str, ...] = (
    DIRECT_FACT, ACCEPTED_GROUP, GRAPH_RELATIONSHIP, STRUCTURAL_RELATIONSHIP,
    SEMANTIC_NEIGHBOUR, CURATED_FOLDER,
)

#: The two channels that can never make a node a candidate on their own terms
#: strongly enough to place. Task 9 refuses a `place` supported only by these.
NON_DECIDING_CHANNELS: tuple[str, ...] = (SEMANTIC_NEIGHBOUR, CURATED_FOLDER)


@dataclass(frozen=True)
class Candidate:
    node_id: str
    channels: tuple[str, ...]
    matching_facts: tuple[MatchingFact, ...]
    group_ids: tuple[str, ...]


@dataclass(frozen=True)
class Retrieval:
    subject_ref: str
    plan_version: str
    candidates: tuple[Candidate, ...]
    conflicts: tuple[ConflictConsidered, ...]
    semantic_only_node_ids: frozenset[str]


def _eligible_facts(conn: sqlite3.Connection, facts) -> tuple[MatchingFact, ...]:
    """Drop facts whose field P6 says is not a destination dimension (§3.8).

    P6 already publishes the answer per field, so P11 asks it rather than keeping
    a second opinion about which fields may build a folder. A field the catalogue
    does not carry raises out of `is_destination_eligible` rather than being
    silently treated as ineligible: a typo must not read as a policy.
    """
    return tuple(
        fact for fact in facts
        if is_destination_eligible(conn, field_key=fact.field)
    )


def retrieve(conn: sqlite3.Connection, *, subject, plan_version, limits,
             facts, group_ids, curated_folder_labels, semantic_neighbours,
             component_version: str, observed_at: str) -> Retrieval:
    subject_ref = subject_ref_of(subject)
    entries = entries_for_plan(conn, plan_version=plan_version)
    usable = _eligible_facts(conn, facts)
    by_field = {(fact.field, fact.value): fact for fact in usable}
    stated_fields = {fact.field for fact in usable}
    wanted_groups = set(group_ids)
    wanted_labels = {label.casefold() for label in curated_folder_labels}
    semantic = set(semantic_neighbours)

    matched: dict[str, dict] = {}
    conflicts: list[ConflictConsidered] = []
    suppressed_by_value: dict[tuple[str, str], list[str]] = {}

    for entry in entries:
        channels: list[str] = []
        entry_facts: list[MatchingFact] = []
        entry_groups: list[str] = []
        contradicted = False
        for field, value in entry.expected_values:
            fact = by_field.get((field, value))
            if fact is not None:
                channels.append(DIRECT_FACT)
                entry_facts.append(fact)
            elif field in stated_fields:
                # The subject states this field with a DIFFERENT value. §6.3's
                # suppression: a direct `target institution = Duke` must not
                # retrieve Columbia branches as a top candidate.
                contradicted = True
                held = next(f for f in usable if f.field == field)
                suppressed_by_value.setdefault(
                    (field, held.value), []).append(entry.node_id)
        if contradicted:
            continue
        overlap = wanted_groups & set(entry.accepted_group_ids)
        if overlap:
            channels.append(ACCEPTED_GROUP)
            entry_groups.extend(sorted(overlap))
        if entry.display_label.casefold() in wanted_labels:
            channels.append(CURATED_FOLDER)
        if entry.node_id in semantic:
            channels.append(SEMANTIC_NEIGHBOUR)
        if channels:
            matched[entry.node_id] = {
                "channels": tuple(dict.fromkeys(channels)),
                "facts": tuple(entry_facts), "groups": tuple(entry_groups),
            }

    for (field, value), node_ids in sorted(suppressed_by_value.items()):
        held = next(f for f in usable if f.field == field and f.value == value)
        conflicts.append(ConflictConsidered(
            kind=field, conflicting_value=value,
            suppressed_node_ids=tuple(sorted(node_ids)),
            evidence_ref=held.evidence_ref,
        ))

    def _rank(item):
        node_id, body = item
        # Deterministic and stable: strongest channel first, then the node id, so
        # two runs over the same evidence produce the same order and a P2 replay
        # can compare them. Never insertion order.
        strength = tuple(
            0 if channel in body["channels"] else 1 for channel in CHANNELS
        )
        return (strength, node_id)

    ordered = sorted(matched.items(), key=_rank)[:limits.max_retrieved_neighbors]
    candidates = tuple(
        Candidate(node_id=node_id, channels=body["channels"],
                  matching_facts=body["facts"], group_ids=body["groups"])
        for node_id, body in ordered
    )
    semantic_only = frozenset(
        candidate.node_id for candidate in candidates
        if set(candidate.channels) <= set(NON_DECIDING_CHANNELS)
    )
    placement_events.candidate_retrieval(
        conn, subject_ref=subject_ref, plan_version=plan_version,
        retrieved=[c.node_id for c in candidates],
        suppressed=sorted({n for c in conflicts for n in c.suppressed_node_ids}),
        component_version=component_version, observed_at=observed_at,
        file_id=subject.file_id, content_hash=subject.content_hash,
    )
    return Retrieval(
        subject_ref=subject_ref, plan_version=plan_version,
        candidates=candidates, conflicts=tuple(conflicts),
        semantic_only_node_ids=semantic_only,
    )
