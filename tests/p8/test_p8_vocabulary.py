"""P8 closed vocabularies: named constants once, tuples composed from those constants."""
from __future__ import annotations

import dataclasses

from llm_harness.vocabulary import (
    A_FACT,
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE,
    ACTION_NOT_IN_CONTROLLED_SET,
    ALL_ELIGIBILITY,
    ALL_REASON_CODES,
    B_GROUP,
    BELOW_SUPPORT_THRESHOLD,
    BUDGET_EXHAUSTED,
    C_PLACEMENT,
    CALL_SITES,
    CHOOSE_BROAD_PARENT,
    CHOOSE_RESIDUAL_DESTINATION,
    CITATION_NOT_FOUND,
    CITATION_NOT_IN_DOSSIER,
    CITATION_SPAN_MISMATCH,
    COHERENCE_JUDGEMENT,
    CONFLICT_IGNORED,
    CONFLICTING_TARGET_INSTITUTION,
    CONTEXT_MEMBER_MISSING_BRANCH_FACT,
    CONTEXT_ONLY_SUPPORT,
    CONTEXT_SUPPORTED,
    CONTEXT_SUPPORTED_MEMBERSHIP,
    CONTRADICTED_BY_STRONGER,
    CUSTOM_TEMPLATE_SEMANTIC_INTERPRETATION,
    D_RESIDUAL,
    DEFERRED,
    DESTINATION_NOT_IN_FROZEN_TREE,
    DIRECT_ANCHOR,
    DIRECT_FACTS_CONFLICT,
    DIRECT_MEMBERSHIP,
    DISPOSITIONS,
    E_TEMPLATE, F_ROLE_SHORTLIST,
    EVIDENCE_BASES,
    EVIDENCE_NOT_IN_FILE_RECORD,
    FACT_ELIGIBILITY,
    FIELD_NOT_IN_ACTIVE_SCHEMA,
    FOLDER_HIERARCHY_PROPOSED,
    GENERIC_HUB_ONLY,
    GENERIC_SIMILARITY_ONLY,
    GROUP_ELIGIBILITY,
    INSUFFICIENT_MARGIN,
    INVENTED_DATE,
    INVENTED_FOLDER,
    INVENTED_INSTITUTION,
    INVENTED_MEMBERSHIP,
    INVENTED_NODE,
    INVENTED_PROJECT,
    INVENTED_PURPOSE,
    LABEL_JUDGEMENT,
    LABEL_WITHOUT_COHERENCE,
    LANGUAGE_REQUIRES_INTERPRETATION,
    LEAVE_IN_CURRENT_LOCATION,
    LEAVE_IN_PLACE,
    LLM_SUPPORTED,
    LLM_SUPPORTED_REVIEW,
    MARK_PROTECTED_OR_UNSUPPORTED,
    MARK_REVIEW_LATER,
    MEMBERSHIP_JUDGEMENT,
    MOVE_PLAN_ELIGIBLE,
    MULTIPLE_PLAUSIBLE_DOMAINS,
    NO_DESTINATION,
    NO_FACT,
    NO_SUPPORTED_DESTINATION,
    NODE_NOT_IN_FROZEN_TREE,
    NOT_ELIGIBLE_FOR_MODEL,
    OUTCOMES,
    OUTLIER_JUDGEMENT,
    PLACE_GROUP_TOGETHER,
    PLACEMENT_ELIGIBILITY,
    POSSIBLE,
    PRESERVED_ANCHORS,
    PRIVACY_GATE_REFUSED,
    REDUCTION_NONE,
    REDUCTION_RUNGS,
    REJECT,
    REJECTED,
    REMAINS_AMBIGUOUS,
    RESIDUAL_ACTIONS,
    RESIDUAL_DESTINATION,
    RESIDUAL_DESTINATION_REVIEW,
    RESIDUAL_ELIGIBILITY,
    RETURN_ACCEPTED_PACKET,
    RETURN_CONFIRMED_GROUP,
    RETURN_TO_PLACEMENT,
    REVIEW_LATER,
    SCHEMA_INVALID,
    SCOPE_CORPUS,
    SCOPE_DOMAIN,
    SCOPE_FILE,
    SCOPE_GROUP,
    SCOPE_NODE,
    SCOPE_TEMPLATE,
    SEARCH_HINT_ONLY,
    SENSITIVITY_POLICY_VIOLATION,
    SENSITIVITY_RESTRICTION_IGNORED,
    SEVERAL_LEGAL_NODES_PLAUSIBLE,
    SITE_A_REASON_CODES,
    SITE_B_REASON_CODES,
    SITE_C_REASON_CODES,
    SITE_D_REASON_CODES,
    SLOT_FILLED_WITHOUT_EVIDENCE,
    SPLIT,
    STRONGER_RELATIONSHIP_OVERLOOKED,
    SUMMARIZED_FACTS,
    TEMPLATE_ELIGIBILITY,
    TERM_MERGE_UNSUPPORTED,
    UNCITED_CLAIM,
    UNIVERSAL_REASON_CODES,
    UNRESOLVED,
    USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW,
    USER_REJECTED_EQUIVALENT,
    VAGUE_OCR_OR_FILENAME,
    VALID_REVIEW_REQUIRED,
    VALUE_NOT_NORMALIZABLE,
    VERDICT_SCOPES,
    WEAK,
)


