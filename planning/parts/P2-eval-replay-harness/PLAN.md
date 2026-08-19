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
tests/eval/fixtures/adversarial/A01.json … A12.json   expected + forbidden + the § that states it
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
- Produces: `VERSION_AXES: tuple[str, ...]` (the six §8.5 axes), `VERSION_TUPLE_FIELDS: tuple[str, ...]` (seven), `ANALYSIS_TIERS: tuple[str, ...]` (four), `RUN_SETTING_KEYS: tuple[str, ...]` (two), `record_version_tuple(conn, **fields) -> str`, `get_version_tuple(conn, ref) -> dict`, `start_run(conn, *, bundle_id, run_kind, version_tuple_ref, budget_ceilings, run_settings, pinned_plan_id, pinned_plan_version) -> str`, `finish_run(conn, run_id) -> None`, `get_run(conn, run_id) -> sqlite3.Row`, `run_ceilings(conn, run_id) -> dict`, `run_settings(conn, run_id) -> dict`, `UnknownAnalysisTier`, `UnknownRunSetting`.

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

### Task 4: The stage output envelope (Contract out §4)

**Files:**
- Create: `src/eval_harness/stage_output.py`
- Modify: `src/eval_harness/store.py` — add `stage_output.STAGE_DDL` to `_ddl_scripts`
- Test: `tests/eval/test_stage_output.py`

**Interfaces:**
- Consumes: `canonical_json` (Task 1); `STAGE_IDS`, `DIMENSIONS`, `OUTCOMES`, `BUDGET_STATES`, `check_stage`, `check_dimension` (Task 2); `run_manifest` (Task 3).
- Produces: `ENVELOPE_FIELDS: tuple[str, ...]` (nine), `DimensionValue` (frozen dataclass: `dimension`, `subject_ref`, `outcome`, `value`), `record_stage_output(conn, *, run_id, stage_id, subject_ref, outcome, payload, version_tuple_ref, inputs, budget_state, dimension_values=()) -> int`, `stage_outputs(conn, run_id, *, stage_id=None) -> list[sqlite3.Row]`, `dimension_values(conn, run_id, *, dimension=None) -> list[sqlite3.Row]`, `stage_payload(conn, stage_output_id) -> str`, `ForeignVocabulary`.

**P2 owns the envelope; the producing part owns `payload`.** `payload` is stored **verbatim as text and never parsed**. The test below stores a payload that is not valid JSON and asserts it comes back byte-identical, because that is the only way to prove opacity: a store that round-trips only well-formed JSON has silently acquired an opinion about another part's shape.

**The envelope's vocabulary is P2's; the record's vocabulary is the producing part's, and they are different vocabularies.** [`../P11-placement-residual/SPEC.md`](../P11-placement-residual/SPEC.md) states it and publishes the mapping table: *"`place`, `abstain`, `deferred_stage` and `abstention_reason = budget_deferred` are values of `placement_decision`, this part's own record — none of them is an envelope value, and none may be written into `stage_output`."* `record_stage_output` rejects them by name, so a part that writes its own vocabulary into the envelope fails at the writer rather than producing a run whose outcomes cannot be compared with any other stage's.

**A budget deferral is `deferred`, never `abstained`.** P11's mapping table again: scored as `abstained`, P2 would grade a ceiling-truncated run `abstained_correctly` or `abstained_incorrectly` — a judgement about evidence — when no judgement was made. The writer enforces the pairing: `outcome = deferred` requires `budget_state = ceiling_reached`, and `budget_state = ceiling_reached` with `outcome = abstained` is refused.

**`dimension_values` is how a measured value reaches P2 without P2 opening the payload.** SPEC Contract out §6 says `observed` comes *"from stage_output"*, and Contract out §4 says the payload is opaque. Both hold only if the producing part hands P2 the value it wants asserted, alongside the payload it keeps to itself. One stage output may carry several — a `fact` stage decides several fields for one file, abstaining on some — so each `DimensionValue` carries its own `outcome`. **The emitting stage names itself**; P2 never looks up which stage owns a dimension (Task 2, SPEC Open question 1).

**`inputs[]` are subject_refs, as the SPEC publishes them.** Contract out §4: *"`inputs[]` subject_refs of the stage outputs consumed."* Task 11 resolves each one to every stage output in the same run carrying that `subject_ref`. Where two stages decided about the same subject, that resolves to both, and the traversal considers both. This ambiguity is in the published shape, not introduced here; a recommended SPEC change is recorded in the report accompanying this plan, and **is not made**.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_stage_output.py
import pytest

from eval_harness.run import record_version_tuple, start_run
from eval_harness.stage_output import (
    ENVELOPE_FIELDS, DimensionValue, ForeignVocabulary, dimension_values,
    record_stage_output, stage_outputs, stage_payload,
)
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import UnknownStage


@pytest.fixture()
def run(eval_conn):
    create_eval_schema(eval_conn)
    ref = record_version_tuple(
        eval_conn, extractor_versions={}, graph_algorithm_version=None,
        prompt_fingerprint=None, model_identifier=None,
        template_library_version=None, placement_scorer_version=None,
        analysis_tiers_enabled=["filesystem"],
    )
    return start_run(eval_conn, bundle_id="b1", run_kind="replay",
                     version_tuple_ref=ref, budget_ceilings={},
                     run_settings={"model_enabled": False, "embeddings_enabled": False},
                     pinned_plan_id="plan-fixture", pinned_plan_version="1"), ref


def _emit(conn, run_id, ref, **overrides):
    fields = dict(run_id=run_id, stage_id="extraction", subject_ref="sha256:aa",
                  outcome="produced", payload='{"opaque": true}',
                  version_tuple_ref=ref, inputs=[], budget_state="within_ceiling")
    fields.update(overrides)
    return record_stage_output(conn, **fields)


def test_the_envelope_has_exactly_the_nine_contract_fields():
    assert ENVELOPE_FIELDS == (
        "run_id", "stage_id", "subject_ref", "outcome", "payload",
        "version_tuple_ref", "inputs", "budget_state", "produced_at",
    )


def test_every_envelope_field_is_stored(eval_conn, run):
    run_id, ref = run
    _emit(eval_conn, run_id, ref, inputs=["sha256:bb"])
    row = stage_outputs(eval_conn, run_id)[0]
    assert row["stage_id"] == "extraction"
    assert row["subject_ref"] == "sha256:aa"
    assert row["outcome"] == "produced"
    assert row["version_tuple_ref"] == ref
    assert row["inputs"] == '["sha256:bb"]'
    assert row["budget_state"] == "within_ceiling"
    assert row["produced_at"]


def test_payload_is_opaque_and_is_never_parsed(eval_conn, run):
    # Contract out §4: "payload  opaque to P2; shape owned by the producing part."
    # Not valid JSON on purpose: a store that round-trips only well-formed JSON
    # has acquired an opinion about another part's shape.
    run_id, ref = run
    blob = "this is not JSON \x00 and it has a NUL and a }brace"
    output_id = _emit(eval_conn, run_id, ref, payload=blob)
    assert stage_payload(eval_conn, output_id) == blob


def test_a_stage_id_outside_the_ten_is_rejected(eval_conn, run):
    run_id, ref = run
    with pytest.raises(UnknownStage):
        _emit(eval_conn, run_id, ref, stage_id="residual")


def test_a_producing_parts_own_vocabulary_is_refused_in_the_envelope(eval_conn, run):
    # P11 SPEC: "none of them is an envelope value, and none may be written into
    # stage_output." Refused at the writer, not discovered during comparison.
    run_id, ref = run
    for foreign in ("place", "abstain", "return_to_placement", "mark_review_later",
                    "leave_in_place", "mark_state", "ask_user"):
        with pytest.raises(ForeignVocabulary):
            _emit(eval_conn, run_id, ref, outcome=foreign)


def test_an_outcome_outside_the_five_is_rejected(eval_conn, run):
    run_id, ref = run
    with pytest.raises(ValueError):
        _emit(eval_conn, run_id, ref, outcome="succeeded")


def test_deferred_and_ceiling_reached_are_bound_together(eval_conn, run):
    # §8.6: a budget deferral must not be scorable as an evidence judgement.
    run_id, ref = run
    _emit(eval_conn, run_id, ref, outcome="deferred", budget_state="ceiling_reached")
    with pytest.raises(ValueError):
        _emit(eval_conn, run_id, ref, outcome="deferred", budget_state="within_ceiling")
    with pytest.raises(ValueError):
        _emit(eval_conn, run_id, ref, outcome="abstained", budget_state="ceiling_reached")


def test_not_implemented_is_a_legal_output(eval_conn, run):
    # 02-segmentation-map.md, Order: the harness runs before the stages exist.
    run_id, ref = run
    _emit(eval_conn, run_id, ref, stage_id="placement_scoring",
          outcome="not_implemented", payload="")
    row = stage_outputs(eval_conn, run_id, stage_id="placement_scoring")[0]
    assert row["outcome"] == "not_implemented"


def test_a_stage_output_may_carry_several_dimension_values(eval_conn, run):
    # One `fact` stage output about one file, three fields, one abstention.
    run_id, ref = run
    _emit(eval_conn, run_id, ref, stage_id="factual_validation",
          subject_ref="file-1",
          dimension_values=[
              DimensionValue("fact", "file-1::field-a", "produced", {"value": "A"}),
              DimensionValue("fact", "file-1::field-b", "produced", {"value": "B"}),
              DimensionValue("fact", "file-1::field-c", "abstained", None),
          ])
    rows = dimension_values(eval_conn, run_id, dimension="fact")
    assert len(rows) == 3
    assert {r["outcome"] for r in rows} == {"produced", "abstained"}
    assert [r["stage_id"] for r in rows] == ["factual_validation"] * 3


def test_the_emitting_stage_names_itself_for_any_dimension(eval_conn, run):
    # SPEC Open question 1 is open: `residual` has no same-named attribution stage,
    # so whichever stage emits it says so. P2 holds no dimension->stage table.
    run_id, ref = run
    _emit(eval_conn, run_id, ref, stage_id="placement_scoring", subject_ref="file-9",
          dimension_values=[DimensionValue("residual", "file-9", "produced",
                                           {"outcome": "leave_in_place"})])
    row = dimension_values(eval_conn, run_id, dimension="residual")[0]
    assert row["stage_id"] == "placement_scoring"


def test_a_dimension_outside_the_ten_is_rejected(eval_conn, run):
    from eval_harness.vocabulary import UnknownDimension
    run_id, ref = run
    with pytest.raises(UnknownDimension):
        _emit(eval_conn, run_id, ref,
              dimension_values=[DimensionValue("factual_validation", "x",
                                               "produced", None)])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/eval/test_stage_output.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_harness.stage_output'`

- [ ] **Step 3: Write the implementation**

```python
# src/eval_harness/stage_output.py
"""Contract out §4 — the one record every measured part emits.

P2 owns the envelope; the producing part owns `payload`, which is stored verbatim
and never parsed. The envelope's vocabulary and the producing part's record
vocabulary are different vocabularies, and a part's own values are refused here.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Sequence

from eval_harness.store import canonical_json
from eval_harness.vocabulary import (
    BUDGET_STATES, OUTCOMES, check_dimension, check_stage,
)

#: Contract out §4, in order. Nine.
ENVELOPE_FIELDS: tuple[str, ...] = (
    "run_id", "stage_id", "subject_ref", "outcome", "payload",
    "version_tuple_ref", "inputs", "budget_state", "produced_at",
)

#: Values that belong to a producing part's OWN record and may never appear in the
#: envelope. P11's SPEC publishes this rule and this list; P2 enforces it so a
#: mis-mapped run fails at the writer instead of during comparison. This is not
#: P2 adopting P11's vocabulary — nothing here is ever WRITTEN, only refused.
_FOREIGN_OUTCOMES = frozenset({
    "place", "return_to_placement", "mark_review_later", "leave_in_place",
    "mark_state", "abstain", "ask_user",
})

STAGE_DDL = """
CREATE TABLE IF NOT EXISTS stage_output (
    stage_output_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id            TEXT NOT NULL REFERENCES run_manifest (run_id),
    stage_id          TEXT NOT NULL,
    subject_ref       TEXT NOT NULL,
    outcome           TEXT NOT NULL,
    payload           TEXT,               -- opaque; never parsed by P2
    version_tuple_ref TEXT NOT NULL,
    inputs            TEXT NOT NULL,      -- canonical JSON array of subject_refs
    budget_state      TEXT NOT NULL,
    produced_at       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS stage_output_run ON stage_output (run_id, stage_id);
CREATE INDEX IF NOT EXISTS stage_output_subject ON stage_output (run_id, subject_ref);

CREATE TABLE IF NOT EXISTS stage_dimension_value (
    run_id          TEXT NOT NULL REFERENCES run_manifest (run_id),
    stage_output_id INTEGER NOT NULL REFERENCES stage_output (stage_output_id),
    stage_id        TEXT NOT NULL,        -- the EMITTING stage, which names itself
    dimension       TEXT NOT NULL,
    subject_ref     TEXT NOT NULL,
    outcome         TEXT NOT NULL,
    value           TEXT,                 -- canonical JSON, or NULL when nothing was produced
    PRIMARY KEY (run_id, dimension, subject_ref)
);
"""


class ForeignVocabulary(Exception):
    """A producing part's own record value was written into P2's envelope."""


@dataclass(frozen=True)
class DimensionValue:
    """One measured value the producing part hands P2 alongside its opaque payload.

    Each carries its own `outcome`: one stage output may produce for one subject
    and abstain for another, and §8.5 measures abstention as an outcome.
    """
    dimension: str
    subject_ref: str
    outcome: str
    value: Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check_outcome(outcome: str) -> str:
    if outcome in _FOREIGN_OUTCOMES:
        raise ForeignVocabulary(
            f"{outcome!r} is a producing part's own record value and may not be "
            f"written into stage_output; the envelope's outcomes are {OUTCOMES}"
        )
    if outcome not in OUTCOMES:
        raise ValueError(f"outcome {outcome!r} is not one of {OUTCOMES}")
    return outcome


def record_stage_output(conn: sqlite3.Connection, *, run_id: str, stage_id: str,
                        subject_ref: str, outcome: str, payload: str | None,
                        version_tuple_ref: str, inputs: Sequence[str],
                        budget_state: str,
                        dimension_values: Sequence[DimensionValue] = ()) -> int:
    """Write one envelope, plus the dimension values the stage hands over.

    §8.6: a budget deferral is `deferred` with `ceiling_reached` and is never
    `abstained`. The pairing is enforced here, because P2 Done-means 6 depends on
    it: a run whose only change is a lower ceiling must produce zero new
    divergences, which is only true if a deferral never reaches a quality verdict.
    """
    check_stage(stage_id)
    _check_outcome(outcome)
    if budget_state not in BUDGET_STATES:
        raise ValueError(f"budget_state {budget_state!r} is not one of {BUDGET_STATES}")
    if outcome == "deferred" and budget_state != "ceiling_reached":
        raise ValueError("outcome 'deferred' requires budget_state 'ceiling_reached' (§8.6)")
    if budget_state == "ceiling_reached" and outcome == "abstained":
        raise ValueError(
            "a ceiling-reached stage is 'deferred', never 'abstained': §8.6 forbids "
            "cost exhaustion becoming a judgement about evidence"
        )
    for value in dimension_values:
        check_dimension(value.dimension)
        _check_outcome(value.outcome)

    cursor = conn.execute(
        "INSERT INTO stage_output (run_id, stage_id, subject_ref, outcome, payload, "
        "version_tuple_ref, inputs, budget_state, produced_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (run_id, stage_id, subject_ref, outcome, payload, version_tuple_ref,
         canonical_json(list(inputs)), budget_state, _now()),
    )
    stage_output_id = cursor.lastrowid
    for value in dimension_values:
        conn.execute(
            "INSERT INTO stage_dimension_value (run_id, stage_output_id, stage_id, "
            "dimension, subject_ref, outcome, value) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, stage_output_id, stage_id, value.dimension, value.subject_ref,
             value.outcome,
             None if value.value is None else canonical_json(value.value)),
        )
    return stage_output_id


def stage_outputs(conn: sqlite3.Connection, run_id: str, *,
                  stage_id: str | None = None) -> list[sqlite3.Row]:
    if stage_id is None:
        return conn.execute(
            "SELECT * FROM stage_output WHERE run_id = ? ORDER BY stage_output_id",
            (run_id,)).fetchall()
    return conn.execute(
        "SELECT * FROM stage_output WHERE run_id = ? AND stage_id = ? "
        "ORDER BY stage_output_id", (run_id, check_stage(stage_id))).fetchall()


def dimension_values(conn: sqlite3.Connection, run_id: str, *,
                     dimension: str | None = None) -> list[sqlite3.Row]:
    if dimension is None:
        return conn.execute(
            "SELECT * FROM stage_dimension_value WHERE run_id = ? "
            "ORDER BY dimension, subject_ref", (run_id,)).fetchall()
    return conn.execute(
        "SELECT * FROM stage_dimension_value WHERE run_id = ? AND dimension = ? "
        "ORDER BY subject_ref", (run_id, check_dimension(dimension))).fetchall()


def stage_payload(conn: sqlite3.Connection, stage_output_id: int) -> str | None:
    """The payload exactly as it was handed over. P2 has never parsed it."""
    row = conn.execute("SELECT payload FROM stage_output WHERE stage_output_id = ?",
                       (stage_output_id,)).fetchone()
    return None if row is None else row["payload"]
```

Add to `store.py`'s `_ddl_scripts`:

```python
    from eval_harness import run, stage_output
    return [run.RUN_DDL, stage_output.STAGE_DDL]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/eval/test_stage_output.py -v`
Expected: PASS — 11 passed

- [ ] **Step 5: Commit**

```bash
git add src/eval_harness/stage_output.py src/eval_harness/store.py tests/eval/test_stage_output.py
git commit -m "feat(P2): stage output envelope, opaque payload, foreign vocabulary refused at the writer"
```

---

### Task 5: The replay bundle — manifest, file entries, sealing, supersession (Done-means 1)

**Files:**
- Create: `src/eval_harness/bundle.py`
- Modify: `src/eval_harness/store.py` — add `bundle.BUNDLE_DDL` to `_ddl_scripts`
- Test: `tests/eval/test_bundle.py`

**Interfaces:**
- Consumes: `canonical_json` (Task 1); `CORPUS_FORMS` (Task 2); `database_agent.db.transaction` (P1 Task 1).
- Produces: `BUNDLE_CONTENTS: tuple[str, ...]` (§8.5's eight listed items), `open_bundle(conn, *, corpus_form, source_scan_ref, pinned_plan_id, pinned_plan_version, policy_settings, supersedes_bundle_id=None) -> str`, `add_file_entry(conn, bundle_id, *, file_id, content_hash, hash_algorithm, handling_class, payload_ref=None, metadata_only=None) -> None`, `seal_bundle(conn, bundle_id) -> None`, `get_bundle(conn, bundle_id) -> sqlite3.Row`, `bundle_files(conn, bundle_id) -> list[sqlite3.Row]`, `rebuild_bundle(conn, bundle_id, **overrides) -> str`, `BundleSealed`, `BodyMismatch`.

**Immutability is enforced by trigger, not by convention** — the same discipline P1 applies to `events`. A bundle is opened, filled, and sealed; after `sealed_at` is stamped, every `UPDATE` on the manifest and every `INSERT`, `UPDATE` or `DELETE` on a child row raises. Before sealing, an abandoned draft can be discarded. **These triggers are on P2's own tables.** P2 does not touch `events`, and I6 (tombstone versus append) is deferred to P7 — nothing here forecloses it.

**A rebuild is a new bundle that supersedes the old** (§8.2 supersede-never-overwrite; §8.8 *"a new plan should never silently reclassify or move old files"*). `rebuild_bundle` copies the manifest, applies overrides, sets `supersedes_bundle_id`, and **leaves the superseded bundle sealed and readable**. There is no delete path.

**`body` is exactly one of two things, and which one is fixed by `corpus_form`.** SPEC Contract out §3: `payload_ref` when `corpus_form = snapshot`, `metadata_only` when `corpus_form = metadata_safe`. `add_file_entry` refuses an entry that carries the wrong one, or both, or neither — otherwise a metadata-safe bundle could silently acquire file bytes, which is the precise thing SPEC Open question 5 is unable to authorize.

**P2 stores `handling_class` and `privacy_mode` as opaque strings and validates neither.** They are P7's closed vocabularies (five classes, four operation modes), published in P7's Contract out. Copying either list into P2's source would be two vocabularies for one concept. The consequence is stated plainly: **a typo in a handling class is not caught here.** When P7 lands, import its vocabulary and validate against the imported names — do not retype the strings. This is the same discipline P1 applied to P11's eight unspelled event types, and it is recorded as a known gap at the end of this plan.

**P2 does not decide whether a bundle may leave the device.** SPEC Open question 5 is open. `corpus_form` is declared per bundle and `handling_class` is recorded per entry *"so that P7's §8.4 policy can be applied to a bundle without P2 deciding it"*. There is no export function in this plan, and no test asserts that any bundle is exportable.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_bundle.py
import sqlite3

import pytest

from eval_harness.bundle import (
    BUNDLE_CONTENTS, BodyMismatch, BundleSealed, add_file_entry, bundle_files,
    get_bundle, open_bundle, rebuild_bundle, seal_bundle,
)
from eval_harness.store import create_eval_schema


def _policy():
    """§8.5's "policy settings". privacy_mode and placement_policy are P7's and
    P10's vocabularies and are carried opaquely; the ceiling set is P1's keys."""
    return {"privacy_mode": "offline", "placement_policy": "policy-fixture",
            "budget_ceilings": {}}


def _open(conn, **overrides):
    fields = dict(corpus_form="snapshot", source_scan_ref="scan-fixture",
                  pinned_plan_id="plan-fixture", pinned_plan_version="1",
                  policy_settings=_policy())
    fields.update(overrides)
    return open_bundle(conn, **fields)


def test_the_manifest_carries_every_8_5_content_item():
    # §8.5: "a frozen corpus snapshot or a metadata-safe representation of one,
    # content hashes, extraction outputs, expected facts, accepted groups, tree
    # versions, policy settings, and expected placement or abstention outcomes."
    assert BUNDLE_CONTENTS == (
        "corpus", "content_hashes", "extraction_outputs", "expected_facts",
        "accepted_groups", "tree_versions", "policy_settings",
        "expected_placement_or_abstention",
    )
    assert len(BUNDLE_CONTENTS) == 8


def test_a_bundle_records_its_scan_plan_and_policy(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn)
    row = get_bundle(eval_conn, bundle_id)
    assert row["corpus_form"] == "snapshot"
    assert row["source_scan_ref"] == "scan-fixture"          # P3's scan_id (§1.1)
    assert row["pinned_plan_id"] == "plan-fixture"           # §8.8
    assert row["pinned_plan_version"] == "1"
    assert '"privacy_mode":"offline"' in row["policy_settings"]
    assert row["created_at"] and row["sealed_at"] is None
    assert row["supersedes_bundle_id"] is None


def test_a_corpus_form_outside_the_two_is_rejected(eval_conn):
    create_eval_schema(eval_conn)
    with pytest.raises(ValueError):
        _open(eval_conn, corpus_form="redacted")


def test_a_snapshot_entry_carries_a_payload_ref_and_not_metadata_only(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn, corpus_form="snapshot")
    add_file_entry(eval_conn, bundle_id, file_id="f1", content_hash="sha256:aa",
                   hash_algorithm="sha256", handling_class="public_low",
                   payload_ref="blobs/aa")
    entry = bundle_files(eval_conn, bundle_id)[0]
    assert entry["payload_ref"] == "blobs/aa"
    assert entry["metadata_only"] is None
    with pytest.raises(BodyMismatch):
        add_file_entry(eval_conn, bundle_id, file_id="f2", content_hash="sha256:bb",
                       hash_algorithm="sha256", handling_class="public_low",
                       metadata_only='{"size":10}')


def test_a_metadata_safe_entry_carries_metadata_only_and_no_bytes(eval_conn):
    # A metadata_safe bundle acquiring a payload_ref is the failure SPEC OQ5
    # cannot authorize. Refused structurally, not by review.
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn, corpus_form="metadata_safe")
    add_file_entry(eval_conn, bundle_id, file_id="f1", content_hash="sha256:aa",
                   hash_algorithm="sha256", handling_class="sensitive_personal",
                   metadata_only='{"size":10}')
    entry = bundle_files(eval_conn, bundle_id)[0]
    assert entry["metadata_only"] == '{"size":10}'
    assert entry["payload_ref"] is None
    with pytest.raises(BodyMismatch):
        add_file_entry(eval_conn, bundle_id, file_id="f2", content_hash="sha256:bb",
                       hash_algorithm="sha256", handling_class="public_low",
                       payload_ref="blobs/bb")


def test_an_entry_with_both_bodies_or_neither_is_refused(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn)
    with pytest.raises(BodyMismatch):
        add_file_entry(eval_conn, bundle_id, file_id="f1", content_hash="sha256:aa",
                       hash_algorithm="sha256", handling_class="public_low",
                       payload_ref="blobs/aa", metadata_only="{}")
    with pytest.raises(BodyMismatch):
        add_file_entry(eval_conn, bundle_id, file_id="f2", content_hash="sha256:bb",
                       hash_algorithm="sha256", handling_class="public_low")


def test_a_sealed_bundle_cannot_be_changed(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn)
    add_file_entry(eval_conn, bundle_id, file_id="f1", content_hash="sha256:aa",
                   hash_algorithm="sha256", handling_class="public_low",
                   payload_ref="blobs/aa")
    seal_bundle(eval_conn, bundle_id)
    with pytest.raises(BundleSealed):
        add_file_entry(eval_conn, bundle_id, file_id="f2", content_hash="sha256:bb",
                       hash_algorithm="sha256", handling_class="public_low",
                       payload_ref="blobs/bb")
    with pytest.raises(sqlite3.IntegrityError):
        eval_conn.execute("UPDATE bundle_manifest SET corpus_form = 'metadata_safe' "
                          "WHERE bundle_id = ?", (bundle_id,))
    with pytest.raises(sqlite3.IntegrityError):
        eval_conn.execute("DELETE FROM bundle_file_entry WHERE bundle_id = ?",
                          (bundle_id,))


def test_a_rebuild_supersedes_and_retains(eval_conn):
    # §8.2 supersede-never-overwrite; §8.8 a new plan never silently reclassifies.
    create_eval_schema(eval_conn)
    first = _open(eval_conn)
    add_file_entry(eval_conn, first, file_id="f1", content_hash="sha256:aa",
                   hash_algorithm="sha256", handling_class="public_low",
                   payload_ref="blobs/aa")
    seal_bundle(eval_conn, first)
    second = rebuild_bundle(eval_conn, first, pinned_plan_version="2")
    assert second != first
    assert get_bundle(eval_conn, second)["supersedes_bundle_id"] == first
    assert get_bundle(eval_conn, second)["pinned_plan_version"] == "2"
    # the old one is still there, still sealed, still readable
    assert get_bundle(eval_conn, first)["sealed_at"]
    assert bundle_files(eval_conn, first)[0]["content_hash"] == "sha256:aa"


def test_p2_validates_no_p7_vocabulary(eval_conn):
    # P7 owns the five handling classes and the four operation modes. P2 carries
    # what it is handed. A typo is NOT caught here, deliberately: retyping P7's
    # enum would be two vocabularies for one concept. See Known gaps.
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn)
    add_file_entry(eval_conn, bundle_id, file_id="f1", content_hash="sha256:aa",
                   hash_algorithm="sha256", handling_class="anything-p7-says",
                   payload_ref="blobs/aa")
    assert bundle_files(eval_conn, bundle_id)[0]["handling_class"] == "anything-p7-says"


def test_p2_source_carries_no_p7_class_or_mode_name():
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness"
    forbidden = ("public_low", "personal_non_sensitive", "sensitive_personal",
                 "highly_sensitive_credential_bearing", "unreadable_unclassified",
                 "local_model", "cloud_assisted", "hybrid")
    for path in src.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for term in forbidden:
            assert term not in text, f"{path.name} carries P7's {term!r}"


