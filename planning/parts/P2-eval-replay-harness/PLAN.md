# P2 — Evaluation and Replay Harness — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the machinery §8.5 requires before the stages it measures exist — the replay bundle, the stage-output envelope, the run manifest, the per-stage assertion record with its seven verdicts, earliest-divergence attribution, the run-to-run comparison record with no aggregate accuracy anywhere in it, shadow mode, and the twelve-case adversarial suite.

**Architecture:** P2's tables live in P1's single local SQLite database (§0: *"Each part owns its own tables within it"*), created by P2's own `create_eval_schema` — **P1's `db.py` is not modified**. Thirteen modules, one per published surface in [`SPEC.md`](SPEC.md)'s Contract out plus the runner that ties them together. Nine of the ten measured stages do not exist; every one of them is reached through a **stage adapter registry**, and a stage with no adapter yields `outcome = not_implemented`, which is a legal run, not a failure. That registry is why every task below is independently testable with nothing but P1 and fixtures on disk.

**Tech Stack:** Python 3.12 · stdlib `sqlite3`, `json`, `hashlib` · `pytest` · no third-party runtime dependencies · P1's `database_agent` package as the substrate.

---

## Global Constraints

Every task's requirements implicitly include these. Values are copied verbatim from [`SPEC.md`](SPEC.md) and from [`../../01-product-design-structured.md`](../../01-product-design-structured.md).

- **P2 asserts on outcomes. It does not repair them, does not re-rank, and does not feed its verdicts back into any live decision path** (SPEC, *Design slice owned*).
- **No aggregate accuracy scalar exists anywhere in the output** — bundle, run, assertion, comparison, or rendered report (§8.5: *"A single overall 'accuracy' number hides the mechanism that needs repair."*). Done-means 3 makes this a negative acceptance test, enforced in Task 16 over every P2 column and every key of every P2 reader's return value.
- **`deferred` is never `divergent`** (§8.6: *"cost exhaustion must never turn into lower-quality automatic classification"*). Scoring a budget deferral as a quality failure creates exactly the pressure §8.6 forbids.
- **`abstained_correctly` is a passing verdict** (§6.10: *"correct abstention is a successful outcome"*), reported as a pass and never as a miss.
- **P2 appends no `events` row.** SPEC Cross-cutting answers → Provenance: *"P2 appends no file-level provenance event."* P2 writes only its own run-scoped tables. `src/eval_harness/` never imports `append_event`; Task 16 asserts it. Every model call a replay, shadow or adversarial run makes appends a consent-aware audit record **through P7** — P2 requires that record and links to it, and writes none of it.
- **Never DELETE from `events`.** P2 never touches that table at all. The immutability triggers written in Task 5 are on P2's own bundle tables. I6 (tombstone versus append) is deferred to P7 and nothing here forecloses it.
- **P2 defines no other part's vocabulary.** The observation shape (P4), any stage's payload (P5/P6/P8/P9/P10/P11), handling classes and operation modes (P7), the correction record (§8.7), the plan version object (P10), the mutation transaction (P12) are **read and stored opaquely**. Where a neighbour's closed vocabulary is needed for a comparison, P2 stores the string it was handed and compares by value — it does not copy the neighbour's enum into its own source. The one closed vocabulary P2 *does* carry beyond its own is `analysis_tiers_enabled[] ⊆ filesystem | native | ocr | llm`, because SPEC Contract out §5 prints those four inside P2's own `run_manifest` record and [`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md) ratifies them as binding.
- **No thresholds.** §8.5 states no pass threshold, target rate, or regression tolerance for any dimension (SPEC Open question 2, **left open**). Value comparison is exact equality over canonical JSON. There is no tolerance parameter, no score, no rounding, and §6.10's two-condition rule is **not** borrowed as an eval threshold.
- **No ceiling numbers.** §8.6's ceilings are configurable and hand-authored. P2 holds **keys**, never values: a run snapshots whatever `database_agent.budget.all_ceilings` returns. Any number appearing in a test below is a fixture value chosen to make a comparison observable, exactly as P1's `tests/test_budget.py` does, and is not a design value.
- **P2 fills no expectation.** SPEC *Deferred*: the hand-labelled reference corpus, the 200–300 domain template library, gazetteer contents, domain fact-schema fields beyond §3.11's literal table, and residual-library contents beyond §7.3's nine names are hand work. P2 publishes `bundle_expectation`; it does not author its contents. Task 16 asserts `src/eval_harness/` ships none.
- **A bundle is immutable once sealed**, and a rebuild is a **new** bundle with `supersedes_bundle_id` set — supersede, never overwrite (§8.2, §8.8).
- **A stage that does not exist is `not_implemented`, not an error** (`02-segmentation-map.md`, *Order*). A run in which nine stages report `not_implemented` is a valid run with `not_run` verdicts, and the adversarial gate reports `not_run` for such a case — **never `pass`**.
- **Python 3.12.** Pin it; do not assume a newer runtime. P1 already pins it in `pyproject.toml` and **P2 adds no pyproject change**: `[tool.setuptools.packages.find] where = ["src"]` finds `eval_harness` and `testpaths = ["tests"]` collects `tests/eval/`.

---

## Dependency on P1

P2 is built on P1's substrate and on nothing else. The surfaces consumed, all from [`../P1-storage-identity-provenance/PLAN.md`](../P1-storage-identity-provenance/PLAN.md)'s *Produces* lines:

| P1 surface | Used by | For |
|---|---|---|
| `database_agent.db.open_database(path, *, scan_roots=())` | every task | the one local database (§0) |
| `database_agent.db.transaction(conn)` | Tasks 5–8 | bundle build atomicity |
| `database_agent.db.create_schema(conn)` | Tasks 7, 17 | `files` and `events` must exist before P1's learning projection is readable |
| `database_agent.budget.all_ceilings(conn)`, `CEILING_KEYS` | Task 4 | the §8.6 ceiling set a run was given |
| `database_agent.learning.learning_records(conn, scope, subject_id)`, `SCOPES` | Task 7 | the §8.7 rows a bundle must carry |
| `database_agent.files_table.observe_path(...)`, `database_agent.events.append_event(...)` | Task 17 only | the skeleton's P1/P3 step, authored by a P3 fixture |

