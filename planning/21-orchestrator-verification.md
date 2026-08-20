# Wave-2 orchestrator verification

Date: 2026-08-21 (~02:10)
Status: **The happy path runs. The caller is not finished.** `PYTHONPATH=src python3 -m pytest tests/wave2 -v` → **16 passed** (fresh this pass). Probes below were executed against live `src/orchestrator.py`, not inferred from [`18-wave2-orchestrator.md`](18-wave2-orchestrator.md).
Companion: [`20-p1-p5-recheck.md`](20-p1-p5-recheck.md) (P1–P5 join). Seam contract: [`18-wave2-orchestrator.md`](18-wave2-orchestrator.md) (partly stale vs code).

The orchestrator is **not a part**. It owns order, the two refusal outcomes, the two joins (`source_scan_ref`, `extraction_status_by_tier`), and passing `author` through. It publishes no vocabulary and adds no table.

---

## Verdict

`run_wave2` does what Wave 2 was cut to do on a first scan of a mixed corpus: P3 `scan` → filesystem + P5 `extract()` → P4 `RunWriter` → P1 `set_extraction_status` → P2 bundle. Protected `.app` is untouched. A reader exception becomes `failed` and the scan continues. Extractor upgrade bypasses P3 `REUSE`. First-sight iCloud is detections-only. Hashed-then-evicted writes one `dataless` run.

It does **not** yet produce a bundle that is safe to evaluate from, does **not** persist routing or sensitivity, and **does not** isolate a second selection from the first. Those are caller defects, not P4/P5 unit-test gaps. None of them fail `tests/wave2`.

Do not start P6 as a substitute for closing the three persist/wiring leftovers already named in file 20, plus the bundle-scope bug in this file.

---

## Fresh evidence (this pass)

