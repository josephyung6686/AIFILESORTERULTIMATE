# Wave 2 — the scan → extract → store → bundle orchestrator

Date: 2026-08-20
Status: **seam contract draft** — one page, not a fourteenth part
Design: [`01-product-design-structured.md`](01-product-design-structured.md) · source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md)
Bindings: [`02-segmentation-map.md`](02-segmentation-map.md) (walking skeleton) · [`11-ops-runtime.md`](11-ops-runtime.md) · [`16-p4-p5-catalogue-recheck.md`](16-p4-p5-catalogue-recheck.md) punch-list item 4

P1, P2 and P3 are shipped; P4 and P5 are planned and green. **Nothing calls them in sequence.**
`scan_agent.scan.scan()` returns a `scan_run_id` and stops. This page names the caller.

It is **not a part.** It owns no design section, publishes no vocabulary, and adds no table.
[`02`](02-segmentation-map.md) says the walking skeleton *"stays in the repository as the integration
test every later part must keep green"*; this page makes the Wave-2 half of it **one path** rather
than four separate stories.

## What it owns

1. **Order.** P3 scan → P5 route/extract → P4 record → P1 status → P2 bundle, once per scan run.
2. **The exception contract** — which refusal produces a run row and which produces nothing.
3. **The two joins each part half-published** — `source_scan_ref = scan_run_id` and `files.extraction_status_by_tier`.
4. **Passing `author` through.** M8, §8.2: the acting part authors, P1 stores.

## What it does not own

- **No vocabulary.** It spells no `completeness`, `source_type`, `analysis_tier`, zone or event type;
  every such value reaches P1/P4 inside a record a part constructed.
- **No derivation.** `extraction_status_by_tier(runs)` is P5's, `bundle_counts` P2's,
  `scan_run_summary` P3's. It calls them and computes none of them.
- **No ceiling enforcement.** §8.6's ceilings are P1's sixteen keys; the predicates belong to the
  parts that spend.
- **No refusal of its own.** Full Disk Access (11 §1) is `require_access` inside `scan()`; protected
  containers and dataless files are `admit()` inside every extractor (11 §4b, §5).
- **No concurrency rule.** 11 §7's *"two scans do not run on the same root"* is unowned and **this page
  does not claim it** (OQ1). **No authorship** either: it never appears in an event's `subsystem`.

## Contract in

| From | Surface the orchestrator uses |
|---|---|
| **P3** (shipped) | `scan(conn, selection_id, *, source, mime_type_for, scan_state, budget_exhausted) -> scan_run_id`; the roster `cache_verdicts(conn, scan_run_id)` with `VERDICT_RECOMPUTE`/`VERDICT_REUSE`; `exclusion_verdicts`, `dataless_detections`, `scan_run_summary`; the two predicates P5's `SafetyPolicy` takes |
| **P1** (shipped) | `get_file`; `set_extraction_status(conn, file_id, *, status_by_tier, author, component_version)` (`files_table.py:147`); `budget.CEILING_KEYS`; `scan_usage.scan_resource_usage` |
| **P4** (planned) | `record_run(conn, ExtractionRun) -> run_id`; `record_run_event(conn, run_id, *, author)`; the nine `completeness` values, `dataless` among `ZERO_OBSERVATION_COMPLETENESS` |
| **P5** (planned) | `route()`, `SafetyPolicy`, `admit()`, `ProtectedContainerRefused`, `DatalessRefused`, `ExtractionResult`, the `EvidenceSink` protocol, `extraction_status_by_tier(runs)`, `authorship.SUBSYSTEM`/`COMPONENT_VERSION` |
| **P2** (shipped) | `open_bundle(conn, *, corpus_form, source_scan_ref, pinned_plan_id, pinned_plan_version, policy_settings, supersedes_bundle_id=None)`, `add_file_entry`, `add_extraction_run`, `add_extraction_output`, `add_text_unit`, `seal_bundle`, `bundle_counts` |

**Required from P5 and not yet published:** a `dataless_result()` constructor beside
`unrouted_result()` and `deferred_result()` (OQ4), and a per-file dispatcher (OQ2).

