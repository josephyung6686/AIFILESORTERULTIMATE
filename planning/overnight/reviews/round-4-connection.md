# Round 4 — connection

Date: 2026-08-21 (overnight)
Lens: **when P6 and P7 are built as planned, does the whole thing form one working path from a real
file on disk to a bundle, with every seam carrying what the next part needs?**
Subjects: [`../../parts/P6-facts-facets/PLAN-SKELETON.md`](../../parts/P6-facts-facets/PLAN-SKELETON.md) ·
[`../../parts/P7-privacy-consent-gate/PLAN-SKELETON.md`](../../parts/P7-privacy-consent-gate/PLAN-SKELETON.md)
Seam contract under review: [`../../22-p1-p7-connection-contract.md`](../../22-p1-p7-connection-contract.md)
Prior rounds read and **not** re-reported: [`round-1-fidelity.md`](round-1-fidelity.md) ·
[`round-2-buildability.md`](round-2-buildability.md) · [`round-3-adversarial.md`](round-3-adversarial.md)

Baseline this pass: `python3 -m pytest tests -q` → **1,241 passed in 8.09s**. Nothing in `src/` or
`tests/` was modified; two probe scripts were run from the scratchpad and never written into the
repository. Every token-absence claim below was made with `ast`, never by scanning source text.
Every "executed" claim ran against live `src/` this pass.

---

## Verdict

**P1–P7 will not join as the two plans stand, and the gap is not on the axis the plans are worried
about.** Both plans are careful about *columns* with no writer — round 1 and round 3 found several,
and P7's Task 4 models the right discipline. What neither plan checks is the converse, and that is
where the wave breaks: **four cross-part surfaces are named by a consumer and produced by no task in
any plan** — P7's `SensitivityFacts` protocol (0 mentions in 1,621 lines of P6), P8's
`contradicts(claim, existing_fact)` and `normalize(field, raw_value)` (both named in P8's Contract-in
as P6's, both refused by P6 Task 17's "P6 owns none of the checking"), and P2's `StageAdapter`, which
is the actual connector between a stage and the replay/adversarial machinery and appears in **no
SPEC at all**. One level above those: **the classification itself has no producer anywhere in the
thirteen parts.** P7's Deferred row says "the detector rule set … are hand-authored. P7 publishes the
vocabulary the detectors write into", and no part's SPEC claims the detector. So `basis = detector`
is a vocabulary member with no producer, `files.sensitivity_state` stays NULL after P7 ships, and
`Denied(unclassified)` is the universal outcome of §8.4's door.

**The one seam most likely to be broken on the day P6 lands is `FactPassNotRun`'s base class.** The
underlying cause was fixed — `_extract_one` now re-raises `ContractViolation` beside the two §4b/§5
refusals (`src/orchestrator.py:151`), and `src/extractors/failure.py:25-48` names this exact defect in
its docstring. But **`ContractViolation` appears zero times in either plan**, and P6 Task 19's
`Produces` still reads `FactPassNotRun(Exception)` (`PLAN-SKELETON.md:997`). Executed both ways this
pass, on the repo's own Wave-2 corpus fixture:

```text
FactPassNotRun(Exception)         run_wave2 RETURNED NORMALLY, bundle sealed
                                  pdf.text · native · failed
                                  "FactPassNotRunPlain: no recorded P6 pass for ea672498…"

FactPassNotRun(ContractViolation) propagated out of run_wave2 on the first text-bearing PDF
                                  no pdf.text run written at all
```

Neither is Task 26's stated acceptance test (*"running a full corpus without it firing"*). The first
is round 2's B-1 and round 3's A1, still live because the plan was not updated to the fix. The second
is new and it is the more important half: **with the correct base class, loop 1 cannot arm a raising
verdict at all**, because `ocr_policy.text_layer_state` consults `no_usable_facts` unconditionally for
every text-bearing PDF, so the first such file ends the scan. Loop 1 must be structurally unable to
reach the verdict, which is a `dispatch` change the plan says it does not make.

Everything else on the list below is closable. Nothing found this round makes a part unbuildable; it
makes the *joins* between parts unbuildable, which is a different and later kind of failure.

**One correction to round 3, in the lead's favour:** A2 (the sensitivity signal keyed to the
filesystem run's observations) is **closed**. `src/orchestrator.py:230` now sets
`signal_target = routed[0] if routed else None`, compared by identity, and
`extractors.dispatch.Dispatched.__post_init__` raises if signals ride with more than one result — so
the mis-keying is now unconstructible rather than merely fixed. P7's Task 7 story stands.

---

## The producer/consumer table across all seven parts

Built both ways: every published surface traced to a consumer, and every surface a SPEC's Contract-in
names traced to a producing task. Function surfaces resolved by `ast` import/attribute analysis over
all of `src/` and `tests/`; database columns resolved by opening a live schema and reading
`PRAGMA table_info` against every `INSERT`/`UPDATE` in `src/`.

**Legend.** `OK` — producer and consumer both exist. `PLANNED` — the consumer is a P6/P7 task and the
producer is live, or the reverse, and the seam closes when the part lands. `NO PRODUCER` — a consumer
names it and nothing produces it. `NO CONSUMER` — it is produced and nothing reads it. `BROKEN` — both
sides exist and do not fit. `UNOWNED` — no part in the thirteen claims it.

### Function and record surfaces

