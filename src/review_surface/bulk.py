"""A bulk acceptance that stays expandable. §7.10 + §8.2 + §8.7.

    "bulk decisions where the evidence pattern is similar"

The evidence pattern is `bulk_basis` and it is REQUIRED, because it is the thing
the user was shown as the reason these files were offered together. Without it a
bulk acceptance is an unexplained batch, and §8.7's "stored with the evidence that
produced it" has nothing to store.

Every member is enumerated on the record, never a filter expression: a filter
cannot be re-read later to say which files a reversal applies to. `expand` turns
the one action back into a per-member view, and `member_is_separately_correctable`
asserts the property that actually matters -- that a member can be FOUND from the
member's side -- rather than promising it in a docstring. A property nothing can
query is not a property.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from review_surface.collect import collect
from review_surface.records import ReviewAction
from review_surface.store import actions_naming_member
from review_surface.vocabulary import ACTION_ACCEPT_BULK


class BulkBasisRequired(ValueError):
    """A bulk acceptance with no stated evidence pattern."""


@dataclass(frozen=True)
class BulkMemberView:
    """One member of a batch, carrying what the batch was decided against."""

    member_ref: str
    bulk_action_id: str
    bulk_basis: str
    correction_scope: str
    presented_state_ref: str


def collect_bulk(conn: sqlite3.Connection, *, action_id: str, surface: str,
                 subject_ref: str, plan_version: str, session_id: str,
                 correction_scope: str, presented_state_ref: str, user_id: str,
                 acted_at: str, component_version: str,
                 members: Sequence[str], bulk_basis: str,
                 payload: Mapping[str, object] | None = None) -> ReviewAction:
    """One `accept_bulk` action, with every member named and a basis stated."""
    if not bulk_basis:
        raise BulkBasisRequired(
            "a bulk acceptance must carry the evidence pattern the user was "
            "shown as the reason these files were offered together (§7.10). "
            "Without it the batch is unexplained and §8.7 has no evidence to "
            "store beside the decision")
    return collect(
        conn, action_id=action_id, surface=surface, subject_ref=subject_ref,
        plan_version=plan_version, session_id=session_id,
        action=ACTION_ACCEPT_BULK, correction_scope=correction_scope,
        presented_state_ref=presented_state_ref, user_id=user_id,
        acted_at=acted_at, component_version=component_version,
        bulk_member_refs=tuple(members), bulk_basis=bulk_basis, payload=payload)


def expand(conn: sqlite3.Connection,
           action: ReviewAction) -> tuple[BulkMemberView, ...]:
    """One view per enumerated member, in the order the user's action named them."""
    return tuple(
        BulkMemberView(
            member_ref=member, bulk_action_id=action.action_id,
            bulk_basis=action.bulk_basis or "",
            correction_scope=action.correction_scope,
            presented_state_ref=action.presented_state_ref)
        for member in action.bulk_member_refs)


def member_is_separately_correctable(conn: sqlite3.Connection, *,
                                     member_ref: str) -> bool:
    """Can this member be found from the member's side? §8.2's real requirement."""
    return bool(actions_naming_member(conn, member_ref=member_ref))
