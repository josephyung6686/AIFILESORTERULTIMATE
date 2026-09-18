# src/facts/llm_seam.py
"""O6 -- what P6 hands P8, and the consequence of each verdict (§3.3, §3.5, §3.6).

§3.6, and every clause of it binds here:

    "Every LLM-produced fact must pass a validation step before it becomes active in
     the database. The validator checks that the proposed field exists in the relevant
     domain schema, that the model's cited quote or metadata field is actually present
     in the stored evidence, that the proposed value can be normalized safely, and
     that no stronger direct or rule-validated fact contradicts it. A model that
     cannot cite sufficient evidence must return unknown. A model output that is
     useful but too weak to establish a fact may remain a possible clue for review; it
     must not quietly become a folder proposal or an asserted file property."

**P6 supplies the four inputs and owns none of the checking.** `apply_verdict` takes a
`Verdict` it did not compute. A PASSING verdict over a proposal citing a key that is
not in the store therefore writes a fact -- deliberately, because the alternative is
P6 and P8 each holding half a validator and drifting apart. P8 can be built against
this shape without this module changing.

**One floor is not left to the verdict.** §3.5: the LLM "is not allowed to invent a
new fact schema, create an unsupported field". The field catalogue is closed, so a
passing verdict naming a field outside it raises `FieldNotInCatalogue` through the
value and fact writers -- not because this module checked, but because there is no row
to point at. The ALLOWLIST is narrower than the catalogue and is check 1's input,
which is P8's.

**UNRESOLVED SEAM (round 4, C-5) -- do not close it here.** P8's SPEC names two
functions as P6's: a normalizer `normalize(field, raw_value) -> value |
not_normalizable` and a contradiction oracle `contradicts(claim, existing_fact) ->
bool`. P8's own Deferred table files their domain logic back to P6, and P6's task says
P6 owns none of the checking -- so each part hands them to the other and neither
builds them. This module supplies the four INPUTS (allowlist, citable observations,
existing stronger facts, per-field normalizers as injected data) and publishes NEITHER
function. A test asserts no module in `facts` publishes one, so the day someone adds
it, the decision gets made rather than absorbed. The ruling is owed before P8 is
planned.

**Five verdicts, five reasons, no shared bucket.** The reason is derived from the
failed check rather than supplied, because P6 owns the `unresolved` vocabulary and P8
must not spell a member of it. The fifth outcome is not a check at all: an explicit
`unknown` is the model declining before anything could be validated.

**And a refusal never raises.** The one thing `refuse` does not take on trust is that
the model's reference is a citation at all: what the model is shown is a wire handle,
what M14 admits into `evidence_refs` is an `observation_key`, and a handle the release
never issued translates to neither. Such a reference is dropped from the row and moves
the row's reason to check 2's, which is still one of the five. See `refuse` for the run
this cost.

**The ceiling is a function, not a call site.** `require_llm_state` is the only gate to
an LLM-origin fact and admits exactly `llm_supported` and `possible`, so a test can
attempt the promotion and require the raise. Which of the two a proposal earns is
§3.7's score-and-margin question and is Deferred, so `proposal_state` is required with
no default.

**There is no model call here, and no default for one.** §3.3 puts every model call in
P8. `analysis_tier = "llm"` is a value recorded on a cache key, never a call.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from evidence_shape.canonical import canonical_json
from evidence_shape.observation import Observation, is_observation_key
from evidence_shape.vocabulary import ANALYSIS_TIERS, check

from facts.cache import llm_pass_cache_key
from facts.domains import active_field_allowlist
from facts.evidence import cite, observations_for_version
from facts.fields import FieldNotInCatalogue, get_field
from facts.file_facts import LLM_INTERPRETATION, facts_for_file, write_fact
from facts.states import (EXCLUDED_STATE, LLM_SUPPORTED, POSSIBLE, USER_CONFIRMED,
                          is_stronger)
from facts.supersede import FACT_TABLE, supersede_fact
from facts.unresolved import ATTEMPTED_PRODUCERS, LLM_ROUTE, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: §3.6's four, in §3.6's own order. These are names for the CHECKS, which are P8's;
#: P6 publishes them so both parts address one list.
FOUR_CHECKS: tuple[str, ...] = (
    "field_in_active_schema",
    "citation_present_in_evidence",
    "value_normalizes_safely",
    "no_stronger_fact_contradicts",
)

#: The one correspondence between P8's checks and P6's `unresolved` reasons. It lives
#: here because P6 owns the reason vocabulary: a `Verdict` names the check that
#: failed, never the reason, so P8 never spells a member of P6's closed set.
CHECK_REASONS: Mapping[str, str] = {
    FOUR_CHECKS[0]: "field_not_in_active_schema",
    FOUR_CHECKS[1]: "citation_absent_from_evidence",
    FOUR_CHECKS[2]: "normalization_failed",
    FOUR_CHECKS[3]: "contradicted_by_stronger_fact",
}

#: The fifth outcome, and it is not a check: §3.6's "A model that cannot cite
#: sufficient evidence must return unknown" is the model declining before anything
#: could be validated.
UNKNOWN_REASON: str = "model_returned_unknown"

#: The only two states an LLM-origin fact may carry. §3.13 gives `llm_supported` to a
#: model conclusion that passed validation; §3.6 gives `possible` to one that is
#: "useful but too weak to establish a fact". Which of the two is §3.7's question and
#: is Deferred, so nothing here chooses between them.
LLM_STATES: tuple[str, str] = (LLM_SUPPORTED, POSSIBLE)


class ProposalStateRefused(ValueError):
    """§3.6's ceiling, raised rather than documented."""


