# src/llm_harness/vocabulary.py
"""P8's closed vocabularies, published once.

Downstream code imports the named constants. Tuples exist for iteration and
membership. A value outside a closed set is a load error, not a fallback.

There is no `needs_consent` reason code and none may be added (B2). Consent is
`privacy.release.NeedsConsent`, returned unchanged; it is not an outcome, event, or
P2 row. P8 does not invent `normalize(` or `contradicts(` implementations; those
remain injected capabilities (C-5) and missing ones are `ValidationUnavailable`.
"""
from __future__ import annotations

from types import MappingProxyType

# ---------------------------------------------------------------------------
# Call sites (SPEC envelope spellings)
# ---------------------------------------------------------------------------

A_FACT: str = "A_fact"
B_GROUP: str = "B_group"
C_PLACEMENT: str = "C_placement"
D_RESIDUAL: str = "D_residual"
E_TEMPLATE: str = "E_template"

CALL_SITES: tuple[str, ...] = (
    A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE,
)

# ---------------------------------------------------------------------------
# Outcomes (uniform across sites) and residual actions (site D controlled set)
# ---------------------------------------------------------------------------

ACCEPT_DIRECT: str = "accept_direct"
ACCEPT_CONTEXT_SUPPORTED: str = "accept_context_supported"
WEAK: str = "weak"
REJECT: str = "reject"
ABSTAIN: str = "abstain"

OUTCOMES: tuple[str, ...] = (
    ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED, WEAK, REJECT, ABSTAIN,
)

RETURN_CONFIRMED_GROUP: str = "return_to_confirmed_domain_group"
RETURN_ACCEPTED_PACKET: str = "return_to_accepted_graph_or_purpose_packet"
CHOOSE_RESIDUAL_DESTINATION: str = "choose_approved_residual_destination"
CHOOSE_BROAD_PARENT: str = "choose_approved_broad_parent_branch"
MARK_REVIEW_LATER: str = "mark_review_later"
LEAVE_IN_CURRENT_LOCATION: str = "leave_in_current_location"
MARK_PROTECTED_OR_UNSUPPORTED: str = "mark_protected_or_unsupported"

RESIDUAL_ACTIONS: tuple[str, ...] = (
    RETURN_CONFIRMED_GROUP,
    RETURN_ACCEPTED_PACKET,
    CHOOSE_RESIDUAL_DESTINATION,
    CHOOSE_BROAD_PARENT,
    MARK_REVIEW_LATER,
    LEAVE_IN_CURRENT_LOCATION,
    MARK_PROTECTED_OR_UNSUPPORTED,
    ABSTAIN,
)

# ---------------------------------------------------------------------------
# Reduction ladder, including `none` for an unreduced fitting call
# ---------------------------------------------------------------------------

REDUCTION_NONE: str = "none"
SUMMARIZED_FACTS: str = "summarized_facts"
PRESERVED_ANCHORS: str = "preserved_anchors"
SPLIT: str = "split"
DEFERRED: str = "deferred"

REDUCTION_RUNGS: tuple[str, ...] = (
    REDUCTION_NONE, SUMMARIZED_FACTS, PRESERVED_ANCHORS, SPLIT, DEFERRED,
)

# ---------------------------------------------------------------------------
# Closed eligibility reasons, per site
# ---------------------------------------------------------------------------

REMAINS_AMBIGUOUS: str = "remains_ambiguous"
MULTIPLE_PLAUSIBLE_DOMAINS: str = "multiple_plausible_domains"
LANGUAGE_REQUIRES_INTERPRETATION: str = "language_requires_interpretation"

FACT_ELIGIBILITY: tuple[str, ...] = (
    REMAINS_AMBIGUOUS,
    MULTIPLE_PLAUSIBLE_DOMAINS,
    LANGUAGE_REQUIRES_INTERPRETATION,
)

COHERENCE_JUDGEMENT: str = "coherence_judgement"
MEMBERSHIP_JUDGEMENT: str = "membership_judgement"
OUTLIER_JUDGEMENT: str = "outlier_judgement"
LABEL_JUDGEMENT: str = "label_judgement"

