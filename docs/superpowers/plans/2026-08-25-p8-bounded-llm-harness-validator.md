# P8 Bounded LLM Harness and Validator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the single P7-gated model egress and deterministic, replayable validator shared by fact, grouping, placement, residual, and template call sites, without inventing prompts, domain rules, thresholds, or unbuilt neighbour behavior.

**Architecture:** `llm_harness` owns immutable dossier/response/verdict records, one release-consuming transport, deterministic validation, append-only provenance, and the P2 `llm_interpretation` measurement. Call-site builders remain owned by P6/P9/P10/P11; P8 accepts their closed-world data through typed inputs and fixtures. Missing authored policy is a required injection or an explicit unavailable result—never a permissive default.

**Tech Stack:** Python 3.12, stdlib (`dataclasses`, `hashlib`, `json`, `sqlite3`, `typing`), existing P1 SQLite/event APIs, P2 stage-output API, P4 observation keys, P6 fact seam, and P7 `Gate.release`/single-use release ledger.

---

## Authority and scope

Read in this order before executing any task:

1. `planning/00-database-agent-product-design.md` — original mission; wins on conflict.
2. `planning/02-segmentation-map.md` — P8 is the only model caller; P7 precedes it.
3. `planning/parts/P8-llm-harness-validator/SPEC.md` — detailed P8 contract.
4. `planning/04-resolutions.md`, `planning/05-minor-resolutions.md`, and `planning/parts/_ASSEMBLY-RULINGS.md` — ratified refinements.
5. `docs/superpowers/specs/2026-08-25-p8-p9-planning-design.md` — plan boundary and fail-closed posture.
6. Live P1–P7 APIs — code wins over stale planned names where the design meaning is unchanged.
7. `planning/30-p8-p9-connection-contract.md` — frozen cross-part names and seam ownership.

This plan creates or modifies only `src/llm_harness/`, `tests/p8/`, and the named narrow integration tests. Tests call P8's `create_llm_schema` explicitly; this plan does not edit `src/production.py`, `src/orchestrator.py`, or P1 event registration. It also does **not** edit `planning/domains/`, deferred catalogues, prompts, P6, P7, or P9–P13.

### Implemented prerequisites

- P1 provides SQLite, append-only `events`, the five P8 event-type registrations, canonical provenance fields, and supersede helpers.
- P2 provides `record_stage_output(...)`, the `llm_interpretation` stage id, replay run manifests, and opaque payload storage.
- P4 provides stable `observation_key` citation identity, observations, text units, and current/superseded evidence rows.
- P6 provides `FactRequest`, `Proposal`, `Verdict`, `build_request`, `apply_verdict`, the active allowlist, citable observations, stronger-fact rows, normalizer mappings as injected data, and the reliability ordering.
- P7 provides `ModelCallRequest`, `Released | Denied | NeedsConsent`, `Gate.release(...)`, materialised released items, redaction manifests, and `consume_release(...)`.

### Missing prerequisites and dependency gates

- P6 deliberately publishes neither `normalize(field, raw_value)` nor `contradicts(claim, existing_fact)` (`facts.llm_seam`, unresolved C-5). P8 must not import imaginary functions. Site A remains disabled unless the caller supplies both exact callbacks through `FactValidationDependencies`; omission returns `ValidationUnavailable`, writes no verdict/fact, and makes no model call.
- P9, P10, and P11 producers do not exist. Sites B–E are implemented against P8-owned contract fixtures. The eventual producer swaps occur at dossier construction only; validators and stored records do not change.
- Prompt text, sensitivity detector rules, redaction transforms/reverse mapping, domain extensions, gazetteers, residual libraries, template libraries, support thresholds, margins, model clients, and numeric budgets are incomplete or deployment-authored. Every such value is injected with no default. An absent input fails closed.
- `NeedsConsent` is not a verdict, refusal, abstention, reason code, event, or P2 stage output. It is returned unchanged to the caller for eventual P13 presentation.
- Public P8 imports are frozen as `run_call`, `DossierRequest`, `Dossier`, `P8Verdict`, gate-only `Refusal`, `CallFailed`, `ValidationUnavailable`, and P7's exact `NeedsConsent`. `P8Verdict` never aliases or shadows `facts.llm_seam.Verdict`. P9 constructs only `DossierRequest`; P8 alone constructs materialised `Dossier`; P9 owns no validator or model call.

## File map

- Create `src/llm_harness/__init__.py` — intentionally small public surface.
- Create `src/llm_harness/vocabulary.py` — one home for sites, outcomes, reason codes, dispositions, reduction rungs, and eligibility reasons.
- Create `src/llm_harness/records.py` — frozen prompt, call payload, dossier, claim, citation, verdict, report, gate-only refusal, pre-call abstention, and unavailable types.
- Create `src/llm_harness/fingerprint.py` — deterministic prompt fingerprint and dossier content address.
- Create `src/llm_harness/schema.py` — append-only P8 tables and schema bootstrap.
- Create `src/llm_harness/store.py` — insert/read/supersede functions; no validation policy.
- Create `src/llm_harness/eligibility.py` — closed eligibility check and pre-call suppression seam.
- Create `src/llm_harness/budgets.py` — scan-scoped call/cost reservations and the fixed reduction ladder.
- Create `src/llm_harness/transport.py` — the only code that invokes a model client; accepts `Released` only.
- Create `src/llm_harness/validation.py` — universal deterministic checks and site dispatcher.
- Create `src/llm_harness/fact_validation.py` — Site A checks using required injected P6-domain callbacks.
- Create `src/llm_harness/group_validation.py` — Site B checks over fixture/P9 payloads.
- Create `src/llm_harness/placement_validation.py` — Sites C/D checks using required injected tree/policy callbacks.
- Create `src/llm_harness/template_validation.py` — Site E structural/citation checks using an injected strict schema validator.
- Create `src/llm_harness/harness.py` — gate → branch handling → transport → validate → persist → measure orchestration.
- Create `src/llm_harness/stage_output.py` — sole P8-to-P2 outcome mapping.
- Create `src/llm_harness/fixtures.py` — recorded, content-free neighbour fixtures.
- Create `tests/p8/` modules matching the files above.
- Create `tests/integration/test_p8_p7_egress.py` and `tests/integration/test_p8_p2_replay.py`.

### Build-order dependency check

The numbered order is executable as written: Task 1 creates all shared records/vocabularies; Task 2 adds payload construction/fingerprinting over Task 1; Task 3 adds core storage over Tasks 1–2 only; Task 4 adds its own budget schema after core schema exists; Task 5 adds transport over Tasks 1–4 and completes the one deferred event-matrix row; Task 6 adds universal validation over stored records; Tasks 7–8 add site validators over Task 6; Task 9 is the first composition of eligibility, budgets, gate, transport, and validation; Task 10 maps Task 9 results into already-live P2; Task 11 guards the complete module graph; Task 12 alone runs the full walking skeleton and cross-process probe. No task's RED test imports a file or API first created by a later task.

