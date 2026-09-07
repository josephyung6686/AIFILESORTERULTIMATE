# src/llm_harness/fact_validation.py
"""Site A: §3.6 fact checks through explicit P6-domain callbacks.

P6 publishes the four inputs and the consequence writer. It publishes neither
`normalize` nor `contradicts` (C-5). This module owns the four checks and maps a
`P8Verdict` onto the distinct live `facts.llm_seam.Verdict`. Domain catalogues and
oracle implementations stay with the caller; omitting either callback is
`ValidationUnavailable`, not a pass.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace

from facts.llm_seam import (
    FOUR_CHECKS,
    FactRequest,
    Proposal,
    Verdict,
    apply_verdict,
)
from facts.states import LLM_SUPPORTED, POSSIBLE

from llm_harness.authorship import COMPONENT_VERSION
from llm_harness.records import (
    CheckedCitation,
    Citation,
    CompatibilityConversion,
    Dossier,
    P8Verdict,
    ValidationUnavailable,
)
from llm_harness.validation import check_citations
from llm_harness.value_grounding import value_is_grounded
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    CITATION_NOT_FOUND,
    CITATION_NOT_IN_DOSSIER,
    CITATION_SPAN_MISMATCH,
    CONTRADICTED_BY_STRONGER,
    FIELD_NOT_IN_ACTIVE_SCHEMA,
    LLM_SUPPORTED as P8_LLM_SUPPORTED,
    LLM_SUPPORTED_REVIEW,
    POSSIBLE as P8_POSSIBLE,
    REJECT,
    REJECTED,
    SCOPE_FILE,
    VALUE_NOT_IN_CITED_TEXT,
    VALUE_NOT_NORMALIZABLE,
    WEAK,
)

_DISPOSITION = {
    ACCEPT_DIRECT: P8_LLM_SUPPORTED,
    ACCEPT_CONTEXT_SUPPORTED: LLM_SUPPORTED_REVIEW,
    WEAK: P8_POSSIBLE,
    REJECT: REJECTED,
    ABSTAIN: ABSTAIN,
}

#: Three P8 citation reasons, one P6 consequence. P6's vocabulary has a single
#: word for a citation that does not hold -- `citation_absent_from_evidence` --
#: and P8 keeps the three ways it can fail: the key is outside what P7 released,
#: the key no longer resolves in the store, or the quoted span is not in the
#: released value. Collapsing them at P8 would lose which one happened.
_REASON_TO_CHECK = {
    FIELD_NOT_IN_ACTIVE_SCHEMA: FOUR_CHECKS[0],
    CITATION_NOT_FOUND: FOUR_CHECKS[1],
    CITATION_NOT_IN_DOSSIER: FOUR_CHECKS[1],
    CITATION_SPAN_MISMATCH: FOUR_CHECKS[1],
    VALUE_NOT_NORMALIZABLE: FOUR_CHECKS[2],
    VALUE_NOT_IN_CITED_TEXT: FOUR_CHECKS[1],
    CONTRADICTED_BY_STRONGER: FOUR_CHECKS[3],
}


def _freeze_sequence(value: object, *, name: str) -> tuple | ValidationUnavailable:
    """Reject str/bytes; require a Sequence; copy to tuple.

    Same idea as `records._freeze_sequence`: `in` on a string is substring
    search, and iterating a bare string would become one-character members.
    Does not mutate the P6 record. A bad shape is `ValidationUnavailable`,
    so the public function still returns `P8Verdict | ValidationUnavailable`.
    """
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        return ValidationUnavailable(missing=(name,))
    return tuple(value)


def _freeze_str_sequence(value: object, *, name: str) -> tuple[str, ...] | ValidationUnavailable:
    frozen = _freeze_sequence(value, name=name)
    if isinstance(frozen, ValidationUnavailable):
        return frozen
    if not all(isinstance(item, str) for item in frozen):
        return ValidationUnavailable(missing=(name,))
    return frozen


def _require_bool(value: object, *, name: str) -> bool | ValidationUnavailable:
    if value is not True and value is not False:
        return ValidationUnavailable(missing=(name,))
    return value


@dataclass(frozen=True)
class FactValidationDependencies:
    normalize: Callable[[str, str], object]
    contradicts: Callable[[Proposal, sqlite3.Row], bool]
    #: THE REVIEW HALF OF CHECK 3 (`104` R-98), AND IT IS THE DEPLOYMENT'S TOO.
    #:
    #: `normalize` answers "is this value storable as a fact this deployment can
    #: canonicalise", and its `None` is `VALUE_NOT_NORMALIZABLE`. That refused ten of
    #: ten correct `subject` answers on the owner's corpus, because every one was a
    #: course TITLE and the deterministic rule reads a CODE. `104` §13.5 says a rule
    #: may reject only a structurally invalid answer and §13.7 says a value the
    #: library has not seen is proposed once and the person confirms it, so a title
    #: is neither storable nor refusable: it is a candidate.
    #:
    #: This callback is what tells the two apart, and P8 does not author it any more
    #: than it authors the other two (C-5). It answers a canonical form for a value a
    #: PERSON could confirm, or `None`; a value only it can normalise is accepted
    #: `accept_context_supported`, whose disposition is `llm_supported_review` and
    #: whose P6 state is `possible` -- `00`:42's "possible clue for review", below the
    #: floor `facts.read_surface.PROPOSAL_ELIGIBLE_STATES` puts under every folder.
    #:
    #: **Undefaulted, like the other two, and `None` is a value a caller states.**
    #: `tests/p8/test_p8_no_invention.py` forbids a default on any P8 dependency
    #: field: an authority nobody supplied must be a decision somebody made, not a
    #: shape that quietly appeared. A deployment that authors no review normaliser
    #: passes `None` and check 3 is exactly what it was before this field existed.
    normalize_for_review: Callable[[str, str], object] | None


def _missing(dependencies: FactValidationDependencies | None) -> tuple[str, ...]:
    if dependencies is None:
        return ("normalize", "contradicts")
    missing: list[str] = []
    if not callable(getattr(dependencies, "normalize", None)):
        missing.append("normalize")
    if not callable(getattr(dependencies, "contradicts", None)):
        missing.append("contradicts")
    return tuple(missing)


def p6_verdict_from_p8(verdict: P8Verdict) -> Verdict:
    """Map a Site A `P8Verdict` onto the distinct live P6 `Verdict`."""
    if verdict.outcome != REJECT:
        return Verdict(passed=True, failed_check=None)
    reason = verdict.reasons[0]
    return Verdict(passed=False, failed_check=_REASON_TO_CHECK[reason])


def proposal_state_from_p8(verdict: P8Verdict) -> str:
    """P6 `proposal_state` for a passing Site A outcome. Required; no default.

    **`accept_context_supported` writes `possible`, and that moved on 2026-09-07.**
    It used to write `llm_supported`, which is the state a folder proposal may rest
    on (`facts.read_surface.PROPOSAL_ELIGIBLE_STATES`). Nothing anywhere reads
    `requires_review` -- `104` R-75 is that finding from the placement side -- so an
    outcome that says a person must look at the value first was writing a fact that
    P10 could turn into a folder before anybody looked. `00`:42 fixes the state for
    exactly this case: a model output "useful but too weak to establish a fact may
    remain a possible clue for review; it must not quietly become a folder proposal
    or an asserted file property". Confirming the value is what raises it, and
    confirming is the person's.
    """
    if verdict.outcome in (WEAK, ACCEPT_CONTEXT_SUPPORTED):
        return POSSIBLE
    return LLM_SUPPORTED


def _verdict(
    request: FactRequest,
    proposal: Proposal,
    *,
    outcome: str,
    reasons: Sequence[str],
    citations_checked: Sequence[CheckedCitation],
    policy_version: str,
    dossier_id: str,
    compatibility: CompatibilityConversion | None = None,
) -> P8Verdict:
    return P8Verdict(
        verdict_id=f"{dossier_id}:{proposal.field_key}",
        dossier_id=dossier_id,
        claim_ref=proposal.field_key,
        outcome=outcome,
        disposition=_DISPOSITION[outcome],
        reasons=tuple(reasons),
        may_propose=outcome in (ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED),
        requires_review=outcome == ACCEPT_CONTEXT_SUPPORTED,
        citations_checked=tuple(citations_checked),
        scope=SCOPE_FILE,
        validator_version=COMPONENT_VERSION,
        policy_version=policy_version,
        plan_version=None,
        compatibility=compatibility,
    )


#: THE COMPATIBILITY RULE THIS MODULE APPLIES, AND ITS VERSION (`104` R-132).
#:
#: `105` §14.5: the canonical decline stays `unknown` with an `insufficiency_statement`
#: and no value, a supported value stays non-empty, and the ratified schema keeps
#: `minLength: 1` -- so `""` is a shape the schema forbids and the CODE tolerates. A
#: tolerance nobody can name is indistinguishable from a bug, so it is named here and
#: numbered: every verdict it produces carries `empty_value_to_unknown/1`.
#:
#: **The version moves when the RULE moves, not when this file does.** `104` §14.7
#: says a validator or normalisation change must re-evaluate cached responses rather
#: than retain obsolete verdicts; a stored verdict that names version 1 is a verdict
#: some later reader can decide to re-judge, and it can only decide that if the
#: version is on the record. Widening what counts as empty, or changing what the
#: conversion drops, is version 2.
EMPTY_VALUE_TO_UNKNOWN_RULE: str = "empty_value_to_unknown"
EMPTY_VALUE_TO_UNKNOWN_VERSION: str = "1"


def _declined_the_field(raw_value: object) -> bool:
    """An EMPTY answer is the model declining the field, not a bad value (`104` R-119).

    Check 3 asks whether a value can be canonicalised, and it answered `None` for the
    empty string as readily as for nonsense -- so a decline was recorded `reject
    VALUE_NOT_NORMALIZABLE`. Measured on the owner's corpus: 19 claims (`term` 10,
    `work_type` 9) came back as `""` and every one was scored a wrong answer in
    VERDICTS BY SITE. Worse, `model_facts` reuses ABSTENTIONS and not rejections
    (`store.abstained_fields`), so the next run asked the same model the same question
    it had already declined.

    The product already has the outcome for "I cannot say": `abstain`. This is a rule
    about the SHAPE of the answer, not about the prompt or the vocabulary -- the model
    is not told anything new, and a non-empty value that fails to normalise is
    `VALUE_NOT_NORMALIZABLE` exactly as before.

    Whitespace counts as empty, and so does an empty string the model QUOTED: a local
    run returned the two characters `""` in a JSON string, which is the same decline
    spelled with the quotes left in. A lone `"` is not: it is one character the
    normaliser has an opinion about.
    """
    if not isinstance(raw_value, str):
        return False
    stripped = raw_value.strip()
    if len(stripped) >= 2 and stripped[0] == '"' and stripped[-1] == '"':
        stripped = stripped[1:-1].strip()
    return not stripped


def _check_three(
    dependencies: FactValidationDependencies,
    field_key: str,
    raw_value: object,
) -> tuple[object, str]:
    """Check 3, both halves, in one place so the write cannot answer it twice.

    Returns the canonical form and the outcome it earns: the deployment's own
    normaliser first, whose answer is `accept_direct`; then, only if that declined,
    the review normaliser, whose answer is `accept_context_supported`. `(None, ...)`
    is `VALUE_NOT_NORMALIZABLE` as before.

    Called from `_run_checks` to decide and from `validate_fact_proposal` to write,
    because a canonical form computed twice by two routes is `65` §4.2's failure
    waiting on a seam.
    """
    if not isinstance(raw_value, str):
        return None, REJECT
    normalized = dependencies.normalize(field_key, raw_value)
    if normalized is not None:
        return normalized, ACCEPT_DIRECT
    review = dependencies.normalize_for_review
    if not callable(review):
        return None, REJECT
    candidate = review(field_key, raw_value)
    if not isinstance(candidate, str) or not candidate:
        return None, REJECT
    return candidate, ACCEPT_CONTEXT_SUPPORTED


def _run_checks(
    request: FactRequest,
    proposal: Proposal,
    dependencies: FactValidationDependencies,
    *,
    policy_version: str,
    dossier: Dossier,
    citations: Sequence[Citation],
    evidence_resolver: Callable[[str], object],
) -> P8Verdict | ValidationUnavailable:
    dossier_id = dossier.dossier_id
    allowlist = _freeze_str_sequence(request.allowlist, name="allowlist")
    if isinstance(allowlist, ValidationUnavailable):
        return allowlist
    keys = _freeze_sequence(proposal.citations, name="citations")
    if isinstance(keys, ValidationUnavailable):
        return keys
    rich = _freeze_sequence(citations, name="citations")
    if isinstance(rich, ValidationUnavailable):
        return rich
    if not all(isinstance(item, Citation) for item in rich):
        return ValidationUnavailable(missing=("citations",))
    if tuple(item.evidence_ref for item in rich) != tuple(keys):
        # P6's `Proposal` carries bare keys and cannot carry a span, so Site A
        # gets both shapes. Two lists that disagree are two answers to the same
        # question; the caller built them from one claim, and they must match.
        return ValidationUnavailable(missing=("citations",))
    observations = _freeze_sequence(
        request.citable_observations, name="citable_observations")
    if isinstance(observations, ValidationUnavailable):
        return observations
    existing = _freeze_sequence(request.existing_facts, name="existing_facts")
    if isinstance(existing, ValidationUnavailable):
        return existing

    citable_keys = {item.observation_key for item in observations}
    grounded = check_citations(rich, dossier, evidence_resolver)
    if isinstance(grounded, ValidationUnavailable):
        return grounded
    checked, citation_reasons = grounded

    if proposal.field_key not in allowlist:
        return _verdict(
            request, proposal, outcome=REJECT,
            reasons=(FIELD_NOT_IN_ACTIVE_SCHEMA,),
            citations_checked=checked, policy_version=policy_version,
            dossier_id=dossier_id,
        )
    # Check two, coarse then fine. P6 owns which observations exist for this file
    # version; P7 owns which of them the model was actually shown, and whether the
    # quotation is in the released text. A key that is not a P6 observation at all
    # fails the coarse check -- asking whether it was released would be asking
    # about something that does not exist. Both reach P6 as the one word its
    # vocabulary has for it, `citation_absent_from_evidence`.
    if not keys or any(key not in citable_keys for key in keys):
        return _verdict(
            request, proposal, outcome=REJECT,
            reasons=(CITATION_NOT_FOUND,),
            citations_checked=checked, policy_version=policy_version,
            dossier_id=dossier_id,
        )
    if citation_reasons:
        return _verdict(
            request, proposal, outcome=REJECT,
            reasons=citation_reasons,
            citations_checked=checked, policy_version=policy_version,
            dossier_id=dossier_id,
        )
    raw_value = proposal.value
    if _declined_the_field(raw_value):
        # BEFORE check 3, and after checks 1 and 2 on purpose. An empty answer about
        # a field nobody asked for is still a field nobody asked for, and putting it
        # in `abstained_fields` would suppress a question that was never valid.
        #
        # AND IT IS A CONVERSION, WHICH IS A THING THE RECORD SAYS (`104` R-132).
        # The outcome is the canonical `abstain` an explicit `unknown` earns and
        # nothing about it is new; what is new is that the verdict now names the
        # rule that produced it, its version, the field, and what the conversion
        # dropped -- the value as the model wrote it and the keys it cited -- so a
        # reader can tell a decline the model GAVE from one the validator MADE.
        # Reaching here at all means checks 1 and 2 passed; the closed-object and
        # duplicate-field refusals are earlier still, in `sites`, and this cannot
        # route around either of them.
        dropped = _freeze_str_sequence(proposal.citations, name="citations")
        if isinstance(dropped, ValidationUnavailable):
            # The record refuses a citation key that is not a string, and a record
            # that refuses must not refuse by raising out of a function whose whole
            # contract is `P8Verdict | ValidationUnavailable`.
            return dropped
        return _verdict(
            request, proposal, outcome=ABSTAIN, reasons=(),
            citations_checked=checked, policy_version=policy_version,
            dossier_id=dossier_id,
            compatibility=CompatibilityConversion(
                rule_id=EMPTY_VALUE_TO_UNKNOWN_RULE,
                version=EMPTY_VALUE_TO_UNKNOWN_VERSION,
                field=proposal.field_key,
                dropped_value=raw_value,
                dropped_citations=dropped,
            ),
        )
    normalized, outcome = _check_three(
        dependencies, proposal.field_key, raw_value)
    if normalized is None:
        return _verdict(
            request, proposal, outcome=REJECT,
            reasons=(VALUE_NOT_NORMALIZABLE,),
            citations_checked=checked, policy_version=policy_version,
            dossier_id=dossier_id,
        )
    if not value_is_grounded(
            raw_value, normalized,
            citations=rich, released_evidence=dossier.released_evidence):
        return _verdict(
            request, proposal, outcome=REJECT,
            reasons=(VALUE_NOT_IN_CITED_TEXT,),
            citations_checked=checked, policy_version=policy_version,
            dossier_id=dossier_id,
        )
    for row in existing:
        conflict = _require_bool(
            dependencies.contradicts(proposal, row), name="contradicts")
        if isinstance(conflict, ValidationUnavailable):
            return conflict
        if conflict is True:
            return _verdict(
                request, proposal, outcome=REJECT,
                reasons=(CONTRADICTED_BY_STRONGER,),
                citations_checked=checked, policy_version=policy_version,
                dossier_id=dossier_id,
            )
    return _verdict(
        request, proposal, outcome=outcome,
        reasons=(), citations_checked=checked, policy_version=policy_version,
        dossier_id=dossier_id,
    )


def validate_fact_proposal(
    conn: sqlite3.Connection,
    request: FactRequest,
    proposal: Proposal,
    *,
    dependencies: FactValidationDependencies,
    model_identifier: str,
    prompt_fingerprint: str,
    policy_version: str,
    dossier: Dossier,
    citations: Sequence[Citation],
    evidence_resolver: Callable[[str], object],
    apply_consequence: bool,
) -> P8Verdict | ValidationUnavailable:
    """Run Site A's four §3.6 checks and hand the consequence to P6.

    ``proposal_state`` is derived from the `P8Verdict` and passed to
    `apply_verdict` with no default. This module does not write facts or
    unresolved rows itself.

    `citations` are the model's citations with their spans intact. P6's
    `Proposal` carries bare observation keys, and a key alone cannot say whether
    the model quoted the release or invented the quotation.

    `apply_consequence` has no default. A live call appends P6's consequence; a
    replay re-validates the same stored bytes and must not, because
    `facts.unresolved.write_unresolved` is always an INSERT and never
    de-duplicated -- replaying an abstention wrote a second row saying the model
    had declined twice for one thing it declined once. The verdict is identical
    either way, which is what makes the comparison a replay.
    """
    missing = _missing(dependencies)
    if missing:
        return ValidationUnavailable(missing=missing)
    if not isinstance(dossier, Dossier):
        return ValidationUnavailable(missing=("dossier",))
    if not callable(evidence_resolver):
        return ValidationUnavailable(missing=("evidence_resolver",))
    if dossier.subject_ref != request.file_id:
        # The dossier is the model's closed world; the `FactRequest` decides
        # where the consequence lands. Nothing checked that they name the same
        # file, so a dossier describing one file wrote a fact onto another,
        # cited to observations that file never had.
        return ValidationUnavailable(missing=("subject_ref",))
    if apply_consequence is not True and apply_consequence is not False:
        return ValidationUnavailable(missing=("apply_consequence",))

    if proposal.unknown:
        p8 = _verdict(
            request, proposal, outcome=ABSTAIN, reasons=(),
            citations_checked=(), policy_version=policy_version,
            dossier_id=dossier.dossier_id,
        )
    else:
        p8 = _run_checks(
            request, proposal, dependencies, policy_version=policy_version,
            dossier=dossier, citations=citations,
            evidence_resolver=evidence_resolver,
        )
        if isinstance(p8, ValidationUnavailable):
            return p8

    if apply_consequence:
        # CHECK 3'S OWN ANSWER, carried to the write instead of being dropped.
        # `_run_checks` normalises to decide whether the proposal is storable and
        # to ground it; what P6 must STORE is that canonical form, or one course
        # arrives from two producers as two spellings and becomes two folders. The
        # normalizer is a pure function of these two arguments, so calling it here
        # is the same answer and not a second one -- and it is called only on the
        # path that writes, because a rejected proposal has no canonical form (a
        # `None` from check 3 IS the rejection).
        p6 = p6_verdict_from_p8(p8)
        # AN ABSTENTION IS AN ABSTENTION ON BOTH SIDES OF THE SEAM (`104` R-119).
        # `apply_verdict` reads `proposal.unknown` to decide between "the model
        # declined" and "the model answered", and an empty answer is `unknown=False`
        # -- `Proposal` will not hold a value AND a decline, so the empty string
        # arrives here as a claim. Left alone, `p6.passed` is True for every
        # non-REJECT outcome and the write reached `ensure_value` with the canonical
        # form of nothing, ending the pass on a value the model never asserted. The
        # consequence P6 records is the one an explicit abstention records:
        # `model_returned_unknown`, no fact, no value row.
        consequence = proposal
        if p8.outcome == ABSTAIN and not proposal.unknown:
            consequence = replace(proposal, value=None, citations=(), unknown=True)
        # ONLY ON THE PATH THAT WRITES. A rejected proposal has no canonical form,
        # and normalising one here would call the deployment's normalizer for a
        # value no check asked about -- including after checks 1 and 2, which are
        # ordered BEFORE check 3 precisely so a bad field or a bad citation is
        # refused without the value ever being canonicalised. Three tests in
        # `tests/p8/test_p8_fact_validation.py` count those calls and caught it.
        canonical = None
        if p6.passed and not consequence.unknown and isinstance(consequence.value, str):
            # `_check_three`, not `normalize`: a title accepted into review has no
            # answer from the first normaliser, and reading only that one here wrote
            # `canonical_value=None` onto a PASSING verdict -- which `ensure_value`
            # raises on, ending the pass rather than storing the candidate.
            canonical, _outcome = _check_three(
                dependencies, consequence.field_key, consequence.value)
        apply_verdict(
            conn, request=request, proposal=consequence,
            verdict=p6,
            proposal_state=proposal_state_from_p8(p8),
            model_identifier=model_identifier,
            prompt_fingerprint=prompt_fingerprint,
            canonical_value=canonical if isinstance(canonical, str) else None,
        )
    return p8
