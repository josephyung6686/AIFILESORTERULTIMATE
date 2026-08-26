# src/grouping/pipeline.py
"""P9's five stages, in order, with every authority injected.

seeds -> bounded embeddings -> bounded retrieval -> graph and pre-model stop rules
-> reference-only dossier -> P8's `run_call` when eligible -> mapped disposition.

Two orderings are load-bearing.

**The stop rules run before the dossier.** A group that cannot form should not
cost a dossier, let alone a model call, so SR1-SR4 and SR6 return before anything
is assembled.

**The eligible set is bounded before a single text is read.** Encoding is paid at
read time, so a cap applied afterwards has already been exceeded. The seed
reserves one slot; at most `max_graph_nodes - 1` other versions survive, after
duplicates are removed and a stable order is applied.

`p8_run_call=None` is a legal deterministic run. What it cannot do is finish a
judgement: a candidate that needs one stays `candidate` with a stated reason,
because a group P9 called coherent without asking would be P9 synthesising a
verdict.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field

from grouping.acceptance import record_acceptance  # noqa: F401  (seam readability)
from grouping.config import ConfigurationRequired, GroupingLimits
from grouping.dossier import DossierRefused, assemble_group_dossier
from grouping.embeddings import (
    EmbeddingsOff,
    EmbeddingsOn,
    FileVersionRef,
    ensure_file_embedding,
)
from grouping.graph import LocalEvidenceGraph, build_graph, evaluate_stop_rules
from grouping.learning import group_basis_key
from grouping.records import (
    AnchorFact,
    CandidateGroupDossier,
    Group,
    Membership,
    StopRuleOutcome,
    Support,
)
from grouping.retrieval import Neighborhood, RetrievalKnowledge, retrieve_neighbors
from grouping.seeds import Seed, UserSeed, seeds_for_file
from grouping.store import record_group, record_membership
from grouping.vocabulary import (
    CANDIDATE,
    DIRECT_ANCHOR,
    INCLUDED,
    NO_SENSITIVITY,
    NOT_FLAGGED,
    RULES,
    SHARED_VALIDATED_FACT,
)

#: What a deterministic run says about a judgement it did not make. Named rather
#: than left blank: a candidate with no reason reads as a candidate nobody looked
#: at, and this one was looked at and deliberately not decided.
NO_MODEL_CONFIGURED: str = "no_model_call_configured"


@dataclass(frozen=True)
class GroupingKnowledge:
    """Everything P9 does not author, in one bundle. Absent means refuse."""

    retrieval: RetrievalKnowledge
    active_schema_for: Callable[..., Sequence[str]]
    signal_evaluator_for: Callable[[str | None], object]
    classification_store: Callable[[str, str], object]
    conflicts_for: Callable[[Sequence[str]], Sequence[object]]
    duplicate_or_version: Callable[[str, str], str] | None


@dataclass(frozen=True)
class GroupingResult:
    """One subject, through the whole sequence. Every field is derived."""

    subject_file_id: str
    subject_content_hash: str
    seeds: tuple[Seed, ...]
    neighborhood: Neighborhood | None
    graph: LocalEvidenceGraph | None
    stop_rule_outcome: StopRuleOutcome | None
    group: Group | None
    memberships: tuple[Membership, ...]
    dossier: CandidateGroupDossier | None
    model_result: object | None
    not_implemented_reason: str | None
    omissions: tuple[str, ...] = field(default=())


def _bounded_versions(
    conn: sqlite3.Connection,
    runtime: EmbeddingsOn,
    seed: Seed,
    limits: GroupingLimits,
) -> tuple[FileVersionRef, ...]:
    """The eligible set, deduplicated, ordered and cut -- before any text is read.

    The seed reserves one graph slot, so at most `max_graph_nodes - 1` others
    survive. The order is `(content_hash, file_id)` so two runs over one corpus
    encode the same versions rather than whichever the caller happened to list
    first.
    """
    eligible = runtime.eligible_versions_for(conn, seed, limits.max_graph_nodes)
    seen: dict[tuple[str, str], FileVersionRef] = {}
    for ref in eligible:
        if ref.file_id == seed.file_id and ref.content_hash == seed.content_hash:
            continue
        seen.setdefault((ref.content_hash, ref.file_id), ref)
    ordered = [seen[key] for key in sorted(seen)]
    return tuple(ordered[:max(0, limits.max_graph_nodes - 1)])


def _prepare_embeddings(
    conn: sqlite3.Connection,
    *,
    embeddings,
    seed: Seed,
    limits: GroupingLimits,
    created_at: str,
) -> None:
    """Compute the vectors retrieval will read back from P1, and no others.

    Retrieval receives no encoder output. The path is encoder -> versioned P1
    record -> P1 read -> mutual semantic retrieval, so a vector that was never
    stored cannot become a neighbour by shortcut.
    """
    if isinstance(embeddings, EmbeddingsOff):
        return
    if not isinstance(embeddings, EmbeddingsOn):
        raise ConfigurationRequired(
            "embeddings must be EmbeddingsOff or EmbeddingsOn; P9 does not "
            "interpret another shape as a runtime"
        )
    missing = [
        name for name in ("config", "encoder", "embedding_text_for",
                          "eligible_versions_for")
        if getattr(embeddings, name, None) is None
    ]
    if missing:
        # Revalidated rather than trusted: a deserializer can construct this
        # record past `__post_init__`, and an incomplete enabled runtime reaching
        # retrieval is a semantic channel with no vectors behind it.
        raise ConfigurationRequired(
            f"an enabled embedding runtime is missing {missing}; P9 authors no "
            "encoder, no scope and no model identity"
        )
    versions = (
        FileVersionRef(file_id=seed.file_id, content_hash=seed.content_hash),
        *_bounded_versions(conn, embeddings, seed, limits),
    )
    for ref in versions:
        ensure_file_embedding(
            conn, file_id=ref.file_id, content_hash=ref.content_hash,
            config=embeddings.config, encoder=embeddings.encoder,
            embedding_text_for=embeddings.embedding_text_for,
            embeddings_enabled=True, created_at=created_at,
        )


def _group_for(seed: Seed, *, group_id: str, created_at: str) -> Group:
    facts = (
        (AnchorFact(
            field=seed.field_key, value=seed.value,
            file_ids=(seed.file_id,), reliability_state=seed.reliability_state,
            observation_key=seed.observation_key),)
        if seed.field_key and seed.value and seed.observation_key
        and seed.reliability_state
        else ()
    )
    return Group(
        group_id=group_id,
        seed_ref=f"{seed.file_id}:{seed.content_hash}",
        seed_kind=seed.seed_kind,
        proposed_basis=(
            f"{seed.field_key}={seed.value}" if seed.field_key
            else seed.basis or seed.seed_kind
        ),
        anchor_facts=facts,
        pre_model_signals={"anchor_count": len(facts)},
        anchor_count=len(facts),
        coherence_verdict=None,
        coherence_citations=(),
        group_category=None,
        display_label=None,
        label_source=None,
        conflicts=(),
        stop_rule_hits=(),
        state=CANDIDATE,
        sensitivity_state=NO_SENSITIVITY,
        dossier_id=None,
        llm_response_ref=None,
        validation_verdict_ref=None,
        created_by=RULES,
        created_at=created_at,
    )


def _self_membership(group: Group, seed: Seed, *, created_at: str) -> Membership:
    """The group of one. Its own direct fact is what makes it a member."""
    return Membership(
        membership_id=f"{group.group_id}:{seed.file_id}",
        group_id=group.group_id,
        file_id=seed.file_id,
        content_hash=seed.content_hash,
        basis=DIRECT_ANCHOR,
        decision=INCLUDED,
        decision_source=RULES,
        support=(Support(
            support_kind=SHARED_VALIDATED_FACT,
            observation_key=seed.observation_key,
            quote_or_field=seed.field_key,
            location=None,
            edge_ref=None),),
        insufficient_evidence=False,
        insufficiency_statement=None,
        conflicts=(),
        outlier_flag=NOT_FLAGGED,
        validation_verdict_ref=None,
        created_at=created_at,
    )


def group_subject(
    conn: sqlite3.Connection,
    *,
    file_id: str,
    content_hash: str,
    plan_version_id: str,
    limits: GroupingLimits,
    knowledge: GroupingKnowledge,
    user_seed_for: Callable[[str, str], UserSeed | None],
    p8_run_call: Callable[..., object] | None,
    embeddings,
    created_at: str,
) -> GroupingResult:
    """One subject, through P9's five stages. Decides nothing it was not given."""
    def _result(**overrides) -> GroupingResult:
        values = dict(
            subject_file_id=file_id, subject_content_hash=content_hash,
            seeds=(), neighborhood=None, graph=None, stop_rule_outcome=None,
            group=None, memberships=(), dossier=None, model_result=None,
            not_implemented_reason=None,
        )
        values.update(overrides)
        return GroupingResult(**values)

    seeds = seeds_for_file(
        conn, file_id=file_id, content_hash=content_hash,
        user_seed_for=user_seed_for)
    if not seeds:
        # A filename is not a fact. A file P6 holds nothing direct about has no
        # legal starting point, and inventing one is where a group with no
        # evidence comes from.
        return _result()

    seed = seeds[0]
    _prepare_embeddings(
        conn, embeddings=embeddings, seed=seed, limits=limits,
        created_at=created_at)

    neighborhood = retrieve_neighbors(
        conn, seed=seed, limits=limits, knowledge=knowledge.retrieval,
        embeddings_enabled=isinstance(embeddings, EmbeddingsOn))

    group = _group_for(
        seed, group_id=f"group:{file_id}:{seed.seed_kind}", created_at=created_at)
    graph = build_graph(
        group_id=group.group_id, neighborhood=neighborhood, limits=limits,
        duplicate_or_version=knowledge.duplicate_or_version,
        created_at=created_at)

    outcome = evaluate_stop_rules(
        conn, graph, limits=limits, conflicts_for=knowledge.conflicts_for,
        basis_key=group_basis_key(group),
        # The seed's own fact is an anchor when P6 validated it. A group of one
        # is a group whose only anchor is itself.
        seed_anchors=bool(seed.observation_key and seed.reliability_state))
    if outcome is not None:
        # Before the dossier and before the call: a group that cannot form
        # should not cost either one.
        return _result(
            seeds=seeds, neighborhood=neighborhood, graph=graph,
            stop_rule_outcome=outcome, group=group)

    record_group(conn, group)
    membership = _self_membership(group, seed, created_at=created_at)
    record_membership(conn, membership)

    dossier = assemble_group_dossier(
        conn, group=group, graph=graph, limits=limits,
        active_schema_for=knowledge.active_schema_for,
        signal_evaluator_for=knowledge.signal_evaluator_for,
        classification_store=knowledge.classification_store,
        conflicts=(), created_at=created_at)
    if isinstance(dossier, DossierRefused):
        return _result(
            seeds=seeds, neighborhood=neighborhood, graph=graph, group=group,
            memberships=(membership,),
            not_implemented_reason=dossier.reason,
            omissions=dossier.withheld)

    if p8_run_call is None:
        return _result(
            seeds=seeds, neighborhood=neighborhood, graph=graph, group=group,
            memberships=(membership,), dossier=dossier,
            not_implemented_reason=NO_MODEL_CONFIGURED)

    from grouping.p8_seam import apply_p8_verdict, build_dossier_request

    request = build_dossier_request(
        dossier,
        model_target=knowledge.retrieval.embedding_identity,
        prompt_template_id="template.grouping",
        prompt_fingerprint=dossier.dossier_fingerprint,
        max_dossier_tokens=limits.max_dossier_tokens)
    outcome_from_model = p8_run_call(conn, request)
    if outcome_from_model is None:
        return _result(
            seeds=seeds, neighborhood=neighborhood, graph=graph, group=group,
            memberships=(membership,), dossier=dossier,
            not_implemented_reason=NO_MODEL_CONFIGURED)
    decision = apply_p8_verdict(
        conn, group=group, dossier=dossier, result=outcome_from_model,
        plan_version_id=plan_version_id, created_at=created_at)
    return _result(
        seeds=seeds, neighborhood=neighborhood, graph=graph, group=group,
        memberships=(membership,), dossier=dossier, model_result=decision)
