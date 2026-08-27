# src/tree_design/templates.py
"""The four template records, kept apart on purpose.

`TemplateFragment` is reusable organization logic: semantic roles, recommended
order, optionality, safety constraints, its own identity and version. It holds no
user value and no field mapping, and it creates no node.

`TemplateDefinition` composes exact fragment versions plus template-local
dimensions. P10 publishes no ambiguous generic `Template` record beside it.

`TemplateApplicability` maps roles to live P6 fields for exactly ONE
`uses_schema`. Several rows may reference one definition and one schema may have
several rows; that is the many-to-many seam, and it never widens a P6 allow-list
because every individual row still resolves against one schema.

`BranchTemplateBinding` is what one branch in one draft chose. Applying or
editing a recipe in one branch cannot change another branch that started from the
same definition, and a newer definition, fragment or applicability version is a
new candidate rather than an automatic migration.

TWO OWNER RULINGS ARE BUILT IN HERE RATHER THAN LEFT TO CONVENTION:

* **Dimension order is a RUNTIME choice** (§5.3, §5.8). A definition therefore
  carries `candidate_orders` and names one default; it does NOT carry a single
  `dimensions` tuple, because that shape makes the recipe's author the one who
  decided the ordering. `BranchTemplateBinding.chosen_order_id` records which
  candidate the user took, or `None` when they composed their own.
* **`purpose_profile_ref` is authored and versioned, and enforced distinct**
  from a P6 purpose value and from a runtime P9 group id. Both of those are bare
  strings minted elsewhere; a purpose profile is a reviewed record with a
  version, and the record refuses anything that is not one.
"""
from __future__ import annotations

import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from tree_design.config import ConfigurationRequired
from tree_design.vocabulary import (
    BINDING_STATES,
    C1,
    C5,
    COMPOSITION_GATE_CONSEQUENCE,
    COMPOSITION_GATES,
    DIMENSION_ACTIONS,
    DIMENSION_SCOPE_VALUES,
    GATE_WARN,
    DIMENSION_REQUIREMENTS,
    ORIGIN_KINDS,
    PUBLICATION_STATES,
    REFINEMENT_DISPOSITIONS,
    SCOPE_KINDS,
    SCOPE_TEMPLATE_LOCAL,
    WORKFLOW_APPROVED,
    check,
)

_SEPARATORS = frozenset({"/", "\\", os.sep, os.altsep or "/"})

#: The namespace every authored purpose profile carries. P10 owns it, so it is
#: spelled once, here. It exists to make "distinct from a P6 purpose value and a
#: runtime P9 group id" a STRUCTURAL fact rather than a naming convention: P6's
#: field keys are bare identifiers (`purpose`) and P9 mints
#: `group:{file_id}:{seed_kind}` (`src/grouping/pipeline.py:323`), and neither
#: can ever carry this prefix.
PURPOSE_PROFILE_NAMESPACE: str = "pp."


class MalformedTemplateRecord(ValueError):
    """A template record that cannot be built is one that cannot mislead."""


class CompositionConflict(RuntimeError):
    """A gate refused. The report names the inputs and the user's choices.

    Conflict handling is fail-closed and explanatory: the composable-template
    design fixes the offered choices as "omit one fragment, change the order,
    flatten a level, keep the branch shallow, or defer". There is no hidden
    precedence rule and no last-writer-wins.

    `consequence` and `overridable` are READ from the gate, never passed in.
    Owner ruling: a privacy or safety gate refuses and no user gesture waves it
    through; a tidiness or structure gate surfaces a choice the user resolves. A
    conflict that could be told which it was would eventually be told wrong.
    """

    CHOICES: tuple[str, ...] = (
        "omit one fragment",
        "change the order",
        "flatten a level",
        "keep the branch shallow",
        "defer",
    )

    def __init__(self, gate: str, conflicting: Sequence[str], detail: str) -> None:
        self.gate = check(gate, COMPOSITION_GATES, name="composition gate")
        self.consequence = COMPOSITION_GATE_CONSEQUENCE[gate]
        self.overridable = self.consequence == GATE_WARN
        self.conflicting = tuple(conflicting)
        self.choices = self.CHOICES
        super().__init__(
            f"{gate}: {detail}. Conflicting inputs: {', '.join(self.conflicting)}. "
            f"Available choices: {'; '.join(self.CHOICES)}."
        )


