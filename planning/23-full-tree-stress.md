# P1–P5 + orchestrator — full-tree stress

Date: 2026-08-21 (~11:45)
Status: **Not perfect.** Wave 1–2 runs. The caller still produces an eval bundle that can lie, and an OCR failure can erase a finished PDF run. `PYTHONPATH=src python3 -m pytest tests -q` → **1244 passed** in 72.77s (fresh this pass).
Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md) · cut: [`02-segmentation-map.md`](02-segmentation-map.md)
Supersedes the leftover list in [`20-p1-p5-recheck.md`](20-p1-p5-recheck.md) and the persist claims in [`21-orchestrator-verification.md`](21-orchestrator-verification.md). Those files stay as the pass that found the breaks. This pass re-executed against **live** `src/`.

Do not treat a green suite as “everything is perfect.” Every remaining break below passed 1244 tests.

---

> **Items 1–4 of *What to do next* are CLOSED (2026-08-21, commits `abcd1c4` + this one).** Nine
> tests in `tests/wave2/test_wave2_full_tree.py`, each verified red before green; suite at 1,256.
> This file stays as the pass that found the breaks — it is not rewritten.
>
> | | Closed by |
> |---|---|
> | 1 · bundle is the roster + current runs + `add_extraction_output` | roster from `cache_verdicts`, runs from `runs_for_file`, payloads deduped on P2's own UNIQUE key |
> | 2 · OCR failure keeps the native run; `failed` version; `UnknownFamily` | `_ocr` records its own failure run; `_failed_version`; `UnknownFamily(ContractViolation)` |
> | 3 · eviction composes `{filesystem: complete, native: dataless}` **+ the done-means 3 fixture, both halves** | status merge; `test_eviction_composes_…` (identity exists) and `test_a_file_dataless_at_first_sight_…` (identity never minted) |
> | 4 · one dataless switch | P3's detection wins in the caller; the native extractor no longer opens an evicted file |
>
> **Still open, and deliberately not touched:**
>
> - **Defect 5** — `extract_filesystem` sits inside the two-refusal `try` but outside the
>   `except Exception` catcher, which lives in `_extract_one` and runs after it. Fixing it changes
>   exception semantics for the indexer (is an indexer crash a fact about the FILE, or a
>   `ContractViolation` about the row it was handed?), and that is a decision, not a patch.
> - **Defect 6** — 11 §7, two in-flight scans on one root. Unowned, and P3's, not the caller's.
> - Found while fixing 1: two runs at one version over one content hash collided on
>   `bundle_extraction_output`'s UNIQUE key and killed the scan **at the bundle, after every
>   extraction had succeeded**. Deduped.

---

## Verdict

It is **not** perfect. It **is** the Wave 1–2 cut: one SQLite database, P3 fills `files`, P4 freezes one observation shape, P5 fills it, P2 measures, the caller runs them in order.

P4 and P5, as packages, hold the closed join-breaks from file 19 (fingerprint, stopped-run identity, `failed` catcher, D10 collapse, one event writer, empty `raw_value`, OCR name folding). The overnight caller fixes landed: sensitivity is stored against the E3 run, routing is persisted, `handling_class` is literal `None`.

What is still wrong is almost all in `src/orchestrator.py`, and none of it is a missing gazetteer.

---

## Closed since file 21 (re-executed)

| Leftover | Live now |
|---|---|
| Sensitivity dropped | Closed. Contacts `FN` / `EMAIL` stored as `potentially sensitive` on `text.structured`, keyed to those values, not the filename |
| Routing not recorded | Closed. One `extraction_routing` row per file on first extract. Wave2 fixture now calls `create_extraction_schema` |
| `handling_class=sensitivity_state` | Closed. Literal `None`. AST-guarded in `tests/wave2` |
| Fake P6 verdict `lambda: False` | Named. `TARGETED_OCR_UNAVAILABLE`. Behaviour unchanged (no targeted OCR); the call site no longer claims P6 examined the file |
| `ContractViolation` swallowed as `failed` | Closed. Propagates; scan stops; zero `failed` rows. Reader `ValueError` is still the file’s failure |

