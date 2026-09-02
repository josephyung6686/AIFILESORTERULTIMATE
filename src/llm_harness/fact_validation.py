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
from dataclasses import dataclass

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
    """P6 `proposal_state` for a passing Site A outcome. Required; no default."""
    if verdict.outcome == WEAK:
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
    )


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
    normalized = (dependencies.normalize(proposal.field_key, raw_value)
                  if isinstance(raw_value, str) else None)
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
        request, proposal, outcome=ACCEPT_DIRECT,
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
        apply_verdict(
            conn, request=request, proposal=proposal,
            verdict=p6_verdict_from_p8(p8),
            proposal_state=proposal_state_from_p8(p8),
            model_identifier=model_identifier,
            prompt_fingerprint=prompt_fingerprint,
        )
    return p8
