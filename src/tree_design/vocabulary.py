# src/tree_design/vocabulary.py
"""P10's closed vocabularies. Named constant == string value, one home each.

Three collisions are handled by naming rather than by hoping:

* `draft` is a template's PUBLICATION lifecycle and also a branch binding's
  WORKFLOW state. Neither is `DRAFT`; both carry their axis in the name.
* `template`, `node`, `group`, `domain` and `corpus` are §8.7 correction scopes
  AND ordinary P10 nouns. The scopes are imported from P1, never respelled.
* P10's V1-V6 are §5.7's template design checks. P1's V1-V4 are §8.2's checksum
  verification points. They share the letter and nothing else.

Every set another part owns is IMPORTED. A second copy of P7's handling classes
would silently disagree with P7 the day P7 adds one, and the disagreement would
look like a P10 load error on a file P7 had classified correctly.

That import rule is why the registry has two halves. `P10_OWNED_SETS` holds the
sets P10 PUBLISHES, and BRIEF §11 applies to every one of them: a tuple for
membership and a named constant for each member. `BORROWED_SETS` holds the sets
another part publishes; their members are named by their owner and are NOT
respelled here, because a constant naming `direct-anchor` in this file would be
the second home the guard test exists to forbid. `P10_CLOSED_SETS` is the union
and is what the no-second-home guard walks.
"""
from __future__ import annotations

from types import MappingProxyType

from database_agent.events import CORRECTION_SCOPES, RESERVED_EVENT_TYPES
from eval_harness.vocabulary import (
    BUDGET_STATES as _P2_BUDGET_STATES,
    OUTCOMES as _P2_OUTCOMES,
)
from grouping.vocabulary import MEMBERSHIP_BASES
from llm_harness.vocabulary import (
    DIMENSION_SCOPES,
    E_TEMPLATE,
    SCOPE_SCHEMA_FIELD,
    SCOPE_TEMPLATE_LOCAL,
    TEMPLATE_ELIGIBILITY,
)
from privacy.vocabulary import (
    HANDLING_CLASSES, OPERATION_MODES, USER as _BASIS_USER,
)
from scan_agent.inventory import CURATION_SIGNAL_VALUES

# --- node identity (§5.12) ------------------------------------------------------

EXISTING: str = "existing"
PROPOSED: str = "proposed"
USER_CREATED: str = "user-created"
PROTECTED: str = "protected"
IGNORED: str = "ignored"

#: §5.12's five, in §5.12's order. Whether `protected` is a type or an orthogonal
#: flag is SPEC open question 3; this carries the enum literally AND a separate
#: `handling_class` so the answer can go either way without a migration.
NODE_TYPES: tuple[str, ...] = (EXISTING, PROPOSED, USER_CREATED, PROTECTED, IGNORED)

ORDINARY: str = "ordinary"
SCOPED_GENERAL: str = "scoped-general"
RESIDUAL: str = "residual"
SHARED_MATERIAL: str = "shared-material"

#: MINOR 6: P10 owns the tree, so P10 names its node kinds. P11 carries these
#: verbatim and publishes no parallel vocabulary.
NODE_ROLES: tuple[str, ...] = (ORDINARY, SCOPED_GENERAL, RESIDUAL, SHARED_MATERIAL)

PHYSICAL_DESTINATION: str = "physical-destination"
REVIEW_ONLY: str = "review-only"
LEAVE_IN_PLACE: str = "leave-in-place"

#: §7.4. Required on a `residual` node, meaningless on every other role.
RESIDUAL_DISPOSITIONS: tuple[str, ...] = (
    PHYSICAL_DESTINATION, REVIEW_ONLY, LEAVE_IN_PLACE,
)

REFINED: str = "refined"
SHALLOW_BY_CHOICE: str = "shallow-by-choice"
REFINE_LATER: str = "refine-later"

#: §5.8 + §8.8. `shallow-by-choice` and `refine-later` are different answers, and
#: collapsing them would make a deliberate design look like unfinished work.
REFINEMENT_DISPOSITIONS: tuple[str, ...] = (REFINED, SHALLOW_BY_CHOICE, REFINE_LATER)

# --- template records (§5.4, §5.7) ----------------------------------------------

BUILT_IN: str = "built-in"
LLM_GENERATED: str = "llm-generated"
USER_AUTHORED: str = "user-authored"

