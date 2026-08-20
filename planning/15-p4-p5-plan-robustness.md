# P4 and P5 plan robustness

Date: 2026-08-20
Status: **P4 is almost freeze-ready; P5 is a shape-correct extractor package, not a working reader.** Do not execute them as a stack against each other until three named seams are closed. They connect to shipped P1–P3 on paper and, with those fixes, in code.
Scope: live P4 PLAN (6943 lines, 19 tasks) and P5 PLAN (9415 lines, 21 tasks) against live SPECs, shipped `src/database_agent/`, `src/eval_harness/`, `src/scan_agent/`, [`11-ops-runtime.md`](11-ops-runtime.md), [`02-segmentation-map.md`](02-segmentation-map.md).
Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md)

Neither package is in the repo yet. Self-reviews claim assembled pytest (P4: 349; P5: 272; combined with P1–P3: 811). Those numbers were not re-run here.

---

## Verdict

| | P4 evidence shape | P5 extractors |
|---|---|---|
| What it actually is | Schema, vocabularies, locator, `observation_key`, conformance, fixtures. Opens no file. | Six extractor *families* that emit P4 records through an injected sink and injected format readers. Stdlib only. No PDF/DOCX/OCR library. |
| Against shipped P1 | Strong. Written against `src/database_agent/` as built, not P1 PLAN.md. `mark_superseded` reused via a generated `record_id` column. Authorship is M8-correct: P4 authors no event. | Strong on the `files` row and `append_event`. Does not re-hash, does not re-stat. Safety gate matches 11 §4b / §5. |
| Against shipped P2 | Intentional: `observation_key` excludes extractor version; P2's bundle keys *include* it. That is MINOR 8, already in P2 SPEC. Completeness eight-set already used in `eval_harness.counts`. | Task 17 maps P4 completeness → P2 `StageResult` against live `OUTCOMES` / `BUDGET_STATES`. Production module imports no `eval_harness`. Mapping of `metadata_only` and `unreadable` → `abstained` is still NEEDS JOSEPH. |
| Against shipped P3 | Skeleton hangs one observation off a real `files` row via `observe_path`. | O5 re-emits P3's row as `source_type: filesystem`. Does not recompute the ten fields. Protected-container and dataless gates refuse work P3 already refused. |
| Execute? | **Yes, Tasks 1–19**, after finding 1 (OQ2) is implemented as the *closed* SPEC, not as an open question. | **After P4 is in `src/evidence_shape/`**, Tasks 1–21, after findings 2–4. Do not treat the `p4_stub` as the connection to P4. |

A later part can be built against P4's fixtures with no extractor present — that is the point of the split, and the plans honour it. What they do not yet honour is *one* identity of an observation across two live copies, *one* event writer for a run, and *one* Python package name.

---

## What is actually good

Do not re-open these.

- Shape precedes extractors. P4 runs no reader; P5 invents no second observation record.
- Closed vocabularies, fail-not-coerce conformance, RAW-1 on code points, locator escaping, supersede-never-overwrite, D10 collapsing.
- P5 injects every real library. That is why this plan can be green in stdlib and still be honest that v1 PDF/HEIC/OCR is a Joseph choice.
- P5 holds SPEC OQ1 (threshold), OQ2 (CSV/PDF listed twice), OQ4–OQ8 open with introspection guards, not source-text greps.
- P4/P5 both refuse to invent ceilings, gazetteers, date regexes, handling classes, facts.
- P2 is already the consumer these SPECs describe: `bundle_extraction_run`, `bundle_text_unit`, `observation_key` on assertions, completeness → §8.6 counts.
- P1 `HASH_ALGORITHM = "sha256"` and P4's key formula agree. P4 Task 19 copies `get_file()["content_hash"]` (64 hex, no prefix) onto the observation — the live join works even though fixture strings in earlier tasks are `"sha256:abc"`.
- Known gaps are named: no orchestrator, no `files.extraction_status_by_tier` writer, five zones with no fixture, context budget not a P1 ceiling, Graphify unpaid.

---

## The blockers

Same defect class as yesterday's P3 Task 3: a plan that is internally consistent and implements a **superseded** decision.

