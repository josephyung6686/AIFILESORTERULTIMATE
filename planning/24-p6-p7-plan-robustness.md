# P6 and P7 plan robustness

> ## SUPERSEDED 2026-08-22 — read `26-handoff.md` and `parts/_PLAN-AUTHORING-BRIEF.md` first
>
> **This file is evidence from 2026-08-21 and is stale on its three headline blockers.** It is kept
> because its method and its unresolved findings are still good; do not act on its Status line.
>
> | This file says | Now |
> |---|---|
> | "Task 26 implements a four-pass caller that cannot land against live `dispatch`" | **Task 26 is CUT** (D5 / round 5 CUT 1). Nothing rewires `src/orchestrator.py`. |
> | "Task 2 implements a closed field list the design never closed" | Written against `planning/domains/canonical_fields.json` (37 keys) as a **source to read**, never a runtime import. D1/D6/D8/D9 have since settled its contested rows. |
> | "P6 seam **injected**" / missing `SensitivityFacts` | **D2 + D7.** P7 owns a concrete `ClassificationStore` in `src/privacy/classification_store.py`. No injected protocol, no `SensitivityFacts`, and P6 keeps **no** `sensitivity_status` row. |
> | "**1244 passed**" | **1302 passed** (2026-08-22). |
> | "skeletons, not freeze-ready PLANs" | P6 is **26/26 tasks written**, P7 **22/22** — complete TDD packages, ~43k lines. Assembly into two `PLAN.md` files is the open job. |
>
> **What this file got right and is still true:** P7 is a shape-correct gate with **no classifier
> behind it** — there is still no detector, so on a real corpus every file resolves to
> `Denied(unclassified)`. That remains the honest state and is deliberately not papered over.

Date: 2026-08-21
Status: **do not execute as a stack.** The skeletons are honest about mechanism and dishonest about join. P7 is a shape-correct gate with no classifier behind it. P6 Task 2 implements a closed field list the design never closed, and Task 26 implements a four-pass caller that cannot land against live `dispatch`.
Scope: live P6 `PLAN-SKELETON.md` (27 tasks) and P7 `PLAN-SKELETON.md` (22 tasks) against live SPECs, shipped `src/` (P1–P5 + Wave-2 caller), [`00-database-agent-product-design.md`](00-database-agent-product-design.md), [`04-resolutions.md`](04-resolutions.md), [`02-segmentation-map.md`](02-segmentation-map.md), [`22-p1-p7-connection-contract.md`](22-p1-p7-connection-contract.md), overnight council [`DECISION-BRIEF.md`](overnight/council/DECISION-BRIEF.md). Substrate this pass: [`23-full-tree-stress.md`](23-full-tree-stress.md) — **1244 passed**. Neither skeleton was updated after that file, nor after rounds 4–5.
Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md)

These are **skeletons, not freeze-ready PLANs.** P4 and P5 were judged as complete TDD packages. P6 and P7 still need every task filled with complete test code and complete implementation code. A skeleton that cannot be executed as written is still the right thing to refuse, because filling it in would ship the same lies at 9,000 lines.

Prior overnight rounds 1–5 are treated as evidence, then re-checked against live plan text and live `src/` rather than trusted as current. Three of their blocking findings are still in the skeletons unchanged.

---

## Verdict

