# src/grouping/vocabulary.py
"""P9's closed vocabularies. Named constant == string value, one home each.

Two of these are one word apart and mean different things. `Membership.basis` is
the direct / context / user axis, and it is the vocabulary P8's dossier
`evidence_items[].basis` draws from. `Membership.support[].support_kind` is the
retrieval channel a support came through. The SPEC says twice not to merge them.

P9 publishes no verdict enum. P8's `outcome` registry plus `reasons[]` is the one
vocabulary for whether a membership is valid, and it carries two outcomes P9 had
no word for (`weak`, `abstain`).

No destination, node, tree, placement, branch or template concept lives here.
"""
from __future__ import annotations

# --- group lifecycle ------------------------------------------------------------
#
# The SHARED lifecycle only. `accepted` and `rejected` are resolved as of a plan
# version from `group_acceptance` and are never stored on a group.

CANDIDATE: str = "candidate"
SUPPORTED: str = "supported"
TENTATIVE_DISCOVERY: str = "tentative-discovery"
UNRESOLVED: str = "unresolved"

GROUP_STATES: tuple[str, ...] = (
    CANDIDATE, SUPPORTED, TENTATIVE_DISCOVERY, UNRESOLVED,
)

#: The two values `group_state_as_of` adds at read time. Never stored.
PLAN_VERSIONED_STATES: tuple[str, ...] = ("accepted", "rejected")

#: Every value `group_state_as_of` may return.
GROUP_STATES_AS_OF: tuple[str, ...] = GROUP_STATES + PLAN_VERSIONED_STATES

# --- seeds ----------------------------------------------------------------------

STRONGLY_IDENTIFIED_FILE: str = "strongly-identified-file"
VALIDATED_SHARED_FACT: str = "validated-shared-fact"
STRUCTURAL_FAMILY: str = "structural-family"
USER_CREATED_STARTING_POINT: str = "user-created-starting-point"

SEED_KINDS: tuple[str, ...] = (
    STRONGLY_IDENTIFIED_FILE, VALIDATED_SHARED_FACT, STRUCTURAL_FAMILY,
    USER_CREATED_STARTING_POINT,
)

# --- membership -----------------------------------------------------------------

DIRECT_ANCHOR: str = "direct-anchor"
CONTEXT_SUPPORTED: str = "context-supported"
USER_ATTACHED: str = "user-attached"

MEMBERSHIP_BASES: tuple[str, ...] = (DIRECT_ANCHOR, CONTEXT_SUPPORTED, USER_ATTACHED)

INCLUDED: str = "included"
EXCLUDED: str = "excluded"
UNCERTAIN: str = "uncertain"

MEMBERSHIP_DECISIONS: tuple[str, ...] = (INCLUDED, EXCLUDED, UNCERTAIN)

RULES: str = "rules"
LLM: str = "llm"
VALIDATOR: str = "validator"
USER: str = "user"

DECISION_SOURCES: tuple[str, ...] = (RULES, LLM, VALIDATOR, USER)

ENGINE_FLAGGED: str = "engine-flagged"
MODEL_FLAGGED: str = "model-flagged"
BOTH_FLAGGED: str = "both"
NOT_FLAGGED: str = "none"

OUTLIER_FLAGS: tuple[str, ...] = (
    ENGINE_FLAGGED, MODEL_FLAGGED, BOTH_FLAGGED, NOT_FLAGGED,
)

# --- a borrowed value, named because it collides ---------------------------------
#
# P1 stores `scan_state = "included"` to mean "this file is in the corpus". P9's
# `INCLUDED` above means "this member is in the group". Same spelling, different
# concepts, different owners — the `support_kind` / `basis` collision one layer up.
#
# P1 and P3 publish no named constant for it: in all of `src/` the string appears
# only as a literal at call sites. P9 gives it one home rather than a second
# literal, and a name that cannot be mistaken for the membership decision.

P1_INCLUDED_SCAN_STATE: str = "included"


# --- retrieval channels ---------------------------------------------------------
#
# `support_kind`, NOT `basis`. Six channels; a membership carries one or more.

SHARED_VALIDATED_FACT: str = "shared-validated-fact"
DUPLICATE_OR_VERSION_LINK: str = "duplicate-or-version-link"
COMPATIBLE_DOCUMENT_TYPE: str = "compatible-document-type"
EXISTING_RELATED_FOLDER: str = "existing-related-folder"
BOUNDED_SESSION: str = "bounded-session"
MUTUAL_SEMANTIC_RETRIEVAL: str = "mutual-semantic-retrieval"

SUPPORT_KINDS: tuple[str, ...] = (
    SHARED_VALIDATED_FACT, DUPLICATE_OR_VERSION_LINK, COMPATIBLE_DOCUMENT_TYPE,
    EXISTING_RELATED_FOLDER, BOUNDED_SESSION, MUTUAL_SEMANTIC_RETRIEVAL,
)

