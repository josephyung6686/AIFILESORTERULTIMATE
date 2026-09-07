# src/llm_harness/validation.py
"""Universal deterministic validation and grounding-report construction.

Parse JSON once, keep the raw response bytes untouched, and check claims in
input order. No model is consulted. Contradiction is an injected oracle; this
module does not implement domain contradiction or normalization.

Recorded response shape (stable; later site validators reuse it)::

    {"claims": [
        {"claim_ref": str,                 # optional; default claim-<index>
         "payload": object,
         "citations": [
             {"evidence_ref": str,         # P4 observation_key
              "cited_span": str | None,
              "metadata_field_name": str | None,
              "why_it_supports": str}
         ],
         "unknown": {"insufficiency_statement": str}}
    ]}

Exactly one of a non-empty ``citations`` list or ``unknown`` is valid, unless
the site's ``uncited_claim`` hook admits an empty list (site C, `105` §14.1).
"""
from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from typing import Any

from llm_harness.authorship import COMPONENT_VERSION
from llm_harness.records import (
    CallFailed,
    CheckedCitation,
    Citation,
    Dossier,
    DossierRequest,
    GroundingReport,
    MalformedRecord,
    P8Verdict,
    PreCallAbstention,
    Refusal,
    Unknown,
    ValidationUnavailable,
)
from llm_harness.wire_handles import WIRE_HANDLE_KEY, issued_handles, local_ref
from llm_harness.vocabulary import (
    pre_call_address,
    A_FACT,
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    B_GROUP,
    BUDGET_EXHAUSTED,
    C_PLACEMENT,
    CITATION_NOT_FOUND,
    CITATION_NOT_IN_DOSSIER,
    CITATION_SPAN_MISMATCH,
    CONTEXT_SUPPORTED,
    CONTRADICTED_BY_STRONGER,
    D_RESIDUAL,
    DEFERRED,
    E_TEMPLATE,
    LLM_SUPPORTED,
    LLM_SUPPORTED_REVIEW,
    POSSIBLE,
    REDUCTION_NONE,
    REJECT,
    REJECTED,
    SCHEMA_INVALID,
    SCOPE_FILE,
    SCOPE_GROUP,
    SCOPE_NODE,
    SCOPE_TEMPLATE,
    UNCITED_CLAIM,
    WEAK,
)

#: Tag for reports this module constructs when no neighbour built a dossier.
DOSSIER_BUILDER = "p8"

_SCOPE_BY_SITE = {
    A_FACT: SCOPE_FILE,
    B_GROUP: SCOPE_GROUP,
    C_PLACEMENT: SCOPE_NODE,
    D_RESIDUAL: SCOPE_FILE,
    E_TEMPLATE: SCOPE_TEMPLATE,
}

_DISPOSITION_BY_OUTCOME = {
    ACCEPT_DIRECT: LLM_SUPPORTED,
    ACCEPT_CONTEXT_SUPPORTED: LLM_SUPPORTED_REVIEW,
    WEAK: POSSIBLE,
    REJECT: REJECTED,
    ABSTAIN: ABSTAIN,
}

_ZERO_COUNTS = dict(
    citations_total=0,
    citations_resolved=0,
    citations_span_matched=0,
    claims_total=0,
    claims_abstained=0,
    claims_accepted_direct=0,
    claims_accepted_context=0,
    claims_weak=0,
    claims_rejected=0,
)


def parse_citation(raw: object) -> Citation | None:
    """One citation parser. Site A used to reduce citations to bare keys."""
    if not isinstance(raw, Mapping):
        return None
    cited_span = raw.get("cited_span")
    metadata_field_name = raw.get("metadata_field_name")
    if cited_span is not None and not isinstance(cited_span, str):
        return None
    if metadata_field_name is not None and not isinstance(metadata_field_name, str):
        return None
    try:
        return Citation(
            evidence_ref=str(raw.get("evidence_ref") or ""),
            cited_span=cited_span,
            metadata_field_name=metadata_field_name,
            why_it_supports=str(raw.get("why_it_supports") or ""),
        )
    except (MalformedRecord, TypeError, ValueError):
        return None


