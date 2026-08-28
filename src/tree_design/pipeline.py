# src/tree_design/pipeline.py
"""§5's design chain end to end, §6.1 after it, and §8.8's freeze last.

`placement.pipeline.run_corpus` is the shape this mirrors and the reason it
exists. P11 has had one entry point that takes a corpus and runs §6 and §7 over
it since it shipped. P10 had eleven modules and no chain, so every P10 test drove
one of them with the module before it replaced by a literal — `route_branch` over
a hand-built `BranchContext`, `materialise_branch` over a hand-built
`CompositionCandidate`, `freeze` over hand-written nodes. Each module was green.
Nothing ran them in order, and the order is where the seam lives.

**Nothing here decides anything.** Two records carry what this module may not
invent, and neither has a default anywhere:

* `TreeDesignAuthorities` — what the DESIGN leaves open. Ranking weights, the
  privacy ordering, the handling-class collapse, the disclosure test: every one
  is a number or a judgement §5 declines to state, and `tree_design.config`
  already gives the rule — absent means refuse, never guess.
* `TreeDesignDecisions` — what the USER decides. Which branches to keep, which
  nesting to take, §5.8's answer per branch, §6.9's policy, `00`:99's scoped
  General, and which residual templates to enable. §5.7 is explicit that a
  template is inert until approved, so a chain that chose for the user would be
  the failure C8 exists to prevent, one layer up.

**The version chain is the point, not an implementation detail.** §8.8 makes
every edit open a draft, and `apply_review_action` mints a NEW `node_id` for
every node it copies. So a run produces a chain of plan versions and only the
last is frozen — which is exactly the condition P11's `reproject` was written for
and, until this module existed, had never been given by a real P10 run.

What this chain does NOT do is recorded rather than hidden: it creates no
`existing` node, because §5.10's `adopt-existing` is one of the tree-edit actions
P10 defines and has not built a writer for, and `apply_review_action` refuses it
by name. A corpus whose existing folders should become nodes is not yet
expressible, and the refusal says so.
"""
from __future__ import annotations

import dataclasses
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field

from tree_design.candidates import (
    BranchCandidate, VerticalOption, horizontal_candidates, vertical_options,
)
from tree_design.config import ConfigurationRequired, TreeLimits
from tree_design.freeze import FrozenTree, freeze, frozen_tree, represent_protected_areas
from tree_design.materialise import (
    BranchEvidence, MaterialisationRefused, materialise_branch,
    project_branch_nodes, project_branch_preview,
)
from tree_design.profiles import build_profiles
from tree_design.records import Node, PlanVersion, derive_accepts_placement
from tree_design.residuals import ResidualChoice, ResidualTemplate, project_residual_nodes
from tree_design.routing import BranchContext, CompositionCandidate, RoutingReport, route_branch
from tree_design.store import (
    apply_review_action, nodes_for_version, write_node, write_plan_version,
)
from tree_design.templates import CompositionConflict
from tree_design.upstream import (
    AcceptedGroup, ProtectedArea, UpstreamUnavailable, accepted_groups,
    cross_folder_moves, existing_folders, protected_areas,
)
from tree_design.validation import ValidationReport, run_checks
from tree_design.vocabulary import (
    ACCEPT, ADD_SCOPED_GENERAL, ORDINARY, PROPOSED, SET_SHARED_MATERIAL_POLICY,
)

#: §5's chain, in §5's order, plus §6.1 and §8.8. Named so the shape is checkable
#: against the design rather than against this file — the same reason
#: `placement.pipeline.STEPS` names §6.12's nine. Steps 10 and 11 here ARE P11's
#: own steps 1 and 2 (`freeze_approved_tree`, `profile_each_node`), which is what
#: makes the two lists meet rather than merely adjoin.
STEPS: tuple[str, ...] = (
    "read_upstream_evidence",        # §5.3, §5.10, §5.2 — P9, P3, P6, P7
    "offer_top_level_branches",      # §5.3  horizontal_candidates
    "route_each_branch",             # §5.7  route_branch, C1-C8
    "materialise_from_facts",        # §5.4  materialise_branch
    "validate_against_v1_v6",        # §5.7  run_checks
    "offer_vertical_options",        # §5.5  vertical_options, §5.9's warnings
    "apply_the_users_decisions",     # §5.12 apply_review_action
    "enable_the_residual_library",   # §7.4  project_residual_nodes
    "represent_protected_areas",     # §5.2, §8.4
    "profile_each_node",             # §6.1  build_profiles          — P11 step 2
    "freeze_the_approved_tree",      # §8.8  freeze                  — P11 step 1
)


