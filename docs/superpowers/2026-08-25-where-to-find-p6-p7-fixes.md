# Where to find the P6 and P7 fixes

Date: 2026-08-25
This file is an index for the **live packages**, not the P8/P9 plans. P8/P9 plan
patches: `docs/superpowers/2026-08-25-where-to-find-fixes.md`.

Verdict from this pass: both packages are **COMPLETE WITH KNOWN GAPS**. There is
no missing task. What remains is parked debt, seams that must stay open, and a
few live-code P2/P3s. Full write-ups are the audits; this file says where to
open them and which `src/` file each item lives in.

---

## Source-of-truth reviews

| What | File | Jump to |
|---|---|---|
| P6 completeness | `.superpowers/sdd/p6-completeness-audit.md` | `## Remaining defects`, `## Open seams that must stay open`, `## Assembly vs package` |
| P7 completeness | `.superpowers/sdd/p7-completeness-audit.md` | `## Remaining defects`, `## Detector honesty`, `## Assembly vs package` |
| P1–P7 assembly (caller, not package) | `planning/28-p1-p7-design-conformance-audit.md` | remaining boundary |
| Per-task SDD reviews (parked P3s from the build) | `.superpowers/sdd/p6-task-*-review.md`, `.superpowers/sdd/p7-task-*-review.md` | only if you are re-opening a specific task |

Plans (do not execute remaining “missing tasks” — they are already shipped):

- `planning/parts/P6-facts-facets/PLAN.md` (26 tasks: 1–25 and 27; Task 26 CUT)
- `planning/parts/P7-privacy-consent-gate/PLAN.md` (22 tasks)

---

## Do not “fix” these — they must stay open

These are the honest product gaps. Closing them inside `src/facts/` or
`src/privacy/` would paper over a later part.

### P6

| Seam | Live proof | Write-up |
|---|---|---|
| C-5: no `normalize(field, raw_value)` / `contradicts(...)` | `src/facts/llm_seam.py`; `tests/p6/test_p6_llm_seam.py` `test_p6_publishes_neither_a_normalizer_nor_a_contradiction_oracle` | P6 audit **Open seams**. P8 injects both. |
| Date regex bodies unauthored | `src/facts/dates.py` (ids only); patterns injected | P6 audit **Open seams** |
| Domain activation signals unauthored | `src/facts/domains.py` `ActivationSignals` has no default | P6 audit **Open seams** |
| Gazetteers / catalogue-01 producer strings | `tests/p6/test_p6_no_invention.py` | P6 audit **Open seams** |
| OQ3, OQ5, OQ6, OQ8, OQ9, OQ10 | `tests/p6/test_p6_no_invention.py` | P6 audit **Open seams** |
| `usable_threshold` empty of policy (M11) | caller must inject; `src/production.py` | P6 audit substrate gaps |
| Task 26 CUT / `run_wave2` stub | `TARGETED_OCR_UNAVAILABLE`; do not wire `no_usable_facts_for` into `run_wave2` | P6 audit **Assembly vs package**. Additive path is `run_p1_p7`. |

### P7

| Seam | Live proof | Write-up |
|---|---|---|
| No detector | unclassified → `Denied(unclassified)` | P7 audit **Detector honesty** |
| `delete_derived` refuses (I6 / D3) until P13 tombstones | `src/privacy/revocation.py` | P7 audit P3.1; planning/28 |
| Filename kind unratified | `UNRATIFIED_ITEM_KINDS == ("filename",)` | P7 audit P3.5; open question 2 |
| Gate does not invent `effective_policy` | `NoPolicyInForce` if no stored policy | P7 audit P3.6. Callers `set_policy` first. |
| `correction_scope` stored, `suppressed` reads `FILE_SCOPE` only | `src/privacy/learning_seam.py` | P7 audit P3.2; ASSEMBLY OQ7 |

---

## Joseph / design decisions (not a silent code patch)

| Issue | Live files | Write-up | What a fix actually is |
|---|---|---|---|
| D8 dual key: `target_school` and `target_university` both in the catalogue | `src/facts/fields.py` FIELD_ROWS (~128–173); Done-means 14 test writes `target_university` in `tests/p6/test_p6_domains.py` | P6 audit Done-means 14, Bottom line | Fold or keep both **as a decision**. Do not delete a row to make the audit green. |
| Two §3.5 direct slots with no production publisher (filesystem timestamp; content-hash as `observation_key`) | PLAN §6; `src/facts/direct.py` | P6 audit substrate gaps | Name a producer or leave as known consumer-without-producer. |
| `document_title` publisher, no catalogue field | `get_field` → `FieldNotInCatalogue` | P6 audit **Open seams** | Catalogue row or stop publishing. |

---

## Live-code debt you can patch in `src/`

Parked P2/P3. Fix only if a later task would break, or if you want hygiene before
P8. Full wording is in the audits.

### P6 — `src/facts/`

