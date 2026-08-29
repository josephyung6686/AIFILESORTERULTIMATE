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
    `canonical_json`, so a module-level import here would be circular.
    """
    from eval_harness import assertions, bundle, comparison, run, shadow, stage_output
    return [bundle.BUNDLE_DDL, run.RUN_DDL, stage_output.STAGE_DDL,
            assertions.ASSERTION_DDL, comparison.COMPARISON_DDL, shadow.SHADOW_DDL]


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
