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
from types import MappingProxyType

from tree_design.candidates import (
    EXISTING_FOLDER_SOURCES, BranchCandidate, VerticalOption,
    horizontal_candidates, node_type_for, vertical_options,
)
from tree_design.config import ConfigurationRequired, TreeLimits
from tree_design.freeze import FrozenTree, freeze, frozen_tree, represent_protected_areas
from tree_design.materialise import (
    BranchEvidence, MaterialisationRefused, materialise_branch,
    project_branch_preview,
)
from tree_design.node_key import branch_key
from tree_design.profiles import build_profiles
from tree_design.records import (
    ExpectedValue, Node, PlanVersion, derive_accepts_placement,
)
from tree_design.residuals import ResidualChoice, ResidualTemplate, project_residual_nodes
from tree_design.routing import BranchContext, CompositionCandidate, RoutingReport, route_branch
from tree_design.store import (
    apply_review_action, nodes_for_version, write_node, write_plan_version,
)
from tree_design.templates import CompositionConflict
from tree_design.user_edits import UserLevelEdit, user_level_edits
from tree_design.upstream import (
    AcceptedGroup, AnchorAgreement, GroupMember, ProtectedArea,
    UpstreamUnavailable,
    accepted_groups, cross_folder_moves, existing_folders,
    file_ids_in_directory, group_level_reader, protected_areas,
    settled_values_by_directory,
)
from tree_design.validation import ValidationReport, run_checks
from tree_design.vocabulary import (
    ACCEPT, ADD_SCOPED_GENERAL, C3, EXISTING, ORDINARY, PROPOSED,
    REVIEW_SURFACES, SET_SHARED_MATERIAL_POLICY, check,
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
    #: Which of the 358 researched SITUATIONS one accepted group's evidence
    #: recognises, as `recognition:{row_id}` refs. Injected for the reason
    #: `facts.domains` gives about its own signals — *"P6 authors no activation
    #: signal … the signals arrive as an injected `ActivationSignals` with no
    #: default"* — and for the same reason one part over: `src/recognition/`
    #: owns the patterns, and its detector answers at SCHEMA grain, naming a
    #: `schema_id` and never a row, because `compile_rules` unions every row's
    #: terms per schema. So the vocabulary exists upstream and the row-level
    #: producer does not; P10 reads the answer and writes no rule of its own.
    detection_signals_for: Callable[[AcceptedGroup], frozenset[str]]
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
    #: `104` §11.2 step 2, keyed by SCHEMA: the template roles whose value belongs
    #: to the accepted group rather than to each file. `production.
    #: GROUP_LEVEL_ROLES` is the deployment's answer and P10 derives none of it --
    #: which role means what is the library's, and `00`:57 is the sentence that
    #: makes coursework's school and term the group's.
    #:
    #: Defaulted to the empty mapping rather than required, and the default is the
    #: honest reading rather than a guess: with no mapping every level is the
    #: file's own, which is what P10 has always done and what 22 of the 23 schemas
    #: still mean. `protected_handling_classes` refuses its absence because a set
    #: chosen there would weaken a floor; a mapping missing here weakens nothing.
    group_level_roles: Mapping[str, frozenset[str]] = MappingProxyType({})
    #: `105` §14.4 with `104` R-131. What two anchors must BE before one of their
    #: values becomes a folder level: independently originating, non-conflicting,
    #: and about one course or one enrollment. `upstream.AnchorAgreement` carries
    #: the whole of the rule and every field key inside it is the deployment's.
    #:
    #: `None` is the rule as it stood before the ruling -- one anchor's value is
    #: the group's -- and it is the default for the same reason `group_level_roles`
    #: defaults empty: a deployment that has not been handed the ruling keeps the
    #: behaviour it had, and P10 authors neither the fields nor the rule.
    anchor_agreement: AnchorAgreement | None = None
    #: Packet G12. WHO TO ASK FOR A TEMPLATE when C3 refuses -- when this branch's
    #: evidence recognises no shipped situation and `00`:97's site E is the answer.
    #: Handed the branch's accepted groups and its plan version; returns nothing,
    #: because a template design that reached this chain would be structure nobody
    #: approved (`00`:97: "valid shape is not activation").
    #:
    #: `None` is the ordinary deployment and is not a refusal: a run with no model
    #: designs the branch exactly as it always has and the C3 refusal still reaches
    #: the person through the report.
    template_call_for: Callable[
        [Sequence[AcceptedGroup], str], None] | None = None

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
                     "detection_signals_for",
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
    #:
    #: `None` IS AN ANSWER AND IT IS "NOT YET" (`104` §18.42 item 1, R-92).
    #: `00`:66 designs the branches the person accepted and no others, so a
    #: branch whose shape is still the person's to pick gets no lower level on
    #: this run. It is deliberately not `opt_no_split`: the two build the same
    #: folders -- none -- and only one of them is somebody's decision, so
    #: recording "keep this branch as it is" for a person who has not spoken
    #: would be the engine taking their turn, which is the finding this exists
    #: to close. The branch node is still written and the options are still
    #: computed, because the screen has to show what is being asked.
    choose_option: Callable[[BranchCandidate, tuple[VerticalOption, ...]],
                            str | None]
    #: §5.8, per node the chain writes, WITH the number of files that node holds.
    #: The count is passed because every §5.8 answer is a claim about one — "few
    #: enough files that a further split would not help" is a sentence about a
    #: number — and `Node` carries no count, so a policy handed only the node
    #: could state that claim without ever being in a position to check it. It
    #: was: `cli.py` returned `shallow-by-choice` with exactly that sentence for
    #: every node with a parent, and attached it to a folder holding 21 files.
    #: Returns `(disposition, reason)` or None. None is not a default — it is the
    #: state of a branch nobody answered, and `validate_for_freeze` refuses it for
    #: any node that would be a destination.
    refinement_for: Callable[..., tuple[str, str] | None]
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
    #: Which of P13's review surfaces these decisions were collected on -- or
    #: `SURFACE_UNATTENDED`, when they were collected on none of them because
    #: nobody was at the screen. The chain stamps it on every review action it
    #: builds and on the freeze, and §8.2's sentences read it to decide whether
    #: they may say a person acted. Required, and deliberately not defaulted: a
    #: default would be this dataclass asserting somebody was watching.
    surface: str
    shared_material: SharedMaterialAnswer | None = None
    scoped_general: tuple[ScopedGeneralAnswer, ...] = ()

    def __post_init__(self) -> None:
        for name in ("from_plan_version", "created_at", "user_id",
                     "component_version", "surface"):
            if not getattr(self, name):
                raise ConfigurationRequired(f"{name} is required on a design run")
        # A surface outside the closed set would be interpolated into the audit
        # log verbatim, and a surface a deployment invented is a surface whose
        # meaning nobody designed.
        check(self.surface, REVIEW_SURFACES, name="review surface")
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
    #: `None` when nobody has answered this branch's shape yet -- see
    #: `TreeDesignDecisions.choose_option`. The options beside it are what the
    #: person is choosing between.
    chosen_option_id: str | None
    evidence: BranchEvidence | None
    #: §5.9's warnings for the option the user took, computed by
    #: `vertical_options` over `health.warnings_for` and `parent_concepts_for`.
    warnings: tuple[object, ...]
    #: The composition the user's chosen option was built from, or `None` when
    #: they took `opt_no_split`. `64` §5a reads `template_refs` off it: "the
    #: `(template_id, template_version)` set it ACTUALLY used" is the set the
    #: chosen options named, not every recipe that was merely offered.
    composition: CompositionCandidate | None = None


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
    #: §5.1's horizontal pass, WHOLE: every top-level candidate this run built a
    #: card for, including the ones the decisions did not select. `branches`
    #: holds the selected ones only, so without this a card the person has not
    #: accepted is computed and then dropped -- which is `104` §18.42 item 1's
    #: "branch cards live on `BranchCandidate` and no screen renders them", one
    #: layer down: a screen cannot render what the chain does not return.
    candidates: tuple[BranchCandidate, ...] = ()


# --- step 1 -------------------------------------------------------------------------


def _upstream(conn, authorities, decisions):
    groups = accepted_groups(authorities.group_reader,
                             plan_version_id=decisions.from_plan_version)
    folders = existing_folders(conn, scan_run_id=authorities.scan_run_id)
    areas = protected_areas(conn, scan_run_id=authorities.scan_run_id)
    moves = cross_folder_moves(conn, selection_id=authorities.selection_id)
    return groups, folders, areas, moves


# --- steps 3 to 6, for one branch ---------------------------------------------------


def _members(groups: Sequence[AcceptedGroup]) -> tuple[GroupMember, ...]:
    """Every member of every group in one branch, in branch order.

    Deduplicated on `file_id`: two groups in one branch may both claim a file —
    that is §6.9's shared material — and a member counted twice would inflate
    every count the user reads before choosing a split.
    """
    seen: set[str] = set()
    members = []
    for group in groups:
        for member in group.members:
            if member.file_id in seen:
                continue
            seen.add(member.file_id)
            members.append(member)
    return tuple(members)


def _route(conn, authorities, *, branch_node_id: str,
           groups: Sequence[AcceptedGroup],
           user_edits: Sequence[UserLevelEdit] = ()) -> RoutingReport:
    members = _members(groups)
    context = BranchContext(
        branch_node_id=branch_node_id,
        # `group.domain` is P9's `group_category`, which is the schema an
        # applicability row is eligible in. A group with none is eligible for no
        # row, and that is a real state — `tests/p10/p9_fixtures.py` records that
        # live P9 emits unlabelled groups today — so it produces a C3 conflict
        # rather than being widened to every schema here.
        #
        # EVERY domain the branch's groups carry, not one. A branch holding two
        # lives is eligible for both their recipes, and `route_branch` composes
        # per coverage so neither refuses on account of the other.
        domains=tuple(dict.fromkeys(
            group.domain for group in groups if group.domain is not None)),
        accepted_groups=tuple(groups),
        member_file_ids=frozenset(member.file_id for member in members),
        handling_classes=frozenset(
            authorities.handling_class_for_member(member)
            for member in members),
        # The UNION over the branch's groups, for the same reason `domains` is
        # a union: a branch holding two lives recognises both their situations,
        # and `route_branch` composes per coverage afterwards so neither life's
        # recipe is refused on account of the other's.
        detection_signals=frozenset().union(
            *(authorities.detection_signals_for(group) for group in groups)),
    )
    return route_branch(
        conn, authorities.catalogue, context, limits=authorities.limits,
        privacy_rank=authorities.privacy_rank,
        satisfies_purpose_profile=authorities.satisfies_purpose_profile,
        rank_candidates=authorities.rank_candidates,
        # `64` §1's third hole, closed. The chain fed NO user vocabulary into
        # routing, so a rename lived on one node in one plan version and the
        # next route re-derived the catalogue's word over it.
        user_edits=user_edits)


def _ask_for_a_template(authorities, report: RoutingReport, *,
                        groups: Sequence[AcceptedGroup],
                        plan_version: str) -> None:
    """Packet G12: a C3 refusal becomes a site-E request, or nothing happens.

    C3 is the gate that refuses to widen "to every row sharing a schema", and its
    message is the one place the product says *"no recipe recognises the situation
    these files are in"*. `00`:97's site E is the answer to exactly that sentence,
    and until now the refusal reached no caller: E "can be ratified and stay
    inert".

    **P10 asks and reads nothing back.** The callable is injected, takes the
    groups the refusal is about, and returns nothing at all -- there is no result
    for this chain to act on, because `00`:97 ends with "valid shape is not
    activation: the person reviews, edits and accepts or discards", and the canvas
    that review happens on is Release 2. A return value would be a template design
    reaching a tree nobody approved.

    **`None` is the ordinary deployment.** A run with no model, or one whose E
    tier is not on this device, asks nobody and designs the branch exactly as it
    always has; the refusal is still in the report and still reaches the person.
    """
    if authorities.template_call_for is None:
        return
    if not any(conflict.gate == C3 for conflict in report.conflicts):
        return
    authorities.template_call_for(groups, plan_version)


def _group_level_roles(authorities, candidate: CompositionCandidate) -> frozenset[str]:
    """The roles this candidate fills from the group. `104` §11.2 step 2.

    Read off the candidate's OWN applicability rows, because the mapping is keyed
    by schema and a branch may hold several lives: `cycle_period` is the course's
    term under `academic` and a statement month under commerce, and a branch that
    holds both must not make the second one the group's.

    P10 authors none of it. `TreeDesignAuthorities.group_level_roles` is the
    composition root's answer, and the catalogue is what turns a row into a schema.
    """
    roles = authorities.group_level_roles
    if not roles:
        return frozenset()
    rows = authorities.catalogue.applicabilities
    found: set[str] = set()
    for ref in candidate.applicability_refs:
        row = rows.get(ref.key())
        if row is not None:
            found |= set(roles.get(row.uses_schema, frozenset()))
    return frozenset(found)


def _option_bindings(conn, authorities, *, parent: Node,
                     members: Sequence[GroupMember],
                     groups: Sequence[AcceptedGroup] = ()):
    """`materialise`, `validate` and `preview` for one branch, sharing one pass.

    `vertical_options` calls all three per candidate and they must agree: a
    validator that saw different levels from the projection would accept a tree
    that cannot be built, or refuse one that can. So `materialise_branch` runs
    once per candidate and both views are remembered.

    `groups` is the branch's own accepted groups and is what makes `104` §11.2
    step 2 answerable: a group-level dimension's value is read off the GROUP a
    member belongs to, so the members have to be traceable back to their groups
    here, where both are in hand. A member in no group of this branch has no such
    value and is unresolved at that level.

    The reader is `upstream`'s, and per group rather than per member: the answer
    does not vary between a group's members, and asking it once for each of them
    was `104` R-110 -- 47.9 of 77.8 profiled seconds at a thousand files, and
    essentially the whole of P8--P11 at five thousand. It lives exactly as long as
    this branch's pass over its own candidates.
    """
    # `105` §14.4 travels with the reader rather than beside it: the agreement is
    # about which anchors may speak for a group, and the reader is the one place
    # that question is answered.
    group_value_for_member = group_level_reader(
        conn, groups=groups, agreement=authorities.anchor_agreement)
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
                members=members, ancestor_field_refs=(), ancestor_depth=0,
                handling_class_for_member=authorities.handling_class_for_member,
                protected_handling_classes=authorities.protected_handling_classes,
                # `104` §11.2 step 2. The roles are the deployment's answer, read
                # here for THIS candidate's own schemas so a role that is the
                # group's under `academic` stays the file's under a recipe that
                # means something else by it.
                group_level_roles=_group_level_roles(authorities, candidate),
                group_value_for_member=group_value_for_member)
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


