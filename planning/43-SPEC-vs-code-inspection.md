# SPEC vs code inspection — for Joseph

Date: 2026-08-29  
Branch inspected: `build/p6-p7-first-packages`  
Repo: this tree (same GitHub project as the long-standing part SPECs)  
Inspector role: **find** design-intention vs code inconsistencies and explain why the product path does not work as the SPECs require. **Not** to implement fixes in this pass.

Authority order used:

1. `planning/00-database-agent-product-design.md`
2. `planning/parts/*/SPEC.md` (P1–P13) — Contract in/out + **Done means**
3. Live `src/` and `src/cli.py` / `src/production.py` (what the product actually runs)

---

## Plain-English verdict

A large amount of code exists under `src/` for parts **P1–P11**. Much of it is written in the spirit of the SPECs (shapes, refusals, freeze closed-set, privacy gate types, validators).

What fails the SPECs’ **product intentions** is mainly this:

> The packages often satisfy Done means **when tested in isolation**, but the **live command path** (`src/cli.py` → `production.run_production_corpus`) deliberately turns off or never connects the behaviours the SPECs assume. So the system “has the parts” and still does not behave like the designed product.

P12 and P13 have SPECs (and plans) but **no** `src/` packages yet — so apply/undo and the review surface Done means cannot hold at all.

---

## How to read the scorecard

| Label | Meaning |
|-------|---------|
| **HOLDS** | Live code + tests encode the SPEC intention; usable on a normal product path |
| **PACKAGE ONLY** | SPEC intention exists in `src/<part>/` and part tests, but CLI/production does not wire it, so the product path does not deliver it |
| **DRIFTS** | Code behaviour conflicts with SPEC / `00` intention |
| **MISSING** | SPEC exists; no implementing package (or required deployment surface is empty) |

---

## Why it “isn’t working” (root causes)

### R1 — Chooser under-wires hybrid intelligence (P6 + P8 + P9 SPECs)

SPECs expect: direct + rule + LLM facts with validation before activation; grouping/placement may call the harness; privacy gate is on the only egress.

**Live CLI (`src/cli.py`):**

- `FactResolver` stages: `rule=None`, `llm=None` (only `direct`)
- `p8_run_call=None`, `p8_authorities=None`
- `EmbeddingsOff()`
- Placement model path off

**Effect:** P6 Done means that require rule/LLM paths, and P8/P9 Done means that require a real harness call on the product path, stay **PACKAGE ONLY**. Grouping records “no model call configured.” The product feels empty/dumb relative to the SPECs even though `src/facts/`, `src/llm_harness/`, `src/grouping/` exist.

### R2 — Extraction deployment does not match P5’s format intentions

P5 Done means require real DOCX/image/archive/OCR behaviours (and `unsupported` ≠ fake empty success). Extractors and router know those families.

**Live deployment (`src/readers/deployment.py`):**

- `read_docx` / `read_image` / `read_manifest` / `read_long_tail` = `_no_reader` → always `None` → `unsupported`
- Vision `languages`: `["en-US"]` only (SPEC/`00` intend CJK where required; DPI/level otherwise match)

**Live CLI:** `_detect_format` only maps `.pdf` / `.txt` / `.md`.

**Effect:** P5 Done means 6–10 largely **PACKAGE ONLY** or **DRIFTS** on the shipped macOS path. Word/images/archives never become reusable evidence in SQLite for the command users run.

### R3 — Targeted OCR path is disabled by the chooser (P5 Done means 5 / `00` §2.7)

Orchestrator *can* run targeted OCR after P6.

**CLI:** `usable_threshold=lambda facts, unresolved: True` — always “usable,” so the second OCR route never fires.

**Effect:** Broken text-layer documents never get the SPEC’d OCR retry on the product path.

### R4 — Freeze catalogue vs launch-domain intention (P6 §3.11 / P10 Deferred)

SPECs/`00`: initial release focuses on six launch domains; do not prematurely treat hundreds of specialized schemas as the default freeze set. P10 Deferred: only five §5.4 template dimension sets are design-stated.

**Live:** `load_shipped_catalogue` loads the large shipped wave2 library; CLI can route situation signals into specialized trees. `facts` also carries a wide `SCHEMA_IDS` set.

**Effect:** **DRIFTS** toward “everything is a destination schema” ahead of the SPEC launch posture. Finance is both a **safety** domain (P7) and a destination field catalogue — ordering intention (detect/protect before automated placement) is easy to violate in practice.

