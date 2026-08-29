# tests/p10/conftest.py
"""A real P1 database carrying every upstream table P10's tests read.

`open_database` creates EIGHT tables and no more — `budget_ceilings`, `events`,
`files`, `learning_resets`, `scan_resource_usage`, `vector_arrays`,
`vector_embeddings` and `sqlite_sequence`. Verified:

    PYTHONPATH=src python3 -c "import pathlib, tempfile
    from database_agent.db import open_database
    c = open_database(pathlib.Path(tempfile.mkdtemp())/'a.sqlite')
    print(sorted(r[0] for r in c.execute(
        \"select name from sqlite_master where type='table'\")))"

Every other part's tables come from that part's own idempotent creator, and each
one below is here because a named test raises `sqlite3.OperationalError: no such
table` without it:

* `create_fields` -> `fields` (it calls `create_facts_schema` itself, `src/facts/
  fields.py:284`). Task 4's `resolve_role_to_field` reads `get_field` and
  `is_destination_eligible`; C2 cannot be exercised at all without the catalogue.
* `create_scan_schema` -> `corpus_selections`, `directory_inventory`, `scan_runs`.
  Task 4's `record_selection`, `get_selection`, `selection_candidate_roots` and
  `directory_inventory` all read them.
* `create_privacy_schema` -> `classifications`. Task 4's `ClassificationStore
  (conn).current(...)` reads it, and D2's absent-record case is a SELECT that
  must return `None` rather than fail to run.
* `create_eval_schema` -> `version_tuple`, `run_manifest`, `stage_output`,
  `stage_dimension_value`. Task 16's P2 envelopes write all four.

P10's OWN tables are deliberately absent: `create_tree_schema` is Task 2's, and
each suite that needs it calls it explicitly so the schema test can observe a
database both before and after.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from database_agent.db import open_database
from eval_harness.store import create_eval_schema
from facts.fields import create_fields
from privacy.schema import create_privacy_schema
from scan_agent.schema import create_scan_schema


@pytest.fixture()
def conn(tmp_path: Path):
    c = open_database(tmp_path / "agent.sqlite")
    create_fields(c)
    create_scan_schema(c)
    create_privacy_schema(c)
    create_eval_schema(c)
    yield c
    c.close()