Do not reopen fingerprint, D10-at-result, `failed` catcher existence, stopped-run identity (`format.unrouted` / `native`), the one-event writer, or these five.

---

## Still broken (executed this pass)

### 1. The bundle is this pass’s writes, not this selection’s corpus

Unchanged from file 21. Second `run_wave2` on an unchanged two-file corpus:

| | First scan | Second scan (`REUSE`) |
|---|---|---|
| `extraction_runs` in the database | 4 | 4 |
| `Wave2.run_ids` | 4 | **0** |
| `bundle_counts.files_with_any_run` | 2 | **0** |

§8.5’s eval envelope is then a directory listing with no extractions. `test_a_second_scan_of_an_unchanged_corpus_re_extracts_nothing` only checks the database count. `test_the_bundle_counts_read_the_runs_that_were_actually_written` only asserts `files_indexed == 2`.

File membership is still `SELECT * FROM files`. Two selections on one connection: bundle B contains `a.md` **and** `b.md`.

`add_extraction_output` is still never called. Bundle observation payloads = 0. P2 already implements the writer; the caller never uses it. `observations_for_run` is no longer even imported.

### 2. An OCR failure discards a successful PDF run, and the version on `failed` is the router’s

`extract()` builds the PDF result, then calls OCR. OCR raises. `extract()` never returns the PDF result. `_extract_one` catches `Exception` and emits one `failed_result` stamped:

- `extractor_name = decision.extractor_name` (`pdf.text`)
- `extractor_version = decision.router_version` (**`0.2.0`**, live `pdf.text` is **`0.1.0`**)
- `failure_reason = RuntimeError: vision unavailable`

Executed: `pages=()` PDF + OCR engine that raises. Database: filesystem `complete` + `pdf.text` `failed`. No native-complete PDF. No OCR run. A locked-PDF probe without OCR produced the same version lie (`pdf.text` / `0.2.0`).

OCR **success** is fine: three runs, event types `extraction`, `extraction`, `OCR`. The mixed-corpus test still counts only `event_type = 'extraction'` against `len(run_ids)` and would fail if OCR were in that fixture.

### 3. Eviction 2b overwrites status with the dataless run alone

P5’s own test (`test_p5_dataless_result.py`) states the map must be `{filesystem: complete, native: dataless}` when both runs are passed to `extraction_status_by_tier`. The orchestrator passes **only** the dataless run.

Hashed-then-evicted (same size/mtime, P3 `dataless=True`, policy agrees):

| | Before | After |
|---|---|---|
| Status | `{filesystem: complete, native: complete}` | **`{native: dataless}`** |
| `dataless` runs | 0 | 1 (`format.unrouted`, `observation_count == 0`) |
| `bundle_counts.runs_dataless` | 0 | 1 |
| Routing rows for that file | 1 | 1 (2b calls `route()` again and does not record it) |

Done-means 3’s **run** contract holds. The status projection does not. Eviction bundle: `files_indexed == 2`, `files_with_any_run == 1` (`keep.md` is in the bundle with no runs — defect 1 again).

**No `tests/wave2` fixture for this.** First-sight still holds when probed: 0 `files`, 1 detection, 0 runs. Also untested at the caller.

### 4. P3’s dataless bit and P5’s `SafetyPolicy.is_dataless` are not the same gate

Wave2 `go()` still defaults the policy to `is_dataless=lambda path: False`. Eviction **and** size change (`RECOMPUTE`) with that default: native extractor ran again (`text.structured` `complete` — a real iCloud file would download) **and** 2b still wrote `dataless`. Two native outcomes for one file. Status after 2b is `{native: dataless}`.

The orchestrator is the only place that sees both predicates. It does not wire them.

### 5. `extract_filesystem` is outside the failed catcher

Patched to raise. Scan crashed. No `failed` run. Normal `admit()` only raises the two refusals, so a typical corpus will not hit this. A missing `files` column would.

### 6. Two in-flight scans of one root are both accepted

