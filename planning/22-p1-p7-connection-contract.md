# P1–P7 — the connection contract

Date: 2026-08-21 (overnight)
Status: **seam contract.** What must be true for P6 and P7 to attach to a built P1–P5.
Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md) ·
cut: [`02-segmentation-map.md`](02-segmentation-map.md) ·
live state: [`20-p1-p5-recheck.md`](20-p1-p5-recheck.md)

P1–P5 and the Wave-2 caller are built and green. P6 and P7 are specified and unbuilt. This page is
the lead's half of the work: **the seams between them**, authored before either plan's detail, so
two parts are not written against two different readings of one contract.

Everything below was verified against live code, not against prose. Where a claim is inference it
says so.

---

## 1. What P6 and P7 attach to — verified, not assumed

P4/P5 were planned against a reconstructed stub and it cost a whole class of defects: two
computations of one fingerprint, two spellings of one engine name, a published emit order that was
random-UUID order. **P6 and P7 are planned against live modules.** Every surface below was checked
by import and signature this pass.

**Correction (round 4).** This table lists surfaces that **exist**, which is exactly why it missed
every seam that actually breaks. The failures are all the converse: a function a neighbouring SPEC
names and no plan builds — P7's `SensitivityFacts` (0 mentions in P6's plan), P8's `contradicts` and
`normalize` (each part hands them to the other), and P2's `StageAdapter`, named in no SPEC at all.
Of 69 seams round 4 tabulated, **21 have no producer.** See §6, check 7.

| Needed by | Real surface | Verified |
|---|---|---|
| P6 ← P4 | `evidence_shape.observation.Observation` — `observation_key`, `signal_tier`, `context_before` / `context_after` / `context_truncated` | names match P6 SPEC's Contract in exactly |
| P6 ← P4 | `evidence_shape.store.observations_for_run` / `observation_keys_for_run` / `observations_by_key` | present; **ordering fixed this pass** (was uuid4 order) |
| P6 ← P4 | `evidence_shape.fixtures` — 19 golden records | P6 is buildable with **no extractor present** |
| P6 → P5 | `no_usable_facts(file_id, content_hash) -> bool` | signature matches `dispatch.py`'s `Callable[[str, str], bool]` — **but see §4** |
| P6 ← P1 | `files_table.get_file`, `events.append_event`, `supersede.mark_superseded` | present |
| P7 ← P1 | `files.sensitivity_state` column | **exists, and nothing writes it** — see §3 |
| P7 ← P4 | the three context fields | present, and M5 says they exist *so §8.4 can redact a value without dropping its context* |
| P7 ← P5 | `extractors.safety.admit`, `SafetyPolicy`, the two refusals | present |
| ~~P7 → P2~~ **orchestrator → P2** | `bundle_file_entry.handling_class` | mis-attributed here: **P7 never reaches the bundle** (its own OQ8 says so). The producer is the caller's stage 4, and **no task in either plan gives it a value** |

---

## 2. The four refusals — a distinction P7 must not collapse

Two refusals were in the codebase, and they behave differently **on purpose**. P7's gate is a third
kind. **A fourth landed on 2026-08-21 and this section is the page a Task 19 author reads to pick a
base class, so it must name it.** Conflating any two is the obvious way this part goes wrong.

| Refusal | Rule | Refuses | Record produced |
|---|---|---|---|
| `ProtectedContainerRefused` | 11 §4b | **reading** | **nothing at all** — no run, no observation, no status write. P3's exclusion verdict on the container is the whole record |
| `DatalessRefused` | 11 §5 | **reading** | **one run** at `completeness = dataless`, zero observations — the identity is already known and §8.6 requires the file to stay visible as unfinished |
| P7's gate | §8.4 | **release**, not reading | an audit record; the content stays local and readable |
| `ContractViolation` | — | nothing: it is about the **call**, not the file | **nothing, and it ends the scan.** `extractors.failure.ContractViolation` always propagates. A caller's ordering error is not a fact about a file, and recording it as one both lies about the corpus and hides the defect. P6's `FactPassNotRun` inherits this |

The asymmetry between the first two is not an inconsistency: nothing inside a protected container
ever acquires a `file_id` or a `content_hash`, so a run row there is **unconstructible**, whereas a
dataless file's identity already exists. P7's is different again — it never prevents a local read.

Round 4 executed both candidate base classes for `FactPassNotRun`: under `Exception` it is swallowed
into a `failed` run per text-bearing PDF; under `ContractViolation` it propagates and **ends the scan
on the first text-bearing PDF**, because `ocr_policy.text_layer_state` consults the verdict
unconditionally. The second is the correct behaviour and it is still not sufficient — loop 1 cannot
avoid arming the verdict while `dispatch` publishes one entry point. The base class is necessary; the
`dispatch` split is what makes it usable.

Note for P7 Task 21, which asserts `src/privacy/` imports neither refusal: **that list is now three
names.**

**C4 binds the first three:** *"the gate still raises and writes nothing — a gate that also wrote would be
doing two jobs."* The catcher is always the caller's.

---

## 3. `sensitivity` — one concept with four candidate homes, and no producer at all

**The largest connection risk in the wave, and P6's own SPEC flags it** (P6 open question 11,
marked `[seam]`):