**P1 must be green before Task 1 starts.** Run `pytest tests/ -q` and confirm P1's suite passes; P2's first import failure otherwise reads as a P2 defect when it is a missing substrate.

**P2 does not modify any P1 file.** Not `db.py`, not `pyproject.toml`, not `tests/conftest.py`. P2's schema function is its own, its fixtures live in `tests/eval/conftest.py`, and its tests live in `tests/eval/` so that P1's `tests/conftest.py` stays untouched.

---

## File Structure

```text
src/eval_harness/__init__.py            package marker; exports the run entry points
src/eval_harness/store.py               every P2 table + create_eval_schema; P1's db.py untouched
src/eval_harness/vocabulary.py          Contract out §1, §2 — ten stages, ten dimensions, kept apart
src/eval_harness/bundle.py              Contract out §3 — the replay bundle, sealed and superseded
src/eval_harness/stage_output.py        Contract out §4 — the envelope every measured part emits
src/eval_harness/run.py                 Contract out §5 — run manifest, version tuple, run settings
src/eval_harness/replay.py              the stage adapter registry and the replay runner
src/eval_harness/assertions.py          Contract out §6 — the per-stage assertion record
src/eval_harness/attribution.py         Contract out §6 — attributed_stage over inputs[]
src/eval_harness/comparison.py          Contract out §7 — the comparison record, never collapsed
src/eval_harness/shadow.py              Contract out §8 — shadow mode and its three empty proofs
src/eval_harness/adversarial.py         Contract out §9 — A1–A12 as a gate, never a silent pass
src/eval_harness/counts.py              §8.6's count line, from the bundle alone

tests/eval/conftest.py                  eval_conn, sealed-bundle helpers
tests/eval/fixtures/p4_runs.json        recorded P4 `extraction_runs` rows (P4 does not exist yet)
tests/eval/fixtures/p4_text_units.json  recorded P4 `text_units` rows
tests/eval/fixtures/adversarial/A1..A12 twelve case files: expected + forbidden + the § that states it
tests/eval/test_store.py                schema, idempotence, P1 tables untouched
tests/eval/test_vocabulary.py           Done-means 2; SPEC OQ1 left open and asserted as open
tests/eval/test_bundle.py               Done-means 1
tests/eval/test_bundle_extraction.py    Done-means 1, 13 input
tests/eval/test_bundle_learning.py      10-i4-learning-ops.md's P2 clause
tests/eval/test_bundle_expectation.py   Done-means 12
tests/eval/test_stage_output.py         Contract out §4
tests/eval/test_run.py                  Contract out §5
tests/eval/test_replay.py               Done-means 7
tests/eval/test_assertions.py           Done-means 2, 5, 6
tests/eval/test_attribution.py          Done-means 4
tests/eval/test_comparison.py           Done-means 6, 8
tests/eval/test_shadow.py               Done-means 9
tests/eval/test_adversarial.py          Done-means 10
tests/eval/test_counts.py               Done-means 13
tests/eval/test_no_aggregate.py         Done-means 3 + the vocabulary and authorship guards
tests/eval/test_skeleton_p2_step.py     Done-means 11
```

Files split by published surface, not by technical layer — each module is one Contract-out section, so a reviewer can reject one without touching its neighbours.

---

### Task 1: Package skeleton and the eval store

**Files:**
- Create: `src/eval_harness/__init__.py`
- Create: `src/eval_harness/store.py`
- Create: `tests/eval/conftest.py`
- Test: `tests/eval/test_store.py`

**Interfaces:**
- Consumes: `database_agent.db.open_database(path, *, scan_roots=()) -> sqlite3.Connection` (P1 Task 1).
- Produces: `EVAL_SCHEMA_VERSION: int`, `create_eval_schema(conn: sqlite3.Connection) -> None`, `EVAL_TABLES: tuple[str, ...]`, `canonical_json(value) -> str`, `content_ref(text: str) -> str`.

**P2 owns tables inside P1's database, and creates them itself.** §0 gives the product one local SQLite database and each part its own tables within it. P2 therefore does **not** add DDL to `database_agent/db.py`: `create_eval_schema` takes the connection P1 hands out and runs P2's own script. Two reasons beyond file ownership. First, P1's `create_schema` is *"Create every P1-owned table"* and a P2 table in it would make P1's Done-means 8 vocabulary guard scan a table P1 does not own. Second, P2 must be droppable — an eval store is not a precondition for a live scan — and a part whose tables are welded into the substrate's schema function cannot be.

**No foreign key from a bundle row into `files`.** A bundle is a frozen capture that §8.5 requires be re-runnable *"without touching a live filesystem"*, and SPEC Open question 5 asks whether a metadata-safe bundle may leave the device at all. Both readings require a bundle to load into a database whose `files` table does not contain those rows. `bundle_file_entry.file_id` and `content_hash` are therefore plain columns carrying P1's identity values, not references into P1's table. P2 does not answer OQ5 by doing this; it stops the schema from deciding OQ5 by accident.

**`content_ref` is a hash, not an identity claim.** It exists so two structurally identical version tuples (Task 4) share a stable reference. Computing one says nothing about whether re-running a bundle under one tuple reproduces its outputs — that is SPEC Open question 11, and it stays open.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_store.py
import sqlite3
from pathlib import Path

from database_agent.db import open_database

from eval_harness.store import (
    EVAL_SCHEMA_VERSION, EVAL_TABLES, canonical_json, content_ref, create_eval_schema,
)


def _table_names(conn: sqlite3.Connection) -> set[str]:
    return {r["name"] for r in
            conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}


def test_eval_tables_names_every_table_p2_will_own(eval_conn):
    # EVAL_TABLES is the manifest of P2's surface. Tasks 3-15 each add the DDL
    # for one or more of these names; this list is what Task 16's column guard
    # walks, so a table missing from it escapes the no-aggregate scan.
    assert len(EVAL_TABLES) == len(set(EVAL_TABLES)) == 18
    assert EVAL_TABLES[0] == "eval_schema_meta"