def require_llm_state(reliability_state: str) -> str:
    """The only gate to an LLM-origin fact.

    §3.6: a model output "must not quietly become a folder proposal or an asserted
    file property". That is a statement about every route, so it is enforced where
    every route has to pass rather than at the one call this module makes.
    """
    if reliability_state not in LLM_STATES:
        raise ProposalStateRefused(
            f"§3.6 admits an LLM-origin fact at {LLM_STATES!r} only; "
            f"{reliability_state!r} would give a model conclusion the standing of a "
            "directly extracted or rule-validated fact")
    return reliability_state


@dataclass(frozen=True)
class FactRequest:
    """The four inputs P6 supplies for one file version. P8 consumes; P6 checks none.

    `normalizers` is carried, not called. Per-field normalizers and alias tables are a
    Deferred row -- `U Chicago -> University of Chicago -> UChicago` is "one worked
    example, not a table" -- so P6 authors none of the contents and injects the whole
    mapping. See the C-5 note in the module docstring: `normalize` as a FUNCTION has
    no owner in either part's plan.
    """

    file_id: str
    content_hash: str
    allowlist: tuple[str, ...]
    citable_observations: tuple[Observation, ...]
    existing_facts: tuple[sqlite3.Row, ...]
    normalizers: Mapping[str, Callable[[str], Any]]
    #: `104` R-135: readings of ANOTHER file that this call was allowed to show as
    #: CONTEXT, and which a citation may therefore name. Separate from
    #: `citable_observations` and not folded into it, because that field is this file
    #: version's own readings and check 2's coarse half is written against exactly
    #: that: a fact is about a file, and an answer resting only on a neighbour's words
    #: is a different kind of answer. P8 records the difference rather than losing it
    #: -- `EvidenceItem.basis` is `context-supported` for these, so
    #: `validation._acceptance_outcome` returns `ACCEPT_CONTEXT_SUPPORTED` and the
    #: fact carries a review obligation.
    #:
    #: EMPTY BY DEFAULT AND EMPTY IS THE COMMON CASE. A deployment that offers no
    #: context, and a file with no anchor near it, both produce `()`, and check 2 then
    #: admits exactly what it admitted before this field existed.
    context_observations: tuple[Observation, ...] = ()