| | P6 facts and facets | P7 privacy and consent gate |
|---|---|---|
| What it actually is | Four tables, six reliability states, injected producers, `unresolved` as a row, a four-pass caller rewrite. Stdlib. No model. No gazetteer. | `src/privacy/`: five classes, four modes, unforgeable `Released`, audit-as-`events`+JSON, P6 seam **injected**. Stdlib. No detector. |
| Against `00` | Mechanism is faithful (§3.1–3.14). Catalogue is not. `00` says academic files **may use** those fields; Task 2 forbids every field outside a ~37-row list, including §3.8's `authored_by` that Done-means 13 and 22 require. Done-means 4 answers OQ4 as `course` while `00` says `subject = BUSIB 4300` three times. | Gate shape is faithful (§8.4: before any model, local-first, always-local nine, four consent options, audit six, retraction-limit `must`). SPEC adds a sixth releasable kind (`filename`) the design does not name. I6 (`delete local derived data` vs append-only) is correctly refused, not guessed. |
| Against binding resolutions | Task 2 hardens **S3** (*Career/recruiting **deferred***) into *acquiring a career field **fails the test***. Deferral is not prohibition. | Eight event types already sit in P1's frozen `_REGISTERED`. Matches B5 / registration-is-a-spec-act. |
| Against shipped P1–P5 | Consumption is written against live signatures, not P1 PLAN.md. Production of what P7 and the caller need is missing. Task 26 says `dispatch.py` does not change; live `document_ocr_decision` consults `no_usable_facts` on every text-bearing PDF, so that sentence is the defect. | Reads P4 locators, P5 `sensitivity_signals_for`, P1 `append_event` correctly. `SensitivityFacts` has **zero** mentions in P6's 1,621 lines. `files.sensitivity_state` still has no writer. `handling_class` is hardcoded `None` at `orchestrator.py:321`, and no task in either skeleton owns that line. |
| Execute? | **No** as written. Tasks 1, 3–18, 20–25, 27 are fillable after D6/D2/D1 land in Task 2. Task 19's base class and Task 26's "dispatch unchanged" must be rewritten first. | **Yes for Tasks 1–21 against the P6 fixture**, after finding 2 (producer of a classification) is named, not after it is built. **No for Task 15** until I6. **No for Task 22** as a second owner of `run_wave2`. |

A later part can be built against P7's fixtures with no gate present — that is the point of the split, and P7 honours it. What they do not honour is *one* identity of sensitivity across four homes, *one* producer of a classification, and *one* owner of the Wave-2 caller.

---

## What is actually good

Do not re-open these. They are the reason the skeletons are worth editing rather than discarding.

- Shape precedes extractors, facts precede models, the gate precedes transport. `02` Wave 2 is P4→P5→P6 (deterministic); Wave 3 is P7→P8. The skeletons keep that order and inject the missing neighbour.
- Closed vocabularies, fail-not-coerce. P6 imports P4's six reliability states by identity, not a second spelling. P7 pins five `protected*` strings so they cannot collapse.
- No invented thresholds, gazetteers, regex catalogues, identifier classes, or install-default mode. Injected, no default. Task 25 / Task 21 hold open questions by runtime introspection, not `read_text()`.
- P6 never writes an observation. P4's `evidence_never_overwritten` / `evidence_no_delete` triggers make that unfalsifiable.
- `unresolved` is a row, not an absent fact. B7 and §8.5's "did it abstain?" are met. `budget_deferred` / `privacy_withheld` are not abstentions; P2's writer already enforces that pairing.
- P7's three refusals are distinguished: protected container produces nothing, dataless produces one run, the gate produces an audit. `src/privacy/` imports neither P3/P5 refusal. C4 holds: the gate writes the audit and nothing else.
- L1 (unforgeable single-use `release_id`) is provable inside P7. L2 (one materialiser module) is written now so P8 cannot invent a second. L3 honestly says it is P8's.
- Live P1 surfaces were introspected, not reconstructed: sixteen `CEILING_KEYS` including `evidence.context_window`; P7's eight event types already registered; `append_event` has no audit columns so explanation-JSON is the only jointly-satisfiable home; `learning_records` filters on scope/subject only, so P6 T22 and P7 T16 filter in the acting part.
- P5's `extraction_sensitivity_signal` is now actually written (file 23 closed the drop). P7 T3/T7 consume a live table, not a discarded `Dispatched.sensitivity`.
- Both skeletons report their own SPEC-vs-design divergences instead of smoothing them. P6 F2/F3/F4 and P7's `filename` / "verbatim" catch are correct against `00`.
- Graphify is still unpaid. Same standing hole as every prior robustness pass. Named, not a reason to refuse these two.

---

## The blockers

Same defect class as P3 Task 3 and P4 OQ2: a plan that is internally consistent and implements a **superseded or still-open decision**.

### 1. P6 Task 2 closes a list `00` left open, and forbids a field two Done-means require — **blocking P6 Task 2, and therefore everything that stores a `field_key`**

