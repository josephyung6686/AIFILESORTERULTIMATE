# src/grouping/p8_seam.py
"""P9 maps P8's verdict. It does not re-decide it.

P8 owns the only function that speaks to a model and the only validator that says
whether the model's answer held. P9's job here is a mapping: an authoritative
outcome in, a membership and a review obligation out. Every check P8 already ran
-- invented member, citation grounding, contradiction, schema -- is deliberately
absent, and a test reads this package's imports to prove no second validator grew
here.

The rule that costs the most if it is wrong: an `accept_context_supported`
membership and its `pending-review` acceptance row are written in ONE transaction.
A context-supported member is a file the model was not sure about; making it
visible without the obligation that makes it safe is how an uncertain guess
becomes a silent decision.

SR5 is mapped here and nowhere earlier. It means P8 could not explain the group
with valid citations, and only P8's returned reason codes can say that.

P9 runs no reduction ladder. A budget-deferred P8 result becomes
`DossierDeferred`; M9's summarize -> preserve anchors -> split/defer belongs to
`run_call`.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from database_agent.db import transaction
from database_agent.events import append_event
from evidence_shape.location import TextSpan
from llm_harness.fingerprint import prompt_fingerprint
from llm_harness.records import (
    CallFailed,
    DossierRequest,
    EvidenceItem,
    P8Verdict,
    PromptDefinition,
    Refusal,
    ValidationUnavailable,
)
# P8's `Conflict` is `(conflict_id, kind)`; P9's is `(kind, competing_values,
# file_ids)`. Two records, one word, so the import is qualified rather than bare.
from llm_harness.records import Conflict as P8Conflict
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    BUDGET_EXHAUSTED,
    CITATION_NOT_FOUND,
    CITATION_NOT_IN_DOSSIER,
    CITATION_SPAN_MISMATCH,
    COHERENCE_JUDGEMENT,
    REJECT,
    UNCITED_CLAIM,
)
from privacy.items import Excerpt as ReleaseExcerpt
from privacy.release import ModelCallRequest, NeedsConsent, Target

from grouping.acceptance import record_context_review_pending
from grouping.records import (
    CandidateGroupDossier,
    FailurePoint,
    Group,
    Membership,
    StopRuleOutcome,
    Support,
)
from grouping.store import record_failure_point, record_membership
from grouping.vocabulary import (
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    INCLUDED,
    INTERPRETATION,
    LLM,
    NO_GROUP,
    NOT_FLAGGED,
    SHARED_VALIDATED_FACT,
    SR5,
    UNCERTAIN,
    VALIDATION,
    VALIDATOR,
)

#: The P8 reason codes that mean exactly SR5: the model could not explain the
#: group with citations that held. P9 reads the codes and inspects no citation.
_SR5_REASONS: frozenset[str] = frozenset({
    CITATION_NOT_IN_DOSSIER,
    CITATION_NOT_FOUND,
    CITATION_SPAN_MISMATCH,
    UNCITED_CLAIM,
})

#: P8's own stage name for a group call, and the request's `stage`.
GROUP_STAGE: str = "group_interpretation"

#: The one event P1 reserves for this write.
MEMBERSHIP_PROPOSAL_EVENT: str = "group membership proposal"


@dataclass(frozen=True)
class DossierDeferred:
    """P8 could not afford the call. P9 records it and reruns no ladder."""

    group_id: str
    dossier_id: str
    reason: str


@dataclass(frozen=True)
class GroupDecision:
    """What P9 did with one P8 result. Every field is derived, none invented."""

    group_id: str
    dossier_id: str
    group_state: str
    membership_ids: tuple[str, ...]
    stop_rule_outcome: StopRuleOutcome | None
    failure_stage: str | None
    deferred: DossierDeferred | None


def _member_items(dossier: CandidateGroupDossier) -> tuple[EvidenceItem, ...]:
    """Every file in the dossier, as a `kind == "member"` reference.

    Site B rejects a member the dossier did not carry under that kind, so a
    candidate sent as an excerpt reference is a member P8 will call invented.
    """
    return tuple(
        EvidenceItem(
            evidence_ref=item.file_id,
            kind="member",
            location=item.document_type,
            excerpt_span=None,
            reliability_state="direct" if item.basis == DIRECT_ANCHOR else "possible",
            basis=item.basis,
        )
        for item in (*dossier.anchor_files, *dossier.candidate_files)
    )


def _excerpt_items(dossier: CandidateGroupDossier) -> tuple[EvidenceItem, ...]:
    return tuple(
        EvidenceItem(
            evidence_ref=excerpt.observation_key,
            kind="excerpt",
            location=excerpt.location,
            # The observation's own span, straight through. This computed
            # `(0, len(excerpt.text))`, which is a span the observation never
            # claimed whenever it did not start at 0 or the text was truncated.
            excerpt_span=excerpt.text_span,
            reliability_state="direct",
            basis=DIRECT_ANCHOR,
        )
        for excerpt in dossier.excerpts
    )


def prompt_fingerprint_for(prompt: object, *, absent: str) -> str:
    """The fingerprint P7 binds the release to: the PROMPT's, not the dossier's.

    `llm_harness/transport.py:74` recomputes this from the `PromptDefinition` it
    is about to send and refuses the release when the two disagree, so a request
    bound to anything else -- the dossier's own content address, for instance --
    raises `privacy.binding.BindingMismatch` after P7 has already spent the
    release. The pipeline bound it to the dossier address, which is why the first
    real group call could never reach a model.

    `absent` is used only when there is no prompt to fingerprint. That request is
    refused with `ValidationUnavailable(missing=("prompt",))` before any egress
    (`llm_harness/harness.py:144`), so the value never reaches a binding.

    It lives here rather than in `pipeline.py` because
    `test_src_grouping_imports_no_later_part` allows exactly one file under
    `src/grouping/` to import `llm_harness`, and this is that file.
    """
    if isinstance(prompt, PromptDefinition):
        return prompt_fingerprint(prompt)
    return absent


def build_dossier_request(
    dossier: CandidateGroupDossier,
    *,
    model_target,
    prompt_template_id: str,
    prompt_fingerprint: str,
    max_dossier_tokens: int,
) -> DossierRequest:
    """A reference-shape conversion, and nothing else.

    P8 materialises released evidence through P7 and constructs its own `Dossier`.
    Nothing here carries a span of text, a path or an observation body.
    """
    files = tuple(
        item.file_id for item in (*dossier.anchor_files, *dossier.candidate_files)
    )
    return DossierRequest(
        call_site="B_group",
        subject_ref=dossier.group_id,
        eligibility_reason=COHERENCE_JUDGEMENT,
        evidence_items=_member_items(dossier) + _excerpt_items(dossier),
        # The builder's known conflicts, in P8's shape. Hardcoding `()` here made
        # Site B's `target_institution` check (`llm_harness/group_validation.py:113`)
        # unreachable from P9 -- the same defect the frozen contract added this
        # field to fix (`planning/30-p8-p9-connection-contract.md:60-61`), arriving
        # from the other side. The id is stable per (group, kind) so two calls over
        # one group name the same conflict.
        conflicts=tuple(
            P8Conflict(conflict_id=f"{dossier.group_id}:{item.kind}", kind=item.kind)
            for item in dossier.conflicts),
        model_call_request=ModelCallRequest(
            stage=GROUP_STAGE,
            target=Target(file_ids=files, group_id=dossier.group_id),
            model_target=model_target,
            requested_items=tuple(
                ReleaseExcerpt(
                    observation_key=excerpt.observation_key,
                    # `None` means "the whole citation" and is a legal request
                    # (`privacy/items.py:116`). Synthesising `TextSpan(0, len(...))`
                    # for it is what made P7 refuse every unbounded observation
                    # with `UnresolvableSpan`, after the release had been minted.
                    span=(None if excerpt.text_span is None
                          else TextSpan(*excerpt.text_span)),
                    reason="states the group's basis",
                )
                for excerpt in dossier.excerpts
            ),
            prompt_template_id=prompt_template_id,
            prompt_fingerprint=prompt_fingerprint,
            max_dossier_tokens=max_dossier_tokens,
        ),
        plan_version=None,
        evidence_snapshot_id=None,
    )


def _failure(conn, group_id: str, dossier_id: str, *, stage: str, cause: str,
             created_at: str) -> None:
    record_failure_point(conn, FailurePoint(
        group_id=group_id, dossier_id=dossier_id, membership_id=None,
        stage=stage, cause_code=cause, evidence_ref=None,
        detected_by=VALIDATOR,
    ), created_at=created_at)


def _decision(group: Group, dossier: CandidateGroupDossier, **overrides
              ) -> GroupDecision:
    values = dict(
        group_id=group.group_id, dossier_id=dossier.dossier_id,
        group_state=group.state, membership_ids=(), stop_rule_outcome=None,
        failure_stage=None, deferred=None,
    )
    values.update(overrides)
    return GroupDecision(**values)


def _support_for(item) -> tuple[Support, ...]:
    if item.excerpts:
        return tuple(
            Support(
                support_kind=SHARED_VALIDATED_FACT,
                observation_key=excerpt.observation_key,
                quote_or_field=excerpt.text,
                location=excerpt.location,
                edge_ref=None,
            )
            for excerpt in item.excerpts
        )
    return ()


def _edge_support(dossier: CandidateGroupDossier, file_id: str) -> tuple[Support, ...]:
    """Every unsuppressed edge touching this file, in either direction.

    An edge relates two file versions; which end it was drawn from is a fact about
    the seed, not about which file the edge supports. Matching one direction only
    would leave a candidate the graph reached with no support to name.
    """
    return tuple(
        Support(
            support_kind=edge.edge_type,
            observation_key=None,
            quote_or_field=edge.bridge_entity_ref,
            location=None,
            edge_ref=edge.edge_id,
        )
        for edge in dossier.typed_edges
        if file_id in (edge.from_file_id, edge.to_file_id)
        and not edge.hub_suppressed
    )


def apply_p8_verdict(
    conn: sqlite3.Connection,
    *,
    group: Group,
    dossier: CandidateGroupDossier,
    result,
    plan_version_id: str | None,
    created_at: str,
):
    """Map one authoritative P8 result onto P9's records.

    `NeedsConsent` is returned unchanged and writes nothing: it is a question for
    the user, not an outcome, and a P9 row about it would be P9 answering it.
    """
    if isinstance(result, NeedsConsent):
        return result

    if isinstance(result, CallFailed):
        _failure(conn, group.group_id, dossier.dossier_id,
                 stage=INTERPRETATION, cause="call_failed", created_at=created_at)
        return _decision(group, dossier, failure_stage=INTERPRETATION)

    if isinstance(result, (Refusal, ValidationUnavailable)):
        cause = ("privacy_gate_refused" if isinstance(result, Refusal)
                 else "validation_unavailable")
        _failure(conn, group.group_id, dossier.dossier_id,
                 stage=VALIDATION, cause=cause, created_at=created_at)
        return _decision(group, dossier, failure_stage=VALIDATION)

    if not isinstance(result, P8Verdict):
        raise TypeError(
            "apply_p8_verdict takes one of P8's frozen result types; a mapping "
            "that looks like a verdict has not been through P8's validator"
        )

    accepting = result.outcome in (ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED)
    if accepting and not result.may_propose:
        raise ValueError(
            f"P8 returned {result.outcome!r} with may_propose=False. That is P8's "
            "own answer to whether this may become a proposal, and P9 does not "
            "resolve the disagreement in the model's favour."
        )

    if result.outcome == ABSTAIN and BUDGET_EXHAUSTED in result.reasons:
        return _decision(group, dossier, deferred=DossierDeferred(
            group_id=group.group_id, dossier_id=dossier.dossier_id,
            reason=BUDGET_EXHAUSTED))

    if not accepting:
        outcome = None
        if set(result.reasons) & _SR5_REASONS:
            outcome = StopRuleOutcome(
                group_id=group.group_id, rules_fired=(SR5,),
                evidence_refs=tuple(result.reasons), outcome=NO_GROUP)
        return _decision(group, dossier, stop_rule_outcome=outcome)

    context = result.outcome == ACCEPT_CONTEXT_SUPPORTED
    if context and not plan_version_id:
        raise ValueError(
            "a context-supported membership carries a review obligation, and the "
            "obligation is per plan version. Without one there is nowhere to "
            "record the review, and a membership visible without its review is "
            "the failure this rule exists to prevent."
        )

    written: list[str] = []
    # One transaction. A membership that became visible while its review
    # obligation failed to record is an uncertain guess wearing a decision.
    with transaction(conn):
        for item in (dossier.candidate_files if context else dossier.anchor_files):
            membership_id = f"{group.group_id}:{item.file_id}:{result.verdict_id}"
            support = (
                _edge_support(dossier, item.file_id) if context
                else _support_for(item)
            )
            record_membership(conn, Membership(
                membership_id=membership_id,
                group_id=group.group_id,
                file_id=item.file_id,
                content_hash=item.content_hash,
                basis=CONTEXT_SUPPORTED if context else DIRECT_ANCHOR,
                decision=UNCERTAIN if context else INCLUDED,
                decision_source=LLM,
                support=support,
                insufficient_evidence=False,
                insufficiency_statement=None,
                # The conflicts that name THIS file, not the group's whole set: a
                # membership claiming a conflict it is not part of is as wrong as
                # the hardcoded `()` that claimed none at all.
                conflicts=tuple(
                    conflict for conflict in dossier.conflicts
                    if item.file_id in conflict.file_ids),
                outlier_flag=NOT_FLAGGED,
                validation_verdict_ref=result.verdict_id,
                created_at=created_at,
            ))
            if context:
                record_context_review_pending(
                    conn, plan_version_id=plan_version_id,
                    group_id=group.group_id, membership_id=membership_id,
                    created_at=created_at)
            append_event(
                conn,
                event_type=MEMBERSHIP_PROPOSAL_EVENT,
                file_id=item.file_id,
                content_hash=item.content_hash,
                subsystem="P9",
                component_version="p9",
                observed_at=created_at,
                explanation=(
                    f"P8 verdict {result.verdict_id} ({result.outcome}) proposed "
                    f"this membership"
                ),
            )
            written.append(membership_id)
    return _decision(group, dossier, membership_ids=tuple(written))
