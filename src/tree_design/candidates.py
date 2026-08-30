# src/tree_design/candidates.py
"""§5.1's horizontal pass and §5.3's vertical pass. Two passes, one rule.

The rule is that a candidate is DERIVED. It comes from an accepted group, an
active domain membership, an existing folder the scan found, or a label the user
typed. §5.1 wants labels that "reflect the user's vocabulary rather than a
universal corporate taxonomy", so this module ships no branch names at all — the
nine §5.1 lists are what a typical canvas "might include" and are illustrative.

The horizontal pass runs first and stays shallow and template-independent. The
composable-template design is explicit: "Top-level branches are derived before
template routing. A template cannot silently create a new high-level domain or
replace the user's vocabulary."
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from tree_design.config import ConfigurationRequired, TreeLimits
from tree_design.health import (
    sample_size,
    Warning_,
    branch_counts,
    parent_concepts_for,
    warnings_for,
)
from tree_design.materialise import (
    BranchEvidence,
    BranchPreview,
    child_counts,
    narrow_wide_date_levels,
)
from tree_design.provenance import branch_basis_key, suppressed_branch_basis_keys
from tree_design.routing import CompositionCandidate, RoutingReport
from tree_design.records import Node
from tree_design.upstream import AcceptedGroup, ExistingFolder, ProtectedArea
from tree_design.validation import ValidationReport
from tree_design.vocabulary import (
    ACCEPT,
    ORDINARY,
    PROTECTED,
    CREATE_MANUALLY,
    DEFER,
    DRAG_GROUP_INTO_BRANCH,
    IGNORE,
    MERGE,
    MOVE_UNDER_ROOT,
    RENAME,
)

#: The option that keeps the branch as it is. §5.3 lists it beside a complete
#: template and a fragment composition, so it is an answer and not a fallback.
NO_SPLIT: str = "no-split"
COMPLETE_TEMPLATE: str = "complete-template"
FRAGMENT_COMPOSITION: str = "fragment-composition"

#: P3's curation signal has three values, and only one of them is §5.10's "strong
#: expression of user intent". `undetermined` gets its own source so the canvas
#: can show the folder without claiming the user curated it.
_CURATED = "curated"

#: The two sources that mean "the person made this folder and the scan read it".
#: Named because `pipeline._top_level_node` has to tell an adopted folder from a
#: proposal to decide the node's TYPE, and a string literal repeated in two
#: modules is how the curated/undetermined split silently loses a member.
EXISTING_FOLDER: str = "existing-folder"
EXISTING_FOLDER_UNDETERMINED: str = "existing-folder-undetermined"
EXISTING_FOLDER_SOURCES: tuple[str, ...] = (
    EXISTING_FOLDER, EXISTING_FOLDER_UNDETERMINED)

_BRANCH_ACTIONS: tuple[str, ...] = (
    ACCEPT, RENAME, MERGE, MOVE_UNDER_ROOT, DEFER, CREATE_MANUALLY,
    DRAG_GROUP_INTO_BRANCH, IGNORE,
)


@dataclass(frozen=True)
class BranchCandidate:
    """§5.1 and §5.2's card, as data. No layout, no score."""

    subject_id: str
    display_label: str
    why_suggested: str
    supporting_file_count: int
    accepted_group_ids: tuple[str, ...]
    representative_group_labels: tuple[str, ...]
    resembling_existing_folders: tuple[str, ...]
    sensitive_content_present: bool
    source: str
    available_actions: tuple[str, ...]


@dataclass(frozen=True)
class ChildPreview:
    """One branch this option would create, and the files that would land in it.

    `label_chain` runs from the branch being split down to this child, so two
    children with the same label under different parents are distinguishable
    without exposing a node id that only exists for the duration of the preview.
    It is a chain of display labels and never a path (resolution B3).
    """

    label_chain: tuple[str, ...]
    dimension: str | None
    file_count: int


