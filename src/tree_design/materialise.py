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

import dataclasses
import re
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
    #: What this level is CALLED, in the words of the schema that bound it
    #: (Amendment A). Authored on `TemplateApplicability.role_bindings` and
    #: carried here by `ResolvedDimension.display_label`.
    #:
    #: It carries a default because `None` is a real value with a real meaning —
    #: "this level was composed without a binding, so nobody authored a name for
    #: it" — and `_label_of` answers for it. Every level the ROUTER builds has a
    #: label, because `RoleBinding.label` is required; a level built directly,
    #: as the suite's own fixtures do, has none.
    dimension_label: str | None = None

    @property
    def values(self) -> tuple[str, ...]:
        return tuple(sorted(self.members_by_value))


@dataclass(frozen=True)
class BranchEvidence:
    branch_node_id: str
    levels: tuple[LevelEvidence, ...]
    member_file_ids: frozenset[str]
    unresolved_by_field: Mapping[str, frozenset[str]]
    #: Members of this branch whose handling class is protected. They are IN
    #: `member_file_ids` and in every count — marked, not removed. `00`:101 asks
    #: tree health to show "where sensitive material has been isolated", and
    #: naming them is how the interface shows it. Removing them would be the
    #: silent omission the standing rule forbids.
    protected_file_ids: frozenset[str] = frozenset()


def materialise_branch(
    conn: sqlite3.Connection,
    candidate: CompositionCandidate,
    *,
    branch_node_id: str,
    members: Sequence[GroupMember],
    ancestor_field_refs: Sequence[str],
    ancestor_depth: int,
    handling_class_for_member: Callable[[GroupMember], str],
    protected_handling_classes: frozenset[str] | None,
    metadata_only_roles: frozenset[str] = frozenset(),
    group_label_for_member: Callable[[GroupMember], tuple[str, str]] | None = None,
) -> tuple[MaterialisedCandidate, BranchEvidence]:
    """Populate one composition from the branch's own files.

    `handling_class_for_member` is injected rather than read here because P7's
    store is another part's record and `upstream.py` is the only module allowed
    to name it. The caller passes `upstream.handling_class_for` already bound to
    a `ClassificationStore`.

    `protected_handling_classes` MARKS rather than removes, and the distinction
    is the whole point. The standing rule is that protected material is MARKED
    AND COUNTED, never opened, NEVER SILENTLY OMITTED — so a protected member
    stays a member, stays under its value, and stays in the counts the user
    reads. It is named in `protected_file_ids` so the interface can say "this
    branch holds one protected file and it will not be moved".

    Removing it would be the omission the rule forbids: a file dropped out of the
    evidence is uncounted, and uncounted is worse than present-but-untouched.

    The safety property does not depend on removal.
    `placement.privacy.automatic_move_permitted_for` delegates to P7's
    `may_move_automatically`, which refuses a protected file — and an
    unclassified one — unless an explicit policy permits it. P11 will not move
    it whether or not P10 counts it.

    What this ISN'T is a reason to refuse the branch. `handling_classes_by_value`
    is still the union of the members' classes, and V5 no longer reads it: one
    passport under `Columbia` used to give the STRING "Columbia" a protected
    class and refuse the whole composition, so the user lost the organisation and
    kept none of the protection.

    `group_label_for_member` returns `(group_id, label)` for one file and is
    required only when the candidate carries a template-local level. Such a
    level has no P6 field, so its children come from the accepted P9 groups
    (§2.3, E4) rather than from fact values. It is injected for the same reason
    as the handling class: the accepted group is P9's record, and inventing a
    label here would be P10 authoring the user's vocabulary.
    """
    if protected_handling_classes is None:
        raise ConfigurationRequired(
            "the set of handling classes that count as protected is injected "
            "configuration with no default: P7 owns HANDLING_CLASSES and has "
            "published no ordering, and a set chosen here would let P10 decide "
            "which of a user's material is isolated from the tree"
        )
    classes = {member.file_id: handling_class_for_member(member)
               for member in members}
    # Marked, NOT removed. These files stay members and stay counted; the name
    # is what lets the interface show them as present-but-not-movable.
    protected = frozenset(
        file_id for file_id, handling in classes.items()
        if handling in protected_handling_classes)
    member_ids = frozenset(member.file_id for member in members)

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
            dimension_label=dimension.display_label,
            display_labels=dict(labels),
            members_by_value={value: frozenset(files)
                              for value, files in by_value.items()},
            handling_classes_by_value={value: frozenset(found)
                                       for value, found in classes_by_value.items()},
        ))

    evidence = BranchEvidence(
        branch_node_id=branch_node_id, levels=tuple(levels),
        member_file_ids=member_ids, unresolved_by_field=dict(unresolved),
        protected_file_ids=protected)
    return _for_validation(evidence, ancestor_field_refs, ancestor_depth), evidence