## Task 1: Freeze vocabularies and immutable contracts

**Files:**
- Create: `src/llm_harness/__init__.py`
- Create: `src/llm_harness/vocabulary.py`
- Create: `src/llm_harness/records.py`
- Test: `tests/p8/test_p8_records.py`
- Test: `tests/p8/test_p8_vocabulary.py`

- [ ] **Step 1: Write failing contract tests**

Assert exact named constants and tuple membership for `CALL_SITES`, `OUTCOMES`, `REDUCTION_RUNGS` (including `none` for an unreduced call), universal reason codes, each site's additional codes, every closed eligibility reason, and the exact residual actions `RETURN_CONFIRMED_GROUP`, `RETURN_ACCEPTED_PACKET`, `CHOOSE_RESIDUAL_DESTINATION`, `CHOOSE_BROAD_PARENT`, `MARK_REVIEW_LATER`, `LEAVE_IN_CURRENT_LOCATION`, `MARK_PROTECTED_OR_UNSUPPORTED`, and `ABSTAIN`. Define and construct frozen `DossierRequest`, `PromptDefinition`, `CallPayload`, `Citation`, `EvidenceItem`, `Dossier`, `Claim`, `P8Verdict`, `GroundingReport`, gate-only `Refusal`, `PreCallAbstention`, `CallFailed`, `CallResult`, and `ValidationUnavailable`; no later task may introduce one of these names with a different shape. Include negative cases: citation and `unknown` together, neither citation nor `unknown`, plan version absent at C/D/E, unknown vocabulary member, `accept_context_supported` without `requires_review`, and `weak` with `may_propose=True`. Assert `llm_harness.__init__` exports exactly `run_call`, `DossierRequest`, `Dossier`, `P8Verdict`, gate-only `Refusal`, `CallFailed`, `ValidationUnavailable`, and the exact re-exported `privacy.release.NeedsConsent`; it exports no ambiguous `Verdict`. Assert that `P8Verdict is not facts.llm_seam.Verdict`, that P9 constructs only the reference-only `DossierRequest`, and that only P8 constructs the post-release materialised `Dossier`.

`CallResult`, retained only as an internal execution accumulator, is not exported,
returned by `run_call`, or accepted by a cross-part consumer. Internal
`PreCallAbstention` is converted before return into a no-claim `P8Verdict` carrying
its exact abstained/deferred outcome and reason. Gate `Denied` alone becomes the
gate-only public `Refusal`.

The vocabulary module spells the closed values once:

```python
FACT_ELIGIBILITY = (
    "remains_ambiguous", "multiple_plausible_domains", "language_requires_interpretation",
)
GROUP_ELIGIBILITY = (
    "coherence_judgement", "membership_judgement", "outlier_judgement", "label_judgement",
)
PLACEMENT_ELIGIBILITY = (
    "several_legal_nodes_plausible", "context_member_missing_branch_fact",
    "place_group_together", "custom_template_semantic_interpretation",
    "vague_ocr_or_filename", "direct_facts_conflict",
)
RESIDUAL_ELIGIBILITY = ("user_opted_residual_set_into_ai_review",)
TEMPLATE_ELIGIBILITY = ("accepted_group_fits_no_existing_template",)

RESIDUAL_ACTIONS = (
    "return_to_confirmed_domain_group",
    "return_to_accepted_graph_or_purpose_packet",
    "choose_approved_residual_destination",
    "choose_approved_broad_parent_branch",
    "mark_review_later",
    "leave_in_current_location",
    "mark_protected_or_unsupported",
    "abstain",
)

REDUCTION_RUNGS = (
    "none", "summarized_facts", "preserved_anchors", "split", "deferred",
)
```

Each tuple member also has the named constant listed above; downstream code imports constants, never tuple indices or bare strings.

```python
def test_context_acceptance_always_requires_review():
    with pytest.raises(MalformedVerdict):
        P8Verdict(outcome=ACCEPT_CONTEXT_SUPPORTED, requires_review=False, **VERDICT_BASE)

def test_consent_is_absent_from_p8_vocabularies():
    published = set(OUTCOMES) | set(ALL_REASON_CODES)
    assert "needs_consent" not in published
    assert "consent" not in published
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `pytest -q tests/p8/test_p8_records.py tests/p8/test_p8_vocabulary.py`

Expected: FAIL during collection because `llm_harness` does not exist.

- [ ] **Step 3: Implement the minimal contracts**

Use named constants, never tuple indices or repeated literals. Keep `Dossier` closed-world and content-bearing only after P7 release:

```python
@dataclass(frozen=True, slots=True)
class Dossier:
    dossier_id: str
    call_site: str
    subject_ref: str
    eligibility_reason: str
    plan_version: str | None
    policy_version: str
    allowed_vocabulary: tuple[str, ...]
    evidence_items: tuple[EvidenceItem, ...]
    conflicts: tuple[Conflict, ...]
    max_dossier_tokens: int
    reduction_rung: str
    release_id: str
