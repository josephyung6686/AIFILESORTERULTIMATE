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
from collections.abc import Callable, Collection, Mapping, Sequence
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
from tree_design.node_key import branch_key, level_key
from tree_design.profiles import build_profiles
from tree_design.records import (
    ExpectedValue, Node, PlanVersion, derive_accepts_placement,
)
from tree_design.residuals import ResidualChoice, ResidualTemplate, project_residual_nodes
from tree_design.routing import BranchContext, CompositionCandidate, RoutingReport, route_branch
from tree_design.store import (
    ReviewActionRefused, apply_review_action, nodes_for_version, open_draft,
    write_node, write_plan_version,
)
from tree_design.templates import CompositionConflict
from tree_design.user_edits import UserLevelEdit, user_level_edits
from tree_design.upstream import (
    AcceptedGroup, AnchorAgreement, GroupMember, ProtectedArea,
    UpstreamUnavailable,
    accepted_groups, cross_folder_moves, existing_folders,
    _normalised, _parent_directory_of,
    file_ids_in_directory, group_level_reader, protected_areas,
    settled_values_by_directory,
)
from tree_design.validation import ValidationReport, run_checks
from tree_design.vocabulary import (
    ACCEPT, ADD_SCOPED_GENERAL, ARCHIVE, C3, DISABLE, ENABLE, EXISTING, IGNORE,
    ORDINARY, PROPOSED, REPLACE_WITH_EXISTING, REVIEW_AND_UNSORTED,
    REVIEW_SURFACES, SET_SHARED_MATERIAL_POLICY, check,
)

#: `110` §2.1's scope for leaving a branch out. NOT a new member: `branch` is
#: `CORRECTION_SCOPES`' own, ratified by the owner on 11 Sep 2026 as *a node AND
#: everything under it*, which is exactly this gesture's reach. It is named here
#: rather than spelled at each of its two sites so the gesture P13 collects and
#: the event P1 records cannot drift apart.
IGNORED_BRANCH_SCOPE: str = "branch"

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
    #: `110` §2.1's *Disable*: the ORIGIN KEYS of the branches the person has
    #: said to leave out. Keys and not node ids, because §8.8 mints a new node id
    #: per plan version and this decision outlives the version it was made on --
    #: `node_key` spells an origin from the node's own claim, so the branch a
    #: person left out last week is findable in the tree this run just designed.
    #: Naming a key this tree does not carry is not an error: the corpus may
    #: simply no longer produce that branch, and the decision is kept for the day
    #: it does (the same rule `learned_preferences_still_applicable` states for a
    #: rejection of a node that no longer exists).
    ignored_branches: tuple[str, ...] = ()

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
    # `110` §2.1, LAST among the edits and before the freeze, which is the only
    # order that works: the branches to leave out are named by origin key, and
    # the nodes carrying those keys do not exist until every pass above has
    # written them. Before the freeze because `approved_branch_ids` is filtered
    # on `accepts_placement` -- an ignored branch must not be named approved, and
    # `freeze`'s own comment below already says so -- and before placement
    # because P11 reads the index this freeze projects.
    version = _apply_ignored_branches(conn, authorities, decisions,
                                      version=version, versions=versions)
    version, absorbed = _file_a_claim_under_the_folder_the_files_already_sit_in(
        conn, authorities, decisions, version=version, versions=versions)
    _kinds_under_the_folders_they_sit_in(
        conn, authorities, decisions, version=version, absorbed=absorbed)

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


def values_strong_enough_to_name_a_folder(
        rows: Mapping[str, Mapping[str, str]]) -> dict[str, str]:
    """Values a folder proposal may rest on.

    The slot read returns every live row, including a model clue too weak
    to establish a fact. That clue stays on the file. It does not become a
    folder. The states are the same set a proposal already rests on.
    """
    # Through the declared seam, not around it: `upstream.py` is the module
    # this package permits to name P6's records
    # (`tests/p10/test_p10_no_invention.py::test_only_the_declared_seams_name_another_parts_records`).
    from tree_design.upstream import PROPOSAL_ELIGIBLE_STATES

    return {
        file_id: row["canonical_value"]
        for file_id, row in rows.items()
        if row["canonical_value"]
        and row["reliability_state"] in PROPOSAL_ELIGIBLE_STATES
    }


