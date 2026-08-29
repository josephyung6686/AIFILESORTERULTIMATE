# tests/p7/test_p7_classification_store.py
"""Done-means 2's second half: exactly one current classification per file version,
supersede-never-overwrite through P1's three columns, and the projection onto
`files.sensitivity_state` through P1's published setter.

Three things this file deliberately does NOT do.

It creates no `file_facts` row and imports nothing from a P6 module, because D2 made
P7's `ClassificationRecord` authoritative and there is no P6 record to read. P7's
SPEC still says "P6 must accept `sensitivity` as a first-class universal field" while
round 1 found that field has no producer; that conflict is Joseph's (NEEDS-JOSEPH C5)
and this file is written so nothing in it depends on the answer.

It stores no `unreadable_unclassified` record and never lets one reach the column.
That value is a GATE OUTCOME (D2) -- what the release decision says when it has no
classification to release against -- and storing it would make "nothing has looked"
read as "this file carries nothing".

It writes its own classifications and says so, because the detector is unwritten (D2)
and on a real corpus every file would resolve to `Denied(unclassified)`. A fixture
standing in for a detector is the honest v1 posture; a fixture pretending to BE one
is not.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from database_agent.files_table import FILES_COLUMNS, get_file, record_file
from database_agent.supersede import SUPERSEDE_COLUMNS, chain

from evidence_shape.observation import observation_key

from privacy.authorship import SUBSYSTEM
from privacy.classification import UNREADABLE_UNCLASSIFIED, ClassificationRecord
from privacy.classification_store import (
    REJECTED,
    RELIABILITY_ORDER,
    AmbiguousCurrentClassification,
    ClassificationStore,
    GateOutcomeNotAFileFact,
    UnrankedReliability,
    mirror,
    mirror_state,
    strongest,
)
from privacy.schema import (
    CLASSIFICATIONS_TABLE,
    SUPERSEDE_ADAPTER_COLUMN,
    create_privacy_schema,
)
from privacy.vocabulary import RELIABILITY_STATES, USER, USER_CONFIRMED

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"

#: Bare hex digests, because that is what P1 stores (R1) and what P4 refuses to
#: accept anything else as: `MalformedRun: content_hash is the digest P1 stored`.
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_EDITED = "e" * 64


def a_key(raw_value: str, locator: str) -> str:
    """A real P4 citation handle. `ClassificationRecord` refuses anything else (M14):
    a per-row `observation_id` dies on extractor upgrade, so the record checks the
    shape of the handle rather than trusting the caller. These are therefore minted
    through P4's own `observation_key` and never spelled as opaque placeholders."""
    return observation_key(content_hash=HASH_A, extractor_name="pdf_text",
                           locator=locator, raw_value=raw_value)


#: §8.4: "A scanned passport ... should enter a protected state immediately." The
#: DETECTOR that would notice is unwritten (D2), so the test plays its part and the
#: `basis` says which part it is playing.
PASSPORT_KEYS = (
    a_key("P<GBRSPECIMEN<<JANE<<<<<<<<<<<", "zone=ocr/page=1/region=1"),
    a_key("Passport No. 123456789", "zone=ocr/page=1/region=2"),
)

#: Two distinct handles, for the case where two live records disagree.
KEY_A = a_key("first reading", "zone=body/page=1")
KEY_B = a_key("second reading", "zone=body/page=2")


def a_file(conn, tmp_path: Path, *, name: str = "passport.pdf",
           content_hash: str = HASH_A) -> str:
    """A `files` row. `record_file` stats the path, so the bytes must exist."""
    path = tmp_path / name
    path.write_bytes(b"scanned passport")
    return record_file(
        conn, path, filename=name, normalized_filename=name.rsplit(".", 1)[0],
        extension=".pdf", observed_size=path.stat().st_size,
        observed_timestamps="{}", parent_folder_context=None, mime_type=None,
        detected_format=None, scan_state="seen", materialized=True,
        content_hash=content_hash)


def a_record(**over) -> ClassificationRecord:
    base = dict(file_id="file-1", content_hash=HASH_A,
                handling_class="highly_sensitive_credential_bearing",
                protected=True, basis="detector", evidence_refs=PASSPORT_KEYS,
                reliability_state="validated", observed_at=FIXED_CLOCK)
    base.update(over)
    return ClassificationRecord(**base)


@pytest.fixture()
def store(p7_conn) -> ClassificationStore:
    return ClassificationStore(p7_conn)


