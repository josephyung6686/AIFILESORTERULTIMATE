"""§6.12's nine steps, in §6.12's order, and §7's separate stage after them.

The design's own list (`planning/01-product-design-structured.md:1295-1306`) is the
spine, and `STEPS` names it so the shape is checkable against the design rather
than against this file. Steps 1 and 2 belong to P10 and step 8 to P8; this module
orchestrates 3 through 7 and produces 9.

Every injection arrives on `PipelineInputs` and none has a default. A run with no
model injections is a legal run -- §6.6 decides a unique direct match with zero
model calls -- and a run with no support policy is not, because §6.10's thresholds
are unsettled by the design and guessing one would place files under a bar nobody
chose.

The order inside `place_file` is not arbitrary. §8.4's privacy gate is consulted
before any dossier could be assembled, and §8.7's learning store is consulted
before `place` is emitted. Both are preconditions rather than filters, and moving
either later would make a spend or a placement happen first.

**Three questions P11 cannot answer from a `P8Verdict` are injected**, and each
one is injected because the verdict carries a `claim_ref` and not the answer:

* `chosen_node_of` -- which of P11's candidates a Site C verdict chose;
* `residual_action_of` -- which of §7.7's eight actions a Site D verdict carried,
  and its target. P8 validates `payload["action"]` against `RESIDUAL_ACTIONS`
  (`placement_validation.py:311-312`) but the verdict's own `disposition` is
  P8's coarser vocabulary: `residual_destination` cannot say whether the model
  chose a residual destination or a broad parent, and `return_to_placement`
  cannot say whether it named a confirmed group or an accepted packet -- which is
  exactly what `ReturnTarget.kind` has to record. The caller holds the response
  and hands back the pair;
* `sensitivity_policy` -- P7's answer about this release.

**P11 never calls `record_cd_verdict`.** `harness.py:245-253` calls it for every C
and D verdict and `placement_validation.py:614` does the same on revalidation; a
second call would write the row twice. What P11 owes is the input that call needs
-- `DossierRequest.evidence_snapshot_id`, which `run_call` refuses a C or D
request without BEFORE the spend -- and `_judge_with_model` mints it.
"""
from __future__ import annotations

import dataclasses
import sqlite3
from dataclasses import dataclass
from decimal import Decimal

from database_agent.supersede import mark_superseded
from llm_harness import P8Verdict, Refusal
from llm_harness.records import DossierRequest
from llm_harness.vocabulary import (
    C_PLACEMENT, D_RESIDUAL, REJECT as P8_REJECT,
    SEVERAL_LEGAL_NODES_PLAUSIBLE, USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW,
)

from grouping.vocabulary import NOT_FLAGGED

from placement import events as placement_events
from placement.config import PlacementLimits, SupportPolicy, require_policy
from placement.graph import build_node_local_graph
from placement.groups import (
    AcceptedGroup, ExcludedOutlier, GroupPlan, accepted_group_as_of,
    confirm_shared_parent, excluded_outlier_for, resolve_multi_home,
)
from placement.index import entry_for, legal_node_ids
from placement.learning import basis_key_for, suppressed_nodes
from placement.p8_seam import (
    call_placement, evidence_snapshot_id_for, placement_authorities,
    residual_authorities, site_dependencies, to_p8_conflicts, transcribe,
)
from placement.privacy import (
    automatic_move_permitted_for, is_unclassified, may_assemble_dossier,
    privacy_state_for, review_policy_for,
)
from placement.records import (
    Ask, DecisionDepth, Destination, PlacementDecision, ResidualContext,
    ReturnTarget, Subject, TwoCondition,
)
from placement.residual import (
    ACTION_OUTCOME, ResidualSet, SetDecisionRequired, check_return_cycle,
    link_return, model_calls_permitted, outcome_for_action,
    require_model_call_permitted, require_set_decision, surface_residual_sets,
)
from placement.retrieval import Retrieval, retrieve
from placement.scoring import assess, needs_model_call
from placement.stage_output import emit_retrieval_stage, emit_scoring_stage
from placement.store import current_decision, record_decision, subject_ref_of
from placement.vocabulary import (
    ABSTAIN, ABSTAIN_NO_SUPPORTED_DESTINATION, ASK_USER, BUDGET_DEFERRED,
    CONTEXT_SUPPORTED, CONTEXT_SUPPORTED_GROUP_MATCH, DIRECT, EXISTING, FILE,
    MARGIN_TRUE_VACUOUS, MARK_STATE, NO_SHARED_BRANCH,
    MULTIPLE_SUPPORTED_HOMES, NO_SUPPORTED_DESTINATION, PLACE, PLACEMENT,
    PRIVACY_BLOCKED, RESIDUAL,
    RETURN_TO_PLACEMENT, SHARED_MATERIAL, SHARED_MATERIAL_DECISION, WEAK,
)

#: §6.12's nine, in §6.12's order. Steps 1-2 are P10's and step 8 is P8's; naming
#: them anyway is what makes the pipeline auditable against the design.
STEPS: tuple[str, ...] = (
    "freeze_approved_tree",                     # 1, P10
    "profile_each_node",                        # 2, P10
    "retrieve_legal_candidates",                # 3
    "build_local_graph",                        # 4
    "suppress_impossible_nodes",                # 5
    "identify_child_parent_fallback_or_none",   # 6
    "judge_bounded_ambiguity",                  # 7
    "validate_evidence_and_constraints",        # 8, P8
    "reviewable_plan_of_placements",            # 9
)


def _without_superseded_ancestors(conn: sqlite3.Connection, retrieval: Retrieval,
                                  *, plan_version: str) -> Retrieval:
    """Step 6's first half: an ANCESTOR of another candidate is not a rival.

    A nested tree means a file's facts match its whole chain. Given
    `Coursework/Columbia/PHYS1401/Homework`, a file settling school, subject and
    work_type matches all three folders, and P11 scored them as competitors: they
    tied at 0.714 apiece, `assess` returned `multiple_supported_homes`, and the
    tie went to a model that offline mode forbids -- so the file abstained
    `privacy_blocked`. Four personas, four one-folder trees, nothing ever filed.

    They are not multiple homes. Filing something in `Columbia/PHYS1401/Homework`
    files it in `Columbia` and in `PHYS1401` too; that is what nesting MEANS, and
    §6.7 asks for the deepest node the evidence actually supports. So a candidate
    that is a strict ancestor of another candidate is dropped -- not judged, not
    rejected, superseded by a more specific form of itself.

    **Only strict ancestors, and only within one chain.** Two candidates on
    different branches are genuinely two homes and stay two homes: that is the
    §6.10 ambiguity the model call exists for, and collapsing it would be P11
    picking an institution for the user, which `00` forbids in as many words.

    **The broad-parent case survives.** A node is a candidate only because its
    expected values matched, so the deepest surviving candidate is supported by
    construction. Where the tree stops shallower than the evidence reaches, the
    parent IS the deepest candidate and is what this returns -- which is the case
    `DecisionDepth.unsupported_levels` was written for.
    """
    node_ids = {candidate.node_id for candidate in retrieval.candidates}
    if len(node_ids) < 2:
        return retrieval

    superseded: set[str] = set()
    for node_id in node_ids:
        cursor = entry_for(conn, plan_version=plan_version,
                           node_id=node_id).parent_node_id
        # Walk to the root marking every ancestor that is ALSO a candidate. A
        # cycle cannot occur -- `build_destination_index` refuses a node whose
        # parent the frozen tree does not contain -- and the walk is bounded by
        # the tree's depth, which §7.2 caps.
        while cursor is not None:
            if cursor in node_ids:
                superseded.add(cursor)
            cursor = entry_for(conn, plan_version=plan_version,
                               node_id=cursor).parent_node_id
    if not superseded:
        return retrieval

    return Retrieval(
        subject_ref=retrieval.subject_ref,
        plan_version=retrieval.plan_version,
        candidates=tuple(candidate for candidate in retrieval.candidates
                         if candidate.node_id not in superseded),
        conflicts=retrieval.conflicts,
        semantic_only_node_ids=retrieval.semantic_only_node_ids,
    )