class NothingToDesign(RuntimeError):
    """The corpus reached the chain with no accepted group to build from.

    Distinct from a refusal: `validate_for_freeze` would say "this version holds
    no node", which describes the symptom one stage later and not the cause. §5.3
    builds the top level out of accepted groups, existing folders and user
    labels; with none of them there is no design to make and saying so here is
    what stops an empty frozen tree being adopted as if it were one.
    """


@dataclass(frozen=True)
class SharedMaterialAnswer:
    """§6.9's policy, and where its branch sits when it has one.

    `parent_origin_id = None` means "the single top-level branch this run built",
    which is the ordinary case and saves the caller re-deriving an id the chain
    minted. It is resolved to a real origin id before the action is applied, so
    the action still names one node and `_write_overlap_answer` still matches by
    lineage.
    """

    policy: str
    reason: str
    parent_origin_id: str | None = None
    display_label: str = "Shared Material"
    policy_scope: str | None = None


@dataclass(frozen=True)
class ScopedGeneralAnswer:
    """`00`:99's scoped General, inside a meaningful parent and never at the root."""

    parent_origin_id: str | None = None
    display_label: str = "General"


@dataclass(frozen=True)
class TreeDesignAuthorities:
    """Everything §5 needs that the design declines to state.

    Every field is required. `tree_design.config` states the rule for limits and
    it holds for all of these: "absent means refuse, never guess". A default for
    `collapse_handling_classes` in particular could give a branch a weaker floor
    than one of its own files requires, which is why P10 refuses one everywhere
    else it appears.
    """

    catalogue: object
    group_reader: object
    limits: TreeLimits
    root_anchor: str
    selection_id: str
    scan_run_id: str
    active_domains: tuple[str, ...]
    sensitive_group_ids: frozenset[str]
    privacy_rank: Callable[[str], int]
    satisfies_purpose_profile: Callable[[object, Sequence[AcceptedGroup]], bool]
    rank_candidates: Callable[[Sequence[CompositionCandidate]],
                              Sequence[CompositionCandidate]]
    handling_class_for_member: Callable[[object], str]
    collapse_handling_classes: Callable[[frozenset[str]], str]
    handling_class_for_area: Callable[[ProtectedArea], str]
    protected_handling_classes: frozenset[str] | None
    collector_field_keys: frozenset[str]
    value_discloses_protected_material: Callable[[str | None, str], bool] | None
    template_context_for: Callable[[str | None, int], object | None]
    mint_node_id: Callable[[], str]
    mint_version_id: Callable[[], str]

    def __post_init__(self) -> None:
        if not isinstance(self.limits, TreeLimits):
            raise ConfigurationRequired(
                "the chain runs under P1's tree ceilings and §5.9's thresholds, "
                "read through `tree_design.config.tree_limits`; a run with no "
                "limits is a run under a bound nobody chose")
        for name in ("root_anchor", "selection_id", "scan_run_id"):
            if not getattr(self, name):
                raise ConfigurationRequired(
                    f"{name} names the user's §1.1 choice and P10 supplies none")
        for name in ("privacy_rank", "satisfies_purpose_profile",
                     "rank_candidates", "handling_class_for_member",
                     "collapse_handling_classes", "handling_class_for_area",
                     "template_context_for", "mint_node_id", "mint_version_id"):
            if not callable(getattr(self, name)):
                raise ConfigurationRequired(
                    f"{name} is an injected authority with no default; the "
                    "design states no answer for it and one chosen here would "
                    "be P10 authoring the design")