GROUP_ELIGIBILITY: tuple[str, ...] = (
    COHERENCE_JUDGEMENT,
    MEMBERSHIP_JUDGEMENT,
    OUTLIER_JUDGEMENT,
    LABEL_JUDGEMENT,
)

SEVERAL_LEGAL_NODES_PLAUSIBLE: str = "several_legal_nodes_plausible"
CONTEXT_MEMBER_MISSING_BRANCH_FACT: str = "context_member_missing_branch_fact"
PLACE_GROUP_TOGETHER: str = "place_group_together"
CUSTOM_TEMPLATE_SEMANTIC_INTERPRETATION: str = (
    "custom_template_semantic_interpretation"
)
VAGUE_OCR_OR_FILENAME: str = "vague_ocr_or_filename"
DIRECT_FACTS_CONFLICT: str = "direct_facts_conflict"

PLACEMENT_ELIGIBILITY: tuple[str, ...] = (
    SEVERAL_LEGAL_NODES_PLAUSIBLE,
    CONTEXT_MEMBER_MISSING_BRANCH_FACT,
    PLACE_GROUP_TOGETHER,
    CUSTOM_TEMPLATE_SEMANTIC_INTERPRETATION,
    VAGUE_OCR_OR_FILENAME,
    DIRECT_FACTS_CONFLICT,
)

USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW: str = (
    "user_opted_residual_set_into_ai_review"
)
RESIDUAL_ELIGIBILITY: tuple[str, ...] = (USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW,)

ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE: str = (
    "accepted_group_fits_no_existing_template"
)
TEMPLATE_ELIGIBILITY: tuple[str, ...] = (ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE,)

ALL_ELIGIBILITY: tuple[str, ...] = (
    FACT_ELIGIBILITY
    + GROUP_ELIGIBILITY
    + PLACEMENT_ELIGIBILITY
    + RESIDUAL_ELIGIBILITY
    + TEMPLATE_ELIGIBILITY
)

ELIGIBILITY_BY_SITE: MappingProxyType[str, tuple[str, ...]] = MappingProxyType({
    A_FACT: FACT_ELIGIBILITY,
    B_GROUP: GROUP_ELIGIBILITY,
    C_PLACEMENT: PLACEMENT_ELIGIBILITY,
    D_RESIDUAL: RESIDUAL_ELIGIBILITY,
    E_TEMPLATE: TEMPLATE_ELIGIBILITY,
})

SITES_REQUIRING_PLAN_VERSION: frozenset[str] = frozenset(
    {C_PLACEMENT, D_RESIDUAL, E_TEMPLATE}
)

#: `record_cd_verdict` refuses a C or D verdict without one. Named here so the
#: requirement can be checked before a call is reserved rather than after it is
#: paid for.
SITES_REQUIRING_EVIDENCE_SNAPSHOT: frozenset[str] = frozenset(
    {C_PLACEMENT, D_RESIDUAL}
)

# ---------------------------------------------------------------------------
# Reason-code registry (SPEC spellings). Named constant == string value.
# ---------------------------------------------------------------------------

SCHEMA_INVALID: str = "SCHEMA_INVALID"
UNCITED_CLAIM: str = "UNCITED_CLAIM"
CITATION_NOT_IN_DOSSIER: str = "CITATION_NOT_IN_DOSSIER"
CITATION_NOT_FOUND: str = "CITATION_NOT_FOUND"
CITATION_SPAN_MISMATCH: str = "CITATION_SPAN_MISMATCH"
CONTRADICTED_BY_STRONGER: str = "CONTRADICTED_BY_STRONGER"
NOT_ELIGIBLE_FOR_MODEL: str = "NOT_ELIGIBLE_FOR_MODEL"
PRIVACY_GATE_REFUSED: str = "PRIVACY_GATE_REFUSED"
BUDGET_EXHAUSTED: str = "BUDGET_EXHAUSTED"
USER_REJECTED_EQUIVALENT: str = "USER_REJECTED_EQUIVALENT"

UNIVERSAL_REASON_CODES: tuple[str, ...] = (
    SCHEMA_INVALID,
    UNCITED_CLAIM,
    CITATION_NOT_IN_DOSSIER,
    CITATION_NOT_FOUND,
    CITATION_SPAN_MISMATCH,
    CONTRADICTED_BY_STRONGER,
    NOT_ELIGIBLE_FOR_MODEL,
    PRIVACY_GATE_REFUSED,
    BUDGET_EXHAUSTED,
    USER_REJECTED_EQUIVALENT,
)