## The call sequence — one scan

```python
# scan_agent (P3), database_agent (P1) and eval_harness (P2) are shipped;
# evidence_shape (P4) and extractors (P5) are planned. SUBSYSTEM == "P5".
from pathlib import Path
from scan_agent.scan import scan
from scan_agent.stat_cache import VERDICT_RECOMPUTE, cache_verdicts
from database_agent.files_table import get_file, set_extraction_status
from eval_harness.bundle import open_bundle, seal_bundle
from evidence_shape.runs import record_run_event
from extractors.authorship import COMPONENT_VERSION, SUBSYSTEM
from extractors.router import route
from extractors.safety import DatalessRefused, ProtectedContainerRefused
from extractors.tiers import extraction_status_by_tier

# 1 — P3. Full Disk Access is checked INSIDE scan(), before the run row exists (11 §1),
#     so a refused scan leaves no partial corpus and no run to mistake for one.
scan_run_id = scan(conn, selection_id, source=source, mime_type_for=mime_type_for,
                   scan_state=scan_state, budget_exhausted=budget_exhausted)

# 2 — the roster. §1.2's stat cache: on REUSE, P5 is not invoked and prior results stand.
#     The skip is P3's published constant, not a local rule.
for verdict in cache_verdicts(conn, scan_run_id):
    if verdict["verdict"] != VERDICT_RECOMPUTE or verdict["file_id"] is None:
        continue
    file_row = get_file(conn, verdict["file_id"])
    decision = route(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                     path=Path(file_row["current_path"]),          # live column name
                     extension=file_row["extension"],
                     detect_format=detect_format)
    runs = []
    for handler in p5_handlers(decision):     # OQ2 — P5 publishes no dispatcher yet
        try:
            result = handler(file_row=file_row, policy=policy, decision=decision, now=now())
        except ProtectedContainerRefused:
            # `continue` the OUTER loop, never `break` this one: `break` falls through
            # to set_extraction_status below, which is a P1 write authored "P5" on a
            # file the product is forbidden to have touched. Verified by execution
            # (19-orchestrator-verification.md D3a).
            raise _SkipFile                   # NO run, and NO status write, for anything inside
        except DatalessRefused:
            result = dataless_result(file_row=file_row, decision=decision, now=now())  # OQ4
        run_id = sink.write(result)           # P4's EvidenceSink -> P4's run_id
        record_run_event(conn, run_id, author=SUBSYSTEM)     # §8.2 `extraction` / `OCR`
        runs.append(result.run)

    # 3 — P1. The map is P5's; P1 stores it opaquely and interprets no key.
    set_extraction_status(conn, file_row["file_id"],
                          status_by_tier=extraction_status_by_tier(runs),
                          author=SUBSYSTEM, component_version=COMPONENT_VERSION)

# 4 — P2. The join P3 published, P1 adopted, and nothing made until now.
bundle_id = open_bundle(conn, corpus_form=corpus_form,               # OQ7
                        source_scan_ref=scan_run_id,
                        pinned_plan_id=None, pinned_plan_version=None,  # P10 absent
                        policy_settings=policy_settings)
#   then add_file_entry / add_extraction_run / add_extraction_output / add_text_unit per file
seal_bundle(conn, bundle_id)
```

Every value passed came from the part that owns it. `dataless_result`, `p5_handlers`, `sink`,
`policy`, `detect_format`, `now`, `corpus_form` and `policy_settings` are caller-supplied or
part-owned; none is a value this page names.

## The exception contract

| Refusal | Raised by | Orchestrator | The record that already exists |
|---|---|---|---|
| `ProtectedContainerRefused` | `admit()` — 11 §4b | **nothing**: `break`; no run row, no observation, no status write for anything inside | P3's R3 exclusion verdict on the **container**, reason `protected_container`, label `untouched_protected` (P3 SPEC, ratified 2026-08-20) |
| `DatalessRefused` | `admit()` — 11 §5 | **one** run at `completeness = dataless`, zero observations, then `record_run_event` | P3's `dataless_detections` row for the path |