@dataclass(frozen=True)
class TreeDesignDecisions:
    """Everything the USER decides. §5.7: a template is inert until approved."""

    from_plan_version: str
    #: Which accepted groups become top-level branches. §5.3's horizontal pass
    #: offers more than this; the user keeps some and deletes the rest.
    branch_group_ids: tuple[str, ...]
    #: §5.5. Given the branch and every option with its counts, warnings and
    #: validation report, which nesting the user took. A callable rather than a
    #: mapping because the options do not exist until the chain has computed
    #: them, and a caller naming `opt_0` in advance has chosen nothing.
    choose_option: Callable[[BranchCandidate, tuple[VerticalOption, ...]], str]
    #: §5.8, per node the chain writes. Returns `(disposition, reason)` or None.
    #: None is not a default — it is the state of a branch nobody answered, and
    #: `validate_for_freeze` refuses it for any node that would be a destination.
    refinement_for: Callable[[Node], tuple[str, str] | None]
    residual_library: Mapping[str, ResidualTemplate]
    residual_choices: tuple[ResidualChoice, ...]
    residual_configuration: Mapping[str, str]
    residual_handling_class: Callable[[str], str]
    #: §5.8's answer for the residual nodes. They are legal destinations like any
    #: other and §7.2 caps their depth, so the answer is one pair for all of them
    #: rather than a callable — a per-template answer would be a question §7.4
    #: does not ask the user.
    residual_refinement: tuple[str, str] | None
    created_at: str
    user_id: str
    component_version: str
    shared_material: SharedMaterialAnswer | None = None
    scoped_general: tuple[ScopedGeneralAnswer, ...] = ()

    def __post_init__(self) -> None:
        for name in ("from_plan_version", "created_at", "user_id",
                     "component_version"):
            if not getattr(self, name):
                raise ConfigurationRequired(f"{name} is required on a design run")
        for name in ("choose_option", "refinement_for", "residual_handling_class"):
            if not callable(getattr(self, name)):
                raise ConfigurationRequired(
                    f"{name} is the user's decision arriving as a callable; a "
                    "chain that answered it would be choosing for them")


@dataclass(frozen=True)
class BranchDesign:
    """One top-level branch, and everything §5 produced on the way to it."""

    origin_node_id: str
    candidate: BranchCandidate
    routing: RoutingReport
    options: tuple[VerticalOption, ...]
    chosen_option_id: str
    evidence: BranchEvidence | None
    #: §5.9's warnings for the option the user took, computed by
    #: `vertical_options` over `health.warnings_for` and `parent_concepts_for`.
    warnings: tuple[object, ...]


@dataclass(frozen=True)
class TreeDesignResult:
    """What the chain produced, in one object, so nothing is re-derived.

    `tree` is the value `freeze.frozen_tree(conn, plan_version=...)` returns —
    read back through the seam function rather than kept from the write, because
    P11 reads it that way and a bundle that differed between the two would be a
    seam nobody had crossed.
    """

    tree: FrozenTree
    plan_version_ids: tuple[str, ...]
    branches: tuple[BranchDesign, ...]
    protected_areas: tuple[ProtectedArea, ...]


# --- step 1 -------------------------------------------------------------------------


def _upstream(conn, authorities, decisions):
    groups = accepted_groups(authorities.group_reader,
                             plan_version_id=decisions.from_plan_version)
    folders = existing_folders(conn, scan_run_id=authorities.scan_run_id)
    areas = protected_areas(conn, scan_run_id=authorities.scan_run_id)
    moves = cross_folder_moves(conn, selection_id=authorities.selection_id)
    return groups, folders, areas, moves


# --- steps 3 to 6, for one branch ---------------------------------------------------


def _route(conn, authorities, *, branch_node_id: str,
           group: AcceptedGroup) -> RoutingReport:
    context = BranchContext(
        branch_node_id=branch_node_id,
        # `group.domain` is P9's `group_category`, which is the schema an
        # applicability row is eligible in. A group with none is eligible for no
        # row, and that is a real state — `tests/p10/p9_fixtures.py` records that
        # live P9 emits unlabelled groups today — so it produces a C3 conflict
        # rather than being widened to every schema here.
        domains=() if group.domain is None else (group.domain,),
        accepted_groups=(group,),
        member_file_ids=frozenset(member.file_id for member in group.members),
        handling_classes=frozenset(
            authorities.handling_class_for_member(member)
            for member in group.members),
    )
    return route_branch(
        conn, authorities.catalogue, context, limits=authorities.limits,
        privacy_rank=authorities.privacy_rank,
        satisfies_purpose_profile=authorities.satisfies_purpose_profile,
        rank_candidates=authorities.rank_candidates)