def test_a_bundle_needs_no_live_filesystem(eval_conn, tmp_path):
    # Done-means 1: built, stored, and read back with nothing on disk to consult.
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn, corpus_form="metadata_safe")
    add_file_entry(eval_conn, bundle_id, file_id="f1", content_hash="sha256:aa",
                   hash_algorithm="sha256", handling_class="public_low",
                   metadata_only='{"size":10}')
    seal_bundle(eval_conn, bundle_id)
    assert not any(tmp_path.glob("corpus*"))
    assert bundle_files(eval_conn, bundle_id)[0]["content_hash"] == "sha256:aa"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/eval/test_bundle.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_harness.bundle'`

- [ ] **Step 3: Write the implementation**

```python
# src/eval_harness/bundle.py
"""Contract out §3 — the replay bundle.

Contents are exactly §8.5's list. A bundle is immutable once sealed, and a rebuild
is a NEW bundle that supersedes the old and retains it (§8.2, §8.8).

P2 records `handling_class` and `privacy_mode` and validates neither: those are
P7's closed vocabularies and copying them here would be two vocabularies for one
concept. P2 does not decide whether a bundle may leave the device — SPEC Open
question 5 is open and there is no export path in this module.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

from eval_harness.store import canonical_json
from eval_harness.vocabulary import CORPUS_FORMS

#: §8.5's contents list, verbatim, as the names of the things a bundle must hold.
#: Each maps to a table created here or in Tasks 6-8.
BUNDLE_CONTENTS: tuple[str, ...] = (
    "corpus",                            # bundle_file_entry.body (both forms)
    "content_hashes",                    # bundle_file_entry.content_hash
    "extraction_outputs",                # bundle_extraction_output/_run/_text_unit (Task 6)
    "expected_facts",                    # bundle_expectation, dimension = fact (Task 8)
    "accepted_groups",                   # bundle_accepted_group (Task 8)
    "tree_versions",                     # bundle_manifest.pinned_plan_id/version
    "policy_settings",                   # bundle_manifest.policy_settings
    "expected_placement_or_abstention",  # bundle_expectation, dimensions 9 and 10 (Task 8)
)

BUNDLE_DDL = """
CREATE TABLE IF NOT EXISTS bundle_manifest (
    bundle_id            TEXT PRIMARY KEY,
    created_at           TEXT NOT NULL,
    corpus_form          TEXT NOT NULL,
    source_scan_ref      TEXT,
    pinned_plan_id       TEXT,
    pinned_plan_version  TEXT,
    policy_settings      TEXT NOT NULL,
    supersedes_bundle_id TEXT REFERENCES bundle_manifest (bundle_id),
    sealed_at            TEXT
);
CREATE TABLE IF NOT EXISTS bundle_file_entry (
    bundle_id      TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    file_id        TEXT NOT NULL,
    content_hash   TEXT NOT NULL,
    hash_algorithm TEXT NOT NULL,
    handling_class TEXT,                 -- P7's vocabulary, carried opaquely
    payload_ref    TEXT,                 -- corpus_form = snapshot
    metadata_only  TEXT,                 -- corpus_form = metadata_safe
    PRIMARY KEY (bundle_id, file_id)
);

-- A sealed bundle is immutable (Contract out §3). These triggers are on P2's own
-- tables; `events` is P1's and P2 never writes it.
CREATE TRIGGER IF NOT EXISTS bundle_manifest_sealed_no_update
BEFORE UPDATE ON bundle_manifest
WHEN OLD.sealed_at IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_manifest_sealed_no_delete
BEFORE DELETE ON bundle_manifest
WHEN OLD.sealed_at IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'a sealed bundle is retained, never deleted (8.2)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_file_entry_sealed_no_insert
BEFORE INSERT ON bundle_file_entry
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = NEW.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_file_entry_sealed_no_update
BEFORE UPDATE ON bundle_file_entry
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_file_entry_sealed_no_delete
BEFORE DELETE ON bundle_file_entry
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;
"""


class BundleSealed(Exception):
    """A sealed bundle was written to. Rebuild instead — it supersedes (§8.2)."""


class BodyMismatch(Exception):
    """An entry's body does not match its bundle's declared corpus_form."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def open_bundle(conn: sqlite3.Connection, *, corpus_form: str,
                source_scan_ref: str | None, pinned_plan_id: str | None,
                pinned_plan_version: str | None, policy_settings: dict,
                supersedes_bundle_id: str | None = None) -> str:
    """Open a draft bundle. Fill it, then `seal_bundle` to make it immutable."""
    if corpus_form not in CORPUS_FORMS:
        raise ValueError(f"corpus_form {corpus_form!r} is not one of {CORPUS_FORMS}")
    bundle_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO bundle_manifest (bundle_id, created_at, corpus_form, "
        "source_scan_ref, pinned_plan_id, pinned_plan_version, policy_settings, "
        "supersedes_bundle_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (bundle_id, _now(), corpus_form, source_scan_ref, pinned_plan_id,
         pinned_plan_version, canonical_json(policy_settings), supersedes_bundle_id),
    )
    return bundle_id


def _require_open(conn: sqlite3.Connection, bundle_id: str) -> sqlite3.Row:
    row = get_bundle(conn, bundle_id)
    if row is None:
        raise KeyError(f"no bundle {bundle_id!r}")
    if row["sealed_at"] is not None:
        raise BundleSealed(
            f"bundle {bundle_id} was sealed at {row['sealed_at']}; a rebuild "
            "creates a new bundle that supersedes it (§8.2)"
        )
    return row


def add_file_entry(conn: sqlite3.Connection, bundle_id: str, *, file_id: str,
                   content_hash: str, hash_algorithm: str,
                   handling_class: str | None,
                   payload_ref: str | None = None,
                   metadata_only: str | None = None) -> None:
    """One `bundle_file_entry`. Exactly one body, fixed by the bundle's corpus_form."""
    row = _require_open(conn, bundle_id)
    if (payload_ref is None) == (metadata_only is None):
        raise BodyMismatch("an entry carries exactly one body: payload_ref "
                           "(snapshot) or metadata_only (metadata_safe)")
    if row["corpus_form"] == "snapshot" and payload_ref is None:
        raise BodyMismatch("a snapshot bundle's entries carry payload_ref")
    if row["corpus_form"] == "metadata_safe" and metadata_only is None:
        raise BodyMismatch(
            "a metadata_safe bundle's entries carry metadata_only; whether such a "
            "bundle may carry anything more is SPEC Open question 5, not P2's call"
        )
    conn.execute(
        "INSERT INTO bundle_file_entry (bundle_id, file_id, content_hash, "
        "hash_algorithm, handling_class, payload_ref, metadata_only) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (bundle_id, file_id, content_hash, hash_algorithm, handling_class,
         payload_ref, metadata_only),
    )


def seal_bundle(conn: sqlite3.Connection, bundle_id: str) -> None:
    _require_open(conn, bundle_id)
    conn.execute("UPDATE bundle_manifest SET sealed_at = ? WHERE bundle_id = ?",
                 (_now(), bundle_id))


def get_bundle(conn: sqlite3.Connection, bundle_id: str) -> sqlite3.Row:
    return conn.execute("SELECT * FROM bundle_manifest WHERE bundle_id = ?",
                        (bundle_id,)).fetchone()


def bundle_files(conn: sqlite3.Connection, bundle_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM bundle_file_entry WHERE bundle_id = ? ORDER BY file_id",
        (bundle_id,)).fetchall()


def rebuild_bundle(conn: sqlite3.Connection, bundle_id: str, **overrides) -> str:
    """Open a NEW bundle that supersedes `bundle_id`. The old one is retained.

    §8.2's supersede-never-overwrite, applied to bundles. The caller re-adds the
    contents it wants; nothing is copied silently, because a rebuild that quietly
    carried the old contents forward would make the two indistinguishable.
    """
    old = get_bundle(conn, bundle_id)
    if old is None:
        raise KeyError(f"no bundle {bundle_id!r}")
    import json
    fields = dict(
        corpus_form=old["corpus_form"], source_scan_ref=old["source_scan_ref"],
        pinned_plan_id=old["pinned_plan_id"],
        pinned_plan_version=old["pinned_plan_version"],
        policy_settings=json.loads(old["policy_settings"]),
    )
    fields.update(overrides)
    return open_bundle(conn, supersedes_bundle_id=bundle_id, **fields)
```

Add to `store.py`'s `_ddl_scripts`:

```python
    from eval_harness import bundle, run, stage_output
    return [bundle.BUNDLE_DDL, run.RUN_DDL, stage_output.STAGE_DDL]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/eval/test_bundle.py -v`
Expected: PASS — 11 passed

- [ ] **Step 5: Commit**

```bash
git add src/eval_harness/bundle.py src/eval_harness/store.py tests/eval/test_bundle.py
git commit -m "feat(P2): replay bundle, sealed by trigger, superseded never overwritten"
```

---

### Task 6: Bundle extraction rows — outputs, runs, and text units (Done-means 1)

**Files:**
- Modify: `src/eval_harness/bundle.py` — add the three tables and their writers
- Create: `tests/eval/fixtures/p4_runs.json`
- Create: `tests/eval/fixtures/p4_text_units.json`
- Test: `tests/eval/test_bundle_extraction.py`

**Interfaces:**
- Consumes: `open_bundle`, `add_file_entry`, `seal_bundle`, `_require_open` (Task 5); `canonical_json` (Task 1).
- Produces: `add_extraction_output(conn, bundle_id, *, content_hash, extractor_version, observation_key, payload) -> None`, `add_extraction_run(conn, bundle_id, *, row: dict) -> None`, `add_text_unit(conn, bundle_id, *, row: dict) -> None`, `extraction_outputs(conn, bundle_id, *, content_hash=None, extractor_version=None) -> list[sqlite3.Row]`, `extraction_runs(conn, bundle_id) -> list[dict]`, `text_units(conn, bundle_id, *, run_id=None) -> list[dict]`, `P4_RUN_FIELDS: tuple[str, ...]`, `P4_TEXT_UNIT_FIELDS: tuple[str, ...]`.

**P4 does not exist, so these rows come from a recorded fixture, and the fixture is copied from P4's SPEC.** [`../P4-evidence-shape/SPEC.md`](../P4-evidence-shape/SPEC.md) Record 2 and Record 3 print both shapes in full; the fixture files below carry those field names and those example values, and nothing invented. **P2 defines no part of either shape.** When P4 lands, the fixtures are replaced by real rows and the column list is checked against P4's, not rewritten from memory.

**The full P4 row is stored verbatim alongside the queried columns.** SPEC Contract out §3: *"Read exactly as P4 publishes them; P2 defines none of it."* The columns P2 promotes are exactly the ones §3 enumerates — `run_id`, `file_id`, `content_hash`, extractor name and version, `source_type`, `config_fingerprint`, `completeness`, `coverage`, `observation_count` — because Done-means 13's count line and adversarial case A9 query them. Every other field P4 publishes is retained in a verbatim `row` column, so a bundle never becomes a lossy copy of the record it exists to replay.

**Keying is deliberately divergent from P4, and neither side should later be "fixed" into agreement.** SPEC Contract out §3: `bundle_extraction_output[]` is keyed by content hash **plus extractor version**, so one bundle holds two versions' outputs side by side for a diff. P4's `observation_key` deliberately **excludes** the version — `sha256(content_hash ‖ extractor_name ‖ locator ‖ raw_value)` — so a citation recorded today still resolves after an extractor upgrade (§8.7). Both are stored, and the test below asserts both properties on the same rows.

**Why the text rows are here.** After P4's D12 the text is not on the observation — an observation is a *located value* and `text_units` is the unit it points into. Dimension 1 is §8.5's *"Did the expected text … appear?"*, which P4 states is a query against `text_units`. Without these rows the first of the ten dimensions has nothing to query, and a `capped` OCR run's recovered text — exactly what a version-to-version diff of a new OCR engine must compare — is absent from the bundle. **Whether a `metadata_safe` bundle may carry them is SPEC Open question 5 and is not answered here:** `add_text_unit` refuses on a `metadata_safe` bundle with an error naming OQ5, rather than silently allowing or silently forbidding it. That refusal is reversible in one line the day OQ5 closes; a silent allow would not be.

- [ ] **Step 1: Write the fixtures**

```json
// tests/eval/fixtures/p4_runs.json
// P4 SPEC Record 2 (D5). Field names and example values copied from that record.
// P2 defines none of this shape. Replace with real P4 rows when P4 lands.
[
  {
    "run_id": "run-ocr-1", "file_id": "file-book", "content_hash": "sha256:book",
    "extractor_name": "ocr.apple_vision", "extractor_version": "2.4.1",
    "source_type": "ocr", "analysis_tier": "ocr",
    "config": {"dpi": 200, "languages": ["en", "zh-Hans"], "recognition": "accurate"},
    "config_fingerprint": "sha256:cfg-ocr", "completeness": "capped",
    "coverage": {"units": "pages", "processed": 40, "total": 312},
    "observation_count": 118,
    "started_at": "2026-08-19T00:00:00+00:00",
    "finished_at": "2026-08-19T00:04:00+00:00", "failure_reason": null
  },
  {
    "run_id": "run-native-1", "file_id": "file-syllabus", "content_hash": "sha256:syl",
    "extractor_name": "pdf.native", "extractor_version": "1.0.0",
    "source_type": "text", "analysis_tier": "native",
    "config": {}, "config_fingerprint": "sha256:cfg-native",
    "completeness": "complete",
    "coverage": {"units": "pages", "processed": 3, "total": 3},
    "observation_count": 7,
    "started_at": "2026-08-19T00:00:00+00:00",
    "finished_at": "2026-08-19T00:00:02+00:00", "failure_reason": null
  },
  {
    "run_id": "run-broken-1", "file_id": "file-broken", "content_hash": "sha256:brk",
    "extractor_name": "pdf.native", "extractor_version": "1.0.0",
    "source_type": "text", "analysis_tier": "native",
    "config": {}, "config_fingerprint": "sha256:cfg-native",
    "completeness": "unreadable",
    "coverage": {"units": "pages", "processed": 0, "total": 12},
    "observation_count": 0,
    "started_at": "2026-08-19T00:00:00+00:00",
    "finished_at": "2026-08-19T00:00:01+00:00",
    "failure_reason": "damaged"
  }
]
```

```json
// tests/eval/fixtures/p4_text_units.json
// P4 SPEC Record 3 (D12, G1). Keyed by (run_id, container_path).
[
  {"run_id": "run-ocr-1", "container_path": [{"kind": "page", "index": 4}],
   "unit_locator": "page=4", "text": "recovered page four text",
   "length": 24, "truncated": false},
  {"run_id": "run-native-1", "container_path": [],
   "unit_locator": "", "text": "the whole syllabus text",
   "length": 23, "truncated": false}
]
```

- [ ] **Step 2: Write the failing test**

```python
# tests/eval/test_bundle_extraction.py
import json
from pathlib import Path

import pytest

from eval_harness.bundle import (
    P4_RUN_FIELDS, P4_TEXT_UNIT_FIELDS, add_extraction_output, add_extraction_run,
    add_file_entry, add_text_unit, extraction_outputs, extraction_runs, open_bundle,
    text_units,
)
from eval_harness.store import create_eval_schema

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _snapshot(conn):
    return open_bundle(conn, corpus_form="snapshot", source_scan_ref="scan-fixture",
                       pinned_plan_id="plan-fixture", pinned_plan_version="1",
                       policy_settings={})


def test_the_promoted_run_columns_are_exactly_the_ones_the_spec_enumerates():
    # SPEC Contract out §3: "run_id, file_id, content_hash, extractor name and
    # version, source_type, config_fingerprint, completeness, coverage,
    # observation_count."
    assert P4_RUN_FIELDS == (
        "run_id", "file_id", "content_hash", "extractor_name", "extractor_version",
        "source_type", "config_fingerprint", "completeness", "coverage",
        "observation_count",
    )
    assert P4_TEXT_UNIT_FIELDS == (
        "run_id", "container_path", "unit_locator", "text", "length", "truncated",
    )


def test_a_run_row_round_trips_every_field_p4_publishes(eval_conn):
    # "Read exactly as P4 publishes them; P2 defines none of it." Fields P2 does
    # not promote to columns survive in the verbatim row.
    create_eval_schema(eval_conn)
    bundle_id = _snapshot(eval_conn)
    for row in _load("p4_runs.json"):
        add_extraction_run(eval_conn, bundle_id, row=row)
    stored = {r["run_id"]: r for r in extraction_runs(eval_conn, bundle_id)}
    ocr = stored["run-ocr-1"]
    assert ocr["completeness"] == "capped"
    assert ocr["coverage"] == {"units": "pages", "processed": 40, "total": 312}
    assert ocr["analysis_tier"] == "ocr"          # not promoted, not lost
    assert ocr["config"] == {"dpi": 200, "languages": ["en", "zh-Hans"],
                             "recognition": "accurate"}
    assert stored["run-broken-1"]["failure_reason"] == "damaged"


def test_two_extractor_versions_of_one_content_hash_coexist(eval_conn):
    # This is why bundle_extraction_output is keyed by hash PLUS version: one
    # bundle holds both sides of a version-to-version diff (§8.5).
    create_eval_schema(eval_conn)
    bundle_id = _snapshot(eval_conn)
    add_extraction_output(eval_conn, bundle_id, content_hash="sha256:syl",
                          extractor_version="1.0.0",
                          observation_key="sha256:obs-a", payload='{"v":"old"}')
    add_extraction_output(eval_conn, bundle_id, content_hash="sha256:syl",
                          extractor_version="2.0.0",
                          observation_key="sha256:obs-a", payload='{"v":"new"}')
    both = extraction_outputs(eval_conn, bundle_id, content_hash="sha256:syl")
    assert {r["extractor_version"] for r in both} == {"1.0.0", "2.0.0"}
    assert {r["payload"] for r in both} == {'{"v":"old"}', '{"v":"new"}'}


def test_the_observation_key_survives_an_extractor_upgrade(eval_conn):
    # P4's observation_key deliberately EXCLUDES the extractor version, so a
    # citation recorded today still resolves after an upgrade (§8.7). P2's key
    # deliberately includes it. Neither should be "fixed" into agreement.
    create_eval_schema(eval_conn)
    bundle_id = _snapshot(eval_conn)
    add_extraction_output(eval_conn, bundle_id, content_hash="sha256:syl",
                          extractor_version="1.0.0",
                          observation_key="sha256:obs-a", payload='{"v":"old"}')
    add_extraction_output(eval_conn, bundle_id, content_hash="sha256:syl",
                          extractor_version="2.0.0",
                          observation_key="sha256:obs-a", payload='{"v":"new"}')
    cited = eval_conn.execute(
        "SELECT DISTINCT observation_key FROM bundle_extraction_output "
        "WHERE bundle_id = ?", (bundle_id,)).fetchall()
    assert [r["observation_key"] for r in cited] == ["sha256:obs-a"]


def test_an_extraction_payload_is_opaque(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _snapshot(eval_conn)
    blob = "not JSON, still an observation payload"
    add_extraction_output(eval_conn, bundle_id, content_hash="sha256:x",
                          extractor_version="1.0.0", observation_key="sha256:k",
                          payload=blob)
    assert extraction_outputs(eval_conn, bundle_id)[0]["payload"] == blob


def test_text_units_round_trip_with_their_container_path(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _snapshot(eval_conn)
    for row in _load("p4_text_units.json"):
        add_text_unit(eval_conn, bundle_id, row=row)
    page_four = text_units(eval_conn, bundle_id, run_id="run-ocr-1")[0]
    assert page_four["container_path"] == [{"kind": "page", "index": 4}]
    assert page_four["unit_locator"] == "page=4"
    assert page_four["text"] == "recovered page four text"
    assert page_four["truncated"] is False
    whole_file = text_units(eval_conn, bundle_id, run_id="run-native-1")[0]
    assert whole_file["container_path"] == []          # D12: [] is the whole file


def test_a_metadata_safe_bundle_refuses_text_units_and_names_the_open_question(eval_conn):
    # SPEC Open question 5: "What exactly does 'metadata-safe' exclude?" P2 does
    # not answer it. It refuses, naming OQ5, rather than deciding either way in
    # silence. One line changes the day OQ5 closes.
    create_eval_schema(eval_conn)
    bundle_id = open_bundle(eval_conn, corpus_form="metadata_safe",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    with pytest.raises(NotImplementedError) as excinfo:
        add_text_unit(eval_conn, bundle_id, row=_load("p4_text_units.json")[0])
    assert "Open question 5" in str(excinfo.value)


def test_p2_invents_no_text_unit_field():
    # The shape is P4's D12 and P2 publishes none of it.
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness" / "bundle.py"
    text = src.read_text(encoding="utf-8")
    for invented in ("excerpt", "snippet", "page_text", "ocr_text", "full_text"):
        assert invented not in text
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/eval/test_bundle_extraction.py -v`
Expected: FAIL with `ImportError: cannot import name 'add_extraction_run' from 'eval_harness.bundle'`

- [ ] **Step 4: Extend bundle.py**

Append to `BUNDLE_DDL`:

```sql
CREATE TABLE IF NOT EXISTS bundle_extraction_output (
    bundle_id         TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    content_hash      TEXT NOT NULL,
    extractor_version TEXT NOT NULL,
    observation_key   TEXT NOT NULL,   -- P4's citation handle; EXCLUDES the version
    payload           TEXT,            -- opaque observation payload
    PRIMARY KEY (bundle_id, content_hash, extractor_version, observation_key)
);
CREATE TABLE IF NOT EXISTS bundle_extraction_run (
    bundle_id          TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    run_id             TEXT NOT NULL,
    file_id            TEXT,
    content_hash       TEXT,
    extractor_name     TEXT,
    extractor_version  TEXT,
    source_type        TEXT,
    config_fingerprint TEXT,
    completeness       TEXT,
    coverage           TEXT,           -- P4's {units, processed, total}, canonical JSON
    observation_count  INTEGER,
    row                TEXT NOT NULL,  -- P4's whole row, verbatim; nothing is lost
    PRIMARY KEY (bundle_id, run_id)
);
CREATE TABLE IF NOT EXISTS bundle_text_unit (
    bundle_id     TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    run_id        TEXT NOT NULL,
    unit_locator  TEXT NOT NULL,
    row           TEXT NOT NULL,       -- P4's whole row, verbatim
    PRIMARY KEY (bundle_id, run_id, unit_locator)
);
```

Append the writers and readers to `bundle.py`:

```python
#: P4 SPEC Record 2 (D5), the subset SPEC Contract out §3 enumerates and P2 queries.
#: Every other field P4 publishes is retained verbatim in the `row` column.
P4_RUN_FIELDS: tuple[str, ...] = (
    "run_id", "file_id", "content_hash", "extractor_name", "extractor_version",
    "source_type", "config_fingerprint", "completeness", "coverage",
    "observation_count",
)

#: P4 SPEC Record 3 (D12, G1). P2 defines none of it.
P4_TEXT_UNIT_FIELDS: tuple[str, ...] = (
    "run_id", "container_path", "unit_locator", "text", "length", "truncated",
)


def add_extraction_output(conn: sqlite3.Connection, bundle_id: str, *,
                          content_hash: str, extractor_version: str,
                          observation_key: str, payload: str | None) -> None:
    """One opaque observation payload, keyed by content hash PLUS extractor version.

    The key deliberately diverges from P4's `observation_key`, which excludes the
    version so a citation survives an upgrade (§8.7). Both are stored: the key
    holds two versions apart for a diff, `observation_key` holds them together for
    a citation.
    """
    _require_open(conn, bundle_id)
    conn.execute(
        "INSERT INTO bundle_extraction_output (bundle_id, content_hash, "
        "extractor_version, observation_key, payload) VALUES (?, ?, ?, ?, ?)",
        (bundle_id, content_hash, extractor_version, observation_key, payload),
    )


def add_extraction_run(conn: sqlite3.Connection, bundle_id: str, *, row: dict) -> None:
    """One P4 `extraction_runs` row, read exactly as P4 publishes it."""
    _require_open(conn, bundle_id)
    promoted = [row.get(f) for f in P4_RUN_FIELDS]
    promoted[P4_RUN_FIELDS.index("coverage")] = canonical_json(row.get("coverage"))
    conn.execute(
        "INSERT INTO bundle_extraction_run (bundle_id, "
        + ", ".join(P4_RUN_FIELDS) + ", row) VALUES ("
        + ", ".join("?" * (len(P4_RUN_FIELDS) + 2)) + ")",
        (bundle_id, *promoted, canonical_json(row)),
    )


def add_text_unit(conn: sqlite3.Connection, bundle_id: str, *, row: dict) -> None:
    """One P4 `text_units` row (D12, G1), read exactly as P4 publishes it."""
    manifest = _require_open(conn, bundle_id)
    if manifest["corpus_form"] == "metadata_safe":
        raise NotImplementedError(
            "whether a metadata_safe bundle may carry text_units is SPEC Open "
            "question 5 (§8.4 requires full extracted text to remain local; §8.5 "
            "offers a metadata-safe representation and defines neither). P2 does "
            "not decide it."
        )
    conn.execute(
        "INSERT INTO bundle_text_unit (bundle_id, run_id, unit_locator, row) "
        "VALUES (?, ?, ?, ?)",
        (bundle_id, row["run_id"], row["unit_locator"], canonical_json(row)),
    )


def extraction_outputs(conn: sqlite3.Connection, bundle_id: str, *,
                       content_hash: str | None = None,
                       extractor_version: str | None = None) -> list[sqlite3.Row]:
    sql = "SELECT * FROM bundle_extraction_output WHERE bundle_id = ?"
    args: list = [bundle_id]
    if content_hash is not None:
        sql += " AND content_hash = ?"
        args.append(content_hash)
    if extractor_version is not None:
        sql += " AND extractor_version = ?"
        args.append(extractor_version)
    return conn.execute(sql + " ORDER BY content_hash, extractor_version",
                        args).fetchall()


def extraction_runs(conn: sqlite3.Connection, bundle_id: str) -> list[dict]:
    """P4's rows, as P4 wrote them."""
    import json
    return [json.loads(r["row"]) for r in conn.execute(
        "SELECT row FROM bundle_extraction_run WHERE bundle_id = ? ORDER BY run_id",
        (bundle_id,))]


def text_units(conn: sqlite3.Connection, bundle_id: str, *,
               run_id: str | None = None) -> list[dict]:
    import json
    if run_id is None:
        rows = conn.execute(
            "SELECT row FROM bundle_text_unit WHERE bundle_id = ? "
            "ORDER BY run_id, unit_locator", (bundle_id,))
    else:
        rows = conn.execute(
            "SELECT row FROM bundle_text_unit WHERE bundle_id = ? AND run_id = ? "
            "ORDER BY unit_locator", (bundle_id, run_id))
    return [json.loads(r["row"]) for r in rows]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/eval/test_bundle_extraction.py -v`
Expected: PASS — 8 passed

- [ ] **Step 6: Commit**

```bash
git add src/eval_harness/bundle.py tests/eval/fixtures/p4_runs.json tests/eval/fixtures/p4_text_units.json tests/eval/test_bundle_extraction.py
git commit -m "feat(P2): bundle carries P4's runs, outputs and text units verbatim, keyed for a version diff"
```

---

### Task 7: `bundle_learning_record[]` — the negative examples a replay needs

**Files:**
- Modify: `src/eval_harness/bundle.py` — add the table and its writer/reader
- Test: `tests/eval/test_bundle_learning.py`

**Interfaces:**
- Consumes: `_require_open`, `canonical_json`; `database_agent.learning.learning_records(conn, scope, subject_id) -> list[sqlite3.Row]`, `database_agent.learning.SCOPES` (P1 Task 9); `database_agent.db.create_schema` (P1 Task 3).
- Produces: `LEARNING_RECORD_FIELDS: tuple[str, ...]`, `capture_learning_records(conn, bundle_id, *, scope, subject_id) -> int`, `bundle_learning_records(conn, bundle_id, *, scope=None, subject_id=None) -> list[dict]`.