def _label_of(level: LevelEvidence) -> str:
    """What to call this level in the sentence a user reads (Amendment A).

    The authored per-schema name when a binding supplied one; otherwise the P6
    field key, which is what every node said before the amendment and is still
    the honest answer for a level composed without a binding.

    The last fallback is the ROLE, not the null. A template-local level has no
    field by construction (Contract W5), so `field_ref or ...` alone would put
    the four characters `None` into every one of those nodes' explanations —
    §5.12 asks each node to state what caused it to appear, and "record None =
    'Physics Homework'" states nothing.
    """
    return level.dimension_label or level.field_ref or level.dimension_role


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

    return project_branch_preview(
        evidence, report, parent=parent, plan_version_id=plan_version_id,
        mint_node_id=mint_node_id, handling_class_for=handling_class_for,
        template_context_for=template_context_for,
        protected_movement_permitted=protected_movement_permitted).nodes


@dataclass(frozen=True)
class BranchPreview:
    """The tree one option WOULD create, with the files that would sit in it.

    `00`:99 asks the interface to show, BEFORE the user chooses a split, "the
    resulting number of child branches, THE NUMBER OF FILES UNDER EACH CHILD,
    example members, unresolved files, and any evidence gaps", and to warn on the
    §5.9 conditions. `members_by_node` is the files-per-child half: without it
    `WARN_TINY_FOLDERS` cannot be computed at all, because `child_counts` answers
    how many BRANCHES a level makes and never how many FILES are under each.

    `parent` is kept apart from `nodes` on purpose. `nodes` is exactly what would
    be written, which is what `project_branch_nodes` returns and what the store
    persists; `tree` adds the branch being split, which is what §5.9 has to read
    — a level that produces one child is a fact about the PARENT, and a preview
    that omitted it could never fire `WARN_ONE_CHILD` on the first level.
    """

    parent: Node
    nodes: tuple[Node, ...]
    members_by_node: Mapping[str, frozenset[str]]

    @property
    def tree(self) -> tuple[Node, ...]:
        return (self.parent, *self.nodes)


