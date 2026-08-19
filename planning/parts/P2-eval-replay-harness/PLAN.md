# P2 — Evaluation and Replay Harness — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the machinery §8.5 requires before the stages it measures exist — the replay bundle, the stage-output envelope, the run manifest, the per-stage assertion record with its seven verdicts, earliest-divergence attribution, the run-to-run comparison record with no aggregate accuracy anywhere in it, shadow mode, and the twelve-case adversarial suite.

**Architecture:** P2's tables live in P1's single local SQLite database (§0: *"Each part owns its own tables within it"*), created by P2's own `create_eval_schema` — **P1's `db.py` is not modified**. Thirteen modules, one per published surface in [`SPEC.md`](SPEC.md)'s Contract out plus the runner that ties them together. Nine of the ten measured stages do not exist; every one of them is reached through a **stage adapter registry**, and a stage with no adapter yields `outcome = not_implemented`, which is a legal run, not a failure. That registry is why every task below is independently testable with nothing but P1 and fixtures on disk.

**Tech Stack:** Python 3.12 · stdlib `sqlite3`, `json`, `hashlib` · `pytest` · no third-party runtime dependencies · P1's `database_agent` package as the substrate.

---

## Global Constraints

Every task's requirements implicitly include these. Values are copied verbatim from [`SPEC.md`](SPEC.md) and from [`../../01-product-design-structured.md`](../../01-product-design-structured.md).

- **P2 asserts on outcomes. It does not repair them, does not re-rank, and does not feed its verdicts back into any live decision path** (SPEC, *Design slice owned*).
- **No aggregate accuracy scalar exists anywhere in the output** — bundle, run, assertion, comparison, or rendered report (§8.5: *"A single overall 'accuracy' number hides the mechanism that needs repair."*). Done-means 3 makes this a negative acceptance test, enforced in Task 16 over every P2 column and every key of every P2 reader's return value.
- **`deferred` is never `divergent`** (§8.6: *"cost exhaustion must never turn into lower-quality automatic classification"*). Scoring a budget deferral as a quality failure creates exactly the pressure §8.6 forbids.
- **`abstained_correctly` is a passing verdict** (§6.10: *"correct abstention is a successful outcome"*), reported as a pass and never as a miss.
- **P2 appends no `events` row.** SPEC Cross-cutting answers → Provenance: *"P2 appends no file-level provenance event."* P2 writes only its own run-scoped tables. `src/eval_harness/` never imports `append_event`; Task 16 asserts it. Every model call a replay, shadow or adversarial run makes appends a consent-aware audit record **through P7** — P2 requires that record and links to it, and writes none of it.
- **Never DELETE from `events`.** P2 never touches that table at all. The immutability triggers written in Task 5 are on P2's own bundle tables. I6 (tombstone versus append) is deferred to P7 and nothing here forecloses it.
- **P2 defines no other part's vocabulary.** The observation shape (P4), any stage's payload (P5/P6/P8/P9/P10/P11), handling classes and operation modes (P7), the correction record (§8.7), the plan version object (P10), the mutation transaction (P12) are **read and stored opaquely**. Where a neighbour's closed vocabulary is needed for a comparison, P2 stores the string it was handed and compares by value — it does not copy the neighbour's enum into its own source. The one closed vocabulary P2 *does* carry beyond its own is `analysis_tiers_enabled[] ⊆ filesystem | native | ocr | llm`, because SPEC Contract out §5 prints those four inside P2's own `run_manifest` record and [`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md) ratifies them as binding.
- **No thresholds.** §8.5 states no pass threshold, target rate, or regression tolerance for any dimension (SPEC Open question 2, **left open**). Value comparison is exact equality over canonical JSON. There is no tolerance parameter, no score, no rounding, and §6.10's two-condition rule is **not** borrowed as an eval threshold.
- **No ceiling numbers.** §8.6's ceilings are configurable and hand-authored. P2 holds **keys**, never values: a run snapshots whatever `database_agent.budget.all_ceilings` returns. Any number appearing in a test below is a fixture value chosen to make a comparison observable, exactly as P1's `tests/test_budget.py` does, and is not a design value.
- **P2 fills no expectation.** SPEC *Deferred*: the hand-labelled reference corpus, the 200–300 domain template library, gazetteer contents, domain fact-schema fields beyond §3.11's literal table, and residual-library contents beyond §7.3's nine names are hand work. P2 publishes `bundle_expectation`; it does not author its contents. Task 16 asserts `src/eval_harness/` ships none.
- **A bundle is immutable once sealed**, and a rebuild is a **new** bundle with `supersedes_bundle_id` set — supersede, never overwrite (§8.2, §8.8).
- **A stage that does not exist is `not_implemented`, not an error** (`02-segmentation-map.md`, *Order*). A run in which nine stages report `not_implemented` is a valid run with `not_run` verdicts, and the adversarial gate reports `not_run` for such a case — **never `pass`**.
- **Python 3.12.** Pin it; do not assume a newer runtime. P1 already pins it in `pyproject.toml` and **P2 adds no pyproject change**: `[tool.setuptools.packages.find] where = ["src"]` finds `eval_harness` and `testpaths = ["tests"]` collects `tests/eval/`.

