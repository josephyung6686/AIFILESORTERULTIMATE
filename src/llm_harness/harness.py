# src/llm_harness/harness.py
"""Compose P7 gate branches into one P8 evaluation. Consent is never converted.

`run_call` is the only public evaluation callable. It does not invoke a model
client; `transport.issue` is the sole egress. Q8 leaves retry disabled: one
attempt, then `CallFailed` or a schema-invalid `P8Verdict`.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, fields, replace
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
    REFUSAL_EXCEPTIONS,
    CallFailed,
    CallRefused,
    DossierRequest,
    P8Verdict,
    PreCallAbstention,
    PromptDefinition,
    Refusal,
    ValidationUnavailable,
    build_call_payload,
)
from llm_harness.store import (
    record_call_refusal,
    record_call_usage,
    refusal_outcome,
    record_dossier,
    record_grounding_report,
    record_pre_call_abstention,
    record_refusal,
    record_verdict,
)
from llm_harness.transport import ModelClient, ModelResponse, _issue_steps
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
    G_SITUATION_SENSITIVITY,
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
#: `104` §18.15: WHICH LANE A CALL BELONGS TO, in P7's own word for it. Read off
#: `_PendingSend.locality`, which is `released.model_target.locality` -- the value
#: `Gate.release` decided by and `consume_release` has already checked against the
#: ledger row. A driver that decided the lane from anything else would be a second
#: answer to "may this leave the device", and the two would drift.
from privacy.vocabulary import CLOUD_LOCALITY
_SCOPE_BY_SITE = {
    A_FACT: SCOPE_FILE,
    B_GROUP: SCOPE_GROUP,
    C_PLACEMENT: SCOPE_NODE,
    D_RESIDUAL: SCOPE_FILE,
    E_TEMPLATE: SCOPE_TEMPLATE,
    # `104` §17.1's seventh site, and the same scope `validation._SCOPE_BY_SITE`
    # gives it: one file version is what a situation verdict is about.
    G_SITUATION_SENSITIVITY: SCOPE_FILE,
}

_BOOL_FLAGS = frozenset({"unreduced_fits", "summarized_fits", "anchors_fit"})
#: `folder_levels` joins these because EMPTY is a truthful answer at B, C and D --
#: they design no folder tree -- while `None` is a caller who never read the
#: template library. The site that does design one refuses an empty list at
#: composition, where the mistake is legible.
_NONE_OK = frozenset({"split_shard_fits", "split_shards", "estimated_cost",
                      "actual_cost", "folder_levels"})
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
    #: The folder levels of the situation the person named, in the template
    #: library's order. A projection of `allowed_vocabulary` above it and never a
    #: second vocabulary.
    #:
    #: **No default, like every other field here**, which
    #: `test_p8_no_invention.py::test_configurable_callbacks_thresholds_and_prompts
    #: _have_no_defaults` enforces over this whole class: absent means refuse, never
    #: guess. `()` is a legal VALUE and it is the truthful one at B, C and D, which
    #: design no folder tree -- so it is in `_NONE_OK` above, where an empty list
    #: passes and a `None` is reported missing. Site A does design one, and the
    #: emptiness it must not have is refused a layer up, at
    #: `model_facts.require_folder_levels`.
    folder_levels: Sequence[object] | None


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
    conn, *, request, gate, model_client, prompt, validation_dependencies,
) -> tuple[str, ...]:
    missing: list[str] = []
    if conn is None:
        missing.append("conn")
    if gate is None:
        missing.append("gate")
    if not isinstance(prompt, PromptDefinition):
        missing.append("prompt")
    elif prompt.call_site != request.call_site:
        # THE PROMPT'S OWN SITE, read for the first time. `PromptDefinition`
        # carries `call_site` and nothing checked it against the request's.
        #
        # The dossier the model is shown carries THIS prompt's `response_schema`
        # and `shaping_policy` (`dossier._body`), while `validate_response`
        # dispatches on the REQUEST's site. A prompt built for one site and sent
        # at another therefore shows the model one contract and measures it
        # against a different one -- `model_facts.pending_fields_for` names that
        # exact failure: "a model measured against one list and validated against
        # another can be rejected for obeying its instructions".
        #
        # It was live, not hypothetical: `cli.observe_placement_injections` handed
        # site D site C's prompt, because `_judge_with_model` served both from one
        # `PipelineInputs` field. This is the wall at the one place that holds the
        # request and the prompt together, so any other wiring of the same mistake
        # is caught here rather than in a verdict nobody can account for.
        missing.append("prompt_call_site")
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


def _issue_and_validate_steps(
    conn: sqlite3.Connection,
    request: DossierRequest,
    released: Released, *,
    prompt: PromptDefinition,
    model_client: ModelClient,
    deps: CallDependencies,
    reduction_rung: str,
    observed_at: str,
    usage_recorder: object | None = None,
):
    """`104` §18.15: the dossier, then the socket as a suspension point, then the
    verdict. Returns `(outcome, usage)` for `_issue_steps`' own reason.
    """
    dossier = build_dossier(
        request, released,
        reduction_rung=reduction_rung,
        allowed_vocabulary=deps.allowed_vocabulary,
        folder_levels=deps.folder_levels,
        prompt=prompt,
        handle_key=deps.wire_handle_key,
    )
    if isinstance(dossier, ValidationUnavailable):
        return dossier, None
    payload = build_call_payload(
        prompt,
        canonical_dossier_bytes(dossier, prompt, handle_key=deps.wire_handle_key),
        model_target=released.model_target,
        policy_version=released.policy_version,
        release_id=released.release_id,
        dossier_id=dossier.dossier_id,
    )
    record_dossier(conn, dossier, observed_at=observed_at)
    result, usage = yield from _issue_steps(
        conn, released, payload, model_client=model_client,
        usage_recorder=usage_recorder)
    if isinstance(result, CallFailed):
        report = report_for_call_failure(
            request, result, validator_version=COMPONENT_VERSION,
        )
        record_grounding_report(conn, report, observed_at=observed_at)
        return result, usage
    if not isinstance(result, ModelResponse):
        return ValidationUnavailable(missing=("model_response",)), usage
    # One transaction spans the consequence and the verdict that justifies it.
    # Site A's dispatch writes P6's fact; `_record_verdicts` writes the P8 row
    # about it. Split, a failure between them leaves P6 holding an
    # `llm_supported` fact whose judgement nothing records.
    with transaction(conn):
        return _validate_and_record(
            conn, request, dossier, result, released,
            deps=deps, observed_at=observed_at,
        ), usage


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
    # `104` §18.2 GAP 5: THE BUILDER'S CUT, STAMPED ONTO THE VALIDATOR'S REPORT.
    #
    # The count belongs on the report because that is where a call's counters live
    # and where the scorecard reads them; it cannot be COMPUTED there because the cut
    # happened in `model_facts`' fill, before a dossier existed, and the validator is
    # shown only what was released. Threading it through `dispatch` and
    # `validate_response` would hand every site's validator a number it must not use
    # for anything, so it is copied here instead -- the one place in the harness that
    # holds the request the builder wrote and the report that is about to be stored.
    #
    # `_zero_report` reads the same two fields off the same request directly, so a
    # refused, deferred or failed call reports the cut too and the two paths cannot
    # disagree about what the ceiling took.
    report = replace(
        report,
        readings_dropped=request.readings_dropped,
        readings_dropped_bytes=request.readings_dropped_bytes,
    )
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
    usage_recorder: object | None = None,
) -> (
    P8Verdict | Refusal | NeedsConsent |
    ValidationUnavailable | CallFailed | CallRefused
):
    """`run_call_steps` with the round trip where it has always been: right here.

    `104` §18.15 split the body into a generator so the cloud lane could hold
    several round trips at once. This is that generator driven to its end on this
    thread, one call and one answer, and it is what every caller that does not own
    a lane still gets. Sites B, D, E and G reach a model through this line and
    through nothing else, and none of them changed.
    """
    return drive_inline(run_call_steps(
        conn, request, gate=gate, model_client=model_client, prompt=prompt,
        validation_dependencies=validation_dependencies,
        observed_at=observed_at, usage_recorder=usage_recorder))


def run_call_steps(
    conn,
    request: DossierRequest, *,
    gate: Gate,
    model_client: ModelClient,
    prompt: PromptDefinition | None,
    validation_dependencies,
    observed_at: Callable[[], str],
    usage_recorder: object | None = None,
):
    """Evaluate one reference-only request. NeedsConsent is returned unchanged.

    `usage_recorder` is `104` R-14's one-slot mailbox and is OPTIONAL, unlike every
    field of `CallDependencies`: that bundle is for authorities a caller must
    supply, and a deployment that records no usage is a real deployment -- the local
    transport has no such reading to give and neither does a test's byte recorder.
    Absent, nothing is written and nothing else changes.

    Its whole protocol is `take()`, answering the composition root's translation of
    what the provider reported for the call just made, `{}` when the provider
    reported nothing, and `None` when no call was made. It is read HERE because this
    is the only place that holds the reservation, the release and the dossier at one
    moment; `llm_harness` may not import `readers`, so what crosses this line is a
    mapping whose keys `store.record_call_usage` checks, never a provider's type.

    **`104` §18.15: IT IS A GENERATOR, AND ONE `yield` IS THE WHOLE OF IT.** Every
    statement below stays where it was and runs on the thread that owns `conn` --
    the reservation, the release, the audit row, the dossier, the response, the
    verdicts, the settlement, the usage row. The one thing that leaves is the
    socket, and it leaves as a `_PendingSend` the driver may run wherever it likes.
    Read this function as the straight line it still is; the suspension point is
    inside `_issue_steps`, where the bytes are finished and there is nothing left to
    decide.

    R-14'S MAILBOX IS NOW READ OFF THE RESUME AND NOT OFF `take()`. The mailbox has
    one slot per thread, so the thread that made the call is the only one that can
    empty it honestly; `_PendingSend.perform` does that, and the reading comes back
    here with the outcome. On the serial path this is the same value at the same
    moment, taken one function deeper.
    """
    missing = _missing_configuration(
        conn, request=request, gate=gate, model_client=model_client, prompt=prompt,
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
        except REFUSAL_EXCEPTIONS as refusal:
            # `104` R-O. The reservation goes back first, for the reason the
            # comment below `_issue_and_validate` gives: a raise between
            # `reserve_call` and `settle_call` that does not release the
            # reservation takes a call and its estimated cost out of the scan
            # budget permanently, with nothing left holding the id. On a scan
            # budget of one, the file AFTER the refusal would then be refused for
            # a reason that was not about it.
            #
            # AND THEN IT IS AN OUTCOME RATHER THAN A RAISE. Twice on a real
            # corpus this raise reached `main` -- `UnresolvableSpan` after
            # thirty-seven minutes of fact calls, `MalformedRequest` after
            # forty-eight -- and each time the person got a traceback instead of
            # the report the run had already earned. `00` §8 and `104` §7's Phase
            # 1 step 6 say the call is recorded as refused, by reason, and the run
            # goes on; `UnresolvableSpan` was not even in the old tuple, so it
            # also leaked the slot on its way out.
            release_reservation(conn, reservation)
            return refusal_outcome(
                conn, call_site=unit.call_site, subject_ref=unit.subject_ref,
                error=refusal, observed_at=observed_at())
        except NoPolicyInForce:
            # NOT a per-subject refusal: a run with no policy in force is
            # misconfigured for every call it will ever make, and one loud stop is
            # better for the person than 199 identical rows. The reservation is
            # still given back, so a caller that catches this can carry on.
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
            issued, observed = yield from _issue_and_validate_steps(
                conn, unit, decision,
                prompt=prompt,
                model_client=model_client,
                deps=deps,
                reduction_rung=reduction.rung,
                observed_at=observed_at(),
                usage_recorder=usage_recorder,
            )
        except REFUSAL_EXCEPTIONS as refusal:
            # `104` R-O on the far side of the release. `model_facts` records what
            # this cost at site B -- "every unbounded observation refused with
            # `UnresolvableSpan` after the release had been minted" -- so the
            # refusal is not confined to the door. Settled rather than released:
            # the release was spent, and a slot given back here would let one
            # scan pay for a call twice.
            settle_call(conn, reservation, actual_cost=deps.actual_cost)
            return refusal_outcome(
                conn, call_site=unit.call_site, subject_ref=unit.subject_ref,
                error=refusal, observed_at=observed_at())
        except BaseException:
            # Only the gate's own terminal decisions released the reservation.
            # Every other raise between `reserve_call` and `settle_call` --
            # a binding mismatch, an open transaction, a malformed record, an
            # interrupt -- removed a call and its estimated cost from the scan
            # budget permanently, with nothing left holding the reservation id.
            release_reservation(conn, reservation)
            raise
        settle_call(conn, reservation, actual_cost=deps.actual_cost)
        # `104` R-14, AFTER the settlement and never instead of it. The budget's
        # unit is calls -- `cli.FACT_CALL_COST` is 1 against a 200-per-scan ceiling
        # -- and this changes nothing it enforces: it records what was RESERVED
        # beside what the provider says was CONSUMED, so the distance between the
        # estimate and the truth is readable per call and per scan. Re-denominating
        # the ceiling in tokens is the owner's question.
        #
        # Written whichever way the call went, because the release was spent and the
        # budget settled either way: an `issued` that is a `CallFailed` still cost a
        # call. `dossier_id` comes off whichever of the two carries it -- both name
        # the dossier, `CallFailed` under `request_identity`.
        #
        # `104` §18.15: `observed` came back from the resume rather than from a
        # `take()` here, because the thread that made the call is the only one
        # that can empty a one-slot-per-thread mailbox and have it mean this call.
        if usage_recorder is not None:
            if observed is not None:
                record_call_usage(
                    conn,
                    dossier_id=getattr(issued, "dossier_id", None)
                    or getattr(issued, "request_identity", ""),
                    release_id=decision.release_id,
                    reserved_cost=format(deps.estimated_cost, "f"),
                    observed=observed, observed_at=observed_at())
        if isinstance(issued, CallFailed):
            return issued
        if isinstance(issued, ValidationUnavailable):
            return issued
        produced.append(issued)
    if not produced:
        return ValidationUnavailable(missing=("fitting_shard",))
    # One call, one returned verdict, chosen by severity and not by position.
    return worst_outcome(produced)


# ======================================================================
# `104` §18.15: HOW A RUN DRIVES ITS CALLS, and the only place a second
# thread exists in this product's model path.
#
# The owner's direction of 9 and 10 September: local is too slow, the cloud
# is what ships, run it in parallel. What that can mean here is bounded by
# one fact -- sqlite has a single writer and a connection belongs to the
# thread that made it -- so what runs at once is the round trip and nothing
# else. `run_call_steps` hands out a `_PendingSend` when its bytes are
# finished and every decision about them is already recorded; these two
# functions are the two ways to run one.
# ======================================================================


def drive_inline(steps):
    """Run one call's steps here, on this thread, to the end.

    The serial path, unchanged in every observable way: the socket is invoked
    between the same two statements it always was.
    """
    try:
        pending = next(steps)
        while True:
            pending = steps.send(pending.perform())
    except StopIteration as done:
        return done.value


@dataclass
class CallLane:
    """How many round trips a pass may hold at once, and how many it ever held.

    **`width` IS NOT A NUMBER THIS MODULE CHOOSES.** `104` §18.15's direction is
    to run the cloud lane wider, not to invent a second answer to "how much of
    this machine may one run take": the composition root already picked that when
    it chose how many processes read files at once, and it passes the same count
    here. A lane this module sized for itself would be a knob nobody could find
    and a second number to keep in step with the first.

    `at_once` is the widest window this pass actually opened -- what the printed
    sentence reports. It is a MEASUREMENT and not a setting: a corpus whose cloud
    files never sit next to each other opens windows of one and says so.

    `reused` is the other measurement, and it is the one that says a question was
    NOT bought: how many parked sends this pass answered out of another send's
    round trip because the two carried byte-identical bytes to the same client
    (`104` §18.28). Like `at_once` it counts what happened rather than setting
    anything, and a corpus with no duplicate in any one batch reports zero.
    """

    width: int
    at_once: int = 0
    reused: int = 0

    def __post_init__(self) -> None:
        if (not isinstance(self.width, int) or isinstance(self.width, bool)
                or self.width < 1):
            raise ValueError(
                f"a lane holds at least one call at a time and {self.width!r} is "
                f"not such a count. A width of zero is not a narrow lane; it is a "
                f"pass that prepares every call and sends none.")


@dataclass
class _Slot:
    """One walked subject's place in the batch, held so the order survives."""

    key: object
    steps: object = None
    #: Whatever the steps handed up: a thing with a `locality` and a `perform`. It
    #: is NOT named as a type, because the type is `transport._PendingSend` and that
    #: class is private for P7's own reason -- the driver never builds one, it only
    #: runs the one it was given.
    pending: object = None
    value: object = None


