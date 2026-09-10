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

#: THE CHANNELS `retrieve` CAN ACTUALLY PUT ON A CANDIDATE, which is not
#: `CHANNELS` and has never been. `104` §18.2 gap 13 is what the difference cost:
#: `retrieve`'s loop below appends exactly four -- `DIRECT_FACT` from
#: `matched_pairs`, `ACCEPTED_GROUP` from `accepted_groups`, `CURATED_FOLDER`
#: from `label_matches` and `SEMANTIC_NEIGHBOUR` from `semantic_matches` -- and
#: nothing anywhere produces `GRAPH_RELATIONSHIP` or `STRUCTURAL_RELATIONSHIP`.
#: The scorer, meanwhile, divided by all four DECIDING weights (3+2+1+1 = 7), so
#: a file whose every direct fact matched one node scored 3/7 = 0.429 against a
#: 0.50 bar and could not be placed by facts alone. Two sevenths of the scale
#: were reserved for evidence nothing could collect, and that reservation decided
#: the outcome.
#:
#: So retrieval DECLARES what it produces and the scorer normalises over that.
#: The declaration lives here because this is the module whose loop decides it:
#: a channel gains a producer here and its weight starts counting in the same
#: commit, and a channel that loses one stops counting without anybody editing a
#: number in `scoring.py`.
#:
#: **The two absentees are Release-2 items and not oversights.** §18.2 gap 12 is
#: the node-local typed graph, which is built and contributes nothing -- five of
#: nine edge types, never entering the dossier -- and it is what would produce
#: `GRAPH_RELATIONSHIP`. §18.2 gap 14 is group placement as a first-class
#: capability, which today is post-hoc aggregation over single-file decisions,
#: and the version family / duplicate family / photo event links it would carry
#: are what would produce `STRUCTURAL_RELATIONSHIP`. Both are ranked **L**.
#: Adding either name here without its producer would restore exactly the gap
#: this constant closes.
PRODUCED_CHANNELS: tuple[str, ...] = (
    DIRECT_FACT, ACCEPTED_GROUP, CURATED_FOLDER, SEMANTIC_NEIGHBOUR,
)


@dataclass(frozen=True)
class Candidate:
    node_id: str
    channels: tuple[str, ...]
    matching_facts: tuple[MatchingFact, ...]
    group_ids: tuple[str, ...]


@dataclass(frozen=True)
class SetAside:
    """A candidate a step-6 rule RANKED BELOW the contenders instead of deleting.

    `104` §18.2 gap 2, and `00`'s placement amendment of 2026-09-05 is the whole
    of the argument: "Deterministic scores RANK AND SHORTLIST the candidates the
    model is shown, and deterministic validation rejects only a structurally
    invalid answer." A rule that DELETES a legal folder before the model sees it
    is not ranking it -- it is answering the model's question for it, and then
    Site C calls the model's own correct answer `INVENTED_NODE` because the
    folder is not on the list P11 handed over.

    So the four step-6 rules keep every discrimination their docstrings argue and
    measure, and lose only the deletion. What each one used to drop is moved
    here, `because` carrying the rule's own sentence, and `pipeline._offered_items`
    writes that sentence into the folder's description in the dossier -- the same
    `location` string that already tells the model "the file sits in this folder
    now". The model reads the reason and decides; the rules stop deciding.

    **The contenders are still the contenders**, and that is why this is a
    separate field rather than a flag on `Candidate`. `Retrieval.candidates` is
    read by `score_candidates`, `assess`, `needs_model_call`, the node-local
    graphs and `_explain`, and every one of those is §6.10's DETERMINISTIC path
    -- the fallback `00` keeps "with no model configured". A flag on `Candidate`
    would need a filter at each of those readers, and a single missed filter
    would silently move an offline placement: the `Desktop/AP world` exams and the
    law student's report card, both measured on 2026-09-05, come back the moment
    a set-aside candidate is scored as a rival. Here they cannot, by construction.
    """

    candidate: Candidate
    because: str


@dataclass(frozen=True)
class Retrieval:
    subject_ref: str
    plan_version: str
    candidates: tuple[Candidate, ...]
    conflicts: tuple[ConflictConsidered, ...]
    semantic_only_node_ids: frozenset[str]
    #: Which of `CHANNELS` the run that produced this retrieval could put on a
    #: candidate. REQUIRED, WITH NO DEFAULT, for the reason `PipelineInputs.
    #: ask_or_abstain` is required: a default here would be a second answer to
    #: the question this field exists to make explicit, and it would be the
    #: WRONG answer the moment a caller retrieves through a narrower path than
    #: `retrieve` -- silently scoring against a scale that caller cannot reach.
    #: `scoring.score_candidates` reads it as the denominator; `104` §18.2 gap
    #: 13 is what the missing declaration cost.
    producible_channels: tuple[str, ...]
    #: The candidates step 6's four rules ranked below the contenders rather than
    #: deleting (`104` §18.2 gap 2, and gap 11's shallower approved parent).
    #: DEFAULTED, unlike `producible_channels` above, and the difference is real:
    #: an empty set-aside list is the honest answer for every retrieval nobody
    #: has run a step-6 rule over, whereas an empty producible-channel list is a
    #: scale no candidate could score against. `retrieve` never fills this --
    #: §6.3 suppresses on conflicting evidence and that suppression is a
    #: CONFLICT, recorded in `conflicts` and shown to the model as a flag it must
    #: echo; the four rules that fill this are §6.12 step 6's and live in
    #: `placement.pipeline`.
    set_aside: tuple[SetAside, ...] = ()


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
        producible_channels=PRODUCED_CHANNELS,
    )