`start_scan_run` twice on the same selection: two ids, no refusal. 11 §7 is still unowned (18-wave2 OQ1: P3’s). Not an orchestrator claim and not implemented.

---

## P4 and P5 as packages

Not the problem. Re-checked, not reopened:

| Property | Live |
|---|---|
| Fingerprint | P5 `fingerprint` delegates to P4 `config_fingerprint` |
| Stopped run | `format.unrouted` / `native`. `.dmg` mixed-corpus status `native=metadata_only` |
| D10 | Collapse on `ExtractionResult` |
| One event writer | `RunWriter.write` ends with `record_run_event` |
| Empty `raw_value` | Builder calls P4 `check_non_empty` |
| P5 skeleton | Writes through real `RunWriter`, not `RecordingSink` |
| OCR name | `apple-vision` → `ocr.apple_vision` |
| `Dispatched` invariant | Signals may ride with exactly one result (stops the filesystem-keying bug from coming back) |
| `current_versions()` | Seven names. OCR absent on purpose (provider-reported) |
| Ceilings | P1 publishes **16** keys including `evidence.context_window`. P5 names four of them and stores none |
| Readers | Still injected. The skeleton proves the seam, not Apple Vision or `pypdf` |
| `.pages` / `.swift` | `unsupported`. Spec-faithful |

`UnknownFamily` (router/handler drift) is a plain `Exception`, so the orchestrator would record it as that **file’s** `failed` run — the same swallow `ContractViolation` was added to stop, for a defect that is about the call, not the bytes.

---

## P1–P3 (the rest of the live tree)

| Check | Live |
|---|---|
| Identity | 64-hex `content_hash`, no `sha256:` prefix, on the mixed path |
| Column | `current_path`. Caller uses it |
| `files.sensitivity_state` | Column exists. **Nothing writes it** (file 22 §3). Until Joseph decides the four-home question, passing `None` at the bundle is the standing rule |
| P3 first-sight iCloud | No `files` row. Detection only |
| P3 hashed-then-evicted | Cache verdict recorded, hashing skipped. Caller 2b is what emits C4’s run |
| Protected `.app` | P3 excludes the subtree. Mixed corpus: no `sheet.numbers` row |
| 11 §7 two scans / one root | Unowned. Both `start_scan_run` calls succeed |
| P2 counts | `runs_dataless` exists and fills when the caller writes the run |

P6–P13 unbuilt. File 22 is the seam contract for attaching them; it is not a claim that Wave 2 is finished.

---

## What the 26 wave2 tests still do not see

- Done-means 3 (eviction + first-sight)
- REUSE scan’s bundle contents
- Two selections sharing `files`
- OCR failure preserving the PDF run
- `failed` `extractor_version` vs the extractor
- `add_extraction_output`
- P3/P5 dataless predicate split

`test_the_sensitivity_signals_reach_the_database` asserts the table exists and that **if** rows exist their keys are non-empty. A fixture that raised nothing would still pass. The real lock is `test_a_sensitivity_signal_is_keyed_to_the_run_that_raised_it`.

---

## What “perfect” would still not include

A finished sorter. No facts, folders, LLM, privacy gate, grouping, placement, apply/undo, or review. No production readers. That is P6–P13 plus a chosen PDF/OCR library, not a P5 hole.

---

## What to do next

Caller, in the order that stops eval and §2.9 from lying about a **rescan**:

1. Bundle file entries = this scan’s roster. Runs / text units / outputs = **current** runs for those files, not only `written` this pass. Then a `REUSE` scan is evaluable and a second selection does not swallow the first.
2. `_extract_one` / `extract()`: keep the native result if OCR raises; `failed_result` version from the handler that failed. `UnknownFamily` should propagate like `ContractViolation`, not become a file’s `failed`.
3. 2b status = `{filesystem: complete, native: dataless}` (compose with the existing filesystem run). Add the done-means 3 fixture file 18 required.
4. Wire `SafetyPolicy.is_dataless` to the observation P3 already made, or `RECOMPUTE` will download.

Then P6, against file 22, not against a reconstructed stub. Do not start P6 as a substitute for (1)–(4).