### R5 — Residual library empty (P10 Contract out §6 / P11 residual)

P10 fixes nine residual **names**; slot *contents* are Deferred, but enablement must be possible.

**CLI:** `RESIDUAL_LIBRARY = {}` → tree design early-returns residual projection.

**Effect:** Residual Done means / §7 workflow **PACKAGE ONLY** or blocked on product path.

### R6 — No apply/undo, no review surface (P12 / P13 SPECs)

SPECs require plan → verify → mutate with journal → conditional undo; review records and consent hand-back (P13). P11 SPEC: placement **moves nothing**.

**Live:** no `src/mutation/`, no `src/review_surface/`. CLI ends with “Nothing was moved.”

**Effect:** P12/P13 Done means **MISSING**. Working-memory story in `00` (movement plans, undo history) incomplete. Product stops at a report.

### R7 — Validation oracles not owned (P6/P8 C-5)

P8 Site A needs `normalize` / `contradicts`. P6 explicitly does not publish them. Deployment does not inject them on the CLI path.

**Effect:** Even if P8 were wired, fact validation can fail closed as `ValidationUnavailable` — looks “safe” while LLM facts never activate (P6 Done means 11 / P8 Site A **PACKAGE ONLY** or ineffective).

### R8 — Stale docs hide the real gap

README still said no application code; older audit text said P8/P9 are plans only. That confuses “packages missing” with “chooser under-wired.”

**Effect:** Process drift — people re-implement or mis-prioritize. Not a SPEC Done means failure, but it blocks fixing the right layer.

---

## Part-by-part scorecard (inspection summary)

### P1 — Storage / identity / provenance (`src/database_agent/`)

| Area | Verdict | Note |
|------|---------|------|
| Identity ≠ path; append-only events; budgets; supersede | **HOLDS** | Package + tests align with SPEC intentions |
| Movement/undo tables as full working memory | **MISSING / deferred to P12** | Event *vocabulary* mentions moves; P12 not present |

### P2 — Eval / replay (`src/eval_harness/`)

| Area | Verdict | Note |
|------|---------|------|
| Bundle / replay / compare | **HOLDS** (package) | Schema bootstrapped in production; CLI sets `evaluation=None` → **PACKAGE ONLY** on default CLI |

### P3 — Scan / corpus (`src/scan_agent/`)

| Area | Verdict | Note |
|------|---------|------|
| Selection, exclusions, REUSE cache | **HOLDS** | Live path uses scan |
| Candidate destination roots | **DRIFTS (thin)** | CLI uses `candidate_roots=[]` — PICK incomplete vs design |

### P4 — Evidence shape (`src/evidence_shape/`)

| Area | Verdict | Note |
|------|---------|------|
| Observation / text-unit / citation shape | **HOLDS** | Shared boundary for later parts |

### P5 — Extractors (`src/extractors/` + `src/readers/`)

| Done-means focus | Verdict | Evidence |
|------------------|---------|----------|
| One outcome per file; unsupported ≠ empty success | **HOLDS** in extractors; **DRIFTS** if callers treat unsupported as “understood empty” | Router/extractors; deployment `_no_reader` |
| DOCX zones (DM 6) | **PACKAGE ONLY / DRIFTS on CLI** | Extractor exists; `read_docx=_no_reader` |
| Archives no unpack (DM 7) | **PACKAGE ONLY on CLI** | `read_manifest=_no_reader` |
| HEIC / image traps (DM 8) | **PACKAGE ONLY on CLI** | `read_image=_no_reader` |
| OCR fields + languages (DM 9) | **PARTIAL** | Vision wired; languages `en-US` only |
| Signature over extension (DM 10) | **HOLDS** in router; **weakened on CLI** | CLI `_detect_format` extension-only before protected check |
| Two text-layer states / targeted OCR (DM 5) | **PACKAGE ONLY** | CLI `usable_threshold` always True |

### P6 — Facts / facets (`src/facts/`)

| Done-means focus | Verdict | Evidence |
|------------------|---------|----------|
| Schema / direct facts / refusals in package tests | **HOLDS** (many DM) | Rich `src/facts/` + tests |
| Academic rule path (DM 4, 8) on product path | **PACKAGE ONLY** | CLI `rule=None` |
| LLM validation path (DM 11) on product path | **PACKAGE ONLY** | CLI `llm=None`; C-5 oracles not injected |
| Deterministic subset without P8 (DM 17) | **HOLDS** if only direct is required | Matches current CLI — but that is a **narrower product** than SPEC hybrid intention |
| Launch vs 23 schemas | **DRIFTS** | Wide `SCHEMA_IDS` / fields vs launch posture |