#: WHO authored the recipe. Three axes are kept apart deliberately: authorship,
#: scope and lifecycle answer three different questions, and "user-saved" used to
#: stand in for two of them.
ORIGIN_KINDS: tuple[str, ...] = (BUILT_IN, LLM_GENERATED, USER_AUTHORED)

DOMAIN_FOCUSED: str = "domain-focused"
CROSS_DOMAIN: str = "cross-domain"
PURPOSE_FOCUSED: str = "purpose-focused"
PERSONAL: str = "personal"

#: WHAT the recipe spans.
SCOPE_KINDS: tuple[str, ...] = (
    DOMAIN_FOCUSED, CROSS_DOMAIN, PURPOSE_FOCUSED, PERSONAL,
)

PUBLICATION_DRAFT: str = "draft"
PUBLISHED: str = "published"
RETIRED: str = "retired"

#: WHERE the recipe is in its library lifecycle. Saving a draft definition does
#: not activate it and publishing a newer record does not migrate a prior binding.
PUBLICATION_STATES: tuple[str, ...] = (PUBLICATION_DRAFT, PUBLISHED, RETIRED)

REQUIRED: str = "required"
OPTIONAL: str = "optional"

DIMENSION_REQUIREMENTS: tuple[str, ...] = (REQUIRED, OPTIONAL)

WORKFLOW_DRAFT: str = "draft"
WORKFLOW_REVIEWED: str = "reviewed"
WORKFLOW_APPROVED: str = "approved"

#: A branch binding's workflow state. The SPEC's example binding shows only
#: `approved`; the closed set is the composable-template design's.
BINDING_STATES: tuple[str, ...] = (
    WORKFLOW_DRAFT, WORKFLOW_REVIEWED, WORKFLOW_APPROVED,
)

ACTION_SELECTED: str = "selected"
ACTION_OMITTED: str = "omitted"
ACTION_REORDERED: str = "reordered"
ACTION_FLATTENED: str = "flattened"
ACTION_RENAMED: str = "renamed"
ACTION_ADDED: str = "added"

#: What the user did to one dimension of a routed recipe, recorded per branch.
#: Six, not four: `renamed` and `added` are legal edits and an unrepresentable
#: edit is an edit the diff cannot explain.
DIMENSION_ACTIONS: tuple[str, ...] = (
    ACTION_SELECTED, ACTION_OMITTED, ACTION_REORDERED, ACTION_FLATTENED,
    ACTION_RENAMED, ACTION_ADDED,
)

#: P7's basis for "the user's own act", REUSED rather than restated. `64` §2:
#: "the catalogue is a proposal, the user's edits are facts", and the precedence
#: that carries it already exists — a P7 record on this basis outranks an
#: inferred one of any reliability. A second word for the same idea would be two
#: vocabularies to keep in step, and `tree_design.user_edits` checks membership
#: in `CLASSIFICATION_BASES` so the reuse cannot quietly become a copy.
BASIS_USER: str = _BASIS_USER

# --- the two check families -----------------------------------------------------
#
# Each gate and each check gets a named constant, the same way every other P10
# value does (BRIEF §11). `routing.py` and `validation.py` report a failure by
# NAME, and `COMPOSITION_GATES[1]` would couple every report to tuple order.

C1: str = "C1"
C2: str = "C2"
C3: str = "C3"
C4: str = "C4"
C5: str = "C5"
C6: str = "C6"
C7: str = "C7"
C8: str = "C8"

COMPOSITION_GATES: tuple[str, ...] = (C1, C2, C3, C4, C5, C6, C7, C8)

COMPOSITION_GATE_MEANINGS: MappingProxyType = MappingProxyType({
    C1: "every referenced template, fragment, applicability and version exists",
    C2: "every resolved dimension maps to a live P6 field",
    C3: "the branch's accepted groups and facts satisfy the selected binding",
    C4: "a required role resolves exactly once",
    C5: "combined relative-order constraints are acyclic",
    C6: "the composition loses no group or file silently",
    C7: "combined privacy is no weaker than any included restriction",
    C8: "a valid preview stays inert until branch-specific approval",
})

GATE_REFUSE: str = "refuse"
GATE_WARN: str = "warn"

