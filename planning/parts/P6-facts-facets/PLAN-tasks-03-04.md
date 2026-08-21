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