def _with_refinement(node: Node, refinement_for, *, file_count: int,
                     was_split: bool) -> Node:
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

    `file_count` is the number of files this node holds, and it is REQUIRED with
    no default. §5.8's answers are claims about that number, and a default here
    would let the chain hand a policy a count nobody measured — which is the
    shape the defect took the first time: the answer was stated, the number never
    read, and the sentence was wrong about a real folder by twenty files.

    `was_split` is required for the same reason and answers the other half: this
    function runs BEFORE a branch is routed, so the verdict it stamps there is
    about a branch that has no children YET. `_projection` re-derives it once the
    children exist -- see `_restamped` -- because `refine-later` on a branch that
    was in fact just refined is a false sentence in the person's own voice.
    """
    if not node.accepts_placement or node.refinement_disposition is not None:
        return node
    answer = refinement_for(node, file_count, was_split=was_split)
    if answer is None:
        return node
    disposition, reason = answer
    return dataclasses.replace(node, refinement_disposition=disposition,
                               refinement_reason=reason)


def _top_level_node(candidate: BranchCandidate, *, plan_version_id: str,
                    authorities: TreeDesignAuthorities,
                    member_classes: frozenset[str],
                    parent_node_id: str | None = None,
                    expected_values: tuple[ExpectedValue, ...] = (),
                    associated_groups: tuple[str, ...] = ()) -> Node:
    """The node one accepted card becomes -- proposed, or the person's own.

    §5.3 builds the top level "out of the accepted groups, domain memberships,
    existing CURATED FOLDERS, and user-approved labels", and until this function
    read the card's SOURCE it made all four the same thing: a `proposed` node,
    which is a folder that does not exist yet. For the two sources that name a
    directory the scan actually read, that was a false claim in the one place the
    user is most likely to check -- `00`:100 gives them six gestures over their
    own folders and every one of them presumes the product knows which folders
    are theirs.

    So an adopted card is written as `00`:102's `existing` node, carrying the
    real `existing_path`. The difference is not cosmetic. A `proposed` node
    labelled `PHYS1401` at the root is an offer to MOVE `Uni/PHYS1401/lab.txt`
    out of the folder it is already in, and doing that to every folder at once
    flattens the hierarchy in the name of honouring it.

    `parent_node_id` is how the rest of that promise is kept: an adopted folder
    whose own parent was also adopted hangs beneath it, so the shape the person
    built survives adoption. It stays `None` for a proposal, which has no place
    on disk to inherit one from.
    """
    node_id = authorities.mint_node_id()
    adopted = candidate.source in EXISTING_FOLDER_SOURCES
    return Node(
        node_id=node_id, plan_version_id=plan_version_id,
        # `candidates.node_type_for`, so the word the CARD prints and the word
        # the frozen node carries cannot come apart (`104` §18.42 items 1, 5).
        node_type=node_type_for(candidate),
        # An observed fact about the corpus, never a composition -- which is why
        # `Node.__post_init__` refuses it on any other type. The candidate's
        # `subject_id` IS the directory path for these two sources.
        existing_path=candidate.subject_id if adopted else None,
        display_label=candidate.display_label, parent_node_id=parent_node_id,
        # What the folder's own contents already agree on (§6.2). Empty for a
        # proposal, whose expectations are composed by `_project` from the
        # branch's evidence rather than observed from a directory that does not
        # exist yet.
        expected_values=expected_values,
        root_anchor=authorities.root_anchor, ordinal=0,
        associated_group_ids=candidate.accepted_group_ids or associated_groups,
        explanation=candidate.why_suggested, node_role=ORDINARY,
        accepts_placement=derive_accepts_placement(
            node_type_for(candidate), protected_movement_permitted=False),
        # The classes the branch's own members carry, collapsed by the injected
        # authority. P7 publishes `HANDLING_CLASSES` as a set and no ordering, so
        # a rank chosen here could give the branch a weaker floor than one of its
        # files requires — the same reason `project_branch_nodes` refuses a
        # default for it. A branch with no members yet hands over an empty set
        # and the authority answers for that too.
        handling_class=authorities.collapse_handling_classes(member_classes),
        # `106` Phase 5.1 (SPEC OQ5 closed): the origin is the card's KEY --
        # the observed path for an adopted folder, the label for a proposal
        # -- so two runs that build the same branch agree about which node
        # it is. `node_id` is still minted per version.
        origin_node_id=branch_key(
            display_label=candidate.display_label,
            existing_path=candidate.subject_id if adopted else None))


def _adopt_parents_first(chosen: tuple[BranchCandidate, ...],
                         ) -> tuple[BranchCandidate, ...]:
    """Shallower adopted folders before deeper ones, and nothing else moved.

    An adopted folder finds its parent by looking for the node that parent
    directory ALREADY became, so a child designed first would find nothing and
    silently land at the root -- the flattening this whole path exists to avoid.

    Only the adopted cards are reordered, and they are spliced back into the very
    positions they occupied. §5.3 lists four sources for the top level and states
    no order among them; `branches[0]` is the default parent for a scoped General
    and for the shared-material policy, so a sort that reshuffled the whole
    sequence would quietly re-home two things nobody asked to move.
    """
    positions = [index for index, candidate in enumerate(chosen)
                 if candidate.source in EXISTING_FOLDER_SOURCES]
    # Separator counting is an ORDERING heuristic and carries no authority: the
    # parent link itself comes from P3's `parent_directory` below. Both
    # separators are counted because `upstream._folder_name` reads both.
    in_depth_order = sorted(
        (chosen[index] for index in positions),
        key=lambda candidate: (candidate.subject_id.count("/")
                               + candidate.subject_id.count("\\")))
    ordered = list(chosen)
    for index, candidate in zip(positions, in_depth_order):
        ordered[index] = candidate
    return tuple(ordered)


def _adopted_expectations(conn: sqlite3.Connection,
                          chosen: Sequence[BranchCandidate],
                          ) -> dict[str, tuple[ExpectedValue, ...]]:
    """§6.2's expectations for every adopted folder, read off their own contents.

    A proposal gets none here on purpose: its expectations are COMPOSED by
    `_project` out of the branch's evidence, and a folder that does not exist yet
    has no contents to be asked about.

    **Every folder at once, before the loop that consumes them.** Asked one branch
    at a time, this was P10's largest read: each call walked the whole corpus once
    per destination-eligible field to find out whether the folder's agreement
    divided anything (`104` R-79). The answers do not depend on each other, and
    nothing in the branch loop writes a fact, so asking together is the same
    question with the reads shared. `settled_values_by_directory` carries the
    reasoning.
    """
    folders = [candidate.subject_id for candidate in chosen
               if candidate.source in EXISTING_FOLDER_SOURCES]
    return {
        path: tuple(ExpectedValue(field=value.field_ref,
                                  value=value.canonical_value)
                    for value in settled)
        for path, settled in settled_values_by_directory(
            conn, directory_paths=folders).items()
    }


def _groups_already_held(conn: sqlite3.Connection, candidate: BranchCandidate, *,
                         groups: Sequence[AcceptedGroup]) -> tuple[str, ...]:
    """The accepted groups whose files are ALREADY IN this folder (`00`:100).

    `00`:100 lists this among what the person should see about a folder of their
    own -- "which extracted facts and accepted groups overlap with it" -- and it
    is also what makes an adopted folder reachable at all. §6.3 scores over four
    weighted channels and `ACCEPTED_GROUP` is two of the seven points; a folder
    the person made is not built FROM a group, so without this it carries
    `DIRECT_FACT` alone, 3/7 against a 0.5 threshold, and everything in it
    abstains `no_supported_destination`.

    Overlap is READ. A folder holding none of a group's files claims none of it,
    which is what stops every adopted folder inheriting every group in the corpus
    and scoring as though it held the whole collection.

    Immediate children only, for the reason `settled_values_in_directory` gives
    at length: a file in `Uni/PHYS1401` is evidence about `PHYS1401`, and letting
    it count for `Uni` as well would put the person's own tree in competition
    with itself at every level.
    """
    if candidate.source not in EXISTING_FOLDER_SOURCES:
        return ()
    here = file_ids_in_directory(conn, directory_path=candidate.subject_id)
    if not here:
        return ()
    return tuple(
        group.group_id for group in groups
        if any(member.file_id in here for member in group.members))


def _adopted_parent_id(conn: sqlite3.Connection, candidate: BranchCandidate, *,
                       parent_of: Mapping[str, str | None],
                       version: str) -> str | None:
    """The node this folder's own parent directory became, if it became one.

    Looked up in the CURRENT version rather than remembered from an earlier one.
    Every accepted decision re-mints a `node_id` for every node it copies (§8.8),
    so an id captured before a branch split would name a node this version does
    not contain -- and a dangling parent is a tree `validate_for_freeze` refuses
    whole, arriving from a folder the person merely happened to own.

    `None` when the parent directory was not adopted, which is the honest answer:
    §5.3 builds the top level out of what the user approved, and inventing the
    ancestors above an adopted folder would put folders in their tree that they
    did not choose.
    """
    if candidate.source not in EXISTING_FOLDER_SOURCES:
        return None
    parent_path = parent_of.get(candidate.subject_id)
    if parent_path is None:
        return None
    return next((node.node_id for node in nodes_for_version(conn, version)
                 if node.existing_path == parent_path), None)


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
    # READ, not injected. The whole point of `64` is that a rename outlives the
    # session it was made in, so a chain that took the overlay as a decision
    # would lose every edit the moment a caller forgot to pass it — which is
    # `64` §1's hole 3 in a different disguise.
    edits = user_level_edits(conn)

    wanted = frozenset(decisions.branch_group_ids)
    candidates = horizontal_candidates(
        conn, accepted=groups, existing_folders=folders, user_labels=(),
        active_domains=authorities.active_domains,
        sensitive_group_ids=authorities.sensitive_group_ids,
        # Only the drafts this decision names fold into an area; a stale draft
        # of the same label stays its own unchosen card (`same_label_areas`).
        foldable=wanted)
    # An AREA folded from several accepted drafts (`candidates.same_label_areas`,
    # `00`:67) is chosen when any of them was: `cli.design_decisions` names
    # every accepted draft, and a card keyed `area:<label>` is in no
    # `branch_group_ids` by itself. A single-draft card's `subject_id` is its
    # group id, so the first test is the one every existing pin passes.
    chosen = tuple(candidate for candidate in candidates
                   if candidate.subject_id in wanted
                   or any(group_id in wanted
                          for group_id in candidate.accepted_group_ids))
    if not chosen:
        raise NothingToDesign(
            f"none of {sorted(decisions.branch_group_ids)} is a top-level branch "
            f"candidate for {decisions.from_plan_version!r}. §5.3 builds the top "
            "level out of accepted groups, existing folders and user labels, and "
            "a tree with no branch is not a design the user approved"
        )

    # P3's own record of which directory sits inside which. Derived here rather
    # than by splitting the path, because the scan observed the relationship and
    # a separator rule invented in this module would be a second, rival answer.
    parent_of = {folder.directory_path: folder.parent_directory
                 for folder in folders}
    groups_all = tuple(groups)
    chosen = _adopt_parents_first(chosen)
    # Read before the loop, because the loop asks it once per branch and the
    # answer is a property of the corpus rather than of the branch (`104` R-79).
    expectations = _adopted_expectations(conn, chosen)

    version = _open_first_draft(conn, authorities, decisions, moves)
    versions = [version]
    branches: list[BranchDesign] = []

    for candidate in chosen:
        # Every group the candidate names, not the one its `subject_id` happens
        # to be. A candidate derived from an existing folder or a user label
        # names NO group — `by_id[candidate.subject_id]` raised `KeyError` on
        # both — and a candidate that aggregates several names several.
        version, design = _design_one_branch(
            conn, authorities, decisions, candidate=candidate,
            groups=tuple(by_id[group_id]
                         for group_id in candidate.accepted_group_ids),
            version=version, user_edits=edits,
            parent_node_id=_adopted_parent_id(
                conn, candidate, parent_of=parent_of, version=version),
            expected_values=expectations.get(candidate.subject_id, ()),
            associated_groups=_groups_already_held(
                conn, candidate, groups=groups_all))
        versions.append(version)
        branches.append(design)

    default_parent = branches[0].origin_node_id
    version = _add_scoped_generals(conn, authorities, decisions, version=version,
                                   default_parent=default_parent,
                                   versions=versions)

    if decisions.shared_material is not None:
        answer = decisions.shared_material
        parent = answer.parent_origin_id or default_parent
        version = _apply(conn, authorities, decisions, action=_Action(
            review_action_id=f"ra_shared_{parent}", surface=decisions.surface,
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
        user_id=decisions.user_id, surface=decisions.surface,
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
        profiles=profiles, protected_areas=areas,
        # §5a. `load_shipped_catalogue` already derives `release_id` as a digest
        # of exactly the bytes it read; the value existed and was simply never
        # carried onto the frozen tree, which made a library upgrade
        # undetectable rather than merely unhandled.
        catalogue_release_id=getattr(authorities.catalogue, "release_id", None),
        template_versions=tuple(
            ref for design in branches if design.composition is not None
            for ref in design.composition.template_refs))

    return TreeDesignResult(
        tree=frozen_tree(conn, plan_version=version),
        plan_version_ids=tuple(versions), branches=tuple(branches),
        protected_areas=areas, candidates=candidates)


def _add_scoped_generals(conn, authorities, decisions, *, version: str,
                         default_parent: str, versions: list[str]) -> str:
    """`00`:99's General into the version chain, one review action per parent.

    Factored out of `design_tree` because gap 11c asks for the SAME actions at a
    second moment -- after the placement pass has proved which parents want one --
    and two spellings of one gesture would be two answers to "what does adding a
    General record".
    """
    for answer in decisions.scoped_general:
        parent = answer.parent_origin_id or default_parent
        version = _apply(conn, authorities, decisions, action=_Action(
            review_action_id=f"ra_general_{parent}",
            surface=decisions.surface,
            subject_ref=parent,
            plan_version=version, action=ADD_SCOPED_GENERAL,
            correction_scope="node",
            presented_state_ref=f"ps_{parent}",
            user_id=decisions.user_id, observed_at=decisions.created_at,
            payload={"display_label": answer.display_label}))
        versions.append(version)
    return version


def mint_scoped_generals(conn: sqlite3.Connection, *,
                         authorities: TreeDesignAuthorities,
                         decisions: TreeDesignDecisions,
                         tree: TreeDesignResult) -> TreeDesignResult:
    """`00`:99's General, minted AFTER placement proved a file wants one.

    `104` §18.2 gap 11c. The owner's ruling of 10 Sep is that the General is minted
    on demand -- "only under a parent that actually has a file whose accepted facts
    support the parent and no leaf, never under every branch" -- and the demand is
    a placement outcome (`placement.versions.scoped_general_demand`), which the
    tree pass cannot see because it runs first. So the chain continues: the frozen
    version the files were placed against gains one review action per parent in
    demand, exactly the action `design_tree` applies when a person asks for one at
    the canvas, and the last version is frozen again.

    **THE NODE IS A PROPOSAL LIKE ANY OTHER.** It enters the plan and nothing
    else: P12's apply is what creates a folder on disk, and a General with no file
    in it would be created by neither, because a parent nothing demanded gets no
    action here at all.

    Returns the result unchanged, having written NOTHING, when no parent is in
    demand. That is the r37 case and the common one -- a corpus every file of
    which settles its levels asks for no catch-all, and a run that opened a draft
    to record that would show the person a new plan version that changed nothing.
    """
    if not decisions.scoped_general:
        return tree
    groups, _folders, areas, _moves = _upstream(conn, authorities, decisions)
    versions: list[str] = []
    version = _add_scoped_generals(
        conn, authorities, decisions, version=tree.tree.plan_version_id,
        default_parent=tree.branches[0].origin_node_id, versions=versions)
    # Rebuilt for the new version rather than carried: §6.1's profiles are keyed
    # on `node_id` and every one of them was just re-minted, so the frozen
    # bundle's profiles would name nodes this version does not contain.
    profiles = build_profiles(
        conn, plan_version_id=version,
        groups_by_id={group.group_id: group for group in groups},
        document_types_by_node={}, anchor_excerpts_by_node={},
        user_edits_by_node={}, node_scoped_rejections={})
    freeze(
        conn, plan_version_id=version, created_at=decisions.created_at,
        user_id=decisions.user_id, surface=decisions.surface,
        component_version=decisions.component_version,
        residual_configuration=decisions.residual_configuration,
        approved_branch_ids=tuple(
            node.node_id for node in nodes_for_version(conn, version)
            if node.accepts_placement),
        profiles=profiles, protected_areas=areas,
        catalogue_release_id=getattr(authorities.catalogue, "release_id", None),
        # Read off the version this one descends from. The recipes that built the
        # tree are the same recipes; re-deriving them would mean re-running §5's
        # composition over a tree that is already designed.
        template_versions=tree.tree.freeze_record.template_versions)
    return dataclasses.replace(
        tree, tree=frozen_tree(conn, plan_version=version),
        plan_version_ids=tree.plan_version_ids + tuple(versions))


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


def _design_one_branch(conn, authorities, decisions, *, candidate, groups,
                       version: str,
                       user_edits: Sequence[UserLevelEdit] = (),
                       parent_node_id: str | None = None,
                       expected_values: tuple[ExpectedValue, ...] = (),
                       associated_groups: tuple[str, ...] = (),
                       ) -> tuple[str, BranchDesign]:
    """One branch: written, routed, materialised, judged, split.

    The top-level node is written directly into the current draft and the SPLIT
    is what goes through `apply_review_action`. That asymmetry is §5.3's own: the
    horizontal pass produces the few major areas and the vertical pass is the
    edit the user makes to one of them, which §8.8 turns into a version.

    `groups` is PLURAL because `BranchCandidate.accepted_group_ids` is, and
    `Node.associated_group_ids` is, and §5.3's card is: "Academics, 201 files:
    ... includes five accepted course groups". This used to read ONE group per
    branch — the candidate's `subject_id` — so a branch naming three groups was
    designed from one, and the other two were absent from every count, every
    option and every level while the node it wrote still claimed all three.
    """
    members = _members(groups)
    parent = _with_refinement(
        _top_level_node(candidate, plan_version_id=version,
                        authorities=authorities,
                        member_classes=frozenset(
                            authorities.handling_class_for_member(member)
                            for member in members),
                        parent_node_id=parent_node_id,
                        expected_values=expected_values,
                        associated_groups=associated_groups),
        decisions.refinement_for,
        # §5.3's own count for this branch, not one re-derived here: for an
        # accepted group it is the size of its membership and for an adopted
        # folder it is the file count the scan observed in that directory.
        file_count=candidate.supporting_file_count,
        # Nothing has been routed yet, so this is a fact and not a guess. When a
        # split does happen, `_projection` re-derives the verdict.
        was_split=False)
    write_node(conn, parent)

    report = _route(conn, authorities, branch_node_id=parent.node_id,
                    groups=groups, user_edits=user_edits)
    _ask_for_a_template(authorities, report, groups=groups,
                        plan_version=parent.plan_version_id)
    materialise, validate, preview, evidence_by, reports = _option_bindings(
        conn, authorities, parent=parent, members=members, groups=groups)
    options = vertical_options(
        report, branch_members=[member.file_id for member in members],
        materialise=materialise, validate=validate, limits=authorities.limits,
        preview=preview)
    option_id = decisions.choose_option(candidate, options)
    if option_id is None:
        # `104` §18.42 item 1. THE BRANCH IS PRESENTED AND NOT DESIGNED. Its node
        # is written -- `00`:101's horizontal pass produces the few major areas
        # and that is a real product, and an adopted folder still carries the
        # expectations its own contents already agree on -- but nothing is routed
        # into it, no `accept` action is applied, and the version is returned
        # unchanged, so the freeze that follows contains no level nobody chose.
        return version, BranchDesign(
            origin_node_id=parent.origin_node_id, candidate=candidate,
            routing=report, options=options, chosen_option_id=None,
            evidence=None, warnings=())
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
        review_action_id=f"ra_accept_{parent.origin_node_id}",
        surface=decisions.surface,
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
        evidence=evidence, warnings=chosen.warnings, composition=composition)


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
        # The PREVIEW rather than `project_branch_nodes`, for its
        # `members_by_node`: §5.8's answer is a claim about how many files a node
        # holds and this is the one place that number is already computed, beside
        # the node it belongs to and in the same traversal that built it. Reading
        # it here is what makes the answer checkable; recovering it afterwards
        # would be a second count that could disagree with the tree.
        preview = project_branch_preview(
            evidence, validation, parent=parent,
            plan_version_id=plan_version_id,
            mint_node_id=authorities.mint_node_id,
            handling_class_for=authorities.collapse_handling_classes,
            template_context_for=authorities.template_context_for)
        # WHICH OF THESE NODES IS A PARENT, read off the projection itself
        # rather than asked of the tree: these are exactly the nodes about to be
        # written, and a node that another one names as its parent HAS been
        # split. `refinement_for` needs it to tell a branch that was refined from
        # one that nobody has refined yet.
        split_parents = {node.parent_node_id for node in preview.projected}
        stamped = tuple(
            _with_refinement(node, decisions.refinement_for,
                             file_count=len(preview.members_by_node[node.node_id]),
                             was_split=node.node_id in split_parents)
            for node in preview.projected)
        # THE BRANCH'S OWN VERDICT, RE-DERIVED NOW THAT IT HAS CHILDREN. It was
        # stamped before `_route` ran, when it had none, and `_with_refinement`
        # skips a node that already carries one -- so without this the first
        # adopted folder to gain a child keeps `refine-later` on a branch that
        # was in fact just refined. Written directly because the branch is
        # usually NOT among the projected nodes: `project_branch_nodes` returns
        # the parent only when the composition put its values there instead of
        # into a folder, which is the case where it has no children at all.
        if parent.node_id in split_parents and not any(
                node.node_id == parent.node_id for node in stamped):
            write_node(conn, _restamped(
                parent, decisions.refinement_for,
                file_count=len(preview.members_by_node[parent.node_id]),
                was_split=True))
        return stamped
    return project


def _restamped(node: Node, refinement_for, *, file_count: int,
               was_split: bool) -> Node:
    """`_with_refinement` for a node that already carries a stale answer.

    `_with_refinement` refuses to overwrite one on purpose -- §5.8's answer is
    the USER's and a chain that re-derived it at every write would overrule an
    edit they made. This is the one case where the earlier answer was not theirs
    and not about this node as it now stands: it was computed before the branch
    was routed, about a branch with no children. Blanking it first is what makes
    the re-derivation visible here rather than hidden inside the guard.
    """
    return _with_refinement(
        dataclasses.replace(node, refinement_disposition=None,
                            refinement_reason=None),
        refinement_for, file_count=file_count, was_split=was_split)


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
    # The parent must be a branch THIS RUN proposed, and never a folder the
    # person already had. `00`:100 forbids reorganising an existing folder
    # "simply because a template would produce a different structure", and
    # nesting a product-created residual home inside somebody's own `Memes`
    # folder is that, done as a side effect of enabling something else.
    # `existing_path` is what tells the two apart: it is set only on an adopted
    # folder. When this run proposed no top-level branch there is no meaningful
    # parent to use, and the honest answer is none -- the node sits at the root
    # rather than inside a folder chosen because it happened to be first.
    default_parent = next(
        (node for node in existing.values()
         if node.parent_node_id is None and node.existing_path is None), None)
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
        # A residual home is a template: it is created empty and P11/P12 put
        # files in it later, so the number it holds AT DESIGN TIME is zero and
        # that is the count handed over rather than a stand-in. §7.4 asks the
        # user once for all of them, so `residual_refinement` is a fixed pair and
        # reads neither argument.
        write_node(conn, _with_refinement(
            node, lambda _node, _count, *, was_split: decisions.residual_refinement,
            # §7.4's home is flat DELIBERATELY, so neither number is a claim
            # about anything measured: the answer is the user's, verbatim.
            file_count=0, was_split=False))
