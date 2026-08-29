---
last_mapped_commit: a5219c2d247f9cb754ea3eb38a6cf025a52fb26c
---
# Codebase Structure

**Analysis Date:** 2026-08-29

## Directory Layout

```
database-agent-build/
├── src/                      # Installable Python package root (setuptools where=["src"])
│   ├── cli.py                # Deployment chooser + CLI entry
│   ├── production.py         # P1–P11 composition (order only)
│   ├── orchestrator.py       # P1–P7 / wave-2 sequencing
│   ├── database_agent/       # P1 — SQLite substrate
│   ├── eval_harness/         # P2 — bundles, replay, eval schema
│   ├── scan_agent/           # P3 — corpus walk / selection
│   ├── evidence_shape/       # P4 — observation/run shape
│   ├── extractors/           # P5 — route + extract (stdlib)
│   ├── facts/                # P6 — fact resolution
│   ├── privacy/              # P7 — classification + Gate
│   ├── llm_harness/          # P8 — bounded LLM + validator
│   ├── grouping/             # P9 — evidence grouping
│   ├── tree_design/          # P10 — tree design + freeze
│   │   └── library/          # Shipped template JSON release
│   ├── placement/            # P11 — place / abstain / residual
│   ├── readers/              # Deployment format adapters (optional extra)
│   └── recognition/          # Detector rule compile/load
│       └── library/          # Shipped recognition.json
├── tests/                    # pytest suite (pythonpath = src)
│   ├── p3/…/p11/             # Part-scoped unit/contract tests
│   ├── integration/          # Cross-part live paths
│   ├── eval/                 # Eval-harness focused tests
│   ├── readers/              # Reader adapter tests
│   ├── recognition/          # Detector tests
│   └── wave2/                # Wave-2 orchestrator tests
├── planning/                 # Product design + domain research (not runtime)
│   └── domains/              # Node research JSON/MD, dispatch prompts
├── docs/                     # Ancillary docs / superpowers plans
├── .planning/                # GSD state + codebase maps
├── pyproject.toml            # Package metadata, pytest, optional [readers]
└── README.md                 # Product loop + design pointer
```

## Directory Purposes

**`src/`:**
- Purpose: All runtime and deployment code; packages discovered under this tree
- Contains: Part packages (P1–P11), composition modules, readers, recognition
- Key files: `src/cli.py`, `src/production.py`, `src/orchestrator.py`

**`src/database_agent/`:**
- Purpose: P1 storage, identity, provenance, ceilings, supersede, vectors
- Contains: `db.py`, `files_table.py`, `identity.py`, `events.py`, `budget.py`, `learning.py`, `verify.py`
- Key files: `src/database_agent/db.py` (`open_database`, `create_schema`)

**`src/scan_agent/`:**
- Purpose: P3 filesystem traversal and corpus selection only
- Contains: `scan.py`, `traversal.py`, `exclusion.py`, `selection.py`, `stat_cache.py`, `corpus_source.py`, `schema.py`
- Key files: `src/scan_agent/scan.py`, `src/scan_agent/stat_cache.py`

**`src/evidence_shape/`:**
- Purpose: P4 evidence contract and persistence helpers
- Contains: `schema.py`, `store.py`, `observation.py`, `text_units.py`, `conformance.py`, `canonical.py`
- Key files: `src/evidence_shape/store.py` (`RunWriter`, run/observation queries)

**`src/extractors/`:**
- Purpose: P5 routing and format extraction into P4 shape
- Contains: `router.py`, `dispatch.py`, per-family modules (`pdf.py`, `docx.py`, `ocr.py`, …), `safety.py`, `sink.py`
- Key files: `src/extractors/dispatch.py`, `src/extractors/router.py`

**`src/facts/`:**
- Purpose: P6 claims with evidence; resolver sequencing
- Contains: `resolver.py`, producers (`direct.py`, `rules.py`, …), `schema.py`, `usable.py`, `llm_seam.py`
- Key files: `src/facts/resolver.py`, `src/facts/usable.py`

**`src/privacy/`:**
- Purpose: P7 handling classes, consent, Gate.release, redaction
- Contains: `gate.py`, `classification.py`, `classification_store.py`, `policy.py`, `release.py`, `audit.py`
- Key files: `src/privacy/gate.py`, `src/privacy/classification_store.py`

