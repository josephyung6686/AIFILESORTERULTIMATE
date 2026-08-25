# Where to find the P8/P9 plan fixes

Date: 2026-08-25
This file is an index for **P8/P9 plan-text** patches. Live P6/P7 package debt:
`docs/superpowers/2026-08-25-where-to-find-p6-p7-fixes.md`.

The numbered blocking text lives in the judgment files. Open those first; edit
the target files listed under each item.

Canvas board (same pass): open
`/Users/jy/.cursor/projects/Users-jy-GRAPH-AGENT/canvases/p6-p9-readiness.canvas.tsx`
beside the chat.

---

## Source-of-truth reviews (read these)

| What | File | Jump to |
|---|---|---|
| P6 package audit | `.superpowers/sdd/p6-completeness-audit.md` | `## Remaining defects`, `## Bottom line for P8 planners` |
| P7 package audit | `.superpowers/sdd/p7-completeness-audit.md` | `## Remaining defects`, `## Bottom line for P8 planners` |
| P8 plan judgment | `.superpowers/sdd/p8-plan-judgment.md` | `## Blocking issues` (1–6), `## P9 coupling risks` |
| P9 plan judgment | `.superpowers/sdd/p9-plan-judgment.md` | `## Blocking issues` (1–8), `## P8 coupling risks` |
| Older P1–P7 assembly audit | `planning/28-p1-p7-design-conformance-audit.md` | remaining boundary; detector still injected |

Do not treat `planning/29-DOMAIN-OWNERSHIP.md` as the P8/P9 connection contract.
It is the concurrent domain-research claim register.

---

## Files you actually edit

### Must patch before executing P8 or P9

These are **plan-text** fixes. Do not start P8 Task 1 or P9 Task 8/9 against the
25 Aug files as-is.

| Fix | Edit this | Exact write-up |
|---|---|---|
| Missing charter artifacts / connection contract | New file (not `planning/29-…` unless you rename domain ownership). Optionally copy/link into `planning/parts/P8-llm-harness-validator/PLAN.md` and `planning/parts/P9-grouping/PLAN.md`. Amend `docs/superpowers/specs/2026-08-25-p8-p9-planning-design.md` if you relocate instead of writing the promised paths. | P8 judgment **Blocking 1**; P9 judgment **Blocking 1** |
| Freeze P8 public names (`run_call`, `Dossier`, P8 `Verdict` vs P6 `Verdict`) | Same contract, then both plans | P8 **Blocking 1** and **P9 coupling**; P9 **Blocking 4** |
| Live P2 version tuple (seven fields, no `produced_at`) | `docs/superpowers/plans/2026-08-25-p8-bounded-llm-harness-validator.md` Task 10 | P8 **Blocking 2**. Live shape: `src/eval_harness/run.py` (`VERSION_TUPLE_FIELDS`), `src/eval_harness/stage_output.py` (`record_stage_output`) |
| Live `apply_verdict` kwargs | P8 plan Tasks 7 and 12 | P8 **Blocking 3**. Live signature: `src/facts/llm_seam.py` `apply_verdict` |
| Name live P7 construction types | P8 plan Tasks 5, 9, 12 | P8 **Blocking 4**. Live: `src/privacy/items.py`, `src/privacy/release.py`, `src/privacy/gate.py`, `src/privacy/fixtures.py` |
| Suppression → P1 `learning_records` or fixture | P8 plan (eligibility / Task 4) | P8 **Blocking 5**. Live: `src/database_agent/learning.py` |
| Silent SPEC closures (Q8 retry, Q3 site D, `none` rung, `DossierRequest` in Task 1) | P8 plan Task 1 / 8 / 9 + open-question appendix | P8 **Blocking 6** |
| SR5 after P8 | `docs/superpowers/plans/2026-08-25-p9-bounded-evidence-grouping.md` Task 7 | P9 **Blocking 2** |
| Remove M9 token ladder from P9 | P9 plan Task 8 | P9 **Blocking 3**. Ladder belongs in P8 plan Task 9 |
| P9 must not call `Gate.release` or a model | P9 plan Tasks 8 and 13 | P9 **Blocking 4** |
| Honest P6 seed filter | P9 plan Task 4 + current-state ledger | P9 **Blocking 5**. Live: `src/facts/read_surface.py` `proposal_eligible` |
| G4 ceilings via `get_ceiling` | P9 plan config / `GroupingLimits` | P9 **Blocking 6**. Live: `src/database_agent/budget.py` |
| SPEC Done-means 6 and 8 (purpose packet, failure-point split) | P9 plan (new tasks or explicit unmet list) | P9 **Blocking 7**. Spec: `planning/parts/P9-grouping/SPEC.md` |
| Hard-gate Task 9 after Task 10 | P9 plan numbering / dependency note | P9 **Blocking 8** |