def _check_citation(
    citation: Citation,
    dossier: Dossier,
    evidence_resolver: Callable[[str], object],
) -> tuple[CheckedCitation, str | None]:
    """Two checks, two sources. SPEC: `CITATION_SPAN_MISMATCH` compares the cited
    span against *"the released dossier's excerpt -- what the model actually saw"*,
    while `CITATION_NOT_FOUND` *"resolves the reference against the store"*.

    P4's value is never the span-matching source. With redaction on, the stored
    text is the raw value and the model was shown the redacted one; matching
    against the store would accept a quotation the model could not have read and
    reject the one it did.
    """
    refs = {item.evidence_ref for item in dossier.evidence_items}
    if citation.evidence_ref not in refs:
        return (
            CheckedCitation(citation.evidence_ref, False, False),
            CITATION_NOT_IN_DOSSIER,
        )
    released = {
        item.observation_key: item for item in dossier.released_evidence
    }.get(citation.evidence_ref)
    if released is None:
        # In the dossier as a reference, but nothing about it was released.
        return (
            CheckedCitation(citation.evidence_ref, False, False),
            CITATION_NOT_IN_DOSSIER,
        )
    if evidence_resolver(citation.evidence_ref) is None:
        return (
            CheckedCitation(citation.evidence_ref, False, False),
            CITATION_NOT_FOUND,
        )
    if citation.cited_span:
        matched = citation.cited_span in released.value
    elif citation.cited_span is None:
        matched = citation.metadata_field_name == released.address
    else:
        # `"" in anything` is True. An empty span is not a quotation of the
        # release, and the `is not None` guard sent it to the substring test
        # rather than to the address comparison -- so neither check ever ran.
        matched = False
    if not matched:
        return (
            CheckedCitation(citation.evidence_ref, True, False),
            CITATION_SPAN_MISMATCH,
        )
    return CheckedCitation(citation.evidence_ref, True, True), None


def check_citations(
    citations: Sequence[Citation],
    dossier: Dossier,
    evidence_resolver: Callable[[str], object],
) -> tuple[tuple[CheckedCitation, ...], tuple[str, ...]] | ValidationUnavailable:
    """Every site's citation check, in input order, over one dossier.

    Site A ran its own: it took the citable set from P6's `FactRequest`, which is
    every observation for the file version, and set `span_matched` to a copy of
    `resolved`. A key P7 withheld, quoted with a span the model invented, was
    accepted and the fact was written. There is one check now, and it is bound to
    the release.
    """
    checked: list[CheckedCitation] = []
    reasons: list[str] = []
    for citation in citations:
        item, reason = _check_citation(citation, dossier, evidence_resolver)
        checked.append(item)
        if reason is not None:
            reasons.append(reason)
    return tuple(checked), tuple(reasons)


def _make_verdict(
    *,
    dossier: Dossier,
    claim_ref: str,
    outcome: str,
    reasons: Sequence[str],
    may_propose: bool,
    requires_review: bool,
    citations_checked: Sequence[CheckedCitation],
) -> P8Verdict:
    return P8Verdict(
        verdict_id=f"{dossier.dossier_id}:{claim_ref}",
        dossier_id=dossier.dossier_id,
        claim_ref=claim_ref,
        outcome=outcome,
        disposition=_DISPOSITION_BY_OUTCOME[outcome],
        reasons=tuple(reasons),
        may_propose=may_propose,
        requires_review=requires_review,
        citations_checked=tuple(citations_checked),
        scope=_SCOPE_BY_SITE[dossier.call_site],
        validator_version=COMPONENT_VERSION,
        policy_version=dossier.policy_version,
        plan_version=dossier.plan_version,
    )