def _option_bindings(conn, authorities, *, parent: Node, group: AcceptedGroup):
    """`materialise`, `validate` and `preview` for one branch, sharing one pass.

    `vertical_options` calls all three per candidate and they must agree: a
    validator that saw different levels from the projection would accept a tree
    that cannot be built, or refuse one that can. So `materialise_branch` runs
    once per candidate and both views are remembered.
    """
    # Keyed on the candidate RECORD, not on `id(candidate)`: `CompositionCandidate`
    # is a frozen dataclass and hashes by value, so two calls about the same
    # composition find the same pass — which is the property the three bindings
    # have to share.
    materialised: dict[CompositionCandidate, object] = {}
    evidence_by_candidate: dict[CompositionCandidate, BranchEvidence] = {}
    reports: dict[CompositionCandidate, ValidationReport] = {}

    def materialise(candidate: CompositionCandidate) -> BranchEvidence | None:
        try:
            candidate_view, evidence = materialise_branch(
                conn, candidate, branch_node_id=parent.node_id,
                members=group.members, ancestor_field_refs=(), ancestor_depth=0,
                handling_class_for_member=authorities.handling_class_for_member,
                protected_handling_classes=authorities.protected_handling_classes)
        except (MaterialisationRefused, UpstreamUnavailable, CompositionConflict):
            # §8.6 wants deferred work visible rather than absent: a candidate
            # that cannot be populated still becomes an option, with no counts
            # and its own summary, instead of vanishing from the canvas.
            return None
        materialised[candidate] = candidate_view
        evidence_by_candidate[candidate] = evidence
        return evidence

    def validate(candidate: CompositionCandidate) -> ValidationReport | None:
        view = materialised.get(candidate)
        if view is None:
            return None
        report = run_checks(
            view, report_id=f"vr_{parent.origin_node_id}_{len(reports)}",
            limits=authorities.limits,
            collector_field_keys=authorities.collector_field_keys,
            value_discloses_protected_material=(
                authorities.value_discloses_protected_material))
        reports[candidate] = report
        return report

    def preview(candidate: CompositionCandidate, evidence: BranchEvidence):
        return project_branch_preview(
            evidence, _accepted_or_provisional(reports.get(candidate)),
            parent=parent, plan_version_id=parent.plan_version_id,
            mint_node_id=authorities.mint_node_id,
            handling_class_for=authorities.collapse_handling_classes,
            template_context_for=authorities.template_context_for)

    return materialise, validate, preview, evidence_by_candidate, reports


def _accepted_or_provisional(report: ValidationReport | None) -> ValidationReport:
    """The report a PREVIEW is built under.

    `project_branch_preview` refuses a failed report, and rightly — §5.7's checks
    gate the build. But §8.6 requires a failing option to stay on the canvas WITH
    its reason, and an option with no preview has no counts to show. So the
    preview is built under a provisional accepted report and the real one travels
    beside it on `VerticalOption.validation`, where the user reads it. Nothing is
    written from a preview; the build path below uses the REAL report and is
    refused by it.
    """
    if report is not None and report.accepted:
        return report
    return ValidationReport(report_id="vr_preview", passed=(), failures=())


# --- step 7: the user's decisions become versions -----------------------------------


@dataclass(frozen=True)
class _Action:
    """P13's `review_action`, as P13's SPEC publishes its fields.

    P13 is specification only and has no producer, so the chain builds the record
    it would send. `tests/p10/p13_fixtures.py` declares the same shape for the
    same reason; this is `src/`'s copy because a source module may not import a
    test one, and the day P13 ships both are replaced by its record.
    """

    review_action_id: str
    surface: str
    subject_ref: str
    plan_version: str
    action: str
    correction_scope: str
    presented_state_ref: str
    user_id: str
    observed_at: str
    payload: dict = field(default_factory=dict)


def _with_refinement(node: Node, refinement_for) -> Node:
    """§5.8's answer, stamped on a node the chain is about to write.

    Nothing in P10 wrote this field. `project_branch_nodes` leaves it `None`,
    `project_residual_nodes` leaves it `None`, and there is no `set-refinement-
    disposition` review action — so every tree P10 actually built carried `None`
    on every node, and `build_destination_index` refuses such a tree WHOLE. The
    answer is the user's (§5.8: it distinguishes intentional shallowness from
    unfinished work), so it arrives injected and is applied here, at the one
    place that writes.

    A node that is not a destination is left alone. `Node.__post_init__` pairs
    the disposition with its reason, so both are set or neither is.
    """
    if not node.accepts_placement or node.refinement_disposition is not None:
        return node
    answer = refinement_for(node)
    if answer is None:
        return node
    disposition, reason = answer
    return dataclasses.replace(node, refinement_disposition=disposition,
                               refinement_reason=reason)