def test_create_eval_schema_creates_the_tables_wired_so_far(eval_conn):
    # At Task 1 only the meta table is wired. From Task 3 onward each task's own
    # test asserts its table exists; test_no_aggregate.py (Task 16) asserts at the
    # end that every EVAL_TABLES name has been created.
    create_eval_schema(eval_conn)
    assert "eval_schema_meta" in _table_names(eval_conn)


def test_create_eval_schema_is_idempotent(eval_conn):
    create_eval_schema(eval_conn)
    create_eval_schema(eval_conn)
    assert "eval_schema_meta" in _table_names(eval_conn)


def test_p2_creates_no_p1_table(eval_conn):
    # §0: each part owns its own tables. P2 does not create, alter, or shadow
    # `files` or `events`; P1's create_schema is the only thing that makes them.
    create_eval_schema(eval_conn)
    present = _table_names(eval_conn)
    assert "files" not in present
    assert "events" not in present


def test_no_bundle_table_references_the_live_files_table(eval_conn):
    # A bundle must load into a database whose `files` table is empty (§8.5
    # "without touching a live filesystem"; SPEC OQ5 on export). A foreign key
    # into P1's table would decide OQ5 by making that impossible.
    create_eval_schema(eval_conn)
    created = _table_names(eval_conn) & set(EVAL_TABLES)
    for table in created:
        targets = {r["table"] for r in
                   eval_conn.execute(f"PRAGMA foreign_key_list({table})")}
        assert "files" not in targets and "events" not in targets, table


def test_schema_version_is_recorded_separately_from_p1s(eval_conn):
    create_eval_schema(eval_conn)
    row = eval_conn.execute(
        "SELECT value FROM eval_schema_meta WHERE key = 'eval_schema_version'"
    ).fetchone()
    assert int(row["value"]) == EVAL_SCHEMA_VERSION


def test_canonical_json_is_order_independent():
    # Value comparison in Task 10 is exact equality over this form, so the form
    # must not depend on key order. No tolerance, no rounding (SPEC OQ2 open).
    assert canonical_json({"b": 1, "a": [2, 3]}) == canonical_json({"a": [2, 3], "b": 1})
    assert canonical_json({"a": 1}) != canonical_json({"a": 1.0000001})


def test_content_ref_is_stable_and_distinguishing():
    assert content_ref(canonical_json({"a": 1})) == content_ref(canonical_json({"a": 1}))
    assert content_ref(canonical_json({"a": 1})) != content_ref(canonical_json({"a": 2}))
    assert len(content_ref("x")) == 71 and content_ref("x").startswith("sha256:")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/eval/test_store.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_harness'`

- [ ] **Step 3: Write the conftest**

```python
# tests/eval/conftest.py
"""P2 fixtures. Deliberately separate from tests/conftest.py, which is P1's."""
from pathlib import Path

import pytest

from database_agent.db import open_database


@pytest.fixture()
def eval_conn(tmp_path: Path):
    """P1's handle (§0: one local database). P2 owns tables inside it."""
    c = open_database(tmp_path / "agent.sqlite")
    yield c
    c.close()
```

- [ ] **Step 4: Write the store**

```python
# src/eval_harness/store.py
"""P2's tables, created inside P1's single local database (§0).

P1's `create_schema` is not touched: §0 gives each part its own tables, and an
eval store is droppable in a way the substrate is not.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3

EVAL_SCHEMA_VERSION = 1

EVAL_TABLES: tuple[str, ...] = (
    "eval_schema_meta",
    "bundle_manifest",
    "bundle_file_entry",
    "bundle_extraction_output",
    "bundle_extraction_run",
    "bundle_text_unit",
    "bundle_learning_record",
    "bundle_accepted_group",
    "bundle_expectation",
    "version_tuple",
    "run_manifest",
    "stage_output",
    "stage_dimension_value",
    "assertion",
    "comparison",
    "comparison_dimension",
    "shadow_run",
    "review_adjudication",
)

_META_DDL = """
CREATE TABLE IF NOT EXISTS eval_schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def _ddl_scripts() -> list[str]:
    """Every P2 table, each DDL owned by the module that publishes the surface.

    Imported inside the function: `run`, `bundle` and the rest import `store` for
    `canonical_json`, so a module-level import here would be circular. Tasks 3-15
    each append exactly one name to this list.
    """
    return []


def create_eval_schema(conn: sqlite3.Connection) -> None:
    """Create every P2-owned table. Idempotent. Creates no P1 table."""
    conn.executescript(_META_DDL)
    for ddl in _ddl_scripts():
        conn.executescript(ddl)
    conn.execute(
        "INSERT INTO eval_schema_meta (key, value) VALUES ('eval_schema_version', ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (str(EVAL_SCHEMA_VERSION),),
    )


def canonical_json(value) -> str:
    """The one serialization P2 compares by.

    Sorted keys, no whitespace, no float coercion. Exact equality over this form
    is the whole of P2's value comparison: §8.5 states no tolerance and SPEC Open
    question 2 ("what distinguishes a regression from run-to-run noise, and who
    sets it?") is NOT answered here.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_ref(text: str) -> str:
    """A stable reference to a canonical serialization. `sha256:` + 64 hex chars.

    Used for the version tuple (Task 4) so two runs given the same tuple share a
    reference. It is an identity of the *tuple*, not a claim that re-running one
    bundle under it reproduces its outputs — SPEC Open question 11 stays open.
    """
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
```

```python
# src/eval_harness/__init__.py
"""P2 — evaluation and replay harness (§8.5).

P2 asserts on outcomes. It does not repair them, does not re-rank, and does not
feed its verdicts back into any live decision path.
"""
from eval_harness.store import EVAL_SCHEMA_VERSION, create_eval_schema

__all__ = ["create_eval_schema", "EVAL_SCHEMA_VERSION"]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/eval/test_store.py -v`
Expected: PASS — 8 passed

- [ ] **Step 6: Commit**