def _without_duplicated_proposals(conn: sqlite3.Connection, retrieval: Retrieval,
                                  *, plan_version: str) -> Retrieval:
    """Step 6's second half: a vaguer COPY of the person's folder is not a rival.

    `00`:100 says a folder the person made "should be treated as a strong
    expression of user intent". Once those folders are adopted, the engine's own
    proposal for the same material stands beside them -- `Uni/CHEM1500` and
    `Coursework/CHEM1500`, the same name twice on one screen -- and the two tie at
    every file. §6.10 sends a tie to a model, offline mode forbids the call, and
    the file abstains `privacy_blocked`. Measured: six files that had been placing
    fine went back to abstaining the day folders were adopted.

    This is not P11 picking between two homes. The rule is the ancestor rule's
    own -- superseded by a more specific form of itself -- and the specificity is
    measured, not assumed: the proposal is dropped only when the person's folder
    expects EVERYTHING it expects. `Uni/CHEM1500`'s files agree on the term as
    well as the subject, so it is strictly the better-supported destination, and
    the proposal is a vaguer copy of a folder that already exists.

    **Three refusals hold the rule to that.**

    * A proposal expecting NOTHING is never dropped. An empty set is a subset of
      everything, so without this any adopted folder would supersede every
      unexpectant proposal in the tree -- the person's `Downloads` swallowing a
      branch it has no relationship with.
    * The person's folder must expect a SUPERSET, not merely overlap. Two folders
      that share one field and differ on another are genuinely two homes, and
      §6.10's ambiguity is what the model call exists for.
    * Only a PROPOSAL is dropped. Two of the person's own folders competing is
      their business, and resolving it here would be the product overruling one
      of their decisions with another.
    """
    entries = {candidate.node_id: entry_for(conn, plan_version=plan_version,
                                            node_id=candidate.node_id)
               for candidate in retrieval.candidates}
    if len(entries) < 2:
        return retrieval

    adopted = [entry for entry in entries.values()
               if entry.node_type == EXISTING]
    if not adopted:
        return retrieval

    superseded = {
        node_id for node_id, entry in entries.items()
        if entry.node_type != EXISTING and entry.expected_values
        and any(set(entry.expected_values) <= set(folder.expected_values)
                for folder in adopted)}
    if not superseded:
        return retrieval

    return Retrieval(
        subject_ref=retrieval.subject_ref,
        plan_version=retrieval.plan_version,
        candidates=tuple(candidate for candidate in retrieval.candidates
                         if candidate.node_id not in superseded),
        conflicts=retrieval.conflicts,
        semantic_only_node_ids=retrieval.semantic_only_node_ids,
    )


class ModelJudgementUnavailable(RuntimeError):
    """`run_call` came back with something that is not a verdict.

    P8 declares five return types and only one of them is a judgement.
    `Refusal` is P7 denying the release, which IS §8.4's `privacy_blocked` and is
    recorded as that. The other three -- `NeedsConsent`, `ValidationUnavailable`
    and `CallFailed` -- are not judgements about evidence, and §6.10's abstention
    reasons are a closed set with no member for "the call did not happen". Naming
    one anyway would record a conclusion about the file that nothing reached, so
    this raises and the caller decides. B2 says the same of `NeedsConsent`: it
    writes no P11 decision and no P2 row.
    """


class ResidualActionUnavailable(RuntimeError):
    """A Site D verdict arrived with no way to recover §7.7's action."""


class ScanBudgetRequired(RuntimeError):
    """A model call was about to be made with no scan to charge it to.

    §8.6's two spend ceilings are per SCAN -- calls per thousand files, cost per
    scan -- so they need the scan's identity and its file count, which belong to
    the scan and not to P11. P11 supplies the ceilings; the caller supplies what
    they are ceilings ON. Absent, `run_call` would reserve against nothing and
    the run would spend without a bound, which is the state §8.6 exists to make
    impossible.
    """


@dataclass(frozen=True)
class P2Run:
    """P2's three coordinates for one measured run, or nothing at all.

    They travel together because `emit_scoring_stage` needs all three and a
    partial injection would silently emit no row -- a run that looks measured and
    is not. `eval_harness` measures replays, shadows and adversarial runs, so an
    ordinary run supplies no `P2Run` and writes no stage output; that is a state,
    not a gap.
    """

    run_id: str
    version_tuple_ref: str
    upstream_stage_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("run_id", "version_tuple_ref"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"{name} is required on a P2Run; half an injection emits no "
                    "row at all and makes an unmeasured run look measured"
                )
        object.__setattr__(self, "upstream_stage_refs",
                           tuple(self.upstream_stage_refs))


@dataclass(frozen=True)
class PipelineInputs:
    plan_version: str
    tree: object
    policy: SupportPolicy
    limits: PlacementLimits
    partition: object
    ask_or_abstain: object
    max_return_cycles: int | None
    gate: object
    model_client: object
    prompt: object
    call_dependencies: object
    model_call_request: object
    chosen_node_of: object
    residual_action_of: object
    sensitivity_policy: object
    p2: P2Run | None

    def __post_init__(self) -> None:
        require_policy(self.policy)
        if not isinstance(self.limits, PlacementLimits):
            raise ValueError(
                "the pipeline runs under P1's seven ceilings and reads them "
                "through `placement.config.placement_limits`; a run with no "
                "limits is a run under a bound nobody chose"
            )
        if self.p2 is not None and not isinstance(self.p2, P2Run):
            raise ValueError("`p2` is a P2Run or None; P11 assembles neither half")

    def model_path_available(self) -> bool:
        """Whether step 7 can run at all. A deterministic-only run is legal.

        §6.6 decides a unique direct match with zero model calls, so a run with
        no model injections is a correct run and must not look like a failure.
        What is NOT legal is discovering the injections are missing after a
        dossier has been assembled, which is why this is asked before one is.
        """
        return None not in (self.gate, self.model_client, self.prompt,
                            self.call_dependencies, self.model_call_request,
                            self.chosen_node_of, self.sensitivity_policy)


@dataclass(frozen=True)
class CorpusResult:
    """§6.12 step 9 -- "a reviewable plan of exact placements, shallow placements,
    scoped fallbacks, and abstentions" -- plus what §7 then did with the rest.

    One object, so a review surface does not have to run the pipeline twice to
    learn what happened, and so `unplaced_file_ids` is a fact the run produced
    rather than something the caller re-derives by filtering.
    """

    decisions: tuple[PlacementDecision, ...]
    group_plans: tuple[GroupPlan, ...]
    residual_sets: tuple[ResidualSet, ...]
    unplaced_file_ids: tuple[str, ...]
    #: Every subject the run knew about, by file id -- the ones handed in and the
    #: members P9 supplied. `review_residual_sets` needs them and re-deriving a
    #: content hash from P1 afterwards would be a second copy of P1's identity.
    subjects: dict


# --- identity and the supersede link ----------------------------------------------


def _identity(conn: sqlite3.Connection, *, plan_version: str, subject_ref: str,
              observed_at: str, suffix: str = "") -> tuple[str, str | None]:
    """This decision's id, and the live decision it revises.

    `one_current_placement_decision` is a partial unique index over unsuperseded
    rows, so a second live decision about one subject is refused by SQLite. Every
    writer here therefore links rather than remembering to: §8.2's rule is that a
    revised decision is a NEW row whose `supersedes` names the prior one, and the
    prior row keeps its evidence.

    The id gains a counter only when the plain one is already taken, because
    `mark_superseded` refuses a self-supersede and a fixed clock would otherwise
    produce the same id twice for one subject.
    """
    live = current_decision(conn, plan_version=plan_version,
                            subject_ref=subject_ref)
    taken = {row["record_id"] for row in conn.execute(
        "SELECT record_id FROM placement_decisions WHERE plan_version = ? AND "
        "subject_ref = ?", (plan_version, subject_ref))}
    decision_id = f"{plan_version}:{subject_ref}:{observed_at}{suffix}"
    if decision_id in taken:
        decision_id = f"{decision_id}#{len(taken)}"
    return decision_id, (live.decision_id if live is not None else None)


def _write(conn: sqlite3.Connection, decision: PlacementDecision, *, inputs,
           reason: str, component_version: str, observed_at: str) -> PlacementDecision:
    """Append the decision, then measure it. One place, so nothing is unmeasured."""
    record_decision(conn, decision, component_version=component_version,
                    observed_at=observed_at,
                    supersede_reason=reason if decision.supersedes else None)
    if inputs.p2 is not None:
        emit_scoring_stage(conn, run_id=inputs.p2.run_id, decision=decision,
                           version_tuple_ref=inputs.p2.version_tuple_ref,
                           inputs=inputs.p2.upstream_stage_refs)
    return decision


