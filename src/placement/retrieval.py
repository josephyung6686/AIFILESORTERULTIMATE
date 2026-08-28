"""§6.3's bounded candidate retrieval, and §6.3's active suppression.

Six channels drive retrieval and none of them decides. A candidate is a node the
evidence gives a reason to consider; whether it becomes a placement is §6.10's
question, asked one task later. Keeping the two apart is what lets a semantic
neighbour improve recall (§6.5) without ever becoming the sole reason for a move.

Suppression is recorded, not silent. §6.3 says conflicting evidence "actively
suppresses" nodes, and SPEC:502-504 requires the suppression to reach
`conflicts_considered` so the review interface can show what was ruled out and
why. A node dropped without a record is a question the user cannot ask.

What the record NAMES is the nodes a channel was pulling the subject towards --
`00`:107's Columbia branches, reached by the essays and ruled out by the Duke
fact. What it COUNTS is every node the conflicting value rules out, including the
ones nothing was pulling towards. Naming those too is one row per node per file:
eight million ids on a 10,000-file disk with an 800-node tree
(`planning/58-SCALE-STRESS.md` §2), and a review surface listing every folder the
user owns. Counted-and-unnamed keeps them visible without making them the record.

An `ignored` node needs no rule here at all: it never entered the index, so it can
neither be retrieved nor suppressed, and §5.10 holds without a second mechanism.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from facts.read_surface import is_destination_eligible

from placement import events as placement_events
from placement.index import reachable_entries
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
    usable = _eligible_facts(conn, facts)
    by_field = {(fact.field, fact.value): fact for fact in usable}
    wanted_groups = frozenset(group_ids)
    wanted_labels = frozenset(label.casefold() for label in curated_folder_labels)
    semantic = frozenset(semantic_neighbours)

    # §6.2's index, asked for the nodes this subject's own evidence selects. It
    # used to be `entries_for_plan` -- every legal node, payload deserialised,
    # once per subject -- which is the O(files x nodes) read
    # `planning/58-SCALE-STRESS.md` §2 measured. Every node this skips carries
    # none of the subject's stated fields, none of its groups and none of its
    # labels, and is not a semantic neighbour, so §6.3's loop would have
    # collected nothing from it and suppressed nothing on it.
    reachable = reachable_entries(
        conn, plan_version=plan_version, pairs=frozenset(by_field),
        group_ids=wanted_groups, labels=wanted_labels, node_ids=semantic,
        name_limit=limits.max_retrieved_neighbors)

    matched: dict[str, dict] = {}
    conflicts: list[ConflictConsidered] = []
    suppressed_by_value: dict[tuple[str, str], list[str]] = {}

    # §6.3's suppression, recorded before anything is a candidate. The key is the
    # subject's OWN value for the field, not the value the node carried, because
    # `ConflictConsidered.conflicting_value` is "what this file says" -- one
    # record per stated value, naming the branches it pulled the file away from
    # and counting every branch it ruled out.
    suppressed_counts: dict[tuple[str, str], int] = {}
    for field, total in reachable.contradicted_counts.items():
        held = next(fact for fact in usable if fact.field == field)
        key = (field, held.value)
        suppressed_by_value.setdefault(key, []).extend(
            reachable.contradicted.get(field, ()))
        suppressed_counts[key] = suppressed_counts.get(key, 0) + total

    for node_id in reachable.candidate_node_ids:
        channels: list[str] = []
        entry_facts: list[MatchingFact] = []
        entry_groups: list[str] = []
        for field, value in reachable.matched_pairs.get(node_id, ()):
            channels.append(DIRECT_FACT)
            entry_facts.append(by_field[(field, value)])
        overlap = wanted_groups & reachable.accepted_groups.get(
            node_id, frozenset())
        if overlap:
            channels.append(ACCEPTED_GROUP)
            entry_groups.extend(sorted(overlap))
        if node_id in reachable.label_matches:
            channels.append(CURATED_FOLDER)
        if node_id in reachable.semantic_matches:
            channels.append(SEMANTIC_NEIGHBOUR)
        # No `if channels:` guard. Every node in `candidate_node_ids` got there
        # from one of the four collections above, so at least one branch fired --
        # a guard here could never be false, and a guard that cannot fail reads
        # as a rule this loop enforces when it enforces nothing.
        matched[node_id] = {
            "channels": tuple(dict.fromkeys(channels)),
            "facts": tuple(entry_facts), "groups": tuple(entry_groups),
        }

    for (field, value), node_ids in sorted(suppressed_by_value.items()):
        held = next(f for f in usable if f.field == field and f.value == value)
        conflicts.append(ConflictConsidered(
            kind=field, conflicting_value=value,
            suppressed_node_ids=tuple(sorted(node_ids)),
            evidence_ref=held.evidence_ref,
            suppressed_node_count=suppressed_counts[(field, value)],
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
        suppressed_count=sum(c.suppressed_node_count for c in conflicts),
        component_version=component_version, observed_at=observed_at,
        file_id=subject.file_id, content_hash=subject.content_hash,
    )
    return Retrieval(
        subject_ref=subject_ref, plan_version=plan_version,
        candidates=candidates, conflicts=tuple(conflicts),
        semantic_only_node_ids=semantic_only,
    )