**Why this table exists at all.** [`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md), binding: *"a replay bundle that exercises SR6 or `USER_REJECTED_EQUIVALENT` must carry the matching `bundle_learning_record[]` rows. Otherwise a run with the store populated and a run without it compare as a grouping-quality regression when the cause is a missing negative example."* Six parts — P6, P7, P8, P9, P10, P11 — now query the learning store before they propose. A bundle that omits their inputs produces a comparison that blames the algorithm for the harness.

**Same document, binding: the attribution does not move.** *"Dimension attribution stays with grouping / placement / factual_validation, not with a new stage."* This plan mints no learning stage and no learning dimension.

**The three opaque fields are copied, never interpreted.** `polarity ∈ accept | reject`, `proposal_class` and `basis_key` are supplied by the acting part on the event it authors; P1 stores and returns all three and decides nothing from them, and P2 does the same. **P2 applies no suppression rule.** Query-before-propose is the *acting* part's rule, enforced in that part; a bundle carries the rows so that the part's rule has the same inputs it had live.

**"Evidence refs" resolves to whatever P1's row carries.** SPEC Contract out §3 names *"evidence refs"* as a field of a `bundle_learning_record`. §8.2's event record field is *"a structured explanation **or** evidence reference"* — one field, which P1 spells `explanation`. Rather than mint a second name for it, `capture_learning_records` stores P1's whole row verbatim in a `row` column and promotes the five fields the SPEC enumerates by name. The naming divergence is recorded in the report accompanying this plan and **is not resolved here**.

**A capture is a snapshot, not a live read.** The rows are copied into the bundle at capture time. A later reset in P1's store does not retroactively change a sealed bundle — which is the whole point: two runs over one bundle must see the same negative examples.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_bundle_learning.py
import pytest
from database_agent.db import create_schema
from database_agent.events import append_event
from database_agent.learning import SCOPES, reset_preferences

from eval_harness.bundle import (
    LEARNING_RECORD_FIELDS, bundle_learning_records, capture_learning_records,
    open_bundle, seal_bundle,
)
from eval_harness.store import create_eval_schema


def _reject(conn, *, subject, basis_key, proposal_class="group"):
    """A user rejection, authored by the acting part (M8: P1 only writes)."""
    return append_event(
        conn, event_type="user group decision", subsystem="P9",
        component_version="p9-fixture", observed_at="2026-08-19T00:00:00+00:00",
        explanation="fixture rejection", user_id="u1",
        correction_scope="group", correction_subject=subject,
        polarity="reject", proposal_class=proposal_class, basis_key=basis_key,
    )


def _bundle(conn):
    return open_bundle(conn, corpus_form="snapshot", source_scan_ref="scan-fixture",
                       pinned_plan_id="plan-fixture", pinned_plan_version="1",
                       policy_settings={})


def test_the_five_named_fields():
    # SPEC Contract out §3: "scope, subject_id, proposal_class, basis_key,
    # polarity, evidence refs."
    assert LEARNING_RECORD_FIELDS == (
        "scope", "subject_id", "polarity", "proposal_class", "basis_key",
    )


def test_a_rejection_is_captured_with_all_three_opaque_fields(eval_conn):
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    _reject(eval_conn, subject="group-7", basis_key="anchor-a|anchor-b")
    bundle_id = _bundle(eval_conn)
    assert capture_learning_records(eval_conn, bundle_id, scope="group",
                                    subject_id="group-7") == 1
    row = bundle_learning_records(eval_conn, bundle_id)[0]
    assert row["scope"] == "group"
    assert row["subject_id"] == "group-7"
    assert row["polarity"] == "reject"
    assert row["proposal_class"] == "group"
    assert row["basis_key"] == "anchor-a|anchor-b"
    # §8.2's "structured explanation or evidence reference" survives verbatim.
    assert row["row"]["explanation"] == "fixture rejection"


def test_p2_applies_no_suppression_rule(eval_conn):
    # Query-before-propose is the ACTING part's rule (10-i4-learning-ops.md).
    # P2 carries the rows; it never decides that a reject means "do not emit".
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness"
    for path in src.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "polarity ==" not in text, path.name
        assert 'polarity") ==' not in text, path.name


def test_a_sealed_bundle_keeps_the_records_a_later_reset_removed(eval_conn):
    # Two runs over one bundle must see the same negative examples, or the
    # comparison measures the store instead of the algorithm.
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    _reject(eval_conn, subject="group-7", basis_key="anchor-a")
    bundle_id = _bundle(eval_conn)
    capture_learning_records(eval_conn, bundle_id, scope="group", subject_id="group-7")
    seal_bundle(eval_conn, bundle_id)
    reset_preferences(eval_conn, "group", "group-7", author="P13",
                      component_version="p13-fixture", user_id="u1")
    assert len(bundle_learning_records(eval_conn, bundle_id)) == 1


def test_an_empty_capture_is_recorded_as_empty_not_as_missing(eval_conn):
    # A bundle with no negative example is a legal bundle. What must never happen
    # is a bundle that silently omits one that existed.
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    assert capture_learning_records(eval_conn, bundle_id, scope="group",
                                    subject_id="group-nothing") == 0
    assert bundle_learning_records(eval_conn, bundle_id) == []


def test_scope_is_p1s_and_is_exact(eval_conn):
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    assert set(SCOPES) == {"file", "group", "node", "template", "domain", "corpus"}
    with pytest.raises(ValueError):
        capture_learning_records(eval_conn, bundle_id, scope="destination node",
                                 subject_id="n1")


def test_a_file_scoped_record_is_not_returned_by_a_corpus_scoped_read(eval_conn):
    # §8.7 scope discipline: one transcript belonging in a Columbia packet "should
    # not teach the engine that all transcripts belong there." P2 reads scope; it
    # never assigns or widens it.
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    append_event(eval_conn, event_type="user group decision", subsystem="P9",
                 component_version="p9-fixture",
                 observed_at="2026-08-19T00:00:00+00:00",
                 explanation="file-scoped", user_id="u1",
                 correction_scope="file", correction_subject="file-1",
                 polarity="reject", proposal_class="membership",
                 basis_key="group-1|file-1")
    bundle_id = _bundle(eval_conn)
    assert capture_learning_records(eval_conn, bundle_id, scope="corpus",
                                    subject_id="file-1") == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/eval/test_bundle_learning.py -v`
Expected: FAIL with `ImportError: cannot import name 'capture_learning_records' from 'eval_harness.bundle'`

- [ ] **Step 3: Extend bundle.py**

Append to `BUNDLE_DDL`:

```sql
CREATE TABLE IF NOT EXISTS bundle_learning_record (
    bundle_id      TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    event_id       INTEGER NOT NULL,
    scope          TEXT NOT NULL,
    subject_id     TEXT NOT NULL,
    polarity       TEXT,          -- opaque; accept | reject, supplied by the acting part
    proposal_class TEXT,          -- opaque
    basis_key      TEXT,          -- opaque
    row            TEXT NOT NULL, -- P1's whole row, verbatim, incl. §8.2's explanation
    PRIMARY KEY (bundle_id, event_id)
);
```

Append to `bundle.py`:

```python
#: SPEC Contract out §3's named fields. "evidence refs" is §8.2's "structured
#: explanation or evidence reference", which P1 spells `explanation` and which
#: survives in the verbatim `row`. P2 mints no second name for it.
LEARNING_RECORD_FIELDS: tuple[str, ...] = (
    "scope", "subject_id", "polarity", "proposal_class", "basis_key",
)


def capture_learning_records(conn: sqlite3.Connection, bundle_id: str, *,
                             scope: str, subject_id: str) -> int:
    """Snapshot P1's §8.7 records at one scope and subject into the bundle.

    Required by 10-i4-learning-ops.md: a bundle exercising SR6 or
    USER_REJECTED_EQUIVALENT must carry these, or a store-populated run and a
    store-empty run compare as a grouping regression when the cause is a missing
    negative example.

    P2 copies `polarity`, `proposal_class` and `basis_key` and interprets none of
    them. Suppression is the acting part's rule, applied in that part.
    """
    from database_agent.learning import SCOPES, learning_records

    _require_open(conn, bundle_id)
    if scope not in SCOPES:
        raise ValueError(f"unknown scope {scope!r}; §8.7 defines exactly {SCOPES}")
    captured = 0
    for row in learning_records(conn, scope, subject_id):
        record = {k: row[k] for k in row.keys()}
        conn.execute(
            "INSERT INTO bundle_learning_record (bundle_id, event_id, scope, "
            "subject_id, polarity, proposal_class, basis_key, row) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(bundle_id, event_id) DO NOTHING",
            (bundle_id, row["event_id"], scope, subject_id, row["polarity"],
             row["proposal_class"], row["basis_key"], canonical_json(record)),
        )
        captured += 1
    return captured


def bundle_learning_records(conn: sqlite3.Connection, bundle_id: str, *,
                            scope: str | None = None,
                            subject_id: str | None = None) -> list[dict]:
    import json
    sql = "SELECT * FROM bundle_learning_record WHERE bundle_id = ?"
    args: list = [bundle_id]
    if scope is not None:
        sql += " AND scope = ?"
        args.append(scope)
    if subject_id is not None:
        sql += " AND subject_id = ?"
        args.append(subject_id)
    out = []
    for r in conn.execute(sql + " ORDER BY event_id", args):
        record = {k: r[k] for k in r.keys()}
        record["row"] = json.loads(r["row"])
        out.append(record)
    return out
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/eval/test_bundle_learning.py -v`
Expected: PASS — 7 passed

- [ ] **Step 5: Commit**

```bash
git add src/eval_harness/bundle.py tests/eval/test_bundle_learning.py
git commit -m "feat(P2): bundle carries P1's scoped learning records so a missing negative is not a regression"
```

---

### Task 8: Accepted groups and `bundle_expectation[]` (Done-means 12)

**Files:**
- Modify: `src/eval_harness/bundle.py` — add the two tables and their writers/readers
- Test: `tests/eval/test_bundle_expectation.py`

**Interfaces:**
- Consumes: `_require_open`, `canonical_json`; `DIMENSIONS`, `EXPECTED_OUTCOME_KINDS`, `EXPECTATION_SOURCES`, `check_dimension` (Task 2).
- Produces: `add_accepted_group(conn, bundle_id, *, group_id, acceptance_row) -> None`, `accepted_groups(conn, bundle_id) -> list[dict]`, `add_expectation(conn, bundle_id, *, dimension, subject_ref, expected_value, expected_outcome_kind, source) -> None`, `expectations(conn, bundle_id, *, dimension=None) -> list[dict]`, `expectation_for(conn, bundle_id, dimension, subject_ref) -> dict | None`.

**Accepted groups are resolved *as of* the pinned plan version, and the resolution is P9's.** SPEC Contract out §3: *"accepted groups as of the pinned plan version — resolved through P9's per-version `group_acceptance` record, since the group and membership records themselves are shared across plan versions."* P9 does not exist, so the caller hands over the already-resolved row and P2 stores it verbatim. **P2 does not resolve acceptance itself** — doing so would require reading P9's `Group.state`, `group_acceptance` and membership tables and re-deriving §8.8's per-version projection, which is P9's published surface, not P2's inference.

**`expected_value` is opaque and P2 validates no member of it.** For `fact` it is field + value + reliability state (§3.13, P6's vocabulary); for `placement` a node id, a shallow-fallback node id, or abstain (§6.7, §6.10, P11's); for `residual` P11's published `outcome` plus its qualifier. SPEC Contract out §3 is explicit: *"The `residual` expectation is P11's published `outcome` vocabulary, not a P2 vocabulary."* Copying P11's eight-action table into P2's source would be exactly the two-vocabularies failure MINOR 7 forbids. The consequence is stated plainly: **a typo in an expected `outcome` is not caught here.** When P11 lands, import its vocabulary and validate against the imported names.

**Done-means 12 is a round-trip test, not a validation test.** §7.8's worked example — the screenshot reading *"Your Columbia University application has been submitted"* — must be *representable* as `return_to_placement` with `return_target.kind = confirmed_domain_group`, and a run in which the file lands in a generic residual folder must come out `divergent` rather than a match. Representability is asserted here; the `divergent` half is asserted in Task 10, where the verdict function exists.

**P2 fills no expectation.** SPEC *Deferred*: *"§8.5 requires a bundle to carry 'expected facts' and 'expected placement or abstention outcomes' but does not author them. The corpus selection, the labelling, and the per-subject expected values are hand work. P2 publishes `bundle_expectation`; it does not fill it."* No expected value appears anywhere in `src/eval_harness/`; Task 16 asserts it.

**`source` distinguishes a label from a captured decision.** `hand-labelled` and `captured-from-accepted-user-decision` are the SPEC's two. The second is how §8.7 correction records become expectations — and **scope discipline applies**: a file-scoped correction becomes an expectation *for that file only*. P2 must not generalise it into a dimension-wide expectation (§8.7: one transcript in a Columbia packet *"should not teach the engine that all transcripts belong there"*). `add_expectation` takes one `subject_ref` and there is no bulk-apply path.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_bundle_expectation.py
import pytest

from eval_harness.bundle import (
    accepted_groups, add_accepted_group, add_expectation, expectation_for,
    expectations, open_bundle, seal_bundle,
)
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import DIMENSIONS, UnknownDimension


def _bundle(conn):
    return open_bundle(conn, corpus_form="snapshot", source_scan_ref="scan-fixture",
                       pinned_plan_id="plan-fixture", pinned_plan_version="1",
                       policy_settings={})


def test_an_accepted_group_is_stored_as_p9_resolved_it(eval_conn):
    # P9 owns the per-version resolution; P2 stores the row it is handed.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    row = {"group_id": "g-columbia", "plan_version": "1", "review_state": "accepted",
           "members": ["file-1", "file-2"]}
    add_accepted_group(eval_conn, bundle_id, group_id="g-columbia", acceptance_row=row)
    assert accepted_groups(eval_conn, bundle_id) == [row]


def test_every_dimension_can_carry_an_expectation(eval_conn):
    # Done-means 2: all ten have a distinct assertion record; none is collapsed.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    for dimension in DIMENSIONS:
        add_expectation(eval_conn, bundle_id, dimension=dimension,
                        subject_ref=f"subject-{dimension}",
                        expected_value={"fixture": dimension},
                        expected_outcome_kind="produced", source="hand-labelled")
    assert len({r["dimension"] for r in expectations(eval_conn, bundle_id)}) == 10


def test_a_dimension_outside_the_ten_is_rejected(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    with pytest.raises(UnknownDimension):
        add_expectation(eval_conn, bundle_id, dimension="candidate_node_retrieval",
                        subject_ref="x", expected_value={},
                        expected_outcome_kind="produced", source="hand-labelled")


def test_the_columbia_screenshot_is_representable(eval_conn):
    # Done-means 12 / §7.8's worked example: the correct outcome is retrieval of
    # the accepted Columbia application group and a RETURN TO PLACEMENT, not a
    # residual destination. The vocabulary is P11's; P2 stores it, validates none.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    add_expectation(
        eval_conn, bundle_id, dimension="residual", subject_ref="file-screenshot",
        expected_value={"outcome": "return_to_placement",
                        "return_target": {"kind": "confirmed_domain_group",
                                          "id": "g-columbia"}},
        expected_outcome_kind="produced", source="hand-labelled",
    )
    stored = expectation_for(eval_conn, bundle_id, "residual", "file-screenshot")
    assert stored["expected_value"]["outcome"] == "return_to_placement"
    assert stored["expected_value"]["return_target"]["kind"] == "confirmed_domain_group"


def test_all_eight_of_7_7s_actions_are_representable(eval_conn):
    # Done-means 12: "Dimension 10 can express all eight of §7.7's actions."
    # These strings are P11's published vocabulary, quoted in a test fixture, not
    # declared as a P2 enum in src/.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    eight = [
        {"outcome": "return_to_placement",
         "return_target": {"kind": "confirmed_domain_group"}},
        {"outcome": "return_to_placement",
         "return_target": {"kind": "accepted_graph_or_purpose_packet"}},
        {"outcome": "place", "destination": {"node_role": "residual"}},
        {"outcome": "place", "destination": {"node_role": "ordinary"},
         "decision_depth": {"unsupported_levels": ["term"]}},
        {"outcome": "mark_review_later"},
        {"outcome": "leave_in_place"},
        {"outcome": "mark_state", "marked_state": "protected"},
        {"outcome": "abstain", "abstention_reason": "no_supported_destination"},
    ]
    for i, value in enumerate(eight):
        add_expectation(eval_conn, bundle_id, dimension="residual",
                        subject_ref=f"file-{i}", expected_value=value,
                        expected_outcome_kind=(
                            "abstained" if value["outcome"] == "abstain" else "produced"),
                        source="hand-labelled")
    stored = expectations(eval_conn, bundle_id, dimension="residual")
    assert len(stored) == 8
    assert {r["expected_value"]["outcome"] for r in stored} == {
        "return_to_placement", "place", "mark_review_later", "leave_in_place",
        "mark_state", "abstain"}


def test_an_abstention_is_an_expectable_outcome(eval_conn):
    # §6.10: correct abstention is a successful outcome, so it must be expressible
    # as an EXPECTATION, not only as an observation.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    add_expectation(eval_conn, bundle_id, dimension="fact",
                    subject_ref="file-1::field-a", expected_value=None,
                    expected_outcome_kind="abstained", source="hand-labelled")
    assert expectation_for(eval_conn, bundle_id, "fact",
                           "file-1::field-a")["expected_outcome_kind"] == "abstained"


