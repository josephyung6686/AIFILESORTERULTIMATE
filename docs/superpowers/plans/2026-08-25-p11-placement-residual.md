# P11 Placement and Residual Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Decide which frozen P10 destination node—or no node—each accepted file/group belongs to, while preserving evidence, privacy, reversibility, and the original product rule that P11 emits decisions but never moves files.

**Architecture:** P11 consumes a frozen P10 tree/profile projection, accepted P9 groups, P6/P4 evidence, P7 handling metadata, and injected P8/P13 authorities. It builds a bounded destination index, performs deterministic matching first, calls P8 only for bounded ambiguity, and runs residual review only after normal placement. Both paths emit one append-only `PlacementDecision` shape; P12 alone resolves paths and mutates the filesystem.

**Tech Stack:** Python 3.12, stdlib dataclasses/sqlite3/json, P1 events/learning, P2 stage output, P4 observation keys, P6 read surfaces, P7 privacy records, P8 frozen `run_call` union, P9 groups, P10 frozen tree/profiles, pytest, Graphify.

---

## Authority and non-negotiable boundaries

Start with `planning/00-database-agent-product-design.md`, then `planning/04-resolutions.md`, `planning/parts/P11-placement-residual/SPEC.md`, P10/P9 plans, P8/P9 connection contract, and `planning/parts/P12-apply-undo/SPEC.md`. The original design remains the north star: organize conservatively, explain every recommendation, preserve existing structure, and leave the user in control.

- P10 owns the frozen tree, node roles, destination profiles, residual definitions, shared-material policy, and legality metadata.
- P11 owns retrieval index, placement/residual decisions, deterministic destination checks, residual workflow, and P2 placement stages.
- P8 owns privacy release, model invocation, materialized dossiers, citation/schema validation, and the frozen direct result union.
- P9 owns accepted groups and memberships; P11 never re-groups.
- P12 owns path composition, collision policy, filesystem mutation, and undo.
- P13 presents/collects review actions; P11 authors the resulting decision records.

Dependency gates: **G-P10** (frozen plan/profile), **G-P8** (live `run_call`), **G-P13** (review-action input), **G-KNOWLEDGE** (destination checks/thresholds injected), and **G-P12** (node-only output). Before a gate ships, use fixtures but do not replace the missing authority with a source stub.

## File structure

```text
src/placement/vocabulary.py       outcomes, evidence/review/abstention vocabularies
src/placement/records.py           PlacementDecision, GroupPlan, ResidualSet, SetDecision
src/placement/schema.py            append-only decision/index/residual tables
src/placement/store.py             current/history/supersession reads and writes
src/placement/index.py             frozen-profile retrieval index
src/placement/retrieval.py         bounded candidates, conflicts, shallow fallback
src/placement/scoring.py           injected support/margin calculation and two-condition record
src/placement/p8_seam.py           reference-only request and direct-union result mapping
src/placement/groups.py            coherent group plans and outlier handling
src/placement/residual.py          second-stage sets, set gating, eight actions, return loop
src/placement/privacy.py           carried P7 policy and review eligibility
src/placement/learning.py          scoped negative-example suppression
src/placement/stage_output.py      P11→P2 candidate retrieval/placement scoring mapping
src/placement/pipeline.py           normal placement then residual orchestration
src/placement/fixtures.py           P10/P9/P8/P13 contract fixtures
tests/p11/test_p11_*.py
tests/integration/test_p11_p10_tree.py
tests/integration/test_p11_p8_seam.py
tests/integration/test_p11_p12_node_boundary.py
tests/integration/test_p11_p2_replay.py
```

### Task 1: Canonical decision records and append-only schema

- [ ] Write failing round-trip tests for one `PlacementDecision` shape covering normal and residual origins, all eight residual actions, node-only destinations, evidence/conflicts/alternatives, privacy/review, two-condition data, `returned_from`, and `supersedes`/`superseded_by`/`supersede_reason`.
- [ ] Implement strict validation: plan version required; destination only for `place`; unknown/non-placeable node rejected; no path/deletion/expiry fields; user-attached never validated/auto-eligible; observation references use `observation_key`.
- [ ] Add immutable tables/triggers for decisions, group plans, residual sets/set decisions, and index entries. Test historical rows remain readable after supersession.
- [ ] Commit `feat(p11): add append-only placement decision contract`.

### Task 2: Frozen P10 adapter and legal destination index

