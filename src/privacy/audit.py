# src/privacy/audit.py
"""§8.4's consent-aware audit record, as ONE `events` row plus canonical JSON.

§8.4: "Every model call should be recorded in a consent-aware audit record. The record
should show what policy authorized the call, whether the file was sensitive, which
excerpts were included, whether values were redacted, which model received the data,
and the prompt fingerprint."

Three constraints meet here and are jointly satisfiable exactly one way. P1's
`append_event` accepts seventeen named columns and rejects an eighteenth; MINOR 1 fixes
§8.2's list at eleven forever; B5 settles that there is ONE log -- "§8.4's consent-aware
record is that log with the consent fields". So five fields land in their columns and
the other sixteen land in `explanation`, which is §8.2's own "structured explanation or
evidence reference" slot. P7 adds no column to `events` and does not ask P1 to.

Two properties this module exists to make structural rather than procedural:

- **`audit_id` cannot exist before the record does.** It IS the `event_id` P1 returns
  from a completed insert, so SPEC §6's "the audit record is appended ... before
  `Released` is returned" is not a discipline anyone can forget.
- **The record says what left the device without holding a copy of it.**
  `excerpts_included` is `(observation_key, span)` pairs, where `span` is P4's canonical
  locator; re-running `resolve.materialise` over them reproduces the payload exactly.
  §8.4 puts "raw sensitive values" in the always-local set, and the text already exists
  once.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from database_agent.events import EVENT_FIELDS, append_event
from evidence_shape.canonical import canonical_json

from privacy.authorship import (
    CONSENT_REQUESTED, MODEL_RELEASE, MODEL_RELEASE_DENIED, SUBSYSTEM, event_defaults,
)
from privacy.vocabulary import AUDIT_OUTCOMES

#: SPEC §7's nineteen, in §7's order: §8.4's six required, §7's carried block, then
#: §8.2's two per-file columns. `appended_at` is spelled `observed_at` because §7
#: annotates it '§8.2 "time of observation"' and that is P1's column; one thing has
#: one name.
AUDIT_FIELDS: tuple[str, ...] = (
    "authorizing_policy", "file_sensitivity", "excerpts_included",
    "redaction_applied", "model", "prompt_fingerprint",
    "audit_id", "release_id", "observed_at", "stage", "file_ids", "group_id",
    "content_hashes", "operation_mode", "policy_version", "plan_version", "outcome",
    "file_id", "content_hash",
)

#: Three names SPEC §7 does not list as fields, kept outside the nineteen so
#: `AUDIT_FIELDS == §7` stays a testable identity. Each is reported in the plan.
CARRIED_FIELDS: tuple[str, str, str] = (
    "user_id", "consent_request_id", "redaction_manifest",
)

#: The five with an `events` column. Everything else has none.
COLUMN_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "prompt_fingerprint", "observed_at", "user_id",
)

#: The sixteen that travel as canonical JSON. `audit_id` is in neither list: it is the
#: row's identity, assigned by the insert and read back off `event_id`.
EXPLANATION_FIELDS: tuple[str, ...] = tuple(
    name for name in AUDIT_FIELDS + CARRIED_FIELDS
    if name not in COLUMN_FIELDS and name != "audit_id"
)

#: outcome -> the P7 event type that records it. `model_release` and its consent-aware
#: record are the same event (B5).
OUTCOME_EVENT_TYPES: Mapping[str, str] = MappingProxyType({
    "released": MODEL_RELEASE,
    "denied": MODEL_RELEASE_DENIED,
    "consent_requested": CONSENT_REQUESTED,
})

_TUPLE_FIELDS = ("excerpts_included", "file_ids", "content_hashes",
                 "redaction_manifest")
_PAIR_FIELDS = ("excerpts_included",)


class MalformedAudit(Exception):
    """Shape check at the writer. An append-only row cannot be repaired later."""


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """SPEC §7's nineteen, plus three carried names §7 does not list as fields."""

    authorizing_policy: str
    file_sensitivity: str
    excerpts_included: tuple[tuple[str, str], ...]
    redaction_applied: bool
    model: Mapping[str, str]
    prompt_fingerprint: str
    audit_id: int | None
    release_id: str | None
    observed_at: str
    stage: str
    file_ids: tuple[str, ...]
    group_id: str | None
    content_hashes: tuple[str, ...]
    operation_mode: str
    policy_version: str
    plan_version: str
    outcome: str
    file_id: str | None
    content_hash: str | None
    user_id: str | None = None
    consent_request_id: str | None = None
    redaction_manifest: tuple[Mapping[str, object], ...] = ()


def _check(record: AuditRecord, author: str) -> None:
    if author != SUBSYSTEM:
        raise MalformedAudit(
            f"author {author!r} is not {SUBSYSTEM!r}. M8 gives authorship to the "
            "acting part, and `privacy` writes its subsystem name in one place")
    if record.outcome not in AUDIT_OUTCOMES:
        raise MalformedAudit(
            f"outcome {record.outcome!r} is not one of {AUDIT_OUTCOMES}; a value "
            "outside a closed vocabulary is a load error, not a fallback")
    for name in ("stage", "authorizing_policy", "operation_mode", "policy_version",
                 "plan_version", "file_sensitivity", "prompt_fingerprint",
                 "observed_at"):
        if not getattr(record, name):
            raise MalformedAudit(
                f"{name} is required on every audit record; §8.5 decomposes replay "
                "by stage and §8.8 reproduces the policy in force at each call, and "
                "neither is possible from a record that omitted one")
    if not record.model:
        raise MalformedAudit(
            "§8.4 requires the record show which model received the data")


