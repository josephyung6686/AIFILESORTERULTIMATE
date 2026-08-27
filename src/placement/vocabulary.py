# src/placement/vocabulary.py
"""P11's closed vocabularies. Named constant == string value, one home each.

One rule decides every import here. Import when the CONCEPT is the same; publish
a distinct constant and pin it by test when the SPELLING is the same but the
concept differs. `grouping/vocabulary.py` set the precedent with P1's
`scan_state = "included"`: a borrowed value gets a name that cannot be mistaken
for the local one, never a shared binding.

Four strings are P8's and P11's at once. `return_to_placement`, `leave_in_place`
and `abstain` are P8 dispositions; `mark_review_later` is a P8 residual action.
All four are P11 OUTCOMES -- a different axis -- so P11 spells its own and a test
holds the strings equal. `VERDICTS` is the opposite case: it IS P8's outcome
vocabulary (SPEC:462, MINOR 7) and is the same object, not a copy.

No path, folder, template or node-creation concept lives here. P11 names nodes
P10 froze; it mints none.
"""
from __future__ import annotations

from database_agent.events import CORRECTION_SCOPES
from evidence_shape.vocabulary import RELIABILITY_STATES
from facts.states import DIRECT, LLM_SUPPORTED, POSSIBLE, USER_CONFIRMED, VALIDATED
from llm_harness.vocabulary import (
    ABSTAIN as P8_ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    CONTEXT_SUPPORTED,
    OUTCOMES as P8_OUTCOMES,
    REJECT,
    RESIDUAL_ACTIONS,
    SCOPE_FILE,
    SCOPE_GROUP,
    WEAK,
)
from privacy.vocabulary import HANDLING_CLASSES

# --- re-exported, because the concept is the other part's ------------------------

#: §6.10's verdict, unchanged from P8 (SPEC:462). The same tuple object. Its five
#: members are bound above -- `ACCEPT_DIRECT`, `ACCEPT_CONTEXT_SUPPORTED`, `WEAK`,
#: `REJECT` and `ABSTAIN` -- so a reader of a P11 verdict never types the string.
VERDICTS: tuple[str, ...] = P8_OUTCOMES

#: `abstain` on P8's VERDICT axis. It is the same string as the OUTCOME `ABSTAIN`
#: below and a separate name for exactly the reason this module's docstring gives:
#: the spelling is shared, the concept is not, and `grouping/vocabulary.py` set the
#: precedent with P1's borrowed `scan_state`. A module reading a verdict must not
#: reach for the outcome constant to spell it.
#:
#: `ACCEPT_DIRECT`, `ACCEPT_CONTEXT_SUPPORTED`, `WEAK` and `REJECT` need no such
#: twin: they are bound by name from P8 above and exist on no second P11 axis, so
#: a `_VERDICT` alias for them would be a third spelling of one string.
ABSTAIN_VERDICT: str = P8_ABSTAIN
assert ABSTAIN_VERDICT in VERDICTS

#: §7.7's eight actions in their machine spelling. P8 owns the controlled set and
#: refuses anything outside it at Site D; P11 maps them into `OUTCOMES`.
ACTIONS: tuple[str, ...] = RESIDUAL_ACTIONS

#: §8.7's six scopes, in P1's spelling, which is also P13's.
SCOPES: tuple[str, ...] = CORRECTION_SCOPES

#: §8.4's five handling classes, P7's.
CLASSES: tuple[str, ...] = HANDLING_CLASSES

# --- origin and subject -----------------------------------------------------------

PLACEMENT: str = "placement"
RESIDUAL: str = "residual"
ORIGIN_STAGES: tuple[str, ...] = (PLACEMENT, RESIDUAL)

FILE: str = SCOPE_FILE
GROUP: str = SCOPE_GROUP
SUBJECT_KINDS: tuple[str, ...] = (FILE, GROUP)

# --- outcomes: P11's own axis, four of them spelled like P8 values ----------------

PLACE: str = "place"
RETURN_TO_PLACEMENT: str = "return_to_placement"
MARK_REVIEW_LATER: str = "mark_review_later"
LEAVE_IN_PLACE: str = "leave_in_place"
MARK_STATE: str = "mark_state"
ASK_USER: str = "ask_user"
ABSTAIN: str = P8_ABSTAIN

OUTCOMES: tuple[str, ...] = (
    PLACE, RETURN_TO_PLACEMENT, MARK_REVIEW_LATER, LEAVE_IN_PLACE, MARK_STATE,
    ASK_USER, ABSTAIN,
)

#: The one outcome P12 builds a plan from (SPEC:551, M13). Every other produces
#: no plan, `abstain` included.
PLAN_BEARING_OUTCOMES: tuple[str, ...] = (PLACE,)

# --- the destination -------------------------------------------------------------
#
# P10's vocabulary, carried verbatim on the node (SPEC:322-323, MINOR 6). P10 is
# unbuilt, so the values are spelled here from P10's SPEC and this module is the
# one home until P10 publishes them, at which point this becomes a re-export.

