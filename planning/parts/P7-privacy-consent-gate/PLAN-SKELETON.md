# P7 — Privacy and consent gate — Plan Skeleton

> **For plan authors:** this is the decomposition, not the plan. Each `### Task N` below is a
> contract for one author to fill in with **complete** test code and **complete** implementation
> code, in the format of [`../P4-evidence-shape/PLAN.md`](../P4-evidence-shape/PLAN.md) and
> [`../P5-extractors/PLAN.md`](../P5-extractors/PLAN.md). No placeholders, ever. A task that cannot
> be written out in full is a task that was decomposed wrong.

**Goal:** Build §8.4 as the **only door** through which file content may reach a model or an external
connector — the five handling classes, the four operation modes, the always-local set, the six
releasable item kinds, `Gate.release` and its three-branch return, the consent-aware audit record,
revocation, the automatic-move predicate and the display policy — so that P8 can be built against
P7's fixtures before P7 ships, and so that a call which bypasses the gate is not a policy violation
to be caught in review but a call that **cannot be constructed**.

**Architecture:** P7 is a sixth package, `src/privacy/`, alongside `database_agent` (P1),
`eval_harness` (P2), `scan_agent` (P3), `evidence_shape` (P4) and `extractors` (P5), inside P1's
single local SQLite database (§0: *"Each part owns its own tables within it"*). It owns the policy,
consent-grant and release-ledger tables; it owns **no** classification table — the classification is
written through P6's `sensitivity` field, and P6 does not exist, so that seam is an **injected
protocol with a fixture implementation** exactly as P5 injected `no_usable_facts`. P7 reads P4's
evidence through P4's published readers and is the **one and only** place in the repository where an
`(observation_key, span)` becomes a string of document text.

**Tech Stack:** Python 3.12 · stdlib only (`sqlite3`, `json`, `hashlib`, `uuid`, `dataclasses`,
`inspect`, `secrets`) · `pytest` · P1/P2/P4/P5 as the substrate · no third-party runtime dependency.
P7 adds no `pyproject.toml` change: `[tool.setuptools.packages.find] where = ["src"]` already
discovers `privacy`, and `pythonpath = ["src"]` already makes it importable under pytest.

---

## Read this before Task 1 — the rules that decide whether this part is correct

### 1. There are now three refusals in this product, and they are not the same refusal

Conflating them is the single most likely way this part goes wrong, because all three are called
"the gate" in conversation and only one of them is P7's.

| # | Refusal | Owner | What it refuses | What gets written |
|---|---|---|---|---|
| 1 | **Protected container** (11 §4b, P3 SPEC) | P3 / P5 `safety.admit` | *Reading, at all.* | **Nothing at all.** No `files` row, no `content_hash`, no run row. The exclusion verdict is the whole record. |
| 2 | **Dataless file** (11 §5) | P3 / P5 `safety.admit` | *Materializing, hashing, extracting.* | **One run row**, `completeness = dataless`, recording that the bytes are elsewhere. |
| 3 | **The privacy gate** (§8.4) | **P7** | *Release.* Not reading — the bytes were read locally, lawfully, long ago. | **An audit event**, `model_release_denied`, and no `Released`. |

The differences are load-bearing and each is stated by its own source:

- **Refusal 1 produces nothing because producing something would be the read the rule forbids.**
  P3's SPEC: *"P3 does not descend into one, does not stat its contents, does not hash a byte of it,
  and does not create a `files` row for anything inside it. P12 may never move one or anything
  within one, and no policy, approval, or user gesture makes it movable — this is not a default that
  review can override, which is what separates it from every other refusal in this design."* A run
  row needs a `file_id` and a `content_hash`; inside a protected container neither exists, so the
  row is not merely disallowed, it is **unconstructible**.
- **Refusal 2 produces one row because the file must stay visible as unfinished.** 11 §5: *"Do not
  materialize, hash, or extract."* The identity is already known, and §8.6 requires the UI to *"show
  the difference between completed work and deferred work"* and to avoid *"the false impression that
  an unprocessed file was understood and found unimportant."* C4's ninth `completeness` value
  exists so that line can say *31 files are in iCloud* instead of filing them under a word that lies.
- **Refusal 3 is the only one that is a policy.** It **can** be overridden — by the user, through
  consent, per §8.4's four options — which is exactly what makes it different from 1 and 2. This is
  why `NeedsConsent` exists and why refusals 1 and 2 have no consent branch. A P7 author who adds a
  consent path to a protected container has broken refusal 1; a P7 author who removes the consent
  path from a `Denied` has broken §8.4.

**Consequence for P7's code:** `src/privacy/` never calls `extractors.safety.admit`, never imports
`ProtectedContainerRefused` or `DatalessRefused`, and never re-derives a protected-container or
dataless verdict. Those are decided upstream and a file that failed either never acquires the
`(file_id, content_hash)` pair P7 keys on. Task 21 asserts the absence of both imports.

**Consequence for vocabulary:** `protected` (§8.4, the handling state) and `protected container`
(11 §4b, the filesystem rule) are **two different words that share a stem**. P3 already publishes
`exclusion.LABEL_UNTOUCHED_PROTECTED = "untouched_protected"` and
`exclusion.REASON_PROTECTED_CONTAINER = "protected_container"`. P7's `Denied.reason` vocabulary
contains `protected_cloud_target` and `protected_records_template` and **no bare `protected`**.
Task 2 pins all four spellings side by side so a later "normalization" pass cannot collapse them.

### 2. The gate keeps one job (C4)

C4, ratified in both P4's and P5's tables: *"the gate still raises and writes nothing — a gate that
also wrote would be doing two jobs."* In P5 this meant `admit()` raises and the **router** writes the
run row. In P7 it means something narrower and it must not be over-read:

- **`Gate.release` writes exactly one thing — the audit event — and it writes it because §8.4
  requires it, before the value is returned.** It does not write a classification, does not update
  `files.sensitivity_state`, does not write a `stage_output`, does not write a P2 assertion, does not
  write a placement decision, and does not write P8's `Refusal`. The `Refusal` is P8's record of
  having received a `Denied`; the caller is the catcher.
- **The catcher is the caller's**, everywhere. `Denied` → P8 writes its `Refusal` with reason
  `PRIVACY_GATE_REFUSED` (P8 SPEC). `NeedsConsent` → the calling part routes to P13, which collects
  a `review_action` with `action = select_consent_option` and routes the choice back to P7. P7's
  classification writers (`Gate.reclassify`) are separate entry points, invoked by a caller, and are
  never a side effect of `release`.
- The one apparent exception is not one. The audit append is **inside** the release decision because
  §8.4 makes it a precondition of the release, not a consequence of it: *"Every model call should be
  recorded in a consent-aware audit record."* A release returned before its record exists would open
  an interval in which content is releasable and unaudited. Recording the authorization is the same
  job as granting it.

### 3. "Enforced before content reaches any model" is a property, not a promise

§8.4's opening sentence is a sequencing requirement — *"Privacy policy must be enforced **before**
content reaches any model or external connector"* — and the segmentation map orders P7 ahead of P8
for exactly that reason: *"If the gate arrives after the harness, the first cloud call has already
shipped an unclassified document."* This plan makes that mechanically checkable in **three layers**,
of which two are provable inside P7 today and one is not:

- **L1 — the token is unforgeable and single-use (Task 12, provable now).** `Released` carries a
  `release_id` minted by the gate and recorded in P7's ledger, bound to
  `(model_target, prompt_fingerprint, policy_version)`. `consume_release(...)` is the only way to
  spend one, it checks the ledger, and it consumes on first use. A hand-constructed `Released` is
  **inert**: it is a dataclass a caller can instantiate, and doing so buys nothing, because the id it
  carries is not in the ledger. This is the property that makes the door real, and it is entirely
  testable with no P8 in existence.
- **L2 — content materialises in exactly one module (Tasks 9 and 21, provable now).** P4's text
  materialisers are `evidence_shape.text_units.raw_value_at`, `evidence_shape.store.text_units_for_run`,
  `evidence_shape.store.text_unit_at` and `evidence_shape.store.unit_for_observation`. Task 21
  asserts by **runtime introspection of module namespaces** that exactly one module under
  `src/privacy/` binds any of them, and that the repo-wide set of packages binding them is
  `{evidence_shape, extractors, privacy}` and nothing else. This guard passes trivially today; it
  becomes load-bearing the moment P8 lands, and it is written now so it is not written later by
  someone who wants it to pass.
- **L3 — the transport has one entry point and its only content parameter is a `Released`
  (Task 19, NOT provable inside P7).** Done-means 3 is a static property of a transport P7 does not
  own — P8 Done-means 1 says *"Exactly one function in the codebase constructs a model request, and
  its only parameter type is P7's `Released`."* P7 therefore ships the **checker**,
  `assert_single_egress(module)`, and tests it against a conforming fixture transport and a
  non-conforming one, so the check itself is proven correct. Running it over the real transport is
  P8's obligation. **Say this plainly in the plan and in the report: until P8 exists, Done-means 3
  is proven only to the extent that the instrument is proven.**

### 4. P6 does not exist, and P7 must not answer P6's open question

SPEC §2 says the classification record is *"written through P6's `sensitivity` field"*. P6 is
unbuilt, and **P6's own SPEC Open question 11 is open**: *"`sensitivity status` is a universal *fact*
(§3.11), a *sensitivity state* on the file record (§8.2), and a *handling class* in the privacy gate
(§8.4). One record or three? Which part writes it, and does a user reclassification (§8.4) arrive as
a `user_confirmed` fact?"* P7's SPEC asserts an answer to that question; P6's SPEC still asks it.

**P7 does not settle it.** Every task below is written against an injected `SensitivityFacts`
protocol with a fixture implementation in `tests/p7/p6_fixture.py`, reconstructed from P6's SPEC —
the same device `tests/p5/p4_stub.py` used, and the same delete-and-import swap when P6 ships. The
protocol is the narrowest surface that satisfies §8.4 and it deliberately does **not** decide
whether the fact, the file column and the handling class are one record or three. Task 21 holds
P6 OQ11 open by name and fails if an implementation answers it.

### 5. Every open question stays open

Eleven questions are open in P7's SPEC, plus the unresolved I6. Not one is answered in code. Each is
held by a guard in Task 21 that names it and fails the moment someone answers it in an implementation
instead of in a SPEC. Where the design leaves a value open — a threshold, a ceiling, an identifier
class, a redaction transform, a detection rule, a retention period — this plan holds a
**caller-supplied strategy or a required keyword**, never a number and never a list.

---

## Global Constraints

Every task's requirements implicitly include these. Values are copied verbatim from
[`SPEC.md`](SPEC.md) and from
[`../../00-database-agent-product-design.md`](../../00-database-agent-product-design.md).

- **P7 owns no detection rule.** SPEC *Deferred*: *"The design states *what* is protected and never
  *how it is recognised*. The detector rule set, its signals, and its thresholds are hand-authored.
  P7 publishes the vocabulary the detectors write into."* `src/privacy/` contains no regex, no
  gazetteer, no filename pattern, no keyword list, and no rule that decides a given file is a
  passport. A detector is a caller that writes a classification through P7's writer.
- **P7 never truncates and never reduces.** SPEC *Budgets*: *"The gate never truncates and never
  reduces"*; reduction changes what the model sees, which is a dossier decision. The gate's only
  content operations are **resolution and redaction**. §8.6's four-rung ladder — *"summarize
  deterministic facts, preserve anchor excerpts, split the task, or defer the decision"* — runs in
  P8, before the call (M9). `dossier_over_budget` is a backstop denial that should never fire.