def schema_invalid_verdict(dossier: Dossier, claim_ref: str = "schema") -> P8Verdict:
    return _make_verdict(
        dossier=dossier,
        claim_ref=claim_ref,
        outcome=REJECT,
        reasons=(SCHEMA_INVALID,),
        may_propose=False,
        requires_review=False,
        citations_checked=(),
    )


#: WHERE THE BYTES STOPPED BEING JSON, carried on the verdict's own address.
#:
#: `SCHEMA_INVALID` is the reason and it stays the reason: the reason codes are a
#: closed vocabulary the owner approves member by member (`vocabulary.py` records the
#: last such approval, 2026-09-02, in full), and "the response did not parse" is what
#: this one already says. What it does not say is WHERE, and without that a run
#: reports seven identical refusals and nobody can tell a truncation from a code fence
#: from a stray bracket. `claim_ref` is the verdict's address, free text, and for a
#: decode failure there is no claim to name -- so the address names the byte instead.
JSON_DECODE_CLAIM_REF: str = "schema:json_decode@byte-{offset}"


def _decode_claim_ref(offset: int) -> str:
    return JSON_DECODE_CLAIM_REF.format(offset=offset)


def _byte_offset(text: str, position: object) -> int:
    """A character index from `json`, as the byte offset this module reports.

    `JSONDecodeError.pos` counts CHARACTERS into the decoded string. Every offset
    recorded here is a byte offset into the response as it was stored, because that
    is the thing somebody would open.
    """
    if not isinstance(position, int) or position < 0:
        return 0
    return len(text[:position].encode("utf-8"))


def _one_surplus_closing_bracket(text: str) -> object | None:
    """A complete JSON document followed by exactly one stray `]` or `}`, parsed.

    **This is the only repair, and the condition is a proof rather than a guess.**
    `raw_decode` parses one complete value and says where it ended. If everything
    after that end is whitespace and a single closing bracket, then the document was
    finished before the surplus character and no value inside it can depend on that
    character: a closing bracket cannot open, name, or extend anything. The bytes are
    stored raw, so a replay re-derives the same repair from the same evidence.

    **What is deliberately NOT repaired, with the measured shapes.** `105` §5.3 and
    §4.7 record the defect this is about: deepseek-chat closes a payload whose last
    key is a populated array as `...]]}],"citations":[` -- one bracket too many, in
    the MIDDLE, with the citations still to come -- and `"merge_terms":[]}],"citations"`
    one bracket short in the same position. Neither is a complete document plus a
    stray character; each is a mis-close with content after it, and repairing one
    means choosing which of several documents the model meant. There is no
    unambiguous repair for those and this function refuses them, which is why `105`
    §4.7's own fix was to reorder the payload so the last key is a scalar, not to
    mend the bytes. A response missing a closing bracket at the very tail is refused
    for the same reason: appending one is choosing between `]` and `}`, and between
    one and several.

    `raw_decode` does not skip leading whitespace, so the scan starts at the first
    non-space character; a preamble or a code fence is not whitespace and fails here
    exactly as it fails in `json.loads`.
    """
    start = len(text) - len(text.lstrip())
    try:
        value, end = json.JSONDecoder().raw_decode(text, start)
    except ValueError:
        return None
    if text[end:].strip() not in ("]", "}"):
        return None
    return value


def decode_response(response_bytes: object) -> tuple[object, str | None]:
    """The one JSON parse every site's validator runs. `(value, None)` or `(None, ref)`.

    The second member is the `claim_ref` a `schema_invalid_verdict` should carry: it
    names the byte the decoder stopped on. `None` means the bytes decoded -- either
    outright, or after `_one_surplus_closing_bracket` proved the surplus inert.
    """
    text = response_bytes
    if isinstance(text, (bytes, bytearray)):
        try:
            text = text.decode("utf-8")
        except UnicodeDecodeError as exc:
            return None, _decode_claim_ref(exc.start)
    if not isinstance(text, str):
        return None, _decode_claim_ref(0)
    try:
        return json.loads(text), None
    except ValueError as exc:
        offset = _byte_offset(text, getattr(exc, "pos", 0))
    repaired = _one_surplus_closing_bracket(text)
    if repaired is None:
        return None, _decode_claim_ref(offset)
    return repaired, None


