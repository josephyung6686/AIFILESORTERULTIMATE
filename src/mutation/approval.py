"""The two gates: P13's approval, and §8.4's permission to move at all.

Both answer the same shape of question -- *may this plan run?* -- and neither
answers it by looking at the file. They are together because they are the two
places a person's own decision, rather than a fact about a disk, stops a move,
and because SPEC rule 3 is a statement about how they COMPOSE: an approval lifts
`review_policy_unsatisfied` and nothing else.

**Absence is a refusal, never a default.** No `review_approval` means
`review_policy_unsatisfied`. There is no timeout that ripens into consent and no
configuration that skips the check for a plan whose `Required review policy`
demands one (SPEC, Contract in -> From P13). P13 is unbuilt, so the record
arrives through an injected lookup and what that lookup returns when nobody has
answered is `None` -- which is the refusal, not a gap in the wiring.

**P12 verifies; it does not present.** Rendering the plan, collecting the
gesture and appending `apply review approval` are P13's (M8, S4). Nothing here
writes a `review_approval`, and nothing here decides one.

**§8.4 is P7's, read and not re-derived.** `74` §5.3 is explicit that
`may_move_automatically` is complete -- absence checked first, the flag read
rather than the class, the policy read at the asked-for plan version, no policy
at all treated as no permission -- so P12 calls it and invents no
`movement_permitted_for` seam of its own. Until P13 builds the surface that
WRITES `Policy.automatic_move_permissions` (`74` Wave B9), it refuses every
protected file, and that is the correct posture rather than a bug.

**What is deliberately not here: a precedence rule.** `74` §5.4 -- where
`PlacementDecision.privacy.handling_class` disagrees with P7's current answer,
the decision is stale rather than wrong, and P12 does not pick a winner. The
consequential half of that disagreement is already covered: if P7 now says
protected with no permitting policy, `may_move_automatically` refuses and this
module reports `protected_without_policy`, which is a truer sentence for the
person than "something changed". The inconsequential half -- a class that moved
between two non-protected values, which changes nothing about whether the file
may move -- has no named trigger among §8.3's five, and choosing one would be
P12 answering a question the design left open. It is flagged, not closed.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from placement.vocabulary import (
    BLOCKED_PENDING_USER, REVIEW_POLICIES, REVIEW_REQUIRED,
)
from privacy.moves import (
    NOT_PROTECTED, POLICY_PERMITS, may_move_automatically,
)

from mutation.plan import MovePlan
from mutation.vocabulary import (
    APPROVED, PROTECTED_WITHOUT_POLICY, REFRESH_REQUIRED, REVIEW_POLICY_UNSATISFIED,
    REVIEW_VERDICTS, check, decline_message,
)

#: The `REVIEW_POLICIES` members that demand a `review_approval` before a move
#: may run. `auto_eligible` is the third and demands none -- which is the whole
#: point of the field, and is why this is a tuple over P11's vocabulary rather
#: than a re-listing of it. A policy P11 adds later is refused by `check` at the
#: record boundary rather than silently treated as needing no approval.
POLICIES_REQUIRING_APPROVAL: tuple[str, ...] = (
    REVIEW_REQUIRED, BLOCKED_PENDING_USER)

#: P7's two permitting answers. The other two -- `unreadable_unclassified` and
#: `protected_without_permitting_policy` -- both refuse, and WHICH of them did is
#: carried on the verdict's detail so the person is told that nothing has looked
#: at their file rather than that their file is protected.
_PERMITTING: tuple[str, ...] = (NOT_PROTECTED, POLICY_PERMITS)

_EMPTY: Mapping[str, object] = MappingProxyType({})


@dataclass(frozen=True)
class ReviewApproval:
    """P13's record, as P12 reads it (SPEC, Contract in -> From P13).

    P12 never constructs one in production: it is collected on a screen and
    appended by P13 under `apply review approval`. The dataclass exists here
    because P12 must be able to state what it requires of the record, and
    because a typed record is what makes the three-identifier check a property
    of the code rather than of a caller's dictionary keys.
    """

    approval_id: str
    plan_id: str
    placement_decision_ref: str
    plan_version: str
    required_review_policy: str
    verdict: str
    presented_state_ref: str
    user_id: str
    decided_at: str

    def __post_init__(self) -> None:
        check(self.verdict, REVIEW_VERDICTS, name="review verdict")
        check(self.required_review_policy, REVIEW_POLICIES,
              name="required review policy")


@dataclass(frozen=True)
class GateVerdict:
    """May this plan run, as far as one gate is concerned?"""

    satisfied: bool
    refusal_class: str | None
    #: True only for `refresh_required`: SPEC rule 1 routes it to the same
    #: staleness path as §8.3's five triggers, so P12 re-validates rather than
    #: applying an old decision to a changed file. It still authorizes nothing.
    revalidate: bool = False
    detail: Mapping[str, object] = field(default_factory=lambda: _EMPTY)

    def __post_init__(self) -> None:
        if self.satisfied == (self.refusal_class is not None):
            raise ValueError(
                "a gate verdict is a permission or a named refusal, never both "
                "and never neither")


def _refused(refusal_class: str, *, revalidate: bool = False,
             **detail: object) -> GateVerdict:
    return GateVerdict(
        satisfied=False, refusal_class=refusal_class, revalidate=revalidate,
        detail=MappingProxyType({
            **detail, "message": decline_message(refusal_class)}))


def approval_verdict(plan: MovePlan,
                     approval: ReviewApproval | None) -> GateVerdict:
    """SPEC's four rules, in order. Only `approved` satisfies; absence refuses.

    The three identifiers are checked together and every mismatch is named, so
    a person is told the approval they gave was for a different version of the
    plan rather than that their approval "did not work".
    """
    check(plan.required_review_policy, REVIEW_POLICIES,
          name="required review policy")
    if plan.required_review_policy not in POLICIES_REQUIRING_APPROVAL:
        return GateVerdict(satisfied=True, refusal_class=None)

    if approval is None:
        return _refused(REVIEW_POLICY_UNSATISFIED, plan_id=plan.plan_id,
                        required_review_policy=plan.required_review_policy,
                        approval="absent")

    mismatched = tuple(
        name for name, expected, given in (
            ("plan_id", plan.plan_id, approval.plan_id),
            ("placement_decision_ref", plan.placement_decision_reference,
             approval.placement_decision_ref),
            ("plan_version", plan.organization_plan_version,
             approval.plan_version))
        if expected != given)
    if mismatched:
        # Rule 2. A mismatch is not an approval of a neighbouring plan, and this
        # is what keeps an approval collected under one plan version from
        # authorizing a move under another (§8.8).
        return _refused(REVIEW_POLICY_UNSATISFIED,
                        approval_id=approval.approval_id,
                        mismatched=mismatched)

    if approval.verdict != APPROVED:
        return _refused(REVIEW_POLICY_UNSATISFIED,
                        revalidate=approval.verdict == REFRESH_REQUIRED,
                        approval_id=approval.approval_id,
                        verdict=approval.verdict)
    return GateVerdict(satisfied=True, refusal_class=None)


def protection_verdict(conn: sqlite3.Connection,
                       plan: MovePlan) -> GateVerdict:
    """§8.4's gate, answered by P7 and reported by P12.

    Both refusing answers land on `protected_without_policy`, which is Contract
    out §5's only class for this, and the P7 reason travels on the detail --
    *"nothing has looked at this file"* and *"this file is protected and no
    policy permits it"* are two different things to tell a person even where
    they produce the same refusal.
    """
    verdict = may_move_automatically(conn, plan.file_id,
                                     plan.organization_plan_version)
    if verdict.allowed and verdict.reason in _PERMITTING:
        return GateVerdict(satisfied=True, refusal_class=None)
    return _refused(PROTECTED_WITHOUT_POLICY, file_id=plan.file_id,
                    privacy_reason=verdict.reason,
                    permitting_policy=verdict.permitting_policy)
