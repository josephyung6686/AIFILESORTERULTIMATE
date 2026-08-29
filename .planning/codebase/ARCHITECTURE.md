---
last_mapped_commit: a5219c2d247f9cb754ea3eb38a6cf025a52fb26c
---
<!-- refreshed: 2026-08-29 -->
# Architecture

**Analysis Date:** 2026-08-29

## System Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  Deployment / choosing layer                                                │
│  `src/cli.py`  (thresholds, ceilings, clocks, situation, label)             │
│  `src/readers/`  (pdfminer / Apple Vision adapters)                         │
│  `src/recognition/`  (compiled detector rules → ClassificationProducer)     │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ authorities + decisions
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Composition (ORDER only — no domain defaults)                              │
│  `src/production.py`  →  `run_production_corpus` / `run_production_p1_p7`     │
│                         / `run_production_p8_p11`                            │
│  `src/orchestrator.py` → `run_p1_p7` / `run_wave2`                           │
└───┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────────┘
    │         │         │         │         │         │         │
    ▼         ▼         ▼         ▼         ▼         ▼         ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐
│ P3   │ │ P5   │ │ P4   │ │ P6   │ │ P7   │ │ P2   │ │ P9   │ │ P10/P11  │
│scan_ │ │extrac│ │eviden│ │facts │ │priva │ │eval_ │ │group │ │tree_ /   │
│agent │ │tors  │ │ce_   │ │      │ │cy    │ │harne │ │ing   │ │placement │
└──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └────┬─────┘
   │        │        │        │        │        │        │          │
   │        │        └────────┴────────┴────────┴────────┴──────────┤
   │        │                         │                             │
   │        │              ┌──────────▼──────────┐                  │
   │        │              │ P8 llm_harness      │◄─────────────────┤
   │        │              │ (gated model calls) │                  │
   │        │              └──────────┬──────────┘                  │
   └────────┴─────────────────────────┴─────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  P1 substrate — single local SQLite (`database_agent`)                      │
│  `src/database_agent/db.py`  files / events / budgets / supersede / vectors │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| CLI | Sole chooser of deployment constants; wires authorities; prints plan | `src/cli.py` |
| Production | Composes P1–P11 order; loads shipped template library; validates authorities | `src/production.py` |
| Orchestrator | P3→P5→P4→P6→P7→P2 sequence; joins `scan_run_id` and extraction status | `src/orchestrator.py` |
| P1 database_agent | SQLite open/schema, identity, files table, events, budgets, supersede | `src/database_agent/` |
| P2 eval_harness | Immutable eval bundles, expectations, replay, stage dimensions | `src/eval_harness/` |
| P3 scan_agent | Only filesystem walker; selection, exclusion, stat cache, inventory | `src/scan_agent/` |
| P4 evidence_shape | Observation / text-unit / run shape; conformance; RunWriter | `src/evidence_shape/` |
| P5 extractors | Route + extract into P4 shape; stdlib-only; injected Readers | `src/extractors/` |
| P6 facts | Observations → structured claims; resolver degradation order | `src/facts/` |
| P7 privacy | Classification store, Gate.release, consent, redaction, policy | `src/privacy/` |
| P8 llm_harness | Bounded dossiers; transport; validator; sites A–E | `src/llm_harness/` |
| P9 grouping | Seeds, neighbourhood, graph, stop rules, P8 Site-B seam | `src/grouping/` |
| P10 tree_design | Horizontal/vertical design, freeze, profiles, template catalogue | `src/tree_design/` |
| P11 placement | Retrieve/score/place or abstain against frozen tree; residual sets | `src/placement/` |
| readers | Deployment adapters filling `extractors.Readers` | `src/readers/` |
| recognition | Compile/load detector rules; ClassificationProducer for P7 | `src/recognition/` |

## Pattern Overview

**Overall:** Part-numbered pipeline with injected authorities and a single SQLite working memory

