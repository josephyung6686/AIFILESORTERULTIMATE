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
from typing import Any, Callable, Mapping

from evidence_shape.canonical import canonical_json
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS, check

from facts.cache import llm_pass_cache_key
from facts.domains import active_field_allowlist
from facts.evidence import cite, observations_for_version
from facts.file_facts import LLM_INTERPRETATION, facts_for_file, write_fact
from facts.states import EXCLUDED_STATE, LLM_SUPPORTED, POSSIBLE, is_stronger
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
                  normalizers: Mapping[str, Callable[[str], Any]]) -> FactRequest:
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
        normalizers=normalizers)


def apply_verdict(conn: sqlite3.Connection, *, request: FactRequest,
                  proposal: Proposal, verdict: Verdict, proposal_state: str,
                  model_identifier: str, prompt_fingerprint: str) -> str | None:
    """Done-means 11 and 12. The consequence of one verdict, and never the check.

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
        write_unresolved(
            conn, file_id=request.file_id, content_hash=request.content_hash,
            field_key=proposal.field_key, reason=reason,
            attempted_producers=(LLM_ROUTE,),
            evidence_refs=tuple(proposal.citations), cache_key=cache_key)

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
        conn, field_key=proposal.field_key, canonical_value=proposal.value,
        first_evidence_ref=proposal.citations[0] if proposal.citations else None,
        origin=VALUE_ORIGINS[0])
    return write_fact(
        conn, file_id=request.file_id, content_hash=request.content_hash,
        field_key=proposal.field_key, value_id=value_id,
        reliability_state=reliability_state, origin=LLM_INTERPRETATION,
        evidence_refs=tuple(proposal.citations), cache_key=cache_key, active=True,
        model_identifier=model_identifier, prompt_fingerprint=prompt_fingerprint)