def test_expected_outcome_kind_and_source_are_closed(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    with pytest.raises(ValueError):
        add_expectation(eval_conn, bundle_id, dimension="fact", subject_ref="x",
                        expected_value={}, expected_outcome_kind="maybe",
                        source="hand-labelled")
    with pytest.raises(ValueError):
        add_expectation(eval_conn, bundle_id, dimension="fact", subject_ref="y",
                        expected_value={}, expected_outcome_kind="produced",
                        source="guessed")


def test_there_is_no_bulk_apply_path(eval_conn):
    # §8.7 scope discipline: a file-scoped correction is an expectation for that
    # file only. P2 must not generalise one into a dimension-wide expectation.
    import inspect

    from eval_harness import bundle as bundle_module
    for name, fn in inspect.getmembers(bundle_module, inspect.isfunction):
        if "expectation" in name:
            params = inspect.signature(fn).parameters
            assert "subject_refs" not in params, name
            assert "apply_to_all" not in params, name


def test_a_sealed_bundle_takes_no_further_expectation(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    seal_bundle(eval_conn, bundle_id)
    from eval_harness.bundle import BundleSealed
    with pytest.raises(BundleSealed):
        add_expectation(eval_conn, bundle_id, dimension="fact", subject_ref="x",
                        expected_value={}, expected_outcome_kind="produced",
                        source="hand-labelled")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/eval/test_bundle_expectation.py -v`
Expected: FAIL with `ImportError: cannot import name 'add_expectation' from 'eval_harness.bundle'`

- [ ] **Step 3: Extend bundle.py**

Append to `BUNDLE_DDL`:

```sql
CREATE TABLE IF NOT EXISTS bundle_accepted_group (
    bundle_id TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    group_id  TEXT NOT NULL,
    row       TEXT NOT NULL,   -- P9's group_acceptance row, resolved by P9, verbatim
    PRIMARY KEY (bundle_id, group_id)
);
CREATE TABLE IF NOT EXISTS bundle_expectation (
    bundle_id             TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    dimension             TEXT NOT NULL,
    subject_ref           TEXT NOT NULL,
    expected_value        TEXT,           -- canonical JSON; opaque, another part's vocabulary
    expected_outcome_kind TEXT NOT NULL,
    source                TEXT NOT NULL,
    PRIMARY KEY (bundle_id, dimension, subject_ref)
);
```

and the same three seal triggers, one per new table, copied from `bundle_file_entry`'s (INSERT, UPDATE, DELETE, each `WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = NEW.bundle_id) IS NOT NULL` — use `OLD` for UPDATE and DELETE). Write them out in full; do not factor them into a loop, because SQLite has no parameterized trigger and a partially-written set would leave one table mutable after sealing.

Append to `bundle.py`:

```python
def add_accepted_group(conn: sqlite3.Connection, bundle_id: str, *, group_id: str,
                       acceptance_row: dict) -> None:
    """One accepted group, AS OF the bundle's pinned plan version.

    The per-version resolution is P9's `group_acceptance` (§8.8) and the caller
    hands over the already-resolved row. P2 does not re-derive acceptance from
    membership records: that projection is P9's published surface.
    """
    _require_open(conn, bundle_id)
    conn.execute(
        "INSERT INTO bundle_accepted_group (bundle_id, group_id, row) VALUES (?, ?, ?)",
        (bundle_id, group_id, canonical_json(acceptance_row)),
    )


def accepted_groups(conn: sqlite3.Connection, bundle_id: str) -> list[dict]:
    import json
    return [json.loads(r["row"]) for r in conn.execute(
        "SELECT row FROM bundle_accepted_group WHERE bundle_id = ? ORDER BY group_id",
        (bundle_id,))]


def add_expectation(conn: sqlite3.Connection, bundle_id: str, *, dimension: str,
                    subject_ref: str, expected_value, expected_outcome_kind: str,
                    source: str) -> None:
    """The expected side of one assertion, for one subject.

    `expected_value` is opaque: for `fact` it is P6's field/value/reliability
    state, for `placement` and `residual` it is P11's published vocabulary. P2
    validates no member of it — see the module docstring.

    One subject per call, with no bulk path: §8.7's scope discipline means a
    file-scoped correction is an expectation for that file and no other.
    """
    from eval_harness.vocabulary import (
        EXPECTATION_SOURCES, EXPECTED_OUTCOME_KINDS, check_dimension,
    )
    _require_open(conn, bundle_id)
    check_dimension(dimension)
    if expected_outcome_kind not in EXPECTED_OUTCOME_KINDS:
        raise ValueError(f"expected_outcome_kind {expected_outcome_kind!r} is not "
                         f"one of {EXPECTED_OUTCOME_KINDS}")
    if source not in EXPECTATION_SOURCES:
        raise ValueError(f"source {source!r} is not one of {EXPECTATION_SOURCES}")
    conn.execute(
        "INSERT INTO bundle_expectation (bundle_id, dimension, subject_ref, "
        "expected_value, expected_outcome_kind, source) VALUES (?, ?, ?, ?, ?, ?)",
        (bundle_id, dimension, subject_ref,
         None if expected_value is None else canonical_json(expected_value),
         expected_outcome_kind, source),
    )


def _expectation_row(row: sqlite3.Row) -> dict:
    import json
    record = {k: row[k] for k in row.keys()}
    record["expected_value"] = (None if row["expected_value"] is None
                                else json.loads(row["expected_value"]))
    return record


def expectations(conn: sqlite3.Connection, bundle_id: str, *,
                 dimension: str | None = None) -> list[dict]:
    if dimension is None:
        rows = conn.execute(
            "SELECT * FROM bundle_expectation WHERE bundle_id = ? "
            "ORDER BY dimension, subject_ref", (bundle_id,))
    else:
        rows = conn.execute(
            "SELECT * FROM bundle_expectation WHERE bundle_id = ? AND dimension = ? "
            "ORDER BY subject_ref", (bundle_id, dimension))
    return [_expectation_row(r) for r in rows]


def expectation_for(conn: sqlite3.Connection, bundle_id: str, dimension: str,
                    subject_ref: str) -> dict | None:
    row = conn.execute(
        "SELECT * FROM bundle_expectation WHERE bundle_id = ? AND dimension = ? "
        "AND subject_ref = ?", (bundle_id, dimension, subject_ref)).fetchone()
    return None if row is None else _expectation_row(row)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/eval/test_bundle_expectation.py -v`
Expected: PASS — 9 passed

- [ ] **Step 5: Commit**

```bash
git add src/eval_harness/bundle.py tests/eval/test_bundle_expectation.py
git commit -m "feat(P2): accepted groups and expectations, opaque values, all eight residual actions representable"
```

---

### Task 9: The stage adapters and the replay runner (Done-means 7)

**Files:**
- Create: `src/eval_harness/replay.py`
- Test: `tests/eval/test_replay.py`

**Interfaces:**
- Consumes: `bundle` readers (Tasks 5–8); `record_version_tuple`, `start_run`, `finish_run` (Task 3); `record_stage_output`, `DimensionValue` (Task 4); `STAGE_IDS` (Task 2).
- Produces: `ReplayContext` (frozen dataclass: `conn`, `run_id`, `bundle_id`, `stage_id`, `run_settings`, `budget_ceilings`), `StageResult` (frozen dataclass: `outcome`, `payload`, `inputs`, `budget_state`, `subject_ref`, `values`), `replay_bundle(conn, bundle_id, *, version_tuple, budget_ceilings, run_settings, adapters, run_kind="replay") -> str`, `NO_ADAPTER: object`.

**Adapters are passed in, never registered in a module-level dict.** P1's plan records what goes wrong with a process-local mutable registry: *"a type existed only in the process that added it, appends started failing after a restart, and a direct write to the dict bypassed the reserved-name check entirely."* The same trap is available here and is avoided the same way — `replay_bundle` takes `adapters` as an argument, and there is no `register_stage` function anywhere in P2. A run's stage set is therefore visible in the call that started it.

**A stage with no adapter is `not_implemented`, and the run completes.** `02-segmentation-map.md`, *Order*: the harness must be runnable before the stages exist. All ten stages appear in every run, in §8.5's order; nine of them reporting `not_implemented` is a valid run.

**Each adapter returns zero or more subjects' results.** A stage decides about many subjects — many files, many groups — so an adapter returns a list of `StageResult`, each with its own `subject_ref`. An adapter that returns an empty list still gets one `not_implemented`-free record: `outcome = produced` with no dimension values would be a lie about a stage that ran and decided nothing, so an adapter returning `[]` is recorded as `abstained` for the bundle as a whole with `subject_ref = bundle_id`. **This is P2's own bookkeeping for its own runner and is not a claim about any stage's semantics** — a real stage that abstains says so per subject.

**Budget ceilings reach the adapter and are enforced by nobody here.** SPEC Cross-cutting answers → Budgets: a replay run *"executes real stages and is therefore bound by the same §8.6 ceilings as a live run"*. The ceilings are handed to the adapter through `ReplayContext`; the stage that owns the ceiling enforces it and reports `deferred` / `ceiling_reached`. P2 enforces no ceiling and substitutes no cheaper approximation.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_replay.py
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.replay import ReplayContext, StageResult, replay_bundle
from eval_harness.run import get_run, run_settings
from eval_harness.stage_output import DimensionValue, dimension_values, stage_outputs
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import STAGE_IDS


def _tuple():
    return dict(extractor_versions={"pdf.native": "1.0.0"},
                graph_algorithm_version=None, prompt_fingerprint=None,
                model_identifier=None, template_library_version=None,
                placement_scorer_version=None,
                analysis_tiers_enabled=["filesystem", "native"])


def _bundle(conn):
    bundle_id = open_bundle(conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    add_expectation(conn, bundle_id, dimension="extraction",
                    subject_ref="sha256:syl", expected_value={"text": "COMS 4995"},
                    expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(conn, bundle_id)
    return bundle_id


def _extraction_adapter(ctx: ReplayContext) -> list[StageResult]:
    """Stands in for P5, which does not exist. It reads the bundle, not the disk."""
    return [StageResult(
        subject_ref="sha256:syl", outcome="produced",
        payload='{"p5": "opaque"}', inputs=[], budget_state="within_ceiling",
        values=[DimensionValue("extraction", "sha256:syl", "produced",
                               {"text": "COMS 4995"})],
    )]


def _settings(**overrides):
    s = {"model_enabled": False, "embeddings_enabled": False}
    s.update(overrides)
    return s


def test_a_run_with_no_adapters_completes_with_ten_not_implemented_stages(eval_conn):
    # Done-means 7 / 02-segmentation-map.md, Order.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={})
    rows = stage_outputs(eval_conn, run_id)
    assert [r["stage_id"] for r in rows] == list(STAGE_IDS)
    assert {r["outcome"] for r in rows} == {"not_implemented"}
    assert get_run(eval_conn, run_id)["finished_at"]


def test_one_adapter_runs_and_the_other_nine_report_not_implemented(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"extraction": _extraction_adapter})
    by_stage = {r["stage_id"]: r["outcome"] for r in stage_outputs(eval_conn, run_id)}
    assert by_stage["extraction"] == "produced"
    assert sum(1 for v in by_stage.values() if v == "not_implemented") == 9
    value = dimension_values(eval_conn, run_id, dimension="extraction")[0]
    assert value["value"] == '{"text":"COMS 4995"}'


def test_stages_run_in_8_5s_order(eval_conn):
    # The order is §8.5's list, which is also §4.10's and §6.12's pipeline order,
    # and Task 11 depends on it for tie-breaking.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    seen = []

    def spy(stage_id):
        def adapter(ctx: ReplayContext) -> list[StageResult]:
            seen.append(ctx.stage_id)
            return []
        return adapter

    replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(), budget_ceilings={},
                  run_settings=_settings(),
                  adapters={s: spy(s) for s in STAGE_IDS})
    assert seen == list(STAGE_IDS)


def test_the_adapter_receives_the_run_settings_and_the_ceilings(eval_conn):
    # A bundle must be re-runnable with the model disabled and with embeddings
    # disabled, independently (Contract out §5).
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    captured = {}

    def adapter(ctx: ReplayContext) -> list[StageResult]:
        captured["settings"] = dict(ctx.run_settings)
        captured["ceilings"] = dict(ctx.budget_ceilings)
        captured["bundle_id"] = ctx.bundle_id
        return []

    replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                  budget_ceilings={"ocr.max_pages_per_file": 3},
                  run_settings=_settings(embeddings_enabled=True),
                  adapters={"retrieval": adapter})
    assert captured["settings"] == {"model_enabled": False, "embeddings_enabled": True}
    assert captured["ceilings"] == {"ocr.max_pages_per_file": 3}
    assert captured["bundle_id"] == bundle_id


def test_an_adapter_that_defers_is_recorded_as_deferred(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)

    def deferring(ctx: ReplayContext) -> list[StageResult]:
        return [StageResult(subject_ref="sha256:syl", outcome="deferred",
                            payload=None, inputs=[],
                            budget_state="ceiling_reached",
                            values=[DimensionValue("extraction", "sha256:syl",
                                                   "deferred", None)])]

    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"extraction": deferring})
    row = [r for r in stage_outputs(eval_conn, run_id)
           if r["stage_id"] == "extraction"][0]
    assert row["outcome"] == "deferred"
    assert row["budget_state"] == "ceiling_reached"


def test_an_adapter_that_raises_is_recorded_as_error_not_swallowed(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)

    def broken(ctx: ReplayContext) -> list[StageResult]:
        raise RuntimeError("the stage crashed")

    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"grouping": broken})
    row = [r for r in stage_outputs(eval_conn, run_id)
           if r["stage_id"] == "grouping"][0]
    assert row["outcome"] == "error"
    assert "the stage crashed" in row["payload"]


def test_there_is_no_global_stage_registry(eval_conn):
    # P1's lesson: a process-local mutable registry makes a run's stage set
    # invisible and mutable from anywhere. Adapters are an argument.
    import inspect

    from eval_harness import replay
    assert not [n for n, v in vars(replay).items()
                if callable(v) and n.lower().startswith("register")]
    assert "adapters" in inspect.signature(replay.replay_bundle).parameters


def test_the_run_records_its_settings_verbatim(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={})
    assert run_settings(eval_conn, run_id) == {"model_enabled": False,
                                               "embeddings_enabled": False}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/eval/test_replay.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_harness.replay'`

- [ ] **Step 3: Write the implementation**

```python
# src/eval_harness/replay.py
"""The replay runner.

Every run walks all ten §8.5 stages in §8.5's order. A stage with no adapter
reports `not_implemented`, which is what makes the harness runnable while nine of
the ten measured stages are still absent (02-segmentation-map.md, Order).

Adapters are an ARGUMENT, never a module-level registry: a run's stage set must be
visible in the call that started it and must not be mutable from elsewhere.
"""
from __future__ import annotations

import sqlite3
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from eval_harness.run import finish_run, record_version_tuple, start_run
from eval_harness.stage_output import DimensionValue, record_stage_output
from eval_harness.vocabulary import STAGE_IDS


@dataclass(frozen=True)
class ReplayContext:
    """What an adapter is given. It reads the bundle; it never reads the disk."""
    conn: sqlite3.Connection
    run_id: str
    bundle_id: str
    stage_id: str
    run_settings: Mapping[str, bool]
    budget_ceilings: Mapping[str, int]


@dataclass(frozen=True)
class StageResult:
    """One subject's outcome from one stage. `payload` stays the stage's own."""
    subject_ref: str
    outcome: str
    payload: str | None
    inputs: Sequence[str]
    budget_state: str
    values: Sequence[DimensionValue] = field(default_factory=tuple)


StageAdapter = Callable[[ReplayContext], Sequence[StageResult]]


def replay_bundle(conn: sqlite3.Connection, bundle_id: str, *,
                  version_tuple: dict, budget_ceilings: Mapping[str, int],
                  run_settings: Mapping[str, bool],
                  adapters: Mapping[str, StageAdapter],
                  run_kind: str = "replay") -> str:
    """Replay one bundle through whatever stages exist. Returns the run_id.

    No live filesystem is touched: adapters read the bundle through `ctx.conn`.
    P2 enforces no §8.6 ceiling — it hands the set to the stage that owns it and
    records what the stage reports.
    """
    from eval_harness.bundle import get_bundle

    manifest = get_bundle(conn, bundle_id)
    if manifest is None:
        raise KeyError(f"no bundle {bundle_id!r}")
    version_tuple_ref = record_version_tuple(conn, **version_tuple)
    run_id = start_run(
        conn, bundle_id=bundle_id, run_kind=run_kind,
        version_tuple_ref=version_tuple_ref, budget_ceilings=dict(budget_ceilings),
        run_settings=dict(run_settings),
        pinned_plan_id=manifest["pinned_plan_id"],
        pinned_plan_version=manifest["pinned_plan_version"],
    )
    for stage_id in STAGE_IDS:
        adapter = adapters.get(stage_id)
        if adapter is None:
            record_stage_output(
                conn, run_id=run_id, stage_id=stage_id, subject_ref=bundle_id,
                outcome="not_implemented", payload=None,
                version_tuple_ref=version_tuple_ref, inputs=[],
                budget_state="within_ceiling",
            )
            continue
        ctx = ReplayContext(conn=conn, run_id=run_id, bundle_id=bundle_id,
                            stage_id=stage_id, run_settings=dict(run_settings),
                            budget_ceilings=dict(budget_ceilings))
        try:
            results = list(adapter(ctx))
        except Exception:
            # A crash is `error`, which is distinct from an abstention and from a
            # deferral. It is never silently swallowed and never scored as either.
            record_stage_output(
                conn, run_id=run_id, stage_id=stage_id, subject_ref=bundle_id,
                outcome="error", payload=traceback.format_exc(),
                version_tuple_ref=version_tuple_ref, inputs=[],
                budget_state="within_ceiling",
            )
            continue
        if not results:
            # P2's own bookkeeping for a stage that ran and returned nothing. It
            # is not a claim about any stage's semantics: a real stage that
            # abstains reports `abstained` per subject.
            record_stage_output(
                conn, run_id=run_id, stage_id=stage_id, subject_ref=bundle_id,
                outcome="abstained", payload=None,
                version_tuple_ref=version_tuple_ref, inputs=[],
                budget_state="within_ceiling",
            )
            continue
        for result in results:
            record_stage_output(
                conn, run_id=run_id, stage_id=stage_id,
                subject_ref=result.subject_ref, outcome=result.outcome,
                payload=result.payload, version_tuple_ref=version_tuple_ref,
                inputs=result.inputs, budget_state=result.budget_state,
                dimension_values=result.values,
            )
    finish_run(conn, run_id)
    return run_id
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/eval/test_replay.py -v`
Expected: PASS — 8 passed

- [ ] **Step 5: Commit**

```bash
git add src/eval_harness/replay.py tests/eval/test_replay.py
git commit -m "feat(P2): replay runner, ten stages every run, missing stage is not_implemented"
```

---

### Task 10: The per-stage assertion record and its seven verdicts (Done-means 2, 5, 6)

**Files:**
- Create: `src/eval_harness/assertions.py`
- Modify: `src/eval_harness/store.py` — add `assertions.ASSERTION_DDL` to `_ddl_scripts`
- Test: `tests/eval/test_assertions.py`

**Interfaces:**
- Consumes: `expectations` (Task 8); `dimension_values` (Task 4); `VERDICTS`, `DIMENSIONS` (Task 2); `canonical_json` (Task 1).
- Produces: `verdict_for(*, expected_outcome_kind, expected_value, observed_outcome, observed_value) -> tuple[str | None, str | None]`, `assert_run(conn, run_id) -> int`, `assertions(conn, run_id, *, dimension=None) -> list[sqlite3.Row]`, `verdict_counts(conn, run_id) -> dict[str, int]`, `PASSING_VERDICTS: frozenset[str]`.

**The verdict table, in full.** Every row traces to a design sentence.

| observed `outcome` | `expected_outcome_kind` | verdict | why |
|---|---|---|---|
| `not_implemented` | any | `not_run` | the stage does not exist (`02-segmentation-map.md`, *Order*) |
| `deferred` | any | `deferred` | §8.6 — a budget event, never a quality failure |
| `abstained` | `abstained` | `abstained_correctly` | §6.10 *"correct abstention is a successful outcome"* — a **pass** |
| `abstained` | `produced` | `abstained_incorrectly` | evidence was present and the stage abstained |
| `produced` | `abstained` | `asserted_incorrectly` | the stage produced where it should have abstained |
| `produced` | `produced`, values equal | `match` | exact equality over canonical JSON |
| `produced` | `produced`, values differ | `divergent` | |
| any | `not-applicable` | **no verdict** | see below |
| `error` | any | **no verdict** | see below |
| *no dimension value recorded* | any | `not_run` | the stage that would have produced it did not |

**Two cases get no verdict, and P2 mints no eighth verdict name for them.**

- **`outcome = error`.** SPEC Contract out §6 publishes seven verdicts and none of them means *the stage crashed*. Scoring it `divergent` would call a crash a quality regression; scoring it `not_run` would hide a crash inside "the stage does not exist". The assertion is therefore written with `verdict = NULL` and `no_verdict_reason = 'stage_error'`, it is counted in neither the passing nor the failing bucket, and `verdict_counts` reports it under `unverdicted`. This is the same move P1 made for `file_path_history.volume_id`: a `NULL` reads as *unknown*, a fabricated value reads as an answer. **A recommended SPEC change is recorded in the report and is not made here.**
- **`expected_outcome_kind = 'not-applicable'`.** The record exists to say the dimension cannot be asserted on this subject. Neither pass nor fail applies, and §8.5 defines no verdict for it. `verdict = NULL`, `no_verdict_reason = 'expectation_not_applicable'`.

**`abstained_correctly` is a pass and is reported as one.** `PASSING_VERDICTS = {match, abstained_correctly}`. Done-means 5 turns on this and so does §6.10.

**`deferred` never becomes `divergent`, for any dimension.** Done-means 6's second half — *"a run whose only change is a lower budget ceiling produces zero new divergences"* — is asserted in Task 12, where two runs exist to compare; the per-verdict half is asserted here.

**No thresholds, and the comparison is exact.** SPEC Open question 2 is open: §8.5 states no pass threshold, target rate, or regression tolerance, and §6.10's two-condition rule is a *placement* rule that must not be borrowed as one. `verdict_for` takes no tolerance argument, and there is none to add without answering OQ2.

**`evidence_ref` is a P4 `observation_key`, never an `observation_id`.** §8.7 requires a negative example recorded today to still resolve after an extractor upgrade, and an upgraded extractor emits a new row with a new `observation_id`. `assert_run` copies whatever `evidence_ref` the dimension value carried and the writer refuses a value whose shape is an observation *id*; the test below pins the rule.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_assertions.py
import pytest

from eval_harness.assertions import (
    PASSING_VERDICTS, assert_run, assertions, verdict_counts, verdict_for,
)
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.replay import ReplayContext, StageResult, replay_bundle
from eval_harness.stage_output import DimensionValue
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import DIMENSIONS, VERDICTS


def _tuple():
    return dict(extractor_versions={}, graph_algorithm_version=None,
                prompt_fingerprint=None, model_identifier=None,
                template_library_version=None, placement_scorer_version=None,
                analysis_tiers_enabled=["filesystem"])


def _settings():
    return {"model_enabled": False, "embeddings_enabled": False}


def _v(expected_kind, expected, observed_outcome, observed):
    return verdict_for(expected_outcome_kind=expected_kind, expected_value=expected,
                       observed_outcome=observed_outcome, observed_value=observed)


def test_a_matching_produced_value_is_a_match():
    assert _v("produced", {"a": 1}, "produced", {"a": 1}) == ("match", None)


def test_key_order_does_not_make_a_divergence():
    assert _v("produced", {"a": 1, "b": 2}, "produced", {"b": 2, "a": 1})[0] == "match"


def test_a_different_produced_value_is_divergent():
    assert _v("produced", {"a": 1}, "produced", {"a": 2}) == ("divergent", None)


def test_correct_abstention_is_a_passing_verdict():
    # §6.10: "correct abstention is a successful outcome."
    assert _v("abstained", None, "abstained", None) == ("abstained_correctly", None)
    assert "abstained_correctly" in PASSING_VERDICTS
    assert PASSING_VERDICTS == frozenset({"match", "abstained_correctly"})


def test_the_two_wrong_abstention_directions_are_distinct():
    assert _v("produced", {"a": 1}, "abstained", None)[0] == "abstained_incorrectly"
    assert _v("abstained", None, "produced", {"a": 1})[0] == "asserted_incorrectly"


def test_a_deferral_is_deferred_for_every_expectation_kind():
    # §8.6: cost exhaustion must never turn into a quality judgement.
    for kind in ("produced", "abstained"):
        assert _v(kind, {"a": 1}, "deferred", None) == ("deferred", None)


def test_not_implemented_is_not_run():
    assert _v("produced", {"a": 1}, "not_implemented", None) == ("not_run", None)


def test_a_stage_error_gets_no_verdict_and_p2_mints_no_eighth_name():
    verdict, reason = _v("produced", {"a": 1}, "error", None)
    assert verdict is None
    assert reason == "stage_error"
    assert len(VERDICTS) == 7


def test_a_not_applicable_expectation_gets_no_verdict():
    verdict, reason = _v("not-applicable", None, "produced", {"a": 1})
    assert verdict is None
    assert reason == "expectation_not_applicable"


def test_verdict_for_takes_no_tolerance_argument():
    # SPEC Open question 2 is OPEN: §8.5 states no threshold and §6.10's
    # two-condition rule is a placement rule, not an eval threshold.
    import inspect
    params = set(inspect.signature(verdict_for).parameters)
    assert params == {"expected_outcome_kind", "expected_value",
                      "observed_outcome", "observed_value"}


def _run_with(eval_conn, *, expectation, adapter):
    create_eval_schema(eval_conn)
    bundle_id = open_bundle(eval_conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    add_expectation(eval_conn, bundle_id, **expectation)
    seal_bundle(eval_conn, bundle_id)
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters=adapter)
    return bundle_id, run_id


def test_assert_run_writes_one_assertion_per_expectation(eval_conn):
    def adapter(ctx: ReplayContext):
        return [StageResult(subject_ref="sha256:syl", outcome="produced",
                            payload=None, inputs=[], budget_state="within_ceiling",
                            values=[DimensionValue("extraction", "sha256:syl",
                                                   "produced", {"text": "COMS 4995"})])]

    _, run_id = _run_with(
        eval_conn,
        expectation=dict(dimension="extraction", subject_ref="sha256:syl",
                         expected_value={"text": "COMS 4995"},
                         expected_outcome_kind="produced", source="hand-labelled"),
        adapter={"extraction": adapter})
    assert assert_run(eval_conn, run_id) == 1
    row = assertions(eval_conn, run_id)[0]
    assert row["dimension"] == "extraction"
    assert row["verdict"] == "match"
    assert row["expected"] == '{"text":"COMS 4995"}'
    assert row["observed"] == '{"text":"COMS 4995"}'


def test_an_expectation_no_stage_answered_is_not_run(eval_conn):
    # Done-means 7: nine absent stages yield not_run verdicts, not failures.
    _, run_id = _run_with(
        eval_conn,
        expectation=dict(dimension="placement", subject_ref="file-1",
                         expected_value={"node_id": "n1"},
                         expected_outcome_kind="produced", source="hand-labelled"),
        adapter={})
    assert_run(eval_conn, run_id)
    assert assertions(eval_conn, run_id)[0]["verdict"] == "not_run"


def test_the_columbia_screenshot_in_a_residual_folder_is_divergent(eval_conn):
    # Done-means 12's second half (§7.8, §7.9): landing in a generic residual
    # folder instead of returning to placement is divergent, not a match.
    def adapter(ctx: ReplayContext):
        return [StageResult(
            subject_ref="file-screenshot", outcome="produced", payload=None,
            inputs=[], budget_state="within_ceiling",
            values=[DimensionValue("residual", "file-screenshot", "produced",
                                   {"outcome": "place",
                                    "destination": {"node_role": "residual"}})])]

    _, run_id = _run_with(
        eval_conn,
        expectation=dict(dimension="residual", subject_ref="file-screenshot",
                         expected_value={"outcome": "return_to_placement",
                                         "return_target": {"kind": "confirmed_domain_group",
                                                           "id": "g-columbia"}},
                         expected_outcome_kind="produced", source="hand-labelled"),
        adapter={"placement_scoring": adapter})
    assert_run(eval_conn, run_id)
    assert assertions(eval_conn, run_id)[0]["verdict"] == "divergent"


def test_verdict_counts_separates_passes_deferrals_and_unverdicted(eval_conn):
    def adapter(ctx: ReplayContext):
        return [StageResult(subject_ref="s", outcome="deferred", payload=None,
                            inputs=[], budget_state="ceiling_reached",
                            values=[DimensionValue("extraction", "sha256:syl",
                                                   "deferred", None)])]

    _, run_id = _run_with(
        eval_conn,
        expectation=dict(dimension="extraction", subject_ref="sha256:syl",
                         expected_value={"text": "x"},
                         expected_outcome_kind="produced", source="hand-labelled"),
        adapter={"extraction": adapter})
    assert_run(eval_conn, run_id)
    counts = verdict_counts(eval_conn, run_id)
    assert counts["deferred"] == 1
    assert counts.get("divergent", 0) == 0
    assert set(counts) <= set(VERDICTS) | {"unverdicted"}


def test_every_dimension_has_its_own_assertion_record(eval_conn):
    # Done-means 2: none is collapsed into another.
    create_eval_schema(eval_conn)
    bundle_id = open_bundle(eval_conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    for dimension in DIMENSIONS:
        add_expectation(eval_conn, bundle_id, dimension=dimension,
                        subject_ref=f"s-{dimension}", expected_value={"d": dimension},
                        expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(eval_conn, bundle_id)
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={})
    assert assert_run(eval_conn, run_id) == 10
    assert {r["dimension"] for r in assertions(eval_conn, run_id)} == set(DIMENSIONS)


def test_an_evidence_ref_that_looks_like_an_observation_id_is_refused(eval_conn):
    # §8.7 / SPEC Cross-cutting answers: a bundle expectation cited by
    # observation_id would decay silently across exactly the version change §8.5
    # exists to measure.
    from eval_harness.assertions import ObservationIdRefused, write_assertion
    create_eval_schema(eval_conn)
    with pytest.raises(ObservationIdRefused):
        write_assertion(eval_conn, run_id="r1", dimension="extraction",
                        subject_ref="s", expected=None, observed=None,
                        verdict="not_run", no_verdict_reason=None,
                        evidence_ref="observation_id:12345")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/eval/test_assertions.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_harness.assertions'`

- [ ] **Step 3: Write the implementation**

```python
# src/eval_harness/assertions.py
"""Contract out §6 — the per-stage assertion record.

Seven verdicts, and P2 mints no eighth. Two cases §8.5 does not define a verdict
for — a stage `error`, and an expectation whose kind is `not-applicable` — are
written with a NULL verdict and a named reason: a NULL reads as "no verdict is
defined for this", a fabricated verdict reads as an answer.

There is no threshold and no tolerance anywhere in this module. §8.5 states none,
and SPEC Open question 2 is open.
"""
from __future__ import annotations

import json
import sqlite3

from eval_harness.store import canonical_json
from eval_harness.vocabulary import VERDICTS, check_dimension

#: Done-means 5 — `abstained_correctly` is reported as a pass, not as a miss (§6.10).
PASSING_VERDICTS: frozenset[str] = frozenset({"match", "abstained_correctly"})

ASSERTION_DDL = """
CREATE TABLE IF NOT EXISTS assertion (
    assertion_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id            TEXT NOT NULL REFERENCES run_manifest (run_id),
    dimension         TEXT NOT NULL,
    subject_ref       TEXT NOT NULL,
    expected          TEXT,
    observed          TEXT,
    verdict           TEXT,               -- NULL only for the two undefined cases
    no_verdict_reason TEXT,               -- 'stage_error' | 'expectation_not_applicable'
    attributed_stage  TEXT,               -- filled by Task 11
    evidence_ref      TEXT,               -- a P4 observation_key, never an observation_id
    UNIQUE (run_id, dimension, subject_ref)
);
"""


class ObservationIdRefused(Exception):
    """An assertion cited a per-row observation id instead of the content-addressed key."""


def verdict_for(*, expected_outcome_kind: str, expected_value,
                observed_outcome: str | None,
                observed_value) -> tuple[str | None, str | None]:
    """One verdict, or (None, reason) where §8.5 defines none.

    No tolerance parameter exists, and none can be added without answering SPEC
    Open question 2. Comparison is exact equality over canonical JSON.
    """
    if expected_outcome_kind == "not-applicable":
        return None, "expectation_not_applicable"
    if observed_outcome is None:
        # No stage produced a value for this subject. The stage that would have
        # is absent, or did not decide about it.
        return "not_run", None
    if observed_outcome == "not_implemented":
        return "not_run", None
    if observed_outcome == "error":
        return None, "stage_error"
    if observed_outcome == "deferred":
        # §8.6: a budget event. Never `divergent`, for any dimension.
        return "deferred", None
    if observed_outcome == "abstained":
        if expected_outcome_kind == "abstained":
            return "abstained_correctly", None
        return "abstained_incorrectly", None
    if observed_outcome == "produced":
        if expected_outcome_kind == "abstained":
            return "asserted_incorrectly", None
        if canonical_json(expected_value) == canonical_json(observed_value):
            return "match", None
        return "divergent", None
    raise ValueError(f"unhandled observed outcome {observed_outcome!r}")


def write_assertion(conn: sqlite3.Connection, *, run_id: str, dimension: str,
                    subject_ref: str, expected: str | None, observed: str | None,
                    verdict: str | None, no_verdict_reason: str | None,
                    evidence_ref: str | None) -> int:
    check_dimension(dimension)
    if verdict is not None and verdict not in VERDICTS:
        raise ValueError(f"verdict {verdict!r} is not one of {VERDICTS}")
    if evidence_ref is not None and evidence_ref.startswith("observation_id"):
        raise ObservationIdRefused(
            "an assertion cites a P4 observation by `observation_key`, which is "
            "content-addressed and survives an extractor upgrade; `observation_id` "
            "is per-row and dies on exactly the version change §8.5 measures (§8.7)"
        )
    cursor = conn.execute(
        "INSERT INTO assertion (run_id, dimension, subject_ref, expected, observed, "
        "verdict, no_verdict_reason, evidence_ref) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (run_id, dimension, subject_ref, expected, observed, verdict,
         no_verdict_reason, evidence_ref),
    )
    return cursor.lastrowid


def assert_run(conn: sqlite3.Connection, run_id: str) -> int:
    """Write one assertion per expectation in the run's bundle. Returns the count."""
    from eval_harness.bundle import expectations
    from eval_harness.run import get_run

    bundle_id = get_run(conn, run_id)["bundle_id"]
    observed_rows = {
        (r["dimension"], r["subject_ref"]): r
        for r in conn.execute(
            "SELECT dimension, subject_ref, outcome, value FROM "
            "stage_dimension_value WHERE run_id = ?", (run_id,))
    }
    written = 0
    for expectation in expectations(conn, bundle_id):
        key = (expectation["dimension"], expectation["subject_ref"])
        observed = observed_rows.get(key)
        observed_outcome = None if observed is None else observed["outcome"]
        observed_value = (None if observed is None or observed["value"] is None
                          else json.loads(observed["value"]))
        verdict, reason = verdict_for(
            expected_outcome_kind=expectation["expected_outcome_kind"],
            expected_value=expectation["expected_value"],
            observed_outcome=observed_outcome, observed_value=observed_value,
        )
        write_assertion(
            conn, run_id=run_id, dimension=expectation["dimension"],
            subject_ref=expectation["subject_ref"],
            expected=(None if expectation["expected_value"] is None
                      else canonical_json(expectation["expected_value"])),
            observed=None if observed is None else observed["value"],
            verdict=verdict, no_verdict_reason=reason, evidence_ref=None,
        )
        written += 1
    return written


def assertions(conn: sqlite3.Connection, run_id: str, *,
               dimension: str | None = None) -> list[sqlite3.Row]:
    if dimension is None:
        return conn.execute(
            "SELECT * FROM assertion WHERE run_id = ? ORDER BY dimension, subject_ref",
            (run_id,)).fetchall()
    return conn.execute(
        "SELECT * FROM assertion WHERE run_id = ? AND dimension = ? "
        "ORDER BY subject_ref", (run_id, check_dimension(dimension))).fetchall()


def verdict_counts(conn: sqlite3.Connection, run_id: str) -> dict[str, int]:
    """Per-verdict counts, with the two undefined cases under `unverdicted`.

    §8.6's legibility requirement, applied to evaluation: completed versus
    deferred work is visible, and a partial evaluation is reported as partial.
    There is no total, no ratio, and no aggregate (Done-means 3).
    """
    counts: dict[str, int] = {}
    for row in conn.execute(
            "SELECT verdict, count(*) AS n FROM assertion WHERE run_id = ? "
            "GROUP BY verdict", (run_id,)):
        counts[row["verdict"] or "unverdicted"] = row["n"]
    return counts
```

Add to `store.py`'s `_ddl_scripts`:

```python
    from eval_harness import assertions, bundle, run, stage_output
    return [bundle.BUNDLE_DDL, run.RUN_DDL, stage_output.STAGE_DDL,
            assertions.ASSERTION_DDL]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/eval/test_assertions.py -v`
Expected: PASS — 16 passed

- [ ] **Step 5: Commit**

```bash
git add src/eval_harness/assertions.py src/eval_harness/store.py tests/eval/test_assertions.py
git commit -m "feat(P2): seven verdicts, abstention passes, deferral is never divergence, no eighth name"
```

---

### Task 11: Earliest-divergence attribution (Done-means 4)

**Files:**
- Create: `src/eval_harness/attribution.py`
- Test: `tests/eval/test_attribution.py`

**Interfaces:**
- Consumes: `assertions` (Task 10); `stage_outputs` (Task 4); `stage_order`, `STAGE_IDS` (Task 2).
- Produces: `FAILING_VERDICTS: frozenset[str]`, `ANCESTOR_VERDICTS: frozenset[str]`, `attribute_run(conn, run_id) -> int`, `attribution_histogram(conn, run_id) -> dict[str, int]`.

**`attributed_stage` is the mechanism for §8.5's "identify whether the error *began* with…".** SPEC Contract out §6 defines it literally: *"the earliest stage on this subject's `inputs[]` chain whose own assertion verdict is divergent / asserted_incorrectly."* `ANCESTOR_VERDICTS` is those two, verbatim. `FAILING_VERDICTS` — the verdicts that *get* attributed — is those two plus `abstained_incorrectly`, because a stage that abstained when evidence was present is a wrong terminal outcome and Done-means 4 says every wrong terminal outcome yields exactly one attributed stage.

**"Earliest" is resolved by §8.5's own stage order.** Among every qualifying stage reachable on the chain, including the emitting stage itself, the attributed one is the smallest `stage_order`. That order is §8.5's list order, *"which is also the pipeline order of §4.10 and §6.12"* — so "earliest" means earliest in the pipeline, which is what *"where the error began"* asks. Because `stage_order` is injective over the ten, the minimum is unique: **exactly one** stage, always. If no ancestor qualifies, the emitting stage attributes to itself, which is still exactly one.

**SPEC Open question 3 stays open and this traversal is why it can.** OQ3 asks whether attribution follows `inputs[]` edges *across subjects* or only within one subject's own chain. The traversal walks the edge set it is given: if P9 or P11 emit a cross-file `inputs[]` edge, it is followed; if they emit only same-subject edges, only the subject's own chain is walked. **P2 neither requires nor forbids cross-subject edges**, so nothing here decides OQ3, and the two tests below show the same code producing both behaviours from the recorded edges alone.

**Resolution of an `inputs[]` entry is by `subject_ref` within the run.** Contract out §4 publishes `inputs[]` as subject_refs, so an entry resolves to every stage output in this run carrying that subject_ref — which may be more than one where two stages decided about one subject. All of them are traversed. The ambiguity is in the published shape; a recommended SPEC change is in the report and is not made here.

**Cycles terminate.** A visited set over `(stage_id, subject_ref)` bounds the walk. A cycle in `inputs[]` is a defect in the emitting part, not something P2 repairs — but P2 must not hang on one.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_attribution.py
from eval_harness.assertions import assert_run, assertions
from eval_harness.attribution import (
    ANCESTOR_VERDICTS, FAILING_VERDICTS, attribute_run, attribution_histogram,
)
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.replay import ReplayContext, StageResult, replay_bundle
from eval_harness.stage_output import DimensionValue
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import STAGE_IDS


def _tuple():
    return dict(extractor_versions={}, graph_algorithm_version=None,
                prompt_fingerprint=None, model_identifier=None,
                template_library_version=None, placement_scorer_version=None,
                analysis_tiers_enabled=["filesystem"])


def _settings():
    return {"model_enabled": False, "embeddings_enabled": False}


def _emit(subject_ref, dimension, value, inputs=(), outcome="produced"):
    def adapter(ctx: ReplayContext):
        return [StageResult(subject_ref=subject_ref, outcome=outcome, payload=None,
                            inputs=list(inputs), budget_state="within_ceiling",
                            values=[DimensionValue(dimension, subject_ref, outcome,
                                                   value)])]
    return adapter


def _bundle(conn, expectations):
    bundle_id = open_bundle(conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    for e in expectations:
        add_expectation(conn, bundle_id, **e)
    seal_bundle(conn, bundle_id)
    return bundle_id


def test_the_two_verdict_sets():
    # SPEC Contract out §6, verbatim: the ancestor criterion is divergent /
    # asserted_incorrectly. Done-means 4 attributes every wrong terminal outcome.
    assert ANCESTOR_VERDICTS == frozenset({"divergent", "asserted_incorrectly"})
    assert FAILING_VERDICTS == frozenset({"divergent", "asserted_incorrectly",
                                          "abstained_incorrectly"})


def test_a_wrong_placement_attributes_to_the_earliest_divergent_stage(eval_conn):
    # extraction produced the wrong text; the fact and the placement are wrong in
    # consequence. §8.5: name where the error BEGAN.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="extraction", subject_ref="file-1",
             expected_value={"text": "COMS 4995"}, expected_outcome_kind="produced",
             source="hand-labelled"),
        dict(dimension="fact", subject_ref="file-1",
             expected_value={"course": "COMS 4995"},
             expected_outcome_kind="produced", source="hand-labelled"),
        dict(dimension="placement", subject_ref="file-1",
             expected_value={"node_id": "n-coms"}, expected_outcome_kind="produced",
             source="hand-labelled"),
    ])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "extraction": _emit("file-1", "extraction", {"text": "COMS 4996"}),
        "factual_validation": _emit("file-1", "fact", {"course": "COMS 4996"},
                                    inputs=["file-1"]),
        "placement_scoring": _emit("file-1", "placement", {"node_id": "n-other"},
                                   inputs=["file-1"]),
    })
    assert_run(eval_conn, run_id)
    assert attribute_run(eval_conn, run_id) == 3
    by_dimension = {r["dimension"]: r for r in assertions(eval_conn, run_id)}
    assert by_dimension["placement"]["verdict"] == "divergent"
    assert by_dimension["placement"]["attributed_stage"] == "extraction"
    assert by_dimension["fact"]["attributed_stage"] == "extraction"
    assert by_dimension["extraction"]["attributed_stage"] == "extraction"


