# tests/p6/test_p6_plan_versions.py
"""§8.8: the evidence database is shared across plan versions; the rendering is not.

The negative half is the one that matters and it is enforced by absence -- no P6
record table has a plan-version column, so there is nowhere a version could be
written. The positive half is one side table holding the label a plan version chose.

The fixtures build on `p6_conn` (preamble §3.6) rather than re-creating the schema:
the only thing this file adds is `create_plan_version_tables`, because Task 23's Files
block names no `modify src/facts/schema.py` and the aggregate creator does not call it
yet (reported as an owed line, not edited here).
"""
from __future__ import annotations

import pytest

from database_agent.supersede import SUPERSEDE_COLUMNS

from evidence_shape.observation import observation_key

from facts.cache import fact_cache_key
from facts.file_facts import (
    DETERMINISTIC_EXTRACTOR, FILE_FACTS_COLUMNS, write_fact,
)
from facts.plan_versions import (
    PLAN_VERSIONED,
    SHARED_ACROSS_PLAN_VERSIONS,
    VALUE_RENDERINGS_COLUMNS,
    create_plan_version_tables,
    display_label,
    set_display_label,
)
from facts.values import VALUE_ORIGINS, ensure_value

CONTENT_HASH = "sha256:" + "a" * 64
FORBIDDEN = ("path", "destination", "folder", "node", "group")
RECORD_TABLES = ("fields", "values", "file_facts", "unresolved")

REF = observation_key(
    content_hash=CONTENT_HASH,
    extractor_name="pdf.text",
    locator="heading:page=1/heading=2",
    raw_value="University of Chicago",
)
CACHE_KEY = fact_cache_key(
    content_hash=CONTENT_HASH,
    extractor_version="1.0.0",
    analysis_tier="native",
    model_identifier=None,
    prompt_fingerprint=None,
)


@pytest.fixture()
def conn(p6_conn):
    create_plan_version_tables(p6_conn)
    return p6_conn


@pytest.fixture()
def value_id(conn) -> str:
    # §3.8's target_school, which D1 ratifies into the catalogue. §2.8's three
    # renderings of one institution are the design's own worked example.
    return ensure_value(
        conn,
        field_key="target_school",
        canonical_value="University of Chicago",
        first_evidence_ref=REF,
        origin=VALUE_ORIGINS[0],
    )


@pytest.fixture()
def fact_id(conn, value_id) -> str:
    return write_fact(
        conn,
        file_id="file-1",
        content_hash=CONTENT_HASH,
        field_key="target_school",
        value_id=value_id,
        reliability_state="direct",
        origin=DETERMINISTIC_EXTRACTOR,
        evidence_refs=(REF,),
        cache_key=CACHE_KEY,
        active=True,
    )


def snapshot(connection) -> dict[str, list[str]]:
    """Every table's every row, byte-for-byte.

    Rows are compared as sorted reprs: SQLite guarantees no row order without an
    ORDER BY, `ORDER BY rowid` is not available on every table, and sorting the
    tuples themselves would compare None against str. Sorted reprs are total,
    deterministic, and still catch a single changed byte in any column.
    """
    names = [
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        )
    ]
    return {
        name: sorted(
            repr(tuple(row)) for row in connection.execute(f'SELECT * FROM "{name}"')
        )
        for name in names
    }


# --- the declaration -------------------------------------------------------------


def test_the_two_tuples_name_the_8_8_split_and_do_not_overlap():
    assert PLAN_VERSIONED == ("display_label", "aliases")
    assert set(PLAN_VERSIONED).isdisjoint(SHARED_ACROSS_PLAN_VERSIONS)
    for name in RECORD_TABLES:
        assert name in SHARED_ACROSS_PLAN_VERSIONS
    for name in ("evidence_refs", "reliability_state", "supersession_history"):
        assert name in SHARED_ACROSS_PLAN_VERSIONS


def test_what_is_declared_shared_is_actually_a_shared_record(conn):
    # §8.8: "The evidence database remains shared across plan versions."
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    for name in RECORD_TABLES:
        assert name in tables
    assert "evidence_refs" in FILE_FACTS_COLUMNS
    assert "reliability_state" in FILE_FACTS_COLUMNS
    for column in SUPERSEDE_COLUMNS:
        assert column in FILE_FACTS_COLUMNS


def test_no_record_table_carries_a_plan_version_column(conn):
    # Enforced by absence: there is nowhere a version could be written.
    for name in RECORD_TABLES:
        columns = {row[1] for row in conn.execute(f'PRAGMA table_info("{name}")')}
        assert "plan_version" not in columns, name
        assert "plan_id" not in columns, name


def test_no_plan_versioned_attribute_is_a_fact_column():
    # A fact is a claim, not a rendering. If `display_label` ever became a
    # `file_facts` column, a label change would rewrite facts.
    assert set(FILE_FACTS_COLUMNS).isdisjoint(PLAN_VERSIONED)


def test_the_renderings_table_is_keyed_by_version_and_carries_no_destination(conn):
    assert VALUE_RENDERINGS_COLUMNS == ("value_id", "plan_version", "display_label")
    columns = [row[1] for row in conn.execute("PRAGMA table_info(value_renderings)")]
    assert tuple(columns) == VALUE_RENDERINGS_COLUMNS
    # §3.14's negative contract, applied to this table too.
    for column in columns:
        for forbidden in FORBIDDEN:
            assert forbidden not in column, column


