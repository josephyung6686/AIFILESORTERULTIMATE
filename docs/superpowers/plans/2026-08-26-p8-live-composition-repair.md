# P8 Live Composition Repair Plan

**Date:** 2026-08-26

**Status:** Required completion work discovered by the post-Task-12 architecture audit. This plan repairs P8 only; it does not author prompts, domain rules, P9 groups, P10 templates, P11 placements, or P13 consent handling.

**Authority:** `planning/00-database-agent-product-design.md` → `planning/parts/P8-llm-harness-validator/SPEC.md` → `planning/30-p8-p9-connection-contract.md` → live unchanged-meaning P1–P7 APIs.

## Release blockers

The existing suite is green, but the live composition path is incomplete:

1. `run_call` sends newline-joined released values rather than the closed-world dossier and discards P7 release addresses plus builder-owned evidence metadata.
2. A caller-supplied `site_validator` can bypass P8's Site A–E validators.
3. citation span matching is not structurally bound to the released/redacted material the model saw.
4. dossier identity uses the random single-use release id instead of the deterministic content address.
5. the frozen public surface, P2 tuple binding, event provenance, walking skeleton, and live determinism proof are incomplete.

## Non-negotiable boundary

- P7 remains the sole materializer and release authority. P8 never substitutes raw P4 text for P7's released/redacted value.
- Pre-release requests remain reference-only. Builder metadata may describe an evidence reference, candidate, conflict, or structural reference; it may not carry document bodies or prompt text.
- P8 owns dispatch and validation. Callers inject required authorities and typed site dependencies, never an acceptance callback.
- P9/P10/P11 continue to own producer data. Missing producer data yields `ValidationUnavailable`; P8 does not synthesize it.
- Site A applies one model claim to one P6 `Proposal` exactly once. Replay validates without appending a second P6 consequence.

## Task R1: Freeze the real public and provenance boundaries

Write failing tests, then:

- export the exact eight names frozen by `planning/30-p8-p9-connection-contract.md`;
- require P2 `version_tuple_ref` to equal the referenced run manifest's exact live seven-field tuple;
- reconcile the stale four-field SPEC paragraph;
- retain `validator_version` and `policy_version` in every opaque P8 result payload, including refusal/failure measurements;
- carry model id, prompt fingerprint, and P7 audit id through verdict events.

Verification: focused P8 architecture/stage-output tests plus `tests/eval`.

## Task R2: Canonical post-release dossier

Write adversarial tests proving the model-visible bytes contain, in canonical form:

- common envelope and exact call site/subject/plan/policy/budget/reduction identities;
- every allowed vocabulary member;
- P7 `Materialised` observation key, address, released/redacted value, zone, context fields, and truncation flag;
- builder-owned reference metadata (`kind`, `location`, `excerpt_span`, reliability, basis);
- conflicts and permitted reference-only site structure/candidates;
- the authored response schema and shaping policy from `PromptDefinition`.

Reject a mismatch between requested/released observation keys and builder evidence metadata. Retain an immutable released-evidence map on the materialized `Dossier`. Compute `dossier_id` from the canonical model-visible dossier sources, never from `release_id`; keep `release_id` separately as the spend capability.

Verification: equivalent released content under different release ids produces the same dossier id and bytes; any content/schema/vocabulary/builder change changes the address.

## Task R3: Built-in site dispatcher

Replace the arbitrary `site_validator` injection with one P8-owned dispatcher and typed site dependency bundles:

- A → exact one-claim adapter, P6 `FactRequest`, `FactValidationDependencies`, four checks, one `apply_verdict` consequence;
- B → `validate_group_response`;
- C → `validate_placement_response` with `PlacementDependencies`;
- D → `validate_residual_response` with `ResidualDependencies`;
- E → `validate_template_response` with `TemplateDependencies`.

Missing or malformed site dependencies return `ValidationUnavailable`. Both live evaluation and replay call this dispatcher. Universal validation cannot be invoked with a caller-authored permissive callback from the public path.

Verification: one adversarial bypass test per site, including an invented Site-C node, invented Site-B member, invalid Site-E schema, and missing C/D/E authorities.

## Task R4: Release-bound citation validation

Universal validation uses the dossier's immutable released-evidence map for exact cited-span/metadata matching. P4 may confirm that the observation key still exists/currently resolves for replay, but its raw value is never the span-matching source. A citation outside the release, a raw-only match, or an address mismatch rejects.

Verification: a redacted released value passes when cited exactly; citing the raw SQLite value fails even when P4 contains it.

## Task R5: One connected consequence path

Replace the manual walking skeleton with real:

`Gate.release → run_call → canonical dossier → transport.issue → built-in dispatcher → P6/P8 consequence → P2 emit`.

For Sites B–E, recorded fixtures stand in only at the named producer seams. `NeedsConsent`, `Denied`, missing policy, budget exhaustion, and call failure retain their existing fail-closed branches.

The determinism probe must load the recorded response through replay, use the same dispatcher, emit/read the P2 row, and compare canonical bytes across independent processes.

## Task R6: Architecture and completion audit

- scan all `src/**/*.py` for model egress, including nested modules and aliases;
- strengthen no-invention checks around all public/configurable P8 callables;
- run focused P8/P6/P7/P2 tests, full `pytest -q`, independent-process determinism, and Graphify multigraph/path checks;
- request independent spec-conformance and code-quality reviews;
- update the P8 completion audit with explicit remaining honest seams (authored prompts/deployment transport, C-5 authorities, later B–E producers, P13 consent hand-off).

P8 may be called complete only when all release blockers above are closed and the remaining seams are accurately external rather than bypasses in P8.
