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

---

### Task 1: Package skeleton, and the eight event types P1 already registered

**Files:**
- Create: `src/privacy/__init__.py`
- Create: `src/privacy/authorship.py`
- Create: `tests/p7/conftest.py`
- Test: `tests/p7/test_p7_authorship.py`

**Interfaces:**
- Consumes: `database_agent.events.REGISTERED_EVENT_TYPES: MappingProxyType`,
  `.RESERVED_EVENT_TYPES: frozenset[str]`, `.EVENT_TYPES: MappingProxyType`,
  `.EVENT_FIELDS: tuple[str, ...]`, `.CORRECTION_FIELDS: tuple[str, ...]`,
  `.append_event(conn, **fields) -> int`, `.MalformedEvent`, `.UnregisteredEventType`.
- Produces (`authorship.py`):
  - `SUBSYSTEM: str = "P7"` — §8.2's *"responsible subsystem"*, bound in exactly one place.
  - `COMPONENT_VERSION: str` — P7's own version, the default for §8.2's version slot.
  - `CLASSIFICATION_ASSIGNED`, `CLASSIFICATION_SUPERSEDED`, `POLICY_SET`, `CONSENT_GRANTED`,
    `CONSENT_REVOKED`, `MODEL_RELEASE`, `MODEL_RELEASE_DENIED`, `CONSENT_REQUESTED` — all `str`.
  - `P7_EVENT_TYPES: tuple[str, ...]` — the eight, in the SPEC's order.
  - `event_defaults(*, event_type, **fields) -> dict[str, object]`.
- Produces (`tests/p7/conftest.py`): the `p7_conn` fixture and `FIXED_CLOCK`.

**Done-means:** substrate for 4, 6, 7, 8.

**Why this is Task 1.** Every P7 surface that records anything appends an event, and the one thing
that must never be got wrong is whose name lands in `subsystem`. M8 — *"the acting part authors; P1
writes"* — is unmeetable from a log where the author is a parameter anyone may set. Putting the
authorship helper first means no later task has a plausible reason to type `"P7"` by hand, and Task
21's *"there is one place in `privacy` where that value is written"* guard has exactly one place to
look.

**`event_defaults` writes nothing and takes no connection.** It fills §8.2's authorship fields and
returns a plain `dict` for the caller to hand to P1's `append_event`. There is no code path in which
importing `privacy.authorship` appends an event, and no code path in which P7 writes without a caller
having decided to. C4's rule — *"the gate still raises and writes nothing — a gate that also wrote
would be doing two jobs"* — starts being true here.

**It raises P1's exceptions, not its own, and that is why both are in the `Consumes` list.**
`event_defaults` pre-validates the same shape `append_event` validates: an unknown field is
`MalformedEvent`, an event type outside P7's eight is `UnregisteredEventType`. A caller therefore
catches one exception type whether the refusal came early or at the writer. A third exception class
here would mean two vocabularies for one refusal.

**P7's helper is narrower than P1's writer, on purpose.** `append_event` accepts any of the
thirty-five registered names; `event_defaults` accepts eight. P8's `model_call_issued` is a
perfectly valid event that P7 has no business authoring, and a helper that stamps
`subsystem = "P7"` onto it would produce a true-looking row that names the wrong actor.

**`base_event_type` is refused rather than defaulted.** All eight of P7's names carry `base = None`
in P1's table — none is a typed specialization of one of §8.2's nineteen — so a caller supplying one
is asserting a relationship the registration does not record. P1 would store it; P7 refuses it.

**`explanation` is deliberately not defaulted.** P1's `_REQUIRED` includes it and rejects the empty
string, so every P7 event carries a non-empty *"structured explanation or evidence reference"*
(§8.2) by construction. That slot is where the consent-aware audit record lives — §8.4's record has
thirteen fields `events` has no column for, and Task 10 puts them there as canonical JSON. A default
here would let an event ship with placeholder prose in the one column the audit record needs.

**`observed_at` defaults to now and a caller-supplied value wins.** §8.5's replay must be able to pin
the clock, and every call site in the finished sibling section passes one explicitly.

**`tests/p7/conftest.py` holds P7 names only.** The skeleton's constraint is that nothing imported
across parts by name may live there — `tests/` has no `__init__.py`, so pytest puts each test
directory on `sys.path` and a helper module named the same thing in two directories is one module.
P7's own fixtures are safe; a name another part's conftest or helper also defines is not. The fixture
composes the four substrate schema creators and **does not** create P7's own tables: `schema.py` and
`create_privacy_schema` are Task 5's, and Task 5 adds that one call to this fixture. The request
builders the File Structure line mentions need `ModelCallRequest`, which is Task 11's, and arrive
with it.

- [ ] **Step 1: Write `tests/p7/conftest.py`**

```python
# tests/p7/conftest.py
"""P7's test fixtures.

`p7_conn` is P1's root `conn` fixture with the substrate P7 reads from added:
P1's own tables, P3's scan tables, P4's evidence tables and P5's extraction
tables. `tests/conftest.py` is not modified — P1 owns it.

P7's OWN tables are absent here on purpose. `privacy.schema.create_privacy_schema`
is Task 5's, and Task 5 adds the one call below. Everything Tasks 1-4 need already
exists in the substrate.

Nothing in this file may be a name another part's conftest or test helper also
defines: `tests/` carries no `__init__.py`, so pytest puts each test directory on
`sys.path` and two helpers sharing a name are one module. Only P7 fixtures live
here.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema

from scan_agent.schema import create_scan_schema

from evidence_shape.schema import create_evidence_schema

from extractors.schema import create_extraction_schema

#: §8.5 requires replay to reproduce a run, and every P7 record carries §8.2's
#: "time of observation". An injectable clock is what makes an equality assertion
#: on a stored record possible at all.
FIXED_CLOCK = "2026-08-22T12:00:00+00:00"


@pytest.fixture()
def p7_conn(conn):
    """P1's database with P3's, P4's and P5's tables added.

    P7 creates and owns its own tables inside this one database and creates no
    table belonging to another part. Four creators, run in dependency order, were
    verified to coexist: nineteen tables, no collision.
    """
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    return conn
```

- [ ] **Step 2: Write the failing test**

```python
# tests/p7/test_p7_authorship.py
"""P7's eight event types are P1's already, and P7's name is written once.

Two things are proved here and they pull in opposite directions. Registration is a
SPEC-level act, so this package must be unable to perform one: the eight names are
asserted present and nothing is added. Authorship is a run-time act, so this package
must perform it in exactly one place: `event_defaults` fills `subsystem` and refuses
to let a caller set it, because M8's "the acting part authors" is unmeetable from a
log where the author is a parameter anyone may set.
"""
import importlib

import pytest

from database_agent.events import (
    CORRECTION_FIELDS, EVENT_FIELDS, EVENT_TYPES, REGISTERED_EVENT_TYPES,
    RESERVED_EVENT_TYPES, MalformedEvent, UnregisteredEventType, append_event,
)

import privacy.authorship as authorship
from privacy.authorship import (
    CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, COMPONENT_VERSION,
    CONSENT_GRANTED, CONSENT_REQUESTED, CONSENT_REVOKED, MODEL_RELEASE,
    MODEL_RELEASE_DENIED, P7_EVENT_TYPES, POLICY_SET, SUBSYSTEM, event_defaults,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"

#: A ninth name that looks exactly like one of P7's and is registered nowhere. It is
#: the shape of the mistake this test exists to catch: a later author needing an
#: event, inventing a plausible name, and discovering at run time that registration
#: is not something this package can do.
UNREGISTERED = "classification_downgraded"

#: P8's, registered in P1's table and not P7's to author.
ANOTHER_PARTS_EVENT = "model_call_issued"


def an_event(**over):
    fields = dict(event_type=CLASSIFICATION_ASSIGNED, observed_at=FIXED_CLOCK,
                  explanation='{"handling_class": "sensitive_personal"}')
    fields.update(over)
    return fields


# --- the eight names, and the fact that P7 did not add them ------------------

def test_the_eight_are_the_specs_eight_in_the_specs_order():
    # SPEC, Cross-cutting answers -> Provenance, in its own order: "Appends:
    # classification_assigned, classification_superseded (including user
    # reclassification), policy_set, consent_granted, consent_revoked,
    # model_release, model_release_denied, consent_requested."
    assert P7_EVENT_TYPES == (
        "classification_assigned", "classification_superseded", "policy_set",
        "consent_granted", "consent_revoked", "model_release",
        "model_release_denied", "consent_requested",
    )
    assert len(P7_EVENT_TYPES) == 8


def test_each_constant_names_its_own_string():
    assert (CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, POLICY_SET,
            CONSENT_GRANTED, CONSENT_REVOKED, MODEL_RELEASE, MODEL_RELEASE_DENIED,
            CONSENT_REQUESTED) == P7_EVENT_TYPES


def test_all_eight_are_already_registered_in_p1_with_no_base():
    # src/database_agent/events.py:43-51, under the comment "P7 SPEC, Cross-cutting
    # answers -> Provenance. Eight." P1 compiled them from this SPEC; P7 asserts.
    for name in P7_EVENT_TYPES:
        assert name in REGISTERED_EVENT_TYPES, name
        assert REGISTERED_EVENT_TYPES[name] is None, name


def test_none_of_the_eight_collides_with_8_2s_nineteen():
    # §8.2's list is reserved and may not be redefined by any part. P1 checks this at
    # IMPORT, so a collision is an ImportError; this asserts the property P1 checked.
    assert len(RESERVED_EVENT_TYPES) == 19
    assert set(P7_EVENT_TYPES).isdisjoint(RESERVED_EVENT_TYPES)


def test_importing_privacy_authorship_registers_nothing():
    # Registration is a spec-level act (P1 Contract out §3, rule 4) and there is no
    # run-time registration call. Reloading the module must not grow P1's table.
    before = len(EVENT_TYPES)
    importlib.reload(authorship)
    from database_agent.events import EVENT_TYPES as after_table
    assert len(after_table) == before == 35
    assert not [n for n, v in vars(authorship).items()
                if callable(v) and n.lower().startswith("register")]


def test_p1s_registry_is_a_read_only_mapping_so_p7_could_not_add_one():
    with pytest.raises(TypeError):
        REGISTERED_EVENT_TYPES["classification_downgraded"] = None


# --- authorship: one place, and not a parameter -------------------------------

def test_subsystem_is_p7_and_event_defaults_always_stamps_it():
    assert SUBSYSTEM == "P7"
    for name in P7_EVENT_TYPES:
        assert event_defaults(**an_event(event_type=name))["subsystem"] == SUBSYSTEM


def test_a_caller_may_not_supply_or_override_the_subsystem():
    # M8: "The acting part authors; P1 writes." An author that is a parameter is not
    # an author. This is the check Task 21 counts on when it asserts there is exactly
    # one place in `privacy` where "P7" is written.
    with pytest.raises(MalformedEvent):
        event_defaults(**an_event(subsystem="P7"))
    with pytest.raises(MalformedEvent):
        event_defaults(**an_event(subsystem="P8"))


def test_component_version_defaults_and_a_caller_wins():
    assert event_defaults(**an_event())["component_version"] == COMPONENT_VERSION
    assert event_defaults(**an_event(component_version="9.9.9"))[
        "component_version"] == "9.9.9"


def test_observed_at_defaults_to_now_and_a_caller_supplied_value_wins():
    # §8.5's replay must be able to pin the clock; §8.2 requires "time of observation"
    # on every event, so it can never be absent.
    assert event_defaults(**an_event())["observed_at"] == FIXED_CLOCK
    fields = an_event()
    del fields["observed_at"]
    assert event_defaults(**fields)["observed_at"]


def test_event_defaults_writes_nothing(p7_conn):
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    event_defaults(**an_event())
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before
    assert "conn" not in event_defaults.__code__.co_varnames


# --- what the helper accepts, and what it refuses -----------------------------

def test_a_ninth_p7_looking_name_is_refused_here_and_at_p1s_writer(p7_conn):
    with pytest.raises(UnregisteredEventType):
        event_defaults(**an_event(event_type=UNREGISTERED))
    with pytest.raises(UnregisteredEventType):
        append_event(p7_conn, event_type=UNREGISTERED, subsystem=SUBSYSTEM,
                     component_version=COMPONENT_VERSION, observed_at=FIXED_CLOCK,
                     explanation="{}")


def test_another_parts_registered_name_is_refused_by_p7s_helper(p7_conn):
    # P8's event is valid at P1's writer and is not P7's to author. A helper that
    # stamped subsystem="P7" onto it would produce a true-looking row naming the
    # wrong actor.
    assert ANOTHER_PARTS_EVENT in EVENT_TYPES
    with pytest.raises(UnregisteredEventType):
        event_defaults(**an_event(event_type=ANOTHER_PARTS_EVENT))


def test_a_field_p1_has_no_column_for_is_refused():
    # The largest shape decision in this part: §8.4's audit record has thirteen
    # fields `events` has no column for. They go into `explanation` as canonical JSON
    # (Task 10), never into a field name P1 would reject.
    for absent in ("release_id", "audit_id", "policy_version", "outcome"):
        with pytest.raises(MalformedEvent):
            event_defaults(**an_event(**{absent: "x"}))


def test_every_one_of_8_2s_eleven_fields_passes_through():
    passable = [n for n in EVENT_FIELDS
                if n not in ("event_type", "subsystem", "component_version")]
    fields = an_event(**{n: "v" for n in passable if n != "observed_at"})
    defaults = event_defaults(**fields)
    for name in passable:
        assert name in defaults, name


def test_the_five_correction_fields_pass_through():
    # §8.7's columns ride beside §8.2's eleven on a user-action event. Task 16's
    # reclassify needs all five and this helper is its only writer path.
    defaults = event_defaults(**an_event(
        event_type=CLASSIFICATION_SUPERSEDED, correction_scope="file",
        correction_subject="file-1", polarity="reject", proposal_class="privacy",
        basis_key='{"file_id": "file-1"}'))
    for name in CORRECTION_FIELDS:
        assert name in defaults, name


def test_base_event_type_is_refused_because_all_eight_carry_no_base():
    # P1 stores it; P7 refuses it. None of the eight is a typed specialization of one
    # of §8.2's nineteen, so a caller supplying one asserts a relationship the
    # registration does not record.
    with pytest.raises(MalformedEvent):
        event_defaults(**an_event(base_event_type="extraction"))


# --- the round trip, against the real writer ----------------------------------

def test_p1_accepts_an_event_of_each_of_the_eight_types(p7_conn):
    for name in P7_EVENT_TYPES:
        append_event(p7_conn, **event_defaults(**an_event(event_type=name)))
    rows = p7_conn.execute(
        "SELECT event_type, subsystem, base_event_type FROM events "
        "ORDER BY event_id").fetchall()
    assert [r["event_type"] for r in rows] == list(P7_EVENT_TYPES)
    assert {r["subsystem"] for r in rows} == {SUBSYSTEM}
    assert {r["base_event_type"] for r in rows} == {None}


def test_p1_refuses_a_p7_event_with_an_empty_explanation(p7_conn):
    # §8.2's "structured explanation or evidence reference" is where §8.4's
    # consent-aware record lives. P1 rejects None and "", so a P7 event without one
    # is unwritable rather than merely discouraged.
    with pytest.raises(MalformedEvent):
        append_event(p7_conn, **event_defaults(**an_event(explanation="")))
```

- [ ] **Step 3: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_authorship.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy'`. `pyproject.toml` already carries
`pythonpath = ["src"]` and `[tool.setuptools.packages.find] where = ["src"]`, so the package becomes
importable the moment `src/privacy/__init__.py` exists and no build-configuration change is needed.
Collection fails on the first import, so no test runs.

- [ ] **Step 4: Write `src/privacy/__init__.py`**

```python
# src/privacy/__init__.py
"""P7 — the privacy and consent gate (§8.4).

The only door through which file content may reach a model or an external connector.
Five handling classes, four operation modes, nine always-local items, six releasable
item kinds, one `Gate.release` with three branches, and a consent-aware audit record
appended before any release is returned.

The package marker re-exports nothing yet: `Gate` and the three decision types arrive
with `gate.py`. `src/evidence_shape/__init__.py` and `src/extractors/__init__.py` are
the same shape, and a marker that imported a module later tasks have not written
would make every task before that one uncollectable.
"""
```

- [ ] **Step 5: Write `src/privacy/authorship.py`**

```python
# src/privacy/authorship.py
"""P7 authors its events; P1 writes them (M8). The name "P7" is written here, once.

Two rules pull in opposite directions and both are enforced in this module.

**Registration is a SPEC-level act, so this package cannot perform one.** P7's eight
event types are already in P1's frozen `_REGISTERED` table, compiled from this SPEC
under the comment "P7 SPEC, Cross-cutting answers -> Provenance. Eight." There is no
run-time registration call anywhere in P1, and there is none here: the eight names
below are ASSERTED by this part's tests, never added. None collides with §8.2's
nineteen reserved names, and P1 checks that at import, so a collision is an
ImportError rather than a run-time rejection.

**Authorship is a run-time act, so this package performs it in exactly one place.**
M8: "The acting part authors; P1 writes. P1 appends no event on its own initiative."
`event_defaults` stamps `subsystem = SUBSYSTEM` and refuses a caller who supplies
one, because an author that is a parameter is not an author. Task 21 asserts there is
no second place under `src/privacy/` where that value is written.

This module opens no connection and appends nothing. `event_defaults` returns a plain
mapping for a caller to hand to `database_agent.events.append_event`, so there is no
code path in which importing P7 writes to the log.
"""
from __future__ import annotations

from datetime import datetime, timezone

from database_agent.events import (
    CORRECTION_FIELDS, EVENT_FIELDS, MalformedEvent, REGISTERED_EVENT_TYPES,
    UnregisteredEventType,
)

#: §8.2's "responsible subsystem", for every event this part authors. THE one place.
SUBSYSTEM: str = "P7"

#: §8.2's "extractor or model version" slot, for a part that is neither. P7's own
#: package version, and the default a caller may override for a replay (§8.5).
COMPONENT_VERSION: str = "0.1.0"

#: A classification was assigned to a (file_id, content_hash). D2 makes P7's record
#: authoritative, so this event is the record OF the record, not of a write to P6.
CLASSIFICATION_ASSIGNED: str = "classification_assigned"

#: A classification was superseded — including by a user reclassification (§8.4's
#: "revised by the user"). §8.2 forbids overwriting: both records remain inspectable.
CLASSIFICATION_SUPERSEDED: str = "classification_superseded"

#: A privacy/consent policy version was set. §8.8 puts "Privacy and model-consent
#: policies" inside the plan version, so a change must be diffable, which needs a row.
POLICY_SET: str = "policy_set"

#: Consent was granted for a scope. §8.4's four options are the user's, not P7's.
CONSENT_GRANTED: str = "consent_granted"

#: Consent was withdrawn. Forward-only: §8.4 requires the product to say what already
#: left the device, which is unsatisfiable once the send record is erasable.
CONSENT_REVOKED: str = "consent_revoked"

#: Content was released to a model. §8.4: "Every model call should be recorded in a
#: consent-aware audit record" — every, with no exemption for a local model.
MODEL_RELEASE: str = "model_release"

#: A release was refused. Appended on the strength of §8.2's "Every significant event
#: affecting a file" and §8.6's requirement that the UI show what was deferred and why.
MODEL_RELEASE_DENIED: str = "model_release_denied"

#: The gate asked the user. §8.4: "the user should see that requirement and choose".
CONSENT_REQUESTED: str = "consent_requested"

#: The eight, in the SPEC's own order (Cross-cutting answers -> Provenance).
P7_EVENT_TYPES: tuple[str, ...] = (
    CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, POLICY_SET,
    CONSENT_GRANTED, CONSENT_REVOKED, MODEL_RELEASE, MODEL_RELEASE_DENIED,
    CONSENT_REQUESTED,
)

#: What a caller may pass through: §8.2's eleven minus the three this module owns,
#: plus §8.7's five correction columns. `base_event_type` is P1-writable and is NOT
#: here: all eight of P7's names carry `base = None`, so a caller supplying one is
#: asserting a relationship the registration does not record.
_PASSTHROUGH: frozenset[str] = frozenset(
    set(EVENT_FIELDS) | set(CORRECTION_FIELDS)
) - {"event_type", "subsystem"}

#: The fields this module fills and a caller may not: authorship itself.
_AUTHORED: tuple[str, ...] = ("subsystem",)


def event_defaults(*, event_type: str, **fields) -> dict[str, object]:
    """§8.2's authorship fields for one P7 event, ready for P1's `append_event`.

    Writes nothing and takes no connection. Raises P1's own exceptions rather than
    inventing a third vocabulary for the same refusal: an unknown or authored field
    is `MalformedEvent`, an event type outside P7's eight is `UnregisteredEventType`.

    `explanation` is deliberately not defaulted. P1's writer requires it and rejects
    the empty string, so every P7 event carries a non-empty "structured explanation or
    evidence reference" (§8.2) by construction — and that column is where §8.4's
    consent-aware record lives, since `events` has no column for thirteen of its
    fields. A default here would let an event ship with placeholder prose in the one
    column the audit record needs.
    """
    if event_type not in P7_EVENT_TYPES:
        raise UnregisteredEventType(
            f"{event_type!r} is not one of P7's eight declared event types "
            f"{P7_EVENT_TYPES}. Registration is a spec-level act (P1 Contract out "
            "§3, rule 4): a new P7 event is a SPEC revision, and an event another "
            "part declared is that part's to author (M8)."
        )
    for name in _AUTHORED:
        if name in fields:
            raise MalformedEvent(
                f"{name} is authored by this module and is not a parameter. M8: "
                '"the acting part authors; P1 writes." An author a caller may set '
                "is not an author."
            )
    unknown = sorted(set(fields) - _PASSTHROUGH)
    if unknown:
        raise MalformedEvent(
            f"{unknown} are not among §8.2's eleven event fields (MINOR 1) or §8.7's "
            "five correction columns; P7 adds no column to `events` and does not ask "
            "P1 to. §8.4's audit fields with no column go into `explanation` as "
            "canonical JSON (B5)."
        )
    return {
        "event_type": event_type,
        "subsystem": SUBSYSTEM,
        "component_version": COMPONENT_VERSION,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
```

- [ ] **Step 6: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_authorship.py -v`
Expected: PASS — 19 passed

- [ ] **Step 7: Run P1–P5 and confirm P7 broke nothing**

Run: `pytest tests/ -q`
Expected: PASS — every pre-existing test still green. P7 created `src/privacy/` and `tests/p7/` and
modified no file belonging to another part: not `pyproject.toml`, not `tests/conftest.py`, and
nothing under `src/database_agent/`, `src/scan_agent/`, `src/evidence_shape/`, `src/extractors/` or
`src/eval_harness/`.

- [ ] **Step 8: Commit**

```bash
git add src/privacy/__init__.py src/privacy/authorship.py tests/p7/conftest.py tests/p7/test_p7_authorship.py
git commit -m "feat(P7): package skeleton, and the eight event types asserted against P1's frozen registry"
```

---

---

### Task 2: The closed vocabularies, and the four words with `protected` in them

**Files:**
- Create: `src/privacy/vocabulary.py`
- Test: `tests/p7/test_p7_vocabulary.py`

**Interfaces:**
- Consumes: `scan_agent.exclusion.LABEL_UNTOUCHED_PROTECTED: str`, `.REASON_PROTECTED_CONTAINER: str`
  — imported **in the test only**, to pin the distinction. `src/privacy/` imports neither, and
  `privacy.vocabulary` binds no value equal to either.
- Produces (`vocabulary.py`):
  - `HANDLING_CLASSES: tuple[str, ...]` (5), `HANDLING_CLASS_LABELS: Mapping[str, str]` (added — the
    design's own five lines).
  - `OPERATION_MODES: tuple[str, ...]` (4), `MODE_SEMANTICS: Mapping[str, str]` (§8.4 verbatim).
  - `ALWAYS_LOCAL: tuple[str, ...]` (9).
  - `ITEM_KINDS: tuple[str, ...]` (6).
  - `DENIAL_REASONS: tuple[str, ...]` (8).
  - `CONSENT_OPTIONS: tuple[str, ...]` (4).
  - `DISPLAY_FACETS: tuple[str, ...]` (5).
  - `CLASSIFICATION_BASES: tuple[str, ...]` (3).
  - `AUDIT_OUTCOMES: tuple[str, ...]` (3).
  - `OPEN_QUESTIONS: Mapping[int, str]` (added — the SPEC's eleven, held open).
  - `OutOfVocabulary`.
  - `check_handling_class(value) -> str`, `check_mode(value) -> str`,
    `check_item_kind(value) -> str`, `check_denial_reason(value) -> str`.

**Done-means:** 1.

**Why this is Task 2 and not later.** Every subsequent task validates against one of these tuples,
and a vocabulary that arrives after its consumers is a vocabulary each consumer has already spelled
its own way. D2's warning from P4's equivalent task applies verbatim in shape: six callers produce
six spellings and nothing has a stable key.

**A value outside the set is a load error, not a fallback.** The SPEC states it once and it is the
whole point of the four `check_*` functions: *"A value outside this set is a load error, not a
fallback."* The refusal message therefore names the closed set and **does not suggest a nearest
match**. `check_handling_class("public")` must not mention `public_low`. A suggestion is how a
misspelling becomes a silent downgrade, and a silent downgrade in this vocabulary is the failure
§8.6 forbids by name.

**Four checkers, not nine, and that is the skeleton's contract.** The four vocabularies with a
checker are the four a caller supplies a value into from outside P7: a handling class arrives from a
detector or a user, a mode from a policy, an item kind from P8's request, a denial reason from P7's
own branches under test. `CONSENT_OPTIONS`, `DISPLAY_FACETS`, `CLASSIFICATION_BASES` and
`AUDIT_OUTCOMES` are consumed as membership tests by the tasks that own them (5, 10, 14). Adding
five more checkers would be five more names for Task 21 to introspect and five more places for the
same refusal to be spelled differently.

**No threshold, no ceiling, no number.** This module contains no `int` and no `float` at all, and a
test asserts it by walking the module namespace. §8.6 names the knobs, states they are
*"configurable"*, and gives no values; the SPEC's *Deferred* table puts *"Numeric values for every
ceiling"* outside this contract. A number here would be the first invented value in the part.

**The five spellings, pinned side by side.** The skeleton's heading counts four words with
`protected` in them and its body enumerates five strings; the body is right, and this task follows
it. The five are P7's `protected` flag (Task 3's boolean field), P7's `protected_cloud_target` and
`protected_records_template` denial reasons, P3's `untouched_protected` label and P3's
`protected_container` exclusion reason. Two facts make the distinction load-bearing rather than
tidy:

- **P3's two are about *reading*, P7's three are about *release*.** A protected container is a
  filesystem rule: P3 *"does not descend into one, does not stat its contents, does not hash a byte
  of it, and does not create a `files` row for anything inside it"*. A file inside one never acquires
  the `(file_id, content_hash)` pair P7 keys on, so `Gate.release` cannot be asked about it. The
  guarantee is structural, not a check P7 performs.
- **P7's `Denial.reason` vocabulary contains no bare `protected`.** It contains
  `protected_cloud_target` — a protected file with a cloud target — and `protected_records_template`
  — §7.3's residual template, whose design sentence is *"it should normally remain local-only and
  must not cause filenames or content to be exposed in model prompts"*. A normalization pass that
  collapsed either onto `protected` would produce a denial that cannot say which rule fired.

**`filename` is the one item kind the design's own sentence does not list, and it is flagged in
code.** §8.4 permits *"selected excerpts, redacted identifiers, candidate labels, non-sensitive
metadata, and evidence references"* — five. The sixth, `filename`, comes from the SPEC's flagged
reading: §8.4 puts *paths* in the always-local set, §7.7 puts the filename in the residual dossier,
and §7.3 forbids filenames in prompts **only** for Protected Records, which is vacuous under any
reading that already forbade them everywhere. The SPEC calls this *"the one place where the contract
resolves an apparent conflict rather than deferring it, because P8 and P11 cannot build without an
answer"*, and it is Open question 2. The test asserts `filename` is the only member of `ITEM_KINDS`
absent from §8.4's five, and `OPEN_QUESTIONS[2]` keeps the question open.

**What this task does not do.** It publishes no detection rule, no regex, no gazetteer, no filename
pattern and no keyword list. SPEC *Deferred*: *"The design states *what* is protected and never *how
it is recognised*. The detector rule set, its signals, and its thresholds are hand-authored. P7
publishes the vocabulary the detectors write into."* This module is that vocabulary and nothing else.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_vocabulary.py
"""§8.4's closed vocabularies, and the five strings that share the stem "protected".

Two kinds of assertion live here. Most pin a tuple against the design's own words, in
the design's own order, so a later edit is a red test and not an editorial choice. The
rest pin the boundary: an out-of-vocabulary value is a load error that suggests no
neighbour, no member is a number, and nothing in this module is one of P3's strings
wearing P7's clothes.

Where a vocabulary can be DERIVED from a design sentence mechanically, it is. A test
that retypes the nine always-local items proves the author can retype; a test that
splits the design's sentence proves the identifiers are the design's words.
"""
from collections.abc import Mapping

import pytest

from scan_agent.exclusion import LABEL_UNTOUCHED_PROTECTED, REASON_PROTECTED_CONTAINER

import privacy.vocabulary as vocabulary
from privacy.vocabulary import (
    ALWAYS_LOCAL, AUDIT_OUTCOMES, CLASSIFICATION_BASES, CONSENT_OPTIONS,
    DENIAL_REASONS, DISPLAY_FACETS, HANDLING_CLASSES, HANDLING_CLASS_LABELS,
    ITEM_KINDS, MODE_SEMANTICS, OPEN_QUESTIONS, OPERATION_MODES, OutOfVocabulary,
    check_denial_reason, check_handling_class, check_item_kind, check_mode,
)

#: §8.4, verbatim. The nine names are derived from this sentence rather than retyped.
ALWAYS_LOCAL_SENTENCE = (
    "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, "
    "user edits, group memberships, and raw sensitive values should remain local."
)

#: §8.4, verbatim. The five facets are derived from this sentence.
DISPLAY_SENTENCE = (
    "The user can choose whether names, previews, thumbnails, OCR text, or "
    "location data are shown."
)

#: §8.4's compact dossier, verbatim. Five kinds; `filename` is not among them.
DOSSIER_SENTENCE = (
    "selected excerpts, redacted identifiers, candidate labels, non-sensitive "
    "metadata, and evidence references"
)


def _identifiers(listed: str) -> tuple[str, ...]:
    """Split a design list into P7's snake_case identifiers, mechanically."""
    out = []
    for part in listed.split(","):
        word = part.strip().removeprefix("and ").removeprefix("or ")
        out.append(word.lower().replace(" ", "_"))
    return tuple(out)


# --- the five handling classes -----------------------------------------------

def test_the_five_classes_are_the_designs_five_in_the_designs_order():
    assert HANDLING_CLASSES == (
        "public_low", "personal_non_sensitive", "sensitive_personal",
        "highly_sensitive_credential_bearing", "unreadable_unclassified",
    )


def test_each_identifier_is_the_designs_own_line():
    # "The system should classify data into handling classes before LLM escalation:"
    # then five lines. Without this mapping the five identifiers are five words a P7
    # author chose; with it they are the design's, spelled in snake_case.
    assert tuple(HANDLING_CLASS_LABELS[name] for name in HANDLING_CLASSES) == (
        "Public or low sensitivity",
        "Personal but non-sensitive",
        "Sensitive personal",
        "Highly sensitive or credential-bearing",
        "Unreadable or unclassified",
    )
    assert tuple(HANDLING_CLASS_LABELS) == HANDLING_CLASSES


def test_no_sixth_class_was_added():
    assert len(HANDLING_CLASSES) == 5
    assert len(set(HANDLING_CLASSES)) == 5


def test_an_out_of_vocabulary_class_is_a_load_error_that_suggests_no_neighbour():
    # "A value outside this set is a load error, not a fallback." A suggestion is how
    # a misspelling becomes a silent downgrade, which is what §8.6 forbids by name.
    with pytest.raises(OutOfVocabulary) as caught:
        check_handling_class("public")
    assert "public_low" not in str(caught.value)
    with pytest.raises(OutOfVocabulary):
        check_handling_class("")
    with pytest.raises(OutOfVocabulary):
        check_handling_class(None)
    assert check_handling_class("unreadable_unclassified") == "unreadable_unclassified"


# --- the four operation modes ------------------------------------------------

def test_the_four_modes_are_the_designs_four_in_order():
    assert OPERATION_MODES == ("offline", "local_model", "hybrid", "cloud_assisted")


def test_mode_semantics_reproduces_8_4s_four_sentences_verbatim():
    # Verbatim so a later paraphrase is a failing test. "Sensitive files remain local"
    # is the whole of what `hybrid` promises; a reworded version could promise less.
    assert MODE_SEMANTICS == {
        "offline":
            "No content leaves the device; only local rules and local models may run.",
        "local_model":
            "Local extraction plus a user-installed local LLM for eligible dossiers.",
        "hybrid":
            "Sensitive files remain local; non-sensitive bounded dossiers may use a "
            "cloud LLM.",
        "cloud_assisted":
            "User explicitly permits selected corpus areas to use a cloud model.",
    }
    assert tuple(MODE_SEMANTICS) == OPERATION_MODES


def test_an_out_of_vocabulary_mode_is_refused():
    with pytest.raises(OutOfVocabulary):
        check_mode("cloud")
    assert check_mode("offline") == "offline"


# --- the always-local nine ---------------------------------------------------

def test_the_nine_always_local_items_are_the_designs_own_words():
    listed = ALWAYS_LOCAL_SENTENCE.split(" should remain local.")[0]
    assert ALWAYS_LOCAL == _identifiers(listed)
    assert len(ALWAYS_LOCAL) == 9


def test_nothing_in_the_always_local_set_is_a_releasable_item_kind():
    # "Nothing in this set can be named as a releasable item kind. The gate has no
    # code path that materialises one." The vocabulary makes it unnameable; Task 7
    # makes it a denial.
    assert set(ALWAYS_LOCAL).isdisjoint(ITEM_KINDS)


def test_paths_are_always_local_and_filename_is_a_separate_string():
    # Open question 2, and the SPEC's flagged reading: directory path is not filename.
    assert "paths" in ALWAYS_LOCAL
    assert "filename" in ITEM_KINDS
    assert "filename" not in ALWAYS_LOCAL


# --- the six releasable item kinds -------------------------------------------

def test_the_six_item_kinds_are_the_specs_six_in_order():
    assert ITEM_KINDS == (
        "excerpt", "redacted_identifier", "candidate_label", "metadata_field",
        "evidence_reference", "filename",
    )


def test_filename_is_the_only_kind_the_designs_own_sentence_does_not_list():
    # §8.4 permits five. P7 singularises each and spells "non-sensitive metadata" as
    # `metadata_field`, because the item carries ONE named field. The sixth kind
    # corresponds to no phrase in that sentence: it is the SPEC's flagged reading of
    # §7.3 versus §7.7, adopted because P8 and P11 cannot build without an answer,
    # and held open as Open question 2 rather than treated as settled.
    from_design = {
        "excerpt": "selected excerpts",
        "redacted_identifier": "redacted identifiers",
        "candidate_label": "candidate labels",
        "metadata_field": "non-sensitive metadata",
        "evidence_reference": "evidence references",
    }
    assert [k for k in ITEM_KINDS if k not in from_design] == ["filename"]
    for phrase in from_design.values():
        assert phrase in DOSSIER_SENTENCE, phrase
    assert "filename" not in DOSSIER_SENTENCE
    assert 2 in OPEN_QUESTIONS


def test_an_out_of_vocabulary_item_kind_is_refused():
    with pytest.raises(OutOfVocabulary):
        check_item_kind("whole_document")
    assert check_item_kind("excerpt") == "excerpt"


# --- the eight denial reasons and the five protected spellings ---------------

def test_the_eight_denial_reasons_are_the_specs_eight_in_order():
    assert DENIAL_REASONS == (
        "protected_cloud_target", "unclassified", "policy_revoked",
        "protected_records_template", "whole_document_requested",
        "dossier_over_budget", "always_local_item", "mode_forbids_target",
    )
    assert check_denial_reason("unclassified") == "unclassified"
    with pytest.raises(OutOfVocabulary):
        check_denial_reason("protected")


def test_the_five_protected_spellings_coexist_and_no_two_are_equal():
    # P3's two are about READING and P7's three are about RELEASE. A file inside a
    # protected container has no `files` row, so the gate cannot be asked about it;
    # a protected file under `hybrid` has one and is denied a cloud target.
    spellings = (
        "protected",                     # P7's flag on ClassificationRecord (Task 3)
        "protected_cloud_target",        # P7's denial reason
        "protected_records_template",    # P7's denial reason (§7.3)
        LABEL_UNTOUCHED_PROTECTED,       # P3: "untouched_protected"
        REASON_PROTECTED_CONTAINER,      # P3: "protected_container"
    )
    assert len(set(spellings)) == 5
    assert all("protected" in s for s in spellings)
    assert LABEL_UNTOUCHED_PROTECTED == "untouched_protected"
    assert REASON_PROTECTED_CONTAINER == "protected_container"


def test_no_p7_vocabulary_contains_a_bare_protected():
    for closed in (HANDLING_CLASSES, OPERATION_MODES, ALWAYS_LOCAL, ITEM_KINDS,
                   DENIAL_REASONS, CONSENT_OPTIONS, DISPLAY_FACETS,
                   CLASSIFICATION_BASES, AUDIT_OUTCOMES):
        assert "protected" not in closed


def test_p7s_vocabulary_module_holds_none_of_p3s_strings():
    # The test imports P3 to pin the distinction; `src/privacy/` imports neither
    # constant and holds no copy of either literal.
    p3 = {LABEL_UNTOUCHED_PROTECTED, REASON_PROTECTED_CONTAINER, "protected container"}

    def strings_in(value):
        if isinstance(value, str):
            return {value}
        if isinstance(value, tuple):
            return {v for v in value if isinstance(v, str)}
        if isinstance(value, Mapping):
            return {v for v in value.values() if isinstance(v, str)}
        return set()

    for name, value in vars(vocabulary).items():
        if name.startswith("_"):
            continue
        assert not strings_in(value) & p3, name


# --- consent options, display facets, bases, outcomes ------------------------

def test_the_four_consent_options_are_8_4s_own_four():
    # "the user should see that requirement and choose whether to allow a local
    # model, a cloud model, a redacted prompt, or no model use" -- those four,
    # exactly, and in that order.
    assert CONSENT_OPTIONS == (
        "local_model", "cloud_model", "redacted_prompt", "no_model_use")


def test_local_model_is_both_a_mode_and_a_consent_option_and_that_is_not_a_bug():
    # §8.4 names it in both lists. Open question 6 asks whether a local call is a
    # consent event or only an audit event; the shared string is where that question
    # touches the code, and nothing here answers it.
    assert "local_model" in OPERATION_MODES
    assert "local_model" in CONSENT_OPTIONS
    assert 6 in OPEN_QUESTIONS


def test_the_five_display_facets_are_the_designs_own_words():
    listed = DISPLAY_SENTENCE.split("whether ")[1].split(" are shown.")[0]
    assert DISPLAY_FACETS == _identifiers(listed)
    assert DISPLAY_FACETS == (
        "names", "previews", "thumbnails", "ocr_text", "location_data")


def test_three_classification_bases_and_three_audit_outcomes():
    assert CLASSIFICATION_BASES == ("detector", "safety_domain", "user")
    assert AUDIT_OUTCOMES == ("released", "denied", "consent_requested")


def test_unreadable_unclassified_is_a_class_and_unclassified_is_a_denial_reason():
    # D2: "Unreadable or unclassified is a GATE OUTCOME, not a file fact." The class
    # is what `resolve_class` returns to a caller; the denial reason is what the gate
    # says when it has no classification to release against. Two strings, one idea,
    # and neither may be written into `files.sensitivity_state`.
    assert "unreadable_unclassified" in HANDLING_CLASSES
    assert "unclassified" in DENIAL_REASONS
    assert "unclassified" not in HANDLING_CLASSES
    assert "unreadable_unclassified" not in DENIAL_REASONS


# --- the boundary: eleven questions, and no numbers --------------------------

def test_all_eleven_open_questions_are_present_and_unanswered():
    assert set(OPEN_QUESTIONS) == set(range(1, 12))
    for number, question in OPEN_QUESTIONS.items():
        assert isinstance(question, str) and question.strip(), number


def test_the_module_holds_no_number_at_all():
    # "no numeric ceiling, no retention period" -- the SPEC's Deferred table puts
    # "Numeric values for every ceiling" outside this contract, and §8.6 gives none.
    # A number here would be the first invented value in the part.
    for name, value in vars(vocabulary).items():
        if name.startswith("_"):
            continue
        assert not isinstance(value, (int, float)), name


def test_every_vocabulary_is_a_tuple_of_unique_nonempty_strings():
    for closed in (HANDLING_CLASSES, OPERATION_MODES, ALWAYS_LOCAL, ITEM_KINDS,
                   DENIAL_REASONS, CONSENT_OPTIONS, DISPLAY_FACETS,
                   CLASSIFICATION_BASES, AUDIT_OUTCOMES):
        assert isinstance(closed, tuple)
        assert len(set(closed)) == len(closed)
        assert all(isinstance(v, str) and v and v == v.strip() for v in closed)


def test_the_mappings_are_read_only_so_a_caller_cannot_add_a_member():
    with pytest.raises(TypeError):
        MODE_SEMANTICS["air_gapped"] = "no"
    with pytest.raises(TypeError):
        HANDLING_CLASS_LABELS["top_secret"] = "no"
    with pytest.raises(TypeError):
        OPEN_QUESTIONS[12] = "no"
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_vocabulary.py -v`
Expected: FAIL — `ImportError: cannot import name 'ALWAYS_LOCAL' from 'privacy.vocabulary'`, because
`src/privacy/vocabulary.py` does not exist yet and collection fails on the first import. `privacy`
itself imports, since Task 1 created the package.

- [ ] **Step 3: Write `src/privacy/vocabulary.py`**

```python
# src/privacy/vocabulary.py
"""§8.4's closed vocabularies, and the eleven questions P7 holds open.

Closed means a caller may not add a value. SPEC §1: "A value outside this set is a
load error, not a fallback." Adding a member is a P7 contract revision, not an
implementation decision, and the four `check_*` functions below refuse an outsider
WITHOUT suggesting a neighbour -- a suggestion is how a misspelling becomes a silent
downgrade, and a silent downgrade in this vocabulary is the failure §8.6 names:
"Cost exhaustion must never turn into lower-quality automatic classification."

Every member is the design's, in the design's order, and nothing here is invented.
Where the design writes prose, the prose is carried beside the identifier
(`HANDLING_CLASS_LABELS`, `MODE_SEMANTICS`) so a later paraphrase is a failing test.

**This module holds no detection rule and no number.** SPEC *Deferred*: "The design
states *what* is protected and never *how it is recognised*. The detector rule set,
its signals, and its thresholds are hand-authored. P7 publishes the vocabulary the
detectors write into." There is no regex, no gazetteer, no filename pattern, no
keyword list, no threshold and no ceiling; §8.6 names the knobs, calls them
"configurable", and gives no values.

**Five strings share the stem "protected" and no two of them are the same word.**
P7's `protected` flag (`classification.ClassificationRecord`), P7's
`protected_cloud_target` and `protected_records_template` denial reasons, P3's
`untouched_protected` exclusion label and P3's `protected_container` exclusion reason.
P3's two are about READING -- a file inside a protected container never acquires the
(file_id, content_hash) pair the gate keys on, so `Gate.release` cannot be asked about
it. P7's three are about RELEASE, which is a policy the user can override through
consent, and that is exactly what makes it a different refusal. `src/privacy/` imports
neither of P3's constants; the distinction is pinned in `tests/p7/test_p7_vocabulary.py`.
"""
from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType


class OutOfVocabulary(ValueError):
    """A value outside a closed set. SPEC §1: a load error, not a fallback."""


def _check(value: object, closed: tuple[str, ...], what: str) -> str:
    """Refuse an outsider by naming the closed set, never a nearest match."""
    if not isinstance(value, str) or value not in closed:
        raise OutOfVocabulary(
            f"{value!r} is not one of the {len(closed)} {what} the design defines "
            f"{closed}. §8.4's vocabularies are closed: a value outside the set is a "
            "load error, not a fallback, and adding a member is a P7 contract "
            "revision rather than an implementation decision."
        )
    return value


# --- §8.4: five handling classes, assigned before LLM escalation -------------

#: "The system should classify data into handling classes before LLM escalation".
#: The five, in the design's order. Absence of a classification resolves to the last
#: of them and NEVER to the first -- see `classification.resolve_class`.
HANDLING_CLASSES: tuple[str, ...] = (
    "public_low",
    "personal_non_sensitive",
    "sensitive_personal",
    "highly_sensitive_credential_bearing",
    "unreadable_unclassified",
)

#: The design's own five lines, so the snake_case identifiers above are traceable to
#: the words that define them rather than to a P7 author's choice of spelling.
HANDLING_CLASS_LABELS: Mapping[str, str] = MappingProxyType({
    "public_low": "Public or low sensitivity",
    "personal_non_sensitive": "Personal but non-sensitive",
    "sensitive_personal": "Sensitive personal",
    "highly_sensitive_credential_bearing": "Highly sensitive or credential-bearing",
    "unreadable_unclassified": "Unreadable or unclassified",
})


def check_handling_class(value: object) -> str:
    return _check(value, HANDLING_CLASSES, "handling classes")


# --- §8.4: four operation modes ----------------------------------------------

#: "The product should support clear operation modes". Four, in the design's order.
OPERATION_MODES: tuple[str, ...] = (
    "offline", "local_model", "hybrid", "cloud_assisted",
)

#: The design's four sentences, verbatim. A paraphrase can promise less than the
#: original -- "Sensitive files remain local" is the whole of what `hybrid` promises --
#: so the words are pinned and a rewording is a failing test.
MODE_SEMANTICS: Mapping[str, str] = MappingProxyType({
    "offline":
        "No content leaves the device; only local rules and local models may run.",
    "local_model":
        "Local extraction plus a user-installed local LLM for eligible dossiers.",
    "hybrid":
        "Sensitive files remain local; non-sensitive bounded dossiers may use a "
        "cloud LLM.",
    "cloud_assisted":
        "User explicitly permits selected corpus areas to use a cloud model.",
})


def check_mode(value: object) -> str:
    return _check(value, OPERATION_MODES, "operation modes")


# --- §8.4: the always-local set ----------------------------------------------

#: "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS, user
#: edits, group memberships, and raw sensitive values should remain local." Nine, in
#: the design's order. Nothing here can be named as a releasable item kind, and Task 7
#: turns an attempt into the `always_local_item` denial.
ALWAYS_LOCAL: tuple[str, ...] = (
    "paths", "complete_extracted_text", "ocr_output", "file_hashes", "image_exif",
    "gps", "user_edits", "group_memberships", "raw_sensitive_values",
)

# --- §8.4: the compact dossier -----------------------------------------------

#: "the engine should send only a compact dossier relevant to the current question:
#: selected excerpts, redacted identifiers, candidate labels, non-sensitive metadata,
#: and evidence references." Five from that sentence; `filename` is the sixth and is
#: the SPEC's flagged reading -- §8.4 puts *paths* in the always-local set, §7.7 puts
#: the filename in the residual dossier, and §7.3 forbids filenames in prompts only
#: for Protected Records, which is vacuous under any reading that forbade them
#: everywhere. Adopted because P8 and P11 cannot build without an answer; held open as
#: Open question 2 rather than treated as settled.
ITEM_KINDS: tuple[str, ...] = (
    "excerpt", "redacted_identifier", "candidate_label", "metadata_field",
    "evidence_reference", "filename",
)


def check_item_kind(value: object) -> str:
    return _check(value, ITEM_KINDS, "releasable item kinds")


# --- §8.4 + §7.3 + §8.6: the eight denial reasons ----------------------------

#: SPEC Contract out §6, in the SPEC's order. `dossier_over_budget` is a backstop that
#: should never fire: M9 puts the ceiling and §8.6's four-rung ladder in P8, BEFORE
#: the call, because a gate-only check runs after the last point at which the dossier
#: could still be reduced. A `dossier_over_budget` denial in a running pipeline is a
#: P8 defect to fix, not a normal outcome.
#:
#: There is no bare `protected` here. `protected_cloud_target` is a protected file
#: with a cloud target; `protected_records_template` is §7.3's residual template,
#: which "should normally remain local-only and must not cause filenames or content
#: to be exposed in model prompts". Collapsing either onto `protected` would produce
#: a denial that cannot say which rule fired.
DENIAL_REASONS: tuple[str, ...] = (
    "protected_cloud_target", "unclassified", "policy_revoked",
    "protected_records_template", "whole_document_requested",
    "dossier_over_budget", "always_local_item", "mode_forbids_target",
)


def check_denial_reason(value: object) -> str:
    return _check(value, DENIAL_REASONS, "denial reasons")


# --- §8.4: the four consent options ------------------------------------------

#: "If a model needs text containing sensitive content, the user should see that
#: requirement and choose whether to allow a local model, a cloud model, a redacted
#: prompt, or no model use." Those four, exactly. `NeedsConsent` is a question only
#: the user can answer, and no caller may absorb it into an abstention (B2).
CONSENT_OPTIONS: tuple[str, ...] = (
    "local_model", "cloud_model", "redacted_prompt", "no_model_use",
)

# --- §8.4: the five configurable display facets ------------------------------

#: "The user can choose whether names, previews, thumbnails, OCR text, or location
#: data are shown." Where the design is silent on a default, W1 makes the more
#: redacting option the default -- that rule is Task 6's and no default lives here.
DISPLAY_FACETS: tuple[str, ...] = (
    "names", "previews", "thumbnails", "ocr_text", "location_data",
)

# --- SPEC §2 and §7: bases and outcomes --------------------------------------

#: SPEC §2's classification record: "basis  detector | safety_domain | user".
#: `safety_domain` is §3.15's: finance, identity, medical and legal material ship
#: first as safety domains, "meaning the system detects and protects them before any
#: cloud or automated placement decision is allowed". This is NOT P6's five-value
#: `origin` vocabulary (§3.1) and the two are never mapped onto one another here.
CLASSIFICATION_BASES: tuple[str, ...] = ("detector", "safety_domain", "user")

#: SPEC §7's audit record: "outcome  released | denied | consent_requested". Every
#: model call is recorded -- §8.4 says "Every model call" with no exemption for a
#: local model -- and denials and consent requests are recorded too, on §8.2's "Every
#: significant event affecting a file" and §8.6's requirement that the UI show what
#: has been deferred and why.
AUDIT_OUTCOMES: tuple[str, ...] = ("released", "denied", "consent_requested")


# --- the eleven questions the design leaves open -----------------------------

#: P7's SPEC Open questions 1-11, held open. An entry here means "still unanswered".
#: Task 21 reads this mapping and fails if any of them is answered in an
#: implementation instead of in a SPEC. Where the design leaves a value open -- a
#: threshold, a ceiling, an identifier class, a redaction transform, a detection rule,
#: a retention period -- this part holds a caller-supplied strategy or a required
#: keyword, never a number and never a list.
OPEN_QUESTIONS: Mapping[int, str] = MappingProxyType({
    1: "Is `protected` exactly the top two handling classes? §8.4 lists five classes "
       "and, separately, five kinds of material that enter a protected state "
       "immediately, without stating the relation. Neighbouring parts consume the "
       "flag and never infer it from the class.",
    2: "Filename versus path. §8.4 puts paths in the always-local set, §7.7 puts the "
       "filename in the residual dossier, and §7.3 forbids filenames in prompts only "
       "for Protected Records. The contract adopts the reading that makes §7.3 "
       "non-vacuous and flags it.",
    3: "What is a corpus area? `cloud_assisted` permits a cloud model for selected "
       "corpus areas. A scan root, a frozen tree node, an accepted group, a domain? "
       "Consent grants cannot be scoped until this is named.",
    4: "Deletion versus append-only. §8.4 gives the user the right to review and "
       "delete local derived data; §8.2 forbids updating or deleting an event. "
       "Which wins, what counts as derived, and are audit records themselves "
       "deletable? Tracked as I6.",
    5: "Does `unreadable_unclassified` permit a LOCAL model call? Reading escalation "
       "strictly denies local calls on unclassified files, which may block exactly "
       "the OCR-opaque screenshots §2.7 and §7.8 want a model to interpret.",
    6: "Is a local-model call a consent event or only an audit event? §8.4 audits "
       "every model call and offers a local model as one of the four consent "
       "options. The threshold at which a local call needs a prompt is unstated.",
    7: "Does repeated reclassification generalize? §8.7 allows a repeated residual "
       "destination to become a corpus-level preference; it does not say whether "
       "repeated privacy corrections may raise a sensitivity floor.",
    8: "May a replay bundle carry audit records and excerpt spans? §8.5 allows a "
       "metadata-safe representation and lists policy settings; whether a bundle "
       "intended to leave the machine may carry records that name excerpts is "
       "unstated.",
    9: "What is an external connector besides a model? §8.4 gates any model or "
       "external connector, but no non-model connector is named in the twelve parts. "
       "If one is added later, does it route through `Gate.release`?",
    10: "Retention. How long audit records, consent grants and superseded "
        "classifications are kept. The design states no retention period anywhere.",
    11: "Which of `offline` and `local_model` ships as the install default. W1 closes "
        "the floor -- the default must be one of those two and may never be `hybrid` "
        "or `cloud_assisted` -- and the design names no answer between them.",
})
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_vocabulary.py -v`
Expected: PASS — 26 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–2 green, and every pre-existing test still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/vocabulary.py tests/p7/test_p7_vocabulary.py
git commit -m "feat(P7): the nine closed vocabularies, and the five strings that share the stem protected"
```

---

---

### Task 3: The classification record, and absence resolving to `unreadable_unclassified`

**Files:**
- Create: `src/privacy/classification.py`
- Test: `tests/p7/test_p7_classification.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.CLASSIFICATION_BASES`, `.check_handling_class(value) -> str`,
  `.OutOfVocabulary`; `evidence_shape.observation.observation_key(*, content_hash, extractor_name,
  locator, raw_value) -> str`; `evidence_shape.store.runs_for_file(conn, file_id) ->
  list[ExtractionRun]`; `extractors.long_tail.POTENTIALLY_SENSITIVE: str`,
  `.sensitivity_signals_for(conn, run_id) -> list[sqlite3.Row]`;
  `evidence_shape.runs.COMPLETENESS` — consumed **in the test**, as the cross-check that the
  nine-value table names P4's nine and no tenth.
- Produces (`classification.py`):
  - `ClassificationRecord` — frozen: `file_id: str`, `content_hash: str`, `handling_class: str`,
    `protected: bool`, `basis: str`, `evidence_refs: tuple[str, ...]`, `reliability_state: str`,
    `observed_at: str`.
  - `CLASSIFICATION_FIELDS: tuple[str, ...]` — SPEC §2's eight, in SPEC §2's order.
  - `UnbackedClassification`.
  - `resolve_class(record: ClassificationRecord | None) -> str`.
  - `completeness_implies_unclassified(completeness) -> bool`.
  - `COMPLETENESS_RULE: Mapping[str, tuple[bool, str]]` (added — see below).
  - `sensitivity_signal_keys(conn, file_id) -> tuple[str, ...]` (added — see below).

**Done-means:** 2 (first half), and the input side of 6.

**Two readings of the `Consumes` block, stated so a reviewer can reject them rather than discover
them.** The skeleton lists `vocabulary.HANDLING_CLASSES` and `.CLASSIFICATION_BASES`. This module
imports `CLASSIFICATION_BASES` directly and reaches `HANDLING_CLASSES` **through Task 2's published
`check_handling_class`**, which is the checker over that exact tuple; importing both would give this
module two ways to say the same no, which is what Task 2's *"four checkers, not nine"* paragraph
argues against. `OutOfVocabulary` comes with them, because consuming a closed vocabulary without its
refusal type forces a second refusal vocabulary. Both are Task 2 products already in Task 2's
`Produces` list, so no new surface is created. The skeleton also lists
`evidence_shape.runs.COMPLETENESS`; the module deliberately does **not** import it, because the
requirement is that the mapping be *"stated explicitly per value rather than by an `in`-check over a
set the author guessed"* and deriving the table from P4's tuple is that `in`-check wearing a better
name. The tuple is consumed in the **test**, as the cross-check that the table covers P4's nine and
no tenth.

**`ClassificationRecord` is authoritative and it is keyed on bytes (D2).**
`(file_id, content_hash)` — on the hash, because *a classification is about BYTES* and new bytes at
a path are a new file version that inherits nothing. `files.sensitivity_state` is the projection of
this record onto the current row, and **this module does not write it**. Task 4 owns `mirror_state`
and P1's `set_sensitivity_state`; Task 3 owns the record. That split is not tidiness — it is what
keeps the next paragraph true.

**`Unreadable or unclassified` is a gate outcome and this is the module where that becomes
concrete.** `resolve_class` returns a string to a caller. There is no writer in this file: no
function takes a connection and inserts or updates, no name begins `set_`, `write_`, `record_`,
`mirror_` or `update_`, and `database_agent.files_table` is not imported. A test asserts each of
those by walking the module namespace. The reason is D2's: *"nothing has looked"* and *"this file
carries nothing"* must never be the same value in the same column, and the only durable way to hold
that apart is for the string that means the first to be produced by a decision function and by
nothing that can reach a column.

**The detector is unwritten, and the strongest available proof of that is a test.** D2 puts the rule
set behind an injection and no task in any plan produces one. Until one is supplied, every real file
resolves to `Denied(unclassified)`. The test that says so is
`test_a_file_with_every_value_marked_sensitive_still_has_no_classification`: P5 marks a value
`potentially sensitive` at emission, the signal is in the database, `sensitivity_signal_keys` returns
its `observation_key` — and the file still has no `ClassificationRecord`, so `resolve_class(None)`
still returns `unreadable_unclassified`. **A signal is not a class.** P5's own docstring says so:
*"Email addresses, message content and every VCF value are marked POTENTIALLY SENSITIVE at emission,
for P7 to act on. P5 assigns no handling class: section 8.4 gives classification to P7."*

**`sensitivity_signal_keys` is added, and it is not a detector.** Task 3's `Consumes` block lists
`POTENTIALLY_SENSITIVE`, `sensitivity_signals_for` and `runs_for_file` and its `Produces` block names
nothing that could consume them — an interface block with three unconsumed imports is incoherent. The
skeleton's prose settles the intent: *"The reader is keyed by `run_id` only, so the file-level walk is
`runs_for_file(conn, file_id)` → `sensitivity_signals_for(conn, run.run_id)`. P7 adds no reader to P5;
it composes the two P4 and P5 already publish."* The composition decides nothing: it applies no rule,
assigns no class, and returns the citation handles a detector would pass as `evidence_refs`. It
deduplicates while preserving first-seen order, because a re-run of the same extractor at the same
content hash produces the same `observation_key`, and the same key listed twice would make a
classification look doubly backed by one observation.

**`evidence_refs` holds `observation_key` values and refuses anything shaped like an
`observation_id` (M14).** *"The key, not the id, is what makes that durable"* — a per-row
`observation_id` dies when the extractor is upgraded, so a negative example recorded today would
silently stop resolving and the same false protection would return. The shape check is **derived from
P4's own function** rather than hard-coded: the module mints one probe key at import and reads the
algorithm prefix and digest length off it, so a change in `evidence_shape.canonical.sha256_of`
propagates instead of drifting. It was introspected: `observation_key(...)` returns
`"sha256:" + 64 lowercase hex` (71 characters) and `evidence_shape.store.new_id()` — the minter of
`observation_id` — returns `str(uuid.uuid4())`, so the two handles are mechanically
distinguishable. P1's `content_hash` carries **no** algorithm prefix, which the test also pins.

**`evidence_refs` is required non-empty for `basis = "detector"` and for that basis only.** SPEC §2:
*"`evidence_refs` is non-empty for any `basis = detector` classification"*, on §3.1's principle that
every fact preserves where it came from. `basis = "user"` needs none — the user's act is the
evidence, and §8.4 makes the classification *"revised by the user"* a first-class outcome.
`basis = "safety_domain"` needs none either: §3.15's four domains are *"implemented first as safety
domains, meaning the system detects and protects them before any cloud or automated placement
decision is allowed"*, which is a rule about a domain and not a reading of a span. Requiring evidence
there would be inventing a stricter rule than the SPEC states.

**`protected` is a boolean the caller supplies and this module never derives it.** SPEC §2:
*"Neighbouring parts should consume the `protected` flag, not infer it from the class."* Whether
`protected` is exactly co-extensive with the top two classes is Open question 1, unsettled and not
settled by D2. A record with `handling_class = "public_low"` and `protected = True` constructs, and so
does its opposite; the test asserts both, and asserts the module publishes no function mapping one to
the other.

**`reliability_state` is stored and not validated here.** It is P6's vocabulary — §3.13's six — and
Task 4 publishes `RELIABILITY_ORDER` and the `strongest` resolution over it. Validating in two places
invites two vocabularies, which is the defect this part is most exposed to. This module requires it
to be a non-empty string and stores it.

**`COMPLETENESS_RULE` is added because the requirement is a per-value statement.** Nine entries, in
P4's order, each carrying `(implies_unclassified, the sentence that decides it)`. An unpublished
internal frozenset **is** the *"set the author guessed"* the skeleton forbids; a published table with
a citation per value is not. The test cross-checks the six `True` values against P4's own
`evidence_shape.vocabulary.ZERO_OBSERVATION_COMPLETENESS` — `("unsupported", "deferred", "failed",
"metadata_only", "dataless")`, five values where *"nothing was opened, so nothing was seen"* — plus
`unreadable`, which is §2.9's *"indexed-but-unreadable"* and which M3 keeps carrying metadata-level
rows. That cross-check is what makes the table grounded rather than asserted.

**One factual correction to the skeleton, applied here.** The skeleton's Task 3 paragraph says
*"the case of a file with **no run row at all**, which is what a dataless file has."* The skeleton's
own refusal table says the opposite and is right: a dataless file gets **one run row**,
`completeness = dataless`, *"recording that the bytes are elsewhere"*; it is a file inside a
**protected container** that has no row — and no `files` row either, so the gate cannot be asked
about it at all. Both cases are covered: `completeness_implies_unclassified("dataless") is True`
covers the run row, and `resolve_class(None)` covers every file with no classification, including one
with no runs. Reported.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_classification.py
"""SPEC §2's record, and the one resolution the design states twice.

"Absence of a classification resolves to `unreadable_unclassified`, never to
`public_low`." §8.6 says why: "Cost exhaustion must never turn into lower-quality
automatic classification." The failure that sentence forbids is precisely defaulting
an unclassified file to public so the pipeline can continue, and the tests below are
written to fail if any input at all produces `public_low` without a record saying so.

The second thing proved here is D2's: `Unreadable or unclassified` is a GATE OUTCOME.
This module returns it to a caller and cannot write it anywhere, and the namespace
tests are what keep that true when someone later needs a shortcut.
"""
import dataclasses
import json
import re
import uuid

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.observation import observation_key
from evidence_shape.runs import COMPLETENESS, ExtractionRun
from evidence_shape.store import record_run
from evidence_shape.vocabulary import ZERO_OBSERVATION_COMPLETENESS

from extractors.long_tail import (
    POTENTIALLY_SENSITIVE, SensitivitySignal, record_sensitivity_signals,
)

import privacy.classification as classification
from privacy.classification import (
    CLASSIFICATION_FIELDS, COMPLETENESS_RULE, ClassificationRecord,
    UnbackedClassification, completeness_implies_unclassified, resolve_class,
    sensitivity_signal_keys,
)
from privacy.vocabulary import CLASSIFICATION_BASES, HANDLING_CLASSES, OutOfVocabulary

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"


@pytest.fixture()
def file_id(p7_conn, tmp_path):
    """A real P1 row. The record is keyed on (file_id, content_hash) and a synthesized
    pair would not exercise the identity D2 makes authoritative."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    document = corpus / "passport-scan.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    return record_file(
        p7_conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


@pytest.fixture()
def content_hash(p7_conn, file_id):
    return get_file(p7_conn, file_id)["content_hash"]


def a_key(content_hash, raw_value="Passport No. X", locator="zone=body/page=1"):
    return observation_key(content_hash=content_hash, extractor_name="pdf_text",
                           locator=locator, raw_value=raw_value)


def a_record(file_id, content_hash, **over):
    fields = dict(file_id=file_id, content_hash=content_hash,
                  handling_class="highly_sensitive_credential_bearing",
                  protected=True, basis="detector",
                  evidence_refs=(a_key(content_hash),),
                  reliability_state="validated", observed_at=FIXED_CLOCK)
    fields.update(over)
    return ClassificationRecord(**fields)


def a_run(file_id, content_hash, run_id="run-1", completeness="complete"):
    return ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf_text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native",
        config={"reader": "injected"}, completeness=completeness,
        started_at=FIXED_CLOCK, observation_count=1, finished_at=FIXED_CLOCK)


# --- SPEC §2's eight fields ---------------------------------------------------

def test_the_eight_fields_are_specs_eight_in_specs_order():
    assert CLASSIFICATION_FIELDS == (
        "file_id", "content_hash", "handling_class", "protected", "basis",
        "evidence_refs", "reliability_state", "observed_at",
    )
    assert tuple(f.name for f in dataclasses.fields(ClassificationRecord)) == \
        CLASSIFICATION_FIELDS


def test_the_record_is_frozen(file_id, content_hash):
    record = a_record(file_id, content_hash)
    with pytest.raises(dataclasses.FrozenInstanceError):
        record.handling_class = "public_low"


def test_the_record_is_keyed_on_bytes_not_on_a_path(file_id, content_hash):
    # D2: "keyed on the hash because a classification is about BYTES, and new bytes at
    # a path are a new file version that inherits nothing."
    old = a_record(file_id, content_hash)
    new = a_record(file_id, "0" * 64, evidence_refs=(a_key("0" * 64),))
    assert old.file_id == new.file_id
    assert old != new
    assert (old.file_id, old.content_hash) != (new.file_id, new.content_hash)


def test_a_sequence_of_refs_is_frozen_on_the_way_in(file_id, content_hash):
    record = a_record(file_id, content_hash, evidence_refs=[a_key(content_hash)])
    assert isinstance(record.evidence_refs, tuple)


def test_a_bare_string_is_not_a_sequence_of_refs(file_id, content_hash):
    # tuple("sha256:...") is 71 one-character refs. Refusing the string is the only
    # way that mistake is visible.
    with pytest.raises(UnbackedClassification):
        a_record(file_id, content_hash, evidence_refs=a_key(content_hash))


# --- evidence-backed (§8.4) ---------------------------------------------------

def test_a_detector_record_with_no_evidence_is_unbacked(file_id, content_hash):
    # §8.4: the classification "is itself evidence-backed". §3.1's principle: every
    # fact preserves where it came from.
    with pytest.raises(UnbackedClassification) as caught:
        a_record(file_id, content_hash, evidence_refs=())
    assert "detector" in str(caught.value)


def test_a_user_record_and_a_safety_domain_record_need_no_evidence(
        file_id, content_hash):
    # The SPEC scopes the rule to one basis: "evidence_refs is non-empty for any
    # basis = detector classification". The user's act is the evidence (§8.4's
    # "revised by the user"); a safety domain is §3.15's rule about a domain, not a
    # reading of a span. Requiring evidence here would invent a stricter rule.
    assert a_record(file_id, content_hash, basis="user",
                    evidence_refs=(), reliability_state="user_confirmed")
    assert a_record(file_id, content_hash, basis="safety_domain", evidence_refs=())


def test_evidence_refs_must_be_observation_keys_and_not_observation_ids(
        file_id, content_hash):
    # M14: "The key, not the id, is what makes that durable." A per-row
    # observation_id dies on extractor upgrade, so a negative example recorded today
    # would silently stop resolving. `evidence_shape.store.new_id()` mints uuid4.
    with pytest.raises(UnbackedClassification) as caught:
        a_record(file_id, content_hash, evidence_refs=(str(uuid.uuid4()),))
    assert "observation_key" in str(caught.value)


def test_a_content_hash_is_not_an_observation_key(file_id, content_hash):
    # P1's content_hash carries no algorithm prefix; P4's key does. Introspected.
    assert ":" not in content_hash
    assert a_key(content_hash).startswith("sha256:")
    with pytest.raises(UnbackedClassification):
        a_record(file_id, content_hash, evidence_refs=(content_hash,))


def test_a_truncated_or_uppercased_key_is_refused(file_id, content_hash):
    real = a_key(content_hash)
    for bad in (real[:-1], real.upper(), real.replace("sha256", "sha512"), "", None):
        with pytest.raises(UnbackedClassification):
            a_record(file_id, content_hash, evidence_refs=(bad,))


def test_a_real_p4_key_is_accepted_and_survives_an_extractor_version_change(
        file_id, content_hash):
    # MINOR 8: `observation_key` deliberately excludes extractor_version, which is
    # what lets a classification survive an upgrade.
    key = a_key(content_hash)
    assert a_record(file_id, content_hash, evidence_refs=(key,)).evidence_refs == (key,)


# --- the closed vocabularies -------------------------------------------------

def test_an_out_of_vocabulary_handling_class_is_refused(file_id, content_hash):
    with pytest.raises(OutOfVocabulary):
        a_record(file_id, content_hash, handling_class="secret")


def test_p6s_origin_vocabulary_is_not_p7s_basis_vocabulary(file_id, content_hash):
    # P6's five §3.1 origins include "rule" and "LLM interpretation"; P7's basis is
    # three values. The two are never mapped onto one another.
    assert CLASSIFICATION_BASES == ("detector", "safety_domain", "user")
    with pytest.raises(OutOfVocabulary):
        a_record(file_id, content_hash, basis="rule")


def test_reliability_state_is_stored_and_not_validated_here(file_id, content_hash):
    # §3.13's six are P6's and Task 4 publishes the ordering. Two validators would be
    # two vocabularies. Non-empty is the only requirement this module makes.
    assert a_record(file_id, content_hash,
                    reliability_state="llm_supported").reliability_state == \
        "llm_supported"
    with pytest.raises(UnbackedClassification):
        a_record(file_id, content_hash, reliability_state="")


def test_protected_is_a_boolean_and_is_never_derived_from_the_class(
        file_id, content_hash):
    # Open question 1: "Is `protected` exactly the top two handling classes?" The
    # design lists five classes and, separately, five kinds of material that enter a
    # protected state, without stating the relation. Both combinations construct.
    assert a_record(file_id, content_hash,
                    handling_class="public_low", protected=True).protected is True
    assert a_record(file_id, content_hash,
                    handling_class="highly_sensitive_credential_bearing",
                    protected=False).protected is False
    with pytest.raises(UnbackedClassification):
        a_record(file_id, content_hash, protected="yes")


def test_no_function_here_maps_a_class_onto_the_protected_flag():
    names = [n for n in vars(classification) if not n.startswith("_")]
    assert not [n for n in names if "protect" in n.lower() and callable(
        getattr(classification, n))]


# --- resolve_class: the one resolution the design states twice ---------------

def test_absence_resolves_to_unreadable_unclassified():
    assert resolve_class(None) == "unreadable_unclassified"


def test_no_input_at_all_produces_public_low_without_a_record_saying_so(
        file_id, content_hash):
    # §8.6: "Cost exhaustion must never turn into lower-quality automatic
    # classification." There is no default-to-public code path anywhere.
    assert resolve_class(None) != "public_low"
    for name in HANDLING_CLASSES:
        record = a_record(file_id, content_hash, handling_class=name)
        assert resolve_class(record) == name
    produced = {resolve_class(None)} | {
        resolve_class(a_record(file_id, content_hash, handling_class=n))
        for n in HANDLING_CLASSES if n != "public_low"}
    assert "public_low" not in produced


def test_resolve_class_refuses_something_that_is_not_a_record():
    for wrong in ({"handling_class": "public_low"}, "public_low", 0, ()):
        with pytest.raises(TypeError):
            resolve_class(wrong)


# --- D2: a gate outcome, and therefore no writer in this module --------------

def test_this_module_contains_no_writer():
    # "Unreadable or unclassified is a GATE OUTCOME, not a file fact." It must never
    # reach `files.sensitivity_state`, and the durable guarantee is that the string is
    # produced by a decision function in a module that can reach no column.
    forbidden = ("set_", "write_", "record_", "mirror_", "update_", "insert_")
    for name, value in vars(classification).items():
        if name.startswith("_") or not callable(value):
            continue
        assert not name.startswith(forbidden), name
    assert "set_sensitivity_state" not in vars(classification)
    for name, value in vars(classification).items():
        assert getattr(value, "__module__", "") != "database_agent.files_table", name


def test_the_only_connection_taking_function_here_reads(p7_conn, file_id):
    assert "conn" not in resolve_class.__code__.co_varnames
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    sensitivity_signal_keys(p7_conn, file_id)
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before
    assert get_file(p7_conn, file_id)["sensitivity_state"] is None


# --- COMPLETENESS_RULE: stated per value, cross-checked against P4 -----------

def test_the_rule_names_p4s_nine_values_and_no_tenth():
    assert tuple(COMPLETENESS_RULE) == COMPLETENESS
    assert len(COMPLETENESS_RULE) == 9


def test_every_value_carries_the_sentence_that_decides_it():
    for name, (implies, reason) in COMPLETENESS_RULE.items():
        assert isinstance(implies, bool), name
        assert isinstance(reason, str) and reason.strip(), name


def test_the_six_that_imply_unclassified_are_p4s_five_plus_unreadable():
    # Grounded against P4's own tuple rather than against a set this author guessed:
    # ZERO_OBSERVATION_COMPLETENESS is where "nothing was opened, so nothing was
    # seen", and `unreadable` is §2.9's "indexed-but-unreadable", which the SPEC maps
    # to this class by name.
    implied = {n for n, (yes, _) in COMPLETENESS_RULE.items() if yes}
    assert implied == set(ZERO_OBSERVATION_COMPLETENESS) | {"unreadable"}
    assert len(implied) == 6


def test_the_three_that_do_not_are_the_ones_where_content_was_read():
    assert {n for n, (yes, _) in COMPLETENESS_RULE.items() if not yes} == \
        {"complete", "capped", "partial"}
    for name in ("complete", "capped", "partial"):
        assert completeness_implies_unclassified(name) is False


def test_a_dataless_run_row_implies_unclassified(p7_conn, file_id, content_hash):
    # 11 §5: "Do not materialize, hash, or extract." A dataless file gets ONE run row
    # recording that the bytes are elsewhere -- it is a file inside a protected
    # container that has no row at all, and no `files` row either, so the gate cannot
    # be asked about it. Both cases end at `unreadable_unclassified`, by two routes.
    record_run(p7_conn, a_run(file_id, content_hash, completeness="dataless"))
    assert completeness_implies_unclassified("dataless") is True
    assert resolve_class(None) == "unreadable_unclassified"


def test_an_unknown_completeness_value_is_refused():
    for wrong in ("indexed-but-unreadable", "empty", "", None, 1):
        with pytest.raises(OutOfVocabulary):
            completeness_implies_unclassified(wrong)


# --- sensitivity_signal_keys: a detector input, and not a detector -----------

def test_signal_keys_are_p4_keys_in_run_then_emit_order(
        p7_conn, file_id, content_hash):
    record_run(p7_conn, a_run(file_id, content_hash, run_id="run-1"))
    record_run(p7_conn, a_run(file_id, content_hash, run_id="run-2"))
    first = a_key(content_hash, raw_value="Passport No. X")
    second = a_key(content_hash, raw_value="a@b.example", locator="zone=body/page=2")
    record_sensitivity_signals(
        p7_conn, run_id="run-1",
        signals=(SensitivitySignal(0, POTENTIALLY_SENSITIVE, "vcf value"),),
        observation_keys=(first,), now=FIXED_CLOCK)
    record_sensitivity_signals(
        p7_conn, run_id="run-2",
        signals=(SensitivitySignal(0, POTENTIALLY_SENSITIVE, "email address"),),
        observation_keys=(second,), now=FIXED_CLOCK)
    assert sensitivity_signal_keys(p7_conn, file_id) == (first, second)


def test_a_file_with_every_value_marked_sensitive_still_has_no_classification(
        p7_conn, file_id, content_hash):
    # THE test for D2's open posture. P5's docstring: "P5 assigns no handling class:
    # section 8.4 gives classification to P7." The detector is unwritten, so a file
    # covered in signals is still unclassified and the gate still denies it.
    record_run(p7_conn, a_run(file_id, content_hash))
    record_sensitivity_signals(
        p7_conn, run_id="run-1",
        signals=(SensitivitySignal(0, POTENTIALLY_SENSITIVE, "vcf value"),),
        observation_keys=(a_key(content_hash),), now=FIXED_CLOCK)
    assert sensitivity_signal_keys(p7_conn, file_id)
    assert resolve_class(None) == "unreadable_unclassified"
    assert get_file(p7_conn, file_id)["sensitivity_state"] is None


def test_signal_keys_deduplicates_across_runs(p7_conn, file_id, content_hash):
    # A re-run of the same extractor at the same content hash produces the same key
    # (MINOR 8). Listing it twice would make one observation look like two.
    same = a_key(content_hash)
    for run_id in ("run-1", "run-2"):
        record_run(p7_conn, a_run(file_id, content_hash, run_id=run_id))
        record_sensitivity_signals(
            p7_conn, run_id=run_id,
            signals=(SensitivitySignal(0, POTENTIALLY_SENSITIVE, "vcf value"),),
            observation_keys=(same,), now=FIXED_CLOCK)
    assert sensitivity_signal_keys(p7_conn, file_id) == (same,)


def test_signal_keys_is_empty_for_a_file_with_no_runs(p7_conn, file_id):
    assert sensitivity_signal_keys(p7_conn, file_id) == ()


def test_signal_keys_ignores_a_signal_that_is_not_p5s(
        p7_conn, file_id, content_hash):
    record_run(p7_conn, a_run(file_id, content_hash))
    key = a_key(content_hash)
    p7_conn.execute(
        "INSERT INTO extraction_sensitivity_signal (run_id, observation_key, signal, "
        "basis, observed_at) VALUES (?, ?, ?, ?, ?)",
        ("run-1", key, "something else", "unknown", FIXED_CLOCK))
    assert sensitivity_signal_keys(p7_conn, file_id) == ()


def test_this_module_publishes_no_detector():
    # SPEC Deferred: "The design states *what* is protected and never *how it is
    # recognised*." No regex, no gazetteer, no filename pattern, no keyword list.
    for name, value in vars(classification).items():
        if name.startswith("_"):
            continue
        assert not isinstance(value, re.Pattern), name
        assert "detect" not in name.lower(), name
        assert "classify" not in name.lower(), name
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_classification.py -v`
Expected: FAIL — `ImportError: cannot import name 'CLASSIFICATION_FIELDS' from
'privacy.classification'`, because `src/privacy/classification.py` does not exist yet and collection
fails on the first import. Tasks 1 and 2 are green, so `privacy`, `privacy.authorship` and
`privacy.vocabulary` all import.

- [ ] **Step 3: Write `src/privacy/classification.py`**

```python
# src/privacy/classification.py
"""SPEC §2's classification record, and the resolution the design states twice.

"Absence of a classification resolves to `unreadable_unclassified`, never to
`public_low`." §8.6 gives the reason: "Cost exhaustion must never turn into
lower-quality automatic classification." The failure that sentence forbids is exactly
defaulting an unclassified file to public so the pipeline can continue, so there is no
default-to-public code path in this module or anywhere under `src/privacy/`.

**The record is authoritative and it is keyed on BYTES (D2).** `(file_id,
content_hash)` -- on the hash, because a classification is about the bytes, and new
bytes at a path are a new file version that inherits nothing.
`files.sensitivity_state` is this record's PROJECTION onto the current row, written
through P1's published `set_sensitivity_state`; that is Task 4's `mirror_state`, and
it is not here.

**`Unreadable or unclassified` is a GATE OUTCOME, not a file fact (D2), and this
module is where that becomes concrete.** `resolve_class` returns a string to a caller
and this file contains no writer at all: no function inserts or updates, no name
begins `set_`, `write_`, `record_`, `mirror_` or `update_`, and
`database_agent.files_table` is not imported. "Nothing has looked" and "this file
carries nothing" must never become the same value in the same column, and the durable
way to hold them apart is for the string meaning the first to be produced by a
decision function in a module that can reach no column.

**No detector lives here (D2).** SPEC *Deferred*: "The design states *what* is
protected and never *how it is recognised*. The detector rule set, its signals, and
its thresholds are hand-authored. P7 publishes the vocabulary the detectors write
into." There is no regex, no gazetteer, no filename pattern and no keyword list.
`sensitivity_signal_keys` composes two readers P4 and P5 already publish and decides
nothing: it returns the citation handles a detector would pass as `evidence_refs`.
Until a detector is supplied, every real file resolves to `Denied(unclassified)` --
a correct, locked door with nobody holding a key, and the honest v1 posture.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.observation import observation_key
from evidence_shape.store import runs_for_file

from extractors.long_tail import POTENTIALLY_SENSITIVE, sensitivity_signals_for

from privacy.vocabulary import (
    CLASSIFICATION_BASES, OutOfVocabulary, check_handling_class,
)

#: SPEC §2's eight, in SPEC §2's order.
CLASSIFICATION_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "handling_class", "protected", "basis",
    "evidence_refs", "reliability_state", "observed_at",
)

#: §8.4's fifth class, validated against Task 2's closed vocabulary at import: a
#: rename there becomes an ImportError here rather than a string that silently stops
#: matching. Private, because it is a value this module RETURNS and never stores.
_UNREADABLE_UNCLASSIFIED: str = check_handling_class("unreadable_unclassified")

#: The one basis §8.4's "evidence-backed" binds. `user` needs no evidence -- the
#: user's act is the evidence -- and `safety_domain` is §3.15's rule about a domain,
#: not a reading of a span.
_EVIDENCE_REQUIRED_BASIS: str = "detector"

#: M14's citation handle, shaped by asking P4 rather than by hard-coding a pattern.
#: One probe key at import yields the algorithm prefix and the digest width, so a
#: change in `evidence_shape.canonical.sha256_of` propagates instead of drifting.
_PROBE_KEY: str = observation_key(
    content_hash="", extractor_name="", locator="", raw_value="")
_KEY_PREFIX, _, _KEY_DIGEST = _PROBE_KEY.partition(":")
_HEX = frozenset("0123456789abcdef")


class UnbackedClassification(ValueError):
    """§8.4: the classification "is itself evidence-backed".

    Raised when a `detector` classification carries no evidence, when a reference is
    not a P4 `observation_key` (M14), or when a field of the record is not the kind of
    value §8.2 can preserve.
    """


def _is_observation_key(value: object) -> bool:
    """P4's content-addressed handle, never the per-row `observation_id` (M14).

    `evidence_shape.store.new_id()` mints `str(uuid.uuid4())` and P1's `content_hash`
    carries no algorithm prefix, so both are rejected by shape rather than by policy.
    """
    if not isinstance(value, str):
        return False
    prefix, separator, digest = value.partition(":")
    if not separator or prefix != _KEY_PREFIX or len(digest) != len(_KEY_DIGEST):
        return False
    return all(character in _HEX for character in digest)


@dataclass(frozen=True, slots=True)
class ClassificationRecord:
    """One handling class for one file VERSION. D2 makes this record authoritative.

    `protected` is supplied and never derived: SPEC §2, "Neighbouring parts should
    consume the `protected` flag, not infer it from the class", and Open question 1 --
    whether `protected` is exactly the top two classes -- is unsettled.

    `reliability_state` is P6's vocabulary (§3.13's six) and is stored, not validated:
    Task 4 publishes the ordering and the `strongest` resolution over it, and two
    validators would be two vocabularies.
    """

    file_id: str
    content_hash: str
    handling_class: str
    protected: bool
    basis: str
    evidence_refs: tuple[str, ...]
    reliability_state: str
    observed_at: str

    def __post_init__(self) -> None:
        for name in ("file_id", "content_hash", "reliability_state", "observed_at"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise UnbackedClassification(
                    f"{name} must be a non-empty string; §8.2 preserves a record and "
                    f"cannot preserve {value!r}")
        check_handling_class(self.handling_class)
        if self.basis not in CLASSIFICATION_BASES:
            raise OutOfVocabulary(
                f"basis {self.basis!r} is not one of {CLASSIFICATION_BASES}. P6's "
                "five §3.1 `origin` values are a different vocabulary and are never "
                "mapped onto this one.")
        if not isinstance(self.protected, bool):
            raise UnbackedClassification(
                f"protected is §8.4's flag and is a boolean, not {self.protected!r}. "
                "It is supplied by the caller and never derived from the handling "
                "class (SPEC §2, Open question 1).")
        refs = self.evidence_refs
        if isinstance(refs, str) or not isinstance(refs, Sequence):
            raise UnbackedClassification(
                "evidence_refs is a sequence of P4 observation keys; a bare string "
                f"would become {len(refs) if isinstance(refs, str) else 0} "
                "one-character references")
        refs = tuple(refs)
        object.__setattr__(self, "evidence_refs", refs)
        if self.basis == _EVIDENCE_REQUIRED_BASIS and not refs:
            raise UnbackedClassification(
                f"a basis={_EVIDENCE_REQUIRED_BASIS!r} classification carries no "
                "evidence. §8.4: the classification 'is itself evidence-backed', on "
                "§3.1's principle that every fact preserves where it came from.")
        for ref in refs:
            if not _is_observation_key(ref):
                raise UnbackedClassification(
                    f"{ref!r} is not a P4 observation_key. M14: 'The key, not the id, "
                    "is what makes that durable' -- a per-row observation_id dies on "
                    "extractor upgrade, so a negative example recorded today would "
                    "silently stop resolving and the same false protection would "
                    "return.")


def resolve_class(record: ClassificationRecord | None) -> str:
    """The handling class a caller must treat this file version as carrying.

    A GATE OUTCOME (D2), returned to a caller and stored by nothing here. Absence
    resolves to `unreadable_unclassified` and never to `public_low` (SPEC §1, §8.4,
    §8.6): a file that has not been classified has not met §8.4's precondition for
    escalation -- "classify data into handling classes before LLM escalation" -- and
    the gate denies it rather than guessing at it downward.
    """
    if record is None:
        return _UNREADABLE_UNCLASSIFIED
    if not isinstance(record, ClassificationRecord):
        raise TypeError(
            f"resolve_class takes a ClassificationRecord or None, not "
            f"{type(record).__name__}. A mapping that looks like one has not been "
            "through the evidence-backed check.")
    return record.handling_class


#: Per value, with the sentence that decides it, for each of P4's nine
#: `completeness` markings. Stated one at a time rather than as a membership test over
#: a set, because the set is what an author guesses and the sentences are what the
#: design says. Six imply unclassified; they are P4's own
#: ZERO_OBSERVATION_COMPLETENESS plus `unreadable`, and the test cross-checks that.
COMPLETENESS_RULE: Mapping[str, tuple[bool, str]] = MappingProxyType({
    "complete": (False,
        "The run finished on its own terms and the content was read. Whether a "
        "classification EXISTS is a separate question this function does not answer."),
    "capped": (False,
        "§2.7 requires that 'whether extraction was complete or capped' be preserved. "
        "Capped text exists and a detector can read it."),
    "partial": (False,
        "§2.5's 'partially inspected'. M3 keeps the metadata-level rows on a partial "
        "run, so content was read."),
    "metadata_only": (True,
        "In P4's ZERO_OBSERVATION_COMPLETENESS: the stopping extractor emits nothing "
        "and the file stays indexed through its filesystem observations. No content "
        "was read, so no evidence-backed classification is possible."),
    "deferred": (True,
        "§8.6: 'If the budget is exhausted, the product should retain extracted "
        "evidence, mark the deferred stage, and leave the file or group in review "
        "rather than guessing.' The stage did not run."),
    "unsupported": (True,
        "§2.4: 'an empty extraction result is different from an extractor that does "
        "not yet exist.' No extractor looked, so nothing was seen."),
    "unreadable": (True,
        "§2.9: 'unsupported proprietary formats should be recorded as "
        "indexed-but-unreadable rather than silently treated as empty.' The SPEC maps "
        "an unreadable extraction result to this handling class by name."),
    "failed": (True,
        "In P4's ZERO_OBSERVATION_COMPLETENESS: the run did not complete and emitted "
        "nothing."),
    "dataless": (True,
        "11 §5: 'Do not materialize, hash, or extract.' C4: nothing was opened, so "
        "nothing was seen. The bytes are elsewhere and the row records that."),
})


def completeness_implies_unclassified(completeness: object) -> bool:
    """Whether a run at this marking leaves the file with nothing to classify.

    True does not mean the class was WRITTEN -- nothing writes it, and D2 forbids
    `unreadable_unclassified` from reaching `files.sensitivity_state`. It means no
    content was read, so no evidence-backed classification is possible and the gate's
    resolution for this file version is `unreadable_unclassified`.
    """
    try:
        implies, _ = COMPLETENESS_RULE[completeness]
    except (KeyError, TypeError):
        raise OutOfVocabulary(
            f"{completeness!r} is not one of P4's nine completeness markings "
            f"{tuple(COMPLETENESS_RULE)}. There is no marking literally named "
            "'indexed-but-unreadable': §2.9's phrase is spelled `unreadable`."
        ) from None
    return implies


def sensitivity_signal_keys(conn: sqlite3.Connection,
                            file_id: str) -> tuple[str, ...]:
    """P4 observation keys P5 marked "potentially sensitive" for this file.

    A detector INPUT and not a detector. It applies no rule, assigns no class and
    returns no value: only the citation handles a detector would pass as
    `evidence_refs`. P5's own docstring is explicit about who it is for -- "Email
    addresses, message content and every VCF value are marked POTENTIALLY SENSITIVE at
    emission, for P7 to act on. P5 assigns no handling class: section 8.4 gives
    classification to P7."

    P5's reader is keyed by `run_id` only, so this is the file-level walk P7 composes
    from the two readers P4 and P5 already publish; P7 adds no reader to P5. Keys are
    deduplicated in first-seen order, because a re-run of the same extractor at the
    same content hash produces the same key (MINOR 8) and listing it twice would make
    one observation look like two.
    """
    seen: dict[str, None] = {}
    for run in runs_for_file(conn, file_id):
        for row in sensitivity_signals_for(conn, run.run_id):
            if row["signal"] == POTENTIALLY_SENSITIVE:
                seen.setdefault(row["observation_key"], None)
    return tuple(seen)
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_classification.py -v`
Expected: PASS — 33 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–3 green, and every pre-existing test still green. P7 has created
`src/privacy/` and `tests/p7/` and modified no file belonging to another part.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/classification.py tests/p7/test_p7_classification.py
git commit -m "feat(P7): the classification record, evidence-backed, with absence resolving to unreadable_unclassified"
```

---

---

### Task 4: P7's own classification store, §3.13's ordering, and the `sensitivity_state` projection

**Files:**
- Create: `src/privacy/schema.py`, `src/privacy/classification_store.py`
- Modify: `tests/p7/conftest.py` (P7's own; `tests/conftest.py` is not touched)
- Test: `tests/p7/test_p7_classification_store.py`

**Interfaces:**
- Consumes: `database_agent.supersede.mark_superseded(conn, table, *, old_id, new_id, reason)
  -> None`, `.chain(conn, table, record_id) -> list[sqlite3.Row]`, `.SUPERSEDE_COLUMNS`,
  `.supersede_ddl(table) -> str`,
  `database_agent.files_table.set_sensitivity_state(conn, file_id, *, state: dict, author: str,
  component_version: str) -> None`, `.get_file(conn, file_id) -> sqlite3.Row`, `.FILES_COLUMNS`,
  `database_agent.db.create_schema(conn) -> None`,
  `evidence_shape.canonical.canonical_json(value) -> str`,
  `privacy.classification.ClassificationRecord`, `.CLASSIFICATION_FIELDS`,
  `.UNREADABLE_UNCLASSIFIED` (A5),
  `privacy.authorship.SUBSYSTEM`.
- Produces (`schema.py`):
  - `CLASSIFICATIONS_TABLE: str = "classifications"`
  - `SUPERSEDE_ADAPTER_COLUMN: str = "record_id"`
  - `CLASSIFICATIONS_DDL: str`
  - `create_privacy_schema(conn) -> None` — idempotent; **Task 5 extends this function**.
- Produces (`classification_store.py`):
  - `RELIABILITY_ORDER: tuple[str, ...]` — §3.13's five ranked, strongest first.
  - `REJECTED: str = "rejected"` — the sixth state, outside the ranking.
  - `ClassificationStore(conn)` with `current(file_id, content_hash) -> ClassificationRecord | None`,
    `current_fact_id(file_id, content_hash) -> str | None`, `write(record) -> str`,
    `supersede(old_fact_id, new_fact_id, reason) -> None`,
    `history(file_id) -> list[ClassificationRecord]`.
  - `strongest(records: Sequence[ClassificationRecord]) -> ClassificationRecord`
  - `mirror_state(record) -> dict`
  - `mirror(conn, record, *, component_version) -> None`
  - `AmbiguousCurrentClassification`, `UnrankedReliability`, `GateOutcomeNotAFileFact`.

**Done-means:** 2 (second half).

**This task owns storage and authors nothing.** C4: *"the gate still raises and writes nothing — a
gate that also wrote would be doing two jobs."* `ClassificationStore.write` inserts a row and
appends **no** event; `classification_assigned` and `classification_superseded` are appended by
sibling Task 16's `assign` and `reclassify`, which are the entry points a detector or a user
correction calls. A store that also appended would put one act in the log twice and would make the
event's `user_id` a property of the storage layer rather than of the act.

**The key is `(file_id, content_hash)` and new bytes inherit nothing.** D2: *"Keyed on the hash
because a classification is about BYTES; new bytes at a path are a new file version and inherit
nothing."* `current` is keyed on the pair, not on `file_id`, and a second content hash at the same
`file_id` resolves to `None` until something classifies it. That is the whole reason
`unreadable_unclassified` cannot be a stored fact: an edited passport scan must read as *nobody has
looked at these bytes*, not as *these bytes were found to carry nothing*.

**Ties are a red test, never a pick.** Two unsuperseded records at one key and one reliability rank
raise `AmbiguousCurrentClassification`. P4 took the identical position on `observations_by_key`
returning two rows — resolve to the current row, and *"an unresolvable ambiguity raises rather than
picking the first"*. A gate that picked would release under whichever classification the query
planner happened to return first.

**Whether `protected` is co-extensive with the top two handling classes stays open.** SPEC Open
question 1, and SPEC §2: *"Neighbouring parts should consume the `protected` flag, not infer it from
the class."* `protected` is a stored column on every record and is never derived here; one test
holds the question by name.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_classification_store.py
"""Done-means 2's second half: exactly one current classification per file version,
supersede-never-overwrite through P1's three columns, and the projection onto
`files.sensitivity_state` through P1's published setter.

Three things this file deliberately does NOT do.

It creates no `file_facts` row and imports nothing from a P6 module, because D2 made
P7's `ClassificationRecord` authoritative and there is no P6 record to read. P7's
SPEC still says "P6 must accept `sensitivity` as a first-class universal field" while
round 1 found that field has no producer; that conflict is Joseph's (NEEDS-JOSEPH C5)
and this file is written so nothing in it depends on the answer.

It stores no `unreadable_unclassified` record and never lets one reach the column.
That value is a GATE OUTCOME (D2) -- what the release decision says when it has no
classification to release against -- and storing it would make "nothing has looked"
read as "this file carries nothing".

It writes its own classifications and says so, because the detector is unwritten (D2)
and on a real corpus every file would resolve to `Denied(unclassified)`. A fixture
standing in for a detector is the honest v1 posture; a fixture pretending to BE one
is not.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from database_agent.files_table import FILES_COLUMNS, get_file, record_file
from database_agent.supersede import SUPERSEDE_COLUMNS, chain

from privacy.authorship import SUBSYSTEM
from privacy.classification import UNREADABLE_UNCLASSIFIED, ClassificationRecord
from privacy.classification_store import (
    REJECTED,
    RELIABILITY_ORDER,
    AmbiguousCurrentClassification,
    ClassificationStore,
    GateOutcomeNotAFileFact,
    UnrankedReliability,
    mirror,
    mirror_state,
    strongest,
)
from privacy.schema import (
    CLASSIFICATIONS_TABLE,
    SUPERSEDE_ADAPTER_COLUMN,
    create_privacy_schema,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"

#: Bare hex digests, because that is what P1 stores (R1) and what P4 refuses to
#: accept anything else as: `MalformedRun: content_hash is the digest P1 stored`.
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_EDITED = "e" * 64

#: §8.4: "A scanned passport ... should enter a protected state immediately." The
#: DETECTOR that would notice is unwritten (D2), so the test plays its part and the
#: `basis` says which part it is playing.
PASSPORT_KEYS = ("obs-key-passport-mrz", "obs-key-passport-number")


def a_file(conn, tmp_path: Path, *, name: str = "passport.pdf",
           content_hash: str = HASH_A) -> str:
    """A `files` row. `record_file` stats the path, so the bytes must exist."""
    path = tmp_path / name
    path.write_bytes(b"scanned passport")
    return record_file(
        conn, path, filename=name, normalized_filename=name.rsplit(".", 1)[0],
        extension=".pdf", observed_size=path.stat().st_size,
        observed_timestamps="{}", parent_folder_context=None, mime_type=None,
        detected_format=None, scan_state="seen", materialized=True,
        content_hash=content_hash)


def a_record(**over) -> ClassificationRecord:
    base = dict(file_id="file-1", content_hash=HASH_A,
                handling_class="highly_sensitive_credential_bearing",
                protected=True, basis="detector", evidence_refs=PASSPORT_KEYS,
                reliability_state="validated", observed_at=FIXED_CLOCK)
    base.update(over)
    return ClassificationRecord(**base)


@pytest.fixture()
def store(p7_conn) -> ClassificationStore:
    return ClassificationStore(p7_conn)


# --- the table P7 creates and owns ------------------------------------------

def test_the_schema_is_idempotent(p7_conn):
    # `p7_conn` already created it; a second call is a no-op, the way P4's
    # `create_evidence_schema` is.
    create_privacy_schema(p7_conn)
    create_privacy_schema(p7_conn)


def test_the_table_carries_p1s_three_supersede_columns_under_p1s_spelling(p7_conn):
    # M1, and MINOR 3 confirms the spelling is `supersede_reason`. P7 does not
    # re-spell the set and does not add a fourth.
    columns = {row["name"] for row in p7_conn.execute(
        f"PRAGMA table_info({CLASSIFICATIONS_TABLE})")}
    assert set(SUPERSEDE_COLUMNS) <= columns
    assert "preferred" not in columns


def test_record_id_is_a_virtual_projection_of_the_published_fact_id(p7_conn):
    # P1's `mark_superseded` and `chain` are `... WHERE record_id = ?`, and P7's
    # published id is `fact_id`. P4 solved this once (`SUPERSEDE_ADAPTER_COLUMN`)
    # and P7 copies the solution rather than a second supersede implementation.
    assert SUPERSEDE_ADAPTER_COLUMN == "record_id"
    visible = {row["name"] for row in p7_conn.execute(
        f"PRAGMA table_info({CLASSIFICATIONS_TABLE})")}
    assert "fact_id" in visible
    assert "record_id" not in visible          # VIRTUAL: absent from table_info
    hidden = {row["name"] for row in p7_conn.execute(
        f"PRAGMA table_xinfo({CLASSIFICATIONS_TABLE})")}
    assert "record_id" in hidden


def test_a_classification_cannot_be_deleted(p7_conn, store):
    # §8.2's rule, and §8.7 needs the rejected proposal's evidence to survive.
    fact_id = store.write(a_record())
    with pytest.raises(sqlite3.IntegrityError, match="superseded"):
        p7_conn.execute(
            f"DELETE FROM {CLASSIFICATIONS_TABLE} WHERE fact_id = ?", (fact_id,))


def test_a_classification_cannot_be_overwritten(p7_conn, store):
    # §8.2 forbids overwriting the earlier record. The three supersede columns are
    # outside the trigger: supersession is the one legal write to an existing row.
    fact_id = store.write(a_record())
    with pytest.raises(sqlite3.IntegrityError, match="superseded"):
        p7_conn.execute(
            f"UPDATE {CLASSIFICATIONS_TABLE} SET handling_class = ? WHERE fact_id = ?",
            ("public_low", fact_id))


def test_p7_adds_no_column_to_p1s_files_table(p7_conn):
    # P7 creates and modifies no file owned by another part, and `sensitivity_state`
    # has been on `files` since P1's first schema.
    columns = tuple(row["name"] for row in p7_conn.execute("PRAGMA table_info(files)"))
    assert columns == FILES_COLUMNS


# --- one current record per file VERSION ------------------------------------

def test_write_returns_a_fact_id_and_current_reads_the_record_back(store):
    record = a_record()
    fact_id = store.write(record)
    assert isinstance(fact_id, str) and fact_id
    assert store.current("file-1", HASH_A) == record


def test_current_is_keyed_on_the_content_hash_and_not_on_the_file_id(store):
    store.write(a_record())
    assert store.current("file-1", HASH_B) is None


def test_new_bytes_at_the_same_file_inherit_nothing(store):
    # D2: "a classification is about BYTES; new bytes at a path are a new file
    # version and inherit nothing." The edited scan reads as unlooked-at, which is
    # what makes `Denied(unclassified)` correct rather than a regression.
    store.write(a_record())
    assert store.current("file-1", HASH_EDITED) is None
    assert store.current_fact_id("file-1", HASH_EDITED) is None


def test_current_is_none_before_anything_classifies(store):
    # The detector is unwritten (D2). This is the state a real corpus is in.
    assert store.current("file-unknown", "sha256:zzz") is None


def test_current_fact_id_returns_the_unsuperseded_row(store):
    old = store.write(a_record())
    new = store.write(a_record(reliability_state="user_confirmed", observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    assert store.current_fact_id("file-1", HASH_A) == new


# --- §3.13's ordering, quoted and not re-derived ----------------------------

def test_the_ordering_is_p6s_listed_order(store):
    # The design lists them in this order and states no comparison rule; P6's
    # canonical snake_case literals, never a respelling.
    assert RELIABILITY_ORDER == (
        "user_confirmed", "direct", "validated", "llm_supported", "possible")
    assert REJECTED == "rejected"
    assert REJECTED not in RELIABILITY_ORDER


def test_a_user_confirmed_record_outranks_a_validated_one(store):
    validated = a_record(reliability_state="validated")
    confirmed = a_record(reliability_state="user_confirmed",
                         handling_class="personal_non_sensitive", protected=False,
                         basis="user", evidence_refs=(), observed_at=LATER)
    store.write(validated)
    store.write(confirmed)
    assert store.current("file-1", HASH_A) == confirmed


def test_the_ordering_holds_regardless_of_write_order(store):
    confirmed = a_record(reliability_state="user_confirmed", basis="user",
                         evidence_refs=())
    store.write(confirmed)
    store.write(a_record(reliability_state="direct", observed_at=LATER))
    assert store.current("file-1", HASH_A) == confirmed


def test_strongest_reads_the_order_and_computes_no_score(store):
    records = [a_record(reliability_state=state) for state in
               ("possible", "llm_supported", "direct", "user_confirmed", "validated")]
    assert strongest(records).reliability_state == "user_confirmed"
    assert strongest(records[:1]).reliability_state == "possible"


def test_strongest_of_nothing_is_a_programming_error(store):
    with pytest.raises(ValueError):
        strongest(())


def test_a_rejected_record_is_stored_and_is_never_current(store):
    # §8.7: rejections are stored "with the evidence that produced them". A rejected
    # fact is a record of a proposal the user marked incorrect, so it must survive
    # and must never be the answer to "what is this file".
    rejected = store.write(a_record(reliability_state=REJECTED))
    assert store.current("file-1", HASH_A) is None
    assert [r.reliability_state for r in store.history("file-1")] == [REJECTED]
    assert rejected


def test_an_unranked_reliability_raises_rather_than_sorting_last(store):
    # A value outside §3.13's six is a load error, not a fallback. Sorting it last
    # would let an unknown state quietly become the weakest evidence in the product.
    with pytest.raises(UnrankedReliability):
        strongest([a_record(reliability_state="probably_fine")])


def test_two_live_records_at_the_same_rank_raise_rather_than_pick(store):
    store.write(a_record(evidence_refs=("obs-key-a",)))
    store.write(a_record(evidence_refs=("obs-key-b",), observed_at=LATER))
    with pytest.raises(AmbiguousCurrentClassification):
        store.current("file-1", HASH_A)


# --- supersede, never overwrite ---------------------------------------------

def test_a_revision_supersedes_through_p1s_three_columns(p7_conn, store):
    old = store.write(a_record())
    new = store.write(a_record(handling_class="personal_non_sensitive", protected=False,
                               basis="user", evidence_refs=(),
                               reliability_state="user_confirmed", observed_at=LATER))
    store.supersede(old, new, "user reclassified as non-sensitive")
    row = p7_conn.execute(
        f"SELECT * FROM {CLASSIFICATIONS_TABLE} WHERE fact_id = ?", (old,)).fetchone()
    assert row["superseded_by"] == new
    assert row["supersede_reason"] == "user reclassified as non-sensitive"
    assert p7_conn.execute(
        f"SELECT supersedes FROM {CLASSIFICATIONS_TABLE} WHERE fact_id = ?",
        (new,)).fetchone()["supersedes"] == old


def test_both_records_remain_readable_afterwards(store):
    # §8.2's explicit rule, and its OCR example applies directly: an early detector
    # and a later one may disagree and both survive.
    old = store.write(a_record())
    new = store.write(a_record(reliability_state="user_confirmed", basis="user",
                               evidence_refs=(), observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    history = store.history("file-1")
    assert len(history) == 2
    assert {r.basis for r in history} == {"detector", "user"}


def test_the_chain_is_p1s_and_p7_does_not_copy_it(p7_conn, store):
    old = store.write(a_record())
    new = store.write(a_record(reliability_state="user_confirmed", basis="user",
                               evidence_refs=(), observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    assert [row["fact_id"] for row in chain(p7_conn, CLASSIFICATIONS_TABLE, old)] == \
        [old, new]


def test_the_first_supersede_reason_is_never_overwritten(store):
    old = store.write(a_record())
    new = store.write(a_record(reliability_state="user_confirmed", basis="user",
                               evidence_refs=(), observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    third = store.write(a_record(reliability_state="direct", observed_at=LATER))
    with pytest.raises(ValueError, match="already superseded"):
        store.supersede(old, third, "a second reason")


def test_a_superseded_record_is_not_current(store):
    old = store.write(a_record(reliability_state="user_confirmed", basis="user",
                               evidence_refs=()))
    new = store.write(a_record(reliability_state="validated", observed_at=LATER))
    store.supersede(old, new, "detector re-ran on better evidence")
    # The superseded record outranks the survivor by §3.13, and is still not the
    # answer: supersession is a stronger statement than reliability.
    assert store.current("file-1", HASH_A).reliability_state == "validated"


def test_history_is_oldest_first_and_spans_file_versions(store):
    store.write(a_record(observed_at=FIXED_CLOCK))
    store.write(a_record(content_hash=HASH_EDITED, observed_at=LATER))
    assert [r.content_hash for r in store.history("file-1")] == \
        [HASH_A, HASH_EDITED]


# --- the projection onto files.sensitivity_state ----------------------------

def test_the_mirror_goes_through_p1s_published_setter(p7_conn, tmp_path):
    # D2: the column is the record's PROJECTION, written through the twin of
    # `set_extraction_status`. P5 took the identical position on
    # `extraction_status_by_tier` and the resolution was P1 publishing the setter.
    file_id = a_file(p7_conn, tmp_path)
    record = a_record(file_id=file_id)
    mirror(p7_conn, record, component_version=COMPONENT)
    stored = json.loads(get_file(p7_conn, file_id)["sensitivity_state"])
    assert stored == mirror_state(record)


def test_privacy_issues_no_update_files_of_its_own(p7_conn, tmp_path):
    # Asserted by RUNTIME TRACE, not by grepping source text: `set_trace_callback`
    # sees the statements sqlite actually executed, and a comment or a docstring
    # cannot fake one. Exactly one `UPDATE files` runs and it is P1's, verbatim.
    file_id = a_file(p7_conn, tmp_path)
    statements: list[str] = []
    p7_conn.set_trace_callback(statements.append)
    try:
        mirror(p7_conn, a_record(file_id=file_id), component_version=COMPONENT)
    finally:
        p7_conn.set_trace_callback(None)
    updates = [s for s in statements if s.lstrip().upper().startswith("UPDATE FILES")]
    assert len(updates) == 1
    assert updates[0].startswith("UPDATE files SET sensitivity_state = ")


def test_the_mirror_authors_as_p7(p7_conn, tmp_path, monkeypatch):
    # M8: the acting part authors, P1 stores. `author` is not a parameter a caller
    # of `mirror` may set.
    import privacy.classification_store as module
    seen: dict[str, object] = {}
    monkeypatch.setattr(
        module, "set_sensitivity_state",
        lambda conn, file_id, **fields: seen.update(fields, file_id=file_id))
    mirror(p7_conn, a_record(file_id="file-1"), component_version=COMPONENT)
    assert seen["author"] == SUBSYSTEM == "P7"
    assert seen["component_version"] == COMPONENT


def test_the_projection_carries_the_record_and_not_a_second_vocabulary(store):
    record = a_record()
    state = mirror_state(record)
    assert state == {
        "handling_class": "highly_sensitive_credential_bearing",
        "protected": True,
        "basis": "detector",
        "reliability_state": "validated",
        "content_hash": HASH_A,
        "evidence_refs": list(PASSPORT_KEYS),
        "observed_at": FIXED_CLOCK,
    }


def test_the_projection_is_json_serialisable_the_way_p1_stores_it(store):
    # P1 does `json.dumps(state, sort_keys=True)` and holds no handling-class
    # vocabulary: a class P1 has never heard of round-trips unchanged.
    state = mirror_state(a_record())
    assert json.loads(json.dumps(state, sort_keys=True)) == state


def test_the_record_stays_authoritative_and_the_column_is_the_projection(p7_conn, tmp_path, store):
    file_id = a_file(p7_conn, tmp_path)
    record = a_record(file_id=file_id)
    store.write(record)
    mirror(p7_conn, record, component_version=COMPONENT)
    # Provenance -- basis, evidence, reliability, supersede chain -- is answerable
    # from the record. The column answers only "what is this file right now".
    assert store.current(file_id, HASH_A).evidence_refs == PASSPORT_KEYS
    assert json.loads(get_file(p7_conn, file_id)["sensitivity_state"])["evidence_refs"] \
        == list(PASSPORT_KEYS)


# --- `Unreadable or unclassified` is a gate outcome, not a file fact (D2) ---

def test_an_unclassified_record_is_refused_by_the_store(store):
    # D2. Absence already says "nothing has looked"; a row saying it would be a
    # FACT claiming the same thing, and the two would then disagree.
    with pytest.raises(GateOutcomeNotAFileFact):
        store.write(a_record(handling_class=UNREADABLE_UNCLASSIFIED, protected=False,
                             basis="detector", evidence_refs=("obs-key-a",)))


def test_unclassified_never_reaches_the_column(store):
    with pytest.raises(GateOutcomeNotAFileFact):
        mirror_state(a_record(handling_class=UNREADABLE_UNCLASSIFIED, protected=False))


def test_no_input_makes_the_column_read_public_low(p7_conn, tmp_path, store):
    # §8.6: "Cost exhaustion must never turn into lower-quality automatic
    # classification." The failure that sentence forbids is exactly defaulting an
    # unclassified file to public so the pipeline can continue.
    file_id = a_file(p7_conn, tmp_path)
    assert get_file(p7_conn, file_id)["sensitivity_state"] is None
    assert store.current(file_id, HASH_A) is None


# --- D2's shape: no protocol, no injection, no P6 surface -------------------

def test_the_store_is_concrete_and_takes_no_injection(p7_conn):
    import privacy.classification_store as module
    assert not hasattr(module, "SensitivityFacts")
    assert not hasattr(module, "SensitivityStateWriter")
    # One constructor argument: the connection. A second would be the injection D2
    # removed.
    import inspect
    assert list(inspect.signature(ClassificationStore).parameters) == ["conn"]


def test_the_p6_stand_in_is_deleted_and_not_reimplemented(p7_conn):
    # There is no longer a P6 surface for it to stand in for (D2).
    assert not (Path(__file__).parent / "p6_fixture.py").exists()


def test_the_store_needs_no_p6_table_to_exist(p7_conn, store):
    # NEEDS-JOSEPH C5: P7's SPEC still says "P6 must accept `sensitivity` as a
    # first-class universal field" while D2 makes P7's record authoritative and
    # round 1 found that P6 field has no producer. Task 4 is built so the answer
    # does not matter: there is no `file_facts` table in this database.
    tables = {row["name"] for row in p7_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "file_facts" not in tables
    store.write(a_record())
    assert store.current("file-1", HASH_A) is not None


def test_the_store_appends_no_event(p7_conn, store):
    # C4's one job. `classification_assigned` is Task 16's, once, with a user_id.
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    old = store.write(a_record())
    new = store.write(a_record(reliability_state="user_confirmed", basis="user",
                               evidence_refs=(), observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before


def test_whether_protected_is_the_top_two_classes_is_not_answered_here(store):
    # SPEC Open question 1, unsettled and not settled by D2. `protected` is stored,
    # never derived: SPEC §2, "Neighbouring parts should consume the `protected`
    # flag, not infer it from the class."
    low_but_protected = a_record(handling_class="personal_non_sensitive",
                                 protected=True, basis="safety_domain")
    store.write(low_but_protected)
    assert store.current("file-1", HASH_A).protected is True
    import privacy.classification_store as module
    assert not [name for name in vars(module) if "co_extensive" in name]
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_classification_store.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.classification_store'`
(neither `privacy.schema` nor `privacy.classification_store` exists yet, so collection fails on the
first import of the module under test).

- [ ] **Step 3: Write `src/privacy/schema.py`**

```python
# src/privacy/schema.py
"""P7's tables. They live inside the one local SQLite database the design names --
§0: "A local SQLite database acts as the durable working memory of the product."

One table per part is this project's CONVENTION, not a design quotation. P4's schema
module records what happened the last time that convention acquired quote marks: a
sentence nobody wrote was cited in three PLANs and one module. It is written plainly
here instead.

P1 owns the handle, the transaction boundary, `files` and `events`. P7 creates none
of them and modifies no P1 file. `create_privacy_schema` is the one entry point;
Task 5 adds `privacy_policies` to it.

One column is not a published field. P1's `mark_superseded` and `chain` are
`... WHERE record_id = ?`, and P7's published primary key is `fact_id`. `record_id`
is a VIRTUAL generated projection of it: it stores nothing, cannot diverge, does not
appear in `PRAGMA table_info`, and lets P1's tested supersede functions be reused
verbatim instead of written a second time under a second name. P4 solved this once
(`evidence.record_id`) and P7 copies the solution, not the implementation.

The table is keyed on `(file_id, content_hash)` and the index says so. D2: a
classification is about BYTES. New bytes at a path are a new file version and
inherit nothing, which is what lets "nobody has looked at these bytes" stay
distinguishable from "these bytes were found to carry nothing".
"""
from __future__ import annotations

import sqlite3

#: P7's classification table. Named here so no caller retypes the string.
CLASSIFICATIONS_TABLE = "classifications"

#: The one column that is not a published classification field. See the docstring.
SUPERSEDE_ADAPTER_COLUMN = "record_id"

CLASSIFICATIONS_DDL = f"""
CREATE TABLE IF NOT EXISTS {CLASSIFICATIONS_TABLE} (
    fact_id           TEXT PRIMARY KEY,
    {SUPERSEDE_ADAPTER_COLUMN} TEXT GENERATED ALWAYS AS (fact_id) VIRTUAL,
    file_id           TEXT NOT NULL,
    content_hash      TEXT NOT NULL,
    handling_class    TEXT NOT NULL,
    protected         INTEGER NOT NULL,
    basis             TEXT NOT NULL,
    evidence_refs     TEXT NOT NULL,
    reliability_state TEXT NOT NULL,
    observed_at       TEXT NOT NULL,
    supersedes        TEXT,
    superseded_by     TEXT,
    supersede_reason  TEXT
);
-- Deliberately NOT unique: an early detector and a later one may disagree and both
-- survive (§8.2's OCR example). The resolver is `ClassificationStore.current`.
CREATE INDEX IF NOT EXISTS classifications_version
    ON {CLASSIFICATIONS_TABLE} (file_id, content_hash);
CREATE INDEX IF NOT EXISTS classifications_file
    ON {CLASSIFICATIONS_TABLE} (file_id);
CREATE TRIGGER IF NOT EXISTS classifications_no_delete
BEFORE DELETE ON {CLASSIFICATIONS_TABLE}
BEGIN SELECT RAISE(ABORT, 'a classification is superseded, never removed (§8.2, §8.7)'); END;
-- Over the eight SPEC §2 fields. The three supersede columns are outside it:
-- supersession is the one legal write to an existing row.
CREATE TRIGGER IF NOT EXISTS classifications_never_overwritten
BEFORE UPDATE OF fact_id, file_id, content_hash, handling_class, protected, basis,
                 evidence_refs, reliability_state, observed_at
    ON {CLASSIFICATIONS_TABLE}
BEGIN SELECT RAISE(ABORT, 'a classification is superseded, never overwritten (§8.2)'); END;
"""


def create_privacy_schema(conn: sqlite3.Connection) -> None:
    """Create every P7-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(CLASSIFICATIONS_DDL)
```

- [ ] **Step 4: Write `src/privacy/classification_store.py`**

```python
# src/privacy/classification_store.py
"""P7's own classification store (D2, ratified 2026-08-21).

This module used to be `facts_seam.py`: an injected `SensitivityFacts` protocol over
a `sensitivity` fact P6 owned. D2 removed the seam. P7's `ClassificationRecord`,
keyed `(file_id, content_hash)`, is AUTHORITATIVE, so there is no P6 record to read
and nothing to inject. The four methods keep their shape -- `current`, `write`,
`supersede`, `history` -- over a table P7 creates and owns.

Three rules, each a quotation rather than a choice.

**The key is the bytes.** A classification is bound to a file VERSION (§8.2). New
bytes at a path are a new version and inherit nothing, so `current` is keyed on the
pair and returns `None` for a hash nothing has classified.

**Supersede, never overwrite (§8.2).** A revision is a new record linked through P1's
three published columns; both remain inspectable. P7 does not implement supersession,
it calls `mark_superseded` and `chain`. §3.13's ordering is P6's -- the design's own
listed order, `user confirmed`, `direct`, `validated`, `LLM-supported`, `possible`,
with `rejected` outside it -- written down once and never re-derived from a score.

**`Unreadable or unclassified` is a gate OUTCOME, not a file fact (D2).** It lives on
the release decision. It is refused here on both sides of the projection, because a
stored row saying it would claim, as a fact, exactly what the absence of a row
already says -- and the two would then be able to disagree.

This module authors nothing. C4: "a gate that also wrote would be doing two jobs."
`classification_assigned` and `classification_superseded` are appended once, by
`privacy.learning_seam.assign` and `.reclassify`, which are the entry points a
detector or a user correction calls.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from collections.abc import Sequence

from database_agent.files_table import set_sensitivity_state
from database_agent.supersede import chain, mark_superseded

from evidence_shape.canonical import canonical_json

from privacy.authorship import SUBSYSTEM
from privacy.classification import UNREADABLE_UNCLASSIFIED, ClassificationRecord
from privacy.schema import CLASSIFICATIONS_TABLE

#: §3.13, in the design's own listed order, strongest first. P6's canonical
#: snake_case literals. Never sorted, never scored, never re-derived.
RELIABILITY_ORDER: tuple[str, ...] = (
    "user_confirmed", "direct", "validated", "llm_supported", "possible",
)

#: The sixth state. "A rejected fact is a proposal that the user or validator marked
#: as incorrect" -- stored, kept for §8.7's negative examples, never current.
REJECTED = "rejected"

_COLUMNS = (
    "fact_id", "file_id", "content_hash", "handling_class", "protected", "basis",
    "evidence_refs", "reliability_state", "observed_at",
)


class AmbiguousCurrentClassification(Exception):
    """Two live records at one key and one rank. Raised, never resolved by picking."""


class UnrankedReliability(Exception):
    """A reliability state outside §3.13's six. A load error, not a fallback."""


class GateOutcomeNotAFileFact(Exception):
    """`unreadable_unclassified` was offered as a stored fact or as a projection."""


def _rank(record: ClassificationRecord) -> int:
    try:
        return RELIABILITY_ORDER.index(record.reliability_state)
    except ValueError:
        raise UnrankedReliability(
            f"{record.reliability_state!r} is not one of §3.13's ranked states "
            f"{RELIABILITY_ORDER!r}; {REJECTED!r} is stored but never current"
        ) from None


def strongest(records: Sequence[ClassificationRecord]) -> ClassificationRecord:
    """The record §3.13's listed order ranks highest. Ties raise."""
    if not records:
        raise ValueError("strongest() of no records")
    ranked = sorted(records, key=_rank)
    best = _rank(ranked[0])
    tied = [r for r in ranked if _rank(r) == best]
    if len(tied) > 1:
        raise AmbiguousCurrentClassification(
            f"{len(tied)} live classifications at reliability "
            f"{tied[0].reliability_state!r} for {tied[0].file_id!r} at "
            f"{tied[0].content_hash!r}; one must supersede the other (§8.2)"
        )
    return ranked[0]


def _row_to_record(row: sqlite3.Row) -> ClassificationRecord:
    return ClassificationRecord(
        file_id=row["file_id"],
        content_hash=row["content_hash"],
        handling_class=row["handling_class"],
        protected=bool(row["protected"]),
        basis=row["basis"],
        evidence_refs=tuple(json.loads(row["evidence_refs"])),
        reliability_state=row["reliability_state"],
        observed_at=row["observed_at"],
    )


class ClassificationStore:
    """P7's authoritative classification record (D2). Concrete; no injection."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def write(self, record: ClassificationRecord) -> str:
        """Insert one record and return its `fact_id`. Appends no event (C4)."""
        if record.handling_class == UNREADABLE_UNCLASSIFIED:
            raise GateOutcomeNotAFileFact(
                f"{UNREADABLE_UNCLASSIFIED!r} is a gate outcome, not a file fact "
                "(D2): the absence of a record already says nothing has looked"
            )
        fact_id = str(uuid.uuid4())
        self._conn.execute(
            f"INSERT INTO {CLASSIFICATIONS_TABLE} ({','.join(_COLUMNS)}) "
            f"VALUES ({','.join('?' * len(_COLUMNS))})",
            (fact_id, record.file_id, record.content_hash, record.handling_class,
             int(record.protected), record.basis,
             canonical_json(list(record.evidence_refs)), record.reliability_state,
             record.observed_at),
        )
        return fact_id

    def _live_rows(self, file_id: str, content_hash: str) -> list[sqlite3.Row]:
        return list(self._conn.execute(
            f"SELECT * FROM {CLASSIFICATIONS_TABLE} "
            "WHERE file_id = ? AND content_hash = ? AND superseded_by IS NULL "
            "  AND reliability_state <> ? "
            "ORDER BY observed_at, rowid",
            (file_id, content_hash, REJECTED),
        ))

    def current(self, file_id: str, content_hash: str) -> ClassificationRecord | None:
        """The one current classification for this file VERSION, or None."""
        rows = self._live_rows(file_id, content_hash)
        if not rows:
            return None
        return strongest([_row_to_record(row) for row in rows])

    def current_fact_id(self, file_id: str, content_hash: str) -> str | None:
        """The row id `mark_superseded` needs. `ClassificationRecord` carries none."""
        rows = self._live_rows(file_id, content_hash)
        if not rows:
            return None
        pairs = [(row["fact_id"], _row_to_record(row)) for row in rows]
        best = strongest([record for _, record in pairs])
        # `strongest` returns one of the objects it was given, so identity is the
        # match. Equality would collapse two byte-identical live rows into one and
        # hide the ambiguity `current` raises on.
        return next(fact_id for fact_id, record in pairs if record is best)

    def supersede(self, old_fact_id: str, new_fact_id: str, reason: str) -> None:
        """P1's three columns. P7 does not copy P1's supersede implementation."""
        mark_superseded(self._conn, CLASSIFICATIONS_TABLE,
                        old_id=old_fact_id, new_id=new_fact_id, reason=reason)

    def history(self, file_id: str) -> list[ClassificationRecord]:
        """Every classification ever written for this file, oldest first."""
        return [_row_to_record(row) for row in self._conn.execute(
            f"SELECT * FROM {CLASSIFICATIONS_TABLE} WHERE file_id = ? "
            "ORDER BY observed_at, rowid", (file_id,))]

    def chain_for(self, fact_id: str) -> list[sqlite3.Row]:
        """P1's `chain`, exposed so a caller does not name P7's table itself."""
        return chain(self._conn, CLASSIFICATIONS_TABLE, fact_id)


def mirror_state(record: ClassificationRecord) -> dict:
    """The opaque dict P1 stores in `files.sensitivity_state` (D2's projection).

    P1 holds no handling-class vocabulary and validates nothing here; §8.4's classes
    are P7's. `file_id` is absent because it is the row's key, and `fact_id` is
    absent because it is not one of SPEC §2's eight fields -- a reader needing the
    classification's provenance reads the record, not the column.
    """
    if record.handling_class == UNREADABLE_UNCLASSIFIED:
        raise GateOutcomeNotAFileFact(
            f"{UNREADABLE_UNCLASSIFIED!r} never reaches files.sensitivity_state "
            "(D2): 'nothing has looked' must not be readable as 'this file carries "
            "nothing'"
        )
    return {
        "handling_class": record.handling_class,
        "protected": record.protected,
        "basis": record.basis,
        "reliability_state": record.reliability_state,
        "content_hash": record.content_hash,
        "evidence_refs": list(record.evidence_refs),
        "observed_at": record.observed_at,
    }


def mirror(conn: sqlite3.Connection, record: ClassificationRecord, *,
           component_version: str) -> None:
    """Project the authoritative record onto P1's column, through P1's setter.

    The single `UPDATE files` in the product's privacy path is P1's, inside
    `set_sensitivity_state`. `author` is not a parameter: M8 makes the acting part
    the author, and a log where the author is a caller-supplied value cannot answer
    §8.2's reconstruction question.
    """
    set_sensitivity_state(conn, record.file_id, state=mirror_state(record),
                          author=SUBSYSTEM, component_version=component_version)
```

- [ ] **Step 5: Add P7's schema to the `p7_conn` fixture in `tests/p7/conftest.py`**

Keep everything Task 1 put in the file; the `p7_conn` fixture gains one line.

```python
# tests/p7/conftest.py
import pytest

from database_agent.db import create_schema

from privacy.schema import create_privacy_schema


@pytest.fixture()
def p7_conn(conn):
    """P1's database with P7's tables added. `conn` is P1's root fixture and
    `tests/conftest.py` is not modified. Nothing imported across parts by name lives
    in this file: under pytest's default prepend import mode every `conftest.py` is
    the top-level module `conftest`, and the last one wins."""
    create_schema(conn)
    create_privacy_schema(conn)
    return conn
```

- [ ] **Step 6: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_classification_store.py -v`
Expected: PASS — 39 passed

- [ ] **Step 7: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–4 green, and P1–P5 still green (P7 modified no file belonging to another
part; `tests/p7/conftest.py` is P7's own).

- [ ] **Step 8: Commit**

```bash
git add src/privacy/schema.py src/privacy/classification_store.py tests/p7/conftest.py tests/p7/test_p7_classification_store.py
git commit -m "feat(P7): P7's own classification store, §3.13's ordering, and the sensitivity_state projection through P1's setter"
```

---

---

### Task 5: Policy — the four modes, consent grants, redaction settings, `policy_version`

**Files:**
- Create: `src/privacy/policy.py`
- Modify: `src/privacy/schema.py` (Task 4 created it; Task 5 adds one table and one line)
- Test: `tests/p7/test_p7_policy.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.OPERATION_MODES`, `.DISPLAY_FACETS`, `.CONSENT_OPTIONS`,
  `.MODE_SEMANTICS`, `.check_mode(value) -> str`, `.OutOfVocabulary`,
  `privacy.authorship.POLICY_SET`, `.CONSENT_GRANTED`, `.SUBSYSTEM`,
  `.event_defaults(*, event_type, **fields) -> dict[str, object]`,
  `database_agent.events.append_event(conn, **fields) -> int`,
  `database_agent.db.transaction(conn)`,
  `database_agent.supersede.mark_superseded(conn, table, *, old_id, new_id, reason) -> None`,
  `evidence_shape.canonical.canonical_json(value) -> str`,
  `privacy.schema.POLICIES_TABLE`.
- Produces (`schema.py`, added):
  - `POLICIES_TABLE: str = "privacy_policies"`, `POLICIES_DDL: str`;
    `create_privacy_schema` also executes it.
- Produces (`policy.py`):
  - `SHOWN: str = "shown"`, `REDACTED: str = "redacted"`,
    `REDACTION_VALUES: tuple[str, str] = (SHOWN, REDACTED)` (A7).
  - `NO_MODEL_USE: str = "no_model_use"` — validated against `CONSENT_OPTIONS` at import.
  - `UNSET_POLICY_VERSION: str = ""` — what a `Policy` carries before the gate mints one.
  - `Policy` — frozen: `policy_version: str`, `operation_mode: str`,
    `consent_grants: tuple[tuple[str, str], ...]`, `redaction_settings: dict`,
    `automatic_move_permissions: dict`, `plan_version: str`, `set_at: str`.
  - `set_policy(conn, policy, *, component_version, user_id, reason) -> str`
  - `current_policy(conn, *, plan_version) -> Policy | None` (A6)
  - `policy_at(conn, policy_version) -> Policy`
  - `grant_consent(conn, policy, scope, option, *, user_id, component_version, observed_at) -> str`
  - `revoke_consent(conn, policy, scope, *, user_id, component_version, observed_at) -> str`
  - `TranscriptionAuthorization` — frozen, `scope: str`, `__call__() -> bool`.
  - `transcription_authorized_for(conn, scope, *, plan_version) -> TranscriptionAuthorization`
  - `CallerSuppliedPolicyVersion`, `UnknownPolicyVersion`, `AmbiguousCurrentPolicy`.

**Done-means:** substrate for 5, 6, 8, 12; the P5 back-edge.

**Two more deviations, on top of the table above.**

- **A14 — `set_policy` drops `author` and gains a required `reason`.** Task 1's `event_defaults`
  *"fills `subsystem = "P7"` and never lets a caller override it, because M8's 'the acting part
  authors' is unmeetable from a log where the author is a parameter anyone may set."* An `author`
  keyword on `set_policy` is exactly that parameter. `reason` replaces it because
  `mark_superseded` refuses an empty one and because §8.8 requires the diff to be *"meaningful"* —
  a fixed string held in `policy.py` would make every privacy-policy diff line read the same, and
  §8.8 calls a silent widening of egress policy the least acceptable silent change in the product.
- **A15 — `transcription_authorized_for` gains `conn` and `plan_version`.** The predicate answers
  from the policy in force, and policy is plan-scoped (§8.8). The skeleton's one-argument form
  cannot reach a policy.

**One table, not two (A9), and the reason is the binding tuple.** A consent grant that did not mint
a new `policy_version` would leave a release minted before the grant still spendable after it —
`policy_version` is a binding term (B2), and Task 12's ledger checks it. §8.8 also lists *"Privacy
and model-consent policies"* as **one** plan-version item. So a policy version is the whole snapshot:
mode, grants, redaction settings, automatic-move permissions.

**One act, one event.** `_persist` mints, inserts, supersedes and appends nothing. `set_policy` is
`_persist` plus `policy_set`; `grant_consent` is `_persist` plus `consent_granted`; **`revoke_consent`
is `_persist` and no event at all** — the `consent_revoked` append belongs to sibling Task 15's
`revoke`, which is where §8.4's `prior_releases` and `retraction_limit` are assembled, and which
reads that event back out of the log. Two appends would put one act in the log twice.

**Policy is plan-scoped; classifications and audit records are not.** §8.8: *"The evidence database
remains shared across plan versions, but the destination tree and user policy define which
projections are valid in each version."* `current_policy` takes `plan_version`;
`ClassificationStore.current` does not, and a test asserts the asymmetry by signature rather than by
comment.

**Consent-grant scoping stays parameterised.** SPEC Open question 3: *"What is a 'corpus area'?
`cloud_assisted` permits a cloud model for 'selected corpus areas' (§8.4). A scan root (§1.1)? A
frozen tree node (§5.12)? An accepted group (§4)? A domain (§3.15)? Consent grants cannot be scoped
until this is named."* `scope` is an opaque string P7 neither parses nor validates. Task 21 asserts
P7 supplies no answer.

**The P5 back-edge is an adapter over a genuine mismatch, and the test says so.**
`transcription_authorized` is `Callable[[], bool]`, called as `transcription_authorized()` in
`src/extractors/long_tail.py:204`. It takes no `file_id` and no scope; P7's surfaces are all
per-file or per-scope. `TranscriptionAuthorization` closes over the scope and **carries it as a
field**, so the scope P5 cannot pass is visible on the object rather than hidden inside a lambda.
**Which of the four consent options authorizes speech-to-text is not stated anywhere in the design.**
§2.9 requires *"only under an explicit privacy and compute policy"*. The rule used is the narrowest
one expressible in the vocabulary P7 owns — an **explicit** grant naming the scope, whose option is
anything other than `no_model_use` — and it is reported as a reading, not a ratification.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_policy.py
"""§8.4's four operation modes, its consent options, its five configurable redaction
facets, and the `policy_version` the gate mints.

W1 is NOT here. This file never asserts what the resolved default is, because
`policy.py` holds no default: `current_policy` returns `None` when nothing has been
set and Task 6 is what turns that into §8.4's local-first floor. A default living in
two modules is a default that can disagree with itself, and the one it would disagree
about is whether content leaves the device.
"""
from __future__ import annotations

import inspect
import json
import sqlite3

import pytest

from database_agent.supersede import SUPERSEDE_COLUMNS

from extractors.dispatch import extract

from privacy.authorship import CONSENT_GRANTED, POLICY_SET, SUBSYSTEM
from privacy.classification_store import ClassificationStore
from privacy.policy import (
    NO_MODEL_USE,
    REDACTED,
    REDACTION_VALUES,
    SHOWN,
    UNSET_POLICY_VERSION,
    AmbiguousCurrentPolicy,
    CallerSuppliedPolicyVersion,
    Policy,
    TranscriptionAuthorization,
    UnknownPolicyVersion,
    current_policy,
    grant_consent,
    policy_at,
    revoke_consent,
    set_policy,
    transcription_authorized_for,
)
from privacy.schema import POLICIES_TABLE
from privacy.vocabulary import (
    CONSENT_OPTIONS,
    DISPLAY_FACETS,
    OPERATION_MODES,
    OutOfVocabulary,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"
PLAN = "plan-1"

ALL_REDACTED = {facet: REDACTED for facet in DISPLAY_FACETS}


def a_policy(**over) -> Policy:
    base = dict(policy_version=UNSET_POLICY_VERSION, operation_mode="local_model",
                consent_grants=(), redaction_settings=dict(ALL_REDACTED),
                automatic_move_permissions={}, plan_version=PLAN, set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


def store(conn, **over) -> str:
    return set_policy(conn, a_policy(**over), component_version=COMPONENT,
                      user_id="joseph", reason="the user chose local-model mode")


# --- the table -------------------------------------------------------------

def test_the_policy_table_carries_p1s_three_supersede_columns(p7_conn):
    columns = {row["name"] for row in p7_conn.execute(
        f"PRAGMA table_info({POLICIES_TABLE})")}
    assert set(SUPERSEDE_COLUMNS) <= columns


def test_a_policy_row_cannot_be_deleted(p7_conn):
    version = store(p7_conn)
    with pytest.raises(sqlite3.IntegrityError, match="superseded"):
        p7_conn.execute(f"DELETE FROM {POLICIES_TABLE} WHERE policy_version = ?",
                        (version,))


def test_a_policy_row_cannot_be_overwritten(p7_conn):
    # §8.8's diff needs both sides. A mutated policy row is a diff with one side.
    version = store(p7_conn)
    with pytest.raises(sqlite3.IntegrityError, match="superseded"):
        p7_conn.execute(
            f"UPDATE {POLICIES_TABLE} SET operation_mode = ? WHERE policy_version = ?",
            ("cloud_assisted", version))


# --- the gate mints the version --------------------------------------------

def test_the_gate_mints_the_policy_version(p7_conn):
    # SPEC §6: "the gate owns the policy, so the caller does not supply this value,
    # it echoes it."
    version = store(p7_conn)
    assert isinstance(version, str) and version != UNSET_POLICY_VERSION


def test_a_caller_supplied_policy_version_is_refused(p7_conn):
    with pytest.raises(CallerSuppliedPolicyVersion):
        set_policy(p7_conn, a_policy(policy_version="policy-i-picked"),
                   component_version=COMPONENT, user_id="joseph", reason="because")


def test_two_policies_never_share_a_version(p7_conn):
    first = store(p7_conn)
    second = store(p7_conn, operation_mode="offline", set_at=LATER)
    assert first != second


def test_policy_at_returns_the_policy_that_was_set(p7_conn):
    version = store(p7_conn, operation_mode="offline")
    loaded = policy_at(p7_conn, version)
    assert loaded.policy_version == version
    assert loaded.operation_mode == "offline"
    assert loaded.redaction_settings == ALL_REDACTED
    assert loaded.plan_version == PLAN


def test_an_unknown_policy_version_raises(p7_conn):
    with pytest.raises(UnknownPolicyVersion):
        policy_at(p7_conn, "policy-never-minted")


def test_current_policy_is_none_before_anything_is_set(p7_conn):
    # A6. "No policy has been set" is a fact, and it is Task 6's input, not an
    # occasion for `policy.py` to invent one.
    assert current_policy(p7_conn, plan_version=PLAN) is None


# --- supersede, never mutate -----------------------------------------------

def test_a_policy_change_supersedes_the_prior_policy(p7_conn):
    first = store(p7_conn)
    second = store(p7_conn, operation_mode="offline", set_at=LATER)
    row = p7_conn.execute(
        f"SELECT * FROM {POLICIES_TABLE} WHERE policy_version = ?", (first,)).fetchone()
    assert row["superseded_by"] == second
    assert row["supersede_reason"]
    assert current_policy(p7_conn, plan_version=PLAN).policy_version == second


def test_the_prior_policy_remains_readable(p7_conn):
    first = store(p7_conn)
    store(p7_conn, operation_mode="offline", set_at=LATER)
    # §8.5 replay reproduces "the policy in force at each call", so a superseded
    # policy version must stay loadable by name forever.
    assert policy_at(p7_conn, first).operation_mode == "local_model"


def test_a_policy_change_appends_policy_set_once(p7_conn):
    store(p7_conn)
    rows = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                           (POLICY_SET,)).fetchall()
    assert len(rows) == 1
    assert rows[0]["subsystem"] == SUBSYSTEM == "P7"
    assert rows[0]["user_id"] == "joseph"


def test_the_policy_set_explanation_carries_a_diffable_policy(p7_conn):
    # §8.8 requires a privacy-policy change to appear as a first-class diff line.
    # The explanation carries both sides and the reason, so the diff is a read of
    # the log rather than a recomputation from two snapshots.
    store(p7_conn)
    second = store(p7_conn, operation_mode="offline", set_at=LATER,
                   consent_grants=(("Academics", "cloud_model"),))
    payload = json.loads(p7_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ? ORDER BY event_id DESC",
        (POLICY_SET,)).fetchone()["explanation"])
    assert payload["policy_version"] == second
    assert payload["operation_mode"] == "offline"
    assert payload["superseded_policy_version"]
    assert payload["consent_grants"] == [["Academics", "cloud_model"]]
    assert payload["reason"]


def test_two_live_policies_at_one_plan_version_raise_rather_than_pick(p7_conn):
    store(p7_conn)
    p7_conn.execute(
        f"INSERT INTO {POLICIES_TABLE} (policy_version, plan_version, operation_mode,"
        " consent_grants, redaction_settings, automatic_move_permissions, set_at)"
        " VALUES (?,?,?,?,?,?,?)",
        ("policy-smuggled", PLAN, "cloud_assisted", "[]", "{}", "{}", LATER))
    with pytest.raises(AmbiguousCurrentPolicy):
        current_policy(p7_conn, plan_version=PLAN)


# --- plan scoping ----------------------------------------------------------

def test_policy_is_plan_scoped(p7_conn):
    store(p7_conn)
    assert current_policy(p7_conn, plan_version="plan-2") is None


def test_each_plan_version_carries_its_own_current_policy(p7_conn):
    store(p7_conn, operation_mode="offline")
    store(p7_conn, operation_mode="local_model", plan_version="plan-2", set_at=LATER)
    assert current_policy(p7_conn, plan_version=PLAN).operation_mode == "offline"
    assert current_policy(p7_conn, plan_version="plan-2").operation_mode == "local_model"


def test_classifications_are_not_plan_scoped(p7_conn):
    # §8.8: "The evidence database remains shared across plan versions." Asserted by
    # signature, so a later plan_version parameter on the store is a failing test.
    assert "plan_version" not in inspect.signature(ClassificationStore.current).parameters
    assert "plan_version" in inspect.signature(current_policy).parameters


# --- the four modes --------------------------------------------------------

def test_policy_holds_no_second_list_of_modes(p7_conn):
    import privacy.policy as module
    held = [value for name, value in vars(module).items()
            if not name.startswith("_") and isinstance(value, str)]
    assert not [text for text in held if text in OPERATION_MODES]


def test_every_mode_in_the_vocabulary_is_settable(p7_conn):
    for index, mode in enumerate(OPERATION_MODES):
        version = store(p7_conn, operation_mode=mode, plan_version=f"plan-{index}")
        assert policy_at(p7_conn, version).operation_mode == mode


def test_a_mode_outside_the_vocabulary_is_a_load_error(p7_conn):
    # SPEC §1: "A value outside this set is a load error, not a fallback."
    with pytest.raises(OutOfVocabulary):
        a_policy(operation_mode="mostly_offline")


# --- redaction settings ----------------------------------------------------

def test_the_two_redaction_values_are_the_specs_own(p7_conn):
    # SPEC §10: "names | previews | thumbnails | ocr_text | location_data
    #            each shown | redacted".
    assert REDACTION_VALUES == ("shown", "redacted") == (SHOWN, REDACTED)


def test_an_unknown_facet_is_a_load_error(p7_conn):
    with pytest.raises(OutOfVocabulary):
        a_policy(redaction_settings={"filenames": REDACTED})


def test_an_unknown_redaction_value_is_a_load_error(p7_conn):
    with pytest.raises(OutOfVocabulary):
        a_policy(redaction_settings={DISPLAY_FACETS[0]: "blurred"})


def test_a_partial_redaction_map_is_accepted_and_left_to_task_6(p7_conn):
    # The migrated-from-nothing case. Refusing it here would make W1 unreachable:
    # Task 6's job is to fill an absent facet with its more redacting value, and it
    # cannot fill what `Policy` refuses to hold.
    partial = a_policy(redaction_settings={DISPLAY_FACETS[0]: SHOWN})
    assert set(partial.redaction_settings) == {DISPLAY_FACETS[0]}


def test_the_five_facets_are_task_2s_and_policy_names_no_sixth(p7_conn):
    assert len(DISPLAY_FACETS) == 5
    version = store(p7_conn, redaction_settings=dict(ALL_REDACTED))
    assert set(policy_at(p7_conn, version).redaction_settings) == set(DISPLAY_FACETS)


# --- consent grants --------------------------------------------------------

def test_grant_consent_mints_a_new_version_carrying_the_grant(p7_conn):
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    second = grant_consent(p7_conn, first, "Academics", "cloud_model",
                           user_id="joseph", component_version=COMPONENT,
                           observed_at=LATER)
    assert second != first.policy_version
    assert policy_at(p7_conn, second).consent_grants == (("Academics", "cloud_model"),)
    # The grant is why the version changes: a release minted under `first` must not
    # survive into a policy it was not authorized under (B2's binding tuple).
    assert policy_at(p7_conn, first.policy_version).consent_grants == ()


def test_grant_consent_appends_consent_granted_once_and_no_policy_set(p7_conn):
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    grant_consent(p7_conn, first, "Academics", "cloud_model", user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    granted = p7_conn.execute("SELECT count(*) c FROM events WHERE event_type = ?",
                              (CONSENT_GRANTED,)).fetchone()["c"]
    policies = p7_conn.execute("SELECT count(*) c FROM events WHERE event_type = ?",
                               (POLICY_SET,)).fetchone()["c"]
    assert (granted, policies) == (1, 1)      # the 1 policy_set is the initial set


def test_an_option_outside_the_four_is_a_load_error(p7_conn):
    first = policy_at(p7_conn, store(p7_conn))
    with pytest.raises(OutOfVocabulary):
        grant_consent(p7_conn, first, "Academics", "cloud_model_but_only_tuesdays",
                      user_id="joseph", component_version=COMPONENT, observed_at=LATER)


def test_the_four_options_are_84s_own(p7_conn):
    # §8.4: the user should "choose whether to allow a local model, a cloud model, a
    # redacted prompt, or no model use."
    assert CONSENT_OPTIONS == ("local_model", "cloud_model", "redacted_prompt",
                               "no_model_use")


def test_revoke_consent_removes_the_grant_and_mints_a_version(p7_conn):
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    granted = policy_at(p7_conn, grant_consent(
        p7_conn, first, "Academics", "cloud_model", user_id="joseph",
        component_version=COMPONENT, observed_at=LATER))
    revoked = revoke_consent(p7_conn, granted, "Academics", user_id="joseph",
                             component_version=COMPONENT, observed_at=LATER)
    assert policy_at(p7_conn, revoked).consent_grants == ()
    assert policy_at(p7_conn, granted.policy_version).consent_grants == \
        (("Academics", "cloud_model"),)


def test_revoke_consent_appends_no_event(p7_conn):
    # Sibling Task 15 pins this: `consent_revoked` is appended once, by `revoke`,
    # which is where §8.4's prior-release list and retraction limit are assembled.
    # Two appends would put one act in the log twice and §8.4's `prior_releases` is
    # read back out of that log.
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    revoke_consent(p7_conn, first, "Academics", user_id="joseph",
                   component_version=COMPONENT, observed_at=LATER)
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before


def test_the_scope_is_opaque_and_p7_defines_no_corpus_area(p7_conn):
    # SPEC Open question 3, held: "Consent grants cannot be scoped until this is
    # named." A scan root, a frozen node, an accepted group and a domain are all
    # accepted, unparsed, because P7 has no basis to prefer one.
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    for scope in ("/Users/j/Corpus", "node-17", "group-4", "Finance"):
        first = policy_at(p7_conn, grant_consent(
            p7_conn, first, scope, "cloud_model", user_id="joseph",
            component_version=COMPONENT, observed_at=LATER))
    assert [grant[0] for grant in first.consent_grants] == \
        ["/Users/j/Corpus", "node-17", "group-4", "Finance"]


# --- the P5 back-edge (M10) ------------------------------------------------

def test_the_adapter_satisfies_p5s_zero_argument_predicate(p7_conn):
    predicate = transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)
    assert isinstance(predicate, TranscriptionAuthorization)
    assert inspect.signature(predicate).parameters == {}
    assert predicate() is False


def test_the_adapter_carries_the_scope_p5_cannot_pass(p7_conn):
    # The mismatch is REPORTED, not patched: P5's call site is
    # `transcription_authorized()` with no arguments, so the scope has to live on
    # the object. A lambda would hide it.
    predicate = transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)
    assert predicate.scope == "Academics"


def test_p5s_call_site_takes_no_scope(p7_conn):
    # Asserted against P5 as shipped, so the day P5's signature widens this test
    # fails and the adapter can be deleted rather than quietly kept.
    parameter = inspect.signature(extract).parameters["transcription_authorized"]
    assert "Callable[[], bool]" in str(parameter.annotation)


def test_an_explicit_grant_authorizes_and_absence_does_not(p7_conn):
    # §2.9: speech-to-text runs "only under an explicit privacy and compute policy".
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    assert transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)() \
        is False
    grant_consent(p7_conn, first, "Academics", "local_model", user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    assert transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)() \
        is True
    assert transcription_authorized_for(p7_conn, "Finance", plan_version=PLAN)() \
        is False


def test_no_model_use_does_not_authorize(p7_conn):
    assert NO_MODEL_USE in CONSENT_OPTIONS
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    grant_consent(p7_conn, first, "Academics", NO_MODEL_USE, user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    assert transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)() \
        is False


def test_the_adapter_reads_the_policy_in_force_and_caches_nothing(p7_conn):
    predicate = transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)
    assert predicate() is False
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    grant_consent(p7_conn, first, "Academics", "cloud_model", user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    assert predicate() is True
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_policy.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.policy'` (collection fails on the
first import of the module under test).

- [ ] **Step 3: Add `privacy_policies` to `src/privacy/schema.py`**

Append the DDL and add one line to `create_privacy_schema`. Everything Task 4 wrote stays.

```python
#: P7's policy table. One row per policy VERSION; a change supersedes, never mutates.
POLICIES_TABLE = "privacy_policies"

POLICIES_DDL = f"""
CREATE TABLE IF NOT EXISTS {POLICIES_TABLE} (
    policy_version             TEXT PRIMARY KEY,
    {SUPERSEDE_ADAPTER_COLUMN} TEXT GENERATED ALWAYS AS (policy_version) VIRTUAL,
    plan_version               TEXT NOT NULL,
    operation_mode             TEXT NOT NULL,
    consent_grants             TEXT NOT NULL,
    redaction_settings         TEXT NOT NULL,
    automatic_move_permissions TEXT NOT NULL,
    set_at                     TEXT NOT NULL,
    supersedes                 TEXT,
    superseded_by              TEXT,
    supersede_reason           TEXT
);
CREATE INDEX IF NOT EXISTS privacy_policies_plan
    ON {POLICIES_TABLE} (plan_version);
CREATE TRIGGER IF NOT EXISTS privacy_policies_no_delete
BEFORE DELETE ON {POLICIES_TABLE}
BEGIN SELECT RAISE(ABORT, 'a policy is superseded, never removed (§8.2, §8.5 replay)'); END;
-- §8.8's diff needs both sides. The three supersede columns stay writable.
CREATE TRIGGER IF NOT EXISTS privacy_policies_never_overwritten
BEFORE UPDATE OF policy_version, plan_version, operation_mode, consent_grants,
                 redaction_settings, automatic_move_permissions, set_at
    ON {POLICIES_TABLE}
BEGIN SELECT RAISE(ABORT, 'a policy is superseded, never overwritten (§8.2, §8.8)'); END;
"""


def create_privacy_schema(conn: sqlite3.Connection) -> None:
    """Create every P7-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(CLASSIFICATIONS_DDL)
    conn.executescript(POLICIES_DDL)
```

- [ ] **Step 4: Write `src/privacy/policy.py`**

```python
# src/privacy/policy.py
"""§8.4's operation modes, consent grants and redaction settings, as one versioned
policy record.

**One policy version is the whole snapshot.** §8.8 lists "Privacy and model-consent
policies" as a single plan-version item, and B2 makes `policy_version` a binding term
of every release. A consent grant that did not mint a new version would leave a
release minted before the grant still spendable after it, which is the one silent
widening of egress policy §8.8 calls the least acceptable silent change in the
product. So mode, grants, redaction settings and automatic-move permissions travel
together and a change to any of them is a new version.

**The gate mints the version; the caller echoes it.** SPEC §6. A `Policy` handed in
carries `UNSET_POLICY_VERSION` and is refused if it carries anything else.

**Supersede, never mutate (§8.2).** The prior version stays loadable by name forever,
because §8.5 replay must reproduce "the policy in force at each call".

**One act, one event.** `_persist` appends nothing. `set_policy` adds `policy_set`;
`grant_consent` adds `consent_granted`; `revoke_consent` adds NOTHING -- the
`consent_revoked` append belongs to `privacy.revocation.revoke`, which assembles
§8.4's prior-release list and retraction limit and reads that event back out of the
log.

**This module holds no default.** §8.4's local-first `must` is W1 and lives in
`privacy.defaults`. `current_policy` returns `None` when nothing has been set. A
default in two modules is a default that can disagree with itself, and the thing it
would disagree about is whether content leaves the device.

**`scope` is opaque.** SPEC Open question 3 -- "What is a 'corpus area'?" -- is open,
so a scan root, a frozen node id, a group id and a domain name are all accepted,
unparsed. P7 has no basis to prefer one and does not invent it.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass, replace

from database_agent.db import transaction
from database_agent.events import append_event
from database_agent.supersede import mark_superseded

from evidence_shape.canonical import canonical_json

from privacy.authorship import CONSENT_GRANTED, POLICY_SET, event_defaults
from privacy.schema import POLICIES_TABLE
from privacy.vocabulary import (
    CONSENT_OPTIONS,
    DISPLAY_FACETS,
    OutOfVocabulary,
    check_mode,
)

#: SPEC §10: "names | previews | thumbnails | ocr_text | location_data -- each
#: shown | redacted". Two values, named once. Reported to Task 2's author: if
#: `vocabulary.py` adopts them, this module re-exports and deletes its own.
SHOWN = "shown"
REDACTED = "redacted"
REDACTION_VALUES: tuple[str, str] = (SHOWN, REDACTED)

#: The consent option that authorizes nothing. Named so `transcription_authorized_for`
#: does not index into a tuple, and validated at import so it cannot drift from
#: Task 2's vocabulary.
NO_MODEL_USE = "no_model_use"
if NO_MODEL_USE not in CONSENT_OPTIONS:
    raise ImportError(
        f"{NO_MODEL_USE!r} is not one of §8.4's four consent options "
        f"{CONSENT_OPTIONS!r}; a value outside the set is a load error"
    )

#: What a `Policy` carries before the gate mints one (SPEC §6).
UNSET_POLICY_VERSION = ""

_COLUMNS = (
    "policy_version", "plan_version", "operation_mode", "consent_grants",
    "redaction_settings", "automatic_move_permissions", "set_at",
)


class CallerSuppliedPolicyVersion(Exception):
    """The gate owns the policy version; a caller offered one (SPEC §6)."""


class UnknownPolicyVersion(Exception):
    """No policy was ever minted under that version."""


class AmbiguousCurrentPolicy(Exception):
    """Two live policies at one plan version. Raised, never resolved by picking."""


@dataclass(frozen=True)
class Policy:
    """§8.4's authorizing policy: the mode, the grants, and the redaction settings.

    `redaction_settings` may be PARTIAL. Filling an absent facet with its more
    redacting value is W1's job (`privacy.defaults`), and a `Policy` that refused a
    partial map would make the migrated-from-nothing case unreachable.
    """

    policy_version: str
    operation_mode: str
    consent_grants: tuple[tuple[str, str], ...]
    redaction_settings: dict
    automatic_move_permissions: dict
    plan_version: str
    set_at: str

    def __post_init__(self) -> None:
        check_mode(self.operation_mode)
        for facet, value in self.redaction_settings.items():
            if facet not in DISPLAY_FACETS:
                raise OutOfVocabulary(
                    f"{facet!r} is not one of §8.4's five configurable facets "
                    f"{DISPLAY_FACETS!r}")
            if value not in REDACTION_VALUES:
                raise OutOfVocabulary(
                    f"{value!r} is not one of {REDACTION_VALUES!r} for facet {facet!r}")
        for scope, option in self.consent_grants:
            if option not in CONSENT_OPTIONS:
                raise OutOfVocabulary(
                    f"{option!r} is not one of §8.4's four consent options "
                    f"{CONSENT_OPTIONS!r} (scope {scope!r})")
        for scope, permitted in self.automatic_move_permissions.items():
            if not isinstance(permitted, bool):
                raise OutOfVocabulary(
                    f"automatic-move permission for {scope!r} is {permitted!r}; "
                    "§8.4 permits or does not permit, and nothing between")


def _row_to_policy(row: sqlite3.Row) -> Policy:
    return Policy(
        policy_version=row["policy_version"],
        operation_mode=row["operation_mode"],
        consent_grants=tuple(tuple(pair) for pair in
                             json.loads(row["consent_grants"])),
        redaction_settings=json.loads(row["redaction_settings"]),
        automatic_move_permissions=json.loads(row["automatic_move_permissions"]),
        plan_version=row["plan_version"],
        set_at=row["set_at"],
    )


def _live_row(conn: sqlite3.Connection, plan_version: str) -> sqlite3.Row | None:
    rows = list(conn.execute(
        f"SELECT * FROM {POLICIES_TABLE} "
        "WHERE plan_version = ? AND superseded_by IS NULL ORDER BY set_at, rowid",
        (plan_version,)))
    if len(rows) > 1:
        raise AmbiguousCurrentPolicy(
            f"{len(rows)} live policies at plan version {plan_version!r}; "
            "one must supersede the other (§8.2)")
    return rows[0] if rows else None


def _persist(conn: sqlite3.Connection, policy: Policy, *,
             supersede_reason: str) -> str:
    """Mint a version, insert the row, supersede the prior one. Appends no event."""
    if policy.policy_version != UNSET_POLICY_VERSION:
        raise CallerSuppliedPolicyVersion(
            f"policy_version {policy.policy_version!r} was supplied by the caller; "
            "the gate owns the policy and the caller echoes it (SPEC §6)")
    version = f"policy-{uuid.uuid4().hex}"
    with transaction(conn):
        prior = _live_row(conn, policy.plan_version)
        conn.execute(
            f"INSERT INTO {POLICIES_TABLE} ({','.join(_COLUMNS)}) "
            f"VALUES ({','.join('?' * len(_COLUMNS))})",
            (version, policy.plan_version, policy.operation_mode,
             canonical_json([list(pair) for pair in policy.consent_grants]),
             canonical_json(policy.redaction_settings),
             canonical_json(policy.automatic_move_permissions), policy.set_at),
        )
        if prior is not None:
            mark_superseded(conn, POLICIES_TABLE, old_id=prior["policy_version"],
                            new_id=version, reason=supersede_reason)
    return version


def _explanation(conn: sqlite3.Connection, version: str, **extra) -> str:
    policy = policy_at(conn, version)
    prior = conn.execute(
        f"SELECT supersedes FROM {POLICIES_TABLE} WHERE policy_version = ?",
        (version,)).fetchone()["supersedes"]
    payload = {
        "policy_version": version,
        "superseded_policy_version": prior,
        "plan_version": policy.plan_version,
        "operation_mode": policy.operation_mode,
        "consent_grants": [list(pair) for pair in policy.consent_grants],
        "redaction_settings": policy.redaction_settings,
        "automatic_move_permissions": policy.automatic_move_permissions,
    }
    payload.update(extra)
    return canonical_json(payload)


def set_policy(conn: sqlite3.Connection, policy: Policy, *,
               component_version: str, user_id: str, reason: str) -> str:
    """Mint and record a policy version, and append §8.4's `policy_set` event.

    `reason` is required and is the caller's: §8.8 requires the plan diff to be
    "meaningful", and a fixed sentence held here would make every privacy-policy
    diff line read the same. There is no `author` parameter -- M8 makes the acting
    part the author, and a log where the author is a caller-supplied value cannot
    answer §8.2's reconstruction question.
    """
    if not reason.strip():
        raise ValueError("a policy change carries a reason (§8.2, §8.8)")
    version = _persist(conn, policy, supersede_reason=reason)
    append_event(conn, **event_defaults(
        event_type=POLICY_SET, user_id=user_id, observed_at=policy.set_at,
        component_version=component_version,
        explanation=_explanation(conn, version, reason=reason)))
    return version


def current_policy(conn: sqlite3.Connection, *, plan_version: str) -> Policy | None:
    """The policy in force for this plan version, or None if none has been set.

    None is a fact, not a gap: §8.4's local-first floor is W1's and lives in
    `privacy.defaults`, which is what turns None into a resolved posture.
    """
    row = _live_row(conn, plan_version)
    return None if row is None else _row_to_policy(row)


def policy_at(conn: sqlite3.Connection, policy_version: str) -> Policy:
    """Any policy version, superseded or not. §8.5 replay reads through this."""
    row = conn.execute(
        f"SELECT * FROM {POLICIES_TABLE} WHERE policy_version = ?",
        (policy_version,)).fetchone()
    if row is None:
        raise UnknownPolicyVersion(policy_version)
    return _row_to_policy(row)


def grant_consent(conn: sqlite3.Connection, policy: Policy, scope: str, option: str,
                  *, user_id: str, component_version: str, observed_at: str) -> str:
    """Add one §8.4 consent grant, as a new policy version. Appends `consent_granted`."""
    if option not in CONSENT_OPTIONS:
        raise OutOfVocabulary(
            f"{option!r} is not one of §8.4's four consent options {CONSENT_OPTIONS!r}")
    grants = tuple(pair for pair in policy.consent_grants if pair[0] != scope)
    revised = replace(policy, policy_version=UNSET_POLICY_VERSION,
                      consent_grants=grants + ((scope, option),), set_at=observed_at)
    version = _persist(conn, revised, supersede_reason=canonical_json(
        {"act": "consent_granted", "scope": scope, "option": option}))
    append_event(conn, **event_defaults(
        event_type=CONSENT_GRANTED, user_id=user_id, observed_at=observed_at,
        component_version=component_version,
        explanation=_explanation(conn, version, granted_scope=scope,
                                 granted_option=option)))
    return version


def revoke_consent(conn: sqlite3.Connection, policy: Policy, scope: str, *,
                   user_id: str, component_version: str, observed_at: str) -> str:
    """Withdraw every grant at `scope` and return the new policy version.

    **Appends no event.** `privacy.revocation.revoke` appends `consent_revoked`
    once, because that is where §8.4's prior-release list and retraction limit are
    assembled and where the event is read back out of the log. `user_id` is on the
    signature because it is the acting user and `revoke` carries it into the event.
    """
    revised = replace(
        policy, policy_version=UNSET_POLICY_VERSION, set_at=observed_at,
        consent_grants=tuple(p for p in policy.consent_grants if p[0] != scope))
    return _persist(conn, revised, supersede_reason=canonical_json(
        {"act": "consent_revoked", "scope": scope, "user_id": user_id,
         "component_version": component_version}))


@dataclass(frozen=True)
class TranscriptionAuthorization:
    """P5's `Callable[[], bool]`, with the scope P5's call site cannot pass.

    `src/extractors/long_tail.py:204` calls `transcription_authorized()` with no
    arguments. P7's surfaces are per-file or per-scope, so the scope has to be
    closed over -- and it is carried as a FIELD rather than captured in a lambda so
    the mismatch stays visible to a reader and to a test.
    """

    conn: sqlite3.Connection
    scope: str
    plan_version: str

    def __call__(self) -> bool:
        policy = current_policy(self.conn, plan_version=self.plan_version)
        if policy is None:
            return False
        return any(scope == self.scope and option != NO_MODEL_USE
                   for scope, option in policy.consent_grants)


def transcription_authorized_for(conn: sqlite3.Connection, scope: str, *,
                                 plan_version: str) -> TranscriptionAuthorization:
    """§2.9's speech-to-text authorization, as P5's zero-argument predicate (M10).

    §2.9 permits transcripts "only under an explicit privacy and compute policy".
    **Which of the four consent options authorizes speech-to-text is not stated
    anywhere in the design.** The rule here is the narrowest one expressible in the
    vocabulary P7 owns -- an explicit grant naming this scope, whose option is
    anything other than `no_model_use` -- and it is a reported reading, not a
    ratification.
    """
    return TranscriptionAuthorization(conn, scope, plan_version)
```

- [ ] **Step 5: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_policy.py -v`
Expected: PASS — 38 passed

- [ ] **Step 6: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–5 green, and P1–P5 still green.

- [ ] **Step 7: Commit**

```bash
git add src/privacy/policy.py src/privacy/schema.py tests/p7/test_p7_policy.py
git commit -m "feat(P7): the four operation modes, consent grants, redaction settings, and a gate-minted policy_version"
```

---

---

### Task 6: The local-first default (W1)

**Files:**
- Create: `src/privacy/defaults.py`
- Test: `tests/p7/test_p7_defaults.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.OPERATION_MODES`, `.DISPLAY_FACETS`, `.check_mode(value) -> str`,
  `.OutOfVocabulary`, `privacy.policy.Policy`, `.current_policy(conn, *, plan_version)
  -> Policy | None`, `.REDACTED`, `.SHOWN`, `.REDACTION_VALUES`, `.UNSET_POLICY_VERSION`.
- Produces (`defaults.py`):
  - `OFFLINE: str = "offline"`, `LOCAL_MODEL: str = "local_model"` — each validated through
    `check_mode` at import, so neither can drift from Task 2's vocabulary.
  - `LOCAL_FIRST_MODES: tuple[str, str] = (OFFLINE, LOCAL_MODEL)`
  - `MORE_REDACTING: Mapping[str, str]` — every facet in `DISPLAY_FACETS` → `REDACTED`.
  - `resolve_default_policy(stored, *, install_mode, plan_version, set_at) -> Policy` (A10)
  - `effective_policy(conn, *, plan_version, install_mode, set_at) -> Policy` (A16)
  - `assert_local_first(policy) -> None`
  - `DefaultPostureViolation`

**Done-means:** 12.

**A16 — `effective_policy` is added, and it is the function the gate calls.** The skeleton's
`Consumes` block lists `policy.current_policy` and its `Produces` block lists nothing that reads a
connection, so the composition — read the stored policy, resolve the absent parts — has no home. It
is one line and it is what Task 13 needs; without it every caller would compose it again and each
composition would be a place the floor could be forgotten.

**`install_mode` is a required keyword and it is the whole design of this task (A10).** SPEC
Contract out §5: *"Which of `offline` and `local_model` ships is still open (Open question 11) and
P7 will not guess it; what is closed is that the answer cannot be `hybrid` or `cloud_assisted`, and
that no build configuration, first-run flow, or migration may set one of those as the state a user
arrives at without choosing it."* A required keyword validated against `LOCAL_FIRST_MODES` is that
sentence made mechanical: `src/privacy/` holds **no default mode at all**, so Open question 11 is
structurally open rather than open by discipline, and the two modes it forbids are unreachable
through this door.

**W1 binds the DEFAULT, never the choice.** §8.4's `must` — *"The default posture must therefore be
local-first and data-minimizing"* — constrains what a user finds on install, not what they may pick
afterwards. So `resolve_default_policy` returns a stored `cloud_assisted` policy **unchanged**;
`assert_local_first` on that same policy raises. Those are two different questions and one test
proves they are, because collapsing them would either forbid a mode §8.4 explicitly offers or let
an install ship one it forbids.

**The more-redacting rule is the second half of the same `must`, and §8.4 settles its direction.**
*"A summary such as '11 protected identity records' may be safe to show, while a visible list of
passport filenames on a shared screen may not be."* The aggregate is the default; the expansion is
the user's act. Between `shown` and `redacted` the more redacting value is `redacted`, for every one
of §8.4's five configurable facets. An absent facet is filled; a facet the user set is left alone.
`consent_grants` defaults to nothing granted and `automatic_move_permissions` to nothing permitted —
§8.4: protected material *"should not be moved automatically without a user policy that explicitly
permits it"*, and an empty map explicitly permits nothing.

**The negative half is asserted by runtime introspection, not by grep, and the skeleton says why.**
Done-means 12 says *"by fixture and by grep over the shipped defaults"*; the skeleton overrides
that, because `hybrid` and `cloud_assisted` appear legitimately in `vocabulary.py`, in docstrings
and in denial messages, and *"a text scan would either pass vacuously or fail on a comment."* The
guard here walks every module under `src/privacy/`, skips any object that **is** one of
`vocabulary.py`'s own — identity, not name, so a re-export of `OPERATION_MODES` is not a false
positive — and asserts no remaining module-level value names either mode. It also asserts
`defaults.py` binds no configuration reader at all, which is what makes *"no build flag, packaged
configuration file, or first-run flow"* checkable rather than aspirational.

**This test does not assert which of the two ships.** Open question 11 stays open; both are accepted
and a test says so by name.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_defaults.py
"""Done-means 12 — §8.4's local-first `must` (W1), and the negative half that matters
more than the positive one.

The positive half: with no user configuration present, the resolved mode is one of
the two under which no content leaves the device, and every configurable redaction
setting resolves to its more redacting value.

The negative half: no code path, build flag, packaged configuration file or first-run
flow produces a starting mode of `hybrid` or `cloud_assisted`. Asserted by calling
the resolver over every reachable stored state and by walking the package's
module-level namespaces at run time -- not by grepping source text, because both mode
names appear legitimately in `vocabulary.py`, in docstrings and in denial messages,
and a text scan would either pass vacuously or fail on a comment.

What this file must NOT assert: which of `offline` and `local_model` ships. That is
SPEC Open question 11 and P7 will not guess it.
"""
from __future__ import annotations

import importlib
import pkgutil

import pytest

import privacy
import privacy.vocabulary as vocab
from privacy.defaults import (
    LOCAL_FIRST_MODES,
    LOCAL_MODEL,
    MORE_REDACTING,
    OFFLINE,
    DefaultPostureViolation,
    assert_local_first,
    effective_policy,
    resolve_default_policy,
)
from privacy.policy import (
    REDACTED,
    SHOWN,
    UNSET_POLICY_VERSION,
    Policy,
    set_policy,
)
from privacy.vocabulary import DISPLAY_FACETS, OPERATION_MODES, OutOfVocabulary

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
COMPONENT = "0.1.0"
PLAN = "plan-1"

#: The two names §8.4 forbids as a DEFAULT. Both remain modes a user may choose.
CLOUD_MODES = ("hybrid", "cloud_assisted")


def resolved(stored=None, *, install_mode=OFFLINE) -> Policy:
    return resolve_default_policy(stored, install_mode=install_mode,
                                  plan_version=PLAN, set_at=FIXED_CLOCK)


def a_stored_policy(**over) -> Policy:
    base = dict(policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
                consent_grants=(("Academics", "cloud_model"),),
                redaction_settings={facet: REDACTED for facet in DISPLAY_FACETS},
                automatic_move_permissions={"Academics": True}, plan_version=PLAN,
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


# --- the two modes under which nothing leaves the device --------------------

def test_the_two_local_first_modes_are_the_two_that_send_nothing(p7_conn):
    # §8.4: "Fully offline mode: No content leaves the device; only local rules and
    # local models may run." / "Local-model mode: Local extraction plus a
    # user-installed local LLM for eligible dossiers." The other two both permit a
    # cloud model, which is the posture §8.4 forbids as a DEFAULT.
    assert LOCAL_FIRST_MODES == (OFFLINE, LOCAL_MODEL) == ("offline", "local_model")
    assert set(LOCAL_FIRST_MODES) < set(OPERATION_MODES)
    assert set(OPERATION_MODES) - set(LOCAL_FIRST_MODES) == set(CLOUD_MODES)


def test_the_local_mode_names_are_task_2s_and_not_a_second_spelling(p7_conn):
    for mode in LOCAL_FIRST_MODES:
        assert vocab.check_mode(mode) == mode


def test_more_redacting_covers_every_facet(p7_conn):
    # §8.4's five configurable facets: "names, previews, thumbnails, OCR text, or
    # location data".
    assert set(MORE_REDACTING) == set(DISPLAY_FACETS)
    assert set(MORE_REDACTING.values()) == {REDACTED}
    assert SHOWN not in MORE_REDACTING.values()


# --- fresh install ----------------------------------------------------------

def test_a_fresh_install_resolves_to_the_named_local_mode(p7_conn):
    assert resolved(None, install_mode=OFFLINE).operation_mode == OFFLINE
    assert resolved(None, install_mode=LOCAL_MODEL).operation_mode == LOCAL_MODEL


def test_a_fresh_install_redacts_every_facet(p7_conn):
    assert resolved(None).redaction_settings == dict(MORE_REDACTING)


def test_a_fresh_install_grants_nothing_and_permits_no_automatic_move(p7_conn):
    # §8.4: protected material "should not be moved automatically without a user
    # policy that explicitly permits it." An empty map permits nothing explicitly.
    fresh = resolved(None)
    assert fresh.consent_grants == ()
    assert fresh.automatic_move_permissions == {}


def test_the_resolved_default_is_unpersisted(p7_conn):
    # A default nobody chose has no policy version. `set_policy` is what mints one,
    # and it is a user act with a reason (§8.8's meaningful diff).
    assert resolved(None).policy_version == UNSET_POLICY_VERSION


def test_the_resolved_default_passes_its_own_assertion(p7_conn):
    for mode in LOCAL_FIRST_MODES:
        assert_local_first(resolved(None, install_mode=mode))


# --- migrated from nothing --------------------------------------------------

def test_a_migrated_install_fills_every_absent_facet(p7_conn):
    # A policy row exists with a mode and no redaction settings -- the state a build
    # that predates §8.4's facets leaves behind.
    migrated = a_stored_policy(operation_mode=LOCAL_MODEL, redaction_settings={})
    assert resolved(migrated).redaction_settings == dict(MORE_REDACTING)


def test_a_partial_facet_map_is_completed_and_the_users_setting_survives(p7_conn):
    # Filling an absent facet is the default; overwriting a facet the user set would
    # be the product changing a choice behind their back (§8.8).
    partial = a_stored_policy(operation_mode=LOCAL_MODEL,
                              redaction_settings={DISPLAY_FACETS[0]: SHOWN})
    filled = resolved(partial).redaction_settings
    assert filled[DISPLAY_FACETS[0]] == SHOWN
    assert all(filled[facet] == REDACTED for facet in DISPLAY_FACETS[1:])


def test_every_reachable_stored_state_resolves_to_a_complete_facet_map(p7_conn):
    for stored in (None,
                   a_stored_policy(redaction_settings={}),
                   a_stored_policy(redaction_settings={DISPLAY_FACETS[2]: REDACTED}),
                   a_stored_policy()):
        assert set(resolved(stored).redaction_settings) == set(DISPLAY_FACETS)


# --- the floor is on the INSTALL, not on the user's choice ------------------

def test_a_user_chosen_cloud_mode_is_returned_unchanged(p7_conn):
    # §8.4: "Either remains a legitimate mode the user may choose; neither may be
    # what they find on install." W1 binds the default, never the choice.
    chosen = a_stored_policy(operation_mode="cloud_assisted")
    assert resolved(chosen).operation_mode == "cloud_assisted"
    assert resolved(chosen).consent_grants == (("Academics", "cloud_model"),)


def test_the_two_questions_are_different_and_the_test_proves_it(p7_conn):
    # `resolve_default_policy` answers "what is in force". `assert_local_first`
    # answers "is this a posture a user may arrive at without choosing it".
    # Collapsing them would either forbid a mode §8.4 offers or ship one it forbids.
    chosen = a_stored_policy(operation_mode="hybrid")
    assert resolved(chosen).operation_mode == "hybrid"
    with pytest.raises(DefaultPostureViolation):
        assert_local_first(resolved(chosen))


# --- the negative half ------------------------------------------------------

@pytest.mark.parametrize("mode", CLOUD_MODES)
def test_a_cloud_mode_cannot_be_the_install_mode(p7_conn, mode):
    with pytest.raises(DefaultPostureViolation):
        resolved(None, install_mode=mode)


@pytest.mark.parametrize("mode", CLOUD_MODES)
def test_a_cloud_mode_cannot_be_the_install_mode_over_a_stored_policy(p7_conn, mode):
    with pytest.raises(DefaultPostureViolation):
        resolved(a_stored_policy(redaction_settings={}), install_mode=mode)


def test_an_unknown_install_mode_is_a_load_error_and_not_a_posture_violation(p7_conn):
    # Two different failures. "A value outside this set is a load error, not a
    # fallback" is Task 2's; being a known mode that §8.4 forbids as a default is
    # W1's. A caller that catches one must not silently absorb the other.
    with pytest.raises(OutOfVocabulary):
        resolved(None, install_mode="mostly_offline")


def test_assert_local_first_rejects_a_shown_facet(p7_conn):
    # Data-minimizing is the second half of the same `must`, and §8.4's own example
    # settles the direction: the aggregate is safe to show, the expansion is not.
    almost = resolved(None)
    from dataclasses import replace
    loosened = replace(almost, redaction_settings={
        **almost.redaction_settings, DISPLAY_FACETS[0]: SHOWN})
    with pytest.raises(DefaultPostureViolation):
        assert_local_first(loosened)


def test_assert_local_first_rejects_an_incomplete_facet_map(p7_conn):
    from dataclasses import replace
    with pytest.raises(DefaultPostureViolation):
        assert_local_first(replace(resolved(None), redaction_settings={}))


def test_no_module_under_privacy_names_a_cloud_mode_at_module_level(p7_conn):
    # Runtime introspection of every module's namespace, the way
    # `tests/p3/test_p3_no_invention.py` established. Objects that ARE
    # `vocabulary.py`'s own are skipped by IDENTITY, not by name, so a legitimate
    # re-export of `OPERATION_MODES` or `MODE_SEMANTICS` is not a false positive
    # while a second private copy of either is a failure.
    vocabulary_objects = {id(value) for value in vars(vocab).values()}
    forbidden = set(CLOUD_MODES)
    offenders: list[str] = []
    for info in pkgutil.iter_modules(privacy.__path__):
        module = importlib.import_module(f"privacy.{info.name}")
        if module is vocab:
            continue
        for name, value in vars(module).items():
            if name.startswith("_") or id(value) in vocabulary_objects:
                continue
            found: set[str] = set()
            if isinstance(value, str):
                found = forbidden & {value}
            elif isinstance(value, (tuple, list, set, frozenset)):
                found = forbidden & {v for v in value if isinstance(v, str)}
            elif isinstance(value, dict):
                found = forbidden & (
                    {k for k in value if isinstance(k, str)}
                    | {v for v in value.values() if isinstance(v, str)})
            if found:
                offenders.append(f"privacy.{info.name}.{name} -> {sorted(found)}")
    assert not offenders


def test_defaults_reads_no_configuration_at_all(p7_conn):
    # "No build flag, packaged configuration file, or first-run flow." A module that
    # cannot reach a file or an environment variable cannot be handed a mode by one.
    import privacy.defaults as module
    readers = {"os", "sys", "pathlib", "Path", "json", "tomllib", "configparser",
               "environ", "getenv", "open", "importlib", "pkgutil"}
    assert not (readers & set(vars(module)))


def test_the_resolver_is_deterministic(p7_conn):
    assert resolved(None) == resolved(None)


def test_p7_names_no_winner_between_the_two_local_modes(p7_conn):
    # SPEC Open question 11, held open BY CONSTRUCTION: there is no default mode in
    # `src/privacy/` for a later reader to mistake for an answer. `install_mode` has
    # no default, so a build that forgets to name one does not start; it fails.
    import inspect
    parameter = inspect.signature(resolve_default_policy).parameters["install_mode"]
    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    import privacy.defaults as module
    held = [value for name, value in vars(module).items()
            if not name.startswith("_") and isinstance(value, str)]
    assert sorted(text for text in held if text in OPERATION_MODES) == \
        sorted(LOCAL_FIRST_MODES)


# --- what the gate actually calls -------------------------------------------

def test_effective_policy_falls_back_to_the_floor_when_nothing_is_set(p7_conn):
    policy = effective_policy(p7_conn, plan_version=PLAN, install_mode=OFFLINE,
                              set_at=FIXED_CLOCK)
    assert policy.operation_mode == OFFLINE
    assert policy.policy_version == UNSET_POLICY_VERSION
    assert_local_first(policy)


def test_effective_policy_reads_the_stored_policy_when_there_is_one(p7_conn):
    version = set_policy(
        p7_conn,
        a_stored_policy(operation_mode="cloud_assisted", redaction_settings={}),
        component_version=COMPONENT, user_id="joseph",
        reason="the user turned on cloud assistance for Academics")
    policy = effective_policy(p7_conn, plan_version=PLAN, install_mode=OFFLINE,
                              set_at=FIXED_CLOCK)
    assert policy.policy_version == version
    assert policy.operation_mode == "cloud_assisted"
    # The absent facets are still filled with the more redacting value: a stored
    # policy that never named a facet has not chosen `shown` for it.
    assert policy.redaction_settings == dict(MORE_REDACTING)
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_defaults.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.defaults'` (collection fails on the
first import of the module under test).

- [ ] **Step 3: Write `src/privacy/defaults.py`**

```python
# src/privacy/defaults.py
"""W1 — §8.4's local-first `must`, made mechanical.

§8.4: "The default posture must therefore be local-first and data-minimizing." The
design names no install mode, so P7 does not pick one: `install_mode` is a required
keyword and the only values it accepts are the two under which no content leaves the
device. `src/privacy/` therefore holds NO default mode, which is what keeps SPEC
Open question 11 -- which of `offline` and `local_model` ships -- open by
construction rather than by discipline, and what makes `hybrid` and `cloud_assisted`
unreachable as a starting state through this door.

Both halves of the `must` are here.

**Local-first** is `LOCAL_FIRST_MODES`: §8.4's "Fully offline mode: No content leaves
the device" and "Local-model mode: Local extraction plus a user-installed local LLM
for eligible dossiers." The other two both permit a cloud model without the user
having asked for one.

**Data-minimizing** is `MORE_REDACTING`. §8.4's own example settles the direction: "A
summary such as '11 protected identity records' may be safe to show, while a visible
list of passport filenames on a shared screen may not be." The aggregate is the
default and the expansion is the user's act, so every facet the design leaves
configurable resolves to `redacted`, nothing is granted, and nothing is permitted to
move automatically.

**The floor binds the DEFAULT, never the choice.** §8.4: either cloud mode "remains a
legitimate mode the user may choose; neither may be what they find on install." So
`resolve_default_policy` returns a stored `cloud_assisted` policy unchanged, and
`assert_local_first` on that same policy raises. Two questions, two functions.

This module reads no file, no environment variable and no build flag. That is not a
style preference: Done-means 12's negative half names "build flag, packaged
configuration file, or first-run flow", and a module that cannot reach one cannot be
handed a mode by one.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import replace
from types import MappingProxyType

from privacy.policy import REDACTED, Policy, UNSET_POLICY_VERSION, current_policy
from privacy.vocabulary import DISPLAY_FACETS, check_mode

#: §8.4's two local modes, named once and validated against Task 2's vocabulary at
#: import so neither can drift into a second spelling.
OFFLINE = check_mode("offline")
LOCAL_MODEL = check_mode("local_model")

#: The floor. NOT a default: the caller names which of the two its build ships.
LOCAL_FIRST_MODES: tuple[str, str] = (OFFLINE, LOCAL_MODEL)

#: Per facet, the more redacting of §8.4's two values. Five facets, one value.
MORE_REDACTING: Mapping[str, str] = MappingProxyType(
    {facet: REDACTED for facet in DISPLAY_FACETS})


class DefaultPostureViolation(Exception):
    """A starting state §8.4's `must` forbids: a cloud mode, or a facet left shown."""


def _check_install_mode(install_mode: str) -> str:
    """A load error and a posture violation are different failures (Task 2, W1)."""
    check_mode(install_mode)
    if install_mode not in LOCAL_FIRST_MODES:
        raise DefaultPostureViolation(
            f"{install_mode!r} permits a cloud model without the user having asked "
            f"for one; §8.4's default posture must be local-first, so the install "
            f"default is one of {LOCAL_FIRST_MODES!r}. Either remains a mode the "
            f"user may choose."
        )
    return install_mode


def resolve_default_policy(stored: Policy | None, *, install_mode: str,
                           plan_version: str, set_at: str) -> Policy:
    """The policy in force, with everything nobody chose resolved to the floor.

    `install_mode` has no default. A build that forgets to name one does not start.
    """
    _check_install_mode(install_mode)
    if stored is None:
        return Policy(
            policy_version=UNSET_POLICY_VERSION,
            operation_mode=install_mode,
            consent_grants=(),
            redaction_settings=dict(MORE_REDACTING),
            automatic_move_permissions={},
            plan_version=plan_version,
            set_at=set_at,
        )
    # The mode is the user's and is not touched. An ABSENT facet is filled; a facet
    # the user set survives -- overwriting it would be the product changing a choice
    # behind their back (§8.8).
    return replace(stored, redaction_settings={**MORE_REDACTING,
                                               **stored.redaction_settings})


def effective_policy(conn: sqlite3.Connection, *, plan_version: str,
                     install_mode: str, set_at: str) -> Policy:
    """`current_policy` with the floor applied. The one composition the gate calls."""
    return resolve_default_policy(
        current_policy(conn, plan_version=plan_version),
        install_mode=install_mode, plan_version=plan_version, set_at=set_at)


def assert_local_first(policy: Policy) -> None:
    """Raise unless this is a posture a user may arrive at without choosing it.

    Applied to a fresh-install or migrated-from-nothing resolution. NOT applied to a
    policy the user set: §8.4 offers all four modes as choices and only constrains
    the default.
    """
    if policy.operation_mode not in LOCAL_FIRST_MODES:
        raise DefaultPostureViolation(
            f"a starting posture of {policy.operation_mode!r} permits a cloud model "
            f"without the user having asked for one (§8.4)")
    missing = sorted(set(DISPLAY_FACETS) - set(policy.redaction_settings))
    if missing:
        raise DefaultPostureViolation(
            f"facets {missing} are unresolved; §8.4's data-minimizing `must` has no "
            f"'unset' value, and an unresolved facet is decided by whoever reads it")
    shown = sorted(facet for facet, value in policy.redaction_settings.items()
                   if value != MORE_REDACTING[facet])
    if shown:
        raise DefaultPostureViolation(
            f"facets {shown} start shown; §8.4's example makes the aggregate the "
            f"default and the expansion the user's act")
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_defaults.py -v`
Expected: PASS — 26 passed (24 test functions; the two `CLOUD_MODES` parametrizations contribute
two cases each).

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–6 green, and P1–P5 still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/defaults.py tests/p7/test_p7_defaults.py
git commit -m "feat(P7): W1's local-first floor and the more-redacting default, with the mode left unchosen"
```

---

---

### Task 7: The six releasable item kinds, the always-local nine, and `whole_document_requested`

> **DUPLICATE-AUTHORING NOTICE — read before assembling.** A `### Task 7` was being written into
> [`PLAN-tasks-04-07.md`](PLAN-tasks-04-07.md) at line 2414 while this file was being written
> (file mtime 2026-08-22 02:56, thirty seconds before this section started). Two sections now
> claim Task 7. They agree on A11/A12/A13 — the additions table that file publishes at its own
> lines 113–116 — and they **disagree on three field lists**, which is the whole of the difference:
>
> | | `PLAN-tasks-04-07.md`'s Task 7 | This section |
> |---|---|---|
> | `MetadataField` | `(name, value)` | `(name,)` — **no value** |
> | `Filename` | `(file_id, value)` | `(file_id,)` — **no value** |
> | `Excerpt.span` / `RedactedIdentifier.span` | `TextSpan` | `TextSpan \| None` |
>
> **This section's shapes are the ones SPEC §6 and the already-written Task 9 require, and the
> other section's cannot be built.** SPEC §6 line 227 spells the request field as
> *"`requested_items[]`    item kinds from §4 above — references only, never materialised content"*.
> A `MetadataField` carrying a `value` and a `Filename` carrying a `value` **are** materialised
> content in the request, so the two-field forms make that line false. And Task 9
> ([`PLAN-tasks-08-11.md`](PLAN-tasks-08-11.md), *"Task 9 pins one field of Task 7's items"*)
> states the span pin outright: *"`Excerpt.span` and `RedactedIdentifier.span` are
> `evidence_shape.location.TextSpan | None` — `None` for the container-path form, where the address
> is the whole citation."* A non-optional `span` makes §2.3's cell and §2.8's EXIF field
> unaddressable, and Task 9's `test_a_container_path_address_has_no_unit_length` fails on
> construction. **Take this section's field lists.** Everything else in the other section — the
> B5d/C9a flagging, `allow_unratified`, `sensitive_observation_keys`, the `current_path` gap —
> is the same decision reached independently and is preserved here.

**Files:**
- Create: `src/privacy/items.py`
- Test: `tests/p7/test_p7_items.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.ALWAYS_LOCAL`, `.ITEM_KINDS`, `.check_item_kind(value) -> str`,
  `.OPEN_QUESTIONS`, `.OutOfVocabulary`, `evidence_shape.location.TextSpan(start, end)`,
  `evidence_shape.store.runs_for_file(conn, file_id) -> list[ExtractionRun]`,
  `extractors.long_tail.POTENTIALLY_SENSITIVE`,
  `.sensitivity_signals_for(conn, run_id) -> list[sqlite3.Row]`.
- Produces (`items.py`):
  - `Excerpt(observation_key: str, span: TextSpan | None, reason: str)`
  - `RedactedIdentifier(observation_key: str, span: TextSpan | None, identifier_class: str)`
  - `CandidateLabel(label: str)`
  - `MetadataField(name: str)`
  - `EvidenceReference(observation_key: str)`
  - `Filename(file_id: str)`
  - `RequestedItem` — the union of the six.
  - `ITEM_FIELDS: Mapping[str, tuple[str, ...]]` — kind → field names, read from
    `dataclasses.fields`, never retyped.
  - `RATIFIED_ITEM_KINDS: tuple[str, ...]` (§8.4's five), `UNRATIFIED_ITEM_KINDS: tuple[str, ...]`
    (`("filename",)`), `FILENAME_OPEN_QUESTION: str`.
  - `kind_of(item) -> str` (A13)
  - `is_whole_document(item, *, unit_length) -> bool`
  - `check_item(item, *, unit_length, protected, sensitive_keys, allow_unratified) -> None` (A11)
  - `sensitive_observation_keys(conn, file_id) -> frozenset[str]` (A13)
  - `AlwaysLocalRequested`, `WholeDocumentRequested`, `UnratifiedItemKind`, `ProtectedItemRequested`.

**Done-means:** 6 (the `always_local_item` and `whole_document_requested` reasons).

---

**The sixth kind is built, is named as unratified, and cannot ship by accident — NEEDS-JOSEPH B5d
and C9a.** §8.4's sentence names **five**: *"the engine should send only a compact dossier relevant
to the current question: selected excerpts, redacted identifiers, candidate labels, non-sensitive
metadata, and evidence references"*, and **the same sentence** puts *"Paths"* in the always-local
set. §7.7's residual dossier *"includes the filename"*. §7.3 forbids filenames in prompts **only**
for `Protected Records`: *"it should normally remain local-only and must not cause filenames or
content to be exposed in model prompts."* P7's SPEC §4 reads directory path ≠ filename — §7.3's
carve-out is vacuous under any other reading — permits `filename` for non-protected files, denies it
for protected ones, and lists the whole thing as its own **Open question 2**.

**This plan does not settle it, and three separate mechanisms make that visible rather than
implicit:**

1. `UNRATIFIED_ITEM_KINDS = ("filename",)` sits beside `RATIFIED_ITEM_KINDS` (§8.4's five) in the
   module, so the split is a value a reviewer can print, not a comment.
2. `allow_unratified` is a **required keyword with no default** on `check_item`. A caller who has
   not typed the word cannot admit a `Filename`; a build that forgets it raises `TypeError`, not a
   release.
3. `FILENAME_OPEN_QUESTION` names the three sections that disagree and is asserted equal to
   `vocabulary.OPEN_QUESTIONS[2]`, so the module and the SPEC's open-questions list cannot drift
   apart, and `test_filename_is_the_unratified_sixth_kind_needs_joseph_b5d_c9a` is the named test
   the reviewer greps for.

Task 21 can then assert that **no module under `src/privacy/` passes `allow_unratified=True`** —
the opt-in exists for a caller outside this part, and P7 itself never takes it.

**The always-local nine are refused at CONSTRUCTION, not at release, and that is the skeleton's own
word.** The skeleton: each of the nine is *"**not expressible** as any of the six item kinds,
asserted by attempting to construct one and catching `AlwaysLocalRequested`"*. Task 13 says the same
from its side — *"Task 7 refuses those at construction with `AlwaysLocalRequested`"* — and Task 20
has already been written against it: *"Task 7 makes the nine named kinds unconstructible, so a
request holding 'OCR output' cannot be built and cannot be a fixture."* Three sections agree, so the
check lives in `__post_init__` and `check_item` does not repeat it. SPEC §3 is the sentence being
made mechanical: *"Nothing in this set can be named as a releasable item kind. The gate has no code
path that materialises one."*

**Eight of the nine have no field to live in; the ninth is a name, and only one field names a kind
of data.** `Excerpt`, `RedactedIdentifier` and `EvidenceReference` carry an `observation_key` and at
most a span — an address, never content. `CandidateLabel` carries a label, which §4.5 and §5.4 make
a **destination** name rather than a kind of data. `Filename` carries a `file_id` — an id, not a
name — because SPEC §6 says requests carry *"references only, never materialised content"*, and the
gate is what turns the reference into a string. That leaves `MetadataField.name` as the single
channel through which one of §8.4's nine could be *named*, and it is checked against
`vocabulary.ALWAYS_LOCAL` — **the nine names exactly, after one normalisation, with no synonym
list.**

**The normalisation is Task 2's, not a second one.** Task 2 derived `ALWAYS_LOCAL` from §8.4's
sentence with `word.lower().replace(" ", "_")` and its own test asserts the round trip. `_normalise`
here is that transformation and nothing more, so `"GPS"`, `"image EXIF"` and `"Complete extracted
text"` all land on their key and a caller cannot evade the check by matching the design's surface
spelling instead of P7's. A test asserts `_normalise` is the identity on every member of
`ALWAYS_LOCAL`, which is what makes "same transformation" checkable rather than asserted.

**The gap this leaves is real, is deliberate, and is reported rather than papered over.**
`MetadataField(name="current_path")` is **not** caught by this layer. A synonym list would be a
detection rule, and SPEC's own constraint is that *"`src/privacy/` contains no regex, no gazetteer,
no filename pattern, no keyword list"* — Task 21 asserts it by introspection. What catches
`current_path` is that a `metadata_field` is *"a named non-sensitive field"* whose name the **caller
declares**; Task 13 decides on the declared name, and P7 owns no detector that could second-guess
it. One test asserts the gap by name so a later reader finds a decision instead of an oversight.

**`paths` gets a second, structural home because it is a value shape, not only a name.**
`Filename.file_id` is P1's opaque id. A `file_id` carrying a path separator **is** a path wearing an
id's field name, so `Filename.__post_init__` refuses one with `AlwaysLocalRequested`. That is one
character, not a pattern catalogue, and it closes the only kind whose field could plausibly carry
§8.4's first always-local word.

**"Raw sensitive values" is the one always-local item that cannot be recognised by name, and P5
already publishes the only thing that recognises it.** P5's `long_tail` marks each located value it
emits with `POTENTIALLY_SENSITIVE` (`= "potentially sensitive"`, verified by import), keyed on P4's
`observation_key`: *"the row is keyed on `observation_key`, which is what survives a re-run and what
P7 can redact against."* So the resolution-time half of the rule is:

> an **`Excerpt`** over a key P5 marked is `AlwaysLocalRequested`; a **`RedactedIdentifier`** over
> the **same** key is permitted.

That asymmetry is exactly what §8.4's *"redacted identifiers"* allowance means, and it is why
Task 8's transform is injected with no default — the permitted path cannot silently emit the raw
value. `sensitive_keys` is a **required keyword** on `check_item` and `check_item` opens no database:
the walk is `runs_for_file` → `sensitivity_signals_for`, composed once here as
`sensitive_observation_keys`. P7 adds no reader to P4 or P5.

**"OCR output" is the whole output; an OCR excerpt is not — and this contradicts a sentence already
written in Task 20.** §8.4 permits *"a short heading or OCR excerpt"* in the very sentence that puts
*"OCR output"* in the always-local set, so an `Excerpt` over an observation in the `ocr` zone is
releasable and the complete OCR text is not; what stops the complete text is
`WholeDocumentRequested`. [`PLAN-tasks-20-22.md`](PLAN-tasks-20-22.md) reaches fixture 7's
`Denied(always_local_item)` *"by a CONSTRUCTIBLE `Excerpt` that RESOLVES to always-local content --
P4's fixture 8 is an `ocr.apple_vision` run in zone `ocr`, and §8.4 puts 'OCR output' in the
always-local set."* **`items.py` does not branch on `zone` and will not deny that excerpt.**
Reported, not resolved: the two readings cannot both hold, §8.4's *"OCR excerpt"* clause is the
evidence against the zone reading, and if Task 20's fixture 7 is to stay reachable it should stand
on a **P5-signalled key** (the mechanism above, which fires for a real reason) rather than on the
zone. Naming it here so assembly finds it; no fixture is edited by this task.

**Task 6's local-first default is a DEFAULT; these nine are not, and the two must not be read as one
rule.** Task 6's own words: *"W1 binds the DEFAULT, never the choice"* — `resolve_default_policy`
returns a stored `cloud_assisted` policy unchanged, and `MORE_REDACTING` fills a facet the user has
not set. The always-local nine are the opposite kind of rule: **no mode, no policy, no consent
option and no default makes one of them expressible.** SPEC §3: *"The gate has no code path that
materialises one."* So `items.py` consumes neither `defaults` nor `policy`, takes no mode argument,
and has no branch a mode could change — which is the structural statement that the nine are not a
posture. A test asserts the absence of both imports.

**What this task does NOT own, so the rule keeps one home each.** `check_item`'s `protected` refuses
a **`Filename`** on a protected file and nothing else. §7.3 also forbids *content* for a
`Protected Records` file, and §8.4 forbids protected material in cloud prompts by default — those
are the gate's `protected_records_template` and `protected_cloud_target` denials, which Task 13
builds and `release.DECISION_ORDER` sequences. A second copy here would be a rule with two homes,
and this task refuses to hold one. The stricter of the two readings is taken for the filename
itself: §7.3 has **no locality qualifier** — *"must not cause filenames or content to be exposed in
model prompts"*, full stop — while §8.4's *"not included in cloud-model prompts **by default**"* is
what the consent path reopens. So a protected `Filename` is refused for **any** target and
`NeedsConsent` is where the user reopens it. Reported as a reading.

**`UnratifiedItemKind` deliberately maps to NO denial reason.** `DENIAL_REASONS` has eight and none
of them says "the caller named an unratified kind", which is correct: that is a **build defect**,
not a policy outcome, and it must propagate to the developer rather than reach a user as a `Denied`
they could try to consent around. Task 13's eight builders are complete without a ninth.

---

### Two cross-task demands this task raises

Both are on **Task 11**, both are one-line changes to code already written in
[`PLAN-tasks-08-11.md`](PLAN-tasks-08-11.md), and the second is a **live defect** rather than a
tidying.

| Demanded of | What, and why |
|---|---|
| **P7 Task 11** | `Gate._materialise` calls `check_item(item, unit_length=found.unit_length)`. A11 — published in [`PLAN-tasks-04-07.md`](PLAN-tasks-04-07.md) line 114 — gives `check_item` three further **required** keywords. The call must become `check_item(item, unit_length=found.unit_length, protected=<the record's flag>, sensitive_keys=sensitive_observation_keys(self._conn, file_id), allow_unratified=False)`. As written it is a `TypeError` on the first release. |
| **P7 Task 11** | `Gate._materialise` runs `if not isinstance(item, TEXT_BEARING): continue` **before** `check_item`, so `CandidateLabel`, `MetadataField`, `EvidenceReference` and `Filename` are never checked at all. `release.DECISION_ORDER` lists `always_local_item` as a step and `PLAN-tasks-15-22.md`'s fixture 7 is *"GPS requested as an item"* — under the current loop a `MetadataField` reaching the gate is released unchecked. The fix is to split the loop: **check every requested item, materialise only the text-addressed ones.** |

One further note, not a demand: `release.TEXT_BEARING: tuple[type, ...] = (Excerpt, RedactedIdentifier)`
in Task 11 is a second home for a fact `ITEM_FIELDS` already carries — an item is text-addressed iff
`"span" in ITEM_FIELDS[kind_of(item)]`. `items.py` therefore publishes **no** type tuple of its own
and keys every branch off `kind_of`, so there is exactly one place to change if a seventh kind is
ever ratified. Task 11 may keep `TEXT_BEARING` or derive it; this task will not add a competing one.

---

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_items.py
"""§8.4's compact dossier: what a request may name, and what it may not.

Three of the assertions here are held open on purpose, and each says so in its own
docstring rather than in a comment a reader has to find.

`filename` is a SIXTH kind and §8.4's sentence names FIVE. §7.7 puts the filename in
the residual dossier and §7.3 forbids filenames in prompts only for Protected
Records. P7's SPEC adopts the reading that makes §7.3 non-vacuous and lists it as its
own Open question 2. NEEDS-JOSEPH B5d and C9a. The tests below prove the kind is
unadmittable without an explicit opt-in; they never prove the reading is right.

The always-local check over `MetadataField.name` is a VOCABULARY check against §8.4's
nine names, not a detector. `MetadataField(name="current_path")` is NOT caught and a
test says so by name, because a synonym list would be the gazetteer P7 is forbidden
to own.

`_normalise` is Task 2's transformation -- `word.lower().replace(" ", "_")` -- and a
test asserts it is the identity on every member of `ALWAYS_LOCAL`. If Task 2's
derivation ever changes, that test fails here rather than opening a hole.
"""
from __future__ import annotations

import dataclasses
import inspect

import pytest

from evidence_shape.location import TextSpan
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_run
from extractors.long_tail import (
    POTENTIALLY_SENSITIVE,
    SensitivitySignal,
    record_sensitivity_signals,
)

import privacy.items as items
from privacy.items import (
    FILENAME_OPEN_QUESTION,
    ITEM_FIELDS,
    RATIFIED_ITEM_KINDS,
    UNRATIFIED_ITEM_KINDS,
    AlwaysLocalRequested,
    CandidateLabel,
    EvidenceReference,
    Excerpt,
    Filename,
    MetadataField,
    ProtectedItemRequested,
    RedactedIdentifier,
    RequestedItem,
    UnratifiedItemKind,
    WholeDocumentRequested,
    check_item,
    is_whole_document,
    kind_of,
    sensitive_observation_keys,
)
from privacy.vocabulary import ALWAYS_LOCAL, ITEM_KINDS, OPEN_QUESTIONS, OutOfVocabulary

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
CONTENT_HASH = "a" * 64
KEY = "sha256:" + "b" * 64
OTHER_KEY = "sha256:" + "c" * 64
BODY_LENGTH = 39

#: The six kinds, constructed once, so every structural assertion runs over all six
#: rather than over whichever one the test author remembered.
ONE_OF_EACH: tuple[RequestedItem, ...] = (
    Excerpt(observation_key=KEY, span=TextSpan(16, 27), reason="the group's subject"),
    RedactedIdentifier(observation_key=KEY, span=TextSpan(16, 27),
                       identifier_class="passport_number"),
    CandidateLabel(label="Passport"),
    MetadataField(name="page_count"),
    EvidenceReference(observation_key=KEY),
    Filename(file_id="file-1"),
)

#: A permissive default for the three keywords a given test is not about. Every one
#: of them is REQUIRED on `check_item` (A11); this helper spells them so a test that
#: IS about one of them can override exactly that one and nothing else.
def admit(item, *, unit_length=None, protected=False, sensitive_keys=frozenset(),
          allow_unratified=True) -> None:
    check_item(item, unit_length=unit_length, protected=protected,
               sensitive_keys=sensitive_keys, allow_unratified=allow_unratified)


# --- the six kinds, and the five that §8.4 actually names ----------------------

def test_the_six_kinds_are_task_twos_six_and_split_five_plus_one():
    assert RATIFIED_ITEM_KINDS + UNRATIFIED_ITEM_KINDS == ITEM_KINDS
    assert len(RATIFIED_ITEM_KINDS) == 5
    assert UNRATIFIED_ITEM_KINDS == ("filename",)


def test_every_kind_has_a_dataclass_and_every_dataclass_has_a_kind():
    assert set(ITEM_FIELDS) == set(ITEM_KINDS)
    assert {kind_of(item) for item in ONE_OF_EACH} == set(ITEM_KINDS)


def test_kind_of_refuses_a_type_that_is_not_one_of_the_six():
    # A foreign object is not "an unknown kind" to be tolerated: §8.4's list is
    # closed and Task 2's `OutOfVocabulary` is the load error that says so.
    with pytest.raises(OutOfVocabulary):
        kind_of("excerpt")
    with pytest.raises(OutOfVocabulary):
        kind_of(TextSpan(0, 1))


def test_item_fields_are_read_from_the_dataclasses_and_never_retyped():
    for item in ONE_OF_EACH:
        expected = tuple(f.name for f in dataclasses.fields(item))
        assert ITEM_FIELDS[kind_of(item)] == expected


def test_the_four_reference_only_shapes_are_the_ones_spec_six_requires():
    # SPEC §6: "requested_items[] item kinds from §4 above -- references only, never
    # materialised content." A `value` on any of these four would make that false.
    assert ITEM_FIELDS["candidate_label"] == ("label",)
    assert ITEM_FIELDS["metadata_field"] == ("name",)
    assert ITEM_FIELDS["evidence_reference"] == ("observation_key",)
    assert ITEM_FIELDS["filename"] == ("file_id",)


def test_no_item_kind_has_a_field_that_could_carry_document_content():
    # The structural half of "not expressible": eight of §8.4's nine always-local
    # items have nowhere to live, because no kind has a content-bearing field.
    forbidden = {"value", "text", "content", "raw_value", "path", "current_path",
                 "excerpt", "ocr_text", "bytes", "content_hash", "filename"}
    for item in ONE_OF_EACH:
        assert not set(ITEM_FIELDS[kind_of(item)]) & forbidden, kind_of(item)


def test_evidence_reference_is_an_id_only_with_no_content_field():
    # SPEC §4: "evidence_reference   an id only -- no content". Checked with
    # `dataclasses.fields`, not by reading the class body.
    names = [f.name for f in dataclasses.fields(EvidenceReference)]
    assert names == ["observation_key"]


def test_every_item_is_frozen():
    # A request the gate has already decided on must not change under it.
    for item in ONE_OF_EACH:
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(item, ITEM_FIELDS[kind_of(item)][0], "anything else")


def test_the_two_addressed_kinds_accept_a_span_of_none():
    # Task 9's pin: `None` is the container-path form -- §2.3's cell and §2.8's EXIF
    # field, where `unit_for_observation` returns None and the address is the whole
    # citation. A non-optional span makes those unaddressable.
    assert Excerpt(observation_key=KEY, span=None, reason="the cell").span is None
    assert RedactedIdentifier(observation_key=KEY, span=None,
                              identifier_class="account_number").span is None


# --- the always-local nine: one test per name ---------------------------------
# §8.4: "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS,
# user edits, group memberships, and raw sensitive values should remain local."
# SPEC §3: "Nothing in this set can be named as a releasable item kind. The gate has
# no code path that materialises one."

@pytest.mark.parametrize("surface, key", [
    ("Paths", "paths"),
    ("complete extracted text", "complete_extracted_text"),
    ("OCR output", "ocr_output"),
    ("file hashes", "file_hashes"),
    ("image EXIF", "image_exif"),
    ("GPS", "gps"),
    ("user edits", "user_edits"),
    ("group memberships", "group_memberships"),
    ("raw sensitive values", "raw_sensitive_values"),
])
def test_an_always_local_name_is_not_expressible_as_an_item(surface, key):
    """Nine names, nine cases, refused at CONSTRUCTION.

    The skeleton's word is "not expressible", and Task 20 has already been written
    against it: "Task 7 makes the nine named kinds unconstructible, so a request
    holding 'OCR output' cannot be built and cannot be a fixture." So the refusal is
    in `__post_init__` and `check_item` does not repeat it.

    `MetadataField.name` is the only field that names a KIND OF DATA. The other five
    kinds carry an address, an id, or a destination label, and a test above proves
    none of them has a content-bearing field to smuggle one through.
    """
    assert key in ALWAYS_LOCAL
    with pytest.raises(AlwaysLocalRequested) as caught:
        MetadataField(name=surface)
    assert key in str(caught.value)


def test_normalise_is_task_twos_transformation_and_not_a_second_one():
    # Task 2 derived ALWAYS_LOCAL from §8.4's sentence with
    # `word.lower().replace(" ", "_")`. If that derivation ever changes, this fails
    # here rather than silently opening a hole in the check above.
    for key in ALWAYS_LOCAL:
        assert items._normalise(key) == key


def test_the_always_local_check_is_exact_and_not_a_prefix_match():
    # "GPS Logs" normalises to "gps_logs", which is not "gps". A check that matched
    # loosely would be a keyword list, and §8.4 does not authorise one.
    assert MetadataField(name="GPS Logs").name == "GPS Logs"
    assert MetadataField(name="page_count").name == "page_count"


def test_a_candidate_label_naming_a_data_kind_is_not_refused():
    """§4.5 and §5.4 make a candidate label a DESTINATION name, not a data kind.

    The always-local set is a set of kinds of DATA. Applying the check to a label
    would refuse a legitimate folder called "GPS" while releasing nothing extra:
    the label carries no observation and no value.
    """
    assert CandidateLabel(label="GPS").label == "GPS"


def test_a_metadata_field_named_current_path_is_not_caught_and_that_is_deliberate():
    """The reported gap. `current_path` is not one of §8.4's nine names.

    Catching it would need a synonym list, and SPEC's constraint is that
    `src/privacy/` "contains no regex, no gazetteer, no filename pattern, no keyword
    list" -- Task 21 asserts that by introspection. A `metadata_field` is "a named
    non-sensitive field" whose name the CALLER declares; Task 13 decides on the
    declared name and P7 owns no detector that could second-guess it.

    This test exists so a later reader finds a decision instead of an oversight.
    """
    assert MetadataField(name="current_path").name == "current_path"
    assert "current_path" not in ALWAYS_LOCAL


def test_a_file_id_that_is_a_path_is_refused_as_the_first_always_local_name():
    # §8.4's first always-local word is "Paths". A `file_id` carrying a separator is
    # a path wearing an id's field name. One character, not a pattern catalogue.
    with pytest.raises(AlwaysLocalRequested) as caught:
        Filename(file_id="/Users/j/Documents/passport.pdf")
    assert "paths" in str(caught.value)
    assert Filename(file_id="file-1").file_id == "file-1"


def test_items_imports_no_mode_and_no_policy_so_the_nine_are_not_a_default():
    """Task 6's local-first posture is a DEFAULT; these nine are not.

    Task 6: "W1 binds the DEFAULT, never the choice" -- a stored `cloud_assisted`
    policy comes back unchanged. The always-local set is the opposite kind of rule:
    no mode, no policy, no consent option and no default makes one expressible. The
    structural statement of that is that this module has no branch a mode could
    change, so it binds neither `defaults` nor `policy`.
    """
    bound = {value.__name__ for value in vars(items).values()
             if inspect.ismodule(value)}
    bound |= {getattr(value, "__module__", "") for value in vars(items).values()}
    assert "privacy.defaults" not in bound
    assert "privacy.policy" not in bound
    assert not any(f.name == "operation_mode"
                   for item in ONE_OF_EACH
                   for f in dataclasses.fields(item))


# --- whole_document_requested -------------------------------------------------

def test_an_excerpt_covering_the_whole_unit_is_a_whole_document():
    # §8.4: "It should not send full documents where a short heading or OCR excerpt
    # is enough to resolve the question."
    whole = Excerpt(observation_key=KEY, span=TextSpan(0, BODY_LENGTH),
                    reason="all of it")
    assert is_whole_document(whole, unit_length=BODY_LENGTH) is True
    with pytest.raises(WholeDocumentRequested) as caught:
        admit(whole, unit_length=BODY_LENGTH)
    assert "0" in str(caught.value) and str(BODY_LENGTH) in str(caught.value)


def test_a_span_that_over_covers_the_unit_is_still_a_whole_document():
    # A span wider than the unit is not "outside the rule"; it is the same request
    # with worse arithmetic. `<= 0` and `>= unit_length`, not `== `.
    wide = Excerpt(observation_key=KEY, span=TextSpan(0, BODY_LENGTH + 400),
                   reason="all of it and then some")
    assert is_whole_document(wide, unit_length=BODY_LENGTH) is True


def test_a_bounded_excerpt_is_not_a_whole_document():
    short = Excerpt(observation_key=KEY, span=TextSpan(16, 27), reason="the number")
    assert is_whole_document(short, unit_length=BODY_LENGTH) is False
    admit(short, unit_length=BODY_LENGTH)


def test_a_redacted_identifier_over_the_whole_unit_is_also_refused():
    # The rule is about the SPAN, not about the kind. A redaction that covered the
    # whole unit would send the whole unit with one value starred out.
    whole = RedactedIdentifier(observation_key=KEY, span=TextSpan(0, BODY_LENGTH),
                               identifier_class="passport_number")
    with pytest.raises(WholeDocumentRequested):
        admit(whole, unit_length=BODY_LENGTH)


def test_a_container_path_address_is_never_a_whole_document():
    # Task 9: `unit_for_observation` returns None for §2.3's cell and §2.8's EXIF
    # field. There is no unit, so there is nothing for a span to cover, and a
    # `None` unit_length must not be read as "length zero" -- which would make every
    # cell a whole document.
    cell = Excerpt(observation_key=KEY, span=None, reason="the cell")
    assert is_whole_document(cell, unit_length=None) is False
    admit(cell, unit_length=None)


def test_a_kind_with_no_span_is_never_a_whole_document():
    for item in (CandidateLabel(label="Passport"), MetadataField(name="page_count"),
                 EvidenceReference(observation_key=KEY), Filename(file_id="file-1")):
        assert is_whole_document(item, unit_length=BODY_LENGTH) is False


# --- raw sensitive values: P5's signal, and the excerpt/identifier asymmetry ----

def test_an_excerpt_over_a_p5_signalled_key_is_always_local():
    """§8.4's ninth always-local name, and the only one that needs P5.

    P5 marks each located value it emits with POTENTIALLY_SENSITIVE, keyed on P4's
    `observation_key`. P7 owns no detector, so this signal is the only thing in the
    product that can recognise a "raw sensitive value" at all.
    """
    with pytest.raises(AlwaysLocalRequested) as caught:
        admit(Excerpt(observation_key=KEY, span=TextSpan(16, 27), reason="it"),
              unit_length=BODY_LENGTH, sensitive_keys=frozenset({KEY}))
    assert "raw_sensitive_values" in str(caught.value)


def test_a_redacted_identifier_over_the_same_key_is_permitted():
    # This asymmetry IS §8.4's "redacted identifiers" allowance. Task 8's transform
    # is injected with no default, so the permitted path cannot emit a raw value.
    admit(RedactedIdentifier(observation_key=KEY, span=TextSpan(16, 27),
                             identifier_class="passport_number"),
          unit_length=BODY_LENGTH, sensitive_keys=frozenset({KEY}))


def test_an_excerpt_over_an_unsignalled_key_is_permitted():
    admit(Excerpt(observation_key=OTHER_KEY, span=TextSpan(16, 27), reason="it"),
          unit_length=BODY_LENGTH, sensitive_keys=frozenset({KEY}))


def test_check_item_requires_every_one_of_its_four_keywords():
    # A11: none of the four has a default. A build that forgets one is a TypeError,
    # never a release. `sensitive_keys` in particular: a default of `frozenset()`
    # would mean "nothing is sensitive" for a caller who never wired P5.
    item = Excerpt(observation_key=KEY, span=TextSpan(16, 27), reason="it")
    for omit in ("unit_length", "protected", "sensitive_keys", "allow_unratified"):
        kwargs = dict(unit_length=BODY_LENGTH, protected=False,
                      sensitive_keys=frozenset(), allow_unratified=False)
        del kwargs[omit]
        with pytest.raises(TypeError):
            check_item(item, **kwargs)


def test_sensitive_observation_keys_walks_p4_runs_to_p5_signals(p7_conn):
    record_run(p7_conn, ExtractionRun(
        run_id="run-1", file_id="file-1", content_hash=CONTENT_HASH,
        extractor_name="long_tail", extractor_version="1.0.0",
        source_type="contacts", analysis_tier="native", config={},
        completeness="complete", started_at=FIXED_CLOCK, observation_count=2))
    record_sensitivity_signals(
        p7_conn, run_id="run-1",
        signals=(SensitivitySignal(observation_index=0,
                                   signal=POTENTIALLY_SENSITIVE,
                                   basis="every VCF value"),),
        observation_keys=(KEY, OTHER_KEY), now=FIXED_CLOCK)
    assert sensitive_observation_keys(p7_conn, "file-1") == frozenset({KEY})


def test_sensitive_observation_keys_is_empty_for_a_file_with_no_runs(p7_conn):
    # The honest v1 posture: nothing signalled is not "nothing sensitive". It is the
    # caller's job to know that, and the empty set says so without inventing a rule.
    assert sensitive_observation_keys(p7_conn, "file-404") == frozenset()


def test_only_the_potentially_sensitive_signal_counts(p7_conn):
    record_run(p7_conn, ExtractionRun(
        run_id="run-2", file_id="file-2", content_hash=CONTENT_HASH,
        extractor_name="long_tail", extractor_version="1.0.0",
        source_type="contacts", analysis_tier="native", config={},
        completeness="complete", started_at=FIXED_CLOCK, observation_count=1))
    record_sensitivity_signals(
        p7_conn, run_id="run-2",
        signals=(SensitivitySignal(observation_index=0, signal="something else",
                                   basis="not P5's word"),),
        observation_keys=(KEY,), now=FIXED_CLOCK)
    assert sensitive_observation_keys(p7_conn, "file-2") == frozenset()


# --- filename: the unratified sixth kind -- NEEDS-JOSEPH B5d and C9a -----------

def test_filename_is_the_unratified_sixth_kind_needs_joseph_b5d_c9a():
    """SPEC Open question 2 -- the one place the contract resolved a conflict.

    §8.4 names FIVE releasable kinds and puts *paths* in the always-local set. §7.7
    puts *the filename* in the residual dossier. §7.3 forbids filenames in prompts
    ONLY for Protected Records, which is vacuous under any reading that forbade them
    everywhere. P7's SPEC reads directory path != filename, permits `filename` for
    non-protected files, denies it for protected ones, and lists the reading as its
    own Open question 2 for the reviewer.

    NEEDS-JOSEPH B5d and C9a. This test proves the kind is UNADMITTABLE without an
    explicit opt-in. It does not prove the reading is right, and nothing in P7 does.
    """
    assert UNRATIFIED_ITEM_KINDS == ("filename",)
    assert "filename" not in RATIFIED_ITEM_KINDS
    assert FILENAME_OPEN_QUESTION == OPEN_QUESTIONS[2]
    for section in ("8.4", "7.7", "7.3"):
        assert section in FILENAME_OPEN_QUESTION


def test_a_filename_cannot_be_admitted_without_the_explicit_opt_in():
    with pytest.raises(UnratifiedItemKind) as caught:
        check_item(Filename(file_id="file-1"), unit_length=None, protected=False,
                   sensitive_keys=frozenset(), allow_unratified=False)
    assert "filename" in str(caught.value)
    assert "B5d" in str(caught.value) and "C9a" in str(caught.value)


def test_the_five_ratified_kinds_need_no_opt_in():
    for item in ONE_OF_EACH:
        if kind_of(item) in UNRATIFIED_ITEM_KINDS:
            continue
        check_item(item, unit_length=None, protected=False,
                   sensitive_keys=frozenset(), allow_unratified=False)


def test_a_filename_is_permitted_for_a_non_protected_file():
    admit(Filename(file_id="file-1"), protected=False)


def test_a_filename_is_denied_for_a_protected_file():
    """§7.3: Protected Records "must not cause filenames or content to be exposed in
    model prompts" -- no locality qualifier, so this refuses for ANY target, which is
    the stricter of the two available readings. §8.4's "not included in cloud-model
    prompts BY DEFAULT" is what the consent path reopens, and that path is
    `NeedsConsent`, not a weaker check here.
    """
    with pytest.raises(ProtectedItemRequested) as caught:
        admit(Filename(file_id="file-1"), protected=True)
    assert "7.3" in str(caught.value)


def test_protected_does_not_refuse_the_other_five_kinds_here():
    # One rule, one home. §7.3's content half and §8.4's cloud-prompt half are the
    # gate's `protected_records_template` and `protected_cloud_target` denials, which
    # Task 13 builds and `release.DECISION_ORDER` sequences. A second copy here would
    # be a rule with two homes.
    for item in ONE_OF_EACH:
        if kind_of(item) in UNRATIFIED_ITEM_KINDS:
            continue
        admit(item, unit_length=None, protected=True)


def test_unratified_maps_to_no_denial_reason():
    # A caller naming an unratified kind has a BUILD defect, not a policy problem.
    # It must propagate to the developer rather than reach a user as a `Denied` they
    # could try to consent around. Task 13's eight builders are complete without a
    # ninth.
    from privacy.vocabulary import DENIAL_REASONS
    assert not any("unratified" in reason for reason in DENIAL_REASONS)
    assert len(DENIAL_REASONS) == 8
```

- [ ] **Step 2: Run the test and watch it fail**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p7/test_p7_items.py -q
```

Expected: **FAIL** — `ModuleNotFoundError: No module named 'privacy.items'`, at collection, on the
`import privacy.items as items` line. Nothing in `src/privacy/` defines the six kinds yet.

- [ ] **Step 3: Write `src/privacy/items.py` — the six kinds and the two refusals in `__post_init__`**

```python
# src/privacy/items.py
"""§8.4's compact dossier: the six kinds a request may name, and the nine it may not.

§8.4: "When a cloud model is used, the engine should send only a compact dossier
relevant to the current question: selected excerpts, redacted identifiers, candidate
labels, non-sensitive metadata, and evidence references." That is FIVE. `filename` is
a sixth, adopted by P7's SPEC and held unratified here -- see `FILENAME_OPEN_QUESTION`
and `UNRATIFIED_ITEM_KINDS`, NEEDS-JOSEPH B5d and C9a.

Every item carries a REFERENCE. SPEC §6: "requested_items[] item kinds from §4 above
-- references only, never materialised content." A field named `value` on any of these
would make that sentence false, so there is none: an excerpt is an
`(observation_key, span)` address, an evidence reference is "an id only -- no
content", a metadata field is a NAME, and a filename is a `file_id`. `resolve.py` is
the one module that turns a reference into a string.

Two refusals fire at CONSTRUCTION, because the skeleton's word is "not expressible"
and Task 20 is already written against it: a request naming one of §8.4's nine
always-local items cannot be built, so it cannot be a fixture either.

  AlwaysLocalRequested  -- a `MetadataField` naming one of the nine, or a `Filename`
                           whose `file_id` is a path.
  WholeDocumentRequested -- raised by `check_item`, not here: it needs the stored unit
                           length, which only `resolve.materialise` can supply.

This module holds no threshold, no regex, no gazetteer and no keyword list. The nine
names come from `vocabulary.ALWAYS_LOCAL`, which Task 2 derives from §8.4's own
sentence; `_normalise` is Task 2's transformation and nothing more. The consequence is
that `MetadataField(name="current_path")` is NOT caught, and that gap is deliberate
and tested: a synonym list would be a detection rule P7 is forbidden to own.

It also imports neither `defaults` nor `policy`. Task 6's local-first posture is a
DEFAULT that a user may change; the always-local nine are not a posture at all, and a
module with no mode to branch on is the structural way to say so.
"""
from __future__ import annotations

import dataclasses
import sqlite3
from collections.abc import Container, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.location import TextSpan
from evidence_shape.store import runs_for_file
from extractors.long_tail import POTENTIALLY_SENSITIVE, sensitivity_signals_for

from privacy.vocabulary import (
    ALWAYS_LOCAL, ITEM_KINDS, OPEN_QUESTIONS, OutOfVocabulary, check_item_kind,
)


class AlwaysLocalRequested(ValueError):
    """§8.4's nine, named in a request. SPEC §3: "Nothing in this set can be named as
    a releasable item kind. The gate has no code path that materialises one."

    Task 13's `deny_always_local_item` translates a caught instance into the gate's
    `Denied(always_local_item)`; it does not re-decide which names are always-local.
    """


class WholeDocumentRequested(ValueError):
    """§8.4: the engine "should not send full documents where a short heading or OCR
    excerpt is enough to resolve the question." Raised by `check_item`, which is the
    first point at which the stored unit length is known.
    """


class UnratifiedItemKind(ValueError):
    """A kind §8.4's own sentence does not name, admitted without the opt-in.

    Deliberately NOT one of `vocabulary.DENIAL_REASONS`: this is a build defect, not
    a policy outcome, and it must reach the developer rather than a user who might
    try to consent around it.
    """


class ProtectedItemRequested(ValueError):
    """§7.3: `Protected Records` "must not cause filenames or content to be exposed
    in model prompts." Scoped here to the filename; the content half is Task 13's
    `protected_records_template`, so the rule keeps one home each.
    """


def _normalise(name: str) -> str:
    """Task 2's transformation, and not a second one.

    Task 2 derives `ALWAYS_LOCAL` from §8.4's sentence with
    `word.lower().replace(" ", "_")`. Using anything wider here would be a keyword
    rule; using anything narrower would let "GPS" through while refusing "gps".
    """
    return name.strip().lower().replace(" ", "_")


def _refuse_always_local_name(field: str, value: str) -> None:
    key = _normalise(value)
    if key in ALWAYS_LOCAL:
        raise AlwaysLocalRequested(
            f"{field}={value!r} names {key!r}, which §8.4 places in the always-local "
            f"set: 'Paths, complete extracted text, OCR output, file hashes, image "
            f"EXIF, GPS, user edits, group memberships, and raw sensitive values "
            f"should remain local.' Nothing in that set can be named as a releasable "
            f"item kind, so the request is not constructible rather than merely "
            f"denied. §8.4's releasable five are: selected excerpts, redacted "
            f"identifiers, candidate labels, non-sensitive metadata, and evidence "
            f"references."
        )


@dataclass(frozen=True)
class Excerpt:
    """SPEC §4: `{ observation_key, span, reason }`, "resolved by the gate from local
    storage". The span is the whole of what bounds it -- an excerpt with no bound is
    the full document §8.4 forbids.

    `span` is `TextSpan | None`: `None` is §2.3's cell and §2.8's EXIF field, where
    `unit_for_observation` returns `None` and the address is the whole citation
    (Task 9's pin). It is never "unbounded".
    """

    observation_key: str
    span: TextSpan | None
    reason: str


@dataclass(frozen=True)
class RedactedIdentifier:
    """SPEC §4: `{ observation_key, span, identifier_class }`.

    `identifier_class` is an OPAQUE string. SPEC *Deferred*: "Which identifier classes
    exist and how each is transformed is not enumerated anywhere in the design." Task 8
    carries it through to the manifest; this module enumerates none.
    """

    observation_key: str
    span: TextSpan | None
    identifier_class: str


@dataclass(frozen=True)
class CandidateLabel:
    """SPEC §4: "a label already present in the local database (§4.5, §5.4)".

    A DESTINATION name, not a kind of data -- which is why the always-local check does
    not run over it. A label carries no observation and no value, so a label reading
    "GPS" releases the word and nothing else.
    """

    label: str


@dataclass(frozen=True)
class MetadataField:
    """SPEC §4: "a named non-sensitive field (e.g. file type, page count, capture
    year)". The NAME only -- the gate looks the value up, per SPEC §6's "references
    only, never materialised content".

    This is the single field in the product through which one of §8.4's nine could be
    NAMED, which is why it is the one that is checked.
    """

    name: str

    def __post_init__(self) -> None:
        _refuse_always_local_name("name", self.name)


@dataclass(frozen=True)
class EvidenceReference:
    """SPEC §4: "an id only -- no content"."""

    observation_key: str


@dataclass(frozen=True)
class Filename:
    """The unratified sixth kind. NEEDS-JOSEPH B5d and C9a; SPEC Open question 2.

    Carries a `file_id`, not a name: SPEC §6 says requests carry references only, and
    the gate is what resolves the reference. A `file_id` holding a path separator is
    a path wearing an id's field name, and §8.4's first always-local word is "Paths".
    """

    file_id: str

    def __post_init__(self) -> None:
        if "/" in self.file_id or "\\" in self.file_id:
            raise AlwaysLocalRequested(
                f"file_id={self.file_id!r} carries a path separator, and §8.4 places "
                f"'paths' in the always-local set. `Filename` carries P1's opaque "
                f"file id; the gate resolves the name. A file id that is a path is a "
                f"path wearing an id's field name."
            )


RequestedItem = (Excerpt | RedactedIdentifier | CandidateLabel | MetadataField
                 | EvidenceReference | Filename)

#: Every branch in this module keys off `kind_of`, so `ITEM_KINDS` is the one place a
#: seventh kind would have to be added. Validated through Task 2's checker at import,
#: so these are provably members of the closed vocabulary and not a second spelling.
_KIND_BY_TYPE: Mapping[type, str] = MappingProxyType({
    Excerpt: check_item_kind("excerpt"),
    RedactedIdentifier: check_item_kind("redacted_identifier"),
    CandidateLabel: check_item_kind("candidate_label"),
    MetadataField: check_item_kind("metadata_field"),
    EvidenceReference: check_item_kind("evidence_reference"),
    Filename: check_item_kind("filename"),
})

#: §8.4's own five, in the design's order.
RATIFIED_ITEM_KINDS: tuple[str, ...] = (
    _KIND_BY_TYPE[Excerpt], _KIND_BY_TYPE[RedactedIdentifier],
    _KIND_BY_TYPE[CandidateLabel], _KIND_BY_TYPE[MetadataField],
    _KIND_BY_TYPE[EvidenceReference],
)

#: The sixth. Built, named, and unadmittable without `allow_unratified=True`.
UNRATIFIED_ITEM_KINDS: tuple[str, ...] = (_KIND_BY_TYPE[Filename],)

#: SPEC Open question 2, quoted from `vocabulary.OPEN_QUESTIONS` rather than retyped,
#: so the module and the SPEC's list cannot drift apart. NEEDS-JOSEPH B5d and C9a.
FILENAME_OPEN_QUESTION: str = OPEN_QUESTIONS[2]

#: Kind -> field names, READ from the dataclasses. Retyping them would be a second
#: home for a shape SPEC §4 already fixes, and the field list is what the "no content
#: field" guard reads.
ITEM_FIELDS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    kind: tuple(field.name for field in dataclasses.fields(cls))
    for cls, kind in _KIND_BY_TYPE.items()
})


def kind_of(item: object) -> str:
    """The `ITEM_KINDS` name for one item. A foreign type is a load error (A13)."""
    kind = _KIND_BY_TYPE.get(type(item))
    if kind is None:
        raise OutOfVocabulary(
            f"{type(item).__name__!r} is not one of the {len(ITEM_KINDS)} releasable "
            f"item kinds the design defines {ITEM_KINDS}. §8.4's vocabularies are "
            f"closed: an unrecognised kind is a load error, not a fallback."
        )
    return kind


def is_whole_document(item: object, *, unit_length: int | None) -> bool:
    """§8.4: "It should not send full documents where a short heading or OCR excerpt
    is enough to resolve the question."

    `unit_length is None` is the container-path form -- §2.3's cell, §2.8's EXIF
    field -- where `unit_for_observation` returns `None` and there is no unit for a
    span to cover. Reading it as length zero would make every cell a whole document.
    """
    if "span" not in ITEM_FIELDS[kind_of(item)]:
        return False
    span = item.span
    if span is None or unit_length is None:
        return False
    return span.start <= 0 and span.end >= unit_length


def check_item(item: object, *, unit_length: int | None, protected: bool,
               sensitive_keys: Container[str], allow_unratified: bool) -> None:
    """The release-time half of §8.4's item rules. Returns None or raises (A11).

    Four required keywords, no defaults. `sensitive_keys` in particular: a default of
    the empty set would mean "nothing is sensitive" for a caller who never wired P5,
    which is the same shape of failure as a column with no writer.

    The order matches `release.DECISION_ORDER`: always-local before whole-document,
    so an item that fails both is reported as the stronger refusal.

    Not checked here, on purpose:
      * the always-local NAMES -- refused in `__post_init__`, so a request holding one
        is unconstructible;
      * protected CONTENT and the cloud-prompt default -- Task 13's
        `protected_records_template` and `protected_cloud_target`.
    """
    kind = kind_of(item)

    if kind in UNRATIFIED_ITEM_KINDS and not allow_unratified:
        raise UnratifiedItemKind(
            f"{kind!r} is a releasable item kind §8.4's own sentence does not name. "
            f"§8.4 names five -- selected excerpts, redacted identifiers, candidate "
            f"labels, non-sensitive metadata, and evidence references -- and puts "
            f"paths in the always-local set. P7's SPEC adds this sixth on the reading "
            f"that §7.3's carve-out is otherwise vacuous, and flags it as its own "
            f"Open question 2. NEEDS-JOSEPH B5d and C9a. Pass allow_unratified=True "
            f"to admit it deliberately; there is no default."
        )

    if protected and kind in UNRATIFIED_ITEM_KINDS:
        raise ProtectedItemRequested(
            f"§7.3: a Protected Records file 'should normally remain local-only and "
            f"must not cause filenames or content to be exposed in model prompts.' "
            f"That sentence carries no locality qualifier, so a {kind!r} on a "
            f"protected file is refused for any target. §8.4's 'not included in "
            f"cloud-model prompts by default' is what the consent path reopens, and "
            f"that path is NeedsConsent."
        )

    if kind == _KIND_BY_TYPE[Excerpt] and item.observation_key in sensitive_keys:
        raise AlwaysLocalRequested(
            f"observation {item.observation_key!r} was marked "
            f"{POTENTIALLY_SENSITIVE!r} at emission, and §8.4 places "
            f"'raw_sensitive_values' in the always-local set. §8.4 permits 'redacted "
            f"identifiers', so the same key is releasable as a RedactedIdentifier, "
            f"whose transform is injected with no default."
        )

    if is_whole_document(item, unit_length=unit_length):
        raise WholeDocumentRequested(
            f"span {item.span.start}-{item.span.end} covers the whole of a "
            f"{unit_length}-character text unit. §8.4: the engine 'should not send "
            f"full documents where a short heading or OCR excerpt is enough to "
            f"resolve the question.'"
        )


def sensitive_observation_keys(conn: sqlite3.Connection,
                               file_id: str) -> frozenset[str]:
    """P4's runs for a file -> P5's per-value sensitivity signals (A13).

    P7 owns no detector, and this is the only per-value sensitivity signal in the
    product. P5 assigns no handling class -- §8.4 gives classification to P7 -- so
    this says "P5 saw a value worth redacting", never "this file is sensitive".

    An empty set means NOTHING WAS SIGNALLED, not "nothing is sensitive". The two
    published readers are composed here; no reader is added to P4 or P5.
    """
    keys: set[str] = set()
    for run in runs_for_file(conn, file_id):
        for row in sensitivity_signals_for(conn, run.run_id):
            if row["signal"] == POTENTIALLY_SENSITIVE:
                keys.add(row["observation_key"])
    return frozenset(keys)
```

- [ ] **Step 4: Run the test and watch it pass**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p7/test_p7_items.py -q
```

Expected: **PASS** — 39 passed (the nine parametrised always-local cases count as nine). No test
asserts that `filename` belongs in §8.4's list, and no test asserts that Task 20's `ocr`-zone
reading is right; both are held open by name.

- [ ] **Step 5: Prove the two things the guard tasks will re-assert repo-wide**

```bash
cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 - <<'PY'
import inspect
import privacy.items as items

# 1. No module-level constant in this module is a threshold, a pattern, or a class
#    catalogue. Every public string or tuple constant is drawn from a vocabulary some
#    OTHER module publishes, or is the SPEC's own open-question text. Task 21
#    re-asserts the same property over the whole package.
from extractors.long_tail import POTENTIALLY_SENSITIVE
from privacy.vocabulary import ALWAYS_LOCAL, ITEM_KINDS, OPEN_QUESTIONS

#: The published sets a constant here is allowed to be drawn from, and who owns each.
OWNED_ELSEWHERE = {
    "privacy.vocabulary.ITEM_KINDS": frozenset(ITEM_KINDS),
    "privacy.vocabulary.ALWAYS_LOCAL": frozenset(ALWAYS_LOCAL),
    "extractors.long_tail.POTENTIALLY_SENSITIVE": frozenset({POTENTIALLY_SENSITIVE}),
    "privacy.vocabulary.OPEN_QUESTIONS[2]": frozenset({OPEN_QUESTIONS[2]}),
}
constants = {name: value for name, value in vars(items).items()
             if not name.startswith("_") and not inspect.isclass(value)
             and isinstance(value, (str, tuple))}
for name, value in constants.items():
    members = frozenset((value,) if isinstance(value, str) else value)
    owner = next((who for who, published in OWNED_ELSEWHERE.items()
                  if members <= published), None)
    assert owner is not None, f"{name} is an invented constant: {value!r}"
    print(f"   {name:<24} <- {owner}")
print("1. no invented constant:", len(constants), "checked")

# 2. This module binds no P4 text materialiser. Task 9's `resolve.py` is the ONLY
#    module under src/privacy/ that may, and Task 21 re-asserts it repo-wide against
#    the authoritative `resolve.MATERIALISERS`, which does not exist yet at Task 7.
#
#    BY IDENTITY, not by name. `evidence_shape.text_units` RE-EXPORTS `TextSpan`,
#    `Mapping` and `dataclass`, all three of which this module legitimately binds, so
#    a name-set intersection reports three false positives -- measured, 2026-08-22.
#    `evidence_shape.store` re-exports nothing but DOES own `runs_for_file`, which
#    this module legitimately binds, so its three materialisers are named one by one.
import evidence_shape.store as store
import evidence_shape.text_units as tu

materialisers = [getattr(tu, name) for name in dir(tu)
                 if not name.startswith("_") and callable(getattr(tu, name))
                 and getattr(getattr(tu, name), "__module__", None) == tu.__name__]
materialisers += [store.text_unit_at, store.text_units_for_run,
                  store.unit_for_observation]
bound = [value for value in vars(items).values()]
for materialiser in materialisers:
    assert not any(value is materialiser for value in bound), materialiser
print("2. binds no P4 text materialiser:", len(materialisers),
      "checked by identity; resolve.py stays the one door")
PY
```

Expected output:

```text
   POTENTIALLY_SENSITIVE    <- extractors.long_tail.POTENTIALLY_SENSITIVE
   ALWAYS_LOCAL             <- privacy.vocabulary.ALWAYS_LOCAL
   ITEM_KINDS               <- privacy.vocabulary.ITEM_KINDS
   RATIFIED_ITEM_KINDS      <- privacy.vocabulary.ITEM_KINDS
   UNRATIFIED_ITEM_KINDS    <- privacy.vocabulary.ITEM_KINDS
   FILENAME_OPEN_QUESTION   <- privacy.vocabulary.OPEN_QUESTIONS[2]
1. no invented constant: 6 checked
2. binds no P4 text materialiser: 9 checked by identity; resolve.py stays the one door
```

Six constants, six owners, and **not one of them is owned here** — which is the whole claim. If a
later edit adds a seventh, the script names it as invented rather than letting it pass.

`POTENTIALLY_SENSITIVE` is P5's published constant, re-exported by import rather than retyped, and
`ALWAYS_LOCAL` / `ITEM_KINDS` are Task 2's — the check above is written to fail if any of the three
becomes a local literal. If it fails on `POTENTIALLY_SENSITIVE` on the day P5 changes the word, that
is the check working: the string has one home and it is P5's.

- [ ] **Step 6: Run the whole P7 suite, then commit**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p7 -q
```

Expected: **PASS** — Tasks 1–7 green. Nothing in `src/privacy/items.py` is imported by Tasks 1–6, so
no earlier test changes.

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/privacy/items.py tests/p7/test_p7_items.py && \
git commit -m "feat(P7): the six releasable item kinds, the always-local nine held unconstructible, and filename kept unratified"
```

---

### What this task deliberately did not do

- **It did not settle Open question 2.** `filename` is built, named `UNRATIFIED`, and unadmittable
  without `allow_unratified=True`. NEEDS-JOSEPH **B5d** and **C9a**.
- **It did not build a detector.** `sensitive_keys` carries P5's signal and nothing infers one. On a
  corpus P5 never ran over, `sensitive_observation_keys` returns the empty set, and that means
  *nothing was signalled* — never *nothing is sensitive*.
- **It did not close the `current_path` gap.** A synonym list is the gazetteer P7 may not own; the
  gap is asserted by a named test and decided on the caller's declared name by Task 13.
- **It did not rule on C22.** `Region` carries no origin, so a region address is not resolvable and
  `items.py` binds no `Region`: an `Excerpt.span` is a `TextSpan | None` and Task 8's `span_address`
  is where a region raises `RegionOriginUnspecified`. Assume no origin; nothing here depends on one.

---

### Task 8: Redaction, and a manifest whose identifier class stays opaque

**Files:**
- Create: `src/privacy/redaction.py`
- Test: `tests/p7/test_p7_redaction.py`

**Interfaces:**
- Consumes: `evidence_shape.location.Location`, `.Region`, `.TextSpan`, `.REGION_UNITS`,
  `evidence_shape.locator.serialize_locator(location) -> str`,
  `evidence_shape.canonical.canonical_json(value) -> str`.
- Produces (`redaction.py`):
  - `REGION_ORIGIN_UNDECIDED: str = "NEEDS-JOSEPH C3"` — the key of the open decision, not a
    sentence about it.
  - `IdentifierClassifier` — `Protocol`, `__call__(value: str, *, context_before: str | None,
    context_after: str | None) -> str | None`. **Injected, no default.**
  - `RedactionTransform` — `Protocol`, `__call__(value: str, *, identifier_class: str) -> str`.
    **Injected, no default.**
  - `RedactionEntry` — frozen: `observation_key: str`, `span: str`, `identifier_class: str | None`,
    `redacted: bool`, `context_before: str | None`, `context_after: str | None`,
    `context_truncated: bool`.
  - `RedactionManifest` — frozen: `entries: tuple[RedactionEntry, ...]`; properties `any_redacted`,
    `identifier_classes`; `to_mapping() -> list[dict]`.
  - `RedactionIneffective`, `RegionOriginUnspecified`.
  - `span_address(location: Location) -> str`.
  - `apply_redaction(value: str, *, observation_key: str, span: str, context_before: str | None,
    context_after: str | None, context_truncated: bool, classifier: IdentifierClassifier,
    transform: RedactionTransform) -> tuple[str, RedactionEntry]`.

**Done-means:** 4 (`redaction_applied`), and the redaction half of 12.

**Three deviations from the skeleton's `Interfaces` block, each reported rather than absorbed.**

1. **`apply_redaction` gains `observation_key`, `span` and `context_truncated` as keywords.** The
   skeleton's signature is `apply_redaction(value, *, context_before, context_after, classifier,
   transform)` and its `RedactionEntry` carries `observation_key` and `span` — which that signature
   cannot fill. Three keywords are added, not invented: two are the entry's own published fields and
   the third is M5's third context field, which the skeleton separately requires be *"carried through
   to the manifest, because §8.6 forbids anything being truncated silently."*
2. **`RedactionEntry` gains `context_before`, `context_after` and `context_truncated`.** The
   skeleton requires that redaction *"replaces the **value** and preserves `context_before` and
   `context_after`"*. A function that never returns the context cannot be shown to have preserved
   it; putting the two fields on the entry makes the preservation an assertion instead of an absence.
   This is the whole reason P4 split them (M5): *"M5's three context fields exist so §8.4 can redact
   a value without dropping its context."*
3. **`redaction.py` imports neither `privacy.items` nor `evidence_shape.observation`.** The
   skeleton's `Consumes` names both. `apply_redaction` takes flat values so that Task 7's
   `RedactedIdentifier` and Task 9's `Materialised` can each feed it without `redaction` depending on
   a module written in parallel by a different author. M5's three fields are consumed **as values**,
   which is the substance; the test imports `evidence_shape.observation.Observation` and drives the
   three fields through it, so the seam is still proved against P4's real record.

**The identifier class is an opaque string and this module enumerates none.** SPEC *Deferred*:
*"Which identifier classes exist and how each is transformed is not enumerated anywhere in the
design. `redaction_manifest` carries the class as an opaque string until this is authored."* The
classifier is injected, its return value is stored unexamined, and the test drives a deliberately
absurd class name through to prove nothing validates it. There is no regex, no gazetteer, no keyword
list, and no module-level collection constant of any kind — asserted by **runtime introspection of
the module namespace**, not by scanning source text, because a source scan matches docstrings and
that technique has produced a false result on this project more than once.

**Both protocols are injected with no default, and that is a safety property rather than a style.**
A build that forgets to wire a transform must fail loudly at the call, not emit unredacted values
under a helpful identity function. The test asserts it two ways: the parameters are `KEYWORD_ONLY`
with `inspect.Parameter.empty` defaults, and calling `apply_redaction` without them raises
`TypeError`. A transform that returns its input unchanged is refused with `RedactionIneffective` for
the same reason — an identity transform is the shape a forgotten wiring takes when someone does
supply one.

**C3 — the bounding box, and the guess this task refuses to make.** P4's region is exactly
`(x, y, w, h, unit)` with `unit` in `("px", "norm")`, validated by
`evidence_shape.location.region_from_mapping`. **`norm` does not say which corner it measures
from.** Apple Vision reports normalized coordinates from the **bottom-left**; most tooling — PDF
viewers, HTML canvases, the majority of OCR SDKs — measures from the **top-left**. A redaction that
picked the common convention and was wrong would blank a band mirrored about the horizontal centre
of the page: it would leave the passport number visible and cover something else, while the manifest
recorded `redacted = True`. That is worse than refusing, because the audit record would be false.

So `span_address` **raises `RegionOriginUnspecified`** on a region-addressed location, the message
names `REGION_ORIGIN_UNDECIDED`, and P7 redacts only what it can address in text. The mechanical
evidence that this is a real gap and not a scruple is in P4 itself: `serialize_locator` **drops the
region entirely** — an `ocr` location with a region serialises to `'ocr:page=2'` — and
`parse_locator(text, *, region=None)` takes it back as a separate argument, so P4's own canonical
address has no slot for a box. The test pins `REGION_UNITS == ("px", "norm")` and pins that
`dataclasses.fields(Region)` names no origin, so the day an origin is added the test goes red and
this refusal is revisited rather than forgotten. **NEEDS-JOSEPH C3.**

**The manifest never holds a second copy of the value.** `RedactionEntry` has no `value` field and
no `redacted_value` field, asserted over `dataclasses.fields`. §8.4 puts *"raw sensitive values"* in
the always-local set; a manifest that stored the pre-redaction value would be a local record of
exactly the thing the redaction removed, sitting in the same JSON blob that gets written to the audit
log. What the entry stores is the class, the yes/no, the address, and the context — which is what
SPEC §6 asks for: *"redaction_manifest[]  per item: identifier class, redacted yes/no."*

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_redaction.py
"""§8.4's "redacted identifiers", and the manifest that records what was redacted.

Four things this test refuses to let the implementation do:

- **Name an identifier class.** The SPEC's *Deferred* table says the classes are not
  enumerated anywhere in the design, so a nonsense class name is driven end to end and
  nothing may validate it.
- **Ship a default transform.** A build that forgets to wire one must fail at the call.
- **Throw away the context.** M5 split `context_before` / `context_after` /
  `context_truncated` out of `raw_value` precisely so §8.4 could redact a value without
  dropping what surrounds it.
- **Guess which corner `Region`'s `norm` unit measures from.** NEEDS-JOSEPH C3.
"""
import dataclasses
import inspect
import json

import pytest

from evidence_shape.canonical import canonical_json
from evidence_shape.location import (
    REGION_UNITS, Location, Region, Segment, TextSpan, TimeSpan,
)
from evidence_shape.locator import parse_locator, serialize_locator
from evidence_shape.observation import Observation

import privacy.redaction as redaction_module
from privacy.redaction import (
    REGION_ORIGIN_UNDECIDED, RedactionEntry, RedactionIneffective, RedactionManifest,
    RegionOriginUnspecified, apply_redaction, span_address,
)

CONTENT_HASH = "a" * 64
VALUE = "992-33-1188"
BEFORE = "Passport number "
AFTER = " issued 2019."
PAGE = (Segment(kind="page", index=2),)
TEXT_LOCATION = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
CELL_LOCATION = Location(zone="table", container_path=(
    Segment(kind="sheet", index=1), Segment(kind="row", index=4),
    Segment(kind="cell", index=3)))
OCR_LOCATION = Location(zone="ocr", container_path=PAGE,
                        region=Region(0.10, 0.22, 0.30, 0.04, "norm"))
KEY = "sha256:" + "b" * 64

#: Deliberately not a plausible identifier class. If anything in `src/privacy/`
#: validated, normalised, or recognised the class, this string would not survive.
ABSURD_CLASS = "  zzz-NOT-A-REAL-CLASS-éé  "


def classifier_naming(name):
    """An injected classifier. P7 owns no rule that decides what an identifier is."""
    def classify(value, *, context_before, context_after):
        return name
    return classify


def classifier_declining(value, *, context_before, context_after):
    """The other half of the injection: a value that is not an identifier."""
    return None


def transform_masking(value, *, identifier_class):
    return "[redacted]"


def transform_returning_the_value(value, *, identifier_class):
    """The shape a forgotten wiring takes when somebody does supply one."""
    return value


def redact(**over):
    base = dict(observation_key=KEY, span=span_address(TEXT_LOCATION),
                context_before=BEFORE, context_after=AFTER, context_truncated=False,
                classifier=classifier_naming("passport_number"),
                transform=transform_masking)
    base.update(over)
    return apply_redaction(VALUE, **base)


# --- the class is opaque, and this module enumerates none ---------------------

def test_the_identifier_class_is_whatever_the_classifier_said():
    # SPEC *Deferred*: "`redaction_manifest` carries the class as an opaque string
    # until this is authored." Whitespace, case and non-ASCII all survive, which is
    # what "opaque" means and what "normalised" would not.
    _, entry = redact(classifier=classifier_naming(ABSURD_CLASS))
    assert entry.identifier_class == ABSURD_CLASS


def test_src_privacy_redaction_enumerates_no_identifier_class():
    # The no-invention guard, by RUNTIME INTROSPECTION of the module namespace and
    # not by reading source text: a text scan matches docstrings, and this project
    # has already recorded that failure more than once. The one string constant is
    # the key of an open question; there is no collection constant at all.
    strings, collections = {}, {}
    for name, value in vars(redaction_module).items():
        if name.startswith("_"):
            continue
        if isinstance(value, str):
            strings[name] = value
        elif isinstance(value, (tuple, list, set, frozenset, dict)):
            collections[name] = value
    assert set(strings) == {"REGION_ORIGIN_UNDECIDED"}, strings
    assert collections == {}, (
        "a gazetteer, a class list, or a transform table would land here; §8.4 "
        "states WHAT is protected and never HOW it is recognised")


def test_the_open_question_is_carried_as_a_key_and_not_as_a_sentence():
    # The same rule the retraction limit follows: P7 asserts the obligation and
    # holds none of the copy.
    assert REGION_ORIGIN_UNDECIDED == "NEEDS-JOSEPH C3"


# --- both protocols are injected, with no default -----------------------------

def test_the_classifier_and_the_transform_are_keyword_only_with_no_default():
    parameters = inspect.signature(apply_redaction).parameters
    for name in ("classifier", "transform"):
        assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY
        assert parameters[name].default is inspect.Parameter.empty, (
            f"{name} has a default; a build that forgets to wire one would then "
            "emit unredacted values under a helpful identity function")


def test_apply_redaction_cannot_be_called_without_them():
    with pytest.raises(TypeError):
        apply_redaction(VALUE, observation_key=KEY, span=span_address(TEXT_LOCATION),
                        context_before=BEFORE, context_after=AFTER,
                        context_truncated=False)


def test_a_transform_that_returns_the_value_is_refused():
    with pytest.raises(RedactionIneffective):
        redact(transform=transform_returning_the_value)


# --- what redaction does, and what it leaves alone ----------------------------

def test_redaction_replaces_the_value():
    redacted, entry = redact()
    assert redacted == "[redacted]"
    assert entry.redacted is True


def test_a_declining_classifier_leaves_the_value_alone():
    # Not every materialised value is an identifier. §8.4 permits "selected excerpts"
    # beside "redacted identifiers"; an excerpt the injected rule set does not
    # recognise passes through, and the entry records that it was not redacted.
    redacted, entry = redact(classifier=classifier_declining)
    assert redacted == VALUE
    assert entry.redacted is False
    assert entry.identifier_class is None


def test_redaction_preserves_the_context():
    # M5, and the reason P4 split the field: "a redaction that returns the whole
    # surrounding text has thrown away the reason the fields were split" -- and one
    # that blanks the context has thrown away the other half.
    observation = Observation(
        file_id="file-1", content_hash=CONTENT_HASH, extractor_name="pdf_text",
        extractor_version="1.0.0", source_type="text_document", raw_value=VALUE,
        location=TEXT_LOCATION, occurrence_count=1,
        observed_at="2026-08-22T12:00:00+00:00", reliability="direct", run_id="run-1",
        context_before=BEFORE, context_after=AFTER, context_truncated=False)
    redacted, entry = apply_redaction(
        observation.raw_value, observation_key=KEY,
        span=span_address(observation.location),
        context_before=observation.context_before,
        context_after=observation.context_after,
        context_truncated=observation.context_truncated,
        classifier=classifier_naming("passport_number"), transform=transform_masking)
    assert redacted == "[redacted]"
    assert entry.context_before == BEFORE
    assert entry.context_after == AFTER
    assert VALUE not in entry.context_before + entry.context_after


def test_context_truncated_is_carried_through_to_the_entry():
    # §8.6 forbids anything being truncated silently. The flag is P4's third context
    # field and it is not a detail the manifest may drop.
    _, entry = redact(context_truncated=True)
    assert entry.context_truncated is True


def test_the_entry_holds_no_copy_of_the_value():
    # "raw sensitive values" are in §8.4's always-local set. A manifest that stored
    # the pre-redaction value would be a local copy of exactly what was removed,
    # inside the JSON that gets written to the audit log.
    names = {field.name for field in dataclasses.fields(RedactionEntry)}
    assert names == {"observation_key", "span", "identifier_class", "redacted",
                     "context_before", "context_after", "context_truncated"}
    assert "value" not in names and "redacted_value" not in names


def test_the_entry_is_frozen():
    _, entry = redact()
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.redacted = False


# --- the manifest -------------------------------------------------------------

def test_the_manifest_is_the_per_item_record():
    # SPEC §6: "redaction_manifest[]  per item: identifier class, redacted yes/no."
    _, one = redact(classifier=classifier_naming("passport_number"))
    _, two = redact(classifier=classifier_declining)
    manifest = RedactionManifest(entries=(one, two))
    assert manifest.identifier_classes == ("passport_number", None)
    assert manifest.any_redacted is True


def test_a_manifest_with_nothing_redacted_says_so():
    _, only = redact(classifier=classifier_declining)
    assert RedactionManifest(entries=(only,)).any_redacted is False
    assert RedactionManifest(entries=()).any_redacted is False


def test_the_manifest_serialises_as_canonical_json():
    # It travels inside the audit record's `explanation` (the preamble's shape
    # decision), so it has to survive `canonical_json` without a custom encoder.
    _, entry = redact()
    payload = canonical_json(RedactionManifest(entries=(entry,)).to_mapping())
    assert json.loads(payload) == [{
        "observation_key": KEY, "span": "body:page=2#16-27",
        "identifier_class": "passport_number", "redacted": True,
        "context_before": BEFORE, "context_after": AFTER,
        "context_truncated": False}]


# --- span_address, and the two forms it serialises ----------------------------

def test_span_address_of_a_text_span_is_p4s_canonical_locator():
    assert span_address(TEXT_LOCATION) == "body:page=2#16-27"
    assert parse_locator(span_address(TEXT_LOCATION)) == TEXT_LOCATION


def test_span_address_of_a_container_path_address_is_the_same_serialiser():
    # §2.3's table/row/cell has no text span at all; the address IS the citation.
    assert span_address(CELL_LOCATION) == "table:sheet=1/row=4/cell=3"
    assert parse_locator(span_address(CELL_LOCATION)) == CELL_LOCATION


# --- C3: the bounding box this task will not guess at -------------------------

def test_a_region_address_is_refused_and_names_the_open_decision():
    with pytest.raises(RegionOriginUnspecified) as caught:
        span_address(OCR_LOCATION)
    assert REGION_ORIGIN_UNDECIDED in str(caught.value)


def test_p4s_region_names_no_origin():
    # (x, y, w, h, unit) and unit in ("px", "norm"). Neither says which corner the
    # origin sits in: Apple Vision measures from bottom-left, most tooling from
    # top-left, and a wrong guess covers a band mirrored about the page centre --
    # leaving the value visible while the manifest records `redacted = True`.
    assert REGION_UNITS == ("px", "norm")
    assert tuple(f.name for f in dataclasses.fields(Region)) == (
        "x", "y", "w", "h", "unit")


def test_p4s_own_canonical_address_cannot_carry_a_region_either():
    # The mechanical form of C3, and the reason this is a gap rather than a scruple:
    # `serialize_locator` drops the region, and `parse_locator` takes it back as a
    # SEPARATE argument. There is no slot for a box in the address.
    assert serialize_locator(OCR_LOCATION) == "ocr:page=2"
    assert parse_locator("ocr:page=2").region is None
    assert parse_locator("ocr:page=2", region=OCR_LOCATION.region) == OCR_LOCATION


def test_a_time_span_address_is_refused_too():
    # A transcript offset is an address P7 publishes no redaction for. §2.9 puts
    # speech-to-text behind "an explicit privacy and compute policy" and this task
    # owns none of it; refusing is the honest answer, and it is not C3's question.
    spoken = Location(zone="transcript", container_path=(),
                      time_span=TimeSpan(1000, 2000))
    with pytest.raises(RegionOriginUnspecified):
        span_address(spoken)
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_redaction.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.redaction'`. Collection fails on the
import line; no test runs.

- [ ] **Step 3: Write `src/privacy/redaction.py`**

```python
# src/privacy/redaction.py
"""§8.4's "redacted identifiers", and the manifest that says what was redacted.

Four things are decided here, and each is a quotation or a refusal rather than a
choice:

- **The identifier class is an opaque string.** SPEC *Deferred*: "Which identifier
  classes exist and how each is transformed is not enumerated anywhere in the design.
  `redaction_manifest` carries the class as an opaque string until this is authored."
  Nothing in this module validates, normalises, or recognises one.
- **The classifier and the transform are injected with no default.** §8.4 states WHAT
  is protected and never HOW it is recognised. A default would be a rule set, and a
  default that did nothing would be an unredacted value emitted by a build that forgot
  to wire one.
- **The value is replaced and its context is not.** M5 split `context_before`,
  `context_after` and `context_truncated` out of the observation "precisely so §8.4
  can redact a value without dropping its context". Both halves of that are properties
  of the entry this module returns, so both can be asserted.
- **A region address is refused, by name (NEEDS-JOSEPH C3).** P4's region is
  `(x, y, w, h, unit)` with `unit` in `("px", "norm")` and neither unit names the
  corner the origin sits in. Apple Vision measures normalized coordinates from the
  bottom-left; most tooling measures from the top-left. Guessing would blank a band
  mirrored about the page's horizontal centre -- the value still visible, the manifest
  still saying `redacted = True`, which is worse than refusing because it makes the
  audit record false. P4's own `serialize_locator` drops the region and `parse_locator`
  takes it back separately, so there is not even an address to record.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from evidence_shape.location import Location
from evidence_shape.locator import serialize_locator

#: The open decision this module refuses to make. A key, not a sentence: the wording
#: belongs to whoever answers it, exactly as §8.4's retraction-limit copy does.
REGION_ORIGIN_UNDECIDED: str = "NEEDS-JOSEPH C3"


class RedactionIneffective(Exception):
    """The transform returned its input. That is not a redaction, and recording it
    as one would put a false `redacted = True` in the audit log."""


class RegionOriginUnspecified(Exception):
    """The address is a bounding box and no origin corner is defined (C3).

    Also raised for a time span, for the narrower reason that P7 publishes no
    redaction for a transcript offset at all. Both are "this address has no
    redactable form here", and neither is a silent fallback to the whole unit.
    """


class IdentifierClassifier(Protocol):
    """The injected rule set. Returns an opaque class name, or None for a value that
    is not an identifier. P7 ships no implementation of this protocol."""

    def __call__(self, value: str, *, context_before: str | None,
                 context_after: str | None) -> str | None: ...


class RedactionTransform(Protocol):
    """The injected transform. §8.4 says "redacted identifiers" and never says how."""

    def __call__(self, value: str, *, identifier_class: str) -> str: ...


@dataclass(frozen=True, slots=True)
class RedactionEntry:
    """One row of SPEC §6's `redaction_manifest[]`: "per item: identifier class,
    redacted yes/no" -- plus the address it applies to and M5's three context fields.

    There is deliberately no `value` and no `redacted_value`. §8.4 puts "raw sensitive
    values" in the always-local set, and this record travels inside the audit event's
    `explanation`.
    """

    observation_key: str
    span: str
    identifier_class: str | None
    redacted: bool
    context_before: str | None
    context_after: str | None
    context_truncated: bool

    def to_mapping(self) -> dict[str, object]:
        return {
            "observation_key": self.observation_key,
            "span": self.span,
            "identifier_class": self.identifier_class,
            "redacted": self.redacted,
            "context_before": self.context_before,
            "context_after": self.context_after,
            "context_truncated": self.context_truncated,
        }


@dataclass(frozen=True, slots=True)
class RedactionManifest:
    """SPEC §6's `redaction_manifest[]`, as one object so `Released` carries one field."""

    entries: tuple[RedactionEntry, ...]

    @property
    def any_redacted(self) -> bool:
        """§8.4's audit field: "whether values were redacted"."""
        return any(entry.redacted for entry in self.entries)

    @property
    def identifier_classes(self) -> tuple[str | None, ...]:
        return tuple(entry.identifier_class for entry in self.entries)

    def to_mapping(self) -> list[dict[str, object]]:
        return [entry.to_mapping() for entry in self.entries]


def span_address(location: Location) -> str:
    """P4's canonical locator, and the two addressing forms P7 can redact.

    A text span serialises to `body:page=2#16-27`; a container-path address to
    `table:sheet=1/row=4/cell=3`. Both round-trip through `parse_locator`, which is
    what lets SPEC §7's audit record "reconstruct the released payload from local
    storage" rather than merely name it.

    A region or a time span raises. `serialize_locator` drops a region, so the string
    it returns would silently address the whole page.
    """
    if location.region is not None:
        raise RegionOriginUnspecified(
            f"{location.zone}:{serialize_locator(location)} carries a bounding box "
            f"and `Region(x, y, w, h, unit)` names no origin corner -- `norm` is "
            f"bottom-left in Apple Vision and top-left in most other tooling, so a "
            f"redaction band placed from a guess covers a mirrored region while the "
            f"manifest records it as redacted. P4's own locator drops the region "
            f"(`{serialize_locator(location)}`) and `parse_locator` takes it back as "
            f"a separate argument, so there is no address to record either. "
            f"{REGION_ORIGIN_UNDECIDED}")
    if location.time_span is not None:
        raise RegionOriginUnspecified(
            f"{serialize_locator(location)} is a transcript offset and P7 publishes "
            f"no redaction for one; §2.9 puts speech-to-text behind an explicit "
            f"privacy and compute policy this task does not own")
    return serialize_locator(location)


def apply_redaction(value: str, *, observation_key: str, span: str,
                    context_before: str | None, context_after: str | None,
                    context_truncated: bool, classifier: IdentifierClassifier,
                    transform: RedactionTransform) -> tuple[str, RedactionEntry]:
    """Redact one materialised value, and record what was done to it.

    Returns `(value_to_release, entry)`. The context is returned on the entry
    unchanged: M5's fields exist so a value can be redacted without dropping what
    surrounds it, and a caller that has both can prove it kept them.
    """
    identifier_class = classifier(value, context_before=context_before,
                                  context_after=context_after)
    if identifier_class is None:
        return value, RedactionEntry(
            observation_key=observation_key, span=span, identifier_class=None,
            redacted=False, context_before=context_before,
            context_after=context_after, context_truncated=context_truncated)
    redacted = transform(value, identifier_class=identifier_class)
    if redacted == value:
        raise RedactionIneffective(
            f"the transform returned its input for identifier_class "
            f"{identifier_class!r}; recording that as `redacted = True` would put a "
            f"false statement in the §8.4 audit record, and returning it as redacted "
            f"would release the value")
    return redacted, RedactionEntry(
        observation_key=observation_key, span=span,
        identifier_class=identifier_class, redacted=True,
        context_before=context_before, context_after=context_after,
        context_truncated=context_truncated)
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_redaction.py -v`
Expected: PASS — 21 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–8 green, and P1–P5's 1302 tests still green (P7 modified no file belonging
to another part).

- [ ] **Step 6: Commit**

```bash
git add src/privacy/redaction.py tests/p7/test_p7_redaction.py
git commit -m "feat(P7): redaction with an opaque identifier class, and a region address refused by name (C3)"
```

---

---

### Task 9: Excerpt resolution — the only place content materialises

**Files:**
- Create: `src/privacy/resolve.py`
- Test: `tests/p7/test_p7_resolve.py`

**Interfaces:**
- Consumes: `evidence_shape.store.observations_by_key(conn, observation_key) ->
  list[Observation]`, `.get_observation(conn, observation_id) -> Observation`,
  `.unit_for_observation(conn, observation) -> TextUnit | None`,
  `evidence_shape.text_units.raw_value_at(unit, text_span) -> str`,
  `.check_span_anchor(observation, unit) -> None`, `.SpanAnchorError`,
  `evidence_shape.location.TextSpan`, `privacy.redaction.span_address(location) -> str`,
  `.RegionOriginUnspecified`.
- Produces (`resolve.py`):
  - `Materialised` — frozen: `observation_key: str`, `span: str`, `value: str`, `zone: str`,
    `context_before: str | None`, `context_after: str | None`, `context_truncated: bool`,
    `unit_length: int | None`.
  - `MATERIALISERS: Mapping[str, tuple[str, ...]]` — the P4 functions that turn a record into text,
    by module, so the single-locus guard has a subject rather than a guess.
  - `UnresolvableSpan`, `AmbiguousObservationKey`.
  - `current_observation(conn, observation_key) -> Observation`.
  - `materialise(conn, item) -> Materialised`.

**Done-means:** substrate for 3 (L2), 4, 5, 6.

**This module is the door's threshold, and everything about it is narrow on purpose.** It is the
only module under `src/privacy/` that imports a P4 text materialiser; `release.py` is the only module
that imports it; and Task 21 re-asserts both repo-wide. `MATERIALISERS` is published here so that
guard names the eight functions rather than pattern-matching on the word "text".

**The current-row rule, and the P4 gap it exposes — reported, and closed with one narrow read.**
P4's docstring is explicit that the reader is multi-valued: *"A LIST: two extractor versions carry
one key, which is what MINOR 8 arranged and what §8.5's cross-version diff reads."* The gate must
resolve to the **current** row, because resolving to a superseded one releases text an extractor
upgrade has already retracted. But — verified by import, 2026-08-22 — `Observation` has seventeen
fields and **`observation_id` and `superseded_by` are not among them**; supersession lives on the
`evidence` row, and P4's `supersede_chain(conn, observation_id)` needs an id the list does not carry.
**There is no published reader that returns the current row for a key.**

So `current_observation` does exactly one thing P4 does not publish — a read-only

```sql
SELECT observation_id FROM evidence WHERE observation_key = ? AND superseded_by IS NULL
```

— and then hands the id straight back to P4's published `get_observation`. It is a **read**, not a
write; P7 modifies no P1–P5 file; and the whole of the record's construction stays P4's. **The
addition that would remove it is one function, `evidence_shape.store.current_observation_by_key(conn,
observation_key) -> Observation | None`**, and it belongs in P4 rather than here. Reported, not
patched — the same posture this plan takes on P5's zero-argument `transcription_authorized`.

**Two resolvers, and no third; a missing resolver is a refusal, not a fallback.**

- **`text_span` → `raw_value_at(unit, text_span)`.** The precondition is P4's own
  `check_span_anchor`, which *"raises; never returns a repair"*. A `SpanAnchorError` becomes
  `UnresolvableSpan`, chained with `from`, and no substring is returned. A gate that repaired would
  release text nobody addressed — and P4 does **not** validate the anchor at write time (verified: a
  non-anchoring observation records cleanly), so this check is load-bearing rather than belt-and-braces.
- **container-path only → `Observation.raw_value`.** §2.3's table/row/cell and §2.8's EXIF field are
  addressed entirely by `container_path`, and `unit_for_observation` returns **`None`** for them —
  verified against a real database. There is no unit, so there is nothing to take a substring of, and
  the materialisable value is the observation's own `raw_value`. It must **never** fall back to the
  whole unit: that is how "send the cell" becomes "send the sheet".
- **A region or a time span raises `RegionOriginUnspecified`** through `span_address` (Task 8, C3).
  P7 publishes no third resolver, and the refusal is what keeps the two above honest.

**Task 9 pins one field of Task 7's items, because it cannot resolve without knowing its type.**
`Excerpt.span` and `RedactedIdentifier.span` are `evidence_shape.location.TextSpan | None` — `None`
for the container-path form, where the address is the whole citation. SPEC §4 spells the items as
`{ observation_key, span, reason }` and `{ observation_key, span, identifier_class }`; P4's span type
is `TextSpan` and Task 7's `Consumes` already imports it. Reported as a pin.

**The caller's span is a claim; the observation's span is the answer.** SPEC §4: an excerpt is
*"resolved by the gate from local storage"*. If `item.span` disagrees with
`observation.location.text_span`, that is `UnresolvableSpan` — the caller has addressed something the
key does not carry, and the gate neither honours the caller's coordinates nor silently substitutes
its own.

**M14, made falsifiable.** A caller who passes an `observation_id` where an `observation_key` belongs
gets `UnresolvableSpan`, because `observations_by_key` returns `[]` for it. That is the test that
makes *"The key, not the id, is what makes that durable"* a property rather than a convention.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_resolve.py
"""The one place in the repository where (observation_key, span) becomes text.

Everything here is about narrowness. Two resolvers and no third; the current row and
not the first; a refusal where P4 gives no answer, never a best-effort substring; and
an AST guard proving no other module under `src/privacy/` binds a P4 materialiser.
"""
import ast
import dataclasses
import pathlib

import pytest

from evidence_shape.location import Location, Region, Segment, TextSpan, TimeSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import (
    get_observation, observations_by_key, record_observation, record_run,
    record_text_unit, supersede_observation, unit_for_observation,
)
from evidence_shape.text_units import TextUnit

import privacy
from privacy.redaction import RegionOriginUnspecified, span_address
from privacy.resolve import (
    MATERIALISERS, AmbiguousObservationKey, Materialised, UnresolvableSpan,
    current_observation, materialise,
)

CONTENT_HASH = "a" * 64
FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T13:00:00+00:00"
PAGE = (Segment(kind="page", index=2),)
BODY = "Passport number 992-33-1188 issued 2019."
VALUE = "992-33-1188"
BEFORE = "Passport number "
AFTER = " issued 2019."
CELL = (Segment(kind="sheet", index=1), Segment(kind="row", index=4),
        Segment(kind="cell", index=3))


class Item:
    """Stands in for Task 7's `Excerpt` / `RedactedIdentifier`.

    Task 9 reads exactly two attributes -- `observation_key` and `span` -- and Task 7
    owns the rest of the shape. A local stand-in keeps this test from going red when a
    field this module never touches is added next door, and states the pin: `span` is
    a `TextSpan | None`.
    """

    def __init__(self, observation_key: str, span: TextSpan | None):
        self.observation_key = observation_key
        self.span = span


@pytest.fixture()
def evidence(p7_conn):
    create_evidence_schema(p7_conn)
    return p7_conn


def a_run(conn, run_id, version, started):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id="file-1", content_hash=CONTENT_HASH,
        extractor_name="pdf_text", extractor_version=version,
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=started, observation_count=1))


def an_observation(conn, *, run_id, version, location, raw_value=VALUE,
                   context_before=BEFORE, context_after=AFTER,
                   context_truncated=False, extractor_name="pdf_text",
                   source_type="text_document", observed_at=FIXED_CLOCK) -> str:
    return record_observation(conn, Observation(
        file_id="file-1", content_hash=CONTENT_HASH, extractor_name=extractor_name,
        extractor_version=version, source_type=source_type, raw_value=raw_value,
        location=location, occurrence_count=1, observed_at=observed_at,
        reliability="direct", run_id=run_id, context_before=context_before,
        context_after=context_after, context_truncated=context_truncated))


def key_for(location, *, extractor_name="pdf_text", raw_value=VALUE) -> str:
    """P4 mints the key from `serialize_locator`, not from `span_address`.

    They agree on the two forms P7 can resolve and differ on the two it refuses --
    `span_address` raises for a region and a time span, and P4 still has a key for
    both. The key is P4's, so the test computes it P4's way.
    """
    return observation_key(content_hash=CONTENT_HASH, extractor_name=extractor_name,
                           locator=serialize_locator(location), raw_value=raw_value)


@pytest.fixture()
def one_excerpt(evidence):
    """One run, one unit, one observation: the ordinary text-span case."""
    a_run(evidence, "run-1", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-1", container_path=PAGE, text=BODY))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    an_observation(evidence, run_id="run-1", version="1.0.0", location=location)
    return key_for(location), location


# --- the ordinary text-span path ---------------------------------------------

def test_a_text_span_materialises_the_substring(evidence, one_excerpt):
    key, location = one_excerpt
    result = materialise(evidence, Item(key, TextSpan(16, 27)))
    assert result.value == VALUE
    assert result.value == BODY[16:27]


def test_the_result_carries_the_key_the_address_and_the_zone(evidence, one_excerpt):
    key, location = one_excerpt
    result = materialise(evidence, Item(key, TextSpan(16, 27)))
    assert result.observation_key == key
    assert result.span == "body:page=2#16-27" == span_address(location)
    assert result.zone == "body"


def test_the_three_context_fields_travel_with_the_value(evidence, one_excerpt):
    # M5, and Task 8's whole reason for existing: §8.4 redacts the value without
    # dropping what surrounds it, so the value cannot arrive at the redactor alone.
    key, _ = one_excerpt
    result = materialise(evidence, Item(key, TextSpan(16, 27)))
    assert result.context_before == BEFORE
    assert result.context_after == AFTER
    assert result.context_truncated is False


def test_context_truncated_travels_too(evidence):
    # §8.6 forbids anything being truncated silently, so the flag reaches the manifest.
    a_run(evidence, "run-t", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-t", container_path=PAGE, text=BODY))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    an_observation(evidence, run_id="run-t", version="1.0.0", location=location,
                   context_truncated=True)
    result = materialise(evidence, Item(key_for(location), TextSpan(16, 27)))
    assert result.context_truncated is True


def test_materialised_holds_no_path_and_no_file_id(evidence, one_excerpt):
    # §8.4 puts "Paths" in the always-local set. The type cannot carry one.
    names = {field.name for field in dataclasses.fields(Materialised)}
    assert names == {"observation_key", "span", "value", "zone", "context_before",
                     "context_after", "context_truncated", "unit_length"}
    assert not names & {"file_id", "path", "current_path", "filename", "content_hash"}


def test_unit_length_travels_so_the_whole_document_check_can_run(evidence, one_excerpt):
    # §8.4: "It should not send full documents where a short heading or OCR excerpt
    # is enough to resolve the question." Task 7's `check_item(item, *, unit_length)`
    # needs the stored length, and this is the only module that may ask P4 for it.
    key, _ = one_excerpt
    assert materialise(evidence, Item(key, TextSpan(16, 27))).unit_length == len(BODY)


def test_a_container_path_address_has_no_unit_length(evidence, one_cell):
    key, _ = one_cell
    assert materialise(evidence, Item(key, None)).unit_length is None


def test_materialised_is_frozen(evidence, one_excerpt):
    key, _ = one_excerpt
    result = materialise(evidence, Item(key, TextSpan(16, 27)))
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.value = "anything else"


# --- the current-row rule ------------------------------------------------------

@pytest.fixture()
def two_versions(evidence):
    """P4's guaranteed shape: two extractor versions, one key (MINOR 8)."""
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    a_run(evidence, "run-1", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-1", container_path=PAGE, text=BODY))
    old = an_observation(evidence, run_id="run-1", version="1.0.0", location=location)
    a_run(evidence, "run-2", "2.0.0", LATER)
    record_text_unit(evidence, TextUnit(run_id="run-2", container_path=PAGE, text=BODY))
    new = an_observation(evidence, run_id="run-2", version="2.0.0", location=location,
                         observed_at=LATER)
    return key_for(location), old, new


def test_p4_really_does_return_two_rows_for_one_key(evidence, two_versions):
    # The premise. If P4 ever made the key unique this test goes red and the
    # current-row rule below becomes unnecessary rather than silently wrong.
    key, _, _ = two_versions
    assert len(observations_by_key(evidence, key)) == 2


def test_resolution_picks_the_current_row_and_not_the_first(evidence, two_versions):
    key, old, new = two_versions
    supersede_observation(evidence, old_observation_id=old, new_observation_id=new,
                          reason="extractor upgrade")
    resolved = current_observation(evidence, key)
    assert resolved.extractor_version == "2.0.0"
    assert resolved.run_id == "run-2"
    assert resolved == get_observation(evidence, new)


def test_two_unsuperseded_rows_raise_rather_than_picking_one(evidence, two_versions):
    # "an unresolvable ambiguity raises rather than picking the first." Releasing the
    # wrong one of two live rows is a silent release of retracted text.
    key, _, _ = two_versions
    with pytest.raises(AmbiguousObservationKey):
        current_observation(evidence, key)


def test_p1s_writer_refuses_to_build_a_headless_chain(evidence, two_versions):
    # Verified against the live substrate: `mark_superseded` rejects a cycle and
    # rejects re-superseding a superseded row, so a key with no live head cannot be
    # reached through P1's published writer at all. Asserted here so the next test's
    # raw UPDATE is legible as "around the writer" rather than as normal usage.
    key, old, new = two_versions
    supersede_observation(evidence, old_observation_id=old, new_observation_id=new,
                          reason="extractor upgrade")
    with pytest.raises(ValueError, match="cycle"):
        supersede_observation(evidence, old_observation_id=new,
                              new_observation_id=old,
                              reason="a cycle nobody meant to write")


def test_a_key_with_no_live_row_raises(evidence, two_versions):
    # Reachable only by writing around P1's writer -- which is what a hand-edited,
    # half-restored, or partially migrated database looks like. The gate answers it
    # with a refusal rather than with whichever row it happened to see last.
    key, old, new = two_versions
    supersede_observation(evidence, old_observation_id=old, new_observation_id=new,
                          reason="extractor upgrade")
    evidence.execute("UPDATE evidence SET superseded_by = ? WHERE observation_id = ?",
                     (old, new))
    with pytest.raises(AmbiguousObservationKey):
        current_observation(evidence, key)


def test_an_unknown_key_is_unresolvable(evidence):
    with pytest.raises(UnresolvableSpan):
        current_observation(evidence, "sha256:" + "f" * 64)


def test_an_observation_id_is_not_a_citation_handle(evidence, one_excerpt):
    # M14: "a per-row `observation_id` dies on extractor upgrade". A caller who
    # passes one gets a refusal here rather than a resolution that stops working
    # the next time an extractor ships.
    key, location = one_excerpt
    row = evidence.execute(
        "SELECT observation_id FROM evidence WHERE observation_key = ?", (key,)
    ).fetchone()
    with pytest.raises(UnresolvableSpan):
        current_observation(evidence, row["observation_id"])


def test_p4_publishes_no_current_row_reader(evidence, one_excerpt):
    # The reported gap, asserted so it cannot be quietly forgotten: the published
    # reader returns records with no id and no supersession column, so P7 cannot
    # ask P4 which row is current. `store.current_observation_by_key` would close it.
    key, _ = one_excerpt
    (only,) = observations_by_key(evidence, key)
    names = {field.name for field in dataclasses.fields(only)}
    assert "observation_id" not in names
    assert "superseded_by" not in names


# --- the second resolver: a container-path address -----------------------------

@pytest.fixture()
def one_cell(evidence):
    a_run(evidence, "run-c", "1.0.0", FIXED_CLOCK)
    location = Location(zone="table", container_path=CELL)
    an_observation(evidence, run_id="run-c", version="1.0.0", location=location,
                   raw_value="4,200.00", extractor_name="xlsx_tables",
                   source_type="spreadsheet", context_before=None, context_after=None)
    return key_for(location, extractor_name="xlsx_tables", raw_value="4,200.00"), location


def test_a_container_path_address_materialises_the_raw_value(evidence, one_cell):
    key, location = one_cell
    result = materialise(evidence, Item(key, None))
    assert result.value == "4,200.00"
    assert result.span == "table:sheet=1/row=4/cell=3"
    assert result.zone == "table"


def test_a_container_path_address_has_no_text_unit_at_all(evidence, one_cell):
    # The reason it is a SECOND resolver and not a degenerate first: there is
    # nothing to take a substring of.
    key, _ = one_cell
    assert unit_for_observation(evidence, current_observation(evidence, key)) is None


def test_a_container_path_address_never_falls_back_to_a_unit(evidence, one_cell):
    # Even with a unit sitting at the same run, the cell address resolves to the
    # cell. "Send the cell" must not become "send the sheet".
    key, _ = one_cell
    record_text_unit(evidence, TextUnit(run_id="run-c", container_path=CELL,
                                        text="the whole sheet, flattened"))
    assert materialise(evidence, Item(key, None)).value == "4,200.00"


# --- refusals ------------------------------------------------------------------

def test_a_span_that_does_not_anchor_is_unresolvable(evidence):
    # P4 does NOT validate the anchor at write time -- verified against the live
    # store, a non-anchoring observation records cleanly -- so this check is the
    # only thing standing between a stale span and released text.
    a_run(evidence, "run-x", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-x", container_path=PAGE,
                                        text="X" * 40))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    an_observation(evidence, run_id="run-x", version="1.0.0", location=location)
    with pytest.raises(UnresolvableSpan) as caught:
        materialise(evidence, Item(key_for(location), TextSpan(16, 27)))
    assert "RAW-1" in str(caught.value.__cause__)


def test_a_failed_anchor_returns_no_substring_at_all(evidence):
    # "P4's checker raises; never returns a repair, and a gate that repaired would
    # release text nobody addressed." The wrong substring is right there in the
    # unit; nothing hands it back.
    a_run(evidence, "run-y", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-y", container_path=PAGE,
                                        text="X" * 40))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    an_observation(evidence, run_id="run-y", version="1.0.0", location=location)
    with pytest.raises(UnresolvableSpan):
        materialise(evidence, Item(key_for(location), TextSpan(16, 27)))


def test_a_span_beyond_the_stored_unit_is_unresolvable(evidence):
    a_run(evidence, "run-z", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-z", container_path=PAGE,
                                        text="short", truncated=True))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(10, 20))
    an_observation(evidence, run_id="run-z", version="1.0.0", location=location,
                   raw_value="beyond")
    with pytest.raises(UnresolvableSpan):
        materialise(evidence, Item(key_for(location, raw_value="beyond"),
                                   TextSpan(10, 20)))


def test_a_text_span_with_no_unit_is_unresolvable(evidence):
    a_run(evidence, "run-w", "1.0.0", FIXED_CLOCK)
    location = Location(zone="body", container_path=(Segment(kind="page", index=9),),
                        text_span=TextSpan(0, 6))
    an_observation(evidence, run_id="run-w", version="1.0.0", location=location,
                   raw_value="orphan")
    with pytest.raises(UnresolvableSpan):
        materialise(evidence, Item(key_for(location, raw_value="orphan"),
                                   TextSpan(0, 6)))


def test_the_callers_span_must_match_the_one_the_key_carries(evidence, one_excerpt):
    # SPEC §4: an excerpt is "resolved by the gate from local storage". The caller's
    # coordinates are a claim, and a claim that disagrees with the record is refused
    # rather than honoured or silently replaced.
    key, _ = one_excerpt
    with pytest.raises(UnresolvableSpan):
        materialise(evidence, Item(key, TextSpan(0, 39)))


def test_a_region_addressed_observation_is_refused(evidence):
    # NEEDS-JOSEPH C3, reached through Task 8's `span_address`.
    a_run(evidence, "run-r", "1.0.0", FIXED_CLOCK)
    location = Location(zone="ocr", container_path=PAGE,
                        region=Region(0.10, 0.22, 0.30, 0.04, "norm"))
    an_observation(evidence, run_id="run-r", version="1.0.0", location=location,
                   raw_value="992-33-1188", extractor_name="ocr_engine",
                   source_type="ocr")
    key = key_for(location, extractor_name="ocr_engine")
    with pytest.raises(RegionOriginUnspecified):
        materialise(evidence, Item(key, None))


def test_a_time_span_addressed_observation_is_refused(evidence):
    a_run(evidence, "run-a", "1.0.0", FIXED_CLOCK)
    location = Location(zone="transcript", container_path=(),
                        time_span=TimeSpan(1000, 2000))
    an_observation(evidence, run_id="run-a", version="1.0.0", location=location,
                   raw_value="spoken", extractor_name="whisper_local",
                   source_type="audio_video")
    key = key_for(location, extractor_name="whisper_local", raw_value="spoken")
    with pytest.raises(RegionOriginUnspecified):
        materialise(evidence, Item(key, None))


# --- the single-locus guard ----------------------------------------------------

def test_the_materialiser_list_names_p4s_functions_and_not_a_pattern():
    assert MATERIALISERS["evidence_shape.text_units"] == ("raw_value_at",)
    assert "unit_for_observation" in MATERIALISERS["evidence_shape.store"]
    assert "get_observation" in MATERIALISERS["evidence_shape.store"]


def test_resolve_is_the_only_module_under_src_privacy_that_binds_one():
    # Asserted by walking the AST, not by reading source text: a text scan matches
    # docstrings and comments, and this repository has recorded that false result
    # more than once. Task 21 runs the same walk over the finished package.
    package = pathlib.Path(privacy.__file__).parent
    offenders: dict[str, list[str]] = {}
    for path in sorted(package.glob("*.py")):
        if path.name == "resolve.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        bound: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                names = MATERIALISERS.get(node.module or "", ())
                bound |= {f"{node.module}.{a.name}" for a in node.names
                          if a.name in names}
            elif isinstance(node, ast.Import):
                bound |= {a.name for a in node.names if a.name in MATERIALISERS}
        if bound:
            offenders[path.name] = sorted(bound)
    assert offenders == {}, (
        f"{sorted(offenders)} bind a P4 materialiser; resolve.py is the only module "
        "under src/privacy/ that may, and release.py is the only one that may import "
        "resolve")
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_resolve.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.resolve'`. Collection fails on the
import line; no test runs.

- [ ] **Step 3: Write `src/privacy/resolve.py`**

```python
# src/privacy/resolve.py
"""(observation_key, span) -> text. The only module in the product that does this.

Everything about this module is narrow deliberately:

- **The handle is the key, never the id** (M14). SPEC *Correction learning*: "The key,
  not the id, is what makes that durable" -- a per-row `observation_id` dies when the
  extractor is upgraded, and a citation that stops resolving is a citation that stops
  being evidence.
- **The current row, not the first.** P4's reader is a LIST on purpose: "two extractor
  versions carry one key, which is what MINOR 8 arranged". Resolving to a superseded
  row would release text a later extractor already retracted.
- **Two resolvers and no third.** A `text_span` materialises through P4's
  `raw_value_at` behind P4's own `check_span_anchor`; a container-path-only address
  (§2.3's table/row/cell, §2.8's EXIF field) materialises `Observation.raw_value`,
  because `unit_for_observation` returns None for one and there is nothing to take a
  substring of. Anything else raises. A fallback to the whole unit is how "send the
  cell" becomes "send the sheet".
- **A failure is a refusal, never a repair.** P4's checker "raises; never returns a
  repair", and P4 does not validate the anchor at write time, so this is the only
  thing between a stale span and released text.

One thing here is not P4's, and it is reported rather than hidden: P4 publishes no
reader that returns the CURRENT row for a key. `observations_by_key` returns records
carrying neither `observation_id` nor `superseded_by`, and `supersede_chain` needs an
id those records do not have. `current_observation` therefore issues one read-only
SELECT for the live id and hands it straight back to P4's published `get_observation`.
The one-function fix belongs in P4 -- `store.current_observation_by_key(conn,
observation_key) -> Observation | None` -- and this module is the caller waiting for it.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.store import (
    get_observation, observations_by_key, unit_for_observation,
)
from evidence_shape.observation import Observation
from evidence_shape.text_units import SpanAnchorError, check_span_anchor, raw_value_at

from privacy.redaction import span_address

#: The P4 functions that turn a stored record into a string of document text, by
#: module. Published so Task 21's single-locus guard names them instead of matching
#: on the word "text" -- an AST walk needs a subject, and a guess is how a guard
#: passes vacuously.
MATERIALISERS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "evidence_shape.store": (
        "get_observation", "observation_row", "observations_by_key",
        "observations_for_file", "observations_for_run", "text_unit_at",
        "text_units_for_run", "unit_for_observation",
    ),
    "evidence_shape.text_units": ("raw_value_at",),
})


class UnresolvableSpan(Exception):
    """The address does not resolve, and the gate does not guess.

    Raised for an unknown key, an id passed where a key belongs, a span that does not
    anchor, a span with no unit, and a caller span that disagrees with the record.
    """


class AmbiguousObservationKey(Exception):
    """The key resolves to no live row, or to more than one.

    P4's reader is multi-valued on purpose; the supersession chain is what makes it
    single-valued again. When it does not, picking one would release the wrong text
    silently, so this raises instead.
    """


@dataclass(frozen=True, slots=True)
class Materialised:
    """One resolved item, with M5's three context fields still attached.

    No `file_id`, no path, no `content_hash`: §8.4 puts "Paths" and "file hashes" in
    the always-local set, and the type is where that is cheapest to enforce.

    `unit_length` is the STORED length of the text unit the span points into, or None
    for a container-path address that has no unit. Task 7's whole-document check --
    §8.4's "It should not send full documents where a short heading or OCR excerpt is
    enough to resolve the question" -- needs it, and this module is the only one that
    may ask P4 for it.
    """

    observation_key: str
    span: str
    value: str
    zone: str
    context_before: str | None
    context_after: str | None
    context_truncated: bool
    unit_length: int | None


def _live_observation_ids(conn: sqlite3.Connection,
                          observation_key: str) -> list[str]:
    """The rows for this key that nothing has superseded.

    The one read P4 does not publish. See the module docstring: `Observation` carries
    neither the id nor the supersession columns, so the current-row rule cannot be
    expressed with the published readers alone.
    """
    return [row["observation_id"] for row in conn.execute(
        "SELECT observation_id FROM evidence "
        "WHERE observation_key = ? AND superseded_by IS NULL ORDER BY rowid",
        (observation_key,))]


def current_observation(conn: sqlite3.Connection,
                        observation_key: str) -> Observation:
    """The one live row for a key, or a refusal."""
    candidates = observations_by_key(conn, observation_key)
    if not candidates:
        raise UnresolvableSpan(
            f"no observation carries key {observation_key!r}. P4's citation handle is "
            "the content-addressed `observation_key`, not the per-row "
            "`observation_id`, which dies on extractor upgrade (M14)")
    live = _live_observation_ids(conn, observation_key)
    if not live:
        raise AmbiguousObservationKey(
            f"key {observation_key!r} has {len(candidates)} rows and every one is "
            "superseded; the chain has no head, so there is no current text to release")
    if len(live) > 1:
        raise AmbiguousObservationKey(
            f"key {observation_key!r} has {len(live)} live rows. P4 returns a list "
            "because two extractor versions carry one key (MINOR 8); the supersession "
            "chain is what makes it single-valued, and picking one of two would "
            "release text an upgrade may already have retracted")
    return get_observation(conn, live[0])


def materialise(conn: sqlite3.Connection, item) -> Materialised:
    """Resolve one requested item against local storage.

    `item` is Task 7's `Excerpt` or `RedactedIdentifier`: it needs an
    `observation_key` and a `span` of `TextSpan | None`, and nothing else is read.
    """
    observation = current_observation(conn, item.observation_key)
    location = observation.location
    address = span_address(location)  # refuses a region (C3) and a time span
    text_span = location.text_span
    if item.span != text_span:
        raise UnresolvableSpan(
            f"the request addresses {item.span!r} and key "
            f"{item.observation_key!r} carries {text_span!r}. SPEC §4 has the gate "
            "resolve the excerpt from local storage, so a caller's coordinates are a "
            "claim; a claim that disagrees with the record is refused, not honoured "
            "and not silently replaced")
    if text_span is None:
        value, unit_length = observation.raw_value, None
    else:
        unit = unit_for_observation(conn, observation)
        if unit is None:
            raise UnresolvableSpan(
                f"{address} has a text span and no text unit at "
                f"{location.container_path!r} in run {observation.run_id!r}; there is "
                "nothing to take a substring of and the whole file is not a fallback")
        try:
            check_span_anchor(observation, unit)
        except SpanAnchorError as error:
            raise UnresolvableSpan(
                f"{address} does not anchor in run {observation.run_id!r}: {error}. "
                "P4's checker raises and never returns a repair, and a gate that "
                "repaired would release text nobody addressed"
            ) from error
        value, unit_length = raw_value_at(unit, text_span), unit.length
    return Materialised(
        observation_key=item.observation_key, span=address, value=value,
        zone=location.zone, context_before=observation.context_before,
        context_after=observation.context_after,
        context_truncated=observation.context_truncated, unit_length=unit_length)
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_resolve.py -v`
Expected: PASS — 28 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–9 green, and P1–P5's 1302 tests still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/resolve.py tests/p7/test_p7_resolve.py
git commit -m "feat(P7): the one materialisation locus - key to current row to text, two resolvers and no fallback"
```

---

---

### Task 10: The consent-aware audit record, and the ordering guarantee

**Files:**
- Create: `src/privacy/audit.py`
- Test: `tests/p7/test_p7_audit.py`

**Interfaces:**
- Consumes: `database_agent.events.append_event(conn, **fields) -> int`, `.EVENT_FIELDS`,
  `.CORRECTION_FIELDS`, `.MalformedEvent`, `evidence_shape.canonical.canonical_json(value) -> str`,
  `privacy.authorship.SUBSYSTEM`, `.MODEL_RELEASE`, `.MODEL_RELEASE_DENIED`, `.CONSENT_REQUESTED`,
  `.event_defaults(*, event_type, **fields) -> dict[str, object]`,
  `privacy.vocabulary.AUDIT_OUTCOMES`.
- Produces (`audit.py`):
  - `AUDIT_FIELDS: tuple[str, ...]` — SPEC §7's **nineteen**, in §7's order.
  - `CARRIED_FIELDS: tuple[str, str, str]` = `("user_id", "consent_request_id",
    "redaction_manifest")` — three names §7 does not list as fields, each with a reason.
  - `COLUMN_FIELDS: tuple[str, ...]` — the five with an `events` column.
  - `EXPLANATION_FIELDS: tuple[str, ...]` — the sixteen with none.
  - `OUTCOME_EVENT_TYPES: Mapping[str, str]` — outcome → P7 event name.
  - `AuditRecord` — frozen, twenty-two fields (`AUDIT_FIELDS + CARRIED_FIELDS`, the three carried
    defaulting to `None` / `()`).
  - `MalformedAudit`.
  - `append_audit(conn, record, *, author, component_version, extra=None) -> int`.
  - `audit_record(conn, audit_id) -> AuditRecord`.
  - `audit_extra(conn, audit_id) -> dict[str, object]`.
  - `audit_records_for(conn, *, file_id=None, release_id=None, consent_request_id=None)
    -> list[AuditRecord]`.

**Done-means:** 4, and the record half of 6, 7, 8.

**The nineteen, resolved name by name — this is the largest shape decision in the section.** SPEC §7
lists six required fields and a *"carried additionally"* block, and the skeleton fixes the total at
nineteen. Reading §7 literally gives sixteen, so three of §8.2's own event columns complete it, and
one §7 name is respelled. Both moves are recorded here rather than absorbed:

```text
§8.4's six          authorizing_policy · file_sensitivity · excerpts_included ·
                    redaction_applied · model · prompt_fingerprint
§7's carried        audit_id · release_id · observed_at · stage · file_ids · group_id ·
                    content_hashes · operation_mode · policy_version · plan_version · outcome
§8.2's per-file     file_id · content_hash
```

- **`appended_at` is spelled `observed_at`.** §7 annotates it *"§8.2 'time of observation'"*, and
  §8.2's time of observation is P1's `events.observed_at` column. A second name for one column is
  exactly the three-spellings defect this plan already records for `sensitivity`; there is one name
  and it is P1's.
- **`policy_version` is a field beside `authorizing_policy`.** §8.8 requires audit records to carry
  enough to *"reproduce the policy in force at each call"*, and `policy_version` is Task 12's third
  binding term. The sibling section reads it off the record by that name.
- **`file_ids` / `group_id` stay two fields, not one `target`.** §7 writes them on one line; the
  sibling section's fixtures already name them separately, and one composite field would break a
  written neighbour to gain nothing.
- **`file_id` and `content_hash` are the singular §8.2 columns and are not duplicates of the
  plurals.** §8.2's event record is per file — *"the event type, file ID, content hash"* — so a
  single-file request fills both, and a group request fills the plurals and leaves the singulars
  `NULL`. Without them `audit_records_for(file_id=...)` would have to search a JSON array, and §8.2's
  own log would not be per-file.

**Three carried fields, and why each is outside the nineteen.** `CARRIED_FIELDS` exists so that
`AUDIT_FIELDS == §7` stays a testable identity while the record still holds what neighbouring tasks
need. `user_id` is §8.2's *"user identity when there is an explicit user action"* and has an `events`
column; a model release has no live user, so it is normally `None` and is filled on a
`consent_requested` a person triggered. `consent_request_id` is **added by Task 14** — P13's
`subject_ref` is one and `NeedsConsent` as published carries no id — and Done-means 7's *"a
`consent_requested` event and no `model_release` for that request"* has no join key without it.
`redaction_manifest` is §7's *"plus the `redaction_manifest`"* clause: §7 folds it into
`excerpts_included`, but `excerpts_included` is read elsewhere as pairs, so the manifest travels
beside them as its mapping form. All three are reported.

**One events row, and canonical JSON in `explanation`.** P1's `append_event` accepts seventeen named
columns and `MalformedEvent`s an eighteenth; MINOR 1 fixes §8.2's list at eleven forever; B5 settles
that there is **one log**. The only shape that satisfies all three: five fields land in their
columns, the other sixteen land in `explanation` as canonical JSON — §8.2's own *"structured
explanation or evidence reference"* slot, the same device P5's Task 16 used, and queryable through
`json_extract`. **P7 adds no column to `events` and does not ask P1 to.**

**The ordering guarantee is structural, not a discipline.** `append_event` returns
`cursor.lastrowid` and the row exists at that moment, so `audit_id` **cannot be produced before the
record exists**. SPEC §6: *"the audit record is appended … before `Released` is returned"*; there is
no interval in which content is releasable and unaudited, because the only source of an `audit_id`
is a completed append. The test asserts it from both sides: the returned id is immediately
`SELECT`-able, and it equals the `event_id` of the row.

**`excerpts_included` is what left the device, and it is not a copy of it.** SPEC §7: *"a record
that cannot reconstruct the released payload from local storage fails §8.4's stated purpose."* The
field holds `(observation_key, span)` pairs where `span` is P4's canonical locator, and the test
proves the reconstruction by **re-running `resolve.materialise` from the stored pairs** and comparing
against what was released. That is why Task 9's `span` is a locator and not an opaque offset.

**`extra` is one keyword, owned here, and it is what makes a denial legible.** SPEC §7 enumerates a
**release** record: a denial's `reason` and `remedy_options[]`, and a consent request's `requirement`
and `options`, have no field in it, while §8.6 requires the product show *"what has been deferred,
and why"*. `append_audit(..., extra=...)` merges a mapping into the **same** canonical-JSON
`explanation` — §8.2's own *"structured explanation or evidence reference"* slot — and refuses a key
that collides with one of the sixteen, so the nineteen stay the nineteen. `audit_extra` reads the
surplus back. Tasks 13 and 14 use it; this task owns it, which is what the sibling section's table
already assigns.

**Every model call, including local ones.** §8.4 says *"Every model call should be recorded in a
consent-aware audit record"* and names no exemption; Open question 6 asks whether a local call is
also a *consent* event, and that stays open. Denials and consent requests are appended too, on §8.2's
*"Every significant event affecting a file"* and §8.6's requirement that the UI show *"what has been
deferred, and why"*.

**`author` is checked, not trusted.** M8 gives authorship to the acting part, and Task 1's
`event_defaults` refuses a caller-supplied `subsystem`. `append_audit` keeps the published `author`
keyword and rejects anything but `SUBSYSTEM`, so `privacy` still writes `"P7"` in exactly one place.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_audit.py
"""§8.4's consent-aware audit record, as one events row plus canonical JSON.

The two properties that matter: the field list IS SPEC §7's, name for name, so a
dropped field is a red test rather than a quiet omission; and the record can
reconstruct what left the device, proved by re-running the resolver over the stored
pairs rather than by asserting that a string was kept.
"""
import dataclasses
import json

import pytest

from database_agent.events import EVENT_FIELDS, MalformedEvent, append_event
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.locator import parse_locator, serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run, record_text_unit
from evidence_shape.text_units import TextUnit

from privacy.audit import (
    AUDIT_FIELDS, CARRIED_FIELDS, COLUMN_FIELDS, EXPLANATION_FIELDS,
    OUTCOME_EVENT_TYPES, AuditRecord, MalformedAudit, append_audit, audit_extra,
    audit_record, audit_records_for,
)
from privacy.authorship import (
    CONSENT_REQUESTED, MODEL_RELEASE, MODEL_RELEASE_DENIED, SUBSYSTEM,
)
from privacy.resolve import materialise
from privacy.vocabulary import AUDIT_OUTCOMES

COMPONENT = "0.1.0"
FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
CONTENT_HASH = "a" * 64
PAGE = (Segment(kind="page", index=2),)
BODY = "Passport number 992-33-1188 issued 2019."
LOCATION = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
SPAN = serialize_locator(LOCATION)
KEY = observation_key(content_hash=CONTENT_HASH, extractor_name="pdf_text",
                      locator=SPAN, raw_value="992-33-1188")
CLOUD = {"locality": "cloud", "model_id": "acme-large", "provider": "Acme"}
LOCAL = {"locality": "local", "model_id": "llama-local", "provider": "self-hosted"}


def a_record(**over) -> AuditRecord:
    base = dict(
        authorizing_policy="policy-1", file_sensitivity="sensitive_personal",
        excerpts_included=((KEY, SPAN),), redaction_applied=True, model=CLOUD,
        prompt_fingerprint="fp-1", audit_id=None, release_id="release-1",
        observed_at=FIXED_CLOCK, stage="grouping", file_ids=("file-1",),
        group_id=None, content_hashes=(CONTENT_HASH,), operation_mode="cloud_assisted",
        policy_version="policy-1", plan_version="plan-1", outcome="released",
        file_id="file-1", content_hash=CONTENT_HASH)
    base.update(over)
    return AuditRecord(**base)


def go(conn, **over) -> int:
    return append_audit(conn, a_record(**over), author=SUBSYSTEM,
                        component_version=COMPONENT)


class Item:
    """Task 7's item shape, as Task 9 reads it."""

    def __init__(self, observation_key, span):
        self.observation_key = observation_key
        self.span = span


@pytest.fixture()
def excerpt(p7_conn):
    """A real observation, so the reconstruction test resolves against real storage."""
    create_evidence_schema(p7_conn)
    record_run(p7_conn, ExtractionRun(
        run_id="run-1", file_id="file-1", content_hash=CONTENT_HASH,
        extractor_name="pdf_text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=FIXED_CLOCK, observation_count=1))
    record_text_unit(p7_conn, TextUnit(run_id="run-1", container_path=PAGE, text=BODY))
    record_observation(p7_conn, Observation(
        file_id="file-1", content_hash=CONTENT_HASH, extractor_name="pdf_text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value="992-33-1188", location=LOCATION, occurrence_count=1,
        observed_at=FIXED_CLOCK, reliability="direct", run_id="run-1",
        context_before="Passport number ", context_after=" issued 2019.",
        context_truncated=False))
    return p7_conn


# --- SPEC §7's field list ------------------------------------------------------

def test_audit_fields_are_spec_7s_nineteen_name_for_name():
    # §8.4's six required, then §7's carried block, then §8.2's two per-file columns.
    assert AUDIT_FIELDS == (
        "authorizing_policy", "file_sensitivity", "excerpts_included",
        "redaction_applied", "model", "prompt_fingerprint",
        "audit_id", "release_id", "observed_at", "stage", "file_ids", "group_id",
        "content_hashes", "operation_mode", "policy_version", "plan_version",
        "outcome", "file_id", "content_hash")
    assert len(AUDIT_FIELDS) == 19


def test_the_six_84_requires_are_all_present():
    # "what policy authorized the call, whether the file was sensitive, which
    # excerpts were included, whether values were redacted, which model received the
    # data, and the prompt fingerprint."
    assert set(AUDIT_FIELDS[:6]) == {
        "authorizing_policy", "file_sensitivity", "excerpts_included",
        "redaction_applied", "model", "prompt_fingerprint"}


def test_the_three_carried_fields_are_outside_the_nineteen():
    assert CARRIED_FIELDS == ("user_id", "consent_request_id", "redaction_manifest")
    assert not set(CARRIED_FIELDS) & set(AUDIT_FIELDS)


def test_the_record_is_exactly_the_nineteen_plus_the_three():
    names = tuple(field.name for field in dataclasses.fields(AuditRecord))
    assert names == AUDIT_FIELDS + CARRIED_FIELDS


def test_the_split_between_column_and_explanation_is_total_and_disjoint():
    assert COLUMN_FIELDS == ("file_id", "content_hash", "prompt_fingerprint",
                             "observed_at", "user_id")
    assert set(COLUMN_FIELDS) <= set(EVENT_FIELDS), (
        "P7 adds no column to `events` and does not ask P1 to")
    assert not set(COLUMN_FIELDS) & set(EXPLANATION_FIELDS)
    assert set(COLUMN_FIELDS) | set(EXPLANATION_FIELDS) | {"audit_id"} == set(
        AUDIT_FIELDS + CARRIED_FIELDS)
    assert len(EXPLANATION_FIELDS) == 16


def test_the_record_is_frozen(p7_conn):
    with pytest.raises(dataclasses.FrozenInstanceError):
        a_record().outcome = "denied"


# --- one events row, and the JSON explanation ----------------------------------

def test_the_five_column_fields_land_in_their_columns(p7_conn):
    audit_id = go(p7_conn)
    row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["file_id"] == "file-1"
    assert row["content_hash"] == CONTENT_HASH
    assert row["prompt_fingerprint"] == "fp-1"
    assert row["observed_at"] == FIXED_CLOCK
    assert row["user_id"] is None


def test_the_rest_land_in_explanation_as_canonical_json(p7_conn):
    audit_id = go(p7_conn)
    row = p7_conn.execute("SELECT explanation FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    payload = json.loads(row["explanation"])
    assert set(payload) == set(EXPLANATION_FIELDS)
    assert payload["authorizing_policy"] == "policy-1"
    assert payload["model"] == CLOUD
    # canonical: sorted keys, so two identical records serialise identically.
    assert row["explanation"] == json.dumps(payload, sort_keys=True,
                                            separators=(",", ":"), ensure_ascii=False)


def test_p7_authors_and_p1_writes(p7_conn):
    audit_id = go(p7_conn)
    row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["subsystem"] == "P7"
    assert row["component_version"] == COMPONENT


def test_a_foreign_author_is_refused(p7_conn):
    # M8: the acting part authors. `privacy` writes "P7" in exactly one place and
    # this entry point is not a second one.
    with pytest.raises(MalformedAudit):
        append_audit(p7_conn, a_record(), author="P8", component_version=COMPONENT)


def test_p1_would_reject_an_eighteenth_column(p7_conn):
    # The constraint the JSON shape exists to satisfy, asserted against P1 rather
    # than quoted: none of §7's own field names is a column.
    with pytest.raises(MalformedEvent):
        append_event(p7_conn, event_type=MODEL_RELEASE, subsystem="P7",
                     component_version=COMPONENT, observed_at=FIXED_CLOCK,
                     explanation="{}", release_id="release-1")


# --- the round trip ------------------------------------------------------------

def test_the_record_round_trips(p7_conn):
    audit_id = go(p7_conn)
    assert audit_record(p7_conn, audit_id) == a_record(audit_id=audit_id)


def test_tuples_come_back_as_tuples(p7_conn):
    # JSON has one sequence type; the record has frozen fields that get compared.
    recovered = audit_record(p7_conn, go(p7_conn))
    assert recovered.excerpts_included == ((KEY, SPAN),)
    assert recovered.content_hashes == (CONTENT_HASH,)
    assert recovered.file_ids == ("file-1",)


def test_an_unknown_audit_id_raises(p7_conn):
    with pytest.raises(KeyError):
        audit_record(p7_conn, 999999)


# --- the ordering guarantee ----------------------------------------------------

def test_the_returned_id_is_already_selectable(p7_conn):
    # SPEC §6: "the audit record is appended ... BEFORE `Released` is returned."
    # `append_event` returns `cursor.lastrowid`, so an `audit_id` cannot exist
    # before its row does. There is no interval in which content is releasable and
    # unaudited, and the property is structural rather than a discipline.
    audit_id = go(p7_conn)
    (count,) = p7_conn.execute("SELECT count(*) FROM events WHERE event_id = ?",
                               (audit_id,)).fetchone()
    assert count == 1


def test_the_returned_id_is_the_rows_event_id(p7_conn):
    audit_id = go(p7_conn)
    row = p7_conn.execute("SELECT event_id FROM events ORDER BY event_id DESC "
                          "LIMIT 1").fetchone()
    assert row["event_id"] == audit_id


def test_audit_ids_are_monotonic(p7_conn):
    first, second = go(p7_conn), go(p7_conn, release_id="release-2")
    assert second > first


# --- outcomes, and what each one appends ---------------------------------------

def test_each_outcome_maps_to_its_own_p7_event_type(p7_conn):
    assert OUTCOME_EVENT_TYPES == {
        "released": MODEL_RELEASE,
        "denied": MODEL_RELEASE_DENIED,
        "consent_requested": CONSENT_REQUESTED}
    assert tuple(OUTCOME_EVENT_TYPES) == AUDIT_OUTCOMES


def test_a_denial_is_recorded_too(p7_conn):
    # §8.2: "Every significant event affecting a file"; §8.6: the UI must show "what
    # has been deferred, and why".
    audit_id = go(p7_conn, outcome="denied", release_id=None)
    row = p7_conn.execute("SELECT event_type FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["event_type"] == MODEL_RELEASE_DENIED


def test_a_consent_request_is_recorded_with_its_id(p7_conn):
    # Done-means 7's join key. Task 14 adds the field; the record carries it.
    audit_id = go(p7_conn, outcome="consent_requested", release_id=None,
                  consent_request_id="consent-1", user_id="joseph")
    row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["event_type"] == CONSENT_REQUESTED
    assert row["user_id"] == "joseph"
    assert json.loads(row["explanation"])["consent_request_id"] == "consent-1"


def test_a_local_model_call_is_audited(p7_conn):
    # §8.4: "Every model call should be recorded" -- no exemption is named, and
    # Open question 6 (is a local call also a CONSENT event?) stays open.
    audit_id = go(p7_conn, model=LOCAL, operation_mode="local_model")
    assert audit_record(p7_conn, audit_id).model == LOCAL


def test_an_outcome_outside_the_vocabulary_is_refused(p7_conn):
    with pytest.raises(MalformedAudit):
        go(p7_conn, outcome="probably_fine")


def test_an_empty_stage_is_refused(p7_conn):
    # §8.5 requires per-stage decomposition; an unattributed call cannot be
    # decomposed later.
    with pytest.raises(MalformedAudit):
        go(p7_conn, stage="")


# --- the readers ---------------------------------------------------------------

def test_records_are_found_by_file_by_release_and_by_consent_request(p7_conn):
    first = go(p7_conn)
    second = go(p7_conn, release_id="release-2", file_id="file-2",
                file_ids=("file-2",))
    third = go(p7_conn, outcome="consent_requested", release_id=None,
               consent_request_id="consent-1")
    assert [r.audit_id for r in audit_records_for(p7_conn, file_id="file-1")] == [
        first, third]
    assert [r.audit_id for r in audit_records_for(p7_conn, release_id="release-2")] == [
        second]
    assert [r.audit_id for r in
            audit_records_for(p7_conn, consent_request_id="consent-1")] == [third]


def test_the_readers_return_records_in_append_order(p7_conn):
    ids = [go(p7_conn), go(p7_conn, release_id="release-2"),
           go(p7_conn, release_id="release-3")]
    assert [r.audit_id for r in audit_records_for(p7_conn, file_id="file-1")] == ids


def test_the_readers_see_only_p7s_three_event_types(p7_conn):
    # The log is shared (B5). A `discovery` event on the same file is not an audit
    # record and must not appear in one.
    go(p7_conn)
    append_event(p7_conn, event_type="discovery", subsystem="P3",
                 component_version="0.1.0", observed_at=FIXED_CLOCK,
                 explanation="a scan saw it", file_id="file-1")
    assert len(audit_records_for(p7_conn, file_id="file-1")) == 1


def test_no_filter_at_all_is_refused(p7_conn):
    # Returning the whole log for a call that named nothing is how a "show me the
    # releases for this file" screen quietly becomes "show me every release".
    go(p7_conn)
    with pytest.raises(MalformedAudit):
        audit_records_for(p7_conn)


def test_extra_carries_what_spec_7_has_no_field_for(p7_conn):
    # §8.6: the product must show "what has been deferred, and why". A denial's
    # reason has no §7 field, and Tasks 13 and 14 write theirs through here.
    audit_id = append_audit(
        p7_conn, a_record(outcome="denied", release_id=None), author=SUBSYSTEM,
        component_version=COMPONENT,
        extra={"reason": "unclassified", "remedy_options": ["classify and retry"]})
    assert audit_extra(p7_conn, audit_id) == {
        "reason": "unclassified", "remedy_options": ["classify and retry"]}
    # and the nineteen are untouched by it
    assert audit_record(p7_conn, audit_id).outcome == "denied"


def test_extra_may_not_shadow_a_spec_7_field(p7_conn):
    # A second value under one name is how a record starts disagreeing with itself,
    # in a log nothing may ever update.
    with pytest.raises(MalformedAudit):
        append_audit(p7_conn, a_record(), author=SUBSYSTEM,
                     component_version=COMPONENT,
                     extra={"outcome": "not really released"})


# --- what left the device ------------------------------------------------------

def test_excerpts_included_holds_pairs_and_not_a_second_copy_of_the_text(excerpt):
    audit_id = go(excerpt)
    payload = json.loads(excerpt.execute(
        "SELECT explanation FROM events WHERE event_id = ?",
        (audit_id,)).fetchone()["explanation"])
    assert payload["excerpts_included"] == [[KEY, SPAN]]
    assert "992-33-1188" not in json.dumps(payload)
    assert BODY not in json.dumps(payload)


def test_the_stored_pairs_reconstruct_what_left_the_device(excerpt):
    # SPEC §7: "a record that cannot reconstruct the released payload from local
    # storage fails §8.4's stated purpose." Proved by re-running the resolver over
    # the stored pairs, which is why Task 9's `span` is P4's canonical locator and
    # not an opaque offset.
    recovered = audit_record(excerpt, go(excerpt))
    for key, span in recovered.excerpts_included:
        again = materialise(excerpt, Item(key, parse_locator(span).text_span))
        assert again.value == "992-33-1188"
        assert again.span == span
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_audit.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.audit'`. Collection fails on the
import line; no test runs.

- [ ] **Step 3: Write `src/privacy/audit.py`**

```python
# src/privacy/audit.py
"""§8.4's consent-aware audit record, as ONE `events` row plus canonical JSON.

§8.4: "Every model call should be recorded in a consent-aware audit record. The record
should show what policy authorized the call, whether the file was sensitive, which
excerpts were included, whether values were redacted, which model received the data,
and the prompt fingerprint."

Three constraints meet here and are jointly satisfiable exactly one way. P1's
`append_event` accepts seventeen named columns and rejects an eighteenth; MINOR 1 fixes
§8.2's list at eleven forever; B5 settles that there is ONE log -- "§8.4's consent-aware
record is that log with the consent fields". So five fields land in their columns and
the other sixteen land in `explanation`, which is §8.2's own "structured explanation or
evidence reference" slot. P7 adds no column to `events` and does not ask P1 to.

Two properties this module exists to make structural rather than procedural:

- **`audit_id` cannot exist before the record does.** It IS the `event_id` P1 returns
  from a completed insert, so SPEC §6's "the audit record is appended ... before
  `Released` is returned" is not a discipline anyone can forget.
- **The record says what left the device without holding a copy of it.**
  `excerpts_included` is `(observation_key, span)` pairs, where `span` is P4's canonical
  locator; re-running `resolve.materialise` over them reproduces the payload exactly.
  §8.4 puts "raw sensitive values" in the always-local set, and the text already exists
  once.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from database_agent.events import EVENT_FIELDS, append_event
from evidence_shape.canonical import canonical_json

from privacy.authorship import (
    CONSENT_REQUESTED, MODEL_RELEASE, MODEL_RELEASE_DENIED, SUBSYSTEM, event_defaults,
)
from privacy.vocabulary import AUDIT_OUTCOMES

#: SPEC §7's nineteen, in §7's order: §8.4's six required, §7's carried block, then
#: §8.2's two per-file columns. `appended_at` is spelled `observed_at` because §7
#: annotates it '§8.2 "time of observation"' and that is P1's column; one thing has
#: one name.
AUDIT_FIELDS: tuple[str, ...] = (
    "authorizing_policy", "file_sensitivity", "excerpts_included",
    "redaction_applied", "model", "prompt_fingerprint",
    "audit_id", "release_id", "observed_at", "stage", "file_ids", "group_id",
    "content_hashes", "operation_mode", "policy_version", "plan_version", "outcome",
    "file_id", "content_hash",
)

#: Three names SPEC §7 does not list as fields, kept outside the nineteen so
#: `AUDIT_FIELDS == §7` stays a testable identity. Each is reported in the plan.
CARRIED_FIELDS: tuple[str, str, str] = (
    "user_id", "consent_request_id", "redaction_manifest",
)

#: The five with an `events` column. Everything else has none.
COLUMN_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "prompt_fingerprint", "observed_at", "user_id",
)

#: The sixteen that travel as canonical JSON. `audit_id` is in neither list: it is the
#: row's identity, assigned by the insert and read back off `event_id`.
EXPLANATION_FIELDS: tuple[str, ...] = tuple(
    name for name in AUDIT_FIELDS + CARRIED_FIELDS
    if name not in COLUMN_FIELDS and name != "audit_id"
)

#: outcome -> the P7 event type that records it. `model_release` and its consent-aware
#: record are the same event (B5).
OUTCOME_EVENT_TYPES: Mapping[str, str] = MappingProxyType({
    "released": MODEL_RELEASE,
    "denied": MODEL_RELEASE_DENIED,
    "consent_requested": CONSENT_REQUESTED,
})

_TUPLE_FIELDS = ("excerpts_included", "file_ids", "content_hashes",
                 "redaction_manifest")
_PAIR_FIELDS = ("excerpts_included",)


class MalformedAudit(Exception):
    """Shape check at the writer. An append-only row cannot be repaired later."""


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """SPEC §7's nineteen, plus three carried names §7 does not list as fields."""

    authorizing_policy: str
    file_sensitivity: str
    excerpts_included: tuple[tuple[str, str], ...]
    redaction_applied: bool
    model: Mapping[str, str]
    prompt_fingerprint: str
    audit_id: int | None
    release_id: str | None
    observed_at: str
    stage: str
    file_ids: tuple[str, ...]
    group_id: str | None
    content_hashes: tuple[str, ...]
    operation_mode: str
    policy_version: str
    plan_version: str
    outcome: str
    file_id: str | None
    content_hash: str | None
    user_id: str | None = None
    consent_request_id: str | None = None
    redaction_manifest: tuple[Mapping[str, object], ...] = ()


def _check(record: AuditRecord, author: str) -> None:
    if author != SUBSYSTEM:
        raise MalformedAudit(
            f"author {author!r} is not {SUBSYSTEM!r}. M8 gives authorship to the "
            "acting part, and `privacy` writes its subsystem name in one place")
    if record.outcome not in AUDIT_OUTCOMES:
        raise MalformedAudit(
            f"outcome {record.outcome!r} is not one of {AUDIT_OUTCOMES}; a value "
            "outside a closed vocabulary is a load error, not a fallback")
    for name in ("stage", "authorizing_policy", "operation_mode", "policy_version",
                 "plan_version", "file_sensitivity", "prompt_fingerprint",
                 "observed_at"):
        if not getattr(record, name):
            raise MalformedAudit(
                f"{name} is required on every audit record; §8.5 decomposes replay "
                "by stage and §8.8 reproduces the policy in force at each call, and "
                "neither is possible from a record that omitted one")
    if not record.model:
        raise MalformedAudit(
            "§8.4 requires the record show which model received the data")


def append_audit(conn: sqlite3.Connection, record: AuditRecord, *, author: str,
                 component_version: str,
                 extra: Mapping[str, object] | None = None) -> int:
    """Append one audit record and return its `audit_id`.

    The id is P1's `event_id`, produced by the insert, so it cannot be handed to a
    caller before the row exists. That is SPEC §6's ordering guarantee, structurally.

    `extra` merges into the same `explanation` object. SPEC §7 enumerates a RELEASE
    record; a denial's reason and a consent request's four options have no field in
    it, and §8.6 requires the product show "what has been deferred, and why". A key
    that collides with one of the sixteen is refused, so the nineteen stay the
    nineteen.
    """
    _check(record, author)
    payload = {name: _jsonable(getattr(record, name)) for name in EXPLANATION_FIELDS}
    if extra:
        collisions = sorted(set(extra) & set(payload))
        if collisions:
            raise MalformedAudit(
                f"{collisions} are SPEC §7 field names; `extra` carries what §7 has "
                "no field for, and a second value under one name is how a record "
                "starts disagreeing with itself")
        payload.update({name: _jsonable(value) for name, value in extra.items()})
    explanation = canonical_json(payload)
    columns = {name: getattr(record, name) for name in COLUMN_FIELDS}
    return append_event(conn, **event_defaults(
        event_type=OUTCOME_EVENT_TYPES[record.outcome],
        component_version=component_version, explanation=explanation, **columns))


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, Mapping):
        return dict(value)
    return value


def _record_from_row(row: sqlite3.Row) -> AuditRecord:
    import json

    payload = json.loads(row["explanation"])
    values: dict[str, object] = {name: payload[name] for name in EXPLANATION_FIELDS}
    values.update({name: row[name] for name in COLUMN_FIELDS})
    values["audit_id"] = row["event_id"]
    values["redaction_applied"] = bool(values["redaction_applied"])
    for name in _TUPLE_FIELDS:
        values[name] = tuple(
            tuple(item) if name in _PAIR_FIELDS else item
            for item in values[name])
    return AuditRecord(**values)


def audit_record(conn: sqlite3.Connection, audit_id: int) -> AuditRecord:
    """One record, by the id `append_audit` returned."""
    row = conn.execute("SELECT * FROM events WHERE event_id = ? AND event_type IN "
                       "(?, ?, ?)",
                       (audit_id, MODEL_RELEASE, MODEL_RELEASE_DENIED,
                        CONSENT_REQUESTED)).fetchone()
    if row is None:
        raise KeyError(f"no audit record {audit_id!r}")
    return _record_from_row(row)


def audit_extra(conn: sqlite3.Connection, audit_id: int) -> dict[str, object]:
    """The keys `append_audit`'s `extra` added, beside SPEC §7's sixteen."""
    import json

    row = conn.execute("SELECT explanation FROM events WHERE event_id = ?",
                       (audit_id,)).fetchone()
    if row is None:
        raise KeyError(f"no audit record {audit_id!r}")
    return {name: value for name, value in json.loads(row["explanation"]).items()
            if name not in EXPLANATION_FIELDS}


def audit_records_for(conn: sqlite3.Connection, *, file_id: str | None = None,
                      release_id: str | None = None,
                      consent_request_id: str | None = None) -> list[AuditRecord]:
    """Audit records matching every filter given, in append order.

    At least one filter is required. A reader that returned the whole log for a call
    that named nothing is how "the releases for this file" becomes "every release".
    """
    clauses = ["event_type IN (?, ?, ?)"]
    parameters: list[object] = [MODEL_RELEASE, MODEL_RELEASE_DENIED, CONSENT_REQUESTED]
    if file_id is not None:
        clauses.append("file_id = ?")
        parameters.append(file_id)
    for name, value in (("release_id", release_id),
                        ("consent_request_id", consent_request_id)):
        if value is not None:
            clauses.append(f"json_extract(explanation, '$.{name}') = ?")
            parameters.append(value)
    if len(clauses) == 1:
        raise MalformedAudit(
            "audit_records_for needs at least one of file_id, release_id or "
            "consent_request_id")
    rows = conn.execute(
        f"SELECT * FROM events WHERE {' AND '.join(clauses)} ORDER BY event_id",
        parameters)
    return [_record_from_row(row) for row in rows]
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_audit.py -v`
Expected: PASS — 31 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–10 green, and P1–P5's 1302 tests still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/audit.py tests/p7/test_p7_audit.py
git commit -m "feat(P7): the consent-aware audit record as one events row, and the ordering guarantee"
```

---

---

### Task 11: `Gate.release` — the request, the three-branch union, and no override parameter

> ### ⚠ CUT 4 — unratified. This task is a cut target; it is written in full anyway.
>
> `planning/overnight/reviews/round-5-scope.md` **CUT 4** recommends deleting **P7's `Gate` facade as
> a seven-method object**, on the argument that seven methods on one class is a namespace, not an
> abstraction, and that six of the seven are one-line delegations to modules that already publish the
> function. **Joseph has not ruled on it.** Of round 5's seven cuts exactly one is ratified (CUT 1,
> P6 Task 26, via D5); this is not that one.
>
> Written in full, per the authoring brief §9, because an unratified recommendation is not a decision
> and a half-written keystone is worth nothing to either outcome. **What the cut would and would not
> take:** it would take the *class*; it would not take `release`, which SPEC §6 publishes as
> `Gate.release(ModelCallRequest) -> ReleaseDecision` and which B2 makes P8's call verbatim. A build
> that adopts CUT 4 has to answer what `Gate.release` becomes — SPEC §6 names the method on an object
> — and that is a Contract-out revision, not an implementation choice. This task therefore ships
> `Gate` with **one** method and names the six that Tasks 15–18 add (see *What this task does not do*),
> which is the smallest form the published signature admits and the form a reviewer deciding CUT 4
> needs in front of them.

**Files:**
- Create: `src/privacy/release.py`, `src/privacy/gate.py`
- Test: `tests/p7/test_p7_release.py`

**Interfaces:**
- Consumes (`release.py`): `privacy.consent.NeedsConsent` (**the only `privacy` module `release.py`
  imports at run time besides `vocabulary`** — see *The import direction*),
  `privacy.vocabulary.check_denial_reason(value) -> str`, `.OutOfVocabulary`;
  under `TYPE_CHECKING` only: `privacy.resolve.Materialised`, `privacy.redaction.RedactionManifest`,
  `privacy.items.RequestedItem`, `privacy.denial.RemedyOption`.
- Consumes (`gate.py`): `privacy.release.*`; `privacy.classification.resolve_class(record) -> str`,
  `.UNREADABLE_UNCLASSIFIED`, `.ClassificationRecord`, `.completeness_implies_unclassified`;
  `privacy.classification_store.ClassificationStore`;
  `privacy.policy.Policy`, `.current_policy(conn, *, plan_version) -> Policy | None`;
  `privacy.items.Excerpt`, `.RedactedIdentifier`, `.check_item(item, *, unit_length, protected,
  sensitive_keys, allow_unratified) -> None`, `.sensitive_observation_keys(conn, file_id)
  -> frozenset[str]`, `.AlwaysLocalRequested`, `.WholeDocumentRequested`, `.kind_of(item) -> str`;
  `privacy.redaction.RedactionManifest`, `.apply_redaction(value, *, observation_key, span,
  context_before, context_after, context_truncated, classifier, transform)
  -> tuple[str, RedactionEntry]`;
  `privacy.resolve.materialise(conn, item) -> Materialised`;
  `privacy.audit.AuditRecord`, `.append_audit(conn, record, *, author, component_version,
  extra=None) -> int`;
  `privacy.authorship.SUBSYSTEM`;
  `privacy.consent.ConsentRequirement`, `.open_consent_request(conn, requirement, *, request,
  policy, content_hashes, user_id, component_version, observed_at) -> NeedsConsent`;
  `privacy.denial.DENIAL_ORDER`, `.DECIDABLE_FROM_REQUEST`, `.first_reason(reasons) -> str | None`,
  `.mode_forbids`, `.policy_revoked_for`, `.unclassified_denies`, `.is_protected_records`,
  `.protected_cloud_denies`, `.over_dossier_ceiling`, and the eight builders
  `deny_mode_forbids_target`, `deny_policy_revoked`, `deny_always_local_item`, `deny_unclassified`,
  `deny_protected_records_template`, `deny_protected_cloud_target`,
  `deny_whole_document_requested`, `deny_dossier_over_budget`, `.record_denial(conn, denied, *,
  request, policy, classification, content_hashes, user_id, component_version, observed_at) -> int`,
  `.PROTECTED_RECORDS_TEMPLATE`;
  `privacy.binding.mint_release(conn, *, policy, model_target, prompt_fingerprint, audit_id,
  minted_at) -> str`;
  `database_agent.files_table.get_file(conn, file_id) -> sqlite3.Row`,
  `database_agent.budget.get_ceiling(conn, key) -> int | None`.
- Produces (`release.py`):
  - `ModelTarget` — frozen: `locality: str`, `model_id: str`, `provider: str`; `LOCALITIES:
    tuple[str, str] = ("local", "cloud")`; `to_mapping() -> dict[str, str]`.
  - `Target` — frozen: `file_ids: tuple[str, ...]`, `group_id: str | None = None`.
  - `ModelCallRequest` — frozen; SPEC §6's **seven** exactly: `stage`, `target`, `model_target`,
    `requested_items`, `prompt_template_id`, `prompt_fingerprint`, `max_dossier_tokens`.
  - `Released` — frozen; SPEC §6's **six**: `release_id`, `audit_id`, `policy_version`,
    `materialised_items`, `redaction_manifest`, `model_target`.
  - `Denied` — frozen; **four**: `reason`, `explanation`, `remedy_options`, **`evidence_refs`**.
  - `NeedsConsent` — **re-exported** from `privacy.consent`, not redefined (Task 14 owns it).
  - `ReleaseDecision` — the union alias, `Released | Denied | NeedsConsent`.
  - `REQUEST_FIELDS`, `RELEASED_FIELDS`, `DENIED_FIELDS`, `NEEDS_CONSENT_FIELDS`,
    `DECISION_TYPES: tuple[type, ...]`, `DECISION_ORDER: tuple[str, ...]`,
    `FORBIDDEN_PARAMETER_NAMES: frozenset[str]`, `RELEASE_PARAMETERS: frozenset[str]`.
  - `MalformedRequest`, `MalformedDecision`, `NoPolicyInForce`.
- Produces (`gate.py`):
  - `TEXT_BEARING: tuple[type, ...]` — the two item kinds that resolve to local text.
  - `Gate(conn, *, store, plan_version, classifier, transform, unclassified_permits_local,
    scope_for, files_in_scope, component_version, now, user_id, measure_tokens=None,
    template_for=None)`.
  - `Gate.release(request) -> ReleaseDecision`.

**Done-means:** 3 (the gate half), and the entry point for 5, 6, 7.

---

#### Execution order — this task's two files sit on either side of Tasks 12 and 13

**Read this before scheduling the task.** The four modules of Tasks 11–14 form an acyclic *module*
graph, but the task numbering is not a valid *build* order, and neither Task 12 nor Task 13 nor
Task 14 carries a `Modify: src/privacy/release.py` line — each of the three states, in its own
"what this section leaves for its neighbours" table, that the wiring is Task 11's. Both facts are
true and together they force this task to land in two commits:

```text
consent.py   imports policy, audit, authorship, vocabulary        — needs no release
release.py   imports consent (NeedsConsent) and vocabulary        — needs consent
denial.py    imports release.Denied AT RUN TIME                   — needs release
binding.py   imports release under TYPE_CHECKING ONLY             — needs release only to type-check
gate.py      imports release, consent, denial, binding, and 2-10  — needs all four
```

**The order that builds is `… 10, 14, 11-a, 13, 12, 11-b`:**

| | What lands | Steps |
|---|---|---|
| **11-a** | `src/privacy/release.py` — nine frozen dataclasses and eight constants, no behaviour | Steps 1–2 |
| **11-b** | `src/privacy/gate.py` and `tests/p7/test_p7_release.py` | Steps 3–8 |

`release.py` carries no test of its own at 11-a, and that is deliberate rather than a gap:
`test_p7_release.py` tests **the door**, and the door is `gate.py`. Every assertion about `release.py`
is a shape assertion in that file, and in the interim Task 12's and Task 13's own tests import and
exercise the dataclasses. Splitting Task 11 into two numbered tasks instead would put
`FORBIDDEN_PARAMETER_NAMES` in one task and the signature it constrains in another, which is the one
thing the shape tests exist to keep together.

**Two consequences reported to their owners, not patched here:**

1. **Task 14 runs before Task 11-a**, and Task 14's assertion that *"the two branch types share no
   field name at all"* imports `release.Denied`. Either that one assertion moves to this file — where
   `test_the_three_branches_share_no_field_name` already makes it, over all three types rather than
   two — or Task 14 is scheduled after 11-a. **Reported to Task 14's author.**
2. **Task 20 pins `Gate.__init__`** (`GATE_ARGUMENTS`, ten keywords) and this task adopts all ten
   verbatim — `store`, `plan_version`, `classifier`, `transform`, `unclassified_permits_local`,
   `scope_for`, `files_in_scope`, `component_version`, `now`, `user_id`. It adds **two optional
   keywords Task 20's `gate_arguments` does not supply**, `measure_tokens` and `template_for`, both
   defaulting to `None`. See *Two denials the gate cannot reach without a keyword Task 20 omits*,
   below. **Reported to Task 20's author.**

---

#### The signature is adopted VERBATIM on both sides (B2), and everything else is constructor state

SPEC §6: *"`Gate.release(ModelCallRequest) -> ReleaseDecision`. **This is the only gate signature in
the product.** P8's `seal(...) -> SealedDossier | Refusal` is withdrawn; P8 adopts this call, this
return union, and these field names verbatim (B2). There is one door, named once."*

`Gate.release` therefore has **two** parameters, `self` and `request`. The connection, the
classification store, the policy scope, the two injected redaction protocols, the clock, the user
identity and the two open questions that need a value all live on `Gate.__init__`. That is not a
workaround for a cramped signature; it is what *"one door, named once"* costs, and it is what lets
the whitelist test be an **equality** rather than a subset.

**There is no override parameter, and the test proves it two ways.**

- **The whitelist** — `set(inspect.signature(Gate.release).parameters) == {"self", "request"}` —
  proves no unpublished parameter exists **at all**. This is the stronger half: a blacklist can only
  catch the words someone thought of.
- **The blacklist** — `FORBIDDEN_PARAMETER_NAMES` — names the specific words a future convenience
  would reach for, and asserts they appear in neither the signature, nor `Gate.__init__`, nor any
  field of the request, nor any field of any of the three branch types.

**Both are parsed from `inspect.signature` and `dataclasses.fields`, never from source text.** A
source scan matches comments and docstrings, and that technique has produced a false result eight
times on this project; the established mechanism where a token assertion is unavoidable is
`code_tokens()` in `tests/p3/test_p3_no_invention.py`, which walks the AST. This is P5's
`SafetyPolicy` discipline applied to the gate: *"Two fields, and deliberately no third."*

The blacklist is compared **token-wise**, on `name.split("_")`, not by substring. Substring matching
would fail `unclassified_permits_local` against a blacklisted `permit` and would tempt the next
author to rename a legitimate parameter to appease a test. Token-wise, every published name here is
clean: `{conn, store, plan, version, classifier, transform, unclassified, permits, local, scope,
for, files, in, component, now, user, id, measure, tokens, template, release, request, stage,
target, model, requested, items, prompt, fingerprint, max, dossier, audit, policy, materialised,
redaction, manifest, reason, explanation, remedy, options, evidence, refs, consent, requirement}`.

**Three constructor parameters carry no default, and each one is an open question refusing to be
guessed.** `classifier` and `transform` are SPEC *Deferred*'s row for identifier classes: *"Which
identifier classes exist and how each is transformed is not enumerated anywhere in the design."*
`scope_for` is Open question 3 — *"What is a 'corpus area'? … Consent grants cannot be scoped until
this is named"* — so the caller maps a `file_id` to an opaque scope string and P7 resolves none.
`unclassified_permits_local` is Open question 5 — *"Does `unreadable_unclassified` permit a local
model call?"* — and it reaches `denial.unclassified_denies`, whose own docstring records that P7
names no winner.

---

#### `Denied` has FOUR fields, and the fourth is `evidence_refs`

The skeleton's Task 11 `Produces` lists three. That is a defect in the skeleton and it is corrected
here, on three independent grounds that all point the same way:

1. **SPEC §6 requires it.** `Denied.explanation` is *"user-facing, evidence-referenced"*. A field
   that references evidence and a record that cannot carry the references are not the same thing.
2. **Task 13's own constructor takes it.** The skeleton spells
   `deny(reason, *, explanation, remedy_options, evidence_refs) -> Denied`, and the written Task 13
   implements exactly that signature. *A constructor that accepts a value the dataclass cannot hold
   is not writable* — Task 13's author raised this and it is honoured, not renegotiated.
3. **The one denial that has evidence to cite would silently drop it.**
   `deny_protected_cloud_target(*, file_ids, operation_mode, scope, evidence_refs=())` passes the
   classification's own refs through. SPEC §2 makes `evidence_refs` non-empty for any
   `basis = detector` classification, and §3.1's principle is that every fact preserves where it came
   from. A denial that says *"this file is protected"* and cannot say *on what evidence* has thrown
   away the half of §8.4 that makes the classification *"evidence-backed"*.

`evidence_refs` is `tuple[str, ...]` of P4 **`observation_key`** values, never `observation_id`
(M14, and SPEC *Correction learning*: *"The key, not the id, is what makes that durable"*). It
defaults to `()` because six of the eight denials are decided from the request and the policy and
have no evidence to cite — `deny_mode_forbids_target` passes `evidence_refs=()` explicitly, and an
empty tuple there is honest rather than lazy.

---

#### The import direction — fixed by Tasks 12–14, adopted here without renegotiation

The rule, quoted from the written Tasks 12–14 section, which says in its own words that this is
*"the one constraint these three tasks place on"* Task 11:

```text
release.py    ModelCallRequest · ModelTarget · Target · Released · Denied · ReleaseDecision
              imports privacy.consent for NeedsConsent, and no other privacy module
consent.py    NeedsConsent · ConsentRequirement       imports policy, audit, authorship, vocabulary
binding.py    the ledger                              imports release under TYPE_CHECKING ONLY
denial.py     the eight denials                       imports release.Denied at run time
gate.py       the Gate facade                         imports all four; holds the decision logic
```

Adopted. Three notes on how it is applied, each stated rather than done quietly:

- **`vocabulary` is the one addition, and it cannot create a cycle.** `Denied.__post_init__` calls
  `check_denial_reason`, so a hand-constructed `Denied("looks_fine", …)` is refused at construction
  and not only inside `denial.deny`. `privacy.vocabulary` is a **leaf**: Task 2's `Consumes` names
  no `privacy` module at all, and imports `scan_agent.exclusion` *in the test only*. `release` →
  `vocabulary` therefore cannot close any loop, and `denial.py` imports it too. The rule's purpose —
  `release.py` sits **below** `denial` and `binding` so they may import it — is preserved exactly.
- **`resolve`, `redaction`, `items` and `denial` are imported under `TYPE_CHECKING` only.**
  `Released.materialised_items` is `tuple[Materialised, ...]`, `Released.redaction_manifest` is a
  `RedactionManifest`, `ModelCallRequest.requested_items` is `tuple[RequestedItem, ...]`, and
  `Denied.remedy_options` is `tuple[RemedyOption, ...]`. Precise annotations with no run-time edge is
  exactly the device Task 12 sanctioned for `binding`, and `from __future__ import annotations` makes
  it work. The `denial` edge is a TYPE_CHECKING cycle — `denial` imports `release` at run time,
  `release` imports `denial` at type-check time — which type checkers resolve and the interpreter
  never sees. The **field name** `remedy_options` is fixed here; the **element type** is Task 13's.
- **`NeedsConsent` is not redefined here.** It is imported from `privacy.consent` and re-exported, so
  that `ReleaseDecision = Released | Denied | NeedsConsent` reads as one union in one module — the
  File Structure gives `release.py` *"Gate.release — the request, the three branches, the ordering"* —
  while Task 14 keeps the dataclass, its `consent_request_id`, its four-option invariant and its
  whole lifecycle. **One dataclass, one home, one import.** The skeleton lists `NeedsConsent` under
  both Task 11's and Task 14's `Produces`; this is that collision resolved, and the resolution is the
  one a sibling already wrote its task against.

---

#### `DECISION_ORDER` — published, because the order is the contract

```text
1  collect_request_denials   the six in DENIAL_ORDER decidable from request + policy + a row
2  needs_consent             a question only the user can answer — asked only if nothing denied
3  materialise               the ONLY content read, and the first step that touches text
4  collect_content_denials   whole_document_requested, dossier_over_budget
5  append_audit              §8.4: recording the authorization is part of granting it
6  mint_release              Task 12's ledger; the token exists only after the record does
```

It is published as a tuple so a reviewer can read the order without reading the function, and so a
reordering is a diff on a constant rather than an invisible behaviour change.

**The order is forced, not chosen, and Task 13's `DECIDABLE_FROM_REQUEST` is the proof obligation in
data form.** Its principle: *no denial that can be decided from the request alone may be decided
after one that requires reading the file.* A gate that materialised an excerpt and **then**
discovered the mode forbade the call has read a sensitive file for a call that was never going to
happen. `test_no_content_is_read_before_every_request_decidable_check_has_run` asserts it directly,
by handing the gate a `materialise` that fails the test if it is called at all.

**Within step 1 the gate does not re-decide precedence — it collects and delegates.** Four of the
eight reasons overlap on real inputs (a protected unclassified file under `offline` with a cloud
target satisfies three at once), so the gate gathers every triggered reason into a set and asks
`denial.first_reason(reasons)` which one wins. `DENIAL_ORDER` lives in `denial.py` and is Task 13's;
a gate that re-sorted them would be a second home for a total order, which is the defect class
§11 of the authoring brief was written to stop.

---

#### `Denied(unclassified)` is the ordinary path and this task is built for it

The detector is unwritten. D2 puts the rule set behind an injection and **no task in any plan
produces one**, so against a real corpus `ClassificationStore.current(file_id, content_hash)` returns
`None` for every file, `classification.resolve_class(None)` returns `unreadable_unclassified`, and the
call is denied. That is not a degraded mode; it is what a correct locked door does when nobody has
been handed a key.

It shapes this task concretely: the denial tests need no evidence setup at all, and the **one**
`Released` test is the one that has to write a classification by hand and says so in its docstring.
Absence never resolves to `public_low` — SPEC §1, which is §8.6's *"Cost exhaustion must never turn
into lower-quality automatic classification"* applied to the case that matters — and
`test_absence_never_resolves_to_a_lower_class` asserts it on the audit record the gate wrote, not on
an internal variable.

**`unreadable_unclassified` reaches `AuditRecord.file_sensitivity` and never
`files.sensitivity_state`** (D2: *"a GATE OUTCOME, not a file fact"*). The gate issues no
`UPDATE files` of its own; `test_the_gate_writes_no_classification_and_leaves_the_column_alone`
proves C4 and D2 with one assertion, which is why it is one test and not two.

---

#### `NeedsConsent` fires on the `protected` flag, and it answers no open question

The consent branch is reached when **no denial triggered**, the request carries text-bearing items,
at least one targeted file is `protected`, and the policy holds no grant for the scope. §8.4: *"If a
model needs text containing sensitive content, the user should see that requirement and choose
whether to allow a local model, a cloud model, a redacted prompt, or no model use."*

**It reads `ClassificationRecord.protected` and never a set of handling classes**, and that is
deliberate. SPEC §2: *"Whether `protected` is exactly co-extensive with the top two classes is **not
settled by the design** — see Open questions. Neighbouring parts should consume the `protected` flag,
not infer it from the class."* An earlier draft of this task published a
`SENSITIVE_CLASSES: tuple[str, str]` constant naming the top two; **that constant is removed here**,
because publishing it would answer NEEDS-JOSEPH **C5** (*"is `protected` exactly the top two handling
classes?"*) in an implementation instead of in a SPEC, which Task 21's guard exists to catch.

The cloud case never reaches this branch: `denial.protected_cloud_denies` decides it at position 6 of
`DENIAL_ORDER`, and its carve-out — `cloud_assisted` **plus** an explicit grant for the scope — is
§8.4's own sentence, *"User explicitly permits selected corpus areas to use a cloud model."* So the
branch that reaches the user is the **local** one, which is exactly the choice §8.4 describes: the
user is being asked whether a model may see sensitive text at all, and all four answers are open.

---

#### Two denials the gate cannot reach without a keyword Task 20 omits — reported, not invented

`Gate.__init__` adopts Task 20's ten pinned keywords verbatim and adds two optional ones. Both
default to `None`, and with the default the corresponding denial is **unreachable through the gate**
while remaining fully proven in Task 13:

- **`measure_tokens: Callable[[ModelCallRequest, tuple[Materialised, ...]], int] | None = None`.**
  `denial.over_dossier_ceiling(conn, *, measured_tokens)` needs a measurement and **P7 owns no
  tokenizer** — inventing one would invent a number, which SPEC *Deferred* and Task 21 both forbid.
  Task 13 is explicit that the check reads P1's stored ceiling and *"never `request.max_dossier_tokens`,
  which is only 'the caller's echo of it (M9)': a caller must not be able to raise its own ceiling by
  echoing a larger one."* So the measurement is injected. With none supplied there is nothing to
  compare, exactly as *"an UNSET ceiling cannot deny"* — the same shape, one level up. `dossier_over_budget`
  is M9's backstop that **should never fire in a correct pipeline**; do not delete the check.
- **`template_for: Callable[[str], str | None] | None = None`.**
  `denial.is_protected_records(template_name)` compares against §7.3's literal
  `PROTECTED_RECORDS_TEMPLATE = "Protected Records"`. The residual-template library that assigns a
  file to a template is P10's and P11's and **is unbuilt**; SPEC *Deferred* keeps its contents out of
  this contract. With no mapping supplied, no file is under a residual template.

**Reported to Task 20's author:** `gate_arguments(fixture, store=…)` supplies ten keywords, and
fixtures **4** and **16** (*"`Protected Records` residual, excerpt requested"* and *"…, filename
requested"*, both expecting `Denied(protected_records_template)`) cannot be replayed through the real
gate until it also supplies `template_for`. The two keywords are named here so that gap is a
one-line fixture change rather than a discovery during assembly.

---

#### `NoPolicyInForce` — the gate does not default a policy, and here is why that is not a gap

`policy.current_policy(conn, *, plan_version)` returns `Policy | None` (A6). When it returns `None`,
`Gate.release` raises `NoPolicyInForce`. It does **not** synthesise one.

The reason is brief §11's rule, applied: `defaults.effective_policy(conn, *, plan_version,
install_mode, set_at)` is Task 6's, it is where W1's local-first floor is resolved, and Done-means 12
is proven there. A gate that resolved its own default would be a **second home** for that floor,
which is the defect class this project has paid the most for — and it would need `install_mode`,
which is Open question 11 (*which* of `offline` and `local_model` ships) and which Task 20's pinned
constructor deliberately does not carry.

`NoPolicyInForce` is not a policy decision and it is not a `Denied`. It is the same class as
`resolve.UnresolvableSpan` — a call the gate cannot evaluate — and like those two it **propagates**.
It is not a *fourth branch*: `ReleaseDecision` has exactly three members and
`test_release_returns_one_of_exactly_three_types` asserts it.

---

#### What this task does not do

| Not done here | Owner | Why |
|---|---|---|
| The other six `Gate` methods — `revoke`, `reclassify`, `delete_derived`, `may_move_automatically`, `display_policy`, `summarize_protected` | Tasks 15–18 | Their modules do not exist at 11-b. Each of those tasks needs a `Modify: src/privacy/gate.py` line that its `Files` block currently omits; **named here so assembly can add it.** `files_in_scope` is constructor state held for `Gate.revoke` and is unused by `release`. |
| `DENIAL_ORDER`, `first_reason`, the eight builders, `RemedyOption`, `record_denial` | Task 13 | Published there; consumed here. The gate collects reasons and delegates the precedence. |
| The release ledger, `consume_release`, unforgeability | Task 12 | `gate.py` calls `mint_release`; L1 is proven in Task 12's own tests. |
| `NeedsConsent`'s dataclass, its id, `record_consent_choice`, the four-option invariant | Task 14 | `release.py` re-exports the type; `gate.py` calls `open_consent_request`. |
| Whether a caller absorbs `NeedsConsent` | P8 Done-means 13, P13 Done-means 16 | *"P7's obligation is to make the absorption unrepresentable, not to police it."* |
| Writing `bundle_file_entry.handling_class` | Task 22 / OQ8 | The gate never reaches P2's bundle. |
| A detector | **Nobody, and that is the finding** | D2 put the rule set behind an injection and no task supplies one. |

---

- [ ] **Step 1: Write `src/privacy/release.py`** — the request, the three branches, and the union

```python
# src/privacy/release.py
"""SPEC §6's request and its three-branch return. Types and constants only.

This module sits at the BOTTOM of P7's decision stack on purpose. `denial.py` imports
`Denied` from it at run time and `binding.py` imports `Released` from it under
TYPE_CHECKING, so anything this module imported from those two would close a cycle.
It therefore imports exactly two `privacy` modules at run time:

    privacy.consent      for NeedsConsent, which Task 14 owns and this module
                         re-exports so the union reads as one union in one place
    privacy.vocabulary   a LEAF -- it imports no `privacy` module at all -- for
                         `check_denial_reason`, so a hand-built `Denied` with an
                         invented reason is refused at construction

Everything else is annotation-only, under TYPE_CHECKING, which `from __future__ import
annotations` makes sufficient.

There is no override parameter anywhere in this file, and `FORBIDDEN_PARAMETER_NAMES`
plus `RELEASE_PARAMETERS` are what `tests/p7/test_p7_release.py` proves that with --
by parsing signatures and `dataclasses.fields`, never by reading source text.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from privacy.consent import NeedsConsent
from privacy.vocabulary import check_denial_reason

if TYPE_CHECKING:  # pragma: no cover - annotations only; no run-time edge
    from privacy.denial import RemedyOption
    from privacy.items import RequestedItem
    from privacy.redaction import RedactionManifest
    from privacy.resolve import Materialised

__all__ = [
    "LOCALITIES", "ModelTarget", "Target", "ModelCallRequest", "Released", "Denied",
    "NeedsConsent", "ReleaseDecision", "REQUEST_FIELDS", "RELEASED_FIELDS",
    "DENIED_FIELDS", "NEEDS_CONSENT_FIELDS", "DECISION_TYPES", "DECISION_ORDER",
    "FORBIDDEN_PARAMETER_NAMES", "RELEASE_PARAMETERS", "MalformedRequest",
    "MalformedDecision", "NoPolicyInForce",
]


class MalformedRequest(ValueError):
    """The request cannot be evaluated. Shape, not policy."""


class MalformedDecision(ValueError):
    """A branch value was constructed in a shape §8.4 does not permit."""


class NoPolicyInForce(RuntimeError):
    """No policy is stored for this plan version, so there is nothing to authorize by.

    NOT a fourth branch and NOT a `Denied`. §8.4's audit record names the "authorizing
    policy"; with none in force there is no answer to give, only a call that cannot be
    evaluated -- the same class as `resolve.UnresolvableSpan`, and it propagates.

    The gate deliberately does not synthesise a default. W1's local-first floor is
    resolved in `defaults.effective_policy`, which is where Done-means 12 is proven,
    and a second resolution here would be a second home for it.
    """


#: SPEC §6: `model_target { locality: local | cloud, model_id, provider }`.
LOCALITIES: tuple[str, str] = ("local", "cloud")


@dataclass(frozen=True, slots=True)
class ModelTarget:
    """Which model would receive the data. §8.4 audits it; §6 binds a release to it."""

    locality: str
    model_id: str
    provider: str

    def __post_init__(self) -> None:
        if self.locality not in LOCALITIES:
            raise MalformedRequest(
                f"locality {self.locality!r} is not one of {LOCALITIES}; a value "
                "outside a closed vocabulary is a load error, not a fallback")
        if not self.model_id or not self.provider:
            raise MalformedRequest(
                "§8.4 requires the audit record show WHICH MODEL received the data; "
                "an unnamed model or provider cannot satisfy that")

    def to_mapping(self) -> dict[str, str]:
        """The stored form. `AuditRecord.model` and the ledger both use it."""
        return {"locality": self.locality, "model_id": self.model_id,
                "provider": self.provider}


@dataclass(frozen=True, slots=True)
class Target:
    """§4.4, §7.7 -- what the call is about. Files, and optionally a group."""

    file_ids: tuple[str, ...]
    group_id: str | None = None

    def __post_init__(self) -> None:
        if not self.file_ids:
            raise MalformedRequest(
                "a release decision is about file versions; a target with no files "
                "has nothing to classify and nothing to audit")
        if len(set(self.file_ids)) != len(self.file_ids):
            raise MalformedRequest(
                f"file_ids {self.file_ids!r} repeats an id; the audit record's "
                "content_hashes would then double-count what left the device")


@dataclass(frozen=True, slots=True)
class ModelCallRequest:
    """SPEC §6's SEVEN fields, and deliberately no eighth.

    Every field is a REFERENCE. No field accepts a document string, a path, or an
    `Observation`: §8.4 puts "complete extracted text", "paths", "OCR output" and
    "raw sensitive values" in the always-local set, and a request that could carry one
    would have moved content before the gate had decided anything.

    `call_site` is NOT a field: B2 puts it inside `prompt_fingerprint` (§3.4, §8.2,
    §8.4), so it is neither a separate request field nor a separate binding term.
    """

    stage: str
    target: Target
    model_target: ModelTarget
    requested_items: tuple[RequestedItem, ...]
    prompt_template_id: str
    prompt_fingerprint: str
    max_dossier_tokens: int

    def __post_init__(self) -> None:
        if not self.stage:
            raise MalformedRequest(
                "§8.5 requires per-stage decomposition, so a call with no stage "
                "cannot be replayed or attributed")
        if not self.prompt_fingerprint:
            raise MalformedRequest(
                "§8.4 audits the prompt fingerprint, and B2 puts `call_site` inside "
                "it rather than beside it; an empty fingerprint audits nothing")
        if not self.prompt_template_id:
            raise MalformedRequest(
                "§8.8 reproduces the prompt in force at each call; that needs the "
                "template id")
        if not self.requested_items:
            raise MalformedRequest(
                "a request with no items has nothing to release")
        if self.max_dossier_tokens <= 0:
            raise MalformedRequest(
                "§8.6's ceiling is the caller's echo of P1's stored value (M9); zero "
                "or negative is not an echo of anything")


REQUEST_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(ModelCallRequest))


@dataclass(frozen=True, slots=True)
class Released:
    """SPEC §6's SIX fields. Single-use and bound; the ledger is Task 12's.

    Instantiating this dataclass outside the gate buys nothing: `consume_release`
    checks the ledger, and a `release_id` that was never minted raises
    `ReleaseNotIssued`. That is the property that makes the door real, and it is
    proven in Task 12, not here.
    """

    release_id: str
    audit_id: int
    policy_version: str
    materialised_items: tuple[Materialised, ...]
    redaction_manifest: RedactionManifest
    model_target: ModelTarget

    def __post_init__(self) -> None:
        if not self.release_id:
            raise MalformedDecision(
                "a release with no id cannot be bound or consumed (§6)")
        if not self.policy_version:
            raise MalformedDecision(
                "§6: the gate owns the policy and STAMPS the version; an unstamped "
                "release cannot be replayed under §8.8")


RELEASED_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(Released))


@dataclass(frozen=True, slots=True)
class Denied:
    """The gate's answer. Evidence-referenced (§6), and never a dead end (§8.6).

    FOUR fields. The skeleton's Task 11 block lists three and omits `evidence_refs`;
    SPEC §6 requires the explanation be "evidence-referenced" and Task 13's published
    `deny(reason, *, explanation, remedy_options, evidence_refs)` takes them, so a
    three-field dataclass makes that constructor unwritable.

    `evidence_refs` holds P4 `observation_key` values and never `observation_id`
    (M14): a per-row id dies on extractor upgrade, and `observation_key` deliberately
    excludes `extractor_version` (MINOR 8) so it survives one. It defaults to `()`
    because six of the eight reasons are decided from the request and the policy and
    have no evidence to cite; an empty tuple there is honest, not lazy.
    """

    reason: str
    explanation: str
    remedy_options: tuple[RemedyOption, ...]
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        check_denial_reason(self.reason)
        if not self.explanation or not self.explanation.strip():
            raise MalformedDecision(
                "§8.6 requires the product show 'what has been deferred, and why'; a "
                "denial with an empty explanation shows only the first half")
        if not self.remedy_options:
            raise MalformedDecision(
                "a denial with no legitimate alternative is a dead end the user "
                "cannot act on (§8.6)")


DENIED_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(Denied))
NEEDS_CONSENT_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(NeedsConsent))

#: SPEC §6: `ReleaseDecision = Released | Denied | NeedsConsent`. Three, and no fourth.
#: `NoPolicyInForce` is an exception, not a member: it says the call cannot be
#: evaluated, where all three of these say what the answer IS.
ReleaseDecision = Released | Denied | NeedsConsent

DECISION_TYPES: tuple[type, ...] = (Released, Denied, NeedsConsent)

#: The order `Gate.release` evaluates in, published so a reviewer can read it without
#: reading the function and so a reordering is a diff on a constant. It is forced, not
#: chosen: nothing materialises until every check that could deny has run, because a
#: gate that resolved first would hold the text in memory before deciding it was
#: allowed to. Task 13's `DECIDABLE_FROM_REQUEST` is the same principle as data, and
#: the test asserts the two agree.
DECISION_ORDER: tuple[str, ...] = (
    "collect_request_denials",
    "needs_consent",
    "materialise",
    "collect_content_denials",
    "append_audit",
    "mint_release",
)

#: The exact parameter names of `Gate.release`. Published so the whitelist assertion
#: is an EQUALITY against a named constant rather than a literal buried in a test.
RELEASE_PARAMETERS: frozenset[str] = frozenset({"self", "request"})

#: The words a future convenience would reach for. Compared TOKEN-WISE, on
#: `name.split("_")`, never by substring: substring matching would fail a legitimate
#: `unclassified_permits_local` and would tempt the next author to rename a parameter
#: to appease a test. This is the weaker of the two guards -- a blacklist only catches
#: the words someone thought of -- and it exists beside `RELEASE_PARAMETERS`, which
#: proves no unpublished parameter exists at all.
FORBIDDEN_PARAMETER_NAMES: frozenset[str] = frozenset({
    "force", "override", "bypass", "allow", "approved", "skip", "unsafe",
    "trusted", "internal", "escalate", "ignore", "disable", "raw", "plaintext",
})
```

- [ ] **Step 2: Commit `release.py` — this is commit 11-a, and it lands BEFORE Tasks 13 and 12**

Run first, because a types-only module either imports or it does not:

```bash
PYTHONPATH=src python3 -c "
import privacy.release as r
print(r.REQUEST_FIELDS)
print(r.RELEASED_FIELDS)
print(r.DENIED_FIELDS)
print(r.NEEDS_CONSENT_FIELDS)
"
```

Expected:

```text
('stage', 'target', 'model_target', 'requested_items', 'prompt_template_id', 'prompt_fingerprint', 'max_dossier_tokens')
('release_id', 'audit_id', 'policy_version', 'materialised_items', 'redaction_manifest', 'model_target')
('reason', 'explanation', 'remedy_options', 'evidence_refs')
('consent_request_id', 'requirement', 'options')
```

If the last line raises `ModuleNotFoundError: privacy.consent`, **Task 14 has not been executed yet**
and the order in *Execution order* was not followed.

```bash
git add src/privacy/release.py
git commit -m "feat(P7): the release request and the three-branch union, with Denied carrying evidence_refs"
```

> **Tasks 13 and 12 run now.** `denial.py` imports `release.Denied` at run time; `binding.py` imports
> `release.Released` under `TYPE_CHECKING`. Neither can be written before this commit exists.

---

- [ ] **Step 3: Write the failing test**

```python
# tests/p7/test_p7_release.py
"""§8.4's one door: the request, the three branches, and no way around it.

The shape tests are the point, and they come first. A gate whose decision logic is
right and whose signature carries an `override=` keyword is not a gate, and the second
failure is the one review does not catch. Every shape assertion here is parsed from
`inspect.signature` and `dataclasses.fields` -- never from source text, which matches
comments and docstrings and has produced a false result eight times on this project.

`Denied(unclassified)` is the ordinary path. The detector is unwritten (D2), so on a
real corpus every file lands there; the denial tests need no evidence at all, and the
ONE `Released` test is the one that has to write a classification by hand.
"""
from __future__ import annotations

import dataclasses
import inspect
import json
import sqlite3
from pathlib import Path

import pytest

from database_agent.budget import set_ceiling
from database_agent.files_table import get_file, record_file
from evidence_shape.canonical import canonical_json
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import (
    TextUnit, new_id, record_observation, record_run, record_text_unit,
)

from privacy.authorship import COMPONENT_VERSION
from privacy.binding import consume_release
from privacy.classification import ClassificationRecord, UNREADABLE_UNCLASSIFIED
from privacy.classification_store import ClassificationStore
from privacy.consent import NeedsConsent
from privacy.defaults import MORE_REDACTING
from privacy.denial import DECIDABLE_FROM_REQUEST, DENIAL_ORDER
from privacy.gate import TEXT_BEARING, Gate
from privacy.items import Excerpt, Filename, RedactedIdentifier
from privacy.policy import Policy, UNSET_POLICY_VERSION, set_policy
from privacy.redaction import RedactionManifest
from privacy.release import (
    DECISION_ORDER, DECISION_TYPES, DENIED_FIELDS, FORBIDDEN_PARAMETER_NAMES,
    NEEDS_CONSENT_FIELDS, RELEASED_FIELDS, RELEASE_PARAMETERS, REQUEST_FIELDS,
    Denied, ModelCallRequest, ModelTarget, NoPolicyInForce, Released, Target,
)
from privacy.resolve import UnresolvableSpan
from privacy.schema import create_privacy_schema

OBSERVED_AT = "2026-08-22T09:00:00Z"
PLAN_VERSION = "plan-v1"
TEXT = "Passport number A1234567 was issued in 2019 to the applicant."
SPAN = TextSpan(start=16, end=24)          # "A1234567"
LOCAL = ModelTarget(locality="local", model_id="llama-local", provider="on-device")
CLOUD = ModelTarget(locality="cloud", model_id="big-model", provider="a-provider")


# --------------------------------------------------------------------------
# seeding -- P1 and P4 writers only, all introspected live 2026-08-22
# --------------------------------------------------------------------------

def _file(conn: sqlite3.Connection, name: str, content_hash: str) -> str:
    return record_file(
        conn, Path("/corpus") / name, filename=name,
        normalized_filename=name.lower(), extension=Path(name).suffix,
        observed_size=4096,
        observed_timestamps=canonical_json({"modified": OBSERVED_AT}),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="scanned", materialized=True,
        content_hash=content_hash)


def _evidence(conn: sqlite3.Connection, file_id: str, content_hash: str) -> str:
    """One run, one text unit, one observation. Returns the `observation_key`."""
    run_id = new_id()
    page = (Segment(kind="page", index=1),)
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="fixture.text", extractor_version="1.0.0",
        source_type="pdf", analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, observation_count=1))
    record_text_unit(conn, TextUnit(run_id=run_id, container_path=page, text=TEXT))
    location = Location(zone="body", container_path=page, text_span=SPAN)
    record_observation(conn, Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="fixture.text",
        extractor_version="1.0.0", source_type="pdf",
        raw_value=TEXT[SPAN.start:SPAN.end], location=location, occurrence_count=1,
        observed_at=OBSERVED_AT, reliability="direct", run_id=run_id,
        context_before=TEXT[:SPAN.start], context_after=TEXT[SPAN.end:],
        context_truncated=False))
    return observation_key(
        content_hash=content_hash, extractor_name="fixture.text",
        locator=serialize_locator(location), raw_value=TEXT[SPAN.start:SPAN.end])


def _policy(conn: sqlite3.Connection, mode: str, *, grants=()) -> Policy:
    """Store a policy and read back the version the gate will stamp."""
    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode=mode,
        consent_grants=tuple(grants), redaction_settings=dict(MORE_REDACTING),
        automatic_move_permissions={}, plan_version=PLAN_VERSION, set_at=OBSERVED_AT)
    version = set_policy(conn, draft, component_version=COMPONENT_VERSION,
                         user_id="joseph", reason="test fixture")
    return dataclasses.replace(draft, policy_version=version)


def _classify(conn: sqlite3.Connection, file_id: str, content_hash: str, *,
              handling_class: str, protected: bool, refs=("obs-key-1",)) -> None:
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class=handling_class,
        protected=protected, basis="detector", evidence_refs=tuple(refs),
        reliability_state="direct", observed_at=OBSERVED_AT))


def _classifier(value: str, *, context_before=None, context_after=None) -> str | None:
    """SPEC *Deferred* keeps identifier classes opaque; this enumerates nothing."""
    return "fixture-identifier-class"


def _transform(value: str, *, identifier_class: str) -> str:
    return "[redacted]"


def _gate(conn: sqlite3.Connection, **overrides) -> Gate:
    keywords: dict[str, object] = {
        "store": ClassificationStore(conn),
        "plan_version": PLAN_VERSION,
        "classifier": _classifier,
        "transform": _transform,
        "unclassified_permits_local": False,
        "scope_for": lambda file_id: "area-1",
        "files_in_scope": lambda scope: (),
        "component_version": COMPONENT_VERSION,
        "now": lambda: OBSERVED_AT,
        "user_id": "joseph",
    }
    keywords.update(overrides)
    return Gate(conn, **keywords)


def _request(*, items, model_target=CLOUD, file_ids=("f1",), stage="grouping",
             max_dossier_tokens=4000) -> ModelCallRequest:
    return ModelCallRequest(
        stage=stage, target=Target(file_ids=tuple(file_ids)),
        model_target=model_target, requested_items=tuple(items),
        prompt_template_id=f"template.{stage}",
        prompt_fingerprint=f"fingerprint.{stage}",
        max_dossier_tokens=max_dossier_tokens)


def _events(conn: sqlite3.Connection, event_type: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM events WHERE event_type = ? ORDER BY event_id",
        (event_type,)).fetchall()


@pytest.fixture()
def gate_conn(p7_conn):
    create_privacy_schema(p7_conn)
    return p7_conn


# --------------------------------------------------------------------------
# 1-12  shape: the signature, the fields, and the absence of an override
# --------------------------------------------------------------------------

def test_release_takes_the_request_and_nothing_else():
    """B2: P8 adopts SPEC §6's signature verbatim, so there is no second parameter.

    The WHITELIST half, and it is the stronger one: an equality proves no unpublished
    parameter exists AT ALL, where a blacklist only catches words someone thought of.
    """
    assert set(inspect.signature(Gate.release).parameters) == RELEASE_PARAMETERS
    assert RELEASE_PARAMETERS == {"self", "request"}


def test_no_signature_and_no_branch_field_names_an_override():
    """The BLACKLIST half, token-wise over every published name in the part."""
    names = set(inspect.signature(Gate.release).parameters)
    names |= set(inspect.signature(Gate.__init__).parameters)
    for kind in (ModelCallRequest, Target, ModelTarget, *DECISION_TYPES):
        names |= {f.name for f in dataclasses.fields(kind)}
    tokens = {token for name in names for token in name.split("_")}
    assert tokens.isdisjoint(FORBIDDEN_PARAMETER_NAMES), sorted(
        tokens & FORBIDDEN_PARAMETER_NAMES)


def test_the_blacklist_is_compared_token_wise_and_not_by_substring():
    """`unclassified_permits_local` is legitimate and must stay legitimate.

    A substring comparison would have to drop `permit` from the blacklist or rename a
    parameter to appease a test. Both are worse than splitting on underscores.
    """
    name = "unclassified_permits_local"
    assert name in inspect.signature(Gate.__init__).parameters
    # A substring rule would have to keep `permit` out of the blacklist to let this
    # name through. A token rule does not: "permits" is not "permit".
    assert set(name.split("_")).isdisjoint(FORBIDDEN_PARAMETER_NAMES)
    assert "permit" not in FORBIDDEN_PARAMETER_NAMES


def test_the_request_carries_references_only():
    """§8.4 puts complete extracted text, paths and OCR output in the always-local set.

    A request field that accepted one would have moved content before the gate had
    decided anything. Asserted over the annotations, not over a value.
    """
    annotations = {f.name: str(f.type) for f in dataclasses.fields(ModelCallRequest)}
    assert annotations["target"] == "Target"
    assert annotations["model_target"] == "ModelTarget"
    assert annotations["requested_items"] == "tuple[RequestedItem, ...]"
    for name, annotation in annotations.items():
        assert "Observation" not in annotation, name
        assert "Path" not in annotation, name
    assert [f.name for f in dataclasses.fields(ModelCallRequest)
            if str(f.type) == "str"] == [
        "stage", "prompt_template_id", "prompt_fingerprint"]


def test_request_fields_are_specs_seven_in_specs_order():
    assert REQUEST_FIELDS == (
        "stage", "target", "model_target", "requested_items", "prompt_template_id",
        "prompt_fingerprint", "max_dossier_tokens")
    assert "call_site" not in REQUEST_FIELDS   # B2 puts it inside the fingerprint


def test_released_fields_are_specs_six_in_specs_order():
    assert RELEASED_FIELDS == (
        "release_id", "audit_id", "policy_version", "materialised_items",
        "redaction_manifest", "model_target")


def test_denied_carries_evidence_refs_as_its_fourth_field():
    """SPEC §6: the explanation is "evidence-referenced". Task 13's `deny` takes them.

    The skeleton's Task 11 block lists three fields and omits this one; a constructor
    that accepts a value the dataclass cannot hold is not writable.
    """
    assert DENIED_FIELDS == ("reason", "explanation", "remedy_options",
                             "evidence_refs")
    denied = Denied(reason="unclassified", explanation="why", remedy_options=("ask",),
                    evidence_refs=("obs-key-1", "obs-key-2"))
    assert denied.evidence_refs == ("obs-key-1", "obs-key-2")
    assert Denied(reason="unclassified", explanation="why",
                  remedy_options=("ask",)).evidence_refs == ()


def test_needs_consent_has_no_reason_field():
    """"`Denied` is the gate's answer, `NeedsConsent` is a question only the user can
    answer." A caller cannot map it onto a denial reason even by accident."""
    assert "reason" not in NEEDS_CONSENT_FIELDS
    assert "consent_request_id" in NEEDS_CONSENT_FIELDS


def test_the_three_branches_share_no_field_name():
    """Structurally distinct, so no branch can be read as another.

    This also carries the assertion Task 14 makes over two of the three; it is made
    here over all three because this is the module that publishes the union.
    """
    named = [{f.name for f in dataclasses.fields(kind)} for kind in DECISION_TYPES]
    for left in range(len(named)):
        for right in range(left + 1, len(named)):
            assert named[left].isdisjoint(named[right])


def test_release_returns_one_of_exactly_three_types():
    """SPEC §6: `ReleaseDecision = Released | Denied | NeedsConsent`. No fourth.

    `NoPolicyInForce` is an exception rather than a member: it says the call cannot be
    EVALUATED, where all three of these say what the answer IS.
    """
    assert DECISION_TYPES == (Released, Denied, NeedsConsent)
    assert not issubclass(NoPolicyInForce, tuple(DECISION_TYPES))


def test_release_py_imports_no_privacy_module_but_consent_and_vocabulary():
    """The import direction Tasks 12-14 fixed, asserted by module introspection.

    `denial` imports `release.Denied` at run time and `binding` imports `Released`
    under TYPE_CHECKING, so anything `release` imported back from those two would
    close a cycle. `vocabulary` is a leaf and cannot.
    """
    import privacy.release as module

    bound = {value.__name__ for value in vars(module).values()
             if getattr(value, "__module__", "").startswith("privacy.")}
    imported = {getattr(value, "__module__", "")
                for value in vars(module).values()
                if getattr(value, "__module__", "").startswith("privacy.")}
    assert imported <= {"privacy.consent", "privacy.vocabulary", "privacy.release"}
    assert "NeedsConsent" in bound          # re-exported, not redefined
    assert NeedsConsent.__module__ == "privacy.consent"


def test_decision_order_puts_every_request_decidable_denial_before_materialisation():
    """No denial decidable from the request may be decided after one that reads text.

    A gate that materialised an excerpt and THEN discovered the mode forbade the call
    has read a sensitive file for a call that was never going to happen.
    """
    assert DECISION_ORDER == (
        "collect_request_denials", "needs_consent", "materialise",
        "collect_content_denials", "append_audit", "mint_release")
    assert DECISION_ORDER.index("collect_request_denials") < \
        DECISION_ORDER.index("materialise")
    assert DECISION_ORDER.index("append_audit") < DECISION_ORDER.index("mint_release")
    late = {r for r in DENIAL_ORDER if r not in DECIDABLE_FROM_REQUEST}
    assert max(DENIAL_ORDER.index(r) for r in DECIDABLE_FROM_REQUEST) < \
        min(DENIAL_ORDER.index(r) for r in late)


# --------------------------------------------------------------------------
# 13-20  the denial branch -- the ordinary path
# --------------------------------------------------------------------------

def test_an_unclassified_file_is_denied_and_that_is_the_ordinary_path(gate_conn):
    """No detector exists (D2), so this is what the gate answers on a Tuesday.

    No classification is written by this test, which is the point: the setup for the
    normal case is nothing at all.
    """
    file_id = _file(gate_conn, "unknown.pdf", "hash-unknown")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-unknown")
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Denied)
    assert decision.reason == "unclassified"


def test_absence_never_resolves_to_a_lower_class(gate_conn):
    """SPEC §1: absence resolves to `unreadable_unclassified`, NEVER to `public_low`.

    §8.6: "Cost exhaustion must never turn into lower-quality automatic
    classification." Asserted on the audit record the gate wrote, not on an internal.
    """
    file_id = _file(gate_conn, "unknown.pdf", "hash-unknown")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-unknown")
    _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    row = _events(gate_conn, "model_release_denied")[0]
    explanation = json.loads(row["explanation"])
    assert explanation["file_sensitivity"] == UNREADABLE_UNCLASSIFIED
    assert "public_low" not in row["explanation"]


def test_offline_mode_denies_a_cloud_target_before_anything_is_read(gate_conn):
    """§8.4: under offline "No content leaves the device". Outermost in DENIAL_ORDER."""
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    _policy(gate_conn, "offline")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Denied)
    assert decision.reason == "mode_forbids_target"


def test_overlapping_reasons_resolve_through_first_reason(gate_conn):
    """An unclassified protected file under `offline` with a cloud target triggers
    three reasons at once. The gate collects and DELEGATES; `DENIAL_ORDER` is Task
    13's and a gate that re-sorted them would be a second home for a total order."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "offline")
    key = _evidence(gate_conn, file_id, "hash-passport")
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert decision.reason == DENIAL_ORDER[0] == "mode_forbids_target"


def test_a_protected_file_with_a_cloud_target_is_denied(gate_conn):
    """SPEC §2's first protected consequence: not in cloud prompts BY DEFAULT."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-passport")
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="sensitive_personal", protected=True,
              refs=(key,))
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Denied)
    assert decision.reason == "protected_cloud_target"
    assert decision.evidence_refs == (key,)


def test_a_denial_appends_exactly_one_model_release_denied(gate_conn):
    """§8.2: "Every significant event affecting a file." One event, not two."""
    file_id = _file(gate_conn, "unknown.pdf", "hash-unknown")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-unknown")
    _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert len(_events(gate_conn, "model_release_denied")) == 1
    assert _events(gate_conn, "model_release") == []


def test_the_gate_writes_no_classification_and_leaves_the_column_alone(gate_conn):
    """C4 and D2 in one assertion, which is why it is one test and not two.

    C4: "a gate that also wrote would be doing two jobs." D2: "`Unreadable or
    unclassified` is a GATE OUTCOME, not a file fact ... it lives on the release
    decision and never in that column."
    """
    file_id = _file(gate_conn, "unknown.pdf", "hash-unknown")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-unknown")
    before = get_file(gate_conn, file_id)["sensitivity_state"]
    _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    after = get_file(gate_conn, file_id)["sensitivity_state"]
    assert after == before
    assert after is None or UNREADABLE_UNCLASSIFIED not in str(after)
    assert ClassificationStore(gate_conn).current(file_id, "hash-unknown") is None


def test_a_filename_on_a_protected_records_file_is_denied(gate_conn):
    """§7.3: for Protected Records, "filenames and content must not be exposed in
    model prompts at all" -- and it binds a LOCAL target too, which is why it
    outranks the cloud rule in DENIAL_ORDER."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "cloud_assisted", grants=(("area-1", "cloud_model"),))
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="highly_sensitive_credential_bearing", protected=True)
    decision = _gate(
        gate_conn,
        template_for=lambda _file_id: "Protected Records",
    ).release(_request(items=(Filename(file_id=file_id, value="passport.pdf"),),
                       model_target=LOCAL, file_ids=(file_id,), stage="residual"))
    assert isinstance(decision, Denied)
    assert decision.reason == "protected_records_template"


# --------------------------------------------------------------------------
# 21-23  the consent branch
# --------------------------------------------------------------------------

def test_a_protected_file_on_a_local_target_with_no_grant_needs_consent(gate_conn):
    """§8.4: "If a model needs text containing sensitive content, the user should see
    that requirement and choose." The cloud case is denied at DENIAL_ORDER 6; the
    local case is the one that reaches the user, and all four answers are open."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "local_model")
    key = _evidence(gate_conn, file_id, "hash-passport")
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="sensitive_personal", protected=True)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=LOCAL, file_ids=(file_id,)))
    assert isinstance(decision, NeedsConsent)
    assert decision.consent_request_id
    assert len(_events(gate_conn, "consent_requested")) == 1
    assert _events(gate_conn, "model_release") == []


def test_the_consent_branch_reads_the_protected_flag_and_not_a_class_list(gate_conn):
    """SPEC §2: "Neighbouring parts should consume the `protected` flag, not infer it
    from the class." Whether `protected` is co-extensive with the top two classes is
    NEEDS-JOSEPH C5 and this module answers it nowhere."""
    import privacy.release as release_module
    import privacy.gate as gate_module

    assert not hasattr(release_module, "SENSITIVE_CLASSES")
    assert not hasattr(gate_module, "SENSITIVE_CLASSES")
    file_id = _file(gate_conn, "odd.pdf", "hash-odd")
    _policy(gate_conn, "local_model")
    key = _evidence(gate_conn, file_id, "hash-odd")
    _classify(gate_conn, file_id, "hash-odd",
              handling_class="personal_non_sensitive", protected=True)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=LOCAL, file_ids=(file_id,)))
    assert isinstance(decision, NeedsConsent)


def test_a_granted_scope_does_not_ask_again(gate_conn):
    """Consent already given is not a question. §8.4's grant is per corpus area, and
    what a corpus area IS stays Open question 3 -- `scope_for` is the caller's.

    It returns `str | None` because Open question 3 is open: a file that belongs to
    no area must be representable, and `None not in granted` is True, so such a file
    asks for consent rather than matching a grant by accident. Widened from
    `Callable[[str], str]` at assembly, when Task 20's fixtures -- which pass
    `lambda _file_id: None` -- were reconciled onto this name."""
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "local_model", grants=(("area-1", "local_model"),))
    key = _evidence(gate_conn, file_id, "hash-passport")
    _classify(gate_conn, file_id, "hash-passport",
              handling_class="sensitive_personal", protected=True)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        model_target=LOCAL, file_ids=(file_id,)))
    assert isinstance(decision, Released)


# --------------------------------------------------------------------------
# 24-28  the release branch, the ordering guarantee, and what escapes
# --------------------------------------------------------------------------

def test_a_clean_call_returns_released_with_an_audit_id_already_in_the_log(gate_conn):
    """Done-means 4, and the ONE test that has to write a classification by hand.

    SPEC §6: "the audit record is appended ... BEFORE `Released` is returned. There is
    no interval in which content is releasable and unaudited." `append_audit` returns
    `cursor.lastrowid`, so the id exists only after the row does -- which makes the
    ordering a structural fact rather than a discipline.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    policy = _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False, refs=(key,))
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Released)
    assert decision.policy_version == policy.policy_version
    assert decision.model_target == CLOUD
    row = gate_conn.execute("SELECT * FROM events WHERE event_id = ?",
                            (decision.audit_id,)).fetchone()
    assert row is not None
    assert row["event_type"] == "model_release"
    assert row["subsystem"] == "P7"
    explanation = json.loads(row["explanation"])
    pairs = explanation["excerpts_included"]
    assert len(pairs) == 1 and pairs[0][0] == key
    # SPEC §7: the record stores (observation_key, span) pairs "not a second copy of
    # the text". The pair is enough to re-run `resolve.materialise`; the value is not
    # in the log.
    assert TEXT[SPAN.start:SPAN.end] not in row["explanation"]


def test_the_released_id_is_in_the_ledger_and_a_fabricated_one_is_not(gate_conn):
    """Task 12 proves single use; this proves the gate actually MINTED through it.

    A `Released` the gate returned consumes; one a caller builds does not, because the
    id it carries was never in the ledger.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    policy = _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    consume_release(gate_conn, decision, model_target=CLOUD,
                    prompt_fingerprint="fingerprint.grouping",
                    policy_version=policy.policy_version)
    forged = dataclasses.replace(decision, release_id="0" * 32)
    with pytest.raises(Exception):
        consume_release(gate_conn, forged, model_target=CLOUD,
                        prompt_fingerprint="fingerprint.grouping",
                        policy_version=policy.policy_version)


def test_no_content_is_read_before_every_request_decidable_check_has_run(
        gate_conn, monkeypatch):
    """The ordering property, proven by making materialisation fail the test.

    "Nothing materialises until every check that could deny has run" is the reason
    `DECISION_ORDER` exists, and a comment is not a proof.
    """
    import privacy.gate as gate_module

    def _explode(conn, item):   # pragma: no cover - the assertion IS not calling it
        raise AssertionError("the gate read content before it had decided")

    monkeypatch.setattr(gate_module, "materialise", _explode)
    file_id = _file(gate_conn, "passport.pdf", "hash-passport")
    _policy(gate_conn, "offline")
    key = _evidence(gate_conn, file_id, "hash-passport")
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,)))
    assert isinstance(decision, Denied)


def test_materialised_items_hold_only_what_had_a_value_to_resolve(gate_conn):
    """SPEC §6: "materialised_items[] post-redaction values only."

    §4: an evidence reference is "an id only -- no content", and a filename, a
    candidate label and a metadata field carry no local content either. The gate does
    not echo back what it did not touch; the caller still holds the request it sent.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),
               Filename(file_id=file_id, value="notes.pdf")),
        file_ids=(file_id,)))
    assert isinstance(decision, Released)
    assert len(decision.materialised_items) == 1
    assert decision.materialised_items[0].observation_key == key
    assert decision.materialised_items[0].value == "[redacted]"
    assert isinstance(decision.redaction_manifest, RedactionManifest)
    assert decision.redaction_manifest.any_redacted is True
    assert TEXT_BEARING == (Excerpt, RedactedIdentifier)


def test_a_call_with_no_policy_in_force_raises_rather_than_defaulting(gate_conn):
    """W1's local-first floor is resolved in `defaults.effective_policy`, where
    Done-means 12 is proven. A second resolution here would be a second home for it,
    and it would need `install_mode`, which is Open question 11."""
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    key = _evidence(gate_conn, file_id, "hash-notes")
    with pytest.raises(NoPolicyInForce):
        _gate(gate_conn).release(_request(
            items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
            file_ids=(file_id,)))


def test_a_resolve_failure_propagates_and_is_not_a_denial(gate_conn):
    """A span the evidence does not carry is a contract violation by the CALLER.

    P4's `check_span_anchor` "raises; never returns a repair", and a gate that
    repaired would release text nobody addressed. `Denied` and `NeedsConsent` are
    values; these two are exceptions, and the difference is deliberate.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    _policy(gate_conn, "hybrid")
    _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    with pytest.raises(UnresolvableSpan):
        _gate(gate_conn).release(_request(
            items=(Excerpt(observation_key="no-such-key", span=SPAN,
                           reason="heading"),),
            file_ids=(file_id,)))


def test_an_unset_dossier_ceiling_and_no_measurement_cannot_deny(gate_conn):
    """M9's backstop, and the two reasons it stays unreachable by default.

    `get_ceiling` returns `None` when nothing set it, and P7 owns no tokenizer, so
    `measure_tokens` is injected. With a ceiling AND a measurement the backstop fires;
    a P8 test that reaches it through the normal path is a P8 failure, not a gate
    result. Do not delete the check.
    """
    file_id = _file(gate_conn, "notes.pdf", "hash-notes")
    _policy(gate_conn, "hybrid")
    key = _evidence(gate_conn, file_id, "hash-notes")
    _classify(gate_conn, file_id, "hash-notes",
              handling_class="public_low", protected=False)
    request = _request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),),
        file_ids=(file_id,))
    assert isinstance(_gate(gate_conn).release(request), Released)

    set_ceiling(gate_conn, "model.max_dossier_tokens_per_call", 10)
    decision = _gate(
        gate_conn, measure_tokens=lambda request, items: 11).release(request)
    assert isinstance(decision, Denied)
    assert decision.reason == "dossier_over_budget"
```

- [ ] **Step 4: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_release.py -q`

Expected: **FAIL — collection error**, `ModuleNotFoundError: No module named 'privacy.gate'`.
`src/privacy/release.py` exists from commit 11-a and `privacy.binding`, `privacy.denial` and
`privacy.consent` exist from Tasks 12, 13 and 14; `privacy.gate` is the one module still missing, so
the failure is one import and not thirty.

- [ ] **Step 5: Write `src/privacy/gate.py`**

```python
# src/privacy/gate.py
"""The one door. `Gate.release(ModelCallRequest) -> ReleaseDecision`, and nothing else.

B2 adopts SPEC §6's signature verbatim on both sides, so `release` takes the request
and NOTHING ELSE -- no override, no flag, no connection. Everything the gate needs
beyond the request is constructor state, and three of those constructor parameters
carry no default because each is an open question this plan will not guess:

    classifier / transform      SPEC *Deferred*: identifier classes and the redaction
                                transform are not enumerated anywhere in the design.
    scope_for                   Open question 3: "What is a 'corpus area'? ... Consent
                                grants cannot be scoped until this is named."
    unclassified_permits_local  Open question 5: does `unreadable_unclassified` permit
                                a LOCAL model call?

The gate writes exactly ONE thing -- the audit record -- and it writes it BEFORE the
decision is returned, because §8.4 makes recording the authorization part of granting
it (C4). It writes no classification, no `files.sensitivity_state`, no `stage_output`,
no placement decision and no P8 `Refusal`. The catcher is always the caller's.

It decides no precedence of its own: it COLLECTS every triggered reason and asks
`denial.first_reason` which one wins, because `DENIAL_ORDER` is Task 13's and a second
total order here would be a second home for it.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence

from database_agent.budget import get_ceiling
from database_agent.files_table import get_file
from evidence_shape.canonical import canonical_json

from privacy.audit import AuditRecord, append_audit
from privacy.authorship import SUBSYSTEM
from privacy.binding import mint_release
from privacy.classification import (
    UNREADABLE_UNCLASSIFIED, ClassificationRecord, resolve_class,
)
from privacy.consent import ConsentRequirement, open_consent_request
from privacy.denial import (
    deny_always_local_item, deny_dossier_over_budget, deny_mode_forbids_target,
    deny_policy_revoked, deny_protected_cloud_target,
    deny_protected_records_template, deny_unclassified,
    deny_whole_document_requested, first_reason, is_protected_records, mode_forbids,
    over_dossier_ceiling, policy_revoked_for, protected_cloud_denies, record_denial,
    unclassified_denies,
)
from privacy.items import (
    AlwaysLocalRequested, Excerpt, ProtectedItemRequested, RedactedIdentifier,
    WholeDocumentRequested, check_item, kind_of, sensitive_observation_keys,
)
from privacy.policy import current_policy
from privacy.redaction import RedactionManifest, apply_redaction
from privacy.release import (
    DECISION_ORDER, Denied, ModelCallRequest, NeedsConsent, NoPolicyInForce,
    ReleaseDecision, Released,
)
from privacy.resolve import Materialised, materialise

#: §4's two item kinds that address local text and therefore resolve to a value.
#: `candidate_label`, `metadata_field`, `evidence_reference` and `filename` carry no
#: local content -- §4: an evidence reference is "an id only -- no content" -- so they
#: are never materialised and never echoed back.
TEXT_BEARING: tuple[type, ...] = (Excerpt, RedactedIdentifier)


class Gate:
    """§8.4's gate. One object, one door, no second name.

    Task 20 pins the first ten keywords (`GATE_ARGUMENTS`) so its fixtures replay
    through the real gate. `measure_tokens` and `template_for` are two OPTIONAL
    additions, both defaulting to `None`, and both reported to Task 20:

    - `measure_tokens` -- P7 owns no tokenizer and inventing one would invent a
      number. With no measurement there is nothing to compare, exactly as an unset
      ceiling cannot deny.
    - `template_for` -- §7.3's residual-template library is P10's and P11's and is
      unbuilt. With no mapping, no file is under a residual template.
    """

    def __init__(self, conn: sqlite3.Connection, *, store, plan_version: str,
                 classifier, transform, unclassified_permits_local: bool,
                 scope_for: Callable[[str], str | None],
                 files_in_scope: Callable[[str], Sequence[str]],
                 component_version: str, now: Callable[[], str],
                 user_id: str | None,
                 measure_tokens: Callable[..., int] | None = None,
                 template_for: Callable[[str], str | None] | None = None) -> None:
        self._conn = conn
        self._store = store
        self._plan_version = plan_version
        self._classifier = classifier
        self._transform = transform
        self._unclassified_permits_local = unclassified_permits_local
        self._scope_for = scope_for
        #: Held for `Gate.revoke` (Task 15); `release` does not use it.
        self._files_in_scope = files_in_scope
        self._component_version = component_version
        self._now = now
        self._user_id = user_id
        self._measure_tokens = measure_tokens
        self._template_for = template_for

    # -- §8.4's only door ---------------------------------------------------

    def release(self, request: ModelCallRequest) -> ReleaseDecision:
        """See `release.DECISION_ORDER` for the order and why it is forced."""
        assert DECISION_ORDER[0] == "collect_request_denials"
        policy = current_policy(self._conn, plan_version=self._plan_version)
        if policy is None:
            raise NoPolicyInForce(
                f"no privacy policy is stored for plan version "
                f"{self._plan_version!r}. §8.4's audit record names the authorizing "
                "policy and there is none; W1's local-first floor is resolved in "
                "`defaults.effective_policy`, not here, so the gate refuses to "
                "invent one")

        observed_at = self._now()
        locality = request.model_target.locality
        file_ids = request.target.file_ids
        scope = self._scope_for(file_ids[0])
        granted = tuple(name for name, _option in policy.consent_grants)

        rows = {file_id: get_file(self._conn, file_id) for file_id in file_ids}
        hashes = tuple(rows[file_id]["content_hash"] for file_id in file_ids)
        records = {file_id: self._store.current(file_id, rows[file_id]["content_hash"])
                   for file_id in file_ids}
        classes = {file_id: resolve_class(record)
                   for file_id, record in records.items()}
        protected_ids = tuple(file_id for file_id, record in records.items()
                              if record is not None and record.protected)
        decisive = self._decisive(records, protected_ids, file_ids)
        sensitive_keys = frozenset().union(*(
            sensitive_observation_keys(self._conn, file_id) for file_id in file_ids))

        # 1 -- every reason decidable from the request, the policy and a row lookup.
        builders: dict[str, Callable[[], Denied]] = {}

        if mode_forbids(policy.operation_mode, locality):
            builders["mode_forbids_target"] = lambda: deny_mode_forbids_target(
                operation_mode=policy.operation_mode,
                model_target=request.model_target, file_ids=file_ids)

        if policy_revoked_for(self._conn, policy, scope):
            builders["policy_revoked"] = lambda: deny_policy_revoked(
                scope=scope, policy=policy, file_ids=file_ids)

        caught = self._precheck_items(request, protected=bool(protected_ids),
                                      sensitive_keys=sensitive_keys)
        if isinstance(caught, AlwaysLocalRequested):
            builders["always_local_item"] = lambda: deny_always_local_item(
                caught, file_ids=file_ids)
        elif isinstance(caught, ProtectedItemRequested):
            builders["protected_records_template"] = \
                lambda: deny_protected_records_template(
                    file_ids=file_ids, model_target=request.model_target)

        unclassified = tuple(sorted(
            file_id for file_id, name in classes.items()
            if name == UNREADABLE_UNCLASSIFIED))
        if unclassified and unclassified_denies(
                locality=locality,
                local_calls_on_unclassified=self._unclassified_permits_local):
            builders["unclassified"] = lambda: deny_unclassified(
                file_ids=unclassified, locality=locality,
                completeness=self._completeness(rows, unclassified[0]))

        if self._template_for is not None and any(
                is_protected_records(self._template_for(file_id))
                for file_id in file_ids):
            builders["protected_records_template"] = \
                lambda: deny_protected_records_template(
                    file_ids=file_ids, model_target=request.model_target)

        if protected_cloud_denies(protected=bool(protected_ids), locality=locality,
                                  operation_mode=policy.operation_mode, scope=scope,
                                  granted_scopes=granted):
            builders["protected_cloud_target"] = \
                lambda: deny_protected_cloud_target(
                    file_ids=protected_ids, operation_mode=policy.operation_mode,
                    scope=scope,
                    evidence_refs=(decisive.evidence_refs
                                   if decisive is not None else ()))

        chosen = first_reason(builders)
        if chosen is not None:
            return self._denied(builders[chosen](), request, policy, decisive,
                                hashes, observed_at)

        # 2 -- a question only the user can answer, asked only if nothing denied.
        text_items = tuple(item for item in request.requested_items
                           if isinstance(item, TEXT_BEARING))
        if text_items and protected_ids and scope not in granted:
            requirement = ConsentRequirement(
                file_ids=protected_ids,
                handling_class=classes[protected_ids[0]],
                items=tuple(kind_of(item) for item in text_items),
                why=("§8.4: this call needs text from files entered into protected "
                     f"state, and policy {policy.policy_version} holds no consent "
                     f"grant for scope {scope!r}"))
            return open_consent_request(
                self._conn, requirement, request=request, policy=policy,
                content_hashes=hashes, user_id=self._user_id,
                component_version=self._component_version, observed_at=observed_at)

        # 3 -- the only content read in the part.
        resolved, manifest = self._materialise(text_items)

        # 4 -- the two reasons that needed the resolved text.
        late: dict[str, Callable[[], Denied]] = {}
        caught = self._postcheck_items(request, resolved,
                                       protected=bool(protected_ids),
                                       sensitive_keys=sensitive_keys)
        if isinstance(caught, WholeDocumentRequested):
            late["whole_document_requested"] = \
                lambda: deny_whole_document_requested(caught, file_ids=file_ids)

        if self._measure_tokens is not None:
            measured = self._measure_tokens(request, resolved)
            if over_dossier_ceiling(self._conn, measured_tokens=measured):
                late["dossier_over_budget"] = lambda: deny_dossier_over_budget(
                    measured_tokens=measured,
                    ceiling=self._ceiling(), file_ids=file_ids)

        chosen = first_reason(late)
        if chosen is not None:
            return self._denied(late[chosen](), request, policy, decisive, hashes,
                                observed_at)

        # 5 -- the one write, before the value exists.
        audit_id = append_audit(
            self._conn,
            self._release_record(request, policy, classes, hashes, resolved,
                                 manifest, observed_at),
            author=SUBSYSTEM, component_version=self._component_version)

        # 6 -- the capability, recorded in Task 12's ledger and bound to three terms.
        release_id = mint_release(
            self._conn, policy=policy, model_target=request.model_target,
            prompt_fingerprint=request.prompt_fingerprint, audit_id=audit_id,
            minted_at=observed_at)

        return Released(
            release_id=release_id, audit_id=audit_id,
            policy_version=policy.policy_version, materialised_items=resolved,
            redaction_manifest=manifest, model_target=request.model_target)

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _decisive(records: Mapping[str, ClassificationRecord | None],
                  protected_ids: Sequence[str],
                  file_ids: Sequence[str]) -> ClassificationRecord | None:
        """The one record `record_denial` stores, which takes a single record.

        The first protected file if there is one, because that is the file the
        denial is about; otherwise the first target, whose record is `None` on the
        ordinary path and is exactly what `resolve_class` turns into
        `unreadable_unclassified`.
        """
        if protected_ids:
            return records[protected_ids[0]]
        return records[file_ids[0]]

    @staticmethod
    def _completeness(rows: Mapping[str, object], file_id: str) -> str | None:
        """P1 stores extraction status per tier; absent means nothing has run."""
        stored = rows[file_id]["extraction_status_by_tier"]
        return str(stored) if stored else None

    def _ceiling(self) -> int:
        """P1's stored ceiling, read for the denial's explanation only.

        Never `request.max_dossier_tokens`, which is "the caller's echo of it (M9)":
        a caller must not be able to raise its own ceiling by echoing a larger one.
        Reached only when `over_dossier_ceiling` already returned True, so the value
        is never `None` here; P7 invents no number for the case that cannot occur.
        """
        value = get_ceiling(self._conn, "model.max_dossier_tokens_per_call")
        if value is None:  # pragma: no cover - `over_dossier_ceiling` gated this
            raise AssertionError(
                "dossier_over_budget was reached with no ceiling stored; "
                "`over_dossier_ceiling` cannot return True in that state")
        return int(value)

    def _precheck_items(self, request: ModelCallRequest, *, protected: bool,
                        sensitive_keys) -> Exception | None:
        """Task 7's refusals that need no content. `unit_length=None` means unknown.

        `allow_unratified=True` because SPEC §4's flagged reading permits `filename`
        for non-protected files and denies it for protected ones; the denial is §7.3's
        and it arrives as `ProtectedItemRequested`, not as an unratified kind.
        """
        for item in request.requested_items:
            try:
                check_item(item, unit_length=None, protected=protected,
                           sensitive_keys=sensitive_keys, allow_unratified=True)
            except (AlwaysLocalRequested, ProtectedItemRequested) as caught:
                return caught
        return None

    def _postcheck_items(self, request: ModelCallRequest,
                         resolved: Sequence[Materialised], *, protected: bool,
                         sensitive_keys) -> Exception | None:
        """The one refusal that needs the resolved unit length."""
        lengths = {item.observation_key: item.unit_length for item in resolved}
        for item in request.requested_items:
            if not isinstance(item, TEXT_BEARING):
                continue
            try:
                check_item(item, unit_length=lengths.get(item.observation_key),
                           protected=protected, sensitive_keys=sensitive_keys,
                           allow_unratified=True)
            except WholeDocumentRequested as caught:
                return caught
        return None

    def _materialise(self, text_items: Sequence[object]
                     ) -> tuple[tuple[Materialised, ...], RedactionManifest]:
        """(observation_key, span) -> text -> redacted text. `resolve` is the only
        module under `src/privacy/` that binds a P4 text materialiser (L2)."""
        resolved: list[Materialised] = []
        entries = []
        for item in text_items:
            found = materialise(self._conn, item)
            value, entry = apply_redaction(
                found.value, observation_key=found.observation_key,
                span=found.span, context_before=found.context_before,
                context_after=found.context_after,
                context_truncated=found.context_truncated,
                classifier=self._classifier, transform=self._transform)
            resolved.append(Materialised(
                observation_key=found.observation_key, span=found.span, value=value,
                zone=found.zone, context_before=found.context_before,
                context_after=found.context_after,
                context_truncated=found.context_truncated,
                unit_length=found.unit_length))
            entries.append(entry)
        return tuple(resolved), RedactionManifest(entries=tuple(entries))

    def _release_record(self, request, policy, classes, hashes, resolved, manifest,
                        observed_at) -> AuditRecord:
        """SPEC §7's record for a release. `release_id` is None -- see the plan.

        §6 puts the append strictly BEFORE the release id exists, `mint_release`
        takes the `audit_id`, and `events` is append-only so the row cannot be
        back-filled. The join therefore runs ledger -> events, which is the
        direction Task 12 published the ledger's `audit_id` column for.
        """
        single = len(request.target.file_ids) == 1
        distinct = sorted(set(classes.values()))
        return AuditRecord(
            authorizing_policy=policy.policy_version,
            file_sensitivity=(distinct[0] if len(distinct) == 1
                              else canonical_json(distinct)),
            excerpts_included=tuple(
                (item.observation_key, item.span) for item in resolved),
            redaction_applied=manifest.any_redacted,
            model=request.model_target.to_mapping(),
            prompt_fingerprint=request.prompt_fingerprint,
            audit_id=None, release_id=None, observed_at=observed_at,
            stage=request.stage, file_ids=request.target.file_ids,
            group_id=request.target.group_id, content_hashes=hashes,
            operation_mode=policy.operation_mode,
            policy_version=policy.policy_version, plan_version=policy.plan_version,
            outcome="released",
            file_id=request.target.file_ids[0] if single else None,
            content_hash=hashes[0] if single else None,
            user_id=self._user_id,
            redaction_manifest=tuple(manifest.to_mapping()))

    def _denied(self, denied: Denied, request, policy, decisive, hashes,
                observed_at) -> Denied:
        """One `model_release_denied`, appended before the value is returned."""
        record_denial(self._conn, denied, request=request, policy=policy,
                      classification=decisive, content_hashes=hashes,
                      user_id=self._user_id,
                      component_version=self._component_version,
                      observed_at=observed_at)
        return denied
```

- [ ] **Step 6: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_release.py -v`

Expected: **PASS — 28 passed.**

- [ ] **Step 7: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`

Expected: **PASS** — Tasks 1–14 green, and P1–P5's 1300 collected tests still green.
`src/privacy/` still imports none of `extractors`' three refusals, and `src/privacy/gate.py` binds no
P4 text materialiser — `resolve` is still the only module that does, which Task 21 re-asserts
repo-wide.

- [ ] **Step 8: Commit `gate.py` and the test — this is commit 11-b**

```bash
git add src/privacy/gate.py tests/p7/test_p7_release.py
git commit -m "feat(P7): Gate.release, the three-branch union, and a signature with no override"
```

---

#### Reported by this task

| # | Finding | Who owns it |
|---|---|---|
| 1 | **The skeleton's `Denied` is missing `evidence_refs`.** Corrected here; SPEC §6 and Task 13's `deny` both require it. | closed here |
| 2 | **Task numbering is not a build order for 11–14.** The module graph is acyclic; the task graph is not. Executable order: `14, 11-a, 13, 12, 11-b`. | assembly |
| 3 | **SPEC §6 and SPEC §7 cannot both hold for `release_id`.** §6 puts the audit append strictly before the release exists; §7 lists `release_id` on the audit record; `events` is append-only so the row cannot be back-filled. Resolved by leaving `AuditRecord.release_id` `None` on a release record and joining ledger → events, the direction Task 12 built its `audit_id` column for. **Contract-out mismatch, not an implementation choice.** | Joseph / Task 10 |
| 4 | **Task 20's `GATE_ARGUMENTS` omits `template_for`**, so fixtures 4 and 16 (`Protected Records` residual) cannot be replayed through the real gate. One-line fixture change. | Task 20 |
| 5 | **Task 14's branch-disjointness assertion imports `release.Denied`**, so it needs 11-a first, or it moves here where `test_the_three_branches_share_no_field_name` already covers all three types. | Task 14 |
| 6 | **Tasks 15–18 each need a `Modify: src/privacy/gate.py` line** for the six remaining facade methods; their `Files` blocks omit it. Relevant to CUT 4. | Tasks 15–18 |
| 7 | **`SENSITIVE_CLASSES` is deliberately not published.** Naming the top two classes as "the sensitive ones" would answer NEEDS-JOSEPH **C5** in an implementation. The consent branch reads `ClassificationRecord.protected`, per SPEC §2's *"consume the `protected` flag, not infer it from the class."* | held open |
| 8 | **CUT 4 is unratified and this task is its target.** See the callout at the top. | Joseph |

---

### Task 12: Binding and single use

**Files:**
- Create: `src/privacy/binding.py`
- Modify: `src/privacy/schema.py` (execute `RELEASE_LEDGER_DDL`; Task 5 created the file)
- Test: `tests/p7/test_p7_binding.py`

**Interfaces:**
- Consumes: `privacy.release.Released` and `privacy.release.ModelTarget` (**annotation only** — see
  the import-direction section above), `privacy.release.RELEASED_FIELDS` (in the test),
  `privacy.policy.Policy`, `privacy.schema.create_privacy_schema(conn) -> None`,
  `evidence_shape.canonical.canonical_json(value) -> str`.
- Produces (`binding.py`):
  - `RELEASE_LEDGER_DDL: str` — the one table this task owns.
  - `BINDING_TERMS: tuple[str, str, str] = ("model_target", "prompt_fingerprint", "policy_version")`.
  - `mint_release(conn, *, policy, model_target, prompt_fingerprint, audit_id, minted_at) -> str`.
  - `consume_release(conn, released, *, model_target, prompt_fingerprint, policy_version) -> None`.
  - `ReleaseNotIssued`, `ReleaseAlreadySpent`, `BindingMismatch`.

**Done-means:** 5, and layer L1 of 3.

**This task is the whole of the sentence the part exists for.** *"A call that bypasses P7 is not a
policy violation to be caught in review — it is a call that cannot be constructed."* Nothing else in
P7 makes that true. The vocabularies can be respelled, the denials can be argued about, the audit
record can be reshaped — and the door still holds, because the token a transport must present is
minted in one function, recorded in one table, and spent once. The three tests that carry it are
`test_a_hand_constructed_released_is_inert`, `test_a_second_use_of_the_same_release_is_refused`, and
the three binding-mismatch tests. Everything else in the file is scaffolding for those five.

**Why the ledger is not a second job (C4).** The plan's own §3 L1 says the `release_id` is *"minted
by the gate and recorded in P7's ledger"*, so the row is sanctioned by the layer it belongs to. The
argument is the same one that puts the audit append inside the release decision: a capability that
is single-use has to have somewhere that records it was used, and that record is not a second
subject — it is the capability. What C4 forbids is the gate writing about *other parts' subjects*:
a classification, `files.sensitivity_state`, a `stage_output`, a placement decision, P8's `Refusal`.
The ledger row is about the release and nothing else.

**`mint_release` takes the `Policy`; `consume_release` takes the echoed `policy_version` string.**
This asymmetry is SPEC §6 made structural: *"the gate owns the policy, so the caller does not supply
this value, it echoes it."* The minter is inside the gate and holds the policy object; the consumer
is the transport, outside the gate, and can only echo. A `mint_release` that accepted a
`policy_version` string would let a caller stamp a release with a version that was never in force.
A test asserts both halves by `inspect.signature`.

**The spend is one atomic `UPDATE … WHERE spent_at IS NULL`, and a mismatch never spends.** Reading
the row, deciding, and then marking spent would leave a window between the decision and the mark.
`UPDATE … WHERE release_id = ? AND spent_at IS NULL` with `rowcount != 1` as the refusal collapses
check and mark into one statement, so single-use survives a second caller arriving between them.
And the binding is checked **before** the spend, never after: a call under the wrong model must not
burn the token, because burning it would let a mis-wired caller destroy an authorization the user
granted, and because a release that never reached a model must not be recorded as one that did.

**`audit_id` is carried and never compared.** SPEC §6: *"`audit_id` remains a field of `Released` —
it is what makes the record traceable — but it is not a binding term: two releases differing only in
audit record are the same authorization, while a release spent under a different policy version is
not."* The column exists so a ledger row can be joined back to its `events` row; the comparison is
driven by `BINDING_TERMS`, which has three members and does not contain it. The test constructs
exactly the pair SPEC §6 describes and shows both consume.

**`audit_id` is `NOT NULL`, and that is the ordering guarantee's last mile.** §6: *"the audit record
is appended (P1, §8.2) **before** `Released` is returned. There is no interval in which content is
releasable and unaudited."* `append_event` returns `cursor.lastrowid`, which exists only after the
row does, so a mint that has no `audit_id` to pass is a mint whose audit record was never written —
and SQLite refuses the row rather than P7 remembering to. The test proves it against the substrate,
by catching `sqlite3.IntegrityError`, not against P7's restraint.

**The `release_id` is `secrets.token_hex(16)` and the ledger, not the entropy, is the authority.**
A caller that holds a legitimate id can spend it; entropy does not change that. What entropy buys is
that a caller holding *one* id cannot enumerate its way to another one minted for a different call
in the same run. The unforgeability property is the ledger lookup — `ReleaseNotIssued` — and the
test says so in its own name.

**`spent_at` is the only wall-clock read in these three tasks, and it is reported.** The skeleton
fixes `consume_release`'s signature and it carries no clock, so the module reads one. That is
tolerable precisely because the ledger is not a fact: the authoritative time of a model call is the
audit record's `observed_at`, which the caller supplies, and nothing in P7 reads `spent_at` back as
evidence. Widening the published signature to take an `observed_at` would have been the alternative
and it was rejected because the signature is a contract with the Task 19/20 authors and with P8.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_binding.py
"""Done-means 5, and layer L1 of Done-means 3.

SPEC §6: "A release is consumed on first transport use." "The binding tuple is
(model_target, prompt_fingerprint, policy_version)." And the property the part
exists for: "a call that bypasses P7 is not a policy violation to be caught in
review -- it is a call that cannot be constructed."

The last one is testable in exactly one way and this file does it: build a
`Released` by hand, with a `release_id` the gate never minted, and show that
spending it fails. The dataclass is constructible. It is simply inert.
"""
import inspect
import sqlite3
from dataclasses import FrozenInstanceError

import pytest

from privacy.binding import (
    BINDING_TERMS, BindingMismatch, ReleaseAlreadySpent, ReleaseNotIssued,
    consume_release, mint_release,
)
from privacy.policy import Policy
from privacy.release import RELEASED_FIELDS, ModelTarget, Released

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
FINGERPRINT = "fp-1"
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
OTHER_CLOUD = ModelTarget(locality="cloud", model_id="acme-small", provider="Acme")
LOCAL = ModelTarget(locality="local", model_id="llama-3-8b", provider="local")

_TYPED_DEFAULTS = {
    "release_id": "release-never-minted",
    "audit_id": 1,
    "policy_version": "policy-1",
    "materialised_items": (),
    "redaction_manifest": (),
    "model_target": CLOUD,
}


def a_released(**over) -> Released:
    """Built from `RELEASED_FIELDS`, never from a literal keyword list.

    Task 11 owns SPEC §6's six field names. Constructing from the published tuple
    means a field this task never reads can be respelled without breaking it, while
    a field it DOES read disappearing fails here, at the seam that cares.
    """
    missing = [name for name in RELEASED_FIELDS if name not in _TYPED_DEFAULTS]
    assert not missing, (
        f"RELEASED_FIELDS names {missing} and this test has no value for them; "
        "SPEC §6 changed and Task 12 needs a value, not a default")
    values = {name: _TYPED_DEFAULTS[name] for name in RELEASED_FIELDS}
    values.update(over)
    return Released(**values)


def a_policy(**over) -> Policy:
    base = dict(policy_version="policy-1", operation_mode="cloud_assisted",
                consent_grants=(("Academics", "cloud_model"),),
                redaction_settings={"names": "redacted", "previews": "redacted",
                                    "thumbnails": "redacted", "ocr_text": "redacted",
                                    "location_data": "redacted"},
                automatic_move_permissions={}, plan_version="plan-1",
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


def mint(conn, *, policy=None, model_target=CLOUD, prompt_fingerprint=FINGERPRINT,
         audit_id=1, minted_at=FIXED_CLOCK) -> str:
    return mint_release(conn, policy=policy or a_policy(), model_target=model_target,
                        prompt_fingerprint=prompt_fingerprint, audit_id=audit_id,
                        minted_at=minted_at)


def spend(conn, released, **over) -> None:
    base = dict(model_target=CLOUD, prompt_fingerprint=FINGERPRINT,
                policy_version="policy-1")
    base.update(over)
    consume_release(conn, released, **base)


@pytest.fixture()
def minted(p7_conn) -> Released:
    """One live release, bound to CLOUD / fp-1 / policy-1."""
    return a_released(release_id=mint(p7_conn))


# --- minting ----------------------------------------------------------------

def test_a_minted_release_is_recorded_in_the_ledger(p7_conn, minted):
    row = p7_conn.execute("SELECT * FROM release_ledger WHERE release_id = ?",
                          (minted.release_id,)).fetchone()
    assert row is not None
    assert row["prompt_fingerprint"] == FINGERPRINT
    assert row["policy_version"] == "policy-1"
    assert row["audit_id"] == 1
    assert row["minted_at"] == FIXED_CLOCK
    assert row["spent_at"] is None


def test_two_mints_with_the_same_binding_get_different_ids(p7_conn):
    # The ledger is the authority and the entropy is not. What the entropy buys is
    # that a caller holding one id cannot walk to another one minted in the same run.
    first, second = mint(p7_conn), mint(p7_conn)
    assert first != second
    assert p7_conn.execute("SELECT count(*) c FROM release_ledger").fetchone()["c"] == 2


def test_a_mint_without_an_audit_record_is_refused_by_the_substrate(p7_conn):
    # SPEC §6's ordering guarantee, at its last mile: "the audit record is appended
    # ... BEFORE `Released` is returned." `append_event` returns `lastrowid`, which
    # exists only after the row does, so a mint with no audit_id is a mint whose
    # audit record was never written. SQLite refuses it; P7 does not have to remember.
    with pytest.raises(sqlite3.IntegrityError, match="NOT NULL"):
        mint(p7_conn, audit_id=None)


# --- single use -------------------------------------------------------------

def test_a_release_is_consumed_on_first_use(p7_conn, minted):
    # SPEC §6: "A release is consumed on first transport use."
    spend(p7_conn, minted)
    row = p7_conn.execute("SELECT spent_at FROM release_ledger WHERE release_id = ?",
                          (minted.release_id,)).fetchone()
    assert row["spent_at"] is not None


def test_a_second_use_of_the_same_release_is_refused(p7_conn, minted):
    spend(p7_conn, minted)
    with pytest.raises(ReleaseAlreadySpent):
        spend(p7_conn, minted)


def test_consuming_writes_no_event(p7_conn, minted):
    # C4: the gate writes its audit record and nothing else. The spend is a state
    # change on P7's own capability row, not a second entry in the one log; Task 10's
    # `model_release` is the record that a call was authorized.
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    spend(p7_conn, minted)
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before


# --- the three binding terms, one test each ---------------------------------

def test_a_different_model_target_is_refused(p7_conn, minted):
    # §8.4's audit record must show "which model received the data". A payload
    # replayable against another model makes that field false.
    replayed = a_released(release_id=minted.release_id, model_target=OTHER_CLOUD)
    with pytest.raises(BindingMismatch):
        spend(p7_conn, replayed, model_target=OTHER_CLOUD)


def test_a_different_prompt_fingerprint_is_refused(p7_conn, minted):
    # §8.4's sixth audit field is "the prompt fingerprint"; B2 puts `call_site`
    # inside it, so one fingerprint is one call site and one prompt.
    with pytest.raises(BindingMismatch):
        spend(p7_conn, minted, prompt_fingerprint="fp-2")


def test_a_different_policy_version_is_refused(p7_conn, minted):
    # SPEC §6: "a release spent under a different policy version is not [the same
    # authorization]". This is the term that makes revocation forward-only rather
    # than retroactive -- see the policy-change test below.
    with pytest.raises(BindingMismatch):
        spend(p7_conn, a_released(release_id=minted.release_id,
                                  policy_version="policy-2"),
              policy_version="policy-2")


def test_a_binding_mismatch_does_not_spend_the_release(p7_conn, minted):
    # A mis-wired caller must not be able to destroy an authorization the user
    # granted, and a release that never reached a model must not be recorded as one
    # that did. The binding is checked before the spend, never after.
    with pytest.raises(BindingMismatch):
        spend(p7_conn, minted, prompt_fingerprint="fp-2")
    assert p7_conn.execute(
        "SELECT spent_at FROM release_ledger WHERE release_id = ?",
        (minted.release_id,)).fetchone()["spent_at"] is None
    spend(p7_conn, minted)


def test_a_released_whose_echo_disagrees_with_the_call_is_refused(p7_conn, minted):
    # `Released` echoes `model_target` and `policy_version` (SPEC §6). If the echo
    # and the checked binding could disagree, one of the audit record's two fields
    # would be false for whichever the transport actually used.
    with pytest.raises(BindingMismatch):
        consume_release(p7_conn, a_released(release_id=minted.release_id,
                                            model_target=LOCAL),
                        model_target=CLOUD, prompt_fingerprint=FINGERPRINT,
                        policy_version="policy-1")


# --- audit_id is not a binding term -----------------------------------------

def test_the_binding_terms_are_the_specs_three(p7_conn):
    assert BINDING_TERMS == ("model_target", "prompt_fingerprint", "policy_version")
    assert "audit_id" not in BINDING_TERMS


def test_two_releases_differing_only_in_audit_record_both_consume(p7_conn):
    # SPEC §6, constructed exactly: "two releases differing only in audit record are
    # the same authorization".
    first = a_released(release_id=mint(p7_conn, audit_id=11), audit_id=11)
    second = a_released(release_id=mint(p7_conn, audit_id=12), audit_id=12)
    spend(p7_conn, first)
    spend(p7_conn, second)


def test_every_binding_term_is_a_ledger_column(p7_conn):
    # The comparison is driven by BINDING_TERMS. A fourth term added to the tuple
    # without a column to hold it fails here rather than silently comparing nothing.
    columns = {row[1] for row in p7_conn.execute("PRAGMA table_xinfo(release_ledger)")}
    assert set(BINDING_TERMS) <= columns


# --- unforgeability ---------------------------------------------------------

def test_a_hand_constructed_released_is_inert(p7_conn):
    # THE test. "A call that bypasses P7 is not a policy violation to be caught in
    # review -- it is a call that cannot be constructed."
    with pytest.raises(ReleaseNotIssued):
        spend(p7_conn, a_released(release_id="release-deadbeef"))


def test_constructing_a_released_is_permitted_and_useless(p7_conn):
    # The dataclass is not defended and does not need to be. Instantiating it is a
    # normal Python act that buys nothing, which is a stronger property than a
    # constructor that raises: nothing has to guess where the caller came from.
    forged = a_released(release_id="release-deadbeef")
    assert forged.release_id == "release-deadbeef"
    with pytest.raises(FrozenInstanceError):
        forged.release_id = "release-something-else"
    assert p7_conn.execute(
        "SELECT count(*) c FROM release_ledger WHERE release_id = ?",
        ("release-deadbeef",)).fetchone()["c"] == 0


def test_a_refused_consume_leaves_the_ledger_untouched(p7_conn, minted):
    before = p7_conn.execute("SELECT count(*) c FROM release_ledger").fetchone()["c"]
    with pytest.raises(ReleaseNotIssued):
        spend(p7_conn, a_released(release_id="release-deadbeef"))
    assert p7_conn.execute(
        "SELECT count(*) c FROM release_ledger").fetchone()["c"] == before


# --- the policy-version term is what makes revocation forward-only ----------

def test_a_release_minted_before_a_policy_change_still_consumes_against_its_own_version(p7_conn):
    # Task 15's `revoke` mints a new policy version and asserts `effective_from`
    # affects "future gate calls only". That property lives HERE: the ledger row
    # carries the version the release was minted under, so a token issued before the
    # revocation is still spendable against policy-1, while a call presented under
    # policy-2 is a different authorization. The other half -- that a request made
    # AFTER the revocation denies with `policy_revoked` -- is Task 13's.
    early = a_released(release_id=mint(p7_conn, policy=a_policy(policy_version="policy-1")))
    spend(p7_conn, early, policy_version="policy-1")
    late = a_released(release_id=mint(p7_conn, policy=a_policy(policy_version="policy-1")))
    with pytest.raises(BindingMismatch):
        spend(p7_conn, a_released(release_id=late.release_id,
                                  policy_version="policy-2"),
              policy_version="policy-2")


# --- shape ------------------------------------------------------------------

def test_mint_takes_the_policy_and_consume_takes_the_echo():
    # SPEC §6: "the gate owns the policy, so the caller does not supply this value,
    # it echoes it." The minter is inside the gate and holds the object; the
    # transport is outside it and can only echo a string.
    minting = inspect.signature(mint_release).parameters
    assert "policy" in minting and "policy_version" not in minting
    spending = inspect.signature(consume_release).parameters
    assert "policy_version" in spending and "policy" not in spending


def test_the_ledger_holds_no_content(p7_conn):
    # `excerpts_included` is "(observation_key, span) pairs ... not a second copy of
    # the text" (SPEC §7). A ledger that stored the payload would be that second
    # copy, in a table with no reason to have one.
    columns = {row[1] for row in p7_conn.execute("PRAGMA table_xinfo(release_ledger)")}
    assert columns == {"release_id", "model_target", "prompt_fingerprint",
                       "policy_version", "audit_id", "minted_at", "spent_at"}


def test_consume_release_is_the_only_spender():
    # Repo-wide, this is Task 21's. Here it is the module's own namespace: there is
    # no second function in `binding` that can mark a release spent.
    import privacy.binding as module
    published = {name for name, value in vars(module).items()
                 if not name.startswith("_") and callable(value)
                 and getattr(value, "__module__", None) == module.__name__}
    assert published == {"mint_release", "consume_release", "ReleaseNotIssued",
                         "ReleaseAlreadySpent", "BindingMismatch"}


def test_p7_adds_no_delete_trigger_to_its_own_ledger(p7_conn):
    # Task 15 counts the tables carrying `BEFORE DELETE ... RAISE(ABORT)` and asserts
    # THIRTEEN. A fourteenth here would fail a sibling task. §8.2's R6 binds `events`;
    # the ledger is a capability record and P7 does not extend R6 by imitation.
    triggers = {row["name"] for row in p7_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'trigger' "
        "AND tbl_name = 'release_ledger'")}
    assert triggers == set()
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_binding.py -v`
Expected: FAIL — `ImportError: cannot import name 'BINDING_TERMS' from 'privacy.binding'` (the
module does not exist yet, so collection fails on the first import).

- [ ] **Step 3: Write `src/privacy/binding.py`**

```python
# src/privacy/binding.py
"""The release ledger: what makes `Released` a capability rather than a value.

SPEC §6 states the property and the reason in one breath: "Binding and single use
exist to keep the audit record truthful. §8.4 requires the record to show *which
model received the data* and *the prompt fingerprint*; a payload that could be
replayed against a different model or under a different prompt would make both
fields false. A release is consumed on first transport use."

Three decisions, each forced rather than chosen:

- **The ledger is the authority, not the entropy.** `ReleaseNotIssued` is what makes
  a hand-constructed `Released` inert, and it is a lookup. The 128 bits are so that a
  caller holding one id cannot enumerate its way to another minted in the same run.
- **The binding is checked before the spend, and a mismatch spends nothing.** A
  mis-wired caller must not be able to burn an authorization the user granted, and a
  release that never reached a model must not be recorded as one that did.
- **`audit_id` is carried and never compared.** SPEC §6: "two releases differing only
  in audit record are the same authorization, while a release spent under a different
  policy version is not." It is `NOT NULL` because `append_event` returns
  `cursor.lastrowid`, which exists only after the audit row does -- so a mint with no
  audit_id is a mint whose audit record was never written, and SQLite refuses it.

This module imports `privacy.release` under `TYPE_CHECKING` only. It never constructs
a `Released` -- `mint_release` returns a `str` and the facade builds the value -- so
the need for the type is annotation-only, and the guard is what lets `release.py`
import nothing from here while `gate.py` imports both.
"""
from __future__ import annotations

import dataclasses
import secrets
import sqlite3
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from evidence_shape.canonical import canonical_json

from privacy.policy import Policy

if TYPE_CHECKING:  # pragma: no cover - annotation only; see the module docstring
    from privacy.release import ModelTarget, Released

#: SPEC §6, B2: "The binding tuple is (model_target, prompt_fingerprint,
#: policy_version)." Three terms, and `audit_id` is deliberately not one.
BINDING_TERMS: tuple[str, str, str] = (
    "model_target", "prompt_fingerprint", "policy_version",
)

#: P7's third table, inside P1's single local database (§0). No `BEFORE DELETE`
#: trigger: §8.2's R6 binds `events`, and this is a capability record, not a
#: provenance record. Task 15 counts the guarded tables and asserts thirteen.
RELEASE_LEDGER_DDL: str = """
CREATE TABLE IF NOT EXISTS release_ledger (
    release_id         TEXT PRIMARY KEY,
    model_target       TEXT NOT NULL,
    prompt_fingerprint TEXT NOT NULL,
    policy_version     TEXT NOT NULL,
    audit_id           INTEGER NOT NULL,
    minted_at          TEXT NOT NULL,
    spent_at           TEXT
);
"""


class ReleaseNotIssued(Exception):
    """The `release_id` is not in the ledger, so the gate never minted it.

    This is the refusal that makes the door real. A caller may construct a
    `Released` -- it is an ordinary frozen dataclass -- and doing so buys nothing.
    """


class ReleaseAlreadySpent(Exception):
    """SPEC §6: "A release is consumed on first transport use.\""""


class BindingMismatch(Exception):
    """The call does not match the terms the release was minted under.

    Raised before the spend and never after, so a mismatched call leaves the
    authorization intact.
    """


def _target_form(model_target: ModelTarget) -> str:
    """One stored form per model target.

    `canonical_json` over `dataclasses.asdict` rather than `str()`: §8.4's audit
    field is "which model received the data", and a hosted model is identified by
    provider AND id. A form that dropped either would let two different targets
    compare equal.
    """
    return canonical_json(dataclasses.asdict(model_target))


def _utcnow() -> str:
    """The ledger's own clock.

    The published `consume_release` signature carries no `observed_at`, and it is a
    contract with P8's transport. That is tolerable because `spent_at` is not a fact:
    the authoritative time of a model call is the audit record's `observed_at`, which
    the caller supplies, and nothing in P7 reads this column back as evidence.
    """
    return datetime.now(timezone.utc).isoformat()


def mint_release(conn: sqlite3.Connection, *, policy: Policy,
                 model_target: ModelTarget, prompt_fingerprint: str,
                 audit_id: int, minted_at: str) -> str:
    """Record one authorization and return its single-use id.

    Takes the `Policy` object, not a `policy_version` string: SPEC §6 says "the gate
    owns the policy, so the caller does not supply this value, it echoes it", and the
    minter is inside the gate. `consume_release` takes the echo.
    """
    release_id = "release-" + secrets.token_hex(16)
    conn.execute(
        "INSERT INTO release_ledger (release_id, model_target, prompt_fingerprint, "
        "policy_version, audit_id, minted_at, spent_at) "
        "VALUES (?, ?, ?, ?, ?, ?, NULL)",
        (release_id, _target_form(model_target), prompt_fingerprint,
         policy.policy_version, audit_id, minted_at),
    )
    return release_id


def consume_release(conn: sqlite3.Connection, released: Released, *,
                    model_target: ModelTarget, prompt_fingerprint: str,
                    policy_version: str) -> None:
    """Spend one release, once, against the terms it was minted under.

    Order: issued, then bound, then spent. Checking the binding after the spend
    would burn a token on a call that was never authorized for that model, and
    would report "already spent" for what is really a forgery-shaped event.
    """
    row = conn.execute("SELECT * FROM release_ledger WHERE release_id = ?",
                       (released.release_id,)).fetchone()
    if row is None:
        raise ReleaseNotIssued(
            f"{released.release_id!r} is not in the release ledger; the gate never "
            "minted it. A `Released` constructed outside `Gate.release` carries no "
            "authorization -- SPEC §6, and the reason a bypassing call cannot be "
            "constructed rather than merely being disallowed"
        )
    call = {
        "model_target": _target_form(model_target),
        "prompt_fingerprint": prompt_fingerprint,
        "policy_version": policy_version,
    }
    differing = [term for term in BINDING_TERMS if row[term] != call[term]]
    if differing:
        raise BindingMismatch(
            f"{released.release_id!r} was minted under different {differing}; SPEC §6 "
            "binds a release to (model_target, prompt_fingerprint, policy_version) so "
            "that §8.4's 'which model received the data' and 'the prompt fingerprint' "
            "stay true of the call that actually happened"
        )
    echoed = {
        "model_target": _target_form(released.model_target),
        "policy_version": released.policy_version,
    }
    disagreeing = [term for term, value in echoed.items() if call[term] != value]
    if disagreeing:
        raise BindingMismatch(
            f"{released.release_id!r} echoes {disagreeing} that the call does not "
            "use; the echo and the binding must agree or one of §8.4's audit fields "
            "is false for whichever the transport actually used"
        )
    spent = conn.execute(
        "UPDATE release_ledger SET spent_at = ? "
        "WHERE release_id = ? AND spent_at IS NULL",
        (_utcnow(), released.release_id),
    )
    if spent.rowcount != 1:
        raise ReleaseAlreadySpent(
            f"{released.release_id!r} was already consumed; SPEC §6: 'A release is "
            "consumed on first transport use.' The check and the mark are one "
            "statement so that single use survives a second caller arriving between "
            "them"
        )
```

- [ ] **Step 4: Add the ledger to `src/privacy/schema.py`**

Task 5 created `create_privacy_schema(conn)` and it is the one place P7's schema is applied, so a
caller does not have to know which modules own tables. The DDL text stays with the module that owns
the table's semantics; `schema.py` executes it. The import direction is `schema` → `binding`, which
is acyclic because `binding` imports nothing from `schema`.

Two lines are added to Task 5's file and nothing else in it changes — the import at module
level, and the execution inside `create_privacy_schema`, alongside Task 5's own policy and
consent-grant tables:

```text
src/privacy/schema.py

  module level, with the other imports
      from privacy.binding import RELEASE_LEDGER_DDL

  inside create_privacy_schema(conn), after Task 5's own executescript calls
      # Task 12's ledger is what makes `Released` single-use (SPEC §6).
      conn.executescript(RELEASE_LEDGER_DDL)
```

- [ ] **Step 5: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_binding.py -v`
Expected: PASS — 22 passed

- [ ] **Step 6: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–12 green, and the 1302 P1–P5 tests still green (P7 modified no file
belonging to another part).

- [ ] **Step 7: Commit**

```bash
git add src/privacy/binding.py src/privacy/schema.py tests/p7/test_p7_binding.py
git commit -m "feat(P7): the release ledger, its three binding terms, and single use"
```

---

---

### Task 13: The eight denials

**Files:**
- Create: `src/privacy/denial.py`
- Test: `tests/p7/test_p7_denials.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.DENIAL_REASONS`, `.check_denial_reason(value) -> str`,
  `.OutOfVocabulary`, `privacy.classification.ClassificationRecord`,
  `.resolve_class(record) -> str`, `privacy.policy.Policy`,
  `privacy.items.AlwaysLocalRequested`, `.WholeDocumentRequested`,
  `privacy.audit.AuditRecord`, `.AUDIT_FIELDS`,
  `.append_audit(conn, record, *, author, component_version) -> int`,
  `privacy.authorship.SUBSYSTEM`, `privacy.release.Denied` (run time — see the import-direction
  section), `database_agent.budget.get_ceiling(conn, key) -> int | None`,
  `evidence_shape.canonical.canonical_json(value) -> str`.
- Produces (`denial.py`):
  - `PROTECTED_RECORDS_TEMPLATE: str = "Protected Records"` — §7.3's literal name.
  - `REVOKED_SCOPE_KEY: str = "scope"` — the key Task 15's `revoke` writes into `explanation`.
  - `DENIAL_ORDER: tuple[str, ...]` — the eight, in evaluation order.
  - `DECIDABLE_FROM_REQUEST: frozenset[str]` — the six that need no content read.
  - `RemedyOption` — frozen: `action: str`, `detail: str`.
  - `MalformedDenial(ValueError)`.
  - `deny(reason, *, explanation, remedy_options, evidence_refs) -> Denied`.
  - `first_reason(reasons) -> str | None`.
  - Predicates: `mode_forbids(operation_mode, locality) -> bool`,
    `policy_revoked_for(conn, policy, scope) -> bool`,
    `unclassified_denies(*, locality, local_calls_on_unclassified) -> bool`,
    `is_protected_records(template_name) -> bool`,
    `protected_cloud_denies(*, protected, locality, operation_mode, scope, granted_scopes) -> bool`,
    `over_dossier_ceiling(conn, *, measured_tokens) -> bool`.
  - Eight builders: `deny_mode_forbids_target`, `deny_policy_revoked`, `deny_always_local_item`,
    `deny_unclassified`, `deny_protected_records_template`, `deny_protected_cloud_target`,
    `deny_whole_document_requested`, `deny_dossier_over_budget`.
  - `record_denial(conn, denied, *, request, policy, classification, content_hashes, user_id,
    component_version, observed_at) -> int`.

**Done-means:** 6.

**This is the ordinary path and it is written as one.** The detector is unwritten (D2). No task in
any plan produces a rule set. So on a real corpus, `Gate.release` is asked about a file with no
`ClassificationRecord`, `resolve_class(None)` returns `unreadable_unclassified`, and the call is
**denied**. That is not a degraded mode; it is what a correct locked door does when nobody has been
given a key. The consequences run through this whole task: `deny_unclassified` gets the longest
explanation and the most remedy options; the `unclassified` test is the one that also proves absence
never resolves to `public_low`; and the audit-record test uses an unclassified file, because that is
what the audit log will actually be full of.

**The eight reasons need a total order, and it is `DENIAL_ORDER`.** The skeleton requires eight
tests *"each reaching **exactly** that reason and no other"*, and four of the eight overlap on real
inputs — a protected file with a cloud target under `offline` satisfies both `mode_forbids_target`
and `protected_cloud_target`; an unclassified protected file satisfies `unclassified` and
`protected_cloud_target`; a `Protected Records` file satisfies both of the latter. "Exactly one" is
unmeetable without saying which wins. The order and the reason for each position:

```text
1  mode_forbids_target          the mode is outermost. §8.4: offline is "No content leaves the
                                device"; a cloud target is refused before anything about the file
                                is consulted. This is also Done-means 13's asserted reason.
2  policy_revoked               with no authorizing policy for the scope there is nothing to
                                evaluate the remaining rules against.
3  always_local_item            §8.4: "Nothing in this set can be named as a releasable item kind."
                                Decidable from the item kind, and true of every file.
4  unclassified                 §8.4 makes classification "a precondition of escalation". With no
                                record there is no `protected` flag to read, so every rule below
                                this line is literally unevaluable above it.
5  protected_records_template   §7.3 binds LOCAL calls too, so it must precede the cloud rule or a
                                local call on a Protected Records file would pass.
6  protected_cloud_target       protected + cloud, under a mode that otherwise permits cloud.
7  whole_document_requested     needs the resolved unit length, so it is the first rule that
                                requires the file's content.
8  dossier_over_budget          M9's backstop, last: P8 measured and ran its ladder before calling.
```

**The principle that orders them, and `DECIDABLE_FROM_REQUEST` is it in data form: no denial that
can be decided from the request alone may be decided after one that requires reading the file.**
A gate that materialised an excerpt and *then* discovered the mode forbade the call has read a
sensitive file for a call that was never going to happen. Six of the eight are decidable from the
request, the policy and a row lookup; two — `whole_document_requested` and `dossier_over_budget` —
need the resolved text. A test asserts every member of the first set precedes every member of the
second, so a future reordering that puts a content-reading check first is a red test.

**Every denial appends exactly one `model_release_denied`, and the gate writes nothing else.** The
audit obligation is §8.2's *"Every significant event affecting a file should be preserved in an
append-only provenance log"* and SPEC §7's *"Denials and consent requests are also appended."* The
builders are pure and the append is one function, because the audit record needs the request and the
policy and a builder sees neither; a builder that took them would compose SPEC §7's record eight
times over, and Task 10 owns that record once. `Gate.release` calls a builder and then
`record_denial`; that wiring is Task 11's.

**`AuditRecord.file_sensitivity` is where `unreadable_unclassified` belongs, and
`files.sensitivity_state` is where it must never appear.** D2: *"`Unreadable or unclassified` is a
GATE OUTCOME, not a file fact. It lives on the release decision and never in that column, so
'nothing has looked' can never be read as 'this file carries nothing'."* `record_denial` computes
the field with `classification.resolve_class(record)` — the same function, so the outcome is not
re-derived — and one test asserts the column is exactly as the denial found it. That test proves C4
and D2 with one assertion, which is why it is written as one test and not two.

**`dossier_over_budget` reads P1's ceiling and counts no tokens.** `get_ceiling(conn,
"model.max_dossier_tokens_per_call")` returns `int | None`, and `None` is the ordinary state.
**An unset ceiling cannot deny**, because P7 owns no number: SPEC *Deferred* puts every numeric
ceiling outside this contract and Task 21 asserts none appears in `src/privacy/`. The size itself is
the **caller's** measurement, passed as `measured_tokens` with no default, for the same reason the
redaction transform is injected with no default — P7 has no tokenizer and inventing one would invent
a number. And the check reads P1's stored ceiling, never `request.max_dossier_tokens`, which is only
*"the caller's echo of it (M9)"*: a caller must not be able to raise its own ceiling by echoing a
larger one. Its test says in its own docstring that this denial is **an M9 backstop that should
never fire in a correct pipeline**, so a later reader does not delete the check on the grounds that
P8 already ran the ladder.

**`policy_revoked` is "granted and then withdrawn", not "never granted".** Never-granted is
`protected_cloud_target` or `mode_forbids_target`, and its remedy is *ask*. Withdrawn is a different
fact with a different remedy and §8.7's negative-feedback rule attached — the user has already said
no once, so the option is offered and never re-proposed automatically. The predicate is therefore
two-sided: the current policy carries no grant for the scope **and** the log holds a
`consent_revoked` for it. A re-grant puts the scope back in `policy.consent_grants` and the denial
stops firing, which is what makes revocation forward-only rather than permanent. The scope is read
from the `consent_revoked` explanation under the key `"scope"` — verified against the written
[`PLAN-tasks-15-16.md`](PLAN-tasks-15-16.md), where `revoke` composes
`canonical_json({"scope": scope, "revoked_policy_version": …})` — and pinned as
`REVOKED_SCOPE_KEY` so a rename is a red test on both sides.

**`unclassified_denies` is parameterised on locality and the parameter has no default.** Open
question 5: *"Does `unreadable_unclassified` permit a *local* model call? … Reading escalation
strictly denies local calls on unclassified files, which may block exactly the OCR-opaque
screenshots §2.7 and §7.8 want a model to interpret."* Unanswered, so
`local_calls_on_unclassified` is a required keyword and calling without it is a `TypeError` the
test asserts. P7 supplies no answer and Task 21 holds the question open.

**`always_local_item` and `whole_document_requested` are translations, not re-derivations.** Task 7
refuses those at construction with `AlwaysLocalRequested` and `WholeDocumentRequested`. Task 13's two
builders take the caught exception and turn it into the gate's `Denied`, so the rule lives in one
place and the gate's answer carries the item that failed. A builder that re-decided which names are
always-local would be a second copy of §8.4's nine.

**Remedy options are composed per denial and are deliberately not a closed vocabulary.** §8.6 names
four ladder rungs for an over-budget dossier; §8.4 names four consent options for a sensitive text
request; §8.6 names deferral and review for an exhausted budget. Collapsing those into one
`REMEDY_ACTIONS` tuple would invent a fifth thing that no section states. `denial.py` publishes no
such enumeration and Task 21 asserts none exists. What is enforced is presence: §8.6 requires the UI
to show *"what has been deferred, and why"*, and a denial with no legitimate alternative is a dead
end the user cannot act on, so `deny` refuses an empty `remedy_options`.

**M14 is not re-checked here.** `Denied.evidence_refs` carries whatever the classification carried,
and the observation-key-versus-id rule is Task 3's on `ClassificationRecord.evidence_refs`. `deny`
validates that each ref is a non-empty string and no more; a second copy of M14's shape rule is a
second place for it to drift.

**One finding for Task 10, reported rather than worked around.** `events` has one `file_id` column,
so a group-scoped denial cannot put all of its files in it. `record_denial` sets the column when the
call is about exactly one file and always stores the full tuple as `file_ids` in the explanation
JSON. **`audit_records_for(conn, file_id=…)` must therefore match the explanation's `file_ids` and
not only the column**, or Task 15's `prior_releases` under-reports every group-scoped release.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_denials.py
"""Done-means 6 -- all eight reasons, and the one that is the ordinary case.

The detector is unwritten (D2), so on a real corpus every file resolves to
`Denied(unclassified)`. This file is written for that: `unclassified` gets the
longest section, and the audit-record tests run against an unclassified file
because that is what the log will actually be full of.

SPEC §6's eight: protected_cloud_target | unclassified | policy_revoked |
protected_records_template | whole_document_requested | dossier_over_budget |
always_local_item | mode_forbids_target.
"""
import json

import pytest

from database_agent.budget import CEILING_KEYS, set_ceiling
from database_agent.events import append_event
from database_agent.files_table import get_file, record_file

from privacy.audit import AUDIT_FIELDS, audit_record
from privacy.authorship import CONSENT_REVOKED, MODEL_RELEASE_DENIED, SUBSYSTEM
from privacy.classification import ClassificationRecord
from privacy.denial import (
    DECIDABLE_FROM_REQUEST, DENIAL_ORDER, PROTECTED_RECORDS_TEMPLATE,
    REVOKED_SCOPE_KEY, MalformedDenial, RemedyOption, deny,
    deny_always_local_item, deny_dossier_over_budget, deny_mode_forbids_target,
    deny_policy_revoked, deny_protected_cloud_target,
    deny_protected_records_template, deny_unclassified,
    deny_whole_document_requested, first_reason, is_protected_records,
    mode_forbids, over_dossier_ceiling, policy_revoked_for,
    protected_cloud_denies, record_denial, unclassified_denies,
)
from privacy.items import AlwaysLocalRequested, WholeDocumentRequested
from privacy.policy import Policy
from privacy.release import REQUEST_FIELDS, Denied, ModelCallRequest, ModelTarget, Target
from privacy.vocabulary import DENIAL_REASONS, OutOfVocabulary

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"
CEILING_KEY = "model.max_dossier_tokens_per_call"
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
LOCAL = ModelTarget(locality="local", model_id="llama-3-8b", provider="local")
DETECTOR_KEYS = (
    "sha256:ba9777bcba0096decc525198035644949d2357bf7f9a9cb3492c948c86c0fcbd",
)

_REQUEST_DEFAULTS = {
    "stage": "grouping",
    "target": Target(file_ids=("file-1",), group_id=None),
    "model_target": CLOUD,
    "requested_items": (),
    "prompt_template_id": "template-1",
    "prompt_fingerprint": "fp-1",
    "max_dossier_tokens": 4000,
}


def a_request(**over) -> ModelCallRequest:
    """Built from `REQUEST_FIELDS`; Task 11 owns SPEC §6's seven names."""
    missing = [name for name in REQUEST_FIELDS if name not in _REQUEST_DEFAULTS]
    assert not missing, (
        f"REQUEST_FIELDS names {missing} and this test has no value for them; "
        "SPEC §6 changed and Task 13 needs a value, not a default")
    values = {name: _REQUEST_DEFAULTS[name] for name in REQUEST_FIELDS}
    values.update(over)
    return ModelCallRequest(**values)


def a_policy(**over) -> Policy:
    base = dict(policy_version="policy-1", operation_mode="cloud_assisted",
                consent_grants=(("Academics", "cloud_model"),),
                redaction_settings={"names": "redacted", "previews": "redacted",
                                    "thumbnails": "redacted", "ocr_text": "redacted",
                                    "location_data": "redacted"},
                automatic_move_permissions={}, plan_version="plan-1",
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


@pytest.fixture()
def file_id(p7_conn, tmp_path) -> str:
    """A real P1 row, because the denial must be shown NOT to write to it."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    document = corpus / "passport-scan.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    return record_file(
        p7_conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


def all_eight() -> dict[str, Denied]:
    """One built `Denied` per reason, so the audit test can parameterise over them."""
    return {
        "mode_forbids_target": deny_mode_forbids_target(
            operation_mode="offline", model_target=CLOUD, file_ids=("file-1",)),
        "policy_revoked": deny_policy_revoked(
            scope="Academics", policy=a_policy(consent_grants=()),
            file_ids=("file-1",)),
        "always_local_item": deny_always_local_item(
            AlwaysLocalRequested("GPS"), file_ids=("file-1",)),
        "unclassified": deny_unclassified(
            file_ids=("file-1",), locality="cloud", completeness=None),
        "protected_records_template": deny_protected_records_template(
            file_ids=("file-1",), model_target=LOCAL),
        "protected_cloud_target": deny_protected_cloud_target(
            file_ids=("file-1",), operation_mode="hybrid", scope="Academics",
            evidence_refs=DETECTOR_KEYS),
        "whole_document_requested": deny_whole_document_requested(
            WholeDocumentRequested("span 0-4096 covers the whole unit"),
            file_ids=("file-1",)),
        "dossier_over_budget": deny_dossier_over_budget(
            measured_tokens=9000, ceiling=4000, file_ids=("file-1",)),
    }


# --- the order, and the principle behind it ---------------------------------

def test_denial_order_is_a_permutation_of_the_vocabulary():
    assert set(DENIAL_ORDER) == set(DENIAL_REASONS)
    assert len(DENIAL_ORDER) == len(DENIAL_REASONS) == 8


def test_nothing_that_needs_content_is_decided_before_something_that_does_not():
    # The principle: a gate that materialised an excerpt and THEN discovered the mode
    # forbade the call has read a sensitive file for a call that was never going to
    # happen. Six reasons are decidable from the request; two need the resolved text.
    assert DECIDABLE_FROM_REQUEST < set(DENIAL_REASONS)
    needs_content = set(DENIAL_REASONS) - DECIDABLE_FROM_REQUEST
    assert needs_content == {"whole_document_requested", "dossier_over_budget"}
    last_cheap = max(DENIAL_ORDER.index(r) for r in DECIDABLE_FROM_REQUEST)
    first_costly = min(DENIAL_ORDER.index(r) for r in needs_content)
    assert last_cheap < first_costly


def test_dossier_over_budget_is_last():
    # M9: P8 measures and runs §8.6's ladder BEFORE calling. The gate is "the last
    # place to catch a caller that skipped its ladder", so it is checked last.
    assert DENIAL_ORDER[-1] == "dossier_over_budget"


def test_first_reason_returns_none_when_nothing_triggered():
    assert first_reason(()) is None
    assert first_reason(set()) is None


def test_mode_outranks_protected_cloud_target():
    # The negative-tests table: protected + cloud under `offline` or `local_model` is
    # `mode_forbids_target`, not `protected_cloud_target`. The mode is outermost.
    assert first_reason({"protected_cloud_target", "mode_forbids_target"}) == \
        "mode_forbids_target"


def test_unclassified_outranks_protected_cloud_target():
    # §8.4 makes classification "a precondition of escalation". With no record there
    # is no `protected` flag to read, so the rule below is literally unevaluable.
    assert first_reason({"protected_cloud_target", "unclassified"}) == "unclassified"


def test_protected_records_template_outranks_protected_cloud_target():
    # §7.3 binds local calls too, so it must precede the cloud-only rule.
    assert first_reason({"protected_cloud_target", "protected_records_template"}) == \
        "protected_records_template"


# --- 1. mode_forbids_target -------------------------------------------------

def test_mode_forbids_target_under_offline_and_local_model():
    # §8.4: "Fully offline mode: No content leaves the device; only local rules and
    # local models may run." A local model is permitted under both; a cloud one is not.
    assert mode_forbids("offline", "cloud") is True
    assert mode_forbids("local_model", "cloud") is True
    assert mode_forbids("offline", "local") is False
    assert mode_forbids("local_model", "local") is False
    assert mode_forbids("hybrid", "cloud") is False
    assert mode_forbids("cloud_assisted", "cloud") is False
    assert deny_mode_forbids_target(operation_mode="offline", model_target=CLOUD,
                                    file_ids=("file-1",)).reason == "mode_forbids_target"


# --- 2. policy_revoked ------------------------------------------------------

def test_policy_revoked_after_a_scope_is_withdrawn(p7_conn):
    # Task 15's `revoke` appends this event with `canonical_json({"scope": scope, ...})`.
    # "Granted and then withdrawn" is a different fact from "never granted": the user
    # has already said no once, so §8.7's negative feedback applies to the remedy.
    granted = a_policy()
    assert policy_revoked_for(p7_conn, granted, "Academics") is False
    append_event(p7_conn, event_type=CONSENT_REVOKED, subsystem=SUBSYSTEM,
                 component_version=COMPONENT, observed_at=LATER,
                 explanation=json.dumps({REVOKED_SCOPE_KEY: "Academics"}))
    withdrawn = a_policy(consent_grants=(), policy_version="policy-2")
    assert policy_revoked_for(p7_conn, withdrawn, "Academics") is True
    assert deny_policy_revoked(scope="Academics", policy=withdrawn,
                               file_ids=("file-1",)).reason == "policy_revoked"


def test_a_re_granted_scope_stops_denying(p7_conn):
    # Revocation is forward-only, not permanent: a new grant puts the scope back and
    # the denial stops. The ledger half -- a token minted before the revocation still
    # consuming -- is Task 12's.
    append_event(p7_conn, event_type=CONSENT_REVOKED, subsystem=SUBSYSTEM,
                 component_version=COMPONENT, observed_at=LATER,
                 explanation=json.dumps({REVOKED_SCOPE_KEY: "Academics"}))
    assert policy_revoked_for(p7_conn, a_policy(), "Academics") is False


# --- 3. always_local_item ---------------------------------------------------

def test_always_local_item_translates_task_sevens_refusal():
    # §8.4: "Nothing in this set can be named as a releasable item kind." Task 7
    # refuses at construction; this builder turns that refusal into the gate's answer
    # rather than re-deciding which of the nine names are always-local.
    caught = AlwaysLocalRequested("GPS")
    denied = deny_always_local_item(caught, file_ids=("file-1",))
    assert denied.reason == "always_local_item"
    assert "GPS" in denied.explanation


# --- 4. unclassified -- the ordinary case -----------------------------------

def test_unclassified_is_the_ordinary_denial():
    # D2: no detector exists, so every real file lands here. §8.4: "classify data into
    # handling classes before LLM escalation" makes classification a PRECONDITION.
    assert unclassified_denies(locality="cloud",
                               local_calls_on_unclassified=True) is True
    denied = deny_unclassified(file_ids=("file-1",), locality="cloud",
                               completeness=None)
    assert denied.reason == "unclassified"


def test_absence_of_a_classification_never_resolves_to_public_low():
    # SPEC §1: "Absence of a classification resolves to `unreadable_unclassified`,
    # never to `public_low`." §8.6's rule it applies: "Cost exhaustion must never turn
    # into lower-quality automatic classification."
    denied = deny_unclassified(file_ids=("file-1",), locality="cloud",
                               completeness=None)
    assert "unreadable_unclassified" in denied.explanation
    assert "public_low" not in denied.explanation


def test_a_local_call_on_an_unclassified_file_has_no_default():
    # Open question 5, unanswered: "Does `unreadable_unclassified` permit a LOCAL
    # model call? ... which may block exactly the OCR-opaque screenshots §2.7 and §7.8
    # want a model to interpret." The parameter is required; P7 names no winner.
    with pytest.raises(TypeError):
        unclassified_denies(locality="local")
    assert unclassified_denies(locality="local",
                               local_calls_on_unclassified=True) is False
    assert unclassified_denies(locality="local",
                               local_calls_on_unclassified=False) is True


def test_unclassified_offers_a_remedy_the_user_can_actually_take():
    # §8.6 requires the UI to show "what has been deferred, and why", and §8.6's own
    # answer to an exhausted budget is to "leave the file or group in review rather
    # than guessing". A denial nobody can act on is a dead end.
    denied = deny_unclassified(file_ids=("file-1",), locality="cloud",
                               completeness=None)
    actions = {option.action for option in denied.remedy_options}
    assert "classify" in actions
    assert "defer" in actions


# --- 5. protected_records_template ------------------------------------------

def test_protected_records_template_denies_local_targets_too():
    # §7.3: Protected Records "should normally remain local-only and must not cause
    # filenames or content to be exposed in model prompts." No locality qualifier --
    # which is why this reason must outrank the cloud-only one.
    assert is_protected_records(PROTECTED_RECORDS_TEMPLATE) is True
    assert is_protected_records("Reading Inbox") is False
    for target in (LOCAL, CLOUD):
        denied = deny_protected_records_template(file_ids=("file-1",),
                                                 model_target=target)
        assert denied.reason == "protected_records_template"


def test_the_template_name_is_section_seven_threes_literal():
    assert PROTECTED_RECORDS_TEMPLATE == "Protected Records"


# --- 6. protected_cloud_target ----------------------------------------------

def test_protected_cloud_target_under_hybrid():
    # §8.4: "Hybrid mode: Sensitive files remain local". And SPEC §2's first protected
    # consequence: "not included in cloud-model prompts BY DEFAULT" -- the carve-out
    # that `cloud_assisted` plus an explicit grant satisfies.
    assert protected_cloud_denies(protected=True, locality="cloud",
                                  operation_mode="hybrid", scope="Academics",
                                  granted_scopes=("Academics",)) is True
    assert protected_cloud_denies(protected=True, locality="cloud",
                                  operation_mode="cloud_assisted", scope="Academics",
                                  granted_scopes=("Academics",)) is False
    assert protected_cloud_denies(protected=True, locality="cloud",
                                  operation_mode="cloud_assisted", scope="Taxes",
                                  granted_scopes=("Academics",)) is True
    assert protected_cloud_denies(protected=False, locality="cloud",
                                  operation_mode="hybrid", scope="Academics",
                                  granted_scopes=()) is False
    assert protected_cloud_denies(protected=True, locality="local",
                                  operation_mode="hybrid", scope="Academics",
                                  granted_scopes=()) is False
    denied = deny_protected_cloud_target(file_ids=("file-1",),
                                         operation_mode="hybrid", scope="Academics",
                                         evidence_refs=DETECTOR_KEYS)
    assert denied.reason == "protected_cloud_target"
    assert denied.evidence_refs == DETECTOR_KEYS


def test_the_corpus_area_is_the_callers_and_p7_defines_none():
    # Open question 3: "What is a 'corpus area'? ... Consent grants cannot be scoped
    # until this is named." The scope is a string the caller supplies; P7 compares it
    # and never resolves it.
    assert protected_cloud_denies(protected=True, locality="cloud",
                                  operation_mode="cloud_assisted",
                                  scope="whatever-the-caller-calls-it",
                                  granted_scopes=("whatever-the-caller-calls-it",)) \
        is False


# --- 7. whole_document_requested --------------------------------------------

def test_whole_document_requested_translates_task_sevens_refusal():
    # §8.4: "It should not send full documents where a short heading or OCR excerpt is
    # enough to resolve the question."
    caught = WholeDocumentRequested("span 0-4096 covers the whole unit")
    denied = deny_whole_document_requested(caught, file_ids=("file-1",))
    assert denied.reason == "whole_document_requested"
    assert "narrow_span" in {option.action for option in denied.remedy_options}


# --- 8. dossier_over_budget -- the backstop ---------------------------------

def test_dossier_over_budget_is_a_backstop_that_should_never_fire(p7_conn):
    """M9: P8 measures against the ceiling and runs §8.6's four-rung ladder BEFORE it
    calls the gate. A `dossier_over_budget` denial in a running pipeline is a P8
    defect to fix, not a normal outcome -- and the check stays because §8.6 forbids a
    prompt that "truncate[s] silently in a way that removes the decisive evidence"
    and the gate is the last place to catch a caller that skipped its ladder.
    Reachable in test; not reachable in a correct pipeline. Do not delete it.
    """
    assert CEILING_KEY in CEILING_KEYS
    set_ceiling(p7_conn, CEILING_KEY, 4000)
    assert over_dossier_ceiling(p7_conn, measured_tokens=9000) is True
    assert over_dossier_ceiling(p7_conn, measured_tokens=4000) is False
    denied = deny_dossier_over_budget(measured_tokens=9000, ceiling=4000,
                                      file_ids=("file-1",))
    assert denied.reason == "dossier_over_budget"
    ladder = {option.action for option in denied.remedy_options}
    assert ladder == {"summarize_deterministic_facts", "preserve_anchor_excerpts",
                      "split_the_task", "defer_the_decision"}


def test_an_unset_ceiling_cannot_deny(p7_conn):
    # `get_ceiling` returns None when nothing set it, which is the ordinary state.
    # P7 owns no number: SPEC Deferred puts "Numeric values for every ceiling"
    # outside this contract, and Task 21 asserts none appears in `src/privacy/`.
    assert over_dossier_ceiling(p7_conn, measured_tokens=10 ** 9) is False


def test_a_caller_cannot_raise_its_own_ceiling_by_echoing_a_larger_one(p7_conn):
    # `ModelCallRequest.max_dossier_tokens` is "the caller's echo of it (M9)". The
    # check reads P1's stored ceiling and never the echo.
    set_ceiling(p7_conn, CEILING_KEY, 4000)
    request = a_request(max_dossier_tokens=10 ** 6)
    assert request.max_dossier_tokens > 4000
    assert over_dossier_ceiling(p7_conn, measured_tokens=9000) is True


def test_the_measurement_is_the_callers_and_has_no_default(p7_conn):
    # P7 has no tokenizer and inventing one would invent a number -- the same
    # discipline as Task 8's injected redaction transform with no default.
    with pytest.raises(TypeError):
        over_dossier_ceiling(p7_conn)


# --- what every denial carries ----------------------------------------------

def test_every_denial_carries_a_non_empty_explanation():
    for reason, denied in all_eight().items():
        assert denied.reason == reason
        assert denied.explanation.strip(), reason


def test_every_denial_carries_at_least_one_remedy_option():
    # §8.6: the UI must show "what has been deferred, and why". A denial with no
    # legitimate alternative is a dead end the user cannot act on.
    for reason, denied in all_eight().items():
        assert denied.remedy_options, reason
        assert all(isinstance(option, RemedyOption)
                   for option in denied.remedy_options), reason


def test_a_denial_with_no_remedy_is_refused():
    with pytest.raises(MalformedDenial):
        deny("unclassified", explanation="nothing classified this file",
             remedy_options=(), evidence_refs=())


def test_a_denial_with_an_empty_explanation_is_refused():
    for blank in ("", "   "):
        with pytest.raises(MalformedDenial):
            deny("unclassified", explanation=blank,
                 remedy_options=(RemedyOption("defer", "leave it in review"),),
                 evidence_refs=())


def test_a_denial_with_an_out_of_vocabulary_reason_is_refused():
    # SPEC §1: "A value outside this set is a load error, not a fallback."
    with pytest.raises(OutOfVocabulary):
        deny("too_sensitive", explanation="made up",
             remedy_options=(RemedyOption("defer", "leave it in review"),),
             evidence_refs=())


def test_denied_carries_no_audit_id_and_no_content():
    # `Denied` is the gate's answer, not its record. The audit_id is reachable through
    # `audit_records_for`; putting it on the branch would invite a caller to treat the
    # answer as the log.
    from dataclasses import fields
    names = {field.name for field in fields(Denied)}
    assert names == {"reason", "explanation", "remedy_options", "evidence_refs"}


def test_no_two_reasons_share_one_remedy_list():
    # Proof that the remedies were authored per reason rather than defaulted from one
    # list. There is no REMEDY_ACTIONS vocabulary: §8.6 names four ladder rungs for one
    # situation and §8.4 names four consent options for another, and one enumeration
    # over both would invent a fifth thing no section states.
    lists = [tuple(sorted(option.action for option in denied.remedy_options))
             for denied in all_eight().values()]
    assert len(set(lists)) == len(lists)


# --- the audit record every denial appends ----------------------------------

def a_denial_record(conn, file_id, denied, *, classification=None, **over) -> int:
    base = dict(request=a_request(target=Target(file_ids=(file_id,), group_id=None)),
                policy=a_policy(), classification=classification,
                content_hashes=(get_file(conn, file_id)["content_hash"],),
                user_id=None, component_version=COMPONENT, observed_at=FIXED_CLOCK)
    base.update(over)
    return record_denial(conn, denied, **base)


def test_every_denial_appends_a_model_release_denied_event(p7_conn, file_id):
    # SPEC §7: "Denials and consent requests are also appended", on the strength of
    # §8.2's "Every significant event affecting a file".
    for reason, denied in all_eight().items():
        audit_id = a_denial_record(p7_conn, file_id, denied)
        row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                              (audit_id,)).fetchone()
        assert row["event_type"] == MODEL_RELEASE_DENIED, reason
        assert row["subsystem"] == "P7", reason
        assert json.loads(row["explanation"])["reason"] == reason


def test_the_denial_record_says_unreadable_unclassified(p7_conn, file_id):
    # D2: `Unreadable or unclassified` is a GATE OUTCOME. This is the field it lives
    # in -- `AuditRecord.file_sensitivity`, on the release decision.
    audit_id = a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    assert audit_record(p7_conn, audit_id).file_sensitivity == "unreadable_unclassified"


def test_a_denial_writes_no_classification(p7_conn, file_id):
    # C4: "a gate that also wrote would be doing two jobs." D2: the outcome "lives on
    # the release decision and never in that column, so 'nothing has looked' can never
    # be read as 'this file carries nothing'." One assertion, both rulings.
    before = get_file(p7_conn, file_id)["sensitivity_state"]
    a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    assert get_file(p7_conn, file_id)["sensitivity_state"] == before


def test_a_denial_records_the_class_a_classified_file_actually_has(p7_conn, file_id):
    classified = ClassificationRecord(
        file_id=file_id, content_hash=get_file(p7_conn, file_id)["content_hash"],
        handling_class="sensitive_personal", protected=True, basis="detector",
        evidence_refs=DETECTOR_KEYS, reliability_state="validated",
        observed_at=FIXED_CLOCK)
    audit_id = a_denial_record(p7_conn, file_id,
                               all_eight()["protected_cloud_target"],
                               classification=classified)
    assert audit_record(p7_conn, audit_id).file_sensitivity == "sensitive_personal"


def test_the_denial_record_names_no_released_content(p7_conn, file_id):
    # Nothing left the device, so `excerpts_included` is empty and
    # `redaction_applied` is false. A denial that listed excerpts would be a record of
    # a release that did not happen.
    audit_id = a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    record = audit_record(p7_conn, audit_id)
    assert record.outcome == "denied"
    assert record.release_id is None
    assert record.excerpts_included == ()
    assert record.redaction_applied is False


def test_the_denial_record_carries_every_audit_field(p7_conn, file_id):
    # SPEC §7's nineteen names are Task 10's; this asserts the denial path fills the
    # published tuple rather than a subset a later reader would have to guess at.
    audit_id = a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    record = audit_record(p7_conn, audit_id)
    for name in AUDIT_FIELDS:
        assert hasattr(record, name), name


def test_a_group_scoped_denial_names_all_its_files(p7_conn, file_id):
    # `events` has one `file_id` column. The column carries the id only when the call
    # is about exactly one file, so `WHERE file_id = ?` never over-reports; the full
    # tuple is always in the explanation. Task 10's `audit_records_for(file_id=...)`
    # must read the explanation too, or Task 15's `prior_releases` under-reports.
    request = a_request(target=Target(file_ids=(file_id, "file-2"), group_id="group-1"))
    audit_id = a_denial_record(p7_conn, file_id, all_eight()["unclassified"],
                               request=request)
    row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["file_id"] is None
    assert json.loads(row["explanation"])["file_ids"] == [file_id, "file-2"]


def test_a_denial_appends_exactly_one_event(p7_conn, file_id):
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before + 1
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_denials.py -v`
Expected: FAIL — `ImportError: cannot import name 'DECIDABLE_FROM_REQUEST' from 'privacy.denial'`
(the module does not exist yet, so collection fails on the first import).

- [ ] **Step 3: Write `src/privacy/denial.py`**

```python
# src/privacy/denial.py
"""§8.4's eight refusals -- and the one that is the ordinary case.

The detector is unwritten (D2). No task in any plan produces a rule set, so against a
real corpus `Gate.release` is asked about a file with no `ClassificationRecord`,
`resolve_class(None)` returns `unreadable_unclassified`, and the call is denied. That
is not a degraded mode. It is what a correct locked door does when nobody has been
given a key, and this module is written for it: `unclassified` carries the longest
explanation and the most remedies, because it is what the audit log will be full of.

Three things are decided here:

- **The eight reasons have a total order** (`DENIAL_ORDER`), because four of them
  overlap on real inputs and SPEC §6 requires one answer. The ordering principle is
  `DECIDABLE_FROM_REQUEST`: no denial that can be decided from the request alone may
  be decided after one that requires reading the file. A gate that materialised an
  excerpt and then discovered the mode forbade the call has read a sensitive file for
  a call that was never going to happen.
- **The builders are pure and the append is one function.** SPEC §7: "Denials and
  consent requests are also appended." The record needs the request and the policy,
  which a builder does not see; a builder that took them would compose §7's record
  eight times over, and Task 10 owns it once.
- **`unreadable_unclassified` goes in `AuditRecord.file_sensitivity` and nowhere
  else.** D2: it "lives on the release decision and never in that column, so 'nothing
  has looked' can never be read as 'this file carries nothing'." This module issues no
  `UPDATE files`.

It owns no detection rule, no numeric ceiling and no remedy vocabulary. The class of a
file arrives as a `ClassificationRecord`; the ceiling arrives from
`database_agent.budget.get_ceiling`; the remedies are composed per denial from the
design's own sentences, because §8.6 names four ladder rungs for one situation and
§8.4 names four consent options for another, and one enumeration over both would
invent a fifth thing no section states.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from database_agent.budget import get_ceiling

from privacy.audit import AUDIT_FIELDS, AuditRecord, append_audit
from privacy.authorship import CONSENT_REVOKED, SUBSYSTEM
from privacy.classification import ClassificationRecord, resolve_class
from privacy.items import AlwaysLocalRequested, WholeDocumentRequested
from privacy.policy import Policy
from privacy.release import Denied
from privacy.vocabulary import check_denial_reason

#: §7.3's literal template name, the one residual-library name P7 uses.
PROTECTED_RECORDS_TEMPLATE: str = "Protected Records"

#: The key Task 15's `revoke` writes into the `consent_revoked` explanation. Pinned so
#: a rename on either side is a red test rather than a denial that stops firing.
REVOKED_SCOPE_KEY: str = "scope"

#: P1's key for §8.6's dossier ceiling. The VALUE is never P7's -- SPEC Deferred puts
#: "Numeric values for every ceiling" outside this contract.
_DOSSIER_CEILING_KEY: str = "model.max_dossier_tokens_per_call"

#: The eight, in evaluation order. See the module docstring for each position.
DENIAL_ORDER: tuple[str, ...] = (
    "mode_forbids_target",
    "policy_revoked",
    "always_local_item",
    "unclassified",
    "protected_records_template",
    "protected_cloud_target",
    "whole_document_requested",
    "dossier_over_budget",
)

#: The six decidable from the request, the policy and a row lookup. The other two need
#: the resolved text, and every member of this set precedes both of them.
DECIDABLE_FROM_REQUEST: frozenset[str] = frozenset({
    "mode_forbids_target",
    "policy_revoked",
    "always_local_item",
    "unclassified",
    "protected_records_template",
    "protected_cloud_target",
})

#: §8.4's two modes under which no content leaves the device.
_LOCAL_ONLY_MODES: tuple[str, str] = ("offline", "local_model")


class MalformedDenial(ValueError):
    """A denial missing its explanation or its remedy.

    §8.6 requires the UI to show "what has been deferred, and why", and a denial with
    no legitimate alternative is a dead end the user cannot act on.
    """


@dataclass(frozen=True)
class RemedyOption:
    """One thing the caller may legitimately do instead (SPEC §6, §8.6).

    Not a closed vocabulary, deliberately. `action` is a short identifier for the
    surface to key on and `detail` is the sentence it came from.
    """

    action: str
    detail: str


def deny(reason: str, *, explanation: str,
         remedy_options: Sequence[RemedyOption],
         evidence_refs: Sequence[str]) -> Denied:
    """Build one refusal, validated.

    `evidence_refs` carries whatever the classification carried. M14's key-versus-id
    rule is Task 3's, on `ClassificationRecord.evidence_refs`; a second copy of it
    here would be a second place for it to drift.
    """
    check_denial_reason(reason)
    if not explanation or not explanation.strip():
        raise MalformedDenial(
            f"{reason}: SPEC §6 requires the explanation be 'user-facing, "
            "evidence-referenced'; an empty one is neither"
        )
    if not remedy_options:
        raise MalformedDenial(
            f"{reason}: §8.6 requires the product show 'what has been deferred, and "
            "why'. A denial with no legitimate alternative is a dead end"
        )
    refs = tuple(evidence_refs)
    if any(not isinstance(ref, str) or not ref for ref in refs):
        raise MalformedDenial(f"{reason}: every evidence ref must be a non-empty key")
    return Denied(reason=reason, explanation=explanation,
                  remedy_options=tuple(remedy_options), evidence_refs=refs)


def first_reason(reasons: Iterable[str]) -> str | None:
    """The highest-precedence reason among those that fired, or None.

    SPEC §6 gives one `reason`, and four of the eight overlap on real inputs, so the
    gate needs a total order rather than whichever check happened to run first.
    """
    triggered = {check_denial_reason(reason) for reason in reasons}
    for reason in DENIAL_ORDER:
        if reason in triggered:
            return reason
    return None


# --- the six decidable from the request -------------------------------------

def mode_forbids(operation_mode: str, locality: str) -> bool:
    """§8.4: under `offline` and `local_model`, no content leaves the device.

    A LOCAL model is permitted under both -- "only local rules and local models may
    run" -- so this refuses the target's locality, never the call.
    """
    return locality == "cloud" and operation_mode in _LOCAL_ONLY_MODES


def policy_revoked_for(conn: sqlite3.Connection, policy: Policy, scope: str) -> bool:
    """Granted and then withdrawn -- not "never granted", which is a different reason.

    Two-sided on purpose: a re-grant puts the scope back in `policy.consent_grants`
    and this stops firing, which is what makes revocation forward-only rather than
    permanent (§8.4: "revoke a policy for future runs").
    """
    if any(granted == scope for granted, _option in policy.consent_grants):
        return False
    for row in conn.execute(
            "SELECT explanation FROM events WHERE event_type = ?", (CONSENT_REVOKED,)):
        payload = json.loads(row["explanation"])
        if payload.get(REVOKED_SCOPE_KEY) == scope:
            return True
    return False


def unclassified_denies(*, locality: str, local_calls_on_unclassified: bool) -> bool:
    """§8.4 makes classification a precondition of escalation.

    `local_calls_on_unclassified` has NO default. Open question 5: "Does
    `unreadable_unclassified` permit a LOCAL model call? ... Reading escalation
    strictly denies local calls on unclassified files, which may block exactly the
    OCR-opaque screenshots §2.7 and §7.8 want a model to interpret." Unanswered, so
    the caller answers it and P7 names no winner.
    """
    if locality == "cloud":
        return True
    return not local_calls_on_unclassified


def is_protected_records(template_name: str | None) -> bool:
    """§7.3's carve-out, and it binds local calls too."""
    return template_name == PROTECTED_RECORDS_TEMPLATE


def protected_cloud_denies(*, protected: bool, locality: str, operation_mode: str,
                           scope: str, granted_scopes: Sequence[str]) -> bool:
    """SPEC §2's first protected consequence: "not included in cloud-model prompts BY
    DEFAULT" -- and `cloud_assisted` plus an explicit grant is the carve-out.

    §8.4: "Cloud-assisted mode: User explicitly permits selected corpus areas to use a
    cloud model." What a "corpus area" is stays Open question 3, so `scope` is an
    opaque string the caller supplies and P7 resolves none.
    """
    if not protected or locality != "cloud":
        return False
    if operation_mode == "cloud_assisted" and scope in tuple(granted_scopes):
        return False
    return True


# --- the two that need the resolved content ---------------------------------

def over_dossier_ceiling(conn: sqlite3.Connection, *, measured_tokens: int) -> bool:
    """M9's backstop. An UNSET ceiling cannot deny.

    `get_ceiling` returns `int | None` and `None` is the ordinary state. P7 owns no
    number, so with nothing configured there is nothing to exceed. `measured_tokens`
    is the caller's -- P7 has no tokenizer and inventing one would invent a number.
    Reads P1's stored ceiling and never `request.max_dossier_tokens`, which is "the
    caller's echo of it (M9)": a caller must not raise its own ceiling by echoing a
    larger one.
    """
    ceiling = get_ceiling(conn, _DOSSIER_CEILING_KEY)
    if ceiling is None:
        return False
    return measured_tokens > ceiling


# --- the eight builders -----------------------------------------------------

def deny_mode_forbids_target(*, operation_mode: str, model_target,
                             file_ids: Sequence[str]) -> Denied:
    return deny(
        "mode_forbids_target",
        explanation=(
            f"the operation mode is {operation_mode!r} and the request targets a "
            f"{model_target.locality} model ({model_target.provider}/"
            f"{model_target.model_id}). §8.4: under fully offline mode 'No content "
            "leaves the device; only local rules and local models may run.' "
            f"{len(tuple(file_ids))} file(s) were not released."
        ),
        remedy_options=(
            RemedyOption("use_local_model",
                         "§8.4: local rules and local models may run under this mode"),
            RemedyOption("change_operation_mode",
                         "§8.4's four modes are the user's to choose; the default is "
                         "local-first and changing it is an explicit act (W1)"),
        ),
        evidence_refs=(),
    )


def deny_policy_revoked(*, scope: str, policy: Policy,
                        file_ids: Sequence[str]) -> Denied:
    return deny(
        "policy_revoked",
        explanation=(
            f"consent for {scope!r} was granted and then withdrawn; policy "
            f"{policy.policy_version} carries no grant for it. §8.4 gives the user "
            "the right to 'revoke a policy for future runs', and this is a future "
            f"run. {len(tuple(file_ids))} file(s) were not released."
        ),
        remedy_options=(
            RemedyOption("grant_consent",
                         "§8.4's four options are offered again through P13 -- offered, "
                         "not re-proposed: §8.7 stores the withdrawal as negative "
                         "feedback so the same proposal does not resurface by itself"),
            RemedyOption("use_local_model",
                         "§8.4: a local model is one of the four consent options"),
        ),
        evidence_refs=(),
    )


def deny_always_local_item(caught: AlwaysLocalRequested, *,
                           file_ids: Sequence[str]) -> Denied:
    """Task 7's construction-time refusal, translated into the gate's answer.

    The nine names live in `vocabulary.ALWAYS_LOCAL` and the refusal in `items`. A
    builder that re-decided which of them are always-local would be a second copy of
    §8.4's list.
    """
    return deny(
        "always_local_item",
        explanation=(
            f"{caught}. §8.4: 'Paths, complete extracted text, OCR output, file "
            "hashes, image EXIF, GPS, user edits, group memberships, and raw "
            "sensitive values should remain local.' Nothing in that set can be named "
            f"as a releasable item kind. {len(tuple(file_ids))} file(s) were not "
            "released."
        ),
        remedy_options=(
            RemedyOption("request_excerpt",
                         "§8.4's compact dossier: 'selected excerpts, redacted "
                         "identifiers, candidate labels, non-sensitive metadata, and "
                         "evidence references'"),
        ),
        evidence_refs=(),
    )


def deny_unclassified(*, file_ids: Sequence[str], locality: str,
                      completeness: str | None) -> Denied:
    """The ordinary denial. No detector exists (D2), so this is the normal path.

    The explanation says `unreadable_unclassified` and never `public_low`: SPEC §1's
    "Absence of a classification resolves to `unreadable_unclassified`, never to
    `public_low`", which is §8.6's "Cost exhaustion must never turn into
    lower-quality automatic classification" applied to the one case that matters.
    """
    seen = ("no extraction run has completed for it"
            if completeness is None else f"its extraction completeness is {completeness!r}")
    return deny(
        "unclassified",
        explanation=(
            f"{len(tuple(file_ids))} file(s) resolve to handling class "
            "'unreadable_unclassified': no classification record exists and "
            f"{seen}. §8.4 requires the system to 'classify data into handling "
            "classes before LLM escalation', so an unclassified file has not met the "
            f"precondition for a {locality} model call. Absence of a classification "
            "is not evidence that the file carries nothing, and it never resolves to "
            "a lower class so the pipeline can continue."
        ),
        remedy_options=(
            RemedyOption("classify",
                         "§8.4: the classification 'is itself evidence-backed and can "
                         "be revised by the user'; a user may set one directly"),
            RemedyOption("defer",
                         "§8.6: 'retain extracted evidence, mark the deferred stage, "
                         "and leave the file or group in review rather than guessing'"),
            RemedyOption("review",
                         "§8.6: the user 'should be able to see what is running, what "
                         "has been deferred, and why'"),
        ),
        evidence_refs=(),
    )


def deny_protected_records_template(*, file_ids: Sequence[str],
                                    model_target) -> Denied:
    """§7.3, and it binds a LOCAL target too -- which is why it outranks the cloud rule."""
    return deny(
        "protected_records_template",
        explanation=(
            f"{len(tuple(file_ids))} file(s) are held under the "
            f"{PROTECTED_RECORDS_TEMPLATE!r} residual template. §7.3: it 'should "
            "normally remain local-only and must not cause filenames or content to "
            "be exposed in model prompts.' That binds every model, so the "
            f"{model_target.locality} target does not change the answer."
        ),
        remedy_options=(
            RemedyOption("decide_locally",
                         "§7.3: normally local-only; deterministic rules and local "
                         "placement still apply"),
            RemedyOption("review",
                         "§7.11: the system must not 'move them out of a protected "
                         "area without explicit user action'"),
        ),
        evidence_refs=(),
    )


def deny_protected_cloud_target(*, file_ids: Sequence[str], operation_mode: str,
                                scope: str,
                                evidence_refs: Sequence[str] = ()) -> Denied:
    return deny(
        "protected_cloud_target",
        explanation=(
            f"{len(tuple(file_ids))} file(s) are protected and the request targets a "
            f"cloud model under mode {operation_mode!r}. §8.4: 'Protected material "
            "should not be included in cloud-model prompts by default', and 'Hybrid "
            f"mode: Sensitive files remain local.' Scope {scope!r} carries no "
            "explicit grant."
        ),
        remedy_options=(
            RemedyOption("use_local_model",
                         "§8.4: 'Local-model mode: Local extraction plus a "
                         "user-installed local LLM for eligible dossiers'"),
            RemedyOption("grant_consent",
                         "§8.4: 'Cloud-assisted mode: User explicitly permits "
                         "selected corpus areas to use a cloud model'"),
        ),
        evidence_refs=evidence_refs,
    )


def deny_whole_document_requested(caught: WholeDocumentRequested, *,
                                  file_ids: Sequence[str]) -> Denied:
    return deny(
        "whole_document_requested",
        explanation=(
            f"{caught}. §8.4: the engine 'should not send full documents where a "
            "short heading or OCR excerpt is enough to resolve the question.' "
            f"{len(tuple(file_ids))} file(s) were not released."
        ),
        remedy_options=(
            RemedyOption("narrow_span",
                         "§8.4's compact dossier is 'selected excerpts' -- a bounded "
                         "span, addressed by (observation_key, span)"),
        ),
        evidence_refs=(),
    )


def deny_dossier_over_budget(*, measured_tokens: int, ceiling: int,
                             file_ids: Sequence[str]) -> Denied:
    """M9's backstop. It should never fire in a correct pipeline. Do not delete it.

    §8.6 forbids a prompt that "truncate[s] silently in a way that removes the
    decisive evidence", and the gate is the last place to catch a caller that skipped
    its ladder. The four remedies ARE that ladder, in §8.6's own order and words.
    """
    return deny(
        "dossier_over_budget",
        explanation=(
            f"the dossier measures {measured_tokens} tokens against a ceiling of "
            f"{ceiling} for {len(tuple(file_ids))} file(s). §8.6's ladder runs in the "
            "caller before the gate is asked (M9); reaching this denial in a running "
            "pipeline is a caller defect, not a gate result. The gate never truncates "
            "and never reduces -- reduction changes what the model sees, which is a "
            "dossier decision."
        ),
        remedy_options=(
            RemedyOption("summarize_deterministic_facts", "§8.6, rung one"),
            RemedyOption("preserve_anchor_excerpts", "§8.6, rung two"),
            RemedyOption("split_the_task", "§8.6, rung three"),
            RemedyOption("defer_the_decision", "§8.6, rung four"),
        ),
        evidence_refs=(),
    )


# --- the one append ---------------------------------------------------------

def record_denial(conn: sqlite3.Connection, denied: Denied, *, request,
                  policy: Policy, classification: ClassificationRecord | None,
                  content_hashes: Sequence[str], user_id: str | None,
                  component_version: str, observed_at: str) -> int:
    """Append the one `model_release_denied` record and return its `audit_id`.

    `file_sensitivity` is computed with `classification.resolve_class`, the same
    function the rest of P7 uses, so the gate outcome is not re-derived. It lands
    HERE -- on the release decision -- and never in `files.sensitivity_state` (D2).

    The `events` table has one `file_id` column, so it carries the id only when the
    call is about exactly one file and `WHERE file_id = ?` therefore never
    over-reports. The full tuple is always in the explanation as `file_ids`.

    SPEC §7 enumerates a RELEASE record, so it has no field for a denial's own
    `reason` and `remedy_options[]`. They go through `append_audit`'s `extra`, into
    the same canonical-JSON `explanation` -- §8.2's "structured explanation or
    evidence reference" slot -- because §8.6 requires the product to show "what has
    been deferred, and why" and there is nowhere else for the why to live.
    """
    file_ids = tuple(request.target.file_ids)
    values = {
        "audit_id": None,
        "release_id": None,
        "policy_version": policy.policy_version,
        "plan_version": policy.plan_version,
        "stage": request.stage,
        "outcome": "denied",
        "operation_mode": policy.operation_mode,
        "authorizing_policy": policy.policy_version,
        "file_sensitivity": resolve_class(classification),
        "excerpts_included": (),
        "redaction_applied": False,
        "redaction_manifest": (),
        "model": {"locality": request.model_target.locality,
                  "model_id": request.model_target.model_id,
                  "provider": request.model_target.provider},
        "content_hashes": tuple(content_hashes),
        "content_hash": content_hashes[0] if len(tuple(content_hashes)) == 1 else None,
        "prompt_fingerprint": request.prompt_fingerprint,
        "file_id": file_ids[0] if len(file_ids) == 1 else None,
        "file_ids": file_ids,
        "group_id": request.target.group_id,
        "consent_request_id": None,
        "user_id": user_id,
        "observed_at": observed_at,
        "appended_at": observed_at,
    }
    unfilled = [name for name in AUDIT_FIELDS if name not in values]
    if unfilled:
        raise MalformedDenial(
            f"SPEC §7 names {unfilled} and the denial path has no value for them; a "
            "field Task 10 publishes must be filled at the seam, not defaulted"
        )
    record = AuditRecord(**{name: values[name] for name in AUDIT_FIELDS})
    return append_audit(conn, record, author=SUBSYSTEM,
                        component_version=component_version, extra={
                            "reason": denied.reason,
                            "explanation": denied.explanation,
                            "remedy_options": [option.action
                                               for option in denied.remedy_options],
                            "evidence_refs": list(denied.evidence_refs),
                        })
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_denials.py -v`
Expected: PASS — 39 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–13 green, and the 1302 P1–P5 tests still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/denial.py tests/p7/test_p7_denials.py
git commit -m "feat(P7): the eight denials, their precedence, and the audit record each one writes"
```

---

---

### Task 14: `NeedsConsent`, its id, and the P13 seam

**Files:**
- Create: `src/privacy/consent.py`
- Test: `tests/p7/test_p7_consent.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.CONSENT_OPTIONS`, `privacy.audit.AUDIT_FIELDS`, `.AuditRecord`,
  `.append_audit(conn, record, *, author, component_version, extra=None) -> int`,
  `privacy.authorship.SUBSYSTEM`, `.CONSENT_REQUESTED`, `.CONSENT_GRANTED`,
  `.event_defaults(*, event_type, **fields) -> dict[str, object]`,
  `privacy.policy.Policy`,
  `privacy.policy.grant_consent(conn, policy, scope, option, *, user_id, component_version,
  observed_at) -> str`, `database_agent.events.append_event(conn, **fields) -> int`,
  `evidence_shape.canonical.canonical_json(value) -> str`.
- Produces (`consent.py`):
  - `CONSENT_AUTHORIZES: Mapping[str, bool]` — which of the four permit a model call.
  - `ConsentRequirement` — frozen: `file_ids`, `handling_class`, `items`, `why`.
  - `NeedsConsent` — frozen: `consent_request_id`, `requirement`, `options`.
  - `open_consent_request(conn, requirement, *, request, policy, content_hashes, user_id,
    component_version, observed_at) -> NeedsConsent`.
  - `record_consent_choice(conn, consent_request_id, option, *, policy, scope, user_id,
    component_version, observed_at) -> None`.
  - `pending_consent(conn, consent_request_id) -> NeedsConsent | None`.
  - `UnknownConsentOption`, `IncompleteConsentOptions`, `UnknownConsentRequest`,
    `ConsentAlreadyRecorded`.

**Done-means:** 7.

**The whole task exists so that `no_model_use` cannot become `abstain`.** §8.4: *"If a model needs
text containing sensitive content, the user should see that requirement and choose whether to allow
a local model, a cloud model, a redacted prompt, or no model use."* P8's SPEC: *"P8 must never map
this branch to `abstain`: there is no reason code for it, and none may be added. That mapping is the
precise failure B2 was raised to remove — §8.4 requires the *user* to see the requirement and choose,
so an abstention makes the choice for them, silently selecting 'no model use' without asking.
Consent pending is not consent refused."* P7 does exactly two things about that and no third:

1. **`NeedsConsent` carries no `reason` field**, so it is not a `Denied` in disguise and a caller
   cannot map it onto a denial reason even by accident. Asserted over `dataclasses.fields`, both
   ways: the field is absent, and the two branch types share no field name at all.
2. **A recorded `no_model_use` is a `consent_granted` event with a `user_id` and a timestamp.** An
   abstention is the *absence* of an answer. A recorded refusal is an answer. The difference is
   readable in the log by anyone who looks, which is what makes the two outcomes distinguishable
   after the fact rather than only in P8's source.

**Whether a caller absorbs the branch is P8 Done-means 13 and P13 Done-means 16.** P7 makes the
absorption unrepresentable; it does not police it, and no test here reaches into P8.

**`no_model_use` is a choice and changes no policy — `CONSENT_AUTHORIZES` is that as data.** Three of
the four options authorize a model and one does not, so `record_consent_choice` calls
`policy.grant_consent` for three and skips it for one. Written as an `if option !=
"no_model_use"` it would be one negation away from silently granting; written as a mapping it is a
table a reviewer can read and a test can iterate. The event is appended for **all four**, because
§8.2 preserves *"Every significant event affecting a file"* and a user deciding not to use a model is
significant — it is the decision §8.7 would learn from.

**Task 14 adds no table. The audit log is the store.** `consent_request_id` has no `events` column,
so it lands in the canonical-JSON `explanation` that the skeleton's *The audit record's home* already
decided on, and `pending_consent` reads it back with `json_extract`. That is not a shortcut: Done-means
7's own falsifiable form is *"the audit log holds a `consent_requested` event and no `model_release`
for that request until a choice is recorded"*, so the log **is** the state, and a second store beside
it would be a second place for the two to disagree. A test asserts no consent table exists.

**`consent_request_id` is P13's field name, not an invention.** P13's routing table: *"P7 |
`consent`, `privacy_settings` | `review_action` in full; `subject_ref` is a `consent_request_id`;
`action = select_consent_option | set_redaction | mark_private`."* SPEC §6's `NeedsConsent` carries
no id, and Done-means 7 needs a join key, so Task 14 adds it under P13's spelling. It is minted with
`uuid.uuid4()` rather than `secrets`, and the contrast with Task 12's `release_id` is deliberate: a
release id is a **capability** and must not be guessable, a consent request id is a **join key** that
P13 will put in a `subject_ref` column and that carries no authority at all.

**The grant is P7's even though P13 collected the gesture.** P13's SPEC: *"The chosen option is
routed to P7, which authors the §8.4 consent events and the consent-aware audit record. P13 records
the collection, not the grant."* `subsystem = "P7"` on every event this module writes (M8).

**One `consent_granted` per choice, appended here — the mirror of Task 15's ruling.** Task 15 already
settled that `policy.revoke_consent` records the withdrawal and appends nothing, and that `revoke`
appends the single `consent_revoked`. The same split holds on the grant side: `policy.grant_consent`
records the grant and returns the new `policy_version`; `record_consent_choice` appends the one
`consent_granted`. Two appends would put one act in the log twice, and §8.4's `prior_releases` is
read back out of that log. **This pins Task 5's `grant_consent`**, whose `Produces` entry is spelled
with an ellipsis.

**The handoff to Task 15 is one string: `scope`.** The `consent_granted` this task writes and the
`consent_revoked` Task 15 writes both carry the scope under the key `"scope"`, which Task 13 pins as
`REVOKED_SCOPE_KEY` and reads to decide `policy_revoked`. Grant here, withdraw there, deny in
between — three tasks, one key. What a scope *is* stays Open question 3: *"What is a 'corpus area'?
… Consent grants cannot be scoped until this is named."* `scope` is a required keyword with no
default and P7 defines no area, exactly as Task 15's `files_in_scope` does.

**`record_consent_choice` returns `None`, and the new `policy_version` is read back through
`policy.current_policy`.** The skeleton fixes the return type and it is the right one: SPEC §6 says
*"the gate owns the policy, so the caller does not supply this value, it echoes it"*, and handing a
freshly minted `policy_version` back from a consent recorder would give the caller a value from a
path that is not the gate. The caller re-reads the policy, which is what it would have to do anyway
— **the original request is never resumed.** P8's SPEC: *"When the user chooses, the caller composes
a **new** `ModelCallRequest` under the chosen option; the original is never resumed, because the
policy it was composed under is not the policy that now applies."* That sentence is also why one
request accepts exactly one choice, and why a second raises `ConsentAlreadyRecorded` rather than
overwriting — a second answer to an answered question would let a caller turn a recorded
`no_model_use` into a `cloud_model` after the fact.

**The requirement carries references, never text.** `ConsentRequirement.items` is
`(observation_key, span)` pairs, the same shape as `excerpts_included`, for the same reason SPEC §7
gives: *"not a second copy of the text — the always-local text already exists once."* A consent
prompt that embedded the sensitive value would have released it in order to ask permission to
release it. Asserted over `dataclasses.fields`, not by reading the class body.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_consent.py
"""Done-means 7 -- all four options, and no release until a choice is recorded.

§8.4: "If a model needs text containing sensitive content, the user should see that
requirement and choose whether to allow a local model, a cloud model, a redacted
prompt, or no model use." Those four, exactly.

The centre of this file is that `no_model_use` is an ANSWER and an abstention is
SILENCE, and that the log can tell them apart. P8 Done-means 13 and P13 Done-means 16
own whether a caller absorbs the branch; nothing here reaches into either.
"""
import json
from dataclasses import fields

import pytest

from privacy.audit import audit_records_for
from privacy.authorship import CONSENT_GRANTED, CONSENT_REQUESTED, SUBSYSTEM
from privacy.consent import (
    CONSENT_AUTHORIZES, ConsentAlreadyRecorded, ConsentRequirement,
    IncompleteConsentOptions, NeedsConsent, UnknownConsentOption,
    UnknownConsentRequest, open_consent_request, pending_consent,
    record_consent_choice,
)
from privacy.denial import REVOKED_SCOPE_KEY
from privacy.policy import Policy, current_policy, set_policy
from privacy.release import REQUEST_FIELDS, Denied, ModelCallRequest, ModelTarget, Target
from privacy.vocabulary import CONSENT_OPTIONS

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"
SCOPE = "Academics"
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
EXCERPTS = (
    ("sha256:ba9777bcba0096decc525198035644949d2357bf7f9a9cb3492c948c86c0fcbd", "0-19"),
)

_REQUEST_DEFAULTS = {
    "stage": "grouping",
    "target": Target(file_ids=("file-1",), group_id=None),
    "model_target": CLOUD,
    "requested_items": (),
    "prompt_template_id": "template-1",
    "prompt_fingerprint": "fp-1",
    "max_dossier_tokens": 4000,
}


def a_request(**over) -> ModelCallRequest:
    missing = [name for name in REQUEST_FIELDS if name not in _REQUEST_DEFAULTS]
    assert not missing, (
        f"REQUEST_FIELDS names {missing} and this test has no value for them; "
        "SPEC §6 changed and Task 14 needs a value, not a default")
    values = {name: _REQUEST_DEFAULTS[name] for name in REQUEST_FIELDS}
    values.update(over)
    return ModelCallRequest(**values)


def a_requirement(**over) -> ConsentRequirement:
    base = dict(file_ids=("file-1",), handling_class="sensitive_personal",
                items=EXCERPTS,
                why="the grouping question turns on a value the detector marked "
                    "potentially sensitive")
    base.update(over)
    return ConsentRequirement(**base)


def a_policy(**over) -> Policy:
    base = dict(policy_version="policy-1", operation_mode="cloud_assisted",
                consent_grants=(),
                redaction_settings={"names": "redacted", "previews": "redacted",
                                    "thumbnails": "redacted", "ocr_text": "redacted",
                                    "location_data": "redacted"},
                automatic_move_permissions={}, plan_version="plan-1",
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


@pytest.fixture()
def stored_policy(p7_conn) -> Policy:
    """A policy in force, so `grant_consent` has something to supersede."""
    set_policy(p7_conn, a_policy(), component_version=COMPONENT,
               user_id="joseph",
               reason="the fixture's starting policy")
    return current_policy(p7_conn, plan_version="plan-1")


def open_request(conn, policy, **over) -> NeedsConsent:
    base = dict(request=a_request(), policy=policy, content_hashes=("sha256:abc",),
                user_id="joseph", component_version=COMPONENT,
                observed_at=FIXED_CLOCK)
    base.update(over)
    return open_consent_request(conn, a_requirement(), **base)


def choose(conn, needs, option, policy, **over) -> None:
    base = dict(policy=policy, scope=SCOPE, user_id="joseph",
                component_version=COMPONENT, observed_at=LATER)
    base.update(over)
    record_consent_choice(conn, needs.consent_request_id, option, **base)


# --- the four options, always all four --------------------------------------

def test_the_four_options_are_the_designs_own_four():
    # §8.4: "choose whether to allow a local model, a cloud model, a redacted prompt,
    # or no model use." Those four, in that order.
    assert CONSENT_OPTIONS == ("local_model", "cloud_model", "redacted_prompt",
                              "no_model_use")


def test_the_options_default_to_all_four():
    needs = NeedsConsent(consent_request_id="consent-1", requirement=a_requirement())
    assert needs.options == CONSENT_OPTIONS


def test_a_needs_consent_with_three_options_raises():
    # P13's SPEC: "All four options are always presentable. A surface that offers
    # fewer has silently made the user's decision for them."
    with pytest.raises(IncompleteConsentOptions):
        NeedsConsent(consent_request_id="consent-1", requirement=a_requirement(),
                     options=("local_model", "cloud_model", "redacted_prompt"))


def test_dropping_no_model_use_in_particular_raises():
    # The one a caller would be tempted to drop, because "no model" looks like "no
    # call". It is the option that makes the branch a question rather than a refusal.
    with pytest.raises(IncompleteConsentOptions):
        NeedsConsent(consent_request_id="consent-1", requirement=a_requirement(),
                     options=tuple(o for o in CONSENT_OPTIONS if o != "no_model_use"))


def test_an_option_outside_the_vocabulary_raises():
    with pytest.raises(UnknownConsentOption):
        NeedsConsent(consent_request_id="consent-1", requirement=a_requirement(),
                     options=CONSENT_OPTIONS + ("maybe_later",))


# --- structurally not a denial ----------------------------------------------

def test_needs_consent_has_no_reason_field():
    # SPEC §6: "`Denied` is the gate's answer, `NeedsConsent` is a question that only
    # the user can answer. Consent pending is not consent refused."
    names = {field.name for field in fields(NeedsConsent)}
    assert names == {"consent_request_id", "requirement", "options"}
    assert "reason" not in names


def test_needs_consent_shares_no_field_with_denied():
    # A caller cannot map one onto the other even by accident: there is no shared name
    # to copy across.
    assert not ({field.name for field in fields(NeedsConsent)}
                & {field.name for field in fields(Denied)})


def test_the_requirement_carries_references_and_not_text():
    # SPEC §7: `(observation_key, span)` pairs, "not a second copy of the text". A
    # consent prompt embedding the value would have released it in order to ask
    # permission to release it.
    names = {field.name for field in fields(ConsentRequirement)}
    assert names == {"file_ids", "handling_class", "items", "why"}
    assert not (names & {"text", "value", "content", "excerpt", "raw_value"})
    assert a_requirement().items == EXCERPTS


# --- the id, and the P13 seam -----------------------------------------------

def test_opening_a_request_mints_an_id(p7_conn, stored_policy):
    # P13's routing table: "`subject_ref` is a `consent_request_id`". SPEC §6 carries
    # no id and Done-means 7 needs a join key, so Task 14 adds it under P13's name.
    first = open_request(p7_conn, stored_policy)
    second = open_request(p7_conn, stored_policy)
    assert first.consent_request_id
    assert first.consent_request_id != second.consent_request_id


def test_pending_consent_round_trips_the_requirement(p7_conn, stored_policy):
    opened = open_request(p7_conn, stored_policy)
    recovered = pending_consent(p7_conn, opened.consent_request_id)
    assert recovered == opened


def test_pending_consent_is_none_for_an_id_nobody_opened(p7_conn):
    assert pending_consent(p7_conn, "consent-nobody-opened") is None


def test_consent_adds_no_table(p7_conn, stored_policy):
    # Done-means 7's falsifiable form reads the audit log, so the audit log IS the
    # state. A second store beside it is a second place for the two to disagree.
    open_request(p7_conn, stored_policy)
    tables = {row["name"] for row in p7_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert not [name for name in tables if "consent" in name]


# --- Done-means 7, in its own words -----------------------------------------

def test_opening_a_request_appends_consent_requested(p7_conn, stored_policy):
    opened = open_request(p7_conn, stored_policy)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CONSENT_REQUESTED,)).fetchone()
    assert row["subsystem"] == "P7"
    payload = json.loads(row["explanation"])
    assert payload["consent_request_id"] == opened.consent_request_id
    assert payload["options"] == list(CONSENT_OPTIONS)


def test_no_model_release_exists_until_a_choice_is_recorded(p7_conn, stored_policy):
    # Done-means 7 verbatim: "the audit log holds a `consent_requested` event and no
    # `model_release` for that request until a choice is recorded."
    opened = open_request(p7_conn, stored_policy)
    records = audit_records_for(p7_conn, consent_request_id=opened.consent_request_id)
    assert [record.outcome for record in records] == ["consent_requested"]
    choose(p7_conn, opened, "cloud_model", stored_policy)
    outcomes = [record.outcome for record in
                audit_records_for(p7_conn,
                                  consent_request_id=opened.consent_request_id)]
    assert "released" not in outcomes


def test_recording_a_choice_releases_nothing(p7_conn, stored_policy):
    # C4: the gate writes its record and does not act on it. Recording consent is not
    # a release; P8's SPEC: "the caller composes a NEW `ModelCallRequest` under the
    # chosen option; the original is never resumed."
    opened = open_request(p7_conn, stored_policy)
    choose(p7_conn, opened, "cloud_model", stored_policy)
    assert p7_conn.execute(
        "SELECT count(*) c FROM release_ledger").fetchone()["c"] == 0


def test_recording_a_choice_clears_the_pending_request(p7_conn, stored_policy):
    opened = open_request(p7_conn, stored_policy)
    choose(p7_conn, opened, "no_model_use", stored_policy)
    assert pending_consent(p7_conn, opened.consent_request_id) is None


# --- no_model_use is an answer, not silence ---------------------------------

def test_no_model_use_is_recorded_as_a_choice_not_as_silence(p7_conn, stored_policy):
    """B2, and P8's SPEC: "P8 must never map this branch to `abstain` ... an
    abstention makes the choice for them, silently selecting 'no model use' without
    asking." An abstention is the ABSENCE of an answer. This is an answer: it has a
    user, a time, and an event of its own, and a later reader can tell them apart.
    """
    opened = open_request(p7_conn, stored_policy)
    choose(p7_conn, opened, "no_model_use", stored_policy)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CONSENT_GRANTED,)).fetchone()
    payload = json.loads(row["explanation"])
    assert payload["option"] == "no_model_use"
    assert payload["authorized"] is False
    assert row["user_id"] == "joseph"
    assert row["observed_at"] == LATER


def test_no_model_use_grants_no_policy_change(p7_conn, stored_policy):
    opened = open_request(p7_conn, stored_policy)
    before = current_policy(p7_conn, plan_version="plan-1").consent_grants
    choose(p7_conn, opened, "no_model_use", stored_policy)
    assert current_policy(p7_conn,
                          plan_version="plan-1").consent_grants == before


def test_the_three_authorizing_options_change_the_policy(p7_conn, stored_policy):
    # `grant_consent` is Task 5's; this asserts the three that reach it do.
    for option in ("local_model", "cloud_model", "redacted_prompt"):
        opened = open_request(p7_conn, stored_policy)
        choose(p7_conn, opened, option, stored_policy)
        grants = current_policy(p7_conn, plan_version="plan-1").consent_grants
        assert (SCOPE, option) in grants


def test_consent_authorizes_is_data_and_not_an_if(p7_conn):
    # Written as `if option != "no_model_use"` this would be one negation away from
    # silently granting. Written as a mapping it is a table a reviewer can read.
    assert set(CONSENT_AUTHORIZES) == set(CONSENT_OPTIONS)
    assert CONSENT_AUTHORIZES["no_model_use"] is False
    assert all(CONSENT_AUTHORIZES[option] is True
               for option in CONSENT_OPTIONS if option != "no_model_use")


def test_every_option_appends_exactly_one_event(p7_conn, stored_policy):
    # §8.2 preserves "Every significant event affecting a file", and a user deciding
    # not to use a model is significant -- it is the decision §8.7 would learn from.
    for option in CONSENT_OPTIONS:
        opened = open_request(p7_conn, stored_policy)
        before = p7_conn.execute(
            "SELECT count(*) c FROM events WHERE event_type = ?",
            (CONSENT_GRANTED,)).fetchone()["c"]
        choose(p7_conn, opened, option, stored_policy)
        after = p7_conn.execute(
            "SELECT count(*) c FROM events WHERE event_type = ?",
            (CONSENT_GRANTED,)).fetchone()["c"]
        assert after == before + 1, option


# --- authorship, and the handoff to Task 15 ---------------------------------

def test_the_grant_is_authored_by_p7_though_p13_collected_it(p7_conn, stored_policy):
    # P13's SPEC: "The chosen option is routed to P7, which authors the §8.4 consent
    # events and the consent-aware audit record. P13 records the collection, not the
    # grant." M8: the acting part authors, P1 writes.
    opened = open_request(p7_conn, stored_policy)
    choose(p7_conn, opened, "cloud_model", stored_policy)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CONSENT_GRANTED,)).fetchone()
    assert row["subsystem"] == "P7"
    assert row["component_version"] == COMPONENT


def test_the_grant_and_the_revocation_key_on_the_same_scope(p7_conn, stored_policy):
    # The handoff: this task grants, Task 15 withdraws, Task 13 denies in between --
    # three tasks, one key. Open question 3 leaves what a scope IS to the caller.
    opened = open_request(p7_conn, stored_policy)
    choose(p7_conn, opened, "cloud_model", stored_policy)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CONSENT_GRANTED,)).fetchone()
    assert json.loads(row["explanation"])[REVOKED_SCOPE_KEY] == SCOPE


# --- refusals ---------------------------------------------------------------

def test_a_second_choice_for_one_request_is_refused(p7_conn, stored_policy):
    # P8's SPEC: "the caller composes a NEW `ModelCallRequest` under the chosen
    # option; the original is never resumed." A second answer to an answered question
    # would let a caller turn a recorded `no_model_use` into a `cloud_model` after
    # the fact.
    opened = open_request(p7_conn, stored_policy)
    choose(p7_conn, opened, "no_model_use", stored_policy)
    with pytest.raises(ConsentAlreadyRecorded):
        choose(p7_conn, opened, "cloud_model", stored_policy)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CONSENT_GRANTED,)).fetchone()
    assert json.loads(row["explanation"])["option"] == "no_model_use"


def test_a_choice_for_an_unknown_request_is_refused(p7_conn, stored_policy):
    with pytest.raises(UnknownConsentRequest):
        record_consent_choice(p7_conn, "consent-nobody-opened", "cloud_model",
                              policy=stored_policy, scope=SCOPE, user_id="joseph",
                              component_version=COMPONENT, observed_at=LATER)


def test_an_unknown_option_is_refused(p7_conn, stored_policy):
    opened = open_request(p7_conn, stored_policy)
    with pytest.raises(UnknownConsentOption):
        choose(p7_conn, opened, "maybe_later", stored_policy)


def test_a_refused_choice_writes_nothing(p7_conn, stored_policy):
    opened = open_request(p7_conn, stored_policy)
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    with pytest.raises(UnknownConsentOption):
        choose(p7_conn, opened, "maybe_later", stored_policy)
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before
    assert pending_consent(p7_conn, opened.consent_request_id) == opened


def test_the_scope_has_no_default(p7_conn, stored_policy):
    # Open question 3: "What is a 'corpus area'? ... Consent grants cannot be scoped
    # until this is named." Task 15's `files_in_scope` holds it the same way.
    opened = open_request(p7_conn, stored_policy)
    with pytest.raises(TypeError):
        record_consent_choice(p7_conn, opened.consent_request_id, "cloud_model",
                              policy=stored_policy, user_id="joseph",
                              component_version=COMPONENT, observed_at=LATER)
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_consent.py -v`
Expected: FAIL — `ImportError: cannot import name 'CONSENT_AUTHORIZES' from 'privacy.consent'`
(the module does not exist yet, so collection fails on the first import).

- [ ] **Step 3: Write `src/privacy/consent.py`**

```python
# src/privacy/consent.py
"""§8.4's consent question, its id, and the seam P13 collects the answer through.

§8.4: "If a model needs text containing sensitive content, the user should see that
requirement and choose whether to allow a local model, a cloud model, a redacted
prompt, or no model use." Those four, exactly, and always all four -- P13's SPEC: "A
surface that offers fewer has silently made the user's decision for them."

This module exists to make one failure unrepresentable. P8's SPEC: "P8 must never map
this branch to `abstain`: there is no reason code for it, and none may be added ... an
abstention makes the choice for them, silently selecting 'no model use' without
asking. Consent pending is not consent refused." P7 does two things about that:

- `NeedsConsent` carries no `reason` field, so it is not a `Denied` in disguise and
  cannot be mapped onto a denial reason by accident;
- a recorded `no_model_use` is a `consent_granted` event with a user and a time, so an
  answer and a silence are distinguishable in the log by anyone who looks.

Whether a caller absorbs the branch is P8 Done-means 13 and P13 Done-means 16. P7 does
not police it.

**No table.** Done-means 7's falsifiable form is "the audit log holds a
`consent_requested` event and no `model_release` for that request until a choice is
recorded", so the log IS the state, and a second store beside it would be a second
place for the two to disagree.

**One `consent_granted` per choice, appended here.** `policy.grant_consent` records the
grant and returns the new `policy_version`; it appends nothing. That is the mirror of
Task 15's ruling for `revoke_consent` and `consent_revoked`, and for the same reason:
two appends put one act in the log twice, and §8.4's `prior_releases` is read back out
of that log.

This module imports no `privacy` module that imports it: `release.py` re-exports
`NeedsConsent` for the `ReleaseDecision` union, so the request object arrives here as
an argument and its type is an annotation only.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

from database_agent.events import append_event
from evidence_shape.canonical import canonical_json

from privacy.audit import AUDIT_FIELDS, AuditRecord, append_audit
from privacy.authorship import (
    CONSENT_GRANTED, CONSENT_REQUESTED, SUBSYSTEM, event_defaults,
)
from privacy.policy import Policy, grant_consent
from privacy.vocabulary import CONSENT_OPTIONS

if TYPE_CHECKING:  # pragma: no cover - annotation only; see the module docstring
    from privacy.release import ModelCallRequest

#: Which of §8.4's four permit a model call. Data rather than a negated `if`, which
#: would be one edit away from silently granting. `no_model_use` is a CHOICE -- it is
#: recorded like the others and changes no policy.
CONSENT_AUTHORIZES: Mapping[str, bool] = MappingProxyType({
    "local_model": True,
    "cloud_model": True,
    "redacted_prompt": True,
    "no_model_use": False,
})

#: The key the scope is stored under, shared with Task 13's `REVOKED_SCOPE_KEY` and
#: Task 15's `revoke`. Grant here, withdraw there, deny in between.
_SCOPE_KEY: str = "scope"


class UnknownConsentOption(ValueError):
    """A value outside §8.4's four. SPEC §1: "a load error, not a fallback.\""""


class IncompleteConsentOptions(ValueError):
    """Fewer than four options.

    P13's SPEC: "All four options are always presentable. A surface that offers fewer
    has silently made the user's decision for them."
    """


class UnknownConsentRequest(LookupError):
    """No `consent_requested` event carries this id."""


class ConsentAlreadyRecorded(ValueError):
    """This request already has an answer.

    P8's SPEC: "the caller composes a NEW `ModelCallRequest` under the chosen option;
    the original is never resumed." A second answer would let a caller turn a recorded
    `no_model_use` into a `cloud_model` after the fact.
    """


@dataclass(frozen=True)
class ConsentRequirement:
    """SPEC §6: "which items require sensitive text, and why".

    `items` is `(observation_key, span)` pairs -- the same shape as
    `excerpts_included`, and for SPEC §7's reason: "not a second copy of the text".
    A consent prompt that embedded the value would have released it in order to ask
    permission to release it.
    """

    file_ids: tuple[str, ...]
    handling_class: str
    items: tuple[tuple[str, str], ...]
    why: str


@dataclass(frozen=True)
class NeedsConsent:
    """SPEC §6's third branch. It carries no `reason`, and that is load-bearing.

    "`Denied` is the gate's answer, `NeedsConsent` is a question that only the user
    can answer. Consent pending is not consent refused."
    """

    consent_request_id: str
    requirement: ConsentRequirement
    options: tuple[str, ...] = CONSENT_OPTIONS

    def __post_init__(self) -> None:
        unknown = [option for option in self.options if option not in CONSENT_OPTIONS]
        if unknown:
            raise UnknownConsentOption(
                f"{unknown} are not among §8.4's four options {CONSENT_OPTIONS}"
            )
        if tuple(self.options) != CONSENT_OPTIONS:
            raise IncompleteConsentOptions(
                f"{tuple(self.options)} is not §8.4's four in order; P13: 'A surface "
                "that offers fewer has silently made the user's decision for them'"
            )


def _requirement_form(requirement: ConsentRequirement) -> dict[str, object]:
    return {
        "file_ids": list(requirement.file_ids),
        "handling_class": requirement.handling_class,
        "items": [list(pair) for pair in requirement.items],
        "why": requirement.why,
    }


def _requirement_from(form: Mapping[str, object]) -> ConsentRequirement:
    return ConsentRequirement(
        file_ids=tuple(form["file_ids"]),
        handling_class=form["handling_class"],
        items=tuple(tuple(pair) for pair in form["items"]),
        why=form["why"],
    )


def _event_for(conn: sqlite3.Connection, event_type: str,
               consent_request_id: str) -> sqlite3.Row | None:
    """The one event of this type carrying this id.

    `consent_request_id` has no `events` column, so it lives in the canonical-JSON
    `explanation` the skeleton's *The audit record's home* decided on, and is read
    back with `json_extract`.
    """
    return conn.execute(
        "SELECT * FROM events WHERE event_type = ? "
        "AND json_extract(explanation, '$.consent_request_id') = ? "
        "ORDER BY event_id LIMIT 1",
        (event_type, consent_request_id),
    ).fetchone()


def open_consent_request(conn: sqlite3.Connection, requirement: ConsentRequirement, *,
                         request: ModelCallRequest, policy: Policy,
                         content_hashes: Sequence[str], user_id: str | None,
                         component_version: str, observed_at: str) -> NeedsConsent:
    """Ask §8.4's question, record that it was asked, and return all four options.

    The id is `uuid.uuid4()`, not `secrets`: a `release_id` is a capability and must
    not be guessable, while a `consent_request_id` is a join key P13 puts in a
    `subject_ref` column and carries no authority at all.
    """
    consent_request_id = "consent-" + str(uuid.uuid4())
    needs = NeedsConsent(consent_request_id=consent_request_id,
                         requirement=requirement)
    file_ids = tuple(request.target.file_ids)
    values = {
        "audit_id": None,
        "release_id": None,
        "policy_version": policy.policy_version,
        "plan_version": policy.plan_version,
        "stage": request.stage,
        "outcome": "consent_requested",
        "operation_mode": policy.operation_mode,
        "authorizing_policy": policy.policy_version,
        "file_sensitivity": requirement.handling_class,
        "excerpts_included": (),
        "redaction_applied": False,
        "redaction_manifest": (),
        "model": {"locality": request.model_target.locality,
                  "model_id": request.model_target.model_id,
                  "provider": request.model_target.provider},
        "content_hashes": tuple(content_hashes),
        "content_hash": content_hashes[0] if len(tuple(content_hashes)) == 1 else None,
        "prompt_fingerprint": request.prompt_fingerprint,
        "file_id": file_ids[0] if len(file_ids) == 1 else None,
        "file_ids": file_ids,
        "group_id": request.target.group_id,
        "consent_request_id": consent_request_id,
        "user_id": user_id,
        "observed_at": observed_at,
        "appended_at": observed_at,
    }
    unfilled = [name for name in AUDIT_FIELDS if name not in values]
    if unfilled:
        raise ValueError(
            f"SPEC §7 names {unfilled} and the consent path has no value for them; a "
            "field Task 10 publishes must be filled at the seam, not defaulted"
        )
    record = AuditRecord(**{name: values[name] for name in AUDIT_FIELDS})
    append_audit(conn, record, author=SUBSYSTEM,
                 component_version=component_version, extra={
                     "requirement": _requirement_form(requirement),
                     "options": list(needs.options),
                 })
    return needs


def pending_consent(conn: sqlite3.Connection,
                    consent_request_id: str) -> NeedsConsent | None:
    """The open question, or None if it was never asked or has been answered."""
    asked = _event_for(conn, CONSENT_REQUESTED, consent_request_id)
    if asked is None:
        return None
    if _event_for(conn, CONSENT_GRANTED, consent_request_id) is not None:
        return None
    payload = json.loads(asked["explanation"])
    return NeedsConsent(consent_request_id=consent_request_id,
                        requirement=_requirement_from(payload["requirement"]),
                        options=tuple(payload["options"]))


def record_consent_choice(conn: sqlite3.Connection, consent_request_id: str,
                          option: str, *, policy: Policy, scope: str,
                          user_id: str, component_version: str,
                          observed_at: str) -> None:
    """Record the user's answer, and grant only where the answer authorizes a model.

    Returns None. SPEC §6: "the gate owns the policy, so the caller does not supply
    this value, it echoes it" -- handing a freshly minted `policy_version` back from a
    consent recorder would give the caller a value from a path that is not the gate.
    The caller re-reads `current_policy`, which it has to do anyway: the original
    request is never resumed.

    `scope` has no default. Open question 3: "What is a 'corpus area'? ... Consent
    grants cannot be scoped until this is named."
    """
    if option not in CONSENT_OPTIONS:
        raise UnknownConsentOption(
            f"{option!r} is not among §8.4's four options {CONSENT_OPTIONS}"
        )
    if _event_for(conn, CONSENT_REQUESTED, consent_request_id) is None:
        raise UnknownConsentRequest(
            f"no consent_requested event carries {consent_request_id!r}"
        )
    if _event_for(conn, CONSENT_GRANTED, consent_request_id) is not None:
        raise ConsentAlreadyRecorded(
            f"{consent_request_id!r} already has an answer; P8's SPEC: 'the caller "
            "composes a NEW ModelCallRequest under the chosen option; the original is "
            "never resumed'"
        )
    authorized = CONSENT_AUTHORIZES[option]
    if authorized:
        grant_consent(conn, policy, scope, option, user_id=user_id,
                      component_version=component_version, observed_at=observed_at)
    append_event(conn, **event_defaults(
        event_type=CONSENT_GRANTED,
        user_id=user_id,
        component_version=component_version,
        observed_at=observed_at,
        explanation=canonical_json({
            "consent_request_id": consent_request_id,
            "option": option,
            "authorized": authorized,
            _SCOPE_KEY: scope,
            "collected_by": "P13",
        }),
    ))
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_consent.py -v`
Expected: PASS — 28 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–14 green, and the 1302 P1–P5 tests still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/consent.py tests/p7/test_p7_consent.py
git commit -m "feat(P7): NeedsConsent, its consent_request_id, and the P13 seam"
```

---

---

### Task 15: Revocation, the retraction limit, and `delete_derived`'s refusal (I6/D3)

**Files:**
- Create: `src/privacy/revocation.py`
- Modify: `src/privacy/gate.py` (add `Gate.revoke` and `Gate.delete_derived`, delegating to this module — SPEC §8 publishes it on the facade, and **D13 kept CUT 4**, so the facade is certain rather than provisional)
- Test: `tests/p7/test_p7_revocation.py`

**Interfaces:**
- Consumes: `privacy.audit.audit_records_for(conn, *, file_id=None, release_id=None,
  consent_request_id=None) -> list[AuditRecord]`, `privacy.audit.AUDIT_FIELDS`,
  `privacy.authorship.CONSENT_REVOKED`, `privacy.authorship.event_defaults(*, event_type, **fields)
  -> dict[str, object]`, `privacy.policy.Policy`,
  `privacy.policy.revoke_consent(conn, policy, scope, *, user_id, component_version, observed_at)
  -> str`, `database_agent.events.append_event(conn, **fields) -> int`,
  `evidence_shape.canonical.canonical_json(value) -> str`.
- Produces (`revocation.py`):
  - `RELEASED: str = "released"` — the `AuditRecord.outcome` value a prior release carries.
  - `PriorRelease` — frozen: `model: str`, `provider: str`, `when: str`,
    `excerpts: tuple[tuple[str, str], ...]`.
  - `RevocationResult` — frozen: `effective_from: str`, `prior_releases: tuple[PriorRelease, ...]`,
    `retraction_limit: str`.
  - `revoke(conn, policy, scope, *, user_id, component_version, observed_at, retraction_limit,
    files_in_scope) -> RevocationResult`.
  - `DERIVED_PROJECTIONS: Mapping[str, tuple[str, ...]]` — D3's literal enumeration.
  - `NOT_DERIVED: Mapping[str, str]` — table → the reason it is outside the enumeration.
  - `DerivedScope` — frozen: `table: str`, `column: str`.
  - `DeleteDerivedRefused`, `ScopeNotDerived`, `UnratifiedResolution`, `MissingRetractionLimit`.
  - `delete_derived(scope: DerivedScope) -> NoReturn`.

**Done-means:** 8.

**Two signatures this task pins for its neighbours, because it cannot be written without them.**

1. **`policy.revoke_consent(conn, policy, scope, *, user_id, component_version, observed_at) -> str`
   records the withdrawal and returns the new `policy_version`. It appends no event.** The
   `consent_revoked` event is appended **here**, once, by `revoke`. Task 5's `Produces` block spells
   the function `revoke_consent(...)` with an ellipsis, and Task 15's `Consumes` block lists
   `authorship.CONSENT_REVOKED` and `database_agent.events.append_event` beside it — a list that is
   only coherent if the event append is `revoke`'s. Two appends would put one act in the log twice,
   and §8.4's `prior_releases` is read back out of that log.
2. **`AuditRecord.model` stores the `ModelTarget` as a mapping** with `locality`, `model_id` and
   `provider`. SPEC §8 requires `prior_releases[]` to carry *"model, provider, when, which
   excerpts"*; a bare model-name string leaves `PriorRelease.provider` unfillable, and §8.4's audit
   field is *"which model received the data"*, which a provider-less identifier does not answer for
   a hosted model.

**`retraction_limit` is a required keyword with no default, and the module holds no sentence.**
§8.4 states the `must`: *"Revocation cannot necessarily retract data already sent to an external
provider, so the product must communicate that distinction clearly."* The SPEC's *Deferred* table
puts the **wording** outside this contract — *"Consent-prompt and retraction-limit wording | §8.4 |
UX copy"* — while the plan's own Deferred row keeps the obligation: *"The **presence** of
`retraction_limit` is asserted; the wording is not."* So `revoke` refuses an empty one with
`MissingRetractionLimit` and stores whatever P13 supplies. Task 21 asserts no such sentence exists
as a module-level string anywhere under `src/privacy/`.

**`files_in_scope` is a required keyword with no default, and it is where Open question 3 lives.**
*"What is a 'corpus area'? … Consent grants cannot be scoped until this is named."* `revoke` cannot
enumerate the files a scope covers and must not guess; the caller supplies
`Callable[[str], Sequence[str]]` and P7 defines no area.

**`prior_releases` is every release in scope, not only those under the revoked policy version.**
§8.4's purpose is to tell the user what has already left the device. A list filtered to one policy
version answers a narrower question than the one the user is asking, and the audit log carries
`policy_version` on each record for a reader who wants the narrower one.

**What D3 makes this task write down.** The enumeration is the deliverable:

```text
DERIVED_PROJECTIONS
  evidence     raw_value, normalized_value, context_before, context_after
  text_units   text
```

Those five columns are where a scanned passport's OCR text actually lives — verified against the
live schema with `PRAGMA table_xinfo(evidence)` and `PRAGMA table_xinfo(text_units)`. `NOT_DERIVED`
names the four live tables outside it and why, so the refusal is legible:

```text
NOT_DERIVED
  events              append-only forever (R6, §8.2, D3). Three triggers and an authorizer hook.
  files               sensitivity_state is a classification projection (D2); reclassify, never delete.
  extraction_runs     the record THAT a run happened, not what it read (§2.4's empty-versus-absent).
  exclusion_verdicts  P3's refusal record; deleting it deletes the evidence of a refusal.
```

**No tombstone column is added.** `delete_derived` raises on both sides of the enumeration and
writes nothing. A test asserts that neither `evidence` nor `text_units` grew a deletion column.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_revocation.py
"""Done-means 8, and I6 held open under D3.

`retraction_limit` and the derived enumeration are the two halves of this task. The
first is a `must` whose wording is deferred, so the test asserts PRESENCE and refuses
to assert words. The second is D3's literal list, so the test asserts the list, the
refusal on both sides of it, and that no tombstone column was built.
"""
import json
import sqlite3

import pytest

from privacy.audit import AUDIT_FIELDS, AuditRecord, append_audit
from privacy.authorship import CONSENT_REVOKED, SUBSYSTEM
from privacy.policy import UNSET_POLICY_VERSION, Policy
from privacy.revocation import (
    DERIVED_PROJECTIONS, NOT_DERIVED, RELEASED, DeleteDerivedRefused, DerivedScope,
    MissingRetractionLimit, PriorRelease, ScopeNotDerived, UnratifiedResolution,
    delete_derived, revoke,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"

#: §8.4's obligation is the product's; the words are P13's. The test supplies them the
#: way P13 will, so nothing in `src/privacy/` has to hold a sentence.
RETRACTION_LIMIT = (
    "Revoking this policy stops future calls. It cannot retract the excerpts already "
    "sent to Acme, listed above."
)

_TYPED_DEFAULTS = {
    "audit_id": None,
    "release_id": "release-1",
    "policy_version": "policy-1",
    "plan_version": "plan-1",
    "stage": "grouping",
    "outcome": RELEASED,
    "operation_mode": "cloud_assisted",
    "authorizing_policy": "policy-1",
    "file_sensitivity": "personal_non_sensitive",
    "excerpts_included": (("obs-key-1", "0-19"),),
    "redaction_applied": False,
    "redaction_manifest": (),
    "model": {"locality": "cloud", "model_id": "acme-large", "provider": "Acme"},
    "content_hashes": ("sha256:abc",),
    "content_hash": "sha256:abc",
    "prompt_fingerprint": "fp-1",
    "file_id": "file-1",
    "file_ids": ("file-1",),
    "group_id": None,
    "consent_request_id": None,
    "user_id": None,
    "observed_at": FIXED_CLOCK,
    "appended_at": FIXED_CLOCK,
}


def an_audit_record(**over) -> AuditRecord:
    """Built from `AUDIT_FIELDS`, never from a literal keyword list.

    Task 10 owns SPEC §7's nineteen names and asserts they match §7 name for name.
    Constructing from the published tuple means a field this task never reads can be
    respelled without breaking it, while a field it DOES read disappearing fails here,
    loudly, at the seam that cares.
    """
    missing = [name for name in AUDIT_FIELDS if name not in _TYPED_DEFAULTS]
    assert not missing, (
        f"AUDIT_FIELDS names {missing} and this test has no value for them; SPEC §7 "
        "moved and Task 15 needs a value, not a default")
    values = {name: _TYPED_DEFAULTS[name] for name in AUDIT_FIELDS}
    values.update(over)
    return AuditRecord(**values)


def a_policy(**over) -> Policy:
    base = dict(policy_version="policy-1", operation_mode="cloud_assisted",
                consent_grants=(("Academics", "cloud_model"),),
                redaction_settings={"names": "redacted", "previews": "redacted",
                                    "thumbnails": "redacted", "ocr_text": "redacted",
                                    "location_data": "redacted"},
                automatic_move_permissions={}, plan_version="plan-1",
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


@pytest.fixture()
def released(p7_conn) -> int:
    """One prior release, in the log, under the policy about to be revoked."""
    return append_audit(p7_conn, an_audit_record(), author=SUBSYSTEM,
                        component_version=COMPONENT)


def go(conn, **over):
    base = dict(user_id="joseph", component_version=COMPONENT, observed_at=LATER,
                retraction_limit=RETRACTION_LIMIT,
                files_in_scope=lambda scope: ("file-1",))
    base.update(over)
    return revoke(conn, a_policy(), "Academics", **base)


# --- forward-only -----------------------------------------------------------

def test_effective_from_is_the_moment_of_revocation(p7_conn, released):
    # SPEC §8: "effective_from  future gate calls only."
    assert go(p7_conn).effective_from == LATER


def test_a_revocation_mints_a_new_policy_version(p7_conn, released):
    # The forward-only property is carried by a BINDING TERM, not by a flag. A release
    # minted under policy-1 still consumes against policy-1 (Task 12's ledger records
    # the version it was minted under), and a request made after this revocation is
    # decided against the new version, which is what makes Task 13's `policy_revoked`
    # reachable. Those two halves are asserted in Tasks 12 and 13 against signatures
    # this task cannot see; the seam that makes both true is asserted here.
    go(p7_conn)
    row = p7_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ? ORDER BY event_id DESC",
        (CONSENT_REVOKED,)).fetchone()
    payload = json.loads(row["explanation"])
    assert payload["revoked_policy_version"] == "policy-1"
    assert payload["policy_version"] != "policy-1"
    assert payload["effective_from"] == LATER


def test_the_revocation_is_authored_by_p7(p7_conn, released):
    # M8: the acting part authors, P1 writes.
    go(p7_conn)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CONSENT_REVOKED,)).fetchone()
    assert row["subsystem"] == "P7"
    assert row["user_id"] == "joseph"
    assert row["observed_at"] == LATER


# --- the prior-release list -------------------------------------------------

def test_prior_releases_name_model_provider_time_and_excerpts(p7_conn, released):
    # SPEC §8: "prior_releases[]  from the audit log: model, provider, when, which
    # excerpts." The audit log is what makes the retraction limit specific rather than
    # a generic disclaimer.
    assert go(p7_conn).prior_releases == (
        PriorRelease(model="acme-large", provider="Acme", when=FIXED_CLOCK,
                     excerpts=(("obs-key-1", "0-19"),)),
    )


def test_a_denied_record_is_not_a_prior_release(p7_conn, released):
    append_audit(p7_conn, an_audit_record(outcome="denied", release_id=None),
                 author=SUBSYSTEM, component_version=COMPONENT)
    assert len(go(p7_conn).prior_releases) == 1


def test_prior_releases_come_from_the_audit_log_and_not_a_second_store(p7_conn):
    # Nothing else in P7 records what left the device, and §8.4 forbids a second copy
    # of the text: "excerpts_included stores (observation_key, span) pairs ... not a
    # second copy of the text."
    assert go(p7_conn).prior_releases == ()
    append_audit(p7_conn, an_audit_record(), author=SUBSYSTEM,
                 component_version=COMPONENT)
    assert len(go(p7_conn).prior_releases) == 1


def test_a_file_outside_the_scope_is_not_listed(p7_conn, released):
    # Open question 3 is held by the injection: P7 defines no corpus area, so a
    # resolver returning nothing produces an empty list rather than everything.
    assert go(p7_conn, files_in_scope=lambda scope: ()).prior_releases == ()


def test_prior_releases_are_ordered_oldest_first(p7_conn, released):
    append_audit(p7_conn, an_audit_record(release_id="release-2", observed_at=LATER),
                 author=SUBSYSTEM, component_version=COMPONENT)
    assert [r.when for r in go(p7_conn).prior_releases] == [FIXED_CLOCK, LATER]


# --- the retraction limit ---------------------------------------------------

def test_the_retraction_limit_is_always_present(p7_conn, released):
    assert go(p7_conn).retraction_limit == RETRACTION_LIMIT


def test_an_empty_retraction_limit_is_refused(p7_conn, released):
    # §8.4 is a `must`: the product "must communicate that distinction clearly".
    # Presence is enforced; wording is P13's (SPEC Deferred).
    for empty in ("", "   "):
        with pytest.raises(MissingRetractionLimit):
            go(p7_conn, retraction_limit=empty)


def test_the_wording_is_the_callers_and_not_the_modules():
    # SPEC Deferred: "Consent-prompt and retraction-limit wording ... UX copy."
    import privacy.revocation as module
    held = [value for name, value in vars(module).items()
            if not name.startswith("__") and isinstance(value, str)]
    assert not [text for text in held if "retract" in text.lower()]


# --- the substrate proves Done-means 8, not P7's restraint -------------------

def test_deleting_an_audit_record_aborts(p7_conn, released):
    # P1's `events_no_delete`. Done-means 8: revoke "never deletes an audit record",
    # and the proof is the database refusing, not P7 declining to try.
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        p7_conn.execute("DELETE FROM events WHERE event_id = ?", (released,))


def test_updating_an_audit_record_aborts(p7_conn, released):
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        p7_conn.execute("UPDATE events SET subsystem = 'P8' WHERE event_id = ?",
                        (released,))


def test_the_append_only_triggers_cannot_be_dropped(p7_conn):
    # `db._deny_events_history_loss`, installed by `open_database` as a
    # `set_authorizer` hook: SQLITE_DROP_TRIGGER on the three names, and DROP TABLE
    # events, both return SQLITE_DENY.
    for statement in ("DROP TRIGGER events_no_delete",
                      "DROP TRIGGER events_no_update",
                      "DROP TRIGGER events_no_replace",
                      "DROP TABLE events"):
        with pytest.raises(sqlite3.DatabaseError, match="not authorized"):
            p7_conn.execute(statement)


def test_a_revocation_adds_a_row_and_removes_none(p7_conn, released):
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    go(p7_conn)
    after = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    assert after == before + 1
    assert p7_conn.execute("SELECT count(*) c FROM events WHERE event_id = ?",
                           (released,)).fetchone()["c"] == 1


# --- D3: the enumeration, and delete_derived refusing on both sides ----------

def test_delete_derived_refuses_an_enumerated_scope_and_names_i6():
    # D3 ratified the DIRECTION and built nothing: "No tombstone column is built until
    # P13 drives it." The surface exists; the semantics do not.
    with pytest.raises(UnratifiedResolution) as caught:
        delete_derived(DerivedScope("text_units", "text"))
    assert "I6" in str(caught.value)
    assert "D3" in str(caught.value)


def test_delete_derived_refuses_an_unenumerated_scope_by_name():
    # The point of a LITERAL enumeration: a table nobody listed is a red test, not a
    # silent miss. `ScopeNotDerived` is a different failure from "not built yet" and
    # the two must not be readable as one.
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("extraction_runs", "completeness"))
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("evidence", "reliability"))


def test_both_refusals_share_one_base_so_delete_derived_never_succeeds():
    for scope in (DerivedScope("text_units", "text"),
                  DerivedScope("nowhere", "nothing")):
        with pytest.raises(DeleteDerivedRefused):
            delete_derived(scope)


def test_events_is_named_as_outside_the_enumeration():
    # D3's first clause. `events` is not merely absent from DERIVED_PROJECTIONS; the
    # reason is written down, because absence and oversight look identical.
    assert "events" not in DERIVED_PROJECTIONS
    assert "events" in NOT_DERIVED
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("events", "explanation"))


def test_sensitivity_state_is_reclassified_and_never_deleted():
    # D2: the column is a PROJECTION of P7's authoritative record. The supported user
    # act is Task 16's reclassification, which supersedes; deleting a projection would
    # leave the authoritative record and its mirror disagreeing.
    assert "files" not in DERIVED_PROJECTIONS
    assert "files" in NOT_DERIVED
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("files", "sensitivity_state"))


def test_the_enumeration_names_only_live_tables_and_live_columns(p7_conn):
    # An enumeration that drifts from the schema is worse than none: it would refuse a
    # real column and accept a name that no longer exists.
    for table, columns in DERIVED_PROJECTIONS.items():
        live = {row[1] for row in p7_conn.execute(f"PRAGMA table_xinfo({table})")}
        assert live, table
        assert set(columns) <= live, (table, sorted(set(columns) - live))
    for table in NOT_DERIVED:
        assert {row[1] for row in p7_conn.execute(f"PRAGMA table_xinfo({table})")}


def test_the_enumerated_columns_are_where_ocr_text_actually_lives():
    # I6's own worked case: "The product cannot ship unable to forget a scanned
    # passport's OCR text." That text is `text_units.text` and `evidence.raw_value`
    # with M5's two context fields; nothing else in the schema holds it.
    assert DERIVED_PROJECTIONS["text_units"] == ("text",)
    assert DERIVED_PROJECTIONS["evidence"] == (
        "raw_value", "normalized_value", "context_before", "context_after")


def test_no_tombstone_column_was_built(p7_conn):
    # D3's second clause, and the whole reason it is a clause:
    # `files.sensitivity_state` spent this project as a column nothing wrote and
    # produced a second wrong value one column away. A migration later is cheaper.
    for table in DERIVED_PROJECTIONS:
        columns = {row[1] for row in p7_conn.execute(f"PRAGMA table_xinfo({table})")}
        for token in ("tombstone", "tombstoned", "deleted", "deleted_at",
                      "redacted_at", "forgotten"):
            assert token not in columns, (table, token)


def test_thirteen_tables_already_refuse_a_delete(p7_conn):
    # The substrate D3 lands on top of, counted rather than remembered: events,
    # evidence, text_units, extraction_runs, exclusion_verdicts and P2's eight
    # bundle_* tables. "Deletion later is always available; un-deletion never is" is a
    # posture the schema already holds.
    from eval_harness.store import create_eval_schema
    from scan_agent.schema import create_scan_schema
    create_scan_schema(p7_conn)
    create_eval_schema(p7_conn)
    guarded = {row["tbl_name"] for row in p7_conn.execute(
        "SELECT tbl_name, sql FROM sqlite_master WHERE type = 'trigger'")
        if "BEFORE DELETE" in (row["sql"] or "")}
    assert len(guarded) == 13
    assert {"events", "evidence", "text_units", "extraction_runs",
            "exclusion_verdicts"} <= guarded


def test_p7_creates_no_trigger_of_its_own_on_events(p7_conn):
    # P1 owns R6. A second set of triggers under a second set of names is the
    # duplication that has cost this project most.
    names = {row["name"] for row in p7_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'trigger' "
        "AND tbl_name = 'events'")}
    assert names == {"events_no_update", "events_no_delete", "events_no_replace"}
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_revocation.py -v`
Expected: FAIL — `ImportError: cannot import name 'DERIVED_PROJECTIONS' from 'privacy.revocation'`
(the module does not exist, so collection fails on the first import).

- [ ] **Step 3: Write `src/privacy/revocation.py`**

```python
# src/privacy/revocation.py
"""§8.4's revocation, its stated limit, and the derived-data deletion D3 left unbuilt.

Three things are decided here and each is a quotation rather than a choice:

- **Revocation is forward-only.** §8.4 gives the user the right to "revoke a policy
  for future runs". A revocation appends; it never rewrites the record of what has
  already happened, because §8.4 also requires the product to say what already left,
  and that is unsatisfiable once the send record is erasable.
- **The retraction limit is mandatory and its wording is not P7's.** §8.4: "Revocation
  cannot necessarily retract data already sent to an external provider, so the product
  must communicate that distinction clearly." The SPEC defers the copy to P13; this
  module enforces presence and holds no sentence.
- **`delete_derived` refuses, on both sides of a literal list (D3).** §8.4 gives the
  user the right to "review and delete local derived data" and §8.2 forbids updating
  or deleting an event. D3 ratifies the direction -- events append-only forever,
  derived projections tombstonable, "derived" a literal enumeration -- and ratifies
  that NOTHING IS BUILT until P13 drives it. So the surface exists and the semantics
  do not, and an unenumerated scope fails differently from an unbuilt one.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import NoReturn

from database_agent.events import append_event
from evidence_shape.canonical import canonical_json

from privacy.audit import audit_records_for
from privacy.authorship import CONSENT_REVOKED, event_defaults
from privacy.policy import Policy, revoke_consent

#: The `AuditRecord.outcome` value that means content left the device (SPEC §7).
RELEASED: str = "released"


class MissingRetractionLimit(ValueError):
    """§8.4 requires the distinction be communicated; a blank statement is not one."""


class DeleteDerivedRefused(Exception):
    """`delete_derived` never succeeds today. It refuses for one of two reasons."""


class ScopeNotDerived(DeleteDerivedRefused):
    """The scope is outside D3's literal enumeration.

    This is why the list is literal rather than a predicate: a table nobody enumerated
    produces a red test here instead of being quietly deleted from, or quietly skipped,
    depending on which way a clever rule happened to fall.
    """


class UnratifiedResolution(DeleteDerivedRefused):
    """The scope IS derived, and no tombstone column is built (D3, I6).

    The name is the one the plan skeleton published and it is kept so the contract does
    not move; what it now reports is *unbuilt*, not *unratified*. D3 settled the
    direction on 2026-08-21 and deliberately built nothing, because a writer-less column
    is the defect `files.sensitivity_state` demonstrated for the length of this project.
    """


@dataclass(frozen=True)
class PriorRelease:
    """One row of SPEC §8's `prior_releases[]`: "model, provider, when, which excerpts"."""

    model: str
    provider: str
    when: str
    excerpts: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class RevocationResult:
    """SPEC §8's return: forward-only, evidenced, and limited."""

    effective_from: str
    prior_releases: tuple[PriorRelease, ...]
    retraction_limit: str


@dataclass(frozen=True)
class DerivedScope:
    """One table-and-column D3's enumeration may or may not name."""

    table: str
    column: str


#: D3's literal enumerated table-and-column list. These five columns are where the text
#: extracted from a file's bytes actually lives -- checked against the live schema, not
#: against a PLAN. Anything else is `NOT_DERIVED` and refused by name.
DERIVED_PROJECTIONS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "evidence": ("raw_value", "normalized_value", "context_before", "context_after"),
    "text_units": ("text",),
})

#: The live tables outside the enumeration, each with the reason. Absence and oversight
#: are indistinguishable, so the reason is written down.
NOT_DERIVED: Mapping[str, str] = MappingProxyType({
    "events": (
        "append-only forever (R6, §8.2, D3). Three triggers and an authorizer hook "
        "enforce it, and §8.4's retraction limit is unsatisfiable without the log."
    ),
    "files": (
        "`sensitivity_state` is a projection of P7's authoritative ClassificationRecord "
        "(D2). The supported user act is reclassification, which supersedes."
    ),
    "extraction_runs": (
        "the record THAT a run happened, not what it read. §2.4 distinguishes an empty "
        "extraction result from an extractor that does not yet exist, and dropping the "
        "run row collapses the two."
    ),
    "exclusion_verdicts": (
        "P3's refusal record. Deleting it deletes the evidence that a refusal occurred, "
        "which is the whole record a protected container leaves behind (11 §4b)."
    ),
})


def revoke(conn: sqlite3.Connection, policy: Policy, scope: str, *, user_id: str,
           component_version: str, observed_at: str, retraction_limit: str,
           files_in_scope: Callable[[str], Sequence[str]]) -> RevocationResult:
    """Withdraw consent for `scope`, forward only, and say what already left.

    `files_in_scope` has no default. Open question 3 -- "What is a 'corpus area'? ...
    Consent grants cannot be scoped until this is named" -- is unanswered, so the
    resolver is the caller's and P7 defines no area.

    `retraction_limit` has no default either, and for the opposite reason: §8.4 makes
    the statement mandatory and the SPEC defers its wording, so presence is enforced
    here and the words come from P13.
    """
    if not retraction_limit or not retraction_limit.strip():
        raise MissingRetractionLimit(
            "§8.4: revocation 'cannot necessarily retract data already sent to an "
            "external provider, so the product must communicate that distinction "
            "clearly' -- an empty statement does not communicate it"
        )
    new_version = revoke_consent(conn, policy, scope, user_id=user_id,
                                 component_version=component_version,
                                 observed_at=observed_at)
    prior = _prior_releases(conn, files_in_scope(scope))
    append_event(conn, **event_defaults(
        event_type=CONSENT_REVOKED,
        user_id=user_id,
        component_version=component_version,
        observed_at=observed_at,
        explanation=canonical_json({
            "scope": scope,
            "revoked_policy_version": policy.policy_version,
            "policy_version": new_version,
            "effective_from": observed_at,
            "prior_release_count": len(prior),
            "retraction_limit": retraction_limit,
        }),
    ))
    return RevocationResult(effective_from=observed_at, prior_releases=prior,
                            retraction_limit=retraction_limit)


def _prior_releases(conn: sqlite3.Connection,
                    file_ids: Sequence[str]) -> tuple[PriorRelease, ...]:
    """Every release in scope, oldest first, read out of the one audit log.

    Not filtered to the revoked policy version. §8.4's purpose is to tell the user what
    has already been sent; a list narrowed to one version answers a different question,
    and each record carries `policy_version` for a reader who wants it.
    """
    found: list[tuple[str, int, PriorRelease]] = []
    for file_id in file_ids:
        for record in audit_records_for(conn, file_id=file_id):
            if record.outcome != RELEASED:
                continue
            target = record.model
            found.append((record.observed_at, int(record.audit_id), PriorRelease(
                model=target["model_id"],
                provider=target["provider"],
                when=record.observed_at,
                excerpts=tuple(tuple(pair) for pair in record.excerpts_included),
            )))
    found.sort(key=lambda item: (item[0], item[1]))
    return tuple(entry for _, _, entry in found)


def delete_derived(scope: DerivedScope) -> NoReturn:
    """§8.4's "review and delete local derived data" -- surfaced, and unbuilt (D3, I6).

    Raises `ScopeNotDerived` for anything outside `DERIVED_PROJECTIONS` and
    `UnratifiedResolution` for anything inside it. There is no third branch: no
    tombstone column exists, this function writes nothing, and P13 is the part that
    will drive the migration that gives it one.
    """
    columns = DERIVED_PROJECTIONS.get(scope.table)
    if columns is None or scope.column not in columns:
        reason = NOT_DERIVED.get(scope.table)
        enumerated = {table: list(cols)
                      for table, cols in DERIVED_PROJECTIONS.items()}
        raise ScopeNotDerived(
            f"{scope.table}.{scope.column} is not in D3's enumerated derived list "
            f"{enumerated}" + (f"; {reason}" if reason else "")
        )
    raise UnratifiedResolution(
        f"{scope.table}.{scope.column} is derived (D3), and no tombstone column is "
        "built. D3, ratified 2026-08-21, settled the direction and deliberately built "
        "nothing until P13 drives it; I6 named the §8.4-versus-§8.2 conflict it "
        "resolves. Deletion later is always available; un-deletion never is."
    )
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_revocation.py -v`
Expected: PASS — 22 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–15 green, and 1302 P1–P5 tests still green (P7 modified no file belonging
to another part).

- [ ] **Step 6: Commit**

```bash
git add src/privacy/revocation.py tests/p7/test_p7_revocation.py
git commit -m "feat(P7): revocation, the retraction limit, and delete_derived refusing on both sides of D3's enumeration"
```

---

---

### Task 16: Reclassification, and §8.7's query-before-classify

**Files:**
- Create: `src/privacy/learning_seam.py`
- Modify: `src/privacy/gate.py` (add `Gate.reclassify`, delegating to this module — SPEC §8 publishes it on the facade, and **D13 kept CUT 4**, so the facade is certain rather than provisional)
- Test: `tests/p7/test_p7_learning_seam.py`

**Interfaces:**
- Consumes: `database_agent.learning.learning_records(conn, scope, subject_id) -> list[sqlite3.Row]`,
  `.SCOPES`, `.reset_preferences`, `database_agent.events.CORRECTION_FIELDS`, `.CORRECTION_SCOPES`,
  `.append_event`, `database_agent.files_table.set_sensitivity_state`,
  `evidence_shape.canonical.canonical_json`, `privacy.classification.ClassificationRecord`,
  `privacy.classification_store.ClassificationStore`, `.mirror_state` (the skeleton's
  `facts_seam.SensitivityFacts` — see the rename note above), `privacy.authorship.SUBSYSTEM`,
  `.CLASSIFICATION_ASSIGNED`, `.CLASSIFICATION_SUPERSEDED`, `.event_defaults`,
  `privacy.vocabulary.check_handling_class`.
- Produces (`learning_seam.py`):
  - `PROPOSAL_CLASS: str = "privacy"`, `FILE_SCOPE: str = "file"`, `ACCEPT: str`, `REJECT: str`.
  - `RECORDED_ACTIONS: tuple[str, ...]` (SPEC *Correction learning*'s six),
    `RECORDED_ACTION_SOURCES: Mapping[str, str]` (each identifier → the SPEC's own phrase),
    `check_recorded_action(value) -> str`, `UnknownRecordedAction`.
  - `basis_key_for(file_id, handling_class) -> str`.
  - `suppressed(conn, file_id, handling_class) -> bool`.
  - `assign(conn, record, *, store, component_version) -> ClassificationRecord | None`.
  - `reclassify(conn, file_id, handling_class, reason, *, store, content_hash, protected,
    evidence_refs, user_id, component_version, observed_at, correction_scope=FILE_SCOPE)
    -> ClassificationRecord`.

**Done-means:** part of 2 (the user-revision half), and the §8.7 obligation.

**`assign` is added by this task and it is what makes the Done-means falsifiable.** The skeleton's
`Produces` block lists `suppressed` and stops, and 10-i4's Done-means is *"a fixture with one
unresected reject at the stated `basis_key` produces **zero re-emissions** of that proposal."* A
predicate returning `True` is not zero re-emissions; something has to be the emission that does not
happen. `assign` is the system-side write — the one a detector would call — and it returns `None`
when suppressed. Reported as an addition.

**Suppression guards `assign` and never `reclassify`.** 10-i4's table: *"**P7** | Before assigning a
handling class the user has already set or rejected at this scope | Do not re-prompt the same
classification."* What is suppressed is the product re-proposing, not the user acting. A
`reclassify` that consulted the suppression store would refuse the user's own correction on the
grounds that they had already made it.

**`assign` appends no correction field, so it can never be its own suppressor.** P1's
`learning_records` filters `user_id IS NOT NULL`, which makes a system assignment structurally
incapable of becoming a learning record. Only `reclassify`, which carries a `user_id`, writes one.

**One event per act, and the event is the rejection.** A reclassification over an existing
classification appends exactly one `classification_superseded` with `polarity = "reject"` at
`basis_key_for(file_id, prior_class)` — §8.7's negative example, *"stored with the evidence that
produced them"* — and supersedes through P1's three columns. A reclassification where nothing was
classified appends one `classification_assigned` with `polarity = "accept"` at the new class. There
is no accept-and-reject pair: 10-i4 rule 4 says *"A `polarity = accept` record at the same
`basis_key` is not a suppression and must not be read as one"*, so the second event would be a row
that changes nothing plus a second place for the two to disagree.

**The keys, not the ids (M14).** *"a per-row `observation_id` dies when the extractor is upgraded,
so a negative example recorded today would silently stop resolving and the same false protection
would return."* `evidence_refs` is a required keyword carrying P4 `observation_key` values; it lands
on the new record and is echoed into the superseding event's explanation as
`rejected_evidence_refs`.

**`correction_scope` defaults to `file`, and that default is the design's own.** §8.7's worked
warning: one transcript belonging in one packet *"should not teach the engine that all transcripts
belong there."* A broader scope is accepted when the caller passes one and is never inferred. Open
question 7 — *"Does repeated reclassification generalize?"* — stays open; nothing here counts
repetitions, and Task 21 asserts it.

**`protected` is a required keyword on `reclassify` and is never derived.** SPEC §2:
*"Neighbouring parts should consume the `protected` flag, not infer it from the class"*, and Open
question 1 is unsettled.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_learning_seam.py
"""§8.7's query-before-classify, and reclassification as supersession.

The three assertions 10-i4-learning-ops.md's Done-means names, in its own words:
"a fixture with one unresected reject at the stated `basis_key` produces zero
re-emissions of that proposal ... A different `basis_key` at the same scope still
emits. A reset at that scope+subject allows emission again."
"""
import json

import pytest

from database_agent.events import CORRECTION_FIELDS, CORRECTION_SCOPES, append_event
from database_agent.files_table import get_file, record_file
from database_agent.learning import SCOPES, learning_records, reset_preferences

from privacy.authorship import (
    CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, SUBSYSTEM,
)
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.learning_seam import (
    ACCEPT, FILE_SCOPE, PROPOSAL_CLASS, RECORDED_ACTIONS, RECORDED_ACTION_SOURCES,
    REJECT, UnknownRecordedAction, assign, basis_key_for, check_recorded_action,
    reclassify, suppressed,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"
DETECTOR_KEYS = (
    "sha256:ba9777bcba0096decc525198035644949d2357bf7f9a9cb3492c948c86c0fcbd",
    "sha256:11e3d2a5b8c47f6019a4d3e5c7b2a10f9d8c6b4a3e2f1d0c9b8a7654321fedcba",
)


@pytest.fixture()
def file_id(p7_conn, tmp_path):
    """A real P1 row: the classification is keyed on (file_id, content_hash) and a
    synthesized id would not exercise the projection onto `files`."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    document = corpus / "passport-scan.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    return record_file(
        p7_conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


@pytest.fixture()
def content_hash(p7_conn, file_id):
    return get_file(p7_conn, file_id)["content_hash"]


@pytest.fixture()
def store(p7_conn):
    return ClassificationStore(p7_conn)


def a_record(file_id, content_hash, handling_class="sensitive_personal", **over):
    base = dict(file_id=file_id, content_hash=content_hash,
                handling_class=handling_class, protected=True, basis="detector",
                evidence_refs=DETECTOR_KEYS, reliability_state="validated",
                observed_at=FIXED_CLOCK)
    base.update(over)
    return ClassificationRecord(**base)


def a_user_rejection(conn, file_id, content_hash, *, store):
    """The user downgrading `sensitive_personal`, which is what leaves the reject."""
    return reclassify(conn, file_id, "personal_non_sensitive",
                      "these are my own notes, not an identity record",
                      store=store, content_hash=content_hash, protected=False,
                      evidence_refs=DETECTOR_KEYS, user_id="joseph",
                      component_version=COMPONENT, observed_at=LATER)


# --- the vocabulary ---------------------------------------------------------

def test_the_proposal_class_is_the_one_10_i4_assigns_p7():
    # 10-i4-learning-ops.md's table: `privacy` | `(file_id, handling_class)` | P7.
    assert PROPOSAL_CLASS == "privacy"


def test_the_basis_key_is_file_id_and_handling_class_and_nothing_else():
    key = basis_key_for("file-1", "sensitive_personal")
    assert json.loads(key) == ["file-1", "sensitive_personal"]
    assert basis_key_for("file-1", "sensitive_personal") == key
    assert basis_key_for("file-1", "public_low") != key


def test_the_six_recorded_actions_carry_the_specs_own_words():
    # SPEC Correction learning, "Recorded actions". A paraphrase is a failing test and
    # not an editorial choice -- Task 2's MODE_SEMANTICS discipline, applied here.
    assert len(RECORDED_ACTIONS) == 6
    assert set(RECORDED_ACTION_SOURCES) == set(RECORDED_ACTIONS)
    assert RECORDED_ACTION_SOURCES["reclassify_private"] == (
        "reclassifying a file as private")
    assert RECORDED_ACTION_SOURCES["mark_private_residual_review"] == (
        "mark it as private")
    assert RECORDED_ACTION_SOURCES["downgrade_classification"] == (
        "downgrading a classification")
    assert RECORDED_ACTION_SOURCES["set_policy"] == (
        "granting, changing, or revoking a policy")
    assert RECORDED_ACTION_SOURCES["change_redaction_setting"] == (
        "changing a redaction setting")
    assert RECORDED_ACTION_SOURCES["set_automatic_move_permission"] == (
        "granting or withdrawing an automatic-move permission for protected material")


def test_a_seventh_recorded_action_is_a_load_error():
    assert check_recorded_action("downgrade_classification") == (
        "downgrade_classification")
    with pytest.raises(UnknownRecordedAction):
        check_recorded_action("delete_the_file")


def test_the_default_scope_is_file_and_it_is_one_of_p1s_six():
    # §8.7's worked warning: one transcript belonging in one packet "should not teach
    # the engine that all transcripts belong there."
    assert FILE_SCOPE == "file"
    assert FILE_SCOPE in SCOPES and FILE_SCOPE in CORRECTION_SCOPES


# --- query before classify --------------------------------------------------

def test_an_unrejected_class_is_not_suppressed(p7_conn, file_id):
    assert suppressed(p7_conn, file_id, "sensitive_personal") is False


def test_an_unreset_reject_produces_zero_re_emissions(
        p7_conn, file_id, content_hash, store):
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    assert suppressed(p7_conn, file_id, "sensitive_personal") is True

    before = p7_conn.execute(
        "SELECT count(*) c FROM events WHERE event_type = ?",
        (CLASSIFICATION_ASSIGNED,)).fetchone()["c"]
    again = assign(p7_conn, a_record(file_id, content_hash), store=store,
                   component_version=COMPONENT)
    after = p7_conn.execute(
        "SELECT count(*) c FROM events WHERE event_type = ?",
        (CLASSIFICATION_ASSIGNED,)).fetchone()["c"]

    assert again is None
    assert after == before


def test_a_different_basis_key_at_the_same_scope_still_emits(
        p7_conn, file_id, content_hash, store):
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    emitted = assign(
        p7_conn,
        a_record(file_id, content_hash,
                 handling_class="highly_sensitive_credential_bearing"),
        store=store, component_version=COMPONENT)
    assert emitted is not None
    assert emitted.handling_class == "highly_sensitive_credential_bearing"


def test_a_reset_restores_emission(p7_conn, file_id, content_hash, store):
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    assert suppressed(p7_conn, file_id, "sensitive_personal") is True
    reset_preferences(p7_conn, FILE_SCOPE, file_id, author=SUBSYSTEM,
                      component_version=COMPONENT, user_id="joseph")
    assert suppressed(p7_conn, file_id, "sensitive_personal") is False
    assert assign(p7_conn, a_record(file_id, content_hash), store=store,
                  component_version=COMPONENT) is not None


def test_p7_does_the_filtering_because_p1s_reader_does_not(
        p7_conn, file_id, content_hash, store):
    # `learning_records(conn, scope, subject_id)` filters on correction_scope,
    # correction_subject and `user_id IS NOT NULL` only. 10-i4 assigns proposal_class
    # and basis_key filtering to the acting part: "Ignores records at the wrong
    # `proposal_class`. Ignores records whose `basis_key` does not match."
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    rows = learning_records(p7_conn, FILE_SCOPE, file_id)
    assert len(rows) == 1
    assert rows[0]["proposal_class"] == PROPOSAL_CLASS
    assert rows[0]["basis_key"] == basis_key_for(file_id, "sensitive_personal")
    assert rows[0]["polarity"] == REJECT
    # Another part's rejection at the same subject is ignored, not counted.
    append_event(p7_conn, event_type="review action routed", subsystem="P13",
                 component_version=COMPONENT, observed_at=LATER,
                 explanation='{"note":"another part"}', user_id="joseph",
                 correction_scope=FILE_SCOPE, correction_subject=file_id,
                 polarity=REJECT, proposal_class="placement",
                 basis_key=basis_key_for(file_id, "sensitive_personal"))
    assert len(learning_records(p7_conn, FILE_SCOPE, file_id)) == 2
    assert suppressed(p7_conn, file_id, "sensitive_personal") is True
    assert suppressed(p7_conn, file_id, "public_low") is False


def test_a_system_assignment_can_never_become_a_learning_record(
        p7_conn, file_id, content_hash, store):
    # P1's reader requires `user_id IS NOT NULL`. A detector's assignment carries no
    # user, so it is structurally incapable of suppressing the next one.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    assert learning_records(p7_conn, FILE_SCOPE, file_id) == []
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CLASSIFICATION_ASSIGNED,)).fetchone()
    for field in CORRECTION_FIELDS:
        assert row[field] is None
    assert row["user_id"] is None


# --- reclassification is supersession, never overwrite ----------------------

def test_reclassify_writes_a_new_user_confirmed_fact(
        p7_conn, file_id, content_hash, store):
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    revised = a_user_rejection(p7_conn, file_id, content_hash, store=store)
    assert revised.reliability_state == "user_confirmed"
    assert revised.basis == "user"
    assert revised.handling_class == "personal_non_sensitive"
    assert store.current(file_id, content_hash) == revised


def test_both_records_remain_inspectable(p7_conn, file_id, content_hash, store):
    # §8.2's explicit rule, and §8.4's "can be revised by the user" -- a revision
    # supersedes and both remain available.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    history = store.history(file_id)
    assert [r.handling_class for r in history] == [
        "sensitive_personal", "personal_non_sensitive"]
    assert [r.basis for r in history] == ["detector", "user"]


def test_reclassify_appends_classification_superseded_and_not_an_overwrite(
        p7_conn, file_id, content_hash, store):
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CLASSIFICATION_SUPERSEDED,)).fetchone()
    assert row["subsystem"] == "P7"
    assert row["user_id"] == "joseph"
    assert row["polarity"] == REJECT
    assert row["correction_scope"] == FILE_SCOPE
    assert row["correction_subject"] == file_id
    assert row["basis_key"] == basis_key_for(file_id, "sensitive_personal")


def test_a_first_classification_by_the_user_accepts_rather_than_rejects(
        p7_conn, file_id, content_hash, store):
    # Nothing was classified, so there is nothing to reject. One event, and it is an
    # assignment: 10-i4 rule 4 makes an accept-and-reject pair a row that changes
    # nothing plus a second place for the two to disagree.
    reclassify(p7_conn, file_id, "highly_sensitive_credential_bearing",
               "this is my passport", store=store, content_hash=content_hash,
               protected=True, evidence_refs=(), user_id="joseph",
               component_version=COMPONENT, observed_at=LATER)
    assert p7_conn.execute("SELECT count(*) c FROM events WHERE event_type = ?",
                           (CLASSIFICATION_SUPERSEDED,)).fetchone()["c"] == 0
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CLASSIFICATION_ASSIGNED,)).fetchone()
    assert row["polarity"] == ACCEPT
    assert row["basis_key"] == basis_key_for(
        file_id, "highly_sensitive_credential_bearing")


def test_a_downgrade_stores_the_observation_keys_the_detector_fired_on(
        p7_conn, file_id, content_hash, store):
    # §8.7 and M14: "The key, not the id, is what makes that durable" -- a per-row
    # `observation_id` dies when the extractor is upgraded and the same false
    # protection returns.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    row = p7_conn.execute("SELECT explanation FROM events WHERE event_type = ?",
                          (CLASSIFICATION_SUPERSEDED,)).fetchone()
    payload = json.loads(row["explanation"])
    assert tuple(payload["rejected_evidence_refs"]) == DETECTOR_KEYS
    assert all(ref.startswith("sha256:") for ref in payload["rejected_evidence_refs"])
    assert payload["superseded_handling_class"] == "sensitive_personal"


def test_protected_is_carried_and_never_derived_from_the_class(
        p7_conn, file_id, content_hash, store):
    # SPEC §2, and Open question 1. A caller may mark a `public_low` file protected and
    # this module does not argue.
    record = reclassify(p7_conn, file_id, "public_low", "a scan of my own poster",
                        store=store, content_hash=content_hash, protected=True,
                        evidence_refs=(), user_id="joseph",
                        component_version=COMPONENT, observed_at=LATER)
    assert record.handling_class == "public_low"
    assert record.protected is True


def test_a_reason_is_required(p7_conn, file_id, content_hash, store):
    with pytest.raises(ValueError):
        reclassify(p7_conn, file_id, "public_low", "   ", store=store,
                   content_hash=content_hash, protected=False, evidence_refs=(),
                   user_id="joseph", component_version=COMPONENT, observed_at=LATER)


def test_a_scope_outside_8_7s_six_is_refused(p7_conn, file_id, content_hash, store):
    with pytest.raises(ValueError):
        reclassify(p7_conn, file_id, "public_low", "because", store=store,
                   content_hash=content_hash, protected=False, evidence_refs=(),
                   user_id="joseph", component_version=COMPONENT, observed_at=LATER,
                   correction_scope="everything")


def test_the_projection_onto_files_goes_through_p1s_setter(
        p7_conn, file_id, content_hash, store):
    # D2: `files.sensitivity_state` is the projection of the authoritative record,
    # written through P1's published `set_sensitivity_state`. Task 21 asserts
    # `src/privacy/` issues no `UPDATE files` of its own.
    assert get_file(p7_conn, file_id)["sensitivity_state"] is None
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    state = json.loads(get_file(p7_conn, file_id)["sensitivity_state"])
    assert state["handling_class"] == "sensitive_personal"
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    state = json.loads(get_file(p7_conn, file_id)["sensitivity_state"])
    assert state["handling_class"] == "personal_non_sensitive"


def test_open_question_7_is_not_answered_here(p7_conn, file_id, content_hash, store):
    # OQ7: "§8.7 allows a repeated residual destination to become a corpus-level
    # preference; it does not say whether repeated privacy corrections may raise a
    # sensitivity floor for a class of files." Two rejections stay two file-scoped
    # records; nothing counts them and nothing widens.
    for _ in range(2):
        assign(p7_conn, a_record(file_id, content_hash), store=store,
               component_version=COMPONENT)
        a_user_rejection(p7_conn, file_id, content_hash, store=store)
    for scope in ("corpus", "domain", "group", "node", "template"):
        assert learning_records(p7_conn, scope, file_id) == []
    import privacy.learning_seam as module
    assert not [name for name, value in vars(module).items()
                if not name.startswith("__")
                and isinstance(value, (int, float)) and not isinstance(value, bool)]
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_learning_seam.py -v`
Expected: FAIL — `ImportError: cannot import name 'ACCEPT' from 'privacy.learning_seam'`

- [ ] **Step 3: Write `src/privacy/learning_seam.py`**

```python
# src/privacy/learning_seam.py
"""§8.7's query-before-classify, and reclassification as supersession.

Two directions across one seam. Reading: before the product assigns a handling class it
asks P1 whether the user has already rejected that class for that file, because
10-i4-learning-ops.md puts P7 in the query-before-propose table -- "Before assigning a
handling class the user has already set or rejected at this scope | Do not re-prompt the
same classification". Writing: a user reclassification is a new `user_confirmed` fact
that supersedes the prior one and leaves a negative example behind, because §8.7
requires rejections be "stored with the evidence that produced them".

P1's `learning_records(conn, scope, subject_id)` filters on `correction_scope`,
`correction_subject` and `user_id IS NOT NULL` and nothing else. `proposal_class` and
`basis_key` filtering is the acting part's, by 10-i4's own assignment, so it happens
here.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence
from types import MappingProxyType

from database_agent.events import CORRECTION_SCOPES, append_event
from database_agent.files_table import set_sensitivity_state
from database_agent.learning import learning_records
from evidence_shape.canonical import canonical_json

from privacy.authorship import (
    CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, SUBSYSTEM, event_defaults,
)
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore, mirror_state
from privacy.vocabulary import check_handling_class

#: 10-i4-learning-ops.md's table: `privacy` | `(file_id, handling_class)` | P7.
PROPOSAL_CLASS: str = "privacy"

#: §8.7's default, and the only scope this module supplies. "one particular transcript
#: belongs in a Columbia packet but should not teach the engine that all transcripts
#: belong there."
FILE_SCOPE: str = "file"

#: 10-i4: "`polarity ∈ accept | reject` ... supplied by the acting part, never inferred".
ACCEPT: str = "accept"
REJECT: str = "reject"

#: SPEC *Correction learning*, "Recorded actions". The identifiers are P7's; the phrases
#: are the SPEC's, held beside them so a later paraphrase is a failing test.
RECORDED_ACTIONS: tuple[str, ...] = (
    "reclassify_private",
    "mark_private_residual_review",
    "downgrade_classification",
    "set_policy",
    "change_redaction_setting",
    "set_automatic_move_permission",
)

RECORDED_ACTION_SOURCES: Mapping[str, str] = MappingProxyType({
    "reclassify_private": "reclassifying a file as private",
    "mark_private_residual_review": "mark it as private",
    "downgrade_classification": "downgrading a classification",
    "set_policy": "granting, changing, or revoking a policy",
    "change_redaction_setting": "changing a redaction setting",
    "set_automatic_move_permission":
        "granting or withdrawing an automatic-move permission for protected material",
})


class UnknownRecordedAction(ValueError):
    """A §8.7 action outside the SPEC's six. A value outside the set is a load error."""


def check_recorded_action(value: str) -> str:
    if value not in RECORDED_ACTIONS:
        raise UnknownRecordedAction(
            f"{value!r} is not one of SPEC Correction learning's six recorded actions "
            f"{RECORDED_ACTIONS}")
    return value


def basis_key_for(file_id: str, handling_class: str) -> str:
    """10-i4's `basis_key` for `proposal_class = privacy`: `(file_id, handling_class)`.

    P1 stores `basis_key` as one opaque TEXT column, so the pair is composed here as
    canonical JSON -- the same encoding P4 uses for its own comparable bytes, so two
    parts never disagree about how a tuple becomes a string.
    """
    return canonical_json([file_id, handling_class])


def suppressed(conn: sqlite3.Connection, file_id: str, handling_class: str) -> bool:
    """Has the user rejected this exact classification for this file, unreset?

    P1's reader already honours a later `reset_preferences` as a cutoff, so a reset
    restores emission without anything being deleted (R6).
    """
    key = basis_key_for(file_id, handling_class)
    for row in learning_records(conn, FILE_SCOPE, file_id):
        if row["proposal_class"] != PROPOSAL_CLASS:
            continue                                     # 10-i4 rule 1
        if row["basis_key"] != key:
            continue                                     # 10-i4 rule 2
        if row["polarity"] == REJECT:                    # 10-i4 rule 4
            return True
    return False


def assign(conn: sqlite3.Connection, record: ClassificationRecord, *,
           store: ClassificationStore,
           component_version: str) -> ClassificationRecord | None:
    """The system-side write, guarded by §8.7. Returns None when suppressed.

    None is the zero re-emission 10-i4's Done-means requires: "a fixture with one
    unresected reject at the stated `basis_key` produces zero re-emissions of that
    proposal". Nothing is written and no event is appended, so the log shows the
    proposal was not made rather than that it was made and hidden.

    This appends no `correction_*` field and no `user_id`, so a system assignment can
    never become the learning record that suppresses the next one.
    """
    check_handling_class(record.handling_class)
    if suppressed(conn, record.file_id, record.handling_class):
        return None
    store.write(record)
    _project(conn, record, component_version=component_version)
    append_event(conn, **event_defaults(
        event_type=CLASSIFICATION_ASSIGNED,
        file_id=record.file_id,
        content_hash=record.content_hash,
        component_version=component_version,
        observed_at=record.observed_at,
        explanation=canonical_json({
            "handling_class": record.handling_class,
            "protected": record.protected,
            "basis": record.basis,
            "reliability_state": record.reliability_state,
            "evidence_refs": list(record.evidence_refs),
        }),
    ))
    return record


def reclassify(conn: sqlite3.Connection, file_id: str, handling_class: str,
               reason: str, *, store: ClassificationStore, content_hash: str,
               protected: bool, evidence_refs: Sequence[str], user_id: str,
               component_version: str, observed_at: str,
               correction_scope: str = FILE_SCOPE) -> ClassificationRecord:
    """§8.4's "can be revised by the user", as a supersession and a negative example.

    `protected` is a parameter and is never derived from `handling_class`. Open question
    1 -- "Is `protected` exactly the top two handling classes?" -- is unsettled, and
    SPEC §2 says outright: "Neighbouring parts should consume the `protected` flag, not
    infer it from the class."

    `evidence_refs` carries P4 `observation_key` values (M14) -- the keys the detector
    fired on. They land on the new record and are echoed into the superseding event so
    §8.7's "stored with the evidence that produced them" has somewhere to be true.
    """
    check_handling_class(handling_class)
    if not reason or not reason.strip():
        raise ValueError(
            "§8.2 retains 'the old observation and the reason it was superseded'; a "
            "revision without a reason cannot satisfy it")
    if correction_scope not in CORRECTION_SCOPES:
        raise ValueError(
            f"correction_scope {correction_scope!r} is not one of §8.7's six "
            f"{tuple(sorted(CORRECTION_SCOPES))}")
    prior = store.current(file_id, content_hash)
    prior_fact_id = store.current_fact_id(file_id, content_hash)
    record = ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class=handling_class,
        protected=protected, basis="user", evidence_refs=tuple(evidence_refs),
        reliability_state="user_confirmed", observed_at=observed_at)
    fact_id = store.write(record)
    if prior is not None and prior_fact_id is not None:
        store.supersede(prior_fact_id, fact_id, reason)
    _project(conn, record, component_version=component_version)

    if prior is None:
        event_type, polarity, subject = CLASSIFICATION_ASSIGNED, ACCEPT, handling_class
    else:
        event_type, polarity, subject = (
            CLASSIFICATION_SUPERSEDED, REJECT, prior.handling_class)
    append_event(conn, **event_defaults(
        event_type=event_type,
        file_id=file_id,
        content_hash=content_hash,
        user_id=user_id,
        component_version=component_version,
        observed_at=observed_at,
        explanation=canonical_json({
            "handling_class": handling_class,
            "protected": protected,
            "reason": reason,
            "superseded_handling_class":
                None if prior is None else prior.handling_class,
            "rejected_evidence_refs": list(evidence_refs),
        }),
        correction_scope=correction_scope,
        correction_subject=file_id,
        polarity=polarity,
        proposal_class=PROPOSAL_CLASS,
        basis_key=basis_key_for(file_id, subject),
    ))
    return record


def _project(conn: sqlite3.Connection, record: ClassificationRecord, *,
             component_version: str) -> None:
    """D2's projection: P7 authors, P1 stores. `src/privacy/` writes no `UPDATE files`."""
    set_sensitivity_state(conn, record.file_id, state=mirror_state(record),
                          author=SUBSYSTEM, component_version=component_version)
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_learning_seam.py -v`
Expected: PASS — 21 passed

- [ ] **Step 5: Commit**

```bash
git add src/privacy/learning_seam.py tests/p7/test_p7_learning_seam.py
git commit -m "feat(P7): reclassification as supersession, and 8.7's query-before-classify"
```

---

---

### Task 17: `may_move_automatically`

**Files:**
- Create: `src/privacy/moves.py`
- Modify: `src/privacy/gate.py` (add `Gate.may_move_automatically`, delegating to this module — SPEC §9 publishes it on the facade, and **D13 kept CUT 4**, so the facade is certain rather than provisional)
- Test: `tests/p7/test_p7_moves.py`

**Interfaces:**
- Consumes: `privacy.classification.ClassificationRecord`,
  `privacy.classification.resolve_class(record: ClassificationRecord | None) -> str`,
  `privacy.classification_store.ClassificationStore` (`current(file_id, content_hash)
  -> ClassificationRecord | None`; the test also uses `current_fact_id`, `write` and
  `supersede`), `privacy.policy.Policy`, `privacy.policy.set_policy` (test only),
  `privacy.policy.current_policy(conn, *, plan_version) -> Policy`,
  `database_agent.files_table.get_file(conn, file_id) -> sqlite3.Row`.
- Produces (`moves.py`):
  - `NOT_PROTECTED: str = "not_protected"`
  - `POLICY_PERMITS: str = "policy_permits"`
  - `PROTECTED_WITHOUT_PERMITTING_POLICY: str = "protected_without_permitting_policy"`
  - `UNREADABLE_UNCLASSIFIED: str` — bound to `resolve_class(None)`, never typed a second time.
  - `MOVE_REASONS: tuple[str, ...]` — those four, in decision order.
  - `MoveVerdict` — frozen: `allowed: bool`, `reason: str`, `permitting_policy: str | None`.
  - `may_move_automatically(conn, file_id, plan_version) -> MoveVerdict`.

**Done-means:** 9, first clause. The coverage table holds the second: *"**Partly.** First clause
yes. The second is a property of P11 and P12, which do not exist; P7 makes it *possible* by naming
the permitting policy in the verdict."* A named test in this file carries that sentence so the
limitation lives in the suite rather than in a report nobody rereads.

**Three design sentences, none of them P7's, and each decides a branch.**

1. §8.4, verbatim: *"Protected material should not be included in cloud-model prompts by default,
   should not display raw content in general group summaries, and should not be moved automatically
   without a user policy that explicitly permits it."* — the third clause is this predicate.
2. §7.11, verbatim: the system *"must not delete files, mark them disposable, or move them out of a
   protected area without explicit user action."* This is why the refusal is the default branch and
   the permission is the exception, rather than the other way round.
3. §8.8, verbatim: *"A new plan should never silently reclassify or move old files."* The policy is
   read **at the asked-for plan version**, so a permission adopted later does not reach backwards
   and one adopted earlier does not leak forwards.

**The classification is not plan-scoped and the policy is.** §8.8: *"The evidence database remains
shared across plan versions, but the destination tree and user policy define which projections are
valid in each version."* So `ClassificationStore.current(...)` takes no plan version and
`current_policy(...)` requires one. That asymmetry is the whole of the §8.8 behaviour and it is
not a choice this task makes.

**`UNREADABLE_UNCLASSIFIED` is bound to `resolve_class(None)` rather than typed.** Task 3 owns the
rule that absence resolves to that class and refuses to resolve it to `public_low`. Spelling the
string a second time here would create a second place for the two to disagree, which is the defect
class this project has recorded most often. The module-level binding evaluates Task 3's function at
import, so a change there is a failing test here rather than a silent divergence.

**The order of the branches is load-bearing.** Absence is checked **before** the flag, because a
file nothing has classified has no `protected` flag to read and "no flag" must never be read as
"flag false". Then the flag, then the policy. A predicate that checked the flag first would answer
`not_protected` for every file in a corpus with no detector — the exact §8.6 failure, arrived at
from a different direction.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_moves.py
"""Done-means 9's first clause: §8.4's automatic-move predicate.

Three sentences decide every assertion here and none of them is P7's. §8.4: protected
material "should not be moved automatically without a user policy that explicitly
permits it." §7.11: the system "must not delete files, mark them disposable, or move
them out of a protected area without explicit user action." §8.8: "A new plan should
never silently reclassify or move old files."

The fourth fact is D2's, and it is why so much of this file is about absence: no
detector exists, so on a real corpus `store.current(...)` returns None for every file
and the verdict is `unreadable_unclassified` every time. That is the honest posture
rather than a gap, and one test says so by name.
"""
import dataclasses
import json

import pytest

from database_agent.files_table import get_file, record_file

from privacy.authorship import SUBSYSTEM
from privacy.classification import ClassificationRecord, resolve_class
from privacy.classification_store import ClassificationStore
from privacy.moves import (
    MOVE_REASONS, NOT_PROTECTED, POLICY_PERMITS,
    PROTECTED_WITHOUT_PERMITTING_POLICY, UNREADABLE_UNCLASSIFIED, MoveVerdict,
    may_move_automatically,
)
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
COMPONENT = "0.1.0"
PLAN_ONE = "plan-1"
PLAN_TWO = "plan-2"


@pytest.fixture()
def file_id(p7_conn, tmp_path):
    """A real P1 row: the classification is keyed on (file_id, content_hash) and a
    synthesized id would not exercise the hash lookup the predicate performs."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    document = corpus / "passport-scan.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    return record_file(
        p7_conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


@pytest.fixture()
def content_hash(p7_conn, file_id):
    return get_file(p7_conn, file_id)["content_hash"]


@pytest.fixture()
def store(p7_conn):
    return ClassificationStore(p7_conn)


def a_policy(**over) -> Policy:
    base = dict(policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
                consent_grants=(("Academics", "cloud_model"),),
                redaction_settings={"names": "redacted", "previews": "redacted",
                                    "thumbnails": "redacted", "ocr_text": "redacted",
                                    "location_data": "redacted"},
                automatic_move_permissions={}, plan_version=PLAN_ONE,
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


def stored(conn, **over) -> str:
    """Store a policy; return the version the gate minted for it.

    SPEC §6: "the gate owns the policy, so the caller does not supply this value, it
    echoes it." The tests below compare the verdict against the RETURNED version, not
    against the placeholder `a_policy` carries in, which is what makes
    `permitting_policy` a fact P11 and P12 can record rather than a value the caller
    already had.
    """
    return set_policy(conn, a_policy(**over), component_version=COMPONENT, user_id="joseph",
                      reason="the policy this test starts from")


def classify(store, file_id, content_hash, *, handling_class, protected):
    """Stand in for the detector that does not exist (D2).

    `basis = "user"` rather than `"detector"`, because Task 3 raises
    `UnbackedClassification` on a detector record with no `evidence_refs` and this
    test has no detector to have fired.

    A second call supersedes the first through Task 4's `current_fact_id` and
    `supersede`, which is Task 16's `reclassify` path rather than a second current
    record: §8.2 forbids overwriting, and two unsuperseded records would leave
    `current(...)` ambiguous and this file testing the wrong thing.
    """
    prior_fact_id = store.current_fact_id(file_id, content_hash)
    record = ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class=handling_class,
        protected=protected, basis="user", evidence_refs=(),
        reliability_state="user_confirmed", observed_at=FIXED_CLOCK)
    fact_id = store.write(record)
    if prior_fact_id is not None:
        store.supersede(prior_fact_id, fact_id, "the fixture revises its own record")
    return record


# --- the shape SPEC §9 published ---------------------------------------------

def test_the_verdict_carries_specs_three_fields_and_no_fourth(p7_conn):
    # SPEC §9: `Gate.may_move_automatically(file_id, plan_version) -> { allowed,
    # reason, permitting_policy? }`. Read off the dataclass, never off the class body.
    assert [f.name for f in dataclasses.fields(MoveVerdict)] == [
        "allowed", "reason", "permitting_policy"]


def test_the_four_reasons_are_the_only_ones_the_predicate_can_return(
        p7_conn, file_id, content_hash, store):
    assert len(MOVE_REASONS) == 4
    assert set(MOVE_REASONS) == {
        NOT_PROTECTED, POLICY_PERMITS, PROTECTED_WITHOUT_PERMITTING_POLICY,
        UNREADABLE_UNCLASSIFIED}
    seen = set()
    stored(p7_conn)
    seen.add(may_move_automatically(p7_conn, file_id, PLAN_ONE).reason)
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    seen.add(may_move_automatically(p7_conn, file_id, PLAN_ONE).reason)
    stored(p7_conn, plan_version=PLAN_TWO,
           automatic_move_permissions={file_id: True})
    seen.add(may_move_automatically(p7_conn, file_id, PLAN_TWO).reason)
    classify(store, file_id, content_hash, handling_class="public_low",
             protected=False)
    seen.add(may_move_automatically(p7_conn, file_id, PLAN_ONE).reason)
    assert seen == set(MOVE_REASONS)


# --- absence, which is every file until a detector exists ---------------------

def test_absence_of_a_classification_refuses_and_never_reads_as_public(
        p7_conn, file_id):
    # D2: "Unreadable or unclassified is a GATE OUTCOME, not a file fact." §8.6: cost
    # exhaustion "must never turn into lower-quality automatic classification" -- the
    # forbidden move is exactly resolving absence to a low class so work can continue.
    stored(p7_conn)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is False
    assert verdict.reason == UNREADABLE_UNCLASSIFIED
    assert verdict.reason == "unreadable_unclassified"
    assert verdict.reason != "public_low"
    assert verdict.permitting_policy is None


def test_the_unclassified_reason_is_task_3s_value_and_not_a_second_spelling():
    # One string, one owner. A second literal here is a second place for the two to
    # disagree, and Task 3 owns the rule that absence resolves to this class.
    assert UNREADABLE_UNCLASSIFIED == resolve_class(None)


def test_with_no_detector_every_file_gets_that_verdict(p7_conn, tmp_path):
    # The honest v1 posture, stated in the suite rather than in a report. No task in
    # any plan produces a detector rule set (D2), so this is what a real corpus looks
    # like on the day P7 ships: a correct, locked door with nobody holding a key.
    stored(p7_conn)
    corpus = tmp_path / "many"
    corpus.mkdir()
    for index in range(3):
        document = corpus / f"file-{index}.pdf"
        document.write_bytes(f"%PDF-1.4 body {index}".encode())
        new_id = record_file(
            p7_conn, document, filename=document.name,
            normalized_filename=document.name.lower(), extension=".pdf",
            observed_size=document.stat().st_size,
            observed_timestamps=json.dumps({"mtime": 1.0}),
            parent_folder_context=str(corpus), mime_type="application/pdf",
            detected_format="pdf", scan_state="fixture-scan-state",
            materialized=True)
        verdict = may_move_automatically(p7_conn, new_id, PLAN_ONE)
        assert verdict == MoveVerdict(allowed=False,
                                      reason=UNREADABLE_UNCLASSIFIED,
                                      permitting_policy=None)


# --- protected material, with and without a permitting policy -----------------

def test_protected_material_without_a_permitting_policy_cannot_move(
        p7_conn, file_id, content_hash, store):
    # §8.4: protected material "should not be moved automatically without a user
    # policy that explicitly permits it." §7.11: the system must not "move them out of
    # a protected area without explicit user action."
    stored(p7_conn)
    classify(store, file_id, content_hash,
             handling_class="highly_sensitive_credential_bearing", protected=True)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is False
    assert verdict.reason == PROTECTED_WITHOUT_PERMITTING_POLICY


def test_a_policy_that_explicitly_permits_this_file_allows_the_move(
        p7_conn, file_id, content_hash, store):
    stored(p7_conn, automatic_move_permissions={file_id: True})
    classify(store, file_id, content_hash,
             handling_class="highly_sensitive_credential_bearing", protected=True)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is True
    assert verdict.reason == POLICY_PERMITS


def test_the_permitting_policy_is_named_in_the_verdict(
        p7_conn, file_id, content_hash, store):
    # Done-means 9's second clause depends on this field existing: P11 records the
    # answer in the placement decision (§6.11 "required review policy") and P12 in the
    # plan precondition (§8.3 "Sensitivity and consent state"), and neither re-derives
    # it. The version asserted is the one the GATE minted, not the placeholder in.
    version = stored(p7_conn, automatic_move_permissions={file_id: True})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(
        p7_conn, file_id, PLAN_ONE).permitting_policy == version


def test_a_refusal_names_no_permitting_policy(
        p7_conn, file_id, content_hash, store):
    # There is no policy to name, and naming one would let a caller record a
    # permission that never existed.
    stored(p7_conn)
    assert may_move_automatically(
        p7_conn, file_id, PLAN_ONE).permitting_policy is None
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(
        p7_conn, file_id, PLAN_ONE).permitting_policy is None


def test_a_withdrawn_permission_does_not_permit(
        p7_conn, file_id, content_hash, store):
    # §8.7's recorded action is "granting or withdrawing an automatic-move permission
    # for protected material". A withdrawal is a stored `False`, not an absent key,
    # and both refuse -- but only the stored `False` proves the branch reads the value
    # rather than the presence of the key.
    stored(p7_conn, automatic_move_permissions={file_id: False})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is False
    assert verdict.reason == PROTECTED_WITHOUT_PERMITTING_POLICY


def test_a_grant_at_a_scope_p7_cannot_resolve_does_not_permit(
        p7_conn, file_id, content_hash, store):
    # Open question 3: "What is a 'corpus area'? ... Consent grants cannot be scoped
    # until this is named." P7 defines no area, so the only key it can resolve to a
    # file is the file's own id. A grant at "Academics" is not read as covering this
    # file, and the alternative -- guessing that it does -- would widen egress policy
    # on an unanswered question.
    stored(p7_conn, automatic_move_permissions={"Academics": True, "/Users/jy": True})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is False


# --- the flag, not the class (SPEC §2, Open question 1) -----------------------

def test_a_file_that_is_not_protected_may_move(
        p7_conn, file_id, content_hash, store):
    stored(p7_conn)
    classify(store, file_id, content_hash, handling_class="public_low",
             protected=False)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is True
    assert verdict.reason == NOT_PROTECTED
    assert verdict.permitting_policy is None


def test_the_verdict_keys_on_the_flag_and_not_the_handling_class(
        p7_conn, file_id, content_hash, store):
    # SPEC §2: "Neighbouring parts should consume the `protected` flag, not infer it
    # from the class." Open question 1 -- whether `protected` is exactly the top two
    # classes -- is unsettled, so both records below are legal and the flag wins in
    # both directions.
    stored(p7_conn)
    classify(store, file_id, content_hash, handling_class="public_low",
             protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is False
    classify(store, file_id, content_hash,
             handling_class="highly_sensitive_credential_bearing", protected=False)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is True


# --- §8.8: the plan version is not decoration ---------------------------------

def test_a_later_plan_version_does_not_retroactively_permit(
        p7_conn, file_id, content_hash, store):
    # §8.8: "A new plan should never silently reclassify or move old files." The
    # permission is adopted at plan-2; asking under plan-1 must not see it.
    stored(p7_conn, plan_version=PLAN_ONE, automatic_move_permissions={})
    stored(p7_conn, plan_version=PLAN_TWO,
           automatic_move_permissions={file_id: True})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is False
    assert may_move_automatically(p7_conn, file_id, PLAN_TWO).allowed is True


def test_a_permission_does_not_leak_forward_into_a_later_plan_either(
        p7_conn, file_id, content_hash, store):
    # The symmetric half. §8.8 makes the user policy one of the two things that
    # "define which projections are valid in each version", so a permission granted
    # under plan-1 is not in force under plan-2 unless plan-2 carries it too.
    stored(p7_conn, plan_version=PLAN_ONE,
           automatic_move_permissions={file_id: True})
    stored(p7_conn, plan_version=PLAN_TWO, automatic_move_permissions={})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is True
    assert may_move_automatically(p7_conn, file_id, PLAN_TWO).allowed is False


def test_the_classification_is_shared_across_plan_versions(
        p7_conn, file_id, content_hash, store):
    # §8.8: "The evidence database remains shared across plan versions." The
    # classification is looked up with no plan version at all; only the policy is
    # plan-scoped, and that asymmetry is §8.8's and not this task's.
    stored(p7_conn, plan_version=PLAN_ONE, automatic_move_permissions={})
    stored(p7_conn, plan_version=PLAN_TWO, automatic_move_permissions={})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    for plan_version in (PLAN_ONE, PLAN_TWO):
        assert may_move_automatically(
            p7_conn, file_id, plan_version).reason == (
                PROTECTED_WITHOUT_PERMITTING_POLICY)


# --- C4: a predicate writes nothing -------------------------------------------

def test_the_predicate_writes_nothing(p7_conn, file_id, content_hash, store):
    # C4: "a gate that also wrote would be doing two jobs." This one does not even
    # release; it answers a question P11 and P12 ask before they plan a move.
    stored(p7_conn)
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    mirror = get_file(p7_conn, file_id)["sensitivity_state"]
    for plan_version in (PLAN_ONE, PLAN_TWO, PLAN_ONE):
        may_move_automatically(p7_conn, file_id, plan_version)
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before
    assert get_file(p7_conn, file_id)["sensitivity_state"] == mirror


# --- the half of Done-means 9 that cannot be proved here ----------------------

def test_p11_and_p12_consuming_the_answer_is_not_provable_inside_p7(p7_conn):
    """Done-means 9's second clause is a property of two parts that do not exist.

    The coverage table states it: "**Partly.** First clause yes. The second is a
    property of P11 and P12, which do not exist; P7 makes it *possible* by naming the
    permitting policy in the verdict." §6.11's "required review policy" and §8.3's
    "Sensitivity and consent state" are where the answer lands, and neither field has
    a schema in this repository yet.

    What P7 can assert is that the verdict is complete enough to be recorded without
    re-derivation: three fields, and the permitting policy named whenever one
    permitted. That is asserted above. The rest is P11's and P12's, and this test
    exists so the limitation is in the suite rather than in a report nobody rereads.
    """
    assert [f.name for f in dataclasses.fields(MoveVerdict)] == [
        "allowed", "reason", "permitting_policy"]
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_moves.py -v`
Expected: FAIL — `ImportError: cannot import name 'MOVE_REASONS' from 'privacy.moves'` (the module
does not exist yet, so collection fails on the first import).

- [ ] **Step 3: Write `src/privacy/moves.py`**

```python
# src/privacy/moves.py
"""§8.4's automatic-move predicate — one of the two surfaces P7 publishes off the model path.

§8.4's sentence is the whole specification: protected material "should not be included
in cloud-model prompts by default, should not display raw content in general group
summaries, and should not be moved automatically without a user policy that explicitly
permits it." The third clause is this module. §7.11 states the same rule from the
residual side -- the system "must not delete files, mark them disposable, or move them
out of a protected area without explicit user action" -- which is why refusal is the
default branch and permission is the exception.

Three properties are deliberate and each has a test:

- **Absence is checked first.** A file nothing has classified has no `protected` flag,
  and "no flag" must never be read as "flag false". The verdict is
  `unreadable_unclassified`, which is Task 3's value and not a second spelling of it.
  With no detector built (D2) this is the verdict for every file in a real corpus.
- **The flag decides, never the class.** SPEC §2: "Neighbouring parts should consume
  the `protected` flag, not infer it from the class", and Open question 1 -- whether
  `protected` is exactly the top two classes -- is unsettled.
- **The policy is read at the asked-for plan version and the classification is not.**
  §8.8: "The evidence database remains shared across plan versions, but the destination
  tree and user policy define which projections are valid in each version", and "A new
  plan should never silently reclassify or move old files."

This module writes nothing (C4). It appends no event, mints no policy version and
issues no `UPDATE files`.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from database_agent.files_table import get_file

from privacy.classification import resolve_class
from privacy.classification_store import ClassificationStore
from privacy.policy import current_policy

#: The file carries no `protected` flag, so §8.4's restriction does not attach.
NOT_PROTECTED: str = "not_protected"

#: Protected, and a user policy at this plan version explicitly permits this file.
POLICY_PERMITS: str = "policy_permits"

#: Protected, and no policy at this plan version permits it. §8.4's default answer.
PROTECTED_WITHOUT_PERMITTING_POLICY: str = "protected_without_permitting_policy"

#: Nothing has classified this file. Bound to Task 3's resolver rather than typed a
#: second time: Task 3 owns the rule that absence resolves here and never to
#: `public_low`, and two literals would be two places for one rule to drift.
UNREADABLE_UNCLASSIFIED: str = resolve_class(None)

#: The four, in the order the predicate decides them.
MOVE_REASONS: tuple[str, ...] = (
    UNREADABLE_UNCLASSIFIED,
    NOT_PROTECTED,
    POLICY_PERMITS,
    PROTECTED_WITHOUT_PERMITTING_POLICY,
)


@dataclass(frozen=True)
class MoveVerdict:
    """SPEC §9's return: `{ allowed, reason, permitting_policy? }`.

    `permitting_policy` is populated only when a policy permitted the move, and it
    carries the `policy_version` the gate minted. P11 records it in the placement
    decision (§6.11 "required review policy") and P12 in the plan precondition (§8.3
    "Sensitivity and consent state"); neither re-derives the answer, and neither can
    record a permission that did not exist, because a refusal names none.
    """

    allowed: bool
    reason: str
    permitting_policy: str | None


def may_move_automatically(conn: sqlite3.Connection, file_id: str,
                           plan_version: str) -> MoveVerdict:
    """May P11/P12 move this file without asking the user, under this plan version?

    Reads only. The branch order is absence, then the flag, then the policy, and it
    is not interchangeable: checking the flag first would answer `not_protected` for
    every file in a corpus nothing has classified, which is §8.6's forbidden move --
    "Cost exhaustion must never turn into lower-quality automatic classification" --
    reached from a different direction.
    """
    content_hash = get_file(conn, file_id)["content_hash"]
    record = ClassificationStore(conn).current(file_id, content_hash)
    if record is None:
        return MoveVerdict(allowed=False, reason=UNREADABLE_UNCLASSIFIED,
                           permitting_policy=None)
    if not record.protected:
        return MoveVerdict(allowed=True, reason=NOT_PROTECTED,
                           permitting_policy=None)
    policy = current_policy(conn, plan_version=plan_version)
    if policy.automatic_move_permissions.get(file_id) is True:
        return MoveVerdict(allowed=True, reason=POLICY_PERMITS,
                           permitting_policy=policy.policy_version)
    return MoveVerdict(allowed=False, reason=PROTECTED_WITHOUT_PERMITTING_POLICY,
                       permitting_policy=None)
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_moves.py -v`
Expected: PASS — 18 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–17 green, and the 1302 P1–P5 tests still green (P7 modified no file
belonging to another part).

- [ ] **Step 6: Commit**

```bash
git add src/privacy/moves.py tests/p7/test_p7_moves.py
git commit -m "feat(P7): may_move_automatically, keyed on the protected flag and the asked-for plan version"
```

---

---

### Task 18: `display_policy` and `summarize_protected`

**Files:**
- Create: `src/privacy/display.py`
- Modify: `src/privacy/gate.py` (add `Gate.display_policy` and `Gate.summarize_protected`, delegating to this module — SPEC §10 publishes it on the facade, and **D13 kept CUT 4**, so the facade is certain rather than provisional)
- Test: `tests/p7/test_p7_display.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.DISPLAY_FACETS`, `.HANDLING_CLASSES`,
  `privacy.defaults.MORE_REDACTING`, `privacy.policy.current_policy(conn, *, plan_version) -> Policy`,
  `privacy.classification.resolve_class(record) -> str`,
  `privacy.classification_store.ClassificationStore` (the skeleton's `facts_seam.SensitivityFacts` —
  see the rename note), `database_agent.files_table.get_file`.
- Produces (`display.py`):
  - `SHOWN: str = "shown"`, `REDACTED: str = "redacted"`, `SETTING_VALUES: tuple[str, str]`.
  - `RedactionSettings` — frozen, five fields, one per §8.4 facet, in §8.4's order;
    `facet(name) -> str`.
  - `ProtectedSummary` — frozen: `count: int`, `class_breakdown: Mapping[str, int]`. Two fields,
    and deliberately no third.
  - `UnknownDisplaySetting`.
  - `display_policy(conn, *, plan_version) -> RedactionSettings`.
  - `summarize_protected(conn, scope, *, store, files_in_scope) -> ProtectedSummary`.

**Done-means:** 10, and the display half of 12.

**Two signature widenings, both reported.** The skeleton publishes `display_policy(conn)` and
`summarize_protected(conn, scope)`. `current_policy(conn, *, plan_version)` is plan-scoped — §8.8
lists *"Privacy and model-consent policies"* inside the plan version — so `display_policy` needs the
plan version and takes it as a keyword. `summarize_protected` needs the classification store and a
scope resolver for the same Open-question-3 reason `revoke` does. SPEC §10's published surface is
`Gate.display_policy()` and `Gate.summarize_protected(scope)`, and the facade holds both values, so
the SPEC's shape is unchanged where a caller sees it.

**`shown | redacted` is SPEC §10's own text**, not a vocabulary this task invented:
`names | previews | thumbnails | ocr_text | location_data     each shown | redacted`. Task 2 owns
`DISPLAY_FACETS`; the two values live here because no earlier task's `Produces` block claims them.

**The default is the more redacting value, per facet, and that is Task 6's rule applied.** §8.4's
`must` — *"The default posture must therefore be local-first and data-minimizing"* — with §8.4's own
worked example settling the direction: *"A summary such as '11 protected identity records' may be
safe to show, while a visible list of passport filenames on a shared screen may not be."* The
aggregate is the default and the expansion is the user's act. A facet absent from the stored policy
resolves through `defaults.MORE_REDACTING`, never to `shown`.

**`ProtectedSummary` cannot return a filename, and the proof is at the type level.** Done-means 10:
*"returns counts and class breakdown and cannot return filenames or content."* Asserted over
`dataclasses.fields(ProtectedSummary)` — a runtime filter is something a future caller can route
around, and a string scan matches the docstring that explains the rule. §5.2 applies the same rule
to the canvas: a Finance or Identity proposal *"may be visible as a protected area, but the product
should avoid showing sensitive filenames"*, and §7.5's residual screen already uses the form —
*"11 protected personal records."*

**`count` counts protected files; `class_breakdown` counts every file in scope by its resolved
class.** Both are needed and they answer different questions. `count` is §8.4's aggregate. The
breakdown includes `unreadable_unclassified`, which is what makes today's honest state visible: with
no detector (D2) every file resolves there, so a real corpus yields `count = 0` — and *"0 protected
records"* means *nothing has looked*, not *nothing is protected*. That is exactly why D2 keeps
`unreadable_unclassified` off `files.sensitivity_state` and on the gate outcome, and a named test
records it here rather than leaving a reader to find it.

**P13's open question is recorded against this signature and not resolved.** §8.4: *"Protected
branches should have configurable redaction in the canvas and review screens"* — which reads
per-branch — while `display_policy()` takes no branch. Quoted in a named test, unresolved.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_display.py
"""Done-means 10, and the display half of Done-means 12.

§8.4's UI paragraph, entire: "Privacy also applies to the user interface. A summary
such as '11 protected identity records' may be safe to show, while a visible list of
passport filenames on a shared screen may not be. Protected branches should have
configurable redaction in the canvas and review screens. The user can choose whether
names, previews, thumbnails, OCR text, or location data are shown."
"""
import dataclasses
import json

import pytest

from database_agent.files_table import get_file, record_file

from privacy.authorship import SUBSYSTEM
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.display import (
    REDACTED, SETTING_VALUES, SHOWN, ProtectedSummary, RedactionSettings,
    UnknownDisplaySetting, display_policy, summarize_protected,
)
from privacy.policy import Policy, set_policy
from privacy.vocabulary import DISPLAY_FACETS, HANDLING_CLASSES

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
COMPONENT = "0.1.0"
IDENTITY = "Identity"

ALL_SHOWN = {facet: SHOWN for facet in DISPLAY_FACETS}


@pytest.fixture()
def store(p7_conn):
    return ClassificationStore(p7_conn)


@pytest.fixture()
def corpus(p7_conn, tmp_path):
    """Eleven passport scans and two ordinary files, so §8.4's own example number is
    the number the summary produces."""
    root = tmp_path / "corpus"
    root.mkdir()
    file_ids = []
    for index in range(11):
        document = root / f"passport-scan-{index}.pdf"
        document.write_bytes(f"%PDF-1.4 passport {index}".encode())
        file_ids.append(_record(p7_conn, root, document))
    for name in ("syllabus.pdf", "notes.md"):
        document = root / name
        document.write_bytes(f"plain {name}".encode())
        file_ids.append(_record(p7_conn, root, document))
    return file_ids


def _record(conn, root, document):
    return record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=document.suffix,
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(root), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


def classify(conn, store, file_id, *, handling_class, protected):
    store.write(ClassificationRecord(
        file_id=file_id, content_hash=get_file(conn, file_id)["content_hash"],
        handling_class=handling_class, protected=protected, basis="user",
        evidence_refs=(), reliability_state="user_confirmed",
        observed_at=FIXED_CLOCK))


def install(conn, *, plan_version="plan-1", redaction_settings=None) -> str:
    policy = Policy(policy_version=UNSET_POLICY_VERSION, operation_mode="local_model",
                    consent_grants=(),
                    redaction_settings=dict(redaction_settings or {}),
                    automatic_move_permissions={}, plan_version=plan_version,
                    set_at=FIXED_CLOCK)
    return set_policy(conn, policy, component_version=COMPONENT,
                      user_id="joseph",
                      reason="the fixture's starting policy")


def summarize(conn, store, file_ids):
    return summarize_protected(conn, IDENTITY, store=store,
                               files_in_scope=lambda scope: tuple(file_ids))


# --- the five facets --------------------------------------------------------

def test_the_five_facets_are_8_4s_own_list_in_8_4s_order():
    # "whether names, previews, thumbnails, OCR text, or location data are shown."
    assert [field.name for field in dataclasses.fields(RedactionSettings)] == [
        "names", "previews", "thumbnails", "ocr_text", "location_data"]
    assert tuple(DISPLAY_FACETS) == tuple(
        field.name for field in dataclasses.fields(RedactionSettings))


def test_there_is_no_sixth_facet():
    assert len(dataclasses.fields(RedactionSettings)) == 5


def test_each_facet_takes_one_of_two_values(p7_conn):
    # SPEC §10: "each shown | redacted".
    assert SETTING_VALUES == (SHOWN, REDACTED) == ("shown", "redacted")
    install(p7_conn, redaction_settings=ALL_SHOWN)
    settings = display_policy(p7_conn, plan_version="plan-1")
    for facet in DISPLAY_FACETS:
        assert settings.facet(facet) in SETTING_VALUES


def test_a_third_value_is_a_load_error(p7_conn):
    # "A value outside this set is a load error, not a fallback" (SPEC §1's rule,
    # applied to the setting values §10 states).
    install(p7_conn, redaction_settings={**ALL_SHOWN, "names": "blurred"})
    with pytest.raises(UnknownDisplaySetting):
        display_policy(p7_conn, plan_version="plan-1")


def test_an_unknown_facet_is_a_load_error(p7_conn):
    install(p7_conn, redaction_settings={**ALL_SHOWN, "audio": REDACTED})
    with pytest.raises(UnknownDisplaySetting):
        display_policy(p7_conn, plan_version="plan-1")


# --- the default is the more redacting one ----------------------------------

def test_an_empty_policy_resolves_every_facet_to_its_more_redacting_value(p7_conn):
    # Done-means 12's display half: "every redaction setting the design leaves
    # configurable resolves to its more redacting value".
    install(p7_conn)
    settings = display_policy(p7_conn, plan_version="plan-1")
    for facet in DISPLAY_FACETS:
        assert settings.facet(facet) == MORE_REDACTING[facet] == REDACTED


def test_a_partial_policy_fills_the_missing_facets_from_the_more_redacting_rule(
        p7_conn):
    install(p7_conn, redaction_settings={"names": SHOWN})
    settings = display_policy(p7_conn, plan_version="plan-1")
    assert settings.names == SHOWN
    for facet in ("previews", "thumbnails", "ocr_text", "location_data"):
        assert settings.facet(facet) == REDACTED


def test_the_user_can_still_choose_shown(p7_conn):
    # §8.4: "The user can choose whether names, previews, thumbnails, OCR text, or
    # location data are shown." The floor is on the DEFAULT, never on the choice.
    install(p7_conn, redaction_settings=ALL_SHOWN)
    settings = display_policy(p7_conn, plan_version="plan-1")
    assert all(settings.facet(facet) == SHOWN for facet in DISPLAY_FACETS)


def test_settings_are_plan_scoped(p7_conn):
    # §8.8 lists "Privacy and model-consent policies" inside the plan version.
    install(p7_conn, plan_version="plan-1")
    install(p7_conn, plan_version="plan-2", redaction_settings=ALL_SHOWN)
    assert display_policy(p7_conn, plan_version="plan-1").names == REDACTED
    assert display_policy(p7_conn, plan_version="plan-2").names == SHOWN


# --- the aggregate-safe summary ---------------------------------------------

def test_protected_summary_has_two_fields_and_deliberately_no_third():
    # Done-means 10: "cannot return filenames or content". Proven at the TYPE level --
    # a runtime filter is something a future caller can route around, and a string
    # scan matches the docstring that explains the rule.
    names = [field.name for field in dataclasses.fields(ProtectedSummary)]
    assert names == ["count", "class_breakdown"]
    for forbidden in ("filename", "filenames", "path", "paths", "examples",
                      "members", "file_ids", "raw_value", "text", "preview",
                      "thumbnail"):
        assert forbidden not in names


def test_eleven_protected_identity_records(p7_conn, store, corpus):
    # §8.4's own example, as the acceptance criterion: "A summary such as '11
    # protected identity records' may be safe to show."
    for file_id in corpus[:11]:
        classify(p7_conn, store, file_id,
                 handling_class="highly_sensitive_credential_bearing",
                 protected=True)
    for file_id in corpus[11:]:
        classify(p7_conn, store, file_id, handling_class="public_low",
                 protected=False)
    summary = summarize(p7_conn, store, corpus)
    assert summary.count == 11
    assert summary.class_breakdown["highly_sensitive_credential_bearing"] == 11
    assert summary.class_breakdown["public_low"] == 2


def test_the_breakdown_covers_every_handling_class_zero_filled(
        p7_conn, store, corpus):
    for file_id in corpus:
        classify(p7_conn, store, file_id, handling_class="public_low",
                 protected=False)
    summary = summarize(p7_conn, store, corpus)
    assert set(summary.class_breakdown) == set(HANDLING_CLASSES)
    assert summary.class_breakdown["sensitive_personal"] == 0


def test_the_count_follows_the_flag_and_not_the_class(p7_conn, store, corpus):
    # SPEC §2, and Open question 1 again: a `public_low` file the user marked
    # protected is counted, and a top-class file that is not marked is not.
    classify(p7_conn, store, corpus[0], handling_class="public_low", protected=True)
    classify(p7_conn, store, corpus[1],
             handling_class="highly_sensitive_credential_bearing", protected=False)
    summary = summarize(p7_conn, store, corpus[:2])
    assert summary.count == 1
    assert summary.class_breakdown["public_low"] == 1
    assert summary.class_breakdown["highly_sensitive_credential_bearing"] == 1


def test_a_file_outside_the_scope_is_not_counted(p7_conn, store, corpus):
    classify(p7_conn, store, corpus[0],
             handling_class="highly_sensitive_credential_bearing", protected=True)
    assert summarize(p7_conn, store, ()).count == 0
    assert summarize(p7_conn, store, corpus[:1]).count == 1


def test_with_no_detector_the_summary_reads_zero_and_the_breakdown_says_why(
        p7_conn, store, corpus):
    # D2 leaves the detector unwritten, so this is the summary a real corpus produces
    # today. "0 protected records" means NOTHING HAS LOOKED, not "nothing is
    # protected" -- which is precisely why D2 keeps `unreadable_unclassified` off
    # `files.sensitivity_state` and on the gate outcome instead.
    summary = summarize(p7_conn, store, corpus)
    assert summary.count == 0
    assert summary.class_breakdown["unreadable_unclassified"] == len(corpus)
    assert sum(summary.class_breakdown.values()) == len(corpus)


def test_the_breakdown_is_not_mutable_by_a_caller(p7_conn, store, corpus):
    summary = summarize(p7_conn, store, corpus)
    with pytest.raises(TypeError):
        summary.class_breakdown["public_low"] = 99


# --- what is not resolved here ----------------------------------------------

def test_p13s_per_branch_question_is_recorded_and_not_answered(p7_conn):
    # §8.4: "Protected branches should have configurable redaction in the canvas and
    # review screens" -- which reads per-branch -- while SPEC §10 publishes
    # `Gate.display_policy()` with no branch. Recorded against the signature so the
    # reviewer sees where the gap is, and not resolved by this plan.
    import inspect
    parameters = set(inspect.signature(display_policy).parameters)
    assert parameters == {"conn", "plan_version"}
    assert "branch" not in parameters and "node_id" not in parameters


def test_files_in_scope_has_no_default(p7_conn):
    # Open question 3 once more: P7 defines no corpus area.
    import inspect
    parameter = inspect.signature(summarize_protected).parameters["files_in_scope"]
    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_display.py -v`
Expected: FAIL — `ImportError: cannot import name 'REDACTED' from 'privacy.display'`

- [ ] **Step 3: Write `src/privacy/display.py`**

```python
# src/privacy/display.py
"""§8.4's UI privacy: the five configurable facets, and the aggregate-safe summary.

§8.4's paragraph gives both surfaces and both defaults. The facets are its own list --
"whether names, previews, thumbnails, OCR text, or location data are shown" -- and the
default direction is its own example: "A summary such as '11 protected identity
records' may be safe to show, while a visible list of passport filenames on a shared
screen may not be." The aggregate is the default; the expansion is the user's act.

`ProtectedSummary` has two fields because Done-means 10 says it "cannot return
filenames or content", and the cheapest way to make that true is for there to be
nowhere to put one.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, fields
from types import MappingProxyType

from database_agent.files_table import get_file

from privacy.classification import resolve_class
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.policy import current_policy
from privacy.vocabulary import DISPLAY_FACETS, HANDLING_CLASSES

#: SPEC §10: "each shown | redacted". Two values, and no third.
SHOWN: str = "shown"
REDACTED: str = "redacted"
SETTING_VALUES: tuple[str, str] = (SHOWN, REDACTED)


class UnknownDisplaySetting(ValueError):
    """A facet or a value outside §8.4's list. A load error, never a fallback."""


@dataclass(frozen=True)
class RedactionSettings:
    """§8.4's five configurable facets, in §8.4's order."""

    names: str
    previews: str
    thumbnails: str
    ocr_text: str
    location_data: str

    def facet(self, name: str) -> str:
        if name not in DISPLAY_FACETS:
            raise UnknownDisplaySetting(
                f"{name!r} is not one of §8.4's five display facets {DISPLAY_FACETS}")
        return getattr(self, name)


@dataclass(frozen=True)
class ProtectedSummary:
    """§8.4's aggregate: "11 protected identity records", and nothing that names a file.

    Two fields, and deliberately no third. There is no `examples`, no `file_ids` and no
    `filenames`, because Done-means 10 forbids returning one and a field that does not
    exist cannot be populated by a later caller in a hurry.
    """

    count: int
    class_breakdown: Mapping[str, int]


def display_policy(conn: sqlite3.Connection, *,
                   plan_version: str) -> RedactionSettings:
    """The five facets as they resolve under the policy in force for `plan_version`.

    A facet the stored policy does not mention resolves through `MORE_REDACTING`, never
    to `shown`: §8.4's `must` is that the default posture be "local-first and
    data-minimizing", and §8.4's own example settles which direction that points.

    `plan_version` is a keyword because §8.8 places "Privacy and model-consent policies"
    inside the plan version. SPEC §10's published surface is `Gate.display_policy()`;
    the facade holds the plan version and supplies it here.
    """
    stored = current_policy(conn, plan_version=plan_version).redaction_settings
    unknown = [facet for facet in stored if facet not in DISPLAY_FACETS]
    if unknown:
        raise UnknownDisplaySetting(
            f"{sorted(unknown)} are not among §8.4's five display facets "
            f"{DISPLAY_FACETS}")
    resolved = {}
    for facet in DISPLAY_FACETS:
        value = stored.get(facet, MORE_REDACTING[facet])
        if value not in SETTING_VALUES:
            raise UnknownDisplaySetting(
                f"{facet} = {value!r} is not one of {SETTING_VALUES}; a value outside "
                "the set is a load error, not a fallback")
        resolved[facet] = value
    return RedactionSettings(**resolved)


def summarize_protected(conn: sqlite3.Connection, scope: str, *,
                        store: ClassificationStore,
                        files_in_scope: Callable[[str], Sequence[str]]
                        ) -> ProtectedSummary:
    """Counts only. §5.2: "avoid showing sensitive filenames"; §7.5: "11 protected
    personal records".

    `count` follows the `protected` flag, never the handling class (SPEC §2, Open
    question 1). `class_breakdown` covers every file in scope by its RESOLVED class,
    so a corpus nothing has classified reports `unreadable_unclassified` rather than
    disappearing -- which is today's ordinary state, since D2 leaves the detector
    unwritten.

    `files_in_scope` has no default: Open question 3 leaves "corpus area" unnamed.
    """
    counts = {handling_class: 0 for handling_class in HANDLING_CLASSES}
    protected = 0
    for file_id in files_in_scope(scope):
        record = store.current(file_id, get_file(conn, file_id)["content_hash"])
        counts[resolve_class(record)] += 1
        if record is not None and record.protected:
            protected += 1
    return ProtectedSummary(count=protected,
                            class_breakdown=MappingProxyType(counts))
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_display.py -v`
Expected: PASS — 17 passed

- [ ] **Step 5: Commit**

```bash
git add src/privacy/display.py tests/p7/test_p7_display.py
git commit -m "feat(P7): display_policy and summarize_protected, aggregate-safe at the type level"
```

---

---

### Task 19: The transport guard — Done-means 3's instrument

**Files:**
- Create: `src/privacy/transport_guard.py`, `tests/p7/transport_fixtures.py`
- Test: `tests/p7/test_p7_transport.py`

**Interfaces:**
- Consumes: `inspect`, `typing.get_args`, `privacy.release.Released`,
  `evidence_shape.observation.Observation`, `evidence_shape.text_units.TextUnit` (the **classes**,
  as members of `CONTENT_PARAMETER_TYPES` — neither is one of P4's four text materialisers, so
  layer L2's *"exactly one module under `src/privacy/` binds a P4 text materialiser"* is untouched
  and Task 21's repo-wide guard still passes).
- Produces (`transport_guard.py`):
  - `CONTENT_PARAMETER_TYPES: frozenset[type]` = `{str, bytes, Path, Observation, TextUnit}`.
  - `EgressGuardFailure`, `MultipleEgressPoints`, `NoEgressPoint`, `UnreleasedContentParameter`.
  - `egress_functions(module) -> list[Callable]`.
  - `assert_single_egress(module) -> None`.

**Done-means:** 3 — the instrument only. The coverage table states the limit and this plan repeats
it rather than softening it: *"**No — and this is a finding.** The transport is P8's. P7 proves the
instrument, the unforgeable token, and the single materialisation locus. The property itself is P8
Done-means 1."*

**What this is, precisely.** §8.4's opening sentence — *"Privacy policy must be enforced **before**
content reaches any model or external connector"* — is a **property**, and P8's Done-means 1 states
the method for checking it: *"Exactly one function in the codebase constructs a model request, and
its only parameter type is P7's `Released`. A call without a release is not constructible. Verified
by inspection plus a test that the un-released path does not type-check / does not exist."*
`assert_single_egress` is that inspection, mechanised. It is an **existence proof over a module
namespace** — it answers *does a string-prompt entry point exist in this module?* — and it is not a
runtime check on a call. Nothing here executes a transport.

**Three implementation rules, each of which is the difference between a guard and a decoration.**

1. **It reads resolved annotations, never source text.** `inspect.signature(fn, eval_str=True)` and
   `typing.get_args`. A source scan sees the word `Released` in a docstring and passes a transport
   that takes a string; a fixture whose docstring says exactly that is in the suite. This project
   has recorded that failure more than once, which is why `code_tokens()` exists in
   `tests/p3/test_p3_no_invention.py` — and why this task does not need it, because it never looks
   at text at all.
2. **It walks into containers and unions.** `list[str]`, `Sequence[str]`, `str | None`,
   `Path | None` are the shapes a transport that "takes no string" actually takes one in.
   `_leaves` recurses through `get_args` and checks every leaf.
3. **It checks every function in the module, public or private, and the entry-point count only over
   the public ones.** *"the un-released path does not exist"* is a statement about the module, not
   about its exports: a private `_format(text: str)` beside the entry point is a string-prompt path
   that happens to be unexported, and inside a module whose entire job is egress there is nothing
   for it to legitimately be. Classes are walked too — an SDK-client wrapper, `Client.send(self,
   prompt: str)`, is the single most likely real shape and a module-level-functions-only guard would
   miss it entirely. The receiver parameter (`self` / `cls`) is skipped; everything else is checked.

**An unresolvable annotation is a failure, not a crash.** If `eval_str=True` raises, the parameter
cannot be **shown** to be a `Released`, and a guard that propagates a bare `NameError` gives an
ambiguous signal at exactly the moment it matters. It is re-raised as
`UnreleasedContentParameter` with the original attached.

**A `str` return annotation is legal and must stay legal.** The model's reply comes back as text;
that is the direction the gate does not govern. Only **parameters** are checked, and a test pins it
so a later tightening does not make the real transport unrepresentable.

**The honest limit, said here and again in a named test.** Running this over the **real** transport
is P8's Done-means 1 and cannot happen in this repository today: there is no `src/llm/` and no
transport module to point it at. What Task 19 delivers is a checker proven correct against four
conforming fixtures and against seventeen non-conforming ones — the skeleton's rule that *"A checker
only proven on the passing case is an assertion that has never been tested."* Round 5 recommended
cutting this task on the grounds that P8 stated its own method; the ruling for this plan is that the
method P8 stated **is this**, and shipping it here means the day P8 lands, the check exists and was
not written by someone who wanted it to pass.

- [ ] **Step 1: Write the fixture transports**

```python
# tests/p7/transport_fixtures.py
"""Conforming and non-conforming transports, for proving the guard in both directions.

Each factory builds a real `ModuleType` populated with real function objects, rather
than a source string: the guard resolves annotations through `fn.__globals__`, which
is this module's namespace, so `Released`, `Path`, `Observation` and `TextUnit` all
resolve exactly as they would in a real transport module. Nothing here is executed by
the guard; only its signature is read.

`_module` sets `__module__` on each member it is given, because the guard filters on
`__module__` to distinguish a function a module DEFINES from one it merely imported.
Members passed as keywords are left alone, which is how the imported-helper fixture is
built.
"""
from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType

from evidence_shape.observation import Observation
from evidence_shape.text_units import TextUnit

from privacy.release import Released


def _module(name: str, *defined, **imported) -> ModuleType:
    module = ModuleType(name)
    for member in defined:
        member.__module__ = name
        setattr(module, member.__name__, member)
    for attribute, value in imported.items():
        setattr(module, attribute, value)
    return module


# --- conforming ---------------------------------------------------------------

def conforming_transport() -> ModuleType:
    """The shape P8's Done-means 1 requires: one public function, one parameter,
    annotated `Released`."""

    def send(released: Released) -> str:
        return released.release_id

    return _module("conforming_transport", send)


def conforming_transport_with_a_timeout() -> ModuleType:
    """A non-content parameter beside the release. Done-means 3 constrains the
    CONTENT parameter -- "No transport function accepts a string, a file path, or an
    observation record" -- and says nothing about a timeout."""

    def send(released: Released, timeout: int = 30) -> str:
        return released.release_id

    return _module("conforming_transport_with_a_timeout", send)


def conforming_transport_as_a_class() -> ModuleType:
    """The likeliest real shape: a client wrapper. The receiver is skipped; the
    parameter is not."""

    class Client:
        def send(self, released: Released) -> str:
            return released.release_id

    return _module("conforming_transport_as_a_class", Client)


def conforming_transport_with_an_imported_helper() -> ModuleType:
    """`json.dumps` in the namespace is not an entry point this module defines."""

    def send(released: Released) -> str:
        return released.release_id

    return _module("conforming_transport_with_an_imported_helper", send,
                   dumps=json.dumps)


# --- non-conforming: the count --------------------------------------------------

def transport_with_two_entry_points() -> ModuleType:
    def send(released: Released) -> str:
        return released.release_id

    def send_batch(released: Released) -> str:
        return released.release_id

    return _module("transport_with_two_entry_points", send, send_batch)


def transport_with_no_entry_point() -> ModuleType:
    return _module("transport_with_no_entry_point")


# --- non-conforming: the content types -----------------------------------------

def transport_taking_a_string() -> ModuleType:
    def send(prompt: str) -> str:
        return prompt

    return _module("transport_taking_a_string", send)


def transport_taking_a_path() -> ModuleType:
    def send(document: Path) -> str:
        return str(document)

    return _module("transport_taking_a_path", send)


def transport_taking_an_observation() -> ModuleType:
    def send(observation: Observation) -> str:
        return observation.raw_value

    return _module("transport_taking_an_observation", send)


def transport_taking_a_text_unit() -> ModuleType:
    def send(unit: TextUnit) -> str:
        return unit.text

    return _module("transport_taking_a_text_unit", send)


def transport_taking_bytes() -> ModuleType:
    def send(payload: bytes) -> str:
        return payload.decode()

    return _module("transport_taking_bytes", send)


def transport_taking_a_list_of_strings() -> ModuleType:
    """The hole a naive checker leaves: no parameter is annotated `str`, and every
    element of one of them is."""

    def send(released: Released, extra: list[str]) -> str:
        return released.release_id

    return _module("transport_taking_a_list_of_strings", send)


def transport_taking_a_sequence_of_strings() -> ModuleType:
    def send(released: Released, extra: Sequence[str]) -> str:
        return released.release_id

    return _module("transport_taking_a_sequence_of_strings", send)


def transport_taking_an_optional_path() -> ModuleType:
    def send(released: Released, attachment: Path | None = None) -> str:
        return released.release_id

    return _module("transport_taking_an_optional_path", send)


# --- non-conforming: the ways a parameter avoids being annotated ----------------

def transport_with_an_unannotated_parameter() -> ModuleType:
    def send(released):
        return released

    return _module("transport_with_an_unannotated_parameter", send)


def transport_taking_var_keyword() -> ModuleType:
    """`**payload` accepts a prompt under any name at all."""

    def send(released: Released, **payload) -> str:
        return released.release_id

    return _module("transport_taking_var_keyword", send)


def transport_taking_var_positional() -> ModuleType:
    def send(released: Released, *parts) -> str:
        return released.release_id

    return _module("transport_taking_var_positional", send)


def transport_with_no_released_parameter() -> ModuleType:
    """One entry point, nothing forbidden, and no release either -- so nothing binds
    the call to a policy version, a model target or an audit record."""

    def send(timeout: int = 30) -> str:
        return "sent"

    return _module("transport_with_no_released_parameter", send)


# --- non-conforming: the ones a source scan would pass --------------------------

def transport_with_a_private_string_helper() -> ModuleType:
    """The un-released path, unexported. It is still a path."""

    def send(released: Released) -> str:
        return _format(released.release_id)

    def _format(text: str) -> str:
        return text

    return _module("transport_with_a_private_string_helper", send, _format)


def transport_as_a_class_taking_a_string() -> ModuleType:
    class Client:
        def send(self, prompt: str) -> str:
            return prompt

    return _module("transport_as_a_class_taking_a_string", Client)


def transport_whose_docstring_mentions_released() -> ModuleType:
    """The fixture that decides the technique.

    A source-text scan for `Released` passes this module. Its entry point takes a
    string.
    """

    def send(prompt: str) -> str:
        """Send a Released to the model. Accepts only a Released. Released, Released."""
        return prompt

    return _module("transport_whose_docstring_mentions_released", send)
```

- [ ] **Step 2: Write the failing test**

```python
# tests/p7/test_p7_transport.py
"""Done-means 3's instrument, proven in both directions.

§8.4 opens with a sequencing requirement -- "Privacy policy must be enforced before
content reaches any model or external connector" -- and P8's Done-means 1 states the
method: "Exactly one function in the codebase constructs a model request, and its only
parameter type is P7's `Released`. A call without a release is not constructible.
Verified by inspection plus a test that the un-released path does not type-check /
does not exist."

`assert_single_egress` is that inspection. It is an existence proof over a module
namespace, not a runtime check: it answers whether a string-prompt entry point EXISTS,
and it answers by resolving annotations rather than by reading text. The last test in
this file states, by name, what it cannot do.
"""
import inspect
from pathlib import Path

import pytest

from evidence_shape.observation import Observation
from evidence_shape.text_units import TextUnit

from privacy.transport_guard import (
    CONTENT_PARAMETER_TYPES, EgressGuardFailure, MultipleEgressPoints,
    NoEgressPoint, UnreleasedContentParameter, assert_single_egress,
    egress_functions,
)

import transport_fixtures as fixtures


# --- the conforming shapes pass -------------------------------------------------

def test_the_conforming_transport_passes():
    # One public function, one parameter, annotated `Released`. A checker only proven
    # on the passing case is an assertion that has never been tested, so this is the
    # first of twenty-two and not the whole file.
    assert_single_egress(fixtures.conforming_transport()) is None


def test_a_non_content_parameter_beside_the_release_is_allowed():
    # Done-means 3 constrains the CONTENT parameter: "No transport function accepts a
    # string, a file path, or an observation record." A timeout is none of those, and
    # a guard that refused one would make the real transport unwritable.
    assert_single_egress(fixtures.conforming_transport_with_a_timeout())


def test_a_class_based_transport_passes():
    # The receiver is skipped and the parameter is checked. This is the shape an SDK
    # client wrapper takes, so a module-level-functions-only guard would be blind to
    # the most likely real transport.
    assert_single_egress(fixtures.conforming_transport_as_a_class())


def test_a_string_return_annotation_is_allowed():
    # The model's reply comes back as text. The gate governs what LEAVES, and pinning
    # this stops a later tightening from making the real transport unrepresentable.
    module = fixtures.conforming_transport()
    assert_single_egress(module)
    only = egress_functions(module)[0]
    assert inspect.signature(only, eval_str=True).return_annotation is str


def test_an_imported_helper_is_not_counted_as_an_entry_point():
    # A real transport imports things. The guard filters on `__module__`, so a helper
    # the module did not define is not one of its entry points.
    module = fixtures.conforming_transport_with_an_imported_helper()
    assert hasattr(module, "dumps")
    assert [fn.__name__ for fn in egress_functions(module)] == ["send"]
    assert_single_egress(module)


# --- exactly one entry point ----------------------------------------------------

def test_two_entry_points_fail():
    with pytest.raises(MultipleEgressPoints) as caught:
        assert_single_egress(fixtures.transport_with_two_entry_points())
    assert "send" in str(caught.value) and "send_batch" in str(caught.value)


def test_no_entry_point_fails():
    # "Exactly one" is violated by zero as surely as by two, and a module with no
    # entry point is not a transport. Naming this `MultipleEgressPoints` would have
    # been a lie in the exception name, which is why the guard publishes both.
    with pytest.raises(NoEgressPoint):
        assert_single_egress(fixtures.transport_with_no_entry_point())


# --- the content types ----------------------------------------------------------

def test_the_five_content_types_are_the_published_set():
    assert CONTENT_PARAMETER_TYPES == frozenset(
        {str, bytes, Path, Observation, TextUnit})


def test_a_transport_taking_a_string_fails():
    with pytest.raises(UnreleasedContentParameter, match="prompt"):
        assert_single_egress(fixtures.transport_taking_a_string())


def test_a_transport_taking_a_path_fails():
    with pytest.raises(UnreleasedContentParameter, match="document"):
        assert_single_egress(fixtures.transport_taking_a_path())


def test_a_transport_taking_an_observation_fails():
    with pytest.raises(UnreleasedContentParameter, match="observation"):
        assert_single_egress(fixtures.transport_taking_an_observation())


def test_a_transport_taking_a_text_unit_fails():
    with pytest.raises(UnreleasedContentParameter, match="unit"):
        assert_single_egress(fixtures.transport_taking_a_text_unit())


def test_a_transport_taking_bytes_fails():
    with pytest.raises(UnreleasedContentParameter, match="payload"):
        assert_single_egress(fixtures.transport_taking_bytes())


# --- containers and unions, which is where "takes no string" hides ---------------

def test_a_list_of_strings_fails():
    with pytest.raises(UnreleasedContentParameter, match="extra"):
        assert_single_egress(fixtures.transport_taking_a_list_of_strings())


def test_a_sequence_of_strings_fails():
    with pytest.raises(UnreleasedContentParameter, match="extra"):
        assert_single_egress(fixtures.transport_taking_a_sequence_of_strings())


def test_an_optional_path_fails():
    with pytest.raises(UnreleasedContentParameter, match="attachment"):
        assert_single_egress(fixtures.transport_taking_an_optional_path())


# --- the ways a parameter avoids being annotated ---------------------------------

def test_an_unannotated_parameter_fails():
    # An unannotated parameter is not shown to be a `Released`, and "not shown to be"
    # is the only standard an inspection can hold.
    with pytest.raises(UnreleasedContentParameter, match="released"):
        assert_single_egress(fixtures.transport_with_an_unannotated_parameter())


def test_var_keyword_fails():
    with pytest.raises(UnreleasedContentParameter, match="payload"):
        assert_single_egress(fixtures.transport_taking_var_keyword())


def test_var_positional_fails():
    with pytest.raises(UnreleasedContentParameter, match="parts"):
        assert_single_egress(fixtures.transport_taking_var_positional())


def test_a_transport_with_no_released_parameter_fails():
    # Nothing forbidden and no release either. SPEC §6: the payload "is bound to one
    # model target and one prompt fingerprint, and is single-use" -- a call carrying no
    # release is bound to nothing and has no audit record behind it.
    with pytest.raises(UnreleasedContentParameter, match="Released"):
        assert_single_egress(fixtures.transport_with_no_released_parameter())


# --- the two fixtures a weaker guard would pass ----------------------------------

def test_a_private_string_helper_fails():
    """"The un-released path does not exist" is about the module, not its exports.

    A private `_format(text: str)` beside the entry point is a string-prompt path that
    happens to be unexported, and inside a module whose whole job is egress there is
    nothing for it to legitimately be. The entry-point COUNT is taken over public
    functions; the content check is taken over all of them.
    """
    with pytest.raises(UnreleasedContentParameter, match="_format"):
        assert_single_egress(fixtures.transport_with_a_private_string_helper())


def test_a_class_method_taking_a_string_fails():
    with pytest.raises(UnreleasedContentParameter, match="Client.send"):
        assert_single_egress(fixtures.transport_as_a_class_taking_a_string())


def test_the_check_reads_signatures_and_never_source_text():
    """The fixture that decides the technique.

    Its docstring says "Released" four times and its entry point takes a `str`. A
    source scan passes it. `inspect.signature(..., eval_str=True)` does not, because
    it never reads the text -- it resolves the annotation objects.
    """
    module = fixtures.transport_whose_docstring_mentions_released()
    assert "Released" in egress_functions(module)[0].__doc__
    with pytest.raises(UnreleasedContentParameter, match="prompt"):
        assert_single_egress(module)


# --- shape of the guard's own surface --------------------------------------------

def test_egress_functions_returns_only_the_public_entry_points():
    module = fixtures.transport_with_a_private_string_helper()
    assert [fn.__name__ for fn in egress_functions(module)] == ["send"]
    assert hasattr(module, "_format")


def test_every_failure_shares_one_base():
    # A caller that does not care WHICH way a transport failed catches one thing.
    for failure in (MultipleEgressPoints, NoEgressPoint, UnreleasedContentParameter):
        assert issubclass(failure, EgressGuardFailure)
    for factory in (fixtures.transport_with_two_entry_points,
                    fixtures.transport_with_no_entry_point,
                    fixtures.transport_taking_a_string):
        with pytest.raises(EgressGuardFailure):
            assert_single_egress(factory())


# --- the honest limit ------------------------------------------------------------

def test_running_this_over_the_real_transport_is_p8s_obligation():
    """Done-means 3 is NOT closed by this file, and the coverage table says so.

        "**No — and this is a finding.** The transport is P8's. P7 proves the
        instrument, the unforgeable token, and the single materialisation locus. The
        property itself is P8 Done-means 1."

    There is no transport module in this repository to point `assert_single_egress`
    at. Layers L1 and L2 -- the unforgeable single-use release (Task 12) and the
    single materialisation locus (Tasks 9 and 21) -- are proven here; layer L3 is
    proven only to the extent that the instrument is proven, which is what the
    twenty-five tests above do.

    The call P8 must make, once `src/llm/transport.py` exists, is exactly:

        from privacy.transport_guard import assert_single_egress
        import llm.transport
        assert_single_egress(llm.transport)

    and P8's Done-means 1 -- not this test -- is what fails if it is never made.
    """
    import privacy.transport_guard as module

    assert inspect.isfunction(module.assert_single_egress)
    assert list(inspect.signature(module.assert_single_egress).parameters) == [
        "module"]
```

- [ ] **Step 3: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_transport.py -v`
Expected: FAIL — `ImportError: cannot import name 'CONTENT_PARAMETER_TYPES' from
'privacy.transport_guard'` (the module does not exist yet, so collection fails on the first import).

- [ ] **Step 4: Write `src/privacy/transport_guard.py`**

```python
# src/privacy/transport_guard.py
"""Done-means 3's instrument: does a string-prompt entry point exist in this module?

§8.4 opens with a sequencing requirement -- "Privacy policy must be enforced before
content reaches any model or external connector" -- which is a PROPERTY of a transport
P7 does not own. P8's Done-means 1 states the method for checking it: "Exactly one
function in the codebase constructs a model request, and its only parameter type is
P7's `Released`. A call without a release is not constructible. Verified by inspection
plus a test that the un-released path does not type-check / does not exist."

This module is that inspection, mechanised. It is an EXISTENCE PROOF over a module
namespace, not a runtime check on a call: nothing here executes a transport, and a
transport that passes has been shown to have no place to put a string, not to have
declined to use one.

Three rules, each of which separates a guard from a decoration:

1. **Resolved annotations, never source text.** `inspect.signature(fn, eval_str=True)`.
   A text scan sees `Released` in a docstring and passes a transport that takes a
   string; `tests/p7/transport_fixtures.py` contains exactly that module.
2. **Containers and unions are walked.** `list[str]`, `Sequence[str]` and
   `Path | None` are how a transport that "takes no string" takes one.
3. **Every function in the module is checked; only the public ones are counted.**
   "The un-released path does not exist" is a claim about the module, not its exports,
   so a private `_format(text: str)` fails it. Classes are walked too: a client
   wrapper `Client.send(self, prompt: str)` is the likeliest real shape.

Running this over the real transport is P8's obligation and cannot happen here --
there is no transport module in this repository. What P7 ships is a checker proven
against four conforming fixtures and seventeen non-conforming ones.
"""
from __future__ import annotations

import inspect
import typing
from collections.abc import Callable
from pathlib import Path
from types import FunctionType, ModuleType

from evidence_shape.observation import Observation
from evidence_shape.text_units import TextUnit

from privacy.release import Released

#: The types a transport may not take. Done-means 3: "No transport function accepts a
#: string, a file path, or an observation record." `bytes` and `TextUnit` are the same
#: refusal wearing different clothes -- P4's `TextUnit.text` is the complete extracted
#: text, which §8.4 puts in the always-local set.
CONTENT_PARAMETER_TYPES: frozenset[type] = frozenset(
    {str, bytes, Path, Observation, TextUnit})

#: Skipped on a method: it is the instance, not a parameter the caller supplies.
_RECEIVER_NAMES: frozenset[str] = frozenset({"self", "cls"})


class EgressGuardFailure(AssertionError):
    """A module does not satisfy Done-means 3's static property.

    An `AssertionError` because this is an assertion helper: it is called from a test
    and its failure is a test failure, not an exception a running product handles.
    """


class MultipleEgressPoints(EgressGuardFailure):
    """More than one public entry point. "Exactly one function ... constructs a model
    request" -- two doors is two places to audit and one of them will be forgotten."""


class NoEgressPoint(EgressGuardFailure):
    """No public entry point at all. Zero violates "exactly one" as surely as two, and
    a module with no entry point is not the transport the caller thinks it is."""


class UnreleasedContentParameter(EgressGuardFailure):
    """A parameter that could carry content without a release.

    Raised for a forbidden type, for a container or union that has one inside it, for
    an unannotated parameter (which is not SHOWN to be a `Released`, and "shown to be"
    is the only standard an inspection can hold), for an annotation that cannot be
    resolved, and for an entry point that takes no `Released` at all.
    """


def _defined_here(obj: object, module: ModuleType) -> bool:
    return getattr(obj, "__module__", None) == module.__name__


def _functions(module: ModuleType, *,
               public_only: bool) -> list[tuple[str, FunctionType, bool]]:
    """Every function this module defines, as `(qualified_name, fn, has_receiver)`.

    Module-level functions and the methods of module-level classes. Imported members
    are excluded by `__module__`, so a transport that imports a helper is not accused
    of having two entry points.
    """
    found: list[tuple[str, FunctionType, bool]] = []
    for name, value in vars(module).items():
        if name.startswith("__"):
            continue
        if public_only and name.startswith("_"):
            continue
        if isinstance(value, FunctionType) and _defined_here(value, module):
            found.append((name, value, False))
        elif isinstance(value, type) and _defined_here(value, module):
            for attribute, member in vars(value).items():
                if attribute.startswith("__"):
                    continue
                if public_only and attribute.startswith("_"):
                    continue
                if isinstance(member, (staticmethod, classmethod)):
                    found.append((f"{name}.{attribute}", member.__func__,
                                  isinstance(member, classmethod)))
                elif isinstance(member, FunctionType):
                    found.append((f"{name}.{attribute}", member, True))
    found.sort(key=lambda entry: entry[0])
    return found


def _leaves(annotation: object) -> list[object]:
    """Every leaf of a possibly-parameterised annotation.

    `list[str]` -> `[str]`; `Path | None` -> `[Path, NoneType]`;
    `dict[str, Released]` -> `[str, Released]`. This is rule 2, and without it a
    transport declares `extra: list[str]` and passes.
    """
    arguments = typing.get_args(annotation)
    if not arguments:
        return [annotation]
    leaves: list[object] = []
    for argument in arguments:
        leaves.extend(_leaves(argument))
    return leaves


def _parameters(qualified_name: str, function: FunctionType,
                has_receiver: bool) -> list[inspect.Parameter]:
    try:
        signature = inspect.signature(function, eval_str=True)
    except (NameError, TypeError) as error:
        raise UnreleasedContentParameter(
            f"{qualified_name}: an annotation could not be resolved ({error}), so no "
            "parameter can be shown to be a Released"
        ) from error
    parameters = list(signature.parameters.values())
    if has_receiver and parameters and parameters[0].name in _RECEIVER_NAMES:
        parameters = parameters[1:]
    return parameters


def egress_functions(module: ModuleType) -> list[Callable]:
    """The module's public entry points, sorted by name.

    Public module-level functions plus the public methods of public module-level
    classes. This is what Done-means 3 counts; the content check below looks wider.
    """
    return [function for _, function, _ in _functions(module, public_only=True)]


def assert_single_egress(module: ModuleType) -> None:
    """Assert Done-means 3's static property of `module`.

    Raises `NoEgressPoint` or `MultipleEgressPoints` when the module does not have
    exactly one public entry point, and `UnreleasedContentParameter` when any function
    it defines -- public or private, module-level or method -- has a parameter that
    could carry content, or when the entry point takes no `Released`.

    Returns `None` on success. Nothing is executed, nothing is written, and the module
    under inspection is not imported by this function: the caller imports it and hands
    it over, which is what keeps the guard usable from a test in another package.
    """
    public = _functions(module, public_only=True)
    if not public:
        raise NoEgressPoint(
            f"{module.__name__} defines no public entry point; Done-means 3 requires "
            "exactly one, and zero violates it as surely as two")
    if len(public) > 1:
        raise MultipleEgressPoints(
            f"{module.__name__} defines {len(public)} public entry points "
            f"{[name for name, _, _ in public]}; Done-means 3 requires exactly one, "
            "because two doors is two places to audit")

    for qualified_name, function, has_receiver in _functions(module,
                                                            public_only=False):
        for parameter in _parameters(qualified_name, function, has_receiver):
            if parameter.annotation is inspect.Parameter.empty:
                raise UnreleasedContentParameter(
                    f"{qualified_name}({parameter.name}) is unannotated, so it cannot "
                    "be shown to be a Released")
            for leaf in _leaves(parameter.annotation):
                if leaf in CONTENT_PARAMETER_TYPES:
                    raise UnreleasedContentParameter(
                        f"{qualified_name}({parameter.name}) accepts {leaf!r}, which "
                        "is content the gate never minted a release for")

    name, entry_point, has_receiver = public[0]
    if not any(parameter.annotation is Released
               for parameter in _parameters(name, entry_point, has_receiver)):
        raise UnreleasedContentParameter(
            f"{name} takes no Released; SPEC §6 binds a release to one model target "
            "and one prompt fingerprint, and a call carrying none is bound to nothing")
```

- [ ] **Step 5: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_transport.py -v`
Expected: PASS — 26 passed

- [ ] **Step 6: Run P7's suite, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–19 green, and the 1302 P1–P5 tests still green (P7 modified no file
belonging to another part).

- [ ] **Step 7: Commit**

```bash
git add src/privacy/transport_guard.py tests/p7/transport_fixtures.py tests/p7/test_p7_transport.py
git commit -m "feat(P7): the transport guard, proven against one conforming and seventeen non-conforming transports"
```

---

---

### Task 20: The published fixtures (SPEC §11)

**Files:**
- Create: `src/privacy/fixtures.py`
- Test: `tests/p7/test_p7_fixtures.py`

**Interfaces:**
- Consumes: `privacy.release.ModelCallRequest`, `.ModelTarget`, `.Target`, `.Released`, `.Denied`,
  `.NeedsConsent`, `.Gate`; `privacy.items.Excerpt`, `.RedactedIdentifier`, `.CandidateLabel`,
  `.MetadataField`, `.EvidenceReference`, `.Filename`; `privacy.redaction.RedactionEntry`;
  `privacy.consent.ConsentRequirement`; `privacy.audit.AuditRecord`, `.AUDIT_FIELDS`;
  `privacy.policy.Policy`; `privacy.classification.ClassificationRecord`;
  `privacy.vocabulary.DENIAL_REASONS`, `.OPERATION_MODES`, `.CONSENT_OPTIONS`, `.HANDLING_CLASSES`;
  `privacy.denial.PROTECTED_RECORDS_TEMPLATE`; `evidence_shape.location.TextSpan`;
  `evidence_shape.fixtures.FIXTURES` (as `P4_FIXTURES`, for the substrate an excerpt resolves
  against).
- Produces (`fixtures.py`):
  - `GateFixture` — frozen, eleven fields: `number: int`, `spec_case: str`,
    `policy: Policy`, `classification: ClassificationRecord | None`,
    `area: str | None`, `request: ModelCallRequest`,
    `decision: Released | Denied | NeedsConsent`, `audit_record: AuditRecord`,
    `p4_fixture: int | None`, `downstream_obligation: str | None`, `revoked: bool`.
  - `FIXTURES: tuple[GateFixture, ...]` — sixteen.
  - `FIXTURE_CLOCK: str`, `FIXTURE_AREA: str`, `LOCAL_MODEL`, `CLOUD_MODEL`.
  - `SPEC_11_ITEMS: tuple[str, ...]` — SPEC §11's five *"plus"* items, in the SPEC's own words.
  - `FIXTURE_COVERAGE: Mapping[str, tuple[int, ...]]` — thirteen keys: the eight `Denied.reason`
    values and the five `SPEC_11_ITEMS`.
  - `MODE_SWEEP: Mapping[str, int]` — operation mode → the fixture number that exercises a protected
    file under it.
  - `by_number(n) -> GateFixture`, `UnknownFixture`.

**Done-means:** 11 (first clause; the second clause is P8's test run and is named as such).

**One published surface this task pins for Task 11, because the fixtures cannot be replayed without
it.** `Gate` takes a **required keyword** `scope_for: Callable[[str], str | None]` with **no default**.
SPEC Open question 3 — *"What is a 'corpus area'? … Consent grants cannot be scoped until this is
named"* — is unanswered, so a gate that resolved a file to an area would be answering it in code.
This is the identical discipline Task 15 applied to `files_in_scope` for the identical question, and
the skeleton's own negative-test table already anticipates it: *"Open question 3 leaves the area
undefined, so the test parameterises the scope."* Reported as a pin on Task 11.

**Five fields this task adds to the skeleton's `GateFixture`. Done-means 11 turns entirely on
replayability, and six fields cannot be replayed.** The skeleton's `Produces` lists `number`,
`spec_case`, `request`, `decision`, `audit_record`, `policy`.

1. **`classification`.** D2 makes `ClassificationRecord` P7's own authoritative record and the gate's
   second input. A fixture that carries a request and a policy but no classification cannot be
   replayed, because the gate would resolve every one of them to `Denied(unclassified)` and fifteen
   of the sixteen expected decisions would be wrong. `None` is a legitimate value and fixture 2 is
   the fixture where it is the point.
2. **`p4_fixture`.** The skeleton's own `Consumes` block already anticipates it —
   *"`evidence_shape.fixtures.FIXTURES` (for the P4 substrate a fixture excerpt resolves against)"* —
   and this is the field that names which of P4's nineteen. Naming the number rather than copying the
   observation is what keeps the two in lockstep: `observation_key` is derived from
   `(content_hash, extractor_name, locator, raw_value)`, so a P4 fixture that changes changes P7's
   key with it and the replay still resolves. A copied key would rot silently.
3. **`downstream_obligation`.** SPEC §11's last paragraph puts an obligation on P8 for exactly two of
   these fixtures. Carrying the sentence in the record rather than in a comment is what lets P8 read
   it; a comment in P7's source is not a contract P8 can consume.
4. **`area`.** Open question 3's parameter, carried as **data** rather than as a rule. `Gate` takes
   the resolver; the fixture supplies the answer. P7 still defines no area and Task 21 asserts it.
5. **`revoked`.** `policy_revoked` means a grant **existed and was withdrawn**. A fixture whose
   policy simply never carried the grant would be testing *never permitted*, which is a different
   denial with a different remedy. Task 5's `revoke_consent` is what the seeding step calls.

Reported as five additions.

**The sixteen fixtures are SPEC §11's list item for item, and two pairs look like duplicates until
you read what they differ on.** §11: *"Request → decision pairs, one per `Denied.reason`, plus: a
clean `Released` with redaction applied; a `NeedsConsent` returning all four options; a protected
file under each of the four modes; an `unreadable_unclassified` file; a `Protected Records` residual
request."* Eight plus five items, sixteen fixtures, because *"a protected file under each of the four
modes"* is four.

- **Fixture 2 (`unclassified`) and fixture 15 (an `unreadable_unclassified` file) are not the same
  fixture.** Fixture 2 has **no `ClassificationRecord` at all** — nothing has looked. Fixture 15 has
  one, and its `handling_class` **is** `unreadable_unclassified` — something looked and could not
  read it, which is §2.9's indexed-but-unreadable case and P4's fixture 18 (`completeness =
  "unreadable"`). Both deny with reason `unclassified`, and the distinction between them is D2's
  third clause: *"nothing has looked"* can never be read as *"this file carries nothing"*. A fixture
  set that collapsed them would delete the distinction D2 exists to protect.
- **Fixture 4 and fixture 16 are the two halves of one sentence.** §7.3: `Protected Records`
  *"must not cause filenames or content to be exposed in model prompts"*. Fixture 4 requests an
  `Excerpt` — the content half. Fixture 16 requests a `Filename` — the filename half, and the one
  §4's flagged reading of Open question 2 makes reachable at all.
- **Fixtures 1 and 13 differ on the item, not the mode.** Both are a protected file with a cloud
  target under `hybrid`. Fixture 1 asks for an `Excerpt`; fixture 13 asks for a `MetadataField`. That
  is the assertion that §8.4's protected rule is about **the prompt**, not about how innocuous the
  requested item is — *"Protected material should not be included in cloud-model prompts by
  default"* names no item kind.

**One precedence rule this task pins for Task 13, because the mode sweep cannot be written without
it.** A protected file with a cloud target under `offline` satisfies two denial reasons at once.
**Mode is evaluated first**, so fixtures 11 and 12 are `mode_forbids_target` and fixtures 13 and 14
are `protected_cloud_target`. The reason is §8.4's opening sentence — *"Privacy policy must be
enforced before content reaches any model or external connector"* — read with §8.4's mode table:
under `offline`, *"No content leaves the device"* for **any** file, so the mode answer is the more
general and the more truthful one. Telling a user their passport was blocked because it is a passport
when it would have been blocked anyway is a false explanation, and §8.6 requires the UI to show
*"what has been deferred, and why"*. Reported as a pin on Task 13.

**Every fixture is replayed through the real gate and compared field for field, and that is the
substance of the task.** SPEC §11's second sentence — *"Each fixture carries the audit record the
gate would have appended"* — is satisfiable two ways, and one of them is a trap: a hand-written audit
record is a second implementation of the gate that drifts from the first, and the drift is invisible
because both sides are P7's. So `tests/p7/test_p7_fixtures.py` seeds a real database from the
fixture, calls the real `Gate`, and compares. **`file_id` is the only substituted field**, because
`record_file` accepts an explicit `content_hash` and every `observation_key` is derived from the
content hash rather than the file id. The substituted and minted field names are published in the
test as two small frozen sets, so the ignore-list cannot quietly grow.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_fixtures.py
"""Done-means 11's first clause, and its second clause named as P8's rather than faked.

SPEC §11: "Request -> decision pairs, one per `Denied.reason`, plus: a clean
`Released` with redaction applied; a `NeedsConsent` returning all four options; a
protected file under each of the four modes; an `unreadable_unclassified` file; a
`Protected Records` residual request. Each fixture carries the audit record the gate
would have appended."

The second sentence is what makes this worth doing and what makes it hard. A fixture
carrying a HAND-WRITTEN audit record is a second implementation of the gate, and it
drifts from the first invisibly because both sides belong to P7. So every fixture here
is replayed through the real gate against a real database and compared field for
field, and only the identity fields a replay cannot preserve are excused -- by name,
in a frozen set, so the excuse list cannot grow quietly.
"""
import dataclasses

import pytest

from database_agent.files_table import record_file

from evidence_shape.fixtures import FIXTURES as P4_FIXTURES
from evidence_shape.store import record_observation, record_run, record_text_unit

from privacy.audit import AUDIT_FIELDS, audit_record
from privacy.classification_store import ClassificationStore
from privacy.fixtures import (
    FIXTURE_CLOCK, FIXTURE_COVERAGE, FIXTURES, GateFixture, MODE_SWEEP, SPEC_11_ITEMS,
    UnknownFixture, by_number,
)
from privacy.gate import Gate
from privacy.policy import revoke_consent, set_policy
from privacy.release import Denied, NeedsConsent, Released, Target
from privacy.vocabulary import (
    CONSENT_OPTIONS, DENIAL_REASONS, HANDLING_CLASSES, OPERATION_MODES,
)

COMPONENT = "0.1.0"

#: The only field a replay cannot preserve. `record_file` mints the id; everything
#: else -- content hash, observation key, locator -- is content-addressed and survives.
SUBSTITUTED_FIELDS = frozenset({"file_id", "file_ids"})

#: Minted by the gate at call time, so a fixture can carry an example and never the
#: value. `audit_id` is P1's `lastrowid`; the other two are P7's own ids.
MINTED_FIELDS = frozenset({"audit_id", "release_id", "consent_request_id",
                           "appended_at"})


def p4(number: int):
    found = [f for f in P4_FIXTURES if f.number == number]
    assert found, f"P4 fixture {number} does not exist"
    return found[0]


def seed(conn, fixture, tmp_path) -> str:
    """A real `files` row, a real P4 substrate, a real policy, a real classification.

    Nothing here is synthesized past P1's own writer. `record_file` takes an explicit
    `content_hash` with `materialized=False`, which is what lets the row carry P4's
    fixture hash -- and therefore what makes the seeded `observation_key` identical to
    the published one. Without that, every excerpt in every fixture would address an
    observation the replay had not written.
    """
    source = p4(fixture.p4_fixture) if fixture.p4_fixture is not None else None
    content_hash = (source.run.content_hash if source is not None
                    else fixture.request.target.file_ids[0])
    corpus = tmp_path / f"corpus-{fixture.number}"
    corpus.mkdir(parents=True, exist_ok=True)
    document = corpus / "fixture-document.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    file_id = record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size, observed_timestamps='{"mtime": 1.0}',
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=False,
        content_hash=content_hash)

    if source is not None:
        run = dataclasses.replace(source.run, file_id=file_id)
        record_run(conn, run)
        for unit in source.text_units:
            record_text_unit(conn, unit)
        for observation in source.observations:
            record_observation(conn, dataclasses.replace(observation, file_id=file_id))

    set_policy(conn, fixture.policy, component_version=COMPONENT,
               user_id="joseph",
               reason="the published fixture's policy")
    if fixture.revoked:
        # Task 5's `revoke_consent` records the withdrawal and mints a new
        # `policy_version`; it appends no event (Task 15 owns that append). It is what
        # makes `policy_revoked` distinguishable from "never granted", which is the
        # whole content of that denial reason.
        revoke_consent(conn, fixture.policy, fixture.area, user_id="joseph",
                       component_version=COMPONENT, observed_at=FIXTURE_CLOCK)
    if fixture.classification is not None:
        ClassificationStore(conn).write(
            dataclasses.replace(fixture.classification, file_id=file_id,
                                content_hash=content_hash))
    return file_id


def replay(conn, fixture, tmp_path):
    """Run the fixture's own request through the real gate and return the decision."""
    file_id = seed(conn, fixture, tmp_path)
    request = dataclasses.replace(
        fixture.request,
        target=Target(file_ids=(file_id,), group_id=fixture.request.target.group_id))
    # `scope_for` has no default. SPEC Open question 3 -- "What is a 'corpus area'? ...
    # Consent grants cannot be scoped until this is named" -- is unanswered, so the
    # resolver is the caller's and the fixture carries the answer as data.
    gate = Gate(conn, component_version=COMPONENT,
                scope_for=lambda _file_id: fixture.area)
    return gate.release(request), file_id


# --- SPEC §11's list, item for item -----------------------------------------

def test_the_coverage_map_names_every_spec_11_item_and_nothing_else():
    # The test that fails if a list member has no fixture, which is the only thing
    # standing between "sixteen fixtures" and "the sixteen the SPEC asked for".
    assert set(FIXTURE_COVERAGE) == set(DENIAL_REASONS) | set(SPEC_11_ITEMS)
    for item, numbers in FIXTURE_COVERAGE.items():
        assert numbers, item
        for number in numbers:
            assert by_number(number)


def test_the_five_plus_items_carry_the_specs_own_words():
    # A paraphrase here is a failing test and not an editorial choice: SPEC_11_ITEMS is
    # the checklist, and a checklist rewritten in the author's words no longer checks
    # the document it came from.
    assert SPEC_11_ITEMS == (
        "a clean `Released` with redaction applied",
        "a `NeedsConsent` returning all four options",
        "a protected file under each of the four modes",
        "an `unreadable_unclassified` file",
        "a `Protected Records` residual request",
    )


def test_there_is_one_fixture_per_denial_reason():
    for reason in DENIAL_REASONS:
        reached = [f for f in FIXTURES
                   if isinstance(f.decision, Denied) and f.decision.reason == reason]
        assert reached, reason


def test_the_denial_reasons_are_all_eight_and_no_ninth():
    reasons = {f.decision.reason for f in FIXTURES if isinstance(f.decision, Denied)}
    assert reasons == set(DENIAL_REASONS)
    assert len(DENIAL_REASONS) == 8


def test_fixture_numbers_are_dense_unique_and_sixteen():
    numbers = [f.number for f in FIXTURES]
    assert numbers == list(range(1, 17))


def test_by_number_raises_on_a_number_nobody_published():
    assert by_number(1).number == 1
    with pytest.raises(UnknownFixture):
        by_number(99)


def test_the_gate_fixture_publishes_eleven_named_fields():
    # Six are the skeleton's. Five are added by this task and every one of them is
    # either a held-open question the fixture answers AS DATA (`area`) or a replay
    # precondition without which "each fixture carries the audit record the gate would
    # have appended" is unfalsifiable (`classification`, `p4_fixture`, `revoked`).
    # `downstream_obligation` carries SPEC §11's own two sentences to P8.
    assert [f.name for f in dataclasses.fields(GateFixture)] == [
        "number", "spec_case", "policy", "classification", "area", "request",
        "decision", "audit_record", "p4_fixture", "downstream_obligation", "revoked"]


def test_exactly_one_fixture_revokes_a_grant_before_the_call():
    # §8.4: the user may "revoke a policy for future runs". `policy_revoked` means a
    # grant EXISTED and was withdrawn; a fixture with no grant to begin with would be
    # testing "never permitted", which is a different denial.
    revoking = {f.number for f in FIXTURES if f.revoked}
    assert revoking == {3}
    fixture = by_number(3)
    assert fixture.decision.reason == "policy_revoked"
    assert fixture.area in dict(fixture.policy.consent_grants)


def test_the_corpus_area_is_carried_as_data_and_never_inferred():
    # Open question 3 stays open: P7 defines no area, so every fixture that needs one
    # states it and the gate takes a resolver with no default. Task 21 asserts
    # `src/privacy/` publishes no corpus-area definition of its own.
    scoped = {f.number: f.area for f in FIXTURES if f.area is not None}
    assert scoped
    assert all(isinstance(area, str) and area for area in scoped.values())
    for fixture in FIXTURES:
        for scope, _option in fixture.policy.consent_grants:
            assert isinstance(scope, str)


def test_no_fixture_invents_a_vocabulary_value():
    for fixture in FIXTURES:
        assert fixture.policy.operation_mode in OPERATION_MODES
        if fixture.classification is not None:
            assert fixture.classification.handling_class in HANDLING_CLASSES
        if isinstance(fixture.decision, Denied):
            assert fixture.decision.reason in DENIAL_REASONS
        if isinstance(fixture.decision, NeedsConsent):
            assert set(fixture.decision.options) == set(CONSENT_OPTIONS)


# --- the two pairs that look like duplicates and are not ---------------------

def test_the_unclassified_fixture_has_no_record_and_the_unreadable_one_does():
    # D2's third clause: `Unreadable or unclassified` is a GATE OUTCOME, not a file
    # fact, so "nothing has looked" and "something looked and could not read it" are
    # two different states that produce one verdict. Collapsing these two fixtures
    # would delete the distinction D2 exists to protect.
    nothing_looked = by_number(2)
    looked_and_failed = by_number(15)
    assert nothing_looked.classification is None
    assert looked_and_failed.classification is not None
    assert looked_and_failed.classification.handling_class == "unreadable_unclassified"
    assert nothing_looked.decision.reason == looked_and_failed.decision.reason == (
        "unclassified")


def test_the_unreadable_fixture_stands_on_p4s_own_unreadable_run():
    # §2.9's indexed-but-unreadable, which P4 fixture 18 carries as
    # `completeness = "unreadable"`. P7 invents no extraction outcome of its own.
    assert by_number(15).p4_fixture == 18
    assert p4(18).run.completeness == "unreadable"


def test_both_halves_of_7_3_are_covered_separately():
    # §7.3: Protected Records "must not cause filenames or content to be exposed in
    # model prompts". Two nouns, two fixtures.
    from privacy.items import Excerpt, Filename
    content_half = by_number(4)
    filename_half = by_number(16)
    assert all(isinstance(item, Excerpt)
               for item in content_half.request.requested_items)
    assert all(isinstance(item, Filename)
               for item in filename_half.request.requested_items)
    assert content_half.decision.reason == "protected_records_template"
    assert filename_half.decision.reason == "protected_records_template"


def test_the_protected_cloud_rule_does_not_depend_on_the_item_kind():
    # §8.4 names no item kind: "Protected material should not be included in
    # cloud-model prompts by default." Fixture 1 asks for an excerpt, fixture 13 for a
    # metadata field, and both are denied for the same reason under the same mode.
    from privacy.items import Excerpt, MetadataField
    assert by_number(1).policy.operation_mode == by_number(13).policy.operation_mode
    assert isinstance(by_number(1).request.requested_items[0], Excerpt)
    assert isinstance(by_number(13).request.requested_items[0], MetadataField)
    assert by_number(1).decision.reason == "protected_cloud_target"
    assert by_number(13).decision.reason == "protected_cloud_target"


# --- the mode sweep ---------------------------------------------------------

def test_a_protected_file_appears_under_each_of_the_four_modes():
    assert set(MODE_SWEEP) == set(OPERATION_MODES)
    for mode, number in MODE_SWEEP.items():
        fixture = by_number(number)
        assert fixture.policy.operation_mode == mode
        assert fixture.classification is not None
        assert fixture.classification.protected is True


def test_mode_is_evaluated_before_protection_so_the_reason_is_the_general_one():
    # The precedence this task pins for Task 13. Under `offline` and `local_model` a
    # cloud target is unreachable for ANY file, so naming the passport as the cause
    # would be a false explanation -- and §8.6 requires the UI to show "what has been
    # deferred, and why". Under `hybrid` and `cloud_assisted` the target IS reachable
    # and the protection is the real cause.
    assert by_number(MODE_SWEEP["offline"]).decision.reason == "mode_forbids_target"
    assert by_number(MODE_SWEEP["local_model"]).decision.reason == "mode_forbids_target"
    assert by_number(MODE_SWEEP["hybrid"]).decision.reason == "protected_cloud_target"
    assert by_number(
        MODE_SWEEP["cloud_assisted"]).decision.reason == "protected_cloud_target"


def test_the_mode_only_denial_uses_a_non_protected_file():
    # Fixture 8 isolates the mode axis: a `public_low`, unprotected file still cannot
    # reach a cloud target under `offline`. Without this, `mode_forbids_target` would
    # only ever be observed on protected files and the two rules would be untestable
    # apart.
    fixture = by_number(8)
    assert fixture.classification.handling_class == "public_low"
    assert fixture.classification.protected is False
    assert fixture.policy.operation_mode == "offline"
    assert fixture.decision.reason == "mode_forbids_target"


# --- the two non-denial branches --------------------------------------------

def test_the_released_fixture_applied_redaction_and_carries_a_manifest():
    # §11: "a clean `Released` with redaction applied".
    fixture = by_number(9)
    assert isinstance(fixture.decision, Released)
    assert fixture.audit_record.redaction_applied is True
    assert fixture.decision.redaction_manifest
    assert all(entry.identifier_class for entry in fixture.decision.redaction_manifest)


def test_the_needs_consent_fixture_offers_all_four_options_in_the_specs_order():
    # §8.4: the user should "choose whether to allow a local model, a cloud model, a
    # redacted prompt, or no model use". Four, and a surface that offers three has
    # made the decision for them.
    fixture = by_number(10)
    assert isinstance(fixture.decision, NeedsConsent)
    assert fixture.decision.options == CONSENT_OPTIONS
    assert len(CONSENT_OPTIONS) == 4


def test_the_needs_consent_fixture_has_no_reason_field_to_be_read_as_a_denial():
    # B2: `NeedsConsent` "is never an outcome the caller may absorb". P7's obligation
    # is to make the absorption unrepresentable, and the type-level form of that is
    # the absence of a `reason` field a caller could map onto a denial.
    names = {f.name for f in dataclasses.fields(by_number(10).decision)}
    assert "reason" not in names
    assert names == {"consent_request_id", "requirement", "options"}


# --- the P8 obligations, carried as data rather than as a comment ------------

def test_exactly_two_fixtures_carry_an_obligation_on_p8():
    carriers = {f.number for f in FIXTURES if f.downstream_obligation is not None}
    assert carriers == {6, 10}


def test_the_budget_fixture_says_a_p8_test_that_reaches_it_is_a_p8_failure():
    # SPEC §11, verbatim: a M9 backstop, not a gate result.
    obligation = by_number(6).downstream_obligation
    assert obligation == (
        "so P8 can prove its ladder ran first -- a P8 test that reaches this denial "
        "through the normal path is a P8 failure, not a gate result")
    assert by_number(6).decision.reason == "dossier_over_budget"


def test_the_consent_fixture_says_p8_must_return_the_branch_intact():
    assert by_number(10).downstream_obligation == (
        "so P8 can prove it returns the branch to its caller intact")


def test_done_means_11s_second_clause_is_p8s_test_run_and_not_assertable_here():
    # "and P8's harness passes its own tests against those fixtures with P7
    # unimplemented." P8 does not exist. This test exists so the limitation lives in
    # the suite rather than in a report nobody rereads -- the same posture Task 19
    # takes for Done-means 3.
    import importlib
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("llm_harness")
    assert all(f.decision is not None for f in FIXTURES), (
        "the P7 half -- published, replayable request/decision pairs -- is what this "
        "part can deliver; the P8 half is P8's test run")


# --- requests carry references, never content --------------------------------

def test_no_request_carries_materialised_content(p7_conn, tmp_path):
    # SPEC §6: requests "carry references, never materialised content". Asserted over
    # the item records rather than by eye, because a sixth item kind added later would
    # otherwise slip through.
    for fixture in FIXTURES:
        for item in fixture.request.requested_items:
            for field in dataclasses.fields(item):
                value = getattr(item, field.name)
                if isinstance(value, str):
                    assert "\n" not in value, (fixture.number, field.name)
                    assert len(value) < 200, (fixture.number, field.name)


def test_a_metadata_field_names_a_field_and_does_not_carry_its_value():
    from privacy.items import MetadataField
    names = {f.name for f in dataclasses.fields(MetadataField)}
    assert names == {"name"}


def test_excerpts_included_holds_key_and_span_pairs_and_not_the_text():
    # SPEC §7: "excerpts_included stores (observation_key, span) pairs plus the
    # redaction_manifest, not a second copy of the text". The always-local text
    # already exists once.
    unit_text = p4(8).text_units[0].text
    for fixture in FIXTURES:
        for key, span in fixture.audit_record.excerpts_included:
            assert key.startswith("sha256:")
            assert "-" in span
            assert unit_text not in key and unit_text not in span


# --- the fixtures stand on P4's fixtures, not on a private substrate ---------

def test_every_excerpt_addresses_an_observation_p4_published():
    # The reason `p4_fixture` names a NUMBER and does not copy the observation:
    # `observation_key` is derived from (content_hash, extractor_name, locator,
    # raw_value), so a P4 fixture that moves moves P7's key with it. A copied key
    # would rot silently and the replay would address nothing.
    from privacy.items import Excerpt, RedactedIdentifier
    for fixture in FIXTURES:
        addressed = [item for item in fixture.request.requested_items
                     if isinstance(item, (Excerpt, RedactedIdentifier))]
        if not addressed:
            continue
        assert fixture.p4_fixture is not None, fixture.number
        published = {o.observation_key for o in p4(fixture.p4_fixture).observations}
        for item in addressed:
            assert item.observation_key in published, (fixture.number, item)


# --- the replay: the fixture and the gate are one implementation -------------

@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_replaying_a_fixture_through_the_real_gate_reproduces_the_decision(
        p7_conn, tmp_path, number):
    fixture = by_number(number)
    decision, _ = replay(p7_conn, fixture, tmp_path)
    assert type(decision) is type(fixture.decision), fixture.spec_case
    if isinstance(fixture.decision, Denied):
        assert decision.reason == fixture.decision.reason
        assert decision.explanation
        assert decision.remedy_options
    if isinstance(fixture.decision, NeedsConsent):
        assert decision.options == fixture.decision.options
    if isinstance(fixture.decision, Released):
        assert decision.model_target == fixture.decision.model_target
        assert decision.policy_version == fixture.policy.policy_version


@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_replaying_a_fixture_reproduces_its_audit_record_field_for_field(
        p7_conn, tmp_path, number):
    # SPEC §11: "Each fixture carries the audit record the gate would have appended."
    # `would have appended` is a claim about the implementation, so it is checked
    # against the implementation and not against a second hand-written copy of it.
    fixture = by_number(number)
    decision, file_id = replay(p7_conn, fixture, tmp_path)
    appended = audit_record(p7_conn, _audit_id_of(p7_conn, decision))
    for field in AUDIT_FIELDS:
        if field in MINTED_FIELDS or field in SUBSTITUTED_FIELDS:
            continue
        assert getattr(appended, field) == getattr(fixture.audit_record, field), (
            fixture.number, field)


def test_the_excused_field_list_is_small_and_named():
    # An ignore-list is the standard way a golden-record test stops testing anything.
    # Five names, each with a reason, and the set is asserted rather than extended.
    assert SUBSTITUTED_FIELDS == {"file_id", "file_ids"}
    assert MINTED_FIELDS == {"audit_id", "release_id", "consent_request_id",
                             "appended_at"}
    assert len(SUBSTITUTED_FIELDS | MINTED_FIELDS) < len(AUDIT_FIELDS) / 2


@pytest.mark.parametrize("number", [f.number for f in FIXTURES])
def test_every_replay_leaves_exactly_one_audit_event(p7_conn, tmp_path, number):
    # §8.4: "Every model call should be recorded in a consent-aware audit record."
    # Every call, including the denied ones and the local ones -- §8.4 names no
    # exemption, and §8.2 covers "Every significant event affecting a file".
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    replay(p7_conn, by_number(number), tmp_path)
    after = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    assert after > before


def _audit_id_of(conn, decision) -> int:
    """The audit id the gate returned, whichever branch it returned it on."""
    if isinstance(decision, Released):
        return int(decision.audit_id)
    row = conn.execute(
        "SELECT event_id FROM events WHERE subsystem = 'P7' "
        "ORDER BY event_id DESC LIMIT 1").fetchone()
    return int(row["event_id"])
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_fixtures.py -v`
Expected: FAIL — `ImportError: cannot import name 'FIXTURE_COVERAGE' from 'privacy.fixtures'`
(the module does not exist yet, so collection fails on the first import).

- [ ] **Step 3: Write `src/privacy/fixtures.py`**

```python
# src/privacy/fixtures.py
"""SPEC §11's published fixtures: the door's behaviour as data, so P8 can be built
against P7 before P7 ships.

§11: "Request -> decision pairs, one per `Denied.reason`, plus: a clean `Released`
with redaction applied; a `NeedsConsent` returning all four options; a protected file
under each of the four modes; an `unreadable_unclassified` file; a `Protected Records`
residual request. Each fixture carries the audit record the gate would have appended."

Three things are true of this module and none of them is a style choice:

- **It is a LEAF.** Nothing else under `src/privacy/` imports it. That is what keeps
  the numbers it holds -- one `max_dossier_tokens`, one span length -- out of the
  gate: a fixture records a value the way a recorded call records one, and Task 21
  asserts no other module holds a bare number at all.
- **Every excerpt stands on one of P4's nineteen published fixtures.** The keys are
  computed from `evidence_shape.fixtures` at import, never copied. `observation_key`
  is derived from `(content_hash, extractor_name, locator, raw_value)` (M14, MINOR 8),
  so a P4 fixture that moves moves P7's key with it and the replay keeps resolving.
- **The always-local set is enforced twice, and fixture 7 is why.** Task 7 makes the
  nine named kinds unconstructible, so a request holding "OCR output" cannot be built
  and cannot be a fixture. `Denied(always_local_item)` is therefore reached the other
  way: by a CONSTRUCTIBLE `Excerpt` that RESOLVES to always-local content -- P4's
  fixture 8 is an `ocr.apple_vision` run in zone `ocr`, and §8.4 puts "OCR output" in
  the always-local set. Construction refuses the name; release refuses the resolution.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.fixtures import FIXTURES as P4_FIXTURES
from evidence_shape.location import TextSpan

from privacy.audit import AUDIT_FIELDS, AuditRecord
from privacy.classification import ClassificationRecord
from privacy.consent import ConsentRequirement
from privacy.denial import PROTECTED_RECORDS_TEMPLATE
from privacy.items import (
    CandidateLabel, EvidenceReference, Excerpt, Filename, MetadataField,
    RedactedIdentifier,
)
from privacy.policy import Policy
from privacy.redaction import RedactionEntry
from privacy.release import Denied, ModelCallRequest, ModelTarget, NeedsConsent, \
    Released, Target
from privacy.vocabulary import CONSENT_OPTIONS

#: One clock for every fixture. A fixture whose timestamps drift is a fixture whose
#: golden audit record cannot be compared field for field.
FIXTURE_CLOCK: str = "2026-08-22T09:00:00+00:00"

#: The area name every scoped fixture uses. It is a STRING THE CALLER SUPPLIED and not
#: a definition: SPEC Open question 3 asks "What is a 'corpus area'?" and P7 answers
#: nothing. `Gate` takes an `scope_for` resolver with no default for the same reason.
FIXTURE_AREA: str = "Academics"

LOCAL_MODEL = ModelTarget(locality="local", model_id="local-small", provider="local")
CLOUD_MODEL = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")

#: SPEC §11's five "plus" items, in the SPEC's own words. This is the checklist, so a
#: paraphrase here stops it checking the document it came from.
SPEC_11_ITEMS: tuple[str, ...] = (
    "a clean `Released` with redaction applied",
    "a `NeedsConsent` returning all four options",
    "a protected file under each of the four modes",
    "an `unreadable_unclassified` file",
    "a `Protected Records` residual request",
)


class UnknownFixture(KeyError):
    """A fixture number nobody published. Not a fallback, not the nearest neighbour."""


def _p4(number: int):
    for fixture in P4_FIXTURES:
        if fixture.number == number:
            return fixture
    raise UnknownFixture(f"P4 publishes no fixture {number}")


def _key(number: int) -> str:
    """P4 fixture `number`'s first observation key, computed by P4 and read here."""
    return _p4(number).observations[0].observation_key


def _hash(number: int) -> str:
    return _p4(number).run.content_hash


def _unit_length(number: int) -> int:
    return len(_p4(number).text_units[0].text)


def _policy(mode: str, *, grants: tuple[tuple[str, str], ...] = (),
            moves: Mapping[str, str] | None = None, version: str = "policy-1") -> Policy:
    """A policy at `mode`. Every redaction facet is at its more redacting value.

    W1's second half: "Where the design is silent on a redaction default, the more
    redacting option is the default." A fixture that shipped a `shown` facet would be
    publishing a posture §8.4's `must` forbids -- "The default posture must therefore
    be local-first and data-minimizing" -- and P8 would build against it.
    """
    return Policy(
        policy_version=version, operation_mode=mode, consent_grants=grants,
        redaction_settings={"names": "redacted", "previews": "redacted",
                            "thumbnails": "redacted", "ocr_text": "redacted",
                            "location_data": "redacted"},
        automatic_move_permissions=dict(moves or {}), plan_version="plan-1",
        set_at=FIXTURE_CLOCK)


def _classified(p4_number: int, handling_class: str, *, protected: bool,
                basis: str = "detector",
                reliability_state: str = "validated") -> ClassificationRecord:
    """A classification over P4 fixture `p4_number`'s bytes.

    `protected` is a PARAMETER here, never derived from `handling_class`. SPEC §2:
    "Neighbouring parts should consume the `protected` flag, not infer it from the
    class", and Open question 1 -- whether `protected` is exactly the top two classes
    -- is unsettled. Fixture 10 is the fixture that depends on it staying unsettled.
    """
    return ClassificationRecord(
        file_id="fixture-file", content_hash=_hash(p4_number),
        handling_class=handling_class, protected=protected, basis=basis,
        evidence_refs=(_key(p4_number),) if basis == "detector" else (),
        reliability_state=reliability_state, observed_at=FIXTURE_CLOCK)


def _request(*, stage: str, model_target: ModelTarget, items: tuple,
             fingerprint: str, max_dossier_tokens: int,
             template: str = "tpl.resolve_subject") -> ModelCallRequest:
    return ModelCallRequest(
        stage=stage, target=Target(file_ids=("fixture-file",), group_id=None),
        model_target=model_target, requested_items=items,
        prompt_template_id=template, prompt_fingerprint=fingerprint,
        max_dossier_tokens=max_dossier_tokens)


#: Built from `AUDIT_FIELDS` rather than from a literal keyword list, the way Task 15
#: builds its own. Task 10 owns SPEC §7's names and asserts they match §7 name for
#: name; constructing from the published tuple means a field this module never varies
#: can be respelled without breaking sixteen fixtures, while a field it DOES vary
#: disappearing fails loudly at the seam that cares.
_AUDIT_DEFAULTS: Mapping[str, object] = MappingProxyType({
    "audit_id": None,
    "release_id": None,
    "policy_version": "policy-1",
    "plan_version": "plan-1",
    "stage": "grouping",
    "outcome": "denied",
    "operation_mode": "offline",
    "authorizing_policy": "policy-1",
    "file_sensitivity": "unreadable_unclassified",
    "excerpts_included": (),
    "redaction_applied": False,
    "redaction_manifest": (),
    "model": {"locality": "local", "model_id": "local-small", "provider": "local"},
    "content_hashes": (),
    "content_hash": None,
    "prompt_fingerprint": "fp-fixture",
    "file_id": "fixture-file",
    "file_ids": ("fixture-file",),
    "group_id": None,
    "consent_request_id": None,
    "user_id": None,
    "observed_at": FIXTURE_CLOCK,
    "appended_at": FIXTURE_CLOCK,
})


def _audit(**over: object) -> AuditRecord:
    """Built from `AUDIT_FIELDS`, never from a literal keyword list.

    Task 10 owns SPEC §7's names and asserts they match §7 name for name. Building
    from the published tuple means a field these sixteen fixtures never vary can be
    respelled without breaking them, while a field they DO vary disappearing fails
    here, loudly, at the seam that cares.
    """
    missing = [name for name in AUDIT_FIELDS if name not in _AUDIT_DEFAULTS]
    if missing:
        raise KeyError(
            f"AUDIT_FIELDS names {missing} and this module has no value for them; "
            "SPEC §7 changed and the fixtures need a value, not a default")
    unknown = [name for name in over if name not in _AUDIT_DEFAULTS]
    if unknown:
        raise KeyError(
            f"{unknown} is not an audit field this module knows; a silently dropped "
            "keyword is how a fixture stops carrying the value it claims to carry")
    values = {name: _AUDIT_DEFAULTS[name] for name in AUDIT_FIELDS}
    values.update({name: value for name, value in over.items() if name in values})
    return AuditRecord(**values)


@dataclass(frozen=True)
class GateFixture:
    """One published request -> decision pair, replayable against the real gate.

    Six fields are the plan skeleton's. Five are added here: `classification`,
    `p4_fixture` and `revoked` because a fixture that cannot be seeded cannot be
    replayed, and Done-means 11 turns on replay; `area` because Open question 3 is
    open and the corpus area must therefore be data rather than a rule; and
    `downstream_obligation` because SPEC §11 puts an obligation on P8 for two of these
    and a comment in P7's source is not a contract P8 can read.
    """

    number: int
    spec_case: str
    policy: Policy
    classification: ClassificationRecord | None
    area: str | None
    request: ModelCallRequest
    decision: Released | Denied | NeedsConsent
    audit_record: AuditRecord
    p4_fixture: int | None
    downstream_obligation: str | None
    revoked: bool


def _denied(reason: str, explanation: str, *remedies: str,
            evidence_refs: tuple[str, ...] = ()) -> Denied:
    """Every denial carries an explanation and at least one legitimate alternative.

    §8.6 requires the UI to show "what has been deferred, and why", and a denial whose
    remedy list is empty is a dead end the user cannot act on.
    """
    return Denied(reason=reason, explanation=explanation,
                  remedy_options=tuple(remedies), evidence_refs=evidence_refs)


FIXTURES: tuple[GateFixture, ...] = (
    GateFixture(
        number=1,
        spec_case="Denied.reason = protected_cloud_target (an excerpt)",
        policy=_policy("hybrid", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(3),
                                        span=TextSpan(12043, 12051),
                                        reason="resolve the institution"),),
                         fingerprint="fp-01", max_dossier_tokens=2000),
        decision=_denied(
            "protected_cloud_target",
            "§8.4: protected material is not included in cloud-model prompts by "
            "default, and this policy is `hybrid` -- 'Sensitive files remain local; "
            "non-sensitive bounded dossiers may use a cloud LLM.'",
            "run the same request against a local model",
            "ask the user for a consent grant covering this area",
            evidence_refs=(_key(3),)),
        audit_record=_audit(outcome="denied", operation_mode="hybrid",
                            file_sensitivity="sensitive_personal",
                            content_hash=_hash(3), content_hashes=(_hash(3),),
                            prompt_fingerprint="fp-01",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=2,
        spec_case="Denied.reason = unclassified (nothing has looked)",
        policy=_policy("local_model"),
        classification=None,
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-02", max_dossier_tokens=2000),
        decision=_denied(
            "unclassified",
            "§8.4 makes classification a precondition of escalation -- 'classify data "
            "into handling classes before LLM escalation' -- and no classification "
            "exists for this file. Absence resolves to `unreadable_unclassified`, "
            "never to `public_low`.",
            "classify the file and retry",
            "resolve the question from local deterministic facts"),
        audit_record=_audit(outcome="denied", operation_mode="local_model",
                            prompt_fingerprint="fp-02"),
        p4_fixture=None, downstream_obligation=None, revoked=False),
    GateFixture(
        number=3,
        spec_case="Denied.reason = policy_revoked",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "public_low", protected=False),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(CandidateLabel(label="Columbia"),),
                         fingerprint="fp-03", max_dossier_tokens=2000),
        decision=_denied(
            "policy_revoked",
            "the consent grant authorizing a cloud model for this area was revoked. "
            "§8.4: revocation applies to future runs, so this call is decided against "
            "the policy version in force now.",
            "grant consent for this area again",
            "run the same request against a local model"),
        audit_record=_audit(outcome="denied", operation_mode="cloud_assisted",
                            file_sensitivity="public_low", content_hash=_hash(3),
                            content_hashes=(_hash(3),), prompt_fingerprint="fp-03",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=True),
    GateFixture(
        number=4,
        spec_case="Denied.reason = protected_records_template (the content half)",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "highly_sensitive_credential_bearing",
                                   protected=True, basis="safety_domain"),
        area=FIXTURE_AREA,
        request=_request(stage="placement", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(3),
                                        span=TextSpan(12043, 12051),
                                        reason="identify the issuing body"),),
                         fingerprint="fp-04", max_dossier_tokens=2000),
        decision=_denied(
            "protected_records_template",
            f"the file is held under the {PROTECTED_RECORDS_TEMPLATE} residual "
            "template, which 'must not cause filenames or content to be exposed in "
            "model prompts' (§7.3).",
            "resolve the placement from local deterministic facts",
            "ask the user to move the file out of the protected area explicitly",
            evidence_refs=(_key(3),)),
        audit_record=_audit(
            outcome="denied", operation_mode="cloud_assisted",
            file_sensitivity="highly_sensitive_credential_bearing",
            content_hash=_hash(3), content_hashes=(_hash(3),),
            prompt_fingerprint="fp-04",
            model={"locality": "cloud", "model_id": "acme-large", "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=5,
        spec_case="Denied.reason = whole_document_requested",
        policy=_policy("local_model"),
        classification=_classified(3, "public_low", protected=False),
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(Excerpt(observation_key=_key(3),
                                        span=TextSpan(0, _unit_length(3)),
                                        reason="read the page"),),
                         fingerprint="fp-05", max_dossier_tokens=20000),
        decision=_denied(
            "whole_document_requested",
            "the requested span covers the whole text unit. §8.4: the engine 'should "
            "not send full documents where a short heading or OCR excerpt is enough "
            "to resolve the question.'",
            "request the heading or the anchor excerpt instead",
            "split the task across bounded excerpts",
            evidence_refs=(_key(3),)),
        audit_record=_audit(outcome="denied", operation_mode="local_model",
                            file_sensitivity="public_low", content_hash=_hash(3),
                            content_hashes=(_hash(3),), prompt_fingerprint="fp-05"),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=6,
        spec_case="Denied.reason = dossier_over_budget (M9's backstop)",
        policy=_policy("local_model"),
        classification=_classified(3, "public_low", protected=False),
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(Excerpt(observation_key=_key(3),
                                        span=TextSpan(12043, 12051),
                                        reason="resolve the institution"),),
                         fingerprint="fp-06", max_dossier_tokens=1),
        decision=_denied(
            "dossier_over_budget",
            "the resolved dossier exceeds the `max_dossier_tokens` the caller is "
            "operating under. This is a backstop: §8.6's ladder -- 'summarize "
            "deterministic facts, preserve anchor excerpts, split the task, or defer "
            "the decision' -- runs in P8 before the call (M9).",
            "run §8.6's reduction ladder and call again",
            "defer the decision",
            evidence_refs=(_key(3),)),
        audit_record=_audit(outcome="denied", operation_mode="local_model",
                            file_sensitivity="public_low", content_hash=_hash(3),
                            content_hashes=(_hash(3),), prompt_fingerprint="fp-06"),
        p4_fixture=3,
        downstream_obligation=(
            "so P8 can prove its ladder ran first -- a P8 test that reaches this "
            "denial through the normal path is a P8 failure, not a gate result"),
        revoked=False),
    GateFixture(
        number=7,
        spec_case="Denied.reason = always_local_item (an excerpt resolving to OCR)",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(8, "public_low", protected=False),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(8),
                                        span=TextSpan(0, 24),
                                        reason="read the status banner"),),
                         fingerprint="fp-07", max_dossier_tokens=2000),
        decision=_denied(
            "always_local_item",
            "the excerpt resolves to OCR output, which §8.4 places in the always-local "
            "set: 'Paths, complete extracted text, OCR output, file hashes, image "
            "EXIF, GPS, user edits, group memberships, and raw sensitive values should "
            "remain local.'",
            "use the deterministic facts derived from the OCR text",
            "ask the user to review the screenshot locally",
            evidence_refs=(_key(8),)),
        audit_record=_audit(outcome="denied", operation_mode="cloud_assisted",
                            file_sensitivity="public_low", content_hash=_hash(8),
                            content_hashes=(_hash(8),), prompt_fingerprint="fp-07",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=8, downstream_obligation=None, revoked=False),
    GateFixture(
        number=8,
        spec_case="Denied.reason = mode_forbids_target (the mode axis, unprotected)",
        policy=_policy("offline"),
        classification=_classified(3, "public_low", protected=False),
        area=None,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(CandidateLabel(label="Columbia"),),
                         fingerprint="fp-08", max_dossier_tokens=2000),
        decision=_denied(
            "mode_forbids_target",
            "§8.4's fully offline mode: 'No content leaves the device; only local "
            "rules and local models may run.' The file is neither sensitive nor "
            "protected; the mode alone forbids the target.",
            "run the same request against a local model",
            "change the operation mode explicitly"),
        audit_record=_audit(outcome="denied", operation_mode="offline",
                            file_sensitivity="public_low", content_hash=_hash(3),
                            content_hashes=(_hash(3),), prompt_fingerprint="fp-08",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=9,
        spec_case="a clean `Released` with redaction applied",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "personal_non_sensitive", protected=False),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(3),
                                        span=TextSpan(12043, 12051),
                                        reason="resolve the institution"),
                                RedactedIdentifier(observation_key=_key(3),
                                                   span=TextSpan(12043, 12051),
                                                   identifier_class="institution"),
                                EvidenceReference(observation_key=_key(3))),
                         fingerprint="fp-09", max_dossier_tokens=2000),
        decision=Released(
            release_id="release-fixture-09", audit_id=None,
            policy_version="policy-1",
            materialised_items=("Columbia", "[institution]"),
            redaction_manifest=(
                RedactionEntry(observation_key=_key(3), span="12043-12051",
                               identifier_class="institution", redacted=True),),
            model_target=CLOUD_MODEL),
        audit_record=_audit(
            outcome="released", operation_mode="cloud_assisted",
            file_sensitivity="personal_non_sensitive", content_hash=_hash(3),
            content_hashes=(_hash(3),), prompt_fingerprint="fp-09",
            excerpts_included=((_key(3), "12043-12051"),),
            redaction_applied=True,
            redaction_manifest=((_key(3), "12043-12051", "institution", True),),
            model={"locality": "cloud", "model_id": "acme-large", "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=10,
        spec_case="a `NeedsConsent` returning all four options",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        # `sensitive_personal` and NOT protected. Open question 1 -- "Is `protected`
        # exactly the top two handling classes?" -- is unsettled, and SPEC §2 says
        # outright: "Neighbouring parts should consume the `protected` flag, not infer
        # it from the class." This fixture is where that stays true: a gate that
        # inferred `protected` from the class would deny here and §8.4's consent
        # branch would be unreachable.
        classification=_classified(3, "sensitive_personal", protected=False),
        area=FIXTURE_AREA,
        request=_request(stage="fact_resolution", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(3),
                                        span=TextSpan(12043, 12051),
                                        reason="the sensitive passage names the "
                                               "institution"),),
                         fingerprint="fp-10", max_dossier_tokens=2000),
        decision=NeedsConsent(
            consent_request_id=None,
            requirement=ConsentRequirement(
                items=(_key(3),),
                why="the requested excerpt is text from a file classified "
                    "`sensitive_personal`"),
            options=CONSENT_OPTIONS),
        audit_record=_audit(
            outcome="consent_requested", operation_mode="cloud_assisted",
            file_sensitivity="sensitive_personal", content_hash=_hash(3),
            content_hashes=(_hash(3),), prompt_fingerprint="fp-10",
            model={"locality": "cloud", "model_id": "acme-large", "provider": "Acme"}),
        p4_fixture=3,
        downstream_obligation=(
            "so P8 can prove it returns the branch to its caller intact"),
        revoked=False),
    GateFixture(
        number=11,
        spec_case="a protected file under `offline`",
        policy=_policy("offline"),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=None,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-11", max_dossier_tokens=2000),
        decision=_denied(
            "mode_forbids_target",
            "§8.4's fully offline mode: 'No content leaves the device; only local "
            "rules and local models may run.' The mode is evaluated first, because "
            "under `offline` this target is unreachable for every file and naming the "
            "file's protection would be a narrower reason than the true one.",
            "run the same request against a local model",
            "change the operation mode explicitly"),
        audit_record=_audit(outcome="denied", operation_mode="offline",
                            file_sensitivity="sensitive_personal",
                            content_hash=_hash(3), content_hashes=(_hash(3),),
                            prompt_fingerprint="fp-11",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=12,
        spec_case="a protected file under `local_model`",
        policy=_policy("local_model"),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=None,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-12", max_dossier_tokens=2000),
        decision=_denied(
            "mode_forbids_target",
            "§8.4's local-model mode: 'Local extraction plus a user-installed local "
            "LLM for eligible dossiers.' No cloud target is reachable under it.",
            "run the same request against the local model",
            "change the operation mode explicitly"),
        audit_record=_audit(outcome="denied", operation_mode="local_model",
                            file_sensitivity="sensitive_personal",
                            content_hash=_hash(3), content_hashes=(_hash(3),),
                            prompt_fingerprint="fp-12",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=13,
        spec_case="a protected file under `hybrid` (a metadata field, not an excerpt)",
        policy=_policy("hybrid", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-13", max_dossier_tokens=2000),
        decision=_denied(
            "protected_cloud_target",
            "§8.4: 'Protected material should not be included in cloud-model prompts "
            "by default.' The sentence names no item kind, so an innocuous metadata "
            "field is refused on the same ground as an excerpt.",
            "run the same request against a local model",
            "ask the user for a policy that explicitly permits it"),
        audit_record=_audit(outcome="denied", operation_mode="hybrid",
                            file_sensitivity="sensitive_personal",
                            content_hash=_hash(3), content_hashes=(_hash(3),),
                            prompt_fingerprint="fp-13",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=14,
        spec_case="a protected file under `cloud_assisted`, with no grant for the area",
        policy=_policy("cloud_assisted"),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-14", max_dossier_tokens=2000),
        decision=_denied(
            "protected_cloud_target",
            "§8.4's cloud-assisted mode: 'User explicitly permits selected corpus "
            "areas to use a cloud model.' No grant covers this area, and the material "
            "is protected.",
            "ask the user for a consent grant covering this area",
            "run the same request against a local model"),
        audit_record=_audit(outcome="denied", operation_mode="cloud_assisted",
                            file_sensitivity="sensitive_personal",
                            content_hash=_hash(3), content_hashes=(_hash(3),),
                            prompt_fingerprint="fp-14",
                            model={"locality": "cloud", "model_id": "acme-large",
                                   "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=15,
        spec_case="an `unreadable_unclassified` file (something looked and failed)",
        policy=_policy("local_model"),
        classification=_classified(18, "unreadable_unclassified", protected=False,
                                   basis="detector", reliability_state="direct"),
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-15", max_dossier_tokens=2000),
        decision=_denied(
            "unclassified",
            "the extraction is §2.9's indexed-but-unreadable case and the handling "
            "class is `unreadable_unclassified`. §8.4 makes classification a "
            "precondition of escalation, and §8.6 forbids the alternative: 'Cost "
            "exhaustion must never turn into lower-quality automatic classification.'",
            "show the file as unprocessed rather than unimportant",
            "ask the user to classify it"),
        audit_record=_audit(outcome="denied", operation_mode="local_model",
                            file_sensitivity="unreadable_unclassified",
                            content_hash=_hash(18), content_hashes=(_hash(18),),
                            prompt_fingerprint="fp-15"),
        p4_fixture=18, downstream_obligation=None, revoked=False),
    GateFixture(
        number=16,
        spec_case="a `Protected Records` residual request (the filename half)",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "highly_sensitive_credential_bearing",
                                   protected=True, basis="safety_domain"),
        area=FIXTURE_AREA,
        request=_request(stage="placement", model_target=CLOUD_MODEL,
                         items=(Filename(file_id="fixture-file"),),
                         fingerprint="fp-16", max_dossier_tokens=2000),
        decision=_denied(
            "protected_records_template",
            f"the file is held under the {PROTECTED_RECORDS_TEMPLATE} residual "
            "template. §7.3 forbids both nouns: it 'must not cause filenames or "
            "content to be exposed in model prompts'.",
            "place the file from local deterministic facts",
            "surface the residual area to the user without naming the file"),
        audit_record=_audit(
            outcome="denied", operation_mode="cloud_assisted",
            file_sensitivity="highly_sensitive_credential_bearing",
            content_hash=_hash(3), content_hashes=(_hash(3),),
            prompt_fingerprint="fp-16",
            model={"locality": "cloud", "model_id": "acme-large", "provider": "Acme"}),
        p4_fixture=3, downstream_obligation=None, revoked=False),
)


#: SPEC §11's list, mapped to the fixtures that satisfy it. Thirteen keys: the eight
#: `Denied.reason` values and the five `SPEC_11_ITEMS`. A key with an empty tuple is a
#: §11 item with no fixture, which is the failure this map exists to make visible.
FIXTURE_COVERAGE: Mapping[str, tuple[int, ...]] = MappingProxyType({
    "protected_cloud_target": (1, 13, 14),
    "unclassified": (2, 15),
    "policy_revoked": (3,),
    "protected_records_template": (4, 16),
    "whole_document_requested": (5,),
    "dossier_over_budget": (6,),
    "always_local_item": (7,),
    "mode_forbids_target": (8, 11, 12),
    "a clean `Released` with redaction applied": (9,),
    "a `NeedsConsent` returning all four options": (10,),
    "a protected file under each of the four modes": (11, 12, 13, 14),
    "an `unreadable_unclassified` file": (15,),
    "a `Protected Records` residual request": (16,),
})

#: The four-mode sweep, mode -> fixture number. `offline` and `local_model` deny on the
#: mode; `hybrid` and `cloud_assisted` deny on the protection. That difference is the
#: precedence rule, published as data so Task 13 cannot quietly invert it.
MODE_SWEEP: Mapping[str, int] = MappingProxyType({
    "offline": 11,
    "local_model": 12,
    "hybrid": 13,
    "cloud_assisted": 14,
})

_BY_NUMBER: Mapping[int, GateFixture] = MappingProxyType(
    {fixture.number: fixture for fixture in FIXTURES})


def by_number(number: int) -> GateFixture:
    """The fixture with this number, or `UnknownFixture`. Never a nearest neighbour."""
    try:
        return _BY_NUMBER[number]
    except KeyError:
        raise UnknownFixture(
            f"P7 publishes no gate fixture {number}; the published numbers are "
            f"{tuple(sorted(_BY_NUMBER))}") from None
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_fixtures.py -v`
Expected: PASS — 68 passed (24 unparameterised tests plus three parameterisations over the
sixteen fixtures)

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–20 green, and the 1302 P1–P5 tests still green (P7 modified no file
belonging to another part).

- [ ] **Step 6: Commit**

```bash
git add src/privacy/fixtures.py tests/p7/test_p7_fixtures.py
git commit -m "feat(P7): SPEC 11's sixteen published fixtures, each replayed through the real gate"
```

---

---

### Task 21: The no-invention guard, and every open question held open

**Files:**
- Modify: `src/privacy/vocabulary.py` (add `HELD_OPEN` — see below)
- Test: `tests/p7/test_p7_no_invention.py`

**Interfaces:**
- Consumes: every module under `src/privacy/`, by `importlib` + `vars(module)`; `ast` over the same
  files for the assertions introspection cannot make; `database_agent.files_table.FILES_COLUMNS`,
  `.set_sensitivity_state`, `.get_file`, `.record_file`; `privacy.classification.ClassificationRecord`;
  `privacy.classification_store.ClassificationStore`, `.mirror_state`;
  `privacy.learning_seam.assign`; `evidence_shape.text_units.raw_value_at`;
  `evidence_shape.store.text_units_for_run`, `.text_unit_at`, `.unit_for_observation`.
- Produces (`vocabulary.py`): `HELD_OPEN: Mapping[str, str]` — the three questions held open that are
  **not** among the SPEC's eleven. `OPEN_QUESTIONS` (the eleven) is Task 2's and is asserted here.

**Done-means:** the guard behind 1, 12, and the whole *Deferred* table.

**One guard INVERTS, and it is the reason this task cannot be written from the skeleton alone.**
The skeleton's §5 says *"Every open question stays open … Each is held by a guard in Task 21 that
names it and fails the moment someone answers it"*, and its §4 says the opposite about one of them:
**P6 OQ11 is CLOSED (D2).** A guard asserting OQ11 is open **fails on the day this plan is
executed**, because that is the day D2 is applied. Task 21 asserts the **D2 shape** instead, in four
clauses, each of which is a separate test:

1. `ClassificationRecord` keyed `(file_id, content_hash)` is **authoritative** — the store resolves
   one current record per pair, and a new content hash inherits nothing.
2. `files.sensitivity_state` is a **projection**, written through P1's published
   `set_sensitivity_state`. P7 takes no writer protocol; P1 publishes the setter and P7 calls it.
3. `src/privacy/` issues **no `UPDATE files`** of its own — asserted over the AST's string literals,
   so a docstring explaining the rule cannot satisfy it and cannot break it.
4. **`unclassified` never reaches that column.** It is a gate outcome, not a file fact. Storing it
   would make *"nothing has looked"* indistinguishable from *"this file carries nothing"*, which is
   the distinction D2's third clause exists to protect and Task 20's fixtures 2 and 15 exist to
   demonstrate.

**Two things are genuinely open and are held open BY NAME, because a question nobody names is a
question that gets answered by accident.**

- **`filename` as a sixth releasable kind.** §8.4 names **five** — *"selected excerpts, redacted
  identifiers, candidate labels, non-sensitive metadata, and evidence references"* — and puts
  *paths* in the always-local set. P7's SPEC adds a sixth and **flags it itself**: *"This is the one
  place where the contract resolves an apparent conflict rather than deferring it, because P8 and
  P11 cannot build without an answer."* It is SPEC Open question 2, and it is Joseph's call, routed
  as NEEDS-JOSEPH **B5d** (*"`filename` as a releasable kind — the one P7 open question its own plan
  left off its list. §8.4's releasable list is five and does not name it"*) and **C9a**
  (*"Recorded; the design wins. The SPEC flags it itself. **Your call.**"*). The guard asserts the
  sixth kind exists, that the SPEC's own flag text is carried beside it, and that **nothing in
  `src/privacy/` treats the conflict as settled** — no module holds a resolution constant, and the
  `Filename` item is denied for protected files exactly as §7.3 requires, which is the narrow part
  the design does settle.
- **Whether P6 keeps a `sensitivity status` field row at all.** P7's SPEC Contract-in says
  *"**P6 must accept `sensitivity` as a first-class universal field** (§3.11) rather than a
  domain-scoped one"* while D2 makes P7's own record authoritative. The skeleton states the residue
  precisely: *"whether P6 keeps a `sensitivity status` row among §3.11's universal fields at all.
  Round 1's F-2 already found that field has no producer. D2 decided which record is AUTHORITATIVE;
  it did not decide whether a second, P6-owned field row continues to exist beside it. Until that is
  answered, P6 should create no such row and P7 should not read one."* **Do not resolve it.** The
  guard asserts `src/privacy/` reads no P6 surface, holds no `file_facts` table name, and names all
  three spellings — `sensitivity` (P7 SPEC), `sensitivity status` (§3.11, P6), `sensitivity_state`
  (P1's column) — as distinct.

**And a third, which is P4's and reaches P7 through redaction.** `Region` is
`{ x, y, w, h, unit }` with `unit ∈ {px, norm}` and **no document in this repository says which
corner the origin is**. `evidence_shape.vocabulary.OPEN_QUESTIONS` carries one entry, OQ4, and it is
not this one; the design says only *"locations or bounding boxes where available"* (§2.7). P7's
redaction and resolution both touch `Location.region`, so a guard that P7 never assumes an origin is
cheap now and unbuildable after someone has written `y = height - y` somewhere. The guard asserts
`src/privacy/` performs **no arithmetic on a region field at all** and holds no origin token.

**`src/privacy/` imports none of `extractors`' refusals, and that list is now THREE names.** The
skeleton's §1 says *"never imports `ProtectedContainerRefused` or `DatalessRefused`"* and stops at
two. `extractors.failure.ContractViolation` is the third and it is live —
`src/orchestrator.py` imports all three side by side. The three refusals in this product are three,
and P7 owns only the last of them: reading is refused by P3/P5, materialising is refused by P3/P5,
and **release** is refused by P7. A file that failed either of the first two never acquires the
`(file_id, content_hash)` pair P7 keys on, so re-deriving the verdict is not merely redundant, it is
unconstructible. Reported as a correction from two names to three.

**Two corrections to the L2 guard, found by running it against the live repository rather than by
reading the skeleton.** The skeleton says the set of packages binding a P4 text materialiser is
*"`{evidence_shape, extractors, privacy}` and nothing else"*. Introspected 2026-08-22, the live set
is **`{evidence_shape, orchestrator}`**:

- **`extractors` binds none of the four.** P5 emits observations and text units; it never reads one
  back. The skeleton's set would have been wrong in the permissive direction — it licenses a package
  that does not need the licence.
- **`orchestrator` binds `text_units_for_run`**, at `src/orchestrator.py`, to copy units into P2's
  replay bundle. That is a **local** copy, not an egress — but whether a bundle may carry excerpt
  text is **P7's own Open question 8**, unanswered, so this guard **records the binder and its reason
  and does not rule on it**. Writing the guard to exclude `orchestrator` by calling it "not a
  package" would be hiding a real binder behind a technicality.

The guard is therefore written over **every module under `src/`**, with an allowlist of three
top-level names and a published reason for each. It passes trivially today and becomes load-bearing
the moment P8 lands, which is why it is written now rather than by someone who wants it to pass.

**Everything else is runtime introspection, and where it cannot be, it is the AST.** The skeleton is
emphatic and it is right: *"a source-text guard matches comments and docstrings, which is a failure
this repository has already recorded more than once."* `tests/p3/test_p3_no_invention.py` documents
the case where it broke the other way — a comment explaining why a value is absent failed the test
asserting the value is absent. This task reimplements `code_tokens()` over `src/privacy/` rather
than importing it, because `tests/` has no `__init__.py` and a cross-directory import there would
collide on module basenames the way `conftest.py` already has twice on this project.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_no_invention.py
"""P7 answers no open question in code, and D2's shape holds.

Two techniques and one rule. The rule: an assertion of the form "this token appears
nowhere" is made against the AST, never against `read_text()`, because a comment or a
docstring EXPLAINING why a value is absent matches a text scan for that value. That
failure is recorded in `tests/p3/test_p3_no_invention.py`, which is where
`code_tokens()` comes from and why it exists.

The technique for everything else is `vars(module)`: what a module BINDS is what it
holds, and a number inside a docstring is prose.
"""
import ast
import importlib
import json
import pathlib

import pytest

import privacy
from database_agent.files_table import FILES_COLUMNS, get_file, record_file

from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore, mirror_state
from privacy.learning_seam import assign, reclassify
from privacy.vocabulary import HELD_OPEN, OPEN_QUESTIONS

COMPONENT = "0.1.0"
FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
SOURCE_DIR = pathlib.Path(privacy.__file__).parent
SRC_ROOT = pathlib.Path(privacy.__file__).parent.parent

#: Module-level names permitted to be bound to a number. It is EMPTY, and adding a
#: name to it is a P7 contract revision rather than an implementation decision:
#: SPEC *Deferred* puts "Numeric values for every ceiling" outside this contract --
#: §8.6 "names the knobs, states they are 'configurable', and gives no values".
NUMERIC_ALLOWLIST: frozenset[str] = frozenset()

#: Top-level names permitted to bind a P4 text materialiser, each with its reason.
#: Introspected against the live repository, not copied from the plan skeleton, which
#: named `extractors` (which binds none) and omitted `orchestrator` (which binds one).
MATERIALISER_BINDERS = {
    "evidence_shape": "P4 owns them",
    "privacy": "L2 -- `resolve.py` is the ONE place a (key, span) becomes text",
    "orchestrator": (
        "copies text units into P2's replay bundle (§8.5). A local copy, not an "
        "egress -- and whether a bundle may carry excerpt text is P7 Open question 8, "
        "unanswered, so this guard records it and does not rule on it"),
}

MATERIALISERS = ("raw_value_at", "text_units_for_run", "text_unit_at",
                 "unit_for_observation")


def modules():
    return sorted(SOURCE_DIR.glob("*.py"))


def imported():
    """Every module under `src/privacy/`, imported, for namespace introspection."""
    found = []
    for path in modules():
        name = path.stem
        if name == "__init__":
            found.append(privacy)
            continue
        found.append(importlib.import_module(f"privacy.{name}"))
    return found


def _docstrings(tree: ast.AST) -> set[int]:
    """The id() of every node that is a docstring, so it can be skipped."""
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                found.add(id(body[0].value))
    return found


def code_strings(path: pathlib.Path) -> set[str]:
    """String and numeric literals P7's code USES, docstrings excluded."""
    tree = ast.parse(path.read_text(), filename=str(path))
    skip = _docstrings(tree)
    tokens: set[str] = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and id(node) not in skip
                and isinstance(node.value, (str, int, float))
                and not isinstance(node.value, bool)):
            tokens.add(str(node.value))
    return tokens


def code_names(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    tokens: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            tokens.add(node.id)
        elif isinstance(node, ast.Attribute):
            tokens.add(node.attr)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            tokens.add(node.name)
        elif isinstance(node, ast.arg):
            tokens.add(node.arg)
        elif isinstance(node, ast.keyword) and node.arg:
            tokens.add(node.arg)
        elif isinstance(node, ast.alias):
            tokens.add(node.name)
            if node.asname:
                tokens.add(node.asname)
    return tokens


def code_tokens(path: pathlib.Path) -> set[str]:
    return code_names(path) | code_strings(path)


def imports_of(path: pathlib.Path) -> set[str]:
    """Every dotted name this module imports, from the AST rather than from text."""
    tree = ast.parse(path.read_text(), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            found.add(module)
            found.update(f"{module}.{alias.name}" for alias in node.names)
            found.update(alias.name for alias in node.names)
    return found


def module_numbers(module):
    return {name: value for name, value in vars(module).items()
            if not name.startswith("_")
            and isinstance(value, (int, float)) and not isinstance(value, bool)}


# --- the eleven, present with the SPEC's own text ---------------------------

def test_all_eleven_spec_open_questions_are_present():
    assert set(OPEN_QUESTIONS) == set(range(1, 12))
    for number, text in OPEN_QUESTIONS.items():
        assert text.strip(), number


def test_open_question_11_names_no_winner_between_the_two_local_modes():
    # W1 narrowed it and did not close it: "What remains genuinely open is only WHICH
    # of those two ships, which turns on whether a local model is assumed present."
    from privacy.defaults import LOCAL_FIRST_MODES
    assert set(LOCAL_FIRST_MODES) == {"offline", "local_model"}
    for module in imported():
        for name, value in vars(module).items():
            if name.startswith("_") or not isinstance(value, str):
                continue
            assert value not in ("offline", "local_model"), (module.__name__, name)


def test_no_module_holds_a_bare_hybrid_or_cloud_assisted_default():
    # Done-means 12's negative half, by introspection rather than by grep: both names
    # appear legitimately inside `OPERATION_MODES`, inside `MODE_SEMANTICS`, inside
    # denial messages and inside fixture records, so a text scan either passes
    # vacuously or fails on a comment.
    for module in imported():
        for name, value in vars(module).items():
            if name.startswith("_") or not isinstance(value, str):
                continue
            assert value not in ("hybrid", "cloud_assisted"), (module.__name__, name)


def test_open_question_3_defines_no_corpus_area():
    # "What is a 'corpus area'? ... Consent grants cannot be scoped until this is
    # named." The gate takes an `scope_for` resolver with no default; the only area
    # STRING in the package is the fixture module's single example.
    import inspect
    from privacy.gate import Gate
    parameters = inspect.signature(Gate.__init__).parameters
    assert "scope_for" in parameters
    assert parameters["scope_for"].default is inspect.Parameter.empty
    holders = [m.__name__ for m in imported()
               if any(name.upper().endswith("AREA") or name.upper().endswith("AREAS")
                      for name in vars(m) if not name.startswith("_"))]
    assert holders == ["privacy.fixtures"]
    from privacy.fixtures import FIXTURE_AREA
    assert isinstance(FIXTURE_AREA, str)


def test_open_question_1_never_infers_protected_from_the_handling_class():
    # SPEC §2: "Neighbouring parts should consume the `protected` flag, not infer it
    # from the class." Fixture 10 is where that stays true -- a `sensitive_personal`
    # file that is NOT protected, which is the input §8.4's consent branch needs.
    from privacy.fixtures import by_number
    fixture = by_number(10)
    assert fixture.classification.handling_class == "sensitive_personal"
    assert fixture.classification.protected is False
    record = ClassificationRecord(
        file_id="f", content_hash="sha256:abc", handling_class="public_low",
        protected=True, basis="user", evidence_refs=(),
        reliability_state="user_confirmed", observed_at=FIXED_CLOCK)
    assert record.protected is True


def test_open_question_7_counts_no_repetitions():
    # "Does repeated reclassification generalize?" Nothing counts, so nothing widens.
    for module in imported():
        assert not module_numbers(module) - set(NUMERIC_ALLOWLIST), module.__name__


def test_open_question_10_states_no_retention_period():
    # "How long audit records, consent grants, and superseded classifications are
    # kept. The design states no retention period anywhere."
    for module in imported():
        for name in vars(module):
            upper = name.upper()
            for token in ("RETENTION", "TTL", "EXPIR", "MAX_AGE", "PURGE", "DAYS"):
                assert token not in upper, (module.__name__, name)


# --- the three held open that are not among the eleven ----------------------

def test_held_open_names_exactly_three_and_each_carries_its_source():
    # Three again, but not the same three: D7 and D10 closed two, and the
    # `filename` sixth kind and the five kept round-5 cuts took their places.
    assert set(HELD_OPEN) == {"I6", "filename-sixth-releasable-kind", "round-5-cuts"}
    for key, text in HELD_OPEN.items():
        assert text.strip(), key


def test_i6_is_held_by_delete_derived_refusing_and_not_by_a_sentence():
    from privacy.revocation import DerivedScope, UnratifiedResolution, delete_derived
    with pytest.raises(UnratifiedResolution) as caught:
        delete_derived(DerivedScope("text_units", "text"))
    assert "I6" in str(caught.value)


def test_p7s_classification_record_is_the_sole_home_d7():
    # RULED. D2 made P7's own record authoritative; **D7** then closed the question
    # behind it -- P6 creates no `sensitivity_status` row at all, so P7's Contract-in
    # from P6 is empty. This asserted the question was OPEN; it now asserts the ruled
    # outcome, which is the stronger of the two and needs no change to the body.
    for path in modules():
        tokens = code_tokens(path)
        for forbidden in ("file_facts", "fact_id", "field_key", "value_id"):
            assert forbidden not in tokens, (path.name, forbidden)
        assert not [name for name in imports_of(path) if name.startswith("facts")]


def test_the_three_spellings_of_sensitivity_stay_three():
    # `sensitivity` (P7 SPEC), `sensitivity status` (§3.11, P6), `sensitivity_state`
    # (P1's column). C8 calls this "the defect class that has cost this project the
    # most, at the largest scale it has appeared." Three names, one concept, and no
    # code that treats any two as one.
    assert "sensitivity_state" in FILES_COLUMNS
    from privacy.classification import CLASSIFICATION_FIELDS
    assert "handling_class" in CLASSIFICATION_FIELDS
    assert "sensitivity" not in CLASSIFICATION_FIELDS
    assert "sensitivity_state" not in CLASSIFICATION_FIELDS


def test_the_filename_sixth_kind_is_flagged_and_not_treated_as_settled():
    # §8.4's releasable list is FIVE -- "selected excerpts, redacted identifiers,
    # candidate labels, non-sensitive metadata, and evidence references" -- and puts
    # paths in the always-local set. The SPEC adds a sixth and flags it (Open question
    # 2, NEEDS-JOSEPH B5d / C9a). It is Joseph's call and nothing here decides it.
    from privacy.items import Filename
    from privacy.vocabulary import ITEM_KINDS
    assert ITEM_KINDS[-1] == "filename"
    assert len(ITEM_KINDS) == 6
    assert "filename" in OPEN_QUESTIONS[2].lower() or "Filename" in OPEN_QUESTIONS[2]
    assert {f.name for f in __import__("dataclasses").fields(Filename)} == {"file_id"}
    for path in modules():
        tokens = code_tokens(path)
        for settled in ("filename_resolved", "filename_settled",
                        "FILENAME_IS_NOT_A_PATH"):
            assert settled not in tokens, path.name


def test_a_normalized_bounding_box_is_measured_from_the_top_left_d10():
    # RULED. This test used to forbid P7 from doing ANY arithmetic on a region field,
    # because no document said which corner `norm` measured from and P7 is the part
    # that would otherwise have answered it by accident. **D10** answered it: `norm`
    # means TOP-LEFT, and `readers.ocr_vision._box` converts Vision's bottom-left
    # rectangles at the adapter (commit 87016b0). Redaction may now rely on it.
    #
    # The guard inverts rather than disappearing. P4's shape is still five keys with
    # no origin field, so the convention lives in exactly one place and P7 must not
    # re-declare it: P7 holds no origin token of its own, and the one place the flip
    # happens stays outside this part.
    from evidence_shape.location import Region
    region_fields = {f.name for f in __import__("dataclasses").fields(Region)}
    assert region_fields == {"x", "y", "w", "h", "unit"}, (
        "D10 was closed at the adapter precisely so P4's shape would not move")

    import inspect as _inspect

    import readers.ocr_vision as _vision
    assert "1.0 - (" in _inspect.getsource(_vision._box), (
        "the top-left flip lives in the Vision adapter; if it moved, P7's redaction "
        "is reading a convention nothing enforces")

    for path in modules():
        tokens = code_tokens(path)
        for origin in ("top_left", "bottom_left", "top-left", "bottom-left"):
            assert origin not in tokens, (path.name, origin)


# --- D2's shape, which is what replaced the OQ11 guard -----------------------

def test_the_classification_record_is_keyed_on_file_id_and_content_hash(
        p7_conn, tmp_path):
    # D2 clause 1: "Keyed on the hash because a classification is about BYTES; new
    # bytes at a path are a new file version and inherit nothing."
    store = ClassificationStore(p7_conn)
    document = tmp_path / "doc.pdf"
    document.write_bytes(b"%PDF-1.4 one")
    file_id = record_file(
        p7_conn, document, filename="doc.pdf", normalized_filename="doc.pdf",
        extension=".pdf", observed_size=document.stat().st_size,
        observed_timestamps='{"mtime": 1.0}', parent_folder_context=str(tmp_path),
        mime_type="application/pdf", detected_format="pdf",
        scan_state="fixture-scan-state", materialized=True)
    first = ClassificationRecord(
        file_id=file_id, content_hash=get_file(p7_conn, file_id)["content_hash"],
        handling_class="sensitive_personal", protected=True, basis="user",
        evidence_refs=(), reliability_state="user_confirmed", observed_at=FIXED_CLOCK)
    store.write(first)
    assert store.current(file_id, first.content_hash) == first
    assert store.current(file_id, "sha256:different-bytes") is None


def test_the_column_is_written_only_through_p1s_published_setter():
    # D2 clause 2, and the reason there is no `SensitivityStateWriter`: P1 publishes
    # `set_sensitivity_state`, the twin of `set_extraction_status`. A protocol
    # wrapping a function that exists is a second write path to a column that spent
    # the whole project with none.
    binders = [m.__name__ for m in imported()
               if "set_sensitivity_state" in vars(m)]
    assert binders == ["privacy.learning_seam"]
    for module in imported():
        for name in vars(module):
            assert "SensitivityStateWriter" not in name, module.__name__


def test_src_privacy_issues_no_update_files_of_its_own():
    # D2 clause 2's negative half. Over the AST's string literals, so a docstring
    # explaining the rule neither satisfies it nor breaks it.
    for path in modules():
        for literal in code_strings(path):
            collapsed = " ".join(literal.lower().split())
            assert "update files" not in collapsed, (path.name, literal[:60])
            assert "insert into files" not in collapsed, (path.name, literal[:60])
            assert "delete from files" not in collapsed, (path.name, literal[:60])


def test_unclassified_never_reaches_the_projection_column(p7_conn, tmp_path):
    # D2 clause 3: "`Unreadable or unclassified` is a GATE OUTCOME, not a file fact.
    # It lives on the release decision and never in that column, so 'nothing has
    # looked' can never be read as 'this file carries nothing'."
    store = ClassificationStore(p7_conn)
    document = tmp_path / "opaque.psd"
    document.write_bytes(b"8BPS fixture bytes")
    file_id = record_file(
        p7_conn, document, filename="opaque.psd", normalized_filename="opaque.psd",
        extension=".psd", observed_size=document.stat().st_size,
        observed_timestamps='{"mtime": 1.0}', parent_folder_context=str(tmp_path),
        mime_type="image/vnd.adobe.photoshop", detected_format="psd",
        scan_state="fixture-scan-state", materialized=True)
    content_hash = get_file(p7_conn, file_id)["content_hash"]
    record = ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="unreadable_unclassified", protected=False, basis="detector",
        evidence_refs=("sha256:" + "0" * 64,), reliability_state="direct",
        observed_at=FIXED_CLOCK)
    assign(p7_conn, record, store=store, component_version=COMPONENT)
    stored = get_file(p7_conn, file_id)["sensitivity_state"]
    assert stored is not None
    assert "unclassified" not in json.dumps(json.loads(stored))


def test_the_projection_is_not_the_authoritative_record():
    # `mirror_state` is a PROJECTION: it drops what the column cannot answer. A mirror
    # that carried every field would invite a reader to treat the column as the
    # record, which is the shape D2 replaced.
    record = ClassificationRecord(
        file_id="f", content_hash="sha256:abc", handling_class="public_low",
        protected=False, basis="detector", evidence_refs=("sha256:x",),
        reliability_state="validated", observed_at=FIXED_CLOCK)
    state = mirror_state(record)
    assert set(state) < {f for f in vars(record)} | set(state)
    assert "file_id" not in state


# --- the three refusals stay three ------------------------------------------

def test_src_privacy_imports_none_of_extractors_three_refusals():
    # Reading is refused by P3/P5 (`ProtectedContainerRefused`); materializing is
    # refused by P3/P5 (`DatalessRefused`); a malformed extraction is refused by P5
    # (`ContractViolation`). RELEASE is P7's, and only release has a consent branch.
    # A file that failed either of the first two never acquires the
    # `(file_id, content_hash)` pair P7 keys on, so re-deriving is unconstructible.
    refusals = ("ProtectedContainerRefused", "DatalessRefused", "ContractViolation")
    for path in modules():
        names = imports_of(path)
        for refusal in refusals:
            assert refusal not in names, (path.name, refusal)
            assert f"extractors.safety.{refusal}" not in names, path.name
        assert "extractors.safety" not in names, path.name
        assert "admit" not in names, path.name


def test_the_orchestrator_imports_all_three_so_the_list_is_three_and_not_two():
    # The plan skeleton names two. The live caller names three, side by side, which is
    # how the omission was found.
    orchestrator = importlib.import_module("orchestrator")
    for refusal in ("ProtectedContainerRefused", "DatalessRefused",
                    "ContractViolation"):
        assert refusal in vars(orchestrator), refusal


# --- L2: one materialisation locus, repo-wide -------------------------------

def test_only_one_module_under_src_privacy_binds_a_p4_text_materialiser():
    binders = [m.__name__ for m in imported()
               if any(name in vars(m) for name in MATERIALISERS)]
    assert binders == ["privacy.resolve"]


def test_the_repo_wide_set_of_materialiser_binders_is_the_named_three():
    # Layer L2 of Done-means 3. This passes trivially today and becomes load-bearing
    # the moment P8 lands, which is why it is written now rather than later by someone
    # who wants it to pass.
    from evidence_shape import store as p4_store
    from evidence_shape import text_units as p4_text
    targets = {p4_text.raw_value_at, p4_store.text_units_for_run,
               p4_store.text_unit_at, p4_store.unit_for_observation}
    found: set[str] = set()
    for path in sorted(SRC_ROOT.rglob("*.py")):
        dotted = str(path.relative_to(SRC_ROOT).with_suffix("")).replace("/", ".")
        dotted = dotted[:-9] if dotted.endswith(".__init__") else dotted
        module = importlib.import_module(dotted)
        if any(value in targets for value in vars(module).values()):
            found.add(dotted.split(".")[0])
    assert found == set(MATERIALISER_BINDERS), sorted(found)
    for binder, reason in MATERIALISER_BINDERS.items():
        assert reason.strip(), binder


# --- P7 invents nothing -----------------------------------------------------

def test_no_module_imports_re_so_p7_holds_no_detection_rule():
    # SPEC *Deferred*: "The design states *what* is protected and never *how it is
    # recognised*. The detector rule set, its signals, and its thresholds are
    # hand-authored. P7 publishes the vocabulary the detectors write into."
    for path in modules():
        names = imports_of(path)
        assert "re" not in names, path.name
        assert "regex" not in names, path.name


def test_no_module_enumerates_an_identifier_class_or_holds_a_transform():
    # SPEC *Deferred*: "Which identifier classes exist and how each is transformed is
    # not enumerated anywhere in the design. `redaction_manifest` carries the class as
    # an opaque string until this is authored."
    import inspect
    from privacy import redaction
    assert not hasattr(redaction, "IDENTIFIER_CLASSES")
    assert not hasattr(redaction, "TRANSFORMS")
    parameters = inspect.signature(redaction.apply_redaction).parameters
    for required in ("classifier", "transform"):
        assert parameters[required].default is inspect.Parameter.empty


def test_the_gate_holds_no_threshold_and_reads_p1s_ceiling():
    # SPEC *Deferred*: "Numeric values for every ceiling ... Deferred to configuration,
    # not to this contract." The ceiling is read from `database_agent.budget`; the
    # request field is the caller's echo of it (M9).
    from database_agent.budget import CEILING_KEYS
    assert "model.max_dossier_tokens_per_call" in CEILING_KEYS
    from privacy.release import REQUEST_FIELDS
    assert "max_dossier_tokens" in REQUEST_FIELDS


def test_the_fixture_module_is_a_leaf_so_its_numbers_reach_no_decision():
    # The one module holding numbers holds them INSIDE records, and nothing imports
    # it. A fixture records a value the way a recorded call records one.
    for path in modules():
        if path.stem == "fixtures":
            continue
        assert "privacy.fixtures" not in imports_of(path), path.name
        assert "fixtures" not in imports_of(path), path.name


def test_subsystem_p7_is_written_in_exactly_one_module():
    # M8: "the acting part authors, P1 stores." A second place that writes the author
    # is a second place the two can disagree.
    holders = [path.name for path in modules() if "P7" in code_strings(path)]
    assert holders == ["authorship.py"]


def test_no_module_holds_a_gazetteer():
    # §3.7 names "validated gazetteers" as a mechanism and never enumerates contents.
    for module in imported():
        for name, value in vars(module).items():
            if name.startswith("_") or not isinstance(value, (tuple, frozenset)):
                continue
            assert len(value) <= 20, (module.__name__, name, len(value))


def test_the_retraction_limit_wording_lives_nowhere_in_the_package():
    # SPEC *Deferred*: "Consent-prompt and retraction-limit wording | §8.4 | UX copy."
    # Task 15 enforces PRESENCE; the words are P13's. Asserted package-wide here
    # because the failure mode is a helpful default appearing in a neighbouring module.
    for path in modules():
        for literal in code_strings(path):
            assert "cannot retract" not in literal.lower(), path.name
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_no_invention.py -v`
Expected: FAIL — `ImportError: cannot import name 'HELD_OPEN' from 'privacy.vocabulary'`.
Task 2 publishes `OPEN_QUESTIONS` (the SPEC's eleven) and nothing else; the three questions held
open that are **not** among the eleven have no home until this step adds one.

- [ ] **Step 3: Add `HELD_OPEN` to `src/privacy/vocabulary.py`**

Append to the module, below `OPEN_QUESTIONS`:

```python
#: The questions held open that are NOT among SPEC Open questions 1-11, each with the
#: document that states it. They are separate from `OPEN_QUESTIONS` because that
#: mapping is keyed by the SPEC's own numbering and these three are not in it: one is
#: a cross-part conflict deferred to this build, one is a residue D2 deliberately left,
#: and one belongs to P4 and reaches P7 only through redaction.
#:
#: Nothing here is answered anywhere under `src/privacy/`, and
#: `tests/p7/test_p7_no_invention.py` fails the moment one of them is.
HELD_OPEN: Mapping[str, str] = MappingProxyType({
    "I6": (
        "§8.4 gives the user the right to 'review and delete local derived data'; "
        "§8.2 forbids updating or deleting an event. D3 (2026-08-21) ratified the "
        "DIRECTION -- events append-only forever, derived projections tombstonable, "
        "'derived' a literal enumerated list -- and ratified that NOTHING IS BUILT "
        "until P13 drives it. `delete_derived` therefore refuses on both sides of the "
        "enumeration and writes nothing. Also open in: P5 OQ6, P13 OQ11, P1 OQ16."
    ),
    "filename-sixth-releasable-kind": (
        "§8.4's releasable list names FIVE kinds and puts 'Paths' in the always-local "
        "set, while §7.7's residual dossier 'includes the filename' and §7.3 forbids "
        "filenames in prompts only for `Protected Records`. P7's SPEC adds a sixth "
        "kind and flags it itself (NEEDS-JOSEPH B5d / C9a). Task 7 builds it and makes "
        "it unadmittable without `allow_unratified`, so a reviewer sees an unratified "
        "reading rather than a shipped one."
    ),
    "round-5-cuts": (
        "Round 5 recommended seven cuts. D5 ratified CUT 1 (P6 Task 26). D13 "
        "(2026-08-22) ruled the remaining five KEPT, including CUT 2 (this part's "
        "Task 19, the transport guard) and CUT 4 (the `Gate` facade). They are held "
        "here because a kept cut is a decision that can be revisited, and the tasks "
        "carry their callouts so a later reader can decide against them with the plan "
        "in front of them."
    ),
})

#: Two entries were REMOVED on 2026-08-22 because Joseph ruled them, and a guard that
#: asserts a ruled question is still open fails the day the plan is executed -- the exact
#: failure this task's own preamble diagnoses for P6 OQ11 under D2.
#:   `P6-sensitivity-field-row` -> **D7**: P6 creates no `sensitivity_status` row and
#:      P7's `ClassificationRecord` is the sole home. C24 and C25 closed.
#:   `P4-region-origin`         -> **D10**: P4's `norm` means TOP-LEFT; the Vision
#:      adapter converts (`readers.ocr_vision._box`, commit 87016b0). C22 closed.
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_no_invention.py -v`
Expected: PASS — 27 passed

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–21 green, and the 1302 P1–P5 tests still green. This is the run that
matters most for this task: the L2 guard walks **every module under `src/`** and imports each one, so
a module that raises at import anywhere in the repository fails here.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/vocabulary.py tests/p7/test_p7_no_invention.py
git commit -m "feat(P7): the no-invention guard, D2's shape asserted where OQ11's guard used to be"
```

---

---

### Task 22: The walking-skeleton P7 step, and 11 §9's second fixture path

**Files:**
- Modify: `src/privacy/fixtures.py` (add `SKELETON_FIXTURE` — see below)
- Test: `tests/p7/test_p7_skeleton_step.py`

**Interfaces:**
- Consumes: `orchestrator.run_wave2`, `.Wave2`, `.TARGETED_OCR_UNAVAILABLE`;
  `scan_agent.corpus_source.FilesystemCorpusSource`, `scan_agent.selection.record_selection`,
  `scan_agent.exclusion.is_protected_container`, `scan_agent.schema.create_scan_schema`;
  `extractors.safety.SafetyPolicy`, `extractors.dispatch.Readers`, `extractors.schema.create_extraction_schema`;
  `evidence_shape.store.RunWriter`; `eval_harness.bundle.bundle_files`,
  `eval_harness.store.create_eval_schema`; `database_agent.files_table.get_file`;
  `privacy.gate.Gate`, `privacy.release.Denied`, `.NeedsConsent`, `.Released`, `.Target`;
  `privacy.policy.set_policy`, `.transcription_authorized_for`;
  `privacy.classification_store.ClassificationStore`; `privacy.learning_seam.assign`;
  `privacy.consent.record_consent_choice`, `.pending_consent`;
  `privacy.audit.audit_records_for`; `privacy.transport_guard.assert_single_egress`;
  `privacy.fixtures.by_number`, `.SKELETON_FIXTURE`, `.FIXTURE_CLOCK`.
- Produces (`fixtures.py`): `SKELETON_FIXTURE: int = 10` — which published fixture **is** 11 §9's
  second path, named as data so P8 and P13 can find it without reading this plan.

**Done-means:** 13.

**The `run_wave2` signature is what makes path one assertable, and it was read live.** Eighteen
parameters, and **none of them is a gate, a classification, a detector or a P7 policy**. So *"`release`
was called zero times"* is not a discipline the skeleton observes — it is a **structural fact**: the
caller has nowhere to put a gate, so it cannot have called one. That is the strongest available form
of the Done-means clause and it is checked with `inspect.signature`, not by counting.

The parameter that **is** called `policy` is P5's `SafetyPolicy` — two fields, `is_protected_container`
and `is_dataless` — and **not** P7's `Policy`. Two different words one parameter apart is the defect
class this project has paid for most (`sensitivity` in four homes; `handling_class` fed
`sensitivity_state`). The test names both types in one assertion so the two cannot be conflated by a
later author who sees `policy=` and reaches for the gate's.

**The one seam Wave-2 does have is `transcription_authorized`, and P7 fills it.** P5's call site is
`transcription_authorized()` — a zero-argument predicate, `Callable[[], bool]`,
`src/extractors/long_tail.py:204`. Task 5 publishes `transcription_authorized_for(scope)` to satisfy
it. Path one wires the real one in and asserts it answers `False` under a policy with no grant, which
is the M10 back-edge working end to end. **This is not the gate being exercised**: it is an
authorization predicate consulted before an extractor runs locally, and no content leaves. The test
says so, because a reader who saw P7 in the Wave-2 call could otherwise conclude the skeleton
exercises §8.4's door.

**The bundle assertion INVERTS the skeleton's, and this is the second guard that would fail on day
one if it were copied.** The skeleton says path one *"must also assert that after classification the
Wave-2 bundle's `handling_class` is non-null, closing the loop `src/orchestrator.py:259` left open."*
That is wrong on two counts, and both are quotable:

1. **P7 never reaches the bundle, by its own Open question 8.** *"May a replay bundle carry audit
   records and excerpt spans? §8.5 allows 'a frozen corpus snapshot or a metadata-safe
   representation of one' and lists 'policy settings'. Whether a bundle intended to leave the user's
   machine may carry audit records — which name excerpts — is unstated. Affects P2."* Unanswered. A
   task that made P7 write into `bundle_file_entry` would answer it in code.
2. **The value is the Wave-2 caller's, and it is `None` on purpose.** The live comment at the call
   site — now at `src/orchestrator.py:402`, not 259 — says it in the caller's own words: *"The honest
   value is None because the class is unknown, not because another column happened to be empty."*
   That is the standing rule from the connection review: *"a part that does not own the concept
   passes `None` and says the value is unknown. It never forwards a neighbour's column because the
   shapes line up."* And it remains true after P7 ships, because **no task in any plan produces a
   detector** — so on a real corpus there is no class to carry.

So the test asserts the `None` **stays**, asserts `src/privacy/` writes nothing into any `bundle_*`
table, and names OQ8 as the reason. Reported as a correction to the skeleton's Task 22 block.

**Path two is 11 §9's addendum and P7 owns two of its four clauses.** The addendum, verbatim:

```text
P7/P8   a dossier that requires sensitive text
        Gate.release returns NeedsConsent
        P13 presents the four §8.4 options
        choosing no_model_use does not become abstain inside P8
```

11 §9 also states what kind of test it is: *"This is a contract test of B2, not an LLM test. It is
the minimum that makes the one privacy-failure seam exercisable without waiting for full depth."*
Clauses one and two are P7's and are asserted here against **fixture 10**, which exists for exactly
this. Clause three is P13's — its SPEC's routing table gives P7 the `consent` surface and
`action = select_consent_option`, and P13 is unbuilt. Clause four is P8's Done-means 13 and cannot be
run without P8. The test names both as deferred **in named tests that assert the parts do not exist**,
so the limitation lives in the suite rather than in a report nobody rereads. The B2 contract test the
first path cannot exercise is exactly this: path one never returns a `NeedsConsent`, because under
`offline` nothing gets far enough to need consent.

**And the honesty clause, which is the point of the whole task.** The detector is unwritten (D2), so
on a real corpus **every file resolves to `Denied(unclassified)`** — a correct, locked door with
nobody holding a key. Path one's classification is therefore written **by the test**, standing in for
the detector and saying so in its docstring, exactly as Task 17's verdict test and Task 20's fixtures
do. A final named test runs the gate over the actually-scanned file **with no classification** and
asserts `Denied(unclassified)`, so the plan's honest posture is a passing assertion rather than a
paragraph. **This step proves the door, not the classification.**

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_skeleton_step.py
"""Done-means 13, and 11 §9's second fixture path.

02-segmentation-map.md's walking skeleton is "One file, one deterministic path, every
seam touched. No LLM, no cloud, no embeddings -- which also means no privacy gate is
exercised, because nothing leaves the machine."

Done-means 13 turns that into an obligation: the skeleton "must nonetheless assert:
the classification exists for the scanned file; the gate is installed on the only
egress path; `release` was called zero times; the audit log is empty; and a deliberate
attempted call under `offline` returns `Denied` with reason `mode_forbids_target`.
That is the seam test -- that the door exists and is shut."

Read the last test in this file before reading the rest of it. The detector is
unwritten (D2), so the classification path one asserts is written HERE, by the test,
standing in for a detector that does not exist. On a real corpus every file resolves
to `Denied(unclassified)`. This step proves the door, not the classification.
"""
import dataclasses
import importlib
import inspect
import pathlib
from typing import Callable

import pytest

from database_agent.files_table import get_file

from eval_harness.bundle import bundle_files
from eval_harness.store import create_eval_schema

from evidence_shape.store import RunWriter

from extractors.archive import ArchiveManifest
from extractors.dispatch import Readers
from extractors.docx import DocxDocument
from extractors.image import ImageRecord
from extractors.long_tail import LongTailFile
from extractors.pdf import PdfDocument, PdfPage
from extractors.reading import Region
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from extractors.structured_text import TextDocument

from orchestrator import TARGETED_OCR_UNAVAILABLE, Wave2, run_wave2

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.exclusion import is_protected_container
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection

from privacy.audit import audit_records_for
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.consent import pending_consent, record_consent_choice
from privacy.fixtures import FIXTURE_CLOCK, SKELETON_FIXTURE, by_number
from privacy.gate import Gate
from privacy.learning_seam import assign
from privacy.policy import set_policy, transcription_authorized_for
from privacy.release import Denied, ModelTarget, NeedsConsent, Released, Target
from privacy.transport_guard import assert_single_egress
from privacy.vocabulary import CONSENT_OPTIONS

COMPONENT = "0.1.0"
NEVER: Callable[[], bool] = lambda: False
SKELETON_CLOCK = "2026-08-22T10:00:00+00:00"
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
SRC_ROOT = pathlib.Path(importlib.import_module("privacy").__file__).parent.parent


@pytest.fixture()
def skeleton_db(p7_conn):
    """P1 + P4 + P7 from `p7_conn`, plus the three schemas Wave 2 also needs.

    `tests/wave2/`'s own harness records why all five are created rather than four:
    "§0's 'each part owns its own tables' cuts both ways, and a harness that creates
    four parts' tables out of five is testing a database the product never runs on."
    """
    create_scan_schema(p7_conn)
    create_extraction_schema(p7_conn)
    create_eval_schema(p7_conn)
    return p7_conn


@pytest.fixture()
def corpus(tmp_path: pathlib.Path) -> pathlib.Path:
    """02-segmentation-map.md's input: "one PDF whose title carries a course code"."""
    root = tmp_path / "Documents"
    root.mkdir()
    (root / "syllabus.pdf").write_bytes(b"%PDF-1.4 BUSIB 4300")
    return root


def mime_for(path: pathlib.Path) -> str | None:
    return {".pdf": "application/pdf"}.get(path.suffix)


def skeleton_readers() -> Readers:
    """Deterministic readers. No LLM, no network, no OCR provider."""
    page = "BUSIB 4300 Course Information"
    return Readers(
        read_pdf=lambda p: PdfDocument(
            metadata={"Title": "BUSIB 4300 Syllabus"}, iso_dates={},
            pages=(PdfPage(number=1, text=page,
                           regions=(Region(zone="heading", start=0, end=29,
                                           ordinal=1, label="Course Information"),)),)),
        read_docx=lambda p: DocxDocument(core_properties={}),
        read_text_document=lambda p: TextDocument(text=page),
        read_long_tail=lambda p, transcribe=False: LongTailFile(),
        read_manifest=lambda p: ArchiveManifest(archive_type="zip"),
        read_image=lambda p: ImageRecord(image_format="PNG", dimensions="2880x1800",
                                         width=2880, height=1800),
        find_structured_strings=lambda text: (),
        recognize_markers=lambda names: (),
        dimension_signal=lambda w, h: None,
        filename_pattern=lambda name: None)


def offline_policy():
    """W1's floor, and every redaction facet at its more redacting value.

    §8.4's `must`: "The default posture must therefore be local-first and
    data-minimizing." A skeleton that ran under anything else would be testing a
    posture the design forbids as a default.
    """
    from privacy.policy import Policy
    return Policy(
        policy_version="policy-skeleton", operation_mode="offline",
        consent_grants=(),
        redaction_settings={"names": "redacted", "previews": "redacted",
                            "thumbnails": "redacted", "ocr_text": "redacted",
                            "location_data": "redacted"},
        automatic_move_permissions={}, plan_version="plan-1",
        set_at=SKELETON_CLOCK)


def walk(conn, corpus_root, *, authorized=None) -> Wave2:
    """One deterministic pass. Note what is NOT passed: there is no gate parameter."""
    selection = record_selection(conn, sources=[corpus_root], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return run_wave2(
        conn, selection, source=FilesystemCorpusSource(), mime_type_for=mime_for,
        scan_state="scanned", budget_exhausted=NEVER,
        detect_format=lambda p: p.suffix.lstrip(".") or None,
        policy=SafetyPolicy(is_protected_container=is_protected_container,
                            is_dataless=lambda path: False),
        readers=skeleton_readers(), sink=RunWriter(conn, author="P5"),
        now=lambda: SKELETON_CLOCK, context_window=40,
        no_usable_facts=TARGETED_OCR_UNAVAILABLE,
        transcription_authorized=authorized or NEVER,
        corpus_form="snapshot", policy_settings={},
        file_entry_body=lambda row: {"payload_ref": f"blobs/{row['content_hash']}"})


def only_file(conn) -> str:
    rows = conn.execute("SELECT file_id FROM files").fetchall()
    assert len(rows) == 1
    return rows[0]["file_id"]


def classify(conn, file_id, handling_class="personal_non_sensitive", *,
             protected=False) -> ClassificationRecord:
    """THE DETECTOR THAT DOES NOT EXIST, written by the test and saying so.

    D2 put the rule set behind an injection and no task in any plan produces one.
    SPEC *Deferred*: "The design states *what* is protected and never *how it is
    recognised*. The detector rule set, its signals, and its thresholds are
    hand-authored. P7 publishes the vocabulary the detectors write into."

    Until one is supplied, this is what a classification's arrival looks like: a
    caller writing through P7's writer. Nothing here is a detection rule; it is the
    act of recording a decision some other component made.
    """
    record = ClassificationRecord(
        file_id=file_id, content_hash=get_file(conn, file_id)["content_hash"],
        handling_class=handling_class, protected=protected, basis="user",
        evidence_refs=(), reliability_state="user_confirmed",
        observed_at=SKELETON_CLOCK)
    assign(conn, record, store=ClassificationStore(conn),
           component_version=COMPONENT)
    return record


def p7_events(conn) -> int:
    return conn.execute(
        "SELECT count(*) c FROM events WHERE subsystem = 'P7'").fetchone()["c"]


# ===========================================================================
# Path one -- the deterministic skeleton. The door exists and is shut.
# ===========================================================================

def test_the_wave_2_caller_has_nowhere_to_put_a_gate():
    # "`release` was called zero times" as a STRUCTURAL fact rather than a counted one:
    # eighteen parameters and not one of them is a gate, a classification, a detector
    # or a P7 policy. A caller that cannot hold a gate cannot have called one.
    parameters = inspect.signature(run_wave2).parameters
    assert len(parameters) == 18
    for forbidden in ("gate", "release", "classifier", "detector", "handling_class",
                      "privacy_policy", "classification"):
        assert forbidden not in parameters, forbidden


def test_the_policy_parameter_is_p5s_safety_policy_and_not_p7s():
    # Two different words one parameter apart. `SafetyPolicy` has two fields and
    # deliberately no third; P7's `Policy` has seven. Conflating them is how a future
    # author "wires the gate in" and silently disables the container rule instead.
    assert {f.name for f in dataclasses.fields(SafetyPolicy)} == {
        "is_protected_container", "is_dataless"}
    from privacy.policy import Policy
    assert "operation_mode" in {f.name for f in dataclasses.fields(Policy)}
    assert "operation_mode" not in {f.name for f in dataclasses.fields(SafetyPolicy)}


def test_the_deterministic_path_runs_end_to_end(skeleton_db, corpus):
    result = walk(skeleton_db, corpus)
    assert isinstance(result, Wave2)
    assert skeleton_db.execute(
        "SELECT count(*) c FROM extraction_runs").fetchone()["c"] > 0


def test_the_audit_log_is_empty_after_the_deterministic_path(skeleton_db, corpus):
    # Done-means 13's fourth clause. Not "P7 wrote few events" -- none, because
    # nothing asked the gate anything.
    walk(skeleton_db, corpus)
    assert p7_events(skeleton_db) == 0
    assert audit_records_for(skeleton_db,
                             file_id=only_file(skeleton_db)) == []


def test_the_classification_exists_for_the_scanned_file(skeleton_db, corpus):
    # Done-means 13's first clause. Written by `classify`, which stands in for the
    # detector and says so; see its docstring.
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    record = classify(skeleton_db, file_id)
    store = ClassificationStore(skeleton_db)
    assert store.current(file_id, record.content_hash) == record
    assert get_file(skeleton_db, file_id)["sensitivity_state"] is not None


def test_the_gate_is_installed_on_the_only_egress_path(skeleton_db, corpus):
    # Done-means 13's second clause, in the only form available before P8 exists:
    # there is no transport, so the property "the transport's only content parameter
    # is a `Released`" holds over an empty set -- and `assert_single_egress` is proven
    # correct against a conforming and four non-conforming fixtures in Task 19.
    walk(skeleton_db, corpus)
    transports = []
    for path in sorted(SRC_ROOT.rglob("*.py")):
        dotted = str(path.relative_to(SRC_ROOT).with_suffix("")).replace("/", ".")
        dotted = dotted[:-9] if dotted.endswith(".__init__") else dotted
        module = importlib.import_module(dotted)
        if getattr(module, "IS_MODEL_TRANSPORT", False):
            transports.append(module)
    assert transports == [], "a transport appeared; run assert_single_egress over it"
    for module in transports:                      # reachable the day P8 lands
        assert_single_egress(module)


def test_release_was_called_zero_times(skeleton_db, corpus):
    # Done-means 13's third clause, counted as well as proven structurally. A gate is
    # constructed, handed to nobody, and asked nothing -- which is exactly the
    # skeleton's shape: the door is installed and never opened.
    calls: list[object] = []

    class RecordingGate(Gate):
        def release(self, request):
            calls.append(request)
            return super().release(request)

    RecordingGate(skeleton_db, component_version=COMPONENT,
                  scope_for=lambda file_id: None)
    walk(skeleton_db, corpus)
    assert calls == []


def test_a_deliberate_call_under_offline_is_denied_mode_forbids_target(
        skeleton_db, corpus):
    # Done-means 13's fifth clause, and the whole point: the door is SHUT, not absent.
    # §8.4's fully offline mode: "No content leaves the device; only local rules and
    # local models may run."
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id)
    set_policy(skeleton_db, offline_policy(), component_version=COMPONENT, user_id="joseph",
               reason="the user switched the corpus to offline mode")
    gate = Gate(skeleton_db, component_version=COMPONENT,
                scope_for=lambda _file_id: None)
    request = dataclasses.replace(
        by_number(8).request, target=Target(file_ids=(file_id,), group_id=None))
    decision = gate.release(request)
    assert isinstance(decision, Denied)
    assert decision.reason == "mode_forbids_target"
    assert decision.explanation
    assert decision.remedy_options


def test_the_deliberate_call_is_audited_even_though_it_was_denied(
        skeleton_db, corpus):
    # §8.4: "Every model call should be recorded in a consent-aware audit record", and
    # §8.2 covers "Every significant event affecting a file". The empty log above is
    # empty because nothing asked, not because denials go unrecorded.
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id)
    set_policy(skeleton_db, offline_policy(), component_version=COMPONENT, user_id="joseph",
               reason="the user switched the corpus to offline mode")
    before = p7_events(skeleton_db)
    Gate(skeleton_db, component_version=COMPONENT,
         scope_for=lambda _file_id: None).release(dataclasses.replace(
             by_number(8).request,
             target=Target(file_ids=(file_id,), group_id=None)))
    assert p7_events(skeleton_db) > before
    assert audit_records_for(skeleton_db, file_id=file_id)


def test_the_transcription_back_edge_is_p7s_and_is_not_the_gate(skeleton_db, corpus):
    # M10's back-edge: P5's call site is `transcription_authorized()`, a zero-argument
    # predicate at `src/extractors/long_tail.py:204`. P7 fills it. This is an
    # authorization consulted before a LOCAL extractor runs -- no content leaves, and
    # it is NOT §8.4's door. A reader who saw P7 in the Wave-2 call could otherwise
    # conclude the skeleton exercises the gate.
    set_policy(skeleton_db, offline_policy(), component_version=COMPONENT, user_id="joseph",
               reason="the user switched the corpus to offline mode")
    authorized = transcription_authorized_for("Academics")
    assert inspect.signature(authorized).parameters == {}
    assert authorized() is False
    walk(skeleton_db, corpus, authorized=authorized)
    assert p7_events(skeleton_db) == 1        # the `policy_set` above, and nothing more


# ===========================================================================
# The bundle -- where this task INVERTS the plan skeleton
# ===========================================================================

def test_the_bundle_handling_class_is_still_none_after_a_classification(
        skeleton_db, corpus):
    # The plan skeleton expects this to be non-null "closing the loop
    # src/orchestrator.py:259 left open". It is NOT, and both reasons are quotable.
    #
    # 1. P7 Open question 8 is open: "Whether a bundle intended to leave the user's
    #    machine may carry audit records -- which name excerpts -- is unstated."
    #    A P7 that wrote into `bundle_file_entry` would answer it in code.
    # 2. The value is the Wave-2 caller's and the caller's own comment says why it is
    #    None: "The honest value is None because the class is unknown, not because
    #    another column happened to be empty."
    result = walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id)
    entries = bundle_files(skeleton_db, result.bundle_id)
    assert entries
    for entry in entries:
        assert entry["handling_class"] is None


def test_a_second_pass_after_classification_still_carries_none(skeleton_db, corpus):
    # The classification is written BEFORE this pass, so "the bundle was built too
    # early" is not the explanation. The caller passes a literal `None` and P7 has no
    # seam into it -- which is the honest posture while no detector exists.
    walk(skeleton_db, corpus)
    classify(skeleton_db, only_file(skeleton_db))
    second = walk(skeleton_db, corpus)
    for entry in bundle_files(skeleton_db, second.bundle_id):
        assert entry["handling_class"] is None


def test_src_privacy_writes_into_no_bundle_table(skeleton_db, corpus):
    # OQ8 held structurally, not by restraint: P7 imports no P2 writer at all.
    import ast
    privacy_dir = SRC_ROOT / "privacy"
    for path in sorted(privacy_dir.glob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("eval_harness"), path.name
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("eval_harness"), path.name


# ===========================================================================
# Path two -- 11 §9's second fixture path, the B2 contract test
# ===========================================================================

def test_the_skeleton_fixture_is_named_as_data():
    # So P8 and P13 can find 11 §9's second path without reading this plan.
    assert SKELETON_FIXTURE == 10
    assert isinstance(by_number(SKELETON_FIXTURE).decision, NeedsConsent)


def test_a_dossier_requiring_sensitive_text_returns_needs_consent(
        skeleton_db, corpus):
    # 11 §9, clauses one and two: "a dossier that requires sensitive text /
    # Gate.release returns NeedsConsent". §8.4: "If a model needs text containing
    # sensitive content, the user should see that requirement and choose."
    fixture = by_number(SKELETON_FIXTURE)
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id, handling_class="sensitive_personal",
             protected=False)
    set_policy(skeleton_db, fixture.policy, component_version=COMPONENT, user_id="joseph",
               reason="the published fixture's policy")
    gate = Gate(skeleton_db, component_version=COMPONENT,
                scope_for=lambda _file_id: fixture.area)
    decision = gate.release(dataclasses.replace(
        fixture.request, target=Target(file_ids=(file_id,), group_id=None)))
    assert isinstance(decision, NeedsConsent)
    assert decision.options == CONSENT_OPTIONS
    assert decision.consent_request_id


def test_path_one_can_never_produce_this_branch(skeleton_db, corpus):
    # Why 11 §9 exists: "It is the minimum that makes the one privacy-failure seam
    # exercisable without waiting for full depth." Under `offline` nothing gets far
    # enough to need consent, so the first path cannot exercise B2 at all.
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id, handling_class="sensitive_personal")
    set_policy(skeleton_db, offline_policy(), component_version=COMPONENT, user_id="joseph",
               reason="the user switched the corpus to offline mode")
    gate = Gate(skeleton_db, component_version=COMPONENT,
                scope_for=lambda _file_id: None)
    decision = gate.release(dataclasses.replace(
        by_number(SKELETON_FIXTURE).request,
        target=Target(file_ids=(file_id,), group_id=None)))
    assert isinstance(decision, Denied)
    assert decision.reason == "mode_forbids_target"


def test_no_model_release_exists_until_a_choice_is_recorded(skeleton_db, corpus):
    # Done-means 7's own falsifiable form, and it needs the id Task 14 added.
    fixture = by_number(SKELETON_FIXTURE)
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id, handling_class="sensitive_personal")
    set_policy(skeleton_db, fixture.policy, component_version=COMPONENT, user_id="joseph",
               reason="the published fixture's policy")
    gate = Gate(skeleton_db, component_version=COMPONENT,
                scope_for=lambda _file_id: fixture.area)
    decision = gate.release(dataclasses.replace(
        fixture.request, target=Target(file_ids=(file_id,), group_id=None)))
    records = audit_records_for(skeleton_db,
                                consent_request_id=decision.consent_request_id)
    assert [r.outcome for r in records] == ["consent_requested"]
    assert pending_consent(skeleton_db, decision.consent_request_id) is not None


def test_choosing_no_model_use_records_the_choice_and_releases_nothing(
        skeleton_db, corpus):
    # 11 §9's third clause is P13's gesture; P7's half is that the recorded choice
    # closes the request and produces no `model_release`. P13's SPEC: "P13 records the
    # collection, not the grant."
    fixture = by_number(SKELETON_FIXTURE)
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    classify(skeleton_db, file_id, handling_class="sensitive_personal")
    set_policy(skeleton_db, fixture.policy, component_version=COMPONENT, user_id="joseph",
               reason="the published fixture's policy")
    gate = Gate(skeleton_db, component_version=COMPONENT,
                scope_for=lambda _file_id: fixture.area)
    decision = gate.release(dataclasses.replace(
        fixture.request, target=Target(file_ids=(file_id,), group_id=None)))
    record_consent_choice(skeleton_db, decision.consent_request_id, "no_model_use",
                          user_id="joseph", component_version=COMPONENT,
                          observed_at=FIXTURE_CLOCK)
    outcomes = [r.outcome for r in audit_records_for(
        skeleton_db, consent_request_id=decision.consent_request_id)]
    assert "released" not in outcomes
    assert pending_consent(skeleton_db, decision.consent_request_id) is None


def test_no_model_use_is_one_of_the_four_and_is_not_a_denial_reason():
    # The typed half of "does not become abstain": `no_model_use` is a CONSENT OPTION.
    # It is not in `DENIAL_REASONS`, so a caller cannot map the branch onto a denial by
    # respelling, and `NeedsConsent` carries no `reason` field to hold one.
    from privacy.vocabulary import DENIAL_REASONS
    assert "no_model_use" in CONSENT_OPTIONS
    assert "no_model_use" not in DENIAL_REASONS
    fields = {f.name for f in dataclasses.fields(NeedsConsent)}
    assert fields == {"consent_request_id", "requirement", "options"}


def test_clause_four_is_p8s_and_clause_three_is_p13s_and_neither_exists_here():
    # 11 §9: "choosing no_model_use does not become abstain inside P8." INSIDE P8 --
    # so the assertion belongs to P8's suite, as its Done-means 13, and to P13's as its
    # Done-means 16. P7's obligation is to make the absorption UNREPRESENTABLE, which
    # the test above does at the type level; policing it is not P7's and cannot be.
    #
    # This test exists so the limitation lives in the suite rather than in a report
    # nobody rereads -- the same posture Task 19 takes for Done-means 3 and Task 20
    # takes for Done-means 11's second clause.
    for absent in ("llm_harness", "review_surface"):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(absent)
    assert by_number(SKELETON_FIXTURE).downstream_obligation == (
        "so P8 can prove it returns the branch to its caller intact")


# ===========================================================================
# The honesty clause -- read this one first
# ===========================================================================

def test_with_no_detector_every_real_file_resolves_to_denied_unclassified(
        skeleton_db, corpus):
    # The claim the plan skeleton makes in prose, asserted: "Until it is supplied, a
    # P7 running against a real corpus classifies nothing and every real file resolves
    # to `Denied(unclassified)` -- a correct, locked door with nobody holding a key."
    #
    # Nothing is classified here because nothing in the product classifies. Path one's
    # `classify()` is the test standing in for a detector; remove it and this is what
    # the walking skeleton actually produces.
    walk(skeleton_db, corpus)
    file_id = only_file(skeleton_db)
    assert get_file(skeleton_db, file_id)["sensitivity_state"] is None
    assert ClassificationStore(skeleton_db).history(file_id) == []
    set_policy(skeleton_db, by_number(9).policy, component_version=COMPONENT, user_id="joseph",
               reason="the fixture's starting policy")
    gate = Gate(skeleton_db, component_version=COMPONENT,
                scope_for=lambda _file_id: "Academics")
    decision = gate.release(dataclasses.replace(
        by_number(9).request, target=Target(file_ids=(file_id,), group_id=None)))
    assert isinstance(decision, Denied)
    assert decision.reason == "unclassified"
    assert not isinstance(decision, Released)


def test_this_step_proves_the_door_and_not_the_classification():
    # Said once, in a test, so it survives the plan being archived. "P7 is done" and
    # "the product classifies files" are different claims and only the first is
    # deliverable from these twenty-two tasks.
    detector_producers = []
    for name in ("privacy.classification", "privacy.classification_store",
                 "privacy.learning_seam", "privacy.gate"):
        module = importlib.import_module(name)
        detector_producers += [
            attribute for attribute in vars(module)
            if attribute.lower().startswith("detect")
            or attribute.upper().startswith("RULE")]
    assert detector_producers == []
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_skeleton_step.py -v`
Expected: FAIL — `ImportError: cannot import name 'SKELETON_FIXTURE' from 'privacy.fixtures'`
(collection fails on the first import; Task 20 published sixteen fixtures and named none of them as
11 §9's second path).

- [ ] **Step 3: Add `SKELETON_FIXTURE` to `src/privacy/fixtures.py`**

Append to the module, below `MODE_SWEEP`:

```python
#: 11 §9's second fixture path, named as data rather than left to be rediscovered:
#:
#:     P7/P8   a dossier that requires sensitive text
#:             Gate.release returns NeedsConsent
#:             P13 presents the four §8.4 options
#:             choosing no_model_use does not become abstain inside P8
#:
#: 11 §9 also says what kind of test that is -- "a contract test of B2, not an LLM
#: test ... the minimum that makes the one privacy-failure seam exercisable without
#: waiting for full depth". P7 owns the first two lines; the third is P13's and the
#: fourth is P8's Done-means 13.
SKELETON_FIXTURE: int = 10
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_skeleton_step.py -v`
Expected: PASS — 21 passed

- [ ] **Step 5: Run the whole repository**

Run: `pytest tests/ -q`
Expected: PASS — P7 complete, and the 1302 P1–P5 tests still green. This task touches
`src/orchestrator.py`, `tests/wave2/` and `tests/conftest.py` **not at all**: it imports the Wave-2
caller and asserts against it, and every P7 fixture it needs lives in `tests/p7/`.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/fixtures.py tests/p7/test_p7_skeleton_step.py
git commit -m "feat(P7): the walking-skeleton gate step, and 11 9's NeedsConsent path"
```

---

---

# Appendix — what the section authors reported rather than resolved

Each section closed by naming its own contradictions instead of silently resolving them. That is the
mechanism that found this project's defects, so the reports are kept **verbatim**, grouped by the
section that made them. **They are dated, and they are not all still true** — several were closed by
rulings made afterwards. Read the preamble first; it wins.

Two of these appendices belong to files whose **last task lost** — `PLAN-tasks-04-07.md`'s sits after
its Task 7 and `PLAN-tasks-15-22.md`'s three sit after its Task 22. They are kept because they are
evidence about **tasks**, not about files.

## What in here is no longer true

**Two labels are wrong.** Passages citing **NEEDS-JOSEPH C5** for *"does P6 keep a
`sensitivity_status` field row"* mean **C24**; passages citing **C3** for the region origin mean
**C22** (brief §14 renumbered both).

**Three questions below are RULED, and every "held open" / "remains for Joseph" row naming them is
stale:**

| Row as written | Now |
|---|---|
| *"Whether P6 keeps a `sensitivity status` field row beside P7's record … Joseph."* | **D7** — P6 creates **no** such row. P7's `ClassificationRecord` is the sole home, and P7's Contract-in from P6 is empty. **C24 and C25 closed.** |
| *"Which corner `norm` measures from … P4's, and nobody's yet."* | **D10** — `norm` is **TOP-LEFT**. `readers.ocr_vision._box` converts Vision's bottom-left rectangles at the adapter (`87016b0`). **C22 closed**, and Task 8's redaction may rely on it. |
| *"SPEC §6 and §7 cannot both hold for `release_id` … Joseph / Task 10."* | **D14** — `AuditRecord.release_id` is `None` on a release record and the join runs **ledger → events**. SPEC §7 amended; §6's ordering stands. |

**One citation that looks like the first row but is NOT, and must not be swept up with it.**
`PLAN-tasks-11.md` cites **C5** as the reason `SENSITIVE_CLASSES` stays unpublished. That label is
**correct** and the question is **still open**: C5 is *"is `protected` exactly the top two handling
classes?"*, which D7 did not touch. **Reading D7 as licence to publish that set would be exactly the
error the restraint exists to prevent.**

**The five round-5 cuts are ruled KEPT (D13)**, so any row describing one as "unratified, may be
deleted" now means "ruled, kept, and revisitable" — the tasks keep their callouts so a later reader
can decide against them with the plan in front of them.

---

# Reported by the Tasks 1–3 section


## What these three tasks leave open, and for whom

**NEEDS-JOSEPH C5 — P7's SPEC and D2 disagree about whether a P6 `sensitivity` field exists, and
nothing here picks a side.** P7's SPEC Contract in says *"**P6 must accept `sensitivity` as a
first-class universal field** (§3.11) rather than a domain-scoped one"*, and the design does list
*"sensitivity status"* among §3.11's universal file facts. D2 then made P7's `ClassificationRecord`
authoritative, and round 1 found that the P6 field has no producer. D2 settled which record is
AUTHORITATIVE; it did not settle whether a second, P6-owned field row continues to exist beside it.
**Task 3 is written so that nothing depends on the answer:** `src/privacy/classification.py` imports
nothing from P6, reads no `file_facts` row, and uses no P6 vocabulary except `reliability_state`,
which it stores opaquely and does not validate. If Joseph rules that P6 keeps the field, Task 3 is
unchanged and Task 4 gains a reader; if he rules that it does not, Task 3 is unchanged and P6 creates
no such row. Flagged, not resolved.

**Open questions this section holds and does not answer.** Question 1 (`protected` versus the top
two classes) is held by `ClassificationRecord.protected` being a required caller-supplied boolean
with no derivation. Question 2 (filename versus path) is held by `filename` being the one item kind
absent from §8.4's own sentence, marked as such in `vocabulary.py`'s comment and asserted in the
test. Questions 3–11 are held by `vocabulary.OPEN_QUESTIONS`, which Task 21 reads. None of the eleven
is answered in code.

**Contract deviations, all four reported above and repeated here so a reviewer can find them in one
place.** `vocabulary.OPEN_QUESTIONS` and `vocabulary.HANDLING_CLASS_LABELS` are added to Task 2;
`classification.COMPLETENESS_RULE` and `classification.sensitivity_signal_keys` are added to Task 3.
`src/privacy/__init__.py` is a docstring-only package marker rather than the re-export the File
Structure describes, because `Gate` is Task 20. Task 3 reaches `vocabulary.HANDLING_CLASSES` through
`check_handling_class` and does not import `evidence_shape.runs.COMPLETENESS` into the module. The
skeleton's Task 2 heading counts four `protected` spellings and its body names five; the body is
followed. The skeleton's Task 3 paragraph says a dataless file has no run row; the skeleton's own
refusal table says it has one, and the table is followed.

---

# Reported by the Tasks 4–7 section


## What these four tasks leave open, by name

| # | Question | Held by | Where it must be answered |
|---|---|---|---|
| **C5** | Does P6 keep a `sensitivity status` row among §3.11's universal fields, beside P7's authoritative record? P7's SPEC Contract-in says P6 *"must accept `sensitivity` as a first-class universal field"*; D2 makes P7's record authoritative; round 1's F-2 found the P6 field has no producer. | Task 4 depends on no P6 field: its store creates its own table and one test asserts it works in a database with no `file_facts` at all. | **Joseph.** Until then P6 creates no such row and P7 reads none. |
| **B5d / C9a** | Is `filename` a sixth releasable kind? §8.4 names five and puts *paths* in the always-local set; §7.7 puts the filename in the residual dossier; §7.3 forbids filenames in prompts only for Protected Records. | Task 7: `UNRATIFIED_ITEM_KINDS`, `FILENAME_OPEN_QUESTION`, and `allow_unratified` as a required keyword with no default. | **Joseph.** Task 21 should assert no module under `src/privacy/` passes `allow_unratified=True`. |
| **OQ1** | Is `protected` exactly the top two handling classes? | Task 4 stores `protected` and never derives it; Task 7 takes it as a required keyword. | P7 SPEC revision. |
| **OQ3** | What is a *"corpus area"*? | Task 5: `scope` is an opaque string P7 neither parses nor validates. | P7 SPEC revision; affects P3, P9, P10. |
| **OQ11** | Which of `offline` and `local_model` ships as the install default? | Task 6: `install_mode` is a required keyword and `src/privacy/` holds no default mode. | Turns on whether a local model is assumed present. |
| **§2.9** | Which consent option authorizes speech-to-text? | Task 5: an explicit grant at the scope whose option is not `no_model_use`. Reported as a reading. | Not stated anywhere in the design. |
| **M10 seam** | P5's `transcription_authorized` is `Callable[[], bool]` and takes no scope. | Task 5: `TranscriptionAuthorization` carries the scope as a field, and a test asserts P5's signature so the day it widens the adapter can be deleted. | P5 contract revision, or leave the adapter. |
| **Always-local by name** | `MetadataField(name="current_path")` is not caught by Task 7's vocabulary check. | Task 7: a test asserts the gap deliberately, because a synonym list is the gazetteer P7 may not own. | Task 13's decision on the declared name, or a detector nobody has written. |
| **`candidate_label`** | *"a label already present in the local database"* is unverifiable while P6 is unbuilt. | Task 7: named in `CandidateLabel`'s docstring; no length ceiling invented. | P6. |

---

# Reported by the Tasks 12–14 section


## What this section leaves for its neighbours

| Left open | Owner | Why it is not closed here |
|---|---|---|
| `Gate.release` calling `mint_release` after `append_audit` and before returning | Task 11 | The facade is Task 11's file. Task 12 proves the ledger; the wiring is one call in `gate.py`. |
| `Gate.release` collecting triggered reasons and calling `first_reason` | Task 11 | Same. Task 13 publishes the order and the resolver; the collection is the facade's. |
| `append_audit`'s `extra` keyword | Task 10 | SPEC §7 enumerates a release record, and a denial's `reason` and a consent request's `requirement` have no field in it. Reported in the additions table. |
| `audit_records_for(file_id=…)` matching the explanation's `file_ids`, not only the column | Task 10 | `events` has one `file_id` column. Without this, Task 15's `prior_releases` under-reports every group-scoped release. Reported. |
| `policy.grant_consent` appending no event | Task 5 | Pinned here, as the mirror of Task 15's ruling for `revoke_consent`. |
| `Denied` carrying `evidence_refs` | Task 11 | The skeleton's own `deny(...)` takes them and SPEC §6 requires the explanation be evidence-referenced. |
| `release.py` re-exporting `NeedsConsent` and importing no other `privacy` module | Task 11 | The import-direction rule above. It is the one constraint these tasks place on Task 11. |
| Whether a caller absorbs `NeedsConsent` | P8 Done-means 13, P13 Done-means 16 | *"P7's obligation is to make the absorption unrepresentable, not to police it."* |
| A detector that produces a `ClassificationRecord` | **Nobody, and that is the finding** | D2 put the rule set behind an injection and no task in any plan supplies one. Until it is, `Denied(unclassified)` is every real file's verdict, which is what Task 13 is built for. |

---

# Reported by the Tasks 15–22 section


## Self-Review — Tasks 15–22

**Spec coverage.** SPEC §8's revocation surface → Task 15. §8.7's *Correction learning* and
10-i4's query-before-propose row for P7 → Task 16. SPEC §9's automatic-move predicate → Task 17.
SPEC §10's display policy and aggregate summary → Task 18. Done-means 3's instrument → Task 19.
SPEC §11's fixture list, item for item → Task 20. The *Deferred* table and all eleven Open questions
→ Task 21. Done-means 13 and 11 §9's second path → Task 22.

Done-means in this section: **8** → T15 · **9** (first clause) → T17 · **10** → T18 · **3** (the
instrument only) → T19 · **11** (first clause) → T20 · **12** (the display half) → T18, (the
introspection half) → T21 · **2** (the user-revision half) → T16 · **13** → T22.

**Three items are not fully provable here and each names the part that closes it.** Done-means 3's
property is P8 Done-means 1 (T19 has a named test). Done-means 9's second clause is P11's and P12's
(T17 names the permitting policy so they can consume rather than re-derive). Done-means 11's second
clause is P8's test run (T20 has a named test). None is hidden.

**No invention.** No module in this section holds a number except `privacy.fixtures`, which holds
two, both allowlisted by name in Task 21 and both installed through P1's `budget.set_ceiling`. No
regex, no gazetteer, no identifier class outside the fixture's own opaque string, no retention
period, no corpus-area definition, no detection rule, no default operation mode. Every scope is a
required keyword with no default (`files_in_scope`, `scope_for`), and so is every question the design
leaves open (`unclassified_permits_local`, `retraction_limit`, `classifier`, `transform`).

**Every guard is runtime introspection**, with one exception that is stated where it occurs: Task 21's
SQL guard walks the AST and excludes docstrings, the `code_tokens()` mechanism from
`tests/p3/test_p3_no_invention.py`, because *"this token appears nowhere"* cannot be asserted by
introspecting a namespace.

**P7 modifies no file it does not own.** Every task creates only under `src/privacy/` and `tests/p7/`.
Task 22's final step checks it with `git status --porcelain`.

---

## Where the skeleton was ambiguous or self-contradictory

Each of these was resolved in the plan above and is listed so a reviewer can reject the resolution
rather than discover it.

| # | Where | What is wrong, and what this section did |
|---|---|---|
| 1 | Task 21 `Interfaces` · Task 2 `Produces` | The skeleton's **repo-wide L2 set `{evidence_shape, extractors, privacy}` is wrong in both directions.** Measured 2026-08-22: `extractors` binds **no** P4 text materialiser, and **`orchestrator` binds `text_units_for_run`** (`src/orchestrator.py`, copying text units into P2's sealed bundle). Task 21 asserts `{evidence_shape, orchestrator, privacy}` with a reason per member. A guard naming a package that binds nothing passes forever without checking anything. |
| 2 | Task 22 | **`bundle_file_entry.handling_class` cannot be made non-null by P7.** The skeleton asks Task 22 to assert it is non-null after a classification; P7's own OQ8 and 22-p1-p7-connection-contract.md §1 say P7 never reaches the bundle, and the live caller passes literal `None` at `src/orchestrator.py:402`. Task 22 asserts `NULL`, names the field as the Wave-2 caller's, and names the closing move. |
| 3 | SETTLED paragraph · Tasks 16, 17, 18 | The `facts_seam` → `classification_store` rename says *"Tasks 12, 13 and 14 change only the import and the type name"* — but **Tasks 16, 17 and 18 also name `facts_seam.SensitivityFacts`** in their `Consumes` blocks. Renamed here on the same ruling. |
| 4 | Task 4 `Produces` | `ClassificationStore` publishes `current`, `write`, `supersede`, `history` and **no way to get a record's id**, while P1's `mark_superseded` keys on a `record_id` column and `ClassificationRecord`'s eight SPEC §2 fields carry none. Task 16 cannot supersede. **Added `current_fact_id(file_id, content_hash) -> str \| None`.** |
| 5 | Task 5 `Produces` | `grant_consent(...)` and `revoke_consent(...)` are published **with literal ellipses**. Task 15 pins `revoke_consent(conn, policy, scope, *, user_id, component_version, observed_at) -> str`, returning the new `policy_version` and appending **no** event — the `consent_revoked` append is `revoke`'s, which is the only reading under which Task 15's `Consumes` list (`CONSENT_REVOKED` **and** `append_event` **and** `revoke_consent`) is coherent. |
| 6 | Task 14 `Produces` | `record_consent_choice(conn, consent_request_id, option, *, user_id, ...)` ends in an ellipsis. Task 22 pins `*, user_id, component_version, observed_at -> None`. |
| 7 | Task 11 · Task 20 | **`Gate.__init__` is unpinned anywhere**, and SPEC §11's fixtures cannot be replayed without it — and an unreplayed fixture is the drift the skeleton itself calls *"worse than none."* Task 20 publishes `GATE_ARGUMENTS`, ten keywords, each traceable to a published requirement or an open question. |
| 8 | Task 15 `Produces` · D3 | **`UnratifiedResolution` is now a misnomer** — D3 ratified the direction. The name is kept because it is the published contract, its docstring says what it now reports (*unbuilt*, not *unratified*), and a second exception `ScopeNotDerived` carries the other side of the enumeration. A rename is a contract revision and is left to Joseph. |
| 9 | Task 15 `Produces` | `revoke(conn, policy, scope, *, user_id, ...)` ends in an ellipsis and `RevocationResult.prior_releases` needs the files in scope, which OQ3 leaves unnamed. Added `files_in_scope` and `retraction_limit`, both required keywords with no default. |
| 10 | SPEC §7 vs the skeleton's audit-record paragraph | **`appended_at` versus `observed_at`.** SPEC §7 lists `appended_at`; the skeleton's *audit record's home* paragraph lists `observed_at` among the five fields with an `events` column and does **not** list `appended_at` among the thirteen without one. Tasks 15 and 20 read `record.observed_at` and build every fixture from `AUDIT_FIELDS` rather than a literal list, so a respelling of a field they do not read cannot break them — but **Task 10 must settle which name it publishes.** |
| 11 | Skeleton preamble | **`AUDIT_FIELDS` is said to be nineteen and SPEC §7's own list enumerates sixteen names**, with `content_hash`/`content_hashes` and `file_id`/`file_ids` appearing in both singular and plural forms across the two documents. Tasks 15 and 20 build from the published tuple and assert coverage rather than the count, so the count is Task 10's to settle. |
| 12 | Tasks 11 and 14 | **`NeedsConsent` is in both `Produces` blocks** — Task 11's branch-type list and Task 14's. Two definitions of one type is the defect class this project pays for most. This section imports it from `privacy.release` (Task 11's) throughout; Task 14 should re-export, not redefine. |
| 13 | Task 16 `Produces` | `suppressed` is a predicate, and 10-i4's Done-means is *"**zero re-emissions**"* — a predicate returning `True` is not an emission that did not happen. **Added `assign`**, the system-side write that returns `None` when suppressed. |
| 14 | Task 16 `Consumes` | The list omits `authorship`, `append_event` and `set_sensitivity_state`, while *"What its tests must prove"* requires `reclassify` to append `classification_superseded` and D2 requires the projection. Added. |
| 15 | Task 17 `Interfaces` | `may_move_automatically(conn, file_id, plan_version)` has no way to reach the `content_hash` the classification is keyed on (D2). Added `database_agent.files_table.get_file` and the keyword-only `store` and `scope_for`. |
| 16 | Task 18 `Interfaces` | `display_policy(conn)` cannot read a plan-scoped policy (§8.8) and `summarize_protected(conn, scope)` cannot enumerate a scope OQ3 leaves unnamed. Widened with keyword-only `plan_version`, `store` and `files_in_scope`; SPEC §10's published `Gate.display_policy()` / `Gate.summarize_protected(scope)` are unchanged where a caller sees them. |
| 17 | Task 18 | Neither Task 2's `DISPLAY_FACETS` nor Task 6's `MORE_REDACTING` claims the two **values** SPEC §10 states (`shown | redacted`). They are defined in `display.py`, which is the first module that needs them. |
| 18 | Task 19 `Produces` | Two exceptions, and a module with **no** public function is neither — it passes any `len(functions) <= 1` check, which is the vacuous pass this layer exists to prevent. Added `NoEgressPoint`. |
| 19 | Task 20 `Produces` | `GateFixture`'s six fields cannot express the classification a fixture assumes, nor the *"obligation on P8 ... in their own metadata"* the same paragraph requires. Added `classification` and `p8_obligation`, both with defaults, so the six-name positional order is unchanged. |
| 20 | Task 21 `Interfaces` | `vocabulary.OPEN_QUESTIONS` is asserted there and appears in **no** task's `Produces`. Task 21 adds it to `vocabulary.py`, together with `NEEDS_JOSEPH` for the two items held open by name (B5d/C9a and C5), which are not among SPEC's numbered eleven. |
| 21 | Task 21 · D2 | The skeleton's own Task 21 text says *"That **the D2 shape holds** — see §4"*, while §5 of the preamble still says *"Every open question stays open ... Eleven questions are open in P7's SPEC."* P6 OQ11 is closed and is **not** one of P7's eleven, so both are true — but a guard written from the second sentence without reading the first fails on execution day. The guard is written from D2. |
| 22 | Skeleton *Deferred* table vs Task 15 | The table keeps *"The **presence** of `retraction_limit` is asserted; the wording is not"*, but the `Produces` block gives `revoke` no way to receive a wording. `retraction_limit` is now a required keyword with no default, and Task 21 asserts no module-level string in `src/privacy/` contains the word. |

## What remains for Joseph, from this section only

1. **I6 / D3.** `delete_derived` refuses on both sides of the enumeration and writes nothing. The
   enumeration — `evidence.{raw_value, normalized_value, context_before, context_after}` and
   `text_units.text` — is written down here for the first time and is the thing to check.
   **No tombstone column exists**; P13 drives the migration.
2. **`UnratifiedResolution`'s name** (item 8 above). Keeping it is a contract-stability choice, not a
   semantic one.
3. **B5d / C9a — `filename` as a sixth releasable kind.** Held open by name in
   `vocabulary.NEEDS_JOSEPH` and exercised by fixture 16, where §7.3's Protected Records rule denies
   it either way, so the fixture does not settle it.
4. **C5 — does P6 keep a `sensitivity status` field row?** Held open by name. P7's SPEC Contract-in
   *requires* P6 to build it; D2 makes P7's record authoritative. Until it is answered, P6 creates no
   such row and P7 reads none.
5. **Open question 5** — whether `unreadable_unclassified` permits a local model call. Carried as
   `Gate(..., unclassified_permits_local=...)` with no default, and as fixtures 14 and 15, one per
   branch.
6. **Open question 3** — what a corpus area is. Three functions take a resolver with no default.
7. **The detector.** Not in this section's gift and not in any task's: D2 puts the rule set behind an
   injection and no plan produces one. Until it is supplied, `Denied(unclassified)` is what a real
   corpus gets, `summarize_protected` reports `count = 0`, and `may_move_automatically` refuses every
   file. Every task above is built for that being the ordinary path.

---

# Reported by the Tasks 17–19 section


## What these three tasks did not close

- **Done-means 3** stays where the coverage table put it. The instrument is proven; the property is
  P8's, and the call that closes it (`assert_single_egress(llm.transport)`) is written out in this
  plan's last test so P8 does not have to rediscover it.
- **Done-means 9's second clause** — *"P11/P12 consume the answer rather than re-deriving it"* — is a
  property of two parts that do not exist. Task 17 makes it possible by naming the permitting policy
  in the verdict and says so in a named test.
- **Open question 1** (is `protected` the top two classes?), **Open question 3** (what is a corpus
  area?) and **P13's Open question 7** (does a redaction setting have a scope?) are each held open
  by a signature and named in a test. None is answered in code.
- **The detector is still unwritten.** With no rule set, Task 17 answers `unreadable_unclassified`
  for every file and Task 18 counts zero protected records. Both are correct; neither is a finished
  product, and each has a test that says so in its own docstring.

---

# Reported by the Tasks 20–22 section


## What these three tasks leave open, and to whom

| Held open | Held by | Whose call |
|---|---|---|
| I6 — §8.4's delete versus §8.2's append-only | `vocabulary.HELD_OPEN["I6"]`; `delete_derived` refusing on both sides of D3's enumeration (Task 15) | Joseph — NEEDS-JOSEPH C1. D3 ratified the direction; nothing is built until P13 drives it. |
| `filename` as a sixth releasable kind | SPEC Open question 2, asserted present and unresolved by Task 21 | Joseph — NEEDS-JOSEPH **B5d** and **C9a**. §8.4 names five kinds and puts *paths* in the always-local set; the SPEC adds a sixth and flags it itself. |
| Whether P6 keeps a `sensitivity status` field row beside P7's record | `vocabulary.HELD_OPEN["P6-sensitivity-field-row"]`; Task 21 asserts P7 reads no P6 surface | Joseph. D2 settled which record is authoritative and did not settle whether a second row exists; P7's SPEC Contract-in still requires P6 to accept `sensitivity` as a universal field, and round 1 found that field has no producer. |
| Which corner `norm` measures from | `vocabulary.HELD_OPEN["P4-region-origin"]`; Task 21 asserts P7 does no arithmetic on a region field | P4's, and nobody's yet — no document in the repository states an origin. P7 is the part that would otherwise answer it by accident, when it redacts a bounding box. |
| What a *corpus area* is (Open question 3) | `Gate(scope_for=…)`, a required keyword with no default; Task 20's fixtures carry the answer as data | Joseph — NEEDS-JOSEPH C3. |
| Whether a replay bundle may carry audit records and excerpt spans (Open question 8) | Task 22 asserting `bundle_file_entry.handling_class` stays `None` and that `src/privacy/` imports no P2 writer | Joseph, and P2's. |
| Whether the product classifies anything at all | Task 22's last two tests | **The detector.** No task in any plan produces one. Twenty-two tasks deliver a correct, locked door; they do not deliver a key. |
