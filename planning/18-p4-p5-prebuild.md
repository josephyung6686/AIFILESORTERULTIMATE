# P4 / P5 pre-build review

Date: 2026-08-20 (late)
Status: **Start P4. Do not start P5 until `from evidence_shape…` imports.** Follow task *tests and tuples*, not leftover prose.
Supersedes the execute-headline of [`16-p4-p5-catalogue-recheck.md`](16-p4-p5-catalogue-recheck.md) for the question “can we build now?”
Wave 1 this session: `python3 -m pytest tests -q` → **468 passed**.

Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md). Joseph’s 2026-08-20 answers live in the P4/P5 SPEC ratification tables. Those tables and the **test functions** win over Self-Review, Task intro prose, and NEEDS JOSEPH items that still ask already-answered questions.

---

## Go / no-go

| | Go? | Why |
|---|---|---|
| **P4 `src/evidence_shape/`** | **Yes.** Tasks 1–19. | Vocabularies, OQ2, nine completeness values, hash-owns-the-set, and Task 18’s `OPEN_QUESTIONS == {"OQ4"}` match the ratification table. |
| **P5 `src/extractors/`** | **Not yet.** After P4 is importable. | Plan is written for that order. Stub-swap already names `evidence_shape`. |
| **Catalogues** | Inject at P5/P6 *caller* time. Not a P4 dependency. | P5 PLAN now says so. Do not `import` under `src/extractors/`. |
| **End-to-end sorter on disk** | No | Still no scan→extract orchestrator. Green P4+P5 is a package pair, not a product run. |

**Reading rule for whoever executes P4:** if a paragraph and a test disagree, **the test is the contract.** Several intro blocks and the Self-Review were patched in the task bodies and not in the surrounding pages. That is the same defect class as file 16. It will not fail pytest if you type the tests; it *will* fail the product if you type the stale sentences.

Safer than a reading rule: strike the six stale paragraphs listed below (about twenty minutes), then Task 1. Do not re-plan the nineteen tasks.

---

## What is actually frozen (do not re-open, do not re-ask Joseph)

| Decision | Where it lives now |
|---|---|
| Observation identity = **content hash**, not `file_id` | P4 Task 15 compared set excludes `file_id`; Task 18 `test_oq2_ratified_…` |
| Completeness has **nine** values; ninth is `dataless` | P4 `COMPLETENESS`; P2 `runs_dataless` (shipped) |
| Zero observations: `unsupported`, `deferred`, `failed`, **`metadata_only`**, **`dataless`** | P4 Task 2 tuple **and** P5 Task 2 tuple (file 16 blocker 3 is **closed** in the tuples) |
| Rule 8 keys on **four** fields | `REPLAY_KEY_FIELDS`; A1 |
| One reliability vocab; extractors `direct` \| `possible` | C1; Task 18 `test_oq3_ratified_…` |
| User corrects **facts**, never `raw_value` | C3 |
| Context window = P1 16th key `evidence.context_window` + run `config` | **Shipped** in `src/database_agent/budget.py`; Task 18 asserts the key exists and P4 does not hard-code a length |
| XLSX/PPTX **ship at launch** | P5 SPEC B6 |
| Apple Vision, macOS v1 OCR | P5 SPEC B1 |
| OCR languages: English, CJK, Western European — in **run config**, not a P5 constant | P5 NEEDS JOSEPH #2 answered |
| Speech-to-text out of scope v1 | P5 NEEDS JOSEPH #7 answered |
| Catalogues: production caller loads JSON; tests use fixtures | P5 “Catalogue wiring” section |
| Archive marker **zone = `manifest`** | P5 E4 tests; P4 zone table. PLAN Task 12 historically said `metadata` — that is the bug |

OQ4 (handling-class granularity) stays open. P7 settles it. P4 must not grow a privacy column.

---

## Stale paragraphs that will ship the old world if followed

These are **not** reasons to delay P4. They are reasons to ignore those pages, or strike them first.

### P4 — follow the tests, not these sentences

1. **Task 2 intro** still says `ZERO_OBSERVATION_COMPLETENESS` is **three values, not five**, and that OQ3 is held open. The **tuple and tests six lines later** are five values and `OPEN_QUESTIONS = {OQ4}`.
2. **Task 14 intro** still says `metadata_only` **may and normally does** carry observations. The **test** `test_rule_9_a_metadata_only_run_carries_none` is the 2026-08-20 freeze (fixture 19). The helper `test_rule_9_the_three_zero_observation_states_*` still loops only three names; `metadata_only` / `dataless` have their own tests. Do not “fix” rule 9 by allowing observations on `metadata_only`.
3. **Self-Review “Every open question held open”** still says OQ2 keeps `file_id` in the digest, `COMPLETENESS` is eight, OQ6 has no ninth. **False.** Task 15 and Task 18 contradict it. If you implement from Self-Review you undo the ratification.
4. **Global Constraints “The context budget is caller-supplied”** still says P1 has fifteen keys and a sixteenth raises. **False.** P1 has sixteen; `evidence.context_window` exists. P4 still holds **no number** (correct). P5 reads the ceiling; P4 stores what arrives and fingerprints it via run `config`.
5. **NEEDS JOSEPH A1 / A3** still ask where the context budget lives and whether rule 8 includes extractor name. **Already ratified** (B4, A1). Do not stop and re-ask.