### 1. P4 OQ2 is closed in the SPEC and still open in the PLAN — **blocking P4 Task 2 / Task 15, and P5 re-extraction**

P4 SPEC OQ2, ratified 2026-08-20: **the content hash owns the observation.** Two `files` rows with the same hash share one observation set; a fact derived on one applies to the other; P5 re-extracts per content version, not per path; P6 attaches facts to the hash; P11's multi-home file has one evidence set.

P4 PLAN Task 2 still puts OQ2 in `OPEN_QUESTIONS` and guards it so that answering it in code fails. Self-review: Task 15 "takes no position" by keeping `file_id` in the compared digest. That is the open reading.

If you execute the PLAN as written, two live copies (P1 I1, already shipped) each get their own observation set, P5 will re-extract the same bytes, and P6 will have two fact homes for one version. The SPEC just forbade that.

The SPEC page also still carries the *old* "Unsettled:" paragraph under the settlement. Delete it. Do not freeze a page that says both.

**Fix:** drop OQ2 from `OPEN_QUESTIONS`. Key store reads and the compared set on `content_hash`. Keep `file_id` as §2.8's way in (which copy we happened to open), not as owner. P5 Task 5 cache key is already per content version — align P4 to that, don't reopen P5.

### 2. P5's "when P4 ships" import is the wrong package — **blocking the stub swap**

P4 publishes `src/evidence_shape/` (`observation.py`, `conformance.py`, `locator.py`, …).

P5 header and Task 2: when P4 lands, delete `p4_stub.py` and `from evidence.records import …` / `from evidence.conformance import validate_observation`.

That module path does not exist in the P4 PLAN. Production `extractors/` talks to an injected `EvidenceSink` (good — those modules need not change). Every test file that imports `p4_stub` as a top-level module will not switch by search-replace onto `evidence_shape`.

**Fix:** write the swap now: `from evidence_shape.observation import …`, `from evidence_shape.conformance import validate_observation`, `from evidence_shape.locator import serialize_locator`. Prefer sequential build: P4 first, then P5 against the real package, stub never merged. Two locator implementations is the drift §2.8 exists to prevent.

### 3. Two writers for one `extraction` / `OCR` event — **blocking P5 Tasks 16 and 21 once P4 exists**

P4 Task 10: `record_run_event(conn, run_id, *, author)` appends the one §8.2 event after observations exist, explanation = `run_id` + `observation_key`s. P5 is the author; P4 is the writer. Correct.

P5 Task 16 / 21: `extractors.events.append` / `extraction_event` also call P1's `append_event`. The skeleton uses P5's path because P4 "has not landed."

If both ship, a run either gets two events or one dead API. M8 cannot survive two helpers.

**Fix:** P5's event module becomes a thin call to `evidence_shape.store.record_run_event(..., author="P5")` the day P4 lands. Delete the parallel payload builder, or make it produce the dict P4 already builds.

### 4. P4 fixture 19 vs conformance rule 9 on `metadata_only` — **blocking P5 Task 6**

P5 already reported this and picked fixture 19: `metadata_only` run carries **zero** observations; the filesystem run indexes the file.

P4 conformance rule 9's note says `metadata_only` runs *likewise carry* the metadata-level rows.

Both cannot be the gate six extractors run. Freeze one sentence in the P4 SPEC before P5 Task 6. P5's choice (filesystem run carries them) is the one that keeps `complete`-with-zero / `unsupported` / `metadata_only` distinguishable.

---

## Connects, with holes — not blockers for P4 itself

