# P10 Tree Design and Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Turn accepted P9 groups, validated P6 facts, and user-approved existing structure into an explainable, versioned, closed destination tree without changing evidence or inventing filesystem paths.

**Architecture:** P10 is a user-facing proposal and freeze layer. It reads facts/groups and emits immutable node, profile, template, residual-library, diff, and freeze records. P10 never moves files, resolves filesystem paths, reclassifies privacy, or mutates facts. Every suggestion is explainable, reviewable, reversible through a new plan version, and inert until explicit user approval.

**Tech Stack:** Python 3.12, stdlib dataclasses/sqlite3/json, existing P1 append-only events and plan versions, P2 stage outputs, P6 public reads, P7 handling classes, P9 fixtures, pytest, Graphify.

---

## Authority and dependency gates

Read `planning/00-database-agent-product-design.md` first, then `planning/04-resolutions.md`, `planning/parts/P10-tree-design-freeze/SPEC.md`, `docs/superpowers/specs/2026-08-26-composable-template-scaffolding-design.md`, the P8/P9 planning charter, and `planning/30-p8-p9-connection-contract.md`. The original product design wins if a plan convenience conflicts with it. P10 must not edit `planning/domains/`, prompts, P6 facts, P7 classifications, P9 groups, or P12 paths.

The full authored-library pass is separately gated in
`docs/superpowers/plans/2026-08-26-composable-template-library.md`. P10 Tasks 1–4 build the runtime
contracts and deterministic fixtures first; they do not bulk-import unfinished domain research.

- **G-P9:** deterministic fixtures may drive Tasks 1–9; accepted P9 groups and labels are required before a production freeze.
- **G-P8:** template-generation model calls use only P8's frozen `run_call`; P10 supplies the schema and dossier contents, never transport or privacy release.
- **G-P13:** tree edits use recorded review-action fixtures until P13 publishes its surface.
- **G-KNOWLEDGE:** missing domain schemas, applicability bindings, fragment versions, role-to-P6-field mappings, template dimensions, thresholds, or residual slot values produce `ConfigurationRequired`/review, never defaults.
- **G-P12:** P10 emits node IDs and label ancestry only; it never emits or stores composed filesystem paths.

## File structure