@dataclass(frozen=True)
class VerticalOption:
    option_id: str
    kind: str
    resulting_child_counts: Mapping[str, int]
    total_child_branches: int
    #: `00`:99's "example members" — a SAMPLE, which is what the word says. It
    #: was `members[:len(members)]`, a slice that truncates nothing written in
    #: the shape of a truncation, so every option carried its own copy of the
    #: branch's whole membership: at 20,000 files that is the corpus, once per
    #: option. `member_count` beside it is the whole number, so a shorter list
    #: hides nothing — the count the user reads is unchanged.
    example_members: tuple[str, ...]
    member_count: int
    unresolved_file_ids: tuple[str, ...]
    summary: str
    validation: ValidationReport | None
    #: `00`:99's "number of files under each child", which `resulting_child_counts`
    #: does not answer: that maps a role to how many BRANCHES it makes.
    children: tuple[ChildPreview, ...]
    #: Members of this branch whose handling class is protected. They ARE placed
    #: and ARE counted — marked, not removed — and P7's `may_move_automatically`
    #: is what stops them being moved. Named here so the interface can say the
    #: branch holds them, because a file that is neither placed nor mentioned has
    #: been silently omitted, which the standing rule forbids.
    protected_file_ids: tuple[str, ...]
    #: §5.9's four warnings and its flattening recommendation, computed against
    #: this option's own preview tree. `validation` is a different thing: those
    #: are §5.7's ENGINE checks, which decide whether an option may be built at
    #: all. These are advice to the user about a tree that is perfectly legal.
    warnings: tuple[Warning_, ...]


def _folder_label(directory_path: str) -> str:
    """The last segment, as a display label. Never the path."""
    cleaned = directory_path.rstrip("/\\")
    for separator in ("/", "\\"):
        if separator in cleaned:
            cleaned = cleaned.rsplit(separator, 1)[-1]
    return cleaned


def protected_area_nodes(
    areas: Sequence[ProtectedArea],
    *,
    plan_version_id: str,
    root_anchor: str,
    mint_node_id: Callable[[], str],
    handling_class_for: Callable[[ProtectedArea], str] | None,
) -> tuple[Node, ...]:
    """One `protected` node per area P3 marked. Present, counted, never opened.

    The product owner's standing rule, verbatim: "reports, apps and system files
    MUST NOT BE MOVED OR READ OR ANYTHING SYSTEM OR SENSITIVE IN THAT SENSE." A
    protected container is MARKED AND COUNTED, NEVER OPENED — present-but-
    untouched in the UI, with a reachable explanation, never silently omitted,
    and never described as "understood and found unimportant".

    `node_type=PROTECTED` existed in `NODE_TYPES` and `derive_accepts_placement`
    already returned `protected_movement_permitted` for it, but nothing in `src/`
    ever CONSTRUCTED one. The vocabulary, the deriver and the consistency guard
    were all correct and all unreachable, so a protected area was pruned by the
    scan and then appeared nowhere — silently omitted.

    **SCOPE BOUND — this builds nodes for P3's protected CONTAINERS and nothing
    else.** The caller's areas come from `upstream.protected_areas`, which filters
    on `RULE_PROTECTED_CONTAINER`: P3's apps-and-system-items decision. The
    hardcoded immovability below rests on THAT rule specifically, ratified
    2026-08-20 — "applications and system items are never read and never moved,
    and no policy, approval, or user gesture makes them movable". §8.4 does
    contemplate a user policy permitting movement for other protected material,
    and sensitive personal material is not the same thing as `Numbers.app`. A
    different protected class needs a different producer, not this one widened.

    There is deliberately NO `protected_movement_permitted` parameter. §8.4 lets
    a user policy permit moving protected material, but P3's rule is stronger and
    says so in its own docstring: applications and system items are never read and
    never moved, and "no policy, approval, or user gesture makes them movable". A
    keyword here would be that override. The flag stays False, which makes
    `derive_accepts_placement` return False, which the `Node` consistency guard
    then enforces — three independent mechanisms agreeing, none of them optional.
    """
    if handling_class_for is None:
        raise ConfigurationRequired(
            "the handling class for a protected area is injected configuration "
            "with no default: P7 owns HANDLING_CLASSES and has published no "
            "ordering, and a class chosen here could give a protected area a "
            "weaker floor than the material inside it requires"
        )
    nodes: list[Node] = []
    for ordinal, area in enumerate(areas):
        node_id = mint_node_id()
        nodes.append(Node(
            node_id=node_id,
            plan_version_id=plan_version_id,
            node_type=PROTECTED,
            display_label=area.display_label,
            parent_node_id=None,
            root_anchor=root_anchor,
            ordinal=ordinal,
            associated_group_ids=(),
            explanation=(
                f"{area.display_label} is a protected area. The scan marked and "
                "counted it and never opened it, so nothing inside it was read "
                "and nothing inside it will be moved. It is shown here so that "
                "it is accounted for rather than missing."
            ),
            node_role=ORDINARY,
            accepts_placement=False,
            handling_class=handling_class_for(area),
            origin_node_id=node_id,
            existing_path=None,
        ))
    return tuple(nodes)