**Why the asymmetry is not an inconsistency.** Both refusals protect a read; they differ in what the
product is permitted to *know*. §4b says exactly this and no more: *"P3 does not descend into one and
hashes nothing inside it, and P12 never moves one."* The rest is **inference, and is marked as such**:
if P3 never descends and never hashes, then nothing inside ever acquires a `file_id` or a
`content_hash`. A run row requires both — so writing one is not merely disallowed, it is
**unconstructible** — so writing one **would be** the read
the rule exists to prevent; the container's exclusion verdict is the whole record, and P13 presents
protected containers as a distinct, inspectable list (P3 SPEC). A dataless file is the opposite: 11 §5
says only *"do not materialize, hash, or extract"* and the identity is already known, so the file **can**
be named — and §8.6 requires it to be, *"to show the difference between completed work and deferred
work… avoids the false impression that an unprocessed file was understood and found unimportant."* C4
(ratified 2026-08-20, in both P4's and P5's tables) added the ninth value precisely so §8.6's line can
say *31 files are in iCloud* instead of filing them under a word that lies. P2 already counts a row
nothing writes — `runs_dataless`, `src/eval_harness/counts.py:66`.

**The gate keeps one job.** C4: *"the gate still raises and writes nothing — a gate that also wrote
would be doing two jobs."* `admit()` is unchanged; this page is the catcher C4 names. **Caveat:** a
file dataless at *first sight* has no `files` row at all, so the run is writable only for a file
recorded while local and evicted since — OQ3.

**Not yet built.** Shipped `src/scan_agent/exclusion.py` has three rules and no `protected_container`;
P3's ratified rule and its `untouched_protected` label are spec-only, so `SafetyPolicy.is_protected_container`
has no P3 implementation to inject and done-means 4 cannot pass until P3 ships it. Build order: P4 → P5
(with `dataless_result` and a dispatcher) → P3's protected-container rule → this caller → the skeleton.

## Where `author` comes from

Never from the orchestrator. §8.2 requires *"the responsible subsystem"*, and [`02`](02-segmentation-map.md)
states the rule inherited here: an author field naming the part that merely arranged the work makes §8.2's
reconstruction requirement unmeetable.

| Write | `author` | Source |
|---|---|---|
| `record_run_event(conn, run_id, author=…)` | `"P5"` | `extractors.authorship.SUBSYSTEM` |
| `set_extraction_status(…, author=…, component_version=…)` | `"P5"`, P5's version | same module |
| `discovery` · `stat observation` · `external modification detection` | `"P3"` | authored inside `scan()`; the orchestrator is not on that path |

P1's shipped docstring states it: *"the acting part authors its `extraction` or `OCR` event and P1
records the status under it."* The orchestrator's only duty is that the event is appended for the same run.

## `files.extraction_status_by_tier`

- **P5 computes the map** — `extraction_status_by_tier(runs)`, a pure function over this file's runs,
  mapping I4's four tiers `filesystem | native | ocr | llm` to P4 `completeness`; a missing key means
  that tier was not attempted ([`10-i4-learning-ops.md`](10-i4-learning-ops.md)).
- **P1 stores it** — `set_extraction_status` (shipped, `files_table.py:147`), opaquely; a key P1 has
  never heard of round-trips unchanged.
- **The orchestrator calls it** once per file, after that file's runs are written; it builds nothing.
  §8.2's file record names *"Extraction status by extractor tier"*, and until this call exists the column
  reads `{}` after a real extraction.

## Idempotency and resumption

**There is no checkpoint mechanism in the design and none is invented here.** An interrupted scan
resumes as a *new* scan, and what holds is what the parts already guarantee:

- **P3** — `scan_runs.completed_at` stays NULL and P1's closing `sample_scan_resources` never runs. A
  re-scan mints a new `scan_run_id`; already-recorded files take `VERDICT_REUSE` when size and mtime are
  unchanged, so §1.2's stat cache does resumption's work without being called that.
- **P4/P5** — `extraction_runs` is append-only (`extraction_runs_no_delete`) and a re-run at the same
  §3.4 cache key **supersedes** rather than replaces (§8.2), so re-extraction is duplicative and never
  corrupting; P1's `extraction_status_by_tier` is a projection the second pass simply rewrites.