def _top_level_node(candidate: BranchCandidate, *, plan_version_id: str,
                    authorities: TreeDesignAuthorities,
                    member_classes: frozenset[str]) -> Node:
    node_id = authorities.mint_node_id()
    return Node(
        node_id=node_id, plan_version_id=plan_version_id, node_type=PROPOSED,
        display_label=candidate.display_label, parent_node_id=None,
        root_anchor=authorities.root_anchor, ordinal=0,
        associated_group_ids=candidate.accepted_group_ids,
        explanation=candidate.why_suggested, node_role=ORDINARY,
        accepts_placement=derive_accepts_placement(
            PROPOSED, protected_movement_permitted=False),
        # The classes the branch's own members carry, collapsed by the injected
        # authority. P7 publishes `HANDLING_CLASSES` as a set and no ordering, so
        # a rank chosen here could give the branch a weaker floor than one of its
        # files requires — the same reason `project_branch_nodes` refuses a
        # default for it. A branch with no members yet hands over an empty set
        # and the authority answers for that too.
        handling_class=authorities.collapse_handling_classes(member_classes),
        origin_node_id=node_id)


# --- the chain ----------------------------------------------------------------------


def design_tree(conn: sqlite3.Connection, *,
                authorities: TreeDesignAuthorities,
                decisions: TreeDesignDecisions) -> TreeDesignResult:
    """§5's eleven steps over one corpus, ending in the bundle P11 reads.

    The version chain is real. Each accepted decision goes through
    `apply_review_action`, which opens a draft and mints a new `node_id` for
    every node it copies (§8.8), so a run of N decisions produces N+1 versions
    and the ids of the tree the user sees are not the ids of the tree they
    started from. That is the condition `placement.versions.reproject` exists
    for, and it is why this chain — rather than a fixture that reuses ids — is
    what the §8.8 identity contract has to be tested against.
    """
    groups, folders, areas, moves = _upstream(conn, authorities, decisions)
    by_id = {group.group_id: group for group in groups}

    candidates = horizontal_candidates(
        conn, accepted=groups, existing_folders=folders, user_labels=(),
        active_domains=authorities.active_domains,
        sensitive_group_ids=authorities.sensitive_group_ids)
    chosen = tuple(candidate for candidate in candidates
                   if candidate.subject_id in set(decisions.branch_group_ids))
    if not chosen:
        raise NothingToDesign(
            f"none of {sorted(decisions.branch_group_ids)} is a top-level branch "
            f"candidate for {decisions.from_plan_version!r}. §5.3 builds the top "
            "level out of accepted groups, existing folders and user labels, and "
            "a tree with no branch is not a design the user approved"
        )

    version = _open_first_draft(conn, authorities, decisions, moves)
    versions = [version]
    branches: list[BranchDesign] = []

    for candidate in chosen:
        group = by_id[candidate.subject_id]
        version, design = _design_one_branch(
            conn, authorities, decisions, candidate=candidate, group=group,
            version=version)
        versions.append(version)
        branches.append(design)

    default_parent = branches[0].origin_node_id
    for answer in decisions.scoped_general:
        version = _apply(conn, authorities, decisions, action=_Action(
            review_action_id=f"ra_general_{answer.parent_origin_id or default_parent}",
            surface="canvas",
            subject_ref=answer.parent_origin_id or default_parent,
            plan_version=version, action=ADD_SCOPED_GENERAL,
            correction_scope="node",
            presented_state_ref=f"ps_{answer.parent_origin_id or default_parent}",
            user_id=decisions.user_id, observed_at=decisions.created_at,
            payload={"display_label": answer.display_label}))
        versions.append(version)

    if decisions.shared_material is not None:
        answer = decisions.shared_material
        parent = answer.parent_origin_id or default_parent
        version = _apply(conn, authorities, decisions, action=_Action(
            review_action_id=f"ra_shared_{parent}", surface="canvas",
            subject_ref=parent, plan_version=version,
            action=SET_SHARED_MATERIAL_POLICY, correction_scope="corpus",
            presented_state_ref=f"ps_{parent}", user_id=decisions.user_id,
            observed_at=decisions.created_at,
            payload={"policy": answer.policy, "reason": answer.reason,
                     "display_label": answer.display_label,
                     "policy_scope": answer.policy_scope}))
        versions.append(version)

    _enable_residual_library(conn, authorities, decisions, version=version)
    represent_protected_areas(
        conn, plan_version_id=version, areas=areas,
        root_anchor=authorities.root_anchor,
        mint_node_id=authorities.mint_node_id,
        handling_class_for=authorities.handling_class_for_area)

    profiles = build_profiles(
        conn, plan_version_id=version, groups_by_id=by_id,
        document_types_by_node={}, anchor_excerpts_by_node={},
        user_edits_by_node={}, node_scoped_rejections={})
    freeze(
        conn, plan_version_id=version, created_at=decisions.created_at,
        user_id=decisions.user_id,
        component_version=decisions.component_version,
        residual_configuration=decisions.residual_configuration,
        # The branches the user approved, which in this chain is exactly the
        # nodes their decisions produced. A protected area and an ignored folder
        # are in the tree as observed CONTEXT — the scan marked one and the user
        # left the other alone — and naming them approved would ask the user to
        # answer §5.8 about a branch they never designed.
        approved_branch_ids=tuple(
            node.node_id for node in nodes_for_version(conn, version)
            if node.accepts_placement),
        profiles=profiles, protected_areas=areas)

    return TreeDesignResult(
        tree=frozen_tree(conn, plan_version=version),
        plan_version_ids=tuple(versions), branches=tuple(branches),
        protected_areas=areas)


