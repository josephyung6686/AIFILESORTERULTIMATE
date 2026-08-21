### Task 3: `values` — auto-create, raw variants, aliases, display labels

**Files:**
- Create: `src/facts/values.py`
- Modify: `src/facts/schema.py` (add `VALUES_DDL`; one line in `create_facts_schema`)
- Test: `tests/p6/test_p6_values.py`

**Interfaces:**
- Consumes: `facts.fields` — `get_field`, `FieldNotInCatalogue`; `evidence_shape.canonical` —
  `canonical_json`, `sha256_of`; `evidence_shape.vocabulary` — `check`, `NotInVocabulary`.
- Produces: `ValueRow(value_id, field_id, canonical_value, raw_variants, display_label, aliases,
  origin, first_evidence_ref)`, `VALUE_ORIGINS: tuple[str, str]` (`automatic`, `user`),
  `ensure_value(conn, *, field_key, canonical_value, first_evidence_ref, origin) -> str`,
  `add_raw_variant(conn, value_id, raw) -> None`,
  `set_display_label(conn, value_id, display_label) -> None`,
  `merge_values(conn, *, keep, merged, reason) -> None`,
  `values_in_field(conn, field_key) -> list[sqlite3.Row]`.

**Done-means:** the positive half of 3 — *"A new value auto-creates on first sight"*.

---

**Three additions to the skeleton's `Produces:` block, each named rather than smuggled.**

1. **`set_display_label`.** The SPEC's `values` shape carries `display_label` — *"the user's preferred
   rendering — `UChicago` (§2.8)"* — and the skeleton's `Produces:` block publishes no function that
   writes it. A column with no producer is the exact defect round 1's F-2 found on
   `sensitivity_status`, so this task publishes the writer rather than leaving the column unreachable
   or setting it by raw SQL inside a test. It is an **addition**, not a rename: every name the
   skeleton lists keeps its spelling and its signature.
2. **`sha256_of`**, from the same module as `canonical_json`. `value_id` is content-addressed (see
   the identity note below) and `canonical_json` alone yields a string, not a digest.
3. **`check` / `NotInVocabulary`.** Global Constraints binds this above the per-task Consumes list:
   *"`unresolved` reasons and `origin` values are P6's own closed vocabularies, published once, in
   one module, checked with P4's `evidence_shape.vocabulary.check(value, vocabulary, *, name)` so a
   bad value raises `NotInVocabulary` rather than being stored."* `VALUE_ORIGINS` is such a
   vocabulary and is checked the same way.

**Two facts verified by execution on 2026-08-22, not read from a document.** Both change the code
below and neither is guessable:

```text
CREATE TABLE values (a TEXT)        ->  sqlite3.OperationalError: near "values": syntax error
CREATE TABLE "values" (a TEXT)      ->  OK          (SQLite 3.45.3, the interpreter's build)
observation_key(content_hash=..., extractor_name=..., locator=..., raw_value=...)
                                    ->  'sha256:' + 64 lowercase hex, 71 characters
canonical_json(('a','b'))           ->  '["a","b"]'      tuples serialize as JSON arrays
canonical_json([])                  ->  '[]'
```

`values` is a SQL keyword. **Every statement in this task spells the table `"values"` with double
quotes**, and it is the only table in the product that needs them. An unquoted one is not a style
slip — it is an `OperationalError` at `create_facts_schema` and therefore at the first test of every
later task in the part.

**The one contradiction this task hits, resolved and reported.** The SPEC's `fields` table (§3.12)
publishes **`field_key`** as its *"stable identifier"* and declares no surrogate key; the SPEC's
`values` and `file_facts` tables, and the skeleton's `ValueRow`, both name the foreign key
**`field_id`**. Two names, one thing. The resolution taken here — and taken identically in Task 4, so
the two cannot drift — is:

> **`field_id` is the column name; the field *key* is the value it holds.** The column is declared
> `field_id TEXT NOT NULL REFERENCES fields (field_key)`, and it is filled from
> `get_field(conn, field_key)["field_key"]` rather than from a surrogate that the `fields` catalogue
> does not publish.

That keeps the skeleton's `ValueRow` field name (a contract with the parallel authors) and the SPEC's
`fields` shape (no invented surrogate) simultaneously true. It is reported to the lead as a naming
collision to settle once, not patched differently in two files.

**Value identity is content-addressed, and that is a decision.** `value_id` is
`sha256_of("facts.values", field_id, canonical_value)` rather than a random UUID. Three consequences,
all wanted: `ensure_value` is idempotent without a read-then-write race; the same corpus produces the
same `value_id` in two different databases, which is what §8.5's replay compares against; and
*"a value belongs to exactly one field (§3.12)"* becomes an arithmetic property of the identifier
rather than a rule someone must remember. P4's `sha256_of` is length-prefixed and injective, so
`("a", "bc")` and `("ab", "c")` do not collide.

**What this task does not build.** §8.8 places the display label and the aliases inside a plan
version — *"§8.8's plan-version record lists 'User labels and aliases' literally, so `UChicago` vs
`University of Chicago` as a rendering choice is plan-versioned while the underlying value and every
fact pointing at it are not."* Task 22 owns `plan_versions.py`. This task stores both columns
**unscoped** and writes no plan-version key; scoping them is Task 22's, and inventing a
`plan_version` keyword here that no caller can supply would be a threshold with no injector.

---

- [ ] **Step 1: Confirm `tests/p6/conftest.py` publishes `p6_conn`, and create it if Wave A has not**

`PLAN-tasks-07-09.md` and `PLAN-tasks-14-15.md` both record the same precondition — *"`tests/p6/conftest.py`
publishes `p6_conn` — P1's database with P4's three tables, P6's own tables, and Task 2's `fields`
catalogue rows created"* — and **no task's `Files:` line owns the file.** That gap is reported to the
lead. Until it is assigned, Task 3 is the first task whose tests need catalogue rows *and* a P6 table
in the same fixture, so it carries the file. If Task 1 or Task 2 has already created it, verify it
matches this content byte for byte and change nothing.

```python
# tests/p6/conftest.py
import pytest

from database_agent.db import create_schema

from evidence_shape.schema import create_evidence_schema

from facts.fields import create_fields
from facts.schema import create_facts_schema


@pytest.fixture()
def p6_conn(conn):
    """P1's database, P4's three tables, P6's own tables, and Task 2's closed field
    catalogue loaded. `conn` is P1's root fixture and `tests/conftest.py` is not
    modified -- the same shape `tests/p4/conftest.py` uses for `p4_conn`."""
    create_schema(conn)
    create_evidence_schema(conn)
    create_facts_schema(conn)
    create_fields(conn)
    return conn
```

- [ ] **Step 2: Write the failing test**

Create `tests/p6/test_p6_values.py` with exactly this content.

Two field keys carry the whole file, and both are chosen because their spelling is **ratified rather
than assumed**: `target_school` and `client` are two of §3.8's four role fields, which Done-means 2's
2026-08-22 amendment puts in the catalogue by name. Using them means this task cannot be broken by a
spelling Task 2 has not published yet, and it makes §3.8's role separation testable in the value
table with two fields that can genuinely hold the same organization name.

