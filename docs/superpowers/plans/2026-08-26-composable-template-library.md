# Composable Template Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn ratified domain research into a versioned library of reusable template fragments,
assembled definitions, and one-schema applicability bindings that P10 can route, preview, validate,
and place under explicit user control.

**Architecture:** Domain catalogue rows remain research/authorship records with one `uses_schema` each.
A deterministic offline compiler extracts separately reviewed shared fragments and definitions, joins
them to one-schema applicability records, validates composition, and emits a packaged immutable
catalogue. P10 receives that catalogue through its loader; it never imports `planning/domains/` or
prompt files at runtime.

**Tech Stack:** Python 3.12, JSON, stdlib dataclasses/hashlib/pathlib, existing P6 field catalogue,
P10 records/routing contracts, pytest, Graphify.

---

## Do-not-start gates

This plan is for the template-building pass **after** domain research, not for the current P8 build.

- **G-DOMAINS:** the selected domain rows and their research memos are ratified and the active claim
  swarm has stopped writing them.
- **G-P10:** P10 Tasks 1–4 have published `TemplateFragment`, `TemplateDefinition`,
  `TemplateApplicability`, `BranchTemplateBinding`, and C1–C8 validation.
- **G-FIELDS:** every applicability mapping targets the live P6 catalogue; missing future fields are
  explicit configuration gaps, never created here.
- **G-SELECTION:** the user approves the release-wave manifest. The design's eventual 200–300 library
  is not a licence to publish every research row automatically.
- **G-PROMPTS:** prompt wording may be developed concurrently, but it cannot become a source of
  definitions, bindings, fields, thresholds, privacy rules, or activation.

Read `planning/00-database-agent-product-design.md`,
`docs/superpowers/specs/2026-08-26-composable-template-scaffolding-design.md`,
`planning/domains/TEMPLATE-BUILDING-HANDOFF.md`, the P10 SPEC, and the P10 plan before beginning.

## File structure

```text
planning/templates/_CONTRACT.md                 closed authoring and versioning shape
planning/templates/release-manifest.json        user-approved rows/definitions in this wave
planning/templates/role-vocabulary.json         organization roles; never P6 facts
planning/templates/fragments/*.json             canonical reusable fragments
planning/templates/definitions/*.json           thin assembled template definitions
planning/templates/applicability/*.json         one-schema domain/purpose bindings
planning/templates/reviews/*.md                  reuse/refusal and provenance judgments
planning/templates/check.py                      authoring graph and semantic gate
tools/compile_tree_templates.py                  deterministic offline compiler
src/tree_design/catalogue.py                     packaged-catalogue loader only
src/tree_design/catalogue_data/manifest.json     immutable compiled release
tests/template_library/test_*.py                 authoring/compiler contract tests
tests/p10/test_p10_catalogue_routing.py           compiled-library runtime tests
tests/integration/test_template_library_p8_p10.py custom-proposal/validation seam
```

### Task 1: Freeze the authoring contract and release manifest

**Files:** create `planning/templates/_CONTRACT.md`, `release-manifest.json`,
`role-vocabulary.json`; tests `tests/template_library/test_contract.py`.

- [ ] Write failing tests for closed keys, stable IDs, exact versions, immutable published records,
  one `uses_schema` per applicability row, and role names that cannot collide with or create P6 fields.
- [ ] Define separate JSON shapes for fragments, definitions, applicability rows, and reviews. Forbid
  copied field lists, embedded prompt text, numeric thresholds, path strings, activation flags, and
  version ranges in a published release. Separate `origin_kind`, `scope_kind`, and
  `publication_state`; do not treat “user-saved” as both provenance and scope.
- [ ] Define the release manifest as an explicit allow-list of ratified source rows plus selected
  definition/applicability IDs. Unlisted domain research cannot enter the compiled catalogue.
- [ ] Run `pytest tests/template_library/test_contract.py -q`; commit
  `docs(templates): freeze composable library contract`.

### Task 2: Build the evidence-backed reuse inventory