def test_exactly_one_stage_is_named_and_it_is_one_of_the_ten(eval_conn):
    # Done-means 4.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="placement", subject_ref="file-1",
             expected_value={"node_id": "n1"}, expected_outcome_kind="produced",
             source="hand-labelled")])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "placement_scoring": _emit("file-1", "placement", {"node_id": "n2"})})
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)
    row = assertions(eval_conn, run_id)[0]
    assert row["attributed_stage"] in STAGE_IDS
    assert isinstance(row["attributed_stage"], str)


def test_a_matching_verdict_is_attributed_to_nothing(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="placement", subject_ref="file-1",
             expected_value={"node_id": "n1"}, expected_outcome_kind="produced",
             source="hand-labelled")])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "placement_scoring": _emit("file-1", "placement", {"node_id": "n1"})})
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)
    row = assertions(eval_conn, run_id)[0]
    assert row["verdict"] == "match"
    assert row["attributed_stage"] is None


def test_a_deferral_is_attributed_to_nothing(eval_conn):
    # §8.6: a deferral is not a wrong outcome, so it has no origin to name.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="placement", subject_ref="file-1",
             expected_value={"node_id": "n1"}, expected_outcome_kind="produced",
             source="hand-labelled")])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "placement_scoring": lambda ctx: [StageResult(
            subject_ref="file-1", outcome="deferred", payload=None, inputs=[],
            budget_state="ceiling_reached",
            values=[DimensionValue("placement", "file-1", "deferred", None)])]})
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)
    row = assertions(eval_conn, run_id)[0]
    assert row["verdict"] == "deferred"
    assert row["attributed_stage"] is None


def test_attribution_follows_a_cross_subject_edge_when_one_is_emitted(eval_conn):
    # SPEC Open question 3 is OPEN. P2 walks the edges it is given: a wrong
    # placement for file A originating in a wrong fact on file B is attributed
    # across subjects ONLY because the emitting part recorded that edge.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="fact", subject_ref="file-B", expected_value={"v": 1},
             expected_outcome_kind="produced", source="hand-labelled"),
        dict(dimension="placement", subject_ref="file-A", expected_value={"n": 1},
             expected_outcome_kind="produced", source="hand-labelled"),
    ])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "factual_validation": _emit("file-B", "fact", {"v": 2}),
        "placement_scoring": _emit("file-A", "placement", {"n": 2},
                                   inputs=["file-B"]),
    })
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)
    placement = [r for r in assertions(eval_conn, run_id)
                 if r["dimension"] == "placement"][0]
    assert placement["attributed_stage"] == "factual_validation"


def test_without_a_cross_subject_edge_attribution_stays_within_the_subject(eval_conn):
    # The same code, the same two wrong values, no recorded edge between them.
    # Nothing in P2 requires the edge to exist — that is what OQ3 asks.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="fact", subject_ref="file-B", expected_value={"v": 1},
             expected_outcome_kind="produced", source="hand-labelled"),
        dict(dimension="placement", subject_ref="file-A", expected_value={"n": 1},
             expected_outcome_kind="produced", source="hand-labelled"),
    ])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "factual_validation": _emit("file-B", "fact", {"v": 2}),
        "placement_scoring": _emit("file-A", "placement", {"n": 2}, inputs=[]),
    })
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)
    placement = [r for r in assertions(eval_conn, run_id)
                 if r["dimension"] == "placement"][0]
    assert placement["attributed_stage"] == "placement_scoring"


def test_a_cycle_in_inputs_terminates(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="grouping", subject_ref="g-1", expected_value={"m": 1},
             expected_outcome_kind="produced", source="hand-labelled")])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "retrieval": _emit("g-1", "retrieval", {"x": 1}, inputs=["g-1"]),
        "grouping": _emit("g-1", "grouping", {"m": 2}, inputs=["g-1"]),
    })
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)      # must return, not hang
    assert assertions(eval_conn, run_id)[0]["attributed_stage"] in STAGE_IDS


def test_the_histogram_counts_stages_and_totals_nothing(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn, [
        dict(dimension="fact", subject_ref="file-1", expected_value={"v": 1},
             expected_outcome_kind="produced", source="hand-labelled"),
        dict(dimension="placement", subject_ref="file-1", expected_value={"n": 1},
             expected_outcome_kind="produced", source="hand-labelled"),
    ])
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(), adapters={
        "factual_validation": _emit("file-1", "fact", {"v": 2}),
        "placement_scoring": _emit("file-1", "placement", {"n": 2},
                                   inputs=["file-1"]),
    })
    assert_run(eval_conn, run_id)
    attribute_run(eval_conn, run_id)
    histogram = attribution_histogram(eval_conn, run_id)
    assert histogram == {"factual_validation": 2}
    assert set(histogram) <= set(STAGE_IDS)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/eval/test_attribution.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_harness.attribution'`

- [ ] **Step 3: Write the implementation**

```python
# src/eval_harness/attribution.py
"""Contract out §6 — `attributed_stage`.

§8.5: "identify whether the error BEGAN with extraction, factual validation,
retrieval, graph construction, LLM interpretation, grouping, template generation,
tree design, candidate-node retrieval, or placement scoring."

The traversal walks whatever `inputs[]` edges the emitting parts recorded. It does
NOT require cross-subject edges and does not forbid them — SPEC Open question 3
asks whether attribution should follow them, and this module answers it neither
way: given cross-subject edges it follows them, given none it stays inside the
subject's own chain.
"""
from __future__ import annotations

import json
import sqlite3

from eval_harness.vocabulary import stage_order

#: SPEC Contract out §6, verbatim: the verdicts that make an ANCESTOR the origin.
ANCESTOR_VERDICTS: frozenset[str] = frozenset({"divergent", "asserted_incorrectly"})

#: Done-means 4: every wrong terminal outcome yields exactly one attributed stage.
#: An incorrect abstention is a wrong terminal outcome; a deferral and a `not_run`
#: are not, and are attributed to nothing.
FAILING_VERDICTS: frozenset[str] = ANCESTOR_VERDICTS | {"abstained_incorrectly"}


def _stage_verdicts(conn: sqlite3.Connection, run_id: str) -> dict[str, set[str]]:
    """(stage_id, subject_ref) -> the verdicts of assertions on values it emitted."""
    out: dict[str, set[str]] = {}
    for row in conn.execute(
            "SELECT v.stage_id, v.subject_ref, a.verdict "
            "FROM stage_dimension_value v JOIN assertion a "
            "  ON a.run_id = v.run_id AND a.dimension = v.dimension "
            "     AND a.subject_ref = v.subject_ref "
            "WHERE v.run_id = ?", (run_id,)):
        out.setdefault((row["stage_id"], row["subject_ref"]), set()).add(row["verdict"])
    return out


def _edges(conn: sqlite3.Connection, run_id: str):
    """subject_ref -> the stage outputs that carry it, and their inputs[]."""
    by_subject: dict[str, list[tuple[str, list[str]]]] = {}
    for row in conn.execute(
            "SELECT stage_id, subject_ref, inputs FROM stage_output WHERE run_id = ?",
            (run_id,)):
        by_subject.setdefault(row["subject_ref"], []).append(
            (row["stage_id"], json.loads(row["inputs"])))
    return by_subject


def attribute_run(conn: sqlite3.Connection, run_id: str) -> int:
    """Fill `assertion.attributed_stage` for this run. Returns rows attributed.

    Exactly one stage per wrong terminal outcome: among every qualifying stage
    reachable on the chain — including the emitting stage itself — the attributed
    one is the smallest `stage_order`, which is §8.5's list order and therefore
    §4.10's and §6.12's pipeline order. `stage_order` is injective over the ten,
    so the minimum is unique.
    """
    verdicts = _stage_verdicts(conn, run_id)
    by_subject = _edges(conn, run_id)
    emitters = {
        (row["dimension"], row["subject_ref"]): row["stage_id"]
        for row in conn.execute(
            "SELECT dimension, subject_ref, stage_id FROM stage_dimension_value "
            "WHERE run_id = ?", (run_id,))
    }

    attributed = 0
    for row in conn.execute(
            "SELECT assertion_id, dimension, subject_ref, verdict FROM assertion "
            "WHERE run_id = ?", (run_id,)).fetchall():
        if row["verdict"] not in FAILING_VERDICTS:
            continue
        emitting_stage = emitters.get((row["dimension"], row["subject_ref"]))
        if emitting_stage is None:
            continue
        candidates = {emitting_stage}
        seen: set[tuple[str, str]] = set()
        frontier = [(emitting_stage, row["subject_ref"])]
        while frontier:
            stage_id, subject_ref = frontier.pop()
            if (stage_id, subject_ref) in seen:
                continue          # a cycle in inputs[] is a defect upstream, not a hang here
            seen.add((stage_id, subject_ref))
            for candidate_stage, inputs in by_subject.get(subject_ref, []):
                if candidate_stage != stage_id:
                    continue
                for input_ref in inputs:
                    for ancestor_stage, _ in by_subject.get(input_ref, []):
                        if verdicts.get((ancestor_stage, input_ref), set()) & ANCESTOR_VERDICTS:
                            candidates.add(ancestor_stage)
                        frontier.append((ancestor_stage, input_ref))
        earliest = min(candidates, key=stage_order)
        conn.execute("UPDATE assertion SET attributed_stage = ? WHERE assertion_id = ?",
                     (earliest, row["assertion_id"]))
        attributed += 1
    return attributed


def attribution_histogram(conn: sqlite3.Connection, run_id: str) -> dict[str, int]:
    """attributed_stage -> count. A count per stage and no total: §8.5 forbids the
    single number, and a total over ten stages is the shape that invites one."""
    return {row["attributed_stage"]: row["n"] for row in conn.execute(
        "SELECT attributed_stage, count(*) AS n FROM assertion "
        "WHERE run_id = ? AND attributed_stage IS NOT NULL "
        "GROUP BY attributed_stage", (run_id,))}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/eval/test_attribution.py -v`
Expected: PASS — 9 passed

- [ ] **Step 5: Commit**

```bash
git add src/eval_harness/attribution.py tests/eval/test_attribution.py
git commit -m "feat(P2): earliest-divergence attribution over recorded inputs[], exactly one stage"
```

---

### Task 12: The comparison record (Done-means 6, 8)

**Files:**
- Create: `src/eval_harness/comparison.py`
- Modify: `src/eval_harness/store.py` — add `comparison.COMPARISON_DDL` to `_ddl_scripts`
- Test: `tests/eval/test_comparison.py`

**Interfaces:**
- Consumes: `get_run`, `get_version_tuple`, `run_ceilings`, `VERSION_AXES`, `VERSION_TUPLE_FIELDS` (Task 3); `assertions`, `PASSING_VERDICTS` (Task 10); `attribution_histogram` (Task 11); `DIMENSIONS` (Task 2).
- Produces: `compare_runs(conn, baseline_run_id, candidate_run_id) -> str` returning `comparison_id`, `get_comparison(conn, comparison_id) -> dict`, `DifferentBundles`.

**A comparison is over one bundle.** `compare_runs` refuses two runs whose `bundle_id` differs — a delta between different corpora is not a version comparison, and §8.5's whole premise is *"the same bundle … compared against prior results."*

**The delta names all seven tuple fields and labels the six §8.5 axes.** Done-means 8 requires a comparison of two runs differing in one of the six axes to *name that axis*. `version_tuple_delta` therefore carries, per differing field, its baseline value, its candidate value, and `is_8_5_axis` — true for the six, false for `analysis_tiers_enabled`, which arrives from I4 rather than from §8.5. Nothing is hidden and nothing is mislabelled.

**Different ceilings make a comparison labelled, not refused.** SPEC Contract out §5: *"Two runs are only comparable when they were given the same `budget_ceilings`; a comparison across different ceilings must be labelled, because deferral changes outputs."* `ceilings_differ` plus the differing keys is that label. **The values are not interpreted** — P2 does not decide that one ceiling is "lower" than another, because that would require knowing each key's polarity, and §8.6 supplies none.

**Every dimension gets a block, always, even an empty one.** Done-means 2 — none is collapsed into another — and §8.5's prohibition on the single number both fail the moment a renderer is allowed to skip the dimensions with nothing in them, because a ten-row table with three rows present reads as three dimensions mattering.

**`deferral_changed[]` is separate from `newly_divergent[]`, and Done-means 6 depends on it.** A subject whose verdict moved to `deferred` appears in `deferral_changed`, never in `newly_divergent`. The test below runs the same bundle, same version tuple, different ceilings, with a stage that defers under the tighter one, and asserts **zero** newly divergent subjects across every dimension.

**There is no aggregate field.** No total, no rate, no score, no delta-of-scores. Task 16 scans for one; this module simply has none to find.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_comparison.py
import pytest

from eval_harness.assertions import assert_run
from eval_harness.attribution import attribute_run
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.comparison import DifferentBundles, compare_runs, get_comparison
from eval_harness.replay import ReplayContext, StageResult, replay_bundle
from eval_harness.stage_output import DimensionValue
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import DIMENSIONS


def _tuple(**overrides):
    fields = dict(extractor_versions={"pdf.native": "1.0.0"},
                  graph_algorithm_version=None, prompt_fingerprint=None,
                  model_identifier=None, template_library_version=None,
                  placement_scorer_version=None,
                  analysis_tiers_enabled=["filesystem", "native"])
    fields.update(overrides)
    return fields


def _settings():
    return {"model_enabled": False, "embeddings_enabled": False}


