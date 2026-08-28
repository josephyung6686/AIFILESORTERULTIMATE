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

That sentence is about a candidate that NEEDS a judgement -- one BELOW §4.9's
independent-anchor bar. A group at or above it has been decided by a rule, not by
an interpretation: several files independently state the same fact P6 already
validated. `naming.engine_proposal` is where that is written down, between the
stop rules and `record_group`, and `label_source = engine` records who said it.
Every group below the bar still comes out of here with `coherence_verdict`,
`group_category` and `display_label` all absent, and so does every group whose
anchor facts state no value.
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
from grouping.graph import (
    LocalEvidenceGraph,
    build_graph,
    evaluate_stop_rules,
    meets_support_bar,
)
from grouping.learning import group_basis_key
from grouping.naming import engine_proposal
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
    SUPPORTED,
)

#: What a deterministic run says about a judgement it did not make. Named rather
#: than left blank: a candidate with no reason reads as a candidate nobody looked
#: at, and this one was looked at and deliberately not decided.
NO_MODEL_CONFIGURED: str = "no_model_call_configured"


@dataclass(frozen=True)
class ModelCallAuthorities:
    """`run_call`'s five keyword arguments, as P9 receives them.

    Every annotation is `object` on purpose. `CallDependencies` lives in
    `llm_harness.harness` and the release gate in `privacy.gate`, and
    `test_p9_never_imports_run_calls_neighbours` fails the build if any file under
    `src/grouping/` imports either -- an import is a second route to a model. P9
    constructs neither, reads no field of either, and does not know their types;
    it forwards them under `run_call`'s own keywords.

    The first five FIELD NAMES are `run_call`'s keyword names exactly, and a
    conformance test binds them to the live signature. `pipeline.py` called
    `p8_run_call(conn, request)` for as long as this bundle did not exist, which is
    a `TypeError` on the first real call and a green suite behind a `**kwargs` spy.

    `model_target` is the SIXTH, and it is deliberately not a `run_call` keyword:
    it goes into `ModelCallRequest.model_target`, which is P7's, and the gate reads
    `.locality` off it to decide whether bytes may leave the machine
    (`privacy/gate.py:133`). P9 cannot construct one -- `ModelTarget` lives in
    `privacy.release` and the boundary test forbids importing it -- so it arrives
    here with the rest. The conformance test names it as the one exception rather
    than relaxing the equality, so a seventh cannot be added silently.
    """

    gate: object
    model_client: object
    prompt: object
    validation_dependencies: object
    observed_at: object
    model_target: object


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


def _group_for(seed: Seed, *, group_id: str, state: str,
               conflicts: Sequence[object], created_at: str) -> Group:
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
        # Blank on purpose, and blank ONLY here. This builder runs before the stop
        # rules, so it cannot know whether the group is going to form at all, and a
        # verdict written on a group SR4 is about to destroy would be a claim about
        # material that never became a group. `naming.engine_proposal` fills these
        # in after `evaluate_stop_rules` returns nothing, which is the first moment
        # anything true can be said about them.
        coherence_verdict=None,
        coherence_citations=(),
        group_category=None,
        display_label=None,
        label_source=None,
        # The oracle's conflicts over this graph. Hardcoded `()` meant a group SR4
        # destroyed came back claiming no conflict, with the reason surviving only
        # as a formatted string in `stop_rule_outcome.evidence_refs`.
        conflicts=tuple(conflicts),
        stop_rule_hits=(),
        state=state,
        sensitivity_state=NO_SENSITIVITY,
        dossier_id=None,
        llm_response_ref=None,
        validation_verdict_ref=None,
        created_by=RULES,
        created_at=created_at,
    )


