# src/llm_harness/records.py
"""Immutable P8 contracts. Shapes freeze here; later tasks must not rename them.

Internal modules import `P8Verdict` by that name. This package exports no bare
`Verdict`. `NeedsConsent` is P7's class and is not a P8 outcome.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.vocabulary import RELIABILITY_STATES, check
from privacy.release import Denied, ModelCallRequest, ModelTarget, NeedsConsent

from llm_harness.vocabulary import (
    ACCEPT_CONTEXT_SUPPORTED,
    ALL_REASON_CODES,
    CALL_SITES,
    DISPOSITIONS,
    ELIGIBILITY_BY_SITE,
    EVIDENCE_BASES,
    OUTCOMES,
    PRE_CALL_REASON_CODES,
    PRIVACY_GATE_REFUSED,
    REDUCTION_RUNGS,
    SITES_REQUIRING_PLAN_VERSION,
    VERDICT_SCOPES,
    WEAK,
)


class MalformedRecord(ValueError):
    """A frozen contract was constructed in a shape P8 does not permit."""


class MalformedVerdict(MalformedRecord):
    """A `P8Verdict` violated a construction-time SPEC invariant."""


def _require(value: str, vocabulary: tuple[str, ...] | frozenset[str], *,
             name: str) -> str:
    if value not in vocabulary:
        raise MalformedRecord(
            f"{name}={value!r} is not one of {tuple(vocabulary)}"
        )
    return value


def _require_plan_version(call_site: str, plan_version: str | None) -> None:
    if call_site in SITES_REQUIRING_PLAN_VERSION and not plan_version:
        raise MalformedRecord(
            f"plan_version is required at {call_site}; it is null only at A and B"
        )


def assemble(prompt_definition: PromptDefinition,
             canonical_dossier_bytes: bytes) -> bytes:
    """Exact model-visible bytes. Provenance fields are not included."""
    return prompt_definition.template_bytes + canonical_dossier_bytes


@dataclass(frozen=True, slots=True)
class PromptDefinition:
    template_id: str
    template_bytes: bytes
    response_schema_bytes: bytes
    call_site: str
    call_site_version: str
    shaping_policy_bytes: bytes

    def __post_init__(self) -> None:
        _require(self.call_site, CALL_SITES, name="call_site")
        if not self.template_id or not self.call_site_version:
            raise MalformedRecord("prompt definition requires template_id and call_site_version")
        if not self.template_bytes:
            raise MalformedRecord("template_bytes are injected; there is no default prompt")
        if not self.response_schema_bytes:
            raise MalformedRecord(
                "response_schema_bytes are injected; there is no default schema"
            )
        if not self.shaping_policy_bytes:
            raise MalformedRecord(
                "shaping_policy_bytes are injected; there is no default policy"
            )


@dataclass(frozen=True, slots=True)
class CallPayload:
    prompt_definition: PromptDefinition
    canonical_dossier_bytes: bytes
    model_visible_bytes: bytes
    model_target: ModelTarget
    prompt_fingerprint: str
    policy_version: str
    release_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.prompt_definition, PromptDefinition):
            raise MalformedRecord("CallPayload.prompt_definition must be a PromptDefinition")
        if not isinstance(self.model_target, ModelTarget):
            raise MalformedRecord("CallPayload.model_target must be privacy.release.ModelTarget")
        expected = assemble(self.prompt_definition, self.canonical_dossier_bytes)
        if self.model_visible_bytes != expected:
            raise MalformedRecord(
                "model_visible_bytes must equal assemble(prompt_definition, "
                "canonical_dossier_bytes); callers cannot supply a mismatched "
                "preassembled representation"
            )
        if not self.prompt_fingerprint or not self.policy_version or not self.release_id:
            raise MalformedRecord(
                "prompt_fingerprint, policy_version, and release_id are required "
                "provenance fields and are not part of the model-visible bytes"
            )


def build_call_payload(
    prompt_definition: PromptDefinition,
    canonical_dossier_bytes: bytes,
    *,
    model_target: ModelTarget,
    prompt_fingerprint: str,
    policy_version: str,
    release_id: str,
) -> CallPayload:
    """Sole public factory. Always assembles model-visible bytes from the two sources."""
    return CallPayload(
        prompt_definition=prompt_definition,
        canonical_dossier_bytes=canonical_dossier_bytes,
        model_visible_bytes=assemble(prompt_definition, canonical_dossier_bytes),
        model_target=model_target,
        prompt_fingerprint=prompt_fingerprint,
        policy_version=policy_version,
        release_id=release_id,
    )


@dataclass(frozen=True, slots=True)
class DossierRequest:
    """Reference-only. No materialised content, excerpts, or observation bodies."""

    call_site: str
    subject_ref: str
    eligibility_reason: str
    evidence_refs: tuple[str, ...]
    model_call_request: ModelCallRequest
    plan_version: str | None
    evidence_snapshot_id: str | None
    budget_context: str | None

    def __post_init__(self) -> None:
        _require(self.call_site, CALL_SITES, name="call_site")
        _require(
            self.eligibility_reason,
            ELIGIBILITY_BY_SITE[self.call_site],
            name="eligibility_reason",
        )
        _require_plan_version(self.call_site, self.plan_version)
        if not self.subject_ref:
            raise MalformedRecord("DossierRequest.subject_ref is required")
        if not isinstance(self.model_call_request, ModelCallRequest):
            raise MalformedRecord(
                "DossierRequest.model_call_request must be the live "
                "privacy.release.ModelCallRequest"
            )
        if any(not ref for ref in self.evidence_refs):
            raise MalformedRecord("evidence_refs are ids only and must be non-empty")


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    evidence_ref: str
    kind: str
    location: str
    excerpt_span: tuple[int, int] | None
    reliability_state: str
    basis: str

    def __post_init__(self) -> None:
        if not self.evidence_ref:
            raise MalformedRecord("EvidenceItem.evidence_ref is required")
        check(self.reliability_state, RELIABILITY_STATES, name="reliability_state")
        _require(self.basis, EVIDENCE_BASES, name="basis")


@dataclass(frozen=True, slots=True)
class Conflict:
    conflict_id: str
    kind: str

    def __post_init__(self) -> None:
        if not self.conflict_id or not self.kind:
            raise MalformedRecord("Conflict requires conflict_id and kind")


@dataclass(frozen=True, slots=True)
class Citation:
    evidence_ref: str
    cited_span: str | None
    metadata_field_name: str | None
    why_it_supports: str

    def __post_init__(self) -> None:
        if not self.evidence_ref or not self.why_it_supports:
            raise MalformedRecord("Citation requires evidence_ref and why_it_supports")
        has_span = bool(self.cited_span)
        has_field = bool(self.metadata_field_name)
        if has_span == has_field:
            raise MalformedRecord(
                "Citation carries exactly one of cited_span or metadata_field_name"
            )


@dataclass(frozen=True, slots=True)
class Unknown:
    insufficiency_statement: str

    def __post_init__(self) -> None:
        if not self.insufficiency_statement:
            raise MalformedRecord("Unknown requires an insufficiency_statement")


@dataclass(frozen=True, slots=True)
class Claim:
    payload: Mapping[str, object]
    citations: tuple[Citation, ...]
    unknown: Unknown | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))
        has_unknown = self.unknown is not None
        has_citations = bool(self.citations)
        if has_unknown == has_citations:
            raise MalformedRecord(
                "Claim carries exactly one of citations or Unknown, never both or neither"
            )
        if has_unknown and not isinstance(self.unknown, Unknown):
            raise MalformedRecord("Claim.unknown must be Unknown")
        if has_citations and any(not isinstance(item, Citation) for item in self.citations):
            raise MalformedRecord("Claim.citations must be Citation records")


@dataclass(frozen=True, slots=True)
class Dossier:
    dossier_id: str
    call_site: str
    subject_ref: str
    eligibility_reason: str
    plan_version: str | None
    policy_version: str
    allowed_vocabulary: tuple[str, ...]
    evidence_items: tuple[EvidenceItem, ...]
    conflicts: tuple[Conflict, ...]
    max_dossier_tokens: int
    reduction_rung: str
    release_id: str

    def __post_init__(self) -> None:
        _require(self.call_site, CALL_SITES, name="call_site")
        _require(
            self.eligibility_reason,
            ELIGIBILITY_BY_SITE[self.call_site],
            name="eligibility_reason",
        )
        _require_plan_version(self.call_site, self.plan_version)
        _require(self.reduction_rung, REDUCTION_RUNGS, name="reduction_rung")
        if not self.dossier_id or not self.subject_ref:
            raise MalformedRecord("Dossier requires dossier_id and subject_ref")
        if not self.policy_version or not self.release_id:
            raise MalformedRecord(
                "Dossier is content-bearing only after P7 release; "
                "policy_version and release_id are required"
            )
        if self.max_dossier_tokens <= 0:
            raise MalformedRecord("max_dossier_tokens must be a positive echo of the ceiling")
        if any(not isinstance(item, EvidenceItem) for item in self.evidence_items):
            raise MalformedRecord("evidence_items must be EvidenceItem records")
        if any(not isinstance(item, Conflict) for item in self.conflicts):
            raise MalformedRecord("conflicts must be Conflict records")


@dataclass(frozen=True, slots=True)
class CheckedCitation:
    citation_ref: str
    resolved: bool
    span_matched: bool

    def __post_init__(self) -> None:
        if not self.citation_ref:
            raise MalformedRecord("CheckedCitation.citation_ref is required")


@dataclass(frozen=True, slots=True)
class P8Verdict:
    verdict_id: str
    dossier_id: str
    claim_ref: str
    outcome: str
    disposition: str
    reasons: tuple[str, ...]
    may_propose: bool
    requires_review: bool
    citations_checked: tuple[CheckedCitation, ...]
    scope: str
    validator_version: str
    policy_version: str
    plan_version: str | None

    def __post_init__(self) -> None:
        try:
            _require(self.outcome, OUTCOMES, name="outcome")
            _require(self.disposition, DISPOSITIONS, name="disposition")
            _require(self.scope, VERDICT_SCOPES, name="scope")
            for reason in self.reasons:
                _require(reason, ALL_REASON_CODES, name="reason")
        except ValueError as exc:
            raise MalformedVerdict(str(exc)) from exc
        if not self.verdict_id or not self.dossier_id or not self.claim_ref:
            raise MalformedVerdict("verdict_id, dossier_id, and claim_ref are required")
        if not self.validator_version or not self.policy_version:
            raise MalformedVerdict("validator_version and policy_version are required")
        if self.outcome == ACCEPT_CONTEXT_SUPPORTED and not self.requires_review:
            raise MalformedVerdict(
                "accept_context_supported always requires_review=True"
            )
        if self.outcome == WEAK and self.may_propose:
            raise MalformedVerdict("weak forbids may_propose=True")
        if any(not isinstance(item, CheckedCitation) for item in self.citations_checked):
            raise MalformedVerdict("citations_checked must be CheckedCitation records")


@dataclass(frozen=True, slots=True)
class GroundingReport:
    dossier_id: str
    call_site: str
    model_id: str
    prompt_fingerprint: str
    validator_version: str
    citations_total: int
    citations_resolved: int
    citations_span_matched: int
    claims_total: int
    claims_abstained: int
    claims_accepted_direct: int
    claims_accepted_context: int
    claims_weak: int
    claims_rejected: int
    reasons_histogram: Mapping[str, int]
    reduction_rung: str
    release_audit_id: int | None
    dossier_builder: str

    def __post_init__(self) -> None:
        _require(self.call_site, CALL_SITES, name="call_site")
        _require(self.reduction_rung, REDUCTION_RUNGS, name="reduction_rung")
        object.__setattr__(
            self, "reasons_histogram", MappingProxyType(dict(self.reasons_histogram)),
        )
        if not self.dossier_id or not self.model_id or not self.prompt_fingerprint:
            raise MalformedRecord("GroundingReport requires dossier, model, and fingerprint")
        if not self.validator_version or not self.dossier_builder:
            raise MalformedRecord("validator_version and dossier_builder are required")


@dataclass(frozen=True, slots=True)
class Refusal:
    """Gate-only. Constructed from P7 `Denied`. Not `NeedsConsent`."""

    denied: Denied

    def __post_init__(self) -> None:
        if not isinstance(self.denied, Denied):
            raise MalformedRecord(
                "Refusal is the Denied path only; construct from privacy.release.Denied"
            )

    @property
    def reason(self) -> str:
        return PRIVACY_GATE_REFUSED

    @property
    def explanation(self) -> str:
        return self.denied.explanation

    @property
    def denial_reason(self) -> str:
        return self.denied.reason


@dataclass(frozen=True, slots=True)
class PreCallAbstention:
    reason: str
    call_site: str
    subject_ref: str

    def __post_init__(self) -> None:
        _require(self.reason, PRE_CALL_REASON_CODES, name="reason")
        _require(self.call_site, CALL_SITES, name="call_site")
        if not self.subject_ref:
            raise MalformedRecord("PreCallAbstention.subject_ref is required")


@dataclass(frozen=True, slots=True)
class CallFailed:
    request_identity: str
    release_id: str
    audit_id: int | None
    explanation: str

    def __post_init__(self) -> None:
        if not self.request_identity or not self.release_id or not self.explanation:
            raise MalformedRecord(
                "CallFailed requires request_identity, release_id, and explanation"
            )


@dataclass(frozen=True, slots=True)
class CallResult:
    """Completed P8 attempt. NeedsConsent is not a branch of this type."""

    value: P8Verdict | Refusal | PreCallAbstention | CallFailed

    def __post_init__(self) -> None:
        if isinstance(self.value, NeedsConsent):
            raise MalformedRecord(
                "NeedsConsent is not a P8 CallResult branch; return it unchanged"
            )
        if not isinstance(
            self.value, (P8Verdict, Refusal, PreCallAbstention, CallFailed),
        ):
            raise MalformedRecord(
                "CallResult.value must be P8Verdict, Refusal, PreCallAbstention, "
                "or CallFailed"
            )


@dataclass(frozen=True, slots=True)
class ValidationUnavailable:
    """Missing injected capabilities. Never an abstain outcome."""

    missing: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.missing or any(not name for name in self.missing):
            raise MalformedRecord(
                "ValidationUnavailable must name the missing injected capabilities"
            )
