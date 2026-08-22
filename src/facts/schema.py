# src/facts/schema.py
"""P6's tables, created inside P1's single local database (§0).

P6 owns four — `fields`, `values`, `file_facts`, `unresolved` — and creates none of
anyone else's. `database_agent.db.create_schema` and
`evidence_shape.schema.create_evidence_schema` are separate calls and are never
invoked from here.

Task 2 creates `fields` and Task 3 `values`. Tasks 4 and 5 add their own DDL to
`_TABLE_DDL`.
"""
from __future__ import annotations

import sqlite3

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

#: `values` is a SQL keyword -- `CREATE TABLE values (...)` is a syntax error in
#: SQLite, verified on 3.45.3 -- so the identifier is quoted here and at every call
#: site in `facts.values`. It is the only table in the product that needs quoting.
#:
#: `field_key` is the field key, under the name the SPEC's `fields` table publishes
#: for it. The skeleton's `values` / `file_facts` shapes and its `ValueRow` called
#: this `field_id`; brief §17 ruled that the error -- a column named `_id` holding a
#: key is a name that lies about its content.
#:
#: It carries NO `REFERENCES fields (...)` clause, and that is deliberate rather than
#: forgotten. `open_database` leaves `PRAGMA foreign_keys` ON (verified: it reads 1),
#: and Task 2 now declares `fields.field_key` PRIMARY KEY, so a REFERENCES clause
#: WOULD bind. It is still omitted, deliberately: the gate the SPEC actually names is
#: the catalogue lookup. `get_field` raises `FieldNotInCatalogue` before any INSERT
#: reaches here and Task 3's test asserts it, whereas an FK would raise
#: `IntegrityError` from the driver and replace a named refusal with an anonymous
#: one. Adding it is a live option, not an oversight.
#:
#: UNIQUE (field_key, canonical_value) is §3.12's "a value belongs to exactly one
#: field" enforced by the database rather than remembered by a caller.
#:
#: `merged_into` / `merge_reason` are NOT P1's supersede set. A merge is not a
#: supersession: the merged value was not wrong and is not replaced by a better
#: reading of the same evidence -- it is the same entity under another name, which is
#: §0's "taxonomy aliases". The SPEC's sentence for this table says so outright:
#: merges "record an alias, never delete a value (§8.2)". Task 16 owns supersession,
#: for `file_facts`, where a later pass genuinely replaces an earlier conclusion.
VALUES_DDL = """
CREATE TABLE IF NOT EXISTS "values" (
    value_id           TEXT PRIMARY KEY,
    field_key          TEXT NOT NULL,
    canonical_value    TEXT NOT NULL,
    raw_variants       TEXT NOT NULL,
    display_label      TEXT,
    aliases            TEXT NOT NULL,
    origin             TEXT NOT NULL,
    first_evidence_ref TEXT,
    merged_into        TEXT REFERENCES "values" (value_id),
    merge_reason       TEXT,
    UNIQUE (field_key, canonical_value)
);
CREATE INDEX IF NOT EXISTS values_field ON "values" (field_key);
CREATE INDEX IF NOT EXISTS values_merged ON "values" (merged_into);
CREATE TRIGGER IF NOT EXISTS values_no_delete
BEFORE DELETE ON "values"
BEGIN SELECT RAISE(ABORT, 'a merge records an alias; a value is never deleted (§0, §8.2)'); END;
"""

_TABLE_DDL: tuple[str, ...] = (_FIELDS_DDL, VALUES_DDL)


def create_facts_schema(conn: sqlite3.Connection) -> None:
    """Create P6's tables. Idempotent; creates no other part's table.

    Each element of `_TABLE_DDL` is a script, not a statement: `VALUES_DDL` carries a
    table, two indexes and a trigger, and the trigger body contains its own `;`, so it
    can neither be `conn.execute`d nor split on the semicolon. It is therefore
    `executescript`, which is what P1's `create_schema`, P4's `create_evidence_schema`
    and P7's `create_privacy_schema` all do.

    That also settles the transaction question rather than leaving it to taste.
    `executescript` commits any pending transaction before it runs, so wrapping this
    loop in P1's `transaction` boundary raises `OperationalError: cannot commit - no
    transaction is active` at the boundary's own COMMIT -- verified by execution on
    the interpreter's build. Every statement here is `IF NOT EXISTS`, so a partial
    run is completed by the next call rather than needing a rollback.
    """
    for ddl in _TABLE_DDL:
        conn.executescript(ddl)
