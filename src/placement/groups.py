"""§6.8's coherent group plan and §6.9's multi-home rule.

Group-level placement is first class, and the order is the point: §6.8 confirms
the shared parent from the group's anchors and purpose evidence FIRST, then
classifies members beneath it. A member classified before the parent has no shared
context to be classified against, and the result is several unrelated file moves
presented as a plan.

An outlier is excluded and explained, never forced in. P9 already flags it
(`Membership.outlier_flag`) and already holds the competing values
(`Membership.conflicts`), so P11 records what P9 found and routes the file rather
than re-deciding whether it belongs. A member P9 did NOT flag cannot be excluded
here: manufacturing one would publish "P9 flagged this" about a decision P9 never
made.

§6.9's hardest rule is stated as a prohibition and implemented as one: with no
shared branch there is NO argument to `resolve_multi_home` that returns one of the
competing institutions -- including the shared-branch argument itself, which is
the only remaining way to smuggle one out. Whether the answer is `abstain` or
`ask_user` is SPEC Open question 6 and stays open: the selector is injected, and
its absence refuses.

The other half of "never pick an institution" -- `00`:44's prohibition on
authorship or creator identity as a destination dimension -- is enforced upstream
and is deliberately NOT re-implemented here. P6's field catalogue marks
`authored_by`, `our_firm`, `instructor` and `people` `destination_eligible =
False`, and `placement/retrieval.py:74` filters on it, so no such fact reaches a
candidate node at all. A second check here would be a second opinion with no way
to be reconciled.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from grouping.acceptance import group_state_as_of
from grouping.store import memberships_for_group
from grouping.vocabulary import ACCEPTED, NOT_FLAGGED

from placement.store import subject_ref_of
from placement.vocabulary import (
    ABSTAIN, ASK_USER, FILE, NO_SHARED_BRANCH, OUTLIER_ROUTES, PLACE,
    ROUTED_TO_NODE, ROUTED_TO_REVIEW_QUEUE, check,
)

SHARED_BRANCH: str = "shared-branch"
PRIMARY_HOME: str = "primary-home"
REFERENCE_OR_ALIAS: str = "reference-or-alias"
MANDATORY_REVIEW: str = "mandatory-review"

#: §6.9's four: "a shared branch, a primary-home convention, a reference or alias
#: convention, or mandatory review". P10 records which one at freeze, and the
#: VALUES are P10's spelling -- hyphenated, like every other value in P10's node
#: vocabulary (`scoped-general`, `shared-material`, `review-only`). Underscored
#: here, `resolve_multi_home` would match none of them and every multi-home file
#: would fall through every branch with nothing raising.
SHARED_MATERIAL_POLICIES: tuple[str, ...] = (
    SHARED_BRANCH, PRIMARY_HOME, REFERENCE_OR_ALIAS, MANDATORY_REVIEW,
)

#: The three that resolve to one approved node when the tree offers one. Under
#: `mandatory-review` the tree deliberately offers none, which is the policy --
#: so a branch handed in under `mandatory-review` is ignored rather than placed.
_BRANCH_BEARING: frozenset[str] = frozenset(
    {SHARED_BRANCH, PRIMARY_HOME, REFERENCE_OR_ALIAS}
)


class SharedMaterialPolicyRequired(RuntimeError):
    """§6.9 requires the frozen tree to carry one. Absent means refuse."""


class AskOrAbstainSelectorRequired(RuntimeError):
    """SPEC Open question 6 is open; the design gives no selector and nor does P11."""


class InstitutionalDestinationRefused(ValueError):
    """One of the competing homes was offered as the shared one. Named, not taken."""


class GroupNotAcceptedInVersion(LookupError):
    """This plan version has not accepted this group. Not an error; a state."""


@dataclass(frozen=True)
class AcceptedGroup:
    """One P9 group as this plan version sees it. Read, never reconstructed."""

    group_id: str
    plan_version: str
    state: str
    memberships: tuple


def accepted_group_as_of(conn: sqlite3.Connection, *, group_id: str,
                         plan_version: str) -> AcceptedGroup:
    """P9's own read, asked as of P10's frozen plan version.

    `accepted` is NOT a field on `Group`: `grouping/vocabulary.py:31-32` says of
    `accepted` and `rejected` that they are "the two values `group_state_as_of`
    adds at read time. Never stored." Reading `Group.state` instead would answer
    `supported` in every version, and P11 would place a group nobody accepted.

    A version holding no opinion is not an empty result -- `group_state_as_of`
    falls back to the SHARED state (`acceptance.py:154-170`) -- so the fallback
    is refused explicitly here rather than read as consent, and the refusal names
    the state it saw so "this version said no" reads differently from "this
    version said nothing".
    """
    state = group_state_as_of(conn, group_id=group_id,
                              plan_version_id=plan_version)
    if state != ACCEPTED:
        raise GroupNotAcceptedInVersion(
            f"group {group_id!r} is {state!r} as of {plan_version!r}, not "
            f"{ACCEPTED!r}. §6.8 places ACCEPTED groups; a shared lifecycle "
            "state is what the group is, not what this version decided about it"
        )
    return AcceptedGroup(
        group_id=group_id, plan_version=plan_version, state=state,
        memberships=tuple(memberships_for_group(conn, group_id)),
    )


@dataclass(frozen=True)
class ExcludedOutlier:
    file_id: str
    conflicting_fact: str
    evidence_ref: str
    routed_to: str
    node_id: str | None

    def __post_init__(self) -> None:
        check(self.routed_to, OUTLIER_ROUTES, name="routed_to")
        if (self.node_id is None) is (self.routed_to == ROUTED_TO_NODE):
            raise ValueError(
                "an outlier routed to a node names it, and one sent to review "
                "names none; §6.8 requires the user to see where it went"
            )


@dataclass(frozen=True)
class GroupPlan:
    group_plan_id: str
    plan_version: str
    group_id: str
    shared_parent_node_id: str | None
    member_decisions: tuple
    excluded_outliers: tuple[ExcludedOutlier, ...]

    def __post_init__(self) -> None:
        if not self.member_decisions:
            raise ValueError(
                "a group plan with no member decisions is not a plan; §6.8 asks "
                "for one coherent presentation, not an empty one"
            )
        ids = {decision.group_plan_id for decision in self.member_decisions}
        if ids != {self.group_plan_id}:
            raise ValueError(
                "every member decision shares this plan's id; that shared id is "
                "what makes the review surface show one plan rather than several "
                "unrelated file moves"
            )
        placed = {decision.subject.file_id for decision in self.member_decisions
                  if decision.subject.kind == FILE}
        placed.update(file_id for decision in self.member_decisions
                      for file_id in decision.subject.member_file_ids)
        both = placed & {outlier.file_id for outlier in self.excluded_outliers}
        if both:
            raise ValueError(
                f"{sorted(both)} appear as members AND as excluded outliers of "
                "the same plan; one presentation cannot say a file was placed "
                "with the group and left out of it"
            )


def _require_policy(policy: object) -> str:
    if not isinstance(policy, str) or policy not in SHARED_MATERIAL_POLICIES:
        raise SharedMaterialPolicyRequired(
            f"§6.9: the frozen tree must include a policy for shared material and "
            f"{policy!r} is not one of {SHARED_MATERIAL_POLICIES}. Without one a "
            "transcript belonging to two packets has no rule, and the only "
            "remaining options are to guess or to stop."
        )
    return policy


def confirm_shared_parent(member_parents, *, policy) -> str | None:
    """§6.8 step one. One parent, or none, and never a majority vote.

    A majority would place the minority members somewhere their own evidence does
    not support, which is exactly the "moved because it resembles a folder"
    failure §6.12 prohibits.
    """
    _require_policy(policy)
    parents = {parent for parent in member_parents.values() if parent}
    return parents.pop() if len(parents) == 1 else None


def excluded_outlier_for(membership, *, routed_node_id: str | None) -> ExcludedOutlier:
    """P9's flag and P9's competing values, recorded rather than re-derived.

    An unflagged member is refused. `outlier_flag` is P9's answer to whether this
    file sits apart from the group, and building an exclusion for a member P9
    called `none` would publish a finding P9 never made -- under a
    `conflicting_fact` string that says P9 flagged it.
    """
    if membership.outlier_flag == NOT_FLAGGED:
        raise ValueError(
            f"P9 flagged {membership.file_id!r} as {NOT_FLAGGED!r}; §6.8 excludes "
            "the outliers P9 identified and P11 does not re-decide belonging"
        )
    conflict = membership.conflicts[0] if membership.conflicts else None
    return ExcludedOutlier(
        file_id=membership.file_id,
        conflicting_fact=(
            f"{conflict.kind} = {' | '.join(conflict.competing_values)}"
            if conflict
            else f"P9 flagged this file {membership.outlier_flag!r} with no "
                 "competing value recorded"
        ),
        evidence_ref=next(
            (support.observation_key for support in membership.support
             if support.observation_key), ""
        ),
        routed_to=ROUTED_TO_NODE if routed_node_id else ROUTED_TO_REVIEW_QUEUE,
        node_id=routed_node_id,
    )


def resolve_multi_home(*, candidate_node_ids, shared_material_policy: str,
                       shared_branch_node_id: str | None,
                       ask_or_abstain) -> tuple[str, object]:
    """§6.9. Returns (outcome, payload) and never one of the competing nodes.

    The payload is the shared branch's node id for a `place`, the competing ids
    for an `ask_user`, and `no_shared_branch` for an `abstain`. There is no branch
    of this function that returns a member of `candidate_node_ids`, which is how
    "never arbitrarily pick one institution" is enforced rather than asserted.
    """
    candidates = tuple(candidate_node_ids)
    # ONE membership check, not two. `_require_policy` already refuses anything
    # outside §6.9's four, so a `check(...)` call beside it would be unreachable:
    # deleting either one alone would leave the suite green and the other doing
    # all the work.
    _require_policy(shared_material_policy)
    if len(candidates) < 2:
        raise ValueError(
            f"§6.9 resolves material that belongs to two or more homes and "
            f"{candidates!r} names fewer; abstaining {NO_SHARED_BRANCH!r} over a "
            "file with one home would report a competition that never happened"
        )
    if shared_branch_node_id in candidates:
        raise InstitutionalDestinationRefused(
            f"{shared_branch_node_id!r} is one of the competing homes "
            f"{candidates!r}, so placing there IS choosing between them. §6.9's "
            "shared branch is a destination above the competition, not one side "
            "of it"
        )
    if shared_material_policy in _BRANCH_BEARING and shared_branch_node_id:
        return PLACE, shared_branch_node_id
    if ask_or_abstain is None:
        raise AskOrAbstainSelectorRequired(
            "with no shared branch §6.9 permits abstaining OR asking the user to "
            "choose a primary home, and gives no rule for which. SPEC Open "
            "question 6 is open; the selector is injected and never invented."
        )
    chosen = ask_or_abstain(candidates)
    if chosen == ASK_USER:
        return ASK_USER, candidates
    if chosen == ABSTAIN:
        return ABSTAIN, NO_SHARED_BRANCH
    raise AskOrAbstainSelectorRequired(
        f"the selector returned {chosen!r}; §6.9 permits exactly "
        f"{ASK_USER!r} and {ABSTAIN!r}, and a third answer would be a placement"
    )
