"""§8.8's diff and `66` §17's draft the user adopts. The presentation half.

P10 emits the node-level diff (`tree_design.diff.diff_versions`), P11 computes the
file-level consequence (`placement.versions.reproject`), and P13 renders BOTH --
§8.8's own examples being that Applications was renamed to Admissions, Research
moved under Projects, Reference Clips was added, the Academic template's dimension
order changed, and "twenty-three files now require renewed review because their
previous destination no longer exists."

**The two halves must agree.** If P11 names a removed node that P10's node diff
does not report as removed, the screen states a consequence with no visible cause:
twenty-three files needing review and nothing on the page saying which destination
went away. That is §8.8's sentence with its second half missing, and it is worse
than no diff at all because it looks complete. So the mismatch raises.

**Nothing here writes.** `66` §17: a changed structural answer "must not silently
rename folders, reclassify files, reveal protected records, or move anything as a
consequence of a changed answer." This module imports no writer, and a test
asserts that by parsing it rather than by trusting this paragraph.

**Nothing is adopted until the user adopts it.** `adopted` is False on every view
this module builds, because existing approved structure remains stable unless the
user explicitly adopts the new plan. Adoption is a collected `review_action`
routed to P10, which owns the record.

**A rename the user made and this release cannot honour is SURFACED, not
resolved.** `tree_design.user_edits.UnappliedUserEdit` is the shipped record for
exactly that -- "that is a question for the user, not a decision for the product"
-- and it is carried through verbatim, in P10's own vocabulary, so "what changed
when I updated" and "what changed when I edited" read the same way.

**Three of `66` §17's six diff dimensions have NO PRODUCER** anywhere in `src/`.
They are `None` with a note each, never invented and never quietly dropped.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass

from placement.versions import VersionDiff
from tree_design.diff import DIFF_REMOVED, NodeDiffEntry, diff_versions
from tree_design.user_edits import UnappliedUserEdit

from review_surface.collect import collect
from review_surface.records import ReviewAction
from review_surface.vocabulary import (
    ACTION_ADOPT_VERSION,
    ACTION_RESTORE_VERSION,
    SURFACE_PLAN_VERSION,
)

#: §8.8's three named user actions. `compare` is the view itself and is listed so
#: the three read together; the other two are P13 vocabulary members and are
#: collected as actions.
COMPARE: str = "compare"
THREE_VERSION_ACTIONS: tuple[str, ...] = (
    COMPARE, ACTION_RESTORE_VERSION, ACTION_ADOPT_VERSION)

#: One note per dimension `66` §17 asks for and no part produces. Each says what
#: was looked for and why the nearest live record is NOT it, so a later reader can
#: tell an unbuilt producer from an unnoticed one.
GAP_NOTES: tuple[str, ...] = (
    "`66` §17 asks which schemas become active or inactive. No part publishes a "
    "schema-activation delta: `user_edits.UserLevelEdit.uses_schema` names the "
    "schema an edit was made in, not a change in which schemas are active. "
    "Reported as absent rather than derived from something that does not mean it.",
    "`66` §17 asks whether any protected area changes. "
    "`tree_design.freeze.represent_protected_areas` builds protected nodes and "
    "nothing diffs them across versions. Reported as absent -- and inferring it "
    "from the node diff would risk revealing a protected record, which the same "
    "section forbids in the same sentence.",
    "`66` §17 asks whether any filing policy is paused. No part publishes a "
    "filing-policy record at all; automatic filing is a later item in the "
    "release order. Reported as absent rather than invented.",
)


class NothingIsAdoptedSilently(RuntimeError):
    """A version gesture that is not one of §8.8's three named user actions."""


class RemovedNodeMissingFromDiff(RuntimeError):
    """P11 named a removed node that P10's node diff does not report as removed."""


@dataclass(frozen=True)
class RenewedReviewStatement:
    """§8.8's own sentence, with the files it is about."""

    count: int
    subject_refs: tuple[str, ...]
    sentence: str