# --- §6.12 steps 3 to 9, for one subject -------------------------------------------


def place_file(conn: sqlite3.Connection, *, subject, inputs: PipelineInputs,
               evidence, component_version: str, observed_at: str,
               group_plan_id: str | None = None,
               returned_from: str | None = None) -> PlacementDecision:
    """One file through steps 3-7 and 9. Step 8 runs inside P8 when it is needed.

    `group_plan_id` is passed in rather than patched on afterwards, because the
    STORED row has to carry it: `GroupPlan` asserts every member decision shares
    the plan's id, and a row written without it would make the review surface show
    several unrelated file moves while the in-memory plan looked correct.

    `returned_from` is §7.9's link: the residual decision that handed this file
    back. Without it `link_return` refuses, and §8.8's diff cannot walk the loop.
    """
    subject_ref = subject_ref_of(subject)

    # §8.4, before anything a model could see exists.
    privacy = privacy_state_for(conn, file_id=subject.file_id,
                                content_hash=subject.content_hash,
                                plan_version=inputs.plan_version)
    # Design:185 -- protected material "should not be moved automatically without a
    # user policy that explicitly permits it". P7 publishes the predicate and P11
    # asks it; asking only for protected material is not an optimisation, it is the
    # only case the answer can change. `may_move_automatically` reads P1's `files`
    # row, and a file P1 has never seen has no automatic move to permit.
    automatic_move_permitted = (
        automatic_move_permitted_for(conn, file_id=subject.file_id,
                                     plan_version=inputs.plan_version)
        if privacy.protected else False
    )

    # Step 3, and half of step 5 with it: retrieval suppresses as it goes, because
    # §6.3 makes suppression part of retrieval rather than a later filter.
    retrieval = retrieve(
        conn, subject=subject, plan_version=inputs.plan_version,
        limits=inputs.limits, facts=evidence["facts"],
        group_ids=evidence["group_ids"],
        curated_folder_labels=evidence["curated_folder_labels"],
        semantic_neighbours=evidence["semantic_neighbours"],
        component_version=component_version, observed_at=observed_at,
    )

    # §8.7, before any `place` is emitted.
    # `file` only. `learning._subject_ids` keys the file scope on the file id and
    # refuses `template` and `domain` outright, because P11 cannot know which
    # template or domain a user meant. `node` and `corpus` need a subject the
    # caller names; asking for them here would look like a wider check and
    # perform none.
    rejected = {
        hit.node_id for hit in suppressed_nodes(
            conn, subject_ref=subject_ref,
            node_ids=tuple(c.node_id for c in retrieval.candidates),
            scopes=(FILE,),
        )
    }
    if rejected:
        retrieval = Retrieval(
            subject_ref=retrieval.subject_ref,
            plan_version=retrieval.plan_version,
            candidates=tuple(c for c in retrieval.candidates
                             if c.node_id not in rejected),
            conflicts=retrieval.conflicts,
            semantic_only_node_ids=retrieval.semantic_only_node_ids,
        )
    if inputs.p2 is not None:
        emit_retrieval_stage(conn, run_id=inputs.p2.run_id, retrieval=retrieval,
                             version_tuple_ref=inputs.p2.version_tuple_ref,
                             inputs=inputs.p2.upstream_stage_refs)

    # Step 4.
    graphs = {
        candidate.node_id: build_node_local_graph(
            subject=subject, candidate=candidate,
            entry=entry_for(conn, plan_version=inputs.plan_version,
                            node_id=candidate.node_id),
            related_files=evidence["related_files"], limits=inputs.limits,
            entity_frequency=evidence["entity_frequency"],
            generic_entity_frequency=evidence["generic_entity_frequency"],
        )
        for candidate in retrieval.candidates
    }

    # Step 6, both halves. `identify_child_parent_fallback_or_none` names the
    # first one and it had no implementation until 2026-08-29.
    retrieval = _without_superseded_ancestors(
        conn, retrieval, plan_version=inputs.plan_version)
    # And the same collapse across branches, where the rival is the engine's own
    # vaguer copy of a folder the person already made (`00`:100).
    retrieval = _without_duplicated_proposals(
        conn, retrieval, plan_version=inputs.plan_version)
    graphs = {node_id: graph for node_id, graph in graphs.items()
              if node_id in {c.node_id for c in retrieval.candidates}}
    assessment = assess(retrieval, graphs, policy=inputs.policy)

    context = _Context(subject=subject, subject_ref=subject_ref, inputs=inputs,
                       privacy=privacy, retrieval=retrieval,
                       assessment=assessment, graphs=graphs,
                       automatic_move_permitted=automatic_move_permitted,
                       group_plan_id=group_plan_id, returned_from=returned_from,
                       component_version=component_version,
                       observed_at=observed_at)

    # Steps 7 and 8. Only for a bounded ambiguity, only if §8.4's gate allows a
    # dossier, and only if the caller supplied the model path. Step 8 -- the
    # validator -- runs INSIDE `run_call`; P11 supplies authorities and reads a
    # verdict, and re-checks none of Site C's fifteen.
    chosen_node_id: str | None = None
    if needs_model_call(assessment):
        if not may_assemble_dossier(privacy):
            return _abstention(conn, context, reason=PRIVACY_BLOCKED)
        if inputs.model_path_available():
            result = _judge_with_model(
                conn, subject=subject, inputs=inputs, retrieval=retrieval,
                evidence=evidence, call_site=C_PLACEMENT,
                observed_at=observed_at)
            if isinstance(result, Refusal):
                # P7 denied the release, from inside `run_call`. That is §8.4's
                # own answer arrived at from the other direction, and it is the
                # reason the record already has.
                return _abstention(conn, context, reason=PRIVACY_BLOCKED)
            verdict = _require_verdict(result, call_site=C_PLACEMENT)
            outcome, reason, deferred = transcribe(verdict, assessment=assessment)
            if outcome != PLACE:
                return _abstention(conn, context, reason=reason,
                                   deferred_stage=deferred)
            # The model chose among P11's candidates; which one it chose is read
            # back through the injected resolver, because `P8Verdict` names a
            # `claim_ref` and not a destination.
            chosen_node_id = inputs.chosen_node_of(verdict)
            if chosen_node_id not in legal_node_ids(
                    conn, plan_version=inputs.plan_version):
                raise ValueError(
                    f"{chosen_node_id!r} is not a legal destination of "
                    f"{inputs.plan_version!r}. P8 already refuses an invented "
                    "node; reaching here means the resolver disagreed with the "
                    "index, and P11 places nothing on a disagreement"
                )

    # Step 9.
    if chosen_node_id is None and assessment.abstention_reason is not None:
        return _abstention(conn, context, reason=assessment.abstention_reason)

    node_id = chosen_node_id or assessment.scored[0].node_id
    entry = entry_for(conn, plan_version=inputs.plan_version, node_id=node_id)
    # A model-decided placement is a context-supported one by construction: the
    # deterministic path had already declined to call it an exact match, which is
    # the only reason a model was asked. Carrying `assessment.confidence_class`
    # through unchanged would label a `place` "abstain: no supported destination"
    # -- a record whose label contradicts its own outcome.
    confidence = (CONTEXT_SUPPORTED_GROUP_MATCH if chosen_node_id is not None
                  else assessment.confidence_class)
    two = (dataclasses.replace(assessment.two_condition, requires_review=True)
           if chosen_node_id is not None else assessment.two_condition)
    decision_id, supersedes = _identity(
        conn, plan_version=inputs.plan_version, subject_ref=subject_ref,
        observed_at=observed_at)
    decision = PlacementDecision(
        decision_id=decision_id, plan_version=inputs.plan_version,
        supersedes=supersedes, superseded_by=None, supersede_reason=None,
        created_at=observed_at, origin_stage=PLACEMENT,
        returned_from=returned_from, subject=subject,
        group_plan_id=group_plan_id, outcome=PLACE,
        destination=Destination(node_id=entry.node_id, node_role=entry.node_role),
        return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=entry.depth,
                                     supported_depth=entry.depth,
                                     unsupported_levels=()),
        evidence_type=DIRECT if assessment.unique_direct_match else CONTEXT_SUPPORTED,
        confidence_class=confidence,
        matching_facts=_facts_of(retrieval, entry.node_id),
        group_support=None,
        # A model-chosen node need not be one P11 retrieved: `allowed_vocabulary`
        # is every legal destination, which is what stops Site C rejecting a
        # correct answer P11's six channels happened to miss. So the node-local
        # graph may not exist, and claiming anchors it does not have would be
        # evidence the file was never shown to carry.
        graph_anchors=(graphs[entry.node_id].anchors
                       if entry.node_id in graphs else ()),
        conflicts_considered=retrieval.conflicts,
        alternatives=assessment.alternatives,
        two_condition=two, abstention_reason=None,
        deferred_stage=None, privacy=privacy,
        review_policy=review_policy_for(
            privacy_state=privacy, two_condition=two, group_support=None,
            unique_direct_match=assessment.unique_direct_match,
            destination_disposition=entry.disposition,
            automatic_move_permitted=automatic_move_permitted),
        explanation=_explain(entry, assessment, retrieval,
                             model_decided=chosen_node_id is not None),
        residual=None,
    )
    return _write(conn, decision, inputs=inputs,
                  reason="a later placement of the same file version supersedes "
                         "this one (§8.2)",
                  component_version=component_version, observed_at=observed_at)


