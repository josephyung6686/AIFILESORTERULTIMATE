# P6 — Facts and facets — PLAN

Date: 2026-08-22
Substrate: P1–P5, the Wave-2 orchestrator and the reader stack, shipped and green at **1302 tests**.
Source of truth: `planning/00-database-agent-product-design.md`. Then `SPEC.md`. Then this preamble.

**26 tasks: 1–25 and 27.** Task 26 is cut (D5). Every task carries complete test code and complete
implementation code; there are no placeholders and no stubs anywhere in this plan.

This preamble is written **once, by the lead**, and is the only place these facts appear. The task
sections do not repeat it. If a task section and this preamble disagree, this preamble is later and
wins — every such disagreement was found deliberately and is recorded in
`../_ASSEMBLY-RULINGS.md`.

---

## 1. How to execute this plan

Each task is a TDD unit: write the test, **run it and see the stated failure**, write the
implementation, run it again and see PASS, commit. A step that says *"Expected: FAIL — …"* means it.
If the failure you get is not the failure written down, **stop** — the plan is wrong about the
substrate, and that is worth more than the task.

**P6 writes only `src/facts/` and `tests/p6/`.** It touches no file outside them, mints no new §8.2
event type, and no module branches on `source_type` or `extractor_name`. `subsystem = "P6"` appears
in exactly one place.

**Python 3.12, stdlib only.** Third-party libraries live in `src/readers/` behind the `readers`
extra, and `src/facts/` may not import one.

**`planning/domains/` is NOT P6's field catalogue and `src/facts/` must never import it.** It is a
research artifact. `FIELD_ROWS` is a small authored module-level table whose *content* comes from
`planning/domains/canonical_fields.json` (37 canonical keys) — a **source to read**, not a runtime
dependency.

### Build order — the numbering is not the order

```
Tasks 1–6      package, catalogue, values, file_facts, unresolved, cache
   ↓
Tasks 7–13     Wave B. Task 7 first (the citation layer).
               ┌─ Task 11 (facts.facets) BEFORE Task 10 and Task 12 ─┐
               │  Task 10 Consumes facts.facets' word-boundary matcher │
               │  Task 12 Consumes facts.facets.fill_or_abstain        │
               └─ Task 13 (facts.domains) may run at any point ────────┘
   ↓
Tasks 14–16    Wave C — the three fact families
   ↓
Tasks 17–19    Wave D — the seams
   ↓
Tasks 20–25, 27
```

**Run Task 10 before Task 11 and its Step 2 failure is the wrong failure**, and Step 4 cannot pass.
The edge is the skeleton's own, not invented here: §3.7's word-boundary discipline binds facet values
**and** §3.5 context terms, so a second matcher inside `facts.rules` would be a second home for the
one rule that makes `MIT` not be found inside `submit`.

One more ordering constraint, stated once because it appears nowhere else: **`chain()` walks forward
only.** With `a → b → c`, `chain(a)` returns `[a, b, c]` and `chain(c)` returns `[c]`. A history read
must start at the **oldest** row, so Task 18's `fact_history` finds the tail before it walks.

---

## 2. The ratified decisions that bind this plan

| | Ruling |
|---|---|
| **D1** | §3.8's four role fields — `authored_by`, `target_school`, `our_firm`, `client` — **are** in the catalogue. Done-means 13 and 22 require `authored_by` to exist. No career fields are authored. |
| **D2** | P7's `ClassificationRecord` is authoritative for sensitivity. `files.sensitivity_state` is its projection. P6 takes **no** `SensitivityStateWriter` and **no** injected protocol. |
| **D3** | `events` is append-only forever. Derived projections may be tombstoned; "derived" is a literal enumerated list; **no writer-less tombstone column**. |
| **D4** | `jurisdiction` is a **value**, never a field name and never a destination dimension. |
| **D5** | **Task 26 is CUT.** No `dispatch` split, no `run_wave2` restructure. |
| **D6** | The academic field key is **`subject`**, and every stored key is `snake_case`. The catalogue carries **no `course` row**; §3.11's word "course" is the design's prose and survives inside quotations only. |
| **D7** | **P6 creates no `sensitivity_status` field row.** P7's record is the sole home. §3.11's mention describes an attribute; it does not commission a field. |
| **D8** | **`target_school` is the stored key.** "target university" (§3.11) is an alias, never a second key. |
| **D9** | `destination_eligible` is **TRUE** for `target_school` and `client`, **FALSE** for `authored_by` and `our_firm`. §3.8 forbids *authorship or creator identity* as a destination dimension — that is the other two. |
| **D10** | P4's `norm` region unit means **TOP-LEFT**. Closed in `src/readers/ocr_vision.py`. |
| **D12** | **`p6_conn` seeds Task 2's catalogue rows** — it calls `create_fields(conn)`. The catalogue is a closed authored table §3.12 forbids creating at runtime: schema in spirit, not test data. |
| **D13** | The five unratified round-5 cuts are **kept**. Each cut-target task carries its callout. |

**The general naming rule, which produced D6, D8 and the `field_key` ruling:** *one stored key per
concept; every other word the design uses for it becomes an alias, never a second key.* Which word
becomes the key is decided per concept on the evidence, not by "prose wins".

**`document type` is never a key.** It is the design's generic word for whichever field the active
domain declares — `application_document_type` (College applications) or `artifact_type`
(Research/Code).

**`capture_date` and `capture_year` are two different fields.** `capture_date` is §3.2's EXIF-derived
fact; `capture_year` is §3.11's Photos destination dimension. Neither is `creation_date`.

---

## 3. Conventions, stated once

### 3.1 Closed vocabularies are NAMED CONSTANTS — never a literal, never an index

Task 1 publishes the six reliability states **both ways**: `STATES: tuple[str, ...]` for iteration and
membership, **and one named constant per state** — `DIRECT`, `POSSIBLE`, `VALIDATED`, `LLM_SUPPORTED`,
`USER_CONFIRMED`, `REJECTED`. **Every other module imports the named constant.**

> A bare literal is a second home for a published vocabulary — the defect class that has cost this
> project the most. An index (`STATES[1]`) is single-homed and unreadable, and it **silently couples
> every consumer to the tuple's order**: reorder the tuple and meanings change with no test failing.
> The repo's own precedent is a named constant — P5 publishes `POTENTIALLY_SENSITIVE`, P1 publishes
> `SUPERSEDED_CONTENT`.

**This extends to every closed vocabulary either part publishes.** Concretely, and because three
earlier drafts stated the opposite as shared law: **Task 4 publishes a named constant per
`FACT_ORIGINS` member; Task 5 publishes one per `ATTEMPTED_PRODUCERS` member and one per
`UNRESOLVED_REASONS` member.** Consumers import them.

That `write_unresolved` validates its reason against `UNRESOLVED_REASONS` through P4's `check` — so a
misspelling raises `NotInVocabulary` rather than storing — is **true and worth knowing**. It is not a
reason to spell the reason inline. Validation at the seam catches a *typo*; it does not stop the
literal being a *second home*.

**One deliberate exception**, blessed rather than left silent: Task 16's `SIGNAL_TIERS[-1:]` for
§2.6's screenshot band. That is P4's tuple, its members are integers rather than a string vocabulary,
and "the last band" is a genuine reading of an ordering rather than a spelled member.

**Task 1's guard, precisely.** No module other than the one publishing them may bind a collection
whose members **are** the six states — asserted by **runtime introspection**, never by source-text
search. Read more broadly it would forbid `VERSION_FAMILY_STATES`, `SESSION_STATE`, `EVENT_STATE` and
`LLM_STATES`, which siblings legitimately publish, and would break three tasks.

Every threshold, weight, gazetteer, regex catalogue and producer string is **injected with no
default**. The guard tasks assert this by runtime introspection too — a text search matches comments
and docstrings, and scanning text for a token has produced a false result on this project nine times.

### 3.2 §3.4's cache key — ONE rule, ONE helper, and it is Task 6's

**`facts.cache` is Task 6's module and no other task may add to it.** Task 6 publishes
`fact_cache_key`, and **every producer imports it**. No task writes its own copy.

The rule, settled — and note it is **not** the rule three earlier drafts carried:

> `extractor_version` is `canonical_json` of the sorted distinct `[extractor_name, extractor_version]`
> pairs of **every observation of that file version** — not of the observations the fact happens to
> cite — and the key is computed per **(file version, deterministic pass)**.

The deciding argument, which is the abstention:

> **The fact and the abstention produced by one pass share one key.** The SPEC requires the
> `unresolved` row to carry the *"same composition as `file_facts` (§3.4), so an abstention is
> invalidated by the same events that invalidate a fact"* — and **an abstention with no citations has
> no cited observations to compute a key from**. One key per pass answers both.

### 3.3 Two orderings that are readings of P4, not new orders

**`analysis_tier` is the LAST tier present**, in `ANALYSIS_TIERS` order:
`filesystem` < `native` < `ocr` < `llm`. That is what lets a later, richer pass **supersede** rather
than overwrite.

`canonical_json` is the project's one deterministic serialization; a second one would be a second
answer. `sha256_of` is **length-prefixed and injective**, so `None` is distinguishable from `""` in
the digest and `("a","bc")` cannot collide with `("ab","c")`.

**`model_identifier` and `prompt_fingerprint` are `None` on every deterministic fact.** Task 17 is the
one exception: an LLM-supported fact carries P8's real values and lands at `analysis_tier = "llm"`,
which is `ANALYSIS_TIERS[-1]` — and that is precisely why the two never share a slot.

### 3.4 The published surface — the union, and it is binding

`facts.states` — `STATES`, the six named constants, `EXCLUDED_STATE`, `strength`, `is_stronger`
· `facts.fields` — `FIELD_SCOPES`, `DOMAIN_FIELDS`, `FIELD_ROWS`, `FieldRow`, `create_fields`,
`get_field`, `fields_in_scope`, `FieldNotInCatalogue` · `facts.values` — `ValueRow`, `VALUE_ORIGINS`,
`ensure_value`, `set_display_label` · `facts.file_facts` — `FILE_FACTS_COLUMNS`,
`FORBIDDEN_COLUMN_SUBSTRINGS`, `FACT_ORIGINS`, `write_fact`, `facts_for_file`, `EvidenceRequired`
· `facts.unresolved` — `UNRESOLVED_REASONS`, `ATTEMPTED_PRODUCERS`, `write_unresolved`
· `facts.cache` — `CACHE_KEY_PARTS`, `fact_cache_key`, `is_stale` · `facts.evidence` —
`observations_for_version`, `context_pair`, `cite`, `analysis_tier_for_observation`
· `facts.facets` — `word_boundary_match`, `Candidate`, `rank`, `fill_or_abstain` · `facts.domains`
· `facts.schema` — `create_facts_schema`.

> **`strength` and `is_stronger` are CUT 6's target, and CUT 6 is unratified (D13).** Tasks 14–19
> import `is_stronger`. That dependence is exactly the evidence a reader needs to decide the cut, so
> it is stated here rather than buried.

**`write_fact`'s signature, pinned — and it has no tail:**

```python
write_fact(conn, *, file_id, content_hash, field_key, value_id, reliability_state, origin,
           evidence_refs, cache_key, active, cited_quote_refs=(), model_identifier=None,
           prompt_fingerprint=None, internal_score=None, rejection_reason=None) -> str
```

Two earlier drafts wrote this ending in `…`, which brief §2 forbids and which left three consuming
tasks guessing.

**`field_key`, not `field_id`.** The column is `field_key` and it holds the field key — in `values`,
in `file_facts`, and in every signature that takes one. `fields.field_key` is the PRIMARY KEY, which
is what an FK to it requires: `PRAGMA foreign_keys` is ON and a foreign key to a non-PK/UNIQUE parent
raises `foreign key mismatch` at INSERT, not at DDL.

**Trap:** `FORBIDDEN_COLUMN_SUBSTRINGS` must **not** be run against the `fields` table — the
legitimate column `destination_eligible` contains the substring `destination`.

**Trap:** `values` is a SQL reserved word. Every statement must quote it `"values"`. One unquoted
statement breaks `create_facts_schema` and therefore every later task.

### 3.5 The one permitted import edge

`facts` imports **`ContractViolation` from `extractors`**, and nothing else. `FactPassNotRun` must
inherit it, or the orchestrator's catch-all swallows the guard into a `failed` run and it stops
guarding. Task 25's no-import guard permits exactly this edge.

### 3.6 `tests/p6/conftest.py`

**Task 1 creates it and publishes `p6_conn`** — P1's database with P4's three tables, P6's own tables,
**and Task 2's `fields` catalogue rows created** (D12) — built on the root `conn` fixture in
`tests/conftest.py`, exactly as `tests/p4/conftest.py` builds `p4_conn`. Every test file takes
`p6_conn` and `tmp_path` and constructs everything else itself. Any task carrying a copy becomes
*verify it exists, do not duplicate it*.

---

## 4. Verified live, 2026-08-22 — by import and by execution, not from a document

> Every one of these was run before a line of this plan was written, because three defects on this
> project came from reading a signature instead of importing it.

Re-confirmed by the lead at assembly, not copied forward.

**P4 vocabulary.** `RELIABILITY_STATES == ('user_confirmed', 'direct', 'validated', 'llm_supported',
'possible', 'rejected')` · `ANALYSIS_TIERS == ('filesystem', 'native', 'ocr', 'llm')` ·
`SIGNAL_TIERS == (1, 2, 3)` and its members are **integers** · `SOURCE_TYPES` has 14 members ·
`ZONES` has 15.

**P4 store.** `observations_for_file(conn, file_id) -> list[Observation]` — spans **every content hash
the file has had**, `ORDER BY rowid` · `observations_by_key(conn, observation_key)` — same ordering,
and returns `[]` for an unknown key rather than raising · `runs_for_content(conn, content_hash)` ·
`unit_for_observation(conn, observation) -> TextUnit | None` · `record_run` / `record_observation`
write with **no foreign key to `files`**, so Task 7's tests need no P1 file row.

**`Observation`.** `observation_key`, `locator` and `zone` are **`@property`, not dataclass fields**;
the key is `sha256:`-prefixed. `__post_init__` raises `NotInVocabulary` for a `source_type` outside
`SOURCE_TYPES`, but does **not** enforce conformance rule 11 — an `Observation` with
`signal_tier=1` and `source_type="text_document"` constructs without complaint, and
`conformance.validate_observation` is where rule 11 lives. `dataclasses.replace` works on the
frozen-slots class and **recomputes the key**. `validate_observation` raises **`NotInVocabulary`**,
not `NonConforming`.

**The `observation_key` experiment — executed, not assumed.** Writing fixture 1's observation at
`extractor_version = "1.0.0"` and again at `"2.0.0"` produces the **same** key
(`sha256:db67768abb77…`), because the key hashes `content_hash · extractor_name · locator · raw_value`
and nothing else — and `observations_by_key` then returns both rows. **That is the whole of M14 and
Done-means 30, provable rather than asserted.**

**P1.** `files_table.get_file` returns a bare `sqlite3.Row` from `fetchone()` — **no `.get`**, and
`None` for an unknown file, so wrap in `dict()` only after checking. `FILES_COLUMNS` has sixteen
members. `content_hash` is **64 lowercase hex with no `sha256:` prefix**, and
`ExtractionRun.__post_init__` rejects any other shape.

**P1 supersede.** `mark_superseded(conn, table, *, old_id, new_id, reason) -> None` writes **three
columns across two rows** — the old row gets `superseded_by` and `supersede_reason`, the new row gets
`supersedes`. It raises `KeyError` on an unknown `old_id`, and `ValueError` when the old row is
already superseded (*the first `supersede_reason` is never overwritten, §8.2*), when the reason is
empty, and when the link would cycle. **It does not touch `preferred` and knows nothing about it** —
that column is Task 18's whole job. `chain(conn, table, record_id) -> list[sqlite3.Row]` walks
**forward only**. `supersede_ddl(table)` returns exactly
`"supersedes TEXT, superseded_by TEXT, supersede_reason TEXT"`.

**P1 events.** `RESERVED_EVENT_TYPES` contains `"fact creation"` and `"fact rejection"` — **both
spelled with a space** — and contains **no supersession event and no abstention event**, which is why
Task 18 appends none.

**The propagation proof.** `extractors.failure.ContractViolation` inherits `Exception` **directly**,
and `orchestrator._extract_one` re-raises it by name rather than converting it into a `failed` run.
Executed end to end: a `ContractViolation` subclass raised from inside a `no_usable_facts` callable
propagates out of `ocr_policy.text_layer_state` untouched.

**`extractors.filesystem.METADATA_SLOTS == ("normalized_filename", "extension", "mime_type")`** —
**no timestamp**. See §6.

---

## 5. The P4 fixtures this plan uses, byte-exact

All nineteen are usable **with no extractor present**, which is what makes P6 buildable today. Task 10
drives fixture 1 verbatim; other tasks author P4-shaped observations directly, which is the same thing
`evidence_shape.fixtures` does. These five are the ones the plan pins:

| # | design case | the bytes that matter |
|---|---|---|
| **1** | §2.8 "page 1, heading 2"; §3.2's syllabus | `raw_value="BUSIB 4300"`, zone `heading`, `reliability="possible"`, locator `heading:page=1/heading=2`, `context_before="Syllabus — "` (capital S, U+2014, one space either side), `context_after=" — Spring 2026"`, `context_truncated=False`, `occurrence_count=3`, `pdf.text/1.0.0` |
| **6** | §2.2 — `direct` describes the slot, not the value's usefulness | `raw_value="python-docx"`, zone `metadata`, locator `metadata:field=Producer`, `reliability="direct"`, `docx.metadata/1.0.0` |
| **7** | §2.8's EXIF example; §3.2's capture-date derivation | `raw_value="2026:07:17 14:03:22"`, zone `metadata`, locator `metadata:field=DateTimeOriginal`, `reliability="direct"`, `image.exif/1.0.0` |
| **12** | §2.9 "dates or identifiers from labeled cells" | `raw_value="2025"`, zone `table`, locator `table:sheet=2/row=7/column=3`, **`reliability="possible"`**, `xlsx.cells/1.0.0` |
| **18** | §2.9 design/creative, indexed-but-unreadable (M3) | `source_type="design_creative"`, zone `metadata`, locator `metadata:layer=3`, `raw_value="Background"` |

**Fixture 12 is why §3.5's fourth slot must not gate on the observation's own reliability.** It is one
of the four slots §3.5 names, and P4 marks it `possible`. A producer that required `direct` would make
one of the design's four worked slots unreachable against P4's own fixture for it — and would still
pass a test suite whose helper hard-codes `direct`.

---

## 6. What is open, and stays open

**The detector does not exist.** D2 puts P7's rule set behind an injection and no task in any plan
produces one. On a real corpus **every file resolves to `Denied(unclassified)`**. Build that as the
ordinary path; **never default an absent classification to a public or low class.**

**Two of §3.5's four direct slots cannot reach a fact today.**
`extractors.filesystem.METADATA_SLOTS` carries **no timestamp**, so §3.13's filesystem-timestamp slot
has no publisher. And the **content-hash** slot cannot produce a fact at all: M14 admits no citation
that is not an `observation_key`, and P1's `files.content_hash` is a **column, not evidence**. Task 8
supports the slot when a caller supplies one and passes an empty tuple in production; the fact the
hash actually supports is Task 14's duplicate family. **Consumer with no producer, twice, in the
design's own worked list.**

**Catalogue 01's 115 entries have no compiler, and it does not belong in `src/facts/`.** 102 of the
115 are `prefix` or `regex`, and `boundary_rule` is English prose with no machine-readable form.
Task 9 takes **compiled predicates** so `facts` holds no regex catalogue — which means something must
compile 115 entries and no task here does. It belongs with the loader, beside the flattening of
`property_names`. A working matcher exists and was executed against all 115 entries with **0 misses
and 0 false positives**; it is recorded in `../_ASSEMBLY-RULINGS.md` §4.8 for the loader's author.

**The discount has a caller.** §2.2's suppression fires **before** ranking. `FactResolver`
requires `screen_metadata` with no default (Task 20); Task 9 publishes the helper. `DEGRADATION_ORDER`
stays the three producers — screening is not a fourth producer.

**D9's positive half is asserted in Task 2.** `authored_by` and `our_firm` are not destination-eligible;
`target_school` and `client` are.

**`document_title` has a publisher and no catalogue field.** Task 8 routes it to
`FieldNotInCatalogue`, which is the honest outcome. If a PDF title should reach a fact, the catalogue
owes a row — Task 2's call.

**Round 4's C-5.** P8's Contract-in names `normalize(field, raw_value)` and
`contradicts(claim, existing_fact)` as P6's; Task 17 disowns both. Each part hands them to the other,
so neither builds them. **Named, not invented.**

**Open questions carried, not closed:** OQ3 (`purpose` universal vs Applications) · OQ5 (Finance
schema vs safety-first) · OQ6 (multiplicity) · OQ8 (custom-template fields) · OQ9 (group-accepted
purpose copy) · OQ10 (equal-rank contradiction). Task 25's guard holds each one open **by runtime
introspection**, and must not hold open anything already ruled.

**The five unratified cuts (D13).** CUT 3 (Task 23, `plan_versions`), CUT 6 (the five-rank strength
ladder) and CUT 7 (the read surface, Task 24) target this part. Each target task carries its callout.
**Do not silently comply with a cut, and do not silently ignore one** — both are the same failure.

---

## 7. The one thing that must not be built

Task 19 has P6 raise `FactPassNotRun` when the verdict is consulted for a `(file_id, content_hash)`
whose deterministic pass has not been recorded. That is correct, and it always propagates.

But **Task 26 is cut**, so nothing rewires `src/orchestrator.py`, and
`extractors.ocr_policy.text_layer_state` consults `no_usable_facts` for **every text-bearing PDF**
inside the caller's single loop, before any deterministic pass could have run.

> **If P6's resolver is ever passed to `run_wave2` as `no_usable_facts`, the first text-bearing PDF
> ends the scan.**

The caller keeps passing `orchestrator.TARGETED_OCR_UNAVAILABLE`. P6 publishes
`no_usable_facts_for(conn, *, usable_threshold)` as a **read surface its own tests exercise**. Wiring
it into the caller is separate later work and **must not be done as "integration"**.

---

## 8. The safety rule that outranks everything here

A protected container is **marked and counted, never opened**. It appears in the UI as
present-but-untouched, with a reachable explanation. It is **never silently omitted**, and it is never
described as *"understood and found unimportant"*.

---

### Task 1: Package skeleton, P6's authorship, and the six states published once

**Files:**
- Create: `src/facts/__init__.py`
- Create: `src/facts/authorship.py`
- Create: `src/facts/states.py`
- Create: `tests/p6/conftest.py`
- Test: `tests/p6/test_p6_authorship.py`
- Test: `tests/p6/test_p6_states.py`

**Interfaces:**
- Consumes: `database_agent.events.RESERVED_EVENT_TYPES`, `evidence_shape.vocabulary.RELIABILITY_STATES`, `evidence_shape.vocabulary.EXTRACTOR_RELIABILITY_STATES`, `evidence_shape.vocabulary.check`, `evidence_shape.vocabulary.NotInVocabulary`, `evidence_shape.conformance.validate_observation`, `evidence_shape.fixtures.by_number`.
- Produces: `SUBSYSTEM: str`, `COMPONENT_VERSION: str`, `AUTHORED_EVENT_TYPES: tuple[str, str]`, `event_defaults(**fields) -> dict`; `STATES: tuple[str, ...]` (re-export), **one named constant per state — `USER_CONFIRMED: str`, `DIRECT: str`, `VALIDATED: str`, `LLM_SUPPORTED: str`, `POSSIBLE: str`, `REJECTED: str`** — `STRENGTH_ORDER: tuple[str, ...]`, `EXCLUDED_STATE: str`, `strength(state: str) -> int`, `is_stronger(a: str, b: str) -> bool`.

**Done-means:** foundational to all; directly none.

**Why this is Task 1.** Two things every later task touches are settled here and nowhere else: whose
name lands in `events.subsystem`, and how the six reliability states are spelled. Both are the kind
of value that, left to the task that first needs it, gets typed by hand in twenty places. Putting
them first means Task 25's guard has exactly one module to look at for each.

**`event_defaults` is a helper, not a writer.** It fills §8.2's authorship fields and returns a
plain `dict` for the caller to hand to P1's `append_event`. It opens no connection and writes
nothing, so there is no path on which `facts` appends an event without a caller having decided one
is due. This is P3's shape verbatim (`src/scan_agent/authorship.py`, read on 2026-08-22), and P6
follows it rather than inventing a second one.

**The two event names carry a space.** `RESERVED_EVENT_TYPES` was introspected on 2026-08-22 and
contains `fact creation` and `fact rejection` — nineteen names, both present. `fact_creation` raises
`UnregisteredEventType` at run time, not at review, which is the same class of defect as MINOR 2's
`OCR`/`ocr`. P6 registers neither name, because registration is a spec-level act (P1 *Contract out*
§3, rule 4).

> **A skeleton line corrected against live code, 2026-08-22.** The skeleton's Task 1 says
> *"`conformance.validate_observation` raises `NonConforming` on an observation whose `reliability`
> is `validated`"*. It raises **`NotInVocabulary`**. Verified by execution:
>
> ```text
> RAISED NotInVocabulary : reliability='validated' is not one of ('direct', 'possible');
> adding a member is a P4 contract revision and a shape-version bump, not a local decision
> inside an extractor (segment-kind rule 5)
> ```
>
> `NonConforming` and `NotInVocabulary` are unrelated classes (`NotInVocabulary` subclasses
> `ValueError`; `NonConforming` subclasses `Exception`), so a test written to the skeleton's wording
> would fail against shipped, green P4. The test below expects `NotInVocabulary`. The boundary the
> skeleton wanted asserted — extractors write two of the six, P6 owns all six — is asserted exactly
> as it asked, from both sides, in one test.

> **A skeleton line narrowed, for the same reason.** The skeleton asks Task 1 to prove *"the absence
> of any string literal spelling a state name anywhere else in `facts`"*. Three sibling task files,
> already written against this skeleton, put state literals inside `src/facts/`:
> `PLAN-tasks-14-15.md` has `VERSION_FAMILY_STATES = ("validated", "possible")` and
> `SESSION_STATE = "possible"`; `PLAN-tasks-16-19.md` has `EVENT_STATE = "validated"` and
> `LLM_STATES = ("llm_supported", "possible")`. A producer naming the one or two states it is
> allowed to write is not a second copy of the vocabulary — it is the producer's own contract, and
> forbidding it would make this task's test the thing that blocks three correct tasks.
>
> What preamble rule 2 actually forbids is *"a second copy and no alias table"*. So the guard here
> is the precise one: **no module in `facts` other than `states.py` binds a module-level collection
> whose members are the six**. That is runtime introspection over `vars(module)`, not a source-text
> search, and it catches the defect the skeleton was aiming at while permitting the three subsets
> above. Task 25 owns the whole-package version of it.

**The six are published BOTH ways, and every other module imports the NAMED CONSTANT.** `STATES` is
for iteration and membership; `USER_CONFIRMED`, `DIRECT`, `VALIDATED`, `LLM_SUPPORTED`, `POSSIBLE`
and `REJECTED` are for naming one state. **Never a bare literal, never an index.** A bare literal is
a second home for a published vocabulary — this project's most expensive defect class. An index
(`STATES[1]`) is single-homed and unreadable, and it silently couples every consumer to the tuple's
**order**: reorder the tuple and every meaning changes with no test failing. The repo's own
precedent is the named constant — P5 publishes `POTENTIALLY_SENSITIVE`, P1 publishes
`SUPERSEDED_CONTENT`.

The literal is spelled **here and nowhere else**, because this is the module that publishes it, and
`test_the_six_named_constants_are_exactly_the_six_states` pins each name to its member of `STATES`
so a typo in one of them is a failing test rather than a silent second vocabulary. A producer that
names the one or two states it may write — `EVENT_STATE`, `SESSION_STATE`, `VERSION_FAMILY_STATES`,
`LLM_STATES` — builds that subset **from these constants**, which is what keeps it the producer's
own contract rather than a second copy.

**`rejected` has no strength, and asking for one raises.** §3.13: *"A rejected fact is a proposal
that the user or validator marked as incorrect."* It is an exclusion, not the bottom of a ladder — a
`rejected` fact that compared as merely weaker than a `possible` one would be resurfaced by any
comparison that picks the strongest, which is exactly what §8.7 forbids (*"Otherwise the system will
repeatedly resurface the same attractive but incorrect grouping"*). So `STRENGTH_ORDER` has five
members, `STATES` has six, and the sixth is named as excluded rather than omitted silently.

- [ ] **Step 1: Write the two failing tests**

```python
# tests/p6/test_p6_authorship.py
"""M8: the acting part authors, P1 writes. P6 authors two of §8.2's nineteen."""
import pytest

from database_agent.events import RESERVED_EVENT_TYPES, append_event

from facts.authorship import (
    AUTHORED_EVENT_TYPES, COMPONENT_VERSION, SUBSYSTEM, event_defaults,
)


def test_the_two_event_names_are_8_2s_own_and_carry_a_space():
    # Introspected from P1 on 2026-08-22: RESERVED_EVENT_TYPES contains
    # "fact creation" and "fact rejection". `fact_creation` raises
    # UnregisteredEventType at run time — the MINOR 2 `OCR`/`ocr` defect again.
    assert AUTHORED_EVENT_TYPES == ("fact creation", "fact rejection")
    for name in AUTHORED_EVENT_TYPES:
        assert " " in name
        assert "_" not in name


def test_both_names_are_already_reserved_so_p6_registers_nothing():
    # P1 Contract out §3, rule 4: registration is a spec-level act. Both names are
    # in P1's frozen table of nineteen; P6 declares neither.
    assert set(AUTHORED_EVENT_TYPES) <= set(RESERVED_EVENT_TYPES)
    assert len(RESERVED_EVENT_TYPES) == 19


def test_facts_publishes_no_registration_call():
    import facts.authorship as module
    assert not [n for n, v in vars(module).items()
                if callable(v) and n.lower().startswith("register")]


def test_p6_is_named_in_exactly_one_module_at_this_task():
    # The whole-package version of this is Task 25's. Here it is the two modules
    # that exist: authorship names P6, states names nobody.
    import facts.authorship as authorship
    import facts.states as states
    assert authorship.SUBSYSTEM == "P6"
    assert not hasattr(states, "SUBSYSTEM")


def test_event_defaults_fill_in_8_2s_authorship_fields():
    fields = event_defaults(event_type="fact creation", file_id="f1",
                            content_hash="sha256:abc", explanation='{"field": "subject"}')
    assert fields["subsystem"] == SUBSYSTEM
    assert fields["component_version"] == COMPONENT_VERSION
    assert fields["event_type"] == "fact creation"
    assert fields["file_id"] == "f1"
    assert fields["observed_at"]


def test_a_caller_supplied_observed_at_wins_so_a_replay_can_pin_the_clock():
    # §8.5 replays a run and compares it against a prior result; two readings of the
    # wall clock would be a false diff.
    fields = event_defaults(event_type="fact rejection", explanation="{}",
                            observed_at="2026-08-19T14:03:22+00:00")
    assert fields["observed_at"] == "2026-08-19T14:03:22+00:00"


def test_event_defaults_refuse_an_event_type_p6_does_not_author():
    # P3 authors `hashing` and `stat observation`; P5 authors `extraction` and `OCR`;
    # P12 authors the move events. P6 authors exactly two.
    for foreign in ("hashing", "extraction", "OCR", "planned move", "fact_creation"):
        with pytest.raises(ValueError):
            event_defaults(event_type=foreign, explanation="{}")


def test_event_defaults_refuse_to_name_another_subsystem():
    # M8: a `fact creation` event whose subsystem reads "P8" records that the model
    # harness wrote the fact table. P6 authors its facts; P8 proposes.
    with pytest.raises(ValueError):
        event_defaults(event_type="fact creation", subsystem="P8", explanation="{}")
    # Naming P6 explicitly is not an error — it is a no-op.
    assert event_defaults(event_type="fact creation", subsystem="P6",
                          explanation="{}")["subsystem"] == "P6"


def test_what_event_defaults_produces_is_accepted_by_p1s_live_writer(conn):
    # The contract is only real if P1 takes it. `events.file_id` carries no foreign
    # key, so this needs no `files` row, no observation and no extractor.
    event_id = append_event(conn, **event_defaults(
        event_type="fact creation", file_id="f1", content_hash="sha256:abc",
        explanation='{"field_key": "subject", "evidence_refs": ["sha256:deadbeef"]}'))
    row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    assert row["event_type"] == "fact creation"
    assert row["subsystem"] == "P6"
    assert row["component_version"] == COMPONENT_VERSION
    assert row["explanation"]
```

```python
# tests/p6/test_p6_states.py
"""§3.13's six reliability states, spelled once — by P4, and re-exported here."""
import importlib
import pkgutil

import dataclasses

import pytest

from evidence_shape.conformance import validate_observation
from evidence_shape.fixtures import by_number
from evidence_shape.vocabulary import (
    EXTRACTOR_RELIABILITY_STATES, RELIABILITY_STATES, NotInVocabulary,
)

from facts.states import (
    DIRECT, EXCLUDED_STATE, LLM_SUPPORTED, POSSIBLE, REJECTED, STATES,
    STRENGTH_ORDER, USER_CONFIRMED, VALIDATED, is_stronger, strength,
)


def test_states_is_p4s_tuple_and_not_a_copy_of_it():
    # Preamble rule 2: "The six literals are P4's, already published, and P6
    # re-spells none of them." Identity, not equality: a copy would drift.
    assert STATES is RELIABILITY_STATES
    assert STATES == ("user_confirmed", "direct", "validated", "llm_supported",
                      "possible", "rejected")


def test_the_six_named_constants_are_exactly_the_six_states():
    # Preamble §3.1: the six are published BOTH ways -- `STATES` for iteration and
    # membership, one named constant for naming one state. Every other module
    # imports the constant: never a bare literal (a second home), never an index
    # (single-homed, unreadable, and coupled to the tuple's ORDER). This test is
    # what makes the literal safe to spell in `states.py` and nowhere else -- a typo
    # in one constant fails here rather than becoming a second vocabulary.
    named = (USER_CONFIRMED, DIRECT, VALIDATED, LLM_SUPPORTED, POSSIBLE, REJECTED)
    assert named == STATES
    assert len(set(named)) == 6
    for one in named:
        assert one in STATES


def test_the_3_13_prose_spellings_are_prose_and_are_not_members():
    # §3.13 writes "LLM-supported" and "user confirmed"; §3.5 writes "LLM-supported"
    # too. Those are English, not values. A value outside the six is a load error,
    # never a spelling to normalize.
    for prose in ("LLM-supported", "User-confirmed", "user confirmed", "Direct"):
        assert prose not in STATES


def test_no_module_in_facts_publishes_a_second_copy_of_the_six():
    # Preamble rule 2: "P6 publishes no second copy and no alias table." A producer
    # naming the one or two states it may write is not a copy; a module-level
    # collection whose members ARE the six is.
    import facts
    offenders = []
    for info in pkgutil.iter_modules(facts.__path__):
        module = importlib.import_module(f"facts.{info.name}")
        if module.__name__ == "facts.states":
            continue
        for name, value in vars(module).items():
            if not isinstance(value, (tuple, list, set, frozenset)):
                continue
            if all(isinstance(m, str) for m in value) and set(value) == set(STATES):
                offenders.append(f"{module.__name__}.{name}")
    assert offenders == []


def test_the_strength_order_is_3_13s_and_has_five_members():
    assert STRENGTH_ORDER == ("possible", "llm_supported", "validated", "direct",
                              "user_confirmed")
    assert strength("user_confirmed") > strength("direct") > strength("validated") \
        > strength("llm_supported") > strength("possible")
    assert set(STRENGTH_ORDER) < set(STATES)


def test_rejected_has_no_strength_because_3_13_makes_it_an_exclusion():
    # "A rejected fact is a proposal that the user or validator marked as incorrect."
    # A rejected fact that merely ranked below `possible` would be resurfaced by any
    # comparison that picks the strongest — §8.7's own failure mode.
    assert EXCLUDED_STATE == "rejected"
    assert EXCLUDED_STATE in STATES
    assert EXCLUDED_STATE not in STRENGTH_ORDER
    with pytest.raises(NotInVocabulary):
        strength("rejected")
    with pytest.raises(NotInVocabulary):
        is_stronger("direct", "rejected")


def test_a_string_that_is_not_a_state_at_all_raises_rather_than_scoring_zero():
    with pytest.raises(NotInVocabulary):
        strength("probable")
    with pytest.raises(NotInVocabulary):
        strength("")


def test_is_stronger_is_strict_and_total_over_the_five():
    assert is_stronger("direct", "possible")
    assert not is_stronger("possible", "direct")
    assert not is_stronger("direct", "direct")


def test_extractors_write_two_of_the_six_and_p6_owns_all_six(p6_conn):
    # Takes `p6_conn` so Task 1's step 4 proves the fixture builds — P1's schema plus
    # P4's three tables — before Task 2 extends it with P6's own.
    #
    # P4 conformance rule 3 / P4 D11: an *observation* may carry only `direct` or
    # `possible`. A *fact* may carry any of the six. The same tuple, two admissible
    # subsets, asserted from both sides — not a comment in a docstring.
    assert EXTRACTOR_RELIABILITY_STATES == ("direct", "possible")
    assert set(EXTRACTOR_RELIABILITY_STATES) < set(STATES)

    observation = by_number(1).observations[0]
    assert observation.reliability == "possible"
    assert validate_observation(observation) == observation

    # Verified live 2026-08-22: P4 raises NotInVocabulary here, not NonConforming.
    with pytest.raises(NotInVocabulary):
        validate_observation(dataclasses.replace(observation, reliability="validated"))

    # And the same word is a rank P6 can ask for.
    assert strength("validated") > strength("llm_supported")
```

```python
# tests/p6/conftest.py
"""P6's fixtures. P1's `tests/conftest.py` supplies `conn` and is not modified.

Nothing here may be imported across parts by name: under pytest's default prepend
import mode, with no `__init__.py` under `tests/`, every `conftest.py` is imported as
the top-level module `conftest` and the last one wins.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema

from evidence_shape.schema import create_evidence_schema

#: §8.5 replays a run and compares it against a prior result, so any test that
#: compares two records must be comparing what the resolver produced and not two
#: readings of the wall clock.
FIXED_OBSERVED_AT = "2026-08-19T14:03:22+00:00"


@pytest.fixture()
def observed_at() -> str:
    return FIXED_OBSERVED_AT


@pytest.fixture()
def p6_conn(conn):
    """P1's database with P4's three tables added. Task 2 extends this fixture with
    P6's own tables and the `fields` catalogue; it is the same shape
    `tests/p4/conftest.py` builds as `p4_conn`."""
    create_schema(conn)
    create_evidence_schema(conn)
    return conn
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/p6/test_p6_authorship.py tests/p6/test_p6_states.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'facts'` — collection fails on both
files before any test runs, because `src/facts/` does not exist. (Verified 2026-08-22:
`ls src/facts` → `No such file or directory`.)

- [ ] **Step 3: Write the implementation**

```python
# src/facts/__init__.py
"""P6 — facts and facets (§3.1–§3.14).

Claims with their evidence attached: four tables (`fields`, `values`, `file_facts`,
`unresolved`) inside P1's single database, three producers writing one fact format
in §8.6's order, and an abstention that is a row rather than a silence.

No path, no destination, no folder and no group column anywhere (§3.14, §4.3).
"""
```

```python
# src/facts/authorship.py
"""P6 authors its two §8.2 events; P1 writes them (M8).

M8 (04-resolutions.md): "The acting part authors; P1 writes. P1 appends no event on
its own initiative." §8.2 requires "the responsible subsystem" on every event, and a
`fact creation` row whose subsystem named P1 or P8 would record that the storage
substrate, or the model harness, wrote the fact table.

Both names are already among §8.2's nineteen reserved types (introspected from
`database_agent.events.RESERVED_EVENT_TYPES`, 2026-08-22), so P6 registers nothing —
registration is a spec-level act (P1 Contract out §3, rule 4).

**Both names carry a space.** `fact_creation` raises `UnregisteredEventType` at run
time rather than at review. This is the same defect class as MINOR 2's `OCR`/`ocr`.

This module is the ONE place `subsystem = "P6"` is written (Task 25 asserts there is
no second). It holds no connection and writes nothing.
"""
from __future__ import annotations

from datetime import datetime, timezone

#: §8.2's "responsible subsystem" for every event this part appends.
SUBSYSTEM = "P6"

#: §8.2's "extractor or model version" field. P1's Done-means 7 requires it
#: populated and `append_event` rejects an empty one. P3's spelling, followed.
COMPONENT_VERSION = "P6/0.1.0"

#: The two reserved §8.2 types P6 authors, in §8.2's order. Spelled with a space,
#: because that is how §8.2 spells them and how P1's frozen table stores them.
AUTHORED_EVENT_TYPES: tuple[str, str] = ("fact creation", "fact rejection")


def event_defaults(**fields) -> dict:
    """Fill §8.2's authorship fields and return the row for P1's `append_event`.

    Writes nothing and holds no connection: P6 authors, and the caller still has to
    decide an event is due and hand it to P1. A caller-supplied `observed_at` wins,
    so §8.5's replay can pin the clock.
    """
    event_type = fields.get("event_type")
    if event_type not in AUTHORED_EVENT_TYPES:
        raise ValueError(
            f"P6 does not author {event_type!r}; it authors {AUTHORED_EVENT_TYPES}. "
            f"Note the space: `fact_creation` is not a registered §8.2 type."
        )
    if fields.get("subsystem", SUBSYSTEM) != SUBSYSTEM:
        raise ValueError(
            f"P6 events name P6 as the responsible subsystem, not "
            f"{fields['subsystem']!r} (M8)"
        )
    return {
        **fields,
        "subsystem": SUBSYSTEM,
        "component_version": COMPONENT_VERSION,
        "observed_at": fields.get(
            "observed_at", datetime.now(timezone.utc).isoformat()
        ),
    }
```

```python
# src/facts/states.py
"""§3.13's six reliability states — P4's tuple, re-exported, never re-spelled.

Preamble rule 2: "There is one `file_facts` table and one set of six reliability
states." §3.5 settles why: "A file fact is not inherently rule-based or LLM-based. It
is the common format into which both systems write their conclusions." The producer
is a column, not a schema.

`STATES` IS `evidence_shape.vocabulary.RELIABILITY_STATES` — the same object, not a
copy, so the two cannot drift. Beside it, **one named constant per state**, spelled
here and nowhere else: every other module imports `DIRECT`, `POSSIBLE`, `VALIDATED`,
`LLM_SUPPORTED`, `USER_CONFIRMED` or `REJECTED`, never a bare literal and never an
index into `STATES`. The §3.13 prose spellings ("LLM-supported", "user
confirmed") are English; a value outside the six is a load error, not a spelling to
normalize.

**Extractors write two of the six; P6 owns all six.** P4 conformance rule 3 (P4 D11)
rejects the other four on an *observation*; `file_facts` accepts all six on a *fact*.
That boundary is asserted from both sides in `tests/p6/test_p6_states.py`.

**`rejected` has no strength.** §3.13: "A rejected fact is a proposal that the user
or validator marked as incorrect." It is an exclusion, not the bottom of a ladder: a
rejected fact that merely ranked below `possible` would be resurfaced by any
comparison that picks the strongest candidate, which is the failure §8.7 names —
"Otherwise the system will repeatedly resurface the same attractive but incorrect
grouping." Asking for its strength raises.
"""
from __future__ import annotations

from evidence_shape.vocabulary import (
    RELIABILITY_STATES as STATES,
    NotInVocabulary,
    check,
)

#: §3.13's six states, one named constant each. This module is the ONE place a state
#: name is spelled; every other module imports the constant. Never a bare literal (a
#: second home for a published vocabulary) and never an index into `STATES` (which is
#: single-homed and unreadable, and silently couples the consumer to the tuple's
#: ORDER -- reorder it and meanings change with no test failing). The repo's own
#: precedent: P5 publishes POTENTIALLY_SENSITIVE, P1 publishes SUPERSEDED_CONTENT.
#: `test_the_six_named_constants_are_exactly_the_six_states` pins each to `STATES`.
USER_CONFIRMED: str = "user_confirmed"
DIRECT: str = "direct"
VALIDATED: str = "validated"
LLM_SUPPORTED: str = "llm_supported"
POSSIBLE: str = "possible"
REJECTED: str = "rejected"

#: §3.13's five ranked states, weakest first, so `strength` is an index and the order
#: is readable in one line. §3.13's own sentence order is strongest-first; the ladder
#: is written the other way round only so that a larger number means a stronger fact.
STRENGTH_ORDER: tuple[str, ...] = (
    POSSIBLE,
    LLM_SUPPORTED,
    VALIDATED,
    DIRECT,
    USER_CONFIRMED,
)

#: The sixth state, named as excluded rather than left out silently.
EXCLUDED_STATE = REJECTED


def strength(state: str) -> int:
    """Where `state` sits on §3.13's ladder. Larger is stronger.

    Raises `NotInVocabulary` for `rejected` (an exclusion, not a rank) and for any
    string that is not one of the six.
    """
    check(state, STATES, name="reliability_state")
    if state == EXCLUDED_STATE:
        raise NotInVocabulary(
            f"{EXCLUDED_STATE!r} is §3.13's exclusion, not a rank: 'a proposal that "
            f"the user or validator marked as incorrect'. Compare membership, never "
            f"strength — a rejected fact that merely ranked below 'possible' would be "
            f"resurfaced by any comparison that picks the strongest candidate (§8.7)."
        )
    return STRENGTH_ORDER.index(state)


def is_stronger(a: str, b: str) -> bool:
    """Strictly stronger on §3.13's ladder. Both arguments must be ranked states."""
    return strength(a) > strength(b)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/p6/test_p6_authorship.py tests/p6/test_p6_states.py -v`
Expected: PASS — 9 passed in `test_p6_authorship.py`, 9 passed in `test_p6_states.py`, 18 total.

- [ ] **Step 5: Run the whole suite and confirm nothing else moved**

Run: `pytest tests/ -q`
Expected: PASS — the 1302 P1–P5 tests still pass, plus 18. `src/facts/` and `tests/p6/` are new
directories; `pyproject.toml` already carries `pythonpath = ["src"]` and `testpaths = ["tests"]`,
so `facts` is importable and `tests/p6/` is collected with no change to any file P6 does not own.

- [ ] **Step 6: Commit**

```bash
git add src/facts/__init__.py src/facts/authorship.py src/facts/states.py tests/p6/conftest.py tests/p6/test_p6_authorship.py tests/p6/test_p6_states.py
git commit -m "feat(P6): the two §8.2 fact events, spelled with a space; §3.13's six states re-exported from P4"
```

---

---

### Task 2: `fields` — the closed catalogue, and the field that cannot be created at runtime

**Files:**
- Create: `src/facts/vocabulary.py`
- Create: `src/facts/fields.py`
- Create: `src/facts/schema.py`
- Modify: `tests/p6/conftest.py`
- Test: `tests/p6/test_p6_fields.py`

> **The skeleton says "modify `src/facts/schema.py`". Nothing creates it earlier**, so Task 2
> creates it. Tasks 3, 4 and 5 then modify it, which is what the skeleton's later "modify" lines
> assume. `create_facts_schema(conn)` is the name three sibling task files already import
> (`PLAN-tasks-07-09.md`, `PLAN-tasks-14-15.md`), and it is honoured unchanged.

**Interfaces:**
- Consumes: `evidence_shape.vocabulary.check`, `evidence_shape.vocabulary.NotInVocabulary`; `database_agent.db.transaction`.
- Produces: `FIELD_SCOPES: tuple[str, ...]` (`universal`, `academic`, `college_applications`, `research`, `finance`, `photos`, `code`), `VALUE_KINDS: tuple[str, ...]`, `UNIVERSAL_FIELDS: tuple[str, ...]`, `ROLE_FIELDS: tuple[str, ...]`, `DOMAIN_FIELDS: Mapping[str, tuple[str, ...]]`, `FIELD_ROWS: tuple[FieldRow, ...]`, `FieldRow(field_key, display_name, scope, value_kind, normalizer_id, destination_eligible, multiplicity)`, `FIELDS_COLUMNS: tuple[str, ...]`, `create_fields(conn) -> None`, `get_field(conn, field_key) -> sqlite3.Row`, `fields_in_scope(conn, scope) -> list[sqlite3.Row]`, `FieldNotInCatalogue`; `facts.schema.create_facts_schema(conn) -> None`.

> **`ROLE_FIELDS` and `VALUE_KINDS` and `FIELDS_COLUMNS` are additions to the skeleton's
> `Produces:` line, not renames.** Nothing the skeleton names is renamed, dropped or re-signatured.
> `ROLE_FIELDS` exists because §3.8's mandatory-`FALSE` rule needs one home rather than four
> literals scattered across the tests that assert it; `VALUE_KINDS` because the `value_kind` column
> is checked through P4's `check` like every other closed vocabulary in this part; `FIELDS_COLUMNS`
> because the column set is asserted from `PRAGMA table_info` and the expected list has to live
> somewhere. No sibling task file binds any of the three.

**Done-means:** 2, and the negative half of 3.

---

#### What the catalogue contains, and how each row was decided

`FIELD_ROWS` is **37 rows**. Its content comes from `planning/domains/canonical_fields.json` — the
R1a canonical field catalogue, 37 keys, another agent's read-only output — with **two changes, each
forced by a ruling that postdates it**:

| | Change | Why |
|---|---|---|
| **−1** | `sensitivity_status` is **withheld** | NEEDS-JOSEPH **C5**, still open: *"Create no such row either way."* See the contradiction recorded below. |
| **+1** | `capture_date` is **added** | Done-means 2(b) and Done-means 5. §3.2: *"an EXIF field called DateTimeOriginal is raw metadata; capture date = 2026-07-17 is the file fact derived from it"*. `canonical_fields.json` does not carry it. |

37 − 1 + 1 = **37**. The two changes cancel in count and not in content; the test asserts the
membership, never the number alone.

**`planning/domains/` is a source to read, not a runtime dependency.** `src/facts/` imports nothing
from it, loads no JSON at import time, and does not read the file at run time. `FIELD_ROWS` is an
authored module-level table, typed out in full below. The skeleton's own table says why: the 574
domain entries are *"a menu someone may one day draw from, entry by entry, with a decision each
time"*, and their own gate currently reports 566 failures. `canonical_fields.json` is the small
grep-verified subset of that work — every one of its `00_cite` strings was re-checked against
`planning/00-database-agent-product-design.md` before this plan was written, and all fifteen
quotations used below returned exactly one match.

**The seven groups, and the design sentence each comes from.** Every one of the six sentences below
was grep-verified verbatim on 2026-08-22 (`grep -cF` → `1`).

| Scope | Design sentence | Keys |
|---|---|---|
| `universal` | §3.11: *"a small shared set of universal file facts, such as file type, creation date, language, duplicate family, version family, and sensitivity status"* | `file_type`, `creation_date`, `language`, `duplicate_family`, `version_family` — **and not** `sensitivity_status` (C5) |
| `universal` | §3.9: *"It may be supported more weakly by a tightly bounded download session"* | `download_session` — P6's one recorded addition (SPEC, *Table: `fields`*) |
| `academic` | §3.11: *"Academic files may use school, term, course, instructor, and work type"* | `school`, `term`, **`subject`**, `instructor`, `work_type` |
| `college_applications` | §3.11: *"College application files may use target university, application cycle, application document type, and purpose"* | `target_university`, `application_cycle`, `application_document_type`, `purpose` |
| `research` | §3.11: *"Research files may use project, stage, artifact type, lab, and venue"* | `project`, `stage`, `artifact_type`, `lab`, `venue` |
| `finance` | §3.11: *"Finance files may use institution, account type, tax year, and record type"* | `institution`, `account_type`, `tax_year`, `record_type` |
| `photos` | §3.11: *"Photos may use capture year, event, location, people, camera information, and media type"* | `capture_year`, `event`, `location`, `people`, `camera_information`, `media_type` — **plus `capture_date`** |
| `code` | §3.11: *"Code files may use project, repository, programming language, and artifact type"* | `repository`, `programming_language` declared here; `project` and `artifact_type` **referenced** from `research` |
| `universal` | §3.8: *"distinct facets, such as authored_by and target_school, or our_firm and client"* | `authored_by`, `target_school`, `our_firm`, `client` |

**Why `subject` and not `course`.** D6, ratified 2026-08-21: the stored academic key is `subject`,
every stored key is `snake_case`, and §3.11's word "course" is the design's prose for the same
field. §3.2's own sentence is *"the system can create facts such as subject = BUSIB 4300"*. A field
key is a join handle, and two spellings are two columns. The catalogue carries a `subject` row and
**no** `course` row; the test asserts both halves. **OQ4 is closed and Task 25's guard inverts.**

**Why `project` and `artifact_type` are one row each, referenced twice.** §3.11 names both under
Research and under Code. `field_key` is unique, so two rows would be two join handles for one
concept — the tie-break rule's exact failure (*"one stored key per concept"*). `canonical_fields.json`
records the same model: *"One global table: schemas REFERENCE these keys and declare no private
spellings."* So the `scope` **column** records where a key is *declared* — Research, the first §3.11
sentence that names it — while `DOMAIN_FIELDS["code"]` **references** it. The two published views
mean different things and the test says so out loud:

- `DOMAIN_FIELDS[scope]` — the §3.11 sentence, literal. `DOMAIN_FIELDS["code"]` has four keys.
- `fields_in_scope(conn, scope)` — the rows *declared* at that scope. `fields_in_scope(conn, "code")`
  has two.

Task 14's `active_field_allowlist` is the consumer that wants the first of these; nothing in this
plan consumes the second except a reviewer checking the catalogue.

**Where `capture_date` sits, and why it is a recorded choice rather than a quotation.** The design
gives it no scope: §3.11's universal list does not name it, and §3.11's Photos row names `capture
year`, not the date. `FIELD_SCOPES` is closed at seven, so the row must take one of them. It is
placed at **`photos`**, on the producer evidence: Done-means 5 ties it to an EXIF `DateTimeOriginal`
observation, which arrives only as `source_type="image"` from `image.metadata` (P5's seam, §2.6). A
universal field is one any file may carry; a file with no capture metadata can never carry this one.
The alternative — `universal` — was rejected because P6's own SPEC says *"Exactly one further
universal field is added here"* and that one is `download_session`. Placing it at `photos` makes the
Photos scope seven rows where §3.11 names six; the test asserts that count explicitly, with this
reason, so the deviation is visible rather than discovered.

`capture_date`, `capture_year` and `creation_date` are **three different fields** and the test
proves it. §3.2 separates the first two from the third by name; the brief's field-naming ruling
separates the first from the second (*"`capture_date` is the EXIF-derived fact … `capture_year` is
the Photos destination dimension"*). `capture_date` is `destination_eligible = FALSE` — the Photos
template's time dimension is the year.

**What is NOT here, and stays not here.** Career and recruiting, identity, medical and legal get
**no field rows**. §5's Career template words (*"company → role or recruiting cycle → document
type"*) name no `fields` row in this catalogue and the test asserts each is absent.

> **D1, narrowed by Joseph 2026-08-21 — what the test may and may not assert.** The clause *"and
> acquiring one fails the test"* is **struck**. The test asserts what the catalogue contains today;
> it does **not** assert that the contents can never change. S3's deferral stands on its own, and
> P6's suite is not where that resolution is held — otherwise a later, deliberate reversal of S3
> would arrive as a regression rather than as a decision. **Do not author career fields**: not here,
> not as domain-catalogue field rows. Career is owed before P10, which is where a destination
> dimension first needs one. Anyone adding one before then is reversing S3 and must say so.

**`document type` is never a key** (brief, field-naming rulings). It is the design's generic word —
twelve uses — for whichever specific field the active domain declares: `application_document_type`
for College applications, `artifact_type` for Research and Code. The test asserts `document_type`
and `document type` are both absent while those two are present.

**`jurisdiction` is a value, never a field name** (D4). The test asserts no key contains it.

---

#### Three contradictions this task hits, resolved in the open

**1. `sensitivity_status`: the SPEC's Done-means 2 and the brief's C5 disagree.**

- SPEC Done-means 2: *"All six universal fields … are present, and no field outside them."*
- Brief §7, NEEDS-JOSEPH **C5**: *"whether P6 keeps a `sensitivity_status` field row. P7's SPEC
  Contract-in says 'P6 must accept `sensitivity` as a first-class universal field'; D2 makes P7's
  record authoritative; round 1 found the field has no producer. **Create no such row either way.**"*
- Skeleton, Task 2 note on D2: *"Round 1 F-2 found it has no producer. Create no such row until asked."*

**Resolved for the brief, which is binding and later.** The catalogue carries **five** §3.11
universal keys, not six. Done-means 2's "all six" is therefore **not satisfied by this task**, and
that is deliberate: C5 is open, D2 makes P7's `ClassificationRecord` authoritative and
`files.sensitivity_state` its projection, and a field row with no producer would be a column
somebody later writes into from the wrong side. The test asserts the **absence** and names C5, so
the day Joseph answers, one row and one assertion change together. **Do not "fix" Done-means 2 by
adding the row.**

**2. `destination_eligible` for `target_school` and `client`: the skeleton and `canonical_fields.json`
disagree.**

- Skeleton, Task 2: *"every one of the four is `destination_eligible = FALSE`"*, quoting §3.8's
  *"It should avoid using authorship or creator identity as a destination dimension"*.
- `canonical_fields.json` marks `target_school` **true** and `client` **true**, reasoning that the
  §3.8 sentence binds the authorship side only and that §3.8 *"places a document's purpose, project,
  subject, or target above its authorship"*.

**Resolved for D9**, which overrules both the skeleton and the earlier "all four FALSE" reading.
Authorship is never destination-eligible (`authored_by`, and `our_firm` as the firm-side identity).
`target_school` and `client` **are** destination-eligible: they are targets, not authorship.
D8: the stored key is `target_school`, not a second `target_university` key. The catalogue may still
list both with a NEEDS-JOSEPH note; this task stores `target_school`.

**3. `value_kind` cannot carry the SPEC's "date/term" obligation.** The SPEC's column comment is
*"how this field's values normalize; date/term fields must use §3.10 rules"*, but
`canonical_fields.json` types `term` as `string`, not as a term kind. Rather than invent a fifth
`value_kind` member, `VALUE_KINDS` is exactly the four kinds that file uses — `string`, `date`,
`identifier`, `enum` — and the §3.10 obligation stays where it is enforceable: Task 10's `dates.py`,
keyed on the field, with its three required injected patterns. The gap is named, not closed here.

**`normalizer_id` and `multiplicity` are `NULL` on every row, and that is the answer.**
Per-field normalizers are a **Deferred** row in the SPEC (*"`U Chicago` → `University of Chicago` →
`UChicago` is one worked example, not a table"*), and round 4's C-5 has P8's Contract-in naming
`normalize(field, raw_value)` as P6's while P6 Task 17 disowns it — each part hands it to the other,
so neither builds it. **OQ6** (multiplicity) is Joseph's: *"May one (file, field) hold several
simultaneously active values, and if so how does the §3.7 margin rule apply?"* Both columns exist so
a later answer has somewhere to land; both are unanswered, and the test asserts they are unanswered
rather than asserting a guess.

**A trap for Task 4's author, stated here because this is where the column is born.** Task 4's
`FORBIDDEN_COLUMN_SUBSTRINGS` check must **not** be run against `fields`: the column
`destination_eligible` contains the substring `destination`. §3.14's negative contract is about the
**fact** row carrying no path, destination, folder or group — not about the catalogue declaring
which fields may ever become a folder level. Applying the same guard to both tables would fail on a
column §3.8 requires.

---

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_fields.py
"""§3.12's closed catalogue: the LLM may create values, never fields.

Done-means 2 and the negative half of Done-means 3.
"""
import re

import pytest

from evidence_shape.vocabulary import NotInVocabulary

from facts.fields import (
    DOMAIN_FIELDS, FIELDS_COLUMNS, FIELD_ROWS, FIELD_SCOPES, ROLE_FIELDS,
    UNIVERSAL_FIELDS, VALUE_KINDS, FieldNotInCatalogue, create_fields,
    fields_in_scope, get_field,
)

KEYS = tuple(row.field_key for row in FIELD_ROWS)


def test_the_catalogue_is_thirty_seven_rows_with_no_duplicate_key():
    assert len(FIELD_ROWS) == 37
    assert len(set(KEYS)) == 37


def test_the_catalogue_is_exactly_these_keys_and_nothing_else():
    # §3.11's six sentences + §3.9's download session + §3.8's four roles +
    # capture_date (Done-means 2(b)), minus sensitivity_status (NEEDS-JOSEPH C5).
    assert set(KEYS) == {
        # universal (§3.11, five of six — see C5 below)
        "file_type", "creation_date", "language", "duplicate_family", "version_family",
        # universal (§3.9, P6's one recorded addition)
        "download_session",
        # academic (§3.11)
        "school", "term", "subject", "instructor", "work_type",
        # college applications (§3.11)
        "target_university", "application_cycle", "application_document_type", "purpose",
        # research (§3.11)
        "project", "stage", "artifact_type", "lab", "venue",
        # finance (§3.11)
        "institution", "account_type", "tax_year", "record_type",
        # photos (§3.11), plus §3.2's capture_date
        "capture_year", "event", "location", "people", "camera_information",
        "media_type", "capture_date",
        # code (§3.11) — project and artifact_type are declared under research
        "repository", "programming_language",
        # §3.8's four role fields
        "authored_by", "target_school", "our_firm", "client",
    }


def test_the_three_published_groups_partition_the_catalogue():
    referenced = {key for keys in DOMAIN_FIELDS.values() for key in keys}
    assert set(UNIVERSAL_FIELDS) | set(ROLE_FIELDS) | referenced == set(KEYS)
    assert not set(UNIVERSAL_FIELDS) & set(ROLE_FIELDS)


def test_every_key_is_snake_case():
    # D6: "every stored field key is snake_case".
    for key in KEYS:
        assert re.fullmatch(r"[a-z][a-z0-9_]*", key), key


def test_the_academic_key_is_subject_and_there_is_no_course_row():
    # D6, ratified 2026-08-21. §3.2: "the system can create facts such as
    # subject = BUSIB 4300". §3.11's word "course" is prose for the same field and
    # survives inside quotations only. Two spellings would be two join handles.
    assert "subject" in KEYS
    assert "course" not in KEYS
    assert "course_code" not in KEYS
    assert DOMAIN_FIELDS["academic"] == ("school", "term", "subject", "instructor",
                                         "work_type")
    assert all(row.display_name != "course" for row in FIELD_ROWS)


def test_sensitivity_status_has_no_row_because_C5_is_open():
    # NEEDS-JOSEPH C5. P7's SPEC Contract-in wants `sensitivity` as a first-class
    # universal field; D2 makes P7's ClassificationRecord authoritative and
    # `files.sensitivity_state` its projection; round 1 F-2 found the field has no
    # producer. The brief: "Create no such row either way."
    #
    # This is knowingly at odds with SPEC Done-means 2 ("all six universal fields").
    # Do not close it by adding the row.
    for spelling in ("sensitivity_status", "sensitivity", "sensitivity_state"):
        assert spelling not in KEYS
    assert len([k for k in UNIVERSAL_FIELDS if k != "download_session"]) == 5


def test_document_type_is_never_a_key():
    # The design's generic word (twelve uses) for whichever field the active domain
    # declares. The specific ones are keys; the generic one is not.
    assert "document_type" not in KEYS
    assert "document type" not in KEYS
    assert "application_document_type" in KEYS
    assert "artifact_type" in KEYS


def test_jurisdiction_is_a_value_and_never_a_field_name():
    # D4: "jurisdiction is a value, never a field name and never a destination
    # dimension."
    assert not [k for k in KEYS if "jurisdiction" in k]


def test_career_identity_medical_and_legal_have_no_field_rows():
    # §5's Career template words are "company → role or recruiting cycle → document
    # type"; none of them is a `fields` row. S3 deferred those schemas.
    #
    # D1 (narrowed 2026-08-21): this asserts the catalogue's contents today. It does
    # NOT assert that the contents can never change — a later deliberate reversal of
    # S3 is a decision, not a regression, and P6's suite is not where it is held.
    for absent in ("company", "role", "recruiting_cycle", "job_title", "employer",
                   "resume_version", "passport_number", "identity_document_type",
                   "patient", "diagnosis", "medical_record_type",
                   "matter", "case_number", "counterparty"):
        assert absent not in KEYS


def test_the_four_3_8_role_fields_exist_and_d9_splits_destination_eligibility():
    # §3.8: "distinct facets, such as authored_by and target_school, or our_firm and
    # client" — the design's own spelling, underscores included.
    #
    # D9: authorship is never destination-eligible; target_school and client ARE.
    # Round 1's F-1: Done-means 13 and 22 both require `authored_by` to exist, so a
    # catalogue without these four made two of the SPEC's own Done-means unwritable.
    assert ROLE_FIELDS == ("authored_by", "target_school", "our_firm", "client")
    for key in ROLE_FIELDS:
        row = next(r for r in FIELD_ROWS if r.field_key == key)
        assert row.scope == "universal", key
    assert get_row("authored_by").destination_eligible is False
    assert get_row("our_firm").destination_eligible is False
    assert get_row("target_school").destination_eligible is True
    assert get_row("client").destination_eligible is True


def test_the_application_target_is_destination_eligible_under_its_3_11_spelling():
    # §3.11's College-applications row names "target university" as a dimension, so
    # target_university IS eligible. target_school is §3.8's spelling of the same
    # concept, held as a key referenced by no domain until the ROSTER NEEDS-JOSEPH
    # about folding the two is answered.
    assert get_row("target_university").destination_eligible is True
    assert "target_school" not in DOMAIN_FIELDS["college_applications"]


def test_capture_date_capture_year_and_creation_date_are_three_fields():
    # Brief, field-naming rulings: capture_date is §3.2's EXIF-derived fact
    # ("capture date = 2026-07-17 is the file fact derived from it"); capture_year is
    # §3.11's Photos destination dimension; creation_date is what §3.2 separates both
    # from by name.
    assert {"capture_date", "capture_year", "creation_date"} <= set(KEYS)
    assert get_row("capture_date").value_kind == "date"
    assert get_row("capture_date").destination_eligible is False
    assert get_row("capture_year").destination_eligible is True
    assert get_row("creation_date").scope == "universal"
    assert get_row("capture_date").scope == "photos"


def test_the_photos_scope_carries_seven_rows_and_the_reason_is_recorded():
    # §3.11 names six. capture_date is the seventh: the design gives it no scope,
    # FIELD_SCOPES is closed at seven members, and its only producer is an EXIF
    # DateTimeOriginal observation (Done-means 5), which arrives only for an image.
    assert DOMAIN_FIELDS["photos"] == ("capture_year", "event", "location", "people",
                                       "camera_information", "media_type",
                                       "capture_date")


def test_download_session_is_universal_and_never_a_folder_level():
    # §3.9: "It may be supported more weakly by a tightly bounded download session."
    # A session is a purpose clue and a review aid, never proof of topic.
    row = get_row("download_session")
    assert row.scope == "universal"
    assert row.destination_eligible is False
    assert "download_session" in UNIVERSAL_FIELDS


def test_the_seven_scopes_are_the_specs_seven_and_every_row_uses_one():
    assert FIELD_SCOPES == ("universal", "academic", "college_applications",
                            "research", "finance", "photos", "code")
    for row in FIELD_ROWS:
        assert row.scope in FIELD_SCOPES, row.field_key
        assert row.value_kind in VALUE_KINDS, row.field_key


def test_project_and_artifact_type_are_one_row_each_referenced_by_two_domains():
    # canonical_fields.json's own model: "One global table: schemas REFERENCE these
    # keys and declare no private spellings." Two rows would be two join handles for
    # one concept — the tie-break rule's exact failure.
    assert DOMAIN_FIELDS["research"] == ("project", "stage", "artifact_type", "lab",
                                         "venue")
    assert DOMAIN_FIELDS["code"] == ("project", "repository", "programming_language",
                                     "artifact_type")
    assert get_row("project").scope == "research"
    assert get_row("artifact_type").scope == "research"
    assert len([r for r in FIELD_ROWS if r.field_key == "project"]) == 1


def test_no_normalizer_and_no_multiplicity_is_answered_anywhere():
    # Per-field normalizers are a Deferred SPEC row, and round 4's C-5 has P6 and P8
    # each handing `normalize(field, raw_value)` to the other. OQ6 (multiplicity) is
    # Joseph's. Both columns exist so an answer has somewhere to land.
    assert all(row.normalizer_id is None for row in FIELD_ROWS)
    assert all(row.multiplicity is None for row in FIELD_ROWS)


def test_the_module_publishes_no_way_to_add_a_field_at_runtime(p6_conn):
    # §3.12: "The system may create new values when it sees a new course, project,
    # company, university, or event, but it should not invent new fields
    # automatically." §3.5: "The LLM is not allowed to invent a new fact schema,
    # create an unsupported field, or make a free-form filing decision."
    #
    # Runtime introspection of the module namespace, not a source-text search: a text
    # search matches comments and docstrings.
    import facts.fields as module
    forbidden = ("add_field", "create_field", "register_field", "new_field",
                 "ensure_field", "upsert_field")
    assert not [n for n in vars(module) if n in forbidden]
    assert not [n for n, v in vars(module).items()
                if callable(v) and n.lower().endswith("_field")
                and n not in ("get_field",)]


def test_an_unknown_field_key_raises_rather_than_creating_a_row(p6_conn):
    before = p6_conn.execute("SELECT count(*) FROM fields").fetchone()[0]
    with pytest.raises(FieldNotInCatalogue):
        get_field(p6_conn, "vibe")
    with pytest.raises(FieldNotInCatalogue):
        get_field(p6_conn, "course")          # D6: prose, not a key
    with pytest.raises(FieldNotInCatalogue):
        get_field(p6_conn, "sensitivity_status")   # C5: open, so no row
    assert p6_conn.execute("SELECT count(*) FROM fields").fetchone()[0] == before


def test_create_fields_loads_the_authored_table_and_is_idempotent(p6_conn):
    # `p6_conn` has already called it once.
    assert p6_conn.execute("SELECT count(*) FROM fields").fetchone()[0] == 37
    create_fields(p6_conn)
    create_fields(p6_conn)
    assert p6_conn.execute("SELECT count(*) FROM fields").fetchone()[0] == 37


def test_the_stored_row_carries_exactly_the_specs_columns(p6_conn):
    # Read from the database, so a future column fails the test the day it is added.
    # NOTE for Task 4: `destination_eligible` contains the substring "destination".
    # §3.14's forbidden-substring guard is for `file_facts` and `unresolved`; running
    # it against `fields` would fail on a column §3.8 requires.
    stored = tuple(r[1] for r in p6_conn.execute("PRAGMA table_info(fields)"))
    assert stored == FIELDS_COLUMNS
    assert FIELDS_COLUMNS == ("field_key", "display_name", "scope",
                              "value_kind", "normalizer_id", "destination_eligible",
                              "multiplicity")
    # brief §17: one concept, one name. A second identifier column holding the same
    # string is the defect this rule exists to stop, so its ABSENCE is asserted --
    # not the equality of two columns, which is what an earlier draft tested.
    assert "field_id" not in stored, (
        "`field_id` was the skeleton's name for the field key; brief §17 ruled the "
        "column is `field_key` and holds the key. Two columns is not the fix.")


def test_the_row_identity_is_the_field_key(p6_conn):
    # SPEC: "field_key — stable identifier". Task 3's `values.field_key` joins on it.
    # One identity, one name.
    row = get_field(p6_conn, "subject")
    assert row["field_key"] == "subject"
    assert row["display_name"] == "subject"
    assert row["scope"] == "academic"
    assert row["value_kind"] == "string"
    assert row["normalizer_id"] is None
    assert row["multiplicity"] is None
    assert row["destination_eligible"] == 1


def test_fields_in_scope_returns_the_rows_declared_at_that_scope(p6_conn):
    # `fields_in_scope` answers "declared here"; `DOMAIN_FIELDS` answers "referenced
    # by this §3.11 sentence". They differ for exactly the two shared keys.
    assert [r["field_key"] for r in fields_in_scope(p6_conn, "code")] == [
        "repository", "programming_language"]
    assert [r["field_key"] for r in fields_in_scope(p6_conn, "finance")] == [
        "institution", "account_type", "tax_year", "record_type"]
    assert [r["field_key"] for r in fields_in_scope(p6_conn, "universal")] == [
        "file_type", "creation_date", "language", "duplicate_family",
        "version_family", "download_session",
        "authored_by", "target_school", "our_firm", "client"]
    assert len(fields_in_scope(p6_conn, "photos")) == 7


def test_fields_in_scope_refuses_a_scope_outside_the_seven(p6_conn):
    for absent in ("career", "identity", "medical", "legal", "Universal"):
        with pytest.raises(NotInVocabulary):
            fields_in_scope(p6_conn, absent)


def test_every_destination_eligible_flag_round_trips_as_a_boolean(p6_conn):
    for row in FIELD_ROWS:
        stored = get_field(p6_conn, row.field_key)
        assert bool(stored["destination_eligible"]) is row.destination_eligible


def get_row(field_key):
    return next(r for r in FIELD_ROWS if r.field_key == field_key)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/p6/test_p6_fields.py -v`
Expected: FAIL — collection fails with
`ModuleNotFoundError: No module named 'facts.fields'`. (`src/facts/` exists after Task 1; `fields.py`
does not.)

- [ ] **Step 3: Write the implementation**

```python
# src/facts/vocabulary.py
"""P6's own closed vocabularies, published once, checked through P4's `check`.

Global constraint: "`unresolved` reasons and `origin` values are P6's own closed
vocabularies, published once, in one module, checked with P4's
`evidence_shape.vocabulary.check(value, vocabulary, *, name)` so a bad value raises
`NotInVocabulary` rather than being stored."

The six reliability states are NOT here — they are P4's, re-exported by
`facts.states`, and a second copy is what preamble rule 2 forbids.

Task 5 adds `UNRESOLVED_REASONS` and `ATTEMPTED_PRODUCERS` to this module.
"""
from __future__ import annotations

#: §3.11's six domain families plus the universal scope. Exactly the SPEC's list, in
#: the SPEC's order. Adding a member is a contract revision: §3.15 names Career and
#: recruiting, identity, medical and legal, and §3.11 gives them no field row, so
#: they are Deferred rather than empty scopes (S3).
FIELD_SCOPES: tuple[str, ...] = (
    "universal",
    "academic",
    "college_applications",
    "research",
    "finance",
    "photos",
    "code",
)

#: How a field's values normalize (SPEC, `fields` table). Exactly the four kinds
#: `planning/domains/canonical_fields.json` uses; P6 invents no fifth.
#:
#: The SPEC's column comment adds "date/term fields must use §3.10 rules", but that
#: file types `term` as `string`. Rather than mint a `term` kind the design does not
#: name, the §3.10 obligation stays in `facts.dates`, keyed on the field, with its
#: injected patterns. The gap is named in the plan, not closed here.
VALUE_KINDS: tuple[str, ...] = ("string", "date", "identifier", "enum")
```

```python
# src/facts/schema.py
"""P6's tables, created inside P1's single local database (§0).

P6 owns four — `fields`, `values`, `file_facts`, `unresolved` — and creates none of
anyone else's. `database_agent.db.create_schema` and
`evidence_shape.schema.create_evidence_schema` are separate calls and are never
invoked from here.

Task 2 creates `fields`. Tasks 3, 4 and 5 add their own DDL to `_TABLE_DDL`.
"""
from __future__ import annotations

import sqlite3

from database_agent.db import transaction

#: The `fields` catalogue (SPEC, Table: `fields`). `field_key` is the SPEC's
#: "stable identifier" and the ONLY identifier this table has. An earlier draft
#: carried `field_id` beside it holding the identical string, to satisfy the
#: skeleton and the SPEC at once; brief §17 overruled that -- one concept wears one
#: name -- so the second column is gone rather than kept in sync. `field_key` is the
#: PRIMARY KEY, which is also what Task 3's `REFERENCES fields (field_key)` needs:
#: `PRAGMA foreign_keys` is ON and an FK to a non-PK/UNIQUE parent raises
#: `foreign key mismatch` at INSERT, not at DDL.
#:
#: `destination_eligible` is INTEGER because SQLite has no boolean; `create_fields`
#: writes 0/1 and the reader coerces with `bool()`.
#:
#: `normalizer_id` and `multiplicity` are nullable and NULL on every authored row:
#: per-field normalizers are a Deferred SPEC row, and multiplicity is open question 6.
_FIELDS_DDL = """
CREATE TABLE IF NOT EXISTS fields (
    field_key            TEXT PRIMARY KEY,
    display_name         TEXT NOT NULL,
    scope                TEXT NOT NULL,
    value_kind           TEXT NOT NULL,
    normalizer_id        TEXT,
    destination_eligible INTEGER NOT NULL,
    multiplicity         TEXT
)
"""

_TABLE_DDL: tuple[str, ...] = (_FIELDS_DDL,)


def create_facts_schema(conn: sqlite3.Connection) -> None:
    """Create P6's tables. Idempotent; creates no other part's table."""
    with transaction(conn):
        for ddl in _TABLE_DDL:
            conn.execute(ddl)
```

```python
# src/facts/fields.py
"""§3.12's closed field catalogue: values may auto-create, fields may not.

§3.12: "The system may create new values when it sees a new course, project, company,
university, or event, but it should not invent new fields automatically."
§3.5: "The LLM is not allowed to invent a new fact schema, create an unsupported
field, or make a free-form filing decision."

So the write path is this module-level authored table, loaded by `create_fields`.
There is no `add_field`, no `register_field`, and no path on which a producer — rules,
the LLM seam, or a user correction — inserts a `fields` row. `get_field` raises
`FieldNotInCatalogue` for an unknown key, which is what makes an unknown field a
refusal rather than a schema change.

**`planning/domains/` is not this catalogue and is never imported.** That directory is
a research artifact of 574 proposed entries. This table's content was READ from
`planning/domains/canonical_fields.json` (37 grep-verified canonical keys) when the
plan was written, with two changes forced by later rulings: `sensitivity_status` is
withheld (NEEDS-JOSEPH C5, open) and `capture_date` is added (Done-means 2(b), §3.2).
Nothing here loads a file at import time or at run time.

**The scope column records where a key is DECLARED; `DOMAIN_FIELDS` records which
§3.11 sentence REFERENCES it.** §3.11 names `project` and `artifact type` under both
Research and Code, and one concept gets one stored key (the tie-break rule), so those
two are declared at `research` and referenced by `code`.

**Every field a §3.8 role names is `destination_eligible = False`.** §3.8: "It should
avoid using authorship or creator identity as a destination dimension."
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from evidence_shape.vocabulary import check

from database_agent.db import transaction

from facts.schema import create_facts_schema
from facts.vocabulary import FIELD_SCOPES, VALUE_KINDS

__all__ = [
    "DOMAIN_FIELDS", "FIELDS_COLUMNS", "FIELD_ROWS", "FIELD_SCOPES", "ROLE_FIELDS",
    "UNIVERSAL_FIELDS", "VALUE_KINDS", "FieldNotInCatalogue", "FieldRow",
    "create_fields", "fields_in_scope", "get_field",
]


class FieldNotInCatalogue(KeyError):
    """A producer named a field §3.12 does not let it create.

    Raised instead of inserting a row: "it should not invent new fields
    automatically" is enforced by there being no code that could.
    """


@dataclass(frozen=True, slots=True)
class FieldRow:
    """One row of the catalogue, in the SPEC's column order."""

    field_key: str
    display_name: str
    scope: str
    value_kind: str
    normalizer_id: str | None
    destination_eligible: bool
    multiplicity: str | None


#: The stored columns, asserted against `PRAGMA table_info(fields)`.
FIELDS_COLUMNS: tuple[str, ...] = (
    "field_key", "display_name", "scope", "value_kind",
    "normalizer_id", "destination_eligible", "multiplicity",
)


def _row(field_key: str, display_name: str, scope: str, value_kind: str,
         destination_eligible: bool) -> FieldRow:
    """One catalogue row. `normalizer_id` and `multiplicity` are NULL on every row:
    per-field normalizers are Deferred and multiplicity is open question 6."""
    return FieldRow(field_key=field_key, display_name=display_name, scope=scope,
                    value_kind=value_kind, normalizer_id=None,
                    destination_eligible=destination_eligible, multiplicity=None)


#: §3.11: "a small shared set of universal file facts, such as file type, creation
#: date, language, duplicate family, version family, and sensitivity status".
#:
#: FIVE of that six are here. `sensitivity_status` is WITHHELD: NEEDS-JOSEPH C5 is
#: open (P7's SPEC wants it first-class; D2 makes P7's ClassificationRecord
#: authoritative and `files.sensitivity_state` its projection; round 1 F-2 found the
#: field has no producer), and the instruction is to create no such row either way.
#: This is knowingly at odds with SPEC Done-means 2's "all six"; do not close it by
#: adding the row.
_UNIVERSAL_3_11: tuple[FieldRow, ...] = (
    _row("file_type", "file type", "universal", "string", False),
    _row("creation_date", "creation date", "universal", "date", False),
    _row("language", "language", "universal", "string", False),
    _row("duplicate_family", "duplicate family", "universal", "identifier", False),
    _row("version_family", "version family", "universal", "identifier", False),
)

#: P6's one recorded addition to the universal list. §3.9: "It may be supported more
#: weakly by a tightly bounded download session." §4.2 requires it retrievable. It is
#: not `purpose` — the session names no purpose value — and it is never a folder
#: level, because a session is a clue and a review aid, not proof of topic.
_DOWNLOAD_SESSION: tuple[FieldRow, ...] = (
    _row("download_session", "download session", "universal", "identifier", False),
)

#: §3.8: "distinct facets, such as authored_by and target_school, or our_firm and
#: client" — the design's own spelling, underscores included, so `display_name` keeps
#: it rather than inventing English the design does not use.
#:
#: D9: authorship (`authored_by`, and `our_firm` as firm-side identity) is never
#: destination-eligible. `target_school` and `client` ARE — they are targets, not
#: authorship. D8: the stored key is `target_school`.
#:
#: They take `scope = "universal"`: no §3.11 domain sentence names any of them, and
#: FIELD_SCOPES has no eighth member to hold them. `authored_by` in particular is
#: produced from document metadata on any file, in any domain (§3.8's demotion tier).
_ROLES_3_8: tuple[FieldRow, ...] = (
    _row("authored_by", "authored_by", "universal", "string", False),
    _row("target_school", "target_school", "universal", "string", True),
    _row("our_firm", "our_firm", "universal", "string", False),
    _row("client", "client", "universal", "string", True),
)

#: §3.11: "Academic files may use school, term, course, instructor, and work type."
#: D6: the stored key is `subject`; "course" is the design's prose for the same field
#: and survives inside quotations only. §3.2: "the system can create facts such as
#: subject = BUSIB 4300."
#:
#: `instructor` is not destination-eligible: §3.11's Academic template is school →
#: term → course → work type, and §3.8 disfavours person-identity collectors.
_ACADEMIC: tuple[FieldRow, ...] = (
    _row("school", "school", "academic", "string", True),
    _row("term", "term", "academic", "string", True),
    _row("subject", "subject", "academic", "string", True),
    _row("instructor", "instructor", "academic", "string", False),
    _row("work_type", "work type", "academic", "enum", True),
)

#: §3.11: "College application files may use target university, application cycle,
#: application document type, and purpose."
#:
#: `purpose` stays exactly where that sentence puts it. No per-domain `purpose` clone
#: is minted; a purpose-coherent packet outside admissions activates the nearest
#: schema on its own evidence or falls through to residual.
_COLLEGE_APPLICATIONS: tuple[FieldRow, ...] = (
    _row("target_university", "target university", "college_applications", "string", True),
    _row("application_cycle", "application cycle", "college_applications", "string", True),
    _row("application_document_type", "application document type",
         "college_applications", "enum", True),
    _row("purpose", "purpose", "college_applications", "string", True),
)

#: §3.11: "Research files may use project, stage, artifact type, lab, and venue."
#: `project` and `artifact_type` are DECLARED here and REFERENCED by `code`.
_RESEARCH: tuple[FieldRow, ...] = (
    _row("project", "project", "research", "string", True),
    _row("stage", "stage", "research", "string", True),
    _row("artifact_type", "artifact type", "research", "enum", True),
    _row("lab", "lab", "research", "string", True),
    _row("venue", "venue", "research", "string", True),
)

#: §3.11: "Finance files may use institution, account type, tax year, and record type."
_FINANCE: tuple[FieldRow, ...] = (
    _row("institution", "institution", "finance", "string", True),
    _row("account_type", "account type", "finance", "string", True),
    _row("tax_year", "tax year", "finance", "string", True),
    _row("record_type", "record type", "finance", "enum", True),
)

#: §3.11: "Photos may use capture year, event, location, people, camera information,
#: and media type."
#:
#: Plus `capture_date`, which the design gives no scope. §3.2: "an EXIF field called
#: DateTimeOriginal is raw metadata; capture date = 2026-07-17 is the file fact
#: derived from it." Its only producer is an image-metadata observation, so it is
#: declared here rather than as an eighth universal field; the Photos template's time
#: dimension is `capture_year`, so the date itself is not destination-eligible.
#:
#: `people` and `camera_information` are not destination-eligible: §3.11's Photos
#: template is year → event, and person-folders are privacy-loaded (§8.4). Widening
#: either is Joseph's call, never a schema's.
_PHOTOS: tuple[FieldRow, ...] = (
    _row("capture_year", "capture year", "photos", "string", True),
    _row("event", "event", "photos", "string", True),
    _row("location", "location", "photos", "string", True),
    _row("people", "people", "photos", "string", False),
    _row("camera_information", "camera information", "photos", "string", False),
    _row("media_type", "media type", "photos", "enum", True),
    _row("capture_date", "capture date", "photos", "date", False),
)

#: §3.11: "Code files may use project, repository, programming language, and artifact
#: type." `project` and `artifact_type` are declared under Research.
#:
#: `programming_language` is not destination-eligible: the design treats code projects
#: as structural units whose existing layout is preserved, and scattering a project by
#: language would break that.
_CODE: tuple[FieldRow, ...] = (
    _row("repository", "repository", "code", "string", True),
    _row("programming_language", "programming language", "code", "string", False),
)

#: The catalogue, in declaration order. Thirty-seven rows.
FIELD_ROWS: tuple[FieldRow, ...] = (
    *_UNIVERSAL_3_11,
    *_DOWNLOAD_SESSION,
    *_ROLES_3_8,
    *_ACADEMIC,
    *_COLLEGE_APPLICATIONS,
    *_RESEARCH,
    *_FINANCE,
    *_PHOTOS,
    *_CODE,
)

#: §3.11's universal list (five of six, C5) plus §3.9's download session.
UNIVERSAL_FIELDS: tuple[str, ...] = tuple(
    row.field_key for row in (*_UNIVERSAL_3_11, *_DOWNLOAD_SESSION)
)

#: §3.8's four role fields.
ROLE_FIELDS: tuple[str, ...] = tuple(row.field_key for row in _ROLES_3_8)

#: §3.11's six domain sentences, literal — the keys each REFERENCES, which is not the
#: same question as which scope declares them. `project` and `artifact_type` appear
#: under two domains and are one row each.
DOMAIN_FIELDS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "academic": tuple(row.field_key for row in _ACADEMIC),
    "college_applications": tuple(row.field_key for row in _COLLEGE_APPLICATIONS),
    "research": tuple(row.field_key for row in _RESEARCH),
    "finance": tuple(row.field_key for row in _FINANCE),
    "photos": tuple(row.field_key for row in _PHOTOS),
    "code": ("project", "repository", "programming_language", "artifact_type"),
})


def create_fields(conn: sqlite3.Connection) -> None:
    """Load the authored catalogue. Idempotent, and the only writer of this table.

    There is deliberately no counterpart that adds a row (§3.12, §3.5). A drifted
    row raises `NotInVocabulary` through P4's `check` rather than being stored.
    """
    create_facts_schema(conn)
    with transaction(conn):
        for row in FIELD_ROWS:
            check(row.scope, FIELD_SCOPES, name="field scope")
            check(row.value_kind, VALUE_KINDS, name="value_kind")
            conn.execute(
                "INSERT OR IGNORE INTO fields (field_key, display_name, "
                "scope, value_kind, normalizer_id, destination_eligible, "
                "multiplicity) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (row.field_key, row.display_name, row.scope,
                 row.value_kind, row.normalizer_id,
                 1 if row.destination_eligible else 0, row.multiplicity),
            )


def get_field(conn: sqlite3.Connection, field_key: str) -> sqlite3.Row:
    """The catalogue row for `field_key`.

    Raises `FieldNotInCatalogue` for anything else — including `course` (D6: prose,
    not a key), `target_university` (D8: prose for `target_school`) and
    `sensitivity_status` (**D7**: P7's `ClassificationRecord` is the sole home; P6
    creates no such row. The old citation here was C5, which is a different question
    — brief §14).
    """
    row = conn.execute(
        "SELECT * FROM fields WHERE field_key = ?", (field_key,)
    ).fetchone()
    if row is None:
        raise FieldNotInCatalogue(
            f"{field_key!r} is not in the field catalogue. §3.12: the system 'should "
            f"not invent new fields automatically'; §3.5: the LLM may not 'create an "
            f"unsupported field'. Adding one is a design decision, not a write."
        )
    return row


def fields_in_scope(conn: sqlite3.Connection, scope: str) -> list[sqlite3.Row]:
    """The rows DECLARED at `scope`, in catalogue order.

    Not the same question as `DOMAIN_FIELDS[scope]`, which is the §3.11 sentence's
    own list: `project` and `artifact_type` are declared at `research` and referenced
    by `code`, so `fields_in_scope(conn, "code")` returns two rows where
    `DOMAIN_FIELDS["code"]` names four.
    """
    check(scope, FIELD_SCOPES, name="field scope")
    return list(conn.execute(
        "SELECT * FROM fields WHERE scope = ? ORDER BY rowid", (scope,)
    ))
```

```python
# tests/p6/conftest.py   — MODIFY: extend `p6_conn` with P6's tables and catalogue
"""P6's fixtures. P1's `tests/conftest.py` supplies `conn` and is not modified.

Nothing here may be imported across parts by name: under pytest's default prepend
import mode, with no `__init__.py` under `tests/`, every `conftest.py` is imported as
the top-level module `conftest` and the last one wins.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema

from evidence_shape.schema import create_evidence_schema

from facts.fields import create_fields

#: §8.5 replays a run and compares it against a prior result, so any test that
#: compares two records must be comparing what the resolver produced and not two
#: readings of the wall clock.
FIXED_OBSERVED_AT = "2026-08-19T14:03:22+00:00"


@pytest.fixture()
def observed_at() -> str:
    return FIXED_OBSERVED_AT


@pytest.fixture()
def p6_conn(conn):
    """P1's database with P4's three tables, P6's own tables, and the `fields`
    catalogue loaded — the same shape `tests/p4/conftest.py` builds as `p4_conn`.

    `create_fields` calls `create_facts_schema` itself, so there is no ordering trap
    for a test that only wants the catalogue.
    """
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    return conn
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/p6/test_p6_fields.py -v`
Expected: PASS — 25 passed.

- [ ] **Step 5: Re-run Task 1's tests against the extended fixture**

Run: `pytest tests/p6/ -v`
Expected: PASS — 42 passed (17 from Task 1, 25 here).
`tests/p6/test_p6_states.py::test_extractors_write_two_of_the_six_and_p6_owns_all_six` takes
`p6_conn`, which now also creates P6's tables and loads the catalogue; nothing in that test reads
`fields`, so it is unaffected. `test_no_module_in_facts_publishes_a_second_copy_of_the_six` now
walks five modules instead of two — `authorship`, `fields`, `schema`, `states`, `vocabulary`, of
which four are inspected because `states` is skipped by name — and must still report no offender:
`FIELD_SCOPES` and `VALUE_KINDS` are collections of strings, and neither is the six.

- [ ] **Step 6: Run the whole suite**

Run: `pytest tests/ -q`
Expected: PASS — the 1302 P1–P5 tests, plus 42.

- [ ] **Step 7: Commit**

```bash
git add src/facts/vocabulary.py src/facts/fields.py src/facts/schema.py tests/p6/conftest.py tests/p6/test_p6_fields.py
git commit -m "feat(P6): the closed field catalogue — 37 rows, no add_field, sensitivity_status held open (C5)"
```

---

---

### Task 3: `values` — auto-create, raw variants, aliases, display labels

**Files:**
- Create: `src/facts/values.py`
- Modify: `src/facts/schema.py` (add `VALUES_DDL`; one line in `create_facts_schema`)
- Test: `tests/p6/test_p6_values.py`

**Interfaces:**
- Consumes: `facts.fields` — `get_field`, `FieldNotInCatalogue`; `evidence_shape.canonical` —
  `canonical_json`, `sha256_of`; `evidence_shape.vocabulary` — `check`, `NotInVocabulary`.
- Produces: `ValueRow(value_id, field_key, canonical_value, raw_variants, display_label, aliases,
  origin, first_evidence_ref)`, `VALUE_ORIGINS: tuple[str, str]` (`automatic`, `user`),
  `ensure_value(conn, *, field_key, canonical_value, first_evidence_ref, origin) -> str`,
  `add_raw_variant(conn, value_id, raw) -> None`,
  `set_display_label(conn, value_id, display_label) -> None`,
  `merge_values(conn, *, keep, merged, reason) -> None`,
  `values_in_field(conn, field_key) -> list[sqlite3.Row]`.

**Done-means:** the positive half of 3 — *"A new value auto-creates on first sight"*.

---

**Three additions to the skeleton's `Produces:` block, each named rather than smuggled.**

1. **`set_display_label`.** The SPEC's `values` shape carries `display_label` — *"the user's preferred
   rendering — `UChicago` (§2.8)"* — and the skeleton's `Produces:` block publishes no function that
   writes it. A column with no producer is the exact defect round 1's F-2 found on
   `sensitivity_status`, so this task publishes the writer rather than leaving the column unreachable
   or setting it by raw SQL inside a test. It is an **addition**, not a rename: every name the
   skeleton lists keeps its spelling and its signature.
2. **`sha256_of`**, from the same module as `canonical_json`. `value_id` is content-addressed (see
   the identity note below) and `canonical_json` alone yields a string, not a digest.
3. **`check` / `NotInVocabulary`.** Global Constraints binds this above the per-task Consumes list:
   *"`unresolved` reasons and `origin` values are P6's own closed vocabularies, published once, in
   one module, checked with P4's `evidence_shape.vocabulary.check(value, vocabulary, *, name)` so a
   bad value raises `NotInVocabulary` rather than being stored."* `VALUE_ORIGINS` is such a
   vocabulary and is checked the same way.

**Two facts verified by execution on 2026-08-22, not read from a document.** Both change the code
below and neither is guessable:

```text
CREATE TABLE values (a TEXT)        ->  sqlite3.OperationalError: near "values": syntax error
CREATE TABLE "values" (a TEXT)      ->  OK          (SQLite 3.45.3, the interpreter's build)
observation_key(content_hash=..., extractor_name=..., locator=..., raw_value=...)
                                    ->  'sha256:' + 64 lowercase hex, 71 characters
canonical_json(('a','b'))           ->  '["a","b"]'      tuples serialize as JSON arrays
canonical_json([])                  ->  '[]'
```

`values` is a SQL keyword. **Every statement in this task spells the table `"values"` with double
quotes**, and it is the only table in the product that needs them. An unquoted one is not a style
slip — it is an `OperationalError` at `create_facts_schema` and therefore at the first test of every
later task in the part.

**The one contradiction this task hits, and the lead's ruling on it.** The SPEC's `fields` table
(§3.12) publishes **`field_key`** as its *"stable identifier"* and declares no surrogate key; the
SPEC's `values` and `file_facts` tables, and the skeleton's `ValueRow`, named the foreign key
**`field_id`**. Two names, one thing — and it was reported to the lead rather than patched
differently in two files, which was right.

> **RULED, brief §17: the column is `field_key` and it holds the field key** — in `values`, in
> `file_facts`, and in every signature that takes one. The skeleton's `field_id` is the error, not
> the SPEC.

The rejected resolution was *"`field_id` is the column name; the field key is the value it holds"*,
which keeps both published names true at once. It was overruled because a column named `_id` holding
a key is a name that lies about its content, and one concept wearing two names is this project's most
expensive defect class — it has already cost `subject`/`course`, spaced-vs-snake keys, and
`capture_date`/`capture_year`.

**Task 2 went further than the rename and it matters here.** Its first draft satisfied both names by
declaring **two columns**, `field_id TEXT PRIMARY KEY` beside `field_key TEXT NOT NULL UNIQUE`,
holding the identical string. That is the same defect made physical, and it is now deleted: `fields`
has one identifier column, `field_key`, and it is the PRIMARY KEY.

**Value identity is content-addressed, and that is a decision.** `value_id` is
`sha256_of("facts.values", field_key, canonical_value)` rather than a random UUID. Three consequences,
all wanted: `ensure_value` is idempotent without a read-then-write race; the same corpus produces the
same `value_id` in two different databases, which is what §8.5's replay compares against; and
*"a value belongs to exactly one field (§3.12)"* becomes an arithmetic property of the identifier
rather than a rule someone must remember. P4's `sha256_of` is length-prefixed and injective, so
`("a", "bc")` and `("ab", "c")` do not collide.

**What this task does not build.** §8.8 places the display label and the aliases inside a plan
version — *"§8.8's plan-version record lists 'User labels and aliases' literally, so `UChicago` vs
`University of Chicago` as a rendering choice is plan-versioned while the underlying value and every
fact pointing at it are not."* Task 22 owns `plan_versions.py`. This task stores both columns
**unscoped** and writes no plan-version key; scoping them is Task 22's, and inventing a
`plan_version` keyword here that no caller can supply would be a threshold with no injector.

---

- [ ] **Step 1: Confirm `tests/p6/conftest.py` publishes `p6_conn`, and create it if Wave A has not**

`PLAN-tasks-07-09.md` and `PLAN-tasks-14-15.md` both record the same precondition — *"`tests/p6/conftest.py`
publishes `p6_conn` — P1's database with P4's three tables, P6's own tables, and Task 2's `fields`
catalogue rows created"* — and **no task's `Files:` line owns the file.** That gap is reported to the
lead. Until it is assigned, Task 3 is the first task whose tests need catalogue rows *and* a P6 table
in the same fixture, so it carries the file. If Task 1 or Task 2 has already created it, verify it
matches this content byte for byte and change nothing.

```python
# tests/p6/conftest.py
import pytest

from database_agent.db import create_schema

from evidence_shape.schema import create_evidence_schema

from facts.fields import create_fields
from facts.schema import create_facts_schema


@pytest.fixture()
def p6_conn(conn):
    """P1's database, P4's three tables, P6's own tables, and Task 2's closed field
    catalogue loaded. `conn` is P1's root fixture and `tests/conftest.py` is not
    modified -- the same shape `tests/p4/conftest.py` uses for `p4_conn`."""
    create_schema(conn)
    create_evidence_schema(conn)
    create_facts_schema(conn)
    create_fields(conn)
    return conn
```

- [ ] **Step 2: Write the failing test**

Create `tests/p6/test_p6_values.py` with exactly this content.

Two field keys carry the whole file, and both are chosen because their spelling is **ratified rather
than assumed**: `target_school` and `client` are two of §3.8's four role fields, which Done-means 2's
2026-08-22 amendment puts in the catalogue by name. Using them means this task cannot be broken by a
spelling Task 2 has not published yet, and it makes §3.8's role separation testable in the value
table with two fields that can genuinely hold the same organization name.

```python
# tests/p6/test_p6_values.py
"""§3.12's auto-create rule, §2.8's three renderings, §3.8's role separation seen from
the value table, and §0's taxonomy aliases -- a merge records an alias and deletes
nothing (§8.2).

Every field key used here is one of §3.8's four role fields, whose spelling Done-means
2 ratifies. `target_school` and `client` are two roles that can hold the same
organization name, which is the whole of the §3.12 one-value-one-field test.
"""
import json
import sqlite3

import pytest

from evidence_shape.observation import observation_key
from evidence_shape.vocabulary import NotInVocabulary

from facts.fields import FieldNotInCatalogue
from facts.values import (
    VALUE_ORIGINS,
    ValueRow,
    add_raw_variant,
    ensure_value,
    merge_values,
    set_display_label,
    values_in_field,
)

FIELD = "target_school"
OTHER_FIELD = "client"

#: §2.8's three renderings of one entity, verbatim: "If a document says U Chicago, the
#: raw observation remains exactly that wording, while a resolver may normalize it to
#: University of Chicago and the user may later choose to display it as UChicago."
RAW = "U Chicago"
CANONICAL = "University of Chicago"
DISPLAY = "UChicago"

CONTENT_HASH = "a" * 64


def _key(raw: str, *, locator: str = "heading:page=1/heading=2") -> str:
    """A real P4 observation key, not a hand-written string. Content-addressed, so the
    same wording at the same locator is the same key (M14)."""
    return observation_key(content_hash=CONTENT_HASH,
                           extractor_name="pdf.text",
                           locator=locator,
                           raw_value=raw)


def _row(conn, value_id: str) -> sqlite3.Row:
    """Find a value through the published read only. There is no get-by-id in this
    task's surface, and none is added: `values_in_field` is how a reader reaches a
    value, and a merged value must still be reachable through it."""
    for field_key in (FIELD, OTHER_FIELD):
        for row in values_in_field(conn, field_key):
            if row["value_id"] == value_id:
                return row
    raise AssertionError(f"{value_id} is not readable in any field")


# --------------------------------------------------------------------------- §3.12
def test_a_value_auto_creates_on_first_sight(p6_conn):
    # §3.12: "The system may create new values when it sees a new course, project,
    # company, university, or event". Nobody registers it first.
    assert values_in_field(p6_conn, FIELD) == []
    value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                            first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    rows = values_in_field(p6_conn, FIELD)
    assert [r["canonical_value"] for r in rows] == [CANONICAL]
    assert rows[0]["origin"] == VALUE_ORIGINS[0] == "automatic"
    assert rows[0]["value_id"] == value_id


def test_seeing_the_same_value_again_returns_the_same_id_and_not_a_second_row(p6_conn):
    first = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                         first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    # A different file, a different observation, the same normalized answer.
    second = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                          first_evidence_ref=_key("UChicago", locator="metadata:field=Subject"),
                          origin=VALUE_ORIGINS[0])
    assert first == second
    assert len(values_in_field(p6_conn, FIELD)) == 1
    # The FIRST evidence ref is the one that introduced it, and it is not overwritten
    # by the second sighting -- §3.2's "preserve both the original evidence and the
    # conclusion built from it" applied to the value row itself.
    assert _row(p6_conn, first)["first_evidence_ref"] == _key(RAW)


def test_an_automatic_value_must_cite_the_observation_that_introduced_it(p6_conn):
    # §3.1: "Every fact preserves where it came from." A value the system created for
    # itself, with nothing to point at, is the guess this part exists to refuse.
    with pytest.raises(ValueError):
        ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                     first_evidence_ref=None, origin=VALUE_ORIGINS[0])
    with pytest.raises(ValueError):
        # A plausible-looking string that is not a P4 observation key.
        ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                     first_evidence_ref="observation-17", origin=VALUE_ORIGINS[0])
    assert values_in_field(p6_conn, FIELD) == []


def test_a_user_created_value_needs_no_observation(p6_conn):
    # §3.12's other origin. A user typing a value is not citing evidence, and
    # demanding one would make the user path impossible rather than careful.
    value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value="Georgetown Prep",
                            first_evidence_ref=None, origin=VALUE_ORIGINS[1])
    row = _row(p6_conn, value_id)
    assert row["origin"] == VALUE_ORIGINS[1] == "user"
    assert row["first_evidence_ref"] is None


def test_a_foreign_origin_is_refused_by_p4s_check(p6_conn):
    with pytest.raises(NotInVocabulary):
        ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                     first_evidence_ref=_key(RAW), origin="inferred")
    assert values_in_field(p6_conn, FIELD) == []


# ------------------------------------------------ §3.12 one value, exactly one field
def test_the_same_string_under_two_fields_is_two_values(p6_conn):
    # §3.12: "a value belongs to exactly one field". §3.8 is why it matters: "the same
    # entity type in a different role is a different field". A school we are applying
    # TO and a school that is our client are not one value with two meanings.
    target = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                          first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    client = ensure_value(p6_conn, field_key=OTHER_FIELD, canonical_value=CANONICAL,
                          first_evidence_ref=_key(RAW, locator="metadata:field=Client"),
                          origin=VALUE_ORIGINS[0])
    assert target != client
    assert [r["value_id"] for r in values_in_field(p6_conn, FIELD)] == [target]
    assert [r["value_id"] for r in values_in_field(p6_conn, OTHER_FIELD)] == [client]


def test_a_value_cannot_be_created_under_a_field_outside_the_catalogue(p6_conn):
    # Done-means 3's negative half, seen from the value side: §3.5's "The LLM is not
    # allowed to invent a new fact schema, create an unsupported field". Creating a
    # value must not be a back door into creating a field.
    with pytest.raises(FieldNotInCatalogue):
        ensure_value(p6_conn, field_key="vibe", canonical_value="energetic",
                     first_evidence_ref=_key("energetic"), origin=VALUE_ORIGINS[0])
    tables = {r[0] for r in p6_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "fields" in tables
    assert p6_conn.execute(
        "SELECT COUNT(*) FROM fields WHERE field_key = 'vibe'").fetchone()[0] == 0


# ------------------------------------------------------------- §2.8 three renderings
def test_the_three_renderings_coexist_and_none_overwrites_another(p6_conn):
    # §2.8: "If a document says U Chicago, the raw observation remains exactly that
    # wording, while a resolver may normalize it to University of Chicago and the user
    # may later choose to display it as UChicago."
    value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                            first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    add_raw_variant(p6_conn, value_id, RAW)
    set_display_label(p6_conn, value_id, DISPLAY)

    value = ValueRow.from_row(_row(p6_conn, value_id))
    assert value.raw_variants == (RAW,)
    assert value.canonical_value == CANONICAL
    assert value.display_label == DISPLAY
    # Three columns, three renderings, and the raw wording is byte-exact.
    assert len({value.raw_variants[0], value.canonical_value, value.display_label}) == 3


def test_every_raw_wording_observed_is_kept(p6_conn):
    value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                            first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    for raw in (RAW, "U. Chicago", RAW, "the University of Chicago"):
        add_raw_variant(p6_conn, value_id, raw)
    # Recorded once each, and the duplicate did not create a second entry.
    assert ValueRow.from_row(_row(p6_conn, value_id)).raw_variants == (
        "U Chicago", "U. Chicago", "the University of Chicago")


def test_raw_variants_do_not_depend_on_the_order_they_arrived_in(p6_conn):
    # Global constraint: P4's reads are in insertion order and P6 imposes its own.
    # Two values that saw the same wordings in different orders must store the same
    # column, or §8.5's replay compares a run against itself and reports a change.
    # Two DIFFERENT canonical values, so these are two rows rather than one row
    # visited twice -- `ensure_value` is idempotent and would otherwise make this
    # test pass without proving anything.
    wordings = ("U Chicago", "U. Chicago", "the University of Chicago")
    stored = []
    for canonical, order in ((CANONICAL, wordings),
                             ("Chicago University", tuple(reversed(wordings)))):
        value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value=canonical,
                                first_evidence_ref=_key(canonical),
                                origin=VALUE_ORIGINS[0])
        for raw in order:
            add_raw_variant(p6_conn, value_id, raw)
        stored.append(_row(p6_conn, value_id)["raw_variants"])
    assert stored[0] == stored[1]


def test_an_empty_raw_variant_is_refused(p6_conn):
    value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                            first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    with pytest.raises(ValueError):
        add_raw_variant(p6_conn, value_id, "")
    assert ValueRow.from_row(_row(p6_conn, value_id)).raw_variants == ()


def test_a_variant_on_an_unknown_value_raises(p6_conn):
    with pytest.raises(KeyError):
        add_raw_variant(p6_conn, "sha256:" + "0" * 64, RAW)


# --------------------------------------------- §0 taxonomy aliases; §8.2 never delete
def test_a_merge_records_an_alias_and_deletes_nothing(p6_conn):
    keep = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                        first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    merged = ensure_value(p6_conn, field_key=FIELD, canonical_value="U Chicago",
                          first_evidence_ref=_key(RAW, locator="filename:name"),
                          origin=VALUE_ORIGINS[0])
    add_raw_variant(p6_conn, merged, "U Chicago")
    set_display_label(p6_conn, merged, "U Chi")

    merge_values(p6_conn, keep=keep, merged=merged,
                 reason="one university under two wordings")

    kept_row = ValueRow.from_row(_row(p6_conn, keep))
    # The merged value's canonical wording, its label and its raw variants survive on
    # the surviving row. §0 records "taxonomy aliases"; this is one.
    assert "U Chicago" in kept_row.aliases
    assert "U Chi" in kept_row.aliases
    assert "U Chicago" in kept_row.raw_variants

    # And the merged row is STILL A ROW. Every fact that pointed at it still resolves,
    # and it names where it went.
    merged_row = _row(p6_conn, merged)
    assert merged_row["merged_into"] == keep
    assert merged_row["merge_reason"] == "one university under two wordings"
    assert merged_row["canonical_value"] == "U Chicago"
    assert {r["value_id"] for r in values_in_field(p6_conn, FIELD)} == {keep, merged}


def test_a_value_row_can_never_be_deleted(p6_conn):
    # The SPEC's own words for this table: merges "record an alias, never delete a
    # value (§8.2)". Enforced by trigger, so the assertion above is unfalsifiable
    # rather than merely true of today's code path.
    value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                            first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    with pytest.raises(sqlite3.IntegrityError):
        p6_conn.execute('DELETE FROM "values" WHERE value_id = ?', (value_id,))
    assert len(values_in_field(p6_conn, FIELD)) == 1


def test_a_merge_across_two_fields_is_refused(p6_conn):
    # Merging §3.8's roles together would erase the separation the field split exists
    # to create -- the school we apply to becoming the school that is our client.
    target = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                          first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    client = ensure_value(p6_conn, field_key=OTHER_FIELD, canonical_value=CANONICAL,
                          first_evidence_ref=_key(RAW, locator="metadata:field=Client"),
                          origin=VALUE_ORIGINS[0])
    with pytest.raises(ValueError):
        merge_values(p6_conn, keep=target, merged=client, reason="same name")
    assert _row(p6_conn, client)["merged_into"] is None


def test_a_merge_records_why_and_refuses_the_degenerate_cases(p6_conn):
    keep = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                        first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    merged = ensure_value(p6_conn, field_key=FIELD, canonical_value="U Chicago",
                          first_evidence_ref=_key(RAW, locator="filename:name"),
                          origin=VALUE_ORIGINS[0])
    with pytest.raises(ValueError):
        merge_values(p6_conn, keep=keep, merged=merged, reason="")
    with pytest.raises(ValueError):
        merge_values(p6_conn, keep=keep, merged=keep, reason="itself")
    with pytest.raises(KeyError):
        merge_values(p6_conn, keep=keep, merged="sha256:" + "0" * 64, reason="ghost")

    merge_values(p6_conn, keep=keep, merged=merged, reason="first merge")
    # The first reason sticks -- P1's supersede rule, applied to the alias record.
    with pytest.raises(ValueError):
        merge_values(p6_conn, keep=keep, merged=merged, reason="second merge")
    assert _row(p6_conn, merged)["merge_reason"] == "first merge"


def test_a_merge_chain_cannot_cycle(p6_conn):
    a = ensure_value(p6_conn, field_key=FIELD, canonical_value="A University",
                     first_evidence_ref=_key("A University"), origin=VALUE_ORIGINS[0])
    b = ensure_value(p6_conn, field_key=FIELD, canonical_value="B University",
                     first_evidence_ref=_key("B University"), origin=VALUE_ORIGINS[0])
    merge_values(p6_conn, keep=b, merged=a, reason="a is b")
    with pytest.raises(ValueError):
        merge_values(p6_conn, keep=a, merged=b, reason="and b is a")


# ------------------------------------------------------------------------ §8.8 held
def test_the_display_label_is_stored_unscoped_and_no_plan_version_is_invented(p6_conn):
    # §8.8 puts "User labels and aliases" inside a plan version; Task 22 owns that
    # scoping. This task must not invent a plan_version keyword no caller can supply.
    import inspect
    assert "plan_version" not in inspect.signature(set_display_label).parameters
    columns = {r["name"] for r in p6_conn.execute('PRAGMA table_info("values")')}
    assert "plan_version" not in columns
```

- [ ] **Step 3: Run the test and confirm it FAILS for the right reason**

Run: `pytest tests/p6/test_p6_values.py -q`

Expected: **collection error** — `ModuleNotFoundError: No module named 'facts.values'`, raised at the
`from facts.values import ...` line. All 18 tests error at collection; none run. Any other failure at
this step means Task 1 or Task 2 is not green and this task should stop rather than proceed.

- [ ] **Step 4: Add the `values` DDL to `src/facts/schema.py`**

Append this constant to `src/facts/schema.py`, after the `fields` DDL Task 2 added.

```python
#: `values` is a SQL keyword -- `CREATE TABLE values (...)` is a syntax error in
#: SQLite, verified on 3.45.3 -- so the identifier is quoted here and at every call
#: site in `facts.values`. It is the only table in the product that needs quoting.
#:
#: `field_key` is the field key, under the name the SPEC's `fields` table publishes
#: for it. The skeleton's `values` / `file_facts` shapes and its `ValueRow` called
#: this `field_key`; brief §17 ruled that the error -- a column named `_id` holding a
#: key is a name that lies about its content.
#:
#: It carries NO `REFERENCES fields (...)` clause, and that is deliberate rather than
#: forgotten. `open_database` leaves `PRAGMA foreign_keys` ON (verified: it reads 1),
#: and a foreign key whose parent column is not a declared PRIMARY KEY or UNIQUE
#: raises `sqlite3.OperationalError: foreign key mismatch` at INSERT -- also verified.
#: Task 2 now declares `fields.field_key` PRIMARY KEY, so a REFERENCES clause WOULD
#: bind -- the condition this omission was hedged against is decided. It is still
#: omitted, deliberately: the gate the SPEC actually names is the catalogue lookup.
#: `get_field` raises `FieldNotInCatalogue` before any INSERT reaches here and Task 3's
#: test asserts it, whereas an FK would raise `IntegrityError` from the driver and
#: replace a named refusal with an anonymous one. Adding it is a live option, not an
#: oversight.
#:
#: UNIQUE (field_key, canonical_value) is §3.12's "a value belongs to exactly one
#: field" enforced by the database rather than remembered by a caller.
#:
#: `merged_into` / `merge_reason` are NOT P1's supersede set. A merge is not a
#: supersession: the merged value was not wrong and is not replaced by a better
#: reading of the same evidence -- it is the same entity under another name, which is
#: §0's "taxonomy aliases". The SPEC's sentence for this table says so outright:
#: merges "record an alias, never delete a value (§8.2)". Task 16 owns supersession,
#: for `file_facts`, where a later pass genuinely replaces an earlier conclusion.
VALUES_DDL = """
CREATE TABLE IF NOT EXISTS "values" (
    value_id           TEXT PRIMARY KEY,
    field_key           TEXT NOT NULL,
    canonical_value    TEXT NOT NULL,
    raw_variants       TEXT NOT NULL,
    display_label      TEXT,
    aliases            TEXT NOT NULL,
    origin             TEXT NOT NULL,
    first_evidence_ref TEXT,
    merged_into        TEXT REFERENCES "values" (value_id),
    merge_reason       TEXT,
    UNIQUE (field_key, canonical_value)
);
CREATE INDEX IF NOT EXISTS values_field ON "values" (field_key);
CREATE INDEX IF NOT EXISTS values_merged ON "values" (merged_into);
CREATE TRIGGER IF NOT EXISTS values_no_delete
BEFORE DELETE ON "values"
BEGIN SELECT RAISE(ABORT, 'a merge records an alias; a value is never deleted (§0, §8.2)'); END;
"""
```

Then add one line to `create_facts_schema`, after the `fields` script:

```python
def create_facts_schema(conn: sqlite3.Connection) -> None:
    """Create every P6-owned table. Idempotent. P1's `create_schema` runs first, and
    P4's `create_evidence_schema` before any read."""
    conn.executescript(FIELDS_DDL)
    conn.executescript(VALUES_DDL)
```

`RAISE(ABORT, ...)` surfaces in Python as `sqlite3.IntegrityError`, which is what
`test_a_value_row_can_never_be_deleted` catches — the same class P4's `evidence_no_delete` raises.

- [ ] **Step 5: Write `src/facts/values.py`**

```python
# src/facts/values.py
"""§3.12's `values` table -- "the changing, user-specific content discovered from
files", as against `fields`, which are "the long-term organization language of the
product".

Three design sentences are load-bearing here, and each is a test rather than a comment:

  * §3.12: "The system may create new values when it sees a new course, project,
    company, university, or event, but it should not invent new fields automatically."
    `ensure_value` creates a VALUE row and never a FIELD row. The field must already be
    in Task 2's closed catalogue; `get_field` raises `FieldNotInCatalogue` if it is not,
    so creating a value is not a back door into creating a field (§3.5).
  * §3.12 again: "a value belongs to exactly one field". The same string under two
    fields is two values. That is §3.8's role separation -- "the same entity type in a
    different role is a different field" -- expressed in this table.
  * §2.8: "If a document says U Chicago, the raw observation remains exactly that
    wording, while a resolver may normalize it to University of Chicago and the user
    may later choose to display it as UChicago." Three renderings, three columns,
    none of them overwriting another.

`value_id` is content-addressed over (field_key, canonical_value). That makes
`ensure_value` idempotent with no read-then-write race, gives two databases that saw
the same corpus the same value ids (§8.5's replay), and turns one-value-one-field into
a property of the identifier rather than a rule to remember.

Ordering is imposed, never inherited. `raw_variants` and `aliases` are stored sorted,
and `values_in_field` sorts, because P4's reads are in insertion order (verified by
execution) and a corpus extracted in a different order must not produce a different
row.

The table name is a SQL keyword and every statement below quotes it.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import check

from facts.fields import get_field

#: §3.12's two origins. A closed vocabulary, checked through P4's `check` so a foreign
#: value raises `NotInVocabulary` instead of being stored (Global Constraints).
VALUE_ORIGINS: tuple[str, str] = ("automatic", "user")

#: An observation key is P4's, content-addressed, and `sha256:`-prefixed (M14).
_KEY_PREFIX = "sha256:"


@dataclass(frozen=True)
class ValueRow:
    """The SPEC's `values` shape, with its two JSON arrays already decoded.

    Decoding happens in exactly one place. A reader that calls `json.loads` on
    `raw_variants` itself is a second decoder, and a second decoder is where the two
    representations drift.
    """

    value_id: str
    field_key: str
    canonical_value: str
    raw_variants: tuple[str, ...]
    display_label: str | None
    aliases: tuple[str, ...]
    origin: str
    first_evidence_ref: str | None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "ValueRow":
        return cls(
            value_id=row["value_id"],
            field_key=row["field_key"],
            canonical_value=row["canonical_value"],
            raw_variants=tuple(json.loads(row["raw_variants"])),
            display_label=row["display_label"],
            aliases=tuple(json.loads(row["aliases"])),
            origin=row["origin"],
            first_evidence_ref=row["first_evidence_ref"],
        )


def _checked_field_key(conn: sqlite3.Connection, field_key: str) -> str:
    """The catalogue row's key, and the gate that stops a value inventing a field.

    `get_field` raises `FieldNotInCatalogue` for a key outside Task 2's closed
    catalogue, so this function is also §3.12's "it should not invent new fields
    automatically" enforced on the value path.
    """
    return get_field(conn, field_key)["field_key"]


def _value_identity(*, field_key: str, canonical_value: str) -> str:
    """Content-addressed value identity. `sha256_of` is length-prefixed and injective,
    so ("a", "bc") and ("ab", "c") do not collide."""
    return sha256_of("facts.values", field_key, canonical_value)


def _fetch(conn: sqlite3.Connection, value_id: str) -> sqlite3.Row:
    row = conn.execute(
        'SELECT * FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    if row is None:
        raise KeyError(f"unknown value {value_id!r}")
    return row


def _store_list(items) -> str:
    """One sorted, de-duplicated, canonical JSON array. Sorted because P4's reads are
    in insertion order and this row must not inherit it."""
    return canonical_json(sorted(set(items)))


def ensure_value(conn: sqlite3.Connection, *, field_key: str, canonical_value: str,
                 first_evidence_ref: str | None, origin: str) -> str:
    """§3.12's auto-create. Returns the value id, creating the row on first sight.

    Idempotent: the second sighting of the same canonical value under the same field
    returns the first row's id and does not overwrite its `first_evidence_ref`, which
    is the observation that introduced it.
    """
    check(origin, VALUE_ORIGINS, name="value origin")
    if not canonical_value:
        raise ValueError("a value needs a canonical form (§3.12)")
    if origin == VALUE_ORIGINS[0]:
        if not first_evidence_ref or not first_evidence_ref.startswith(_KEY_PREFIX):
            raise ValueError(
                "an automatically created value cites the observation that introduced "
                "it (§3.1); first_evidence_ref must be a P4 observation key"
            )
    field_key = _checked_field_key(conn, field_key)
    value_id = _value_identity(field_key=field_key, canonical_value=canonical_value)
    existing = conn.execute(
        'SELECT value_id FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    if existing is not None:
        return existing["value_id"]
    conn.execute(
        'INSERT INTO "values" (value_id, field_key, canonical_value, raw_variants, '
        'display_label, aliases, origin, first_evidence_ref, merged_into, '
        'merge_reason) VALUES (?, ?, ?, ?, NULL, ?, ?, ?, NULL, NULL)',
        (value_id, field_key, canonical_value, _store_list(()), _store_list(()),
         origin, first_evidence_ref),
    )
    return value_id


def add_raw_variant(conn: sqlite3.Connection, value_id: str, raw: str) -> None:
    """§2.8: "the raw observation remains exactly that wording". Byte-exact, and
    recorded once however many times it is seen."""
    if not raw:
        raise ValueError(
            "a raw variant is the wording the document used; it is never empty (§2.8)"
        )
    row = _fetch(conn, value_id)
    variants = json.loads(row["raw_variants"])
    if raw in variants:
        return
    conn.execute(
        'UPDATE "values" SET raw_variants = ? WHERE value_id = ?',
        (_store_list([*variants, raw]), value_id),
    )


def set_display_label(conn: sqlite3.Connection, value_id: str,
                      display_label: str) -> None:
    """§2.8's third rendering: "the user may later choose to display it as UChicago".

    Stored unscoped. §8.8 places the display label inside a plan version and Task 22
    owns that scoping; this function invents no `plan_version` keyword, because no
    caller could supply one today and a required keyword nobody can fill is a
    threshold with no injector.
    """
    if not display_label:
        raise ValueError("a display label is a rendering, never empty (§2.8)")
    _fetch(conn, value_id)
    conn.execute(
        'UPDATE "values" SET display_label = ? WHERE value_id = ?',
        (display_label, value_id),
    )


def merge_values(conn: sqlite3.Connection, *, keep: str, merged: str,
                 reason: str) -> None:
    """§0's taxonomy aliases. The merge records an alias and deletes nothing (§8.2).

    The merged row keeps its identity, its canonical wording and its evidence ref, and
    gains a pointer to the surviving value, so every fact that already pointed at it
    still resolves and a reader can see where it went. The surviving row absorbs the
    merged value's canonical wording, its label and its raw variants as aliases.
    """
    if not reason:
        raise ValueError("a merge records why (§8.2)")
    if keep == merged:
        raise ValueError("a value cannot be merged into itself")
    keep_row, merged_row = _fetch(conn, keep), _fetch(conn, merged)
    if keep_row["field_key"] != merged_row["field_key"]:
        raise ValueError(
            "a value belongs to exactly one field (§3.12); merging across two fields "
            "would erase §3.8's role separation"
        )
    if merged_row["merged_into"] is not None:
        raise ValueError(
            f"{merged} is already merged into {merged_row['merged_into']}; "
            "the first merge_reason is never overwritten (§8.2)"
        )
    seen, cursor = {merged}, keep
    while cursor is not None:
        if cursor in seen:
            raise ValueError("merge chain would cycle")
        seen.add(cursor)
        row = conn.execute(
            'SELECT merged_into FROM "values" WHERE value_id = ?', (cursor,)
        ).fetchone()
        cursor = None if row is None else row["merged_into"]

    aliases = set(json.loads(keep_row["aliases"]))
    aliases.add(merged_row["canonical_value"])
    aliases.update(json.loads(merged_row["aliases"]))
    if merged_row["display_label"]:
        aliases.add(merged_row["display_label"])
    variants = set(json.loads(keep_row["raw_variants"]))
    variants.update(json.loads(merged_row["raw_variants"]))
    conn.execute(
        'UPDATE "values" SET aliases = ?, raw_variants = ? WHERE value_id = ?',
        (_store_list(aliases), _store_list(variants), keep),
    )
    conn.execute(
        'UPDATE "values" SET merged_into = ?, merge_reason = ? WHERE value_id = ?',
        (keep, reason, merged),
    )


def values_in_field(conn: sqlite3.Connection, field_key: str) -> list[sqlite3.Row]:
    """Every value in one field, merged ones included -- a merged value is still a
    readable value (§8.2) and a fact that points at it must still resolve.

    Sorted, because P4's reads are in insertion order and this one imposes its own.
    """
    return list(conn.execute(
        'SELECT * FROM "values" WHERE field_key = ? '
        'ORDER BY canonical_value, value_id',
        (_checked_field_key(conn, field_key),),
    ))
```

- [ ] **Step 6: Run the test and confirm it passes**

Run: `pytest tests/p6/test_p6_values.py -v`

Expected: PASS — **18 passed**. Two of the eighteen are the ones worth watching:
`test_a_value_row_can_never_be_deleted` passes because the trigger raises
`sqlite3.IntegrityError`, not because `merge_values` politely declines to delete; and
`test_raw_variants_do_not_depend_on_the_order_they_arrived_in` passes because `_store_list` sorts,
which is the Global Constraint about P4's insertion-order reads applied to the one column in this
task that accumulates.

- [ ] **Step 7: Run the whole P6 suite, so Tasks 1 and 2 are still green**

Run: `pytest tests/p6 -q`

Expected: PASS. Task 2's guard walks `facts` for a runtime-created field, and `facts.values` is a new
module inside its reach: `ensure_value` creates value rows only, and the only write it makes to
`fields` is none. A failure here is a real finding.

- [ ] **Step 8: Commit**

```bash
git add src/facts/values.py src/facts/schema.py tests/p6/conftest.py tests/p6/test_p6_values.py
git commit -m "feat(P6): §3.12 values auto-create; §2.8's three renderings; a merge aliases, never deletes"
```

---

---

### Task 4: `file_facts` — the row, and the negative contract a reviewer can check from the schema

**Files:**
- Create: `src/facts/file_facts.py`
- Modify: `src/facts/schema.py` (add `FILE_FACTS_DDL`; one line in `create_facts_schema`)
- Test: `tests/p6/test_p6_file_facts.py`

**Interfaces:**
- Consumes: `facts.states` — `STATES`; `facts.fields` — `get_field`, `FieldNotInCatalogue`;
  `facts.values` — `values_in_field`; `facts.authorship` — `event_defaults`, `AUTHORED_EVENT_TYPES`;
  `database_agent.supersede` — `SUPERSEDE_COLUMNS`, `supersede_ddl`; `database_agent.events` —
  `append_event`; `evidence_shape.canonical` — `canonical_json`, `sha256_of`;
  `evidence_shape.vocabulary` — `check`, `NotInVocabulary`.
- Produces: `FILE_FACTS_COLUMNS: tuple[str, ...]`, `FORBIDDEN_COLUMN_SUBSTRINGS: tuple[str, ...]`,
  `FACT_ORIGINS: tuple[str, ...]` (§3.1's five: deterministic extractor · rule · LLM interpretation ·
  user correction · user-approved folder) **and one named constant per member —
  `DETERMINISTIC_EXTRACTOR`, `RULE`, `LLM_INTERPRETATION`, `USER_CORRECTION`,
  `USER_APPROVED_FOLDER`**, `write_fact(conn, *, file_id, content_hash, field_key,
  value_id, reliability_state, origin, evidence_refs, cache_key, active, cited_quote_refs=(),
  model_identifier=None, prompt_fingerprint=None, internal_score=None, rejection_reason=None) -> str`,
  `facts_for_file(conn, file_id, content_hash) -> list[sqlite3.Row]`, `EvidenceRequired`.

**Done-means:** 1.

---

**The negative contract is the point of this task, so it is stated before anything else.**

§3.14, verbatim: *"Facts remain separate from the future destination tree. A fact such as subject =
BUSIB 4300 does not itself dictate one permanent folder path. The user may later organize the same
facts as Academics/Columbia/2026-Spring/BUSIB 4300/Syllabus or as Academics/BUSIB 4300/Spring
2026/Syllabus. The facts have not changed; only the user's preferred organization view has changed."*
§4.1 adds the other half — the graph *"does not automatically copy those missing facts onto sparse
files"* — and §3.9 that a session is *"not a basis for automatic semantic propagation"*.

The SPEC turns that into a sentence a reviewer can act on: *"`file_facts` has no path column, no
destination column, no folder column, and no group column. A fact does not dictate a path (§3.14) and
does not record membership (§4.3). A reviewer should be able to check this by reading the schema
alone."*

**"By reading the schema alone" is a testable claim, and this task makes it one.** Three published
names carry it, and Task 5 and Tasks 16–19 import two of them so the same contract binds `unresolved`
and every later reader:

```text
FILE_FACTS_COLUMNS              what the module declares the table to be
FORBIDDEN_COLUMN_SUBSTRINGS     ("path", "destination", "folder", "node", "group")
PRAGMA table_info(file_facts)   what the database actually is
```

The test asserts all three agree: the declared tuple **equals** the live column set, so the module
cannot describe a table it does not have; and no live column name **contains** any forbidden
substring, so `destination_node_id` fails the day it is added rather than the day someone reads it.
A substring list is used rather than an exact-name list for that reason alone.

**And the guard is proved non-vacuous in the same file.** A check that scans for a token has returned
a false result nine times on this project. So one test builds a scratch table carrying
`destination_node_id` and runs the identical check over it, asserting it is caught. A guard that
cannot be shown to fail is not evidence that the thing it guards is absent.

**The negative contract also covers the writer's signature, not only the schema.** A column is one
way to smuggle a path in; a keyword argument is the other. `write_fact` is introspected at run time
for a parameter whose name contains any forbidden substring — which is how §4.3's *"P6 stores no
group membership"* is asserted from this task rather than deferred to Task 25's sweep.

---

**`FACT_ORIGINS` — this task owns the literal spelling, and two documents order it differently.**

The SPEC's `file_facts` shape publishes the five in one order: *"origin — which producer created it —
deterministic extractor | rule | LLM interpretation | user correction | user-approved folder
(§3.1)"*. §3.1's prose sentence lists the same producers in a different order and with *"deterministic
rule"* as a single phrase: *"a filename, document title, heading, table cell, page of extracted text,
EXIF field, OCR region, archive manifest, user-approved folder, deterministic rule, LLM
interpretation, or explicit user correction."* The first eight of those are evidence *locations* —
P4's business, already carried on the observation — and the last four are producers.

**The SPEC's order is the stored one**, and **this task owns the literal spelling of each member**.
The spelling is `snake_case`, matching every other stored vocabulary in the part:

```python
FACT_ORIGINS = (DETERMINISTIC_EXTRACTOR, RULE, LLM_INTERPRETATION,
                USER_CORRECTION, USER_APPROVED_FOLDER)
```

**Consumers import the NAMED CONSTANT, not an index** (preamble §3.1). Earlier drafts of
`PLAN-tasks-07-09.md`, `PLAN-tasks-14-15.md` and `PLAN-tasks-16-19.md` addressed the tuple by index
— `FACT_ORIGINS[0]` for a deterministic producer, `FACT_ORIGINS[1]` for a rule — and stated that as
shared law. It is not. An index is single-homed and unreadable, and it silently couples every
consumer to this tuple's **order**: re-ordering it would then re-label every fact three other
authors write with no test failing. So this task publishes `DETERMINISTIC_EXTRACTOR`, `RULE`,
`LLM_INTERPRETATION`, `USER_CORRECTION` and `USER_APPROVED_FOLDER` beside the tuple, and the
ordering question stops being load-bearing on anyone else.

---

**Two facts about the SPEC's `file_facts` shape that this task changes, both reported.**

1. **`content_hash` is missing from the SPEC's column list and is added here.** It has to be:
   `facts_for_file(conn, file_id, content_hash)` is the skeleton's published signature, the abstention
   row and the §3.4 cache key are both per content hash, and the Global Constraint is explicit —
   *"Every P6 read that is per file version — which is all of them — must filter on
   `observation.content_hash`."* The cache key contains the content hash but is a digest, so it
   cannot be filtered on. Without the column the published read is unimplementable.
2. **No foreign key points at `fields`.** `open_database` leaves `PRAGMA foreign_keys` ON (verified:
   it reads `1`), and a foreign key whose parent column is not a declared PRIMARY KEY or UNIQUE
   raises `sqlite3.OperationalError: foreign key mismatch` at INSERT (also verified). Whether
   `fields.field_key` is declared PRIMARY KEY is Task 2's DDL decision. `get_field` is the gate the
   SPEC names, it raises `FieldNotInCatalogue` before any INSERT, and this task's test asserts it.
   The one foreign key kept is `value_id REFERENCES "values" (value_id)`, whose parent **is** a
   primary key — so a fact can never cite a value that does not exist.

**`fact_id` is content-addressed, for the same three reasons `value_id` is** (Task 3): writing the
same conclusion at the same cache key twice is one row rather than two, replay (§8.5) produces the
same identifiers in a second database, and the identity is checkable rather than remembered. §8.2's
supersession path is unaffected: pass 4 cites `ocr`-tier observations, so §3.4's `analysis_tier`
differs, so the cache key differs, so the fact id differs and the new fact supersedes rather than
collides. **A second write at an identical cache key appends no second `fact creation` event**, or the
provenance log would count one fact twice.

**What this task does not write.** `preferred` is Task 18's — *"`mark_superseded` does not touch
`preferred` and knows nothing about it — that column is Task 18's whole job."* This task **creates**
the column, because M1 places it on `file_facts` and nowhere else, and **never sets it**; a test
asserts `write_fact` leaves it `NULL`. Filtering a read by `active`, `preferred` or reliability state
is Task 24's proposal-eligible read; `facts_for_file` returns every fact row for that file version, in
an order it imposes itself.

---

- [ ] **Step 1: Write the failing test**

Create `tests/p6/test_p6_file_facts.py` with exactly this content. It uses `p6_conn` from
`tests/p6/conftest.py` (Task 3, Step 1) and needs **no P1 `files` row** — verified: `append_event`
accepts a `file_id` that is in no `files` row, and `file_facts` references `files` no more than P4's
`evidence` does.

```python
# tests/p6/test_p6_file_facts.py
"""Done-means 1: the fact row exists with the shape the SPEC declares, and it carries
no path, no destination, no folder, no node and no group -- checkable from the schema
alone (§3.14, §4.3).

§3.14: "Facts remain separate from the future destination tree. A fact such as
subject = BUSIB 4300 does not itself dictate one permanent folder path."
"""
import inspect
import json
import sqlite3

import pytest

from database_agent.supersede import SUPERSEDE_COLUMNS, mark_superseded

from evidence_shape.observation import observation_key
from evidence_shape.vocabulary import NotInVocabulary

from facts.fields import FieldNotInCatalogue
from facts.file_facts import (
    DETERMINISTIC_EXTRACTOR,
    FACT_ORIGINS,
    FILE_FACTS_COLUMNS,
    FORBIDDEN_COLUMN_SUBSTRINGS,
    LLM_INTERPRETATION,
    RULE,
    USER_APPROVED_FOLDER,
    USER_CORRECTION,
    EvidenceRequired,
    facts_for_file,
    write_fact,
)
from facts.states import DIRECT, STATES, USER_CONFIRMED
from facts.values import VALUE_ORIGINS, ensure_value

FIELD = "subject"            # D6: the ratified academic field key
OTHER_FIELD = "client"       # §3.8, a role field -- a different field, same string
CONTENT_HASH = "a" * 64
OTHER_HASH = "b" * 64
FILE_ID = "file-1"
CACHE_KEY = "sha256:" + "c" * 64


def _key(raw: str, *, locator: str = "heading:page=1/heading=2") -> str:
    return observation_key(content_hash=CONTENT_HASH, extractor_name="pdf.text",
                           locator=locator, raw_value=raw)


def _value(conn, *, field_key: str = FIELD, canonical: str = "BUSIB 4300") -> str:
    return ensure_value(conn, field_key=field_key, canonical_value=canonical,
                        first_evidence_ref=_key(canonical), origin=VALUE_ORIGINS[0])


def _write(conn, **overrides) -> str:
    kwargs = dict(file_id=FILE_ID, content_hash=CONTENT_HASH, field_key=FIELD,
                  value_id=_value(conn), reliability_state=DIRECT,
                  origin=DETERMINISTIC_EXTRACTOR, evidence_refs=(_key("BUSIB 4300"),),
                  cache_key=CACHE_KEY, active=True)
    kwargs.update(overrides)
    return write_fact(conn, **kwargs)


def _live_columns(conn, table: str) -> tuple[str, ...]:
    """What the database actually is. Generated VIRTUAL columns are absent from
    `table_info` -- verified on SQLite 3.45.3 -- which is exactly why `record_id` is
    not in FILE_FACTS_COLUMNS and is asserted separately below."""
    return tuple(r["name"] for r in conn.execute(f"PRAGMA table_info({table})"))


def _offending(names) -> list[str]:
    """The one check the negative contract is made of, in one place, so the vacuity
    test below runs the identical code over a table built to fail it."""
    return [name for name in names
            if any(bad in name.lower() for bad in FORBIDDEN_COLUMN_SUBSTRINGS)]


# ------------------------------------------- Done-means 1: the shape, and only it
def test_the_module_declares_exactly_the_table_it_has(p6_conn):
    # A module that describes a table it does not have makes every other assertion
    # in this file an assertion about a document rather than about a database.
    assert _live_columns(p6_conn, "file_facts") == FILE_FACTS_COLUMNS


def test_the_row_carries_what_the_spec_declares(p6_conn):
    for column in ("fact_id", "file_id", "content_hash", "field_key", "value_id",
                   "reliability_state", "origin", "evidence_refs",
                   "cited_quote_refs", "cache_key", "model_identifier",
                   "prompt_fingerprint", "internal_score", "active", "preferred",
                   "rejection_reason", "created_at", *SUPERSEDE_COLUMNS):
        assert column in FILE_FACTS_COLUMNS


def test_the_three_supersede_columns_are_p1s_and_are_not_respelled(p6_conn):
    # M1: the set is published once, by P1, and adopted by name.
    assert set(SUPERSEDE_COLUMNS) <= set(FILE_FACTS_COLUMNS)
    assert SUPERSEDE_COLUMNS == ("supersedes", "superseded_by", "supersede_reason")


# ----------------------------------------- the negative contract (§3.14, §4.3, §4.1)
def test_no_column_names_a_path_a_destination_a_folder_a_node_or_a_group(p6_conn):
    # §3.14: "A fact such as subject = BUSIB 4300 does not itself dictate one
    # permanent folder path." §4.3 and §4.1: a fact records no group membership.
    # Read from the database, not from the module, so a DDL edit cannot pass by
    # editing the tuple.
    assert _offending(_live_columns(p6_conn, "file_facts")) == []
    assert _offending(FILE_FACTS_COLUMNS) == []


def test_the_forbidden_substring_guard_is_not_vacuous(p6_conn):
    # A scan for a token has produced a false result nine times on this project. So
    # the guard is run over a table built to fail it. If this test ever passes with
    # an empty list, the check above is proving nothing.
    p6_conn.execute("CREATE TABLE scratch_tree (fact_id TEXT, destination_node_id "
                    "TEXT, folder_path TEXT, group_id TEXT)")
    assert _offending(_live_columns(p6_conn, "scratch_tree")) == [
        "destination_node_id", "folder_path", "group_id"]
    p6_conn.execute("DROP TABLE scratch_tree")


def test_the_writer_takes_no_path_and_no_group_either(p6_conn):
    # A column is one way to smuggle a destination in; a keyword is the other.
    # §4.3: P6 accepts no fact write derived from group membership.
    parameters = inspect.signature(write_fact).parameters
    assert _offending(parameters) == []
    assert "group_id" not in parameters
    assert "path" not in parameters


def test_a_fact_never_learns_the_files_path(p6_conn):
    # The whole of §3.14 in one assertion: the row that results from writing a fact
    # contains no rendering of any path, under any column name.
    fact_id = _write(p6_conn)
    row = [r for r in facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)
           if r["fact_id"] == fact_id][0]
    assert _offending(row.keys()) == []


# --------------------------------------------------- §3.1 a fact carries its evidence
def test_a_fact_is_written_and_read_back_with_its_field_and_its_value(p6_conn):
    fact_id = _write(p6_conn)
    rows = facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)
    assert len(rows) == 1
    row = rows[0]
    assert row["fact_id"] == fact_id
    # The read projects the field KEY and the canonical value, so no caller has to
    # join `fields` and `values` for itself.
    assert row["field_key"] == FIELD
    assert row["canonical_value"] == "BUSIB 4300"
    assert row["reliability_state"] == DIRECT == "direct"
    assert row["origin"] == DETERMINISTIC_EXTRACTOR
    assert json.loads(row["evidence_refs"]) == [_key("BUSIB 4300")]
    assert row["active"] == 1


def test_a_non_user_fact_with_no_evidence_is_refused(p6_conn):
    # §3.1: "Every fact preserves where it came from." A fact with nothing behind it
    # is the plausible guess this part exists to refuse.
    with pytest.raises(EvidenceRequired):
        _write(p6_conn, evidence_refs=())
    assert facts_for_file(p6_conn, FILE_ID, CONTENT_HASH) == []


def test_every_evidence_ref_must_be_a_p4_observation_key(p6_conn):
    # M14: the citation is the content-addressed key, never an observation_id and
    # never a row id -- that is what makes it survive an extractor upgrade (§8.7).
    for bad in ("observation-17", "", "sha255:" + "0" * 64, "0" * 64):
        with pytest.raises(EvidenceRequired):
            _write(p6_conn, evidence_refs=(bad,))
    assert facts_for_file(p6_conn, FILE_ID, CONTENT_HASH) == []


def test_a_user_confirmed_fact_may_stand_without_an_observation(p6_conn):
    # A user asserting a fact is not citing evidence, and demanding one would make
    # the user path impossible rather than careful.
    fact_id = _write(p6_conn, reliability_state=USER_CONFIRMED,
                     origin=USER_CORRECTION, evidence_refs=())
    row = [r for r in facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)
           if r["fact_id"] == fact_id][0]
    assert row["reliability_state"] == USER_CONFIRMED == "user_confirmed"
    assert json.loads(row["evidence_refs"]) == []


def test_the_evidence_refs_stored_do_not_depend_on_the_order_they_arrived_in(p6_conn):
    # P4's reads are in insertion order; P6 imposes its own before it stores.
    refs = (_key("BUSIB 4300"), _key("BUSIB 4300", locator="filename:name"))
    first = _write(p6_conn, evidence_refs=refs)
    second = _write(p6_conn, evidence_refs=tuple(reversed(refs)))
    assert first == second
    assert len(facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)) == 1


# ------------------------------------------------------- closed vocabularies (§3.5)
def test_a_foreign_reliability_state_is_refused(p6_conn):
    # The six are P4's and P6 re-spells none of them. §3.13's prose spellings are
    # prose: a value outside the six is a load error, not a spelling to normalize.
    for bad in ("LLM-supported", "User-confirmed", "probable"):
        with pytest.raises(NotInVocabulary):
            _write(p6_conn, reliability_state=bad)
    assert facts_for_file(p6_conn, FILE_ID, CONTENT_HASH) == []


def test_a_foreign_origin_is_refused(p6_conn):
    with pytest.raises(NotInVocabulary):
        _write(p6_conn, origin="guess")
    assert facts_for_file(p6_conn, FILE_ID, CONTENT_HASH) == []


def test_the_five_origins_are_the_specs_five_in_the_specs_order(p6_conn):
    assert FACT_ORIGINS == ("deterministic_extractor", "rule", "llm_interpretation",
                            "user_correction", "user_approved_folder")


def test_each_origin_has_a_named_constant_so_no_consumer_needs_an_index(p6_conn):
    # Preamble §3.1. An index is single-homed and unreadable, and it couples every
    # consumer to this tuple's ORDER -- reorder it and every fact three other tasks
    # write is relabelled with no test failing. This test is what makes the literal
    # safe to spell here and nowhere else.
    named = (DETERMINISTIC_EXTRACTOR, RULE, LLM_INTERPRETATION, USER_CORRECTION,
             USER_APPROVED_FOLDER)
    assert named == FACT_ORIGINS
    assert len(set(named)) == 5


def test_a_fact_naming_a_field_outside_the_catalogue_is_refused(p6_conn):
    # §3.5: "The LLM is not allowed to invent a new fact schema, create an
    # unsupported field". Writing a fact is not a back door into creating a field.
    with pytest.raises(FieldNotInCatalogue):
        _write(p6_conn, field_key="vibe")
    assert p6_conn.execute(
        "SELECT COUNT(*) FROM fields WHERE field_key = 'vibe'").fetchone()[0] == 0


def test_a_value_belonging_to_another_field_cannot_be_attached(p6_conn):
    # §3.12: "a value belongs to exactly one field", which is §3.8's role separation.
    # A client named BUSIB 4300 is not the subject BUSIB 4300.
    other = _value(p6_conn, field_key=OTHER_FIELD)
    with pytest.raises(ValueError):
        _write(p6_conn, field_key=FIELD, value_id=other)
    assert facts_for_file(p6_conn, FILE_ID, CONTENT_HASH) == []


def test_a_fact_cannot_cite_a_value_that_does_not_exist(p6_conn):
    with pytest.raises(KeyError):
        _write(p6_conn, value_id="sha256:" + "0" * 64)


# ------------------------------------------------------------------ §8.2 provenance
def test_a_fact_creation_event_is_appended_through_p1(p6_conn):
    fact_id = _write(p6_conn)
    rows = list(p6_conn.execute("SELECT * FROM events ORDER BY event_id"))
    assert len(rows) == 1
    event = rows[0]
    # Spelled with a SPACE, and already one of §8.2's nineteen -- P6 registers none.
    assert event["event_type"] == "fact creation"
    assert event["subsystem"] == "P6"          # M8: P6 authors, P1 writes
    assert event["file_id"] == FILE_ID
    assert event["content_hash"] == CONTENT_HASH
    # §8.2's "structured explanation or evidence reference", not a sentence.
    explanation = json.loads(event["explanation"])
    assert explanation["fact_id"] == fact_id
    assert explanation["field"] == FIELD
    assert explanation["evidence_refs"] == [_key("BUSIB 4300")]


def test_this_task_appends_no_event_of_any_other_type(p6_conn):
    _write(p6_conn)
    _write(p6_conn, value_id=_value(p6_conn, canonical="Spring 2026"),
           evidence_refs=(_key("Spring 2026"),))
    types = {r["event_type"] for r in p6_conn.execute("SELECT event_type FROM events")}
    assert types == {"fact creation"}


def test_writing_the_same_fact_twice_is_one_row_and_one_event(p6_conn):
    first = _write(p6_conn)
    second = _write(p6_conn)
    assert first == second
    assert len(facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)) == 1
    assert p6_conn.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 1


def test_the_record_id_projection_lets_p1_address_the_table(p6_conn):
    # P1's `mark_superseded` and `chain` are "... WHERE record_id = ?", and P6's
    # published key is `fact_id`. `record_id` is a VIRTUAL projection of it: it
    # stores nothing, cannot diverge, and is absent from `table_info`, which is why
    # it is not in FILE_FACTS_COLUMNS. P4 solved this the same way.
    hidden = {r["name"]: r["hidden"]
              for r in p6_conn.execute("PRAGMA table_xinfo(file_facts)")}
    assert hidden["record_id"] == 2
    assert "record_id" not in FILE_FACTS_COLUMNS

    old = _write(p6_conn)
    new = _write(p6_conn, cache_key="sha256:" + "d" * 64)
    assert old != new
    # Task 16 owns supersession; this only proves P1 can address the table at all.
    mark_superseded(p6_conn, "file_facts", old_id=old, new_id=new,
                    reason="a later pass at a different cache key")
    rows = {r["fact_id"]: r for r in facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)}
    assert rows[old]["superseded_by"] == new
    assert rows[new]["supersedes"] == old


def test_write_fact_never_sets_preferred(p6_conn):
    # M1 places `preferred` on this table and nowhere else, and Task 18 is the only
    # thing that writes it. A fact is not preferred because it is the only one.
    fact_id = _write(p6_conn)
    row = [r for r in facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)
           if r["fact_id"] == fact_id][0]
    assert row["preferred"] is None


# ------------------------------------------------------------------- the read (§3.4)
def test_facts_for_file_is_per_file_version(p6_conn):
    # Every P6 read is per content hash: the cache key and the abstention row both
    # are (§3.4, §8.2). A prior version's facts are not this version's.
    _write(p6_conn)
    _write(p6_conn, content_hash=OTHER_HASH)
    assert len(facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)) == 1
    assert len(facts_for_file(p6_conn, FILE_ID, OTHER_HASH)) == 1
    assert facts_for_file(p6_conn, "file-2", CONTENT_HASH) == []


def test_the_read_order_is_imposed_and_not_inherited_from_insertion(p6_conn):
    # Written in one order, read back in another -- because the read sorts. Without
    # this the same corpus written in a different order reads differently and §8.5's
    # replay reports a regression when nothing changed.
    # Inserted subject-then-client; read back client-then-subject.
    for field_key, canonical in ((FIELD, "BUSIB 4300"), (OTHER_FIELD, "Zeta LLP")):
        _write(p6_conn, field_key=field_key,
               value_id=_value(p6_conn, field_key=field_key, canonical=canonical),
               evidence_refs=(_key(canonical),))
    assert [r["field_key"] for r in facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)] == [
        OTHER_FIELD, FIELD]      # "client" before "subject", alphabetically
```

- [ ] **Step 2: Run the test and confirm it FAILS for the right reason**

Run: `pytest tests/p6/test_p6_file_facts.py -q`

Expected: **collection error** — `ModuleNotFoundError: No module named 'facts.file_facts'`, raised at
the `from facts.file_facts import ...` line. All 25 tests error at collection; none run.

- [ ] **Step 3: Add the `file_facts` DDL to `src/facts/schema.py`**

Append this to `src/facts/schema.py`, after `VALUES_DDL`, and put the one new import at the top of the
file beside the existing ones. It imports P1's `supersede_ddl` so the three supersede column names are
P1's spelling rather than P6's typing (M1).

**One assumption on Task 1, stated so it can be checked rather than discovered.** `event_defaults(**fields)
-> dict` is expected to return a mapping that already carries `subsystem = "P6"`, a
`component_version`, and an `observed_at` from the part's one clock, with the caller's fields merged
in. `write_fact` calls it **once** and reads `observed_at` back out of the returned dict for the row's
`created_at`, so the fact and its creation event share one instant from one clock and this module owns
no clock of its own. If Task 1's `event_defaults` does not fill `observed_at`, that is a Task 1 defect
and `append_event` will raise `MalformedEvent` at the first test here — which is the right failure.

```python
from database_agent.supersede import supersede_ddl

#: §3.12's `file_facts`: "connects one file to one field and one value while retaining
#: the evidence and reliability state that justify the connection."
#:
#: THE NEGATIVE CONTRACT. No path column, no destination column, no folder column, no
#: node column, no group column -- §3.14 ("A fact such as subject = BUSIB 4300 does not
#: itself dictate one permanent folder path") and §4.3. A reviewer checks it here, and
#: `tests/p6/test_p6_file_facts.py` checks it against `PRAGMA table_info` so a future
#: `destination_node_id` fails on the day it is added.
#:
#: `content_hash` is not in the SPEC's column list and is required: `facts_for_file` is
#: published per file version, and the cache key that carries the hash is a digest and
#: cannot be filtered on. Reported to the lead as a gap in the SPEC's shape.
#:
#: `field_key` is the field key (brief §17). It carries no REFERENCES clause: foreign
#: keys are ON and a parent column that is not PRIMARY KEY or UNIQUE raises `foreign
#: key mismatch` at INSERT. Task 2 now declares `fields.field_key` PRIMARY KEY so the
#: clause would bind, but `get_field` remains the gate the SPEC names and the one that
#: raises a refusal with a name on it. `value_id` DOES reference
#: `"values"`, whose `value_id` is a primary key, so a fact can never cite a value that
#: does not exist.
#:
#: `record_id` is a VIRTUAL projection of `fact_id`, so P1's `mark_superseded` and
#: `chain` -- both `... WHERE record_id = ?` -- address this table unchanged. It stores
#: nothing, cannot diverge, and does not appear in `PRAGMA table_info`. Same device,
#: same reason, as P4's `evidence` table.
FILE_FACTS_DDL = f"""
CREATE TABLE IF NOT EXISTS file_facts (
    fact_id            TEXT PRIMARY KEY,
    record_id          TEXT GENERATED ALWAYS AS (fact_id) VIRTUAL,
    file_id            TEXT NOT NULL,
    content_hash       TEXT NOT NULL,
    field_key           TEXT NOT NULL,
    value_id           TEXT NOT NULL REFERENCES "values" (value_id),
    reliability_state  TEXT NOT NULL,
    origin             TEXT NOT NULL,
    evidence_refs      TEXT NOT NULL,
    cited_quote_refs   TEXT NOT NULL,
    cache_key          TEXT NOT NULL,
    model_identifier   TEXT,
    prompt_fingerprint TEXT,
    internal_score     REAL,
    active             INTEGER NOT NULL,
    {supersede_ddl("file_facts")},
    preferred          INTEGER,
    rejection_reason   TEXT,
    created_at         TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS file_facts_version ON file_facts (file_id, content_hash);
CREATE INDEX IF NOT EXISTS file_facts_field ON file_facts (field_key);
CREATE INDEX IF NOT EXISTS file_facts_value ON file_facts (value_id);
CREATE TRIGGER IF NOT EXISTS file_facts_no_delete
BEFORE DELETE ON file_facts
BEGIN SELECT RAISE(ABORT, 'a fact is superseded by a later fact, never removed (§8.2)'); END;
"""
```

Then one more line in `create_facts_schema`:

```python
def create_facts_schema(conn: sqlite3.Connection) -> None:
    """Create every P6-owned table. Idempotent. P1's `create_schema` runs first, and
    P4's `create_evidence_schema` before any read."""
    conn.executescript(FIELDS_DDL)
    conn.executescript(VALUES_DDL)
    conn.executescript(FILE_FACTS_DDL)
```

- [ ] **Step 4: Write `src/facts/file_facts.py`**

```python
# src/facts/file_facts.py
"""§3.12's `file_facts` -- the table that "connects one file to one field and one value
while retaining the evidence and reliability state that justify the connection."

There is ONE fact table and one set of six reliability states. §3.5: "A file fact is
not inherently rule-based or LLM-based. It is the common format into which both systems
write their conclusions." So the producer is a COLUMN (`origin`), not a second schema:
there is no rules table and no model table, and this module is the only writer.

THE NEGATIVE CONTRACT, which is this module's reason to exist as a separate file:

    §3.14  "Facts remain separate from the future destination tree. A fact such as
            subject = BUSIB 4300 does not itself dictate one permanent folder path."
    §4.3   a fact records no group membership; §4.1, the graph "does not automatically
            copy those missing facts onto sparse files".

`file_facts` therefore has no path, destination, folder, node or group column, and
`write_fact` has no such keyword either -- a keyword argument is the other way a
destination gets in. `FILE_FACTS_COLUMNS` and `FORBIDDEN_COLUMN_SUBSTRINGS` are
published so a reviewer, `unresolved` (Task 5) and Tasks 16-19 all check the same
contract against the same list rather than three lists that drift.

A fact is never separable from its evidence (§3.1: "Every fact preserves where it came
from"). Every non-`user_confirmed` fact carries at least one `evidence_refs` entry and
every entry is a P4 observation KEY -- content-addressed, `sha256:`-prefixed, and
excluding `extractor_version` by construction, which is what makes a citation recorded
today still resolve after an extractor upgrade (M14, §8.7).

`fact_id` is content-addressed over the whole conclusion, so writing the same fact at
the same cache key twice is one row and one event. §8.2's supersession is unaffected: a
later pass cites `ocr`-tier observations, so §3.4's `analysis_tier` differs, so the
cache key differs, so the id differs and the new fact supersedes rather than collides.

This module does not set `preferred` (Task 18) and appends no event but `fact creation`.
"""
from __future__ import annotations

import json
import sqlite3

from database_agent.events import append_event
from database_agent.supersede import SUPERSEDE_COLUMNS

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import check

from facts.authorship import AUTHORED_EVENT_TYPES, event_defaults
from facts.fields import get_field
from facts.states import STATES, USER_CONFIRMED

#: §3.1's five producers, one named constant each. This module owns the literal
#: spelling; every consumer imports the CONSTANT, never an index into the tuple
#: (preamble §3.1: an index couples the consumer to this tuple's order, so a reorder
#: relabels every fact with no test failing).
DETERMINISTIC_EXTRACTOR: str = "deterministic_extractor"
RULE: str = "rule"
LLM_INTERPRETATION: str = "llm_interpretation"
USER_CORRECTION: str = "user_correction"
USER_APPROVED_FOLDER: str = "user_approved_folder"

#: The five in the order the SPEC's `file_facts` shape publishes them:
#: "deterministic extractor | rule | LLM interpretation | user correction |
#: user-approved folder". For iteration and membership; to NAME one origin, import
#: the constant above.
FACT_ORIGINS: tuple[str, ...] = (
    DETERMINISTIC_EXTRACTOR, RULE, LLM_INTERPRETATION,
    USER_CORRECTION, USER_APPROVED_FOLDER,
)

#: What the table is, in declaration order, minus the VIRTUAL `record_id`, which
#: `PRAGMA table_info` does not report. The test asserts this EQUALS the live column
#: set, so this tuple cannot describe a table that does not exist.
FILE_FACTS_COLUMNS: tuple[str, ...] = (
    "fact_id", "file_id", "content_hash", "field_key", "value_id",
    "reliability_state", "origin", "evidence_refs", "cited_quote_refs",
    "cache_key", "model_identifier", "prompt_fingerprint", "internal_score",
    "active", *SUPERSEDE_COLUMNS, "preferred", "rejection_reason", "created_at",
)

#: §3.14 and §4.3 as a checkable list. A SUBSTRING list, not a name list: a future
#: `destination_node_id` must fail on the day it is added, not on the day someone
#: reads the schema. Task 5's `unresolved` imports this and obeys the same contract.
FORBIDDEN_COLUMN_SUBSTRINGS: tuple[str, ...] = (
    "path", "destination", "folder", "node", "group",
)

#: A P4 observation key is `sha256:` + 64 hex (M14, verified by execution).
_KEY_PREFIX = "sha256:"
_KEY_LENGTH = len(_KEY_PREFIX) + 64


class EvidenceRequired(Exception):
    """§3.1: a fact is never separable from its evidence.

    Raised when a non-`user_confirmed` fact carries no citation, or when a citation is
    not a P4 observation key. Both are refusals to store, never warnings: a fact whose
    provenance cannot be resolved is the invisible permanent label §3.1 exists to
    prevent.
    """


def _checked_field_key(conn: sqlite3.Connection, field_key: str) -> str:
    """`get_field` raises `FieldNotInCatalogue` for a key outside Task 2's closed
    catalogue, so writing a fact is not a back door into creating a field (§3.5)."""
    return get_field(conn, field_key)["field_key"]


def _checked_refs(refs, reliability_state: str) -> tuple[str, ...]:
    """The M14 citation rule. Sorted, because P4's reads are in insertion order and
    this column must not inherit it (§8.5's replay compares runs)."""
    ordered = tuple(sorted(set(refs)))
    if reliability_state != USER_CONFIRMED and not ordered:
        raise EvidenceRequired(
            f"a {reliability_state} fact cites at least one observation (§3.1); "
            "only a user_confirmed fact may stand without one"
        )
    for ref in ordered:
        if not ref.startswith(_KEY_PREFIX) or len(ref) != _KEY_LENGTH:
            raise EvidenceRequired(
                f"{ref!r} is not a P4 observation key; a citation is the "
                "content-addressed key, never an observation_id or a row id (M14)"
            )
    return ordered


def _fact_identity(*, file_id: str, content_hash: str, field_key: str, value_id: str,
                   reliability_state: str, origin: str, cache_key: str,
                   evidence_refs: tuple[str, ...]) -> str:
    """The same conclusion, from the same evidence, at the same cache key, is the same
    fact -- not a second one. `sha256_of` is length-prefixed and injective."""
    return sha256_of("facts.file_facts", file_id, content_hash, field_key, value_id,
                     reliability_state, origin, cache_key,
                     canonical_json(list(evidence_refs)))


def write_fact(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
               field_key: str, value_id: str, reliability_state: str, origin: str,
               evidence_refs, cache_key: str, active: bool,
               cited_quote_refs=(), model_identifier: str | None = None,
               prompt_fingerprint: str | None = None,
               internal_score: float | None = None,
               rejection_reason: str | None = None) -> str:
    """Write one fact and author its `fact creation` event. Returns the fact id.

    No path, no destination, no folder, no group -- not as a column and not as a
    keyword (§3.14, §4.3).

    Idempotent: the same conclusion at the same cache key returns the existing row and
    appends no second event, or the provenance log would count one fact twice.
    """
    check(reliability_state, STATES, name="reliability state")
    check(origin, FACT_ORIGINS, name="fact origin")
    if not cache_key:
        raise ValueError("a fact records the cache key it was computed under (§3.4)")
    refs = _checked_refs(evidence_refs, reliability_state)
    quotes = tuple(sorted(set(cited_quote_refs)))
    field_key = _checked_field_key(conn, field_key)

    value = conn.execute(
        'SELECT field_key FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    if value is None:
        raise KeyError(f"unknown value {value_id!r}")
    if value["field_key"] != field_key:
        raise ValueError(
            f"value {value_id!r} belongs to field {value['field_key']!r}, not "
            f"{field_key!r}; a value belongs to exactly one field (§3.12), which is "
            "§3.8's role separation"
        )

    fact_id = _fact_identity(
        file_id=file_id, content_hash=content_hash, field_key=field_key,
        value_id=value_id, reliability_state=reliability_state, origin=origin,
        cache_key=cache_key, evidence_refs=refs)
    existing = conn.execute(
        "SELECT fact_id FROM file_facts WHERE fact_id = ?", (fact_id,)
    ).fetchone()
    if existing is not None:
        return existing["fact_id"]

    # One call, so the fact row's timestamp and its creation event's timestamp are the
    # same instant from the same clock. `authorship` owns that clock; this module has
    # none of its own.
    event = event_defaults(
        event_type=AUTHORED_EVENT_TYPES[0],
        file_id=file_id,
        content_hash=content_hash,
        explanation=canonical_json({
            "fact_id": fact_id,
            "field": field_key,
            "value_id": value_id,
            "reliability_state": reliability_state,
            "origin": origin,
            "cache_key": cache_key,
            "evidence_refs": list(refs),
        }),
    )
    conn.execute(
        "INSERT INTO file_facts (fact_id, file_id, content_hash, field_key, value_id, "
        "reliability_state, origin, evidence_refs, cited_quote_refs, cache_key, "
        "model_identifier, prompt_fingerprint, internal_score, active, "
        "supersedes, superseded_by, supersede_reason, preferred, rejection_reason, "
        "created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "NULL, NULL, NULL, NULL, ?, ?)",
        (fact_id, file_id, content_hash, field_key, value_id, reliability_state,
         origin, canonical_json(list(refs)), canonical_json(list(quotes)), cache_key,
         model_identifier, prompt_fingerprint, internal_score, int(bool(active)),
         rejection_reason, event["observed_at"]),
    )
    append_event(conn, **event)
    return fact_id


def facts_for_file(conn: sqlite3.Connection, file_id: str,
                   content_hash: str) -> list[sqlite3.Row]:
    """Every fact for one file VERSION, with its field key and canonical value joined
    on so no caller reassembles them.

    Per content hash, because the cache key and the abstention row both are (§3.4,
    §8.2). Sorted, because P4's reads are in insertion order and this one imposes its
    own. Unfiltered: selecting by `active`, by `preferred` or by reliability state is
    the proposal-eligible read, which Task 24 owns.
    """
    return list(conn.execute(
        'SELECT f.*, fl.field_key AS field_key, '
        '       v.canonical_value AS canonical_value, '
        '       v.display_label AS display_label '
        'FROM file_facts AS f '
        'JOIN fields AS fl ON fl.field_key = f.field_key '
        'JOIN "values" AS v ON v.value_id = f.value_id '
        'WHERE f.file_id = ? AND f.content_hash = ? '
        'ORDER BY fl.field_key, v.canonical_value, f.fact_id',
        (file_id, content_hash),
    ))
```

- [ ] **Step 5: Run the test and confirm it passes**

Run: `pytest tests/p6/test_p6_file_facts.py -v`

Expected: PASS — **25 passed**. Four are the ones a reviewer should read the output of:

- `test_the_module_declares_exactly_the_table_it_has` passes only if `FILE_FACTS_COLUMNS` and the DDL
  agree column for column and in order, which is what makes every other schema assertion in the file
  an assertion about the database rather than about the module.
- `test_the_forbidden_substring_guard_is_not_vacuous` passes because the scratch table's three
  offending columns are all caught. If it ever reports `[]`, the negative contract is proving nothing.
- `test_the_record_id_projection_lets_p1_address_the_table` passes because `PRAGMA table_xinfo`
  reports `record_id` with `hidden == 2` **and** because P1's own `mark_superseded` completes against
  the table — verified behaviour, not a claim about the DDL.
- `test_a_user_confirmed_fact_may_stand_without_an_observation` passes on Task 1's `USER_CONFIRMED`,
  never on a string literal and never on an index, so `facts.states` is what pins the spelling.

- [ ] **Step 6: Run the whole P6 suite, so Tasks 1–3 are still green**

Run: `pytest tests/p6 -q`

Expected: PASS. `create_facts_schema` now creates three tables and is still idempotent, and Task 3's
`values` tests are unaffected because `file_facts` references `"values"` and not the other way round.
A failure in `tests/p6/test_p6_values.py` here means the new foreign key changed a delete or insert
path in Task 3 and is a real finding.

- [ ] **Step 7: Commit**

```bash
git add src/facts/file_facts.py src/facts/schema.py tests/p6/test_p6_file_facts.py
git commit -m "feat(P6): §3.12's fact row — evidence required, and no path, destination, folder or group"
```

---

### Task 5: `unresolved` — the abstention row, and its thirteen reasons

**Files:**
- Create: `src/facts/unresolved.py`
- Modify: `src/facts/vocabulary.py`, `src/facts/schema.py`
- Test: `tests/p6/test_p6_unresolved.py`

**Interfaces:**
- Consumes: `facts.fields.get_field`, `facts.fields.FieldNotInCatalogue`;
  `evidence_shape.vocabulary.check`, `evidence_shape.vocabulary.NotInVocabulary`;
  `evidence_shape.canonical.canonical_json`; `database_agent.supersede.supersede_ddl`.
- Produces: `UNRESOLVED_REASONS: tuple[str, ...]` (the thirteen) **and one named constant per reason
  — `NO_CANDIDATE_EVIDENCE`, `BELOW_SCORE_THRESHOLD`, `BELOW_MARGIN`, `CONTEXT_CHECK_FAILED`,
  `CONTEXT_TRUNCATED`, `FIELD_NOT_IN_ACTIVE_SCHEMA`, `CITATION_ABSENT_FROM_EVIDENCE`,
  `NORMALIZATION_FAILED`, `CONTRADICTED_BY_STRONGER_FACT`, `MODEL_RETURNED_UNKNOWN`,
  `DISCOUNTED_TOOL_METADATA`, `PRIVACY_WITHHELD`, `BUDGET_DEFERRED`**,
  `ATTEMPTED_PRODUCERS: tuple[str, str, str]` (`direct`, `rule`, `llm`) **and one named constant per
  member — `DIRECT_ROUTE`, `RULE_ROUTE`, `LLM_ROUTE`** (suffixed, because `facts.states.DIRECT` and
  `facts.file_facts.RULE` are different vocabularies and several modules import both),
  `write_unresolved(conn, *, file_id, content_hash, field_key, reason, attempted_producers,
  evidence_refs, cache_key) -> str`,
  `unresolved_for_file(conn, file_id, content_hash, *, field_key=None, reason=None) -> list[sqlite3.Row]`,
  `NOT_ABSTENTIONS: frozenset[str]` (`budget_deferred`, `privacy_withheld`).

**Done-means:** 18, 19.

#### What this task is for, in one paragraph

§3.6 says a model that cannot cite sufficient evidence *"must return unknown"*, and stops there — no
fact. **B7 says no fact is not enough**, because §8.5 asks under Fact quality *"Did it abstain when
evidence was absent?"* and an absent row cannot answer a question about absence. So every refusal P6
makes writes a row naming the field it attempted, the reason, the routes it tried, and the
observation keys it looked at. Two rules make the row trustworthy and both are tests below: it is
**not a weak fact** (no `value_id`, no reliability state, absent from every fact read), and
`budget_deferred` and `privacy_withheld` are **not abstentions** — §8.6 requires the product to
*"mark the deferred stage, and leave the file or group in review rather than guessing"*, so that
reporting *"avoids the false impression that an unprocessed file was understood and found
unimportant"*. Merging them would report a budget stop as a considered refusal, which is that
impression exactly.

#### Verified by execution, 2026-08-22 — three things this task's shape depends on

Run before the code below was written, because reading a signature instead of importing it has cost
this project three defects.

```text
supersede_ddl("unresolved")   -> "supersedes TEXT, superseded_by TEXT, supersede_reason TEXT"
SUPERSEDE_COLUMNS             == ("supersedes", "superseded_by", "supersede_reason")
check(v, vocab, *, name)      -> v, or raises NotInVocabulary (a ValueError subclass)
```

1. **A VIRTUAL generated column does not appear in `PRAGMA table_info`.** Executed against a table
   built exactly like the DDL below: `PRAGMA table_info(unresolved)` returned
   `['unresolved_id', 'supersedes', 'superseded_by', 'supersede_reason']` and **not** `record_id`,
   while `SELECT record_id FROM unresolved` returned the `unresolved_id`. Both tests below depend on
   this: the negative-contract test reads `PRAGMA table_info` and would otherwise have to whitelist a
   column, and the `record_id` test must use a `SELECT` because the pragma cannot see it.

2. **P1's `mark_superseded` works across the two tables, in the one direction Task 5 needs, and
   silently declines the other.** Executed with an `unresolved` row `u1` and a `file_facts` row `f1`:
   `mark_superseded(conn, "unresolved", old_id="u1", new_id="f1", reason="…")` set
   `superseded_by="f1"` and `supersede_reason` on the `unresolved` row, left the row readable, and
   left `file_facts.supersedes` as `None` — because its last statement is
   `UPDATE unresolved SET supersedes = ? WHERE record_id = ?` and no `unresolved` row has id `f1`, so
   it matches zero rows and raises nothing. The forward link is recorded, the back-pointer is not.
   **This is stated rather than fixed.** `mark_superseded` takes one `table`, so a cross-table
   back-pointer is not expressible through P1's published surface; `src/facts/supersede.py` (§8.2,
   Task 23) owns supersession as an operation and is where a back-pointer would be decided. Task 5
   owns only the **schema affordance** — the three supersede columns and the `record_id` projection —
   and asserts the `unresolved` side of the link, which is the half Done-means 19 and SPEC rule 3
   require: *"A later fact … does not delete the row — it supersedes it, and the row remains
   readable."*

3. `record_file(...)` → `get_file(conn, file_id)["content_hash"]` is 64 lowercase hex with **no**
   `sha256:` prefix. Observation **keys** are `sha256:`-prefixed; content hashes are not. The two
   never share a validator.

#### Three rulings this task makes, each because leaving it implicit would be worse

- **`evidence_refs` may be empty; `attempted_producers` may be empty too.** The SPEC's schema is
  explicit for the first — *"the observation keys considered, where any were (may be empty)"*. The
  second follows from `budget_deferred`: an §8.6 ceiling can be reached **before** any producer runs,
  so a required-non-empty producer list would make the one reason that most needs recording
  unwritable. Neither absence is silent: both columns are `NOT NULL` and hold `[]`, so a reader can
  tell "looked at nothing" from "column never written".
- **`evidence_refs` entries are validated for the `sha256:` prefix, and nothing else.** The prefix is
  what distinguishes M14's `observation_key` from an `observation_id` or a row id, and getting that
  wrong is the defect Done-means 30 exists to catch. Whether the key **resolves** is not checked
  here: `observations_by_key` on an unknown key returns `[]` rather than raising, so a resolution
  check would need a policy for the empty result, and that policy is Task 7's.
- **The row is never de-duplicated and never updated.** Two abstentions for the same
  `(file_id, content_hash, field_key)` under two different cache keys are two rows, because §3.4's key
  is what makes them different events. `write_unresolved` only ever INSERTs.

---

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_unresolved.py
"""B7 — Done-means 18 and 19. The abstention is a ROW, and two of the thirteen
reasons are not abstentions at all.

§3.6 stops at "no fact". §8.5 asks "Did it abstain when evidence was absent?" and an
absent row cannot answer a question about absence, which is the whole of B7.
"""
from __future__ import annotations

import json

import pytest

from database_agent.supersede import mark_superseded

from evidence_shape.observation import observation_key
from evidence_shape.vocabulary import NotInVocabulary

from facts.fields import FieldNotInCatalogue
from facts.file_facts import (
    RULE, FORBIDDEN_COLUMN_SUBSTRINGS, facts_for_file, write_fact,
)
from facts.states import VALIDATED
from facts.unresolved import (
    ATTEMPTED_PRODUCERS, BELOW_MARGIN, BUDGET_DEFERRED, DIRECT_ROUTE, LLM_ROUTE,
    NOT_ABSTENTIONS, NO_CANDIDATE_EVIDENCE, PRIVACY_WITHHELD, RULE_ROUTE,
    UNRESOLVED_REASONS, unresolved_for_file, write_unresolved,
)
from facts.values import ensure_value

FILE_ID = "file-syllabus"
HASH = "6243c215e75e0f4a1d0c3b9e8a77215d5a4c9f6e2b1d0348ac59e7b0d1f2a3b4"
OTHER_HASH = "0f1e2d3c4b5a69788796a5b4c3d2e1f00f1e2d3c4b5a69788796a5b4c3d2e1f0"
CACHE_KEY = "sha256:cache-native-1"

#: The SPEC's thirteen, in the SPEC's own table order. Spelled here so the test is a
#: second, independent copy of the list rather than an echo of the module under test.
SPEC_THIRTEEN = (
    "no_candidate_evidence",
    "below_score_threshold",
    "below_margin",
    "context_check_failed",
    "context_truncated",
    "field_not_in_active_schema",
    "citation_absent_from_evidence",
    "normalization_failed",
    "contradicted_by_stronger_fact",
    "model_returned_unknown",
    "discounted_tool_metadata",
    "privacy_withheld",
    "budget_deferred",
)


def _key(raw: str) -> str:
    """A real P4 observation key. It needs no `evidence` row: `observation_key` is a
    pure function of content hash, extractor name, locator and raw value."""
    return observation_key(content_hash=HASH, extractor_name="pdf.text",
                           locator="heading:page=1/heading=2", raw_value=raw)


def _abstained(conn, file_id: str, content_hash: str, field_key: str) -> bool:
    """"Did P6 abstain on this field?" — the question a caller actually asks.

    This is deliberately NOT a published function. `NOT_ABSTENTIONS` is published so
    the caller can compute it; adding a predicate would be a second home for a rule
    §8.6 states once. The three lines are the whole of it.
    """
    rows = unresolved_for_file(conn, file_id, content_hash, field_key=field_key)
    return any(row["reason"] not in NOT_ABSTENTIONS for row in rows)


def _columns(conn) -> list[str]:
    return [row[1] for row in conn.execute("PRAGMA table_info(unresolved)")]


def test_the_thirteen_reasons_are_the_specs_thirteen(p6_conn):
    assert UNRESOLVED_REASONS == SPEC_THIRTEEN
    assert len(UNRESOLVED_REASONS) == 13
    assert len(set(UNRESOLVED_REASONS)) == 13


def test_a_fourteenth_reason_is_refused_at_the_write(p6_conn):
    with pytest.raises(NotInVocabulary):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
            reason="looked_wrong", attempted_producers=(DIRECT_ROUTE,),
            evidence_refs=(), cache_key=CACHE_KEY)
    assert unresolved_for_file(p6_conn, FILE_ID, HASH) == []


def test_the_three_attempted_producers_and_a_fourth_refused(p6_conn):
    assert ATTEMPTED_PRODUCERS == ("direct", "rule", "llm")
    with pytest.raises(NotInVocabulary):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
            reason=NO_CANDIDATE_EVIDENCE, attempted_producers=(DIRECT_ROUTE, "heuristic"),
            evidence_refs=(), cache_key=CACHE_KEY)


def test_the_row_carries_no_value_and_no_reliability_state_column(p6_conn):
    """Asserted from PRAGMA, not from a null check: a nullable `value_id` is a place
    someone will later write a value, and then `unresolved` is a weak fact."""
    columns = _columns(p6_conn)
    assert "value_id" not in columns
    assert "reliability_state" not in columns
    assert not [c for c in columns if "value" in c or "reliab" in c or "state" in c]


def test_the_row_obeys_file_facts_negative_contract(p6_conn):
    """The same list Task 4 publishes, imported rather than copied — one home for the
    forbidden set, so a column named `destination_node_id` fails both tables' tests on
    the day it is added (§3.14, §4.3)."""
    for column in _columns(p6_conn):
        for forbidden in FORBIDDEN_COLUMN_SUBSTRINGS:
            assert forbidden not in column, f"{column} violates the negative contract"


def test_record_id_projects_unresolved_id_so_p1_can_address_the_row(p6_conn):
    unresolved_id = write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        reason=NO_CANDIDATE_EVIDENCE, attempted_producers=(DIRECT_ROUTE, RULE_ROUTE),
        evidence_refs=(), cache_key=CACHE_KEY)
    projected = p6_conn.execute(
        "SELECT record_id FROM unresolved WHERE unresolved_id = ?",
        (unresolved_id,)).fetchone()["record_id"]
    assert projected == unresolved_id
    # Verified by execution: a VIRTUAL generated column is invisible to the pragma,
    # which is exactly why the two tests above can read the pragma unqualified.
    assert "record_id" not in _columns(p6_conn)


def test_a_later_fact_supersedes_the_row_and_does_not_delete_it(p6_conn):
    """SPEC rule 3 and §8.2's worked example: the first pass refused, a later pass
    resolved, and the record of the refusal stays inspectable."""
    unresolved_id = write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        reason=NO_CANDIDATE_EVIDENCE, attempted_producers=(DIRECT_ROUTE, RULE_ROUTE),
        evidence_refs=(), cache_key=CACHE_KEY)
    value_id = ensure_value(
        p6_conn, field_key="subject", canonical_value="BUSIB 4300",
        first_evidence_ref=_key("BUSIB 4300"), origin="automatic")
    # Task 4 owns the literal spelling of `rule` and publishes it as a named
    # constant; this call site imports the constant (preamble §3.1).
    fact_id = write_fact(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        value_id=value_id, reliability_state=VALIDATED, origin=RULE,
        evidence_refs=(_key("BUSIB 4300"),), cache_key="sha256:cache-ocr-1",
        active=True)

    mark_superseded(p6_conn, "unresolved", old_id=unresolved_id, new_id=fact_id,
                    reason="resolved on re-resolution over OCR evidence (§8.2)")

    rows = unresolved_for_file(p6_conn, FILE_ID, HASH)
    assert len(rows) == 1, "supersede must not delete the abstention"
    assert rows[0]["unresolved_id"] == unresolved_id
    assert rows[0]["superseded_by"] == fact_id
    assert rows[0]["supersede_reason"]
    assert rows[0]["reason"] == NO_CANDIDATE_EVIDENCE


def test_an_unresolved_row_is_absent_from_every_fact_read(p6_conn):
    """Done-means 19. The two tables never leak into one another."""
    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        reason=BELOW_MARGIN, attempted_producers=(RULE_ROUTE,),
        evidence_refs=(_key("BUSIB 4300"),), cache_key=CACHE_KEY)
    assert facts_for_file(p6_conn, FILE_ID, HASH) == []


def test_budget_deferred_and_privacy_withheld_are_not_abstentions(p6_conn):
    """B7's second half, and §8.6's "avoids the false impression that an unprocessed
    file was understood and found unimportant". All three are rows; only one is an
    abstention."""
    assert NOT_ABSTENTIONS == frozenset({"budget_deferred", "privacy_withheld"})
    assert NOT_ABSTENTIONS <= set(UNRESOLVED_REASONS)

    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        reason=NO_CANDIDATE_EVIDENCE, attempted_producers=(DIRECT_ROUTE, RULE_ROUTE),
        evidence_refs=(), cache_key=CACHE_KEY)
    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="purpose",
        reason=BUDGET_DEFERRED, attempted_producers=(),
        evidence_refs=(), cache_key=CACHE_KEY)
    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="project",
        reason=PRIVACY_WITHHELD, attempted_producers=(DIRECT_ROUTE, RULE_ROUTE),
        evidence_refs=(), cache_key=CACHE_KEY)

    assert _abstained(p6_conn, FILE_ID, HASH, "subject") is True
    assert _abstained(p6_conn, FILE_ID, HASH, "purpose") is False
    assert _abstained(p6_conn, FILE_ID, HASH, "project") is False
    # All three are still RECORDS. Not an abstention is not the same as not a row.
    assert len(unresolved_for_file(p6_conn, FILE_ID, HASH)) == 3


def test_a_ceiling_reached_before_any_producer_ran_is_writable(p6_conn):
    """`attempted_producers` may be empty, and the column still says so out loud."""
    unresolved_id = write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="purpose",
        reason=BUDGET_DEFERRED, attempted_producers=(),
        evidence_refs=(), cache_key=CACHE_KEY)
    row = unresolved_for_file(p6_conn, FILE_ID, HASH)[0]
    assert row["unresolved_id"] == unresolved_id
    assert json.loads(row["attempted_producers"]) == []
    assert json.loads(row["evidence_refs"]) == []


def test_evidence_refs_hold_observation_keys_and_nothing_else(p6_conn):
    """M14: the citation is a KEY, never an `observation_id` and never a row id."""
    refs = (_key("BUSIB 4300"), _key("Columbia"))
    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
        reason=BELOW_MARGIN, attempted_producers=(RULE_ROUTE,),
        evidence_refs=refs, cache_key=CACHE_KEY)
    stored = json.loads(unresolved_for_file(p6_conn, FILE_ID, HASH)[0]["evidence_refs"])
    assert stored == list(refs)
    assert all(ref.startswith("sha256:") for ref in stored)

    with pytest.raises(ValueError):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="subject",
            reason=BELOW_MARGIN, attempted_producers=(RULE_ROUTE,),
            evidence_refs=("obs-00000001",), cache_key=CACHE_KEY)


def test_a_field_outside_the_catalogue_cannot_be_abstained_on(p6_conn):
    """§3.12 — new values may be created automatically, new fields may not. The rule
    binds the refusal row as hard as it binds the fact row."""
    with pytest.raises(FieldNotInCatalogue):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="vibe_score",
            reason=NO_CANDIDATE_EVIDENCE, attempted_producers=(DIRECT_ROUTE,),
            evidence_refs=(), cache_key=CACHE_KEY)


def test_the_abstention_is_per_file_version_and_the_read_is_totally_ordered(p6_conn):
    """§3.4, §8.2 — the row is per content hash, and the reader imposes its own order
    rather than inheriting insertion order from SQLite."""
    for content_hash, reason in ((HASH, NO_CANDIDATE_EVIDENCE),
                                 (OTHER_HASH, BELOW_MARGIN)):
        write_unresolved(
            p6_conn, file_id=FILE_ID, content_hash=content_hash, field_key="subject",
            reason=reason, attempted_producers=(RULE_ROUTE,),
            evidence_refs=(), cache_key=CACHE_KEY)

    native = unresolved_for_file(p6_conn, FILE_ID, HASH)
    assert [row["reason"] for row in native] == [NO_CANDIDATE_EVIDENCE]
    assert [row["reason"] for row in unresolved_for_file(
        p6_conn, FILE_ID, OTHER_HASH)] == [BELOW_MARGIN]

    write_unresolved(
        p6_conn, file_id=FILE_ID, content_hash=HASH, field_key="purpose",
        reason=PRIVACY_WITHHELD, attempted_producers=(LLM_ROUTE,),
        evidence_refs=(), cache_key=CACHE_KEY)
    rows = unresolved_for_file(p6_conn, FILE_ID, HASH)
    order = [(row["created_at"], row["unresolved_id"]) for row in rows]
    assert order == sorted(order), "the reader imposes its own total order"
    assert len(unresolved_for_file(p6_conn, FILE_ID, HASH,
                                   reason=PRIVACY_WITHHELD)) == 1
    assert len(unresolved_for_file(p6_conn, FILE_ID, HASH,
                                   field_key="purpose")) == 1


def test_the_filters_refuse_a_value_outside_their_vocabulary(p6_conn):
    with pytest.raises(NotInVocabulary):
        unresolved_for_file(p6_conn, FILE_ID, HASH, reason="looked_wrong")
    with pytest.raises(FieldNotInCatalogue):
        unresolved_for_file(p6_conn, FILE_ID, HASH, field_key="vibe_score")
```

- [ ] **Step 2: Run the test and see it fail**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_unresolved.py -x -q
```

**Expected failure:** collection fails before a single test runs —
`ModuleNotFoundError: No module named 'facts.unresolved'`. `src/facts/unresolved.py` does not exist,
so every one of the fourteen tests errors at import. This is the failure to see; a failure inside a
test body at this step would mean the module already existed and the task is mis-scoped.

- [ ] **Step 3: Append P6's third and fourth closed vocabularies to `src/facts/vocabulary.py`**

Task 2 created this module and owns everything already in it (`FIELD_SCOPES` and the field-scope
checks). Append the block below **unchanged**; edit nothing above it. The reasons and the producers
live here rather than in `unresolved.py` because the Global Constraints put P6's closed vocabularies
in **one** module, checked with P4's `check` — the same rule that keeps `FIELD_SCOPES` here.

```python
# ---------------------------------------------------------------------------
# Task 5 — the abstention vocabularies (§3.6, §8.5, §8.6; B7)
# ---------------------------------------------------------------------------

#: The thirteen reasons, one named constant each. This module owns the literal
#: spelling; every call site imports the CONSTANT (preamble §3.1). That
#: `write_unresolved` validates the reason through P4's `check` -- so a misspelling
#: raises `NotInVocabulary` rather than storing -- is true and worth knowing, and it
#: is NOT a reason to spell the reason inline: validation at the seam catches a TYPO,
#: it does not stop the literal being a SECOND HOME.
NO_CANDIDATE_EVIDENCE: str = "no_candidate_evidence"
BELOW_SCORE_THRESHOLD: str = "below_score_threshold"
BELOW_MARGIN: str = "below_margin"
CONTEXT_CHECK_FAILED: str = "context_check_failed"
CONTEXT_TRUNCATED: str = "context_truncated"
FIELD_NOT_IN_ACTIVE_SCHEMA: str = "field_not_in_active_schema"
CITATION_ABSENT_FROM_EVIDENCE: str = "citation_absent_from_evidence"
NORMALIZATION_FAILED: str = "normalization_failed"
CONTRADICTED_BY_STRONGER_FACT: str = "contradicted_by_stronger_fact"
MODEL_RETURNED_UNKNOWN: str = "model_returned_unknown"
DISCOUNTED_TOOL_METADATA: str = "discounted_tool_metadata"
PRIVACY_WITHHELD: str = "privacy_withheld"
BUDGET_DEFERRED: str = "budget_deferred"

#: The thirteen in the SPEC's own table order, for iteration and membership. Each is
#: fired by exactly one place, named in the comment beside it, so a reason with no
#: producer or a producer with no reason is visible by reading this list. To NAME one
#: reason, import the constant above -- never a literal, never an index.
UNRESOLVED_REASONS: tuple[str, ...] = (
    NO_CANDIDATE_EVIDENCE,           # no observation offered a candidate (§3.6)
    BELOW_SCORE_THRESHOLD,           # §3.7 minimum score not cleared
    BELOW_MARGIN,                    # §3.7 margin not cleared, incl. §2.6's conflict
    CONTEXT_CHECK_FAILED,            # §3.5 pattern matched, required context absent
    CONTEXT_TRUNCATED,               # §3.5 check failed on context_truncated = true (§8.6)
    FIELD_NOT_IN_ACTIVE_SCHEMA,      # §3.6 check 1
    CITATION_ABSENT_FROM_EVIDENCE,   # §3.6 check 2
    NORMALIZATION_FAILED,            # §3.6 check 3
    CONTRADICTED_BY_STRONGER_FACT,   # §3.6 check 4
    MODEL_RETURNED_UNKNOWN,          # §3.6 — the model declined
    DISCOUNTED_TOOL_METADATA,        # the §2.2/§2.3 producer/creator discount fired
    PRIVACY_WITHHELD,                # P7's handling class forbids the model route (§8.4)
    BUDGET_DEFERRED,                 # §8.6 ceiling reached — never merged with abstention
)

#: §3.5's three routes, one named constant each. `direct` and `rule` are P6's own;
#: `llm` is P8's, and P6 records that it was tried without owning the call (§3.3).
#: The `_ROUTE` suffix is deliberate: `facts.states.DIRECT` (a reliability state) and
#: `facts.file_facts.RULE` (a fact origin) are different vocabularies that happen to
#: share a word, and four modules import two of the three.
DIRECT_ROUTE: str = "direct"
RULE_ROUTE: str = "rule"
LLM_ROUTE: str = "llm"

ATTEMPTED_PRODUCERS: tuple[str, str, str] = (DIRECT_ROUTE, RULE_ROUTE, LLM_ROUTE)

#: The two reasons that are NOT abstentions (B7, §8.6). A refusal for either of these
#: means the question was never answered on the evidence: the budget stopped the work,
#: or the privacy class forbade the only remaining route. §8.6: "If the budget is
#: exhausted, the product should retain extracted evidence, mark the deferred stage,
#: and leave the file or group in review rather than guessing", and reporting
#: "avoids the false impression that an unprocessed file was understood and found
#: unimportant". Reporting either of these as a considered refusal is that impression.
#:
#: This is a frozenset and not a tuple because it is asked `in` and never iterated for
#: order, and because P2's writer (`record_stage_output`) already enforces the
#: consequence -- outcome `deferred` requires budget_state `ceiling_reached`, and
#: `ceiling_reached` refuses outcome `abstained`. P6 does not re-implement that rule;
#: it names the two reasons that must not be routed into it as abstentions.
NOT_ABSTENTIONS: frozenset[str] = frozenset({BUDGET_DEFERRED, PRIVACY_WITHHELD})
```

- [ ] **Step 4: Add the `unresolved` table to `src/facts/schema.py`**

Task 4 owns this module's shape: one `<TABLE>_DDL` string per table and one tuple of them that
`create_facts_schema` executes. Append the constant below and add `UNRESOLVED_DDL` as the **last**
member of that tuple — `unresolved` references no other P6 table, so its position only has to be
after nothing.

```python
from database_agent.supersede import supersede_ddl

#: §3.6's abstention (B7). Every column here is in the SPEC's `unresolved` sketch, and
#: nothing else is:
#:
#:   - no `value_id` and no `reliability_state`. Not "nullable" -- ABSENT. A nullable
#:     column is a place someone later writes a value, and then the abstention is a
#:     weak `possible` and SPEC rule 1 is gone.
#:   - no path, destination, folder or group column: the same negative contract
#:     `file_facts` carries (§3.14, §4.3), checkable by reading this DDL alone.
#:   - `cache_key` has the same composition as `file_facts` (§3.4), so an abstention is
#:     invalidated by exactly the events that invalidate a fact -- which is what makes
#:     preamble rule 5's pass 4 supersede a pass-2 refusal instead of ignoring it.
#:
#: `record_id` is a VIRTUAL projection of `unresolved_id`, for the same reason P4's
#: `evidence` table carries one: P1's `mark_superseded` and `chain` are literally
#: `... WHERE record_id = ?`, so the projection lets P1's tested functions be reused
#: verbatim rather than written a second time under a second name. It stores nothing,
#: cannot diverge, and does not appear in `PRAGMA table_info`.
#:
#: No foreign key to `files`. P4 made the same choice for the same reason: P6 must be
#: buildable and testable against P4's nineteen fixtures with no scan, no extractor and
#: no `files` row in existence.
UNRESOLVED_DDL = f"""
CREATE TABLE IF NOT EXISTS unresolved (
    unresolved_id       TEXT PRIMARY KEY,
    file_id             TEXT NOT NULL,
    content_hash        TEXT NOT NULL,
    field_key            TEXT NOT NULL,
    reason              TEXT NOT NULL,
    attempted_producers TEXT NOT NULL,
    evidence_refs       TEXT NOT NULL,
    cache_key           TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    {supersede_ddl("unresolved")},
    record_id           TEXT GENERATED ALWAYS AS (unresolved_id) VIRTUAL
);
CREATE INDEX IF NOT EXISTS unresolved_by_version
    ON unresolved (file_id, content_hash);
"""
```

- [ ] **Step 5: Write `src/facts/unresolved.py`**

```python
# src/facts/unresolved.py
"""§3.6's abstention, as a ROW -- B7, Done-means 18 and 19.

§3.6 stops at "no fact": "A model that cannot cite sufficient evidence must return
unknown." §8.5 then asks, under Fact quality, "Did it abstain when evidence was
absent?" -- and an absent row cannot answer a question about absence. P2 cannot tell a
considered refusal from a crash, a skip, or a file that was never reached. So every
refusal P6 makes is recorded here, naming the field it attempted, the reason, the §3.5
routes it tried, and the observation keys it looked at.

Four properties make the row trustworthy, and each is a test rather than a comment:

  1. It is NOT a fact. No `value_id`, no reliability state -- absent from the schema,
     not merely null -- and absent from every fact read including the proposal-eligible
     one. A reader that treats it as a weaker `possible` has broken it.
  2. It obeys `file_facts`' negative contract: no path, destination, folder or group
     column (§3.14, §4.3). The forbidden-substring list is imported from `file_facts`
     rather than copied, so the two tables cannot drift.
  3. A later fact SUPERSEDES it and never deletes it (§8.2, §8.7). This module builds
     the affordance -- P1's three supersede columns and the `record_id` projection --
     and `facts/supersede.py` owns the operation.
  4. `budget_deferred` and `privacy_withheld` are NOT abstentions (§8.6). They are
     rows; they are not answers. `NOT_ABSTENTIONS` is published so a caller can make
     the distinction without a second copy of the rule.

The vocabularies are defined in `facts.vocabulary` -- one home for every closed set P6
owns -- and re-exported here because `facts.unresolved` is the address the rest of the
part imports them from.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Iterable, Sequence

from evidence_shape.canonical import canonical_json
from evidence_shape.vocabulary import check

from facts.fields import get_field
from facts.vocabulary import (
    ATTEMPTED_PRODUCERS, BELOW_MARGIN, BELOW_SCORE_THRESHOLD, BUDGET_DEFERRED,
    CITATION_ABSENT_FROM_EVIDENCE, CONTEXT_CHECK_FAILED, CONTEXT_TRUNCATED,
    CONTRADICTED_BY_STRONGER_FACT, DIRECT_ROUTE, DISCOUNTED_TOOL_METADATA,
    FIELD_NOT_IN_ACTIVE_SCHEMA, LLM_ROUTE, MODEL_RETURNED_UNKNOWN,
    NO_CANDIDATE_EVIDENCE, NORMALIZATION_FAILED, NOT_ABSTENTIONS, PRIVACY_WITHHELD,
    RULE_ROUTE, UNRESOLVED_REASONS,
)

#: The vocabularies are re-exported here, beside `write_unresolved`, because this is
#: the module preamble §3.4 publishes and a call site should import the reason it
#: passes from the same place as the writer it passes it to.
__all__ = [
    "ATTEMPTED_PRODUCERS",
    "BELOW_MARGIN",
    "BELOW_SCORE_THRESHOLD",
    "BUDGET_DEFERRED",
    "CITATION_ABSENT_FROM_EVIDENCE",
    "CONTEXT_CHECK_FAILED",
    "CONTEXT_TRUNCATED",
    "CONTRADICTED_BY_STRONGER_FACT",
    "DIRECT_ROUTE",
    "DISCOUNTED_TOOL_METADATA",
    "FIELD_NOT_IN_ACTIVE_SCHEMA",
    "LLM_ROUTE",
    "MODEL_RETURNED_UNKNOWN",
    "NOT_ABSTENTIONS",
    "NO_CANDIDATE_EVIDENCE",
    "NORMALIZATION_FAILED",
    "PRIVACY_WITHHELD",
    "RULE_ROUTE",
    "UNRESOLVED_REASONS",
    "unresolved_for_file",
    "write_unresolved",
]

#: An observation key is `sha256:`-prefixed (P4's `sha256_of`); an `observation_id` and
#: a content hash are not. The prefix is the whole difference between citing M14's
#: version-independent key and citing a row id that an extractor upgrade invalidates.
_KEY_PREFIX = "sha256:"


def _checked_field_key(conn: sqlite3.Connection, field_key: str) -> str:
    """The catalogue row's identity, resolved through Task 2's published reader.

    Named `_checked_` rather than `_field_key` because after brief §17 it takes a key
    and returns the same key: its whole value is the refusal on the way through.

    `get_field` raises `FieldNotInCatalogue` for a key the catalogue does not carry,
    which is §3.12 -- "it should not invent new fields automatically" -- enforced at
    the abstention row exactly as hard as at the fact row. A refusal naming a field
    that does not exist is not a refusal, it is a typo.
    """
    return get_field(conn, field_key)["field_key"]


def _required(value: str, *, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} is required and must be a non-empty string")
    return value


def _evidence_refs(refs: Iterable[str]) -> list[str]:
    """The observation keys considered, "where any were" -- the SPEC allows none.

    An empty list is stored as `[]` in a NOT NULL column, so "looked at nothing" is
    distinguishable from "column never written". Membership in `evidence` is NOT
    checked here: `observations_by_key` returns `[]` rather than raising for an unknown
    key, so a resolution check would need a policy for the empty result and that policy
    is Task 7's.
    """
    out: list[str] = []
    for ref in refs:
        _required(ref, name="evidence_ref")
        if not ref.startswith(_KEY_PREFIX):
            raise ValueError(
                f"evidence_refs entry {ref!r} is not a P4 observation key: every "
                f"citation is an `observation_key` and starts {_KEY_PREFIX!r} (M14). "
                "An `observation_id` or a row id does not survive an extractor "
                "version bump and is not a citation (§8.7)."
            )
        out.append(ref)
    return out


def _attempted(producers: Iterable[str]) -> list[str]:
    """Which §3.5 routes were tried. May be empty.

    An §8.6 ceiling can be reached BEFORE any producer runs, so requiring at least one
    would make `budget_deferred` -- the reason that most needs recording -- unwritable.
    """
    return [check(one, ATTEMPTED_PRODUCERS, name="attempted_producer")
            for one in producers]


def write_unresolved(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                     field_key: str, reason: str,
                     attempted_producers: Sequence[str],
                     evidence_refs: Sequence[str], cache_key: str) -> str:
    """Record one refusal. Returns the `unresolved_id`.

    Always an INSERT, never an update and never de-duplicated: two refusals for the
    same `(file_id, content_hash, field_key)` under two different §3.4 cache keys are
    two different events, and §8.2 keeps both readable.
    """
    _required(file_id, name="file_id")
    _required(content_hash, name="content_hash")
    _required(cache_key, name="cache_key")
    field_key = _checked_field_key(conn, field_key)
    check(reason, UNRESOLVED_REASONS, name="reason")
    producers = _attempted(attempted_producers)
    refs = _evidence_refs(evidence_refs)

    unresolved_id = uuid.uuid4().hex
    conn.execute(
        """
        INSERT INTO unresolved (
            unresolved_id, file_id, content_hash, field_key, reason,
            attempted_producers, evidence_refs, cache_key, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (unresolved_id, file_id, content_hash, field_key, reason,
         canonical_json(producers), canonical_json(refs), cache_key,
         datetime.now(timezone.utc).isoformat()),
    )
    return unresolved_id


def unresolved_for_file(conn: sqlite3.Connection, file_id: str, content_hash: str, *,
                        field_key: str | None = None,
                        reason: str | None = None) -> list[sqlite3.Row]:
    """Every refusal recorded for one file VERSION, superseded rows included.

    Superseded rows are returned deliberately: SPEC rule 3 says a later fact "does not
    delete the row -- it supersedes it, and the row remains readable as the record of
    what was once refused". A reader that wants only live refusals filters on
    `superseded_by IS NULL` itself; hiding them here would delete the history at the
    read instead of at the write, which is the same loss by a quieter route.

    The order is `(created_at, unresolved_id)` -- P6's own total order, never SQLite's
    insertion order. P4's reads are `ORDER BY rowid`, which is stable within one
    database and is not a property of the corpus, so §8.5's replay would compare a run
    against itself and report a difference.
    """
    clauses = ["file_id = ?", "content_hash = ?"]
    params: list[str] = [file_id, content_hash]
    if field_key is not None:
        clauses.append("field_key = ?")
        params.append(_checked_field_key(conn, field_key))
    if reason is not None:
        clauses.append("reason = ?")
        params.append(check(reason, UNRESOLVED_REASONS, name="reason"))
    return list(conn.execute(
        "SELECT * FROM unresolved WHERE " + " AND ".join(clauses)
        + " ORDER BY created_at, unresolved_id",
        params,
    ))
```

- [ ] **Step 6: Run the test and see it pass**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_unresolved.py -q
```

**Expected:** `14 passed`. Then the whole part, to prove Task 4's table and Task 2's catalogue are
undisturbed by the schema edit:

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6 -q && python3 -m pytest tests -q
```

**Expected:** every P6 test green, and the 1302 P1–P5 tests still green — P6 modified no file outside
`src/facts/` and `tests/p6/`.

- [ ] **Step 7: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/facts/unresolved.py src/facts/vocabulary.py \
  src/facts/schema.py tests/p6/test_p6_unresolved.py && \
git commit -m "feat(P6): unresolved — the abstention is a row, and two of its thirteen reasons are not abstentions"
```

---

---

### Task 6: §3.4's cache key, and what invalidates a fact

**Files:**
- Create: `src/facts/cache.py`
- Test: `tests/p6/test_p6_cache.py`

**Interfaces:**
- Consumes: `evidence_shape.canonical.sha256_of`, `evidence_shape.canonical.canonical_json`,
  `evidence_shape.vocabulary.ANALYSIS_TIERS`, `evidence_shape.vocabulary.check`,
  `evidence_shape.runs.ExtractionRun`. P4's `evidence` and `extraction_runs` tables are read **by
  SQL**, importing no sibling — see *"the two derived parts"* below.
- Produces: `CACHE_KEY_PARTS: tuple[str, ...]` (`content_hash`, `extractor_version`, `analysis_tier`,
  `model_identifier`, `prompt_fingerprint`),
  `fact_cache_key(conn, *, file_id: str, content_hash: str, model_identifier: str | None,
  prompt_fingerprint: str | None) -> str`,
  `is_stale(conn, *, file_id, content_hash, cache_key) -> bool`.

**Done-means:** 15, 16.

#### The design sentence, grepped before it was quoted

`planning/00-database-agent-product-design.md`, one line, one occurrence:

> *"Each extraction result is tied to the content hash and the exact process that produced it. The
> cache key includes content hash, extractor version, analysis tier, model identifier when relevant,
> and prompt fingerprint for model-derived results. This prevents stale results from surviving a
> content rewrite, avoids unnecessary work when a file is merely renamed, and makes model or prompt
> changes auditable."*

Every one of Done-means 15 and 16 is in the third sentence. `CACHE_KEY_PARTS` is the second sentence
in the second sentence's order, and the third sentence is what `is_stale` has to make true:

| the design's clause | what it forces | which test |
|---|---|---|
| *"prevents stale results from surviving a content rewrite"* | a changed `content_hash` is a different key, so the old facts are outside the new slot | Done-means 16, second half |
| *"avoids unnecessary work when a file is merely renamed"* | there is **no path input** — not a nullable one, not an ignored one, none | Done-means 16, first half |
| *"makes model or prompt changes auditable"* | `model_identifier` and `prompt_fingerprint` are parts of the key, so a prompt change re-resolves and both keys stay readable | Done-means 15 |

#### The naming trap, verified live rather than remembered

`extractors.runs.cache_key` **already exists** and is a **different key answering a different
question**. Read from the installed source on 2026-08-22, not from P5's PLAN:

```python
def cache_key(*, content_hash: str, extractor_name: str, extractor_version: str,
              analysis_tier: str, config_fingerprint: str) -> str:
    return canonical_json([content_hash, extractor_name, extractor_version,
                           analysis_tier, config_fingerprint])
```

Three differences, and each of them matters:

- **Different identity.** P5's key identifies an **extraction result** — which extractor, at which
  configuration, produced these observations. P6's identifies a **fact** — which evidence, under
  which model and prompt, produced this conclusion. §3.4's sentence covers both because §3.2 has not
  yet split observation from fact at that point in the design; the two parts split it.
- **Different parts.** P5 carries `extractor_name` and `config_fingerprint`; P6 carries
  `model_identifier` and `prompt_fingerprint`. Neither list is a subset of the other, so neither
  function can be expressed in terms of the other without adding a part that its own question does
  not have.
- **Different return shape.** P5 returns `canonical_json([...])` — a JSON array string. P6 returns
  `sha256_of(...)` — a `sha256:`-prefixed digest, which is the form `file_facts.cache_key` and
  `unresolved.cache_key` store and the form the test at the end of Task 5 already passes
  (`"sha256:cache-native-1"`).

**So `facts` does not import P5's, and the test asserts that by runtime introspection** — no object
in `facts.cache`'s namespace is `extractors.runs.cache_key` and none is the `extractors.runs` module.
Not by searching source text: a text search matches comments and docstrings, and this document's own
docstring names `extractors.runs.cache_key` twice.

**And this is the second implementation of one design sentence, which is a fact about the plan and
not a defect in it.** It is recorded here so a later reviewer meets it as a decision rather than as a
surprise: the design describes one cache key; the built system has two functions, because P4's
observation/fact split gave the sentence two subjects. If they are ever reconciled, the reconciliation
is a P4/P5/P6 seam change and not an edit inside `facts.cache`.

#### The two derived parts — the settled rule, and it is not the one three drafts carried

**`facts.cache` is this task's module and no other task may add to it. This task publishes ONE
helper, `fact_cache_key`, and every producer imports it.** Eight sibling sections had written their
own private `_cache_key` copy of the reconciliation below; one copy is the rule, eight are eight
places for it to drift.

Two of §3.4's five parts are scalars and a file version has many of each — several extractors,
several analysis tiers. The reconciliation is **this function's**, not the caller's, and it is:

> `extractor_version` is `canonical_json` of the sorted distinct `[extractor_name,
> extractor_version]` pairs of **every observation of that file version** — *not* of the
> observations the fact happens to cite — and `analysis_tier` is the **last tier present** across
> the same set, in `ANALYSIS_TIERS` order (`filesystem` < `native` < `ocr` < `llm`). The key is
> therefore one key per **(file version, deterministic pass)**.

**The deciding argument is the abstention.** The SPEC gives `unresolved.cache_key` the *"same
composition as `file_facts` (§3.4), so an abstention is invalidated by the same events that
invalidate a fact"* — and **an abstention with no citations has no cited observations to compute a
key from**. A per-cited-observation rule cannot key the row that Done-means 18 and 19 exist for. One
key per pass answers both, and it is why `file_id` and `content_hash` are the inputs rather than a
set of observations: **a caller cannot hand this function a filtered subset**, which is the whole
defect the rule was written against.

It is also what makes preamble §3.3's supersession work. A later, richer pass adds observations at a
higher tier, so both derived parts move, so the pass lands in a **different cache slot** and
supersedes rather than overwrites (§8.2).

**The two derived parts are read by SQL, importing no sibling.** One query joins P4's `evidence` to
its `extraction_runs`:

```sql
SELECT DISTINCT e.extractor_name, e.extractor_version, r.analysis_tier
  FROM evidence e JOIN extraction_runs r ON r.run_id = e.run_id
 WHERE e.file_id = ? AND e.content_hash = ?
```

`facts.evidence.observations_for_version` answers the same question and this module does **not**
import it, for the reason `is_stale` does not import `facts.file_facts`: every Wave B producer
imports both this module and those, and a module that imports none of its siblings cannot be half of
an import cycle. Column names verified live on 2026-08-22 — `evidence` carries `extractor_name`,
`extractor_version`, `file_id`, `content_hash` and `run_id`; `extraction_runs` carries `run_id` and
`analysis_tier`.

**A file version with no observations at all is not an error.** It is the abstention's own case, and
it keys at `analysis_tier = ANALYSIS_TIERS[0]` with an empty pair list — a real slot, distinct from
every slot that has evidence in it, so an abstention recorded before any extractor ran is not
mistaken for work done after one did.

#### The three rulings this task makes

- **Each part is `canonical_json`-encoded before it is hashed, and that is what makes `None`
  distinguishable from `""`.** `sha256_of` is length-prefixed over `str` parts, so it is injective
  over the tuple it is given — but it takes strings, and `None` is not one. Encoding each part
  through `canonical_json` gives `None` → `null` and `""` → `""` (four characters, including the
  quotes), which are different strings of different lengths, so the digests differ. The skeleton
  calls this *"a property to assert rather than a hazard to avoid"*, and the test asserts it.
- **No coupling rule between `model_identifier` and `prompt_fingerprint` is invented.** §3.4 says
  *"model identifier when relevant"* and *"prompt fingerprint for model-derived results"* and states
  no dependency between them. A guard requiring both-or-neither would be a rule this plan authored,
  and P8 — which does not exist — is the part that would know whether it is true. Both are
  independently `str | None`. The **deterministic** case is the one this plan can assert, and it does:
  both are `None`, on every fact P6 produces with no model configured (Done-means 17).
- **`is_stale` reads `file_facts` and `unresolved`, by SQL, importing neither module.** Both halves
  are deliberate. It reads both because the SPEC's `unresolved` schema says `cache_key` has the
  *"same composition as `file_facts` (§3.4), so an abstention is invalidated by the same events that
  invalidate a fact"* — a file whose pass-2 produced only abstentions has had work done under that
  key, and a reader that saw only `file_facts` would call it stale forever and re-resolve it on every
  loop. It uses SQL rather than importing `facts.file_facts` and `facts.unresolved` because Task 6's
  `Consumes:` block lists neither, and because `direct.py`, `rules.py`, `facets.py`, `families.py`
  and `session.py` all import **both** `facts.cache` and `facts.file_facts` — keeping `facts.cache`
  free of its siblings is what guarantees no import cycle forms as Wave B lands in parallel.

#### What `is_stale` means, stated as one sentence and then as three cases

**`is_stale` is `True` unless at least one record for `(file_id, content_hash)` — a fact or an
abstention — was written under exactly this cache key.**

| case | records for `(file_id, content_hash)` | verdict | why that is right |
|---|---|---|---|
| a rename, content unchanged, same versions | facts under this same key | `False` | §3.4 *"avoids unnecessary work when a file is merely renamed"*. Done-means 16, first half |
| a content rewrite | none — the new `content_hash` is a new slot | `True` | §3.4 *"prevents stale results from surviving a content rewrite"*. Done-means 16, second half |
| a bumped extractor version or a changed prompt fingerprint | facts, but under the **old** key | `True` | Done-means 15 — re-resolution, and the new fact then supersedes the old one |

The "no records at all" case resolving to `True` is the same case as the content rewrite, and it is
the only reading that lets one predicate serve all three: a file version nothing has been computed
for is a file version that needs computing. **`is_stale` does not itself re-resolve, supersede, or
write anything** — Done-means 15's supersession is `facts/supersede.py`'s (Task 23) and the
sequencing is `facts/resolver.py`'s (Task 24). This function answers one question and returns a bool.

---

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_cache.py
"""§3.4 — Done-means 15 and 16. The five-part key, and what invalidates a fact.

"The cache key includes content hash, extractor version, analysis tier, model
identifier when relevant, and prompt fingerprint for model-derived results. This
prevents stale results from surviving a content rewrite, avoids unnecessary work when
a file is merely renamed, and makes model or prompt changes auditable."
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import get_run, record_observation, record_run
from evidence_shape.vocabulary import ANALYSIS_TIERS, NotInVocabulary

from extractors.runs import cache_key as extraction_cache_key

from facts import cache as cache_module
from facts.cache import CACHE_KEY_PARTS, fact_cache_key, is_stale
from facts.file_facts import RULE, write_fact
from facts.states import POSSIBLE, VALIDATED
from facts.unresolved import (
    DIRECT_ROUTE, NO_CANDIDATE_EVIDENCE, RULE_ROUTE, write_unresolved,
)
from facts.values import ensure_value

CLOCK = "2026-08-22T12:00:00+00:00"

#: The design's five parts, in the design's own order, spelled independently of the
#: module under test so the assertion is a comparison and not an echo.
DESIGN_FIVE = ("content_hash", "extractor_version", "analysis_tier",
               "model_identifier", "prompt_fingerprint")

#: One deterministic baseline. `model_identifier` and `prompt_fingerprint` are None
#: because P6 contains no model call of any kind (§3.3) and P8 does not exist.
BASELINE = dict(content_hash="a" * 64, extractor_version="1.0.0",
                analysis_tier="native", model_identifier=None,
                prompt_fingerprint=None)


def _record(conn, tmp_path: Path, *, name: str, body: bytes) -> tuple[str, str]:
    """A real P1 file row, so this test never assumes whether `file_facts` carries a
    foreign key to `files`. Returns `(file_id, content_hash)`."""
    path = tmp_path / "corpus" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=path.suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _write_subject_fact(conn, *, file_id: str, content_hash: str, key: str) -> str:
    ref = observation_key(content_hash=content_hash, extractor_name="pdf.text",
                          locator="heading:page=1/heading=2", raw_value="BUSIB 4300")
    value_id = ensure_value(conn, field_key="subject", canonical_value="BUSIB 4300",
                            first_evidence_ref=ref, origin="automatic")
    # Task 4 owns the literal spelling of `rule` and publishes the named constant.
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key="subject", value_id=value_id,
                      reliability_state=VALIDATED, origin=RULE,
                      evidence_refs=(ref,), cache_key=key, active=True)


def test_the_key_is_exactly_section_3_4s_five_parts(p6_conn):
    assert CACHE_KEY_PARTS == DESIGN_FIVE
    parameters = inspect.signature(fact_cache_key).parameters
    assert tuple(parameters) == CACHE_KEY_PARTS
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in parameters.values())
    assert all(p.default is inspect.Parameter.empty for p in parameters.values()), (
        "every part is supplied by the caller; a defaulted part is a part that "
        "silently stops distinguishing cache slots")


def test_changing_any_one_part_changes_the_key(p6_conn):
    baseline = fact_cache_key(**BASELINE)
    mutations = (
        dict(BASELINE, content_hash="b" * 64),
        dict(BASELINE, extractor_version="2.0.0"),
        dict(BASELINE, analysis_tier="ocr"),
        dict(BASELINE, model_identifier="claude-x/2026-08"),
        dict(BASELINE, prompt_fingerprint="sha256:prompt-1"),
    )
    keys = {baseline} | {fact_cache_key(**one) for one in mutations}
    assert len(keys) == 6, "each of the five parts must move the key on its own"
    assert baseline.startswith("sha256:")
    assert fact_cache_key(**BASELINE) == baseline, "the key is a pure function"


def test_a_rename_cannot_reach_the_key(p6_conn, tmp_path):
    """Done-means 16, first half, at the strongest place to assert it: the key has no
    path input at all -- not ignored, not nullable, absent."""
    parameters = inspect.signature(fact_cache_key).parameters
    for forbidden in ("path", "current_path", "filename", "file_id", "directory_position"):
        assert forbidden not in parameters

    before = _record(p6_conn, tmp_path, name="Syllabus.pdf", body=b"BUSIB 4300")
    after = _record(p6_conn, tmp_path, name="renamed.pdf", body=b"BUSIB 4300")
    assert before[1] == after[1], "same bytes, same content hash (P1 R1)"
    assert (fact_cache_key(**dict(BASELINE, content_hash=before[1]))
            == fact_cache_key(**dict(BASELINE, content_hash=after[1])))


def test_a_rename_triggers_no_re_resolution_and_a_content_change_does(p6_conn, tmp_path):
    """Done-means 16, end to end, through the fact table."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300")
    key = fact_cache_key(**dict(BASELINE, content_hash=content_hash))
    _write_subject_fact(p6_conn, file_id=file_id, content_hash=content_hash, key=key)

    # The rename: P1's identity is the content hash, so the row is the same row and
    # the key is the same key.
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=key) is False

    # The content rewrite: a new content hash is a new slot, and nothing has been
    # computed in it.
    _, rewritten = _record(p6_conn, tmp_path, name="Syllabus-v2.pdf",
                           body=b"BUSIB 4300 revised")
    assert rewritten != content_hash
    rewritten_key = fact_cache_key(**dict(BASELINE, content_hash=rewritten))
    assert is_stale(p6_conn, file_id=file_id, content_hash=rewritten,
                    cache_key=rewritten_key) is True


def test_a_bumped_extractor_version_re_resolves(p6_conn, tmp_path):
    """Done-means 15's trigger. The supersession itself is Task 23's."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300")
    old = fact_cache_key(**dict(BASELINE, content_hash=content_hash))
    _write_subject_fact(p6_conn, file_id=file_id, content_hash=content_hash, key=old)

    bumped = fact_cache_key(**dict(BASELINE, content_hash=content_hash,
                                   extractor_version="2.0.0"))
    assert bumped != old
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=bumped) is True
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=old) is False


def test_a_changed_prompt_fingerprint_re_resolves(p6_conn, tmp_path):
    """§3.4's "makes model or prompt changes auditable" -- both keys stay computable,
    and the fact written under the old one stays readable."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Essay.pdf",
                                    body=b"Columbia")
    first = fact_cache_key(content_hash=content_hash, extractor_version="1.0.0",
                           analysis_tier="llm", model_identifier="model-a",
                           prompt_fingerprint="sha256:prompt-1")
    _write_subject_fact(p6_conn, file_id=file_id, content_hash=content_hash, key=first)
    second = fact_cache_key(content_hash=content_hash, extractor_version="1.0.0",
                            analysis_tier="llm", model_identifier="model-a",
                            prompt_fingerprint="sha256:prompt-2")
    assert first != second
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=second) is True


def test_none_is_distinguishable_from_the_empty_string(p6_conn):
    """P4's `sha256_of` is length-prefixed and injective, and each part is
    canonical_json-encoded before it is hashed, so `null` and `""` are different
    strings of different lengths. A property to assert, not a hazard to avoid."""
    absent = fact_cache_key(**dict(BASELINE, model_identifier=None))
    empty = fact_cache_key(**dict(BASELINE, model_identifier=""))
    assert absent != empty
    assert (fact_cache_key(**dict(BASELINE, prompt_fingerprint=None))
            != fact_cache_key(**dict(BASELINE, prompt_fingerprint="")))
    # And no two parts can be smeared into each other by concatenation.
    assert (fact_cache_key(content_hash="ab", extractor_version="c",
                           analysis_tier="native", model_identifier=None,
                           prompt_fingerprint=None)
            != fact_cache_key(content_hash="a", extractor_version="bc",
                              analysis_tier="native", model_identifier=None,
                              prompt_fingerprint=None))


def test_the_deterministic_fact_carries_neither_model_part(p6_conn):
    """Done-means 17's half of this task: P8 is absent, so both are None and the key
    is still computable. P6 contains no model call of any kind (§3.3)."""
    assert fact_cache_key(**BASELINE).startswith("sha256:")
    assert BASELINE["model_identifier"] is None
    assert BASELINE["prompt_fingerprint"] is None


def test_the_analysis_tier_is_p4s_and_a_fourth_value_is_refused(p6_conn):
    """P6 never infers a tier -- it comes from P4's `ExtractionRun` (Global
    Constraints), and an unknown one raises rather than being hashed."""
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")
    for tier in ANALYSIS_TIERS:
        assert fact_cache_key(**dict(BASELINE, analysis_tier=tier))
    with pytest.raises(NotInVocabulary):
        fact_cache_key(**dict(BASELINE, analysis_tier="ocr_v2"))
    for empty in ("content_hash", "extractor_version"):
        with pytest.raises(ValueError):
            fact_cache_key(**dict(BASELINE, **{empty: ""}))


def test_a_run_supplies_the_two_parts_p6_must_not_invent(p6_conn, tmp_path):
    """Preamble rule 5, at the key: a native run and an OCR run over the same content
    hash land in different cache slots, which is why pass 4 supersedes rather than
    overwrites (§8.2). Both parts are read off P4's run, never inferred."""
    _, content_hash = _record(p6_conn, tmp_path, name="Scan.pdf", body=b"scanned")
    runs = [
        ExtractionRun(run_id=f"run-{tier}", file_id="file-scan",
                      content_hash=content_hash, extractor_name="pdf.text",
                      extractor_version="1.0.0", source_type="text_document",
                      analysis_tier=tier, config={}, completeness="complete",
                      started_at=CLOCK, finished_at=CLOCK)
        for tier in ("native", "ocr")
    ]
    keys = {fact_cache_key(content_hash=run.content_hash,
                           extractor_version=run.extractor_version,
                           analysis_tier=run.analysis_tier,
                           model_identifier=None, prompt_fingerprint=None)
            for run in runs}
    assert len(keys) == 2


def test_an_abstention_counts_as_work_done_under_that_key(p6_conn, tmp_path):
    """The SPEC's `unresolved.cache_key` is "same composition as `file_facts` (§3.4),
    so an abstention is invalidated by the same events that invalidate a fact". A
    reader that saw only `file_facts` would call a file that produced only refusals
    stale forever and re-resolve it on every loop."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Blank.pdf", body=b"   ")
    key = fact_cache_key(**dict(BASELINE, content_hash=content_hash))
    write_unresolved(p6_conn, file_id=file_id, content_hash=content_hash,
                     field_key="subject", reason=NO_CANDIDATE_EVIDENCE,
                     attempted_producers=(DIRECT_ROUTE, RULE_ROUTE), evidence_refs=(),
                     cache_key=key)
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=key) is False
    ocr = fact_cache_key(**dict(BASELINE, content_hash=content_hash,
                                analysis_tier="ocr"))
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=ocr) is True


def test_the_fact_key_is_not_p5s_extraction_key(p6_conn):
    """The naming trap. Two functions, two questions, one design sentence."""
    content_hash = BASELINE["content_hash"]
    mine = fact_cache_key(**BASELINE)
    theirs = extraction_cache_key(content_hash=content_hash,
                                  extractor_name="pdf.text",
                                  extractor_version="1.0.0",
                                  analysis_tier="native",
                                  config_fingerprint="sha256:config-1")
    assert mine != theirs

    ours = set(inspect.signature(fact_cache_key).parameters)
    p5 = set(inspect.signature(extraction_cache_key).parameters)
    assert "extractor_name" not in ours and "config_fingerprint" not in ours
    assert "model_identifier" not in p5 and "prompt_fingerprint" not in p5

    # Runtime introspection, not a source-text search: this file's own docstrings
    # name `extractors.runs.cache_key` and a text guard would match them.
    namespace = vars(cache_module).values()
    assert not any(one is extraction_cache_key for one in namespace)
    assert not any(getattr(one, "__name__", "") == "extractors.runs"
                   for one in namespace)
```

- [ ] **Step 2: Run the test and see it fail**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_cache.py -x -q
```

**Expected failure:** collection fails before any test body runs —
`ModuleNotFoundError: No module named 'facts.cache'`. All thirteen tests error at import.

- [ ] **Step 3: Write `src/facts/cache.py`**

```python
# src/facts/cache.py
"""§3.4's cache key, and what invalidates a fact -- Done-means 15 and 16.

The design, in one sentence: "The cache key includes content hash, extractor version,
analysis tier, model identifier when relevant, and prompt fingerprint for model-derived
results. This prevents stale results from surviving a content rewrite, avoids
unnecessary work when a file is merely renamed, and makes model or prompt changes
auditable."

Three consequences, and every one of them is a test:

  - There is NO path input. Not ignored, not nullable -- absent. That absence IS
    "avoids unnecessary work when a file is merely renamed": a rename cannot reach the
    key because the key has nowhere to put a path.
  - `content_hash` is a part, so a content rewrite is a different slot and the old
    facts cannot be found in it. That is "prevents stale results from surviving a
    content rewrite".
  - `model_identifier` and `prompt_fingerprint` are parts, so a prompt change
    re-resolves and BOTH keys stay computable and readable. That is "makes model or
    prompt changes auditable" -- §8.2's supersede-never-overwrite, at the cache.

TWO CACHE KEYS EXIST, AND THIS IS NOT THE OTHER ONE. `extractors.runs.cache_key(*,
content_hash, extractor_name, extractor_version, analysis_tier, config_fingerprint)`
identifies an EXTRACTION RESULT -- which extractor at which configuration produced
these observations. This one identifies a FACT -- which evidence, under which model and
prompt, produced this conclusion. §3.4 predates §3.2's observation/fact split, so one
design sentence has two subjects and the built system has two functions. Neither list
of parts is a subset of the other, so neither can be expressed in terms of the other,
and this module imports nothing from `extractors`.

`None` VS `""`. `sha256_of` is length-prefixed and therefore injective over the tuple
of strings it is handed, but it takes strings and `None` is not one. Every part is
encoded through `canonical_json` first: `None` becomes `null` and `""` becomes `""`
(with the quotes) -- different strings, different lengths, different digests. An absent
model identifier and an empty one are not the same cache slot.

WHAT IS NOT DECIDED HERE. §3.4 says "model identifier when relevant" and "prompt
fingerprint for model-derived results" and states no dependency between them, so no
both-or-neither guard is imposed: P8 is the part that would know whether one is true and
P8 does not exist.

WHAT IS DECIDED HERE, AND ONLY HERE. A file version has several extractor versions and
several analysis tiers, and §3.4 wants one of each. That reconciliation is THIS
function's: `extractor_version` is the canonical JSON of the sorted distinct
(extractor_name, extractor_version) pairs of EVERY observation of the version -- not of
the ones a fact happens to cite -- and `analysis_tier` is the last tier present in
ANALYSIS_TIERS order. So there is ONE key per (file version, deterministic pass), which
is what lets the abstention share the fact's key: an `unresolved` row with no citations
has no cited observations to compute a key from, and the SPEC gives it the "same
composition as `file_facts` (§3.4)". Taking `file_id` and `content_hash` rather than a
set of observations is deliberate: a caller CANNOT hand this function a filtered subset.
No producer writes its own copy of this rule; `facts.cache` is Task 6's module and no
other task adds to it.
"""
from __future__ import annotations

import sqlite3

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import ANALYSIS_TIERS, check

__all__ = ["CACHE_KEY_PARTS", "fact_cache_key", "is_stale"]

#: §3.4's five parts, in §3.4's own order. The order is part of the key: the digest is
#: over an ordered tuple, so reordering this tuple would invalidate every stored key.
CACHE_KEY_PARTS: tuple[str, ...] = (
    "content_hash",
    "extractor_version",
    "analysis_tier",
    "model_identifier",
    "prompt_fingerprint",
)

#: The two tables whose rows record "work was done under this key". `unresolved` is
#: here because the SPEC gives its `cache_key` the "same composition as `file_facts`
#: (§3.4), so an abstention is invalidated by the same events that invalidate a fact".
#: A file whose deterministic pass produced only refusals HAS been resolved under that
#: key; a reader that saw only `file_facts` would call it stale forever.
#:
#: Addressed by SQL rather than by importing `facts.file_facts` and `facts.unresolved`,
#: because every Wave B producer imports both this module and those, and a module that
#: imports none of its siblings cannot be half of an import cycle.
_RECORD_TABLES: tuple[str, ...] = ("file_facts", "unresolved")

#: P4's evidence, joined to the run that produced it. Column names verified live on
#: 2026-08-22. `facts.evidence.observations_for_version` answers the same question and
#: is deliberately NOT imported, for the same reason as `_RECORD_TABLES` above.
_VERSION_PARTS_SQL = """
    SELECT DISTINCT e.extractor_name  AS extractor_name,
                    e.extractor_version AS extractor_version,
                    r.analysis_tier   AS analysis_tier
      FROM evidence e
      JOIN extraction_runs r ON r.run_id = e.run_id
     WHERE e.file_id = ? AND e.content_hash = ?
"""


def _required(value: str, *, name: str) -> str:
    """`file_id` and `content_hash` identify the work. An empty one means "unknown",
    and two unknowns must not silently share a cache slot with each other or with a
    real value."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} is required and must be a non-empty string")
    return value


def _version_parts(conn: sqlite3.Connection, *, file_id: str,
                   content_hash: str) -> tuple[str, str]:
    """§3.4's two derived parts for one file version: `(extractor_version, tier)`.

    Both are over EVERY observation of the version. A version with no observations
    yet keys at the first tier with an empty pair list -- a real slot, distinct from
    every slot that has evidence in it, which is what an abstention recorded before
    any extractor ran needs.

    The tier is the LAST one present in `ANALYSIS_TIERS` order, so a pass that reached
    OCR lands outside the slot the native pass computed under: preamble §3.3's
    supersede-rather-than-overwrite, at the key. `check` is applied to what P4 stored
    because P6 never infers a tier and a tier P4 does not publish is a contract
    revision, not a row this module quietly hashes.
    """
    rows = conn.execute(_VERSION_PARTS_SQL, (file_id, content_hash)).fetchall()
    pairs = sorted({(row["extractor_name"], row["extractor_version"])
                    for row in rows})
    tiers = {check(row["analysis_tier"], ANALYSIS_TIERS, name="analysis_tier")
             for row in rows}
    tier = max(tiers, key=ANALYSIS_TIERS.index) if tiers else ANALYSIS_TIERS[0]
    return canonical_json([list(pair) for pair in pairs]), tier


def fact_cache_key(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                   model_identifier: str | None,
                   prompt_fingerprint: str | None) -> str:
    """§3.4's key for one (file version, deterministic pass). A `sha256:` digest.

    THE ONE HELPER. Every producer imports this; no task writes its own copy of the
    reconciliation in `_version_parts`, and `facts.cache` is the module that owns it.

    `extractor_version` and `analysis_tier` are derived from every observation of the
    version rather than supplied, so a caller cannot narrow them to the observations
    one fact cited -- and so an `unresolved` row, which cites nothing, computes the
    SAME key as the facts of the pass that wrote it.

    The two model parts stay the caller's and carry no default: they are `None` on
    every deterministic fact P6 writes (§3.3), and Task 17's LLM-supported fact is the
    one place that is not true. A defaulted part is a part that silently stops
    distinguishing cache slots.
    """
    _required(content_hash, name="content_hash")
    _required(file_id, name="file_id")
    extractor_version, analysis_tier = _version_parts(
        conn, file_id=file_id, content_hash=content_hash)
    parts = (content_hash, extractor_version, analysis_tier,
             model_identifier, prompt_fingerprint)
    assert len(parts) == len(CACHE_KEY_PARTS)
    return sha256_of(*(canonical_json(part) for part in parts))


def is_stale(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
             cache_key: str) -> bool:
    """True unless some record for `(file_id, content_hash)` was written under exactly
    this key.

    Three cases, one rule:

      - a rename, content unchanged  -> facts under this same key   -> False
      - a content rewrite            -> new slot, nothing in it     -> True
      - a bumped version or prompt   -> facts under the OLD key     -> True

    "Nothing has been computed for this file version" and "the content was rewritten"
    are the same case, and both need computing, which is why one predicate serves all
    three. This function re-resolves nothing and writes nothing: §8.2's supersession is
    `facts/supersede.py`'s and the sequencing is `facts/resolver.py`'s.
    """
    _required(file_id, name="file_id")
    _required(content_hash, name="content_hash")
    _required(cache_key, name="cache_key")
    for table in _RECORD_TABLES:
        found = conn.execute(
            f"SELECT 1 FROM {table} "
            "WHERE file_id = ? AND content_hash = ? AND cache_key = ? LIMIT 1",
            (file_id, content_hash, cache_key),
        ).fetchone()
        if found is not None:
            return False
    return True
```

- [ ] **Step 4: Run the test and see it pass**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_cache.py -q
```

**Expected:** `12 passed`.

- [ ] **Step 5: Run Wave A and then the whole suite**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6 -q && python3 -m pytest tests -q
```

**Expected:** every P6 test green and the 1302 P1–P5 tests still green. Wave A is complete after this
step: `fields`, `values`, `file_facts`, `unresolved` and the cache key all exist, and Tasks 7–13 can
start in parallel.

- [ ] **Step 6: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/facts/cache.py tests/p6/test_p6_cache.py && \
git commit -m "feat(P6): §3.4's five-part fact cache key — a rename is free, a version bump is not"
```

---

---

### Task 7: The evidence read — observation keys, the context pair, and `context_truncated`

**Files:**
- Create: `src/facts/evidence.py`
- Test: `tests/p6/test_p6_evidence.py`

**Interfaces:**
- Consumes: `evidence_shape.store` — `observations_for_file`, `observations_by_key`,
  `runs_for_content`, `unit_for_observation`; `evidence_shape.observation.Observation`.
- Produces: `observations_for_version(conn, file_id, content_hash) -> tuple[Observation, ...]`,
  `context_pair(observation) -> tuple[str, str, bool]`, `cite(observation) -> str`,
  `resolve_citation(conn, observation_key) -> tuple[Observation, ...]`,
  `analysis_tier_for_observation(conn, observation) -> str`.

**Done-means:** 6, 30.

**Why this is the first task of Wave B.** Every producer in Wave B and Wave C cites evidence, and the
one thing that must never be got wrong is *what* it cites. Putting the read first means no later task
has a plausible reason to touch `evidence_shape.store` directly, and the two guards this task
owns — the citation is a key, and no module branches per format — have exactly one place to look.
`PLAN-tasks-14-15.md` already imports `observations_for_version`, `cite` and
`analysis_tier_for_observation` from this module; the names below are that document's contract as
well as the skeleton's.

**The four properties this module exists to hold, each of which is a test rather than a comment.**

1. **The citation is `observation_key`, never `observation_id`.** M14. `observation_key` hashes
   `content_hash · extractor_name · locator · raw_value` and excludes `extractor_version` by
   construction, which is what makes a citation recorded today resolve after an extractor upgrade
   (§8.7: *"Rejected groups, rejected destination matches, rejected labels, and rejected residual
   recommendations must be stored with the evidence that produced them."* A reference that dies on a
   version bump cannot do that.) `observation_id` is per-row and P4-assigned; a fact citing one is a
   fact whose provenance an upgrade silently breaks.

2. **The read is per file *version*, and P4 publishes no such read.** `observations_for_file(conn,
   file_id)` spans every content hash the file has ever had. Every P6 computation is per version —
   the cache key is (§3.4) and the abstention row is (§8.2) — so the `content_hash` filter exists
   **once**, here. This is finding F12 and it is P4's gap, filtered rather than patched.

3. **The context is a pair, and the flag travels with it.** M5 split §2.8's *"surrounding context"*
   into `context_before` / `context_after` / `context_truncated` so §8.4 can redact a value without
   dropping its context. `context_pair` returns three values in one call so no caller can read the
   context without seeing the flag — §8.6, in the design's own words: *"A model prompt that exceeds
   its token budget should not truncate silently in a way that removes the decisive evidence."*
   Task 10 turns that flag into `reason = context_truncated` rather than `context_check_failed`;
   this module makes forgetting it impossible rather than merely discouraged.

4. **P6 branches on no format, ever.** §2.8 exists so downstream logic does not branch per format.
   Done-means 6 asserts P6 resolves a fixture whose `source type` is unknown to it. "Unknown to it"
   means a member of P4's fourteen that P6 has no code for — `Observation.__post_init__` rejects a
   value outside the vocabulary outright, verified by execution, so a genuinely novel string cannot
   even be constructed. The real assertion is the negative one: no module in `facts` holds a
   per-format dispatch table or names a format in code.

**`unit_for_observation` is listed in Consumes and is deliberately not called.** The text unit is the
span substrate §3.6's *quote* check needs, and that check is Task 17's. Calling it here to satisfy the
list would put a second reader of P4's text units in the part, and re-deriving context P4 already
split is exactly what M5 forbids. `Consumes:` states what the module may read; every name in
`Produces:` is delivered unchanged.

**Ordering is P6's, not P4's.** Verified by execution: `observations_for_file` is `ORDER BY rowid`,
which is insertion order, which is a property of the database and not of the corpus — writing the
same three fixtures as runs 1,2,3 and as 3,2,1 returns them in opposite orders. `observations_for_version`
therefore returns a **sorted tuple**, keyed on `observation_key`, so every consumer starts from a
total order that the same corpus produces in any write order. Task 11 sorts again by score before it
ranks; sorting twice is correct and sorting zero times is the defect §8.5's replay would report as a
fact-quality regression when nothing had changed.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_evidence.py
"""M14, Done-means 6 and 30 — keys, the context pair, truncation, and no per-format branching."""
from __future__ import annotations

import ast
import dataclasses
import importlib
import inspect
import pkgutil

import pytest

from evidence_shape.fixtures import by_number
from evidence_shape.location import Location
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import SOURCE_TYPES

import facts
from facts.evidence import (
    UnknownRun, analysis_tier_for_observation, cite, context_pair,
    observations_for_version, resolve_citation,
)

CLOCK = "2026-08-19T12:00:00+00:00"

#: A second content hash for the same `file_id`: the file was edited, so §3.4 puts its
#: facts in a different cache slot and §8.2 makes the old version's rows survive.
SECOND_HASH = "b" * 64

#: Every `extractor_name` P4's nineteen fixtures use. P6 must not contain one of these
#: strings in code: branching on the extractor is branching on the format (§2.8), and
#: F14 records that P4's fixture names and P5's live names already differ.
FIXTURE_EXTRACTORS = frozenset(
    by_number(n).run.extractor_name for n in range(1, 20))


def _run(conn, *, run_id, file_id, content_hash, extractor="pdf.text",
         version="1.0.0", source_type="text_document", tier="native"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version=version,
        source_type=source_type, analysis_tier=tier, config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="heading",
             container_path=(), extractor="pdf.text", version="1.0.0",
             source_type="text_document", before=None, after=None,
             truncated=False):
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version=version, source_type=source_type, raw_value=raw,
        location=Location(zone, tuple(container_path)), occurrence_count=1,
        observed_at=CLOCK, reliability="possible", run_id=run_id,
        context_before=before, context_after=after, context_truncated=truncated)
    record_observation(conn, observation)
    return observation


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring.

    A source-text search matches comments and docstrings, and a guard that does that
    has broken three tasks on this project already (P5 PLAN, Task 20). This reads the
    code.
    """
    tree = ast.parse(inspect.getsource(module))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings}


def _facts_modules():
    """Every module in the `facts` package, imported. Grows as siblings land."""
    for info in pkgutil.iter_modules(facts.__path__):
        yield importlib.import_module(f"facts.{info.name}")


# --- the per-version read (F12) ------------------------------------------------

def test_observations_for_version_does_not_return_a_prior_versions_observations(p6_conn):
    # §3.4 and §8.2 make every P6 computation per file *version*. P4 publishes only
    # `observations_for_file`, which spans content hashes; the filter lives here once.
    fixture = by_number(1)
    _run(p6_conn, run_id="r-old", file_id="file-01",
         content_hash=fixture.run.content_hash)
    _run(p6_conn, run_id="r-new", file_id="file-01", content_hash=SECOND_HASH)
    _observe(p6_conn, run_id="r-old", file_id="file-01",
             content_hash=fixture.run.content_hash, raw="BUSIB 4300")
    _observe(p6_conn, run_id="r-new", file_id="file-01",
             content_hash=SECOND_HASH, raw="PHYS 1401")

    new = observations_for_version(p6_conn, "file-01", SECOND_HASH)
    assert [one.raw_value for one in new] == ["PHYS 1401"]

    old = observations_for_version(p6_conn, "file-01", fixture.run.content_hash)
    assert [one.raw_value for one in old] == ["BUSIB 4300"]


def test_observations_for_version_returns_a_tuple_not_a_list(p6_conn):
    # A tuple is the shape `PLAN-tasks-14-15.md` stores on its `_Version` record, and
    # an immutable read is one fewer way a producer can reorder its own input.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    _observe(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH, raw="x")
    assert isinstance(observations_for_version(p6_conn, "f1", SECOND_HASH), tuple)


def test_the_read_order_is_p6s_own_and_not_p4s_insertion_order(p6_conn):
    # Verified by execution 2026-08-21: `observations_for_file` is ORDER BY rowid,
    # which is a property of this database and not of the corpus. Two files given the
    # same three values in opposite write orders must read back identically, or §8.5's
    # replay compares a run against itself and reports a regression.
    values = ["Columbia", "BUSIB 4300", "Wash U"]
    _run(p6_conn, run_id="r-fwd", file_id="f-fwd", content_hash=SECOND_HASH)
    _run(p6_conn, run_id="r-rev", file_id="f-rev", content_hash=SECOND_HASH)
    for raw in values:
        _observe(p6_conn, run_id="r-fwd", file_id="f-fwd",
                 content_hash=SECOND_HASH, raw=raw)
    for raw in reversed(values):
        _observe(p6_conn, run_id="r-rev", file_id="f-rev",
                 content_hash=SECOND_HASH, raw=raw)

    forward = observations_for_version(p6_conn, "f-fwd", SECOND_HASH)
    reverse = observations_for_version(p6_conn, "f-rev", SECOND_HASH)
    assert [one.raw_value for one in forward] == [one.raw_value for one in reverse]
    assert [cite(one) for one in forward] == sorted(cite(one) for one in forward)


# --- the citation (M14, Done-means 30) ----------------------------------------

def test_cite_returns_the_observation_key_and_never_the_observation_id(p6_conn):
    # M14. `observation_id` is per-row and P4-assigned; a fact citing one is a fact an
    # extractor upgrade silently orphans.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    observation = _observe(p6_conn, run_id="r1", file_id="f1",
                           content_hash=SECOND_HASH, raw="Columbia")
    assert cite(observation) == observation.observation_key
    assert cite(observation).startswith("sha256:")
    assert not hasattr(observation, "observation_id")


def test_a_citation_stored_before_a_version_bump_still_resolves_after_it(p6_conn):
    # Done-means 30 and §8.7. `observation_key` hashes content_hash · extractor_name ·
    # locator · raw_value and NOT extractor_version, so the same reading re-extracted
    # at 2.0.0 carries the identical key and the stored reference resolves to both.
    fixture = by_number(1)
    _run(p6_conn, run_id="r-1", file_id="file-01",
         content_hash=fixture.run.content_hash)
    before = _observe(p6_conn, run_id="r-1", file_id="file-01",
                      content_hash=fixture.run.content_hash, raw="BUSIB 4300")
    stored = cite(before)

    _run(p6_conn, run_id="r-2", file_id="file-01",
         content_hash=fixture.run.content_hash, version="2.0.0")
    after = _observe(p6_conn, run_id="r-2", file_id="file-01",
                     content_hash=fixture.run.content_hash, raw="BUSIB 4300",
                     version="2.0.0")
    assert cite(after) == stored

    resolved = resolve_citation(p6_conn, stored)
    assert {one.extractor_version for one in resolved} == {"1.0.0", "2.0.0"}
    assert {one.raw_value for one in resolved} == {"BUSIB 4300"}


def test_resolve_citation_returns_empty_for_a_key_no_observation_carries(p6_conn):
    # §3.6 check 2 asks whether a cited quote is present in the evidence. An empty
    # answer is the answer; an exception would make an absent citation a crash.
    assert resolve_citation(p6_conn, "sha256:" + "0" * 64) == ()


def test_resolve_citation_is_ordered_and_not_p4s_rowid_order(p6_conn):
    # The newer extractor version is written FIRST, so P4's rowid order and P6's order
    # disagree and the assertion has something to catch.
    fixture = by_number(1)
    stored = ""
    for run_id, version in (("r-b", "2.0.0"), ("r-a", "1.0.0")):
        _run(p6_conn, run_id=run_id, file_id="file-01",
             content_hash=fixture.run.content_hash, version=version)
        stored = cite(_observe(
            p6_conn, run_id=run_id, file_id="file-01",
            content_hash=fixture.run.content_hash, raw="BUSIB 4300",
            version=version))

    resolved = resolve_citation(p6_conn, stored)
    assert [one.extractor_version for one in resolved] == ["1.0.0", "2.0.0"]


# --- the context pair (M5, §8.6) ----------------------------------------------

def test_context_pair_returns_two_values_and_never_a_concatenation(p6_conn):
    # M5: P4 split §2.8's "surrounding context" into two fields so §8.4 can redact a
    # value without dropping its context. Fixture 1's bytes, verbatim.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    observation = _observe(p6_conn, run_id="r1", file_id="f1",
                           content_hash=SECOND_HASH, raw="BUSIB 4300",
                           before="Syllabus — ", after=" — Spring 2026")
    before, after, truncated = context_pair(observation)
    assert before == "Syllabus — "
    assert after == " — Spring 2026"
    assert truncated is False
    assert before + after not in (before, after)


def test_context_pair_hands_back_the_truncation_flag_with_the_context(p6_conn):
    # §8.6: "A model prompt that exceeds its token budget should not truncate silently
    # in a way that removes the decisive evidence." Three values in one call is how a
    # caller is stopped from reading the context without seeing the flag.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    observation = _observe(p6_conn, run_id="r1", file_id="f1",
                           content_hash=SECOND_HASH, raw="BUSIB 4300",
                           before="…llabus ", after=" — Spri", truncated=True)
    assert context_pair(observation) == ("…llabus ", " — Spri", True)
    assert len(context_pair(observation)) == 3


def test_context_pair_renders_an_absent_context_as_the_empty_string(p6_conn):
    # Fixture 2 (the PDF title) carries context_before=None. A caller doing a
    # substring or word-boundary check on None raises; on "" it simply finds nothing.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    observation = _observe(p6_conn, run_id="r1", file_id="f1",
                           content_hash=SECOND_HASH, raw="BUSIB 4300 Syllabus",
                           zone="title")
    assert observation.context_before is None
    assert context_pair(observation) == ("", "", False)


# --- the analysis tier comes from P4 and is never inferred ---------------------

def test_the_analysis_tier_is_read_from_p4s_run(p6_conn):
    # Global constraint: P6 never re-derives what P4 assigns. Inferring the tier from
    # `extractor_name` would encode the routing table in a second place.
    _run(p6_conn, run_id="r-ocr", file_id="f1", content_hash=SECOND_HASH,
         extractor="ocr.apple_vision", source_type="ocr", tier="ocr")
    observation = _observe(p6_conn, run_id="r-ocr", file_id="f1",
                           content_hash=SECOND_HASH, raw="Your Columbia University",
                           zone="ocr", extractor="ocr.apple_vision",
                           source_type="ocr")
    assert analysis_tier_for_observation(p6_conn, observation) == "ocr"


def test_an_observation_whose_run_was_never_recorded_raises(p6_conn):
    # Guessing a tier here would put the wrong value in §3.4's cache key, and a wrong
    # cache key is a fact that never invalidates. Refusing is the only safe answer.
    observation = Observation(
        file_id="f1", content_hash=SECOND_HASH, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value="x",
        location=Location("heading", ()), occurrence_count=1, observed_at=CLOCK,
        reliability="possible", run_id="run-that-does-not-exist")
    with pytest.raises(UnknownRun):
        analysis_tier_for_observation(p6_conn, observation)


# --- Done-means 6: no per-format branching ------------------------------------

def test_p6_reads_an_observation_whose_source_type_it_has_never_seen(p6_conn):
    # Done-means 6. Fixture 18 is `design_creative`, indexed-but-unreadable (M3) --
    # a source type nothing in `facts` was written against. It reads, it cites, and
    # its tier resolves, with no code added for it.
    fixture = by_number(18)
    record_run(p6_conn, fixture.run)
    for observation in fixture.observations:
        record_observation(p6_conn, observation)

    read = observations_for_version(p6_conn, fixture.run.file_id,
                                    fixture.run.content_hash)
    assert [one.raw_value for one in read] == ["Background"]
    assert cite(read[0]).startswith("sha256:")
    assert analysis_tier_for_observation(p6_conn, read[0]) == "native"
    assert context_pair(read[0]) == ("", "", False)


def test_a_source_type_outside_p4s_vocabulary_cannot_be_constructed_at_all():
    # Why Done-means 6 is read as "unknown to P6" and not "unknown to P4": P4 refuses
    # the latter at the record, so the only reachable case is a member of the fourteen
    # that P6 has no code for. Verified by execution, not by reading the docstring.
    from evidence_shape.vocabulary import NotInVocabulary
    with pytest.raises(NotInVocabulary):
        dataclasses.replace(by_number(1).observations[0],
                            source_type="holographic_scroll")


def test_no_facts_module_holds_a_dispatch_table_keyed_by_source_type():
    # §2.8 exists so downstream logic does not branch per format. "At least two keys,
    # all of them source types" is the shape of a real dispatch table; the bound is
    # two because `ocr` is a member of BOTH SOURCE_TYPES and ZONES, so a zone-keyed
    # map with a single `ocr` entry would otherwise read as a format branch.
    offenders = []
    for module in _facts_modules():
        for name, value in vars(module).items():
            if name.startswith("__") or not isinstance(value, dict):
                continue
            keys = {k for k in value if isinstance(k, str)}
            if len(keys) >= 2 and keys <= set(SOURCE_TYPES):
                offenders.append(f"{module.__name__}.{name}")
    assert offenders == []


def test_no_facts_module_names_a_source_type_or_an_extractor_in_code():
    # The stronger half: a single `if observation.source_type == "image"` is a format
    # branch too. Extractor names are checked against P4's nineteen fixtures because
    # F14 records that P4's fixture names and P5's live names already differ -- only
    # the no-branching rule keeps that harmless.
    forbidden = set(SOURCE_TYPES) | FIXTURE_EXTRACTORS
    offenders = []
    for module in _facts_modules():
        for literal in _code_strings(module) & forbidden:
            offenders.append(f"{module.__name__}: {literal!r}")
    assert offenders == []
```

- [ ] **Step 2: Run the test and read the failure**

Run: `pytest tests/p6/test_p6_evidence.py -v`

Expected: FAIL — collection errors with
`ModuleNotFoundError: No module named 'facts.evidence'`. Tasks 1–6 are green, so `facts`,
`facts.schema`, `facts.fields`, `facts.values`, `facts.file_facts`, `facts.unresolved` and
`facts.cache` all import; `facts.evidence` is the only missing name and it is the one this task
creates. **16 tests fail to collect, 0 pass.**

- [ ] **Step 3: Write the implementation**

```python
# src/facts/evidence.py
"""The read over P4, and the one place P6 turns an observation into a citation.

Four properties live here because each of them must exist exactly once:

* **The citation is `observation_key`** (M14). It hashes `content_hash · extractor_name
  · locator · raw_value` and excludes `extractor_version` by construction, so a
  reference stored today resolves after an extractor upgrade -- which is what §8.7's
  requirement that rejected proposals "must be stored with the evidence that produced
  them" needs in order to still mean something in six months. `observation_id` is
  P4's per-row identity and is never cited.

* **The read is per file version.** §3.4's cache key and §8.2's abstention row are both
  per content hash, and P4 publishes only `observations_for_file`, which spans every
  hash the file has ever had. The filter is here and nowhere else (finding F12).

* **The context is a pair with its flag** (M5, §8.6). `context_before` and
  `context_after` are never concatenated, and `context_truncated` is returned beside
  them so a caller cannot read one without the other. §8.6: a prompt over budget
  "should not truncate silently in a way that removes the decisive evidence."

* **Nothing here branches on a format.** §2.8 exists so downstream logic does not, and
  Done-means 6 asserts P6 resolves a source type it has never seen. There is no
  mapping keyed by `source_type` and no string naming one anywhere in `facts`;
  `tests/p6/test_p6_evidence.py` asserts that by runtime introspection of every
  module in the package, not by reading the source text.

P4's reads are `ORDER BY rowid`, which is insertion order -- a property of the
database, not of the corpus. Every read published here imposes a total order of P6's
own before returning, so the same corpus extracted in a different order produces the
same facts (§8.5 replay).

`unit_for_observation` is part of P4's read surface and is deliberately not called
here: the text unit is the span substrate §3.6's quote check needs, and that check is
the P8 seam's. Re-deriving context P4 already split is what M5 forbids.
"""
from __future__ import annotations

import sqlite3
from typing import Iterable

from evidence_shape.observation import Observation
from evidence_shape.store import (
    observations_by_key, observations_for_file, runs_for_content,
)


class UnknownRun(Exception):
    """An observation whose `run_id` has no `extraction_runs` row.

    P6 never re-derives what P4 assigns, so there is no fallback: an inferred
    `analysis_tier` would land in §3.4's cache key, and a wrong cache key is a fact
    that never invalidates.
    """


def cite(observation: Observation) -> str:
    """M14: the citation handle P6 stores. Content-addressed, version-independent."""
    return observation.observation_key


def observations_for_version(conn: sqlite3.Connection, file_id: str,
                             content_hash: str) -> tuple[Observation, ...]:
    """Every observation P4 holds for one *version* of one file, in P6's own order.

    P4's `observations_for_file` spans content hashes and returns insertion order.
    Both are corrected here: the filter is §3.4's per-version scope, and the sort is
    the total order every downstream ranking starts from.
    """
    return _ordered(one for one in observations_for_file(conn, file_id)
                    if one.content_hash == content_hash)


def resolve_citation(conn: sqlite3.Connection,
                     observation_key: str) -> tuple[Observation, ...]:
    """Every observation carrying this key -- one per extractor version that saw it.

    Returns an empty tuple when nothing carries the key: §3.6 check 2 asks whether a
    cited quote is present in the evidence, and "no" is an answer, not a crash.
    """
    return _ordered(observations_by_key(conn, observation_key))


def context_pair(observation: Observation) -> tuple[str, str, bool]:
    """§2.8's surrounding context, as M5 split it: `(before, after, truncated)`.

    Never a concatenation, and never the pair without the flag. `None` renders as the
    empty string so a word-boundary check over an absent context finds nothing rather
    than raising.
    """
    return (observation.context_before or "",
            observation.context_after or "",
            bool(observation.context_truncated))


def analysis_tier_for_observation(conn: sqlite3.Connection,
                                  observation: Observation) -> str:
    """I4's tier, read from P4's run. Never inferred from the extractor or the zone."""
    for run in runs_for_content(conn, observation.content_hash):
        if run.run_id == observation.run_id:
            return run.analysis_tier
    raise UnknownRun(
        f"observation {observation.observation_key} names run "
        f"{observation.run_id!r}, which has no extraction_runs row; P6 reads "
        f"analysis_tier from P4 and derives it from nothing"
    )


def _ordered(observations: Iterable[Observation]) -> tuple[Observation, ...]:
    """Score-free total order: `observation_key` ascending, then extractor version.

    The key is content-addressed, so this order is a property of the corpus. P4's
    `rowid` order is a property of the database and reverses when the same three runs
    are written in the opposite sequence (verified by execution, 2026-08-21).
    """
    return tuple(sorted(observations,
                        key=lambda one: (one.observation_key,
                                         one.extractor_version, one.run_id)))
```

- [ ] **Step 4: Run the test and confirm it passes**

Run: `pytest tests/p6/test_p6_evidence.py -v`

Expected: PASS — **16 passed**. In particular
`test_a_citation_stored_before_a_version_bump_still_resolves_after_it` passes because
`observation_key` excludes `extractor_version` (executed and confirmed before this plan was
written), and the two introspection guards pass over every `facts` module that exists at the time
the suite runs, including the siblings landing in parallel.

- [ ] **Step 5: Run the whole P6 suite, so a sibling's module is not broken by the guards**

Run: `pytest tests/p6 -q`

Expected: PASS. The two guards in this file walk `pkgutil.iter_modules(facts.__path__)`, so they
police modules this task did not write. A failure here is a real finding — a sibling holding a
format-keyed table — and is reported to that task's author rather than fixed by weakening the guard.

- [ ] **Step 6: Commit**

```bash
git add src/facts/evidence.py tests/p6/test_p6_evidence.py
git commit -m "feat(P6): the evidence read — observation keys, the context pair, context_truncated"
```

---

---

### Task 8: Direct facts — §3.5's four explicit slots

**Files:**
- Create: `src/facts/direct.py`
- Test: `tests/p6/test_p6_direct.py`

**Interfaces:**
- Consumes: `facts.evidence`, `facts.file_facts.write_fact`, `facts.values.ensure_value`,
  `database_agent.files_table.get_file`.
- Produces: `direct_facts(conn, *, file_id, content_hash, slots: DirectSlots) -> tuple[str, ...]`,
  `DirectSlots` — an injected frozen dataclass of slot-name predicates, no defaults.
- Also imports, because the skeleton's `Consumes:` line predates Task 4's signature and
  `write_fact` requires a `cache_key`: `facts.cache.fact_cache_key`, `facts.states.STATES`,
  `facts.file_facts.FACT_ORIGINS`, `facts.values.VALUE_ORIGINS`,
  `evidence_shape.canonical.canonical_json`, `evidence_shape.vocabulary.ANALYSIS_TIERS`. It reads
  none of them for anything but the cache key and the two enumerations it addresses by index.
- Also produces, beyond the skeleton's list and for the same reason Task 7 publishes `UnknownRun`:
  `DirectSlot` (the member of `DirectSlots.slots`), `DIRECT_STATE`, `DIRECT_ORIGIN`, `UnknownFile`.
  Nothing in the skeleton's list is renamed.

**Done-means:** 5, and part of 4.

**What "part of 4" is, stated exactly, because the whole of it is not this task's.** Done-means 4 is
the §3.2 fixture producing `subject`, term and work type. **None of those three is a direct fact** —
they come from a filename, a PDF title and a page-one heading, and §3.5 gives text to the *rule*
producer (Task 10), which is why Task 10's Done-means line reads *"8, and the `validated` half of
4"*. What Task 8 owns of item 4 is its last clause: *"each observation's `raw value` unchanged
afterwards (§3.2, §2.8)"*. This task proves it for the one fixture where the temptation to rewrite is
real — the EXIF reading, whose stored form (`2026:07:17 14:03:22`) is not the fact's form
(`2026-07-17`).

**The one rule this module exists to hold: the slot decides, and nothing else does.**

§3.5, verbatim: *"Deterministic extractors create direct facts when the information comes from a
reliable, explicit source, such as a content hash, EXIF timestamp, a document title, or a labeled
form field."* §3.13 says the same in the reliability vocabulary: *"A direct fact was read from a
reliable and explicit source, such as a content hash, EXIF timestamp, document title, or labeled
form field."*

Both sentences describe a **location**, never a value and never a confidence. That is not a reading
imposed here; it is P4's own fixture 6, whose design case is written on the fixture:

> `6 · §2.2 — direct describes the slot, not the value's usefulness` — `raw_value = "python-docx"`,
> zone `metadata`, locator `metadata:field=Producer`, `reliability = "direct"`.

So this module applies **no** test to the observation's own `reliability`. Two consequences, and both
are tests below:

- **A slot match on a `possible` observation still produces a `direct` fact.** P4's fixture 12 is
  §3.5's fourth slot — *"dates or identifiers from labeled cells"*, locator
  `table:sheet=2/row=7/column=3` — and P4 marks it `reliability = "possible"`. A gate on the
  observation's reliability would make one of the four slots §3.5 names unreachable against P4's own
  fixture for it. P4's two-member `EXTRACTOR_RELIABILITY_STATES` is what an extractor may claim about
  an *observation*; the fact's six-state vocabulary is P6's, and Task 1 asserts that boundary from
  both sides. Confusing the two is the same error in the other direction.
- **A `Producer` slot would therefore turn `python-docx` into a `direct` fact.** It is stopped by
  Task 9's suppression tier firing first, not by anything here. Task 8 declares no metadata-property
  slot and imports nothing from `facts.discount` — the ordering obligation is the sequencer's
  (Task 24) and is named in *Contract ambiguities* rather than assumed.

**Why the slot name is injected and not written down (F8).** P5's `image.py` carries the EXIF tag
only as a reader-supplied `container_path` segment label and spells no tag name anywhere, on purpose
(P4 D7: *"the source format's own slot name, verbatim"*). P4's fixture 7 happens to use
`DateTimeOriginal`, but a fixture is data, not a vocabulary. A literal `"DateTimeOriginal"` in
`src/facts/` would be P6 minting a vocabulary member P5 deliberately refused to publish, and it would
be wrong for the first camera whose reader spells it differently. So `DirectSlots` arrives at the
call, with **no default**, and `facts.direct` contains not one slot name. The catalogue behind that
injection **does not exist**; it is the same shape as catalogue 01 and belongs beside it (F8).

**The predicate reads P4's `locator`, which is the slot's published name.** `Observation.locator` is
a P4 property (verified: `metadata:field=DateTimeOriginal`, `title:page=1`,
`table:sheet=2/row=7/column=3`, `metadata:field=Producer`). Reading it means this module needs no
rule for *which* `container_path` segment names a slot — a rule that would differ per format and
would be exactly the branching §2.8 exists to prevent. Task 9 reads the `field`-kind segment's label
instead, because **catalogue 01 specifies that** in its `match_field` clause; the two reads are
different because their sources ask for different things, and neither is a helper the other could
share across a module boundary it does not own.

**How far §3.5's four slots actually reach today.** This is checked, not assumed, and two of the four
do not land in a fact:

| §3.5 slot | Publisher in the built system | Field it can fill | Status |
|---|---|---|---|
| EXIF timestamp | `image.exif` / P5's `image.py`, tag name as a segment label | `capture_date` | **produces a fact** (Done-means 5) |
| labeled form field | `xlsx.cells` and its siblings, fixture 12's shape | `application_cycle` | **produces a fact** |
| document title | `pdf.text`, zone `title`, fixture 2 | *none in the catalogue* | **raises `FieldNotInCatalogue`** — §3.12 forbids creating one at run time, so the refusal is the correct outcome and is the test |
| content hash | P1's `files.content_hash` — **not an observation** | — | **cannot be written here.** M14 makes every citation an `observation_key` and Task 4 raises `EvidenceRequired` on anything else, so a fact whose only evidence is a P1 column has no lawful form. Its design consumer is §8.3's duplicate family, which is Task 14's |

Verified against the shipped extractor, because this is where a plan invents a publisher that is not
there: `extractors.filesystem` emits `METADATA_SLOTS = ("normalized_filename", "extension",
"mime_type")` at `reliability = "direct"`, zone `metadata`, `extractor_name = "filesystem.record"`,
`analysis_tier = "filesystem"`. **`mime_type` is a real, shipped §3.5 slot** and fills `file_type`.
**No timestamp is among them**, so §3.13's "filesystem timestamp" — `creation_date` — has the slot
and no publisher. The test drives its shape and the gap is reported; the injection makes it a
one-line change on the day P5 adds the slot, which is the point of injecting it.

**Why `get_file` is consumed.** P1 owns identity (§1.2) and P6 re-observes no filesystem. A `direct`
fact is the strongest state a deterministic producer writes, and writing one against a `file_id` the
system of record does not hold would put an unanchored fact in the strongest tier. `direct_facts`
reads the row and raises `UnknownFile` when P1 has none. It reads **no value** out of it: the row's
`content_hash` and `observed_timestamps` are the two columns a careless implementation would mine for
§3.5's first and second slots, and neither is citable evidence.

**This producer never abstains.** `facts.unresolved` is absent from its `Consumes:` and that is
deliberate rather than an omission. A slot that matched nothing is not a refusal — §8.6's order runs
direct, then rule-validated, then the model, and a field that no direct slot filled is a field the
next producer has not tried yet. Writing an `unresolved` row here would report *"P6 abstained"* for
every field on every file before the work had been done, which is the exact opposite of B7's purpose:
the row exists so §8.5's *"Did it abstain when evidence was absent?"* has a truthful answer. The
abstention is written once, by the sequencer, after every producer has had its turn.

**Ordering.** `observations_for_version` already returns Task 7's total order, keyed on
`observation_key`. This module sorts once more, by `(field_key, canonical_value)`, before it writes,
so the returned tuple is identical whether the caller lists its slots in one order or another and
whether P4's rows went in forwards or backwards. Same reason as Task 7's: a corpus extracted twice
must produce one answer, or §8.5's replay compares a run with itself and reports a regression.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_direct.py
"""Done-means 5, §3.5's four explicit slots, and the raw-value half of Done-means 4."""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.fixtures import by_number
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import (
    observations_by_key, observations_for_file, record_observation, record_run,
)

from facts import direct as direct_module
from facts.direct import (
    DIRECT_ORIGIN, DIRECT_STATE, DirectSlot, DirectSlots, UnknownFile, direct_facts,
)
from facts.fields import FieldNotInCatalogue
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file
from facts.values import values_in_field

CLOCK = "2026-08-19T12:00:00+00:00"

#: §3.2's own worked derivation: "an EXIF field called DateTimeOriginal is raw
#: metadata; capture date = 2026-07-17 is the file fact derived from it." Fixture 7
#: carries the left-hand side byte-exact.
EXIF_RAW = "2026:07:17 14:03:22"
CAPTURE_DATE = "2026-07-17"


def _iso_date(raw: str) -> str:
    """The caller's canonicaliser, not P6's.

    §3.2 names both forms and P6 owns neither: round 4's C-5 records that
    `normalize(field, raw_value)` is claimed by P8's Contract-in and disowned by P6's
    Task 17, so no part builds it. A per-slot canonicaliser supplied at the call is
    how this task produces §3.2's right-hand side without inventing the function
    neither part owns. `facts.direct` holds no date knowledge whatever; the guard
    below asserts that by introspection.
    """
    return raw[:10].replace(":", "-")


def _refuse(raw: str) -> str:
    raise ValueError(f"this slot cannot canonicalise {raw!r}")


def _file(conn, tmp_path, *, name, body, mtime=1_700_000_000.0, parent="Downloads"):
    """One P1 `files` row over real bytes, so the content hash is P1's own."""
    path = tmp_path / parent / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": mtime}),
        parent_folder_context=parent, mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, zone, container_path=(),
             extractor="pdf.text", version="1.0.0", source_type="text_document",
             analysis_tier="native", reliability="direct"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version=version,
        source_type=source_type, analysis_tier=analysis_tier, config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version=version, source_type=source_type, raw_value=raw,
        location=Location(zone, tuple(container_path)), occurrence_count=1,
        observed_at=CLOCK, reliability=reliability, run_id=run_id)
    record_observation(conn, observation)
    return observation


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring.

    A source-text search matches comments and docstrings, and a guard that does that
    has broken three tasks on this project already (P5 PLAN, Task 20). This reads the
    code. Same helper as `tests/p6/test_p6_evidence.py`; each test file stands alone.
    """
    tree = ast.parse(inspect.getsource(module))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings}


# --- the slots, declared by the caller and never by `facts` ---------------------

EXIF_SLOT = DirectSlot(
    slot_id="exif-capture-time", field_key="capture_date",
    names=lambda locator: locator.endswith("field=DateTimeOriginal"),
    canonical=_iso_date)

#: P5's `filesystem.record` publishes `mime_type` at zone `metadata`,
#: `reliability = "direct"` -- a §3.5 slot that exists in the shipped system today.
FILE_TYPE_SLOT = DirectSlot(
    slot_id="fs-mime-type", field_key="file_type",
    names=lambda locator: locator.endswith("field=mime_type"),
    canonical=lambda raw: raw)

#: §3.13's "filesystem timestamp". `extractors.filesystem.METADATA_SLOTS` is
#: ("normalized_filename", "extension", "mime_type") -- no timestamp -- so this slot
#: has no publisher today. The injection is what makes that a one-line change later.
CREATION_SLOT = DirectSlot(
    slot_id="fs-observed-timestamps", field_key="creation_date",
    names=lambda locator: locator.endswith("field=observed_timestamps"),
    canonical=lambda raw: raw)

#: §3.5's "labeled form field" -- P4's fixture 12, a labeled spreadsheet cell.
CELL_SLOT = DirectSlot(
    slot_id="labeled-cell-cycle", field_key="application_cycle",
    names=lambda locator: locator.startswith("table:sheet=2/row=7/column=3"),
    canonical=lambda raw: raw)

#: §3.5's "document title". The catalogue carries no field for a raw document title,
#: which is the point of the test that uses it.
TITLE_SLOT = DirectSlot(
    slot_id="pdf-title", field_key="document_title",
    names=lambda locator: locator.startswith("title:"),
    canonical=lambda raw: raw)


@pytest.fixture()
def photo(p6_conn, tmp_path):
    """Fixture 7's EXIF reading on a file P1 holds, plus a text date to contrast."""
    file_id, content_hash = _file(p6_conn, tmp_path, name="IMG_4821.heic",
                                  body=b"\x00photo-bytes")
    exif = _observe(p6_conn, run_id="run-exif", file_id=file_id,
                    content_hash=content_hash, raw=EXIF_RAW, zone="metadata",
                    container_path=(Segment("field", label="DateTimeOriginal"),),
                    extractor="image.exif", source_type="image")
    return file_id, content_hash, exif


# --- Done-means 5: the EXIF slot ------------------------------------------------

def test_an_exif_datetimeoriginal_observation_produces_a_direct_capture_date_fact(
        p6_conn, photo):
    # Done-means 5, and §3.2's worked derivation: the EXIF field is raw metadata,
    # `capture date = 2026-07-17` is the file fact derived from it.
    file_id, content_hash, exif = photo
    written = direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                           slots=DirectSlots(slots=(EXIF_SLOT,)))
    assert len(written) == 1

    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [row["field_key"] for row in rows] == ["capture_date"]
    assert rows[0]["reliability_state"] == DIRECT_STATE == "direct"
    assert rows[0]["origin"] == DIRECT_ORIGIN
    assert json.loads(rows[0]["evidence_refs"]) == [exif.observation_key]

    values = values_in_field(p6_conn, "capture_date")
    assert [value["canonical_value"] for value in values] == [CAPTURE_DATE]


def test_the_exif_observation_is_readable_and_unchanged_after_resolution(
        p6_conn, photo):
    # Done-means 5's second clause and Done-means 4's last: "each observation's raw
    # value unchanged afterwards". §3.2: the product "must preserve both the original
    # evidence and the conclusion built from it". P4's `evidence_never_overwritten`
    # trigger makes this unfalsifiable; the assertion states the intent.
    file_id, content_hash, exif = photo
    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(EXIF_SLOT,)))

    still = observations_by_key(p6_conn, exif.observation_key)
    assert [one.raw_value for one in still] == [EXIF_RAW]
    assert still[0].raw_value != CAPTURE_DATE
    assert still[0].normalized_value is None


# --- §3.5's distinction: the slot, not the string --------------------------------

def test_a_filesystem_timestamp_is_direct(p6_conn, tmp_path):
    # §3.13 names the filesystem timestamp a Direct source. `creation_date` is
    # §3.11's universal field for it and is distinct from `capture_date` (§3.2
    # separates them by name) and from `capture_year` (§3.11's Photos dimension).
    file_id, content_hash = _file(p6_conn, tmp_path, name="notes.pdf", body=b"%PDF-1")
    _observe(p6_conn, run_id="run-fs", file_id=file_id, content_hash=content_hash,
             raw="1700000000.0", zone="metadata",
             container_path=(Segment("field", label="observed_timestamps"),),
             extractor="filesystem.record", version="0.1.0",
             source_type="filesystem", analysis_tier="filesystem")

    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(CREATION_SLOT,)))
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(row["field_key"], row["reliability_state"]) for row in rows] == [
        ("creation_date", DIRECT_STATE)]


def test_the_same_date_string_in_body_text_produces_no_direct_fact(p6_conn, photo):
    # The §3.5 distinction, asserted on ONE string in TWO slots: the EXIF reading is
    # direct, the identical characters on page three are not, and §3.10's explicit-
    # pattern path (Task 12) is where the second one goes. The slot decides.
    file_id, content_hash, exif = photo
    body = _observe(p6_conn, run_id="run-body", file_id=file_id,
                    content_hash=content_hash, raw=EXIF_RAW, zone="body",
                    reliability="possible")

    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(EXIF_SLOT,)))
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert len(rows) == 1
    assert json.loads(rows[0]["evidence_refs"]) == [exif.observation_key]
    assert body.observation_key not in json.loads(rows[0]["evidence_refs"])

    # And it is still there for Task 12 to rank -- this producer consumed nothing.
    keys = {one.observation_key for one in observations_for_file(p6_conn, file_id)}
    assert body.observation_key in keys


def test_a_filename_date_produces_no_direct_fact(p6_conn, tmp_path):
    # P4's fixture 11 is `fs.basic` at zone `filename`, reliability `possible`: a
    # filename is evidence (§2.2) and is not one of §3.5's explicit slots.
    file_id, content_hash = _file(p6_conn, tmp_path, name="2026-07-17 scan.pdf",
                                  body=b"%PDF-2")
    _observe(p6_conn, run_id="run-name", file_id=file_id, content_hash=content_hash,
             raw=EXIF_RAW, zone="filename", extractor="filesystem.record",
             version="0.1.0", source_type="filesystem", analysis_tier="filesystem",
             reliability="possible")

    assert direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                        slots=DirectSlots(slots=(EXIF_SLOT, CREATION_SLOT))) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []


def test_the_slot_decides_and_not_the_observations_own_reliability(p6_conn, tmp_path):
    # P4's fixture 6 states it on the fixture: "direct describes the slot, not the
    # value's usefulness". Fixture 12 is §3.5's labeled form field and P4 marks it
    # `possible`; gating on that would make one of the four named slots unreachable
    # against P4's own fixture for it.
    fixture = by_number(12)
    assert fixture.observations[0].reliability == "possible"
    file_id, content_hash = _file(p6_conn, tmp_path, name="applications.xlsx",
                                  body=b"PK\x03\x04cells")
    _observe(p6_conn, run_id="run-cells", file_id=file_id,
             content_hash=content_hash, raw="2025", zone="table",
             container_path=(Segment("sheet", index=2, label="Applications"),
                             Segment("row", index=7),
                             Segment("column", index=3, label="C7")),
             extractor="xlsx.cells", source_type="spreadsheet",
             reliability="possible")

    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(CELL_SLOT,)))
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(row["field_key"], row["reliability_state"]) for row in rows] == [
        ("application_cycle", DIRECT_STATE)]


def test_a_shipped_filesystem_mime_type_slot_fills_file_type(p6_conn, tmp_path):
    # `extractors.filesystem.METADATA_SLOTS` publishes `mime_type` at zone
    # `metadata`, reliability `direct` -- a §3.5 slot that exists today, so at least
    # one slot in this task is proved against a real publisher and not only a shape.
    file_id, content_hash = _file(p6_conn, tmp_path, name="essay.pdf", body=b"%PDF-3")
    _observe(p6_conn, run_id="run-fsm", file_id=file_id, content_hash=content_hash,
             raw="application/pdf", zone="metadata",
             container_path=(Segment("field", label="mime_type"),),
             extractor="filesystem.record", version="0.1.0",
             source_type="filesystem", analysis_tier="filesystem")

    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(FILE_TYPE_SLOT,)))
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(row["field_key"], row["reliability_state"]) for row in rows] == [
        ("file_type", DIRECT_STATE)]


# --- §3.12: a producer may not create a field ------------------------------------

def test_a_slot_naming_a_field_outside_the_catalogue_raises_and_creates_nothing(
        p6_conn, tmp_path):
    # §3.5's "document title" slot has no catalogue field, and §3.12 is the reason
    # the answer is a raise rather than a new row: "The system may create new values
    # ... but it should not invent new fields automatically." Done-means 3's negative
    # half, reached from a producer instead of from Task 2's own test.
    file_id, content_hash = _file(p6_conn, tmp_path, name="syllabus.pdf",
                                  body=b"%PDF-4")
    _observe(p6_conn, run_id="run-title", file_id=file_id,
             content_hash=content_hash, raw="BUSIB 4300 Syllabus", zone="title",
             container_path=(Segment("page", index=1),))

    with pytest.raises(FieldNotInCatalogue):
        direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                     slots=DirectSlots(slots=(TITLE_SLOT,)))
    assert facts_for_file(p6_conn, file_id, content_hash) == []


# --- the abstention is NOT this producer's -----------------------------------

def test_a_slot_that_matches_nothing_writes_no_fact_and_no_unresolved_row(
        p6_conn, tmp_path):
    # B7's row answers §8.5's "Did it abstain when evidence was absent?". A field the
    # direct producer did not fill is a field the rule and model producers have not
    # tried yet (§8.6's order), so a row here would report an abstention that has not
    # happened. The sequencer writes it once, after every producer has had its turn.
    file_id, content_hash = _file(p6_conn, tmp_path, name="empty.pdf", body=b"%PDF-5")
    _observe(p6_conn, run_id="run-none", file_id=file_id, content_hash=content_hash,
             raw="Columbia", zone="body", reliability="possible")

    assert direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                        slots=DirectSlots(slots=(EXIF_SLOT,))) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


# --- evidence, grouping and the per-version scope --------------------------------

def test_two_observations_of_one_value_make_one_fact_citing_both(p6_conn, tmp_path):
    # §3.1: "Every fact preserves where it came from" -- plural. Two readings of the
    # same capture time are one claim with two citations, not two identical facts.
    # This is not an answer to OQ6: multiplicity asks how many VALUES a field may
    # hold, and both readings carry one.
    file_id, content_hash = _file(p6_conn, tmp_path, name="IMG_9.heic",
                                  body=b"\x00two-readers")
    first = _observe(p6_conn, run_id="run-a", file_id=file_id,
                     content_hash=content_hash, raw=EXIF_RAW, zone="metadata",
                     container_path=(Segment("field", label="DateTimeOriginal"),),
                     extractor="image.exif", source_type="image")
    second = _observe(p6_conn, run_id="run-b", file_id=file_id,
                      content_hash=content_hash, raw=EXIF_RAW, zone="metadata",
                      container_path=(Segment("field", label="DateTimeOriginal"),),
                      extractor="image.metadata", source_type="image")

    written = direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                           slots=DirectSlots(slots=(EXIF_SLOT,)))
    assert len(written) == 1
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert json.loads(rows[0]["evidence_refs"]) == sorted(
        {first.observation_key, second.observation_key})


def test_every_evidence_ref_is_an_observation_key(p6_conn, photo):
    # M14. Task 4 raises `EvidenceRequired` on anything else; this asserts the shape
    # this producer actually stores rather than trusting the writer's guard.
    file_id, content_hash, _ = photo
    direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                 slots=DirectSlots(slots=(EXIF_SLOT,)))
    refs = json.loads(facts_for_file(p6_conn, file_id, content_hash)[0]["evidence_refs"])
    assert refs and all(ref.startswith("sha256:") for ref in refs)


def test_a_prior_versions_observation_is_not_cited(p6_conn, tmp_path):
    # §3.4's cache key and §8.2's records are per content hash. Task 7 owns the
    # filter; this asserts the producer uses it and does not reach for
    # `observations_for_file` itself.
    file_id, content_hash = _file(p6_conn, tmp_path, name="IMG_5.heic",
                                  body=b"\x00version-one")
    old = _observe(p6_conn, run_id="run-old", file_id=file_id,
                   content_hash=content_hash, raw=EXIF_RAW, zone="metadata",
                   container_path=(Segment("field", label="DateTimeOriginal"),),
                   extractor="image.exif", source_type="image")
    second_hash = "c" * 64
    _observe(p6_conn, run_id="run-new", file_id=file_id, content_hash=second_hash,
             raw="2026:08:01 09:00:00", zone="metadata",
             container_path=(Segment("field", label="DateTimeOriginal"),),
             extractor="image.exif", source_type="image")

    direct_facts(p6_conn, file_id=file_id, content_hash=second_hash,
                 slots=DirectSlots(slots=(EXIF_SLOT,)))
    rows = facts_for_file(p6_conn, file_id, second_hash)
    assert [row["field_key"] for row in rows] == ["capture_date"]
    assert old.observation_key not in json.loads(rows[0]["evidence_refs"])
    assert facts_for_file(p6_conn, file_id, content_hash) == []


def test_the_result_does_not_depend_on_the_order_the_slots_were_declared(
        p6_conn, tmp_path):
    # Same reason as Task 7's shuffle test: an outcome that depends on the caller's
    # list order is an outcome §8.5's replay reports as a regression when nothing
    # changed. The write order is (field_key, canonical_value), imposed here.
    def resolve(slots):
        file_id, content_hash = _file(p6_conn, tmp_path,
                                      name=f"{len(slots)}-{slots[0].slot_id}.heic",
                                      body=b"\x00order" + slots[0].slot_id.encode())
        _observe(p6_conn, run_id=f"r-x-{file_id}", file_id=file_id,
                 content_hash=content_hash, raw=EXIF_RAW, zone="metadata",
                 container_path=(Segment("field", label="DateTimeOriginal"),),
                 extractor="image.exif", source_type="image")
        _observe(p6_conn, run_id=f"r-y-{file_id}", file_id=file_id,
                 content_hash=content_hash, raw="application/pdf", zone="metadata",
                 container_path=(Segment("field", label="mime_type"),),
                 extractor="filesystem.record", version="0.1.0",
                 source_type="filesystem", analysis_tier="filesystem")
        direct_facts(p6_conn, file_id=file_id, content_hash=content_hash,
                     slots=DirectSlots(slots=slots))
        return [row["field_key"]
                for row in facts_for_file(p6_conn, file_id, content_hash)]

    assert resolve((EXIF_SLOT, FILE_TYPE_SLOT)) == resolve(
        (FILE_TYPE_SLOT, EXIF_SLOT)) == ["capture_date", "file_type"]


# --- P1 owns identity ------------------------------------------------------------

def test_a_file_p1_does_not_hold_raises_rather_than_writing_a_direct_fact(p6_conn):
    # P1 owns §1.2's identity and P6 re-observes no filesystem. `direct` is the
    # strongest state a deterministic producer writes; writing one against a file the
    # system of record has never seen would put an unanchored fact in the top tier.
    with pytest.raises(UnknownFile):
        direct_facts(p6_conn, file_id="file-that-p1-never-recorded",
                     content_hash="d" * 64,
                     slots=DirectSlots(slots=(EXIF_SLOT,)))


# --- the injection (F8) ----------------------------------------------------------

def test_direct_slots_has_no_default(p6_conn):
    # "Every threshold is injected with no default." A default slot table would be
    # P6 minting the EXIF tag names P5 deliberately refused to publish (P4 D7).
    with pytest.raises(TypeError):
        DirectSlots()
    with pytest.raises(TypeError):
        DirectSlot(slot_id="incomplete", field_key="capture_date")


def test_facts_direct_names_no_slot_and_holds_no_catalogue():
    # Runtime introspection, not a source-text search: a text search matches comments
    # and docstrings and has produced a false result nine times on this project. The
    # module-level namespace must hold no container at all -- every imported symbol is
    # bound to a private name precisely so this guard has nothing to excuse.
    forbidden = {"DateTimeOriginal", "CreateDate", "ModifyDate", "Producer",
                 "Creator", "Author", "Title", "mime_type", "observed_timestamps",
                 "normalized_filename", "extension"}
    assert _code_strings(direct_module) & forbidden == set()

    containers = {name: value for name, value in vars(direct_module).items()
                  if not name.startswith("_")
                  and isinstance(value, (tuple, list, dict, set, frozenset))}
    assert containers == {}


def test_facts_direct_holds_no_date_knowledge():
    # §3.10: "no fuzzy date parsing, ever", and §3.2's `2026-07-17` is produced by
    # the injected canonicaliser above. If this module could turn `2026:07:17
    # 14:03:22` into a date on its own it would be Task 12's job done twice, in the
    # one place with no pattern id to name.
    assert "re" not in vars(direct_module)
    assert not [name for name in vars(direct_module) if "date" in name.lower()]
    # Two adjacent digits, not one: `UnknownFile`'s message names P1 and P6, and a
    # part number is not a date format. Any year, offset, or `%Y:%m:%d` fragment has
    # two in a row.
    assert not [literal for literal in _code_strings(direct_module)
                if any(left.isdigit() and right.isdigit()
                       for left, right in zip(literal, literal[1:]))]
```

- [ ] **Step 2: Run the test and read the failure**

Run: `pytest tests/p6/test_p6_direct.py -v`

Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.direct'`. Tasks 1–6
are green and Task 7 has landed, so `facts.evidence`, `facts.fields`, `facts.values`,
`facts.file_facts`, `facts.unresolved` and `facts.cache` all import; `facts.direct` is the only
missing name. **17 tests fail to collect, 0 pass.**

- [ ] **Step 3: Write the implementation**

```python
# src/facts/direct.py
"""§3.5's direct facts. The slot decides, and the slot is injected.

§3.5: "Deterministic extractors create direct facts when the information comes from a
reliable, explicit source, such as a content hash, EXIF timestamp, a document title,
or a labeled form field." §3.13 repeats it in the reliability vocabulary. Both
sentences name a LOCATION, never a value and never a confidence -- which is P4's own
fixture 6, whose design case reads "direct describes the slot, not the value's
usefulness" over a `raw_value` of `python-docx`.

Three consequences, and each is a test rather than a comment:

* **No test is applied to the observation's own `reliability`.** P4's fixture 12 is
  §3.5's labeled form field and P4 marks it `possible`; a gate here would make one of
  the four named slots unreachable against P4's own fixture for it. An extractor's
  two admissible states are a claim about an OBSERVATION (P4 D11); the fact's six are
  P6's, and Task 1 asserts that boundary from both sides.

* **A `Producer` slot would therefore make `python-docx` a direct fact.** It is
  stopped by §2.2's suppression tier firing first (`facts.discount`), never by
  anything here. This module declares no slot and imports nothing from that one; the
  ordering is the sequencer's.

* **No slot name appears in this file.** P5 spells no EXIF tag name anywhere, on
  purpose (P4 D7: "the source format's own slot name, verbatim"), so a literal here
  would be P6 minting a vocabulary member P5 refused to publish. `DirectSlots`
  arrives at the call with no default. The catalogue behind it does not exist (F8).

The predicate reads P4's `locator` -- `metadata:field=DateTimeOriginal`,
`title:page=1`, `table:sheet=2/row=7/column=3` -- because that is the slot's
published name and reading it needs no rule for which `container_path` segment names
a slot. Such a rule would differ per format, which is what §2.8 exists to prevent.

This producer never abstains. §8.6's order is direct, then rule-validated, then the
model; a field no direct slot filled is a field the next producer has not tried. An
`unresolved` row here would answer §8.5's "Did it abstain when evidence was absent?"
with a claim that had not happened yet. The sequencer writes that row once, at the
end.

`get_file` is read for exactly one thing: P1 owns §1.2's identity, and a `direct`
fact -- the strongest state a deterministic producer writes -- must not be anchored
to a `file_id` the system of record does not hold. No VALUE is taken from the row:
`files.content_hash` and `files.observed_timestamps` are the two columns a careless
implementation would mine for §3.5's first and second slots, and neither is citable
evidence (M14 makes every citation an `observation_key`).
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Callable, Iterable

from database_agent.files_table import get_file as _get_file
from evidence_shape.canonical import canonical_json as _canonical_json
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS as _ANALYSIS_TIERS

from facts.cache import fact_cache_key as _fact_cache_key
from facts.evidence import analysis_tier_for_observation as _tier_of
from facts.evidence import cite as _cite
from facts.evidence import observations_for_version as _observations_for_version
from facts.file_facts import write_fact as _write_fact
from facts.file_facts import DETERMINISTIC_EXTRACTOR
from facts.states import DIRECT
from facts.values import VALUE_ORIGINS as _VALUE_ORIGINS
from facts.values import ensure_value as _ensure_value

#: Task 1 owns the spelling. Never an index into STATES.
DIRECT_STATE: str = DIRECT

#: Task 4 owns the spelling. Never an index into FACT_ORIGINS.
DIRECT_ORIGIN: str = DETERMINISTIC_EXTRACTOR


class UnknownFile(Exception):
    """P1 holds no `files` row for the `file_id` a direct fact was asked for."""


@dataclass(frozen=True)
class DirectSlot:
    """One of §3.5's explicit slots, named and canonicalised by the caller.

    `names` is a predicate over the slot's published name -- P4's
    `Observation.locator`. `canonical` turns the raw reading into the fact's value;
    §3.2's own example is `2026:07:17 14:03:22` becoming `2026-07-17`, and P6 owns
    neither end of that map (round 4's C-5: `normalize(field, raw_value)` is claimed
    by P8's Contract-in and disowned by P6's Task 17, so no part builds it). A
    canonicaliser that raises propagates: a broken injection must not arrive as a
    silent absence of facts (§8.6).
    """

    slot_id: str
    field_key: str
    names: Callable[[str], bool]
    canonical: Callable[[str], str]


@dataclass(frozen=True)
class DirectSlots:
    """The injected slot set. No default, so no call can omit it (F8)."""

    slots: tuple[DirectSlot, ...]


def direct_facts(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                 slots: DirectSlots) -> tuple[str, ...]:
    """§3.5's direct facts for one version of one file. Returns the fact ids.

    Every reading a slot claims becomes a `direct` fact citing the observation it was
    read from. Readings that agree on a value are ONE fact with several citations
    (§3.1: "Every fact preserves where it came from" -- plural); that is not an answer
    to OQ6, which asks how many values a field may hold.
    """
    if _get_file(conn, file_id) is None:
        raise UnknownFile(
            f"P1 holds no files row for {file_id!r}; P6 re-observes no filesystem "
            f"and will not anchor a {DIRECT_STATE!r} fact to a file the system of "
            f"record has never seen"
        )

    grouped: dict[tuple[str, str], list[Observation]] = {}
    for slot in slots.slots:
        for one in _observations_for_version(conn, file_id, content_hash):
            if slot.names(one.locator):
                key = (slot.field_key, slot.canonical(one.raw_value))
                grouped.setdefault(key, []).append(one)

    written: list[str] = []
    for (field_key, canonical_value) in sorted(grouped):
        cited = grouped[(field_key, canonical_value)]
        refs = tuple(sorted({_cite(one) for one in cited}))
        value_id = _ensure_value(conn, field_key=field_key,
                                 canonical_value=canonical_value,
                                 first_evidence_ref=refs[0],
                                 origin=_VALUE_ORIGINS[0])
        written.append(_write_fact(
            conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
            value_id=value_id, reliability_state=DIRECT_STATE,
            origin=DIRECT_ORIGIN, evidence_refs=refs,
            cache_key=_cache_key(conn, content_hash=content_hash,
                                 observations=cited),
            active=True))
    return tuple(written)


def _cache_key(conn: sqlite3.Connection, *, content_hash: str,
               observations: Iterable[Observation]) -> str:
    """§3.4's five parts for a fact built from several observations.

    §3.4 states one extractor version and one analysis tier; a fact citing several
    observations has several of each, and no task owns the reconciliation, so the
    rule is written out here rather than shared -- `facts.cache` is another task's
    module. The versions are the canonical JSON of the sorted distinct
    (name, version) pairs; the tier is the LAST one present in `ANALYSIS_TIERS`
    order -- filesystem < native < ocr < llm -- so a fact that cited an OCR reading
    lands outside the slot the native pass computed under, which is what makes
    preamble rule 5's pass 4 supersede rather than overwrite. Identical wording in
    `facts.families`, `facts.session` and `facts.discount`; see Contract ambiguities.
    """
    observations = tuple(observations)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in observations})
    tiers = {_tier_of(conn, one) for one in observations}
    tier = max(tiers, key=_ANALYSIS_TIERS.index) if tiers else _ANALYSIS_TIERS[0]
    return _fact_cache_key(
        content_hash=content_hash,
        extractor_version=_canonical_json([list(pair) for pair in pairs]),
        analysis_tier=tier, model_identifier=None, prompt_fingerprint=None)
```

- [ ] **Step 4: Run the test and confirm it passes**

Run: `pytest tests/p6/test_p6_direct.py -v`

Expected: PASS — **17 passed**. The two that would have been silently wrong are
`test_the_slot_decides_and_not_the_observations_own_reliability`, which passes only because no gate
on `Observation.reliability` was written, and `test_facts_direct_holds_no_date_knowledge`, which
passes only because every import is bound to a private name and the module holds no digit-bearing
literal.

- [ ] **Step 5: Run the whole P6 suite, because Task 7's guards police this module**

Run: `pytest tests/p6 -q`

Expected: PASS. `tests/p6/test_p6_evidence.py` walks `pkgutil.iter_modules(facts.__path__)` and
fails if any module holds a `source_type`-keyed dict or a code string equal to a member of
`SOURCE_TYPES` or to one of P4's nineteen fixture extractor names. `facts.direct` has neither: the
only literals it contains are the two f-string message fragments in `UnknownFile`, and `"filesystem"`
— which is both a source type and an analysis tier — is reached as `_ANALYSIS_TIERS[0]` rather than
written down.

- [ ] **Step 6: Commit**

```bash
git add src/facts/direct.py tests/p6/test_p6_direct.py
git commit -m "feat(P6): §3.5 direct facts — the slot decides, and the slot is injected"
```

---

---

### Task 9: Roles, and the producer/creator discount (M4)

**Files:**
- Create: `src/facts/discount.py`
- Test: `tests/p6/test_p6_discount.py`

**Interfaces:**
- Consumes: `facts.evidence`, `facts.fields`, `facts.unresolved.write_unresolved`.
- Produces: `discount(observation, *, tool_producer_strings, metadata_property_names) -> str`
  returning one of `suppress` | `demote` | `not_metadata`; `AUTHORSHIP_FIELDS: tuple[str, ...]`;
  `is_discount_target(observation, *, metadata_property_names) -> bool`.
- Also produces, because the skeleton's own `Consumes:` line makes it necessary — three pure
  functions cannot call `write_unresolved`, so the row Done-means 22 requires has nowhere to be
  written: `DISCOUNT_OUTCOMES: tuple[str, str, str]` (the three return values, published once),
  `field_permitted(observation, field_key, *, tool_producer_strings, metadata_property_names) -> bool`,
  and `screen_metadata(conn, *, file_id, content_hash, observations, tool_producer_strings,
  metadata_property_names) -> tuple[Observation, ...]`. Nothing in the skeleton's list is renamed and
  no signature in it is changed.
- Also imports, for the same reason as Task 8: `facts.cache.fact_cache_key`,
  `facts.unresolved.ATTEMPTED_PRODUCERS`, `evidence_shape.canonical.canonical_json`,
  `evidence_shape.vocabulary.ZONES`, `check`, `ANALYSIS_TIERS`.

**Done-means:** 22, and the §3.8 half of 13.

---

**The two tiers, and they are not interchangeable.** This is the half of the part that has already
been got backwards once, in a shipped fixture, so it is stated as a table before anything else:

| The value in the slot | Tier | What P6 does | What P6 must **not** do |
|---|---|---|---|
| A generic **tool** string — `python-docx`, `Mozilla/5.0`, a browser-generated producer string | **Suppression** (§2.2) | **No fact in any field**, `authored_by` included. Exactly one `unresolved` row, `reason = discounted_tool_metadata`. The observation is dropped from the candidate stream | Write it as a `possible` fact. Write it as `authored_by`. Let it reach §3.7's ranking |
| A **human** name — `Jane Chen`, a prior editor, a real author | **Demotion** (§2.3, §3.8) | It may populate **`authored_by`** and no other field. The observation is **kept** in the candidate stream as supporting evidence. `authored_by` is `destination_eligible = FALSE` (§3.8) | Write an `unresolved` row for it. Suppress it. Let it populate topic, purpose, project, subject, institution or target |

Both directions of that swap are asserted below, in named tests, because either one alone would let
the mistake through: `test_a_tool_string_is_suppressed_and_never_demoted` and
`test_a_human_name_is_demoted_and_never_suppressed`.

The design's words for each tier, greppable and quoted whole:

- Suppression, §2.2: *"Author and creator fields may be stale, generic, or generated by a tool
  rather than a person, so a value such as python-docx, Mozilla/5.0, or a browser-generated producer
  string should not be mistaken for meaningful content."* **"Not meaningful content"** is not
  **"weak content"**. A tool name is a true fact about the software and no evidence at all about the
  document, so there is nothing for a `possible` fact to be weak *about*. Demoting it would put a
  wrong answer in the candidate list at low confidence, and §3.7's ranking would then have to beat
  it — which is precisely the contest §2.2 says should never start.
- Demotion, §2.3: *"DOCX author metadata should remain supporting information only, because it may
  identify a prior editor, a document template, or a script rather than the meaningful subject or
  purpose of the file."* Note what that sentence does: it keeps the value (*"supporting
  information"*) and bounds what it may mean (*"rather than the meaningful subject or purpose"*).
  Deleting it would lose real authorship; promoting it would let a prior editor name a folder.
- The role separation, §3.8, verbatim: *"The agent should model these as distinct facets, such as
  authored_by and target_school, or our_firm and client. It should avoid using authorship or creator
  identity as a destination dimension. A folder should not become a collection point for everything
  produced by the same person or organization. Authorship is usually metadata; the document's
  purpose, project, subject, or target is more informative for placement."*

**Why the discount exists at all, and why it is P6's (M4).** There is no marker on the observation.
P4 emits fixture 6 with `reliability = "direct"` because — the fixture's own design case —
*"direct describes the slot, not the value's usefulness"*. P5 emits the producer value verbatim with
no flag, and P5 Open question 13 closes as answered: nobody upstream owned this, and both §2.2 and
§2.3 require it. So the discount is here, and it is keyed on exactly what P4 publishes: `location.zone
= metadata` plus the property name, which is catalogue 01's `match_field` clause word for word.

**`AUTHORSHIP_FIELDS` is `("authored_by",)`, and the three fields it leaves out are left out on
purpose.** §3.8 names four role fields and Task 2 puts all four in the catalogue with
`destination_eligible = FALSE`. This tuple is a narrower thing: the fields a **demoted metadata
value may fill**, and Done-means 22 is literal — *"a human author name in the same slot may populate
`authored_by` and no other field"*. `target_school` and `client` are targets, not authorship;
`our_firm` is an authoring organisation but no Done-means reaches it, and §2.3's stated reason (*"a
prior editor, a document template, or a script"*) is about a person. Widening a rule the design
states narrowly is how a discount becomes a leak. There is a second reason not to name the other
three here: `target_school` (§3.8) and `target university` (§3.11) are one concept under the
one-key-per-concept rule, and which spelling survives is **Task 2's** decision. Naming either in this
module would pre-empt it. The name `AUTHORSHIP_FIELDS` is the skeleton's and is honoured unchanged.

**What "injected" means for catalogue 01, and the one thing that would destroy it.** The catalogue's
own `injection` clause: *"P6 receives this list as data at construction … It is **not** imported as
a module-level constant."* Copying its 115 entries into `src/facts/catalogues.py` satisfies the
letter of Task 25's guard and destroys its point. Two shapes cross the boundary and neither is a
constant:

- **`tool_producer_strings` is a collection of compiled predicates**, `Callable[[str], bool]`, one
  per catalogue entry. It is not a collection of strings, because the catalogue declares three
  `match_kind`s (`exact` 13, `prefix` 86, `regex` 16) whose semantics — the boundary-character set,
  the version-tail rule, `tail_required` — live in the catalogue's `boundary_rule` field **as
  English prose with no machine-readable form**. Implementing that prose inside `facts` would put a
  regex catalogue's semantics in a module Task 25 forbids to hold one, and would freeze catalogue
  v1.0's rules into P6 where a v2.0 could not change them. Compiling belongs with the loader. **That
  compiler does not exist**; see *Contract ambiguities*.
- **`metadata_property_names` is a flat collection of names.** The catalogue groups them by format
  family (`pdf_info_dictionary`, `ooxml_core_properties`, `exif`, `png_text_chunks`, `id3`,
  `icalendar`, `email_headers`, …). **The caller flattens it**, because consuming that mapping inside
  `facts` would be a lookup keyed by format — the branching §2.8 exists to prevent and Task 7's guard
  polices. P6 asks one question: is this slot's name one of the names I was given.

The one piece of matching that **is** P6's, because the catalogue assigns it here in writing:
*"Compare against the raw value with Unicode NFC applied and leading/trailing whitespace stripped,
**for comparison only**. P4 RAW-1/RAW-2 keep the stored `raw_value` byte-for-byte untouched; this
normalization exists inside P6's matcher and never writes back."*

**The rule fires before ranking.** §3.7's procedure decides by score and margin; a suppressed value
that reaches it can win, and a suppressed value that loses still moves the margin and can push a good
candidate below it. So `screen_metadata` runs over the version's observations and returns the
survivors, and the survivors are what any ranking sees. The test for this is the case where the
discounted string would otherwise be top-ranked: the field must end up filled **by the second
candidate**, not left empty for the wrong reason — an empty field there would look like §3.7 doing
its job and would in fact be §2.2's own example beating it.

`facts.facets` is Task 11's and is not in this task's `Consumes:`, so the test states "would
otherwise be top-ranked" in its own terms — highest `occurrence_count` — rather than importing a
ranker. That is the assertion the requirement asks for and it borrows nothing from a module written
in parallel.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_discount.py
"""Done-means 22, M4, §8.5's A04 "generic author metadata", and §3.8's half of 13."""
from __future__ import annotations

import ast
import inspect
import json
import unicodedata
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.fixtures import by_number
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import observations_by_key, record_observation, record_run

from facts import discount as discount_module
from facts.discount import (
    AUTHORSHIP_FIELDS, DISCOUNT_OUTCOMES, discount, field_permitted,
    is_discount_target, screen_metadata,
)
from facts.evidence import cite, observations_for_version
from facts.fields import get_field
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-19T12:00:00+00:00"
SUPPRESS, DEMOTE, NOT_METADATA = DISCOUNT_OUTCOMES

#: Catalogue 01's `property_names`, FLATTENED by the caller. The catalogue groups
#: these by format family; flattening here rather than inside `facts` is what keeps
#: the discount from becoming a lookup keyed by format (§2.8, Task 7's guard).
PROPERTY_NAMES = frozenset({
    "Producer", "Creator", "Author",            # pdf_info_dictionary
    "pdf:Producer", "xmp:CreatorTool", "dc:creator",
    "creator", "lastModifiedBy",                # ooxml_core_properties
    "Application", "AppVersion",
    "meta:generator", "meta:initial-creator",
    "Software", "ProcessingSoftware", "HostComputer",
    "TENC", "TSSE", "PRODID", "X-Mailer", "User-Agent",
})


def _fold(value: str) -> str:
    return value.casefold()


def _exact(match: str, *, case_sensitive: bool):
    """One catalogue `exact` entry, compiled to the predicate P6 is handed.

    Copied from `planning/deferred-catalogues/01-tool-producer-strings.json` by hand.
    Nothing under `src/facts/` reads that file, and nothing under `planning/` is
    edited by this task: the catalogue is data injected at construction, and a test
    is a construction site like any other.
    """
    target = _fold(match) if not case_sensitive else match
    return lambda value: (_fold(value) if not case_sensitive else value) == target


#: `tps-python-docx`: match "python-docx", match_kind "exact", case_sensitive false.
#: `tps-ua-mozilla-5`: match "Mozilla/5.0", match_kind "prefix", case_sensitive true
#: -- rendered here as a bare `startswith` because the catalogue's boundary rule is
#: prose and its compiler does not exist (see Contract ambiguities). The two entries
#: §2.2 names by name are the two this task needs.
TOOL_STRINGS = (
    _exact("python-docx", case_sensitive=False),
    lambda value: value.startswith("Mozilla/5.0"),
)

#: §3.8's "never topic, purpose, project, course, institution or target", spelled in
#: the catalogue's keys. `subject` is D6's key for §3.11's "course".
NON_AUTHORSHIP_FIELDS = ("subject", "purpose", "project", "term", "work_type",
                         "target_university", "application_document_type")


def _file(conn, tmp_path, *, name, body, parent="Documents"):
    path = tmp_path / parent / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context=parent,
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        detected_format="docx", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="metadata",
             slot="Producer", extractor="docx.metadata", version="1.0.0",
             source_type="text_document", reliability="direct", occurrences=1):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version=version,
        source_type=source_type, analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    container = (Segment("field", label=slot),) if slot is not None else ()
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version=version, source_type=source_type, raw_value=raw,
        location=Location(zone, container), occurrence_count=occurrences,
        observed_at=CLOCK, reliability=reliability, run_id=run_id)
    record_observation(conn, observation)
    return observation


def _code_strings(module) -> set[str]:
    """Every string literal that is not a docstring. Same helper as Task 7's file."""
    tree = ast.parse(inspect.getsource(module))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings}


def _screen(conn, file_id, content_hash):
    return screen_metadata(
        conn, file_id=file_id, content_hash=content_hash,
        observations=observations_for_version(conn, file_id, content_hash),
        tool_producer_strings=TOOL_STRINGS,
        metadata_property_names=PROPERTY_NAMES)


@pytest.fixture()
def docx(p6_conn, tmp_path):
    return _file(p6_conn, tmp_path, name="Wash U.docx", body=b"PK\x03\x04docx")


# --- the two tiers, and the swap that must fail -------------------------------

def test_a_tool_string_is_suppressed_and_never_demoted(p6_conn, docx):
    # Done-means 22, first half. §2.2: such a value "should not be mistaken for
    # meaningful content" -- not "for strong content". A tool name is a true fact
    # about the software and no evidence at all about the document, so there is
    # nothing a `possible` fact could be weak about.
    file_id, content_hash = docx
    tool = _observe(p6_conn, run_id="run-tool", file_id=file_id,
                    content_hash=content_hash, raw="python-docx")

    assert discount(tool, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) == SUPPRESS
    assert discount(tool, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) != DEMOTE

    survivors = _screen(p6_conn, file_id, content_hash)
    assert survivors == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert field_permitted(tool, "authored_by", tool_producer_strings=TOOL_STRINGS,
                           metadata_property_names=PROPERTY_NAMES) is False


def test_a_suppressed_tool_string_writes_exactly_one_unresolved_row(p6_conn, docx):
    # Done-means 22's second clause, and B7: the refusal is a record, not a gap.
    # §8.5 asks under Fact quality "Did it abstain when evidence was absent?" and an
    # absent row cannot answer it.
    file_id, content_hash = docx
    tool = _observe(p6_conn, run_id="run-tool", file_id=file_id,
                    content_hash=content_hash, raw="python-docx")
    _screen(p6_conn, file_id, content_hash)

    rows = unresolved_for_file(p6_conn, file_id, content_hash)
    assert len(rows) == 1
    assert rows[0]["reason"] == "discounted_tool_metadata"
    assert rows[0]["field_key"] == AUTHORSHIP_FIELDS[0] == "authored_by"
    assert json.loads(rows[0]["evidence_refs"]) == [cite(tool)]


def test_a_human_name_is_demoted_and_never_suppressed(p6_conn, docx):
    # Done-means 22, second half, and §2.3: author metadata "should remain supporting
    # information only". Supporting information is KEPT. Suppressing it here would
    # lose real authorship and would write an abstention that did not happen.
    file_id, content_hash = docx
    person = _observe(p6_conn, run_id="run-person", file_id=file_id,
                      content_hash=content_hash, raw="Jane Chen", slot="Author")

    assert discount(person, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) == DEMOTE
    assert discount(person, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) != SUPPRESS

    survivors = _screen(p6_conn, file_id, content_hash)
    assert [one.raw_value for one in survivors] == ["Jane Chen"]
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_a_demoted_value_may_populate_authored_by_and_no_other_field(p6_conn, docx):
    # §3.8: "It should avoid using authorship or creator identity as a destination
    # dimension ... Authorship is usually metadata; the document's purpose, project,
    # subject, or target is more informative for placement."
    file_id, content_hash = docx
    person = _observe(p6_conn, run_id="run-person", file_id=file_id,
                      content_hash=content_hash, raw="Jane Chen", slot="creator")

    assert field_permitted(person, "authored_by", tool_producer_strings=TOOL_STRINGS,
                           metadata_property_names=PROPERTY_NAMES) is True
    for field_key in NON_AUTHORSHIP_FIELDS:
        assert field_permitted(
            person, field_key, tool_producer_strings=TOOL_STRINGS,
            metadata_property_names=PROPERTY_NAMES) is False, field_key


def test_the_two_tiers_are_different_outcomes_for_the_same_slot(p6_conn, docx):
    # The anti-swap assertion, stated once with both values in one place: same file,
    # same zone, same property name, two values, two different tiers.
    file_id, content_hash = docx
    tool = _observe(p6_conn, run_id="run-a", file_id=file_id,
                    content_hash=content_hash, raw="python-docx", slot="Creator")
    person = _observe(p6_conn, run_id="run-b", file_id=file_id,
                      content_hash=content_hash, raw="Jane Chen", slot="Author")
    kwargs = dict(tool_producer_strings=TOOL_STRINGS,
                  metadata_property_names=PROPERTY_NAMES)

    assert (discount(tool, **kwargs), discount(person, **kwargs)) == (SUPPRESS, DEMOTE)
    assert [one.raw_value for one in _screen(p6_conn, file_id, content_hash)] == [
        "Jane Chen"]
    assert len(unresolved_for_file(p6_conn, file_id, content_hash)) == 1


# --- §3.8's half of Done-means 13 ---------------------------------------------

def test_authored_by_is_never_destination_eligible(p6_conn):
    # Done-means 13. §3.8: "A folder should not become a collection point for
    # everything produced by the same person or organization."
    for field_key in AUTHORSHIP_FIELDS:
        row = get_field(p6_conn, field_key)
        assert row is not None, field_key
        assert not row["destination_eligible"], field_key


# --- P4's fixture 6, verbatim --------------------------------------------------

def test_fixture_six_is_a_discount_target_and_its_direct_reliability_is_untouched(
        p6_conn, tmp_path):
    # M4 in one assertion: P4 emits `python-docx` with reliability `direct` because
    # `direct` describes the SLOT. P6 discounts the VALUE and changes nothing P4
    # wrote -- the two statements are about different things and both stay true.
    fixture = by_number(6)
    assert fixture.observations[0].raw_value == "python-docx"
    assert fixture.observations[0].reliability == "direct"
    assert fixture.observations[0].locator == "metadata:field=Producer"

    record_run(p6_conn, fixture.run)
    for observation in fixture.observations:
        record_observation(p6_conn, observation)

    assert is_discount_target(fixture.observations[0],
                              metadata_property_names=PROPERTY_NAMES) is True
    assert discount(fixture.observations[0], tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) == SUPPRESS
    still = observations_by_key(p6_conn, fixture.observations[0].observation_key)
    assert [(one.raw_value, one.reliability) for one in still] == [
        ("python-docx", "direct")]


# --- what is and is not a target ------------------------------------------------

def test_a_value_outside_the_metadata_zone_is_not_a_discount_target(p6_conn, docx):
    # Catalogue 01's `match_field`: zone `metadata` PLUS a listed property name. A
    # body paragraph that happens to read "python-docx" is text, and text is §3.7's.
    file_id, content_hash = docx
    body = _observe(p6_conn, run_id="run-body", file_id=file_id,
                    content_hash=content_hash, raw="python-docx", zone="body",
                    slot=None, reliability="possible")

    assert is_discount_target(body, metadata_property_names=PROPERTY_NAMES) is False
    assert discount(body, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) == NOT_METADATA
    assert [one.raw_value for one in _screen(p6_conn, file_id, content_hash)] == [
        "python-docx"]
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_a_metadata_slot_not_on_the_injected_names_is_not_a_target(p6_conn, docx):
    # Catalogue 01: "A slot not on this list is not a discount target." `Subject` is
    # a real PDF info-dictionary slot and is deliberately absent from the list.
    file_id, content_hash = docx
    subject = _observe(p6_conn, run_id="run-subject", file_id=file_id,
                       content_hash=content_hash, raw="python-docx", slot="Subject")

    assert is_discount_target(subject,
                              metadata_property_names=PROPERTY_NAMES) is False
    assert discount(subject, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) == NOT_METADATA


def test_a_metadata_observation_with_no_field_segment_is_not_a_target(p6_conn, docx):
    # P4's `container_path` is a tuple and may be empty. Reading `[0]` unguarded is
    # the crash this asserts is not there.
    file_id, content_hash = docx
    bare = _observe(p6_conn, run_id="run-bare", file_id=file_id,
                    content_hash=content_hash, raw="python-docx", slot=None)
    assert is_discount_target(bare, metadata_property_names=PROPERTY_NAMES) is False


# --- ordering: before the ranking, not after -----------------------------------

def test_the_discount_fires_before_ranking_and_the_second_candidate_wins(
        p6_conn, docx):
    # The requirement, in its own words: run a corpus where the discounted string
    # would otherwise be the top-ranked candidate and show the field is filled by the
    # second candidate rather than left empty for the wrong reason. `facts.facets` is
    # Task 11's and is not imported; "top-ranked" is stated here as the highest
    # occurrence count, which is what makes the setup adversarial in the first place.
    file_id, content_hash = docx
    _observe(p6_conn, run_id="run-tool", file_id=file_id, content_hash=content_hash,
             raw="python-docx", occurrences=40)
    _observe(p6_conn, run_id="run-real", file_id=file_id, content_hash=content_hash,
             raw="Columbia", zone="heading", slot=None, reliability="possible",
             occurrences=3)

    before = observations_for_version(p6_conn, file_id, content_hash)
    assert max(before, key=lambda one: one.occurrence_count).raw_value == "python-docx"

    survivors = _screen(p6_conn, file_id, content_hash)
    assert survivors != ()
    assert max(survivors, key=lambda one: one.occurrence_count).raw_value == "Columbia"


def test_screening_preserves_the_order_it_was_given(p6_conn, docx):
    # Task 7's read is already a total order keyed on `observation_key`. Screening
    # filters; it must not reorder, or every downstream tie changes for a reason that
    # has nothing to do with the corpus (§8.5 replay).
    file_id, content_hash = docx
    for index, raw in enumerate(("Columbia", "Wash U", "UChicago")):
        _observe(p6_conn, run_id=f"run-{index}", file_id=file_id,
                 content_hash=content_hash, raw=raw, zone="heading", slot=None,
                 reliability="possible")
    _observe(p6_conn, run_id="run-tool", file_id=file_id, content_hash=content_hash,
             raw="python-docx")

    given = observations_for_version(p6_conn, file_id, content_hash)
    survivors = _screen(p6_conn, file_id, content_hash)
    assert [cite(one) for one in survivors] == [
        cite(one) for one in given if one.raw_value != "python-docx"]


# --- matching: normalized for comparison, never written back --------------------

def test_the_matcher_normalizes_for_comparison_only(p6_conn, docx):
    # Catalogue 01: "Compare against the raw value with Unicode NFC applied and
    # leading/trailing whitespace stripped, for comparison only. P4 RAW-1/RAW-2 keep
    # the stored raw_value byte-for-byte untouched."
    file_id, content_hash = docx
    padded = _observe(p6_conn, run_id="run-pad", file_id=file_id,
                      content_hash=content_hash, raw="  PYTHON-DOCX ")

    assert discount(padded, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) == SUPPRESS
    still = observations_by_key(p6_conn, padded.observation_key)
    assert [one.raw_value for one in still] == ["  PYTHON-DOCX "]


def test_a_composed_and_a_decomposed_value_match_the_same_entry(p6_conn, docx):
    # NFC, from the same clause. The two spellings of the same string must not give
    # two different tiers, because which one an extractor emits is the reader's
    # accident and not a fact about the file.
    file_id, content_hash = docx
    decomposed = unicodedata.normalize("NFD", "Café Writer")
    assert decomposed != "Café Writer"
    observation = _observe(p6_conn, run_id="run-nfd", file_id=file_id,
                           content_hash=content_hash, raw=decomposed)
    matcher = (_exact("Café Writer", case_sensitive=False),)

    assert discount(observation, tool_producer_strings=matcher,
                    metadata_property_names=PROPERTY_NAMES) == SUPPRESS


def test_one_unresolved_row_even_when_several_slots_carry_a_tool_string(
        p6_conn, docx):
    # Done-means 22 says ONE row. A DOCX commonly writes the same generator into
    # `creator` and `lastModifiedBy`; two rows would double-count one refusal and
    # make §8.5's abstention count wrong.
    file_id, content_hash = docx
    first = _observe(p6_conn, run_id="run-1", file_id=file_id,
                     content_hash=content_hash, raw="python-docx", slot="creator")
    second = _observe(p6_conn, run_id="run-2", file_id=file_id,
                      content_hash=content_hash, raw="python-docx",
                      slot="lastModifiedBy")
    _screen(p6_conn, file_id, content_hash)

    rows = unresolved_for_file(p6_conn, file_id, content_hash)
    assert len(rows) == 1
    assert json.loads(rows[0]["evidence_refs"]) == sorted(
        {cite(first), cite(second)})


def test_screening_a_version_with_nothing_to_discount_writes_no_row(p6_conn, docx):
    # An abstention that did not happen must not be recorded as one (B7).
    file_id, content_hash = docx
    _observe(p6_conn, run_id="run-clean", file_id=file_id,
             content_hash=content_hash, raw="Columbia", zone="heading", slot=None,
             reliability="possible")
    assert len(_screen(p6_conn, file_id, content_hash)) == 1
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


# --- the injection --------------------------------------------------------------

def test_the_list_and_the_property_names_have_no_defaults(p6_conn, docx):
    # Catalogue 01: "P6 receives this list as data at construction ... It is not
    # imported as a module-level constant."
    file_id, content_hash = docx
    observation = _observe(p6_conn, run_id="run-inj", file_id=file_id,
                           content_hash=content_hash, raw="python-docx")
    with pytest.raises(TypeError):
        discount(observation)
    with pytest.raises(TypeError):
        discount(observation, tool_producer_strings=TOOL_STRINGS)
    with pytest.raises(TypeError):
        is_discount_target(observation)


def test_facts_discount_holds_no_producer_string_and_no_property_catalogue():
    # Runtime introspection over the module namespace, not a source-text search.
    # Copying catalogue 01 into `src/facts/` would satisfy Task 25's letter and
    # destroy its point, so the guard is here as well as there.
    literals = _code_strings(discount_module)
    assert "python-docx" not in literals
    assert not [one for one in literals if one.startswith("Mozilla")]
    assert literals & PROPERTY_NAMES == set()

    catalogues = {name: value for name, value in vars(discount_module).items()
                  if not name.startswith("_")
                  and name not in {"AUTHORSHIP_FIELDS", "DISCOUNT_OUTCOMES"}
                  and isinstance(value, (tuple, list, dict, set, frozenset))}
    assert catalogues == {}
    assert len(AUTHORSHIP_FIELDS) == 1
    assert len(DISCOUNT_OUTCOMES) == 3
```

- [ ] **Step 2: Run the test and read the failure**

Run: `pytest tests/p6/test_p6_discount.py -v`

Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.discount'`.
Everything else it imports is green: Tasks 1–6 plus Task 7's `facts.evidence`. **18 tests fail to
collect, 0 pass.**

- [ ] **Step 3: Write the implementation**

```python
# src/facts/discount.py
"""§2.2/§2.3's producer, creator and author discount, and §3.8's role bound (M4).

**Two tiers, and they are not interchangeable.** Getting them the other way round is
the mistake this module is written against.

* **Suppression (§2.2).** A generic TOOL string produces **no fact in any field**,
  `authored_by` included, and one `unresolved` row with
  `reason = discounted_tool_metadata`. §2.2: "a value such as python-docx,
  Mozilla/5.0, or a browser-generated producer string should not be mistaken for
  meaningful content." Not-meaningful is not weak: a tool name is a true fact about
  the software and no evidence about the document, so there is nothing for a
  `possible` fact to be weak about, and letting one into §3.7's ranking starts a
  contest §2.2 says should never start.

* **Demotion (§2.3, §3.8).** Any other producer/creator/author value is KEPT. §2.3:
  such metadata "should remain supporting information only, because it may identify a
  prior editor, a document template, or a script rather than the meaningful subject or
  purpose of the file." It may populate `authored_by` and no other field, it is never
  destination-eligible (§3.8), and it gets NO `unresolved` row -- an abstention that
  did not happen must not be recorded as one (B7).

**Why the discount is P6's (M4).** There is no marker on the observation. P4 emits
fixture 6 with `reliability = "direct"` because "direct describes the slot, not the
value's usefulness"; P5 emits the value verbatim with no flag. Nobody upstream owned
this and both sections require it, so it is here, keyed on exactly what P4 publishes:
`location.zone == metadata` plus the `field`-kind segment's label -- catalogue 01's
`match_field` clause word for word.

**Everything catalogue-shaped is injected.** `tool_producer_strings` is a collection
of compiled predicates, one per catalogue entry, because the catalogue declares three
`match_kind`s whose semantics (the boundary-character set, the version-tail rule) live
in its `boundary_rule` field as prose with no machine-readable form; compiling belongs
with the loader, so a catalogue v2.0 needs no change here. `metadata_property_names`
arrives FLAT: the catalogue groups the names by format family, and consuming that
mapping here would be a lookup keyed by format -- the branching §2.8 exists to prevent.

The one piece of matching that IS P6's, because the catalogue assigns it here in
writing: "Compare against the raw value with Unicode NFC applied and leading/trailing
whitespace stripped, for comparison only ... this normalization exists inside P6's
matcher and never writes back."

**Ordering.** `screen_metadata` returns survivors, and the survivors are what any
ranking sees. §3.7 decides by score and margin, so a suppressed value that reaches it
can win outright, and one that loses still moves the margin and can push a good
candidate under it -- an empty field that looks like §3.7 working and is in fact
§2.2's own example beating it.
"""
from __future__ import annotations

import sqlite3
import unicodedata
from typing import Callable, Collection, Iterable

from evidence_shape.canonical import canonical_json as _canonical_json
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS as _ANALYSIS_TIERS
from evidence_shape.vocabulary import ZONES as _ZONES
from evidence_shape.vocabulary import check as _check

from facts.cache import fact_cache_key as _fact_cache_key
from facts.evidence import analysis_tier_for_observation as _tier_of
from facts.evidence import cite as _cite
from facts.unresolved import ATTEMPTED_PRODUCERS as _ATTEMPTED_PRODUCERS
from facts.unresolved import write_unresolved as _write_unresolved

#: The three outcomes, published once. `suppress` and `demote` are §2.2's and §2.3's
#: two tiers; `not_metadata` is "this observation is not in the slots the discount
#: reads", which is neither a refusal nor a permission.
DISCOUNT_OUTCOMES: tuple[str, str, str] = ("suppress", "demote", "not_metadata")

#: The fields a DEMOTED metadata value may fill. Done-means 22 is literal: "a human
#: author name in the same slot may populate `authored_by` and no other field". §3.8
#: names four role fields and Task 2 carries all four with
#: `destination_eligible = FALSE`; this is the narrower set, because `target_school`
#: and `client` are targets rather than authorship and no Done-means reaches
#: `our_firm`. Naming §3.8's `target_school` here would also pre-empt Task 2's
#: decision about whether that concept's key is `target_school` or §3.11's
#: `target_university` -- one concept, one key, and it is not this module's to pick.
AUTHORSHIP_FIELDS: tuple[str, ...] = ("authored_by",)

#: P4's zone the discount reads. Validated against P4's published vocabulary at
#: import, so a rename upstream is a load error rather than a rule that silently
#: stops firing.
_METADATA_ZONE: str = _check("metadata", _ZONES, name="zone")

_SUPPRESS, _DEMOTE, _NOT_METADATA = DISCOUNT_OUTCOMES


def is_discount_target(observation: Observation, *,
                       metadata_property_names: Collection[str]) -> bool:
    """Catalogue 01's `match_field`: zone `metadata` plus a listed property name.

    "A slot not on this list is not a discount target." An observation with no
    `field`-kind segment has no slot name and is therefore not one either -- P4's
    `container_path` is a tuple and is routinely empty.
    """
    if observation.zone != _METADATA_ZONE:
        return False
    return _slot_name(observation) in metadata_property_names


def discount(observation: Observation, *,
             tool_producer_strings: Collection[Callable[[str], bool]],
             metadata_property_names: Collection[str]) -> str:
    """§2.2/§2.3's two tiers. One of `DISCOUNT_OUTCOMES`."""
    if not is_discount_target(observation,
                              metadata_property_names=metadata_property_names):
        return _NOT_METADATA
    candidate = _for_comparison(observation.raw_value)
    if any(matches(candidate) for matches in tool_producer_strings):
        return _SUPPRESS
    return _DEMOTE


def field_permitted(observation: Observation, field_key: str, *,
                    tool_producer_strings: Collection[Callable[[str], bool]],
                    metadata_property_names: Collection[str]) -> bool:
    """May this observation support a fact in this field?

    §3.8, in one predicate: a suppressed value supports nothing, a demoted value
    supports an authorship role and "no other field" (Done-means 22), and an
    observation the discount does not read is not this module's to restrict.
    """
    outcome = discount(observation, tool_producer_strings=tool_producer_strings,
                       metadata_property_names=metadata_property_names)
    if outcome == _SUPPRESS:
        return False
    if outcome == _DEMOTE:
        return field_key in AUTHORSHIP_FIELDS
    return True


def screen_metadata(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                    observations: Iterable[Observation],
                    tool_producer_strings: Collection[Callable[[str], bool]],
                    metadata_property_names: Collection[str],
                    ) -> tuple[Observation, ...]:
    """Drop the suppressed observations, record the refusal, keep everything else.

    Returns the survivors in the order they were given -- Task 7's read is already a
    total order keyed on `observation_key`, and reordering here would change every
    downstream tie for a reason that has nothing to do with the corpus (§8.5).

    ONE `unresolved` row is written for the whole version, citing every suppressed
    observation: a DOCX commonly writes the same generator into `creator` and
    `lastModifiedBy`, and two rows would double-count one refusal. The row names
    `AUTHORSHIP_FIELDS[0]`, which is the field the value would otherwise have filled
    -- Done-means 22's "no fact in any field, including `authored_by`" recorded as the
    one field there was to refuse.
    """
    observations = tuple(observations)
    suppressed = [one for one in observations
                  if discount(one, tool_producer_strings=tool_producer_strings,
                              metadata_property_names=metadata_property_names)
                  == _SUPPRESS]
    if suppressed:
        _write_unresolved(
            conn, file_id=file_id, content_hash=content_hash,
            field_key=AUTHORSHIP_FIELDS[0], reason="discounted_tool_metadata",
            attempted_producers=(_ATTEMPTED_PRODUCERS[0],),
            evidence_refs=tuple(sorted({_cite(one) for one in suppressed})),
            cache_key=_cache_key(conn, content_hash=content_hash,
                                 observations=suppressed))
    dropped = {id(one) for one in suppressed}
    return tuple(one for one in observations if id(one) not in dropped)


def _slot_name(observation: Observation) -> str:
    """The `field`-kind segment's label, or the empty string.

    Catalogue 01 names this read: "the `field`-kind segment's label is one of the
    property names below". Task 8 reads the whole `locator` instead, because its
    predicates are the caller's and a locator needs no extraction rule; the two reads
    differ because their sources ask for different things.
    """
    for segment in observation.location.container_path:
        if segment.kind == "field" and segment.label:
            return segment.label
    return ""


def _for_comparison(raw_value: str) -> str:
    """Catalogue 01's `normalization_for_matching`, and nothing else.

    "Compare against the raw value with Unicode NFC applied and leading/trailing
    whitespace stripped, for comparison only." Never written back: P4's
    `evidence_never_overwritten` trigger would refuse it, and §3.2 requires the
    original evidence to survive the conclusion built from it.
    """
    return unicodedata.normalize("NFC", raw_value).strip()


def _cache_key(conn: sqlite3.Connection, *, content_hash: str,
               observations: Iterable[Observation]) -> str:
    """§3.4's five parts for a record built from several observations.

    Identical to `facts.direct._cache_key`, `facts.families` and `facts.session`: the
    versions are the canonical JSON of the sorted distinct (name, version) pairs, and
    the tier is the last present in `ANALYSIS_TIERS` order, so a record that cited an
    OCR reading lands outside the slot the native pass computed under. See Contract
    ambiguities -- the reconciliation belongs in `facts.cache`, which is Task 6's.
    """
    observations = tuple(observations)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in observations})
    tiers = {_tier_of(conn, one) for one in observations}
    tier = max(tiers, key=_ANALYSIS_TIERS.index) if tiers else _ANALYSIS_TIERS[0]
    return _fact_cache_key(
        content_hash=content_hash,
        extractor_version=_canonical_json([list(pair) for pair in pairs]),
        analysis_tier=tier, model_identifier=None, prompt_fingerprint=None)
```

- [ ] **Step 4: Run the test and confirm it passes**

Run: `pytest tests/p6/test_p6_discount.py -v`

Expected: PASS — **18 passed**. The four that would each have caught the swap on their own are
`test_a_tool_string_is_suppressed_and_never_demoted`,
`test_a_human_name_is_demoted_and_never_suppressed`,
`test_the_two_tiers_are_different_outcomes_for_the_same_slot` and
`test_a_suppressed_tool_string_writes_exactly_one_unresolved_row` — the last because a demotion that
wrote a row, or a suppression that did not, both fail on the count.

`test_authored_by_is_never_destination_eligible` passes only if Task 2 landed `authored_by` with
`destination_eligible = FALSE`. If it fails, the finding is Task 2's catalogue, not this module: round
1's F-1 is exactly that failure and Done-means 13 and 22 are both unwritable without the row.

- [ ] **Step 5: Run the whole P6 suite, because Task 7's guards police this module too**

Run: `pytest tests/p6 -q`

Expected: PASS. `facts.discount` holds no dict keyed by `source_type` and no code string equal to a
member of `SOURCE_TYPES` or to one of P4's nineteen fixture extractor names: its literals are
`"metadata"` (a `ZONES` member, checked against P4's tuple at import), `"field"` (a `Segment.kind`),
`"discounted_tool_metadata"` (checked against `UNRESOLVED_REASONS` by Task 5's writer), the three
`DISCOUNT_OUTCOMES` and `"authored_by"`.

- [ ] **Step 6: Commit**

```bash
git add src/facts/discount.py tests/p6/test_p6_discount.py
git commit -m "feat(P6): §2.2/§2.3 producer discount — suppression, demotion, and §3.8's role bound"
```

---

---

### Task 10: Rule-validated facts, and the §3.5 context check (N-6)

**Files:**
- Create: `src/facts/rules.py`
- Test: `tests/p6/test_p6_rules.py`

**Interfaces:**
- Consumes: `facts.evidence` — `observations_for_version`, `context_pair`, `cite`,
  `analysis_tier_for_observation`; `facts.facets.word_boundary_match`; `facts.file_facts` —
  `write_fact`, `FACT_ORIGINS`; `facts.unresolved` — `write_unresolved`, `ATTEMPTED_PRODUCERS`;
  `facts.values` — `ensure_value`, `VALUE_ORIGINS`; `facts.states.STATES`;
  `facts.cache.fact_cache_key`; `evidence_shape.canonical.canonical_json`;
  `evidence_shape.vocabulary.ANALYSIS_TIERS`.
- Produces: `ACADEMIC_CONTEXT_TERMS: tuple[str, str, str, str, str]`, `MalformedRule`,
  `Rule(pattern, required_context_terms, field_key)` — an injected frozen dataclass;
  `context_check(before: str, after: str, terms) -> bool`;
  `apply_rules(conn, *, file_id, content_hash, rules) -> tuple[str, ...]`.

**Done-means:** 8, and the `validated` half of 4.

**The rule is literal, and its five terms are the whole authored vocabulary.** §3.5, verbatim:
*"Rules create validated facts when a candidate passes strict context checks. For example, BUSIB
4300 becomes a course fact only when the engine finds a course-code pattern together with academic
context such as "syllabus," "lecture," "credits," "instructor," or "semester.""* Five terms are
stated. The SPEC's Deferred table says the rest is unauthored — *"Rule context-term lists beyond the
five literal academic terms | §3.5 | Only "syllabus", "lecture", "credits", "instructor",
"semester" are stated. Every other domain's context vocabulary is unauthored."* So this module
publishes exactly those five and every other rule's terms arrive on the `Rule`. **There is no sixth
term**, and "course", "class", "professor" and "seminar" — all of which read as academic context to
a human — are each a test below that must fail the check.

**The stored field key is `subject` (D6), and this module never spells it.** §3.11's Academic row
says "course"; §3.1, §3.2 and §3.12 all say `subject`; D6 ratified `subject` because a field key is
a join handle and two spellings are two columns. `Rule.field_key` is data, so `facts.rules` names no
field at all and the tests supply `subject`.

**The pattern is injected too.** A course-code regex is not among §3.10's three named patterns, so
it is part of the Deferred catalogue. `Rule.pattern` is a **compiled** `re.Pattern`; a string is
refused, because §3.10 requires *"explicit regular expressions"* and a string would let a caller
pass something that is silently treated as a literal by one call site and as syntax by another.

**Case-insensitive, and it does not relax the boundary (N-6, B8(a)).** §3.5 writes its terms in
lowercase and states no matching rule, so P6 states one. P4's fixture 1 carries `context_before`
exactly `"Syllabus — "` with a capital S — B8(a) authored it that way so the walking skeleton's one
fact would resolve — and a case-sensitive check refuses it. But folding case is not relaxing the
boundary: the matcher is `facts.facets.word_boundary_match`, the same one §3.7 facet values go
through, so `semester` still cannot match inside `Semesterly` and A01's `MIT`-inside-"submit" is
refused by the boundary rather than by case.

**A truncated context is a different refusal.** §8.6 forbids silent truncation. A check that fails
on a record with `context_truncated = true` writes `reason = context_truncated`, never
`context_check_failed`: the term may have been cut off, and claiming a clean refusal would be a
claim this module cannot support. A check that **passes** on a truncated record still produces the
fact — if the term is present, it was not the part that got cut.

**A pattern that does not match writes nothing at all.** The SPEC's reason for
`context_check_failed` is *"§3.5 rule matched the pattern, found no required context term"* — the
pattern match is the precondition of the refusal. Without that, `unresolved` would fill with every
field every rule could theoretically have produced, and Done-means 18's *"every refusal … also
writes an `unresolved` row"* would become noise rather than a record.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_rules.py
"""§3.5 rule-validated facts -- Done-means 8, N-6, B8(a), and A03's ZIP-code case."""
import dataclasses
import json
import re
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.fixtures import by_number
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.file_facts import facts_for_file
from facts.rules import (
    ACADEMIC_CONTEXT_TERMS, MalformedRule, Rule, apply_rules, context_check,
)
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-22T00:00:00Z"

#: §3.10's catalogue is Deferred beyond the three named date patterns, and a
#: course-code pattern is not among them -- so the pattern is the test's, injected on
#: the Rule, and `facts.rules` holds no regex of its own.
COURSE_CODE = re.compile(r"\b[A-Z]{2,5} ?\d{2,5}\b")


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _run(conn, *, run_id, file_id, content_hash, analysis_tier="native"):
    if conn.execute("SELECT 1 FROM extraction_runs WHERE run_id = ?",
                    (run_id,)).fetchone() is None:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="1.0.0",
            source_type="text_document", analysis_tier=analysis_tier, config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="heading",
             context_before=None, context_after=None, context_truncated=False):
    _run(conn, run_id=run_id, file_id=file_id, content_hash=content_hash)
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, (Segment("page", 1), Segment("heading", 2))),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=run_id, context_before=context_before, context_after=context_after,
        context_truncated=context_truncated)
    record_observation(conn, observation)
    return observation


def _course_rule(terms=ACADEMIC_CONTEXT_TERMS):
    # D6: the stored academic key is `subject`. §3.11's word "course" is the design's
    # prose for the same field and survives inside quotations only.
    return Rule(pattern=COURSE_CODE, required_context_terms=tuple(terms),
                field_key="subject")


# --- the five terms are the design's, complete, and closed -------------------

def test_the_five_context_terms_are_exactly_the_designs_five():
    # §3.5, verbatim: "a course-code pattern together with academic context such as
    # "syllabus," "lecture," "credits," "instructor," or "semester."" Five terms are
    # stated literally; a sixth is a design change, not an implementation detail.
    assert ACADEMIC_CONTEXT_TERMS == ("syllabus", "lecture", "credits",
                                      "instructor", "semester")
    assert len(ACADEMIC_CONTEXT_TERMS) == 5
    assert len(set(ACADEMIC_CONTEXT_TERMS)) == 5


def test_no_other_context_vocabulary_is_authored_in_the_module():
    # "Rule context-term lists beyond the five literal academic terms | §3.5 | Only
    # "syllabus", "lecture", "credits", "instructor", "semester" are stated. Every
    # other domain's context vocabulary is unauthored."
    import facts.file_facts
    import facts.rules as module
    import facts.states
    import facts.unresolved
    import facts.values
    import evidence_shape.vocabulary
    foreign = {id(value)
               for source in (evidence_shape.vocabulary, facts.states,
                              facts.file_facts, facts.unresolved, facts.values)
               for value in vars(source).values()}
    catalogues = [name for name, value in vars(module).items()
                  if isinstance(value, tuple) and value and id(value) not in foreign
                  and all(isinstance(entry, str) for entry in value)]
    assert catalogues == ["ACADEMIC_CONTEXT_TERMS"]


def test_a_rule_carries_its_own_terms_and_the_module_supplies_no_default():
    # Every other domain's terms arrive injected; there is no default argument that
    # would quietly lend the academic five to a research or finance rule.
    with pytest.raises(TypeError):
        Rule(pattern=COURSE_CODE, field_key="subject")
    with pytest.raises(MalformedRule):
        Rule(pattern=COURSE_CODE, required_context_terms=(), field_key="subject")
    with pytest.raises(MalformedRule):
        Rule(pattern=r"\b[A-Z]{2,5} ?\d{3,4}\b",
             required_context_terms=ACADEMIC_CONTEXT_TERMS, field_key="subject")


# --- the context check itself ------------------------------------------------

def test_the_context_check_is_case_insensitive():
    # N-6. §3.5 writes its terms lowercase and states no matching rule, so P6 states
    # one: a term matches regardless of the case it appears in.
    for spelling in ("Syllabus", "SYLLABUS", "syllabus", "SyLLaBuS"):
        assert context_check(f"{spelling} - ", "", ACADEMIC_CONTEXT_TERMS) is True


def test_case_insensitivity_does_not_relax_the_word_boundary():
    # The §3.7 discipline is unchanged: a case-insensitive match is not a substring
    # match, so `semester` must not match inside a longer word.
    assert context_check("Semesterly digest", "", ACADEMIC_CONTEXT_TERMS) is False
    assert context_check("", "mid-semester break", ACADEMIC_CONTEXT_TERMS) is True
    assert context_check("lectureship award", "", ACADEMIC_CONTEXT_TERMS) is False


def test_both_halves_of_the_context_pair_are_read_and_never_concatenated():
    # M5: P4 split the context so §8.4 can redact a value without dropping its
    # context. Joining the halves would forge an adjacency the document does not have.
    assert context_check("Instructor: ", "", ACADEMIC_CONTEXT_TERMS) is True
    assert context_check("", " - 3 credits", ACADEMIC_CONTEXT_TERMS) is True
    assert context_check("sylla", "bus", ACADEMIC_CONTEXT_TERMS) is False


def test_an_absent_context_half_is_not_a_match():
    assert context_check("", "", ACADEMIC_CONTEXT_TERMS) is False
    assert context_check(None, None, ACADEMIC_CONTEXT_TERMS) is False


# --- Done-means 8, both halves ----------------------------------------------

def test_a_course_code_with_no_academic_context_produces_no_fact(p6_conn, tmp_path):
    # Done-means 8, negative half: "A course-code-shaped string with no academic
    # context term in its surrounding context produces no course fact."
    file_id, content_hash = _record(p6_conn, tmp_path, name="receipt.pdf",
                                    body=b"receipt")
    _observe(p6_conn, run_id="r-plain", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="Order ", context_after=" shipped")
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="subject")
    assert [r["reason"] for r in rows] == ["context_check_failed"]


def test_p4s_fixture_1_verbatim_does_produce_one_validated_fact(p6_conn, tmp_path):
    # Done-means 8, positive half, and B8(a): fixture 1 carries `context_before`
    # exactly "Syllabus - " with a capital S. A case-sensitive check refuses it and
    # the walking skeleton produces no fact at all.
    fixture = by_number(1)
    original = fixture.observations[0]
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300 Syllabus")
    _run(p6_conn, run_id="fixture-1", file_id=file_id, content_hash=content_hash)
    observation = dataclasses.replace(original, file_id=file_id,
                                      content_hash=content_hash, run_id="fixture-1")
    record_observation(p6_conn, observation)

    assert observation.raw_value == "BUSIB 4300"
    assert observation.context_before == "Syllabus — "   # capital S, EM DASH
    assert observation.context_before[0] == "S"

    written = apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                          rules=(_course_rule(),))
    assert len(written) == 1
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(r["field_key"], r["canonical_value"], r["reliability_state"])
            for r in rows] == [("subject", "BUSIB 4300", "validated")]
    assert json.loads(rows[0]["evidence_refs"]) == [observation.observation_key]
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_the_fact_cites_an_observation_key_and_leaves_the_raw_value_alone(
        p6_conn, tmp_path):
    # §3.2: the conclusion is stored beside the evidence, and the evidence survives.
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300")
    observation = _observe(p6_conn, run_id="r-ok", file_id=file_id,
                           content_hash=content_hash, raw="BUSIB 4300",
                           context_before="Syllabus — ")
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(_course_rule(),))
    refs = json.loads(facts_for_file(p6_conn, file_id, content_hash)[0]["evidence_refs"])
    assert refs == [observation.observation_key]
    assert all(ref.startswith("sha256:") for ref in refs)
    stored = p6_conn.execute("SELECT raw_value FROM evidence WHERE file_id = ?",
                             (file_id,)).fetchone()
    assert stored["raw_value"] == "BUSIB 4300"


def test_every_one_of_the_five_terms_satisfies_the_check_on_its_own(
        p6_conn, tmp_path):
    for index, term in enumerate(ACADEMIC_CONTEXT_TERMS):
        file_id, content_hash = _record(p6_conn, tmp_path, name=f"t{index}.pdf",
                                        body=f"BUSIB 4300 {term}".encode())
        _observe(p6_conn, run_id=f"r{index}", file_id=file_id,
                 content_hash=content_hash, raw="BUSIB 4300",
                 context_after=f" ({term.title()})")
        assert len(apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                               rules=(_course_rule(),))) == 1


def test_a_term_outside_the_five_does_not_satisfy_the_check(p6_conn, tmp_path):
    # "course", "class", "professor" and "seminar" all read as academic context to a
    # human. The design names five and this module authors no sixth.
    for index, near_miss in enumerate(("course", "class", "professor", "seminar")):
        file_id, content_hash = _record(p6_conn, tmp_path, name=f"n{index}.pdf",
                                        body=f"BUSIB 4300 {near_miss}".encode())
        _observe(p6_conn, run_id=f"n{index}", file_id=file_id,
                 content_hash=content_hash, raw="BUSIB 4300",
                 context_before=f"{near_miss} ")
        assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                           rules=(_course_rule(),)) == ()
        assert [r["reason"] for r in unresolved_for_file(
            p6_conn, file_id, content_hash)] == ["context_check_failed"]


# --- §8.6: a cut context is not a clean refusal ------------------------------

def test_a_failed_check_on_a_truncated_record_is_context_truncated(
        p6_conn, tmp_path):
    # §8.6 forbids silent truncation. The term may have been cut off, so this is not
    # the same refusal as "the term is not there".
    file_id, content_hash = _record(p6_conn, tmp_path, name="cut.pdf", body=b"cut")
    _observe(p6_conn, run_id="r-cut", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="...ourse outline for ",
             context_after=" and the", context_truncated=True)
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="subject")
    assert [r["reason"] for r in rows] == ["context_truncated"]
    assert unresolved_for_file(p6_conn, file_id, content_hash,
                               reason="context_check_failed") == []


def test_a_truncated_record_whose_check_passes_still_produces_the_fact(
        p6_conn, tmp_path):
    # Truncation is only a problem for a refusal. If the term is present, it was not
    # the part that got cut.
    file_id, content_hash = _record(p6_conn, tmp_path, name="cut2.pdf", body=b"cut")
    _observe(p6_conn, run_id="r-cut2", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="...Syllabus — ",
             context_truncated=True)
    assert len(apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                           rules=(_course_rule(),))) == 1
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


# --- the shape of the refusal set --------------------------------------------

def test_a_pattern_that_does_not_match_writes_no_row_at_all(p6_conn, tmp_path):
    # A rule that does not apply is not a refusal. Writing one would fill
    # `unresolved` with every field every rule could theoretically have produced.
    file_id, content_hash = _record(p6_conn, tmp_path, name="prose.pdf",
                                    body=b"prose")
    _observe(p6_conn, run_id="r-none", file_id=file_id, content_hash=content_hash,
             raw="a paragraph about nothing in particular",
             context_before="Syllabus — ")
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_a03s_zip_code_produces_no_subject_fact(p6_conn, tmp_path):
    # A03, `subject_ref: "A03::zip::course"`, `expected_outcome_kind: "abstained"`,
    # `forbidden_value: {"field": "course", "value": "MA 02139"}` -- read on the
    # stored key, which D6 fixes as `subject`. The pattern DOES match; the context
    # check is what refuses it, which is exactly §3.5's point.
    file_id, content_hash = _record(p6_conn, tmp_path, name="A03-zip.txt",
                                    body=b"Ship to Cambridge MA 02139 by Friday.")
    _observe(p6_conn, run_id="A03-zip", file_id=file_id, content_hash=content_hash,
             raw="MA 02139", zone="body", context_before="Ship to Cambridge ",
             context_after=" by Friday.")
    assert COURSE_CODE.search("MA 02139") is not None
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert [r["reason"] for r in unresolved_for_file(
        p6_conn, file_id, content_hash)] == ["context_check_failed"]


def test_a03s_device_model_produces_no_subject_fact(p6_conn, tmp_path):
    # A03's second subject: `{"field": "course", "value": "XPS 13"}`.
    file_id, content_hash = _record(p6_conn, tmp_path, name="A03-device.txt",
                                    body=b"Receipt for one XPS 13 laptop.")
    _observe(p6_conn, run_id="A03-device", file_id=file_id,
             content_hash=content_hash, raw="XPS 13", zone="body",
             context_before="Receipt for one ", context_after=" laptop.")
    assert COURSE_CODE.search("XPS 13") is not None
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert [r["reason"] for r in unresolved_for_file(
        p6_conn, file_id, content_hash)] == ["context_check_failed"]


def test_rules_do_not_read_another_versions_observations(p6_conn, tmp_path):
    # The abstention and the fact are both per file VERSION (§3.4, §8.2), so the read
    # filters on content hash and a prior version's evidence cannot resolve this one.
    file_id, content_hash = _record(p6_conn, tmp_path, name="v1.pdf", body=b"one")
    _observe(p6_conn, run_id="r-old", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="Syllabus — ")
    other_hash = "f" * 64
    _run(p6_conn, run_id="r-other", file_id=file_id, content_hash=other_hash)
    record_observation(p6_conn, Observation(
        file_id=file_id, content_hash=other_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value="ECON 1001", location=Location("heading", (Segment("page", 1),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id="r-other", context_before="Syllabus — "))
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(_course_rule(),))
    values = {r["canonical_value"]
              for r in facts_for_file(p6_conn, file_id, content_hash)}
    assert values == {"BUSIB 4300"}


def test_the_outcome_does_not_depend_on_p4s_insertion_order(p6_conn, tmp_path):
    # `observations_for_file` orders by rowid. Two observations, written in either
    # order, must produce the same two facts.
    def resolve(order):
        file_id, content_hash = _record(
            p6_conn, tmp_path, name=f"order-{'-'.join(order)}.pdf", body=b"x")
        for index, raw in enumerate(order):
            _observe(p6_conn, run_id=f"o{index}-{raw}", file_id=file_id,
                     content_hash=content_hash, raw=raw,
                     context_before="Syllabus — ")
        apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                    rules=(_course_rule(),))
        return sorted(r["canonical_value"]
                      for r in facts_for_file(p6_conn, file_id, content_hash))

    assert resolve(("BUSIB 4300", "ECON 1001")) == \
        resolve(("ECON 1001", "BUSIB 4300")) == ["BUSIB 4300", "ECON 1001"]


def test_several_rules_over_one_observation_each_write_their_own_row(
        p6_conn, tmp_path):
    # One rule fills, one refuses. The two outcomes are independent and neither
    # suppresses the other.
    file_id, content_hash = _record(p6_conn, tmp_path, name="two.pdf", body=b"two")
    _observe(p6_conn, run_id="r-two", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="Syllabus — ")
    venue_rule = Rule(pattern=COURSE_CODE,
                      required_context_terms=("proceedings", "conference"),
                      field_key="venue")
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(_course_rule(), venue_rule))
    assert [r["field_key"] for r in facts_for_file(
        p6_conn, file_id, content_hash)] == ["subject"]
    assert [(r["field_key"], r["reason"]) for r in unresolved_for_file(
        p6_conn, file_id, content_hash)] == [("venue", "context_check_failed")]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_rules.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'facts.rules'`
(if it instead fails with `No module named 'facts.facets'`, Task 11 has not been executed yet — see
the ordering edge above)

- [ ] **Step 3: Write the implementation**

```python
# src/facts/rules.py
"""§3.5 rule-validated facts: a pattern match PLUS a strict context check.

§3.5, verbatim and load-bearing: *"Rules create validated facts when a candidate
passes strict context checks. For example, BUSIB 4300 becomes a course fact only when
the engine finds a course-code pattern together with academic context such as
"syllabus," "lecture," "credits," "instructor," or "semester.""*

Five terms are stated literally and they are the only context vocabulary this module
authors. Every other domain's terms arrive on the `Rule`, because the SPEC defers
them: *"Rule context-term lists beyond the five literal academic terms | §3.5 | Only
"syllabus", "lecture", "credits", "instructor", "semester" are stated. Every other
domain's context vocabulary is unauthored."* There is no sixth term here and adding
one is a design change, not an implementation detail.

**The check is case-insensitive (N-6).** §3.5 writes its five terms in lowercase and
states no matching rule, so P6 states one. P4's fixture 1 carries `context_before`
exactly `"Syllabus - "` with a capital S, and B8(a)'s whole purpose was to make the
walking skeleton's one fact resolvable; a case-sensitive reading refuses that fixture
and the skeleton produces no fact at all.

**Case-insensitivity does not relax the word boundary.** The matcher is
`facts.facets.word_boundary_match`, the same one §3.7's facet values go through, so
`semester` still cannot match inside a longer word. One rule, one implementation.

**A truncated context is not a clean refusal.** §8.6 forbids silent truncation, so a
check that fails on a record with `context_truncated = true` writes
`reason = context_truncated` and never `context_check_failed`: the term may have been
cut off, and reporting a considered refusal would be a claim this module cannot make.
"""
from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from evidence_shape.canonical import canonical_json
from evidence_shape.vocabulary import ANALYSIS_TIERS

from facts.cache import fact_cache_key
from facts.evidence import (
    analysis_tier_for_observation, cite, context_pair, observations_for_version,
)
from facts.facets import word_boundary_match
from facts.file_facts import FACT_ORIGINS, write_fact, RULE
from facts.states import STATES, VALIDATED
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: §3.5's five academic context terms, quoted from the design and complete. This is
#: the ONLY context vocabulary `facts` authors; everything else is injected on a
#: `Rule`. A sixth term is a design change.
ACADEMIC_CONTEXT_TERMS: tuple[str, str, str, str, str] = (
    "syllabus", "lecture", "credits", "instructor", "semester")

#: Task 1 owns the spelling. Never an index into STATES.
_VALIDATED = VALIDATED


class MalformedRule(ValueError):
    """A rule with no pattern, no context term, or no field. §3.5 requires all three."""


@dataclass(frozen=True, slots=True)
class Rule:
    """One injected §3.5 rule: a pattern, the context it demands, and the field it fills.

    Every one of the three is caller-supplied. `facts.rules` authors no course-code
    regex (§3.10's catalogue beyond the three named date patterns is Deferred and a
    course-code pattern is not among them), and it authors no field key -- D6 fixes
    the academic key as `subject`, and a module that spelled it would be a second home
    for `fields`.
    """

    pattern: re.Pattern[str]
    required_context_terms: tuple[str, ...]
    field_key: str

    def __post_init__(self) -> None:
        if not isinstance(self.pattern, re.Pattern):
            raise MalformedRule("a rule matches a compiled pattern, never a string: "
                                "§3.10 requires explicit regular expressions")
        if not self.required_context_terms:
            raise MalformedRule(
                f"rule for {self.field_key!r} demands no context term; §3.5's whole "
                "point is that a pattern match alone is not a fact")
        if not self.field_key:
            raise MalformedRule("a rule names the field it fills")


def context_check(before: str, after: str, terms: Iterable[str]) -> bool:
    """True when any required term appears in either half of §2.8's context pair.

    The two halves are read together and never concatenated (M5): P4 split them so
    §8.4 can redact a value without dropping its context, and joining them here would
    forge an adjacency that the document does not contain.
    """
    haystacks = (before or "", after or "")
    return any(word_boundary_match(term, haystack)
               for term in terms for haystack in haystacks)


def _pass_cache_key(conn: sqlite3.Connection, *, file_id: str,
                    content_hash: str) -> str:
    """§3.4's key for one deterministic pass over one file version.

    Written out here rather than imported from a producer sibling: the SPEC requires
    an `unresolved` row to carry the "same composition as `file_facts` (§3.4), so an
    abstention is invalidated by the same events that invalidate a fact", and the
    reconciliation of several extractor versions into one key belongs to `facts.cache`
    (Task 6), which does not own it yet. See the plan's contract ambiguities.
    """
    observations = observations_for_version(conn, file_id, content_hash)
    pairs = sorted({(o.extractor_name, o.extractor_version) for o in observations})
    tiers = {analysis_tier_for_observation(conn, o) for o in observations}
    present = [tier for tier in ANALYSIS_TIERS if tier in tiers]
    if not present:
        raise ValueError(
            f"no extraction run for {content_hash!r}: §3.4's key has no analysis tier")
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=present[-1], model_identifier=None, prompt_fingerprint=None)


def apply_rules(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                rules: Sequence[Rule]) -> tuple[str, ...]:
    """Run every rule over every observation of one file version.

    Three outcomes and they are not interchangeable:

    * the pattern does not match -- nothing at all. A rule that does not apply is not
      a refusal, and writing one would fill `unresolved` with every field every rule
      could theoretically have produced;
    * the pattern matches and the context check passes -- one `validated` fact citing
      that observation's key (M14);
    * the pattern matches and the context check fails -- one `unresolved` row, whose
      reason is `context_truncated` when P4 flagged the context as cut and
      `context_check_failed` when it did not.
    """
    written: list[str] = []
    observations = sorted(observations_for_version(conn, file_id, content_hash),
                          key=lambda o: o.observation_key)
    for observation in observations:
        before, after, truncated = context_pair(observation)
        for rule in rules:
            match = rule.pattern.search(observation.raw_value)
            if match is None:
                continue
            if not context_check(before, after, rule.required_context_terms):
                write_unresolved(
                    conn, file_id=file_id, content_hash=content_hash,
                    field_key=rule.field_key,
                    reason="context_truncated" if truncated else "context_check_failed",
                    attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                    evidence_refs=(cite(observation),),
                    cache_key=_pass_cache_key(conn, file_id=file_id,
                                              content_hash=content_hash))
                continue
            value_id = ensure_value(conn, field_key=rule.field_key,
                                    canonical_value=match.group(0),
                                    first_evidence_ref=cite(observation),
                                    origin=VALUE_ORIGINS[0])
            written.append(write_fact(
                conn, file_id=file_id, content_hash=content_hash,
                field_key=rule.field_key, value_id=value_id,
                reliability_state=_VALIDATED, origin=RULE,
                evidence_refs=(cite(observation),),
                cache_key=_pass_cache_key(conn, file_id=file_id,
                                          content_hash=content_hash),
                active=True))
    return tuple(written)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_rules.py -v`
Expected: PASS — 20 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/rules.py tests/p6/test_p6_rules.py
git commit -m "feat(P6): §3.5 rule-validated facts — a pattern match plus a strict context check"
```

---

---

### Task 11: §3.7 facet ranking — word boundary, positional weight, score and margin

**Files:**
- Create: `src/facts/facets.py`
- Test: `tests/p6/test_p6_facets.py`

**Interfaces:**
- Consumes: `facts.evidence` — `observations_for_version`, `analysis_tier_for_observation`;
  `facts.file_facts` — `write_fact`, `FACT_ORIGINS`; `facts.unresolved` — `write_unresolved`,
  `ATTEMPTED_PRODUCERS`; `facts.values` — `ensure_value`, `VALUE_ORIGINS`; `facts.states.STATES`;
  `facts.cache.fact_cache_key`; `evidence_shape.canonical.canonical_json`;
  `evidence_shape.vocabulary` — `ANALYSIS_TIERS`, `ZONES`.
- Produces: `MissingWeight`, `Candidate(value, score, evidence_refs, zone=None, signal_tier=None)`,
  `word_boundary_match(needle, haystack) -> bool`,
  `rank(candidates, *, zone_weight, tier_weight) -> tuple[Candidate, ...]`,
  `fill_or_abstain(conn, *, file_id, content_hash, field_key, candidates, minimum_score,
  minimum_margin) -> str | None` — every threshold and weight a required keyword with no default.

**Done-means:** 7, 9.

**§3.7 in its own words, and this module is all four clauses of it:** *"It should use word-boundary
matching rather than substring matching. Without this rule, names such as MIT can be found inside
"submit," and UNC can be found inside "uncertainty," producing polished but completely false filing
paths. It should use positional weighting because a value in a filename or document title carries
more meaning than the same value in a footer or a late body-page reference. It should rank candidate
matches instead of accepting the first match, and it should require both a minimum score and a
minimum margin over the second-best candidate before it fills a facet."*

**Why the matcher is hand-rolled rather than `\b`.** `\b` is defined against a word character on
*both* sides, which is wrong for a needle whose own first or last character is not one — `C++`,
`PVA/RDP`, `AY 2024-25` are all real facet values and all would be mis-bounded. And the needle is
`re.escape`d before it is searched for: a gazetteer entry is **data**, and a catalogue row compiled
as syntax would let `a+` match `aaaa` and one row match the whole corpus. The boundary is therefore
tested per edge: a word character at the edge of the needle demands a non-word character (or the end
of the string) beside it, and a non-word character at the edge demands nothing.

**Case is folded, and A01 and A02 still fail.** N-6 requires the §3.5 context check to be
case-insensitive and Task 10 shares this matcher, so folding case here is what keeps the rule in one
place. It costs nothing: `mit` inside `submit` and `unc` inside `uncertainty` are both refused by
the boundary, not by case, which is the assertion `test_case_folding_does_not_relax_the_boundary`
makes explicit so a later reader cannot mistake it for luck.

**`Candidate` carries two descriptors beyond the published three.** The skeleton fixes
`Candidate(value, score, evidence_refs)` and `rank(candidates, *, zone_weight, tier_weight)` — but a
weight map has nothing to weight unless the contribution says which zone and which signal tier it
came from. So `zone` and `signal_tier` follow the three, defaulted to `None`, carrying P4's
`location.zone` and P4's integer `signal_tier` unchanged. `rank` clears both on what it returns: a
ranked candidate aggregates several positions and a single zone on it would be a claim about where
it came from that is not true. This is an addition to the skeleton's shape and is listed under
*Contract ambiguities*.

**A null `signal_tier` is not a band.** P4's conformance rule 11 ties a non-null `signal_tier` to
`source_type == "image"`, so most observations have none. `rank` applies no tier factor at all in
that case — not a default weight. §2.6 is the reason and it is unconditional: *"the system must not
mistake the absence of EXIF for proof that an image is a screenshot."* A missing signal contributes
nothing to either candidate; it does not contribute a middling amount.

**Every weight and threshold is required, and an unweighted zone raises.** The SPEC defers
*"Minimum score and minimum margin values"*, *"Positional weight per document zone"* and
*"Signal-tier weights for §2.6's three bands"*. `MissingWeight` is what a zone with no injected
weight produces — a fallback weight would answer a Deferred question silently, which is the failure
mode this plan exists to avoid.

**The total order is this module's, and it is imposed twice.** `evidence_shape.store` reads in
`rowid` order, which is insertion order — verified by execution — and insertion order is a property
of one database, not of the corpus. `rank` sorts by (weighted score descending, smallest cited
observation key ascending, value ascending) and `fill_or_abstain` applies the same key again to its
own input, so a caller that hands the candidates over reversed gets the same fact. Without it a tie
is decided by whichever run was written first and §8.5's replay reports a regression when nothing
changed.

**Three refusals, not one.** `no_candidate_evidence` when nothing was offered,
`below_score_threshold` when the winner is under the floor, `below_margin` when the winner is too
close to the runner-up. §8.5 asks under Fact quality *"Did it abstain when evidence was absent?"* and
a single merged reason cannot answer it — absent evidence and contested evidence are different
events with different fixes.

**The state is `validated` and the signature has no room to say otherwise.** §3.13: a `validated`
fact *"was found by a deterministic rule and passed contextual checks"*, and clearing a minimum score
and a minimum margin over ranked candidates is that check. Nothing here writes `direct` — no explicit
slot states a ranked facet — and nothing here writes `possible`.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_facets.py
"""§3.7 -- Done-means 7 and 9, adversarial cases A01 and A02."""
import itertools
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import ZONES

from facts.facets import (
    Candidate, MissingWeight, fill_or_abstain, rank, word_boundary_match,
)
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-22T00:00:00Z"

#: §3.7's weights are Deferred -- "Positional weight per document zone | §3.7, §2.2 |
#: Zones arrive from P4's `location`; the weights are manual." These are the test's
#: own, injected at every call, and they exist nowhere in `src/facts`.
ZONE_WEIGHT = {"filename": 3.0, "title": 3.0, "heading": 2.0, "body": 1.0,
               "header_footer": 0.25, "metadata": 1.0, "path": 1.0, "table": 1.0,
               "notes": 1.0, "link": 1.0, "annotation": 1.0, "reference_list": 0.5,
               "manifest": 1.0, "ocr": 1.0, "transcript": 1.0}
TIER_WEIGHT = {1: 4.0, 2: 2.0, 3: 1.0}


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="text/plain",
        detected_format="txt", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, zone, occurrence_count=1,
             signal_tier=None, source_type="text_document", analysis_tier="native"):
    if conn.execute("SELECT 1 FROM extraction_runs WHERE run_id = ?",
                    (run_id,)).fetchone() is None:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="text.plain", extractor_version="1.0.0",
            source_type=source_type, analysis_tier=analysis_tier, config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="text.plain",
        extractor_version="1.0.0", source_type=source_type, raw_value=raw,
        location=Location(zone, (Segment("page", 1),)),
        occurrence_count=occurrence_count, observed_at=CLOCK,
        reliability="possible", run_id=run_id, signal_tier=signal_tier)
    record_observation(conn, observation)
    return observation


def _candidate(observation, value, score=1.0):
    return Candidate(value=value, score=score,
                     evidence_refs=(observation.observation_key,),
                     zone=observation.location.zone,
                     signal_tier=observation.signal_tier)


# --- the word-boundary rule, which is the whole of A01 and A02 -----------------

def test_mit_is_not_found_inside_submit():
    # §3.7, verbatim: "names such as MIT can be found inside "submit,"" -- and A01
    # carries that exact sentence as `Please submit the completed form.`
    assert word_boundary_match("MIT", "Please submit the completed form.") is False


def test_unc_is_not_found_inside_uncertainty():
    # §3.7's second named case; A02's text unit verbatim.
    assert word_boundary_match(
        "UNC", "Measurement uncertainty dominates the result.") is False


def test_the_same_needles_do_match_when_they_stand_alone():
    # The refusal has to be a boundary rule and not a blanket "never match", or the
    # facet could never be filled at all.
    assert word_boundary_match("MIT", "Accepted to MIT this spring.") is True
    assert word_boundary_match("UNC", "UNC Chapel Hill, 2024") is True
    assert word_boundary_match("MIT", "MIT") is True


def test_case_folding_does_not_relax_the_boundary():
    # N-6 makes the §3.5 context check case-insensitive and it shares this matcher.
    # If folding case turned the rule into a substring rule, A01 and A02 would both
    # start passing, so this is the assertion that keeps N-6 safe.
    for haystack in ("Please SUBMIT the form.", "please submit the form.",
                     "Submit the form."):
        assert word_boundary_match("mit", haystack) is False
    assert word_boundary_match("syllabus", "Syllabus — ") is True
    assert word_boundary_match("SYLLABUS", "syllabus — ") is True


def test_a_needle_whose_edges_are_not_word_characters_still_bounds_correctly():
    # `\b` is defined against a word character on both sides and would be wrong here;
    # the matcher tests the boundary per edge instead.
    assert word_boundary_match("PVA/RDP", "the PVA/RDP abstract") is True
    assert word_boundary_match("AY 2024-25", "Calendar AY 2024-25 published") is True
    assert word_boundary_match("C++", "written in C++ and Rust") is True


def test_the_needle_is_never_compiled_as_a_pattern():
    # A gazetteer entry is data, not syntax. `.` must match a full stop and nothing
    # else, or one catalogue row would match every file in the corpus.
    assert word_boundary_match("M.I.T", "MXIXT") is False
    assert word_boundary_match("a+", "aaaa") is False


def test_an_empty_needle_or_haystack_matches_nothing():
    assert word_boundary_match("", "anything") is False
    assert word_boundary_match("MIT", "") is False


# --- ranking: never first-match, and never P4's read order --------------------

def test_ranking_is_over_all_candidates_and_never_the_first_match(p6_conn, tmp_path):
    # §3.7: "It should rank candidate matches instead of accepting the first match."
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Duke", zone="header_footer")
    title = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="title")
    ranked = rank([_candidate(footer, "Duke"), _candidate(title, "Columbia")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    assert [c.value for c in ranked] == ["Columbia", "Duke"]


def test_a_title_outranks_a_footer_and_a_late_body_page(p6_conn, tmp_path):
    # §3.7: "a value in a filename or document title carries more meaning than the
    # same value in a footer or a late body-page reference."
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    in_title = _observe(p6_conn, run_id="r1", file_id=file_id,
                        content_hash=content_hash, raw="Columbia", zone="title")
    in_footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                         content_hash=content_hash, raw="Columbia",
                         zone="header_footer")
    weighted = rank([_candidate(in_footer, "Columbia")], zone_weight=ZONE_WEIGHT,
                    tier_weight=TIER_WEIGHT)[0].score
    stronger = rank([_candidate(in_title, "Columbia")], zone_weight=ZONE_WEIGHT,
                    tier_weight=TIER_WEIGHT)[0].score
    assert stronger > weighted


def test_contributions_for_one_value_are_summed_and_their_refs_merged(
        p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    first = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="body")
    second = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Columbia College",
                      zone="heading")
    ranked = rank([_candidate(first, "Columbia"), _candidate(second, "Columbia")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    assert len(ranked) == 1
    assert ranked[0].score == pytest.approx(3.0)
    assert ranked[0].evidence_refs == tuple(sorted(
        (first.observation_key, second.observation_key)))


def test_the_result_does_not_depend_on_p4s_read_order(p6_conn, tmp_path):
    # `observations_for_file` orders by rowid, which is insertion order and not a
    # property of the corpus. Every permutation must produce the same ranking or
    # §8.5's replay compares a run against itself and reports a regression.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    made = [
        _candidate(_observe(p6_conn, run_id="r1", file_id=file_id,
                            content_hash=content_hash, raw=raw, zone=zone), value)
        for raw, zone, value in (("Columbia", "title", "Columbia"),
                                 ("Duke", "body", "Duke"),
                                 ("Yale", "header_footer", "Yale"),
                                 ("Duke again", "heading", "Duke"))]
    expected = rank(made, zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    for permutation in itertools.permutations(made):
        assert rank(permutation, zone_weight=ZONE_WEIGHT,
                    tier_weight=TIER_WEIGHT) == expected


def test_a_tie_is_broken_by_the_observation_key_and_not_by_insertion_order(
        p6_conn, tmp_path):
    # The case that actually bites: two candidates with identical weighted scores.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    left = _candidate(_observe(p6_conn, run_id="r1", file_id=file_id,
                               content_hash=content_hash, raw="Duke", zone="body"),
                      "Duke")
    right = _candidate(_observe(p6_conn, run_id="r1", file_id=file_id,
                                content_hash=content_hash, raw="Yale", zone="body"),
                       "Yale")
    forward = rank([left, right], zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    backward = rank([right, left], zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    assert forward == backward
    assert forward[0].score == forward[1].score
    assert forward[0].evidence_refs[0] < forward[1].evidence_refs[0]


def test_a_signal_tier_weights_the_contribution_and_absence_of_one_does_not(
        p6_conn, tmp_path):
    # §2.6, and M2: P6 consumes P4's integer tier and never re-derives it. A null
    # tier is not a band -- "the system must not mistake the absence of EXIF for
    # proof that an image is a screenshot."
    file_id, content_hash = _record(p6_conn, tmp_path, name="photo.jpg", body=b"px")
    tier_one = _observe(p6_conn, run_id="r1", file_id=file_id,
                        content_hash=content_hash, raw="Canon EOS R6",
                        zone="metadata", signal_tier=1, source_type="image")
    untiered = _observe(p6_conn, run_id="r1", file_id=file_id,
                        content_hash=content_hash, raw="Canon EOS R5",
                        zone="metadata", source_type="image")
    assert rank([_candidate(tier_one, "photograph")], zone_weight=ZONE_WEIGHT,
                tier_weight=TIER_WEIGHT)[0].score == pytest.approx(4.0)
    assert rank([_candidate(untiered, "photograph")], zone_weight=ZONE_WEIGHT,
                tier_weight=TIER_WEIGHT)[0].score == pytest.approx(1.0)


def test_an_unweighted_zone_or_tier_raises_rather_than_defaulting(p6_conn, tmp_path):
    # No default weight exists anywhere: §3.7's numbers are Deferred and a fallback
    # would answer them silently.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    observation = _observe(p6_conn, run_id="r1", file_id=file_id,
                           content_hash=content_hash, raw="Columbia", zone="title")
    with pytest.raises(MissingWeight):
        rank([_candidate(observation, "Columbia")], zone_weight={},
             tier_weight=TIER_WEIGHT)
    with pytest.raises(MissingWeight):
        rank([Candidate(value="Columbia", score=1.0, evidence_refs=("sha256:a",))],
             zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    tiered = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Canon", zone="metadata",
                      signal_tier=2, source_type="image")
    with pytest.raises(MissingWeight):
        rank([_candidate(tiered, "photograph")], zone_weight=ZONE_WEIGHT,
             tier_weight={})


def test_every_p4_zone_is_weightable_because_the_map_is_the_callers(p6_conn):
    # The map is over P4's fifteen zones; P6 states which zones exist nowhere.
    assert set(ZONE_WEIGHT) == set(ZONES)


# --- the two thresholds, and the three different refusals ---------------------

def test_a_clear_winner_fills_the_facet_as_validated(p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    title = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="title")
    footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Duke", zone="header_footer")
    ranked = rank([_candidate(title, "Columbia"), _candidate(footer, "Duke")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    fact_id = fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                              field_key="school", candidates=ranked,
                              minimum_score=1.0, minimum_margin=1.0)
    assert fact_id is not None
    rows = [r for r in facts_for_file(p6_conn, file_id, content_hash)
            if r["field_key"] == "school"]
    assert [(r["canonical_value"], r["reliability_state"]) for r in rows] == \
        [("Columbia", "validated")]
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_two_candidates_within_the_margin_fill_nothing(p6_conn, tmp_path):
    # Done-means 9, and §3.7's "minimum margin over the second-best candidate".
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    left = _observe(p6_conn, run_id="r1", file_id=file_id,
                    content_hash=content_hash, raw="Columbia", zone="heading")
    right = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Duke", zone="heading")
    ranked = rank([_candidate(left, "Columbia"), _candidate(right, "Duke")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                           field_key="school", candidates=ranked,
                           minimum_score=1.0, minimum_margin=1.0) is None
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="school")
    assert [r["reason"] for r in rows] == ["below_margin"]
    assert json.loads(rows[0]["evidence_refs"]) == sorted(
        (left.observation_key, right.observation_key))


def test_failing_the_minimum_score_is_a_different_refusal_from_the_margin(
        p6_conn, tmp_path):
    # Two thresholds, two reasons. §8.5 asks "Did it abstain when evidence was
    # absent?" and one merged reason cannot answer it.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Columbia",
                      zone="header_footer")
    ranked = rank([_candidate(footer, "Columbia")], zone_weight=ZONE_WEIGHT,
                  tier_weight=TIER_WEIGHT)
    assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                           field_key="school", candidates=ranked,
                           minimum_score=1.0, minimum_margin=0.1) is None
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="school")
    assert [r["reason"] for r in rows] == ["below_score_threshold"]


def test_no_candidate_at_all_is_a_third_refusal(p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    _observe(p6_conn, run_id="r1", file_id=file_id, content_hash=content_hash,
             raw="nothing relevant", zone="body")
    assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                           field_key="school", candidates=(),
                           minimum_score=1.0, minimum_margin=1.0) is None
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="school")
    assert [r["reason"] for r in rows] == ["no_candidate_evidence"]
    assert json.loads(rows[0]["evidence_refs"]) == []


def test_a_lone_candidate_clears_the_margin_because_there_is_no_second_best(
        p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    title = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="title")
    ranked = rank([_candidate(title, "Columbia")], zone_weight=ZONE_WEIGHT,
                  tier_weight=TIER_WEIGHT)
    assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                           field_key="school", candidates=ranked,
                           minimum_score=1.0, minimum_margin=1.0) is not None


def test_fill_or_abstain_re_imposes_the_order_on_its_own_input(p6_conn, tmp_path):
    # A caller that hands the candidates over in the wrong order must not change the
    # outcome: `rank` orders, and `fill_or_abstain` orders again before it looks at
    # the first element.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    title = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="title")
    footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Duke", zone="header_footer")
    ranked = rank([_candidate(title, "Columbia"), _candidate(footer, "Duke")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key="school", candidates=tuple(reversed(ranked)),
                    minimum_score=1.0, minimum_margin=1.0)
    rows = [r for r in facts_for_file(p6_conn, file_id, content_hash)
            if r["field_key"] == "school"]
    assert [r["canonical_value"] for r in rows] == ["Columbia"]


def test_a01_and_a02_fill_nothing_end_to_end(p6_conn, tmp_path):
    # The two adversarial cases as built: `expected_outcome_kind: "abstained"`,
    # `forbidden_value: {"field": "school", "value": "MIT"}` / `"UNC"`. The gazetteer
    # is the test's, because §3.7's gazetteer contents are Deferred.
    gazetteer = ("MIT", "UNC", "Columbia")
    for name, text, forbidden in (("A01", "Please submit the completed form.", "MIT"),
                                  ("A02", "Measurement uncertainty dominates the "
                                          "result.", "UNC")):
        file_id, content_hash = _record(p6_conn, tmp_path, name=f"{name}.txt",
                                        body=text.encode())
        observation = _observe(p6_conn, run_id=f"{name}-run", file_id=file_id,
                               content_hash=content_hash, raw=text, zone="body")
        candidates = [_candidate(observation, entry) for entry in gazetteer
                      if word_boundary_match(entry, observation.raw_value)]
        assert candidates == []
        assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                               field_key="school",
                               candidates=rank(candidates, zone_weight=ZONE_WEIGHT,
                                               tier_weight=TIER_WEIGHT),
                               minimum_score=1.0, minimum_margin=1.0) is None
        assert facts_for_file(p6_conn, file_id, content_hash) == []
        rows = unresolved_for_file(p6_conn, file_id, content_hash,
                                   field_key="school")
        assert [r["reason"] for r in rows] == ["no_candidate_evidence"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_facets.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'facts.facets'`

- [ ] **Step 3: Write the implementation**

```python
# src/facts/facets.py
"""§3.7 conservative facet extraction: word boundary, positional weight, score, margin.

§3.7, verbatim and in its own order: *"It should use word-boundary matching rather
than substring matching. Without this rule, names such as MIT can be found inside
"submit," and UNC can be found inside "uncertainty," producing polished but
completely false filing paths. It should use positional weighting because a value in
a filename or document title carries more meaning than the same value in a footer or
a late body-page reference. It should rank candidate matches instead of accepting the
first match, and it should require both a minimum score and a minimum margin over the
second-best candidate before it fills a facet."*

Four obligations, and this module is all four:

1. word-boundary matching, never substring;
2. positional weighting off P4's `location.zone`;
3. ranked candidates, never first-match;
4. a minimum score AND a minimum margin, both cleared, before a facet is filled.

**Every weight and every threshold is a required keyword with no default.** §3.7's
numbers are Deferred -- the SPEC's own table lists "Minimum score and minimum margin
values", "Positional weight per document zone" and "Signal-tier weights for §2.6's
three bands" as manual work. A default here would answer them.

**The total order is this module's, not P4's.** `observations_for_file` orders by
rowid, which is insertion order and is not a property of the corpus. `rank` therefore
sorts by (weighted score descending, smallest cited observation key ascending, value
ascending) before anything looks at the first element, and `fill_or_abstain` applies
the same order again to its own input. Without that, a tie is decided by whichever
run happened to be written first and §8.5's replay reports a regression when nothing
changed.
"""
from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from evidence_shape.canonical import canonical_json
from evidence_shape.vocabulary import ANALYSIS_TIERS

from facts.cache import fact_cache_key
from facts.evidence import (
    analysis_tier_for_observation, observations_for_version,
)
from facts.file_facts import FACT_ORIGINS, write_fact, RULE
from facts.states import STATES, VALIDATED
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value


#: §3.13's third state. Rule 2: the six literals are P4's and P6 re-spells none of
#: them, so every state in this module is addressed by its index into P4's tuple.
_VALIDATED = VALIDATED


class MissingWeight(KeyError):
    """A zone or signal tier with no injected weight. P6 invents no number."""


@dataclass(frozen=True, slots=True)
class Candidate:
    """One candidate value for one field.

    `value`, `score` and `evidence_refs` are the published three. `zone` and
    `signal_tier` are the two P4 descriptors `rank` weights by; they are present on a
    contribution (one candidate from one observation) and cleared on the aggregate
    `rank` returns, because a ranked candidate spans several positions and a single
    zone would be a lie about where it came from.
    """

    value: str
    score: float
    evidence_refs: tuple[str, ...]
    zone: str | None = None
    signal_tier: int | None = None


def _is_word_character(character: str) -> bool:
    return character.isalnum() or character == "_"


def word_boundary_match(needle: str, haystack: str) -> bool:
    """True when `needle` occurs in `haystack` bounded by non-word characters.

    §3.7's own two cases are the specification: `MIT` must not match inside "submit"
    and `UNC` must not match inside "uncertainty". Both are decided by the boundary
    and not by case, which is why folding case (N-6, required for the §3.5 context
    check that shares this matcher) does not weaken either refusal.

    `re.escape` is applied to the needle: facet values contain `/`, `-`, `+` and `.`
    (`PVA/RDP`, `AY 2024-25`, `C++`), and a needle compiled as a pattern would make
    the value catalogue an injection surface. `\\b` is not used either -- it is
    defined against a word character on both sides, which is wrong for a needle whose
    own first or last character is not one.
    """
    if not needle or not haystack:
        return False
    for match in re.finditer(re.escape(needle), haystack, flags=re.IGNORECASE):
        start, end = match.start(), match.end()
        if _is_word_character(haystack[start]) and start > 0 \
                and _is_word_character(haystack[start - 1]):
            continue
        if _is_word_character(haystack[end - 1]) and end < len(haystack) \
                and _is_word_character(haystack[end]):
            continue
        return True
    return False


def _weight_of(candidate: Candidate, *, zone_weight: Mapping[str, float],
               tier_weight: Mapping[int, float]) -> float:
    if candidate.zone is None:
        raise MissingWeight(
            "a contribution carries P4's location.zone; §3.7's positional weighting "
            "has nothing to weight without it")
    try:
        weight = zone_weight[candidate.zone]
    except KeyError as exc:
        raise MissingWeight(f"no injected weight for zone {candidate.zone!r}") from exc
    if candidate.signal_tier is None:
        # §2.6 is image-scoped (P4 conformance rule 11 ties a non-null signal_tier to
        # source_type == "image"). No tier means the hierarchy does not apply, not
        # that some default band does -- absence is never evidence (§2.6).
        return candidate.score * weight
    try:
        return candidate.score * weight * tier_weight[candidate.signal_tier]
    except KeyError as exc:
        raise MissingWeight(
            f"no injected weight for signal tier {candidate.signal_tier!r}") from exc


def _order(candidate: Candidate) -> tuple[float, str, str]:
    refs = sorted(candidate.evidence_refs)
    return (-candidate.score, refs[0] if refs else "", candidate.value)


def rank(candidates: Iterable[Candidate], *, zone_weight: Mapping[str, float],
         tier_weight: Mapping[int, float]) -> tuple[Candidate, ...]:
    """Aggregate per-observation contributions into weighted, totally ordered candidates.

    Contributions for the same value are summed, so a value stated in a filename and
    again in a heading outranks one stated once in a footer -- which is §3.7's
    positional weighting, expressed as an injected map over P4's fifteen zones rather
    than as a number this module chose.
    """
    weighted: dict[str, float] = {}
    refs: dict[str, set[str]] = {}
    for candidate in candidates:
        score = _weight_of(candidate, zone_weight=zone_weight, tier_weight=tier_weight)
        weighted[candidate.value] = weighted.get(candidate.value, 0.0) + score
        refs.setdefault(candidate.value, set()).update(candidate.evidence_refs)
    aggregated = tuple(
        Candidate(value=value, score=weighted[value],
                  evidence_refs=tuple(sorted(refs[value])))
        for value in weighted)
    return tuple(sorted(aggregated, key=_order))


def _pass_cache_key(conn: sqlite3.Connection, *, file_id: str,
                    content_hash: str) -> str:
    """§3.4's key for one deterministic pass over one file version.

    The SPEC requires an `unresolved` row to carry the "same composition as
    `file_facts` (§3.4), so an abstention is invalidated by the same events that
    invalidate a fact" -- so the fill and the refusal computed by one pass share one
    key. `model_identifier` and `prompt_fingerprint` are None on every deterministic
    fact; P4's `sha256_of` is length-prefixed and injective, so None is
    distinguishable from "" in the digest.
    """
    observations = observations_for_version(conn, file_id, content_hash)
    pairs = sorted({(o.extractor_name, o.extractor_version) for o in observations})
    tiers = {analysis_tier_for_observation(conn, o) for o in observations}
    present = [tier for tier in ANALYSIS_TIERS if tier in tiers]
    if not present:
        raise ValueError(
            f"no extraction run for {content_hash!r}: §3.4's key has no analysis tier")
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=present[-1], model_identifier=None, prompt_fingerprint=None)


def fill_or_abstain(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                    field_key: str, candidates: Iterable[Candidate],
                    minimum_score: float, minimum_margin: float) -> str | None:
    """Fill the facet, or write the refusal that says why it was not filled.

    Three different refusals, never one: no candidate at all is
    `no_candidate_evidence`; a winner under the floor is `below_score_threshold`; a
    winner too close to the runner-up is `below_margin`. §8.5 asks "Did it abstain
    when evidence was absent?" and a single reason cannot answer it.

    The state is `validated`: §3.13 defines it as "found by a deterministic rule and
    passed contextual checks", and clearing a minimum score and a minimum margin over
    ranked candidates is exactly that check. Nothing here produces `direct` -- no
    explicit slot states a ranked facet -- and nothing here produces `possible`.
    """
    ordered = tuple(sorted(candidates, key=_order))
    if not ordered:
        write_unresolved(conn, file_id=file_id, content_hash=content_hash,
                         field_key=field_key, reason="no_candidate_evidence",
                         attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                         evidence_refs=(),
                         cache_key=_pass_cache_key(conn, file_id=file_id,
                                                   content_hash=content_hash))
        return None
    considered = tuple(sorted({ref for candidate in ordered
                               for ref in candidate.evidence_refs}))
    winner = ordered[0]
    if winner.score < minimum_score:
        write_unresolved(conn, file_id=file_id, content_hash=content_hash,
                         field_key=field_key, reason="below_score_threshold",
                         attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                         evidence_refs=considered,
                         cache_key=_pass_cache_key(conn, file_id=file_id,
                                                   content_hash=content_hash))
        return None
    if len(ordered) > 1 and winner.score - ordered[1].score < minimum_margin:
        write_unresolved(conn, file_id=file_id, content_hash=content_hash,
                         field_key=field_key, reason="below_margin",
                         attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                         evidence_refs=considered,
                         cache_key=_pass_cache_key(conn, file_id=file_id,
                                                   content_hash=content_hash))
        return None
    value_id = ensure_value(conn, field_key=field_key,
                            canonical_value=winner.value,
                            first_evidence_ref=winner.evidence_refs[0],
                            origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state=_VALIDATED, origin=RULE,
                      evidence_refs=winner.evidence_refs,
                      cache_key=_pass_cache_key(conn, file_id=file_id,
                                                content_hash=content_hash),
                      active=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_facets.py -v`
Expected: PASS — 22 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/facets.py tests/p6/test_p6_facets.py
git commit -m "feat(P6): §3.7 facet ranking — word boundary, positional weight, score and margin"
```

---

---

### Task 12: §3.10 dates and academic terms — explicit patterns, no fuzzy parsing

**Files:**
- Create: `src/facts/dates.py`
- Test: `tests/p6/test_p6_dates.py`

**Interfaces:**
- Consumes: `facts.evidence.cite`; `facts.facets` — `Candidate`, `fill_or_abstain` (applied by the
  caller and by the tests, not imported into the producer's own path);
  `evidence_shape.observation.Observation`.
- Produces: `SEASON_YEAR: str`, `ACADEMIC_YEAR_RANGE: str`, `NAMED_TERM_YEAR: str`,
  `REQUIRED_PATTERN_IDS: tuple[str, str, str]`, `MissingRequiredPattern`, `NoPatternIdentity`,
  `DatePattern(pattern_id, pattern)`, `DatePatterns(patterns)` — an injected frozen dataclass of
  compiled patterns with the three named academic-term patterns required;
  `DateMatch(pattern_id, raw, value, evidence_ref, zone, signal_tier, occurrence_count)`;
  `date_matches(observation, *, patterns) -> tuple[DateMatch, ...]`;
  `date_candidates(observation, *, patterns) -> tuple[Candidate, ...]`;
  `parse_exact(raw, *, pattern_id) -> str`.

**Done-means:** 10.

**§3.10, verbatim, because every clause of it is a test below:** *"Date extraction should be
deliberately narrow. The product must not use fuzzy date parsing because file names and documents
frequently contain numbers that look like years but are course identifiers, version numbers, build
numbers, ZIP codes, or other unrelated values. Date candidates should be identified with explicit
regular expressions and then parsed without fuzzy matching. Academic terms such as Spring 2025, AY
2024-25, and Michaelmas Term 2024 require dedicated patterns rather than generic parsing."*

**`capture_date` is not this task's field, and it is not `capture_year` either.** Three fields are
in play across P6 and they are three: `creation_date` is §3.11's universal filesystem/document
timestamp; **`capture_date` is the EXIF-derived fact** — §3.2: *"an EXIF field called
DateTimeOriginal is raw metadata; capture date = 2026-07-17 is the file fact derived from it"* — and
it is **Task 8's**, a `direct` fact from an explicit slot; `capture_year` is §3.11's Photos
*destination dimension*. This task owns none of them. It owns the §3.5 contrast's other half:
*"Filesystem timestamps are direct; dates recovered from text or filenames are not, and take the
§3.10 path."* Everything reached from here is a ranked candidate, never a `direct` fact.

**The three ids are authored; not one character of regex is.** The SPEC defers *"Date and
academic-term regex catalogue beyond the three named patterns"*, and which seasons, which term names
and which numeric formats count is exactly that catalogue. So `facts.dates` publishes the three
**ids** the design's three worked cases correspond to — `season_year` for `Spring 2025`,
`academic_year_range` for `AY 2024-25`, `named_term_year` for `Michaelmas Term 2024` — validates that
a `DatePatterns` carries all three, and holds no `re.Pattern` of its own. A test asserts that by
runtime introspection: `[name for name, value in vars(module).items() if isinstance(value,
re.Pattern)] == []`.

**"Dedicated patterns rather than generic parsing" is asserted by identity, not by value.** A single
permissive expression could match all three strings and would satisfy a value-only test. `DateMatch`
therefore carries `pattern_id`, the test asserts that each of the three strings is claimed by its own
id, and a second test asserts that no one pattern claims another's case. `DateMatch` is an addition
to the skeleton's `Produces:` list — `Candidate` has no room for a pattern id and Done-means 10 wants
one — and `date_candidates` is the skeleton's function, unchanged, defined as this record projected
onto §3.7's shape. Listed under *Contract ambiguities*.

**There is no route to a value that a pattern did not claim.** `parse_exact` raises
`NoPatternIdentity` on an empty pattern id and on an empty span, so the fuzzy path is not a
discouraged branch, it is an absent one. And "then parsed without fuzzy matching" is taken at its
word: `parse_exact` collapses runs of whitespace and returns the matched text. No month table, no
locale, no two-digit-year expansion — those would be per-field normalizers, which the SPEC defers
under *"Per-field normalizers and alias tables"*.

**The look-alikes are the point.** `v2024`, `build 20240117`, A03's ZIP code
(`Ship to Cambridge MA 02139 by Friday.`), A03's device model (`Receipt for one XPS 13 laptop.`) and
a bare course identifier (`BUSIB 4300`) each produce no candidate, therefore no fact, therefore one
`unresolved` row with `reason = no_candidate_evidence` — Done-means 18's requirement that the
refusal be a record. A bare `2025` produces nothing either, which is the trap §3.10 exists to close.

**A date is ranked like any other facet and gets no exemption.** Two named terms in one raw value
produce two candidates that tie, and §3.7's margin refuses both — a test asserts `below_margin`
rather than a first-match fill.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_dates.py
"""§3.10 -- Done-means 10, and A03's ZIP code and device model as date candidates."""
import json
import re
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.dates import (
    ACADEMIC_YEAR_RANGE, NAMED_TERM_YEAR, REQUIRED_PATTERN_IDS, SEASON_YEAR,
    DateMatch, DatePattern, DatePatterns, MissingRequiredPattern, NoPatternIdentity,
    date_candidates, date_matches, parse_exact,
)
from facts.facets import fill_or_abstain, rank
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-22T00:00:00Z"

#: §3.10's catalogue beyond the three named patterns is Deferred, so these three
#: expressions are the TEST's and live nowhere in `src/facts`. Each is dedicated to
#: exactly one of the design's three worked cases.
SPRING_2025 = DatePattern(
    pattern_id=SEASON_YEAR,
    pattern=re.compile(r"\b(?:Spring|Summer|Fall|Autumn|Winter) \d{4}\b"))
AY_2024_25 = DatePattern(
    pattern_id=ACADEMIC_YEAR_RANGE, pattern=re.compile(r"\bAY \d{4}-\d{2}\b"))
MICHAELMAS_TERM_2024 = DatePattern(
    pattern_id=NAMED_TERM_YEAR,
    pattern=re.compile(
        r"\b(?:Michaelmas|Hilary|Trinity|Lent|Easter) Term \d{4}\b"))
PATTERNS = DatePatterns(patterns=(SPRING_2025, AY_2024_25, MICHAELMAS_TERM_2024))

ZONE_WEIGHT = {"filename": 3.0, "title": 3.0, "heading": 2.0, "body": 1.0,
               "header_footer": 0.25, "metadata": 1.0, "path": 1.0, "table": 1.0,
               "notes": 1.0, "link": 1.0, "annotation": 1.0, "reference_list": 0.5,
               "manifest": 1.0, "ocr": 1.0, "transcript": 1.0}
TIER_WEIGHT = {1: 4.0, 2: 2.0, 3: 1.0}


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="text/plain",
        detected_format="txt", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="heading"):
    if conn.execute("SELECT 1 FROM extraction_runs WHERE run_id = ?",
                    (run_id,)).fetchone() is None:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="1.0.0",
            source_type="text_document", analysis_tier="native", config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, (Segment("page", 1),)), occurrence_count=1,
        observed_at=CLOCK, reliability="possible", run_id=run_id)
    record_observation(conn, observation)
    return observation


def _resolve(conn, tmp_path, *, name, raw, field_key="term"):
    file_id, content_hash = _record(conn, tmp_path, name=name, body=raw.encode())
    observation = _observe(conn, run_id=f"run-{name}", file_id=file_id,
                           content_hash=content_hash, raw=raw)
    candidates = date_candidates(observation, patterns=PATTERNS)
    fact_id = fill_or_abstain(
        conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
        candidates=rank(candidates, zone_weight=ZONE_WEIGHT,
                        tier_weight=TIER_WEIGHT),
        minimum_score=1.0, minimum_margin=0.5)
    return file_id, content_hash, fact_id


# --- the three named patterns are required, dedicated, and identified --------

def test_the_three_named_academic_term_patterns_are_required():
    # §3.10: "Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024
    # require dedicated patterns rather than generic parsing."
    assert REQUIRED_PATTERN_IDS == ("season_year", "academic_year_range",
                                    "named_term_year")
    for dropped in range(3):
        remaining = tuple(one for index, one in enumerate(PATTERNS.patterns)
                          if index != dropped)
        with pytest.raises(MissingRequiredPattern):
            DatePatterns(patterns=remaining)


def test_the_catalogue_beyond_the_three_is_injected_and_empty_by_default():
    # "Date and academic-term regex catalogue beyond the three named patterns |
    # §3.10 | ... The rest is manual."
    assert PATTERNS.extra_pattern_ids == ()
    extended = DatePatterns(patterns=PATTERNS.patterns + (
        DatePattern(pattern_id="iso_day", pattern=re.compile(r"\b\d{4}-\d{2}-\d{2}\b")),))
    assert extended.extra_pattern_ids == ("iso_day",)


def test_duplicate_pattern_ids_are_refused():
    with pytest.raises(ValueError):
        DatePatterns(patterns=PATTERNS.patterns + (SPRING_2025,))


@pytest.mark.parametrize("raw,expected_id", [
    ("Spring 2025", SEASON_YEAR),
    ("AY 2024-25", ACADEMIC_YEAR_RANGE),
    ("Michaelmas Term 2024", NAMED_TERM_YEAR),
])
def test_each_named_term_is_claimed_by_its_own_dedicated_pattern(raw, expected_id):
    # Done-means 10 asserts dedication "by pattern identity in the result rather than
    # by the value alone", which is what `DateMatch.pattern_id` is for.
    observation = Observation(
        file_id="f", content_hash="a" * 64, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("heading", ()), occurrence_count=1, observed_at=CLOCK,
        reliability="possible", run_id="r")
    found = date_matches(observation, patterns=PATTERNS)
    assert [one.pattern_id for one in found] == [expected_id]
    assert [one.value for one in found] == [raw]


def test_no_pattern_claims_another_patterns_case():
    # Three dedicated patterns, not one general one wearing three ids.
    for one in PATTERNS.patterns:
        claimed = [raw for raw in ("Spring 2025", "AY 2024-25",
                                   "Michaelmas Term 2024")
                   if one.pattern.search(raw)]
        assert len(claimed) == 1


# --- Done-means 10, positive half -------------------------------------------

@pytest.mark.parametrize("raw", ["Spring 2025", "AY 2024-25",
                                 "Michaelmas Term 2024"])
def test_each_named_term_produces_exactly_one_term_fact(raw, p6_conn, tmp_path):
    file_id, content_hash, fact_id = _resolve(
        p6_conn, tmp_path, name=f"{raw.replace(' ', '-')}.txt", raw=raw)
    assert fact_id is not None
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(r["field_key"], r["canonical_value"], r["reliability_state"])
            for r in rows] == [("term", raw, "validated")]
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_a_term_fact_cites_the_observation_that_carried_the_span(
        p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="syllabus.txt",
                                    body=b"Spring 2025")
    observation = _observe(p6_conn, run_id="r-cite", file_id=file_id,
                           content_hash=content_hash, raw="Spring 2025")
    fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key="term",
                    candidates=rank(date_candidates(observation, patterns=PATTERNS),
                                    zone_weight=ZONE_WEIGHT,
                                    tier_weight=TIER_WEIGHT),
                    minimum_score=1.0, minimum_margin=0.5)
    refs = json.loads(
        facts_for_file(p6_conn, file_id, content_hash)[0]["evidence_refs"])
    assert refs == [observation.observation_key]


# --- Done-means 10, negative half: §3.10's four look-alike number kinds ------

@pytest.mark.parametrize("raw,name", [
    ("v2024", "version"),
    ("build 20240117", "build"),
    ("Ship to Cambridge MA 02139 by Friday.", "zip"),
    ("Receipt for one XPS 13 laptop.", "device"),
    ("BUSIB 4300", "course_identifier"),
])
def test_a_number_that_only_looks_like_a_year_produces_no_date_fact(
        raw, name, p6_conn, tmp_path):
    # §3.10: "file names and documents frequently contain numbers that look like years
    # but are course identifiers, version numbers, build numbers, ZIP codes, or other
    # unrelated values." A03's two subjects are the ZIP and the device model.
    file_id, content_hash, fact_id = _resolve(
        p6_conn, tmp_path, name=f"{name}.txt", raw=raw)
    assert fact_id is None
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="term")
    assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


def test_a_bare_year_is_not_a_candidate_without_a_pattern_that_claims_it(
        p6_conn, tmp_path):
    # The trap §3.10 exists to close: `2025` on its own is a four-digit number, and
    # no pattern in the catalogue claims it.
    assert date_matches(
        Observation(file_id="f", content_hash="a" * 64, extractor_name="pdf.text",
                    extractor_version="1.0.0", source_type="text_document",
                    raw_value="2025", location=Location("heading", ()),
                    occurrence_count=1, observed_at=CLOCK, reliability="possible",
                    run_id="r"),
        patterns=PATTERNS) == ()


# --- no fuzzy path exists ----------------------------------------------------

def test_there_is_no_route_to_a_value_without_a_pattern_id():
    # "no bare four-digit-year regex reachable without a pattern id, and no fallback
    # that accepts a candidate a pattern rejected."
    with pytest.raises(NoPatternIdentity):
        parse_exact("Spring 2025", pattern_id="")
    with pytest.raises(NoPatternIdentity):
        parse_exact("   ", pattern_id=SEASON_YEAR)
    with pytest.raises(NoPatternIdentity):
        DatePattern(pattern_id="", pattern=re.compile(r"x"))


def test_parse_exact_reinterprets_nothing():
    # "then parsed without fuzzy matching" -- whitespace runs collapse and that is
    # the entire transformation. No month table, no locale, no century expansion.
    assert parse_exact("Spring  2025", pattern_id=SEASON_YEAR) == "Spring 2025"
    assert parse_exact("AY 2024-25", pattern_id=ACADEMIC_YEAR_RANGE) == "AY 2024-25"
    assert parse_exact("Michaelmas Term 2024",
                       pattern_id=NAMED_TERM_YEAR) == "Michaelmas Term 2024"
    assert parse_exact("Fall 25", pattern_id=SEASON_YEAR) == "Fall 25"


def test_no_fuzzy_parser_is_imported_or_reachable():
    # Runtime introspection, not a source-text search: a fuzzy parser would arrive as
    # a callable in the module namespace or as an import.
    import facts.dates as module
    names = {name.lower() for name in vars(module)}
    assert not any(marker in name for name in names
                   for marker in ("dateutil", "fuzzy", "guess", "strptime",
                                  "parse_date", "dateparser"))
    import sys
    assert "dateutil" not in sys.modules


def test_the_module_authors_no_regular_expression():
    # §3.10's catalogue is Deferred. The ids are the design's three cases; every
    # expression that recognises them is the caller's.
    import facts.dates as module
    assert [name for name, value in vars(module).items()
            if isinstance(value, re.Pattern)] == []
    assert [name for name, value in vars(module).items()
            if isinstance(value, (DatePattern, DatePatterns))] == []


def test_a_string_is_not_accepted_where_an_explicit_expression_is_required():
    with pytest.raises(ValueError):
        DatePattern(pattern_id=SEASON_YEAR, pattern=r"\bSpring \d{4}\b")


# --- several spans in one observation ----------------------------------------

def test_two_terms_in_one_raw_value_are_two_candidates_and_fill_nothing(
        p6_conn, tmp_path):
    # Two dedicated patterns each claim a span, the two candidates tie, and §3.7's
    # margin refuses -- a date is ranked like any other facet and gets no exemption.
    raw = "Spring 2025 and Michaelmas Term 2024"
    file_id, content_hash = _record(p6_conn, tmp_path, name="both.txt",
                                    body=raw.encode())
    observation = _observe(p6_conn, run_id="r-both", file_id=file_id,
                           content_hash=content_hash, raw=raw)
    candidates = date_candidates(observation, patterns=PATTERNS)
    assert sorted(c.value for c in candidates) == ["Michaelmas Term 2024",
                                                   "Spring 2025"]
    assert fill_or_abstain(
        p6_conn, file_id=file_id, content_hash=content_hash, field_key="term",
        candidates=rank(candidates, zone_weight=ZONE_WEIGHT,
                        tier_weight=TIER_WEIGHT),
        minimum_score=1.0, minimum_margin=0.5) is None
    assert [r["reason"] for r in unresolved_for_file(
        p6_conn, file_id, content_hash, field_key="term")] == ["below_margin"]


def test_a_candidate_carries_p4s_zone_so_the_ranker_can_weight_it(p6_conn, tmp_path):
    # §3.7's positional weighting applies to dates too; the producer supplies the
    # zone and never the weight.
    file_id, content_hash = _record(p6_conn, tmp_path, name="pos.txt",
                                    body=b"Spring 2025")
    observation = _observe(p6_conn, run_id="r-pos", file_id=file_id,
                           content_hash=content_hash, raw="Spring 2025",
                           zone="filename")
    candidate = date_candidates(observation, patterns=PATTERNS)[0]
    assert candidate.zone == "filename"
    assert candidate.signal_tier is None
    assert candidate.score == 1.0


def test_date_candidates_is_date_matches_projected_onto_the_facet_shape(
        p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="proj.txt",
                                    body=b"Spring 2025")
    observation = _observe(p6_conn, run_id="r-proj", file_id=file_id,
                           content_hash=content_hash, raw="Spring 2025")
    found = date_matches(observation, patterns=PATTERNS)
    candidates = date_candidates(observation, patterns=PATTERNS)
    assert len(found) == len(candidates) == 1
    assert isinstance(found[0], DateMatch)
    assert candidates[0].value == found[0].value
    assert candidates[0].evidence_refs == (found[0].evidence_ref,)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_dates.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'facts.dates'`

- [ ] **Step 3: Write the implementation**

```python
# src/facts/dates.py
"""§3.10 dates and academic terms: explicit patterns, and no fuzzy parsing anywhere.

§3.10, verbatim: *"Date extraction should be deliberately narrow. The product must not
use fuzzy date parsing because file names and documents frequently contain numbers
that look like years but are course identifiers, version numbers, build numbers, ZIP
codes, or other unrelated values. Date candidates should be identified with explicit
regular expressions and then parsed without fuzzy matching. Academic terms such as
Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather
than generic parsing."*

Three consequences, and all three are structural rather than advisory:

* **A candidate exists only where a pattern matched.** There is no scanner, no
  four-digit-year fallback and no "looks like a date" branch. `parse_exact` refuses to
  produce a value without a pattern id, so the only way to a date fact is through a
  pattern that claimed the span.
* **The three named academic terms get three dedicated patterns**, identified by id.
  `Spring 2025` is not `AY 2024-25` parsed loosely, and the result carries which
  pattern claimed it so a test can assert dedication rather than coincidence.
* **The pattern bodies are injected.** Which seasons, which term names, which
  numeric formats -- that is the SPEC's *"Date and academic-term regex catalogue
  beyond the three named patterns"*, which is Deferred. This module authors the three
  **ids** the design names and not one character of regex.

"Parsed without fuzzy matching" is taken at its word: `parse_exact` collapses runs of
whitespace and returns the matched text. Any further normalization is a per-field
normalizer, and those are Deferred too (*"Per-field normalizers and alias tables |
§2.8, §3.6"*).
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from evidence_shape.observation import Observation

from facts.evidence import cite
from facts.facets import Candidate

#: The three academic-term patterns §3.10 names, as ids. The design states
#: `Spring 2025` (a season and a year), `AY 2024-25` (an academic-year range) and
#: `Michaelmas Term 2024` (a named term and a year) and requires "dedicated patterns
#: rather than generic parsing" for each. The ids are the design's three cases; the
#: expressions that recognise them are the caller's.
SEASON_YEAR = "season_year"
ACADEMIC_YEAR_RANGE = "academic_year_range"
NAMED_TERM_YEAR = "named_term_year"
REQUIRED_PATTERN_IDS: tuple[str, str, str] = (
    SEASON_YEAR, ACADEMIC_YEAR_RANGE, NAMED_TERM_YEAR)


class MissingRequiredPattern(ValueError):
    """A `DatePatterns` without one of §3.10's three named academic-term patterns."""


class NoPatternIdentity(ValueError):
    """A parse attempted without a pattern id -- the fuzzy path, refused."""


@dataclass(frozen=True, slots=True)
class DatePattern:
    """One explicit regular expression and the id that identifies it in a result."""

    pattern_id: str
    pattern: re.Pattern[str]

    def __post_init__(self) -> None:
        if not self.pattern_id:
            raise NoPatternIdentity("a pattern is identified by a non-empty id")
        if not isinstance(self.pattern, re.Pattern):
            raise ValueError("§3.10 requires an explicit compiled regular expression")


@dataclass(frozen=True, slots=True)
class DatePatterns:
    """The injected catalogue. The three §3.10 names are required; the rest is the
    Deferred catalogue and is empty unless a caller supplies it."""

    patterns: tuple[DatePattern, ...]

    def __post_init__(self) -> None:
        ids = tuple(one.pattern_id for one in self.patterns)
        if len(set(ids)) != len(ids):
            raise ValueError(f"duplicate pattern ids: {ids}")
        missing = [name for name in REQUIRED_PATTERN_IDS if name not in ids]
        if missing:
            raise MissingRequiredPattern(
                f"§3.10 names three academic-term patterns and requires a dedicated "
                f"one for each; missing: {missing}")

    @property
    def pattern_ids(self) -> tuple[str, ...]:
        return tuple(one.pattern_id for one in self.patterns)

    @property
    def extra_pattern_ids(self) -> tuple[str, ...]:
        """Everything beyond §3.10's three -- the Deferred half, empty by default."""
        return tuple(name for name in self.pattern_ids
                     if name not in REQUIRED_PATTERN_IDS)

    def by_id(self, pattern_id: str) -> re.Pattern[str]:
        for one in self.patterns:
            if one.pattern_id == pattern_id:
                return one.pattern
        raise KeyError(pattern_id)


@dataclass(frozen=True, slots=True)
class DateMatch:
    """One pattern's claim on one span, carrying which pattern claimed it.

    Done-means 10 requires each of the three academic terms to be matched by a
    *dedicated* pattern "asserted by pattern identity in the result rather than by the
    value alone", and `Candidate` has no room for an id -- so the identity lives here
    and `date_candidates` is this record projected onto §3.7's shape.
    """

    pattern_id: str
    raw: str
    value: str
    evidence_ref: str
    zone: str
    signal_tier: int | None
    occurrence_count: int


def parse_exact(raw: str, *, pattern_id: str) -> str:
    """Return the matched text, whitespace-normalized, or refuse.

    This is the whole of "then parsed without fuzzy matching": no month table, no
    locale, no two-digit-year expansion, no reinterpretation of any kind. A caller
    with no pattern id has nothing that claimed the span, and there is no route from
    here to a value without one.
    """
    if not pattern_id:
        raise NoPatternIdentity(
            "§3.10 admits no candidate that a dedicated pattern did not claim")
    if not raw or not raw.strip():
        raise NoPatternIdentity(f"pattern {pattern_id!r} claimed an empty span")
    return " ".join(raw.split())


def date_matches(observation: Observation, *,
                 patterns: DatePatterns) -> tuple[DateMatch, ...]:
    """Every span of this observation's raw value that an explicit pattern claims."""
    found: list[DateMatch] = []
    for one in patterns.patterns:
        for match in one.pattern.finditer(observation.raw_value):
            found.append(DateMatch(
                pattern_id=one.pattern_id, raw=match.group(0),
                value=parse_exact(match.group(0), pattern_id=one.pattern_id),
                evidence_ref=cite(observation), zone=observation.location.zone,
                signal_tier=observation.signal_tier,
                occurrence_count=observation.occurrence_count))
    return tuple(sorted(found, key=lambda one: (one.pattern_id, one.value)))


def date_candidates(observation: Observation, *,
                    patterns: DatePatterns) -> tuple[Candidate, ...]:
    """§3.7 candidates for §3.10 spans, so a date is ranked like any other facet.

    The score is P4's `occurrence_count` and nothing else: §3.7's weights are applied
    by `facts.facets.rank` from an injected map, and a producer that pre-weighted its
    own candidates would be a second place those numbers live.
    """
    return tuple(
        Candidate(value=one.value, score=float(one.occurrence_count),
                  evidence_refs=(one.evidence_ref,), zone=one.zone,
                  signal_tier=one.signal_tier)
        for one in date_matches(observation, patterns=patterns))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_dates.py -v`
Expected: PASS — 25 passed (17 test functions; three are parametrized and expand to eleven)

- [ ] **Step 5: Commit**

```bash
git add src/facts/dates.py tests/p6/test_p6_dates.py
git commit -m "feat(P6): §3.10 dates and academic terms — explicit patterns, no fuzzy parsing"
```

---

---

### Task 13: §3.11 domain activation, and several domains on one file at once

**Files:**
- Create: `src/facts/domains.py`
- Test: `tests/p6/test_p6_domains.py`

**Interfaces:**
- Consumes: `facts.fields` — `DOMAIN_FIELDS`, `FIELD_SCOPES`, `fields_in_scope`;
  `facts.file_facts.facts_for_file`.
- Produces: `SCHEMA_IDS: tuple[str, ...]` (ten), `UNIVERSAL_SCOPE: str`,
  `FIELD_LESS_SCHEMA_IDS: tuple[str, ...]` (derived), `UnknownSchema`,
  `ActivationSignal(schema_id, activates)`, `ActivationSignals(signals)` — injected, no defaults;
  `active_domains(conn, *, file_id, content_hash, activation_signals) -> frozenset[str]`;
  `active_field_allowlist(conn, *, file_id, content_hash, activation_signals) -> tuple[str, ...]`;
  `schema_fields(schema_id) -> tuple[str, ...]`.

**Done-means:** 14.

**§3.11's two sentences that this module is:** *"It should then activate domain-specific schemas
only when the evidence indicates that a domain is plausible … This means target university is not a
fact that every file is expected to have. It is a field available only when the Applications domain
is plausibly active."* And the worked case: *"One file may hold facts from more than one domain
without losing information. An academic abstract submitted as part of a university application can
retain project = PVA/RDP and document type = abstract while also carrying purpose = university
application and target university = UChicago. At the pre-sorting stage, the product does not need to
decide which of those perspectives will ultimately determine its physical location. It preserves
both so the user can later choose the appropriate organization structure."*

**`active_domains` returns a set because §3.11 forbids a winner.** Nothing here ranks, nothing here
suppresses, and no field is dropped. That is the whole of Done-means 14 and it is a structural
property rather than a behaviour to remember: a function returning `frozenset[str]` has no tie to
break.

**`document type` is never a key.** F4 settled it: the design uses *"document type"* as the generic
word for whichever specific field the active domain declares — `application_document_type` under
College applications, `artifact_type` under Research and Code. §3.11's own worked case is a research
artifact (*"project = PVA/RDP and document type = abstract"*), so Done-means 14's four fields are
read here as **`project`, `artifact_type`, `purpose`, `target_university`**. Two keys, one prose
word, no third field.

**Ten schemas activate; six of them have field rows.** `SCHEMA_IDS` is `academic`,
`college_applications`, `research`, `career`, `photos`, `code` plus the four safety domains
`finance`, `identity`, `medical`, `legal`. `FIELD_LESS_SCHEMA_IDS` is **derived** —
`tuple(s for s in SCHEMA_IDS if s not in FIELD_SCOPES)` — rather than written down, so the schema
vocabulary and the field-scope vocabulary cannot drift apart, and a test asserts the derivation lands
on exactly `("career", "identity", "medical", "legal")`. Activating one of the four contributes
nothing to the allowlist. That is D1, narrowed, made mechanical: *"Do not author career fields. Not
in this task, not in the domain catalogue as field rows. Career is owed before P10."* A schema with
no authored fields must not cause fields to be invented, and the allowlist skipping it is how that is
guaranteed rather than remembered.

**`src/facts/` never imports `planning/domains/`.** That directory is a 574-entry research artifact
with its own gate and its own owner; the catalogue this module activates is `facts.fields`, which is
§00's own small list. Task 25 asserts the whole directory is imported nowhere in `facts`; the test
below carries the module-local half of the same guard.

**P6 authors no activation signal.** The SPEC defers it outright: *"Domain activation signals |
§3.11 ("when the evidence indicates that a domain is plausible"), §5.7 ("detection signals") | Which
evidence activates which domain is unauthored."* So `ActivationSignals` is a required argument with
no default, an empty one activates nothing, and a test asserts no `ActivationSignal` instance exists
in the module namespace. The predicate reads the file version's **existing facts** — the skeleton's
`Consumes:` line names `facts.file_facts.facts_for_file` and that is the right input: §8.6's
degradation order runs direct and rule-validated facts first, and the allowlist those facts activate
is what bounds the model afterwards.

**The allowlist is one object, computed once.** §3.5: the model *"can only propose facts that belong
to the active domain schema"*, and the skeleton requires that *"the allowlist this produces is the
same object Task 17 hands to P8, so the model … is one computation and not two."* It is deterministic
— universal fields first in catalogue order, then each active schema in `SCHEMA_IDS` order — and
deduplicated, because `project` and `artifact_type` belong to **both** Research and Code and a file
with both active must list each once and lose neither.

**Activation is per file version.** §3.4 and §8.2 make every P6 read per content hash, so a prior
version's facts cannot activate a domain on this one. A test drives that directly.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_domains.py
"""§3.11 domain activation -- Done-means 14, and §3.11's own worked case."""
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from facts.domains import (
    FIELD_LESS_SCHEMA_IDS, SCHEMA_IDS, UNIVERSAL_SCOPE, ActivationSignal,
    ActivationSignals, UnknownSchema, active_domains, active_field_allowlist,
    schema_fields,
)
from facts.fields import DOMAIN_FIELDS, FIELD_SCOPES, fields_in_scope
from facts.file_facts import FACT_ORIGINS, facts_for_file, write_fact, RULE
from facts.values import VALUE_ORIGINS, ensure_value

EVIDENCE_REF = "sha256:" + "a" * 64
CACHE_KEY = "sha256:" + "b" * 64


def _record(conn, tmp_path, *, name, body=b"one file, several facts"):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Applications", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _fact(conn, *, file_id, content_hash, field_key, value):
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=EVIDENCE_REF,
                            origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state="validated", origin=RULE,
                      evidence_refs=(EVIDENCE_REF,), cache_key=CACHE_KEY,
                      active=True)


def _when_field_present(schema_id, field_key):
    """An injected signal: this schema is plausible when this field is filled.

    The test's rule, not P6's -- "which evidence activates which domain is
    unauthored", so the plan holds the slot and the caller fills it.
    """
    return ActivationSignal(
        schema_id=schema_id,
        activates=lambda rows: any(row["field_key"] == field_key for row in rows))


@pytest.fixture()
def abstract(p6_conn, tmp_path):
    """§3.11's worked case, as facts: a research artifact submitted with an
    application. `project = PVA/RDP`, `artifact_type = abstract`,
    `purpose = university application`, `target_university = UChicago`."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="PVA-RDP abstract.pdf")
    for field_key, value in (("project", "PVA/RDP"),
                             ("artifact_type", "abstract"),
                             ("purpose", "university application"),
                             ("target_university", "UChicago")):
        _fact(p6_conn, file_id=file_id, content_hash=content_hash,
              field_key=field_key, value=value)
    return file_id, content_hash


# --- the ten schemas, and the four that carry no fields ----------------------

def test_the_ten_recognised_schemas_are_named_once():
    assert SCHEMA_IDS == ("academic", "college_applications", "research", "career",
                          "photos", "code", "finance", "identity", "medical",
                          "legal")
    assert len(set(SCHEMA_IDS)) == 10


def test_the_field_bearing_schemas_are_exactly_the_non_universal_field_scopes():
    # One vocabulary, two views: a scope is a field row's home, a schema id is what
    # activates. They cannot drift because the second is derived from the first.
    assert set(FIELD_SCOPES) - {UNIVERSAL_SCOPE} == set(SCHEMA_IDS) - set(
        FIELD_LESS_SCHEMA_IDS)
    assert UNIVERSAL_SCOPE not in SCHEMA_IDS


def test_career_identity_medical_and_legal_carry_no_field_rows(p6_conn):
    # D1 (narrowed): "Do not author career fields. Not in this task, not in the domain
    # catalogue as field rows. Career is owed before P10." Identity, medical and legal
    # are §3.15 safety domains that §3.11 gives no field row.
    assert FIELD_LESS_SCHEMA_IDS == ("career", "identity", "medical", "legal")
    for schema_id in FIELD_LESS_SCHEMA_IDS:
        assert schema_fields(schema_id) == ()
        assert schema_id not in DOMAIN_FIELDS


def test_the_catalogue_constant_and_the_loaded_table_are_the_same_data(p6_conn):
    # `DOMAIN_FIELDS` and the `fields` rows `create_fields` loaded must agree, or the
    # allowlist and the model's schema check would be reading two different lists.
    for schema_id, keys in DOMAIN_FIELDS.items():
        assert {row["field_key"] for row in fields_in_scope(p6_conn, schema_id)} == \
            set(keys)


def test_an_unrecognised_schema_is_refused_rather_than_created():
    with pytest.raises(UnknownSchema):
        ActivationSignal(schema_id="astrology", activates=lambda rows: True)
    with pytest.raises(UnknownSchema):
        schema_fields("astrology")


# --- activation: the universal set always, a domain only on evidence ---------

def test_the_universal_set_applies_to_every_file(p6_conn, tmp_path):
    # §3.11: "a small shared set of universal file facts" -- shared meaning every
    # file, with no signal required.
    file_id, content_hash = _record(p6_conn, tmp_path, name="anything.pdf")
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=ActivationSignals(()))
    universal = {row["field_key"] for row in fields_in_scope(p6_conn,
                                                             UNIVERSAL_SCOPE)}
    assert set(allowlist) == universal
    assert universal


def test_target_university_is_not_a_field_every_file_is_expected_to_have(
        p6_conn, tmp_path):
    # §3.11, verbatim: "This means target university is not a fact that every file is
    # expected to have. It is a field available only when the Applications domain is
    # plausibly active."
    file_id, content_hash = _record(p6_conn, tmp_path, name="plain.pdf")
    assert "target_university" not in active_field_allowlist(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=ActivationSignals(()))
    assert "target_university" in DOMAIN_FIELDS["college_applications"]


def test_no_signal_activates_no_domain(p6_conn, abstract):
    # "Domain activation signals ... Which evidence activates which domain is
    # unauthored." An empty signal set is the honest behaviour of an unauthored rule,
    # not a reason to guess.
    file_id, content_hash = abstract
    assert active_domains(p6_conn, file_id=file_id, content_hash=content_hash,
                          activation_signals=ActivationSignals(())) == frozenset()


def test_the_module_authors_no_activation_signal():
    import facts.domains as module
    assert [name for name, value in vars(module).items()
            if isinstance(value, (ActivationSignal, ActivationSignals))] == []
    with pytest.raises(TypeError):
        ActivationSignals()


def test_a_duplicate_signal_for_one_schema_is_refused():
    signal = _when_field_present("research", "project")
    with pytest.raises(ValueError):
        ActivationSignals((signal, signal))


# --- Done-means 14: several domains on one file, none dropped ----------------

def test_one_file_holds_four_facts_across_two_domains(p6_conn, abstract):
    # Done-means 14, as F4 resolves its field names: `document type` is the design's
    # generic word for whichever specific field the active domain declares, and
    # §3.11's own worked case is a research artifact, so it is `artifact_type`.
    file_id, content_hash = abstract
    held = {(row["field_key"], row["canonical_value"])
            for row in facts_for_file(p6_conn, file_id, content_hash)}
    assert held == {("project", "PVA/RDP"), ("artifact_type", "abstract"),
                    ("purpose", "university application"),
                    ("target_university", "UChicago")}

    signals = ActivationSignals((_when_field_present("research", "project"),
                                 _when_field_present("college_applications",
                                                     "target_university")))
    assert active_domains(p6_conn, file_id=file_id, content_hash=content_hash,
                          activation_signals=signals) == frozenset(
        {"research", "college_applications"})


def test_no_domain_is_forced_to_win(p6_conn, abstract):
    # §3.11: "the product does not need to decide which of those perspectives will
    # ultimately determine its physical location. It preserves both."
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("research", "project"),
                                 _when_field_present("college_applications",
                                                     "target_university")))
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=signals)
    for field_key in ("project", "artifact_type", "purpose", "target_university"):
        assert field_key in allowlist
    assert set(DOMAIN_FIELDS["research"]) <= set(allowlist)
    assert set(DOMAIN_FIELDS["college_applications"]) <= set(allowlist)


def test_no_field_is_dropped_when_two_domains_share_one(p6_conn, abstract):
    # `project` and `artifact_type` belong to Research AND Code. Two active domains
    # must list each once and lose neither.
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("research", "project"),
                                 _when_field_present("code", "project")))
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=signals)
    assert len(allowlist) == len(set(allowlist))
    assert set(DOMAIN_FIELDS["research"]) <= set(allowlist)
    assert set(DOMAIN_FIELDS["code"]) <= set(allowlist)
    assert allowlist.count("project") == 1
    assert allowlist.count("artifact_type") == 1


def test_an_inactive_domains_fields_stay_out_of_the_allowlist(p6_conn, abstract):
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("research", "project"),))
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=signals)
    assert "target_university" not in allowlist
    assert "capture_year" not in allowlist
    assert set(DOMAIN_FIELDS["research"]) <= set(allowlist)


def test_a_field_less_schema_activates_and_contributes_nothing(p6_conn, abstract):
    # Activating `career` must not cause a career field to appear. S3's deferral holds
    # and P6 does not un-defer it by side effect.
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("career", "project"),))
    assert active_domains(p6_conn, file_id=file_id, content_hash=content_hash,
                          activation_signals=signals) == frozenset({"career"})
    allowlist = active_field_allowlist(p6_conn, file_id=file_id,
                                       content_hash=content_hash,
                                       activation_signals=signals)
    assert set(allowlist) == {row["field_key"]
                              for row in fields_in_scope(p6_conn, UNIVERSAL_SCOPE)}


# --- the allowlist is a value, and it is deterministic -----------------------

def test_the_allowlist_is_deterministic_and_ordered_by_the_catalogue(
        p6_conn, abstract):
    file_id, content_hash = abstract
    signals = ActivationSignals((_when_field_present("college_applications",
                                                     "target_university"),
                                 _when_field_present("research", "project")))
    first = active_field_allowlist(p6_conn, file_id=file_id,
                                   content_hash=content_hash,
                                   activation_signals=signals)
    reordered = ActivationSignals(tuple(reversed(signals.signals)))
    assert active_field_allowlist(p6_conn, file_id=file_id,
                                  content_hash=content_hash,
                                  activation_signals=reordered) == first
    universal = tuple(row["field_key"]
                      for row in fields_in_scope(p6_conn, UNIVERSAL_SCOPE))
    assert first[:len(universal)] == universal


def test_activation_is_per_file_version(p6_conn, tmp_path):
    # §3.4 and §8.2 make every P6 read per file VERSION, so a prior version's facts
    # cannot activate a domain on this one.
    file_id, content_hash = _record(p6_conn, tmp_path, name="v1.pdf")
    _fact(p6_conn, file_id=file_id, content_hash=content_hash,
          field_key="project", value="PVA/RDP")
    signals = ActivationSignals((_when_field_present("research", "project"),))
    assert active_domains(p6_conn, file_id=file_id, content_hash=content_hash,
                          activation_signals=signals) == frozenset({"research"})
    assert active_domains(p6_conn, file_id=file_id, content_hash="f" * 64,
                          activation_signals=signals) == frozenset()


def test_domains_imports_nothing_from_the_research_domain_library():
    # `planning/domains/` is a 574-entry research artifact, not this catalogue.
    # Task 25 asserts the whole directory is imported nowhere in `facts`; this is the
    # module-local half of the same guard.
    import facts.domains as module
    assert module.__doc__ is not None
    imported = {value.__name__ for value in vars(module).values()
                if getattr(value, "__module__", None) is None
                and hasattr(value, "__name__")}
    assert not any(name.startswith("domains.") or name == "roster"
                   for name in imported)
    assert all(not getattr(value, "__module__", "").startswith("planning")
               for value in vars(module).values())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_domains.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'facts.domains'`

- [ ] **Step 3: Write the implementation**

```python
# src/facts/domains.py
"""§3.11 domain activation, and several domains on one file at once.

§3.11, verbatim: *"The product should have a small shared set of universal file facts
... It should then activate domain-specific schemas only when the evidence indicates
that a domain is plausible ... This means target university is not a fact that every
file is expected to have. It is a field available only when the Applications domain is
plausibly active."*

And the worked case this module exists to preserve, also verbatim: *"One file may hold
facts from more than one domain without losing information. An academic abstract
submitted as part of a university application can retain project = PVA/RDP and
document type = abstract while also carrying purpose = university application and
target university = UChicago. At the pre-sorting stage, the product does not need to
decide which of those perspectives will ultimately determine its physical location. It
preserves both so the user can later choose the appropriate organization structure."*

Two things follow and both are structural:

* **Activation adds; it never chooses.** `active_domains` returns a set, not a winner.
  No domain suppresses another, no field is dropped, and nothing here ranks.
* **P6 authors no activation signal.** *"Domain activation signals | §3.11 ("when the
  evidence indicates that a domain is plausible"), §5.7 ("detection signals") | Which
  evidence activates which domain is unauthored."* The signals arrive as an injected
  `ActivationSignals` with no default; an empty one activates nothing, which is the
  honest behaviour of an unauthored rule.

**Schemas are named, fields are not implied.** `SCHEMA_IDS` is the ten domains the
product recognises -- §3.11's six with field rows plus §3.15's remaining safety
domains. Four of the ten have **no field rows at all** (D1, narrowed): activating one
contributes nothing to the allowlist, which is exactly right, because a schema with no
authored fields must not cause fields to be invented. `FIELD_LESS_SCHEMA_IDS` is
derived from `facts.fields.FIELD_SCOPES` rather than written down, so the two
vocabularies cannot drift apart.

**This module reads `planning/domains/` never.** That directory is a research artifact
of 574 proposed entries with its own gate; the catalogue this activates is
`facts.fields`, and Task 25 asserts the import does not exist.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from facts.fields import DOMAIN_FIELDS, FIELD_SCOPES, fields_in_scope
from facts.file_facts import facts_for_file

#: §3.11's six domains with field rows, plus §3.15's four safety domains. Named here
#: because a schema id is a closed vocabulary the product recognises; what activates
#: one, and which fields one carries, are elsewhere.
SCHEMA_IDS: tuple[str, ...] = (
    "academic", "college_applications", "research", "career", "photos", "code",
    "finance", "identity", "medical", "legal")

#: `FIELD_SCOPES[0]` is the universal scope. §3.11: the universal set "applies to
#: every file", so it is in every allowlist and is never activated.
UNIVERSAL_SCOPE: str = FIELD_SCOPES[0]

#: Derived, not authored: the schemas the product recognises that carry no field rows.
#: D1 (narrowed): "Do not author career fields ... Career is owed before P10." The
#: same holds for identity, medical and legal, which §3.15 names as safety domains and
#: §3.11 gives no field row.
FIELD_LESS_SCHEMA_IDS: tuple[str, ...] = tuple(
    schema_id for schema_id in SCHEMA_IDS if schema_id not in FIELD_SCOPES)


class UnknownSchema(KeyError):
    """A signal naming a domain the product does not recognise."""


@dataclass(frozen=True, slots=True)
class ActivationSignal:
    """One injected rule: this schema is plausible when this predicate says so.

    The predicate receives the file version's existing facts -- §3.11's "when the
    evidence indicates that a domain is plausible", read as P6's own evidence-derived
    claims, which is also what makes §8.6's degradation order work: direct and
    rule-validated facts are produced first, and the allowlist they activate is what
    bounds the model afterwards.
    """

    schema_id: str
    activates: Callable[[tuple[sqlite3.Row, ...]], bool]

    def __post_init__(self) -> None:
        if self.schema_id not in SCHEMA_IDS:
            raise UnknownSchema(
                f"{self.schema_id!r} is not one of the ten recognised schemas")
        if not callable(self.activates):
            raise TypeError("an activation signal is a predicate over the file's facts")


@dataclass(frozen=True, slots=True)
class ActivationSignals:
    """The injected signal set. No default: P6 authors none of these."""

    signals: tuple[ActivationSignal, ...]

    def __post_init__(self) -> None:
        ids = [signal.schema_id for signal in self.signals]
        if len(set(ids)) != len(ids):
            raise ValueError(f"one signal per schema; duplicates: {sorted(ids)}")


def active_domains(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                   activation_signals: ActivationSignals) -> frozenset[str]:
    """Which domain schemas this file version's own evidence makes plausible.

    A set, deliberately: §3.11 preserves every perspective and "does not need to
    decide which of those perspectives will ultimately determine its physical
    location". Nothing here breaks a tie because nothing here has one to break.
    """
    established = tuple(facts_for_file(conn, file_id, content_hash))
    return frozenset(signal.schema_id for signal in activation_signals.signals
                     if signal.activates(established))


def active_field_allowlist(conn: sqlite3.Connection, *, file_id: str,
                           content_hash: str,
                           activation_signals: ActivationSignals) -> tuple[str, ...]:
    """The universal fields plus every active schema's fields, deduplicated.

    This is the object §3.5's sentence turns on -- the model "can only propose facts
    that belong to the active domain schema" -- and Task 17 hands this exact tuple to
    P8, so the allowlist is one computation and not two.

    Order is deterministic and is the catalogue's: universal first, then each active
    schema in `SCHEMA_IDS` order. `project` and `artifact_type` belong to both Research
    and Code, so a file with both active must list each once and lose neither.
    """
    active = active_domains(conn, file_id=file_id, content_hash=content_hash,
                            activation_signals=activation_signals)
    allowed: list[str] = []
    for scope in (UNIVERSAL_SCOPE,
                  *(schema_id for schema_id in SCHEMA_IDS if schema_id in active)):
        if scope not in FIELD_SCOPES:
            # A recognised schema with no field rows (D1). It activates and
            # contributes nothing; it does not cause a field to be invented.
            continue
        for row in fields_in_scope(conn, scope):
            if row["field_key"] not in allowed:
                allowed.append(row["field_key"])
    return tuple(allowed)


def schema_fields(schema_id: str) -> tuple[str, ...]:
    """The authored field keys of one schema, empty for the four field-less ones."""
    if schema_id not in SCHEMA_IDS:
        raise UnknownSchema(schema_id)
    return tuple(DOMAIN_FIELDS.get(schema_id, ()))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_domains.py -v`
Expected: PASS — 18 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/domains.py tests/p6/test_p6_domains.py
git commit -m "feat(P6): §3.11 domain activation — several domains on one file, none forced to win"
```

---

---

### Task 14: Duplicate family and version family (G5)

**Files:**
- Create: `src/facts/families.py`
- Test: `tests/p6/test_p6_families.py`

**Interfaces:**
- Consumes: `facts.evidence` — `observations_for_version`, `cite`, `analysis_tier_for_observation`;
  `database_agent.files_table.get_file`; `facts.file_facts` — `write_fact`, `FACT_ORIGINS`;
  `facts.unresolved` — `write_unresolved`, `ATTEMPTED_PRODUCERS`; `facts.values` — `ensure_value`,
  `VALUE_ORIGINS`; `facts.cache.fact_cache_key`; `evidence_shape.canonical` — `canonical_json`,
  `sha256_of`; `evidence_shape.vocabulary` — `ANALYSIS_TIERS`, `check`.
- Produces (`families.py`): `DUPLICATE_FAMILY_FIELD: str`, `VERSION_FAMILY_FIELD: str`,
  `PERCEPTUAL_HASH_LABEL: str`, `VERSION_FAMILY_STATES: tuple[str, str]`,
  `Lineage(family_value, reliability_state, evidence_refs)`,
  `duplicate_family(conn, *, file_ids, perceptual_hash_label, near_match) -> tuple[str, ...]`,
  `version_family(conn, *, file_ids, lineage_rule) -> tuple[str, ...]`.

**Done-means:** 23, 24.

**§8.3, quoted, because the refusal is the sentence:**

> The collision rule must distinguish exact duplicates from different files that happen to share a filename. A content-hash match supports deduplication review; a filename match alone does not.

**§2.6, quoted, because it is where near-duplicates come from:**

> Exact hashes and perceptual hashes can identify duplicates and near-duplicates.

**Version family had no owner anywhere in the design.** §2.9 lists *"duplicate and version-family
signals"* among what basic extraction produces and defines neither; nothing else in the design names
a version-family rule. So this task builds the two ends the design does state — byte identity, and
the refusal — and holds the middle open behind an injected `lineage_rule`. A rule that returns
nothing writes nothing, and that is the default state of the product until someone authors one.

**What the evidence for byte identity actually is, and why it is not the `files` row.** Task 4
requires every non-user fact to carry at least one `evidence_refs[]` entry and every entry to be a
P4 `observation_key` (M14). P1's `content_hash` lives on the `files` row and is **not** an
observation — P5's `filesystem.py` says so in its own source: *"G5 gives duplicate and version-family
signals to P6 'from P1's content hashes' … P6 reads those from `files`; a second copy here would be
two homes for one value."* So the hash decides the family and cannot be cited for it.

The citation is the observations the two versions **share**. `observation_key` hashes
`content_hash · extractor_name · locator · raw_value` and nothing else (P4 MINOR 8, verified), so two
files holding the same bytes produce, for every extractor that reads those bytes, literally the same
keys. That is not a proxy for byte identity; it is a consequence of it, recorded in P4's own
addressing, and a reviewer following the citation lands on the readings that are the same reading for
both files. It is also the property P4's OQ2 closure states outright: the content hash owns the
observation, so two `files` rows holding the same bytes share one observation set.

**When the shared set is empty, P6 abstains rather than asserting.** A fact with no citable evidence
is not a fact (rule 1), so the pair gets an `unresolved` row with `reason = no_candidate_evidence`
rather than a `direct` fact nobody can inspect. This is a real branch, not a defensive one: a file
version with no stored observations at all reaches it.

**A pair the design never asks about gets no row of any kind.** `report (1).pdf` and
`invoice (1).pdf` share a `(1)` suffix and nothing else. Their hashes differ, neither carries a
perceptual-hash observation, and the injected lineage rule returns nothing — so no family fact, and
**no `unresolved` row either**. The SPEC's `unresolved` schema is explicit that `field_key` is *"the
field that was attempted"*; a relation nobody proposed was never attempted, and recording it as a
refusal would make the abstention table a log of every pair in the corpus.

**`PERCEPTUAL_HASH_LABEL` is a parameter name, not a label.** P5 writes the perceptual hash as an
ordinary observation whose only distinguisher is its container-path label — and that label is P5's
string, with a space in it. P6 holding a copy would be two homes for one spelling, so the label
arrives as a required keyword with no default and the module publishes the **name of that keyword**
so the injection site has one address. Task 25's introspection can assert the property directly:
`families.PERCEPTUAL_HASH_LABEL` names a keyword-only parameter of `duplicate_family` with no
default. The test below asserts P5's actual string appears in none of this module's code.

**Two families, two value schemes, and the reason they differ.** An exact family has a natural name —
the content hash itself, which §3.13 names a Direct source and which a reviewer can verify by
hashing the bytes. A near family has none, so its value is `sha256_of(canonical_json(sorted(
perceptual-hash raw values)))`: deterministic, member-derived, and carrying no path. Adding a member
changes the near family's name, which is acceptable for a `possible` clue and is stated rather than
hidden.

**A family is only as strong as its weakest link.** `version_family` collects the injected rule's
edges, unions them into components, and writes one fact per member at the **weakest** state any edge
in that component carried. `Lineage.__post_init__` refuses `direct` outright, so Done-means 24's
*"never receive a `direct` one at all"* is enforced at the type rather than at a call site.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_families.py
"""G5 — Done-means 23 and 24. §8.3's refusal, and the two families P6 was handed."""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import NotInVocabulary

from extractors.image import PERCEPTUAL_HASH_FIELD

from facts import families
from facts.families import (
    DUPLICATE_FAMILY_FIELD, Lineage, PERCEPTUAL_HASH_LABEL, VERSION_FAMILY_FIELD,
    duplicate_family, version_family,
)
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-19T12:00:00+00:00"

#: P5 spells the label; P6 injects it. The test is the only place the two meet.
LABEL = PERCEPTUAL_HASH_FIELD


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring.

    A source-text search matches comments and docstrings, and a guard that does that
    has broken three tasks on this project already (P5 PLAN, Task 20). This reads the
    code.
    """
    tree = ast.parse(inspect.getsource(module))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings}


def _record(conn, tmp_path, *, name, body, parent="Downloads"):
    """One P1 `files` row over real bytes, so the content hash is P1's own."""
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context=parent, mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, label,
             extractor="pdf.text", zone="metadata", source_type="text_document",
             analysis_tier="native"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version="1.0.0",
        source_type=source_type, analysis_tier=analysis_tier, config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version="1.0.0", source_type=source_type, raw_value=raw,
        location=Location(zone, (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


def _never_near(left: str, right: str) -> bool:
    """The injected near-match predicate that never matches. P6 states no distance."""
    return False


def _no_lineage(conn, left_file_id: str, right_file_id: str):
    """§2.9 lists 'duplicate and version-family signals' and defines neither."""
    return None


@pytest.fixture()
def twins(p6_conn, tmp_path):
    """Two `files` rows over identical bytes: one content hash, two file ids."""
    left, left_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                              body=b"BUSIB 4300 Syllabus, Spring 2026")
    right, right_hash = _record(p6_conn, tmp_path, name="Syllabus copy.pdf",
                                body=b"BUSIB 4300 Syllabus, Spring 2026")
    assert left_hash == right_hash
    key_left = _observe(p6_conn, run_id="r-left", file_id=left,
                        content_hash=left_hash, raw="application/pdf",
                        label="mime_type")
    key_right = _observe(p6_conn, run_id="r-right", file_id=right,
                         content_hash=right_hash, raw="application/pdf",
                         label="mime_type")
    assert key_left == key_right          # the whole point: one key, two files
    return left, right, left_hash, key_left


def test_two_byte_identical_files_share_a_direct_duplicate_family_fact(twins, p6_conn):
    # Done-means 23. §3.13 names the content hash a Direct source.
    left, right, content_hash, _ = twins
    written = duplicate_family(p6_conn, file_ids=(left, right),
                               perceptual_hash_label=LABEL, near_match=_never_near)
    assert len(written) == 2
    for file_id in (left, right):
        rows = [r for r in facts_for_file(p6_conn, file_id, content_hash)
                if r["field_key"] == DUPLICATE_FAMILY_FIELD]
        assert len(rows) == 1
        assert rows[0]["reliability_state"] == "direct"
        assert rows[0]["canonical_value"] == content_hash


def test_the_duplicate_family_cites_the_keys_the_two_versions_share(twins, p6_conn):
    # M14: every entry is an observation key, and the key is what byte identity
    # produces twice. P1's content hash decides; P4's key is what a reviewer follows.
    left, right, content_hash, shared_key = twins
    duplicate_family(p6_conn, file_ids=(left, right),
                     perceptual_hash_label=LABEL, near_match=_never_near)
    row = [r for r in facts_for_file(p6_conn, left, content_hash)
           if r["field_key"] == DUPLICATE_FAMILY_FIELD][0]
    assert json.loads(row["evidence_refs"]) == [shared_key]
    assert shared_key.startswith("sha256:")


def test_a_duplicate_pair_with_nothing_to_cite_abstains(p6_conn, tmp_path):
    # Rule 1: a fact with no citable evidence is not a fact. Two identical files with
    # no stored observations get a refusal that names itself, not a silent gap.
    left, content_hash = _record(p6_conn, tmp_path, name="a.pdf", body=b"same bytes")
    right, _ = _record(p6_conn, tmp_path, name="b.pdf", body=b"same bytes")
    assert duplicate_family(p6_conn, file_ids=(left, right),
                            perceptual_hash_label=LABEL,
                            near_match=_never_near) == ()
    for file_id in (left, right):
        rows = unresolved_for_file(p6_conn, file_id, content_hash,
                                   field_key=DUPLICATE_FAMILY_FIELD)
        assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


def test_a_perceptual_hash_near_match_is_possible_and_never_direct(p6_conn, tmp_path):
    # §2.6 distinguishes "duplicates and near-duplicates"; §8.3 keeps the hash match
    # as the only thing that supports deduplication review.
    left, left_hash = _record(p6_conn, tmp_path, name="photo.jpg", body=b"pixels-one")
    right, right_hash = _record(p6_conn, tmp_path, name="photo-resized.jpg",
                                body=b"pixels-two")
    assert left_hash != right_hash
    _observe(p6_conn, run_id="p-left", file_id=left, content_hash=left_hash,
             raw="phash:00ff00ff", label=LABEL, extractor="image.metadata",
             source_type="image")
    _observe(p6_conn, run_id="p-right", file_id=right, content_hash=right_hash,
             raw="phash:00ff00fe", label=LABEL, extractor="image.metadata",
             source_type="image")
    written = duplicate_family(p6_conn, file_ids=(left, right),
                               perceptual_hash_label=LABEL,
                               near_match=lambda a, b: a[:-1] == b[:-1])
    assert len(written) == 2
    states = {r["reliability_state"]
              for file_id, digest in ((left, left_hash), (right, right_hash))
              for r in facts_for_file(p6_conn, file_id, digest)
              if r["field_key"] == DUPLICATE_FAMILY_FIELD}
    assert states == {"possible"}


def test_the_container_path_label_is_injected_and_the_module_holds_no_copy():
    # P5 owns the spelling and it has a space in it. A copy here would be a second
    # home for one string, which is this project's most expensive defect.
    assert PERCEPTUAL_HASH_LABEL == "perceptual_hash_label"
    parameter = inspect.signature(duplicate_family).parameters[PERCEPTUAL_HASH_LABEL]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty
    assert LABEL not in _code_strings(families)
    near = inspect.signature(duplicate_family).parameters["near_match"]
    assert near.default is inspect.Parameter.empty


def test_two_files_sharing_only_a_one_suffix_share_no_family_of_either_kind(
        p6_conn, tmp_path):
    # Done-means 23 and 24, and §8.5's "duplicate suffixes on unrelated files".
    left, left_hash = _record(p6_conn, tmp_path, name="report (1).pdf",
                              body=b"quarterly report")
    right, right_hash = _record(p6_conn, tmp_path, name="invoice (1).pdf",
                                body=b"an invoice")
    _observe(p6_conn, run_id="s-left", file_id=left, content_hash=left_hash,
             raw="report (1).pdf", label="normalized_filename")
    _observe(p6_conn, run_id="s-right", file_id=right, content_hash=right_hash,
             raw="invoice (1).pdf", label="normalized_filename")
    assert duplicate_family(p6_conn, file_ids=(left, right),
                            perceptual_hash_label=LABEL,
                            near_match=_never_near) == ()
    assert version_family(p6_conn, file_ids=(left, right),
                          lineage_rule=_no_lineage) == ()
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        assert facts_for_file(p6_conn, file_id, digest) == []
        # A relation nobody proposed was never attempted; `unresolved` records the
        # field that WAS attempted, not every pair in the corpus.
        assert unresolved_for_file(p6_conn, file_id, digest) == []


def test_identical_hashes_are_a_duplicate_family_and_never_a_version_family(
        twins, p6_conn):
    left, right, content_hash, _ = twins

    def always(conn, a, b):
        return Lineage(family_value="v1", reliability_state="validated",
                       evidence_refs=("sha256:deadbeef",))

    assert version_family(p6_conn, file_ids=(left, right), lineage_rule=always) == ()
    rows = [r for r in facts_for_file(p6_conn, left, content_hash)
            if r["field_key"] == VERSION_FAMILY_FIELD]
    assert rows == []


def test_a_version_family_fact_is_never_direct():
    # Done-means 24: no explicit slot states a version relation, so the refusal is at
    # the type rather than at a call site.
    assert families.VERSION_FAMILY_STATES == ("validated", "possible")
    with pytest.raises(NotInVocabulary):
        Lineage(family_value="v1", reliability_state="direct",
                evidence_refs=("sha256:deadbeef",))
    assert Lineage(family_value="v1", reliability_state="possible",
                   evidence_refs=("sha256:deadbeef",)).reliability_state == "possible"


def test_an_empty_lineage_rule_writes_no_version_family_fact(p6_conn, tmp_path):
    # §2.9 names the signals and defines none, so the default state of the product is
    # a rule that establishes nothing.
    left, left_hash = _record(p6_conn, tmp_path, name="draft v1.docx", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="draft v2.docx", body=b"two")
    assert version_family(p6_conn, file_ids=(left, right),
                          lineage_rule=_no_lineage) == ()
    assert facts_for_file(p6_conn, left, left_hash) == []
    assert facts_for_file(p6_conn, right, right_hash) == []


def test_a_lineage_that_cites_no_evidence_is_refused_rather_than_asserted(
        p6_conn, tmp_path):
    left, left_hash = _record(p6_conn, tmp_path, name="draft v1.docx", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="draft v2.docx", body=b"two")

    def uncited(conn, a, b):
        return Lineage(family_value="draft", reliability_state="validated",
                       evidence_refs=())

    assert version_family(p6_conn, file_ids=(left, right),
                          lineage_rule=uncited) == ()
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        rows = unresolved_for_file(p6_conn, file_id, digest,
                                   field_key=VERSION_FAMILY_FIELD)
        assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


def test_the_result_does_not_depend_on_the_order_the_file_ids_arrive_in(
        twins, p6_conn):
    # P4's reads are in insertion order and P6 must not inherit it (Global
    # Constraints). Two orders, one outcome, compared as sets of stored rows.
    left, right, content_hash, _ = twins
    forward = duplicate_family(p6_conn, file_ids=(left, right),
                               perceptual_hash_label=LABEL, near_match=_never_near)
    reverse = duplicate_family(p6_conn, file_ids=(right, left),
                               perceptual_hash_label=LABEL, near_match=_never_near)
    assert len(forward) == len(reverse) == 2

    def shape(ids):
        return sorted(
            (r["file_id"], r["reliability_state"], r["canonical_value"],
             r["evidence_refs"])
            for file_id in (left, right)
            for r in facts_for_file(p6_conn, file_id, content_hash)
            if r["fact_id"] in ids and r["field_key"] == DUPLICATE_FAMILY_FIELD)

    assert shape(forward) == shape(reverse)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_families.py -v`
Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.families'`

- [ ] **Step 3: Write `families.py`**

```python
# src/facts/families.py
"""G5 — the duplicate family and the version family (§2.6, §2.9, §3.11, §8.3).

Both are §3.11 universal fields and **version family had no owner anywhere in the
design**. §2.9 lists "duplicate and version-family signals" among what basic
extraction produces and defines neither, so this module builds the two ends the
design does state and holds the middle open:

    byte identity          §8.3: "A content-hash match supports deduplication
                           review; a filename match alone does not."     -> `direct`
    near-duplicates        §2.6: "Exact hashes and perceptual hashes can identify
                           duplicates and near-duplicates."              -> `possible`
    shared lineage         nothing states it                             -> injected

**Why the decision and the citation are different objects.** P1's `content_hash`
lives on the `files` row and is not an observation -- `extractors/filesystem.py`
deliberately does not re-emit it, because "a second copy here would be two homes for
one value". So the hash decides membership and cannot be cited for it. What is cited
is the observations the members SHARE: `observation_key` hashes
`content_hash / extractor_name / locator / raw_value` and nothing else, so two files
holding the same bytes produce literally the same keys for every extractor that read
those bytes. The citation is a consequence of byte identity, not a proxy for it.

When the shared set is empty, this module abstains: a fact with no citable evidence
is not a fact, and the refusal is a row (B7), not a gap.

**No filename ever establishes either family.** `report (1).pdf` and
`invoice (1).pdf` share a suffix and nothing else. That pair produces no fact and no
`unresolved` row: the SPEC's `unresolved` schema records "the field that was
attempted", and a relation nobody proposed was never attempted.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from itertools import combinations
from typing import Any, Callable, Iterable, Mapping

from database_agent.files_table import get_file

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS, check

from facts.cache import fact_cache_key
from facts.evidence import analysis_tier_for_observation, cite, observations_for_version
from facts.file_facts import FACT_ORIGINS, write_fact, DETERMINISTIC_EXTRACTOR, RULE
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: §3.11's universal field keys, snake_case per D6. Resolved through the catalogue on
#: every write, so a drift raises `FieldNotInCatalogue` rather than inserting a field.
DUPLICATE_FAMILY_FIELD: str = "duplicate_family"
VERSION_FAMILY_FIELD: str = "version_family"

#: The NAME of the required keyword the container-path label arrives under -- not the
#: label. P5 spells the label and it has a space in it; a copy here would be a second
#: home for one string. Task 25 asserts this names a keyword-only parameter of
#: `duplicate_family` with no default.
PERCEPTUAL_HASH_LABEL: str = "perceptual_hash_label"

#: Done-means 24: a version family is never `direct`, because no explicit slot states
#: a version relation. §3.13: a deterministic rule that passes a contextual check is
#: `validated`; anything weaker is `possible`.
VERSION_FAMILY_STATES: tuple[str, str] = ("validated", "possible")


@dataclass(frozen=True)
class Lineage:
    """One injected rule's verdict that two file versions share lineage.

    The rule is the caller's: §2.9 names the signals and states none of them. What
    this type enforces is the half the design DOES state -- that the answer is never
    `direct`.
    """
    family_value: str
    reliability_state: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        check(self.reliability_state, VERSION_FAMILY_STATES, name="reliability_state")


@dataclass(frozen=True)
class _Version:
    """One (file, content hash) with its evidence already read once."""
    file_id: str
    content_hash: str
    observations: tuple[Observation, ...]

    @property
    def keys(self) -> frozenset[str]:
        return frozenset(cite(one) for one in self.observations)


def _read(conn: sqlite3.Connection, file_ids: Iterable[str]) -> tuple[_Version, ...]:
    """Every version, in file-id order.

    Sorted before anything is decided. P4's reads are in insertion order (verified by
    execution) and insertion order is a property of one database, not of the corpus;
    a computation that inherited it would make the same corpus resolve differently
    depending on the order it was extracted in.
    """
    versions = []
    for file_id in sorted(set(file_ids)):
        row = dict(get_file(conn, file_id))
        content_hash = row["content_hash"]
        versions.append(_Version(
            file_id=file_id, content_hash=content_hash,
            observations=tuple(observations_for_version(conn, file_id, content_hash))))
    return tuple(versions)


def _cache_key(conn: sqlite3.Connection, *, content_hash: str,
               observations: Iterable[Observation]) -> str:
    """§3.4's five parts for a fact built from several observations.

    §3.4 states one extractor version and one analysis tier; a fact citing several
    observations has several of each, and no task owns the reconciliation. The rule
    is written out here rather than shared because `facts.cache` is another task's
    module: the versions are the canonical JSON of the sorted distinct
    (name, version) pairs, and the tier is the LAST one present in `ANALYSIS_TIERS`
    order -- filesystem < native < ocr < llm -- so a fact that cited an `ocr`
    reading lands outside the cache slot the native pass computed under, which is
    what makes preamble rule 5's pass 4 supersede rather than overwrite.
    """
    observations = tuple(observations)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in observations})
    tiers = {analysis_tier_for_observation(conn, one) for one in observations}
    tier = max(tiers, key=ANALYSIS_TIERS.index) if tiers else ANALYSIS_TIERS[0]
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=tier, model_identifier=None, prompt_fingerprint=None)


def _abstain(conn: sqlite3.Connection, *, version: _Version, field_key: str,
             producer: str) -> None:
    """B7: a refusal is a row naming the field and the reason it refused."""
    write_unresolved(
        conn, file_id=version.file_id, content_hash=version.content_hash,
        field_key=field_key, reason="no_candidate_evidence",
        attempted_producers=(producer,), evidence_refs=(),
        cache_key=_cache_key(conn, content_hash=version.content_hash,
                             observations=version.observations))


def _write_family(conn: sqlite3.Connection, *, version: _Version, field_key: str,
                  canonical_value: str, reliability_state: str, origin: str,
                  evidence_refs: tuple[str, ...],
                  cited: tuple[Observation, ...]) -> str:
    value_id = ensure_value(conn, field_key=field_key,
                            canonical_value=canonical_value,
                            first_evidence_ref=evidence_refs[0],
                            origin=VALUE_ORIGINS[0])
    return write_fact(
        conn, file_id=version.file_id, content_hash=version.content_hash,
        field_key=field_key, value_id=value_id,
        reliability_state=reliability_state, origin=origin,
        evidence_refs=evidence_refs,
        cache_key=_cache_key(conn, content_hash=version.content_hash,
                             observations=cited),
        active=True)


def duplicate_family(conn: sqlite3.Connection, *, file_ids: Iterable[str],
                     perceptual_hash_label: str,
                     near_match: Callable[[str, str], bool]) -> tuple[str, ...]:
    """Done-means 23. Byte identity is `direct`; a near match is at most `possible`.

    `perceptual_hash_label` and `near_match` are required with no default. §2.6 names
    the perceptual hash and states no distance metric and no threshold, so P6 holds
    neither; the label is P5's string and P6 holds no copy of it.
    """
    versions = _read(conn, file_ids)
    written: list[str] = []

    by_hash: dict[str, list[_Version]] = {}
    for version in versions:
        by_hash.setdefault(version.content_hash, []).append(version)

    exact_members: set[str] = set()
    for content_hash, members in sorted(by_hash.items()):
        if len(members) < 2:
            continue
        exact_members.update(member.file_id for member in members)
        shared = sorted(frozenset.intersection(*(m.keys for m in members)))
        for member in members:
            if not shared:
                _abstain(conn, version=member, field_key=DUPLICATE_FAMILY_FIELD,
                         producer=ATTEMPTED_PRODUCERS[0])
                continue
            cited = tuple(one for one in member.observations
                          if cite(one) in set(shared))
            written.append(_write_family(
                conn, version=member, field_key=DUPLICATE_FAMILY_FIELD,
                canonical_value=content_hash, reliability_state="direct",
                origin=DETERMINISTIC_EXTRACTOR, evidence_refs=tuple(shared), cited=cited))

    written.extend(_near_families(conn, versions=versions,
                                  perceptual_hash_label=perceptual_hash_label,
                                  near_match=near_match))
    return tuple(written)


def _perceptual(version: _Version, label: str) -> tuple[Observation, ...]:
    """Every observation whose container path carries the injected label."""
    return tuple(
        one for one in version.observations
        if any(segment.label == label
               for segment in one.location.container_path))


def _near_families(conn: sqlite3.Connection, *, versions: tuple[_Version, ...],
                   perceptual_hash_label: str,
                   near_match: Callable[[str, str], bool]) -> list[str]:
    """§2.6's near-duplicates, at `possible` and never above.

    Pairs already in one exact family are skipped: they are a duplicate family at
    `direct` already, and a weaker second fact over the same members for the same
    field is noise rather than evidence.
    """
    carriers = {version.file_id: readings
                for version in versions
                if (readings := _perceptual(version, perceptual_hash_label))}
    parent = {file_id: file_id for file_id in carriers}

    def find(file_id: str) -> str:
        while parent[file_id] != file_id:
            parent[file_id] = parent[parent[file_id]]
            file_id = parent[file_id]
        return file_id

    by_id = {version.file_id: version for version in versions}
    for left, right in combinations(sorted(carriers), 2):
        if by_id[left].content_hash == by_id[right].content_hash:
            continue
        if any(near_match(a.raw_value, b.raw_value)
               for a in carriers[left] for b in carriers[right]):
            parent[find(left)] = find(right)

    components: dict[str, list[str]] = {}
    for file_id in sorted(carriers):
        components.setdefault(find(file_id), []).append(file_id)

    written: list[str] = []
    for members in sorted(components.values()):
        if len(members) < 2:
            continue
        raws = sorted({one.raw_value for file_id in members
                       for one in carriers[file_id]})
        canonical_value = sha256_of(canonical_json(raws))
        for file_id in members:
            cited = carriers[file_id]
            refs = tuple(sorted(cite(one) for one in cited))
            written.append(_write_family(
                conn, version=by_id[file_id], field_key=DUPLICATE_FAMILY_FIELD,
                canonical_value=canonical_value, reliability_state="possible",
                origin=DETERMINISTIC_EXTRACTOR, evidence_refs=refs, cited=cited))
    return written


def version_family(conn: sqlite3.Connection, *, file_ids: Iterable[str],
                   lineage_rule: Callable[[sqlite3.Connection, str, str],
                                          Lineage | None]) -> tuple[str, ...]:
    """Done-means 24. Distinct content hashes, never `direct`, never a filename.

    `lineage_rule` is required with no default and receives the connection and the
    two file ids: §2.9 names the signals and defines none, so P6 states nothing about
    what a lineage is and a rule that establishes nothing writes nothing.

    A family is only as strong as its weakest link -- a component joined by one
    `validated` edge and one `possible` edge is written at `possible`, because the
    component is only connected at all through the weaker claim.
    """
    versions = _read(conn, file_ids)
    by_id = {version.file_id: version for version in versions}
    parent = {version.file_id: version.file_id for version in versions}
    edges: dict[str, list[Lineage]] = {}

    def find(file_id: str) -> str:
        while parent[file_id] != file_id:
            parent[file_id] = parent[parent[file_id]]
            file_id = parent[file_id]
        return file_id

    refused: set[str] = set()
    for left, right in combinations(sorted(by_id), 2):
        # Identical hashes are a duplicate family, never a version family.
        if by_id[left].content_hash == by_id[right].content_hash:
            continue
        lineage = lineage_rule(conn, left, right)
        if lineage is None:
            continue
        if not lineage.evidence_refs:
            refused.update((left, right))
            continue
        parent[find(left)] = find(right)
        for file_id in (left, right):
            edges.setdefault(file_id, []).append(lineage)

    for file_id in sorted(refused):
        if file_id not in edges:
            _abstain(conn, version=by_id[file_id], field_key=VERSION_FAMILY_FIELD,
                     producer=ATTEMPTED_PRODUCERS[1])

    components: dict[str, list[str]] = {}
    for file_id in sorted(by_id):
        if file_id in edges:
            components.setdefault(find(file_id), []).append(file_id)

    written: list[str] = []
    for members in sorted(components.values()):
        if len(members) < 2:
            continue
        lineages = [one for file_id in members for one in edges[file_id]]
        canonical_value = min(one.family_value for one in lineages)
        weakest = ("possible" if any(one.reliability_state == "possible"
                                     for one in lineages) else "validated")
        for file_id in members:
            refs = tuple(sorted({ref for one in edges[file_id]
                                 for ref in one.evidence_refs}))
            cited = tuple(one for one in by_id[file_id].observations
                          if cite(one) in set(refs))
            written.append(_write_family(
                conn, version=by_id[file_id], field_key=VERSION_FAMILY_FIELD,
                canonical_value=canonical_value, reliability_state=weakest,
                origin=RULE, evidence_refs=refs, cited=cited))
    return tuple(written)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_families.py -v`
Expected: PASS — 11 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/families.py tests/p6/test_p6_families.py
git commit -m "feat(P6): G5 duplicate and version families — a hash decides, a filename never does"
```

---

---

### Task 15: The bounded download session (G6)

**Files:**
- Create: `src/facts/session.py`
- Test: `tests/p6/test_p6_session.py`

**Interfaces:**
- Consumes: `database_agent.files_table.get_file` (`observed_timestamps`, `directory_position`);
  `facts.evidence` — `observations_for_version`, `cite`, `analysis_tier_for_observation`;
  `facts.file_facts` — `write_fact`, `FACT_ORIGINS`; `facts.unresolved` — `write_unresolved`,
  `ATTEMPTED_PRODUCERS`; `facts.values` — `ensure_value`, `VALUE_ORIGINS`;
  `facts.cache.fact_cache_key`; `evidence_shape.canonical` — `canonical_json`, `sha256_of`;
  `evidence_shape.vocabulary.ANALYSIS_TIERS`.
- Produces (`session.py`): `DOWNLOAD_SESSION_FIELD: str`, `SESSION_STATE: str`,
  `SessionBoundary(window_seconds, require_same_parent_folder_context, minimum_members)` — injected,
  no defaults; `SessionNeverPromoted(ValueError)`, `require_possible(reliability_state) -> str`,
  `bounded_sessions(conn, *, file_ids, boundary) -> Mapping[str, str]`.

**Done-means:** 25.

**§3.9, quoted, because every clause of it binds:**

> Purpose may be supported strongly by an existing user-created folder name or explicit language in a form or portal. It may be supported more weakly by a tightly bounded download session. A session should never be treated as proof of topic, and it should not carry the same confidence as a hash match or a directly extracted document fact. It is a purpose clue and a review aid, not a basis for automatic semantic propagation.

**§4.7, quoted, because it is the other half of the ceiling:**

> A tight download session alone is never sufficient: it is a retrieval clue that may bring the files together, but not proof of their shared purpose.

**The ceiling is enforced at a function, not at a call site.** *"It should not carry the same
confidence as a hash match or a directly extracted document fact"* is a statement about every route,
not about this module's one call. So `require_possible` is the module's only gate to a
`download_session` write and it raises on anything but `possible` — a test can attempt the promotion
directly and require the raise, which is what the skeleton asks for and what inspecting a call site
cannot give. No rule promotes it because no rule can reach the write.

**Being `possible` is what keeps it out of a folder proposal, and that is by construction.** §3.6's
proposal-eligible read excludes `possible` and `rejected`; the session never becomes eligible
because the state it is pinned at is one of the two excluded ones. There is no second mechanism and
there is nothing to remember to switch off.

**`destination_eligible = FALSE` for the field.** §3.9 calls the session *"a purpose clue and a
review aid"*; a folder level built from one would put the download window into the tree. The
catalogue is Task 2's, so this task asserts the property rather than setting it.

**The fact is written for the member file only.** §3.9: *"not a basis for automatic semantic
propagation"*; §4.3 and §4.1 say the same for groups — the graph *"does not automatically copy those
missing facts onto sparse files"*. Membership in a session gives a file one row on one field and
nothing else, ever.

**Half of §3.9's evidence has no observation to cite, and that is a finding rather than a
workaround.** §3.9's two inputs are the timestamps and the parent-folder context. P5's
`filesystem.py` emits the parent-folder context as an ordinary observation at `zone = "path"` —
citable. It deliberately emits **no** timestamp observation, because G6 hands the session to P6
"computed from P3 timestamps" and a second copy would be two homes for one value. So the mtime is
read from P1's `files` row and is not citable, and a session whose members carry no `path`
observation has nothing to cite at all: it abstains with `reason = no_candidate_evidence` rather
than asserting an uninspectable clue. Reported under *Contract ambiguities*.

**The session's name is a digest, not a folder.** A session identifier built from the parent folder's
name would put a path fragment inside a value, which is the same mistake §3.14's negative contract
forbids at the column level. The canonical value is
`sha256_of(canonical_json(sorted(member file ids)))`: deterministic, inspectable, and carrying
nothing about where the files sat. Adding a member renames the session, which is acceptable for a
clue that may never exceed `possible` and is stated rather than hidden.

**Silence is not a refusal.** A file whose two inputs exist but which lands in no session gets no
fact and no `unresolved` row, on the same reading Task 14 applies: `unresolved` records *"the field
that was attempted"*, and a window that simply contained one file was never a proposal.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_session.py
"""G6 — Done-means 25. §3.9's bounded download session, pinned at `possible`."""
from __future__ import annotations

import dataclasses
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts import session
from facts.fields import get_field
from facts.file_facts import FACT_ORIGINS, facts_for_file, write_fact, RULE
from facts.session import (
    DOWNLOAD_SESSION_FIELD, SESSION_STATE, SessionBoundary, SessionNeverPromoted,
    bounded_sessions, require_possible,
)
from facts.unresolved import unresolved_for_file
from facts.values import VALUE_ORIGINS, ensure_value

CLOCK = "2026-08-19T12:00:00+00:00"

#: Every number below is the TEST's, injected. §3.9 requires the clue and states no
#: numbers, so the module holds none.
TIGHT = SessionBoundary(window_seconds=120.0,
                        require_same_parent_folder_context=True,
                        minimum_members=2)


def _download(conn, tmp_path, *, name, body, mtime, parent="Downloads",
              with_path_observation=True, run_id=None):
    path = tmp_path / parent / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": mtime}),
        parent_folder_context=parent, mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    run_id = run_id or f"run-{name}"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="filesystem.record", extractor_version="0.1.0",
        source_type="filesystem", analysis_tier="filesystem", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    key = None
    if with_path_observation:
        # P5's `filesystem.py` emits §2.9's parent-folder context at zone `path`.
        observation = Observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="filesystem.record", extractor_version="0.1.0",
            source_type="filesystem", raw_value=parent,
            location=Location("path"), occurrence_count=1, observed_at=CLOCK,
            reliability="possible", run_id=run_id)
        record_observation(conn, observation)
        key = observation.observation_key
    return file_id, content_hash, key


def _session_rows(conn, file_id, content_hash):
    return [r for r in facts_for_file(conn, file_id, content_hash)
            if r["field_key"] == DOWNLOAD_SESSION_FIELD]


@pytest.fixture()
def one_session(p6_conn, tmp_path):
    left = _download(p6_conn, tmp_path, name="transcript.pdf", body=b"one",
                     mtime=1_700_000_000.0)
    right = _download(p6_conn, tmp_path, name="resume.pdf", body=b"two",
                      mtime=1_700_000_060.0)
    return left, right


def test_a_session_derived_fact_is_possible(one_session, p6_conn):
    # Done-means 25, and §3.13's "a possible fact is a useful but insufficient clue,
    # such as membership in a short download session".
    (left, left_hash, _), (right, right_hash, _) = one_session
    written = bounded_sessions(p6_conn, file_ids=(left, right), boundary=TIGHT)
    assert set(written) == {left, right}
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        rows = _session_rows(p6_conn, file_id, digest)
        assert len(rows) == 1
        assert rows[0]["reliability_state"] == "possible"
    assert SESSION_STATE == "possible"


def test_no_code_path_can_write_the_session_field_at_another_state():
    # §3.9: it "should not carry the same confidence as a hash match or a directly
    # extracted document fact". Attempted, not inspected.
    assert require_possible("possible") == "possible"
    for state in ("validated", "direct", "llm_supported", "user_confirmed"):
        with pytest.raises(SessionNeverPromoted):
            require_possible(state)


def test_a_session_fact_is_absent_from_the_proposal_eligible_read(one_session, p6_conn):
    # §3.6 excludes `possible`, so the exclusion is the state and not a second rule.
    (left, left_hash, _), (right, _, _) = one_session
    bounded_sessions(p6_conn, file_ids=(left, right), boundary=TIGHT)
    read_surface = pytest.importorskip("facts.read_surface")
    eligible = read_surface.proposal_eligible(p6_conn, file_id=left,
                                              content_hash=left_hash)
    assert [r["field_key"] for r in eligible] == []


def test_the_download_session_field_is_never_destination_eligible(p6_conn):
    # §3.9 makes it a purpose clue and a review aid; a folder level built from one
    # would put the download window into the tree.
    row = get_field(p6_conn, DOWNLOAD_SESSION_FIELD)
    assert row["scope"] == "universal"
    assert not row["destination_eligible"]


def test_the_session_fact_is_written_for_the_member_file_only(one_session, p6_conn):
    # §3.9: "not a basis for automatic semantic propagation"; §4.1: the graph "does
    # not automatically copy those missing facts onto sparse files".
    (left, left_hash, left_key), (right, right_hash, _) = one_session
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="BUSIB 4300",
                            first_evidence_ref=left_key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=left, content_hash=left_hash, field_key="subject",
               value_id=value_id, reliability_state="validated",
               origin=RULE, evidence_refs=(left_key,),
               cache_key="sha256:cache", active=True)
    bounded_sessions(p6_conn, file_ids=(left, right), boundary=TIGHT)
    right_fields = {r["field_key"]
                    for r in facts_for_file(p6_conn, right, right_hash)}
    assert right_fields == {DOWNLOAD_SESSION_FIELD}


def test_the_boundary_is_injected_and_the_module_states_no_window():
    # §3.9 requires the clue and states no numbers, so none is here.
    fields = dataclasses.fields(SessionBoundary)
    assert [f.name for f in fields] == ["window_seconds",
                                        "require_same_parent_folder_context",
                                        "minimum_members"]
    for field in fields:
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING
    parameter = inspect.signature(bounded_sessions).parameters["boundary"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty
    # Task 25's technique: runtime introspection of the namespace, not a text search.
    numbers = {name: value for name, value in vars(session).items()
               if isinstance(value, (int, float)) and not isinstance(value, bool)}
    assert numbers == {}


def test_files_outside_the_window_are_not_one_session(p6_conn, tmp_path):
    left = _download(p6_conn, tmp_path, name="a.pdf", body=b"one",
                     mtime=1_700_000_000.0)
    right = _download(p6_conn, tmp_path, name="b.pdf", body=b"two",
                      mtime=1_700_009_999.0)
    assert bounded_sessions(p6_conn, file_ids=(left[0], right[0]),
                            boundary=TIGHT) == {}
    assert _session_rows(p6_conn, left[0], left[1]) == []
    assert _session_rows(p6_conn, right[0], right[1]) == []


def test_a_session_below_the_minimum_is_not_a_session(p6_conn, tmp_path):
    # "Tightly bounded" is the caller's definition, including how many files make one.
    only = _download(p6_conn, tmp_path, name="alone.pdf", body=b"one",
                     mtime=1_700_000_000.0)
    assert bounded_sessions(p6_conn, file_ids=(only[0],), boundary=TIGHT) == {}
    assert _session_rows(p6_conn, only[0], only[1]) == []
    # Silence, not a refusal: a window that contained one file was never a proposal.
    assert unresolved_for_file(p6_conn, only[0], only[1]) == []


def test_a_member_with_no_citable_parent_folder_observation_abstains(
        p6_conn, tmp_path):
    # Rule 1: an uninspectable clue is not a clue. P5 writes no timestamp
    # observation, so a member with no `path` observation has nothing to cite.
    left = _download(p6_conn, tmp_path, name="a.pdf", body=b"one",
                     mtime=1_700_000_000.0, with_path_observation=False)
    right = _download(p6_conn, tmp_path, name="b.pdf", body=b"two",
                      mtime=1_700_000_060.0, with_path_observation=False)
    assert bounded_sessions(p6_conn, file_ids=(left[0], right[0]),
                            boundary=TIGHT) == {}
    for file_id, digest, _ in (left, right):
        rows = unresolved_for_file(p6_conn, file_id, digest,
                                   field_key=DOWNLOAD_SESSION_FIELD)
        assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


def test_the_session_value_is_deterministic_and_carries_no_path(one_session, p6_conn):
    (left, left_hash, _), (right, right_hash, _) = one_session
    bounded_sessions(p6_conn, file_ids=(left, right), boundary=TIGHT)
    values = {_session_rows(p6_conn, file_id, digest)[0]["canonical_value"]
              for file_id, digest in ((left, left_hash), (right, right_hash))}
    assert len(values) == 1
    value = values.pop()
    assert value.startswith("sha256:")
    assert "Downloads" not in value


def test_different_parent_folder_contexts_are_not_one_session(p6_conn, tmp_path):
    left = _download(p6_conn, tmp_path, name="a.pdf", body=b"one",
                     mtime=1_700_000_000.0, parent="Downloads")
    right = _download(p6_conn, tmp_path, name="b.pdf", body=b"two",
                      mtime=1_700_000_060.0, parent="Desktop")
    assert bounded_sessions(p6_conn, file_ids=(left[0], right[0]),
                            boundary=TIGHT) == {}
    relaxed = SessionBoundary(window_seconds=120.0,
                              require_same_parent_folder_context=False,
                              minimum_members=2)
    assert set(bounded_sessions(p6_conn, file_ids=(left[0], right[0]),
                                boundary=relaxed)) == {left[0], right[0]}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_session.py -v`
Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.session'`

- [ ] **Step 3: Write `session.py`**

```python
# src/facts/session.py
"""G6 — §3.9's tightly bounded download session, pinned at `possible` (§4.2).

§3.9, and every clause binds:

    "It may be supported more weakly by a tightly bounded download session. A session
     should never be treated as proof of topic, and it should not carry the same
     confidence as a hash match or a directly extracted document fact. It is a
     purpose clue and a review aid, not a basis for automatic semantic propagation."

So:

- the ceiling is a FUNCTION, not a call site. `require_possible` is the only gate to
  a `download_session` write and it raises on anything else, so no rule can promote
  the field and no §3.7 margin can reach it;
- being `possible` is what keeps it out of §3.6's proposal-eligible read. There is no
  second mechanism, and nothing to remember to switch off;
- the fact is written for the member file and copies nothing. §4.1: the graph "does
  not automatically copy those missing facts onto sparse files".

**What is citable and what is not.** §3.9's two inputs are the timestamps and the
parent-folder context. P5 emits the parent-folder context as an ordinary observation
at `zone = "path"`; it deliberately emits NO timestamp observation, because G6 hands
the session to P6 "computed from P3 timestamps" and a second copy would be two homes
for one value. The mtime is therefore read from P1's `files` row and is not citable,
and a member with no `path` observation has nothing to cite at all: it abstains
rather than asserting a clue nobody can inspect.

**The session's name is a digest.** A name built from the parent folder would put a
path fragment inside a value, which is §3.14's mistake one layer down.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from database_agent.files_table import get_file

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS

from facts.cache import fact_cache_key
from facts.evidence import analysis_tier_for_observation, cite, observations_for_version
from facts.file_facts import FACT_ORIGINS, write_fact, DETERMINISTIC_EXTRACTOR
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: The one universal field this part adds beyond §3.11's six, because §3.9 requires a
#: representation and §4.2 requires it to be retrievable. It is not `purpose`: the
#: session names no purpose value.
DOWNLOAD_SESSION_FIELD: str = "download_session"

#: §3.13's own example of a `possible` fact is "membership in a short download
#: session". The ceiling and the floor are the same value.
SESSION_STATE: str = "possible"

#: P4's zone for §2.9's parent-folder context, as P5 writes it. Read from P4's
#: vocabulary rather than from an extractor name: P6 branches on neither
#: `source_type` nor `extractor_name` anywhere.
PARENT_FOLDER_ZONE: str = "path"


class SessionNeverPromoted(ValueError):
    """§3.9's ceiling, raised rather than documented."""


@dataclass(frozen=True)
class SessionBoundary:
    """What makes a session "tightly bounded". Injected; the design states none.

    Every field is required. §3.9 asks for the clue and gives no window, no folder
    rule and no minimum, so a default here would be P6 answering a deferred question
    inside an implementation.
    """
    window_seconds: float
    require_same_parent_folder_context: bool
    minimum_members: int


def require_possible(reliability_state: str) -> str:
    """The only gate to a `download_session` write.

    §3.9: a session "should not carry the same confidence as a hash match or a
    directly extracted document fact". That is a statement about every route, so it
    is enforced where every route has to pass rather than at the one call this module
    makes -- a test can attempt the promotion and require the raise.
    """
    if reliability_state != SESSION_STATE:
        raise SessionNeverPromoted(
            f"§3.9 pins a download-session clue at {SESSION_STATE!r}; "
            f"{reliability_state!r} would give a retrieval clue the confidence of a "
            "hash match or a directly extracted document fact")
    return reliability_state


@dataclass(frozen=True)
class _Member:
    file_id: str
    content_hash: str
    mtime: float
    parent_folder_context: str
    observations: tuple[Observation, ...]

    @property
    def citable(self) -> tuple[Observation, ...]:
        return tuple(one for one in self.observations
                     if one.zone == PARENT_FOLDER_ZONE)


def _members(conn: sqlite3.Connection,
             file_ids: Iterable[str]) -> tuple[_Member, ...]:
    """Every file that carries §3.9's two inputs, ordered by time then by file id.

    The secondary key is not decoration: two files written in the same second must
    fall in one order for one corpus regardless of the order P4 stored them in.
    """
    members: list[_Member] = []
    for file_id in sorted(set(file_ids)):
        row = dict(get_file(conn, file_id))
        parent = row["directory_position"]
        stamps = json.loads(row["observed_timestamps"] or "{}")
        mtime = stamps.get("mtime")
        if parent is None or mtime is None:
            continue          # §3.9's inputs are absent; nothing was proposed
        content_hash = row["content_hash"]
        members.append(_Member(
            file_id=file_id, content_hash=content_hash, mtime=float(mtime),
            parent_folder_context=parent,
            observations=tuple(observations_for_version(conn, file_id,
                                                        content_hash))))
    return tuple(sorted(members, key=lambda m: (m.mtime, m.file_id)))


def _windows(members: tuple[_Member, ...],
             boundary: SessionBoundary) -> list[list[_Member]]:
    """Consecutive members inside the injected window, as one chain each."""
    runs: list[list[_Member]] = []
    for member in members:
        if runs and _joins(runs[-1][-1], member, boundary):
            runs[-1].append(member)
        else:
            runs.append([member])
    return [run for run in runs if len(run) >= boundary.minimum_members]


def _joins(previous: _Member, candidate: _Member,
           boundary: SessionBoundary) -> bool:
    if candidate.mtime - previous.mtime > boundary.window_seconds:
        return False
    if (boundary.require_same_parent_folder_context
            and previous.parent_folder_context
            != candidate.parent_folder_context):
        return False
    return True


def _cache_key(conn: sqlite3.Connection, *, content_hash: str,
               observations: Iterable[Observation]) -> str:
    """§3.4's five parts. The rule is stated once in the plan and applied here.

    The versions are the canonical JSON of the sorted distinct (name, version) pairs
    of the cited observations; the tier is the last one present in `ANALYSIS_TIERS`
    order, so a fact citing an `ocr` reading lands outside the slot the native pass
    computed under.
    """
    observations = tuple(observations)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in observations})
    tiers = {analysis_tier_for_observation(conn, one) for one in observations}
    tier = max(tiers, key=ANALYSIS_TIERS.index) if tiers else ANALYSIS_TIERS[0]
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=tier, model_identifier=None, prompt_fingerprint=None)


def bounded_sessions(conn: sqlite3.Connection, *, file_ids: Iterable[str],
                     boundary: SessionBoundary) -> Mapping[str, str]:
    """Done-means 25. `file_id -> fact_id` for every member of a bounded session.

    A file whose two §3.9 inputs exist but which lands in no session gets no fact and
    no `unresolved` row: the abstention record names "the field that was attempted",
    and a window that contained one file was never a proposal. A file that IS in a
    session but has nothing to cite abstains, because a clue nobody can inspect is
    not a clue.
    """
    written: dict[str, str] = {}
    for window in _windows(_members(conn, file_ids), boundary):
        citable = {member.file_id: member.citable for member in window}
        if not all(citable.values()):
            for member in window:
                write_unresolved(
                    conn, file_id=member.file_id,
                    content_hash=member.content_hash,
                    field_key=DOWNLOAD_SESSION_FIELD,
                    reason="no_candidate_evidence",
                    attempted_producers=(ATTEMPTED_PRODUCERS[0],),
                    evidence_refs=(),
                    cache_key=_cache_key(conn,
                                         content_hash=member.content_hash,
                                         observations=member.observations))
            continue
        canonical_value = sha256_of(canonical_json(
            sorted(member.file_id for member in window)))
        for member in window:
            refs = tuple(sorted(cite(one) for one in citable[member.file_id]))
            value_id = ensure_value(
                conn, field_key=DOWNLOAD_SESSION_FIELD,
                canonical_value=canonical_value, first_evidence_ref=refs[0],
                origin=VALUE_ORIGINS[0])
            written[member.file_id] = write_fact(
                conn, file_id=member.file_id, content_hash=member.content_hash,
                field_key=DOWNLOAD_SESSION_FIELD, value_id=value_id,
                reliability_state=require_possible(SESSION_STATE),
                origin=DETERMINISTIC_EXTRACTOR, evidence_refs=refs,
                cache_key=_cache_key(conn, content_hash=member.content_hash,
                                     observations=citable[member.file_id]),
                active=True)
    return written
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_session.py -v`
Expected: PASS — 11 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/session.py tests/p6/test_p6_session.py
git commit -m "feat(P6): G6 the bounded download session — a clue, pinned at possible"
```

---

---

### Task 16: Photo events, and §2.6's media-type conflict (G7, M2)

**Files:**
- Create: `src/facts/photo_event.py`
- Test: `tests/p6/test_p6_photo_event.py`

**Interfaces:**
- Consumes: `facts.evidence` — `observations_for_version`, `cite`, `analysis_tier_for_observation`;
  `facts.facets` — `Candidate`, `fill_or_abstain`; `facts.file_facts` — `write_fact`,
  `FACT_ORIGINS`; `facts.unresolved` — `write_unresolved`, `ATTEMPTED_PRODUCERS`; `facts.values` —
  `ensure_value`, `VALUE_ORIGINS`; `facts.cache.fact_cache_key`;
  `database_agent.files_table.get_file`; `evidence_shape.canonical` — `canonical_json`, `sha256_of`;
  `evidence_shape.vocabulary` — `SIGNAL_TIERS`, `ANALYSIS_TIERS`, `check`.
- Produces (`photo_event.py`): `EVENT_FIELD: str`, `MEDIA_TYPE_FIELD: str`, `EVENT_STATE: str`,
  `EVENT_INPUTS: tuple[str, str, str]`, `MEDIA_TYPES: tuple[str, str]`,
  `PHOTO_BANDS: tuple[int, ...]`, `SCREENSHOT_BAND: tuple[int, ...]`,
  `PhotoEventClustering(labels, same_event, minimum_members)` — injected, no defaults;
  `photo_events(conn, *, file_ids, clustering) -> Mapping[str, str]`;
  `media_type(conn, *, file_id, content_hash, tier_weight, minimum_score, minimum_margin) -> str | None`.

> **Addition to the skeleton's `Produces:` line, declared.** The skeleton names three: `photo_events`,
> `media_type`, `PhotoEventClustering`. The six constants above are added because §2.6's two
> hypotheses, §4.2's three inputs and the two field keys are each a spelling that would otherwise
> live twice — once in the module and once in the test — and P6's standing rule is that a closed
> vocabulary has one home. Nothing named by the skeleton is renamed or re-typed.

**Done-means:** 26, 27. **Adversarial case:** A07.

**§4.2, quoted, because it is the only sentence in the design that states this fact exists:**

> For a photo group, it might be a deterministic event created from camera, time, and GPS metadata.

**§2.6, quoted in full for the hierarchy, because every clause of it decides something below:**

> The system should therefore use a hierarchy of signals: camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact display resolutions, PNG format, and software metadata may support a screenshot hypothesis; conflicting signals should lead to abstention rather than an invented classification.

**§2.6 again, the sentence that makes the tier-3-only case a refusal rather than a conclusion:**

> However, the system must not mistake the absence of EXIF for proof that an image is a screenshot. Messaging platforms and downloaded web images often strip metadata from real photographs. OCR text density is also not a reliable screenshot detector because receipts, document scans, whiteboards, and photographs of pages can all contain dense text.

**The tier is read, never re-derived (M2).** `Observation.signal_tier` carries §2.6's hierarchy
because P4 put it there for exactly this consumer, and the skeleton's Global Constraints are
explicit: *"`signal_tier` comes from P4's observation and is never recomputed from `extractor_name`
or a field label — that would encode §2.6 in a second place (M2)."* So this module branches on the
integer and on nothing else. An observation P5 left untiered contributes to nothing, and the test
below drives that case with an observation carrying a camera label, the image extractor's name, and
`signal_tier = None`: it produces no event and no vote.

**The bands are read off P4's published order, not re-spelled.** `SIGNAL_TIERS == (1, 2, 3)` and
§2.6's three bands arrive in that order, so `SCREENSHOT_BAND = SIGNAL_TIERS[-1:]` and
`PHOTO_BANDS = SIGNAL_TIERS[:-1]`. That is a reading of a published tuple — the same technique the
cache-key rule applies to `ANALYSIS_TIERS` — and it is not decoration: `extractors/ocr_policy.py`
already reads the same split as `USABLE_METADATA_TIERS = frozenset({1, 2})`, so a literal `3` here
would be P6's copy of a boundary that exists in two places already. Both constants are **tuples**,
because Task 25 introspects every module namespace for a bare `int` or `float` and a band index is
not a threshold but is indistinguishable from one at run time.

**P5 spells the EXIF tag names and P6 holds no copy.** The skeleton's P5 table is explicit that a
camera / capture-time / GPS observation's container-path label is *"the reader-supplied tag name,
which P5 deliberately never spells"*. So the labels arrive inside `PhotoEventClustering.labels`,
keyed by `EVENT_INPUTS`, with no default — the same shape Task 14 uses for the perceptual-hash
label, and the same reason.

**The event is `validated`, and both boundaries are load-bearing.** Not `direct`: no explicit slot
states an event, and §3.13 reserves `direct` for a value read out of a reliable slot. Not
`possible`: P9 requires a seed fact to be Direct or Validated, so a `possible` event is a seed P9 can
never use and G7 would deliver nothing. `validated` is §3.13's own definition — a deterministic rule
that passes a contextual check — and the contextual check is the injected `same_event` predicate
agreeing that two files' camera, capture-time and GPS readings describe one occasion.

**A photograph with no EXIF gets no event and no `unresolved` row.** Same reading Tasks 14 and 15
apply: the SPEC's `unresolved` schema records *"the field that was attempted"*, and a file that
offered none of §4.2's three inputs was never proposed into a cluster. Recording it would make the
abstention table a list of every image in the corpus.

**`media_type` is the ordinary §3.7 procedure and not a new mechanism.** The SPEC is explicit:
*"Resolution is the ordinary §3.7 procedure over the `media type` field: each tiered observation is a
weighted vote for one candidate (`photograph` or `screenshot`), the candidates are ranked, and the
winner must clear both the minimum score and the minimum margin."* So this module builds candidates
and hands them to Task 11's `fill_or_abstain`, which owns the ranking, the two thresholds and the
`below_margin` / `below_score_threshold` rows. The tier-to-weight mapping is injected; §3.7's numbers
are Deferred and the SPEC files these with them (*"The tier-to-weight mapping is deferred with the
other §3.7 weights"*).

**The one rule §3.7's arithmetic cannot reach, stated rather than smuggled.** A file whose only
tiered observations are in the screenshot band fills nothing and gets `reason = below_margin`,
**before** any ranking runs. This is the single place Task 16 states a rule the injected thresholds
could otherwise override, so here is the whole argument:

- A07 is a P6 gate case (`dimension: "fact"`), its `expected_outcome_kind` is `"abstained"` and its
  `forbidden_value` is `{"field": "media_type", "value": "screenshot"}` — verified in
  `tests/eval/fixtures/adversarial/A07.json`. Its subject is a real photograph a messaging app
  stripped, which therefore carries only what every image carries.
- Left to the arithmetic, that file has one candidate (`screenshot`) and no second-best, so it clears
  any margin the caller injects and A07's forbidden value is produced. The outcome would depend on a
  Deferred number, which is not what a Done-means-grade prohibition may rest on.
- §2.6 states the prohibition directly and unconditionally — *"must not mistake the absence of EXIF
  for proof that an image is a screenshot"* — and the screenshot band is, in
  `ocr_policy`'s own words, *"what every image has"*. Evidence every image carries separates the two
  hypotheses by nothing, and a separation of nothing clears no margin.
- `below_margin` is the SPEC's own home for this: its reason table reads *"§3.7 margin over
  second-best not cleared — **including the conflicting-image-signal case (§2.6)**"*. It is not
  `no_candidate_evidence`, because there is a candidate and its observations are cited on the row.

**A missing signal contributes nothing to either candidate, and that is provable rather than
asserted.** P5 records "no EXIF" on `ExtractionRun.completeness` or nowhere — P4's `runs.py` says so
and conformance rule 12 enforces it — so no absence observation exists for this module to read. Every
candidate's score is a sum over observations that are present; there is no branch anywhere that
subtracts for one that is not.

**OCR text density is never a screenshot signal.** §2.6 rules it out by name. The guard is
structural rather than behavioural: this module imports nothing from `evidence_shape.store`, never
calls `unit_for_observation`, and holds no identifier containing `text` or `unit`. The test asserts
that by parsing the module, and pairs it with the behavioural case — an image with a large OCR text
unit and one tier-1 camera reading is still `photograph`.

**The event's name is a digest.** Consistent with Tasks 14 and 15 and for the same reason: an event
identifier built from a folder, a filename or a timestamp would put a path fragment or an
unvalidated parse inside a value. The canonical value is
`sha256_of(canonical_json(sorted(member file ids)))` — deterministic, member-derived, carrying
nothing about where the photographs sat. Adding a member renames the event, which is stated rather
than hidden.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_photo_event.py
"""G7 — Done-means 26 and 27. §4.2's deterministic event, §2.6's hierarchy, A07."""
from __future__ import annotations

import ast
import dataclasses
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import SIGNAL_TIERS

from facts import photo_event
from facts.file_facts import facts_for_file
from facts.photo_event import (
    EVENT_FIELD, EVENT_INPUTS, EVENT_STATE, MEDIA_TYPES, MEDIA_TYPE_FIELD,
    PHOTO_BANDS, SCREENSHOT_BAND, PhotoEventClustering, media_type, photo_events,
)
from facts.states import is_stronger
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-19T12:00:00+00:00"

#: P5 spells the tag names; P6 injects them. The test is the only place they meet.
LABELS = {
    "camera": frozenset({"Make", "Model"}),
    "capture_time": frozenset({"DateTimeOriginal"}),
    "location": frozenset({"GPSLatitude", "GPSLongitude"}),
}

#: Every number below is the TEST's. §4.2 names the inputs and states no thresholds.
WEIGHTS = {SIGNAL_TIERS[0]: 8.0, SIGNAL_TIERS[1]: 4.0, SIGNAL_TIERS[2]: 7.5}


def _identifiers(module) -> set[str]:
    """Every name and attribute this module's CODE mentions.

    An AST walk, not a source-text search: a text search matches comments and
    docstrings, and a guard that does that has broken three tasks on this project
    already (P5 PLAN, Task 20). §2.6 rules OCR text density out by name, so the
    assertion is that nothing here can reach a text unit at all.
    """
    tree = ast.parse(inspect.getsource(module))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update(alias.name for alias in node.names)
            names.add(getattr(node, "module", "") or "")
    return names


def _record(conn, tmp_path, *, name, body):
    """One P1 `files` row over real bytes, so the content hash is P1's own."""
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Photos", mime_type="image/jpeg",
        detected_format="jpeg", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, label, signal_tier,
             extractor="image.metadata", zone="metadata", source_type="image",
             analysis_tier="native", text_units=()):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version="1.0.0",
        source_type=source_type, analysis_tier=analysis_tier, config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version="1.0.0", source_type=source_type, raw_value=raw,
        location=Location(zone, (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="direct",
        run_id=run_id, signal_tier=signal_tier)
    record_observation(conn, observation)
    return observation.observation_key


def _photo(conn, tmp_path, *, name, body, camera="Canon EOS R5",
           stamp="2026:07:04 11:02:13", gps="40.7128", tier_three=None):
    """One image with §4.2's three inputs, each at the band §2.6 gives it."""
    file_id, content_hash = _record(conn, tmp_path, name=name, body=body)
    _observe(conn, run_id=f"{name}-cam", file_id=file_id, content_hash=content_hash,
             raw=camera, label="Make", signal_tier=SIGNAL_TIERS[0])
    _observe(conn, run_id=f"{name}-time", file_id=file_id, content_hash=content_hash,
             raw=stamp, label="DateTimeOriginal", signal_tier=SIGNAL_TIERS[1])
    _observe(conn, run_id=f"{name}-gps", file_id=file_id, content_hash=content_hash,
             raw=gps, label="GPSLatitude", signal_tier=SIGNAL_TIERS[1])
    if tier_three is not None:
        _observe(conn, run_id=f"{name}-shot", file_id=file_id,
                 content_hash=content_hash, raw=tier_three, label="PixelWidth",
                 signal_tier=SIGNAL_TIERS[2])
    return file_id, content_hash


def _same_camera_and_day(left, right) -> bool:
    """The injected contextual check. §4.2 names the inputs and states no window."""
    return (left["camera"] == right["camera"]
            and bool(left["capture_time"]) and bool(right["capture_time"])
            and left["capture_time"][0][:10] == right["capture_time"][0][:10])


CLUSTERING = PhotoEventClustering(labels=LABELS, same_event=_same_camera_and_day,
                                  minimum_members=2)


def _event_rows(conn, file_id, content_hash):
    return [r for r in facts_for_file(conn, file_id, content_hash)
            if r["field_key"] == EVENT_FIELD]


@pytest.fixture()
def one_event(p6_conn, tmp_path):
    left = _photo(p6_conn, tmp_path, name="IMG_0101.jpg", body=b"pixels-one")
    right = _photo(p6_conn, tmp_path, name="IMG_0102.jpg", body=b"pixels-two",
                   stamp="2026:07:04 11:04:52", gps="40.7130")
    return left, right


def test_a_camera_time_and_gps_cluster_is_a_validated_event(one_event, p6_conn):
    # Done-means 26, and §4.2's "a deterministic event created from camera, time,
    # and GPS metadata".
    (left, left_hash), (right, right_hash) = one_event
    written = photo_events(p6_conn, file_ids=(left, right), clustering=CLUSTERING)
    assert set(written) == {left, right}
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        rows = _event_rows(p6_conn, file_id, digest)
        assert len(rows) == 1
        assert rows[0]["reliability_state"] == EVENT_STATE
        assert json.loads(rows[0]["evidence_refs"])       # M14: cited, and non-empty
        assert all(ref.startswith("sha256:")
                   for ref in json.loads(rows[0]["evidence_refs"]))


def test_the_event_state_is_never_direct_and_never_possible():
    # Not `direct`: no explicit slot states an event. Not `possible`: P9 requires a
    # seed fact to be Direct or Validated, so a `possible` event is unusable as one.
    assert is_stronger("direct", EVENT_STATE)
    assert is_stronger(EVENT_STATE, "possible")


def test_an_image_with_no_exif_produces_no_event_and_no_row(p6_conn, tmp_path):
    # Done-means 26. §2.6: absence is never evidence, and P5 writes no absence
    # observation for this module to read. Nothing was proposed, so nothing refused.
    left, left_hash = _record(p6_conn, tmp_path, name="stripped.jpg", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="stripped2.jpg", body=b"two")
    assert photo_events(p6_conn, file_ids=(left, right),
                        clustering=CLUSTERING) == {}
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        assert facts_for_file(p6_conn, file_id, digest) == []
        assert unresolved_for_file(p6_conn, file_id, digest) == []


def test_a_tier_three_signal_never_contributes_to_an_event(p6_conn, tmp_path):
    # §2.6 puts exact display resolutions, PNG format and software metadata in the
    # screenshot-hypothesis band. §4.2's event is built from the other two bands.
    left, left_hash = _record(p6_conn, tmp_path, name="a.png", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="b.png", body=b"two")
    for file_id, digest, run in ((left, left_hash, "l"), (right, right_hash, "r")):
        # A tier-3 reading that carries a CAMERA label: the label is not what is
        # read, the tier is (M2).
        _observe(p6_conn, run_id=f"{run}-shot", file_id=file_id,
                 content_hash=digest, raw="Canon EOS R5", label="Make",
                 signal_tier=SIGNAL_TIERS[2])
    assert photo_events(p6_conn, file_ids=(left, right),
                        clustering=CLUSTERING) == {}
    assert _event_rows(p6_conn, left, left_hash) == []


def test_a_tier_is_read_from_the_observation_and_never_re_derived(p6_conn, tmp_path):
    # M2, stated in the skeleton's Global Constraints: `signal_tier` "comes from P4's
    # observation and is never recomputed from `extractor_name` or a field label".
    # These two rows carry the image extractor's name AND a camera label AND no tier.
    left, left_hash = _record(p6_conn, tmp_path, name="untiered1.jpg", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="untiered2.jpg", body=b"two")
    for file_id, digest, run in ((left, left_hash, "l"), (right, right_hash, "r")):
        _observe(p6_conn, run_id=f"{run}-cam", file_id=file_id, content_hash=digest,
                 raw="Canon EOS R5", label="Make", signal_tier=None)
        _observe(p6_conn, run_id=f"{run}-time", file_id=file_id, content_hash=digest,
                 raw="2026:07:04 11:02:13", label="DateTimeOriginal",
                 signal_tier=None)
    assert photo_events(p6_conn, file_ids=(left, right),
                        clustering=CLUSTERING) == {}
    assert media_type(p6_conn, file_id=left, content_hash=left_hash,
                      tier_weight=WEIGHTS, minimum_score=1.0,
                      minimum_margin=1.0) is None
    rows = unresolved_for_file(p6_conn, left, left_hash,
                               field_key=MEDIA_TYPE_FIELD)
    assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


def test_a_cluster_below_the_injected_minimum_is_not_an_event(p6_conn, tmp_path):
    # §4.2 uses the event as a GROUP seed; how many photographs make one is deferred
    # with the time window and the GPS radius, so it is injected.
    only, only_hash = _photo(p6_conn, tmp_path, name="alone.jpg", body=b"one")
    assert photo_events(p6_conn, file_ids=(only,), clustering=CLUSTERING) == {}
    assert _event_rows(p6_conn, only, only_hash) == []
    assert unresolved_for_file(p6_conn, only, only_hash) == []


def test_tier_one_and_tier_three_in_conflict_fill_no_media_type(p6_conn, tmp_path):
    # Done-means 27, and §2.6's "conflicting signals should lead to abstention rather
    # than an invented classification" — reached by the ordinary §3.7 margin, with
    # weights the TEST injects, and not by a mechanism this module owns.
    file_id, content_hash = _record(p6_conn, tmp_path, name="conflict.png",
                                    body=b"pixels")
    _observe(p6_conn, run_id="c-cam", file_id=file_id, content_hash=content_hash,
             raw="Canon EOS R5", label="Make", signal_tier=SIGNAL_TIERS[0])
    _observe(p6_conn, run_id="c-shot", file_id=file_id, content_hash=content_hash,
             raw="2560x1440", label="PixelWidth", signal_tier=SIGNAL_TIERS[2])
    assert media_type(p6_conn, file_id=file_id, content_hash=content_hash,
                      tier_weight=WEIGHTS, minimum_score=1.0,
                      minimum_margin=2.0) is None
    rows = unresolved_for_file(p6_conn, file_id, content_hash,
                               field_key=MEDIA_TYPE_FIELD)
    assert [r["reason"] for r in rows] == ["below_margin"]


def test_stripped_exif_never_becomes_a_screenshot(p6_conn, tmp_path):
    # A07, verbatim from tests/eval/fixtures/adversarial/A07.json: outcome
    # `abstained`, forbidden value {"field": "media_type", "value": "screenshot"}.
    # §2.6: "must not mistake the absence of EXIF for proof that an image is a
    # screenshot." The margin is injected at zero, so the arithmetic alone would
    # have produced the forbidden value.
    file_id, content_hash = _record(p6_conn, tmp_path, name="whatsapp.jpg",
                                    body=b"a real photograph, stripped")
    _observe(p6_conn, run_id="a-shot", file_id=file_id, content_hash=content_hash,
             raw="1170x2532", label="PixelWidth", signal_tier=SIGNAL_TIERS[2])
    _observe(p6_conn, run_id="a-fmt", file_id=file_id, content_hash=content_hash,
             raw="PNG", label="Format", signal_tier=SIGNAL_TIERS[2])
    assert media_type(p6_conn, file_id=file_id, content_hash=content_hash,
                      tier_weight=WEIGHTS, minimum_score=0.0,
                      minimum_margin=0.0) is None
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash,
                               field_key=MEDIA_TYPE_FIELD)
    assert [r["reason"] for r in rows] == ["below_margin"]
    # The refusal cites what it looked at; a refusal with no record is not inspectable.
    assert len(json.loads(rows[0]["evidence_refs"])) == 2


def test_a_missing_signal_contributes_nothing_to_either_candidate(p6_conn, tmp_path):
    # Done-means 27. Provable precisely because P5 writes no absence observation:
    # the file with one reading and the file with three reach the same conclusion,
    # and the two the first one lacks moved neither candidate.
    lean, lean_hash = _record(p6_conn, tmp_path, name="lean.jpg", body=b"one")
    _observe(p6_conn, run_id="lean-cam", file_id=lean, content_hash=lean_hash,
             raw="Canon EOS R5", label="Make", signal_tier=SIGNAL_TIERS[0])
    full, full_hash = _photo(p6_conn, tmp_path, name="full.jpg", body=b"two")
    for file_id, digest in ((lean, lean_hash), (full, full_hash)):
        assert media_type(p6_conn, file_id=file_id, content_hash=digest,
                          tier_weight=WEIGHTS, minimum_score=1.0,
                          minimum_margin=1.0) is not None
        row = [r for r in facts_for_file(p6_conn, file_id, digest)
               if r["field_key"] == MEDIA_TYPE_FIELD][0]
        assert row["canonical_value"] == MEDIA_TYPES[0]
        assert unresolved_for_file(p6_conn, file_id, digest,
                                   field_key=MEDIA_TYPE_FIELD) == []


def test_ocr_text_density_is_never_a_screenshot_signal(p6_conn, tmp_path):
    # §2.6: "OCR text density is also not a reliable screenshot detector because
    # receipts, document scans, whiteboards, and photographs of pages can all contain
    # dense text." Structural first: nothing here can reach a text unit at all.
    mentioned = _identifiers(photo_event)
    assert not [name for name in mentioned
                if "text" in name.lower() or "unit" in name.lower()]
    assert "evidence_shape.store" not in mentioned
    # And behaviourally: a page photographed at close range, dense with text.
    file_id, content_hash = _record(p6_conn, tmp_path, name="whiteboard.jpg",
                                    body=b"pixels")
    _observe(p6_conn, run_id="w-cam", file_id=file_id, content_hash=content_hash,
             raw="Canon EOS R5", label="Make", signal_tier=SIGNAL_TIERS[0])
    _observe(p6_conn, run_id="w-ocr", file_id=file_id, content_hash=content_hash,
             raw="lecture notes " * 400, label="ocr_text", signal_tier=None,
             extractor="ocr.vision", zone="ocr", source_type="ocr",
             analysis_tier="ocr")
    assert media_type(p6_conn, file_id=file_id, content_hash=content_hash,
                      tier_weight=WEIGHTS, minimum_score=1.0,
                      minimum_margin=1.0) is not None
    row = [r for r in facts_for_file(p6_conn, file_id, content_hash)
           if r["field_key"] == MEDIA_TYPE_FIELD][0]
    assert row["canonical_value"] == MEDIA_TYPES[0]


def test_the_clustering_and_the_weights_are_injected_with_no_defaults():
    # §4.2 names the inputs and states no time window, no GPS radius and no
    # camera-identity test; §3.7's weights are Deferred. None is here.
    fields = dataclasses.fields(PhotoEventClustering)
    assert [f.name for f in fields] == ["labels", "same_event", "minimum_members"]
    for field in fields:
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING
    signature = inspect.signature(media_type)
    for name in ("tier_weight", "minimum_score", "minimum_margin"):
        parameter = signature.parameters[name]
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        assert parameter.default is inspect.Parameter.empty
    clustering = inspect.signature(photo_events).parameters["clustering"]
    assert clustering.default is inspect.Parameter.empty
    # Task 25's technique: runtime introspection of the namespace, not a text search.
    numbers = {name: value for name, value in vars(photo_event).items()
               if isinstance(value, (int, float)) and not isinstance(value, bool)}
    assert numbers == {}
    # The bands are P4's published order, read — not P6's copy of it.
    assert PHOTO_BANDS == SIGNAL_TIERS[:-1]
    assert SCREENSHOT_BAND == SIGNAL_TIERS[-1:]
    assert EVENT_INPUTS == ("camera", "capture_time", "location")
    assert set(LABELS) == set(EVENT_INPUTS)


def test_the_result_does_not_depend_on_the_order_the_file_ids_arrive_in(
        one_event, p6_conn):
    # P4's reads are in insertion order and P6 must not inherit it (Global
    # Constraints). Two orders, one outcome, compared as sets of stored rows.
    (left, left_hash), (right, right_hash) = one_event
    forward = photo_events(p6_conn, file_ids=(left, right), clustering=CLUSTERING)
    reverse = photo_events(p6_conn, file_ids=(right, left), clustering=CLUSTERING)
    assert set(forward) == set(reverse) == {left, right}

    def shape(written):
        return sorted(
            (r["file_id"], r["reliability_state"], r["canonical_value"],
             r["evidence_refs"])
            for file_id, digest in ((left, left_hash), (right, right_hash))
            for r in _event_rows(p6_conn, file_id, digest)
            if r["fact_id"] in set(written.values()))

    assert shape(forward) == shape(reverse)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_photo_event.py -v`
Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.photo_event'`

- [ ] **Step 3: Write `photo_event.py`**

```python
# src/facts/photo_event.py
"""G7 — §4.2's deterministic photo event, and §2.6's media-type conflict (M2).

§4.2, the only sentence in the design that states this fact exists:

    "For a photo group, it might be a deterministic event created from camera, time,
     and GPS metadata."

§2.6, the hierarchy this module READS and never rebuilds:

    "camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped
     dimensions reinforce it; exact display resolutions, PNG format, and software
     metadata may support a screenshot hypothesis; conflicting signals should lead to
     abstention rather than an invented classification."

**The tier is read, never re-derived (M2).** P4 puts `signal_tier` on the observation
for exactly this consumer, so this module branches on the integer and on nothing else
-- not on `extractor_name`, not on the container-path label. An observation P5 left
untiered contributes to nothing. Deriving the band from a name would encode §2.6 in a
second place, which is the defect M2 exists to prevent.

**The bands are P4's published order, read.** `SIGNAL_TIERS == (1, 2, 3)` and §2.6's
three bands arrive in that order, so the screenshot band is `SIGNAL_TIERS[-1:]` and
the photo bands are the rest. `extractors/ocr_policy.py` already reads the same split
as `USABLE_METADATA_TIERS`; a literal `3` here would be a third home for one boundary.
Both are tuples rather than ints because a band index is not a threshold and must not
look like one to Task 25's namespace introspection.

**P5 spells the EXIF tag names and this module holds no copy.** The tag name a
container-path label carries is "the reader-supplied tag name, which P5 deliberately
never spells", so the labels arrive inside the injected `PhotoEventClustering`.

**The event is `validated`.** Not `direct` -- no explicit slot states an event. Not
`possible` -- P9 requires a seed fact to be Direct or Validated, so a `possible` event
is a seed P9 can never use and G7 would deliver nothing.

**`media_type` is the ordinary §3.7 procedure.** Each tiered observation is one
weighted vote, the candidates are ranked by `facts.facets.fill_or_abstain`, and that
function owns the two thresholds and the `below_margin` row. One rule is applied
BEFORE the ranking, and it is the only rule here the injected numbers cannot override:
a file whose only tiered observations are in the screenshot band fills nothing.
§2.6 -- "the system must not mistake the absence of EXIF for proof that an image is a
screenshot" -- and the screenshot band is what every image carries, so it separates
the two hypotheses by nothing. `below_margin` is the SPEC's own home for §2.6's
abstention: "margin over second-best not cleared -- including the
conflicting-image-signal case (§2.6)".

**OCR text density is never a signal here.** §2.6 rules it out by name, and this
module imports nothing from `evidence_shape.store` and holds no identifier that could
reach a text unit.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Iterable, Mapping

from database_agent.files_table import get_file

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS, SIGNAL_TIERS, check

from facts.cache import fact_cache_key
from facts.evidence import analysis_tier_for_observation, cite, observations_for_version
from facts.facets import Candidate, fill_or_abstain
from facts.file_facts import FACT_ORIGINS, write_fact, RULE
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: §3.11's Photos fields, snake_case per D6. Both already exist in the catalogue, so
#: this module creates no field: §3.12 lets values auto-create and fields never.
EVENT_FIELD: str = "event"
MEDIA_TYPE_FIELD: str = "media_type"

#: §3.13's definition of `validated` -- a deterministic rule that passes a contextual
#: check -- and the contextual check is the injected `same_event` predicate.
EVENT_STATE: str = "validated"

#: §4.2's three inputs, in §4.2's order: "camera, time, and GPS metadata". These are
#: the KEYS the injected label sets arrive under, not the labels themselves.
EVENT_INPUTS: tuple[str, str, str] = ("camera", "capture_time", "location")

#: §2.6's two hypotheses, photograph first. There is no third and no "unknown"
#: member: not filling the field IS the third outcome, and it is a row (B7).
MEDIA_TYPES: tuple[str, str] = ("photograph", "screenshot")

#: §2.6's three bands, read off P4's published order rather than re-spelled. Tuples,
#: not ints: a band index is not a threshold and must not look like one to Task 25.
PHOTO_BANDS: tuple[int, ...] = SIGNAL_TIERS[:-1]
SCREENSHOT_BAND: tuple[int, ...] = SIGNAL_TIERS[-1:]


@dataclass(frozen=True)
class PhotoEventClustering:
    """§4.2's three inputs, and the thresholds the design states for none of them.

    Every field is required and none has a default.

    `labels` maps each member of `EVENT_INPUTS` to the container-path labels P5's
    reader used for that input. P5 spells the EXIF tag names and this module holds no
    copy, so the mapping is the injection site and `EVENT_INPUTS` is its one address.

    `same_event` receives two files' signal mappings -- each `{kind: sorted raw
    values}` over `EVENT_INPUTS` -- and answers whether they describe one occasion.
    The time window, the GPS radius and the camera-identity test are Deferred
    together; they arrive as this one predicate rather than as three numbers.

    `minimum_members` is how many photographs make an event. §4.2 uses the event as a
    GROUP seed and states no count, so the count is the caller's.
    """
    labels: Mapping[str, frozenset[str]]
    same_event: Callable[[Mapping[str, tuple[str, ...]],
                          Mapping[str, tuple[str, ...]]], bool]
    minimum_members: int

    def __post_init__(self) -> None:
        for kind in EVENT_INPUTS:
            check(kind, self.labels, name="event input")


@dataclass(frozen=True)
class _Photo:
    """One (file, content hash) with its §4.2 inputs already read once."""
    file_id: str
    content_hash: str
    observations: tuple[Observation, ...]
    cited: tuple[Observation, ...]
    signals: Mapping[str, tuple[str, ...]]

    @property
    def offered(self) -> bool:
        """Did this file offer any of §4.2's three inputs at all?"""
        return any(self.signals[kind] for kind in EVENT_INPUTS)


def _read(conn: sqlite3.Connection, file_ids: Iterable[str],
          clustering: PhotoEventClustering) -> tuple[_Photo, ...]:
    """Every version, in file-id order, with its signals resolved.

    Sorted before anything is decided. P4's reads are in insertion order (verified by
    execution) and insertion order is a property of one database, not of the corpus.
    """
    photos: list[_Photo] = []
    for file_id in sorted(set(file_ids)):
        row = dict(get_file(conn, file_id))
        content_hash = row["content_hash"]
        observations = tuple(observations_for_version(conn, file_id, content_hash))
        signals: dict[str, tuple[str, ...]] = {}
        cited: dict[str, Observation] = {}
        for kind in EVENT_INPUTS:
            labels = clustering.labels[kind]
            readings = tuple(
                one for one in observations
                if one.signal_tier in PHOTO_BANDS
                and any(segment.label in labels
                        for segment in one.location.container_path))
            signals[kind] = tuple(sorted(one.raw_value for one in readings))
            for one in readings:
                cited[cite(one)] = one
        photos.append(_Photo(
            file_id=file_id, content_hash=content_hash, observations=observations,
            cited=tuple(cited[key] for key in sorted(cited)), signals=signals))
    return tuple(photos)


def _cache_key(conn: sqlite3.Connection, *, content_hash: str,
               observations: Iterable[Observation]) -> str:
    """§3.4's five parts for a fact built from several observations.

    §3.4 states one extractor version and one analysis tier; a fact citing several
    observations has several of each, and no task owns the reconciliation. The rule
    is written out here rather than shared because `facts.cache` is another task's
    module: the versions are the canonical JSON of the sorted distinct
    (name, version) pairs, and the tier is the LAST one present in `ANALYSIS_TIERS`
    order -- filesystem < native < ocr < llm -- so a fact that cited an `ocr` reading
    lands outside the cache slot the native pass computed under, which is what makes
    preamble rule 5's pass 4 supersede rather than overwrite.
    """
    observations = tuple(observations)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in observations})
    tiers = {analysis_tier_for_observation(conn, one) for one in observations}
    tier = max(tiers, key=ANALYSIS_TIERS.index) if tiers else ANALYSIS_TIERS[0]
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=tier, model_identifier=None, prompt_fingerprint=None)


def photo_events(conn: sqlite3.Connection, *, file_ids: Iterable[str],
                 clustering: PhotoEventClustering) -> Mapping[str, str]:
    """Done-means 26. `file_id -> fact_id` for every member of a photo event.

    An image that offered none of §4.2's three inputs gets no fact AND no `unresolved`
    row: the abstention record names "the field that was attempted", and a file that
    proposed nothing was never attempted. Recording it would make the abstention table
    a list of every image in the corpus.
    """
    photos = _read(conn, file_ids, clustering)
    by_id = {photo.file_id: photo for photo in photos}
    offered = sorted(photo.file_id for photo in photos if photo.offered)
    parent = {file_id: file_id for file_id in offered}

    def find(file_id: str) -> str:
        while parent[file_id] != file_id:
            parent[file_id] = parent[parent[file_id]]
            file_id = parent[file_id]
        return file_id

    for left, right in combinations(offered, 2):
        if clustering.same_event(by_id[left].signals, by_id[right].signals):
            parent[find(left)] = find(right)

    components: dict[str, list[str]] = {}
    for file_id in offered:
        components.setdefault(find(file_id), []).append(file_id)

    written: dict[str, str] = {}
    for members in sorted(components.values()):
        if len(members) < clustering.minimum_members:
            continue
        canonical_value = sha256_of(canonical_json(sorted(members)))
        for file_id in members:
            photo = by_id[file_id]
            refs = tuple(sorted(cite(one) for one in photo.cited))
            value_id = ensure_value(
                conn, field_key=EVENT_FIELD, canonical_value=canonical_value,
                first_evidence_ref=refs[0], origin=VALUE_ORIGINS[0])
            written[file_id] = write_fact(
                conn, file_id=file_id, content_hash=photo.content_hash,
                field_key=EVENT_FIELD, value_id=value_id,
                reliability_state=EVENT_STATE, origin=RULE,
                evidence_refs=refs,
                cache_key=_cache_key(conn, content_hash=photo.content_hash,
                                     observations=photo.cited),
                active=True)
    return written


def _abstain(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
             reason: str, considered: tuple[Observation, ...]) -> None:
    """B7: a refusal is a row naming the field, the reason, and what it looked at."""
    write_unresolved(
        conn, file_id=file_id, content_hash=content_hash,
        field_key=MEDIA_TYPE_FIELD, reason=reason,
        attempted_producers=(ATTEMPTED_PRODUCERS[1],),
        evidence_refs=tuple(sorted(cite(one) for one in considered)),
        cache_key=_cache_key(conn, content_hash=content_hash,
                             observations=considered))


def media_type(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
               tier_weight: Mapping[int, float], minimum_score: float,
               minimum_margin: float) -> str | None:
    """Done-means 27. §2.6's two hypotheses, ranked by §3.7's ordinary procedure.

    Every tiered observation is one weighted vote: the screenshot band votes
    `screenshot`, every other band votes `photograph`. The weights are injected --
    §3.7's numbers are Deferred and the SPEC files the tier-to-weight mapping with
    them -- and the ranking, the score floor, the margin and the two refusal rows they
    produce all belong to `facts.facets.fill_or_abstain`.

    Two refusals happen here rather than there, and each is a sentence of §2.6:

    * no tiered observation at all -> `no_candidate_evidence`. Nothing was read about
      this image, so there is nothing to rank and nothing to cite (rule 1).
    * only screenshot-band observations -> `below_margin`. "The system must not
      mistake the absence of EXIF for proof that an image is a screenshot", and that
      band is what EVERY image carries, so it separates the two hypotheses by nothing.
      Left to the arithmetic this file has one candidate, no second-best, and clears
      any injected margin -- which is exactly A07's forbidden value. The reason is
      §2.6's own: the SPEC files "the conflicting-image-signal case (§2.6)" under
      `below_margin`.
    """
    observations = tuple(observations_for_version(conn, file_id, content_hash))
    tiered = tuple(one for one in observations if one.signal_tier in SIGNAL_TIERS)
    if not tiered:
        _abstain(conn, file_id=file_id, content_hash=content_hash,
                 reason="no_candidate_evidence", considered=())
        return None
    if all(one.signal_tier in SCREENSHOT_BAND for one in tiered):
        _abstain(conn, file_id=file_id, content_hash=content_hash,
                 reason="below_margin", considered=tiered)
        return None

    candidates: list[Candidate] = []
    for value, band in ((MEDIA_TYPES[0], PHOTO_BANDS),
                        (MEDIA_TYPES[1], SCREENSHOT_BAND)):
        voters = tuple(one for one in tiered if one.signal_tier in band)
        if not voters:
            # A candidate with nothing to cite is not a candidate (rule 1). It is
            # also not a subtraction: a signal P5 never wrote moves neither side.
            continue
        candidates.append(Candidate(
            value=value,
            score=sum(tier_weight[one.signal_tier] for one in voters),
            evidence_refs=tuple(sorted(cite(one) for one in voters))))

    return fill_or_abstain(
        conn, file_id=file_id, content_hash=content_hash,
        field_key=MEDIA_TYPE_FIELD, candidates=tuple(candidates),
        minimum_score=minimum_score, minimum_margin=minimum_margin)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_photo_event.py -v`
Expected: PASS — 12 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/photo_event.py tests/p6/test_p6_photo_event.py
git commit -m "feat(P6): G7 photo events and the media-type conflict — the tier is read, never re-derived"
```

---

### Wave D — the seams (17–23 parallelise)

---

### Task 17: The P8 seam — what P6 supplies, and the consequence of each verdict (O6)

**Files:**
- Create: `src/facts/llm_seam.py`
- Test: `tests/p6/test_p6_llm_seam.py`

**Interfaces:**
- Consumes: `facts.domains` — `active_field_allowlist`; `facts.evidence` —
  `observations_for_version`, `cite`, `analysis_tier_for_observation`; `facts.file_facts` —
  `facts_for_file`, `write_fact`, `FACT_ORIGINS`, `FieldNotInCatalogue` (raised through
  `write_fact`); `facts.unresolved` — `write_unresolved`, `ATTEMPTED_PRODUCERS`; `facts.values` —
  `ensure_value`, `VALUE_ORIGINS`; `facts.states` — `is_stronger`; `facts.cache.fact_cache_key`;
  `evidence_shape.canonical` — `canonical_json`; `evidence_shape.vocabulary` — `ANALYSIS_TIERS`,
  `check`, `NotInVocabulary`.
- Produces (`llm_seam.py`): `FOUR_CHECKS: tuple[str, ...]`, `CHECK_REASONS: Mapping[str, str]`,
  `UNKNOWN_REASON: str`, `LLM_STATES: tuple[str, str]`, `ProposalStateRefused(ValueError)`,
  `require_llm_state(reliability_state) -> str`,
  `FactRequest(file_id, content_hash, allowlist, citable_observations, existing_facts, normalizers)`,
  `Proposal(field_key, value, citations, unknown)`, `Verdict(passed, failed_check, reason)`,
  `build_request(conn, *, file_id, content_hash, activation_signals, normalizers) -> FactRequest`,
  `apply_verdict(conn, *, request, proposal, verdict, proposal_state, model_identifier,
  prompt_fingerprint) -> str | None`.

> **Additions to the skeleton's `Produces:` line, declared.** `CHECK_REASONS`, `UNKNOWN_REASON`,
> `LLM_STATES`, `ProposalStateRefused` and `require_llm_state` are added. The first two exist because
> the check-to-reason map is a closed correspondence that would otherwise be spelled once in the
> module and once in P8; the last three exist because §3.6's *"useful but too weak"* downgrade is a
> reliability-state choice that must be enforced at a function a test can call, which is Task 15's
> `require_possible` pattern applied to the one other place a state ceiling binds. `apply_verdict`
> and `build_request` fill in the skeleton's `...` with named keywords; no name it states is renamed.

**Done-means:** 11, 12, and the P8-absent half of 17.

**§3.6, quoted in full, because the four checks and the two outcomes are all in it:**

> Every LLM-produced fact must pass a validation step before it becomes active in the database. The validator checks that the proposed field exists in the relevant domain schema, that the model’s cited quote or metadata field is actually present in the stored evidence, that the proposed value can be normalized safely, and that no stronger direct or rule-validated fact contradicts it. A model that cannot cite sufficient evidence must return unknown. A model output that is useful but too weak to establish a fact may remain a possible clue for review; it must not quietly become a folder proposal or an asserted file property.

**P6 supplies the four inputs and owns none of the checking.** `apply_verdict` takes a `Verdict` it
did not compute. That is not a convenience — it is what lets P8 be built against this shape later
without P6 being rewritten, and it is what the skeleton states. The consequence is that a **passing**
verdict over a proposal citing a key absent from the evidence still writes a fact, and the test below
drives exactly that case and asserts the fact appears. Anything else would mean P6 re-ran a check it
does not own, and the two implementations would drift.

**One floor is not left to the verdict, and it is not P6 doing P8's job.** §3.12 and §3.5 are
absolute — *"The LLM is not allowed to invent a new fact schema, create an unsupported field"* — and
the field catalogue is closed at Task 2. So a passing verdict naming a field outside the catalogue
raises `FieldNotInCatalogue` through `write_fact`, not because this module checked anything but
because there is no row to point at. The allowlist is narrower than the catalogue and *is* left to
the verdict: it is check 1's input, and check 1 is P8's.

> ## ⚠ An unresolved seam: `normalize` and `contradicts` have no owner (round 4, C-5)
>
> **This must be decided before P8 is planned. It is not closed here and this task does not pick a
> side.**
>
> P8's SPEC, under *From P6 — facts and facets (§3.1–3.14)*, names four things it receives from P6.
> Two of them are functions, quoted verbatim from `planning/parts/P8-llm-harness-validator/SPEC.md`:
>
> > - A normalizer: `normalize(field, raw_value) -> value | not_normalizable` (§3.6), including the
> >   gazetteer and word-boundary discipline (§3.7).
> > - A contradiction oracle: `contradicts(claim, existing_fact) -> bool`.
>
> And P8's own Deferred table files the same pair back the other way:
>
> > | **The `contradicts()` and normalization predicates' domain logic** | §3.6, §3.7, P6 | P8 calls them; P6 defines what contradiction means per field |
>
> P6's Task 17, meanwhile, says P6 *"supplies the four inputs and owns none of the checking"*. So
> **each part hands these two functions to the other and neither builds them.** A gap of this shape
> does not surface at integration; it surfaces when P8's validator has no `contradicts` to call and
> someone writes one in a hurry, in P8, where P6's field semantics are not available.
>
> **What this task does about it, and what it deliberately does not.**
>
> - It supplies the four *inputs*, exactly as the skeleton says: the active field allowlist, the
>   citable observation set, the existing `direct`/`validated`/`user_confirmed` facts, and the
>   per-field normalizers as **injected data the request carries**. P6 authors none of the
>   normalizers' contents — the SPEC's Deferred table already holds *"Per-field normalizers and
>   alias tables"* open, with `U Chicago → University of Chicago → UChicago` named as *"one worked
>   example, not a table"*.
> - It builds **neither** `normalize` **nor** `contradicts`. Inventing them into `facts.llm_seam`
>   would answer a live question inside an implementation, which is the failure mode this plan
>   exists to avoid, and would make the gap invisible rather than closed.
> - It **pins P6's side in code** so the gap is visible from the repository and not only from a
>   document: a test asserts that no module in `facts` publishes a `normalize` or a `contradicts`.
>   The day someone adds one, that test fails and the decision gets made deliberately.
>
> **Owed:** a ruling on which part owns `normalize(field, raw_value)` and
> `contradicts(claim, existing_fact)`, before P8 is planned. If the answer is P6, it is a new P6
> task and not an edit to this one — the request shape above is unchanged either way, because both
> functions would be called by P8 on values this request already carries.

**Five verdicts, five reasons, and no shared bucket.** `Verdict` carries `passed`, the
`failed_check` that failed, and the P6 `unresolved` reason that follows from it. The reason is
**derived** in `__post_init__` from `CHECK_REASONS`, not supplied: P6 owns the `unresolved`
vocabulary and P8 must not spell a member of it. The fifth outcome is not a check at all — an
explicit `unknown` is the model declining before anything could be validated, so `apply_verdict`
records `model_returned_unknown` and never consults the verdict. `Proposal.__post_init__` refuses an
`unknown` proposal that also carries a value or citations, so "declined" and "proposed" cannot both
be true of one record.

**The useful-but-too-weak downgrade is a ceiling at a function.** §3.6's *"may remain a possible clue
for review; it must not quietly become a folder proposal"* is a statement about every route, so
`require_llm_state` is the only gate to an LLM-origin fact and it admits exactly `llm_supported` and
`possible`. A test attempts `validated` and requires the raise. Which of the two a given proposal
earns is §3.7's score-and-margin question and is Deferred, so `proposal_state` is a required keyword
with no default — P6 states no rule for how weak "too weak" is.

**Being `possible` is what keeps it out of a folder proposal, and that is by construction.** Same
mechanism as Task 15's session: §3.6's proposal-eligible read excludes `possible` and `rejected`, so
the downgrade *is* the exclusion. There is no second switch.

**The LLM fact's cache key is the one in this file that is not all-`None`.** §3.4's five parts are
`content hash + extractor version + analysis tier + model identifier + prompt fingerprint`, and P8's
SPEC states who supplies the last two: *"P8 computes and publishes the `prompt_fingerprint` and
`model_id` that P6's cache key requires; P6 owns cache-key composition."* So both arrive as required
keywords, and `analysis_tier` is `ANALYSIS_TIERS[-1]` — `llm` — unconditionally, because an
LLM-produced fact is at the LLM tier by definition. That is what puts it in a different cache slot
from the deterministic fact over the same evidence, so re-resolution supersedes rather than
overwrites (§8.2).

**All of it runs with P8 absent.** There is no model call, no client, no configuration and no
default `propose`. The whole module is exercised with hand-authored `Verdict` fixtures, which is
Done-means 17's shape and is exactly how P5 was built against P4 fixtures.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_llm_seam.py
"""O6 — Done-means 11 and 12. What P6 hands P8, and the consequence of each verdict."""
from __future__ import annotations

import dataclasses
import importlib
import importlib.util
import inspect
import json
import pkgutil
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import ANALYSIS_TIERS, NotInVocabulary

import facts
from facts import llm_seam
from facts.domains import ActivationSignals
from facts.fields import FieldNotInCatalogue
from facts.file_facts import FACT_ORIGINS, facts_for_file, write_fact, LLM_INTERPRETATION, RULE
from facts.llm_seam import (
    CHECK_REASONS, FOUR_CHECKS, LLM_STATES, UNKNOWN_REASON, FactRequest, Proposal,
    ProposalStateRefused, Verdict, apply_verdict, build_request, require_llm_state,
)
from facts.unresolved import unresolved_for_file
from facts.values import VALUE_ORIGINS, ensure_value

CLOCK = "2026-08-19T12:00:00+00:00"
MODEL = "test-model-1"
PROMPT = "sha256:prompt-fingerprint"

#: The empty value of each declared type, used to build an `ActivationSignals` that
#: activates nothing. Task 13 owns that type's shape and this test must not hard-code
#: one it does not own, so each field is filled from its own annotation.
_EMPTY = {"tuple": (), "frozenset": frozenset(), "set": frozenset(), "dict": {},
          "Mapping": {}, "list": [], "str": "", "bool": False, "int": 0}


def _no_signals() -> ActivationSignals:
    """An `ActivationSignals` that activates no domain, built from its own fields."""
    values = {}
    for field in dataclasses.fields(ActivationSignals):
        head = str(field.type).split("[")[0].split(".")[-1].strip("'\" ")
        assert head in _EMPTY, f"ActivationSignals.{field.name}: {field.type!r}"
        values[field.name] = _EMPTY[head]
    return ActivationSignals(**values)


#: The per-field normalizers the request CARRIES. P6 authors none of their contents:
#: "Per-field normalizers and alias tables" is a Deferred row, and `U Chicago ->
#: University of Chicago -> UChicago` is "one worked example, not a table".
NORMALIZERS = {"subject": lambda raw: raw.strip()}


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, label="heading"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("heading", (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=run_id, context_before="Syllabus — ")
    record_observation(conn, observation)
    return observation.observation_key


@pytest.fixture()
def subject_file(p6_conn, tmp_path):
    """One file with one citable heading observation."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300 Syllabus, Spring 2026")
    key = _observe(p6_conn, run_id="r-1", file_id=file_id,
                   content_hash=content_hash, raw="BUSIB 4300")
    return file_id, content_hash, key


def _request(conn, subject_file) -> FactRequest:
    file_id, content_hash, _ = subject_file
    return build_request(conn, file_id=file_id, content_hash=content_hash,
                         activation_signals=_no_signals(), normalizers=NORMALIZERS)


def _apply(conn, request, proposal, verdict, *, state=LLM_STATES[0]):
    return apply_verdict(conn, request=request, proposal=proposal, verdict=verdict,
                         proposal_state=state, model_identifier=MODEL,
                         prompt_fingerprint=PROMPT)


def _reasons(conn, request, field_key=None):
    return [r["reason"] for r in unresolved_for_file(
        conn, request.file_id, request.content_hash, field_key=field_key)]


def test_the_request_carries_the_four_inputs_and_nothing_else(subject_file, p6_conn):
    # O6. The four are the active field allowlist, the citable observation set, the
    # existing stronger facts, and the per-field normalizers.
    file_id, content_hash, key = subject_file
    request = _request(p6_conn, subject_file)
    assert [f.name for f in dataclasses.fields(FactRequest)] == [
        "file_id", "content_hash", "allowlist", "citable_observations",
        "existing_facts", "normalizers"]
    assert request.file_id == file_id and request.content_hash == content_hash
    assert "subject" in request.allowlist
    assert [one.observation_key for one in request.citable_observations] == [key]
    assert request.normalizers is NORMALIZERS
    assert request.existing_facts == ()


def test_the_allowlist_is_task_thirteens_and_not_a_second_computation(
        subject_file, p6_conn):
    # §3.5: the model "may extract only fields allowed by the relevant schema". The
    # skeleton requires that to be ONE computation, so the request holds Task 13's
    # answer rather than a second reading of the catalogue.
    from facts.domains import active_field_allowlist
    file_id, content_hash, _ = subject_file
    signals = _no_signals()
    request = build_request(p6_conn, file_id=file_id, content_hash=content_hash,
                            activation_signals=signals, normalizers=NORMALIZERS)
    assert request.allowlist == active_field_allowlist(
        p6_conn, file_id=file_id, content_hash=content_hash,
        activation_signals=signals)


def test_the_request_carries_the_stronger_facts_a_contradiction_check_needs(
        subject_file, p6_conn):
    # §3.6 check 4: "no stronger direct or rule-validated fact contradicts it". P6
    # supplies the facts; whether one CONTRADICTS is not computed here (see C-5).
    file_id, content_hash, key = subject_file
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="BUSIB 4300",
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=file_id, content_hash=content_hash,
               field_key="subject", value_id=value_id,
               reliability_state="validated", origin=RULE,
               evidence_refs=(key,), cache_key="sha256:cache", active=True)
    request = _request(p6_conn, subject_file)
    assert [r["reliability_state"] for r in request.existing_facts] == ["validated"]


def test_a_citation_absent_from_evidence_produces_no_fact(subject_file, p6_conn):
    # Done-means 11, and §3.6 check 2.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=("sha256:not-in-the-store",), unknown=False)
    verdict = Verdict(passed=False, failed_check=FOUR_CHECKS[1])
    assert _apply(p6_conn, request, proposal, verdict) is None
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []
    assert _reasons(p6_conn, request) == ["citation_absent_from_evidence"]


def test_a_field_outside_the_active_schema_produces_no_fact(subject_file, p6_conn):
    # Done-means 11, and §3.6 check 1.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="event", value="Graduation",
                        citations=(subject_file[2],), unknown=False)
    verdict = Verdict(passed=False, failed_check=FOUR_CHECKS[0])
    assert _apply(p6_conn, request, proposal, verdict) is None
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []
    assert _reasons(p6_conn, request) == ["field_not_in_active_schema"]


def test_a_proposal_contradicted_by_a_stronger_fact_produces_no_fact(
        subject_file, p6_conn):
    # Done-means 11, and §3.6 check 4. The stronger fact is real and is in the
    # request; the VERDICT is the fixture, because P6 owns no contradiction oracle.
    file_id, content_hash, key = subject_file
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="BUSIB 4300",
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=file_id, content_hash=content_hash,
               field_key="subject", value_id=value_id,
               reliability_state="validated", origin=RULE,
               evidence_refs=(key,), cache_key="sha256:cache", active=True)
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="ECON 1010",
                        citations=(key,), unknown=False)
    verdict = Verdict(passed=False, failed_check=FOUR_CHECKS[3])
    assert _apply(p6_conn, request, proposal, verdict) is None
    subjects = [r for r in facts_for_file(p6_conn, file_id, content_hash)
                if r["field_key"] == "subject"]
    assert [r["canonical_value"] for r in subjects] == ["BUSIB 4300"]
    assert _reasons(p6_conn, request) == ["contradicted_by_stronger_fact"]


def test_a_value_that_cannot_be_normalized_produces_no_fact(subject_file, p6_conn):
    # §3.6 check 3: "that the proposed value can be normalized safely".
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="  ??  ",
                        citations=(subject_file[2],), unknown=False)
    verdict = Verdict(passed=False, failed_check=FOUR_CHECKS[2])
    assert _apply(p6_conn, request, proposal, verdict) is None
    assert _reasons(p6_conn, request) == ["normalization_failed"]


def test_an_explicit_unknown_is_the_model_declining_and_not_a_failed_check(
        subject_file, p6_conn):
    # §3.6: "A model that cannot cite sufficient evidence must return unknown."
    # Nothing was validated, so no verdict is consulted.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value=None, citations=(), unknown=True)
    assert _apply(p6_conn, request, proposal,
                  Verdict(passed=True, failed_check=None)) is None
    assert _reasons(p6_conn, request) == [UNKNOWN_REASON]
    assert UNKNOWN_REASON == "model_returned_unknown"
    # And "declined" and "proposed" cannot both be true of one record.
    with pytest.raises(ValueError):
        Proposal(field_key="subject", value="BUSIB 4300",
                 citations=("sha256:x",), unknown=True)


def test_five_verdicts_have_five_distinct_reasons_and_no_shared_bucket():
    assert FOUR_CHECKS == ("field_in_active_schema", "citation_present_in_evidence",
                           "value_normalizes_safely", "no_stronger_fact_contradicts")
    assert tuple(CHECK_REASONS[check] for check in FOUR_CHECKS) == (
        "field_not_in_active_schema", "citation_absent_from_evidence",
        "normalization_failed", "contradicted_by_stronger_fact")
    reasons = set(CHECK_REASONS.values()) | {UNKNOWN_REASON}
    assert len(reasons) == 5
    assert "rejected" not in reasons
    # The reason follows from the check; P8 does not spell a member of P6's
    # vocabulary, and a check outside the four is refused rather than stored.
    assert Verdict(passed=False, failed_check=FOUR_CHECKS[2]).reason == (
        "normalization_failed")
    with pytest.raises(NotInVocabulary):
        Verdict(passed=False, failed_check="vibes")
    with pytest.raises(ValueError):
        Verdict(passed=True, failed_check=FOUR_CHECKS[0])
    with pytest.raises(ValueError):
        Verdict(passed=False, failed_check=None)


def test_a_passing_verdict_writes_one_llm_supported_fact(subject_file, p6_conn):
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=(subject_file[2],), unknown=False)
    fact_id = _apply(p6_conn, request, proposal, Verdict(passed=True))
    assert fact_id is not None
    rows = [r for r in facts_for_file(p6_conn, request.file_id,
                                      request.content_hash)
            if r["field_key"] == "subject"]
    assert len(rows) == 1
    assert rows[0]["reliability_state"] == LLM_STATES[0] == "llm_supported"
    assert rows[0]["origin"] == LLM_INTERPRETATION
    assert json.loads(rows[0]["evidence_refs"]) == [subject_file[2]]
    assert unresolved_for_file(p6_conn, request.file_id,
                               request.content_hash) == []


def test_a_useful_but_too_weak_proposal_is_possible_and_never_proposal_eligible(
        subject_file, p6_conn):
    # Done-means 12. §3.6: it "may remain a possible clue for review; it must not
    # quietly become a folder proposal or an asserted file property". The exclusion
    # IS the state — §3.6's proposal-eligible read drops `possible` — so there is no
    # second switch and nothing to remember to turn off.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=(subject_file[2],), unknown=False)
    assert _apply(p6_conn, request, proposal, Verdict(passed=True),
                  state=LLM_STATES[1]) is not None
    rows = [r for r in facts_for_file(p6_conn, request.file_id,
                                      request.content_hash)
            if r["field_key"] == "subject"]
    assert [r["reliability_state"] for r in rows] == ["possible"]
    read_surface = pytest.importorskip("facts.read_surface")
    eligible = read_surface.proposal_eligible(p6_conn, file_id=request.file_id,
                                              content_hash=request.content_hash)
    assert [r["field_key"] for r in eligible] == []


def test_no_code_path_can_write_an_llm_fact_at_another_state(subject_file, p6_conn):
    # §3.6's ceiling, attempted rather than inspected — Task 15's `require_possible`
    # applied to the one other place a state ceiling binds.
    assert LLM_STATES == ("llm_supported", "possible")
    for state in LLM_STATES:
        assert require_llm_state(state) == state
    for state in ("validated", "direct", "user_confirmed", "rejected"):
        with pytest.raises(ProposalStateRefused):
            require_llm_state(state)
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=(subject_file[2],), unknown=False)
    with pytest.raises(ProposalStateRefused):
        _apply(p6_conn, request, proposal, Verdict(passed=True), state="validated")
    assert facts_for_file(p6_conn, request.file_id, request.content_hash) == []


def test_p6_owns_none_of_the_checking(subject_file, p6_conn):
    # O6, and the reason the seam is shaped this way: `apply_verdict` takes a
    # `Verdict` it did not compute, so a PASSING verdict over a proposal citing a key
    # that is not in the store still writes a fact. If P6 re-ran the check, P6 and P8
    # would each hold half a validator and they would drift.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="ANYTHING",
                        citations=("sha256:not-in-the-store",), unknown=False)
    assert _apply(p6_conn, request, proposal, Verdict(passed=True)) is not None
    rows = [r for r in facts_for_file(p6_conn, request.file_id,
                                      request.content_hash)
            if r["field_key"] == "subject"]
    assert [r["canonical_value"] for r in rows] == ["ANYTHING"]


def test_the_closed_field_catalogue_is_the_one_floor_a_verdict_cannot_lift(
        subject_file, p6_conn):
    # §3.5: the LLM "is not allowed to invent a new fact schema, create an
    # unsupported field". That is not this module checking anything — there is no row
    # to point at, so `write_fact` refuses.
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="vibe_score", value="9",
                        citations=(subject_file[2],), unknown=False)
    with pytest.raises(FieldNotInCatalogue):
        _apply(p6_conn, request, proposal, Verdict(passed=True))


def test_the_llm_fact_lands_at_the_llm_tier_with_p8s_two_values(
        subject_file, p6_conn):
    # §3.4's five parts. P8's SPEC: "P8 computes and publishes the
    # `prompt_fingerprint` and `model_id` that P6's cache key requires; P6 owns
    # cache-key composition." Both are required keywords here.
    signature = inspect.signature(apply_verdict)
    for name in ("proposal_state", "model_identifier", "prompt_fingerprint"):
        parameter = signature.parameters[name]
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        assert parameter.default is inspect.Parameter.empty
    request = _request(p6_conn, subject_file)
    proposal = Proposal(field_key="subject", value="BUSIB 4300",
                        citations=(subject_file[2],), unknown=False)
    deterministic_key = "sha256:the-native-pass-slot"
    fact_id = _apply(p6_conn, request, proposal, Verdict(passed=True))
    row = [r for r in facts_for_file(p6_conn, request.file_id,
                                     request.content_hash)
           if r["fact_id"] == fact_id][0]
    assert row["cache_key"] != deterministic_key
    assert ANALYSIS_TIERS[-1] == "llm"


def test_p6_publishes_neither_a_normalizer_nor_a_contradiction_oracle():
    """Round 4's C-5, pinned in code so the gap is visible from the repository.

    P8's SPEC names `normalize(field, raw_value) -> value | not_normalizable` and
    `contradicts(claim, existing_fact) -> bool` as things it receives FROM P6; P6's
    Task 17 says P6 owns none of the checking. Each part hands them to the other, so
    neither builds them. This task does not pick a side and does not invent them —
    it makes the day someone quietly adds one a failing test instead of a merge.
    """
    for owner in (llm_seam,):
        assert not hasattr(owner, "normalize")
        assert not hasattr(owner, "contradicts")
    for info in pkgutil.iter_modules(facts.__path__):
        module = importlib.import_module(f"facts.{info.name}")
        assert not hasattr(module, "normalize"), info.name
        assert not hasattr(module, "contradicts"), info.name


def test_the_whole_module_runs_with_p8_absent():
    # Done-means 17. No client, no model call, no configuration, no default
    # `propose`. Every verdict above was a hand-authored fixture.
    source = inspect.getsource(llm_seam)
    assert "propose" not in source
    for banned in ("http", "openai", "anthropic", "requests", "urllib", "socket"):
        assert banned not in source.lower(), banned
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_llm_seam.py -v`
Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.llm_seam'`

- [ ] **Step 3: Write `llm_seam.py`**

```python
# src/facts/llm_seam.py
"""O6 — what P6 hands P8, and the consequence of each verdict (§3.3, §3.5, §3.6).

§3.6, and every clause of it binds here:

    "Every LLM-produced fact must pass a validation step before it becomes active in
     the database. The validator checks that the proposed field exists in the relevant
     domain schema, that the model's cited quote or metadata field is actually present
     in the stored evidence, that the proposed value can be normalized safely, and
     that no stronger direct or rule-validated fact contradicts it. A model that
     cannot cite sufficient evidence must return unknown. A model output that is
     useful but too weak to establish a fact may remain a possible clue for review; it
     must not quietly become a folder proposal or an asserted file property."

**P6 supplies the four inputs and owns none of the checking.** `apply_verdict` takes a
`Verdict` it did not compute. A PASSING verdict over a proposal citing a key that is
not in the store therefore writes a fact -- deliberately, because the alternative is
P6 and P8 each holding half a validator and drifting apart. P8 can be built against
this shape without this module changing.

**One floor is not left to the verdict.** §3.5: the LLM "is not allowed to invent a
new fact schema, create an unsupported field". The field catalogue is closed, so a
passing verdict naming a field outside it raises `FieldNotInCatalogue` through
`write_fact` -- not because this module checked, but because there is no row to point
at. The ALLOWLIST is narrower than the catalogue and is check 1's input, which is
P8's.

**UNRESOLVED SEAM (round 4, C-5) -- do not close it here.** P8's SPEC names two
functions as P6's: a normalizer `normalize(field, raw_value) -> value |
not_normalizable` and a contradiction oracle `contradicts(claim, existing_fact) ->
bool`. P8's own Deferred table files their domain logic back to P6, and P6's task says
P6 owns none of the checking -- so each part hands them to the other and neither
builds them. This module supplies the four INPUTS (allowlist, citable observations,
existing stronger facts, per-field normalizers as injected data) and publishes NEITHER
function. A test asserts no module in `facts` publishes one, so the day someone adds
it, the decision gets made rather than absorbed. The ruling is owed before P8 is
planned.

**Five verdicts, five reasons, no shared bucket.** The reason is derived from the
failed check rather than supplied, because P6 owns the `unresolved` vocabulary and P8
must not spell a member of it. The fifth outcome is not a check at all: an explicit
`unknown` is the model declining before anything could be validated.

**The ceiling is a function, not a call site.** `require_llm_state` is the only gate to
an LLM-origin fact and admits exactly `llm_supported` and `possible`, so a test can
attempt the promotion and require the raise. Which of the two a proposal earns is
§3.7's score-and-margin question and is Deferred, so `proposal_state` is required with
no default.

**There is no model call here, and no default for one.** §3.3 puts every model call in
P8. `analysis_tier = "llm"` is a value recorded on a cache key, never a call.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from evidence_shape.canonical import canonical_json
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS, check

from facts.cache import fact_cache_key
from facts.domains import active_field_allowlist
from facts.evidence import cite, observations_for_version
from facts.file_facts import FACT_ORIGINS, facts_for_file, write_fact, LLM_INTERPRETATION
from facts.states import is_stronger
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: §3.6's four, in §3.6's own order. These are names for the CHECKS, which are P8's;
#: P6 publishes them so both parts address one list.
FOUR_CHECKS: tuple[str, ...] = (
    "field_in_active_schema",
    "citation_present_in_evidence",
    "value_normalizes_safely",
    "no_stronger_fact_contradicts",
)

#: The one correspondence between P8's checks and P6's `unresolved` reasons. It lives
#: here because P6 owns the reason vocabulary: a `Verdict` names the check that
#: failed, never the reason, so P8 never spells a member of P6's closed set.
CHECK_REASONS: Mapping[str, str] = {
    FOUR_CHECKS[0]: "field_not_in_active_schema",
    FOUR_CHECKS[1]: "citation_absent_from_evidence",
    FOUR_CHECKS[2]: "normalization_failed",
    FOUR_CHECKS[3]: "contradicted_by_stronger_fact",
}

#: The fifth outcome, and it is not a check: §3.6's "A model that cannot cite
#: sufficient evidence must return unknown" is the model declining before anything
#: could be validated.
UNKNOWN_REASON: str = "model_returned_unknown"

#: The only two states an LLM-origin fact may carry. §3.13 gives `llm_supported` to a
#: model conclusion that passed validation; §3.6 gives `possible` to one that is
#: "useful but too weak to establish a fact". Which of the two is §3.7's question and
#: is Deferred, so nothing here chooses between them.
LLM_STATES: tuple[str, str] = ("llm_supported", "possible")


class ProposalStateRefused(ValueError):
    """§3.6's ceiling, raised rather than documented."""


def require_llm_state(reliability_state: str) -> str:
    """The only gate to an LLM-origin fact.

    §3.6: a model output "must not quietly become a folder proposal or an asserted
    file property". That is a statement about every route, so it is enforced where
    every route has to pass rather than at the one call this module makes.
    """
    if reliability_state not in LLM_STATES:
        raise ProposalStateRefused(
            f"§3.6 admits an LLM-origin fact at {LLM_STATES!r} only; "
            f"{reliability_state!r} would give a model conclusion the standing of a "
            "directly extracted or rule-validated fact")
    return reliability_state


@dataclass(frozen=True)
class FactRequest:
    """The four inputs P6 supplies for one file version. P8 consumes; P6 checks none.

    `normalizers` is carried, not called. Per-field normalizers and alias tables are a
    Deferred row -- `U Chicago -> University of Chicago -> UChicago` is "one worked
    example, not a table" -- so P6 authors none of the contents and injects the whole
    mapping. See the C-5 note in the module docstring: `normalize` as a FUNCTION has
    no owner in either part's plan.
    """
    file_id: str
    content_hash: str
    allowlist: tuple[str, ...]
    citable_observations: tuple[Observation, ...]
    existing_facts: tuple[sqlite3.Row, ...]
    normalizers: Mapping[str, Callable[[str], Any]]


@dataclass(frozen=True)
class Proposal:
    """One thing the model said about one field, or its refusal to say anything."""
    field_key: str | None
    value: str | None
    citations: tuple[str, ...]
    unknown: bool

    def __post_init__(self) -> None:
        if self.unknown and (self.value is not None or self.citations):
            raise ValueError(
                "an `unknown` proposal is the model declining (§3.6); it carries no "
                "value and no citations, so 'declined' and 'proposed' cannot both be "
                "true of one record")
        if not self.unknown and self.value is None:
            raise ValueError("a proposal that is not `unknown` carries a value")


@dataclass(frozen=True)
class Verdict:
    """P8's answer for one proposal. P6 records the consequence and computes none.

    `reason` is DERIVED from `failed_check`, not supplied: the `unresolved` vocabulary
    is P6's and P8 must not spell a member of it.
    """
    passed: bool
    failed_check: str | None = None
    reason: str | None = field(default=None)

    def __post_init__(self) -> None:
        if self.passed and self.failed_check is not None:
            raise ValueError("a verdict that passed names no failed check")
        if not self.passed and self.failed_check is None:
            raise ValueError(
                "a verdict that failed names WHICH of §3.6's four checks failed; "
                "five verdicts carry five reasons and there is no shared bucket")
        if self.failed_check is not None:
            check(self.failed_check, FOUR_CHECKS, name="failed_check")
            object.__setattr__(self, "reason", CHECK_REASONS[self.failed_check])


def build_request(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                  activation_signals: Any,
                  normalizers: Mapping[str, Callable[[str], Any]]) -> FactRequest:
    """The four inputs, for one file version.

    The allowlist is Task 13's answer, not a second reading of the catalogue: §3.5's
    "may extract only fields allowed by the relevant schema" must be ONE computation,
    or the model is measured against one list and validated against another.

    `existing_facts` is every active fact stronger than an LLM conclusion --
    `user_confirmed`, `direct`, `validated` -- derived through `is_stronger` rather
    than listed, so §3.13's ordering has one home. These are check 4's input. Whether
    any of them CONTRADICTS a proposal is not decided here (C-5).
    """
    return FactRequest(
        file_id=file_id,
        content_hash=content_hash,
        allowlist=tuple(active_field_allowlist(
            conn, file_id=file_id, content_hash=content_hash,
            activation_signals=activation_signals)),
        citable_observations=tuple(
            observations_for_version(conn, file_id, content_hash)),
        existing_facts=tuple(
            row for row in facts_for_file(conn, file_id, content_hash)
            if is_stronger(row["reliability_state"], LLM_STATES[0])),
        normalizers=normalizers)


def _cache_key(request: FactRequest, proposal: Proposal, *, model_identifier: str,
               prompt_fingerprint: str) -> str:
    """§3.4's five parts for an LLM-produced fact.

    The tier is `ANALYSIS_TIERS[-1]` unconditionally: an LLM-produced fact is at the
    LLM tier by definition, which is what puts it in a different cache slot from the
    deterministic fact over the same evidence, so re-resolution supersedes rather than
    overwrites (§8.2).

    The versions are the canonical JSON of the sorted distinct (name, version) pairs
    of the observations the proposal CITES, on the same rule the deterministic
    producers apply, so a re-extraction still invalidates this fact. A citation that
    matches nothing contributes no pair -- this module checks citations no more here
    than anywhere else.
    """
    keys = set(proposal.citations)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in request.citable_observations if cite(one) in keys})
    return fact_cache_key(
        content_hash=request.content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=ANALYSIS_TIERS[-1],
        model_identifier=model_identifier,
        prompt_fingerprint=prompt_fingerprint)


def apply_verdict(conn: sqlite3.Connection, *, request: FactRequest,
                  proposal: Proposal, verdict: Verdict, proposal_state: str,
                  model_identifier: str, prompt_fingerprint: str) -> str | None:
    """Done-means 11 and 12. The consequence of one verdict, and never the check.

    Returns the new `fact_id`, or `None` when nothing was written -- in which case an
    `unresolved` row names the field and the reason (B7). Five outcomes, five reasons,
    no shared "rejected" bucket:

        unknown                         model_returned_unknown
        check 1 failed                  field_not_in_active_schema
        check 2 failed                  citation_absent_from_evidence
        check 3 failed                  normalization_failed
        check 4 failed                  contradicted_by_stronger_fact

    The `unknown` branch is taken BEFORE the verdict is read: the model declined, so
    there was nothing to validate and a verdict about it would be a statement nobody
    made.
    """
    cache_key = _cache_key(request, proposal, model_identifier=model_identifier,
                           prompt_fingerprint=prompt_fingerprint)

    def refuse(reason: str) -> None:
        write_unresolved(
            conn, file_id=request.file_id, content_hash=request.content_hash,
            field_key=proposal.field_key, reason=reason,
            attempted_producers=(ATTEMPTED_PRODUCERS[2],),
            evidence_refs=tuple(proposal.citations), cache_key=cache_key)

    if proposal.unknown:
        refuse(UNKNOWN_REASON)
        return None
    if not verdict.passed:
        refuse(verdict.reason)
        return None

    # The state is gated before anything is written, so a refused promotion leaves no
    # value row behind either.
    reliability_state = require_llm_state(proposal_state)
    value_id = ensure_value(
        conn, field_key=proposal.field_key, canonical_value=proposal.value,
        first_evidence_ref=proposal.citations[0] if proposal.citations else None,
        origin=VALUE_ORIGINS[0])
    return write_fact(
        conn, file_id=request.file_id, content_hash=request.content_hash,
        field_key=proposal.field_key, value_id=value_id,
        reliability_state=reliability_state, origin=LLM_INTERPRETATION,
        evidence_refs=tuple(proposal.citations), cache_key=cache_key, active=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_llm_seam.py -v`
Expected: PASS — 15 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/llm_seam.py tests/p6/test_p6_llm_seam.py
git commit -m "feat(P6): O6 the P8 seam — four inputs, five verdicts, and no checking P6 owns"
```

---

---

### Task 18: Supersession, and the `preferred` pointer (M1)

**Files:**
- Create: `src/facts/supersede.py`
- Test: `tests/p6/test_p6_supersede.py`

**Interfaces:**
- Consumes: `database_agent.supersede` — `mark_superseded`, `chain`, `SUPERSEDE_COLUMNS`;
  `facts.file_facts` — `facts_for_file`, `FILE_FACTS_COLUMNS`; `facts.fields.get_field`;
  `facts.states` — `STATES`, `is_stronger`.
- Produces (`supersede.py`): `FACT_TABLE: str`, `PreferredNeverReverses(ValueError)`,
  `SupersedeAcrossSlots(ValueError)`,
  `supersede_fact(conn, *, old_fact_id, new_fact_id, reason) -> None`,
  `preferred_fact(conn, *, file_id, field_key) -> sqlite3.Row | None`,
  `fact_history(conn, *, file_id, field_key) -> list[sqlite3.Row]`.

> **Additions to the skeleton's `Produces:` line, declared.** `FACT_TABLE` exists because P1's
> `mark_superseded` and `chain` are addressed by table *name* and that string must have one home; the
> test below asserts it names a real table carrying both the `record_id` projection and the
> `preferred` column, so a drift fails at the first run rather than at review. The two exceptions
> exist because §8.2's two invariants — *"`preferred` never reverses §3.13's ordering"* and
> supersession happens inside one slot — are enforced at a function a test can call rather than at
> the one call site this module makes. Nothing the skeleton names is renamed.

**Done-means:** 29, and the history half of 15.

**§8.2, quoted, because the whole task is one paragraph of it:**

> The product must never overwrite the evidence record merely because a later extractor or model produces a different answer. A newer result should supersede an earlier result while retaining the old observation and the reason it was superseded. For example, if a first OCR pass produces unreadable text and a later improved OCR engine recovers a university name, both extraction records should remain available. The resolver may mark the newer value as preferred, but a user reviewing a placement should still be able to inspect the origin of the conclusion.

**`preferred` is a pointer, not a strength, and the SPEC states the negative directly:**

> **`preferred` is a pointer, not a strength.** It never enters the §3.6 contradiction check, never breaks a §3.7 margin tie, and never makes a fact destination-eligible. A reader that wants strength reads `reliability_state`.

**What this module writes, and what it deliberately does not.** P1's `mark_superseded` writes three
columns across two rows — `superseded_by` and `supersede_reason` on the old, `supersedes` on the new
— and, verified by execution, **knows nothing about `preferred`**. So `preferred` is this module's
whole addition: `0` on the superseded row, `1` on the survivor, set in the same call that links them
and nowhere else in `facts`.

**No event is appended here, and that is a decision rather than an omission.** §8.2's list gives P6
two event types, `fact creation` and `fact rejection`, both spelled with a space and both already in
P1's `RESERVED_EVENT_TYPES`. Supersession is neither: §8.7 keeps a `rejected` fact rather than
removing it, so *rejection* is a state a fact carries, while supersession is one fact replacing
another — and P1 publishes three columns for exactly that, one of which is the reason §8.2 asks to be
retained. The skeleton is also explicit that `subsystem = "P6"` is written in **one** module (M8), so
an `append_event` call here would be a second home for P6's authorship. Task 4 already appends
`fact creation` when the new fact is written; this call links two rows that both already exist.

**The chain is walked backwards before it is walked forwards, because P1's `chain` only goes one
way.** Verified by execution: with `a → b → c` recorded, `chain(a)` returns `[a, b, c]` and
`chain(c)` returns `[c]`. A history read that started from the newest row would return one row and
look correct. So `fact_history` finds the tail of each chain through the `supersedes` column first,
then walks forward from there. The walk terminates without a guard because `mark_superseded` refuses
a cycle at write time — it walks the prospective chain and raises *"supersede chain would cycle"* —
so the graph on disk is acyclic by construction rather than by a second check here.

**The slot is addressed through Task 4's reader and P1's columns, never through `field_key`.** Which
column `file_facts` uses to reference the catalogue is Task 4's schema decision, and a second module
spelling it would be a second home for one decision — the defect this project pays most for. So this
module reads `file_id` and `content_hash` (both in §3's own table block), gets the live rows and
their `field_key` from `facts_for_file`, and expands each into its full history with P1's `chain`.
The four columns it touches directly are asserted against `FILE_FACTS_COLUMNS` in a test, so a Task 4
rename fails here immediately.

**Why `preferred_fact` returns `None` for several live rows, rather than picking one.** OQ6 —
multiplicity — is Joseph's and is open: §3.11's `people` and `language` are plainly multi-valued and
the SPEC carries `multiplicity` as an *unanswered* column. So a slot holding several live,
unsuperseded facts has no preferred row, because "which of several simultaneous values is preferred"
*is* the multiplicity question and answering it inside a reader would close it by accident. Three
cases are answerable and are answered: a `user_confirmed` row wins outright (§3.13's ordering is not
negotiable and the SPEC names this case), a single live row is the answer even though `preferred` was
never set on it (the column is set *only* on supersession), and among several live rows exactly one
carrying `preferred` is the pointer.

**`preferred_fact` and `fact_history` span every content hash the file has had.** That is the
skeleton's signature — `(file_id, field_key)`, no content hash — and it is right for a *reader*: the
read surface published to P2 and the review UI is *"fact and value history, including superseded
rows"*, and a user inspecting the origin of a conclusion does not know which version produced it.
Supersession itself always happens inside one content hash, because §3.4's invalidation cases — a
bumped extractor version, a changed prompt fingerprint, a new analysis tier — all leave the bytes
alone; §8.2's own worked example is two OCR passes over one file version.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_supersede.py
"""M1 — Done-means 29 and the history half of 15. §8.2's worked example, run."""
from __future__ import annotations

import ast
import importlib
import importlib.util
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from database_agent.supersede import SUPERSEDE_COLUMNS

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.file_facts import FACT_ORIGINS, FILE_FACTS_COLUMNS, facts_for_file, write_fact, RULE
from facts.states import STATES, USER_CONFIRMED
from facts.supersede import (
    FACT_TABLE, PreferredNeverReverses, SupersedeAcrossSlots, fact_history,
    preferred_fact, supersede_fact,
)
from facts.unresolved import ATTEMPTED_PRODUCERS, unresolved_for_file, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

CLOCK = "2026-08-19T12:00:00+00:00"

#: The three places §8.2 forbids the pointer from reaching. Each is another task's
#: module; a missing one is skipped rather than assumed, and the two that ship before
#: Wave D are required to be present so the guard cannot pass by being empty.
POINTER_FREE = {"facts.facets": True, "facts.fields": True,
                "facts.llm_seam": False, "facts.read_surface": False}


def _mentions(module_name: str) -> set[str]:
    """Every name, attribute and string literal a module's CODE contains."""
    module = importlib.import_module(module_name)
    tree = ast.parse(inspect.getsource(module))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            found.add(node.id)
        elif isinstance(node, ast.Attribute):
            found.add(node.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            found.add(node.value)
    return found


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Scans", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, analysis_tier="ocr",
             extractor="ocr.vision", version="1.0.0"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version=version,
        source_type="ocr", analysis_tier=analysis_tier, config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version=version, source_type="ocr", raw_value=raw,
        location=Location("ocr", (Segment("page", index=1),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible", run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


def _fact(conn, *, file_id, content_hash, field_key, value, key, state, cache_key):
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state=state, origin=RULE,
                      evidence_refs=(key,), cache_key=cache_key, active=True)


@pytest.fixture()
def scanned(p6_conn, tmp_path):
    """§8.2's own case: one scanned file, and two OCR passes over it."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="transcript.pdf",
                                    body=b"a scanned transcript")
    first = _observe(p6_conn, run_id="ocr-1", file_id=file_id,
                     content_hash=content_hash, raw="C0lumb1a Un1vers1ty")
    second = _observe(p6_conn, run_id="ocr-2", file_id=file_id,
                      content_hash=content_hash, raw="Columbia University",
                      version="2.0.0")
    return file_id, content_hash, first, second


def test_the_table_this_module_addresses_carries_both_columns_it_needs(p6_conn):
    # P1's `mark_superseded` requires a column literally named `record_id`; the
    # pointer requires `preferred`. Both are Task 4's DDL and are asserted rather
    # than assumed, so a drift fails at the first run instead of at review.
    assert FACT_TABLE == "file_facts"
    columns = {row["name"] for row in
               p6_conn.execute(f"PRAGMA table_info({FACT_TABLE})")}
    assert "record_id" in columns
    assert "preferred" in columns
    assert set(SUPERSEDE_COLUMNS) <= columns
    # The four this module reads directly are Task 4's published set, not guesses.
    for column in ("fact_id", "file_id", "content_hash", "reliability_state",
                   "preferred"):
        assert column in FILE_FACTS_COLUMNS, column
    assert USER_CONFIRMED == "user_confirmed"      # P4 publishes the tuple strongest-first


def test_a_superseding_fact_is_preferred_and_the_superseded_row_is_not(
        scanned, p6_conn):
    # Done-means 29.
    file_id, content_hash, first, second = scanned
    old = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="C0lumb1a Un1vers1ty", key=first,
                state="possible", cache_key="sha256:pass-one")
    new = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia University", key=second,
                state="validated", cache_key="sha256:pass-two")
    supersede_fact(p6_conn, old_fact_id=old, new_fact_id=new,
                   reason="a later OCR engine recovered the name")
    rows = {r["fact_id"]: r for r in fact_history(p6_conn, file_id=file_id,
                                                  field_key="subject")}
    assert not rows[old]["preferred"]
    assert rows[new]["preferred"]
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == new


def test_both_rows_both_states_and_both_evidence_chains_remain_readable(
        scanned, p6_conn):
    # Done-means 29 and 15. §8.2: "both extraction records should remain available".
    file_id, content_hash, first, second = scanned
    old = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="C0lumb1a Un1vers1ty", key=first,
                state="possible", cache_key="sha256:pass-one")
    new = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia University", key=second,
                state="validated", cache_key="sha256:pass-two")
    supersede_fact(p6_conn, old_fact_id=old, new_fact_id=new,
                   reason="a later OCR engine recovered the name")
    history = fact_history(p6_conn, file_id=file_id, field_key="subject")
    assert [r["fact_id"] for r in history] == [old, new]          # oldest first
    assert [r["reliability_state"] for r in history] == ["possible", "validated"]
    assert history[0]["supersede_reason"] == "a later OCR engine recovered the name"
    assert history[1]["supersede_reason"] is None
    for row, key in ((history[0], first), (history[1], second)):
        assert json.loads(row["evidence_refs"]) == [key]
    # And P4's raw values are untouched by any of it (§3.2, rule 1).
    raws = {r["raw_value"] for r in p6_conn.execute(
        "SELECT raw_value FROM evidence WHERE file_id = ?", (file_id,))}
    assert raws == {"C0lumb1a Un1vers1ty", "Columbia University"}


def test_section_eight_two_s_worked_example_end_to_end(scanned, p6_conn):
    # "If a first OCR pass produces unreadable text and a later improved OCR engine
    # recovers a university name, both extraction records should remain available."
    # Under B7 the first pass is a ROW, not an absence. The unresolved -> fact
    # supersession is Task 5's; what is asserted here is that the refusal survives.
    file_id, content_hash, first, second = scanned
    write_unresolved(p6_conn, file_id=file_id, content_hash=content_hash,
                     field_key="subject", reason="no_candidate_evidence",
                     attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                     evidence_refs=(first,), cache_key="sha256:pass-zero")
    old = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="C0lumb1a Un1vers1ty", key=first,
                state="possible", cache_key="sha256:pass-one")
    new = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                field_key="subject", value="Columbia University", key=second,
                state="validated", cache_key="sha256:pass-two")
    supersede_fact(p6_conn, old_fact_id=old, new_fact_id=new,
                   reason="a later OCR engine recovered the name")
    refusals = unresolved_for_file(p6_conn, file_id, content_hash,
                                   field_key="subject")
    assert [r["reason"] for r in refusals] == ["no_candidate_evidence"]
    assert len(fact_history(p6_conn, file_id=file_id, field_key="subject")) == 2
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == new


def test_preferred_is_set_only_on_supersession(scanned, p6_conn):
    # The SPEC: "It is set only on supersession" and "only by the resolver". A fact
    # written by a producer carries no pointer, and a slot with one live row is still
    # answerable — the row IS the answer, without the column being set.
    file_id, content_hash, first, _ = scanned
    only = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                 field_key="subject", value="C0lumb1a Un1vers1ty", key=first,
                 state="possible", cache_key="sha256:pass-one")
    row = [r for r in facts_for_file(p6_conn, file_id, content_hash)
           if r["fact_id"] == only][0]
    assert not row["preferred"]
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == only


def test_a_user_confirmed_fact_is_always_the_preferred_row(scanned, p6_conn):
    # §3.13's ordering is not negotiable and `preferred` never reverses it.
    file_id, content_hash, first, second = scanned
    confirmed = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                      field_key="subject", value="Columbia University", key=first,
                      state=USER_CONFIRMED, cache_key="sha256:user")
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
          value="Colombia", key=second, state="llm_supported",
          cache_key="sha256:model")
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == confirmed


def test_preferred_never_reverses_the_reliability_ordering(scanned, p6_conn):
    # Attempted, not inspected: the refusal is at a function every route passes.
    file_id, content_hash, first, second = scanned
    confirmed = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                      field_key="subject", value="Columbia University", key=first,
                      state=USER_CONFIRMED, cache_key="sha256:user")
    weaker = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                   field_key="subject", value="Colombia", key=second,
                   state="validated", cache_key="sha256:rule")
    with pytest.raises(PreferredNeverReverses):
        supersede_fact(p6_conn, old_fact_id=confirmed, new_fact_id=weaker,
                       reason="a rule disagreed with the user")
    assert preferred_fact(p6_conn, file_id=file_id,
                          field_key="subject")["fact_id"] == confirmed


def test_supersession_happens_inside_one_slot(scanned, p6_conn):
    # §8.2 replaces an ANSWER; a row about a different field or a different file is
    # not an earlier version of this one.
    file_id, content_hash, first, second = scanned
    subject = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key="subject", value="Columbia University", key=first,
                    state="validated", cache_key="sha256:one")
    other = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                  field_key="document_type", value="transcript", key=second,
                  state="validated", cache_key="sha256:two")
    with pytest.raises(SupersedeAcrossSlots):
        supersede_fact(p6_conn, old_fact_id=subject, new_fact_id=other,
                       reason="wrong slot")


def test_several_live_rows_have_no_preferred_row(scanned, p6_conn):
    # OQ6 — multiplicity — is open and the SPEC carries `multiplicity` as an
    # UNANSWERED column. "Which of several simultaneous values is preferred" IS that
    # question, so a reader that picked one would close it by accident.
    file_id, content_hash, first, second = scanned
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
          value="Columbia University", key=first, state="validated",
          cache_key="sha256:one")
    _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
          value="Columbia College", key=second, state="validated",
          cache_key="sha256:two")
    assert preferred_fact(p6_conn, file_id=file_id, field_key="subject") is None
    assert len(fact_history(p6_conn, file_id=file_id, field_key="subject")) == 2


def test_an_empty_slot_has_no_preferred_row_and_no_history(scanned, p6_conn):
    file_id, _, _, _ = scanned
    assert preferred_fact(p6_conn, file_id=file_id, field_key="subject") is None
    assert fact_history(p6_conn, file_id=file_id, field_key="subject") == []


def test_preferred_appears_in_no_contradiction_margin_or_destination_path():
    # Done-means 29's third clause, and the SPEC's own negative: "`preferred` is a
    # pointer, not a strength. It never enters the §3.6 contradiction check, never
    # breaks a §3.7 margin tie, and never makes a fact destination-eligible."
    # Introspected, not read: each module's code is parsed and the column is looked
    # for by name.
    checked = 0
    for module_name, required in POINTER_FREE.items():
        if importlib.util.find_spec(module_name) is None:
            assert not required, module_name
            continue
        assert "preferred" not in _mentions(module_name), module_name
        checked += 1
    assert checked >= 2                       # the guard cannot pass by being empty


def test_preferred_is_not_plan_versioned():
    # §8.8: facts are shared across plan versions, so the pointer is not addressable
    # per plan version. If it were, this module's three functions would have to say
    # WHICH plan version they meant.
    for function in (supersede_fact, preferred_fact, fact_history):
        names = set(inspect.signature(function).parameters)
        assert not [name for name in names if "plan" in name or "version" in name]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_supersede.py -v`
Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.supersede'`

- [ ] **Step 3: Write `supersede.py`**

```python
# src/facts/supersede.py
"""§8.2 supersession, and the `preferred` pointer M1 places on P6 (§8.2, §8.7).

§8.2, and it is the whole task in one paragraph:

    "The product must never overwrite the evidence record merely because a later
     extractor or model produces a different answer. A newer result should supersede
     an earlier result while retaining the old observation and the reason it was
     superseded. ... The resolver may mark the newer value as preferred, but a user
     reviewing a placement should still be able to inspect the origin of the
     conclusion."

**What P1 does and what this module adds.** `mark_superseded` writes three columns
across two rows -- `superseded_by` and `supersede_reason` on the old, `supersedes` on
the new -- and knows nothing about `preferred`. So the pointer is this module's whole
addition, set in the same call that links the two rows and set nowhere else in
`facts`.

**No event is appended here.** §8.2 gives P6 two event types, `fact creation` and
`fact rejection`, and supersession is neither: §8.7 keeps a `rejected` fact rather
than removing it, so rejection is a STATE a fact carries, while supersession is one
fact replacing another -- and P1 publishes three columns for exactly that, one of
which is the reason §8.2 asks to be retained. M8 also puts `subsystem = "P6"` in one
module, so an `append_event` call here would be a second home for P6's authorship.

**The chain is walked backwards before forwards.** P1's `chain` walks forward only:
with `a -> b -> c` recorded, `chain(a)` is `[a, b, c]` and `chain(c)` is `[c]`. A
history read starting from the newest row would return one row and look correct, so
`fact_history` finds each chain's tail through `supersedes` first. The walk needs no
cycle guard: `mark_superseded` refuses a cycle at write time, so the graph on disk is
acyclic by construction rather than by a second policy here.

**The slot is addressed through Task 4's reader, never through `field_key`.** Which
column `file_facts` uses to reference the catalogue is Task 4's schema decision, and a
second module spelling it would be a second home for one decision. This module reads
`file_id` and `content_hash`, takes the field key off `facts_for_file`'s rows, and
expands each into its history with P1's `chain`.

**`preferred` is a pointer, not a strength.** The SPEC's negative is exact: "It never
enters the §3.6 contradiction check, never breaks a §3.7 margin tie, and never makes a
fact destination-eligible. A reader that wants strength reads `reliability_state`."
Nothing here exports it into those paths, and a test parses those modules for the
column by name.
"""
from __future__ import annotations

import sqlite3
from typing import Iterable

from database_agent.supersede import chain, mark_superseded

from facts.file_facts import facts_for_file
from facts.states import STATES, USER_CONFIRMED

#: The table P1's `mark_superseded` and `chain` are addressed by. Task 4 owns the DDL,
#: including the VIRTUAL `record_id` projection of `fact_id` that P1 requires and the
#: `preferred` column this module sets; the name has one home and the test asserts it
#: names a table carrying both.
FACT_TABLE: str = "file_facts"


class PreferredNeverReverses(ValueError):
    """§3.13's ordering, raised rather than documented.

    "A `user_confirmed` fact is always the preferred row for its `(file_id,
    field_key)`; §3.13's ordering is not negotiable and `preferred` never reverses it."
    """


class SupersedeAcrossSlots(ValueError):
    """§8.2 replaces an ANSWER, so both rows answer the same question."""


def _row(conn: sqlite3.Connection, fact_id: str) -> sqlite3.Row:
    row = conn.execute(
        f"SELECT * FROM {FACT_TABLE} WHERE fact_id = ?", (fact_id,)).fetchone()
    if row is None:
        raise KeyError(f"unknown fact {fact_id!r}")
    return row


def _tail(conn: sqlite3.Connection, fact_id: str) -> str:
    """The oldest row of this fact's chain.

    P1's `chain` walks forward only, so a history read has to find the start itself.
    No cycle guard: `mark_superseded` walks the prospective chain and refuses one at
    write time, so this loop terminates on any graph the writer could have produced.
    """
    row = _row(conn, fact_id)
    while row["supersedes"] is not None:
        row = _row(conn, row["supersedes"])
    return row["fact_id"]


def _slot(conn: sqlite3.Connection, *, file_id: str,
          field_key: str) -> list[sqlite3.Row]:
    """Every row for one (file, field) slot, superseded rows included.

    Spans every content hash the file has had, which is what a reader inspecting the
    origin of a conclusion needs: §8.2's user "does not know which version produced
    it". Supersession itself always happens inside one content hash, because §3.4's
    invalidation cases -- a bumped extractor version, a changed prompt fingerprint, a
    new analysis tier -- all leave the bytes alone.
    """
    hashes = sorted(row["content_hash"] for row in conn.execute(
        f"SELECT DISTINCT content_hash FROM {FACT_TABLE} WHERE file_id = ?",
        (file_id,)))
    reachable: dict[str, sqlite3.Row] = {}
    for content_hash in hashes:
        for row in facts_for_file(conn, file_id, content_hash):
            if row["field_key"] != field_key:
                continue
            for member in chain(conn, FACT_TABLE, _tail(conn, row["fact_id"])):
                reachable[member["fact_id"]] = member
    return [reachable[fact_id] for fact_id in sorted(reachable)]


def supersede_fact(conn: sqlite3.Connection, *, old_fact_id: str,
                   new_fact_id: str, reason: str) -> None:
    """Done-means 29. Link two facts, and move the pointer. Nothing is deleted.

    The reason is required by P1 and is the half §8.2 names explicitly -- "retaining
    the old observation AND the reason it was superseded".
    """
    old = _row(conn, old_fact_id)
    new = _row(conn, new_fact_id)
    if (old["file_id"], old["field_key"]) != (new["file_id"], new["field_key"]):
        raise SupersedeAcrossSlots(
            "§8.2 supersedes an answer: both facts must be for one file and one "
            f"field; {old_fact_id!r} and {new_fact_id!r} are not")
    if old["reliability_state"] == USER_CONFIRMED != new["reliability_state"]:
        raise PreferredNeverReverses(
            f"{old_fact_id!r} is {USER_CONFIRMED!r}; §3.13's ordering is not negotiable "
            "and `preferred` never reverses it, so a weaker fact cannot take the "
            "pointer from a user's own answer")
    mark_superseded(conn, FACT_TABLE, old_id=old_fact_id, new_id=new_fact_id,
                    reason=reason)
    conn.execute(f"UPDATE {FACT_TABLE} SET preferred = 0 WHERE fact_id = ?",
                 (old_fact_id,))
    conn.execute(f"UPDATE {FACT_TABLE} SET preferred = 1 WHERE fact_id = ?",
                 (new_fact_id,))


def preferred_fact(conn: sqlite3.Connection, *, file_id: str,
                   field_key: str) -> sqlite3.Row | None:
    """The row a reader should show for this slot, or `None`.

    Three cases are answerable and are answered:

    * a `user_confirmed` live row wins outright -- §3.13's ordering is not
      negotiable and the SPEC names this case;
    * a single live row is the answer even though `preferred` was never set on it,
      because the column is set ONLY on supersession;
    * among several live rows, exactly one carrying `preferred` is the pointer.

    Anything else returns `None`. OQ6 -- multiplicity -- is open and the SPEC carries
    `multiplicity` as an unanswered column, so "which of several simultaneous values
    is preferred" is that question and a reader that picked one would close it by
    accident.

    Live means not superseded. `active` is a different axis and is Task 4's: §8.2's
    mechanism for the pointer is supersession, and reading a second column here would
    make the pointer depend on two rules instead of one.
    """
    live = [row for row in _slot(conn, file_id=file_id, field_key=field_key)
            if row["superseded_by"] is None]
    confirmed = [row for row in live if row["reliability_state"] == USER_CONFIRMED]
    if confirmed:
        live = confirmed
    if len(live) == 1:
        return live[0]
    pointed = [row for row in live if row["preferred"]]
    return pointed[0] if len(pointed) == 1 else None


def fact_history(conn: sqlite3.Connection, *, file_id: str,
                 field_key: str) -> list[sqlite3.Row]:
    """Done-means 15's history half. Every row for the slot, oldest first.

    Superseded rows included, each carrying its own reliability state, its own
    evidence refs and the reason it was superseded -- §8.2's "a user reviewing a
    placement should still be able to inspect the origin of the conclusion".
    """
    rows = _slot(conn, file_id=file_id, field_key=field_key)
    tails = sorted({_tail(conn, row["fact_id"]) for row in rows})
    history: list[sqlite3.Row] = []
    for tail in tails:
        history.extend(chain(conn, FACT_TABLE, tail))
    return history
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_supersede.py -v`
Expected: PASS — 12 passed

- [ ] **Step 5: Commit**

```bash
git add src/facts/supersede.py tests/p6/test_p6_supersede.py
git commit -m "feat(P6): M1 supersession and the preferred pointer — a pointer, never a strength"
```

---

---

### Task 19: `no_usable_facts`, the recorded pass, and the ordering guard (M11)

**Files:**
- Create: `src/facts/usable.py`
- Modify: `src/facts/schema.py` (two lines — see Step 3b)
- Test: `tests/p6/test_p6_usable.py`

**Interfaces:**
- Consumes: `facts.file_facts.facts_for_file`; `facts.unresolved.unresolved_for_file`;
  `evidence_shape.vocabulary` — `ANALYSIS_TIERS`, `check`; `evidence_shape.canonical` —
  `canonical_json`, `sha256_of`; `extractors.failure.ContractViolation`.
- Produces (`usable.py`): `FACT_PASSES_TABLE: str`, `FACT_PASSES_DDL: str`,
  `create_fact_passes(conn) -> None`, `FactPassNotRun(ContractViolation)`,
  `record_pass(conn, *, file_id, content_hash, analysis_tiers: frozenset[str]) -> None`,
  `passes_for(conn, *, file_id, content_hash) -> tuple[frozenset[str], ...]`,
  `no_usable_facts_for(conn, *, usable_threshold) -> Callable[[str, str], bool]`.

> **Additions to the skeleton's `Produces:` line, declared.** `FACT_PASSES_TABLE`,
> `FACT_PASSES_DDL` and `create_fact_passes` are added because the skeleton's Files line says
> *modify `src/facts/schema.py`* and something has to hold the DDL. Keeping it in this module rather
> than in `schema.py` means a reviewer can reject Task 19 whole without touching four other tasks'
> table definitions, and `schema.py` gains two lines instead of a block. `FactPassNotRun`'s **base
> class changes** from the skeleton's `Exception` to `extractors.failure.ContractViolation` — that is
> a ratified change and the reason is below.

**Done-means:** 28, and the enforceable half of preamble rule 5. **Adversarial case:** A10.

**§2.2, quoted, because both halves of the verdict are in one sentence pair:**

> The system should also distinguish between a PDF with no text layer and one with a broken text layer. A file with no text should route directly to OCR; a file that technically produces text but yields no usable facts may receive targeted OCR as a fallback because scanned PDFs can contain unreadable or corrupted extracted text. The system should not use unreliable global language-quality checks that incorrectly punish multilingual or mathematics-heavy documents.

**§2.7, quoted, because it forbids the same shortcut a second time:**

> A document with a non-empty but unusable text layer should receive OCR only when its extracted evidence fails to produce usable facts, not because a broad quality heuristic says the text looks unusual.

---

> # ⛔ DO NOT WIRE THIS INTO `run_wave2`. Read this before writing a line of the module.
>
> **What this task builds is a read surface P6's own tests exercise. Wiring it into the caller is
> separate, later work and must not be done as "integration", as "finishing the seam", or as a
> tidy-up at the end of the phase.**
>
> The mechanism, verified in the source on 2026-08-22:
>
> 1. `extractors.ocr_policy.text_layer_state(*, result, file_id, content_hash, no_usable_facts)`
>    calls `no_usable_facts(file_id, content_hash)` for **every** document whose run produced any
>    non-empty text unit — that is every text-bearing PDF in the corpus.
> 2. It is called from `document_ocr_decision`, which is called inside `extract()` on the
>    freshly-built `ExtractionResult`, which `orchestrator._extract_one` calls inside
>    `run_wave2`'s **single** loop over `cache_verdicts`. `_write(sink, result, ...)` does not run
>    until after `_extract_one` returns, so at the moment of the call P4 does not yet hold the
>    observations, let alone any fact derived from them.
> 3. **P6 Task 26 — the caller restructure — is CUT (D5).** Nothing reorders that loop. Nothing in
>    this plan touches `src/orchestrator.py`.
> 4. `FactPassNotRun` inherits `ContractViolation`, and `orchestrator._extract_one` re-raises
>    `ContractViolation` by name rather than converting it into one `failed` run.
>
> **Therefore: if P6's resolver is ever passed to `run_wave2` as `no_usable_facts`, the first
> text-bearing PDF ends the scan.** Not one bad file — the scan.
>
> **The caller keeps passing `orchestrator.TARGETED_OCR_UNAVAILABLE`,** which is P5's own stub and
> whose docstring already says why. Wiring the real verdict is the four-pass work described under
> preamble rule 5, and it is owed together with the pass-3/pass-4 ordering — not before it, and not
> instead of it. A test in this task asserts the orchestrator still imports nothing from `facts`, so
> the day someone wires it, that test fails first.
>
> **This is not a reason to soften the raise.** See *Why raise rather than default* below: the raise
> is what makes the ordering checkable at all, and the loud failure above is the guard working, not
> the guard misfiring.

---

**Why `FactPassNotRun` inherits `ContractViolation` rather than `Exception`.** The skeleton wrote
`FactPassNotRun(Exception)`. A plain `Exception` raised from inside a `no_usable_facts` callable is
caught by `orchestrator._extract_one`'s broad `except Exception` and converted into one `failed`
extraction run — the file is recorded as unreadable, the scan continues, and the ordering defect
becomes a data-quality mystery in a corner of the corpus. `ContractViolation` is re-raised by name,
above that branch, with the reason stated in the orchestrator's own comment:

> A `ContractViolation` is not about this file at all, so recording it as the file's failure would be a false statement about the corpus AND would hide the defect it exists to surface.

That is precisely this exception's case: being asked for a verdict before the pass that defines it is
not a fact about the PDF. So the base class is `ContractViolation`.

**This is the one import `facts` makes from `extractors`, and it is worth naming.** P6's dependency
on P5 is otherwise zero — the skeleton is explicit that P6 consumes P5 *"only via P4's shape"*. An
exception base class is not per-format knowledge and creates no cycle (`extractors.failure` imports
nothing from `facts`), but it *is* an edge that did not exist before, and Task 25's guard should
permit exactly this one and no other. Flagged in the contract notes.

**The pass record is a fifth table, and the "four tables" line needs reading with it.** The skeleton
says P6 *"owns four tables and creates none of anyone else's"*, and Task 19's own Files line says to
modify `schema.py`. Both are the same author and both are right: the **four** are §3's published
records — `fields`, `values`, `file_facts`, `unresolved` — which neighbours read. `fact_passes` is
P6-internal bookkeeping that no other part reads and that carries no claim about any file. The clause
that actually binds is the second one, *"creates none of anyone else's"*, and this creates none.

**The pass record carries no timestamp, deliberately.** It answers a membership question — *has a
deterministic pass over this `(file_id, content_hash)` completed, and which analysis tiers did it
cover* — and a time column would invite a caller to reason about "the latest pass", which is the
kind of ordering P6 refuses to infer anywhere else (Global Constraints: P6 imposes its own total
order and inherits none). Recording the same pass twice writes one row, because `pass_id` is
`sha256_of(canonical_json([file_id, content_hash, sorted(tiers)]))`.

**Computed from the fact tables and nothing else.** The SPEC's negative is load-bearing and is stated
twice in the design — §2.2's *"should not use unreliable global language-quality checks"* and §2.7's
*"not because a broad quality heuristic says the text looks unusual"* — and A10 names the failure
literally: `forbidden_value: {"ocr_fallback": true, "triggered_by": "language_quality_heuristic"}`,
verified in `tests/eval/fixtures/adversarial/A10.json`. So the module reads `facts_for_file` and
`unresolved_for_file` and nothing else; it never touches a `text_unit`, never counts characters,
never inspects a language. The test parses the module and asserts no identifier mentions text, a
unit, a language, a ratio or a character, alongside the behavioural cases.

**`usable_threshold` is a required keyword with no default, and its polarity is stated once here.**
It receives `(facts, unresolved)` — the two row lists for the version — and returns **`True` when
the stored facts ARE usable**. The verdict returns the negation. Which facts count and how many is
Deferred by name (*"The `no_usable_facts` threshold — M11, P5 OQ1. Which facts count as usable and
how many. The design requires the verdict and states no threshold."*), so nothing here chooses, and
Task 25 asserts no threshold is a module-level constant by runtime introspection of the namespace.

**Why raise rather than default.** Returning `False` for an unrecorded pass would be safe — no OCR —
and would hide the bug forever; the current stub does exactly that, which is why the defect survived
to now. Returning `True` is the corpus-wide OCR the SPEC names outright (*"Consulted earlier it
would return `true` for every file and trigger OCR on the whole corpus"*). Raising is the only option
that makes a wrong call sequence a failing test rather than a silent behaviour, which is this
project's stated decision criterion: *"the one that … makes a wrong outcome impossible rather than
merely unlikely, wins"*. Note what the raise buys structurally: `True` is not a value the
unrecorded-pass branch can produce at all, so the SPEC's named disaster is unreachable rather than
unlikely.

**The termination condition is a lookup, not a flag.** A pass record carries which tiers it covered,
so *"have we already tried OCR for this content hash"* is `"ocr" in some recorded pass` — answerable
from the table. A file whose OCR pass also produced nothing is a file with no usable facts, not a
file to OCR again, and the verdict keeps answering after an `ocr` pass rather than raising. **Nothing
here asserts the caller does not loop** — that was Task 26's and Task 26 is cut. The non-looping
property is owed with the four-pass wiring, and until then no caller consults this verdict at all.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_usable.py
"""M11 — Done-means 28, A10, and the guard that makes preamble rule 5 checkable."""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

import orchestrator

from database_agent.files_table import get_file, record_file

from evidence_shape.vocabulary import ANALYSIS_TIERS, NotInVocabulary

from extractors.failure import ContractViolation
from extractors.ocr_policy import text_layer_state
from extractors.sink import ExtractionResult

from facts import usable
from facts.file_facts import FACT_ORIGINS, FORBIDDEN_COLUMN_SUBSTRINGS, write_fact, RULE
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.usable import (
    FACT_PASSES_TABLE, FactPassNotRun, no_usable_facts_for, passes_for, record_pass,
)
from facts.values import VALUE_ORIGINS, ensure_value

NATIVE = frozenset({ANALYSIS_TIERS[1]})            # "native"
WITH_OCR = frozenset({ANALYSIS_TIERS[1], ANALYSIS_TIERS[2]})


def _any_fact(facts, unresolved) -> bool:
    """The injected threshold. Returns True when the stored facts ARE usable.

    §2.2's threshold is Deferred by name, so the test states one and the module
    states none. This one is the simplest that distinguishes the two Done-means 28
    cases; it is not a proposal.
    """
    return bool(facts)


def _never_usable(facts, unresolved) -> bool:
    return False


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring.

    A source-text search matches comments and docstrings, and a guard that does that
    has broken three tasks on this project already (P5 PLAN, Task 20).
    """
    tree = ast.parse(inspect.getsource(module))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings}


def _identifiers(module) -> set[str]:
    tree = ast.parse(inspect.getsource(module))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update(alias.name for alias in node.names)
            names.add(getattr(node, "module", "") or "")
    return names


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Scans", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


@pytest.fixture()
def scanned(p6_conn, tmp_path):
    return _record(p6_conn, tmp_path, name="scan.pdf", body=b"a scanned page")


def test_the_returned_callable_is_exactly_the_shape_p5_already_requires(p6_conn):
    # Two P5 tests assert `no_usable_facts` has no default and is called
    # positionally; the factory must therefore return that shape with no adapter.
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    signature = inspect.signature(verdict)
    parameters = list(signature.parameters.values())
    assert [p.name for p in parameters] == ["file_id", "content_hash"]
    for parameter in parameters:
        assert parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        assert parameter.annotation == "str"
    assert signature.return_annotation == "bool"
    # And it binds against the seam the orchestrator already declares.
    seam = inspect.signature(orchestrator.run_wave2).parameters["no_usable_facts"]
    assert seam.kind is inspect.Parameter.KEYWORD_ONLY
    assert seam.default is inspect.Parameter.empty


def test_false_for_a_file_with_one_active_usable_fact(scanned, p6_conn):
    # Done-means 28, first half.
    file_id, content_hash = scanned
    key = "sha256:" + "a" * 64
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="Columbia University",
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=file_id, content_hash=content_hash,
               field_key="subject", value_id=value_id,
               reliability_state="validated", origin=RULE,
               evidence_refs=(key,), cache_key="sha256:cache", active=True)
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    assert verdict(file_id, content_hash) is False


def test_true_for_a_file_whose_evidence_produced_only_unresolved_rows(
        scanned, p6_conn):
    # Done-means 28, second half. §2.2's `text_layer_broken` case: text came out,
    # and no fact did. The `unresolved` rows are evidence FOR the verdict.
    file_id, content_hash = scanned
    write_unresolved(p6_conn, file_id=file_id, content_hash=content_hash,
                     field_key="subject", reason="no_candidate_evidence",
                     attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                     evidence_refs=(), cache_key="sha256:cache")
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    assert verdict(file_id, content_hash) is True


def test_the_threshold_decides_and_the_module_states_none(scanned, p6_conn):
    # Both polarities driven through the same stored rows, so the module cannot be
    # holding a rule of its own behind the injected one.
    file_id, content_hash = scanned
    key = "sha256:" + "b" * 64
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="Columbia University",
                            first_evidence_ref=key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=file_id, content_hash=content_hash,
               field_key="subject", value_id=value_id,
               reliability_state="possible", origin=RULE,
               evidence_refs=(key,), cache_key="sha256:cache", active=True)
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    assert no_usable_facts_for(
        p6_conn, usable_threshold=_any_fact)(file_id, content_hash) is False
    assert no_usable_facts_for(
        p6_conn, usable_threshold=_never_usable)(file_id, content_hash) is True
    parameter = inspect.signature(no_usable_facts_for).parameters["usable_threshold"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty
    # Task 25's technique: runtime introspection of the namespace, not a text search.
    numbers = {name: value for name, value in vars(usable).items()
               if isinstance(value, (int, float)) and not isinstance(value, bool)}
    assert numbers == {}


def test_no_recorded_pass_raises_rather_than_answering(scanned, p6_conn):
    # The SPEC: the verdict is "defined only after P6's deterministic pass on that
    # content hash has completed. Consulted earlier it would return `true` for every
    # file and trigger OCR on the whole corpus." `True` is not a value this branch
    # can produce, so that outcome is unreachable rather than unlikely.
    file_id, content_hash = scanned
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    with pytest.raises(FactPassNotRun):
        verdict(file_id, content_hash)


def test_the_verdict_is_per_file_version_and_not_per_file(p6_conn, tmp_path):
    # Keyed on (file_id, content_hash): a pass over one version says nothing about
    # another, because the §3.4 cache key differs and so do the facts.
    file_id, content_hash = _record(p6_conn, tmp_path, name="v1.pdf", body=b"one")
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    assert verdict(file_id, content_hash) is True
    with pytest.raises(FactPassNotRun):
        verdict(file_id, "f" * 64)


def test_the_raise_is_a_contract_violation_and_the_caller_cannot_swallow_it():
    # A plain Exception would be caught by `orchestrator._extract_one`'s broad
    # `except Exception` and become one `failed` run -- the file recorded as
    # unreadable, the scan continuing, the ordering defect turned into a data-quality
    # mystery. The orchestrator re-raises ContractViolation by name because "a
    # ContractViolation is not about this file at all".
    assert issubclass(FactPassNotRun, ContractViolation)


def test_consulting_it_during_extraction_ends_the_scan(p6_conn, tmp_path):
    """The danger, proved rather than described — this is why it is not wired in.

    `ocr_policy.text_layer_state` consults the verdict for every document whose run
    produced any non-empty text unit, inside `run_wave2`'s single loop, before P4
    holds the observations at all. Task 26 is cut, so nothing reorders that. This
    test IS the reason `orchestrator.TARGETED_OCR_UNAVAILABLE` is still the value the
    caller passes.
    """
    file_id, content_hash = _record(p6_conn, tmp_path, name="text.pdf",
                                    body=b"a text-bearing PDF")
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    result = ExtractionResult(run={},
                              text_units=({"text": "a non-empty text layer"},))
    with pytest.raises(FactPassNotRun):
        text_layer_state(result=result, file_id=file_id,
                         content_hash=content_hash, no_usable_facts=verdict)
    # A document with NO text never reaches the verdict, which is §2.2's other route
    # and needs no pass at all.
    assert text_layer_state(result=ExtractionResult(run={}), file_id=file_id,
                            content_hash=content_hash,
                            no_usable_facts=verdict) == "text_layer_absent"


def test_the_orchestrator_still_passes_the_stub_and_imports_nothing_from_facts():
    # D5, asserted from P6's side. The day someone wires this verdict into
    # `run_wave2`, this test fails before the scan does.
    assert orchestrator.TARGETED_OCR_UNAVAILABLE("any-file", "any-hash") is False
    tree = ast.parse(inspect.getsource(orchestrator))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
    assert "facts" not in imported


def test_a_pass_at_native_answers_and_a_pass_that_included_ocr_still_answers(
        scanned, p6_conn):
    # Pass 3's gate, and the termination condition. A file whose OCR pass also
    # produced nothing is a file with no usable facts, not a file to OCR again.
    file_id, content_hash = scanned
    verdict = no_usable_facts_for(p6_conn, usable_threshold=_any_fact)
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=NATIVE)
    assert verdict(file_id, content_hash) is True
    record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                analysis_tiers=WITH_OCR)
    assert verdict(file_id, content_hash) is True
    # "Have we already tried OCR for this content hash" is a LOOKUP, not a flag.
    covered = passes_for(p6_conn, file_id=file_id, content_hash=content_hash)
    assert any(ANALYSIS_TIERS[2] in tiers for tiers in covered)
    assert NATIVE in covered and WITH_OCR in covered


def test_a_pass_recorded_twice_is_one_row(scanned, p6_conn):
    file_id, content_hash = scanned
    for _ in range(3):
        record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                    analysis_tiers=NATIVE)
    assert passes_for(p6_conn, file_id=file_id, content_hash=content_hash) == (
        NATIVE,)


def test_a_pass_records_only_tiers_p4_publishes(scanned, p6_conn):
    file_id, content_hash = scanned
    with pytest.raises(NotInVocabulary):
        record_pass(p6_conn, file_id=file_id, content_hash=content_hash,
                    analysis_tiers=frozenset({"vibes"}))
    assert passes_for(p6_conn, file_id=file_id, content_hash=content_hash) == ()


def test_it_is_computed_from_the_fact_tables_and_no_text_quality_heuristic(p6_conn):
    # Done-means 28's second half, and A10's forbidden value by name:
    # {"ocr_fallback": true, "triggered_by": "language_quality_heuristic"}.
    # §2.2 and §2.7 both forbid deciding this from text quality.
    mentioned = _identifiers(usable)
    for banned in ("text", "unit", "language", "quality", "ratio", "char", "ocr_"):
        assert not [name for name in mentioned if banned in name.lower()], banned
    assert "evidence_shape.store" not in mentioned
    assert "language_quality_heuristic" not in _code_strings(usable)
    # The two reads it IS built from.
    assert "facts_for_file" in mentioned and "unresolved_for_file" in mentioned


def test_the_pass_record_obeys_the_same_negative_contract_as_the_fact_tables(
        p6_conn):
    # §3.14, applied to the fifth table too: a reviewer checks it from the schema.
    columns = [row["name"] for row in
               p6_conn.execute(f"PRAGMA table_info({FACT_PASSES_TABLE})")]
    assert columns == ["pass_id", "file_id", "content_hash", "analysis_tiers"]
    for column in columns:
        for forbidden in FORBIDDEN_COLUMN_SUBSTRINGS:
            assert forbidden not in column, (column, forbidden)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_usable.py -v`
Expected: FAIL — collection error, `ModuleNotFoundError: No module named 'facts.usable'`

- [ ] **Step 3: Write `usable.py`**

```python
# src/facts/usable.py
"""M11 — `no_usable_facts`, the recorded pass, and the ordering guard (§2.2, §2.7).

§2.2 permits targeted OCR on a PDF with a non-empty but BROKEN text layer only when
its stored evidence yields no usable facts. This module is that verdict.

    "A file that technically produces text but yields no usable facts may receive
     targeted OCR as a fallback ... The system should not use unreliable global
     language-quality checks that incorrectly punish multilingual or
     mathematics-heavy documents."          -- §2.2

    "A document with a non-empty but unusable text layer should receive OCR only when
     its extracted evidence fails to produce usable facts, not because a broad quality
     heuristic says the text looks unusual."                              -- §2.7

**DO NOT WIRE THIS INTO `run_wave2`.** `extractors.ocr_policy.text_layer_state`
consults `no_usable_facts` for every document whose run produced any non-empty text
unit, inside the orchestrator's single extraction loop, before P4 has been handed the
observations at all. P6 Task 26 -- the caller restructure -- is CUT (D5), so nothing
reorders that. `FactPassNotRun` is a `ContractViolation` and the orchestrator re-raises
those by name, so passing this verdict to `run_wave2` today would END THE SCAN on the
first text-bearing PDF. The caller keeps `orchestrator.TARGETED_OCR_UNAVAILABLE`.
Wiring the real verdict is the four-pass work and is owed together with the pass-3 and
pass-4 ordering, not before it. A test asserts the orchestrator still imports nothing
from `facts`.

**Computed from the fact tables and nothing else.** The negative is load-bearing and
the design states it twice. A10 names the failure literally --
`triggered_by: "language_quality_heuristic"` is its forbidden value -- so this module
reads `facts_for_file` and `unresolved_for_file` and touches no text unit, no
character count and no language.

**Why it raises.** Returning `False` for an unrecorded pass would be safe and would
hide the bug forever -- the current stub does exactly that, which is why the defect
survived to now. Returning `True` is the corpus-wide OCR the SPEC names. Raising is
the only option that turns a wrong call sequence into a failing test, and it makes the
SPEC's named disaster UNREACHABLE rather than unlikely: `True` is not a value the
unrecorded-pass branch can produce.

**The pass record is a fifth table and no neighbour reads it.** The four P6 owns are
§3's published records -- `fields`, `values`, `file_facts`, `unresolved`. This one is
bookkeeping, carries no claim about any file, and creates none of anyone else's. It
has no timestamp on purpose: it answers a membership question, and a time column would
invite a caller to reason about "the latest pass", which is an ordering P6 refuses to
infer anywhere else.
"""
from __future__ import annotations

import json
import sqlite3
from typing import Callable, Iterable, Sequence

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import ANALYSIS_TIERS, check

from extractors.failure import ContractViolation

from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

#: P6-internal bookkeeping. Not one of the four published records, and read by no
#: other part. `analysis_tiers` is canonical JSON of the sorted tier names, so one
#: pass has one representation.
FACT_PASSES_TABLE: str = "fact_passes"

FACT_PASSES_DDL: str = f"""
CREATE TABLE IF NOT EXISTS {FACT_PASSES_TABLE} (
    pass_id        TEXT PRIMARY KEY,
    file_id        TEXT NOT NULL,
    content_hash   TEXT NOT NULL,
    analysis_tiers TEXT NOT NULL
)
"""


class FactPassNotRun(ContractViolation):
    """The verdict was consulted before the pass that defines it.

    The base class is deliberate. A plain `Exception` raised from inside a
    `no_usable_facts` callable is caught by `orchestrator._extract_one`'s broad
    `except Exception` and becomes one `failed` extraction run: the file recorded as
    unreadable, the scan continuing, and the ordering defect turned into a
    data-quality mystery. The orchestrator re-raises `ContractViolation` by name for
    the reason its own comment gives -- "a ContractViolation is not about this file at
    all, so recording it as the file's failure would be a false statement about the
    corpus AND would hide the defect it exists to surface" -- which is exactly this
    exception's case.
    """


def create_fact_passes(conn: sqlite3.Connection) -> None:
    """Create the pass record. Called from `facts.schema.create_facts_schema`."""
    conn.execute(FACT_PASSES_DDL)


def record_pass(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                analysis_tiers: frozenset[str]) -> None:
    """A P6 deterministic pass over this file version, at these tiers, completed.

    Idempotent: `pass_id` is derived from the three values, so recording the same
    pass twice writes one row. The tiers are checked against P4's published tuple
    rather than stored as given -- a tier P4 does not publish is a spelling error
    that would make the termination lookup silently wrong.
    """
    for tier in sorted(analysis_tiers):
        check(tier, ANALYSIS_TIERS, name="analysis_tier")
    tiers = canonical_json(sorted(analysis_tiers))
    pass_id = sha256_of(canonical_json([file_id, content_hash, tiers]))
    conn.execute(
        f"INSERT OR IGNORE INTO {FACT_PASSES_TABLE} "
        "(pass_id, file_id, content_hash, analysis_tiers) VALUES (?, ?, ?, ?)",
        (pass_id, file_id, content_hash, tiers))


def passes_for(conn: sqlite3.Connection, *, file_id: str,
               content_hash: str) -> tuple[frozenset[str], ...]:
    """Every recorded pass over this file version, as its set of analysis tiers.

    Ordered by `pass_id` so the sequence is a property of the values rather than of
    insertion order, which P6 inherits from nothing. This is also the termination
    lookup: "have we already tried OCR for this content hash" is
    `any("ocr" in tiers for tiers in passes_for(...))`, a fact on disk rather than a
    flag someone remembers to set.
    """
    rows = conn.execute(
        f"SELECT analysis_tiers FROM {FACT_PASSES_TABLE} "
        "WHERE file_id = ? AND content_hash = ? ORDER BY pass_id",
        (file_id, content_hash)).fetchall()
    return tuple(frozenset(json.loads(row["analysis_tiers"])) for row in rows)


def no_usable_facts_for(
        conn: sqlite3.Connection, *,
        usable_threshold: Callable[[Sequence[sqlite3.Row], Sequence[sqlite3.Row]],
                                   bool]) -> Callable[[str, str], bool]:
    """Done-means 28. The exact `Callable[[str, str], bool]` P5 already requires.

    `usable_threshold` receives the two row lists for the version -- the facts, then
    the `unresolved` rows -- and returns **True when the stored facts ARE usable**.
    This function returns the negation, which is what §2.2 asks for. Which facts count
    and how many is Deferred by name ("The `no_usable_facts` threshold -- M11, P5
    OQ1"), so it is a required keyword with no default and nothing here chooses.

    The `unresolved` rows are passed because the SPEC makes them evidence FOR the
    verdict, not merely the absence of facts: a version whose every attempted field
    ended in a recorded refusal is a version whose text yielded nothing, and that is
    a stronger statement than an empty fact list.

    **Read the module docstring before passing this anywhere.**
    """

    def no_usable_facts(file_id: str, content_hash: str) -> bool:
        if not passes_for(conn, file_id=file_id, content_hash=content_hash):
            raise FactPassNotRun(
                f"no P6 deterministic pass is recorded for {file_id!r} at "
                f"{content_hash!r}; §2.2's verdict is defined only after that pass "
                "has completed, and answering here would be a statement about rows "
                "that do not exist yet")
        return not usable_threshold(
            facts_for_file(conn, file_id, content_hash),
            unresolved_for_file(conn, file_id, content_hash))

    return no_usable_facts
```

- [ ] **Step 3b: Add two lines to `src/facts/schema.py`**

`create_facts_schema` creates the four published records; the pass record is created with them so
one call still builds every table P6 owns. Add exactly these two lines — the import is **local to the
function**, not at module scope, because `facts.usable` imports `facts.file_facts` and
`facts.unresolved`, and a module-level import here would make the schema module depend on two
modules that may in turn reach back to it:

**Line 1**, as the last statement inside `create_facts_schema`, after the four published records
are created (if the function ends with a `return`, immediately before it):

```python
    create_fact_passes(conn)              # P6's fifth, internal table (PLAN Task 19)
```

**Line 2**, the import it needs, placed on the line *above* it — **inside the function body, not at
module scope**:

```python
    from facts.usable import create_fact_passes   # local import: see below
```

The import is local because `facts.usable` imports `facts.file_facts` and `facts.unresolved`, and a
module-scope import here would make the schema module depend on two modules that Tasks 4 and 5 build
against it. A function-local import is the standard fix and costs one call's lookup at schema
creation time, which happens once per database.

Nothing else in `schema.py` changes. No existing line is edited, reordered or removed.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_usable.py -v`
Expected: PASS — 14 passed

- [ ] **Step 5: Run the whole P6 suite, to prove the schema edit broke nothing**

Run: `pytest tests/p6 -q`
Expected: PASS — every earlier task's tests still green, because `create_facts_schema` gained one
table and changed none.

- [ ] **Step 6: Commit**

```bash
git add src/facts/usable.py src/facts/schema.py tests/p6/test_p6_usable.py
git commit -m "feat(P6): M11 no_usable_facts and the recorded pass — a read surface, deliberately unwired"
```

---

---

### Task 20: §8.6 — the three ceilings, the degradation order, and the resolver that enforces it

**Files:** create `src/facts/budgets.py`, `src/facts/resolver.py`; test `tests/p6/test_p6_budgets.py`.

**Interfaces:**
- Consumes: `database_agent.budget.CEILING_KEYS`, `database_agent.budget.get_ceiling`;
  `facts.unresolved.write_unresolved`, `facts.unresolved.unresolved_for_file`; every producer
  module, **through injected stage callables bound at the composition root** (see Step 1's note).
- Produces: `P6_CEILING_KEYS: tuple[str, str, str]` (`model.max_llm_calls_per_thousand_files`,
  `model.max_cost_per_scan`, `model.max_dossier_tokens_per_call`),
  `DEGRADATION_ORDER: tuple[str, str, str]` (`direct`, `rule`, `llm`),
  `CEILING_GATED_STAGES: frozenset[str]`, `UnknownCeiling`,
  `ceiling_values(conn) -> dict[str, int | None]`,
  `exhausted_ceilings(*, budget_exhausted: Callable[[str], bool]) -> tuple[str, ...]`,
  `deferred_counts(conn, *, results: Iterable[ResolveResult]) -> dict[str, int]`;
  `Stage`, `PassRecorder`, `REASON_BY_BAR: Mapping[str, str]`, `StageSetInvalid`,
  `ResolveResult(file_id, content_hash, fact_ids, reason_counts, stages_run, stages_barred,
  deferred_against, error)` with `ResolveResult.errored(*, file_id, content_hash, error)`,
  `FactResolver` — the one entry point, constructed with every injected strategy and threshold;
  `FactResolver.resolve(conn, *, file_id, content_hash) -> ResolveResult`.

**Done-means:** 20 (the `budget_deferred` half).

---

**The design sentences this task is accountable to, quoted from
`planning/00-database-agent-product-design.md` and verified by `grep` before they were written here:**

> *"The engine should degrade in a predictable order. Direct facts and high-precision rules run first
> because they are cheap and reliable. Full local extraction and OCR run within the configured
> budget. Graph retrieval activates only for files with meaningful incomplete evidence and a
> plausible anchor. LLM calls are reserved for bounded ambiguities, group coherence, custom-template
> generation, and residual interpretation. If the budget is exhausted, the product should retain
> extracted evidence, mark the deferred stage, and leave the file or group in review rather than
> guessing. Cost exhaustion must never turn into lower-quality automatic classification."*

> *"This makes the product's limitations legible and avoids the false impression that an unprocessed
> file was understood and found unimportant."*

Three consequences, and each is a test below rather than a paragraph:

1. **All three of P6's ceilings are `model.*` ceilings.** Checked against P1's live sixteen:
   `model.max_llm_calls_per_thousand_files`, `model.max_cost_per_scan`,
   `model.max_dossier_tokens_per_call`. The other thirteen are P5's, P9's, P10's, P11's, P13's and
   P4's. So the **only** producer a P6 ceiling can close is the LLM route — `direct` and `rule` have
   already run by the time any ceiling is consulted. That is what makes *"cost exhaustion must never
   turn into lower-quality automatic classification"* mechanically true here instead of aspirational:
   there is no cheaper producer to fall back **to**. Degradation in P6 is subtraction, never
   substitution.
2. **The bar is recorded, not inferred.** A barred field gets an `unresolved` row — `budget_deferred`
   for a ceiling, `privacy_withheld` for a handling class that forbids the model route — so the
   unfinished work is visible *as* unfinished. Neither reason is an abstention (P6 SPEC,
   `unresolved` rule 4).
3. **No number lives in `facts`.** P1 stores ceiling *values* and enforces nothing
   (`database_agent/budget.py`: *"P1 holds and publishes values; P1 enforces none of them. Reading a
   ceiling is not enforcing it."*), so exhaustion arrives as an injected predicate — P3's precedent,
   widened from `Callable[[], bool]` to `Callable[[str], bool]` because P6 must report per-ceiling
   deferral counts and therefore has to name which ceiling it asked about.

**Where the per-ceiling count durably lives.** `write_unresolved` has no ceiling-key column and P6
owns exactly four tables, so `deferred_counts` is a scan-scoped aggregate over the `ResolveResult`s
the caller collected, cross-checked against the `unresolved` rows actually written. The durable
per-ceiling record is Task 21's `stage_output.payload`, which carries `deferred_against` verbatim and
which P2 stores and never parses. Stated here so no one later adds a fifth P6 table for it.

---

- [ ] **Step 1: Read the seams this task binds to, and confirm the two names Wave A owes it.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -c "
  import inspect
  from database_agent.budget import CEILING_KEYS, get_ceiling, set_ceiling
  print('P1 ceilings:', len(CEILING_KEYS))
  print([k for k in CEILING_KEYS if k.startswith('model.')])
  print('get_ceiling:', inspect.signature(get_ceiling))
  from facts.unresolved import write_unresolved, unresolved_for_file, UNRESOLVED_REASONS, ATTEMPTED_PRODUCERS
  print('write_unresolved:', inspect.signature(write_unresolved))
  print('unresolved_for_file:', inspect.signature(unresolved_for_file))
  print('reasons:', UNRESOLVED_REASONS)
  print('producers:', ATTEMPTED_PRODUCERS)
  from facts.schema import create_facts_schema
  from facts.fields import create_fields
  print('schema entry point OK')
  "
  ```

  Expected: P1 publishes sixteen keys of which exactly three start with `model.`; `get_ceiling` is
  `(conn, key) -> int | None`; `UNRESOLVED_REASONS` contains `budget_deferred` and `privacy_withheld`;
  `ATTEMPTED_PRODUCERS` is `("direct", "rule", "llm")`.

  > **The one name this task assumes rather than reads from the skeleton.** Tasks 2–5 each *modify*
  > `src/facts/schema.py` but the skeleton's `Interfaces:` blocks never name its entry point. This
  > task, and Task 21, call it **`facts.schema.create_facts_schema(conn) -> None`**. If Wave A landed
  > a different spelling, change the two import lines and nothing else — no logic in this task
  > depends on it. Do not add a second creator.

  > **And the one contract this task reads as a binding, not as an import.** The skeleton's
  > `Consumes:` says *"every producer module"*. `resolver.py` imports **none** of them. It takes the
  > three producers as injected `Stage` callables of one uniform shape,
  > `Callable[[sqlite3.Connection, str, str], tuple[str, ...]]`, which the composition root binds:
  >
  > | `DEGRADATION_ORDER` entry | bound at the composition root to |
  > |---|---|
  > | `direct` | `partial(facts.direct.direct_facts, slots=<injected DirectSlots>)` |
  > | `rule` | `partial(facts.rules.apply_rules, rules=<injected Rule tuple>)` |
  > | `llm` | the P8 route, or **`None`** — and `None` is the ordinary case, because P8 does not exist |
  >
  > Three reasons, and they are the whole justification for not importing the producers here.
  > **(a)** It is what "constructed with every injected strategy and threshold" means: `DirectSlots`,
  > the `Rule` tuple, the score minimum and the margin minimum are bound *into* the stage callable by
  > the caller, so no strategy and no number can reach `resolver.py` at all — Task 25's
  > runtime-introspection guard then passes for a structural reason rather than by inspection luck.
  > **(b)** It is what makes *"the order is asserted from the call sequence rather than from a
  > docstring"* a test one can actually write: a recording stage appends its own name.
  > **(c)** Tasks 17 and 19 are being written in parallel with this one, in the same wave; a direct
  > import would put a build-order edge inside a wave that has none. `record_pass` is injected as a
  > `PassRecorder` for exactly that reason, and because the tier set it needs
  > (`analysis_tiers: frozenset[str]`) is a read over P4's runs that `resolve`'s fixed signature has
  > nowhere to carry.

- [ ] **Step 2: Write the test file, complete.**

  Create `tests/p6/test_p6_budgets.py`:

  ```python
  # tests/p6/test_p6_budgets.py
  """§8.6 — the three ceilings, the degradation order, and what a ceiling may not do.

  The rule under test is one sentence of §00: "Cost exhaustion must never turn into
  lower-quality automatic classification." Its P6 form is that a ceiling SUBTRACTS the
  LLM route and substitutes nothing for it, and that the subtraction is a row.
  """
  from __future__ import annotations

  import inspect
  from collections.abc import Mapping

  import pytest

  from database_agent.budget import CEILING_KEYS, set_ceiling

  import facts.budgets as budgets_module
  import facts.resolver as resolver_module
  from facts.budgets import (
      CEILING_GATED_STAGES, DEGRADATION_ORDER, P6_CEILING_KEYS, UnknownCeiling,
      ceiling_values, deferred_counts, exhausted_ceilings,
  )
  from facts.fields import create_fields
  from facts.resolver import REASON_BY_BAR, FactResolver, ResolveResult, StageSetInvalid
  from facts.schema import create_facts_schema
  from facts.unresolved import ATTEMPTED_PRODUCERS, NOT_ABSTENTIONS, unresolved_for_file

  #: §3.8's role field, ratified into the catalogue by round 1's F-1 and required to
  #: exist by Done-means 13 and 22. Used here only as a field key that is certain to be
  #: in the catalogue, so `write_unresolved` has something legal to name.
  FIELD = "authored_by"

  FILE_ID = "file-01"
  CONTENT_HASH = "042896dc1966b8a6214e5383aba5b8b931cfa049d17aafa37eb8a77c859b95da"
  CACHE_KEY = "sha256:0000000000000000000000000000000000000000000000000000000000000001"


  @pytest.fixture()
  def p6(conn):
      create_facts_schema(conn)
      create_fields(conn)
      return conn


  class Recorder:
      """A producer, recorded. The call ORDER is the thing under test, so the stages
      write their own names into one shared list rather than being asked afterwards."""

      def __init__(self) -> None:
          self.calls: list[str] = []
          self.passes: list[tuple[str, str]] = []

      def stage(self, name: str, *, produces: tuple[str, ...] = ()):
          def run(conn, file_id: str, content_hash: str) -> tuple[str, ...]:
              self.calls.append(name)
              return produces
          return run

      def record_pass(self, conn, file_id: str, content_hash: str) -> None:
          self.passes.append((file_id, content_hash))


  def a_resolver(recorder: Recorder, *, llm=None, permitted=True, exhausted=(),
                 pending=(FIELD,)) -> FactResolver:
      return FactResolver(
          stages={
              "direct": recorder.stage("direct", produces=("fact-direct",)),
              "rule": recorder.stage("rule"),
              "llm": llm,
          },
          pending_fields=lambda conn, file_id, content_hash: tuple(pending),
          budget_exhausted=lambda key: key in exhausted,
          model_route_permitted=lambda file_id: permitted,
          record_pass=recorder.record_pass,
          cache_key_for=lambda file_id, content_hash: CACHE_KEY,
          screen_metadata=lambda conn, file_id, content_hash: (),
      )


  def resolve(resolver: FactResolver, conn) -> ResolveResult:
      return resolver.resolve(conn, file_id=FILE_ID, content_hash=CONTENT_HASH)


  # --- the three ceilings ------------------------------------------------------

  def test_p6_holds_exactly_three_ceilings_and_all_three_are_p1s():
      assert len(P6_CEILING_KEYS) == 3
      assert set(P6_CEILING_KEYS) <= set(CEILING_KEYS)


  def test_every_p6_ceiling_is_a_model_ceiling_which_is_why_degradation_cannot_substitute():
      # The whole of §8.6's "cost exhaustion must never turn into lower-quality
      # automatic classification" rests on this: the only route a P6 ceiling can close
      # is the LLM route, and `direct` and `rule` have already run.
      assert all(key.startswith("model.") for key in P6_CEILING_KEYS)
      assert {key for key in CEILING_KEYS if key.startswith("model.")} == set(P6_CEILING_KEYS)


  def test_the_ceiling_values_come_from_p1s_store_and_never_from_this_package(p6):
      assert ceiling_values(p6) == {key: None for key in P6_CEILING_KEYS}
      set_ceiling(p6, "model.max_cost_per_scan", 25)
      assert ceiling_values(p6)["model.max_cost_per_scan"] == 25


  def test_exhaustion_is_an_injected_predicate_asked_once_per_ceiling_in_order():
      asked: list[str] = []

      def budget_exhausted(key: str) -> bool:
          asked.append(key)
          return key == "model.max_cost_per_scan"

      assert exhausted_ceilings(budget_exhausted=budget_exhausted) == \
          ("model.max_cost_per_scan",)
      assert tuple(asked) == P6_CEILING_KEYS


  def test_exhausted_ceilings_takes_its_predicate_as_a_required_keyword():
      parameter = inspect.signature(exhausted_ceilings).parameters["budget_exhausted"]
      assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
      assert parameter.default is inspect.Parameter.empty


  # --- the degradation order ---------------------------------------------------

  def test_the_order_is_direct_then_rule_then_llm(p6):
      recorder = Recorder()
      resolve(a_resolver(recorder, llm=recorder.stage("llm")), p6)
      # Asserted from the call sequence, not from a docstring.
      assert recorder.calls == ["direct", "rule", "llm"]
      assert DEGRADATION_ORDER == ("direct", "rule", "llm")


  def test_the_producer_names_are_the_same_three_the_unresolved_row_records():
      # `rule` is the PRODUCER; `validated` is the reliability state it writes. The
      # `unresolved` row names the producer, so the two tuples must agree exactly.
      assert DEGRADATION_ORDER == ATTEMPTED_PRODUCERS


  def test_only_the_llm_stage_is_ceiling_gated():
      assert CEILING_GATED_STAGES == frozenset({"llm"})
      assert CEILING_GATED_STAGES < set(DEGRADATION_ORDER)


  def test_a_stage_map_that_is_not_exactly_the_three_is_refused():
      recorder = Recorder()
      with pytest.raises(StageSetInvalid):
          FactResolver(
              stages={"direct": recorder.stage("direct")},
              pending_fields=lambda conn, f, c: (FIELD,),
              budget_exhausted=lambda key: False,
              model_route_permitted=lambda file_id: True,
              record_pass=recorder.record_pass,
              cache_key_for=lambda f, c: CACHE_KEY,
              screen_metadata=lambda conn, f, c: (),
          )


  def test_every_constructor_argument_is_a_required_keyword_with_no_default():
      for name, parameter in inspect.signature(FactResolver.__init__).parameters.items():
          if name == "self":
              continue
          assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, name
          assert parameter.default is inspect.Parameter.empty, name
      assert "screen_metadata" in inspect.signature(FactResolver.__init__).parameters


  def test_screen_metadata_runs_before_any_stage(p6):
      calls: list[str] = []

      def screen(conn, file_id, content_hash):
          calls.append("screen")
          return ()

      recorder = Recorder()
      resolver = FactResolver(
          stages={
              "direct": recorder.stage("direct", produces=("fact-direct",)),
              "rule": recorder.stage("rule"),
              "llm": None,
          },
          pending_fields=lambda conn, file_id, content_hash: (FIELD,),
          budget_exhausted=lambda key: False,
          model_route_permitted=lambda file_id: True,
          record_pass=recorder.record_pass,
          cache_key_for=lambda file_id, content_hash: CACHE_KEY,
          screen_metadata=screen,
      )
      resolve(resolver, p6)
      assert calls == ["screen"]
      assert recorder.calls[0] == "direct"


  def test_with_p8_absent_the_llm_route_does_not_exist_and_nothing_is_withheld(p6):
      # Done-means 17's shape: `llm=None` is the ordinary path, not an error path. A
      # route that does not exist is not a route that was barred, so no `unresolved`
      # row is written and neither ceiling nor privacy is consulted.
      recorder = Recorder()
      result = resolve(a_resolver(recorder, llm=None, permitted=False,
                                  exhausted=P6_CEILING_KEYS), p6)
      assert recorder.calls == ["direct", "rule"]
      assert result.stages_run == ("direct", "rule")
      assert result.stages_barred == {}
      assert result.deferred_against == ()
      assert unresolved_for_file(p6, FILE_ID, CONTENT_HASH) == []


  def test_the_pass_is_recorded_once_after_the_stages(p6):
      recorder = Recorder()
      resolve(a_resolver(recorder), p6)
      assert recorder.passes == [(FILE_ID, CONTENT_HASH)]


  # --- what a ceiling is allowed to do -----------------------------------------

  def test_a_reached_ceiling_defers_the_llm_route_and_substitutes_nothing(p6):
      recorder = Recorder()
      llm = recorder.stage("llm", produces=("fact-llm",))
      result = resolve(
          a_resolver(recorder, llm=llm, exhausted=("model.max_cost_per_scan",)), p6)

      # §8.6: the stronger route is subtracted; no weaker route takes its place. The
      # LLM stage was never entered, and no `possible` clue, below-margin candidate or
      # fuzzy date was promoted in its stead — `fact_ids` is exactly what `direct` and
      # `rule` returned.
      assert "llm" not in recorder.calls
      assert result.fact_ids == ("fact-direct",)
      assert result.stages_run == ("direct", "rule")
      assert result.stages_barred == {"llm": "budget"}
      assert result.deferred_against == ("model.max_cost_per_scan",)


  def test_the_deferral_is_a_row_naming_the_field_that_stayed_unknown(p6):
      recorder = Recorder()
      resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                         exhausted=("model.max_dossier_tokens_per_call",)), p6)

      rows = unresolved_for_file(p6, FILE_ID, CONTENT_HASH)
      assert len(rows) == 1
      assert rows[0]["field_key"] == FIELD
      assert rows[0]["reason"] == "budget_deferred"
      # §8.6: "mark the deferred stage, and leave the file or group in review rather
      # than guessing", which "avoids the false impression that an unprocessed file
      # was understood and found unimportant". The row records which producers had
      # already run, so a reader can see the work stopped rather than concluded.
      assert rows[0]["attempted_producers"] is not None


  def test_a_budget_deferral_is_not_an_abstention(p6):
      recorder = Recorder()
      resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                         exhausted=("model.max_cost_per_scan",)), p6)
      rows = unresolved_for_file(p6, FILE_ID, CONTENT_HASH, reason="budget_deferred")
      assert len(rows) == 1
      assert rows[0]["reason"] in NOT_ABSTENTIONS


  def test_multiple_exhausted_ceilings_are_all_attributed(p6):
      recorder = Recorder()
      result = resolve(a_resolver(
          recorder, llm=recorder.stage("llm"),
          exhausted=("model.max_cost_per_scan", "model.max_llm_calls_per_thousand_files")), p6)
      assert result.deferred_against == (
          "model.max_llm_calls_per_thousand_files", "model.max_cost_per_scan")


  # --- privacy is a prohibition, not a resource decision ------------------------

  def test_a_forbidden_model_route_withholds_and_does_not_defer(p6):
      recorder = Recorder()
      result = resolve(a_resolver(recorder, llm=recorder.stage("llm"), permitted=False), p6)

      assert "llm" not in recorder.calls
      assert result.stages_barred == {"llm": "privacy"}
      assert result.deferred_against == ()
      rows = unresolved_for_file(p6, FILE_ID, CONTENT_HASH)
      assert [row["reason"] for row in rows] == ["privacy_withheld"]


  def test_privacy_is_checked_before_the_ceiling_so_a_prohibition_is_never_reported_as_a_deferral(p6):
      # §8.4 is a prohibition — "enforced before content reaches any model or external
      # connector" — and a file that may NEVER go to a model is not a file waiting for
      # budget. Both bars at once must report the prohibition.
      recorder = Recorder()
      result = resolve(a_resolver(recorder, llm=recorder.stage("llm"),
                                  permitted=False, exhausted=P6_CEILING_KEYS), p6)
      assert result.stages_barred == {"llm": "privacy"}
      assert result.deferred_against == ()
      assert [row["reason"] for row in unresolved_for_file(p6, FILE_ID, CONTENT_HASH)] \
          == ["privacy_withheld"]


  def test_the_two_bars_have_two_reasons_and_neither_is_shared():
      assert REASON_BY_BAR == {"privacy": "privacy_withheld", "budget": "budget_deferred"}
      assert set(REASON_BY_BAR.values()) == set(NOT_ABSTENTIONS)


  # --- reporting ---------------------------------------------------------------

  def test_deferred_counts_reports_against_each_of_the_three_ceilings(p6):
      recorder = Recorder()
      result = resolve(a_resolver(
          recorder, llm=recorder.stage("llm"), pending=(FIELD,),
          exhausted=("model.max_cost_per_scan",)), p6)

      counts = deferred_counts(p6, results=(result,))
      assert set(counts) == set(P6_CEILING_KEYS)
      assert counts["model.max_cost_per_scan"] == 1
      assert counts["model.max_dossier_tokens_per_call"] == 0
      assert counts["model.max_llm_calls_per_thousand_files"] == 0


  def test_deferred_counts_refuses_a_ceiling_outside_p6s_three(p6):
      forged = ResolveResult(file_id=FILE_ID, content_hash=CONTENT_HASH,
                             deferred_against=("ocr.max_pages_per_file",))
      with pytest.raises(UnknownCeiling):
          deferred_counts(p6, results=(forged,))


  def test_a_result_with_no_deferral_contributes_nothing(p6):
      recorder = Recorder()
      result = resolve(a_resolver(recorder), p6)
      assert deferred_counts(p6, results=(result,)) == \
          {key: 0 for key in P6_CEILING_KEYS}


  def test_an_errored_result_is_constructible_without_a_resolve(p6):
      # `resolve` never swallows: a producer that raises propagates, because P6's
      # failures are ContractViolations. The scan loop that catches one still owes P2
      # an envelope, so the error result is a named constructor rather than a branch.
      result = ResolveResult.errored(file_id=FILE_ID, content_hash=CONTENT_HASH,
                                     error="rules.apply_rules: boom")
      assert result.error == "rules.apply_rules: boom"
      assert result.fact_ids == ()
      assert result.stages_run == ()


  def test_a_raising_producer_propagates(p6):
      recorder = Recorder()

      def boom(conn, file_id, content_hash):
          raise RuntimeError("boom")

      resolver = FactResolver(
          stages={"direct": recorder.stage("direct"), "rule": boom, "llm": None},
          pending_fields=lambda conn, f, c: (FIELD,),
          budget_exhausted=lambda key: False,
          model_route_permitted=lambda file_id: True,
          record_pass=recorder.record_pass,
          cache_key_for=lambda f, c: CACHE_KEY,
          screen_metadata=lambda conn, f, c: (),
      )
          resolve(resolver, p6)
      assert recorder.passes == []


  # --- the no-invention guard, by runtime introspection -------------------------

  def _numeric_constants(module) -> dict:
      """Every module-level name bound to a number, or to a collection containing one.

      Runtime introspection, not a source-text search: a text search matches comments
      and docstrings, and that false result has broken three tasks on this project.
      """
      found: dict = {}
      for name, value in vars(module).items():
          if name.startswith("_") or isinstance(value, bool):
              continue
          if isinstance(value, (int, float)):
              found[name] = value
          elif isinstance(value, Mapping):
              if any(isinstance(v, (int, float)) and not isinstance(v, bool)
                     for v in value.values()):
                  found[name] = value
          elif isinstance(value, (tuple, list, set, frozenset)):
              if any(isinstance(v, (int, float)) and not isinstance(v, bool)
                     for v in value):
                  found[name] = value
      return found


  def test_neither_module_defines_a_number():
      assert _numeric_constants(budgets_module) == {}
      assert _numeric_constants(resolver_module) == {}


  def test_the_resolver_imports_no_producer_module():
      # The producers arrive as injected `Stage` callables. Importing one here would
      # put a build-order edge inside a wave that has none, and would let a threshold,
      # a gazetteer or a regex catalogue reach this module through a sibling.
      allowed = {"facts.budgets", "facts.unresolved", "facts.resolver"}
      from_facts = {module for module in
                    (getattr(value, "__module__", None)
                     for value in vars(resolver_module).values())
                    if module and module.startswith("facts.")}
      assert from_facts <= allowed
  ```

- [ ] **Step 3: Run it and read the failure.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest tests/p6/test_p6_budgets.py -q
  ```

  **Expected FAILURE:** collection error —
  `ModuleNotFoundError: No module named 'facts.budgets'`. Nothing in the file is
  importable yet, so pytest reports one error and zero tests, not a failed assertion.

- [ ] **Step 4: Write `src/facts/budgets.py`, complete.**

  ```python
  # src/facts/budgets.py
  """§8.6 — the three ceilings P6 holds, and the one thing a ceiling may not change.

  §00, verbatim: "If the budget is exhausted, the product should retain extracted
  evidence, mark the deferred stage, and leave the file or group in review rather than
  guessing. Cost exhaustion must never turn into lower-quality automatic
  classification."

  Every one of P6's three ceilings is a `model.*` ceiling. That is not a coincidence to
  note in passing — it is what makes the sentence above mechanical here. By the time
  any ceiling is consulted, `direct` and `rule` have already run, so the only route a
  ceiling can close is the LLM route and there is no cheaper producer to fall back to.
  Degradation in P6 is subtraction, never substitution.

  P1 holds the ceiling VALUES and enforces none of them, so exhaustion arrives as an
  injected predicate — P3's precedent, widened from `Callable[[], bool]` to
  `Callable[[str], bool]` because §8.6's reporting requirement is per ceiling. No
  number is defined in this module.
  """
  from __future__ import annotations

  import sqlite3
  from typing import TYPE_CHECKING, Callable, Iterable

  from database_agent.budget import CEILING_KEYS, get_ceiling

  from facts.unresolved import unresolved_for_file

  if TYPE_CHECKING:  # `resolver` imports this module; the annotation must not.
      from facts.resolver import ResolveResult

  #: §8.6's three model ceilings, spelled with P1's keys. P1 publishes sixteen; the
  #: other thirteen belong to P4, P5, P9, P10, P11 and P13.
  P6_CEILING_KEYS: tuple[str, str, str] = (
      "model.max_llm_calls_per_thousand_files",
      "model.max_cost_per_scan",
      "model.max_dossier_tokens_per_call",
  )

  #: §8.6: "Direct facts and high-precision rules run first because they are cheap and
  #: reliable ... LLM calls are reserved for bounded ambiguities". P6's three producers
  #: in that order. These are PRODUCER names and they are deliberately the same three
  #: strings as `facts.unresolved.ATTEMPTED_PRODUCERS`, so an abstention row can name
  #: what ran. `rule` is the producer; `validated` is the reliability state it writes.
  DEGRADATION_ORDER: tuple[str, str, str] = ("direct", "rule", "llm")

  #: The only producer a ceiling can close, held as data so the resolver's gate is
  #: readable from this module rather than from an `if` buried in a loop.
  CEILING_GATED_STAGES: frozenset[str] = frozenset({"llm"})


  class UnknownCeiling(Exception):
      """A ceiling key outside P6's three was attributed a deferral."""


  def ceiling_values(conn: sqlite3.Connection) -> dict[str, int | None]:
      """P6's three ceilings as P1 currently holds them.

      Returned for reporting and for a caller assembling its own predicate. P6 does
      not compare against these numbers: comparing would put the enforcement here,
      and P1's own docstring is explicit that reading a ceiling is not enforcing it.
      """
      return {key: get_ceiling(conn, key) for key in P6_CEILING_KEYS}


  def exhausted_ceilings(*, budget_exhausted: Callable[[str], bool]) -> tuple[str, ...]:
      """Which of P6's three the caller reports exhausted, asked in published order.

      All of them are asked, not just the first: §8.6 requires P6 to report how much
      work it deferred against EACH ceiling, and a short-circuit would attribute a
      simultaneous exhaustion to whichever key happened to sort first.
      """
      return tuple(key for key in P6_CEILING_KEYS if budget_exhausted(key))


  def deferred_counts(conn: sqlite3.Connection, *,
                      results: Iterable["ResolveResult"]) -> dict[str, int]:
      """How many fact-resolution requests were deferred against each ceiling.

      Scan-scoped, and cross-checked against the records: the count for a result is
      the number of `budget_deferred` rows that result actually wrote, so the report
      cannot drift from the table. A result exhausted against two ceilings counts
      against both — §8.6 asks what each ceiling cost, not which one to blame.

      There is no per-ceiling column on `unresolved` and P6 owns exactly four tables,
      so the DURABLE per-ceiling record is Task 21's `stage_output.payload`, which
      carries `deferred_against` verbatim and which P2 stores and never parses.
      """
      counts: dict[str, int] = {key: 0 for key in P6_CEILING_KEYS}
      for result in results:
          if not result.deferred_against:
              continue
          rows = unresolved_for_file(conn, result.file_id, result.content_hash,
                                     reason="budget_deferred")
          for key in result.deferred_against:
              if key not in P6_CEILING_KEYS:
                  raise UnknownCeiling(
                      f"{key!r} is not one of P6's three model ceilings "
                      f"{P6_CEILING_KEYS}; P1 publishes it, another part holds it"
                  )
              counts[key] += len(rows)
      return counts


  # Asserted at import so a P1 rename is a startup failure rather than a silent
  # miscount: P6 names three of P1's sixteen keys and owns none of them.
  assert set(P6_CEILING_KEYS) <= set(CEILING_KEYS)
  ```

- [ ] **Step 5: Write `src/facts/resolver.py`, complete.**

  ```python
  # src/facts/resolver.py
  """The one entry point, sequencing P6's producers in §8.6's order.

  The order is a contract, not an implementation detail, which is why it is a
  sequencer and not three calls scattered through a caller: §00 says "The engine
  should degrade in a predictable order. Direct facts and high-precision rules run
  first because they are cheap and reliable."

  The producers arrive as injected `Stage` callables. This module imports none of
  them, so no threshold, gazetteer, regex catalogue or producer-string list can reach
  it — the caller binds those into the stage it hands over. It also means Tasks 17 and
  19, written in the same wave, are not build-order dependencies of this one.

  `resolve` never swallows an exception. P6's failures are ContractViolations and must
  propagate; a caller that catches one still owes P2 an envelope, and constructs it
  with `ResolveResult.errored`.
  """
  from __future__ import annotations

  import sqlite3
  from dataclasses import dataclass, field
  from types import MappingProxyType
  from typing import Callable, Mapping

  from facts.budgets import (
      CEILING_GATED_STAGES, DEGRADATION_ORDER, exhausted_ceilings,
  )
  from facts.unresolved import unresolved_for_file, write_unresolved

  #: One producer, one shape. The caller binds every strategy and every threshold into
  #: the callable before handing it over, so this module sees neither.
  Stage = Callable[[sqlite3.Connection, str, str], "tuple[str, ...]"]

  #: `facts.usable.record_pass`, bound by the caller to supply the tier set it needs.
  #: Injected rather than imported because `resolve`'s signature is fixed by the
  #: skeleton and has nowhere to carry `analysis_tiers`, and because determining which
  #: tiers a pass covered is a read over P4's runs that belongs to Task 19's owner.
  PassRecorder = Callable[[sqlite3.Connection, str, str], None]

  #: Why a ceiling-gated stage did not run, and the `unresolved` reason each produces.
  #: Two bars, two reasons, no shared bucket — and neither reason is an abstention.
  REASON_BY_BAR: Mapping[str, str] = MappingProxyType({
      "privacy": "privacy_withheld",
      "budget": "budget_deferred",
  })


  class StageSetInvalid(Exception):
      """The stage map is not exactly §8.6's three producers."""


  @dataclass(frozen=True)
  class ResolveResult:
      """What one pass over one file version did, in the terms §8.5 measures.

      `fact_ids` is what the producers returned. `reason_counts` is read back from the
      `unresolved` table rather than accumulated in memory, so Done-means 20's "the two
      are distinguishable from the records alone" is true by construction rather than
      by care.
      """
      file_id: str
      content_hash: str
      fact_ids: tuple[str, ...] = ()
      reason_counts: Mapping[str, int] = field(default_factory=dict)
      stages_run: tuple[str, ...] = ()
      stages_barred: Mapping[str, str] = field(default_factory=dict)
      deferred_against: tuple[str, ...] = ()
      error: str | None = None

      def __post_init__(self) -> None:
          object.__setattr__(self, "reason_counts",
                             MappingProxyType(dict(self.reason_counts)))
          object.__setattr__(self, "stages_barred",
                             MappingProxyType(dict(self.stages_barred)))

      @classmethod
      def errored(cls, *, file_id: str, content_hash: str,
                  error: str) -> "ResolveResult":
          """The stage failed. §8.5's fourth outcome still needs an envelope."""
          return cls(file_id=file_id, content_hash=content_hash, error=error)


  class FactResolver:
      """P6's single entry point. Constructed with every injected strategy; holds none.

      `stages` maps each of `DEGRADATION_ORDER` to a `Stage` or to `None`. `None` means
      the route does not exist — which is the ordinary case for `llm`, because P8 does
      not exist. A route that does not exist is NOT a route that was barred: nothing is
      withheld, nothing is deferred, and no `unresolved` row is written for it.

      `screen_metadata` is required and has no default. §2.2's tool-metadata
      suppression must fire **before** any producer; without this call `python-docx`
      can become a `direct` fact and Done-means 22 is unreachable. Task 9 publishes
      the helper; this constructor is the caller. `DEGRADATION_ORDER` stays the three
      producers — screening is not a fourth producer.

      Task 9's helper is keyword-only and takes the version's observations plus the
      two catalogue predicates. The production composition site binds a thin adapter
      with this constructor's three-positional shape::

          def screen(conn, file_id, content_hash):
              observations = observations_for_version(conn, file_id, content_hash)
              return screen_metadata(
                  conn, file_id=file_id, content_hash=content_hash,
                  observations=observations,
                  tool_producer_strings=TOOL_PRODUCER_STRINGS,
                  metadata_property_names=METADATA_PROPERTY_NAMES,
              )

      Tests in this task bind a no-op or a recorder. They do not import Task 9.
      """

      def __init__(self, *, stages: Mapping[str, Stage | None],
                   pending_fields: Callable[[sqlite3.Connection, str, str],
                                            "tuple[str, ...]"],
                   budget_exhausted: Callable[[str], bool],
                   model_route_permitted: Callable[[str], bool],
                   record_pass: PassRecorder,
                   cache_key_for: Callable[[str, str], str],
                   screen_metadata: Callable[[sqlite3.Connection, str, str],
                                            object]) -> None:
          if set(stages) != set(DEGRADATION_ORDER):
              raise StageSetInvalid(
                  f"stages must be exactly {DEGRADATION_ORDER}, got "
                  f"{tuple(sorted(stages))}"
              )
          self._stages = dict(stages)
          self._pending_fields = pending_fields
          self._budget_exhausted = budget_exhausted
          self._model_route_permitted = model_route_permitted
          self._record_pass = record_pass
          self._cache_key_for = cache_key_for
          self._screen_metadata = screen_metadata

      def resolve(self, conn: sqlite3.Connection, *, file_id: str,
                  content_hash: str) -> ResolveResult:
          stages_run: list[str] = []
          barred: dict[str, str] = {}
          deferred_against: tuple[str, ...] = ()
          fact_ids: list[str] = []

          # §2.2 fires before ranking. The return value is the survivor set;
          # stages that re-query observations still use field_permitted.
          # This call is what writes the unresolved row Done-means 22 requires.
          self._screen_metadata(conn, file_id, content_hash)

          for name in DEGRADATION_ORDER:
              stage = self._stages[name]
              if stage is None:
                  continue
              if name in CEILING_GATED_STAGES:
                  # §8.4 first: a handling class that forbids the model route is a
                  # PROHIBITION, and a file that may never reach a model is not a file
                  # waiting for budget to free up. Reporting it as a deferral would
                  # promise work that will never be done.
                  if not self._model_route_permitted(file_id):
                      barred[name] = "privacy"
                      continue
                  exhausted = exhausted_ceilings(
                      budget_exhausted=self._budget_exhausted)
                  if exhausted:
                      barred[name] = "budget"
                      deferred_against = exhausted
                      continue
              fact_ids.extend(stage(conn, file_id, content_hash))
              stages_run.append(name)

          if barred:
              self._write_bars(conn, file_id=file_id, content_hash=content_hash,
                               barred=barred, attempted=tuple(stages_run))

          # Only now: preamble rule 5's recorded pass means a pass that COMPLETED. A
          # producer that raised skipped this line, so `no_usable_facts` still raises
          # `FactPassNotRun` for that content hash rather than answering from a
          # half-written table.
          self._record_pass(conn, file_id, content_hash)

          counts: dict[str, int] = {}
          for row in unresolved_for_file(conn, file_id, content_hash):
              counts[row["reason"]] = counts.get(row["reason"], 0) + 1

          return ResolveResult(
              file_id=file_id, content_hash=content_hash,
              fact_ids=tuple(fact_ids), reason_counts=counts,
              stages_run=tuple(stages_run), stages_barred=barred,
              deferred_against=deferred_against,
          )

      def _write_bars(self, conn: sqlite3.Connection, *, file_id: str,
                      content_hash: str, barred: Mapping[str, str],
                      attempted: "tuple[str, ...]") -> None:
          """The unfinished work, recorded AS unfinished.

          §00: the product must avoid "the false impression that an unprocessed file
          was understood and found unimportant". An absent row gives exactly that
          impression, so every field the barred route would have attempted gets one.

          `evidence_refs` is empty and that is correct rather than lazy: the barred
          route never looked at an observation, and the SPEC's own column note says
          the refs are "the observation keys considered, where any were (may be
          empty)". The extracted evidence is retained where it always was — in P4's
          `evidence` table, which P6 never writes and which P4's
          `evidence_never_overwritten` trigger makes unfalsifiable.
          """
          cache_key = self._cache_key_for(file_id, content_hash)
          for stage_name, bar in barred.items():
              reason = REASON_BY_BAR[bar]
              for field_key in self._pending_fields(conn, file_id, content_hash):
                  write_unresolved(
                      conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, reason=reason,
                      attempted_producers=attempted + (stage_name,),
                      evidence_refs=(), cache_key=cache_key,
                  )
  ```

- [ ] **Step 6: Run it and read the pass.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest tests/p6/test_p6_budgets.py -q
  ```

  **Expected PASS:** 26 passed. Then confirm nothing else moved:

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q
  ```

- [ ] **Step 7: Commit.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && git add src/facts/budgets.py src/facts/resolver.py tests/p6/test_p6_budgets.py && git commit -m "feat(P6): §8.6's three model ceilings, the degradation order, and the resolver that subtracts rather than substitutes"
  ```

---

---

### Task 21: §8.5 / B7 — the `factual_validation` envelope, through P2's live writer

**Files:** create `src/facts/stage_output.py`; test `tests/p6/test_p6_stage_output.py`.

**Interfaces:**
- Consumes: `eval_harness.vocabulary.STAGE_IDS`, `OUTCOMES`, `BUDGET_STATES`, `DIMENSIONS`,
  `check_stage`, `check_dimension`; `eval_harness.replay.StageResult`;
  `eval_harness.stage_output.record_stage_output`, `DimensionValue`;
  `evidence_shape.store.runs_for_content`; `evidence_shape.canonical.canonical_json`;
  `facts.resolver.ResolveResult`.
- Produces: `STAGE_ID: str` (`"factual_validation"`), `DIMENSION: str` (`"fact"`),
  `ENVELOPE_FIELDS: tuple[str, ...]`, `UnsettledOutcome`,
  `fact_stage_output(*, result: ResolveResult) -> dict`,
  `fact_version_axes(conn, *, content_hash: str, model_identifier: str | None,
  prompt_fingerprint: str | None) -> dict`.

**Done-means:** 20 (the outcome half), 21.

---

**Two vocabularies that look like one, and the module exists partly to keep them apart.** P2 publishes
ten `STAGE_IDS` and ten `DIMENSIONS`, and they are **different lists**. Verified live:
`"factual_validation"` is `STAGE_IDS[1]`; `"fact"` is `DIMENSIONS[1]`. `check_stage("fact")` raises
`UnknownStage`; `check_dimension("factual_validation")` raises `UnknownDimension`. P6 spells each
once, in this module, and the test asserts the cross-substitution raises rather than silently
recording under the wrong name.

**The envelope is produced, not stored.** `eval_harness.replay.StageResult` is what a stage adapter
returns; P2 adds `run_id`, `stage_id` and `version_tuple_ref` from the run it is replaying. P5's
`extractors/stage_output.py` set this pattern and this module follows it, with one deliberate
difference: **P6 fills `values`**, and P5 does not. `StageResult`'s sixth field is
`values: Sequence[DimensionValue] = <factory>`, and §8.5's `fact` dimension is P6's to measure, so
`ENVELOPE_FIELDS` here is the **six** `StageResult` fields rather than P5's five.

**`inputs[]`, resolved against P5 as built rather than against a reading of the SPEC.** The SPEC says
`inputs[]` carries *"the `subject_ref`s of the `extraction` stage outputs it consumed"*.
`extractors.stage_output.extraction_stage_output` sets `"subject_ref": run["file_id"]` — read from
the live module, not inferred. So P6's `inputs` is `(file_id,)` while P6's own `subject_ref` is the
**content hash** (§8.2's identity for a file version). The two differ on purpose, and the test asserts
the P5 half rather than restating it, so a future change to P5's subject key breaks this test instead
of quietly mis-linking the two stages.

**No fact id goes in the payload.** §8.5 replays a bundle and diffs the stored forms. A `fact_id` is
minted per row and is not stable across two runs of the same corpus, so putting one in the payload
would make every replay report a divergence that is not one. The payload carries a **count** and the
reason histogram — everything §8.5's "Fact quality: did it abstain when evidence was absent?" needs,
and nothing that changes between two identical runs.

> **NEEDS-JOSEPH (new, found while writing this task): the §8.5 outcome table has no row for a
> privacy-only refusal, and P2's live writer makes the obvious candidates unreachable.**
>
> The SPEC's table has four reachable rows. Its `abstained` row is defined as *"every attempted field
> ended in an `unresolved` row with a **non-budget** reason"*, which would sweep `privacy_withheld`
> into `abstained`. But the SPEC's own `unresolved` rule 4 says the opposite in the same document:
> *"`budget_deferred` and `privacy_withheld` are **not** abstentions … conflating them would report a
> budget stop as a considered refusal."* And `deferred` is not available either: P2's
> `record_stage_output` raises `ValueError` unless `budget_state == "ceiling_reached"`, and a privacy
> stop reaches no ceiling.
>
> So a file that produced **zero** facts and whose only refusals are `privacy_withheld` has no
> representable outcome. That is a real gap between two ratified documents, not a choice this task
> may make, so it is **held open as a raise**: `UnsettledOutcome`, naming the question. Three things
> keep that from being reckless:
> - The case is narrow. `privacy_withheld` is written only when an LLM **stage exists** and a
>   handling class bars it. With P8 absent — Done-means 17's world, and today's — `stages["llm"]` is
>   `None`, the route does not exist, nothing is withheld, and this branch is unreachable.
> - Any field reachable by `direct` or `rule` is still answered, so a privacy bar with **any** fact
>   written reports `produced` and never reaches the raise.
> - Raising is this project's stated tie-break: *"the one that preserves more information, or that
>   makes a wrong outcome impossible rather than merely unlikely, wins"* — `planning/10-i4-learning-ops.md`,
>   verified by grep. (The skeleton's Task 19 attributes this sentence to `04-resolutions.md` **and**
>   `10-i4-learning-ops.md`; it is only in the latter. Reported, not fixed here — the skeleton is not
>   this task's file.) Recording a prohibition as a considered refusal is the wrong outcome the SPEC
>   names in words; a raise forces the decision instead of writing it.
>
> **Do not resolve this by picking an outcome.** Two candidate resolutions exist and both are
> Joseph's: add a `withheld` outcome to P2's five, or rule that `privacy_withheld` **is** an
> abstention for envelope purposes while remaining a non-abstention in the `unresolved` vocabulary.

---

- [ ] **Step 1: Read P2's live writer and P5's precedent — both, before writing anything.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -c "
  import inspect
  from eval_harness.vocabulary import STAGE_IDS, DIMENSIONS, OUTCOMES, BUDGET_STATES
  print('stage :', STAGE_IDS.index('factual_validation'), STAGE_IDS[1])
  print('dim   :', DIMENSIONS.index('fact'), DIMENSIONS[1])
  print('out   :', OUTCOMES); print('budget:', BUDGET_STATES)
  from eval_harness.replay import StageResult
  print('StageResult:', inspect.signature(StageResult))
  from eval_harness.stage_output import record_stage_output, DimensionValue
  print('record_stage_output:', inspect.signature(record_stage_output))
  print('DimensionValue:', inspect.signature(DimensionValue))
  from eval_harness.run import VERSION_AXES, VERSION_TUPLE_FIELDS
  print('axes:', VERSION_AXES); print('tuple:', VERSION_TUPLE_FIELDS)
  from extractors.stage_output import extraction_stage_output
  print('P5 subject_ref is the', 'file_id' if 'file_id' in inspect.getsource(extraction_stage_output) else '???')
  "
  ```

  Expected: `factual_validation` at index 1 of `STAGE_IDS`; `fact` at index 1 of `DIMENSIONS`;
  `OUTCOMES == ("produced","abstained","deferred","not_implemented","error")`;
  `BUDGET_STATES == ("within_ceiling","ceiling_reached")`;
  `StageResult(subject_ref, outcome, payload, inputs, budget_state, values=...)`;
  `VERSION_TUPLE_FIELDS` is seven, `VERSION_AXES` is six.

- [ ] **Step 2: Write the test file, complete.**

  Create `tests/p6/test_p6_stage_output.py`:

  ```python
  # tests/p6/test_p6_stage_output.py
  """§8.5 / B7 — P6's envelope, driven through P2's LIVE writer.

  Nothing here is asserted against a reconstruction of P2. Every outcome pairing goes
  into `eval_harness.stage_output.record_stage_output` and is read back out of the
  `stage_output` table, because B7's claim is that a budget stop and a considered
  refusal are "distinguishable from the records alone" — which is a claim about rows,
  not about a mapping table.
  """
  from __future__ import annotations

  import json

  import pytest

  from eval_harness.replay import StageResult
  from eval_harness.run import (
      VERSION_AXES, VERSION_TUPLE_FIELDS, record_version_tuple, start_run,
  )
  from eval_harness.stage_output import (
      DimensionValue, dimension_values, record_stage_output, stage_outputs,
  )
  from eval_harness.store import create_eval_schema
  from eval_harness.vocabulary import (
      BUDGET_STATES, DIMENSIONS, OUTCOMES, STAGE_IDS, UnknownDimension, UnknownStage,
      check_dimension, check_stage,
  )
  from evidence_shape.fixtures import by_number
  from evidence_shape.schema import create_evidence_schema
  from evidence_shape.store import record_run

  from extractors.stage_output import extraction_stage_output

  import facts.stage_output as stage_output_module
  from facts.resolver import ResolveResult
  from facts.stage_output import (
      DIMENSION, ENVELOPE_FIELDS, STAGE_ID, UnsettledOutcome, fact_stage_output,
      fact_version_axes,
  )

  FILE_ID = "file-01"
  #: Fixture 1's content hash, so the P4 half of this file uses the real one.
  CONTENT_HASH = "042896dc1966b8a6214e5383aba5b8b931cfa049d17aafa37eb8a77c859b95da"
  #: Three more file VERSIONS. P2's `stage_dimension_value` is keyed
  #: `(run_id, dimension, subject_ref)` — verified by execution, it raises
  #: `IntegrityError` on a second `fact` value for one subject in one run — so two
  #: results emitted into the same run must be two different subjects. That is P2
  #: enforcing "one envelope per subject P6 decides about", not a test convenience.
  CONTENT_HASH_B = "b" * 64
  CONTENT_HASH_C = "c" * 64
  CONTENT_HASH_D = "d" * 64


  def a_result(**overrides) -> ResolveResult:
      base = dict(file_id=FILE_ID, content_hash=CONTENT_HASH,
                  stages_run=("direct", "rule"))
      base.update(overrides)
      return ResolveResult(**base)


  PRODUCED = a_result(fact_ids=("fact-1",))
  ABSTAINED = a_result(content_hash=CONTENT_HASH_B,
                       reason_counts={"no_candidate_evidence": 2,
                                      "below_margin": 1})
  DEFERRED = a_result(content_hash=CONTENT_HASH_C,
                      reason_counts={"budget_deferred": 3},
                      stages_barred={"llm": "budget"},
                      deferred_against=("model.max_cost_per_scan",))
  ERRORED = ResolveResult.errored(file_id=FILE_ID, content_hash=CONTENT_HASH_D,
                                  error="rules.apply_rules: boom")


  @pytest.fixture()
  def p2_run(conn):
      """A live P2 run. Mirrors `tests/p5/test_p5_stage_output.py` exactly."""
      create_eval_schema(conn)
      ref = record_version_tuple(
          conn, extractor_versions={"pdf.text": "1.0.0"}, graph_algorithm_version=None,
          prompt_fingerprint=None, model_identifier=None,
          template_library_version=None, placement_scorer_version=None,
          analysis_tiers_enabled=["filesystem", "native"])
      run_id = start_run(conn, bundle_id="b-p6", run_kind="replay",
                         version_tuple_ref=ref, budget_ceilings={},
                         run_settings={"model_enabled": False,
                                       "embeddings_enabled": False},
                         pinned_plan_id=None, pinned_plan_version=None)
      return run_id, ref


  def emit(conn, p2_run, result: ResolveResult) -> int:
      run_id, ref = p2_run
      envelope = fact_stage_output(result=result)
      return record_stage_output(
          conn, run_id=run_id, stage_id=envelope["stage_id"],
          subject_ref=envelope["subject_ref"], outcome=envelope["outcome"],
          payload=envelope["payload"], version_tuple_ref=ref,
          inputs=envelope["inputs"], budget_state=envelope["budget_state"],
          dimension_values=envelope["values"])


  # --- two vocabularies that look like one --------------------------------------

  def test_the_stage_id_is_one_of_section_8_5s_ten():
      assert STAGE_ID == "factual_validation"
      assert STAGE_ID in STAGE_IDS
      assert check_stage(STAGE_ID) == STAGE_ID


  def test_the_dimension_is_fact_and_the_two_lists_are_not_interchangeable():
      assert DIMENSION == "fact"
      assert DIMENSION in DIMENSIONS
      assert DIMENSION not in STAGE_IDS
      assert STAGE_ID not in DIMENSIONS
      with pytest.raises(UnknownStage):
          check_stage(DIMENSION)
      with pytest.raises(UnknownDimension):
          check_dimension(STAGE_ID)


  # --- the envelope shape --------------------------------------------------------

  def test_the_envelope_is_exactly_p2s_stage_result_shape():
      envelope = fact_stage_output(result=PRODUCED)
      assert set(ENVELOPE_FIELDS) == set(envelope) - {"stage_id"}
      StageResult(**{k: v for k, v in envelope.items() if k != "stage_id"})


  def test_p6_fills_values_where_p5_does_not_because_the_fact_dimension_is_p6s():
      assert "values" in ENVELOPE_FIELDS
      envelope = fact_stage_output(result=PRODUCED)
      assert [value.dimension for value in envelope["values"]] == [DIMENSION]


  def test_subject_ref_is_the_content_hash_because_a_fact_is_per_file_version():
      assert fact_stage_output(result=PRODUCED)["subject_ref"] == CONTENT_HASH


  def test_inputs_carries_the_subject_refs_of_the_extraction_stage_outputs():
      # Asserted against P5 AS BUILT: `extraction_stage_output` keys its subject by
      # file id, so P6's `inputs[]` must be file ids even though P6's own subject is
      # the content hash. Reading P5's live envelope here means a change on that side
      # breaks this test instead of quietly mis-linking two stages.
      p5_envelope = extraction_stage_output(run={
          "file_id": FILE_ID, "content_hash": CONTENT_HASH,
          "extractor_name": "pdf.text", "extractor_version": "1.0.0",
          "source_type": "text_document", "analysis_tier": "native",
          "completeness": "complete", "observation_count": 3,
          "coverage": {"units": "pages", "processed": 1, "total": 1}})
      assert p5_envelope["subject_ref"] == FILE_ID
      assert fact_stage_output(result=PRODUCED)["inputs"] == (p5_envelope["subject_ref"],)


  # --- the four outcomes ---------------------------------------------------------

  def test_facts_written_is_produced_within_ceiling():
      envelope = fact_stage_output(result=PRODUCED)
      assert (envelope["outcome"], envelope["budget_state"]) == \
          ("produced", "within_ceiling")


  def test_evidence_based_refusal_is_abstained_within_ceiling():
      envelope = fact_stage_output(result=ABSTAINED)
      assert (envelope["outcome"], envelope["budget_state"]) == \
          ("abstained", "within_ceiling")


  def test_a_ceiling_is_deferred_ceiling_reached():
      envelope = fact_stage_output(result=DEFERRED)
      assert (envelope["outcome"], envelope["budget_state"]) == \
          ("deferred", "ceiling_reached")


  def test_a_ceiling_outranks_facts_because_deferred_work_must_be_visible_as_deferred():
      # §00: the product must avoid "the false impression that an unprocessed file was
      # understood and found unimportant". A run that wrote two facts AND hit a ceiling
      # reports `deferred`; reporting `produced` would hide the unfinished half.
      mixed = a_result(fact_ids=("fact-1", "fact-2"),
                       reason_counts={"budget_deferred": 1},
                       stages_barred={"llm": "budget"},
                       deferred_against=("model.max_dossier_tokens_per_call",))
      envelope = fact_stage_output(result=mixed)
      assert (envelope["outcome"], envelope["budget_state"]) == \
          ("deferred", "ceiling_reached")


  def test_the_stage_failed_is_error():
      envelope = fact_stage_output(result=ERRORED)
      assert envelope["outcome"] == "error"
      assert envelope["budget_state"] in BUDGET_STATES


  def test_every_outcome_p6_can_emit_is_one_of_p2s_five():
      for result in (PRODUCED, ABSTAINED, DEFERRED, ERRORED):
          assert fact_stage_output(result=result)["outcome"] in OUTCOMES


  # --- through P2's live writer --------------------------------------------------

  def test_produced_and_abstained_are_written_and_read_back(conn, p2_run):
      emit(conn, p2_run, PRODUCED)
      emit(conn, p2_run, ABSTAINED)
      rows = stage_outputs(conn, p2_run[0], stage_id=STAGE_ID)
      assert [row["outcome"] for row in rows] == ["produced", "abstained"]
      assert {row["budget_state"] for row in rows} == {"within_ceiling"}
      assert {row["subject_ref"] for row in rows} == {CONTENT_HASH, CONTENT_HASH_B}
      assert json.loads(rows[0]["inputs"]) == [FILE_ID]


  def test_the_two_are_distinguishable_from_the_records_alone(conn, p2_run):
      # Done-means 20. Nothing in this assertion consults P6: the reader has the
      # `stage_output` rows and only those.
      emit(conn, p2_run, ABSTAINED)
      emit(conn, p2_run, DEFERRED)
      rows = stage_outputs(conn, p2_run[0], stage_id=STAGE_ID)
      pairs = [(row["outcome"], row["budget_state"]) for row in rows]
      assert pairs == [("abstained", "within_ceiling"),
                       ("deferred", "ceiling_reached")]
      deferred_payload = json.loads(rows[1]["payload"])
      assert deferred_payload["unresolved_reasons"] == {"budget_deferred": 3}
      assert deferred_payload["deferred_against"] == ["model.max_cost_per_scan"]


  def test_p2s_writer_refuses_the_pairing_p6_must_never_emit(conn, p2_run):
      # P6 does not need to invent B7's rule; it needs to not fight it. Proof that the
      # rule is live rather than remembered.
      run_id, ref = p2_run
      with pytest.raises(ValueError):
          record_stage_output(conn, run_id=run_id, stage_id=STAGE_ID,
                              subject_ref=CONTENT_HASH, outcome="abstained",
                              payload=None, version_tuple_ref=ref, inputs=(FILE_ID,),
                              budget_state="ceiling_reached")
      with pytest.raises(ValueError):
          record_stage_output(conn, run_id=run_id, stage_id=STAGE_ID,
                              subject_ref=CONTENT_HASH, outcome="deferred",
                              payload=None, version_tuple_ref=ref, inputs=(FILE_ID,),
                              budget_state="within_ceiling")


  def test_an_envelope_is_emitted_for_a_file_that_produced_facts_and_for_one_that_did_not(conn, p2_run):
      # Done-means 21, both halves, in one run.
      emit(conn, p2_run, PRODUCED)
      emit(conn, p2_run, ABSTAINED)
      rows = stage_outputs(conn, p2_run[0], stage_id=STAGE_ID)
      assert len(rows) == 2
      assert all(row["version_tuple_ref"] == p2_run[1] for row in rows)


  def test_the_dimension_value_lands_under_fact_and_carries_its_own_outcome(conn, p2_run):
      emit(conn, p2_run, PRODUCED)
      values = dimension_values(conn, p2_run[0], dimension=DIMENSION)
      assert len(values) == 1
      assert values[0]["stage_id"] == STAGE_ID
      assert values[0]["subject_ref"] == CONTENT_HASH
      assert values[0]["outcome"] == "produced"
      assert json.loads(values[0]["value"]) == {"fact_count": 1, "unresolved_count": 0}


  def test_a_dimension_value_with_nothing_produced_is_null(conn, p2_run):
      emit(conn, p2_run, ABSTAINED)
      values = dimension_values(conn, p2_run[0], dimension=DIMENSION)
      assert values[0]["outcome"] == "abstained"
      assert values[0]["value"] is None


  # --- the payload ---------------------------------------------------------------

  def test_the_payload_is_p6s_own_and_carries_no_fact_id():
      # §8.5 diffs STORED FORMS across two runs. A `fact_id` is minted per row and is
      # not stable between two runs of the same corpus, so one in the payload would
      # report a divergence that is not one.
      payload = json.loads(fact_stage_output(result=PRODUCED)["payload"])
      assert payload["fact_count"] == 1
      assert "fact-1" not in fact_stage_output(result=PRODUCED)["payload"]
      assert set(payload) == {"fact_count", "unresolved_reasons", "stages_run",
                              "stages_barred", "deferred_against", "error"}


  def test_the_payload_is_byte_stable_for_the_same_result():
      first = fact_stage_output(result=DEFERRED)["payload"]
      second = fact_stage_output(result=a_result(
          content_hash=CONTENT_HASH_C, reason_counts={"budget_deferred": 3},
          stages_barred={"llm": "budget"},
          deferred_against=("model.max_cost_per_scan",)))["payload"]
      assert first == second


  # --- the two refusals this module makes ----------------------------------------

  def test_a_privacy_only_refusal_has_no_settled_outcome_and_is_held_open():
      # NEEDS-JOSEPH, stated in this task's preamble: the §8.5 table would call this
      # `abstained`, the SPEC's `unresolved` rule 4 forbids exactly that, and P2's
      # writer makes `deferred` unreachable without a ceiling. Held open as a raise.
      withheld = a_result(reason_counts={"privacy_withheld": 2},
                          stages_barred={"llm": "privacy"})
      with pytest.raises(UnsettledOutcome):
          fact_stage_output(result=withheld)


  def test_a_privacy_bar_that_still_produced_a_fact_reports_produced():
      # The raise is narrow: any field reachable by `direct` or `rule` is still
      # answered, and P8 absent means nothing is ever withheld at all.
      partial = a_result(fact_ids=("fact-1",),
                         reason_counts={"privacy_withheld": 1},
                         stages_barred={"llm": "privacy"})
      assert fact_stage_output(result=partial)["outcome"] == "produced"


  def test_a_result_with_no_record_at_all_is_refused():
      # B7's whole point: without the `unresolved` row, §3.6's "no fact" is a missing
      # row and P2 cannot tell a considered refusal from a crash or a skip. A result
      # with neither a fact nor a reason is that missing row, and it is a bug in the
      # producer, not an outcome to report.
      with pytest.raises(ValueError):
          fact_stage_output(result=a_result())


  # --- P6's slice of the version tuple -------------------------------------------

  @pytest.fixture()
  def p4_run(conn):
      create_evidence_schema(conn)
      record_run(conn, by_number(1).run)
      return by_number(1).run


  def test_fact_version_axes_supplies_p6s_three_and_assembles_no_tuple(conn, p4_run):
      axes = fact_version_axes(conn, content_hash=p4_run.content_hash,
                               model_identifier=None, prompt_fingerprint=None)
      assert set(axes) == {"extractor_versions", "model_identifier",
                           "prompt_fingerprint"}
      assert set(axes) < set(VERSION_AXES)
      assert axes["extractor_versions"] == {"pdf.text": "1.0.0"}


  def test_the_axes_merge_into_p2s_seven_field_tuple(conn, p4_run):
      create_eval_schema(conn)
      axes = fact_version_axes(conn, content_hash=p4_run.content_hash,
                               model_identifier="claude-x", prompt_fingerprint="sha256:ab")
      ref = record_version_tuple(
          conn, graph_algorithm_version=None, template_library_version=None,
          placement_scorer_version=None, analysis_tiers_enabled=["native"], **axes)
      assert ref.startswith("sha256:")
      assert set(axes) <= set(VERSION_TUPLE_FIELDS)


  def test_two_versions_of_one_extractor_are_refused_rather_than_resolved(conn):
      # §3.4's cache key is per (extractor, version) and a map cannot hold both, so a
      # caller comparing two extractor versions is comparing two runs. Same rule P5
      # states on its own half of this axis.
      import dataclasses
      create_evidence_schema(conn)
      run = by_number(1).run
      record_run(conn, run)
      record_run(conn, dataclasses.replace(run, run_id="run-01b",
                                           extractor_version="2.0.0"))
      with pytest.raises(ValueError):
          fact_version_axes(conn, content_hash=run.content_hash,
                            model_identifier=None, prompt_fingerprint=None)


  def test_the_module_defines_no_number():
      numbers = {name: value for name, value in vars(stage_output_module).items()
                 if not name.startswith("_") and not isinstance(value, bool)
                 and isinstance(value, (int, float))}
      assert numbers == {}
  ```

- [ ] **Step 3: Run it and read the failure.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest tests/p6/test_p6_stage_output.py -q
  ```

  **Expected FAILURE:** collection error —
  `ModuleNotFoundError: No module named 'facts.stage_output'`. One error, zero tests.

- [ ] **Step 4: Write `src/facts/stage_output.py`, complete.**

  ```python
  # src/facts/stage_output.py
  """§8.5 / B7 — P2's envelope, produced by P6 and stored by P2.

  "P6 emits a `stage_output` with `stage_id = factual_validation`, a populated
  `inputs[]`, and the version tuple, for a file that produced facts and for a file
  that produced none."

  Produced, not stored: `eval_harness.replay.StageResult` is the shape a stage adapter
  returns, and P2 adds `run_id`, `stage_id` and `version_tuple_ref` from the run it is
  replaying. P5's `extractors/stage_output.py` set this pattern; this module follows it
  with one deliberate difference — P6 fills `values`, because §8.5's `fact` dimension is
  P6's to measure and P5 has no dimension of its own to report here.

  TWO VOCABULARIES THAT LOOK LIKE ONE. P2 publishes ten `STAGE_IDS` and ten
  `DIMENSIONS` and they are different lists: P6's stage is `factual_validation`, P6's
  dimension is `fact`, and each raises under the other's checker. They are spelled here
  and nowhere else in `facts`.
  """
  from __future__ import annotations

  import sqlite3

  from evidence_shape.canonical import canonical_json
  from evidence_shape.store import runs_for_content

  from eval_harness.stage_output import DimensionValue
  from eval_harness.vocabulary import check_dimension, check_stage

  from facts.resolver import ResolveResult

  #: Stage 2 of §8.5's ten. Checked at import, so a P2 rename is a startup failure.
  STAGE_ID: str = check_stage("factual_validation")

  #: §8.5's `fact` dimension — NOT the stage id, and not interchangeable with it.
  DIMENSION: str = check_dimension("fact")

  #: `eval_harness.replay.StageResult`'s six fields, as P6 fills them. P5 fills five;
  #: the sixth is `values`, and it is P6's because the `fact` dimension is P6's.
  ENVELOPE_FIELDS: tuple[str, ...] = ("subject_ref", "outcome", "payload", "inputs",
                                      "budget_state", "values")


  class UnsettledOutcome(Exception):
      """A result whose §8.5 outcome the design does not settle.

      One case only: zero facts, at least one `privacy_withheld` refusal, and no
      ceiling. The §8.5 table would call it `abstained`; the SPEC's `unresolved`
      rule 4 says `privacy_withheld` is not an abstention; and P2's writer refuses
      `deferred` without `ceiling_reached`. NEEDS-JOSEPH — see this task's preamble.
      Unreachable while P8 is absent, because a route that does not exist is not a
      route that was barred.
      """


  def fact_stage_output(*, result: ResolveResult) -> dict:
      """One envelope for one `(file_id, content_hash)` P6 decided about.

      `subject_ref` is the CONTENT HASH — §8.2's identity for a file version, and the
      thing a fact is keyed by. `inputs` is the file id, because that is what P5's
      `extraction` stage keys its own subject by (`extractors.stage_output`), and
      §8.5 links the two stages by that ref.
      """
      unresolved_count = sum(result.reason_counts.values())
      outcome, budget_state = _outcome_for(result, unresolved_count=unresolved_count)
      payload = canonical_json({
          # No fact id: §8.5 diffs stored forms across runs and a minted id is not
          # stable between two runs of the same corpus.
          "fact_count": len(result.fact_ids),
          "unresolved_reasons": dict(result.reason_counts),
          "stages_run": list(result.stages_run),
          "stages_barred": dict(result.stages_barred),
          "deferred_against": list(result.deferred_against),
          "error": result.error,
      })
      value = ({"fact_count": len(result.fact_ids),
                "unresolved_count": unresolved_count}
               if outcome == "produced" else None)
      return {
          "stage_id": STAGE_ID,
          "subject_ref": result.content_hash,
          "outcome": outcome,
          "payload": payload,
          "inputs": (result.file_id,),
          "budget_state": budget_state,
          "values": (DimensionValue(dimension=DIMENSION,
                                    subject_ref=result.content_hash,
                                    outcome=outcome, value=value),),
      }


  def _outcome_for(result: ResolveResult, *, unresolved_count: int) -> tuple[str, str]:
      """The §8.5 table, in the one order that keeps unfinished work visible.

      The ceiling is checked BEFORE the facts. A run that wrote two facts and then hit
      a ceiling reports `deferred`: §8.6 says to "mark the deferred stage, and leave
      the file or group in review rather than guessing", and `produced` would hide the
      half that never ran. This is not a widening of the SPEC's first row — that row
      already reads `within_ceiling`.
      """
      if result.error is not None:
          return "error", ("ceiling_reached" if result.deferred_against
                           else "within_ceiling")
      if result.deferred_against:
          return "deferred", "ceiling_reached"
      if result.fact_ids:
          return "produced", "within_ceiling"
      if result.reason_counts.get("privacy_withheld"):
          raise UnsettledOutcome(
              "zero facts and a privacy-withheld refusal has no §8.5 outcome: the "
              "table would say 'abstained', the SPEC's unresolved rule 4 forbids it, "
              "and P2 refuses 'deferred' without a ceiling. NEEDS-JOSEPH."
          )
      if unresolved_count:
          return "abstained", "within_ceiling"
      raise ValueError(
          "a result with no fact and no `unresolved` row is the missing row B7 exists "
          "to forbid: P2 cannot tell a considered refusal from a crash or a skip"
      )


  def fact_version_axes(conn: sqlite3.Connection, *, content_hash: str,
                        model_identifier: str | None,
                        prompt_fingerprint: str | None) -> dict:
      """P6's three axes of §8.5's seven-field version tuple.

      P6 SUPPLIES axes; it does not assemble the tuple — the other four belong to P9,
      P10, P11 and the caller, and `eval_harness.run.record_version_tuple` refuses a
      partial one. The caller merges these three in.

      `extractor_versions` is P6's slice of P4's runs for this content hash. Two
      versions of one extractor in one tuple is refused rather than resolved: §3.4's
      cache key is per (extractor, version) and a map cannot hold both, so a caller
      comparing two extractor versions is comparing two runs.
      """
      versions: dict[str, str] = {}
      for run in runs_for_content(conn, content_hash):
          name, version = run.extractor_name, run.extractor_version
          if versions.get(name, version) != version:
              raise ValueError(
                  f"{name!r} appears at two versions, {versions[name]!r} and "
                  f"{version!r}; §8.5's tuple holds one version per extractor"
              )
          versions[name] = version
      return {
          "extractor_versions": versions,
          "model_identifier": model_identifier,
          "prompt_fingerprint": prompt_fingerprint,
      }
  ```

- [ ] **Step 5: Run it and read the pass.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest tests/p6/test_p6_stage_output.py -q
  ```

  **Expected PASS:** 27 passed. Then the whole suite, which must be unchanged apart from
  the two new files:

  ```bash
  cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -m pytest -q
  ```

- [ ] **Step 6: Commit.**

  ```bash
  cd "/Users/jy/GRAPH AGENT" && git add src/facts/stage_output.py tests/p6/test_p6_stage_output.py && git commit -m "feat(P6): the factual_validation envelope through P2's live writer, and the privacy-only outcome held open"
  ```

---

### Task 22: §8.7 correction learning — query before propose (I4)

**Files:**
- Create: `src/facts/learning.py`
- Test: `tests/p6/test_p6_learning.py`

**Interfaces:**
- Consumes: `database_agent.learning` — `learning_records`, `reset_cutoff`;
  `database_agent.events` — `CORRECTION_SCOPES`, `CORRECTION_FIELDS`, `append_event`;
  `evidence_shape.canonical` — `canonical_json`; `facts.authorship` — `AUTHORED_EVENT_TYPES`,
  `event_defaults`.
- Produces: `PROPOSAL_CLASS: str` (`"fact"`), `POLARITIES: tuple[str, str]`,
  `MalformedCorrection`, `basis_key(*, file_id, field_key, value_id) -> str`,
  `is_suppressed(conn, *, scope, subject_id, file_id, field_key, value_id) -> bool`,
  `record_correction(conn, *, action, scope, subject, polarity, file_id, field_key, value_id,
  evidence_refs, user_id, observed_at) -> int`.

**Done-means:** none numbered; §8.7's obligations and I4's query-before-propose rule.

---

**Which half of this task binds now, and which is owed to P13's wave.** §8.7's corrections arrive
through P13's `review_action`, and **P13 does not exist**. That splits this task cleanly and the
split must be stated before the code, because a reader who assumes both halves are live will look
for a call site that is not there.

| | Built here | Reachable today | Owed to |
|---|---|---|---|
| **The read** — `basis_key`, `PROPOSAL_CLASS`, `is_suppressed` | yes | **yes, and it must be** | — |
| **The write** — `record_correction` | yes | **no** — nothing in this plan calls it | P13 routes the gesture |
| The gesture surface that collects `review_action` | no | — | P13 |
| The inspect / reset UI, and the call to P1's `reset_preferences` | no | — | P13 |
| The resolver's *call site* for the guard | no | — | Task 20 |

**The read half binds now even though the write half cannot fire**, and the reason is ordering, not
completeness. §8.7 requires that a rejected suggestion be **stored** and **not re-proposed** — I4
states the consequence for P6 as *"Before writing a `file_facts` row that would revive a `rejected`
claim … Leave the `rejected` row in place; do not propose the same `(field, value)` again."* A guard
that arrives after the first fact is written is a guard that has already failed once. So
`is_suppressed` ships with the fact tables, answers correctly against an empty store (`False`, no
records, nothing suppressed), and is correct on the day P13 starts filling the store. Building it
later would mean shipping a fact writer with a known missing check.

`record_correction` is built here rather than deferred because P6 **authors** the fact-level
consequence and P1 **writes** the event (M8) — the authorship is P6's whichever part collects the
gesture. It is P13's stand-in, and P6's tests drive it directly, exactly as the skeleton says of
every P13 fixture: *"Tests drive the fixture directly."*

**P6 mints no new §8.2 event type here, and that is the point of I4's design.** A user correction is
identified by two ordinary columns — `proposal_class` and `basis_key` — carried beside the eleven on
an ordinary event, never by a type of its own. Verified live: `database_agent.events.CORRECTION_FIELDS`
is `("correction_scope", "correction_subject", "polarity", "proposal_class", "basis_key")` and the
`events` table carries all five as real columns. The two event types this module uses are P6's own
authored pair from Task 1, `("fact creation", "fact rejection")`, both already members of §8.2's
reserved nineteen (verified: both are in `RESERVED_EVENT_TYPES`, both spelled with a space). Nothing
is registered, and a hypothetical `fact_correction` type would raise `UnregisteredEventType` at run
time — registration is a spec-level act, not a call.

**Why the basis key is canonical JSON and not a digest.** I4 fixes P6's equivalence as
`proposal_class = fact`, `basis_key = (file_id, field, value_id)`, and P1's `basis_key` is one TEXT
column — so the triple has to be serialized, and the deferred table names this task as the one place
that serialization may live. Three candidates:

- `f"{file_id}|{field_key}|{value_id}"` — **rejected, not injective.** A `|` inside any part collides
  two different claims onto one key, and a collision here silently suppresses a proposal the user
  never rejected.
- `sha256_of(file_id, field_key, value_id)` — injective, and rejected for a different reason: §8.7
  requires *"The user should be able to inspect or reset learned preferences, so personalization
  remains understandable and reversible."* A store whose every row's basis is an opaque digest is
  not inspectable, and P1 stores the column verbatim for exactly that reason.
- **`canonical_json({"field_key": …, "file_id": …, "value_id": …})` — chosen.** Injective, because
  JSON escapes its own delimiters; readable in a row dump; and it reuses P4's single canonical form
  rather than minting a second serializer in a project whose replay diff (§8.5) breaks the moment two
  equal records serialize two ways. `canonical_json` sorts keys, so the argument order at the call
  site cannot change the stored key.

**Why `reset_cutoff` is consumed by the test and not by the module.** `learning_records` already
applies the cutoff internally — verified by execution: a rejection appended, then
`reset_preferences` at the same scope and subject, and `learning_records` returns zero rows while the
rejection row is still in `events`. Calling `reset_cutoff` again inside `is_suppressed` would put the
cutoff rule in a second place, which is the defect class this project keeps hitting. The test
consumes it to **prove the mechanism** — that the reset's `event_id` is the cutoff and the rejection
sits below it — rather than to trust a docstring.

**Where the guard is called from.** Task 22 builds the guard; **Task 20's resolver is the call
site.** This task's test proves the guard's behaviour and proves the composition with a
resolver-shaped four-line helper defined in the test, so the red-green cycle is self-contained and
does not depend on Task 4's `write_fact` keyword list or on a conftest fixture whose name is not in
any published contract. The guard is read-only: it appends no event, writes no fact, and mutates
nothing — asserted, because a "guard" that writes is a guard that changes what it is guarding.

**Two names beyond the skeleton's four, both flagged.** `POLARITIES` is I4's own vocabulary
(*"`polarity ∈ accept | reject`** is the third required field and is not cosmetic"*) and Task 25's
introspection needs it published rather than inlined. `MalformedCorrection` follows the pattern
Tasks 2, 4 and 5 already set (`FieldNotInCatalogue`, `EvidenceRequired`) — `events` is append-only,
so a malformed correction cannot be repaired after the fact and must be refused at the writer.

**One thing this task deliberately does not decide.** I4's rule 4 is literal: *"On a record with
`polarity = reject` that no later reset covers: does not emit the proposal. A `polarity = accept`
record at the same `basis_key` is not a suppression and must not be read as one."* It says an accept
is not itself a suppression; it does **not** say a later accept *lifts* an earlier reject. Only a
reset does, in I4's text. This module implements the literal rule — **any** unreset reject at that
scope, subject, class and basis suppresses — and does not invent a newest-wins override. If Joseph
wants an accept to lift a reject without a reset, that is a decision, not a bug fix.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_learning.py
"""§8.7 correction learning: the query-before-propose guard, and what P6 may author.

The read half is live today. The write half is P13's stand-in -- P13 does not exist,
so these tests drive `record_correction` directly, which is how every P13 surface is
exercised in this plan.
"""
from __future__ import annotations

import inspect
import json
import sqlite3

import pytest

from database_agent import db
from database_agent.events import (
    CORRECTION_FIELDS,
    CORRECTION_SCOPES,
    RESERVED_EVENT_TYPES,
    MalformedEvent,
    append_event,
)
from database_agent.learning import learning_records, reset_cutoff, reset_preferences
from facts import learning as learning_module
from facts.authorship import AUTHORED_EVENT_TYPES
from facts.learning import (
    POLARITIES,
    PROPOSAL_CLASS,
    MalformedCorrection,
    basis_key,
    is_suppressed,
    record_correction,
)

CLOCK = "2026-08-22T09:00:00+00:00"
REF = "sha256:" + "e" * 64
OTHER_REF = "sha256:" + "d" * 64


@pytest.fixture()
def conn(tmp_path):
    connection = db.open_database(tmp_path / "p6-learning.db")
    db.create_schema(connection)
    yield connection
    connection.close()


def a_rejection(connection, **overrides) -> int:
    """The walking case: the user rejects `subject = BUSIB 4300` on one file."""
    fields = dict(
        action="reject_fact",
        scope="file",
        subject="file-1",
        polarity="reject",
        file_id="file-1",
        field_key="subject",
        value_id="value-busib-4300",
        evidence_refs=(REF,),
        user_id="user-1",
        observed_at=CLOCK,
    )
    fields.update(overrides)
    return record_correction(connection, **fields)


def event_count(connection) -> int:
    return connection.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]


# --- what P6 identifies a correction by -------------------------------------------


def test_the_proposal_class_is_the_claim_and_p6_mints_no_event_type():
    # I4's equivalence table: P6 owns proposal_class `fact`, basis (file_id, field, value_id).
    assert PROPOSAL_CLASS == "fact"
    # The two names this module writes are P6's own authored pair, and both are already
    # among 8.2's reserved nineteen -- so P6 registers nothing and mints nothing.
    assert AUTHORED_EVENT_TYPES == ("fact creation", "fact rejection")
    for name in AUTHORED_EVENT_TYPES:
        assert name in RESERVED_EVENT_TYPES
    assert POLARITIES == ("accept", "reject")


def test_the_basis_key_is_i4s_triple_serialized_once_and_readably():
    key = basis_key(file_id="file-1", field_key="subject", value_id="value-busib-4300")
    parsed = json.loads(key)
    # Exactly I4's three parts, and nothing else: no plan version, no dossier hash,
    # no display label, no member set.
    assert set(parsed) == {"file_id", "field_key", "value_id"}
    assert parsed["file_id"] == "file-1"
    assert parsed["field_key"] == "subject"
    assert parsed["value_id"] == "value-busib-4300"


def test_the_basis_key_is_deterministic_and_independent_of_argument_order():
    first = basis_key(file_id="f", field_key="subject", value_id="v")
    second = basis_key(value_id="v", file_id="f", field_key="subject")
    assert first == second


def test_the_basis_key_is_injective_over_its_three_parts():
    # A delimiter-joined key would collide these two, and a collision silently
    # suppresses a proposal the user never rejected.
    left = basis_key(file_id="a|b", field_key="subject", value_id="v")
    right = basis_key(file_id="a", field_key="b|subject", value_id="v")
    assert left != right
    assert basis_key(file_id="", field_key="x", value_id="y") != \
        basis_key(file_id="x", field_key="", value_id="y")


# --- the guard --------------------------------------------------------------------


def test_an_empty_store_suppresses_nothing(conn):
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is False


def test_an_unreset_reject_suppresses_the_same_claim(conn):
    a_rejection(conn)
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is True


def test_the_guard_writes_nothing(conn):
    a_rejection(conn)
    before = event_count(conn)
    is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    )
    is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-other",
    )
    assert event_count(conn) == before


def test_a_different_basis_key_at_the_same_scope_still_emits(conn):
    a_rejection(conn)
    # A different value under the same field is a different claim (I4: "A different
    # value is a different proposal").
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4400",
    ) is False
    # A different field on the same file is a different claim.
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="term", value_id="value-busib-4300",
    ) is False


def test_a_record_at_the_wrong_proposal_class_is_ignored(conn):
    key = basis_key(file_id="file-1", field_key="subject", value_id="value-busib-4300")
    # P11's `placement` class, same scope, same subject, same basis string. P6 must
    # not read another part's rejection as its own.
    append_event(
        conn, event_type="placement recommendation", subsystem="P11",
        component_version="0.0.0", observed_at=CLOCK, explanation="{}",
        correction_scope="file", correction_subject="file-1", polarity="reject",
        proposal_class="placement", basis_key=key, user_id="user-1",
    )
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is False


def test_an_accept_is_not_a_suppression(conn):
    a_rejection(conn, action="confirm_fact", polarity="accept", evidence_refs=())
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is False


def test_a_reset_at_that_scope_and_subject_allows_emission_again(conn):
    rejection_id = a_rejection(conn)
    reset_id = reset_preferences(
        conn, "file", "file-1",
        author="P13", component_version="0.0.0", user_id="user-1",
    )
    # The mechanism, not a docstring: the reset's event_id IS the cutoff, and the
    # rejection sits below it, so `learning_records` stops returning it.
    assert reset_cutoff(conn, "file", "file-1") == reset_id
    assert rejection_id < reset_id
    assert learning_records(conn, "file", "file-1") == []
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is False
    # R6: the reset deleted nothing. The rejection is still in the append-only log.
    surviving = conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE event_id = ?", (rejection_id,)
    ).fetchone()["n"]
    assert surviving == 1


def test_the_guard_stops_the_write_a_resolver_would_have_made(conn):
    """Task 20's resolver shape, four lines of it, so the composition is proved here."""
    a_rejection(conn)
    claims = [
        ("file-1", "subject", "value-busib-4300"),   # the rejected one
        ("file-1", "subject", "value-busib-4400"),   # a different value
        ("file-2", "subject", "value-busib-4300"),   # a different file
    ]
    written = []
    for file_id, field_key, value_id in claims:
        if is_suppressed(
            conn, scope="file", subject_id=file_id,
            file_id=file_id, field_key=field_key, value_id=value_id,
        ):
            continue
        written.append((file_id, field_key, value_id))
    assert written == [
        ("file-1", "subject", "value-busib-4400"),
        ("file-2", "subject", "value-busib-4300"),
    ]


# --- 8.7's scopes, and the two worked examples ------------------------------------


def test_every_scope_p1_accepts_p6_can_record(conn):
    assert CORRECTION_SCOPES == ("file", "group", "node", "template", "domain", "corpus")
    for index, scope in enumerate(CORRECTION_SCOPES):
        a_rejection(conn, scope=scope, subject=f"subject-{index}")
    assert event_count(conn) == len(CORRECTION_SCOPES)


def test_a_seventh_scope_is_refused_by_p1_and_p6_does_not_respell_the_six(conn):
    with pytest.raises(MalformedEvent):
        a_rejection(conn, scope="semester")
    # P6 holds no copy of the six: the refusal came from P1's writer, which is the
    # single place they are spelled.
    assert "semester" not in CORRECTION_SCOPES


def test_one_transcript_does_not_teach_the_engine_that_all_transcripts_belong_there(conn):
    # 8.7's own worked case: "a user may say that one particular transcript belongs in
    # a Columbia packet but should not teach the engine that all transcripts belong there."
    a_rejection(
        conn, scope="file", subject="transcript-1", file_id="transcript-1",
        field_key="institution", value_id="value-columbia",
    )
    assert is_suppressed(
        conn, scope="file", subject_id="transcript-1",
        file_id="transcript-1", field_key="institution", value_id="value-columbia",
    ) is True
    # A second transcript is untouched -- scope is exact, and the basis names the file.
    assert is_suppressed(
        conn, scope="file", subject_id="transcript-2",
        file_id="transcript-2", field_key="institution", value_id="value-columbia",
    ) is False
    # And the file-scoped record is invisible to a corpus-scoped read (P1's rule).
    assert learning_records(conn, "corpus", "transcript-1") == []


def test_a_repeated_corpus_scoped_rejection_is_readable_at_corpus_scope(conn):
    # 8.7's other worked case: "if the user repeatedly rejects an association between
    # their authoring school and application documents, the product can lower the role
    # or weight of author-affiliation evidence across that corpus."
    for index, file_id in enumerate(("app-1", "app-2", "app-3")):
        a_rejection(
            conn, scope="corpus", subject="corpus", file_id=file_id,
            field_key="authored_by", value_id="value-columbia",
            observed_at=f"2026-08-2{index}T09:00:00+00:00",
        )
    records = learning_records(conn, "corpus", "corpus")
    assert len(records) == 3
    assert {row["proposal_class"] for row in records} == {PROPOSAL_CLASS}
    assert {row["polarity"] for row in records} == {"reject"}
    # The three are distinguishable from one another by basis, so "repeatedly" is
    # countable by the consumer that weights. P6 weights nothing: 3.7's weights are
    # injected (Task 11) and this module publishes none.
    assert len({row["basis_key"] for row in records}) == 3
    # The corpus record is not a file-scoped one, and the file-scoped read is empty.
    assert learning_records(conn, "file", "app-1") == []


# --- what a correction record must carry ------------------------------------------


def test_a_correction_writes_all_five_of_p1s_correction_fields(conn):
    a_rejection(conn)
    row = conn.execute("SELECT * FROM events").fetchone()
    for column in CORRECTION_FIELDS:
        assert row[column] is not None and row[column] != ""
    assert row["proposal_class"] == PROPOSAL_CLASS
    assert row["polarity"] == "reject"
    assert row["correction_scope"] == "file"
    assert row["correction_subject"] == "file-1"
    assert row["basis_key"] == basis_key(
        file_id="file-1", field_key="subject", value_id="value-busib-4300"
    )


def test_the_polarity_chooses_p6s_own_event_type_and_no_other(conn):
    a_rejection(conn)
    a_rejection(conn, action="confirm_fact", polarity="accept", evidence_refs=())
    types = [row["event_type"] for row in conn.execute(
        "SELECT event_type FROM events ORDER BY event_id"
    )]
    assert types == ["fact rejection", "fact creation"]


def test_the_rejection_is_stored_with_the_evidence_that_produced_it(conn):
    a_rejection(conn, evidence_refs=(REF, OTHER_REF))
    row = conn.execute("SELECT explanation FROM events").fetchone()
    explanation = json.loads(row["explanation"])
    # 8.7: "Rejected groups, rejected destination matches, rejected labels, and
    # rejected residual recommendations must be stored with the evidence that
    # produced them."
    assert explanation["evidence_refs"] == [REF, OTHER_REF]
    assert explanation["proposal_class"] == PROPOSAL_CLASS
    assert explanation["action"] == "reject_fact"


def test_a_rejection_without_evidence_is_refused(conn):
    with pytest.raises(MalformedCorrection):
        a_rejection(conn, evidence_refs=())
    assert event_count(conn) == 0


def test_a_correction_with_no_user_is_refused(conn):
    # `learning_records` filters `user_id IS NOT NULL`. A correction stored without one
    # is storable and permanently unreadable -- a silently lost user gesture.
    with pytest.raises(MalformedCorrection):
        a_rejection(conn, user_id="")
    assert event_count(conn) == 0


def test_an_unknown_polarity_is_refused(conn):
    with pytest.raises(MalformedCorrection):
        a_rejection(conn, polarity="maybe")
    assert event_count(conn) == 0


def test_an_unnamed_action_is_refused(conn):
    with pytest.raises(MalformedCorrection):
        a_rejection(conn, action="")
    assert event_count(conn) == 0


def test_p6_does_not_branch_on_the_action_it_is_handed(conn):
    # P13 owns the action vocabulary. P6 stores the string and branches on polarity.
    a_rejection(conn, action="disable_suggestion_type")
    assert is_suppressed(
        conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is True


# --- the negatives 8.7 turns on ----------------------------------------------------


def test_the_correction_and_its_evidence_can_never_be_removed(conn):
    a_rejection(conn)
    # P1 enforces R6 by trigger, not by convention -- verified live: both raise
    # IntegrityError("events is append-only (R6, 8.2)").
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM events")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE events SET explanation = '{}'")
    assert event_count(conn) == 1


def test_suppression_is_versionless_and_survives_a_new_plan_version(conn):
    # I4: "a rejection in plan v2 has to stop the same proposal in v3. That is why
    # the store is a versionless projection over `events`".
    columns = {row[1] for row in conn.execute("PRAGMA table_info(events)")}
    assert "plan_version" not in columns
    assert "plan_id" not in columns
    parameters = inspect.signature(is_suppressed).parameters
    assert "plan_version" not in parameters
    assert set(parameters) == {
        "conn", "scope", "subject_id", "file_id", "field_key", "value_id"
    }
    assert "plan_version" not in inspect.signature(basis_key).parameters


def test_p6_performs_no_global_training_on_the_users_corpus(conn):
    # 8.7: "The product should not silently train a global model on a user's private
    # corpus." An accumulator at module scope is what that would look like, so there
    # is none -- checked by introspection, not by reading the source text.
    for name, value in vars(learning_module).items():
        if name.startswith("__"):
            continue
        assert not isinstance(value, (dict, list, set, bytearray)), name


def test_the_subsystem_is_named_in_exactly_one_module_and_it_is_not_this_one(conn):
    # M8: `subsystem = "P6"` is written once, in `facts.authorship`. This module gets
    # it from `event_defaults` and never spells it. Exact equality, not substring:
    # the module docstring may name P6; no module-level VALUE may be it.
    literals = {v for v in vars(learning_module).values() if isinstance(v, str)}
    assert "P6" not in literals
    a_rejection(conn)
    assert conn.execute("SELECT subsystem FROM events").fetchone()["subsystem"] == "P6"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_learning.py -v`

Expected: **FAIL** — collection error, `ModuleNotFoundError: No module named 'facts.learning'`. All
28 tests error at import.

- [ ] **Step 3: Write the implementation**

```python
# src/facts/learning.py
"""8.7 correction learning -- the query-before-propose guard (I4).

TWO HALVES, AND ONLY ONE OF THEM CAN FIRE TODAY.

READ (binding now).  8.7's failure mode is literal: without stored negative feedback
the system "will repeatedly resurface the same attractive but incorrect grouping."
I4 states P6's obligation as: before writing a `file_facts` row that would revive a
`rejected` claim, query the learning store; on an unreset reject, leave the `rejected`
row in place and do not propose the same (field, value) again.  `is_suppressed` is
that query.  It ships with the fact tables because a guard that arrives after the
first fact is written has already failed once.

WRITE (built, unreachable).  Corrections arrive through P13's `review_action`, and
P13 does not exist.  `record_correction` is the surface P13 will route a fact-level
gesture into; nothing in this plan calls it, and P6's tests drive it directly.  Owed
to P13's wave: the gesture surface, the inspect/reset UI, the routing decision, and
the call to `database_agent.learning.reset_preferences`.

P6 MINTS NO 8.2 EVENT TYPE HERE.  A user correction is keyed by `proposal_class` and
`basis_key` -- two ordinary columns beside 8.2's eleven -- never by a type of its own.
The two types used are P6's authored pair from `facts.authorship`, both already among
8.2's reserved nineteen, so nothing is registered.

P1 STORES, P6 INTERPRETS.  P1's own docstring is explicit that it "derives no polarity,
compares no basis_key, interprets no proposal_class".  Suppressing a proposal is the
acting part's rule, applied here.
"""
from __future__ import annotations

import sqlite3
from typing import Iterable

from database_agent.events import append_event
from database_agent.learning import learning_records
from evidence_shape.canonical import canonical_json
from facts.authorship import AUTHORED_EVENT_TYPES, event_defaults

#: I4's equivalence table. P6 owns proposal class `fact`; its basis is the claim.
#: `group`, `membership`, `branch`, `placement`, `residual` and `privacy` belong to
#: P9, P10, P11 and P7, and a record at one of those classes is not P6's to read.
PROPOSAL_CLASS: str = "fact"

#: I4: "polarity in accept | reject ... supplied by the acting part, never inferred".
#: Every rule below turns on finding an *unreset reject*; a reader that could not
#: separate rejections from approvals would have to parse explanation free text.
POLARITIES: tuple[str, str] = ("accept", "reject")
ACCEPT, REJECT = POLARITIES

#: P6's two 8.2 names, taken from Task 1's tuple rather than respelled here. Both are
#: reserved names, spelled with a space; `fact_creation` would raise at the writer.
CREATION, REJECTION = AUTHORED_EVENT_TYPES


class MalformedCorrection(Exception):
    """Refused at the writer. `events` is append-only, so a bad row cannot be repaired."""


def basis_key(*, file_id: str, field_key: str, value_id: str) -> str:
    """I4's `(file_id, field, value_id)`, serialized once -- here, and nowhere else.

    Canonical JSON rather than a delimiter join (not injective: a `|` inside a part
    would collide two claims and suppress a proposal the user never rejected) and
    rather than a digest (8.7 requires the user "be able to inspect or reset learned
    preferences", and an opaque basis is not inspectable).  `canonical_json` sorts
    keys, so the argument order at the call site cannot change the stored key.

    Member set, dossier hash and display label are NOT in the basis (I4).
    """
    return canonical_json(
        {"field_key": field_key, "file_id": file_id, "value_id": value_id}
    )


def is_suppressed(conn: sqlite3.Connection, *, scope: str, subject_id: str,
                  file_id: str, field_key: str, value_id: str) -> bool:
    """True when an unreset rejection of exactly this claim stands at this scope.

    I4's query-before-propose, applied in order: ignore records at the wrong
    `proposal_class`; ignore records whose `basis_key` does not match; honour a later
    reset; and on a `polarity = reject` record that no later reset covers, do not
    emit.  An `accept` at the same basis is not a suppression and is not read as one.

    The reset is honoured by `learning_records` itself -- it applies the cutoff and
    returns nothing below it.  This function does not re-derive it: a second place
    the cutoff rule lives is a second place it can drift.

    Read-only.  It appends no event, writes no fact, and mutates nothing.
    """
    key = basis_key(file_id=file_id, field_key=field_key, value_id=value_id)
    for row in learning_records(conn, scope, subject_id):
        if row["proposal_class"] != PROPOSAL_CLASS:
            continue
        if row["basis_key"] != key:
            continue
        if row["polarity"] == REJECT:
            return True
    return False


def record_correction(conn: sqlite3.Connection, *, action: str, scope: str, subject: str,
                      polarity: str, file_id: str, field_key: str, value_id: str,
                      evidence_refs: Iterable[str], user_id: str,
                      observed_at: str) -> int:
    """Author the fact-level consequence of one user correction; P1 writes it (M8).

    P13's stand-in until P13 exists.  `action` is P13's gesture name: P6 stores the
    string in the explanation and branches on `polarity`, never on `action` -- the
    action vocabulary is P13's and P6 does not coin a name another part owns.

    `subject` is not derived from `file_id`.  Five of 8.7's six scopes have no file,
    so the correction's subject is always the caller's to supply.

    `scope` is validated by P1's writer against `CORRECTION_SCOPES`, which is the one
    place the six are spelled.  P6 keeps no copy.
    """
    if polarity not in POLARITIES:
        raise MalformedCorrection(
            f"polarity {polarity!r} is not one of {POLARITIES}; I4 requires it be "
            "supplied by the acting part and never inferred"
        )
    if not action:
        raise MalformedCorrection("action is required; it is P13's gesture name")
    if not user_id:
        raise MalformedCorrection(
            "user_id is required: learning_records filters `user_id IS NOT NULL`, so a "
            "correction stored without one is storable and permanently unreadable"
        )
    refs = tuple(evidence_refs)
    if polarity == REJECT and not refs:
        raise MalformedCorrection(
            "8.7 requires a rejection be stored with the evidence that produced it"
        )
    key = basis_key(file_id=file_id, field_key=field_key, value_id=value_id)
    explanation = canonical_json({
        "action": action,
        "basis_key": key,
        "evidence_refs": list(refs),
        "polarity": polarity,
        "proposal_class": PROPOSAL_CLASS,
    })
    payload = event_defaults(
        event_type=REJECTION if polarity == REJECT else CREATION,
        observed_at=observed_at,
        explanation=explanation,
        file_id=file_id,
        user_id=user_id,
        correction_scope=scope,
        correction_subject=subject,
        polarity=polarity,
        proposal_class=PROPOSAL_CLASS,
        basis_key=key,
    )
    return append_event(conn, **payload)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_learning.py -v`

Expected: **PASS** — 28 passed.

- [ ] **Step 5: Confirm the guard is reachable and the write half is not**

Run:

```bash
cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -c "
import inspect, facts.learning as L
print('read half :', [n for n in ('PROPOSAL_CLASS','basis_key','is_suppressed') if hasattr(L,n)])
print('write half:', 'record_correction' in vars(L))
print('module holds no accumulator:', not any(
    isinstance(v, (dict, list, set)) for n, v in vars(L).items() if not n.startswith('__')))
"
```

Expected: `read half : ['PROPOSAL_CLASS', 'basis_key', 'is_suppressed']`,
`write half: True`, `module holds no accumulator: True`.

Then confirm nothing in `src/facts/` calls the write half — it is P13's to call:

```bash
cd "/Users/jy/GRAPH AGENT" && grep -rn "record_correction" src/ | grep -v "src/facts/learning.py"
```

Expected: **no output.** A hit means some module invented a correction P13 has not routed.

- [ ] **Step 6: Commit**

```bash
git add src/facts/learning.py tests/p6/test_p6_learning.py
git commit -m "feat(P6): 8.7 query-before-propose over P1's learning records (I4)"
```

---

---

### Task 23: §8.8 plan versioning — what belongs to a plan version and what does not

**Files:**
- Create: `src/facts/plan_versions.py`
- Test: `tests/p6/test_p6_plan_versions.py`

**Interfaces:**
- Consumes: `facts.values` — `ensure_value`, `VALUE_ORIGINS`, and the `values` table;
  `facts.file_facts` — `FILE_FACTS_COLUMNS`, `FACT_ORIGINS`, `write_fact`;
  `facts.fields` — `create_fields`; `facts.cache` — `fact_cache_key`;
  `database_agent.supersede.SUPERSEDE_COLUMNS`.
- Produces: `PLAN_VERSIONED: tuple[str, ...]` (`display_label`, `aliases`),
  `SHARED_ACROSS_PLAN_VERSIONS: tuple[str, ...]`,
  `VALUE_RENDERINGS_COLUMNS: tuple[str, ...]`, `create_plan_version_tables(conn) -> None`,
  `display_label(conn, *, value_id, plan_version) -> str`,
  `set_display_label(conn, *, value_id, plan_version, label) -> None`.

**Done-means:** none numbered; §8.8's obligations.

---

**The whole task is one sentence of the design, and its two halves point opposite ways.** §8.8,
verbatim: *"A new plan should never silently reclassify or move old files. It creates a new set of
placement recommendations subject to review. The evidence database remains shared across plan
versions, but the destination tree and user policy define which projections are valid in each
version."*

- **The negative.** Nothing P6 stores as a *record* is plan-versioned. A new plan version
  re-resolves nothing, invalidates nothing and reclassifies nothing. This is the half that matters,
  and it is enforced by absence: none of P6's four record tables has a plan-version column, so
  there is no place a version could be written even by a later mistake.
- **The positive.** §8.8's list of what a plan version captures includes *"User labels and
  aliases"*. So the **rendering** of a value is the plan's: `UChicago` and `University of Chicago`
  are two labels for one value, and choosing between them is a plan-version decision that must
  leave the value and every fact pointing at it untouched.

**Why the rendering gets its own table, and why that is not a fifth record table.** Task 3 puts
`display_label` on the `values` row. If `set_display_label` wrote there, then changing a label in
plan v3 would rewrite a row that v2 shares — which is precisely the silent cross-version mutation
§8.8 forbids. The rendering therefore lives in a **plan-version-keyed side table**,
`value_renderings`, and the `values` row keeps the version-independent default Task 3 gives it. The
result is that the shared/versioned split is checkable from `PRAGMA table_info` alone, the same
reviewer-checkable-negative-contract principle Task 4 uses for paths and destinations.

> **Contradiction found, and flagged rather than papered over.** The skeleton's architecture
> paragraph says P6 *"owns **four** tables"*. This task adds a fifth, and Task 19 already adds one
> too (its recorded deterministic pass — its Files block reads *"modify `src/facts/schema.py`"*).
> The line should read **four record tables**: `fields`, `values`, `file_facts`, `unresolved` are
> the records, and `value_renderings` and Task 19's pass record are auxiliary. If a reviewer wants
> the count kept literally at four, the only alternative is putting per-version labels on the
> `values` row, and that alternative breaks §8.8. Flagging, not deciding.

> **Second, smaller contradiction.** Task 23's Files block lists no `modify src/facts/schema.py`,
> while Tasks 2–5 and 19 all list it. So this task declares its own DDL in `plan_versions.py` and
> publishes `create_plan_version_tables`, rather than editing a file its Files block does not name.
> **One line is then owed to whoever assembles `schema.py`:** its aggregate creator must call
> `create_plan_version_tables`, or the table exists only where a test creates it.

**`aliases` is named in `PLAN_VERSIONED` and has no writer, on purpose.** §8.8 versions *"labels and
aliases"*, so the boundary declaration names both. But the skeleton publishes accessors for the
label only, and Task 3 already uses `values.aliases` for something different — §0's taxonomy
aliases, which a merge records and which are **identity**, not rendering (Task 3: *"a merge records
an alias and deletes nothing"*). Inventing a `set_aliases` here would either duplicate that column
or build a surface no Done-means asks for. So `PLAN_VERSIONED` **declares** the boundary and
`value_renderings` carries only the column that has a writer — D3's rule against a writer-less
column, applied. The per-version alias override is **owed, not stubbed**; a named test in Task 25
should hold it open.

**P6 mints no §8.2 event type for a rendering change, and appends none.** §8.8's diff — *"Applications
was renamed to Admissions"* — belongs to the plan-version object, and that object is P10's and
P12's. `destination-tree edit` is already a reserved name and is not P6's to write. A test asserts
the event count is unchanged across a rendering change.

**Two cross-task assumptions this task makes explicit.** First, `facts.schema.create_facts_schema` —
the name follows P4's `evidence_shape.schema.create_evidence_schema` exactly, but it appears in no
`Interfaces:` block, so if Wave A names its creator otherwise, this one import changes. Second,
`write_fact` is called with exactly the ten keywords its Task 4 contract publishes, and with no P1
`files` row present (P1 puts no foreign key on `events.file_id` — verified). If Task 4 lands an
eleventh required keyword or a files-row precondition, it breaks this test *and* Task 20's resolver,
which is the right place for that to surface.

- [ ] **Step 1: Write the failing test**

```python
# tests/p6/test_p6_plan_versions.py
"""8.8: the evidence database is shared across plan versions; the rendering is not.

The negative half is the one that matters and it is enforced by absence -- no P6
record table has a plan-version column, so there is nowhere a version could be
written. The positive half is one side table holding the label a plan version chose.
"""
from __future__ import annotations

import pytest

from database_agent import db
from database_agent.supersede import SUPERSEDE_COLUMNS
from evidence_shape.observation import observation_key
from facts.cache import fact_cache_key
from facts.fields import create_fields
from facts.file_facts import FACT_ORIGINS, FILE_FACTS_COLUMNS, write_fact, DETERMINISTIC_EXTRACTOR
from facts.plan_versions import (
    PLAN_VERSIONED,
    SHARED_ACROSS_PLAN_VERSIONS,
    VALUE_RENDERINGS_COLUMNS,
    create_plan_version_tables,
    display_label,
    set_display_label,
)
from facts.schema import create_facts_schema
from facts.values import ensure_value

CONTENT_HASH = "sha256:" + "a" * 64
FORBIDDEN = ("path", "destination", "folder", "node", "group")
RECORD_TABLES = ("fields", "values", "file_facts", "unresolved")

REF = observation_key(
    content_hash=CONTENT_HASH,
    extractor_name="pdf.text",
    locator="heading:page=1/heading=2",
    raw_value="University of Chicago",
)
CACHE_KEY = fact_cache_key(
    content_hash=CONTENT_HASH,
    extractor_version="1.0.0",
    analysis_tier="native",
    model_identifier=None,
    prompt_fingerprint=None,
)


@pytest.fixture()
def conn(tmp_path):
    connection = db.open_database(tmp_path / "p6-plan-versions.db")
    db.create_schema(connection)
    create_facts_schema(connection)
    create_fields(connection)
    create_plan_version_tables(connection)
    yield connection
    connection.close()


@pytest.fixture()
def value_id(conn) -> str:
    # 3.8's target_school, which D1 ratifies into the catalogue. 2.8's three
    # renderings of one institution are the design's own worked example.
    return ensure_value(
        conn,
        field_key="target_school",
        canonical_value="University of Chicago",
        first_evidence_ref=REF,
        origin="automatic",
    )


@pytest.fixture()
def fact_id(conn, value_id) -> str:
    return write_fact(
        conn,
        file_id="file-1",
        content_hash=CONTENT_HASH,
        field_key="target_school",
        value_id=value_id,
        reliability_state="direct",
        origin=DETERMINISTIC_EXTRACTOR,
        evidence_refs=(REF,),
        cache_key=CACHE_KEY,
        active=True,
    )


def snapshot(connection) -> dict[str, list[str]]:
    """Every table's every row, byte-for-byte.

    Rows are compared as sorted reprs: SQLite guarantees no row order without an
    ORDER BY, `ORDER BY rowid` is not available on every table, and sorting the
    tuples themselves would compare None against str. Sorted reprs are total,
    deterministic, and still catch a single changed byte in any column.
    """
    names = [
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        )
    ]
    return {
        name: sorted(
            repr(tuple(row)) for row in connection.execute(f'SELECT * FROM "{name}"')
        )
        for name in names
    }


# --- the declaration -------------------------------------------------------------


def test_the_two_tuples_name_the_8_8_split_and_do_not_overlap():
    assert PLAN_VERSIONED == ("display_label", "aliases")
    assert set(PLAN_VERSIONED).isdisjoint(SHARED_ACROSS_PLAN_VERSIONS)
    for name in RECORD_TABLES:
        assert name in SHARED_ACROSS_PLAN_VERSIONS
    for name in ("evidence_refs", "reliability_state", "supersession_history"):
        assert name in SHARED_ACROSS_PLAN_VERSIONS


def test_what_is_declared_shared_is_actually_a_shared_record(conn):
    # 8.8: "The evidence database remains shared across plan versions."
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    for name in RECORD_TABLES:
        assert name in tables
    assert "evidence_refs" in FILE_FACTS_COLUMNS
    assert "reliability_state" in FILE_FACTS_COLUMNS
    for column in SUPERSEDE_COLUMNS:
        assert column in FILE_FACTS_COLUMNS


def test_no_record_table_carries_a_plan_version_column(conn):
    # Enforced by absence: there is nowhere a version could be written.
    for name in RECORD_TABLES:
        columns = {row[1] for row in conn.execute(f'PRAGMA table_info("{name}")')}
        assert "plan_version" not in columns, name
        assert "plan_id" not in columns, name


def test_no_plan_versioned_attribute_is_a_fact_column():
    # A fact is a claim, not a rendering. If `display_label` ever became a
    # `file_facts` column, a label change would rewrite facts.
    assert set(FILE_FACTS_COLUMNS).isdisjoint(PLAN_VERSIONED)


def test_the_renderings_table_is_keyed_by_version_and_carries_no_destination(conn):
    assert VALUE_RENDERINGS_COLUMNS == ("value_id", "plan_version", "display_label")
    columns = [row[1] for row in conn.execute("PRAGMA table_info(value_renderings)")]
    assert tuple(columns) == VALUE_RENDERINGS_COLUMNS
    # 3.14's negative contract, applied to this table too.
    for column in columns:
        for forbidden in FORBIDDEN:
            assert forbidden not in column, column


# --- the rendering ---------------------------------------------------------------


def test_two_plan_versions_render_one_value_two_ways(conn, value_id):
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    set_display_label(
        conn, value_id=value_id, plan_version="v3", label="University of Chicago"
    )
    assert display_label(conn, value_id=value_id, plan_version="v2") == "UChicago"
    assert (
        display_label(conn, value_id=value_id, plan_version="v3")
        == "University of Chicago"
    )


def test_a_version_that_chose_nothing_falls_back_and_never_borrows(conn, value_id):
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    # v3 chose nothing, so it renders the value's own label -- NOT v2's choice. A
    # rendering is scoped to the version that made it.
    assert display_label(conn, value_id=value_id, plan_version="v3") != "UChicago"


def test_the_fallback_chain_ends_at_the_canonical_string(conn, value_id):
    # Total by construction: 5.5's preview needs something to show for every value,
    # and a renderer that can return None shows nothing on a version that chose none.
    rendered = display_label(conn, value_id=value_id, plan_version="v9")
    assert isinstance(rendered, str) and rendered != ""


def test_re_rendering_the_same_version_replaces_rather_than_duplicates(conn, value_id):
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    set_display_label(conn, value_id=value_id, plan_version="v2", label="U Chicago")
    rows = conn.execute("SELECT COUNT(*) AS n FROM value_renderings").fetchone()["n"]
    assert rows == 1
    assert display_label(conn, value_id=value_id, plan_version="v2") == "U Chicago"


def test_a_rendering_for_a_value_that_does_not_exist_is_refused(conn):
    with pytest.raises(ValueError):
        set_display_label(
            conn, value_id="no-such-value", plan_version="v2", label="Ghost"
        )
    rows = conn.execute("SELECT COUNT(*) AS n FROM value_renderings").fetchone()["n"]
    assert rows == 0


def test_a_rendering_without_a_plan_version_is_refused(conn, value_id):
    with pytest.raises(ValueError):
        set_display_label(conn, value_id=value_id, plan_version="", label="UChicago")


# --- the guarantee -----------------------------------------------------------------


def test_a_new_plan_version_changes_no_shared_record_byte_for_byte(conn, value_id, fact_id):
    before = snapshot(conn)
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    set_display_label(
        conn, value_id=value_id, plan_version="v3", label="University of Chicago"
    )
    after = snapshot(conn)
    assert set(before) == set(after)
    for name in after:
        if name == "value_renderings":
            continue
        assert after[name] == before[name], name
    # And the versioned table is the only thing that moved.
    assert len(after["value_renderings"]) == 2
    assert before["value_renderings"] == []


def test_the_value_itself_is_untouched_by_a_rendering_change(conn, value_id):
    before = conn.execute(
        'SELECT * FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    after = conn.execute(
        'SELECT * FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    assert tuple(after) == tuple(before)


def test_every_fact_pointing_at_the_value_still_resolves_unchanged(conn, value_id, fact_id):
    before = [
        tuple(row)
        for row in conn.execute("SELECT * FROM file_facts WHERE value_id = ?", (value_id,))
    ]
    assert len(before) == 1
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    after = [
        tuple(row)
        for row in conn.execute("SELECT * FROM file_facts WHERE value_id = ?", (value_id,))
    ]
    assert after == before


def test_a_rendering_change_re_resolves_nothing_and_invalidates_no_cache_key(
    conn, value_id, fact_id
):
    # 3.4's cache key has five parts and a plan version is none of them, so a plan
    # edit cannot invalidate a fact. 8.8: "A new plan should never silently
    # reclassify or move old files."
    before = conn.execute(
        "SELECT cache_key FROM file_facts WHERE fact_id = ?", (fact_id,)
    ).fetchone()["cache_key"]
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    after = conn.execute(
        "SELECT cache_key FROM file_facts WHERE fact_id = ?", (fact_id,)
    ).fetchone()["cache_key"]
    assert after == before == CACHE_KEY


def test_p6_appends_no_event_for_a_rendering_change(conn, value_id, fact_id):
    # 8.8's diff belongs to the plan-version object, which is P10's and P12's. P6
    # mints no 8.2 type here and writes none of anyone else's.
    before = conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    after = conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]
    assert after == before
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p6/test_p6_plan_versions.py -v`

Expected: **FAIL** — collection error, `ModuleNotFoundError: No module named 'facts.plan_versions'`.
All 16 tests error at import.

- [ ] **Step 3: Write the implementation**

```python
# src/facts/plan_versions.py
"""8.8 -- what belongs to a plan version, and what does not.

8.8's guarantee is one sentence: "A new plan should never silently reclassify or move
old files. It creates a new set of placement recommendations subject to review. The
evidence database remains shared across plan versions, but the destination tree and
user policy define which projections are valid in each version."

THE NEGATIVE, which is the half that matters.  Nothing P6 stores as a record is
plan-versioned: `fields`, value identity, `file_facts`, `unresolved`, every evidence
ref, every reliability state and all supersession history are shared.  Enforced by
ABSENCE -- no record table carries a plan-version column, so there is nowhere a
version could be written even by a later mistake.  A new plan version therefore
re-resolves nothing, invalidates nothing and reclassifies nothing; 3.4's cache key has
five parts and a plan version is none of them.

THE POSITIVE.  8.8's plan version captures "User labels and aliases", so the RENDERING
of a value is the plan's.  `UChicago` and `University of Chicago` are two labels for
one value, and choosing between them must leave the value and every fact pointing at
it untouched.  That is why the rendering lives here, in a plan-version-keyed side
table, and not on the `values` row: writing it there would rewrite a row every other
plan version shares, which is the silent cross-version mutation 8.8 forbids.

`aliases` is declared in PLAN_VERSIONED and has no writer here on purpose.  8.8
versions "labels and aliases", so the boundary names both; but `values.aliases` is
already 0's taxonomy aliases, which are identity rather than rendering, and no
Done-means asks for a per-version alias override.  Declaring the boundary is this
module's job; building a column with no writer is not (D3).

P6 MINTS NO 8.2 EVENT TYPE HERE and appends none.  8.8's plan diff ("Applications was
renamed to Admissions") belongs to the plan-version object, and that object is P10's
and P12's.  `destination-tree edit` is a reserved name and is not P6's to write.
"""
from __future__ import annotations

import sqlite3

#: 8.8: "User labels and aliases" are captured BY a plan version. A declaration of the
#: boundary, not a column list -- only `display_label` has a writer today.
PLAN_VERSIONED: tuple[str, ...] = ("display_label", "aliases")

#: Everything a plan version must NOT be able to change. The four record tables, plus
#: the three fact properties 8.8's guarantee turns on.
SHARED_ACROSS_PLAN_VERSIONS: tuple[str, ...] = (
    "fields",
    "values",
    "file_facts",
    "unresolved",
    "evidence_refs",
    "reliability_state",
    "supersession_history",
)

#: The one plan-version-keyed table P6 owns. Not a fifth RECORD table: it holds no
#: claim, no evidence and no reliability state, and nothing reads it to decide a fact.
VALUE_RENDERINGS_COLUMNS: tuple[str, ...] = ("value_id", "plan_version", "display_label")

_DDL = """
CREATE TABLE IF NOT EXISTS value_renderings (
    value_id      TEXT NOT NULL,
    plan_version  TEXT NOT NULL,
    display_label TEXT NOT NULL,
    PRIMARY KEY (value_id, plan_version)
)
"""


def create_plan_version_tables(conn: sqlite3.Connection) -> None:
    """Create the rendering table inside P1's database. Creates no other part's.

    Owed: `facts.schema`'s aggregate creator must call this, or the table exists only
    where a test creates it.
    """
    conn.execute(_DDL)


def _value_row(conn: sqlite3.Connection, value_id: str) -> sqlite3.Row:
    # `values` is a SQLite keyword; the identifier must be quoted or the statement is
    # a syntax error rather than a missing table.
    row = conn.execute(
        'SELECT canonical_value, display_label FROM "values" WHERE value_id = ?',
        (value_id,),
    ).fetchone()
    if row is None:
        raise ValueError(
            f"no value {value_id!r}: a rendering with no value to render would be a "
            "label the user can never trace back to a fact"
        )
    return row


def set_display_label(conn: sqlite3.Connection, *, value_id: str, plan_version: str,
                      label: str) -> None:
    """Record the label THIS plan version shows for one value. Touches no record.

    Writes only `value_renderings`: no fact, no value, no field, no event. A repeat
    for the same version replaces that version's choice rather than accumulating a
    second one -- a value renders one way per version or the display is ambiguous.
    """
    if not plan_version:
        raise ValueError("plan_version is required: a rendering belongs to a version")
    if not label:
        raise ValueError(
            "label is required: an empty rendering is not a choice, and clearing one "
            "is a different operation than making one"
        )
    _value_row(conn, value_id)
    conn.execute(
        "INSERT INTO value_renderings (value_id, plan_version, display_label) "
        "VALUES (?, ?, ?) "
        "ON CONFLICT (value_id, plan_version) DO UPDATE SET "
        "display_label = excluded.display_label",
        (value_id, plan_version, label),
    )


def display_label(conn: sqlite3.Connection, *, value_id: str,
                  plan_version: str) -> str:
    """This version's rendering, else the value's own label, else its canonical string.

    Total by construction: 5.5 previews "three schools, five terms, and twelve course
    branches" before the user commits, and a renderer that can return None shows
    nothing for a value whose version made no choice.

    The chain never borrows another version's label. A rendering is scoped to the
    version that chose it, exactly as 8.8 scopes everything else a plan captures.
    """
    chosen = conn.execute(
        "SELECT display_label FROM value_renderings "
        "WHERE value_id = ? AND plan_version = ?",
        (value_id, plan_version),
    ).fetchone()
    if chosen is not None:
        return chosen["display_label"]
    value = _value_row(conn, value_id)
    return value["display_label"] or value["canonical_value"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/p6/test_p6_plan_versions.py -v`

Expected: **PASS** — 16 passed.

- [ ] **Step 5: Confirm the negative from the schema alone**

A reviewer must be able to check §8.8's guarantee without reading a test:

```bash
cd "/Users/jy/GRAPH AGENT" && PYTHONPATH=src python3 -c "
import tempfile; from pathlib import Path
from database_agent import db
from facts.schema import create_facts_schema
from facts.plan_versions import create_plan_version_tables, PLAN_VERSIONED
c = db.open_database(Path(tempfile.mkdtemp())/'x.db'); db.create_schema(c)
create_facts_schema(c); create_plan_version_tables(c)
for t in ('fields','values','file_facts','unresolved'):
    cols = [r[1] for r in c.execute(f'PRAGMA table_info(\"{t}\")')]
    print(t, 'plan_version' in cols, sorted(set(cols) & set(PLAN_VERSIONED)))
"
```

Expected: `False []` for `fields`, `file_facts` and `unresolved`; `values` prints
`False ['aliases', 'display_label']` — the version-independent defaults Task 3 owns, which is the
one place the two tuples touch and the reason `value_renderings` exists.

- [ ] **Step 6: Commit**

```bash
git add src/facts/plan_versions.py tests/p6/test_p6_plan_versions.py
git commit -m "feat(P6): 8.8 plan versioning -- shared records, versioned renderings"
```

---

### Task 24: The read surface published to neighbours

**Files:**
- Create: `src/facts/read_surface.py`
- Test: `tests/p6/test_p6_read_surface.py`

**Interfaces:**
- Consumes: `facts.fields` — `FIELD_SCOPES`, `fields_in_scope`, `get_field`, `FieldNotInCatalogue`;
  `facts.file_facts` — `facts_for_file`, `FORBIDDEN_COLUMN_SUBSTRINGS`; `facts.unresolved` —
  `unresolved_for_file`; `facts.values` — `values_in_field`; `facts.states` — `STATES`,
  `STRENGTH_ORDER`; `facts.supersede` — `fact_history`; `facts.domains` —
  `active_field_allowlist`; `facts.families` — `DUPLICATE_FAMILY_FIELD`, `VERSION_FAMILY_FIELD`;
  `facts.session` — `DOWNLOAD_SESSION_FIELD`; `facts.photo_event` — `EVENT_FIELD`;
  `evidence_shape.store.observations_by_key`; `evidence_shape.observation.Observation`;
  `evidence_shape.vocabulary` — `check`, `NotInVocabulary`.
- Produces (`read_surface.py`):
  `facts_for(conn, *, file_id, content_hash, states=None, domain=None) -> list[sqlite3.Row]`,
  `proposal_eligible(conn, *, file_id, content_hash) -> list[sqlite3.Row]`,
  `active_allowlist_for(conn, *, file_id, content_hash, activation_signals) -> tuple[str, ...]`,
  `values_with_counts(conn, *, field_key) -> list[tuple[str, int]]`,
  `evidence_chain(conn, *, fact_id) -> list[Observation]`,
  `history(conn, *, file_id, field_key) -> list[sqlite3.Row]`,
  `unresolved_for(conn, *, file_id, content_hash, field_key=None, reason=None) -> list[sqlite3.Row]`,
  `event_facts(conn, *, file_id, content_hash) -> list[sqlite3.Row]`,
  `session_facts(conn, *, file_id, content_hash) -> list[sqlite3.Row]`,
  `family_facts(conn, *, file_id, content_hash) -> list[sqlite3.Row]`,
  `is_destination_eligible(conn, *, field_key) -> bool`.

**Two additions to the skeleton's `Produces:` line, made here and named so no other author
collides with them.** The skeleton writes four of these signatures with `...` for their keywords;
those are fixed above and nothing is renamed. Beyond that:

- **`PROPOSAL_ELIGIBLE_STATES: tuple[str, ...]`** — §3.6's two exclusions, **derived** from Task 1's
  `STRENGTH_ORDER` rather than spelled. Task 1 requires that no state name appears as a string
  literal anywhere else in `facts`, and `proposal_eligible` is precisely the function that would be
  tempted to spell two. `rejected` is the one member of `STATES` that Task 1 gives no strength, so it
  is absent from `STRENGTH_ORDER` by construction; `possible` is `STRENGTH_ORDER[-1]`, the weakest
  ranked state. `STRENGTH_ORDER[:-1]` is therefore both exclusions at once, with neither named.
- **`DanglingCitation(LookupError)`** — raised when `evidence_chain` meets an `observation_key` that
  resolves to nothing. §3.1 is unconditional — *"Every fact preserves where it came from"* — so a
  citation that resolves to no observation is a broken fact, not an empty result, and returning a
  shorter list would let Done-means 30 pass by counting zero.

**Done-means:** 12, 13, and the read half of 19.

---

**What this module is, stated once, because it decides every line below.** It is the only shape P9,
P10, P11, P13, P2 and the review UI ever see. Three properties follow, and each is a test:

1. **It is a pure read.** No function here writes a row, appends an event or resolves a fact. A read
   surface that could change what it reports is not one.
2. **It returns no filing decision.** §3.14: *"A fact such as subject = BUSIB 4300 does not itself
   dictate one permanent folder path."* Task 4 asserts that from the schema with
   `FORBIDDEN_COLUMN_SUBSTRINGS`; this task asserts the same list against the **keys of every row
   this module hands out**, so a future column named `destination_node_id` fails twice.
3. **It imposes its own total order.** P4's reads are `ORDER BY rowid`, which is insertion order and
   a property of one database rather than of the corpus (skeleton, Global Constraints). Every read
   here sorts before it returns, so the same corpus extracted in a different order produces the same
   read.

**The one carve-out, named rather than left to be discovered.** `evidence_chain` returns P4
`Observation` objects verbatim, and `Observation.location.container_path` contains the word *path*.
That is not a violation and must not be "fixed": §3.2's whole point is that P6 *"preserve both the
original evidence and the conclusion built from it"*, and a container path is a locator **inside a
document** — `heading:page=1/heading=2` — not a filesystem destination. The forbidden-key assertion
therefore runs over the `sqlite3.Row` reads, which are P6's own rows, and `evidence_chain` is
asserted separately: it returns P4's frozen shape unaltered, which is the stronger claim.

**Where `read_surface` queries P6's tables directly, and why that is not a layering break.**
`evidence_chain` is addressed by `fact_id` alone — a reviewer clicking a citation has the fact id and
nothing else — and no module publishes a by-`fact_id` read. `values_with_counts` needs one aggregate
across the whole corpus. Both are `SELECT`s over `file_facts`, which is P6's own table. Everything
else composes the published functions and adds no second answer.

- [ ] **Step 1: Create `tests/p6/test_p6_read_surface.py` with the complete failing test**

```python
# tests/p6/test_p6_read_surface.py
"""Task 24 — the read surface published to neighbours.

Done-means 12 (a `possible` fact is absent from the proposal-eligible read), 13 (an
`authored_by` value is never returned as destination-eligible) and the read half of 19
(an `unresolved` row is absent from every read).
"""
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import NotInVocabulary

from facts.cache import fact_cache_key
from facts.families import DUPLICATE_FAMILY_FIELD
from facts.fields import FieldNotInCatalogue
from facts.file_facts import (
    DETERMINISTIC_EXTRACTOR, FACT_ORIGINS, FORBIDDEN_COLUMN_SUBSTRINGS, RULE,
    write_fact,
)
from facts.photo_event import EVENT_FIELD
from facts.read_surface import (
    DanglingCitation, PROPOSAL_ELIGIBLE_STATES, active_allowlist_for, evidence_chain,
    event_facts, facts_for, family_facts, history, is_destination_eligible,
    proposal_eligible, session_facts, unresolved_for, values_with_counts,
)
from facts.session import DOWNLOAD_SESSION_FIELD
from facts.states import (
    DIRECT, LLM_SUPPORTED, POSSIBLE, REJECTED, STATES, STRENGTH_ORDER,
    USER_CONFIRMED, VALIDATED,
)
from facts.supersede import supersede_fact
from facts.unresolved import ATTEMPTED_PRODUCERS, UNRESOLVED_REASONS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

CLOCK = "2026-08-19T12:00:00+00:00"

#: Task 1 owns every state name; Task 4 owns every origin name. Imported, never
#: indexed, never unpacked from a ladder whose order is the opposite of this comment.

DETERMINISTIC = DETERMINISTIC_EXTRACTOR


def _record(conn, tmp_path, *, name, body, parent="Downloads"):
    """One P1 `files` row over real bytes, so the content hash is P1's own."""
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context=parent, mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, label,
             extractor="pdf.text", zone="metadata", source_type="text_document"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version="1.0.0",
        source_type=source_type, analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version="1.0.0", source_type=source_type, raw_value=raw,
        location=Location(zone, (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


def _key(content_hash):
    """§3.4's five parts. Deterministic facts carry no model and no prompt."""
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=json.dumps([["pdf.text", "1.0.0"]], separators=(",", ":")),
        analysis_tier="native", model_identifier=None, prompt_fingerprint=None)


def _fact(conn, *, file_id, content_hash, field_key, value, ref, state, origin=None):
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=ref, origin=VALUE_ORIGINS[0])
    return write_fact(
        conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
        value_id=value_id, reliability_state=state,
        origin=DETERMINISTIC if origin is None else origin,
        evidence_refs=(ref,), cache_key=_key(content_hash), active=True)


@pytest.fixture()
def syllabus(p6_conn, tmp_path):
    """One file carrying §3.2's worked case, plus the four rows the negatives need:
    a `possible` fact, a `rejected` fact, an `authored_by` fact and an `unresolved` row."""
    file_id, content_hash = _record(
        p6_conn, tmp_path, name="Syllabus BUSIB 4300 Spring 2026.pdf",
        body=b"BUSIB 4300 Syllabus, Spring 2026")
    subject_ref = _observe(p6_conn, run_id="r-1", file_id=file_id,
                           content_hash=content_hash, raw="BUSIB 4300", label="title")
    author_ref = _observe(p6_conn, run_id="r-2", file_id=file_id,
                          content_hash=content_hash, raw="Jane Chen", label="Author")
    weak_ref = _observe(p6_conn, run_id="r-3", file_id=file_id,
                        content_hash=content_hash, raw="Downloads", label="parent")
    dead_ref = _observe(p6_conn, run_id="r-4", file_id=file_id,
                        content_hash=content_hash, raw="Spring 2026", label="heading")
    subject_id = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                       field_key="subject", value="BUSIB 4300", ref=subject_ref,
                       state=VALIDATED, origin=RULE)
    author_id = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                      field_key="authored_by", value="Jane Chen", ref=author_ref,
                      state=DIRECT)
    session_id = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                       field_key=DOWNLOAD_SESSION_FIELD, value="2026-07-17T09:00Z",
                       ref=weak_ref, state=POSSIBLE)
    rejected_id = _fact(p6_conn, file_id=file_id, content_hash=content_hash,
                        field_key=EVENT_FIELD, value="Graduation", ref=dead_ref,
                        state=REJECTED)
    write_unresolved(
        p6_conn, file_id=file_id, content_hash=content_hash, field_key="work_type",
        reason=UNRESOLVED_REASONS[0], attempted_producers=(ATTEMPTED_PRODUCERS[0],),
        evidence_refs=(dead_ref,), cache_key=_key(content_hash))
    return {"file_id": file_id, "content_hash": content_hash,
            "subject_ref": subject_ref, "author_ref": author_ref,
            "subject_id": subject_id, "author_id": author_id,
            "session_id": session_id, "rejected_id": rejected_id}


# ---------------------------------------------------------------- Done-means 12 and 19

def test_the_proposal_eligible_read_excludes_possible_and_rejected(syllabus, p6_conn):
    """§3.6: a weak output "may remain a possible clue for review; it must not quietly
    become a folder proposal or an asserted file property". Both negatives at once —
    they are the two §3.6 turns on."""
    rows = proposal_eligible(p6_conn, file_id=syllabus["file_id"],
                             content_hash=syllabus["content_hash"])
    states = {row["reliability_state"] for row in rows}
    assert POSSIBLE not in states
    assert REJECTED not in states
    assert {row["field_key"] for row in rows} == {"subject", "authored_by"}


def test_proposal_eligible_states_are_derived_and_never_spelled(syllabus):
    """The exclusions come from Task 1's published order, so P6 has one spelling of a
    state name and `read_surface` is not a second."""
    assert PROPOSAL_ELIGIBLE_STATES == STRENGTH_ORDER[:-1]
    assert POSSIBLE not in PROPOSAL_ELIGIBLE_STATES
    assert REJECTED not in PROPOSAL_ELIGIBLE_STATES
    assert set(PROPOSAL_ELIGIBLE_STATES) < set(STATES)


def test_an_unresolved_row_is_absent_from_every_fact_read(syllabus, p6_conn):
    """Done-means 19's read half. `unresolved` is not a weak fact: it appears in no fact
    read at all, including the proposal-eligible one, and `work_type` — the field it
    names — comes back from none of them."""
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    reads = (facts_for(p6_conn, **args),
             facts_for(p6_conn, states=STATES, **args),
             proposal_eligible(p6_conn, **args),
             event_facts(p6_conn, **args),
             session_facts(p6_conn, **args),
             family_facts(p6_conn, **args))
    for rows in reads:
        assert "work_type" not in {row["field_key"] for row in rows}
    assert [row["field_key"] for row in unresolved_for(p6_conn, **args)] == ["work_type"]


def test_the_unresolved_read_carries_no_value_and_no_state(syllabus, p6_conn):
    """It is an abstention, not a `possible`. A reader that could read a state off it
    would eventually treat it as one."""
    row = unresolved_for(p6_conn, file_id=syllabus["file_id"],
                         content_hash=syllabus["content_hash"])[0]
    assert "value_id" not in row.keys()
    assert "reliability_state" not in row.keys()


def test_unresolved_for_filters_by_field_and_by_reason(syllabus, p6_conn):
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    assert len(unresolved_for(p6_conn, field_key="work_type", **args)) == 1
    assert unresolved_for(p6_conn, field_key="subject", **args) == []
    assert len(unresolved_for(p6_conn, reason=UNRESOLVED_REASONS[0], **args)) == 1
    assert unresolved_for(p6_conn, reason=UNRESOLVED_REASONS[1], **args) == []


# ------------------------------------------------------------------- Done-means 13, §3.8

def test_an_authored_by_value_is_never_returned_as_destination_eligible(p6_conn):
    """§3.8: "It should avoid using authorship or creator identity as a destination
    dimension." Done-means 13, asserted from the read rather than from the catalogue."""
    assert is_destination_eligible(p6_conn, field_key="authored_by") is False


def test_every_role_field_is_refused_as_a_destination(p6_conn):
    """§3.8 names four — "authored_by and target_school, or our_firm and client" — and the
    rule binds all four, not only the one Done-means 13 spells."""
    for field_key in ("authored_by", "target_school", "our_firm", "client"):
        assert is_destination_eligible(p6_conn, field_key=field_key) is False


def test_a_destination_question_about_an_unknown_field_raises(p6_conn):
    """Silently answering False for a field that does not exist would let a typo read as
    a policy. §3.12 forbids inventing fields; this read does not invent one either."""
    with pytest.raises(FieldNotInCatalogue):
        is_destination_eligible(p6_conn, field_key="destination")


# --------------------------------------------------------------------- the evidence walk

def test_evidence_chain_walks_a_fact_back_to_its_p4_observations(syllabus, p6_conn):
    """Done-means 30's read half: every step resolves, and what comes back is P4's frozen
    shape with its raw value unchanged (§3.2)."""
    chain = evidence_chain(p6_conn, fact_id=syllabus["subject_id"])
    assert [o.observation_key for o in chain] == [syllabus["subject_ref"]]
    assert chain[0].raw_value == "BUSIB 4300"
    assert isinstance(chain[0], Observation)


def test_evidence_chain_returns_p4s_shape_unaltered(syllabus, p6_conn):
    """The carve-out, asserted rather than assumed: this read hands back P4 objects, so
    `container_path` is a locator inside the document and not a P6 column."""
    observation = evidence_chain(p6_conn, fact_id=syllabus["subject_id"])[0]
    assert observation.location.container_path[0].label == "title"
    assert observation.location.zone == "metadata"


def test_a_citation_that_resolves_to_nothing_raises(syllabus, p6_conn):
    """§3.1: "Every fact preserves where it came from." A fact whose citation is gone is
    broken; returning an empty list would let Done-means 30 pass by counting zero."""
    p6_conn.execute("DELETE FROM evidence WHERE observation_key = ?",
                    (syllabus["subject_ref"],))
    with pytest.raises(DanglingCitation):
        evidence_chain(p6_conn, fact_id=syllabus["subject_id"])


def test_evidence_chain_on_an_unknown_fact_raises(p6_conn):
    with pytest.raises(LookupError):
        evidence_chain(p6_conn, fact_id="fact-that-was-never-written")


# -------------------------------------------------------------------- §5.5's branch counts

def test_values_with_counts_supports_the_branch_preview(p6_conn, tmp_path):
    """§5.5: "The interface can state that Option A would create three schools, five terms,
    and twelve course branches". The read has to answer that before the user commits, so
    it counts FILES per value, which is what a branch will hold."""
    seen = []
    for index, (name, subject) in enumerate((
            ("a.pdf", "BUSIB 4300"), ("b.pdf", "BUSIB 4300"),
            ("c.pdf", "BUSIB 4300"), ("d.pdf", "ECON 2100"),
            ("e.pdf", "STAT 1001"))):
        file_id, content_hash = _record(p6_conn, tmp_path, name=name,
                                        body=f"{subject} number {index}".encode())
        ref = _observe(p6_conn, run_id=f"run-{index}", file_id=file_id,
                       content_hash=content_hash, raw=subject, label="title")
        _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
              value=subject, ref=ref, state=VALIDATED, origin=RULE)
        seen.append(file_id)
    assert values_with_counts(p6_conn, field_key="subject") == [
        ("BUSIB 4300", 3), ("ECON 2100", 1), ("STAT 1001", 1)]


def test_branch_counts_are_totally_ordered_so_the_preview_is_stable(p6_conn, tmp_path):
    """Count descending, then canonical value ascending. Ties are broken by the value and
    never by insertion order, which is a property of one database and not of the corpus."""
    for index, (name, subject) in enumerate((
            ("z.pdf", "ZOOL 1000"), ("a.pdf", "ANTH 1000"))):
        file_id, content_hash = _record(p6_conn, tmp_path, name=name,
                                        body=f"{subject}".encode())
        ref = _observe(p6_conn, run_id=f"tie-{index}", file_id=file_id,
                       content_hash=content_hash, raw=subject, label="title")
        _fact(p6_conn, file_id=file_id, content_hash=content_hash, field_key="subject",
              value=subject, ref=ref, state=VALIDATED, origin=RULE)
    assert values_with_counts(p6_conn, field_key="subject") == [
        ("ANTH 1000", 1), ("ZOOL 1000", 1)]


def test_a_value_no_active_fact_points_at_is_not_a_branch(syllabus, p6_conn):
    """§3.12 lets a value auto-create on first sight. A value with no file behind it would
    preview an empty folder, so it is not a branch — the count read shows what will be
    filed, not what has ever been named."""
    ensure_value(p6_conn, field_key="subject", canonical_value="HIST 9999",
                 first_evidence_ref=syllabus["subject_ref"], origin=VALUE_ORIGINS[0])
    assert "HIST 9999" not in dict(values_with_counts(p6_conn, field_key="subject"))


def test_counts_for_an_unknown_field_raise(p6_conn):
    with pytest.raises(FieldNotInCatalogue):
        values_with_counts(p6_conn, field_key="folder")


# ------------------------------------------------------------------- filtering and history

def test_facts_for_filters_by_state(syllabus, p6_conn):
    rows = facts_for(p6_conn, file_id=syllabus["file_id"],
                     content_hash=syllabus["content_hash"], states=(POSSIBLE,))
    assert [row["field_key"] for row in rows] == [DOWNLOAD_SESSION_FIELD]


def test_facts_for_filters_by_domain(syllabus, p6_conn):
    """`domain` is a field scope. §3.11 puts `subject` in Academic; the role fields and
    `download_session` are universal, so the academic read returns one row."""
    rows = facts_for(p6_conn, file_id=syllabus["file_id"],
                     content_hash=syllabus["content_hash"], domain="academic")
    assert [row["field_key"] for row in rows] == ["subject"]


def test_an_unknown_state_or_domain_raises_rather_than_returning_nothing(syllabus, p6_conn):
    """An empty list for a misspelled filter is how a caller concludes there are no facts.
    P4's `check` is the project's one vocabulary gate and this read uses it."""
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    with pytest.raises(NotInVocabulary):
        facts_for(p6_conn, states=("LLM-supported",), **args)
    with pytest.raises(NotInVocabulary):
        facts_for(p6_conn, domain="Academic", **args)


def test_the_unfiltered_read_still_shows_rejected_facts(syllabus, p6_conn):
    """§3.13 makes `rejected` an exclusion from proposals, not from the record. The review
    UI must be able to see what was rejected and why, or §8.5's "Did it abstain when
    evidence was absent?" is unanswerable from the outside."""
    rows = facts_for(p6_conn, file_id=syllabus["file_id"],
                     content_hash=syllabus["content_hash"])
    assert REJECTED in {row["reliability_state"] for row in rows}


def test_history_returns_superseded_rows(syllabus, p6_conn, tmp_path):
    """§8.2's worked example arriving as the ordinary path: the old row stays readable."""
    ref = _observe(p6_conn, run_id="r-ocr", file_id=syllabus["file_id"],
                   content_hash=syllabus["content_hash"], raw="BUSIB 4300",
                   label="heading")
    newer = _fact(p6_conn, file_id=syllabus["file_id"],
                  content_hash=syllabus["content_hash"], field_key="subject",
                  value="BUSIB 4300 Business Analytics", ref=ref, state=VALIDATED,
                  origin=RULE)
    supersede_fact(p6_conn, old_fact_id=syllabus["subject_id"], new_fact_id=newer,
                   reason="a later pass read the heading")
    rows = history(p6_conn, file_id=syllabus["file_id"], field_key="subject")
    assert [row["fact_id"] for row in rows] == [syllabus["subject_id"], newer]


def test_the_three_handed_families_have_their_own_reads(syllabus, p6_conn):
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    assert [row["field_key"] for row in session_facts(p6_conn, **args)] == [
        DOWNLOAD_SESSION_FIELD]
    assert [row["field_key"] for row in event_facts(p6_conn, **args)] == [EVENT_FIELD]
    assert family_facts(p6_conn, **args) == []


def test_the_active_allowlist_is_the_domain_modules_answer(syllabus, p6_conn):
    """§3.12: "it should not invent new fields automatically". The allowlist read adds no
    field of its own — it republishes Task 13's under the name neighbours use."""
    def signals(conn, *, file_id, content_hash):
        return frozenset({"academic"})

    allowlist = active_allowlist_for(
        p6_conn, file_id=syllabus["file_id"], content_hash=syllabus["content_hash"],
        activation_signals=signals)
    assert "subject" in allowlist
    assert "course" not in allowlist


# ----------------------------------------------------------- the negative contract, §3.14

def test_no_read_returns_a_path_a_destination_a_folder_or_a_group(syllabus, p6_conn):
    """§3.14: "A fact such as subject = BUSIB 4300 does not itself dictate one permanent
    folder path." Task 4 asserts this from `PRAGMA table_info`; this asserts it from the
    shapes that leave the package, so a column that reached a neighbour would fail twice."""
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    reads = (facts_for(p6_conn, **args),
             proposal_eligible(p6_conn, **args),
             unresolved_for(p6_conn, **args),
             event_facts(p6_conn, **args),
             session_facts(p6_conn, **args),
             family_facts(p6_conn, **args),
             history(p6_conn, file_id=syllabus["file_id"], field_key="subject"))
    assert all(rows for rows in reads[:2])
    for rows in reads:
        for row in rows:
            for key in row.keys():
                for forbidden in FORBIDDEN_COLUMN_SUBSTRINGS:
                    assert forbidden not in key.lower(), (key, forbidden)


def test_the_read_surface_writes_nothing(syllabus, p6_conn):
    """A read that could change what it reports is not a read. Asserted over the whole
    module by comparing every P6 table before and after every read runs."""
    def snapshot():
        return {table: p6_conn.execute(
                    f"SELECT count(*) FROM {table}").fetchone()[0]
                for table in ("fields", "values", "file_facts", "unresolved")}

    before = snapshot()
    args = dict(file_id=syllabus["file_id"], content_hash=syllabus["content_hash"])
    facts_for(p6_conn, **args)
    proposal_eligible(p6_conn, **args)
    unresolved_for(p6_conn, **args)
    event_facts(p6_conn, **args)
    session_facts(p6_conn, **args)
    family_facts(p6_conn, **args)
    history(p6_conn, file_id=syllabus["file_id"], field_key="subject")
    evidence_chain(p6_conn, fact_id=syllabus["subject_id"])
    values_with_counts(p6_conn, field_key="subject")
    is_destination_eligible(p6_conn, field_key="authored_by")
    assert snapshot() == before


def test_no_read_accepts_a_group(p6_conn):
    """§4.3 and §4.1: the graph "does not automatically copy those missing facts onto
    sparse files". A read that took a group id would be the place that started."""
    import inspect

    from facts import read_surface

    for name, member in vars(read_surface).items():
        if name.startswith("_") or not callable(member):
            continue
        if getattr(member, "__module__", None) != read_surface.__name__:
            continue
        parameters = set(inspect.signature(member).parameters)
        assert not parameters & {"group_id", "group", "group_ids", "members",
                                 "member_ids", "anchor", "anchor_file_id"}, name
```

- [ ] **Step 2: Run the test and watch it fail for the one right reason**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_read_surface.py -x -q
```

Expected: **collection error**, `ModuleNotFoundError: No module named 'facts.read_surface'`. Not one
test runs. Every other import in the file resolves, because Tasks 1–23 are green when this task
starts — so a different missing name here means a sibling task changed a published signature and
that is the thing to fix first, not this file.

- [ ] **Step 3: Create `src/facts/read_surface.py` with the complete implementation**

```python
# src/facts/read_surface.py
"""P6's read surface — the only shape P9, P10, P11, P13, P2 and the review UI see.

Three properties hold across every function here, and each of them is a test in
`tests/p6/test_p6_read_surface.py`:

* it is a pure read — nothing here writes a row, appends an event or resolves a fact;
* it returns no filing decision — §3.14: "A fact such as subject = BUSIB 4300 does not
  itself dictate one permanent folder path";
* it imposes its own total order — P4's reads are insertion-ordered, which is a property
  of one database and not of the corpus, so every read here sorts before it returns.

`evidence_chain` is the one function that returns something other than P6's own rows: it
returns P4 `Observation` objects verbatim, because §3.2 requires the product to "preserve
both the original evidence and the conclusion built from it".
"""
from __future__ import annotations

import json
import sqlite3
from typing import Iterable, Sequence

from evidence_shape.observation import Observation
from evidence_shape.store import observations_by_key
from evidence_shape.vocabulary import check

from facts.domains import active_field_allowlist
from facts.families import DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD
from facts.fields import FIELD_SCOPES, fields_in_scope, get_field
from facts.file_facts import facts_for_file
from facts.photo_event import EVENT_FIELD
from facts.session import DOWNLOAD_SESSION_FIELD
from facts.states import STATES, STRENGTH_ORDER
from facts.supersede import fact_history
from facts.unresolved import unresolved_for_file
from facts.values import values_in_field

#: §3.6's two exclusions, DERIVED rather than spelled. `rejected` is the one member of
#: `STATES` that Task 1 gives no strength, so it is absent from `STRENGTH_ORDER`;
#: `possible` is the weakest ranked state, so it is the last member. Slicing the last one
#: off therefore drops both, and no state name is written down in this module.
PROPOSAL_ELIGIBLE_STATES: tuple[str, ...] = STRENGTH_ORDER[:-1]


class DanglingCitation(LookupError):
    """A fact cites an `observation_key` that resolves to no observation.

    §3.1: "Every fact preserves where it came from." A citation that resolves to nothing
    is a broken fact, not an empty result.
    """


def _field_index(conn: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    """`field_key` -> its catalogue row, built from Task 2's published scope read only."""
    index: dict[str, sqlite3.Row] = {}
    for scope in FIELD_SCOPES:
        for row in fields_in_scope(conn, scope):
            index[row["field_key"]] = row
    return index


def _ordered(rows: Iterable[sqlite3.Row]) -> list[sqlite3.Row]:
    """P6's own total order. Never SQLite's, never P4's insertion order."""
    return sorted(rows, key=lambda row: (row["field_key"], str(row["value_id"]),
                                         row["fact_id"]))


def _in_fields(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
               field_keys: Sequence[str]) -> list[sqlite3.Row]:
    wanted = frozenset(field_keys)
    return _ordered(row for row in facts_for_file(conn, file_id, content_hash)
                    if row["field_key"] in wanted)


def facts_for(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
              states: Iterable[str] | None = None,
              domain: str | None = None) -> list[sqlite3.Row]:
    """Every fact for one file version, optionally narrowed by state or by field scope.

    Unfiltered, this includes `rejected` facts: §3.13 makes `rejected` an exclusion from
    proposals, not from the record, and the review UI has to be able to see what was
    rejected. `proposal_eligible` is the read that excludes it.
    """
    if states is not None:
        states = tuple(states)
        for state in states:
            check(state, STATES, name="reliability_state")
        allowed: frozenset[str] | None = frozenset(states)
    else:
        allowed = None
    if domain is not None:
        check(domain, FIELD_SCOPES, name="scope")
        index = _field_index(conn)
    selected: list[sqlite3.Row] = []
    for row in facts_for_file(conn, file_id, content_hash):
        if allowed is not None and row["reliability_state"] not in allowed:
            continue
        if domain is not None:
            field = index.get(row["field_key"])
            if field is None or field["scope"] != domain:
                continue
        selected.append(row)
    return _ordered(selected)


def proposal_eligible(conn: sqlite3.Connection, *, file_id: str,
                      content_hash: str) -> list[sqlite3.Row]:
    """The facts a folder proposal may rest on.

    §3.6: a weak model output "may remain a possible clue for review; it must not quietly
    become a folder proposal or an asserted file property". `unresolved` rows are in a
    different table and are therefore absent by construction rather than by a filter.
    """
    return facts_for(conn, file_id=file_id, content_hash=content_hash,
                     states=PROPOSAL_ELIGIBLE_STATES)


def active_allowlist_for(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                         activation_signals) -> tuple[str, ...]:
    """§3.11's active field allowlist, republished under the name neighbours use. The
    signals are injected and this module adds no field of its own (§3.12)."""
    return active_field_allowlist(conn, file_id=file_id, content_hash=content_hash,
                                  activation_signals=activation_signals)


def values_with_counts(conn: sqlite3.Connection, *,
                       field_key: str) -> list[tuple[str, int]]:
    """§5.5's branch preview: "The interface can state that Option A would create three
    schools, five terms, and twelve course branches."

    Counts FILES per value, because that is what a branch will hold, and omits values no
    active fact points at, because those would preview an empty folder. Ordered by count
    descending then canonical value ascending, so the preview is stable across runs.
    """
    get_field(conn, field_key)
    counts: dict[str, int] = {}
    for row in conn.execute(
            "SELECT value_id, COUNT(DISTINCT file_id) FROM file_facts "
            "WHERE active = 1 GROUP BY value_id"):
        counts[row[0]] = row[1]
    branches = [(row["canonical_value"], counts.get(row["value_id"], 0))
                for row in values_in_field(conn, field_key)]
    return sorted(((value, count) for value, count in branches if count),
                  key=lambda pair: (-pair[1], pair[0]))


def evidence_chain(conn: sqlite3.Connection, *, fact_id: str) -> list[Observation]:
    """One fact walked back to the P4 observations it cites.

    Every entry in `evidence_refs[]` is an `observation_key` (M14), which is
    content-addressed and excludes `extractor_version` by construction — so a citation
    recorded before an extractor upgrade still resolves after one (§8.7).
    """
    row = conn.execute("SELECT evidence_refs FROM file_facts WHERE fact_id = ?",
                       (fact_id,)).fetchone()
    if row is None:
        raise LookupError(f"no fact {fact_id!r}")
    chain: list[Observation] = []
    for key in json.loads(row[0]):
        found = observations_by_key(conn, key)
        if not found:
            raise DanglingCitation(
                f"fact {fact_id!r} cites {key!r}, which resolves to no observation")
        chain.extend(sorted(found, key=lambda o: o.observation_id))
    return chain


def history(conn: sqlite3.Connection, *, file_id: str,
            field_key: str) -> list[sqlite3.Row]:
    """Oldest first, superseded rows included. §8.2 keeps them readable."""
    get_field(conn, field_key)
    return fact_history(conn, file_id=file_id, field_key=field_key)


def unresolved_for(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                   field_key: str | None = None,
                   reason: str | None = None) -> list[sqlite3.Row]:
    """The abstentions, which appear in no fact read. §8.5 asks "Did it abstain when
    evidence was absent?" and an absent row cannot answer it."""
    return unresolved_for_file(conn, file_id, content_hash, field_key=field_key,
                               reason=reason)


def event_facts(conn: sqlite3.Connection, *, file_id: str,
                content_hash: str) -> list[sqlite3.Row]:
    """G7's photo event — a P9 seed, never a placement."""
    return _in_fields(conn, file_id=file_id, content_hash=content_hash,
                      field_keys=(EVENT_FIELD,))


def session_facts(conn: sqlite3.Connection, *, file_id: str,
                  content_hash: str) -> list[sqlite3.Row]:
    """G6's bounded download session. §3.9 makes it "not a basis for automatic semantic
    propagation", so it never exceeds `possible` and never reaches `proposal_eligible`."""
    return _in_fields(conn, file_id=file_id, content_hash=content_hash,
                      field_keys=(DOWNLOAD_SESSION_FIELD,))


def family_facts(conn: sqlite3.Connection, *, file_id: str,
                 content_hash: str) -> list[sqlite3.Row]:
    """G5's duplicate family and version family."""
    return _in_fields(conn, file_id=file_id, content_hash=content_hash,
                      field_keys=(DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD))


def is_destination_eligible(conn: sqlite3.Connection, *, field_key: str) -> bool:
    """§3.8: the product "should avoid using authorship or creator identity as a
    destination dimension". Raises `FieldNotInCatalogue` on an unknown field rather than
    answering False, so a typo cannot read as a policy."""
    return bool(get_field(conn, field_key)["destination_eligible"])
```

- [ ] **Step 4: Run the test again and watch it pass**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_read_surface.py -q
```

Expected: **26 passed**. Then the whole part, to prove no sibling read regressed:

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6 -q
```

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add src/facts/read_surface.py tests/p6/test_p6_read_surface.py && \
git commit -m "feat(P6): the read surface published to neighbours — two exclusions derived, never spelled"
```

---

---

### Task 25: The no-invention guard — every open question and every deferred row held open

**Files:**
- Test only: `tests/p6/test_p6_no_invention.py`
- Creates and modifies **no** source file. If this task has to change a line under `src/facts/` to go
  green, the line it changes is the finding and the change belongs to whichever task owns that module.

**Interfaces:**
- Consumes: every module in `facts`, by runtime introspection of `vars(module)` and of each module's
  compiled code object; `facts.fields` — `FIELD_ROWS`, `FieldRow`, `FIELD_SCOPES`, `UNIVERSAL_FIELDS`,
  `DOMAIN_FIELDS`, `fields_in_scope`, `get_field`, `FieldNotInCatalogue`; `facts.states` — `STATES`,
  `STRENGTH_ORDER`, `is_stronger`; `facts.unresolved` — `UNRESOLVED_REASONS`; `facts.values` —
  `ensure_value`, `VALUE_ORIGINS`; `facts.authorship.SUBSYSTEM`; `facts.evidence` —
  `observations_for_version`; `evidence_shape.vocabulary.SOURCE_TYPES`;
  `planning/deferred-catalogues/01-tool-producer-strings.json` **as a file the test reads**.
- Produces: nothing.

**Done-means:** none numbered. It is what makes the Deferred table true.

---

**Why every guard here is runtime and not textual.** A source-text search matches comments and
docstrings, and scanning text for a token has produced a **false result nine times on this project**
— most recently P5's PLAN Task 20, where a `grep` for a threshold matched the sentence explaining
that there was no threshold. So the guards below use two runtime tools and nothing else:

| Tool | What it can see | What it is used for here |
|---|---|---|
| `vars(module)` walked recursively | every **module-level binding** and everything reachable inside it — tuples, mappings, frozen dataclasses | thresholds, weights, resolutions, aspect ratios, session windows, GPS radii, usable-fact counts, compiled regexes, gazetteers, producer-string lists |
| the module's **compiled code object** (`__loader__.get_code(...)`, recursed through nested code objects) | every literal the compiler kept, **including literals inside function bodies** | catalogue 01's producer strings, and the single home of `subsystem = "P6"` |

The second tool matters because the namespace walk alone cannot see a literal buried in a function
body — and that is exactly where a copied catalogue would end up. A comment can never reach
`co_consts`; a docstring reaches it only as the whole docstring, so an **equality** test against a
short token like `"P6"` or `"python-docx"` cannot be satisfied by prose.

**One exemption, and it is by identity, which is the point.** A `facts` module that does
`from evidence_shape.vocabulary import SIGNAL_TIERS` binds a tuple of integers at module level. That
is a re-export of P4's published vocabulary, not a P6 invention, and the guard exempts it **because
`id(value)` matches an object P4 published** — so a re-export passes and a hand-typed copy of the
same numbers fails. That is Task 1's rule (*"`STATES` **is** P4's tuple rather than a copy"*) applied
to every upstream vocabulary at once. A **contiguous slice** of a published upstream tuple is exempt
on the same grounds: Task 16 reads §2.6's screenshot band as `SIGNAL_TIERS[-1:]` precisely so it does
not have to spell a `3`, and a guard that punished that would push the author back to the literal.

**Two guards INVERT here, and the inversion is the whole reason this task is written last.** OQ4 and
OQ11 are closed. A test asserting they are open passes today and **fails the day the decision is
applied — which is the day this plan is executed.** So they assert the closure. Their residues stay
open by name, and OQ11's residue is named in its own test rather than left implied.

**Contradiction found and reported, not resolved.** P7's SPEC, Contract-in, line 90, says in bold:
*"P6 must accept `sensitivity` as a first-class universal field"*. §3.12 names `sensitivity` in the
design's own field list — *"subject, purpose, target university, project, event, or sensitivity"* —
and §3.11 spells it `sensitivity status`. Against that, D2 makes P7's `ClassificationRecord`
authoritative, round 1's F-2 found the P6 field has **no producer**, and NEEDS-JOSEPH **C5** holds
the question of whether the row survives. The authoring brief's instruction is unambiguous: *"Create
no such row either way."* This task therefore asserts **today's** state — no row, under either
spelling — and its test says in its own body that it settles nothing. If Joseph keeps the row, this
test is where the decision lands and the flip is one line here plus one row in Task 2's catalogue.

- [ ] **Step 1: Create `tests/p6/test_p6_no_invention.py` with the complete failing test**

```python
# tests/p6/test_p6_no_invention.py
"""Task 25 — the no-invention guard.

Every threshold, weight, gazetteer, regex catalogue, producer string, resolution, aspect
ratio, session window, GPS radius and usable-fact count in P6 is injected by the caller
with no default. Every still-open question in P6's SPEC stays open. The two that closed
(OQ4, OQ11) have their guards INVERTED, so this file fails if the closure is ever quietly
un-applied.

Nothing here reads source text. See the two-tool table in this task's plan section.
"""
import dataclasses
import importlib
import inspect
import json
import os
import pkgutil
import re
import subprocess
import sys
import types
from collections.abc import Mapping
from pathlib import Path

import pytest

from evidence_shape.vocabulary import SOURCE_TYPES

import facts
from facts.authorship import SUBSYSTEM
from facts.fields import (
    DOMAIN_FIELDS, FIELD_ROWS, FIELD_SCOPES, FieldNotInCatalogue, FieldRow,
    UNIVERSAL_FIELDS, fields_in_scope, get_field,
)
from facts.states import STATES, STRENGTH_ORDER, is_stronger
from facts.unresolved import UNRESOLVED_REASONS
from facts.values import VALUE_ORIGINS, ensure_value

REPO = Path(__file__).resolve().parents[2]
CATALOGUE_01 = REPO / "planning" / "deferred-catalogues" / "01-tool-producer-strings.json"

#: Task 2 owns the spelling of each scope; this file re-spells none of them.
UNIVERSAL, ACADEMIC, COLLEGE_APPLICATIONS, RESEARCH, FINANCE, PHOTOS, CODE = FIELD_SCOPES

#: The file layout the plan declares, and nothing else. A `catalogues.py` appearing here
#: is how catalogue 01 would arrive as a module-level constant while satisfying the letter
#: of every other guard in this file, so the module set itself is asserted.
DECLARED_MODULES = frozenset({
    "authorship", "budgets", "cache", "dates", "direct", "discount", "domains",
    "evidence", "facets", "families", "fields", "file_facts", "learning", "llm_seam",
    "photo_event", "plan_versions", "read_surface", "resolver", "rules", "schema",
    "session", "states", "stage_output", "supersede", "unresolved", "usable", "values",
    "vocabulary",
})

#: Every module-level COLLECTION P6 is allowed to publish, with the task that owns it.
#: A plain string constant needs no entry — a field key is not a catalogue. A collection
#: does, because a gazetteer, a producer-string list, a zone-weight map and a regex
#: catalogue are all collections, and the only way to tell one from a closed vocabulary is
#: to have written the closed vocabularies down. A name missing from this set is a RED
#: TEST, and the fix is a line here with the task that justifies it — never a widening of
#: the rule.
DECLARED_VOCABULARIES = frozenset({
    "AUTHORED_EVENT_TYPES",                                   # Task 1  §8.2's two names
    "STATES", "STRENGTH_ORDER",                               # Task 1  §3.13
    "FIELD_SCOPES", "UNIVERSAL_FIELDS", "DOMAIN_FIELDS", "FIELD_ROWS",   # Task 2  §3.11
    "VALUE_ORIGINS",                                          # Task 3  §3.12
    "FILE_FACTS_COLUMNS", "FORBIDDEN_COLUMN_SUBSTRINGS", "FACT_ORIGINS",  # Task 4 §3.1
    "UNRESOLVED_REASONS", "ATTEMPTED_PRODUCERS", "NOT_ABSTENTIONS",       # Task 5 B7
    "UNRESOLVED_COLUMNS",                                     # Task 5  the negative half
    "FACTS_TABLES",                                           # Tasks 2-5, 19  schema.py
    "CACHE_KEY_PARTS",                                        # Task 6  §3.4
    "SLOT_KINDS",                                             # Task 8  §3.5's slot kinds
    "VERSION_FAMILY_STATES",                                  # Task 14 §8.3
    "EVENT_INPUTS", "MEDIA_TYPES", "PHOTO_BANDS", "SCREENSHOT_BAND",      # Task 16 §2.6
    "FOUR_CHECKS", "CHECK_REASONS", "LLM_STATES",             # Task 17 §3.6
    "P6_CEILING_KEYS", "DEGRADATION_ORDER",                   # Task 20 §8.6
    "ENVELOPE_FIELDS",                                        # Task 21 §8.5
    "PLAN_VERSIONED", "SHARED_ACROSS_PLAN_VERSIONS",          # Task 23 §8.8
    "PROPOSAL_ELIGIBLE_STATES",                               # Task 24 §3.6
})

#: Field-creating callables §3.12 forbids: "it should not invent new fields automatically".
FIELD_CREATORS = frozenset({"add_field", "create_field", "register_field", "define_field",
                            "new_field", "add_fields"})

#: A group handle, by exact parameter name. §4.3 and §4.1: the graph "does not
#: automatically copy those missing facts onto sparse files". `file_ids` is NOT here — it
#: is an explicit set the caller passes, which is the opposite of a membership lookup —
#: and neither is `clustering`, which is Task 16's injected boundary.
GROUP_PARAMETERS = frozenset({"group_id", "group", "group_ids", "members", "member_ids",
                              "anchor", "anchor_file_id", "group_membership"})

#: Names that would encode an answer to OQ10 instead of refusing. Exact, never substrings:
#: `preferred_fact` is Task 18's legitimate pointer and must not be caught by a guess.
TIE_BREAK_NAMES = frozenset({"TIE_BREAK", "TIEBREAK", "TIE_BREAKER", "TIE_BREAK_ORDER",
                             "CONTRADICTION_WINNER", "EQUAL_RANK_POLICY"})

#: Modules whose objects are re-exports rather than P6 inventions.
UPSTREAM_MODULES = (
    "evidence_shape.vocabulary", "evidence_shape.observation", "evidence_shape.conformance",
    "evidence_shape.runs", "evidence_shape.schema", "evidence_shape.canonical",
    "evidence_shape.location", "evidence_shape.store", "evidence_shape.fixtures",
    "database_agent.events", "database_agent.supersede", "database_agent.budget",
    "database_agent.files_table", "database_agent.db", "database_agent.learning",
    "eval_harness.vocabulary", "eval_harness.run", "eval_harness.replay",
    "eval_harness.stage_output", "eval_harness.adversarial",
)

#: `from __future__ import annotations` binds a `_Feature` object at module level. It is
#: not P6 data and it is the only such binding, so it is named rather than pattern-matched.
IGNORED_BINDINGS = frozenset({"annotations"})

TYPING_HOMES = frozenset({"typing", "collections.abc", "__future__"})


# --------------------------------------------------------------------- the two tools

def facts_modules():
    """Every module in `facts`, imported. `facts/__init__.py` is a package marker and
    re-exports nothing, so it is walked with the rest rather than trusted."""
    modules = [facts]
    for info in pkgutil.iter_modules(facts.__path__):
        modules.append(importlib.import_module(f"facts.{info.name}"))
    return tuple(modules)


def module_constants(module):
    """Module-level DATA bindings: not modules, not classes, not callables, not typing
    machinery. An imported constant still counts — a copied gazetteer is still a gazetteer
    when it arrives through an import, which is why the exemption below is by identity."""
    out = {}
    for name, value in vars(module).items():
        if name.startswith("__") or name in IGNORED_BINDINGS:
            continue
        if isinstance(value, (types.ModuleType, type)):
            continue
        if getattr(value, "__module__", None) in TYPING_HOMES:
            continue
        if callable(value) and not dataclasses.is_dataclass(value):
            continue
        out[name] = value
    return out


def reachable(value, out=None, seen=None):
    """Every object reachable from one binding: through mappings, sequences, sets and
    frozen dataclasses. Materialized into a list so no id is ever reused mid-walk."""
    if out is None:
        out, seen = [], set()
    if id(value) in seen:
        return out
    seen.add(id(value))
    out.append(value)
    if isinstance(value, (str, bytes, bytearray)):
        return out
    if isinstance(value, Mapping):
        for key, item in value.items():
            reachable(key, out, seen)
            reachable(item, out, seen)
    elif dataclasses.is_dataclass(value) and not isinstance(value, type):
        for field in dataclasses.fields(value):
            reachable(getattr(value, field.name), out, seen)
    elif isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            reachable(item, out, seen)
    return out


def code_constants(module):
    """Every literal the compiler kept for this module — function bodies, comprehensions
    and nested definitions included. Bytecode, never source text: a comment cannot reach
    `co_consts`, and a docstring reaches it only as the whole docstring, so equality
    against a short token cannot be satisfied by prose."""
    loader = module.__loader__
    out, stack = set(), [loader.get_code(module.__name__)]
    while stack:
        current = stack.pop()
        for const in current.co_consts:
            if isinstance(const, types.CodeType):
                stack.append(const)
            elif isinstance(const, (str, bytes, int, float, tuple, frozenset)):
                try:
                    out.add(const)
                except TypeError:      # an unhashable nested constant; nothing to match
                    pass
    return out


@pytest.fixture(scope="module")
def upstream():
    """Every object P1, P2 and P4 publish, held alive and indexed by identity.

    A re-export passes; a hand-typed copy of the same values does not. That is Task 1's
    rule generalized: "`STATES` IS P4's tuple rather than a copy"."""
    held = []
    for name in UPSTREAM_MODULES:
        module = importlib.import_module(name)
        held.extend(vars(module).values())
    return held, frozenset(id(value) for value in held)


def is_upstream(value, upstream):
    """Identity, or a contiguous slice of a published upstream tuple.

    The slice arm exists for exactly one reason and it is a good one: Task 16 reads §2.6's
    screenshot band as `SIGNAL_TIERS[-1:]` so it never has to spell a `3`. Punishing that
    would push the author back to the literal, which is the thing being guarded against."""
    held, ids = upstream
    if id(value) in ids:
        return True
    if not isinstance(value, tuple) or not value:
        return False
    width = len(value)
    for candidate in held:
        if not isinstance(candidate, tuple) or len(candidate) < width:
            continue
        if any(candidate[start:start + width] == value
               for start in range(len(candidate) - width + 1)):
            return True
    return False


def offending(predicate, upstream):
    """Every (module, binding, value) in `facts` matching `predicate`, minus re-exports."""
    found = []
    for module in facts_modules():
        for name, binding in module_constants(module).items():
            if is_upstream(binding, upstream):
                continue
            for value in reachable(binding):
                if predicate(value):
                    found.append((module.__name__, name, repr(value)[:80]))
    return found


# ------------------------------------------- no invented number, regex or catalogue

def test_no_threshold_weight_window_radius_or_count_exists_as_a_module_constant(upstream):
    """Every one of them is a NUMBER, so one predicate covers the lot: minimum score,
    minimum margin, positional weight, signal-tier weight, session window, GPS radius,
    screen resolution, sensor aspect ratio and the usable-fact threshold.

    Each is a Deferred row and each is injected with no default. `bool` is excluded
    because `destination_eligible` and `active` are flags, not quantities."""
    def is_number(value):
        return isinstance(value, (int, float, complex)) and not isinstance(value, bool)

    assert offending(is_number, upstream) == []


def test_no_regex_catalogue_exists_as_a_module_constant(upstream):
    """§3.10 forbids fuzzy date parsing and requires explicit patterns — and Task 12
    receives them as an injected `DatePatterns`, including the three the design names
    (`Spring 2025`, `AY 2024-25`, `Michaelmas Term 2024`). A compiled pattern sitting at
    module level in `facts` is that catalogue having moved in."""
    assert offending(lambda value: isinstance(value, re.Pattern), upstream) == []


def test_every_module_level_collection_is_a_declared_closed_vocabulary(upstream):
    """A gazetteer, a producer-string list, a zone-weight map and a closed vocabulary are
    all collections. The only way to tell them apart is to have written the closed
    vocabularies down, so a new collection is a red test until someone justifies it."""
    undeclared = []
    for module in facts_modules():
        for name, binding in module_constants(module).items():
            if isinstance(binding, (tuple, list, set, frozenset, dict, Mapping)):
                if is_upstream(binding, upstream):
                    continue
                if name not in DECLARED_VOCABULARIES:
                    undeclared.append((module.__name__, name, len(binding)))
    assert undeclared == []


def test_no_producer_string_from_catalogue_01_appears_anywhere_in_facts():
    """Catalogue 01's own `injection` clause: "P6 receives this list as data at
    construction ... It is **not** imported as a module-level constant."

    Copying it into a `facts` module would satisfy every namespace guard above while
    destroying their point, so this one reads the compiled code: a literal inside a
    function body is caught exactly like one at module level. The `property_names` blocks
    are included because "the metadata property names the discount rule reads" is its own
    Deferred row (Task 9), owned by the catalogue and not by `facts`."""
    assert CATALOGUE_01.is_file(), CATALOGUE_01
    catalogue = json.loads(CATALOGUE_01.read_text(encoding="utf-8"))
    banned = {entry["match"].casefold()
              for block in ("entries", "refused", "uncertain")
              for entry in catalogue[block]}
    for value in catalogue["property_names"].values():
        if isinstance(value, list):
            banned.update(name.casefold() for name in value)
    assert len(banned) >= 115

    found = []
    for module in facts_modules():
        for const in code_constants(module):
            if isinstance(const, str) and const.casefold() in banned:
                found.append((module.__name__, const))
    assert found == []


def test_facts_names_no_file_and_holds_no_path(upstream):
    """P6 loads nothing from disk. A `Path`, or a string naming anything under
    `planning/`, is a catalogue arriving by another door."""
    def is_path_like(value):
        if isinstance(value, Path):
            return True
        if not isinstance(value, str):
            return False
        lowered = value.casefold()
        return ("planning/" in lowered or lowered.endswith(".json")
                or "deferred-catalogues" in lowered)

    assert offending(is_path_like, upstream) == []


def test_facts_has_exactly_the_modules_the_plan_declares():
    """The file layout is a contract. A `catalogues.py` is the one new module that would
    pass every other guard in this file on the day it was added."""
    present = {info.name for info in pkgutil.iter_modules(facts.__path__)}
    assert present == DECLARED_MODULES


# ------------------------------------------------------- imports: what P6 may not touch

PROBE = (
    "import importlib, json, pkgutil, sys\n"
    "import facts\n"
    "for info in pkgutil.iter_modules(facts.__path__):\n"
    "    importlib.import_module('facts.' + info.name)\n"
    "print(json.dumps({name: getattr(module, '__file__', None)\n"
    "                  for name, module in sys.modules.items()}))\n"
)
BASELINE = (
    "import json, sys\n"
    "print(json.dumps({name: getattr(module, '__file__', None)\n"
    "                  for name, module in sys.modules.items()}))\n"
)


def _run(source):
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(REPO / "src")
    finished = subprocess.run([sys.executable, "-c", source], cwd=str(REPO),
                              env=environment, capture_output=True, text=True)
    assert finished.returncode == 0, finished.stderr[-2000:]
    return json.loads(finished.stdout)


@pytest.fixture(scope="module")
def import_delta():
    """Exactly what importing every `facts` module pulls in, over a bare interpreter.

    A fresh subprocess, because `sys.modules` inside a pytest run already holds everything
    the rest of the suite imported — asking the live interpreter what P6 imports would
    answer a different question and always answer "everything"."""
    baseline = _run(BASELINE)
    after = _run(PROBE)
    return {name: path for name, path in after.items() if name not in baseline}


def test_nothing_in_facts_imports_planning_domains(import_delta):
    """The skeleton, Task 2: `planning/domains/` is a RESEARCH ARTIFACT — 574 entries,
    2,164 distinct field keys, `proposal` provenance, and its own gate reporting 566
    failures. It is a menu someone may one day draw from entry by entry, with a decision
    each time. It is not this catalogue's source and `facts` must never import it.

    `planning/domains/check.py` is importable — there is a `__pycache__` beside it — so
    this is a live possibility rather than a theoretical one."""
    planning = str(REPO / "planning")
    domains = str(REPO / "planning" / "domains")
    leaked = {name: path for name, path in import_delta.items()
              if path and (path.startswith(domains) or path.startswith(planning))}
    assert leaked == {}


def test_facts_imports_no_grouping_tree_placement_or_model_module(import_delta):
    """P9, P10, P11 and P8 do not exist, and the absence is the contract (§4.1, §4.3,
    §3.3). Stated as an allowlist rather than a blocklist so it still holds on the day
    they are built: the only first-party packages `facts` may reach are these five."""
    allowed = {"facts", "database_agent", "evidence_shape", "eval_harness", "extractors"}
    source_root = str(REPO / "src")
    reached = {name.split(".")[0] for name, path in import_delta.items()
               if path and path.startswith(source_root)}
    assert reached <= allowed
    for forbidden in ("readers", "orchestrator", "scan_agent", "grouping", "tree",
                      "placement", "llm", "model"):
        assert forbidden not in reached


def test_facts_adds_no_third_party_runtime_dependency(import_delta):
    """Python 3.12, stdlib only. Third-party libraries live in `src/readers/` behind the
    `readers` extra and this part may not import one."""
    third_party = {name: path for name, path in import_delta.items()
                   if path and ("site-packages" in path or "dist-packages" in path)}
    assert third_party == {}


# --------------------------------------------------- the other structural single-homes

def test_subsystem_p6_is_written_in_exactly_one_place():
    """M8: P6 authors its events and P1 writes them. A second module spelling the
    subsystem is a second authority over who authored a fact.

    Read from compiled code rather than the namespace, because `from facts.authorship
    import SUBSYSTEM` is a re-export and puts the NAME in `co_consts`, never the value."""
    holders = sorted(module.__name__ for module in facts_modules()
                     if SUBSYSTEM in code_constants(module))
    assert holders == ["facts.authorship"]


def test_no_module_branches_on_source_type_or_extractor_name():
    """§2.8 and Done-means 6: P6 resolves a fixture carrying an unrecognised `source_type`
    with no new code. A per-format branch is how that stops being true, and P6 requires no
    per-format knowledge and must not acquire any."""
    for module in facts_modules():
        for name, member in vars(module).items():
            if name.startswith("_") or not callable(member):
                continue
            if getattr(member, "__module__", None) != module.__name__:
                continue
            try:
                parameters = set(inspect.signature(member).parameters)
            except (TypeError, ValueError):
                continue
            assert "source_type" not in parameters, f"{module.__name__}.{name}"
            assert "extractor_name" not in parameters, f"{module.__name__}.{name}"

    source_types = {value.casefold() for value in SOURCE_TYPES}
    for module in facts_modules():
        for constant_name, binding in module_constants(module).items():
            for value in reachable(binding):
                if isinstance(value, str) and value.casefold() in source_types:
                    pytest.fail(f"{module.__name__}.{constant_name} names a source type")


def test_no_p4_read_is_consumed_in_p4s_order(monkeypatch):
    """P4's reads are `ORDER BY rowid` — insertion order, which is stable within one
    database and is NOT a property of the corpus. Verified by execution on 2026-08-21:
    writing the same three fixtures as runs 1,2,3 and as 3,2,1 returns
    `['BUSIB 4300', 'BUSIB 4300 Syllabus', 'Columbia']` and the reverse.

    Task 7's `observations_for_version` is the one chokepoint every P6 read goes through
    (it is also the per-content-hash filter P4 does not publish), so the guard hands it
    P4's answer in both orders and requires the same result. Behavioural, not structural:
    the question is whether the ORDER changes the RESULT, and only running it can answer
    that. The P4 read is replaced outright, so no database rows are needed."""
    from evidence_shape.location import Location, Segment
    from evidence_shape.observation import Observation

    import facts.evidence
    from facts.evidence import observations_for_version

    digest = "0" * 64
    made = []
    for raw, label in (("BUSIB 4300", "title"),
                       ("BUSIB 4300 Syllabus", "heading"),
                       ("Columbia", "body")):
        made.append(Observation(
            file_id="file-1", content_hash=digest, extractor_name="pdf.text",
            extractor_version="1.0.0", source_type="text_document", raw_value=raw,
            location=Location("metadata", (Segment("field", label=label),)),
            occurrence_count=1, observed_at="2026-08-19T12:00:00+00:00",
            reliability="direct", run_id="run-1"))

    monkeypatch.setattr(facts.evidence, "observations_for_file",
                        lambda conn, file_id: list(made))
    straight = observations_for_version(None, "file-1", digest)

    monkeypatch.setattr(facts.evidence, "observations_for_file",
                        lambda conn, file_id: list(reversed(made)))
    reversed_order = observations_for_version(None, "file-1", digest)

    assert len(straight) == 3
    assert reversed_order == straight


# ================================================================================
# The open questions. One named test each. None of them is answered here.
# ================================================================================

def test_oq3_purpose_is_still_one_row_and_p6_has_not_promoted_it(p6_conn):
    """OQ3, OPEN: "Is `purpose` a universal field or an Applications-domain field? §3.9
    requires it to be 'first-class'; §3.11's universal list omits it and places it only
    under College applications."

    P6 ships §3.11's placement and answers nothing. What it must NOT do is answer the
    question by creating BOTH — a universal `purpose` and a domain `purpose` would be two
    columns for one concept, which is the tie-break rule's exact prohibition: one stored
    key per concept, every other word an alias. Settling OQ3 changes one row's `scope` and
    nothing else, because no module branches on where it lives."""
    rows = [row for row in FIELD_ROWS if row.field_key == "purpose"]
    assert len(rows) == 1
    assert rows[0].scope == COLLEGE_APPLICATIONS
    assert "purpose" not in UNIVERSAL_FIELDS
    assert get_field(p6_conn, "purpose")["scope"] == COLLEGE_APPLICATIONS


def test_oq5_finance_has_a_schema_and_p6_neither_activates_nor_suppresses_it(p6_conn):
    """OQ5, OPEN [seam with P7]: "Finance has a fact schema in §3.11 but is a safety domain
    in §3.15 ... Does the Finance fact schema activate at launch, or does
    detection-and-protection precede any field extraction?"

    P6 holds the schema and decides nothing: activation is entirely the caller's injected
    signals. A module-level constant naming Finance outside the catalogue would be P6
    taking a side, and so would a hard-coded gate on a handling class."""
    assert FINANCE in FIELD_SCOPES
    assert DOMAIN_FIELDS[FINANCE]
    assert fields_in_scope(p6_conn, FINANCE)

    naming = {module.__name__ for module in facts_modules()
              for binding in module_constants(module).values()
              for value in reachable(binding)
              if isinstance(value, str) and value == FINANCE}
    assert naming <= {"facts.fields", "facts.vocabulary"}


def test_oq6_multiplicity_is_a_column_with_no_answer_in_it(p6_conn):
    """OQ6, OPEN: "May one (file, field) hold several simultaneously active values, and if
    so how does the §3.7 margin rule apply when more than one candidate is correct?"

    The column exists so the answer has somewhere to go. Every row's value is `None`, so
    no field has been quietly given a multiplicity, and §3.7's margin rule stays as Task 11
    wrote it: two candidates within the margin fill nothing."""
    assert "multiplicity" in {field.name for field in dataclasses.fields(FieldRow)}
    assert {row.multiplicity for row in FIELD_ROWS} == {None}
    for scope in FIELD_SCOPES:
        for row in fields_in_scope(p6_conn, scope):
            assert row["multiplicity"] is None


def test_oq8_no_producer_can_create_a_field_at_run_time(p6_conn):
    """OQ8, OPEN [seam with P10]: "Does user approval of a custom template create `fields`
    rows, and at what scope — corpus-wide or plan-version-local?"

    Until that is answered, nothing creates one. §3.12: the system "may create new values
    when it sees a new course, project, company, university, or event, but it should not
    invent new fields automatically", and §3.5: "The LLM is not allowed to invent a new
    fact schema, create an unsupported field, or make a free-form filing decision."

    Both halves: no field-creating callable is published, and the attempt raises and
    leaves the catalogue byte for byte unchanged."""
    creators = {f"{module.__name__}.{name}" for module in facts_modules()
                for name in vars(module) if name in FIELD_CREATORS}
    assert creators == set()

    def catalogue():
        return sorted((row["field_key"], row["scope"]) for scope in FIELD_SCOPES
                      for row in fields_in_scope(p6_conn, scope))

    before = catalogue()
    with pytest.raises(FieldNotInCatalogue):
        ensure_value(p6_conn, field_key="admissions_packet", canonical_value="Round 1",
                     first_evidence_ref="sha256:" + "0" * 64, origin=VALUE_ORIGINS[0])
    assert catalogue() == before


def test_oq9_no_write_path_takes_a_group(import_delta):
    """OQ9, OPEN [seam]: "After the user accepts the group, does that purpose become a fact
    on non-anchor members, or does it remain membership only?"

    Until it is settled, P6 writes nothing group-derived — §4.1: the graph "does not
    automatically copy those missing facts onto sparse files"; §3.9: a session is "not a
    basis for automatic semantic propagation". Enforced twice: no grouping module is
    imported at all, and no callable anywhere in `facts` will accept a group handle."""
    assert "grouping" not in {name.split(".")[0] for name in import_delta}

    for module in facts_modules():
        for name, member in vars(module).items():
            if name.startswith("_") or not callable(member):
                continue
            if getattr(member, "__module__", None) != module.__name__:
                continue
            try:
                parameters = set(inspect.signature(member).parameters)
            except (TypeError, ValueError):
                continue
            assert not parameters & GROUP_PARAMETERS, f"{module.__name__}.{name}"


def test_oq10_two_equal_rank_contradicting_facts_are_never_ranked_by_p6():
    """OQ10, OPEN: "§3.13 orders the six states but does not define the comparison for two
    equal-rank contradicting facts ... Reject both, surface both as competing candidates,
    or defer to the internal score?"

    P6 refuses to choose and writes an `unresolved` row instead, which is why the refusal
    is inspectable (§8.5: "Did it abstain when evidence was absent?"). Two halves: a state
    never outranks itself, so the tie is real rather than resolved by an accident of
    comparison; and no constant anywhere encodes a tie-break policy."""
    for state in STRENGTH_ORDER:
        assert is_stronger(state, state) is False

    #: §3.13 makes `rejected` an EXCLUSION, not a rank, so Task 1 gives it no strength and
    #: asking for one raises. That is the reason the loop above is over `STRENGTH_ORDER`
    #: and not over `STATES`: a `rejected` fact is never compared, it is excluded.
    rejected = next(state for state in STATES if state not in STRENGTH_ORDER)
    with pytest.raises(Exception):
        is_stronger(rejected, rejected)

    encoded = {f"{module.__name__}.{name}" for module in facts_modules()
               for name in vars(module) if name in TIE_BREAK_NAMES}
    assert encoded == set()
    assert any("contradict" in reason for reason in UNRESOLVED_REASONS)


# ================================================================================
# The two that CLOSED. Their guards are inverted: they assert the closure.
# ================================================================================

def test_oq4_is_closed_as_subject_and_the_catalogue_carries_no_course_row(p6_conn):
    """OQ4, CLOSED — D6, ratified 2026-08-21. One field, and its key is `subject`.

    §3.1, §3.2 and §3.12 all say `subject`; only §3.11's Academic row says `course`, and
    that is the design's PROSE for the same field. A field key is a join handle, so two
    spellings are two columns — the word `course` survives inside quotations and nowhere
    else. The same rename has already been applied across `planning/domains/` (1,302 keys).

    This guard is INVERTED on purpose. A test asserting OQ4 is open would pass every day
    up to the one this plan is executed and fail on that day, which is the failure mode
    that made the inversion worth writing down."""
    keys = {row.field_key for row in FIELD_ROWS}
    assert "subject" in keys
    assert "course" not in keys
    assert get_field(p6_conn, "subject")["scope"] == ACADEMIC
    with pytest.raises(FieldNotInCatalogue):
        get_field(p6_conn, "course")

    #: Done-means 4's value lands under `subject` and under no other key.
    assert ensure_value(p6_conn, field_key="subject", canonical_value="BUSIB 4300",
                        first_evidence_ref="sha256:" + "1" * 64,
                        origin=VALUE_ORIGINS[0])
    with pytest.raises(FieldNotInCatalogue):
        ensure_value(p6_conn, field_key="course", canonical_value="BUSIB 4300",
                     first_evidence_ref="sha256:" + "1" * 64, origin=VALUE_ORIGINS[0])

    #: And no module keeps the old key alive as a literal, in a body or at module level.
    assert [module.__name__ for module in facts_modules()
            if "course" in code_constants(module)] == []


def test_oq11_is_closed_and_p6_publishes_no_competing_sensitivity_record(p6_conn):
    """OQ11, CLOSED — D2, ratified 2026-08-21, on the question it asked: WHICH record is
    authoritative. The answer is P7's.

    P7's `ClassificationRecord`, keyed `(file_id, content_hash)`, is authoritative;
    `files.sensitivity_state` is its PROJECTION, written through P1's published
    `set_sensitivity_state`; and `Unreadable or unclassified` is a GATE OUTCOME, not a file
    fact — it never enters that column. P6 was the part that made the name count three
    (§3.11's universal fact, §8.2's file-record state, §8.4's handling class). After D2 it
    makes it one: P6 publishes no record, no table, no vocabulary and no writer.

    INVERTED on purpose, for the same reason as OQ4."""
    tables = {row[0] for row in p6_conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")}
    assert [name for name in tables
            if "sensitiv" in name.lower() or "classification" in name.lower()] == []

    published = {f"{module.__name__}.{name}" for module in facts_modules()
                 for name in vars(module)
                 if not name.startswith("_")
                 and ("sensitiv" in name.lower() or "classification" in name.lower())}
    assert published == set()

    #: P1's writer belongs to P7. P6 importing it would make the projection have two
    #: authors, which is precisely what D2 removed.
    assert [module.__name__ for module in facts_modules()
            if "set_sensitivity_state" in vars(module)] == []


def test_the_sensitivity_field_row_is_needs_joseph_c5_and_is_not_settled(p6_conn):
    """OQ11's RESIDUE, still open, held here by name so it cannot be lost.

    D2 did NOT settle whether P6 keeps a `sensitivity` / `sensitivity status` FIELD ROW
    beside P7's authoritative record. The evidence points three ways and that is exactly
    why it is Joseph's:

      * §3.12 names it in the design's own field list — "subject, purpose, target
        university, project, event, or sensitivity" — and §3.11 spells it
        `sensitivity status`;
      * P7's SPEC, Contract-in, says in bold "P6 must accept `sensitivity` as a
        first-class universal field" (§3.11) rather than a domain-scoped one;
      * round 1's F-2 found the field HAS NO PRODUCER — nothing in P6 would ever write it,
        so it would ship as a permanently empty column that a reader could mistake for
        "not sensitive".

    The instruction standing over all three is "Create no such row until asked." So this
    test pins TODAY'S state and SETTLES NOTHING. If the row stays, this test is where the
    decision lands: flipping it is one line here plus one row in Task 2's catalogue, and
    nothing else in P6 branches on the answer — which is what "held open" has to mean to
    be worth anything."""
    keys = {row.field_key for row in FIELD_ROWS}
    assert "sensitivity" not in keys
    assert "sensitivity_status" not in keys
    for field_key in ("sensitivity", "sensitivity_status"):
        with pytest.raises(FieldNotInCatalogue):
            get_field(p6_conn, field_key)
```

- [ ] **Step 2: Run the test and watch it fail**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_no_invention.py -q
```

Expected on a first run, before Tasks 1–24 are green: **collection error**,
`ModuleNotFoundError: No module named 'facts'`. Run in Wave E order — after Tasks 1–24 — the
expected first failure is
`test_every_module_level_collection_is_a_declared_closed_vocabulary`, listing any collection a
sibling task published that this file does not yet declare. **That failure is the guard working**,
and it is resolved by adding the name to `DECLARED_VOCABULARIES` with the task that owns it — never
by widening the rule to a shape or a length.

- [ ] **Step 3: There is no implementation step**

This task creates no source file. Its "implementation" is the twenty-one tests above holding
against the twenty-four tasks that ran before it. If a guard fails, the fix belongs to the module
that broke it:

| Failing guard | Where the fix goes |
|---|---|
| a module-level number | the producer that introduced it — make it a required keyword with no default, like every other Deferred row |
| a module-level compiled pattern | Task 12's injected `DatePatterns` |
| an undeclared collection | one line in `DECLARED_VOCABULARIES`, naming the task that owns it |
| a catalogue-01 producer string | Task 9 — it is injected at construction, never imported |
| a new module | the file layout is a contract; the module either belongs in it or does not exist |
| an import outside the five packages | the task that added it |
| `subsystem = "P6"` in two places | M8 — one author, one place |
| an open question that has been answered in code | the answer is Joseph's, not this plan's |
| a closed question whose guard did not invert | this file, and only after re-reading the ratified decision |

- [ ] **Step 4: Run it green, then the whole part, then the whole suite**

```bash
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6/test_p6_no_invention.py -q
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest tests/p6 -q
cd "/Users/jy/GRAPH AGENT" && python3 -m pytest -q
```

Expected: **21 passed** for this file; the whole part green; and the pre-existing **1302 tests**
still passing, because P6 touched no file outside `src/facts/` and `tests/p6/` (D5).

- [ ] **Step 5: Commit**

```bash
cd "/Users/jy/GRAPH AGENT" && git add tests/p6/test_p6_no_invention.py && \
git commit -m "feat(P6): the no-invention guard — six questions held open, two closures inverted, every constant checked at run time"
```

---

---

### Task 27: Deterministic operation, and the walking-skeleton P6 step

**Files:**
- Test: `tests/p6/test_p6_deterministic.py`, `tests/p6/test_p6_skeleton_step.py`
- Creates and modifies **no** source file. This is the only task in the plan of which that is true,
  and it is the reason the step list below is not the ordinary red-green shape. See *This task
  writes no source file* immediately after the interfaces.

**Interfaces:**
- Consumes: `facts.resolver.FactResolver`; `evidence_shape.fixtures.by_number`; `facts.rules` —
  `Rule`, `apply_rules`; `facts.dates` — `DatePatterns`, `date_candidates`; `facts.facets` —
  `fill_or_abstain`; `facts.file_facts` — `facts_for_file`, `FILE_FACTS_COLUMNS`,
  `FORBIDDEN_COLUMN_SUBSTRINGS`; `facts.unresolved.unresolved_for_file`;
  `database_agent.files_table` — `record_file`, `get_file`; `evidence_shape.store` —
  `record_run`, `record_observation`, `observations_for_file`; `evidence_shape.vocabulary` —
  `RELIABILITY_STATES`, `ZONES`, `SOURCE_TYPES`; `orchestrator` — read-only, for the D5 guard.
  **Not** `orchestrator.run_wave2`, and **not** the Task 26 wiring, which does not exist (D5).
- Produces: nothing.

**Done-means:** 17, and the end-to-end half of 4.

> **The `Consumes` line the skeleton wrote for this task named "the Task 26 wiring". That wiring is
> cut (D5) and there is nothing to consume.** The skeleton's step resolves facts **from stored
> evidence** — P4's `evidence` rows, already written — and does not run through `run_wave2` at any
> point. Nothing in either test file imports `orchestrator.run_wave2`, and one of the tests asserts
> that `facts` appears nowhere in the orchestrator's import graph. See *The integration a reader
> will reach for here* below, which is placed at the exact point a reader would otherwise reach for
> it.

---

**This task writes no source file, and that changes what its red step can be.**

Every other task in this plan writes a module, so its red is guaranteed: the module does not exist
and the import fails. This task writes two test files against code that Tasks 1–25 have already
landed. If those tasks were done correctly, both files pass on their first run — and **a
verification task that passes on its first run has proved nothing about itself.** It could be
asserting `True == True` in nine places and the run would look identical.

So the cycle here is inverted and made explicit, and it is a real red-green rather than a
formality:

1. **Step 2 runs the file and states the expected failure**, which is genuine at the moment this
   task is executed and is stated exactly.
2. **Step 5 is a teeth proof**: the deterministic assertion is re-run once with a model deliberately
   configured, and it is **required to fail**. Then the configuration is removed and it is required
   to pass. Nothing under `src/` is touched in either direction — the mutation is a keyword argument
   in the test's own helper, applied and reverted inside the step. A guard that cannot be made to
   fail on demand is not a guard, and Done-means 17 is the plan's largest single claim.

This is stated rather than smuggled because the brief forbids placeholders and a "run it, it passes"
step would be one wearing a checkbox.

---

**Done-means 17, verbatim, because two halves of it are two different test files:**

> The whole of items 4–10, 13–16 and 18–27 pass with P8 absent and no model configured — the Wave 2
> requirement and the walking skeleton's `P6 resolve it to ONE validated fact (course = X) with its
> evidence link`.

**And the trap inside it: "P8 absent" is trivially true and therefore worth nothing on its own.**
There is no P8 package anywhere in the repository. `importlib.util.find_spec` cannot find one. So
every test in `tests/p6/` already runs with P8 absent, in the same sense that they run with a Mars
lander absent, and asserting it that way would be a green tick over an empty claim. The three things
that are **not** trivial, and that this task asserts separately:

- **No deterministic producer takes a model parameter at all.** Asserted from `inspect.signature`
  over every fact-producing entry point, so it holds for every call rather than for the one call a
  behavioural test happens to make.
- **No deterministic producer can reach the P8 seam.** `facts.llm_seam` appears in no producer
  module's import graph — an AST walk, not a text search. §3.3 puts every model call in P8; a
  producer that could import the seam has a path to a proposal, and then Done-means 17 rests on that
  path not being *taken* rather than on it not *existing*.
- **`llm_supported` is reachable from exactly one module.** §3.5 is why: *"A file fact is not
  inherently rule-based or LLM-based. It is the common format into which both systems write their
  conclusions."* One format, one table, and the producer is a column — so the state is a **value**,
  and the only assertion available is about which module can supply it. Exactly one can, and it is
  the module P8 talks to.

**One thing that will look like a violation and is not.** Every deterministic producer calls
`facts.cache.fact_cache_key(..., model_identifier=None, prompt_fingerprint=None)` — §3.4's key has
five parts and two of them are the model's, so a deterministic fact records them as `None` rather
than omitting them. Those two names therefore appear in every producer's source as **keyword
argument names**. The AST guard below collects `ast.Name`, `ast.Attribute` and import names, and a
keyword argument is an `ast.keyword` with an `arg` attribute, so it is correctly not collected. The
signature guard is the one that binds: no producer *accepts* either name. Written out because a
reviewer who reaches for `grep model_identifier src/facts/` will get thirteen hits and conclude the
guard is broken.

---

**The walking-skeleton step, read from the file rather than remembered.** `planning/02-segmentation-map.md`
line 190, verified byte-exact on 2026-08-22:

```text
P6      resolve it to ONE validated fact (subject = X) with its evidence link  [D6]
```

**It says `subject`, and Done-means 17 above still says `course`.** D6 is ratified — *the academic
field key is `subject`, and every stored field key is `snake_case`* — and the segmentation map has
been reconciled to it while the SPEC's Done-means 17 sentence has not. Per the skeleton's own rule
(*"if you find a line that still contradicts one, that line is the error, not the decision"*), the
stored field key this test asserts is **`subject`**, and `course` survives only inside the quotation
above. This is not a judgement call this task is making: Done-means 4's own amendment already says
so — *"The stored field key is `subject` … The `fields` catalogue carries a `subject` row and no
`course` row."*

Three properties of that one line decide the test:

- **ONE fact.** Not two, not a fact plus a `possible` clue. Fixture 1 carries one observation, and
  the skeleton's claim is that one observation resolves to one fact.
- **`validated`, not `direct`.** §3.13 reserves `direct` for a value read out of a reliable explicit
  slot; a course code recovered from a heading and confirmed by a §3.5 context term is a
  deterministic rule that passed a contextual check, which is `validated`'s own definition. The
  skeleton line says the word.
- **"with its evidence link"** — the `evidence_refs[]` entry, and it must be fixture 1's
  `observation_key` exactly. M14: never an `observation_id`, never a row id.

**Fixture 1 is the walking-skeleton fixture and its context string is what makes the step possible
at all.** Verified live on 2026-08-22 by loading it rather than by reading a document:

```text
by_number(1).design_case  '§2.8 "page 1, heading 2"; §3.2's syllabus'
raw_value                 'BUSIB 4300'
zone                      'heading'
locator                   'heading:page=1/heading=2'
reliability               'possible'
occurrence_count          3
context_before            'Syllabus — '     capital S, U+2014 EM DASH, one space either side
context_after             ' — Spring 2026'
extractor_name            'pdf.text'        source_type 'text_document', analysis_tier 'native'
run.file_id               'file-01'         run.content_hash '042896dc…b95da'
```

`context_before` is `'Syllabus — '` with a **capital S**. §3.5's context check is
case-insensitive — that is N-6, and B8(a) put this string on the fixture for exactly this reason: a
case-sensitive check comparing against a lowercase term list refuses the skeleton's own fixture and
the walking skeleton has no P6 step at all. Task 10 owns `context_check` and its case-insensitivity;
this task asserts the **consequence**, which is that the byte-exact fixture resolves.

**Fixture 1's `file_id` is `'file-01'` and its `content_hash` is P4's, not P1's.** The fixtures are
P4-shaped test data, not rows P1 created. P1's `content_hash` is 64 lowercase hex characters with no
`sha256:` prefix and is computed by `record_file` over real bytes, and `ExtractionRun.__post_init__`
rejects any other shape. So the test writes a real `files` row first and rebinds the fixture's run
and observation onto it with `dataclasses.replace` — the observation is frozen, `replace` is the
supported move, and it was verified to work on both `Observation` and `ExtractionRun` on
2026-08-22. **The `raw_value`, the location, the context pair and the reliability are carried across
untouched**, which is the whole point: the test must resolve P4's fixture, not a convenient
paraphrase of it. Rebinding changes `observation_key`, because the key hashes `content_hash ·
extractor_name · locator · raw_value` — so the test reads the key off the rebound observation and
never off the original.

---

**§3.2, quoted in full, because Done-means 4 is one sentence of it and the rest is the reason:**

> Raw evidence is not yet a fact. For example, the filename Syllabus BUSIB 4300 Spring 2026.pdf, the PDF title BUSIB 4300 Syllabus, and a page-one heading Spring 2026 are observations. From those observations, the system can create facts such as subject = BUSIB 4300, term = Spring 2026, and work type = syllabus. Similarly, an EXIF field called DateTimeOriginal is raw metadata; capture date = 2026-07-17 is the file fact derived from it. This distinction matters because the product must preserve both the original evidence and the conclusion built from it. If a resolver later improves, the system can generate a better interpretation while retaining the original filename, heading, metadata field, text span, or OCR result that supported the earlier interpretation.

Three observations in, three facts out, and **the observations unchanged afterwards** — the last
clause is not decoration, it is rule 1 of this part. P4 makes the assertion unfalsifiable at the
database (`evidence_never_overwritten` and `evidence_no_delete` triggers on the `evidence` table),
so the test asserts the *intent* and the triggers guarantee it cannot be satisfied by accident.

The three field keys are `subject`, `term` and `work_type` — §3.11's Academic row, in D6's
`snake_case`. The design's prose spells the third *"work type"* with a space; a field key is a join
handle and two spellings are two columns, so the stored key is `work_type` and the space survives
inside the quotation.

---

**The integration a reader will reach for here, and why it must not be made.**

This is the task that resolves the walking skeleton end to end, so it is the exact point at which a
reader thinks: *P6 works now — wire `no_usable_facts_for` into `run_wave2` and delete the stub.*

**Do not.** The authoring brief states the consequence in one line and it is not a preference:

> **If P6's resolver is ever passed to `run_wave2` as `no_usable_facts`, the first text-bearing PDF
> ends the scan.**

The mechanism, so it is checkable rather than believed:

- Task 19 has `no_usable_facts_for(...)` raise `FactPassNotRun` when the verdict is asked about a
  `(file_id, content_hash)` whose deterministic pass has not been recorded. `FactPassNotRun`
  inherits `extractors.failure.ContractViolation`, and `orchestrator._extract_one` **re-raises
  `ContractViolation` by name** instead of converting it into a `failed` run. So it does not degrade
  one file; it propagates out of the loop.
- `extractors.ocr_policy.text_layer_state` consults `no_usable_facts` for **every text-bearing PDF**,
  inside the caller's single loop, during extraction — before any deterministic pass could have run
  for that content hash. Worse than early: `document_ocr_decision` is called inside `extract()` on
  the freshly-built `ExtractionResult`, and `_write(sink, result, …)` does not run until
  `orchestrator.py:211`, so the observations P6 would reason about have not reached P4 at all.
- Reordering that loop was Task 26. **Task 26 is cut (D5)**, so nothing reorders it.

Therefore the caller keeps passing `orchestrator.TARGETED_OCR_UNAVAILABLE`, which is **kept, not
deleted** — round 5's simplification, recorded in the Task 26 cut note. P6 publishes
`no_usable_facts_for` as a read surface **its own tests exercise**, and wiring it is the four-pass
work, owed separately. One of the tests below asserts the negative directly: `facts` appears nowhere
in `orchestrator`'s imports, and `run_wave2`'s `no_usable_facts` parameter still has no default, so
nothing can acquire P6 by omission.

---

**The one declaration this task makes, and why it is made here.**

Task 27 is the only task that drives a producer chain end to end, so it is the first place several
sibling tasks' injected dataclasses are **constructed** rather than described. Three of them
(`DirectSlots`, `ActivationSignals`, `SessionBoundary`) are **not** constructed here — the tests
below reach them only through `inspect.signature`, never by instantiating them — so this task fixes
no field name of theirs.

One is constructed, and its field name is declared here because it cannot be avoided:

> **`DatePatterns(patterns: Mapping[str, re.Pattern[str]])`** — one field, `patterns`, keyed by
> **pattern id**. Task 12 already publishes `parse_exact(raw, *, pattern_id) -> str`, so pattern ids
> exist and are the handle; a mapping from id to compiled pattern is the smallest shape that
> supports it. The three ids §3.10 requires are `season_year` (`Spring 2025`), `academic_year`
> (`AY 2024-25`) and `named_term` (`Michaelmas Term 2024`). **Task 12 owns the contents and this
> task owns none of them** — the test injects its own patterns under those ids and asserts nothing
> about what Task 12's catalogue holds.
>
> If Task 12 lands a different field name, this task's `test_the_three_facts_of_the_designs_own_example`
> fails at construction — loudly, at integration, which is the correct behaviour for a contract and
> the reason it is written down rather than guessed at silently.

---

- [ ] **Step 1: Write `tests/p6/test_p6_deterministic.py`**

```python
# tests/p6/test_p6_deterministic.py
"""Done-means 17 -- every fact-producing path, with P8 absent and no model configured.

`02-segmentation-map.md`'s Wave 2 line is `P4 -> P5 -> P6  (deterministic only, no
model)`. This file is the assertion that the parenthesis is a property of the code
rather than of the diagram.

**"P8 absent" is trivially true and therefore worth nothing on its own.** There is no
P8 package in this repository, so every test in `tests/p6/` already runs with P8
absent in the same sense that it runs without a Mars lander. The three non-trivial
claims are asserted separately below: no deterministic producer TAKES a model
parameter, no deterministic producer can REACH the P8 seam, and `llm_supported` is
supplied by exactly one module.

**One thing that looks like a violation and is not.** §3.4's cache key has five parts
and two are the model's, so every deterministic producer calls `fact_cache_key(...,
model_identifier=None, prompt_fingerprint=None)` and those two names appear in every
producer's source. They appear as `ast.keyword` argument names, which the AST guard
below does not collect, and the signature guard is the one that binds: no producer
ACCEPTS either name.
"""
from __future__ import annotations

import ast
import importlib
import importlib.util
import inspect
import os
import subprocess
import sys
from pathlib import Path

import pytest

from evidence_shape.vocabulary import RELIABILITY_STATES

from facts.resolver import FactResolver
from facts.states import LLM_SUPPORTED

TEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = TEST_DIR.parents[1]

#: Set in the child run so the recursive test skips itself. Everything else in this
#: file is cheap and runs in both.
CHILD_MARKER = "P6_DETERMINISTIC_SUITE_CHILD"

#: The state no deterministic path may reach. Task 1 owns the spelling.

#: Every fact-producing entry point in `facts`, module and function. This is the
#: plan's task list read off -- Tasks 8-16, 18 and 19 publish exactly these. It is
#: written out rather than discovered because a producer added later without being
#: added here would be exempt from both guards; `test_the_producer_list_is_the_whole_
#: of_facts` is the guard on that.
PRODUCERS = (
    ("facts.direct", "direct_facts"),
    ("facts.discount", "discount"),
    ("facts.rules", "apply_rules"),
    ("facts.facets", "fill_or_abstain"),
    ("facts.dates", "date_candidates"),
    ("facts.domains", "active_domains"),
    ("facts.families", "duplicate_family"),
    ("facts.families", "version_family"),
    ("facts.session", "bounded_sessions"),
    ("facts.photo_event", "photo_events"),
    ("facts.photo_event", "media_type"),
    ("facts.supersede", "supersede_fact"),
    ("facts.usable", "no_usable_facts_for"),
)

#: Modules in `facts` that are not producers: the tables, the vocabularies, the
#: reads, the seam, and the sequencer. Every name in `File Structure` is in exactly
#: one of these two lists.
NON_PRODUCERS = frozenset({
    "authorship", "budgets", "cache", "evidence", "fields", "file_facts",
    "learning", "llm_seam", "plan_versions", "read_surface", "resolver", "schema",
    "states", "stage_output", "unresolved", "values", "vocabulary",
})

#: The four names that would carry a model into a deterministic producer.
MODEL_PARAMETERS = ("propose", "validate", "model_identifier", "prompt_fingerprint")


def _facts_dir() -> Path:
    return Path(inspect.getfile(importlib.import_module("facts"))).resolve().parent


def _mentioned_names(module) -> set[str]:
    """Every name this module's CODE mentions.

    An AST walk, never a text search: a text search matches comments and docstrings,
    and a guard that does that has broken three tasks on this project already
    (P5 PLAN, Task 20). Keyword ARGUMENT names are deliberately not collected -- see
    the module docstring.
    """
    tree = ast.parse(inspect.getsource(module))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module or "")
            names.update(alias.name for alias in node.names)
    return names


def test_no_deterministic_producer_takes_a_model_parameter():
    # "no model configured", proved from the SIGNATURES rather than from one call.
    # A producer that accepted `propose` would be a fact path a caller could turn
    # into a model path without P8 existing, which §3.3 forbids outright.
    offences = []
    for module_name, function_name in PRODUCERS:
        module = importlib.import_module(module_name)
        parameters = inspect.signature(getattr(module, function_name)).parameters
        for name in MODEL_PARAMETERS:
            if name in parameters:
                offences.append(f"{module_name}.{function_name}({name}=...)")
    assert offences == []


def test_no_deterministic_producer_reaches_the_p8_seam():
    # §3.3: every model call is P8's. A producer that can IMPORT the seam has a path
    # to a proposal, and Done-means 17 would then rest on that path not being taken
    # rather than on it not existing.
    for module_name in sorted({name for name, _ in PRODUCERS}):
        mentioned = _mentioned_names(importlib.import_module(module_name))
        assert "facts.llm_seam" not in mentioned, module_name
        assert "llm_seam" not in mentioned, module_name


def test_only_one_module_can_supply_the_llm_supported_state():
    # §3.5: "A file fact is not inherently rule-based or LLM-based. It is the common
    # format into which both systems write their conclusions." One format, one table,
    # and the producer is a COLUMN -- so `llm_supported` is a value, and the only
    # assertion available is about which module can supply it.
    reaching: set[str] = set()
    for path in sorted(_facts_dir().glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value == LLM_SUPPORTED:
                reaching.add(path.stem)
            if (isinstance(node, ast.Subscript)
                    and isinstance(node.value, ast.Name)
                    and node.value.id in {"RELIABILITY_STATES", "STATES"}):
                reaching.add(path.stem)
    # `states` publishes the six once (Task 1); `llm_seam` is the module P8 talks to.
    assert reaching <= {"states", "llm_seam"}


def test_the_producer_list_is_the_whole_of_facts():
    # A guard on the two guards above: a producer module added to `src/facts/`
    # without being added to PRODUCERS would be exempt from both, silently.
    modules = {path.stem for path in _facts_dir().glob("*.py")} - {"__init__"}
    assert modules - NON_PRODUCERS == {name.split(".")[1] for name, _ in PRODUCERS}
    assert not (NON_PRODUCERS & {name.split(".")[1] for name, _ in PRODUCERS})


def test_an_absent_p8_is_an_explicit_none_and_never_an_omitted_argument():
    # Skeleton rule 4: every threshold and every injected surface is a required
    # keyword with no default. P8's two are where a default would be most tempting
    # and most wrong -- a defaulted `propose` is a model path nobody chose to enable.
    parameters = inspect.signature(FactResolver.__init__).parameters
    for name, parameter in parameters.items():
        if name == "self":
            continue
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, name
        assert parameter.default is inspect.Parameter.empty, name
        assert parameter.default is not None, name
    for name in ("propose", "validate"):
        assert name in parameters


@pytest.mark.skipif(os.environ.get(CHILD_MARKER) == "1",
                    reason="this IS the child run; the parent asserts on its exit code")
def test_the_whole_p6_suite_passes_with_p8_absent_and_no_model_configured():
    # Done-means 17 in its own words: "The whole of items 4-10, 13-16 and 18-27 pass
    # with P8 absent and no model configured." The only honest way to assert "the
    # whole suite" is to run the whole suite, so it is run -- in a child process, with
    # a marker that stops this one test from recursing.
    assert importlib.util.find_spec("p8") is None
    assert importlib.util.find_spec("llm_harness") is None
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", str(TEST_DIR), "-q",
         "-p", "no:cacheprovider"],
        cwd=REPO_ROOT, env=dict(os.environ, **{CHILD_MARKER: "1"}),
        capture_output=True, text=True, timeout=900, check=False)
    assert completed.returncode == 0, completed.stdout[-4000:]
    assert " failed" not in completed.stdout
```

- [ ] **Step 2: Run it, and state the failure**

Run: `pytest tests/p6/test_p6_deterministic.py -v`

Expected: **FAIL** — `ModuleNotFoundError: No module named 'facts.resolver'` at collection, if this
task is run before Task 20 has landed. Task 20 is in Wave D and this task is in Wave E, so the
ordinary case is that it has landed, and then the expected failure is the one this task exists to
catch: an `AssertionError` from `test_no_deterministic_producer_takes_a_model_parameter` or from
`test_the_producer_list_is_the_whole_of_facts`, naming the producer that got it wrong.

**Neither failure is guaranteed, and Step 5 is where the guarantee comes from.** If all six tests
pass on the first run, that is the good outcome and it is still unproven until Step 5 makes the
central one fail on demand.

- [ ] **Step 3: Write `tests/p6/test_p6_skeleton_step.py`**

```python
# tests/p6/test_p6_skeleton_step.py
"""The walking skeleton's P6 step, and Done-means 4 end to end.

`planning/02-segmentation-map.md`, line 190, verbatim:

    P6      resolve it to ONE validated fact (subject = X) with its evidence link  [D6]

and §3.2's own three-observation example, which is the same step run over the whole of
the design's case rather than over one observation.

**This does not go through `run_wave2`.** Task 26 is cut (D5): the step resolves facts
from evidence P4 has already stored, and `facts` is wired into no caller. The last two
tests assert that negative directly, because this file is the exact place a reader
decides P6 is ready to be wired in. It is not, and the reason is in the plan above
this test: `ocr_policy.text_layer_state` consults `no_usable_facts` for every
text-bearing PDF before any deterministic pass has run, and Task 19's `FactPassNotRun`
is a `ContractViolation`, so the first text-bearing PDF would end the scan.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect
import json
import re
from pathlib import Path

import pytest

import orchestrator

from database_agent.files_table import get_file, record_file

from evidence_shape.fixtures import by_number
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import observations_for_file, record_observation, record_run

from facts.dates import DatePatterns, date_candidates
from facts.facets import fill_or_abstain
from facts.file_facts import FORBIDDEN_COLUMN_SUBSTRINGS, facts_for_file
from facts.rules import Rule, apply_rules
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-19T14:00:00+00:00"

#: §3.11's Academic row in D6's snake_case. §3.2 spells the third "work type" with a
#: space; a field key is a join handle and two spellings are two columns.
SUBJECT, TERM, WORK_TYPE = "subject", "term", "work_type"

#: The rules the TEST injects. §3.5 states that a course-code-shaped string needs an
#: academic context term; it states no pattern and no term list, and Task 10 takes
#: both as injected `Rule`s for that reason. The terms are lowercase on purpose: the
#: context check is case-insensitive (N-6) and fixture 1's context is capital-S
#: "Syllabus -- ", so a case-sensitive check would refuse the skeleton's own fixture.
SUBJECT_RULE = Rule(pattern=re.compile(r"\b[A-Z]{4,6}\s\d{4}\b"),
                    required_context_terms=("syllabus", "course", "term"),
                    field_key=SUBJECT)
WORK_TYPE_RULE = Rule(pattern=re.compile(r"\b[Ss]yllabus\b"),
                      required_context_terms=("syllabus",),
                      field_key=WORK_TYPE)

#: §3.10's three named academic-term patterns, under the pattern ids Task 12's
#: `parse_exact(raw, *, pattern_id)` addresses them by. The TEST supplies these; the
#: catalogue Task 12 ships is its own and nothing here asserts anything about it.
PATTERNS = DatePatterns(patterns={
    "season_year": re.compile(r"\b(Spring|Summer|Autumn|Fall|Winter)\s(\d{4})\b"),
    "academic_year": re.compile(r"\bAY\s(\d{4})-(\d{2})\b"),
    "named_term": re.compile(r"\b(Michaelmas|Hilary|Trinity)\sTerm\s(\d{4})\b"),
})

#: §3.7's weights and thresholds are Deferred. Every number below is the TEST's.
ZONE_WEIGHT = {zone: 1.0 for zone in
               ("filename", "path", "metadata", "title", "heading", "body", "table",
                "header_footer", "notes", "link", "annotation", "reference_list",
                "manifest", "ocr", "transcript")}
ZONE_WEIGHT.update({"title": 5.0, "filename": 4.0, "heading": 3.0})
MINIMUM_SCORE, MINIMUM_MARGIN = 1.0, 0.5


def _p1_row(conn, tmp_path, *, name, body):
    """A real P1 `files` row over real bytes, so the content hash is P1's own.

    P1's hash is 64 lowercase hex characters with no `sha256:` prefix and
    `ExtractionRun.__post_init__` rejects any other shape, so the fixture's own
    `content_hash` cannot be reused against a P1 database.
    """
    path = tmp_path / name
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _rebind(fixture, *, file_id, content_hash):
    """P4's fixture, moved onto a P1 row, with everything else carried across.

    `Observation` and `ExtractionRun` are frozen dataclasses and `dataclasses.replace`
    is the supported move (verified by execution, 2026-08-22). The raw value, the
    location, the context pair and the reliability come across untouched: the point is
    to resolve P4's fixture, not a convenient paraphrase of it.
    """
    run = dataclasses.replace(fixture.run, file_id=file_id,
                              content_hash=content_hash)
    observations = tuple(
        dataclasses.replace(one, file_id=file_id, content_hash=content_hash,
                            run_id=run.run_id)
        for one in fixture.observations)
    return run, observations


def _observe(conn, *, run_id, file_id, content_hash, raw, zone, label,
             extractor="pdf.text", context_before=None, context_after=None):
    """One ordinary P4-shaped observation, for §3.2's three-observation case."""
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=run_id, context_before=context_before, context_after=context_after)
    record_observation(conn, observation)
    return observation


@pytest.fixture()
def skeleton(p6_conn, tmp_path):
    """Fixture 1 -- the walking-skeleton fixture -- on a real P1 row."""
    fixture = by_number(1)
    file_id, content_hash = _p1_row(
        p6_conn, tmp_path, name="Syllabus BUSIB 4300 Spring 2026.pdf",
        body=b"one PDF whose title carries a course code")
    run, observations = _rebind(fixture, file_id=file_id,
                                content_hash=content_hash)
    record_run(p6_conn, run)
    for observation in observations:
        record_observation(p6_conn, observation)
    return file_id, content_hash, observations[0]


def test_fixture_one_resolves_to_one_validated_fact_with_its_evidence_link(
        skeleton, p6_conn):
    # The segmentation map's P6 step, whole: "resolve it to ONE validated fact
    # (subject = X) with its evidence link".
    file_id, content_hash, observation = skeleton
    written = apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                          rules=(SUBJECT_RULE,))
    assert len(written) == 1                                       # ONE fact
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert len(rows) == 1
    row = rows[0]
    assert row["field_key"] == SUBJECT                             # subject = X (D6)
    assert row["canonical_value"] == "BUSIB 4300"
    assert row["reliability_state"] == "validated"                 # validated
    assert json.loads(row["evidence_refs"]) == [observation.observation_key]
    assert observation.observation_key.startswith("sha256:")       # M14, its link


def test_the_step_is_named_in_the_segmentation_map_in_these_words(skeleton, p6_conn):
    # The step is read from the file, not remembered. D6 rewrote `course = X` to
    # `subject = X` there; Done-means 17's sentence still says `course`, and the
    # skeleton's own rule is that the unreconciled line is the error, not the
    # decision.
    repo_root = Path(__file__).resolve().parents[2]
    text = (repo_root / "planning" / "02-segmentation-map.md").read_text(
        encoding="utf-8")
    assert "resolve it to ONE validated fact (subject = X) with its evidence link" \
        in text
    assert "(course = X)" not in text


def test_the_context_that_makes_it_resolvable_is_byte_exact(skeleton):
    # B8(a) put this string on fixture 1 so the skeleton's one fact is resolvable at
    # all, and N-6 is why it is capital-S: §3.5's context check is case-insensitive,
    # and a case-sensitive one comparing against a lowercase term list refuses the
    # walking skeleton's own fixture.
    _, _, observation = skeleton
    assert observation.context_before == "Syllabus — "        # U+2014 EM DASH
    assert observation.context_after == " — Spring 2026"
    assert observation.raw_value == "BUSIB 4300"
    assert observation.location.zone == "heading"
    assert observation.reliability == "possible"                   # a fact is not
    assert observation.occurrence_count == 3
    assert all(term.islower() for term in SUBJECT_RULE.required_context_terms)


def test_a_course_code_with_no_academic_context_produces_no_fact(p6_conn, tmp_path):
    # The negative half of the same rule, and the reason the positive half is not an
    # accident: the identical string in the identical zone, with the context removed.
    file_id, content_hash = _p1_row(p6_conn, tmp_path, name="unlabelled.pdf",
                                    body=b"a heading and nothing around it")
    _observe(p6_conn, run_id="bare", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", zone="heading", label="heading:page=1/heading=2")
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(SUBJECT_RULE,)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key=SUBJECT)
    assert [row["reason"] for row in rows] == ["context_check_failed"]


def test_the_three_facts_of_the_designs_own_example(p6_conn, tmp_path):
    # Done-means 4, end to end: "the filename Syllabus BUSIB 4300 Spring 2026.pdf, the
    # PDF title BUSIB 4300 Syllabus, and a page-one heading Spring 2026 are
    # observations. From those observations, the system can create facts such as
    # subject = BUSIB 4300, term = Spring 2026, and work type = syllabus."
    file_id, content_hash = _p1_row(
        p6_conn, tmp_path, name="Syllabus BUSIB 4300 Spring 2026.pdf",
        body=b"the design's own example")
    name = _observe(p6_conn, run_id="fn", file_id=file_id,
                    content_hash=content_hash,
                    raw="Syllabus BUSIB 4300 Spring 2026.pdf", zone="filename",
                    label="filename", extractor="filesystem.name")
    title = _observe(p6_conn, run_id="ti", file_id=file_id,
                     content_hash=content_hash, raw="BUSIB 4300 Syllabus",
                     zone="title", label="title",
                     context_before="Title: ", context_after=" (syllabus)")
    heading = _observe(p6_conn, run_id="hd", file_id=file_id,
                       content_hash=content_hash, raw="Spring 2026", zone="heading",
                       label="heading:page=1/heading=1",
                       context_before="Syllabus — ", context_after="")

    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(SUBJECT_RULE, WORK_TYPE_RULE))
    candidates = tuple(candidate
                       for observation in (name, title, heading)
                       for candidate in date_candidates(observation,
                                                        patterns=PATTERNS))
    fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key=TERM, candidates=candidates,
                    minimum_score=MINIMUM_SCORE, minimum_margin=MINIMUM_MARGIN)

    rows = {row["field_key"]: row
            for row in facts_for_file(p6_conn, file_id, content_hash)}
    assert set(rows) == {SUBJECT, TERM, WORK_TYPE}                 # exactly three
    assert rows[SUBJECT]["canonical_value"] == "BUSIB 4300"
    assert rows[TERM]["canonical_value"] == "Spring 2026"
    assert rows[WORK_TYPE]["canonical_value"] == "syllabus"
    for row in rows.values():
        refs = json.loads(row["evidence_refs"])
        assert refs and all(ref.startswith("sha256:") for ref in refs)


def test_every_observation_is_unchanged_after_resolution(p6_conn, tmp_path):
    # §3.2: "the product must preserve both the original evidence and the conclusion
    # built from it." P4 makes this unfalsifiable at the database -- the `evidence`
    # table carries `evidence_never_overwritten` and `evidence_no_delete` triggers --
    # so this asserts the INTENT and the triggers guarantee it cannot pass by
    # accident.
    file_id, content_hash = _p1_row(p6_conn, tmp_path, name="unchanged.pdf",
                                    body=b"evidence outlives the conclusion")
    original = _observe(p6_conn, run_id="u", file_id=file_id,
                        content_hash=content_hash, raw="BUSIB 4300", zone="heading",
                        label="heading:page=1/heading=2",
                        context_before="Syllabus — ", context_after="")
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(SUBJECT_RULE,))
    after = [one for one in observations_for_file(p6_conn, file_id)
             if one.observation_key == original.observation_key]
    assert len(after) == 1
    assert after[0].raw_value == "BUSIB 4300"
    assert after[0].context_before == "Syllabus — "
    assert after[0].reliability == "possible"
    assert after[0].extractor_version == "1.0.0"


def test_the_resolved_fact_carries_no_path_destination_folder_or_group(
        skeleton, p6_conn):
    # §3.14: "A fact such as subject = BUSIB 4300 does not itself dictate one
    # permanent folder path." Task 4 asserts this of the SCHEMA; this asserts it of a
    # row the walking skeleton actually produced, which is where a reviewer looks.
    file_id, content_hash, _ = skeleton
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(SUBJECT_RULE,))
    row = facts_for_file(p6_conn, file_id, content_hash)[0]
    for column in row.keys():
        assert not [bad for bad in FORBIDDEN_COLUMN_SUBSTRINGS
                    if bad in column.lower()], column


def test_p6_is_not_wired_into_the_wave_2_caller():
    # D5 cut Task 26, and this is the point in the plan where a reader decides P6 is
    # ready to be wired in. It is not. `ocr_policy.text_layer_state` consults
    # `no_usable_facts` for every text-bearing PDF before any deterministic pass has
    # run, and Task 19's `FactPassNotRun` is a `ContractViolation` that
    # `orchestrator._extract_one` re-raises by name -- so passing P6's resolver ends
    # the scan on the first text-bearing PDF.
    tree = ast.parse(inspect.getsource(orchestrator))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert not [name for name in imported if name.split(".")[0] == "facts"]
    # The stub is KEPT, not deleted -- round 5's simplification, in the Task 26 cut
    # note. And nothing can acquire P6 by omission: the parameter has no default.
    assert callable(orchestrator.TARGETED_OCR_UNAVAILABLE)
    parameter = inspect.signature(orchestrator.run_wave2).parameters[
        "no_usable_facts"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty


def test_this_step_never_runs_through_run_wave2():
    # The other half of the same negative, from this test module's own imports: the
    # skeleton's P6 step resolves from STORED evidence. `orchestrator` is imported
    # here read-only, for the guard above, and `run_wave2` is not imported at all.
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported_names.update(f"{node.module}.{alias.name}"
                                  for alias in node.names)
    assert "orchestrator.run_wave2" not in imported_names
    assert not [name for name in imported_names
                if name.startswith("extractors.")]
```

- [ ] **Step 4: Run it, and state the failure**

Run: `pytest tests/p6/test_p6_skeleton_step.py -v`

Expected: **FAIL**. The certain failure is at collection —
`ImportError: cannot import name 'DatePatterns' from 'facts.dates'` if Task 12 named its injected
dataclass differently, which is the contract this task declared above and the reason it declared it
in writing. Absent that, the expected failure is
`test_the_three_facts_of_the_designs_own_example` with `AssertionError: set(rows) == {subject, term,
work_type}` — the design's example is the plan's hardest single end-to-end claim and it is the one
most likely to be short by one field.

- [ ] **Step 5: Prove the deterministic guard has teeth**

The point of Step 5, restated once so nobody skips it: Steps 2 and 4 expect failures that are
*likely*, not *guaranteed*. This step produces a **guaranteed** failure and then removes it, so
Done-means 17's central assertion is known to be capable of failing.

Temporarily add this producer to `PRODUCERS` in `tests/p6/test_p6_deterministic.py`:

```python
    ("facts.llm_seam", "apply_verdict"),
```

Run: `pytest tests/p6/test_p6_deterministic.py::test_no_deterministic_producer_takes_a_model_parameter -v`

Expected: **FAIL** — `AssertionError: assert ['facts.llm_seam.apply_verdict(propose=...)'] == []`,
or the same failure naming whichever of the four model parameters `apply_verdict` carries. The seam
is the one module that legitimately takes them, so adding it to the deterministic list must break
the guard; if the guard stays green with the seam in the list, it is asserting nothing and Task 27
has not been done.

Then **revert that one line** and run the file again:

Run: `pytest tests/p6/test_p6_deterministic.py -v`
Expected: **PASS**

Nothing under `src/` is edited in either direction.

- [ ] **Step 6: Run both files and the whole part**

Run: `pytest tests/p6/test_p6_deterministic.py tests/p6/test_p6_skeleton_step.py -v`
Expected: PASS — 6 passed, 9 passed

Run: `pytest tests/p6 -q`
Expected: PASS — the whole part, and
`test_the_whole_p6_suite_passes_with_p8_absent_and_no_model_configured` runs it a second time in a
child process with `P6_DETERMINISTIC_SUITE_CHILD=1` set, where that one test skips itself.

Run: `pytest -q`
Expected: PASS — 1302 tests plus P6's, and **no P1–P5 test changes status**, which is Done-means
17's silent half: this part touches no file outside `src/facts/` and `tests/p6/` (D5), so a
regression anywhere else is this plan having broken its own boundary.

- [ ] **Step 7: Commit**

```bash
git add tests/p6/test_p6_deterministic.py tests/p6/test_p6_skeleton_step.py
git commit -m "test(P6): deterministic operation with P8 absent, and the walking-skeleton step from stored evidence"
```

---

---

# Appendix — what the section authors reported rather than resolved

Each section closed by naming its own contradictions instead of silently resolving them. That is the
mechanism that found this project's defects, so the reports are kept **verbatim**, grouped by the
section that made them. **They are dated, and they are not all still true** — several were closed by
rulings made after they were written. Read the preamble first; it wins.

`PLAN-tasks-07-09.md`'s appendix covers Tasks 7, 8 **and** 9, though only Task 7 came from that file.
Its Task 8/9 rows are kept because they are evidence about the **tasks**, not about the file — but
the tasks themselves come from `PLAN-tasks-08-09.md`, whose own appendix follows.

## What in here is no longer true

**The Tasks 7–9 section's item 2 is OVERRULED and must not be followed.** It recommends addressing
the six reliability states **by index** into P4's tuple. Brief §11 ruled the opposite: **Task 1
publishes one named constant per state and every other module imports it** — never a bare string,
never an index, because an index silently couples every consumer to the tuple's order. The *problem*
item 2 identifies is real and was fixed; the *recommendation* it makes is not the fix. The same rule
now extends to `FACT_ORIGINS`, `ATTEMPTED_PRODUCERS` and `UNRESOLVED_REASONS` (preamble §3.1).

**Every "the cache-key rule is written out per module" apology is closed.** One helper in
`facts.cache` — Task 6's — keyed per **(file version, deterministic pass)**, and every producer
imports it. Three of the four section front matters carried the *losing* rule (keying on the
observations a fact cites); the preamble carries the winner and the abstention argument that decides
it. Counts of "five copies" or "seven copies" are historical.

**`field_id` no longer exists.** The column is `field_key` and it is `fields`' PRIMARY KEY. Any row
below discussing the two-name collision is describing a defect that has been fixed — including the
one where Task 2 carried **both** columns holding the identical string.

**`destination_eligible` is TRUE for `target_school` and `client`** (D9), and the academic key is
`subject` with no `course` row (D6). Rows asserting all four §3.8 role fields are ineligible are
stale.

**Still open, and still exactly as reported:** the A04 adversarial fixture contradicts Done-means 22
(it is worded as the suppression tier and carries the demotion tier's expected outcome), and
catalogue 01's 115 entries still have no compiler — the working matcher one section wrote belongs
with the loader, not in `src/facts/`.

---

# Reported by the Tasks 5–6 section


## Contract ambiguities these two tasks hit and did not resolve

Five, reported rather than patched, because each one belongs to a file another author owns.

1. ~~**`get_field(conn, field_key)` must return a `field_id`.**~~ **RESOLVED by brief §17 exactly as
   this author predicted.** The reasoning was right and the prediction was right: *"if Task 2's
   catalogue keys on `field_key` alone, that one line and Task 4's equivalent change together."*
   Task 2's catalogue now keys on `field_key` alone — its first draft carried BOTH `field_id` and
   `field_key` holding the identical string, and that second column is deleted. So `values`,
   `file_facts` and `unresolved` all carry `field_key`, `get_field(...)["field_key"]` is what the
   one-line helper reads, and `PLAN-tasks-16-19.md`'s `old["field_id"]` is corrected with them.
   The column exists in all of them under one name, which is the "in both tables or in neither"
   this item asked for.
2. **One design sentence, two cache-key functions.** §3.4 describes one key; the built system has
   `extractors.runs.cache_key` and `facts.cache.fact_cache_key`, because P4's observation/fact split
   gave the sentence two subjects after §3.4 was written. Task 6's test pins them apart rather than
   reconciling them. Reconciling them would be a P4/P5/P6 seam change.
3. **The cross-table supersede back-pointer does not exist and cannot, through P1's surface.**
   `mark_superseded(conn, table, *, old_id, new_id, reason)` takes **one** table, so superseding an
   `unresolved` row with a `file_facts` row records `superseded_by` on the abstention and leaves
   `file_facts.supersedes` as `None` — verified by execution, silently, with no error raised. Task 5
   asserts the half that Done-means 19 and SPEC rule 3 require. Whether the fact should also point
   back at the refusal it replaced is `facts/supersede.py`'s question (Task 23).
4. **A fabricated quotation lives in P6's SPEC and in the skeleton, and is not repaired here.**
   Both attribute to §8.6 the sentence *"visible as deferred, never as 'understood and found
   unimportant'"*. The design contains no such sentence. Its actual words, grepped: *"If the budget
   is exhausted, the product should retain extracted evidence, mark the deferred stage, and leave the
   file or group in review rather than guessing"*, *"Cost exhaustion must never turn into
   lower-quality automatic classification"*, *"The user interface should show the difference between
   completed work and deferred work"*, and *"avoids the false impression that an unprocessed file was
   understood and found unimportant"*. The paraphrase is faithful in substance, which is why it
   spread; it is still not a quotation. These two tasks quote the design's words instead. **The SPEC
   and `PLAN-SKELETON.md` still carry it** — they are not this author's files, and the same phrase
   should be expected in the other P6 and P7 task documents written against the same skeleton.

5. **The multi-observation reconciliation is stated in five places and owned by none.** A fact built
   from several observations has several extractor versions and several analysis tiers;
   `PLAN-tasks-07-09.md` and `PLAN-tasks-14-15.md` both state the same collapse rule
   (`extractor_version` = `canonical_json` of the sorted distinct `[name, version]` pairs;
   `analysis_tier` = the last tier present in `ANALYSIS_TIERS` order) and both flag that it belongs
   in `facts.cache`. **Task 6 deliberately does not build it.** Its `Interfaces:` block publishes
   three names and a collapse helper is not one of them, and adding a fourth would change a contract
   four parallel authors are already writing against. It is the resolver's (Task 24) or a follow-up
   to this task, and the decision needs the lead rather than an author working alone.

---

# Reported by the Tasks 7–9 section


## Contract additions — names these three tasks publish beyond the skeleton's blocks

The skeleton's `Interfaces:` blocks are a contract with the authors writing Tasks 1–6, 10–13 and
14–27 in parallel. **No name in any of those blocks changed.** Six names are *added*, each because
the skeleton's own `Consumes:` line or `Produces:` type demanded something it did not name. They are
listed here so a parallel author sees them without reading the code.

| Task | Added | Why it had to exist |
|---|---|---|
| 7 | `UnknownRun` | `analysis_tier_for_observation` must fail rather than guess: an inferred tier lands in §3.4's cache key, and a wrong cache key is a fact that never invalidates |
| 8 | `DirectSlot` | `DirectSlots` is "a frozen dataclass of slot-name predicates"; a dataclass of things needs the thing |
| 8 | `SLOT_KINDS` | §3.5's four names, read off `dataclasses.fields(DirectSlots)` so there is no second spelling of them |
| 9 | `DISCOUNT_OUTCOMES` | `discount()` returns one of three literals; publishing the tuple stops every caller re-spelling them |
| 9 | `may_populate` | The demotion tier is a routing rule other producers must consult; a rule with no way to ask it is a comment |
| 9 | `suppress_tool_metadata` | The skeleton gives Task 9 `write_unresolved` in `Consumes:` and no writer to use it in. This is the pre-ranking gate and the suppression tier's only write |

**Task 9 writes no fact.** Its `Consumes:` block names `write_unresolved` and not `write_fact`, and
that is read as deliberate: the demotion tier decides *which field a value may fill*, and the fact
write belongs to whichever producer fills it. `tests/p6/test_p6_discount.py` drives `write_fact`
itself to prove Done-means 22's second half end to end.

---

## Contract ambiguities and conflicts found

Reported, not unilaterally resolved. Each was checked against the source or by execution on
2026-08-22.

**1 (carried, now worse). The §3.4 cache-key reconciliation has no owner and now appears five
times.** §3.4 names one extractor version and one analysis tier; a fact citing several observations
has several of each. `PLAN-tasks-14-15.md` wrote the rule out three times with a note; Tasks 8 and 9
make five. It belongs in `facts.cache` (Task 6) as
`fact_cache_key_for(conn, *, content_hash, observations)`. Five copies of a rule is four chances for
one of them to drift.

**2 (HIGH, unresolved by anyone). `PLAN-tasks-14-15.md` spells reliability states as string literals,
which Task 1's guard forbids.** `families.py` in that document contains
`reliability_state="direct"` and `reliability_state="possible"`. Task 1's stated proof is *"the
absence of any string literal spelling a state name anywhere else in `facts`"* — a guard the sibling
plan's code fails on its face. Tasks 8 and 9 here address the six states **by index** into
`facts.states.STATES` (`STATES[1]` is `direct`, `STATES[4]` is `possible`, in §3.13's published
order) so the spelling stays in one module. **Either the sibling's literals change or Task 1's guard
does; they cannot both stand.** Recommendation: index, because §3.13's order is contract and P4's
tuple is the one copy.

**3 (HIGH, F5, unchanged). A04 as built asserts the demotion tier for values that are the suppression
tier.** `tests/eval/fixtures/adversarial/A04.json` names `python-docx`, `Mozilla/5.0` and browser
producer strings and carries `expected_outcome_kind: "produced"` with
`expected_value: {"retained_as": "supporting_evidence"}`. Done-means 22 requires `abstained` and no
fact in any field for exactly those values. Task 9 implements Done-means 22. The fixture is P2's and
is not edited here. **One of the two must move**; the design's §2.2 sentence backs Done-means 22.

**4 (MEDIUM, F8, now half-closed).** `12-academic-capture-patterns/04-narrow-date-families.json`
(authored 2026-08-22) supplies the EXIF and labeled-date slot families for two of §3.5's four slots
and names *"Task 8's direct-fact slot list"* in its own `owner` field. The **document title** and
**content hash** slots still have no catalogue. Reported, not authored: `planning/deferred-catalogues/`
is another agent's.

**5 (MEDIUM, new). §3.5 names the content hash a direct source, and no observation carries it.**
`src/extractors/filesystem.py` emits `normalized_filename`, `extension` and `mime_type` as labeled
`metadata` observations and deliberately emits **no** content-hash observation — its own comment says
so: *"G5 gives duplicate and version-family signals to P6 'from P1's content hashes' … P6 reads those
from `files`; a second copy here would be two homes for one value."* But P6's rule 1 requires every
non-user fact to cite an observation key, so a content-hash fact has nothing to cite. **Task 8
therefore supports the content-hash slot when the caller supplies one and cross-checks it against
P1's column, and the production `DirectSlots` passes an empty tuple for it**; the fact the content
hash actually supports is Task 14's duplicate family, which cites the observations the family members
share. Nothing is broken; the design's four-slot sentence just has one slot with no producer, and it
should be said out loud rather than discovered.

**6 (LOW, new). §3.5's fourth slot is "labeled form field", and the SPEC's extra direct source is
"filesystem timestamps".** Neither is a form. Catalogue 12/04 calls its two direct families
`metadata_slot` and justifies them from §3.13's *"labeled form field"*; P5's `METADATA_SLOTS` writes
filesystem values the same way. Task 8 reads §3.5's fourth slot as **any explicitly labeled slot
whose label the format itself supplies**, which is what P4 D7 stores and what both of those describe,
and the caller's `DirectSlots.labeled_form_field` carries them. If that reading is wrong the fix is a
fifth member on `DirectSlots`, not a change anywhere else.

**7 (LOW, new). The SPEC restricts P3 input to "exactly two computations", both for the bounded
session.** So a filesystem timestamp must reach Task 8 as an **observation**, never by reading
`files.observed_timestamps` — that would be a third computation the Contract in forecloses. Task 8
reads P1's row for `content_hash` only. This is the same class of tension F10 records for §3.9's
folder-name evidence and is noted so nobody "fixes" Task 8 by reaching into P3's column.

**8 (LOW, informational). `unit_for_observation` is in Task 7's `Consumes:` and is not called.** The
text unit is the span substrate §3.6's quote check needs, which is Task 17's; re-deriving context P4
already split is what M5 forbids. Every name in `Produces:` is delivered unchanged.

---

# Reported by the Tasks 8–9 section


## Contract ambiguities these two tasks hit and did not resolve

Reported here rather than decided, because each belongs to a task or a part this one does not own.

1. **The §3.4 cache-key reconciliation now has a sixth and seventh copy.** `PLAN-tasks-07-09.md`
   states the rule once for Tasks 8 and 9 and counts the copies at five; these two modules make it
   seven, in `facts.direct` and `facts.discount`, character for character. §3.4 names one extractor
   version and one analysis tier, a record built from several observations has several of each, and
   the reconciliation belongs in `facts.cache` — **Task 6's module**, which neither task may add to
   without breaking its contract. One helper in `facts.cache` taking `(conn, content_hash,
   observations)` would delete all seven.

2. **`DirectSlots` has no catalogue behind it (F8, extended).** F8 reported that P5 spells no EXIF
   tag name. Checking the shipped extractor extends it: `extractors.filesystem.METADATA_SLOTS` is
   `("normalized_filename", "extension", "mime_type")` — so §3.13's **filesystem timestamp** slot,
   which Done-means-adjacent prose and this task's own test both need, has **no publisher**, and
   §3.5's **content hash** slot cannot produce a fact at all because M14 admits no citation that is
   not an `observation_key` and P1's `files.content_hash` is a column. §3.5's **document title** slot
   has a publisher (fixture 2) and no catalogue field. Two of §3.5's four slots therefore reach a
   fact today. The catalogue is the same shape as catalogue 01 and belongs beside it.

3. **Catalogue 01's `boundary_rule` is prose, so its compiler has no home.** 86 of the 115 entries
   are `match_kind: "prefix"` and 16 are `regex`; the boundary-character set, the version-tail rule
   and `tail_required` are stated only in an English `boundary_rule` string. Task 9 takes compiled
   predicates so that `facts` holds no regex catalogue and a catalogue v2.0 needs no P6 change, which
   means **something must compile 115 entries and nothing in P6's plan does**. It is the loader's,
   next to the flattening of `property_names`, and it does not exist.

4. **`target_school` (§3.8) and `target university` (§3.11) are one concept with two spellings.**
   Done-means 2 requires both to be present. Under the one-key-per-concept rule one of them is the
   key and the other an alias, and the decision is **Task 2's**. `AUTHORSHIP_FIELDS` names neither,
   so nothing here pre-empts it.

5. **Nothing in this plan orders the discount before the direct producer.** Task 9's suppression is
   what stops a `Producer` slot turning `python-docx` into a `direct` fact, and Task 8 imports
   nothing from `facts.discount` — its `Consumes:` block does not list it. The ordering is
   `facts.resolver`'s (Task 24). Until that task lands, a caller who declares a metadata-property
   slot in its `DirectSlots` gets the fact §2.2 forbids, and no test in either of these two files
   would see it.

---

# Reported by the Tasks 10–13 section


## Contract ambiguities — reported, not resolved

Five, each verified against the source rather than reconstructed, ordered by what it costs if
nobody looks at it.

**1. `Candidate` needs two fields the skeleton's shape does not give it.** The skeleton publishes
`Candidate(value, score, evidence_refs)` and `rank(candidates, *, zone_weight, tier_weight)`. A
weight map has nothing to weight unless the contribution says which zone and which signal tier it
came from, and `rank` has no `conn` with which to resolve the evidence refs back to observations.
Task 11 therefore appends `zone: str | None = None` and `signal_tier: int | None = None` after the
published three, in that order, defaulted, and clears both on the aggregate `rank` returns. The
three published names, their order and their meaning are unchanged, so no parallel author is broken.
**If the reviewer prefers, the alternative is to give `rank` a `conn` and resolve zones from the
cited observations** — one more database read per candidate and one more reason for a pure function
to need a connection. Recommendation: keep the descriptors.

**2. Two cache-key rules now exist across the P6 plan, and they disagree.** This document keys a
fact and an abstention on **every observation of the file version** (see *Two conventions*, above);
`PLAN-tasks-14-15.md` keys a fact on **the observations that fact cites**. Both are readings of
§3.4's five parts and neither is wrong on its own terms. The difference is visible at pass 4: under
this document's rule every pass-4 fact lands in a new cache slot and supersedes; under the sibling's,
only a fact that cited an OCR observation does. This document's rule additionally answers the case
the sibling's cannot — an `unresolved` row with no citations still needs a key, and the SPEC requires
it to have *"same composition as `file_facts`"*. **`facts.cache` (Task 6) owns the reconciliation and
neither of us may add to it.** Whoever executes Task 6 should publish one helper and both plans
should call it. Recommendation: the pass-level rule, because the abstention case forces it.

**3. `DateMatch` is an addition to Task 12's published surface.** Done-means 10 requires the three
academic terms to be matched by dedicated patterns *"asserted by pattern identity in the result
rather than by the value alone"*, and `Candidate` has no field for a pattern id. `date_candidates`
keeps the skeleton's exact signature and is defined as `date_matches` projected onto §3.7's shape,
so nothing that consumes the published name sees a change.

**4. §3.7's "case discipline" is referred to and never stated.** The SPEC says the §3.5
case-insensitivity of N-6 *"does not relax §3.7 facet matching, whose case discipline is stated below
and unchanged"* — and the section below states word boundaries, positional weighting, ranking,
thresholds and validated gazetteers, and no case rule at all. `word_boundary_match` folds case, on
the reading that §3.7's two named cases (`MIT` in "submit", `UNC` in "uncertainty") are decided by
the boundary and not by case, and that a second, case-sensitive matcher would be a second home for
the one word-boundary rule the skeleton says binds facets **and** context terms. Both named refusals
are asserted under case folding in `test_case_folding_does_not_relax_the_boundary`. **If the intended
discipline was case-sensitive facet matching, this is the line to change**, and the change is one
flag on one function — but it would then need a second decision about how the §3.5 context check
reaches a case-insensitive matcher without owning one.

**5. `fill_or_abstain` cannot be told which reliability state to write.** The skeleton's signature
has no state parameter, so Task 11 writes `validated` for every filled facet, on §3.13's definition
(*"found by a deterministic rule and passed contextual checks"*). Task 16's `media_type` uses this
function and wants `validated`, so nothing is broken today. But §3.11's Photos `people`, and any
future field whose ranked fill should be `possible` rather than `validated`, would need a keyword
this signature does not have. Not changed here, because changing a published signature is exactly
what the `Interfaces:` block exists to prevent. Flagged for whoever owns the next facet-producing
task.

## What these four tasks do NOT do

Stated so a reviewer does not look for it: no module here reads `files`, `learning_records`, an
`events` row or a P3 timestamp; none writes an §8.2 event (Task 4 writes `fact creation` when
`write_fact` is called and that is its own task's contract); none branches on `source_type` or
`extractor_name`; none imports `planning/domains/`, `planning/deferred-catalogues/`, a grouping,
tree, placement or model module; none touches a file outside `src/facts/` and `tests/p6/`; and none
contains a model call of any kind — every fact produced by these four is deterministic and Done-means
17 holds over all of them with P8 absent.

---

# Reported by the Tasks 16–19 section


## Contract notes for Tasks 16–19

Reported, not resolved. Each is a decision someone owes; none is answered inside an implementation.

1. **`normalize` and `contradicts` have no owner (round 4, C-5, Task 17).** P8's SPEC names both as
   things it receives *from* P6, and files their domain logic back to P6 in its own Deferred table;
   P6's Task 17 says P6 owns none of the checking. Neither part builds them. Task 17 supplies the
   four inputs as the skeleton says, publishes neither function, and pins that with a test.
   **Owed: a ruling before P8 is planned.** If the answer is P6, it is a new P6 task — the request
   shape does not change either way.

2. **`facts` imports one name from `extractors` (Task 19).** `extractors.failure.ContractViolation`,
   as `FactPassNotRun`'s base class, and nothing else. It creates no cycle and carries no per-format
   knowledge, but it is an edge that did not exist in the skeleton's dependency picture. **Task 25's
   no-invention guard should permit exactly this import and no other from `extractors`.**

3. **The skeleton says four tables; Task 19 adds a fifth (Task 19).** `fact_passes` is P6-internal,
   read by no neighbour, and carries no claim about any file. The clause that binds — *"creates none
   of anyone else's"* — is untouched. Stated so a reviewer counting tables is not surprised.

4. **`FactPassNotRun`'s base class differs from the skeleton's `Exception` (Task 19).** Changed to
   `ContractViolation` on the ratified ruling, because a plain `Exception` is swallowed by
   `orchestrator._extract_one` into a `failed` run and the guard stops guarding.

5. **The tier-3-only refusal is a reading, and it is the one rule Task 16 states that §3.7's
   arithmetic cannot reach.** §2.6's *"must not mistake the absence of EXIF for proof that an image
   is a screenshot"* is unconditional and A07 is a Done-means-grade prohibition, so it cannot rest on
   an injected number. The reason is `below_margin` because the SPEC files *"the
   conflicting-image-signal case (§2.6)"* there by name. If a reviewer prefers a different reason, it
   is a one-word change in `media_type` and one word in the test.

6. **Task 16 assumes `fill_or_abstain` measures the margin against an absent second-best as zero
   (Task 11's contract).** A file carrying only photo-band observations passes one candidate. If
   Task 11 instead refuses a single-candidate list, `test_a_missing_signal_contributes_nothing_to_
   either_candidate` fails and the two authors reconcile — which is the correct place for a
   cross-task disagreement to surface, and is why it is written as a test rather than as an
   assumption in prose.

7. **`ActivationSignals`' shape is Task 13's (Task 17).** The test builds an empty one from the
   dataclass's own field list and annotations rather than hard-coding a shape it does not own; if
   Task 13 declares a field type outside the small map, the assertion fails with that field's name.

8. **The §3.4 cache-key reconciliation is still written out per producer.** Task 16 repeats the rule
   `PLAN-tasks-14-15.md` states once, for the same reason: `facts.cache` is Task 6's module and these
   tasks cannot add to it without breaking its contract. Task 17 is the one place in this file where
   `model_identifier` and `prompt_fingerprint` are not `None`, and its tier is `ANALYSIS_TIERS[-1]`
   unconditionally.

---

# Reported by the Tasks 24–25 section


## Contract notes from Tasks 24 and 25

Reported, not unilaterally resolved. Each was found while writing these two tasks and each belongs to
someone else's decision.

**N1 — Task 1's "no state literal anywhere else in `facts`" is already contradicted by four
sibling tasks, and this guard adopts the narrower rule.** Task 1's skeleton entry asks for *"the
absence of any string literal spelling a state name anywhere else in `facts`"*. As written,
`facts.families` publishes `VERSION_FAMILY_STATES = ("validated", "possible")`, `facts.session`
publishes `SESSION_STATE = "possible"`, `facts.photo_event` publishes `EVENT_STATE = "validated"`
and `facts.llm_seam` publishes `LLM_STATES = ("llm_supported", "possible")`. A guard enforcing Task
1's clause literally would fail on the day this plan is executed — the exact failure mode that made
OQ4's and OQ11's inversions necessary. **What actually matters is the value, not the literal:**
§3.13's risk is a seventh spelling (`LLM-supported`, `User-confirmed`) reaching the database, and
that is closed already — P4's `check` refuses anything outside the six, and every one of the four
constants above is a member of `STATES`. Task 24 nonetheless spells none: `PROPOSAL_ELIGIBLE_STATES`
is derived from `STRENGTH_ORDER`, which is the shape Task 1 wanted. **Owner: Task 1**, to narrow its
clause to "no state name is spelled outside `STATES`'s six members" or to have Tasks 14, 15, 16 and
17 derive theirs by index as Task 24 does.

**N2 — `DECLARED_VOCABULARIES` names two constants no task's `Produces:` line declares.**
`UNRESOLVED_COLUMNS` and `FACTS_TABLES` are listed because Task 5's and Task 4's tests read
`PRAGMA table_info` and Task 19 modifies `schema.py`, so a table-name or column-name tuple is the
natural shape for them — but neither is on a `Produces:` line, so neither is certain. If they are not
built, the two lines are dead entries in an allowlist, which costs nothing. If they are built under
different names, the guard goes red on first run and the fix is one line. **This is the guard
behaving correctly**, and it is written here so that first red is not mistaken for a defect.

**N3 — Task 24 fixes four keyword lists the skeleton left as `...`.** `active_allowlist_for`,
`unresolved_for`, `event_facts`, `session_facts` and `family_facts` are spelled out in this task's
`Interfaces:` block. Nothing is renamed and no signature that another task consumes is changed;
these five are published *by* Task 24 and consumed only by P9–P13, none of which exist.

**N4 — `evidence_chain` and `values_with_counts` are the only two functions in P6 that read another
task's table with SQL.** Both are unavoidable: `evidence_chain` is addressed by `fact_id` alone and
no module publishes a by-`fact_id` read, and `values_with_counts` needs one corpus-wide aggregate.
They read `file_facts`, which is P6's own table, and they write nothing. If Task 4 later publishes
`fact_by_id(conn, fact_id)`, `evidence_chain` should use it. **Owner: Task 4**, optional.

**N5 — the four-pass ordering is not asserted here and must not be.** D5 cut Task 26, so
`no_usable_facts_for` is a read surface P6's own tests exercise and the caller keeps passing
`orchestrator.TARGETED_OCR_UNAVAILABLE`. This guard asserts `facts` imports no `orchestrator`, which
is the correct and only enforceable statement of that today. Wiring it is later, separate work.
