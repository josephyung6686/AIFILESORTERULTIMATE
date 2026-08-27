"""P13's `review_action`, as P13's SPEC publishes its fields. Tests only.

P13 is specification only: its three event names are registered in
`database_agent.events` and it has no producer. This fixture is a structural
stand-in with P13's exact field names, so the day P13 publishes its record the
import swaps and no field name changes. `src/tree_design/` never imports it.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewActionFixture:
    review_action_id: str
    surface: str            # canvas | plan_version
    subject_ref: str        # a node_id, or a plan_version_id for a version action
    plan_version: str
    action: str
    correction_scope: str
    presented_state_ref: str
    user_id: str
    observed_at: str
    payload: dict


def accept(subject_ref: str, *, plan_version: str) -> ReviewActionFixture:
    """§5.1's first gesture: the user accepts a proposed branch.

    `subject_ref` is a BRANCH CANDIDATE id, not a node id — the node does not
    exist until this action is applied. That asymmetry is why `apply_review_action`
    handles `accept` before it looks a target up.
    """
    return ReviewActionFixture(
        review_action_id=f"ra_accept_{subject_ref}", surface="canvas",
        subject_ref=subject_ref, plan_version=plan_version, action="accept",
        correction_scope="node", presented_state_ref=f"ps_{subject_ref}",
        user_id="jy", observed_at="2026-08-27T00:00:00Z", payload={})


def rename(node_id: str, *, plan_version: str, new_label: str) -> ReviewActionFixture:
    return ReviewActionFixture(
        review_action_id=f"ra_rename_{node_id}", surface="canvas",
        subject_ref=node_id, plan_version=plan_version, action="rename",
        correction_scope="node", presented_state_ref=f"ps_{node_id}",
        user_id="jy", observed_at="2026-08-27T00:00:00Z",
        payload={"display_label": new_label},
    )


def ignore_existing(node_id: str, *, plan_version: str) -> ReviewActionFixture:
    return ReviewActionFixture(
        review_action_id=f"ra_ignore_{node_id}", surface="canvas",
        subject_ref=node_id, plan_version=plan_version, action="ignore",
        correction_scope="node", presented_state_ref=f"ps_{node_id}",
        user_id="jy", observed_at="2026-08-27T00:01:00Z", payload={},
    )


def restore(plan_version: str, *, target: str) -> ReviewActionFixture:
    return ReviewActionFixture(
        review_action_id=f"ra_restore_{target}", surface="plan_version",
        subject_ref=target, plan_version=plan_version, action="restore_version",
        correction_scope="corpus", presented_state_ref=f"ps_{target}",
        user_id="jy", observed_at="2026-08-27T00:02:00Z", payload={},
    )
