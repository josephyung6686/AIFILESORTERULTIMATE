# src/facts/authorship.py
"""P6 authors its two §8.2 events; P1 writes them (M8).

M8 (04-resolutions.md): "The acting part authors; P1 writes. P1 appends no event on
its own initiative." §8.2 requires "the responsible subsystem" on every event, and a
`fact creation` row whose subsystem named P1 or P8 would record that the storage
substrate, or the model harness, wrote the fact table.

Both names are already among §8.2's nineteen reserved types (introspected from
`database_agent.events.RESERVED_EVENT_TYPES`, 2026-08-22), so P6 registers nothing —
registration is a spec-level act (P1 Contract out §3, rule 4).

**Both names carry a space.** `fact_creation` raises `UnregisteredEventType` at run
time rather than at review. This is the same defect class as MINOR 2's `OCR`/`ocr`.

This module is the ONE place `subsystem = "P6"` is written (Task 25 asserts there is
no second). It holds no connection and writes nothing.
"""
from __future__ import annotations

from datetime import datetime, timezone

#: §8.2's "responsible subsystem" for every event this part appends.
SUBSYSTEM = "P6"

#: §8.2's "extractor or model version" field. P1's Done-means 7 requires it
#: populated and `append_event` rejects an empty one. P3's spelling, followed.
COMPONENT_VERSION = "P6/0.1.0"

#: The two reserved §8.2 types P6 authors, in §8.2's order. Spelled with a space,
#: because that is how §8.2 spells them and how P1's frozen table stores them.
AUTHORED_EVENT_TYPES: tuple[str, str] = ("fact creation", "fact rejection")


def event_defaults(**fields) -> dict:
    """Fill §8.2's authorship fields and return the row for P1's `append_event`.

    Writes nothing and holds no connection: P6 authors, and the caller still has to
    decide an event is due and hand it to P1. A caller-supplied `observed_at` wins,
    so §8.5's replay can pin the clock.
    """
    event_type = fields.get("event_type")
    if event_type not in AUTHORED_EVENT_TYPES:
        raise ValueError(
            f"P6 does not author {event_type!r}; it authors {AUTHORED_EVENT_TYPES}. "
            f"Note the space: `fact_creation` is not a registered §8.2 type."
        )
    if fields.get("subsystem", SUBSYSTEM) != SUBSYSTEM:
        raise ValueError(
            f"P6 events name P6 as the responsible subsystem, not "
            f"{fields['subsystem']!r} (M8)"
        )
    return {
        **fields,
        "subsystem": SUBSYSTEM,
        "component_version": COMPONENT_VERSION,
        "observed_at": fields.get(
            "observed_at", datetime.now(timezone.utc).isoformat()
        ),
    }
