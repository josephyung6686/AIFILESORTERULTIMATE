# P6 — Facts and facets — Task Decomposition (PLAN skeleton)

> **This is not the plan.** It is the skeleton the plan is written into: the rules, the verified
> seams, the file layout, and the task list with its interfaces and its proof obligations. Every
> task below still needs its **complete** test code and its **complete** implementation code written
> — that is the detail pass, and P4's and P5's PLANs are the standard: no placeholders, ever.
> Several authors can write the detail in parallel; the `Interfaces:` block on each task is what
> keeps them from colliding.

---

## Ratified decisions — read this before planning any task (2026-08-22)

Four decisions landed after this skeleton was written. **This document has been reconciled to them**;
if you find a line that still contradicts one, that line is the error, not the decision.

| | Ratified | What it changes here |
|---|---|---|
| **D6** | The academic field key is **`subject`**, and every stored field key is `snake_case`. | **OQ4 is CLOSED.** Done-means 4 resolves `subject`, the catalogue carries a `subject` row and no `course` row, and Task 25's guard **inverts** — it asserts the closure, not the question. §3.11's word "course" is prose for the same field and survives inside quotations. |
| **D2** | P7's `ClassificationRecord` keyed `(file_id, content_hash)` is authoritative; `files.sensitivity_state` is its projection; `Unreadable or unclassified` is a **gate outcome**. | **OQ11 is CLOSED** on the question it asked — *which record is authoritative* — and the answer is P7's. Task 25's guard inverts. **Not settled by D2, so do not build it either way:** whether §3.11's `sensitivity status` stays a P6 universal field row beside P7's record. Round 1 F-2 found it has no producer. Create no such row until asked. |
| **D5** | **Task 26 is CUT.** No `dispatch` split, no `run_wave2` restructure. | P6 touches **no file outside `src/facts/` and `tests/p6/`**. The four passes are a description, not a build item. See the note under preamble rule 5 for the consequence — it is not neutral. |
| **D1** | Narrowed: *"acquiring one fails the test"* struck; no career fields authored. | Task 2 keeps the closed catalogue but its guard no longer forbids a later deliberate reversal of S3. §3.8's four role fields **are** in the catalogue (round 1 F-1) — Done-means 13 and 22 require `authored_by` to exist. |

**The one thing D5 makes dangerous, stated once here and again at rule 5.** Task 19 has P6 raise
`FactPassNotRun` — a `ContractViolation` — when the verdict is consulted before that content hash's
deterministic pass. `ocr_policy.text_layer_state` consults it for **every text-bearing PDF** during
the caller's single loop. With Task 26 cut, nothing reorders that. **So P6's resolver must not be
passed to `run_wave2` as `no_usable_facts`: the caller keeps `TARGETED_OCR_UNAVAILABLE` until the
four-pass work is done.** P6 publishes `no_usable_facts_for` as a read surface its own tests
exercise; wiring it is a later, separate piece of work.

**`planning/domains/` is not this part's field catalogue.** See Task 2.

---

**Goal:** Turn P4's observations into **claims with their evidence attached** — §3.1's file-as-many-facts,
§3.2's observation/fact split, §3.5's three producers writing one format, §3.6's abstention,
§3.7's conservative facets, §3.13's six reliability states — in `fields` / `values` / `file_facts` /
`unresolved`, with **no path, no destination, no folder and no group column anywhere** (§3.14, §4.3).

**Architecture:** P6 is a sixth package (`src/facts/`) alongside `database_agent`, `scan_agent`,
`eval_harness`, `evidence_shape` and `extractors`, inside P1's single local SQLite database (§0). It
owns **four** tables and creates none of anyone else's. It reads P4's `evidence` rows and never
writes one. Its producers are separate modules with one sequencer (`resolver.py`) because §8.6
fixes their order — direct, then rule-validated, then (budget and privacy permitting) LLM — and
that order is a contract, not an implementation detail.

**Tech Stack:** Python 3.12 · stdlib only (`sqlite3`, `hashlib`, `re`, `json`, `unicodedata`) ·
`pytest` · P1's `database_agent`, P4's `evidence_shape`, P2's `eval_harness` · **no third-party
runtime dependency is added by this plan.** P7 and P8 do not exist; every surface that would be
theirs is an injected callable with no default.

---

## Read this before Task 1 — the five rules that decide whether this part is correct

### 1. A fact is never separable from its evidence

§3.1 is unconditional: *"Every fact preserves where it came from."* §3.2 says why — *"the product
must preserve both the original evidence and the conclusion built from it. If a resolver later
improves, the system can generate a better interpretation while retaining the original filename,
heading, metadata field, text span, or OCR result that supported the earlier interpretation."*

Concretely, and each of these is a test, not a comment:

- **Every non-user fact carries at least one `evidence_refs[]` entry, and every entry is a P4
  `observation_key`** (M14) — never an `observation_id`, never a row id. The key is content-addressed
  and excludes `extractor_version` by construction (P4 MINOR 8, verified: `observation_key` hashes
  `content_hash · extractor_name · locator · raw_value` and nothing else), which is what makes a
  citation recorded today still resolve after an extractor upgrade (§8.7).
- **P6 never writes, edits, re-normalizes or deletes an observation.** P4 enforces this at the
  database: the `evidence` table carries an `evidence_never_overwritten` trigger on
  `raw_value, location, occurrence_count, observed_at, extractor_name, extractor_version, run_id`
  and an `evidence_no_delete` trigger. P6's tests assert the *intent* — the raw value is unchanged
  after resolution — and the triggers make the assertion unfalsifiable.
- **The abstention carries evidence too.** An `unresolved` row records which observation keys were
  considered, where any were. A refusal with no record of what it looked at is not inspectable.

### 2. Rules and the LLM write into ONE fact format, and P6 owns it

§3.5, verbatim: *"A file fact is not inherently rule-based or LLM-based. It is the common format
into which both systems write their conclusions."* So:

- **There is one `file_facts` table and one set of six reliability states.** P6 does not build a
  rules table and a model table. The producer is a column (`origin`), not a schema.
- **The six literals are P4's, already published, and P6 re-spells none of them.**
  `evidence_shape.vocabulary.RELIABILITY_STATES` is `("user_confirmed", "direct", "validated",
  "llm_supported", "possible", "rejected")` — lowercase, snake_case. P6 *imports* that tuple. The
  §3.13 prose spellings (`LLM-supported`, `User-confirmed`) are prose, and a value outside the six
  is a load error rather than a spelling to normalize.
- **P6 owns all six; extractors may write two.** `evidence_shape.vocabulary.EXTRACTOR_RELIABILITY_STATES`
  is `("direct", "possible")` and P4 conformance rule 3 rejects the other four on an *observation*
  (P4 D11). That boundary is **Task 1's test**: the same tuple, two different admissible subsets,
  asserted from both sides — `conformance.validate_observation` refuses a `validated` observation,
  and `file_facts` accepts a `validated` fact. It is not a comment in a docstring.
- **The LLM creates no field and no schema.** §3.5: *"The LLM is not allowed to invent a new fact
  schema, create an unsupported field, or make a free-form filing decision."* §3.12: values may
  auto-create, fields may not. Task 2's guard is a runtime-introspection test, not a code review.

### 3. P6 abstains rather than guesses, and the abstention is a row

§3.6: *"A model that cannot cite sufficient evidence must return unknown. A model output that is
useful but too weak to establish a fact may remain a possible clue for review; it must not quietly
become a folder proposal or an asserted file property."*

The design says "no fact". **B7 says that is not enough**, because §8.5 asks under Fact quality
*"Did it abstain when evidence was absent?"* and an absent row cannot answer it. So every refusal
this part makes writes an `unresolved` row naming the field and one of thirteen reasons.

Two consequences that are contract:

- **`unresolved` is not a weak fact.** No `value_id`, no reliability state, absent from every fact
  read including the proposal-eligible read. A reader that treats it as a `possible` has broken it.
- **`budget_deferred` and `privacy_withheld` are not abstentions.** §8.6: deferred work must be
  *mark the deferred stage, and leave the file or group in review rather than guessing (§8.6), which "avoids the false impression that an unprocessed file was understood and found unimportant"*. P2's writer already enforces
  the separation — `record_stage_output` raises `ValueError` when `outcome == "deferred"` and
  `budget_state != "ceiling_reached"`, and again when `budget_state == "ceiling_reached"` and
  `outcome == "abstained"`. P6 does not need to invent the rule; it needs to not fight it.

### 4. Every open question stays open, and every threshold is injected

Ten questions are open in P6's SPEC (OQ1 and OQ12 closed; the numbering keeps its gaps because P2,
P4 and P5 cite these by number). Not one is answered in code here. Twenty-two rows are Deferred.
Where the design leaves a value open — a minimum score, a minimum margin, a positional weight, a
signal-tier weight, a session window, a GPS radius, a gazetteer, a regex catalogue, a producer-string
list, a usable-fact threshold — **this plan holds a caller-supplied strategy or a required keyword
with no default, never a number and never a list.** Task 25 enforces it by runtime introspection of
every module's namespace, not by searching source text: a source-text guard matches comments and
docstrings and has broken three tasks on this project already (P5 PLAN, Task 20).

The one place this is easy to get wrong: **catalogue 01** (`planning/deferred-catalogues/01-tool-producer-strings.json`,
115 entries) is the suppression list §2.2's discount rule consumes. Its own `injection` clause is
explicit — *"P6 receives this list as data at construction … It is **not** imported as a module-level
constant"*. Copying it into `src/facts/catalogues.py` satisfies the letter of Task 25's guard and
destroys its point.

### 5. P6 runs **twice** per content hash, and the second run is not optional

This is the rule the built Wave-2 caller currently violates, and it is structural rather than
cosmetic — it changes the shape of `run_wave2`, not a line inside it. See finding F1 for the defect;
this is the shape that fixes it.

The SPEC constrains `no_usable_facts` twice, and the two clauses together force three passes:

> *"**Defined only after P6's deterministic pass on that content hash has completed.** Consulted
> earlier it would return `true` for every file and trigger OCR on the whole corpus."*

> *"…it is **re-evaluated after targeted OCR adds observations**, because the new run changes the
> §3.4 cache key."*

So the required order is:

```text
Pass 1   P5 native extraction          every routed extractor except E6; P4 writes the runs
         ↓                             every observation for this content hash is now IN THE STORE
Pass 2   P6 deterministic resolution   direct, then rule-validated, over the native-tier evidence
         ↓                             facts and `unresolved` rows written; the pass is RECORDED
         no_usable_facts(file_id, content_hash)   answerable for the first time, from the fact tables
         ↓
Pass 3   P5 targeted OCR               ONLY for files P6 reported as having no usable facts (§2.2)
         ↓                             a second run, `analysis_tier = "ocr"`, new observations
Pass 4   P6 re-resolution              over native + OCR evidence; a NEW §3.4 cache key, so the
                                       new facts SUPERSEDE rather than overwrite (§8.2)
```

Three facts make this non-negotiable rather than a preference:

- **At the current consult point the evidence does not exist yet.** `document_ocr_decision` is
  called inside `extract()` on the freshly-built `ExtractionResult`, and `_write(sink, result, ...)`
  does not run until `orchestrator.py:211`, after `_extract_one` returns. So the observations P6
  would have to reason about have not been handed to P4 at all — `observations_for_file` returns
  nothing for that run. A correctly-implemented P6 could not answer the question even if it wanted
  to; it is not merely being asked too early, it is being asked about rows that do not exist.
- **Pass 4 is required, not an optimization.** §3.4's cache key includes `analysis_tier`, and the OCR
  run's tier is `ocr` where the native run's is `native` — so the OCR observations are, by
  construction, outside the cache slot the pass-2 facts were computed under. Skipping pass 4 means
  targeted OCR runs, produces evidence, and no fact is ever derived from it.
- **Pass 4 supersedes; it does not overwrite.** The new key is a different key, so §8.2's rule
  applies unchanged: the pass-2 fact (or the pass-2 `unresolved` row) stays readable, the pass-4
  fact is `preferred`, and the reason is recorded. This is §8.2's own worked example — a first pass
  that recovered nothing, a later engine that did — arriving as the ordinary path rather than as an
  edge case.

**The property must be enforceable, not documented.** Task 19 makes P6 raise `FactPassNotRun` when
the verdict is asked about a `(file_id, content_hash)` whose deterministic pass has not been
recorded, so a caller that consults too early fails a test instead of OCRing the corpus.

**Task 26 is CUT (D5), and that changes what this paragraph can promise.** Nothing rewires the
orchestrator, so the four passes above are a DESCRIPTION of the ordering P6's verdict needs, not a
thing this plan builds. The operational consequence must be stated plainly, because it is the
opposite of harmless: `ocr_policy.text_layer_state` consults `no_usable_facts` for every
text-bearing PDF during loop 1, before any deterministic pass has run for that content hash. So if
P6's resolver were passed as `no_usable_facts` today, Task 19's raise — correctly a
`ContractViolation` — would **end the scan on the first text-bearing PDF**.

**Therefore the caller keeps passing `orchestrator.TARGETED_OCR_UNAVAILABLE` even after P6 ships.**
P6 publishes `no_usable_facts_for` as a read surface that P6's own tests exercise; it is not wired
into `run_wave2`. Wiring it is the four-pass work, owed when an OCR engine makes the broken-text-layer
route act on anything (`src/readers/` now supplies one, so the remaining blocker is only this).

---

## Global Constraints

Every task's requirements implicitly include these.

- **A fact carries no path** (§3.14). `file_facts` has no path column, no destination column, no
  folder column, no group column. §3.14: *"A fact such as subject = BUSIB 4300 does not itself
  dictate one permanent folder path."* A reviewer must be able to check this by reading the schema
  alone, so Task 4 asserts the column set is exactly what it declares and nothing else.
- **P6 stores no group membership** (§4.3, §4.1). No fact is written for a file from another file's
  evidence. §4.1: the graph *"does not automatically copy those missing facts onto sparse files"*.
  §3.9: a session is *"not a basis for automatic semantic propagation"*.
- **New values may be created automatically; new fields may not** (§3.12). *"The system may create
  new values when it sees a new course, project, company, university, or event, but it should not
  invent new fields automatically."*
- **The six reliability states are spelled once**, imported from `evidence_shape.vocabulary`. P6
  publishes no second copy and no alias table.
- **`unresolved` reasons and `origin` values are P6's own closed vocabularies**, published once, in
  one module, checked with P4's `evidence_shape.vocabulary.check(value, vocabulary, *, name)` so a
  bad value raises `NotInVocabulary` rather than being stored.
- **No fuzzy date parsing, ever** (§3.10). Candidates are found by explicit regular expressions and
  then parsed without fuzzy matching. The regexes are injected; three patterns are named by the
  design and are required (`Spring 2025`, `AY 2024-25`, `Michaelmas Term 2024`).
- **Word-boundary matching, never substring** (§3.7). `MIT` must not match inside `submit`; `UNC`
  must not match inside `uncertainty`. This binds facet values *and* §3.5 context terms.
- **P6 never re-derives what P4 assigns.** `signal_tier` comes from P4's observation and is never
  recomputed from `extractor_name` or a field label — that would encode §2.6 in a second place (M2).
  `observation_key` comes from P4's function and is never recomputed. `analysis_tier` comes from
  P4's `ExtractionRun` and is never inferred.
