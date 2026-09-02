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

#: THE SIXTH, ADDED 2026-09-02 WITH THE OWNER'S APPROVAL, RECORDED HERE.
#:
#: The five above are the SPEC's envelope spellings and are about FILES: a fact
#: about one, a group of them, a placement, a residual, a template. This one is
#: about the PERSON, and it is the only call site in the product that is -- which
#: is why it is a sixth member rather than a reading of one of the five.
#:
#: `80` §1 rules that a model proposes the role shortlist and the person confirms.
#: `80` §2 rules a typed self-description a `user_edits` item, always local; `80`
#: §8 suspends the ENFORCEMENT of that for development, not the classification.
#: On 2026-09-02 the owner chose a narrow P7 release path for it, over a genuinely
#: local model -- which `80` §1 actually specifies and which
#: `readers/model_ollama.py` could already serve -- and over deferring until a
#: local version existed to compare against, with the irreversibility named:
#: `00`:200, "revocation cannot necessarily retract data already sent to an
#: external provider."
#:
#: WHAT THE APPROVAL COVERS, and it is narrow on purpose: the self-description,
#: for the role shortlist, and nothing else. It does not admit a second question
#: about the person, and `privacy.items.SelfDescription` is the type that makes
#: that structural rather than promised.
#:
#: `83` §3 routes this site to the REASONING tier, because R4 requires the
#: shortlist to read as having heard the WHOLE sentence and that is the judgement
#: a cheaper model flattens to one keyword. `83` §4 forbids the silent downgrade.
#:
#: NO PROMPT IS INSTALLED FOR IT, and this member does not install one. A
#: `PromptDefinition` naming this site still needs `template_bytes`, which are the
#: owner's to ratify and which no agent may author or adopt. A draft is held for
#: him and is inert until he acts on it. No path is named here on purpose: the
#: draft lives outside the repo until it is ratified, and a source comment
#: pointing at a file that may not exist is worse than one that does not point.
F_ROLE_SHORTLIST: str = "F_role_shortlist"