#: The two channels that can never make a membership `direct-anchor`, and can
#: never by themselves make a group `supported` (SR2).
NON_ANCHORING_SUPPORT: tuple[str, ...] = (
    MUTUAL_SEMANTIC_RETRIEVAL, BOUNDED_SESSION,
)

# --- typed edges ----------------------------------------------------------------
#
# Seven, not six: retrieval's `duplicate-or-version-link` is one channel, and the
# graph distinguishes a `duplicate` from a `version-family` edge.

DUPLICATE: str = "duplicate"
VERSION_FAMILY: str = "version-family"

EDGE_TYPES: tuple[str, ...] = (
    SHARED_VALIDATED_FACT, DUPLICATE, VERSION_FAMILY, COMPATIBLE_DOCUMENT_TYPE,
    EXISTING_RELATED_FOLDER, BOUNDED_SESSION, MUTUAL_SEMANTIC_RETRIEVAL,
)

# --- coherence and labels -------------------------------------------------------

COHERENT: str = "coherent"
NOT_COHERENT: str = "not-coherent"
ABSTAINED: str = "abstained"

COHERENCE_VERDICTS: tuple[str, ...] = (COHERENT, NOT_COHERENT, ABSTAINED)

ENGINE: str = "engine"
LLM_PROPOSED: str = "llm-proposed"
USER_EDITED: str = "user-edited"

LABEL_SOURCES: tuple[str, ...] = (ENGINE, LLM_PROPOSED, USER_EDITED)

RULES_AND_GRAPH: str = "rules+graph"

CREATED_BY: tuple[str, ...] = (RULES, RULES_AND_GRAPH, USER)

# --- stop rules -----------------------------------------------------------------

SR1: str = "SR1"
SR2: str = "SR2"
SR3: str = "SR3"
SR4: str = "SR4"
SR5: str = "SR5"
SR6: str = "SR6"

STOP_RULES: tuple[str, ...] = (SR1, SR2, SR3, SR4, SR5, SR6)

NO_GROUP: str = "no-group"

STOP_RULE_OUTCOMES: tuple[str, ...] = (NO_GROUP, TENTATIVE_DISCOVERY)

# --- failure points -------------------------------------------------------------
#
# Six stages, logged separately. A bad group can fail because retrieval brought
# irrelevant neighbours, because the model overgeneralised, or because the label
# was simply not useful, and a collapsed error class cannot tell them apart.

RETRIEVAL: str = "retrieval"
GRAPH: str = "graph"
INTERPRETATION: str = "interpretation"
VALIDATION: str = "validation"
LABEL: str = "label"
USER_REJECTION: str = "user-rejection"

FAILURE_STAGES: tuple[str, ...] = (
    RETRIEVAL, GRAPH, INTERPRETATION, VALIDATION, LABEL, USER_REJECTION,
)

DETECTED_BY: tuple[str, ...] = (VALIDATOR, USER, "replay")

# --- acceptance, per plan version -----------------------------------------------

ACCEPTED: str = "accepted"
REJECTED: str = "rejected"
PENDING_REVIEW: str = "pending-review"
DEFERRED: str = "deferred"

ACCEPTANCES: tuple[str, ...] = (ACCEPTED, REJECTED, PENDING_REVIEW, DEFERRED)

NOT_REQUIRED: str = "not-required"
USER_ACCEPTED: str = "user-accepted"
USER_REJECTED: str = "user-rejected"
USER_EXCLUDED_FROM_PACKET: str = "user-excluded-from-packet"

REVIEW_STATES: tuple[str, ...] = (
    NOT_REQUIRED, PENDING_REVIEW, USER_ACCEPTED, USER_REJECTED,
    USER_EXCLUDED_FROM_PACKET, DEFERRED,
)

DECIDED_BY: tuple[str, ...] = (USER, RULES, VALIDATOR)


# --- SR6's equivalence classes ---------------------------------------------------
#
# What "the same proposal" means, for the two things a user can reject. Spelled
# once: P8's `suppressed_by_learning`, P9's SR6 and P9's review receiver all match
# on these, and two spellings would mean a rejection the user made and a rejection
# the stop rule looks for that never meet.

GROUP_PROPOSAL_CLASS: str = "group"
MEMBERSHIP_PROPOSAL_CLASS: str = "membership"

PROPOSAL_CLASSES: tuple[str, ...] = (
    GROUP_PROPOSAL_CLASS, MEMBERSHIP_PROPOSAL_CLASS,
)


class OutOfVocabulary(ValueError):
    """A value outside a closed P9 set. Not a fallback; a load error."""


def check(value: object, closed: tuple[str, ...], *, name: str) -> str:
    """One membership test. The closed set is named, the nearest match is not.

    Naming the nearest member would be a suggestion, and a suggestion in a
    vocabulary this size is how a misspelling becomes a silent downgrade.
    """
    if not isinstance(value, str) or value not in closed:
        raise OutOfVocabulary(
            f"{name}={value!r} is not one of the {len(closed)} values P9 defines "
            f"for it. Adding a member is a contract revision, not an "
            f"implementation decision."
        )
    return value