def kinds_a_folder_already_separated(
        work_types: Mapping[str, str]) -> tuple[str, ...]:
    """The kinds of work more than one file in one folder already recorded.

    One file agreeing with itself is evidence about that file. It becomes a
    folder when a second file in the same directory records the same kind.
    The values are whatever the files said. Nothing here names a course, a
    laptop, or a directory.
    """
    counts: dict[str, int] = {}
    for value in work_types.values():
        if value:
            counts[value] = counts.get(value, 0) + 1
    return tuple(sorted(value for value, count in counts.items()
                        if not count <= 1))


def values_that_divide_a_folder(
        values: Mapping[str, str], files_in_folder: int) -> tuple[str, ...]:
    """Values more than one file recorded that leave some other file in the folder.

    A value every file in the folder carries separates nothing: the folder
    already says it. The words are whatever the files recorded.
    """
    counts: dict[str, int] = {}
    for value in values.values():
        if value:
            counts[value] = counts.get(value, 0) + 1
    return tuple(value for value in kinds_a_folder_already_separated(values)
                 if counts[value] < files_in_folder)


def field_that_divides_a_folder(
        by_field: Mapping[str, Mapping[str, str]],
        files_in_folder: int, *,
        kinds: Collection[str],
        absorbed: Collection[tuple[str, str]] = (),
) -> str | None:
    """The one field that splits this folder, or none.

    `kinds` is whatever the catalogue calls a closed vocabulary — a kind of
    work — on this machine. Those divide ahead of an open name. A name whose
    every dividing value was already absorbed into this folder is that
    folder's other spelling, so it is not split back out. Two fields that
    cover the same number of files are a tie, and a tie is not a guess.
    """
    absorbed_set = set(absorbed)
    kind_of = set(kinds)

    def winner(pool: list[tuple[int, str]]) -> str | None:
        best: str | None = None
        best_n = -1
        tied = False
        for covered, field in pool:
            if covered > best_n:
                best, best_n, tied = field, covered, False
            elif covered == best_n:
                tied = True
        return None if tied else best

    kind_pool: list[tuple[int, str]] = []
    name_pool: list[tuple[int, str]] = []
    for field, values in by_field.items():
        dividing = values_that_divide_a_folder(values, files_in_folder)
        if not dividing:
            continue
        if (field not in kind_of
                and all((field, value) in absorbed_set for value in dividing)):
            continue
        covered = sum(1 for value in values.values() if value in dividing)
        (kind_pool if field in kind_of else name_pool).append((covered, field))
    if kind_pool:
        return winner(kind_pool)
    return winner(name_pool)


def folder_a_course_already_sits_in(
        member_directories: Sequence[str],
        nested_folders: Mapping[str, str],
) -> str | None:
    """The one nested folder every file of a course already sits in.

    A dump at the top of the scan is not in `nested_folders`, so a course
    whose files are loose in Downloads keeps the spelling the fact used.
    Two directories means the course is not one folder the person made.
    """
    unique = set(member_directories)
    if len(unique) != 1:
        return None
    return nested_folders.get(next(iter(unique)))


