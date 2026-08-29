---
last_mapped_commit: a5219c2d247f9cb754ea3eb38a6cf025a52fb26c
focus: concerns
mapped_at: 2026-08-29
branch: build/p6-p7-first-packages
---

# Codebase Concerns

**Analysis Date:** 2026-08-29

## Tech Debt

**C-5: P6/P8 own neither `normalize` nor `contradicts`:**
- Issue: Round-4 ruling leaves domain normalization and contradiction oracles as injected callbacks. `facts.llm_seam` publishes the four §3.6 check *inputs* and `apply_verdict`, but explicitly refuses to publish `normalize(` / `contradicts(`. `llm_harness.fact_validation` owns the check *order* and maps to P6's `Verdict`, but omitting either callback yields `ValidationUnavailable` rather than a pass.
- Files: `src/facts/llm_seam.py`, `src/facts/direct.py`, `src/llm_harness/fact_validation.py`, `src/llm_harness/placement_validation.py`, `src/llm_harness/harness.py`, `tests/p8/test_p8_transport.py`
- Impact: Site A (and any site that needs domain contradiction) cannot become a live fact producer without a deployment-supplied oracle. Until that is wired, LLM proposals correctly fail closed as `ValidationUnavailable`, which looks like "the harness works" while facts never activate.
- Fix approach: Decide ownership once (P6 domain catalogues vs caller deployment). Implement real `normalize` / `contradicts` against the field catalogue, inject them at `cli.py` / `production.py` assembly, and keep the "facts must not publish them" guard only until the ruling flips.

**P7 Gate constructor answers open questions at wiring time:**
- Issue: `Gate.__init__` requires `classifier`, `transform`, `unclassified_permits_local`, and `scope_for` with no defaults — each is an unsettled SPEC open question or Deferred row. Optional `measure_tokens` / `template_for` default to `None`, which silently disables dossier-token denial and Protected-Records residual denial.
- Files: `src/privacy/gate.py`, `src/privacy/consent.py`, `src/privacy/policy.py`, `src/privacy/denial.py`, `src/privacy/vocabulary.py`
- Impact: Every production assembly invents product policy. Wrong `unclassified_permits_local` or a no-op `scope_for` widens or collapses egress. Absent `template_for`, protected residual templates never deny.
- Fix approach: Close Open questions 3 and 5 in the design; ship a single deployment profile that pins these callables; make missing `measure_tokens` / `template_for` fail loudly when ceilings / residual templates are configured.

**Sensitivity detector vs deferred catalogue 08:**
- Issue: `privacy.denial` still documents the detector as unwritten (D2). Catalogue `planning/deferred-catalogues/08-sensitivity-detector/` holds authored rules that must not live as module-level data under `src/privacy/`. Runtime classification is supplied by `recognition.detector.Detector` plus injected `handling_for` (`SAFETY_DOMAIN_HANDLING` in `src/cli.py`), not by compiling catalogue 08.
- Files: `src/privacy/denial.py`, `src/recognition/detector.py`, `src/cli.py`, `planning/deferred-catalogues/08-sensitivity-detector/01-detector-rules.json`
- Impact: Production can classify via recognition co-occurrence rules while the hand-authored sensitivity conjunction rules remain unwired. Sensitive material may stay `unreadable_unclassified` (deny) or be under/over-protected relative to catalogue 08.
- Fix approach: Compile catalogue 08 into an injected producer; keep recognition schemas free of handling-class assignment (`planning/domains/_CONTRACT.md` rule 5); assert both paths in integration tests.

**Direct-slot catalogue (F8) absent:**
- Issue: `facts.direct` requires injected `DirectSlots` with no default; the catalogue behind reliable EXIF/title/form slots "does not exist (F8)".
- Files: `src/facts/direct.py`
- Impact: Direct facts only appear where the caller invents slots. Without a shipped catalogue, the strongest deterministic path is underused and more work falls to rules/LLM.
- Fix approach: Author and inject the direct-slot catalogue the same way deferred catalogues 01–07 are injected into extractors.

**Composition surface is a second product:**
- Issue: `src/production.py` and `src/cli.py` assemble P1–P11 authorities (resolvers, readers, detectors, gates, catalogues, partitions, P8 `run_call` bindings). Neither is a numbered part; both are large and policy-bearing.
- Files: `src/production.py` (~675 lines), `src/cli.py` (~1094 lines), `src/orchestrator.py` (~734 lines)
- Impact: Miswiring a single required keyword (`classify`, `contradicts`, `sensitivity_policy`, embedding runtime) fails closed in tests but is easy to get wrong in a new situation or CLI path. Plan-version id minting in `cli.py` already had an IntegrityError regression on second run.
- Fix approach: Keep authority records frozen dataclasses with `__post_init__` type checks (already started in `P1P7Authorities`); shrink `cli.py` by moving situation-specific wiring behind named profiles; never add defaults for privacy/LLM oracles.