#: What a failed gate COSTS. Owner ruling: the eight do not share one
#: consequence, and making them uniform is wrong in both directions — a uniform
#: refusal makes the product unusable on an ambiguous library, and a uniform
#: warning makes privacy overridable by a click.
GATE_CONSEQUENCES: tuple[str, ...] = (GATE_REFUSE, GATE_WARN)

#: The split, gate by gate.
#:
#: `refuse` is every gate whose failure means the composition CANNOT be produced
#: or would do harm to produce: a missing artefact (C1), a minted field (C2),
#: evidence that does not support the recipe (C3), material dropped from a
#: "successful" preview (C6), a privacy floor weaker than an included fragment's
#: (C7), and a template that activated itself (C8). No user gesture waves any of
#: these through, because there is nothing behind them to proceed to.
#:
#: `warn` is the two gates that surface a CHOICE rather than a defect. C4 found
#: two rows binding one role to two fields and refuses to pick; C5 found two
#: partial orders that disagree. Both are resolved by the user saying which one,
#: and the composition then proceeds with that decision recorded. C5's OTHER
#: failure — an allowed-value intersection that is empty — stays a refusal, and
#: it does, because no order the user chooses can make two disjoint value sets
#: agree.
COMPOSITION_GATE_CONSEQUENCE: MappingProxyType = MappingProxyType({
    C1: GATE_REFUSE,
    C2: GATE_REFUSE,
    C3: GATE_REFUSE,
    C4: GATE_WARN,
    C5: GATE_WARN,
    C6: GATE_REFUSE,
    C7: GATE_REFUSE,
    C8: GATE_REFUSE,
})

if set(COMPOSITION_GATE_CONSEQUENCE) != set(COMPOSITION_GATES):  # pragma: no cover
    raise ImportError(
        "every composition gate carries exactly one consequence; a gate with "
        "none would be uniform by accident, which is the ruling's failure mode"
    )

#: DERIVED from the map above, never listed beside it. A hand-written second list
#: is the copy that goes stale the day a gate changes class.
NON_OVERRIDABLE_GATES: tuple[str, ...] = tuple(
    gate for gate in COMPOSITION_GATES
    if COMPOSITION_GATE_CONSEQUENCE[gate] == GATE_REFUSE
)
OVERRIDABLE_GATES: tuple[str, ...] = tuple(
    gate for gate in COMPOSITION_GATES
    if COMPOSITION_GATE_CONSEQUENCE[gate] == GATE_WARN
)

V1: str = "V1"
V2: str = "V2"
V3: str = "V3"
V4: str = "V4"
V5: str = "V5"
V6: str = "V6"

TEMPLATE_CHECKS: tuple[str, ...] = (V1, V2, V3, V4, V5, V6)

#: §5.7's six, run by P10 over the materialised candidate. P8 enforces the
#: response shape and returns a verdict; it runs none of these.
TEMPLATE_CHECK_MEANINGS: MappingProxyType = MappingProxyType({
    V1: "repeats a parent dimension",
    V2: "creates meaningless one-child levels",
    V3: "exceeds practical depth limits",
    V4: "author or organization used merely as a collector",
    V5: "exposes protected information",
    V6: "produces empty branches against the accepted group",
})

# --- the residual library (§7.2, §7.3, §7.4) ------------------------------------

TEMPORARY_SCREENSHOTS: str = "Temporary Screenshots"
ONE_OFF_IMAGES: str = "One-Off Images"
REFERENCE_CLIPS: str = "Reference Clips"
INDEPENDENT_RECORDS: str = "Independent Records"
RECEIPTS_AND_CONFIRMATIONS: str = "Receipts and Confirmations"
READING_INBOX: str = "Reading Inbox"
REVIEW_LATER: str = "Review Later"
UNSUPPORTED_OR_ENCRYPTED: str = "Unsupported or Encrypted"
PROTECTED_RECORDS: str = "Protected Records"

#: §7.3's nine, in §7.3's order. Fixed names; their slot VALUES are deferred and
#: none is invented here.
RESIDUAL_TEMPLATE_NAMES: tuple[str, ...] = (
    TEMPORARY_SCREENSHOTS,
    ONE_OFF_IMAGES,
    REFERENCE_CLIPS,
    INDEPENDENT_RECORDS,
    RECEIPTS_AND_CONFIRMATIONS,
    READING_INBOX,
    REVIEW_LATER,
    UNSUPPORTED_OR_ENCRYPTED,
    PROTECTED_RECORDS,
)

