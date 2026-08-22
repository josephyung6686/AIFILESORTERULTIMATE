# P7 — Privacy and consent gate — PLAN

Date: 2026-08-22
Substrate: P1–P5, the Wave-2 orchestrator and the reader stack, shipped and green at **1302 tests**.
Source of truth: `planning/00-database-agent-product-design.md`. Then `SPEC.md`. Then this preamble.

**22 tasks.** Every task carries complete test code and complete implementation code; there are no
placeholders anywhere in this plan.

This preamble is written **once, by the lead**. The task sections do not repeat it. Where a task
section and this preamble disagree, this preamble is later and wins — every such disagreement was
found deliberately and is recorded in `../_ASSEMBLY-RULINGS.md`.

> **P7 is a door, not a classifier.** What is deliverable here is that the door works, is the only
> door, and cannot be talked around. **A P7 that is done and a product that classifies files are
> different claims, and only the first is deliverable here.**

---

## 1. How to execute this plan

Each task is a TDD unit: write the test, **run it and see the stated failure**, write the
implementation, run it again and see PASS, commit. If the failure you get is not the one written
down, **stop** — the plan is wrong about the substrate, and that is worth more than the task.

**P7 creates and owns its own tables inside P1's single database.** It modifies no P1–P5 file. It
invents no handling class. It imports **none** of `extractors`' three refusals
(`ProtectedContainerRefused`, `DatalessRefused`, `ContractViolation`).

**Python 3.12, stdlib only** in `src/privacy/`.

**`src/privacy/` holds no threshold, no identifier class, and no detection rule.** Every one of those
is injected or belongs to a part that does not exist yet.

### Build order — the numbering is not the order

```
Tasks 1–3      package, vocabularies, the classification record
Task 4         classification_store.py + schema.py::create_privacy_schema   ← creates the schema fn
Task 5         policy.py                                    ← EXTENDS the same create_privacy_schema
Tasks 6, 7     local-first default; the releasable item kinds
Task 8         redaction.py — publishes span_address(...)    ← BEFORE Task 9, which imports it
Task 9         resolve.py  — the only place content materialises
Task 10        audit.py

Tasks 11–14 DO NOT BUILD IN NUMERIC ORDER. The module graph is acyclic; the task graph is not.
   Executable order:   14 · 11-a · 13 · 12 · 11-b     ← Task 11 lands in TWO commits
     11-a = src/privacy/release.py — nine frozen dataclasses, eight constants, no behaviour
     11-b = src/privacy/gate.py + tests/p7/test_p7_release.py
   `release.py` carries no test of its own at 11-a, and that is deliberate rather than a gap.
   Task 14 runs BEFORE 11-a, because its branch-disjointness assertion imports `release.Denied`.

Tasks 15–19   revocation · reclassification · moves · display · transport guard
Tasks 20–22   the published fixtures · the no-invention guard · the walking skeleton
```

**`DECISION_ORDER` is published because the order IS the contract.** Five denials, then consent.
**The order is forced, not chosen**, and Task 13's `DECIDABLE_FROM_REQUEST` is the proof obligation:
*no denial decidable from the request alone may be decided after one that needs the file's content* —
a rule that is only enforceable if it is data.

Task 17's internal read order: **absence, then the flag, then the policy.**

---

## 2. The ratified decisions that bind this plan

| | Ruling |
|---|---|
| **D2** | P7's **`ClassificationRecord`**, keyed `(file_id, content_hash)`, is **authoritative**. `files.sensitivity_state` is its **projection**, written through P1's published `set_sensitivity_state`. P7 takes **no** `SensitivityStateWriter` and **no** injected protocol. |
| **D3** | `events` is append-only forever. "Derived" is a **literal enumerated list**. No writer-less tombstone column. |
| **D7** | **P6 creates no `sensitivity_status` field row.** P7's record is the sole home. **P7's Contract-in from P6 is now empty** and SPEC Done-means 2 is amended off *"through P6"*. C24 and C25 are closed. |
| **D10** | P4's `norm` region unit means **TOP-LEFT**. Closed at the adapter in `src/readers/ocr_vision.py` (`87016b0`). **C22 is closed and Task 8's redaction may rely on it.** |
| **D11** | **`ProtectedSummary.class_breakdown` is a census of the WHOLE SCOPE**, not of the protected set. |
| **D13** | The five unratified round-5 cuts are **KEPT** — including **CUT 4, so the `Gate` facade stays**, and **CUT 2, so Task 19 stays**. CUT 1 (P6 Task 26) remains the only ratified cut. |
| **D14** | **`AuditRecord.release_id` is `None` on a release record**; the join runs **ledger → events**. SPEC §7 is amended. **§6's ordering guarantee stands untouched.** |