- **P6 depends on no read order from P4, and imposes its own.** Verified by execution on 2026-08-21,
  not read from a docstring: `evidence_shape.store.observations_for_file` orders by `rowid`, which is
  **insertion order** — writing the same three fixtures as runs 1,2,3 and as 3,2,1 returns
  `['BUSIB 4300', 'BUSIB 4300 Syllabus', 'Columbia']` and `['Columbia', 'BUSIB 4300 Syllabus',
  'BUSIB 4300']` respectively. Every P6 computation whose outcome could depend on order — above all
  §3.7's ranking, where a tie is decided by whichever candidate is seen first — must impose a total
  order of its own (canonically: score descending, then `observation_key` ascending) before it
  decides anything. Otherwise the same corpus extracted in a different order produces different
  facts, and §8.5's replay compares a run against itself and reports a regression. Task 11 asserts
  this by shuffling the input and requiring an identical result; Task 25 asserts no module consumes
  a P4 read as an ordered sequence without re-sorting it.
- **"Parent-folder context", never "directory position"** (MINOR 11). §2.9's name is the published
  one. P1's column is still spelled `directory_position`; P6 reads that column and publishes the
  value under §2.9's name — the same rule P5 follows.
- **P6 authors its events; P1 writes them** (M8). `subsystem = "P6"` is written in exactly one
  module and Task 25 asserts there is no second.
- **P6 recomputes nothing of P3's §1.2 record and re-observes no filesystem.** It reads P1's `files`
  row. Its only non-P4 fact input is the two P3 values §3.9's bounded session needs.
- **P6 contains no model call of any kind.** Every LLM call is P8's (§3.3). `analysis_tier = "llm"`
  is a value P6 records on a fact's cache key when P8 produced it, never a call P6 makes.
- **Python 3.12**, stdlib only. `pyproject.toml` already carries `pythonpath = ["src"]` and
  `testpaths = ["tests"]`, so `facts` is importable and collected with no change to any file P6
  does not own.
- **P6 creates and modifies no P1, P2, P3, P4 or P5 file — and, since D5 cut Task 26, no
  `src/orchestrator.py` either.** The plan now has NO exception: every file it touches is under
  `src/facts/` or `tests/p6/`. That is a stronger guard than the one it replaces, and it should be
  asserted rather than merely stated.

---

## What P6 consumes from P1

Written against `src/database_agent/` **as implemented on 2026-08-21** — read from the source, not
from P1's PLAN.

```text
database_agent.db          open_database(path, *, scan_roots: Iterable[Path] = ()) -> sqlite3.Connection
                           create_schema(conn) -> None
                           transaction(conn)                            contextmanager, reentrant (SAVEPOINT)
database_agent.files_table get_file(conn, file_id: str) -> sqlite3.Row
                           FILES_COLUMNS: tuple[str, ...]               (sixteen)
database_agent.events      append_event(conn, **fields) -> int
                           RESERVED_EVENT_TYPES: frozenset[str]         (§8.2's nineteen)
                           EVENT_FIELDS: tuple[str, ...]                (eleven)
                           CORRECTION_FIELDS: tuple[str, ...]           (five)
                           CORRECTION_SCOPES: tuple[str, ...]           (§8.7's six)
                           MalformedEvent, UnregisteredEventType
database_agent.supersede   SUPERSEDE_COLUMNS: tuple[str, str, str]
                           supersede_ddl(table: str) -> str
                           mark_superseded(conn, table: str, *, old_id: str, new_id: str,
                                           reason: str) -> None
                           chain(conn, table: str, record_id: str) -> list[sqlite3.Row]
database_agent.budget      CEILING_KEYS: tuple[str, ...]                (sixteen)
                           get_ceiling(conn, key: str) -> int | None
database_agent.learning    learning_records(conn, scope: str, subject_id: str) -> list[sqlite3.Row]
                           reset_cutoff(conn, scope: str, subject_id: str) -> int | None
```

Six facts about that surface, each of which changes how a task below is written:

- **`__init__` re-exports four names only** (`open_database`, `default_database_path`, `transaction`,
  `SCHEMA_VERSION`). Everything else imports from its module.
- **The file record is a `sqlite3.Row`, not a dataclass.** There is no `FileRecord` type. The
  columns P6 reads are `file_id`, `content_hash`, `hash_algorithm`, `current_path`, `mime_type`,
  `detected_format`, `sensitivity_state`, `directory_position`, `observed_timestamps`. `sqlite3.Row`
  has no `.get`; `orchestrator.get_file` wraps it in `dict()` for that reason and P6 does the same.
- **`fact creation` and `fact rejection` are spelled with a SPACE**, and both are already in
  `RESERVED_EVENT_TYPES`, so P6 registers nothing. `fact_creation` raises `UnregisteredEventType`
  at run time, not at review. This is the same class of defect as MINOR 2's `OCR`/`ocr`.
