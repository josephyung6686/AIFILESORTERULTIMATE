# src/grouping/dossier.py
"""The bounded, reference-only group dossier. P9 assembles; P8 materialises.

Nothing here reaches a model, a gate or a released span. This module selects
REFERENCES — observation keys, file version identities, typed edges — and records
what it left out. `build_dossier_request` in the P8 seam turns this record into
P8's `DossierRequest`; P8 alone materialises released evidence through P7 and
constructs a `Dossier`.

Three rules carry the weight.

**Anchor and candidate files are separate arrays and are never merged.** The model
must be able to say a group is coherent while still marking particular members
uncertain, and it can only do that if direct evidence and inferred context arrive
apart.

**Nothing is dropped silently.** A file withheld for privacy, a file cut by the
neighbourhood cap and a file cut by a budget are three different omissions with
three different fields, and every one is present-and-named rather than absent.
Silence about a dropped file is the failure, not the drop.

**P9 runs no token ladder.** It measures no dossier tokens, summarises no fact,
drops no excerpt by a budget, splits no request and creates no budget-deferred
decision. M9's summarize -> preserve anchors -> split/defer ladder is P8's
`run_call`, under P1's `model.max_dossier_tokens_per_call` ceiling.
"""
from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from evidence_shape.canonical import canonical_json
from evidence_shape.store import observations_by_key
from privacy.classification import UNREADABLE_UNCLASSIFIED, resolve_class

from grouping.config import ConfigurationRequired, GroupingLimits
from grouping.graph import LocalEvidenceGraph
from grouping.records import (
    AnchorFact,
    BudgetSummary,
    CandidateGroupDossier,
    Conflict,
    DossierFile,
    Excerpt,
    Group,
    Omissions,
    PrivacySummary,
)
from grouping.vocabulary import CONTEXT_SUPPORTED, DIRECT_ANCHOR

#: What P3 records when it cannot name a format. P9 asserts nothing about a file
#: it cannot describe.
UNCLASSIFIED_DOCUMENT_TYPE: str = "unclassified"

ActiveSchemaFor = Callable[[sqlite3.Connection, str, str], Sequence[str]]
SignalEvaluatorFor = Callable[[str], object]
ClassificationStore = Callable[[str, str], object]


@dataclass(frozen=True)
class DossierRefused:
    """No dossier, and the reason. Never a dossier with the reason missing."""

    group_id: str
    reason: str
    withheld: tuple[str, ...]


def _require_knowledge(active_schema_for, signal_evaluator_for,
                       classification_store) -> None:
    missing = [
        name for name, value in (
            ("active_schema_for", active_schema_for),
            ("signal_evaluator_for", signal_evaluator_for),
            ("classification_store", classification_store),
        )
        if not callable(value)
    ]
    if missing:
        raise ConfigurationRequired(
            f"{missing} were not supplied. P9 authors no domain schema, no signal "
            "evaluator and no handling class; without them there is no category to "
            "propose, and inventing one is how a group acquires a name nobody can "
            "trace."
        )


def _file_row(conn: sqlite3.Connection, file_id: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT content_hash, detected_format FROM files WHERE file_id = ?",
        (file_id,),
    ).fetchone()


def _excerpts_for(
    conn: sqlite3.Connection, keys: Sequence[str], *, limit: int,
) -> tuple[Excerpt, ...]:
    """One short excerpt per cited observation key, in the order cited.

    A key that resolves to nothing is skipped rather than carried. P8 verifies a
    citation by resolving it, so an excerpt whose key resolves to nothing would be
    a quotation the model could not be held to.
    """
    found: list[Excerpt] = []
    for key in dict.fromkeys(keys):
        observations = observations_by_key(conn, key)
        if not observations:
            continue
        observation = observations[0]
        found.append(Excerpt(
            observation_key=key,
            location=observation.location.zone,
            text=observation.raw_value[:limit],
        ))
    return tuple(found)


def _facts_for(group: Group, file_id: str) -> tuple[AnchorFact, ...]:
    return tuple(fact for fact in group.anchor_facts if file_id in fact.file_ids)


def _why_retrieved(graph: LocalEvidenceGraph, file_id: str) -> str:
    """The channel that brought this file, named.

    A reviewer has to be able to tell a shared validated fact from a semantic
    guess; without the channel both read as "it was in the neighbourhood".
    """
    kinds = sorted({
        edge.edge_type for edge in graph.edges
        if edge.to_file_id == file_id and not edge.hub_suppressed
    })
    return "+".join(kinds) if kinds else graph.seed_file_id