def horizontal_candidates(
    conn: sqlite3.Connection,
    *,
    accepted: Sequence[AcceptedGroup],
    existing_folders: Sequence[ExistingFolder],
    user_labels: Sequence[str],
    active_domains: Sequence[str],
    sensitive_group_ids: frozenset[str],
) -> tuple[BranchCandidate, ...]:
    """A small candidate set of top-level branches, each with its evidence.

    The learning query runs first. §8.7: "Rejected groups, rejected destination
    matches, rejected labels, and rejected residual recommendations must be
    stored with the evidence that produced them. Otherwise the system will
    repeatedly resurface the same attractive but incorrect grouping."

    That rejection is the ONLY thing that removes an accepted group from this
    surface. `active_domains` is evidence about the corpus, not a verdict on a
    group: a group whose domain did not activate still appears, and its card
    says so. Every other outcome is a silent omission, which the standing rule
    forbids and which cost the professional half of a multi-life disk its entire
    presence on the canvas.
    """
    suppressed = suppressed_branch_basis_keys(conn, parent_node_id=None)
    candidates: list[BranchCandidate] = []

    def suppressed_label(label: str) -> bool:
        return branch_basis_key(
            parent_node_id=None, dimension_or_label=label) in suppressed

    # Keyed by PATH, which is unique, and not by the last path segment, which is
    # not. A person with `Uni/PHYS1401` and `Physics/PHYS1401` -- two real
    # folders, in two places, holding different files -- had one of them
    # overwritten in this dict and dropped with nothing recording it anywhere,
    # which is the one outcome the owner's standing rule forbids without
    # exception. The label is still what the CARD shows; it was never a
    # workable identity.
    folders_by_path = {
        folder.directory_path: folder for folder in existing_folders
    }

    for group in accepted:
        if suppressed_label(group.label):
            continue
        # A group whose domain did not activate on this corpus USED TO BE
        # DROPPED HERE, silently and with no record anywhere. That is the one
        # outcome the owner's standing rule forbids without exception: material
        # is never silently omitted. It is also how a multi-life person loses a
        # whole life — P9 categorises their matters `law_practice`, activation
        # does not name that schema, and every matter they own disappears from
        # the canvas with nothing to click and nothing to read.
        #
        # §4.9 and §8.7 already say what a proposal the user does NOT want looks
        # like: a rejected label, recorded with its evidence, which
        # `suppressed_label` above honours. An inactive domain is not that. So
        # the group is still offered and the card says what the engine found.
        inactive = group.domain is not None and group.domain not in active_domains
        resembling = tuple(
            path for path, folder in folders_by_path.items()
            if _folder_label(path).lower() in group.label.lower()
            or group.label.lower() in _folder_label(path).lower()
        )
        sensitive = group.group_id in sensitive_group_ids
        detail = (
            f"{len(group.members)} file(s) in the accepted group "
            f"{group.label!r} share validated facts"
        )
        if group.domain:
            detail += f" in the {group.domain} schema"
        if inactive:
            detail += (
                "; that schema did not activate on this corpus, so no recipe "
                "will offer a structure for it and it is shown as it is rather "
                "than left out")
        if sensitive:
            detail += "; this area holds sensitive material and is shown without filenames"
        candidates.append(BranchCandidate(
            subject_id=group.group_id,
            display_label=group.label,
            why_suggested=detail + ".",
            supporting_file_count=len(group.members),
            accepted_group_ids=(group.group_id,),
            representative_group_labels=(group.label,),
            resembling_existing_folders=resembling,
            sensitive_content_present=sensitive,
            source="accepted-group",
            available_actions=_BRANCH_ACTIONS,
        ))

    for path, folder in folders_by_path.items():
        label = _folder_label(path)
        if suppressed_label(label):
            continue
        curated = folder.curation_signal == _CURATED
        candidates.append(BranchCandidate(
            subject_id=folder.directory_path,
            display_label=label,
            why_suggested=(
                f"An existing folder holding {folder.file_count} file(s). "
                + ("The scan reads it as curated, which is a strong expression of "
                   "your intent."
                   if curated else
                   "The scan could not tell whether it is curated or incidental, "
                   "so it is shown as it is and nothing is assumed.")
            ),
            supporting_file_count=folder.file_count,
            accepted_group_ids=(),
            representative_group_labels=(),
            resembling_existing_folders=(folder.directory_path,),
            sensitive_content_present=False,
            source=EXISTING_FOLDER if curated else EXISTING_FOLDER_UNDETERMINED,
            available_actions=_BRANCH_ACTIONS,
        ))

    for label in user_labels:
        if suppressed_label(label):
            continue
        candidates.append(BranchCandidate(
            subject_id=f"user-label:{label}",
            display_label=label,
            why_suggested="You created this branch by name.",
            supporting_file_count=0,
            accepted_group_ids=(),
            representative_group_labels=(),
            resembling_existing_folders=(),
            sensitive_content_present=False,
            source="user-label",
            available_actions=_BRANCH_ACTIONS,
        ))

    return tuple(candidates)