def test_call_sites_are_the_spec_envelope_spellings():
    assert A_FACT == "A_fact"
    assert B_GROUP == "B_group"
    assert C_PLACEMENT == "C_placement"
    assert D_RESIDUAL == "D_residual"
    assert E_TEMPLATE == "E_template"
    # The SIXTH is the owner's, added 2026-09-02 with the approval recorded at the
    # member. The five above are the SPEC's envelope spellings and are about FILES;
    # this one is about the PERSON, which is why it is a member rather than a
    # reading of one of the five. No prompt is installed for it: a
    # `PromptDefinition` naming it still needs `template_bytes` the owner ratifies.
    assert F_ROLE_SHORTLIST == "F_role_shortlist"
    assert CALL_SITES == (A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE,
                          F_ROLE_SHORTLIST)
    assert CALL_SITES == (
        "A_fact", "B_group", "C_placement", "D_residual", "E_template",
        "F_role_shortlist",
    )


def test_outcomes_are_the_five_uniform_verdict_values():
    assert ACCEPT_DIRECT == "accept_direct"
    assert ACCEPT_CONTEXT_SUPPORTED == "accept_context_supported"
    assert WEAK == "weak"
    assert REJECT == "reject"
    assert ABSTAIN == "abstain"
    assert OUTCOMES == (
        ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED, WEAK, REJECT, ABSTAIN,
    )


def test_reduction_rungs_include_none_for_an_unreduced_call():
    assert REDUCTION_NONE == "none"
    assert SUMMARIZED_FACTS == "summarized_facts"
    assert PRESERVED_ANCHORS == "preserved_anchors"
    assert SPLIT == "split"
    assert DEFERRED == "deferred"
    assert "none" in REDUCTION_RUNGS
    assert REDUCTION_RUNGS == (
        REDUCTION_NONE, SUMMARIZED_FACTS, PRESERVED_ANCHORS, SPLIT, DEFERRED,
    )


def test_fact_eligibility_is_the_closed_site_a_list():
    assert REMAINS_AMBIGUOUS == "remains_ambiguous"
    assert MULTIPLE_PLAUSIBLE_DOMAINS == "multiple_plausible_domains"
    assert LANGUAGE_REQUIRES_INTERPRETATION == "language_requires_interpretation"
    assert FACT_ELIGIBILITY == (
        REMAINS_AMBIGUOUS,
        MULTIPLE_PLAUSIBLE_DOMAINS,
        LANGUAGE_REQUIRES_INTERPRETATION,
    )


def test_group_eligibility_is_the_closed_site_b_list():
    assert COHERENCE_JUDGEMENT == "coherence_judgement"
    assert MEMBERSHIP_JUDGEMENT == "membership_judgement"
    assert OUTLIER_JUDGEMENT == "outlier_judgement"
    assert LABEL_JUDGEMENT == "label_judgement"
    assert GROUP_ELIGIBILITY == (
        COHERENCE_JUDGEMENT,
        MEMBERSHIP_JUDGEMENT,
        OUTLIER_JUDGEMENT,
        LABEL_JUDGEMENT,
    )