def _file_a_claim_under_the_folder_the_files_already_sit_in(
        conn, authorities, decisions, *, version: str,
        versions: list[str],
) -> tuple[str, dict[str, frozenset[tuple[str, str]]]]:
    """A fact the person already filed is that folder.

    The fact may spell itself however the document spelled it, on any field
    the proposal used. The folder they made is the home. Children of the
    fact-named folder move under it, and the fact-named folder stops
    accepting files, so one set of files is not offered two homes. A claim
    with no child of its own is the same rule: the parallel folder is left
    out, and the files stay where the person put them.
    """
    from tree_design.upstream import preferred_in_field

    nodes = list(nodes_for_version(conn, version))
    nested_paths = {
        _normalised(node.existing_path)
        for node in nodes if node.existing_path and node.parent_node_id}
    if not nested_paths:
        return version, {}
    paths = {
        row["file_id"]: _normalised(_parent_directory_of(row["current_path"]))
        for row in conn.execute("SELECT file_id, current_path FROM files")}
    cache: dict[str, dict[str, str]] = {}
    # Origins, not node ids: the ignore below mints a new id for every node.
    planned: list[tuple[str, str, str, str]] = []
    seen: set[str] = set()
    for node in nodes:
        if node.node_type != PROPOSED or not node.dimension:
            continue
        if node.origin_node_id in seen:
            continue
        value = next((item.value for item in node.expected_values
                      if item.field == node.dimension), None)
        if not value:
            continue
        if node.dimension not in cache:
            cache[node.dimension] = {
                file_id: row["canonical_value"]
                for file_id, row in preferred_in_field(
                    conn, field_key=node.dimension).items()
                if row["canonical_value"]}
        members = [file_id for file_id, got in cache[node.dimension].items()
                   if got == value]
        if not members:
            continue
        directories: list[str] = []
        missing = False
        for file_id in members:
            if file_id not in paths:
                missing = True
                break
            directories.append(paths[file_id])
        if missing:
            continue
        home = folder_a_course_already_sits_in(
            directories, {path: path for path in nested_paths})
        if home is None:
            continue
        seen.add(node.origin_node_id)
        planned.append((node.origin_node_id, home, node.dimension, value,
                        node.node_id))

    # A child of a claim already planned is moved with that claim. Planning it
    # on its own sets it aside first, and the copy then repeats a folder that
    # no longer accepts files.
    by_id = {node.node_id: node for node in nodes}
    chosen_ids = {node_id for *_rest, node_id in planned}

    def _under_a_planned_claim(node_id: str) -> bool:
        parent_id = by_id[node_id].parent_node_id
        while parent_id is not None:
            if parent_id in chosen_ids:
                return True
            parent = by_id.get(parent_id)
            if parent is None:
                return False
            parent_id = parent.parent_node_id
        return False

    planned = [tuple(claim) for *claim, node_id in planned
               if not _under_a_planned_claim(node_id)]

    absorbed: dict[str, set[tuple[str, str]]] = {}
    for origin, home, field, value in planned:
        nodes = list(nodes_for_version(conn, version))
        by_origin = {node.origin_node_id: node for node in nodes}
        claim_node = by_origin.get(origin)
        existing = next(
            (node for node in nodes
             if node.existing_path and _normalised(node.existing_path) == home
             and node.parent_node_id), None)
        if (claim_node is None or existing is None
                or claim_node.node_type != PROPOSED):
            continue
        absorbed.setdefault(home, set()).add((field, value))
        children = [one for one in nodes
                    if one.parent_node_id == claim_node.node_id]
        # The fact-named folder and everything under it, collected before the
        # copies exist, so the copies are not part of what gets set aside.
        subtree = [claim_node.origin_node_id]
        pending = [claim_node.node_id]
        while pending:
            parent_id = pending.pop()
            for one in nodes:
                if one.parent_node_id == parent_id:
                    subtree.append(one.origin_node_id)
                    pending.append(one.node_id)
        already = {
            (item.field, item.value)
            for one in nodes if one.parent_node_id == existing.node_id
            for item in one.expected_values}
        for child in children:
            claim = next((item.value for item in child.expected_values
                          if item.field == child.dimension), child.display_label)
            # The person's folder is the claim. The child keeps the field it
            # was built from, and not the spelling a document used for the
            # folder itself.
            own = tuple(item for item in child.expected_values
                        if item.field == child.dimension)
            if not child.dimension or (child.dimension, claim) in already:
                continue
            if "/" in claim or "\\" in claim:
                continue
            write_node(conn, dataclasses.replace(
                child,
                node_id=authorities.mint_node_id(),
                plan_version_id=version,
                parent_node_id=existing.node_id,
                node_type=PROPOSED,
                dimension=None,
                dimension_role=None,
                accepts_placement=derive_accepts_placement(
                    PROPOSED, protected_movement_permitted=False),
                expected_values=own,
                origin_node_id=level_key(
                    existing.origin_node_id, field=child.dimension,
                    value=claim, role=child.dimension_role or child.dimension
                    or "level")))
            already.add((child.dimension, claim))
        for leaving in subtree:
            version = _apply(conn, authorities, decisions, action=_Action(
                review_action_id=f"ra_ignore_{leaving}",
                surface=decisions.surface, subject_ref=leaving,
                plan_version=version, action=IGNORE,
                correction_scope=IGNORED_BRANCH_SCOPE,
                presented_state_ref=f"ps_{leaving}",
                user_id=decisions.user_id, observed_at=decisions.created_at))
            versions.append(version)
    return version, {home: frozenset(pairs) for home, pairs in absorbed.items()}