**`src/llm_harness/`:**
- Purpose: P8 dossier build, transport, validation, site dispatch
- Contains: `harness.py`, `transport.py`, `dossier.py`, `sites.py`, `*_validation.py`, `store.py`
- Key files: `src/llm_harness/harness.py` (`run_call`)

**`src/grouping/`:**
- Purpose: P9 seeds → graph → optional Site-B call → memberships
- Contains: `pipeline.py`, `seeds.py`, `graph.py`, `retrieval.py`, `dossier.py`, `p8_seam.py`, `store.py`
- Key files: `src/grouping/pipeline.py` (`group_subject`)

**`src/tree_design/`:**
- Purpose: P10 branch design, materialise, freeze, profiles
- Contains: `pipeline.py`, `candidates.py`, `routing.py`, `freeze.py`, `catalogue.py`, `library/*.json`
- Key files: `src/tree_design/pipeline.py` (`design_tree`), `src/tree_design/catalogue.py`

**`src/placement/`:**
- Purpose: P11 retrieval/scoring/placement and residual workflow
- Contains: `pipeline.py`, `retrieval.py`, `scoring.py`, `residual.py`, `index.py`, `p8_seam.py`, `store.py`
- Key files: `src/placement/pipeline.py` (`run_corpus`, `place_file`)

**`src/eval_harness/`:**
- Purpose: P2 immutable bundles and evaluation/replay
- Contains: `bundle.py`, `driver.py`, `store.py`, `assertions.py`, `replay.py`, `shadow.py`
- Key files: `src/eval_harness/bundle.py`, `src/eval_harness/driver.py`

**`src/readers/`:**
- Purpose: Optional third-party adapters for `Readers` injection
- Contains: `deployment.py`, `pdf_pdfminer.py`, `ocr_vision.py`
- Key files: `src/readers/deployment.py` (`macos_readers`)

**`src/recognition/`:**
- Purpose: Compile and apply sensitivity/classification detectors for P7
- Contains: `compile.py`, `rules.py`, `detector.py`, `library/recognition.json`
- Key files: `src/recognition/detector.py`, `src/recognition/rules.py`

**`tests/`:**
- Purpose: Contract and integration coverage mirrored by part number
- Contains: `tests/p{N}/`, `tests/integration/`, root-level P1/seam tests
- Key files: `tests/conftest.py`, `tests/test_cli.py`, `tests/integration/test_live_path.py`

**`planning/`:**
- Purpose: Design authority and domain research feeding shipped libraries
- Contains: Numbered design/plan markdown, `domains/nodes/`, `domains/dispatch/`
- Key files: `planning/00-database-agent-product-design.md` (product contract)

**`.planning/`:**
- Purpose: GSD project state and generated codebase maps
- Contains: `codebase/ARCHITECTURE.md`, `codebase/STRUCTURE.md`, handoff/state as present
- Key files: `.planning/codebase/`

## Key File Locations

**Entry Points:**
- `src/cli.py`: User-facing command; only file that chooses deployment numbers
- `src/production.py`: `run_production_corpus` / bootstrap / catalogue load
- `src/orchestrator.py`: `run_p1_p7`, `run_wave2`

**Configuration:**
- `pyproject.toml`: package name `database-agent`, Python `3.12.*`, empty runtime deps, `[readers]` extra, pytest `pythonpath=["src"]`
- `src/cli.py` (constants block): ceilings, support policy, tree/grouping limits, operation mode
- Part `config.py` modules: `src/grouping/config.py`, `src/tree_design/config.py`, `src/placement/config.py` (require injected limits; refuse silent defaults)

**Core Logic:**
- `src/scan_agent/scan.py`: corpus scan
- `src/extractors/dispatch.py`: extraction passes
- `src/facts/resolver.py`: fact producers in degradation order
- `src/privacy/gate.py`: sole content egress door
- `src/llm_harness/harness.py`: `run_call`
- `src/grouping/pipeline.py`: `group_subject`
- `src/tree_design/pipeline.py`: `design_tree`
- `src/placement/pipeline.py`: `run_corpus` / placement STEPS

**Schema / store:**
- Each part: `schema.py` + `store.py` (or `*_store.py`) under its package
- P1: `src/database_agent/db.py`
- Bootstrap order: `production.bootstrap_p1_p7` then CLI creates grouping/tree/placement schemas as needed

**Testing:**
- `tests/p3` … `tests/p11`: part contracts
- `tests/integration/`: multi-part paths
- `tests/eval/`: eval harness
- Root `tests/test_*.py`: P1 substrate and cross-seam guards

