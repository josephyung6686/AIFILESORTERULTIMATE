"""The records P13 publishes. It publishes no derived judgement of any kind.

Types, stated once for all of them: every `*_id` and `*_ref` is an opaque
identifier string; `plan_version` is P10's plan id plus version, the version the
surface was rendered against; `routed_to[]` is a list of part identifiers;
`user_id` is §8.2's user-identity field; timestamps are strings; `bulk_basis` is
a display string; and every remaining field takes exactly one value from a closed
list P13 prints.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewAction:
    """Every user gesture on every surface. P13 writes nothing else here.

    `bulk_member_refs` ENUMERATES every member and is never a filter expression:
    a filter cannot be re-read later to say which files a reversal applies to,
    and §8.7 requires each resulting per-file decision to stay individually
    inspectable and individually correctable.

    `correction_scope` has no default anywhere in this package. §8.7's governing
    example is that a user saying ONE transcript belongs in a Columbia packet
    must not teach the engine that all transcripts do -- and a default is an
    inference wearing a keyword's clothes.

    `routed_to` is filled by `routing.route`, never by the caller. P13 hands the
    gesture over; the receiving part decides what it means.
    """

    action_id: str
    surface: str
    subject_ref: str
    plan_version: str
    session_id: str
    action: str
    bulk_member_refs: tuple[str, ...]
    bulk_basis: str | None
    correction_scope: str
    routed_to: tuple[str, ...]
    presented_state_ref: str
    payload: Mapping[str, object]
    user_id: str
    acted_at: str