#: §7.3 states a default parent for the first four only. The remaining five have
#: none stated, and an invented default would be P10 authoring §7.3.
RESIDUAL_DEFAULT_PARENTS: MappingProxyType = MappingProxyType({
    TEMPORARY_SCREENSHOTS: ("Photos", TEMPORARY_SCREENSHOTS),
    ONE_OFF_IMAGES: ("Photos", ONE_OFF_IMAGES),
    REFERENCE_CLIPS: ("Personal", REFERENCE_CLIPS),
    INDEPENDENT_RECORDS: ("Personal", INDEPENDENT_RECORDS),
})

SLOT_DISPLAY_NAME: str = "display_name"
SLOT_DEFAULT_PARENT_LOCATION: str = "default_parent_location"
SLOT_ACCEPTED_EVIDENCE_PATTERNS: str = "accepted_evidence_patterns"
SLOT_EXPECTED_FILE_TYPES: str = "expected_file_types"
SLOT_SENSITIVITY_RESTRICTIONS: str = "sensitivity_restrictions"
SLOT_OPTIONAL_SHALLOW_SUBFOLDERS: str = "optional_shallow_subfolders"
SLOT_MAX_PERMITTED_DEPTH: str = "max_permitted_depth"
SLOT_TREATMENT: str = "treatment"

#: §7.2's eight attribute slots. Every residual template defines all eight.
RESIDUAL_SLOTS: tuple[str, ...] = (
    SLOT_DISPLAY_NAME,
    SLOT_DEFAULT_PARENT_LOCATION,
    SLOT_ACCEPTED_EVIDENCE_PATTERNS,
    SLOT_EXPECTED_FILE_TYPES,
    SLOT_SENSITIVITY_RESTRICTIONS,
    SLOT_OPTIONAL_SHALLOW_SUBFOLDERS,
    SLOT_MAX_PERMITTED_DEPTH,
    SLOT_TREATMENT,
)

TREATMENT_REVIEWED: str = "reviewed"
TREATMENT_RETAINED: str = "retained"
TREATMENT_KEPT_SEARCHABLE: str = "merely kept searchable"

RESIDUAL_TREATMENTS: tuple[str, ...] = (
    TREATMENT_REVIEWED, TREATMENT_RETAINED, TREATMENT_KEPT_SEARCHABLE,
)

ENABLE: str = "enable"
DISABLE: str = "disable"
RENAME_RESIDUAL: str = "rename"
RELOCATE: str = "relocate"
MERGE_RESIDUAL: str = "merge"
REPLACE_WITH_EXISTING: str = "replace-with-existing"

#: §7.4's six. A template the user did not enable has no node, which is the whole
#: enforcement mechanism: no model can return a destination that does not exist.
#:
#: Named `RESIDUAL_LIBRARY_ACTIONS`, not `RESIDUAL_ACTIONS`, because
#: `llm_harness.vocabulary.RESIDUAL_ACTIONS` is already live and is §7.7's EIGHT
#: review actions (`return_to_confirmed_domain_group` ... `abstain`), which P11
#: imports. Two different closed sets under one name in one pipeline is a
#: misspelling waiting to become a silent downgrade — the exact failure `check()`
#: below exists to prevent. These six are the LIBRARY actions: what the user does
#: to a residual template before freeze. P8's eight are the WORKFLOW actions:
#: what P11 does with a file that reached a residual node after it.
RESIDUAL_LIBRARY_ACTIONS: tuple[str, ...] = (
    ENABLE, DISABLE, RENAME_RESIDUAL, RELOCATE, MERGE_RESIDUAL,
    REPLACE_WITH_EXISTING,
)

# --- tree-level policies --------------------------------------------------------

SHARED_BRANCH: str = "shared-branch"
PRIMARY_HOME: str = "primary-home"
REFERENCE_OR_ALIAS: str = "reference-or-alias"
MANDATORY_REVIEW: str = "mandatory-review"

#: §6.9. Without one of these recorded, P11 must abstain on a file that belongs
#: to two packets rather than pick one. Whether the policy is tree-global or
#: per-branch is SPEC open question 9, so the record carries an explicit
#: `policy_scope` and this vocabulary answers only WHICH policy.
SHARED_MATERIAL_POLICIES: tuple[str, ...] = (
    SHARED_BRANCH, PRIMARY_HOME, REFERENCE_OR_ALIAS, MANDATORY_REVIEW,
)