**Key Characteristics:**
- Each part owns vocabulary, schema, and stage outputs; composition modules (`orchestrator.py`, `production.py`) own **order and joins only**
- Domain thresholds, catalogues, readers, clocks, and user decisions arrive as injected callables/records with **no defaults** in production composition
- LLM use is optional and always goes through P7 `Gate.release` then P8 `run_call`; deterministic paths are first-class
- After P10 freeze, destinations are a closed set; P11 places or abstains and **moves nothing**
- Evidence is extracted once per content hash and reused; REUSE via P3 stat cache skips re-extraction

## Layers

**Deployment / choosing:**
- Purpose: Bind real numbers, OS readers, recognition rules, and CLI flags
- Location: `src/cli.py`, `src/readers/`, `src/recognition/`
- Contains: Constants (`SUPPORT_POLICY`, `CEILING_VALUE`, `GROUPING_LIMITS`, …), `macos_readers()`, `Detector`
- Depends on: `production`, every part's public records
- Used by: End users / tests invoking `cli.main`

**Composition:**
- Purpose: Enforce pipeline order and authority shape without inventing domain values
- Location: `src/production.py`, `src/orchestrator.py`
- Contains: `P1P7Authorities`, `CorpusAuthorities`, `CorpusDecisions`, `run_p1_p7`, `run_production_corpus`
- Depends on: Part packages via explicit imports
- Used by: `cli.py`, integration tests

**Domain parts (P2–P11):**
- Purpose: Implement design sections; own tables and vocabularies
- Location: `src/scan_agent/` … `src/placement/` (see Component table)
- Contains: `pipeline.py` / `harness.py` / `resolver.py` / `scan.py` entry modules; `schema.py`; `store.py`; `vocabulary.py`; `stage_output.py`
- Depends on: P1 SQLite connection; upstream part stores; P8 only via explicit seams
- Used by: Composition layer

**Substrate (P1):**
- Purpose: One local database; append-only events; transactional writes
- Location: `src/database_agent/`
- Contains: `db.py`, `files_table.py`, `identity.py`, `events.py`, `budget.py`, `supersede.py`, `vectors.py`
- Depends on: stdlib `sqlite3` only
- Used by: Every part

**Planning / research (not runtime):**
- Purpose: Product design and domain research that compile into shipped libraries
- Location: `planning/`, `planning/domains/`
- Contains: Design docs, node JSON research, dispatch prompts
- Depends on: Not imported by runtime parts (except recognition compile at build time)
- Used by: Authors; `recognition.compile`; packaging into `tree_design/library/` and `recognition/library/`

## Data Flow

### Primary Request Path (directory → placement plan)

1. `cli.main` parses directory / `--situation` / `--label`, opens SQLite outside the corpus (`src/cli.py`)
2. `bootstrap_p1_p7` creates schemas in dependency order (`src/production.py`)
3. `run_production_corpus` → `run_production_p1_p7` → `run_p1_p7` (`src/production.py`, `src/orchestrator.py`)
4. P3 `scan()` walks roots, writes `files` + scan run, returns `scan_run_id` (`src/scan_agent/scan.py`)
5. Per file: route → filesystem extract + family extract → `RunWriter` persists P4 runs (`src/extractors/router.py`, `src/extractors/dispatch.py`, `src/evidence_shape/store.py`)
6. P6 `FactResolver.resolve` on native (then OCR if needed); targeted OCR when `targeted_ocr_needed` (`src/facts/resolver.py`, `src/orchestrator.py`)
7. P7 `classify` + `ClassificationStore`; P2 bundle sealed with file entries (`src/privacy/`, `src/eval_harness/bundle.py`)
8. `run_production_p8_p11`: P9 `group_subject` over `corpus_roster` (`src/grouping/pipeline.py`)
9. User `accept_groups` / design decisions → P10 `design_tree` → freeze + profiles (`src/tree_design/pipeline.py`)
10. `approve_plan` + `set_privacy_policy` → `build_destination_index` → P11 `run_corpus` (`src/placement/pipeline.py`)
11. Optional `evaluate_bundle` last (`src/eval_harness/driver.py`); CLI prints plan — files are not moved

### Wave-2 / legacy path

1. `run_wave2` runs P3→P5→P4→P2 without P6/P7 (`src/orchestrator.py`)
2. Targeted OCR predicate is hard-false via `TARGETED_OCR_UNAVAILABLE` for that legacy path only

