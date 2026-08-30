"""P13's closed vocabularies, published BOTH ways.

A tuple for iteration and membership, and one named constant per member for
every consumer. Never a bare string in another module -- a literal is a second
home for a vocabulary and this project's most expensive defect class. Never an
index either: `SURFACES[3]` is single-homed, unreadable, and silently couples the
reader to the tuple's ORDER, so reordering the tuple would change meanings with
no test failing.

`CORRECTION_SCOPES` is IMPORTED from P1, not respelled. P1's writer validates
against it and P1's learning store reads against it; a scope one accepted and the
other rejected would be storable and permanently unreadable.
"""
from __future__ import annotations

from database_agent.events import CORRECTION_SCOPES

#: §8.2's "responsible subsystem" for every event P13 appends. ONE place.
SUBSYSTEM: str = "P13"


class OutOfVocabulary(ValueError):
    """A value outside a closed list, named at the seam rather than stored."""


def check(value: object, allowed: tuple[str, ...], *, name: str) -> str:
    """Return `value` if it is in `allowed`, else raise naming both."""
    if value not in allowed:
        raise OutOfVocabulary(
            f"{value!r} is not one of P13's {len(allowed)} {name} values: "
            f"{list(allowed)}")
    return value  # type: ignore[return-value]


# --- surfaces (P13 SPEC, `review_action.surface`) --------------------------
SURFACE_PLACEMENT: str = "placement"
SURFACE_GROUP_PLAN: str = "group_plan"
SURFACE_RESIDUAL_SET: str = "residual_set"
SURFACE_RESIDUAL_FILE: str = "residual_file"
SURFACE_CANVAS: str = "canvas"
SURFACE_APPLY: str = "apply"
SURFACE_UNDO_CONFLICT: str = "undo_conflict"
SURFACE_CONSENT: str = "consent"
SURFACE_PRIVACY_SETTINGS: str = "privacy_settings"
SURFACE_EVALUATION: str = "evaluation"
SURFACE_LEARNING: str = "learning"
SURFACE_PLAN_VERSION: str = "plan_version"

SURFACES: tuple[str, ...] = (
    SURFACE_PLACEMENT, SURFACE_GROUP_PLAN, SURFACE_RESIDUAL_SET,
    SURFACE_RESIDUAL_FILE, SURFACE_CANVAS, SURFACE_APPLY,
    SURFACE_UNDO_CONFLICT, SURFACE_CONSENT, SURFACE_PRIVACY_SETTINGS,
    SURFACE_EVALUATION, SURFACE_LEARNING, SURFACE_PLAN_VERSION,
)

# --- actions (P13 SPEC, `review_action.action`) ---------------------------
ACTION_ACCEPT: str = "accept"
ACTION_ACCEPT_BULK: str = "accept_bulk"
ACTION_CHANGE_DESTINATION: str = "change_destination"
ACTION_RETURN_TO_ACCEPTED_GROUP: str = "return_to_accepted_group"
ACTION_CREATE_CUSTOM_FOLDER: str = "create_custom_folder"
ACTION_MARK_PRIVATE: str = "mark_private"
ACTION_DEFER: str = "defer"
ACTION_LEAVE_UNTOUCHED: str = "leave_untouched"
ACTION_REJECT: str = "reject"
ACTION_EDIT_RECOMMENDATION: str = "edit_recommendation"
ACTION_DISABLE_SUGGESTION_TYPE: str = "disable_suggestion_type"
ACTION_REFRESH_PLAN: str = "refresh_plan"
ACTION_APPROVE_FOR_APPLY: str = "approve_for_apply"
ACTION_SELECT_CONSENT_OPTION: str = "select_consent_option"
ACTION_SET_REDACTION: str = "set_redaction"
ACTION_ADOPT_VERSION: str = "adopt_version"
ACTION_RESTORE_VERSION: str = "restore_version"
ACTION_RESET_LEARNING: str = "reset_learning"

ACTIONS: tuple[str, ...] = (
    ACTION_ACCEPT, ACTION_ACCEPT_BULK, ACTION_CHANGE_DESTINATION,
    ACTION_RETURN_TO_ACCEPTED_GROUP, ACTION_CREATE_CUSTOM_FOLDER,
    ACTION_MARK_PRIVATE, ACTION_DEFER, ACTION_LEAVE_UNTOUCHED, ACTION_REJECT,
    ACTION_EDIT_RECOMMENDATION, ACTION_DISABLE_SUGGESTION_TYPE,
    ACTION_REFRESH_PLAN, ACTION_APPROVE_FOR_APPLY,
    ACTION_SELECT_CONSENT_OPTION, ACTION_SET_REDACTION, ACTION_ADOPT_VERSION,
    ACTION_RESTORE_VERSION, ACTION_RESET_LEARNING,
)

# --- approval verdicts (P13 SPEC, `review_approval.verdict`) --------------
VERDICT_APPROVED: str = "approved"
VERDICT_REJECTED: str = "rejected"
VERDICT_DEFERRED: str = "deferred"
VERDICT_REFRESH_REQUIRED: str = "refresh_required"

VERDICTS: tuple[str, ...] = (
    VERDICT_APPROVED, VERDICT_REJECTED, VERDICT_DEFERRED,
    VERDICT_REFRESH_REQUIRED,
)

# --- progress line (P13 SPEC, `progress_line.entries[]`) ------------------
STATE_COMPLETED: str = "completed"
STATE_DEFERRED: str = "deferred"
STATE_BLOCKED: str = "blocked"
PROGRESS_STATES: tuple[str, ...] = (
    STATE_COMPLETED, STATE_DEFERRED, STATE_BLOCKED)

SOURCE_P3_R5: str = "P3.R5"
SOURCE_P4_RUNS: str = "P4.extraction_runs"
SOURCE_P8: str = "P8"
PROGRESS_SOURCES: tuple[str, ...] = (SOURCE_P3_R5, SOURCE_P4_RUNS, SOURCE_P8)

# --- the three registered §8.2 event names --------------------------------
# Registration is a spec-level act with NO run-time call, and all three are
# already in P1's registry. P13 registers nothing.
EVENT_PRESENTATION: str = "review presentation"
EVENT_ACTION_ROUTED: str = "review action routed"
EVENT_APPROVAL: str = "apply review approval"
EVENT_TYPES: tuple[str, ...] = (
    EVENT_PRESENTATION, EVENT_ACTION_ROUTED, EVENT_APPROVAL)

#: P3 SPEC, ratified 2026-08-20 and restated in the P13 SPEC's `review_action`
#: block. A protected container is its own inspectable list and carries NO
#: ACTION AT ALL. It is not a surface, because a surface is a place a gesture can
#: be made, and it is not an action, because there is no choice to offer.
UNTOUCHED_PROTECTED: str = "untouched_protected"

__all__ = [name for name in dir() if name.isupper()] + [
    "OutOfVocabulary", "check", "CORRECTION_SCOPES"]
