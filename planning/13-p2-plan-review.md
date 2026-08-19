# P2 Eval/Replay Harness — Plan Review

## Verdict

**Do not execute as written. Four blocking findings, all mechanical, none requiring a redesign.**
The plan's architecture is sound and its refusals are disciplined — the problems are that P1 moved
under it twice today and one patch landed half-wired. Fix the four, and Tasks 1–17 are executable
against P1 and fixtures alone with no dependency on any unbuilt part.

**Reviewed version:** `planning/parts/P2-eval-replay-harness/PLAN.md`, 5,885 lines, mtime
2026-08-20 01:20:24. *The file changed under me mid-review (5,841 → 5,885 lines); B4 below is in
the added text. All four blocking findings were re-verified against the 01:20:24 version.*
P1 baseline: `python3 -m pytest -q` → **150 passed in 4.37s**.

## Counts

| | Count |
|---|---|
| Blocking | **4** |
| Non-blocking | 11 |
| Contract-out surfaces with no task | 0 (one, `assertion.evidence_ref`, has a task that never fills it — N2) |
| Done-means with no task | 0 |
| Tasks secretly needing P3/P4/P6/P8/P9/P10/P11 | **0** |
| Invented thresholds / ceiling numbers | 0 |
| Places P2 appends an event as another part | 0 |
| Earlier review's findings now dead | 0 of 7 (P2-B was answered, but by the patch that is B4) |

| Blocking | Where | One line |
|---|---|---|
| **B1** | Task 1, `test_p2_creates_no_p1_table` | Asserts `files`/`events` are absent; `open_database` now creates them. |
| **B2** | Task 1, `tests/eval/conftest.py` | Shadows P1's `tests/conftest.py`; 4 P1 modules fail to collect and the whole suite aborts. |
| **B3** | Task 17, `test_skeleton_p2_step` | Calls `p3_basic_record(document)` without importing it — `NameError`. |
| **B4** | Task 13, `assert_shadow_wrote_nothing` | Reads `record["foreign_table_counts"]`, which no column, no INSERT and no reader ever produces — `KeyError`. |

---

## Do not execute these as written

### B1 — Task 1's `test_p2_creates_no_p1_table` fails against the live `open_database`

**Where:** Task 1, Step 1, `tests/eval/test_store.py`:

```python
def test_p2_creates_no_p1_table(eval_conn):
    # §0: each part owns its own tables. P2 does not create, alter, or shadow
    # `files` or `events`; P1's create_schema is the only thing that makes them.
    create_eval_schema(eval_conn)
    present = _table_names(eval_conn)
    assert "files" not in present
    assert "events" not in present
```

and Task 1, Step 3, `tests/eval/conftest.py`:

```python
@pytest.fixture()
def eval_conn(tmp_path: Path):
    """P1's handle (§0: one local database). P2 owns tables inside it."""
    c = open_database(tmp_path / "agent.sqlite")
```

**What:** P1's `open_database` now calls `create_schema` itself —
`src/database_agent/db.py:52-56`:

```python
    # Contract out §6 publishes "one local SQLite database ... transactional and
    # inspectable" — a handle whose tables do not exist is not that. create_schema
    # stays public and idempotent for callers that want it explicitly, but no
    # neighbour has to remember a second call to get a usable database.
    create_schema(conn)
```

so `eval_conn` hands back a connection where `files` and `events` already exist. Verified:

```
['budget_ceilings', 'events', 'files', 'learning_resets', 'scan_resource_usage',
 'sqlite_sequence', 'vector_arrays']
files present: True | events present: True
```

Both asserts fail on the first run. Step 5 claims `Expected: PASS — 8 passed`.