@dataclass(frozen=True)
class Proposal:
    """One thing the model said about one field, or its refusal to say anything."""

    field_key: str
    value: str | None
    citations: tuple[str, ...]
    unknown: bool

    def __post_init__(self) -> None:
        if self.field_key is None:
            raise ValueError(
                "a proposal names the field it is about, including when it is "
                "`unknown`: §3.6's refusal is per field, `write_unresolved` takes "
                "`field_key: str`, and a whole-file 'unknown' has no row to write. "
                "This was `str | None`, so the None constructed cleanly and surfaced "
                "later as `FieldNotInCatalogue: None is not in the field catalogue` "
                "-- a catalogue error standing in for this seam's own refusal")
        if self.unknown and (self.value is not None or self.citations):
            raise ValueError(
                "an `unknown` proposal is the model declining (§3.6); it carries no "
                "value and no citations, so 'declined' and 'proposed' cannot both be "
                "true of one record")
        if not self.unknown and self.value is None:
            raise ValueError("a proposal that is not `unknown` carries a value")


@dataclass(frozen=True)
class Verdict:
    """P8's answer for one proposal. P6 records the consequence and computes none.

    `reason` is DERIVED from `failed_check`, not supplied: the `unresolved` vocabulary
    is P6's and P8 must not spell a member of it.
    """

    passed: bool
    failed_check: str | None = None
    reason: str | None = field(default=None)

    def __post_init__(self) -> None:
        if self.passed and self.failed_check is not None:
            raise ValueError("a verdict that passed names no failed check")
        if not self.passed and self.failed_check is None:
            raise ValueError(
                "a verdict that failed names WHICH of §3.6's four checks failed; "
                "five verdicts carry five reasons and there is no shared bucket")
        if self.failed_check is not None:
            check(self.failed_check, FOUR_CHECKS, name="failed_check")
            object.__setattr__(self, "reason", CHECK_REASONS[self.failed_check])


def build_request(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                  activation_signals: Any,
                  normalizers: Mapping[str, Callable[[str], Any]],
                  context_observations: Sequence[Observation] = ()) -> FactRequest:
    """The four inputs, for one file version.

    The allowlist is Task 13's answer, not a second reading of the catalogue: §3.5's
    "may extract only fields allowed by the relevant schema" must be ONE computation,
    or the model is measured against one list and validated against another.

    `existing_facts` is every ACTIVE fact stronger than an LLM conclusion --
    `user_confirmed`, `direct`, `validated` -- derived through `is_stronger` rather
    than listed, so §3.13's ordering has one home. `rejected` is filtered by MEMBERSHIP
    before any comparison, because §3.13 makes it an exclusion rather than a rank and
    `strength` raises on it: a rejected fact is not a weak fact, and asking how strong
    it is would end the pass with a vocabulary error. These are check 4's input.
    Whether any of them CONTRADICTS a proposal is not decided here (C-5).
    """
    established = facts_for_file(conn, file_id, content_hash)
    stronger = tuple(
        row for row in established
        if row["active"]
        and row["reliability_state"] != EXCLUDED_STATE
        and is_stronger(row["reliability_state"], LLM_STATES[0]))
    return FactRequest(
        file_id=file_id,
        content_hash=content_hash,
        allowlist=tuple(active_field_allowlist(
            conn, file_id=file_id, content_hash=content_hash,
            activation_signals=activation_signals)),
        citable_observations=tuple(
            observations_for_version(conn, file_id, content_hash)),
        existing_facts=stronger,
        normalizers=normalizers,
        # `104` R-135. The CALLER's, never read from the database here: which
        # neighbouring readings a call may show is a composition decision about
        # folders, privacy and the field being asked, and P6 owns none of the three.
        context_observations=tuple(context_observations))