def _self_membership(group: Group, seed: Seed, *,
                     conflicts: Sequence[object], created_at: str) -> Membership:
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
        # The conflicts naming the seed's own file. Empty in every path reachable
        # today because SR4 stops the group before this line whenever the oracle
        # returns anything at all -- but taken from the oracle rather than
        # hardcoded, so it stays correct if SR4 ever narrows to a subset of kinds.
        conflicts=tuple(
            conflict for conflict in conflicts
            if seed.file_id in getattr(conflict, "file_ids", ())),
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
    p8_authorities: ModelCallAuthorities | None,
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

    group_id = f"group:{file_id}:{seed.seed_kind}"
    graph = build_graph(
        group_id=group_id, neighborhood=neighborhood, limits=limits,
        duplicate_or_version=knowledge.duplicate_or_version,
        created_at=created_at)

    # The seed's own fact is an anchor when P6 validated it. A group of one is a
    # group whose only anchor is itself.
    seed_anchors = bool(seed.observation_key and seed.reliability_state)
    # §4.9's minimum INDEPENDENT anchor count, and it decides `supported` rather
    # than existence -- `graph.py:265`: "Not a stop rule, and deliberately separate
    # from SR1." SR1 is zero anchors and stops the group forming; this bar leaves a
    # group below it standing as a candidate waiting for confirmation.
    # `minimum_independent_anchors` is injected with no default (`config.py:44`),
    # so nothing here invents a threshold.
    # One call to the injected oracle, and every record below is built from its
    # answer. The group, the self-membership and the dossier each used to hardcode
    # `conflicts=()`, which is the defect the frozen contract added the field to
    # fix, reintroduced from P9's side.
    conflicts = tuple(knowledge.conflicts_for(tuple(graph.file_ids)))

    group = _group_for(
        seed, group_id=group_id, created_at=created_at, conflicts=conflicts,
        state=SUPPORTED if meets_support_bar(
            graph, limits=limits, seed_anchors=seed_anchors) else CANDIDATE)

    outcome = evaluate_stop_rules(
        conn, graph, limits=limits, conflicts_for=lambda _files: conflicts,
        basis_key=group_basis_key(group),
        seed_anchors=seed_anchors)
    if outcome is not None:
        # Before the dossier and before the call: a group that cannot form
        # should not cost either one.
        return _result(
            seeds=seeds, neighborhood=neighborhood, graph=graph,
            stop_rule_outcome=outcome, group=group)

    # No stop rule fired, so the group forms -- and this is the one place P9 knows
    # that AND has the anchor facts in hand. `engine_proposal` writes §4.9's own
    # answer: a group at the independent-anchor bar is `coherent`, named by the
    # values its files actually state, and categorised by the single domain those
    # fields belong to -- or by none, when they belong to several. A group below
    # the bar comes back untouched and is recorded with all four fields still
    # blank, which is the SPEC's `deferred` row and an honest thing for a
    # deployment with no model to show.
    group = engine_proposal(group)
    record_group(conn, group)
    membership = _self_membership(
        group, seed, conflicts=conflicts, created_at=created_at)
    record_membership(conn, membership)

    dossier = assemble_group_dossier(
        conn, group=group, graph=graph, limits=limits,
        active_schema_for=knowledge.active_schema_for,
        signal_evaluator_for=knowledge.signal_evaluator_for,
        classification_store=knowledge.classification_store,
        # Empty in every path reachable today for the same reason as the
        # self-membership above: SR4 has already returned. Wired rather than
        # hardcoded so the dossier does not need a second edit if it narrows.
        conflicts=conflicts, created_at=created_at)
    if isinstance(dossier, DossierRefused):
        return _result(
            seeds=seeds, neighborhood=neighborhood, graph=graph, group=group,
            memberships=(membership,),
            not_implemented_reason=dossier.reason,
            omissions=dossier.withheld)

    if p8_run_call is None or p8_authorities is None:
        # "missing P8/config -> fail closed" (connection contract, seam ledger).
        # A bundle-less run is a deterministic run, not an exception: P9 calling a
        # model it was given no authority for is the failure this returns instead.
        # The bundle is a REQUIRED parameter rather than a defaulted one so that
        # forgetting it is a `TypeError` at the call site, while a deployment with
        # no model says so by passing `None`.
        return _result(
            seeds=seeds, neighborhood=neighborhood, graph=graph, group=group,
            memberships=(membership,), dossier=dossier,
            not_implemented_reason=NO_MODEL_CONFIGURED)

    from grouping.p8_seam import (
        apply_p8_verdict,
        build_dossier_request,
        prompt_fingerprint_for,
    )

    request = build_dossier_request(
        dossier,
        # P7's, not retrieval's. This read `knowledge.retrieval.embedding_identity`
        # -- the local vector model channel 6 retrieves with, `(scope, model_id,
        # model_version)`. The gate reads `.locality` off this field to decide
        # whether bytes may leave the machine, and an embedding identity has none,
        # so the gate raised `AttributeError` before deciding anything (and with
        # retrieval configured off it was plain `None`). `ModelCallRequest`
        # annotates the field `ModelTarget` and checks nothing, which is how a
        # value from another subsystem reached the gate at all. `embedding_identity`
        # was never a model target; it was the only identity `knowledge` had.
        model_target=p8_authorities.model_target,
        prompt_template_id="template.grouping",
        # P7 binds the release to this fingerprint and the transport recomputes it
        # from the prompt it sends, so the dossier's own content address bound the
        # release to something that could never match -- and the mismatch is raised
        # AFTER the release is spent. `prompt_fingerprint_for` is in `p8_seam`
        # because that is the only file under `src/grouping/` allowed to know P8.
        prompt_fingerprint=prompt_fingerprint_for(
            p8_authorities.prompt, absent=dossier.dossier_fingerprint),
        max_dossier_tokens=limits.max_dossier_tokens)
    outcome_from_model = p8_run_call(
        conn, request,
        gate=p8_authorities.gate,
        model_client=p8_authorities.model_client,
        prompt=p8_authorities.prompt,
        validation_dependencies=p8_authorities.validation_dependencies,
        observed_at=p8_authorities.observed_at,
    )
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