- **P2** — a sealed bundle is immutable; an interrupted one stays a draft, and `rebuild_bundle`
  creates a successor rather than editing it.

**Unresolved:** nothing records *which files of a scan run have been extracted*; §3.4's cache-key index
makes skip-on-hit available, but whether a hit is a valid skip is P4/P5's call — OQ6.

## Contract out

`(scan_run_id, bundle_id)` — P3's identity returned unchanged, and P2's sealed bundle carrying
`source_scan_ref = scan_run_id`. No table, no event type, no vocabulary member, no new field on
anyone else's record.

## Done means

1. One function runs P3 → P5 → P4 → P1 → P2 for one selection and returns `(scan_run_id, bundle_id)`.
2. `get_bundle(conn, bundle_id)["source_scan_ref"] == scan_run_id`.
3. A fixture recorded **while local and evicted since** yields exactly one `extraction_runs` row at
   `completeness = "dataless"` with `observation_count == 0`, and `bundle_counts(…)["runs_dataless"] == 1`.
   A **first-sight** dataless file yields no run and is counted only by P3 (OQ3).
4. One application-bundle fixture yields **zero** `extraction_runs` rows for anything inside it, one P3
   exclusion verdict on the container, and no `files` row beneath it.
5. `get_file(…)["extraction_status_by_tier"]` is no longer `"{}"` after a real extraction, and its keys
   are a subset of I4's four.
