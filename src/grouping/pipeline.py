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

import dataclasses
import hashlib
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
    anchoring_files,
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
from grouping.store import (
    RecordAbsent,
    current_group,
    live_memberships_of_file,
    record_edges,
    record_group,
    record_membership,
)
from grouping.vocabulary import (
    CANDIDATE,
    DIRECT_ANCHOR,
    EXCLUDED,
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


def group_address(seed: Seed) -> str:
    """The address of the group this seed starts. An IDENTITY, not a file.

    `store.record_group`: "A group id derived from its seed is an address, so a
    rerun over unchanged evidence is the same group and not a conflict." It was
    derived from the seed's FILE -- `group:{file_id}:{seed_kind}` -- and `65` §4.2
    records what that cost on the first run over a real folder: four coursework
    files each stating `subject = PHYS1401` minted four one-file groups carrying
    the same label, the `Coursework` branch was proposed and left empty, and all
    four placements abstained.

    A fact-backed seed's claim is not about its file. It is `subject = PHYS1401`,
    and every file that states it is stating the SAME thing, so the address is
    that claim. `65` §4.2: "The strategy is not wrong in general: a strongly
    self-identifying file should be able to stand alone when nothing else shares
    its identity. The defect is that the strategy does not check whether anything
    else resolved to the same identity before minting a singleton for it."

    A `user-created-starting-point` keeps the file address, and that is not an
    inconsistency: `seeds.py` -- "user intent enters through `user_seed_for`,
    where it carries a decision the user actually made about *this group*". The
    user said THIS FILE starts a group, and two users' two decisions about two
    files are two groups even when the files look alike.

    The value is digested rather than spelled into the id because a field value is
    arbitrary user text -- a course code, a client name, a filename with a colon
    in it -- and an id is parsed by `test_p10_templates` and read in logs. The
    field key and the seed kind stay in plain sight; `anchor_facts` carries the
    value itself, which is where a reader should be reading it from anyway.
    """
    if not (seed.field_key and seed.value):
        return f"group:{seed.file_id}:{seed.seed_kind}"
    digest = hashlib.sha256(
        "\x1f".join((seed.field_key, seed.value)).encode("utf-8"),
    ).hexdigest()
    return f"group:{seed.field_key}:{digest}:{seed.seed_kind}"


def _group_for(seed: Seed, *, group_id: str, state: str,
               conflicts: Sequence[object], anchor_file_ids: frozenset[str],
               created_at: str) -> Group:
    # Every file the graph says states this value DIRECTLY, not just the seed.
    # The SPEC's own definition of `anchor_count` is "number of files that
    # INDEPENDENTLY state the basis value", and a one-tuple of the seed's own file
    # made that number 1 for a group of four -- understating to P10 and P11 the
    # very support the group was formed on.
    facts = (
        (AnchorFact(
            field=seed.field_key, value=seed.value,
            file_ids=tuple(sorted(anchor_file_ids or {seed.file_id})),
            reliability_state=seed.reliability_state,
            observation_key=seed.observation_key),)
        if seed.field_key and seed.value and seed.observation_key
        and seed.reliability_state
        else ()
    )
    anchor_count = len(facts[0].file_ids) if facts else 0
    return Group(
        group_id=group_id,
        seed_ref=f"{seed.file_id}:{seed.content_hash}",
        seed_kind=seed.seed_kind,
        proposed_basis=(
            f"{seed.field_key}={seed.value}" if seed.field_key
            else seed.basis or seed.seed_kind
        ),
        anchor_facts=facts,
        pre_model_signals={"anchor_count": anchor_count},
        anchor_count=anchor_count,
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


def _standing_group(conn: sqlite3.Connection, group_id: str) -> Group | None:
    """The group already recorded at this address, or None.

    `record_group` would answer this too, but only by raising: it refuses a second
    row under one id whose content differs, and two files that legitimately share
    an identity DO differ in `seed_ref` -- the group started from whichever one the
    corpus loop reached first. That difference is not a conflict, it is the join.
    """
    try:
        return current_group(conn, group_id)
    except RecordAbsent:
        return None


def _self_membership(group: Group, seed: Seed, *,
                     conflicts: Sequence[object], created_at: str) -> Membership:
    """This file's own membership. Its own direct fact is what makes it one.

    It was named for the group of one it used to be the only inhabitant of. Since
    `65` §4.2 a group is addressed by the identity its seed states, so this is the
    record written once per file that states that identity -- four of them for a
    course with four files -- and the name now describes whose membership it is
    rather than how many there are.
    """
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


#: Said on the superseded row, so a later reader has the account §8.2 keeps
#: history for. Plain words, because P13 and the audit log both show it to a
#: person: what changed is the evidence, not P9's opinion of the file.
RETRACTED_ANCHOR_REASON: str = (
    "the fact this membership was built on is no longer one of the file's "
    "anchors -- it was retracted or superseded, and a membership may not "
    "outlive the evidence that produced it"
)


def _retract_unsupported_memberships(
    conn: sqlite3.Connection, *, file_id: str, content_hash: str,
    seeds: Sequence[Seed], created_at: str,
) -> tuple[str, ...]:
    """Retire the memberships this file's CURRENT facts no longer support.

    §8.7 lets a person say a conclusion about their file is wrong. P6 records it
    and `read_surface.proposal_eligible` stops returning the claim, so
    `seeds_for_file` above genuinely does not propose the group again -- and the
    membership written on the earlier run went on standing, because
    `memberships_for_group` reads by `group_id` and asks nothing about the
    evidence underneath. The person was shown their file in the folder they had
    just objected to. P11 SPEC states the rule they were owed: "a rejected fact
    cannot support a placement, so a record resting on one would be a
    contradiction rather than a low-confidence decision."

    **Evidence, not addresses.** The tempting version compares the group ids this
    file's seeds address now against the groups it is in, and sweeps the
    difference. That misses the copy: a review step that carries a membership
    onto the group it merged into writes a SECOND row, under a group no seed ever
    addresses, citing the same withdrawn observation. Reading the citation
    catches both, and it is the thing that actually went stale.

    **`direct-anchor` only.** That basis asserts one thing -- this file's own
    validated fact puts it here -- and it is the only claim a retracted fact can
    falsify by itself. A `context-supported` member is one a model placed for
    other reasons and a `user-attached` one is a decision a person made; unmaking
    either because a fact moved would be P9 overruling a judgement it did not
    make. Those belong to §4.9's review, not here.

    **All of its fact supports, not any.** A membership with a second anchoring
    fact still standing keeps it. Only one that has lost every fact it cited has
    nothing left to say why the file belongs.

    Superseded, never deleted, and the successor keeps the original `support`:
    §8.7 requires a rejected membership be stored WITH the evidence that produced
    it, or the system "will repeatedly resurface the same attractive but
    incorrect grouping".
    """
    anchors = {seed.observation_key for seed in seeds if seed.observation_key}
    retired: list[str] = []
    for membership in live_memberships_of_file(
            conn, file_id=file_id, content_hash=content_hash):
        if membership.basis != DIRECT_ANCHOR or membership.decision != INCLUDED:
            continue
        cited = {support.observation_key for support in membership.support
                 if support.support_kind == SHARED_VALIDATED_FACT
                 and support.observation_key}
        if not cited or cited & anchors:
            continue
        retracted = dataclasses.replace(
            membership,
            membership_id=f"{membership.membership_id}:retracted",
            decision=EXCLUDED,
            # RULES, and not USER. A person's rejection is the usual cause and it
            # is recorded as theirs where they made it, on P6's fact. What P9
            # observed is narrower and is all it may claim: re-reading this
            # file's facts, the anchor this row cites is not among them. An
            # improved extractor withdrawing a value reaches this line by the
            # same route, and writing USER there would put a person's name on a
            # decision they did not make.
            decision_source=RULES,
            created_at=created_at,
            supersedes=membership.membership_id,
            superseded_by=None,
            supersede_reason=RETRACTED_ANCHOR_REASON)
        record_membership(conn, retracted)
        retired.append(retracted.membership_id)
    return tuple(retired)


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
    # BEFORE the empty-seed return, and not after it. A file whose only fact was
    # the one the person retracted has no seeds at all, which is exactly the case
    # where every membership it has is built on evidence that is gone -- and the
    # early return below would have carried all of them into the next plan.
    _retract_unsupported_memberships(
        conn, file_id=file_id, content_hash=content_hash, seeds=seeds,
        created_at=created_at)
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

    group_id = group_address(seed)
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
        anchor_file_ids=anchoring_files(graph, seed_anchors=seed_anchors),
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
    # `65` §4.2's other half. A group is addressed by the identity its seed
    # states, so a second file stating the SAME identity finds the group already
    # standing and JOINS it -- one course, one group, four memberships -- instead
    # of minting a second group under a second address.
    #
    # The standing group is taken as recorded and is not re-judged here. Its
    # verdict was written once, from the graph that already contained these files;
    # re-asking would spend a second dossier and a second model call to answer a
    # question P9 has answered, and could return a different verdict for the same
    # material depending on which file the corpus loop reached first. Whether a
    # LATER member should reopen coherence is §4.5's question and is not this fix.
    # The graph is EVIDENCE, and it was computed and dropped: `record_edges` had
    # no caller in `src/` at all. `66` §3 makes "also related to" a state a person
    # is shown -- "a relationship, not as uncertainty" -- and a relationship whose
    # typed edge exists only in memory cannot be shown, reviewed or replayed.
    # Written here, after the stop rules, so a graph belonging to a group that
    # never formed is not stored as though it did. Edge ids are content-derived
    # and the writer ignores a repeat, so a join and a rerun add nothing.
    record_edges(conn, group_id, graph.edges, created_at=created_at)

    standing = _standing_group(conn, group_id)
    if standing is not None and standing.seed_ref != group.seed_ref:
        membership = _self_membership(
            standing, seed, conflicts=conflicts, created_at=created_at)
        record_membership(conn, membership)
        return _result(
            seeds=seeds, neighborhood=neighborhood, graph=graph, group=standing,
            memberships=(membership,))

    if standing is not None:
        # A RERUN over the seed's own group, which is a different thing again. The
        # recorded row is taken as it stands and is not rewritten, because the
        # anchor set is a fact about the corpus AS SCANNED and scanning more of the
        # corpus later would otherwise rewrite a group's evidence under it. §8.2
        # supersedes rather than overwrites, and a supersession needs a new id --
        # which an address cannot have. Whether a widened anchor set should mint a
        # superseding group is a real §8.2 question and is NOT answered here.
        group = standing
    else:
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