def test_placement_eligibility_is_the_closed_site_c_list():
    assert SEVERAL_LEGAL_NODES_PLAUSIBLE == "several_legal_nodes_plausible"
    assert CONTEXT_MEMBER_MISSING_BRANCH_FACT == "context_member_missing_branch_fact"
    assert PLACE_GROUP_TOGETHER == "place_group_together"
    assert CUSTOM_TEMPLATE_SEMANTIC_INTERPRETATION == (
        "custom_template_semantic_interpretation"
    )
    assert VAGUE_OCR_OR_FILENAME == "vague_ocr_or_filename"
    assert DIRECT_FACTS_CONFLICT == "direct_facts_conflict"
    assert PLACEMENT_ELIGIBILITY == (
        SEVERAL_LEGAL_NODES_PLAUSIBLE,
        CONTEXT_MEMBER_MISSING_BRANCH_FACT,
        PLACE_GROUP_TOGETHER,
        CUSTOM_TEMPLATE_SEMANTIC_INTERPRETATION,
        VAGUE_OCR_OR_FILENAME,
        DIRECT_FACTS_CONFLICT,
    )


def test_residual_and_template_eligibility_are_the_closed_site_d_and_e_lists():
    assert USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW == (
        "user_opted_residual_set_into_ai_review"
    )
    assert ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE == (
        "accepted_group_fits_no_existing_template"
    )
    assert RESIDUAL_ELIGIBILITY == (USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW,)
    assert TEMPLATE_ELIGIBILITY == (ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE,)


def test_every_closed_eligibility_reason_is_published():
    assert ALL_ELIGIBILITY == (
        FACT_ELIGIBILITY
        + GROUP_ELIGIBILITY
        + PLACEMENT_ELIGIBILITY
        + RESIDUAL_ELIGIBILITY
        + TEMPLATE_ELIGIBILITY
    )
    assert len(ALL_ELIGIBILITY) == len(set(ALL_ELIGIBILITY))


def test_residual_actions_are_the_eight_controlled_set_members():
    assert RETURN_CONFIRMED_GROUP == "return_to_confirmed_domain_group"
    assert RETURN_ACCEPTED_PACKET == "return_to_accepted_graph_or_purpose_packet"
    assert CHOOSE_RESIDUAL_DESTINATION == "choose_approved_residual_destination"
    assert CHOOSE_BROAD_PARENT == "choose_approved_broad_parent_branch"
    assert MARK_REVIEW_LATER == "mark_review_later"
    assert LEAVE_IN_CURRENT_LOCATION == "leave_in_current_location"
    assert MARK_PROTECTED_OR_UNSUPPORTED == "mark_protected_or_unsupported"
    assert ABSTAIN == "abstain"
    assert RESIDUAL_ACTIONS == (
        RETURN_CONFIRMED_GROUP,
        RETURN_ACCEPTED_PACKET,
        CHOOSE_RESIDUAL_DESTINATION,
        CHOOSE_BROAD_PARENT,
        MARK_REVIEW_LATER,
        LEAVE_IN_CURRENT_LOCATION,
        MARK_PROTECTED_OR_UNSUPPORTED,
        ABSTAIN,
    )