```bash
git add src/eval_harness/__init__.py src/eval_harness/store.py tests/eval/conftest.py tests/eval/test_store.py
git commit -m "feat(P2): eval store inside P1's database, created by P2, referencing no P1 table"
```

---

### Task 2: The ten stages and the ten dimensions, kept apart (Done-means 2)

**Files:**
- Create: `src/eval_harness/vocabulary.py`
- Test: `tests/eval/test_vocabulary.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `STAGE_IDS: tuple[str, ...]` (ten, in §8.5's order), `DIMENSIONS: tuple[str, ...]` (ten), `PLAN_SCOPED_DIMENSIONS: frozenset[str]`, `SHARED_EVIDENCE_DIMENSIONS: frozenset[str]`, `OUTCOMES: tuple[str, ...]`, `BUDGET_STATES: tuple[str, ...]`, `VERDICTS: tuple[str, ...]`, `RUN_KINDS: tuple[str, ...]`, `CORPUS_FORMS: tuple[str, ...]`, `EXPECTED_OUTCOME_KINDS: tuple[str, ...]`, `EXPECTATION_SOURCES: tuple[str, ...]`, `UnknownStage`, `UnknownDimension`.

**The two lists are not the same list and this module does not merge them.** SPEC Contract out §2: *"§8.5 lists the measured dimensions as a **separate** ten-item list from the attribution stages."* `factual_validation` and `candidate_node_retrieval` are stages with no same-named dimension; `residual` is a dimension with no same-named stage. That asymmetry is **SPEC Open question 1** and this plan does not answer it. Concretely: **there is no `STAGE_FOR_DIMENSION` mapping in P2's source, and no code path derives one.** A dimension value is attributed to a stage because the emitting stage names itself when it emits (Task 9), never because P2 looked the dimension up. If OQ1 later gives §7 residual handling its own attribution stage, or §6.2 its own dimension, this module gains a name and nothing else changes.

**Both tuples are ordered, and the stage order is load-bearing.** §8.5's list order *"is also the pipeline order of §4.10 and §6.12"* (SPEC Contract out §1). Task 11 uses that order as the tie-break when two divergent stages sit at the same depth on an `inputs[]` chain, so the order is a contract, not a formatting choice.

**Why P2 carries these enums when it carries no neighbour's.** Every name here is printed literally inside P2's own Contract out — the ten `stage_id`s, the ten `dimension`s, `outcome`, `budget_state`, `verdict`, `run_kind`, `corpus_form`, `expected_outcome_kind`, `source`. P7's five handling classes, P11's `abstention_reason` members and P6's fact fields are printed in *their* Contract outs and are stored here as opaque strings (Tasks 5, 8).

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_vocabulary.py
import pytest

from eval_harness import vocabulary as V


def test_there_are_exactly_ten_attribution_stages_in_8_5_order():
    assert V.STAGE_IDS == (
        "extraction", "factual_validation", "retrieval", "graph_construction",
        "llm_interpretation", "grouping", "template_generation", "tree_design",
        "candidate_node_retrieval", "placement_scoring",
    )
    assert len(V.STAGE_IDS) == len(set(V.STAGE_IDS)) == 10


def test_there_are_exactly_ten_measured_dimensions():
    assert V.DIMENSIONS == (
        "extraction", "fact", "retrieval", "graph", "llm_grounding",
        "grouping", "template", "tree", "placement", "residual",
    )
    assert len(V.DIMENSIONS) == len(set(V.DIMENSIONS)) == 10


def test_the_two_lists_are_not_the_same_list():
    # SPEC Contract out §2: a SEPARATE ten-item list. Done-means 2: none is
    # collapsed into another.
    assert set(V.STAGE_IDS) != set(V.DIMENSIONS)


def test_the_two_asymmetries_are_recorded_as_found_not_resolved():
    # SPEC Open question 1 is OPEN. These three names are the whole of it, and
    # this test is the standing record: it fails the day someone quietly adds a
    # `residual` stage or a `factual_validation` dimension to close the gap in
    # code instead of in the design.
    assert "factual_validation" in V.STAGE_IDS and "factual_validation" not in V.DIMENSIONS
    assert "candidate_node_retrieval" in V.STAGE_IDS and "candidate_node_retrieval" not in V.DIMENSIONS
    assert "residual" in V.DIMENSIONS and "residual" not in V.STAGE_IDS


def test_no_dimension_to_stage_mapping_exists_anywhere_in_p2():
    # Answering OQ1 in code would look exactly like this mapping appearing.
    # The emitting stage names itself (Task 9); P2 never looks a dimension up.
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness"
    for path in src.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "STAGE_FOR_DIMENSION" not in text, path.name
        assert "DIMENSION_TO_STAGE" not in text, path.name


def test_five_dimensions_are_plan_scoped_and_five_are_not():
    # SPEC Cross-cutting answers → Plan versioning (§8.8): the evidence database
    # remains shared across plan versions, so five dimensions move with the
    # pinned plan version and five do not.
    assert V.PLAN_SCOPED_DIMENSIONS == frozenset(
        {"grouping", "template", "tree", "placement", "residual"})
    assert V.SHARED_EVIDENCE_DIMENSIONS == frozenset(
        {"extraction", "fact", "retrieval", "graph", "llm_grounding"})
    assert V.PLAN_SCOPED_DIMENSIONS | V.SHARED_EVIDENCE_DIMENSIONS == set(V.DIMENSIONS)
    assert not (V.PLAN_SCOPED_DIMENSIONS & V.SHARED_EVIDENCE_DIMENSIONS)


def test_the_five_envelope_outcomes():
    assert V.OUTCOMES == ("produced", "abstained", "deferred", "not_implemented", "error")
    assert V.BUDGET_STATES == ("within_ceiling", "ceiling_reached")


def test_the_seven_verdicts():
    assert V.VERDICTS == (
        "match", "divergent", "abstained_correctly", "abstained_incorrectly",
        "asserted_incorrectly", "deferred", "not_run",
    )


def test_the_remaining_closed_vocabularies():
    assert V.RUN_KINDS == ("replay", "shadow", "adversarial")
    assert V.CORPUS_FORMS == ("snapshot", "metadata_safe")
    assert V.EXPECTED_OUTCOME_KINDS == ("produced", "abstained", "not-applicable")
    assert V.EXPECTATION_SOURCES == ("hand-labelled", "captured-from-accepted-user-decision")


def test_an_unknown_stage_or_dimension_is_rejected():
    with pytest.raises(V.UnknownStage):
        V.check_stage("residual")            # a dimension, not a stage — OQ1
    with pytest.raises(V.UnknownDimension):
        V.check_dimension("factual_validation")   # a stage, not a dimension — OQ1
    V.check_stage("placement_scoring")
    V.check_dimension("placement")


def test_stage_order_is_the_pipeline_order_used_for_attribution():
    assert V.stage_order("extraction") == 0
    assert V.stage_order("placement_scoring") == 9
    assert V.stage_order("grouping") < V.stage_order("tree_design")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/eval/test_vocabulary.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_harness.vocabulary'`