def _kinds_under_the_folders_they_sit_in(
        conn, authorities, decisions, *, version: str,
        absorbed: Mapping[str, frozenset[tuple[str, str]]]) -> None:
    """A value two files in one folder already share becomes a child of it.

    The folder is whichever directory the scan read. The value is whichever
    field those files recorded. A closed vocabulary — what the catalogue
    calls a kind of work — divides ahead of an open name, and the same rule
    applies to every such vocabulary. A top-level folder of the scan is the
    pile the person pointed at, so it is not split; a folder inside it is
    one they made. A name already absorbed into that folder is not split
    back out of it.
    """
    from tree_design.upstream import preferred_in_field

    nodes = list(nodes_for_version(conn, version))
    nested = [node for node in nodes
              if node.existing_path and node.parent_node_id
              and node.node_type == EXISTING]
    if not nested:
        return
    catalogue = list(conn.execute(
        "SELECT field_key, value_kind FROM fields WHERE destination_eligible = 1"))
    if not catalogue:
        return
    kind_fields = frozenset(
        key for key, value_kind in catalogue if value_kind == "enum")
    paths = {
        row["file_id"]: _normalised(_parent_directory_of(row["current_path"]))
        for row in conn.execute("SELECT file_id, current_path FROM files")}
    preferred: dict[str, dict[str, str]] = {}
    for field, _value_kind in catalogue:
        preferred[field] = values_strong_enough_to_name_a_folder(
            preferred_in_field(conn, field_key=field))
    for existing in nested:
        folder = _normalised(existing.existing_path)
        file_ids = [file_id for file_id, found in paths.items()
                    if found == folder]
        by_field = {
            field: {file_id: mapping[file_id]
                    for file_id in file_ids if file_id in mapping}
            for field, mapping in preferred.items()}
        by_field = {field: mapping for field, mapping in by_field.items()
                    if mapping}
        chosen = field_that_divides_a_folder(
            by_field, len(file_ids), kinds=kind_fields,
            absorbed=absorbed.get(folder, ()))
        if chosen is None:
            continue
        children = [node for node in nodes
                    if node.parent_node_id == existing.node_id]
        have = {(item.field, item.value) for child in children
                for item in child.expected_values}
        ordinal = len(children)
        wrote = False
        names_already = absorbed.get(folder, ())
        for kind in values_that_divide_a_folder(
                by_field[chosen], len(file_ids)):
            if (chosen, kind) in have or "/" in kind or "\\" in kind:
                continue
            if chosen not in kind_fields and (chosen, kind) in names_already:
                continue
            members = [file_id for file_id, value
                       in by_field[chosen].items() if value == kind]
            node = _with_refinement(Node(
                node_id=authorities.mint_node_id(),
                plan_version_id=version,
                node_type=PROPOSED,
                display_label=kind,
                parent_node_id=existing.node_id,
                root_anchor=existing.root_anchor,
                ordinal=ordinal,
                associated_group_ids=existing.associated_group_ids,
                explanation=(
                    f"{len(members)} files already in this folder record "
                    f"{chosen} = {kind!r}. The folder they sit in is the "
                    "one the person made; this level only separates what "
                    "those files already named."),
                node_role=ORDINARY,
                accepts_placement=derive_accepts_placement(
                    PROPOSED, protected_movement_permitted=False),
                handling_class=existing.handling_class,
                origin_node_id=level_key(
                    existing.origin_node_id, field=chosen,
                    value=kind, role=chosen),
                expected_values=(ExpectedValue(field=chosen, value=kind),),
            ), decisions.refinement_for, file_count=len(members), was_split=False)
            write_node(conn, node)
            ordinal += 1
            wrote = True
            have.add((chosen, kind))
        if wrote:
            write_node(conn, _restamped(
                existing, decisions.refinement_for,
                file_count=len(file_ids),
                was_split=True))


