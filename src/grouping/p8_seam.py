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

import dataclasses
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
from grouping.store import (
    record_failure_point, record_group, record_membership, standing_group,
)
from grouping.vocabulary import (
    COHERENT,
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    INCLUDED,
    INTERPRETATION,
    LLM,
    LLM_PROPOSED,
    MEMBERSHIP_DECISIONS,
    NO_GROUP,
    NOT_FLAGGED,
    SHARED_VALIDATED_FACT,
    SR5,
    UNCERTAIN,
    VALIDATION,
    VALIDATOR,
)
from facts.domains import SCHEMA_IDS

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


@dataclass(frozen=True)
class MemberDecision:
    """One file, and what the model said about it. `00` §4.5 task 2.

    `decision` is one of P9's OWN three (`MEMBERSHIP_DECISIONS`), already
    translated from the response schema's `include` / `exclude` / `uncertain` by
    whoever read the response. P9 does not know the model's vocabulary and does not
    learn it here: `test_only_the_vocabulary_module_spells_a_closed_p9_value`
    refuses a literal, and a translation table living in this package would be P9
    holding a second copy of a contract the prompt owns.

    `why` is the model's sentence about this file and is kept so a person reading
    the group sees the reason rather than the decision alone.
    """

    file_id: str
    decision: str
    why: str


@dataclass(frozen=True)
class ModelAnswer:
    """§4.5's four tasks, as the site that supplied the prompt read them back.

    **P9 parses nothing.** `P8Verdict` names a `claim_ref` and carries no payload,
    so the model's own four answers can only be read by whoever knows the response
    shape -- which is whoever supplied the prompt, exactly as `model_placement`
    argues for `chosen_node_of` at site C. The composition root reads them and
    hands over this record; this package never touches a response body.

    `label` and `category` are `None` on any answer that is not coherent, because
    the response schema forbids them there and `groups`' own CHECK constraint
    refuses the row.

    `coherent` is a `COHERENCE_VERDICTS` word, translated by the same reader for
    the same reason as `MemberDecision.decision`. `citations` are the references
    the model cited for the coherence it claimed, already checked by P8: this
    package reads no citation and runs no second validator, and a test over its own
    source text holds it to that.
    """

    coherent: str | None
    category: str | None
    label: str | None
    members: tuple[MemberDecision, ...]
    citations: tuple[str, ...] = ()


@dataclass(frozen=True)
class Answered:
    """A P8 result together with the model's own four answers. `104` R-16.

    The twin of `ObservedOnly`, and a wrapper for the same reason: the two things
    that must not drift are "the call happened" and "what the model actually said",
    and a payload travelling beside the result can be read by one branch and missed
    by another. A caller that forgets to unwrap gets an object `apply_p8_verdict`
    refuses to treat as a verdict.

    `result` is whatever `run_call` returned; a refusal or a failure arrives here
    too, and `apply_p8_verdict` handles it exactly as it does unwrapped.
    """

    result: object
    answer: ModelAnswer


@dataclass(frozen=True)
class ObservedOnly:
    """A real P8 outcome that this run recorded and will not act on.

    **`104` §7 Phase 1 step 6: "record dossiers, responses and verdicts; apply
    nothing until Phase 3 fixes R-15 and R-16."** The recording is P8's and has
    already happened by the time this exists: `run_call` wrote the dossier, the
    response and the verdict before returning the value wrapped here. What is
    withheld is the APPLICATION -- the memberships and the acceptance row that
    would turn a model's answer into a group the person sees.

    A WRAPPER RATHER THAN A FLAG ON THE CALL, because the two things that must not
    drift are "the call happened" and "nothing was applied", and a boolean travelling
    beside the result can be read by one branch and missed by another. `result` is
    kept and not discarded: the outcome is still attributable, and a reader of this
    object can see exactly what would have been applied.

    R-15 IS THE REASON THIS IS NOT A PHASE-3 PROBLEM YET. `_invented_dimension`
    checks date, institution and project VALUES against the node-id vocabulary, so
    any real value reads as invented the moment C answers. Applying a verdict under
    a validator known to be wrong would write the wrong thing confidently, which is
    the failure this product exists not to have.
    """

    result: object


def _record_group_once(conn: sqlite3.Connection, group: Group) -> None:
    """Insert the group if it is not on disk yet, and never touch it if it is.

    `104` R-16 moved the insert to the moment the AUTHOR is known, so this is the
    one write for the row. It is a `SELECT` and not a flag on purpose: a boolean
    threaded through the caller would have to be right on every path out, and this
    asks the database the question it is the authority for.

    **A group already recorded is left exactly as it stands, and that is the
    conservative half.** A second model answer about a group whose row already
    carries a proposal is a real supersession question -- a superseding row needs a
    new `group_id`, which every membership and `group_acceptance` row would then
    not name -- and it is refused here rather than answered quietly, which is the
    same position `record_group`'s own docstring takes for a widened anchor set.
    """
    if standing_group(conn, group.group_id) is None:
        record_group(conn, group)


