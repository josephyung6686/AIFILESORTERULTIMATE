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

# --- §8.7's gestures, homed 2026-09-02 -------------------------------------
#: Five of §8.7's six unhomed gestures, in six members -- *"merging or splitting
#: groups"* is one phrase and two gestures. Every spelling is the receiving part's
#: own existing word, ADOPTED rather than coined, so P13 takes the word the part
#: that applies the gesture already uses (`81` §3.3 traces each to a design
#: sentence). The approval block below records who approved these exact strings.
ACTION_EXCLUDE_FROM_PACKET: str = "exclude_from_packet"
ACTION_RENAME: str = "rename"
ACTION_MERGE: str = "merge"
ACTION_SPLIT: str = "split"
ACTION_REORDER: str = "reorder"

#: The one coined name, and it is coined from the sentence recording its own
#: absence: `tree_design/pipeline.py:460-472` says outright *"there is no
#: `set-refinement-disposition` review action"*. §5.8's shallow-by-choice is a
#: deliberate answer and `refine-later` is a different one; collapsing them would
#: make a design look like unfinished work, which is why the gesture needs a name.
ACTION_SET_REFINEMENT_DISPOSITION: str = "set_refinement_disposition"

#: RULING 2026-08-31 (`81` §14), recorded here because a closed vocabulary carries
#: its own approval at the member. **P13 owns the name of a gesture.** `74` §8 Q2 --
#: four rival `review_action` vocabularies for one record -- is closed as reading
#: (i): the part that COLLECTS a gesture names it, and P9, P10 and P11 carry those
#: names verbatim (MINOR 6/7). The alternative was refused on one ground: under it
#: this tuple would grow whenever P10 edited a tuple of its own, and a vocabulary
#: that can grow without anyone approving it is not closed.
#:
#: **THE TUPLE GREW ON 2026-09-02, AND THIS IS THAT APPROVAL.** §8.7
#: (`01`:1842-1845) lists eleven things a person does that *"should become local
#: learning records with scope"*, and the original eighteen covered five of them;
#: `81` §4.4 tabulated the six with no home. The eighteen were §7.10's
#: residual-review sentence plus the §8.3/§8.4/§8.8 machinery actions -- a
#: faithful reading of one paragraph, where the design has four.
#:
#: **APPROVED BY: the owner (Joseph), ON: 2026-09-02.** Relayed by the team lead,
#: whose message is the transport and not the authority. **He was shown these six
#: strings verbatim, as a tuple, beside this approval line, and answered "Approve,
#: these names" -- he approved SPELLINGS, not a category:**
#:
#:     "exclude_from_packet", "rename", "merge", "split", "reorder",
#:     "set_refinement_disposition"
#:
#: An earlier delegated approval for the same members was offered and REFUSED,
#: because `81` §14.1 reserves it: *"Each addition is a closed-vocabulary member
#: and needs the owner's approval recorded at the member. They are not minted by
#: whoever notices the gap."* The refusal is why this line names him.
#:
#: **ONE §8.7 GESTURE IS STILL UNHOMED: "creating a custom template".** `81` §7
#: asked whether it and `create_custom_folder` are one gesture or two; the owner
#: ruled on 2026-09-02 that they are **two** -- *a template is a reusable shape, a
#: folder is one actual folder* -- so it needs its own member. **Its spelling was
#: NOT among the six shown to him**, so no member is minted for it here and the
#: strict xfail in `tests/p13/test_p13_unhomed_gestures.py` stays on, naming that
#: one gesture. It comes off when that spelling is approved the same way these
#: six were.
#:
#: Also settled 2026-09-02, recorded here because a member outlives the
#: conversation: **a canvas gesture DOES travel as a `review_action`** (`81`
#: §13.1's Q5', and with it `74` §8 Q4) -- *"every edit a person makes to the
#: proposed structure is recorded in the same audit trail as accepting or
#: rejecting a file, so one history explains every change"*. `rename`, `merge`,
#: `split` and `reorder` stand on that answer. §14.1 had ASSUMED it; it is now
#: answered.
ACTIONS: tuple[str, ...] = (
    ACTION_ACCEPT, ACTION_ACCEPT_BULK, ACTION_CHANGE_DESTINATION,
    ACTION_RETURN_TO_ACCEPTED_GROUP, ACTION_CREATE_CUSTOM_FOLDER,
    ACTION_MARK_PRIVATE, ACTION_DEFER, ACTION_LEAVE_UNTOUCHED, ACTION_REJECT,
    ACTION_EDIT_RECOMMENDATION, ACTION_DISABLE_SUGGESTION_TYPE,
    ACTION_REFRESH_PLAN, ACTION_APPROVE_FOR_APPLY,
    ACTION_SELECT_CONSENT_OPTION, ACTION_SET_REDACTION, ACTION_ADOPT_VERSION,
    ACTION_RESTORE_VERSION, ACTION_RESET_LEARNING,
    # §8.7's, homed 2026-09-02 on the owner's approval recorded above.
    ACTION_EXCLUDE_FROM_PACKET, ACTION_RENAME, ACTION_MERGE, ACTION_SPLIT,
    ACTION_REORDER, ACTION_SET_REFINEMENT_DISPOSITION,
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