CALL_SITES: tuple[str, ...] = (
    A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE, F_ROLE_SHORTLIST,
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

#: Worst first. `run_call` returns ONE verdict for a call that may have produced
#: several -- one per shard, one per claim -- and `emit_stage_output` maps that
#: one result onto one P2 envelope. Returning the LAST one reported by position:
#: a call whose first shard was rejected and whose second was accepted read
#: `accept_direct`, and the P2 row read `produced`. A caller who is told
#: `accept_direct` must be able to take it as true of the whole call.
OUTCOME_SEVERITY: tuple[str, ...] = (
    REJECT, ABSTAIN, WEAK, ACCEPT_CONTEXT_SUPPORTED, ACCEPT_DIRECT,
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

#: The namespace a pre-call terminal is addressed in. A terminal reached before a
#: dossier exists has no dossier address, and writing the subject ref into the
#: `dossier_id` column made a P1 file id look like one -- a row that joins to no
#: `llm_dossier` row while appearing to promise it does.
PRE_CALL_NAMESPACE: str = "pre-call"


def pre_call_address(call_site: str, subject_ref: str) -> str:
    """An address that cannot be mistaken for, or joined to, a dossier."""
    return f"{PRE_CALL_NAMESPACE}:{call_site}:{subject_ref}"

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

#: THE FOURTH SITE-A CODE, ADDED 2026-09-02 WITH THE OWNER'S APPROVAL, RECORDED HERE.
#:
#: The three above are §3.3's and §3.6's, and each names something a check was
#: already doing. This one names a check that did not exist. `86` §4: **the proposed
#: `value` is never compared to the citation or to any released text.** `90` §5 ranks
#: a check that compares them first among the things that would help -- ahead of any
#: choice between prompt candidates. `llm_harness.value_grounding` is that
#: comparison; this is the word it refuses with.
#:
#: THE NAME, AND WHAT IT WAS CHOSEN OVER. The owner was offered `VALUE_NOT_IN_CITED_
#: EVIDENCE`, `VALUE_NOT_IN_THE_QUOTE` and `MADE_UP_VALUE`, and chose this one: it
#: says what the check measured, in the phrase the codebase already uses for that
#: thing. **`MADE_UP_VALUE` was rejected because absent is not fabricated.** A
#: normalisation this deployment has no rule for, an honest mis-citation and an
#: invention all land in this bucket, and a name asserting intent would make the
#: report claim more than the check knows.
#:
#: WHAT IT ESTABLISHES, AND WHAT IT DOES NOT. It establishes ONE thing: the value's
#: characters, read without case and without separators, are not a whole-token run of
#: any released value this claim cites. It does NOT establish that the model invented
#: the value, and nothing downstream may read it that way. The three false-reject
#: classes are asserted in `tests/p8/test_p8_value_grounding.py` -- morphology, a
#: canonical form whose raw spelling was never proposed, and any script that does not
#: separate words. Nor does it establish that a value which PASSES was found rather
#: than lifted: `90` §2.2 records that several of the glossary's enumerated words are
#: ordinary English, and where the word is on the page a lift and a find are
#: byte-identical. This check narrows S16; it does not close it.
#:
#: WHAT IT MAPS TO AT P6. `FOUR_CHECKS[1]`, whose P6 reason is
#: `citation_absent_from_evidence`. The citation resolves and its span matches; what
#: is absent from it is any support for the value. **The cost, chosen knowingly:** an
#: `unresolved` row will say the model mis-cited when it mis-valued. The alternative
#: was a fifth member of P6's `CHECK_REASONS` -- a second closed vocabulary, in
#: another part -- and one approval was taken over two.
#:
#: WHY NOT AN EXISTING CODE. `SEARCH_HINT_ONLY` is the borrowable one: published,
#: `weak`, and with no producer anywhere in `src/`. `39` A12 rules that it is to be
#: implemented as §3.3's test or removed, not repurposed, and "the characters of this
#: value are not in the text you cited" is not "this is merely a search hint".
VALUE_NOT_IN_CITED_TEXT: str = "VALUE_NOT_IN_CITED_TEXT"

SITE_A_REASON_CODES: tuple[str, ...] = (
    FIELD_NOT_IN_ACTIVE_SCHEMA,
    VALUE_NOT_NORMALIZABLE,
    SEARCH_HINT_ONLY,
    VALUE_NOT_IN_CITED_TEXT,
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


SCOPE_SCHEMA_FIELD: str = "schema-field"
SCOPE_TEMPLATE_LOCAL: str = "template-local"

#: The tier a Site-E proposal declares per dimension. `schema-field` is a claim
#: that the name is in the dossier's own closure and is fact-backed;
#: `template-local` is a display label with a semantic role and a citation, and
#: no P6 field behind it. The tier is a PAYLOAD key, not a `Dossier` field: it is
#: what the model asserts, so the assertion can be checked against the closure
#: rather than inferred from it.
DIMENSION_SCOPES: tuple[str, ...] = (SCOPE_SCHEMA_FIELD, SCOPE_TEMPLATE_LOCAL)

FRAGMENT_NOT_PUBLISHED: str = "FRAGMENT_NOT_PUBLISHED"
FRAGMENT_PUBLICATION_ATTEMPTED: str = "FRAGMENT_PUBLICATION_ATTEMPTED"

SITE_E_REASON_CODES: tuple[str, ...] = (
    FRAGMENT_NOT_PUBLISHED,
    FRAGMENT_PUBLICATION_ATTEMPTED,
)

#: Payload keys that mean the response is trying to PUBLISH shared organization
#: logic rather than reference it. A Site-E proposal may name a published
#: fragment by exact id and version and may add template-local dimensions; it may
#: not create a canonical fragment, because sharing logic is a human review
#: decision made once and not a side effect of one branch's model call.
#:
#: The list lives here, beside `FRAGMENT_PUBLICATION_ATTEMPTED`, because reading
#: a model response is P8's and the scanner and the reason it returns belong
#: together. P10 owns the catalogue publication would write into and IMPORTS
#: this, the way it imports every other P8 vocabulary.
FORBIDDEN_PUBLISHING_KEYS: tuple[str, ...] = (
    "fragment_definitions",
    "new_fragments",
    "publish_fragment",
    "canonical_fragments",
    "definitions",
    "applicabilities",
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
    SITE_E_REASON_CODES,
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
