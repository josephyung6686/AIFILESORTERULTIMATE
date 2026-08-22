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


class _FailsOnTheMergePointer:
    """P1's handle, with the "point `merged` at `keep`" UPDATE turned into a crash.

    Everything else -- P1's own `BEGIN` / `ROLLBACK`, the SELECTs, the alias UPDATE --
    reaches the real connection, so the merge fails exactly where a half-written merge
    would fail and nowhere else. P1's `transaction` is used, never mocked.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def __getattr__(self, name: str):
        return getattr(self._conn, name)

    def execute(self, sql: str, *args):
        if sql.startswith('UPDATE "values" SET merged_into'):
            raise sqlite3.OperationalError("disk I/O error")
        return self._conn.execute(sql, *args)


def test_a_merge_that_fails_halfway_absorbs_nothing(p6_conn):
    # §8.2's alias record is one fact in two rows: the survivor gains the alias and
    # the merged row names where it went. Written outside a transaction they commit
    # independently, and a crash between them leaves `keep` holding an alias for a
    # value whose `merged_into` is still NULL -- a state no invariant here rejects and
    # Task 4's `file_facts`, which point at `value_id`, would resolve wrongly.
    keep = ensure_value(p6_conn, field_key=FIELD, canonical_value=CANONICAL,
                        first_evidence_ref=_key(RAW), origin=VALUE_ORIGINS[0])
    merged = ensure_value(p6_conn, field_key=FIELD, canonical_value="U Chicago",
                          first_evidence_ref=_key(RAW, locator="filename:name"),
                          origin=VALUE_ORIGINS[0])
    add_raw_variant(p6_conn, merged, "U Chicago")
    before = _row(p6_conn, keep)
    aliases_before, variants_before = before["aliases"], before["raw_variants"]

    with pytest.raises(sqlite3.OperationalError):
        merge_values(_FailsOnTheMergePointer(p6_conn), keep=keep, merged=merged,
                     reason="one university under two wordings")

    after = _row(p6_conn, keep)
    assert after["aliases"] == aliases_before
    assert after["raw_variants"] == variants_before
    assert _row(p6_conn, merged)["merged_into"] is None
    assert _row(p6_conn, merged)["merge_reason"] is None


# ------------------------------------------------------------------------ §8.8 held
def test_the_display_label_is_stored_unscoped_and_no_plan_version_is_invented(p6_conn):
    # §8.8 puts "User labels and aliases" inside a plan version; Task 22 owns that
    # scoping. This task must not invent a plan_version keyword no caller can supply.
    import inspect
    assert "plan_version" not in inspect.signature(set_display_label).parameters
    columns = {r["name"] for r in p6_conn.execute('PRAGMA table_info("values")')}
    assert "plan_version" not in columns