**God modules in hot paths:**
- Issue: Several single files concentrate stage logic and are hard to change safely.
- Files: `src/placement/pipeline.py` (~1356), `src/cli.py` (~1094), `src/privacy/fixtures.py` (~1006), `src/tree_design/templates.py` (~932), `src/tree_design/pipeline.py` (~773), `src/llm_harness/placement_validation.py` (~640), `src/llm_harness/validation.py` (~564)
- Impact: Review cost, merge conflict risk, and accidental coupling across P8/P10/P11 seams.
- Fix approach: Split by seam (scoring vs residual vs review in placement; universal vs site validators in P8) without introducing second homes for vocabulary.

**Stale session / README truth:**
- Issue: Root `README.md` still says "No application code in this repo yet." `.planning/.continue-here.md` describes P8 Task 1 mid-ship on older commits while `src/` contains P8–P11 packages and ~4.8k tests.
- Files: `README.md`, `.planning/.continue-here.md`, `.planning/HANDOFF.json`
- Impact: Resume agents and humans re-plan or re-implement shipped work; pathspec constraints in the handoff may be wrong for current branch work.
- Fix approach: Refresh handoff to current HEAD; rewrite README status to match P1–P11 runtime layout.

**P12 / P13 not implemented in `src/`:**
- Issue: `planning/parts/P12-apply-undo/` and `P13-review-approval-surface/` have SPEC/PLAN only. Placement vocabulary and review routing name apply/approve as P12/P13 responsibilities.
- Files: `src/placement/__init__.py`, `src/placement/review.py`, `src/placement/vocabulary.py`, `src/placement/fixtures.py`, `planning/parts/P12-apply-undo/`, `planning/parts/P13-review-approval-surface/`
- Impact: End-to-end product stops at plans and review gestures; filesystem moves and consent-collection UI are not in this tree.
- Fix approach: Implement P12/P13 against placement's published plan outcomes; do not invent apply paths inside P11.

## Known Bugs

**Second tree-design run plan-version collision (mitigated in CLI, pattern risk remains):**
- Symptoms: Historically a second invocation over the same folder minted `version_0` again and died with `IntegrityError` / traceback.
- Files: `src/cli.py` (`design_authorities` counter past existing `plan_versions` / `tree_nodes` rows)
- Trigger: Re-run the shipped command on a DB that already holds a plan version, with a counter that restarts at zero.
- Workaround: Current CLI counts existing rows before minting. Any new entrypoint that mints plan ids must do the same or use P10's version APIs.

**G-P10 xfail shell still present after freeze landed:**
- Symptoms: `tests/integration/test_p11_p10_tree.py` still catches `ModuleNotFoundError` and `pytest.xfail`s as "G-P10 open", even though `tree_design.freeze.frozen_tree` exists.
- Files: `tests/integration/test_p11_p10_tree.py`, `src/tree_design/freeze.py`
- Trigger: Only if the import fails; live path should pass. The dead xfail branch can hide a real import regression as an expected skip.
- Workaround: None needed for green runs. Remove the xfail branch so a missing freeze module fails hard.

**pytest-randomly + spaCy/thinc seed collision:**
- Symptoms: With default pytest-randomly seed reset, thinc's entry point reseeds numpy with an out-of-range value; setup/teardown explode into mass failures.
- Files: `pyproject.toml` (dev extra comments)
- Trigger: `pytest -p randomly` without `--randomly-dont-reset-seed` when thinc is importable in the interpreter.
- Workaround: Documented flag: `python3 -m pytest tests/ -p randomly --randomly-dont-reset-seed`.

## Security Considerations

**Single egress depends on transport_guard + runtime binding:**
- Risk: Model content must only leave through `llm_harness.transport.issue` consuming P7 `Released`. The static guard (`privacy.transport_guard`) intentionally does not walk imported `CallPayload` interiors; it states that limit in-module.
- Files: `src/llm_harness/transport.py`, `src/privacy/transport_guard.py`, `tests/p7/test_p7_real_transport_egress.py`, `tests/integration/test_p8_p7_egress.py`
- Current mitigation: `IS_MODEL_TRANSPORT = True` scan; signature/annotation walk forbidding `str`/`bytes`/`Path`/`Observation`/`TextUnit` on the egress surface; runtime `assemble` / `_require_sources` / `consume_release` / target binding checks.
- Recommendations: Keep `assert_single_egress` on the real transport in CI; never add a second client entrypoint; treat any new `invoke(str)` helper as a privacy incident.