```python
# tests/p6/test_p6_values.py
"""§3.12's auto-create rule, §2.8's three renderings, §3.8's role separation seen from
the value table, and §0's taxonomy aliases -- a merge records an alias and deletes
nothing (§8.2).

Every field key used here is one of §3.8's four role fields, whose spelling Done-means
2 ratifies. `target_school` and `client` are two roles that can hold the same
organization name, which is the whole of the §3.12 one-value-one-field test.
"""
import json
import sqlite3

import pytest

from evidence_shape.observation import observation_key
from evidence_shape.vocabulary import NotInVocabulary

from facts.fields import FieldNotInCatalogue
from facts.values import (
    VALUE_ORIGINS,
    ValueRow,
    add_raw_variant,
    ensure_value,
    merge_values,
    set_display_label,
    values_in_field,
)

FIELD = "target_school"
OTHER_FIELD = "client"

#: §2.8's three renderings of one entity, verbatim: "If a document says U Chicago, the
#: raw observation remains exactly that wording, while a resolver may normalize it to
#: University of Chicago and the user may later choose to display it as UChicago."
RAW = "U Chicago"
CANONICAL = "University of Chicago"
DISPLAY = "UChicago"

CONTENT_HASH = "a" * 64


def _key(raw: str, *, locator: str = "heading:page=1/heading=2") -> str:
    """A real P4 observation key, not a hand-written string. Content-addressed, so the
    same wording at the same locator is the same key (M14)."""
    return observation_key(content_hash=CONTENT_HASH,
                           extractor_name="pdf.text",
                           locator=locator,
                           raw_value=raw)


def _row(conn, value_id: str) -> sqlite3.Row:
    """Find a value through the published read only. There is no get-by-id in this
    task's surface, and none is added: `values_in_field` is how a reader reaches a
    value, and a merged value must still be reachable through it."""
    for field_key in (FIELD, OTHER_FIELD):
        for row in values_in_field(conn, field_key):
            if row["value_id"] == value_id:
                return row
    raise AssertionError(f"{value_id} is not readable in any field")


# --------------------------------------------------------------------------- §3.12
def test_a_value_auto_creates_on_first_sight(p6_conn):
    # §3.12: "The system may create new values when it sees a new course, project,
    # company, university, or event". Nobody registers it first.
    assert values_in_field(p6_conn, FIELD) == []
    value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                            first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    rows = values_in_field(p6_conn, FIELD)
    assert [r["canonical_value"] for r in rows] == [CANONICAL]
    assert rows[0]["origin"] == VALUE_ORIGINS[0] == "automatic"
    assert rows[0]["value_id"] == value_id


def test_seeing_the_same_value_again_returns_the_same_id_and_not_a_second_row(p6_conn):
    first = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                         first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    # A different file, a different observation, the same normalized answer.
    second = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                          first_evidence_ref=_key("UChicago", locator="metadata:field=Subject"),
                          origin=VALUE_ORIGINS[0])
    assert first == second
    assert len(values_in_field(p6_conn, FIELD)) == 1
    # The FIRST evidence ref is the one that introduced it, and it is not overwritten
    # by the second sighting -- §3.2's "preserve both the original evidence and the
    # conclusion built from it" applied to the value row itself.
    assert _row(p6_conn, first)["first_evidence_ref"] == _key(RAW)


def test_an_automatic_value_must_cite_the_observation_that_introduced_it(p6_conn):
    # §3.1: "Every fact preserves where it came from." A value the system created for
    # itself, with nothing to point at, is the guess this part exists to refuse.
    with pytest.raises(ValueError):
        ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                     first_evidence_ref=None, origin=VALUE_ORIGINS[0])
    with pytest.raises(ValueError):
        # A plausible-looking string that is not a P4 observation key.
        ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                     first_evidence_ref="observation-17", origin=VALUE_ORIGINS[0])
    assert values_in_field(p6_conn, FIELD) == []


def test_a_user_created_value_needs_no_observation(p6_conn):
    # §3.12's other origin. A user typing a value is not citing evidence, and
    # demanding one would make the user path impossible rather than careful.
    value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value="Georgetown Prep",
                            first_evidence_ref=None, origin=VALUE_ORIGINS[1])
    row = _row(p6_conn, value_id)
    assert row["origin"] == VALUE_ORIGINS[1] == "user"
    assert row["first_evidence_ref"] is None


def test_a_foreign_origin_is_refused_by_p4s_check(p6_conn):
    with pytest.raises(NotInVocabulary):
        ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                     first_evidence_ref=_key(RAW), origin="inferred")
    assert values_in_field(p6_conn, FIELD) == []


# ------------------------------------------------ §3.12 one value, exactly one field
def test_the_same_string_under_two_fields_is_two_values(p6_conn):
    # §3.12: "a value belongs to exactly one field". §3.8 is why it matters: "the same
    # entity type in a different role is a different field". A school we are applying
    # TO and a school that is our client are not one value with two meanings.
    target = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                          first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    client = ensure_value(p6_conn, field_key=OTHER_FIELD, canonical_value=CANONICAL,
                          first_evidence_ref=_key(RAW, locator="metadata:field=Client"),
                          origin=VALUE_ORIGINS[0])
    assert target != client
    assert [r["value_id"] for r in values_in_field(p6_conn, FIELD)] == [target]
    assert [r["value_id"] for r in values_in_field(p6_conn, OTHER_FIELD)] == [client]


def test_a_value_cannot_be_created_under_a_field_outside_the_catalogue(p6_conn):
    # Done-means 3's negative half, seen from the value side: §3.5's "The LLM is not
    # allowed to invent a new fact schema, create an unsupported field". Creating a
    # value must not be a back door into creating a field.
    with pytest.raises(FieldNotInCatalogue):
        ensure_value(p6_conn, field_key="vibe", canonical_value="energetic",
                     first_evidence_ref=_key("energetic"), origin=VALUE_ORIGINS[0])
    tables = {r[0] for r in p6_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "fields" in tables
    assert p6_conn.execute(
        "SELECT COUNT(*) FROM fields WHERE field_key = 'vibe'").fetchone()[0] == 0


# ------------------------------------------------------------- §2.8 three renderings
def test_the_three_renderings_coexist_and_none_overwrites_another(p6_conn):
    # §2.8: "If a document says U Chicago, the raw observation remains exactly that
    # wording, while a resolver may normalize it to University of Chicago and the user
    # may later choose to display it as UChicago."
    value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                            first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    add_raw_variant(p6_conn, value_id, RAW)
    set_display_label(p6_conn, value_id, DISPLAY)

    value = ValueRow.from_row(_row(p6_conn, value_id))
    assert value.raw_variants == (RAW,)
    assert value.canonical_value == CANONICAL
    assert value.display_label == DISPLAY
    # Three columns, three renderings, and the raw wording is byte-exact.
    assert len({value.raw_variants[0], value.canonical_value, value.display_label}) == 3


def test_every_raw_wording_observed_is_kept(p6_conn):
    value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                            first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    for raw in (RAW, "U. Chicago", RAW, "the University of Chicago"):
        add_raw_variant(p6_conn, value_id, raw)
    # Recorded once each, and the duplicate did not create a second entry.
    assert ValueRow.from_row(_row(p6_conn, value_id)).raw_variants == (
        "U Chicago", "U. Chicago", "the University of Chicago")


def test_raw_variants_do_not_depend_on_the_order_they_arrived_in(p6_conn):
    # Global constraint: P4's reads are in insertion order and P6 imposes its own.
    # Two values that saw the same wordings in different orders must store the same
    # column, or §8.5's replay compares a run against itself and reports a change.
    # Two DIFFERENT canonical values, so these are two rows rather than one row
    # visited twice -- `ensure_value` is idempotent and would otherwise make this
    # test pass without proving anything.
    wordings = ("U Chicago", "U. Chicago", "the University of Chicago")
    stored = []
    for canonical, order in ((CANONICAL, wordings),
                             ("Chicago University", tuple(reversed(wordings)))):
        value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value=canonical,
                                first_evidence_ref=_key(canonical),
                                origin=VALUE_ORIGINS[0])
        for raw in order:
            add_raw_variant(p6_conn, value_id, raw)
        stored.append(_row(p6_conn, value_id)["raw_variants"])
    assert stored[0] == stored[1]


def test_an_empty_raw_variant_is_refused(p6_conn):
    value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                            first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    with pytest.raises(ValueError):
        add_raw_variant(p6_conn, value_id, "")
    assert ValueRow.from_row(_row(p6_conn, value_id)).raw_variants == ()


def test_a_variant_on_an_unknown_value_raises(p6_conn):
    with pytest.raises(KeyError):
        add_raw_variant(p6_conn, "sha256:" + "0" * 64, RAW)


# --------------------------------------------- §0 taxonomy aliases; §8.2 never delete
def test_a_merge_records_an_alias_and_deletes_nothing(p6_conn):
    keep = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                        first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    merged = ensure_value(p6_conn, field_key=FIELD, canonical_value="U Chicago",
                          first_evidence_ref=_key(RAW, locator="filename:name"),
                          origin=VALUE_ORIGINS[0])
    add_raw_variant(p6_conn, merged, "U Chicago")
    set_display_label(p6_conn, merged, "U Chi")

    merge_values(p6_conn, keep=keep, merged=merged,
                 reason="one university under two wordings")

    kept_row = ValueRow.from_row(_row(p6_conn, keep))
    # The merged value's canonical wording, its label and its raw variants survive on
    # the surviving row. §0 records "taxonomy aliases"; this is one.
    assert "U Chicago" in kept_row.aliases
    assert "U Chi" in kept_row.aliases
    assert "U Chicago" in kept_row.raw_variants

    # And the merged row is STILL A ROW. Every fact that pointed at it still resolves,
    # and it names where it went.
    merged_row = _row(p6_conn, merged)
    assert merged_row["merged_into"] == keep
    assert merged_row["merge_reason"] == "one university under two wordings"
    assert merged_row["canonical_value"] == "U Chicago"
    assert {r["value_id"] for r in values_in_field(p6_conn, FIELD)} == {keep, merged}


def test_a_value_row_can_never_be_deleted(p6_conn):
    # The SPEC's own words for this table: merges "record an alias, never delete a
    # value (§8.2)". Enforced by trigger, so the assertion above is unfalsifiable
    # rather than merely true of today's code path.
    value_id = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                            first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    with pytest.raises(sqlite3.IntegrityError):
        p6_conn.execute('DELETE FROM "values" WHERE value_id = ?', (value_id,))
    assert len(values_in_field(p6_conn, FIELD)) == 1


def test_a_merge_across_two_fields_is_refused(p6_conn):
    # Merging §3.8's roles together would erase the separation the field split exists
    # to create -- the school we apply to becoming the school that is our client.
    target = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                          first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    client = ensure_value(p6_conn, field_key=OTHER_FIELD, canonical_value=CANONICAL,
                          first_evidence_ref=_key(RAW, locator="metadata:field=Client"),
                          origin=VALUE_ORIGINS[0])
    with pytest.raises(ValueError):
        merge_values(p6_conn, keep=target, merged=client, reason="same name")
    assert _row(p6_conn, client)["merged_into"] is None


def test_a_merge_records_why_and_refuses_the_degenerate_cases(p6_conn):
    keep = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                        first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    merged = ensure_value(p6_conn, field_key=FIELD, canonical_value="U Chicago",
                          first_evidence_ref=_key(RAW, locator="filename:name"),
                          origin=VALUE_ORIGINS[0])
    with pytest.raises(ValueError):
        merge_values(p6_conn, keep=keep, merged=merged, reason="")
    with pytest.raises(ValueError):
        merge_values(p6_conn, keep=keep, merged=keep, reason="itself")
    with pytest.raises(KeyError):
        merge_values(p6_conn, keep=keep, merged="sha256:" + "0" * 64, reason="ghost")

    merge_values(p6_conn, keep=keep, merged=merged, reason="first merge")
    # The first reason sticks -- P1's supersede rule, applied to the alias record.
    with pytest.raises(ValueError):
        merge_values(p6_conn, keep=keep, merged=merged, reason="second merge")
    assert _row(p6_conn, merged)["merge_reason"] == "first merge"


def test_a_merge_chain_cannot_cycle(p6_conn):
    a = ensure_value(p6_conn, field_key=FIELD, canonical_value="A University",
                     first_evidence_ref=_key("A University"), origin=VALUE_ORIGINS[0])
    b = ensure_value(p6_conn, field_key=FIELD, canonical_value="B University",
                     first_evidence_ref=_key("B University"), origin=VALUE_ORIGINS[0])
    merge_values(p6_conn, keep=b, merged=a, reason="a is b")
    with pytest.raises(ValueError):
        merge_values(p6_conn, keep=a, merged=b, reason="and b is a")


# ------------------------------------------------------------------------ §8.8 held
def test_the_display_label_is_stored_unscoped_and_no_plan_version_is_invented(p6_conn):
    # §8.8 puts "User labels and aliases" inside a plan version; Task 22 owns that
    # scoping. This task must not invent a plan_version keyword no caller can supply.
    import inspect
    assert "plan_version" not in inspect.signature(set_display_label).parameters
    columns = {r["name"] for r in p6_conn.execute('PRAGMA table_info("values")')}
    assert "plan_version" not in columns
```