@dataclass(frozen=True)
class _Context:
    """Everything an abstention needs, gathered once so no builder re-derives it."""

    subject: object
    subject_ref: str
    inputs: PipelineInputs
    privacy: object
    retrieval: object
    assessment: object
    graphs: dict
    automatic_move_permitted: bool
    group_plan_id: str | None
    returned_from: str | None
    component_version: str
    observed_at: str


def _facts_of(retrieval, node_id: str) -> tuple:
    for candidate in retrieval.candidates:
        if candidate.node_id == node_id:
            return candidate.matching_facts
    return ()


def _explain(entry, assessment, retrieval, *, model_decided: bool = False) -> str:
    """§6.4 and §6.11: state the actual basis, claim no evidence the file lacks."""
    parts = [f"{entry.display_label} expects "
             + (", ".join(f"{field} = {value}"
                          for field, value in entry.expected_values)
                or "no stated value")]
    if model_decided:
        # The user is entitled to know a model was involved: §6.11 says a direct
        # and a context-supported placement "should not demand the same level of
        # trust", which a reviewer can only apply if the record says which it is.
        parts.append("chosen by the hierarchical destination judge from P11's "
                     "legal candidates, and validated by P8")
    if retrieval.conflicts:
        # Named first, counted always. The named ones are the branches something
        # was pulling this file towards; the count is every branch the conflict
        # ruled out. A sentence that listed all of them would name every folder in
        # the tree on a corpus like `planning/58-SCALE-STRESS.md` §2's, which is
        # the failure that document records for §5.9's warnings under its own
        # heading -- "the warning list outgrows the tree it describes".
        named = [node for conflict in retrieval.conflicts
                 for node in conflict.suppressed_node_ids]
        total = sum(conflict.suppressed_node_count
                    for conflict in retrieval.conflicts)
        if named:
            unnamed = total - len(named)
            parts.append(
                "ruled out " + ", ".join(named)
                + (f" and {unnamed} further destination"
                   f"{'' if unnamed == 1 else 's'}" if unnamed else "")
                + " on conflicting evidence")
        else:
            parts.append(
                f"ruled out {total} destination{'' if total == 1 else 's'} on "
                "conflicting evidence, none of which this file's evidence "
                "reached")
    parts.append(
        f"support {assessment.two_condition.support_score:.2f} against a "
        f"threshold of {assessment.two_condition.support_threshold:.2f}")
    return "; ".join(parts) + "."


def _supported_homes(context: _Context) -> tuple[str, ...]:
    """The destinations that cleared §6.10's support threshold on their own."""
    threshold = context.assessment.two_condition.support_threshold
    return tuple(item.node_id for item in context.assessment.scored
                 if item.support_score >= threshold)


def _abstention_explanation(context: _Context, *, reason: str) -> str:
    """What the person is told, which is not always what the machine recorded.

    Two abstentions are correct decisions that the default sentence describes
    falsely, and `planning/59-FINAL-UX-EVALUATION.md` finds both.

    * `multiple_supported_homes` (§3a): two legal destinations DID clear §6.10's
      support condition. "No legal destination cleared" is simply untrue of this
      file, and a user told it will distrust the extraction rather than make the
      choice that is actually theirs to make.
    * `privacy_blocked` (§3c, finding 9): the product declined to assemble a
      dossier ON PURPOSE. `00` on this material -- "sensitive personal material
      is not the same thing as `Numbers.app`" -- and a person told their passport
      failed to place concludes the product is broken rather than careful.

    Every other reason keeps the sentence it had. A correct abstention over thin
    evidence IS "no legal destination cleared §6.10's conditions", and giving all
    of them a reassuring new voice would erase the one honest report of a genuine
    evidence failure.
    """
    if reason == MULTIPLE_SUPPORTED_HOMES:
        homes = _supported_homes(context)
        return (
            f"{', '.join(homes)} each cleared §6.10's support threshold and "
            "nothing in the evidence separates them, so this file has more than "
            "one supported home. Nothing moved: which one is its home is a "
            "choice about your material, not a gap in the evidence."
        )
    if reason == PRIVACY_BLOCKED:
        if is_unclassified(context.privacy):
            # The third cause, and the one a corpus produces most. Neither of the
            # sentences below is true of it: nothing marked this file sensitive,
            # and the evidence never got as far as being weighed. `00` --
            # "sensitive personal material is not the same thing as `Numbers.app`"
            # -- and a file nothing could read is a third thing again.
            #
            # It used to end that thought with "nothing has been able to read
            # enough of it", and `65` §4.1 caught that on a live run: all four
            # files had a `direct` fact in `file_facts` and zero rows in
            # `classifications`. Reading is the step that WORKED and it was the
            # step the sentence blamed. `66` §4 forbids it -- "protected",
            # "unreadable", "unsupported format", "still indexing" and "no strong
            # match" may never share one message, and that was two of them
            # sharing one.
            #
            # P11 knows nothing classified this file. Whether it was READABLE is
            # P4's `extraction_runs` (B1: THE extraction-outcome record for the
            # whole system), which P11 does not read and must not guess at. So
            # the sentence names the step that stopped and claims nothing about
            # the one before it.
            return (
                "This file has not been classified -- nothing has yet said what "
                "kind of material it is -- so it was not shown to a model and "
                "nothing moved. It is waiting for you to say what it is, not "
                "marked sensitive and not judged on thin evidence."
            )
        if context.privacy.protected:
            return (
                "This file is protected material (§8.4), so nothing about it was "
                "assembled for a model and it was left exactly where it is. That "
                "is a deliberate decision about sensitivity, not a failure to "
                "find a destination."
            )
        return (
            "Deciding this file needed a model, and §8.4 did not clear this file "
            "for a model call. Nothing about it left this device and nothing "
            "moved; the evidence is retained."
        )
    return (
        f"No legal destination cleared §6.10's conditions ({reason}). "
        "Abstaining is the correct outcome; the evidence is retained and the "
        "file has not moved."
    )