```

`DossierRequest` is immutable and reference-only: it contains call site, subject identity, eligibility reason, evidence references, intended `ModelCallRequest` fields, plan/evidence-snapshot identities, budget context, and no materialised content. `PromptDefinition` is immutable and contains `template_id`, exact `template_bytes`, exact canonical response-schema bytes, `call_site`, `call_site_version`, and exact canonical shaping-policy bytes. `CallPayload` is immutable and contains the source `PromptDefinition`, canonical model-visible dossier bytes, exact final model-visible bytes, the live `privacy.release.ModelTarget`, `prompt_fingerprint`, `policy_version`, and `release_id`. The first three fields are the immutable sources from which transport recomputes the fingerprint and final payload; `model_target`, fingerprint, policy version, and release id are provenance/authorization fields and are explicitly **not** included in the model-visible byte string. A sole `build_call_payload(...)` factory proves `model_visible_bytes == assemble(prompt_definition, canonical_dossier_bytes)` and prevents callers constructing inconsistent source/final representations. `Claim` carries a site-specific canonical JSON mapping plus exactly one of citations or `Unknown`. `P8Verdict` carries the SPEC fields and validates cross-field invariants at construction. Internal modules import `P8Verdict` explicitly; `__init__.py` exports no ambiguous `Verdict`. `ValidationUnavailable` names missing injected capabilities and never aliases `abstain`.

- [ ] **Step 4: Run GREEN and guards**

Run: `pytest -q tests/p8/test_p8_records.py tests/p8/test_p8_vocabulary.py`

Expected: PASS. Also run `rg -n 'needs_consent|normalize\(|contradicts\(' src/llm_harness` and verify only explanatory guards/references exist, not an invented implementation or reason code.

- [ ] **Step 5: Commit**

```bash
git add src/llm_harness/__init__.py src/llm_harness/vocabulary.py src/llm_harness/records.py tests/p8/test_p8_records.py tests/p8/test_p8_vocabulary.py
git commit -m "feat(p8): define bounded harness contracts"
```

## Task 2: Deterministic fingerprint and dossier identity

**Files:**
- Create: `src/llm_harness/fingerprint.py`
- Test: `tests/p8/test_p8_fingerprint.py`

- [ ] **Step 1: Write failing tests**

Test that `prompt_fingerprint(PromptDefinition)` changes for prompt template bytes, response schema, call site, call-site version, or shaping-policy options; remains stable under equivalent canonical source fields; and is a digest rather than embedded raw prompt/evidence. Test that `build_call_payload(...)` retains the immutable definition and canonical dossier source, deterministically assembles exact model-visible bytes, and binds the same `ModelTarget` and policy version carried by `Released`. Mutating either source must change the recomputed result; supplying inconsistent preassembled bytes must be impossible through the public factory. Test that `dossier_content_address(...)` hashes the exact canonical **model-visible dossier payload** (released material plus allowed schema/vocabulary), excludes capability/provenance values such as `release_id` and `audit_id`, is byte-identical for equivalent payloads, and changes when any byte shown to the model changes. The current evidence-snapshot identity is stored separately for revalidation; it is not falsely described as part of the dossier content address.

- [ ] **Step 2: Run RED**

Run: `pytest -q tests/p8/test_p8_fingerprint.py`

Expected: FAIL with `ModuleNotFoundError: llm_harness.fingerprint`.

- [ ] **Step 3: Implement with the repository's canonical serializer**

```python
def prompt_fingerprint(definition: PromptDefinition) -> str:
    payload = canonical_json({...}).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
```

Do not create prompt text, response schemas, or policy values here; callers inject them.

- [ ] **Step 4: Run GREEN**

Run: `pytest -q tests/p8/test_p8_fingerprint.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/llm_harness/fingerprint.py tests/p8/test_p8_fingerprint.py
git commit -m "feat(p8): add deterministic call fingerprints"
```

## Task 3: Append-only P8 storage and provenance

**Files:**
- Create: `src/llm_harness/schema.py`
- Create: `src/llm_harness/store.py`
- Test: `tests/p8/test_p8_store.py`
- Test: `tests/p8/test_p8_provenance.py`

- [ ] **Step 1: Write failing schema and history tests**

Require only Task 3's tables: `llm_dossier`, `llm_response`, `llm_verdict`, `llm_grounding_report`, `llm_verdict_supersession`, `llm_refusal` (P7 denial only), `llm_pre_call_abstention`, and `llm_call_failure`. Budget schema belongs wholly to Task 4 and is neither created nor tested here. Store canonical payloads plus explicit indexed identity/version columns. Prove inserts preserve raw response bytes, prior verdicts survive supersession, UPDATE/DELETE on audit tables is refused by triggers, and matrix-designated provenance writes use `subsystem="P8"` with required `audit_id`/fingerprint/model provenance in the explanation.

Pin this exact writer→event matrix; no writer may append a sixth or convenience event:

| Writer | Event |
|---|---|
| `record_dossier` | none |
| transport immediately before client call | `model_call_issued` |
| `record_response` after bytes return | `model_response_received` |
| `record_verdict` | `validation_verdict` |
| `supersede_verdict` | `verdict_superseded` |
| `record_refusal` for P7 `Denied` only | `call_refused`; also stores that refusal's zero-count grounding report |
| `record_pre_call_abstention` for ineligible, suppression, or exhausted budget | `call_refused`; also stores that abstention's zero-count grounding report |
| `record_grounding_report` | none; issued-call reports derive from validation, refused-call reports derive from the refusal |
| `record_call_failure` | none; it is a terminal row attached to the already-issued call |
| `NeedsConsent` | no P8 writer and no P8 event |

- [ ] **Step 2: Run RED**

Run: `pytest -q tests/p8/test_p8_store.py tests/p8/test_p8_provenance.py`

Expected: FAIL because schema/store modules are absent.

- [ ] **Step 3: Implement schema and narrow writers**

Expose:

```python
create_llm_schema(conn) -> None
record_dossier(conn, dossier, *, observed_at: str) -> str
record_response(conn, *, dossier_id: str, response_bytes: bytes, model_id: str,
                prompt_fingerprint: str, release_audit_id: int, observed_at: str) -> str
record_verdict(conn, verdict, *, observed_at: str) -> str
supersede_verdict(conn, old_verdict_id: str, new_verdict_id: str, *, reason: str,
                  observed_at: str) -> None
record_grounding_report(conn, report, *, observed_at: str) -> str
record_refusal(conn, refusal, report: GroundingReport, *, observed_at: str) -> str
record_pre_call_abstention(conn, abstention: PreCallAbstention,
                           report: GroundingReport, *, observed_at: str) -> str
record_call_failure(conn, *, dossier_id: str, failure_class: str,
                    explanation: str, observed_at: str) -> str