- **Closed vocabularies, and no additions.** Five handling classes, four operation modes, nine
  always-local items, six releasable item kinds, eight `Denied.reason` values, four consent options,
  five display facets, three `basis` values, three `outcome` values. *"A value outside this set is a
  load error, not a fallback"* (SPEC §1). Adding a member is a P7 contract revision, not an
  implementation decision.
- **Absence of a classification resolves to `unreadable_unclassified`, never to `public_low`**
  (SPEC §1, §8.4, §8.6). This is the direct application of §8.6's *"Cost exhaustion must never turn
  into lower-quality automatic classification."* There is no default-to-public code path anywhere.
- **`evidence_refs` is non-empty for any `basis = detector` classification** (SPEC §2, §3.1's
  principle: every fact preserves where it came from).
- **The citation handle is `observation_key`, never `observation_id`** (M14, and SPEC
  *Correction learning*: *"The key, not the id, is what makes that durable"*). A per-row
  `observation_id` dies on extractor upgrade; P4's `observation_key` deliberately excludes
  `extractor_version` (MINOR 8) so it survives one.
- **`events` is INSERT-only and P7 never mutates it.** P1 enforces it with three SQL triggers
  (`events_no_update`, `events_no_delete`, `events_no_replace`). A revocation is a forward-only
  event; §8.4's requirement to communicate that already-sent data cannot be retracted is
  unsatisfiable if the send record is erasable.
- **P7 registers no event type at run time.** Its eight names are **already in P1's frozen
  `_REGISTERED` table** (`src/database_agent/events.py:43-51`), compiled from this SPEC. Task 1
  asserts they are present and collide with none of §8.2's nineteen; it adds nothing.
- **P7 authors its events; P1 writes them** (M8). `subsystem = "P7"`. There is one place in
  `privacy` where that value is written and Task 21 asserts there is no second.
- **Supersede, never overwrite** (§8.2). A user reclassification is a new `user_confirmed` fact that
  supersedes the prior one through P1's published three columns — `supersedes`, `superseded_by`,
  `supersede_reason` (M1; MINOR 3 confirms the spelling is `supersede_reason`). Both remain
  inspectable.
- **No invented values.** No numeric ceiling, no retention period, no identifier class, no redaction
  transform, no corpus-area definition, no default operation mode beyond the `offline | local_model`
  floor W1 binds. Task 21 enforces this by **runtime introspection** of every module's namespace,
  **not by searching source text** — a source-text guard matches comments and docstrings, which is
  a failure this repository has already recorded more than once. The established mechanism is
  `code_tokens()` in `tests/p3/test_p3_no_invention.py`, which walks the AST and excludes
  docstrings; where a token assertion is unavoidable, use that and not `read_text()`.
- **P7 creates and modifies no file owned by another part.** `pyproject.toml`, `tests/conftest.py`,
  and everything under `src/database_agent/`, `src/scan_agent/`, `src/evidence_shape/`,
  `src/extractors/` and `src/eval_harness/` belong elsewhere. P7's tests live in `tests/p7/` with
  their own `conftest.py` and inherit P1's root `conn` fixture without editing it.
- **`tests/p7/conftest.py` must not shadow P1's.** Under pytest's default prepend import mode, with
  no `__init__.py` under `tests/`, every `conftest.py` is imported as the top-level module `conftest`
  and the last one wins. P7's own fixtures may live there; nothing imported across parts by name may.
- **Python 3.12**, stdlib only.
- **P1–P5 must be green before Task 1 starts.** `pytest tests/ -q` → **1231 passed**, confirmed
  2026-08-21. P7's first import failure otherwise reads as a P7 defect when it is a missing substrate.

---

## What P7 consumes from P1

Written against `src/database_agent/` **as implemented**, introspected 2026-08-21 with
`inspect.signature` — not against P1's PLAN, whose header says it is a superseded construction record.

```text
database_agent.db          open_database(path, *, scan_roots=()) -> sqlite3.Connection
                           create_schema(conn) -> None
                           transaction(conn)                          contextmanager
database_agent.events      append_event(conn, **fields) -> int        returns the event_id
                           EVENT_FIELDS: tuple[str, ...]              (eleven, MINOR 1)
                           CORRECTION_FIELDS: tuple[str, ...]         (five, §8.7)
                           CORRECTION_SCOPES: tuple[str, ...]         (six, §8.7)
                           RESERVED_EVENT_TYPES: frozenset[str]       (§8.2's nineteen)
                           REGISTERED_EVENT_TYPES: MappingProxyType   P7's eight are ALREADY here
                           EVENT_TYPES: MappingProxyType              reserved | registered
                           MalformedEvent, UnregisteredEventType
database_agent.files_table get_file(conn, file_id) -> sqlite3.Row
                           file_path_history(conn, file_id) -> list[sqlite3.Row]
                           FILES_COLUMNS: tuple[str, ...]             (sixteen, incl. sensitivity_state)
database_agent.supersede   SUPERSEDE_COLUMNS: tuple[str, str, str]    (M1's three)
                           supersede_ddl(table) -> str
                           mark_superseded(conn, table, *, old_id, new_id, reason) -> None
                           chain(conn, table, record_id) -> list[sqlite3.Row]
database_agent.budget      CEILING_KEYS: tuple[str, ...]              (SIXTEEN -- see below)
                           get_ceiling(conn, key) -> int | None
database_agent.learning    learning_records(conn, scope, subject_id) -> list[sqlite3.Row]
                           SCOPES: tuple[str, ...]                    (§8.7's six)
```

Six facts about that surface, each of which changes how a task below is written:

1. **P7's eight event types are already registered.** `events._REGISTERED` contains
   `classification_assigned`, `classification_superseded`, `policy_set`, `consent_granted`,
   `consent_revoked`, `model_release`, `model_release_denied`, `consent_requested`, each with
   `base = None`, sourced from *"P7 SPEC, Cross-cutting answers -> Provenance. Eight."* None collides
   with §8.2's nineteen; P1 checks that at **import**, so a collision is an ImportError and not a
   run-time rejection. Task 1 asserts the eight are present and adds nothing.
2. **`append_event` accepts exactly seventeen named columns and rejects a hidden eighteenth.**
   `_WRITABLE = EVENT_FIELDS (11) + CORRECTION_FIELDS (5) + "base_event_type"`, and an unknown key
   raises `MalformedEvent`. **None of the consent-aware audit record's own fields is among them.**
   `audit_id`, `release_id`, `policy_version`, `plan_version`, `stage`, `outcome`,
   `operation_mode`, `authorizing_policy`, `file_sensitivity`, `excerpts_included`,
   `redaction_applied`, `model` and `content_hashes` have **no column**. Only `prompt_fingerprint`,
   `file_id`, `content_hash`, `user_id`, `observed_at`, `subsystem` and `component_version` do. See
   *The audit record's home*, below — this is the single largest shape decision in the part.
3. **`append_event` returns `cursor.lastrowid`** — a monotonic `INTEGER`. That is the natural
   `audit_id`, and it exists only *after* the append, which is what makes SPEC §6's ordering
   guarantee — *"the audit record is appended … **before** `Released` is returned"* — a structural
   fact rather than a discipline.
4. **`events` has three append-only triggers.** `UPDATE`, `DELETE` and an id-reusing `INSERT` all
   `RAISE(ABORT, 'events is append-only (R6, 8.2)')`. Done-means 8's *"never deletes an audit
   record"* is therefore provable by attempting the delete and catching the abort.
5. **`learning_records(conn, scope, subject_id)` filters on `correction_scope` and
   `correction_subject` only**, plus `user_id IS NOT NULL`, honouring a reset cutoff. It does **not**
   filter on `proposal_class` or `basis_key` — it returns them on the row and the caller filters.
   10-i4-learning-ops.md assigns that filtering to the acting part: *"Ignores records at the wrong
   `proposal_class`. Ignores records whose `basis_key` does not match."* P7 therefore calls
   `learning_records(conn, "file", file_id)` and filters in `src/privacy/learning_seam.py`.
   `basis_key` is one `TEXT` column, so `(file_id, handling_class)` is a canonical-JSON encoding P7
   composes and P1 stores opaquely.
6. **`budget.CEILING_KEYS` holds `model.max_dossier_tokens_per_call`** and `set_ceiling` raises
   `KeyError` on a SEVENTEENTH key. **Corrected 2026-08-21:** this plan said fifteen and tested for a `KeyError` on a sixteenth. There are sixteen, and the sixteenth is `evidence.context_window`, added by ratification B4 (2026-08-20). P6's plan has the count right, so B4 reached one plan and not its neighbour -- the same defect class the wave keeps finding, one document over. P7 reads the ceiling and never invents a value; the
   `ModelCallRequest.max_dossier_tokens` field is the caller's echo of it (M9).

### The audit record's home — decided here, because every task depends on it

§8.4's consent-aware record has six required fields and SPEC §7 carries thirteen more. P1's `events`
accepts seventeen named columns and MINOR 1 fixes §8.2's list at eleven **forever**. B5 settles that
there is **one log**: *"§8.4's consent-aware record is that log with the consent fields and
`correction_scope`."* These three facts are only jointly satisfiable one way:

**The audit record is one `events` row. Its native columns carry what `events` has a column for; the
remainder is canonical JSON in `explanation`, which is §8.2's own *"structured explanation or
evidence reference"* slot.** `audit_id` is the returned `event_id`. This is the same device P5's
Task 16 used for its `extraction` / `OCR` explanations, and it keeps the record queryable through
SQLite's `json_extract`.

`explanation` is `NOT NULL`-checked by the writer (`_REQUIRED` includes it and rejects the empty
string), so every P7 event carries a non-empty structured explanation by construction. The plan
author writes the exact JSON schema in Task 10 and it is compared field-for-field against SPEC §7's
nineteen names. **P7 does not add a column to `events` and does not ask P1 to.**

## What P7 consumes from P3

```text
scan_agent.exclusion  is_protected_container(path, *, extra=None) -> bool
                      exclusion_for(path, *, is_dir, applies_to,
                                    project_root_markers=(), is_protected=None)
                                                        -> ExclusionVerdict | None
                      LABEL_UNTOUCHED_PROTECTED: str    = "untouched_protected"
                      REASON_PROTECTED_CONTAINER: str   = "protected_container"
                      RULE_PROTECTED_CONTAINER: str     = "protected container"
                      exclusion_verdicts(conn, scan_run_id) -> list[sqlite3.Row]
```

**P7 imports none of these.** They are listed because the corpus boundary is what makes the
Contract-in row true — *"Files excluded at scan never reach the gate"* — and because Task 2 pins
`untouched_protected` and `protected_container` beside P7's own `protected` so the three cannot be
confused. A file excluded at scan has no `files` row, so `Gate.release` cannot be asked about it: the
guarantee is structural, not a check P7 performs.

## What P7 consumes from P4

