# src/llm_harness/store.py
"""Append-only P8 writers. No overwrite, no upsert, no runtime event registration.

The writer→event matrix is closed. `model_call_issued` is Task 5 transport.
`record_call_failure` is a row only. `NeedsConsent` has no writer here.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from collections.abc import Mapping
from dataclasses import fields, is_dataclass

from database_agent.db import transaction
from database_agent.events import append_event
from database_agent.supersede import mark_superseded
from evidence_shape.canonical import canonical_json

from llm_harness.authorship import (
    CALL_REFUSED,
    MODEL_RESPONSE_RECEIVED,
    VALIDATION_VERDICT,
    VERDICT_SUPERSEDED,
    event_defaults,
)
from llm_harness.dossier import dossier_from_stored_body
from llm_harness.records import (
    CallRefused,
    GroundingReport,
    MalformedRecord,
    P8Verdict,
    PreCallAbstention,
    Refusal,
)
from llm_harness.vocabulary import pre_call_address


def _jsonable(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: _jsonable(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, bytes):
        return value.hex()
    return value


def _payload(record: object) -> str:
    return canonical_json(_jsonable(record))


def _new_id() -> str:
    return str(uuid.uuid4())


def _require_response_bytes(response_bytes: object) -> bytes:
    if not isinstance(response_bytes, (bytes, bytearray, memoryview)):
        raise TypeError(
            "response_bytes must be bytes; SQLite stores str as TEXT, not BLOB"
        )
    return bytes(response_bytes)


def _explanation(*, audit_id: int | None, model_id: str | None,
                 prompt_fingerprint: str | None, **extra: object) -> str:
    body = {
        "audit_id": audit_id,
        "model_id": model_id,
        "prompt_fingerprint": prompt_fingerprint,
        **extra,
    }
    return canonical_json(body)


def _append(conn: sqlite3.Connection, *, event_type: str, observed_at: str,
            explanation: str, prompt_fingerprint: str | None = None) -> int:
    fields = event_defaults(
        event_type=event_type,
        observed_at=observed_at,
        explanation=explanation,
    )
    if prompt_fingerprint is not None:
        fields["prompt_fingerprint"] = prompt_fingerprint
    return append_event(conn, **fields)


def record_dossier(conn: sqlite3.Connection, dossier, *, observed_at: str) -> str:
    """Record one dossier by its content address. Appends no event.

    `dossier_id` is the address of the model-visible bytes, so identical bytes
    are the same dossier and recording them twice is not a second row -- it was a
    bare INSERT against a PRIMARY KEY, and the second identical call raised
    `IntegrityError` out of `run_call` with a reservation already taken and no
    path left to settle it.

    An address whose stored content differs from the content offered under it is
    a different failure entirely, and never a silent overwrite: the row is
    append-only by trigger and this refuses before reaching it.
    """
    # The stored payload is the content, and the content alone. `Dossier` carries
    # `release_id` because one call needs it; the row is addressed by content and
    # two calls over identical content are one row, so the capability that paid
    # for either of them is not part of it.
    body = {
        name: value for name, value in _jsonable(dossier).items()
        if name != "release_id"
    }
    payload = canonical_json(body)
    row = conn.execute(
        "SELECT call_site, subject_ref, eligibility_reason, plan_version, "
        "policy_version, reduction_rung, payload FROM llm_dossier "
        "WHERE dossier_id = ?",
        (dossier.dossier_id,),
    ).fetchone()
    if row is not None:
        stored = (
            row["call_site"], row["subject_ref"], row["eligibility_reason"],
            row["plan_version"], row["policy_version"], row["reduction_rung"],
            row["payload"],
        )
        offered = (
            dossier.call_site, dossier.subject_ref, dossier.eligibility_reason,
            dossier.plan_version, dossier.policy_version, dossier.reduction_rung,
            payload,
        )
        if stored != offered:
            raise MalformedRecord(
                f"dossier {dossier.dossier_id} is already recorded with different "
                "content; a content address that disagrees with its content is "
                "not something P8 resolves by overwriting"
            )
        return dossier.dossier_id
    conn.execute(
        "INSERT INTO llm_dossier ("
        "dossier_id, call_site, subject_ref, eligibility_reason, plan_version, "
        "policy_version, reduction_rung, payload, observed_at"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            dossier.dossier_id, dossier.call_site, dossier.subject_ref,
            dossier.eligibility_reason, dossier.plan_version, dossier.policy_version,
            dossier.reduction_rung, payload, observed_at,
        ),
    )
    return dossier.dossier_id


def record_response(conn: sqlite3.Connection, *, dossier_id: str, response_bytes: bytes,
                    model_id: str, prompt_fingerprint: str, release_audit_id: int,
                    release_id: str, observed_at: str) -> str:
    """Store raw response bytes and append `model_response_received`.

    `release_id` is the single-use capability that paid for THIS call. It lives
    here and not on the dossier: the dossier is the content, and two calls over
    identical content are one dossier and two releases.
    """
    response_bytes = _require_response_bytes(response_bytes)
    if not release_id:
        raise MalformedRecord("a recorded response names the release that paid for it")
    response_id = _new_id()
    with transaction(conn):
        conn.execute(
            "INSERT INTO llm_response ("
            "response_id, dossier_id, response_bytes, model_id, prompt_fingerprint, "
            "release_audit_id, release_id, observed_at"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                response_id, dossier_id, response_bytes, model_id,
                prompt_fingerprint, release_audit_id, release_id, observed_at,
            ),
        )
        _append(
            conn,
            event_type=MODEL_RESPONSE_RECEIVED,
            observed_at=observed_at,
            prompt_fingerprint=prompt_fingerprint,
            explanation=_explanation(
                audit_id=release_audit_id,
                model_id=model_id,
                prompt_fingerprint=prompt_fingerprint,
                dossier_id=dossier_id,
                response_id=response_id,
            ),
        )
    return response_id


def last_response_bytes(conn: sqlite3.Connection, dossier_id: str) -> bytes | None:
    """The most recently recorded response for one dossier, or `None`.

    **Read at the call boundary and nowhere else.** `104` R-16: a site that applies
    the model's own answers needs the answer, and `P8Verdict` carries a `claim_ref`
    and no payload. The composition root reads this IMMEDIATELY after `run_call`
    returns, when the row `run_call` just wrote is the last one for that dossier, so
    "most recent" is exact rather than a guess. A later reader has no such
    guarantee: two calls over identical content are one dossier and two responses
    (`record_response`'s own sentence), so this is not the function to reach for
    from a screen or a report.

    `None` when the call produced no response -- a refusal, a pre-call abstention, a
    transport failure. Every one of those is already an outcome the caller applies
    nothing to.
    """
    row = conn.execute(
        "SELECT response_bytes FROM llm_response WHERE dossier_id = ? "
        "ORDER BY rowid DESC LIMIT 1", (dossier_id,),
    ).fetchone()
    return None if row is None else bytes(row["response_bytes"])


def last_response(conn: sqlite3.Connection, dossier_id: str) -> sqlite3.Row | None:
    """The most recent stored response for one dossier, with its provenance.

    `104` R-127's re-validation reads this and not `last_response_bytes`, because
    re-judging stored bytes has to say WHOSE answer it re-judged: `model_id` and
    `prompt_fingerprint` address the events the new verdict appends, `release_id`
    is the capability the dossier row does not carry (`record_dossier` says why),
    and `release_audit_id` is the join back to P7's ledger. Inventing any of the
    four for a replay would put provenance on a record that nobody supplied.

    Latest by `observed_at` then `rowid`, the same order `stage_output` replays in
    and for its reason: `response_id` is a uuid4, so under the fixed clock every
    test and every replay runs on, "the latest response" was decided by random hex.
    """
    return conn.execute(
        "SELECT response_id, response_bytes, model_id, prompt_fingerprint, "
        "release_audit_id, release_id FROM llm_response WHERE dossier_id = ? "
        "ORDER BY observed_at DESC, rowid DESC LIMIT 1",
        (dossier_id,),
    ).fetchone()


def standing_verdicts(conn: sqlite3.Connection, dossier_id: str) -> list[sqlite3.Row]:
    """Every verdict on this dossier that has not been superseded, oldest first.

    `answered_fields` reduces the same rows to the set of fields it needs; this is
    the rows themselves, because `104` R-127's caller has to read the
    `validator_version` each one was written under and then name each one it
    supersedes. Two readers over one table rather than one reader plus a copy of
    the answer somewhere else -- `answered_fields` gives that rule its own
    paragraph.
    """
    return list(conn.execute(
        "SELECT verdict_id, claim_ref, outcome, validator_version FROM llm_verdict "
        "WHERE dossier_id = ? AND superseded_by IS NULL ORDER BY rowid",
        (dossier_id,),
    ))


def load_dossier(conn: sqlite3.Connection, dossier_id: str, *,
                 release_id: str) -> object | None:
    """The stored `Dossier` for one id, rebuilt and checked. `None` when absent.

    The rebuild itself belongs to `dossier.dossier_from_stored_body`, because
    `test_p8_dossier` allows one dossier writer and is right to: a record put back
    together differently would re-derive different model-visible bytes and so a
    different content address. This reads the row, hands over the body, and checks
    what comes back against what was stored.

    **The round trip is checked and not assumed**, key by key over what the ROW
    holds. A field the row carries and the rebuilt record does not match is a
    rebuild that dropped or mistyped something, and refusing is right: a dossier
    short of a field would be judged against evidence the model was not shown. A
    field the RECORD has and the row does not is the defaulted case -- an old
    `folder_levels`-less row -- and comparing whole encodings would turn that into
    the same refusal, which would make an old database unreadable to say that a
    new field is absent from it.
    """
    row = conn.execute(
        "SELECT payload FROM llm_dossier WHERE dossier_id = ?", (dossier_id,),
    ).fetchone()
    if row is None:
        return None
    body = json.loads(row["payload"])
    dossier = dossier_from_stored_body(body, release_id=release_id)
    rebuilt = _jsonable(dossier)
    if any(rebuilt.get(name) != value for name, value in body.items()):
        raise MalformedRecord(
            f"dossier {dossier_id} does not survive the round trip out of its own "
            "row; a record rebuilt with a field dropped would be judged against "
            "evidence the model was not shown"
        )
    return dossier


def record_verdict(conn: sqlite3.Connection, verdict: P8Verdict, *,
                   model_id: str, prompt_fingerprint: str, release_audit_id: int,
                   observed_at: str) -> str:
    """Insert one verdict row and append `validation_verdict`.

    The three provenance keywords are REQUIRED and carry no defaults. A verdict is a
    claim a model made under a specific prompt, released under a specific audit; a
    default would let a caller record one without saying which, and an event that
    cannot name its model is not provenance. `release_audit_id` is stored as
    `audit_id` in the explanation -- the join back to P7's ledger.
    """
    payload = _payload(verdict)
    with transaction(conn):
        stored = conn.execute(
            "SELECT payload FROM llm_verdict WHERE verdict_id = ?",
            (verdict.verdict_id,),
        ).fetchone()
        if stored is None:
            conn.execute(
                "INSERT INTO llm_verdict ("
                "verdict_id, dossier_id, claim_ref, outcome, disposition, "
                "validator_version, policy_version, plan_version, payload, observed_at"
                ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    verdict.verdict_id, verdict.dossier_id, verdict.claim_ref,
                    verdict.outcome, verdict.disposition, verdict.validator_version,
                    verdict.policy_version, verdict.plan_version, payload,
                    observed_at,
                ),
            )
        elif stored["payload"] != payload:
            # Same dossier, same response, same claim, a different conclusion --
            # only reachable if the validator or an injected authority changed.
            # That is a supersession (SS 8.2), which `model_facts` now performs
            # under `104` R-127: it records the re-judgement at its OWN address
            # and links the two, so the second conclusion never arrives here
            # wearing the first one's id. Reaching this branch means a caller
            # tried to change a conclusion in place, which is an overwrite
            # whatever it is called.
            raise MalformedRecord(
                f"verdict {verdict.verdict_id} is already recorded with a "
                "different conclusion; a re-judgement is recorded at its own "
                "address and superseded, never written over this one"
            )
        _append(
            conn,
            event_type=VALIDATION_VERDICT,
            observed_at=observed_at,
            prompt_fingerprint=prompt_fingerprint,
            explanation=_explanation(
                audit_id=release_audit_id,
                model_id=model_id,
                prompt_fingerprint=prompt_fingerprint,
                verdict_id=verdict.verdict_id,
                dossier_id=verdict.dossier_id,
                validator_version=verdict.validator_version,
                policy_version=verdict.policy_version,
            ),
        )
    return verdict.verdict_id


def supersede_verdict(conn: sqlite3.Connection, old_verdict_id: str,
                      new_verdict_id: str, *, reason: str, model_id: str,
                      prompt_fingerprint: str, release_audit_id: int,
                      observed_at: str) -> None:
    """Link two stored verdicts, keep both rows, append `verdict_superseded`."""
    supersession_id = _new_id()
    with transaction(conn):
        new = conn.execute(
            "SELECT verdict_id FROM llm_verdict WHERE record_id = ?",
            (new_verdict_id,),
        ).fetchone()
        if new is None:
            raise KeyError(f"unknown record {new_verdict_id!r} in llm_verdict")
        mark_superseded(
            conn, "llm_verdict",
            old_id=old_verdict_id, new_id=new_verdict_id, reason=reason,
        )
        conn.execute(
            "INSERT INTO llm_verdict_supersession ("
            "supersession_id, old_verdict_id, new_verdict_id, reason, observed_at"
            ") VALUES (?, ?, ?, ?, ?)",
            (supersession_id, old_verdict_id, new_verdict_id, reason, observed_at),
        )
        _append(
            conn,
            event_type=VERDICT_SUPERSEDED,
            observed_at=observed_at,
            prompt_fingerprint=prompt_fingerprint,
            explanation=_explanation(
                audit_id=release_audit_id,
                model_id=model_id,
                prompt_fingerprint=prompt_fingerprint,
                old_verdict_id=old_verdict_id,
                new_verdict_id=new_verdict_id,
                reason=reason,
            ),
        )


def record_grounding_report(conn: sqlite3.Connection, report: GroundingReport, *,
                            observed_at: str) -> str:
    """Insert one grounding report. Appends no event."""
    report_id = _new_id()
    conn.execute(
        "INSERT INTO llm_grounding_report ("
        "report_id, dossier_id, call_site, model_id, prompt_fingerprint, "
        "validator_version, citations_total, claims_total, reduction_rung, "
        "release_audit_id, payload, observed_at"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            report_id, report.dossier_id, report.call_site, report.model_id,
            report.prompt_fingerprint, report.validator_version,
            report.citations_total, report.claims_total, report.reduction_rung,
            report.release_audit_id, _payload(report), observed_at,
        ),
    )
    return report_id


def _append_call_refused(conn: sqlite3.Connection, report: GroundingReport, *,
                         observed_at: str, **extra: object) -> None:
    _append(
        conn,
        event_type=CALL_REFUSED,
        observed_at=observed_at,
        prompt_fingerprint=report.prompt_fingerprint,
        explanation=_explanation(
            audit_id=report.release_audit_id,
            model_id=report.model_id,
            prompt_fingerprint=report.prompt_fingerprint,
            dossier_id=report.dossier_id,
            **extra,
        ),
    )


def record_refusal(conn: sqlite3.Connection, refusal: Refusal, report: GroundingReport,
                   *, observed_at: str) -> str:
    """P7 `Denied` only: row + zero-count report + one `call_refused`, atomically."""
    if not isinstance(refusal, Refusal):
        raise TypeError("record_refusal stores Refusal constructed from Denied")
    refusal_id = _new_id()
    with transaction(conn):
        conn.execute(
            "INSERT INTO llm_refusal (refusal_id, dossier_id, payload, observed_at) "
            "VALUES (?, ?, ?, ?)",
            (refusal_id, report.dossier_id, _payload(refusal), observed_at),
        )
        record_grounding_report(conn, report, observed_at=observed_at)
        _append_call_refused(
            conn, report, observed_at=observed_at, refusal_id=refusal_id,
        )
    return refusal_id


def record_pre_call_abstention(conn: sqlite3.Connection, abstention: PreCallAbstention,
                               report: GroundingReport, *, observed_at: str) -> str:
    """Ineligible / suppression / exhausted budget: row + report + `call_refused`."""
    abstention_id = _new_id()
    with transaction(conn):
        conn.execute(
            "INSERT INTO llm_pre_call_abstention ("
            "abstention_id, dossier_id, reason, call_site, subject_ref, payload, "
            "observed_at"
            ") VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                abstention_id, report.dossier_id, abstention.reason,
                abstention.call_site, abstention.subject_ref, _payload(abstention),
                observed_at,
            ),
        )
        record_grounding_report(conn, report, observed_at=observed_at)
        _append_call_refused(
            conn, report, observed_at=observed_at, abstention_id=abstention_id,
        )
    return abstention_id


def record_unbuilt_call_abstention(conn: sqlite3.Connection,
                                   abstention: PreCallAbstention, *,
                                   observed_at: str) -> str:
    """The same row, for a call whose REQUEST could never be built (`104` R-136).

    **Why the sibling above cannot serve.** It takes a `GroundingReport`, and
    every report is derived from a `DossierRequest`
    (`validation.report_for_pre_call_terminal`). A `DossierRequest` refuses an
    empty `evidence_items` in its own `__post_init__`, so for the one subject this
    function exists for there is no request to derive a report from -- and
    building a stand-in would put a zero-count report on disk describing a dossier
    that never existed.

    **What it records is what there is.** The address is `pre_call_address`, the
    same shape every pre-call row carries, so one query over
    `llm_pre_call_abstention` finds this beside site A's exhausted-budget rows.
    What it does NOT write is the grounding report and the `call_refused` event:
    nothing was ever grounded, and nothing refused a call that was never built.
    The row and its reason are the whole record.

    `104` R-136 is what this is for. Site C's evidence is the file's settled
    facts, and a file with none had no `evidence_items`, so P11 raised
    `ModelJudgementUnavailable` -- which is outside `REFUSAL_EXCEPTIONS`, so
    nothing caught it and the corpus run died at that file. Measured on the C-live
    run r4: 67.5 minutes, 50 placements, 0 site-C dossiers, on a corpus where
    `subject` was right on 2 files and missing on 19.
    """
    abstention_id = _new_id()
    with transaction(conn):
        conn.execute(
            "INSERT INTO llm_pre_call_abstention ("
            "abstention_id, dossier_id, reason, call_site, subject_ref, payload, "
            "observed_at"
            ") VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                abstention_id,
                pre_call_address(abstention.call_site, abstention.subject_ref),
                abstention.reason, abstention.call_site, abstention.subject_ref,
                _payload(abstention), observed_at,
            ),
        )
    return abstention_id


def record_call_refusal(conn: sqlite3.Connection, refused: CallRefused, *,
                        observed_at: str) -> int:
    """`104` R-O's durable half: one `call_refused` event, and no table of its own.

    **Why an event and not a row.** The two rows that exist would each have to lie.
    `llm_call_failure` requires the `release_id` that was spent -- *"A failed call
    still spent a release, and the row says which one"* -- and a refusal raised
    inside `gate.release` spent none. `llm_pre_call_abstention` requires a member of
    `PRE_CALL_REASON_CODES`, and none of its three means *"the gate could not read
    the request"*; adding a fourth is a spec-level act and the owner's, not an
    agent's. `call_refused` is already P8's registered event for *"this call did not
    happen and here is why"*, and both of the rows above append it too, so a reader
    counting refusals over the run finds all three kinds in one place.

    `dossier_id` is `pre_call_address`, the same address `report_for_pre_call_
    terminal` gives a terminal that never reached a dossier -- deliberately shaped
    so it cannot be mistaken for, or joined to, one.
    """
    if not isinstance(refused, CallRefused):
        raise TypeError("record_call_refusal stores a CallRefused")
    return _append(
        conn,
        event_type=CALL_REFUSED,
        observed_at=observed_at,
        explanation=_explanation(
            audit_id=None, model_id=None, prompt_fingerprint=None,
            dossier_id=pre_call_address(refused.call_site, refused.subject_ref),
            call_site=refused.call_site,
            subject_ref=refused.subject_ref,
            refusal_class=refused.refusal_class,
        ),
    )


def refusal_outcome(conn: sqlite3.Connection, *, call_site: str, subject_ref: str,
                    error: BaseException, observed_at: str) -> CallRefused:
    """One refused call, recorded and handed back as an outcome. `104` R-O.

    Public because the raise can happen BEFORE the call seam is entered: at site A
    `build_fact_request` constructs the `ModelCallRequest`, and at site B
    `build_dossier_request` does, so `__post_init__`'s refusal never reaches
    `run_call`'s own `try`. Every site calls this with the same reduction, so one
    refusal is recorded one way wherever it was raised.
    """
    refused = CallRefused(
        call_site=call_site, subject_ref=subject_ref,
        # THE TYPE, NEVER THE MESSAGE. `transport._client_exception_explanation`
        # reduces a third-party exception the same way and for the same reason:
        # the message that ended the second real run named a file id and a
        # filename, and §8.4's property 4 keeps both out of a durable record.
        refusal_class=type(error).__qualname__)
    record_call_refusal(conn, refused, observed_at=observed_at)
    return refused


def record_call_failure(conn: sqlite3.Connection, *, dossier_id: str,
                        failure_class: str, explanation: str,
                        release_id: str, observed_at: str) -> str:
    """Terminal row on an already-issued call. Appends no event.

    A failed call still spent a release, and the row says which one.
    """
    if not release_id:
        raise MalformedRecord("a call failure names the release that was spent")
    failure_id = _new_id()
    conn.execute(
        "INSERT INTO llm_call_failure ("
        "failure_id, dossier_id, failure_class, explanation, release_id, observed_at"
        ") VALUES (?, ?, ?, ?, ?, ?)",
        (failure_id, dossier_id, failure_class, explanation, release_id, observed_at),
    )
    return failure_id


# ======================================================================================
# `104` R-13: a question already answered under the same identity is not asked again
# ======================================================================================

#: The dimensions a call's identity is taken over: `00`:44's own list -- "content
#: hash, extractor version, analysis tier, model identifier when relevant, and prompt
#: fingerprint" -- plus the terms that sentence leaves implicit at a site that has
#: them. Spelled as a constant so the digest and the stored mapping cannot drift
#: apart, and so a reader can see the whole of what invalidates a cached answer in
#: one place.
#:
#: `subject_ref` is in the KEY and not only in the row: two files under one identity
#: would let one file's declined fields answer for another's.
#:
#: `policy` is the policy's CONTENT and not its version string, and that is measured
#: rather than preferred: `privacy.policy._persist` mints `policy-{uuid4()}` on every
#: call, so two runs under an identical policy carry two version ids. Keyed on the
#: string this cache could never hit once.
#:
#: `plan_version` is `None` at site A -- `model_facts.build_fact_request` says why,
#: "a fact is about a file version and not about a plan" -- and is carried anyway,
#: because it is a real dimension at C and D and a key whose shape changes per site
#: is a key nobody can reason about.
CALL_IDENTITY_DIMENSIONS: tuple[str, ...] = (
    "call_site", "content_hash", "extractor_versions", "model_id", "plan_version",
    "policy", "prompt_fingerprint", "schema_id", "subject_ref",
)


def call_identity(dimensions: Mapping[str, object]) -> str:
    """SHA-256 over the canonical dimension mapping. Every key required, none extra.

    **Why a digest over a mapping rather than a column per dimension.** The mapping
    is stored beside the digest, so a row can be read back and its digest recomputed
    from it. A column per dimension would let a row be written whose columns and
    whose digest disagree, and the disagreement would be invisible.

    **Why the asked field set is NOT a dimension.** It cannot be, and a run says so.
    Run one asks about every open field; the model answers some and declines the
    rest; run two's open set is the declined set, which is smaller. Keyed on the
    asked set the two runs have different identities and the second re-asks
    everything -- which is R-13 itself, reproduced by the fix meant to close it. So
    this is the identity of the QUESTION'S CONTEXT, and which fields are still open
    is what the reuse decision compares against the prior's abstentions.
    """
    missing = set(CALL_IDENTITY_DIMENSIONS) - set(dimensions)
    extra = set(dimensions) - set(CALL_IDENTITY_DIMENSIONS)
    if missing or extra:
        raise MalformedRecord(
            f"a call identity is taken over exactly "
            f"{list(CALL_IDENTITY_DIMENSIONS)}; missing={sorted(missing)} "
            f"unexpected={sorted(extra)}. A digest over a different set of terms is "
            "a different cache, and one that silently accepted fewer terms would "
            "reuse an answer across a change nobody saw."
        )
    return hashlib.sha256(
        canonical_json({name: dimensions[name]
                        for name in CALL_IDENTITY_DIMENSIONS}).encode("utf-8")
    ).hexdigest()


def record_call_identity(conn: sqlite3.Connection, *, identity_id: str,
                         dossier_id: str, call_site: str, subject_ref: str,
                         dimensions: Mapping[str, object],
                         observed_at: str) -> None:
    """Remember that this identity was asked, and which dossier answered it.

    Appends no event: `database_agent.events` says registration "is a spec-level act
    (rule 4) ... There is no run-time registration call", so `model_call_reused` is a
    name the owner ratifies and the row carries the provenance until then.

    Writing the same (identity, dossier) twice is not a second row and not an error:
    two runs that reach the same dossier under the same identity have said the same
    thing.
    """
    with transaction(conn):
        stored = conn.execute(
            "SELECT dimensions FROM llm_call_identity "
            "WHERE identity_id = ? AND dossier_id = ?",
            (identity_id, dossier_id),
        ).fetchone()
        if stored is not None:
            return
        conn.execute(
            "INSERT INTO llm_call_identity ("
            "identity_id, dossier_id, call_site, subject_ref, dimensions, "
            "observed_at) VALUES (?, ?, ?, ?, ?, ?)",
            (identity_id, dossier_id, call_site, subject_ref,
             canonical_json(dict(dimensions)), observed_at),
        )


def prior_call(conn: sqlite3.Connection, identity_id: str) -> sqlite3.Row | None:
    """The most recent dossier asked under this identity, or `None`.

    Most recent by insertion and not by `observed_at`: a run under a frozen clock
    writes every row with one timestamp, and "the latest answer" has to survive that.
    """
    return conn.execute(
        "SELECT identity_id, dossier_id, call_site, subject_ref, dimensions, "
        "observed_at FROM llm_call_identity WHERE identity_id = ? "
        "ORDER BY rowid DESC LIMIT 1",
        (identity_id,),
    ).fetchone()


def answered_fields(conn: sqlite3.Connection, dossier_id: str) -> frozenset[str]:
    """Which fields the model ANSWERED under this dossier. `claim_ref` IS the field.

    **Every outcome, and `104` R-109 is why it is not only the abstentions.** This
    read used to be `outcome = 'abstain'`, on the reading that a declined field is
    the one a second run buys nothing by re-asking. A `reject` is the same purchase:
    the model answered, the validator refused the answer, no fact was written and the
    field is open again -- so the next run offers the identical question under the
    identical identity and pays for the identical rejection. Measured on the two-file
    corpus in `tests/integration/test_a_fact_reuse_after_a_verdict.py`: 2 calls, then
    2 more, `llm_call_reuse` empty. On the owner's own resumed run it was 120
    recorded responses consulted zero times and two hours of local calls spent twice.
    An `accept` needs no exclusion of its own -- it settles the field, so the field is
    not open on the next run and never reaches this comparison.

    **What is still never reused is decided before this function, not inside it.** A
    refusal, a call failure and a `ValidationUnavailable` write no verdict and record
    no identity; a pre-call abstention writes no `llm_verdict` row at all, so a
    dossier that holds one answers `frozenset()` here and the caller re-asks. Those
    are transient states -- a denied release, an exhausted budget, a provider that
    hung up -- and remembering one as an answer would turn it into a permanent
    silence about the file.

    Read from `llm_verdict` rather than copied onto the identity row, because a
    second copy of an answer is a second thing that can disagree with it. A
    superseded verdict is excluded: a re-judgement is a different answer and must not
    go on suppressing the ask.
    """
    return frozenset(
        row["claim_ref"] for row in conn.execute(
            "SELECT claim_ref FROM llm_verdict WHERE dossier_id = ? "
            "AND superseded_by IS NULL",
            (dossier_id,),
        )
    )


def record_call_reuse(conn: sqlite3.Connection, *, identity_id: str,
                      prior_dossier_id: str, call_site: str, subject_ref: str,
                      reused_fields, observed_at: str) -> str:
    """One row per question not asked because it already had an answer.

    A run that quietly makes fewer calls than the last one is indistinguishable from
    a run that silently dropped files. This is the difference, written down.
    """
    reuse_id = _new_id()
    with transaction(conn):
        conn.execute(
            "INSERT INTO llm_call_reuse ("
            "reuse_id, identity_id, prior_dossier_id, call_site, subject_ref, "
            "reused_fields, observed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (reuse_id, identity_id, prior_dossier_id, call_site, subject_ref,
             canonical_json(sorted(reused_fields)), observed_at),
        )
    return reuse_id


#: The observed half of a usage row, in insert order. The composition root
#: translates its transport's own shape into exactly these names -- `llm_harness`
#: may not import `readers`, so a provider's record cannot cross this line as a
#: type, and a mapping whose keys are checked is what crosses instead.
USAGE_COLUMNS: tuple[str, ...] = (
    "model_id", "prompt_tokens", "completion_tokens", "prompt_cache_hit_tokens",
    "prompt_cache_miss_tokens", "response_format",
)


def record_call_usage(conn: sqlite3.Connection, *, dossier_id: str, release_id: str,
                      reserved_cost: str, observed: Mapping[str, object] | None,
                      observed_at: str) -> str:
    """`104` R-14: what one call reserved, beside what the provider says it consumed.

    `00`:251 budgets "maximum model cost per scan" and `harness.run_call` settles
    every call against `CallDependencies.actual_cost`, a value the composition root
    fixes BEFORE the call. Nothing has ever recorded what a call actually consumed.
    This is that record, and it changes nothing the budget enforces: the unit stays
    calls, `settle_call` still settles one call as one, and the pair here is what
    makes the distance between the estimate and the truth readable.

    `observed` is the transport's own reading, translated by the composition root
    into this row's column names, or `None` when the provider reported nothing.
    A row is written EITHER WAY: a call was made and the budget spent for it, and a
    row of nulls says "asked, and it told us nothing" where no row is
    indistinguishable from a call that never happened.

    Deliberately NOT a price. Turning tokens into money needs a rate card, a rate
    card is a deployment fact, and this module invents no numbers -- the same rule
    that keeps the model id and the token ceiling injected. `cli.TOKEN_PRICES` is
    where one goes when the owner supplies it.

    Appends no event. `database_agent.events` closes `EVENT_TYPES` and calls
    registration "a spec-level act"; a `model_call_usage` name is the owner's.
    """
    fields = dict(observed or {})
    unexpected = set(fields) - set(USAGE_COLUMNS)
    if unexpected:
        raise MalformedRecord(
            f"a usage record carries {list(USAGE_COLUMNS)} and this one also "
            f"carries {sorted(unexpected)}. A column this table does not have is a "
            "number nobody can read back, and silently dropping it would lose the "
            "one thing the row exists to keep."
        )
    usage_id = _new_id()
    with transaction(conn):
        conn.execute(
            "INSERT INTO llm_call_usage ("
            "usage_id, dossier_id, release_id, model_id, prompt_tokens, "
            "completion_tokens, prompt_cache_hit_tokens, prompt_cache_miss_tokens, "
            "response_format, reserved_cost, observed_at"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (usage_id, dossier_id, release_id,
             *(fields.get(name) for name in USAGE_COLUMNS),
             reserved_cost, observed_at),
        )
    return usage_id