def _heading_exposure(released: Sequence) -> tuple[int, int]:
    """`104` R-135's two counters: how many whole heading units this call released,
    and the longest one's length in characters.

    **The ruling releases a whole heading unit and invents no length bound, so the
    exposure is reported rather than capped.** Each released item already SAYS whether
    it is that exemption: `resolve.materialise` asks
    `privacy.release.released_whole_heading_unit` of P4's own `Location`, which is the
    same predicate the two release builders admit by, and the answer travels as
    `whole_heading_unit` through `ReleasedItem` and `ReleasedEvidence`. So this
    function adds up what the items carry and derives nothing.

    **It re-parsed the address, and that was wrong twice over.** `ReleasedItem.span` is
    a serialisation of a `Location`, so parsing it back was re-deriving a structural
    fact from its own printing -- and `parse_locator` refuses in three ways, all
    `ValueError`, so a fixture address of `0:18` raised `NotInVocabulary` out of a
    report and ended fourteen `tests/p8/test_p8_harness.py` calls that had already been
    answered. A counter runs after the model has spoken and a release has been spent;
    it is never the thing that decides a call's fate. An item that could not be
    classified carries `False` and counts as nothing.

    The identifier inside a heading is not counted, and that is the predicate's doing
    rather than this function's: it shares the heading's container path but its span is
    a fraction of the unit, so no exemption was taken to release it.

    `report_for_budget_exhausted` and `_zero_report` do not call this and report zero:
    both are built from a `DossierRequest` with no `Dossier` behind them, so no dossier
    reached a model and no heading unit left the device. Zero there is the measurement.
    """
    units = [item for item in released
             if getattr(item, "whole_heading_unit", False)]
    lengths = [item.unit_length for item in units
               if isinstance(item.unit_length, int)]
    return len(units), max(lengths, default=0)


def report_from_verdicts(
    dossier: Dossier,
    verdicts: Sequence[P8Verdict],
    *,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
) -> GroundingReport:
    checked = [item for verdict in verdicts for item in verdict.citations_checked]
    heading_units, longest_heading = _heading_exposure(dossier.released_evidence)
    histogram: dict[str, int] = {}
    for verdict in verdicts:
        for reason in verdict.reasons:
            histogram[reason] = histogram.get(reason, 0) + 1
    return GroundingReport(
        dossier_id=dossier.dossier_id,
        call_site=dossier.call_site,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        validator_version=COMPONENT_VERSION,
        citations_total=len(checked),
        citations_resolved=sum(1 for item in checked if item.resolved),
        citations_span_matched=sum(1 for item in checked if item.span_matched),
        claims_total=len(verdicts),
        claims_abstained=sum(1 for verdict in verdicts if verdict.outcome == ABSTAIN),
        claims_accepted_direct=sum(
            1 for verdict in verdicts if verdict.outcome == ACCEPT_DIRECT
        ),
        claims_accepted_context=sum(
            1 for verdict in verdicts if verdict.outcome == ACCEPT_CONTEXT_SUPPORTED
        ),
        claims_weak=sum(1 for verdict in verdicts if verdict.outcome == WEAK),
        claims_rejected=sum(1 for verdict in verdicts if verdict.outcome == REJECT),
        reasons_histogram=histogram,
        reduction_rung=dossier.reduction_rung,
        release_audit_id=release_audit_id,
        dossier_builder=dossier_builder,
        heading_units_released=heading_units,
        longest_heading_unit_length=longest_heading,
    )


