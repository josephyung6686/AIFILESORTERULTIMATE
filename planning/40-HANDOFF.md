# Handoff — 2026-08-27 (audit + P10/P11 plan repair)

Read this, then `git log --oneline -10`. Supersedes `36-HANDOFF.md` for P10/P11 state.

Branch `build/p6-p7-first-packages`. Suite **3621 passed**. **`src/` and `tests/` are
byte-identical to `b7c6e8f`** — this session changed no product code, deliberately.

---

## 1. What happened

Fifteen parallel auditors read P1–P9 against their SPECs, PLANs and the canonical
design, then the P10/P11 plans and the template chain. 111 guard sabotages were run;
**15 came back silent**. Findings are consolidated in **`planning/39-P1-P9-AUDIT.md`**
— that is the document to read for "what is lacking".

Then P10's and P11's plans were repaired and reconciled.

## 2. New documents

| File | What it is |
|---|---|
| `planning/39-P1-P9-AUDIT.md` | the consolidated audit. §8 is a prioritized work list, split List A (live code, **needs authorization**) / List B (plan edits) |
| `planning/38-p10-p11-connection-contract.md` | third seam contract. Freezes the P10↔P11 names and shapes; §10 is the applied correction list |
| `planning/37-TEMPLATE-REUSE-INVENTORY.md` | what the 292 landed domain rows actually justify: **3 fragments, 24 definitions, 54 bindings** |
| `docs/superpowers/plans/2026-08-27-p1-p9-seam-repair.md` | 10-task executable repair plan for the live-code defects. **Not applied. Three OPEN items need an owner ruling.** |

## 3. P10 and P11 — state

Both plans were rewritten, repaired, seam-reconciled and independently verified.

- **P10**: 10013 → ~12100 lines, **17 → 18 tasks**. New **Task 12 "Populate the
  template from real facts, then build the nodes"** — `materialise_branch(...)`. Before
  this, `apply_review_action` handled 2 of 15 actions (not `accept`) and nothing
  materialised a composition into `Node` rows: **P10 could not propose a tree.**
- **P11**: 8276 → ~9900 lines, 21 tasks. Task 19 now actually orchestrates §6.12's
  nine steps (`run_corpus`, `call_placement` wired).
- **The seam joins.** P11 imports `from tree_design.freeze import frozen_tree`; P10
  publishes `def frozen_tree(conn, *, plan_version) -> FrozenTree`. Before: zero
  vocabulary overlap (`FrozenTree` 21/0, `FreezeRecord` 0/14).

Verified by script (`scratchpad/verify_plans.py`, `verify_ctors.py`):
**207 upstream imports resolve, 0 missing. 39 record constructions bound, 0 real defects**
(2 are the declared `TemplateDependencies.published_fragment` addition; 3 are basename
collisions — `Candidate`/`Conflict` exist in several packages).

### Still true of P10/P11
- P10 Task 8 requires **`llm_harness.template_validation.TemplateDependencies` to gain
  `published_fragment`** before it runs. Declared at `PLAN.md:38`. It is a real edit to P8's package.
- The §8.8 identity fix is in: P10 mints a new `node_id` per plan version, so **P11
  matches across versions on `origin_node_id`, never `node_id`.** Matching on `node_id`
  would have marked every decision `requiring_renewed_review` after any tree edit,
  including a pure rename.

## 4. What needs a decision before anything ships

1. **`context_before` / `context_after` on a `Released`** — the gate redacts the value
   and ships both context fields raw. An 8-char requested span released 52 of 60
   characters through the real `Gate` and real `build_dossier`. P7's SPEC says
   `materialised_items[] post-redaction values only` and contains the word "context"
   **zero times**. Redact them, bound them, or remove them. Repair plan Task 4.
2. Whether `src/production.py` grows to cover P8+P9.
3. Whether the egress guard or the transport is wrong (`transport.py` never sets
   `IS_MODEL_TRANSPORT`, so the guard's loop can never fire).

## 5. The three BLOCKER-class live defects

Full detail in `39-P1-P9-AUDIT.md` §4. None is authorized.

- **P3** — `SessionWatch` walks into protected containers, stats them, and writes
  interior paths into the **append-only** `events` log. `watch.py` has zero references
  to protection. Unrecoverable once written.
- **P7** — the context bypass above.
- **P8 + P9** — `harness.py:348` returns `verdicts[-1]` (position, not severity) while
  `:472` selects correctly; and `pipeline.py:323` calls `p8_run_call(conn, request)`
  against a five-keyword-only signature. **P9 is wired to P8 nowhere in production**, so
  the TypeError is latent.

Also worth knowing: **P9's grouping degrades as evidence increases** (audit A6), and an
ordinary `.eml` with a repeated address raises `IndexError` and ends the scan (A4).

## 6. Templates — do not start building yet

Not because of gates. Because **16 of 23 schemas declare zero fields**, so 199 of 253
kept rows carry `dimension_order: []` and cannot express a folder dimension at all.
All three of the handoff's hypothesized reuse shapes are unsupported by the corpus
(`project→stage→artifact` = 0 rows). Three of four §3.15 safety schemas
(`finance`, `identity`, `medical`) lack `is_safety_domain`, so no privacy floor computes.

**The productive next move is declaring fields for those 16 schemas**, not finishing the
remaining ~66 research rows.

One template does serve many domains — evidenced: `def.subject-work-record` binds
**14 rows across 3 schemas** (academic, research, code).

Also: **`G-P10` in `2026-08-26-composable-template-library.md:26` names the wrong tasks**
(says P10 Tasks 1–4; correct is **6–8**).

## 7. Method notes worth keeping

- **A seam is verified when the caller's arguments have been bound against the callee's
  live signature, or when a test drives the real callee end to end — never when a
  reference chain exists between them.** `graphify path` proves a connection exists, not
  that it works. This cost one auditor a wrong verdict and cost the lead's own
  verification script two false positives.
- **17 basenames collide across the ten `src/` packages** (`__init__.py` in all ten,
  `schema.py` in seven, `records.py`, `store.py`, `vocabulary.py`, `fixtures.py`…).
  Three separate careful readers were misled by this in one session.
- The highest-leverage untaken item is **audit A18: one end-to-end test with no doubles**.
  Every component exists and is green; only the composition is missing. It would have
  caught the P3 watch, the P7 context bypass, the P8 claim selection and the P9
  signature mismatch simultaneously.
