# P8/P9 Connection Contract

Date: 2026-08-25

Status: planning contract only. It freezes names and ownership; it implements no
runtime behavior. `planning/29-DOMAIN-OWNERSHIP.md` remains the independent domain
research register, so this contract uses the next available number.

## Authority and boundary

Authority order is `planning/00-database-agent-product-design.md`, the part SPECs,
ratified resolutions, then live P1–P7 APIs for exact unchanged-meaning shapes. No
seam below supplies prompt text, domain rules, thresholds, detectors, gazetteers,
redaction reverse maps, or numeric defaults.

P8 owns the only model invocation and the only deterministic validator for sites
A–E. P9 owns deterministic group seeds/neighbourhoods, reference-only Site-B dossier
construction, and mapping an accepted P8 result into append-only membership history.
P9 must not call a model, call `privacy.gate.Gate.release`, validate citations, or
define `P8GroupResult`/another validator vocabulary.

## Frozen P8 public surface

`src/llm_harness/__init__.py` exports exactly these cross-part names:

- `run_call` from `llm_harness.harness`
- `DossierRequest`, `Dossier`, and `P8Verdict` from `llm_harness.records`
- `Refusal`, `CallFailed`, and `ValidationUnavailable` from
  `llm_harness.records`
- `NeedsConsent`, re-exporting the exact class from `privacy.release`

`P8Verdict` is intentionally not `facts.llm_seam.Verdict`. Internal and consumer
imports use those qualified names; P8 exports no ambiguous bare `Verdict` alias.
`DossierRequest` is the reference-only cross-part request P9 may construct;
`Dossier` is P8's post-release materialised record and is never constructed by P9.
`run_call` is the one public evaluation callable for P9. Its Site-B result is
`P8Verdict | Refusal | NeedsConsent | ValidationUnavailable | CallFailed`; P9 does
not wrap that union in a second authority type. The caller of `run_call` owns the
P13 hand-off when the exact `NeedsConsent` object is returned.

## Seam ledger