def test_store_reports_only_its_exact_bound_connection(p7_conn):
    store = ClassificationStore(p7_conn)
    other = sqlite3.connect(":memory:")
    try:
        assert store.bound_to(p7_conn) is True
        assert store.bound_to(other) is False
    finally:
        other.close()


# --- the table P7 creates and owns ------------------------------------------

def test_the_schema_is_idempotent(p7_conn):
    # `p7_conn` already created it; a second call is a no-op, the way P4's
    # `create_evidence_schema` is.
    create_privacy_schema(p7_conn)
    create_privacy_schema(p7_conn)


def test_the_table_carries_p1s_three_supersede_columns_under_p1s_spelling(p7_conn):
    # M1, and MINOR 3 confirms the spelling is `supersede_reason`. P7 does not
    # re-spell the set and does not add a fourth.
    columns = {row["name"] for row in p7_conn.execute(
        f"PRAGMA table_info({CLASSIFICATIONS_TABLE})")}
    assert set(SUPERSEDE_COLUMNS) <= columns
    assert "preferred" not in columns


def test_record_id_is_a_virtual_projection_of_the_published_fact_id(p7_conn):
    # P1's `mark_superseded` and `chain` are `... WHERE record_id = ?`, and P7's
    # published id is `fact_id`. P4 solved this once (`SUPERSEDE_ADAPTER_COLUMN`)
    # and P7 copies the solution rather than a second supersede implementation.
    assert SUPERSEDE_ADAPTER_COLUMN == "record_id"
    visible = {row["name"] for row in p7_conn.execute(
        f"PRAGMA table_info({CLASSIFICATIONS_TABLE})")}
    assert "fact_id" in visible
    assert "record_id" not in visible          # VIRTUAL: absent from table_info
    hidden = {row["name"] for row in p7_conn.execute(
        f"PRAGMA table_xinfo({CLASSIFICATIONS_TABLE})")}
    assert "record_id" in hidden


def test_a_classification_cannot_be_deleted(p7_conn, store):
    # §8.2's rule, and §8.7 needs the rejected proposal's evidence to survive.
    fact_id = store.write(a_record())
    with pytest.raises(sqlite3.IntegrityError, match="superseded"):
        p7_conn.execute(
            f"DELETE FROM {CLASSIFICATIONS_TABLE} WHERE fact_id = ?", (fact_id,))


def test_a_classification_cannot_be_overwritten(p7_conn, store):
    # §8.2 forbids overwriting the earlier record. The three supersede columns are
    # outside the trigger: supersession is the one legal write to an existing row.
    fact_id = store.write(a_record())
    with pytest.raises(sqlite3.IntegrityError, match="superseded"):
        p7_conn.execute(
            f"UPDATE {CLASSIFICATIONS_TABLE} SET handling_class = ? WHERE fact_id = ?",
            ("public_low", fact_id))


def test_p7_adds_no_column_to_p1s_files_table(p7_conn):
    # P7 creates and modifies no file owned by another part, and `sensitivity_state`
    # has been on `files` since P1's first schema.
    columns = tuple(row["name"] for row in p7_conn.execute("PRAGMA table_info(files)"))
    assert columns == FILES_COLUMNS


# --- one current record per file VERSION ------------------------------------

def test_write_returns_a_fact_id_and_current_reads_the_record_back(store):
    record = a_record()
    fact_id = store.write(record)
    assert isinstance(fact_id, str) and fact_id
    assert store.current("file-1", HASH_A) == record


def test_current_is_keyed_on_the_content_hash_and_not_on_the_file_id(store):
    store.write(a_record())
    assert store.current("file-1", HASH_B) is None


def test_new_bytes_at_the_same_file_inherit_nothing(store):
    # D2: "a classification is about BYTES; new bytes at a path are a new file
    # version and inherit nothing." The edited scan reads as unlooked-at, which is
    # what makes `Denied(unclassified)` correct rather than a regression.
    store.write(a_record())
    assert store.current("file-1", HASH_EDITED) is None
    assert store.current_fact_id("file-1", HASH_EDITED) is None


def test_current_is_none_before_anything_classifies(store):
    # The detector is unwritten (D2). This is the state a real corpus is in.
    assert store.current("file-unknown", "sha256:zzz") is None