def _summarise(counts: Mapping[str, int]) -> str:
    """§5.5's whole-option sentence: "three schools, five terms, twelve courses".

    A level producing NO folders is left out, not reported as zero. It read "0
    school, 1 term, 3 subject, and 0 work_type" on a real run: `_project` skips a
    level with no values and V2 skips one that does not divide, so the sentence
    named four levels where the tree has two. This is the sentence a person reads
    before choosing a shape, and it must not offer folders the shape will not
    build.
    """
    parts = [f"{count} {role}" for role, count in counts.items() if count]
    if not parts:
        return "no child branches"
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def _child_previews(preview: BranchPreview) -> tuple[ChildPreview, ...]:
    """Each projected node as a label chain and a file count."""
    by_id = {node.node_id: node for node in preview.tree}
    previews: list[ChildPreview] = []
    for node in preview.nodes:
        chain: list[str] = [node.display_label]
        current = by_id.get(node.parent_node_id) if node.parent_node_id else None
        while current is not None:
            chain.append(current.display_label)
            current = (by_id.get(current.parent_node_id)
                       if current.parent_node_id else None)
        previews.append(ChildPreview(
            label_chain=tuple(reversed(chain)),
            dimension=node.dimension,
            file_count=len(preview.members_by_node.get(node.node_id, ())),
        ))
    return tuple(previews)


def _counts_for_preview(preview: BranchPreview,
                        evidence: BranchEvidence) -> dict[str, object]:
    """§5.5's counts for every node this option would create.

    Three of `branch_counts`'s inputs used to be hard-wired empty here, which
    made three of its fields unreachable: no node could ever report an
    unresolved file, an evidence gap, or sensitive material. `00`:99 requires the
    picker to show "example members, unresolved files, and any evidence gaps",
    so two of those three were structurally impossible.

    `evidence_gaps_by_node` STAYS empty and that is reported rather than filled:
    nothing in `src/` produces an evidence gap. `BranchCounts.evidence_gap_file_ids`
    is a reserved name with no producer, and inventing one here would be P10
    deciding what counts as a gap.
    """
    tree = preview.tree
    placed: frozenset[str] = frozenset().union(
        *(preview.members_by_node.get(node.node_id, frozenset())
          for node in preview.nodes)) if preview.nodes else frozenset()
    # A file that reaches no folder belongs to the BRANCH being split, which is
    # where the user is looking when they read the number.
    unresolved = tuple(sorted(evidence.member_file_ids - placed))
    sensitive = frozenset(
        node_id for node_id, files in preview.members_by_node.items()
        if files & evidence.protected_file_ids)
    return {
        node.node_id: branch_counts(
            tree, node_id=node.node_id,
            members_by_node={
                node.node_id: sorted(
                    preview.members_by_node.get(node.node_id, ()))},
            unresolved_by_node={preview.parent.node_id: unresolved},
            evidence_gaps_by_node={},
            sensitive_node_ids=sensitive)
        for node in tree
    }


def _unplaced(preview: BranchPreview, evidence: BranchEvidence) -> frozenset[str]:
    placed: frozenset[str] = frozenset().union(
        *(preview.members_by_node.get(node.node_id, frozenset())
          for node in preview.nodes)) if preview.nodes else frozenset()
    return evidence.member_file_ids - placed


def _preview_warnings(preview: BranchPreview, evidence: BranchEvidence,
                      limits: TreeLimits) -> tuple[Warning_, ...]:
    """§5.9, computed on the tree this option WOULD build.

    `00`:99 puts this before the choice — "Before the user chooses a split ... It
    should warn when a level produces only one child, repeats a concept already
    expressed in the parent, creates excessive depth, or creates a large number
    of tiny folders. It should recommend flattening when a dimension does not
    materially improve retrieval."

    `health.warnings_for` is the one implementation of those five and stays the
    one implementation: this hands it the preview tree rather than restating the
    rules against level evidence, because a second copy of §5.9 is a second copy
    that drifts.
    """
    tree = preview.tree
    return warnings_for(tree, _counts_for_preview(preview, evidence),
                        limits=limits, parent_concepts=parent_concepts_for(tree))