```text
evidence_shape.store       observations_by_key(conn, observation_key) -> list[Observation]
                           observations_for_file(conn, file_id) -> list[Observation]
                           unit_for_observation(conn, observation) -> TextUnit | None
                           text_unit_at(conn, run_id, container_path) -> TextUnit | None
                           text_units_for_run(conn, run_id) -> list[TextUnit]
                           runs_for_file(conn, file_id) -> list[ExtractionRun]
                           supersede_chain(conn, observation_id) -> list[sqlite3.Row]
evidence_shape.text_units  raw_value_at(unit, text_span) -> str
                           check_span_anchor(observation, unit) -> None   raises SpanAnchorError
                           TextUnit(run_id, container_path, text, truncated=False)
evidence_shape.location    Location(zone, container_path=(), text_span=None,
                                    time_span=None, region=None)
                           TextSpan(start, end) · TimeSpan(start_ms, end_ms)
                           Region(x, y, w, h, unit) · Segment(kind, index=None, label=None)
                           ZONES (15) · SEGMENT_KINDS (15)
evidence_shape.locator     serialize_locator(location) -> str · parse_locator(text, *, region=None)
                           location_to_mapping / location_from_mapping
evidence_shape.observation observation_key(*, content_hash, extractor_name, locator, raw_value) -> str
                           Observation(...)   — three context fields, M5
evidence_shape.runs        ExtractionRun(...) · COMPLETENESS (nine) · ANALYSIS_TIERS (four)
evidence_shape.fixtures    FIXTURES: tuple[Fixture, ...]   nineteen worked examples
```

Four facts that shape Task 9:

- **`observations_by_key` returns a LIST, deliberately.** P4's docstring: *"A LIST: two extractor
  versions carry one key, which is what MINOR 8 arranged and what §8.5's cross-version diff reads."*
  The gate must resolve to the **current** row — the one not superseded — and Task 9 must state and
  test that selection rule. Resolving to the wrong row means releasing text an extractor upgrade has
  already retracted.
- **Only a `text_span` is materialisable as a substring.** `raw_value_at(unit, text_span)` is
  `unit.text[start:end]`. §2.3's table/row/cell and §2.8's EXIF-field addressing live in
  `container_path`, and for those the materialisable value is `Observation.raw_value` — there may be
  no `TextUnit` at all. Task 9 must publish both resolution paths and deny an item whose span form
  has no resolver, rather than silently falling back to the whole unit.
- **`check_span_anchor` raises `SpanAnchorError` and never returns a repair.** P7 uses it as its
  own precondition: a `(observation_key, span)` whose span does not anchor is a `Denied`, not a
  best-effort excerpt.
- **M5's three context fields exist so §8.4 can redact a value without dropping its context.**
  `context_before`, `context_after`, `context_truncated` are separate columns precisely for P7's
  benefit. Task 8 must use them; a redaction that returns the whole surrounding text has thrown away
  the reason the fields were split.

## What P7 consumes from P5

```text
extractors.long_tail   POTENTIALLY_SENSITIVE: str = "potentially sensitive"
                       sensitivity_signals_for(conn, run_id) -> list[sqlite3.Row]
                         row: signal_id · run_id · observation_key · signal · basis · observed_at
                       SENSITIVE_EMAIL_ZONES: tuple[str, ...]        = ("body", "link")
                       SENSITIVE_EMAIL_VALUE_KINDS: tuple[str, ...]  = ("address",)
                       FULLY_SENSITIVE_SOURCE_TYPES: tuple[str, ...] = ("contacts",)
                       UnauthorizedTranscription
extractors.dispatch    extract(..., transcription_authorized: Callable[[], bool]) -> Dispatched
evidence_shape.runs    COMPLETENESS = ('complete','capped','partial','metadata_only','deferred',
                                       'unsupported','unreadable','failed','dataless')
                       — the nine; there is no marking literally named "indexed-but-unreadable"
```

**This is a live surface P7's SPEC does not mention, and it is the only per-value sensitivity signal
in the product.** P5's docstring is explicit about who it is for: *"Email addresses, message content
and every VCF value are marked POTENTIALLY SENSITIVE at emission, for P7 to act on. P5 assigns no
handling class: section 8.4 gives classification to P7."* Task 3 consumes it as a detector input;
Task 7 uses it to decide which values are §8.4's *"raw sensitive values"* — the always-local item
that cannot otherwise be recognised without a detection rule P7 does not own.

The reader is keyed by `run_id` only, so the file-level walk is
`runs_for_file(conn, file_id)` → `sensitivity_signals_for(conn, run.run_id)`. P7 adds no reader to
P5; it composes the two P5 and P4 already publish.

**`transcription_authorized` is a zero-argument predicate**, `Callable[[], bool]`, called as
`transcription_authorized()` in `src/extractors/long_tail.py:204`. It takes no `file_id` and no
scope. P7's `Gate.*` surfaces are all per-file or per-scope, so Task 5 must publish an adapter that
closes over a scope and satisfies `() -> bool`, or P5's signature must widen. **This is a genuine
seam mismatch and it is reported, not patched here.**

## What P7 consumes from P6 — and how, before P6 exists

P6 is unbuilt and **P6's SPEC Open question 11 is open**. Every field below is quoted from
`../P6-facts-facets/SPEC.md`; nothing is invented, and nothing here answers OQ11.

```text
file_facts     fact_id · file_id · field_id · value_id · reliability_state · origin ·
               evidence_refs[] · cited_quote_refs[] · cache_key · model_identifier ·
               prompt_fingerprint · internal_score · active · preferred ·
               supersedes / superseded_by / supersede_reason · rejection_reason · created_at
reliability    user_confirmed · direct · validated · llm_supported · possible · rejected   (§3.13)
ordering       user_confirmed > direct > validated > llm_supported > possible
origin         deterministic extractor | rule | LLM interpretation | user correction |
               user-approved folder                                                        (§3.1)
universal      file type · creation date · language · duplicate family · version family ·
  fields       sensitivity status                                                         (§3.11)
```

P7 talks to P6 through **one injected protocol** with no default, defined in
`src/privacy/facts_seam.py` and implemented for tests in `tests/p7/p6_fixture.py`:

```text
SensitivityFacts
  current(file_id, content_hash)        -> ClassificationRecord | None
  write(record)                         -> fact_id
  supersede(old_fact_id, new_fact_id, reason) -> None
  history(file_id)                      -> list[ClassificationRecord]
```

Three shape mismatches the fixture must make visible rather than paper over, each reported:

- **`file_facts` has no `protected` column and no `basis` column.** SPEC §2's classification record
  carries both. P6's `origin` vocabulary (five §3.1 values) is not P7's `basis` vocabulary
  (`detector | safety_domain | user`). The fixture stores both and the plan flags that neither has a
  home in the published P6 shape.
- **Three spellings for one thing.** P7 SPEC says `sensitivity`; §3.11 and P6 say `sensitivity
  status`; P1's column is `sensitivity_state`. Task 2 pins all three.
- **P6 OQ11 is open and stays open.** Task 21 asserts P7 publishes no answer to it.

## What P7 consumes from P13

P13 is unbuilt; its SPEC publishes the record and P7's row in its routing table:

```text
review_action   action_id · surface · subject_ref · plan_version · session_id · action ·
                bulk_member_refs[] · bulk_basis · correction_scope · routed_to[] ·
                presented_state_ref · user_id · acted_at
P7's row        surfaces `consent`, `privacy_settings`; `subject_ref` is a consent_request_id;
                action = select_consent_option | set_redaction | mark_private
P6+P7 jointly   action = mark_private
```

**`subject_ref` is a `consent_request_id`, and `NeedsConsent` as published in SPEC §6 carries no
id.** Done-means 7 requires the audit log to show *"a `consent_requested` event and no
`model_release` for that request until a choice is recorded"* — which needs a join key. Task 14
therefore adds `consent_request_id` to `NeedsConsent` and to the `consent_requested` audit record.
**This is a Contract-out gap, reported; the field name is P13's, not invented here.**

## What P7 consumes from P2

```text
eval_harness.bundle   open_bundle(conn, *, corpus_form, source_scan_ref, pinned_plan_id,
                                  pinned_plan_version, policy_settings: dict,
                                  supersedes_bundle_id=None) -> str
                      add_file_entry(conn, bundle_id, *, file_id, content_hash,
                                     hash_algorithm, handling_class: str | None, ...) -> None
                      BUNDLE_CONTENTS  includes 'policy_settings'                    §8.5
```

Both slots the Contract-in names are **built and green**. `src/orchestrator.py:259` already passes
`handling_class=file_row["sensitivity_state"]` with the comment *"P7's, and P7 is unbuilt. P1's
column is the only source and it is NULL until a gate writes it."* Task 4 is what stops that being
NULL. Task 22 asserts the Wave-2 bundle carries a non-null `handling_class` after a classification.

## What P7 publishes, and who consumes it

| Surface | Consumed by | For |
|---|---|---|
| `HANDLING_CLASSES`, `OPERATION_MODES`, `ALWAYS_LOCAL`, `ITEM_KINDS`, `DENIAL_REASONS`, `CONSENT_OPTIONS`, `DISPLAY_FACETS` | P6, P8, P9, P10, P11, P12, P13 | §8.4's closed vocabularies |
| `ClassificationRecord`, `protected` flag | P6 (stores), P9 §4.9, P10 §5.12, P11 §6.10 | §8.4's classification |
| `Gate.release(ModelCallRequest) -> Released \| Denied \| NeedsConsent` | **P8, and every part that wants a model** | §8.4's one door (B2) |
| `Released`, `consume_release` | P8's transport | the unforgeable, single-use capability |
| `assert_single_egress(module)` | P8's Done-means 1 | Done-means 3's instrument |
| `Gate.revoke`, `Gate.reclassify`, `RevocationResult` | P13 | §8.4's user rights |
| `Gate.may_move_automatically(file_id, plan_version)` | P11 §6.11, P12 §8.3 | §8.4's automatic-move rule |
| `Gate.display_policy() -> RedactionSettings`, `Gate.summarize_protected(scope)` | P13, P10 §5.2, P11 §7.5 | §8.4's UI privacy |
| `transcription_authorized_for(scope) -> Callable[[], bool]` | P5 `extractors.dispatch.extract` | §2.9's speech-to-text authorization (M10 back-edge) |
| `fixtures.FIXTURES` | **P8 (builds against them with P7 unimplemented)**, P2, P13 | SPEC §11, Done-means 11 |

---

## File Structure

