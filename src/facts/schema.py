# src/facts/schema.py
"""P6's tables, created inside P1's single local database (§0).

P6 owns four — `fields`, `values`, `file_facts`, `unresolved` — and creates none of
anyone else's. `database_agent.db.create_schema` and
`evidence_shape.schema.create_evidence_schema` are separate calls and are never
invoked from here.

Task 2 creates `fields`, Task 3 `values` and Task 4 `file_facts`. Task 5 adds its own
DDL to `_TABLE_DDL`, and Task 19 adds `fact_passes` the same way.
"""
from __future__ import annotations

import sqlite3

from database_agent.supersede import supersede_ddl

#: The `fields` catalogue (SPEC, Table: `fields`). `field_key` is the SPEC's
#: "stable identifier" and the ONLY identifier this table has. An earlier draft
#: carried `field_id` beside it holding the identical string, to satisfy the
#: skeleton and the SPEC at once; brief §17 overruled that -- one concept wears one
#: name -- so the second column is gone rather than kept in sync. `field_key` is the
#: PRIMARY KEY, so a `REFERENCES fields (field_key)` from a child table would bind --
#: `PRAGMA foreign_keys` is ON and an FK to a non-PK/UNIQUE parent raises `foreign key
#: mismatch` at INSERT, not at DDL. Task 3 declines to declare one and says why on
#: `VALUES_DDL`.
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

#: §3.12's `file_facts`: "connects one file to one field and one value while retaining
#: the evidence and reliability state that justify the connection."
#:
#: THE NEGATIVE CONTRACT. No path column, no destination column, no folder column, no
#: node column, no group column -- §3.14 ("A fact such as subject = BUSIB 4300 does not
#: itself dictate one permanent folder path") and §4.3. A reviewer checks it here, and
#: `tests/p6/test_p6_file_facts.py` checks it against `PRAGMA table_info` so a future
#: `destination_node_id` fails on the day it is added.
#:
#: `content_hash` is not in the SPEC's column list and is required: `facts_for_file` is
#: published per file version, and the cache key that carries the hash is a digest and
#: cannot be filtered on. Reported to the lead as a gap in the SPEC's shape.
#:
#: `field_key` is the field key (brief §17). It carries no REFERENCES clause: foreign
#: keys are ON and a parent column that is not PRIMARY KEY or UNIQUE raises `foreign
#: key mismatch` at INSERT. Task 2 now declares `fields.field_key` PRIMARY KEY so the
#: clause would bind, but `get_field` remains the gate the SPEC names and the one that
#: raises a refusal with a name on it. `value_id` DOES reference `"values"`, whose
#: `value_id` is a primary key, so a fact can never cite a value that does not exist.
#:
#: `record_id` is a VIRTUAL projection of `fact_id`, so P1's `mark_superseded` and
#: `chain` -- both `... WHERE record_id = ?` -- address this table unchanged. It stores
#: nothing, cannot diverge, and does not appear in `PRAGMA table_info`. Same device,
#: same reason, as P4's `evidence` table.
FILE_FACTS_DDL = f"""
CREATE TABLE IF NOT EXISTS file_facts (
    fact_id            TEXT PRIMARY KEY,
    record_id          TEXT GENERATED ALWAYS AS (fact_id) VIRTUAL,
    file_id            TEXT NOT NULL,
    content_hash       TEXT NOT NULL,
    field_key          TEXT NOT NULL,
    value_id           TEXT NOT NULL REFERENCES "values" (value_id),
    reliability_state  TEXT NOT NULL,
    origin             TEXT NOT NULL,
    evidence_refs      TEXT NOT NULL,
    cited_quote_refs   TEXT NOT NULL,
    cache_key          TEXT NOT NULL,
    model_identifier   TEXT,
    prompt_fingerprint TEXT,
    internal_score     REAL,
    active             INTEGER NOT NULL,
    {supersede_ddl("file_facts")},
    preferred          INTEGER,
    rejection_reason   TEXT,
    created_at         TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS file_facts_version ON file_facts (file_id, content_hash);
CREATE INDEX IF NOT EXISTS file_facts_field ON file_facts (field_key);
CREATE INDEX IF NOT EXISTS file_facts_value ON file_facts (value_id);
CREATE TRIGGER IF NOT EXISTS file_facts_no_delete
BEFORE DELETE ON file_facts
BEGIN SELECT RAISE(ABORT, 'a fact is superseded by a later fact, never removed (§8.2)'); END;
"""

#: §3.6's abstention (B7). Every column here is in the SPEC's `unresolved` sketch, and
#: nothing else is:
#:
#:   - no `value_id` and no `reliability_state`. Not "nullable" -- ABSENT. A nullable
#:     column is a place someone later writes a value, and then the abstention is a
#:     weak `possible` and SPEC rule 1 is gone.
#:   - no path, destination, folder or group column: the same negative contract
#:     `file_facts` carries (§3.14, §4.3), checkable by reading this DDL alone.
#:   - `cache_key` has the same composition as `file_facts` (§3.4), so an abstention is
#:     invalidated by exactly the events that invalidate a fact -- which is what makes
#:     preamble rule 5's pass 4 supersede a pass-2 refusal instead of ignoring it.
#:
#: `record_id` is a VIRTUAL projection of `unresolved_id`, for the same reason P4's
#: `evidence` table carries one: P1's `mark_superseded` and `chain` are literally
#: `... WHERE record_id = ?`, so the projection lets P1's tested functions be reused
#: verbatim rather than written a second time under a second name. It stores nothing,
#: cannot diverge, and does not appear in `PRAGMA table_info`.
#:
#: No foreign key to `files`. P4 made the same choice for the same reason: P6 must be
#: buildable and testable against P4's nineteen fixtures with no scan, no extractor and
#: no `files` row in existence.
UNRESOLVED_DDL = f"""
CREATE TABLE IF NOT EXISTS unresolved (
    unresolved_id       TEXT PRIMARY KEY,
    file_id             TEXT NOT NULL,
    content_hash        TEXT NOT NULL,
    field_key            TEXT NOT NULL,
    reason              TEXT NOT NULL,
    attempted_producers TEXT NOT NULL,
    evidence_refs       TEXT NOT NULL,
    cache_key           TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    {supersede_ddl("unresolved")},
    record_id           TEXT GENERATED ALWAYS AS (unresolved_id) VIRTUAL
);
CREATE INDEX IF NOT EXISTS unresolved_by_version
    ON unresolved (file_id, content_hash);
"""

#: Task 19's pass record. P6-internal bookkeeping -- not one of the four published
#: records, and read by no other part. `analysis_tiers` is canonical JSON of the
#: sorted tier names, so one pass has one representation.
#:
#: It lives HERE rather than in `facts.usable` because the DDL has to reach
#: `_TABLE_DDL`, and `facts.schema` importing `facts.usable` would close the cycle
#: schema -> usable -> file_facts -> fields -> schema. `facts.usable` imports these
#: two names back; the direction that works is the only one taken.
FACT_PASSES_TABLE: str = "fact_passes"

FACT_PASSES_DDL: str = f"""
CREATE TABLE IF NOT EXISTS {FACT_PASSES_TABLE} (
    pass_id        TEXT PRIMARY KEY,
    file_id        TEXT NOT NULL,
    content_hash   TEXT NOT NULL,
    analysis_tiers TEXT NOT NULL
)
"""

_TABLE_DDL: tuple[str, ...] = (_FIELDS_DDL, VALUES_DDL, FILE_FACTS_DDL, UNRESOLVED_DDL,
                               FACT_PASSES_DDL)


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
