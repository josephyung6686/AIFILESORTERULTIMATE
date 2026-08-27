# src/tree_design/routing.py
"""Branch evidence in; a small explained candidate set out. No nodes.

The route is deterministic and evidence-bound:

    accepted scaffold branch
      -> branch context (groups, domains, facts, purpose, privacy)
      -> eligible applicability rows
      -> candidate compositions
      -> C1-C8 against the branch's actual evidence
      -> a bounded, ranked, INERT candidate set

Domain is one applicability signal, never a one-template ownership key. A row
makes a recipe eligible to PREVIEW; nothing here activates one, and nothing here
writes a node. C8 is the gate that says so, and it is the last one because every
earlier gate can still turn a plausible recipe into a refusal.

THE GATES DO NOT SHARE ONE CONSEQUENCE (owner ruling). Six refuse and cannot be
overridden: a missing artefact (C1), a minted field (C2), evidence that does not
support the recipe (C3), material a "successful" preview would drop (C6), a
privacy floor weaker than an included fragment's (C7), and a template that
activated itself (C8). Two surface a CHOICE the user resolves: which field an
ambiguous role means (C4) and which nesting two disagreeing partial orders
should become (C5). `CompositionOverride` can only be constructed for the second
kind — a refusal is not overridable at the point where an override would be
written down, not merely at the point where it would be honoured.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType

from tree_design.catalogue import TemplateCatalogue
from tree_design.config import TreeLimits
from tree_design.templates import (
    ApplicabilityRef,
    CompositionConflict,
    PurposeProfileRef,
    ResolvedDimension,
    TemplateApplicability,
    merge_fragment_constraints,
    resolve_fragment_imports,
)
from tree_design.upstream import AcceptedGroup, UpstreamUnavailable, resolve_role_to_field
from tree_design.vocabulary import (
    ACTION_SELECTED,
    SCOPE_SCHEMA_FIELD,
    C1,
    C2,
    C3,
    C4,
    C5,
    C6,
    COMPOSITION_GATES,
    GATE_WARN,
    OVERRIDABLE_GATES,
)


@dataclass(frozen=True)
class BranchContext:
    """Everything the router may consider. Nothing here is a domain label alone."""

    branch_node_id: str
    domains: tuple[str, ...]
    accepted_groups: tuple[AcceptedGroup, ...]
    member_file_ids: frozenset[str]
    handling_classes: frozenset[str]
    purpose_profile_refs: tuple[PurposeProfileRef, ...] = ()


@dataclass(frozen=True)
class CompositionOverride:
    """One WARN-class gate the user resolved, and the decision they made.

    Constructing one for a REFUSE-class gate raises. That is deliberate: a
    record that CAN hold `gate="C7"` is one click from honouring it, and the
    owner ruling is that privacy and safety gates are not overridable at all.

    `approved_by` names the recorded user action. An override with no recorded
    action is the same defect C8 exists to prevent, one gate earlier.
    """

    gate: str
    approved_by: str
    #: C4: the field the user meant, per ambiguous role. Every choice must be one
    #: of the fields the applicability rows actually offered for that role.
    role_choices: Mapping[str, str] = field(default_factory=dict)
    #: C5: the nesting the user picked when the combined partial orders cycled.
    role_order: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.gate not in OVERRIDABLE_GATES:
            raise CompositionConflict(
                self.gate, [self.gate],
                "this gate refuses and is not overridable. A privacy, evidence, "
                "coverage, identity or activation failure is not a tidiness "
                "preference, and no recorded approval turns it into one"
            )
        if not self.approved_by or not str(self.approved_by).strip():
            raise CompositionConflict(
                self.gate, [self.gate],
                "an override names the recorded user action that authorised it; "
                "an unattributed override is indistinguishable from the system "
                "deciding for the user"
            )
        object.__setattr__(self, "role_choices",
                           MappingProxyType(dict(self.role_choices)))
        object.__setattr__(self, "role_order", tuple(self.role_order))


@dataclass(frozen=True)
class CompositionCandidate:
    applicability_refs: tuple[ApplicabilityRef, ...]
    resolved_dimensions: tuple[ResolvedDimension, ...]
    privacy_floor: str
    covered_file_ids: frozenset[str]
    gates_passed: tuple[str, ...]
    #: The WARN-class gates a recorded user decision resolved. Empty on a
    #: candidate that passed every gate outright, so "the user had to choose" is
    #: visible in the preview rather than buried in the log.
    overridden_gates: tuple[str, ...]
    explanation: str


@dataclass(frozen=True)
class RoutingReport:
    candidates: tuple[CompositionCandidate, ...]
    conflicts: tuple[CompositionConflict, ...]
    deferred: int

    @property
    def refusals(self) -> tuple[CompositionConflict, ...]:
        """The conflicts no user gesture can clear. Derived from the gate."""
        return tuple(c for c in self.conflicts if not c.overridable)

    @property
    def resolvable(self) -> tuple[CompositionConflict, ...]:
        """The conflicts that are choices. The surface offers these; it must not
        offer the refusals, and deriving both from one list is what keeps the two
        halves from drifting apart."""
        return tuple(c for c in self.conflicts if c.overridable)


def eligible_rows(catalogue: TemplateCatalogue,
                  context: BranchContext) -> tuple[TemplateApplicability, ...]:
    """Every row whose schema is one of this branch's domains.

    Eligibility is not selection. A row here has done nothing but earn the right
    to be checked against the branch's actual evidence by C3.
    """
    rows: list[TemplateApplicability] = []
    for domain in context.domains:
        rows.extend(catalogue.rows_for_schema(domain))
    return tuple(rows)


def _overrides_by_gate(
        overrides: Sequence[CompositionOverride]) -> dict[str, CompositionOverride]:
    by_gate: dict[str, CompositionOverride] = {}
    for override in overrides:
        if override.gate in by_gate:
            raise CompositionConflict(
                override.gate, [override.gate],
                "two overrides answer one gate; a question with two answers has "
                "none")
        by_gate[override.gate] = override
    return by_gate


def evaluate_composition(
    conn: sqlite3.Connection,
    catalogue: TemplateCatalogue,
    context: BranchContext,
    rows: Sequence[TemplateApplicability],
    *,
    privacy_rank: Callable[[str], int],
    satisfies_purpose_profile: Callable[[PurposeProfileRef, Sequence[AcceptedGroup]], bool],
    overrides: Sequence[CompositionOverride] = (),
) -> CompositionCandidate:
    """Run C1-C8 over one candidate set of rows. Raise or return; never both."""
    if not rows:
        raise CompositionConflict(
            C3, [*context.domains],
            "no applicability row makes any recipe eligible for this branch's "
            "domains, and there is no generic fallback to invent")

    by_gate = _overrides_by_gate(overrides)
    overridden: list[str] = []

    # C1 — identity. Every template, fragment and version the rows name exists.
    fragments = []
    for row in rows:
        definition = catalogue.definitions.get((row.template_id, row.template_version))
        if definition is None:
            raise CompositionConflict(
                C1, [f"{row.template_id}@{row.template_version}"],
                "the packaged release does not contain this definition version")
        for ref in definition.fragment_refs:
            fragments.extend(resolve_fragment_imports(catalogue, ref))
    # Deduplicate by exact identity, preserving import order.
    seen: set[tuple[str, int]] = set()
    ordered = []
    for fragment in fragments:
        key = (fragment.fragment_id, fragment.fragment_version)
        if key not in seen:
            seen.add(key)
            ordered.append(fragment)

    # C3 — applicability from evidence, not from a domain label. Run before C2
    # so a branch that was never eligible does not spend field lookups.
    for row in rows:
        if row.purpose_profile_ref is None:
            continue
        if not satisfies_purpose_profile(row.purpose_profile_ref,
                                         context.accepted_groups):
            raise CompositionConflict(
                C3, [row.purpose_profile_ref.purpose_profile_id, row.applicability_id],
                "the branch's accepted groups do not satisfy this authored purpose "
                "profile; a domain name alone is insufficient")

    # C4 — a required role resolves once. Competing mappings are SURFACED, and
    # the user resolves them; the router still picks none by itself.
    offered: dict[str, set[str]] = {}
    for row in rows:
        for binding in row.role_bindings:
            offered.setdefault(binding.role_ref, set()).add(binding.field_ref)
    ambiguous = sorted(role for role, fields in offered.items() if len(fields) > 1)
    chosen: dict[str, str] = {
        role: next(iter(fields)) for role, fields in offered.items()
        if len(fields) == 1
    }
    if ambiguous:
        detail = "; ".join(f"{role} -> {sorted(offered[role])}" for role in ambiguous)
        override = by_gate.get(C4)
        if override is None:
            raise CompositionConflict(
                C4, ambiguous,
                f"a role resolves to more than one field ({detail}) and P10 picks "
                "none silently")
        for role in ambiguous:
            picked = override.role_choices.get(role)
            if picked not in offered[role]:
                raise CompositionConflict(
                    C4, [role],
                    f"the override chose {picked!r} for {role!r}, which no "
                    f"applicability row offered ({sorted(offered[role])}). An "
                    "override resolves an ambiguity the rows created; it is not a "
                    "second door into a field no row allows")
            chosen[role] = picked
        overridden.append(C4)

    # C2 — every resolved role maps to a live, destination-eligible P6 field.
    for role, field_ref in sorted(chosen.items()):
        try:
            resolve_role_to_field(conn, role_ref=role, field_ref=field_ref)
        except UpstreamUnavailable as exc:
            raise CompositionConflict(C2, [role, field_ref], str(exc)) from exc

    # C5 — combined order is acyclic, and the merge is intersection, not
    # last-writer-wins. `merge_fragment_constraints` raises C5 on either failure;
    # only the order half can be resolved by the user's chosen nesting.
    order_override = by_gate.get(C5)
    merged = merge_fragment_constraints(
        ordered, privacy_rank=privacy_rank,
        role_order=order_override.role_order if order_override else None)
    if merged.order_was_overridden:
        overridden.append(C5)
    position = {role: index for index, role in enumerate(merged.ordered_roles)}
    resolved = tuple(
        ResolvedDimension(
            role_ref=role,
            field_ref=chosen[role],
            # A preview records `selected`: the user has chosen among what the
            # recipe offered, and has not yet acted on the branch. The edit
            # actions (`reordered`, `renamed`, ...) belong to the binding, after
            # the branch exists.
            action=ACTION_SELECTED,
            order_index=position.get(role, len(position)),
            display_label=None,
            # Every dimension the ROUTER resolves came from an applicability
            # row's role binding and passed C2, so it is schema-field by
            # construction. A template-local level has no row and no field; it
            # arrives from an approved Site-E proposal, not from routing.
            scope=SCOPE_SCHEMA_FIELD,
        )
        for role in sorted(chosen, key=lambda r: position.get(r, len(position)))
    )

    # C6 — coverage. Every member of every accepted group in this branch is
    # reachable through one of the selected rows' schemas.
    schemas = {row.uses_schema for row in rows}
    covered: set[str] = set()
    dropped: list[str] = []
    for group in context.accepted_groups:
        if group.domain in schemas:
            covered.update(member.file_id for member in group.members)
        else:
            dropped.extend(member.file_id for member in group.members)
    if dropped:
        raise CompositionConflict(
            C6, sorted(dropped),
            "this composition covers no schema for these members, so a preview "
            "would silently drop them")

    # C7 — the strongest included restriction survives the merge.
    floor = merged.privacy_floor

    # C8 — activation. Reaching here produces a preview and nothing else.

    explanation = (
        f"{len(rows)} applicability row(s) across {sorted(schemas)} resolve "
        f"{len(resolved)} dimension(s) from this branch's accepted groups; the "
        f"combined privacy floor is {floor}."
    )
    if overridden:
        explanation += (
            f" The user resolved {', '.join(overridden)} by recorded decision."
        )
    return CompositionCandidate(
        applicability_refs=tuple(
            ApplicabilityRef(row.applicability_id, row.applicability_version)
            for row in rows),
        resolved_dimensions=resolved,
        privacy_floor=floor,
        covered_file_ids=frozenset(covered),
        gates_passed=tuple(COMPOSITION_GATES),
        overridden_gates=tuple(overridden),
        explanation=explanation,
    )


def route_branch(
    conn: sqlite3.Connection,
    catalogue: TemplateCatalogue,
    context: BranchContext,
    *,
    limits: TreeLimits | None,
    privacy_rank: Callable[[str], int],
    satisfies_purpose_profile: Callable[[PurposeProfileRef, Sequence[AcceptedGroup]], bool],
    rank_candidates: Callable[[Sequence[CompositionCandidate]], Sequence[CompositionCandidate]],
    overrides: Sequence[CompositionOverride] = (),
) -> RoutingReport:
    """One template's worth of candidates per eligible definition, bounded.

    Ranking is injected because the design fixes no weights, and the ceiling is
    P1's `tree.max_folder_proposals_and_depth`. Surplus candidates are DEFERRED
    and counted, never silently dropped: §8.6 requires the interface to "show the
    difference between completed work and deferred work".

    Conflicts come back whole. The report splits them into `refusals` and
    `resolvable` by reading each gate's consequence, so a surface can offer the
    user the choices and only the choices.
    """
    candidates: list[CompositionCandidate] = []
    conflicts: list[CompositionConflict] = []

    rows = eligible_rows(catalogue, context)
    by_template: dict[tuple[str, int], list[TemplateApplicability]] = {}
    for row in rows:
        by_template.setdefault((row.template_id, row.template_version), []).append(row)

    if not by_template:
        conflicts.append(CompositionConflict(
            C3, [*context.domains],
            "no applicability row makes any recipe eligible for this branch's "
            "domains, and there is no generic fallback to invent"))

    for group in by_template.values():
        try:
            candidates.append(evaluate_composition(
                conn, catalogue, context, group, privacy_rank=privacy_rank,
                satisfies_purpose_profile=satisfies_purpose_profile,
                overrides=overrides))
        except CompositionConflict as conflict:
            conflicts.append(conflict)

    ranked = list(rank_candidates(candidates))
    deferred = 0
    if limits is not None and len(ranked) > limits.max_folder_proposals_and_depth:
        deferred = len(ranked) - limits.max_folder_proposals_and_depth
        ranked = ranked[:limits.max_folder_proposals_and_depth]

    return RoutingReport(
        candidates=tuple(ranked),
        conflicts=tuple(conflicts),
        deferred=deferred,
    )