```

Only the five event **types** named in the matrix are emitted: transport issue, response recording, `record_verdict`, `supersede_verdict`, and either pre-call terminal writer emits the already-registered `call_refused`. Each `append_event` call supplies live required fields (`event_type`, `subsystem="P8"`, `component_version`, `observed_at`, `explanation`) and writes the canonical fingerprint through P1's dedicated `prompt_fingerprint` keyword as well as putting audit/model context in the explanation. Task 3 tests monkeypatch `append_event` and assert the exact count/type for every store-owned row—response, verdict, supersession, refusal, pre-call abstention, dossier, report, and failure. Each pre-call terminal writer atomically inserts its own row plus its zero-count grounding report and appends one `call_refused` event; `Refusal` is constructible only from a P7 `Denied`, preserving B2 literally. Calling `record_grounding_report` for an issued/validated call appends no event. The transport-issue row is intentionally completed in Task 5, after `transport.issue` exists. There is no runtime event registration and no overwrite/upsert.

- [ ] **Step 4: Run GREEN and P1 regression**

Run: `pytest -q tests/p8/test_p8_store.py tests/p8/test_p8_provenance.py tests/test_events.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/llm_harness/schema.py src/llm_harness/store.py tests/p8/test_p8_store.py tests/p8/test_p8_provenance.py
git commit -m "feat(p8): persist replayable model validation history"
```

## Task 4: Enforce eligibility, negative-feedback suppression, and scan-scoped budgets before release

**Files:**
- Create: `src/llm_harness/eligibility.py`
- Create: `src/llm_harness/budgets.py`
- Test: `tests/p8/test_p8_eligibility.py`
- Test: `tests/p8/test_p8_budgets.py`

- [ ] **Step 1: Write failing decision-table tests**

Cover every closed eligibility reason from SPEC §2, imported from P8's own vocabulary rather than injected. Implement `suppressed_by_learning(conn, *, scope, subject_id, proposal_class, basis_key)` as a narrow adapter over `database_agent.learning.learning_records(conn, scope, subject_id)`: match exact `proposal_class` and `basis_key`, honor P1's reset cutoff through that API, and suppress only a current negative/rejected polarity. P13 has not authored the production correction events yet, so tests seed fixture events through P1; omission of `conn` or scope/subject identity returns `ValidationUnavailable`. This is not a second store. Direct unique matches produce `PreCallAbstention(NOT_ELIGIBLE_FOR_MODEL)` before gate access. A suppressed equivalent produces `PreCallAbstention(USER_REJECTED_EQUIVALENT)`.

For budgets, create a scan-keyed SQLite ledger with atomic reservations for both concrete metrics named by the design: `model.max_calls_per_1000_files` and `model.max_estimated_cost_per_scan`. Their **values** are required injected/stored ceilings with no default. Define `ScanBudget(scan_id, corpus_file_count, max_calls_per_1000_files, max_estimated_cost)` and compute the allowed calls as `floor(corpus_file_count * max_calls_per_1000_files / 1000)`. Tests cover 0, 1, 999, 1000, and 1001 files, exact-boundary acceptance, one-over refusal, estimated-cost equality/overflow, rollback after a pre-transport failure, settlement of actual cost, and two concurrent SQLite connections racing for the final reservation—exactly one succeeds.

Task 4 alone adds `llm_scan_budget` and `llm_budget_reservation` through `create_budget_schema(conn)`. Its fixture first calls the already-built `create_llm_schema(conn)` from Task 3, then `create_budget_schema(conn)`; Task 3 never references these later tables.

The reduction record is exact: `none -> summarized_facts -> preserved_anchors -> split -> deferred`; `none` records an unreduced fitting request and is not a transformation attempt. Summarization and anchor preservation are **pre-egress dossier transformations**: while the candidate remains oversized they spend no release, reserve no call/cost, and invoke no client. `split` may produce multiple independently bounded dossier requests; each fitting shard obtains its own P7 release and budget reservation immediately before its one call. If no transformed dossier/shard fits, `deferred` yields `BUDGET_EXHAUSTED`, a zero-count pre-call abstention report, and no model call. Task 4 tests these pure size/budget transitions without P7. Task 9 tests the operational call counts and releases after composition exists.

- [ ] **Step 2: Run RED**

Run: `pytest -q tests/p8/test_p8_eligibility.py tests/p8/test_p8_budgets.py`

Expected: FAIL because `llm_harness.eligibility` is absent.

- [ ] **Step 3: Implement pure pre-call decisions**

```python
def assess_call(request: DossierRequest, *,
                conn: sqlite3.Connection | None,
                learning_scope: str | None,
                learning_subject_id: str | None) -> Eligible | PreCallAbstention | ValidationUnavailable:
    ...
```

Expose `create_budget_schema(conn)`, `reserve_call(conn, budget: ScanBudget, *, estimated_cost: Decimal) -> BudgetReservation`, `settle_call(...)`, and `release_reservation(...)`. P8 does not claim P1's transaction helper provides `BEGIN IMMEDIATE` and does not modify it. Live `open_database` connections use `isolation_level=None`, so `budgets.py` explicitly issues its own scoped `BEGIN`, executes one conditional counter statement—`INSERT ... ON CONFLICT DO UPDATE ... WHERE calls_reserved + 1 <= ? AND estimated_cost_reserved + ? <= ? RETURNING ...`—inserts the reservation detail, and commits; on any failure it rolls back. The conditional write obtains SQLite's writer lock and re-evaluates against the committed row, so calls and estimated cost advance together or not at all. The helper rejects entry when `conn.in_transaction` is already true rather than silently changing an outer transaction's isolation. A file-backed test uses the live `database_agent.db.open_database` seam, opens two independent connections, synchronizes two workers at the final slot, and proves one `RETURNING` row, one `BudgetExhausted`, one counter increment, one reservation detail, and `PRAGMA integrity_check = ok`. This is a scoped P8 mechanism, not a claim about or change to P1. No evidence materialisation, model client, default ceiling, or prompt content may enter these modules.

- [ ] **Step 4: Run GREEN**

Run: `pytest -q tests/p8/test_p8_eligibility.py tests/p8/test_p8_budgets.py`

Expected: PASS with branch coverage for every refusal/unavailable path.

- [ ] **Step 5: Commit**

```bash
git add src/llm_harness/eligibility.py src/llm_harness/budgets.py tests/p8/test_p8_eligibility.py tests/p8/test_p8_budgets.py
git commit -m "feat(p8): fail closed before model release"
```

## Task 5: Build the single release-consuming transport

**Files:**
- Create: `src/llm_harness/transport.py`
- Test: `tests/p8/test_p8_transport.py`
- Create: `tests/integration/test_p8_p7_egress.py`

- [ ] **Step 1: Write failing structural and integration tests**

Define `ModelClient` as an immutable, target-bound capability rather than a free callable:

```python
@dataclass(frozen=True, slots=True)
class ModelClient:
    model_target: ModelTarget
    invoke: Callable[[bytes], bytes]
```

`model_target` is authoritative for where bytes will actually go; callers cannot supply a second target to `invoke`. `run_call` may carry the injected capability to the boundary, but assert the sole function that invokes `ModelClient.invoke` has this authority-bearing shape:

```python
issue(conn, released: Released, payload: CallPayload, *,
      model_client: ModelClient) -> ModelResponse