6. Every `extraction_runs` row carries exactly one §8.2 event whose `subsystem` is `"P5"`.
7. The Wave-2 half of [`02`](02-segmentation-map.md)'s walking skeleton runs as one call, and stays green.
8. A grep guard (P5 Task 20's pattern) proves no P4/P5 vocabulary member appears as a literal **in the
   orchestrator module** — this page names `dataless` to state the contract; the code must not.

## Cross-cutting answers

### Provenance (§8.2)
Authors nothing of its own. It carries the acting part's `author` and `component_version` into every P1
write that takes one, and appends the run's `extraction`/`OCR` event immediately after the run write,
so no run exists without its event.

### Budgets and degradation (§8.6)
**This is where §8.6's count line becomes true**, and no count is the orchestrator's:
`scan_run_summary` (P3), `extraction_counts` (P5), `bundle_counts` incl. `runs_dataless` (P2). It
**records; it enforces no ceiling** — the sixteen keys are P1's (`budget.CEILING_KEYS`) and the
predicates belong to the parts that spend: P3's `budget_exhausted`, passed through untouched, and
P5's four OCR/image ceilings (unset, B3). §8.6's *"cost exhaustion must never turn into
lower-quality automatic classification"* is satisfied by the parts refusing, not by this page
choosing; the elapsed/memory/CPU counters are sampled by P3's `finish_scan_run`, not resampled here.

### Correction learning (§8.7)
None. §8.7's learning records are scoped **user actions** and no step here is one. 11 §8 requires every
*proposal* path to read `learning_records` before emit — P3 and P5 propose nothing, so Wave 2 has no
learning read; that obligation begins at P6.

### Plan versioning (§8.8)
Holds no plan. `open_bundle`'s `pinned_plan_id` and `pinned_plan_version` are `None` because P10 does
not exist yet, and P2 already types both nullable. §8.8's *"a new plan should never silently
reclassify"* is unreachable from here: nothing in this sequence places a file.

## Open questions

1. **Two scans on one root.** 11 §7: *"A second scan of an in-flight root is refused."* Nothing refuses
   it — `scan()` has no such check, `start_scan` keys only on `scan_run_id`. **This page does not claim
   it**: the refusal compares *roots*, which is R1 selection knowledge, so it is **P3's**. *Blocks:* a
   correct 11 §7 the moment a re-scan can start while one is in flight.
2. **P5 publishes no per-file dispatcher.** `route()` returns one `RoutingDecision`; the eight
   `extract_*` functions are separate, and an opaque image legitimately runs E5 **and** E6 (two rows).
   Who walks from decision to handler(s) is unassigned. *Blocks:* the inner loop above, written against
   a placeholder. **P5's call.**
3. **A never-local dataless file has no identity to name.** `scan.py` records the detection and
   `continue`s before `record_basic_record`, so no `file_id` or `content_hash` exists; `extraction_runs`
   requires both `NOT NULL`, and minting a `files` row without hashing would violate 11 §5. Direction:
   **two counts** — never-hashed reported from `dataless_detections`, hashed-then-evicted reported as a
   `dataless` run. *Blocks:* done-means 3's fixture choice. **P3's or P4's call**, not settled here.
4. **`dataless_result()` does not exist.** P5 publishes `unrouted_result()` and `deferred_result()` so
   no caller has to spell a stopped run's fields. There is no dataless sibling, and the orchestrator
   must not invent its `source_type` or `analysis_tier`. *Blocks:* done-means 3. **P5's call.**
5. **Two writers for the one `extraction` event.** P4 publishes `record_run_event(conn, run_id, *,
   author)`; P5 publishes `extraction_event()` + `append()`. One concept, one writer. *Blocks:*
   done-means 6, which cannot assert "exactly one event per run" until this is settled.
6. **No resumption record.** Nothing states which files of an interrupted scan were extracted; §3.4's
   cache-key index makes skip-on-hit available, but whether a hit is a valid skip is **P4/P5's**.
   *Blocks:* nothing for correctness (append-only, supersede); a second pass repeats work.
7. **`corpus_form` for the Wave-2 bundle.** `open_bundle` requires it, and the choice has consequences:
   ratified 2026-08-20, `metadata_safe` does not round-trip file identity and writes no `files` row on
   replay, while `snapshot` entries need `payload_ref` bytes. (`handling_class` does *not* block —
   shipped as `str | None`, so it stays `None` until P7 and no class is invented.) *Blocks:* the
   skeleton's bundle step. **P2's call.**

---

## Pre-build review (2026-08-20, late)

Read with [`18-p4-p5-prebuild.md`](18-p4-p5-prebuild.md). Two files share the `18-` prefix; they are different documents. **Do not build this module until P4 and P5 import.** Do not mint P14.

The seam is the right object. The exception contract is load-bearing: `admit()` still raises; **this page** is the catcher C4 named (not P5 Task 4). Protected container → no run is correct. `set_extraction_status` is already shipped (`files_table.py:147`); P5 PLAN still saying P1 has no setter is stale. `author` is always `"P5"` or `"P3"`, never this page.

### Blocking if copied literally

1. **Done-means 3 vs live P3.** `scan()` records `dataless_detections` and `continue`s before any `files` row (`scan.py` ~53–55). First-sight iCloud never enters `cache_verdicts`, so this loop never writes `extraction_runs`. Close OQ3 as two counts: never-hashed → P3 detections only; hashed-then-evicted → one `completeness=dataless` run and `runs_dataless`. Done-means 3 must use the **second** fixture. Inventing a `files` row without a hash violates 11 §5.

2. **`file_row["path"]`.** Live column is `current_path`. The sketch `KeyError`s on the first file.

### Recommended closes (do not invent values here)

| # | Close as |
|---|---|
| OQ1 | P3's. This page does not compare roots. |
| OQ2 | Overstated. One P5 `extract(file_row, decision, …)` that may return two runs (E5+E6). Orchestrator does not dispatch by name. |
| OQ3 | Two counts, table above. |
| OQ4 | P5 adds `dataless_result()` beside `unrouted_result`. Direction: `analysis_tier=filesystem`, zero observations, only if `file_row` exists. |
| OQ5 | One writer: P4 `record_run_event`. P5 `append` becomes the thin wrapper Task 16 already describes. |
| OQ6 | No checkpoint. New `scan_run_id`; `VERDICT_REUSE` + supersede. Repeat work accepted for Wave 2. |
| OQ7 | Overstated. `handling_class` is already `str \| None`. Skeleton: `corpus_form="snapshot"`, `handling_class=None` until P7. Do not invent a class (C2 still open). |

Build order: P4 → P5 (include `dataless_result` + one `extract`) → this caller → walking skeleton with corrected Done-means 3–4.
