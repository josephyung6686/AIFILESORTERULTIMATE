# P2 Eval/Replay Harness — Plan Review

**(review in progress — findings appended as confirmed; verdict written last)**

Reviewed: `planning/parts/P2-eval-replay-harness/PLAN.md` (5,841 lines, 17 tasks)
Against: `planning/parts/P2-eval-replay-harness/SPEC.md`, `planning/01-product-design-structured.md`
(§8.5/§8.6/§8.8), the live P1 implementation in `src/database_agent/` (150 tests passing at
review time), `planning/10-i4-learning-ops.md`, `planning/11-ops-runtime.md`.

---

## Confirmed findings (running list)

### B1 — BLOCKING — Task 1's `test_p2_creates_no_p1_table` fails against the live `open_database`

**Where:** `PLAN.md` Task 1, Step 1, `tests/eval/test_store.py`:

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

**What:** P1's `open_database` now calls `create_schema` itself — `src/database_agent/db.py:52-56`:

```python
    # Contract out §6 publishes "one local SQLite database ... transactional and
    # inspectable" — a handle whose tables do not exist is not that. create_schema
    # stays public and idempotent for callers that want it explicitly, but no
    # neighbour has to remember a second call to get a usable database.
    create_schema(conn)
```

So the `eval_conn` fixture hands back a connection where `files` and `events` **already exist**.
Verified directly:

```
['budget_ceilings', 'events', 'files', 'learning_resets', 'scan_resource_usage',
 'sqlite_sequence', 'vector_arrays']
files present: True | events present: True
```

The two asserts fail on the first run. Step 5 of the task claims `Expected: PASS — 8 passed`.

