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

from database_agent.files_table import (
    PATH_NO_LONGER_EXISTS, SUPERSEDED_CONTENT, get_file,
)
from grouping.acceptance import group_state_as_of
from grouping.store import current_group, memberships_for_group
from grouping.vocabulary import ACCEPTED, EXCLUDED, NOT_FLAGGED

from tree_design.vocabulary import (
    BRANCH_BEARING_SHARED_POLICIES, MANDATORY_REVIEW, PRIMARY_HOME,
    REFERENCE_OR_ALIAS, SHARED_BRANCH, SHARED_MATERIAL_POLICIES,
)

from placement.store import subject_ref_of
from placement.vocabulary import (
    ABSTAIN, ASK_USER, FILE, NO_SHARED_BRANCH, OUTLIER_ROUTES, PLACE,
    ROUTED_TO_NODE, ROUTED_TO_REVIEW_QUEUE, check,
)

#: §6.9's four policies and the three of them that bear a branch, both CARRIED
#: from P10 and neither defined here. MINOR 6: "P10 owns the tree, so P10 names
#: its node kinds. P11 carries these verbatim and publishes no parallel
#: vocabulary." Until P10 shipped there was nowhere to carry them from and this
#: module spelled its own; two spellings of one closed set is how two parts
#: silently disagree, and THIS set decides whether a file belonging to two places
#: gets a home or gets asked about.
#:
#: `BRANCH_BEARING_SHARED_POLICIES` is P10's by ownership and P10's by authorship:
#: P10 needed the set at its own call site, found this module already computing it
#: privately, and published it rather than importing a private name across the
#: seam. `mandatory-review` is absent from it because under that policy the tree
#: deliberately offers no branch -- a branch would answer the question the policy
#: exists to keep open -- so a branch handed in under it is ignored rather than
#: placed.
#:
#: `tests/integration/test_ambiguity_cases.py` still imports the old private name;
#: it is bound to P10's tuple here so there is ONE definition and nothing to
#: drift, and it goes when that file moves to P10's name.
_BRANCH_BEARING: tuple[str, ...] = BRANCH_BEARING_SHARED_POLICIES


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
    #: THE NAME THE PERSON FILED THIS GROUP UNDER, read from P9's own row beside
    #: the state and the members rather than minted anywhere downstream.
    #: `naming.engine_proposal` writes it and `cli` already prints a group by it
    #: on three screens; P11's sentences about a group print the same string, so
    #: a person meets one spelling of their group everywhere. `None` where the
    #: draft carries none -- which is a fact about the group, and the caller says
    #: what to do about it rather than being handed `group_id` wearing a label.
    display_label: str | None = None


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
        display_label=current_group(conn, group_id).display_label,
        # Not every live row. `Membership.decision` has three values and
        # `memberships_for_group` returns all of them, because an `excluded` row
        # is a record P9 keeps on purpose -- §8.7 stores a withdrawn membership
        # WITH the evidence that produced it, and `tree_design.upstream` reads
        # exactly this field to publish `excluded_members`. P11 read the same
        # rows and asked nothing, so a file P9 had excluded went to
        # `place_group`, which gives every membership it is handed a
        # destination. That is P11's own rule about a retracted fact ("a record
        # resting on one would be a contradiction rather than a low-confidence
        # decision") broken one record further out: the person had said the
        # conclusion was wrong, the conclusion was withdrawn, and the file was
        # filed under it anyway.
        #
        # `excluded` ONLY, and not "keep the included ones". The third value is
        # `uncertain` -- what the P8 seam writes for a context-supported member a
        # model was not sure about, alongside the `pending-review` acceptance
        # that makes it safe -- and §6.11's `context-supported group match` is a
        # confidence class P11 is meant to place and show. Dropping it here would
        # answer a question §4.8 deliberately leaves open, under cover of a fix
        # about something else.
        # AND NOT A VERSION THE CORPUS HAS RETIRED (R-25). `memberships` outlive
        # the run that wrote them -- that is the point of them -- so a member row
        # from an earlier run still names the file version that run saw. When the
        # bytes at a path change, P1 marks the old row `superseded_content` and
        # records the new content as a NEW `files` row; the old membership keeps
        # pointing at the old row, and `place_group` gives every membership it is
        # handed a destination.
        #
        # MEASURED, on the four-file corpus of `test_103_diagnosis_backlog.py`:
        # edit one file between two runs and the second run's plan version holds
        # FIVE placement decisions for FOUR files, both versions of the edited
        # file placed. `freeze` then wrote a `move_plans` row for the version that
        # no longer exists -- a plan to move bytes that are not on the disk.
        #
        # A ROW THAT SAYS SO, NOT A ROW THAT IS ABSENT, and the difference is
        # measured. The first draft asked `grouping.retrieval._corpus`'s positive
        # question -- is this file id among the `included` rows? -- which is right
        # when ENUMERATING the corpus and wrong when filtering a list somebody
        # else assembled: every P11 fixture seeds `memberships` without seeding
        # `files`, so it dropped all four members of every group and took 18 tests
        # and 5 errors with it. Absence is not retirement. What P1 wrote is a
        # SENTENCE about this version -- superseded, or its path is gone -- and
        # only a version P1 has spoken about that way is dropped here.
        memberships=tuple(m for m in memberships_for_group(conn, group_id)
                          if m.decision != EXCLUDED
                          and not _p1_has_retired(conn, m.file_id)),
    )


def _p1_has_retired(conn: sqlite3.Connection, file_id: str) -> bool:
    """Has P1 said this file version is no longer part of the corpus?

    Through `get_file`, which is P1's own reader. That table is P1's, and
    `tests/p11/test_p11_connections.py` refuses a query written in this package
    that names it -- "every one of them is asked through its owner's function
    instead" -- so the first draft, which wrote the query here, was a boundary
    breached in order to keep a boundary, and the guard that exists for exactly
    that caught it. Its own prose is written without query keywords for the same
    reason: the scan reads string constants, and a docstring quoting the query it
    replaced would trip the guard describing why it does not.

    P1'S OWN TWO SENTINELS, AND NOTHING ELSE IS READ AS RETIREMENT. Two weaker
    drafts were written and measured first, and each is a rule somebody will
    propose again:

    * "Keep the members whose file id is among the corpus rows." Right when
      ENUMERATING a corpus, wrong when filtering a list somebody else assembled:
      every P11 fixture seeds `memberships` without seeding P1's table at all, so
      it dropped all four members of every group -- 18 tests and 5 errors.
      Absence is not retirement.
    * "Drop any member whose row does not carry the scanned corpus value." The
      column is P3's vocabulary and `scanned`, `unscanned` and `pending` are all
      in it; `tests/test_identity.py` seeds `scanned` as the ordinary case. That
      draft retired every one of them on a word P3 uses to mean the opposite.

    What retires a version is P1 having written a SENTENCE about it, and P1 has
    exactly two to write: the bytes at its path changed, or its path went away.
    Both are P1's own published names, taken from P1's own module, so a third one
    arrives here as an import that does not exist rather than as silence.
    """
    row = get_file(conn, file_id)
    return row is not None and row["scan_state"] in (SUPERSEDED_CONTENT,
                                                     PATH_NO_LONGER_EXISTS)


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
    if (shared_material_policy in BRANCH_BEARING_SHARED_POLICIES
            and shared_branch_node_id):
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