| # | Surface | Producer | Consumer | Status |
|---|---|---|---|---|
| 1 | `database_agent.files_table.get_file` | P1 | orchestrator, P6 T8/T14/T15, P7 T4 | OK |
| 2 | `database_agent.files_table.set_extraction_status` | P1 | orchestrator ×2 | OK |
| 3 | `database_agent.files_table.set_sensitivity_state` | **none — P1 publishes no setter** | P7 T4 (`SensitivityStateWriter`, injected) | **NO PRODUCER** — C-10 |
| 4 | `database_agent.events.append_event` | P1 | P3, P4, P5, P6 T4, P7 T1/T5/T10 | OK |
| 5 | `events` types `fact creation` / `fact rejection` | P1 `RESERVED_EVENT_TYPES` (verified present) | P6 T1 | PLANNED |
| 6 | `events` types — P7's eight | P1 `REGISTERED_EVENT_TYPES` (all eight verified, none colliding) | P7 T1 | PLANNED |
| 7 | `events` types `value creation` / `value merge` / `user fact correction` | **absent from both registries (verified)** | P6 SPEC Provenance | **NO PRODUCER** — P6 F9, interim named |
| 8 | `database_agent.supersede.mark_superseded` (+ `record_id` VIRTUAL) | P1 / P4's adapter column | P6 T4/T18, P7 T4 | PLANNED |
| 9 | `database_agent.budget.get_ceiling` / `CEILING_KEYS` (16) | P1 | P6 T20 (three keys, all verified present), P7 T13 | OK |
| 10 | `database_agent.learning.learning_records` / `reset_cutoff` | P1 | P6 T22, P7 T16 | PLANNED (`reset_cutoff` has no src consumer today) |
| 11 | `eval_harness.stage_output.record_stage_output` | P2 | **`eval_harness.replay` only** — never `run_wave2` | OK *inside P2*; see #13 |
| 12 | `eval_harness.replay.StageResult` / `ReplayContext` | P2 | P6 T21 (constructs one), P5 `extraction_stage_output` | OK |
| 13 | `eval_harness.replay.StageAdapter` — `Callable[[ReplayContext], Sequence[StageResult]]` | **no part; named in no SPEC** | `replay_bundle`, `adversarial.run_case` — the only path to a `stage_dimension_value` row | **NO PRODUCER** — C-3 |
| 14 | `eval_harness.adversarial.run_gate` / `run_case` | P2 | tests only; P6 names A01–A05, A07 as its gate | **BROKEN** — C-3 |
| 15 | `eval_harness.bundle.open_bundle` / `add_file_entry` / `seal_bundle` | P2 | orchestrator stage 4 | OK |
| 16 | `eval_harness.bundle.add_extraction_output` (`extraction_outputs`, a `BUNDLE_CONTENTS` member) | P2 | **no src call site (verified)** | **NO CONSUMER** — C-7 |
| 17 | `eval_harness.bundle.add_expectation` (`expected_facts`) | P2 | `adversarial.build_case_bundle` only | partial — C-7 |
| 18 | `eval_harness.counts.bundle_counts` | P2 | **no src call site** | NO CONSUMER (pre-existing) |
| 19 | `scan_agent.basic_record.parent_folder_context` | P3 | P6 T15 via `files.directory_position` | PLANNED (no consumer anywhere today) |
| 20 | `scan_agent.exclusion.*` protected-container surface | P3 | P7 T2 **test only**, by design | OK |
| 21 | `evidence_shape.store.observations_for_file` / `_by_key` / `_for_run` | P4 | P6 T7, P7 T9 | PLANNED |
| 22 | `evidence_shape.store.observations_for_content(file_id, content_hash)` | **not published (verified `hasattr` False)** | every per-file-version P6 read | **NO PRODUCER** — P6 F12, filter is P6 T7's |
| 23 | `evidence_shape.text_units.raw_value_at` + `store.text_unit_at` / `text_units_for_run` / `unit_for_observation` | P4 | P7 T9 (`resolve.py`, the sole locus) **and `src/orchestrator.py:42`** | **BROKEN** — round 2 B-3, still true |
| 24 | `evidence_shape.fixtures.by_number` (19 golden records) | P4 | P6 T27, P7 T20 | PLANNED |
| 25 | `extractors.dispatch.extract(..., no_usable_facts=…)` | P5 | orchestrator loop 1 and loop 3 | **BROKEN** — C-1 |
| 26 | a public targeted-OCR entry point | **none — `dispatch` publishes `extract`, `current_versions`; `_ocr` is private (`ast`)** | P6 T26 loop 3 | **NO PRODUCER** — round 2 B-2 |
| 27 | `extractors.dispatch.extract(..., transcription_authorized=…)` | P5 (zero-arg predicate) | supplied by `run_wave2`'s caller | **NO PRODUCER in the product** — C-9 |
| 28 | `extractors.long_tail.sensitivity_signals_for` / `POTENTIALLY_SENSITIVE` | P5 | P7 T3, P7 T7 | PLANNED |
| 29 | `extractors.long_tail.SENSITIVE_EMAIL_ZONES` / `SENSITIVE_EMAIL_VALUE_KINDS` / `FULLY_SENSITIVE_SOURCE_TYPES` | P5 | listed in P7's Contract-in; **no P7 task consumes them** | NO CONSUMER — C-13 |
| 30 | `extractors.failure.ContractViolation` | P5, live | **0 mentions in either plan** | **NO CONSUMER** — C-1 |
| 31 | `extractors.stage_output.extraction_stage_output` | P5 | **no src call site (verified)** | NO CONSUMER — C-7 |
| 32 | `facts.usable.no_usable_facts_for(conn, *, usable_threshold)` | P6 T19 | orchestrator T26 — but `usable_threshold` has no path in | **BROKEN** — C-4 |
| 33 | `FactResolver.resolve(conn, *, file_id, content_hash) -> ResolveResult` | P6 T20 | orchestrator T26 loops 2 and 4 | PLANNED (`ResolveResult` undefined — round 2 B-8) |
| 34 | a verdict accessor on `FactResolver` | **no task produces one** | T26: *"the orchestrator obtains it from the resolver"* | **NO PRODUCER** — C-4 |
| 35 | `facts.stage_output.fact_stage_output(*, result) -> dict` | P6 T21 | no live call site; no adapter | NO CONSUMER — C-7 |
| 36 | `facts.read_surface.*` (`facts_for`, `proposal_eligible`, `evidence_chain`, …) | P6 T24 | P9, P10, P11, P13 Contract-in | PLANNED |
| 37 | `contradicts(claim, existing_fact) -> bool` | **no P6 task** | **P8 SPEC Contract-in, ×3** | **NO PRODUCER** — C-5 |
| 38 | `normalize(field, raw_value) -> value \| not_normalizable` | **no P6 task; Deferred and injected** | **P8 SPEC Contract-in** | **NO PRODUCER** — C-5 |
| 39 | reliability total ordering (`STRENGTH_ORDER` / `is_stronger`) | P6 T1 | P8 SPEC, P7 T4 `RELIABILITY_ORDER` | OK |
| 40 | `active_field_allowlist` | P6 T13 | P6 T17, P8 (`FIELD_NOT_IN_ACTIVE_SCHEMA`) | OK |
| 41 | `handling_class(file_id) -> str` | **prose row `PLAN-SKELETON.md:433` only; no task** | P6 T20 privacy rung, `privacy_withheld` | **NO PRODUCER** — round 2 B-6; arity wrong — round 3 A9 |
| 42 | `propose(request)` / `validate(proposal, checks)` | **prose row `:434` only; no task** | P6 T17, T20 | **NO PRODUCER** — round 2 B-6 |
| 43 | `SensitivityFacts` (`current` / `write` / `supersede` / `history`) | **0 occurrences in P6's plan (verified)** | **P7 T4, T16, T17, T18 — the spine of P7** | **NO PRODUCER** — C-2 |
| 44 | `ClassificationRecord` (8 fields, incl. `protected`, `basis`) | **0 occurrences in P6's plan** | P7 T3/T4/T16/T17, P9 §4.9, P10 §5.12, P11 §6.10 | **NO PRODUCER** — C-2 |
| 45 | a **detector** that writes a classification | **no part, no SPEC (verified across all 13)** | P7's entire gate; P2's `handling_class`; P9/P10/P11/P12 | **UNOWNED** — C-2 |
| 46 | `Gate.release` → `Released \| Denied \| NeedsConsent` | P7 T11 | P8 (B2, adopted verbatim), P9, P11 | PLANNED |
| 47 | `consume_release` / `assert_single_egress` | P7 T12, T19 | P8's transport | PLANNED (L1 half-proven — round 3 A15) |
| 48 | `transcription_authorized_for(scope)` | P7 T5 | **no wiring task in either plan** | **NO CONSUMER** — C-9 |
| 49 | `members_of(group_id)` | **none; P9 unbuilt, not injected** | P7 T11 group targets | **NO PRODUCER** — round 3 A3(a) |
| 50 | `residual_template_for(file_id)` | **none; P11 unbuilt, not injected** | P7 T13 `protected_records_template` | **NO PRODUCER** — round 3 A5 |
| 51 | `consent_request_id` on `NeedsConsent` | P7 T14 adds it | P13 `review_action.subject_ref`, P8 SPEC:93 | **BROKEN** — one side only; round 1 F-11 |
| 52 | `prompt_fingerprint` | **no part computes it** | P1 `events` column, P2 `VERSION_AXES`, P6 §3.4 key, P7 binding tuple | **UNOWNED** — round 3 NJ-3 |
| 53 | `basis_key` canonical encoding | two independent serializers (P6 T22, P7 T16) | P1 stores opaquely; readers match by string equality | **BROKEN** — round 3 A13 |

