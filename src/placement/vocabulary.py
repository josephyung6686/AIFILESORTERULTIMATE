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
from eval_harness.vocabulary import (
    BUDGET_STATES as P2_BUDGET_STATES,
    OUTCOMES as P2_ENVELOPE_OUTCOMES,
)
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
# P10's node vocabulary, aliased on import. Four of its names collide with a P11
# axis -- `RESIDUAL`, `PROTECTED`, `LEAVE_IN_PLACE` and `EXISTING` all mean
# something else here -- so each arrives under a `P10_` name and is rebound below
# to the P11 name that says which axis it is on. An unaliased import would
# silently shadow P11's own constant with P10's.
from tree_design.vocabulary import (
    EXISTING as P10_EXISTING,
    IGNORED as P10_IGNORED,
    LEAVE_IN_PLACE as P10_LEAVE_IN_PLACE,
    NODE_ROLES as P10_NODE_ROLES,
    NODE_TYPES as P10_NODE_TYPES,
    ORDINARY as P10_ORDINARY,
    PHYSICAL_DESTINATION as P10_PHYSICAL_DESTINATION,
    PROPOSED as P10_PROPOSED,
    PROTECTED as P10_PROTECTED,
    RESIDUAL as P10_RESIDUAL_ROLE,
    RESIDUAL_DISPOSITIONS as P10_RESIDUAL_DISPOSITIONS,
    REVIEW_ONLY as P10_REVIEW_ONLY,
    SCOPED_GENERAL as P10_SCOPED_GENERAL,
    SHARED_MATERIAL as P10_SHARED_MATERIAL,
    USER_CREATED as P10_USER_CREATED,
)

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
# P10's vocabulary, carried verbatim on the node (SPEC:322-323, MINOR 6): "P10
# owns the tree, so P10 names its node kinds. P11 carries these verbatim and
# publishes no parallel vocabulary." This block spelled the values from P10's
# SPEC while P10 was unbuilt, and said in this comment that it would become a
# re-export the day P10 published them. P10 has, so it is one.
#
# The three closed sets are P10's OBJECTS, not tuples that agree with P10's. A
# tuple that merely agrees is one P10 edit away from disagreeing, and the day it
# did, `index.py` would refuse a node role P10 had just added -- reported as a
# malformed tree rather than as two parts holding different lists.
#
# The NAMES are P11's, and deliberately. `RESIDUAL_ROLE`,
# `LEAVE_IN_PLACE_DISPOSITION` and `PROTECTED_NODE` exist because P11 has its own
# `RESIDUAL` origin stage, `LEAVE_IN_PLACE` outcome and `PROTECTED` marked state
# on unrelated axes, and this module's opening rule is that a module reading one
# axis must never reach for the other's constant. A distinct name bound to P10's
# object is carrying; a distinct name bound to a fresh string is the parallel
# vocabulary MINOR 6 forbids.

ORDINARY: str = P10_ORDINARY
SCOPED_GENERAL: str = P10_SCOPED_GENERAL
RESIDUAL_ROLE: str = P10_RESIDUAL_ROLE
SHARED_MATERIAL: str = P10_SHARED_MATERIAL
NODE_ROLES: tuple[str, ...] = P10_NODE_ROLES

PHYSICAL_DESTINATION: str = P10_PHYSICAL_DESTINATION
REVIEW_ONLY: str = P10_REVIEW_ONLY
#: P10 hyphenates its dispositions; P8 -- whose value P11's `LEAVE_IN_PLACE`
#: OUTCOME is -- underscores. The two are not the same string and must not be
#: bound to one another; the assertion below says so rather than leaving it to a
#: reader to notice.
LEAVE_IN_PLACE_DISPOSITION: str = P10_LEAVE_IN_PLACE
DISPOSITIONS: tuple[str, ...] = P10_RESIDUAL_DISPOSITIONS

EXISTING: str = P10_EXISTING
PROPOSED: str = P10_PROPOSED
USER_CREATED: str = P10_USER_CREATED
PROTECTED_NODE: str = P10_PROTECTED
IGNORED: str = P10_IGNORED
NODE_TYPES: tuple[str, ...] = P10_NODE_TYPES

#: Pinned, not bound. P10's disposition and P8's outcome are two different
#: strings for two different concepts, and an editor who "fixed" the
#: inconsistency by binding one to the other would silently respell a value one
#: of the two owners publishes.
assert LEAVE_IN_PLACE_DISPOSITION != LEAVE_IN_PLACE

assert set(NODE_ROLES) == {ORDINARY, SCOPED_GENERAL, RESIDUAL_ROLE, SHARED_MATERIAL}
assert set(DISPOSITIONS) == {PHYSICAL_DESTINATION, REVIEW_ONLY,
                             LEAVE_IN_PLACE_DISPOSITION}
assert set(NODE_TYPES) == {EXISTING, PROPOSED, USER_CREATED, PROTECTED_NODE,
                           IGNORED}

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