#: The three §6.9 policies that resolve to a DESTINATION, and by omission the one
#: that does not. `mandatory-review` means ask the user, so a branch created for
#: it would answer the question the policy exists to keep open.
#:
#: Named here because MINOR 6 puts the tree's vocabulary in P10: "P10 owns the
#: tree, so P10 names its node kinds. P11 carries these verbatim and publishes no
#: parallel vocabulary." `placement.groups` currently computes the same set
#: privately as `_BRANCH_BEARING`; that is the parallel vocabulary MINOR 6
#: forbids, and it is P11's to carry from here.
BRANCH_BEARING_SHARED_POLICIES: tuple[str, ...] = (
    SHARED_BRANCH, PRIMARY_HOME, REFERENCE_OR_ALIAS,
)

# --- user actions ---------------------------------------------------------------

ACCEPT: str = "accept"
RENAME: str = "rename"
MERGE: str = "merge"
MOVE_UNDER_ROOT: str = "move-under-root"
DEFER: str = "defer"
CREATE_MANUALLY: str = "create-manually"
ADD: str = "add"
REMOVE: str = "remove"
SPLIT: str = "split"
NEST: str = "nest"
REORDER: str = "reorder"
IGNORE: str = "ignore"
DRAG_GROUP_INTO_BRANCH: str = "drag-group-into-branch"
DELETE_SUGGESTED_AREA: str = "delete-suggested-area"

#: Everything §5.1, §5.2 and §5's opening give the user on a branch candidate.
BRANCH_ACTIONS: tuple[str, ...] = (
    ACCEPT, RENAME, MERGE, MOVE_UNDER_ROOT, DEFER, CREATE_MANUALLY,
    ADD, REMOVE, SPLIT, NEST, REORDER, IGNORE,
    DRAG_GROUP_INTO_BRANCH, DELETE_SUGGESTED_AREA,
)

PRESERVE: str = "preserve"
ADOPT_AS_BRANCH: str = "adopt-as-branch"
MERGE_WITH_PROPOSAL: str = "merge-with-proposal"
ATTACH_BENEATH: str = "attach-beneath"
RENAME_PROPOSAL_TO_MATCH: str = "rename-proposal-to-match"
LEAVE_UNTOUCHED: str = "leave-untouched"

#: §5.10's six. Every one is an explicit user action; §5.10 forbids reaching any
#: of these outcomes because a template would have produced a different shape.
EXISTING_FOLDER_ACTIONS: tuple[str, ...] = (
    PRESERVE, ADOPT_AS_BRANCH, MERGE_WITH_PROPOSAL, ATTACH_BENEATH,
    RENAME_PROPOSAL_TO_MATCH, LEAVE_UNTOUCHED,
)

REPARENT: str = "re-parent"
DELETE: str = "delete"
ADOPT_EXISTING: str = "adopt-existing"
ADD_SCOPED_GENERAL: str = "add-scoped-general"
SET_SHARED_MATERIAL_POLICY: str = "set-shared-material-policy"
ENABLE_RESIDUAL: str = "enable-residual"
DISABLE_RESIDUAL: str = "disable-residual"

#: §8.2: every canvas action that alters the draft tree appends one
#: `destination-tree edit` event carrying one of these.
#:
#: This is NOT `BRANCH_ACTIONS`. The two sets are deliberately different: the
#: canvas offers `delete-suggested-area` and `drag-group-into-branch`, the event
#: log records `delete` and `re-parent`. `record_tree_edit` checks against THIS
#: tuple, so a test that passes a `BRANCH_ACTIONS` spelling raises
#: `OutOfVocabulary` before P1 ever sees the row.
TREE_EDIT_ACTIONS: tuple[str, ...] = (
    ACCEPT, RENAME, MERGE, SPLIT, NEST, REPARENT, REORDER, IGNORE, DELETE,
    CREATE_MANUALLY, ADOPT_EXISTING, ENABLE_RESIDUAL, DISABLE_RESIDUAL,
    ADD_SCOPED_GENERAL, SET_SHARED_MATERIAL_POLICY,
)

ADOPT_VERSION: str = "adopt_version"
RESTORE_VERSION: str = "restore_version"