def apply_verdict(conn: sqlite3.Connection, *, request: FactRequest,
                  proposal: Proposal, verdict: Verdict, proposal_state: str,
                  model_identifier: str, prompt_fingerprint: str,
                  canonical_value: str | None) -> str | None:
    """Done-means 11 and 12. The consequence of one verdict, and never the check.

    **`canonical_value` is what gets STORED, and it is required with no default.**
    It is check 3's own output -- the caller ran the deployment's normalizer to decide
    whether this proposal was normalizable at all, and this is that answer rather than
    a second computation of it. `proposal.value` stays the model's raw string, because
    check 2's grounding has to match the text the model actually quoted; what the
    `values` table records is the identity, not the printing.

    Until 2026-09-04 this wrote `proposal.value` and the normalized form was computed,
    spent on check 3, and dropped. Measured consequence on a real run:
    `PHYS1401_Lecture08_Template.pdf` carried TWO active `subject` facts, `PHYS1401`
    from the direct slot and `PHYS 1401` from the model, and a level dividing on
    `subject` builds two folders for one course. Worse, check 4 had already recognised
    the two as one value -- `contradicts_stronger` compares after canonicalisation, so
    the model was seen to AGREE -- and the write then introduced the second spelling
    the check had just decided was not a second value. That is `65` §4.2's failure
    re-created across the seam instead of inside one stage.

    `None` is accepted because a REJECT carries no canonical form (check 3 failing IS
    `normalized is None`), and every such path refuses above without reaching the
    write. A `None` arriving on a passing verdict would be a caller defect, and the
    `ensure_value` below would raise on it rather than store it.

    Returns the new `fact_id`, or `None` when nothing was written -- in which case an
    `unresolved` row names the field and the reason (B7). Five outcomes, five reasons,
    no shared "rejected" bucket:

        unknown                         model_returned_unknown
        check 1 failed                  field_not_in_active_schema
        check 2 failed                  citation_absent_from_evidence
        check 3 failed                  normalization_failed
        check 4 failed                  contradicted_by_stronger_fact

    The `unknown` branch is taken BEFORE the verdict is read: the model declined, so
    there was nothing to validate and a verdict about it would be a statement nobody
    made.

    §3.3: the two model parts are `None` on every deterministic fact and this is the
    one exception, so P8's two values are written onto the fact row as well as into
    its cache key -- a row that recorded neither would leave "which model, under which
    prompt" answerable only by re-deriving the digest.
    """
    cache_key = llm_pass_cache_key(
        conn, file_id=request.file_id, content_hash=request.content_hash,
        model_identifier=model_identifier,
        prompt_fingerprint=prompt_fingerprint)

    def refuse(reason: str) -> None:
        """Record one refusal, and NEVER raise while doing it.

        `proposal.citations` is the MODEL'S reference, and it is not always a
        citation. The model is shown wire handles rather than observation keys
        (`llm_harness.wire_handles` -- an un-keyed P4 key printed beside its own
        locator was a dictionary attack on the value), so what comes back is a
        `handle:` reference that P8 translates through the handles the release
        actually issued. A handle it never issued -- a hallucination, a truncation,
        a plain invention -- translates to nothing and arrives here unchanged.

        This forwarded it into `evidence_refs`, which M14 reserves for `sha256:`
        observation keys, and `write_unresolved` raised. Measured on a live
        `qwen3:8b` run over 199 files: 112 facts written, two hours in, and the
        120th fact call died on its own abstention. `ValueError` is not in
        `llm_harness.records.REFUSAL_EXCEPTIONS` -- correctly, it names a
        programming error -- so it left `harness.run_call` and ended the pass. B7
        exists so that P2 can tell a considered refusal from a crash; a refusal
        that crashes is the one outcome this row must never have.

        So a reference this seam cannot recognise as a citation is not written as
        one, and the fact that it could not be recognised is itself the refusal's
        subject: the reason becomes the one word P6's vocabulary has for a citation
        that does not hold, whichever check the verdict named. No reason code is
        added -- `CHECK_REASONS` already derives it from check 2 -- and
        `evidence_refs` keeps the keys that DID translate, possibly none. The
        `P8Verdict` is untouched and still carries the reference itself in
        `citations_checked`, unresolved and unmatched, which is where a reader
        finds out what the model actually said.
        """
        cited = tuple(ref for ref in proposal.citations if is_observation_key(ref))
        if len(cited) != len(proposal.citations):
            reason = CHECK_REASONS[FOUR_CHECKS[1]]
        # The FIELD is the model's word too, and it is not always a field. `104`
        # §18.37: on the first run of A v4 over the owner's corpus the cloud model
        # answered `unknown` for a field it had named `terminus`; the `unknown`
        # branch is taken before any check reads the verdict, so the refusal
        # reached `write_unresolved`, which resolves its key through the closed
        # catalogue (§3.12: no invented fields) and raised `FieldNotInCatalogue`
        # -- the same shape as the `ValueError` above, one row down: a refusal
        # that crashed, 192 files in. An unresolved row is a statement about a
        # field the schema has; a field it does not have gets no row, because
        # there is nothing for the row to be about. What the model said is still
        # on the `P8Verdict` (`field_key`, `citations_checked`), which is where a
        # reader finds it; nothing is written and nothing raises.
        try:
            get_field(conn, proposal.field_key)
        except FieldNotInCatalogue:
            return
        write_unresolved(
            conn, file_id=request.file_id, content_hash=request.content_hash,
            field_key=proposal.field_key, reason=reason,
            attempted_producers=(LLM_ROUTE,),
            evidence_refs=cited, cache_key=cache_key)

    if proposal.unknown:
        refuse(UNKNOWN_REASON)
        return None
    if not verdict.passed:
        refuse(verdict.reason)
        return None

    # The state is gated before anything is written, so a refused promotion leaves no
    # value row behind either.
    reliability_state = require_llm_state(proposal_state)
    value_id = ensure_value(
        conn, field_key=proposal.field_key, canonical_value=canonical_value,
        first_evidence_ref=proposal.citations[0] if proposal.citations else None,
        origin=VALUE_ORIGINS[0])
    return write_fact(
        conn, file_id=request.file_id, content_hash=request.content_hash,
        field_key=proposal.field_key, value_id=value_id,
        reliability_state=reliability_state, origin=LLM_INTERPRETATION,
        evidence_refs=tuple(proposal.citations), cache_key=cache_key, active=True,
        model_identifier=model_identifier, prompt_fingerprint=prompt_fingerprint)