### P5 — do not start yet; when you do, ignore these

6. **NEEDS JOSEPH #6** still recommends marking spreadsheets/presentations `unsupported` for v1. **SPEC B6 is ship `openpyxl` / `python-pptx` at launch.** Injected readers stay (correct). A deployment with no reader is non-conforming, not “deferred by choice.”
7. **Task 3 comment** says the **router (Task 4)** catches `DatalessRefused` and writes `completeness=dataless`. **Task 4 does not.** It routes formats. The gate still raises and writes nothing. P2 already counts `runs_dataless`, so a real scan still will not show iCloud placeholders until a **caller** (orchestrator, not Task 4 as written) catches the exception and calls `record_run`. That is **not** a P4 blocker and **not** a P5 Task 1 blocker. It is the first Wave-2 join after both packages exist.
8. **Fixtures use `content_hash="sha256:abc"`.** Live P1 stores **64 hex, no prefix**, algorithm in `hash_algorithm`. Task 19 / skeleton must copy `get_file()["content_hash"]`. Do not write a `sha256:` prefix onto `evidence.content_hash`. Prefix belongs on `observation_key` / `config_fingerprint` if at all.

---

## What P4 execution must get right (the load-bearing bits)

- Package name is `evidence_shape`, not `evidence`.
- P4 authors **no** event. `author` is a required keyword; refuse `author="P1"`.
- `create_evidence_schema` is **not** inside `open_database`. Caller must call it.
- `observation_key` excludes extractor **version** (MINOR 8). Replay key **includes** it (four fields).
- Hash on the observation is P1’s hex from the `files` row.
- No gazetteer, no OCR library, no MIME table in this package. Task 18’s introspection is the point.
- Five zones still have no golden fixture (`path`, `header_footer`, `link`, `annotation`, `reference_list`) plus `contacts`. Named gap (B8). Do not invent them.

P1 is green (468). P1 PLAN.md is still a stale construction record — build against `src/database_agent/`.

---

## What P5 execution must get right (after P4)

- Every extractor calls `admit` first. Protected container: no run (P3 exclusion is the record). Dataless: raise; **someone else** writes the `dataless` run.
- `ZERO_OBSERVATION_COMPLETENESS` is the same five-tuple as P4. A `metadata_only` run from the stopping extractor emits nothing; the file stays indexed via `filesystem`.
- `OUTCOME_BY_COMPLETENESS` already maps all nine, including `dataless → abstained`. The docstring that still calls two rows NEEDS JOSEPH is leftover; the dict is the contract.
- Production caller injects catalogues 02–07. Tests use lambdas/fixtures. Green P5 with `dimension_signal=lambda *_: None` is **shape-correct and catalogue-blind** — say that in the PR, do not treat it as “citations work.”
- E4 zone is `manifest`.
- Filename `raw_value` is the matched substring, not the convention label (catalogue 04 close-out).
- Do not copy catalogue JSON into `src/extractors/`.

---

## Wave-2 orchestrator — also read [`18-wave2-orchestrator.md`](18-wave2-orchestrator.md)

That page is the missing caller (not a fourteenth part). It correctly names **itself** as the `DatalessRefused` catcher and uses the shipped `set_extraction_status` (P5 PLAN still claims no setter — stale).

Do **not** build it before P4 and P5 import. Two defects in that draft will fail the skeleton if copied literally: `file_row["path"]` is `current_path` on the live `files` row; Done-means 3 cannot hold for a *first-sight* iCloud file because P3 never creates a `files` row (`scan.py` records `dataless_detections` and continues). Close that as two counts (P3 detections vs `runs_dataless` for formerly-local files). Details are in the pre-build review section on that page.

## Still unpaid (not P4’s job)

- Scan → extract orchestrator — drafted in [`18-wave2-orchestrator.md`](18-wave2-orchestrator.md); build **after** P4+P5.
- Graphify.
- P6 must *state* C1 and consume catalogue 01.
- P7 must settle C2 before its schema.
- Real PDF/HEIC/OCR libraries remain injected. Four OCR/image ceiling **values** unset until the engine is wired (keys exist).

---

## Punch list if you want a clean plan before Task 1

Optional. Does not change task count.

1. P4 Task 2 intro: five zero-observation values; OQ3 closed.
2. P4 Task 14 intro: `metadata_only` / `dataless` carry none; rename “the three” tests or extend the loop to the five-tuple.
3. P4 Self-Review: one remaining open question, OQ4; hash owns the set; nine completeness values.
4. P4 Global Constraints + conflict row 12 + NEEDS JOSEPH A1: sixteenth key exists; P4 holds no number.
5. P5 NEEDS JOSEPH #6: strike; B6 is ship.
6. P5 Task 3/4: stop claiming Task 4 writes the dataless run. The catcher is [`18-wave2-orchestrator.md`](18-wave2-orchestrator.md).

Then execute P4 Tasks 1–19 in order, against live `src/database_agent/`, with the plan’s own pytest commands.

Catalogues are ready to inject later ([`17-catalogue-uncertain-decisions.md`](17-catalogue-uncertain-decisions.md)). They are not on the P4 critical path.