- [ ] **Step 3: Write the implementation**

```python
# src/eval_harness/vocabulary.py
"""Contract out §1 and §2 — the ten attribution stages and the ten measured
dimensions, which are two different ten-item lists (§8.5).

They are NOT merged here and no mapping between them is derived. `factual_validation`
and `candidate_node_retrieval` are stages with no same-named dimension; `residual` is
a dimension with no same-named stage. That is SPEC Open question 1, and it is open:
whether §7 residual handling gets its own attribution stage, and whether §6.2
candidate-node retrieval gets its own dimension, is for the design to settle. A
dimension value reaches a stage because the emitting stage names itself, never
because this module looked it up.
"""
from __future__ import annotations

#: §8.5's attribution stages, in §8.5's order — which is also the pipeline order of
#: §4.10 and §6.12. The order is used as the tie-break in earliest-divergence
#: attribution (Task 11), so it is a contract, not formatting.
STAGE_IDS: tuple[str, ...] = (
    "extraction",               # P5 (§2), shape from P4 (§2.8)
    "factual_validation",       # P6 (§3.5, §3.6)
    "retrieval",                # P9 (§4.2)
    "graph_construction",       # P9 (§4.3)
    "llm_interpretation",       # P8 (§3.3, §4.5)
    "grouping",                 # P9 (§4)
    "template_generation",      # P10 (§5.4, §5.7)
    "tree_design",              # P10 (§5)
    "candidate_node_retrieval", # P11 (§6.2)
    "placement_scoring",        # P11 (§6.10)
)

#: §8.5's measured dimensions. A separate list from the one above.
DIMENSIONS: tuple[str, ...] = (
    "extraction",     # "Did the expected text, metadata, table values, OCR text, or image facts appear?"
    "fact",           # "Did the system create the correct direct and validated facts? Did it abstain...?"
    "retrieval",      # "For sparse files, did the correct anchors appear in the top candidate neighborhood?"
    "graph",          # "Did edges reflect meaningful typed relationships? Did generic hubs create false...?"
    "llm_grounding",  # "Did every cited excerpt exist? Did the model return unknown...?"
    "grouping",       # "Did candidate groups include correct members, exclude outliers...?"
    "template",       # "Did a template generate useful real branches without needless depth?"
    "tree",           # "Did users accept, rename, merge, split, or reject proposed branches?"
    "placement",      # "Did the engine choose the correct frozen node, an appropriate shallow fallback, or abstain?"
    "residual",       # "Did the system avoid inventing associations for isolated files?"
)

#: §8.8: the destination tree and user policy define which projections are valid in
#: each version, while "the evidence database remains shared across plan versions."
PLAN_SCOPED_DIMENSIONS = frozenset({"grouping", "template", "tree", "placement", "residual"})
SHARED_EVIDENCE_DIMENSIONS = frozenset({"extraction", "fact", "retrieval", "graph", "llm_grounding"})

#: Contract out §4. `not_implemented` is what makes the harness runnable before the
#: stages exist (02-segmentation-map.md, Order).
OUTCOMES: tuple[str, ...] = ("produced", "abstained", "deferred", "not_implemented", "error")
BUDGET_STATES: tuple[str, ...] = ("within_ceiling", "ceiling_reached")

#: Contract out §6. Seven, exactly. `abstained_correctly` is a PASS (§6.10);
#: `deferred` is a budget event and never a divergence (§8.6).
VERDICTS: tuple[str, ...] = (
    "match", "divergent", "abstained_correctly", "abstained_incorrectly",
    "asserted_incorrectly", "deferred", "not_run",
)

RUN_KINDS: tuple[str, ...] = ("replay", "shadow", "adversarial")            # §8.5
CORPUS_FORMS: tuple[str, ...] = ("snapshot", "metadata_safe")               # §8.5
EXPECTED_OUTCOME_KINDS: tuple[str, ...] = ("produced", "abstained", "not-applicable")
EXPECTATION_SOURCES: tuple[str, ...] = (
    "hand-labelled", "captured-from-accepted-user-decision",
)

_STAGE_ORDER = {name: i for i, name in enumerate(STAGE_IDS)}


class UnknownStage(Exception):
    """A stage_id outside §8.5's closed ten."""


class UnknownDimension(Exception):
    """A dimension outside §8.5's closed ten."""


def check_stage(stage_id: str) -> str:
    if stage_id not in _STAGE_ORDER:
        raise UnknownStage(f"{stage_id!r} is not one of §8.5's ten attribution stages")
    return stage_id


def check_dimension(dimension: str) -> str:
    if dimension not in DIMENSIONS:
        raise UnknownDimension(f"{dimension!r} is not one of §8.5's ten measured dimensions")
    return dimension


def stage_order(stage_id: str) -> int:
    """Position in §8.5's list, which is §4.10's and §6.12's pipeline order."""
    return _STAGE_ORDER[check_stage(stage_id)]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/eval/test_vocabulary.py -v`
Expected: PASS — 11 passed

- [ ] **Step 5: Commit**

```bash
git add src/eval_harness/vocabulary.py tests/eval/test_vocabulary.py
git commit -m "feat(P2): the ten stages and the ten dimensions, two lists, never merged"
```

---