**NeedsConsent must never become a stage outcome:**
- Risk: Coercing `NeedsConsent` into abstain/deny/retry or writing a P2 row would silently authorize or mis-measure privacy waits.
- Files: `src/llm_harness/harness.py`, `src/llm_harness/stage_output.py`, `src/llm_harness/store.py`, `src/llm_harness/__init__.py`
- Current mitigation: `run_call` returns P7's exact `NeedsConsent` unchanged; `stage_output` raises `TypeError("NeedsConsent writes no P2 row")`; store has no consent writer.
- Recommendations: Preserve this in every new composer (`placement.pipeline`, `grouping`, CLI). Grep new OUTCOME enums for `needs_consent`.

**Consent scope is opaque until Open question 3 closes:**
- Risk: Grants are keyed by caller-supplied `scope` strings via injected `scope_for` / `files_in_scope`. A too-broad scope grants model use across the corpus; a too-narrow scope strands revocation.
- Files: `src/privacy/consent.py`, `src/privacy/policy.py`, `src/privacy/gate.py`, `src/privacy/revocation.py`
- Current mitigation: No default scope; policy version is a concurrency token; revoke path is separate from grant.
- Recommendations: Define corpus-area vocabulary before shipping multi-root corpora; property-test grant/revoke round-trips per file.

**Protected containers and dataless items — no override:**
- Risk: Opening a protected container or dataless iCloud item downloads or indexes material the design forbids.
- Files: `src/extractors/safety.py`, `src/scan_agent/exclusion.py`, `src/scan_agent/dataless.py`, `src/recognition/detector.py`
- Current mitigation: `SafetyPolicy` has no force/override field; `admit` is first statement of extractors; detector checks `is_protected_container` before reading observations.
- Recommendations: Keep predicates caller-supplied from P3 only; never re-derive in P5/P7.

**Always-local / redaction transforms are injected:**
- Risk: Identifier classes and redaction transforms are Deferred; a weak `transform` can leak spans into released dossiers.
- Files: `src/privacy/gate.py`, `src/privacy/items.py`, `src/privacy/redaction.py`, `planning/deferred-catalogues/08-sensitivity-detector/03-redaction-transforms.json`
- Current mitigation: Gate requires `transform`; items refuse defaults for sensitive keys.
- Recommendations: Wire catalogue 08 transforms; fuzz Released payloads for raw always-local substrings.

**Eval bundle `metadata_safe` + text units unresolved:**
- Risk: Whether metadata-safe bundles may carry `text_units` is SPEC Open question 5 (local full text vs replay representation).
- Files: `src/eval_harness/bundle.py` (`add_text_unit` raises `NotImplementedError`)
- Current mitigation: Hard refuse rather than guess.
- Recommendations: Close the question before any external bundle export path exists.

## Performance Bottlenecks

**Placement / retrieval / index on large frozen trees:**
- Problem: Destination indexing and retrieval sit on the critical P11 path; scale tests exist but may skip under conditions.
- Files: `src/placement/index.py`, `src/placement/retrieval.py`, `src/placement/pipeline.py`, `tests/integration/test_scale_stress.py`, `tests/p11/test_p11_retrieval_scale.py`
- Cause: Full corpus placement walks subjects against a frozen index; WAL checkpointing and statement counts are tuned carefully.
- Improvement path: Keep scale stress enabled in CI where fixtures allow; profile `build_destination_index` before adding features to `pipeline.py`.

**Scan WAL growth on huge corpora:**
- Problem: A single transaction around a 500k-file scan would balloon the WAL.
- Files: `src/database_agent/db.py`, `src/scan_agent/scan.py`
- Cause: WAL + `synchronous = FULL` retains pages for the open write transaction.
- Improvement path: Keep batch commits (already documented); monitor `scan_usage` DB/WAL/SHM size via `src/database_agent/scan_usage.py`.

**Embedding runtime fail-closed cost:**
- Problem: Incomplete enabled embedding configs raise `ConfigurationRequired` before grouping proceeds.
- Files: `src/grouping/pipeline.py`, `src/grouping/embeddings.py`, `src/grouping/retrieval.py`, `src/tree_design/config.py`
- Cause: Intentional fail-closed; misconfigured deployments spend setup cost then refuse.
- Improvement path: Validate embedding authorities at CLI startup before scan.