def in_walk_order(started, *, lane: CallLane, on_pause=None, on_resume=None):
    """Drive many calls, several cloud round trips at once, in WALK ORDER.

    `started` is `(key, steps)` pairs in the order the run walked its subjects --
    the roster order at site A, the subject order at site C. Yields
    `(key, returned_value)` in that same order, whichever call came back first.

    **THE SHAPE, and every rule of `104` §18.15's build is one of these lines.**

    1. Each subject's steps are advanced HERE, on this thread, in walk order. That
       advance is the whole of the call up to the socket: the dossier, the call
       identity, the reuse lookup, the budget reservation, the gate's release and
       its audit row. A subject that never reaches a socket -- a reuse, a decline,
       a refusal, a file no route permits -- finishes inside that advance and is
       held in the batch so that its result still leaves in turn.
    2. A cloud send is PARKED. The loop moves on and prepares the next subject
       while it waits, which is the whole gain: r19 spent nine hours on 223
       dossiers with every call, cloud or local, one after another (§18.22).
    3. A LOCAL send joins the batch too, and is performed ON THIS THREAD while the
       cloud sends of the same batch are in the air. That is the whole of the local
       rule and it is narrower than "the local call runs alone": there is ONE local
       lane and this thread is it, so two local sends can no more overlap than one
       thread can be in two places. One Ollama server holds one model in memory and
       a second concurrent local call is what filled the machine's swap in r18
       (§17.21) -- that is a statement about two LOCAL calls, and a cloud socket
       waiting beside one costs the server nothing.

       **IT JOINS ONLY WHEN THERE IS CLOUD WORK TO OVERLAP.** With nothing parked
       there is nothing to be beside, and holding a local call back would mint its
       release early for no gain, so it is settled at once -- a batch of one send,
       performed inline, which is the path this driver has always had. A run with
       no cloud target therefore behaves exactly as it did before the lane existed.

       The first draft settled the batch BEFORE every local send and ran it by
       itself. That is stricter than `104` §18.15 asks -- the direction is that the
       local lane stays serial, not that it stops the world -- and it cost the
       whole gain on the corpus the direction is about: site A's cloud share was
       47% (§18.22), so a walk that alternates would have settled a batch of one or
       two, over and over, and the lane would have been a lane in name.
    4. The batch settles when it is full and at the end. Settling submits the cloud
       sends, runs the local ones here in turn, gathers the cloud answers, and then
       resumes each generator IN WALK ORDER -- so every row after a response, the
       verdict, the fact, the supersession, the usage, the settlement, is written
       in the order the files were walked and not in the order the provider
       answered. Two runs over one corpus write the same rows in the same order.

    **WHAT THIS CHANGES ABOUT ORDER, STATED RATHER THAN BURIED.** Inside one batch
    a later file's PREPARATION now precedes an earlier file's RESPONSE, because
    that is what "several at once" means. One consequence, bounded: a per-file
    clock that is charged by turns sees the batch's shared wait, which `on_pause`
    is for.

    5. **THE SAME QUESTION IS ASKED ONCE PER BATCH** (`104` §18.28). Two subjects
       whose prepared bytes are identical, to the same client, are one question:
       the first is sent, the later ones wait for its answer and are handed it.
       Until this rule the batch asked both and paid twice, and the reuse that
       exists -- `llm_call_identity`, written AFTER the call -- could not fire
       inside a window where nothing has been written yet. R-13's cache is about a
       PRIOR RUN's answer and is untouched; this is about a duplicate standing
       beside its twin in one window.

       **THE KEY IS THE BYTES ON THE WIRE AND NOTHING SOFTER.** `assemble` is the
       template plus the canonical dossier and carries no provenance, so equal
       bytes are the same prompt about the same content -- and unequal bytes, for
       whatever reason, are asked. A looser key would hand one file the answer to
       another file's question, which is the one mistake this product may not make
       to save a call. Walk order decides which is the asking one, so the twin is
       always the later subject and two runs over one corpus spend the same call.

       **A FAILURE IS NOT REUSED.** If the asking send comes back carrying an
       error, the twin performs its own send, in its turn on this thread: a
       provider that timed out bought no answer, and handing the same failure to
       both files would spend a second file's chance on the first one's bad
       minute. Only an answer is shared, and the shared copy carries no usage --
       the twin consumed no tokens and must not be recorded as if it had.

    **`on_pause` AND `on_resume` ARE `104` R-175's CLOCK, AND THE PAIR IS WHAT
    KEEPS IT HONEST.** That clock charges a file for the time the run spends with
    it, by turns: a turn opens when the file is reached and ends when the next
    file's opens. A batch breaks both halves of that. `on_pause` is called before a
    shared window, so the wait for several calls is not billed to whichever file
    happened to be prepared last. `on_resume` is called with a subject's key just
    before ITS OWN send is performed on this thread -- which is every local send in
    the batch -- and without it that send is billed to NOBODY, because the pause
    closed the only open turn. The send this thread performs is the LOCAL one,
    which is the slow call R-175 exists to bound, so a driver that paused and never
    resumed would quietly disable the backstop on exactly the calls it was written
    for. Either may be absent; a caller with no such clock has nothing to say here.
    """
    batch: list[_Slot] = []

    def _cloud_parked() -> bool:
        return any(slot.pending is not None
                   and slot.pending.locality == CLOUD_LOCALITY
                   for slot in batch)

    def _sends() -> int:
        return sum(1 for slot in batch if slot.pending is not None)

    for key, steps in started:
        pending, value = _advance(steps)
        if pending is None:
            batch.append(_Slot(key=key, value=value))
            continue
        if lane.width > 1 and (pending.locality == CLOUD_LOCALITY
                               or _cloud_parked()):
            # A cloud send, or a local one with cloud work already in the air for
            # it to run beside. Either way it waits for the batch.
            #
            # THE BOUND IS OVER EVERY PARKED SEND AND NOT OVER THE CLOUD ONES
            # ALONE. What `width` limits is how much of this run is outstanding at
            # a time -- a parked send is a spent release and a reserved budget slot
            # with no answer against it yet -- and a batch that counted only the
            # cloud half could hold any number of those.
            batch.append(_Slot(key=key, steps=steps, pending=pending))
            if _sends() >= lane.width:
                yield from _settle(batch, lane=lane, on_pause=on_pause,
                                   on_resume=on_resume)
            continue
        # A LOCAL SEND WITH NOTHING TO BE BESIDE, or a lane a person narrowed to
        # one. There is no window to overlap, so holding it back would only mint
        # its release early: it is settled at once, in a batch of one send,
        # performed inline. That is the path this driver has always had, and it is
        # the whole of a run with no cloud target.
        batch.append(_Slot(key=key, steps=steps, pending=pending))
        yield from _settle(batch, lane=lane, on_pause=on_pause,
                           on_resume=on_resume)
    yield from _settle(batch, lane=lane, on_pause=on_pause, on_resume=on_resume)


