# src/llm_harness/transport.py
"""The only model egress. A call is not constructible without a live P7 `Released`.

`issue` recomputes the payload from immutable sources, consumes the release, then
invokes the injected client. The client receives model-visible bytes only.

**The bytes are bound to the release, and were not until 2026-09-02.** The security
review's CR-02 spent a real release -- one materialised item, `"[redacted]"` -- on a
payload whose dossier bytes were a dump of every `raw_value`, every `context_before`,
every path and every content hash, and this function returned a `ModelResponse`. The
three checks that ran were all self-consistency: `_require_sources` recomputes the
fingerprint and reassembles the payload's own two fields, and `CallPayload.
__post_init__` does the same. `_require_binding` and `consume_release` bound WHO
received the bytes and UNDER WHAT POLICY. Nothing bound WHAT.

`released_content.released_content_digest` now folds the payload's own bytes into
P7's fourth binding term and `consume_release` compares it with the ledger row the
gate wrote. See that module for the three checks and for what they do NOT cover.
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
from llm_harness.released_content import released_content_digest
from llm_harness.store import record_call_failure, record_response
from privacy.binding import BindingMismatch, consume_release
from privacy.release import ModelTarget, Released


#: P7's Done-means 3 is a static property OF THE TRANSPORT, and this flag is how the
#: instrument finds it: `tests/p7/test_p7_skeleton_step.py` scans `src/` for
#: `IS_MODEL_TRANSPORT is True` and runs `privacy.transport_guard.assert_single_egress`
#: over every module that sets it. This module is the one writer of `True`. Unset, the
#: scan returned an empty list and the check that §8.4 turns on asserted against
#: nothing.
IS_MODEL_TRANSPORT: bool = True


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
    """The identities. WHAT the bytes are is the fourth term, checked in the spend.

    Kept here rather than folded into this function on purpose: a binding term is
    the ledger's, and comparing content here against the `Released` in the caller's
    hand would be comparing a `dataclasses.replace`d forgery with itself.
    """
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
    """A THIRD-PARTY exception, reduced to the two things anything here reads.

    This returned `str(exc)`, and the `try` around the client call is `except
    Exception` -- as wide as it gets. Whatever an SDK chooses to put in a message
    went from there into a durable `llm_call_failure` row and into a user-visible
    `CallFailed`, which `records.py` says `emit_stage_output` serialises "verbatim
    into P2's `error` row". A request echo, a URL with a query parameter, a header
    dump: §8.4 requires that record to be consent-aware, and nothing was checking
    what a library put in it.

    §8.4's property 4 -- no credential reaches the screen, a log, an audit record or
    an exception message -- was the one a security review could not clear, because
    there is no way to enumerate every string an SDK may produce. This removes the
    channel instead of arguing about it: the type and an HTTP status are what the
    failure taxonomy actually reads, and neither can carry a secret.

    No developer flag for the full text, deliberately. Nothing in `src/` read the
    free string -- `store.record_call_failure` writes it and no code path branches on
    it -- so a flag would be a second, dimmer copy of this channel maintained for a
    reader who does not exist. Add one when somebody needs it, and put the reason at
    the flag.
    """
    return canonical_json({
        "type": type(exc).__qualname__,
        "status": getattr(exc, "status_code", None),
    })


def issue(conn: sqlite3.Connection, released: Released, payload: CallPayload, *,
          model_client: ModelClient) -> ModelResponse | CallFailed:
    """Consume one live release, then invoke the bound client once.

    Binding, payload integrity and the released CONTENT are all checked before the
    ledger spend. The client is invoked only after `consume_release` returns, and it
    receives only `payload.model_visible_bytes` -- whose dossier half has been shown
    to carry exactly what the gate released, in exactly the shape the builder writes.
    """
    _reject_open_transaction(conn)
    fingerprint = _require_sources(payload)
    _require_binding(released, payload, model_client)
    # Folded from the bytes about to be sent, and compared against the gate's ledger
    # row inside `consume_release` -- before the spend, before the socket.
    content = released_content_digest(
        payload.canonical_dossier_bytes,
        prompt_definition=payload.prompt_definition,
        policy_version=payload.policy_version,
    )
    issued_at = _now()
    with transaction(conn):
        consume_release(
            conn, released,
            model_target=model_client.model_target,
            prompt_fingerprint=fingerprint,
            policy_version=payload.policy_version,
            content_digest=content,
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