def _apply_ignored_branches(conn, authorities, decisions, *, version: str,
                            versions: list[str]) -> str:
    """`110` §2.1's *Disable*, through the `IGNORE` writer that already exists.

    The node stays in the tree as `ignored` and stops accepting placement, which
    is `84` §1 rather than a half-measure: material is marked and counted and
    never silently omitted, so a branch the person left out is still on their
    screen, still named, and no longer somewhere a file can go.

    **THE WHOLE SUBTREE, and that is not a convenience.** `accepts_placement` is
    read per node -- `placement/index.py` writes one entry per node carrying it
    and walks no ancestor -- so ignoring the branch alone would leave every
    folder beneath it a live destination, and files would go on landing inside a
    branch the person had just taken out. `branches_named` already selects the
    subtree at the gesture; this walks it again here because the tree this run
    designed is not the tree the gesture was typed against, and the children are
    this run's.

    **Walked by parent, not by key prefix.** A level's origin key is spelled from
    its parent's, so a descendant's key does start with its ancestor's -- and
    matching on that string would make the KEY a path, which is the one thing
    `node_key` says it is not. The parent links are what the tree is made of.

    NOTHING HAPPENS WHEN NOTHING IS IGNORED, which is every run before the person
    types the flag: no draft is opened and no row is written, so a corpus nobody
    has edited produces byte-identically the run it produced before this existed.
    """
    if not decisions.ignored_branches:
        return version
    wanted = frozenset(decisions.ignored_branches)
    nodes = nodes_for_version(conn, version)
    children: dict[str | None, list] = {}
    for node in nodes:
        children.setdefault(node.parent_node_id, []).append(node)
    origins: list[str] = []
    seen: set[str] = set()
    pending = [node for node in nodes if node.origin_node_id in wanted]
    while pending:
        node = pending.pop()
        if node.node_id in seen:
            continue
        seen.add(node.node_id)
        origins.append(node.origin_node_id)
        pending.extend(children.get(node.node_id, ()))
    # Sorted, so two runs over one corpus apply the same edits in the same order
    # and mint the same chain of versions. `_add_scoped_generals` orders its own
    # for the same reason.
    for origin in sorted(origins):
        version = _apply(conn, authorities, decisions, action=_Action(
            review_action_id=f"ra_ignore_{origin}",
            surface=decisions.surface,
            subject_ref=origin,
            plan_version=version, action=IGNORE,
            # `branch`, the scope the gesture was collected at: a node AND
            # everything under it (the owner, 11 Sep 2026). The event log says
            # the same thing about this edit that P13's record says about the
            # gesture that caused it.
            correction_scope=IGNORED_BRANCH_SCOPE,
            presented_state_ref=f"ps_{origin}",
            user_id=decisions.user_id, observed_at=decisions.created_at))
        versions.append(version)
    return version


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