**Why blocking downstream:** it is the *first* task. An executor following
`superpowers:subagent-driven-development` hits a red test it cannot make green without either
editing P1 (forbidden by the plan's own *"P2 does not modify any P1 file"*) or rewriting the guard.
A guard rewritten under pressure to get to green is a guard deleted. The property is still worth
keeping — rewrite it to diff table names across `create_eval_schema`, which tests what it means:

```python
def test_p2_creates_no_p1_table(eval_conn):
    before = _table_names(eval_conn)
    create_eval_schema(eval_conn)
    added = _table_names(eval_conn) - before
    assert "files" not in added and "events" not in added
    assert added <= set(EVAL_TABLES)
```

### B2 — creating `tests/eval/conftest.py` breaks P1's existing suite at collection time

**Where:** Task 1, Step 3, justified in *Dependency on P1*:

> **P2 does not modify any P1 file.** Not `db.py`, not `pyproject.toml`, not `tests/conftest.py`.
> P2's schema function is its own, its fixtures live in `tests/eval/conftest.py`, and its tests live
> in `tests/eval/` so that P1's `tests/conftest.py` stays untouched.

**What:** with pytest's default `prepend` import mode and no `__init__.py` under `tests/`, **both**
conftest files are imported as the top-level module `conftest`. The second one imported wins in
`sys.modules`, and P1's five test modules that do `from conftest import p3_basic_record`
(`tests/test_files_table.py:6`, `tests/test_identity.py:74`, `tests/test_skeleton_p1_step.py:11`,
`tests/test_verify.py:6`, `tests/test_adversarial.py:56`) resolve against the wrong file.

Verified on a copy of this repo with only `tests/eval/conftest.py` (exactly as the plan writes it)
and one trivial P2 test added:

```
tests/test_verify.py:6: in <module>
    from conftest import p3_basic_record
E   ImportError: cannot import name 'p3_basic_record' from 'conftest'
    (/…/tests/eval/conftest.py)
ERROR tests/test_files_table.py
ERROR tests/test_identity.py
ERROR tests/test_skeleton_p1_step.py
ERROR tests/test_verify.py
!!!!!!!!!!!!!!!!!!! Interrupted: 4 errors during collection !!!!!!!!!!!!!!!!!!!
4 errors in 0.53s
```

(`tests/test_adversarial.py` does the import inside a function, so it survives collection and fails
at call time instead.)

**Why blocking downstream:** the plan's own gates stop working. Task 1 Step 5
(`pytest tests/eval/test_store.py -v` → "8 passed") and Task 17 Step 3 (`pytest -q` → "P1's suite
plus P2's Tasks 1–17") both run against a suite that is *Interrupted*: nothing executes, P1 goes
from 150 green to uncollectable, and every task from 2 onward is "validated" by a run that never
happened. The failure is also mis-signposted — it reads as a P1 defect.

`--import-mode=importlib` does **not** fix it (P1's `from conftest import …` then raises
`ModuleNotFoundError`; same four errors). The minimal fix, touching no P1 file and no
`pyproject.toml`, is one empty file:

```
tests/eval/__init__.py
```

which makes the module names `conftest` and `eval.conftest`, keeps `tests/` on `sys.path`, and
leaves `from conftest import p3_basic_record` working from `tests/eval/` as well. Verified: with that
file added, `pytest -q` reports **152 passed** (P1's 150 plus two P2 smoke tests). Add it to Task 1's
*Files* list, its *File Structure* block, and its commit.

### B3 — Task 17 calls `p3_basic_record` but never imports it

**Where:** Task 17, Step 1, `tests/eval/test_skeleton_p2_step.py`. The import block is:

```python
from pathlib import Path

from database_agent.budget import all_ceilings
from database_agent.db import create_schema
from database_agent.files_table import get_file, observe_path

from eval_harness.assertions import assert_run, assertions, verdict_counts
…
from eval_harness.vocabulary import DIMENSIONS, STAGE_IDS
```

and the body calls:

```python
    file_id = observe_path(
        eval_conn, document, author="P3", component_version="p3-fixture",
        # R2 is P3's to compute once (O5); P1 stores it and derives none of it, so
        # the fixture standing in for P3 supplies it. P1's signature requires these
        # with no default — a default would let P1 re-derive them silently.
        **p3_basic_record(document),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="scanned", materialized=True,
    )
```

**What:** `p3_basic_record` is an undefined name in that module — `NameError`. It is not a pytest
fixture (fixtures arrive as parameters; this is a bare call), it is a plain module-level function in
**P1's** `tests/conftest.py:23`, and it is not in the `tests/eval/conftest.py` Task 1 creates. Every
P1 test that uses it imports it explicitly.

**Why blocking downstream:** Task 17 is Done-means 11, the walking-skeleton step, and the plan calls
it "the integration test every later part must keep green". It cannot run at all.

**The patch is otherwise correct, and this should not be re-litigated.** The live signature is

```python
def observe_path(conn, path, *, author, component_version, filename,
                 normalized_filename, extension, observed_size, observed_timestamps,
                 parent_folder_context, mime_type, detected_format, scan_state,
                 materialized) -> str:
```

(`src/database_agent/files_table.py:129-142`), and `p3_basic_record` returns exactly
`{filename, normalized_filename, extension, observed_size, observed_timestamps}` — the five required
keywords, no more, no fewer, colliding with none of the explicit arguments. Add
`from conftest import p3_basic_record`. That import only resolves once B2 is fixed.

### B4 — Task 13's `assert_shadow_wrote_nothing` reads a field nothing ever writes

**Where:** Task 13, `src/eval_harness/shadow.py` (in the text added at 01:20):

```python
    opened = json.loads(record["foreign_table_counts"])
    now = foreign_table_counts(conn)
    changed = {n: (opened.get(n), now[n]) for n in now if opened.get(n) != now[n]}
```

with the docstring above it:

> So the run also snapshots the row count of EVERY table P2 does not own, at
> open, and this compares.

**What:** the snapshot is never taken and the field does not exist. `foreign_table_counts` appears
exactly three times in the plan — its `def`, this read, and this call. Concretely:

- `SHADOW_DDL`'s `shadow_run` table declares nine columns and **no `foreign_table_counts`**;
- `run_shadow`'s INSERT names six columns and never calls `foreign_table_counts`;
- `shadow_record`'s returned dict has eight keys and **no `"foreign_table_counts"`**.

So `record["foreign_table_counts"]` raises `KeyError: 'foreign_table_counts'`.
`test_the_three_empties_are_provable` calls `assert_shadow_wrote_nothing(eval_conn, shadow_id)`
expecting it not to raise, and gets a `KeyError`.
`test_a_shadow_run_that_wrote_live_state_is_caught` happens to pass, because it makes
`move_plan_entries` non-empty and raises `ShadowWroteLiveState` before reaching the broken line —
which is worse, not better: half the suite goes green over a mechanism that does not exist.

**Why blocking downstream:** Done-means 9 is the one place P2 proves shadow mode changes nothing
user-visible, and this is precisely the finding the earlier review raised as **P2-B** ("the 'proved
not promised' claim is self-referential"). The response was the right design — a foreign-table row
count snapshot catches an adapter that writes P10's table without confessing, and keeps working when
P10 and P12 land without this function being edited. It is simply not wired. Three edits complete it:

1. add `foreign_table_counts TEXT NOT NULL` to `SHADOW_DDL`;
2. in `run_shadow`, capture `snapshot = foreign_table_counts(conn)` **before** `replay_bundle` and
   include `canonical_json(snapshot)` in the INSERT;
3. add `"foreign_table_counts": row["foreign_table_counts"]` to `shadow_record` (leave it as the
   JSON string, since `assert_shadow_wrote_nothing` calls `json.loads` on it).

Also add `foreign_table_counts` to Task 13's *Produces* line, and a test that a foreign-table write
during a shadow run is actually caught — otherwise nothing exercises the new branch.

---

## Non-blocking findings

### N1 — the fourteen JSON fixture files are written with `//` comments and will not parse

**Where:** Task 6, Step 1 (`p4_runs.json`, `p4_text_units.json`) and Task 14, Step 1
(`adversarial/A01.json` … `A12.json`), e.g.:

```json
// tests/eval/fixtures/p4_runs.json
// P4 SPEC Record 2 (D5). Field names and example values copied from that record.
// P2 defines none of this shape. Replace with real P4 rows when P4 lands.
[
```

**What:** both consumers use `json.loads(path.read_text(encoding="utf-8"))`. JSON has no comment
syntax; an executor writing the block verbatim gets
`JSONDecodeError: Expecting value: line 1 column 1 (char 0)` on the first load. Verified. The same
`# path` marker convention is harmless in the Python blocks and fatal here.
Not blocking because it fails loudly at the loading line with an unambiguous error and the fix is to
delete the comment lines. Move the provenance note into the task prose, not the file body.

### N2 — `evidence_ref` is a published Contract-out §6 field that no task ever fills

**Where:** Task 10's prose states:

> `assert_run` **copies whatever `evidence_ref` the dimension value carried** and the writer refuses
> a value whose shape is an observation *id*

but `assert_run`'s implementation ends with:

```python
            verdict=verdict, no_verdict_reason=reason, evidence_ref=None,
```

and `DimensionValue` (Task 4) is `dataclass(frozen=True)` with fields
`dimension, subject_ref, outcome, value` — **there is no `evidence_ref` on it**, so a dimension value
cannot carry one. The column is created, guarded by `ObservationIdRefused`, and always `NULL`.

**Why it matters:** SPEC *Cross-cutting answers → Provenance* says *"Every `assertion` carries
`evidence_ref`, so a verdict can be traced to the observation or event that produced it (§8.2's
reconstruction requirement)."* That obligation is unmet, and the prose describes a copy path that
does not exist. This is the one Contract-out surface whose task does not deliver it. Either add
`evidence_ref` to `DimensionValue` and thread it through `assert_run`, or change the prose to say
plainly that `evidence_ref` is reserved and unpopulated until a stage exists to supply one — and
list it under *Known gaps*.

### N3 — the "immutable once sealed" claim holds for three of the eight bundle tables

**Where:** Task 5's prose:

> A bundle is opened, filled, and sealed; after `sealed_at` is stamped, every `UPDATE` on the
> manifest and every `INSERT`, `UPDATE` or `DELETE` on **a child row** raises.

The DDL creates seal triggers for `bundle_manifest` and `bundle_file_entry` only. Task 8 instructs
*"the same three seal triggers, one per new table"* for `bundle_accepted_group` and
`bundle_expectation` — as prose, not written SQL. Tasks 6 and 7 add
`bundle_extraction_output`, `bundle_extraction_run`, `bundle_text_unit` and
`bundle_learning_record` with **no triggers at all**. Those four are protected only by
`_require_open` inside the Python writers, so a raw `INSERT` into a sealed bundle succeeds.
Two consequences: the immutability guarantee is uneven, and Task 8's trigger set is the only code in
the plan given as an instruction rather than written out — which contradicts the Self-Review's
*"Placeholder scan: no 'similar to Task N'"*. Write all the triggers out, or restate immutability as
writer-enforced for the six content tables.

### N4 — `_DDL_SCRIPTS` vs `_ddl_scripts` (two names for one thing)

Task 1 defines `def _ddl_scripts() -> list[str]:`. Task 3's *Files* line says *"append `RUN_DDL` to
`_DDL_SCRIPTS`"* and Task 3 Step 3 says *"Replace the `_DDL_SCRIPTS` placeholder"*. Tasks 4, 5, 10,
12, 13 and 14 all spell it `_ddl_scripts`. Prose only; every code block is consistent. Fix the two
mentions.

### N5 — the P7 forbidden-name guard is spelled two different ways

Task 5's `test_p2_source_carries_no_p7_class_or_mode_name` forbids eight names:

```python
    forbidden = ("public_low", "personal_non_sensitive", "sensitive_personal",
                 "highly_sensitive_credential_bearing", "unreadable_unclassified",
                 "local_model", "cloud_assisted", "hybrid")
```

Task 16's `FOREIGN_VOCABULARY` lists the same names **minus `hybrid`**. Two guards for one rule that
disagree on one member is "one name, one concept" in miniature: whichever runs last defines the rule.
Make Task 16 the single owner and have Task 5 import from it, or drop `hybrid` from both — it is an
ordinary English word and the likeliest false positive of the eight.

### N6 — P2 mints four strings no SPEC publishes

`no_verdict_reason ∈ {"stage_error", "expectation_not_applicable"}`, the `verdict_counts` bucket key
`"unverdicted"`, and `CaseResult.verdict ∈ {pass, fail, not_run}`. The plan is honest about the first
three (*Known gaps*: "Recommended SPEC change, not made") and the reasoning — a `NULL` reads as
*unknown*, a fabricated verdict reads as an answer — is right. Flagging it only because §8.5's
user-facing evaluation view is **P13's**, so these strings will be rendered by a part that has never
seen them. Put them in the SPEC before P13 invents its own names for the same states.

### N7 — an adapter that returns `[]` is recorded as `abstained`, which it is not

Task 9's runner:

```python
        if not results:
            # P2's own bookkeeping for a stage that ran and returned nothing. It
            # is not a claim about any stage's semantics …
            record_stage_output(… subject_ref=bundle_id, outcome="abstained" …)
```

This writes an `abstained` envelope row that does not mean §6.10's abstention, in the same table and
column where every other `abstained` row does. It is harmless to the verdicts (it carries no
dimension value and its `subject_ref` is the bundle id, so `assert_run` never matches it), and none
of the five `OUTCOMES` fits better. But `stage_outputs` is a published reader, and a consumer
counting abstentions per stage will count these. Either give it a `subject_ref` convention that is
obviously not a subject, or record nothing and let the stage's absence from `stage_output` speak —
and say which in the prose.

### N8 — `StageResult`'s field order differs between the Interfaces line and the dataclass

Task 9's Interfaces line: *"`StageResult` (frozen dataclass: `outcome`, `payload`, `inputs`,
`budget_state`, `subject_ref`, `values`)"*. The dataclass is
`(subject_ref, outcome, payload, inputs, budget_state, values)`. Every construction in the plan uses
keywords, so nothing breaks — but the Self-Review claims field-order consistency as a checked
property, and this is the one place it does not hold.

### N9 — the comparison's per-dimension counts do not partition the subjects

`compare_runs` increments `unchanged_count` when the verdicts match, and otherwise files the subject
under `deferral_changed`, `newly_matching` or `newly_divergent` — but a subject that moved between
two *failing* verdicts (`divergent` → `abstained_incorrectly`, say) lands in none of the four. It
appears in `disagreements[]` only. That is defensible (the SPEC publishes exactly those four fields),
but a reader summing the four will silently under-count, which is the legibility failure §8.6 warns
about. Worth one sentence in the prose saying so.

### N10 — two adversarial fixtures encode one correct outcome where the design names several

A08's `expected_value` is `{"outcome": "leave_in_place"}`, but the SPEC's A8 expected outcome is
*"labelled generic screenshot / unresolved image; **leave in place or an approved Screenshot
Inbox**"*. A11's is `{"outcome": "place", "destination": {"node_role": "shared-material"}}`, but §6.9
is *"prefer an approved shared branch if one exists; **otherwise abstain or ask for a primary
home**"* — and A11's fixture bundle declares no plan tree, so nothing in it establishes whether an
approved shared branch exists. With `verdict_for` doing exact equality over a single
`expected_value`, a correct system taking a legal alternative scores `fail`. The fixture bodies are
explicitly hand-authored per the SPEC, so this is fixture authorship rather than a contract defect —
but the *format* is P2's, and it cannot express a disjunction. Either add the missing precondition
rows to A11's bundle, or note in Task 14 that a case's expected value pins one of several legal
outcomes by choice.

### N11 — refusing `text_units` on a `metadata_safe` bundle is a decision, loudly labelled

`add_text_unit` raises `NotImplementedError` naming Open question 5 rather than allowing or
forbidding silently. That is the right call and it is reversible in one line. The consequence should
be stated where Done-means 1 is claimed: dimension 1 (*"Did the expected text … appear?"*) is
**unassertable** in a `metadata_safe` bundle, so Done-means 1's *"in both `corpus_form` variants,
with every field in §8.5's contents list present"* holds only for `snapshot`. The SPEC already
carves this out ("Populated when corpus_form = snapshot"), so this is a documentation gap, not a
contradiction.

---

## Already sound — do not re-litigate

Each of these I checked directly against the live code or by hand-tracing the plan's tests.

- **Task independence is real.** Every task is testable against P1 and fixtures alone. P4's rows are
  recorded fixtures copied from `P4-evidence-shape/SPEC.md` Records 2 and 3; P9's `group_acceptance`
  row is caller-supplied and P2 re-derives nothing; A10's reference to P6's `no_usable_facts` is
  fixture *data* in a JSON string, asserted against a stage that does not exist and therefore
  `not_run`. The only live neighbour is P1. **No sequencing bug.**
- **The fixtures' `completeness` values are all legal.** `complete`, `capped`, `partial`,
  `unreadable` are four of P4's eight closed values (`P4-evidence-shape/SPEC.md:437-446`); `partial`
  in particular is real (§2.5 "partially inspected"), not invented. Task 15's
  `DEFERRED_COMPLETENESS = {deferred, capped}` and `UNREADABLE_COMPLETENESS = {unreadable, failed}`
  are P5's published mappings verbatim (`P5-extractors/SPEC.md:171-175`).
- **Authorship (M8) is clean.** No `append_event`, no `INSERT INTO events`, no `correction_scope`
  write anywhere in `src/eval_harness/`; Task 16 guards all three and Task 13 re-guards two. The
  fixtures in Task 7 that seed P1's learning store author as `subsystem="P9"` and `author="P13"` —
  the same pattern P1's own tests use with `author="P3"`, and the acting part *is* the author there.
  I confirmed `_reject(...)` satisfies the live `append_event` in every respect: `"user group
  decision"` is one of §8.2's nineteen reserved names, all five of `_REQUIRED` are present and
  non-empty, every keyword is in `_WRITABLE`, and `correction_scope="group"` is accompanied by
  `correction_subject` as the live writer now demands.
- **`learning_records` is called with the live signature.** `learning_records(conn, scope,
  subject_id)` keys on `correction_subject`, not `file_id`, and Task 7 passes `subject_id="group-7"`
  matching the fixture's `correction_subject`. The fixture sets `user_id="u1"`, which the live
  reader's `user_id IS NOT NULL` filter requires. `SCOPES` is imported from P1, not restated.
- **No invented values.** `verdict_for` takes no tolerance argument and a test pins its signature;
  a run snapshots whatever `database_agent.budget.all_ceilings` returns and validates keys against
  P1's `CEILING_KEYS` while validating no value; Task 3 carries a guard that fails if a numeric
  ceiling literal appears in `src/`. Every number in the tests is a fixture value.
- **`analysis_tiers_enabled[]` is handled exactly as I4 requires** — validated as a subset of
  `filesystem | native | ocr | llm`, carried as the seventh `version_tuple` field, and reported in
  the comparison delta with `is_8_5_axis: False` so it is never passed off as one of §8.5's six.
- **`bundle_learning_record[]` carries `polarity`, `proposal_class` and `basis_key`** and nothing
  interprets them; the capture is a snapshot, so a later `reset_preferences` cannot retroactively
  change a sealed bundle — which is the property that stops a store-empty run reading as a grouping
  regression.
- **The two ten-item lists stay apart.** No `STAGE_FOR_DIMENSION`, a test that fails if one appears,
  and the emitting stage names itself. OQ1 is held open by mechanism.
- **`deferred` never becomes `divergent`,** enforced at three independent layers: the writer refuses
  `abstained` + `ceiling_reached`, `verdict_for` returns `deferred` for every expectation kind, and
  `compare_runs` routes any verdict change involving `deferred` to `deferral_changed` before the
  newly-divergent branch can see it.
- **The attribution traversal is correct and terminates.** I hand-traced all six attribution tests:
  the three-stage chain attributes to `extraction`, the cross-subject edge is followed only when
  emitted, the no-edge case stays within the subject, the `inputs[]` cycle is bounded by the
  `(stage_id, subject_ref)` visited set, `min(candidates, key=stage_order)` is unique because
  `stage_order` is injective, and the histogram comes out `{"factual_validation": 2}` as asserted.
- **`EVAL_TABLES` is complete.** All 18 names are created by the six DDL scripts plus the meta table,
  so Task 16's `set(EVAL_TABLES) <= present` holds.
- **No forbidden-term guard false-positives.** I scanned all thirteen `src/eval_harness/` blocks:
  no P7 class or mode name, no adversarial case text (`submit`, `uncertainty`, `python-docx`,
  `Mozilla`, `syllabus`, `lecture`, `instructor`, `semester`), and the only `accuracy`/`aggregate`/
  `overall` occurrences are inside docstrings quoting §8.5, which Task 16's AST-based guard is
  specifically written to allow. `placement_scorer_version` splits to `{placement, scorer, version}`
  and passes.
- **Two mechanics I doubted and checked empirically:** `row` is usable as a SQLite column name
  (Tasks 6–8 rely on it), and a `str` containing `\x00` round-trips through a TEXT column unchanged
  (Task 4's opacity test relies on it). Both work.
- **The adversarial gate cannot silently pass.** With no adapters, eleven cases are `not_run` and
  only A09 passes, from `bundle_extraction_run[]` alone; `run_gate` has no `passed` boolean and
  raises nothing.

### Earlier review (`13-p2-p3-plan-robustness.md`) — status of its P2 findings

| ID | Status |
|---|---|
| **P2-B** (three empties self-referential) | **Answered, and the answer is broken** — the response is B4. The design is right; the wiring is missing. Do not treat P2-B as closed. |
| P2-A (`source_scan_ref` comment calls the fixture "P3's scan_id") | **Still live.** The comment is unchanged in Task 5's test. |
| P2-C (`run_gate` enforces nothing) | Still true, deliberate, OQ9 open. |
| P2-D (`inputs[]` bare subject_refs are ambiguous) | Still true, declared under *Known gaps*. |
| P2-E ("files indexed" has two definitions) | Still true, and handled well — `bundle_counts` returns both and picks neither. |
| P2-F (P2's own §8.6 ceilings unimplemented) | Still true, declared. |
| P2-G (NULL verdict / `unverdicted`) | Still true — see N6. |
| Its edit-order item 1 ("P1 stores the §1.2 fields P3 observed") | **Done.** That P1 change is exactly what created B1 and B3. |
| Its verdict "Execute Tasks 1–17 after rewritten P1 is green" | **Stale.** P1 is green; the plan is not executable until B1–B4 are fixed. |

---

## Edit order

Nothing below is a redesign. 1–4 are the blocking fixes, in the order an executor hits them.

| # | Task | Change | Unblocks |
|---|---|---|---|
| 1 | Task 1 | Add `tests/eval/__init__.py` (empty) to *Files*, *File Structure* and the commit. | B2 — the whole suite, P1's 150 tests, and every later task's validation |
| 2 | Task 1 | Rewrite `test_p2_creates_no_p1_table` as a before/after table-name diff over `create_eval_schema`. | B1 — Task 1 goes green without weakening the guard |
| 3 | Task 13 | Add the `foreign_table_counts` column to `SHADOW_DDL`, snapshot it in `run_shadow` before `replay_bundle`, return it from `shadow_record`, add it to *Produces*, and add a test that a foreign-table write is caught. | B4 — Done-means 9 becomes a real proof; closes P2-B |
| 4 | Task 17 | Add `from conftest import p3_basic_record`. | B3 — Done-means 11, the walking skeleton |
| 5 | Tasks 6, 14 | Strip the `//` lines from all fourteen JSON fixture files; move the provenance notes into the task prose. | N1 — Tasks 6 and 14 load their fixtures |
| 6 | Tasks 4, 10 | Decide `evidence_ref`: thread it through `DimensionValue` → `assert_run`, or state in the prose and *Known gaps* that it is reserved and unpopulated. Remove the "copies whatever `evidence_ref` the dimension value carried" claim either way. | N2 — the §8.2 reconstruction obligation stops being silently unmet |
| 7 | Tasks 6, 7, 8 | Write out the seal triggers for the four content tables that have none, or restate the immutability claim as writer-enforced for them. | N3 |
| 8 | Tasks 3, 5, 9, 12, 14, 16 | The prose fixes: `_DDL_SCRIPTS` → `_ddl_scripts`; one owner for the P7 forbidden-name list; `StageResult` field order; the empty-adapter `abstained` convention; the non-partitioning comparison counts; A11's missing precondition rows. | N4, N5, N7, N8, N9, N10 |
| 9 | P2 SPEC | Publish `stage_error`, `expectation_not_applicable`, `unverdicted` and the `CaseResult` verdicts before P13 renders them under different names. | N6 |