def _advance(steps):
    """The call up to its socket, or its whole self if it never reaches one."""
    try:
        return steps.send(None), None
    except StopIteration as done:
        return None, done.value


def _finish(steps, sent):
    """The call from its socket onwards, on this thread and in its turn.

    The `while` is for a call that asks for a SECOND round trip. Sites A and C
    declare `split_shards=()`, so `_units` yields one unit and one send per call
    and this loop turns once today. It is written rather than asserted because the
    honest behaviour for a site that one day splits is serial and in turn, not a
    raise; a second general-purpose lane for a case that cannot happen would be a
    scheduler nobody could measure.
    """
    while True:
        try:
            pending = steps.send(sent)
        except StopIteration as done:
            return done.value
        sent = pending.perform()


def _one_send_per_question(parked: "list[_Slot]"):
    """Split this batch's parked sends into the ones that ask and the ones that wait.

    `104` §18.28. Returns `(sends, twins)`: the slots whose sockets are actually
    performed, in walk order, and `(twin, asking)` pairs for the slots that carry
    a question an earlier slot is already asking.

    **THE SAME QUESTION IS THE SAME BYTES TO THE SAME CLIENT, AND NOTHING WIDER.**
    `records.assemble` is the template plus the canonical dossier and includes no
    provenance, so two subjects with equal bytes are the same prompt about the same
    content -- which is what makes handing one the other's answer honest rather
    than a guess. The client is in the key because two clients are two models and
    two answers. Anything this cannot read -- a carrier that offers no bytes, which
    is what the driver's own tests inject -- is never a twin: an unreadable
    question is asked, because the cost of asking twice is a call and the cost of
    pairing two questions that differ is a person's file answered about another
    person's file.

    **THE EARLIER SUBJECT ASKS.** `parked` is in walk order, so which of a pair
    spends the call is decided by the walk and not by which thread got there first,
    and two runs over one corpus buy the same calls.
    """
    sends: list[_Slot] = []
    twins: list[tuple[_Slot, _Slot]] = []
    asking_for: dict[tuple[int, bytes], _Slot] = {}
    for slot in parked:
        question = _question(slot.pending)
        if question is not None and question in asking_for:
            twins.append((slot, asking_for[question]))
            continue
        if question is not None:
            asking_for[question] = slot
        sends.append(slot)
    return sends, twins