**Why blocking:** it is Task 1 — the first task in the plan. An executor following
`superpowers:subagent-driven-development` hits a red test it cannot make green without either
changing P1 (forbidden by the plan's own *"P2 does not modify any P1 file"*) or rewriting the
test. Rewriting a guard test under time pressure is exactly how a guard gets weakened. The
intended guard is still worth keeping — it should assert that P2's *own* schema function creates
no P1 table, e.g. by diffing table names before and after `create_eval_schema`, not by asserting
their absolute absence.

### N1 — non-blocking — Task 6's JSON fixture files are written with `//` comments and will not parse

**Where:** `PLAN.md` Task 6, Step 1 — `tests/eval/fixtures/p4_runs.json` and
`tests/eval/fixtures/p4_text_units.json`, e.g.:

```json
// tests/eval/fixtures/p4_runs.json
// P4 SPEC Record 2 (D5). Field names and example values copied from that record.
// P2 defines none of this shape. Replace with real P4 rows when P4 lands.
[
  {
```

**What:** the test reads them with `json.loads((FIXTURES / name).read_text(encoding="utf-8"))`.
JSON has no comment syntax; an executor writing the block verbatim gets
`JSONDecodeError: Expecting value: line 1 column 1 (char 0)` on the first `_load(...)`.
Verified. The same `# path` marker convention is harmless in the Python blocks and fatal here.

**Why not blocking:** it fails loudly, at the fixture-loading line, with an unambiguous error, and
the fix is to delete three lines. Move the provenance note into the task prose (or into a
`"_comment"` key) rather than the file body.

### N2 — non-blocking — `_DDL_SCRIPTS` vs `_ddl_scripts` (two names for one thing)

**Where:** Task 1 Step 4 defines `def _ddl_scripts() -> list[str]:` in `store.py`. Task 3's *Files*
line says *"Modify: `src/eval_harness/store.py` — append `RUN_DDL` to `_DDL_SCRIPTS`"*, and Task 3
Step 3 says *"Replace the `_DDL_SCRIPTS` placeholder in `store.py`"*. Tasks 4, 5, 10, 12, 13 and 14
all say `_ddl_scripts` correctly. Only prose is affected; every code block is consistent. Rename the
two prose mentions.

### N3 — non-blocking — the P7 forbidden-name guard is spelled two different ways

**Where:** Task 5, `test_p2_source_carries_no_p7_class_or_mode_name` forbids eight names:

```python
    forbidden = ("public_low", "personal_non_sensitive", "sensitive_personal",
                 "highly_sensitive_credential_bearing", "unreadable_unclassified",
                 "local_model", "cloud_assisted", "hybrid")
```

Task 16's guard (PLAN.md:5483-5485) lists the same names **minus `hybrid`**. Two guards for one
rule that disagree on one member is the "one name, one concept" failure in miniature: whichever runs
last defines the rule. Make Task 16 the single owner and have Task 5 import it, or drop `hybrid`
from both (it is an ordinary English word and the likeliest false positive of the eight).

### B2 — BLOCKING — creating `tests/eval/conftest.py` breaks P1's existing suite at collection time

**Where:** `PLAN.md` Task 1, Step 3 creates `tests/eval/conftest.py`, justified as:

> **P2 does not modify any P1 file.** Not `db.py`, not `pyproject.toml`, not `tests/conftest.py`.
> P2's schema function is its own, its fixtures live in `tests/eval/conftest.py`, and its tests live
> in `tests/eval/` so that P1's `tests/conftest.py` stays untouched.

**What:** with pytest's default `prepend` import mode and no `__init__.py` anywhere under `tests/`,
**both** conftest files are imported under the top-level module name `conftest`. The second one
imported wins in `sys.modules`, and P1's five test modules that do `from conftest import
p3_basic_record` then resolve against the wrong file.

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

`tests/test_adversarial.py:56` does the same import inside a function, so it survives collection and
fails at call time instead.

**Why blocking:** Task 1 is the first task, and its own Step 5 (`pytest tests/eval/test_store.py -v`,
"Expected: PASS — 8 passed") plus Task 17 Step 3 (`pytest -q`, "Expected: PASS — P1's suite plus P2's
Tasks 1–17") are the plan's validation gates. After Task 1 the whole suite is *Interrupted*: nothing
runs, P1 goes from 150 green to uncollectable, and every subsequent task is validated against a
suite that does not execute. The failure is also mis-signposted — it reads as a P1 defect.

`--import-mode=importlib` does **not** fix it (P1's `from conftest import …` then raises
`ModuleNotFoundError`, same four errors). The minimal fix that keeps `tests/conftest.py`,
`pyproject.toml` and every P1 test untouched is one empty file:

```
tests/eval/__init__.py
```

which makes the module names `conftest` and `eval.conftest`, keeps `tests/` on `sys.path`, and
leaves `from conftest import p3_basic_record` working from `tests/eval/` as well. Verified: with that
file added, `pytest -q` reports `152 passed` (P1's 150 plus two P2 smoke tests). Add
`tests/eval/__init__.py` to Task 1's *Files* list and to its commit.

### B3 — BLOCKING — Task 17 calls `p3_basic_record` but never imports it

**Where:** `PLAN.md` Task 17, Step 1, `tests/eval/test_skeleton_p2_step.py`. The import block is:

```python
from pathlib import Path

from database_agent.budget import all_ceilings
from database_agent.db import create_schema
from database_agent.files_table import get_file, observe_path

from eval_harness.assertions import assert_run, assertions, verdict_counts
…
```

and the body calls:

```python
    file_id = observe_path(
        eval_conn, document, author="P3", component_version="p3-fixture",
        # R2 is P3's to compute once (O5); P1 stores it and derives none of it, so
        # the fixture standing in for P3 supplies it. …
        **p3_basic_record(document),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="scanned", materialized=True,
    )
```

**What:** `p3_basic_record` is an undefined name in that module — `NameError: name 'p3_basic_record'
is not defined`. It is not a pytest fixture (fixtures are injected as parameters, and this is a bare
call), it is a plain module-level function in **P1's** `tests/conftest.py:23`, and it is *not* in the
`tests/eval/conftest.py` the plan creates in Task 1. Every P1 test that uses it imports it explicitly
— `tests/test_verify.py:6`, `tests/test_identity.py:74`, `tests/test_files_table.py:6`,
`tests/test_skeleton_p1_step.py:11` all carry `from conftest import p3_basic_record`.

**Why blocking:** Task 17 is Done-means 11, the walking-skeleton step, and the one integration test
the plan says "every later part must keep green". It cannot run. The patch that added
`**p3_basic_record(document)` to satisfy the new `observe_path` signature added the call and not the
import.

**The patch is otherwise correct**, and this is worth stating precisely so it is not re-litigated:
the live signature is

```python
def observe_path(conn, path, *, author, component_version, filename,
                 normalized_filename, extension, observed_size, observed_timestamps,
                 parent_folder_context, mime_type, detected_format, scan_state,
                 materialized) -> str:
```

(`src/database_agent/files_table.py:129-142`), and `p3_basic_record` returns exactly
`{filename, normalized_filename, extension, observed_size, observed_timestamps}` — the five required
keywords, no more, no fewer, so `**p3_basic_record(document)` fills them and collides with none of
the explicit arguments. Add `from conftest import p3_basic_record` to the test's imports. That import
resolves only once B2 is fixed.
