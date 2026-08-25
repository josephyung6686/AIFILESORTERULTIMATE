"""Site E template validation using an injected strict schema validator.

P10 owns template design quality. P8 does not invent or score a hierarchy.
"""
from __future__ import annotations

import dataclasses
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from llm_harness.records import Dossier, P8Verdict, ValidationUnavailable
from llm_harness.validation import validate_response
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    REJECT,
    REJECTED,
    SCHEMA_INVALID,
    UNRESOLVED,
    WEAK,
)


@dataclass(frozen=True, slots=True)
class TemplateDependencies:
    schema_validator: Callable[[object], bool]


def _payload_of(raw: object) -> Mapping[str, object]:
    if not isinstance(raw, Mapping):
        return {}
    payload = raw.get("payload")
    if isinstance(payload, Mapping):
        return payload
    return {}


def _rewrite(
    verdict: P8Verdict,
    *,
    outcome: str | None = None,
    disposition: str | None = None,
    reasons: tuple[str, ...] | None = None,
    may_propose: bool | None = None,
    requires_review: bool | None = None,
) -> P8Verdict:
    new_outcome = verdict.outcome if outcome is None else outcome
    new_review = verdict.requires_review if requires_review is None else requires_review
    if new_outcome == ACCEPT_CONTEXT_SUPPORTED:
        new_review = True
    new_propose = verdict.may_propose if may_propose is None else may_propose
    if new_outcome == WEAK:
        new_propose = False
    return dataclasses.replace(
        verdict,
        outcome=new_outcome,
        disposition=verdict.disposition if disposition is None else disposition,
        reasons=verdict.reasons if reasons is None else reasons,
        may_propose=new_propose,
        requires_review=new_review,
    )


def _dimensions(payload: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    raw = payload.get("dimensions")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return ()
    return tuple(item for item in raw if isinstance(item, Mapping))


def _cited_refs(raw: object) -> set[str]:
    if not isinstance(raw, Mapping):
        return set()
    citations = raw.get("citations")
    if not isinstance(citations, Sequence) or isinstance(citations, (str, bytes)):
        return set()
    refs: set[str] = set()
    for item in citations:
        if isinstance(item, Mapping) and item.get("evidence_ref"):
            refs.add(str(item["evidence_ref"]))
    return refs


def _template_site(
    dossier: Dossier,
    raw: object,
    verdict: P8Verdict,
    dependencies: TemplateDependencies,
) -> P8Verdict | None:
    payload = _payload_of(raw)
    if not dependencies.schema_validator(payload):
        return _rewrite(
            verdict,
            outcome=REJECT,
            disposition=REJECTED,
            reasons=(SCHEMA_INVALID,),
            may_propose=False,
            requires_review=False,
        )
    vocab = set(dossier.allowed_vocabulary)
    dimensions = _dimensions(payload)
    if any(item.get("name") not in vocab for item in dimensions):
        return _rewrite(
            verdict,
            outcome=REJECT,
            disposition=REJECTED,
            reasons=(),
            may_propose=False,
            requires_review=False,
        )
    cited = _cited_refs(raw)
    if any(item.get("evidence_ref") not in cited for item in dimensions):
        return _rewrite(
            verdict,
            outcome=REJECT,
            disposition=REJECTED,
            reasons=(),
            may_propose=False,
            requires_review=False,
        )
    levels = payload.get("levels")
    if isinstance(levels, Sequence) and not isinstance(levels, (str, bytes)):
        if any(
            isinstance(level, Mapping) and not level.get("retrieval_justification")
            for level in levels
        ):
            return _rewrite(
                verdict,
                outcome=WEAK,
                disposition=UNRESOLVED,
                reasons=(),
                may_propose=False,
                requires_review=False,
            )
    return None


def _template_disposition(verdict: P8Verdict) -> P8Verdict:
    if verdict.outcome == REJECT and not verdict.reasons:
        return _rewrite(verdict, disposition=REJECTED)
    if verdict.outcome == WEAK:
        return _rewrite(verdict, disposition=UNRESOLVED)
    if verdict.outcome == ABSTAIN:
        return verdict
    if verdict.outcome == ACCEPT_DIRECT:
        return verdict
    if verdict.outcome == ACCEPT_CONTEXT_SUPPORTED:
        return verdict
    return verdict


def validate_template_response(
    dossier: Dossier,
    response_bytes: bytes,
    *,
    evidence_resolver,
    contradicts,
    dependencies: TemplateDependencies | None,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
):
    if dependencies is None or dependencies.schema_validator is None:
        return ValidationUnavailable(missing=("schema_validator",))

    def site(dossier_arg, raw, verdict):
        return _template_site(dossier_arg, raw, verdict, dependencies)

    result = validate_response(
        dossier,
        response_bytes,
        evidence_resolver=evidence_resolver,
        site_validator=site,
        contradicts=contradicts,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        dossier_builder=dossier_builder,
        release_audit_id=release_audit_id,
    )
    if isinstance(result, ValidationUnavailable):
        return result
    verdicts, report = result
    return tuple(_template_disposition(item) for item in verdicts), report