`00` on domain fields: *"Academic files **may use** school, term, course, instructor, and work type."* Hedged, six times. `01` rendered that as a `Fields` column and the modal disappeared. P6 SPEC Done-means 2 then forbade everything outside ~37 rows.

§3.8, which P6 owns, names `authored_by`, `target_school`, `our_firm`, `client` outright. None is in any §3.11 sentence. Done-means 13 and 22 require `authored_by`. Task 2: *"Career and recruiting, identity, medical and legal have no field rows and acquiring one fails the test (S3)."*

S3 is binding and says **deferred**, not forbidden. Task 2 is the P3-Task-3 shape again: internally typed, implements the wrong reading of a settled decision.

Separately, Done-means 4 requires `course`; `00` §3.1 / §3.2 / §3.12 say `subject`. OQ4 is listed OPEN in the same document. Done-means 5 requires `capture date`; Done-means 2's list has `creation date` and `capture year`. Four of seven universal fields Task 2 creates (`file type`, `creation date`, `language`, `sensitivity status`) have no producing task.

Overnight D6 + D1 are the sentences that close this. They are recommendations. They are not in the skeleton. **Do not fill Task 2 until they are.** `field_key` is a stored join key under §8.2. This is a one-way door.

**Fix:** strike the S3 hardening. Load §3.8's four. Pick one spelling (`subject` or `course`) and one key convention in the SPEC first, then Task 2. Name a producer for each universal field or put the row in Deferred with the blocked consumer (P9, P11 §7.7).

### 2. P6 does not publish the surface P7 is built on — **blocking P7 Tasks 4, 16, 17, 18 as a join, and every later "carried from P7" row**

P7 Task 4: injected `SensitivityFacts` protocol (`current` / `write` / `supersede` / `history`), reconstructed from P6's SPEC, swap when P6 ships.

P6 PLAN-SKELETON, counted this pass: `SensitivityFacts` **0** · `ClassificationRecord` **0** · `mirror_state` **0** · `SensitivityStateWriter` **0**. P6 OQ11 is held open by Task 25, which is correct as a *question* and means P6 publishes **no method of the shape P7 calls**.

This is the largest connection risk in the wave, and it is not new: `22` §3, round 4 C-2, council D2. Live state re-checked:

- `files.sensitivity_state` exists (`db.py` DDL, `FILES_COLUMNS`). `set_sensitivity_state` does not exist. `set_extraction_status` exists for the sibling column.
- `orchestrator.py:321` writes `handling_class=None`. Comment is correct. No task in 49 owns replacing it.
- No part in `02`'s thirteen claims the detector. P7 Deferred: *"P7 publishes the vocabulary the detectors write into."* After P7 ships, every real file is `Denied(unclassified)` while the gate works exactly as designed.

P7 holding OQ11 open by *not answering it in P7* is right. Holding it open by *P6 having no publish task* is the stub-swap defect from P5's `p4_stub`, one layer up: there is nothing to swap onto.

**Fix:** one task in P6 publishes the four methods, or P7's fixture is declared the v1 store and P6 never grows a writer. Council D2 recommends the first (P7 `ClassificationRecord` authoritative, §3.11 fact a projection, `sensitivity_state` a verbatim mirror). Either way, **name which part runs the detector** in `02`. A deferral needs a part to be deferred to.

### 3. P6 Task 26 as written cannot land on live `dispatch` — **blocking the walking skeleton, and it would poison `extraction_runs`**

Verified against `src/` this pass, not against the plan's self-description.

- `extract()` is one entry point. For `pdf.text` it always calls `document_ocr_decision`, which always calls `no_usable_facts` once `_has_text` is true (`ocr_policy.py:99-102`).
- Task 26: *"What does not change: `extract()`'s signature, `dispatch.py`, `ocr_policy.py`."* Loop 1 is supposed to extract without the OCR branch by passing a verdict that **raises** `FactPassNotRun`.
- Task 19 still produces `FactPassNotRun(Exception)`. Live `_extract_one` re-raises `ContractViolation` and swallows other `Exception` into `completeness=failed`. Round 4 executed both: `Exception` → every text-bearing PDF is a `failed` run, scan "succeeds"; `ContractViolation` → first ordinary PDF **ends the scan**. Neither is Task 26's acceptance test (*"running a full corpus without it firing"*).
- `ContractViolation` appears **zero times** in either skeleton. File 23 already closed the swallow. The plans still describe the pre-fix substrate.
- `set_extraction_status` **replaces** the JSON map (`files_table.py:166-169`). File 23 defect 3 already showed 2b erasing `{filesystem: complete, native: complete}` down to `{native: dataless}` by passing only the new run. Task 26 loop 3 does the same with OCR-only results unless it merges. The plan does not mention merge.