def _question(pending) -> "tuple[int, bytes] | None":
    """What this send would ask, as a key, or `None` when it cannot be read.

    The carrier is duck-typed for `transport._PendingSend`'s own reason (the class
    is private and the driver never builds one), so its fields are read the same
    way its `locality` is: by asking, and taking `None` for an answer.
    """
    body = getattr(pending, "model_visible_bytes", None)
    client = getattr(pending, "model_client", None)
    if not isinstance(body, bytes) or client is None:
        return None
    return (id(client), body)


def _settle(batch: "list[_Slot]", *, lane: CallLane, on_pause, on_resume=None):
    """Perform the parked sends, then finish and yield the batch in walk order.

    **THE CLOUD SENDS GO TO A POOL; THE LOCAL ONES RUN HERE, ONE AFTER ANOTHER.**
    That asymmetry is the whole of `104` §18.15's local rule and it needs no
    counter to enforce: this is one thread, so the local sends it performs are
    serial by construction, and a cloud socket waiting beside one costs the Ollama
    server nothing. The local sends are performed INSIDE the pool's window rather
    than before or after it, which is the point -- on a corpus that alternates
    (site A's cloud share was 47%, §18.22) the local call is where the minutes are,
    and the cloud lane should be draining while it runs.
    """
    if not batch:
        return
    parked = [slot for slot in batch if slot.pending is not None]
    # `104` §18.28. ONE SEND PER QUESTION: the later subject of a duplicate pair
    # waits here rather than buying the same answer twice. Walk order decides
    # which one asks, so this is the same spend on every run over one corpus.
    sends, twins = _one_send_per_question(parked)
    away = [slot for slot in sends
            if slot.pending.locality == CLOUD_LOCALITY]
    # BY IDENTITY. `_Slot` is a plain dataclass, so `in` would compare it field by
    # field and two subjects that happened to match would collapse into one.
    gone = {id(slot) for slot in away}
    here = [slot for slot in sends if id(slot) not in gone]
    results: dict[int, object] = {}
    if len(sends) > 1:
        # THE MEASUREMENT IS THE CLOUD WINDOW, because that is what the lane is and
        # what the printed sentence names. The local send beside it is not a second
        # lane; it is this thread.
        lane.at_once = max(lane.at_once, len(away))
        if on_pause is not None:
            on_pause()
        # `max_workers` is the window, never the lane's whole width: a batch of
        # three asks for three threads and not for seven idle ones.
        with ThreadPoolExecutor(max_workers=max(len(away), 1),
                                thread_name_prefix="cloud-call") as pool:
            futures = [pool.submit(slot.pending.perform) for slot in away]
            # THE LOCAL LANE, WHILE THE CLOUD ONES ARE IN THE AIR. In walk order,
            # one at a time, each with `104` R-175's clock reopened for the file
            # that is about to spend the minutes -- and closed again after the last
            # of them, so the wait for the cloud answers is charged to nobody.
            for slot in here:
                if on_resume is not None:
                    on_resume(slot.key)
                results[id(slot)] = slot.pending.perform()
            if here and on_pause is not None:
                on_pause()
            # GATHERED IN WALK ORDER, and `_PendingSend.perform` carries a failure
            # rather than raising it, so one call that does not come back is one
            # `llm_call_failure` row and not the end of the other six.
            for slot, future in zip(away, futures):
                results[id(slot)] = future.result()
    elif sends:
        lane.at_once = max(lane.at_once, 1)
        results[id(sends[0])] = sends[0].pending.perform()

    # THE TWINS, IN WALK ORDER, AFTER THE WINDOW THAT ANSWERED FOR THEM. An answer
    # is copied WITHOUT ITS USAGE: `104` R-14's mailbox reading belongs to the call
    # that was made, and a twin recorded with the asking call's tokens would bill a
    # person twice for one round trip in the very row that exists to say what a
    # call cost. A FAILURE IS NOT COPIED -- a provider that timed out bought no
    # answer, so the twin makes its own send, in its turn on this thread, with
    # R-175's clock reopened for it exactly as a local send has it.
    asked_again = False
    for twin, asking in twins:
        answer = results[id(asking)]
        if getattr(answer, "error", None) is None:
            results[id(twin)] = replace(answer, usage=None)
            lane.reused += 1
            continue
        if on_resume is not None:
            on_resume(twin.key)
        asked_again = True
        results[id(twin)] = twin.pending.perform()
    if asked_again and on_pause is not None:
        # The turn this reopened is closed again, for `here`'s reason: what
        # follows is the batch's own bookkeeping and belongs to no file.
        on_pause()

    # EVERY RESPONSE IS RECORDED BEFORE ANYTHING IS RE-RAISED. A raise out of one
    # subject's post-call work used to end the run with the files behind it not yet
    # walked, which cost nothing; here the files beside it have already spent a
    # release and sent their bytes, and abandoning them would leave answers on the
    # wire with no row naming them. So each is finished, the first raise is kept,
    # and the run then stops the way it stops today.
    # OVER EVERY PARKED SUBJECT AND NOT ONLY THE ONES THAT ASKED: a twin has an
    # answer and the rows that follow it -- the response, the verdict, the fact --
    # are its own, written under its own dossier in its own place in walk order.
    raised: BaseException | None = None
    for slot in parked:
        try:
            slot.value = _finish(slot.steps, results[id(slot)])
        except BaseException as problem:  # noqa: BLE001 -- re-raised below
            if raised is None:
                raised = problem
    if raised is not None:
        batch.clear()
        raise raised
    settled = [(slot.key, slot.value) for slot in batch]
    batch.clear()
    yield from settled