**Files:** create `planning/templates/reviews/reuse-inventory.md`; tests
`tests/template_library/test_inventory.py`.

- [ ] For every selected source row, record its schema, dimension fields, normalized semantic roles,
  relative-order constraints, optionality, branch patterns, privacy constraints, retrieval purpose,
  and provenance links.
- [ ] Cluster candidates only by semantic role and compatible constraints, not label or industry
  similarity. Record both supporting contexts and tempting false matches for every proposed fragment.
- [ ] Give each candidate one judgment: `share-definition`, `share-fragment`, `keep-separate`, or
  `insufficient-evidence`, with a written reason. Refusal is a successful output.
- [ ] Test that every selected source row receives exactly one judgment and every shared candidate has
  at least two independently reviewed applicability contexts.
- [ ] Commit `docs(templates): inventory cross-domain reuse candidates`.

### Task 3: Author and validate reusable fragments

**Files:** create `planning/templates/fragments/*.json`, `planning/templates/check.py`; tests
`tests/template_library/test_fragments.py`.

- [ ] Write failing fixtures for duplicate role IDs, cyclic imports/order, unpinned versions,
  incompatible value semantics, conflicting constraints, domain labels inside canonical roles, and a
  fragment supported by only one context.
- [ ] Author only approved `share-fragment` candidates. Store stable role sequence, relative order,
  optionality, metadata-only hints, privacy floor, and provenance; store no user values or field
  mappings.
- [ ] Implement deterministic import resolution as an acyclic exact-version graph. Resolve a canonical
  snapshot with source provenance and reject last-writer-wins semantics.
- [ ] Run `pytest tests/template_library/test_fragments.py -q`; commit
  `feat(templates): author reusable organization fragments`.

### Task 4: Assemble thin template definitions

**Files:** create `planning/templates/definitions/*.json`; tests
`tests/template_library/test_definitions.py`.

- [ ] Write failing tests for missing fragments, duplicated roles, incoherent relative order, weaker
  privacy than an imported fragment, mandatory full-depth realization, and hidden migration to a
  newer fragment version.
- [ ] Build definitions from exact fragment versions plus the smallest necessary local roles and
  constraints. Keep display examples separate from semantic identity; order remains a recommendation.
- [ ] Record scope, out-of-scope cases, provenance, and whether the definition is domain-focused,
  cross-domain, purpose-focused, or personal; record built-in/LLM/user authorship on the separate
  origin axis and draft/published/retired on the lifecycle axis.
- [ ] Test that a published definition resolves byte-for-byte identically on replay and remains valid
  when a newer fragment exists but is not referenced.
- [ ] Commit `feat(templates): assemble immutable template definitions`.

### Task 5: Author one-schema applicability bindings

**Files:** create `planning/templates/applicability/*.json`; tests
`tests/template_library/test_applicability.py`.

- [ ] Write failing tests for zero/multiple `uses_schema` values, a role mapped outside that schema,
  ambiguous role mappings, unsupported evidence, missing exclusion/privacy rules, and a purpose packet
  that silently unions field allow-lists.
- [ ] Map every selected role to a live P6 field for exactly one schema. Record required evidence,
  exclusions, an optional authored/versioned `purpose_profile_ref`, privacy constraints, and
  source-domain provenance. The purpose profile is not a P6 `purpose` fact and not a runtime P9 group
  ID; branch bindings separately pin actual accepted groups and C3 proves the evidence match.
- [ ] Prove one definition can have independently valid bindings in two domains and one domain can
  offer two definitions without copying a definition or widening either schema.
- [ ] Run `pytest tests/template_library/test_applicability.py -q`; commit
  `feat(templates): bind reusable recipes to domain evidence`.

### Task 6: Compile and package the catalogue deterministically

**Files:** create `tools/compile_tree_templates.py`,
`src/tree_design/catalogue_data/manifest.json`, `src/tree_design/catalogue.py`; tests
`tests/template_library/test_compile.py`, `tests/p10/test_p10_catalogue_routing.py`.