```text
src/privacy/__init__.py            package marker; exports Gate and the three decision types
src/privacy/authorship.py          SUBSYSTEM = "P7"; the eight event names, asserted not added
src/privacy/vocabulary.py          every closed vocabulary, and OPEN_QUESTIONS
src/privacy/classification.py      SPEC §2's record; absence -> unreadable_unclassified
src/privacy/facts_seam.py          the SensitivityFacts protocol — P6's seam, injected, no default
src/privacy/policy.py              modes, consent grants, redaction settings, policy_version
src/privacy/defaults.py            W1 — the local-first floor and the more-redacting rule
src/privacy/items.py               the six releasable kinds; the always-local set as a denial
src/privacy/redaction.py           the manifest; the identifier class is an opaque injected string
src/privacy/resolve.py             THE ONLY MODULE THAT MATERIALISES CONTENT — (key, span) -> text
src/privacy/audit.py               §8.4's consent-aware record, as one events row + JSON explanation
src/privacy/release.py             Gate.release — the request, the three branches, the ordering
src/privacy/binding.py             release_id, the ledger, single use, the binding tuple
src/privacy/denial.py              the eight reasons and their evidence-referenced explanations
src/privacy/consent.py             NeedsConsent, the consent_request_id, the P13 seam
src/privacy/revocation.py          revoke; retraction_limit; delete_derived's refusal (I6)
src/privacy/learning_seam.py       §8.7 query-before-classify over P1's learning_records
src/privacy/moves.py               may_move_automatically
src/privacy/display.py             display_policy, summarize_protected
src/privacy/transport_guard.py     assert_single_egress — Done-means 3's instrument
src/privacy/schema.py              P7's own tables, inside P1's database
src/privacy/gate.py                the Gate facade — one object, one door, no second name
src/privacy/fixtures.py            SPEC §11's published fixtures, as golden records

tests/p7/conftest.py               p7_conn, request builders, a fixed clock
tests/p7/p6_fixture.py             P6's SPEC, stubbed: file_facts, the six states, the ordering
tests/p7/transport_fixtures.py     one conforming and one non-conforming transport, for Task 19
tests/p7/test_p7_authorship.py     the eight names, already registered in P1
tests/p7/test_p7_vocabulary.py     every closed vocabulary; the four `protected` spellings
tests/p7/test_p7_classification.py SPEC §2; Done-means 2; evidence-backed
tests/p7/test_p7_facts_seam.py     the P6 seam; §3.13's ordering; supersede-never-overwrite
tests/p7/test_p7_policy.py         modes, grants, redaction settings, policy_version
tests/p7/test_p7_defaults.py       Done-means 12 — W1, and the negative test
tests/p7/test_p7_items.py          §4's six kinds; the always-local nine; whole_document
tests/p7/test_p7_redaction.py      the manifest; M5's context fields survive redaction
tests/p7/test_p7_resolve.py        (observation_key, span) -> text, and the current-row rule
tests/p7/test_p7_audit.py          §7's fields; Done-means 4 — the ordering guarantee
tests/p7/test_p7_release.py        the three branches; no override parameter
tests/p7/test_p7_binding.py        Done-means 5 — binding and single use
tests/p7/test_p7_denials.py        Done-means 6 — all eight reasons
tests/p7/test_p7_consent.py        Done-means 7 — four options, and no release until a choice
tests/p7/test_p7_revocation.py     Done-means 8; I6 held open
tests/p7/test_p7_learning_seam.py  §8.7 query-before-classify
tests/p7/test_p7_moves.py          Done-means 9
tests/p7/test_p7_display.py        Done-means 10
tests/p7/test_p7_transport.py      Done-means 3 — the instrument, proven both ways
tests/p7/test_p7_fixtures.py       Done-means 11 — every fixture, and the P8 obligation named
tests/p7/test_p7_no_invention.py   every open question held open, by introspection
tests/p7/test_p7_skeleton_step.py  Done-means 13, and 11 §9's second fixture path
```

Files split by published surface, not by technical layer, so a reviewer can reject one without
touching its neighbours. The one structural rule: **`resolve.py` is the only module that binds a P4
text materialiser**, and `release.py` is the only module that imports `resolve`.

---

## Tasks

### Task 1: Package skeleton, and the eight event types P1 already registered

**Files:** create `src/privacy/__init__.py`, `src/privacy/authorship.py`, `tests/p7/conftest.py`;
test `tests/p7/test_p7_authorship.py`.

**Interfaces:**
- Consumes: `database_agent.events.REGISTERED_EVENT_TYPES`, `.RESERVED_EVENT_TYPES`, `.EVENT_TYPES`,
  `.EVENT_FIELDS`, `.CORRECTION_FIELDS`, `.append_event`, `.MalformedEvent`, `.UnregisteredEventType`.
- Produces: `SUBSYSTEM: str`, `COMPONENT_VERSION: str`, `P7_EVENT_TYPES: tuple[str, ...]` (the eight,
  in SPEC order), `CLASSIFICATION_ASSIGNED`, `CLASSIFICATION_SUPERSEDED`, `POLICY_SET`,
  `CONSENT_GRANTED`, `CONSENT_REVOKED`, `MODEL_RELEASE`, `MODEL_RELEASE_DENIED`, `CONSENT_REQUESTED`,
  `event_defaults(*, event_type, **fields) -> dict[str, object]`.

**Done-means:** substrate for 4, 6, 7, 8.

**What its tests must prove.** That all eight names are present in P1's `REGISTERED_EVENT_TYPES`
with `base = None`, that none is in `RESERVED_EVENT_TYPES`, and that `append_event` accepts each —
so registration is asserted, never performed. That `event_defaults` fills `subsystem = "P7"` and
never lets a caller override it, because M8's *"the acting part authors"* is unmeetable from a log
where the author is a parameter anyone may set. That a ninth, unregistered P7-looking name raises
`UnregisteredEventType`, which is what proves registration is a spec-level act and not something
this package can do at run time.

---

### Task 2: The closed vocabularies, and the four words with `protected` in them

**Files:** create `src/privacy/vocabulary.py`; test `tests/p7/test_p7_vocabulary.py`.

**Interfaces:**
- Consumes: `scan_agent.exclusion.LABEL_UNTOUCHED_PROTECTED`, `.REASON_PROTECTED_CONTAINER`
  (imported **in the test only**, to pin the distinction — `src/privacy/` imports neither).
- Produces: `HANDLING_CLASSES: tuple[str, ...]` (5), `OPERATION_MODES: tuple[str, ...]` (4),
  `ALWAYS_LOCAL: tuple[str, ...]` (9), `ITEM_KINDS: tuple[str, ...]` (6),
  `DENIAL_REASONS: tuple[str, ...]` (8), `CONSENT_OPTIONS: tuple[str, ...]` (4),
  `DISPLAY_FACETS: tuple[str, ...]` (5), `CLASSIFICATION_BASES: tuple[str, ...]` (3),
  `AUDIT_OUTCOMES: tuple[str, ...]` (3), `MODE_SEMANTICS: Mapping[str, str]` (§8.4 verbatim),
  `OutOfVocabulary`, `check_handling_class(value) -> str`, `check_mode(value) -> str`,
  `check_item_kind(value) -> str`, `check_denial_reason(value) -> str`.

**Done-means:** 1.

**What its tests must prove.** That each vocabulary is exactly the SPEC's list in the SPEC's order,
and that a value outside it raises `OutOfVocabulary` at load rather than resolving to a neighbour —
*"A value outside this set is a load error, not a fallback."* That `MODE_SEMANTICS` reproduces
§8.4's four sentences verbatim, so a later paraphrase is a failing test and not an editorial choice.
And that the four spellings coexist and differ: P7's `protected` flag, P7's
`protected_cloud_target` and `protected_records_template` denial reasons, P3's
`untouched_protected` label and P3's `protected_container` exclusion reason — five strings, one
stem, and no code that treats any two as the same.

---

### Task 3: The classification record, and absence resolving to `unreadable_unclassified`

**Files:** create `src/privacy/classification.py`; test `tests/p7/test_p7_classification.py`.

**Interfaces:**
- Consumes: `vocabulary.HANDLING_CLASSES`, `.CLASSIFICATION_BASES`,
  `evidence_shape.observation.observation_key`, `evidence_shape.runs.COMPLETENESS`,
  `extractors.long_tail.POTENTIALLY_SENSITIVE`, `.sensitivity_signals_for`,
  `evidence_shape.store.runs_for_file`.