- [ ] Test G-P10: no frozen plan, stale version, missing profile, or missing shared-material policy fails closed.
- [ ] Implement `build_destination_index(frozen_plan)` over every profile whose node has `accepts_placement=True`; carry `node_id`, role, disposition, expected values, parent/child context, labels, accepted groups, anchor excerpts, exclusions, privacy restrictions, and user edits verbatim.
- [ ] Reject ignored/protected-without-policy nodes as automatic destinations; do not rebuild profiles or create nodes in P11.
- [ ] Commit `feat(p11): index only legal frozen destinations`.

### Task 3: Bounded retrieval and conflict suppression

- [ ] Write fixtures for direct/validated facts, accepted groups, graph anchors, curated-folder context, compatible profiles, semantic-only neighbors, generic hubs, and institution/term conflicts.
- [ ] Implement node-local retrieval with injected ceilings and stable `(content_hash, file_id, node_id)` tie-breaks. Record retrieved and suppressed candidates in `conflicts_considered`.
- [ ] Enforce shallow fallback only to a P10-published node; never fill unsupported dimensions or invent `Math Stuff`/`Gate B12` destinations. Embeddings remain retrieval-only.
- [ ] Commit `feat(p11): retrieve bounded evidence-backed candidates`.

### Task 4: Deterministic exact-match and two-condition scoring

- [ ] Define injected `SupportPolicy` with explicit support scale, minimum support threshold, margin threshold, and version. Missing values are `ConfigurationRequired`; no numeric defaults.
- [ ] Implement a unique direct/validated match with zero model calls. Record `confidence_class="exact fact match"`, alternatives, thresholds, support, and margin.
- [ ] Test exactly one legal candidate: support pass yields `margin_over_next=None`, `meets_margin=true_vacuous`; support fail abstains despite no alternative.
- [ ] Ensure weak, semantic-only, generic-hub, conflict, low-margin, and user-attached cases cannot be `auto_eligible`.
- [ ] Commit `feat(p11): score deterministic placement conservatively`.

### Task 5: P8 placement seam

- [ ] Build only reference-only `DossierRequest` from the target file/group, legal candidate profiles, evidence keys, conflicts, and bounded deterministic scores. P11 must not materialize `Dossier`, call `Gate.release`, or import a model client.
- [ ] Call only frozen `llm_harness.run_call`; consume `P8Verdict | Refusal | NeedsConsent | ValidationUnavailable | CallFailed` without a P11 wrapper.
- [ ] Map accepted direct/context results, weak/reject/abstain, refusal, unavailable, call failure, consent, and budget deferral into the shared decision record. `NeedsConsent` passes unchanged to the review boundary and writes no P11 decision/stage row.
- [ ] Commit `feat(p11): consume frozen P8 placement verdicts`.

### Task 6: Group-level placement and multi-home policy

- [ ] Confirm a shared parent before member placement; emit one `group_plan_id` and per-member decisions. Keep direct-anchor, context-supported, and user-attached bases separate.
- [ ] Exclude conflicting outliers with evidence and legal alternatives; never silently force them into the group.
- [ ] Apply the frozen shared-material policy. If no shared branch or ratified ask/abstain selector exists, fail closed; never choose one institution arbitrarily and never invent alias filesystem behavior.
- [ ] Commit `feat(p11): place groups coherently and conservatively`.

### Task 7: Privacy and review eligibility

- [ ] Carry P7 handling class, operation mode, consent audit reference, and model eligibility without reclassification. Protected content is absent from general summaries unless explicitly permitted.
- [ ] Derive `review_policy`: direct exact low-risk may be auto-eligible; context-supported, user-attached, weak, semantic-only, conflict, protected, and consent-pending cases require review or block.
- [ ] Test layered explanation payloads: concise reason/next action plus expandable evidence, conflicts, uncertainty, and reversibility metadata. No raw protected content leaks.
- [ ] Commit `feat(p11): propagate privacy and substantive review policy`.

### Task 8: Residual sets and set-level gating

- [ ] Ensure the normal placement pass completes before residual surfacing. Partition residual candidates into explainable review sets with representative examples, type/age/evidence/sensitivity/weak-neighbor metadata.
- [ ] Require a P13 set decision before any per-file residual model call. `leave_in_place` produces zero model calls; budget deferral is distinct from evidential abstention.
- [ ] Keep residual definitions and enabled nodes in P10; P11 may name only frozen residual node IDs. Custom branch creation routes to P10 and a new plan version.
- [ ] Commit `feat(p11): gate residual work by review set`.

