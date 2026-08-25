# P10 Tree Design and Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Turn accepted P9 groups, validated P6 facts, and user-approved existing structure into an explainable, versioned, closed destination tree without changing evidence or inventing filesystem paths.

**Architecture:** P10 is a user-facing proposal and freeze layer. It reads facts/groups and emits immutable node, profile, template, residual-library, diff, and freeze records. P10 never moves files, resolves filesystem paths, reclassifies privacy, or mutates facts. Every suggestion is explainable, reviewable, reversible through a new plan version, and inert until explicit user approval.

**Tech Stack:** Python 3.12, stdlib dataclasses/sqlite3/json, existing P1 append-only events and plan versions, P2 stage outputs, P6 public reads, P7 handling classes, P9 fixtures, pytest, Graphify.

---

## Authority and dependency gates

Read `planning/00-database-agent-product-design.md` first, then `planning/04-resolutions.md`, `planning/parts/P10-tree-design-freeze/SPEC.md`, the P8/P9 planning charter, and `planning/30-p8-p9-connection-contract.md`. The original product design wins if a plan convenience conflicts with it. P10 must not edit `planning/domains/`, prompts, P6 facts, P7 classifications, P9 groups, or P12 paths.

- **G-P9:** deterministic fixtures may drive Tasks 1–8; accepted P9 groups and labels are required before a production freeze.
- **G-P8:** template-generation model calls use only P8's frozen `run_call`; P10 supplies the schema and dossier contents, never transport or privacy release.
- **G-P13:** tree edits use recorded review-action fixtures until P13 publishes its surface.
- **G-KNOWLEDGE:** missing domain schemas, template dimensions, thresholds, or residual slot values produce `ConfigurationRequired`/review, never defaults.
- **G-P12:** P10 emits node IDs and label ancestry only; it never emits or stores composed filesystem paths.

## File structure

```text
src/tree_design/vocabulary.py       closed node/template/action vocabularies
src/tree_design/records.py           Node, DestinationProfile, Template, FreezeRecord, Diff
src/tree_design/schema.py            append-only P10 tables and triggers
src/tree_design/store.py             versioned writes, current reads, supersession
src/tree_design/templates.py         schema + V1–V6 semantic validation
src/tree_design/residuals.py         nine residual definitions and enablement projection
src/tree_design/candidates.py        horizontal/vertical branch proposals
src/tree_design/health.py            warnings, counts, unresolved coverage, protected summary
src/tree_design/freeze.py            freeze validation and ID-only legality projection
src/tree_design/stage_output.py      P10→P2 template_generation/tree_design mapping
src/tree_design/fixtures.py          P11-consumable walking/realistic fixtures
tests/p10/test_p10_*.py              focused TDD suites
tests/integration/test_p10_p9_tree.py
tests/integration/test_p10_p2_replay.py
```

### Task 1: Freeze vocabularies, records, and schema

**Files:** create `src/tree_design/{vocabulary,records,schema}.py`; tests `tests/p10/test_p10_records.py`.

- [ ] Write failing round-trip tests for six artefacts: `Node`, `DestinationProfile`, `Template`, `FreezeRecord`, `NodeDiff`, and `ResidualTemplateLibrary`.
- [ ] Define exact enums from the SPEC: five node types, four node roles, three residual dispositions, shared-material policies, template dimensions, and P10 stage outcomes. Reject unknown values and filesystem path fields except `existing_path` on existing nodes.
- [ ] Add SQLite tables with append-only triggers and plan-version foreign keys. Serialize canonical JSON with stable ordering; preserve prior versions and supersession links.
- [ ] Run `pytest tests/p10/test_p10_records.py -q`; commit `feat(p10): add versioned tree records`.

### Task 2: Destination profiles and node legality

**Files:** `src/tree_design/store.py`, `src/tree_design/freeze.py`; tests `tests/p10/test_p10_legality.py`.

- [ ] Test that `accepts_placement` derives exactly from node type, protected policy, and explicit user policy; ignored nodes are visible but illegal.
- [ ] Implement `legal_destination_ids(frozen_tree)` as an ID-only lookup. Unknown IDs and known `accepts_placement=False` IDs fail closed; facts, templates, and filesystem access are not consulted.
- [ ] Test that profiles contain domain/template/expected values, parent/child context, accepted groups, exclusions, representative/rich-anchor evidence, privacy restrictions, and user edits, while nodes contain no composed path.
- [ ] Run focused tests and commit `feat(p10): publish closed destination profiles`.

### Task 3: Template schema and V1–V6 validation

**Files:** `src/tree_design/templates.py`; tests `tests/p10/test_p10_templates.py`.

- [ ] Define the custom-template JSON shape with identity/version, domain, dimensions, order, optional levels, metadata-only fields, safety constraints, and prompt/schema provenance.
- [ ] Implement six named checks from SPEC §5.7: referenced P6 fields exist; dimension order is coherent; no duplicate/repeated concept; depth is within injected ceiling; privacy constraints are compatible; generated structure is non-empty and explainable.
- [ ] Test one failing fixture per V1–V6, plus valid built-in, valid model-generated, rejected, and unapproved-inert templates. Never accept a template solely because JSON parses.
- [ ] Commit `feat(p10): validate controlled templates`.

### Task 4: Residual template library

**Files:** `src/tree_design/residuals.py`; tests `tests/p10/test_p10_residual_library.py`.