```text
src/tree_design/vocabulary.py       closed node/template/action vocabularies
src/tree_design/records.py           Node, profiles, template records, FreezeRecord, Diff
src/tree_design/schema.py            append-only P10 tables and triggers
src/tree_design/store.py             versioned writes, current reads, supersession
src/tree_design/templates.py         definitions/fragments + V1–V6 semantic validation
src/tree_design/routing.py           many-to-many applicability and composition gates C1–C8
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

- [ ] Write failing round-trip tests for the frozen artefacts plus exact P10 types `TemplateFragment`, `TemplateDefinition`, `TemplateApplicability`, and branch-local `BranchTemplateBinding`; publish no parallel generic `Template` type, and keep reusable definitions separate from plan-version choices.
- [ ] Define exact enums from the SPEC: five node types, four node roles, three residual dispositions, shared-material policies, template dimensions, and P10 stage outcomes. Reject unknown values and filesystem path fields except `existing_path` on existing nodes.
- [ ] Add append-only SQLite tables. Key shared `TemplateFragment`, `TemplateDefinition`, and
  `TemplateApplicability` rows by immutable library release plus record version; attach plan-version
  foreign keys only to branch bindings, nodes, profiles, diffs, and freeze state. Serialize canonical
  JSON with stable ordering and preserve prior versions/supersession links.
- [ ] Run `pytest tests/p10/test_p10_records.py -q`; commit `feat(p10): add versioned tree records`.

### Task 2: Destination profiles and node legality

**Files:** `src/tree_design/store.py`, `src/tree_design/freeze.py`; tests `tests/p10/test_p10_legality.py`.

- [ ] Test that `accepts_placement` derives exactly from node type, protected policy, and explicit user policy; ignored nodes are visible but illegal.
- [ ] Implement `legal_destination_ids(frozen_tree)` as an ID-only lookup. Unknown IDs and known `accepts_placement=False` IDs fail closed; facts, templates, and filesystem access are not consulted.
- [ ] Test that profiles contain domain/template/expected values, parent/child context, accepted groups, exclusions, representative/rich-anchor evidence, privacy restrictions, and user edits, while nodes contain no composed path.
- [ ] For a composed purpose branch, require `domains[]` and one branch-local binding with exact
  template/fragment provenance per node; never collapse it to an invented primary domain.
- [ ] Run focused tests and commit `feat(p10): publish closed destination profiles`.

### Task 3: Template schema and V1–V6 validation

**Files:** `src/tree_design/templates.py`; tests `tests/p10/test_p10_templates.py`.

- [ ] Define four closed schemas: `TemplateFragment`, `TemplateDefinition`, standalone
  `TemplateApplicability` with its own ID/version and exact definition reference, and
  `BranchTemplateBinding` with exact applicability refs. Split `origin_kind`, `scope_kind`, and
  `publication_state`; never nest applicability or branch evidence inside a reusable definition.
- [ ] Validate fragment imports as an acyclic exact-version graph. Merge allowed-value sets by
  intersection, relative-order constraints by union plus cycle detection, privacy by the strongest
  included restriction, and optionality/cardinality by explicit compatible rules. Fragments contain
  no user/initial values, and semantic conflicts never use last-writer-wins.
- [ ] Implement and test the six named checks exactly as SPEC §5.7 defines them: V1 repeated parent
  dimension; V2 meaningless one-child level; V3 practical-depth ceiling; V4 author/organization used
  merely as collector; V5 protected-information exposure; V6 empty branch against the accepted group.
  Live-field and ordering checks remain C2/C5 pre-gates, not replacements for V1–V6.
- [ ] Test one failing fixture per V1–V6, plus valid built-in, valid model-generated, rejected, and unapproved-inert templates. Prove published definitions are immutable and newer versions do not migrate existing branch bindings.
- [ ] Commit `feat(p10): validate controlled templates`.

### Task 4: Many-to-many applicability and branch-local composition

**Files:** `src/tree_design/routing.py`, `src/tree_design/store.py`; tests `tests/p10/test_p10_template_routing.py`.

- [ ] Write failing tests proving one template version can serve two domains without duplication, one domain can offer two explained templates, and one purpose-coherent mixed-domain branch can combine compatible fragments.
- [ ] Implement the deterministic route: branch context → eligible applicability bindings → bounded candidate compositions → C1–C8 report → inert preview. Domain is one signal, never a one-template ownership key; missing bindings fail closed.
- [ ] Resolve every semantic role to a live P6 field, exact fragment version, and provenance source. Reject ambiguous mappings, cyclic order, weaker combined privacy, unsupported applicability, or silent member loss; create no nodes on conflict.
- [ ] Persist exact applicability IDs/versions and selected/omitted/reordered/flattened dimensions only
  in `BranchTemplateBinding`. Applying or editing a recipe in one branch must not change another
  branch using the same definition; newer definition, fragment, or applicability versions remain inert.
- [ ] Run `pytest tests/p10/test_p10_template_routing.py -q`; commit `feat(p10): route composable templates by branch evidence`.

### Task 5: Residual template library

**Files:** `src/tree_design/residuals.py`; tests `tests/p10/test_p10_residual_library.py`.

- [ ] Define all nine fixed template identities and the eight slots: display name, default parent reference, evidence patterns, file types, sensitivity restrictions, optional shallow children, maximum depth, treatment.
- [ ] Implement user-authored slot injection and enable/disable/rename/relocate/merge/replace-with-existing. Disabled templates create no node; default parents are symbolic references, never paths.
- [ ] Test all three dispositions (`physical-destination`, `review-only`, `leave-in-place`), protected/unsupported behavior, and replacement by an existing `To Sort` folder.
- [ ] Commit `feat(p10): add residual library projection`.

### Task 6: Horizontal and vertical proposal passes

**Files:** `src/tree_design/candidates.py`; tests `tests/p10/test_p10_candidates.py`.

- [ ] Build horizontal candidates only from accepted P9 groups, active P6 domains, curated existing folders, and explicit user labels; rejected groups cannot resurface.
- [ ] Keep the first horizontal scaffold shallow and template-independent. Let the user approve, rename, merge, move, remove, or create major branches before any vertical recipe is activated; an unrefined or shallow-by-choice branch remains valid.
- [ ] Build one branch at a time while preserving compact root context, current path, siblings,
  workflow state (`draft`, `reviewed`, `approved`), and depth disposition (`refined`,
  `shallow-by-choice`, `refine-later`) with its reason. Preserve purpose packets as purpose-coherent
  groups even when their contents differ; do not force institution-only splits.
- [ ] For vertical work, show routed complete templates, compatible fragment compositions, and the no-split option. Permit subset, reorder, rename, flatten, or extension before branch-specific approval.
- [ ] Require each candidate to carry explanation evidence and a stable subject ID. Missing knowledge yields a review candidate or abstention, never an invented branch.
- [ ] Test existing-vs-proposed visual/type distinction, accepted group multi-home, purpose packet, protected area, and unresolved coverage.
- [ ] Commit `feat(p10): derive explainable branch candidates`.

### Task 7: Structural feedback and tree health

**Files:** `src/tree_design/health.py`; tests `tests/p10/test_p10_health.py`.

- [ ] Implement live counts before commit: child count, member count, examples, unresolved files, evidence gaps, sensitive isolation, and accepted-group coverage.
- [ ] Recompute counts for the proposed state across the edited node and visible ancestors/siblings. Expose stale/loading state; never collapse the active branch or move keyboard focus when counts refresh.
- [ ] Emit warnings for one-child levels, repeated parent concepts, excessive depth, and tiny-folder distribution. Read thresholds through injected configuration; missing values fail closed.
- [ ] Ensure warnings are data-backed and explanations are prose/reason, never a confidence score. Test uneven depth, scoped `General` branches, empty-by-design versus unrefined state, and canonical counts through aliases/multiple views.
- [ ] Commit `feat(p10): add live tree health feedback`.

### Task 8: User edits, diffs, and plan-version supersession

**Files:** `src/tree_design/store.py`, `src/tree_design/diff.py`; tests `tests/p10/test_p10_versions.py`.

- [ ] Apply review actions to a draft only: add/remove/rename/merge/split/nest/reorder/ignore/adopt existing/create custom residual branch. Every accepted edit creates a new plan version.
- [ ] Produce node-level diffs with added/removed/renamed/reparented/reordered nodes, renewed-review decisions, template/fragment/binding/residual changes, affected counts, and semantic undo labels. Never rewrite a frozen version.
- [ ] Preserve facts, values, groups, evidence, and original paths byte-for-byte. Test restoring/adopting a prior version and meaningful diff output.
- [ ] Commit `feat(p10): version user tree edits without rewriting evidence`.

### Task 9: Freeze and P2 stage output

**Files:** `src/tree_design/freeze.py`, `src/tree_design/stage_output.py`; tests `tests/p10/test_p10_freeze.py`, `tests/integration/test_p10_p2_replay.py`.

- [ ] Require explicit freeze action, complete node/profile/residual validation, unique IDs, valid parents, no cycles, explainable nodes, legal protected policies, and an explicit depth disposition/reason for every approved branch. Completeness does not require equal depth or every optional template dimension; later refinement opens a new draft.
- [ ] Emit P2 `template_generation` and `tree_design` envelopes using existing seven-field version tuples. Map produced/abstained/deferred/error distinctly; never emit a P10-private stage ID.
- [ ] Test ID-only destination legality, no path strings, disabled residual unreachable, template approval gate, and replay from user-action log.
- [ ] Commit `feat(p10): freeze closed tree and emit replay stages`.

### Task 10: Fixtures, integration, and north-star UX guards

**Files:** `src/tree_design/fixtures.py`; tests `tests/p10/test_p10_fixtures.py`, `tests/integration/test_p10_p9_tree.py`, `tests/p10/test_p10_no_invention.py`.

- [ ] Publish the two-node walking tree, realistic uneven tree, five node types, scoped General, protected branch, shared-material policy, all residual dispositions, one-template/two-domain, one-domain/two-template, compatible cross-domain composition, deterministic conflict, V1–V6 failures, two-version diff, and residual library fixtures.
- [ ] Assert every user-facing proposal exposes reason, strongest evidence, uncertainty, affected files, and next action; existing structure is visibly distinct; no confidence-only explanation is accepted.
- [ ] Assert top-level-only approval, shallow-by-choice, differently matured siblings, branch-local
  template edits, subset application, preview counts/examples/privacy/diff, and no automatic
  definition/fragment/applicability migration.
- [ ] AST/schema guard all `src/tree_design/` against any `planning.*` or prompt import, repository
  scanning, path composition, filesystem mutations, fact writes, P11/P12 imports, copied authored
  catalogue JSON, and hidden numeric defaults. Only the offline compiler may read planning sources.
- [ ] Run `pytest tests/p10 tests/integration/test_p10_p9_tree.py -q`; commit `test(p10): lock tree freeze boundaries`.

### Task 11: Final verification

- [ ] Run `python3.12 -m compileall -q src tests` and the focused P10/P1–P9 integration suite.
- [ ] Run `graphify update .` and `graphify diagnose multigraph --json --max-examples 20`; verify P9→P10 is visible and no P10→P11/P12 runtime edge exists before those parts ship.
- [ ] Re-read the original product design and confirm: facts stay separate, existing folders are not silently changed, destinations are closed after freeze, users can revise the view without data loss, and no P10 path can move a file.

## Explicitly deferred

Domain-specific applicability content, reusable-fragment catalogue contents, full template-library contents, prompt wording, canvas visual layout, warning copy, numeric depth/warning thresholds, and P13 runtime review are authored dependencies. Domain and prompt work must publish versioned records through a named later compilation step; P10 never reads research Markdown or prompt files at runtime. Do not invent missing content to make fixtures green.

## Coverage

| Requirement | Tasks |
|---|---|
| Closed tree, profiles, freeze, versioning | 1, 2, 8, 9 |
| Controlled, composable templates and many-to-many routing | 3, 4 |
| Residual library | 5 |
| Explainable scaffold-first branch design | 6, 7, 10 |
| No path invention or filesystem mutation | 2, 9, 10 |
| P2 replay and original mission fidelity | 9, 11 |
