# src/llm_harness/sites.py
"""The P8-owned site dispatcher. Callers inject authorities, never acceptance.

`run_call` used to take a `site_validator` callable straight from the caller and
hand it to `validate_response`. `lambda *a, **k: None` was a valid value, and it
disabled every site-specific check — invented Site-B member, invented Site-C
node, invalid Site-E schema — while the universal citation checks still ran and
the result still looked like a real verdict.

The mapping from call site to validator is fixed here. What a caller may still
supply are *authorities*: `node_exists`, `support_threshold`, `margin_predicate`,
`sensitivity_policy`, `schema_validator`, the P6 `FactRequest` and its
normalize/contradicts pair. P8 does not author any of them, and a missing or
malformed one is `ValidationUnavailable` — never a pass.

Live evaluation and replay both route through `dispatch`.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass, replace

from facts.llm_seam import FactRequest, Proposal

from llm_harness.fact_validation import (
    FactValidationDependencies,
    validate_fact_proposal,
)
from llm_harness.group_validation import validate_group_response
from llm_harness.placement_validation import (
    PlacementDependencies,
    ResidualDependencies,
    validate_placement_response,
    validate_residual_response,
)
from llm_harness.records import (
    Citation,
    Dossier,
    MalformedRecord,
    ValidationUnavailable,
)
from llm_harness.template_validation import (
    TemplateDependencies,
    validate_template_response,
)
from llm_harness.validation import (
    parse_citation,
    report_from_verdicts,
    schema_invalid_verdict,
)
from llm_harness.vocabulary import (
    A_FACT,
    B_GROUP,
    C_PLACEMENT,
    D_RESIDUAL,
    E_TEMPLATE,
)


@dataclass(frozen=True, slots=True)
class FactSiteDependencies:
    """Site A's authorities. `fact_request` is P6's, from `facts.llm_seam`."""

    fact_request: FactRequest
    fact_dependencies: FactValidationDependencies

    def __post_init__(self) -> None:
        if not isinstance(self.fact_request, FactRequest):
            raise MalformedRecord(
                "fact_request must be the live facts.llm_seam.FactRequest; P8 does "
                "not build one and a callable here is an acceptance callback"
            )
        if not isinstance(self.fact_dependencies, FactValidationDependencies):
            raise MalformedRecord(
                "fact_dependencies must be FactValidationDependencies (C-5: P8 and "
                "P6 invent neither normalize nor contradicts)"
            )


@dataclass(frozen=True, slots=True)
class SiteDependencies:
    """Typed authority bundles, one per site. A bare callable is not one of them."""

    fact: FactSiteDependencies | None
    placement: PlacementDependencies | None
    residual: ResidualDependencies | None
    template: TemplateDependencies | None

    def __post_init__(self) -> None:
        for name, expected in (
            ("fact", FactSiteDependencies),
            ("placement", PlacementDependencies),
            ("residual", ResidualDependencies),
            ("template", TemplateDependencies),
        ):
            value = getattr(self, name)
            if value is None or isinstance(value, expected):
                continue
            raise MalformedRecord(
                f"{name} must be {expected.__name__} or None; P8 owns which "
                f"validator runs at each site and takes no acceptance callback"
            )


def _one_claim(response_bytes: bytes) -> Mapping[str, object] | None:
    """Site A applies one model claim to one P6 proposal, exactly once (§3.6)."""
    try:
        parsed = json.loads(response_bytes)
    except (ValueError, TypeError, UnicodeDecodeError):
        return None
    if not isinstance(parsed, Mapping):
        return None
    claims = parsed.get("claims")
    if not isinstance(claims, list) or len(claims) != 1:
        return None
    claim = claims[0]
    return claim if isinstance(claim, Mapping) else None


def _proposal(
    claim: Mapping[str, object],
) -> tuple[Proposal, tuple[Citation, ...]] | None:
    """One claim as P6 sees it, plus the citations with their spans intact.

    P6's `Proposal` carries bare observation keys. A key alone cannot say whether
    the model quoted what P7 released or invented the quotation, so Site A keeps
    both shapes and hands both down.
    """
    payload = claim.get("payload")
    payload = payload if isinstance(payload, Mapping) else {}
    field_key = payload.get("field")
    if not isinstance(field_key, str) or not field_key:
        # An abstention still names the field it could not fill; a claim with no
        # field is schema-invalid, not an anonymous unknown.
        return None
    unknown = claim.get("unknown")
    if unknown is not None:
        # `"unknown": false` is a claim the model made, not one it declined. The
        # `is not None` guard read every falsey value as an abstention and threw
        # the payload and every citation away with it. `validation` already
        # requires the Mapping shape; Site A now agrees with it.
        if not isinstance(unknown, Mapping):
            return None
        return Proposal(
            field_key=field_key, value=None, citations=(), unknown=True,
        ), ()
    raw = claim.get("citations")
    if not isinstance(raw, list):
        return None
    citations: list[Citation] = []
    for item in raw:
        parsed = parse_citation(item)
        if parsed is None or not parsed.evidence_ref:
            return None
        citations.append(parsed)
    return Proposal(
        field_key=field_key, value=payload.get("value"),
        citations=tuple(item.evidence_ref for item in citations), unknown=False,
    ), tuple(citations)


def _fact_site(
    conn: sqlite3.Connection | None,
    dossier: Dossier,
    response_bytes: bytes,
    bundle: FactSiteDependencies,
    *,
    evidence_resolver,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
    policy_version: str,
    apply_consequence: bool,
):
    if conn is None:
        return ValidationUnavailable(missing=("conn",))

    def finished(verdicts):
        return tuple(verdicts), report_from_verdicts(
            dossier, verdicts,
            model_id=model_id,
            prompt_fingerprint=prompt_fingerprint,
            dossier_builder=dossier_builder,
            release_audit_id=release_audit_id,
        )

    claim = _one_claim(response_bytes)
    if claim is None:
        return finished((schema_invalid_verdict(dossier),))
    parsed = _proposal(claim)
    if parsed is None:
        return finished((schema_invalid_verdict(dossier),))
    proposal, citations = parsed
    verdict = validate_fact_proposal(
        conn, bundle.fact_request, proposal,
        dependencies=bundle.fact_dependencies,
        model_identifier=model_id,
        prompt_fingerprint=prompt_fingerprint,
        policy_version=policy_version,
        dossier=dossier,
        citations=citations,
        evidence_resolver=evidence_resolver,
        apply_consequence=apply_consequence,
    )
    if isinstance(verdict, ValidationUnavailable):
        return verdict
    return finished((verdict,))


def _addressed_to_the_response(result, response_bytes: bytes):
    """A verdict judges one claim of one RESPONSE against one dossier.

    `verdict_id` was `dossier_id:claim_ref`, which is the identity of a question
    rather than of an answer. `llm_verdict.verdict_id` is a PRIMARY KEY, so a
    second call over the same dossier -- a re-scan of an unchanged file, two
    shards showing identical material -- collided on the insert and crashed out
    of `run_call` with the reservation already taken.

    `dispatch` is the only place that holds both the verdicts and the bytes they
    judged, so the response's address is added here and nowhere else.
    """
    if isinstance(result, ValidationUnavailable):
        return result
    verdicts, report = result
    digest = hashlib.sha256(response_bytes).hexdigest()[:16]
    return tuple(
        replace(verdict, verdict_id=f"{verdict.verdict_id}@{digest}")
        for verdict in verdicts
    ), report


def dispatch(
    conn: sqlite3.Connection | None,
    dossier: Dossier,
    response_bytes: bytes,
    *,
    site_dependencies: SiteDependencies,
    evidence_resolver,
    contradicts,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
    policy_version: str,
    apply_consequence: bool,
):
    """Validate a response at the site the dossier names. One mapping, P8's own.

    `apply_consequence` has no default and separates a live call from a replay.
    Only Site A appends to another part's store: `apply_verdict` writes P6's fact
    or its `unresolved` row, and `write_unresolved` is always an INSERT. Replay
    re-validates stored bytes and must produce the same verdict without a second
    consequence. Sites B-E write nothing outside P8 and ignore it.
    """
    if not isinstance(site_dependencies, SiteDependencies):
        return ValidationUnavailable(missing=("site_dependencies",))

    site = dossier.call_site
    common = dict(
        evidence_resolver=evidence_resolver,
        contradicts=contradicts,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        dossier_builder=dossier_builder,
        release_audit_id=release_audit_id,
    )

    if site == A_FACT:
        if site_dependencies.fact is None:
            return ValidationUnavailable(missing=("fact_dependencies",))
        return _addressed_to_the_response(_fact_site(
            conn, dossier, response_bytes, site_dependencies.fact,
            evidence_resolver=evidence_resolver,
            model_id=model_id,
            prompt_fingerprint=prompt_fingerprint,
            dossier_builder=dossier_builder,
            release_audit_id=release_audit_id,
            policy_version=policy_version,
            apply_consequence=apply_consequence,
        ), response_bytes)
    if site == B_GROUP:
        return _addressed_to_the_response(
            validate_group_response(dossier, response_bytes, **common),
            response_bytes,
        )
    if site == C_PLACEMENT:
        if site_dependencies.placement is None:
            return ValidationUnavailable(missing=("placement_dependencies",))
        return _addressed_to_the_response(validate_placement_response(
            dossier, response_bytes,
            dependencies=site_dependencies.placement, **common,
        ), response_bytes)
    if site == D_RESIDUAL:
        if site_dependencies.residual is None:
            return ValidationUnavailable(missing=("residual_dependencies",))
        return _addressed_to_the_response(validate_residual_response(
            dossier, response_bytes,
            dependencies=site_dependencies.residual, **common,
        ), response_bytes)
    if site == E_TEMPLATE:
        if site_dependencies.template is None:
            return ValidationUnavailable(missing=("template_dependencies",))
        return _addressed_to_the_response(validate_template_response(
            dossier, response_bytes,
            dependencies=site_dependencies.template, **common,
        ), response_bytes)
    return ValidationUnavailable(missing=("site_validator",))