### LLM call path (when configured)

1. Part builds `DossierRequest` + site-specific authorities (grouping Site B, placement Sites C/D, facts Site A, templates Site E)
2. `llm_harness.run_call` → eligibility / budget → `privacy.gate.Gate.release` → `transport.issue` → deterministic validation → store verdict (`src/llm_harness/harness.py`)
3. Caller maps `P8Verdict` into part records; never re-implements P8 checks

**State Management:**
- Durable state: one SQLite file (WAL, foreign keys, recursive triggers, events authorizer)
- Plan versions: §8.8 draft chain; freeze closes legal destinations for P11
- Stateless composition: authorities/decisions are per-run frozen dataclasses

## Key Abstractions

**Injected authorities:**
- Purpose: Carry every open design parameter so composition cannot invent defaults
- Examples: `src/production.py` (`P1P7Authorities`, `CorpusAuthorities`), `src/tree_design/pipeline.py` (`TreeDesignAuthorities`), `src/placement/pipeline.py` (`PipelineInputs`), `src/extractors/dispatch.py` (`Readers`)
- Pattern: Frozen dataclass; `__post_init__` type/presence checks; factories when identities are minted mid-run

**User decisions:**
- Purpose: Separate human approvals from engine proposals
- Examples: `CorpusDecisions`, `TreeDesignDecisions`, grouping acceptance records
- Pattern: Callables returning accepted ids / design choices; composition refuses to auto-accept

**Evidence shape (P4):**
- Purpose: Single observation/text-unit/run contract every extractor emits
- Examples: `src/evidence_shape/schema.py`, `src/evidence_shape/store.py` (`RunWriter`)
- Pattern: Closed vocabularies + conformance; extractors never invent private observation columns

**Stage output envelopes:**
- Purpose: Uniform measurable stage results for P2 replay
- Examples: `*/stage_output.py` under facts, extractors, grouping, placement, tree_design, llm_harness, eval_harness
- Pattern: Emit dimension values + opaque payload into eval schema

**Seams to P8:**
- Purpose: Call the model without importing gate/transport internals into domain parts
- Examples: `src/grouping/p8_seam.py`, `src/placement/p8_seam.py`, `src/facts/llm_seam.py`
- Pattern: Forward `run_call` + opaque authority bundles; boundary tests forbid forbidden imports

**Packaged libraries:**
- Purpose: Ship compiled catalogues without scanning `planning/` at runtime
- Examples: `src/tree_design/library/*.json`, `src/recognition/library/recognition.json`
- Pattern: Injected reader (`read_packaged_library_file`); digest-derived `release_id`

## Entry Points

**CLI:**
- Location: `src/cli.py` (`main`)
- Triggers: `python -m` / direct script / tests
- Responsibilities: Choose deployment constants; assemble authorities; print protected areas and placement report

**Production corpus:**
- Location: `src/production.py` (`run_production_corpus`, `run_production_p1_p7`, `run_production_p8_p11`)
- Triggers: CLI and integration tests
- Responsibilities: Schema bootstrap; order P1–P7 then P9–P11; load shipped catalogue

**Orchestrator:**
- Location: `src/orchestrator.py` (`run_p1_p7`, `run_wave2`)
- Triggers: Production composition and wave-2 tests
- Responsibilities: Scan → extract → facts → classify → bundle

**Part pipelines:**
- Location: `src/scan_agent/scan.py`, `src/facts/resolver.py`, `src/grouping/pipeline.py` (`group_subject`), `src/tree_design/pipeline.py` (`design_tree`), `src/placement/pipeline.py` (`run_corpus` / `place_file`), `src/llm_harness/harness.py` (`run_call`), `src/privacy/gate.py` (`Gate.release`)
- Triggers: Orchestrator / production / other parts via seams
- Responsibilities: Own stage contracts

## Architectural Constraints