- [ ] **Step 3: Run the test and confirm it FAILS for the right reason**

Run: `pytest tests/p6/test_p6_values.py -q`

Expected: **collection error** — `ModuleNotFoundError: No module named 'facts.values'`, raised at the
`from facts.values import ...` line. All 18 tests error at collection; none run. Any other failure at
this step means Task 1 or Task 2 is not green and this task should stop rather than proceed.

- [ ] **Step 4: Add the `values` DDL to `src/facts/schema.py`**

Append this constant to `src/facts/schema.py`, after the `fields` DDL Task 2 added.

```python
#: `values` is a SQL keyword -- `CREATE TABLE values (...)` is a syntax error in
#: SQLite, verified on 3.45.3 -- so the identifier is quoted here and at every call
#: site in `facts.values`. It is the only table in the product that needs quoting.
#:
#: `field_id` holds the field KEY. The SPEC's `fields` table publishes `field_key` as
#: its stable identifier and declares no surrogate; the SPEC's `values` and
#: `file_facts` shapes and the plan skeleton's `ValueRow` all name the foreign key
#: `field_id`. The column keeps the published name and holds the published key.
#:
#: It carries NO `REFERENCES fields (...)` clause, and that is deliberate rather than
#: forgotten. `open_database` leaves `PRAGMA foreign_keys` ON (verified: it reads 1),
#: and a foreign key whose parent column is not a declared PRIMARY KEY or UNIQUE
#: raises `sqlite3.OperationalError: foreign key mismatch` at INSERT -- also verified.
#: Whether `fields.field_key` is declared PRIMARY KEY is Task 2's DDL decision, and
#: this table must not fail at run time on a choice it does not own. The gate the SPEC
#: actually names is the catalogue lookup: `get_field` raises `FieldNotInCatalogue`
#: before any INSERT reaches here, and Task 3's test asserts it.
#:
#: UNIQUE (field_id, canonical_value) is §3.12's "a value belongs to exactly one
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
    field_id           TEXT NOT NULL,
    canonical_value    TEXT NOT NULL,
    raw_variants       TEXT NOT NULL,
    display_label      TEXT,
    aliases            TEXT NOT NULL,
    origin             TEXT NOT NULL,
    first_evidence_ref TEXT,
    merged_into        TEXT REFERENCES "values" (value_id),
    merge_reason       TEXT,
    UNIQUE (field_id, canonical_value)
);
CREATE INDEX IF NOT EXISTS values_field ON "values" (field_id);
CREATE INDEX IF NOT EXISTS values_merged ON "values" (merged_into);
CREATE TRIGGER IF NOT EXISTS values_no_delete
BEFORE DELETE ON "values"
BEGIN SELECT RAISE(ABORT, 'a merge records an alias; a value is never deleted (§0, §8.2)'); END;
"""
```

Then add one line to `create_facts_schema`, after the `fields` script:

```python
def create_facts_schema(conn: sqlite3.Connection) -> None:
    """Create every P6-owned table. Idempotent. P1's `create_schema` runs first, and
    P4's `create_evidence_schema` before any read."""
    conn.executescript(FIELDS_DDL)
    conn.executescript(VALUES_DDL)
```

`RAISE(ABORT, ...)` surfaces in Python as `sqlite3.IntegrityError`, which is what
`test_a_value_row_can_never_be_deleted` catches — the same class P4's `evidence_no_delete` raises.

- [ ] **Step 5: Write `src/facts/values.py`**

