# P2 and P3 plan robustness

Date: 2026-08-19
Status: **wave-1 plans are complete TDD packages; do not execute until P1's rewritten substrate is green, and do not treat either plan as perfect**
Scope: live [`parts/P2-eval-replay-harness/PLAN.md`](parts/P2-eval-replay-harness/PLAN.md) (17 tasks, frozen ~17:37) and [`parts/P3-scan-corpus-selection/PLAN.md`](parts/P3-scan-corpus-selection/PLAN.md) (18 tasks, frozen ~17:40) against their SPECs, [`01-product-design-structured.md`](01-product-design-structured.md) §1.1 / §1.2 / §8.5, [`02-segmentation-map.md`](02-segmentation-map.md), [`10-i4-learning-ops.md`](10-i4-learning-ops.md), [`11-ops-runtime.md`](11-ops-runtime.md), and the rewritten P1 plan. Earlier draft of this pass was discarded because both PLANs were still being written.
Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md)

These two plans were written after [`12-p1-plan-robustness.md`](12-p1-plan-robustness.md) and after P1's PLAN was rewritten to match it. They assume that rewritten P1, not the P1 plan 12 judged.

**Verdict.** Neither plan is perfect. Both are substantially more disciplined than the P1 plan 12 reviewed: open questions are held open by tests, not comments; authorship is treated as load-bearing; no neighbour's vocabulary is retyped. P2 is the stronger of the two as a self-contained harness. P3 is the stronger as a contract-with-P1. The wave as a whole still has three seams that will poison later parts if executed as written: unpublished scan identity, P1 re-deriving P3's fields, and a shadow "empty" proof that only checks P2's own columns.

| | P2 | P3 |
|---|---|---|
| Tasks | 17, plus Self-Review | 18, plus Self-Review |
| Done-means in SPEC | 13 | 18 |
| Done-means with a task | 13 / 13 | 18 / 18 |
| Open questions held open by a mechanism | 12 / 12 | 14 / 14 remaining |
| Must not execute before | P1 rewritten plan is green | P1 rewritten plan is green **and** P1 stops re-deriving R2 fields |
| Graphify path-check | absent | absent |

A plan is robust here if a later part can be built against it without inheriting a foreign-key lie, a provenance lie, or a silently answered open question. Completeness of pytest steps is not the test.

---

## Wave 1 as a unit

```
P1 (rewritten substrate) → P2 (harness) → P3 (scan)
```

That order is forced by the structure map: per-stage measurement cannot be retrofitted, and P3 must be runnable against a P2 bundle. Both later plans are honest about depending on P1 alone for their own tests. The remaining wave defects sit *between* the three, not inside any one task list.

| Seam | What each plan does | Why it is a wave defect |
|---|---|---|
| Scan identity | P1 mints `scan_id` on `scan_resource_usage` and keeps it off `events` (OQ19). P3 has a local `scan_run_id`, unpublished, and **forbids** importing `database_agent.scan_usage`. P2 stores `source_scan_ref` and comments it as *"P3's scan_id (§1.1)"*. [`11`](11-ops-runtime.md) §3 already writes `scan_run_id — P3's scan` on the session record as if it were published. | P13 cannot join file counts to resource counters. A P2 bundle cannot name the scan it was captured from. Three documents, three identities, none joined. P3 records this as OQ16 held open; P2's comment treats it as closed. |
| Who computes the ten §1.2 fields | P3 SPEC: P3 computes them once; a second derivation is a contract violation (O5, Done-means 17). P3 PLAN: `observe_path` hands a path; P1's `record_file` stats and hashes it. Drift test compares `os.stat` to the stored row, which both computers read from the same path, so it **passes while the contract is violated**. | §3.4's cache key is built on the hash. Two computers of MIME, timestamps, and hash from the same path will drift the first time they disagree (symlink, dataless race, clock). P3 owns none of P1's files and correctly refuses to patch P1. Do not execute P3 Task 10 until P1's `record_file` stores what P3 observed. |
| Authorship of scan events | Structure map and both SPECs: P3 authors, P1 writes. Rewritten P1 takes `author=` and tests it. P3 supplies `author="P3"` everywhere and guards a second route. P2's skeleton uses a P3 fixture as author. | This seam is **recovered**. It was B1 in 12. Do not re-litigate it. |
| Replay without a live filesystem | P2 deletes the source file before replay (Task 17). P3 serializes listings and re-fires exclusion rules (Task 15). A metadata-safe P3 replay writes **no** `files` row, because P1 has no "record from a supplied hash" entry point. | Done-means 14's exclusion/cache/curation half holds. The `files` half of a metadata-safe bundle cannot round-trip through P1. Recorded, not papered. Needs a P1 surface or a SPEC narrowing before P2's `metadata_safe` form can populate identity. |