ORDINARY: str = "ordinary"
SCOPED_GENERAL: str = "scoped-general"
RESIDUAL_ROLE: str = "residual"
SHARED_MATERIAL: str = "shared-material"
NODE_ROLES: tuple[str, ...] = (ORDINARY, SCOPED_GENERAL, RESIDUAL_ROLE, SHARED_MATERIAL)

PHYSICAL_DESTINATION: str = "physical-destination"
REVIEW_ONLY: str = "review-only"
LEAVE_IN_PLACE_DISPOSITION: str = "leave-in-place"
DISPOSITIONS: tuple[str, ...] = (
    PHYSICAL_DESTINATION, REVIEW_ONLY, LEAVE_IN_PLACE_DISPOSITION,
)

EXISTING: str = "existing"
PROPOSED: str = "proposed"
USER_CREATED: str = "user-created"
PROTECTED_NODE: str = "protected"
IGNORED: str = "ignored"
NODE_TYPES: tuple[str, ...] = (
    EXISTING, PROPOSED, USER_CREATED, PROTECTED_NODE, IGNORED,
)

CONFIRMED_DOMAIN_GROUP: str = "confirmed_domain_group"
ACCEPTED_GRAPH_OR_PURPOSE_PACKET: str = "accepted_graph_or_purpose_packet"
RETURN_TARGET_KINDS: tuple[str, ...] = (
    CONFIRMED_DOMAIN_GROUP, ACCEPTED_GRAPH_OR_PURPOSE_PACKET,
)

PROTECTED: str = "protected"
UNSUPPORTED: str = "unsupported"
MARKED_STATES: tuple[str, ...] = (PROTECTED, UNSUPPORTED)

# --- evidence and confidence -----------------------------------------------------
#
# Five of the six are P6's reliability states in their live snake_case spelling;
# `rejected` is dropped because a rejected fact cannot support a placement
# (SPEC:427-435). `context-supported` is added, hyphenated, because it is P9's
# membership basis and P8 already publishes that exact string. The mixed casing is
# what two owners publish, and P11 respells neither of them.

EVIDENCE_TYPES: tuple[str, ...] = (
    USER_CONFIRMED, DIRECT, VALIDATED, LLM_SUPPORTED, CONTEXT_SUPPORTED, POSSIBLE,
)

EXACT_FACT_MATCH: str = "exact fact match"
CONTEXT_SUPPORTED_GROUP_MATCH: str = "context-supported group match"
SHARED_MATERIAL_DECISION: str = "shared-material decision"
ABSTAIN_NO_SUPPORTED_DESTINATION: str = "abstain: no supported destination"
CONFIDENCE_CLASSES: tuple[str, ...] = (
    EXACT_FACT_MATCH, CONTEXT_SUPPORTED_GROUP_MATCH, SHARED_MATERIAL_DECISION,
    ABSTAIN_NO_SUPPORTED_DESTINATION,
)

# --- the two-condition rule ------------------------------------------------------

MARGIN_TRUE: str = "true"
MARGIN_TRUE_VACUOUS: str = "true_vacuous"
MARGIN_FALSE: str = "false"
MEETS_MARGIN_VALUES: tuple[str, ...] = (
    MARGIN_TRUE, MARGIN_TRUE_VACUOUS, MARGIN_FALSE,
)

# --- abstention ------------------------------------------------------------------

NO_SUPPORTED_DESTINATION: str = "no_supported_destination"
LOW_MARGIN: str = "low_margin"
SEMANTIC_ONLY: str = "semantic_only"
GENERIC_HUB_ONLY: str = "generic_hub_only"
CONFLICTING_FACTS: str = "conflicting_facts"
NO_SHARED_BRANCH: str = "no_shared_branch"
BUDGET_DEFERRED: str = "budget_deferred"
PRIVACY_BLOCKED: str = "privacy_blocked"
ABSTENTION_REASONS: tuple[str, ...] = (
    NO_SUPPORTED_DESTINATION, LOW_MARGIN, SEMANTIC_ONLY, GENERIC_HUB_ONLY,
    CONFLICTING_FACTS, NO_SHARED_BRANCH, BUDGET_DEFERRED, PRIVACY_BLOCKED,
)

# --- privacy and review ----------------------------------------------------------

LOCAL_ONLY: str = "local_only"
DOSSIER_PERMITTED: str = "dossier_permitted"
REDACTED_ELIGIBILITY: str = "redacted"
MODEL_ELIGIBILITY: tuple[str, ...] = (
    LOCAL_ONLY, DOSSIER_PERMITTED, REDACTED_ELIGIBILITY,
)

AUTO_ELIGIBLE: str = "auto_eligible"
REVIEW_REQUIRED: str = "review_required"
BLOCKED_PENDING_USER: str = "blocked_pending_user"
REVIEW_POLICIES: tuple[str, ...] = (
    AUTO_ELIGIBLE, REVIEW_REQUIRED, BLOCKED_PENDING_USER,
)

# --- §8.7's correction polarity: P1's axis, one value spelled like P8's verdict ---

