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
# `extraction_event()` and `ocr_event()` are DELETED, 2026-09-02, for the reason this
# header already established against them: nothing in `src/` ever called either one.
# `record_run_event` builds its own payload from the stored rows, and it writes no
# `prompt_fingerprint` on purpose -- P4's SPEC, Provenance: "`prompt fingerprint` does
# not apply (P4 is model-free)" -- so §2.7's configuration identity reaches the
# database on `extraction_runs.config_fingerprint`, not on the event row. That made
# `ocr_event()`'s docstring a description of a shape the database does not produce,
# which is the same overstatement this header was rewritten to stop making. The one
# stated reason to keep them -- "the guard that P5 authors none of P3's event types"
# -- is `extractors.authorship.event_defaults`'s own refusal, which is live, and
# `tests/p5/test_p5_events.py` now asserts it there.
#
# What survives here is §8.2's two spellings, which P1's writer validates against.
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
this column). The paragraph above is kept because it describes §8.2 as WRITTEN, and
the divergence is the thing worth knowing; the builder that used to claim otherwise
is gone.
"""
from __future__ import annotations

#: Section 8.2's own spellings. `OCR`, not `ocr` (MINOR 2): P1's writer validates the
#: type against section 8.2's frozen vocabulary and the lowercase form is rejected at
#: the INSERT.
EXTRACTION = "extraction"
OCR = "OCR"
