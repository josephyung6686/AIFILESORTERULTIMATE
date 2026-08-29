# P8/P9 Planning Design

## Goal

Produce implementation-ready, independently executable plans for P8 (LLM harness and
validator) and P9 (grouping), plus one shared connection contract that prevents the
two plans from assigning the same seam to neither part or to both parts.

## Authority

The original product design is authoritative. The P8/P9 specifications refine it;
ratified decisions refine the specifications; live P1–P7 code determines the exact
surface names that plans must consume. A task may record a divergence, but it may not
silently choose the plan, old prose, or a convenient stub over a higher authority.

## Deliverables

1. `planning/30-p8-p9-connection-contract.md` (`29-` is already the domain-ownership register)
2. `planning/parts/P8-llm-harness-validator/PLAN.md`
3. `planning/parts/P9-grouping/PLAN.md`

Each plan uses the established P1–P7 format: exact files, checkbox steps, a failing
test before implementation, exact verification commands and expected outcomes,
explicit negative tests, fixtures for unbuilt neighbours, and small tasks suitable
for reviewed execution.

## Architecture

P8 and P9 remain separate parts. P8 owns bounded model calls, P7-gated release,
proposal/validator records, and P2 factual-validation/model-stage attribution. P9 owns
group evidence, seed/neighbourhood construction, membership proposals and decisions,
and its P2 grouping-stage attribution. The shared contract owns no runtime behavior;
it names producer, consumer, record identity, failure mode, and integration test for
every P7→P8, P6→P8, P8→P9, P6→P9, P1/P2→P8/P9, and P9→later-part seam.
The frozen P8 public surface is `llm_harness.run_call`,
`llm_harness.DossierRequest`, `llm_harness.Dossier`,
`llm_harness.P8Verdict`, `llm_harness.Refusal`, `llm_harness.CallFailed`,
`llm_harness.ValidationUnavailable`, and the exact P7 `NeedsConsent` re-export.
`P8Verdict` is deliberately distinct from `facts.llm_seam.Verdict`; P9 consumes
P8's result and reason vocabulary and owns no validator, model call, or parallel
`P8GroupResult` type.

`DossierRequest` is the reference-only cross-part shape P9 constructs. `Dossier`
is the post-release materialized shape P8 alone constructs; P9 never imports or
instantiates it. P9 handles the exact `run_call` union, including `CallFailed`,
without wrapping it in another authority type.

No plan invents detection rules, thresholds, prompt text, gazetteer contents, numeric
ceilings, or unratified policy defaults. Such inputs remain injected and are tested
for fail-closed behavior when absent.

## Data flow

The plan-level reference flow is:

```text
P1 identity/history + P4 evidence + P6 facts
                  ↓
P9 deterministic seeds + bounded graph neighbourhood → reference-only dossier
                  ↓ DossierRequest
P8 run_call → P7 Gate.release(ModelCallRequest) → Released only
                  ↓
P8 bounded model proposal → deterministic citation/schema/conflict validation
                  ↓ exact P8Verdict returned to P9 for membership disposition
P9 validated membership decision
                  ↓
P2 stage outputs/replay records + append-only P1 provenance
```

Every arrow must name the concrete live producer and consumer. A fixture may mediate
an unbuilt back-edge, but the plan must also name the eventual swap site and prevent a
second authority from growing around the fixture.

P9 never calls `Gate.release`, a model client, or a validator. It owns deterministic
reference selection and adopts the frozen seam names
`grouping.p8_seam.build_dossier_request` and `grouping.p8_seam.apply_p8_verdict`.
P8 owns the M9 token-reduction ladder and `run_call` is the sole evaluation callable.
P9 maps SR5 only after P8 returns that the group cannot be explained with valid
citations; SR1–SR4 and SR6 remain P9's pre-dossier checks.

P9 automatic anchors are limited to P6 `direct` and `validated` evidence.
`proposal_eligible` remains the honest live read surface and therefore still includes
`llm_supported`; P9 may retrieve that evidence but may not anchor with it. Possible
family facts and bounded sessions are retrieval-only. `user_confirmed` enters an
automatic group only through P9's explicit user-seed input, not by silently widening
the evidence bar.

Structural G4 ceilings are read through P1 `get_ceiling` using the four registered
keys. Missing values fail closed. Hub frequency and minimum-independent-anchor count
remain required injected OQ1 values with no shipped defaults.

## Error and safety model

- P7 denial/consent is not P8 abstention and is never coerced into a model verdict.
- Invalid citations, invented fields, invented groups, and contradictions fail at the
  validator boundary and produce no active conclusion.
- Missing manually-authored configuration fails closed or remains explicitly
  `not_implemented`; it never selects a permissive default.
- Budget exhaustion records deferred work at the owning stage and never lowers
  validation quality.
- Append-only records supersede; user-confirmed conclusions cannot be silently
  reversed by weaker system output.
- P9 graph expansion is bounded and cannot turn weak proximity into membership.

## Testing design

Each part gets schema/vocabulary tests, conformance tests, no-invention tests,
provenance/history tests, budget tests, replay/stage-output tests, adversarial tests,
and a walking-skeleton step. The shared contract adds caller-level seam tests and AST
guards against duplicate owners or bypass paths.

P8's skeleton proves the only model path goes through P7, citations resolve to P4,
the proposal is legal under P6's active schema, deterministic validation runs before
activation, and P2 can replay the stage without the live filesystem or model.

P9's skeleton proves a P6 fact can seed a bounded group, weak edges alone cannot,
membership carries evidence and history, the group output is replayable, and no
destination/tree/placement concept leaks backward into grouping.

## Review process

The two research tracks are independent and read-only. The primary agent writes the
shared contract and plans, cross-checks task signatures/types across all three files,
scans for placeholders and silently answered open questions, then uses Graphify and
live-source inspection to confirm every named connector exists or is explicitly
fixture-mediated.

## Scope boundary

This pass writes plans only. It does not implement P8 or P9, modify live source, edit
the concurrent domain/catalogue lane, or assemble the P1–P7 runtime blockers recorded
in `planning/28-p1-p7-design-conformance-audit.md`.
