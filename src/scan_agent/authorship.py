# src/scan_agent/authorship.py
"""P3 is the author of its scan events; P1 is only their writer (M8).

P1's SPEC: "The acting part authors; P1 writes. P1 appends no event on its own
initiative." P1's Contract in: "accept the `discovery`, `stat observation`,
`hashing` and `external modification detection` events P3 authors — P1 originates
none of them."

All four are reserved §8.2 names, already present in P1's frozen event-type table,
so P3 registers nothing (B5) and mints nothing at run time.
"""
from __future__ import annotations

from datetime import datetime, timezone

#: §8.2's "responsible subsystem" for every event this part appends.
SUBSYSTEM = "P3"

#: §8.2's "extractor or model version" field. P1's Done-means 7 requires it populated.
COMPONENT_VERSION = "P3/0.1.0"

#: The four reserved §8.2 types P3 authors, in the SPEC's order.
#: `external modification detection` has a second author, P12 (§8.3) — M8. The two
#: routes are independent and separable by `subsystem`.
AUTHORED_EVENT_TYPES: tuple[str, str, str, str] = (
    "discovery",
    "stat observation",
    "hashing",
    "external modification detection",
)


def event_defaults(**fields) -> dict:
    """Fill in §8.2's authorship fields and return the row for P1's `append_event`.

    This helper writes nothing and holds no connection: P3 authors, and the caller
    still has to decide that an event is due and hand it to P1.
    """
    event_type = fields.get("event_type")
    if event_type not in AUTHORED_EVENT_TYPES:
        raise ValueError(
            f"P3 does not author {event_type!r}; it authors {AUTHORED_EVENT_TYPES}"
        )
    if fields.get("subsystem", SUBSYSTEM) != SUBSYSTEM:
        raise ValueError(
            f"P3 events name P3 as the responsible subsystem, not "
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