def test_creating_the_table_twice_is_not_an_error_and_loses_no_rendering(conn, value_id):
    # The aggregate creator is owed a call to this; a second call from a test or a
    # later wave must not drop what a version already chose.
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    create_plan_version_tables(conn)
    assert display_label(conn, value_id=value_id, plan_version="v2") == "UChicago"


# --- the rendering ---------------------------------------------------------------


def test_two_plan_versions_render_one_value_two_ways(conn, value_id):
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    set_display_label(
        conn, value_id=value_id, plan_version="v3", label="University of Chicago"
    )
    assert display_label(conn, value_id=value_id, plan_version="v2") == "UChicago"
    assert (
        display_label(conn, value_id=value_id, plan_version="v3")
        == "University of Chicago"
    )


def test_a_version_that_chose_nothing_falls_back_and_never_borrows(conn, value_id):
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    # v3 chose nothing, so it renders the value's own label -- NOT v2's choice. A
    # rendering is scoped to the version that made it.
    assert display_label(conn, value_id=value_id, plan_version="v3") != "UChicago"


def test_one_values_rendering_is_never_another_values(conn, value_id):
    other = ensure_value(
        conn,
        field_key="target_school",
        canonical_value="Northwestern University",
        first_evidence_ref=REF,
        origin=VALUE_ORIGINS[0],
    )
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    assert display_label(conn, value_id=other, plan_version="v2") == (
        "Northwestern University"
    )


def test_the_fallback_chain_ends_at_the_canonical_string(conn, value_id):
    # Total by construction: §5.5's preview needs something to show for every value,
    # and a renderer that can return None shows nothing on a version that chose none.
    rendered = display_label(conn, value_id=value_id, plan_version="v9")
    assert isinstance(rendered, str) and rendered != ""
    assert rendered == "University of Chicago"


def test_re_rendering_the_same_version_replaces_rather_than_duplicates(conn, value_id):
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    set_display_label(conn, value_id=value_id, plan_version="v2", label="U Chicago")
    rows = conn.execute("SELECT COUNT(*) AS n FROM value_renderings").fetchone()["n"]
    assert rows == 1
    assert display_label(conn, value_id=value_id, plan_version="v2") == "U Chicago"


def test_a_rendering_for_a_value_that_does_not_exist_is_refused(conn):
    with pytest.raises(ValueError):
        set_display_label(
            conn, value_id="no-such-value", plan_version="v2", label="Ghost"
        )
    rows = conn.execute("SELECT COUNT(*) AS n FROM value_renderings").fetchone()["n"]
    assert rows == 0


def test_rendering_a_value_that_does_not_exist_is_refused_rather_than_invented(conn):
    with pytest.raises(ValueError):
        display_label(conn, value_id="no-such-value", plan_version="v2")


def test_a_rendering_without_a_plan_version_is_refused(conn, value_id):
    with pytest.raises(ValueError):
        set_display_label(conn, value_id=value_id, plan_version="", label="UChicago")


def test_an_empty_label_is_not_a_choice(conn, value_id):
    # §2.8's rendering is a wording the user picked; clearing one is a different
    # operation and no Done-means asks for it.
    with pytest.raises(ValueError):
        set_display_label(conn, value_id=value_id, plan_version="v2", label="")
    rows = conn.execute("SELECT COUNT(*) AS n FROM value_renderings").fetchone()["n"]
    assert rows == 0


# --- the guarantee ---------------------------------------------------------------


def test_a_new_plan_version_changes_no_shared_record_byte_for_byte(
    conn, value_id, fact_id
):
    before = snapshot(conn)
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    set_display_label(
        conn, value_id=value_id, plan_version="v3", label="University of Chicago"
    )
    after = snapshot(conn)
    assert set(before) == set(after)
    for name in after:
        if name == "value_renderings":
            continue
        assert after[name] == before[name], name
    # And the versioned table is the only thing that moved.
    assert len(after["value_renderings"]) == 2
    assert before["value_renderings"] == []


def test_the_value_itself_is_untouched_by_a_rendering_change(conn, value_id):
    before = conn.execute(
        'SELECT * FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    after = conn.execute(
        'SELECT * FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    assert tuple(after) == tuple(before)


def test_every_fact_pointing_at_the_value_still_resolves_unchanged(
    conn, value_id, fact_id
):
    before = [
        tuple(row)
        for row in conn.execute(
            "SELECT * FROM file_facts WHERE value_id = ?", (value_id,)
        )
    ]
    assert len(before) == 1
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    after = [
        tuple(row)
        for row in conn.execute(
            "SELECT * FROM file_facts WHERE value_id = ?", (value_id,)
        )
    ]
    assert after == before


def test_a_rendering_change_re_resolves_nothing_and_invalidates_no_cache_key(
    conn, value_id, fact_id
):
    # §3.4's cache key has five parts and a plan version is none of them, so a plan
    # edit cannot invalidate a fact. §8.8: "A new plan should never silently
    # reclassify or move old files."
    before = conn.execute(
        "SELECT cache_key FROM file_facts WHERE fact_id = ?", (fact_id,)
    ).fetchone()["cache_key"]
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    after = conn.execute(
        "SELECT cache_key FROM file_facts WHERE fact_id = ?", (fact_id,)
    ).fetchone()["cache_key"]
    assert after == before == CACHE_KEY


def test_p6_appends_no_event_for_a_rendering_change(conn, value_id, fact_id):
    # §8.8's diff belongs to the plan-version object, which is P10's and P12's. P6
    # mints no §8.2 type here and writes none of anyone else's.
    before = conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]
    set_display_label(conn, value_id=value_id, plan_version="v2", label="UChicago")
    after = conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]
    assert after == before
