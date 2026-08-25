# src/llm_harness/authorship.py
"""P8 authors its store events; P1 writes them (M8). The name "P8" is written here, once.

Registration is a spec-level act. P1 already compiled the five P8 event types into
`_REGISTERED`. This module asserts authorship of the four store-owned names and does
not register anything. `model_call_issued` is authored by transport in Task 5.

`event_defaults` stamps `subsystem = SUBSYSTEM` and writes nothing.
"""
from __future__ import annotations

from datetime import datetime, timezone

from database_agent.events import (
    CORRECTION_FIELDS,
    EVENT_FIELDS,
    MalformedEvent,
    UnregisteredEventType,
)

#: §8.2's "responsible subsystem" for every event this part authors. THE one place.
SUBSYSTEM: str = "P8"

#: §8.2's "extractor or model version" slot for the harness itself.
COMPONENT_VERSION: str = "P8/0.1.0"

MODEL_RESPONSE_RECEIVED: str = "model_response_received"
VALIDATION_VERDICT: str = "validation_verdict"
VERDICT_SUPERSEDED: str = "verdict_superseded"
CALL_REFUSED: str = "call_refused"

#: Store-owned names. Transport's `model_call_issued` is absent until Task 5.
AUTHORED_EVENT_TYPES: tuple[str, ...] = (
    MODEL_RESPONSE_RECEIVED,
    VALIDATION_VERDICT,
    VERDICT_SUPERSEDED,
    CALL_REFUSED,
)

_PASSTHROUGH: frozenset[str] = frozenset(
    set(EVENT_FIELDS) | set(CORRECTION_FIELDS)
) - {"event_type", "subsystem"}


def event_defaults(*, event_type: str, **fields) -> dict[str, object]:
    """Authorship fields for one P8 event, ready for P1's `append_event`.

    Writes nothing and takes no connection. `explanation` is not defaulted: P1
    requires a non-empty structured explanation.
    """
    if event_type not in AUTHORED_EVENT_TYPES:
        raise UnregisteredEventType(
            f"{event_type!r} is not one of P8's store-authored event types "
            f"{AUTHORED_EVENT_TYPES}. model_call_issued is Task 5 transport."
        )
    if "subsystem" in fields:
        raise MalformedEvent(
            "subsystem is authored by this module and is not a parameter. M8: "
            '"the acting part authors; P1 writes."'
        )
    unknown = sorted(set(fields) - _PASSTHROUGH)
    if unknown:
        raise MalformedEvent(
            f"{unknown} are not among §8.2's event fields; P8 adds no column to "
            "`events`. audit_id / model_id context goes in `explanation` as "
            "canonical JSON."
        )
    return {
        "event_type": event_type,
        "subsystem": SUBSYSTEM,
        "component_version": COMPONENT_VERSION,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