Council D5: take the four passes, **and** split `dispatch` into native-only and targeted-OCR entry points so loop 1 cannot reach the verdict by construction. The skeleton's "dispatch does not change" and D5 cannot both be executed.

**Fix:** P5 contract revision (two public entries, or `_ocr` published). `FactPassNotRun(ContractViolation)`. Loop 3 merges the tier map. P6 T26 and P7 T22 are **one diff, one owner**. Fake OCR engine in the Wave-2 fixture, or loops 3–4 remain the §2.7 dead path. Do not run a real corpus through a half-wired pass: `extraction_runs` are append-only.

### 4. P7 Task 22 and P6 Task 26 both edit `run_wave2`, and the one line that closes P7's seam sits in the loop Task 26 calls unchanged — **blocking "P1–P7 connected"**

`22` check 4 needs *"no content reaches a model before P7's classification"* **and a classification exists**. Vacuous today: nothing is classified.

P7 T22 asserts Wave-2 `handling_class` non-null after classification. That value is written at `orchestrator.py:321` inside stage 4, which Task 26 lists as unchanged. Round 4 surface 60: no producer in 49 tasks.

P7 T21 still asserts `src/privacy/` imports neither of **two** refusals. `22` §2 added a fourth (`ContractViolation`) and told P7 T21 the list is now three names. The skeleton was not updated.

**Fix:** one caller diff. `handling_class` gets an owner. T21's import-absence list includes `ContractViolation`. Check 4 asserts a value, not non-nullness (D2's discipline; T22 currently asserts non-null, and the shortest green is restoring the wrong line that was deleted 2026-08-21).

---

## Against the original design (`00`)

`00` has no tables and no section numbers. Every `§` citation in these plans is `01`'s. Where they disagree, `00` wins. `01`'s own header says so.

| `00` sentence | Skeleton | Fit |
|---|---|---|
| *"A fact is a statement such as subject = BUSIB 4300"* | Done-means 4 / walking skeleton: `course` | **Fails.** OQ4 open in the same file. |
| *"Academic files may use …"* | Task 2: closed list, acquiring others fails | **Fails.** Modal stripped. |
| *"Every fact preserves where it came from"* | `evidence_refs[]` required, P4 `observation_key`, never `observation_id` | Holds. |
| Facts carry no path; templates come later | No path/destination/folder/group column; PRAGMA + forbidden-substring test | Holds. |
| *"Privacy policy must be enforced before content reaches any model"* | Gate before P8; `Released` is the only content token | Holds as a P7 property; vacuous as a product property until a classification is produced. |
| Five handling classes, including Unreadable or unclassified | Exact five; absence → `unreadable_unclassified`, never `public_low` | Holds. The fifth class is an extraction outcome sitting in a sensitivity vocabulary — F-9 / D2's unanswered half. |
| Always-local: paths, complete extracted text, OCR, hashes, EXIF, GPS, user edits, group memberships, raw sensitive values | Task 7: nine construction refusals | Holds. |
| Releasable: excerpts, redacted identifiers, candidate labels, non-sensitive metadata, evidence references | SPEC adds `filename` | **Design wins.** Flagged, still in Task 7. |
| Local-first default `must` | W1 floor (`offline` \| `local_model`); winner unnamed | Holds. W1 itself is an audit derivation (`07` headed *"not applied"*); B5c is still Joseph's. |
| *"review and delete local derived data"* vs append-only log | `delete_derived` raises `UnratifiedResolution` naming I6 | Correct refusal. `00` uses "derived" once, in §3.2, to mean *fact from evidence* — under that reading OCR text is **not** derived. P7 SPEC's passport-OCR example is a legislation, not a reading. |
| Initial release: academic, college applications, research, career and recruiting, photos, code | Task 2 forbids career fields citing S3 | S3 is binding and still says deferred. §3.15 names career unhedged. Council D1 option 2 is the design-faithful opening; the skeleton implements neither. |