def test_current_fact_id_returns_the_unsuperseded_row(store):
    old = store.write(a_record())
    new = store.write(a_record(reliability_state=USER_CONFIRMED, observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    assert store.current_fact_id("file-1", HASH_A) == new


# --- §3.13's ordering, quoted and not re-derived ----------------------------

def test_the_ordering_is_the_designs_listed_order(store):
    # The design lists them in this order and states no comparison rule. The
    # spellings are P4's -- `evidence_shape.vocabulary.RELIABILITY_STATES`, which
    # Task 2 re-exports -- and this module retypes none of them: the ranking is the
    # published tuple with the one unranked state removed, in place.
    assert RELIABILITY_ORDER == (
        "user_confirmed", "direct", "validated", "llm_supported", "possible")
    assert REJECTED == "rejected"
    assert REJECTED not in RELIABILITY_ORDER
    assert RELIABILITY_ORDER == tuple(
        state for state in RELIABILITY_STATES if state != REJECTED)
    assert set(RELIABILITY_ORDER) | {REJECTED} == set(RELIABILITY_STATES)


def test_the_ranking_head_is_task_2s_named_constant(store):
    # Brief §11: never a bare string, never an index. The strongest state is the one
    # P7 itself writes (Task 16), so it is the one with a name.
    assert RELIABILITY_ORDER[0] == USER_CONFIRMED


def test_a_user_confirmed_record_outranks_a_validated_one(store):
    validated = a_record(reliability_state="validated")
    confirmed = a_record(reliability_state=USER_CONFIRMED,
                         handling_class="personal_non_sensitive", protected=False,
                         basis=USER, evidence_refs=(), observed_at=LATER)
    store.write(validated)
    store.write(confirmed)
    assert store.current("file-1", HASH_A) == confirmed


def test_the_ordering_holds_regardless_of_write_order(store):
    confirmed = a_record(reliability_state=USER_CONFIRMED, basis=USER,
                         evidence_refs=())
    store.write(confirmed)
    store.write(a_record(reliability_state="direct", observed_at=LATER))
    assert store.current("file-1", HASH_A) == confirmed


def test_strongest_reads_the_order_and_computes_no_score(store):
    records = [a_record(reliability_state=state) for state in
               ("possible", "llm_supported", "direct", USER_CONFIRMED, "validated")]
    assert strongest(records).reliability_state == USER_CONFIRMED
    assert strongest(records[:1]).reliability_state == "possible"


def test_strongest_of_nothing_is_a_programming_error(store):
    with pytest.raises(ValueError):
        strongest(())


def test_a_rejected_record_is_stored_and_is_never_current(store):
    # §8.7: rejections are stored "with the evidence that produced them". A rejected
    # fact is a record of a proposal the user marked incorrect, so it must survive
    # and must never be the answer to "what is this file".
    rejected = store.write(a_record(reliability_state=REJECTED))
    assert store.current("file-1", HASH_A) is None
    assert [r.reliability_state for r in store.history("file-1")] == [REJECTED]
    assert rejected


def test_an_unranked_reliability_raises_rather_than_sorting_last(store):
    # A value outside §3.13's six is a load error, not a fallback. Sorting it last
    # would let an unknown state quietly become the weakest evidence in the product.
    with pytest.raises(UnrankedReliability):
        strongest([a_record(reliability_state="probably_fine")])


def test_two_live_records_at_the_same_rank_raise_rather_than_pick(store):
    store.write(a_record(evidence_refs=(KEY_A,)))
    store.write(a_record(evidence_refs=(KEY_B,), observed_at=LATER))
    with pytest.raises(AmbiguousCurrentClassification):
        store.current("file-1", HASH_A)


# --- supersede, never overwrite ---------------------------------------------

def test_a_revision_supersedes_through_p1s_three_columns(p7_conn, store):
    old = store.write(a_record())
    new = store.write(a_record(handling_class="personal_non_sensitive", protected=False,
                               basis=USER, evidence_refs=(),
                               reliability_state=USER_CONFIRMED, observed_at=LATER))
    store.supersede(old, new, "user reclassified as non-sensitive")
    row = p7_conn.execute(
        f"SELECT * FROM {CLASSIFICATIONS_TABLE} WHERE fact_id = ?", (old,)).fetchone()
    assert row["superseded_by"] == new
    assert row["supersede_reason"] == "user reclassified as non-sensitive"
    assert p7_conn.execute(
        f"SELECT supersedes FROM {CLASSIFICATIONS_TABLE} WHERE fact_id = ?",
        (new,)).fetchone()["supersedes"] == old


def test_both_records_remain_readable_afterwards(store):
    # §8.2's explicit rule, and its OCR example applies directly: an early detector
    # and a later one may disagree and both survive.
    old = store.write(a_record())
    new = store.write(a_record(reliability_state=USER_CONFIRMED, basis=USER,
                               evidence_refs=(), observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    history = store.history("file-1")
    assert len(history) == 2
    assert {r.basis for r in history} == {"detector", "user"}


def test_the_chain_is_p1s_and_p7_does_not_copy_it(p7_conn, store):
    old = store.write(a_record())
    new = store.write(a_record(reliability_state=USER_CONFIRMED, basis=USER,
                               evidence_refs=(), observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    assert [row["fact_id"] for row in chain(p7_conn, CLASSIFICATIONS_TABLE, old)] == \
        [old, new]


def test_the_first_supersede_reason_is_never_overwritten(store):
    old = store.write(a_record())
    new = store.write(a_record(reliability_state=USER_CONFIRMED, basis=USER,
                               evidence_refs=(), observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    third = store.write(a_record(reliability_state="direct", observed_at=LATER))
    with pytest.raises(ValueError, match="already superseded"):
        store.supersede(old, third, "a second reason")


def test_a_superseded_record_is_not_current(store):
    old = store.write(a_record(reliability_state=USER_CONFIRMED, basis=USER,
                               evidence_refs=()))
    new = store.write(a_record(reliability_state="validated", observed_at=LATER))
    store.supersede(old, new, "detector re-ran on better evidence")
    # The superseded record outranks the survivor by §3.13, and is still not the
    # answer: supersession is a stronger statement than reliability.
    assert store.current("file-1", HASH_A).reliability_state == "validated"


def test_history_is_oldest_first_and_spans_file_versions(store):
    store.write(a_record(observed_at=FIXED_CLOCK))
    store.write(a_record(content_hash=HASH_EDITED, observed_at=LATER))
    assert [r.content_hash for r in store.history("file-1")] == \
        [HASH_A, HASH_EDITED]


# --- the projection onto files.sensitivity_state ----------------------------

def test_the_mirror_goes_through_p1s_published_setter(p7_conn, tmp_path):
    # D2: the column is the record's PROJECTION, written through the twin of
    # `set_extraction_status`. P5 took the identical position on
    # `extraction_status_by_tier` and the resolution was P1 publishing the setter.
    file_id = a_file(p7_conn, tmp_path)
    record = a_record(file_id=file_id)
    mirror(p7_conn, record, component_version=COMPONENT)
    stored = json.loads(get_file(p7_conn, file_id)["sensitivity_state"])
    assert stored == mirror_state(record)


def test_privacy_issues_no_update_files_of_its_own(p7_conn, tmp_path):
    # Asserted by RUNTIME TRACE, not by grepping source text: `set_trace_callback`
    # sees the statements sqlite actually executed, and a comment or a docstring
    # cannot fake one. Exactly one `UPDATE files` runs and it is P1's, verbatim.
    file_id = a_file(p7_conn, tmp_path)
    statements: list[str] = []
    p7_conn.set_trace_callback(statements.append)
    try:
        mirror(p7_conn, a_record(file_id=file_id), component_version=COMPONENT)
    finally:
        p7_conn.set_trace_callback(None)
    updates = [s for s in statements if s.lstrip().upper().startswith("UPDATE FILES")]
    assert len(updates) == 1
    assert updates[0].startswith("UPDATE files SET sensitivity_state = ")


def test_the_mirror_authors_as_p7(p7_conn, tmp_path, monkeypatch):
    # M8: the acting part authors, P1 stores. `author` is not a parameter a caller
    # of `mirror` may set.
    import privacy.classification_store as module
    seen: dict[str, object] = {}
    monkeypatch.setattr(
        module, "set_sensitivity_state",
        lambda conn, file_id, **fields: seen.update(fields, file_id=file_id))
    mirror(p7_conn, a_record(file_id="file-1"), component_version=COMPONENT)
    assert seen["author"] == SUBSYSTEM == "P7"
    assert seen["component_version"] == COMPONENT


def test_the_projection_carries_the_record_and_not_a_second_vocabulary(store):
    record = a_record()
    state = mirror_state(record)
    assert state == {
        "handling_class": "highly_sensitive_credential_bearing",
        "protected": True,
        "basis": "detector",
        "reliability_state": "validated",
        "content_hash": HASH_A,
        "evidence_refs": list(PASSPORT_KEYS),
        "observed_at": FIXED_CLOCK,
    }


def test_the_projection_is_json_serialisable_the_way_p1_stores_it(store):
    # P1 does `json.dumps(state, sort_keys=True)` and holds no handling-class
    # vocabulary: a class P1 has never heard of round-trips unchanged.
    state = mirror_state(a_record())
    assert json.loads(json.dumps(state, sort_keys=True)) == state


def test_the_record_stays_authoritative_and_the_column_is_the_projection(p7_conn, tmp_path, store):
    file_id = a_file(p7_conn, tmp_path)
    record = a_record(file_id=file_id)
    store.write(record)
    mirror(p7_conn, record, component_version=COMPONENT)
    # Provenance -- basis, evidence, reliability, supersede chain -- is answerable
    # from the record. The column answers only "what is this file right now".
    assert store.current(file_id, HASH_A).evidence_refs == PASSPORT_KEYS
    assert json.loads(get_file(p7_conn, file_id)["sensitivity_state"])["evidence_refs"] \
        == list(PASSPORT_KEYS)


# --- `Unreadable or unclassified` is a gate outcome, not a file fact (D2) ---

def test_an_unclassified_record_is_refused_by_the_store(store):
    # D2. Absence already says "nothing has looked"; a row saying it would be a
    # FACT claiming the same thing, and the two would then disagree.
    with pytest.raises(GateOutcomeNotAFileFact):
        store.write(a_record(handling_class=UNREADABLE_UNCLASSIFIED, protected=False,
                             basis="detector", evidence_refs=(KEY_A,)))


def test_unclassified_never_reaches_the_column(store):
    with pytest.raises(GateOutcomeNotAFileFact):
        mirror_state(a_record(handling_class=UNREADABLE_UNCLASSIFIED, protected=False))


def test_no_input_makes_the_column_read_public_low(p7_conn, tmp_path, store):
    # §8.6: "Cost exhaustion must never turn into lower-quality automatic
    # classification." The failure that sentence forbids is exactly defaulting an
    # unclassified file to public so the pipeline can continue.
    file_id = a_file(p7_conn, tmp_path)
    assert get_file(p7_conn, file_id)["sensitivity_state"] is None
    assert store.current(file_id, HASH_A) is None


# --- D2's shape: no protocol, no injection, no P6 surface -------------------

def test_the_store_is_concrete_and_takes_no_injection(p7_conn):
    import privacy.classification_store as module
    assert not hasattr(module, "SensitivityFacts")
    assert not hasattr(module, "SensitivityStateWriter")
    # One constructor argument: the connection. A second would be the injection D2
    # removed.
    import inspect
    assert list(inspect.signature(ClassificationStore).parameters) == ["conn"]


def test_the_p6_stand_in_is_deleted_and_not_reimplemented(p7_conn):
    # There is no longer a P6 surface for it to stand in for (D2).
    assert not (Path(__file__).parent / "p6_fixture.py").exists()


def test_the_store_needs_no_p6_table_to_exist(p7_conn, store):
    # NEEDS-JOSEPH C5: P7's SPEC still says "P6 must accept `sensitivity` as a
    # first-class universal field" while D2 makes P7's record authoritative and
    # round 1 found that P6 field has no producer. Task 4 is built so the answer
    # does not matter: there is no `file_facts` table in this database.
    tables = {row["name"] for row in p7_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "file_facts" not in tables
    store.write(a_record())
    assert store.current("file-1", HASH_A) is not None


def test_the_store_appends_no_event(p7_conn, store):
    # C4's one job. `classification_assigned` is Task 16's, once, with a user_id.
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    old = store.write(a_record())
    new = store.write(a_record(reliability_state=USER_CONFIRMED, basis=USER,
                               evidence_refs=(), observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before


def test_whether_protected_is_the_top_two_classes_is_not_answered_here(store):
    # SPEC Open question 1, unsettled and not settled by D2. `protected` is stored,
    # never derived: SPEC §2, "Neighbouring parts should consume the `protected`
    # flag, not infer it from the class."
    low_but_protected = a_record(handling_class="personal_non_sensitive",
                                 protected=True, basis="safety_domain")
    store.write(low_but_protected)
    assert store.current("file-1", HASH_A).protected is True
    import privacy.classification_store as module
    assert not [name for name in vars(module) if "co_extensive" in name]