def _abstention(conn: sqlite3.Connection, context: _Context, *, reason: str,
                deferred_stage: str | None = None) -> PlacementDecision:
    """§6.10: a correct abstention is a successful outcome, and is recorded as one.

    `deferred_stage` is set only when `reason` is `budget_deferred`, and the record
    enforces the pairing both ways. §8.6 requires a ceiling-truncated run to render
    differently from "I looked and could not tell", and a deferral recorded as a
    plain abstention is exactly the "understood and found unimportant" impression
    the design forbids.
    """
    if (reason == BUDGET_DEFERRED) != (deferred_stage is not None):
        raise ValueError(
            "a budget deferral names the stage it was cut short at, and only a "
            "budget deferral has one (§8.6)"
        )
    inputs = context.inputs
    decision_id, supersedes = _identity(
        conn, plan_version=inputs.plan_version, subject_ref=context.subject_ref,
        observed_at=context.observed_at)
    decision = PlacementDecision(
        decision_id=decision_id, plan_version=inputs.plan_version,
        supersedes=supersedes, superseded_by=None, supersede_reason=None,
        created_at=context.observed_at, origin_stage=PLACEMENT,
        returned_from=context.returned_from, subject=context.subject,
        group_plan_id=context.group_plan_id, outcome=ABSTAIN,
        destination=None, return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=0, supported_depth=0,
                                     unsupported_levels=()),
        evidence_type=CONTEXT_SUPPORTED,
        confidence_class=ABSTAIN_NO_SUPPORTED_DESTINATION,
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=context.retrieval.conflicts,
        alternatives=context.assessment.alternatives,
        two_condition=context.assessment.two_condition, abstention_reason=reason,
        deferred_stage=deferred_stage, privacy=context.privacy,
        review_policy=review_policy_for(
            privacy_state=context.privacy,
            two_condition=context.assessment.two_condition, group_support=None,
            unique_direct_match=False, destination_disposition=None,
            automatic_move_permitted=context.automatic_move_permitted),
        explanation=_abstention_explanation(context, reason=reason),
        residual=None,
    )
    return _write(conn, decision, inputs=inputs,
                  reason="a later decision about the same file version "
                         "supersedes this abstention (§8.2)",
                  component_version=context.component_version,
                  observed_at=context.observed_at)


# --- step 7: the hierarchical destination judge -----------------------------------


def _require_verdict(result, *, call_site: str) -> P8Verdict:
    if isinstance(result, P8Verdict):
        return result
    raise ModelJudgementUnavailable(
        f"{call_site} came back with {type(result).__name__}, which is not a "
        "judgement about this file. §6.10's abstention reasons are a closed set "
        "and none of them means 'the call did not happen'; naming one would "
        "record a conclusion nothing reached"
    )


def _judge_with_model(conn, *, subject, inputs: PipelineInputs, retrieval,
                      evidence, call_site: str, observed_at: str):
    """§6.12 step 7, and step 8 with it. P11 assembles the REQUEST, never a check.

    Everything here is either P11's own answer or a caller injection. The four
    Site C authorities come from `p8_seam.placement_authorities`; the fifteen Site
    C checks stay in `llm_harness/placement_validation.py` and P11 spells none of
    their reason codes.

    `allowed_vocabulary` is P11's legal candidate set and is the single most
    load-bearing value handed over: Site C rejects any destination outside it as
    `INVENTED_NODE`. It is set here rather than taken from the caller's
    `CallDependencies`, because a caller-supplied vocabulary is a caller-supplied
    answer to "which nodes exist", which is the index's question.

    `evidence_snapshot_id` is minted here because nothing else mints one and
    `run_call` refuses a C or D request without it BEFORE the spend.
    """
    if not evidence.get("evidence_items"):
        raise ModelJudgementUnavailable(
            "a model call needs the reference-only evidence metadata the dossier "
            "builder supplies; P8 refuses a request with none and P11 synthesises "
            "no kind, location, span or basis of its own"
        )
    if not retrieval.candidates:
        raise ModelJudgementUnavailable(
            "no legal destination was retrievable for this subject, so there is "
            "nothing for the judge to choose between and asking one would be "
            "inviting it to invent (§6.6)"
        )
    # The keys the DOSSIER cites, which is `evidence_items` below and not the
    # subset that happened to match a node. `evidence_snapshot_id_for` addresses
    # what the dossier carries, so drawing from the matched facts alone would
    # address a different set from the one that was sent -- and would refuse to
    # mint at all for a call whose candidates were reached by group evidence.
    observation_keys = tuple(
        fact.evidence_ref for fact in evidence["facts"] if fact.evidence_ref
    )
    snapshot = evidence_snapshot_id_for(plan_version=inputs.plan_version,
                                        observation_keys=observation_keys)
    subject_ref = subject_ref_of(subject)
    legal = sorted(legal_node_ids(conn, plan_version=inputs.plan_version))
    if call_site == C_PLACEMENT:
        sites = site_dependencies(placement=placement_authorities(
            conn, plan_version=inputs.plan_version, policy=inputs.policy,
            sensitivity_policy=inputs.sensitivity_policy))
    else:
        sites = site_dependencies(residual=residual_authorities(
            conn, plan_version=inputs.plan_version, approved_target_ids=legal,
            sensitivity_policy=inputs.sensitivity_policy))

    # §8.6's two spend ceilings, put on the budget P8 reserves against.
    #
    # They are set here for the same reason `allowed_vocabulary` is, and the
    # argument is the same sentence with two words changed: a caller-supplied
    # BUDGET is a caller-supplied answer to "what did the user agree to spend",
    # which is P1's question and is already answered in
    # `model.max_llm_calls_per_thousand_files` and `model.max_cost_per_scan`.
    # Before this, `PlacementLimits` carried both and no module read either
    # (`planning/58-SCALE-STRESS.md` item 8), so the only thing bounding a scan's
    # model spend was whatever number the caller happened to construct.
    #
    # What is NOT taken from P11 is the scan itself. `scan_id` and
    # `corpus_file_count` describe the run and belong to it; P11 knows the
    # ceilings and not how many files the disk holds. So the two are replaced and
    # the two are kept.
    #
    # Enforcement is P8's and stays P8's: `reserve_call` refuses past either
    # ceiling, `run_call` turns the refusal into `BUDGET_EXHAUSTED`, and
    # `p8_seam.transcribe` records it as `budget_deferred` with a
    # `deferred_stage` -- §8.6's "retain extracted evidence, mark the deferred
    # stage, and leave the file in review", never a cheaper placement.
    budget = inputs.call_dependencies.scan_budget
    if budget is None:
        raise ScanBudgetRequired(
            "§8.6 bounds model spend per scan, and this request names no scan to "
            "charge against; P11 supplies the two ceilings and the caller "
            "supplies the scan they apply to"
        )
    dependencies = dataclasses.replace(
        inputs.call_dependencies,
        site_dependencies=sites,
        scan_budget=dataclasses.replace(
            budget,
            max_calls_per_1000_files=inputs.limits.max_llm_calls_per_thousand_files,
            max_estimated_cost=Decimal(inputs.limits.max_cost_per_scan)),
        allowed_vocabulary=legal,
        proposal_class=PLACEMENT if call_site == C_PLACEMENT else RESIDUAL,
        basis_key=basis_key_for(subject_id=subject.file_id,
                                node_id=retrieval.candidates[0].node_id),
        learning_scope=FILE, learning_subject_id=subject.file_id,
    )
    request = DossierRequest(
        call_site=call_site, subject_ref=subject_ref,
        # P8's controlled reason, imported and not retyped. §6.6 lists six
        # circumstances that make a call eligible and P8 publishes a constant for
        # each; spelling one here would be a seventh vocabulary.
        eligibility_reason=(SEVERAL_LEGAL_NODES_PLAUSIBLE
                            if call_site == C_PLACEMENT
                            else USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW),
        # P8's reference-only `EvidenceItem`s, supplied by the dossier builder
        # and never synthesised here. P11's `MatchingFact` carries a field, a
        # value and an observation key; P8's item carries a kind, a location, an
        # excerpt span and a basis, and `records.py:204-207` says in terms that
        # "P8 does not synthesise kind, location, reliability or basis". A
        # conversion here would have to invent three of them, so the caller that
        # built the evidence hands them over instead.
        evidence_items=tuple(evidence["evidence_items"]),
        conflicts=to_p8_conflicts(retrieval.conflicts),
        # P7 builds the release request; P11 holds the builder and never a `Gate`.
        # Assembling it here, after `may_assemble_dossier` answered, is what keeps
        # §8.4's gate on the right side of the spend.
        model_call_request=inputs.model_call_request(
            subject_ref=subject_ref,
            evidence_items=tuple(evidence["evidence_items"]),
            max_dossier_tokens=inputs.limits.max_dossier_tokens),
        plan_version=inputs.plan_version, evidence_snapshot_id=snapshot,
    )
    return call_placement(
        conn, request, gate=inputs.gate, model_client=inputs.model_client,
        prompt=inputs.prompt, call_dependencies=dependencies,
        observed_at=lambda: observed_at,
    )


# --- §6.8 and §6.9: the group plan -------------------------------------------------