| Item | Edit | Tests | Write-up |
|---|---|---|---|
| `AUTHORED_EVENT_TYPES[0]` index coupling for `"fact creation"` | `src/facts/file_facts.py` ~226. Mirror `learning.py:73` named unpack. | `tests/p6/test_p6_file_facts.py` | P6 audit Remaining defects P3 |
| `SELECT f.*` duplicates VIRTUAL `field_key` | `src/facts/file_facts.py` `facts_for_file` ~272 | `tests/p6/test_p6_file_facts.py` | same |
| `cited_quote_refs` never validated as observation keys | `src/facts/file_facts.py` ~191 (`_checked_refs` is evidence_refs only) | `tests/p6/test_p6_file_facts.py` | same |
| `merge_values` SELECTs outside the write transaction | `src/facts/values.py` ~204–237 | `tests/p6/test_p6_values.py` | same (Task 3 Q1-b, Low) |
| `ANALYSIS_TIERS[2]` / `FIELD_SCOPES[0]` index coupling | `src/facts/usable.py` ~181; `src/facts/domains.py` ~58 | `tests/p6/test_p6_usable.py`, `test_p6_domains.py` | same. Task 16 `SIGNAL_TIERS[-1:]` is the blessed exception — leave it. |

### P7 — `src/privacy/`

| Item | Edit | Tests | Write-up |
|---|---|---|---|
| **P2:** `ConsentRequirement.items` — types say `(observation_key, span)` pairs; `Gate.release` writes kind strings (`"excerpt"`). Round-trip through `pending_consent` splits the string into characters. | `src/privacy/gate.py` (what it writes) and/or `src/privacy/consent.py` (type vs persist). Fixture 10 in `src/privacy/fixtures.py`. | `tests/p7/test_p7_release.py`, `tests/p7/test_p7_fixtures.py` | P7 audit **Remaining defects P2**. P13 must not assume pairs until this is one shape. |
| Weaker `assign` still inserts a live row and **returns** the attempted record | `src/privacy/learning_seam.py`. Projection already mirrors `store.current` (uncommitted). | `tests/p7/test_p7_learning_seam.py` | P7 audit Assembly vs package. Callers must re-read `ClassificationStore.current`. Optional: return current, not attempted. |
| `CLASSIFICATION_ASSIGNED` event still names the weaker class | same module, event payload | same tests | same |
| P5 `extractors.long_tail` import (signal reader, not a detector) | `src/privacy/classification.py`, `src/privacy/items.py` | `tests/p7/test_p7_no_invention.py` | P7 audit P3.4. Soft isolation; do not turn it into a detector. |

---

## Uncommitted assembly (keep; do not revert)

These are caller/composition, not missing P6/P7 tasks. See P6 audit
**Assembly vs package** and P7 audit **Assembly vs package**.

| Path | What it is |
|---|---|
| `src/orchestrator.py` `run_p1_p7` | Additive four-pass caller. `run_wave2` stays. |
| `src/production.py` | Composition root; requires injected authorities including `classify`. |
| `src/facts/usable.py` `targeted_ocr_needed_for` | Extra wrapper around Task 19; `no_usable_facts_for` contract intact. |
| `src/extractors/dispatch.py`, `ocr_policy.py` | Targeted-OCR sequencing after first P6 pass. |
| `src/privacy/learning_seam.py` | Projection bugfix: mirror `current`, not the weaker incoming record. |
| `src/privacy/classification_store.py` | `bound_to(conn)` only. |
| `tests/integration/` | Live P1–P7 assembly / production tests. |

Do not wire raw `no_usable_facts_for` into `run_wave2`. That still raises
`FactPassNotRun` on the first text-bearing PDF.

---

## What a later part must not assume

From the audit bottom lines. Later plans copy these; they are not P6/P7 bugs.

**P6 publishes:** `FactRequest`, `Proposal`, `facts.llm_seam.Verdict(passed, failed_check)`,
`build_request`, `apply_verdict` (requires `proposal_state`, `model_identifier`,
`prompt_fingerprint`), `FOUR_CHECKS`, allowlist, fact tables, thirteen unresolved
reasons. `proposal_eligible` excludes `possible` and **includes** `llm_supported`.

**P6 does not publish:** `normalize`, `contradicts`, model call, gazetteers,
activation signals, `usable_threshold` policy, `sensitivity_status`.

**P7 door:** `Gate.release` → `Released | Denied | NeedsConsent`; spend with
`consume_release`. `NeedsConsent` is not a verdict. `NoPolicyInForce` is an
exception, not a fourth branch. D14: `AuditRecord.release_id` is `None` on the
grant row.

**P7 does not:** classify files; forget OCR via `delete_derived`; default a
policy; treat `assign`'s return value as current.

---

## Suggested order if you touch live P6/P7 at all

1. Decide D8 (`target_school` vs `target_university`) — catalogue, not a drive-by
   delete.
2. P7 P2: one shape for `ConsentRequirement.items` before P13.
3. Optional P3 hygiene in `file_facts.py` / `values.py` (named event constant,
   `cited_quote_refs` check, `merge_values` reads inside the transaction).
4. Leave C-5, detector absence, `delete_derived` refusal, and Task 26 CUT
   exactly as they are.