def _zero_report(
    request: DossierRequest,
    *,
    validator_version: str,
    reasons_histogram: Mapping[str, int],
    reduction_rung: str,
    release_audit_id: int | None,
    dossier_id: str,
) -> GroundingReport:
    return GroundingReport(
        dossier_id=dossier_id,
        call_site=request.call_site,
        model_id=request.model_call_request.model_target.model_id,
        prompt_fingerprint=request.model_call_request.prompt_fingerprint,
        validator_version=validator_version,
        reasons_histogram=dict(reasons_histogram),
        reduction_rung=reduction_rung,
        release_audit_id=release_audit_id,
        dossier_builder=DOSSIER_BUILDER,
        **_ZERO_COUNTS,
    )


def acceptance_outcome(dossier: Dossier, citations: Sequence[Citation]) -> str:
    """`accept_context_supported` when every cited item is context, else `accept_direct`.

    **One rule with two callers since `104` R-135, which is why it is public.** This
    file's `_validate_claim` uses it for sites B, C, D and E; `fact_validation`'s
    `_run_checks` uses it at site A, where a `subject` read off a neighbouring syllabus
    must not be recorded as if the file had said it itself. A second spelling of "was
    this answer grounded only in context" would be two answers to one question, and the
    review obligation would then depend on which site asked.

    A MIXED answer is direct. A claim that cites the file's own text as well as a
    neighbour's rests on the file, and `requires_review` is for the claim that does not.
    """
    cited_refs = {item.evidence_ref for item in citations}
    bases = [
        item.basis for item in dossier.evidence_items if item.evidence_ref in cited_refs
    ]
    if bases and all(basis == CONTEXT_SUPPORTED for basis in bases):
        return ACCEPT_CONTEXT_SUPPORTED
    return ACCEPT_DIRECT