### Live P6/P7 debt (optional; not a P8 start blocker)

Parked package defects. Fix in `src/` only if a later task would break. Full list
in the audits; the ones that bite P8/P9/P13:

| Issue | Live code | Write-up |
|---|---|---|
| D8 dual key (`target_school` and `target_university`) | `src/facts/fields.py` FIELD_ROWS; `tests/p6/test_p6_domains.py` Done-means 14 | P6 audit Done-means 14, Bottom line |
| C-5: no `normalize` / `contradicts` | `src/facts/llm_seam.py`; asserted by `tests/p6/test_p6_llm_seam.py` | P6 audit **Open seams**. P8 must inject, not add them to `facts/` |
| `ConsentRequirement.items` kind strings vs pairs | `src/privacy/consent.py`, `src/privacy/gate.py` | P7 audit **Remaining defects P2** |
| Weaker `assign` return value is not current | `src/privacy/learning_seam.py` | P7 audit Assembly vs package. Callers re-read `ClassificationStore.current` |
| `delete_derived` refuses pending P13 | `src/privacy/revocation.py` | P7 audit P3.1; `planning/28-p1-p7-design-conformance-audit.md` |
| Index-coupled event type / `SELECT f.*` / `cited_quote_refs` unvalidated | `src/facts/file_facts.py`, `src/facts/values.py` | P6 audit **Remaining defects P3** |

Uncommitted assembly (`src/orchestrator.py` `run_p1_p7`, `src/production.py`,
`src/facts/usable.py` `targeted_ocr_needed_for`) is caller work, not a missing
P6/P7 task. See P6 audit **Assembly vs package**.

---

## Live APIs to copy from (do not invent names)

| Seam | Read |
|---|---|
| P6 fact request / apply | `src/facts/llm_seam.py` |
| P6 allowlist / reads | `src/facts/domains.py`, `src/facts/read_surface.py` |
| P7 door | `src/privacy/gate.py`, `src/privacy/release.py`, `src/privacy/binding.py`, `src/privacy/consent.py` |
| P7 fixtures | `src/privacy/fixtures.py` `by_number`, `GATE_ARGUMENTS` |
| P2 stage output | `src/eval_harness/stage_output.py`, `src/eval_harness/run.py`, `src/eval_harness/vocabulary.py` |
| P1 events / learning / ceilings | `src/database_agent/events.py`, `learning.py`, `budget.py` |
| P1 vectors (P9 Task 1 must not fall back) | `src/database_agent/vectors.py` `put_embedding` — forbidden fallback |

---

## What to leave alone

| File | Why |
|---|---|
| `planning/00-database-agent-product-design.md` | Wins on conflict. Plans adapt to it; they do not rewrite it. |
| `src/facts/` except parked P3s | C-5 stays open. Do not add `normalize` / `contradicts` to make P8 green. |
| `run_wave2` / `TARGETED_OCR_UNAVAILABLE` | D5. Additive path is `run_p1_p7`. |
| `planning/domains/` | Research artifact. Not a runtime module. |
| P8/P9 fail-closed injections, `NeedsConsent` unmapped, embeddings-never-establish | Already right in the plans. Do not weaken them to compile. |

---

## Suggested order of work

1. Write the connection contract (P8 **Blocking 1** = P9 **Blocking 1**).
2. Patch the P8 plan Tasks 1, 5, 7, 9, 10, 12 (P8 **Blocking 2–6**).
3. Patch the P9 plan Tasks 4, 7, 8, 9, 10, 13 (P9 **Blocking 2–8**).
4. Then P8 Tasks 1–7 can execute against live P1–P7. P9 Tasks 1–7 and 10–12
   can execute against fixtures. P8 Task 8+ and P9 Task 9 wait on the frozen
   public names.