#: §8.8's two version actions, in P13's spelling. They act on a plan version
#: rather than on a node, so they are not `destination-tree edit` actions.
VERSION_ACTIONS: tuple[str, ...] = (ADOPT_VERSION, RESTORE_VERSION)

# --- diffs and warnings ---------------------------------------------------------

DIFF_ADDED: str = "added"
DIFF_REMOVED: str = "removed"
DIFF_RENAMED: str = "renamed"
DIFF_REPARENTED: str = "re-parented"
DIFF_RETEMPLATED: str = "re-templated"
DIFF_REORDERED: str = "re-ordered"
DIFF_TYPE_CHANGED: str = "type-changed"

#: §8.8's seven node-level changes. P11 computes the file-level consequence from
#: this diff; P10 does not, because P10 holds no placement decision.
DIFF_KINDS: tuple[str, ...] = (
    DIFF_ADDED, DIFF_REMOVED, DIFF_RENAMED, DIFF_REPARENTED, DIFF_RETEMPLATED,
    DIFF_REORDERED, DIFF_TYPE_CHANGED,
)

WARN_ONE_CHILD: str = "one-child-level"
WARN_REPEATED_PARENT: str = "repeated-parent-concept"
WARN_EXCESSIVE_DEPTH: str = "excessive-depth"
WARN_TINY_FOLDERS: str = "tiny-folder-distribution"
RECOMMEND_FLATTEN: str = "flatten-recommendation"

#: §5.9's four warnings plus its flattening recommendation. Every one needs a
#: threshold the design deliberately does not set, so none can fire without
#: configuration (SPEC open question 2).
WARNING_KINDS: tuple[str, ...] = (
    WARN_ONE_CHILD, WARN_REPEATED_PARENT, WARN_EXCESSIVE_DEPTH,
    WARN_TINY_FOLDERS, RECOMMEND_FLATTEN,
)

# --- borrowed values, named because they collide or because they have no name ----
#
# §8.2 reserves these two names as bare strings inside a frozenset; P1 publishes
# no named constant for either. P10 gives each one home rather than a literal at
# every call site, and asserts membership so a rename upstream fails here loudly.

TEMPLATE_APPLICATION: str = "template application"
DESTINATION_TREE_EDIT: str = "destination-tree edit"

P10_EVENT_TYPES: tuple[str, ...] = (TEMPLATE_APPLICATION, DESTINATION_TREE_EDIT)

for _name in P10_EVENT_TYPES:
    if _name not in RESERVED_EVENT_TYPES:  # pragma: no cover - import-time guard
        raise ImportError(
            f"{_name!r} is no longer one of §8.2's reserved event names; P10 "
            "appends only names P1 reserves and mints none of its own"
        )

#: P2's two P10 stages. `P10` is not a stage id: a part name in that field would
#: leave two of §8.5's ten stages with no producer.
TEMPLATE_GENERATION: str = "template_generation"
TREE_DESIGN: str = "tree_design"
P10_STAGE_IDS: tuple[str, ...] = (TEMPLATE_GENERATION, TREE_DESIGN)

#: P2's two P10 dimensions. Two lists, not one: `template_generation` is a stage
#: and `template` is a dimension, and P2 derives no mapping between them.
DIMENSION_TEMPLATE: str = "template"
DIMENSION_TREE: str = "tree"
P10_DIMENSIONS: tuple[str, ...] = (DIMENSION_TEMPLATE, DIMENSION_TREE)

#: P2's envelope vocabulary, imported. P10 maps its own results into these and
#: restates neither set in words of its own.
P2_OUTCOMES: tuple[str, ...] = _P2_OUTCOMES
P2_BUDGET_STATES: tuple[str, ...] = _P2_BUDGET_STATES

#: The Site-E dimension tier, imported. P8 reads it off the payload to classify
#: against the dossier closure (Contract W2) and P10 reads it to decide whether
#: C2 applies (Contract W5), so it has ONE home and it is P8's, beside the gate
#: that consumes it. A second spelling here would be a tier P10 accepted and P8
#: classified differently, on the same response.
DIMENSION_SCOPE_VALUES: tuple[str, ...] = DIMENSION_SCOPES

#: P8's call site and its single eligibility reason, imported.
CALL_SITE_TEMPLATE: str = E_TEMPLATE
TEMPLATE_ELIGIBILITY_REASONS: tuple[str, ...] = TEMPLATE_ELIGIBILITY