### D7's consequence, stated rather than buried

P7 consumes **nothing** from P6. Task 21 asserts it from the other side — *"P7 reads no P6 surface,
holds no `file_facts`"* — and the L2 guard set is `{evidence_shape, orchestrator, privacy}`.

> **Open, and it needs an owner:** the reliability-state and basis literals P7 writes —
> `user_confirmed`, `user` — now have **no published home**, because P7 must not import P6. Task 2
> publishes `CLASSIFICATION_BASES` but no per-value constant and **no reliability-state vocabulary at
> all**. Task 2 is the obvious owner and has not been told to build them. Until it does, those two
> literals are bare strings in `classification.py` — the exact defect §3.1 below forbids.

### D11's consequence: `ProtectedSummary` gains a third field

Task 18's `Produces` says *"two fields, and deliberately no third"*. **That clause is struck.** The
type is:

```python
ProtectedSummary — frozen: count: int, scope_total: int, class_breakdown: Mapping[str, int]
```

`count` is §8.4's protected aggregate. `scope_total` and `class_breakdown` census **everything in
scope**. **`sum(class_breakdown.values()) == scope_total`, and it does NOT equal `count`** — they are
two denominators and conflating them would let a UI rendering *"11 protected identity records"* off
the breakdown describe an **unprotected** file as protected.

The *reason* "no third field" was written survives and is why the type is still safe: Done-means 10
requires that the summary **cannot return filenames or content**, proved at the type level over
`dataclasses.fields`. A third `int` does not weaken that. Restate the constraint as **"three fields,
all `int` or `Mapping[str, int]`, and deliberately no field a filename could occupy"** — and update
the type-level test with it, rather than letting one silently break the other.

### D14's consequence: one assertion and two fixtures are now wrong

`AuditRecord.release_id` is `None` on a release record, so **`assert record.release_id ==
decision.release_id` cannot hold** — a `Released` carries a real ledger id and the audit record
carries `None`. Replace it with `assert record.release_id is None` plus a test that the join runs
**ledger → events** through the `audit_id` column Task 12 built for exactly that direction. The
fixtures constructing audit records with `release_id="release-1"` change with it.

---

## 3. Conventions, stated once

### 3.1 Closed vocabularies are NAMED CONSTANTS — never a literal, never an index

Every closed vocabulary P7 publishes — handling classes, denial reasons, operation modes, consent
options, classification bases, recorded actions, move reasons, setting values — is published **once**
with a named constant per member, and every consumer imports the constant. Never a bare string, never
an index into a tuple. Guards assert this by **runtime introspection**, never by source-text search.

**Three live violations to fix at assembly**, all of them the same shape:

1. **`basis="user"` and `reliability_state="user_confirmed"` are bare literals** in Task 16's
   implementation, and recur in Tasks 2 and 4/5. See the open item under D7 — Task 2 owes both.