```python
# src/facts/values.py
"""§3.12's `values` table -- "the changing, user-specific content discovered from
files", as against `fields`, which are "the long-term organization language of the
product".

Three design sentences are load-bearing here, and each is a test rather than a comment:

  * §3.12: "The system may create new values when it sees a new course, project,
    company, university, or event, but it should not invent new fields automatically."
    `ensure_value` creates a VALUE row and never a FIELD row. The field must already be
    in Task 2's closed catalogue; `get_field` raises `FieldNotInCatalogue` if it is not,
    so creating a value is not a back door into creating a field (§3.5).
  * §3.12 again: "a value belongs to exactly one field". The same string under two
    fields is two values. That is §3.8's role separation -- "the same entity type in a
    different role is a different field" -- expressed in this table.
  * §2.8: "If a document says U Chicago, the raw observation remains exactly that
    wording, while a resolver may normalize it to University of Chicago and the user
    may later choose to display it as UChicago." Three renderings, three columns,
    none of them overwriting another.

`value_id` is content-addressed over (field_id, canonical_value). That makes
`ensure_value` idempotent with no read-then-write race, gives two databases that saw
the same corpus the same value ids (§8.5's replay), and turns one-value-one-field into
a property of the identifier rather than a rule to remember.

Ordering is imposed, never inherited. `raw_variants` and `aliases` are stored sorted,
and `values_in_field` sorts, because P4's reads are in insertion order (verified by
execution) and a corpus extracted in a different order must not produce a different
row.

The table name is a SQL keyword and every statement below quotes it.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import check

from facts.fields import get_field

#: §3.12's two origins. A closed vocabulary, checked through P4's `check` so a foreign
#: value raises `NotInVocabulary` instead of being stored (Global Constraints).
VALUE_ORIGINS: tuple[str, str] = ("automatic", "user")

#: An observation key is P4's, content-addressed, and `sha256:`-prefixed (M14).
_KEY_PREFIX = "sha256:"


@dataclass(frozen=True)
class ValueRow:
    """The SPEC's `values` shape, with its two JSON arrays already decoded.

    Decoding happens in exactly one place. A reader that calls `json.loads` on
    `raw_variants` itself is a second decoder, and a second decoder is where the two
    representations drift.
    """

    value_id: str
    field_id: str
    canonical_value: str
    raw_variants: tuple[str, ...]
    display_label: str | None
    aliases: tuple[str, ...]
    origin: str
    first_evidence_ref: str | None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "ValueRow":
        return cls(
            value_id=row["value_id"],
            field_id=row["field_id"],
            canonical_value=row["canonical_value"],
            raw_variants=tuple(json.loads(row["raw_variants"])),
            display_label=row["display_label"],
            aliases=tuple(json.loads(row["aliases"])),
            origin=row["origin"],
            first_evidence_ref=row["first_evidence_ref"],
        )


def _field_id(conn: sqlite3.Connection, field_key: str) -> str:
    """The catalogue row's key, and the gate that stops a value inventing a field.

    `get_field` raises `FieldNotInCatalogue` for a key outside Task 2's closed
    catalogue, so this function is also §3.12's "it should not invent new fields
    automatically" enforced on the value path.
    """
    return get_field(conn, field_key)["field_key"]


def _value_identity(*, field_id: str, canonical_value: str) -> str:
    """Content-addressed value identity. `sha256_of` is length-prefixed and injective,
    so ("a", "bc") and ("ab", "c") do not collide."""
    return sha256_of("facts.values", field_id, canonical_value)


def _fetch(conn: sqlite3.Connection, value_id: str) -> sqlite3.Row:
    row = conn.execute(
        'SELECT * FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    if row is None:
        raise KeyError(f"unknown value {value_id!r}")
    return row


def _store_list(items) -> str:
    """One sorted, de-duplicated, canonical JSON array. Sorted because P4's reads are
    in insertion order and this row must not inherit it."""
    return canonical_json(sorted(set(items)))


def ensure_value(conn: sqlite3.Connection, *, field_key: str, canonical_value: str,
                 first_evidence_ref: str | None, origin: str) -> str:
    """§3.12's auto-create. Returns the value id, creating the row on first sight.

    Idempotent: the second sighting of the same canonical value under the same field
    returns the first row's id and does not overwrite its `first_evidence_ref`, which
    is the observation that introduced it.
    """
    check(origin, VALUE_ORIGINS, name="value origin")
    if not canonical_value:
        raise ValueError("a value needs a canonical form (§3.12)")
    if origin == VALUE_ORIGINS[0]:
        if not first_evidence_ref or not first_evidence_ref.startswith(_KEY_PREFIX):
            raise ValueError(
                "an automatically created value cites the observation that introduced "
                "it (§3.1); first_evidence_ref must be a P4 observation key"
            )
    field_id = _field_id(conn, field_key)
    value_id = _value_identity(field_id=field_id, canonical_value=canonical_value)
    existing = conn.execute(
        'SELECT value_id FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    if existing is not None:
        return existing["value_id"]
    conn.execute(
        'INSERT INTO "values" (value_id, field_id, canonical_value, raw_variants, '
        'display_label, aliases, origin, first_evidence_ref, merged_into, '
        'merge_reason) VALUES (?, ?, ?, ?, NULL, ?, ?, ?, NULL, NULL)',
        (value_id, field_id, canonical_value, _store_list(()), _store_list(()),
         origin, first_evidence_ref),
    )
    return value_id


def add_raw_variant(conn: sqlite3.Connection, value_id: str, raw: str) -> None:
    """§2.8: "the raw observation remains exactly that wording". Byte-exact, and
    recorded once however many times it is seen."""
    if not raw:
        raise ValueError(
            "a raw variant is the wording the document used; it is never empty (§2.8)"
        )
    row = _fetch(conn, value_id)
    variants = json.loads(row["raw_variants"])
    if raw in variants:
        return
    conn.execute(
        'UPDATE "values" SET raw_variants = ? WHERE value_id = ?',
        (_store_list([*variants, raw]), value_id),
    )


def set_display_label(conn: sqlite3.Connection, value_id: str,
                      display_label: str) -> None:
    """§2.8's third rendering: "the user may later choose to display it as UChicago".

    Stored unscoped. §8.8 places the display label inside a plan version and Task 22
    owns that scoping; this function invents no `plan_version` keyword, because no
    caller could supply one today and a required keyword nobody can fill is a
    threshold with no injector.
    """
    if not display_label:
        raise ValueError("a display label is a rendering, never empty (§2.8)")
    _fetch(conn, value_id)
    conn.execute(
        'UPDATE "values" SET display_label = ? WHERE value_id = ?',
        (display_label, value_id),
    )


def merge_values(conn: sqlite3.Connection, *, keep: str, merged: str,
                 reason: str) -> None:
    """§0's taxonomy aliases. The merge records an alias and deletes nothing (§8.2).

    The merged row keeps its identity, its canonical wording and its evidence ref, and
    gains a pointer to the surviving value, so every fact that already pointed at it
    still resolves and a reader can see where it went. The surviving row absorbs the
    merged value's canonical wording, its label and its raw variants as aliases.
    """
    if not reason:
        raise ValueError("a merge records why (§8.2)")
    if keep == merged:
        raise ValueError("a value cannot be merged into itself")
    keep_row, merged_row = _fetch(conn, keep), _fetch(conn, merged)
    if keep_row["field_id"] != merged_row["field_id"]:
        raise ValueError(
            "a value belongs to exactly one field (§3.12); merging across two fields "
            "would erase §3.8's role separation"
        )
    if merged_row["merged_into"] is not None:
        raise ValueError(
            f"{merged} is already merged into {merged_row['merged_into']}; "
            "the first merge_reason is never overwritten (§8.2)"
        )
    seen, cursor = {merged}, keep
    while cursor is not None:
        if cursor in seen:
            raise ValueError("merge chain would cycle")
        seen.add(cursor)
        row = conn.execute(
            'SELECT merged_into FROM "values" WHERE value_id = ?', (cursor,)
        ).fetchone()
        cursor = None if row is None else row["merged_into"]

    aliases = set(json.loads(keep_row["aliases"]))
    aliases.add(merged_row["canonical_value"])
    aliases.update(json.loads(merged_row["aliases"]))
    if merged_row["display_label"]:
        aliases.add(merged_row["display_label"])
    variants = set(json.loads(keep_row["raw_variants"]))
    variants.update(json.loads(merged_row["raw_variants"]))
    conn.execute(
        'UPDATE "values" SET aliases = ?, raw_variants = ? WHERE value_id = ?',
        (_store_list(aliases), _store_list(variants), keep),
    )
    conn.execute(
        'UPDATE "values" SET merged_into = ?, merge_reason = ? WHERE value_id = ?',
        (keep, reason, merged),
    )


def values_in_field(conn: sqlite3.Connection, field_key: str) -> list[sqlite3.Row]:
    """Every value in one field, merged ones included -- a merged value is still a
    readable value (§8.2) and a fact that points at it must still resolve.

    Sorted, because P4's reads are in insertion order and this one imposes its own.
    """
    return list(conn.execute(
        'SELECT * FROM "values" WHERE field_id = ? '
        'ORDER BY canonical_value, value_id',
        (_field_id(conn, field_key),),
    ))
```

- [ ] **Step 6: Run the test and confirm it passes**

Run: `pytest tests/p6/test_p6_values.py -v`

Expected: PASS — **18 passed**. Two of the eighteen are the ones worth watching:
`test_a_value_row_can_never_be_deleted` passes because the trigger raises
`sqlite3.IntegrityError`, not because `merge_values` politely declines to delete; and
`test_raw_variants_do_not_depend_on_the_order_they_arrived_in` passes because `_store_list` sorts,
which is the Global Constraint about P4's insertion-order reads applied to the one column in this
task that accumulates.

- [ ] **Step 7: Run the whole P6 suite, so Tasks 1 and 2 are still green**

Run: `pytest tests/p6 -q`

Expected: PASS. Task 2's guard walks `facts` for a runtime-created field, and `facts.values` is a new
module inside its reach: `ensure_value` creates value rows only, and the only write it makes to
`fields` is none. A failure here is a real finding.

- [ ] **Step 8: Commit**

```bash
git add src/facts/values.py src/facts/schema.py tests/p6/conftest.py tests/p6/test_p6_values.py
git commit -m "feat(P6): §3.12 values auto-create; §2.8's three renderings; a merge aliases, never deletes"
```

---

### Task 4: `file_facts` — the row, and the negative contract a reviewer can check from the schema

**Files:**
- Create: `src/facts/file_facts.py`
- Modify: `src/facts/schema.py` (add `FILE_FACTS_DDL`; one line in `create_facts_schema`)
- Test: `tests/p6/test_p6_file_facts.py`

**Interfaces:**
- Consumes: `facts.states` — `STATES`; `facts.fields` — `get_field`, `FieldNotInCatalogue`;
  `facts.values` — `values_in_field`; `facts.authorship` — `event_defaults`, `AUTHORED_EVENT_TYPES`;
  `database_agent.supersede` — `SUPERSEDE_COLUMNS`, `supersede_ddl`; `database_agent.events` —
  `append_event`; `evidence_shape.canonical` — `canonical_json`, `sha256_of`;
  `evidence_shape.vocabulary` — `check`, `NotInVocabulary`.
- Produces: `FILE_FACTS_COLUMNS: tuple[str, ...]`, `FORBIDDEN_COLUMN_SUBSTRINGS: tuple[str, ...]`,
  `FACT_ORIGINS: tuple[str, ...]` (§3.1's five: deterministic extractor · rule · LLM interpretation ·
  user correction · user-approved folder), `write_fact(conn, *, file_id, content_hash, field_key,
  value_id, reliability_state, origin, evidence_refs, cache_key, active, cited_quote_refs=(),
  model_identifier=None, prompt_fingerprint=None, internal_score=None, rejection_reason=None) -> str`,
  `facts_for_file(conn, file_id, content_hash) -> list[sqlite3.Row]`, `EvidenceRequired`.