> `sensitivity status` is a universal *fact* (§3.11), a *sensitivity state* on the file record
> (§8.2), and a *handling class* in the privacy gate (§8.4). One record or three? Which part writes
> it, and does a user reclassification (§8.4) arrive as a `user_confirmed` fact?

Live state, checked this pass:

- `files.sensitivity_state` exists in P1's schema (`src/database_agent/db.py:120`) and **no code
  writes it.** `grep` for an assignment returns nothing.
- P7's SPEC publishes a classification record *"written through P6's `sensitivity` field"* — so P7
  writes **through P6**, not into P1's column.
- P2's `bundle_file_entry.handling_class` is §8.4's and was being fed P1's `sensitivity_state`
  until this pass. Both were NULL on a live scan, so nothing failed and the name was still wrong.

**Two corrections from round 4.** There are **four** homes, not three: P7's classification record
carries `handling_class` *and* a separate `protected` flag, and its own SPEC says whether the two are
co-extensive is unsettled. And the sharper framing is not "which record is authoritative" but that
**none of the four has a producer.** No part's SPEC claims the detector that writes a classification
— P7's Deferred row says the rule set is hand-authored and that P7 merely "publishes the vocabulary
the detectors write into". So `basis = detector` is unproduced, `files.sensitivity_state` stays NULL
after P7 ships, and `Denied(unclassified)` is the universal outcome of §8.4's door. **Deciding which
record wins does not make anything write one.**

**This is the exact defect class that has cost this project the most, at the largest scale it has
appeared.** It is not resolvable by inference — it is a decision about which record is
authoritative, and a second decision about who produces it. It is in [`overnight/NEEDS-JOSEPH.md`](overnight/NEEDS-JOSEPH.md).

**Until it is decided,** the standing rule for anyone building: a part that does not own the
concept passes `None` and says the value is unknown. It never forwards a neighbouring part's
column because the shapes happen to line up.

---

## 4. `no_usable_facts` — a live ordering defect in the caller

P6's SPEC constrains the signal it publishes to P5:

> **Defined only after P6's deterministic pass on that content hash has completed.** Consulted
> earlier it would return `true` for every file and trigger OCR on the whole corpus.

**The built caller violates this.** `orchestrator.run_wave2` loops over files calling `extract()`,
which consults `no_usable_facts` inline through `document_ocr_decision` to decide §2.2's targeted-OCR
route. P6's pass has not run — it cannot have. Today this is harmless *only* because every test
injects `lambda f, h: False`.

The signature is right; the **ordering** is wrong. Wiring a real P6 into today's caller shape runs
OCR over the entire corpus.

Inference, marked as such: the caller must become **four** passes rather than one loop — native
extraction → P6 deterministic pass → targeted OCR for the files P6 reports → **a second P6 pass**,
which the SPEC implies rather than states outright when it says the verdict *"is re-evaluated after
targeted OCR adds observations, because the new run changes the §3.4 cache key."*

**Caveat (round 4).** "The two cache keys differ by `analysis_tier` alone" is not derivable from the
code: §3.4's key takes **one** `analysis_tier` and **one** `extractor_version`, and a single file's
observations already span `filesystem.record/filesystem` and `pdf.text/native` before OCR exists. A
multi-run fact has no single tier or version to key on, and nothing settles which one it carries.

---

## 5. The pattern that produced three defects tonight

Three of tonight's fixes were the same shape: **a value computed correctly and then dropped, or a
column that exists with no writer.**

- `files.extraction_status_by_tier` — a §8.2 field, no writer, read `{}` after every real
  extraction until the caller was built.
- `Dispatched.sensitivity` — §2.9's signals, computed by E3, discarded by the caller.
- `extraction_routing` — a table P5 owns, written by nobody.
- `files.sensitivity_state` — **still** has no writer (§3 above).
- P2's `runs_dataless` bucket — could only ever read zero until a `dataless` run became
  constructible.

None of these fail a test, because a table that is never written and a column that is always NULL
are indistinguishable from correct behaviour at rest. **Any part added from here must carry a check
that every column it publishes has a writer, or state plainly that it does not yet.**

---

## 6. What "P1–P7 connected" must mean, as checks

Not prose. These are the assertions a caller-level test must make once P6 and P7 exist.

1. Every part is reachable from the caller — verified today for P1–P5 by AST import analysis.
2. Every published column has a writer, or a named part that will write it.
3. `no_usable_facts` is never consulted before P6's deterministic pass for that content hash.
4. No content reaches a model before P7's classification — §8.4, and the reason
   [`02`](02-segmentation-map.md) orders P7 before P8.
5. Exactly one part writes each concept: one fingerprint, one hash spelling, one extractor name per
   engine, one sensitivity record.
6. Every refusal produces the record its rule requires, and no more.
7. **Every surface a SPEC's Contract-in names has a producing task in some plan.** Added by round 4,
   which found that checks 1–6 all run in one direction — they look for a published thing with no
   consumer, and every seam that actually broke was a *consumer with no producer*. This one check
   catches four of round 4's findings mechanically.

Check 4 is currently vacuous in the safe direction: "no content reaches a model before P7's
classification" is trivially satisfied when no file is ever classified. It needs "**and a
classification exists for every file**" to mean anything.