2. **`SHOWN` / `REDACTED` have three homes and the tuple has three names.** Task 5 publishes them as
   `REDACTION_VALUES` (and its author reported the doubt: *"they arguably belong in Task 2's
   `vocabulary.py`; if Task 2 publishes them, `policy.py` re-exports and deletes its own"*), Task 18
   publishes them as `SETTING_VALUES`, and a third section calls the same tuple `FACET_VALUES`.
   **One home, one name, everyone else re-exports.**
3. **Denial reasons must not be prose.** A reason is a snake_case identifier closed by a published
   tuple. A reason that is an English sentence tested by substring containment is a second home for
   a vocabulary *and* it puts UX copy into a value P11/P12 will store verbatim.

### 3.2 The import direction is fixed, and it is what stops a four-task cycle

| module | imports | why |
|---|---|---|
| `consent.py` | — | **defines `NeedsConsent`.** The skeleton gives Task 14 its three fields and its four-option invariant, and one dataclass cannot have two homes. |
| `release.py` | `consent` **only** | re-exports `NeedsConsent` so Tasks 20/22 can take all three branch types from one module |
| `binding.py` | `release` under `TYPE_CHECKING` | `mint_release` returns a `str`; it never *constructs* a `Released`, so the guard is honest rather than evasive |
| `denial.py` | `release` **at run time** | it *does* construct a `Denied`, so `release` must not import back |
| `gate.py` | all of them | the logic lives here |

One section wrote the opposite — branch types defined in `release.py`, `consent.py` importing
`NeedsConsent` — which **inverts the edge and recreates the cycle this rule exists to break.** Its
reasoning is kept because it is the justification for the single-home rule: *"Two definitions of one
branch type is exactly the duplication that makes a caller's `isinstance` check silently false."*

### 3.3 One name per job for the scope device

`scope_for` **resolves** a file to its scope; `files_in_scope` **enumerates** a scope's files. Two
jobs, two names, both required keywords with no default. **`area_of` is deleted** — it is a third
spelling of `scope_for`, invented in a fixture.

`Gate.__init__` takes **twelve** keyword-only parameters, and **Task 20 owns pinning them.** Task 11
said Task 20 pins it and Task 20 said it reports a pin on Task 11; that deferral loop is closed here.
`measure_tokens` and `template_for` default to `None`, so with the default their denials **cannot
fire** — the same shape as *"an unset ceiling cannot deny"* — which is why fixtures 4, 6 and 16 need
`gate_arguments()` to supply them.

### 3.4 `span` is the canonical locator string, everywhere

`'body:page=2#16-27'` for a text span, `'table:sheet=1/row=4/cell=3'` for a container-path address.
It round-trips through `parse_locator`. **An opaque `"0-19"` would satisfy the type and not the
requirement.** `redaction.span_address(location) -> str` is Task 8's and Task 9 imports it — two
independent serialisations of one address is the "three spellings" defect.

`serialize_locator` **drops the region**, and `parse_locator(text, *, region=None)` takes it back as a
separate argument: **P4's canonical address cannot carry a bounding box.** That is still true under
D10 and is independent of it.

### 3.5 Task 9 is the only place content materialises — in the whole repository

`resolve.py` is the only module under `src/privacy/` binding a P4 text materialiser, and `release.py`
is the only module importing `resolve`. Task 21 asserts both **repo-wide**. The handle is
**`observation_key`**, never `observation_id`, which dies on extractor upgrade (M14). **The key, not
the id, is what makes that durable.**

### 3.6 Four refusals, ranked — and P7 owns exactly one

`ProtectedContainerRefused` refuses **reading** and produces nothing · `DatalessRefused` refuses
**reading** and produces one `dataless` run · **P7's `Denied` refuses *release*** — the bytes were read
locally, lawfully, long ago — and is **the only one consent may override** · `ContractViolation` is a
fourth kind, about the **call**, and always propagates. `src/privacy/` imports none of the first three.

### 3.7 `Gate.release` writes exactly one thing and raises nothing

C4: *a gate that also wrote would be doing two jobs.* The one write is the audit event, and it is
**inside** the decision because §8.4 makes it a precondition — *"Every model call should be recorded
in a consent-aware audit record."* **A release returned before its record existed would open an
interval in which content is releasable and unaudited.** D14 preserves that ordering exactly.

Everything else — P8's `Refusal`, P13's consent routing, a classification write — is the caller's.

### 3.8 `no_model_use` must never become `abstain`, and P7 makes that unrepresentable

`NeedsConsent` carries **no `reason` field**, so it cannot be read as a `Denied`. Choosing
`no_model_use` writes a `consent_granted` event with a `user_id` and a timestamp, so a later reader
can tell **a recorded refusal from silence**. Whether a caller absorbs the branch is P8 Done-means 13
and P13 Done-means 16; **P7 does not police it.**

### 3.9 The `protected` flag decides, never the class

SPEC §2 / OQ1: *"Neighbouring parts should consume the `protected` flag, not infer it from the
class."* Two tests construct the records that would break an inference — `public_low` with
`protected=True`, and `highly_sensitive_credential_bearing` with `protected=False` — and assert the
flag wins **in both directions**.

**`SENSITIVE_CLASSES` stays unpublished.** Publishing it would answer NEEDS-JOSEPH **C5** — *"is
`protected` exactly the top two handling classes?"* — in code. **C5 is still open**; D7 closed C24,
which is a different question. The consent branch reads `ClassificationRecord.protected` instead.

### 3.10 The five words with `protected` in them

Five, not four — the skeleton's Task 2 heading counts four and its body names five, **and the body is
right**:

| word | owner |
|---|---|
| `protected` | P7 — the boolean on `ClassificationRecord` (Task 3) |
| `protected_cloud_target` | P7 — a `Denied.reason` (Task 2) |
| `protected_records_template` | P7 — a `Denied.reason` (Task 2) |
| `untouched_protected` | P3 — `exclusion.LABEL_UNTOUCHED_PROTECTED` |
| `protected_container` | P3 — `exclusion.REASON_PROTECTED_CONTAINER` |

### 3.11 P7 tables take no `BEFORE DELETE` trigger

Task 15 asserts **exactly thirteen** tables refuse a delete; a fourteenth fails a sibling's test.
*The release ledger is a capability record, not a provenance record.* §8.2's R6 binds `events`, and
**P7 does not extend it by imitation.**

### 3.12 Two devices worth keeping, because they would be re-invented badly

**`record_id` as a VIRTUAL generated projection.** P1's `mark_superseded` and `chain` are
`… WHERE record_id = ?`, so P7's classification table projects its published `fact_id` under that
name — exactly as P4's `evidence` table projects `observation_id`
(`SUPERSEDE_ADAPTER_COLUMN = "record_id"`). **P1's tested supersede functions are reused verbatim
rather than rewritten under a second name.**

**`sqlite3.Connection.set_trace_callback` for the SQL guard.** `set_sensitivity_state` issues exactly
one statement, `UPDATE files SET sensitivity_state = ? WHERE file_id = ?`, and appends no event (M8:
P7 authors, P1 stores). That statement is **observable at run time**, which is how Task 4 proves
*"`src/privacy/` issues no `UPDATE files` of its own"* **without grepping source text** — the concrete
answer to the runtime-introspection rule where introspecting a Python namespace does not apply.

### 3.13 §3.13's ordering is P6's, quoted, never re-derived

Five states ranked, `rejected` outside the ranking. **Task 4 writes the order down once and computes
nothing from it**, which is why CUT 6's fate does not reach P7 either way.

### 3.14 `tests/p7/conftest.py`

**Task 1 creates it** and publishes `p7_conn` and `FIXED_CLOCK`. **Task 4 modifies it** to add P7's
schema. **Task 5 extends the same `create_privacy_schema`** — one schema entry point, called once.
**It must not shadow P1's conftest** under pytest's default prepend import mode.

Four schema creators coexist on one connection — `database_agent.db.create_schema`,
`scan_agent.schema.create_scan_schema`, `evidence_shape.schema.create_evidence_schema` and
`extractors.schema.create_extraction_schema` — run in sequence they produce **nineteen tables with no
collision**, and that is what `p7_conn` builds on.

---

## 4. Verified live, 2026-08-22 — by import and by execution

> Every signature was read with `inspect.signature`, never from a PLAN. Four fabricated quotations
> were found and removed from these plans this week, and the mechanism that produced them was quoting
> from memory — so nothing here is quoted from memory.

**P1 events.** P7's **eight** event types are already in `database_agent.events._REGISTERED`, each
with `base = None`. **Registration is a spec-level act; Task 1 asserts and adds nothing.**
`append_event(conn, **fields) -> int` accepts exactly **seventeen** named columns, raises
`MalformedEvent` on an eighteenth, and its `_REQUIRED` set includes `explanation` and rejects both
`None` and `""` — so **every P7 event carries a non-empty structured explanation by construction.**
**The `events` table has no `appended_at` column**; `AuditRecord.appended_at` lives in the
`explanation` JSON.

**M14's two handles are shape-distinguishable.** `observation_key` is `"sha256:" + 64 hex` — 71
characters; `evidence_shape.store.new_id()` is a `uuid4` string. Task 3's refusal is **mechanical, not
stylistic.**

**P4.** `observations_by_key` returns **two rows** when two extractor versions carry one key, and
`Observation` — seventeen fields — carries **neither `observation_id` nor `superseded_by`**:
supersession lives on the `evidence` **row**, not the dataclass. **Task 9 therefore cannot pick the
current row out of that list**, and closes the gap with one narrow read plus P4's published
`get_observation`. `unit_for_observation` returns **`None`** for a container-path-only address — there
is no `TextUnit` at a spreadsheet cell — which makes §2.3's addressing a **second** resolution path,
not a degenerate case of the first. `check_span_anchor` **raises** when
`observation.location.text_span is None`, so **it cannot be used as a general-purpose validator.**

**P1 files.** `record_file` **stats the path**, so a `files` row needs a real file on disk even when
`content_hash` is supplied — every fixture writes bytes into `tmp_path` first. It also **accepts an
explicit content hash**, which is what makes Task 20's replay possible: a fixture seeded at P4's own
content hash reproduces P4's own `observation_key`, so `file_id` is the only field a replay
substitutes. **The stored digest carries no `sha256:` prefix.** `FILES_COLUMNS` is sixteen and ends
with `sensitivity_state`.

**P5.** `sensitivity_signals_for` is keyed by `run_id` only, so the file-level walk is
`runs_for_file(conn, file_id)` → `sensitivity_signals_for(conn, run.run_id)`. **P7 adds no reader to
P5.**

**P1 budget and db.** `CEILING_KEYS` has sixteen members including
`model.max_dossier_tokens_per_call`; `get_ceiling` returns **`None` when nothing set it**, which is
the ordinary state and which Task 13 must handle **without inventing a number**. `open_database` runs
autocommit with `row_factory = sqlite3.Row` and an authorizer that denies only
`SQLITE_DROP_TABLE events` and three trigger drops — **`CREATE TABLE` is not denied, so P7 may create
its tables on the same handle.**

**`canonical_json`** is `json.dumps(..., sort_keys=True, separators=(",",":"), ensure_ascii=False,
allow_nan=False)`. **Tuples serialise as arrays**, so a frozen dataclass through `dataclasses.asdict`
has exactly one stored form.

**The thirteen-table append-only proof.** `DELETE FROM events` raises
`sqlite3.IntegrityError: events is append-only (R6, 8.2)`; `DROP TRIGGER events_no_delete` raises
`not authorized`. **Done-means 8 is provable against the substrate rather than against P7's
restraint.**

**The orchestrator.** `run_wave2` takes **seventeen** parameters — `conn`, `selection_id`, then
fifteen keyword-only. Its `policy` parameter is **P5's `SafetyPolicy`** — `is_protected_container`,
`is_dataless` — **not P7's `Policy`**. Two different words one parameter apart, which is the defect
class this project has paid for most; Task 22 names both in the same test.
`src/orchestrator.py:402` passes literal `None` for `bundle_file_entry.handling_class`, with the
comment *"The honest value is None because the class is unknown, not because another column happened
to be empty."*

**P4 fixtures.** Nineteen worked examples, `observation_key` already computed. **Fixture 8** is an OCR
region — a 43-character text unit with an observation spanning `0-24`. **Fixture 18** carries
`completeness = "unreadable"`. **P7 invents no evidence of its own.**

---

## 5. The detector does not exist

D2 puts P7's rule set behind an injection and **no task in any plan produces one.** On a real corpus
**every file resolves to `Denied(unclassified)`.** That is the ordinary path, not an error path — *a
`Denied` is what this gate returns on a Tuesday.* Task 13 is written with `unclassified` at its centre
of gravity: the longest explanation, the most remedy options, its own precedence argument.

**The strongest available test says it plainly:** a file P5 has already marked *potentially sensitive*
on every value still has **no** classification and still resolves to `unreadable_unclassified`.
**Signals are not a class. A signal reader is not a detector.** On a corpus P5 never ran over,
`sensitive_observation_keys` returns the empty set — and that means **nothing was signalled**, never
**nothing is sensitive**.

**Never default an absent classification to a public or low class.** §8.6: cost exhaustion *"must
never turn into lower-quality automatic classification"*.

Under **D11**, today's honest state is now *visible* rather than merely true: a real corpus yields
`count = 0` with `scope_total = N` and `class_breakdown["unreadable_unclassified"] == N`. **"0
protected records" means nothing has looked, not nothing is protected.**

---

## 6. What is open, and stays open

- **B5d / C9a — `filename` as a sixth releasable kind.** §8.4 names **five** and puts *paths* in the
  always-local set; §7.7's residual dossier *"includes the filename"* and §7.3 forbids filenames in
  prompts **only** for `Protected Records`. Task 7 builds the sixth kind and makes it **unadmittable
  without an explicit opt-in** (`allow_unratified`, required, no default), so a reviewer sees an
  unratified reading rather than a shipped one. A test asserts the error message itself contains
  `"B5d"` and `"C9a"`.
- **C5 — is `protected` exactly the top two handling classes?** Held open by
  `ClassificationRecord.protected` being a required caller-supplied boolean with no derivation, and
  by `SENSITIVE_CLASSES` being deliberately unpublished. **D7 did not touch this.**
- **OQ3 — what is a corpus area?** P7 cannot enumerate the files a scope covers and **must not
  guess**; the caller supplies the resolver. **D11 makes that resolver load-bearing for the census,
  not just for the count.**
- **OQ8 — may a replay bundle carry audit records and excerpt spans?** §8.5 allows *"a frozen corpus
  snapshot or a metadata-safe representation of one"* and lists *"policy settings"*; whether a bundle
  intended to leave the machine may carry audit records — which name excerpts — is **unstated**. Task
  22 asserts the caller's literal `None` **stays** and that P7 wrote it nothing.
- **All eleven SPEC open questions are held in `vocabulary.OPEN_QUESTIONS`**, which Task 21 reads.
  **None of the eleven is answered in code.** Task 21's `HELD_OPEN` carries only what is *not* among
  the eleven — and under D7/D10 that is **`I6` alone**, plus the five kept cuts and `filename`.
  **A guard asserting a ruled question is open fails the day the plan executes**, which is exactly
  the failure both authors correctly diagnosed for P6 OQ11 and then reproduced twice.
- **The five kept cuts (D13).** CUT 2 (Task 19) and CUT 4 (the `Gate` facade) target this part and
  are **ruled and kept**. Each carries a callout naming the cut, its argument, and its status. **Do
  not silently comply with a cut, and do not silently ignore one** — both are the same failure, and
  an author writing *"the ruling for this plan is…"* is making a decision that is not theirs.
- **Round 4's C-5.** P8's Contract-in names `normalize` and `contradicts` as P6's; P6 disowns both.
  Each part hands them to the other. **Named, not invented.**
- **D10's remaining half:** `evidence_shape.location.location()` accepts any `region` mapping
  **without validating it**. That check belongs in P4, and **Task 8's redaction is its first real
  consumer.**

---

## 7. The safety rule that outranks everything here

Joseph's words: *"reports, apps and system files MUST NOT BE MOVED OR READ OR ANYTHING SYSTEM OR
SENSITIVE IN THAT SENSE."*

A protected container is **marked and counted, never opened**. It appears in the UI as
present-but-untouched, with a reachable explanation. It is **never silently omitted**, and it is never
described as *"understood and found unimportant"*.

**That rule decided a ruling in this part.** One Task 18 draft filtered its summary to classified,
protected files — so with no detector, a real corpus rendered as an empty summary. It is §8.6's
*"false impression that an unprocessed file was understood and found unimportant"*, reached by
omission rather than by assertion. **D11 is the fix, and it is why `scope_total` exists.**