**Done-means:** 1.

---

**The negative contract is the point of this task, so it is stated before anything else.**

§3.14, verbatim: *"Facts remain separate from the future destination tree. A fact such as subject =
BUSIB 4300 does not itself dictate one permanent folder path. The user may later organize the same
facts as Academics/Columbia/2026-Spring/BUSIB 4300/Syllabus or as Academics/BUSIB 4300/Spring
2026/Syllabus. The facts have not changed; only the user's preferred organization view has changed."*
§4.1 adds the other half — the graph *"does not automatically copy those missing facts onto sparse
files"* — and §3.9 that a session is *"not a basis for automatic semantic propagation"*.

The SPEC turns that into a sentence a reviewer can act on: *"`file_facts` has no path column, no
destination column, no folder column, and no group column. A fact does not dictate a path (§3.14) and
does not record membership (§4.3). A reviewer should be able to check this by reading the schema
alone."*

**"By reading the schema alone" is a testable claim, and this task makes it one.** Three published
names carry it, and Task 5 and Tasks 16–19 import two of them so the same contract binds `unresolved`
and every later reader:

```text
FILE_FACTS_COLUMNS              what the module declares the table to be
FORBIDDEN_COLUMN_SUBSTRINGS     ("path", "destination", "folder", "node", "group")
PRAGMA table_info(file_facts)   what the database actually is
```

The test asserts all three agree: the declared tuple **equals** the live column set, so the module
cannot describe a table it does not have; and no live column name **contains** any forbidden
substring, so `destination_node_id` fails the day it is added rather than the day someone reads it.
A substring list is used rather than an exact-name list for that reason alone.

**And the guard is proved non-vacuous in the same file.** A check that scans for a token has returned
a false result nine times on this project. So one test builds a scratch table carrying
`destination_node_id` and runs the identical check over it, asserting it is caught. A guard that
cannot be shown to fail is not evidence that the thing it guards is absent.

**The negative contract also covers the writer's signature, not only the schema.** A column is one
way to smuggle a path in; a keyword argument is the other. `write_fact` is introspected at run time
for a parameter whose name contains any forbidden substring — which is how §4.3's *"P6 stores no
group membership"* is asserted from this task rather than deferred to Task 25's sweep.

---

**`FACT_ORIGINS` — this task owns the literal spelling, and two documents order it differently.**

The SPEC's `file_facts` shape publishes the five in one order: *"origin — which producer created it —
deterministic extractor | rule | LLM interpretation | user correction | user-approved folder
(§3.1)"*. §3.1's prose sentence lists the same producers in a different order and with *"deterministic
rule"* as a single phrase: *"a filename, document title, heading, table cell, page of extracted text,
EXIF field, OCR region, archive manifest, user-approved folder, deterministic rule, LLM
interpretation, or explicit user correction."* The first eight of those are evidence *locations* —
P4's business, already carried on the observation — and the last four are producers.

**The SPEC's order is the stored one**, because `PLAN-tasks-07-09.md`, `PLAN-tasks-14-15.md` and
`PLAN-tasks-16-19.md` all address the tuple **by index** (`FACT_ORIGINS[0]` for a deterministic
producer, `FACT_ORIGINS[1]` for a rule) precisely so this task can choose the spelling without
breaking them. Re-ordering it would silently re-label every fact three other authors write. The
spelling is `snake_case`, matching every other stored vocabulary in the part:

```python
FACT_ORIGINS = ("deterministic_extractor", "rule", "llm_interpretation",
                "user_correction", "user_approved_folder")
```

---

**Two facts about the SPEC's `file_facts` shape that this task changes, both reported.**

1. **`content_hash` is missing from the SPEC's column list and is added here.** It has to be:
   `facts_for_file(conn, file_id, content_hash)` is the skeleton's published signature, the abstention
   row and the §3.4 cache key are both per content hash, and the Global Constraint is explicit —
   *"Every P6 read that is per file version — which is all of them — must filter on
   `observation.content_hash`."* The cache key contains the content hash but is a digest, so it
   cannot be filtered on. Without the column the published read is unimplementable.
2. **No foreign key points at `fields`.** `open_database` leaves `PRAGMA foreign_keys` ON (verified:
   it reads `1`), and a foreign key whose parent column is not a declared PRIMARY KEY or UNIQUE
   raises `sqlite3.OperationalError: foreign key mismatch` at INSERT (also verified). Whether
   `fields.field_key` is declared PRIMARY KEY is Task 2's DDL decision. `get_field` is the gate the
   SPEC names, it raises `FieldNotInCatalogue` before any INSERT, and this task's test asserts it.
   The one foreign key kept is `value_id REFERENCES "values" (value_id)`, whose parent **is** a
   primary key — so a fact can never cite a value that does not exist.

**`fact_id` is content-addressed, for the same three reasons `value_id` is** (Task 3): writing the
same conclusion at the same cache key twice is one row rather than two, replay (§8.5) produces the
same identifiers in a second database, and the identity is checkable rather than remembered. §8.2's
supersession path is unaffected: pass 4 cites `ocr`-tier observations, so §3.4's `analysis_tier`
differs, so the cache key differs, so the fact id differs and the new fact supersedes rather than
collides. **A second write at an identical cache key appends no second `fact creation` event**, or the
provenance log would count one fact twice.

**What this task does not write.** `preferred` is Task 18's — *"`mark_superseded` does not touch
`preferred` and knows nothing about it — that column is Task 18's whole job."* This task **creates**
the column, because M1 places it on `file_facts` and nowhere else, and **never sets it**; a test
asserts `write_fact` leaves it `NULL`. Filtering a read by `active`, `preferred` or reliability state
is Task 24's proposal-eligible read; `facts_for_file` returns every fact row for that file version, in
an order it imposes itself.

---

- [ ] **Step 1: Write the failing test**

Create `tests/p6/test_p6_file_facts.py` with exactly this content. It uses `p6_conn` from
`tests/p6/conftest.py` (Task 3, Step 1) and needs **no P1 `files` row** — verified: `append_event`
accepts a `file_id` that is in no `files` row, and `file_facts` references `files` no more than P4's
`evidence` does.