Quotation fidelity of the skeletons is high (round 1: ~2,950 lines, three inexact, two of those punctuation). The fidelity failure is **closing hedges** and **answering open questions in Done-means items**.

---

## Against shipped P1–P5 (connection, not prose)

Consumption of live modules is the best this wave has been. The failures are the converse: a consumer with no producer.

| Seam | Live | Skeleton | Status |
|---|---|---|---|
| P1 `append_event` / 17 writable columns | Audit fields are not among them | P7 explanation-JSON | **Right join.** Same device P5 used. |
| P1 P7's eight types | All eight in `_REGISTERED`, no collision | T1 asserts, adds nothing | **Right.** |
| P1 16 ceilings | `evidence.context_window` present | P6 has 16; P7 was 15, overnight README says fixed | Re-check P7 T13 still names `model.max_dossier_tokens_per_call` only — fine. |
| P1 `set_extraction_status` | Replaces whole map | T26 loop 3 / 2b already erase | **Will inherit file 23 defect 3.** |
| P1 `sensitivity_state` | Column, no setter | P7 injects `SensitivityStateWriter` | Gap reported; still no P1 task. |
| P4 `observations_by_key` → list | MINOR 8, two extractor versions, one key | P7 T9 current-row rule | **Right.** |
| P4 `observations_for_content(file_id, hash)` | **Not published** | P6 T7 filters in P6 | Named (F12). Fine for v1 if one filter site. |
| P4 text materialisers | `raw_value_at`, `text_units_for_run`, … | P7 `resolve.py` sole binder; **also `orchestrator.py:42`** | Round 2 B-3 still true: L2's `{evidence_shape, extractors, privacy}` set already excludes the caller that copies units into the bundle. |
| P5 `no_usable_facts` | Required keyword; `TARGETED_OCR_UNAVAILABLE` returns `False` | T19 factory; T26 removes the parameter | Signature matches. **Ordering does not.** |
| P5 `transcription_authorized` | `Callable[[], bool]`, no file_id | T5 adapter closes over scope | Seam mismatch reported, not patched. No wiring task (round 4 C-9). |
| P5 sensitivity signals | Now persisted, keyed to the raising run | T3/T7 consume | **Closed on the producer side.** |
| P2 `handling_class` | `None` | T22 asserts non-null | **No producer.** |
| P2 bundle copies every text unit | Unconditional, no handling-class filter | P7 OQ8: P7 writes nothing into a bundle | Sealed, trigger-protected second corpus of everything. D3. Grows per scan. |
| P2 `StageAdapter` | The only path to `stage_dimension_value` | Named in no SPEC; P6 T21 emits a dict | After P6, a live scan still writes **zero** `stage_output` rows unless someone authors the adapter. §8.5 is true of the harness, not the product. |
| P8 `contradicts` / `normalize` | Unbuilt | P8 Contract-in says From P6; P6 T17 *"owns none of the checking"* | Two of thirteen `unresolved` reasons are written from a check nobody writes. Not a P6/P7 execute-blocker; it is a P8 landmine. |

File 23 leftovers the skeletons do not know about: REUSE bundle with `run_ids=0`; OCR exception discards a successful PDF run; 2b status replace; two dataless predicates; `extract_filesystem` outside the failed catcher; 11 §7 still unowned. **Task 26 that rewrites the caller without absorbing these will preserve them.**

---

## Robust enough?

**As contracts:** P7 almost. One door, three-branch union, no override parameter, closed vocabularies, I6 refused rather than guessed. P6's *mechanism* (one fact format, evidence attached, abstention is a row, no path column) is. P6's *catalogue* is not a contract until D6/D1/D2 are written into Task 2.

**As a walking skeleton through Wave 2+3:** no. P6 T26 and P7 T22 are two stories about one function. Nobody produces a classification. Nobody fills `handling_class`. `no_usable_facts` is still consulted inside `extract()`. The Wave-2 path file 23 just proved still lies about the bundle on REUSE.