def project_branch_preview(
    evidence: BranchEvidence,
    report: ValidationReport,
    *,
    parent: Node,
    plan_version_id: str,
    mint_node_id: Callable[[], str],
    handling_class_for: Callable[[frozenset[str]], str] | None,
    template_context_for: Callable[[str, int], object | None],
    protected_movement_permitted: bool = False,
) -> BranchPreview:
    """`project_branch_nodes`, plus the member set behind each node.

    One traversal, one nesting rule. The member sets are recorded where they are
    already computed rather than recovered afterwards, so the preview's counts
    cannot disagree with the tree the projection would actually build.
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
    members: dict[str, frozenset[str]] = {}
    _project(evidence, level_index=0, parent=parent,
             eligible=evidence.member_file_ids, chain=(),
             plan_version_id=plan_version_id, mint_node_id=mint_node_id,
             handling_class_for=handling_class_for,
             template_context_for=template_context_for,
             protected_movement_permitted=protected_movement_permitted,
             out=nodes, members_out=members)
    return BranchPreview(
        parent=parent, nodes=tuple(nodes),
        members_by_node={parent.node_id: evidence.member_file_ids, **members})


def _project(evidence, *, level_index, parent, eligible, chain, plan_version_id,
             mint_node_id, handling_class_for, template_context_for,
             protected_movement_permitted, out, members_out) -> None:
    if level_index >= len(evidence.levels):
        return
    level = evidence.levels[level_index]
    if level.metadata_only:
        # §5.4: a metadata-only dimension is measured and never becomes a folder.
        _project(evidence, level_index=level_index + 1, parent=parent,
                 eligible=eligible, chain=chain, plan_version_id=plan_version_id,
                 mint_node_id=mint_node_id, handling_class_for=handling_class_for,
                 template_context_for=template_context_for,
                 protected_movement_permitted=protected_movement_permitted,
                 out=out, members_out=members_out)
        return

    ordinal = 0
    for value in level.values:
        members = level.members_by_value[value] & eligible
        if not members:
            continue
        if members <= evidence.protected_file_ids:
            # MARKED, COUNTED, NEVER OPENED -- and never SPOKEN. A folder name is
            # public: visible in the filesystem and in every prompt that names a
            # destination. A name carried by NOTHING BUT protected material
            # publishes that material, and `X12345678`, a client's passport
            # number, was a proposed folder on a real corpus.
            #
            # This does not remove the file and does not uncount it. Its members
            # stay in `eligible`, so they stay under this parent, stay in its
            # counts, and stay in `protected_file_ids` for §5.9 to report -- the
            # standing rule's "never silently omitted" is about the FILE, and the
            # file is still here. What it loses is a NAME of its own.
            #
            # Neither existing lever could do this. `protected_handling_classes`
            # marks rather than removes on purpose -- "uncounted is worse than
            # present-but-untouched" -- and V5 refuses the WHOLE composition,
            # which is the failure its own docstring records: "the user lost the
            # organisation and kept none of the protection".
            #
            # `<=`, not `&`: a value ANY ordinary file also carries is untouched,
            # because then the name is not derived from protected material. A
            # matter number shared with four ordinary documents stays a folder;
            # a passport number that appears nowhere else does not.
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
                f"{_label_of(level)} = {label!r}. P6 settled that value; P10 "
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
        members_out[node_id] = members
        ordinal += 1
        _project(evidence, level_index=level_index + 1, parent=node,
                 eligible=members, chain=expected,
                 plan_version_id=plan_version_id, mint_node_id=mint_node_id,
                 handling_class_for=handling_class_for,
                 template_context_for=template_context_for,
                 protected_movement_permitted=protected_movement_permitted,
                 out=out, members_out=members_out)

    if ordinal == 0:
        # This level said NOTHING about these files -- either it settled no value
        # at all, or none of its values reach this parent's members. Skip it, the
        # way `metadata_only` above is skipped, and let the next level try.
        #
        # It used to fall off the end of the function here, which took every level
        # BENEATH it down as well: the loop was the only thing that recursed, so a
        # level with nothing to say silently truncated the branch. That is the
        # product discarding knowledge it HAS because of knowledge it LACKS --
        # `ap.academic.coursework` resolves school, term, subject, work_type in
        # that order, and a person whose files state a course code and nothing
        # else answers only the third, so their tree came back one folder deep
        # with `PHYS1401` sitting in the evidence unused.
        #
        # `00`:51 is why skipping is the reading that matches the design: the same
        # facts may be organised `Academics/Columbia/2026-Spring/BUSIB 4300` or
        # `Academics/BUSIB 4300/Spring 2026`. The ORDER of levels is not rigid, so
        # a hole in it is a hole and not a floor.
        #
        # Nesting is still by shared files and no level is invented: the children
        # that appear are exactly the ones a later level's own values produce, and
        # they hang off the nearest ancestor that settled something.
        _project(evidence, level_index=level_index + 1, parent=parent,
                 eligible=eligible, chain=chain,
                 plan_version_id=plan_version_id, mint_node_id=mint_node_id,
                 handling_class_for=handling_class_for,
                 template_context_for=template_context_for,
                 protected_movement_permitted=protected_movement_permitted,
                 out=out, members_out=members_out)


#: A value that is a whole calendar day, and a value that is a whole month. Both
#: are matched WHOLE and strictly: `2026-Spring` is a term and not a month, and a
#: level of terms must not be read as a level of dates.
_DAY = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_MONTH = re.compile(r"^(\d{4})-(\d{2})$")

#: day -> month -> year. Each step is a PREFIX of the value the fact already
#: carries, so no label is invented: `2026-03-14` really does record 2026.
#: Each step drops the last hyphen-separated component, which is a PREFIX of the
#: value the fact already carries: `2026-03-14` really does record `2026-03`, and
#: `2026-03` really does record `2026`. No label is invented and no file moves
#: out of the branch — it lands in a coarser folder, which is the only narrowing
#: that costs the user nothing.
_COARSER: tuple[tuple[object, object], ...] = (
    (_DAY, lambda value: value.rsplit("-", 1)[0]),
    (_MONTH, lambda value: value.rsplit("-", 1)[0]),
)


def _coarsen(level: LevelEvidence, key_of) -> LevelEvidence:
    members: dict[str, frozenset[str]] = {}
    classes: dict[str, frozenset[str]] = {}
    for value, files in level.members_by_value.items():
        key = key_of(value)
        members[key] = members.get(key, frozenset()) | files
        classes[key] = (classes.get(key, frozenset())
                        | level.handling_classes_by_value.get(value, frozenset()))
    return dataclasses.replace(
        level,
        display_labels={key: key for key in members},
        members_by_value=members,
        handling_classes_by_value=classes,
    )


def narrow_wide_date_levels(
    evidence: BranchEvidence, *, max_folders: int,
) -> BranchEvidence:
    """Coarsen a date level that would otherwise propose a folder per day.

    NOTHING BOUNDED HOW WIDE A SPLIT WAS. §8.6's ceiling is called "Maximum
    folder proposals and maximum depth"; P10 read it as how many OPTIONS to offer
    and how DEEP one may go, and never as how many FOLDERS a proposal creates —
    which is the reading its own words most plainly carry. A capture-date split
    on a real photo library proposed 337 folders with that ceiling set to six,
    and `00`:88 recommends exactly that split: "Photos and capture-based media
    are the major exception: time often belongs first."

    A CEILING IS THE WRONG INSTRUMENT ANYWAY, and this is why only dates are
    touched. Capping a level of 400 courses at 100 folders means either dropping
    300 courses, which is the silent omission the standing rule forbids, or
    merging them by something the evidence never said, which is invention. There
    is no third option for values with no structure, so a level of opaque values
    passes through at whatever width its evidence produced. A DATE has structure
    the fact already carries: `00`:88's own Photos template "may define year →
    event", and every file keeps a folder — a coarser one, named by a prefix of
    the value P6 settled, with nothing dropped and nothing invented.
    """
    if max_folders < 1:
        return evidence
    levels = []
    changed = False
    for level in evidence.levels:
        current = level
        for pattern, key_of in _COARSER:
            values = tuple(current.members_by_value)
            if len(values) <= max_folders:
                break
            if not values or not all(pattern.match(value) for value in values):
                continue
            coarser = _coarsen(current, key_of)
            if len(coarser.members_by_value) < len(current.members_by_value):
                current = coarser
                changed = True
        levels.append(current)
    if not changed:
        return evidence
    return dataclasses.replace(evidence, levels=tuple(levels))
