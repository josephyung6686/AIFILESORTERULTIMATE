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