#: §8.2's polarity, in P1's own words: "polarity ∈ accept | reject and is supplied
#: by the acting part". P1 publishes no constant for either, so P11 spells them.
#:
#: `POLARITY_REJECT` is the same string as P8's verdict outcome `REJECT`, imported
#: above, and is deliberately NOT bound to it. The axes are unrelated: a verdict is
#: what the validator concluded about a response, a polarity is what the user did
#: about a proposal. A module recording a user's rejection must not reach for the
#: verdict constant to spell it, which is the rule this file opens with.
POLARITY_ACCEPT: str = "accept"
POLARITY_REJECT: str = "reject"
POLARITIES: tuple[str, ...] = (POLARITY_ACCEPT, POLARITY_REJECT)

#: Pinned, not shared. If P8 ever respells its verdict this assertion fails and a
#: reader is told the two strings drifted apart, rather than P11 silently
#: following a change that was never about polarity.
assert POLARITY_REJECT == REJECT


# --- residual sets ---------------------------------------------------------------

REVIEW_WITH_MODEL: str = "review_with_model_against_approved_residual_folders"
SEND_TO_APPROVED_NODE: str = "send_to_approved_node"
CREATE_CUSTOM_BRANCH: str = "create_custom_branch"

#: §7.6's four. The first IS the outcome `leave_in_place`, one level up -- a set
#: the user leaves alone and a file left alone are the same decision at two
#: scales, so the constant is reused and not respelled.
SET_CHOICES: tuple[str, ...] = (
    LEAVE_IN_PLACE, REVIEW_WITH_MODEL, SEND_TO_APPROVED_NODE, CREATE_CUSTOM_BRANCH,
)

ROUTED_TO_NODE: str = "node"
ROUTED_TO_REVIEW_QUEUE: str = "review_queue"
OUTLIER_ROUTES: tuple[str, ...] = (ROUTED_TO_NODE, ROUTED_TO_REVIEW_QUEUE)

# --- P2 -------------------------------------------------------------------------

CANDIDATE_NODE_RETRIEVAL: str = "candidate_node_retrieval"
PLACEMENT_SCORING: str = "placement_scoring"
STAGE_IDS: tuple[str, ...] = (CANDIDATE_NODE_RETRIEVAL, PLACEMENT_SCORING)

DIMENSION_PLACEMENT: str = "placement"
DIMENSION_RESIDUAL: str = "residual"
#: §8.5's *"Retrieval quality: for sparse files, did the correct anchors appear in
#: the top candidate neighborhood?"* -- which is what §6.2 does, in the design's
#: own words. P9 already measures its own retrieval stage under this name, and
#: two stages sharing one dimension is the shape §8.5 already has: its ten
#: dimensions are a shorter and separate list from its ten stages on purpose. The
#: two are kept apart by SUBJECT namespace, not by an eleventh dimension.
DIMENSION_RETRIEVAL: str = "retrieval"
DIMENSIONS: tuple[str, ...] = (
    DIMENSION_PLACEMENT, DIMENSION_RESIDUAL, DIMENSION_RETRIEVAL,
)

# --- events ---------------------------------------------------------------------

INDEX_ENTRY_BUILT: str = "placement_index_entry_built"
CANDIDATE_RETRIEVAL: str = "candidate_destination_retrieval"
RECOMMENDATION_EMITTED: str = "placement_recommendation_emitted"
GROUP_PLAN_EMITTED: str = "group_plan_emitted"
RESIDUAL_SET_SURFACED: str = "residual_set_surfaced"
RESIDUAL_SET_DECIDED: str = "residual_set_decision_recorded"
RESIDUAL_RECOMMENDATION_EMITTED: str = "residual_recommendation_emitted"
RETURN_ISSUED: str = "return_to_placement_issued"
REVIEW_DECISION: str = "placement_review_decision"
EVENT_TYPES: tuple[str, ...] = (
    INDEX_ENTRY_BUILT, CANDIDATE_RETRIEVAL, RECOMMENDATION_EMITTED,
    GROUP_PLAN_EMITTED, RESIDUAL_SET_SURFACED, RESIDUAL_SET_DECIDED,
    RESIDUAL_RECOMMENDATION_EMITTED, RETURN_ISSUED, REVIEW_DECISION,
)

#: `rejected` is deliberately absent from `EVIDENCE_TYPES` and named here so the
#: exclusion is a published decision rather than an omission (SPEC:430-432).
DROPPED_RELIABILITY_STATE: str = "rejected"
assert DROPPED_RELIABILITY_STATE in RELIABILITY_STATES
assert DROPPED_RELIABILITY_STATE not in EVIDENCE_TYPES


class OutOfVocabulary(ValueError):
    """A value outside a closed P11 set. Not a fallback; a load error."""


def check(value: object, closed: tuple[str, ...], *, name: str) -> str:
    """One membership test. The closed set is named; the nearest match is not.

    Naming the nearest member would be a suggestion, and a suggestion in a
    vocabulary carrying four strings that also belong to P8 is how a
    misspelling becomes a silent change of axis.
    """
    if not isinstance(value, str) or value not in closed:
        raise OutOfVocabulary(
            f"{name}={value!r} is not one of the {len(closed)} values P11 defines "
            f"for it. Adding a member is a contract revision, not an "
            f"implementation decision."
        )
    return value