def place_group(conn: sqlite3.Connection, *, group_id: str,
                inputs: PipelineInputs, evidence_for,
                component_version: str, observed_at: str,
                skip_file_ids: frozenset[str] = frozenset()) -> GroupPlan:
    """§6.8: confirm the shared parent FIRST, then classify members beneath it.

    The ordering is the whole of §6.8. A member classified before the parent is
    classified against no shared context, and the result is several unrelated file
    moves presented as a plan.

    Acceptance is read through P9 as of P10's frozen version
    (`accepted_group_as_of`), never off `Group.state`.

    `skip_file_ids` names the members §6.9 resolves instead: a file with accepted
    membership in two packets belongs to neither plan alone, and placing it inside
    one of them IS choosing between them.
    """
    accepted: AcceptedGroup = accepted_group_as_of(
        conn, group_id=group_id, plan_version=inputs.plan_version)
    # The address carries `observed_at`, for `residual.record_set_decision`'s own
    # reason: `one_current_group_plan` is a partial unique index over UNSUPERSEDED
    # rows, so it already forbids two live plans for one group in one version.
    # Addressing the row as `plan_version:group_id` as well would forbid a SECOND
    # ROW OF ANY KIND -- including the superseding one -- and the three supersede
    # columns on that table would be columns no writer could ever reach.
    group_plan_id = f"{inputs.plan_version}:{group_id}:{observed_at}"
    memberships = tuple(m for m in accepted.memberships
                        if m.file_id not in skip_file_ids)

    # Step one: the shared parent, from each member's own best destination.
    member_parents: dict[str, str | None] = {}
    provisional: dict[str, PlacementDecision] = {}
    for membership in memberships:
        decision = place_file(
            conn, subject=_member_subject(membership), inputs=inputs,
            evidence=evidence_for(membership.file_id),
            group_plan_id=group_plan_id,
            component_version=component_version, observed_at=observed_at)
        provisional[membership.file_id] = decision
        member_parents[membership.file_id] = (
            decision.destination.node_id if decision.destination else None)

    shared_parent = confirm_shared_parent(
        member_parents, policy=inputs.tree.shared_material_policy)

    # Step two: outliers are excluded and explained, never forced in. P9 already
    # flagged them and already holds the competing values; P11 records what P9
    # found and routes the file (§6.8).
    outliers: list[ExcludedOutlier] = []
    members: list[PlacementDecision] = []
    for membership in memberships:
        decision = provisional[membership.file_id]
        if membership.outlier_flag != NOT_FLAGGED:
            outliers.append(excluded_outlier_for(
                membership,
                routed_node_id=(decision.destination.node_id
                                if decision.destination else None)))
            continue
        members.append(decision)   # already carries `group_plan_id`, in the row

    plan = GroupPlan(
        group_plan_id=group_plan_id, plan_version=inputs.plan_version,
        group_id=group_id, shared_parent_node_id=shared_parent,
        member_decisions=tuple(members), excluded_outliers=tuple(outliers))
    _record_group_plan(conn, plan, component_version=component_version,
                       observed_at=observed_at)
    return plan


def _record_group_plan(conn: sqlite3.Connection, plan: GroupPlan, *,
                       component_version: str, observed_at: str) -> None:
    """§6.8's plan, in the table the schema made for it.

    Without this the plan exists only in the caller's memory: `placement_group_plans`
    had no writer at all, so a review surface reopened a day later would find four
    file decisions and no evidence they were ever one plan.
    """
    import json

    live = conn.execute(
        "SELECT record_id FROM placement_group_plans WHERE plan_version = ? AND "
        "group_id = ? AND superseded_by IS NULL",
        (plan.plan_version, plan.group_id),
    ).fetchone()
    if live is not None and live["record_id"] != plan.group_plan_id:
        # Supersede first, then insert: the unique index is over unsuperseded
        # rows, so linking after the insert would put two current plans for one
        # group in the table for the length of one statement.
        mark_superseded(
            conn, "placement_group_plans", old_id=live["record_id"],
            new_id=plan.group_plan_id,
            reason="§6.8's plan for this group was recomputed (§8.2)")
    conn.execute(
        "INSERT INTO placement_group_plans (record_id, plan_version, group_id, "
        "shared_parent_node_id, payload, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (plan.group_plan_id, plan.plan_version, plan.group_id,
         plan.shared_parent_node_id,
         json.dumps({
             "group_plan_id": plan.group_plan_id,
             "member_decision_ids": [d.decision_id for d in plan.member_decisions],
             "excluded_outliers": [dataclasses.asdict(o)
                                   for o in plan.excluded_outliers],
         }, sort_keys=True),
         observed_at),
    )
    placement_events.group_plan_emitted(
        conn, group_plan_id=plan.group_plan_id, group_id=plan.group_id,
        shared_parent_node_id=plan.shared_parent_node_id,
        component_version=component_version, observed_at=observed_at)


def _member_subject(membership) -> Subject:
    return Subject(kind=FILE, file_id=membership.file_id,
                   content_hash=membership.content_hash, group_id=None,
                   member_file_ids=())


def _shared_branch_of(tree) -> str | None:
    """The frozen tree's shared-material node, if it froze one. P11 mints none.

    §6.9's worked example: *"If no shared branch exists, the system should not
    arbitrarily choose one university."* So absence is answered with None and the
    policy decides what happens next, rather than P11 producing a branch.
    """
    for node in tree.nodes:
        if node.node_role == SHARED_MATERIAL and node.accepts_placement:
            return node.node_id
    return None


def _flat_two_condition(inputs: PipelineInputs) -> TwoCondition:
    """§6.10's figures on a record §6.10 did not decide. One shape, one set of
    figures.

    SPEC:473-475 makes `verdict` a P11 field on every decision, so a §7 decision
    and a §6.9 decision carry the thresholds they were judged under even though
    the judgement was P8's or the user's. `meets_margin` is vacuous because
    neither path compares against a next-best destination.
    """
    return TwoCondition(
        support_score=0.0,
        support_threshold=inputs.policy.minimum_support_threshold,
        meets_threshold=False, margin_over_next=None,
        margin_threshold=inputs.policy.margin_threshold,
        meets_margin=MARGIN_TRUE_VACUOUS, verdict=WEAK,
        requires_review=True)


def _multi_home_decision(conn, *, subject, inputs: PipelineInputs, outcome,
                         payload, privacy, automatic_move_permitted: bool,
                         component_version: str,
                         observed_at: str) -> PlacementDecision:
    """§6.9's answer as one decision: a shared branch, a question, or an abstention.

    `payload` is the shared branch's node id for `place`, the competing ids for
    `ask_user`, and `no_shared_branch` for `abstain` -- and it is NEVER one of the
    competing packets, because `resolve_multi_home` has no branch that returns one.
    """
    two = _flat_two_condition(inputs)
    entry = (entry_for(conn, plan_version=inputs.plan_version, node_id=payload)
             if outcome == PLACE else None)
    decision_id, supersedes = _identity(
        conn, plan_version=inputs.plan_version,
        subject_ref=subject_ref_of(subject), observed_at=observed_at,
        suffix=":mh")
    decision = PlacementDecision(
        decision_id=decision_id, plan_version=inputs.plan_version,
        supersedes=supersedes, superseded_by=None, supersede_reason=None,
        created_at=observed_at, origin_stage=PLACEMENT, returned_from=None,
        subject=subject, group_plan_id=None, outcome=outcome,
        destination=(Destination(node_id=entry.node_id,
                                 node_role=entry.node_role)
                     if entry is not None else None),
        return_target=None, marked_state=None,
        ask=(Ask(question="Which packet is this file's primary home?",
                 options=tuple(payload)) if outcome == ASK_USER else None),
        decision_depth=DecisionDepth(
            node_depth=entry.depth if entry else 0,
            supported_depth=entry.depth if entry else 0, unsupported_levels=()),
        evidence_type=CONTEXT_SUPPORTED,
        confidence_class=(SHARED_MATERIAL_DECISION if entry is not None
                          else ABSTAIN_NO_SUPPORTED_DESTINATION),
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=(), alternatives=(), two_condition=two,
        abstention_reason=(NO_SHARED_BRANCH if outcome == ABSTAIN else None),
        deferred_stage=None, privacy=privacy,
        review_policy=review_policy_for(
            privacy_state=privacy, two_condition=two, group_support=None,
            unique_direct_match=False,
            destination_disposition=entry.disposition if entry else None,
            automatic_move_permitted=automatic_move_permitted),
        explanation=(
            "This file has accepted membership in more than one packet. §6.9 "
            "permits a shared branch, a question, or an abstention, and never an "
            "arbitrary choice between the packets."),
        residual=None,
    )
    return _write(conn, decision, inputs=inputs,
                  reason="§6.9 resolved this file's multiple homes (§8.2)",
                  component_version=component_version, observed_at=observed_at)