### Database columns

| # | Column | Writer | Reader | Status |
|---|---|---|---|---|
| 54 | `files.extraction_status_by_tier` | orchestrator ×2 via P1's setter | P2 bundle, §8.6 progress | OK (loop 3 would erase it — round 2 B-2) |
| 55 | `files.sensitivity_state` | **none. `ast` over `src/`: two occurrences, the DDL string and `FILES_COLUMNS`** | `orchestrator` used to; now `None` | **NO PRODUCER** — still, after three rounds |
| 56 | `files.directory_position` | P3 | P6 T15 | PLANNED |
| 57 | `files.observed_timestamps` | P3 | P6 T15 | PLANNED |
| 58 | `extraction_routing.*` | `record_routing_decision`, orchestrator:253 | A10 | OK (was the third no-writer table) |
| 59 | `extraction_sensitivity_signal.*` | orchestrator:266, keyed to the routed run | P7 T3, T7 | OK — round 3 A2 closed |
| 60 | `bundle_file_entry.handling_class` | **`None`, hard-coded, `src/orchestrator.py:321`** | P2, P10, P11, P12 ("carried from P7, not re-derived") | **NO PRODUCER** — round 2 B-15, no owner in 49 tasks |
| 61 | `bundle_manifest.policy_settings` | caller-supplied; **`{}` on a live scan (executed)** | §8.5's `BUNDLE_CONTENTS` | **NO PRODUCER** — C-7; P7 OQ8 says P7 writes nothing into a bundle |
| 62 | `stage_output.*` | `replay` only; **0 rows after a live scan (executed)** | P2 assertions, attribution, adversarial | **NO PRODUCER in the live path** — C-7 |
| 63 | `bundle_expectation.*` (`expected_facts`) | `adversarial` only; **0 rows after a live scan** | P2 assertions | NO PRODUCER in the live path — C-7 |
| 64 | `file_facts.internal_score` / `cited_quote_refs[]` / `rejection_reason` | none | OQ10's third option, P8, T22 | NO PRODUCER — round 3 A16 |
| 65 | `fields.normalizer_id` | none | see #38 | NO PRODUCER — round 3 A16 |
| 66 | `fields`: `file type`, `creation date`, `language`, `sensitivity status` | none (round 1 F-2) | **P11 §7.7's literal residual dossier names `file type`, `creation date`, `sensitivity state`; P9 names `sensitivity status`** | **NO PRODUCER, named consumers** — C-11 |
| 67 | `values.display_label` / `aliases` | two homes, one unwritten | P10 (user aliases) | BROKEN — round 3 A11 |
| 68 | P6's pass-record table | T19, unnamed | T26's termination condition | NO PRODUCER — round 2 B-12 |
| 69 | `unresolved.reason = privacy_withheld` | **no task** | B7, Done-means 18 | NO PRODUCER — round 2 B-6 |

**Counted:** of 69 seams, **21 have no producer, 6 have no consumer, 6 are broken on both sides, and
2 are unowned by any of the thirteen parts.** The dominant failure mode is not a column nobody
writes — it is a *function a neighbouring SPEC names and no plan builds*, and neither
`22-p1-p7-connection-contract.md` §5 nor either plan's no-invention guard checks that direction.

---

## Findings, ranked

### C-1 (CRITICAL) — `FactPassNotRun(Exception)` is the wrong base class, and with the right one loop 1 still cannot arm it

**Seam:** P6 → P5, the `no_usable_facts` verdict. **Plan:** `P6 PLAN-SKELETON.md:997` (`Produces`),
`:1207` (loop 1), `:1222` (the test), `:1536` (*"`dispatch.py` … does not change"*).
**Substrate:** `src/extractors/failure.py:25`, `src/orchestrator.py:151`,
`src/extractors/ocr_policy.py:91-97`.

`ContractViolation`'s docstring names this exact defect and says the fix: *"Anything that is a
statement about the caller inherits this."* `FactPassNotRun` is a statement about the caller. The
plan declares it `FactPassNotRun(Exception)`, and **`ContractViolation` occurs zero times in either
plan** — so the fix and the plan have not met. Executed, both branches, output in the Verdict above.

The second half is the one that has not been said yet. With the correct base class the exception
propagates — and `text_layer_state` (`ocr_policy.py:91-97`) consults the verdict for **every**
text-bearing PDF, unconditionally, before `document_ocr_decision` can branch. So loop 1 has no way
to run `extract()` "without the OCR branch" while `dispatch.py` and `ocr_policy.py` are unchanged,
and the first text-bearing PDF in the corpus ends the scan with a `ContractViolation`. Round 2's
option table costed this as "one bad file ends the run"; what it did not say is that **it is not one
bad file, it is every ordinary PDF**, because the consult is not conditional on anything being wrong.