### Task 9: Eight residual actions and return loop

- [ ] Map exactly eight actions into the shared record: return to confirmed group; return to accepted graph/purpose packet; choose approved residual destination; choose approved broad parent; Review Later; leave in place; mark protected/unsupported; abstain.
- [ ] Implement the Columbia-style `return_to_placement` link with `returned_from`; validate the subsequent node against the same frozen tree. A generic screenshot must not create a travel/flight destination.
- [ ] Until the SPEC ratifies a cycle policy, require injected `max_return_cycles`; recommended default for fixtures is one return per file/run, with a second attempt becoming Review Later plus a recorded cycle reason. Do not hide this as a product default.
- [ ] Commit `feat(p11): close residual actions and placement return loop`.

### Task 10: Scoped learning and plan-version projection

- [ ] Query P1 `learning_records` before proposing each destination/residual node using exact proposal class, basis key, scope, and subject. Rejected matches suppress only their declared scope.
- [ ] Store user accept/edit/reject/defer/leave/private/bulk actions with evidence keys and correction scope; expose reset/inspect reads without global training.
- [ ] On a new P10 plan version, re-project decisions. Removed nodes require renewed review; renamed/relocated nodes never silently remap prior decisions.
- [ ] Commit `feat(p11): preserve scoped corrections and version safety`.

### Task 11: P2 stage output and budget degradation

- [ ] Emit only `candidate_node_retrieval` and `placement_scoring` with live seven-field version tuple, exact inputs, plan version, thresholds, and provenance.
- [ ] Map decision outcomes to P2 `produced`, `abstained`, `deferred`, `error`, or `not_implemented`; budget exhaustion is always `deferred + ceiling_reached` with `deferred_stage`.
- [ ] Test model/embedding-disabled runs, replay determinism, no silent truncation of decisive evidence, and no lower-quality fallback after budget exhaustion.
- [ ] Commit `feat(p11): emit replayable placement stages`.

### Task 12: Fixtures, integration, and mission guards

- [ ] Publish fixtures for ignored/unknown nodes, exact direct match, semantic-only/generic hub, conflict suppression, shallow fallback, one-node margin, group outlier, multi-home, user-attached unreadable file, residual set gating, all eight actions, return loop, protected/consent, stale plan, negative learning, and P2 replay.
- [ ] Add P10→P11→P12 node/path seam tests and P11→P8 direct-union tests. Before P8/P10/P13 ship, dependency tests must fail explicitly rather than use source stubs.
- [ ] AST/schema guard against tree edits, path strings, filesystem calls, P9 regrouping, P8 validators/transport, P10 profile construction, prompts/domains, deletion/expiry, and hidden numeric defaults.
- [ ] Assert north-star UX: every decision shows evidence/reason/uncertainty/next action/reversibility; users can correct or defer; protected material remains private; abstention is understandable and successful.
- [ ] Commit `test(p11): lock placement and residual boundaries`.

### Task 13: Final verification

- [ ] Run `python3.12 -m compileall -q src tests`, focused P11 plus P1–P10 integration suites, and the full suite after dependency gates.
- [ ] Run Graphify update/diagnose; verify P10→P11 and P11→P2/P12 edges, with P11→P8 visible only after the live P8 seam exists.
- [ ] Re-read the original product design and confirm P11 never moves files, invents destinations, silently reclassifies, destroys evidence, or converts uncertainty into a confident action.

## Explicitly deferred

Support-score scale, thresholds, confidence/abstention vocabularies, ask-versus-abstain selector, alias filesystem semantics, residual-set taxonomy, cycle limit, residual set reversal semantics, and shared-policy storage remain injected or require ratification. They must not be invented to make tests pass.

## Coverage

| Requirement | Tasks |
|---|---|
| Closed frozen-node placement and no path invention | 1, 2, 3, 13 |
| Direct matching, conflicts, shallow fallback, two-condition rule | 3, 4 |
| P8 privacy/model boundary and verdict mapping | 5, 7 |
| Group plans and multi-home safety | 6 |
| Residual ordering, eight actions, return loop | 8, 9 |
| Learning, reversibility, plan versions | 10 |
| P2 replay and budget truthfulness | 11 |
| North-star explainable review UX and original design fidelity | 7, 12, 13 |
