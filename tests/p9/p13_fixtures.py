# tests/p9/p13_fixtures.py
"""A test-only stand-in for P13's review action. TESTS ONLY.

P13 is specification only: its event types are registered and its test fixtures
exist, but there is no producer. `src/grouping/` may never import this module, and
a test asserts it does not. No source stub impersonates P13 — a stub in `src/`
would be P9 deciding what a user action looks like, which is P13's to say.

Replacing this import with P13's public record is a required integration test when
P13 ships. That swap is the whole point of the boundary being named.
"""
from __future__ import annotations

from dataclasses import dataclass

#: The actions the design gives the user over a proposed group. Append-only and
#: reversible at P9's decision layer: none of them deletes or moves a file.
REVIEW_ACTIONS: tuple[str, ...] = (
    "accept",
    "edit",
    "reject",
    "defer",
    "restore",
    "reset-suggestion",
    "exclude-from-packet",
)


#: The surface a group review happens on. P9 accepts actions from this one and
#: refuses any other: a node or template action reaching P9's receiver would be
#: P9 recording a decision about something it does not own.
GROUP_PLAN_SURFACE: str = "group_plan"


@dataclass(frozen=True)
class ReviewActionFixture:
    """One recorded user decision, as P9 expects to receive it.

    `scope` is the group or the membership. A bulk decision arrives as one action
    per subject with a shared `basis`, not as a single action over a set: the
    design permits bulk review only for equivalent low-risk proposals, and a
    collapsed action could not say which of them a later reversal applies to.

    `correction_scope`, `user_id` and `presented_state_ref` are carried and never
    inferred. P1's learning store is scoped, and a receiver that guessed `corpus`
    would teach the engine from one file that every file like it belongs there --
    the §8.7 failure the scope exists to prevent.
    """

    action: str
    plan_version_id: str
    group_id: str
    membership_id: str | None
    basis: str
    user_edited_label: str | None
    decided_at: str
    user_id: str
    correction_scope: str
    presented_state_ref: str
    surface: str = GROUP_PLAN_SURFACE

    def __post_init__(self) -> None:
        if self.action not in REVIEW_ACTIONS:
            raise ValueError(
                f"{self.action!r} is not one of P13's {len(REVIEW_ACTIONS)} review "
                "actions"
            )
        for name in ("plan_version_id", "group_id", "basis", "decided_at",
                     "user_id", "correction_scope", "presented_state_ref"):
            if not getattr(self, name):
                raise ValueError(f"{name} is required on a review action")


def accept_group(**overrides) -> ReviewActionFixture:
    values = dict(
        action="accept",
        plan_version_id="plan-1",
        group_id="fixture-course-group",
        membership_id=None,
        basis="user reviewed the evidence and accepted the group",
        user_edited_label=None,
        decided_at="2026-08-26T00:00:00Z",
        user_id="user-1",
        correction_scope="group",
        presented_state_ref="presented-1",
    )
    values.update(overrides)
    return ReviewActionFixture(**values)


def reject_group(**overrides) -> ReviewActionFixture:
    """A rejection is both an acceptance state and a scoped learning record.

    SR6 queries the learning record, so a rejection under one plan version still
    stops the same attractive-but-incorrect grouping resurfacing under the next.
    """
    values = dict(
        action="reject",
        basis="the packet mixes two target institutions",
    )
    values.update(overrides)
    return accept_group(**values)


def exclude_member(**overrides) -> ReviewActionFixture:
    values = dict(
        action="exclude-from-packet",
        membership_id="fixture-membership",
        basis="this transcript belongs to a different application",
        correction_scope="file",
    )
    values.update(overrides)
    return accept_group(**values)


def defer_group(**overrides) -> ReviewActionFixture:
    values = dict(action="defer", basis="decide after the term evidence lands")
    values.update(overrides)
    return accept_group(**values)


RECORDED_REVIEW_ACTIONS = (
    accept_group, reject_group, exclude_member, defer_group,
)