```python
# tests/p6/test_p6_file_facts.py
"""Done-means 1: the fact row exists with the shape the SPEC declares, and it carries
no path, no destination, no folder, no node and no group -- checkable from the schema
alone (§3.14, §4.3).

§3.14: "Facts remain separate from the future destination tree. A fact such as
subject = BUSIB 4300 does not itself dictate one permanent folder path."
"""
import inspect
import json
import sqlite3

import pytest

from database_agent.supersede import SUPERSEDE_COLUMNS, mark_superseded

from evidence_shape.observation import observation_key
from evidence_shape.vocabulary import NotInVocabulary

from facts.fields import FieldNotInCatalogue
from facts.file_facts import (
    FACT_ORIGINS,
    FILE_FACTS_COLUMNS,
    FORBIDDEN_COLUMN_SUBSTRINGS,
    EvidenceRequired,
    facts_for_file,
    write_fact,
)
from facts.states import STATES
from facts.values import VALUE_ORIGINS, ensure_value

FIELD = "subject"            # D6: the ratified academic field key
OTHER_FIELD = "client"       # §3.8, a role field -- a different field, same string
CONTENT_HASH = "a" * 64
OTHER_HASH = "b" * 64
FILE_ID = "file-1"
CACHE_KEY = "sha256:" + "c" * 64


def _key(raw: str, *, locator: str = "heading:page=1/heading=2") -> str:
    return observation_key(content_hash=CONTENT_HASH, extractor_name="pdf.text",
                           locator=locator, raw_value=raw)


def _value(conn, *, field_key: str = FIELD, canonical: str = "BUSIB 4300") -> str:
    return ensure_value(conn, field_key=field_key, canonical_value=canonical,
                        first_evidence_ref=_key(canonical), origin=VALUE_ORIGINS[0])


def _write(conn, **overrides) -> str:
    kwargs = dict(file_id=FILE_ID, content_hash=CONTENT_HASH, field_key=FIELD,
                  value_id=_value(conn), reliability_state=STATES[1],
                  origin=FACT_ORIGINS[0], evidence_refs=(_key("BUSIB 4300"),),
                  cache_key=CACHE_KEY, active=True)
    kwargs.update(overrides)
    return write_fact(conn, **kwargs)


def _live_columns(conn, table: str) -> tuple[str, ...]:
    """What the database actually is. Generated VIRTUAL columns are absent from
    `table_info` -- verified on SQLite 3.45.3 -- which is exactly why `record_id` is
    not in FILE_FACTS_COLUMNS and is asserted separately below."""
    return tuple(r["name"] for r in conn.execute(f"PRAGMA table_info({table})"))


def _offending(names) -> list[str]:
    """The one check the negative contract is made of, in one place, so the vacuity
    test below runs the identical code over a table built to fail it."""
    return [name for name in names
            if any(bad in name.lower() for bad in FORBIDDEN_COLUMN_SUBSTRINGS)]


# ------------------------------------------- Done-means 1: the shape, and only it
def test_the_module_declares_exactly_the_table_it_has(p6_conn):
    # A module that describes a table it does not have makes every other assertion
    # in this file an assertion about a document rather than about a database.
    assert _live_columns(p6_conn, "file_facts") == FILE_FACTS_COLUMNS


def test_the_row_carries_what_the_spec_declares(p6_conn):
    for column in ("fact_id", "file_id", "content_hash", "field_id", "value_id",
                   "reliability_state", "origin", "evidence_refs",
                   "cited_quote_refs", "cache_key", "model_identifier",
                   "prompt_fingerprint", "internal_score", "active", "preferred",
                   "rejection_reason", "created_at", *SUPERSEDE_COLUMNS):
        assert column in FILE_FACTS_COLUMNS


def test_the_three_supersede_columns_are_p1s_and_are_not_respelled(p6_conn):
    # M1: the set is published once, by P1, and adopted by name.
    assert set(SUPERSEDE_COLUMNS) <= set(FILE_FACTS_COLUMNS)
    assert SUPERSEDE_COLUMNS == ("supersedes", "superseded_by", "supersede_reason")


# ----------------------------------------- the negative contract (§3.14, §4.3, §4.1)
def test_no_column_names_a_path_a_destination_a_folder_a_node_or_a_group(p6_conn):
    # §3.14: "A fact such as subject = BUSIB 4300 does not itself dictate one
    # permanent folder path." §4.3 and §4.1: a fact records no group membership.
    # Read from the database, not from the module, so a DDL edit cannot pass by
    # editing the tuple.
    assert _offending(_live_columns(p6_conn, "file_facts")) == []
    assert _offending(FILE_FACTS_COLUMNS) == []


def test_the_forbidden_substring_guard_is_not_vacuous(p6_conn):
    # A scan for a token has produced a false result nine times on this project. So
    # the guard is run over a table built to fail it. If this test ever passes with
    # an empty list, the check above is proving nothing.
    p6_conn.execute("CREATE TABLE scratch_tree (fact_id TEXT, destination_node_id "
                    "TEXT, folder_path TEXT, group_id TEXT)")
    assert _offending(_live_columns(p6_conn, "scratch_tree")) == [
        "destination_node_id", "folder_path", "group_id"]
    p6_conn.execute("DROP TABLE scratch_tree")


def test_the_writer_takes_no_path_and_no_group_either(p6_conn):
    # A column is one way to smuggle a destination in; a keyword is the other.
    # §4.3: P6 accepts no fact write derived from group membership.
    parameters = inspect.signature(write_fact).parameters
    assert _offending(parameters) == []
    assert "group_id" not in parameters
    assert "path" not in parameters


def test_a_fact_never_learns_the_files_path(p6_conn):
    # The whole of §3.14 in one assertion: the row that results from writing a fact
    # contains no rendering of any path, under any column name.
    fact_id = _write(p6_conn)
    row = [r for r in facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)
           if r["fact_id"] == fact_id][0]
    assert _offending(row.keys()) == []


# --------------------------------------------------- §3.1 a fact carries its evidence
def test_a_fact_is_written_and_read_back_with_its_field_and_its_value(p6_conn):
    fact_id = _write(p6_conn)
    rows = facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)
    assert len(rows) == 1
    row = rows[0]
    assert row["fact_id"] == fact_id
    # The read projects the field KEY and the canonical value, so no caller has to
    # join `fields` and `values` for itself.
    assert row["field_key"] == FIELD
    assert row["canonical_value"] == "BUSIB 4300"
    assert row["reliability_state"] == STATES[1] == "direct"
    assert row["origin"] == FACT_ORIGINS[0]
    assert json.loads(row["evidence_refs"]) == [_key("BUSIB 4300")]
    assert row["active"] == 1


def test_a_non_user_fact_with_no_evidence_is_refused(p6_conn):
    # §3.1: "Every fact preserves where it came from." A fact with nothing behind it
    # is the plausible guess this part exists to refuse.
    with pytest.raises(EvidenceRequired):
        _write(p6_conn, evidence_refs=())
    assert facts_for_file(p6_conn, FILE_ID, CONTENT_HASH) == []


def test_every_evidence_ref_must_be_a_p4_observation_key(p6_conn):
    # M14: the citation is the content-addressed key, never an observation_id and
    # never a row id -- that is what makes it survive an extractor upgrade (§8.7).
    for bad in ("observation-17", "", "sha255:" + "0" * 64, "0" * 64):
        with pytest.raises(EvidenceRequired):
            _write(p6_conn, evidence_refs=(bad,))
    assert facts_for_file(p6_conn, FILE_ID, CONTENT_HASH) == []


def test_a_user_confirmed_fact_may_stand_without_an_observation(p6_conn):
    # STATES[0] is `user_confirmed`. A user asserting a fact is not citing evidence,
    # and demanding one would make the user path impossible rather than careful.
    fact_id = _write(p6_conn, reliability_state=STATES[0],
                     origin=FACT_ORIGINS[3], evidence_refs=())
    row = [r for r in facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)
           if r["fact_id"] == fact_id][0]
    assert row["reliability_state"] == STATES[0] == "user_confirmed"
    assert json.loads(row["evidence_refs"]) == []


def test_the_evidence_refs_stored_do_not_depend_on_the_order_they_arrived_in(p6_conn):
    # P4's reads are in insertion order; P6 imposes its own before it stores.
    refs = (_key("BUSIB 4300"), _key("BUSIB 4300", locator="filename:name"))
    first = _write(p6_conn, evidence_refs=refs)
    second = _write(p6_conn, evidence_refs=tuple(reversed(refs)))
    assert first == second
    assert len(facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)) == 1


# ------------------------------------------------------- closed vocabularies (§3.5)
def test_a_foreign_reliability_state_is_refused(p6_conn):
    # The six are P4's and P6 re-spells none of them. §3.13's prose spellings are
    # prose: a value outside the six is a load error, not a spelling to normalize.
    for bad in ("LLM-supported", "User-confirmed", "probable"):
        with pytest.raises(NotInVocabulary):
            _write(p6_conn, reliability_state=bad)
    assert facts_for_file(p6_conn, FILE_ID, CONTENT_HASH) == []


def test_a_foreign_origin_is_refused(p6_conn):
    with pytest.raises(NotInVocabulary):
        _write(p6_conn, origin="guess")
    assert facts_for_file(p6_conn, FILE_ID, CONTENT_HASH) == []


def test_the_five_origins_are_the_specs_five_in_the_specs_order(p6_conn):
    assert FACT_ORIGINS == ("deterministic_extractor", "rule", "llm_interpretation",
                            "user_correction", "user_approved_folder")


def test_a_fact_naming_a_field_outside_the_catalogue_is_refused(p6_conn):
    # §3.5: "The LLM is not allowed to invent a new fact schema, create an
    # unsupported field". Writing a fact is not a back door into creating a field.
    with pytest.raises(FieldNotInCatalogue):
        _write(p6_conn, field_key="vibe")
    assert p6_conn.execute(
        "SELECT COUNT(*) FROM fields WHERE field_key = 'vibe'").fetchone()[0] == 0


def test_a_value_belonging_to_another_field_cannot_be_attached(p6_conn):
    # §3.12: "a value belongs to exactly one field", which is §3.8's role separation.
    # A client named BUSIB 4300 is not the subject BUSIB 4300.
    other = _value(p6_conn, field_key=OTHER_FIELD)
    with pytest.raises(ValueError):
        _write(p6_conn, field_key=FIELD, value_id=other)
    assert facts_for_file(p6_conn, FILE_ID, CONTENT_HASH) == []


def test_a_fact_cannot_cite_a_value_that_does_not_exist(p6_conn):
    with pytest.raises(KeyError):
        _write(p6_conn, value_id="sha256:" + "0" * 64)


# ------------------------------------------------------------------ §8.2 provenance
def test_a_fact_creation_event_is_appended_through_p1(p6_conn):
    fact_id = _write(p6_conn)
    rows = list(p6_conn.execute("SELECT * FROM events ORDER BY event_id"))
    assert len(rows) == 1
    event = rows[0]
    # Spelled with a SPACE, and already one of §8.2's nineteen -- P6 registers none.
    assert event["event_type"] == "fact creation"
    assert event["subsystem"] == "P6"          # M8: P6 authors, P1 writes
    assert event["file_id"] == FILE_ID
    assert event["content_hash"] == CONTENT_HASH
    # §8.2's "structured explanation or evidence reference", not a sentence.
    explanation = json.loads(event["explanation"])
    assert explanation["fact_id"] == fact_id
    assert explanation["field"] == FIELD
    assert explanation["evidence_refs"] == [_key("BUSIB 4300")]


def test_this_task_appends_no_event_of_any_other_type(p6_conn):
    _write(p6_conn)
    _write(p6_conn, value_id=_value(p6_conn, canonical="Spring 2026"),
           evidence_refs=(_key("Spring 2026"),))
    types = {r["event_type"] for r in p6_conn.execute("SELECT event_type FROM events")}
    assert types == {"fact creation"}


def test_writing_the_same_fact_twice_is_one_row_and_one_event(p6_conn):
    first = _write(p6_conn)
    second = _write(p6_conn)
    assert first == second
    assert len(facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)) == 1
    assert p6_conn.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 1


def test_the_record_id_projection_lets_p1_address_the_table(p6_conn):
    # P1's `mark_superseded` and `chain` are "... WHERE record_id = ?", and P6's
    # published key is `fact_id`. `record_id` is a VIRTUAL projection of it: it
    # stores nothing, cannot diverge, and is absent from `table_info`, which is why
    # it is not in FILE_FACTS_COLUMNS. P4 solved this the same way.
    hidden = {r["name"]: r["hidden"]
              for r in p6_conn.execute("PRAGMA table_xinfo(file_facts)")}
    assert hidden["record_id"] == 2
    assert "record_id" not in FILE_FACTS_COLUMNS

    old = _write(p6_conn)
    new = _write(p6_conn, cache_key="sha256:" + "d" * 64)
    assert old != new
    # Task 16 owns supersession; this only proves P1 can address the table at all.
    mark_superseded(p6_conn, "file_facts", old_id=old, new_id=new,
                    reason="a later pass at a different cache key")
    rows = {r["fact_id"]: r for r in facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)}
    assert rows[old]["superseded_by"] == new
    assert rows[new]["supersedes"] == old


def test_write_fact_never_sets_preferred(p6_conn):
    # M1 places `preferred` on this table and nowhere else, and Task 18 is the only
    # thing that writes it. A fact is not preferred because it is the only one.
    fact_id = _write(p6_conn)
    row = [r for r in facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)
           if r["fact_id"] == fact_id][0]
    assert row["preferred"] is None


# ------------------------------------------------------------------- the read (§3.4)
def test_facts_for_file_is_per_file_version(p6_conn):
    # Every P6 read is per content hash: the cache key and the abstention row both
    # are (§3.4, §8.2). A prior version's facts are not this version's.
    _write(p6_conn)
    _write(p6_conn, content_hash=OTHER_HASH)
    assert len(facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)) == 1
    assert len(facts_for_file(p6_conn, FILE_ID, OTHER_HASH)) == 1
    assert facts_for_file(p6_conn, "file-2", CONTENT_HASH) == []


def test_the_read_order_is_imposed_and_not_inherited_from_insertion(p6_conn):
    # Written in one order, read back in another -- because the read sorts. Without
    # this the same corpus written in a different order reads differently and §8.5's
    # replay reports a regression when nothing changed.
    # Inserted subject-then-client; read back client-then-subject.
    for field_key, canonical in ((FIELD, "BUSIB 4300"), (OTHER_FIELD, "Zeta LLP")):
        _write(p6_conn, field_key=field_key,
               value_id=_value(p6_conn, field_key=field_key, canonical=canonical),
               evidence_refs=(_key(canonical),))
    assert [r["field_key"] for r in facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)] == [
        OTHER_FIELD, FIELD]      # "client" before "subject", alphabetically
```