@dataclass(frozen=True)
class StructuralDiffView:
    """Six dimensions asked for, three produced, three named as absent."""

    before: str
    after: str
    node_entries: tuple[NodeDiffEntry, ...]
    renewed_review: RenewedReviewStatement
    removed_node_ids: tuple[str, ...]
    carried_unchanged: tuple[str, ...]
    unapplied_user_edits: tuple[UnappliedUserEdit, ...]
    schemas_activated_or_deactivated: None
    protected_area_changes: None
    filing_policies_paused: None
    producer_gap_notes: tuple[str, ...]
    available_actions: tuple[str, ...]
    adopted: bool


def structural_diff_view(conn: sqlite3.Connection, *, before: str, after: str,
                         version_diff: VersionDiff,
                         unapplied: Sequence[UnappliedUserEdit] = (),
                         ) -> StructuralDiffView:
    """Render P10's node diff and P11's file-level consequence. Adopt nothing.

    `version_diff` is passed rather than computed here, because
    `placement.versions.reproject` is a P11 call with its own revalidation inputs
    and P13 must not choose them. P13 renders the diff it was handed -- and checks
    that the two halves are talking about the same removals.
    """
    entries = diff_versions(conn, before=before, after=after)
    removed_in_tree = {entry.origin_node_id for entry in entries
                       if entry.kind == DIFF_REMOVED}
    removed_claimed = tuple(version_diff.removed_node_ids)
    unexplained = [node_id for node_id in removed_claimed
                   if node_id not in removed_in_tree]
    if unexplained:
        raise RemovedNodeMissingFromDiff(
            f"the file-level diff says {unexplained} were removed between "
            f"{before!r} and {after!r}, and the node-level diff reports no "
            "removal for them. Rendering this would state §8.8's consequence "
            "-- files needing renewed review because their destination no "
            "longer exists -- with nothing on the screen saying which "
            "destination went away")
    subjects = tuple(version_diff.requiring_renewed_review)
    return StructuralDiffView(
        before=before, after=after, node_entries=entries,
        renewed_review=RenewedReviewStatement(
            count=len(subjects), subject_refs=subjects,
            sentence=(
                f"{len(subjects)} file(s) now require renewed review because "
                "their previous destination no longer exists or changed. They "
                "are presented as requiring review and are not pre-accepted at "
                "their old destination: approvals do not carry across "
                "versions.")),
        removed_node_ids=removed_claimed,
        carried_unchanged=tuple(version_diff.carried_unchanged),
        unapplied_user_edits=tuple(unapplied),
        schemas_activated_or_deactivated=None,
        protected_area_changes=None,
        filing_policies_paused=None,
        producer_gap_notes=GAP_NOTES,
        available_actions=THREE_VERSION_ACTIONS,
        # Always False. Adoption is a user gesture routed to P10, and a view that
        # could report itself adopted would be a view that adopted something.
        adopted=False)


def collect_version_action(conn: sqlite3.Connection, view: StructuralDiffView,
                           action: str, *, action_id: str, plan_version: str,
                           session_id: str, correction_scope: str,
                           presented_state_ref: str, user_id: str,
                           acted_at: str,
                           component_version: str) -> ReviewAction:
    """Collect an adopt or a restore and route it to P10.

    `subject_ref` follows the action: adopting names the version being adopted,
    restoring names the version being restored to. Naming the same version for
    both would make the two gestures indistinguishable in the store, and P10's
    version actions branch on exactly that difference.
    """
    if action == ACTION_ADOPT_VERSION:
        subject_ref = view.after
    elif action == ACTION_RESTORE_VERSION:
        subject_ref = view.before
    else:
        raise NothingIsAdoptedSilently(
            f"{action!r} is not one of §8.8's three named user actions "
            f"{list(THREE_VERSION_ACTIONS)}. A plan version is compared, "
            "restored, or explicitly adopted; nothing else changes it")
    return collect(
        conn, action_id=action_id, surface=SURFACE_PLAN_VERSION,
        subject_ref=subject_ref, plan_version=plan_version,
        session_id=session_id, action=action,
        correction_scope=correction_scope,
        presented_state_ref=presented_state_ref, user_id=user_id,
        acted_at=acted_at, component_version=component_version,
        payload={"before": view.before, "after": view.after})