#: P13 collects tree edits on one of two surfaces (§5, §8.8). P13 is unbuilt and
#: publishes no constant, so P10 names them here and Task 16 replaces this block
#: with P13's import.
SURFACE_CANVAS: str = "canvas"
SURFACE_PLAN_VERSION: str = "plan_version"
REVIEW_SURFACES: tuple[str, ...] = (SURFACE_CANVAS, SURFACE_PLAN_VERSION)

# --- the registry ---------------------------------------------------------------

#: Every closed set P10 PUBLISHES, by the record field it governs. BRIEF §11
#: applies to each: a tuple here AND a named constant for every member, and the
#: guard test walks this map, so a set added without an entry is a set with no
#: test. `event_type`, `stage_id` and `dimension` carry borrowed VALUES but sit
#: here because their owners publish no constant and P10 therefore names them.
P10_OWNED_SETS: MappingProxyType = MappingProxyType({
    "node_type": NODE_TYPES,
    "node_role": NODE_ROLES,
    "disposition": RESIDUAL_DISPOSITIONS,
    "refinement_disposition": REFINEMENT_DISPOSITIONS,
    "origin_kind": ORIGIN_KINDS,
    "scope_kind": SCOPE_KINDS,
    "publication_state": PUBLICATION_STATES,
    "requirement": DIMENSION_REQUIREMENTS,
    "binding_state": BINDING_STATES,
    "dimension_action": DIMENSION_ACTIONS,
    "composition_gate": COMPOSITION_GATES,
    "gate_consequence": GATE_CONSEQUENCES,
    "template_check": TEMPLATE_CHECKS,
    "residual_template_name": RESIDUAL_TEMPLATE_NAMES,
    "residual_slot": RESIDUAL_SLOTS,
    "treatment": RESIDUAL_TREATMENTS,
    "residual_action": RESIDUAL_LIBRARY_ACTIONS,
    "shared_material_policy": SHARED_MATERIAL_POLICIES,
    "branch_action": BRANCH_ACTIONS,
    "existing_folder_action": EXISTING_FOLDER_ACTIONS,
    "tree_edit_action": TREE_EDIT_ACTIONS,
    "version_action": VERSION_ACTIONS,
    "diff_kind": DIFF_KINDS,
    "warning_kind": WARNING_KINDS,
    "event_type": P10_EVENT_TYPES,
    "stage_id": P10_STAGE_IDS,
    "dimension": P10_DIMENSIONS,
    "surface": REVIEW_SURFACES,
})

#: Every closed set P10 CARRIES but does not publish. The owner names each
#: member; P10 names none of them, because a constant here would be the second
#: home `test_no_module_outside_the_vocabulary_spells_a_closed_value` forbids and
#: would silently disagree with the owner the day the owner adds a member.
BORROWED_SETS: MappingProxyType = MappingProxyType({
    "outcome": P2_OUTCOMES,
    "budget_state": P2_BUDGET_STATES,
    "membership_basis": MEMBERSHIP_BASES,
    "handling_class": HANDLING_CLASSES,
    "operation_mode": OPERATION_MODES,
    "correction_scope": CORRECTION_SCOPES,
    "curation_signal": CURATION_SIGNAL_VALUES,
    "eligibility_reason": TEMPLATE_ELIGIBILITY_REASONS,
    "dimension_scope": DIMENSION_SCOPE_VALUES,
})

#: Both halves, by record field. This is what the no-second-home guard walks: a
#: borrowed value spelled as a literal in another P10 module is the same defect
#: as an owned one.
P10_CLOSED_SETS: MappingProxyType = MappingProxyType(
    {**P10_OWNED_SETS, **BORROWED_SETS}
)


class OutOfVocabulary(ValueError):
    """A value outside a closed P10 set. Not a fallback; a load error."""


def check(value: object, closed: tuple[str, ...], *, name: str) -> str:
    """One membership test. The closed set is named; the nearest match is not.

    Naming a nearest match would be a suggestion, and a suggestion in a
    vocabulary this size is how a misspelling becomes a silent downgrade.
    """
    if not isinstance(value, str) or value not in closed:
        raise OutOfVocabulary(
            f"{name} is not one of the {len(closed)} values P10 defines for it. "
            "Adding a member is a contract revision, not an implementation "
            "decision."
        )
    return value