def _fingerprint(group_id: str, anchors, candidates, edges) -> str:
    """A stable hash of the references assembled, for cache keying and replay.

    Content-derived rather than random: two assemblies over the same references
    are the same dossier, and a replay has to be able to say so. `created_at` is
    deliberately not in it, or the same dossier assembled twice would be two.
    """
    body = canonical_json({
        "anchors": [
            [item.file_id, item.content_hash,
             [excerpt.observation_key for excerpt in item.excerpts]]
            for item in anchors
        ],
        "candidates": [
            [item.file_id, item.content_hash,
             [excerpt.observation_key for excerpt in item.excerpts]]
            for item in candidates
        ],
        "edges": sorted(edge.edge_id for edge in edges),
        "group_id": group_id,
    })
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def assemble_group_dossier(
    conn: sqlite3.Connection,
    *,
    group: Group,
    graph: LocalEvidenceGraph,
    limits: GroupingLimits,
    active_schema_for: ActiveSchemaFor | None,
    signal_evaluator_for: SignalEvaluatorFor | None,
    classification_store: ClassificationStore | None,
    conflicts: Sequence[Conflict] = (),
    created_at: str,
) -> CandidateGroupDossier | DossierRefused:
    """One reference-only dossier over one bounded graph.

    Returns `DossierRefused` when withholding leaves no direct evidence: a group
    with no anchor file has nothing for the model to judge, and building the record
    anyway would put an empty question in front of a paid model call.
    """
    _require_knowledge(active_schema_for, signal_evaluator_for, classification_store)

    stating = {
        file_id for fact in group.anchor_facts for file_id in fact.file_ids
    }
    anchors: list[DossierFile] = []
    candidates: list[DossierFile] = []
    withheld: list[str] = []
    classes: set[str] = set()

    for file_id in graph.file_ids:
        row = _file_row(conn, file_id)
        content_hash = row["content_hash"] if row is not None else ""
        handling_class = resolve_class(classification_store(file_id, content_hash))
        classes.add(handling_class)
        if handling_class == UNREADABLE_UNCLASSIFIED:
            # Marked and counted, never opened. §8.4 requires classification before
            # escalation, so an unclassified file is withheld -- and named in
            # `omissions`, so a later reader shows it as present-but-untouched
            # rather than as a file that was never there.
            withheld.append(file_id)
            continue
        is_anchor = file_id in stating
        facts = _facts_for(group, file_id)
        item = DossierFile(
            file_id=file_id,
            content_hash=content_hash,
            document_type=(
                row["detected_format"] if row is not None and row["detected_format"]
                else UNCLASSIFIED_DOCUMENT_TYPE
            ),
            basis=DIRECT_ANCHOR if is_anchor else CONTEXT_SUPPORTED,
            key_facts=facts,
            excerpts=_excerpts_for(
                conn, [fact.observation_key for fact in facts],
                # How short a short excerpt is decides how much of a file
                # reaches a model. That is a policy, and it arrives injected.
                limit=limits.max_excerpt_characters),
            why_retrieved=None if is_anchor else _why_retrieved(graph, file_id),
        )
        (anchors if is_anchor else candidates).append(item)

    if not anchors:
        return DossierRefused(
            group_id=group.group_id,
            reason=(
                "every file carrying direct evidence was withheld; a dossier with "
                "no anchor has nothing for the model to judge"
                if withheld else
                "no file in the graph states the group's basis directly"
            ),
            withheld=tuple(withheld),
        )

    capped = tuple(
        line.split(": ", 1)[1] for line in graph.omissions if ": " in line
    )
    fingerprint = _fingerprint(group.group_id, anchors, candidates, graph.edges)
    return CandidateGroupDossier(
        dossier_id=fingerprint,
        group_id=group.group_id,
        proposed_basis=group.proposed_basis,
        anchor_files=tuple(anchors),
        candidate_files=tuple(candidates),
        typed_edges=graph.edges,
        key_facts=group.anchor_facts,
        excerpts=tuple(
            excerpt
            for item in (*anchors, *candidates)
            for excerpt in item.excerpts
        ),
        conflicts=tuple(conflicts),
        engine_flagged_outliers=(),
        omissions=Omissions(
            # P9 applies no token budget, so this stays empty by construction.
            budget_cap_dropped=(),
            privacy_redacted=tuple(withheld),
            neighbourhood_capped=capped,
        ),
        privacy=PrivacySummary(
            handling_classes=tuple(sorted(classes)),
            redactions_applied=len(withheld),
            # P7 decides at release time, which is P8's call, not this assembly.
            release_decision_ref=None,
        ),
        budget=BudgetSummary(
            token_ceiling=limits.max_dossier_tokens,
            neighbour_cap=limits.max_graph_nodes,
            files_dropped=len(capped),
        ),
        dossier_fingerprint=fingerprint,
        created_at=created_at,
    )