- [ ] Write failing tests for canonical ordering, content hashes, duplicate IDs, unresolved references,
  source files outside the release manifest, non-reproducible output, and runtime access to
  `planning/domains/`.
- [ ] Compile only allowed, validated, exact-version records. Emit immutable fragment snapshots,
  resolved definitions, one-schema applicability bindings, source hashes, validation-report hashes,
  and a release identity. C1 must resolve every fragment ID/version from the packaged release.
- [ ] Make `tree_design.catalogue` load the packaged manifest through an injected resource/connection.
  It must not import planning code, scan the repository, or default to an empty/partial catalogue.
- [ ] AST-test all `src/tree_design/` modules against any `planning.*` or prompt import and repository
  scan. Only `tools/compile_tree_templates.py` may read authoring sources.
- [ ] Compile twice and assert byte-identical output; run the P10 router and C1–C8 against the compiled
  release.
- [ ] Commit `feat(templates): compile deterministic P10 catalogue`.

### Task 7: Connect bounded P8 custom proposals

**Files:** tests `tests/integration/test_template_library_p8_p10.py`; prompt content remains in its
separately owned folder.

- [ ] Record fixtures for a built-in definition, cross-domain definition, purpose composition,
  valid custom proposal, schema-valid but semantically rejected proposal, consent hand-off, and
  `ValidationUnavailable` caused by a missing applicability binding.
- [ ] Assert P8 returns cited structured output only; P10 owns C1–C8 and V1–V6; no model result writes
  catalogue files, activates a template, creates a node, or widens a P6 allow-list.
- [ ] Freeze Site E: a custom proposal may reference published fragments by exact ID/version and may
  add template-local semantic dimensions, but it cannot publish or propose a new canonical fragment.
  Repeated local dimensions become fragment candidates only in the later human-reviewed synthesis
  pass.
- [ ] Commit `test(templates): lock P8 proposal and P10 validation boundary`.

### Task 8: Prove the scaffold-first user experience

**Files:** tests `tests/p10/test_p10_catalogue_ux_fixtures.py`; fixtures in
`src/tree_design/fixtures.py`.

- [ ] Test top-level scaffold approval before template selection; branch-by-branch refinement with
  persistent root context; full, partial, and no-split application; uneven depth; shallow-by-choice;
  and a later refinement in a new plan version.
- [ ] Test live counts/examples/unresolved/privacy/diff for each candidate, explicit composition
  conflicts, branch-local edits, semantic undo, and no silent changes in another branch reusing the
  same definition.
- [ ] Run card-sort/tree-test fixtures for the release's top retrieval tasks. A visually tidier tree
  cannot replace task-success evidence.
- [ ] Commit `test(templates): prove progressive reusable scaffolding UX`.

### Task 9: Final conformance and Graphify audit

- [ ] Run all template-library and P10 suites, `python3.12 -m compileall -q src tests`, and
  `git diff --check`.
- [ ] Run `graphify update .` and diagnose duplicates/dangling edges. Verify authored source → compiler
  → packaged catalogue → P10 routing edges and no P10 runtime import of planning/prompts/domains.
- [ ] Re-read the original product design and verify: facts stay separate, top-level design remains
  user-led, templates recommend rather than dictate, purpose packets remain legal, uneven depth is
  preserved, existing folders are not silently rewritten, and no unapproved definition creates a
  destination.
- [ ] Commit `test(templates): audit composable library conformance`.

## Done means

- Shared logic is authored once and referenced by immutable ID/version.
- Many-to-many domain/template reuse exists through separate one-schema applicability bindings.
- Cross-domain purpose compositions preserve each schema boundary and every member.
- Missing or conflicting knowledge fails closed with an actionable report.
- The user can approve a useful shallow scaffold, refine branches selectively, preview consequences,
  and revise later through plan versions.
- P8 proposes, P10 validates, and only the user activates a branch-local result.
- The compiled runtime catalogue is deterministic, provenance-bearing, and independent of research
  and prompt directories.