- [ ] **Step 2: Run the test and confirm it FAILS for the right reason**

Run: `pytest tests/p6/test_p6_file_facts.py -q`

Expected: **collection error** — `ModuleNotFoundError: No module named 'facts.file_facts'`, raised at
the `from facts.file_facts import ...` line. All 25 tests error at collection; none run.

- [ ] **Step 3: Add the `file_facts` DDL to `src/facts/schema.py`**

Append this to `src/facts/schema.py`, after `VALUES_DDL`, and put the one new import at the top of the
file beside the existing ones. It imports P1's `supersede_ddl` so the three supersede column names are
P1's spelling rather than P6's typing (M1).

**One assumption on Task 1, stated so it can be checked rather than discovered.** `event_defaults(**fields)
-> dict` is expected to return a mapping that already carries `subsystem = "P6"`, a
`component_version`, and an `observed_at` from the part's one clock, with the caller's fields merged
in. `write_fact` calls it **once** and reads `observed_at` back out of the returned dict for the row's
`created_at`, so the fact and its creation event share one instant from one clock and this module owns
no clock of its own. If Task 1's `event_defaults` does not fill `observed_at`, that is a Task 1 defect
and `append_event` will raise `MalformedEvent` at the first test here — which is the right failure.

```python
from database_agent.supersede import supersede_ddl

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
#: `field_id` holds the field KEY and carries no REFERENCES clause -- foreign keys are
#: ON and a parent column that is not PRIMARY KEY or UNIQUE raises `foreign key
#: mismatch` at INSERT. Whether `fields.field_key` is a primary key is Task 2's DDL
#: decision; `get_field` is the gate the SPEC names. `value_id` DOES reference
#: `"values"`, whose `value_id` is a primary key, so a fact can never cite a value that
#: does not exist.
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
    field_id           TEXT NOT NULL,
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
CREATE INDEX IF NOT EXISTS file_facts_field ON file_facts (field_id);
CREATE INDEX IF NOT EXISTS file_facts_value ON file_facts (value_id);
CREATE TRIGGER IF NOT EXISTS file_facts_no_delete
BEFORE DELETE ON file_facts
BEGIN SELECT RAISE(ABORT, 'a fact is superseded by a later fact, never removed (§8.2)'); END;
"""
```

Then one more line in `create_facts_schema`:

```python
def create_facts_schema(conn: sqlite3.Connection) -> None:
    """Create every P6-owned table. Idempotent. P1's `create_schema` runs first, and
    P4's `create_evidence_schema` before any read."""
    conn.executescript(FIELDS_DDL)
    conn.executescript(VALUES_DDL)
    conn.executescript(FILE_FACTS_DDL)
```

- [ ] **Step 4: Write `src/facts/file_facts.py`**

```python
# src/facts/file_facts.py
"""§3.12's `file_facts` -- the table that "connects one file to one field and one value
while retaining the evidence and reliability state that justify the connection."

There is ONE fact table and one set of six reliability states. §3.5: "A file fact is
not inherently rule-based or LLM-based. It is the common format into which both systems
write their conclusions." So the producer is a COLUMN (`origin`), not a second schema:
there is no rules table and no model table, and this module is the only writer.

THE NEGATIVE CONTRACT, which is this module's reason to exist as a separate file:

    §3.14  "Facts remain separate from the future destination tree. A fact such as
            subject = BUSIB 4300 does not itself dictate one permanent folder path."
    §4.3   a fact records no group membership; §4.1, the graph "does not automatically
            copy those missing facts onto sparse files".

`file_facts` therefore has no path, destination, folder, node or group column, and
`write_fact` has no such keyword either -- a keyword argument is the other way a
destination gets in. `FILE_FACTS_COLUMNS` and `FORBIDDEN_COLUMN_SUBSTRINGS` are
published so a reviewer, `unresolved` (Task 5) and Tasks 16-19 all check the same
contract against the same list rather than three lists that drift.

A fact is never separable from its evidence (§3.1: "Every fact preserves where it came
from"). Every non-`user_confirmed` fact carries at least one `evidence_refs` entry and
every entry is a P4 observation KEY -- content-addressed, `sha256:`-prefixed, and
excluding `extractor_version` by construction, which is what makes a citation recorded
today still resolve after an extractor upgrade (M14, §8.7).

`fact_id` is content-addressed over the whole conclusion, so writing the same fact at
the same cache key twice is one row and one event. §8.2's supersession is unaffected: a
later pass cites `ocr`-tier observations, so §3.4's `analysis_tier` differs, so the
cache key differs, so the id differs and the new fact supersedes rather than collides.

This module does not set `preferred` (Task 18) and appends no event but `fact creation`.
"""
from __future__ import annotations

import json
import sqlite3

from database_agent.events import append_event
from database_agent.supersede import SUPERSEDE_COLUMNS

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import check

from facts.authorship import AUTHORED_EVENT_TYPES, event_defaults
from facts.fields import get_field
from facts.states import STATES

#: §3.1's five producers, in the order the SPEC's `file_facts` shape publishes them:
#: "deterministic extractor | rule | LLM interpretation | user correction |
#: user-approved folder". Three sibling tasks address this tuple BY INDEX so that this
#: task could choose the spelling without breaking them -- reordering it would silently
#: relabel every fact they write.
FACT_ORIGINS: tuple[str, ...] = (
    "deterministic_extractor", "rule", "llm_interpretation",
    "user_correction", "user_approved_folder",
)