- [ ] Define all nine fixed template identities and the eight slots: display name, default parent reference, evidence patterns, file types, sensitivity restrictions, optional shallow children, maximum depth, treatment.
- [ ] Implement user-authored slot injection and enable/disable/rename/relocate/merge/replace-with-existing. Disabled templates create no node; default parents are symbolic references, never paths.
- [ ] Test all three dispositions (`physical-destination`, `review-only`, `leave-in-place`), protected/unsupported behavior, and replacement by an existing `To Sort` folder.
- [ ] Commit `feat(p10): add residual library projection`.

### Task 5: Horizontal and vertical proposal passes

**Files:** `src/tree_design/candidates.py`; tests `tests/p10/test_p10_candidates.py`.

- [ ] Build horizontal candidates only from accepted P9 groups, active P6 domains, curated existing folders, and explicit user labels; rejected groups cannot resurface.
- [ ] Build one branch at a time. Preserve purpose packets as purpose-coherent groups even when their contents differ; do not force institution-only splits.
- [ ] Require each candidate to carry explanation evidence and a stable subject ID. Missing knowledge yields a review candidate or abstention, never an invented branch.
- [ ] Test existing-vs-proposed visual/type distinction, accepted group multi-home, purpose packet, protected area, and unresolved coverage.
- [ ] Commit `feat(p10): derive explainable branch candidates`.

### Task 6: Structural feedback and tree health

**Files:** `src/tree_design/health.py`; tests `tests/p10/test_p10_health.py`.

- [ ] Implement live counts before commit: child count, member count, examples, unresolved files, evidence gaps, sensitive isolation, and accepted-group coverage.
- [ ] Emit warnings for one-child levels, repeated parent concepts, excessive depth, and tiny-folder distribution. Read thresholds through injected configuration; missing values fail closed.
- [ ] Ensure warnings are data-backed and explanations are prose/reason, never a confidence score. Test uneven depth and scoped `General` branches.
- [ ] Commit `feat(p10): add live tree health feedback`.

### Task 7: User edits, diffs, and plan-version supersession

**Files:** `src/tree_design/store.py`, `src/tree_design/diff.py`; tests `tests/p10/test_p10_versions.py`.

- [ ] Apply review actions to a draft only: add/remove/rename/merge/split/nest/reorder/ignore/adopt existing/create custom residual branch. Every accepted edit creates a new plan version.
- [ ] Produce node-level diffs with added/removed/renamed/reparented/reordered nodes, renewed-review decisions, and template/residual changes. Never rewrite a frozen version.
- [ ] Preserve facts, values, groups, evidence, and original paths byte-for-byte. Test restoring/adopting a prior version and meaningful diff output.
- [ ] Commit `feat(p10): version user tree edits without rewriting evidence`.

### Task 8: Freeze and P2 stage output

**Files:** `src/tree_design/freeze.py`, `src/tree_design/stage_output.py`; tests `tests/p10/test_p10_freeze.py`, `tests/integration/test_p10_p2_replay.py`.

- [ ] Require explicit freeze action, complete node/profile/residual validation, unique IDs, valid parents, no cycles, explainable nodes, and legal protected policies.
- [ ] Emit P2 `template_generation` and `tree_design` envelopes using existing seven-field version tuples. Map produced/abstained/deferred/error distinctly; never emit a P10-private stage ID.
- [ ] Test ID-only destination legality, no path strings, disabled residual unreachable, template approval gate, and replay from user-action log.
- [ ] Commit `feat(p10): freeze closed tree and emit replay stages`.

### Task 9: Fixtures, integration, and north-star UX guards

**Files:** `src/tree_design/fixtures.py`; tests `tests/p10/test_p10_fixtures.py`, `tests/integration/test_p10_p9_tree.py`, `tests/p10/test_p10_no_invention.py`.

- [ ] Publish the two-node walking tree, realistic uneven tree, five node types, scoped General, protected branch, shared-material policy, all residual dispositions, three template fixtures, V1–V6 failures, two-version diff, and residual library fixture.
- [ ] Assert every user-facing proposal exposes reason, strongest evidence, uncertainty, affected files, and next action; existing structure is visibly distinct; no confidence-only explanation is accepted.
- [ ] AST/schema guard against prompts, domains, path composition, filesystem mutations, fact writes, P11/P12 imports, and hidden numeric defaults.
- [ ] Run `pytest tests/p10 tests/integration/test_p10_p9_tree.py -q`; commit `test(p10): lock tree freeze boundaries`.

### Task 10: Final verification

- [ ] Run `python3.12 -m compileall -q src tests` and the focused P10/P1–P9 integration suite.
- [ ] Run `graphify update .` and `graphify diagnose multigraph --json --max-examples 20`; verify P9→P10 is visible and no P10→P11/P12 runtime edge exists before those parts ship.
- [ ] Re-read the original product design and confirm: facts stay separate, existing folders are not silently changed, destinations are closed after freeze, users can revise the view without data loss, and no P10 path can move a file.

## Explicitly deferred

Domain-specific template contents, prompt wording, canvas visual layout, warning copy, numeric depth/warning thresholds, and P13 runtime review are authored dependencies. Do not invent them to make fixtures green.

## Coverage

| Requirement | Tasks |
|---|---|
| Closed tree, profiles, freeze, versioning | 1, 2, 7, 8 |
| Controlled templates and residual library | 3, 4 |
| Explainable user-first branch design | 5, 6, 9 |
| No path invention or filesystem mutation | 2, 8, 9 |
| P2 replay and original mission fidelity | 8, 10 |