| Seam | Status |
|---|---|
| P1 `files` + `events` | P4/P5 write through P1. Generated `record_id` adapter is the right way to reuse `mark_superseded` without renaming `observation_id`. |
| P1 `content_hash` is 64 hex, `hash_algorithm` is a sibling column | P4 SPEC JSON shows `"sha256:…"`. Fixtures use that. Live skeleton copies P1's hex. **Document the stored form as P1's hex.** Prefix belongs on `observation_key` / `config_fingerprint` output, not on `evidence.content_hash`, or P2 bundles (hex) will not join P4 rows. |
| P1 `files.extraction_status_by_tier` | P5 Task 5 *computes* the map. P1 has no setter. Column stays `{}` after a real extract unless someone writes it. Named gap. Either P1 grows a writer P5 calls, or P13 reads `extraction_runs` and this column is dropped from the file record's live meaning. |
| P3 scan → P5 extract | **No function connects them.** P3 `scan()` returns `scan_run_id` and stops. P5 has no `extract_file`. Stat-cache "do not re-extract" lives in P3's SPEC contract-in and is unenforced. Task 21 sequences by hand. Honest. Wave 2 skeleton is three tests, not one path. |
| P3 `detected_format` | Often null (P3 Q6 open). P5 router has its own `extraction_routing.detected_format`. Two homes unless something copies back. |
| P2 stage envelope | Completeness → outcome table is P5's to author. `deferred`+`ceiling_reached` matches live P2 writer. `metadata_only`/`unreadable` → `abstained` still Joseph. Task 17 `start_run(bundle_id="b-p5")` works because `run_manifest.bundle_id` has **no FK** — a dangling id, not a bundle. Fine for a unit test; not a capture-from-scan. |
| P6 `no_usable_facts` | Injected, no default. Correct. OCR trigger cannot run "for real" until P6. |
| P7 privacy / speech-to-text | Injected. Sensitivity signal is keyed by **batch position**, not `observation_key` (P5 known gap). That will not survive P7 redaction. |
| Orchestrator / P13 | Unowned. Same class as 11 §7 (two scans, same root). |
| Graphify | Standing rule in `02` still unpaid. |

---

## Robust enough?

**As contracts:** yes, with finding 1 and 4 frozen. This is the most depended-on seam in the map, and the plans treat it that way: one shape, twelve rules, no per-format consumer branch.

**As a walking skeleton through Wave 2:** not yet. P4 fixture 1 + P5 Task 21 + P3 scan + P2 replay are four stories. Nobody captures P5's `extraction_runs` into a P2 bundle. Nobody calls P5 after P3. That is acceptable *if* you do not claim the Wave 2 skeleton is one test.

**As v1 extraction on a Mac:** no. Every reader is a parameter. HEIC, Apple Vision, PDF libraries, libmagic are NEEDS JOSEPH. Executing P5 gives you a router, O5 filesystem observations, and a place to plug `pypdf`. It does not read a syllabus PDF.

**P5 OQ numbering is a trap.** Header "P5 OQ1/OQ2 closed" means Location structured and OCR fields on `extraction_runs` (04/05 resolutions). SPEC OQ1/OQ2 still open means the facts-threshold and CSV/PDF double-listing. Implementers will "close OQ1" and ship a threshold. Rename in the PLAN header: "resolutions Location / OCR-home closed; SPEC OQ1–OQ8 except OQ3 remain."

---

## Execute?

| Document | Execute? |
|---|---|
| P4 PLAN Tasks 1–19 | **Yes**, after OQ2 is implemented as closed (hash owns the set) and rule 9 / fixture 19 agree on `metadata_only`. |
| P5 PLAN Tasks 1–21 against `p4_stub` in parallel with P4 | **No.** Two locators. Wrong import path on swap. |
| P5 PLAN after `evidence_shape` is green | **Yes**, with P5 events going through P4's `record_run_event`, stub deleted, `sqlite3.Row` accepted where P1 returns one. |
| "We can extract PDFs now" | **No**, until a reader is chosen and wired. |
| P6 against P4 fixtures | **Yes**, after P4 Task 16. That is Done-means 9's P4 half. Do not wait for P5. |

Edit order: (1) P4 SPEC OQ2 leftover paragraph + PLAN `OPEN_QUESTIONS` + compared-set owner. (2) P4 SPEC rule 9 vs fixture 19. (3) P4 Tasks 1–19. (4) P5 import path + event writer + Row mapping. (5) P5 Tasks 1–21. (6) A caller — even a test — that does P3 `scan` → P5 extract → P4 store → P2 bundle with `source_scan_ref = scan_run_id`. That last item is not in either plan and is what "connects with P1, P2, P3" actually means.

Then Graphify, then Joseph on libraries, context-ceiling key, and the two P2 outcome rows.