FIELD_NOT_IN_ACTIVE_SCHEMA: str = "FIELD_NOT_IN_ACTIVE_SCHEMA"
VALUE_NOT_NORMALIZABLE: str = "VALUE_NOT_NORMALIZABLE"
SEARCH_HINT_ONLY: str = "SEARCH_HINT_ONLY"

SITE_A_REASON_CODES: tuple[str, ...] = (
    FIELD_NOT_IN_ACTIVE_SCHEMA,
    VALUE_NOT_NORMALIZABLE,
    SEARCH_HINT_ONLY,
)

TERM_MERGE_UNSUPPORTED: str = "TERM_MERGE_UNSUPPORTED"
CONFLICTING_TARGET_INSTITUTION: str = "CONFLICTING_TARGET_INSTITUTION"
INVENTED_DATE: str = "INVENTED_DATE"
INVENTED_PROJECT: str = "INVENTED_PROJECT"
INVENTED_PURPOSE: str = "INVENTED_PURPOSE"
INVENTED_MEMBERSHIP: str = "INVENTED_MEMBERSHIP"
LABEL_WITHOUT_COHERENCE: str = "LABEL_WITHOUT_COHERENCE"
FOLDER_HIERARCHY_PROPOSED: str = "FOLDER_HIERARCHY_PROPOSED"
CONTEXT_ONLY_SUPPORT: str = "CONTEXT_ONLY_SUPPORT"
GENERIC_SIMILARITY_ONLY: str = "GENERIC_SIMILARITY_ONLY"

SITE_B_REASON_CODES: tuple[str, ...] = (
    TERM_MERGE_UNSUPPORTED,
    CONFLICTING_TARGET_INSTITUTION,
    INVENTED_DATE,
    INVENTED_PROJECT,
    INVENTED_PURPOSE,
    INVENTED_MEMBERSHIP,
    LABEL_WITHOUT_COHERENCE,
    FOLDER_HIERARCHY_PROPOSED,
    CONTEXT_ONLY_SUPPORT,
    GENERIC_SIMILARITY_ONLY,
)

NODE_NOT_IN_FROZEN_TREE: str = "NODE_NOT_IN_FROZEN_TREE"
INVENTED_INSTITUTION: str = "INVENTED_INSTITUTION"
INVENTED_NODE: str = "INVENTED_NODE"
SLOT_FILLED_WITHOUT_EVIDENCE: str = "SLOT_FILLED_WITHOUT_EVIDENCE"
CONFLICT_IGNORED: str = "CONFLICT_IGNORED"
SENSITIVITY_POLICY_VIOLATION: str = "SENSITIVITY_POLICY_VIOLATION"
BELOW_SUPPORT_THRESHOLD: str = "BELOW_SUPPORT_THRESHOLD"
INSUFFICIENT_MARGIN: str = "INSUFFICIENT_MARGIN"
GENERIC_HUB_ONLY: str = "GENERIC_HUB_ONLY"

SITE_C_REASON_CODES: tuple[str, ...] = (
    NODE_NOT_IN_FROZEN_TREE,
    INVENTED_DATE,
    INVENTED_INSTITUTION,
    INVENTED_PROJECT,
    INVENTED_NODE,
    SLOT_FILLED_WITHOUT_EVIDENCE,
    CONFLICT_IGNORED,
    SENSITIVITY_POLICY_VIOLATION,
    BELOW_SUPPORT_THRESHOLD,
    INSUFFICIENT_MARGIN,
    GENERIC_HUB_ONLY,
)

ACTION_NOT_IN_CONTROLLED_SET: str = "ACTION_NOT_IN_CONTROLLED_SET"
DESTINATION_NOT_IN_FROZEN_TREE: str = "DESTINATION_NOT_IN_FROZEN_TREE"
EVIDENCE_NOT_IN_FILE_RECORD: str = "EVIDENCE_NOT_IN_FILE_RECORD"
SENSITIVITY_RESTRICTION_IGNORED: str = "SENSITIVITY_RESTRICTION_IGNORED"
STRONGER_RELATIONSHIP_OVERLOOKED: str = "STRONGER_RELATIONSHIP_OVERLOOKED"
INVENTED_FOLDER: str = "INVENTED_FOLDER"

