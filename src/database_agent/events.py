"""Contract out §3 — the append-only provenance log (§8.2).

Append-only means INSERT only: no UPDATE, no DELETE, no row rewrite, no truncation,
no compaction that drops rows (R6). Enforced by trigger, not by convention.
"""
from __future__ import annotations

import sqlite3

#: §8.2's eleven event-record fields. Exactly eleven, forever (MINOR 1).
EVENT_FIELDS: tuple[str, ...] = (
    "event_type", "file_id", "content_hash", "old_path", "new_path",
    "subsystem", "component_version", "prompt_fingerprint", "user_id",
    "observed_at", "explanation",
)

#: §8.7 columns, carried beside the eleven on user-action events. P1 stores them
#: opaquely: it derives no polarity, compares no basis_key, interprets no
#: proposal_class. polarity ∈ accept | reject and is supplied by the acting part.
CORRECTION_FIELDS: tuple[str, ...] = (
    "correction_scope", "correction_subject", "polarity", "proposal_class", "basis_key",
)

_WRITABLE = (*EVENT_FIELDS, *CORRECTION_FIELDS, "base_event_type")


from types import MappingProxyType

#: §8.2's nineteen, verbatim. Reserved: no part may redefine, narrow, or reuse one.
RESERVED_EVENT_TYPES: frozenset[str] = frozenset({
    "discovery", "stat observation", "hashing", "extraction", "OCR",
    "fact creation", "fact rejection", "graph-edge creation",
    "group membership proposal", "user group decision", "template application",
    "destination-tree edit", "placement recommendation",
    "filename-collision resolution", "planned move", "executed move",
    "failed move", "external modification detection", "undo",
})

# Registration is a spec-level act (rule 4), so this table is compiled from the
# declaring SPECs and frozen at import. There is no run-time registration call.
# name -> base type when the name is a typed specialization of a reserved name.
_REGISTERED: dict[str, str | None] = {
    # P7 SPEC, Cross-cutting answers -> Provenance. Eight.
    "classification_assigned": None,
    "classification_superseded": None,
    "policy_set": None,
    "consent_granted": None,
    "consent_revoked": None,
    "model_release": None,
    "model_release_denied": None,
    "consent_requested": None,
    # P8 SPEC, section 8 "Events appended". Five.
    "model_call_issued": None,
    "model_response_received": None,
    "validation_verdict": None,
    "verdict_superseded": None,
    "call_refused": None,
    # P13 SPEC, Cross-cutting answers -> Provenance. Three.
    "review presentation": None,
    "review action routed": None,
    "apply review approval": None,
    # P11 SPEC, Cross-cutting answers -> Provenance. Nine typed specializations of
    # the reserved name `placement recommendation`. The base is a rollup for §8.2's
    # "current and historical placement proposals"; it is not a claim that building
    # an index entry is a recommendation. SPEC:689 is one bullet carrying two state
    # changes -- a set surfaced and a set decided -- and §7.6 gates model spend on
    # the second, so they are two names and the count is nine, not the eight the
    # bullet list reads as.
    "placement_index_entry_built": "placement recommendation",
    "candidate_destination_retrieval": "placement recommendation",
    "placement_recommendation_emitted": "placement recommendation",
    "group_plan_emitted": "placement recommendation",
    "residual_set_surfaced": "placement recommendation",
    "residual_set_decision_recorded": "placement recommendation",
    "residual_recommendation_emitted": "placement recommendation",
    "return_to_placement_issued": "placement recommendation",
    "placement_review_decision": "placement recommendation",
}

# Rule 1, checked once at import: a collision is an import error, not a run-time
# rejection, because there is no run time at which a name could be added.
_collisions = set(_REGISTERED) & RESERVED_EVENT_TYPES
if _collisions:
    raise ImportError(f"registered names shadow reserved 8.2 names: {sorted(_collisions)}")
_bad_bases = {b for b in _REGISTERED.values() if b is not None} - RESERVED_EVENT_TYPES
if _bad_bases:
    raise ImportError(f"specialization base is not a reserved name: {sorted(_bad_bases)}")

REGISTERED_EVENT_TYPES = MappingProxyType(_REGISTERED)
EVENT_TYPES = MappingProxyType(
    {name: None for name in RESERVED_EVENT_TYPES} | _REGISTERED
)


class UnregisteredEventType(Exception):
    """Rule 3: an unregistered type is rejected at the writer, never silently stored."""


class MalformedEvent(Exception):
    """Shape check at the writer. An append-only row cannot be repaired later."""


#: §8.7's six scopes, in §8.7's order, in the spelling `events.correction_scope`
#: and P13's `review_action.correction_scope` both use. Prose "destination node" is
#: the same scope as `node`, not a second value.
#:
#: DEFINED ONCE. `learning.SCOPES` is this tuple, imported — not a second copy.
#: The writer validates against it and the learning store reads against it, and a
#: scope one accepted that the other rejected would be storable and permanently
#: unreadable.
CORRECTION_SCOPES: tuple[str, ...] = (
    "file", "group", "node", "template", "domain", "corpus",
)

_REQUIRED = ("event_type", "subsystem", "component_version", "observed_at", "explanation")


def append_event(conn: sqlite3.Connection, **fields) -> int:
    """Append one event. Returns its monotonic event_id.

    `subsystem` is the authoring part (§8.2 "the responsible subsystem"). P1 never
    fills it in: the acting part authors, P1 writes (M8).
    """
    unknown = [k for k in fields if k not in _WRITABLE]
    if unknown:
        raise MalformedEvent(f"unrecognised event fields: {sorted(unknown)}")
    for name in _REQUIRED:
        value = fields.get(name)
        if value is None or value == "":
            raise MalformedEvent(f"{name} is required and cannot be empty")
    event_type = fields["event_type"]
    if event_type not in EVENT_TYPES:
        raise UnregisteredEventType(
            f"{event_type!r} is neither one of §8.2's nineteen reserved names nor "
            "declared by a part's SPEC; registration is a spec-level act (rule 4)"
        )
    scope = fields.get("correction_scope")
    if scope is not None:
        if scope not in CORRECTION_SCOPES:
            raise MalformedEvent(
                f"correction_scope {scope!r} is not one of {tuple(sorted(CORRECTION_SCOPES))}"
            )
        if not fields.get("correction_subject"):
            raise MalformedEvent("correction_scope requires correction_subject")
    base = EVENT_TYPES[event_type]
    if base is not None:
        fields.setdefault("base_event_type", base)
    columns = list(fields)
    values = [fields[k] for k in columns]
    cursor = conn.execute(
        f"INSERT INTO events ({','.join(columns)}) VALUES ({','.join('?' * len(columns))})",
        values,
    )
    return cursor.lastrowid