### P7 — Privacy / consent (`src/privacy/`)

| Done-means focus | Verdict | Evidence |
|------------------|---------|----------|
| Classification store, Gate, NeedsConsent types, single egress discipline | **HOLDS** in package + integration tests that wire Gate | |
| NeedsConsent never coerced (DM 7) | **HOLDS** in harness design | Must stay true when CLI wires P8 |
| Local-first default (DM 12) | **HOLDS** on CLI (`OPERATION_MODE=offline`) | |
| Gate on live CLI corpus path with P8 | **PACKAGE ONLY** | CLI does not bind `run_call` / Gate into grouping authorities |
| Derived-data deletion | **Deferred / incomplete** | Known P13 dependency from earlier audits |

### P8 — LLM harness (`src/llm_harness/`)

| Done-means focus | Verdict | Evidence |
|------------------|---------|----------|
| Harness, validators, NeedsConsent passthrough, transport guards | **HOLDS** in package | Large `tests/p8/` |
| One egress + unknown→abstain on **CLI product path** | **PACKAGE ONLY** | `cli.py` `p8_run_call=None` |
| Site A oracles | **DRIFTS / incomplete** | C-5: normalize/contradicts not injected at chooser |

### P9 — Grouping (`src/grouping/`)

| Area | Verdict | Note |
|------|---------|------|
| Deterministic grouping pipeline | **HOLDS** on CLI | Used in production |
| P8 coherence / embeddings | **PACKAGE ONLY** | CLI disables both |
| Auto engine naming vs user acceptance | **Watch** | SPEC: acceptance before tree; CLI forces situation signals — risk of **DRIFT** vs “accepted groups” intention |

### P10 — Tree design / freeze (`src/tree_design/`)

| Area | Verdict | Note |
|------|---------|------|
| Freeze closed legal set | **HOLDS** in package | |
| Default catalogue = launch scope | **DRIFTS** | Full shipped library loaded |
| Residual enablement | **PACKAGE ONLY / blocked** | Empty residual library on CLI |

### P11 — Placement / residual (`src/placement/`)

| Area | Verdict | Note |
|------|---------|------|
| Place or abstain; moves nothing | **HOLDS** | Matches SPEC; CLI prints no moves |
| Two-condition scoring | **HOLDS** when wired | Model path off on CLI |
| Residual workflow | **PACKAGE ONLY** | Depends on P10 residual + P13 |

### P12 — Apply / undo

| Area | Verdict | Note |
|------|---------|------|
| Entire SPEC | **MISSING** | `planning/parts/P12-apply-undo/SPEC.md` (+ plan) exists; no `src/mutation/` |

### P13 — Review / approval surface

| Area | Verdict | Note |
|------|---------|------|
| Entire SPEC | **MISSING** | `planning/parts/P13-review-approval-surface/SPEC.md` (+ plan) exists; no `src/review_surface/` |

---

## Detailed Done-means findings (second pass)

These refine the scorecard above. **HOLDS** below often means “package + part tests”; check the CLI column.

### Highest-signal drifts (fix these first)

| # | Part | Done means | Verdict | Why |
|---|------|------------|---------|-----|
| 1 | P4 | #5 (fixtures cover all zones/source types) | **DRIFTS** | 19 fixtures but only ~10/15 zones and ~13/14 source types; shortfall documented as `ZONES_WITHOUT_A_WORKED_EXAMPLE` in `evidence_shape/fixtures.py` |
| 2 | P1 | #14 (budget ceiling keys) | **DRIFTS** | SPEC says fifteen keys; `budget.CEILING_KEYS` has seventeen |
| 3 | P6 | #2 (closed field catalogue / career empty) | **DRIFTS** | `fields.FIELD_ROWS` expanded with career + many professional schemas beyond SPEC’s closed launch set |
| 4 | P5 | #6–#8 on product path | **PACKAGE ONLY** | DOCX/HEIC/archive extractors exist; `readers/deployment.py` wires `_no_reader` |
| 5 | P9 | #6 (purpose fixture §4.7) | **NOT IMPLEMENTED** | No purpose-packet builder/fixture under `src/grouping` / `tests/p9` matching SPEC DM6 |
| 6 | P2 / P7 egress | eval + Gate.release on CLI | **PACKAGE ONLY** | `cli.py`: `evaluation=None`, `p8_run_call=None` |
| 7 | P12 / P13 | all | **MISSING** | SPECs present; no `src/mutation/`, no `src/review_surface/` |