def _named_by_the_model(group: Group, answer, result, dossier) -> Group:
    """§4.5 task 4, on the row, with the author named. `104` R-16 and R-28.

    Returns the group UNCHANGED whenever the model proposed nothing -- no answer at
    all, a coherence that is not `yes`, or no label -- so `naming.engine_proposal`'s
    own conclusion stands and a deployment without a model is untouched.

    **The category is written only when the library recognises it.** `00`'s Q-C
    ruling (§13.7) is "model names, user confirms": a value the library has not seen
    is PROPOSED once and joins the vocabulary when the person confirms it. P10
    selects an applicability row BY `group_category`, so writing an unrecognised one
    would file the material under a schema that speaks for somebody else's life --
    `Group.__post_init__` refuses it for that reason. The label is kept either way,
    because a label is words and a category is a routing decision.
    """
    if answer is None or answer.coherent != COHERENT or not answer.label:
        return group
    return dataclasses.replace(
        group,
        coherence_verdict=COHERENT,
        # What the model pointed at for the coherence it is claiming, handed over
        # already checked. The engine's are its anchor facts' observation keys.
        coherence_citations=(tuple(dict.fromkeys(answer.citations))
                             or group.coherence_citations),
        group_category=(answer.category if answer.category in SCHEMA_IDS
                        else None),
        display_label=answer.label,
        label_source=LLM_PROPOSED,
        dossier_id=dossier.dossier_id,
        validation_verdict_ref=result.verdict_id,
    )


