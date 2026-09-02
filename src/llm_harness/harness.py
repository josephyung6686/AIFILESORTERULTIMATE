# src/llm_harness/harness.py
"""Compose P7 gate branches into one P8 evaluation. Consent is never converted.

`run_call` is the only public evaluation callable. It does not invoke a model
client; `transport.issue` is the sole egress. Q8 leaves retry disabled: one
attempt, then `CallFailed` or a schema-invalid `P8Verdict`.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass, fields
from decimal import Decimal

from database_agent.db import transaction
from llm_harness.authorship import COMPONENT_VERSION
from llm_harness.budgets import (
    BudgetExhausted,
    ScanBudget,
    plan_reduction,
    release_reservation,
    reserve_call,
    settle_call,
)
from llm_harness.dossier import build_dossier, canonical_dossier_bytes
from llm_harness.eligibility import Eligible, assess_call
from llm_harness.placement_validation import record_cd_verdict
from llm_harness.sites import SiteDependencies, dispatch
from llm_harness.records import (
    CallFailed,
    DossierRequest,
    P8Verdict,
    PreCallAbstention,
    PromptDefinition,
    Refusal,
    ValidationUnavailable,
    build_call_payload,
)
from llm_harness.store import (
    record_dossier,
    record_grounding_report,
    record_pre_call_abstention,
    record_refusal,
    record_verdict,
)
from llm_harness.transport import ModelClient, ModelResponse, issue
from llm_harness.validation import (
    report_for_refusal,
    DOSSIER_BUILDER,
    report_for_call_failure,
    report_for_pre_call_terminal,
)
from llm_harness.vocabulary import (
    OUTCOME_SEVERITY,
    pre_call_address,
    SITES_REQUIRING_EVIDENCE_SNAPSHOT,
    A_FACT,
    ABSTAIN,
    B_GROUP,
    BUDGET_EXHAUSTED,
    C_PLACEMENT,
    D_RESIDUAL,
    DEFERRED,
    E_TEMPLATE,
    SCOPE_FILE,
    SCOPE_GROUP,
    SCOPE_NODE,
    SCOPE_TEMPLATE,
    SPLIT,
)
from privacy.gate import Gate
from privacy.release import (
    Denied, MalformedRequest, NeedsConsent, NoPolicyInForce, Released,
)

_SCOPE_BY_SITE = {
    A_FACT: SCOPE_FILE,
    B_GROUP: SCOPE_GROUP,
    C_PLACEMENT: SCOPE_NODE,
    D_RESIDUAL: SCOPE_FILE,
    E_TEMPLATE: SCOPE_TEMPLATE,
}

_BOOL_FLAGS = frozenset({"unreduced_fits", "summarized_fits", "anchors_fit"})
_NONE_OK = frozenset({"split_shard_fits", "split_shards", "estimated_cost", "actual_cost"})
_CALLABLES = frozenset({"evidence_resolver", "contradicts"})
_TYPED = {"site_dependencies": SiteDependencies}


@dataclass(frozen=True, slots=True)
class CallDependencies:
    """Injected authorities for one `run_call`. No prompt, threshold, or oracle defaults."""

    proposal_class: str | None
    basis_key: str | None
    learning_scope: str | None
    learning_subject_id: str | None
    evidence_resolver: object
    site_dependencies: SiteDependencies | None
    contradicts: object
    unreduced_fits: object
    summarized_fits: object
    anchors_fit: object
    split_shard_fits: object
    split_shards: object
    scan_budget: ScanBudget | None
    estimated_cost: Decimal | None
    actual_cost: Decimal | None
    allowed_vocabulary: Sequence[str] | None
    policy_version: str | None
    #: The local-only key every identifier leaving this device is digested under
    #: (`llm_harness.wire_handles`). It is a credential: it is chosen at the
    #: composition root, it never reaches a screen, a log, an audit row or the
    #: wire, and an absent one is reported missing rather than replaced by an
    #: un-keyed digest a recipient can reverse.
    wire_handle_key: bytes | None


def _missing_from_deps(deps: object) -> tuple[str, ...]:
    missing: list[str] = []
    for item in fields(CallDependencies):
        value = getattr(deps, item.name, None)
        if item.name in _BOOL_FLAGS:
            if value is not True and value is not False:
                missing.append(item.name)
            continue
        if item.name in _CALLABLES:
            if not callable(value):
                missing.append(item.name)
            continue
        if item.name in _TYPED:
            if not isinstance(value, _TYPED[item.name]):
                missing.append(item.name)
            continue
        if item.name in _NONE_OK:
            if value is None:
                missing.append(item.name)
            continue
        if not value:
            missing.append(item.name)
    return tuple(missing)


def _missing_configuration(
    conn, *, gate, model_client, prompt, validation_dependencies,
) -> tuple[str, ...]:
    missing: list[str] = []
    if conn is None:
        missing.append("conn")
    if gate is None:
        missing.append("gate")
    if not isinstance(prompt, PromptDefinition):
        missing.append("prompt")
    if not isinstance(model_client, ModelClient):
        missing.append("model_client")
    if validation_dependencies is None:
        missing.extend(item.name for item in fields(CallDependencies))
        return tuple(missing)
    missing.extend(_missing_from_deps(validation_dependencies))
    return tuple(missing)


def _missing_request_inputs(request: DossierRequest) -> tuple[str, ...]:
    """What the call site itself requires of the request, checked before the spend.

    `record_cd_verdict` requires `evidence_snapshot_id` at C and D and raised only
    after the release was consumed, the model was called and the response was
    stored: a call paid for that produced no verdict and no report. Nothing in
    `DossierRequest.__post_init__` requires it, because A and B do not.
    """
    if request.call_site in SITES_REQUIRING_EVIDENCE_SNAPSHOT and (
            not request.evidence_snapshot_id):
        return ("evidence_snapshot_id",)
    return ()


def _pre_call_verdict(
    request: DossierRequest, terminal: PreCallAbstention, *, policy_version: str,
) -> P8Verdict:
    address = pre_call_address(request.call_site, request.subject_ref)
    return P8Verdict(
        verdict_id=f"{address}:{terminal.reason}",
        dossier_id=address,
        claim_ref="pre-call",
        outcome=ABSTAIN,
        disposition=ABSTAIN,
        reasons=(terminal.reason,),
        may_propose=False,
        requires_review=False,
        citations_checked=(),
        scope=_SCOPE_BY_SITE[request.call_site],
        validator_version=COMPONENT_VERSION,
        policy_version=policy_version,
        plan_version=request.plan_version,
    )


def _persist_abstention(
    conn: sqlite3.Connection,
    request: DossierRequest,
    terminal: PreCallAbstention, *,
    observed_at: str,
    policy_version: str,
) -> P8Verdict:
    report = report_for_pre_call_terminal(
        request, terminal, validator_version=COMPONENT_VERSION,
    )
    record_pre_call_abstention(conn, terminal, report, observed_at=observed_at)
    return _pre_call_verdict(request, terminal, policy_version=policy_version)


def _persist_refusal(
    conn: sqlite3.Connection,
    request: DossierRequest,
    denied: Denied, *,
    observed_at: str,
    policy_version: str,
) -> Refusal:
    refusal = Refusal(
        denied=denied,
        validator_version=COMPONENT_VERSION,
        policy_version=policy_version,
    )
    # One entry point for the refusal report. `report_for_refusal` existed with no
    # caller in `src/` while this built the same report by hand, so the two paths
    # could drift apart without a test noticing.
    report = report_for_refusal(
        request, refusal, validator_version=COMPONENT_VERSION)
    record_refusal(conn, refusal, report, observed_at=observed_at)
    return refusal


def _units(request: DossierRequest, deps: CallDependencies, rung: str):
    if rung != SPLIT:
        return (request,)
    shards = tuple(deps.split_shards)
    fits = tuple(deps.split_shard_fits)
    return tuple(
        shard for shard, fits_flag in zip(shards, fits) if fits_flag is True
    )


def _record_verdicts(
    conn: sqlite3.Connection,
    request: DossierRequest,
    verdicts: Sequence[P8Verdict], *,
    model_id: str,
    prompt_fingerprint: str,
    release_audit_id: int,
    observed_at: str,
) -> None:
    for verdict in verdicts:
        if request.call_site in (C_PLACEMENT, D_RESIDUAL):
            record_cd_verdict(
                conn, verdict,
                evidence_snapshot_id=request.evidence_snapshot_id or "",
                model_id=model_id,
                prompt_fingerprint=prompt_fingerprint,
                release_audit_id=release_audit_id,
                observed_at=observed_at,
            )
        else:
            record_verdict(
                conn, verdict,
                model_id=model_id,
                prompt_fingerprint=prompt_fingerprint,
                release_audit_id=release_audit_id,
                observed_at=observed_at,
            )


def _issue_and_validate(
    conn: sqlite3.Connection,
    request: DossierRequest,
    released: Released, *,
    prompt: PromptDefinition,
    model_client: ModelClient,
    deps: CallDependencies,
    reduction_rung: str,
    observed_at: str,
) -> P8Verdict | CallFailed | ValidationUnavailable:
    dossier = build_dossier(
        request, released,
        reduction_rung=reduction_rung,
        allowed_vocabulary=deps.allowed_vocabulary,
        prompt=prompt,
        handle_key=deps.wire_handle_key,
    )
    if isinstance(dossier, ValidationUnavailable):
        return dossier
    payload = build_call_payload(
        prompt,
        canonical_dossier_bytes(dossier, prompt, handle_key=deps.wire_handle_key),
        model_target=released.model_target,
        policy_version=released.policy_version,
        release_id=released.release_id,
        dossier_id=dossier.dossier_id,
    )
    record_dossier(conn, dossier, observed_at=observed_at)
    result = issue(conn, released, payload, model_client=model_client)
    if isinstance(result, CallFailed):
        report = report_for_call_failure(
            request, result, validator_version=COMPONENT_VERSION,
        )
        record_grounding_report(conn, report, observed_at=observed_at)
        return result
    if not isinstance(result, ModelResponse):
        return ValidationUnavailable(missing=("model_response",))
    # One transaction spans the consequence and the verdict that justifies it.
    # Site A's dispatch writes P6's fact; `_record_verdicts` writes the P8 row
    # about it. Split, a failure between them leaves P6 holding an
    # `llm_supported` fact whose judgement nothing records.
    with transaction(conn):
        return _validate_and_record(
            conn, request, dossier, result, released,
            deps=deps, observed_at=observed_at,
        )


def worst_outcome(verdicts: Sequence[P8Verdict]) -> P8Verdict:
    """The single verdict a call returns when it produced several.

    `vocabulary.OUTCOME_SEVERITY` states the rule as "one per shard, one per
    claim" and both halves are reduced here, by ONE function. They were two
    expressions -- the shard reducer used severity and the claim reducer took the
    last verdict by position -- and the fix that landed the first never reached
    the second, so a two-claim response whose FIRST claim was rejected returned
    `accept_direct`. A caller told `accept_direct` must be able to take it as
    true of the whole call.
    """
    return min(verdicts, key=lambda verdict: OUTCOME_SEVERITY.index(verdict.outcome))


def _validate_and_record(
    conn: sqlite3.Connection,
    request: DossierRequest,
    dossier,
    result: ModelResponse,
    released: Released,
    *,
    deps: CallDependencies,
    observed_at: str,
) -> P8Verdict | ValidationUnavailable:
    checked = dispatch(
        conn,
        dossier,
        result.response_bytes,
        site_dependencies=deps.site_dependencies,
        evidence_resolver=deps.evidence_resolver,
        contradicts=deps.contradicts,
        model_id=result.model_id,
        prompt_fingerprint=result.prompt_fingerprint,
        dossier_builder=DOSSIER_BUILDER,
        release_audit_id=released.audit_id,
        policy_version=dossier.policy_version,
        apply_consequence=True,
        handle_key=deps.wire_handle_key,
    )
    if isinstance(checked, ValidationUnavailable):
        return checked
    verdicts, report = checked
    _record_verdicts(
        conn, request, verdicts,
        model_id=result.model_id,
        prompt_fingerprint=result.prompt_fingerprint,
        release_audit_id=released.audit_id,
        observed_at=observed_at,
    )
    record_grounding_report(conn, report, observed_at=observed_at)
    if not verdicts:
        return ValidationUnavailable(missing=("claims",))
    # One call, one returned verdict, chosen by severity and not by position.
    return worst_outcome(verdicts)


def run_call(
    conn,
    request: DossierRequest, *,
    gate: Gate,
    model_client: ModelClient,
    prompt: PromptDefinition | None,
    validation_dependencies,
    observed_at: Callable[[], str],
) -> (
    P8Verdict | Refusal | NeedsConsent |
    ValidationUnavailable | CallFailed
):
    """Evaluate one reference-only request. NeedsConsent is returned unchanged."""
    missing = _missing_configuration(
        conn, gate=gate, model_client=model_client, prompt=prompt,
        validation_dependencies=validation_dependencies,
    )
    if missing:
        return ValidationUnavailable(missing=missing)
    missing = _missing_request_inputs(request)
    if missing:
        return ValidationUnavailable(missing=missing)

    deps = validation_dependencies
    eligibility = assess_call(
        request,
        conn=conn,
        learning_scope=deps.learning_scope,
        learning_subject_id=deps.learning_subject_id,
        proposal_class=deps.proposal_class,
        basis_key=deps.basis_key,
    )
    stamp = observed_at()
    if isinstance(eligibility, ValidationUnavailable):
        return eligibility
    if isinstance(eligibility, PreCallAbstention):
        return _persist_abstention(
            conn, request, eligibility, observed_at=stamp,
            policy_version=deps.policy_version,
        )
    if not isinstance(eligibility, Eligible):
        return ValidationUnavailable(missing=("eligibility",))

    reduction = plan_reduction(
        unreduced_fits=deps.unreduced_fits,
        summarized_fits=deps.summarized_fits,
        anchors_fit=deps.anchors_fit,
        split_shard_fits=deps.split_shard_fits,
        call_site=request.call_site,
        subject_ref=request.subject_ref,
    )
    if reduction.rung == DEFERRED:
        return _persist_abstention(
            conn, request, reduction.abstention, observed_at=stamp,
            policy_version=deps.policy_version,
        )

    produced: list[P8Verdict] = []
    for unit in _units(request, deps, reduction.rung):
        try:
            reservation = reserve_call(
                conn, deps.scan_budget, estimated_cost=deps.estimated_cost,
            )
        except BudgetExhausted:
            exhausted = PreCallAbstention(
                reason=BUDGET_EXHAUSTED,
                call_site=unit.call_site,
                subject_ref=unit.subject_ref,
            )
            persisted = _persist_abstention(
                conn, unit, exhausted, observed_at=observed_at(),
                policy_version=deps.policy_version,
            )
            produced.append(persisted)
            break

        try:
            decision = gate.release(unit.model_call_request)
        except (MalformedRequest, NoPolicyInForce):
            # BOTH of the gate's non-decisions, for the reason the comment below
            # `_issue_and_validate` gives: a raise between `reserve_call` and
            # `settle_call` that does not release the reservation takes a call and
            # its estimated cost out of the scan budget permanently, with nothing
            # left holding the id. `MalformedRequest` joined that set on 2026-09-02
            # -- the gate now refuses a requested item it has no reading for rather
            # than dropping it from the release -- and a refusal that silently
            # spends a budget slot would be its own smaller version of the same
            # defect.
            release_reservation(conn, reservation)
            raise

        if isinstance(decision, NeedsConsent):
            release_reservation(conn, reservation)
            return decision
        if isinstance(decision, Denied):
            release_reservation(conn, reservation)
            return _persist_refusal(
                conn, unit, decision, observed_at=observed_at(),
                policy_version=deps.policy_version,
            )
        if not isinstance(decision, Released):
            release_reservation(conn, reservation)
            return ValidationUnavailable(missing=("release_decision",))

        try:
            issued = _issue_and_validate(
                conn, unit, decision,
                prompt=prompt,
                model_client=model_client,
                deps=deps,
                reduction_rung=reduction.rung,
                observed_at=observed_at(),
            )
        except BaseException:
            # Only the gate's own terminal decisions released the reservation.
            # Every other raise between `reserve_call` and `settle_call` --
            # a binding mismatch, an open transaction, a malformed record, an
            # interrupt -- removed a call and its estimated cost from the scan
            # budget permanently, with nothing left holding the reservation id.
            release_reservation(conn, reservation)
            raise
        settle_call(conn, reservation, actual_cost=deps.actual_cost)
        if isinstance(issued, CallFailed):
            return issued
        if isinstance(issued, ValidationUnavailable):
            return issued
        produced.append(issued)
    if not produced:
        return ValidationUnavailable(missing=("fitting_shard",))
    # One call, one returned verdict, chosen by severity and not by position.
    return worst_outcome(produced)