**Smallest fix.** Two edits, both required: (a) `FactPassNotRun` inherits
`extractors.failure.ContractViolation` — which adds a P6 → P5 import that appears in no `Interfaces`
block and must be declared; (b) loop 1 calls a `dispatch` entry point that **has no
`no_usable_facts` parameter**, so the branch is unreachable by construction rather than armed. That
is round 2's NEEDS JOSEPH 1 and it is now the only remaining shape that satisfies the plan's own
sentence, *"the extract step has to split."*

**Status:** CONFIRMED — executed both ways; `dispatch`'s public defs read by `ast`
(`['_ocr', 'extract', 'current_versions']`).

---

### C-2 (CRITICAL) — P7's spine is a P6 surface that does not exist, and the classification itself is unowned

**Seam:** P6 ↔ P7. **Plan:** `P7 PLAN-SKELETON.md:422-427` (the `SensitivityFacts` protocol),
`:649-651` (T4), `:1256` (Deferred row 1). **P7 SPEC:90.**

Counted mechanically over all 1,621 lines of P6's plan: **`SensitivityFacts` — 0. `ClassificationRecord`
— 0. `mirror_state` — 0. `SensitivityStateWriter` — 0.** `handling_class` appears twice, once in the
prose seam table and once in the OQ11 row. P7 is built on a four-method protocol
(`current`/`write`/`supersede`/`history`) it says P6 implements; twenty-seven P6 tasks produce no
method of that shape, and P6's read surface (T24) publishes `facts_for`, `proposal_eligible`,
`evidence_chain`, `history`, `unresolved_for` — none of which is `current(file_id, content_hash)`
returning a `ClassificationRecord`. Round 3's A9 established that the two plans join on a *name*;
what the connection pass adds is that on P6's side there is no name at all — not a mismatched one.

**And one level up the chain, nothing produces a classification.** P7's own Deferred row: *"The
detector rule set, its signals, and its thresholds are hand-authored. P7 publishes the vocabulary
the detectors write into."* Checked across all thirteen SPECs: **no part claims the detector.** So:
`basis = detector` is a `CLASSIFICATION_BASES` member with no producer; `Gate.release` returns
`Denied(unclassified)` for every file in a real corpus; `files.sensitivity_state` stays NULL;
`bundle_file_entry.handling_class` stays `None` even after P7 ships; and P9's, P10's, P11's and
P12's Contract-in rows — all four of which say the handling class is *carried, never re-derived* —
carry nothing. A deferral is legitimate; a deferral with **no named part to defer to** is a hole.

**Smallest fix.** (a) One P6 task publishing `SensitivityFacts` in P7's shape, or one line in P7's
plan saying P7 owns the classification table after all and P6 reads it — this is P6 OQ11 and it
cannot be settled below Joseph. (b) A named home for the detector, even if the answer is "a
fourteenth part" or "P7's caller, deferred to Wave 3" — stated in `02-segmentation-map.md`, not left
implicit in a Deferred cell.

**Status:** CONFIRMED — token counts over both plans; all thirteen SPECs searched for a detector
owner; `files.sensitivity_state` writers checked by `ast`.

---

### C-3 (HIGH) — P6 cannot reach the five adversarial cases it names as its gate

**Seam:** P6 → P2. **Plan:** `P6 PLAN-SKELETON.md:398-404` (Contract-in), `:1069` (T21 `Produces`),
`:1082` (*"`subject_ref` is the content hash"*), coverage rows 7, 9, 10, 22, 27.
**Substrate:** `src/eval_harness/adversarial.py:68-92` (`build_case_bundle`), `:114-141`
(`_stage_verdict`), `src/eval_harness/replay.py:44` (`StageAdapter`).

P6's plan claims six `dimension: fact` adversarial cases as its gate. Five of them
(A01, A02, A03, A04, A05, A07 — all `assert_against: "stage"`) pass only when a
`stage_dimension_value` row exists with `dimension = "fact"` **and `subject_ref` equal to the case's
own synthetic ref** — `A01::essay::school`, `A03::zip::course`. P2's own test shows the required
shape verbatim (`tests/eval/test_adversarial.py:100-106`):

```python
StageResult(subject_ref="A01::essay::school", outcome="abstained", …,
            values=[DimensionValue("fact", "A01::essay::school", "abstained", None)])
```

Three breaks, each independent:

1. **No adapter.** `StageAdapter` is the only thing `replay_bundle` will call, and **no P6 task
   produces one.** Counted: `StageAdapter`, `ReplayContext`, `DimensionValue` and `dimension_values`
   each occur in P6's plan *only* inside the Contract-in listing at `:398-404`; `adapters`,
   `replay_bundle` and `run_gate` occur zero times. `StageAdapter` is named in **no SPEC** — not
   P2's, not P5's, not P6's — which is why it went missing on both sides.
2. **Wrong key.** T21 fixes `subject_ref` as the content hash. A content hash is never
   `A01::essay::school`, and `_stage_verdict` matches by equality.
3. **No evidence to resolve.** `build_case_bundle` writes `extraction_runs` and `text_units` and
   **no `evidence` rows** (verified: the fixture JSONs carry no `observations` key). P6 resolves from
   P4 observations. A fact-stage adapter replaying A01 sees zero observations, abstains vacuously —
   which *passes* A01, A02, A03 and A07 (all `abstained`) while proving nothing about word-boundary
   matching, and *fails* A04 and A05 (both `produced`). Green for the wrong reason on four, red on
   two. That is §2.7's dead-path shape at the eval layer.

**Smallest fix.** A P6 task producing `fact_stage_adapter(...)  -> StageAdapter` that maps a case's
subject_ref onto the resolution it drives, plus either an `observations` block in the five fact
fixtures or a stated rule that a fact-stage adapter reads `bundle_text_unit` rows. Both are P2/P6
joint decisions and neither plan owns the fixture format.

**Status:** CONFIRMED — `adversarial.py` read in full; all twelve fixtures parsed; token counts over
P6's plan; P2's own adapter test read.

---

### C-4 (HIGH) — Task 26 adds one parameter and needs two values, and `FactResolver` publishes no verdict

**Seam:** P6 → the Wave-2 caller. **Plan:** `:993` (T19 `Produces`), `:1042-1047` (T20 `Produces`),
`:1194-1197` (T26 `Produces`).

T26 removes `run_wave2`'s `no_usable_facts` and adds *"one new keyword-only parameter carrying P6's
resolver … the orchestrator obtains it from the resolver, because handing the caller a verdict
function and a resolver separately is what let them drift apart."* The reasoning is right. The
mechanism does not exist:

- T20's `FactResolver` produces `resolve(...)` and `deferred_counts(...)` and **no verdict
  accessor.** There is nothing on the resolver for the orchestrator to obtain.
- T26 also consumes `facts.usable.no_usable_facts_for` directly — but its signature is
  `no_usable_facts_for(conn, *, usable_threshold)`, and `usable_threshold` is *"a required keyword
  with no default"* (`:1003`, and the Deferred table's own row). **`usable_threshold` occurs exactly
  once in 1,621 lines**, in T19's `Produces`. `run_wave2` gains one parameter, not two, so the
  threshold has no path from the caller into the orchestrator — and giving it a default is the one
  thing Task 25's guard forbids.

**Smallest fix.** Add `FactResolver.no_usable_facts` (or `.verdict`) to T20's `Produces`, constructed
from the same injected threshold the resolver already takes, and say in T26 that the orchestrator
reads it from there. One line in each task, and it makes T26's own argument true.

**Status:** CONFIRMED — both `Produces` blocks read; `usable_threshold` counted across the plan.

---

### C-5 (HIGH) — P8's Contract-in names two P6 functions, and P6 Task 17 says P6 owns neither

**Seam:** P6 ↔ P8. **P8 SPEC**, *From P6 — facts and facets (§3.1–3.14)*, verbatim:

> - A normalizer: `normalize(field, raw_value) -> value | not_normalizable` (§3.6), including the
>   gazetteer and word-boundary discipline (§3.7).
> - A contradiction oracle: `contradicts(claim, existing_fact) -> bool`.

**P6's plan**, Task 17 (`:958-960`): *"P6 supplies the four inputs and owns none of the checking:
`apply_verdict` takes a `Verdict` it did not compute, so P8 can be built against this shape."*

Counted: `contradicts` appears once in P6's plan — inside the D4 discussion of §3.3-vs-§3.6 — and in
no `Produces` block. `normalize(` and `not_normalizable` appear zero times in P6's plan and zero
times in P6's SPEC; `normalizers` appears only as an unshaped field on `FactRequest` and as a
Deferred, injected row.

So both parts hand the same two functions to the other. The consequence is concrete: P6's
`UNRESOLVED_REASONS` carries `contradicted_by_stronger_fact` and `normalization_failed`, written
from a `Verdict` P8 produced using an oracle and a normalizer P8 expects from P6. **Neither part
builds either, and both parts' tests pass, because each side hand-authors the `Verdict`.** This is
round 3's A8 one level up: not "the reason is unreachable in the shipping configuration" but "the
reason is unreachable in *any* configuration, because the check has no author."

**Smallest fix.** P6 T17 gains `contradicts(claim, existing_fact) -> bool` in its `Produces` — it
already owns `is_stronger` and `facts_for_file`, which is everything the oracle needs — and states
that the normalizer is P6's injected per-field map surfaced to P8 under the name P8's SPEC uses. Or
P8's Contract-in loses both rows and gains them in P8's own Produces. Either is a one-line decision;
what cannot stand is both SPECs pointing at each other.

**Status:** CONFIRMED — P8's SPEC block read in full; token counts over P6's plan and SPEC.

---

### C-6 (MEDIUM-HIGH) — §3.4's cache key is scalar and a fact's evidence is not, so "pass 4 is a different key" has no stated rule

**Seam:** P4/P5 → P6, and it is the hinge of the four-pass restructure. **Plan:** `:669-671`
(T6 `Produces`), `:1226-1228` (T26: *"the two cache keys differ by `analysis_tier` alone"*),
`:200-205` (preamble rule 5).

`fact_cache_key(*, content_hash: str, extractor_version: str, analysis_tier: str, model_identifier,
prompt_fingerprint)` takes **one** extractor version and **one** analysis tier. A P6 fact carries
`evidence_refs[]` — plural — and there is no rule anywhere that they come from one run.

Executed against the repo's own Wave-2 corpus fixture, the observations for the skeleton PDF:

```text
'syllabus.pdf'                  filesystem.record  v0.1.0  tier=filesystem
'.pdf'                          filesystem.record  v0.1.0  tier=filesystem
'application/pdf'               filesystem.record  v0.1.0  tier=filesystem
'BUSIB 4300 Syllabus'           pdf.text           v0.1.0  tier=native
'BUSIB 4300 Course Information' pdf.text           v0.1.0  tier=native
```

Done-means 4's three facts (`Syllabus BUSIB 4300 Spring 2026.pdf` → filename, PDF title, page-one
heading) draw on **both** extractors at **two** tiers. Which `extractor_version` and which
`analysis_tier` go in the key is unstated, and it decides:

- whether a pass-4 fact is a different key from its pass-2 predecessor (T26's supersession test), and
- whether Done-means 15's *"a bumped extractor version supersedes"* means "any cited extractor" or
  "one named one".

P5 hit exactly this and solved it differently — `extractors.stage_output.extractor_versions(runs)`
returns a **map** and *raises* if one extractor appears at two versions. P6's key has one slot.

**Smallest fix.** T6 states the rule in one sentence: the key's `analysis_tier` is the **highest**
tier among the cited observations' runs (`filesystem < native < ocr < llm`), and `extractor_version`
is a canonical digest of the `{extractor_name: version}` map over those runs — which keeps
`sha256_of`'s injectivity and makes a bump in *any* cited extractor invalidate the fact. Whatever is
chosen, T26's supersession assertion is unwritable until it is.

**Status:** CONFIRMED — executed; T6's signature read; P5's comparator read.

---

### C-7 (MEDIUM) — the bundle stays a Wave-2 artifact, and neither plan changes that

**Seam:** everything → P2. Executed after a live `run_wave2` on the two-file corpus:

```text
stage_output rows              0
bundle_expectation rows        0
bundle_extraction_output rows  0
bundle_manifest.policy_settings '{}'
bundle_file_entry.handling_class None, None
files.sensitivity_state        None, None
```

`BUNDLE_CONTENTS` names eight things. A live scan writes three of them (`corpus`,
`content_hashes`, and `policy_settings` as an empty object). §8.5's per-stage output has **never**
been produced outside a replay adapter — `record_stage_output` is called only from
`eval_harness/replay.py`, and `extraction_stage_output` has no `src` call site at all. `graphify path
"run_wave2" "record_stage_output"` returns no call edge, only a shared-import detour through
`canonical_json`.

Once P6 and P7 land, this does not change. P6 T21 produces a dict with no caller and no adapter
(C-3). P7's OQ8 says *"P7 writes nothing into a bundle; `open_bundle`'s `policy_settings` slot is the
only surface it touches"* — and no P7 task supplies a value for that slot, so it stays `{}`. §8.5's
requirement that evaluation be *decomposed by stage* is the reason `02` put P2 first; after seven
parts the live pipeline still emits zero stage rows.

**Smallest fix.** One sentence in each plan naming who calls the stage-output writer in the live
path — the honest answer is that `run_wave2` should record the extraction and fact envelopes as it
writes them, which is a T26 addition — and one line in P7 T5 or T22 giving `run_wave2` its
`policy_settings` from `Gate.display_policy()` / `current_policy`.

**Status:** CONFIRMED — executed; `ast` over all call sites; `graphify path`.

---

### C-8 (MEDIUM) — `02`'s three back-edges are actually nine, and two of the new ones have no fixture

**Seam:** the wave order. `02-segmentation-map.md` names three acknowledged back-edges (P5→P7,
P8→P10, P8→P11) and says they are *"mediated by fixtures rather than re-ordered."* The brief names
P6→P5 as a fourth. Traced across both plans, the full list is:

| Back-edge | Wave order | Mediation in the plans | In `02`? |
|---|---|---|---|
| P5 → P7 (`transcription_authorized`) | 2 ← 3 | P7 T5 adapter, **no wiring task** (C-9) | yes |
| P6 → P5 (`no_usable_facts`) | 2 ← 2 | T19/T26 — the four passes | **no** |
| **P6 → P7** (`handling_class`) | 2 ← 3 | injected, prose only, no task (`:433`) | **no** |
| **P6 → P8** (`propose`/`validate`) | 2 ← 3 | injected, prose only, no task (`:434`) | **no** |
| **P7 → P6** (`SensitivityFacts`) | 3 ← 2 | `tests/p7/p6_fixture.py` — **the only one properly fixtured** | **no** |
| **P7 → P9** (`members_of`) | 3 ← 4 | none — round 3 A3(a) | **no** |
| **P7 → P11** (`residual_template_for`) | 3 ← 5 | none — round 3 A5 | **no** |
| **P7 → P13** (`consent_request_id`) | 3 ← 5 | name adopted, shape changed on one side (round 1 F-11) | **no** |
| P8 → P10, P8 → P11 | 3 ← 4/5 | fixtures | yes |

P6 → P7 and P7 → P6 together are a **cycle**, and the only thing that breaks it today is that P7
built a fixture and P6 did not. That is the structural statement of C-2.

**Smallest fix.** `02`'s back-edge paragraph gains the six missing edges, and each one names its
fixture. The two with none (P7→P9, P7→P11) are round 3's findings and their fix is the same
injected-callable-with-no-default pattern P7 already uses four times.

**Status:** CONFIRMED — every `Consumes` block in both plans resolved to an owning part.

---

### C-9 (MEDIUM) — the P5→P7 back-edge has a producer, a consumer, and no wiring

`extractors.dispatch.extract` takes `transcription_authorized: Callable[[], bool]`, threaded from
`run_wave2`'s parameter of the same name, called at `src/extractors/long_tail.py:204`. The only
caller of `run_wave2` is `tests/wave2/`, which passes `lambda: False`. P7 T5 produces
`transcription_authorized_for(scope) -> Callable[[], bool]` (`P7 :677`) and P7's Contract-out row
(`:486`) names P5 as the consumer.

**No task in either plan connects them.** P7 modifies no file another part owns; P6 T26 owns
`src/orchestrator.py` and its `Produces` mentions only the resolver parameter. So M10's back-edge
ships as a function with no caller, and §2.9's speech-to-text authorization remains `lambda: False`
in the one place it is wired.

**Smallest fix.** One line in P6 T26 (which already owns the file) or an explicit statement in P7
that the wiring is deferred to the part that owns the caller, naming it.

**Status:** CONFIRMED — call chain read; `run_wave2` callers enumerated by `ast`.

---

### C-10 (MEDIUM) — `SensitivityStateWriter` needs a P1 setter that no task in any plan adds

P7 T4 injects `SensitivityStateWriter.set_sensitivity_state(conn, file_id, *, state, author,
component_version)` *"because P1 publishes no such writer"*, and reports the gap. Confirmed by
`ast`: the only occurrences of `sensitivity_state` in all of `src/` are the `FILES_DDL` string and
the `FILES_COLUMNS` tuple. The precedent P7 cites is exact — P5 reported the same about
`extraction_status_by_tier` and **P1 then shipped `set_extraction_status`**, which is why column 54
works today. The difference is that no one is holding the P1-side task this time: P1 is finished,
P6 does not touch `database_agent`, and P7 forbids itself from doing so.

**Smallest fix.** Name it. Either a P1 addendum task (`set_sensitivity_state`, the exact shape of
`set_extraction_status`, storing the value opaquely as P1 already does for the tier map), or a line
in P7 T4 saying the mirror does not ship in Wave 3 and `files.sensitivity_state` stays NULL — which
is honest and makes the standing rule in the connection contract §3 true rather than aspirational.

**Status:** CONFIRMED — `ast`.

---

### C-11 (MEDIUM) — round 1's four unwritten universal fields have named downstream consumers

Round 1 F-2 found that `file type`, `creation date`, `language` and `sensitivity status` are created
by P6 T2 with no producer. What the connection pass adds: three of the four are named **literally**
in a downstream SPEC's Contract-in.

**P11 SPEC, residual dossier contents (§7.7, marked *literal*):** *"filename, file type, creation
date, extracted text or OCR, metadata, sensitivity state, any weak graph relationships…"*
**P9 SPEC, From P6:** *"Universal facts including duplicate family, version family and sensitivity
status (§3.11) supply the duplicate/version retrieval channel (§4.2)."*

So these are not spare columns that can wait for a later part to fill. They are fields two later
parts will read on day one, and P11's §7.7 list is the one the design states verbatim. `duplicate
family` and `version family` have producers (T14); the other three do not.

**Smallest fix.** As round 1 said — name the producing task, or put the row in Deferred and say
plainly that P6 publishes the field and does not write it. The addition here is that the Deferred row
must name **P11 §7.7 and P9 §4.2 as the blocked consumers**, so the cost of leaving it is visible.

**Status:** CONFIRMED — both SPEC blocks read.

---

### C-12 (LOW) — P9's Contract-in already assumes OQ3's answer

**P9 SPEC, From P6:** *"The `purpose` facet (§3.9) is a first-class input to §4.7."* P6 OQ3 asks
whether `purpose` is universal or Applications-scoped, and T2 builds §3.11's rows verbatim, which
scopes it to College applications (round 1 F-4). A domain-scoped `purpose` is not "first-class" and
is absent from every file outside one domain. Holding OQ3 open is right; the cost is that a
downstream Contract-in is already written against one answer.

**Status:** CONFIRMED.

---

### C-13 (LOW) — P7's Contract-in lists three P5 constants no P7 task consumes

`SENSITIVE_EMAIL_ZONES`, `SENSITIVE_EMAIL_VALUE_KINDS` and `FULLY_SENSITIVE_SOURCE_TYPES` appear in
P7's *What P7 consumes from P5* block (`:427-431`) and in no task's `Consumes`. All three are
`NO CONSUMER ANYWHERE` in the live repo. They are the only per-value inputs that would let T7 decide
§8.4's *"raw sensitive values"* by zone and kind rather than by signal row alone. Either T3/T7 name
them, or the Contract-in block drops them.

**Status:** CONFIRMED — `ast` over `src/` and `tests/`; every P7 `Consumes` block read.

---

### C-14 (LOW) — the walking skeleton is five independent tests, and the plans add two more of the same shape

`02` describes *"One file, one deterministic path, every seam touched."* What exists is five separate
tests — `tests/test_skeleton_p1_step.py`, `tests/eval/test_skeleton_p2_step.py`,
`tests/p3/test_p3_skeleton_step.py`, `tests/p4/test_p4_skeleton_step.py`,
`tests/p5/test_p5_skeleton_step.py` — each of which calls `create_schema` on its own connection,
writes its own fixture file, asserts its own step and hands nothing to the next. The P2 step builds
its own bundle by hand rather than replaying one a scan produced.

The plans add `tests/p6/test_p6_skeleton_step.py` (T27, driven from `by_number(1)`) and
`tests/p7/test_p7_skeleton_step.py` (T22). Both follow the same pattern, so after P6 and P7 the
skeleton is **seven independent step tests, not a path**. P7's is the only one of the seven that
touches the live pipeline (it consumes `run_wave2`); P6's does not, which means P6's skeleton step
would not exercise the four-pass wiring it depends on — `test_p6_pass_order.py` carries that
separately.

The one test that *does* chain P3 → P5 → P4 → P1 → P2 is `tests/wave2/test_wave2_orchestrator.py`,
which `02` does not name as the skeleton and which P6 T26 rewrites (round 2 B-14).

**So: the plans add the P6 and P7 steps, and the skeleton would not then run end to end — it does not
today either.** P6 and P7 do not regress it; they also do not close it, and the ten-step claim in
`02` should either be reconciled with the wave-2 harness or stated as ten independent step tests.

**Status:** CONFIRMED — all five files read.

---

## Corrections to `22-p1-p7-connection-contract.md`

It was written before rounds 1–3 and before the `ContractViolation` fix. Seven things are now wrong
or incomplete.

**1. §2 — "The three refusals" is now four, and the fourth is the one P6 depends on.**
`extractors.failure.ContractViolation` (shipped since) is a refusal with different semantics from all
three: it is *about the call, never about the file*, it **always propagates**, it writes nothing at
all, and it ends the scan. Its own docstring says so. §2's table is the document P6's Task 19 author
will read to decide `FactPassNotRun`'s base class, and it does not mention it. Add a fourth row, and
add the consequence: **P7 Task 21 asserts `src/privacy/` imports neither `ProtectedContainerRefused`
nor `DatalessRefused` — that list is now three names.**

**2. §1's table is missing every seam that broke this round.** It has nine rows and none of them is
P6 ↔ P7, P6 → P8, P6 → P2's adapter, or P7 → P6. Those four are where the wave actually fails. The
table's own framing — *"Every surface below was checked by import and signature"* — is the reason:
it only lists surfaces that **exist**, and every failure this round is a surface that does not.

**3. §1, row "P7 → P2 | `bundle_file_entry.handling_class`" is mis-attributed.** P7 never reaches the
bundle — P7's own OQ8 says so. The producer is `src/orchestrator.py`'s stage 4, the value is a
hard-coded `None` at line **321** (not 259 or 285 — it has moved twice more), and **no task in either
plan gives it a value.** The row should say "producer: the Wave-2 caller; owner: none."

**4. §1, row "P6 → P5 | `no_usable_facts` … signature matches" needs the base-class clause.** The
signature does match. What does not is the exception type, which is now the thing that decides
whether the seam works — see C-1. Add: *"and the exception a too-early consult raises must inherit
`extractors.failure.ContractViolation`, or `_extract_one` records it as the file's `failed` run."*

**5. §3 undercounts the homes by one and misses the real gap.** It says three homes
(`sensitivity status` / `sensitivity_state` / `handling_class`). There are **four**: P7's
`ClassificationRecord` carries `handling_class` *and* a separate `protected` flag, and P7 SPEC §2
says neighbours must consume the flag and *"not infer it from the class."* More importantly, §3
frames the problem as *which record is authoritative*. The connection pass says the sharper form:
**none of the four has a producer.** Deciding which record wins does not, by itself, make anything
write one.

**6. §4's inference is right and its arithmetic is one short.** It says *"three passes rather than
one loop"* and then describes four. P6's preamble rule 5 gets this right. Fix the count, and add the
caveat C-6 raises: *"a second P6 pass, which the SPEC implies … because the new run changes the §3.4
cache key"* is only true if the key can name a single `analysis_tier`, and a fact whose evidence
spans a filesystem run and a native run cannot.

**7. §5 and §6 check one direction only, and the failures are on the other.** §5's standing rule —
*"Any part added from here must carry a check that every column it publishes has a writer"* — is the
right rule and neither plan carries it (round 1 F-2, round 2 missing-task 7, round 3 A16). But of the
69 seams in the table above, **21 fail the converse**: a consumer names a surface and no plan
produces it. §6's check 2 (*"Every published column has a writer, or a named part that will write
it"*) covers columns; nothing covers functions, and `SensitivityFacts`, `contradicts`, `normalize`
and `StageAdapter` are all functions.

Two further amendments to §6's six checks:

- **Check 3** (*"`no_usable_facts` is never consulted before P6's deterministic pass"*) is not
  mechanically checkable through `run_wave2` as Task 26 builds it — see C-1. Restate it as a property
  of `dispatch`'s published surface: *"the entry point loop 1 calls has no `no_usable_facts`
  parameter."*
- **Check 4** (*"No content reaches a model before P7's classification"*) is currently **vacuous in
  the safe direction**: no part produces a classification, so no content is releasable at all. Add:
  *"and a classification exists for every file in the corpus"*, which is the assertion that would
  have surfaced C-2.

**Add a check 7:** *"Every surface a SPEC's Contract-in names has a producing task in some plan."*
That single check catches C-2, C-3, C-5, C-9 and C-13 mechanically.

---

## The four-pass verdict

**Do the passes connect as specified? No — two of the four joins are unbuildable and the fourth's
identity rule is unstated. The shape is right; every mechanism that implements it is wrong.**

| Pass | What it does | Does it connect? |
|---|---|---|
| **1** — native extraction | route → `extract()` **without the OCR branch** → `_write` → `set_extraction_status` | **NO.** `ocr_policy.text_layer_state` consults the verdict unconditionally for every text-bearing PDF, and `dispatch` publishes no entry point without the parameter. `FactPassNotRun(Exception)` → a `failed` run per PDF, silently; `FactPassNotRun(ContractViolation)` → the scan ends on the first one. **Both executed.** (C-1) |
| **2** — deterministic resolution | reads the P4 `evidence` rows loop 1 wrote; writes facts / `unresolved`; `record_pass` | **YES, on the read side.** Verified: `RunWriter.write` records the run, its text units and every observation inside one transaction, so `observations_for_version(conn, file_id, content_hash)` returns them the moment loop 1's `_write` returns. This is the one join in the restructure that is sound as written. It needs `usable_threshold` to reach the orchestrator (C-4) and a `content_hash` filter P4 does not publish (P6 F12, table row 22). |
| **3** — targeted OCR | for files where the verdict is true: OCR → `_write` → `set_extraction_status` | **NO.** No public OCR-only entry point (`ast`: `dispatch` exports `extract`, `current_versions`; `_ocr` is private), re-entering `extract()` duplicates the native run, and `set_extraction_status` is a full `UPDATE files SET extraction_status_by_tier = ?` that erases loop 1's map. All three are round 2's B-2 and all three are still true against the current file. |
| **4** — re-resolution | resolves again over native + OCR evidence; facts supersede | **READS FINE, WRITES AMBIGUOUSLY.** The evidence is all in the store, so pass 4 can read it. Whether it produces a *different* §3.4 key is unstated: the key takes one `analysis_tier` and one `extractor_version`, and a pass-4 fact's `evidence_refs[]` span a filesystem run, a native run and an OCR run. Executed on the skeleton PDF — its observations already span `filesystem.record/filesystem v0.1.0` and `pdf.text/native v0.1.0` before OCR enters. **"The two cache keys differ by `analysis_tier` alone" is not derivable from the code.** (C-6) |

**Termination.** T26 reads it from `passes_for(...) -> tuple[frozenset[str], ...]`, whose ordering is
unstated and whose consumer needs one (round 3 A12(a)). Not re-argued.

**What is right and should survive any rewrite.** The diagnosis in preamble rule 5 — *"at the consult
point the evidence does not exist yet"* — is correct and is the sharpest statement of the defect
anyone has written. The pass-record-as-a-row instrument is the right instrument. The blast-radius
analysis (PDF branch only, text-bearing only) matches the code exactly. It is the diff, still, that
does not exist.

---

## NEEDS JOSEPH

Verbatim and unresolved. Rounds 1–3's items are not repeated; these are what the connection lens
adds.

**1. Which part runs the sensitivity detector?** P7 SPEC *Deferred*: *"The design states **what** is
protected and never **how** it is recognised. The detector rule set, its signals, and its thresholds
are hand-authored. P7 publishes the vocabulary the detectors write into."* No part in
`02-segmentation-map.md`'s thirteen claims it, and no SPEC names a detector owner. Until one does:
`basis = detector` has no producer, `Gate.release` returns `Denied(unclassified)` for every real
file, `files.sensitivity_state` stays NULL, and P9's, P10's, P11's and P12's *"carried from P7, not
re-derived"* rows carry nothing. **A deferral needs a part to be deferred to.** (C-2)

**2. Does `FactPassNotRun` inherit `extractors.failure.ContractViolation`?** Its docstring says
*"Anything that is a statement about the caller inherits this."* Inheriting makes the ordering error
propagate — and ends the scan on the first text-bearing PDF, because loop 1 cannot avoid consulting
the verdict while `dispatch` publishes one entry point. Not inheriting makes it
`pdf.text · native · failed` for every text-bearing PDF, silently, which is the defect the class was
added to prevent. **Both were executed this pass and neither is acceptable**, so the answer is
bound to round 2's NEEDS JOSEPH 1: `dispatch` gains a native-only entry point and a targeted-OCR
entry point, and `FactPassNotRun` inherits `ContractViolation` as a guard that can then never fire.
**Recommendation: do both.** (C-1)

**3. Who owns the `contradicts` oracle and the `normalize` function?** P8's SPEC lists both under
*From P6*; P6's Task 17 says *"P6 supplies the four inputs and owns none of the checking."* Neither
plan builds either, and both parts' tests pass because each hand-authors the `Verdict`. Two of P6's
thirteen `unresolved` reasons — `contradicted_by_stronger_fact` and `normalization_failed` — are
written from a check nobody wrote. (C-5)

**4. Who authors a `StageAdapter`, and does a §8.5 stage output exist outside a replay?** The adapter
is the only connector between a stage and P2's replay and adversarial machinery, and it is named in
**no SPEC**. Today a live scan writes **zero** `stage_output` rows (executed). P5's envelope has no
call site and P6's would have none either. Either every stage publishes an adapter as part of its
Contract-out, or `run_wave2` records the envelopes as it writes the runs — and the second is the only
one that makes §8.5's per-stage measurement true of the product rather than of the harness. (C-3, C-7)

**5. What single `analysis_tier` and `extractor_version` does a multi-run fact carry in §3.4's cache
key?** §3.4: *"content hash, extractor version, analysis tier, model identifier when relevant, and
prompt fingerprint."* The design assumes one of each. A fact citing a filename observation and a
page-one heading already spans two extractors at two tiers before OCR exists — executed. This decides
whether pass 4 supersedes pass 2 or collides with it. (C-6)

---

## What this round did not look at

Scope and simplification (round 5). Where a finding here overlaps a prior round it is marked as such
and not re-argued: round 2's B-1/B-2/B-6/B-8/B-12/B-15 and round 3's A3/A5/A9/A12/A13/A15/A16 are
cited as still-true rather than restated. Round 3's **A2 is closed** and is reported as closed above.
Two of round 5's likely subjects are visible from here and are left for it: whether P6's twenty-seven
tasks and P7's twenty-two are the right cut once the missing seam tasks are added, and whether the
four-pass restructure should ship in Wave 2 at all given that its loops 3 and 4 do nothing until an
OCR engine is chosen (P5's NEEDS JOSEPH 1).