```

Test forged `Released` → `ReleaseNotIssued`, binding mismatch → `BindingMismatch`, second use → `ReleaseAlreadySpent`, and real `Gate.release(...) -> Released` → exactly one client call. `issue` recomputes `prompt_fingerprint(payload.prompt_definition)`, reassembles exact model-visible bytes from `payload.prompt_definition` and `payload.canonical_dossier_bytes`, compares both results to the stored payload fields, and first requires `model_client.model_target == payload.model_target == released.model_target`. It then passes the authoritative `model_client.model_target`, recomputed fingerprint, and payload policy version into P7 `consume_release`; that function checks all three against the ledger **before** its conditional spend update. Only after it returns does transport invoke the client. Add both mismatch directions, especially a cloud-bound client paired with a local payload/release and a local client paired with a cloud payload/release: each raises `BindingMismatch`, records zero client invocations, and leaves the ledger row unspent. The client receives only `payload.model_visible_bytes`; it does not receive `release_id`, policy version, audit id, model target metadata, or fingerprint unless those bytes were deliberately part of the authored prompt source. Transport verifies immutable sources; it never invents, queries, or mutates them.

Parse every Python module under `src/llm_harness` with AST. Permit `model_client` as a parameter/forwarded name in `harness.run_call` and `transport.issue`, but assert that every `ast.Call` whose callee resolves to `model_client.invoke` occurs in `transport.py:issue` only. Also assert no alias, method wrapper, lambda, or imported SDK call creates a second egress.

- [ ] **Step 2: Run RED**

Run: `pytest -q tests/p8/test_p8_transport.py tests/integration/test_p8_p7_egress.py`

Expected: FAIL because transport does not exist.

- [ ] **Step 3: Implement the one egress**

Call `privacy.binding.consume_release(...)` before invoking the injected client. Construct `CallPayload` through Task 2's sole `build_call_payload(...)` factory before transport from `PromptDefinition` plus `released.materialised_items`; do not query P4/P1 on the outbound path. Record `model_call_issued` immediately before client invocation and `model_response_received` immediately after bytes return, both carrying P7 `audit_id` and the canonical fingerprint. If the client raises or returns malformed transport bytes, write `llm_call_failure` and return `CallFailed` carrying the immutable request/release fields Task 6 needs to report the attempt; do not fabricate a response, verdict, refusal, `call_refused`, or an event outside P8's registered five. Task 9, after Task 6 exists, persists the required zero-count grounding report and P2 `error` for that result.

- [ ] **Step 4: Run GREEN plus P7 release tests**

Run: `pytest -q tests/p8/test_p8_transport.py tests/integration/test_p8_p7_egress.py tests/p7/test_p7_binding.py tests/p7/test_p7_release.py`

Expected: PASS; the fake client count is zero for every denied, consent, forged, mismatched, or spent release.

- [ ] **Step 5: Commit**

```bash
git add src/llm_harness/transport.py tests/p8/test_p8_transport.py tests/integration/test_p8_p7_egress.py
git commit -m "feat(p8): enforce P7 as the single model egress"
```

## Task 6: Implement universal deterministic validation and grounding

**Files:**
- Create: `src/llm_harness/validation.py`
- Test: `tests/p8/test_p8_validation.py`
- Test: `tests/p8/test_p8_grounding.py`

- [ ] **Step 1: Write one failing test per universal reason code**

Use recorded response bytes only. Cover malformed schema, uncited claim, citation outside dossier, unresolved observation key, span absent from released material, stronger contradiction reported by injected oracle, explicit unknown, direct acceptance, context acceptance, and weak outcome. Assert citations resolve by P4 `observation_key`, while span matching uses the released/redacted material the model saw—not raw SQLite text. Honor SPEC Done 11: `GroundingReport` is emitted for every P8 call attempt, including pre-egress refusals. `report_for_refusal(...)` fills `dossier_id`, `call_site`, intended `model_id`, fingerprint, validator version, reduction rung, and dossier builder; sets `release_audit_id=None`; sets every citation/claim counter to zero; and sets `reasons_histogram={refusal.reason: 1}`. Gate `Denied`, ineligibility, suppression, and budget exhaustion each get this report plus `call_refused` and their P2 abstained/deferred mapping. `NeedsConsent` remains outside P8's call/outcome vocabulary and emits neither report nor event. An issued-call transport failure has a call attempt and therefore gets a zero-count grounding report using only the SPEC fields, with the real `release_audit_id` and an empty reason histogram; `llm_call_failure` and P2 `error` carry the failure distinction without inventing a verdict reason or report field.

- [ ] **Step 2: Run RED**

Run: `pytest -q tests/p8/test_p8_validation.py tests/p8/test_p8_grounding.py`

Expected: FAIL because universal validator is absent.

- [ ] **Step 3: Implement ordered pure checks**

Expose `validate_response(dossier, response_bytes, *, evidence_resolver, site_validator)` for response-bearing reports and `report_for_pre_call_terminal(request, terminal: Refusal | PreCallAbstention, *, validator_version)` for zero-count reports. Parse JSON once, preserve raw bytes, validate claims in stable input order, and report all deterministic checks without consulting a model. Response-bearing reports derive solely from verdict/citation results; pre-call reports derive solely from the immutable request/terminal record.

- [ ] **Step 4: Prove determinism**

Run the same validation 100 times in the test and compare `canonical_json(verdicts)` and report bytes. Run: `pytest -q tests/p8/test_p8_validation.py tests/p8/test_p8_grounding.py`.

Expected: PASS and byte-identical outputs.

- [ ] **Step 5: Commit**

```bash
git add src/llm_harness/validation.py tests/p8/test_p8_validation.py tests/p8/test_p8_grounding.py
git commit -m "feat(p8): add deterministic grounding validator"
```

## Task 7: Implement Site A only through explicit P6-domain dependencies

**Files:**
- Create: `src/llm_harness/fact_validation.py`
- Test: `tests/p8/test_p8_fact_validation.py`
- Test: `tests/integration/test_p8_p6_fact_seam.py`

- [ ] **Step 1: Write the missing-prerequisite tests first**

Prove live `facts` exports no `normalize` or `contradicts`. Then require:

```python
@dataclass(frozen=True)
class FactValidationDependencies:
    normalize: Callable[[str, str], object]
    contradicts: Callable[[Proposal, sqlite3.Row], bool]
