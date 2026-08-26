# src/llm_harness/transport.py
"""The only model egress. A call is not constructible without a live P7 `Released`.

`issue` recomputes the payload from immutable sources, consumes the release, then
invokes the injected client. The client receives model-visible bytes only.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from database_agent.db import transaction
from database_agent.events import append_event
from evidence_shape.canonical import canonical_json

from llm_harness.authorship import (
    COMPONENT_VERSION,
    MODEL_CALL_ISSUED,
    event_defaults,
)
from llm_harness.fingerprint import prompt_fingerprint
from llm_harness.records import (
    CallFailed,
    CallPayload,
    MalformedRecord,
    assemble,
)
from llm_harness.store import record_call_failure, record_response
from privacy.binding import BindingMismatch, consume_release
from privacy.release import ModelTarget, Released


class TransportTransactionOpen(Exception):
    """issue refuses to join an already-open transaction."""


@dataclass(frozen=True, slots=True)
class ModelClient:
    """Target-bound capability. Callers cannot supply a second destination to invoke."""

    model_target: ModelTarget
    invoke: Callable[[bytes], bytes]


@dataclass(frozen=True, slots=True)
class ModelResponse:
    """Raw transport bytes plus the identities later validation needs."""

    response_bytes: bytes
    model_id: str
    prompt_fingerprint: str
    release_audit_id: int
    response_id: str
    release_id: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _explanation(*, audit_id: int | None, model_id: str | None,
                 prompt_fingerprint: str | None, **extra: object) -> str:
    return canonical_json({
        "audit_id": audit_id,
        "model_id": model_id,
        "prompt_fingerprint": prompt_fingerprint,
        **extra,
    })


def _require_sources(payload: CallPayload) -> str:
    recomputed = prompt_fingerprint(payload.prompt_definition)
    reassembled = assemble(
        payload.prompt_definition, payload.canonical_dossier_bytes,
    )
    if recomputed != payload.prompt_fingerprint or reassembled != payload.model_visible_bytes:
        raise MalformedRecord(
            "CallPayload sources do not recompute to the stored fingerprint "
            "and model-visible bytes; transport never invents or mutates them"
        )
    return recomputed


def _require_binding(released: Released, payload: CallPayload,
                     model_client: ModelClient) -> None:
    if not (
        model_client.model_target == payload.model_target == released.model_target
    ):
        raise BindingMismatch(
            "model_client.model_target, payload.model_target, and "
            "released.model_target must be the same ModelTarget; a mismatched "
            "destination would make §8.4's 'which model received the data' false"
        )
    if payload.release_id != released.release_id:
        raise MalformedRecord(
            "payload.release_id must be the Released capability being spent"
        )
    if payload.policy_version != released.policy_version:
        raise BindingMismatch(
            "payload.policy_version must echo released.policy_version; "
            "policy_version is a binding term"
        )


def _record_issued(conn: sqlite3.Connection, *, released: Released,
                   payload: CallPayload, fingerprint: str,
                   observed_at: str) -> None:
    fields = event_defaults(
        event_type=MODEL_CALL_ISSUED,
        observed_at=observed_at,
        prompt_fingerprint=fingerprint,
        explanation=_explanation(
            audit_id=released.audit_id,
            model_id=payload.model_target.model_id,
            prompt_fingerprint=fingerprint,
            release_id=released.release_id,
        ),
    )
    append_event(conn, **fields)


def _failed(released: Released, payload: CallPayload, *,
            explanation: str) -> CallFailed:
    """The identity is the dossier's address, not the capability that paid.

    `report_for_call_failure` writes `request_identity` into
    `llm_grounding_report.dossier_id`, so a `release_id` there produced a report
    that joined to neither the dossier it describes nor the failure row.
    """
    return CallFailed(
        request_identity=payload.dossier_id,
        release_id=released.release_id,
        audit_id=released.audit_id,
        explanation=explanation,
        validator_version=COMPONENT_VERSION,
        policy_version=payload.policy_version,
    )


def _reject_open_transaction(conn: sqlite3.Connection) -> None:
    if conn.in_transaction:
        raise TransportTransactionOpen(
            "issue rejects an already-open transaction so a rollback cannot "
            "unspend a release after model-visible bytes have left"
        )


def _client_exception_explanation(exc: BaseException) -> str:
    return str(exc) or type(exc).__name__


def issue(conn: sqlite3.Connection, released: Released, payload: CallPayload, *,
          model_client: ModelClient) -> ModelResponse | CallFailed:
    """Consume one live release, then invoke the bound client once.

    Binding and payload integrity are checked before the ledger spend. The client
    is invoked only after `consume_release` returns, and it receives only
    `payload.model_visible_bytes`.
    """
    _reject_open_transaction(conn)
    fingerprint = _require_sources(payload)
    _require_binding(released, payload, model_client)
    issued_at = _now()
    with transaction(conn):
        consume_release(
            conn, released,
            model_target=model_client.model_target,
            prompt_fingerprint=fingerprint,
            policy_version=payload.policy_version,
        )
        _record_issued(
            conn, released=released, payload=payload, fingerprint=fingerprint,
            observed_at=issued_at,
        )
    try:
        raw = model_client.invoke(payload.model_visible_bytes)
    except Exception as exc:
        explanation = _client_exception_explanation(exc)
        record_call_failure(
            conn, dossier_id=payload.dossier_id, failure_class="client_raised",
            explanation=explanation, release_id=payload.release_id,
            observed_at=_now(),
        )
        return _failed(released, payload, explanation=explanation)
    if not isinstance(raw, (bytes, bytearray, memoryview)):
        explanation = (
            f"client returned {type(raw).__name__}; transport bytes must be bytes"
        )
        record_call_failure(
            conn, dossier_id=payload.dossier_id, failure_class="malformed_bytes",
            explanation=explanation, release_id=payload.release_id,
            observed_at=_now(),
        )
        return _failed(released, payload, explanation=explanation)
    response_bytes = bytes(raw)
    response_id = record_response(
        conn,
        dossier_id=payload.dossier_id,
        response_bytes=response_bytes,
        model_id=payload.model_target.model_id,
        prompt_fingerprint=fingerprint,
        release_audit_id=released.audit_id,
        release_id=released.release_id,
        observed_at=_now(),
    )
    return ModelResponse(
        response_bytes=response_bytes,
        model_id=payload.model_target.model_id,
        prompt_fingerprint=fingerprint,
        release_audit_id=released.audit_id,
        release_id=released.release_id,
        response_id=response_id,
    )