## Fragile Areas

**P8 validation boundary (universal vs site vs P6 apply):**
- Files: `src/llm_harness/validation.py`, `src/llm_harness/fact_validation.py`, `src/llm_harness/group_validation.py`, `src/llm_harness/placement_validation.py`, `src/llm_harness/template_validation.py`, `src/llm_harness/sites.py`, `src/facts/llm_seam.py`
- Why fragile: Three layers — parse/ground (`validation.py`), site oracles (injected), P6 `apply_verdict` — must stay aligned. Dual types `P8Verdict` vs `facts.llm_seam.Verdict`. Empty cited spans and schema-invalid claims are adversarial targets (see `tests/p8/test_p8_release_binding.py`).
- Safe modification: Change check order only with Site A–E tests green; never invent `normalize`/`contradicts` inside `facts/`; missing oracle → `ValidationUnavailable`.
- Test coverage: Strong under `tests/p8/` and `tests/integration/test_p8_p6_fact_seam.py`, `test_p8_p7_egress.py`. Gaps wherever deployment oracles are absent.

**P7 release → P8 `run_call` → P11 `p8_seam`:**
- Files: `src/privacy/gate.py`, `src/llm_harness/harness.py`, `src/placement/p8_seam.py`, `src/placement/pipeline.py`
- Why fragile: P11 must not call `gate.release` itself; it supplies gate/client/prompt and reads verdicts. Budgets, evidence snapshots, and sensitivity policy are required before spend.
- Safe modification: Extend `PipelineInputs` only with fail-closed `__post_init__` checks; keep Site C/D validation inside `run_call`.
- Test coverage: `tests/integration/test_p11_p8_seam.py`, `test_p11_pipeline_live.py`, `tests/p11/test_p11_privacy.py`.

**P9 ↔ P8 group seam:**
- Files: `src/grouping/pipeline.py`, `src/llm_harness/group_validation.py`, `tests/integration/test_p9_p8_group_seam.py`
- Why fragile: Budget-deferred P8 results must map to dossier-deferred, not acceptance. Missing P8/config must fail closed.
- Safe modification: Do not treat `deferred` as `pending-review` or shared lifecycle state (`grouping/acceptance.py` tests).
- Test coverage: Good unit + seam tests; embedding pipeline needs a real runtime to be meaningful.

**P10 freeze ↔ P11 legal destinations:**
- Files: `src/tree_design/freeze.py`, `src/placement/index.py`, `tests/integration/test_p11_p10_tree.py`, `tests/integration/test_p10_p11_live_seam.py`
- Why fragile: Protected nodes must be in the frozen tree and out of the legal set (MARKED AND COUNTED, NEVER OPENED). P11 must not stub freeze.
- Safe modification: Always read through `frozen_tree`; never hand-assemble freeze bundles in placement production code.
- Test coverage: Live seam tests; remove residual G-P10 xfail branch.

**Privacy fixture / Gate argument pin (Task 20):**
- Files: `src/privacy/fixtures.py`, `src/privacy/gate.py`
- Why fragile: Large fixture module (~1006 lines) pins keyword order and replay shapes; renames break fixture replay without obvious product failures.
- Safe modification: Change Gate kwargs only with fixture + Task 20 tests.
- Test coverage: Heavy under `tests/p7/`.

**Domains / recognition catalogue process (runtime-affecting only):**
- Files: `src/recognition/rules.py`, `src/recognition/detector.py`, `src/facts/domains.py`, `planning/domains/check.py`, `tests/p10/test_library_*.py`
- Why fragile: Research nodes under `planning/domains/nodes/` can be absent (`pytest.skip`); `check.py` imports live `evidence_shape.vocabulary.SOURCE_TYPES`. Recognition loads compiled manifests into the CLI detector. Domain research that assigns handling classes would invent P7 vocabulary.
- Safe modification: Keep research → compile → `load_rules` pipeline; never import deferred-catalogue JSON into `src/extractors/` or `src/privacy/` as module constants.
- Test coverage: Recognition tests + library tests that skip when research surface absent — skips hide incomplete catalogues.

## Scaling Limits

**SQLite working memory:**
- Current capacity: Local single-writer design with WAL, foreign keys, recursive triggers (`src/database_agent/db.py`).
- Limit: Large scans and long placement runs grow DB/WAL; dossier token ceilings are injected (`model.max_dossier_tokens_per_call`) with no product-default numbers (Deferred).
- Scaling path: Batch scans; dossier budgets via P8 `budgets.py`; do not move to multi-writer without revisiting P1 contracts.