```

Omitting either must produce `ValidationUnavailable(missing=(...))`, no transport call, no `P8Verdict`, and no P6 fact/unresolved row.

- [ ] **Step 2: Run RED**

Run: `pytest -q tests/p8/test_p8_fact_validation.py tests/integration/test_p8_p6_fact_seam.py`

Expected: FAIL because the dependency type/validator does not exist—not because imaginary P6 imports fail.

- [ ] **Step 3: Implement the four §3.6 checks**

In exact order: field in `FactRequest.allowlist`; every citation in `FactRequest.citable_observations`; injected normalization succeeds; injected contradiction oracle finds no stronger conflict. Map a P8 `P8Verdict` to the distinct live `facts.llm_seam.Verdict(passed, failed_check)`, using members of `facts.llm_seam.FOUR_CHECKS` rather than copied strings. Call `facts.llm_seam.apply_verdict(conn, request=request, proposal=proposal, verdict=p6_verdict, proposal_state=proposal_state, model_identifier=model_identifier, prompt_fingerprint=prompt_fingerprint)`. `proposal_state` is required with no default: `accept_direct` and `accept_context_supported` map to `facts.states.LLM_SUPPORTED`; `weak` maps to `facts.states.POSSIBLE`; reject/unknown paths preserve P6's unresolved consequences. Do not duplicate P6 writes or reliability logic.

- [ ] **Step 4: Run GREEN with fixture callbacks**

Run: `pytest -q tests/p8/test_p8_fact_validation.py tests/integration/test_p8_p6_fact_seam.py tests/p6/test_p6_llm_seam.py`

Expected: PASS. The callbacks are explicit test fixtures; they are not shipped defaults and contain no domain catalogue.

- [ ] **Step 5: Commit**

```bash
git add src/llm_harness/fact_validation.py tests/p8/test_p8_fact_validation.py tests/integration/test_p8_p6_fact_seam.py
git commit -m "feat(p8): validate fact proposals through explicit domain rules"
```

## Task 8: Implement Sites B–E against neighbour fixtures

**Files:**
- Create: `src/llm_harness/group_validation.py`
- Create: `src/llm_harness/placement_validation.py`
- Create: `src/llm_harness/template_validation.py`
- Create: `src/llm_harness/fixtures.py`
- Test: `tests/p8/test_p8_group_validation.py`
- Test: `tests/p8/test_p8_placement_validation.py`
- Test: `tests/p8/test_p8_template_validation.py`
- Test: `tests/p8/test_p8_fixtures.py`

- [ ] **Step 1: Write failing reason-registry coverage tests**

Create one recorded dossier/response pair per B–E reason code plus direct accept, context accept, weak, reject, and unknown. Assert no fixture imports P9/P10/P11. Require injected `node_exists`, support threshold, margin predicate, sensitivity-policy predicate, approved target ids, and strict template schema validator—with no defaults. The residual controlled-action set is **not injected**: it is the exact P8-owned eight constants from Task 1. Only approved residual/group/node IDs are injected.

- [ ] **Step 2: Run RED**

Run: `pytest -q tests/p8/test_p8_group_validation.py tests/p8/test_p8_placement_validation.py tests/p8/test_p8_template_validation.py tests/p8/test_p8_fixtures.py`

Expected: FAIL because site validators/fixtures do not exist.

- [ ] **Step 3: Implement Site B checks**

Enforce dossier membership closure, no invented date/project/purpose/member, no final hierarchy, label only with coherence, direct-anchor versus context-supported basis, and generic-similarity rejection. P8 validates a proposed conclusion; it does not retrieve neighbours, create a group, or accept membership on P9's behalf.

- [ ] **Step 4: Implement Sites C/D checks and plan-version revalidation**

Use required injected tree/policy oracles. Enforce frozen-tree membership, no invented path slot, conflicts considered, sensitivity policy, the SPEC's two-condition weak rule at Site C only, the eight-action closed set, same-file evidence, and `STRONGER_RELATIONSHIP_OVERLOOKED -> return_to_placement`. Q3 remains open for Site D: no two-condition rule is inferred there; a D fixture needing that judgment returns `ValidationUnavailable(missing=("site_d_support_rule",))`. Store `plan_version` and an evidence-snapshot identity with every C/D verdict. Add `revalidate_for_plan(conn, *, current_plan_version, ...)` that never migrates an old verdict: if either identity differs, append a new verdict and supersession after deterministic revalidation; if required current oracles are absent, return `ValidationUnavailable` and leave the prior row historical/inactive for the changed plan. Test same-version stability and changed-plan supersession before declaring C/D live. Do not create tree nodes, residual destinations, thresholds, or actions.

- [ ] **Step 5: Implement Site E checks**

Run the injected strict JSON-schema validator, citation validation per proposed dimension, and allowed-vocabulary closure. P10 remains responsible for template design quality; P8 does not invent or score a hierarchy.

- [ ] **Step 6: Run GREEN**

Run: `pytest -q tests/p8/test_p8_group_validation.py tests/p8/test_p8_placement_validation.py tests/p8/test_p8_template_validation.py tests/p8/test_p8_fixtures.py`

Expected: PASS and every site-specific reason constant exercised exactly once by the registry test.

- [ ] **Step 7: Commit**

```bash
git add src/llm_harness/group_validation.py src/llm_harness/placement_validation.py src/llm_harness/template_validation.py src/llm_harness/fixtures.py tests/p8/test_p8_group_validation.py tests/p8/test_p8_placement_validation.py tests/p8/test_p8_template_validation.py tests/p8/test_p8_fixtures.py
git commit -m "feat(p8): validate bounded neighbour proposals"
```

## Task 9: Compose gate branches without collapsing consent

**Files:**
- Create: `src/llm_harness/harness.py`
- Test: `tests/p8/test_p8_harness.py`

- [ ] **Step 1: Write failing end-to-end branch tests**

Test `run_call(...)` with a fake P7 gate returning each branch:

- `Released`: issue once, validate locally, persist response/verdict/report.
- `Denied`: return `Refusal(PRIVACY_GATE_REFUSED)`, atomically store its zero-count grounding report, append `call_refused`, and do not call model.
- `NeedsConsent`: return the same object unchanged, append no P8 event/stage output/verdict, do not call model.
- `NoPolicyInForce`: propagate the live P7 exception unchanged; it is not a fourth decision branch and writes no P8 result.
- missing configuration: return `ValidationUnavailable`, make no gate/model call.
- model error: persist `llm_call_failure`, append no invented event, return `CallFailed`, store a zero-count issued-call grounding report, and fabricate neither response nor verdict.
- over-budget reduction: record `none` for an initially fitting call; otherwise apply `summarized_facts`, then `preserved_anchors`, then `split` entirely before release. Assert oversized intermediate forms produce zero gate releases, reservations, and invocations; each fitting split shard gets one distinct request/release/reservation/call; `deferred` gets none and emits the required pre-call abstention report.
- retry policy: Q8 remains open. `run_call` performs exactly one attempt and returns `CallFailed` or a schema-invalid `P8Verdict`; it does not retry. A future caller may start a new request only after Q8 is ratified, and any such design must require a new `ModelCallRequest`, P7 release, and budget reservation rather than reusing a spent release.

- [ ] **Step 2: Run RED**

Run: `pytest -q tests/p8/test_p8_harness.py`

Expected: FAIL because `run_call` is absent.

- [ ] **Step 3: Implement the orchestration boundary**

```python
def run_call(conn, request: DossierRequest, *, gate: Gate, model_client: ModelClient,
             prompt: PromptDefinition | None, validation_dependencies,
             observed_at: Callable[[], str]) -> (
                 P8Verdict | Refusal | NeedsConsent |
                 ValidationUnavailable | CallFailed):
    ...