- Produces: `ClassificationRecord` (frozen dataclass: `file_id`, `content_hash`, `handling_class`,
  `protected`, `basis`, `evidence_refs: tuple[str, ...]`, `reliability_state`, `observed_at`),
  `CLASSIFICATION_FIELDS: tuple[str, ...]` (SPEC §2's eight),
  `UnbackedClassification`, `resolve_class(record: ClassificationRecord | None) -> str`,
  `completeness_implies_unclassified(completeness) -> bool`.

**Done-means:** 2 (first half), and the input side of 6.

**What its tests must prove.** That `resolve_class(None)` returns `unreadable_unclassified` and that
**no input** produces `public_low` by default — the failure §8.6 names, *"Cost exhaustion must never
turn into lower-quality automatic classification"*, is exactly defaulting an unclassified file to
public so the pipeline can continue. That a `basis = "detector"` record with empty `evidence_refs`
raises `UnbackedClassification`, because §8.4 says the classification *"is itself evidence-backed"*.
That `evidence_refs` holds P4 `observation_key` values and that a value shaped like an
`observation_id` is refused (M14). And that the mapping from P4's nine `completeness` values to
`unreadable_unclassified` is stated explicitly per value rather than by an `in`-check over a set the
author guessed — including the case of a file with **no run row at all**, which is what a dataless
file has.

---

### Task 4: The P6 seam, §3.13's ordering, and P1's `sensitivity_state` mirror

**Files:** create `src/privacy/facts_seam.py`, `tests/p7/p6_fixture.py`; test
`tests/p7/test_p7_facts_seam.py`.

**Interfaces:**
- Consumes: `database_agent.supersede.mark_superseded`, `.chain`, `.SUPERSEDE_COLUMNS`,
  `database_agent.files_table.get_file`, `.FILES_COLUMNS`; `classification.ClassificationRecord`.
- Produces: `SensitivityFacts` protocol (`current`, `write`, `supersede`, `history`),
  `RELIABILITY_ORDER: tuple[str, ...]` (§3.13's five ranked, `rejected` excluded),
  `strongest(records) -> ClassificationRecord`,
  `SensitivityStateWriter` protocol (`set_sensitivity_state(conn, file_id, *, state, author,
  component_version) -> None`) — **injected, because P1 publishes no such writer**,
  `mirror_state(record) -> str`.

**Done-means:** 2 (second half).

**What its tests must prove.** That exactly one current fact resolves per `(file_id, content_hash)`
and that a `user_confirmed` record outranks a `validated` one by §3.13's listed order — the ordering
is P6's, quoted, never re-derived. That a revision **supersedes** through P1's three columns and both
records remain readable afterwards (§8.2's explicit rule). That the mirror onto
`files.sensitivity_state` goes through an **injected** writer and that `src/privacy/` issues no
`UPDATE files` of its own — the same position P5's plan took on `extraction_status_by_tier` before
P1 published `set_extraction_status`, and the gap is reported rather than patched. And that the
fixture holds P6 OQ11 open: it stores `protected` and `basis` in fields that P6's published
`file_facts` shape has no column for, and says so in the assertion message.

---

### Task 5: Policy — the four modes, consent grants, redaction settings, `policy_version`

**Files:** create `src/privacy/policy.py`, `src/privacy/schema.py`; test `tests/p7/test_p7_policy.py`.

**Interfaces:**
- Consumes: `vocabulary.OPERATION_MODES`, `.DISPLAY_FACETS`, `authorship.POLICY_SET`,
  `.CONSENT_GRANTED`, `.CONSENT_REVOKED`, `database_agent.events.append_event`,
  `database_agent.db.transaction`.
- Produces: `create_privacy_schema(conn) -> None`, `Policy` (frozen: `policy_version`,
  `operation_mode`, `consent_grants`, `redaction_settings`, `automatic_move_permissions`,
  `plan_version`, `set_at`), `set_policy(conn, policy, *, author, component_version, user_id) -> str`,
  `current_policy(conn, *, plan_version) -> Policy`, `policy_at(conn, policy_version) -> Policy`,
  `grant_consent(...)`, `revoke_consent(...)`, `transcription_authorized_for(scope) -> Callable[[], bool]`.

**Done-means:** substrate for 5, 6, 8, 12; the P5 back-edge.

**What its tests must prove.** That `policy_version` is minted by the gate and never accepted from a
caller — SPEC §6: *"the gate owns the policy, so the caller does not supply this value, it echoes
it."* That a policy change appends `policy_set` and supersedes rather than mutating, so §8.8's
requirement that a privacy-policy change appear as a first-class diff line has a record to diff.
That policy is **plan-scoped** while classifications and audit records are **not** (§8.8: *"The
evidence database remains shared across plan versions"*). That `transcription_authorized_for` returns
a zero-argument callable satisfying P5's `Callable[[], bool]` — and that the scope it closes over is
recorded, because P5's call site passes no scope and the mismatch must be visible in the test rather
than hidden by an adapter. **Consent-grant scoping is left parameterised**: SPEC Open question 3
asks what a *"corpus area"* is, and Task 21 asserts P7 supplies no answer.

---

### Task 6: The local-first default (W1)

**Files:** create `src/privacy/defaults.py`; test `tests/p7/test_p7_defaults.py`.

**Interfaces:**
- Consumes: `vocabulary.OPERATION_MODES`, `.DISPLAY_FACETS`, `policy.Policy`, `.current_policy`.
- Produces: `LOCAL_FIRST_MODES: tuple[str, str]` = the two modes under which no content leaves the
  device, `MORE_REDACTING: Mapping[str, str]` (per facet), `resolve_default_policy(stored) -> Policy`,
  `DefaultPostureViolation`, `assert_local_first(policy) -> None`.

**Done-means:** 12.

**What its tests must prove.** Under a **fresh-install** fixture and a **migrated-from-nothing**
fixture, that the resolved mode is one of the two local modes and every configurable redaction
setting resolves to its more redacting value — §8.4's `must`: *"The default posture must therefore be
local-first and data-minimizing."* The **negative** half is the important half: that no code path,
build flag, packaged configuration file or first-run flow produces a starting mode of `hybrid` or
`cloud_assisted`. That must be asserted by **calling the resolver over every reachable stored state**
(absent, empty, partial, unknown-key) and by enumerating the package's module-level constants through
runtime introspection — **not** by grepping source text for the strings, because both mode names
appear legitimately in `vocabulary.py`, in docstrings and in denial messages, and a text scan would
either pass vacuously or fail on a comment. And the test must **not** assert which of the two ships:
Open question 11 stays open, and Task 21 asserts P7 names no winner.

---

### Task 7: The six releasable item kinds, the always-local nine, and `whole_document_requested`

**Files:** create `src/privacy/items.py`; test `tests/p7/test_p7_items.py`.

**Interfaces:**
- Consumes: `vocabulary.ITEM_KINDS`, `.ALWAYS_LOCAL`, `.DENIAL_REASONS`,
  `evidence_shape.location.TextSpan`, `.Region`, `.Segment`,
  `extractors.long_tail.POTENTIALLY_SENSITIVE`.
- Produces: `Excerpt`, `RedactedIdentifier`, `CandidateLabel`, `MetadataField`, `EvidenceReference`,
  `Filename` (six frozen dataclasses), `RequestedItem` union, `ITEM_FIELDS: Mapping[str, tuple]`,
  `AlwaysLocalRequested`, `WholeDocumentRequested`,
  `check_item(item, *, unit_length) -> None`, `is_whole_document(item, *, unit_length) -> bool`.

**Done-means:** 6 (the `always_local_item` and `whole_document_requested` reasons).

**What its tests must prove.** That each of the nine always-local names — *"Paths, complete extracted
text, OCR output, file hashes, image EXIF, GPS, user edits, group memberships, and raw sensitive
values"* — is **not expressible** as any of the six item kinds, asserted by attempting to construct
one and catching `AlwaysLocalRequested`, one test per name, nine tests. That an `Excerpt` whose span
covers the whole of its text unit raises `WholeDocumentRequested` — §8.4: *"It should not send full
documents where a short heading or OCR excerpt is enough to resolve the question."* That
`EvidenceReference` carries an id and has no content field at all, checked with
`dataclasses.fields`, not by reading the class body. And that `Filename` is permitted for
non-protected files and denied for protected ones, with the test naming SPEC Open question 2 in its
docstring so the reviewer knows this is the one place the contract resolved a conflict.

---

### Task 8: Redaction, and a manifest whose identifier class stays opaque

**Files:** create `src/privacy/redaction.py`; test `tests/p7/test_p7_redaction.py`.

**Interfaces:**
- Consumes: `items.RedactedIdentifier`, `evidence_shape.observation.Observation` (for M5's three
  context fields).
- Produces: `RedactionEntry` (frozen: `observation_key`, `span`, `identifier_class`, `redacted`),
  `RedactionManifest`, `IdentifierClassifier` protocol (**injected, no default**),
  `RedactionTransform` protocol (**injected, no default**),
  `apply_redaction(value, *, context_before, context_after, classifier, transform)
   -> tuple[str, RedactionEntry]`.

**Done-means:** 4 (`redaction_applied`), and the redaction half of 12.

**What its tests must prove.** That the identifier class is carried as an **opaque string** and that
`src/privacy/` enumerates none — SPEC *Deferred*: *"Which identifier classes exist and how each is
transformed is not enumerated anywhere in the design. `redaction_manifest` carries the class as an
opaque string until this is authored."* That the transform is injected with **no default**, so a
build that forgets to wire one cannot silently emit unredacted values. That redaction replaces the
**value** and preserves `context_before` and `context_after` — M5's three fields exist *"precisely so
§8.4 can redact a value without dropping its context"*, and a redaction that also blanks the context
has thrown away the reason P4 split the field. And that `context_truncated = true` is carried through
to the manifest, because §8.6 forbids anything being truncated silently.

---

### Task 9: Excerpt resolution — the only place content materialises

**Files:** create `src/privacy/resolve.py`; test `tests/p7/test_p7_resolve.py`.

**Interfaces:**
- Consumes: `evidence_shape.store.observations_by_key`, `.unit_for_observation`, `.supersede_chain`,
  `evidence_shape.text_units.raw_value_at`, `.check_span_anchor`, `.SpanAnchorError`,
  `evidence_shape.location.TextSpan`, `.Region`, `evidence_shape.locator.serialize_locator`.
- Produces: `Materialised` (frozen: `observation_key`, `span`, `value`, `zone`, `context_before`,
  `context_after`, `context_truncated`), `UnresolvableSpan`, `AmbiguousObservationKey`,
  `current_observation(conn, observation_key) -> Observation`,
  `materialise(conn, item) -> Materialised`.

**Done-means:** substrate for 3 (L2), 4, 5, 6.

**What its tests must prove.** That `observations_by_key` returning **two** rows — the shape P4
guarantees, because *"two extractor versions carry one key"* — resolves to the **current**,
non-superseded row, and that an unresolvable ambiguity raises rather than picking the first. That a
span which fails `check_span_anchor` produces `UnresolvableSpan` and never a best-effort substring:
P4's checker *"raises; never returns a repair"*, and a gate that repaired would release text nobody
addressed. That the two addressing forms are handled separately — a `text_span` materialises through
`raw_value_at`, while a `container_path`-only address (§2.3's cell, §2.8's EXIF field) materialises
`Observation.raw_value` and never falls back to the whole unit. And that this module is the **only**
one under `src/privacy/` that binds a P4 text materialiser, asserted here and again repo-wide in
Task 21.

---

### Task 10: The consent-aware audit record, and the ordering guarantee

**Files:** create `src/privacy/audit.py`; test `tests/p7/test_p7_audit.py`.

**Interfaces:**
- Consumes: `database_agent.events.append_event`, `.EVENT_FIELDS`, `.CORRECTION_FIELDS`,
  `evidence_shape.canonical.canonical_json`, `authorship.MODEL_RELEASE`, `.MODEL_RELEASE_DENIED`,
  `.CONSENT_REQUESTED`, `vocabulary.AUDIT_OUTCOMES`.
- Produces: `AuditRecord` (frozen; SPEC §7's six required plus its thirteen carried),
  `AUDIT_FIELDS: tuple[str, ...]` (nineteen), `EXPLANATION_FIELDS: tuple[str, ...]` (those with no
  `events` column), `append_audit(conn, record, *, author, component_version) -> int`,
  `audit_record(conn, audit_id) -> AuditRecord`, `audit_records_for(conn, *, file_id=None,
  release_id=None, consent_request_id=None) -> list[AuditRecord]`.

**Done-means:** 4, and the record half of 6, 7, 8.

**What its tests must prove.** That all six §8.4 fields are present — *"what policy authorized the
call, whether the file was sensitive, which excerpts were included, whether values were redacted,
which model received the data, and the prompt fingerprint"* — and that `AUDIT_FIELDS` matches SPEC §7
name for name, so a dropped field is a failing test. That the record round-trips: the fields with an
`events` column land there (`prompt_fingerprint`, `file_id`, `content_hash`, `user_id`,
`observed_at`) and the rest land in `explanation` as canonical JSON, recoverable by
`audit_record(...)` — the shape decision the preamble makes, tested rather than assumed. That
`excerpts_included` stores `(observation_key, span)` pairs plus the manifest and **not a second copy
of the text**, and that the stored pairs are sufficient to reconstruct exactly what left the device
by re-running `resolve.materialise` — SPEC §7: *"a record that cannot reconstruct the released
payload from local storage fails §8.4's stated purpose."* And the ordering guarantee: that
`append_audit` returns an `event_id` that is already `SELECT`-able before any caller can see it,
which is what makes *"There is no interval in which content is releasable and unaudited"* structural.
Local model calls are audited too — §8.4 says *"Every model call"* and names no exemption.

---

### Task 11: `Gate.release` — the request, the three-branch union, and no override parameter

**Files:** create `src/privacy/release.py`, `src/privacy/gate.py`; test `tests/p7/test_p7_release.py`.

**Interfaces:**
- Consumes: everything from Tasks 2–10.
- Produces: `ModelCallRequest` (frozen; SPEC §6's seven fields exactly: `stage`, `target`,
  `model_target`, `requested_items`, `prompt_template_id`, `prompt_fingerprint`,
  `max_dossier_tokens`), `ModelTarget` (`locality`, `model_id`, `provider`), `Target`
  (`file_ids`, `group_id`), `Released`, `Denied`, `NeedsConsent`, `ReleaseDecision` union,
  `Gate` (facade: `release`, `revoke`, `reclassify`, `delete_derived`, `may_move_automatically`,
  `display_policy`, `summarize_protected`), `REQUEST_FIELDS`, `RELEASED_FIELDS`,
  `FORBIDDEN_PARAMETER_NAMES: frozenset[str]`.

**Done-means:** 3 (the gate half), and the entry point for 5, 6, 7.

**What its tests must prove.** That `Gate.release` is the **only** public entry point that returns a
`Released`, and that `ModelCallRequest` carries references only — no field accepts a document string,
a path, or an `Observation`, asserted over `dataclasses.fields` type annotations. That there is **no
override keyword**: `set(inspect.signature(Gate.release).parameters)` equals exactly the published
parameter names, and the union of the parameter names with `{f.name for f in
dataclasses.fields(ModelCallRequest)}` and the same for every branch type is **disjoint** from
`FORBIDDEN_PARAMETER_NAMES` (`force`, `override`, `bypass`, `allow`, `approved`, `skip`,
`unsafe`, `trusted`, `internal`, …). Both halves matter: the whitelist proves no unpublished
parameter exists at all, the blacklist names the specific words. **This is asserted by parsing the
signature, never by scanning source text** — a source scan matches docstrings and comments, and that
technique has produced a false result eight times on this project. This is P5's `SafetyPolicy`
discipline applied to the gate: *"Two fields, and deliberately no third."*

---

### Task 12: Binding and single use

**Files:** create `src/privacy/binding.py`; test `tests/p7/test_p7_binding.py`.

**Interfaces:**
- Consumes: `release.Released`, `.ModelTarget`, `policy.Policy`, `schema.create_privacy_schema`.
- Produces: `RELEASE_LEDGER_DDL`, `BINDING_TERMS: tuple[str, str, str]` =
  `("model_target", "prompt_fingerprint", "policy_version")`, `mint_release(conn, ...) -> str`,
  `consume_release(conn, released, *, model_target, prompt_fingerprint, policy_version) -> None`,
  `ReleaseAlreadySpent`, `ReleaseNotIssued`, `BindingMismatch`.

**Done-means:** 5, and layer L1 of 3.

**What its tests must prove.** That a release is consumed on first use and that a second
`consume_release` with the same `release_id` raises `ReleaseAlreadySpent` — SPEC §6: *"A release is
consumed on first transport use."* That spending it against a different `model_target`, a different
`prompt_fingerprint`, or a different `policy_version` each raises `BindingMismatch`, three separate
tests, because the binding tuple has three terms and a test that varies only one proves only one.
That `audit_id` is **not** a binding term — two releases differing only in audit record are the same
authorization — asserted by constructing exactly that pair and showing both consume. And the
unforgeability property: a hand-constructed `Released` with a fabricated `release_id` raises
`ReleaseNotIssued`, so instantiating the dataclass outside the gate buys nothing. That last test is
the one that makes *"a call that bypasses P7 is not a policy violation to be caught in review — it is
a call that cannot be constructed"* true rather than aspirational.

---

### Task 13: The eight denials

**Files:** create `src/privacy/denial.py`; test `tests/p7/test_p7_denials.py`.

**Interfaces:**
- Consumes: `vocabulary.DENIAL_REASONS`, `classification`, `policy`, `items`, `audit.append_audit`,
  `database_agent.budget.get_ceiling`.
- Produces: `Denied` construction helpers per reason, `RemedyOption`,
  `deny(reason, *, explanation, remedy_options, evidence_refs) -> Denied`,
  `PROTECTED_RECORDS_TEMPLATE: str` (§7.3's literal name).

**Done-means:** 6.

**What its tests must prove.** One test per reason, eight tests, each reaching **exactly** that
reason and no other — the discipline P8's Done-means 2 states for its own registry, *"A code with no
fixture is an unimplemented check."* That every `Denied` carries a non-empty `explanation` and at
least one `remedy_option`, because §8.6 requires the UI to show *"what has been deferred, and why"*
and a denial with no legitimate alternative is a dead end the user cannot act on. That every denial
appends a `model_release_denied` audit event — denials are recorded on the strength of §8.2's
*"Every significant event affecting a file."* And that `dossier_over_budget` is annotated in its own
test as a **backstop that should never fire in a correct pipeline** (M9), so a future reader does not
optimise away the check on the grounds that P8 already ran the ladder.

---

### Task 14: `NeedsConsent`, its id, and the P13 seam

**Files:** create `src/privacy/consent.py`; test `tests/p7/test_p7_consent.py`.

**Interfaces:**
- Consumes: `vocabulary.CONSENT_OPTIONS`, `audit.append_audit`, `authorship.CONSENT_REQUESTED`,
  `.CONSENT_GRANTED`, `policy.grant_consent`.
- Produces: `NeedsConsent` (`consent_request_id`, `requirement`, `options`),
  `ConsentRequirement`, `open_consent_request(conn, ...) -> NeedsConsent`,
  `record_consent_choice(conn, consent_request_id, option, *, user_id, ...) -> None`,
  `pending_consent(conn, consent_request_id) -> NeedsConsent | None`, `UnknownConsentOption`.

**Done-means:** 7.

**What its tests must prove.** That all four §8.4 options are always present — *"whether to allow a
local model, a cloud model, a redacted prompt, or no model use"* — and that constructing a
`NeedsConsent` with three of them raises, because *"A surface that offers fewer has silently made the
user's decision for them"* (P13 SPEC). That opening a request appends `consent_requested` and that
**no `model_release` event exists for that `consent_request_id` until a choice is recorded** —
Done-means 7's own falsifiable form, and it needs the id, which is why Task 14 adds it. That the
recorded choice appends `consent_granted` authored by P7 even though P13 collected the gesture —
P13's SPEC: *"P13 records the collection, not the grant."* And, from the gate side, that the branch
is structurally distinct from `Denied`: `NeedsConsent` has no `reason` field, so a caller cannot map
it onto a denial reason even by accident. Whether a caller absorbs it is P8's Done-means 13 and P13's
16; **P7's obligation is to make the absorption unrepresentable, not to police it.**

---

### Task 15: Revocation, the retraction limit, and `delete_derived`'s refusal (I6)

**Files:** create `src/privacy/revocation.py`; test `tests/p7/test_p7_revocation.py`.

**Interfaces:**
- Consumes: `audit.audit_records_for`, `authorship.CONSENT_REVOKED`, `policy.revoke_consent`,
  `database_agent.events.append_event`.
- Produces: `RevocationResult` (`effective_from`, `prior_releases`, `retraction_limit`),
  `PriorRelease` (`model`, `provider`, `when`, `excerpts`),
  `revoke(conn, policy, scope, *, user_id, ...) -> RevocationResult`,
  `delete_derived(scope) -> NoReturn` raising `UnratifiedResolution`.

**Done-means:** 8.

**What its tests must prove.** That `effective_from` affects **future** gate calls only, shown by a
release minted before the revocation still consuming and one requested after it denying with
`policy_revoked`. That `prior_releases` is read from the audit log and names model, provider, time
and excerpts — *"The audit log is what makes `retraction_limit` truthful and specific rather than a
generic disclaimer."* That an attempted `DELETE` against `events` raises P1's append-only trigger, so
Done-means 8's *"never deletes an audit record"* is proven against the substrate and not against
P7's own restraint. That `retraction_limit` is always present and non-empty, because §8.4 makes it a
`must`: *"Revocation cannot necessarily retract data already sent to an external provider, so the
product must communicate that distinction clearly"* — the wording is deferred UX copy, the
**presence** is not. And that `delete_derived` raises `UnratifiedResolution` naming **I6**, so the
one function whose semantics the SPEC says are unresolved cannot be quietly implemented: *"the
candidate resolution on the table is to tombstone derived projections while keeping `events`
append-only forever, but it is **not** ratified."*

---

### Task 16: Reclassification, and §8.7's query-before-classify

**Files:** create `src/privacy/learning_seam.py`; test `tests/p7/test_p7_learning_seam.py`.

**Interfaces:**
- Consumes: `database_agent.learning.learning_records`, `.SCOPES`,
  `database_agent.events.CORRECTION_FIELDS`, `.CORRECTION_SCOPES`,
  `evidence_shape.canonical.canonical_json`, `facts_seam.SensitivityFacts`.
- Produces: `PROPOSAL_CLASS: str = "privacy"`, `basis_key_for(file_id, handling_class) -> str`,
  `suppressed(conn, file_id, handling_class) -> bool`,
  `reclassify(conn, file_id, handling_class, reason, *, user_id, ...) -> ClassificationRecord`,
  `RECORDED_ACTIONS: tuple[str, ...]` (SPEC *Correction learning*'s six).

**Done-means:** part of 2 (user revision), and the §8.7 obligation.

**What its tests must prove.** That `reclassify` writes a **new** `user_confirmed` fact that
supersedes the prior one and appends `classification_superseded`, never an overwrite. That before
assigning a class, P7 queries `learning_records(conn, "file", file_id)` and filters on
`proposal_class = "privacy"` and the composed `basis_key` **in P7**, because P1's reader filters on
neither — 10-i4-learning-ops.md assigns that to the acting part. That an unreset `polarity =
"reject"` record at the matching `basis_key` produces zero re-emissions of that classification, while
a different `basis_key` at the same scope still emits, and a reset restores emission. That the
default `correction_scope` is `file`, per §8.7's own worked warning that one transcript belonging in
one packet *"should not teach the engine that all transcripts belong there."* And that a downgrade
stores the observation **keys** the detector fired on, not ids — M14, because *"a per-row
`observation_id` dies when the extractor is upgraded, so a negative example recorded today would
silently stop resolving and the same false protection would return."* Open question 7 —
generalization of repeated reclassification — stays open and Task 21 asserts it.

---

### Task 17: `may_move_automatically`

**Files:** create `src/privacy/moves.py`; test `tests/p7/test_p7_moves.py`.

**Interfaces:**
- Consumes: `facts_seam.SensitivityFacts`, `policy.current_policy`.
- Produces: `MoveVerdict` (`allowed`, `reason`, `permitting_policy`),
  `may_move_automatically(conn, file_id, plan_version) -> MoveVerdict`.

**Done-means:** 9 (first clause; see the coverage table for the second).

**What its tests must prove.** That the verdict is `False` for protected material with no permitting
policy, `True` for protected material under a policy that explicitly permits it, and that the
permitting policy is **named in the verdict** so P11 and P12 can record it without re-deriving it —
§8.4: *"should not be moved automatically without a user policy that explicitly permits it"*, and
§7.11's *"move them out of a protected area without explicit user action."* That the verdict is
keyed on the `protected` **flag** and not inferred from the handling class, because SPEC §2 says so
outright: *"Neighbouring parts should consume the `protected` flag, not infer it from the class"*, and
Open question 1 — whether `protected` is exactly the top two classes — is not settled. And that a
policy adopted at a **later** plan version does not retroactively permit a move under an earlier one
(§8.8: *"A new plan should never silently reclassify or move old files"*).

---

### Task 18: `display_policy` and `summarize_protected`

**Files:** create `src/privacy/display.py`; test `tests/p7/test_p7_display.py`.

**Interfaces:**
- Consumes: `vocabulary.DISPLAY_FACETS`, `defaults.MORE_REDACTING`, `policy.current_policy`,
  `facts_seam.SensitivityFacts`.
- Produces: `RedactionSettings` (five facets, each `shown | redacted`),
  `ProtectedSummary` (`count`, `class_breakdown`), `display_policy(conn) -> RedactionSettings`,
  `summarize_protected(conn, scope) -> ProtectedSummary`.

**Done-means:** 10, and the display half of 12.

**What its tests must prove.** That the five facets are exactly §8.4's own list — *"whether names,
previews, thumbnails, OCR text, or location data are shown"* — and that each takes one of two values.
That `ProtectedSummary` **cannot** return a filename or a raw value, asserted over
`dataclasses.fields(ProtectedSummary)` — a type-level proof, not a runtime filter that a future
caller could pass around, and not a string scan. §8.4's example is the acceptance criterion: *"A
summary such as '11 protected identity records' may be safe to show, while a visible list of passport
filenames on a shared screen may not be."* That the default settings are the more redacting ones
(Task 6's rule, applied here). And the test must record P13's open question against this signature:
§8.4 says *"Protected branches should have configurable redaction"*, which reads per-branch, while
`display_policy()` takes no scope — P13 OQ, quoted, not resolved.

---

### Task 19: The transport guard — Done-means 3's instrument

**Files:** create `src/privacy/transport_guard.py`, `tests/p7/transport_fixtures.py`; test
`tests/p7/test_p7_transport.py`.

**Interfaces:**
- Consumes: `inspect`, `release.Released`.
- Produces: `assert_single_egress(module) -> None`, `egress_functions(module) -> list[Callable]`,
  `CONTENT_PARAMETER_TYPES: frozenset[type]` (the types a transport may **not** take: `str`,
  `bytes`, `Path`, `Observation`, `TextUnit`), `MultipleEgressPoints`, `UnreleasedContentParameter`.

**Done-means:** 3 (the instrument; see the coverage table for what remains).

**What its tests must prove.** That the checker **passes** a conforming fixture transport — one
public function, one parameter, annotated `Released` — and **fails** each of four non-conforming
ones: two entry points; one entry point taking `str`; one taking `Path`; one taking an `Observation`.
A checker only proven on the passing case is an assertion that has never been tested. That the check
reads `inspect.signature(...).parameters` and each parameter's resolved annotation, **never the
module's source text** — a source scan sees `Released` in a docstring and passes a transport that
takes a string. And the test file must carry, in a named test, the honest statement that running
this over the **real** transport is P8's Done-means 1 and cannot happen here, so the limitation is in
the suite rather than in a report nobody rereads.

---

### Task 20: The published fixtures (SPEC §11)

**Files:** create `src/privacy/fixtures.py`; test `tests/p7/test_p7_fixtures.py`.

**Interfaces:**
- Consumes: every record type above; `evidence_shape.fixtures.FIXTURES` (for the P4 substrate a
  fixture excerpt resolves against).
- Produces: `FIXTURES: tuple[GateFixture, ...]`, `GateFixture` (`number`, `spec_case`, `request`,
  `decision`, `audit_record`, `policy`), `by_number(n) -> GateFixture`,
  `FIXTURE_COVERAGE: Mapping[str, tuple[int, ...]]` (denial reason / done-means → fixture numbers).

**Done-means:** 11 (first clause; see the coverage table).

**What its tests must prove.** That there is at least one fixture per `Denied.reason` — eight — plus
a clean `Released` with redaction applied, a `NeedsConsent` returning all four options, a protected
file under **each** of the four modes, an `unreadable_unclassified` file, and a `Protected Records`
residual request: SPEC §11's list, item for item, with a test that fails if a list member has no
fixture. That **each fixture carries the audit record the gate would have appended**, and that
replaying the fixture through the real gate reproduces that record field for field — a fixture that
drifts from the implementation is worse than none. That the two fixtures carrying an obligation on P8
say so in their own metadata: `dossier_over_budget` exists *"so P8 can prove its ladder ran first — a
P8 test that reaches this denial through the normal path is a P8 failure, not a gate result"* (M9),
and the `NeedsConsent` fixture exists *"so P8 can prove it returns the branch to its caller intact"*
(B2).

---

### Task 21: The no-invention guard, and every open question held open

**Files:** test `tests/p7/test_p7_no_invention.py`.

**Interfaces:**
- Consumes: every module under `src/privacy/`, by `importlib` + `vars(module)`.
- Produces: nothing. `vocabulary.OPEN_QUESTIONS: Mapping[int, str]` is asserted here.

**Done-means:** the guard behind 1, 12, and the whole *Deferred* table.

**What its tests must prove.** By **runtime introspection of every module's namespace** — never by
searching source text, because a text guard matches comments and docstrings (the failure
`tests/p3/test_p3_no_invention.py` documents, and the reason `code_tokens()` exists) — that `src/privacy/` publishes no numeric threshold or ceiling
outside a single named allowlist, no identifier class, no redaction transform, no detection rule, no
regex, no gazetteer, no retention period, no corpus-area definition, and no default operation mode
beyond W1's two-member floor. That each of SPEC Open questions 1–11 is present in `OPEN_QUESTIONS`
with its SPEC text and that no module answers it; specifically that Open question 11 names no winner
between `offline` and `local_model`, Open question 3 defines no corpus area, and Open question 1
never infers `protected` from the handling class. That **P6 OQ11** is likewise held open. That
`src/privacy/` imports neither `ProtectedContainerRefused` nor `DatalessRefused` — the three refusals
stay three. That `subsystem = "P7"` is written in exactly one module. And, repo-wide, that the set of
packages binding a P4 text materialiser is `{evidence_shape, extractors, privacy}` and no other —
layer L2, which passes trivially today and becomes load-bearing when P8 lands.

---

### Task 22: The walking-skeleton P7 step, and 11 §9's second fixture path

**Files:** test `tests/p7/test_p7_skeleton_step.py`.

**Interfaces:**
- Consumes: `src/orchestrator.py`'s Wave-2 path, `eval_harness.bundle.bundle_files`,
  `database_agent.files_table.get_file`, the whole gate.
- Produces: nothing.

**Done-means:** 13.

**What its tests must prove.** Path one, the deterministic skeleton — where *"no privacy gate is
exercised, because nothing leaves the machine"* — must nonetheless assert five things: the
classification exists for the scanned file; the gate is installed on the only egress path;
`release` was called **zero** times; the audit log is empty; and a deliberate attempted call under
`offline` returns `Denied` with reason `mode_forbids_target`. That is the seam test — that the door
exists and is shut. It must also assert that after classification the Wave-2 bundle's
`handling_class` is non-null, closing the loop `src/orchestrator.py:259` left open. Path two is
11 §9's addendum, still without a live model: *"a dossier that requires sensitive text; `Gate.release`
returns `NeedsConsent`; P13 presents the four §8.4 options; choosing `no_model_use` does not become
`abstain` inside P8."* P7 owns the first two clauses and asserts them here; the third and fourth are
P13's and P8's, and this test names them as **deferred to those parts** rather than faking a
P8 that does not exist.

---

## Coverage — every Done-means item, and the task that proves it

| # | Done-means (abbreviated) | Task | Fully provable inside P7? |
|---|---|---|---|
| 1 | Five classes, four modes, closed; OOV is a load error | 2 | **Yes** |
| 2 | Exactly one current `sensitivity` fact; absence → `unreadable_unclassified` | 3, 4 | **Yes**, against the P6 fixture. Against real P6: no — P6 is unbuilt and its OQ11 is open. |
| 3 | **Static property:** the transport has one entry point; its only content parameter is a `Released` | 19 (instrument), 12 (L1), 9+21 (L2) | **No — and this is a finding.** The transport is P8's. P7 proves the instrument, the unforgeable token, and the single materialisation locus. The property itself is P8 Done-means 1. |
| 4 | Every `Released` carries an `audit_id` already in the log | 10 | **Yes** |
| 5 | Bound to one `model_target` + `prompt_fingerprint`; consumed on first use; replay fails | 12 | **Yes** |
| 6 | Denials with reasons for at minimum the seven named | 13 (all eight), 7 (`always_local_item`, `whole_document_requested`), 5 (`mode_forbids_target`) | **Yes** |
| 7 | `NeedsConsent` with all four options; no caller converts it; log holds `consent_requested` and no `model_release` until a choice | 14 | **Partly.** The gate-side form — the one Done-means 7 itself states as testable — yes. *"no caller converts it"* is P8 Done-means 13 and P13 Done-means 16. |
| 8 | `revoke` is forward-only, deletes no audit record, returns prior releases + retraction limit | 15 | **Yes** |
| 9 | `may_move_automatically` false for protected absent a permitting policy; **P11/P12 consume rather than re-derive** | 17 | **Partly.** First clause yes. The second is a property of P11 and P12, which do not exist; P7 makes it *possible* by naming the permitting policy in the verdict. |
| 10 | `summarize_protected` returns counts and breakdown, cannot return filenames or content | 18 | **Yes** — proven at the type level over `dataclasses.fields`. |
| 11 | Every item above has a published fixture, **and P8's harness passes its own tests against them with P7 unimplemented** | 20 | **Partly.** The fixtures, yes. *"P8's harness passes"* is P8's test run and cannot execute here. |
| 12 | Local-first default under fresh-install and migrated-from-nothing; every silent redaction setting more redacting; **negative:** no path yields `hybrid` / `cloud_assisted` | 6 | **Yes** — but see the note below on the SPEC's own "by grep" phrasing. |
| 13 | Walking skeleton: classification exists, gate installed, `release` called zero times, audit log empty, `offline` attempt → `mode_forbids_target` | 22 | **Yes** for path one. 11 §9's path two is P7's for two clauses of four. |

**Note on Done-means 12's "by grep".** The SPEC says the negative half is *"asserted by fixture and
by grep over the shipped defaults, the way Done-means 1 asserts the closed vocabularies."* Task 6
implements the fixture half as written and replaces the grep with **runtime introspection of
module-level constants**, for the reason the Global Constraints give: `hybrid` and `cloud_assisted`
appear legitimately in `vocabulary.py`, in `MODE_SEMANTICS`, in docstrings and in denial messages, so
a grep either passes vacuously (excluding those files) or fails on a comment. This is a deliberate
strengthening of the SPEC's stated technique, not a weakening, and it is flagged so the reviewer can
reject it.

**Three items are not fully provable inside P7 — 3, 9, 11 — plus half of 7.** None is a gap being
hidden: each is a property of a part that does not exist yet, each has the P7-side half built and
tested, and each names the downstream Done-means item that closes it. That split is reported.

---

## Negative tests — this part is a gate, so these are the tests that matter

| What must be refused | How it is asserted | Task |
|---|---|---|
| `paths` as a releasable item | `AlwaysLocalRequested` on construction | 7 |
| `complete extracted text` | `AlwaysLocalRequested`; separately `WholeDocumentRequested` for a span covering the unit | 7 |
| `OCR output` | `AlwaysLocalRequested` | 7 |
| `file hashes` | `AlwaysLocalRequested` | 7 |
| `image EXIF` | `AlwaysLocalRequested` | 7 |
| `GPS` | `AlwaysLocalRequested` | 7 |
| `user edits` | `AlwaysLocalRequested` | 7 |
| `group memberships` | `AlwaysLocalRequested` | 7 |
| `raw sensitive values` | `AlwaysLocalRequested`; the value set comes from P5's `extraction_sensitivity_signal`, not from a P7 rule | 7 |
| protected file + cloud target under `offline` | `Denied(mode_forbids_target)` | 13 |
| protected file + cloud target under `local_model` | `Denied(mode_forbids_target)` | 13 |
| protected file + cloud target under `hybrid` | `Denied(protected_cloud_target)` — §8.4's *"Sensitive files remain local"* | 13 |
| protected file + cloud target under `cloud_assisted` **without** a grant for that area | `Denied(protected_cloud_target)`; Open question 3 leaves the area undefined, so the test parameterises the scope | 13 |
| a file with no classification | `Denied(unclassified)`; and **never** a silent `public_low` | 3, 13 |
| a `Protected Records` residual file | `Denied(protected_records_template)`; §7.3 forbids filenames **and** content | 13 |
| a request over `max_dossier_tokens` | `Denied(dossier_over_budget)`, annotated as an M9 backstop | 13 |
| a revoked policy | `Denied(policy_revoked)`; a release minted before the revocation still consumes | 15 |
| **replay:** same `release_id` twice | `ReleaseAlreadySpent` | 12 |
| **replay:** different `model_target` | `BindingMismatch` | 12 |
| **replay:** different `prompt_fingerprint` | `BindingMismatch` | 12 |
| **replay:** different `policy_version` | `BindingMismatch` | 12 |
| a hand-constructed `Released` | `ReleaseNotIssued` — the token is unforgeable | 12 |
| **no override keyword exists** | `set(inspect.signature(Gate.release).parameters)` equals the published names exactly (whitelist), **and** the union of those names with `dataclasses.fields(...)` of the request and all three branch types is disjoint from `FORBIDDEN_PARAMETER_NAMES` (blacklist). **Parsed from the signature; never a source-text scan** — comments and docstrings match; where a token assertion is unavoidable use `code_tokens()` (`tests/p3/test_p3_no_invention.py`), which excludes them by walking the AST. | 11 |
| `NeedsConsent` with fewer than four options | raises at construction | 14 |
| a `model_release` before a consent choice is recorded | asserted absent by `audit_records_for(consent_request_id=...)` | 14 |
| deleting an audit record | P1's `events_no_delete` trigger aborts | 15 |
| updating an audit record | P1's `events_no_update` trigger aborts | 15 |
| `delete_derived` | `UnratifiedResolution` naming **I6** | 15 |
| an automatic move of protected material with no permitting policy | `MoveVerdict(allowed=False)` with a reason | 17 |
| `summarize_protected` returning a filename | impossible at the type level: `dataclasses.fields(ProtectedSummary)` has no such field | 18 |
| a default of `hybrid` or `cloud_assisted` | `resolve_default_policy` over every reachable stored state, plus introspection of module constants — not a grep | 6 |
| a transport with two entry points | `MultipleEgressPoints` on the non-conforming fixture | 19 |
| a transport taking `str` / `Path` / `Observation` | `UnreleasedContentParameter`, three fixtures | 19 |
| a span that does not anchor | `UnresolvableSpan`; never a repaired substring | 9 |
| a `basis = detector` classification with no evidence | `UnbackedClassification` | 3 |
| a suppressed reclassification (unreset `reject` at the same `basis_key`) | zero re-emissions; a different `basis_key` still emits | 16 |

---

## Deferred — manual design required

Reproduced from [`SPEC.md`](SPEC.md) *Deferred*; nothing is added and nothing is resolved.

| Deferred | Defined by | Held in this plan as |
|---|---|---|
| The sensitivity detection rules themselves | §8.4's five kinds; §3.15's safety domains | A classification **writer** with no detector behind it. P5's `extraction_sensitivity_signal` is a signal, not a rule. |
| Gazetteer contents | §3.7 | Nothing. Task 21 asserts none exists in `src/privacy/`. |
| The 200–300 template library and each template's `privacy rules` / `sensitivity policy` | §5.7 | Only the predicate §5.7's validator calls — `may_move_automatically` and the `protected` flag. |
| Residual library contents beyond §7.3's nine names | §7.3 | `PROTECTED_RECORDS_TEMPLATE`, the one literal name §7.3 gives that P7 uses. |
| Domain fact-schema fields beyond §3.11's table | §3.11 | Only `sensitivity status`, which is literally in §3.11's universal set. |
| **Identifier classes and the redaction transform** | §8.4's *"redacted identifiers"* | Two **injected protocols with no default** (Task 8). The class is an opaque string. |
| Numeric values for every ceiling | §8.6 | `budget.get_ceiling(conn, "model.max_dossier_tokens_per_call")`. No literal anywhere. |
| Consent-prompt and retraction-limit wording | §8.4 | The **presence** of `retraction_limit` is asserted; the wording is not. |

## Open questions — carried forward, unresolved

Quoted from [`SPEC.md`](SPEC.md) *Open questions*. Task 21 holds each one open by name.

1. **Is `protected` exactly the top two handling classes?** *"§8.4 lists five classes and,
   separately, five kinds of material that 'enter a protected state immediately', without stating the
   relation."* Consumed as a flag, never inferred (Task 17).
2. **Filename vs. path.** *"This contract adopts the reading that makes §7.3 non-vacuous (§4 above)
   and flags it. Affects P8 and P11 directly."* Task 7 implements the flagged reading and names the
   question in the test.
3. **What is a "corpus area"?** *"Consent grants cannot be scoped until this is named."* Task 5
   parameterises the scope and defines none.
4. **Deletion versus append-only.** *"Which wins, what counts as 'derived', and are audit records
   themselves deletable?"* See I6 below.
5. **Does `unreadable_unclassified` permit a *local* model call?** *"Reading escalation strictly
   denies local calls on unclassified files, which may block exactly the OCR-opaque screenshots §2.7
   and §7.8 want a model to interpret."* Task 13's `unclassified` denial is parameterised on
   locality and the parameter has **no default**.
6. **Is a local-model call a consent event or only an audit event?** *"The threshold at which a local
   call needs a prompt is unstated."* Task 10 audits every call; Task 14 requires consent only where
   a caller asks for it.
7. **Does repeated reclassification generalize?** Task 16 keeps `file` scope and generalizes never.
8. **May a replay bundle carry audit records and excerpt spans?** Affects P2. P7 writes nothing into
   a bundle; `open_bundle`'s `policy_settings` slot is the only surface it touches.
9. **What is an "external connector" besides a model?** *"If a connector is added later, does it
   route through `Gate.release`?"* `ModelTarget.locality` is `local | cloud` and no third value.
10. **Retention.** *"The design states no retention period anywhere."* No period appears in
    `src/privacy/`; Task 21 asserts it.
11. **The local-first default — narrowed, not open-ended (W1).** *"What remains genuinely open is
    only **which of those two** ships."* Task 6 asserts the floor and refuses to name the winner.

**UNRESOLVED — I6, deferred to this part's build (ratified 2026-08-19).** *"§8.4's right to 'review
and delete local derived data' contradicts §8.2's R6, which forbids updating or deleting an event.
The product cannot ship unable to forget a scanned passport's OCR text, and cannot ship silently
deleting from the provenance log. The candidate resolution on the table is to tombstone derived
projections while keeping `events` append-only forever, but it is **not** ratified. P7 must resolve
this before it is built."* **This plan does not resolve it.** Task 15 ships `delete_derived` as a
function that refuses and names I6, so the surface exists and the semantics do not. Every other task
is buildable without the answer; **Task 15 alone is blocked on Joseph**, and the plan says so rather
than guessing at a tombstone design P1 has only been told to keep possible.

---

## SPEC vs code as built — mismatches found

Each was verified by importing the package and reading `inspect.signature`, not from a PLAN.

1. **`files.sensitivity_state` has no writer.** The column exists (`db.py` `FILES_DDL`) and
   `files_table.FILES_COLUMNS` names it, but `observe_path`, `record_file` and
   `invalidate_extraction_state` never set it and P1 publishes no setter — while
   `set_extraction_status` exists for the sibling column. `src/orchestrator.py:259` already reads it.
   Task 4 injects a writer and reports the gap; the precedent is P5's identical report about
   `extraction_status_by_tier`, which P1 then closed.
2. **The audit record has no columns.** SPEC §7 lists nineteen field names; `events._WRITABLE` has
   seventeen and none of P7's own is among them, and MINOR 1 fixes §8.2's list at eleven forever.
   Resolved in this plan as canonical JSON in `explanation` — stated in the preamble because every
   task depends on it.
3. **`learning_records` does not filter on `proposal_class` or `basis_key`.** SPEC *Correction
   learning* says P7 *"queries P1 `learning_records` for `proposal_class = privacy` and `basis_key =
   (file_id, handling_class)`"*; the real signature is `learning_records(conn, scope, subject_id)`
   and the filtering is the caller's (10-i4-learning-ops.md assigns it there). Task 16 filters in P7.
4. **P5 publishes a sensitivity surface P7's Contract-in does not mention.**
   `extraction_sensitivity_signal` (`run_id`, `observation_key`, `signal`, `basis`, `observed_at`)
   and `sensitivity_signals_for(conn, run_id)`, with `POTENTIALLY_SENSITIVE = "potentially
   sensitive"` — P5's docstring says it is *"for P7 to act on."* Added to Contract-in above.
5. **There is no marking named "indexed-but-unreadable".** The SPEC's P5 row names one; the real
   surface is `ExtractionRun.completeness` over nine values. Task 3 maps them explicitly, per value.
6. **`NeedsConsent` carries no id, but P13's `subject_ref` is a `consent_request_id`.** Task 14 adds
   the field; the name is P13's.
7. **The P5 → P7 back-edge is a zero-argument predicate.** `transcription_authorized: Callable[[],
   bool]`, called with no arguments at `src/extractors/long_tail.py:204`. Every P7 surface is
   per-file or per-scope. Task 5 adapts; the mismatch is reported, not patched.
8. **`observations_by_key` returns a list.** SPEC §4 speaks of resolving *"by `(observation_key,
   span)`"* as if it were single-valued. Task 9 must publish a current-row rule.
9. **`file_facts` has no `protected` column and no `basis` column**, and P6's `origin` vocabulary is
   not P7's `basis` vocabulary. SPEC §2's record has no home in P6's published shape.
10. **Three spellings of one field.** `sensitivity` (P7 SPEC), `sensitivity status` (§3.11, P6),
    `sensitivity_state` (P1's column).
11. **P6 OQ11 is open.** P7's Contract-in states an answer to it. Held open here.

## SPEC vs §8.4 — where the design and the contract differ

1. **`filename` is not one of §8.4's releasable kinds.** §8.4 permits *"selected excerpts, redacted
   identifiers, candidate labels, non-sensitive metadata, and evidence references"* — five — and puts
   *"Paths"* in the always-local set. The SPEC adds a sixth, `filename`, under its own flagged
   reading. The SPEC flags this itself (Open question 2); recorded here because **the design wins and
   the design does not name it**.
2. **"Verbatim" is not quite verbatim.** SPEC §2 introduces the three protected consequences as
   *"verbatim from §8.4"*; §8.4's sentence is *"Protected material should not be included in
   cloud-model prompts by default, should not display raw content in general group summaries, and
   should not be moved automatically without a user policy that explicitly permits it."* The SPEC's
   rendering is faithful in substance and lightly normalized in grammar. Task 2 stores §8.4's
   sentence, not the SPEC's rendering.
3. **Mode identifiers are the SPEC's, not the design's.** §8.4 names *"Fully offline mode"*,
   *"Local-model mode"*, *"Hybrid mode"*, *"Cloud-assisted mode"*; the SPEC's identifiers are
   `offline`, `local_model`, `hybrid`, `cloud_assisted`. Same relationship as identifier-to-display-
   name for the handling classes. Task 2 pins both.
4. **No disagreement found on:** the always-local nine, the four consent options, the five display
   facets, the six audit fields, the retraction-limit `must`, the local-first `must`, the four
   mode semantics, or the aggregate-safe example. Each was compared word for word against
   `00-database-agent-product-design.md`.

## NEEDS JOSEPH

1. **I6.** The unratified deletion-versus-append-only resolution. Task 15 is blocked on it. Quoted
   verbatim above.
2. **Which of `offline` and `local_model` ships as the install default** (Open question 11) — *"which
   turns on whether a local model is assumed present — the design names no answer and P7 will not
   guess one."*
3. **What is a "corpus area"** (Open question 3) — consent grants cannot be scoped until it is named.
4. **Does `unreadable_unclassified` permit a local model call** (Open question 5) — the parameter has
   no default until this is answered.
5. **Whether `protected` is exactly the top two handling classes** (Open question 1) — P9, P10 and
   P11 all consume the answer.
6. **Identifier classes and the redaction transform** — deferred by the SPEC, injected by this plan,
   and a shipped product needs them.
7. **Retention** (Open question 10) — how long audit records, consent grants and superseded
   classifications are kept.
