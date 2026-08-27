# src/tree_design/materialise.py
"""§5.4's populate step. The one module where evidence becomes structure.

The design sentence this module exists for is §5.4's: "Each template is populated
from the facts and accepted groups that already exist in the evidence database.
The system does not invent PHYS1401, UChicago, Spring 2026, or PVA/RDP; those
names emerge from validated facts, user-confirmed groups, and accepted labels.
The template simply determines how those real values could be arranged as
branches."

Everything here follows from that. A dimension contributes the DISTINCT settled
values its files actually carry, in P6's own spelling. A file with no settled
value at a level is unresolved at that level and produces no branch — §5.11
allows a tree to "be accepted even if some files remain unresolved", and the only
alternative is invention. A value nests under a parent value only when the same
files carry both, so the counts the user sees are intersections and never
products: §5.5's "three schools, five terms, and twelve course branches" is
twelve real combinations, not one hundred and eighty cells.

Two views come out of ONE pass, deliberately. `MaterialisedCandidate` is what
Task 9's V1-V6 judge; `BranchEvidence` is what the projection builds from. They
are returned together because a validator that saw a different shape from the
builder would pass a tree that cannot be built, or refuse one that can.

This module imports no other part's names. It reads P6 through
`tree_design.upstream`, which is the only module permitted to spell them.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from tree_design.config import ConfigurationRequired
from tree_design.records import ExpectedValue, Node, derive_accepts_placement
from tree_design.routing import CompositionCandidate
from tree_design.upstream import (
    GroupMember,
    preferred_value_for,
    resolve_role_to_field,
)
from tree_design.validation import (
    MaterialisedCandidate,
    MaterialisedLevel,
    ValidationReport,
)
from tree_design.vocabulary import ORDINARY, PROPOSED, SCOPE_TEMPLATE_LOCAL


class MaterialisationRefused(RuntimeError):
    """A branch cannot become nodes: its checks failed, or its inputs disagree."""


@dataclass(frozen=True)
class LevelEvidence:
    """One level, with the file sets `MaterialisedLevel` reduces to counts.

    `MaterialisedLevel.members_by_value` is `Mapping[str, int]` because V1-V6 ask
    "how many", never "which". The projection asks "which", because nesting is an
    intersection. Keeping both avoids widening Task 9's record for a question its
    checks do not ask.
    """

    dimension_role: str
    #: `None` on a template-local level. Contract W5 pairs the two: a level with
    #: no P6 field is one whose children came from accepted groups, and C2 is
    #: deliberately not run for it.
    field_ref: str | None
    order_index: int
    metadata_only: bool
    display_labels: Mapping[str, str]
    members_by_value: Mapping[str, frozenset[str]]
    handling_classes_by_value: Mapping[str, frozenset[str]]

    @property
    def values(self) -> tuple[str, ...]:
        return tuple(sorted(self.members_by_value))


@dataclass(frozen=True)
class BranchEvidence:
    branch_node_id: str
    levels: tuple[LevelEvidence, ...]
    member_file_ids: frozenset[str]
    unresolved_by_field: Mapping[str, frozenset[str]]


def materialise_branch(
    conn: sqlite3.Connection,
    candidate: CompositionCandidate,
    *,
    branch_node_id: str,
    members: Sequence[GroupMember],
    ancestor_field_refs: Sequence[str],
    ancestor_depth: int,
    handling_class_for_member: Callable[[GroupMember], str],
    metadata_only_roles: frozenset[str] = frozenset(),
    group_label_for_member: Callable[[GroupMember], tuple[str, str]] | None = None,
) -> tuple[MaterialisedCandidate, BranchEvidence]:
    """Populate one composition from the branch's own files.

    `handling_class_for_member` is injected rather than read here because P7's
    store is another part's record and `upstream.py` is the only module allowed
    to name it. The caller passes `upstream.handling_class_for` already bound to
    a `ClassificationStore`.

    `group_label_for_member` returns `(group_id, label)` for one file and is
    required only when the candidate carries a template-local level. Such a
    level has no P6 field, so its children come from the accepted P9 groups
    (§2.3, E4) rather than from fact values. It is injected for the same reason
    as the handling class: the accepted group is P9's record, and inventing a
    label here would be P10 authoring the user's vocabulary.
    """
    member_ids = frozenset(member.file_id for member in members)
    classes = {member.file_id: handling_class_for_member(member)
               for member in members}

    levels: list[LevelEvidence] = []
    unresolved: dict[str, frozenset[str]] = {}
    ordered = sorted(candidate.resolved_dimensions, key=lambda d: d.order_index)
    for dimension in ordered:
        local = dimension.scope == SCOPE_TEMPLATE_LOCAL
        if local and group_label_for_member is None:
            raise ConfigurationRequired(
                f"level {dimension.role_ref!r} is template-local, so its children "
                "come from the branch's accepted groups; no reader for them was "
                "supplied and P10 invents no label"
            )
        if not local:
            # C2 again, at the point of USE. Task 7 resolves roles when it routes,
            # but a candidate reaching here with a field P6 does not define would
            # produce an empty level and a silently missing folder rather than a
            # refusal — and §3.12's "should not invent new fields automatically" is
            # exactly the rule a silent empty level breaks quietly. Fail closed.
            #
            # It is NOT run for a template-local level (Contract W5): that level
            # deliberately has no field, and asking P6 to define one would refuse
            # the whole novel-domain path at the gate meant to guard fact-backed
            # levels only.
            resolve_role_to_field(conn, role_ref=dimension.role_ref,
                                  field_ref=dimension.field_ref)
        by_value: dict[str, set[str]] = {}
        labels: dict[str, str] = {}
        classes_by_value: dict[str, set[str]] = {}
        missing: set[str] = set()
        for member in members:
            if local:
                # A group id is the child's identity and the group's own label is
                # its display name. Neither is a fact value, which is why no
                # `ExpectedValue` is written for this level (Contract W4.2-4.3).
                key, label = group_label_for_member(member)
                if not key:
                    missing.add(member.file_id)
                    continue
                by_value.setdefault(key, set()).add(member.file_id)
                labels.setdefault(key, label)
                classes_by_value.setdefault(key, set()).add(classes[member.file_id])
                continue
            settled = preferred_value_for(
                conn, file_id=member.file_id, field_ref=dimension.field_ref)
            if settled is None:
                missing.add(member.file_id)
                continue
            by_value.setdefault(settled.canonical_value, set()).add(member.file_id)
            labels.setdefault(settled.canonical_value, settled.display_label)
            classes_by_value.setdefault(settled.canonical_value, set()).add(
                classes[member.file_id])
        unresolved[dimension.field_ref or dimension.role_ref] = frozenset(missing)
        levels.append(LevelEvidence(
            dimension_role=dimension.role_ref,
            field_ref=dimension.field_ref,
            order_index=dimension.order_index,
            metadata_only=dimension.role_ref in metadata_only_roles,
            display_labels=dict(labels),
            members_by_value={value: frozenset(files)
                              for value, files in by_value.items()},
            handling_classes_by_value={value: frozenset(found)
                                       for value, found in classes_by_value.items()},
        ))

    evidence = BranchEvidence(
        branch_node_id=branch_node_id, levels=tuple(levels),
        member_file_ids=member_ids, unresolved_by_field=dict(unresolved))
    return _for_validation(evidence, ancestor_field_refs, ancestor_depth), evidence


def _for_validation(evidence: BranchEvidence,
                    ancestor_field_refs: Sequence[str],
                    ancestor_depth: int) -> MaterialisedCandidate:
    """The same pass, in the shape V1-V6 read."""
    return MaterialisedCandidate(
        branch_node_id=evidence.branch_node_id,
        ancestor_field_refs=tuple(ancestor_field_refs),
        ancestor_depth=ancestor_depth,
        member_file_ids=evidence.member_file_ids,
        levels=tuple(
            MaterialisedLevel(
                dimension_role=level.dimension_role,
                field_ref=level.field_ref,
                order_index=level.order_index,
                metadata_only=level.metadata_only,
                values=level.values,
                members_by_value={value: len(files)
                                  for value, files in level.members_by_value.items()},
                handling_classes_by_value=dict(level.handling_classes_by_value),
            )
            for level in evidence.levels),
    )


def child_counts(evidence: BranchEvidence) -> Mapping[str, int]:
    """§5.5: "The user sees the actual branch counts before committing."

    One entry per level, holding the number of DISTINCT values that level would
    produce. This is the number the canvas states before an option is chosen.

    Keyed `field_ref or dimension_role`, the same pairing `unresolved_by_field`
    uses. A template-local level HAS no field, so keying on `field_ref` alone put
    every such level under one `None` key and the second silently overwrote the
    first — and two template-local levels are legal, which is why V1 exists to
    tell them apart from a repeated role. The user would then read one count for
    two levels.
    """
    return {level.field_ref or level.dimension_role: len(level.members_by_value)
            for level in evidence.levels if not level.metadata_only}


def project_branch_nodes(
    evidence: BranchEvidence,
    report: ValidationReport,
    *,
    parent: Node,
    plan_version_id: str,
    mint_node_id: Callable[[], str],
    handling_class_for: Callable[[frozenset[str]], str] | None,
    template_context_for: Callable[[str, int], object | None],
    protected_movement_permitted: bool = False,
) -> tuple[Node, ...]:
    """Turn a validated, populated branch into `Node` records.

    Nesting is by shared files. A value becomes a child of a parent value only
    when the same files carry both, which is what keeps the tree the size of the
    evidence rather than the size of the product of its dimensions.

    `handling_class_for` collapses the classes present under one value into the
    node's single class. It is injected with NO default: P7 publishes
    `HANDLING_CLASSES` as a set, not as an ordering, and a rank invented here
    could give a branch a weaker floor than one of its own files requires. This
    is the same treatment `privacy_rank` gets in Task 7.
    """
    if not report.accepted:
        raise MaterialisationRefused(
            f"branch {evidence.branch_node_id!r} failed "
            f"{', '.join(failure.check for failure in report.failures)}; §5.7's "
            "checks gate the build, not only the preview")
    if handling_class_for is None:
        raise ConfigurationRequired(
            "the handling-class collapse for a branch node is injected "
            "configuration with no default: P7 owns the ordering of "
            "HANDLING_CLASSES and has published none, and a rank chosen here "
            "could give a node a weaker floor than one of its files requires")

    nodes: list[Node] = []
    _project(evidence, level_index=0, parent=parent,
             eligible=evidence.member_file_ids, chain=(),
             plan_version_id=plan_version_id, mint_node_id=mint_node_id,
             handling_class_for=handling_class_for,
             template_context_for=template_context_for,
             protected_movement_permitted=protected_movement_permitted,
             out=nodes)
    return tuple(nodes)


def _project(evidence, *, level_index, parent, eligible, chain, plan_version_id,
             mint_node_id, handling_class_for, template_context_for,
             protected_movement_permitted, out) -> None:
    if level_index >= len(evidence.levels):
        return
    level = evidence.levels[level_index]
    if level.metadata_only:
        # §5.4: a metadata-only dimension is measured and never becomes a folder.
        _project(evidence, level_index=level_index + 1, parent=parent,
                 eligible=eligible, chain=chain, plan_version_id=plan_version_id,
                 mint_node_id=mint_node_id, handling_class_for=handling_class_for,
                 template_context_for=template_context_for,
                 protected_movement_permitted=protected_movement_permitted, out=out)
        return

    ordinal = 0
    for value in level.values:
        members = level.members_by_value[value] & eligible
        if not members:
            continue
        node_id = mint_node_id()
        label = level.display_labels.get(value, value)
        # Contract W4.2-4.3: a template-local level writes NO expected value.
        # Its children are accepted group labels, which are not fact values, so
        # the node inherits only what its schema-field ancestors settled and its
        # own `dimension` stays null. Writing one here would assert a fact P6
        # never made, and P11 would then match files against it.
        expected = chain if level.field_ref is None else chain + (
            ExpectedValue(field=level.field_ref, value=value),)
        node = Node(
            node_id=node_id,
            plan_version_id=plan_version_id,
            node_type=PROPOSED,
            display_label=label,
            parent_node_id=parent.node_id,
            root_anchor=parent.root_anchor,
            ordinal=ordinal,
            associated_group_ids=parent.associated_group_ids,
            explanation=(
                f"{len(members)} of this branch's files record "
                f"{level.field_ref} = {label!r}. P6 settled that value; P10 "
                f"placed it under {parent.display_label!r} and composed nothing."),
            node_role=ORDINARY,
            accepts_placement=derive_accepts_placement(
                PROPOSED,
                protected_movement_permitted=protected_movement_permitted),
            handling_class=handling_class_for(level.handling_classes_by_value[value]),
            origin_node_id=node_id,
            template_context=template_context_for(level.field_ref, level.order_index),
            dimension_role=level.dimension_role,
            dimension=level.field_ref,
            expected_values=expected,
            protected_movement_permitted=protected_movement_permitted,
        )
        out.append(node)
        ordinal += 1
        _project(evidence, level_index=level_index + 1, parent=node,
                 eligible=members, chain=expected,
                 plan_version_id=plan_version_id, mint_node_id=mint_node_id,
                 handling_class_for=handling_class_for,
                 template_context_for=template_context_for,
                 protected_movement_permitted=protected_movement_permitted, out=out)