def _bundle(conn):
    bundle_id = open_bundle(conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    add_expectation(conn, bundle_id, dimension="extraction", subject_ref="file-1",
                    expected_value={"text": "COMS 4995"},
                    expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(conn, bundle_id)
    return bundle_id


def _producing(value):
    def adapter(ctx: ReplayContext):
        return [StageResult(subject_ref="file-1", outcome="produced", payload=None,
                            inputs=[], budget_state="within_ceiling",
                            values=[DimensionValue("extraction", "file-1",
                                                   "produced", value)])]
    return adapter


def _deferring(ctx: ReplayContext):
    return [StageResult(subject_ref="file-1", outcome="deferred", payload=None,
                        inputs=[], budget_state="ceiling_reached",
                        values=[DimensionValue("extraction", "file-1", "deferred",
                                               None)])]


def _run(conn, bundle_id, *, adapters, version_tuple=None, ceilings=None):
    run_id = replay_bundle(conn, bundle_id,
                           version_tuple=version_tuple or _tuple(),
                           budget_ceilings=ceilings or {},
                           run_settings=_settings(), adapters=adapters)
    assert_run(conn, run_id)
    attribute_run(conn, run_id)
    return run_id


def test_two_runs_over_different_bundles_are_refused(eval_conn):
    create_eval_schema(eval_conn)
    first, second = _bundle(eval_conn), _bundle(eval_conn)
    a = _run(eval_conn, first, adapters={})
    b = _run(eval_conn, second, adapters={})
    with pytest.raises(DifferentBundles):
        compare_runs(eval_conn, a, b)


def test_a_changed_axis_is_named_and_labelled_as_one_of_the_six(eval_conn):
    # Done-means 8.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    baseline = _run(eval_conn, bundle_id,
                    adapters={"extraction": _producing({"text": "COMS 4996"})})
    candidate = _run(eval_conn, bundle_id,
                     adapters={"extraction": _producing({"text": "COMS 4995"})},
                     version_tuple=_tuple(extractor_versions={"pdf.native": "2.0.0"}))
    comparison = get_comparison(eval_conn, compare_runs(eval_conn, baseline, candidate))
    delta = comparison["version_tuple_delta"]
    assert set(delta) == {"extractor_versions"}
    assert delta["extractor_versions"]["baseline"] == {"pdf.native": "1.0.0"}
    assert delta["extractor_versions"]["candidate"] == {"pdf.native": "2.0.0"}
    assert delta["extractor_versions"]["is_8_5_axis"] is True


def test_a_changed_tier_set_is_reported_and_not_claimed_as_an_8_5_axis(eval_conn):
    # analysis_tiers_enabled comes from 10-i4-learning-ops.md, not from §8.5's six.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    baseline = _run(eval_conn, bundle_id, adapters={})
    candidate = _run(eval_conn, bundle_id, adapters={},
                     version_tuple=_tuple(
                         analysis_tiers_enabled=["filesystem", "native", "ocr"]))
    delta = get_comparison(
        eval_conn, compare_runs(eval_conn, baseline, candidate))["version_tuple_delta"]
    assert set(delta) == {"analysis_tiers_enabled"}
    assert delta["analysis_tiers_enabled"]["is_8_5_axis"] is False


def test_newly_matching_and_newly_divergent_are_per_dimension(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    baseline = _run(eval_conn, bundle_id,
                    adapters={"extraction": _producing({"text": "COMS 4996"})})
    candidate = _run(eval_conn, bundle_id,
                     adapters={"extraction": _producing({"text": "COMS 4995"})})
    comparison = get_comparison(eval_conn, compare_runs(eval_conn, baseline, candidate))
    block = comparison["per_dimension"]["extraction"]
    assert block["newly_matching"] == ["file-1"]
    assert block["newly_divergent"] == []
    assert comparison["disagreements"][0]["baseline_verdict"] == "divergent"
    assert comparison["disagreements"][0]["candidate_verdict"] == "match"


def test_every_dimension_gets_a_block_even_an_empty_one(eval_conn):
    # Done-means 2: "None is collapsed into another." A ten-row table with three
    # rows present reads as three dimensions mattering.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    a = _run(eval_conn, bundle_id, adapters={})
    b = _run(eval_conn, bundle_id, adapters={})
    comparison = get_comparison(eval_conn, compare_runs(eval_conn, a, b))
    assert set(comparison["per_dimension"]) == set(DIMENSIONS)
    for block in comparison["per_dimension"].values():
        assert set(block) == {"newly_matching", "newly_divergent", "unchanged_count",
                              "deferral_changed", "attribution_histogram"}


def test_a_ceiling_only_change_produces_zero_new_divergences(eval_conn):
    # Done-means 6, and §8.6: "cost exhaustion must never turn into lower-quality
    # automatic classification." The numbers are fixture values.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    baseline = _run(eval_conn, bundle_id,
                    adapters={"extraction": _producing({"text": "COMS 4995"})},
                    ceilings={"ocr.max_pages_per_file": 100})
    candidate = _run(eval_conn, bundle_id, adapters={"extraction": _deferring},
                     ceilings={"ocr.max_pages_per_file": 1})
    comparison = get_comparison(eval_conn, compare_runs(eval_conn, baseline, candidate))
    assert comparison["ceilings_differ"] is True
    assert comparison["ceilings_differing_keys"] == ["ocr.max_pages_per_file"]
    for dimension, block in comparison["per_dimension"].items():
        assert block["newly_divergent"] == [], dimension
    assert comparison["per_dimension"]["extraction"]["deferral_changed"] == ["file-1"]


def test_the_attribution_histogram_is_carried_per_dimension(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    baseline = _run(eval_conn, bundle_id,
                    adapters={"extraction": _producing({"text": "COMS 4995"})})
    candidate = _run(eval_conn, bundle_id,
                     adapters={"extraction": _producing({"text": "wrong"})})
    comparison = get_comparison(eval_conn, compare_runs(eval_conn, baseline, candidate))
    assert comparison["per_dimension"]["extraction"]["attribution_histogram"] == \
        {"extraction": 1}


def test_the_comparison_has_no_aggregate_field(eval_conn):
    # §8.5: "A single overall 'accuracy' number hides the mechanism that needs
    # repair." Done-means 3, asserted again over the whole record in Task 16.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    a = _run(eval_conn, bundle_id, adapters={})
    b = _run(eval_conn, bundle_id, adapters={})
    comparison = get_comparison(eval_conn, compare_runs(eval_conn, a, b))

    def walk(node, path=""):
        if isinstance(node, dict):
            for key, value in node.items():
                for part in str(key).split("_"):
                    assert part not in {"accuracy", "score", "aggregate", "overall",
                                        "rate", "percent", "grade", "f1", "precision",
                                        "recall"}, f"{path}.{key}"
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for item in node:
                walk(item, path)

    walk(comparison)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/eval/test_comparison.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_harness.comparison'`

- [ ] **Step 3: Write the implementation**

```python
# src/eval_harness/comparison.py
"""Contract out §7 — the run-to-run comparison record.

It has no aggregate accuracy field and the renderer must not compute one. §8.5:
"A single overall 'accuracy' number hides the mechanism that needs repair." Every
dimension gets a block, always, including an empty one.

Deferral is reported separately from divergence, so a run whose only change is a
different ceiling produces zero new divergences (§8.6).
"""
from __future__ import annotations

import json
import sqlite3
import uuid

from eval_harness.run import VERSION_AXES, VERSION_TUPLE_FIELDS
from eval_harness.store import canonical_json
from eval_harness.vocabulary import DIMENSIONS

COMPARISON_DDL = """
CREATE TABLE IF NOT EXISTS comparison (
    comparison_id           TEXT PRIMARY KEY,
    baseline_run_id         TEXT NOT NULL REFERENCES run_manifest (run_id),
    candidate_run_id        TEXT NOT NULL REFERENCES run_manifest (run_id),
    bundle_id               TEXT NOT NULL,
    version_tuple_delta     TEXT NOT NULL,
    ceilings_differ         INTEGER NOT NULL,
    ceilings_differing_keys TEXT NOT NULL,
    disagreements           TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS comparison_dimension (
    comparison_id         TEXT NOT NULL REFERENCES comparison (comparison_id),
    dimension             TEXT NOT NULL,
    newly_matching        TEXT NOT NULL,
    newly_divergent       TEXT NOT NULL,
    unchanged_count       INTEGER NOT NULL,
    deferral_changed      TEXT NOT NULL,
    attribution_histogram TEXT NOT NULL,
    PRIMARY KEY (comparison_id, dimension)
);
"""


class DifferentBundles(Exception):
    """§8.5 compares THE SAME bundle across versions. Two corpora is not that."""


def _verdicts(conn: sqlite3.Connection, run_id: str) -> dict[tuple[str, str], sqlite3.Row]:
    return {(r["dimension"], r["subject_ref"]): r for r in conn.execute(
        "SELECT dimension, subject_ref, verdict, attributed_stage FROM assertion "
        "WHERE run_id = ?", (run_id,))}


def compare_runs(conn: sqlite3.Connection, baseline_run_id: str,
                 candidate_run_id: str) -> str:
    """Compare two runs over one bundle. Returns the comparison_id."""
    from eval_harness.assertions import PASSING_VERDICTS
    from eval_harness.run import get_run, get_version_tuple, run_ceilings

    baseline, candidate = get_run(conn, baseline_run_id), get_run(conn, candidate_run_id)
    if baseline["bundle_id"] != candidate["bundle_id"]:
        raise DifferentBundles(
            f"{baseline['bundle_id']} vs {candidate['bundle_id']}: §8.5 compares "
            "the same bundle re-processed, not two corpora"
        )

    base_tuple = get_version_tuple(conn, baseline["version_tuple_ref"])
    cand_tuple = get_version_tuple(conn, candidate["version_tuple_ref"])
    delta = {}
    for field in VERSION_TUPLE_FIELDS:
        if base_tuple.get(field) != cand_tuple.get(field):
            delta[field] = {"baseline": base_tuple.get(field),
                            "candidate": cand_tuple.get(field),
                            # six of the seven are §8.5's named axes; the seventh
                            # is I4's tier set and is reported as what it is.
                            "is_8_5_axis": field in VERSION_AXES}

    base_ceilings, cand_ceilings = run_ceilings(conn, baseline_run_id), run_ceilings(
        conn, candidate_run_id)
    differing_keys = sorted(
        k for k in set(base_ceilings) | set(cand_ceilings)
        if base_ceilings.get(k) != cand_ceilings.get(k))
    # Labelled, not refused, and not interpreted: §8.6 supplies no polarity for a
    # ceiling, so P2 does not decide that one run's ceiling was "lower".

    base_verdicts, cand_verdicts = _verdicts(conn, baseline_run_id), _verdicts(
        conn, candidate_run_id)
    comparison_id = str(uuid.uuid4())
    disagreements = []
    blocks = {d: {"newly_matching": [], "newly_divergent": [], "unchanged_count": 0,
                  "deferral_changed": [], "attribution_histogram": {}}
              for d in DIMENSIONS}

    for key in sorted(set(base_verdicts) | set(cand_verdicts)):
        dimension, subject_ref = key
        before = base_verdicts.get(key)
        after = cand_verdicts.get(key)
        before_verdict = None if before is None else before["verdict"]
        after_verdict = None if after is None else after["verdict"]
        block = blocks[dimension]
        if before_verdict == after_verdict:
            block["unchanged_count"] += 1
            continue
        disagreements.append({"subject_ref": subject_ref, "dimension": dimension,
                              "baseline_verdict": before_verdict,
                              "candidate_verdict": after_verdict,
                              "attributed_stage": (None if after is None
                                                   else after["attributed_stage"])})
        if "deferred" in (before_verdict, after_verdict):
            # §8.6 — a budget event, reported as one and never as a regression.
            block["deferral_changed"].append(subject_ref)
            continue
        if after_verdict in PASSING_VERDICTS and before_verdict not in PASSING_VERDICTS:
            block["newly_matching"].append(subject_ref)
        elif before_verdict in PASSING_VERDICTS and after_verdict not in PASSING_VERDICTS:
            block["newly_divergent"].append(subject_ref)
        if after is not None and after["attributed_stage"]:
            histogram = block["attribution_histogram"]
            histogram[after["attributed_stage"]] = histogram.get(
                after["attributed_stage"], 0) + 1

    conn.execute(
        "INSERT INTO comparison (comparison_id, baseline_run_id, candidate_run_id, "
        "bundle_id, version_tuple_delta, ceilings_differ, ceilings_differing_keys, "
        "disagreements) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (comparison_id, baseline_run_id, candidate_run_id, baseline["bundle_id"],
         canonical_json(delta), 1 if differing_keys else 0,
         canonical_json(differing_keys), canonical_json(disagreements)),
    )
    for dimension in DIMENSIONS:                 # every one, always
        block = blocks[dimension]
        conn.execute(
            "INSERT INTO comparison_dimension (comparison_id, dimension, "
            "newly_matching, newly_divergent, unchanged_count, deferral_changed, "
            "attribution_histogram) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (comparison_id, dimension, canonical_json(block["newly_matching"]),
             canonical_json(block["newly_divergent"]), block["unchanged_count"],
             canonical_json(block["deferral_changed"]),
             canonical_json(block["attribution_histogram"])),
        )
    return comparison_id


def get_comparison(conn: sqlite3.Connection, comparison_id: str) -> dict:
    """The comparison record. No aggregate field exists to return."""
    row = conn.execute("SELECT * FROM comparison WHERE comparison_id = ?",
                       (comparison_id,)).fetchone()
    if row is None:
        raise KeyError(comparison_id)
    per_dimension = {}
    for block in conn.execute(
            "SELECT * FROM comparison_dimension WHERE comparison_id = ?",
            (comparison_id,)):
        per_dimension[block["dimension"]] = {
            "newly_matching": json.loads(block["newly_matching"]),
            "newly_divergent": json.loads(block["newly_divergent"]),
            "unchanged_count": block["unchanged_count"],
            "deferral_changed": json.loads(block["deferral_changed"]),
            "attribution_histogram": json.loads(block["attribution_histogram"]),
        }
    return {
        "comparison_id": row["comparison_id"],
        "baseline_run_id": row["baseline_run_id"],
        "candidate_run_id": row["candidate_run_id"],
        "bundle_id": row["bundle_id"],
        "version_tuple_delta": json.loads(row["version_tuple_delta"]),
        "ceilings_differ": bool(row["ceilings_differ"]),
        "ceilings_differing_keys": json.loads(row["ceilings_differing_keys"]),
        "per_dimension": per_dimension,
        "disagreements": json.loads(row["disagreements"]),
    }
```

Add to `store.py`'s `_ddl_scripts`:

```python
    from eval_harness import assertions, bundle, comparison, run, stage_output
    return [bundle.BUNDLE_DDL, run.RUN_DDL, stage_output.STAGE_DDL,
            assertions.ASSERTION_DDL, comparison.COMPARISON_DDL]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/eval/test_comparison.py -v`
Expected: PASS — 8 passed

- [ ] **Step 5: Commit**

```bash
git add src/eval_harness/comparison.py src/eval_harness/store.py tests/eval/test_comparison.py
git commit -m "feat(P2): comparison record, ten blocks always, deferral separate, no aggregate"
```

---

### Task 13: Shadow mode (Done-means 9)

**Files:**
- Create: `src/eval_harness/shadow.py`
- Modify: `src/eval_harness/store.py` — add `shadow.SHADOW_DDL` to `_ddl_scripts`
- Test: `tests/eval/test_shadow.py`

**Interfaces:**
- Consumes: `replay_bundle` (Task 9); `assert_run` (Task 10); `attribute_run` (Task 11); `compare_runs`, `get_comparison` (Task 12).
- Produces: `run_shadow(conn, bundle_id, *, version_tuple, budget_ceilings, run_settings, adapters, live_run_id, select, model_call_audit_refs=()) -> str`, `shadow_record(conn, shadow_run_id) -> dict`, `record_adjudication(conn, shadow_run_id, *, subject_ref, dimension, reviewer_verdict, note=None) -> int`, `adjudications(conn, shadow_run_id) -> list[sqlite3.Row]`, `assert_shadow_wrote_nothing(conn, shadow_run_id) -> None`, `UnauditedModelCall`, `ShadowWroteLiveState`.

**The three empties are proved, not promised.** §8.5: shadow mode generates parallel recommendations *"without changing the user-visible tree or move plan."* `plan_version_writes`, `move_plan_entries` and `user_visible_tree_delta` are columns on the shadow record that must be empty, and `assert_shadow_wrote_nothing` raises `ShadowWroteLiveState` if any is not. **P10 and P12 do not exist**, so nothing can write a plan version or a move plan today — which is exactly why the check is built now: the day P10 lands, a shadow adapter that writes one fails this assertion instead of shipping.

**Everything a shadow run writes goes into `shadow_namespace`.** SPEC Cross-cutting answers → Provenance: replay's derived outputs go to a run-scoped namespace and shadow outputs to `shadow_namespace`. The namespace is the run id, recorded explicitly so a reader never has to infer it. **Whether replay may write *any* derived evidence into the shared database is SPEC Open question 7 and is not answered here:** P2 writes nothing outside its own tables, which is compatible with either answer.

**A shadow model call is still a model call.** §8.4: every model call is gated by P7 before content reaches the model and recorded in the consent-aware audit record. P2 does not write that record — it requires it and links to it. `run_shadow` refuses when `run_settings["model_enabled"]` is true and `model_call_audit_refs` is empty, because a shadow run that made model calls with nothing to link to is the exact gap Done-means 9's audit clause exists to catch. **P7 does not exist**, so the refs are opaque strings today; when P7 lands they are its `audit_id` values, resolved against its record rather than trusted.

**The selection criterion is not P2's to choose.** SPEC Open question 12: §8.5 says shadow mode surfaces *"only selected examples for human review"* and states no criterion. `select` is a **required parameter with no default** — a callable taking the disagreement list and returning the subset. P2 supplies no implementation, not even a trivial one, because a default would be an answer. Done-means 9's *"surfaced-example set"* is whatever the caller's selector returns.

**An adjudication is run-scoped and does not become an §8.7 correction.** SPEC Cross-cutting answers → Correction learning: promoting it *"would make the shadow run change user-visible state, which is the one thing §8.5 says shadow mode must not do"*, and whether promotion is nonetheless permitted is Open question 10. `record_adjudication` writes to P2's own table, appends no `events` row, and there is no promotion function. The test asserts the `events` table is untouched.

**Shadow gets no budget of its own.** SPEC Open question 8 asks whether it should; §8.6's ceiling list has no shadow entry. `run_shadow` takes the same `budget_ceilings` a replay takes and P2 adds no ceiling key. When OQ8 closes, the key is added to P1's `CEILING_KEYS`, not invented here.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_shadow.py
import pytest
from database_agent.db import create_schema

from eval_harness.assertions import assert_run
from eval_harness.attribution import attribute_run
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.replay import ReplayContext, StageResult, replay_bundle
from eval_harness.shadow import (
    ShadowWroteLiveState, UnauditedModelCall, adjudications,
    assert_shadow_wrote_nothing, record_adjudication, run_shadow, shadow_record,
)
from eval_harness.stage_output import DimensionValue
from eval_harness.store import create_eval_schema


def _tuple(**overrides):
    fields = dict(extractor_versions={}, graph_algorithm_version=None,
                  prompt_fingerprint=None, model_identifier=None,
                  template_library_version=None, placement_scorer_version=None,
                  analysis_tiers_enabled=["filesystem"])
    fields.update(overrides)
    return fields


def _settings(**overrides):
    s = {"model_enabled": False, "embeddings_enabled": False}
    s.update(overrides)
    return s


def _bundle(conn):
    bundle_id = open_bundle(conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    add_expectation(conn, bundle_id, dimension="placement", subject_ref="file-1",
                    expected_value={"node_id": "n-right"},
                    expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(conn, bundle_id)
    return bundle_id


def _places(node_id):
    def adapter(ctx: ReplayContext):
        return [StageResult(subject_ref="file-1", outcome="produced", payload=None,
                            inputs=[], budget_state="within_ceiling",
                            values=[DimensionValue("placement", "file-1", "produced",
                                                   {"node_id": node_id})])]
    return adapter


def _live(conn, bundle_id):
    run_id = replay_bundle(conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"placement_scoring": _places("n-wrong")})
    assert_run(conn, run_id)
    attribute_run(conn, run_id)
    return run_id


def _select_all(disagreements):
    """A fixture selector. SPEC Open question 12 is open: P2 ships none."""
    return list(disagreements)


def test_a_shadow_run_produces_a_disagreement_set_and_a_surfaced_set(eval_conn):
    # Done-means 9.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    live = _live(eval_conn, bundle_id)
    shadow_id = run_shadow(eval_conn, bundle_id, version_tuple=_tuple(
        placement_scorer_version="scorer-2"), budget_ceilings={},
        run_settings=_settings(),
        adapters={"placement_scoring": _places("n-right")},
        live_run_id=live, select=_select_all)
    record = shadow_record(eval_conn, shadow_id)
    assert record["disagreement_set"]
    assert record["disagreement_set"][0]["subject_ref"] == "file-1"
    assert record["surfaced_examples"] == record["disagreement_set"]
    assert record["shadow_namespace"] == shadow_id


def test_the_three_empties_are_provable(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    live = _live(eval_conn, bundle_id)
    shadow_id = run_shadow(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"placement_scoring": _places("n-right")},
                           live_run_id=live, select=_select_all)
    record = shadow_record(eval_conn, shadow_id)
    assert record["plan_version_writes"] == []
    assert record["move_plan_entries"] == []
    assert record["user_visible_tree_delta"] == []
    assert_shadow_wrote_nothing(eval_conn, shadow_id)     # does not raise


def test_a_shadow_run_that_wrote_live_state_is_caught(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    live = _live(eval_conn, bundle_id)
    shadow_id = run_shadow(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"placement_scoring": _places("n-right")},
                           live_run_id=live, select=_select_all)
    eval_conn.execute(
        "UPDATE shadow_run SET move_plan_entries = '[\"move-1\"]' "
        "WHERE shadow_run_id = ?", (shadow_id,))
    with pytest.raises(ShadowWroteLiveState):
        assert_shadow_wrote_nothing(eval_conn, shadow_id)


def test_a_model_enabled_shadow_run_needs_its_audit_refs(eval_conn):
    # §8.4: every model call is recorded in the consent-aware audit record. P2
    # requires the reference; P7 writes the record.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    live = _live(eval_conn, bundle_id)
    with pytest.raises(UnauditedModelCall):
        run_shadow(eval_conn, bundle_id, version_tuple=_tuple(model_identifier="m1"),
                   budget_ceilings={}, run_settings=_settings(model_enabled=True),
                   adapters={}, live_run_id=live, select=_select_all)
    shadow_id = run_shadow(
        eval_conn, bundle_id, version_tuple=_tuple(model_identifier="m1"),
        budget_ceilings={}, run_settings=_settings(model_enabled=True), adapters={},
        live_run_id=live, select=_select_all, model_call_audit_refs=["audit-1"])
    assert shadow_record(eval_conn, shadow_id)["model_call_audit_refs"] == ["audit-1"]


def test_the_selector_is_required_and_p2_ships_none(eval_conn):
    # SPEC Open question 12: "By what criterion are shadow examples selected?"
    # A default here would be an answer.
    import inspect

    from eval_harness import shadow
    parameter = inspect.signature(shadow.run_shadow).parameters["select"]
    assert parameter.default is inspect.Parameter.empty
    for name, fn in inspect.getmembers(shadow, inspect.isfunction):
        assert "select" not in name or name == "run_shadow", name


def test_an_adjudication_is_run_scoped_and_appends_no_event(eval_conn):
    # SPEC Open question 10 is OPEN. Promoting an adjudication into an §8.7
    # correction would give shadow mode a path into user-visible state.
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    live = _live(eval_conn, bundle_id)
    shadow_id = run_shadow(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"placement_scoring": _places("n-right")},
                           live_run_id=live, select=_select_all)
    before = eval_conn.execute("SELECT count(*) AS n FROM events").fetchone()["n"]
    record_adjudication(eval_conn, shadow_id, subject_ref="file-1",
                        dimension="placement", reviewer_verdict="candidate_better",
                        note="fixture")
    after = eval_conn.execute("SELECT count(*) AS n FROM events").fetchone()["n"]
    assert after == before
    row = adjudications(eval_conn, shadow_id)[0]
    assert row["shadow_run_id"] == shadow_id      # run scope, not file scope
    assert row["reviewer_verdict"] == "candidate_better"


def test_there_is_no_promotion_path_to_a_correction(eval_conn):
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness"
    for path in src.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "append_event" not in text, path.name
        assert "correction_scope" not in text, path.name


def test_shadow_adds_no_ceiling_key_of_its_own():
    # SPEC Open question 8 is OPEN: §8.6's list has no shadow entry.
    from database_agent.budget import CEILING_KEYS
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness" / "shadow.py"
    text = src.read_text(encoding="utf-8")
    assert "shadow.max" not in text
    assert len(CEILING_KEYS) == 15
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/eval/test_shadow.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_harness.shadow'`

- [ ] **Step 3: Write the implementation**

```python
# src/eval_harness/shadow.py
"""Contract out §8 — shadow mode.

§8.5: "A new model or algorithm can generate parallel recommendations without
changing the user-visible tree or move plan." The three things that must stay
empty are columns, checked by `assert_shadow_wrote_nothing`, not promises.

P2 chooses no selection criterion (SPEC Open question 12), promotes no
adjudication into an §8.7 correction (Open question 10), and adds no shadow budget
key (Open question 8).
"""
from __future__ import annotations

import json
import sqlite3
from typing import Callable, Iterable, Mapping, Sequence

from eval_harness.store import canonical_json

SHADOW_DDL = """
CREATE TABLE IF NOT EXISTS shadow_run (
    shadow_run_id          TEXT PRIMARY KEY REFERENCES run_manifest (run_id),
    live_run_id            TEXT NOT NULL REFERENCES run_manifest (run_id),
    comparison_id          TEXT NOT NULL,
    shadow_namespace       TEXT NOT NULL,
    plan_version_writes    TEXT NOT NULL DEFAULT '[]',   -- MUST be empty (§8.8)
    move_plan_entries      TEXT NOT NULL DEFAULT '[]',   -- MUST be empty (§8.3)
    user_visible_tree_delta TEXT NOT NULL DEFAULT '[]',  -- MUST be empty (§8.5)
    surfaced_examples      TEXT NOT NULL,
    model_call_audit_refs  TEXT NOT NULL                 -- P7's audit ids (§8.4)
);
CREATE TABLE IF NOT EXISTS review_adjudication (
    adjudication_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    shadow_run_id    TEXT NOT NULL REFERENCES shadow_run (shadow_run_id),
    subject_ref      TEXT NOT NULL,
    dimension        TEXT NOT NULL,
    reviewer_verdict TEXT NOT NULL,
    note             TEXT
);
"""

#: The three columns §8.5, §8.3 and §8.8 require to stay empty.
EMPTY_COLUMNS: tuple[str, ...] = (
    "plan_version_writes", "move_plan_entries", "user_visible_tree_delta",
)


class UnauditedModelCall(Exception):
    """A model-enabled shadow run carried no §8.4 audit reference."""


class ShadowWroteLiveState(Exception):
    """A shadow run changed the user-visible tree, a plan version, or the move plan."""


def run_shadow(conn: sqlite3.Connection, bundle_id: str, *, version_tuple: dict,
               budget_ceilings: Mapping[str, int], run_settings: Mapping[str, bool],
               adapters: Mapping[str, object], live_run_id: str,
               select: Callable[[list], Sequence],
               model_call_audit_refs: Iterable[str] = ()) -> str:
    """Run a bundle in shadow and compare it with the live run. Returns the run id.

    `select` has no default. §8.5 surfaces "only selected examples for human
    review" and states no criterion; SPEC Open question 12 is open, and a default
    here would answer it.

    The same `budget_ceilings` a replay takes: §8.6's list has no shadow entry and
    P2 adds no key (Open question 8).
    """
    from eval_harness.assertions import assert_run
    from eval_harness.attribution import attribute_run
    from eval_harness.comparison import compare_runs, get_comparison
    from eval_harness.replay import replay_bundle

    refs = list(model_call_audit_refs)
    if run_settings.get("model_enabled") and not refs:
        raise UnauditedModelCall(
            "a shadow model call is still a model call: §8.4 records every one in "
            "the consent-aware audit record. P2 does not write that record; it "
            "requires the reference and links to it."
        )
    shadow_run_id = replay_bundle(
        conn, bundle_id, version_tuple=version_tuple,
        budget_ceilings=budget_ceilings, run_settings=run_settings,
        adapters=adapters, run_kind="shadow",
    )
    assert_run(conn, shadow_run_id)
    attribute_run(conn, shadow_run_id)
    comparison_id = compare_runs(conn, live_run_id, shadow_run_id)
    disagreements = get_comparison(conn, comparison_id)["disagreements"]
    surfaced = list(select(disagreements))
    conn.execute(
        "INSERT INTO shadow_run (shadow_run_id, live_run_id, comparison_id, "
        "shadow_namespace, surfaced_examples, model_call_audit_refs) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (shadow_run_id, live_run_id, comparison_id, shadow_run_id,
         canonical_json(surfaced), canonical_json(refs)),
    )
    return shadow_run_id


def shadow_record(conn: sqlite3.Connection, shadow_run_id: str) -> dict:
    from eval_harness.comparison import get_comparison

    row = conn.execute("SELECT * FROM shadow_run WHERE shadow_run_id = ?",
                       (shadow_run_id,)).fetchone()
    if row is None:
        raise KeyError(shadow_run_id)
    return {
        "shadow_run_id": row["shadow_run_id"],
        "live_run_id": row["live_run_id"],
        "shadow_namespace": row["shadow_namespace"],
        "plan_version_writes": json.loads(row["plan_version_writes"]),
        "move_plan_entries": json.loads(row["move_plan_entries"]),
        "user_visible_tree_delta": json.loads(row["user_visible_tree_delta"]),
        "disagreement_set": get_comparison(conn, row["comparison_id"])["disagreements"],
        "surfaced_examples": json.loads(row["surfaced_examples"]),
        "model_call_audit_refs": json.loads(row["model_call_audit_refs"]),
    }


def assert_shadow_wrote_nothing(conn: sqlite3.Connection, shadow_run_id: str) -> None:
    """Done-means 9's three provable empties. Raises rather than reporting."""
    record = shadow_record(conn, shadow_run_id)
    non_empty = [name for name in EMPTY_COLUMNS if record[name]]
    if non_empty:
        raise ShadowWroteLiveState(
            f"shadow run {shadow_run_id} wrote {non_empty}; §8.5 requires parallel "
            "recommendations WITHOUT changing the user-visible tree or move plan"
        )


def record_adjudication(conn: sqlite3.Connection, shadow_run_id: str, *,
                        subject_ref: str, dimension: str, reviewer_verdict: str,
                        note: str | None = None) -> int:
    """The reviewer's verdict on one surfaced disagreement, at RUN scope.

    It judges a candidate algorithm, not a file. It is not promoted into an §8.7
    correction and there is no function here that would: SPEC Open question 10 is
    open, and promotion would give shadow mode a path into user-visible state.
    """
    from eval_harness.vocabulary import check_dimension

    check_dimension(dimension)
    cursor = conn.execute(
        "INSERT INTO review_adjudication (shadow_run_id, subject_ref, dimension, "
        "reviewer_verdict, note) VALUES (?, ?, ?, ?, ?)",
        (shadow_run_id, subject_ref, dimension, reviewer_verdict, note),
    )
    return cursor.lastrowid


def adjudications(conn: sqlite3.Connection, shadow_run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM review_adjudication WHERE shadow_run_id = ? "
        "ORDER BY adjudication_id", (shadow_run_id,)).fetchall()
```

Add to `store.py`'s `_ddl_scripts`:

```python
    from eval_harness import assertions, bundle, comparison, run, shadow, stage_output
    return [bundle.BUNDLE_DDL, run.RUN_DDL, stage_output.STAGE_DDL,
            assertions.ASSERTION_DDL, comparison.COMPARISON_DDL, shadow.SHADOW_DDL]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/eval/test_shadow.py -v`
Expected: PASS — 8 passed

- [ ] **Step 5: Commit**

```bash
git add src/eval_harness/shadow.py src/eval_harness/store.py tests/eval/test_shadow.py
git commit -m "feat(P2): shadow mode with three provable empties, required selector, run-scoped adjudication"
```

---

### Task 14: The adversarial suite A1–A12 as a gate (Done-means 10)

**Files:**
- Create: `src/eval_harness/adversarial.py`
- Create: `tests/eval/fixtures/adversarial/A01.json` … `A12.json` (twelve files)
- Test: `tests/eval/test_adversarial.py`

**Interfaces:**
- Consumes: `open_bundle`, `add_expectation`, `add_extraction_run`, `add_text_unit`, `seal_bundle`, `extraction_runs` (Tasks 5–8); `replay_bundle` (Task 9); `assert_run` (Task 10).
- Produces: `CASE_IDS: tuple[str, ...]` (twelve), `load_case(case_id) -> dict`, `load_all_cases() -> list[dict]`, `build_case_bundle(conn, case) -> str`, `run_case(conn, case, *, adapters, version_tuple, budget_ceilings, run_settings) -> CaseResult`, `run_gate(conn, *, adapters, version_tuple, budget_ceilings, run_settings) -> GateReport`, `CaseResult` and `GateReport` (frozen dataclasses), `MissingCase`.

**A case that could not run is `not_run`, never `pass`.** This is the single most important property of this task. Nine of the ten stages are absent, so most cases cannot execute today; a gate that reported "12 passed" because nothing ran would be worse than no gate. `CaseResult.verdict ∈ pass | fail | not_run`, and `GateReport` reports the three counts separately with **no boolean `passed` attribute** to collapse them into.

**Whether the gate blocks or advises is not decided here.** SPEC Open question 9: §8.5 says a new mechanism *"should run against this suite before it affects a user's live plan"* and does not say whether a failing case blocks, or whether P2 or the release process enforces it. `run_gate` returns a report; it raises nothing, exits nothing, and calls nothing. The wiring to "before it affects a user's live plan" is a release-process obligation that P2 records and does not perform.

**A case passes only when the expected outcome is observed *and* the forbidden outcome is absent.** §8.5's suite is about failure modes, so the forbidden half is the load-bearing half: A1 passes because no `MIT` facet was created, not merely because some other value appeared.

**A9 is assertable today, with no stage at all.** SPEC Contract out §9: A9's *"expected outcome **is** a `capped` run row with its `coverage`"*. That is a query against `bundle_extraction_run[]`, which Task 6 built. `assert_against: "bundle"` marks it; every other case is `assert_against: "stage"` and reports `not_run` until its stage exists. A10's condition — P6's published `no_usable_facts(file_id, content_hash)` read — is a **stage** case, because P6 owns that read and P2 must not reimplement it.

**The case text lives in the fixture files, not in `src/`.** A3's academic-context words (`syllabus`, `lecture`, `credits`, `instructor`, `semester`) come from §3.5 and A4's producer strings from §2.2; they are case *data*. Keeping them out of `src/eval_harness/` is what lets Task 16's vocabulary guard stay strict.

**The twelve cases are enumerated because §8.5 names them; their bodies are authored, not invented.** Each file carries §8.5's wording verbatim, the P2 SPEC's expected and forbidden outcomes verbatim, and the § that states the correct behaviour. **No gazetteer, no template, no threshold, and no numeric limit appears in any of them** — A9's fixture uses P4's own recorded `coverage` numbers from Task 6's fixture, which are example values in P4's SPEC, not §2.7 page limits.

- [ ] **Step 1: Write the twelve case files**

```json
// tests/eval/fixtures/adversarial/A01.json
{"case_id": "A01", "wording": "`MIT` inside \"submit\"", "attacks": "facet matching",
 "sections": ["§3.7 word-boundary matching"], "assert_against": "stage",
 "dimension": "fact", "subject_ref": "A01::essay::school",
 "expected_outcome_kind": "abstained", "expected_value": null,
 "forbidden_value": {"field": "school", "value": "MIT"},
 "text_units": [{"run_id": "A01-run", "container_path": [], "unit_locator": "",
                 "text": "Please submit the completed form.", "length": 33,
                 "truncated": false}],
 "extraction_runs": [{"run_id": "A01-run", "file_id": "A01-file",
                      "content_hash": "sha256:A01", "extractor_name": "text.plain",
                      "extractor_version": "1.0.0", "source_type": "text",
                      "config_fingerprint": "sha256:cfg", "completeness": "complete",
                      "coverage": {"units": "files", "processed": 1, "total": 1},
                      "observation_count": 1}]}
```

```json
// tests/eval/fixtures/adversarial/A02.json
{"case_id": "A02", "wording": "`UNC` inside \"uncertainty\"", "attacks": "facet matching",
 "sections": ["§3.7"], "assert_against": "stage",
 "dimension": "fact", "subject_ref": "A02::paper::school",
 "expected_outcome_kind": "abstained", "expected_value": null,
 "forbidden_value": {"field": "school", "value": "UNC"},
 "text_units": [{"run_id": "A02-run", "container_path": [], "unit_locator": "",
                 "text": "Measurement uncertainty dominates the result.",
                 "length": 44, "truncated": false}],
 "extraction_runs": [{"run_id": "A02-run", "file_id": "A02-file",
                      "content_hash": "sha256:A02", "extractor_name": "text.plain",
                      "extractor_version": "1.0.0", "source_type": "text",
                      "config_fingerprint": "sha256:cfg", "completeness": "complete",
                      "coverage": {"units": "files", "processed": 1, "total": 1},
                      "observation_count": 1}]}
```

```json
// tests/eval/fixtures/adversarial/A03.json
// §8.5 names ZIP codes OR device models; the SPEC requires "at least two
// fixtures, one of each", so this case carries two subjects.
{"case_id": "A03",
 "wording": "course-code patterns that are actually ZIP codes or device models",
 "attacks": "rule-validated facts",
 "sections": ["§3.5 (pattern plus \"syllabus\", \"lecture\", \"credits\", \"instructor\", \"semester\")", "§3.10"],
 "assert_against": "stage", "dimension": "fact",
 "subjects": [
   {"subject_ref": "A03::zip::course", "expected_outcome_kind": "abstained",
    "expected_value": null, "forbidden_value": {"field": "course", "value": "MA 02139"},
    "text": "Ship to Cambridge MA 02139 by Friday."},
   {"subject_ref": "A03::device::course", "expected_outcome_kind": "abstained",
    "expected_value": null, "forbidden_value": {"field": "course", "value": "XPS 13"},
    "text": "Receipt for one XPS 13 laptop."}],
 "extraction_runs": [{"run_id": "A03-run", "file_id": "A03-file",
                      "content_hash": "sha256:A03", "extractor_name": "text.plain",
                      "extractor_version": "1.0.0", "source_type": "text",
                      "config_fingerprint": "sha256:cfg", "completeness": "complete",
                      "coverage": {"units": "files", "processed": 2, "total": 2},
                      "observation_count": 2}]}
```

```json
// tests/eval/fixtures/adversarial/A04.json
{"case_id": "A04",
 "wording": "generic author metadata (`python-docx`, `Mozilla/5.0`, browser producer strings)",
 "attacks": "metadata trust",
 "sections": ["§2.2", "§2.3", "§3.8 (\"avoid using authorship or creator identity as a destination dimension\")"],
 "assert_against": "stage", "dimension": "fact", "subject_ref": "A04::doc::creator",
 "expected_outcome_kind": "produced",
 "expected_value": {"retained_as": "supporting_evidence"},
 "forbidden_value": {"used_as": "destination_dimension"},
 "text_units": [{"run_id": "A04-run", "container_path": [], "unit_locator": "",
                 "text": "Quarterly notes.", "length": 16, "truncated": false}],
 "extraction_runs": [{"run_id": "A04-run", "file_id": "A04-file",
                      "content_hash": "sha256:A04", "extractor_name": "docx.native",
                      "extractor_version": "1.0.0", "source_type": "metadata",
                      "config_fingerprint": "sha256:cfg", "completeness": "complete",
                      "coverage": {"units": "files", "processed": 1, "total": 1},
                      "observation_count": 1, "creator": "python-docx"}]}
```

```json
// tests/eval/fixtures/adversarial/A05.json
{"case_id": "A05", "wording": "multiple institutions in one application essay",
 "attacks": "roles vs entity types",
 "sections": ["§3.8", "§4.8", "§4.9 (\"a university name alone should not create a group\")"],
 "assert_against": "stage", "dimension": "fact", "subject_ref": "A05::essay::roles",
 "expected_outcome_kind": "produced",
 "expected_value": {"facets": ["authored_by", "target_school"], "distinct": true},
 "forbidden_value": {"facets": ["target_school"], "chosen_silently": true},
 "text_units": [{"run_id": "A05-run", "container_path": [], "unit_locator": "",
                 "text": "Written at one university, addressed to another.",
                 "length": 48, "truncated": false}],
 "extraction_runs": [{"run_id": "A05-run", "file_id": "A05-file",
                      "content_hash": "sha256:A05", "extractor_name": "text.plain",
                      "extractor_version": "1.0.0", "source_type": "text",
                      "config_fingerprint": "sha256:cfg", "completeness": "complete",
                      "coverage": {"units": "files", "processed": 1, "total": 1},
                      "observation_count": 2}]}
```

```json
// tests/eval/fixtures/adversarial/A06.json
{"case_id": "A06", "wording": "duplicate suffixes on unrelated files",
 "attacks": "family detection, collision policy",
 "sections": ["§8.3 (\"a content-hash match supports deduplication review; a filename match alone does not\")"],
 "assert_against": "stage", "dimension": "grouping", "subject_ref": "A06::family",
 "expected_outcome_kind": "abstained", "expected_value": null,
 "forbidden_value": {"merged": true, "basis": "filename_match"},
 "extraction_runs": [
   {"run_id": "A06-run-1", "file_id": "A06-file-1", "content_hash": "sha256:A06a",
    "extractor_name": "text.plain", "extractor_version": "1.0.0",
    "source_type": "filesystem", "config_fingerprint": "sha256:cfg",
    "completeness": "complete", "coverage": {"units": "files", "processed": 1, "total": 1},
    "observation_count": 1},
   {"run_id": "A06-run-2", "file_id": "A06-file-2", "content_hash": "sha256:A06b",
    "extractor_name": "text.plain", "extractor_version": "1.0.0",
    "source_type": "filesystem", "config_fingerprint": "sha256:cfg",
    "completeness": "complete", "coverage": {"units": "files", "processed": 1, "total": 1},
    "observation_count": 1}]}
```

```json
// tests/eval/fixtures/adversarial/A07.json
{"case_id": "A07", "wording": "stripped EXIF on messaging-app photographs",
 "attacks": "screenshot detection", "sections": ["§2.6"],
 "assert_against": "stage", "dimension": "fact", "subject_ref": "A07::photo::kind",
 "expected_outcome_kind": "abstained", "expected_value": null,
 "forbidden_value": {"field": "kind", "value": "screenshot"},
 "extraction_runs": [{"run_id": "A07-run", "file_id": "A07-file",
                      "content_hash": "sha256:A07", "extractor_name": "image.native",
                      "extractor_version": "1.0.0", "source_type": "metadata",
                      "config_fingerprint": "sha256:cfg", "completeness": "complete",
                      "coverage": {"units": "files", "processed": 1, "total": 1},
                      "observation_count": 0}]}
```

```json
// tests/eval/fixtures/adversarial/A08.json
{"case_id": "A08", "wording": "screenshots with unreadable OCR",
 "attacks": "residual interpretation", "sections": ["§7.8", "§7.9"],
 "assert_against": "stage", "dimension": "residual", "subject_ref": "A08::screenshot",
 "expected_outcome_kind": "produced", "expected_value": {"outcome": "leave_in_place"},
 "forbidden_value": {"outcome": "return_to_placement"},
 "extraction_runs": [{"run_id": "A08-run", "file_id": "A08-file",
                      "content_hash": "sha256:A08", "extractor_name": "ocr.fixture",
                      "extractor_version": "1.0.0", "source_type": "ocr",
                      "config_fingerprint": "sha256:cfg", "completeness": "complete",
                      "coverage": {"units": "pages", "processed": 1, "total": 1},
                      "observation_count": 0}]}
```

```json
// tests/eval/fixtures/adversarial/A09.json
// The one case assertable from the bundle alone: the expected outcome IS a
// `capped` run row with its coverage (SPEC Contract out §9). Numbers are P4's own
// example values from Task 6's fixture, not §2.7 limits.
{"case_id": "A09", "wording": "long scanned books", "attacks": "OCR budget",
 "sections": ["§2.7", "§8.6", "§2.9"], "assert_against": "bundle",
 "dimension": "extraction", "subject_ref": "A09::book::run",
 "expected_outcome_kind": "produced",
 "expected_value": {"completeness": "capped",
                    "coverage": {"units": "pages", "processed": 40, "total": 312}},
 "forbidden_value": {"completeness": "complete"},
 "extraction_runs": [{"run_id": "A09-run", "file_id": "A09-file",
                      "content_hash": "sha256:A09", "extractor_name": "ocr.fixture",
                      "extractor_version": "1.0.0", "source_type": "ocr",
                      "config_fingerprint": "sha256:cfg", "completeness": "capped",
                      "coverage": {"units": "pages", "processed": 40, "total": 312},
                      "observation_count": 118}]}
```

```json
// tests/eval/fixtures/adversarial/A10.json
{"case_id": "A10", "wording": "documents with corrupted text layers",
 "attacks": "extraction routing", "sections": ["§2.2", "§2.7", "§2.4"],
 "assert_against": "stage", "dimension": "extraction", "subject_ref": "A10::doc::routing",
 "expected_outcome_kind": "produced",
 "expected_value": {"ocr_fallback": true, "triggered_by": "no_usable_facts"},
 "forbidden_value": {"ocr_fallback": true, "triggered_by": "language_quality_heuristic"},
 "extraction_runs": [{"run_id": "A10-run", "file_id": "A10-file",
                      "content_hash": "sha256:A10", "extractor_name": "pdf.native",
                      "extractor_version": "1.0.0", "source_type": "text",
                      "config_fingerprint": "sha256:cfg", "completeness": "partial",
                      "coverage": {"units": "pages", "processed": 4, "total": 4},
                      "observation_count": 0}]}
```

```json
// tests/eval/fixtures/adversarial/A11.json
{"case_id": "A11", "wording": "shared resumes across applications",
 "attacks": "multi-home placement", "sections": ["§6.9"],
 "assert_against": "stage", "dimension": "placement", "subject_ref": "A11::resume",
 "expected_outcome_kind": "produced",
 "expected_value": {"outcome": "place", "destination": {"node_role": "shared-material"}},
 "forbidden_value": {"outcome": "place", "destination": {"node_role": "ordinary"}},
 "extraction_runs": [{"run_id": "A11-run", "file_id": "A11-file",
                      "content_hash": "sha256:A11", "extractor_name": "pdf.native",
                      "extractor_version": "1.0.0", "source_type": "text",
                      "config_fingerprint": "sha256:cfg", "completeness": "complete",
                      "coverage": {"units": "pages", "processed": 2, "total": 2},
                      "observation_count": 3}]}
```

```json
// tests/eval/fixtures/adversarial/A12.json
{"case_id": "A12",
 "wording": "files that legitimately belong to more than one purpose group",
 "attacks": "multi-membership", "sections": ["§4.9", "§3.11", "§6.9"],
 "assert_against": "stage", "dimension": "grouping", "subject_ref": "A12::file",
 "expected_outcome_kind": "produced",
 "expected_value": {"memberships": ["g-1", "g-2"]},
 "forbidden_value": {"memberships": ["g-1"]},
 "extraction_runs": [{"run_id": "A12-run", "file_id": "A12-file",
                      "content_hash": "sha256:A12", "extractor_name": "pdf.native",
                      "extractor_version": "1.0.0", "source_type": "text",
                      "config_fingerprint": "sha256:cfg", "completeness": "complete",
                      "coverage": {"units": "pages", "processed": 1, "total": 1},
                      "observation_count": 4}]}
```

- [ ] **Step 2: Write the failing test**

```python
# tests/eval/test_adversarial.py
import pytest

from eval_harness.adversarial import (
    CASE_IDS, GateReport, build_case_bundle, load_all_cases, load_case, run_case,
    run_gate,
)
from eval_harness.replay import ReplayContext, StageResult
from eval_harness.stage_output import DimensionValue
from eval_harness.store import create_eval_schema


def _tuple():
    return dict(extractor_versions={}, graph_algorithm_version=None,
                prompt_fingerprint=None, model_identifier=None,
                template_library_version=None, placement_scorer_version=None,
                analysis_tiers_enabled=["filesystem"])


def _settings():
    return {"model_enabled": False, "embeddings_enabled": False}


def test_there_are_exactly_twelve_cases():
    # §8.5 names twelve failure modes observed in real corpora.
    assert CASE_IDS == ("A01", "A02", "A03", "A04", "A05", "A06",
                        "A07", "A08", "A09", "A10", "A11", "A12")
    assert len(load_all_cases()) == 12


def test_every_case_has_an_expected_a_forbidden_and_a_section():
    for case in load_all_cases():
        assert case["wording"], case["case_id"]
        assert case["sections"], case["case_id"]
        subjects = case.get("subjects") or [case]
        for subject in subjects:
            assert "expected_outcome_kind" in subject, case["case_id"]
            assert "forbidden_value" in subject, case["case_id"]


def test_a3_carries_two_fixtures_one_zip_and_one_device():
    # SPEC Contract out §9: "at least two fixtures, one of each".
    subjects = load_case("A03")["subjects"]
    assert len(subjects) == 2
    assert {s["subject_ref"] for s in subjects} == {"A03::zip::course",
                                                    "A03::device::course"}


def test_the_gate_with_no_adapters_reports_not_run_and_never_pass(eval_conn):
    # The property this whole task exists for. Nine of the ten stages are absent.
    create_eval_schema(eval_conn)
    report = run_gate(eval_conn, adapters={}, version_tuple=_tuple(),
                      budget_ceilings={}, run_settings=_settings())
    assert isinstance(report, GateReport)
    assert report.not_run_count == 11        # every case but A09, which reads the bundle
    assert report.pass_count == 1
    assert report.fail_count == 0
    assert not hasattr(report, "passed")     # SPEC Open question 9 is OPEN
    assert not hasattr(report, "accuracy")


def test_a9_passes_today_from_the_bundle_alone(eval_conn):
    # SPEC Contract out §9: A9's expected outcome IS a `capped` run row with its
    # coverage. No stage is needed and none exists.
    create_eval_schema(eval_conn)
    result = run_case(eval_conn, load_case("A09"), adapters={},
                      version_tuple=_tuple(), budget_ceilings={},
                      run_settings=_settings())
    assert result.verdict == "pass"
    assert result.case_id == "A09"


def test_a_case_fails_when_the_forbidden_outcome_appears(eval_conn):
    # A01: a school facet from a substring hit inside "submit".
    create_eval_schema(eval_conn)

    def forbidden_adapter(ctx: ReplayContext):
        return [StageResult(subject_ref="A01::essay::school", outcome="produced",
                            payload=None, inputs=[], budget_state="within_ceiling",
                            values=[DimensionValue("fact", "A01::essay::school",
                                                   "produced",
                                                   {"field": "school", "value": "MIT"})])]

    result = run_case(eval_conn, load_case("A01"),
                      adapters={"factual_validation": forbidden_adapter},
                      version_tuple=_tuple(), budget_ceilings={},
                      run_settings=_settings())
    assert result.verdict == "fail"
    assert "forbidden" in result.reason


def test_a_case_passes_when_the_stage_abstains(eval_conn):
    # §3.7's word-boundary rule: no MIT facet is created.
    create_eval_schema(eval_conn)

    def abstaining(ctx: ReplayContext):
        return [StageResult(subject_ref="A01::essay::school", outcome="abstained",
                            payload=None, inputs=[], budget_state="within_ceiling",
                            values=[DimensionValue("fact", "A01::essay::school",
                                                   "abstained", None)])]

    result = run_case(eval_conn, load_case("A01"),
                      adapters={"factual_validation": abstaining},
                      version_tuple=_tuple(), budget_ceilings={},
                      run_settings=_settings())
    assert result.verdict == "pass"


def test_a_deferral_is_not_a_pass_and_not_a_fail(eval_conn):
    # §8.6 again: a budget event is neither quality outcome.
    create_eval_schema(eval_conn)

    def deferring(ctx: ReplayContext):
        return [StageResult(subject_ref="A01::essay::school", outcome="deferred",
                            payload=None, inputs=[], budget_state="ceiling_reached",
                            values=[DimensionValue("fact", "A01::essay::school",
                                                   "deferred", None)])]

    result = run_case(eval_conn, load_case("A01"),
                      adapters={"factual_validation": deferring},
                      version_tuple=_tuple(), budget_ceilings={},
                      run_settings=_settings())
    assert result.verdict == "not_run"
    assert "deferred" in result.reason


def test_the_gate_raises_nothing_and_decides_nothing(eval_conn):
    # SPEC Open question 9: is the gate blocking or advisory, and who enforces it?
    # P2 returns a report. It raises no exception and exits no process.
    import inspect

    from eval_harness import adversarial
    create_eval_schema(eval_conn)
    source = inspect.getsource(adversarial.run_gate)
    assert "raise" not in source
    assert "sys.exit" not in source
    run_gate(eval_conn, adapters={}, version_tuple=_tuple(), budget_ceilings={},
             run_settings=_settings())


def test_case_text_lives_in_fixtures_not_in_source():
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness"
    for path in src.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for term in ("submit", "uncertainty", "python-docx", "Mozilla",
                     "syllabus", "lecture", "instructor", "semester"):
            assert term not in text, f"{path.name} carries case text {term!r}"


def test_a_missing_case_file_is_an_error_not_a_silent_skip(eval_conn):
    from eval_harness.adversarial import MissingCase
    with pytest.raises(MissingCase):
        load_case("A13")
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/eval/test_adversarial.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_harness.adversarial'`

- [ ] **Step 4: Write the implementation**

```python
# src/eval_harness/adversarial.py
"""Contract out §9 — the twelve-case adversarial suite, as a gate.

§8.5: "Every new extractor, model, prompt, or graph mechanism should run against
this suite before it affects a user's live plan."

A case that could not run is `not_run`, never `pass`. Whether a failing case
BLOCKS the change, and whether P2 or the release process enforces it, is SPEC Open
question 9: `run_gate` returns a report, raises nothing, and decides nothing.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

CASE_IDS: tuple[str, ...] = (
    "A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10", "A11", "A12",
)

_CASE_DIR = (Path(__file__).resolve().parents[2]
             / "tests" / "eval" / "fixtures" / "adversarial")


class MissingCase(Exception):
    """A named case has no fixture file. Never treated as a skip."""


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    verdict: str          # pass | fail | not_run
    reason: str
    subject_results: tuple


@dataclass(frozen=True)
class GateReport:
    """Per-case results and three counts. No boolean and no aggregate.

    There is deliberately no `passed` attribute: collapsing twelve failure modes
    into one flag is the shape §8.5 rejects, and whether the gate blocks at all is
    Open question 9.
    """
    results: tuple
    pass_count: int
    fail_count: int
    not_run_count: int


def load_case(case_id: str) -> dict:
    path = _CASE_DIR / f"{case_id}.json"
    if not path.exists():
        raise MissingCase(f"no fixture for adversarial case {case_id} at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_all_cases() -> list[dict]:
    return [load_case(case_id) for case_id in CASE_IDS]


def _subjects(case: dict) -> list[dict]:
    """A case is one subject unless it declares several (A03 declares two)."""
    return case.get("subjects") or [case]


def build_case_bundle(conn: sqlite3.Connection, case: dict) -> str:
    """One sealed bundle per case, carrying its fixture rows and its expectations."""
    from eval_harness.bundle import (
        add_expectation, add_extraction_run, add_text_unit, open_bundle, seal_bundle,
    )
    bundle_id = open_bundle(
        conn, corpus_form="snapshot", source_scan_ref=f"{case['case_id']}-scan",
        pinned_plan_id=f"{case['case_id']}-plan", pinned_plan_version="1",
        policy_settings={},
    )
    for row in case.get("extraction_runs", []):
        add_extraction_run(conn, bundle_id, row=row)
    for row in case.get("text_units", []):
        add_text_unit(conn, bundle_id, row=row)
    for subject in _subjects(case):
        add_expectation(
            conn, bundle_id, dimension=case["dimension"],
            subject_ref=subject["subject_ref"],
            expected_value=subject.get("expected_value"),
            expected_outcome_kind=subject["expected_outcome_kind"],
            source="hand-labelled",
        )
    seal_bundle(conn, bundle_id)
    return bundle_id


def _bundle_verdict(conn: sqlite3.Connection, bundle_id: str,
                    case: dict, subject: dict) -> tuple[str, str]:
    """A case assertable from the bundle alone. A9 is the only one today."""
    from eval_harness.bundle import extraction_runs
    from eval_harness.store import canonical_json

    expected = subject["expected_value"]
    forbidden = subject["forbidden_value"]
    for row in extraction_runs(conn, bundle_id):
        observed = {k: row.get(k) for k in expected}
        if canonical_json(observed) == canonical_json(expected):
            if canonical_json({k: row.get(k) for k in forbidden}) == \
                    canonical_json(forbidden):
                return "fail", "forbidden outcome present on the same row"
            return "pass", "expected run row found in the bundle"
    return "fail", "no run row in the bundle matches the expected outcome"


def _stage_verdict(conn: sqlite3.Connection, run_id: str, case: dict,
                   subject: dict) -> tuple[str, str]:
    from eval_harness.store import canonical_json

    row = conn.execute(
        "SELECT outcome, value FROM stage_dimension_value "
        "WHERE run_id = ? AND dimension = ? AND subject_ref = ?",
        (run_id, case["dimension"], subject["subject_ref"])).fetchone()
    if row is None:
        return "not_run", "no stage produced a value for this subject"
    if row["outcome"] in ("not_implemented", "error"):
        return "not_run", f"stage outcome was {row['outcome']}"
    if row["outcome"] == "deferred":
        # §8.6: a budget event is neither a pass nor a failure.
        return "not_run", "stage outcome was deferred (§8.6)"
    observed = None if row["value"] is None else json.loads(row["value"])
    if observed is not None and canonical_json(observed) == \
            canonical_json(subject["forbidden_value"]):
        return "fail", "forbidden outcome was produced"
    if subject["expected_outcome_kind"] == "abstained":
        if row["outcome"] == "abstained":
            return "pass", "abstained as required"
        return "fail", "produced where abstention was required"
    if row["outcome"] != "produced":
        return "fail", f"expected a produced value, got {row['outcome']}"
    if canonical_json(observed) == canonical_json(subject["expected_value"]):
        return "pass", "expected outcome produced, forbidden outcome absent"
    return "fail", "produced value does not match the expected outcome"


def run_case(conn: sqlite3.Connection, case: dict, *, adapters: Mapping[str, object],
             version_tuple: dict, budget_ceilings: Mapping[str, int],
             run_settings: Mapping[str, bool]) -> CaseResult:
    """One case. A case passes only when the expected outcome is observed AND the
    forbidden outcome is absent."""
    from eval_harness.replay import replay_bundle

    bundle_id = build_case_bundle(conn, case)
    run_id = None
    if case["assert_against"] == "stage":
        run_id = replay_bundle(conn, bundle_id, version_tuple=version_tuple,
                               budget_ceilings=budget_ceilings,
                               run_settings=run_settings, adapters=adapters,
                               run_kind="adversarial")
    results = []
    for subject in _subjects(case):
        if case["assert_against"] == "bundle":
            verdict, reason = _bundle_verdict(conn, bundle_id, case, subject)
        else:
            verdict, reason = _stage_verdict(conn, run_id, case, subject)
        results.append((subject["subject_ref"], verdict, reason))
    verdicts = [v for _, v, _ in results]
    if "fail" in verdicts:
        case_verdict, reason = "fail", next(r for _, v, r in results if v == "fail")
    elif "not_run" in verdicts:
        case_verdict, reason = "not_run", next(r for _, v, r in results if v == "not_run")
    else:
        case_verdict, reason = "pass", "every subject passed"
    return CaseResult(case_id=case["case_id"], verdict=case_verdict, reason=reason,
                      subject_results=tuple(results))


def run_gate(conn: sqlite3.Connection, *, adapters: Mapping[str, object],
             version_tuple: dict, budget_ceilings: Mapping[str, int],
             run_settings: Mapping[str, bool]) -> GateReport:
    """All twelve cases. Returns a report and takes no action on it.

    Wiring this to "before it affects a user's live plan" (§8.5) is a release-
    process obligation. Whether a failing case blocks is SPEC Open question 9, and
    P2 does not answer it: this function signals nothing and exits nothing.
    """
    results = tuple(
        run_case(conn, case, adapters=adapters, version_tuple=version_tuple,
                 budget_ceilings=budget_ceilings, run_settings=run_settings)
        for case in load_all_cases()
    )
    return GateReport(
        results=results,
        pass_count=sum(1 for r in results if r.verdict == "pass"),
        fail_count=sum(1 for r in results if r.verdict == "fail"),
        not_run_count=sum(1 for r in results if r.verdict == "not_run"),
    )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/eval/test_adversarial.py -v`
Expected: PASS — 11 passed

- [ ] **Step 6: Commit**

```bash
git add src/eval_harness/adversarial.py tests/eval/fixtures/adversarial tests/eval/test_adversarial.py
git commit -m "feat(P2): twelve adversarial cases as a gate; a case that could not run is never a pass"
```

---

### Task 15: §8.6's count line, from the bundle alone (Done-means 13)

**Files:**
- Create: `src/eval_harness/counts.py`
- Test: `tests/eval/test_counts.py`

**Interfaces:**
- Consumes: `bundle_files`, `extraction_runs` (Tasks 5–6).
- Produces: `bundle_counts(conn, bundle_id) -> dict`, `DEFERRED_COMPLETENESS: frozenset[str]`, `UNREADABLE_COMPLETENESS: frozenset[str]`.

**The mappings are P5's, adopted verbatim.** [`../P5-extractors/SPEC.md`](../P5-extractors/SPEC.md) publishes them for §8.6's sentence *"1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs deferred after the OCR limit; 34 files require model review; 18 files remain unreadable"*: **fully extracted** = files whose every run is `complete`; **deferred** = runs at `deferred` **or** `capped`; **unreadable** = runs at `unreadable` **or** `failed`. P2 restates none of them differently and computes none of them from the observations.

**"Files indexed" is reported twice, because the two sources say different things.** P2's own Contract out §3 says *"1,842 files indexed" (the `bundle_file_entry[]` count)*, while P5's mapping — which the same paragraph says is *"adopted verbatim"* — says **indexed** = files with any run. Those are not the same number when a bundle carries a file no extractor ran against. **This plan does not pick one.** `bundle_counts` returns `files_indexed` (the entry count, as P2's SPEC instructs) **and** `files_with_any_run` (P5's mapping), and the test asserts they can differ. A conflict between two specs is reported, not resolved in code — it is listed in the report accompanying this plan.

**The fifth count is unavailable, not zero.** §8.6's *"34 files require model review"* is a review-state count, not an extraction outcome; P5's mapping says explicitly *"'Files require model review' is P8's count, not P5's."* `bundle_counts` returns `files_requiring_model_review: None`. Following P1's discipline on unmeasured work, `null` keeps it visible as unmeasured and `0` would assert a fact P2 cannot know.

**No live filesystem.** Every count is a query over `bundle_extraction_run[]` and `bundle_file_entry[]`. The test runs with an empty temp directory and asserts nothing on disk is consulted.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_counts.py
import json
from pathlib import Path

from eval_harness.bundle import (
    add_extraction_run, add_file_entry, open_bundle, seal_bundle,
)
from eval_harness.counts import (
    DEFERRED_COMPLETENESS, UNREADABLE_COMPLETENESS, bundle_counts,
)
from eval_harness.store import create_eval_schema

FIXTURES = Path(__file__).parent / "fixtures"


def _bundle_with_runs(conn, runs, *, entries):
    bundle_id = open_bundle(conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    for file_id in entries:
        add_file_entry(conn, bundle_id, file_id=file_id,
                       content_hash=f"sha256:{file_id}", hash_algorithm="sha256",
                       handling_class=None, payload_ref=f"blobs/{file_id}")
    for row in runs:
        add_extraction_run(conn, bundle_id, row=row)
    seal_bundle(conn, bundle_id)
    return bundle_id


def test_the_two_completeness_sets_are_p5s(eval_conn):
    # P5: deferred = runs at `deferred` or `capped`; unreadable = `unreadable` or
    # `failed`. Adopted verbatim, not restated differently.
    assert DEFERRED_COMPLETENESS == frozenset({"deferred", "capped"})
    assert UNREADABLE_COMPLETENESS == frozenset({"unreadable", "failed"})


def test_the_count_line_is_reproducible_from_the_bundle_alone(eval_conn, tmp_path):
    # Done-means 13, with no live filesystem present.
    create_eval_schema(eval_conn)
    runs = json.loads((FIXTURES / "p4_runs.json").read_text(encoding="utf-8"))
    bundle_id = _bundle_with_runs(
        eval_conn, runs, entries=["file-book", "file-syllabus", "file-broken"])
    counts = bundle_counts(eval_conn, bundle_id)
    assert counts["files_indexed"] == 3
    assert counts["files_fully_extracted"] == 1          # only file-syllabus
    assert counts["runs_deferred"] == 1                  # the capped OCR run
    assert counts["runs_unreadable"] == 1                # the unreadable native run
    assert not list(tmp_path.iterdir())


def test_files_requiring_model_review_is_unavailable_not_zero(eval_conn):
    # P5: "'Files require model review' is P8's count, not P5's." A 0 would assert
    # a fact P2 cannot know; None keeps unmeasured work visible as unmeasured.
    create_eval_schema(eval_conn)
    bundle_id = _bundle_with_runs(eval_conn, [], entries=["f1"])
    assert bundle_counts(eval_conn, bundle_id)["files_requiring_model_review"] is None


def test_indexed_is_reported_from_both_sources_because_they_disagree(eval_conn):
    # P2's Contract out §3 says the bundle_file_entry[] count; P5's mapping, which
    # the same paragraph says is adopted verbatim, says "files with any run".
    # This plan reports both and picks neither.
    create_eval_schema(eval_conn)
    runs = [json.loads((FIXTURES / "p4_runs.json").read_text(
        encoding="utf-8"))[1]]                     # only file-syllabus has a run
    bundle_id = _bundle_with_runs(eval_conn, runs,
                                  entries=["file-syllabus", "file-never-extracted"])
    counts = bundle_counts(eval_conn, bundle_id)
    assert counts["files_indexed"] == 2
    assert counts["files_with_any_run"] == 1
    assert counts["files_indexed"] != counts["files_with_any_run"]


def test_a_file_with_one_complete_and_one_capped_run_is_not_fully_extracted(eval_conn):
    # P5: "fully extracted = files whose EVERY run is `complete`." A PDF can have
    # a complete native run and a capped OCR run on the same content hash (I4).
    create_eval_schema(eval_conn)
    runs = [
        {"run_id": "r1", "file_id": "f1", "content_hash": "sha256:f1",
         "extractor_name": "pdf.native", "extractor_version": "1.0.0",
         "source_type": "text", "config_fingerprint": "sha256:c",
         "completeness": "complete",
         "coverage": {"units": "pages", "processed": 2, "total": 2},
         "observation_count": 3},
        {"run_id": "r2", "file_id": "f1", "content_hash": "sha256:f1",
         "extractor_name": "ocr.fixture", "extractor_version": "1.0.0",
         "source_type": "ocr", "config_fingerprint": "sha256:c",
         "completeness": "capped",
         "coverage": {"units": "pages", "processed": 1, "total": 2},
         "observation_count": 1},
    ]
    bundle_id = _bundle_with_runs(eval_conn, runs, entries=["f1"])
    counts = bundle_counts(eval_conn, bundle_id)
    assert counts["files_fully_extracted"] == 0
    assert counts["runs_deferred"] == 1


def test_the_counts_have_no_aggregate_and_no_ratio(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle_with_runs(eval_conn, [], entries=["f1"])
    counts = bundle_counts(eval_conn, bundle_id)
    for key in counts:
        for part in key.split("_"):
            assert part not in {"accuracy", "score", "aggregate", "overall", "rate",
                                "percent", "grade"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/eval/test_counts.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_harness.counts'`

- [ ] **Step 3: Write the implementation**

```python
# src/eval_harness/counts.py
"""§8.6's count line, computed from the bundle alone (Done-means 13).

The mappings are P5's, adopted verbatim: fully extracted = files whose EVERY run
is `complete`; deferred = runs at `deferred` or `capped`; unreadable = runs at
`unreadable` or `failed`. P2 recomputes none of them from the observations.

"Files indexed" is reported from BOTH sources, because P2's own Contract out §3
(the bundle_file_entry[] count) and P5's mapping (files with any run) do not agree
and a plan does not resolve a conflict between two specs.
"""
from __future__ import annotations

import sqlite3

#: P5's mapping. §8.6's "89 scanned PDFs deferred after the OCR limit".
DEFERRED_COMPLETENESS: frozenset[str] = frozenset({"deferred", "capped"})

#: P5's mapping. §8.6's "18 files remain unreadable".
UNREADABLE_COMPLETENESS: frozenset[str] = frozenset({"unreadable", "failed"})


def bundle_counts(conn: sqlite3.Connection, bundle_id: str) -> dict:
    """§8.6's legibility counts, with no live filesystem present.

    `files_requiring_model_review` is None, not 0: it is a review-state count that
    P8 owns, and a zero would assert something P2 cannot know. §8.6 asks that
    unmeasured work stay visible as unmeasured.
    """
    entries = conn.execute(
        "SELECT count(*) AS n FROM bundle_file_entry WHERE bundle_id = ?",
        (bundle_id,)).fetchone()["n"]

    by_file: dict[str, list[str]] = {}
    deferred = unreadable = 0
    for row in conn.execute(
            "SELECT file_id, completeness FROM bundle_extraction_run "
            "WHERE bundle_id = ?", (bundle_id,)):
        by_file.setdefault(row["file_id"], []).append(row["completeness"])
        if row["completeness"] in DEFERRED_COMPLETENESS:
            deferred += 1
        if row["completeness"] in UNREADABLE_COMPLETENESS:
            unreadable += 1

    return {
        # P2 Contract out §3's reading.
        "files_indexed": entries,
        # P5's mapping, which the same paragraph claims to adopt verbatim. The two
        # differ when a bundle carries a file no extractor ran against.
        "files_with_any_run": len(by_file),
        "files_fully_extracted": sum(
            1 for states in by_file.values()
            if states and all(state == "complete" for state in states)),
        "runs_deferred": deferred,
        "runs_unreadable": unreadable,
        # P8's count, not P5's and not P2's.
        "files_requiring_model_review": None,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/eval/test_counts.py -v`
Expected: PASS — 6 passed

- [ ] **Step 5: Commit**

```bash
git add src/eval_harness/counts.py tests/eval/test_counts.py
git commit -m "feat(P2): 8.6 count line from the bundle alone, P5's mappings verbatim, model review unavailable"
```

---

### Task 16: The three guards — no aggregate, no foreign vocabulary, no authorship (Done-means 3)

**Files:**
- Create: `tests/eval/test_no_aggregate.py`

**Interfaces:**
- Consumes: the whole `src/eval_harness/` package and every P2 table.
- Produces: nothing — these are standing guards, in the spirit of P1's `test_no_interpretation.py`.

**Three properties, each of which a future edit could silently break.**

1. **No aggregate accuracy scalar exists anywhere** (Done-means 3, §8.5). Checked in three places: no P2 **column** name, no **key** of any P2 reader's return value, and no identifier in `src/eval_harness/` matches a forbidden name part. The check splits identifiers on `_` and compares whole parts, so `placement_scorer_version` — a §8.5 axis — passes on `scorer`, while a column called `overall_score` fails on both parts.
2. **P2 carries no other part's closed vocabulary and no expectation content.** No P7 class or mode, no P6 fact-field name, no §7.3 residual template name, no template-library name, no gazetteer entry. The adversarial case text lives in fixture files (Task 14), which is why this can stay strict.
3. **P2 authors nothing.** No `append_event` anywhere, no `events` write, no `correction_scope` write. *"The acting part authors"* — and evaluation acts on no file.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_no_aggregate.py
"""Done-means 3 and the two vocabulary/authorship guards.

§8.5: "A single overall 'accuracy' number hides the mechanism that needs repair."
This is a negative acceptance test, not a style preference.
"""
import ast
from pathlib import Path

from database_agent.db import create_schema

from eval_harness.assertions import verdict_counts
from eval_harness.counts import bundle_counts
from eval_harness.store import EVAL_TABLES, create_eval_schema

SRC = Path(__file__).resolve().parents[2] / "src" / "eval_harness"

#: Whole identifier parts, compared after splitting on "_". `placement_scorer_version`
#: splits to {placement, scorer, version} and is therefore clean; `overall_score`
#: splits to {overall, score} and is not.
FORBIDDEN_PARTS = {
    "accuracy", "score", "aggregate", "overall", "rate", "percent", "grade",
    "f1", "precision", "recall", "total",
}

#: Other parts' closed vocabularies. P2 stores their values; it declares none.
FOREIGN_VOCABULARY = [
    # P7 §8.4 handling classes and operation modes
    "public_low", "personal_non_sensitive", "sensitive_personal",
    "highly_sensitive_credential_bearing", "unreadable_unclassified",
    "local_model", "cloud_assisted",
    # P6 §3.11 domain fact fields
    "target_university", "application_cycle", "artifact_type", "tax_year",
    "capture_year",
    # §7.3 residual template names
    "reference clips", "reading inbox", "review later", "protected records",
    # §3.13 reliability states as P2 vocabulary
    "llm-supported", "user_confirmed",
]


def _identifier_parts(name: str) -> set[str]:
    return {part.lower() for part in name.split("_") if part}


def test_no_p2_column_is_an_aggregate(eval_conn):
    create_eval_schema(eval_conn)
    present = {r["name"] for r in eval_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    # Every table P2 declares has actually been created by now.
    assert set(EVAL_TABLES) <= present, sorted(set(EVAL_TABLES) - present)
    for table in EVAL_TABLES:
        for column in eval_conn.execute(f"PRAGMA table_info({table})"):
            offending = _identifier_parts(column["name"]) & FORBIDDEN_PARTS
            assert not offending, f"{table}.{column['name']}: {offending}"


def test_no_reader_returns_an_aggregate_key(eval_conn):
    from eval_harness.bundle import open_bundle, seal_bundle
    create_eval_schema(eval_conn)
    bundle_id = open_bundle(eval_conn, corpus_form="snapshot",
                            source_scan_ref="s", pinned_plan_id="p",
                            pinned_plan_version="1", policy_settings={})
    seal_bundle(eval_conn, bundle_id)
    for reader_result in (bundle_counts(eval_conn, bundle_id),
                          verdict_counts(eval_conn, "no-such-run")):
        for key in reader_result:
            offending = _identifier_parts(str(key)) & FORBIDDEN_PARTS
            assert not offending, f"{key}: {offending}"


def test_no_source_identifier_is_an_aggregate():
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                names.append(node.name)
            elif isinstance(node, ast.Name):
                names.append(node.id)
            for name in names:
                offending = _identifier_parts(name) & FORBIDDEN_PARTS
                assert not offending, f"{path.name}: {name} -> {offending}"


def test_no_string_literal_is_the_word_accuracy():
    # §8.5's sentence is quoted in comparison.py's docstring and must stay there.
    # What may not exist is a string that IS the word — a field name, a key, a
    # column. The AST distinguishes the two; a substring search cannot.
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                assert node.value.strip().lower() != "accuracy", path.name


def test_p2_declares_no_other_parts_vocabulary():
    offenders = []
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        for term in FOREIGN_VOCABULARY:
            if term in text:
                offenders.append(f"{path.name}: {term!r}")
    assert not offenders, "P2 declared another part's vocabulary: " + "; ".join(offenders)


def test_p2_ships_no_expectation_content():
    # SPEC Deferred: the hand-labelled reference corpus, the template library, the
    # gazetteer and the residual library are hand work. P2 publishes
    # bundle_expectation; it does not fill it. Every expected value P2 handles
    # arrives as an argument, so a LITERAL one in source would be P2 authoring it.
    assert not list(SRC.rglob("*.json"))
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg == "expected_value":
                assert not isinstance(node.value, (ast.Dict, ast.List)), \
                    f"{path.name}: a literal expected_value"


def test_p2_appends_no_event_and_writes_no_correction(eval_conn):
    # "The acting part authors" — and evaluation acts on no file. §8.2's event
    # list is a list of things that happen TO a file.
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "append_event" not in text, path.name
        assert "INSERT INTO events" not in text, path.name
        assert "correction_scope" not in text, path.name
    assert eval_conn.execute("SELECT count(*) AS n FROM events").fetchone()["n"] == 0


def test_p2_never_deletes_from_events():
    # I6 (tombstone vs append) is deferred to P7. Nothing here forecloses it, and
    # nothing here deletes provenance.
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        assert "delete from events" not in text, path.name


def test_the_whole_suite_runs():
    # A reminder for the executor, not an assertion: run `pytest -q` before the
    # commit below.
    assert True
```

- [ ] **Step 2: Run the guard**

Run: `pytest tests/eval/test_no_aggregate.py -v`
Expected: PASS — 9 passed. If a guard FAILS, remove the offending name from the source; **do not add it to the allow set.**

- [ ] **Step 3: Run the whole suite**

Run: `pytest -q`
Expected: PASS — P1's tests and P2's Tasks 1–16.

- [ ] **Step 4: Commit**

```bash
git add tests/eval/test_no_aggregate.py
git commit -m "test(P2): guards against an aggregate scalar, a foreign vocabulary, and authorship"
```

---

### Task 17: The walking-skeleton P2 step (Done-means 11)

**Files:**
- Create: `tests/eval/test_skeleton_p2_step.py`

**Interfaces:**
- Consumes: everything above; P1's `create_schema`, `observe_path`, `hash_file`, `all_ceilings`.
- Produces: the integration test every later part must keep green.

**[`../../02-segmentation-map.md`](../../02-segmentation-map.md)'s P2 line is one sentence:** *"the whole run replays from a bundle and asserts each stage's output."* The skeleton is deterministic — *"No LLM, no cloud, no embeddings"* — so the run declares `model_enabled = False` and `embeddings_enabled = False`, and its `analysis_tiers_enabled` is `{filesystem, native}`. An OCR-on replay would be a different tuple (I4), which is the point of the field.

**Nine stages are absent and the run is still a run.** Done-means 7 and Done-means 11 meet here: the skeleton captures a bundle from P1's real substrate, replays it with one minimal extraction adapter, and gets nine `not_implemented` stage outputs, one asserted dimension, and nine `not_run` verdicts. When P4/P5 land, the fixture adapter is replaced by the real stage and this test keeps its shape.

**The bundle is captured from P1's tables and replayed with no filesystem read.** The file is written, hashed and recorded through P1 (with a P3 fixture as the author — *the acting part authors, P1 writes*), the bundle records the resulting identity, and then the source file is **deleted** before the replay. §8.5's *"without touching a live filesystem"* is asserted rather than assumed.

- [ ] **Step 1: Write the failing test**

```python
# tests/eval/test_skeleton_p2_step.py
"""The walking skeleton's P2 step (02-segmentation-map.md):
"the whole run replays from a bundle and asserts each stage's output."

Deterministic: no model, no cloud, no embeddings. Nine of the ten stages are
absent, which is a valid run with nine not_run verdicts.
"""
from pathlib import Path

from database_agent.budget import all_ceilings
from database_agent.db import create_schema
from database_agent.files_table import get_file, observe_path

from eval_harness.assertions import assert_run, assertions, verdict_counts
from eval_harness.attribution import attribute_run
from eval_harness.bundle import (
    add_expectation, add_extraction_run, add_file_entry, add_text_unit, open_bundle,
    seal_bundle,
)
from eval_harness.counts import bundle_counts
from eval_harness.replay import ReplayContext, StageResult, replay_bundle
from eval_harness.stage_output import DimensionValue, stage_outputs
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import DIMENSIONS, STAGE_IDS


def test_skeleton_p2_step(eval_conn, tmp_path: Path):
    create_schema(eval_conn)
    create_eval_schema(eval_conn)

    # ---- P1's step: one PDF whose title carries a course code. P3's fixture
    # authors the scan events; P1 writes (M8).
    document = tmp_path / "corpus" / "syllabus-fixture.pdf"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_bytes(b"%PDF-1.4 COMS 4995 syllabus fixture bytes")
    file_id = observe_path(
        eval_conn, document, author="P3", component_version="p3-fixture",
        # R2 is P3's to compute once (O5); P1 stores it and derives none of it, so
        # the fixture standing in for P3 supplies it. P1's signature requires these
        # with no default — a default would let P1 re-derive them silently.
        **p3_basic_record(document),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="scanned", materialized=True,
    )
    content_hash = get_file(eval_conn, file_id)["content_hash"]

    # ---- P2's step, part one: capture the bundle.
    bundle_id = open_bundle(
        eval_conn, corpus_form="snapshot", source_scan_ref="skeleton-scan",
        pinned_plan_id="skeleton-plan", pinned_plan_version="1",
        policy_settings={"privacy_mode": "offline",
                         "placement_policy": "skeleton-policy",
                         "budget_ceilings": all_ceilings(eval_conn)},
    )
    add_file_entry(eval_conn, bundle_id, file_id=file_id, content_hash=content_hash,
                   hash_algorithm="sha256", handling_class=None,
                   payload_ref="blobs/skeleton")
    add_extraction_run(eval_conn, bundle_id, row={
        "run_id": "skeleton-run", "file_id": file_id, "content_hash": content_hash,
        "extractor_name": "pdf.native", "extractor_version": "1.0.0",
        "source_type": "text", "config_fingerprint": "sha256:cfg",
        "completeness": "complete",
        "coverage": {"units": "pages", "processed": 1, "total": 1},
        "observation_count": 1})
    add_text_unit(eval_conn, bundle_id, row={
        "run_id": "skeleton-run", "container_path": [], "unit_locator": "",
        "text": "COMS 4995 syllabus", "length": 18, "truncated": False})
    add_expectation(eval_conn, bundle_id, dimension="extraction",
                    subject_ref=content_hash,
                    expected_value={"text": "COMS 4995 syllabus"},
                    expected_outcome_kind="produced", source="hand-labelled")
    add_expectation(eval_conn, bundle_id, dimension="placement",
                    subject_ref=file_id, expected_value={"node_id": "n-academics"},
                    expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(eval_conn, bundle_id)

    # §8.5: "without touching a live filesystem". The source is gone from here on.
    document.unlink()
    assert not document.exists()

    # ---- P2's step, part two: replay. One minimal stage, nine absent.
    def extraction_from_the_bundle(ctx: ReplayContext):
        from eval_harness.bundle import text_units
        unit = text_units(ctx.conn, ctx.bundle_id, run_id="skeleton-run")[0]
        return [StageResult(
            subject_ref=content_hash, outcome="produced",
            payload='{"stands in for P4/P5": true}', inputs=[],
            budget_state="within_ceiling",
            values=[DimensionValue("extraction", content_hash, "produced",
                                   {"text": unit["text"]})])]

    run_id = replay_bundle(
        eval_conn, bundle_id,
        version_tuple=dict(extractor_versions={"pdf.native": "1.0.0"},
                           graph_algorithm_version=None, prompt_fingerprint=None,
                           model_identifier=None, template_library_version=None,
                           placement_scorer_version=None,
                           analysis_tiers_enabled=["filesystem", "native"]),
        budget_ceilings=all_ceilings(eval_conn),
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        adapters={"extraction": extraction_from_the_bundle},
    )

    # ---- assert each stage's output.
    outputs = {r["stage_id"]: r for r in stage_outputs(eval_conn, run_id)}
    assert set(outputs) == set(STAGE_IDS)
    assert outputs["extraction"]["outcome"] == "produced"
    assert sum(1 for r in outputs.values() if r["outcome"] == "not_implemented") == 9

    assert assert_run(eval_conn, run_id) == 2
    attribute_run(eval_conn, run_id)
    by_dimension = {r["dimension"]: r for r in assertions(eval_conn, run_id)}
    assert by_dimension["extraction"]["verdict"] == "match"
    assert by_dimension["extraction"]["attributed_stage"] is None
    # The absent stage yields not_run, not a failure (Done-means 7).
    assert by_dimension["placement"]["verdict"] == "not_run"
    assert by_dimension["placement"]["attributed_stage"] is None

    counts = verdict_counts(eval_conn, run_id)
    assert counts == {"match": 1, "not_run": 1}
    assert "divergent" not in counts

    # §8.6's count line, from the bundle, with the corpus deleted (Done-means 13).
    assert bundle_counts(eval_conn, bundle_id) == {
        "files_indexed": 1, "files_with_any_run": 1, "files_fully_extracted": 1,
        "runs_deferred": 0, "runs_unreadable": 0,
        "files_requiring_model_review": None,
    }

    # Every dimension is representable even when only two were asserted.
    assert len(DIMENSIONS) == 10
```

- [ ] **Step 2: Run test to verify it passes**

Run: `pytest tests/eval/test_skeleton_p2_step.py -v`
Expected: PASS — 1 passed. It FAILS if any prior task is incomplete, or if P1's `observe_path` is not yet built.

- [ ] **Step 3: Run the full suite one final time**

Run: `pytest -q`
Expected: PASS — P1's suite plus P2's Tasks 1–17.

- [ ] **Step 4: Commit**

```bash
git add tests/eval/test_skeleton_p2_step.py
git commit -m "test(P2): walking-skeleton P2 step, nine stages absent, corpus deleted before replay"
```

---

## Self-Review

**Spec coverage.** Every Contract-out section has a task: §1 the ten stages → Task 2, §2 the ten dimensions → Task 2, §3 the replay bundle → Tasks 5–8, §4 the stage output envelope → Task 4, §5 the run manifest → Task 3, §6 the assertion record → Tasks 10–11, §7 the comparison record → Task 12, §8 shadow mode → Task 13, §9 the adversarial suite → Task 14. Done-means 1–13 map as: 1→T5/T6, 2→T2/T10/T12, 3→T12/T16, 4→T11, 5→T10, 6→T10/T12, 7→T9/T10, 8→T12, 9→T13, 10→T14, 11→T17, 12→T8/T10, 13→T15.

**Open questions this plan does not answer.** All twelve stay open, and each is held open by a mechanism rather than by a comment:

| OQ | How it is held open |
|---|---|
| 1 — the two lists do not match | no `STAGE_FOR_DIMENSION` mapping exists; the emitting stage names itself (T2, T4). A test fails if one is added. |
| 2 — no thresholds | `verdict_for` takes no tolerance argument and comparison is exact equality; a test pins its signature (T10). |
| 3 — attribution across subjects | the traversal walks the edges it is given and neither requires nor forbids cross-subject ones; two tests show both behaviours from the same code (T11). |
| 4 — is `tree` an assertion or an observation | `tree` is one of the ten dimensions with an ordinary assertion record and **no special-casing anywhere**; nothing in P2 decides whether its verdict is meaningful. |
| 5 — may a bundle leave the device | there is no export function; `add_text_unit` on a `metadata_safe` bundle raises naming OQ5 rather than allowing or forbidding in silence (T6). |
| 6 — no attribution stage for scan, privacy, apply | `STAGE_IDS` is §8.5's ten and P2 attributes nothing to P3, P7 or P12 (T2). |
| 7 — may replay write to the shared evidence database | P2 writes only its own tables; compatible with either answer (T1, T13). |
| 8 — shadow budget | `run_shadow` takes the same ceilings a replay takes; no shadow ceiling key is added (T13). |
| 9 — blocking or advisory gate | `run_gate` returns a report, raises nothing, has no `passed` attribute; a test asserts its source contains no `raise` (T14). |
| 10 — shadow adjudication → §8.7 correction | `record_adjudication` writes P2's own table, appends no event, and there is no promotion function (T13). |
| 11 — reproducibility of a run | `content_ref` is documented as an identity of the tuple, not a claim about reproducing outputs (T1, T3). |
| 12 — shadow selection criterion | `select` is required with no default and P2 ships no selector (T13). |

**No invented values.** No numeric threshold, no ceiling value, no gazetteer entry, no template name, no domain fact field. The only numbers in the plan are fixture values in tests and P4's own example `coverage` figures copied from its SPEC. Task 3 carries a test that fails if a numeric ceiling literal appears in `src/`.

**No foreign vocabulary declared.** P7's five classes and four modes, P6's fact fields, P11's `outcome` and `abstention_reason` members, §3.13's reliability states and §7.3's residual names are stored as opaque strings and never declared in `src/eval_harness/`. Task 16 is the standing guard. The one closed vocabulary P2 carries beyond its own is I4's four analysis tiers, which P2's Contract out §5 prints inside P2's own record.

**Authorship.** P2 appends no `events` row anywhere — no `append_event` import, no `INSERT INTO events`, no `correction_scope` write. Task 16 asserts all three. Nothing deletes from `events`; I6 is untouched.

**Placeholder scan.** No "TBD", no "add error handling", no "similar to Task N", no angle-bracket placeholder standing in for a real name. Every code step carries complete runnable code, and every unresolved thing is named as unresolved with the open question that owns it.

**Type consistency.** `bundle_id`, `run_id`, `stage_id`, `dimension`, `subject_ref`, `version_tuple_ref`, `budget_ceilings`, `run_settings`, `expected_outcome_kind` and `attributed_stage` are spelled identically in every task. `DimensionValue(dimension, subject_ref, outcome, value)` has the same field order in Tasks 4, 9, 10, 11, 12, 13, 14 and 17. `canonical_json` is the only serializer used for comparison anywhere.

## Known gaps, carried deliberately

- **No neighbour's vocabulary is validated.** `handling_class`, `privacy_mode`, `placement_policy`, the `residual` and `placement` expected values, and P6's reliability states are stored as handed. **A typo in any of them is not caught.** The alternative — retyping six parts' enums into P2 — is the two-vocabularies failure this project has already hit. When each part lands, import its published names and validate against the import; do not retype the strings.
- **`bundle_extraction_run` does not promote `analysis_tier`.** SPEC Contract out §3's enumeration of the run fields P2 carries does not include it, so it survives only inside the verbatim `row`. A run-tier-versus-`analysis_tiers_enabled[]` cross-check is therefore not a column query today. Recommended SPEC addition, recorded in the report and not made.
- **`inputs[]` resolves ambiguously where two stages decided about one subject.** Contract out §4 publishes bare `subject_ref`s; the traversal follows all matches. A `(stage_id, subject_ref)` pair would be unambiguous. Recommended SPEC change, not made.
- **`outcome = error` and `expected_outcome_kind = 'not-applicable'` get a NULL verdict.** §8.5 publishes seven verdicts and defines none for either. P2 mints no eighth name and reports both under `unverdicted`. Recommended SPEC change, not made.
- **"Files indexed" has two definitions and both are reported.** P2's Contract out §3 and P5's adopted mapping disagree. `bundle_counts` returns `files_indexed` and `files_with_any_run` and picks neither.
- **`bundle_learning_record`'s "evidence refs" is §8.2's `explanation`.** P1 publishes one field for *"a structured explanation or evidence reference"*; P2's SPEC names two things. The verbatim `row` carries whatever P1 wrote.
- **Nine of the ten stages are fixtures.** Every adapter in these tests stands in for a part that does not exist. When P4–P11 land, each fixture adapter is replaced by the real stage and the assertions keep their shape — that is the property Task 17 exists to protect.
- **Adversarial cases A1–A8 and A10–A12 report `not_run` until their stage exists.** Only A9 can pass today. That is correct and is the reason `not_run` is never folded into `pass`.
- **P2's own §8.6 ceilings are not implemented.** SPEC Cross-cutting answers names three — bundle count, bundle storage size, adversarial suite wall-clock — and a possible shadow-run model budget under Open question 8. Adding a key requires adding it to P1's `CEILING_KEYS`, which is P1's file, and the values are hand-authored. Not blocking Tasks 1–17.
- **No renderer.** §8.5's user-facing evaluation view is P13's (SPEC Open question 12's partial settlement). P2 publishes records; it renders nothing, and Done-means 3's *"or rendered report"* clause therefore binds P13 as well as P2.
- **Schema migration.** `EVAL_SCHEMA_VERSION` is stamped into `eval_schema_meta` on every `create_eval_schema` and never compared, exactly as P1's `SCHEMA_VERSION` is. The first *change* to a P2 table needs one.

## Execution Handoff

Plan saved to `planning/parts/P2-eval-replay-harness/PLAN.md`. **P1 must be green first** — run `pytest tests/ -q` and confirm before starting Task 1. Two execution options:

1. **Subagent-Driven (recommended)** — a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — execute tasks in this session with checkpoints for review.