### Task 3: Run manifest, version tuple, and run settings (Contract out §5)

**Files:**
- Create: `src/eval_harness/run.py`
- Modify: `src/eval_harness/store.py` — append `RUN_DDL` to `_DDL_SCRIPTS`
- Test: `tests/eval/test_run.py`

**Interfaces:**
- Consumes: `create_eval_schema`, `canonical_json`, `content_ref` (Task 1); `RUN_KINDS` (Task 2); `database_agent.budget.all_ceilings(conn) -> dict[str, int]`, `database_agent.budget.CEILING_KEYS` (P1 Task 10).
- Produces: `VERSION_AXES: tuple[str, ...]` (the six §8.5 axes), `VERSION_TUPLE_FIELDS: tuple[str, ...]` (seven), `ANALYSIS_TIERS: tuple[str, ...]` (four), `RUN_SETTING_KEYS: tuple[str, ...]` (two), `record_version_tuple(conn, **fields) -> str`, `get_version_tuple(conn, ref) -> dict`, `start_run(conn, *, bundle_id, run_kind, version_tuple_ref, budget_ceilings, run_settings, pinned_plan_id, pinned_plan_version) -> str`, `finish_run(conn, run_id) -> None`, `get_run(conn, run_id) -> sqlite3.Row`, `run_ceilings(conn, run_id) -> dict`, `UnknownAnalysisTier`, `UnknownRunSetting`.

**The version tuple has seven fields and §8.5 names six axes.** §8.5's six are *"a new extractor version, graph algorithm, LLM prompt, model, template library, or placement scorer."* The seventh, `analysis_tiers_enabled[]`, arrives from [`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md), which is binding: *"P2 `version_tuple.analysis_tier` becomes `analysis_tiers_enabled[]` — a subset of the four — so a walking-skeleton run can declare `{filesystem, native}` and an OCR-on replay is a different tuple. A singular field cannot express 'native on, OCR off.'"* `VERSION_AXES` is the six; `VERSION_TUPLE_FIELDS` is all seven. Task 12's delta reports every field that differs and labels which of them are §8.5's six, so Done-means 8 is satisfied without hiding a tier change. This plan does not decide whether the tier set *should* be a seventh §8.5 axis — see the report accompanying this plan.

**`run_settings` is two keys and is not a version axis.** SPEC Contract out §5: a disable changes *which stages ran*, not *which version produced them*. Exactly two are required — `model_enabled` and `embeddings_enabled` — because §8.5 asks retrieval quality and LLM grounding as separate questions, and because `embeddings_enabled = false` is the run that makes P9's §4.2 obligation checkable (*"embeddings never establish the group by themselves"*). The walking skeleton runs with both false.

**P2 holds ceiling keys, never ceiling values.** §8.6's ceilings are *"configurable"* and hand-authored. `start_run` snapshots whatever `database_agent.budget.all_ceilings(conn)` returns at the moment the run starts and stores it verbatim on the run, so two runs given different ceilings are distinguishable (SPEC Contract out §5: *"a comparison across different ceilings must be labelled, because deferral changes outputs"*). It validates keys against P1's `CEILING_KEYS` and validates no value. **Every number in the test below is a fixture value chosen to make a difference observable, exactly as P1's `tests/test_budget.py` does. None is a design value.**

**A run is not a session.** [`../../11-ops-runtime.md`](../../11-ops-runtime.md) §3: *"P2 replay is not a session; it is a harness run."* There is no `session_id` on `run_manifest`.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_run.py
import pytest
from database_agent.budget import CEILING_KEYS, all_ceilings, set_ceiling
from database_agent.db import create_schema

from eval_harness.run import (
    ANALYSIS_TIERS, RUN_SETTING_KEYS, VERSION_AXES, VERSION_TUPLE_FIELDS,
    UnknownAnalysisTier, UnknownRunSetting, finish_run, get_run, get_version_tuple,
    record_version_tuple, run_ceilings, start_run,
)
from eval_harness.store import create_eval_schema


def _tuple_fields(**overrides):
    fields = dict(
        extractor_versions={"e1": "0.0.0-fixture"},
        graph_algorithm_version="graph-fixture",
        prompt_fingerprint=None,
        model_identifier=None,
        template_library_version="templates-fixture",
        placement_scorer_version="scorer-fixture",
        analysis_tiers_enabled=["filesystem", "native"],
    )
    fields.update(overrides)
    return fields


def test_the_six_8_5_axes_and_the_seventh_i4_field():
    # §8.5: "a new extractor version, graph algorithm, LLM prompt, model,
    # template library, or placement scorer". Six.
    assert VERSION_AXES == (
        "extractor_versions", "graph_algorithm_version", "prompt_fingerprint",
        "model_identifier", "template_library_version", "placement_scorer_version",
    )
    # 10-i4-learning-ops.md adds the tier set. Seven fields, six named axes.
    assert VERSION_TUPLE_FIELDS == VERSION_AXES + ("analysis_tiers_enabled",)


def test_analysis_tiers_enabled_is_a_subset_of_the_four(eval_conn):
    create_eval_schema(eval_conn)
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")
    ref = record_version_tuple(eval_conn, **_tuple_fields())
    assert get_version_tuple(eval_conn, ref)["analysis_tiers_enabled"] == \
        ["filesystem", "native"]


def test_a_tier_outside_the_four_is_rejected(eval_conn):
    create_eval_schema(eval_conn)
    with pytest.raises(UnknownAnalysisTier):
        record_version_tuple(eval_conn,
                             **_tuple_fields(analysis_tiers_enabled=["deep"]))


def test_the_same_tuple_yields_the_same_reference(eval_conn):
    create_eval_schema(eval_conn)
    a = record_version_tuple(eval_conn, **_tuple_fields())
    b = record_version_tuple(eval_conn, **_tuple_fields())
    c = record_version_tuple(eval_conn, **_tuple_fields(model_identifier="m2"))
    assert a == b
    assert a != c