# --- §7: the residual stage ---------------------------------------------------------


def run_residual_file(conn: sqlite3.Connection, *, subject, set_id: str,
                      inputs: PipelineInputs, evidence, action: str, target,
                      component_version: str,
                      observed_at: str) -> PlacementDecision:
    """One §7.7 action, as one decision on the ONE record shape.

    §7.6's gate is checked first and by refusal: `require_set_decision` raises when
    the set has no decision. §7.9's loop is bounded by an injection:
    `check_return_cycle` refuses without `max_return_cycles`, because SPEC Open
    question 8 states no bound and an unbounded loop is a replay that never
    terminates.
    """
    set_decision = require_set_decision(conn, plan_version=inputs.plan_version,
                                        set_id=set_id)
    outcome, qualifier = outcome_for_action(action, target=target)
    if outcome == RETURN_TO_PLACEMENT:
        check_return_cycle(conn, subject_ref=subject_ref_of(subject),
                           max_return_cycles=inputs.max_return_cycles)
    context = ResidualContext(set_id=set_id, set_decision=set_decision.choice,
                              lifecycle_policy_ref=None)
    return _residual_decision(
        conn, subject=subject, inputs=inputs, outcome=outcome,
        qualifier=qualifier, residual=context, evidence=evidence,
        component_version=component_version, observed_at=observed_at)


def _residual_decision(conn, *, subject, inputs: PipelineInputs, outcome,
                       qualifier, residual, evidence, component_version,
                       observed_at) -> PlacementDecision:
    """One §7 decision on the SAME thirty-field shape §6 uses (Done-means 1).

    Exactly one outcome-shaped field is filled, chosen by `outcome`, because the
    record refuses any other combination: `destination` on `place`,
    `return_target` on `return_to_placement`, `marked_state` on `mark_state`,
    `abstention_reason` on `abstain`, and none of the four on `leave_in_place` or
    `mark_review_later` -- whether those two result in a move is the Review Later
    node's `disposition` (§7.4, set by P10), not this record's decision.
    """
    entry = (entry_for(conn, plan_version=inputs.plan_version, node_id=qualifier)
             if outcome == PLACE else None)
    if outcome == PLACE and entry is None:
        raise ValueError(
            f"{qualifier!r} is not a legal destination of "
            f"{inputs.plan_version!r}; §7.7 chooses among APPROVED residual "
            "targets and P11 places nothing outside the frozen tree"
        )
    privacy = privacy_state_for(conn, file_id=subject.file_id,
                                content_hash=subject.content_hash,
                                plan_version=inputs.plan_version)
    automatic_move_permitted = (
        automatic_move_permitted_for(conn, file_id=subject.file_id,
                                     plan_version=inputs.plan_version)
        if privacy.protected else False
    )
    two = _flat_two_condition(inputs)
    decision_id, supersedes = _identity(
        conn, plan_version=inputs.plan_version,
        subject_ref=subject_ref_of(subject), observed_at=observed_at, suffix=":r")
    decision = PlacementDecision(
        decision_id=decision_id, plan_version=inputs.plan_version,
        supersedes=supersedes, superseded_by=None, supersede_reason=None,
        created_at=observed_at, origin_stage=RESIDUAL, returned_from=None,
        subject=subject, group_plan_id=None, outcome=outcome,
        destination=(Destination(node_id=entry.node_id,
                                 node_role=entry.node_role)
                     if entry is not None else None),
        return_target=(ReturnTarget(kind=qualifier, id=subject.file_id)
                       if outcome == RETURN_TO_PLACEMENT else None),
        marked_state=qualifier if outcome == MARK_STATE else None, ask=None,
        decision_depth=DecisionDepth(
            node_depth=entry.depth if entry else 0,
            supported_depth=entry.depth if entry else 0, unsupported_levels=()),
        evidence_type=CONTEXT_SUPPORTED,
        confidence_class=(CONTEXT_SUPPORTED_GROUP_MATCH if entry is not None
                          else ABSTAIN_NO_SUPPORTED_DESTINATION),
        matching_facts=tuple(evidence["facts"]) if entry is not None else (),
        group_support=None, graph_anchors=(), conflicts_considered=(),
        alternatives=(), two_condition=two,
        abstention_reason=qualifier if outcome == ABSTAIN else None,
        deferred_stage=None, privacy=privacy,
        review_policy=review_policy_for(
            privacy_state=privacy, two_condition=two, group_support=None,
            unique_direct_match=False,
            destination_disposition=entry.disposition if entry else None,
            automatic_move_permitted=automatic_move_permitted),
        explanation=(
            f"Residual review of set {residual.set_id} returned {outcome!r}. "
            "The set-level decision authorised this review and the file has not "
            "moved."),
        residual=residual,
    )
    return _write(conn, decision, inputs=inputs,
                  reason="a later decision about the same file version "
                         "supersedes this residual one (§8.2)",
                  component_version=component_version, observed_at=observed_at)


def _residual_action_and_target(inputs: PipelineInputs, verdict) -> tuple[str, object]:
    """§7.7's action and its target, read back through the injected resolver.

    P8 validates `payload["action"]` against `RESIDUAL_ACTIONS` and rewrites the
    verdict's `disposition` into its own coarser vocabulary, so the verdict cannot
    say which of the eight the model chose: `residual_destination` covers both the
    destination choice and the broad parent, and `return_to_placement` covers both
    returns -- and it is the return's KIND that `ReturnTarget` has to record.
    """
    resolver = inputs.residual_action_of
    if not callable(resolver):
        raise ResidualActionUnavailable(
            "§7.7's action lives in the model's response, which P8 validates and "
            "P11 never holds; `residual_action_of` is injected by the caller that "
            "made the call, and absent means refuse rather than guess"
        )
    action, target = resolver(verdict)
    if action not in ACTION_OUTCOME:
        raise ResidualActionUnavailable(
            f"{action!r} is not one of §7.7's eight actions; P8 already refuses "
            "an action outside its controlled set, so reaching here means the "
            "resolver disagreed with P8"
        )
    return action, target


def _review_set_with_model(conn, *, item: ResidualSet, inputs: PipelineInputs,
                           subjects: dict, evidence_for, component_version: str,
                           observed_at: str) -> list[PlacementDecision]:
    """§7.7, per file, for a set whose decision asked for it and no other.

    Site D is P8's; P11 supplies `approved_target_ids` and reads an action.
    `outcome_for_action` maps that action onto one of §6's outcomes, which is why
    a residual decision needs no field the §6 path does not already have.
    """
    written: list[PlacementDecision] = []
    for file_id in item.member_file_ids:
        subject = subjects[file_id]
        privacy = privacy_state_for(conn, file_id=file_id,
                                    content_hash=subject.content_hash,
                                    plan_version=inputs.plan_version)
        evidence = evidence_for(file_id)
        residual = ResidualContext(
            set_id=item.set_id,
            set_decision=require_set_decision(
                conn, plan_version=inputs.plan_version,
                set_id=item.set_id).choice,
            lifecycle_policy_ref=None)
        if not may_assemble_dossier(privacy):
            # §8.4 before the dossier, on the residual path exactly as on the
            # placement path. Protected material does not become releasable
            # because the file reached §7 instead of §6 -- and it is RECORDED
            # rather than skipped, so the file is present-but-untouched and never
            # silently omitted from the review screen.
            written.append(_residual_decision(
                conn, subject=subject, inputs=inputs, outcome=ABSTAIN,
                qualifier=PRIVACY_BLOCKED, residual=residual,
                evidence=evidence, component_version=component_version,
                observed_at=observed_at))
            continue
        retrieval = retrieve(
            conn, subject=subject, plan_version=inputs.plan_version,
            limits=inputs.limits, facts=evidence["facts"],
            group_ids=evidence["group_ids"],
            curated_folder_labels=evidence["curated_folder_labels"],
            semantic_neighbours=evidence["semantic_neighbours"],
            component_version=component_version, observed_at=observed_at)
        result = _judge_with_model(
            conn, subject=subject, inputs=inputs, retrieval=retrieval,
            evidence=evidence, call_site=D_RESIDUAL, observed_at=observed_at)
        if isinstance(result, Refusal):
            written.append(_residual_decision(
                conn, subject=subject, inputs=inputs, outcome=ABSTAIN,
                qualifier=PRIVACY_BLOCKED, residual=residual, evidence=evidence,
                component_version=component_version, observed_at=observed_at))
            continue
        verdict = _require_verdict(result, call_site=D_RESIDUAL)
        if verdict.outcome == P8_REJECT:
            # P8 refused the model's answer. Acting on the action anyway would
            # carry out a proposal the validator threw away.
            written.append(_residual_decision(
                conn, subject=subject, inputs=inputs, outcome=ABSTAIN,
                qualifier=NO_SUPPORTED_DESTINATION, residual=residual,
                evidence=evidence, component_version=component_version,
                observed_at=observed_at))
            continue
        action, target = _residual_action_and_target(inputs, verdict)
        decision = run_residual_file(
            conn, subject=subject, set_id=item.set_id, inputs=inputs,
            evidence=evidence, action=action, target=target,
            component_version=component_version, observed_at=observed_at)
        written.append(decision)
        if decision.outcome == RETURN_TO_PLACEMENT:
            # §7.9: the file actually goes back through §6, and the placement it
            # produces names the residual decision that handed it back. Both
            # records persist; `link_return` refuses if the link is missing.
            placed = place_file(
                conn, subject=subject, inputs=inputs, evidence=evidence,
                returned_from=decision.decision_id,
                component_version=component_version, observed_at=observed_at)
            link_return(conn, residual_decision=decision,
                        placement_decision=placed,
                        component_version=component_version,
                        observed_at=observed_at)
            written.append(placed)
    return written


