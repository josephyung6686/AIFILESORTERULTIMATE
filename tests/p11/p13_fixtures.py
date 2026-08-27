"""A test-only stand-in for P13's `review_action`. TESTS ONLY.

P13 is specification only: its three event types are registered
(`database_agent/events.py:59-61`) and no producer exists. `src/placement/` may
never import this module and a test asserts it does not -- a source stub would be
P11 deciding what a user gesture looks like, which is P13's to say.

The field list is P13 SPEC:247-279 restricted to the four surfaces P13 routes to
P11 (P13 SPEC:294). Replacing this import with P13's public record is a required
integration test when P13 ships.
"""
from __future__ import annotations

from dataclasses import dataclass, field

#: P13 SPEC:294 -- the four surfaces whose actions route to P11.
SURFACES: tuple[str, ...] = (
    "placement", "group_plan", "residual_set", "residual_file",
)

#: The subset of P13 SPEC:264-270's actions a placement or residual surface
#: collects. `adopt_version`, `restore_version`, `select_consent_option`,
#: `set_redaction`, `refresh_plan`, `approve_for_apply` and `reset_learning`
#: route elsewhere and are deliberately absent.
ACTIONS: tuple[str, ...] = (
    "accept", "accept_bulk", "change_destination", "return_to_accepted_group",
    "create_custom_folder", "mark_private", "defer", "leave_untouched", "reject",
    "edit_recommendation", "disable_suggestion_type",
)


@dataclass(frozen=True)
class ReviewActionFixture:
    action_id: str
    surface: str
    subject_ref: str
    plan_version: str
    session_id: str
    action: str
    bulk_member_refs: tuple[str, ...]
    bulk_basis: str | None
    correction_scope: str
    presented_state_ref: str
    user_id: str
    acted_at: str
    payload: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.surface not in SURFACES:
            raise ValueError(f"{self.surface!r} is not one of P11's {SURFACES}")
        if self.action not in ACTIONS:
            raise ValueError(f"{self.action!r} is not one of {ACTIONS}")
        for name in ("action_id", "subject_ref", "plan_version",
                     "presented_state_ref", "user_id", "acted_at"):
            if not getattr(self, name):
                raise ValueError(f"{name} is required on a review action")


def accept(**overrides) -> ReviewActionFixture:
    values = dict(
        action_id="a-1", surface="placement", subject_ref="d1",
        plan_version="plan-1", session_id="s-1", action="accept",
        bulk_member_refs=(), bulk_basis=None, correction_scope="file",
        presented_state_ref="ev-42", user_id="u1",
        acted_at="2026-08-27T00:00:00Z", payload={},
    )
    values.update(overrides)
    return ReviewActionFixture(**values)


def change_destination(**overrides) -> ReviewActionFixture:
    values = dict(action="change_destination",
                  payload={"node_id": "n-course-alt"})
    values.update(overrides)
    return accept(**values)


def reject(**overrides) -> ReviewActionFixture:
    values = dict(action="reject", correction_scope="node",
                  payload={"node_id": "n-course"})
    values.update(overrides)
    return accept(**values)


def accept_bulk(**overrides) -> ReviewActionFixture:
    values = dict(action="accept_bulk", surface="residual_set",
                  subject_ref="set-1",
                  bulk_member_refs=("f-a", "f-b", "f-c"),
                  bulk_basis="all three are product screenshots with no association",
                  correction_scope="corpus")
    values.update(overrides)
    return accept(**values)


def defer(**overrides) -> ReviewActionFixture:
    values = dict(action="defer")
    values.update(overrides)
    return accept(**values)


def create_custom_folder(**overrides) -> ReviewActionFixture:
    values = dict(action="create_custom_folder", surface="residual_set",
                  subject_ref="set-1", correction_scope="node",
                  payload={"display_label": "Receipts to Process"})
    values.update(overrides)
    return accept(**values)


RECORDED_ACTIONS = (
    accept, change_destination, reject, accept_bulk, defer, create_custom_folder,
)