def test_run_settings_are_exactly_two_and_are_not_version_axes(eval_conn):
    create_eval_schema(eval_conn)
    assert RUN_SETTING_KEYS == ("model_enabled", "embeddings_enabled")
    assert not set(RUN_SETTING_KEYS) & set(VERSION_TUPLE_FIELDS)
    ref = record_version_tuple(eval_conn, **_tuple_fields())
    with pytest.raises(UnknownRunSetting):
        start_run(eval_conn, bundle_id="b1", run_kind="replay", version_tuple_ref=ref,
                  budget_ceilings={}, run_settings={"ocr_enabled": True},
                  pinned_plan_id="plan-fixture", pinned_plan_version="1")


def test_a_run_snapshots_the_ceiling_set_it_was_given(eval_conn):
    # SPEC Contract out §5: "Two runs are only comparable when they were given the
    # same budget_ceilings". The numbers below are fixture values, not design values.
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    set_ceiling(eval_conn, "ocr.max_pages_per_file", 40)
    set_ceiling(eval_conn, "model.max_cost_per_scan", 7)
    ref = record_version_tuple(eval_conn, **_tuple_fields())
    run_id = start_run(
        eval_conn, bundle_id="b1", run_kind="replay", version_tuple_ref=ref,
        budget_ceilings=all_ceilings(eval_conn),
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1",
    )
    assert run_ceilings(eval_conn, run_id) == {"ocr.max_pages_per_file": 40,
                                               "model.max_cost_per_scan": 7}
    # A later change to the live config does not rewrite a completed run.
    set_ceiling(eval_conn, "ocr.max_pages_per_file", 5)
    assert run_ceilings(eval_conn, run_id)["ocr.max_pages_per_file"] == 40


def test_a_ceiling_key_outside_p1s_fifteen_is_rejected(eval_conn):
    create_eval_schema(eval_conn)
    ref = record_version_tuple(eval_conn, **_tuple_fields())
    with pytest.raises(KeyError):
        start_run(eval_conn, bundle_id="b1", run_kind="replay", version_tuple_ref=ref,
                  budget_ceilings={"made.up_ceiling": 5},
                  run_settings={"model_enabled": False, "embeddings_enabled": False},
                  pinned_plan_id="plan-fixture", pinned_plan_version="1")