def _validate_claim(
    dossier: Dossier,
    raw: object,
    index: int,
    *,
    evidence_resolver: Callable[[str], object],
    site_validator: Callable[..., Any],
    oracle: Callable[..., Any] | None,
    handles: Mapping[str, str],
    uncited_claim: Callable[[Dossier, Mapping[str, object]], str | None] | None = None,
) -> P8Verdict | ValidationUnavailable:
    claim_ref = f"claim-{index}"
    if not isinstance(raw, Mapping):
        return schema_invalid_verdict(dossier, claim_ref)
    if raw.get("claim_ref"):
        claim_ref = str(raw["claim_ref"])
    payload = raw.get("payload")
    if payload is None:
        payload = {}
    if not isinstance(payload, Mapping):
        return schema_invalid_verdict(dossier, claim_ref)

    unknown_raw = raw.get("unknown")
    citations_raw = raw.get("citations")
    has_unknown = unknown_raw is not None
    if has_unknown:
        if not isinstance(unknown_raw, Mapping):
            return schema_invalid_verdict(dossier, claim_ref)
        try:
            unknown = Unknown(
                insufficiency_statement=str(
                    unknown_raw.get("insufficiency_statement") or ""
                ),
            )
        except (MalformedRecord, TypeError, ValueError):
            return schema_invalid_verdict(dossier, claim_ref)
        del unknown
        if isinstance(citations_raw, Sequence) and not isinstance(
            citations_raw, (str, bytes),
        ) and len(citations_raw) > 0:
            return schema_invalid_verdict(dossier, claim_ref)
        return _make_verdict(
            dossier=dossier,
            claim_ref=claim_ref,
            outcome=ABSTAIN,
            reasons=(),
            may_propose=False,
            requires_review=False,
            citations_checked=(),
        )

    if citations_raw is None or citations_raw == []:
        # A claim with no citation is uncited -- unless the SITE says this one
        # is admissible without any (site C's context-only placement, `105`
        # §14.1: every level supported by an accepted group, which cannot be
        # cited). The site hook names the outcome; the claim then takes the
        # same road as a cited one -- the contradiction oracle, then the site
        # validator, which is where the group support is verified. Nothing
        # here is grounded in file text, so `_acceptance_outcome` is not
        # consulted: with no citations it would answer `accept_direct`.
        admitted = uncited_claim(dossier, raw) if uncited_claim is not None else None
        if admitted is None:
            return _make_verdict(
                dossier=dossier,
                claim_ref=claim_ref,
                outcome=REJECT,
                reasons=(UNCITED_CLAIM,),
                may_propose=False,
                requires_review=False,
                citations_checked=(),
            )
        if oracle is None:
            return ValidationUnavailable(missing=("contradicts",))
        if oracle(payload, dossier):
            return _make_verdict(
                dossier=dossier,
                claim_ref=claim_ref,
                outcome=REJECT,
                reasons=(CONTRADICTED_BY_STRONGER,),
                may_propose=False,
                requires_review=False,
                citations_checked=(),
            )
        verdict = _make_verdict(
            dossier=dossier,
            claim_ref=claim_ref,
            outcome=admitted,
            reasons=(),
            may_propose=True,
            requires_review=admitted == ACCEPT_CONTEXT_SUPPORTED,
            citations_checked=(),
        )
        replacement = site_validator(dossier, raw, verdict)
        if replacement is not None:
            return replacement
        return verdict
    if not isinstance(citations_raw, Sequence) or isinstance(citations_raw, (str, bytes)):
        return schema_invalid_verdict(dossier, claim_ref)

    citations: list[Citation] = []
    for item in citations_raw:
        parsed = parse_citation(item)
        if parsed is None:
            return schema_invalid_verdict(dossier, claim_ref)
        # The model cites the handle it was shown; every check below, the
        # `evidence_resolver` and the recorded `CheckedCitation` all speak P4's
        # own key. Translating once, here, is what keeps them speaking it.
        citations.append(replace(
            parsed,
            evidence_ref=local_ref(parsed.evidence_ref, handles=handles)))
    if not citations:
        return _make_verdict(
            dossier=dossier,
            claim_ref=claim_ref,
            outcome=REJECT,
            reasons=(UNCITED_CLAIM,),
            may_propose=False,
            requires_review=False,
            citations_checked=(),
        )

    checked_all = check_citations(citations, dossier, evidence_resolver)
    if isinstance(checked_all, ValidationUnavailable):
        return checked_all
    checked, reasons = checked_all

    if reasons:
        return _make_verdict(
            dossier=dossier,
            claim_ref=claim_ref,
            outcome=REJECT,
            reasons=reasons,
            may_propose=False,
            requires_review=False,
            citations_checked=checked,
        )

    if oracle is None:
        return ValidationUnavailable(missing=("contradicts",))
    if oracle(payload, dossier):
        return _make_verdict(
            dossier=dossier,
            claim_ref=claim_ref,
            outcome=REJECT,
            reasons=(CONTRADICTED_BY_STRONGER,),
            may_propose=False,
            requires_review=False,
            citations_checked=checked,
        )

    outcome = acceptance_outcome(dossier, citations)
    verdict = _make_verdict(
        dossier=dossier,
        claim_ref=claim_ref,
        outcome=outcome,
        reasons=(),
        may_propose=True,
        requires_review=outcome == ACCEPT_CONTEXT_SUPPORTED,
        citations_checked=checked,
    )
    replacement = site_validator(dossier, raw, verdict)
    if replacement is not None:
        return replacement
    return verdict