def mint_review_homes(conn: sqlite3.Connection, *,
                      authorities: TreeDesignAuthorities,
                      decisions: TreeDesignDecisions,
                      tree: TreeDesignResult,
                      homes: Sequence[str],
                      disposition: str) -> TreeDesignResult:
    """`00` amendment 13's homes, minted AFTER placement proved which sets exist.

    The tree freezes before placement (`STEPS`) and §7.5's sets exist only
    after it, so a home a set is offered can only be added the way `00`:99's
    General is: a draft opened from the frozen version, the nodes written,
    the version frozen again. Returns `tree` unchanged, having written
    NOTHING, when `homes` is empty.
    """
    if not homes:
        return tree
    groups, _folders, areas, _moves = _upstream(conn, authorities, decisions)
    version = authorities.mint_version_id()
    open_draft(conn, from_version=tree.tree.plan_version_id,
               new_version_id=version, created_at=decisions.created_at,
               mint_node_id=authorities.mint_node_id)
    choices = tuple(ResidualChoice(
        template_name=name, action=ENABLE, disposition=disposition,
        display_label=None, parent_node_id=None,
        root_anchor=authorities.root_anchor, merge_into=None,
        replaces_node_id=None) for name in homes)
    enable_review_homes(conn, authorities, decisions, version=version,
                        choices=choices)
    profiles = build_profiles(
        conn, plan_version_id=version,
        groups_by_id={group.group_id: group for group in groups},
        document_types_by_node={}, anchor_excerpts_by_node={},
        user_edits_by_node={}, node_scoped_rejections={})
    freeze(
        conn, plan_version_id=version, created_at=decisions.created_at,
        user_id=decisions.user_id, surface=decisions.surface,
        component_version=decisions.component_version,
        residual_configuration={**decisions.residual_configuration,
                                **{name: ENABLE for name in homes}},
        approved_branch_ids=tuple(
            node.node_id for node in nodes_for_version(conn, version)
            if node.accepts_placement),
        profiles=profiles, protected_areas=areas,
        catalogue_release_id=getattr(authorities.catalogue, "release_id", None),
        template_versions=tree.tree.freeze_record.template_versions)
    return dataclasses.replace(
        tree, tree=frozen_tree(conn, plan_version=version),
        plan_version_ids=tree.plan_version_ids + (version,))


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

    project = _projection(conn, authorities, decisions, evidence=evidence,
                          validation=validation,
                          parent_origin_id=parent.origin_node_id)
    projected_counts: list[int] = []

    def counted(action, plan_version_id: str) -> tuple[Node, ...]:
        nodes = project(action, plan_version_id)
        projected_counts.append(len(nodes))
        return nodes

    try:
        new_version = _apply(conn, authorities, decisions, action=_Action(
            review_action_id=f"ra_accept_{parent.origin_node_id}",
            surface=decisions.surface,
            subject_ref=parent.origin_node_id, plan_version=version,
            action=ACCEPT, correction_scope="node",
            presented_state_ref=f"ps_{option_id}",
            user_id=decisions.user_id, observed_at=decisions.created_at,
            payload={"option_id": option_id}),
            project=counted)
    except ReviewActionRefused:
        if projected_counts != [0]:
            raise
        # The chosen shape builds nothing inside this branch. One branch is
        # not the whole plan: it keeps its own node, as `opt_no_split` does,
        # and the rest of the tree is designed and frozen.
        return version, BranchDesign(
            origin_node_id=parent.origin_node_id, candidate=candidate,
            routing=report, options=options, chosen_option_id=option_id,
            evidence=None, warnings=chosen.warnings)
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
    enable_review_homes(conn, authorities, decisions, version=version,
                        choices=decisions.residual_choices)