def _open_first_draft(conn, authorities, decisions, cross_folder: bool) -> str:
    """The version the chain starts from, carrying P3's §1.1 permission.

    `cross_folder_moves` is read from the selection rather than taken as an
    argument: P3 records the user's choice, P10 stores it under §8.8's placement
    policy settings, P12 enforces it. Taking it as a parameter would let a caller
    state a permission the user never gave.
    """
    version_id = authorities.mint_version_id()
    write_plan_version(conn, PlanVersion(
        plan_version_id=version_id, predecessor_id=None, state="draft",
        created_at=decisions.created_at, cross_folder_moves=cross_folder,
        selection_id=authorities.selection_id))
    return version_id


def _design_one_branch(conn, authorities, decisions, *, candidate, group,
                       version: str) -> tuple[str, BranchDesign]:
    """One branch: written, routed, materialised, judged, split.

    The top-level node is written directly into the current draft and the SPLIT
    is what goes through `apply_review_action`. That asymmetry is §5.3's own: the
    horizontal pass produces the few major areas and the vertical pass is the
    edit the user makes to one of them, which §8.8 turns into a version.
    """
    parent = _with_refinement(
        _top_level_node(candidate, plan_version_id=version,
                        authorities=authorities,
                        member_classes=frozenset(
                            authorities.handling_class_for_member(member)
                            for member in group.members)),
        decisions.refinement_for)
    write_node(conn, parent)

    report = _route(conn, authorities, branch_node_id=parent.node_id, group=group)
    materialise, validate, preview, evidence_by, reports = _option_bindings(
        conn, authorities, parent=parent, group=group)
    options = vertical_options(
        report, branch_members=[member.file_id for member in group.members],
        materialise=materialise, validate=validate, limits=authorities.limits,
        preview=preview)
    option_id = decisions.choose_option(candidate, options)
    chosen = next((option for option in options
                   if option.option_id == option_id), None)
    if chosen is None:
        raise ConfigurationRequired(
            f"{option_id!r} is not one of the options offered for "
            f"{candidate.display_label!r} "
            f"({sorted(option.option_id for option in options)}). §5.5 shows the "
            "user what each option would create and the answer names one of them"
        )

    # `vertical_options` emits one option per routed candidate IN ORDER and then
    # appends `opt_no_split`, so an option's position IS its candidate's — which
    # is why the position is read rather than the `opt_N` string parsed: the id
    # scheme is that function's and this one does not restate it.
    index = next((position for position, option in enumerate(options)
                  if option.option_id == option_id), None)
    if index is None or index >= len(report.candidates):
        # `opt_no_split` — "keep this branch as it is". §5.5 always offers it and
        # a user who takes it has designed the branch, not failed to.
        return version, BranchDesign(
            origin_node_id=parent.origin_node_id, candidate=candidate,
            routing=report, options=options, chosen_option_id=option_id,
            evidence=None, warnings=chosen.warnings)

    composition = report.candidates[index]
    evidence = evidence_by.get(composition)
    validation = reports.get(composition)
    if evidence is None or validation is None:
        raise MaterialisationRefused(
            f"option {option_id!r} for {candidate.display_label!r} could not be "
            "populated from this branch's facts, so accepting it would write "
            "nodes nothing supports (§5.4)")

    new_version = _apply(conn, authorities, decisions, action=_Action(
        review_action_id=f"ra_accept_{parent.origin_node_id}", surface="canvas",
        subject_ref=parent.origin_node_id, plan_version=version, action=ACCEPT,
        correction_scope="node", presented_state_ref=f"ps_{option_id}",
        user_id=decisions.user_id, observed_at=decisions.created_at,
        payload={"option_id": option_id}),
        project=_projection(conn, authorities, decisions, evidence=evidence,
                            validation=validation,
                            parent_origin_id=parent.origin_node_id))
    return new_version, BranchDesign(
        origin_node_id=parent.origin_node_id, candidate=candidate,
        routing=report, options=options, chosen_option_id=option_id,
        evidence=evidence, warnings=chosen.warnings)