def test_p2_stores_no_ceiling_value_of_its_own():
    # §8.6's ceilings are configurable and hand-authored. P2 holds keys.
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness"
    for path in src.rglob("*.py"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if "max_" in line and "=" in line and "CEILING" not in line:
                assert not any(ch.isdigit() for ch in line.split("=", 1)[1]), \
                    f"{path.name}: {line.strip()}"


def test_run_kind_is_one_of_three(eval_conn):
    create_eval_schema(eval_conn)
    ref = record_version_tuple(eval_conn, **_tuple_fields())
    with pytest.raises(ValueError):
        start_run(eval_conn, bundle_id="b1", run_kind="production",
                  version_tuple_ref=ref, budget_ceilings={},
                  run_settings={"model_enabled": False, "embeddings_enabled": False},
                  pinned_plan_id="plan-fixture", pinned_plan_version="1")


def test_a_run_records_its_pinned_plan_version_and_finishes(eval_conn):
    create_eval_schema(eval_conn)
    ref = record_version_tuple(eval_conn, **_tuple_fields())
    run_id = start_run(
        eval_conn, bundle_id="b1", run_kind="replay", version_tuple_ref=ref,
        budget_ceilings={},
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan-fixture", pinned_plan_version="1",
    )
    row = get_run(eval_conn, run_id)
    assert row["pinned_plan_id"] == "plan-fixture"
    assert row["pinned_plan_version"] == "1"
    assert row["started_at"] and row["finished_at"] is None
    finish_run(eval_conn, run_id)
    assert get_run(eval_conn, run_id)["finished_at"]


def test_a_run_carries_no_session_id(eval_conn):
    # 11-ops-runtime.md §3: "P2 replay is not a session; it is a harness run."
    create_eval_schema(eval_conn)
    cols = {r["name"] for r in eval_conn.execute("PRAGMA table_info(run_manifest)")}
    assert "session_id" not in cols
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/eval/test_run.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_harness.run'`

- [ ] **Step 3: Write the implementation**

```python
# src/eval_harness/run.py
"""Contract out §5 — the run manifest.

The six version axes are exactly the six things §8.5 says a bundle may be
re-processed by. `analysis_tiers_enabled[]` is a seventh field, added by
10-i4-learning-ops.md so that "native on, OCR off" is expressible; it is recorded
and compared, and this module does not claim it is a §8.5 axis.

`run_settings` is separate from the tuple because a disable changes WHICH stages
ran, not which version produced them.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

from database_agent.budget import CEILING_KEYS

from eval_harness.store import canonical_json, content_ref
from eval_harness.vocabulary import RUN_KINDS

#: §8.5: "a new extractor version, graph algorithm, LLM prompt, model, template
#: library, or placement scorer". Six, and Task 12 names which of them differ.
VERSION_AXES: tuple[str, ...] = (
    "extractor_versions",         # {} — one version per extractor (§3.4)
    "graph_algorithm_version",
    "prompt_fingerprint",         # §3.4
    "model_identifier",           # §3.4
    "template_library_version",
    "placement_scorer_version",
)

#: The seventh field. 10-i4-learning-ops.md, binding: a subset of the four tiers.
VERSION_TUPLE_FIELDS: tuple[str, ...] = VERSION_AXES + ("analysis_tiers_enabled",)

#: The four analysis tiers (I4, ratified). P5 owns the vocabulary; P2's Contract
#: out §5 prints all four inside its own record, which is why they appear here.
ANALYSIS_TIERS: tuple[str, ...] = ("filesystem", "native", "ocr", "llm")

#: Contract out §5 — "Two are required." Independent stage disables, not versions.
RUN_SETTING_KEYS: tuple[str, ...] = ("model_enabled", "embeddings_enabled")

RUN_DDL = """
CREATE TABLE IF NOT EXISTS version_tuple (
    version_tuple_ref TEXT PRIMARY KEY,
    fields            TEXT NOT NULL          -- canonical JSON of the seven fields
);
CREATE TABLE IF NOT EXISTS run_manifest (
    run_id              TEXT PRIMARY KEY,
    bundle_id           TEXT NOT NULL,
    run_kind            TEXT NOT NULL,
    version_tuple_ref   TEXT NOT NULL REFERENCES version_tuple (version_tuple_ref),
    budget_ceilings     TEXT NOT NULL,       -- canonical JSON; the set this run was GIVEN
    run_settings        TEXT NOT NULL,       -- canonical JSON; exactly RUN_SETTING_KEYS
    pinned_plan_id      TEXT,
    pinned_plan_version TEXT,
    started_at          TEXT NOT NULL,
    finished_at         TEXT
);
CREATE INDEX IF NOT EXISTS run_manifest_bundle ON run_manifest (bundle_id);
"""


class UnknownAnalysisTier(Exception):
    """A tier outside I4's ratified four."""


class UnknownRunSetting(Exception):
    """A run setting outside Contract out §5's two."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_version_tuple(conn: sqlite3.Connection, **fields) -> str:
    """Store the seven-field tuple and return its stable reference.

    Two runs given structurally identical tuples share a reference. That is an
    identity of the tuple and NOT a claim that a re-run under it reproduces its
    outputs — §3.4's cache key pins model identifier and prompt fingerprint and
    says nothing about sampling parameters. SPEC Open question 11 is open.
    """
    missing = set(VERSION_TUPLE_FIELDS) - set(fields)
    extra = set(fields) - set(VERSION_TUPLE_FIELDS)
    if missing or extra:
        raise ValueError(f"version tuple fields: missing {sorted(missing)}, "
                         f"unexpected {sorted(extra)}")
    tiers = fields["analysis_tiers_enabled"]
    unknown = [t for t in tiers if t not in ANALYSIS_TIERS]
    if unknown:
        raise UnknownAnalysisTier(
            f"{unknown} outside the four analysis tiers {ANALYSIS_TIERS} (I4)")
    payload = canonical_json({k: fields[k] for k in VERSION_TUPLE_FIELDS})
    ref = content_ref(payload)
    conn.execute(
        "INSERT INTO version_tuple (version_tuple_ref, fields) VALUES (?, ?) "
        "ON CONFLICT(version_tuple_ref) DO NOTHING",
        (ref, payload),
    )
    return ref


def get_version_tuple(conn: sqlite3.Connection, version_tuple_ref: str) -> dict:
    import json
    row = conn.execute(
        "SELECT fields FROM version_tuple WHERE version_tuple_ref = ?",
        (version_tuple_ref,),
    ).fetchone()
    return {} if row is None else json.loads(row["fields"])


def start_run(conn: sqlite3.Connection, *, bundle_id: str, run_kind: str,
              version_tuple_ref: str, budget_ceilings: dict,
              run_settings: dict, pinned_plan_id: str | None,
              pinned_plan_version: str | None) -> str:
    """Open a run. Returns its run_id.

    `budget_ceilings` is the set this run was GIVEN — snapshot it from
    `database_agent.budget.all_ceilings(conn)` at the call site. P2 validates the
    keys against P1's fifteen and validates no value: §8.6's ceilings are
    configurable and hand-authored, and P2 holds keys, never numbers.
    """
    if run_kind not in RUN_KINDS:
        raise ValueError(f"run_kind {run_kind!r} is not one of {RUN_KINDS}")
    for key in budget_ceilings:
        if key not in CEILING_KEYS:
            raise KeyError(f"{key!r} is not one of §8.6's fifteen ceiling keys")
    unknown = set(run_settings) - set(RUN_SETTING_KEYS)
    if unknown:
        raise UnknownRunSetting(
            f"{sorted(unknown)} outside Contract out §5's {RUN_SETTING_KEYS}")
    run_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO run_manifest (run_id, bundle_id, run_kind, version_tuple_ref, "
        "budget_ceilings, run_settings, pinned_plan_id, pinned_plan_version, started_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (run_id, bundle_id, run_kind, version_tuple_ref,
         canonical_json(budget_ceilings), canonical_json(run_settings),
         pinned_plan_id, pinned_plan_version, _now()),
    )
    return run_id


def finish_run(conn: sqlite3.Connection, run_id: str) -> None:
    conn.execute("UPDATE run_manifest SET finished_at = ? WHERE run_id = ?",
                 (_now(), run_id))


def get_run(conn: sqlite3.Connection, run_id: str) -> sqlite3.Row:
    return conn.execute("SELECT * FROM run_manifest WHERE run_id = ?",
                        (run_id,)).fetchone()


def run_ceilings(conn: sqlite3.Connection, run_id: str) -> dict:
    """The ceiling set this run was given, as recorded. Never re-read from config."""
    import json
    row = get_run(conn, run_id)
    return {} if row is None else json.loads(row["budget_ceilings"])


def run_settings(conn: sqlite3.Connection, run_id: str) -> dict:
    import json
    row = get_run(conn, run_id)
    return {} if row is None else json.loads(row["run_settings"])
```

**Wire the DDL into `create_eval_schema` without a circular import.** `run.py` imports `store.py` for `canonical_json`, so `store.py` cannot import `run.py` at module level. Each module owns its own DDL string and `create_eval_schema` collects them in a function-level import — one owner per table, no duplication, no cycle. Replace the `_DDL_SCRIPTS` placeholder in `store.py` with:

```python
def _ddl_scripts() -> list[str]:
    """Every P2 table, each DDL owned by the module that publishes the surface.

    Imported inside the function: `run`, `bundle` and the rest import `store` for
    `canonical_json`, so a module-level import here would be circular.
    """
    from eval_harness import run
    return [run.RUN_DDL]
```

and change `create_eval_schema`'s loop to `for ddl in _ddl_scripts():`. Each later task appends exactly one name to that list.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/eval/test_run.py -v`
Expected: PASS — 11 passed

- [ ] **Step 5: Commit**

```bash
git add src/eval_harness/run.py src/eval_harness/store.py tests/eval/test_run.py
git commit -m "feat(P2): run manifest, seven-field version tuple, two run settings, ceilings snapshotted"
```

---
