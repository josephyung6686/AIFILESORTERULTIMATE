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

**The discount has no caller.** §2.2's suppression must fire **before** ranking. `field_permitted` and
`screen_metadata` are consumed by no sibling and Task 20's `DEGRADATION_ORDER` binds three stages.
**Task 24 owns adding the stage.** Until it does, a `DirectSlots` declaring a metadata-property slot
turns `python-docx` into a `direct` fact and no test in this part would see it.

**D9's positive half is asserted nowhere.** No test asserts `target_school` and `client` **are**
destination-eligible. Task 2 is the natural home.

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