def test_universal_reason_codes_are_screaming_snake_and_equal_their_names():
    assert SCHEMA_INVALID == "SCHEMA_INVALID"
    assert UNCITED_CLAIM == "UNCITED_CLAIM"
    assert CITATION_NOT_IN_DOSSIER == "CITATION_NOT_IN_DOSSIER"
    assert CITATION_NOT_FOUND == "CITATION_NOT_FOUND"
    assert CITATION_SPAN_MISMATCH == "CITATION_SPAN_MISMATCH"
    assert CONTRADICTED_BY_STRONGER == "CONTRADICTED_BY_STRONGER"
    assert NOT_ELIGIBLE_FOR_MODEL == "NOT_ELIGIBLE_FOR_MODEL"
    assert PRIVACY_GATE_REFUSED == "PRIVACY_GATE_REFUSED"
    assert BUDGET_EXHAUSTED == "BUDGET_EXHAUSTED"
    assert USER_REJECTED_EQUIVALENT == "USER_REJECTED_EQUIVALENT"
    assert UNIVERSAL_REASON_CODES == (
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


def test_site_a_adds_its_three_reason_codes():
    assert FIELD_NOT_IN_ACTIVE_SCHEMA == "FIELD_NOT_IN_ACTIVE_SCHEMA"
    assert VALUE_NOT_NORMALIZABLE == "VALUE_NOT_NORMALIZABLE"
    assert SEARCH_HINT_ONLY == "SEARCH_HINT_ONLY"
    assert SITE_A_REASON_CODES == (
        FIELD_NOT_IN_ACTIVE_SCHEMA,
        VALUE_NOT_NORMALIZABLE,
        SEARCH_HINT_ONLY,
    )


def test_site_b_adds_its_reason_codes():
    assert TERM_MERGE_UNSUPPORTED == "TERM_MERGE_UNSUPPORTED"
    assert CONFLICTING_TARGET_INSTITUTION == "CONFLICTING_TARGET_INSTITUTION"
    assert INVENTED_DATE == "INVENTED_DATE"
    assert INVENTED_PROJECT == "INVENTED_PROJECT"
    assert INVENTED_PURPOSE == "INVENTED_PURPOSE"
    assert INVENTED_MEMBERSHIP == "INVENTED_MEMBERSHIP"
    assert LABEL_WITHOUT_COHERENCE == "LABEL_WITHOUT_COHERENCE"
    assert FOLDER_HIERARCHY_PROPOSED == "FOLDER_HIERARCHY_PROPOSED"
    assert CONTEXT_ONLY_SUPPORT == "CONTEXT_ONLY_SUPPORT"
    assert GENERIC_SIMILARITY_ONLY == "GENERIC_SIMILARITY_ONLY"
    assert SITE_B_REASON_CODES == (
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


def test_site_c_adds_its_codes_and_reuses_invented_date_and_project():
    assert NODE_NOT_IN_FROZEN_TREE == "NODE_NOT_IN_FROZEN_TREE"
    assert INVENTED_INSTITUTION == "INVENTED_INSTITUTION"
    assert INVENTED_NODE == "INVENTED_NODE"
    assert SLOT_FILLED_WITHOUT_EVIDENCE == "SLOT_FILLED_WITHOUT_EVIDENCE"
    assert CONFLICT_IGNORED == "CONFLICT_IGNORED"
    assert SENSITIVITY_POLICY_VIOLATION == "SENSITIVITY_POLICY_VIOLATION"
    assert BELOW_SUPPORT_THRESHOLD == "BELOW_SUPPORT_THRESHOLD"
    assert INSUFFICIENT_MARGIN == "INSUFFICIENT_MARGIN"
    assert GENERIC_HUB_ONLY == "GENERIC_HUB_ONLY"
    assert INVENTED_DATE in SITE_C_REASON_CODES
    assert INVENTED_PROJECT in SITE_C_REASON_CODES
    assert SITE_C_REASON_CODES == (
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


def test_site_d_adds_its_reason_codes():
    assert ACTION_NOT_IN_CONTROLLED_SET == "ACTION_NOT_IN_CONTROLLED_SET"
    assert DESTINATION_NOT_IN_FROZEN_TREE == "DESTINATION_NOT_IN_FROZEN_TREE"
    assert EVIDENCE_NOT_IN_FILE_RECORD == "EVIDENCE_NOT_IN_FILE_RECORD"
    assert SENSITIVITY_RESTRICTION_IGNORED == "SENSITIVITY_RESTRICTION_IGNORED"
    assert STRONGER_RELATIONSHIP_OVERLOOKED == "STRONGER_RELATIONSHIP_OVERLOOKED"
    assert INVENTED_FOLDER == "INVENTED_FOLDER"
    assert SITE_D_REASON_CODES == (
        ACTION_NOT_IN_CONTROLLED_SET,
        DESTINATION_NOT_IN_FROZEN_TREE,
        EVIDENCE_NOT_IN_FILE_RECORD,
        SENSITIVITY_RESTRICTION_IGNORED,
        STRONGER_RELATIONSHIP_OVERLOOKED,
        INVENTED_FOLDER,
    )


def test_all_reason_codes_is_the_membership_union():
    from llm_harness.vocabulary import (
        FRAGMENT_NOT_PUBLISHED,
        FRAGMENT_PUBLICATION_ATTEMPTED,
        SITE_E_REASON_CODES,
    )

    published = set(ALL_REASON_CODES)
    assert published == (
        set(UNIVERSAL_REASON_CODES)
        | set(SITE_A_REASON_CODES)
        | set(SITE_B_REASON_CODES)
        | set(SITE_C_REASON_CODES)
        | set(SITE_D_REASON_CODES)
        | set(SITE_E_REASON_CODES)
    )
    # Site E's two, added with P10's fragment boundary (contract §10.3 #2). They
    # are a PAIR on purpose: a well-formed proposal naming an unpublished
    # fragment is not the same defect as one attempting to publish, and Site C
    # already keeps the analogous pair apart.
    assert SITE_E_REASON_CODES == (
        FRAGMENT_NOT_PUBLISHED, FRAGMENT_PUBLICATION_ATTEMPTED,
    )
    assert FRAGMENT_NOT_PUBLISHED == "FRAGMENT_NOT_PUBLISHED"
    assert FRAGMENT_PUBLICATION_ATTEMPTED == "FRAGMENT_PUBLICATION_ATTEMPTED"
    assert INVENTED_DATE in ALL_REASON_CODES
    assert ALL_REASON_CODES.count(INVENTED_DATE) == 1
    assert ALL_REASON_CODES.count(INVENTED_PROJECT) == 1


def test_consent_is_absent_from_p8_vocabularies():
    published = set(OUTCOMES) | set(ALL_REASON_CODES)
    assert "needs_consent" not in published
    assert "consent" not in published


def test_evidence_basis_is_p9s_spelling():
    assert DIRECT_ANCHOR == "direct-anchor"
    assert CONTEXT_SUPPORTED == "context-supported"
    assert EVIDENCE_BASES == (DIRECT_ANCHOR, CONTEXT_SUPPORTED)


def test_verdict_scopes_are_the_spec_six():
    assert SCOPE_FILE == "file"
    assert SCOPE_GROUP == "group"
    assert SCOPE_NODE == "node"
    assert SCOPE_TEMPLATE == "template"
    assert SCOPE_DOMAIN == "domain"
    assert SCOPE_CORPUS == "corpus"
    assert VERDICT_SCOPES == (
        SCOPE_FILE, SCOPE_GROUP, SCOPE_NODE, SCOPE_TEMPLATE, SCOPE_DOMAIN, SCOPE_CORPUS,
    )


def test_dispositions_cover_the_spec_outcome_table():
    assert LLM_SUPPORTED == "llm_supported"
    assert LLM_SUPPORTED_REVIEW == "llm_supported_review"
    assert POSSIBLE == "possible"
    assert REJECTED == "rejected"
    assert NO_FACT == "no_fact"
    assert DIRECT_MEMBERSHIP == "direct_membership"
    assert CONTEXT_SUPPORTED_MEMBERSHIP == "context_supported_membership"
    assert UNRESOLVED == "unresolved"
    assert MOVE_PLAN_ELIGIBLE == "move_plan_eligible"
    assert VALID_REVIEW_REQUIRED == "valid_review_required"
    assert NO_DESTINATION == "no_destination"
    assert NO_SUPPORTED_DESTINATION == "no_supported_destination"
    assert RETURN_TO_PLACEMENT == "return_to_placement"
    assert RESIDUAL_DESTINATION == "residual_destination"
    assert RESIDUAL_DESTINATION_REVIEW == "residual_destination_review"
    assert REVIEW_LATER == "review_later"
    assert LEAVE_IN_PLACE == "leave_in_place"
    for member in (
        LLM_SUPPORTED, LLM_SUPPORTED_REVIEW, POSSIBLE, REJECTED, NO_FACT,
        DIRECT_MEMBERSHIP, CONTEXT_SUPPORTED_MEMBERSHIP, UNRESOLVED,
        MOVE_PLAN_ELIGIBLE, VALID_REVIEW_REQUIRED, NO_DESTINATION,
        NO_SUPPORTED_DESTINATION, RETURN_TO_PLACEMENT, RESIDUAL_DESTINATION,
        RESIDUAL_DESTINATION_REVIEW, REVIEW_LATER, LEAVE_IN_PLACE, ABSTAIN,
    ):
        assert member in DISPOSITIONS
    assert ACCEPT_DIRECT not in DISPOSITIONS
    assert ACCEPT_CONTEXT_SUPPORTED not in DISPOSITIONS
    assert WEAK not in DISPOSITIONS
    assert "needs_consent" not in DISPOSITIONS


def test_named_constants_are_not_dataclass_instances():
    """Vocabularies are strings and tuples, not a parallel record type."""
    assert not dataclasses.is_dataclass(type(CALL_SITES))
    assert isinstance(SCHEMA_INVALID, str)
    assert isinstance(ALL_REASON_CODES, tuple)


def test_needs_consent_is_not_an_eligibility_or_residual_action():
    assert "needs_consent" not in ALL_ELIGIBILITY
    assert "needs_consent" not in RESIDUAL_ACTIONS
    assert "consent" not in ALL_ELIGIBILITY
    assert "consent" not in RESIDUAL_ACTIONS
