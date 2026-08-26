# src/llm_harness/stage_output.py
"""Map a P8 result onto P2's llm_interpretation envelope.

P2 owns the envelope vocabulary. This module translates P8 outcomes onto
`produced` / `abstained` / `deferred` / `error` and never writes P8's own
`abstain` into the envelope. `NeedsConsent` is not a P8 measurement and
creates no row.

The version tuple is live P2 `VERSION_TUPLE_FIELDS`. P8 supplies fingerprint
and model identifier; every other axis is caller-authored. `validator_version`
and `policy_version` stay in the opaque payload (and on P8 verdict/report
rows), not in that tuple.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import fields, is_dataclass

from eval_harness.run import VERSION_TUPLE_FIELDS, record_version_tuple
from eval_harness.stage_output import record_stage_output
from evidence_shape.canonical import canonical_json

from llm_harness.records import CallFailed, Dossier, P8Verdict, Refusal
from llm_harness.sites import dispatch
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    BUDGET_EXHAUSTED,
    REJECT,
    WEAK,
)
from privacy.release import NeedsConsent

_QUALITY_OUTCOMES = frozenset({
    ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED, WEAK, REJECT,
})
_STALE_TUPLE_KEYS = frozenset({"model_id", "validator_version", "policy_version"})


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


def record_p8_version_tuple(conn: sqlite3.Connection, **axes) -> str:
    """Store the seven-field live P2 tuple. No P8 defaults for unused axes.

    Extra keys (including `validator_version` / `policy_version` / `model_id`)
    and the stale four-field SPEC tuple are refused. An intentionally empty
    caller axis must still be passed.
    """
    extra = set(axes) - set(VERSION_TUPLE_FIELDS)
    missing = set(VERSION_TUPLE_FIELDS) - set(axes)
    if extra or missing:
        raise ValueError(
            "version tuple fields: missing "
            f"{sorted(missing)}, unexpected {sorted(extra)}; "
            f"live VERSION_TUPLE_FIELDS are {VERSION_TUPLE_FIELDS}; "
            f"stale keys {_STALE_TUPLE_KEYS} belong in the opaque P8 payload"
        )
    return record_version_tuple(conn, **{name: axes[name] for name in VERSION_TUPLE_FIELDS})


def _envelope(result: object) -> tuple[str, str]:
    if isinstance(result, NeedsConsent):
        raise TypeError("NeedsConsent writes no P2 row")
    if isinstance(result, CallFailed):
        return "error", "within_ceiling"
    if isinstance(result, Refusal):
        return "abstained", "within_ceiling"
    if isinstance(result, P8Verdict):
        if result.outcome in _QUALITY_OUTCOMES:
            return "produced", "within_ceiling"
        if result.outcome == ABSTAIN:
            if BUDGET_EXHAUSTED in result.reasons:
                return "deferred", "ceiling_reached"
            return "abstained", "within_ceiling"
        raise ValueError(f"unmapped P8 outcome {result.outcome!r}")
    raise TypeError(
        "emit_stage_output accepts P8Verdict, Refusal, or CallFailed; "
        f"got {type(result).__name__}"
    )


def emit_stage_output(
    conn: sqlite3.Connection, *, run_id: str, subject_ref: str,
    result: P8Verdict | Refusal | CallFailed,
    inputs: tuple[str, ...], version_tuple_ref: str,
) -> int:
    """Write one `llm_interpretation` envelope. `produced_at` is stamped by P2."""
    outcome, budget_state = _envelope(result)
    manifest = conn.execute(
        "SELECT rm.version_tuple_ref AS manifest_version_tuple_ref, "
        "vt.version_tuple_ref AS existing_version_tuple_ref "
        "FROM run_manifest AS rm "
        "LEFT JOIN version_tuple AS vt "
        "ON vt.version_tuple_ref = rm.version_tuple_ref "
        "WHERE rm.run_id = ?",
        (run_id,),
    ).fetchone()
    if manifest is None:
        raise KeyError(f"run_id {run_id!r} does not identify an existing run_manifest")
    manifest_ref = manifest["manifest_version_tuple_ref"]
    if manifest["existing_version_tuple_ref"] is None:
        raise KeyError(
            f"run_manifest {run_id!r} references missing version_tuple {manifest_ref!r}"
        )
    if version_tuple_ref != manifest_ref:
        raise ValueError(
            f"version_tuple_ref {version_tuple_ref!r} does not match run_manifest "
            f"{run_id!r} version_tuple_ref {manifest_ref!r}"
        )
    return record_stage_output(
        conn,
        run_id=run_id,
        stage_id="llm_interpretation",
        subject_ref=subject_ref,
        outcome=outcome,
        payload=canonical_json(_jsonable(result)),
        version_tuple_ref=version_tuple_ref,
        inputs=inputs,
        budget_state=budget_state,
    )


def replay_recorded_response(
    conn: sqlite3.Connection,
    dossier: Dossier,
    *,
    evidence_resolver,
    site_dependencies,
    contradicts,
    dossier_builder: str,
    policy_version: str,
):
    """Re-validate stored response bytes against the current evidence snapshot.

    Loads `llm_response.response_bytes`. Does not call a model client. Does not
    return a previously stored verdict.
    """
    row = conn.execute(
        "SELECT response_bytes, model_id, prompt_fingerprint, release_audit_id "
        "FROM llm_response WHERE dossier_id = ? "
        "ORDER BY observed_at DESC, response_id DESC",
        (dossier.dossier_id,),
    ).fetchone()
    if row is None:
        raise KeyError(f"no stored response for dossier {dossier.dossier_id!r}")
    return dispatch(
        conn,
        dossier,
        bytes(row["response_bytes"]),
        site_dependencies=site_dependencies,
        evidence_resolver=evidence_resolver,
        contradicts=contradicts,
        model_id=row["model_id"],
        prompt_fingerprint=row["prompt_fingerprint"],
        dossier_builder=dossier_builder,
        release_audit_id=row["release_audit_id"],
        policy_version=policy_version,
    )