**Graphify.** The structure map's standing rule still has no home in either plan: no `graphify-out/`, no hook, no `graphify path` before code. This pass is again the 6,000-line read the map forbids. Same miss as 12.

---

## P2 — Evaluation and replay harness

**Judgment:** robust as a harness that must exist before the stages it measures. Not perfect. Executable after rewritten P1 is green, with the scan-identity comment treated as a fixture string and not as a published P3 id.

### What holds

| What | Evidence |
|---|---|
| Stages and dimensions kept apart | No `STAGE_FOR_DIMENSION`. OQ1 held by a test that fails if one is added. |
| `not_implemented` is a legal run | Adapter registry is an argument, not a process-local dict. Nine absent stages yield `not_run`, never `pass`. Learned the P1 registry lesson. |
| No aggregate accuracy | Column names, return keys, and identifier parts all guarded (Task 16). `GateReport` has no `passed` boolean. |
| Abstention is a pass; deferral is not divergence | `PASSING_VERDICTS = {match, abstained_correctly}`. Ceiling-only change produces zero new divergences. |
| Open questions held by mechanism | All twelve have a named refusal: no export, no tolerance argument, no shadow selector default, no promotion function, `run_gate` raises nothing. |
| Learning rows in the bundle | Task 7 captures P1's store so a store-empty replay cannot be blamed on grouping. Binding from 10. |
| Adversarial gate does not silently pass | A1–A8, A10–A12 are `not_run` until their stage exists. Only A9 can pass today, from the bundle alone. |
| P2 authors no `events` | `src/eval_harness/` must not import `append_event`. Tests that seed P1 (Task 7) do so as P9 fixtures, which is correct M8. |
| No neighbour enums retyped | Handling class, privacy mode, residual `outcome` stored opaque. Known gap: a typo is not caught. Correct trade. |
| Skeleton deletes the file before replay | Done-means 1 is asserted, not assumed. |

### Do not treat as closed

| ID | Where | What | Risk |
|---|---|---|---|
| **P2-A** | Task 5 comment on `source_scan_ref` | Comment calls the fixture string "P3's scan_id". P3 OQ16 and P3 Task 3 publish nothing. | Later capture code will write a local handle into a field P13/P2 think is shared identity. |
| **P2-B** | Task 13 `assert_shadow_wrote_nothing` | `plan_version_writes` / `move_plan_entries` / `user_visible_tree_delta` default to `'[]'` on P2's own `shadow_run` row. The check never looks at P10 or P12 tables. | The day a shadow adapter writes a real plan version, this assertion still passes unless the adapter also copies into those three columns. The "proved not promised" claim is self-referential. |
| **P2-C** | Task 14 `run_gate` | Returns a report. Raises nothing. OQ9 left open on purpose. | §8.5's "before it affects a user's live plan" has no enforcer. Fine as a SPEC deferral; not fine if anyone reads the gate as a ship block. |
| **P2-D** | Attribution `inputs[]` | Bare `subject_ref`s; two stages on one subject both match. Recorded, SPEC not changed. | Earliest-divergence can name the wrong stage when P9 and P11 both decided about the same file. |
| **P2-E** | "Files indexed" | Contract-out §3 and P5's mapping disagree. `bundle_counts` returns both and picks neither. | P13 will pick one. Pick in the SPEC before a renderer exists. |
| **P2-F** | P2's own §8.6 ceilings | Bundle count, bundle storage, adversarial wall-clock named in SPEC, not implemented. Adding a key requires editing P1's `CEILING_KEYS`. | A snapshot bundle of a real Downloads folder has no size cap. Same class of hole as P1 OQ15 / P3 Q15. |
| **P2-G** | `outcome = error` / `not-applicable` | NULL verdict, counted as `unverdicted`. No eighth name minted. | Honest. Neighbouring assertion dashboards will treat NULL as a bug unless the SPEC is updated. |

OQ4 (`tree` as assertion vs observation) is held open by doing nothing special. That means a bundle replay will emit pass/fail verdicts on a dimension §8.5 phrased as user behaviour. The plan says it does not decide whether those verdicts are meaningful. A later P10 will inherit fake tree-quality scores unless P2 or P10 special-cases it when the SPEC closes.

### Execute?