#: §6.10's margin failure told apart from itself. `low_margin` is a complaint
#: about EVIDENCE -- the best destination is not clearly better than a rival the
#: evidence never supported -- and this is the opposite situation: two or more
#: destinations each cleared the support threshold on their own, and nothing
#: separates them. A research paper that is also school homework is the case, and
#: the two sentences ask the user for different things. One says the product is
#: unsure about the file; this one says the file has more than one right home and
#: the choice belongs to the person. `scoring._reason` decides which is true and
#: `tests/p11/test_p11_scoring.py` pins both halves, because a fix that renamed
#: every margin failure would pass the second and destroy the first.
MULTIPLE_SUPPORTED_HOMES: str = "multiple_supported_homes"

SEMANTIC_ONLY: str = "semantic_only"
GENERIC_HUB_ONLY: str = "generic_hub_only"
CONFLICTING_FACTS: str = "conflicting_facts"
NO_SHARED_BRANCH: str = "no_shared_branch"
BUDGET_DEFERRED: str = "budget_deferred"
PRIVACY_BLOCKED: str = "privacy_blocked"
ABSTENTION_REASONS: tuple[str, ...] = (
    NO_SUPPORTED_DESTINATION, LOW_MARGIN, MULTIPLE_SUPPORTED_HOMES,
    SEMANTIC_ONLY, GENERIC_HUB_ONLY, CONFLICTING_FACTS, NO_SHARED_BRANCH,
    BUDGET_DEFERRED, PRIVACY_BLOCKED,
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


# --- P13's review action: the surfaces and actions P13 routes to P11 --------------
#
# P13 is specification only -- its three event types are registered and no producer
# exists -- so these are spelled here from P13 SPEC:264-294 and this module is
# their one home until P13 publishes them, exactly as P10's node vocabulary is
# above. `placement/review.py` imports them and spells none.

SURFACE_PLACEMENT: str = "placement"
SURFACE_GROUP_PLAN: str = "group_plan"
SURFACE_RESIDUAL_SET: str = "residual_set"
SURFACE_RESIDUAL_FILE: str = "residual_file"

#: P13 SPEC:294's four. A fifth would be P13 routing a surface P11 does not own.
REVIEW_SURFACES: tuple[str, ...] = (
    SURFACE_PLACEMENT, SURFACE_GROUP_PLAN, SURFACE_RESIDUAL_SET,
    SURFACE_RESIDUAL_FILE,
)

#: Pinned, not shared: the surface named `placement` and the origin stage named
#: `placement` are different axes that happen to share a spelling, and a module
#: reading a surface must not reach for the origin-stage constant to spell it.
assert SURFACE_PLACEMENT == PLACEMENT

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

#: The subset of P13's actions a placement or residual surface collects.
#: `adopt_version`, `restore_version`, `select_consent_option`, `set_redaction`,
#: `refresh_plan`, `approve_for_apply` and `reset_learning` route elsewhere and
#: are deliberately absent -- an action outside this set reaching P11 is a routing
#: error, not an action P11 has no branch for.
REVIEW_ACTIONS: tuple[str, ...] = (
    ACTION_ACCEPT, ACTION_ACCEPT_BULK, ACTION_CHANGE_DESTINATION,
    ACTION_RETURN_TO_ACCEPTED_GROUP, ACTION_CREATE_CUSTOM_FOLDER,
    ACTION_MARK_PRIVATE, ACTION_DEFER, ACTION_LEAVE_UNTOUCHED, ACTION_REJECT,
    ACTION_EDIT_RECOMMENDATION, ACTION_DISABLE_SUGGESTION_TYPE,
)

#: Two more collisions, pinned rather than bound. An ACTION is what the user did;
#: a POLARITY is what P11 recorded about it. They agree today for exactly these
#: two names, and `defer` proves they are not the same axis: it is an action with
#: no polarity at all.
assert ACTION_ACCEPT == POLARITY_ACCEPT
assert ACTION_REJECT == POLARITY_REJECT
assert ACTION_DEFER not in POLARITIES

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

#: P2's envelope vocabulary, which is a DIFFERENT vocabulary from `OUTCOMES`
#: above: `OUTCOMES` are values of P11's own record and P2 refuses every one of
#: them in an envelope (`eval_harness/stage_output.py`'s `_FOREIGN_OUTCOMES`).
#: P2 publishes the closed tuples and no named constant per member, so these are
#: spelled here and pinned against P2's own tuples -- the same shape
#: `grouping/vocabulary.py` uses for the identical problem. `not_implemented` and
#: `error` are P2's and deliberately absent: P11 is built, and a stage that raised
#: never reaches a writer at all.
P2_PRODUCED: str = "produced"
P2_ABSTAINED: str = "abstained"
P2_DEFERRED: str = "deferred"
P2_WITHIN_CEILING: str = "within_ceiling"
P2_CEILING_REACHED: str = "ceiling_reached"

assert {P2_PRODUCED, P2_ABSTAINED, P2_DEFERRED} <= set(P2_ENVELOPE_OUTCOMES)
assert {P2_WITHIN_CEILING, P2_CEILING_REACHED} == set(P2_BUDGET_STATES)
#: The pairing §8.6 forbids: a ceiling-reached stage is `deferred`, never
#: `abstained`. Named here so the exclusion is a published decision rather than an
#: absence, and so the two spellings cannot quietly become one string.
assert P2_DEFERRED != P2_ABSTAINED

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