**Frozen tree / placement candidate set:**
- Current capacity: Index built per plan version; retrieval tests measure statement counts.
- Limit: Unbounded residual loops and refresh semantics are still SPEC open questions (noted in `tests/p11/test_p11_pipeline.py`).
- Scaling path: Inject residual partitions and stop rules; refuse unbounded refresh in composers.

**Test suite size:**
- Current capacity: ~229 `src` modules, ~285 test modules, ~4872 `test_*` functions.
- Limit: Full suite + randomly is slow; optional readers (Vision/pdfminer) are platform-gated.
- Scaling path: Keep package-scoped markers; do not drop randomly order checks.

## Dependencies at Risk

**Empty runtime `dependencies` in packaging:**
- Risk: `pyproject.toml` ships `dependencies = []` by design (P5 adds no third-party runtime dep). Readers live in optional `readers` extra (pdfminer, pyobjc Vision/Quartz on Darwin).
- Impact: A bare install cannot OCR or PDF-parse; CLI must inject callables or fail.
- Migration plan: Keep empty core deps; document `pip install '.[dev,readers]'` for local macOS paths; never move gazetteers into package constants.

**Stdlib-only package islands vs deployment oracles:**
- Risk: `llm_harness` and most parts stay stdlib + in-repo imports, but correctness depends on injected model clients, embedding runtimes, and catalogues that are not in the wheel.
- Impact: Green unit tests with fixtures do not prove a deployment can classify, normalize, or embed.
- Migration plan: Production smoke (`tests/integration/test_production_corpus.py`, CLI) must remain the gate for wiring.

## Missing Critical Features

**Filesystem apply / undo (P12):**
- Problem: No `src/` package moves files or implements conditional undo.
- Blocks: Closing the product loop after placement plans (`placement` vocabulary `MOVE_PLAN_ELIGIBLE`, etc.).

**Review / approval / consent collection UI (P13):**
- Problem: Consent recording comments name P13 as collector; no review surface package.
- Blocks: Human answers to `NeedsConsent` and plan approval outside tests/CLI helpers.

**Wired sensitivity + redaction catalogues (08):**
- Problem: Authored JSON exists; privacy modules must not embed it; recognition path is a partial substitute.
- Blocks: Evidence-backed protected classification at catalogue fidelity.

**Domain `normalize` / `contradicts` oracles (C-5):**
- Problem: Required for LLM facts to activate safely.
- Blocks: End-to-end LLM → active fact without `ValidationUnavailable`.

**Direct-slot catalogue (F8):**
- Problem: Missing injected slots for EXIF/title/labeled fields.
- Blocks: Full strength of deterministic fact path.

## Test Coverage Gaps

**Deployment oracle paths:**
- What's not tested: Real `normalize`/`contradicts` implementations; catalogue-08 detector compilation; non-fixture embedding backends.
- Files: `src/llm_harness/fact_validation.py`, `src/recognition/detector.py`, `src/grouping/embeddings.py`
- Risk: Seam tests pass with lambdas (`contradicts=lambda *_a, **_k: False`) that never catch domain contradictions.
- Priority: High

**P12/P13 absence:**
- What's not tested: Actual moves, collision refusal, conditional undo, consent UX.
- Files: planning SPECs only; `src/placement/review.py` routes apply elsewhere
- Risk: Placement plans accepted in tests never meet filesystem reality.
- Priority: High (when P12 starts)

**Optional / skipped surfaces:**
- What's not tested when absent: `planning/domains/nodes` research checks; scale stress under `skipif`; unprivileged filesystem tests; NFC/NFD folding on some FS.
- Files: `tests/p10/test_library_organisational.py`, `tests/integration/test_scale_stress.py`, `tests/p3/test_p3_access.py`, `tests/test_adversarial.py`
- Risk: CI green while research catalogues or OS-specific behaviors drift.
- Priority: Medium

**Dead G-P10 xfail branch:**
- What's not tested: Failure mode when `frozen_tree` import breaks (masked as xfail).
- Files: `tests/integration/test_p11_p10_tree.py`
- Risk: Regressions reported as expected incomplete work.
- Priority: Medium

**Handoff / docs drift:**
- What's not tested: README and `.continue-here.md` accuracy vs tree.
- Files: `README.md`, `.planning/.continue-here.md`
- Risk: Process debt, not runtime — but drives wrong agent behavior.
- Priority: Low (process); fix before next ship wave

---

*Concerns audit: 2026-08-29*