Yes, Tasks 1–17, **after** rewritten P1 is green. Do not wire `source_scan_ref` to P3's local handle. Do not treat Task 13's three empties as a substitute for "shadow adapters must not call P10/P12". Do not treat `run_gate` as a release block.

---

## P3 — Scan and corpus selection

**Judgment:** the authorship half of wave 1 is now actually specified. The plan is the right shape (pure `walk`, separate writer, caller-supplied MIME/scan_state/budget, ops-runtime bound). It is not executable as a faithful O5 implementation until P1 stores P3's observations instead of re-statting the path. It is not perfect.

### What holds

| What | Evidence |
|---|---|
| P3 authors, P1 writes | `event_defaults` is the only place `subsystem` is set; refuses any value but `"P3"`; refuses a type P3 does not author. Task 17 guards a second route. Matches the structure map's rewritten skeleton line. |
| Registers nothing | Four reserved §8.2 names. No `register_event_type`. B5. |
| No invented thresholds | Eleven literal directory names and four marker files only. Five open-ended categories deferred. Curation signal is `undetermined` until a threshold is authored. Budget is a caller predicate with no default. |
| Q4 / Q6 held open | `scan_state` and `mime_type_for` are required keywords. No `mimetypes`, no signature table, no scan-state enum in `scan_agent`. |
| `cross_folder_moves` recorded, not enforced | Q12 guarded. |
| Exclusion verdicts are not events | Own table; Q13 named. Replay can still reproduce the boundary. |
| Dataless before hashing | Detects `SF_DATALESS`; never passes `materialized=True` for it; writes no `extraction_runs` row (P4 OQ6 left to P4). |
| Full Disk Access | Lists the root; `PermissionError` is the oracle; no gazetteer of TCC paths. |
| Stat cache is a difference test | Size-or-mtime, including mtime moving backwards. Done-means 8 and 9 have tasks. |
| Session watch | `notify` implements 11 §4's four rules against a stdlib `poll`. No fake FSEvents. No daemon. Disappearance authors the event (11 wins over Q14 for the *event*); `files` row untouched (Q14's other half stays open). |
| Replay re-fires rules | Serializes listings, not conclusions. `node_modules` still excluded on replay. |
| Candidate roots are landscape | Exclusion + inventory, no `files` rows. Stated as a reading of §1.1, not as a SPEC sentence. Honest. |

### Do not execute these as written — or execute only after P1 changes

| ID | Where | What | Why it is blocking |
|---|---|---|---|
| **P3-A** | Task 10 / Done-means 17 | P1 `record_file` re-derives filename, normalized filename, extension, size, timestamps, hash. P3's drift test cannot fail that. | O5 says a second derivation is a contract violation. The plan reports the divergence for P1 to resolve and then proceeds to write through the violating API. Fix P1 first. |
| **P3-B** | Task 3 vs consume table vs 11 vs P2 | Header lists `database_agent.scan_usage.start_scan` as consumed. Task 3 asserts that import is absent. 11 treats `scan_run_id` as published. P2 comments `source_scan_ref` as P3's scan id. | The consume table is stale. The identity seam is the wave defect above. Do not "fix" it by joining in P3 code; close OQ16 in the SPEC. |
| **P3-C** | Q1 vs P1 NFC | P3 defines no normalization and guards it. P1's `record_file` already does `unicodedata.normalize("NFC", path.name)`. P3 reports this and does not ratify it. | §3.7 word-boundary matching runs over this string. A1/A2 (P2 adversarial) will fire on whatever P1 stored. The open question is already answered in another part's code. Close it in P3 SPEC or stop P1 from normalizing. |

### Serious, not blocking the skeleton

| ID | Where | What | Risk |
|---|---|---|---|
| **P3-D** | Q7 / known gap | `.app` bundles and packages are descended. SPEC names "thousands of spurious rows." Plan records rather than invents a rule. | A user who selects `/Applications` or a folder containing one `.app` will hash a corpus the product cannot mean to organize. Skeleton is fine; first real Mac scan is not. Needs a SPEC rule before v1, not a guessed heuristic in this plan. |
| **P3-E** | Task 6 known gap | Legacy `.Foo.pdf.icloud` placeholders are not detected. 11 §5 does not name that shape. | Optimize Mac Storage still has two on-disk forms. `SF_DATALESS` is the one 11 specified. Accept for this plan; do not invent the filename rule here. |
| **P3-F** | Task 15 | Metadata-safe replay writes no `files` row; R4 `file_id` is NULL. | Correct given P1. A P2 `metadata_safe` bundle cannot round-trip identity. |
| **P3-G** | Task 12 | Content change yields two P3-authored `external modification detection` rows (P3's stat difference and P1's version supersession). | Append-only and distinguishable by explanation. Fine if consumers filter; surprising if they count. |
| **P3-H** | Resource observability | P3 samples no `scan_resource_usage` counter, by OQ16. | A scan can run with P1's six counters stuck at unavailable. 11 and §8.6 wanted them observable. Closing OQ16 is what unsticks this, not a P3 invention of a thirteenth ceiling. |
| **P3-I** | Consume table | Lists `scan_usage` APIs P3 then forbids itself from importing. | Agent executing Task 1 will wire `start_scan` because the header said to. Delete those three lines from "What P3 consumes from P1" before anyone implements. |