def vertical_options(
    report: RoutingReport,
    *,
    branch_members: Sequence[str],
    materialise: Callable[[CompositionCandidate], BranchEvidence | None],
    validate: Callable[[object], ValidationReport | None],
    limits: TreeLimits,
    preview: Callable[[CompositionCandidate, BranchEvidence], BranchPreview],
) -> tuple[VerticalOption, ...]:
    """One option per routed candidate, plus no-split, always last and always there.

    Each option states what it WOULD create from the branch's actual facts, which
    files it leaves unresolved, how many files would sit under each child, every
    §5.9 warning it triggers, and whether it passed V1-V6. An option that failed
    validation stays visible with its reason: §8.6 requires showing the
    difference between completed work and deferred work, and a silently dropped
    option looks to the user like the product having no idea.

    `limits` and `preview` are MANDATORY, and that is the point. §5.9's warnings
    were computed by a function no production code called, so the safety net that
    stops this product proposing a bad tree was not connected to the thing that
    proposes trees. An optional threshold set is an unwired one by the next
    caller who omits it.
    """
    members = tuple(branch_members)
    options: list[VerticalOption] = []

    for index, candidate in enumerate(report.candidates):
        evidence = materialise(candidate)
        # Before anything is previewed, counted or warned about: a date level
        # wide enough to be a folder per day is coarsened to the granularity
        # `00`:88's Photos template names. The preview, the counts and §5.9 all
        # read the SAME evidence afterwards, so no number the user sees can
        # disagree with the tree beside it.
        if evidence is not None:
            evidence = narrow_wide_date_levels(
                evidence, max_folders=limits.max_folder_proposals)
        built = None if evidence is None else preview(candidate, evidence)
        counts = {} if evidence is None else child_counts(evidence)
        children = () if built is None else _child_previews(built)
        protected = (() if evidence is None
                     else tuple(sorted(evidence.protected_file_ids)))
        warnings = (() if built is None
                    else _preview_warnings(built, evidence, limits))
        validation = validate(candidate)
        # Two ways a file gets no folder from this option: the routing never
        # covered it (C6), or it covered it and no level settled a value for it.
        # Both are "unresolved" to the user, and only the first was reported.
        unplaced = frozenset() if built is None else _unplaced(built, evidence)
        unresolved = tuple(sorted(
            {file_id for file_id in members
             if file_id not in candidate.covered_file_ids} | unplaced))
        kind = (COMPLETE_TEMPLATE if len(candidate.applicability_refs) == 1
                else FRAGMENT_COMPOSITION)
        summary = f"This option would create {_summarise(counts)}."
        if unresolved:
            summary += (
                f" {len(unresolved)} file(s) would stay unresolved and visible.")
        if validation is not None and validation.failures:
            failed = ", ".join(
                f"{failure.check} ({failure.reason})"
                for failure in validation.failures)
            summary += f" It does not pass {failed}."
        options.append(VerticalOption(
            option_id=f"opt_{index}",
            kind=kind,
            resulting_child_counts=dict(counts),
            # Every branch this option would create, not the widest single
            # level's count. `00`:99 puts this number in front of the user
            # before they choose, so it has to count something they can see.
            total_child_branches=len(children),
            example_members=members[:sample_size(limits)],
            member_count=len(members),
            unresolved_file_ids=unresolved,
            summary=summary,
            validation=validation,
            children=children,
            protected_file_ids=protected,
            warnings=warnings,
        ))

    no_split_summary = (
        "Keep this branch as it is. Nothing moves and nothing is created."
    )
    if not report.candidates:
        no_split_summary = (
            "Keep this branch as it is: no applicable recipe resolved against "
            "this branch's evidence, and nothing is invented to fill the gap."
        )
    if report.deferred:
        no_split_summary += (
            f" {report.deferred} further option(s) were deferred by the proposal "
            "ceiling and are not judgements about your evidence."
        )
    options.append(VerticalOption(
        option_id="opt_no_split",
        kind=NO_SPLIT,
        resulting_child_counts={},
        total_child_branches=0,
        example_members=members[:sample_size(limits)],
        member_count=len(members),
        unresolved_file_ids=(),
        summary=no_split_summary,
        validation=None,
        children=(),
        protected_file_ids=(),
        warnings=(),
    ))
    return tuple(options)
