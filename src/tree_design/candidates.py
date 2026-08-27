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

from tree_design.provenance import branch_basis_key, suppressed_branch_basis_keys
from tree_design.routing import CompositionCandidate, RoutingReport
from tree_design.upstream import AcceptedGroup, ExistingFolder
from tree_design.validation import ValidationReport
from tree_design.vocabulary import (
    ACCEPT,
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
class VerticalOption:
    option_id: str
    kind: str
    resulting_child_counts: Mapping[str, int]
    total_child_branches: int
    example_members: tuple[str, ...]
    unresolved_file_ids: tuple[str, ...]
    summary: str
    validation: ValidationReport | None


def _folder_label(directory_path: str) -> str:
    """The last segment, as a display label. Never the path."""
    cleaned = directory_path.rstrip("/\\")
    for separator in ("/", "\\"):
        if separator in cleaned:
            cleaned = cleaned.rsplit(separator, 1)[-1]
    return cleaned


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
    """
    suppressed = suppressed_branch_basis_keys(conn, parent_node_id=None)
    candidates: list[BranchCandidate] = []

    def suppressed_label(label: str) -> bool:
        return branch_basis_key(
            parent_node_id=None, dimension_or_label=label) in suppressed

    folders_by_label = {
        _folder_label(folder.directory_path): folder for folder in existing_folders
    }

    for group in accepted:
        if group.domain is not None and group.domain not in active_domains:
            continue
        if suppressed_label(group.label):
            continue
        resembling = tuple(
            folder.directory_path for label, folder in folders_by_label.items()
            if label.lower() in group.label.lower()
            or group.label.lower() in label.lower()
        )
        sensitive = group.group_id in sensitive_group_ids
        detail = (
            f"{len(group.members)} file(s) in the accepted group "
            f"{group.label!r} share validated facts"
        )
        if group.domain:
            detail += f" in the {group.domain} schema"
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

    for label, folder in folders_by_label.items():
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
            source="existing-folder" if curated else "existing-folder-undetermined",
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
    """§5.5's whole-option sentence: "three schools, five terms, twelve courses"."""
    parts = [f"{count} {role}" for role, count in counts.items()]
    if not parts:
        return "no child branches"
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def vertical_options(
    report: RoutingReport,
    *,
    branch_members: Sequence[str],
    materialise: Callable[[CompositionCandidate], Mapping[str, int] | None],
    validate: Callable[[object], ValidationReport | None],
) -> tuple[VerticalOption, ...]:
    """One option per routed candidate, plus no-split, always last and always there.

    Each option states what it WOULD create from the branch's actual facts, which
    files it leaves unresolved, and whether it passed V1-V6. An option that failed
    validation stays visible with its reason: §8.6 requires showing the
    difference between completed work and deferred work, and a silently dropped
    option looks to the user like the product having no idea.
    """
    members = tuple(branch_members)
    options: list[VerticalOption] = []

    for index, candidate in enumerate(report.candidates):
        counts = materialise(candidate) or {}
        validation = validate(candidate)
        unresolved = tuple(
            file_id for file_id in members
            if file_id not in candidate.covered_file_ids
        )
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
            total_child_branches=max(counts.values()) if counts else 0,
            example_members=members[:len(members)],
            unresolved_file_ids=unresolved,
            summary=summary,
            validation=validation,
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
        example_members=members,
        unresolved_file_ids=(),
        summary=no_split_summary,
        validation=None,
    ))
    return tuple(options)