#: `104` §18.95's two field keys, spelled here because this module writes them and
#: `facts.fields` declares them; a typo in either place is a `FieldNotInCatalogue`
#: at the write and not a silently missing row.
SITUATION_FIELD: str = "situation"
SITUATION_ALTERNATIVE_FIELD: str = "situation_alternative"


def record_the_situation(conn: sqlite3.Connection, *, file_id: str,
                         content_hash: str, situation: str,
                         alternatives: Sequence[str], evidence_refs: Sequence[str],
                         cache_key: str, model_identifier: str | None = None,
                         prompt_fingerprint: str | None = None) -> tuple[str, ...]:
    """Write what site G said about this file as facts about the file.

    **THE HOLE THIS CLOSES.** Until 16 Sep 2026 the situation judge's answer was
    stored nowhere. It reached `privacy.ClassificationRecord`, which records the
    HANDLING CLASS the situation implies and not the situation's name, and the name
    itself survived only inside `llm_response.response_bytes` -- so every reader
    re-parsed raw model JSON to learn what the product had decided, and
    `situation_verdict_before` read it back for one purpose only, not re-asking. A
    conclusion the product acts on is a fact about the file.

    **TWO STATES, AND THE DIFFERENCE IS WHAT THE JUDGE CITED.** The first choice is
    `llm_supported`: P8 checked its citations against what P7 released, span by
    span. An alternative is `possible`: the judge said it also fits and cited
    nothing for it separately. Writing both at `llm_supported` would give an
    uncited reading the standing of a checked one, which is the ceiling
    `require_llm_state` exists to hold. The citations recorded on an alternative
    are the same released observations the judge read -- that is what it read them
    OUT of -- and the state is what says it did not quote them.

    **NO PATH, NO FOLDER, NO PLACEMENT**, per `write_fact`'s own contract: neither
    field is destination-eligible (`00` amendment 9 -- the situation is an input to
    the sort and never a level of it), so nothing written here can become a folder.

    Returns the fact ids written, first choice first.
    """
    refs = tuple(evidence_refs)
    # THE SLOT BEFORE THIS CALL, read first because the write is what retires it.
    # `situation` is single-valued and `preferred_fact`'s three cases decide what a
    # reader gets: live rows naming ONE value are that value; live rows naming
    # SEVERAL are resolvable only through `preferred`, and otherwise the slot
    # answers `None` -- open question 6, which a reader that picked one would close
    # by accident. So a second run that changes its mind, with nothing retired,
    # does not leave a stale answer standing: it makes the file's situation
    # UNREADABLE. That is the failure this retirement prevents.
    standing = [row for row in conn.execute(
        'SELECT ff.fact_id, ff.reliability_state, v.canonical_value '
        'FROM file_facts ff JOIN "values" v USING(value_id) '
        "WHERE ff.file_id = ? AND ff.content_hash = ? AND ff.field_key = ? "
        "AND ff.superseded_by IS NULL",
        (file_id, content_hash, SITUATION_FIELD))]
    written: list[str] = []
    for value, state in ((situation, LLM_SUPPORTED),
                         *((alternative, POSSIBLE) for alternative in alternatives)):
        field_key = (SITUATION_FIELD if state is LLM_SUPPORTED
                     else SITUATION_ALTERNATIVE_FIELD)
        value_id = ensure_value(
            conn, field_key=field_key, canonical_value=value,
            first_evidence_ref=refs[0] if refs else None, origin=VALUE_ORIGINS[0])
        written.append(write_fact(
            conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
            value_id=value_id, reliability_state=require_llm_state(state),
            origin=LLM_INTERPRETATION, evidence_refs=refs, cache_key=cache_key,
            active=True, model_identifier=model_identifier,
            prompt_fingerprint=prompt_fingerprint))
        if state is not LLM_SUPPORTED:
            # ALTERNATIVES ARE A SET AND ARE NOT RETIRED HERE. Several live values
            # is their normal state, so their slot is unresolvable by design and a
            # reader takes the rows, not the pointer. Pairing a stale alternative
            # with a new one by position would write "this replaced that" about two
            # readings that have nothing to do with each other.
            continue
        # `106` PHASE 2(b) / `104` §18.108: A REPLAYED ANSWER DOES NOT TAKE THE
        # POINTER BACK. This field now has TWO writers in one run -- the kind pass,
        # then the level pass with the finer situation -- so on a SECOND run of the
        # same command `write_fact`'s idempotence (`file_facts.py`: "returns the
        # existing row") hands the kind pass the row it wrote last time, WHICH THE
        # LEVEL PASS HAS SINCE RETIRED. Retiring the live finer row with that stale
        # one leaves both rows superseded, no live row naming the slot, and
        # `preferred_fact` answering `None`: the file's situation would become
        # unreadable BY HAVING BEEN ANSWERED TWICE -- the very failure the
        # retirement above exists to prevent, reached from the other direction.
        #
        # `supersede_fact` cannot catch this: it guards `old["superseded_by"]` and
        # `new["supersedes"]`, and in this shape both are clear. The rule belongs
        # here, and it is §3.13's own -- `preferred` never reverses for the
        # person's answer, and it must not reverse for a STALE one either.
        #
        # SKIPPED, NOT RAISED. A run must not die over an ordering question;
        # `104` §17.2's rule is that a gap must never become a file that vanished.
        retired = conn.execute(
            f"SELECT superseded_by FROM {FACT_TABLE} WHERE fact_id = ?",
            (written[-1],)).fetchone()
        if retired is not None and retired[0] is not None:
            continue
        for row in standing:
            if row["canonical_value"] == value:
                # The same answer again: `write_fact` is idempotent at one identity
                # and two rows naming one `value_id` are ONE answer with two
                # citations, which `preferred_fact` already resolves.
                continue
            if row["reliability_state"] == USER_CONFIRMED:
                # THE PERSON'S OWN ANSWER IS NOT OVERRULED BY A RE-RUN. §3.13's
                # ordering is not negotiable and `supersede_fact` raises rather than
                # let a weaker row take the pointer; this skip means the model's new
                # answer is recorded beside it and the person's still reads.
                continue
            supersede_fact(
                conn, old_fact_id=row["fact_id"], new_fact_id=written[-1],
                reason=(f"site G named {value} under call {cache_key}; the earlier "
                        f"{row['canonical_value']} stood at "
                        f"{row['reliability_state']}"))
    return tuple(written)
