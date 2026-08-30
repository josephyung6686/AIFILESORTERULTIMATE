"""Routing is the whole contract.

P13 hands the action to the owning part and THAT part decides what it means.
An action may route to more than one part; it is still ONE collected gesture,
which is precisely why P13's `review action routed` event exists: §7.10's
"create a custom folder" during residual review is both a residual decision
(P11) and a tree edit (P10), and without P13's event the two records lose the
fact that they were one user action.

Two tables, not one. A surface says who normally owns what happens there; an
action says who ELSE a particular gesture reaches regardless of surface. Folding
them into one table would need a row per (surface, action) pair, most of them
meaningless, and the two rules are genuinely different rules.

P2 is not a routing target. P13 emits no `stage_output`, is not one of §8.5's
ten attribution stages, and inventing an eleventh would corrupt P2's closed
`stage_id` enumeration.
"""
from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from review_surface.vocabulary import (
    ACTION_ADOPT_VERSION,
    ACTION_APPROVE_FOR_APPLY,
    ACTION_CREATE_CUSTOM_FOLDER,
    ACTION_MARK_PRIVATE,
    ACTION_REFRESH_PLAN,
    ACTION_RESET_LEARNING,
    ACTION_RESTORE_VERSION,
    ACTION_SELECT_CONSENT_OPTION,
    ACTION_SET_REDACTION,
    ACTIONS,
    SURFACE_APPLY,
    SURFACE_CANVAS,
    SURFACE_CONSENT,
    SURFACE_EVALUATION,
    SURFACE_GROUP_PLAN,
    SURFACE_LEARNING,
    SURFACE_PLACEMENT,
    SURFACE_PLAN_VERSION,
    SURFACE_PRIVACY_SETTINGS,
    SURFACE_RESIDUAL_FILE,
    SURFACE_RESIDUAL_SET,
    SURFACE_UNDO_CONFLICT,
    SURFACES,
)

#: The seven parts the SPEC's routing table names, in the order routing output
#: uses. The order is fixed so a replay reproduces the routing exactly; a set
#: would not be an answer.
PARTS: tuple[str, ...] = ("P1", "P6", "P7", "P9", "P10", "P11", "P12")


class Unroutable(RuntimeError):
    """A surface or action with no owning part. Refused, never silently dropped."""


ROUTING: Mapping[str, tuple[str, ...]] = MappingProxyType({
    SURFACE_PLACEMENT: ("P11",),
    # Group changes collected on `group_plan` route to P9 as well as to P11,
    # which owns the group plan record itself.
    SURFACE_GROUP_PLAN: ("P9", "P11"),
    SURFACE_RESIDUAL_SET: ("P11",),
    SURFACE_RESIDUAL_FILE: ("P11",),
    SURFACE_CANVAS: ("P10",),
    SURFACE_APPLY: ("P12",),
    SURFACE_UNDO_CONFLICT: ("P12",),
    SURFACE_CONSENT: ("P7",),
    SURFACE_PRIVACY_SETTINGS: ("P7",),
    # SPEC Open question 9 is OPEN: whether a reviewer adjudication in the
    # evaluation view becomes an §8.7 correction. P2 owns the record either way,
    # and P2 is not in the SPEC's routing table -- so an evaluation gesture
    # routes to P1, which writes the event, and nothing more is claimed.
    SURFACE_EVALUATION: ("P1",),
    SURFACE_LEARNING: ("P1",),
    SURFACE_PLAN_VERSION: ("P10",),
})
assert set(ROUTING) == set(SURFACES)

#: Parts a gesture reaches IN ADDITION to its surface's owner.
ACTION_ROUTING: Mapping[str, tuple[str, ...]] = MappingProxyType({
    # A tree edit, including a custom folder created during residual review,
    # goes to P10. It produces a new plan version (§8.8); it is never the model
    # inventing a destination (§7.4).
    ACTION_CREATE_CUSTOM_FOLDER: ("P10",),
    # A reclassification to private is P7's AND P6's, jointly.
    ACTION_MARK_PRIVATE: ("P6", "P7"),
    ACTION_SELECT_CONSENT_OPTION: ("P7",),
    ACTION_SET_REDACTION: ("P7",),
    ACTION_REFRESH_PLAN: ("P12",),
    ACTION_APPROVE_FOR_APPLY: ("P12",),
    ACTION_ADOPT_VERSION: ("P10",),
    ACTION_RESTORE_VERSION: ("P10",),
    ACTION_RESET_LEARNING: ("P1",),
})
assert set(ACTION_ROUTING) <= set(ACTIONS)


def route(surface: str, action: str) -> tuple[str, ...]:
    """Every part this one gesture is handed to, in `PARTS` order, deduplicated."""
    if surface not in ROUTING:
        raise Unroutable(
            f"{surface!r} is not one of P13's {len(SURFACES)} surfaces, so there "
            "is no part to hand this gesture to. An action with no owner would "
            "be collected and silently mean nothing")
    if action not in ACTIONS:
        raise Unroutable(
            f"{action!r} is not one of P13's {len(ACTIONS)} actions")
    parts = set(ROUTING[surface]) | set(ACTION_ROUTING.get(action, ()))
    return tuple(sorted(parts, key=PARTS.index))