- **`append_event` requires `event_type`, `subsystem`, `component_version`, `observed_at` and
  `explanation` to be present and non-empty**, and rejects any key outside
  `EVENT_FIELDS + CORRECTION_FIELDS + ("base_event_type",)`. P6's structured explanation is
  canonical JSON naming the fact and its evidence refs (§8.2's *"structured explanation or evidence
  reference"*).
- **`mark_superseded` requires the target table to have a column literally named `record_id`.**
  P4 solved this with a VIRTUAL generated column (`evidence_shape.schema.SUPERSEDE_ADAPTER_COLUMN
  = "record_id"`, projecting `observation_id`). `file_facts` and `unresolved` must do the same,
  projecting `fact_id` / `unresolved_id`. It is a one-line DDL clause and a silent failure if missed.
- **`learning_records` is a projection over `events`, not a table**, and it filters on
  `correction_scope` + `correction_subject` + `user_id IS NOT NULL` — **not on `file_id`**. The
  returned rows carry `polarity`, `proposal_class`, `basis_key`. `basis_key` is one TEXT column, so
  I4's `(file_id, field, value_id)` triple must be serialized canonically in exactly one place.
- **P1 has no budget-stop surface at all** — no `ceiling_reached`, no `budget_state`, no exception,
  no counter. It stores ceiling *values* and enforces nothing. P3's precedent is the injected
  predicate `budget_exhausted: Callable[[], bool]`, and P6 follows it.

## What P6 consumes from P3

P6 reads P3's row for exactly two values, both inputs to §3.9's bounded download session (G6), and
re-observes no filesystem.

```text
files.observed_timestamps   TEXT, JSON — written by scan_agent.basic_record as
                            json.dumps({"mtime": observed.mtime}); read through
                            database_agent.files_table.get_file(conn, file_id)
files.directory_position    TEXT — §2.9's "parent-folder context" (MINOR 11); the producing
                            function is scan_agent.basic_record.parent_folder_context(path) -> str
```

Three facts that change a task:

- **There is no `timestamps` field.** One value, `mtime: float`, spelled three different ways
  across the seam: `ObservedFile.mtime` (P3 in memory), `CacheVerdict.observed_modification_time`
  (P3's stat cache), `files.observed_timestamps` (the JSON column). P6 reads the third.
- **`parent_folder_context` is a function name and a keyword name, not a field and not a column.**
  P6 reads the `directory_position` column and publishes the value under §2.9's name.
- **P3 publishes no `file_id` → scan-row read.** `stat_cache.prior_observation(conn, path)` is
  keyed by *path*. P6 goes through P1's `files` row, which is the only per-`file_id` handle.

## What P6 consumes from P4

P6 reads the frozen observation shape and nothing else, and must resolve a fixture carrying an
unrecognised `source_type` with no new code (§2.8, Done-means 6).

```text
evidence_shape.observation   Observation                       frozen dataclass, seventeen fields
                             OBSERVATION_FIELDS: tuple[str, ...]           (eighteen names)
                             observation_key(*, content_hash: str, extractor_name: str,
                                             locator: str, raw_value: str) -> str
                             observation_from_mapping(mapping) -> Observation
                             MalformedObservation
evidence_shape.location      Location(zone, container_path, text_span, time_span, region)
                             Segment(kind, index, label)
evidence_shape.vocabulary    RELIABILITY_STATES            six, lowercase snake_case
                             EXTRACTOR_RELIABILITY_STATES  ("direct", "possible")
                             ZONES (15) · SOURCE_TYPES (14) · SIGNAL_TIERS (1, 2, 3) — ints
                             ANALYSIS_TIERS ("filesystem", "native", "ocr", "llm")
                             check(value, vocabulary, *, name) · NotInVocabulary
evidence_shape.runs          ExtractionRun                    frozen, fourteen fields
                             .analysis_tier · .config_fingerprint (property) · .completeness
evidence_shape.store         observations_for_file(conn, file_id) -> list[Observation]
                             observations_by_key(conn, observation_key) -> list[Observation]
                             observations_for_run(conn, run_id) -> list[Observation]
                             get_observation(conn, observation_id) -> Observation
                             runs_for_content(conn, content_hash) -> list[ExtractionRun]
                             runs_for_file(conn, file_id) -> list[ExtractionRun]
                             unit_for_observation(conn, observation) -> TextUnit | None
evidence_shape.canonical     canonical_json(value) -> str · sha256_of(*parts: str) -> str
evidence_shape.conformance   CONFORMANCE_RULES: Mapping[int, str]          (1..12)
                             validate_observation(candidate) -> Observation
evidence_shape.fixtures      by_number(number: int) -> Fixture             (1..19)
                             Fixture(number, design_case, run, observations, text_units)
evidence_shape.schema        create_evidence_schema(conn) -> None
```

Seven facts that change a task:

- **`__init__.py` re-exports nothing.** Every import is `from evidence_shape.<module> import X`.
- **`observation_key` is a `@property`, not a dataclass field.** `dataclasses.fields(Observation)`
  does not contain it. It *is* in `OBSERVATION_FIELDS`, in `to_mapping()`, and in the `evidence`
  DDL. P6 reads `observation.observation_key`; it never constructs an `Observation` with one.
- **`zone` lives on `Location`, positional field #1**, and is also reachable as the
  `Observation.zone` property. §3.7's positional weighting keys on it.
- **`signal_tier` members are the integers `1, 2, 3`**, not strings, and P4 enforces that a
  non-null `signal_tier` implies `source_type == "image"` (conformance rule 11).
- **The observations table is named `evidence`**, its identity column is `observation_id`, and
  `record_id` is a VIRTUAL projection of it.
- **There is no per-content-hash observation read.** `observations_for_file(conn, file_id)` spans
  every content hash the file has had. Every P6 read that is per *file version* — which is all of
  them, because the cache key and the abstention row are per content hash (§3.4, §8.2) — must filter
  on `observation.content_hash`. Task 7 owns that filter so it exists once. *This is a real gap in
  P4's published read surface and is reported rather than patched here; see the findings.*
- **Every observation read is in insertion order, and P6 must not rely on it.** `ORDER BY rowid` on
  `observations_for_run`, `observations_for_file`, `observations_by_key` and
  `observation_keys_for_run`. Verified by execution (see Global Constraints); `observation_keys_for_run`
  was random-UUID order until 2026-08-21 and is now `rowid`, which is a reason to verify ordering
  claims by running them rather than by reading them. Insertion order is stable within one database
  and is **not** a property of the corpus, so P6 sorts before it ranks.
- **Fixture 1 is the walking-skeleton fixture** and carries `context_before` exactly `"Syllabus — "`
  — capital S, U+2014 EM DASH, one space either side, verified byte-exact. B8(a)'s whole purpose was
  to make the skeleton's one fact resolvable, and a case-sensitive §3.5 context check would refuse it
  (N-6). Its `raw_value` is `"BUSIB 4300"` in zone `heading`, `reliability = "possible"`,
  `occurrence_count = 3`, locator `heading:page=1/heading=2`.

## What P6 consumes from P5

Only via P4's shape. P6 requires no per-format knowledge and must not acquire any. Three P5 outputs
P6 depends on **by value, never by format** — each arrives as an ordinary P4-shaped observation:

| Needed for | How it actually arrives | Verified literals |
|---|---|---|
| perceptual hash (G5) | an ordinary observation | `source_type="image"`, `extractor_name="image.metadata"`, `zone="metadata"`, container-path `Segment("field", label="perceptual hash")` — **the label is the only distinguisher, and it has a space in it**; `signal_tier` is `None` |
| image signal observations (M2, §2.6) | `signal_tier ∈ {1,2,3}` on the observation | P5 assigns it in one place, `image.py`, from `image.SIGNAL_TIER` — `"camera EXIF"→1`, `"capture time"→2`, `"GPS"→2`, `"sensor-shaped dimensions"→2`, `"exact display resolution"→3`, `"PNG format"→3`, `"software metadata"→3`. **P6 consumes the integer and never the signal name.** |
| camera / capture-time / GPS EXIF (G7) | ordinary observations | `source_type="image"`, `extractor_name="image.metadata"`, `zone="metadata"`, container-path label = **the reader-supplied tag name, which P5 deliberately never spells** |

**Absence is never an observation.** P5 records "no EXIF" and "no text layer" on the run
(`ExtractionRun.completeness`, plus `coverage` and `observation_count`) or nowhere — P4's
`runs.py` docstring states it and conformance rule 12 enforces it. So P6 never receives an absence
and must never treat a missing signal as evidence (§2.6).

P6 publishes one signal back to P5: `no_usable_facts(file_id, content_hash) -> bool`. It is already
a required keyword with no default on `extractors.dispatch.extract`,
`extractors.ocr_policy.text_layer_state`, `extractors.ocr_policy.document_ocr_decision` and
`orchestrator.run_wave2`, typed `Callable[[str, str], bool]` and called positionally. **Two P5 tests
assert it has no default** (`tests/p5/test_p5_no_invention.py`, `tests/p5/test_p5_ocr_policy.py`), so
P6's implementation must match that signature exactly. See Task 19 for the ordering problem this
creates.

## What P6 consumes from P2

```text
eval_harness.vocabulary   STAGE_IDS                  ten; "factual_validation" is index 1
                          DIMENSIONS                 ten; P6's dimension is "fact", NOT "factual_validation"
                          OUTCOMES                   ("produced","abstained","deferred","not_implemented","error")
                          BUDGET_STATES              ("within_ceiling","ceiling_reached")
                          check_stage(stage_id) -> str · UnknownStage
eval_harness.replay       StageResult(subject_ref, outcome, payload, inputs, budget_state, values=())
                          ReplayContext(conn, run_id, bundle_id, stage_id, run_settings, budget_ceilings)
                          StageAdapter = Callable[[ReplayContext], Sequence[StageResult]]
eval_harness.stage_output record_stage_output(conn, *, run_id, stage_id, subject_ref, outcome,
                                              payload, version_tuple_ref, inputs, budget_state,
                                              dimension_values=()) -> int
                          DimensionValue(dimension, subject_ref, outcome, value)
eval_harness.run          VERSION_AXES (six) + "analysis_tiers_enabled"
                          record_version_tuple(conn, **fields) -> str
eval_harness.adversarial  CASE_IDS ("A01".."A12")
```

Three facts that change a task:

- **The envelope field is `version_tuple_ref`, a `sha256:` string**, not `version_tuple`. The
  seven-field tuple lives in its own table. P6 supplies its axes — `prompt_fingerprint`,
  `model_identifier`, and its slice of `extractor_versions` — and does not assemble the tuple.
- **B7's separation is already enforced at P2's writer.** `record_stage_output` raises `ValueError`
  if `outcome == "deferred"` and `budget_state != "ceiling_reached"`, and if
  `budget_state == "ceiling_reached"` and `outcome == "abstained"`. P6's Done-means 20 is therefore
  provable end-to-end through the live writer, exactly as P5's Task 17 proved its own.
- **Six of the twelve adversarial cases are `dimension: "fact"`** — A01 (`MIT` in "submit"),
  A02 (`UNC` in "uncertainty"), A03 (course-code patterns that are ZIP codes or device models),
  A04 (generic author metadata), A05 (multiple institutions in one essay), A07 (stripped EXIF on
  messaging-app photographs). They are JSON fixtures under `tests/eval/fixtures/adversarial/`, and
  they are P6's gate. **Two of them contradict this SPEC as built; see the findings.**

## What P6 consumes from P7, P8, P9 and P13 — none of which exist

Each is an injected callable or a P6-authored fixture, with no default. This is exactly how P5 was
built against P4 fixtures, and it is why the plan states Done-means 17 as a whole-suite guard rather
than as a hope.

| From | Shape P6 injects | What it does when absent |
|---|---|---|
| **P7** (§8.4) | `handling_class(file_id) -> str` — resolved **before** any model request (§8.4: *"enforced before content reaches any model or external connector"*) | With no P7, the injected default in tests is a fixture returning a permissive class. In production it has no default. A class that forbids the model route leaves the field `unknown` and writes `unresolved` with `reason = privacy_withheld` — never a weaker route (§8.6) |
| **P8** (§3.3, §3.6) | `propose(request) -> tuple[Proposal, ...]` and `validate(proposal, checks) -> Verdict`; P6 supplies the request and applies the verdict (O6) | With no P8, the callable is absent and **no LLM path runs at all**. Every `direct` and `validated` fact is produced normally. Done-means 17 is the assertion that this is true of items 4–10, 13–16 and 18–27 |
| **P9** (§4) | nothing. P6 accepts **no** fact write derived from group membership (§4.1, §4.3, §3.9) | The absence is the contract. Task 25 asserts `facts` imports nothing from a grouping module and that no write path takes a `group_id` |
| **P13** (§8.4, §8.7) | `review_action` mappings with `action = mark_private`, carrying `subject_ref`, `plan_version`, `correction_scope`, `presented_state_ref` — authored as P6 fixtures | P6 authors the fact-level consequence (M8); P1 writes the event. Tests drive the fixture directly |

Two shapes P6 must author itself because the parts that will own them do not exist:

- **The P8 request** — the active field allowlist for the file, the citable observation set, the
  existing `direct` and `validated` facts, and the per-field normalizers. Task 17 fixes the shape so
  P8 can be built against it.
- **The P8 verdict** — per proposal: field, value, citations or an explicit `unknown`, plus a pass /
  fail against the four §3.6 checks. P6 owns the *consequence* of each verdict and not the check.

---

## File Structure

```text
src/facts/__init__.py            package marker
src/facts/authorship.py          P6 authors `fact creation` / `fact rejection` (M8, §8.2)
src/facts/states.py              the six reliability states, imported from P4 — one spelling, one order
src/facts/vocabulary.py          P6's own closed sets: origins, unresolved reasons, field scopes
src/facts/schema.py              P6's four tables, inside P1's database — creates no other part's
src/facts/fields.py              the `fields` catalogue: six universal + download_session + six domains
src/facts/values.py              the `values` table: auto-create, raw variants, aliases, display labels
src/facts/file_facts.py          the fact row, its writers and readers, and the negative contract
src/facts/unresolved.py          the abstention row and its thirteen reasons
src/facts/cache.py               §3.4's five-part cache key and what invalidates it
src/facts/evidence.py            the read over P4: keys, the context pair, `context_truncated`
src/facts/direct.py              §3.5 direct facts from reliable, explicit slots
src/facts/discount.py            §2.2/§2.3 suppression and demotion (M4) and §3.8's roles
src/facts/rules.py               §3.5 rule-validated facts and the context check (N-6)
src/facts/facets.py              §3.7 ranking: word boundary, positional weight, score, margin
src/facts/dates.py               §3.10 explicit date and academic-term candidates, no fuzzy parsing
src/facts/domains.py             §3.11 activation, and several domains on one file at once
src/facts/families.py            G5 duplicate family and version family
src/facts/session.py             G6 the bounded download session
src/facts/photo_event.py         G7 the photo event, and §2.6's media-type conflict (M2)
src/facts/llm_seam.py            O6 what P6 supplies P8, and the consequence of each verdict
src/facts/supersede.py           §8.2 supersession and the `preferred` pointer (M1)
src/facts/usable.py              M11 `no_usable_facts`, the recorded pass, and the ordering guard
src/facts/budgets.py             §8.6 the three ceilings, the degradation order, `budget_deferred`
src/facts/resolver.py            the one entry point that sequences the producers in §8.6's order
src/facts/stage_output.py        §8.5 / B7 the `factual_validation` envelope, produced not stored
src/facts/learning.py            §8.7 query-before-propose over P1's learning records (I4)
src/facts/plan_versions.py       §8.8 what belongs to a plan version and what does not
src/facts/read_surface.py        the reads published to P9, P10, P11, P13, P2 and the review UI

tests/p6/conftest.py             P4 fixtures, a fixed clock, injected strategies, absent P7/P8
tests/p6/test_p6_authorship.py   M8, §8.2's two event names, spelled with a space
tests/p6/test_p6_states.py       §3.13's six, and the two-of-six extractor boundary (P4 D11)
tests/p6/test_p6_fields.py       §3.12, Done-means 2 and 3 — the closed field catalogue
tests/p6/test_p6_values.py       §3.12 auto-create, §0 aliases, §2.8's three renderings
tests/p6/test_p6_file_facts.py   Done-means 1 — the row, and the negative contract
tests/p6/test_p6_unresolved.py   B7, Done-means 18 and 19
tests/p6/test_p6_cache.py        §3.4, Done-means 15 and 16
tests/p6/test_p6_evidence.py     M14, Done-means 6 and 30 — keys, context pair, truncation
tests/p6/test_p6_direct.py       Done-means 5, §3.5's four explicit slots
tests/p6/test_p6_discount.py     Done-means 22, M4, A04, §3.8
tests/p6/test_p6_rules.py        Done-means 8, N-6, B8(a)
tests/p6/test_p6_facets.py       Done-means 7 and 9, A01, A02
tests/p6/test_p6_dates.py        Done-means 10, A03
tests/p6/test_p6_domains.py      Done-means 14, §3.11's worked case
tests/p6/test_p6_families.py     Done-means 23 and 24, G5, §8.3
tests/p6/test_p6_session.py      Done-means 25, G6, §3.9
tests/p6/test_p6_photo_event.py  Done-means 26 and 27, G7, M2, A07
tests/p6/test_p6_llm_seam.py     Done-means 11 and 12, O6, §3.6's four checks
tests/p6/test_p6_supersede.py    Done-means 29, M1, §8.2's worked example
tests/p6/test_p6_usable.py       Done-means 28, M11, A10 — and `FactPassNotRun`
tests/p6/test_p6_budgets.py      Done-means 20, §8.6's degradation order
tests/p6/test_p6_stage_output.py Done-means 20 and 21, B7, through P2's live writer
tests/p6/test_p6_learning.py     §8.7, I4's query-before-propose
tests/p6/test_p6_plan_versions.py §8.8
tests/p6/test_p6_read_surface.py Done-means 13, and the proposal-eligible read
tests/p6/test_p6_pass_order.py   preamble rule 5 — the four passes, mechanically
tests/p6/test_p6_deterministic.py Done-means 17 — the whole suite with P8 absent
tests/p6/test_p6_no_invention.py every open question and every deferred row held open
tests/p6/test_p6_skeleton_step.py 02-segmentation-map.md's P6 step
```

Files split by **published record** and by **producer**, not by technical layer: the three fact
families P6 was handed (`families`, `session`, `photo_event`) are one module and one test file each,
with no import between siblings, so they can be built in parallel and one can be rejected in review
without touching its neighbours — the same rule P5's six extractors follow.

---

## The task list

Twenty-seven tasks in five waves. **Tasks 1–6 are foundational and strictly sequential** — every
later task writes rows into their tables. **Tasks 7–13, 14–16 and 17–23 parallelise within their
wave.** Tasks 24, 25 and 27 are the read surface, the guards and the skeleton, and run last.
**Task 26 is cut (D5)**, so no task in this plan touches a file P6 does not own and none needs
scheduling with the lead.

Right-sizing rule applied throughout: a task is the smallest unit that carries its own red-green
cycle and is worth a reviewer's gate. Where a §-section maps to one module and one Done-means item,
it is one task; where a §-section is only a property of another module's schema (§3.8's
`destination_eligible`), it lives with that module and is asserted from the read surface.

---

### Wave A — the tables (sequential; nothing else can start)

#### Task 1: Package skeleton, P6's authorship, and the six states published once

**Files:** create `src/facts/__init__.py`, `src/facts/authorship.py`, `src/facts/states.py`;
test `tests/p6/test_p6_authorship.py`, `tests/p6/test_p6_states.py`.

**Interfaces:**
- Consumes: `database_agent.events.RESERVED_EVENT_TYPES`, `evidence_shape.vocabulary.RELIABILITY_STATES`,
  `evidence_shape.vocabulary.EXTRACTOR_RELIABILITY_STATES`, `evidence_shape.conformance.validate_observation`.
- Produces: `SUBSYSTEM: str`, `COMPONENT_VERSION: str`, `AUTHORED_EVENT_TYPES: tuple[str, str]`,
  `event_defaults(**fields) -> dict`; `STATES: tuple[str, ...]` (re-export), `STRENGTH_ORDER: tuple[str, ...]`,
  `strength(state: str) -> int`, `is_stronger(a: str, b: str) -> bool`.

**Done-means:** foundational to all; directly none.

**What its tests must prove.** That `AUTHORED_EVENT_TYPES == ("fact creation", "fact rejection")`
with the space, that both are members of P1's reserved nineteen so P6 registers nothing, and that
`event_defaults` refuses a foreign type and refuses to name another subsystem. That `STATES` **is**
P4's tuple rather than a copy — asserted by identity of contents against
`evidence_shape.vocabulary.RELIABILITY_STATES`, and by the absence of any string literal spelling a
state name anywhere else in `facts`. That the strength order is `user_confirmed > direct > validated
> llm_supported > possible` and that `rejected` has **no** strength — asking for it raises rather
than returning a number, because §3.13 makes it an exclusion, not a rank. **And the boundary, from
both sides in one test:** `conformance.validate_observation` raises `NonConforming` on an observation
whose `reliability` is `validated`, while `strength("validated")` succeeds — extractors write two of
the six, P6 owns all six, and that is a test rather than a comment.

#### Task 2: `fields` — the closed catalogue, and the field that cannot be created at runtime

**Files:** create `src/facts/vocabulary.py`, `src/facts/fields.py`; modify `src/facts/schema.py`;
test `tests/p6/test_p6_fields.py`.

**Interfaces:**
- Consumes: `evidence_shape.vocabulary.check`, `NotInVocabulary`; `database_agent.db.transaction`.
- Produces: `FIELD_SCOPES: tuple[str, ...]` (`universal`, `academic`, `college_applications`,
  `research`, `finance`, `photos`, `code`), `UNIVERSAL_FIELDS`, `DOMAIN_FIELDS: Mapping[str, tuple[str, ...]]`,
  `FIELD_ROWS: tuple[FieldRow, ...]`, `FieldRow(field_key, display_name, scope, value_kind,
  normalizer_id, destination_eligible, multiplicity)`, `create_fields(conn) -> None`,
  `get_field(conn, field_key) -> sqlite3.Row`, `fields_in_scope(conn, scope) -> list[sqlite3.Row]`,
  `FieldNotInCatalogue`.

**Done-means:** 2, and the negative half of 3.

**What its tests must prove.** That the catalogue is exactly the six §3.11 universal fields, plus
`download_session`, plus the six §3.11 domain rows, **plus §3.8's four role fields** — and nothing
else: Career and recruiting, identity, medical and legal have no field rows.

> **Round 1's F-1, applied here at last.** The four roles are the design's own words — §3.8:
> *"authored_by and target_school, or our_firm and client"* — and this task's list said
> **"nothing else"**, which forbade them. That is not a style disagreement: **Done-means 13 and 22
> both require `authored_by` to exist** (*"an `authored_by` value is never returned as
> destination-eligible"*, *"a human name → `authored_by` only"*), so two Done-means were unwritable
> against the catalogue this task builds. A consumer with no producer, inside one document.
>
> They are role fields, so §3.8's other half binds immediately: *"It should avoid using authorship
> or creator identity as a destination dimension"* — every one of the four is
> `destination_eligible = FALSE`, which Done-means 13 already asserts for `authored_by`.

> **D1, narrowed by Joseph 2026-08-21.** The clause *"and acquiring one fails the test"* is
> **struck.** The closed reading it enforced is impossible: it makes P6's own test suite the thing
> that forbids a later, deliberate reversal of S3, so adding a career field would read as a
> regression rather than a decision. S3 deferred that schema and the deferral stands on its own —
> **P6 starting does not silently un-defer a binding resolution, and P6's tests are not the place
> that resolution is held.** The test asserts the catalogue's contents; it does not assert that the
> contents can never change.
>
> **Do not author career fields.** Not in this task, not in the domain catalogue as field rows.
> **Career is owed before P10**, which is where a destination dimension first needs one. Anyone
> adding one before then is reversing S3 and must say so explicitly.
>
> **And do not read `planning/domains/` as this catalogue's source.** The two are different objects
> and conflating them is the likeliest way this task goes wrong:
>
> | | `FIELD_ROWS` (this task) | `planning/domains/` (574 entries) |
> |---|---|---|
> | What it is | The **closed** field catalogue §3.12 forbids adding to at run time | A **research artifact**: a proposed domain library, mostly `proposal` provenance |
> | Size | §3.11's six universal + `download_session` + six domain sets, plus §3.8's four role fields (round 1 F-1) | 574 entries, 2,164 distinct field keys |
> | Authority | Design-derived and binding | Not ratified. Its own gate currently reports **566 failures** — one third of its template dimensions branch on fields it never declares |
> | Imported by `facts`? | It IS `facts` | **Never.** Task 25 already asserts catalogue 01 is imported nowhere in `facts`; that guard should name the whole directory |
>
> The 574 are a menu someone may one day draw from, entry by entry, with a decision each time. They
> are not a placeholder for this table and they must not be loaded into it. What this task builds is
> the **small list**: §00's own field names plus §3.8's four roles.

That no producer can create a field at run time: the write path is a module-level authored table
loaded by `create_fields`, there is no `add_field`, and an attempt to write a fact naming an unknown
field raises `FieldNotInCatalogue` rather than inserting one. That `destination_eligible` is `FALSE`
for every authorship and creator-identity field (§3.8) and that the per-field assignment beyond that
rule is held open rather than guessed. That `multiplicity` is present as a column and **unanswered**
— OQ6 is Joseph's.

#### Task 3: `values` — auto-create, raw variants, aliases, display labels

**Files:** create `src/facts/values.py`; modify `src/facts/schema.py`; test `tests/p6/test_p6_values.py`.

**Interfaces:**
- Consumes: `facts.fields.get_field`, `evidence_shape.canonical.canonical_json`.
- Produces: `ValueRow(value_id, field_id, canonical_value, raw_variants, display_label, aliases,
  origin, first_evidence_ref)`, `VALUE_ORIGINS: tuple[str, str]` (`automatic`, `user`),
  `ensure_value(conn, *, field_key, canonical_value, first_evidence_ref, origin) -> str`,
  `add_raw_variant(conn, value_id, raw)`, `merge_values(conn, *, keep, merged, reason) -> None`,
  `values_in_field(conn, field_key) -> list[sqlite3.Row]`.

**Done-means:** the positive half of 3.

**What its tests must prove.** That a value auto-creates on first sight with `origin = automatic`
and a `first_evidence_ref` that is an observation key, and that seeing it again returns the same
`value_id` rather than a second row. That a value belongs to exactly one field (§3.12), so the same
canonical string under two fields is two values — which is §3.8's role separation expressed in the
value table. That §2.8's three renderings coexist: `raw_variants` keeps `U Chicago` verbatim,
`canonical_value` is `University of Chicago`, `display_label` is `UChicago`. That a merge **records
an alias and deletes nothing** (§0 taxonomy aliases, §8.2) — after merging, both values are still
readable and every fact that pointed at the merged one still resolves.

#### Task 4: `file_facts` — the row, and the negative contract a reviewer can check from the schema

**Files:** create `src/facts/file_facts.py`; modify `src/facts/schema.py`;
test `tests/p6/test_p6_file_facts.py`.

**Interfaces:**
- Consumes: `facts.states`, `facts.fields`, `facts.values`, `database_agent.supersede.SUPERSEDE_COLUMNS`,
  `database_agent.supersede.supersede_ddl`, `database_agent.events.append_event`, `facts.authorship.event_defaults`.
- Produces: `FILE_FACTS_COLUMNS: tuple[str, ...]`, `FORBIDDEN_COLUMN_SUBSTRINGS: tuple[str, ...]`,
  `FACT_ORIGINS: tuple[str, ...]` (§3.1's five: deterministic extractor · rule · LLM interpretation ·
  user correction · user-approved folder), `write_fact(conn, *, file_id, content_hash, field_key,
  value_id, reliability_state, origin, evidence_refs, cache_key, active, ...) -> str`,
  `facts_for_file(conn, file_id, content_hash) -> list[sqlite3.Row]`, `EvidenceRequired`.

**Done-means:** 1.

**What its tests must prove.** That the table exists with the declared columns and that the column
set contains **no** `path`, `destination`, `folder`, `node` or `group` column — asserted by reading
`PRAGMA table_info` and matching against a forbidden-substring list, so a future column named
`destination_node_id` fails the test the day it is added. That `evidence_refs[]` is required and
non-empty for every non-user reliability state and that each entry is an observation key
(`sha256:`-prefixed), raising `EvidenceRequired` otherwise. That the `record_id` VIRTUAL column
exists so P1's `mark_superseded` can address the table. That a `fact creation` event is appended
through P1 with `subsystem = "P6"` and a non-empty structured explanation, and that P6 writes no
event of any other type here.

#### Task 5: `unresolved` — the abstention row, and its thirteen reasons

**Files:** create `src/facts/unresolved.py`; modify `src/facts/vocabulary.py`, `src/facts/schema.py`;
test `tests/p6/test_p6_unresolved.py`.

**Interfaces:**
- Consumes: `facts.fields`, `evidence_shape.vocabulary.check`.
- Produces: `UNRESOLVED_REASONS: tuple[str, ...]` (the thirteen), `ATTEMPTED_PRODUCERS: tuple[str, str, str]`
  (`direct`, `rule`, `llm`), `write_unresolved(conn, *, file_id, content_hash, field_key, reason,
  attempted_producers, evidence_refs, cache_key) -> str`,
  `unresolved_for_file(conn, file_id, content_hash, *, field_key=None, reason=None) -> list[sqlite3.Row]`,
  `NOT_ABSTENTIONS: frozenset[str]` (`budget_deferred`, `privacy_withheld`).

**Done-means:** 18, 19.

**What its tests must prove.** That the thirteen reasons are exactly the SPEC's thirteen and a
fourteenth is refused. That an `unresolved` row carries **no** `value_id` and **no** reliability
state column at all — asserted from `PRAGMA table_info`, not from a null check, because a nullable
column is a place someone will later write a value. That it obeys the same negative contract as
`file_facts` (no path / destination / folder / group column). That a later fact for the same
`(file_id, content_hash, field_id)` **supersedes** the row and does not delete it, and the row
remains readable afterwards. That `budget_deferred` and `privacy_withheld` are members of
`NOT_ABSTENTIONS` and that a caller asking "did P6 abstain on this field" gets `False` for both.

#### Task 6: §3.4's cache key, and what invalidates a fact

**Files:** create `src/facts/cache.py`; test `tests/p6/test_p6_cache.py`.

**Interfaces:**
- Consumes: `evidence_shape.canonical.sha256_of`, `evidence_shape.canonical.canonical_json`,
  `evidence_shape.vocabulary.ANALYSIS_TIERS`, `evidence_shape.runs.ExtractionRun`.
- Produces: `CACHE_KEY_PARTS: tuple[str, ...]` (`content_hash`, `extractor_version`, `analysis_tier`,
  `model_identifier`, `prompt_fingerprint`), `fact_cache_key(*, content_hash: str, extractor_version: str,
  analysis_tier: str, model_identifier: str | None, prompt_fingerprint: str | None) -> str`,
  `is_stale(conn, *, file_id, content_hash, cache_key) -> bool`.

**Done-means:** 15, 16.

**What its tests must prove.** That the key is composed of exactly §3.4's five parts and that
changing any one of them changes the key, while changing the file's **path** does not — Done-means
16's rename case, which follows from `content_hash` being in the key and `current_path` not being.
That a bumped `extractor_version` and a changed `prompt_fingerprint` each produce a different key
and therefore a re-resolution. That `model_identifier` and `prompt_fingerprint` are `None` on a
deterministic fact and that `None` is distinguishable from the empty string in the digest — P4's
`sha256_of` is length-prefixed and injective, so this is a property to assert rather than a hazard to
avoid. **And the naming trap:** `extractors.runs.cache_key(*, content_hash, extractor_name,
extractor_version, analysis_tier, config_fingerprint)` already exists and is a **different key** —
P5's extraction-result identity. The test asserts the two functions produce different digests for the
same content hash and that `facts` does not import P5's, so one name never silently answers the other
question.

---

### Wave B — the citation layer and the deterministic producers (7–13 parallelise)

#### Task 7: The evidence read — observation keys, the context pair, and `context_truncated`

**Files:** create `src/facts/evidence.py`; test `tests/p6/test_p6_evidence.py`.

**Interfaces:**
- Consumes: `evidence_shape.store.observations_for_file`, `observations_by_key`, `runs_for_content`,
  `unit_for_observation`; `evidence_shape.observation.Observation`.
- Produces: `observations_for_version(conn, file_id, content_hash) -> tuple[Observation, ...]`,
  `context_pair(observation) -> tuple[str, str, bool]`, `cite(observation) -> str`,
  `resolve_citation(conn, observation_key) -> tuple[Observation, ...]`,
  `analysis_tier_for_observation(conn, observation) -> str`.

**Done-means:** 6, 30.

**What its tests must prove.** That P6 resolves a fixture whose `source_type` is unknown to it —
driven by constructing an observation with a `source_type` P6 has never seen, and asserting facts are
still produced — and that **no module in `facts` branches on `source_type` or `extractor_name`**,
asserted by runtime introspection of every module namespace for a mapping keyed by a member of
`SOURCE_TYPES`. That `context_pair` returns `context_before` and `context_after` as **two** values
and never a concatenation (M5), and returns the `context_truncated` flag alongside them so no caller
can read the context without seeing the flag. That `cite` returns `observation.observation_key` and
never `observation_id`, and that a citation stored before an extractor-version bump still resolves
through `observations_by_key` afterwards — the M14 property, provable because
`observation_key` excludes `extractor_version`. That `observations_for_version` filters on
`content_hash` and does not return a prior version's observations.

#### Task 8: Direct facts — §3.5's four explicit slots

**Files:** create `src/facts/direct.py`; test `tests/p6/test_p6_direct.py`.

**Interfaces:**
- Consumes: `facts.evidence`, `facts.file_facts.write_fact`, `facts.values.ensure_value`,
  `database_agent.files_table.get_file`.
- Produces: `direct_facts(conn, *, file_id, content_hash, slots: DirectSlots) -> tuple[str, ...]`,
  `DirectSlots` — an injected frozen dataclass of slot-name predicates, no defaults.

**Done-means:** 5, and part of 4.

**What its tests must prove.** That an EXIF `DateTimeOriginal` observation produces a `direct` fact
and that the EXIF observation remains separately readable afterwards with its `raw_value` unchanged.
That a filesystem timestamp is `direct` while a date recovered from text or a filename is **not** and
takes §3.10's path instead — the §3.5 distinction, asserted as two different reliability states from
two observations carrying the same date string. That the four slots §3.5 names (content hash, EXIF
timestamp, document title, labeled form field) are reached through an **injected** `DirectSlots`
rather than a literal slot-name table: P5 deliberately spells no EXIF tag name, so a hard-coded
`"DateTimeOriginal"` in `facts` would be P6 inventing a vocabulary member P5 refused to publish.
*This injection point is a deferred catalogue that does not exist; see the findings.*

#### Task 9: Roles, and the producer/creator discount (M4)

**Files:** create `src/facts/discount.py`; test `tests/p6/test_p6_discount.py`.

**Interfaces:**
- Consumes: `facts.evidence`, `facts.fields`, `facts.unresolved.write_unresolved`.
- Produces: `discount(observation, *, tool_producer_strings, metadata_property_names) -> str`
  returning one of `suppress` | `demote` | `not_metadata`; `AUTHORSHIP_FIELDS: tuple[str, ...]`;
  `is_discount_target(observation, *, metadata_property_names) -> bool`.

**Done-means:** 22, and the §3.8 half of 13.

**What its tests must prove.** That a `Producer` value on the suppression list produces **no fact in
any field** — including `authored_by` — and exactly one `unresolved` row with
`reason = discounted_tool_metadata`; and that it is **not** demoted to `possible`, because §2.2 is
literal that such a value *"should not be mistaken for meaningful content"* and a tool name is a fact
about the software, not a weak clue about the document. That any other producer/creator/author value
may populate an authorship role field and **nothing else** — never topic, purpose, project, course,
institution or target. That the rule fires **before** facet ranking, so a discounted value never
enters §3.7's candidate list and cannot win a margin it should never have contested — asserted by
running a corpus where the discounted string would otherwise be the top-ranked candidate and showing
the field is filled by the second candidate rather than left empty for the wrong reason. That the
suppression list and the metadata property names are **injected** and that P4's fixture 6
(`raw_value = "python-docx"`, zone `metadata`, `reliability = "direct"`) resolves correctly —
`direct` describes the *slot*, not the value's usefulness, which is the whole of M4.

#### Task 10: Rule-validated facts, and the §3.5 context check (N-6)

**Files:** create `src/facts/rules.py`; test `tests/p6/test_p6_rules.py`.

**Interfaces:**
- Consumes: `facts.evidence.context_pair`, `facts.facets` (word-boundary matcher),
  `facts.unresolved.write_unresolved`, `facts.file_facts.write_fact`.
- Produces: `Rule` — an injected frozen dataclass of `(pattern, required_context_terms, field_key)`;
  `apply_rules(conn, *, file_id, content_hash, rules) -> tuple[str, ...]`;
  `context_check(before: str, after: str, terms) -> bool`.

**Done-means:** 8, and the `validated` half of 4.

**What its tests must prove.** That a course-code-shaped string with no academic context term in its
surrounding context produces **no** course fact and one `unresolved` row with
`reason = context_check_failed`. That the same string with `context_before: "Syllabus — "` **does**
produce one — P4's fixture 1 verbatim, capital S — because the check is case-insensitive (N-6, B8(a));
without this the walking skeleton produces no fact at all. That case-insensitivity does **not** relax
word boundaries: `semester` must not match inside a longer word, and `Syllabus`/`SYLLABUS`/`syllabus`
all pass. That a context check failing on a record with `context_truncated = true` writes
`reason = context_truncated` and **not** `context_check_failed` — §8.6 forbids silent truncation, and
a term that may have been cut is not a clean refusal. That the five §3.5 terms are the only authored
set and every other domain's context vocabulary arrives injected.

#### Task 11: §3.7 facet ranking — word boundary, positional weight, score and margin

**Files:** create `src/facts/facets.py`; test `tests/p6/test_p6_facets.py`.

**Interfaces:**
- Consumes: `facts.evidence`, `evidence_shape.vocabulary.ZONES`, `facts.unresolved.write_unresolved`.
- Produces: `Candidate(value, score, evidence_refs)`, `word_boundary_match(needle, haystack) -> bool`,
  `rank(candidates, *, zone_weight, tier_weight) -> tuple[Candidate, ...]`,
  `fill_or_abstain(conn, *, file_id, content_hash, field_key, candidates, minimum_score,
  minimum_margin) -> str | None` — every threshold and weight a required keyword with no default.

**Done-means:** 7, 9.

**What its tests must prove.** That `submit` produces no `MIT` fact and `uncertainty` produces no
`UNC` fact — A01 and A02 as built, and a Done-means assertion in the design's own words. That two
candidates within the margin of each other fill **nothing** and write `reason = below_margin`, and
that failing the minimum score writes `reason = below_score_threshold` — two different refusals, not
one. That ranking is over **all** candidates and never first-match. That a value in a `filename` or
`title` zone outranks the same value in `header_footer` or a late `body` page, driven by an injected
`zone_weight` map over P4's fifteen zones — and that the weights themselves are injected, because
§3.7's numbers are Deferred and inventing them here is the failure mode this plan exists to avoid.
**And that the result does not depend on P4's read order:** the same candidate set shuffled into
every permutation produces an identical outcome, including the tie case, because `rank` imposes its
own total order (score descending, then `observation_key` ascending) before `fill_or_abstain` looks
at the first element. Without this, a tie is broken by whichever run was written first and §8.5's
replay reports a regression when nothing changed.

#### Task 12: §3.10 dates and academic terms — explicit patterns, no fuzzy parsing

**Files:** create `src/facts/dates.py`; test `tests/p6/test_p6_dates.py`.

**Interfaces:**
- Consumes: `facts.evidence`, `facts.facets.fill_or_abstain`.
- Produces: `DatePatterns` — an injected frozen dataclass of compiled patterns with the three named
  academic-term patterns required; `date_candidates(observation, *, patterns) -> tuple[Candidate, ...]`;
  `parse_exact(raw, *, pattern_id) -> str`.

**Done-means:** 10.

**What its tests must prove.** That `v2024`, a build number and a ZIP code each produce **no** date
fact, and that `Spring 2025`, `AY 2024-25` and `Michaelmas Term 2024` each produce **exactly one**
term fact — A03's case and the design's own worked list. That each of the three academic terms is
matched by a **dedicated** pattern rather than by generic parsing, asserted by pattern identity in
the result rather than by the value alone. That no fuzzy path exists anywhere: runtime introspection
finds no `dateutil`-style parser, no bare four-digit-year regex reachable without a pattern id, and
no fallback that accepts a candidate a pattern rejected. That the catalogue beyond the three named
patterns is injected and empty by default.

#### Task 13: §3.11 domain activation, and several domains on one file at once

**Files:** create `src/facts/domains.py`; test `tests/p6/test_p6_domains.py`.

**Interfaces:**
- Consumes: `facts.fields.DOMAIN_FIELDS`, `facts.file_facts.facts_for_file`.
- Produces: `active_domains(conn, *, file_id, content_hash, activation_signals) -> frozenset[str]`,
  `active_field_allowlist(conn, *, file_id, content_hash, activation_signals) -> tuple[str, ...]`,
  `ActivationSignals` — injected, no defaults.

**Done-means:** 14.

**What its tests must prove.** That the universal set applies to every file and a domain schema
activates only when evidence indicates that domain is plausible, so `target university` is not a
field every file is expected to have. That **one file simultaneously holds four facts across two
domains** with no field dropped and no domain forced to win — §3.11's own worked case. That the
activation signals are injected and that P6 authors none of them: which evidence activates which
domain is Deferred, and a default here would be P6 answering it. That the allowlist this produces is
the same object Task 17 hands to P8, so the model *"can only propose facts that belong to the active
domain schema"* is one computation and not two.

---

### Wave C — the three fact families P6 was handed (14–16 parallelise)

#### Task 14: Duplicate family and version family (G5)

**Files:** create `src/facts/families.py`; test `tests/p6/test_p6_families.py`.

**Interfaces:**
- Consumes: `facts.evidence` (the perceptual-hash observation), `database_agent.files_table.get_file`,
  `facts.file_facts.write_fact`, `facts.unresolved.write_unresolved`.
- Produces: `duplicate_family(conn, *, file_ids) -> tuple[str, ...]`,
  `version_family(conn, *, file_ids, lineage_rule) -> tuple[str, ...]`,
  `PERCEPTUAL_HASH_LABEL: str` — the injected container-path label, not a literal.

**Done-means:** 23, 24.

**What its tests must prove.** That two byte-identical files share a `direct` duplicate-family fact —
§3.13 names the content hash a Direct source. That a perceptual-hash near-match yields at most
`possible`. That two files sharing only a `(1)` filename suffix share **no** family fact of either
kind — `report (1).pdf` and `invoice (1).pdf` share a suffix and nothing else (§8.3, §8.5). That a
version family requires **distinct** content hashes, so identical hashes are a duplicate family and
never a version family, and that a version-family fact is **never** `direct` — no explicit slot
states a version relation. That the lineage rule beyond the two hash inputs is injected and empty by
default, because §2.9 lists *"duplicate and version-family signals"* and defines neither.

#### Task 15: The bounded download session (G6)

**Files:** create `src/facts/session.py`; test `tests/p6/test_p6_session.py`.

**Interfaces:**
- Consumes: `database_agent.files_table.get_file` (`observed_timestamps`, `directory_position`),
  `facts.file_facts.write_fact`.
- Produces: `bounded_sessions(conn, *, file_ids, boundary) -> Mapping[str, str]`,
  `SessionBoundary` — injected, no defaults; `DOWNLOAD_SESSION_FIELD: str`.

**Done-means:** 25.

**What its tests must prove.** That a session-derived `download_session` fact is `possible` and that
**no code path can write it at any other state** — asserted by attempting to write it as `validated`
and requiring a raise, not by inspecting a call site. That it is absent from the proposal-eligible
read by construction. That no rule promotes it and no §3.7 margin raises it. That the fact is written
for the member file **only** and copies no other file's facts onto it (§3.9, §4.3). That
`destination_eligible` is `FALSE` for the field so a session can never become a folder level. That
the time window and what makes a session "tightly bounded" arrive as an injected `SessionBoundary`
with no default — §3.9 requires the clue and states no numbers.

#### Task 16: Photo events, and §2.6's media-type conflict (G7, M2)

**Files:** create `src/facts/photo_event.py`; test `tests/p6/test_p6_photo_event.py`.

**Interfaces:**
- Consumes: `facts.evidence` (EXIF observations and `signal_tier`), `facts.facets.fill_or_abstain`,
  `facts.file_facts.write_fact`, `facts.unresolved.write_unresolved`.
- Produces: `photo_events(conn, *, file_ids, clustering) -> Mapping[str, str]`,
  `media_type(conn, *, file_id, content_hash, tier_weight, minimum_score, minimum_margin) -> str | None`,
  `PhotoEventClustering` — injected, no defaults.

**Done-means:** 26, 27.

**What its tests must prove.** That a camera/time/GPS cluster produces a `validated` Photos `event`
fact — not `direct`, because no slot states the event, and not `possible`, because P9 requires a seed
fact to be Direct or Validated. That an image with no EXIF produces **none**, and that tier-3
screenshot signals never contribute to one. That tier-1 and tier-3 signals in conflict fill no
`media type` and write `reason = below_margin` — §2.6's *"conflicting signals should lead to
abstention rather than an invented classification"* stated in P6's vocabulary, resolved by the
ordinary §3.7 procedure and **not** by a new mechanism. That a **missing** EXIF signal contributes
nothing to either candidate, which is provable precisely because P5 writes no absence observation.
That OCR text density is never a screenshot signal — asserted by introspection that no `media type`
candidate is derived from a `text_unit` length. That the tier is read from
`Observation.signal_tier` and **never** re-derived from `extractor_name` or a field label (M2), and
that the tier-to-weight mapping is injected.

---

### Wave D — the seams (17–23 parallelise)

#### Task 17: The P8 seam — what P6 supplies, and the consequence of each verdict (O6)

**Files:** create `src/facts/llm_seam.py`; test `tests/p6/test_p6_llm_seam.py`.

**Interfaces:**
- Consumes: `facts.domains.active_field_allowlist`, `facts.evidence`, `facts.file_facts.facts_for_file`,
  `facts.unresolved.write_unresolved`, `facts.states.is_stronger`.
- Produces: `FactRequest(file_id, content_hash, allowlist, citable_observations, existing_facts,
  normalizers)`, `Proposal(field_key, value, citations, unknown)`, `Verdict(passed, failed_check,
  reason)`, `FOUR_CHECKS: tuple[str, ...]`, `build_request(conn, ...) -> FactRequest`,
  `apply_verdict(conn, *, proposal, verdict, ...) -> str | None`.

**Done-means:** 11, 12.

**What its tests must prove.** That a proposal citing a quote absent from `evidence` produces no fact
and writes `reason = citation_absent_from_evidence`; that a proposal naming a field outside the
active schema produces no fact and writes `reason = field_not_in_active_schema`; that a proposal
contradicted by an existing `direct` or `validated` fact produces no fact and writes
`reason = contradicted_by_stronger_fact`; that a value that cannot be normalized safely writes
`reason = normalization_failed`; and that an explicit `unknown` writes `reason = model_returned_unknown`
— five verdicts, five reasons, no shared "rejected" bucket. That a proposal that is useful but too
weak becomes at most `possible` and is therefore absent from the proposal-eligible read. That P6
supplies the four inputs and owns none of the checking: `apply_verdict` takes a `Verdict` it did not
compute, so P8 can be built against this shape. **And that all of it works with P8 absent** — the
whole module is exercised with hand-authored `Verdict` fixtures and no model configured.

#### Task 18: Supersession, and the `preferred` pointer (M1)

**Files:** create `src/facts/supersede.py`; test `tests/p6/test_p6_supersede.py`.

**Interfaces:**
- Consumes: `database_agent.supersede.mark_superseded`, `chain`; `facts.file_facts`, `facts.states`.
- Produces: `supersede_fact(conn, *, old_fact_id, new_fact_id, reason) -> None`,
  `preferred_fact(conn, *, file_id, field_key) -> sqlite3.Row | None`,
  `fact_history(conn, *, file_id, field_key) -> list[sqlite3.Row]`.

**Done-means:** 29, and the history half of 15.

**What its tests must prove.** That a superseding fact carries `preferred = true` and the superseded
row `preferred = false`, and both rows, both states and both evidence chains remain readable — §8.2's
worked example, run end to end: a first pass that yielded nothing (now an `unresolved` row with
`reason = no_candidate_evidence`, not an absence) and a later pass that recovers a value. That
`preferred` is set **only** on supersession and **only** by the resolver — never by a producer, never
by P8, never as a side effect of a proposal. That a `user_confirmed` fact is always the preferred row
for its `(file_id, field_id)` and that `preferred` never reverses §3.13's ordering. **That `preferred`
appears in no contradiction check, no margin comparison and no destination-eligibility decision** —
asserted by introspecting those three call paths for a read of the column, not by reading the code.
That `preferred` is not plan-versioned.

#### Task 19: `no_usable_facts`, the recorded pass, and the guard that makes the ordering checkable (M11)

**Files:** create `src/facts/usable.py`; modify `src/facts/schema.py`; test `tests/p6/test_p6_usable.py`.

**Interfaces:**
- Consumes: `facts.file_facts.facts_for_file`, `facts.unresolved.unresolved_for_file`,
  `evidence_shape.vocabulary.ANALYSIS_TIERS`.
- Produces: `no_usable_facts_for(conn, *, usable_threshold) -> Callable[[str, str], bool]` — a
  factory returning the exact `Callable[[str, str], bool]` P5 and the orchestrator already require;
  `record_pass(conn, *, file_id, content_hash, analysis_tiers: frozenset[str]) -> None`;
  `passes_for(conn, *, file_id, content_hash) -> tuple[frozenset[str], ...]`;
  `FactPassNotRun(Exception)`.

**Done-means:** 28, and the enforceable half of preamble rule 5.

**What its tests must prove.** That the returned callable's signature matches P5's requirement
exactly — two positional `str` params, `bool` return — verified by `inspect.signature`, the same way
`tests/p5/test_p5_ocr_policy.py` verifies P5's side, and that it therefore drops into
`run_wave2(..., no_usable_facts=...)` with no adapter. That it returns `False` for a file with one
active usable fact and `True` for a file whose evidence produced only `unresolved` rows. **That it is
computed from the fact tables and nothing else** — introspection asserts no text-quality heuristic,
no language check, no character-ratio test and no read of a `text_unit` anywhere in the module,
because §2.2 and §2.7 both forbid deciding it from text quality and A10 forbids
`triggered_by = "language_quality_heuristic"` by name. That the threshold is a required keyword with
no default.

**And the ordering guard, which is the point of the task.** `record_pass` writes a row saying *a P6
deterministic pass over this `(file_id, content_hash)` at these analysis tiers has completed*, and the
verdict is a function of that row:

- Asked about a `(file_id, content_hash)` with **no** recorded pass, it raises `FactPassNotRun` —
  never `True`, never `False`. A caller that consults during extraction fails loudly. The
  alternative the SPEC warns about (*"it would return `true` for every file"*) is unreachable because
  `True` is not a value this branch can produce.
- Asked after a pass at `analysis_tier = "native"`, it answers from the fact tables — this is the
  pass-3 gate.
- Asked after a pass that already included `ocr`, it still answers: a file whose OCR pass also
  produced nothing is a file with no usable facts, not a file to OCR again. **Nothing asserts the
  caller does not loop** — that was Task 26's, and Task 26 is cut. The non-looping property is owed
  with the four-pass wiring, and until then no caller consults this verdict at all.

That last bullet is the termination condition and it is a test, not a convention: the pass record
carries which tiers it covered, so "have we already tried OCR for this content hash" is a lookup
rather than a flag someone remembers to set.

**Why raise rather than default.** Returning `False` for an unrecorded pass would be safe (no OCR)
and would hide the bug forever — the current stub already does exactly that, which is why the defect
survived to now. Returning `True` is the corpus-wide OCR the SPEC names. Raising is the only option
that makes a wrong call sequence a failing test rather than a silent behaviour, which is the
project's stated decision criterion: *"the one that … makes a wrong outcome impossible rather than
merely unlikely, wins"* (`04-resolutions.md`, `10-i4-learning-ops.md`).

#### Task 20: §8.6 — the three ceilings, the degradation order, and the resolver that enforces it

**Files:** create `src/facts/budgets.py`, `src/facts/resolver.py`; test `tests/p6/test_p6_budgets.py`.

**Interfaces:**
- Consumes: `database_agent.budget.CEILING_KEYS`, `get_ceiling`; every producer module.
- Produces: `P6_CEILING_KEYS: tuple[str, str, str]` (`model.max_llm_calls_per_thousand_files`,
  `model.max_cost_per_scan`, `model.max_dossier_tokens_per_call`), `DEGRADATION_ORDER: tuple[str, str, str]`
  (`direct`, `rule`, `llm`), `FactResolver` — the one entry point, constructed with every injected
  strategy and threshold; `FactResolver.resolve(conn, *, file_id, content_hash) -> ResolveResult`;
  `deferred_counts(conn, ...) -> dict[str, int]`.

**Done-means:** 20 (the `budget_deferred` half).

**What its tests must prove.** That the resolver always attempts `direct`, then `validated`, and only
then — budget and privacy permitting — `llm_supported`, and that the order is asserted from the call
sequence rather than from a docstring. That on exhaustion P6 retains the evidence, writes
`reason = budget_deferred`, leaves the field `unknown`, and **does not substitute a weaker route for
a stronger one**: a field reachable only by LLM interpretation stays empty rather than being filled
from a `possible` clue, a below-margin candidate or a fuzzy date. §8.6 is unconditional here — *"cost
exhaustion must never turn into lower-quality automatic classification"*. That P6 can report how many
fact-resolution requests it deferred against each of the three ceilings. That the ceiling **values**
come from P1's store or an injected predicate and that no number appears in `facts`.

#### Task 21: §8.5 / B7 — the `factual_validation` envelope, through P2's live writer

**Files:** create `src/facts/stage_output.py`; test `tests/p6/test_p6_stage_output.py`.

**Interfaces:**
- Consumes: `eval_harness.vocabulary.STAGE_IDS`, `OUTCOMES`, `BUDGET_STATES`;
  `eval_harness.replay.StageResult`; `eval_harness.stage_output.record_stage_output`.
- Produces: `STAGE_ID: str` (`"factual_validation"`), `DIMENSION: str` (`"fact"`),
  `ENVELOPE_FIELDS: tuple[str, ...]`, `fact_stage_output(*, result: ResolveResult) -> dict`,
  `fact_version_axes(conn, ...) -> dict`.

**Done-means:** 20 (the outcome half), 21.

**What its tests must prove.** That `STAGE_ID == "factual_validation"` and is a member of P2's ten,
and that `DIMENSION == "fact"` — the two lists are deliberately different and using one where the
other belongs raises `UnknownStage` / `UnknownDimension`. That the envelope is exactly P2's
`StageResult` shape, asserted by constructing one from it, the same way P5's Task 17 does. That the
four P6 results map to the four outcomes: facts written → `produced`/`within_ceiling`; every
attempted field ended in a non-budget `unresolved` → `abstained`/`within_ceiling`; a ceiling stopped
the work → `deferred`/`ceiling_reached`; the stage failed → `error`. That the two are distinguishable
**from the records alone** — driven through P2's live `record_stage_output`, which already raises
when the pairing is wrong. That `subject_ref` is the content hash and `inputs[]` carries the
`subject_ref`s of the `extraction` stage outputs P6 consumed. That an envelope is emitted for a file
that produced facts **and** for a file that produced none.

#### Task 22: §8.7 correction learning — query before propose (I4)

**Files:** create `src/facts/learning.py`; test `tests/p6/test_p6_learning.py`.

**Interfaces:**
- Consumes: `database_agent.learning.learning_records`, `reset_cutoff`;
  `database_agent.events.CORRECTION_SCOPES`, `CORRECTION_FIELDS`.
- Produces: `PROPOSAL_CLASS: str` (`"fact"`), `basis_key(*, file_id, field_key, value_id) -> str`,
  `is_suppressed(conn, *, scope, subject_id, file_id, field_key, value_id) -> bool`,
  `record_correction(conn, *, action, scope, subject, polarity, ...) -> int`.

**Done-means:** none numbered; §8.7's obligations and I4's Done-means.

**What its tests must prove.** That before writing a `file_facts` row that would revive a rejected
claim, P6 queries `learning_records` for `proposal_class = "fact"` and
`basis_key = (file_id, field, value_id)`, and that an unreset reject leaves the `rejected` row in
place and does not re-propose. That a **different** `basis_key` at the same scope still emits, and a
reset at that scope and subject allows emission again. That the suppression survives a new plan
version — the store is a versionless projection over `events`, which is exactly why I4 required it.
That `basis_key` is serialized in **one** place, canonically, so the write and the read cannot drift.
That every correction record carries one of §8.7's six scopes, and that the two worked examples are
distinguishable: a file-scoped correction about one transcript does not teach the engine that all
transcripts belong there, while a repeated corpus-scoped rejection of author-affiliation evidence
lowers that role's weight across the corpus. That rejected facts persist with their evidence and are
never removed. That P6 performs no global training on the user's corpus — introspection finds no
aggregate write outside the scoped records.

#### Task 23: §8.8 plan versioning — what belongs to a plan version and what does not

**Files:** create `src/facts/plan_versions.py`; test `tests/p6/test_p6_plan_versions.py`.

**Interfaces:**
- Consumes: `facts.values`, `facts.file_facts`.
- Produces: `PLAN_VERSIONED: tuple[str, ...]` (`display_label`, `aliases`),
  `SHARED_ACROSS_PLAN_VERSIONS: tuple[str, ...]`,
  `display_label(conn, *, value_id, plan_version) -> str`,
  `set_display_label(conn, *, value_id, plan_version, label) -> None`.

**Done-means:** none numbered; §8.8's obligations.

**What its tests must prove.** That `fields`, value identity, `file_facts`, every evidence ref, every
reliability state and all supersession history are **shared** across plan versions — §8.8: *"The
evidence database remains shared across plan versions."* That the value's display label and aliases
**are** plan-versioned, so `UChicago` versus `University of Chicago` as a rendering choice changes
with the plan while the underlying value and every fact pointing at it do not. That creating a new
plan version re-resolves nothing, invalidates nothing and reclassifies nothing — asserted by
comparing the full fact table before and after, byte for byte.

---

### Wave E — the read surface, the guards, and the skeleton (last)

#### Task 24: The read surface published to neighbours

**Files:** create `src/facts/read_surface.py`; test `tests/p6/test_p6_read_surface.py`.

**Interfaces:**
- Consumes: every table module.
- Produces: `facts_for(conn, *, file_id, content_hash, states=None, domain=None) -> list[sqlite3.Row]`,
  `proposal_eligible(conn, *, file_id, content_hash) -> list[sqlite3.Row]`,
  `active_allowlist_for(conn, ...) -> tuple[str, ...]`,
  `values_with_counts(conn, *, field_key) -> list[tuple[str, int]]`,
  `evidence_chain(conn, *, fact_id) -> list[Observation]`,
  `history(conn, *, file_id, field_key) -> list[sqlite3.Row]`,
  `unresolved_for(conn, ...) -> list[sqlite3.Row]`,
  `event_facts(conn, ...)`, `session_facts(conn, ...)`, `family_facts(conn, ...)`,
  `is_destination_eligible(conn, *, field_key) -> bool`.

**Done-means:** 12, 13, and the read half of 19.

**What its tests must prove.** That `proposal_eligible` excludes `possible` **and** `rejected` and
that an `unresolved` row is absent from **every** read including this one — the two negatives §3.6
turns on. That an `authored_by` value is never returned as destination-eligible (§3.8). That
`evidence_chain` walks a fact back to its P4 observations through observation keys and that every
step resolves. That `values_with_counts` supports §5.5's *"three schools, five terms, twelve course
branches"* before the user commits. That `history` returns superseded rows. That no read returns a
path, a destination, a folder or a group — the same forbidden-substring assertion as Task 4, applied
to the read shapes rather than to the schema.

#### Task 25: The no-invention guard — every open question and every deferred row held open

**Files:** test `tests/p6/test_p6_no_invention.py`.

**Interfaces:**
- Consumes: every module in `facts`, by runtime introspection of `vars(module)`.
- Produces: nothing.

**Done-means:** none numbered; it is what makes the Deferred table true.

**What its tests must prove.** That no threshold, weight, gazetteer, regex catalogue, producer
string, resolution, aspect ratio, session window, GPS radius or usable-fact count exists as a
module-level constant anywhere in `facts` — by **runtime introspection**, not by source-text search,
because a source-text guard matches comments and docstrings. That every **still-open** question is still open, one named
test each: OQ3 (`purpose` universal or Applications-domain), OQ5 (Finance at launch), OQ6
(multiplicity), OQ8 (user-approved custom templates creating fields), OQ9 (group purpose onto
members), OQ10 (equal-rank contradiction).

**OQ4 and OQ11 are CLOSED and their guards must INVERT.** A guard asserting they are open fails the
day the decision is applied, which is the day this plan is executed — so the tests become:

- **OQ4 is closed as `subject` (D6).** Assert the catalogue carries a `subject` row and **no**
  `course` row, and that Done-means 4 resolves `subject = BUSIB 4300`. §3.11's word "course" is the
  design's prose for the same field and stays inside quotations; the stored key is `subject`,
  because a field key is a join handle and two spellings are two columns. The same rename has
  already been applied across `planning/domains/` (1,302 keys).
- **OQ11 is closed by D2.** Assert P6 publishes **no** sensitivity record of its own: P7's
  `ClassificationRecord`, keyed `(file_id, content_hash)`, is authoritative, `files.sensitivity_state`
  is its projection written through P1's `set_sensitivity_state`, and `Unreadable or unclassified`
  is a **gate outcome** that never enters that column. P6 holds no sensitivity vocabulary at all. That P6 imports nothing from a grouping, tree, placement or model module. That
`subsystem = "P6"` is written in exactly one place. That no module branches on `source_type` or
`extractor_name`. That catalogue 01 is not imported anywhere in `facts`.

#### Task 26: ~~The three-pass Wave-2 wiring — the orchestrator restructure~~ — **CUT (D5)**

> **Not built. Ratified by Joseph, 2026-08-21**, taking round 5's CUT 1 over the council's D5.
>
> The council was right that Task 26 **as written** must not land — round 4 executed it and found
> two of its four joins unbuildable. The wrong inference was that a *fixed* Task 26 must therefore
> land instead. It must not land at all yet.
>
> **Why.** §2.2's targeted-OCR clause is the one clause in that section written as permissive:
> *"a file that technically produces text but yields no usable facts **may** receive targeted OCR
> as a fallback"*. The `text_layer_absent` route is the `should`, and it is already built and
> unaffected. The `text_layer_broken` route — the only route this restructure exists to serve —
> cannot do anything in v1, because **no OCR engine is chosen**: `Readers.ocr_engine` defaults to
> `None` and `_ocr` returns `None` when it is unset.
>
> **Updated 2026-08-21 (later the same day): an engine IS now wired.** `src/readers/` ships Apple
> Vision, and §2.2's `text_layer_absent` route — the `should` — runs today: a scanned PDF reaches
> OCR with no P6 in the loop, proven end to end in `tests/readers/`. **The cut stands and its
> conclusion is unchanged, because the blocker was always P6 and is now ONLY P6.** What has expired
> is the *second* half of the argument: a guard for the broken route is no longer untestable for
> want of an engine, it is unreachable for want of a verdict. Recorded rather than quietly dropped —
> a decision left standing on a premise nobody rechecked is how it gets re-litigated later.
>
> **What stays.** `facts/usable.py` keeps `no_usable_facts_for(conn, *, usable_threshold)` and every
> test Done-means 28 names. That is the whole of the SPEC's read-surface obligation. What goes is
> the machinery that *sequences* it.
>
> **What is NOT done, deliberately.** Do not split `extractors.dispatch` into extra public entry
> points. Do not restructure `run_wave2` into four loops. Do not delete
> `orchestrator.TARGETED_OCR_UNAVAILABLE` — round 2's B-14 says Task 26 forgets to delete it, and
> the simplification is that it should not be deleted. Its docstring needs **one word changed**:
> the honest v1 statement is *no OCR engine is wired*, not *P6 has not run*.
>
> **What this deletes rather than fixes:** round 2's B-1 (CRITICAL), B-2, B-12, B-14, B-19 and
> missing-tasks 3 and 8; round 3's A1 (CRITICAL) and A12(a) and half of A17; and round 4's C-1
> (the `dispatch` split half), C-4 and C-6. Round 5 could not credit the round-4 three because it
> ran before round 4 was written — so its stated saving is **understated by three findings**.
>
> **When it is owed.** When an OCR engine is chosen (P5 NEEDS-JOSEPH 1). Re-adding is round 2's
> three-task split, run **against a live engine** — strictly better than building it now, because
> the guard can then actually be observed firing. `FactPassNotRun` keeps its `ContractViolation`
> base class regardless: that is right on its own merits and costs nothing while unused.
>
> The full cut text is preserved in git history at the commit that removed it.


#### Task 27: Deterministic operation, and the walking-skeleton P6 step

**Files:** test `tests/p6/test_p6_deterministic.py`, `tests/p6/test_p6_skeleton_step.py`.

**Interfaces:**
- Consumes: `facts.resolver.FactResolver`, `evidence_shape.fixtures.by_number`. **Not** the
  Task 26 wiring, which is cut (D5): the skeleton's P6 step resolves facts from stored evidence
  and does not run through `run_wave2`.
- Produces: nothing.

**Done-means:** 17, and the end-to-end half of 4.

**What its tests must prove.** That the whole of Done-means items 4–10, 13–16 and 18–27 pass with
**P8 absent and no model configured** — the Wave 2 requirement, asserted as one test that runs every
fact-producing path with the model callable unset and asserts none of them raises and none of them
silently produces an `llm_supported` fact. That the §3.2 fixture resolves end to end: filename
`Syllabus BUSIB 4300 Spring 2026.pdf`, PDF title `BUSIB 4300 Syllabus`, page-one heading
`Spring 2026` produce exactly the three facts §3.2 names, each with evidence refs to the observations
that supported it, and each observation's `raw_value` unchanged afterwards. That the segmentation
map's P6 step holds — *"P6 resolve it to ONE validated fact (course = X) with its evidence link"* —
driven from P4's fixture 1, whose `context_before` is what makes it resolvable at all (N-6, B8(a)).

---

## Coverage — every Done-means item to the task that proves it

All thirty items appear. Where an item cannot be proven by a test as written, it says so.

| # | Done-means (abbreviated) | Task | Note |
|---|---|---|---|
| 1 | `fields`/`values`/`file_facts` exist; no path, destination, folder or group column | 2, 3, 4 | schema-level assertion via `PRAGMA table_info` + forbidden-substring list |
| 2 | all six universal + `download_session` + six domain sets present, and no field outside them | 2 | Career/identity/medical/legal have no rows (S3) |
| 3 | a value auto-creates; a field cannot be created at runtime by any producer | 2 (negative), 3 (positive) | the LLM path is covered again in 17 |
| 4 | the §3.2 fixture produces exactly **subject**, term, work type with evidence refs, raws unchanged | 8, 10, 27 | **Unblocked by D6 — `subject`.** F2 was right and is ratified: §3.1, §3.2 and §3.12 all say `subject`; only §3.11's Academic row says `course`, and that is prose for the same field. The SPEC's Done-means 4 wording is superseded. **Still owed:** the fixture is not among P4's nineteen and must be authored |
| 5 | EXIF `DateTimeOriginal` → `capture date` as `direct`; EXIF observation still readable | 8 | **partly blocked — see findings F3:** `capture date` is not a field Done-means 2 permits to exist |
| 6 | resolves an unknown `source_type`, no per-format branching anywhere | 7, 25 | positive case in 7, introspection guard in 25 |
| 7 | `submit` → no `MIT`; `uncertainty` → no `UNC` | 11 | A01, A02 |
| 8 | course-code-shaped string with no context → no fact; with `"Syllabus — "` → one fact | 10 | N-6, B8(a), P4 fixture 1 |
| 9 | two candidates within the margin fill nothing | 11 | |
| 10 | `v2024`/build/ZIP → no date; the three named terms → one term fact each | 12 | A03 |
| 11 | LLM proposal with absent citation / foreign field / contradicted → no fact | 17 | driven by authored `Verdict` fixtures, P8 absent |
| 12 | a `possible` fact is absent from the proposal-eligible read; a session clue never exceeds `possible` | 15, 24 | |
| 13 | an `authored_by` value is never returned as destination-eligible | 9 (rule), 24 (read) | |
| 14 | one file holds `project`, `document type`, `purpose`, `target university` at once | 13 | **partly blocked — see findings F4:** `document type` is not a field Done-means 2 permits to exist |
| 15 | bumped extractor version or changed prompt fingerprint → new fact supersedes; old readable with reason | 6, 18 | |
| 16 | rename with unchanged hash → no re-resolution; content change → re-resolution | 6 | |
| 17 | items 4–10, 13–16, 18–27 pass with P8 absent and no model | 27 | |
| 18 | every refusal in 7–12 also writes an `unresolved` row naming field and reason | 5, and asserted again in 9, 10, 11, 12, 16, 17 | each producer's test asserts its own reason |
| 19 | an `unresolved` row is absent from every read, carries no value, is not a `possible` | 5, 24 | |
| 20 | ceiling → `budget_deferred` + `deferred`/`ceiling_reached`; evidence refusal → `abstained`; distinguishable from records alone | 20, 21 | P2's writer already enforces the pairing |
| 21 | a `stage_output` with `stage_id = factual_validation`, populated `inputs[]`, version tuple, for a file with facts and one without | 21 | **partly reshaped — see findings F7:** the envelope field is `version_tuple_ref`; P6 supplies axes, P2 assembles |
| 22 | `python-docx` → no fact anywhere + one `discounted_tool_metadata` row; a human name → `authored_by` only, never destination-eligible | 9 | **contradicted by A04 as built — see findings F5** |
| 23 | two byte-identical files share a `direct` duplicate family; two sharing a `(1)` suffix share none | 14 | A06 is filed under `dimension: grouping`, so P6 cannot claim it as its own gate |
| 24 | distinct hashes never get a version family from a suffix alone, and never a `direct` one | 14 | |
| 25 | a `download_session` fact is `possible`, absent from the proposal-eligible read, promoted by no rule | 15 | |
| 26 | a camera/time/GPS cluster → `validated` Photos `event` usable as a P9 seed; no EXIF → none | 16 | |
| 27 | tier-1 vs tier-3 conflict fills no `media type` and emits `below_margin`; missing EXIF contributes nothing | 16 | **A07 names the field `kind`, which does not exist — see findings F6** |
| 28 | `no_usable_facts` false with one usable fact, true with only `unresolved`; computed from the fact tables, no text-quality heuristic | 19, 26 | 19 owns the verdict and the `FactPassNotRun` guard; 26 owns the four-pass caller that makes the guard never fire (F1) |
| 29 | superseding fact `preferred = true`, superseded `false`, both readable; `preferred` in no contradiction check, no margin, no destination decision | 18 | |
| 30 | every `evidence_refs[]` entry is an `observation_key`; a bumped extractor version leaves every reference resolvable | 4 (write), 7 (resolve) | provable because `observation_key` excludes `extractor_version` |
| — | **Preamble rule 5** — the verdict is never consulted before a recorded pass; targeted OCR fires once and only for files P6 could not resolve; pass 4 supersedes | 19, 26 | not a numbered Done-means item; it is the SPEC's `no_usable_facts` constraint made enforceable (F1) |
| — | **P6 depends on no P4 read order** — the same candidate set in any permutation produces the same fact | 11, 25 | verified by execution that `observations_for_file` is insertion order (F16) |

**Items whose test is blocked on a decision, not on work:** 4, 5, 14, 22, 27. Each is blocked by a
name — a field the SPEC's Done-means uses that the SPEC's own `fields` catalogue forbids from
existing, or an adversarial fixture asserting the opposite tier. They are findings, not gaps to paper
over, and each is written up below with the options and a recommendation. **The plan is buildable
without them settled** — every one of the five has a test that passes under either reading once the
name is chosen; none of them changes a module boundary.

---

## Deferred — manual design required

Carried verbatim from the SPEC's Deferred table, plus the three this decomposition adds. Nothing here
is invented. Every row is a caller-supplied strategy or a required keyword with no default, guarded
by Task 25.

| Deferred item | Defined by | Held by |
|---|---|---|
| The 200–300 domain template library (fact-schema half) | §5.7 | Task 2 — the catalogue is the six §3.11 rows and no more |
| **Career and recruiting** fact-schema fields | §3.15 names it a launch domain; §3.11 gives it no field row | Task 2 — S3 |
| **Identity, medical, legal** fact-schema fields | §3.15 | Task 2 — S3 |
| The "several additional fields used only for search, privacy protection, explanation, or later review" | §3.11 | Task 2 |
| Gazetteer contents and the validation procedure that makes them "validated" | §3.7 | Task 11 — injected |
| Minimum score and minimum margin values | §3.7 | Task 11 — required keywords, no defaults |
| Positional weight per document zone | §3.7, §2.2 | Task 11 — injected `zone_weight` over P4's fifteen zones |
| Rule context-term lists beyond the five literal academic terms | §3.5 | Task 10 — injected |
| Date and academic-term regex catalogue beyond the three named patterns | §3.10 | Task 12 — injected `DatePatterns` |
| Per-field normalizers and alias tables | §2.8, §3.6 | Tasks 3, 17 — injected |
| Domain activation signals | §3.11, §5.7 | Task 13 — injected `ActivationSignals` |
| Allowed value sets for enum-like fields | §3.11 | Task 2 — `value_kind` present, contents open |
| `destination_eligible` assignment beyond the §3.8 authorship rule | §3.8, §3.11 | Task 2 |
| Residual library contents beyond the nine §7.3 names | §7.2–§7.4 | **P10** (M10) — not P6 |
| **Tool-generated producer/creator string list** | §2.2 | Task 9 — catalogue 01 exists (115 entries) and is **injected**, never imported |
| **The `no_usable_facts` threshold** | §2.2, §2.7 | Task 19 — required keyword, no default |
| **Version-family signals beyond content hash and perceptual hash** | §2.9, §8.3 | Task 14 — injected `lineage_rule` |
| **Bounded-session boundary parameters** | §3.9, §4.2 | Task 15 — injected `SessionBoundary` |
| **Photo-event clustering parameters** | §2.6, §4.2 | Task 16 — injected `PhotoEventClustering` |
| **Signal-tier weights for §2.6's three bands** | §2.6, §3.7 | Task 16 — injected `tier_weight` |
| **NEW — the explicit-slot name map** (`DirectSlots`) | §3.5 names four slots; P5 spells no slot name | Task 8 — a catalogue that does not exist yet; see findings F8 |
| **NEW — the metadata property names the discount rule reads** | §2.2, §2.3, P4 D7 | Task 9 — catalogue 01 carries a `property_names` block; it is data, not a P6 constant |
| **NEW — the `basis_key` serialization for I4's `(file_id, field, value_id)`** | I4 | Task 22 — one canonical serialization, one place |

## Open questions — Joseph's, and unchanged

Quoted from the SPEC. **None is answered here.** Task 25 holds one named test per row.

| # | Question | Status |
|---|---|---|
| 1 | `analysis tier` is never defined | **Settled — I4.** `filesystem \| native \| ocr \| llm`, owned by P5, consumed here in §3.4's cache key. Verified present as `evidence_shape.vocabulary.ANALYSIS_TIERS` |
| 3 | *"Is `purpose` a universal field or an Applications-domain field? §3.9 requires it to be 'first-class'; §3.11's universal list omits it and places it only under College applications."* | **OPEN** |
| 4 | *"Are `subject` (§3.1's `subject = BUSIB 4300`, §3.12's field list) and `course` (§3.11's Academic row) the same field under two names, or two fields?"* | **CLOSED — D6, 2026-08-21. One field, and its key is `subject`.** Done-means 4 is unblocked. §3.11's "course" is prose for the same field and stays inside quotations. Task 25's guard **inverts**: it asserts the catalogue has a `subject` row and no `course` row |
| 5 | *"Finance has a fact schema in §3.11 but is a safety domain in §3.15 … Does the Finance fact schema activate at launch, or does detection-and-protection precede any field extraction?"* **[seam with P7]** | **OPEN** |
| 6 | *"Multiplicity. … May one (file, field) hold several simultaneously active values, and if so how does the §3.7 margin rule apply when more than one candidate is correct?"* | **OPEN** — `multiplicity` is a column with no answer |
| 8 | *"Does user approval of a custom template create `fields` rows, and at what scope — corpus-wide or plan-version-local?"* **[seam with P10]** | **OPEN** |
| 9 | *"After the user accepts the group, does that purpose become a fact on non-anchor members, or does it remain membership only?"* **[seam]** | **OPEN** — until settled, P6 writes nothing group-derived |
| 10 | *"§3.13 orders the six states but does not define the comparison for two equal-rank contradicting facts … Reject both, surface both as competing candidates, or defer to the internal score?"* | **OPEN** — Task 17's contradiction check refuses to decide and writes `unresolved` |
| 11 | *"`sensitivity status` is a universal fact (§3.11), a sensitivity state on the file record (§8.2), and a handling class in the privacy gate (§8.4). One record or three?"* **[seam]** | **CLOSED — D2, 2026-08-21.** P7's `ClassificationRecord`, keyed `(file_id, content_hash)`, is authoritative; `files.sensitivity_state` is its projection, written through P1's `set_sensitivity_state` (which now exists); `Unreadable or unclassified` is a **gate outcome** and never enters the column. **Residue, still open (NEEDS-JOSEPH C5):** whether P6 keeps a `sensitivity status` field row at all — round 1 F-2 found it has no producer. Create none until asked. *Original note:* P1's `files.sensitivity_state` column exists and **no code in `src/` writes it**. The orchestrator hit the same ambiguity and left a note in place of an answer (`orchestrator.py:277-285`): it had been passing `sensitivity_state` as P2's `handling_class` — *"a DIFFERENT field on a different record. Both are NULL on a live scan, so nothing failed and the name was still wrong"* — and now passes `None`. P6 owns the third name (`sensitivity status`, a §3.11 universal **fact**), so P6 is the part that makes it three |
| 12 | observations and facts sharing a reliability vocabulary | **CLOSED — ratified by Joseph 2026-08-20 (C1).** One vocabulary, six states; extractors stamp only `direct` and `possible` (P4 D11). Verified in code: `RELIABILITY_STATES` (6) and `EXTRACTOR_RELIABILITY_STATES` (2), enforced by conformance rule 3 |

---

## SPEC vs code — mismatches found

Reported, not unilaterally resolved. Every one was verified against the source on 2026-08-21, not
against a reconstructed stub. Ordered by how much they cost if missed.

**F1 (HIGH, and now planned rather than merely reported). The orchestrator consults
`no_usable_facts` before P6 has run — a genuine cycle.** The SPEC is explicit: the verdict is
*"Defined only after P6's deterministic pass on that content hash has completed. Consulted earlier it
would return `true` for every file and trigger OCR on the whole corpus."* But `src/orchestrator.py`
threads `no_usable_facts` from `run_wave2:138` into `extract()` inside the per-file loop
(`dispatch.py:123`), which consults it through `document_ocr_decision`. Every current caller passes
`lambda f, h: False`, which hides the cycle behind a stub that always says "the text layer is fine".

**Blast radius, verified precisely.** It is narrower than "the whole corpus" and worse than it looks:

- The consult is reached **only on the PDF branch** — `dispatch.py:118-125`, guarded by
  `decision.extractor_name == pdf.EXTRACTOR_NAME`. DOCX has no OCR route by design
  (`dispatch.py:131-133`) and images use `image_ocr_decision`, which never consults P6.
- Within that branch it is reached **only when the PDF has non-empty text** —
  `ocr_policy.text_layer_state` returns `text_layer_absent` before calling the verdict when
  `_has_text(result)` is false. So a scanned PDF routes to OCR without asking P6, correctly.
- So the affected set is **every text-bearing PDF in the corpus**, and a naive P6 (no facts yet, so
  "no usable facts" is true) reports `text_layer_broken` for all of them → targeted OCR on every
  text-bearing PDF. In a real personal corpus that is most of the documents that matter.
- Bounded today only by `readers.ocr_engine is None` (`dispatch.py:86-88`), which makes `_ocr`
  return `None`. That is a second stub doing the same job as the first.

**The sharper statement of the defect, which decides the fix.** At the consult point the evidence
does not exist yet. `document_ocr_decision` runs on the in-memory `ExtractionResult`; `_write(sink,
result, written)` does not run until `orchestrator.py:211`, after `_extract_one` returns. So P6 is
being asked about observations that have not been handed to P4 — `observations_for_file` returns
nothing for that run. A correctly-implemented P6 could not answer even if the ordering were fixed
by moving the call one line; the extract step has to **split**, which is why this is a shape change.

**What the plan does about it.** Preamble rule 5 states the four passes. Task 19 makes P6 raise
`FactPassNotRun` when asked about an unrecorded pass — so too-early consultation is a failing test,
and the `True` the SPEC warns about is not a value that branch can produce. **The caller-side
half — rewiring `run_wave2` into the four passes — is CUT (D5).** The guard therefore protects P6's
own read surface and nothing consults it from the caller; see the note under preamble rule 5.

**F2 (HIGH) — RESOLVED by D6, 2026-08-21. `subject` wins; the analysis below is what the decision
rests on and is kept for that reason.** The SPEC's Done-means 4 is superseded where it says `course`.
Original finding: §3.2, verbatim: *"the system can create facts such as **subject** = BUSIB 4300, term =
Spring 2026, and work type = syllabus."* §3.1 says the same: *"A fact is a statement such as
**subject** = BUSIB 4300"*. §3.12's fields-table list also names *"subject, purpose, target
university, project, event, or sensitivity"*. But Done-means 4 says P6 produces *"exactly the three
facts §3.2 names (**course**, term, work type)"*, and the `fields` catalogue carries `course` (from
§3.11's Academic row) and **no `subject` row at all** — while OQ4 leaves the question explicitly
open. Three consequences: the design's own words for §3.2's worked example cannot be satisfied by the
catalogue Done-means 2 permits; §3.12's fields list names two fields (`subject`, `purpose`) that the
catalogue omits; and the walking skeleton's line *"P6 resolve it to ONE validated fact (course = X)"*
picks the same side. **The design wins where they disagree, and the design says `subject` in §3.1,
§3.2 and §3.12 and `course` only in §3.11's Academic row.** ~~Not resolved here — it is OQ4 and it
is Joseph's.~~ **Resolved: Joseph ratified `subject` (D6, 2026-08-21).** §3.11's "course" is prose
for the same field and survives inside quotations; the stored key is `subject` everywhere.

**F3 (HIGH). Done-means 5 requires a field Done-means 2 forbids from existing.** Item 5: *"An EXIF
`DateTimeOriginal` observation produces `capture date` as a `direct` fact."* Item 2: the catalogue is
the six universal fields, `download_session`, and the six §3.11 domain sets, *"and no field outside
them"*. **`capture date` is in neither list** — the universal set has `creation date` and the Photos
row has `capture year`. §3.1 and §3.2 both use `capture date = 2026-07-17` as the worked example, so
this comes straight from the design.

**RESOLVED 2026-08-22 — they are TWO fields and the design uses both deliberately.** Counted in
`00`: *"capture date"* appears three times and always as a FACT WITH A VALUE — §3.1's
`capture date = 2026-07-17` beside `subject = BUSIB 4300`, and §3.2's *"an EXIF field called
DateTimeOriginal is raw metadata; capture date = 2026-07-17 is the file fact derived from it"*.
*"capture year"* appears once, in §3.11's Photos sentence, among that domain's DESTINATION
dimensions. A photo tree branches by year; the fact is the date.

So: **`capture_date` is a `direct` fact derived from EXIF (Done-means 5), and `capture_year` is the
Photos destination dimension derived from it.** Neither is `creation_date`, which §3.2 separates
explicitly as the filesystem/document timestamp. Done-means 2's list gains `capture_date`; this is
not "a seventh field" smuggled in but the field Done-means 5 always required.

**Cross-check against R1a.** `planning/domains/canonical_fields.json` carries `capture_year` and
**not** `capture_date` — correct for a roster whose job is destination dimensions, and a real gap for
P6, whose job includes facts. Reported rather than edited: that file is another agent's.

**F4 (HIGH). Done-means 14 requires a field that does not exist either.** It asserts one file holds
*"`project`, `document type`, `purpose`, and `target university`"*. §3.11's prose worked case says
*"`document type` = abstract"*, but §3.11's **field table** gives College applications
*"application document type"* and Research *"artifact type"*. **There is no `document type` field.**

**RESOLVED 2026-08-22 — `document type` is the design's GENERIC WORD for whichever specific field
the active domain declares, and it is never itself a key.** `00` uses it twelve times, including
*"project = PVA/RDP and document type = abstract"* — a research artifact, so that instance is
`artifact_type`. College applications declare `application_document_type`. Two keys, one prose word,
no third field.

**Done-means 14 should therefore read `project`, `artifact_type`, `purpose`, `target_university`** —
the case it describes is a research artifact that also carries an application purpose, which is
exactly §3.1's "a file can simultaneously be" point.

R1a already carries `"document type"` as an **alias** of `application_document_type`. It belongs on
`artifact_type` as well, since §3.x's own worked example maps there. Reported, not edited.

**F5 (HIGH). Adversarial case A04 as built asserts the opposite of the SPEC's suppression tier.**
`tests/eval/fixtures/adversarial/A04.json` is worded *"generic author metadata (`python-docx`,
`Mozilla/5.0`, browser producer strings)"* and carries `expected_outcome_kind: "produced"` with
`expected_value: {"retained_as": "supporting_evidence"}` and
`forbidden_value: {"used_as": "destination_dimension"}`. That is the SPEC's **Demotion** tier. But
the values it names by name are the **Suppression** tier, where the SPEC requires *no fact in any
field* and one `unresolved` row — which is `abstained`, not `produced`. A04 and Done-means 22 cannot
both pass. The case is P2's fixture and P6's gate; one of the two must move.

**F6 (MEDIUM). Adversarial case A07 names a field that does not exist.**
`forbidden_value: {"field": "kind", "value": "screenshot"}`. P6's field for that is `media type`
(§3.11 Photos), and Done-means 27 uses `media type`. `kind` is outside the catalogue Done-means 2
closes. The assertion is right; the field name is not.

**F7 (MEDIUM). The SPEC's envelope description does not match P2 as built.** The SPEC says P6 emits
a `stage_output` carrying *"the version tuple"*. P2's envelope field is **`version_tuple_ref`**, a
`sha256:` content ref; the seven-field tuple lives in its own table and is assembled by
`eval_harness.run.record_version_tuple` from six axes plus `analysis_tiers_enabled`, of which P6 owns
`prompt_fingerprint`, `model_identifier` and a slice of `extractor_versions`. This is exactly P5's
SPEC-vs-design item 5, unfixed and now inherited by P6. **The SPEC's wording should say "its axes of
the version tuple."** The plan builds it that way and the requirement is met either way.

**F8 (MEDIUM). Done-means 5's `DateTimeOriginal` has no publisher.** P5 emits every image observation
as `source_type="image"`, `extractor_name="image.metadata"`, `zone="metadata"`, with the EXIF tag name
carried **only** as a reader-supplied `container_path` segment label — P5 spells no EXIF tag name
anywhere, deliberately (P4 D7: *"the source format's own slot name, verbatim"*). P4's fixture 7 uses
`"DateTimeOriginal"`, but a fixture is not a vocabulary. So P6 cannot match the slot without either
hard-coding a string P5 refused to publish, or receiving an injected slot-name map. **The plan
injects it (`DirectSlots`, Task 8) and reports that the catalogue behind it does not exist.** It is
the same shape as catalogue 01 and belongs beside it.

**F9 (MEDIUM). P6's SPEC promises three event types P1's vocabulary does not have.** Under
Provenance: *"Value creation, value merge/alias, and user fact correction are also P6 actions and are
appended with the same record shape."* P1's `RESERVED_EVENT_TYPES` (19) and `_REGISTERED` (16) contain
**none of the three**, and `append_event` raises `UnregisteredEventType` for an unknown type.
Registration is a source edit to P1's `_REGISTERED` and B5 makes it a spec-level act. The SPEC applies
that discipline correctly to `unresolved` (*"P6 claims no new §8.2 event type for it"*) and then
promises three types for these. **The plan's interim is to ride value and correction records on
`fact creation` / `fact rejection` with the five `CORRECTION_FIELDS` populated**, which is what I4's
learning read requires anyway — but it is an interim, not an answer. See NEEDS JOSEPH 2.

**F10 (MEDIUM). §3.9 wants a folder name as strong purpose evidence; the SPEC's Contract in forecloses
it.** §3.9, verbatim: *"Purpose may be supported strongly by an existing user-created folder name or
explicit language in a form or portal."* The SPEC restricts P3 input to *"exactly two computations"*,
both for the bounded session, and says *"This is the only non-P4 input P6 accepts for fact
production."* Meanwhile `file_facts.origin` carries §3.1's `user-approved folder` as a listed value
with **no Contract-in that supplies it**. Either the parent-folder name is a purpose evidence source
(and the Contract in needs a third computation), or `user-approved folder` as an origin belongs to a
later part and should not be in P6's origin list yet. Not resolved here.

**F11 (LOW). Two different things are named `cache_key`.** `extractors.runs.cache_key(*, content_hash,
extractor_name, extractor_version, analysis_tier, config_fingerprint)` already exists and identifies
an *extraction result*. §3.4's key identifies a *fact* and has a different composition
(`model_identifier`, `prompt_fingerprint`; no `extractor_name`, no `config_fingerprint`). Task 6
asserts the two differ and that `facts` does not import P5's. Worth naming P6's `fact_cache_key` in
the SPEC so the collision is visible in prose too.

**F12 (LOW). P4 publishes no per-content-hash observation read.** Every P6 read is per *file version*
(§3.4, §8.2), but `evidence_shape.store` offers `observations_for_file(conn, file_id)` — which spans
content hashes — and `runs_for_content(conn, content_hash)` for runs only. P6 filters on
`observation.content_hash` in Task 7, in one place. **P4 should publish
`observations_for_content(conn, file_id, content_hash)`**; until it does, the filter is P6's and the
plan says where it lives.

**F13 (LOW). Two names for the P6 gate that a planner will conflate.** P2's **stage** is
`factual_validation`; P2's **dimension** is `fact`. Both are closed vocabularies with their own
guards (`UnknownStage`, `UnknownDimension`). Task 21 asserts both.

**F14 (LOW, informational). P4's fixtures use extractor names no P5 extractor emits.** Fixture 7 is
`image.exif`, fixtures 5 and 6 are `docx.text` / `docx.metadata`; real P5 emits `image.metadata` and
`docx.structure`. It costs P6 nothing — P6 must not branch on `extractor_name` at all — but it means
a P6 test written against a fixture and a P6 test written against a live P5 run see different values
in that column, and only the no-branching rule keeps that harmless. It is one more reason Task 7's
introspection guard is a test rather than a convention.

**F15 (LOW, informational). §3.2's fixture is not among P4's nineteen.** Done-means 4 needs filename
`Syllabus BUSIB 4300 Spring 2026.pdf`, PDF title `BUSIB 4300 Syllabus`, and page-one heading
`Spring 2026`. P4's fixtures 1 and 2 give a `heading` observation `BUSIB 4300` and a `title`
observation `BUSIB 4300 Syllabus`; there is **no** `Spring 2026` heading fixture and no such filename
fixture. P6 authors the three-observation set with P4's builders. Not a defect — the SPEC says
Done-means items are *"assertable against P4-shaped fixtures"*, not against P4's own nineteen — but
it is work Task 27 owns and a planner should not assume `by_number` supplies it.

**F16 (MEDIUM). P4's observation reads are in insertion order, which is not a property of the
corpus.** Verified by execution on 2026-08-21, prompted by the note that `observation_keys_for_run`
was random-UUID order until that morning. `observations_for_file` is `ORDER BY rowid`: writing
fixtures 1, 2, 3 as runs in that order returns `['BUSIB 4300', 'BUSIB 4300 Syllabus', 'Columbia']`,
and writing them 3, 2, 1 returns the reverse. Nothing in P4 is wrong here — insertion order is a
reasonable default and P4 makes no ordering promise about the corpus. But it means **any P6
computation that reads a P4 sequence and acts on its order is write-order-dependent**, and §3.7's
margin rule is exactly such a computation: two candidates at the same score are separated by whichever
was written first. The consequence lands on §8.5 — a replay of the same bundle with runs written in a
different order compares as a fact-quality regression when nothing changed. P6 sorts before it ranks
(Global Constraints; Task 11 asserts it by shuffling; Task 25 asserts no module consumes a P4 read as
an ordered sequence without re-sorting). **Worth P4 stating in its read surface which orderings are
guarantees and which are incidental**, because the next consumer will make the same assumption.

## Does this change the orchestrator's shape

Yes, and the honest size of it is: **one loop becomes four, one parameter is added, one is removed,
and no existing call is deleted.** Concretely, against `src/orchestrator.py` as it stands:

| Today | After |
|---|---|
| `run_wave2(..., no_usable_facts: Callable[[str, str], bool], ...)` — line 138 | parameter **removed**; a new keyword-only `resolver` (P6's, no default) replaces it, and the orchestrator obtains the verdict from `resolver` so the two cannot drift apart |
| stage 2, lines 168–218: one loop doing route → `_extract_one` → `_write` → `set_extraction_status`, with OCR decided **inside** `extract()` | **loop 1** identical except the `text_layer_broken` OCR branch does not fire; **loop 2** P6 resolves and records the pass; **loop 3** targeted OCR only where the verdict is true; **loop 4** P6 re-resolves those files |
| `extract(..., no_usable_facts=no_usable_facts)` — line 119 | `extract()` keeps its signature. The orchestrator passes a verdict that raises `FactPassNotRun` in loop 1 and the real one in loop 3, so the `text_layer_absent` path (which never consults it) is unchanged and the `text_layer_broken` path cannot fire early |
| stage 2b (dataless), lines 219–245 | unchanged |
| stage 4 (P2 bundle), lines 247–267 | unchanged in structure; it now runs after four loops instead of two, and P6's facts exist before `seal_bundle` |

What does **not** change: `extract()`'s signature, `dispatch.py`, `ocr_policy.py`, every P5 extractor,
P4's writers, and `route`/`_write`/`set_extraction_status`. The split is at the orchestrator level
because that is where the pass boundary is; nothing inside P5 has to learn about it.

What it costs when nothing is wired: **nothing.** With `readers.ocr_engine is None` — every test
today, and any deployment that has not chosen an OCR engine — `_ocr` returns `None`, loops 3 and 4
are empty, and the corpus resolves from native evidence in loops 1 and 2.

**Superseded 2026-08-21/22.** `src/readers/` now wires Apple Vision, so `ocr_engine is None` is no
longer the universal case and this paragraph's premise has expired. It does not revive Task 26: the
`text_layer_absent` route needs no verdict from P6 and already runs, and the `text_layer_broken`
route still waits on P6 itself.

One scheduling note, now void: Task 26 was the only task touching a file P6 does not own, and it
is cut (D5). Every remaining task is inside `src/facts/` and `tests/p6/`.

## SPEC vs design — where §3 and the SPEC disagree

**D1. §3.2's worked example names `subject`; the SPEC's Done-means names `course`.** Full text in
F2. **CLOSED (D6, 2026-08-21): the design wins and the field is `subject`.** The SPEC's Done-means 4
is superseded on this word. Note this is design-disagreement D1 and is unrelated to decision D1.

**D2. §3.1/§3.2 name `capture date`; §3.11's table has `capture year`.** Full text in F3. The design
uses both, in different sentences, which is why this is a question and not a correction.

**D3. §3.11's prose names `document type`; §3.11's table names `application document type` and
`artifact type`.** Full text in F4. Same shape as D2: the design's prose and the design's own table
disagree with each other, and the SPEC inherited the prose in Done-means 14 and the table in the
`fields` catalogue.

**D4. §3.3 lists four validator checks; §3.6 lists four; they are not the same four.** §3.3: *"the
validator then checks that the cited evidence actually exists, that the requested field belongs to
the active schema, that stronger rule-based evidence does not contradict it, and that the result is
appropriate for a proposal rather than merely a search hint."* §3.6: field in schema · cited quote
present · value normalizes safely · no stronger fact contradicts. §3.3's fourth check
(*"appropriate for a proposal rather than merely a search hint"*) is a **fifth** distinct test, and
§3.6's "value normalizes safely" is absent from §3.3. The SPEC takes §3.6's four and folds §3.3's
fourth into the useful-but-weak rule, which is a defensible reading and is what Task 17 builds — but
it is a reading, and it is worth recording that the design states the check list twice and differently.

**D5. §3.5's five context terms are introduced with "such as".** *"academic context such as
'syllabus,' 'lecture,' 'credits,' 'instructor,' or 'semester.'"* The SPEC calls them *"literal and
required"* in Production rules and *"the five literal academic terms"* in Deferred, which is the right
handling of the floor — but "such as" is the same construction B5 read as **opening** §8.2's event
list and the SPEC itself read as opening §3.11's universal field list. Read consistently, the five
are a floor and not a closed set. The plan treats them as required-and-extensible (Task 10, injected),
which satisfies both readings; the SPEC's two phrasings could be aligned.

---

## NEEDS JOSEPH

Manual input required. Each states the question, the § that raises it, what the design does and does
not say, the options, and a recommendation. **None is answered in code.**

**1. ~~The `no_usable_facts` ordering conflict.~~ Planned, not asked — the four-pass structure in
preamble rule 5 is the answer, and Tasks 19 and 26 build it.** What remains for you is narrower and
is a scope question, not an ordering one: **does targeted OCR ship in v1 at all?** The four passes
cost nothing while `readers.ocr_engine is None` (loops 3 and 4 are empty), so the restructure is
worth doing either way. But §2.2's targeted-OCR route only ever does anything once an OCR engine is
chosen, which is P5's still-open NEEDS JOSEPH 1 (*"Apple Vision only, macOS-only v1"*). *Options:*
(a) build the four passes now and wire an engine when P5's question is settled — the restructure is
free and the seam is proven. (b) Build the four passes now and ship v1 with no engine, so
`text_layer_broken` is recorded as a state and never acted on. (c) Defer the restructure until an
engine exists — which leaves `no_usable_facts` stubbed and the cycle live in the code. **Recommendation:
(a).** (c) is the status quo and it is the thing that let this survive undetected; the cost of (a) is
one orchestrator diff against a green suite.

**2. Three event types P6 needs and P1 does not have (F9). RESOLVED 2026-08-22: ride the existing
types; P6 mints none.** §8.2's reconstruction requirement is about being able to rebuild what
happened, and P1's existing vocabulary plus P6's own rows already carry that: a value creation is
visible as the `values` row itself, a merge as the alias row, and a user correction is keyed on
`proposal_class` + `basis_key` in §8.7's learning record rather than on an event type. **Minting
three new §8.2 types would put one concept in two homes** — the row and the event — which is this
project's most expensive defect, and P6's own discipline already refuses it for `unresolved` (*"P6
claims no new §8.2 event type for it"*). The SPEC must say so rather than leaving it implied.
Original finding: value creation, value merge/alias, and
user fact correction. *Options:* (a) register three new types in P1's `_REGISTERED` — a spec-level act
under B5, which is exactly how the sixteen SPEC-registered types got there. (b) Ride them on
`fact creation` / `fact rejection` with the five `CORRECTION_FIELDS` distinguishing them — which is
what I4's learning read needs anyway. (c) Decide they are not §8.2 events at all, as the SPEC already
decided for `unresolved`. **Recommendation: (b) for v1**, because it needs no P1 change and I4's read
already keys on `proposal_class` + `basis_key` rather than on event type — but say so in the SPEC
rather than leaving the Provenance section promising three types that raise at run time.

**3. The five naming questions that block five Done-means items (F2, F3, F4, F5, F6).** `subject` vs
`course`; `capture date` vs `creation date` vs `capture year`; `document type` vs `application
document type`; A04's tier; A07's `kind` vs `media type`. Each is one word and each is currently
asserted two different ways in two different places that both claim to be contract. **They should be
settled together**, because four of the five are the same underlying issue — the design states its
field names once in prose and once in a table, and the two do not match.

**OQ4 is settled (D6): `subject`. But the rule it establishes is NOT "prose wins"** — that was my
over-generalisation from a single case, and applying it blindly to the other three gives wrong
answers. R1a's canonical catalogue demonstrates the better rule, which is D6's actual mechanism:

> **One stored key per concept. Every other word the design uses for it becomes an ALIAS, never a
> second key.** Which word becomes the key is decided per concept on the evidence, not by a blanket
> precedence between prose and tables.

For `subject`/`course` the prose word won. For `document type` the *specific* words won and the
prose word is the alias. Both are the same rule. Applied 2026-08-22:

| | Resolution |
|---|---|
| **F3** `capture date` vs `capture year` | **Not a tie — two fields.** `capture_date` is the EXIF-derived fact (§3.1, §3.2); `capture_year` is the Photos destination dimension (§3.11). Both exist. |
| **F4** `document type` | **Not a key.** Generic prose for `application_document_type` (College apps) or `artifact_type` (Research/Code). Done-means 14 reads `artifact_type`. |
| **F5** A04 | **Fixture moved.** `python-docx` is a tool string — §2.2's suppression tier, not §3.8's demotion tier. Done-means 22 stands. |
| **F6** A07 | **Fixture moved.** `kind` → `media_type`. |

A04 and A07 are amended in `tests/eval/fixtures/adversarial/`; P2's 156 tests stay green.

**4. Which fields are `destination_eligible` beyond §3.8's rule?** §3.8 settles that no authorship or
creator-identity field ever is. Nothing settles the rest, and P10 cannot build a folder template
against a column nobody has filled. Not blocking P6 — the column exists and the authorship rule is
enforced — but it is the first thing P10 will ask for.