**Shipped data:**
- `src/tree_design/library/`: fragments, definitions, applicabilities, wave2_* packs
- `src/recognition/library/recognition.json`: compiled detector manifest

## Naming Conventions

**Files:**
- `snake_case.py` for all modules
- `pipeline.py`: end-to-end stage chain for a part (P9/P10/P11)
- `schema.py`: DDL / table creation for that part
- `store.py`: persistence API (record/read)
- `vocabulary.py`: closed string constants for that part
- `stage_output.py`: P2-measurable stage envelopes
- `records.py`: frozen dataclasses for domain objects
- `*_seam.py`: boundary adapters to another part (especially P8)
- `fixtures.py`: in-package test helpers when present

**Directories:**
- Part package name matches role, not always the P-number (`scan_agent` = P3, `evidence_shape` = P4, `eval_harness` = P2)
- `library/` under a package = committed shipped artefacts, not generated at import time
- `tests/pN/` mirrors part number from the design segmentation map

**Symbols:**
- Frozen `@dataclass` for authorities, decisions, results
- `UPPER_SNAKE` for vocabulary constants and closed enums-as-strings
- Public package entry often re-exported thinly from `__init__.py` (or left as a marker docstring only)

## Where to Add New Code

**New Feature (along the user loop):**
- Primary code: the owning part package under `src/<part>/` (never invent a parallel vocabulary in composition)
- Wire order only in `src/production.py` / `src/orchestrator.py` if a new stage must run
- Deployment constants / wiring: `src/cli.py`
- Tests: `tests/pN/` for the part; `tests/integration/` for cross-part joins

**New extractor family / format:**
- Implementation: new module under `src/extractors/` + router entry in `src/extractors/router.py` + dispatch half in `src/extractors/dispatch.py`
- Reader adapter (if third-party): `src/readers/` and inject via `Readers`
- Tests: `tests/p5/`

**New fact producer or field:**
- Implementation: `src/facts/` producer module; bind as a `Stage` into `FactResolver` from CLI/production authorities
- Schema/fields catalogue: `src/facts/fields.py` / related schema modules
- Tests: `tests/p6/`

**New LLM site or validator rule:**
- Implementation: `src/llm_harness/sites.py` + appropriate `*_validation.py`
- Callers reach it only through `run_call` / part `*_seam.py`
- Tests: `tests/p8/`

**New grouping / tree / placement behaviour:**
- Grouping: `src/grouping/` (pipeline stages, not destination concepts)
- Tree: `src/tree_design/` (no file moves; freeze before placement)
- Placement: `src/placement/` (node ids only; residual in `residual.py`)
- Template library content: JSON under `src/tree_design/library/` then load via `production.load_shipped_catalogue`
- Tests: `tests/p9/`, `tests/p10/`, `tests/p11/`

**New privacy classification signal:**
- Do not put regex/gazetteers in `src/privacy/`
- Author/compile under `src/recognition/` (and planning research if needed); ship updated `recognition/library/`
- Tests: `tests/recognition/`, `tests/p7/`

**Utilities:**
- Shared helpers: keep inside the owning part; cross-cutting storage helpers belong in `src/database_agent/`
- Do not add a generic `src/utils/` unless a part contract requires it

**Composition-only changes:**
- Order, joins, authority validation: `src/production.py` / `src/orchestrator.py`
- Never add thresholds or catalogue defaults there

## Special Directories

**`src/tree_design/library/`:**
- Purpose: Packaged template release files joined by `production.shipped_catalogue_manifest`
- Generated: No (hand-authored / release artefacts)
- Committed: Yes

**`src/recognition/library/`:**
- Purpose: Versioned recognition manifest consumed via injected reader
- Generated: Produced by compile workflow from planning nodes; runtime only reads
- Committed: Yes (`recognition.json`)

**`planning/`:**
- Purpose: Design + domain research source of truth for authors
- Generated: No
- Committed: Yes
- Runtime: Not imported by part packages (recognition `compile` is the intentional build-time exception)

**`src/database_agent.egg-info/` / `.venv/` / `__pycache__/`:**
- Purpose: Build/install/cache artefacts
- Generated: Yes
- Committed: No (respect `.gitignore`)

**`.planning/codebase/`:**
- Purpose: GSD architecture maps for planners/executors
- Generated: By `/gsd-map-codebase` mappers
- Committed: Yes when the project tracks planning state

---

*Structure analysis: 2026-08-29*
