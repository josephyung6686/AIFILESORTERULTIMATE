# src/extractors/events.py
# P5 WRITES NO EVENT. P4 DOES, ONCE PER RUN, AT THE END OF THE BATCH.
#
# P4 Task 10 publishes `record_run_event(conn, run_id, *, author)`, which appends the
# one §8.2 event for a run AFTER its observations exist, reading the `observation_key`s
# out of the rows so the event and the database cannot disagree. P5 is the AUTHOR
# (`author="P5"`); P4 is the writer. That is M8.
#
# `append` lived here and called P1's `append_event` directly. Both surviving meant an
# orchestrator following both plans wrote TWO `extraction` events per run, and
# "exactly one event per run" could not hold. What had blocked the swap was real and
# was recorded at the call site: `record_run_event` needs the run and its observations
# already stored, and P5 authored its event for a run no sink had yet seen. There was
# no sink. `evidence_shape.store.RunWriter` is now that sink -- run row, text units,
# observations, then the one event, in one transaction -- so the event P5 used to
# append is appended by the writer that owns the rows it references.
#
# `append` is therefore DELETED rather than made a one-line call into P4. A delegating
# wrapper would leave one writer under two names, which is the same defect as one
# value under two computations and is the one this project has paid for most often.
#
# `extraction_event()` / `ocr_event()` remain below as payload builders and as the
# guard that P5 authors none of P3's event types. Stated plainly, because a comment
# that overstates is how the header above went stale: NOTHING IN `src/` CALLS EITHER
# ONE. `record_run_event` builds its own payload from the stored rows, and it writes no
# `prompt_fingerprint` on purpose -- P4's SPEC, Provenance: "`prompt fingerprint` does
# not apply (P4 is model-free)" -- so §2.7's configuration identity reaches the
# database on `extraction_runs.config_fingerprint`, not on the event row. Their only
# callers today are tests/p5/.
"""Section 8.2 - the two events P5 authors. P4 writes them, once per run (M8).

Each carries "the event type, file ID, content hash, responsible subsystem, extractor
version, time of observation, and a structured explanation or evidence reference".
P1's `events` has eleven fields forever (MINOR 1), so section 8.2's extractor version
occupies `component_version`, and the run_id - the handle for a run's observations,
text units and outcome - is section 8.2's evidence reference.

For the OCR event, section 8.2's model positions are the OCR positions: the provider
VERSION is `component_version` and the CONFIGURATION, which is where section 2.7's
languages live, is `prompt_fingerprint`, computed by the same `fingerprint()` that
produces P4's `config_fingerprint` so one configuration has one identity in both.

**That last sentence describes an event P4 does not write, and this is the record of
it.** `record_run_event` leaves `prompt_fingerprint` NULL by design -- P4 SPEC,
Provenance: "`prompt fingerprint` does not apply (P4 is model-free)" -- so an OCR run
that goes through the sink, which is every OCR run now, has no configuration on its
EVENT row. Nothing is lost from the database: the same digest is on
`extraction_runs.config_fingerprint`, and no consumer reads `events.prompt_fingerprint`
(P2's `prompt_fingerprint` is an axis of its own `version_tuple` record, not a read of
this column). What is lost is `ocr_event()`'s claim to describe a shape the database
will produce, and a docstring that overstates is how the header above went stale in
the first place.
"""
from __future__ import annotations

from typing import Any, Mapping

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
