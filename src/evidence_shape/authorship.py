# src/evidence_shape/authorship.py
"""P4 authors no event: the acting part authors, P1 writes, P4 supplies the writer.

M8 (04-resolutions.md): "The acting part authors; P1 writes. P1 appends no event on
its own initiative." P5's SPEC claims the `extraction` and `OCR` events for itself,
and P8 is the acting part for an `analysis_tier = llm` run (I4). This module
therefore publishes no subsystem name and no default author; every caller names
itself, exactly as P1's own `observe_path(conn, path, *, author, ...)` requires.

`OCR` is spelled with capitals because §8.2 spells it that way and P1's writer
validates the event type against that vocabulary (MINOR 2, 05-minor-resolutions.md).
The lowercase word in `analysis_tier` and `source_type` belongs to two other
vocabularies and is not this name.
"""
from __future__ import annotations

from datetime import datetime, timezone

from database_agent.events import EVENT_FIELDS, RESERVED_EVENT_TYPES

#: §8.2's own two names for what an extraction run is. Both reserved; P4 registers
#: neither, because registration is a spec-level act (P1 Contract out §3, rule 4).
EXTRACTION_EVENT = "extraction"
OCR_EVENT = "OCR"
RUN_EVENT_TYPES: tuple[str, str] = (EXTRACTION_EVENT, OCR_EVENT)

#: I4's tier whose run is an OCR event rather than an extraction event. SPEC,
#: Cross-cutting answers -> Provenance: "`extraction`, or `OCR` when the extractor
#: is OCR"; I4 makes "the extractor is OCR" the closed value `ocr`.
OCR_ANALYSIS_TIER = "ocr"

#: M8: a caller naming P1 as the author of an extraction is recording that the
#: storage substrate read the document.
_STORAGE_SUBSYSTEM = "P1"


class UnauthoredEvent(Exception):
    """A run event with no responsible subsystem (§8.2), or with P1 named as one."""


def run_event_type(analysis_tier: str) -> str:
    """Which of §8.2's two names this run's event carries."""
    return OCR_EVENT if analysis_tier == OCR_ANALYSIS_TIER else EXTRACTION_EVENT


def check_author(author: str | None) -> str:
    """§8.2 requires "the responsible subsystem". P4 supplies no default for it."""
    if not author:
        raise UnauthoredEvent(
            "§8.2 requires the responsible subsystem on every event; P4 authors no "
            "event and supplies no default author"
        )
    if author == _STORAGE_SUBSYSTEM:
        raise UnauthoredEvent(
            "P1 stores; it originates no event (M8). Name the acting part: P5 for a "
            "filesystem, native or OCR run, P8 for an llm-tier run."
        )
    return author


def event_defaults(*, author: str, component_version: str, event_type: str,
                   **fields) -> dict[str, object]:
    """§8.2's authorship fields, ready for P1's `append_event`. Writes nothing.

    A caller-supplied `observed_at` wins, so a replay can pin the time (§8.5).
    """
    check_author(author)
    if event_type not in RUN_EVENT_TYPES:
        raise UnauthoredEvent(
            f"{event_type!r} is not one of the two events an extraction run appends "
            f"{RUN_EVENT_TYPES}; P4 supplies a writer for no other event type"
        )
    unknown = sorted(set(fields) - set(EVENT_FIELDS))
    if unknown:
        raise UnauthoredEvent(
            f"{unknown} are not among §8.2's eleven event fields (MINOR 1); P4 adds none"
        )
    return {
        "event_type": event_type,
        "subsystem": author,
        "component_version": component_version,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