Normalization of filename (Q1), timestamps (Q2), MIME (Q6), scan_state (Q4), hashing ceiling (Q15), exclusion override (Q8), R1 plan-versioning (Q11) are correctly not answered. Do not invent them to look finished.

### Execute?

Tasks 1–9, 11–14, 16–18 can proceed against rewritten P1. **Do not execute Task 10** (R2 write) until P1 accepts observed fields instead of re-statting. **Do not execute Task 15** as a claim that `files` round-trips from a metadata-safe bundle. Fix the consume-table stale lines before Task 1 so an implementer does not import `scan_usage`.

---

## Against the structure map

| Map rule | P2 | P3 |
|---|---|---|
| SPECs freeze, then plans | Both plans hold SPEC open questions open rather than answering them in code. Recovered from P1's earlier failure on I1/I2. | Same. Exception: P1's NFC silently answers P3 Q1. |
| Walking skeleton, deterministic | Task 17: one file, nine stages `not_run`, file deleted before replay, model and embeddings off. | Task 18: fixture directory, `node_modules` skipped, every event `subsystem="P3"`. |
| P2 before the stages it measures | Adapter registry with `not_implemented`. Correct. | n/a |
| P3 authors scan events | Skeleton uses a P3 fixture author. | Load-bearing rule of the whole plan. |
| Graphify path-check before code | Absent. | Absent. |
| Second privacy fixture (11, still no model) | Out of scope (P7/P8/P13). | Out of scope. Neither plan claims it. |

---

## Already sound — do not re-litigate

- Thirteen-part cut, P2-before-stages, P4-before-P5, P7-before-P8.
- No invented templates, gazetteers, domain fields, or numeric thresholds in either plan.
- `deferred` never scored as quality failure.
- Correct abstention is a pass.
- I6 (delete vs append-only) untouched; neither plan `DELETE`s from `events`.
- I4 four analysis tiers used only where P2's own `run_manifest` prints them.
- 11's dataless / FDA / no-daemon / crash-is-P12 rules are bound in P3 rather than ignored.
- P3 writing no `extraction_runs` / `completeness` (P4 OQ6) is correct refusal.
- P2 not rendering (P13 owns the eval view) is correct refusal.

---

## Edit order if you want wave 1 executable

Nothing below is a redesign.

| Order | Owner | Change | Unblocks |
|---|---|---|---|
| 1 | P1 | `record_file` / `observe_path` store the §1.2 fields P3 observed. Stop re-statting and re-hashing inside P1. Stop NFC-normalizing unless P3 SPEC closes Q1 that way. | P3 Task 10, O5, P3 Q1 |
| 2 | P3 SPEC + 11 + P2 | Close OQ16 or explicitly say the three ids stay distinct. If they stay distinct, delete P2's "P3's scan_id" comment and P3's consume-table `scan_usage` lines. If they join, P3 publishes and P1's `scan_id` is that value. | P13 progress line, P2 `source_scan_ref`, §8.6 observability |
| 3 | P2 Task 13 | `assert_shadow_wrote_nothing` must inspect P10/P12 tables (or a published "live writes" surface), not three columns P2 itself defaults to `[]`. | Done-means 9 as a real proof |
| 4 | P1 or P3 SPEC | Either P1 grows "record this hash without opening bytes" or P2/P3 SPEC says metadata-safe bundles do not round-trip `files`. | P2 `metadata_safe` identity |
| 5 | Lead | Graphify hook on the planning corpus; path-check `events.subsystem=P3` → P1 writer and `stage_output.stage_id` → P5/P6/P8/P9/P10/P11 before writing code. | Map standing rule |
| 6 | P3 SPEC, later | Q7: do not descend `.app` / packages. Skeleton does not need it; v1 does. | First real Mac scan |

Then: rewritten P1 green → P2 Tasks 1–17 → P3 Tasks 1–9 and 11–18 → P3 Task 10 last.