- **Threading:** Single-threaded SQLite connections; no worker-pool architecture in `src/`
- **Global state:** Module-level packaged library paths (`_LIBRARY_DIR` in `src/production.py`); vocabulary constants; no process-wide mutable singleton for runs
- **Circular imports:** Parts must not import sibling internals across seams (e.g. grouping must not import `privacy.gate` / `llm_harness.harness` neighbours — enforced by tests such as `tests/integration/test_p9_p8_group_seam.py`); extractors must not import `readers`
- **Dependency direction:** `readers` → `extractors` (shapes only); `recognition` supplies classification to production/CLI; `planning/` is not a runtime import for part packages
- **Authorship:** Events stamp part subsystem + component version; composition modules do not appear as event authors
- **Mutation:** Append-oriented stores; supersede rather than rewrite; events table protected against UPDATE/DELETE/DROP via triggers + authorizer (`src/database_agent/db.py`)
- **Filesystem SoR:** Database never created inside a scan root (`DatabaseInsideCorpus`)

## Anti-Patterns

### Composition inventing domain values

**What happens:** Putting thresholds, catalogue choices, or situation labels inside `production.py` / `orchestrator.py`
**Why it's wrong:** Those modules are ORDER-only; inventing values makes two homes for one policy and breaks replay identity
**Do this instead:** Inject via `P1P7Authorities` / `CorpusAuthorities` / `CorpusDecisions`; choose numbers only in `src/cli.py`

### Second routing table outside P5

**What happens:** Caller switches on `extractor_name` and calls extractors directly
**Why it's wrong:** §2.9 routing lives in `src/extractors/router.py` + `dispatch.py`; a second copy drifts versions and cache keys
**Do this instead:** Call `route` then `extract_initial` / `extract_targeted_ocr` / `extract`

### Auto-accepting engine groups

**What happens:** Passing P9's proposed group ids straight into P10 without a user acceptance record
**Why it's wrong:** §5.3 builds top-level branches from **accepted** groups; engine self-approval skips the review screen
**Do this instead:** Use `CorpusDecisions.accept_groups` and only then call `design_tree`

### Importing readers into extractors

**What happens:** Naming pdfminer / Vision inside `src/extractors/`
**Why it's wrong:** P5 is stdlib-only so evidence shape is not bound to a library
**Do this instead:** Inject callables via `Readers` from `src/readers/deployment.py`

### Placing outside a frozen tree / inventing destinations

**What happens:** Emitting a destination path or node id not present on the freeze record
**Why it's wrong:** After freeze the legal set is closed; invention bypasses P10
**Do this instead:** Retrieve via `placement.retrieval` / destination index built from `FrozenTree`

## Error Handling

**Strategy:** Typed refusals and contract violations over silent empty results; unfinished work stays visible as unfinished

**Patterns:**
- Safety refusals: `ProtectedContainerRefused` (no run row), `DatalessRefused` (dataless run + status) in `src/extractors/safety.py` / orchestrator
- Configuration: `ConfigurationRequired`, `InvalidP1P7Authority`, `MissingClassificationAuthority`, `MissingCatalogueAuthority`
- P8 outcomes: `P8Verdict`, `Refusal`, `NeedsConsent`, `CallFailed`, `ValidationUnavailable` — only a verdict is a judgement
- P10/P11: `NothingToDesign`, `FreezeRefused`, abstention as successful placement outcome (`ABSTAIN_*` vocabulary)
- Reader crashes become `failed_result` runs so the scan continues (`_extract_one` / `run_p1_p7`)

## Cross-Cutting Concerns

**Logging:** Append-only `events` table + part audit trails (e.g. privacy audit before release); CLI human-readable stdout report
**Validation:** Deterministic validators in P8 (`validation.py`, site validators); P4 conformance; P10 `run_checks` V1–V6 before freeze
**Authentication:** Not a networked auth system — local privacy/consent gate (`src/privacy/gate.py`) and operation modes (`offline` default in CLI)
**Budgets / ceilings:** P1 `set_ceiling` / `get_ceiling`; parts read through own config (`facts/budgets.py`, `llm_harness/budgets.py`, placement/grouping limits)
**Replay:** P2 sealed bundles + eval adapters; extractor versions in cache keys; plan versions for tree/placement as-of reads

---

*Architecture analysis: 2026-08-29*
