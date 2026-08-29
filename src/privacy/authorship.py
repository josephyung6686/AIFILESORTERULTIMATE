# src/privacy/authorship.py
"""P7 authors its events; P1 writes them (M8). The name "P7" is written here, once.

Two rules pull in opposite directions and both are enforced in this module.

**Registration is a SPEC-level act, so this package cannot perform one.** P7's eight
event types are already in P1's frozen `_REGISTERED` table, compiled from this SPEC
under the comment "P7 SPEC, Cross-cutting answers -> Provenance. Eight." There is no
run-time registration call anywhere in P1, and there is none here: the eight names
below are ASSERTED by this part's tests, never added. None collides with §8.2's
nineteen reserved names, and P1 checks that at import, so a collision is an
ImportError rather than a run-time rejection.

**Authorship is a run-time act, so this package performs it in exactly one place.**
M8: "The acting part authors; P1 writes. P1 appends no event on its own initiative."
`event_defaults` stamps `subsystem = SUBSYSTEM` and refuses a caller who supplies
one, because an author that is a parameter is not an author. Task 21 asserts there is
no second place under `src/privacy/` where that value is written.

This module opens no connection and appends nothing. `event_defaults` returns a plain
mapping for a caller to hand to `database_agent.events.append_event`, so there is no
code path in which importing P7 writes to the log.
"""
from __future__ import annotations

from datetime import datetime, timezone

from database_agent.events import (
    CORRECTION_FIELDS, EVENT_FIELDS, MalformedEvent, REGISTERED_EVENT_TYPES,
    UnregisteredEventType,
)

#: §8.2's "responsible subsystem", for every event this part authors. THE one place.
SUBSYSTEM: str = "P7"

#: §8.2's "extractor or model version" slot, for a part that is neither. P7's own
#: package version, and the default a caller may override for a replay (§8.5).
COMPONENT_VERSION: str = "0.1.0"

#: A classification was assigned to a (file_id, content_hash). D2 makes P7's record
#: authoritative, so this event is the record OF the record, not of a write to P6.
CLASSIFICATION_ASSIGNED: str = "classification_assigned"

#: A classification was superseded — including by a user reclassification (§8.4's
#: "revised by the user"). §8.2 forbids overwriting: both records remain inspectable.
CLASSIFICATION_SUPERSEDED: str = "classification_superseded"

#: A privacy/consent policy version was set. §8.8 puts "Privacy and model-consent
#: policies" inside the plan version, so a change must be diffable, which needs a row.
POLICY_SET: str = "policy_set"

#: Consent was granted for a scope. §8.4's four options are the user's, not P7's.
CONSENT_GRANTED: str = "consent_granted"

#: Consent was withdrawn. Forward-only: §8.4 requires the product to say what already
#: left the device, which is unsatisfiable once the send record is erasable.
CONSENT_REVOKED: str = "consent_revoked"

#: Content was released to a model. §8.4: "Every model call should be recorded in a
#: consent-aware audit record" — every, with no exemption for a local model.
MODEL_RELEASE: str = "model_release"

#: A release was refused. Appended on the strength of §8.2's "Every significant event
#: affecting a file" and §8.6's requirement that the UI show what was deferred and why.
MODEL_RELEASE_DENIED: str = "model_release_denied"

#: The gate asked the user. §8.4: "the user should see that requirement and choose".
CONSENT_REQUESTED: str = "consent_requested"

#: The eight, in the SPEC's own order (Cross-cutting answers -> Provenance).
P7_EVENT_TYPES: tuple[str, ...] = (
    CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, POLICY_SET,
    CONSENT_GRANTED, CONSENT_REVOKED, MODEL_RELEASE, MODEL_RELEASE_DENIED,
    CONSENT_REQUESTED,
)

#: What a caller may pass through: §8.2's eleven minus the three this module owns,
#: plus §8.7's five correction columns. `base_event_type` is P1-writable and is NOT
#: here: all eight of P7's names carry `base = None`, so a caller supplying one is
#: asserting a relationship the registration does not record.
_PASSTHROUGH: frozenset[str] = frozenset(
    set(EVENT_FIELDS) | set(CORRECTION_FIELDS)
) - {"event_type", "subsystem"}

#: The fields this module fills and a caller may not: authorship itself.
_AUTHORED: tuple[str, ...] = ("subsystem",)


def event_defaults(*, event_type: str, **fields) -> dict[str, object]:
    """§8.2's authorship fields for one P7 event, ready for P1's `append_event`.

    Writes nothing and takes no connection. Raises P1's own exceptions rather than
    inventing a third vocabulary for the same refusal: an unknown or authored field
    is `MalformedEvent`, an event type outside P7's eight is `UnregisteredEventType`.

    `explanation` is deliberately not defaulted. P1's writer requires it and rejects
    the empty string, so every P7 event carries a non-empty "structured explanation or
    evidence reference" (§8.2) by construction — and that column is where §8.4's
    consent-aware record lives, since `events` has no column for thirteen of its
    fields. A default here would let an event ship with placeholder prose in the one
    column the audit record needs.
    """
    if event_type not in P7_EVENT_TYPES:
        raise UnregisteredEventType(
            f"{event_type!r} is not one of P7's eight declared event types "
            f"{P7_EVENT_TYPES}. Registration is a spec-level act (P1 Contract out "
            "§3, rule 4): a new P7 event is a SPEC revision, and an event another "
            "part declared is that part's to author (M8)."
        )
    for name in _AUTHORED:
        if name in fields:
            raise MalformedEvent(
                f"{name} is authored by this module and is not a parameter. M8: "
                '"the acting part authors; P1 writes." An author a caller may set '
                "is not an author."
            )
    unknown = sorted(set(fields) - _PASSTHROUGH)
    if unknown:
        raise MalformedEvent(
            f"{unknown} are not among §8.2's eleven event fields (MINOR 1) or §8.7's "
            "five correction columns; P7 adds no column to `events` and does not ask "
            "P1 to. §8.4's audit fields with no column go into `explanation` as "
            "canonical JSON (B5)."
        )
    return {
        "event_type": event_type,
        "subsystem": SUBSYSTEM,
        "component_version": COMPONENT_VERSION,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
