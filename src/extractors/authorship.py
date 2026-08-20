# src/extractors/authorship.py
"""P5 is the author of its own events; P1 writes them (M8).

§8.2: "the responsible subsystem". P1 appends no event on its own initiative, so
the value that lands in `subsystem` is set HERE and in no other module.

P5 authors two of §8.2's nineteen reserved types and registers nothing:

    `extraction`  once per file per extractor family per content version
    `OCR`         once per OCR run

`OCR` is spelled the way §8.2 spells it (MINOR 2). P1's writer validates the type
against §8.2's frozen vocabulary, so the lowercase spelling earlier drafts used is
not a style issue: it raises UnregisteredEventType at the INSERT.
"""
from __future__ import annotations

from datetime import datetime, timezone

#: M8. There is one value and no default anywhere in `extractors`.
SUBSYSTEM = "P5"

#: §8.2's "extractor version" on the event row. Per-extractor versions live on the
#: extractor modules; this is the version of P5's own event authorship.
COMPONENT_VERSION = "0.1.0"

#: §8.2's own names, spelled as §8.2 spells them (MINOR 2). Both are reserved, so
#: P5 registers nothing (B5, rule 4: registration is a spec-level act).
AUTHORED_EVENT_TYPES: tuple[str, str] = ("extraction", "OCR")


def event_defaults(**fields) -> dict:
    """Fill §8.2's authorship fields and return a plain dict for P1's append_event.

    Writes nothing and opens nothing: there is no code path where P5 appends an
    event without a caller having decided to.
    """
    event_type = fields.get("event_type")
    if event_type not in AUTHORED_EVENT_TYPES:
        raise ValueError(
            f"P5 does not author {event_type!r}; it authors {AUTHORED_EVENT_TYPES}. "
            "`discovery`, `stat observation` and `hashing` are P3's, and the move "
            "events are P12's (M8)."
        )
    if "subsystem" in fields and fields["subsystem"] != SUBSYSTEM:
        raise ValueError(
            f"P5 cannot author an event as {fields['subsystem']!r}: the acting part "
            "authors and P1 writes (M8)"
        )
    if not fields.get("explanation"):
        raise ValueError(
            "§8.2 requires a structured explanation or evidence reference on every "
            "event; P1's writer refuses an empty one"
        )
    return {
        **fields,
        "subsystem": SUBSYSTEM,
        "component_version": fields.get("component_version") or COMPONENT_VERSION,
        "observed_at": fields.get("observed_at") or datetime.now(timezone.utc).isoformat(),
    }