| Direction | Producer module.symbol | Consumer module.symbol | Record identity | Failure mode | Integration-test owner |
|---|---|---|---|---|---|
| P7→P8 | `privacy.gate.Gate.release` | `llm_harness.harness.run_call` | live `privacy.release.ModelCallRequest` and exact `Released | Denied | NeedsConsent` union | `Denied` becomes gate-only P8 `Refusal`; `NeedsConsent` is returned unchanged; `privacy.release.NoPolicyInForce` propagates; no model call | `tests/integration/test_p8_p7_egress.py` |
| P7→P8 | `privacy.release.Released` + release ledger | `llm_harness.transport.issue` | `release_id` is spend capability; `audit_id` is provenance; exact `ModelTarget` binds destination | forged, mismatched, or spent release raises before egress | `tests/integration/test_p8_p7_egress.py` |
| P6→P8 | `facts.llm_seam.build_request` | `llm_harness.fact_validation.validate_fact_proposal` | `(FactRequest, Proposal)` for one `(file_id, content_hash)` | missing injected normalize/contradicts authority → `ValidationUnavailable`, no call/verdict/fact | `tests/integration/test_p8_p6_fact_seam.py` |
| P8→P6 | `llm_harness.fact_validation.validate_fact_proposal` | `facts.llm_seam.apply_verdict` | distinct `facts.llm_seam.Verdict(passed, failed_check)` mapped from `P8Verdict`; required `proposal_state`, `model_identifier`, `prompt_fingerprint` | failed check or model unknown uses P6 unresolved consequence; no duplicate P8 fact writer | `tests/integration/test_p8_p6_fact_seam.py` |
| P9→P8 | eventual `grouping.p8_seam.build_dossier_request` | `llm_harness.harness.run_call` | reference-only Site-B `DossierRequest`; P8 materialises only after P7 release | P9 stop-rule failure never calls P8; missing P8/config → fail closed; fixture until P9 exists | P9 owns `tests/integration/test_p9_p8_group_seam.py`; P8 owns recorded Site-B fixtures in `tests/p8/test_p8_group_validation.py` |
| P8→P9 | `llm_harness.harness.run_call` | eventual `grouping.p8_seam.apply_p8_verdict` | exact `llm_harness.records.P8Verdict` outcome + reasons + evidence/plan identities | non-accept outcomes create no accepted membership; `NeedsConsent` is passed by P9 caller to P13 unchanged | `tests/integration/test_p9_p8_group_seam.py` |
| P8→P2 | `llm_harness.stage_output.emit_stage_output` | `eval_harness.stage_output.record_stage_output` | existing `run_id`, seven-field `version_tuple_ref`, stage `llm_interpretation`, opaque P8 payload | foreign vocabulary raises; `NeedsConsent` writes no row; missing run/version fails FK/validation | `tests/integration/test_p8_p2_replay.py` |
| P1→P8 | `database_agent.learning.learning_records` | `llm_harness.eligibility.suppressed_by_learning` | exact `(scope, subject_id, proposal_class, basis_key)` over current post-reset user events | absent connection or scope/subject identity → `ValidationUnavailable`; no second learning store | `tests/p8/test_p8_eligibility.py` |
| P1→P8 | `database_agent.events.append_event` | narrow writers in `llm_harness.store`/`transport` | existing five registered P8 event types; dedicated `prompt_fingerprint` column plus audit/model explanation | unknown event or missing required provenance raises; no runtime registration | `tests/p8/test_p8_provenance.py` |
| P4→P8 | P4 observation readers keyed by `observation_key` | `llm_harness.validation.validate_response` | cited observation key + released/redacted span, never fuzzy text identity | absent/out-of-dossier/unmatched citation rejects; raw sensitive text is not substituted | `tests/p8/test_p8_validation.py` |
| P6→P9 | `facts.read_surface.proposal_eligible` and active fact reads | eventual P9 seed builder | live P6 eligibility (includes `llm_supported`, excludes `possible`) | ineligible fact cannot seed; no copied reliability table | P9 plan Task 4 tests |
| P1/P2→P9 | P1 append-only vector/budget/history APIs and P2 `grouping` stage writer | eventual P9 store/measurement adapters | plan-versioned append-only group/membership identity and P2 run identity | overwrite fallback, foreign outcome, or missing ceiling fails closed | P9 plan-owned tests |

## Shared invariants

1. P8 `run_call` is the only path to `ModelClient.invoke`; P9 has no transport.
2. A `ModelCallRequest` contains references only. Materialised evidence enters P8
   only through a live `Released` capability.
3. `NeedsConsent` is not a P8/P9 outcome and receives no P8/P9 stage row.
4. D14: the grant audit row has `AuditRecord.release_id is None`; link events with
   `Released.audit_id` and spend the ledger with `Released.release_id`.
5. P2 uses live `VERSION_TUPLE_FIELDS` (seven fields). `validator_version` and
   `policy_version` live in P8's opaque payload/verdict/report, not that tuple.
6. C/D verdicts bind plan version and evidence snapshot. A changed plan creates a
   newly validated verdict plus supersession; verdicts never migrate in place.
7. Embeddings/proximity may propose P9 neighbours and never establish membership.
8. Fixtures are content-free contract witnesses, not alternate authorities. The
   eventual producer swap occurs only at the named dossier-builder seam.

## Deliberately open decisions

- P8 Q8 retry policy remains open; P8 performs one attempt and no automatic retry.
- P8 Q3's two-condition support rule is ratified for Site C only. Site D requires
  an injected/ratified rule and otherwise returns `ValidationUnavailable`.
- C-5 normalize/contradiction authorities remain injected; P8 and P6 do not invent
  them.
- P9 public implementation modules do not exist yet. The symbols above prefixed
  `eventual` are names P9 must either adopt in its plan or explicitly revise in this
  shared contract before implementation.
