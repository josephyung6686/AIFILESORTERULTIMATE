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
from llm_harness.records import CheckedCitation, P8Verdict, ValidationUnavailable
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    CITATION_NOT_FOUND,
    CONTRADICTED_BY_STRONGER,
    FIELD_NOT_IN_ACTIVE_SCHEMA,
    LLM_SUPPORTED as P8_LLM_SUPPORTED,
    LLM_SUPPORTED_REVIEW,
    POSSIBLE as P8_POSSIBLE,
    REJECT,
    REJECTED,
    SCOPE_FILE,
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

_REASON_TO_CHECK = {
    FIELD_NOT_IN_ACTIVE_SCHEMA: FOUR_CHECKS[0],
    CITATION_NOT_FOUND: FOUR_CHECKS[1],
    VALUE_NOT_NORMALIZABLE: FOUR_CHECKS[2],
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


def _checked_citations(
    citations: Sequence[str], citable_keys: set[str],
) -> tuple[CheckedCitation, ...]:
    return tuple(
        CheckedCitation(
            citation_ref=key,
            resolved=key in citable_keys,
            span_matched=key in citable_keys,
        )
        for key in citations
    )


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
    dossier_id: str,
) -> P8Verdict | ValidationUnavailable:
    allowlist = _freeze_str_sequence(request.allowlist, name="allowlist")
    if isinstance(allowlist, ValidationUnavailable):
        return allowlist
    citations = _freeze_sequence(proposal.citations, name="citations")
    if isinstance(citations, ValidationUnavailable):
        return citations
    observations = _freeze_sequence(
        request.citable_observations, name="citable_observations")
    if isinstance(observations, ValidationUnavailable):
        return observations
    existing = _freeze_sequence(request.existing_facts, name="existing_facts")
    if isinstance(existing, ValidationUnavailable):
        return existing

    citable_keys = {item.observation_key for item in observations}
    checked = _checked_citations(citations, citable_keys)

    if proposal.field_key not in allowlist:
        return _verdict(
            request, proposal, outcome=REJECT,
            reasons=(FIELD_NOT_IN_ACTIVE_SCHEMA,),
            citations_checked=checked, policy_version=policy_version,
            dossier_id=dossier_id,
        )
    if not citations or any(key not in citable_keys for key in citations):
        return _verdict(
            request, proposal, outcome=REJECT,
            reasons=(CITATION_NOT_FOUND,),
            citations_checked=checked, policy_version=policy_version,
            dossier_id=dossier_id,
        )
    raw_value = proposal.value
    if not isinstance(raw_value, str) or (
            dependencies.normalize(proposal.field_key, raw_value) is None):
        return _verdict(
            request, proposal, outcome=REJECT,
            reasons=(VALUE_NOT_NORMALIZABLE,),
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
    dossier_id: str,
) -> P8Verdict | ValidationUnavailable:
    """Run Site A's four §3.6 checks and hand the consequence to P6.

    ``proposal_state`` is derived from the `P8Verdict` and passed to
    `apply_verdict` with no default. This module does not write facts or
    unresolved rows itself.
    """
    missing = _missing(dependencies)
    if missing:
        return ValidationUnavailable(missing=missing)

    if proposal.unknown:
        p8 = _verdict(
            request, proposal, outcome=ABSTAIN, reasons=(),
            citations_checked=(), policy_version=policy_version,
            dossier_id=dossier_id,
        )
    else:
        p8 = _run_checks(
            request, proposal, dependencies, policy_version=policy_version,
            dossier_id=dossier_id,
        )
        if isinstance(p8, ValidationUnavailable):
            return p8

    apply_verdict(
        conn, request=request, proposal=proposal,
        verdict=p6_verdict_from_p8(p8),
        proposal_state=proposal_state_from_p8(p8),
        model_identifier=model_identifier,
        prompt_fingerprint=prompt_fingerprint,
    )
    return p8