#: What the table is, in declaration order, minus the VIRTUAL `record_id`, which
#: `PRAGMA table_info` does not report. The test asserts this EQUALS the live column
#: set, so this tuple cannot describe a table that does not exist.
FILE_FACTS_COLUMNS: tuple[str, ...] = (
    "fact_id", "file_id", "content_hash", "field_id", "value_id",
    "reliability_state", "origin", "evidence_refs", "cited_quote_refs",
    "cache_key", "model_identifier", "prompt_fingerprint", "internal_score",
    "active", *SUPERSEDE_COLUMNS, "preferred", "rejection_reason", "created_at",
)

#: §3.14 and §4.3 as a checkable list. A SUBSTRING list, not a name list: a future
#: `destination_node_id` must fail on the day it is added, not on the day someone
#: reads the schema. Task 5's `unresolved` imports this and obeys the same contract.
FORBIDDEN_COLUMN_SUBSTRINGS: tuple[str, ...] = (
    "path", "destination", "folder", "node", "group",
)

#: STATES is P4's tuple, re-exported by Task 1 and re-spelled nowhere. Index 0 is
#: `user_confirmed`, the one state a user supplies rather than evidence.
_USER_CONFIRMED = STATES[0]

#: A P4 observation key is `sha256:` + 64 hex (M14, verified by execution).
_KEY_PREFIX = "sha256:"
_KEY_LENGTH = len(_KEY_PREFIX) + 64


class EvidenceRequired(Exception):
    """§3.1: a fact is never separable from its evidence.

    Raised when a non-`user_confirmed` fact carries no citation, or when a citation is
    not a P4 observation key. Both are refusals to store, never warnings: a fact whose
    provenance cannot be resolved is the invisible permanent label §3.1 exists to
    prevent.
    """


def _field_id(conn: sqlite3.Connection, field_key: str) -> str:
    """`get_field` raises `FieldNotInCatalogue` for a key outside Task 2's closed
    catalogue, so writing a fact is not a back door into creating a field (§3.5)."""
    return get_field(conn, field_key)["field_key"]


def _checked_refs(refs, reliability_state: str) -> tuple[str, ...]:
    """The M14 citation rule. Sorted, because P4's reads are in insertion order and
    this column must not inherit it (§8.5's replay compares runs)."""
    ordered = tuple(sorted(set(refs)))
    if reliability_state != _USER_CONFIRMED and not ordered:
        raise EvidenceRequired(
            f"a {reliability_state} fact cites at least one observation (§3.1); "
            "only a user_confirmed fact may stand without one"
        )
    for ref in ordered:
        if not ref.startswith(_KEY_PREFIX) or len(ref) != _KEY_LENGTH:
            raise EvidenceRequired(
                f"{ref!r} is not a P4 observation key; a citation is the "
                "content-addressed key, never an observation_id or a row id (M14)"
            )
    return ordered


def _fact_identity(*, file_id: str, content_hash: str, field_id: str, value_id: str,
                   reliability_state: str, origin: str, cache_key: str,
                   evidence_refs: tuple[str, ...]) -> str:
    """The same conclusion, from the same evidence, at the same cache key, is the same
    fact -- not a second one. `sha256_of` is length-prefixed and injective."""
    return sha256_of("facts.file_facts", file_id, content_hash, field_id, value_id,
                     reliability_state, origin, cache_key,
                     canonical_json(list(evidence_refs)))


def write_fact(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
               field_key: str, value_id: str, reliability_state: str, origin: str,
               evidence_refs, cache_key: str, active: bool,
               cited_quote_refs=(), model_identifier: str | None = None,
               prompt_fingerprint: str | None = None,
               internal_score: float | None = None,
               rejection_reason: str | None = None) -> str:
    """Write one fact and author its `fact creation` event. Returns the fact id.

    No path, no destination, no folder, no group -- not as a column and not as a
    keyword (§3.14, §4.3).

    Idempotent: the same conclusion at the same cache key returns the existing row and
    appends no second event, or the provenance log would count one fact twice.
    """
    check(reliability_state, STATES, name="reliability state")
    check(origin, FACT_ORIGINS, name="fact origin")
    if not cache_key:
        raise ValueError("a fact records the cache key it was computed under (§3.4)")
    refs = _checked_refs(evidence_refs, reliability_state)
    quotes = tuple(sorted(set(cited_quote_refs)))
    field_id = _field_id(conn, field_key)

    value = conn.execute(
        'SELECT field_id FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    if value is None:
        raise KeyError(f"unknown value {value_id!r}")
    if value["field_id"] != field_id:
        raise ValueError(
            f"value {value_id!r} belongs to field {value['field_id']!r}, not "
            f"{field_id!r}; a value belongs to exactly one field (§3.12), which is "
            "§3.8's role separation"
        )

    fact_id = _fact_identity(
        file_id=file_id, content_hash=content_hash, field_id=field_id,
        value_id=value_id, reliability_state=reliability_state, origin=origin,
        cache_key=cache_key, evidence_refs=refs)
    existing = conn.execute(
        "SELECT fact_id FROM file_facts WHERE fact_id = ?", (fact_id,)
    ).fetchone()
    if existing is not None:
        return existing["fact_id"]

    # One call, so the fact row's timestamp and its creation event's timestamp are the
    # same instant from the same clock. `authorship` owns that clock; this module has
    # none of its own.
    event = event_defaults(
        event_type=AUTHORED_EVENT_TYPES[0],
        file_id=file_id,
        content_hash=content_hash,
        explanation=canonical_json({
            "fact_id": fact_id,
            "field": field_key,
            "value_id": value_id,
            "reliability_state": reliability_state,
            "origin": origin,
            "cache_key": cache_key,
            "evidence_refs": list(refs),
        }),
    )
    conn.execute(
        "INSERT INTO file_facts (fact_id, file_id, content_hash, field_id, value_id, "
        "reliability_state, origin, evidence_refs, cited_quote_refs, cache_key, "
        "model_identifier, prompt_fingerprint, internal_score, active, "
        "supersedes, superseded_by, supersede_reason, preferred, rejection_reason, "
        "created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "NULL, NULL, NULL, NULL, ?, ?)",
        (fact_id, file_id, content_hash, field_id, value_id, reliability_state,
         origin, canonical_json(list(refs)), canonical_json(list(quotes)), cache_key,
         model_identifier, prompt_fingerprint, internal_score, int(bool(active)),
         rejection_reason, event["observed_at"]),
    )
    append_event(conn, **event)
    return fact_id


def facts_for_file(conn: sqlite3.Connection, file_id: str,
                   content_hash: str) -> list[sqlite3.Row]:
    """Every fact for one file VERSION, with its field key and canonical value joined
    on so no caller reassembles them.

    Per content hash, because the cache key and the abstention row both are (§3.4,
    §8.2). Sorted, because P4's reads are in insertion order and this one imposes its
    own. Unfiltered: selecting by `active`, by `preferred` or by reliability state is
    the proposal-eligible read, which Task 24 owns.
    """
    return list(conn.execute(
        'SELECT f.*, fl.field_key AS field_key, '
        '       v.canonical_value AS canonical_value, '
        '       v.display_label AS display_label '
        'FROM file_facts AS f '
        'JOIN fields AS fl ON fl.field_key = f.field_id '
        'JOIN "values" AS v ON v.value_id = f.value_id '
        'WHERE f.file_id = ? AND f.content_hash = ? '
        'ORDER BY fl.field_key, v.canonical_value, f.fact_id',
        (file_id, content_hash),
    ))
```

- [ ] **Step 5: Run the test and confirm it passes**

Run: `pytest tests/p6/test_p6_file_facts.py -v`

Expected: PASS — **25 passed**. Four are the ones a reviewer should read the output of:

- `test_the_module_declares_exactly_the_table_it_has` passes only if `FILE_FACTS_COLUMNS` and the DDL
  agree column for column and in order, which is what makes every other schema assertion in the file
  an assertion about the database rather than about the module.
- `test_the_forbidden_substring_guard_is_not_vacuous` passes because the scratch table's three
  offending columns are all caught. If it ever reports `[]`, the negative contract is proving nothing.
- `test_the_record_id_projection_lets_p1_address_the_table` passes because `PRAGMA table_xinfo`
  reports `record_id` with `hidden == 2` **and** because P1's own `mark_superseded` completes against
  the table — verified behaviour, not a claim about the DDL.
- `test_a_user_confirmed_fact_may_stand_without_an_observation` passes on `STATES[0]`, never on a
  string literal, so Task 1's re-export is what pins the spelling.

- [ ] **Step 6: Run the whole P6 suite, so Tasks 1–3 are still green**

Run: `pytest tests/p6 -q`

Expected: PASS. `create_facts_schema` now creates three tables and is still idempotent, and Task 3's
`values` tests are unaffected because `file_facts` references `"values"` and not the other way round.
A failure in `tests/p6/test_p6_values.py` here means the new foreign key changed a delete or insert
path in Task 3 and is a real finding.

- [ ] **Step 7: Commit**

```bash
git add src/facts/file_facts.py src/facts/schema.py tests/p6/test_p6_file_facts.py
git commit -m "feat(P6): §3.12's fact row — evidence required, and no path, destination, folder or group"
```