def validate_response(
    dossier: Dossier,
    response_bytes: bytes,
    *,
    evidence_resolver,
    site_validator,
    contradicts,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
    handle_key: bytes,
    uncited_claim: Callable[[Dossier, Mapping[str, object]], str | None] | None = None,
) -> tuple[tuple[P8Verdict, ...], GroundingReport] | ValidationUnavailable:
    """Validate recorded response bytes against a released dossier.

    ``uncited_claim`` is a site's answer to "may this claim stand with no
    citation at all?": given the dossier and the raw claim it returns the
    outcome the claim starts from, or ``None`` for the universal answer, which
    is ``UNCITED_CLAIM``. Absent, nothing changes for any site.

    ``evidence_resolver`` maps a P4 ``observation_key`` to the released/redacted
    material the model saw, or ``None`` if that key was not shown.
    ``contradicts`` is the injected contradiction oracle; passing ``None`` when a
    cited claim needs that check is ``ValidationUnavailable``, not a pass.

    ``handle_key`` is the same key the dossier bytes were built with. It is the
    only way back from what the model saw to what this validator checks, and an
    absent one refuses rather than reading the model's references as if they were
    P4 keys.
    """
    missing: list[str] = []
    if evidence_resolver is None:
        missing.append("evidence_resolver")
    if site_validator is None:
        missing.append("site_validator")
    if not isinstance(handle_key, (bytes, bytearray)) or not handle_key:
        missing.append(WIRE_HANDLE_KEY)
    if missing:
        return ValidationUnavailable(missing=tuple(missing))

    oracle = contradicts
    handles = issued_handles(
        (item.evidence_ref for item in dossier.evidence_items), key=handle_key)

    def _finished(verdicts: Sequence[P8Verdict]):
        return (
            tuple(verdicts),
            report_from_verdicts(
                dossier,
                verdicts,
                model_id=model_id,
                prompt_fingerprint=prompt_fingerprint,
                dossier_builder=dossier_builder,
                release_audit_id=release_audit_id,
            ),
        )

    parsed, decode_ref = decode_response(response_bytes)
    if decode_ref is not None:
        return _finished((schema_invalid_verdict(dossier, decode_ref),))

    if not isinstance(parsed, Mapping) or not isinstance(parsed.get("claims"), list):
        return _finished((schema_invalid_verdict(dossier),))

    verdicts: list[P8Verdict] = []
    for index, raw in enumerate(parsed["claims"]):
        result = _validate_claim(
            dossier,
            raw,
            index,
            evidence_resolver=evidence_resolver,
            site_validator=site_validator,
            oracle=oracle,
            handles=handles,
            uncited_claim=uncited_claim,
        )
        if isinstance(result, ValidationUnavailable):
            return result
        verdicts.append(result)
    return _finished(verdicts)


def report_for_pre_call_terminal(
    request: DossierRequest,
    terminal: Refusal | PreCallAbstention,
    *,
    validator_version: str,
) -> GroundingReport:
    """Zero-count report for a pre-egress Refusal or PreCallAbstention.

    Derived solely from the immutable request and terminal. ``NeedsConsent`` is
    not a terminal and emits neither a report nor an event.
    """
    if not isinstance(terminal, (Refusal, PreCallAbstention)):
        raise TypeError(
            "NeedsConsent emits neither report nor event; "
            "report_for_pre_call_terminal requires Refusal or PreCallAbstention"
        )
    reason = terminal.reason
    rung = DEFERRED if reason == BUDGET_EXHAUSTED else REDUCTION_NONE
    return _zero_report(
        request,
        validator_version=validator_version,
        reasons_histogram={reason: 1},
        reduction_rung=rung,
        release_audit_id=None,
        dossier_id=pre_call_address(request.call_site, request.subject_ref),
    )


def report_for_refusal(
    request: DossierRequest,
    refusal: Refusal,
    *,
    validator_version: str,
) -> GroundingReport:
    """Zero-count grounding report for a gate ``Denied`` / ``Refusal``."""
    if not isinstance(refusal, Refusal):
        raise TypeError("report_for_refusal requires a gate Refusal")
    return report_for_pre_call_terminal(
        request, refusal, validator_version=validator_version,
    )


def report_for_call_failure(
    request: DossierRequest,
    failed: CallFailed,
    *,
    validator_version: str,
) -> GroundingReport:
    """Zero-count issued-call report: real ``release_audit_id``, empty histogram."""
    if not isinstance(failed, CallFailed):
        raise TypeError("report_for_call_failure requires CallFailed")
    return _zero_report(
        request,
        validator_version=validator_version,
        reasons_histogram={},
        reduction_rung=REDUCTION_NONE,
        release_audit_id=failed.audit_id,
        dossier_id=failed.request_identity,
    )
