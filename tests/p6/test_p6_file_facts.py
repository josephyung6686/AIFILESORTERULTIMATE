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

from evidence_shape.location import Location
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import NotInVocabulary

import facts.file_facts as file_facts_module
from facts.fields import FieldNotInCatalogue
from facts.file_facts import (
    DETERMINISTIC_EXTRACTOR,
    FACT_ORIGINS,
    FILE_FACTS_COLUMNS,
    FORBIDDEN_COLUMN_SUBSTRINGS,
    LLM_INTERPRETATION,
    RULE,
    USER_APPROVED_FOLDER,
    USER_CORRECTION,
    EvidenceRequired,
    facts_for_file,
    write_fact,
)
from facts.states import DIRECT, STATES, USER_CONFIRMED
from facts.values import VALUE_ORIGINS, ensure_value

FIELD = "subject"            # D6: the ratified academic field key
OTHER_FIELD = "client"       # §3.8, a role field -- a different field, same string
CONTENT_HASH = "a" * 64
OTHER_HASH = "b" * 64
FILE_ID = "file-1"
CACHE_KEY = "sha256:" + "c" * 64
CLOCK = "2026-08-25T12:00:00+00:00"


def _key(raw: str, *, locator: str = "heading:page=1/heading=2") -> str:
    return observation_key(content_hash=CONTENT_HASH, extractor_name="pdf.text",
                           locator=locator, raw_value=raw)


def _value(conn, *, field_key: str = FIELD, canonical: str = "BUSIB 4300") -> str:
    return ensure_value(conn, field_key=field_key, canonical_value=canonical,
                        first_evidence_ref=_key(canonical), origin=VALUE_ORIGINS[0])


def _write(conn, **overrides) -> str:
    kwargs = dict(file_id=FILE_ID, content_hash=CONTENT_HASH, field_key=FIELD,
                  value_id=_value(conn), reliability_state=DIRECT,
                  origin=DETERMINISTIC_EXTRACTOR, evidence_refs=(_key("BUSIB 4300"),),
                  cache_key=CACHE_KEY, active=True)
    kwargs.update(overrides)
    return write_fact(conn, **kwargs)


def _stored_observation(conn, *, raw: str = "BUSIB 4300") -> Observation:
    run_id = f"run-{raw}"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=FILE_ID, content_hash=CONTENT_HASH,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK,
    ))
    observation = Observation(
        file_id=FILE_ID, content_hash=CONTENT_HASH, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("heading", ()), occurrence_count=1, observed_at=CLOCK,
        reliability="possible", run_id=run_id,
    )
    record_observation(conn, observation)
    return observation


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
    for column in ("fact_id", "file_id", "content_hash", "field_key", "value_id",
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
    assert row["reliability_state"] == DIRECT == "direct"
    assert row["origin"] == DETERMINISTIC_EXTRACTOR
    assert json.loads(row["evidence_refs"]) == [_key("BUSIB 4300")]
    assert row["active"] == 1


def test_the_read_projects_field_key_exactly_once(p6_conn):
    _write(p6_conn)
    row = facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)[0]
    assert row.keys().count("field_key") == 1


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


def test_every_cited_quote_ref_must_be_a_p4_observation_key(p6_conn):
    for bad in (None, "observation-17", "", "sha255:" + "0" * 64, "0" * 64):
        with pytest.raises(EvidenceRequired):
            _write(p6_conn, cited_quote_refs=(bad,))
    assert facts_for_file(p6_conn, FILE_ID, CONTENT_HASH) == []


def test_every_cited_quote_ref_must_resolve_to_stored_evidence(p6_conn):
    absent = observation_key(
        content_hash=CONTENT_HASH, extractor_name="pdf.text",
        locator="heading:", raw_value="not stored",
    )
    with pytest.raises(EvidenceRequired, match="resolves to no stored observation"):
        _write(p6_conn, cited_quote_refs=(absent,))
    assert facts_for_file(p6_conn, FILE_ID, CONTENT_HASH) == []