def _require(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MalformedTemplateRecord(f"{name} is required and cannot be empty")
    return value


def _version(value: object, *, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise MalformedTemplateRecord(
            f"{name} is an exact positive version. Reuse is by stable id and "
            "exact version, never by copied JSON and never by a range."
        )
    return value


@dataclass(frozen=True)
class FragmentRef:
    fragment_id: str
    fragment_version: int

    def __post_init__(self) -> None:
        _require(self.fragment_id, name="FragmentRef.fragment_id")
        _version(self.fragment_version, name="FragmentRef.fragment_version")

    def key(self) -> tuple[str, int]:
        return (self.fragment_id, self.fragment_version)


@dataclass(frozen=True)
class ApplicabilityRef:
    applicability_id: str
    applicability_version: int

    def __post_init__(self) -> None:
        _require(self.applicability_id, name="ApplicabilityRef.applicability_id")
        _version(self.applicability_version,
                 name="ApplicabilityRef.applicability_version")

    def key(self) -> tuple[str, int]:
        return (self.applicability_id, self.applicability_version)


@dataclass(frozen=True)
class PurposeProfileRef:
    """An AUTHORED, versioned purpose context. Not a value; not a run artefact.

    The two things it must never be are both bare strings minted somewhere else:
    P6's `purpose` field value (a per-file extracted string, `fields.py:172`) and
    a runtime P9 group id (`group:{file_id}:{seed_kind}`). Requiring the
    namespace AND a version makes both structurally impossible to store here,
    which is what "distinct" has to mean if anything is to check it.
    """

    purpose_profile_id: str
    purpose_profile_version: int

    def __post_init__(self) -> None:
        _require(self.purpose_profile_id, name="PurposeProfileRef.purpose_profile_id")
        _version(self.purpose_profile_version,
                 name="PurposeProfileRef.purpose_profile_version")
        if not self.purpose_profile_id.startswith(PURPOSE_PROFILE_NAMESPACE):
            raise MalformedTemplateRecord(
                f"{self.purpose_profile_id!r} is not an authored purpose profile "
                f"id. One carries the {PURPOSE_PROFILE_NAMESPACE!r} namespace, "
                "which is what keeps it distinct from a P6 `purpose` field value "
                "and from a runtime P9 group id; a recipe pinned to either would "
                "be pinned to one user's run."
            )
        if len(self.purpose_profile_id) == len(PURPOSE_PROFILE_NAMESPACE):
            raise MalformedTemplateRecord(
                "a purpose profile id is a namespace AND a name; the namespace "
                "alone identifies nothing"
            )


@dataclass(frozen=True)
class TemplateFragment:
    """A reusable organization recipe. No values, no field mappings, no nodes."""

    fragment_id: str
    fragment_version: int
    roles: tuple[str, ...]
    relative_order: tuple[tuple[str, str], ...]
    imports: tuple[FragmentRef, ...]
    optional_roles: tuple[str, ...]
    metadata_only_roles: tuple[str, ...]
    allowed_values: Mapping[str, Sequence[str]]
    privacy_floor: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        _require(self.fragment_id, name="TemplateFragment.fragment_id")
        _version(self.fragment_version, name="TemplateFragment.fragment_version")
        _require(self.privacy_floor, name="TemplateFragment.privacy_floor")
        if not self.roles:
            raise MalformedTemplateRecord(
                "a fragment with no semantic role organizes nothing")
        for name in ("roles", "optional_roles", "metadata_only_roles", "provenance"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        object.__setattr__(
            self, "relative_order",
            tuple(tuple(pair) for pair in self.relative_order))
        object.__setattr__(
            self, "imports",
            tuple(ref if isinstance(ref, FragmentRef) else FragmentRef(**ref)
                  for ref in self.imports))
        object.__setattr__(self, "allowed_values",
                           {k: tuple(v) for k, v in dict(self.allowed_values).items()})
        stray = (set(self.optional_roles) | set(self.metadata_only_roles)) - set(self.roles)
        if stray:
            raise MalformedTemplateRecord(
                f"{sorted(stray)} are marked optional or metadata-only but are not "
                "roles this fragment defines"
            )
        if not self.provenance:
            raise MalformedTemplateRecord(
                "a fragment records which reviewed contexts produced it; without "
                "provenance nobody can check that at least two independent "
                "contexts justified extracting it"
            )


@dataclass(frozen=True)
class TemplateDimension:
    role_ref: str
    order_index: int
    requirement: str
    metadata_only: bool
    retrieval_rationale: str

    def __post_init__(self) -> None:
        _require(self.role_ref, name="TemplateDimension.role_ref")
        check(self.requirement, DIMENSION_REQUIREMENTS, name="requirement")
        if not isinstance(self.order_index, int) or isinstance(self.order_index, bool):
            raise MalformedTemplateRecord("order_index is an integer position")
        _require(self.retrieval_rationale,
                 name="TemplateDimension.retrieval_rationale")


@dataclass(frozen=True)
class DimensionOrder:
    """ONE way to nest a recipe's dimensions, offered to the user as a choice.

    §5.3 and §5.8 make the ordering a runtime decision — "Subject then Type" and
    "Type then Subject" organize the same material for two different retrieval
    habits, and only the person searching knows which one they have. A definition
    therefore SHIPS the alternatives and recommends one; it does not decide.

    `rationale` is required because an unexplained alternative is not a choice
    the user can make: the interface has to be able to say what each order is
    good for.
    """

    order_id: str
    dimensions: tuple[TemplateDimension, ...]
    is_default: bool
    rationale: str

    def __post_init__(self) -> None:
        _require(self.order_id, name="DimensionOrder.order_id")
        _require(self.rationale, name="DimensionOrder.rationale")
        object.__setattr__(self, "dimensions", tuple(self.dimensions))
        if not isinstance(self.is_default, bool):
            raise MalformedTemplateRecord("DimensionOrder.is_default is a boolean")
        if not self.dimensions:
            raise MalformedTemplateRecord(
                "an order with no dimension orders nothing")
        roles = [d.role_ref for d in self.dimensions]
        if len(set(roles)) != len(roles):
            raise MalformedTemplateRecord(
                f"{self.order_id!r} names one role twice; a role is one level")
        indices = sorted(d.order_index for d in self.dimensions)
        if indices != list(range(len(self.dimensions))):
            raise MalformedTemplateRecord(
                f"{self.order_id!r} has positions {indices}; an order is a "
                "contiguous nesting from 0, and a gap or a duplicate leaves the "
                "level it names undefined"
            )

    def role_set(self) -> frozenset[str]:
        return frozenset(d.role_ref for d in self.dimensions)


@dataclass(frozen=True)
class TemplateDefinition:
    template_id: str
    template_version: int
    origin_kind: str
    scope_kind: str
    publication_state: str
    fragment_refs: tuple[FragmentRef, ...]
    candidate_orders: tuple[DimensionOrder, ...]
    optional_branch_patterns: tuple[str, ...]
    sensitivity_policy_ref: str
    validation_constraints: tuple[str, ...]
    example_label_chains: tuple[tuple[str, ...], ...]

    def __post_init__(self) -> None:
        _require(self.template_id, name="TemplateDefinition.template_id")
        _version(self.template_version, name="TemplateDefinition.template_version")
        check(self.origin_kind, ORIGIN_KINDS, name="origin_kind")
        check(self.scope_kind, SCOPE_KINDS, name="scope_kind")
        check(self.publication_state, PUBLICATION_STATES, name="publication_state")
        _require(self.sensitivity_policy_ref,
                 name="TemplateDefinition.sensitivity_policy_ref")
        for name in ("optional_branch_patterns", "validation_constraints"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        object.__setattr__(
            self, "fragment_refs",
            tuple(ref if isinstance(ref, FragmentRef) else FragmentRef(**ref)
                  for ref in self.fragment_refs))
        object.__setattr__(self, "candidate_orders", tuple(self.candidate_orders))
        object.__setattr__(
            self, "example_label_chains",
            tuple(tuple(chain) for chain in self.example_label_chains))
        for chain in self.example_label_chains:
            for label in chain:
                if any(sep in label for sep in _SEPARATORS):
                    raise MalformedTemplateRecord(
                        f"example label {label!r} holds a path separator. Example "
                        "chains are nested display labels used to review a recipe; "
                        "they are not destinations and P12 alone composes paths."
                    )
        self._check_orders()

    def _check_orders(self) -> None:
        if not self.candidate_orders:
            raise MalformedTemplateRecord(
                "a definition offers at least one candidate order; a recipe with "
                "no ordering cannot be previewed"
            )
        ids = [order.order_id for order in self.candidate_orders]
        if len(set(ids)) != len(ids):
            raise MalformedTemplateRecord(
                f"two candidate orders share an id in {ids}; the branch binding "
                "records the chosen id and an ambiguous one records nothing"
            )
        defaults = [order for order in self.candidate_orders if order.is_default]
        if len(defaults) != 1:
            raise MalformedTemplateRecord(
                f"{len(defaults)} candidate orders are marked default. A "
                "definition RECOMMENDS exactly one and the end user picks per "
                "branch (§5.3, §5.8); none means nothing can be previewed, and "
                "two means the recommendation is undefined."
            )
        roles = self.candidate_orders[0].role_set()
        if any(order.role_set() != roles for order in self.candidate_orders):
            raise MalformedTemplateRecord(
                "candidate orders must cover the same roles. An order that drops "
                "or adds a role is a different RECIPE, and offering it as an "
                "ordering choice would let the user silently change what the "
                "branch organizes by."
            )
        if len(roles) > 1 and len(self.candidate_orders) <= 1:
            raise MalformedTemplateRecord(
                "a recipe with more than one dimension offers at least two "
                "candidate orders. Ordering is the end user's decision per branch "
                "(§5.3, §5.8), and one candidate is a single `dimensions` tuple "
                "wearing a new field name. No maximum is enforced: a ceiling on "
                "how many orders a recipe may offer is a number the design does "
                "not state."
            )

    @property
    def default_order(self) -> DimensionOrder:
        """The one order the recipe RECOMMENDS. Not the one it imposes."""
        for order in self.candidate_orders:
            if order.is_default:
                return order
        raise MalformedTemplateRecord(  # pragma: no cover - __post_init__ forbids it
            "no default candidate order")

    @property
    def dimensions(self) -> tuple[TemplateDimension, ...]:
        """The default order's dimensions, for a reader that wants one shape."""
        return self.default_order.dimensions


@dataclass(frozen=True)
class RoleBinding:
    role_ref: str
    field_ref: str

    def __post_init__(self) -> None:
        _require(self.role_ref, name="RoleBinding.role_ref")
        _require(self.field_ref, name="RoleBinding.field_ref")


@dataclass(frozen=True)
class TemplateApplicability:
    """The join row. Exactly one `uses_schema`; provenance is mandatory.

    The composable-template design and the domain handoff both require every row
    to carry "provenance back to ratified domain rows and research evidence".
    P10's SPEC omits the field from its example JSON; it is required here,
    because a compiled row nobody can trace back to the domain research that
    justified it cannot be reviewed or retired.
    """

    applicability_id: str
    applicability_version: int
    template_id: str
    template_version: int
    uses_schema: str
    purpose_profile_ref: PurposeProfileRef | None
    allowed_fields: tuple[str, ...]
    detection_signal_refs: tuple[str, ...]
    role_bindings: tuple[RoleBinding, ...]
    exclusions: tuple[str, ...]
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        _require(self.applicability_id, name="TemplateApplicability.applicability_id")
        _version(self.applicability_version, name="applicability_version")
        _require(self.template_id, name="TemplateApplicability.template_id")
        _version(self.template_version, name="template_version")
        _require(self.uses_schema, name="TemplateApplicability.uses_schema")
        for name in ("allowed_fields", "detection_signal_refs", "exclusions",
                     "provenance"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        object.__setattr__(
            self, "role_bindings",
            tuple(b if isinstance(b, RoleBinding) else RoleBinding(**b)
                  for b in self.role_bindings))
        if self.purpose_profile_ref is not None and not isinstance(
                self.purpose_profile_ref, PurposeProfileRef):
            raise MalformedTemplateRecord(
                "purpose_profile_ref is an authored, versioned identifier. It is "
                "not a P6 `purpose` value and not a runtime P9 group id; the "
                "branch binding pins the actual accepted groups and C3 proves the "
                "evidence match."
            )
        outside = [b.field_ref for b in self.role_bindings
                   if b.field_ref not in self.allowed_fields]
        if outside:
            raise MalformedTemplateRecord(
                f"role bindings target {sorted(outside)}, which this row does not "
                "allow. A row that binds outside its own allow-list is how reuse "
                "turns a per-schema fact allow-list into a cross-domain union."
            )
        if not self.provenance:
            raise MalformedTemplateRecord(
                "provenance back to the ratified domain rows and research evidence "
                "is required; a row with none cannot be reviewed or retired"
            )


@dataclass(frozen=True)
class ResolvedDimension:
    """One level of a composition, and the tier it was resolved at.

    Contract W5 pairs `scope` and `field_ref` structurally rather than by
    convention: a `schema-field` level names a live P6 field and C2 checks it; a
    `template-local` level has NO field, so C2 is not called — calling it would
    be asking P6 to define something that is deliberately not a field.

    Neither shape can carry an `expected_values` list, because this record has no
    such attribute. A template-local level's children are accepted group labels
    and existing folder names, which are not fact values (Contract W4.2, W4.3).
    """

    role_ref: str
    field_ref: str | None
    action: str
    order_index: int
    display_label: str | None
    scope: str

    def __post_init__(self) -> None:
        _require(self.role_ref, name="ResolvedDimension.role_ref")
        check(self.action, DIMENSION_ACTIONS, name="dimension action")
        check(self.scope, DIMENSION_SCOPE_VALUES, name="dimension scope")
        if self.scope == SCOPE_TEMPLATE_LOCAL:
            if self.field_ref is not None:
                raise MalformedTemplateRecord(
                    f"a template-local level names no P6 field, but this one "
                    f"names {self.field_ref!r}. A level with a field is a "
                    "schema-field level and C2 must run for it."
                )
        elif not self.field_ref:
            raise MalformedTemplateRecord(
                "a schema-field level names the live P6 field it resolved to. "
                "`field_ref = None` is reachable ONLY through the declared "
                "template-local path (Contract W5), so a missing field here is a "
                "composition failure rather than a novel dimension."
            )
        if self.display_label is not None:
            if any(sep in self.display_label for sep in _SEPARATORS):
                raise MalformedTemplateRecord(
                    "a renamed level is a display label, never a path fragment")


@dataclass(frozen=True)
class BranchTemplateBinding:
    binding_id: str
    plan_version_id: str
    branch_node_id: str
    applicability_refs: tuple[ApplicabilityRef, ...]
    resolved_dimensions: tuple[ResolvedDimension, ...]
    accepted_group_ids: tuple[str, ...]
    state: str
    depth_disposition: str
    refinement_reason: str
    validation_report_ref: str
    approval_action_ref: str | None
    justification_fact_refs: tuple[str, ...]
    #: WHICH of the definition's candidate orders this branch took, or `None`
    #: when the user composed an order of their own. Without it, "the user
    #: accepted the kind-first candidate" and "the user hand-reordered into the
    #: same shape" are indistinguishable, and §8.8 requires ordering choices to
    #: be captured per plan version. Membership in the definition's candidate set
    #: is checked where the definition is in hand, at routing time.
    chosen_order_id: str | None

    def __post_init__(self) -> None:
        for name in ("binding_id", "plan_version_id", "branch_node_id",
                     "refinement_reason", "validation_report_ref"):
            _require(getattr(self, name), name=f"BranchTemplateBinding.{name}")
        check(self.state, BINDING_STATES, name="binding state")
        check(self.depth_disposition, REFINEMENT_DISPOSITIONS,
              name="depth_disposition")
        for name in ("applicability_refs", "resolved_dimensions",
                     "accepted_group_ids", "justification_fact_refs"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        if self.chosen_order_id is not None:
            _require(self.chosen_order_id,
                     name="BranchTemplateBinding.chosen_order_id")
        if not self.applicability_refs:
            raise MalformedTemplateRecord(
                "a binding names the exact applicability rows it resolved; without "
                "them the branch cannot say which recipe produced it"
            )
        if self.state == WORKFLOW_APPROVED and not self.approval_action_ref:
            raise MalformedTemplateRecord(
                "an approved binding names the recorded user approval. §5.7: a "
                "template does not become active merely because it is "
                "syntactically valid, so a binding that approved itself is the "
                "exact failure C8 prevents."
            )


def branch_dimension_roles(binding: "BranchTemplateBinding",
                           definition: TemplateDefinition) -> tuple[str, ...]:
    """The roles this BRANCH nests by, in the order the USER took.

    This is the only reader of `BranchTemplateBinding.chosen_order_id`, and it
    exists because a recorded decision nothing acts on is not a decision.

    §5.3 and §5.8 make the ordering a RUNTIME choice. `definition.default_order`
    is a RECOMMENDATION and `definition.dimensions` is that recommendation's
    shape; neither is ever consulted here. A §5.9 warning computed against the
    recommendation would tell a user who took kind-first that their subject-first
    nesting repeats a parent — a warning about a tree that does not exist.

    `chosen_order_id is None` means the user composed an order of their own, and
    the binding's own `resolved_dimensions` are then the record of it. Falling
    back to the default in that case would substitute the recommendation for the
    decision, which is the same defect by a quieter route — so it is refused
    instead.
    """
    if binding.chosen_order_id is None:
        if not binding.resolved_dimensions:
            raise MalformedTemplateRecord(
                f"binding {binding.binding_id!r} records no chosen order and no "
                "resolved dimensions. `chosen_order_id = None` means the user "
                "composed an order of their own, so the composition IS the "
                "record of it; with neither, nothing says how this branch nests "
                "and the recipe's recommendation is not an answer."
            )
        return tuple(
            dimension.role_ref
            for dimension in sorted(binding.resolved_dimensions,
                                    key=lambda d: d.order_index)
        )
    for order in definition.candidate_orders:
        if order.order_id == binding.chosen_order_id:
            return tuple(
                dimension.role_ref
                for dimension in sorted(order.dimensions,
                                        key=lambda d: d.order_index)
            )
    raise MalformedTemplateRecord(
        f"binding {binding.binding_id!r} took order {binding.chosen_order_id!r}, "
        f"which {definition.template_id!r}@{definition.template_version} does not "
        f"offer (it offers "
        f"{sorted(o.order_id for o in definition.candidate_orders)}). Answering "
        "with the recommended order would report a nesting the user never chose."
    )


@dataclass(frozen=True)
class MergedConstraints:
    roles: tuple[str, ...]
    relative_order: tuple[tuple[str, str], ...]
    optional_roles: frozenset[str]
    metadata_only_roles: frozenset[str]
    allowed_values: Mapping[str, tuple[str, ...]]
    privacy_floor: str
    #: The nesting the composition will preview, already resolved. Derived from
    #: the combined partial orders, or supplied by the user when those cycle.
    ordered_roles: tuple[str, ...]
    #: True only when the derived order was a CYCLE and the user's chosen order
    #: replaced it. A caller records C5 as overridden on this, never on the mere
    #: presence of a `role_order` argument — an override that resolved nothing is
    #: not an override.
    order_was_overridden: bool


def _topological(nodes: Sequence[str],
                 edges: Sequence[tuple[str, str]]) -> list[str] | None:
    """Kahn's algorithm. Returns None when the graph has a cycle."""
    incoming = {node: 0 for node in nodes}
    outgoing: dict[str, list[str]] = {node: [] for node in nodes}
    for before, after in edges:
        if before not in incoming or after not in incoming:
            continue
        outgoing[before].append(after)
        incoming[after] += 1
    ready = [node for node in nodes if incoming[node] == 0]
    order: list[str] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for nxt in outgoing[node]:
            incoming[nxt] -= 1
            if incoming[nxt] == 0:
                ready.append(nxt)
    return order if len(order) == len(nodes) else None


def resolve_fragment_imports(catalogue, ref: FragmentRef) -> tuple[TemplateFragment, ...]:
    """C1: every referenced fragment and exact version exists, and the import
    graph is acyclic. Imports come before the fragment that imports them."""
    resolved: list[TemplateFragment] = []
    seen: set[tuple[str, int]] = set()
    path: list[tuple[str, int]] = []

    def visit(current: FragmentRef) -> None:
        key = current.key()
        if key in path:
            cycle = [f"{fid}@{ver}" for fid, ver in (*path, key)]
            raise CompositionConflict(
                C1, cycle, "fragment imports form a cycle")
        if key in seen:
            return
        if not catalogue.has_fragment(*key):
            raise CompositionConflict(
                C1, [f"{key[0]}@{key[1]}"],
                "the packaged release does not contain this fragment version")
        fragment = catalogue.fragment(current)
        path.append(key)
        for imported in fragment.imports:
            visit(imported)
        path.pop()
        seen.add(key)
        resolved.append(fragment)

    visit(ref)
    return tuple(resolved)


def merge_fragment_constraints(
    fragments: Sequence[TemplateFragment],
    *,
    privacy_rank: Callable[[str], int],
    role_order: Sequence[str] | None = None,
) -> MergedConstraints:
    """Combine semantic constraints. Intersection, union, strongest — never
    last-writer-wins.

    Allowed-value sets narrow by intersection, because two fragments that both
    constrain a role both mean it. Relative order unions and is then checked for
    a cycle, because two compatible partial orders may still disagree. Privacy
    takes the strongest included restriction, because a composition that relaxed
    one fragment's floor would release material that fragment protects.

    `role_order` is the user's answer to a C5 order cycle, and it resolves ONLY
    that. The value intersection is checked before it and refuses regardless: no
    nesting the user picks can make two disjoint allowed-value sets agree, so
    that half of C5 is a refusal even though the gate is WARN-class.
    """
    roles: list[str] = []
    edges: list[tuple[str, str]] = []
    optional: set[str] = set()
    metadata_only: set[str] = set()
    allowed: dict[str, tuple[str, ...]] = {}
    floors: list[str] = []

    for fragment in fragments:
        for role in fragment.roles:
            if role not in roles:
                roles.append(role)
        edges.extend(fragment.relative_order)
        metadata_only |= set(fragment.metadata_only_roles)
        floors.append(fragment.privacy_floor)
        for role, values in fragment.allowed_values.items():
            if role in allowed:
                narrowed = tuple(v for v in allowed[role] if v in set(values))
                if not narrowed:
                    raise CompositionConflict(
                        C5, [role, *(f.fragment_id for f in fragments)],
                        f"the allowed values for {role!r} intersect to nothing")
                allowed[role] = narrowed
            else:
                allowed[role] = tuple(values)

    # A role is optional only where EVERY fragment that defines it says so. One
    # fragment requiring it is a requirement the composition must honour.
    for role in roles:
        definers = [f for f in fragments if role in f.roles]
        if definers and all(role in f.optional_roles for f in definers):
            optional.add(role)

    derived = _topological(roles, edges)
    if role_order is None:
        if derived is None:
            raise CompositionConflict(
                C5, [f"{a}->{b}" for a, b in edges],
                "the combined relative-order constraints contain a cycle")
        ordered_roles = tuple(derived)
        order_was_overridden = False
    else:
        chosen = tuple(role_order)
        if set(chosen) != set(roles) or len(chosen) != len(roles):
            raise CompositionConflict(
                C5, sorted(set(roles) ^ set(chosen)),
                "the chosen order must nest exactly the roles this composition "
                "defines; one that drops or adds a role is a different recipe")
        ordered_roles = chosen
        order_was_overridden = derived is None

    try:
        floor = max(floors, key=privacy_rank)
    except Exception as exc:
        raise ConfigurationRequired(
            f"no ordering is available for the privacy floors {sorted(set(floors))}. "
            "C7 keeps the strongest included restriction, and an ordering P10 "
            "invented could silently choose a weaker floor than an included "
            "fragment requires."
        ) from exc

    return MergedConstraints(
        roles=tuple(roles),
        relative_order=tuple(dict.fromkeys(edges)),
        optional_roles=frozenset(optional),
        metadata_only_roles=frozenset(metadata_only),
        allowed_values=allowed,
        privacy_floor=floor,
        ordered_roles=ordered_roles,
        order_was_overridden=order_was_overridden,
    )