```

The request remains reference-only until `gate.release`. Construct the live `privacy.release.ModelCallRequest` using only exact `privacy.items.RequestedItem` variants (`Excerpt`, `RedactedIdentifier`, `CandidateLabel`, `MetadataField`, `EvidenceReference`, and the explicitly unratified `Filename` only when the live caller has ratified/allowed it), `privacy.release.Target`, and the exact `privacy.release.ModelTarget`; do not create P8 twins. Integration tests replay records from `privacy.fixtures.by_number` through a real `privacy.gate.Gate` and supply every required constructor authority: `store`, `plan_version`, `classifier`, `transform`, `unclassified_permits_local`, `scope_for`, `files_in_scope`, `component_version`, `now`, and `user_id`. Optional `measure_tokens`/`template_for` remain explicit fixture inputs when exercised; no default is treated as authored policy. Pre-egress reductions transform references and obtain no release until a bounded dossier (or bounded split shard) is ready. Q8 leaves automatic retry disabled. `NoPolicyInForce` propagates unchanged. D14 is explicit: use `Released.audit_id` for event linkage and `Released.release_id` for ledger consumption; never expect `AuditRecord.release_id` on the grant row, where it is `None`.

- [ ] **Step 4: Run GREEN and branch-exhaustiveness assertion**

Run: `pytest -q tests/p8/test_p8_harness.py tests/integration/test_p8_p7_egress.py`

Expected: PASS; exactly three P7 branch types are handled and `NeedsConsent` has no conversion path.

- [ ] **Step 5: Commit**

```bash
git add src/llm_harness/harness.py tests/p8/test_p8_harness.py
git commit -m "feat(p8): compose gated calls without collapsing consent"
```

## Task 10: Emit the P2 measurement and replay without a model call

**Files:**
- Create: `src/llm_harness/stage_output.py`
- Test: `tests/p8/test_p8_stage_output.py`
- Create: `tests/integration/test_p8_p2_replay.py`

- [ ] **Step 1: Write failing mapping/replay tests**

Pin the SPEC mapping: verdicts `accept_direct`, `accept_context_supported`, `weak`, `reject` → P2 `produced/within_ceiling`; model unknown, gate `Refusal`, and ordinary `PreCallAbstention` → `abstained/within_ceiling`; `BUDGET_EXHAUSTED` → `deferred/ceiling_reached`; failures → `error`; `NeedsConsent` → no row. Require `stage_id="llm_interpretation"`, inputs, and an opaque canonical payload. Before emission, create a live P2 version tuple through `eval_harness.run.record_version_tuple` with exactly the seven `VERSION_TUPLE_FIELDS`: `extractor_versions`, `graph_algorithm_version`, `prompt_fingerprint`, `model_identifier`, `template_library_version`, `placement_scorer_version`, and `analysis_tiers_enabled`. P8 supplies the fingerprint/model values and requires the caller to inject every other axis explicitly (an intentionally empty value is caller-authored, never a P8 default). `validator_version` and `policy_version` belong in the opaque P8 payload and P8 verdict/report rows, not the P2 version tuple. Tests prove extra keys and the stale four-field tuple are refused.

- [ ] **Step 2: Run RED**

Run: `pytest -q tests/p8/test_p8_stage_output.py tests/integration/test_p8_p2_replay.py`

Expected: FAIL because P8's mapping is absent.

- [ ] **Step 3: Implement the single mapping function**

```python
def emit_stage_output(conn, *, run_id: str, subject_ref: str,
                      result: P8Verdict | Refusal | CallFailed,
                      inputs: tuple[str, ...], version_tuple_ref: str) -> int:
    return record_stage_output(...)
