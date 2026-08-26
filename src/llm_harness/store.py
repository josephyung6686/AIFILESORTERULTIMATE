# src/llm_harness/store.py
"""Append-only P8 writers. No overwrite, no upsert, no runtime event registration.

The writer→event matrix is closed. `model_call_issued` is Task 5 transport.
`record_call_failure` is a row only. `NeedsConsent` has no writer here.
"""
from __future__ import annotations

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
from llm_harness.records import GroundingReport, P8Verdict, PreCallAbstention, Refusal


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
    """Insert one dossier row. Appends no event."""
    conn.execute(
        "INSERT INTO llm_dossier ("
        "dossier_id, call_site, subject_ref, eligibility_reason, plan_version, "
        "policy_version, reduction_rung, release_id, payload, observed_at"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            dossier.dossier_id, dossier.call_site, dossier.subject_ref,
            dossier.eligibility_reason, dossier.plan_version, dossier.policy_version,
            dossier.reduction_rung, dossier.release_id, _payload(dossier), observed_at,
        ),
    )
    return dossier.dossier_id


def record_response(conn: sqlite3.Connection, *, dossier_id: str, response_bytes: bytes,
                    model_id: str, prompt_fingerprint: str, release_audit_id: int,
                    observed_at: str) -> str:
    """Store raw response bytes and append `model_response_received`."""
    response_bytes = _require_response_bytes(response_bytes)
    response_id = _new_id()
    with transaction(conn):
        conn.execute(
            "INSERT INTO llm_response ("
            "response_id, dossier_id, response_bytes, model_id, prompt_fingerprint, "
            "release_audit_id, observed_at"
            ") VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                response_id, dossier_id, response_bytes, model_id,
                prompt_fingerprint, release_audit_id, observed_at,
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
    with transaction(conn):
        conn.execute(
            "INSERT INTO llm_verdict ("
            "verdict_id, dossier_id, claim_ref, outcome, disposition, "
            "validator_version, policy_version, plan_version, payload, observed_at"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                verdict.verdict_id, verdict.dossier_id, verdict.claim_ref,
                verdict.outcome, verdict.disposition, verdict.validator_version,
                verdict.policy_version, verdict.plan_version, _payload(verdict),
                observed_at,
            ),
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


def record_call_failure(conn: sqlite3.Connection, *, dossier_id: str,
                        failure_class: str, explanation: str,
                        observed_at: str) -> str:
    """Terminal row on an already-issued call. Appends no event."""
    failure_id = _new_id()
    conn.execute(
        "INSERT INTO llm_call_failure ("
        "failure_id, dossier_id, failure_class, explanation, observed_at"
        ") VALUES (?, ?, ?, ?, ?)",
        (failure_id, dossier_id, failure_class, explanation, observed_at),
    )
    return failure_id
