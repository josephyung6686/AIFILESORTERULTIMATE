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
import sqlite3
from collections.abc import Mapping, Sequence
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
from llm_harness.situation_validation import validate_situation_response
from llm_harness.template_validation import (
    TemplateDependencies,
    validate_template_response,
)
from llm_harness.wire_handles import issued_handles, local_ref
from llm_harness.validation import (
    decode_response,
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
    G_SITUATION_SENSITIVITY,
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


#: WHY EVERY REFUSAL BELOW NAMES ITSELF (`104` R-99).
#:
#: A cloud run over the owner's corpus produced sixteen `SCHEMA_INVALID` responses at
#: this site and the record could not say what was wrong with any of them: every one
#: was one verdict, `claim_ref="schema"`, reason `SCHEMA_INVALID`. Seven turned out to
#: be JSON that did not decode and nine were JSON that decoded and did not fit the
#: shape, and separating them took the bytes, by hand, off a run that costs money.
#:
#: The reason code is unchanged -- it is a closed vocabulary the owner approves member
#: by member -- and the ADDRESS now says which claim and which rule. Each token below
#: is a rule of the ratified A_fact template, in the template's own terms.
_NOT_AN_OBJECT: str = "not_an_object"
_CLAIMS_NOT_A_LIST: str = "claims_not_a_list"
#: Template rule 9: *"claims must never be empty. If you can support nothing at all,
#: send one declining claim for each field you considered."*
_CLAIMS_EMPTY: str = "claims_empty"
#: Template rule 1: the claim names the field it is about, in `payload`.
_FIELD_MISSING: str = "payload_field_missing"
#: Template rule 10: *"Never write `unknown: false` and never write `unknown: null`."*
_UNKNOWN_NOT_AN_OBJECT: str = "unknown_not_an_object"
#: Template rule 10 again, from the other side: a claim carries either citations or
#: `unknown`, never neither -- so a supporting claim with no `value` is neither.
_VALUE_MISSING: str = "payload_value_missing"
_CITATIONS_NOT_A_LIST: str = "citations_not_a_list"
#: Template rule 6: *"A citation carries `evidence_ref` and exactly one of
#: `cited_span` or `metadata_field_name`. Supplying both, or neither, destroys your
#: whole answer."*
_CITATION_MALFORMED: str = "citation_malformed"
#: Template rule 8: *"Never send two claims about the same field: that destroys your
#: whole answer."*
_DUPLICATE_FIELD: str = "duplicate_field"
#: `104` R-132: a claim that names two answerable fields, one in `payload.field` and a
#: different one in the optional `claim_ref`. Neither wins by being first; the claim
#: is refused and the address names both.
_CLAIM_REF_DISAGREES: str = "claim_ref_disagrees_with_field"


def _answerable_fields(request) -> frozenset[str]:
    """The field names this request can be about, or an empty set if it cannot say.

    Only used to read the OPTIONAL `claim_ref`. A bad allowlist shape is
    `_run_checks`'s `ValidationUnavailable` to report, not this function's to
    pre-empt, so an unreadable one answers "no field names" and every `claim_ref` is
    then just an identifier.
    """
    allowlist = getattr(request, "allowlist", None)
    if isinstance(allowlist, (str, bytes)) or not isinstance(allowlist, Sequence):
        return frozenset()
    return frozenset(item for item in allowlist if isinstance(item, str) and item)


def _claim_ref_disagreement(
    claim: Mapping[str, object],
    field_key: str,
    answerable: frozenset[str],
) -> str | None:
    """The refusal address when `claim_ref` names a DIFFERENT answerable field.

    **`payload.field` is authoritative and this does not change that** (`105`
    §14.5): it named the proposal, it decided rule 8's duplicate check, and it is
    the verdict's `claim_ref` on every claim that is judged. What this reads is the
    claim's own optional `claim_ref`, which `13.5`(a) proposed to define as "the
    field the claim is about".

    **Only when it is a field name.** The template prints no `claim_ref` at all and
    this repo's fixtures send `"c1"`; an identifier is not a second answer to "which
    field", so it disagrees with nothing. A `claim_ref` that IS a member of the
    request's allowlist and is not `payload.field` is a second answer, and a claim
    that names two answerable fields does not say which one it answered.

    Both names go in the address, truncated the way `_DUPLICATE_FIELD` truncates,
    because the record has to survive being read a run later.
    """
    raw = claim.get("claim_ref")
    if not isinstance(raw, str) or not raw:
        return None
    if raw == field_key or raw not in answerable:
        return None
    return f"{field_key[:40]}:{_CLAIM_REF_DISAGREES}:{raw[:40]}"


def _claims(
    response_bytes: bytes,
) -> tuple[tuple[Mapping[str, object], ...] | None, str | None]:
    """Every claim in the response, in input order, or the address of the refusal.

    SPEC: *"One verdict record per claim."* Site A used to require exactly one and
    call anything else schema-invalid, so a well-formed two-field response became
    one REJECT and P6 recorded nothing for either field -- the model's whole answer
    vanished. The one-claim rule was P8's; the injected `response_schema_bytes` is
    what decides how many claims are legal, and P8 does not parse it.

    A response with no claims at all is still schema-invalid: there is nothing to
    judge, and silence is what `unknown` is for.

    The JSON parse is `validation.decode_response`, which is the one parser every
    site runs: it reports the byte the decoder stopped on and repairs exactly one
    shape, a complete document followed by a single stray closing bracket.
    """
    parsed, decode_ref = decode_response(response_bytes)
    if decode_ref is not None:
        return None, decode_ref
    if not isinstance(parsed, Mapping):
        return None, f"schema:{_NOT_AN_OBJECT}"
    claims = parsed.get("claims")
    if not isinstance(claims, list):
        return None, f"schema:{_CLAIMS_NOT_A_LIST}"
    if not claims:
        return None, f"schema:{_CLAIMS_EMPTY}"
    for index, claim in enumerate(claims):
        if not isinstance(claim, Mapping):
            return None, f"claim-{index}:{_NOT_AN_OBJECT}"
    return tuple(claims), None


def _proposal(
    claim: Mapping[str, object],
    *,
    handles: Mapping[str, str],
) -> tuple[Proposal, tuple[Citation, ...]] | str:
    """One claim as P6 sees it, plus the citations with their spans intact, or the
    name of the template rule it broke.

    P6's `Proposal` carries bare observation keys. A key alone cannot say whether
    the model quoted what P7 released or invented the quotation, so Site A keeps
    both shapes and hands both down.

    The model cited the handle it was shown, and BOTH shapes carry P4's own key
    from here on: `_run_checks` compares the bare list against P6's citable
    observations, and a handle would match none of them.
    """
    payload = claim.get("payload")
    payload = payload if isinstance(payload, Mapping) else {}
    field_key = payload.get("field")
    if not isinstance(field_key, str) or not field_key:
        # An abstention still names the field it could not fill; a claim with no
        # field is schema-invalid, not an anonymous unknown.
        return _FIELD_MISSING
    unknown = claim.get("unknown")
    if unknown is not None:
        # `"unknown": false` is a claim the model made, not one it declined. The
        # `is not None` guard read every falsey value as an abstention and threw
        # the payload and every citation away with it. `validation` already
        # requires the Mapping shape; Site A now agrees with it.
        if not isinstance(unknown, Mapping):
            return _UNKNOWN_NOT_AN_OBJECT
        return Proposal(
            field_key=field_key, value=None, citations=(), unknown=True,
        ), ()
    value = payload.get("value")
    if value is None:
        # A SUPPORTING claim that never says what it read -- the key absent, or
        # present and `null`. The ratified schema forbids both: the `support`
        # branch requires `payload.required: ["field", "value"]`, and rule 3 is
        # *"`value` must be a JSON string ... Never a number, a list, an object,
        # true, false or null"*. At site A this function IS that check, because
        # nothing validates the response bytes against
        # `a_fact_response_schema.json` before they are parsed.
        #
        # **Only `None`, and the narrowness is the point.** Rule 3's other
        # forbidden types are already answered a layer down, per claim: `76` §7's
        # S15 is a number and its recorded expectation is
        # `VALUE_NOT_NORMALIZABLE`, one rejected claim rather than a destroyed
        # response. Widening this to every non-string moved S15's verdict and
        # rewrote a row the owner ratified. `None` is the one spelling that has no
        # verdict below, because it is the one `Proposal` will not hold.
        #
        # Left unchecked it built `Proposal(value=None, unknown=False)`, which
        # `facts.llm_seam.Proposal` refuses with a bare `ValueError` -- not a
        # verdict, not a refusal, and not catchable by anything between here and
        # `FactResolver`. A live model produced exactly that shape on a real
        # corpus: the exception left `run_call`, ended the pass at 25 of 40 files,
        # and the run designed no tree at all.
        #
        # `None` is the answer every other bad shape here gets: one
        # `schema_invalid` verdict for the whole response, which is the refusal
        # this seam already has for a model that did not answer in the shape it was
        # given.
        return _VALUE_MISSING
    raw = claim.get("citations")
    if not isinstance(raw, list):
        return _CITATIONS_NOT_A_LIST
    citations: list[Citation] = []
    for item in raw:
        parsed = parse_citation(item)
        if parsed is None or not parsed.evidence_ref:
            return _CITATION_MALFORMED
        citations.append(replace(
            parsed,
            evidence_ref=local_ref(parsed.evidence_ref, handles=handles)))
    return Proposal(
        field_key=field_key, value=value,
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
    handle_key: bytes,
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

    claims, refusal = _claims(response_bytes)
    if claims is None:
        return finished((schema_invalid_verdict(dossier, refusal),))
    handles = issued_handles(
        (item.evidence_ref for item in dossier.evidence_items), key=handle_key)
    parsed = [_proposal(claim, handles=handles) for claim in claims]
    for index, item in enumerate(parsed):
        if isinstance(item, str):
            return finished((
                schema_invalid_verdict(dossier, f"claim-{index}:{item}"),))
    fields = [proposal.field_key for proposal, _citations in parsed]
    if len(set(fields)) != len(fields):
        # `claim_ref` is what tells two verdicts apart and Site A's is the field
        # key, so two claims about one field are indistinguishable. P8 does not
        # choose which of the model's two answers it meant.
        repeated = next(
            name for index, name in enumerate(fields) if name in fields[:index])
        return finished((schema_invalid_verdict(
            dossier, f"claims:{_DUPLICATE_FIELD}:{repeated[:40]}"),))
    answerable = _answerable_fields(bundle.fact_request)
    verdicts = []
    # `parsed` is one entry per claim, in input order, and the loop above returned
    # for every entry that was a refusal -- so `strict` is the invariant said out
    # loud rather than a shape this zip could quietly drop half of.
    for claim, (proposal, citations) in zip(claims, parsed, strict=True):
        disagreement = _claim_ref_disagreement(
            claim, proposal.field_key, answerable)
        if disagreement is not None:
            # ONE CLAIM REFUSED, THE RESPONSE ALIVE (`104` R-132, `105` §14.5(d)).
            # `payload.field` is authoritative -- it decided the duplicate check
            # above and it names this verdict -- so the refusal is not about which
            # name wins. It is that a claim naming TWO answerable fields does not
            # say which question it answered, and P8 does not choose. The address
            # carries both, because a record saying only "invalid" is the failure
            # this file's matrix was written to end.
            verdicts.append(schema_invalid_verdict(dossier, disagreement))
            continue
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
        verdicts.append(verdict)
    return finished(tuple(verdicts))


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
    handle_key: bytes,
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
        # The key the dossier's bytes were built with. Every site reads the
        # model's references, and none of them may read a handle as a P4 key.
        handle_key=handle_key,
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
            handle_key=handle_key,
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
    if site == G_SITUATION_SENSITIVITY:
        # NO BUNDLE, ON SITE B'S PRECEDENT. C, D and E take typed authorities
        # because they need a frozen tree, a controlled action set or a fragment
        # catalogue; B and G need none. Everything site G checks is already in the
        # dossier -- the shortlist it showed the model and the evidence it released
        # -- so a slot here would be a slot a caller could fill with an acceptance
        # callback, which is the shape this module exists to refuse.
        return _addressed_to_the_response(validate_situation_response(
            dossier, response_bytes, **common,
        ), response_bytes)
    return ValidationUnavailable(missing=("site_validator",))