```

Call live `eval_harness.stage_output.record_stage_output(conn, run_id=..., stage_id="llm_interpretation", subject_ref=..., outcome=..., payload=..., version_tuple_ref=..., inputs=..., budget_state=...)`; it stamps `produced_at` internally, so P8 passes no such keyword. Require `run_id` to identify an existing `run_manifest` row created with `eval_harness.run.start_run`; the integration fixture calls `record_version_tuple`, then `start_run`, then emits. Reject `NeedsConsent` at the type/runtime boundary. Replay loads stored response bytes and re-runs validation against the current evidence snapshot without calling `ModelClient`; cached validation is never trusted blindly.

- [ ] **Step 4: Run GREEN with P2 regression**

Run: `pytest -q tests/p8/test_p8_stage_output.py tests/integration/test_p8_p2_replay.py tests/p2`

Expected: PASS and fake model call count remains zero during replay.

- [ ] **Step 5: Commit**

```bash
git add src/llm_harness/stage_output.py tests/p8/test_p8_stage_output.py tests/integration/test_p8_p2_replay.py
git commit -m "feat(p8): publish replayable grounding measurements"
```

## Task 11: Add no-bypass, no-invention, and dependency-boundary guards

**Files:**
- Create: `tests/p8/test_p8_architecture.py`
- Create: `tests/p8/test_p8_no_invention.py`

- [ ] **Step 1: Write architecture guards**

Use AST/import introspection, not comment-sensitive substring tests, to assert:

- `harness.run_call` may accept/forward `ModelClient`, but AST call-site resolution proves only `transport.issue` invokes it;
- `transport.issue` requires live P7 `Released` and calls `consume_release`;
- outbound transport imports neither evidence-store readers nor P6/P9/P10/P11;
- no P8 module imports `planning/domains`, prompts, deferred catalogues, network/model SDKs, or readers;
- every configurable callback/threshold/prompt has no default; closed P8 eligibility/reason/outcome/action vocabularies are local named constants and are never injected;
- P8 exports no detector, redactor, normalizer, contradiction domain rule, tree builder, grouping producer, or placement producer;
- every reason/outcome/site/reduction value has one named home.

- [ ] **Step 2: Run the guards and correct violations**

Run: `pytest -q tests/p8/test_p8_architecture.py tests/p8/test_p8_no_invention.py`

Expected: PASS. Any failure is fixed by removing duplicate authority, not weakening the assertion.

- [ ] **Step 3: Run Graphify connection checks**

Run:

```bash
graphify update .
graphify path "privacy.release.Released" "llm_harness.transport.issue"
graphify path "llm_harness.stage_output.emit_stage_output" "eval_harness.stage_output.record_stage_output"
graphify path "facts.llm_seam.FactRequest" "llm_harness.fact_validation"
graphify diagnose
```

Expected: P7→P8, P8→P2, and P6→P8 paths exist; no alternate model-client path; diagnose reports no new P8 structural issue. P9/P10/P11 paths remain fixture-mediated and are not claimed live.

- [ ] **Step 4: Commit**

```bash
git add tests/p8/test_p8_architecture.py tests/p8/test_p8_no_invention.py
git commit -m "test(p8): guard model egress and authored-policy boundaries"
```

## Task 12: Full verification and handoff gates

**Files:**
- Create: `tests/integration/test_p8_walking_skeleton.py`
- Create: `tests/p8/determinism_probe.py`
- Modify only if evidence requires it: files already owned by Tasks 1–11.

- [ ] **Step 1: Write and run one full P7→P8→P6→P2 walking skeleton**

Seed a real P1/P4/P6 SQLite fixture with one ambiguous file, one current P7 classification and policy, and one citable observation. Build a reference-only Site-A request and pass it through a real `Gate.release`; use a fake deterministic `ModelClient` only at `transport.issue`; return one cited claim; validate it with explicitly supplied fixture normalization/contradiction callbacks; pass the accepted result through `facts.llm_seam.apply_verdict`; then emit P2 `llm_interpretation` stage output. Assert, in order:

1. the gate audit and release ledger precede transport;
2. exactly one release is spent and exactly one model invocation occurs;
3. citation resolves and matches the released text;
4. one P8 verdict/report is stored;
5. one active P6 `llm_supported` fact cites the observation key and records model/fingerprint;
6. one P2 `produced/within_ceiling` row references the exact seven-field live version tuple, while `validator_version` and `policy_version` remain in the opaque P8 payload/verdict/report;
7. the exact writer→event matrix holds.

Run: `pytest -q tests/integration/test_p8_walking_skeleton.py`

Expected: PASS. This proves the current live seams; it does not claim the fixture domain callbacks are the unresolved C-5 production authority.

- [ ] **Step 2: Run focused P8 and seam suites**

Run:

```bash
pytest -q tests/p8
pytest -q tests/integration/test_p8_p7_egress.py tests/integration/test_p8_p6_fact_seam.py tests/integration/test_p8_p2_replay.py
pytest -q tests/integration/test_p8_walking_skeleton.py
pytest -q tests/p6/test_p6_llm_seam.py tests/p7/test_p7_binding.py tests/p7/test_p7_release.py tests/p2
```

Expected: all pass.

- [ ] **Step 3: Run the complete repository suite**

Run: `pytest -q`

Expected: all tests pass with no deselections introduced by P8.

- [ ] **Step 4: Verify deterministic replay across two fresh processes**

`tests/p8/determinism_probe.py` creates its own temporary database, seeds fixed logical inputs, validates a recorded response, and writes a canonical JSON line containing the model-visible dossier address, response-bytes SHA-256, verdict canonical JSON, grounding-report canonical JSON, and P2 payload. It normalizes only documented database-generated ids/timestamps before output.

Run two independent interpreters, not two calls in one process:

```bash
python -m tests.p8.determinism_probe > /tmp/p8-determinism-a.json
python -m tests.p8.determinism_probe > /tmp/p8-determinism-b.json
cmp /tmp/p8-determinism-a.json /tmp/p8-determinism-b.json
```

Expected: `cmp` exits 0. Then run the same probe with one released model-visible byte changed and assert the dossier address differs, while changing only release/audit ids leaves it unchanged.

- [ ] **Step 5: Verify dependency gates before declaring P8 complete**

P8 may be declared **core complete, neighbour-fixture complete** when Tasks 1–12 pass. It may not be declared **live end-to-end complete** until all of these are true:

1. P1–P7 live assembly reaches authoritative P7 classification and gate release.
2. The C-5 ruling names and implements the real P6 normalization and contradiction authorities, replacing test fixture callbacks without changing P8's validator contract.
3. Authored prompts and deployment model transport are provided explicitly.
4. P9/P10/P11 producers replace B–E fixtures at their named dossier-builder seams.
5. P13 consumes `NeedsConsent` unchanged and presents all four choices.

- [ ] **Step 6: Request two-stage review**

First review design/spec fidelity and authority ownership; then review code quality, failure modes, and test evidence. Resolve every Critical/Important finding and rerun Steps 1–4 before any completion claim.

## Open-question and divergence ledger

- **Q8 retry remains open.** This plan performs one attempt and defines no automatic
  retry. A later ratification must specify eligibility, budget denominator, and P2
  grounding semantics; any retry would require a new request, release, and reservation.
- **Q3 Site-D support remains open.** The two-condition rule is implemented for Site
  C only. Site D fails with `ValidationUnavailable` when that missing rule is needed.
- **Q1, Q2, Q6, Q7, and Q9 remain open** and are required injections or disabled
  paths; the plan does not choose a model, support threshold, weak-fact re-entry rule,
  conflict policy, or Site-D batch granularity.
- **Q4 follows SPEC §7.** Validation compares citations against the released text
  and retained observation references; it does not invent a redaction reverse map.
- **Live P2 shape overrides stale SPEC envelope prose without changing meaning.** The
  run version tuple has the seven live `VERSION_TUPLE_FIELDS`; P8-specific validator
  and policy versions remain in P8's opaque payload and own records.
- **Charter path relocation is explicit.** `planning/29-DOMAIN-OWNERSHIP.md` already
  occupies 29, so the shared contract is `planning/30-p8-p9-connection-contract.md`.

## Integration seam ledger

| Producer | Consumer | Live now? | P8 plan treatment | Failure mode |
|---|---|---:|---|---|
| P7 `Gate.release(ModelCallRequest)` | `harness.run_call` | Yes | Direct integration test | Branch preserved; no model call on denial/consent |
| P7 `Released` + ledger | `transport.issue` | Yes | Required authority type and consume-before-call | Forged/mismatched/spent release raises before egress |
| P4 observation key/store | local validation | Yes | Exact ref resolution after response | Reject citation; never fuzzy-match |
| P6 `FactRequest`/`apply_verdict` | Site A | Yes | Reuse live seam | P6 owns consequence; P8 owns checks |
| P6 normalization/contradiction domain logic | Site A | **No** | Required callbacks, no defaults | `ValidationUnavailable`; no call/verdict/fact |
| P9 group dossier | Site B | No | P8 fixture, exact eventual swap at dossier input | No active group decision |
| P10 frozen-tree/schema oracles | Sites C–E | No | Required injected fixture oracles | `ValidationUnavailable` |
| P11 placement/residual dossier | Sites C/D | No | P8 fixture only | No placement/residual decision |
| P8 report/result | P2 stage output | Yes | Exact mapping test | Writer rejects foreign vocabulary |
| P8 `NeedsConsent` return | P13 | No | Preserve unchanged; no fixture conversion | Caller must surface; never abstain |

## Completion standard

The implementation succeeds when P8 is provably the only model egress; no unreleased content can reach its client; denial and consent remain distinct; every recorded response is deterministically validated against a closed released dossier; citations and outcomes are replayable; P2 receives the correct stage semantics; and missing authored inputs stop safely. Passing fixture tests does not imply the unfinished domain, catalogue, prompt, grouping, tree, placement, or review systems exist.