def _projection(conn, authorities, decisions, *, evidence, validation,
                parent_origin_id: str):
    """`project_branch_nodes`, bound to the DRAFT's copy of the parent.

    §8.8's identity rule bites here and nowhere else in this module: `open_draft`
    minted a new `node_id` for the whole copied tree, so the parent handed to the
    projection has to be looked up by `origin_node_id`. A caller passing the
    pre-draft parent would project every child onto an id the new version does
    not contain, and each one would hang off nothing.
    """
    def project(_action, plan_version_id: str) -> tuple[Node, ...]:
        parent = next(node for node in nodes_for_version(conn, plan_version_id)
                      if node.origin_node_id == parent_origin_id)
        return tuple(
            _with_refinement(node, decisions.refinement_for)
            for node in project_branch_nodes(
                evidence, validation, parent=parent,
                plan_version_id=plan_version_id,
                mint_node_id=authorities.mint_node_id,
                handling_class_for=authorities.collapse_handling_classes,
                template_context_for=authorities.template_context_for))
    return project


def _apply(conn, authorities, decisions, *, action: _Action, project=None) -> str:
    return apply_review_action(
        conn, action, new_version_id=authorities.mint_version_id(),
        created_at=decisions.created_at,
        mint_node_id=authorities.mint_node_id,
        component_version=decisions.component_version, project=project)


def _enable_residual_library(conn, authorities, decisions, *, version: str) -> None:
    """§7.4's enabled branches, into the draft that is about to be frozen.

    They are written directly and not through a review action because §7.4's
    enablement is a decision about the LIBRARY rather than an edit to a node:
    `enable-residual` is one of the tree-edit actions `apply_review_action`
    refuses by name for want of a writer, and routing them through `accept` would
    record the wrong gesture in the event log.
    """
    if not decisions.residual_choices:
        return
    existing = {node.node_id: node for node in nodes_for_version(conn, version)}
    default_parent = next(
        (node for node in existing.values() if node.parent_node_id is None), None)
    nodes = project_residual_nodes(
        decisions.residual_library, decisions.residual_choices,
        plan_version_id=version,
        handling_class_for_template=decisions.residual_handling_class,
        mint_node_id=authorities.mint_node_id, existing_nodes=existing)
    for node in nodes:
        if node.parent_node_id is None and default_parent is not None:
            # `00`:99 again: a residual branch belongs inside a meaningful
            # parent, and "a global catch-all folder should not become the
            # product's default answer to ambiguity". A choice that named no
            # parent gets this run's top-level branch rather than the root.
            node = dataclasses.replace(node,
                                       parent_node_id=default_parent.node_id)
        write_node(conn, _with_refinement(
            node, lambda _node: decisions.residual_refinement))
