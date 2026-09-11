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
    REFUSAL_EXCEPTIONS,
    CallFailed,
    CallRefused,
    DossierRequest,
    EvidenceItem,
    P8Verdict,
    PromptDefinition,
    Refusal,
    ValidationUnavailable,
)
from llm_harness.store import refusal_outcome
# P8's `Conflict` is `(conflict_id, kind)`; P9's is `(kind, competing_values,
# file_ids)`. Two records, one word, so the import is qualified rather than bare.
from llm_harness.records import Conflict as P8Conflict
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    B_GROUP,
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

from grouping.acceptance import record_acceptance, record_context_review_pending
from grouping.records import (
    CandidateGroupDossier,
    FailurePoint,
    Group,
    GroupAcceptance,
    Membership,
    StopRuleOutcome,
    Support,
)
from grouping.store import (
    carry_memberships, memberships_for_group, propose_group_category,
    record_failure_point, record_group, record_membership, standing_group,
)
from grouping.vocabulary import (
    ACCEPTED,
    COHERENT,
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    INTERPRETATION,
    LLM,
    LLM_PROPOSED,
    MEMBERSHIP_DECISIONS,
    NO_GROUP,
    NOT_FLAGGED,
    PENDING_REVIEW,
    SHARED_VALIDATED_FACT,
    SR5,
    UNCERTAIN,
    USER,
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

    **Every path but one comes through here, and none of them is an answer.** A
    refusal, a failure, a budget deferral, a rejection and an observe-only call
    all carry the ENGINE's group -- `naming.engine_proposal`'s conclusion, which
    the model has not touched -- so a recorded row differing from it is not a
    second opinion about anything and is left exactly as it stands. `104` R-80 is
    about the one path that IS an answer, and that path is `_the_answers_row`.
    """
    if standing_group(conn, group.group_id) is None:
        record_group(conn, group)


#: `104` R-80, the words on the superseded row. A later reader gets the account
#: §8.2 keeps history for: not "P9 changed its mind" and not "the person renamed
#: it", but the one thing that happened.
SECOND_ANSWER_DIFFERED: str = "the model answered differently"

#: WHAT A MODEL ANSWERS ABOUT A GROUP, and nothing about the call that carried it.
#: `dossier_id` and `validation_verdict_ref` are new on every call by
#: construction, so comparing whole rows would call every second answer a
#: different one and mint a superseding group for a model that said exactly what
#: it said the first time. These five are §4.5's task 4 as it reaches the record.
_THE_ANSWER: tuple[str, ...] = (
    "coherence_verdict", "coherence_citations", "group_category",
    "display_label", "label_source",
)


def _answer_on(group: Group) -> tuple:
    return tuple(getattr(group, name) for name in _THE_ANSWER)


def _head_of(conn: sqlite3.Connection, group_id: str) -> Group | None:
    """The row at the end of this group's supersession chain, or `None`.

    THE CHAIN IS ALREADY LONGER THAN ONE IN THE SHIPPED FLOW, which is why this
    walks rather than reading the address it was handed. `cli.review_and_accept`
    runs on every run of the command -- `--label` and `--situation` are required
    flags -- and it mints a MERGED group carrying `supersedes=<P9's group>` and
    writes the person's acceptance on the merged row. So by the second run the
    address P9 re-derives names a row that was superseded on the first, and a
    supersession minted against it would fork the chain: `_link` would move
    `superseded_by` off the merged row and onto the new one, and the person's
    accepted group would be reachable from nothing.

    A cycle cannot be written through `record_group` (a predecessor must already
    exist), but it is read here rather than trusted: a walk that cannot terminate
    is worse than a walk that stops and says the row it stopped on.
    """
    standing = standing_group(conn, group_id)
    seen: set[str] = set()
    while standing is not None and standing.superseded_by:
        if standing.superseded_by in seen:
            return standing
        seen.add(standing.superseded_by)
        successor = standing_group(conn, standing.superseded_by)
        if successor is None:
            return standing
        standing = successor
    return standing


def _a_person_accepted(conn: sqlite3.Connection, group_id: str) -> bool:
    """Is there a standing acceptance of this group as a whole?

    `104` R-80: a person's acceptance outranks both model answers.

    **`decided_by` IS NOW READ, AND `104` SF-3 IS WHY IT CAN BE.** This clause
    used to take ANY standing `accepted` row as the person's word, and it said so:
    *"the row is the person's word however the command carried it --
    `review_and_accept` records `decided_by=RULES` because the FILE SET was nobody's
    judgement, while the label and the situation on it are what the person typed"*.
    That reading was only available while the rules wrote an acceptance nobody had
    made. They no longer do: a merged draft is `pending-review` until a person's
    gesture or a ratified B verdict decides it, so the only thing an `accepted` row
    with `decided_by=USER` can be is a decision somebody made.

    Reading the column is now what keeps the sentence true in the other direction
    as well. `_record_the_models_acceptance` below writes an `accepted` row with
    `decided_by=VALIDATOR` when B is ratified, and a clause that counted every
    `accepted` row would let B's own answer from the last run stand as "a person
    accepted it" and silence B's next one -- the model overruling itself through a
    door built for the person.

    Group-level only. A `membership_id` row is one file's review obligation, which
    `record_context_review_pending` writes below and which says nothing about
    whether the group stands.
    """
    return conn.execute(
        "SELECT acceptance_id FROM group_acceptance WHERE group_id = ? "
        "AND membership_id IS NULL AND acceptance = ? AND decided_by = ? "
        "AND superseded_by IS NULL",
        (group_id, ACCEPTED, USER),
    ).fetchone() is not None


def _support_of(dossier: CandidateGroupDossier, item) -> tuple[Support, ...]:
    """The support a membership for this file would carry, or none at all.

    Asked twice -- by the loop that writes the row, and by the carry that has to
    know which files that loop will leave to it -- so it is ONE expression rather
    than two that have to agree. A file the model decided and the dossier supports
    with nothing gets no row (`records.py`: "a membership with no support cannot
    say why the file belongs"), which makes it a file the carry still owes.
    """
    return _support_for(item) or _edge_support(dossier, item.file_id)


def _would_be_carried(conn: sqlite3.Connection, carried_from: str | None,
                      members, dossier: CandidateGroupDossier) -> tuple:
    """The memberships a supersession would carry, asked before anything is written.

    Asked of the same rows `carry_memberships` will read and under the same
    exclusion, so the refusal beside this can be raised BEFORE the group is
    recorded rather than after: a group recorded beside a raise is a group whose
    author this run cannot name, and `groups` cannot correct one.

    The exclusion is the files that will END WITH A ROW, not the files this answer
    mentioned. A file the model decided and the dossier supports with nothing gets
    no row from the loop, so its earlier membership is carried -- and if that
    membership was uncertain it needs a review obligation in this plan version
    exactly as any other carried one does.
    """
    if carried_from is None:
        return ()
    written = {item.file_id for item, _decision in members
               if _support_of(dossier, item)}
    return tuple(
        membership for membership in memberships_for_group(conn, carried_from)
        if membership.file_id not in written)


def _the_answers_row(conn: sqlite3.Connection, *, group: Group, named: Group,
                     verdict_id: str, created_at: str
                     ) -> tuple[Group | None, str | None]:
    """Which `groups` row this answer writes, and whose memberships travel to it.

    `104` R-80. `groups` is append-only in the strong sense -- a row is superseded,
    never overwritten -- so a second, differing answer about a group used to leave
    the first one standing and go unrecorded except in the harness tables. It is
    now what the person's own review does with the same constraint: a NEW row,
    naming its predecessor and saying why, and the memberships carried onto it.

    Five answers, in the order they are asked:

    **Nothing recorded** -- R-16's normal case for a deployment whose model
    decides. The row is the model's proposal and this is its first write.

    **The same answer twice** -- the head as it stands, and nothing is superseded.
    A rerun over unchanged evidence re-derives the same group and asks the same
    question of the same model; a supersession there would be a new row per run
    saying what the last one said, which is history nobody can read.

    **A person accepted it** -- `None`, and the caller applies nothing. This is
    the clause that makes the record readable at all: two model answers and a
    person's decision, and the person's is the one the product acts on. The answer
    is not lost, it is in `llm_response` and `llm_verdict` under its own verdict
    id, which is exactly what an unratified site does with every answer it gets.

    **A SECOND answer, differing** -- a superseding row. Its id is the address, the
    word `superseded-by` and the verdict that produced it, so it is DERIVED rather
    than minted: the same answer arriving twice is the same id and `record_group`
    returns the row it already holds, while two different answers can never
    collide. A reader who has only the id can still say what happened to it.

    **A first answer over a row no model wrote** -- the head as it stands, exactly
    as before this change. R-80's row is about a SECOND model answer, and
    `label_source` is the record's own answer to whether there was a first one: a
    row already on disk when a model is about to decide is a row R-16 did not
    withhold, which is a deployment saying the engine is the author here. What that
    costs is unchanged and is not R-80's to widen -- the label is dropped and the
    memberships land on the standing row -- and the seven tests that pre-record the
    engine's row hold exactly that.
    """
    head = _head_of(conn, group.group_id)
    if head is None:
        return named, None
    if _answer_on(head) == _answer_on(named):
        return head, None
    if _a_person_accepted(conn, head.group_id):
        return None, None
    if head.label_source != LLM_PROPOSED:
        return head, None
    return dataclasses.replace(
        named,
        group_id=f"{group.group_id}:superseded-by:{verdict_id}",
        supersedes=head.group_id,
        # THE HISTORY IS NOT INHERITED. `named` is a `replace` of the group handed
        # in, and on the second run that group is the row read back off the disk --
        # which by then carries the `superseded_by` this same branch stamped on it
        # last time. Carried through, a THIRD differing answer would insert a row
        # already pointing at its own predecessor while `_link` pointed that
        # predecessor at it: a two-node cycle in a chain `_head_of` has to walk.
        # `superseded_by` is stamped on a row by whatever superseded it, later, and
        # a row being written has nothing to say about it.
        superseded_by=None,
        supersede_reason=SECOND_ANSWER_DIFFERED,
        created_at=created_at,
    ), head.group_id


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

    **And the unrecognised value is now PROPOSED rather than only dropped**, which
    is the other half of the same ruling and was missing. `None` here is still what
    the row carries -- nothing is filed under a category nobody confirmed -- but
    `_propose_group_category` beside this writes the question down, so the person
    has something to confirm and the model's answer leaves a trace. Dropping it
    silently satisfied the first clause of §13.7 and none of the second.
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


def _propose_group_category(conn: sqlite3.Connection, *, group: Group, answer,
                            result, dossier, created_at: str) -> None:
    """`00`'s Q-C, second clause: the value the library has not seen, written down.

    Only for a value the model actually named and the library does not recognise.
    A recognised one is filed on the row above and is nobody's question; no value
    at all is the model declining, and a question about nothing is not one.

    Guarded by the same conditions as the naming itself, because a category is
    task 4 of §4.5 and task 4 runs "only if coherence is supported": a category
    proposed inside a group the model did not call coherent would be asking the
    person to confirm a word about material the model said was not one thing.
    """
    if answer is None or answer.coherent != COHERENT or not answer.label:
        return
    if not answer.category or answer.category in SCHEMA_IDS:
        return
    propose_group_category(
        conn,
        proposed_value=answer.category,
        group_id=group.group_id,
        # The model's own display label, so the question a person is shown reads
        # "this group, which the model called X, is a kind of material it calls Y"
        # rather than naming an opaque id.
        display_label=answer.label,
        # §4.5's three-author field, at its middle rung. `104` R-28: a record says
        # who decided, and nobody has confirmed this yet.
        proposed_by=LLM_PROPOSED,
        verdict_ref=result.verdict_id,
        dossier_id=dossier.dossier_id,
        created_at=created_at)


def _members_of(dossier, answer: ModelAnswer):
    """`(dossier file, P9 decision)` for every member this write covers.

    **The model's own per-member decisions**, which is R-16's other half:
    `include`, `exclude` and `uncertain` were collapsed into one blanket decision
    per branch, so a file the model excluded became a member and a file it was
    unsure about became a certainty. A member the model did not mention gets no row
    at all -- writing one would be P9 authoring a decision on the model's behalf,
    which is what the blanket write was.

    **`104` R-83: THERE IS NO READING HERE FOR A CALLER WITH NO ANSWER.** A second
    branch took the dossier's own sides -- every anchor included, or every
    candidate uncertain -- whenever `answer` was `None`, which is R-16's blanket
    write still standing for "a caller holding a verdict and no response body".
    That caller does not exist: `cli.observed_run_call` is the only route into this
    function and it always wraps, and `apply_p8_verdict` now turns one away before
    reaching here. The `context` flag went with the branch, because its only job
    was to say which side to blanket.
    """
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

    **`104` R-83: AND THE WRAPPER IS NOW THE ONLY WAY IN.** R-16 left the blanket
    write standing one branch further down, for a caller that had the verdict and
    no response body: `_members_of` read the dossier's own sides and P9 wrote
    memberships nobody had decided. It was never reachable from the live root, but
    "not reachable today" is how a coarse path survives a refactor. An accepting
    verdict arriving bare is a caller bug, so it is raised on exactly as a
    non-verdict is -- before the group row is written, because a group recorded
    beside a raise is a group whose author this run cannot name.

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

    if answer is None:
        # `104` R-83, and the twin of the `not isinstance(result, P8Verdict)` raise
        # above: RAISED WITH THE GROUP ROW UNWRITTEN, because nothing here can be
        # written correctly. The four answers live in the response body, and only
        # the root that supplied the prompt can read one, so a caller holding the
        # verdict alone knows no member decision, no label and no category.
        raise TypeError(
            "apply_p8_verdict was handed a bare P8Verdict for an accepting "
            "outcome. Pass `Answered(result=..., answer=...)` carrying the four "
            "answers the composition root read back, or `ObservedOnly(result=...)` "
            "when it could read none. The group row is withheld rather than "
            "written with the blanket memberships `104` R-16 took out."
        )
    members = _members_of(dossier, answer)
    # `104` R-80: WHICH ROW THIS ANSWER WRITES, decided before anything is written
    # and never by overwriting. A second, differing answer about a group whose row
    # already carries a proposal mints a superseding one and the memberships travel
    # to it; the same answer twice writes nothing new; and a group the person has
    # accepted is not superseded by either answer. Every branch of it is a READ, so
    # it is asked here -- above the refusal below, which has to know what will be
    # carried before it can say whether this run can carry it.
    row, carried_from = _the_answers_row(
        conn, group=group, named=_named_by_the_model(group, answer, result, dossier),
        verdict_id=result.verdict_id, created_at=created_at)
    if row is None:
        # THE PERSON'S ANSWER OUTRANKS BOTH OF THE MODEL'S, and this is the observe
        # style: the call happened, it is on disk in `llm_dossier`, `llm_response`
        # and `llm_verdict` under its own verdict id, and nothing here is applied.
        # No membership, no category proposal, no supersession -- a proposal about a
        # group the person has already accepted is a question nobody asked, and a
        # membership under a second author is the group changing under the decision
        # that accepted it.
        return _decision(group, dossier)

    # THE OBLIGATION IS PER UNCERTAIN MEMBER, so the refusal is too. It read
    # `context and not plan_version_id`, which was right while the whole branch was
    # uncertain; a model may now call one member uncertain inside a group it
    # otherwise accepted directly, and that member needs the same review.
    #
    # AND IT COVERS THE CARRIED ONES (`104` R-80). A membership travelling to a
    # superseding group keeps the decision it was written with, so an uncertain one
    # arrives on a row whose plan version has recorded no review for it -- a
    # membership visible without its review, arriving through the back door this
    # rule was written to bar the front of.
    uncertain = any(decision == UNCERTAIN for _item, decision in members) or any(
        membership.decision == UNCERTAIN
        for membership in _would_be_carried(conn, carried_from, members, dossier))
    if uncertain and not plan_version_id:
        raise ValueError(
            "an uncertain membership carries a review obligation, and the "
            "obligation is per plan version. Without one there is nowhere to "
            "record the review, and a membership visible without its review is "
            "the failure this rule exists to prevent."
        )

    # BEFORE the group is recorded, and in its own transaction: the question and
    # the row are two records about two different things, and a proposal that
    # failed to write while the group succeeded would leave a category the model
    # named with nothing anywhere saying it had.
    _propose_group_category(conn, group=row, answer=answer, result=result,
                            dossier=dossier, created_at=created_at)
    # `record_group` rather than `_record_group_once`: the id is either absent, or
    # the head exactly as it stands, or new. There is nothing here to overwrite.
    record_group(conn, row)

    written: list[str] = []
    written_files: set[str] = set()
    # One transaction. A membership that became visible while its review
    # obligation failed to record is an uncertain guess wearing a decision.
    with transaction(conn):
        for item, decision in members:
            membership_id = f"{row.group_id}:{item.file_id}:{result.verdict_id}"
            # THE FILE'S OWN BASIS, from the dossier that described it. This read
            # `CONTEXT_SUPPORTED if context else DIRECT_ANCHOR`, so the basis was
            # decided by which branch ran rather than by what the builder concluded
            # about the file -- and `DossierFile.basis` is already one of
            # `MEMBERSHIP_BASES` and is that conclusion.
            direct = item.basis == DIRECT_ANCHOR
            support = _support_of(dossier, item)
            if not support:
                # `records.py`: "a membership with no support cannot say why the
                # file belongs". P9 authors none, so a member whose evidence the
                # dossier does not carry gets no row -- and the model's decision
                # about it is still on disk in `llm_response` under this verdict.
                continue
            record_membership(conn, Membership(
                membership_id=membership_id,
                group_id=row.group_id,
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
                    group_id=row.group_id, membership_id=membership_id,
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
            written_files.add(item.file_id)
        if carried_from is not None:
            # `104` R-80's other half, and the reason a supersession is available
            # at all: a new `group_id` names a row no membership names, so the
            # memberships have to arrive on it or the superseding group is an
            # empty one and the superseded row keeps the files. Carried AFTER the
            # loop and past the files this answer decided itself -- those already
            # have a row under this verdict, and a second one would be one file
            # with two standing memberships of one group.
            for carried in carry_memberships(
                    conn, from_group_id=carried_from, into_group_id=row.group_id,
                    except_files=frozenset(written_files)):
                if carried.decision == UNCERTAIN:
                    # The obligation travels with the decision. The refusal above
                    # has already established there is a plan version to record it
                    # in, for exactly this row.
                    record_context_review_pending(
                        conn, plan_version_id=plan_version_id,
                        group_id=row.group_id,
                        membership_id=carried.membership_id,
                        created_at=created_at)
    _record_the_models_acceptance(
        conn, group_id=row.group_id, plan_version_id=plan_version_id,
        verdict_id=result.verdict_id, created_at=created_at)
    return _decision(row, dossier, membership_ids=tuple(written))


def _record_the_models_acceptance(conn: sqlite3.Connection, *, group_id: str,
                                  plan_version_id: str | None, verdict_id: str,
                                  created_at: str) -> None:
    """`104` SF-3: B's ACCEPTING verdict is what decides this group's plan opinion.

    **Reached only from the accepting branch, and only when B is ratified.** The
    one gate on "may B act" is `prompt.ratified`, read at `cli.observed_run_call`
    and nowhere else: an unratified site returns `ObservedOnly` and this function
    is unreachable from it. Nothing here ratifies anything -- that is the owner's
    act -- and nothing here reads the flag a second time, because a second reading
    is a second answer to the same question.

    **This is the row `review_and_accept` used to write with nobody's judgement
    behind it.** SF-3 measured the old one: every group P9 proposed was recorded
    `accepted`, `coherent`, `decided_by=RULES`, on a screen nobody saw. The rules
    now DRAFT (`cli.draft_for_review`), and the draft is decided by one of exactly
    two things -- a person's gesture, or this.

    `decided_by=VALIDATOR` and not `LLM`: `DECIDED_BY` has three members and the
    model is not one of them, and the honest one of the three is the one that is
    true. `ACCEPT_DIRECT` and `ACCEPT_CONTEXT_SUPPORTED` are P8's VALIDATOR's
    outcomes over the model's claim, reached only after P8's own checks passed, so
    the decider named here is the part that did the deciding. P9 reads no citation
    and runs no second validator to find that out -- it reads the outcome word.

    `review_state=PENDING_REVIEW` beside `acceptance=ACCEPTED`, because both are
    true and they are about different questions: this plan version accepts the
    group, and no person has reviewed it yet. §4.9's whole design is that the user
    makes the final call, and a `not-required` here would say they never need to.

    **Silent without a plan version.** An acceptance is the ONE plan-versioned
    record P9 publishes, so a caller with no version has nowhere to record one --
    and the uncertain-member refusal above has already raised for the case where
    that absence costs something.

    **A SECOND ANSWER SUPERSEDES THE FIRST BY NAME**, which is the same rule
    `_the_answers_row` applies to the group row one call up and is enforced here by
    `one_current_group_acceptance`: the index is over unsuperseded rows, so a
    second run answering the same group under a new verdict id would be refused by
    the database rather than by a check. The standing row is read and named, and
    the same verdict answering twice writes nothing new -- `record_acceptance`
    returns the id it already holds.

    **A PERSON'S ROW IS NEVER SUPERSEDED HERE.** It cannot be: `_the_answers_row`
    returns `None` above when a person has accepted, so this function is
    unreachable for that group at all. The guard is restated as a refusal rather
    than trusted, because the cost of being wrong is the model quietly overwriting
    the one decision the product exists to keep.
    """
    if not plan_version_id:
        return
    standing = conn.execute(
        "SELECT acceptance_id, decided_by FROM group_acceptance "
        "WHERE plan_version_id = ? AND group_id = ? AND membership_id IS NULL "
        "AND superseded_by IS NULL",
        (plan_version_id, group_id)).fetchone()
    if standing is not None and standing["decided_by"] == USER:
        raise ValueError(
            f"group {group_id!r} carries a standing acceptance decided by the "
            f"person in {plan_version_id!r}; a model answer does not supersede "
            "one. `_the_answers_row` returns None for this case and this branch "
            "should not have been reached"
        )
    acceptance_id = f"acc:{plan_version_id}:{group_id}:{verdict_id}"
    supersedes = (standing["acceptance_id"]
                  if standing is not None
                  and standing["acceptance_id"] != acceptance_id else None)
    record_acceptance(conn, GroupAcceptance(
        acceptance_id=acceptance_id,
        plan_version_id=plan_version_id, group_id=group_id,
        membership_id=None, acceptance=ACCEPTED,
        review_state=PENDING_REVIEW, user_edited_label=None, aliases=(),
        review_decision_ref=verdict_id, decided_by=VALIDATOR,
        created_at=created_at, supersedes=supersedes,
        supersede_reason=(None if supersedes is None else
                          "site B answered this group again")))


# --- `104` R-O: a refusal is an outcome here too -------------------------------


def refused_group_call(conn: sqlite3.Connection, *, group_id: str,
                       error: BaseException, observed_at: str) -> CallRefused:
    """One refused site-B call, recorded and handed back.

    HERE rather than in `pipeline.py` for the reason this module exists: it is the
    only file under `src/grouping/` allowed to know P8, and
    `tests/p9/test_p9_no_invention.py` reads every module's imports to keep it
    that way. `REFUSAL_EXCEPTIONS` is re-exported above for the same reason -- the
    caller needs the tuple and may not reach `privacy.resolve` for it.
    """
    return refusal_outcome(
        conn, call_site=B_GROUP, subject_ref=group_id, error=error,
        observed_at=observed_at)