def test_cited_quote_refs_round_trip_as_sorted_observation_keys(p6_conn):
    first = _stored_observation(p6_conn, raw="BUSIB 4300")
    second = _stored_observation(p6_conn, raw="Spring 2026")
    fact_id = _write(
        p6_conn,
        cited_quote_refs=(second.observation_key, first.observation_key,
                          second.observation_key),
    )
    row = p6_conn.execute(
        "SELECT cited_quote_refs FROM file_facts WHERE fact_id = ?", (fact_id,)
    ).fetchone()
    assert json.loads(row["cited_quote_refs"]) == sorted(
        {first.observation_key, second.observation_key}
    )


def test_a_user_confirmed_fact_may_stand_without_an_observation(p6_conn):
    # A user asserting a fact is not citing evidence, and demanding one would make
    # the user path impossible rather than careful.
    fact_id = _write(p6_conn, reliability_state=USER_CONFIRMED,
                     origin=USER_CORRECTION, evidence_refs=())
    row = [r for r in facts_for_file(p6_conn, FILE_ID, CONTENT_HASH)
           if r["fact_id"] == fact_id][0]
    assert row["reliability_state"] == USER_CONFIRMED == "user_confirmed"
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


def test_each_origin_has_a_named_constant_so_no_consumer_needs_an_index(p6_conn):
    # Preamble §3.1. An index is single-homed and unreadable, and it couples every
    # consumer to this tuple's ORDER -- reorder it and every fact three other tasks
    # write is relabelled with no test failing. This test is what makes the literal
    # safe to spell here and nowhere else.
    named = (DETERMINISTIC_EXTRACTOR, RULE, LLM_INTERPRETATION, USER_CORRECTION,
             USER_APPROVED_FOLDER)
    assert named == FACT_ORIGINS
    assert len(set(named)) == 5


def test_fact_creation_event_does_not_follow_authored_tuple_reordering(
        p6_conn, monkeypatch):
    # Selecting AUTHORED_EVENT_TYPES[0] silently changes meaning when the owning
    # vocabulary is reordered. The writer binds the semantic name instead.
    monkeypatch.setattr(
        file_facts_module, "AUTHORED_EVENT_TYPES",
        tuple(reversed(file_facts_module.AUTHORED_EVENT_TYPES)),
    )
    _write(p6_conn)
    event = p6_conn.execute("SELECT event_type FROM events").fetchone()
    assert event["event_type"] == "fact creation"


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


class _FailsOnTheEventInsert:
    """P1's handle, with the event INSERT turned into a crash.

    Everything else — P1's own `BEGIN` / `ROLLBACK`, the SELECTs, the fact INSERT —
    reaches the real connection, so the write fails exactly where a half-written
    fact would fail and nowhere else. P1's `transaction` is used, never mocked.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def __getattr__(self, name: str):
        return getattr(self._conn, name)

    def execute(self, sql: str, *args):
        if sql.startswith("INSERT INTO events"):
            raise sqlite3.OperationalError("disk I/O error")
        return self._conn.execute(sql, *args)


def test_a_write_that_fails_on_the_event_absorbs_nothing(p6_conn):
    # The fact INSERT and its `fact creation` event are one provenance record.
    # Written outside a transaction they commit independently, and a crash on
    # the event leaves a `file_facts` row with no event — the §8.2 hole this
    # module's docstring is written against.
    with pytest.raises(sqlite3.OperationalError):
        _write(_FailsOnTheEventInsert(p6_conn))

    assert p6_conn.execute("SELECT COUNT(*) FROM file_facts").fetchone()[0] == 0
    assert p6_conn.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0


def test_a_second_write_that_diverges_on_a_non_identity_column_is_refused(p6_conn):
    # Identity ignores active, cited_quote_refs, model_identifier,
    # prompt_fingerprint, internal_score and rejection_reason. A second write
    # that changes one of those is not a re-write — changing `active` is Task
    # 16's supersession path. The stored row must stay as first written.
    first = _write(p6_conn, active=True)
    identical = _write(p6_conn, active=True)
    assert identical == first

    with pytest.raises(ValueError, match="active"):
        _write(p6_conn, active=False)

    row = p6_conn.execute(
        "SELECT active FROM file_facts WHERE fact_id = ?", (first,)
    ).fetchone()
    assert row["active"] == 1
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