def enable_review_homes(conn, authorities, decisions, *, version: str,
                        choices: Sequence[ResidualChoice]) -> tuple[Node, ...]:
    """`00` amendment 13: residual homes live under a root-level `98`.

    The root is minted the first time a home needs it and never otherwise --
    `00`:121's "not automatically created" is kept for the root as for the
    homes. A choice that names its own parent or replaces an existing folder
    keeps that; only a parentless one goes under `98`. `99 Archive` is a home
    of its own at the root: it is in the library as the owner's user-defined
    template (`cli._residual_library`), its choice names no parent, and it is
    exempt from `98` by name.

    This supersedes the first-proposed-branch parent a parentless home used
    to get: `00`:99's "a global catch-all folder should not become the
    product's default answer" is kept by amendment 13's own words -- the
    catch-all "MUST exist, be typed, and be visible at the root", and a file
    reaches it only when no branch can hold it. The parent is still a branch
    THIS RUN proposed and never a folder the person already had (`00`:100).

    Published so `mint_review_homes` can call it after placement, on a draft
    opened from the frozen tree -- the same seam `mint_scoped_generals` uses
    for `00`:99's General.

    **THE ROOT IS MINTED BY ORIGIN AND FOUND BY LABEL, AND THAT IS NOT AN
    OVERSIGHT.** It reads like one -- `9bf8ffe3` keyed the mint and left the
    lookup on `display_label` -- so the measurement is here rather than left for
    somebody to "fix". The label is what reunites this run with the folder the
    LAST run created. Once a plan has been applied the person really has a
    `98 Review and Unsorted` directory, `cli.adopted_folders` offers every
    directory to the design, and it comes back as a parentless `existing` node
    whose origin is `existing:<its path>` and never `branch:98 Review and
    Unsorted`. Measured on a corpus holding that folder: the homes land INSIDE
    the person's own `98`. A lookup on `origin_node_id == branch_key(...)` would
    miss it and mint a second root-level `98` beside the first, so the swap is
    not the behaviour-neutral tightening it looks like, whichever of the two
    behaviours is the wanted one.

    **AND WHICH OF THEM IS WANTED IS NOT SETTLED HERE.** The paragraph above says
    "the parent is still a branch THIS RUN proposed and never a folder the person
    already had (`00`:100)", and the measurement says that on the second run over
    an applied corpus it IS a folder they already had. Reuse reads like the
    kinder answer -- the folder exists and holds their files -- and `00`:100 as
    quoted reads like it forbids exactly that. Two readings of one paragraph is
    the owner's to decide and not an agent's; what is recorded here is that the
    two disagree and where, so whoever settles it starts from the measurement.

    What the label lookup cannot find is a root somebody RENAMED --
    `store.apply_review_action`'s RENAME arm writes `display_label` and leaves
    the origin alone. That is unreachable today and by more than one argument:
    no production caller constructs a RENAME at all (`pipeline._apply` emits
    `ACCEPT`, `IGNORE`, `ADD_SCOPED_GENERAL` and `SET_SHARED_MATERIAL_POLICY`,
    and the CLI's `--rename` is P6's value claim while a canvas relabel travels
    as P13's gesture into `user_level_edits`), and the two callers here both run
    within one invocation, the second on a draft opened from the first's frozen
    tree. If a RENAME writer ever arrives, the answer is the shape
    `placement.versions` already uses for exactly this problem -- match EITHER
    identity, the label or the origin -- and not a swap of one for the other.
    """
    existing = {node.node_id: node for node in nodes_for_version(conn, version)}
    root = next((node for node in existing.values()
                 if node.parent_node_id is None
                 and node.display_label == REVIEW_AND_UNSORTED), None)
    parentless = [choice for choice in choices
                  if choice.parent_node_id is None
                  and choice.action not in (DISABLE, REPLACE_WITH_EXISTING)
                  and choice.template_name != ARCHIVE]
    if parentless and root is None:
        root = _with_refinement(Node(
            node_id=authorities.mint_node_id(), plan_version_id=version,
            node_type=PROPOSED,
            display_label=REVIEW_AND_UNSORTED, parent_node_id=None,
            root_anchor=authorities.root_anchor,
            ordinal=sum(1 for node in existing.values() if node.parent_node_id is None),
            associated_group_ids=(),
            explanation=("Files no branch of this plan can hold are gathered "
                         "here, in named sets, and offered to you before "
                         "anything moves (`00` amendment 13)."),
            node_role=ORDINARY,
            accepts_placement=derive_accepts_placement(
                PROPOSED, protected_movement_permitted=False),
            handling_class=authorities.collapse_handling_classes(frozenset()),
            # `106` Phase 5.1 keyed every other mint site and this root, added
            # afterwards by amendment 13, kept the fresh mint's own id -- so it
            # was the one node in the tree with NO LINEAGE, and two identical
            # runs reported it removed and added and every home under it moved.
            # It is a parentless proposal, which is exactly what `branch_key`
            # keys: the label, because a proposal has nothing else it is named
            # by. `node_id` is still minted per version.
            origin_node_id=branch_key(display_label=REVIEW_AND_UNSORTED,
                                      existing_path=None)),
            lambda _node, _count, *, was_split: decisions.residual_refinement,
            file_count=0, was_split=False)
        write_node(conn, root)
        existing[root.node_id] = root
    rehomed = tuple(
        dataclasses.replace(choice, parent_node_id=root.node_id)
        if choice in parentless else choice
        for choice in choices)
    nodes = project_residual_nodes(
        decisions.residual_library, rehomed, plan_version_id=version,
        handling_class_for_template=decisions.residual_handling_class,
        mint_node_id=authorities.mint_node_id, existing_nodes=existing)
    for node in nodes:
        # A residual home is a template: it is created empty and P11/P12 put
        # files in it later, so the number it holds AT DESIGN TIME is zero and
        # that is the count handed over rather than a stand-in. §7.4 asks the
        # user once for all of them, so `residual_refinement` is a fixed pair and
        # reads neither argument. §7.4's home is flat DELIBERATELY, so neither
        # number is a claim about anything measured: the answer is the user's.
        write_node(conn, _with_refinement(
            node, lambda _node, _count, *, was_split: decisions.residual_refinement,
            file_count=0, was_split=False))
    return nodes