### P1–P7 (package vs CLI)

| Part | Mostly | CLI notes |
|------|--------|-----------|
| P1 | **HOLDS** (identity, events, supersede, V1–V4, learning, scan_usage) | Budget key-count **DRIFTS** (#14) |
| P2 | **HOLDS** in package | Bundle sealed on CLI; **evaluate / shadow / adversarial not wired** (`evaluation=None`) |
| P3 | **HOLDS** | Scan/exclusions/REUSE on product path; P2-from-bundle eval package-only |
| P4 | **HOLDS** except fixture coverage **DRIFTS** (#5) | — |
| P5 | **HOLDS** for PDF+OCR routing/shape | DOCX/HEIC/archive **unwired** on default readers |
| P6 | **HOLDS** many deterministic DM | Direct resolver on CLI; rule/LLM unused; catalogue **DRIFTS** (#2) |
| P7 | **HOLDS** classify + local-first offline | Classification on CLI; **Gate.release / transport never called** on default path; `delete_derived` still refuses (P13 tombstone) |

### P8–P11 (package vs CLI)

| Part | Package | Live CLI |
|------|---------|----------|
| P8 (13 DM) | ~10 **HOLDS**; egress/`may_propose` end-to-end **PACKAGE ONLY** | **Off** (`p8_run_call=None`) — none of DM 1–13 exercised by shipped command |
| P9 (11 DM) | ~9 **HOLDS**; privacy-before-model **PACKAGE ONLY**; **DM6 purpose missing** | Deterministic grouping + acceptance **HOLDS**; embeddings/P8 off |
| P10 (17 DM) | ~16 **HOLDS**; P2 stage emit **PACKAGE ONLY** | Design/freeze path **HOLDS**; residual enablement depends on library wiring |
| P11 (incl 10b) | ~15 **HOLDS**; P2 scoring / model residual **PACKAGE ONLY** | Deterministic place/abstain **HOLDS**; no model residual |

### Cross-cutting CLI map (quick)

| Area | On `cli.run`? |
|------|----------------|
| P1 identity / events / budgets / scan usage | Yes |
| P2 seal bundle | Yes |
| P2 evaluate / shadow / adversarial | No |
| P3 scan | Yes |
| P5 PDF + OCR | Yes |
| P5 DOCX / HEIC / archive | No |
| P6 direct facts | Yes |
| P6 rules / LLM facts | No |
| P7 classify + offline policy | Yes |
| P7 Gate.release | No |
| P8 harness | No |
| P9 deterministic group | Yes |
| P10 design/freeze | Yes |
| P11 deterministic place | Yes |
| P12 move / undo | No package |
| P13 review surface | No package |

---

## Concrete hotspots for Joseph (fix targets)

Priority is **wiring and missing parts**, not rewriting healthy package interiors.

1. **`src/cli.py`** — re-enable SPEC behaviours with injected authorities (rules, usable_threshold, P8 pair, residual library, launch catalogue filter). Do not put domain defaults in `production.py`.
2. **`src/readers/deployment.py`** — replace `_no_reader` for DOCX/image/manifest; expand OCR languages per P5/`00`.
3. **Deployment-owned `normalize` / `contradicts`** — inject into P8 without adding them to `facts` (C-5).
4. **Catalogue gate** — default freeze to launch destination schemas; keep finance/identity/medical/legal as safety-first.
5. **Implement P12 then P13** from existing SPECs/plans (`docs/superpowers/plans/2026-08-29-p12-apply-undo.md`, `...-p13-review-approval-surface.md`), then connect CLI `--apply` / review.
6. **Re-audit** claiming SPEC Done means numbers on the **CLI path**, not “folder exists under `src/`.”

A separate implementation roadmap was drafted earlier as `docs/superpowers/plans/2026-08-29-restore-00-fidelity.md` — use it only if you want an execution sequence; **this file is the inspection finding**, not a claim that those fixes were applied.

---

## What was *not* done in this inspection pass

- No SPEC text rewritten
- No P12/P13 implementation
- No CLI wiring fixes landed as part of this report
- Open SPEC questions / NEEDS-JOSEPH left open

---

## Suggested next step for Joseph

Pick R1–R3 first (CLI + readers): that is why a green package suite still feels like “the product doesn’t work.” Then P12/P13 for “files never move.” Re-run part Done means against `cli.main` / `run_production_corpus` with the launch profile enabled.
