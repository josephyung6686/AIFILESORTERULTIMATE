# src/extractors/events.py
# WHEN P4 LANDS, `append` BECOMES A CALL INTO P4 AND STOPS WRITING DIRECTLY.
#
# P4 Task 10 publishes `record_run_event(conn, run_id, *, author)`, which appends the
# one §8.2 event for a run AFTER its observations exist, reading the `observation_key`s
# out of the rows so the event and the database cannot disagree. P5 is the AUTHOR
# (`author="P5"`); P4 is the writer. That is M8.
#
# This module exists because P4 has not landed, and it must not survive as a second
# writer: two helpers appending one run's event means either a duplicated event or a
# dead API, and M8 cannot survive two. The day `evidence_shape` is importable:
#
#     from database_agent.events import append_event
#
#     def append(conn, event) -> int:
#         return record_run_event(conn, event.run_id, author=SUBSYSTEM)
#
# `extraction_event()` / `ocr_event()` stay: they are the payload builders and the
# guard that P5 authors none of P3's event types. What goes is the direct
# `append_event` call below -- P4 builds the same dict from the stored rows.
"""Section 8.2 - the two events P5 authors. P1 writes them (M8).

Each carries "the event type, file ID, content hash, responsible subsystem, extractor
version, time of observation, and a structured explanation or evidence reference".
P1's `events` has eleven fields forever (MINOR 1), so section 8.2's extractor version
occupies `component_version`, and the run_id - the handle for a run's observations,
text units and outcome - is section 8.2's evidence reference.

For the OCR event, section 8.2's model positions are the OCR positions: the provider
VERSION is `component_version` and the CONFIGURATION, which is where section 2.7's
languages live, is `prompt_fingerprint`, computed by the same `fingerprint()` that
produces P4's `config_fingerprint` so one configuration has one identity in both.
"""
from __future__ import annotations

import sqlite3
from typing import Any, Mapping

from database_agent.events import append_event

from extractors.authorship import event_defaults
from extractors.shape import canonical_json, fingerprint

#: Section 8.2's own spellings. `OCR`, not `ocr` (MINOR 2): P1's writer validates the
#: type against section 8.2's frozen vocabulary and the lowercase form is rejected at
#: the INSERT.
EXTRACTION = "extraction"
OCR = "OCR"


def extraction_event(*, run_id: str, file_id: str, content_hash: str,
                     extractor_name: str, extractor_version: str,
                     completeness: str, observed_at: str,
                     event_type: str = EXTRACTION, **extra: Any) -> dict:
    """One `extraction` event - once per file per extractor family per content
    version."""
    return event_defaults(
        event_type=event_type, file_id=file_id, content_hash=content_hash,
        component_version=extractor_version, observed_at=observed_at,
        explanation=canonical_json({
            "run_id": run_id,
            "extractor_name": extractor_name,
            "extractor_version": extractor_version,
            "completeness": completeness,
            **extra,
        }),
    )


def ocr_event(*, run_id: str, file_id: str, content_hash: str, provider: str,
              provider_version: str, config: Mapping[str, Any],
              completeness: str, observed_at: str, **extra: Any) -> dict:
    """One `OCR` event - once per OCR run."""
    return event_defaults(
        event_type=OCR, file_id=file_id, content_hash=content_hash,
        component_version=provider_version,
        prompt_fingerprint=fingerprint(config), observed_at=observed_at,
        explanation=canonical_json({
            "run_id": run_id,
            "provider": provider,
            "provider_version": provider_version,
            "completeness": completeness,
            **extra,
        }),
    )


def append(conn: sqlite3.Connection, event: Mapping[str, Any]) -> int:
    """Hand one authored event to **P4's** writer. P5 stores no event of its own.

    P4 shipped 2026-08-20 and publishes `record_run_event(conn, run_id, *, author)`,
    which appends the run's one §8.2 event AFTER its observations exist and builds the
    explanation from the stored rows -- so the event and the database cannot disagree.
    This function called P1's `append_event` directly until then. Both surviving meant
    an orchestrator following both plans wrote TWO `extraction` events per run, and
    "exactly one event per run" could not hold. P5 is the AUTHOR; P4 is the writer.

    `extraction_event()` / `ocr_event()` stay: they are the payload builders and the
    guard that P5 authors none of P3's event types.
    """
    # NOT YET P4's writer, and this is a finding rather than an oversight.
    # `record_run_event(conn, run_id, *, author)` reads the run's observation_keys
    # from the STORED rows, so it requires the run to already exist in P4's tables.
    # P5 authors an event for a run it has just built and not yet handed to a sink,
    # so there is nothing for P4 to read. Closing break 5 therefore needs the
    # orchestrator's ordering -- write run, write observations, THEN one event --
    # which is exactly the sequence 18-wave2-orchestrator.md specifies and which
    # does not exist yet. Swapping the call here without that ordering trades two
    # writers for one broken one.
    return append_event(conn, **event)