---

## Dependency on P1

P2 is built on P1's substrate and on nothing else. The surfaces consumed, all from [`../P1-storage-identity-provenance/PLAN.md`](../P1-storage-identity-provenance/PLAN.md)'s *Produces* lines:

| P1 surface | Used by | For |
|---|---|---|
| `database_agent.db.open_database(path, *, scan_roots=())` | every task | the one local database (§0) |
| `database_agent.db.transaction(conn)` | Tasks 5–8 | bundle build atomicity |
| `database_agent.db.create_schema(conn)` | Tasks 7, 17 | `files` and `events` must exist before P1's learning projection is readable |
| `database_agent.budget.all_ceilings(conn)`, `CEILING_KEYS` | Task 4 | the §8.6 ceiling set a run was given |
| `database_agent.learning.learning_records(conn, scope, subject_id)`, `SCOPES` | Task 7 | the §8.7 rows a bundle must carry |
| `database_agent.files_table.observe_path(...)`, `database_agent.events.append_event(...)` | Task 17 only | the skeleton's P1/P3 step, authored by a P3 fixture |

**P1 must be green before Task 1 starts.** Run `pytest tests/ -q` and confirm P1's suite passes; P2's first import failure otherwise reads as a P2 defect when it is a missing substrate.

**P2 does not modify any P1 file.** Not `db.py`, not `pyproject.toml`, not `tests/conftest.py`. P2's schema function is its own, its fixtures live in `tests/eval/conftest.py`, and its tests live in `tests/eval/` so that P1's `tests/conftest.py` stays untouched.

---

## File Structure

```text
src/eval_harness/__init__.py            package marker; exports the run entry points
src/eval_harness/store.py               every P2 table + create_eval_schema; P1's db.py untouched
src/eval_harness/vocabulary.py          Contract out §1, §2 — ten stages, ten dimensions, kept apart
src/eval_harness/bundle.py              Contract out §3 — the replay bundle, sealed and superseded
src/eval_harness/stage_output.py        Contract out §4 — the envelope every measured part emits
src/eval_harness/run.py                 Contract out §5 — run manifest, version tuple, run settings
src/eval_harness/replay.py              the stage adapter registry and the replay runner
src/eval_harness/assertions.py          Contract out §6 — the per-stage assertion record
src/eval_harness/attribution.py         Contract out §6 — attributed_stage over inputs[]
src/eval_harness/comparison.py          Contract out §7 — the comparison record, never collapsed
src/eval_harness/shadow.py              Contract out §8 — shadow mode and its three empty proofs
src/eval_harness/adversarial.py         Contract out §9 — A1–A12 as a gate, never a silent pass
src/eval_harness/counts.py              §8.6's count line, from the bundle alone

tests/eval/conftest.py                  eval_conn, sealed-bundle helpers
tests/eval/fixtures/p4_runs.json        recorded P4 `extraction_runs` rows (P4 does not exist yet)
tests/eval/fixtures/p4_text_units.json  recorded P4 `text_units` rows
tests/eval/fixtures/adversarial/A1..A12 twelve case files: expected + forbidden + the § that states it
tests/eval/test_store.py                schema, idempotence, P1 tables untouched
tests/eval/test_vocabulary.py           Done-means 2; SPEC OQ1 left open and asserted as open
tests/eval/test_bundle.py               Done-means 1
tests/eval/test_bundle_extraction.py    Done-means 1, 13 input
tests/eval/test_bundle_learning.py      10-i4-learning-ops.md's P2 clause
tests/eval/test_bundle_expectation.py   Done-means 12
tests/eval/test_stage_output.py         Contract out §4
tests/eval/test_run.py                  Contract out §5
tests/eval/test_replay.py               Done-means 7
tests/eval/test_assertions.py           Done-means 2, 5, 6
tests/eval/test_attribution.py          Done-means 4
tests/eval/test_comparison.py           Done-means 6, 8
tests/eval/test_shadow.py               Done-means 9
tests/eval/test_adversarial.py          Done-means 10
tests/eval/test_counts.py               Done-means 13
tests/eval/test_no_aggregate.py         Done-means 3 + the vocabulary and authorship guards
tests/eval/test_skeleton_p2_step.py     Done-means 11
```

Files split by published surface, not by technical layer — each module is one Contract-out section, so a reviewer can reject one without touching its neighbours.

---