| Check | Result |
|---|---|
| `tests/wave2` | **16 passed** in 0.99s |
| Done-means 1 (`Wave2(scan_run_id, bundle_id, run_ids)`) | Holds. First mixed scan writes runs |
| Done-means 2 (`source_scan_ref == scan_run_id`) | Holds (`test_the_bundle_carries_the_scan_run_as_its_source_ref`) |
| Done-means 3 (hashed-then-evicted → one `dataless` run, `runs_dataless == 1`; first-sight → no run) | **Holds when probed. No wave2 test covers it.** Status map side-effect is wrong (defect 3) |
| Done-means 4 (protected container → nothing inside) | Holds |
| Done-means 5 (status column no longer `{}`; keys ⊂ I4's four) | Holds on first extract. Eviction overwrite drops `filesystem` (defect 3) |
| Done-means 6 (one §8.2 event per run, `subsystem == "P5"`) | Holds. OCR runs correctly get `event_type = OCR` (P4 `run_event_type`). Skeleton assertion counts only `extraction` and would undercount if OCR were in the mixed corpus |
| Done-means 7 (walking skeleton one call) | Holds for the mixed corpus fixture |
| Done-means 8 (no completeness / zone / event-type literals in the module) | Holds (`test_the_orchestrator_holds_no_vocabulary`) |
| File 20 leftover 1 (sensitivity) | Confirmed live. Email `From` is stored. `extraction_sensitivity_signal` stays at 0 |
| File 20 leftover 2 (routing) | Confirmed live. Wave2 fixture never calls `create_extraction_schema`. Table absent on the path. `route()` is called; `record_routing_decision` is not |
| File 20 leftover 3 (`handling_class`) | Stored value is `None` (P1 `sensitivity_state` is NULL). The **name** is still the wrong column |

Do not reopen fingerprint, D10-at-the-result, `failed` catcher existence, stopped-run identity (`format.unrouted` / `native`), or the one-event writer.

---

## What the live caller actually does

`src/orchestrator.py` · `run_wave2(conn, selection_id, …) -> Wave2`.

1. P3 `scan()`.
2. For each `cache_verdicts` row with a `file_id`: skip unless `VERDICT_RECOMPUTE` **or** `_extraction_is_stale` (extractor version vs `current_versions()`). `current_path`, not `path`. `route()` then `extract_filesystem` + `_extract_one` (`extract()` dispatcher). `ProtectedContainerRefused` → `continue` the outer loop (no status write). `DatalessRefused` → `dataless_result`. Reader / builder errors inside `_extract_one` → `failed_result`. Each result → `sink.write` → `set_extraction_status` from **this pass's** runs only.
3. Loop `dataless_detections` for this `scan_run_id` (2b). No `files` row → skip (OQ3 first-sight). Else write `dataless_result` and **replace** the status map with that one run.
4. P2 `open_bundle` / `add_file_entry` for **`SELECT * FROM files`** / `add_extraction_run` + `add_text_unit` for **`written` this pass** / `seal_bundle`. `add_extraction_output` is never called.

`observations_for_run` is imported and unused — the hook for the missing output copy is sitting there.

---

## Confirmed defects (executed 2026-08-21)

### 1. The bundle is this pass's writes, not this selection's corpus

Second `run_wave2` on an unchanged two-file corpus:

| | After first scan | After second scan (all `REUSE`) |
|---|---|---|
| `extraction_runs` in the database | 4 | 4 |
| `Wave2.run_ids` | 4 | **0** |
| `bundle_counts` `files_indexed` | 2 | 2 |
| `bundle_counts` `files_with_any_run` | 2 | **0** |
| bundle `extraction_runs` | 4 | **0** |

§8.5's eval bundle is then a directory listing with no extractions. `test_a_second_scan_of_an_unchanged_corpus_re_extracts_nothing` only checks the database count, not the second bundle.

Worse, file membership is `SELECT * FROM files`, not this scan's roster. Two selections on one connection: bundle B contains `a.md` (selection A) **and** `b.md` (selection B). Bundle A correctly had one file. The second call leaks the first corpus into the eval envelope.

18-wave2's sketch says add runs **per file**. Live code adds runs per `_write` in this invocation.

### 2. `_extract_one` is all-or-nothing — an OCR failure discards a successful PDF run

`extract()` returns `(pdf native, ocr)` when the text layer is absent. The orchestrator wraps the **whole** call:

```python
dispatched = extract(...)
return dispatched.results
except Exception as error:
    return (failed_result(..., extractor_name=decision.extractor_name,
                          extractor_version=decision.router_version, ...),)
```

Executed: `pages=()` PDF + OCR engine that raises `RuntimeError("vision unavailable")`.

- Database: one `filesystem.record` `complete`, one `pdf.text` `failed`.
- `failure_reason`: `RuntimeError: vision unavailable`.
- No native-complete PDF run. No OCR run. The native work that finished is gone.

The same catcher stamps **`extractor_version = decision.router_version`** (`0.2.0`) onto a `pdf.text` row whose live version is `0.1.0`. A locked-PDF probe without OCR produced the same version lie. §3.4's cache key for that failed run is therefore the router's identity, not the extractor's.

### 3. Eviction 2b overwrites `extraction_status_by_tier` with the dataless run alone

Hashed-then-evicted fixture (P3 `Entry.dataless=True`, same size/mtime → `REUSE`, 2b writes the run):

| | Before eviction scan | After |
|---|---|---|
| Status map | `{filesystem: complete, native: complete}` | **`{native: dataless}`** |
| `dataless` runs | 0 | 1 (`format.unrouted`, `observation_count == 0`) |
| `bundle_counts()["runs_dataless"]` | 0 | 1 |
| `files` row | kept | kept |

Done-means 3's **run** contract holds. The status projection does not: filesystem indexing is still true and still in `extraction_runs`, and the column no longer says so. A later `extraction_status_by_tier` over **all** runs for the file would `TierConflict` (`native` `complete` vs `dataless`); 2b avoids that by discarding history from the projection instead of composing `{filesystem: complete, native: dataless}`.

There is **no** `tests/wave2` fixture for this. First-sight (no prior `files` row) was also probed: 0 files, 1 `dataless_detections` row, 0 runs. That half is implemented and untested too.

### 4. P3's dataless bit and P5's `SafetyPolicy.is_dataless` are not the same gate

P3 reads `st_flags` (or the corpus-source field). P5 `admit()` reads the injected policy. Wave2 `go()` defaults the policy to `is_dataless=lambda path: False`.

Executed: eviction **and** size change (`RECOMPUTE`) with the default policy. The native extractor ran again (`text.structured` `complete` — a real iCloud file would download). 2b **still** wrote `dataless`. The file now has both a complete native run and a dataless native run. Status after 2b is `{native: dataless}`.

The orchestrator is the only place that sees both predicates. It does not wire them.

### 5. Sensitivity, routing, outputs, `handling_class` — still dropped on the real path

Already named in file 20; re-executed so they are not stale:

| Signal | Live |
|---|---|
| Email `From: dean@wustl.edu` | Native observation stored. `extract()` returned `Dispatched.sensitivity`. Orchestrator keeps `.results` only. Table count **0** (and the table is not created by the wave2 fixture) |
| `route()` | Called twice per extracted file (main loop + 2b when it fires). `record_routing_decision` never called |
| `add_extraction_output` | Not in `orchestrator.py`. Bundle observation payloads **0** |
| `handling_class` | `file_row["sensitivity_state"]`. C2/P7 still open. 18-wave2 OQ7 close was **`None` until P7**, not a different P1 column. NULL today, so tests pass |

### 6. `extract_filesystem` is outside the failed catcher

Patched `orchestrator.extract_filesystem` to raise `Weird("stat exploded")`. The scan **crashed**; no `failed` run. `_extract_one`'s `except Exception` only wraps `extract()`. `admit()` on the indexer only raises the two refusals, so a normal corpus will not hit this. A missing `files` column would.

---

## What is already right

- Order is P3 → P5 → P4 → P1 → P2, one function, no fourteenth part.
- `current_path`. Protected container: `continue` the outer loop, not `break` (the sketch's `break` would have written status). First-sight dataless: no invented `files` row.
- M8: events `subsystem` ∈ `{P3, P5}`. Orchestrator never appears. AST guard has no completeness/zone/event-type/`P5` literals.
- One event per written run, inside `RunWriter`, including `OCR` when E6 actually runs.
- Reader errors on the dispatched extractors do not abort the scan (locked PDF fixture).
- Stale extractor versions bypass `REUSE`; earlier runs are kept.
- Mixed corpus: pdf / md / png / dmg (`native=metadata_only`) / mp4 / `Numbers.app` untouched. Live 64-hex hashes.

---

## 18-wave2 vs live (stale on the page, closed in code)

| 18 says | Live |
|---|---|
| `p5_handlers(decision)` (OQ2 open) | `extract()` dispatcher. OQ2 closed |
| `dataless_result` does not exist (OQ4) | Exists. `analysis_tier=native` (A4), not the page's `filesystem` direction |
| Two event writers (OQ5) | `RunWriter.write` ends with `record_run_event` |
| `record_run_event` beside the sink | Inside the sink |
| Protected catcher `break` | `continue` |
| `file_row["path"]` | `current_path` |
| P3 has no `protected_container` | Shipped. `.app` suffix + subtree |
| OQ7 `handling_class=None` until P7 | Code passes `sensitivity_state` |

OQ1 (two scans on one root) is still P3's and still unclaimed. OQ6 (no checkpoint) is the live policy: new `scan_run_id`, `REUSE` + version bypass.

---

## What to do next

Caller fixes, in the order that stops eval and §2.9 from lying:

1. **Bundle scope.** File entries = this scan's roster (or this selection's `files`), not `SELECT * FROM files`. Runs/text units = current runs for those files, not only `written` this pass. Then a `REUSE` scan's bundle is evaluable and a second selection does not swallow the first.
2. **`_extract_one`.** Persist `dispatched.results` that finished before a later handler raised; `failed_result` version from the handler that failed, not `router_version`. OCR failure must not erase a complete PDF run.
3. **2b status.** Projection is `{filesystem: complete, native: dataless}` (compose with the existing filesystem run), not `{native: dataless}`. Add the done-means 3 fixture that file 18 required and wave2 never wrote.
4. File 20 leftovers: `record_sensitivity_signals` after write via `observation_keys_for_run`; `record_routing_decision` + `create_extraction_schema` on the fixture; `handling_class=None` until P7.
5. Wire P5 `SafetyPolicy.is_dataless` to the same observation P3 used, or 2b is the only honest dataless path and `RECOMPUTE` will download.

Then P6. Do not reopen the closed join-breaks in file 19/20.