# --- §6.12 step 9, over a corpus, and §7 after it ------------------------------------


def run_corpus(conn: sqlite3.Connection, *, subjects, group_ids,
               inputs: PipelineInputs, evidence_for, component_version: str,
               observed_at: str) -> CorpusResult:
    """§6 for every subject and every accepted group, then §7 for what is left.

    The two-pass order is contractual, not stylistic. §7.1: residual is *"a
    separate stage that runs only after normal group-aware classification has been
    attempted"*, so every file and every accepted group goes through §6 first and
    only what §6 could not place reaches §7. `surface_residual_sets` refuses a
    `placement_pass_complete=False` caller, so the ordering is enforced by a raise
    rather than by this function remembering to do it.
    """
    decisions: list[PlacementDecision] = []
    plans: list[GroupPlan] = []
    known: dict[str, Subject] = {s.file_id: s for s in subjects if s.file_id}

    # §6.9, detected BEFORE anything is placed. A file with accepted membership in
    # two packets belongs to neither plan alone, and the design is explicit that
    # the engine "should not arbitrarily choose one university"
    # (`01-product-design-structured.md:1255-1259`). Placing it inside the first
    # plan and correcting afterwards would mean the arbitrary choice was made and
    # then withdrawn, which is not the same as never making it.
    accepted = {group_id: accepted_group_as_of(
        conn, group_id=group_id, plan_version=inputs.plan_version)
        for group_id in group_ids}
    homes: dict[str, list[str]] = {}
    for group_id, group in accepted.items():
        for membership in group.memberships:
            known.setdefault(membership.file_id, _member_subject(membership))
            homes.setdefault(membership.file_id, []).append(group_id)
    multi_home = frozenset(file_id for file_id, ids in homes.items()
                           if len(set(ids)) > 1)

    # §6.8 before the per-file pass: a member's decision belongs to its group's
    # plan, and a file placed alone first would be placed against no shared
    # context. `place_group` writes the member decisions itself.
    covered: set[str] = set(multi_home)
    for group_id in group_ids:
        plan = place_group(conn, group_id=group_id, inputs=inputs,
                           evidence_for=evidence_for,
                           component_version=component_version,
                           observed_at=observed_at, skip_file_ids=multi_home)
        plans.append(plan)
        decisions.extend(plan.member_decisions)
        covered.update(d.subject.file_id for d in plan.member_decisions)
        covered.update(o.file_id for o in plan.excluded_outliers)

    by_group = {plan.group_id: plan for plan in plans}
    for file_id in sorted(multi_home):
        subject = known[file_id]
        parents = sorted({by_group[group_id].shared_parent_node_id
                          for group_id in homes[file_id]
                          if by_group[group_id].shared_parent_node_id})
        if len(parents) < 2:
            # The packets agree, or neither settled a parent, so there is no
            # competition to resolve and the ordinary path applies.
            decisions.append(place_file(
                conn, subject=subject, inputs=inputs,
                evidence=evidence_for(file_id),
                component_version=component_version, observed_at=observed_at))
            continue
        privacy = privacy_state_for(conn, file_id=file_id,
                                    content_hash=subject.content_hash,
                                    plan_version=inputs.plan_version)
        outcome, payload = resolve_multi_home(
            candidate_node_ids=tuple(parents),
            shared_material_policy=inputs.tree.shared_material_policy,
            shared_branch_node_id=_shared_branch_of(inputs.tree),
            ask_or_abstain=inputs.ask_or_abstain)
        decisions.append(_multi_home_decision(
            conn, subject=subject, inputs=inputs, outcome=outcome,
            payload=payload, privacy=privacy,
            automatic_move_permitted=(
                automatic_move_permitted_for(conn, file_id=file_id,
                                             plan_version=inputs.plan_version)
                if privacy.protected else False),
            component_version=component_version, observed_at=observed_at))

    for subject in subjects:
        if subject.file_id in covered:
            continue
        decisions.append(place_file(
            conn, subject=subject, inputs=inputs,
            evidence=evidence_for(subject.file_id),
            component_version=component_version, observed_at=observed_at))

    unplaced = tuple(d.subject.file_id for d in decisions
                     if d.outcome != PLACE and d.subject.file_id)

    # §7.5. The §6 pass is complete for the corpus, which is the only condition
    # under which a file may be called residual.
    sets: tuple[ResidualSet, ...] = surface_residual_sets(
        conn, plan_version=inputs.plan_version, unplaced=unplaced,
        partition=inputs.partition, limits=inputs.limits,
        placement_pass_complete=True, component_version=component_version,
        observed_at=observed_at)

    return CorpusResult(
        decisions=tuple(decisions), group_plans=tuple(plans),
        residual_sets=sets, unplaced_file_ids=unplaced, subjects=known)


def review_residual_sets(conn: sqlite3.Connection, *, result: CorpusResult,
                         inputs: PipelineInputs, evidence_for,
                         component_version: str,
                         observed_at: str) -> tuple[PlacementDecision, ...]:
    """§7.6 and §7.7, for the sets the user decided and no others.

    This is a SECOND call and not the tail of `run_corpus`, because the user
    decides between the two. §7.6's gate is "no per-file residual model call may
    be issued for a set until that set has a decision", and the decision arrives
    from the review screen after the sets were surfaced -- so a single pass that
    surfaced and reviewed in one breath could only ever be reviewing a decision
    made about some earlier run's sets.
    """
    written: list[PlacementDecision] = []
    for item in result.residual_sets:
        # Two questions in this order, and the order is the point. FIRST: did the
        # user's set-level choice ask for a model at all? Surfaced and not yet
        # decided is the state §7.6's gate exists to make visible, and a set
        # decided any other way asked for nothing -- both are left alone, which is
        # the decision the user made, and neither is an error.
        try:
            set_decision = require_set_decision(
                conn, plan_version=inputs.plan_version, set_id=item.set_id)
        except SetDecisionRequired:
            continue
        if not model_calls_permitted(set_decision):
            continue
        # SECOND, and only now that a spend is about to happen: the one gate.
        # `ProtectedSetNotReadable` is deliberately NOT caught. It fires only when
        # a decision asked to open a protected set, and answering that by skipping
        # would record it as understood and found unimportant -- which is exactly
        # what the set stays on the review screen, counted and explained, to
        # prevent. A protected set nobody decided never reaches this line.
        require_model_call_permitted(conn, plan_version=inputs.plan_version,
                                     residual_set=item)
        written.extend(_review_set_with_model(
            conn, item=item, inputs=inputs, subjects=result.subjects,
            evidence_for=evidence_for, component_version=component_version,
            observed_at=observed_at))
    return tuple(written)