def _members_of(dossier, answer, *, context: bool):
    """`(dossier file, P9 decision)` for every member this write covers.

    **With an answer, the model's own per-member decisions**, which is R-16's other
    half: `include`, `exclude` and `uncertain` were collapsed into one blanket
    decision per branch, so a file the model excluded became a member and a file it
    was unsure about became a certainty. A member the model did not mention gets no
    row at all -- writing one would be P9 authoring a decision on the model's
    behalf, which is what the blanket write was.

    **Without one, the pre-R-16 reading**, and it is not a fallback for the live
    site: `cli.observed_run_call` always wraps, so B's answers always arrive. This
    is what a caller that holds a verdict and no response body has -- P8 accepted
    the group's coherence and said nothing per file, so P9 reads the dossier's own
    sides, which is exactly as coarse as that caller's evidence.
    """
    if answer is None:
        return tuple(
            (item, UNCERTAIN if context else INCLUDED)
            for item in (dossier.candidate_files if context
                         else dossier.anchor_files)
        )
    by_id = {item.file_id: item
             for item in dossier.anchor_files + dossier.candidate_files}
    found = []
    for member in answer.members:
        item = by_id.get(member.file_id)
        # A file id the dossier does not carry is `INVENTED_MEMBERSHIP` and P8 has
        # already rejected the whole claim, so this is unreachable through the live
        # seam; a decision outside P9's own three is the same shape of answer.
        # Neither is repaired here.
        if item is not None and member.decision in MEMBERSHIP_DECISIONS:
            found.append((item, member.decision))
    return tuple(found)


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

    `NeedsConsent` is returned unchanged and writes nothing about the answer: it is
    a question for the user, not an outcome, and a P9 row about it would be P9
    answering it. The GROUP is still recorded, because recording that a group was
    proposed is not answering the question.

    **`104` R-16: §4.5's task 4 now reaches the record.** This wrote no
    `display_label`, no `group_category` and no `coherence_verdict`, and collapsed
    per-member include/exclude/uncertain into blanket memberships -- "the model's
    four answers are validated and then three of them are dropped" (packet §7 G11).
    `P8Verdict` still carries no payload and P9 still parses none: the composition
    root that supplied the prompt reads the model's own answers and hands them over
    as `Answered`, which is the same argument `model_placement` makes for
    `chosen_node_of` at site C.

    **THE GROUP ROW IS INSERTED HERE WHEN ITS AUTHOR IS THE MODEL, and that is what
    made the three fields writable at all.** `groups` is append-only in the strong
    sense: `groups_never_overwritten` refuses an UPDATE of any of these columns, and
    a superseding row needs a new `group_id` that every membership, every
    `group_acceptance` row and `GroupingResult.group` would then not name. So the
    fix is not a later write -- it is writing the row ONCE, after the author is
    known. `grouping.pipeline` withholds the insert exactly when a ratified model is
    going to decide, and every path out of here records the group before it returns.
    §4.1 is untouched: the engine's REASON -- `proposed_basis`, `pre_model_signals`,
    `anchor_facts`, the stop rules -- is computed before the model sees anything and
    is carried on the row this writes.

    **The engine keeps its role, which is the fallback.** `naming.engine_proposal`
    has already filled the three on the group handed in; when the model does not
    accept, or accepts without a label, that is what lands, and a deterministic
    deployment is unchanged in every respect. When the model does answer, its
    proposal is what the row carries and `label_source` says so -- R-28's actor
    rule: never say the person, and never say the engine, when the model decided.
    """
    if isinstance(result, ObservedOnly):
        # RECORDED AND NOT ACTED ON. `_decision`'s defaults are `membership_ids=()`
        # and no acceptance row, which is exactly "no accepted state written by B":
        # the group keeps the state P9's own engine gave it, and what the model
        # said is on disk in `llm_dossier`, `llm_response` and `llm_verdict` under
        # a template id carrying the word `unratified`.
        _record_group_once(conn, group)
        return _decision(group, dossier)

    answer: ModelAnswer | None = None
    if isinstance(result, Answered):
        answer, result = result.answer, result.result

    if isinstance(result, NeedsConsent):
        _record_group_once(conn, group)
        return result

    if isinstance(result, CallFailed):
        _record_group_once(conn, group)
        _failure(conn, group.group_id, dossier.dossier_id,
                 stage=INTERPRETATION, cause="call_failed", created_at=created_at)
        return _decision(group, dossier, failure_stage=INTERPRETATION)

    if isinstance(result, (Refusal, ValidationUnavailable)):
        _record_group_once(conn, group)
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
        _record_group_once(conn, group)
        return _decision(group, dossier, deferred=DossierDeferred(
            group_id=group.group_id, dossier_id=dossier.dossier_id,
            reason=BUDGET_EXHAUSTED))

    if not accepting:
        # NOT the model's label, and the schema agrees: `groups`' CHECK allows a
        # label and a category only beside `coherent`, which is §4.5's own "only if
        # coherence is supported" in SQL. So the row carries what the engine
        # concluded and nothing the model proposed.
        _record_group_once(conn, group)
        outcome = None
        if set(result.reasons) & _SR5_REASONS:
            outcome = StopRuleOutcome(
                group_id=group.group_id, rules_fired=(SR5,),
                evidence_refs=tuple(result.reasons), outcome=NO_GROUP)
        return _decision(group, dossier, stop_rule_outcome=outcome)

    context = result.outcome == ACCEPT_CONTEXT_SUPPORTED
    members = _members_of(dossier, answer, context=context)
    # THE OBLIGATION IS PER UNCERTAIN MEMBER, so the refusal is too. It read
    # `context and not plan_version_id`, which was right while the whole branch was
    # uncertain; a model may now call one member uncertain inside a group it
    # otherwise accepted directly, and that member needs the same review.
    if any(decision == UNCERTAIN for _item, decision in members) and (
            not plan_version_id):
        raise ValueError(
            "an uncertain membership carries a review obligation, and the "
            "obligation is per plan version. Without one there is nowhere to "
            "record the review, and a membership visible without its review is "
            "the failure this rule exists to prevent."
        )

    _record_group_once(conn, _named_by_the_model(group, answer, result, dossier))

    written: list[str] = []
    # One transaction. A membership that became visible while its review
    # obligation failed to record is an uncertain guess wearing a decision.
    with transaction(conn):
        for item, decision in members:
            membership_id = f"{group.group_id}:{item.file_id}:{result.verdict_id}"
            # THE FILE'S OWN BASIS, from the dossier that described it. This read
            # `CONTEXT_SUPPORTED if context else DIRECT_ANCHOR`, so the basis was
            # decided by which branch ran rather than by what the builder concluded
            # about the file -- and `DossierFile.basis` is already one of
            # `MEMBERSHIP_BASES` and is that conclusion.
            direct = item.basis == DIRECT_ANCHOR
            support = _support_for(item) or _edge_support(dossier, item.file_id)
            if not support:
                # `records.py`: "a membership with no support cannot say why the
                # file belongs". P9 authors none, so a member whose evidence the
                # dossier does not carry gets no row -- and the model's decision
                # about it is still on disk in `llm_response` under this verdict.
                continue
            record_membership(conn, Membership(
                membership_id=membership_id,
                group_id=group.group_id,
                file_id=item.file_id,
                content_hash=item.content_hash,
                basis=DIRECT_ANCHOR if direct else CONTEXT_SUPPORTED,
                decision=decision,
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
            if decision == UNCERTAIN:
                # THE OBLIGATION FOLLOWS THE DECISION, not the verdict's outcome.
                # An uncertain member is one the model was not sure about, and it
                # is safe to show only because a review is pending on it -- which
                # is now true of a member the model called uncertain inside an
                # `accept_direct` group as well.
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
                    f"this membership as {decision}"
                ),
            )
            written.append(membership_id)
    return _decision(group, dossier, membership_ids=tuple(written))