SITE_D_REASON_CODES: tuple[str, ...] = (
    ACTION_NOT_IN_CONTROLLED_SET,
    DESTINATION_NOT_IN_FROZEN_TREE,
    EVIDENCE_NOT_IN_FILE_RECORD,
    SENSITIVITY_RESTRICTION_IGNORED,
    STRONGER_RELATIONSHIP_OVERLOOKED,
    INVENTED_FOLDER,
)


def _unique(*groups: tuple[str, ...]) -> tuple[str, ...]:
    seen: list[str] = []
    for group in groups:
        for member in group:
            if member not in seen:
                seen.append(member)
    return tuple(seen)


ALL_REASON_CODES: tuple[str, ...] = _unique(
    UNIVERSAL_REASON_CODES,
    SITE_A_REASON_CODES,
    SITE_B_REASON_CODES,
    SITE_C_REASON_CODES,
    SITE_D_REASON_CODES,
)

PRE_CALL_REASON_CODES: tuple[str, ...] = (
    NOT_ELIGIBLE_FOR_MODEL,
    BUDGET_EXHAUSTED,
    USER_REJECTED_EQUIVALENT,
)

# ---------------------------------------------------------------------------
# Evidence basis (P9 spelling) and verdict scope
# ---------------------------------------------------------------------------

DIRECT_ANCHOR: str = "direct-anchor"
CONTEXT_SUPPORTED: str = "context-supported"
EVIDENCE_BASES: tuple[str, ...] = (DIRECT_ANCHOR, CONTEXT_SUPPORTED)

SCOPE_FILE: str = "file"
SCOPE_GROUP: str = "group"
SCOPE_NODE: str = "node"
SCOPE_TEMPLATE: str = "template"
SCOPE_DOMAIN: str = "domain"
SCOPE_CORPUS: str = "corpus"

VERDICT_SCOPES: tuple[str, ...] = (
    SCOPE_FILE, SCOPE_GROUP, SCOPE_NODE, SCOPE_TEMPLATE, SCOPE_DOMAIN, SCOPE_CORPUS,
)

# ---------------------------------------------------------------------------
# Dispositions: SPEC outcome → what the owning part does, per site.
# Not a second copy of OUTCOMES.
# ---------------------------------------------------------------------------

LLM_SUPPORTED: str = "llm_supported"
LLM_SUPPORTED_REVIEW: str = "llm_supported_review"
POSSIBLE: str = "possible"
REJECTED: str = "rejected"
NO_FACT: str = "no_fact"
DIRECT_MEMBERSHIP: str = "direct_membership"
CONTEXT_SUPPORTED_MEMBERSHIP: str = "context_supported_membership"
UNRESOLVED: str = "unresolved"
MOVE_PLAN_ELIGIBLE: str = "move_plan_eligible"
VALID_REVIEW_REQUIRED: str = "valid_review_required"
NO_DESTINATION: str = "no_destination"
NO_SUPPORTED_DESTINATION: str = "no_supported_destination"
RETURN_TO_PLACEMENT: str = "return_to_placement"
RESIDUAL_DESTINATION: str = "residual_destination"
RESIDUAL_DESTINATION_REVIEW: str = "residual_destination_review"
REVIEW_LATER: str = "review_later"
LEAVE_IN_PLACE: str = "leave_in_place"

DISPOSITIONS: tuple[str, ...] = (
    LLM_SUPPORTED,
    LLM_SUPPORTED_REVIEW,
    POSSIBLE,
    REJECTED,
    NO_FACT,
    DIRECT_MEMBERSHIP,
    CONTEXT_SUPPORTED_MEMBERSHIP,
    UNRESOLVED,
    MOVE_PLAN_ELIGIBLE,
    VALID_REVIEW_REQUIRED,
    NO_DESTINATION,
    NO_SUPPORTED_DESTINATION,
    RETURN_TO_PLACEMENT,
    RESIDUAL_DESTINATION,
    RESIDUAL_DESTINATION_REVIEW,
    REVIEW_LATER,
    LEAVE_IN_PLACE,
    ABSTAIN,
)