def append_audit(conn: sqlite3.Connection, record: AuditRecord, *, author: str,
                 component_version: str,
                 extra: Mapping[str, object] | None = None) -> int:
    """Append one audit record and return its `audit_id`.

    The id is P1's `event_id`, produced by the insert, so it cannot be handed to a
    caller before the row exists. That is SPEC §6's ordering guarantee, structurally.

    `extra` merges into the same `explanation` object. SPEC §7 enumerates a RELEASE
    record; a denial's reason and a consent request's four options have no field in
    it, and §8.6 requires the product show "what has been deferred, and why". A key
    that collides with one of the sixteen is refused, so the nineteen stay the
    nineteen.
    """
    _check(record, author)
    payload = {name: _jsonable(getattr(record, name)) for name in EXPLANATION_FIELDS}
    if extra:
        collisions = sorted(set(extra) & set(payload))
        if collisions:
            raise MalformedAudit(
                f"{collisions} are SPEC §7 field names; `extra` carries what §7 has "
                "no field for, and a second value under one name is how a record "
                "starts disagreeing with itself")
        payload.update({name: _jsonable(value) for name, value in extra.items()})
    explanation = canonical_json(payload)
    columns = {name: getattr(record, name) for name in COLUMN_FIELDS}
    return append_event(conn, **event_defaults(
        event_type=OUTCOME_EVENT_TYPES[record.outcome],
        component_version=component_version, explanation=explanation, **columns))


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, Mapping):
        return dict(value)
    return value


def _record_from_row(row: sqlite3.Row) -> AuditRecord:
    import json

    payload = json.loads(row["explanation"])
    values: dict[str, object] = {name: payload[name] for name in EXPLANATION_FIELDS}
    values.update({name: row[name] for name in COLUMN_FIELDS})
    values["audit_id"] = row["event_id"]
    values["redaction_applied"] = bool(values["redaction_applied"])
    for name in _TUPLE_FIELDS:
        values[name] = tuple(
            tuple(item) if name in _PAIR_FIELDS else item
            for item in values[name])
    return AuditRecord(**values)


def audit_record(conn: sqlite3.Connection, audit_id: int) -> AuditRecord:
    """One record, by the id `append_audit` returned."""
    row = conn.execute("SELECT * FROM events WHERE event_id = ? AND event_type IN "
                       "(?, ?, ?)",
                       (audit_id, MODEL_RELEASE, MODEL_RELEASE_DENIED,
                        CONSENT_REQUESTED)).fetchone()
    if row is None:
        raise KeyError(f"no audit record {audit_id!r}")
    return _record_from_row(row)


def audit_extra(conn: sqlite3.Connection, audit_id: int) -> dict[str, object]:
    """The keys `append_audit`'s `extra` added, beside SPEC §7's sixteen."""
    import json

    row = conn.execute("SELECT explanation FROM events WHERE event_id = ?",
                       (audit_id,)).fetchone()
    if row is None:
        raise KeyError(f"no audit record {audit_id!r}")
    return {name: value for name, value in json.loads(row["explanation"]).items()
            if name not in EXPLANATION_FIELDS}


def audit_records_for(conn: sqlite3.Connection, *, file_id: str | None = None,
                      release_id: str | None = None,
                      consent_request_id: str | None = None) -> list[AuditRecord]:
    """Audit records matching every filter given, in append order.

    At least one filter is required. A reader that returned the whole log for a call
    that named nothing is how "the releases for this file" becomes "every release".
    """
    clauses = ["event_type IN (?, ?, ?)"]
    parameters: list[object] = [MODEL_RELEASE, MODEL_RELEASE_DENIED, CONSENT_REQUESTED]
    if file_id is not None:
        # Column match covers a single-file release. A group release writes
        # NULL into that column and puts the ids in explanation.file_ids
        # (§8.4 prior_releases must list every release that carried this
        # file's excerpts). json_each is the match; a second reader in
        # revoke() would be a second home.
        clauses.append(
            "(file_id = ? OR EXISTS ("
            "SELECT 1 FROM json_each(explanation, '$.file_ids') "
            "WHERE value = ?))"
        )
        parameters.extend([file_id, file_id])
    for name, value in (("release_id", release_id),
                        ("consent_request_id", consent_request_id)):
        if value is not None:
            clauses.append(f"json_extract(explanation, '$.{name}') = ?")
            parameters.append(value)
    if len(clauses) == 1:
        raise MalformedAudit(
            "audit_records_for needs at least one of file_id, release_id or "
            "consent_request_id")
    rows = conn.execute(
        f"SELECT * FROM events WHERE {' AND '.join(clauses)} ORDER BY event_id",
        parameters)
    return [_record_from_row(row) for row in rows]
