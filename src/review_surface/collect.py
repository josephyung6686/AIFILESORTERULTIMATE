"""Collecting one gesture. P13 presents and collects; it never decides.

Four refusals, and each is a Done-means:

* **`correction_scope` has no default.** A default is an inference, and §8.7's
  whole example is about not inferring one: a user saying that ONE transcript
  belongs in a Columbia packet must not teach the engine that all transcripts do.
  The widest scope is not spelled in this module at all; the value is validated
  against P1's tuple.
* **A presentation must exist.** §8.7 requires negative feedback stored WITH the
  evidence that produced it: a file rejected while its OCR text was redacted is a
  different signal from one rejected with the evidence visible. An action with no
  recorded presentation carries no such evidence.
* **A protected container has no action.** Applications and system items are
  never read or moved, so offering the user a choice would imply one exists. The
  SPEC prints that paragraph inside its `review_action` field block, between
  `session_id` and `action`; it is plainly not a field, and it is read here as a
  rule about presentation and enforced as a refusal. If the owner intended a
  field there, this reading is wrong -- it is flagged rather than resolved.
* **A bulk acceptance enumerates its members.** A filter expression cannot be
  re-read later to say which files a reversal applies to.

Nothing here interprets the gesture. `routed_to` names who will.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping, Sequence

from database_agent.events import CORRECTION_SCOPES, append_event

from review_surface.records import ReviewAction
from review_surface.routing import route
from review_surface.store import presentation_exists
from review_surface.vocabulary import (
    ACTION_ACCEPT_BULK,
    ACTIONS,
    EVENT_ACTION_ROUTED,
    SUBSYSTEM,
    SURFACES,
    UNTOUCHED_PROTECTED,
    check,
)


class ScopeNotPresented(ValueError):
    """A scope outside §8.7's six. It was not chosen, so it was not presented."""


class PresentationRequired(ValueError):
    """An action with no record of what the user was shown."""


class ProtectedContainerHasNoAction(RuntimeError):
    """A gesture over an untouched protected container. There is no choice to offer."""


class BulkMembersRequired(ValueError):
    """A bulk acceptance with no enumerated members. A filter is not a list."""


def collect(conn: sqlite3.Connection, *, action_id: str, surface: str,
            subject_ref: str, plan_version: str, session_id: str, action: str,
            correction_scope: str, presented_state_ref: str, user_id: str,
            acted_at: str, component_version: str,
            bulk_member_refs: Sequence[str] = (), bulk_basis: str | None = None,
            payload: Mapping[str, object] | None = None) -> ReviewAction:
    """Validate, route, append the §8.2 event, return the record. Store separately.

    `correction_scope` is a required keyword with NO default. That is the whole
    mechanism behind "scope is presented, never inferred": there is no value this
    function can supply on the user's behalf, so there is no path by which one
    gets supplied.
    """
    check(surface, SURFACES, name="surface")
    check(action, ACTIONS, name="action")
    if correction_scope not in CORRECTION_SCOPES:
        raise ScopeNotPresented(
            f"{correction_scope!r} is not one of §8.7's six scopes "
            f"{list(CORRECTION_SCOPES)}. Every collected action carries a scope "
            "the user chose at collection time")
    fields = dict(payload or {})
    if UNTOUCHED_PROTECTED in (subject_ref, fields.get("subject_kind")):
        raise ProtectedContainerHasNoAction(
            "protected containers are presented as their own inspectable list "
            "and carry no action at all. Applications and system items are "
            "never read or moved, so offering the user a choice here would "
            "imply one exists. The list answers 'why was nothing proposed for "
            "this?' instead of leaving silence")
    members = tuple(bulk_member_refs)
    if action == ACTION_ACCEPT_BULK and not members:
        raise BulkMembersRequired(
            "a bulk acceptance enumerates every member. A filter expression "
            "cannot be re-read later to say which files a reversal applies to")
    if not presentation_exists(conn, presented_state_ref):
        raise PresentationRequired(
            f"{presented_state_ref!r} names no recorded presentation. §8.7 "
            "requires feedback to be stored with the evidence that produced it, "
            "and a gesture with no record of what was shown carries none")
    parts = route(surface, action)
    record = ReviewAction(
        action_id=action_id, surface=surface, subject_ref=subject_ref,
        plan_version=plan_version, session_id=session_id, action=action,
        bulk_member_refs=members, bulk_basis=bulk_basis,
        correction_scope=correction_scope, routed_to=parts,
        presented_state_ref=presented_state_ref, payload=fields,
        user_id=user_id, acted_at=acted_at)
    append_event(
        conn, event_type=EVENT_ACTION_ROUTED, subsystem=SUBSYSTEM,
        component_version=component_version, observed_at=acted_at,
        user_id=user_id, correction_scope=correction_scope,
        correction_subject=subject_ref,
        explanation=json.dumps(
            {"action_id": action_id, "surface": surface, "action": action,
             "routed_to": list(parts), "correction_scope": correction_scope,
             "presented_state_ref": presented_state_ref,
             "bulk_member_refs": list(members), "bulk_basis": bulk_basis},
            sort_keys=True))
    return record