**As v1 facts on a Mac corpus:** no. Thresholds, gazetteers, career schema, identifier classes, OCR engine, PDF reader are all still Joseph or injected-None. Executing P6 gives you tables and a resolver over P4 fixtures. It does not resolve a real syllabus.

**As v1 privacy:** the door can be built. It denies the entire corpus, correctly, because nothing classified anything. That is not a P7 bug. It is a hole between all thirteen SPECs.

---

## Execute?

**No, not the stack.** Same headline as P2/P3 and P4/P5 at the equivalent moment.

| Document | Execute? |
|---|---|
| P6 Tasks 1, 3–18, 20–25, 27 | **After** Task 2 is rewritten to the D6/D1/D2 sentences, against live `evidence_shape` / `database_agent`. Do not wait for P5 readers. P4 fixtures are enough, as the split intended. |
| P6 Task 2 as written | **No.** Closed list, S3 hardened, `course` vs `subject`, four universal fields with no producer. |
| P6 Task 19 as written | **No** until `FactPassNotRun` inherits `ContractViolation` and loop 1 cannot reach the verdict. |
| P6 Task 26 as written | **No.** Dispatch must split; tier map must merge; one owner with P7 T22; absorb file 23 leftovers 1–3. |
| P7 Tasks 1–14, 16–21 against `tests/p7/p6_fixture.py` | **Yes**, after finding 2 names a detector owner in `02` (the fixture can stay; the *map* cannot stay silent). Sequential after P6's publish task is cleaner than another stub-swap. |
| P7 Task 15 | **No.** I6. The refusal surface can ship; the semantics cannot. |
| P7 Task 22 as a second `run_wave2` edit | **No.** Same diff as P6 T26. |
| "We can classify / redact / release now" | **No.** No detector, no identifier classes, no transform, no OCR engine. |
| P8 against P7 fixtures | **Yes**, after P7 T20. That is Done-means 11's P7 half. Do not wait for a live transport. |

---

## Edit order

Nothing below is a redesign. Each item is a named decision or a surgery on one task.

| Order | Owner | Change |
|---|---|---|
| 1 | Joseph | D6 (spelling + `subject`/`course`), D2 (authoritative record **and** detector owner), D1 (how far the catalogue opens). One-way at Task 2. |
| 2 | P6 SPEC + Task 2 | Strike S3-as-prohibition. Load §3.8's four. Spell the keys. Name producers for the four empty universals, or Deferred them with P9/P11 as blocked consumers. |
| 3 | P6 | One task publishes `SensitivityFacts` (or an equivalent P7 can import). P7 T4's swap path written now: `from facts.…`, not a hope. |
| 4 | `02` | Name the detector part. Fourteenth, or "Wave 3 caller, deferred", but *stated*. |
| 5 | P5 | Native-only and targeted-OCR public entries. `_ocr` is currently private. |
| 6 | P6 T19 + T26 + P7 T22 | One caller diff: four passes, `FactPassNotRun(ContractViolation)`, merge `set_extraction_status`, `handling_class` has an owner, file 23 leftovers 1–3 absorbed, fake OCR in the fixture. |
| 7 | P1 | `set_sensitivity_state`, same shape as `set_extraction_status`. Do not add a writer-less tombstone column (D3). |
| 8 | P7 T21 | Import-absence list is three names. |
| 9 | Fill | P7 1–21 against the fixture; P6 1, 3–18, 20–25, 27 against P4 fixtures. |
| 10 | Lead | Graphify hook. Still unpaid. Bundle text-unit copy (D3). `StageAdapter` owner. `contradicts` / `normalize` owner. |

Then: a caller-level test that does P3 `scan` → P5 native extract → P6 resolve → P5 targeted OCR → P6 re-resolve → P7 classify → P2 bundle with a **value** in `handling_class` and `source_scan_ref = scan_run_id`. That last item is not in either skeleton and is what "connects with the previous code" actually means.

Joseph still owes I6, install default, corpus area, whether unclassified may call a local model, identifier classes, retention, and whether W1 was ratified. None of those block Tasks 1 of either part except I6 blocking P7 T15.
