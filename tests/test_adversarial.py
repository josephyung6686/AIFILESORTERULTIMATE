"""Adversarial tests against P1 — the storage/identity/provenance substrate.

Every other part foreign-keys into `files` and `events`, and `events` is append-only,
so a wrong row written here is unrecoverable later. These tests attack the cases the
implementation plan did not enumerate.

Marker convention used throughout:

    FAILS         — a real defect, still live. The docstring names the contract
                    clause it violates and the downstream consequence.
    WAS-FAILING   — a real defect that was live when the test was written and was
                    fixed while this file was being built. Kept as a regression pin;
                    the original finding is preserved in the docstring.
    PINS          — passed from the start. Pinned so it cannot regress.
    CHARACTERISES — pins today's behaviour where the SPEC does not settle what the
                    behaviour should be. Not an assertion of a preferred reading.
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

import pytest

from database_agent.budget import all_ceilings, get_ceiling, set_ceiling
from database_agent.db import create_schema, transaction
from database_agent.events import MalformedEvent, append_event
from database_agent.files_table import (
    ReservedScanState, get_file, observe_path, record_file,
)
from database_agent.learning import learning_records, reset_preferences
from database_agent.scan_usage import (
    record_llm_cost, sample_scan_resources, scan_resource_usage, start_scan,
)
from database_agent.supersede import chain, mark_superseded
from database_agent.vectors import get_embedding, put_embedding
from database_agent.verify import (
    VerificationPoint, confirm_cross_volume_copy, verify_content,
)

# P3's arguments to observe_path. P1 invents none of them; every test that scans a
# path passes the same set so the tests differ only in what they are attacking.
SCAN = dict(
    author="P3", component_version="p3-1", parent_folder_context=None,
    mime_type=None, detected_format=None, scan_state="scanned", materialized=True,
)


def scan(path, **overrides):
    """SCAN plus the R2 fields P3 computes once (O5) and hands to P1.

    P1 stores them and derives none of them, so a caller standing in for P3 has
    to supply them — that is the contract, not a test inconvenience.
    """
    from p1_contract import p3_basic_record
    return {**SCAN, **p3_basic_record(Path(path)), **overrides}


@pytest.fixture()
def db(conn: sqlite3.Connection) -> sqlite3.Connection:
    create_schema(conn)
    return conn


def _event(conn, **overrides):
    """A minimally valid event. Overrides attack one field at a time."""
    fields = dict(
        event_type="hashing", subsystem="P3", component_version="p3-1",
        observed_at="2026-08-19T00:00:00+00:00", explanation="fixture",
    )
    fields.update(overrides)
    return append_event(conn, **fields)


# ═════════════════════════════════════════════════════════════════════════════
# 1. Identity (R1–R5) — resolving a path observation to a file version
# ═════════════════════════════════════════════════════════════════════════════

def test_deleting_one_of_two_live_copies_does_not_hijack_the_survivor(db, tmp_path):
    """PINS — R2 / SPEC OQ2. Exact path match wins before the dead-path move rule.
    """
    a, b = tmp_path / "A.pdf", tmp_path / "B.pdf"
    a.write_bytes(b"duplicate bytes")
    b.write_bytes(b"duplicate bytes")
    file_a = observe_path(db, a, **scan(a))
    file_b = observe_path(db, b, **scan(b))
    assert file_a != file_b, "two live copies are two rows (OQ2)"

    a.unlink()
    again = observe_path(db, b, **scan(b))

    assert again == file_b, "re-observing a live path must resolve to that path's own row"
    paths = [r["current_path"] for r in db.execute("SELECT current_path FROM files")]
    assert len(paths) == len(set(paths)), f"two rows claim one path: {paths}"


def test_three_live_copies_of_one_hash_are_three_rows(db, tmp_path):
    """PINS — SPEC OQ2. §2.9's duplicate family has nothing to detect if duplicates
    collapse, and §8.3's identical-file collision presumes both copies are separately
    addressable. The plan's tests cover two copies; three is where a loop that breaks
    on the first candidate would start collapsing them."""
    ids = []
    for name in ("one.txt", "two.txt", "three.txt"):
        p = tmp_path / name
        p.write_bytes(b"identical content")
        ids.append(observe_path(db, p, **scan(p)))
    assert len(set(ids)) == 3
    hashes = {get_file(db, i)["content_hash"] for i in ids}
    assert len(hashes) == 1, "one hash, three separately addressable versions"


def test_content_reverting_to_a_previous_version_does_not_resurrect_it(db, tmp_path):
    """PINS — R3 / OQ1. A file whose content goes X -> Y -> X must produce a THIRD
    row, not resurrect the superseded X row. Resurrection would re-attach P6's facts
    and P4's evidence from the first X to bytes that have since been rewritten twice,
    and would leave the Y row with no successor."""
    p = tmp_path / "doc.txt"
    p.write_bytes(b"version X")
    first = observe_path(db, p, **scan(p))
    p.write_bytes(b"version Y")
    second = observe_path(db, p, **scan(p))
    p.write_bytes(b"version X")
    third = observe_path(db, p, **scan(p))

    assert len({first, second, third}) == 3, "a reverted content hash is still a new version"
    assert get_file(db, first)["scan_state"] == "superseded_content"
    assert get_file(db, second)["scan_state"] == "superseded_content"
    assert get_file(db, third)["scan_state"] == "scanned"


def test_a_superseded_row_is_never_re_selected_by_a_later_observation(db, tmp_path):
    """PINS — OQ1. Once `scan_state = 'superseded_content'`, the row is history. Both
    of `observe_path`'s lookups must exclude it, or a later observation would write a
    new current_path onto a row whose whole purpose is to still describe the bytes
    P6's facts were extracted from."""
    p = tmp_path / "doc.txt"
    p.write_bytes(b"old bytes")
    old = observe_path(db, p, **scan(p))
    p.write_bytes(b"new bytes")
    observe_path(db, p, **scan(p))
    assert get_file(db, old)["scan_state"] == "superseded_content"

    elsewhere = tmp_path / "moved.txt"
    elsewhere.write_bytes(b"old bytes")
    revived = observe_path(db, elsewhere, **scan(elsewhere))

    assert revived != old, "a superseded version is never revived by a new observation"
    assert get_file(db, old)["current_path"] == str(p), "the superseded row keeps its path"


def test_caller_supplied_scan_state_can_forge_the_superseded_sentinel(db, tmp_path):
    """PINS — OQ1 sentinel is P1's write. A caller that supplies it is refused,
    so the row cannot be hidden from later lookups.
    """
    p = tmp_path / "doc.txt"
    p.write_bytes(b"bytes")
    forged = scan(p, scan_state="superseded_content")
    with pytest.raises(ReservedScanState):
        observe_path(db, p, **forged)


def test_observe_path_hashes_once_so_the_row_and_its_event_agree(db, tmp_path, monkeypatch):
    """PINS — R1. Identity hashes once; the row is keyed on that digest.
    """
    import database_agent.files_table as ft

    real = ft.hash_file
    calls = []

    def counting_hash(path, *, materialized):
        calls.append(path)
        digest = real(path, materialized=materialized)
        # Second read of the same path sees different bytes.
        return "f" * 64 if len(calls) > 1 else digest

    monkeypatch.setattr(ft, "hash_file", counting_hash)

    p = tmp_path / "syncing.txt"
    p.write_bytes(b"bytes at time of first read")
    file_id = observe_path(db, p, **scan(p))

    assert len(calls) == 1, f"observe_path read the file {len(calls)} times to record it once"
    row_hash = get_file(db, file_id)["content_hash"]
    event_hash = db.execute(
        "SELECT content_hash FROM events WHERE file_id = ? ORDER BY event_id DESC LIMIT 1",
        (file_id,),
    ).fetchone()["content_hash"]
    assert row_hash == event_hash, "the row and its own provenance disagree about the hash"


def test_an_empty_file_is_a_normal_file_version(db, tmp_path):
    """PINS — R1. Zero bytes still has a hash, so an empty file must record like any
    other. If it did not, every empty file in a corpus would share one degenerate
    identity or none at all."""
    p = tmp_path / "empty.txt"
    p.write_bytes(b"")
    file_id = observe_path(db, p, **scan(p))
    row = get_file(db, file_id)
    assert row["observed_size"] == 0
    assert len(row["content_hash"]) == 64


# ═════════════════════════════════════════════════════════════════════════════
# 2. Append-only (R6) — "INSERT only. No UPDATE, no DELETE, no row rewrite,
#    no truncation, no compaction that drops rows."
# ═════════════════════════════════════════════════════════════════════════════

def test_insert_or_replace_cannot_rewrite_an_event_row(db):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     R6, and Contract out §3 "Append-only means: INSERT only ... no row
    rewrite. A correction to an event is a new event, not an edit."

    The two triggers guard UPDATE and DELETE. SQLite's REPLACE conflict resolution
    deletes the conflicting row WITHOUT firing delete triggers unless
    `PRAGMA recursive_triggers` is ON, and it is OFF by default and never set here.
    So `INSERT OR REPLACE` rewrites any event row in place, in one statement, with
    no error: the row count is unchanged and the old subsystem, explanation and
    timestamp are gone.

    Downstream: the provenance log is the only record of who did what. P2's replay,
    §8.4's consent-aware audit and §8.7's negative-feedback evidence all read it and
    all silently read the forgery. The fix is `PRAGMA recursive_triggers = ON` at
    open (which makes REPLACE fire the delete trigger), or a BEFORE INSERT trigger
    that rejects an INSERT naming an existing event_id.
    """
    original = _event(db, explanation="the real event", subsystem="P3")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT OR REPLACE INTO events "
            "(event_id, event_type, subsystem, observed_at, explanation) "
            "VALUES (?, ?, ?, ?, ?)",
            (original, "hashing", "FORGED", "1970-01-01T00:00:00+00:00", "TAMPERED"),
        )
    row = db.execute("SELECT * FROM events WHERE event_id = ?", (original,)).fetchone()
    assert row["explanation"] == "the real event"
    assert row["subsystem"] == "P3"


def test_open_database_enforces_append_only_on_an_existing_file(db, tmp_path):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     R6. Enforcement is create-time only and is never verified at open.

    The triggers are created by `create_schema`, which a caller invokes once. Nothing
    in `open_database` checks that they survived. A database whose triggers were
    dropped — by an earlier tool, a migration, a repair, or `PRAGMA writable_schema` —
    reopens as a fully writable events table with no error and no signal, and the
    only guarantee the whole product rests on is silently absent.

    Downstream: every consumer of `events` (P2 replay, P12 undo, P13's audit view,
    §8.7 learning) trusts R6 structurally. A substrate that cannot say at open time
    whether R6 is in force cannot support that trust. `open_database` should assert
    the triggers exist whenever the `events` table does.
    """
    from database_agent.db import open_database

    path = tmp_path / "reopened.sqlite"
    first = open_database(path)
    create_schema(first)
    _event(first, explanation="written under enforcement")
    first.close()

    # A connection that did not go through open_database can strip the triggers.
    # Reopening through P1 must put them back.
    stripped = sqlite3.connect(path)
    stripped.execute("DROP TRIGGER events_no_update")
    stripped.execute("DROP TRIGGER events_no_delete")
    stripped.close()

    second = open_database(path)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            second.execute("UPDATE events SET subsystem = 'FORGED'")
        with pytest.raises(sqlite3.IntegrityError):
            second.execute("DELETE FROM events")
    finally:
        second.close()


def test_events_cannot_be_truncated_by_dropping_the_table(db):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     R6 "no truncation". DROP TABLE is truncation by another name, and
    nothing stops it: it removes both the rows and the triggers that were the only
    thing protecting them, then `create_schema` re-creates an empty table that looks
    exactly like a corpus nobody ever scanned.

    Downstream: undetectable. There is no other copy of `events` — §0 says the
    database is rebuildable from the filesystem, but 11-ops-runtime.md §2 is explicit
    that a rebuild does NOT reconstruct `events`. This is the one P1 table whose loss
    is permanent, and the loss leaves no trace.
    """
    _event(db, explanation="a row that must survive")
    with pytest.raises(sqlite3.DatabaseError):
        db.execute("DROP TABLE events")
    assert db.execute("SELECT COUNT(*) c FROM events").fetchone()["c"] == 1


def test_upsert_on_conflict_do_update_is_blocked(db):
    """PINS — R6. Unlike REPLACE, an explicit `ON CONFLICT DO UPDATE` does fire the
    UPDATE trigger. Pinned because the natural fix for the REPLACE hole is to add a
    BEFORE INSERT guard, and that must not be done in a way that stops firing here."""
    original = _event(db, explanation="original")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO events (event_id, event_type, subsystem, observed_at) "
            "VALUES (?, ?, ?, ?) ON CONFLICT(event_id) DO UPDATE SET explanation = 'x'",
            (original, "hashing", "P3", "t"),
        )
    assert db.execute(
        "SELECT explanation FROM events WHERE event_id = ?", (original,)
    ).fetchone()["explanation"] == "original"


def test_unqualified_delete_does_not_take_the_truncate_optimization(db):
    """PINS — R6. `DELETE FROM t` with no WHERE normally uses SQLite's truncate
    optimization, which drops the whole table without visiting rows and so without
    firing per-row triggers. The presence of a BEFORE DELETE trigger disables that
    optimization. Pinned because it is invisible in the source and a future schema
    change that moves enforcement off a row trigger would silently reopen it."""
    _event(db)
    _event(db)
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("DELETE FROM events")
    assert db.execute("SELECT COUNT(*) c FROM events").fetchone()["c"] == 2


def test_a_second_connection_to_the_same_file_is_equally_bound(db, tmp_path):
    """PINS — R6. The triggers live in the schema, not the connection, so a plain
    `sqlite3.connect` that never went through `open_database` is bound too. This is
    what makes §0's "easy inspection" safe: a user with the sqlite3 CLI open on the
    file cannot quietly edit history."""
    from database_agent.db import open_database

    path = tmp_path / "shared.sqlite"
    owner = open_database(path)
    create_schema(owner)
    _event(owner, explanation="written by the owner")
    other = sqlite3.connect(path)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            other.execute("UPDATE events SET explanation = 'x'")
        with pytest.raises(sqlite3.IntegrityError):
            other.execute("DELETE FROM events")
    finally:
        other.close()
        owner.close()


def test_vacuum_compacts_without_dropping_rows(db):
    """PINS — R6 "no compaction that drops rows". VACUUM rebuilds the file; it must
    move rows, never lose them."""
    ids = [_event(db, explanation=f"e{i}") for i in range(5)]
    db.execute("VACUUM")
    assert [r["event_id"] for r in db.execute("SELECT event_id FROM events ORDER BY event_id")] == ids


# ═════════════════════════════════════════════════════════════════════════════
# 3. Authorship (M8) — "the acting part authors; P1 writes."
# ═════════════════════════════════════════════════════════════════════════════

def test_p1_authors_nothing_but_its_own_verifications(db, tmp_path):
    """PINS — M8, and Cross-cutting answers → Provenance: "P1 appends no event on
    its own initiative." The only events P1 may sign are the V1–V4 comparisons it
    performs. Every other write path must carry the caller's author through to
    `subsystem`. This is checked behaviourally rather than by grep, because a
    future refactor could reintroduce a default author without adding the literal.
    """
    p = tmp_path / "doc.txt"
    p.write_bytes(b"bytes")
    file_id = observe_path(db, p, **scan(p))
    reset_preferences(db, "file", file_id, author="P13", component_version="p13-1",
                      user_id="u1")

    authors = {r["subsystem"] for r in db.execute("SELECT subsystem FROM events")}
    assert authors == {"P3", "P13"}, f"P1 signed an event it did not perform: {authors}"

    verify_content(db, file_id, "0" * 64, point=VerificationPoint.V1, author="P12",
                   component_version="p12-1", materialized=True)
    p1_rows = db.execute("SELECT * FROM events WHERE subsystem = 'P1'").fetchall()
    assert len(p1_rows) == 1 and p1_rows[0]["event_type"] == "hashing"
    assert '"requested_by": "P12"' in p1_rows[0]["explanation"], (
        "the performer is P1; the requester must stay recoverable from the event"
    )


def test_the_writer_rejects_an_event_with_no_author_version_or_explanation(db):
    """PINS — Done-means 7: subsystem, component_version and explanation are required.
    """
    with pytest.raises(MalformedEvent):
        append_event(db, event_type="hashing", subsystem="", observed_at="t",
                     component_version="v", explanation="e")
    with pytest.raises(MalformedEvent):
        append_event(db, event_type="hashing", subsystem="P3", observed_at="t")


def test_the_writer_silently_discards_any_field_it_does_not_recognise(db):
    """PINS — unknown kwargs are refused. A misspelled column cannot become a
    successful append of a row that is missing the value.
    """
    with pytest.raises(MalformedEvent, match="unrecognised"):
        append_event(
            db, event_type="review action routed", subsystem="P13", component_version="v",
            observed_at="t", explanation="e", user_id="u1",
            correction_scope="file", correction_subjct="MISSPELLED",
        )


def test_an_unregistered_event_type_is_still_rejected_when_other_fields_are_valid(db):
    """PINS — Contract out §3, rule 3: "An unregistered type is rejected at the
    writer, never silently stored." Registration is spec-level (rule 4), so there
    must be no run-time path that mints one — including a name that differs from a
    reserved one only in case or spacing."""
    from database_agent.events import UnregisteredEventType

    for forged in ("Discovery", "stat  observation", "hashing ", "placement recommendation!"):
        with pytest.raises(UnregisteredEventType):
            _event(db, event_type=forged)


# ═════════════════════════════════════════════════════════════════════════════
# 4. The §8.7 learning-record store — "Scope is the filter, and it is exact."
# ═════════════════════════════════════════════════════════════════════════════

def _correction(conn, **overrides):
    fields = dict(
        event_type="review action routed", subsystem="P9", component_version="p9-1",
        observed_at="t", explanation="rejected this grouping", user_id="u1",
        polarity="reject", proposal_class="group", basis_key="bk-1",
    )
    fields.update(overrides)
    return append_event(conn, **fields)


def test_one_subject_at_two_scopes_never_leaks_across(db):
    """PINS — Contract out §7. §8.7's worked case is the reason the column exists:
    one transcript belonging in a Columbia packet "should not teach the engine that
    all transcripts belong there." The subject id is the same string at both scopes,
    which is the case where a `LIKE`, an `IN`, or a forgotten scope predicate would
    show up."""
    _correction(db, correction_scope="file", correction_subject="S", explanation="this file")
    _correction(db, correction_scope="corpus", correction_subject="S", explanation="all files")

    assert [r["explanation"] for r in learning_records(db, "file", "S")] == ["this file"]
    assert [r["explanation"] for r in learning_records(db, "corpus", "S")] == ["all files"]
    for other in ("group", "node", "template", "domain"):
        assert learning_records(db, other, "S") == []


def test_records_come_back_newest_first_with_their_opaque_fields(db):
    """PINS — Contract out §7: "newest first, each with its §8.2 explanation,
    polarity, proposal_class, basis_key, and evidence reference". Order is contract
    because every query-before-propose reader in 10-i4-learning-ops.md takes the most
    recent correction as the governing one."""
    _correction(db, correction_scope="group", correction_subject="G", explanation="first")
    _correction(db, correction_scope="group", correction_subject="G", explanation="second")
    rows = learning_records(db, "group", "G")
    assert [r["explanation"] for r in rows] == ["second", "first"]
    assert rows[0]["polarity"] == "reject"
    assert rows[0]["proposal_class"] == "group"
    assert rows[0]["basis_key"] == "bk-1"


def test_a_correction_with_no_subject_is_not_written_unreadable(db):
    """PINS — a scoped correction without a subject is refused at the writer.
    """
    with pytest.raises(MalformedEvent, match="correction_subject"):
        _correction(db, correction_scope="file", correction_subject=None)


def test_an_unknown_correction_scope_is_rejected_at_the_writer(db):
    """PINS — stored spelling is `node`, not the prose `destination node`.
    """
    with pytest.raises(MalformedEvent):
        _correction(db, correction_scope="destination node", correction_subject="N")
    with pytest.raises(MalformedEvent):
        _correction(db, correction_scope="FILE", correction_subject="N")


def test_a_reset_at_one_scope_does_not_reset_another(db):
    """PINS — Contract out §7 and R6. Reset is scoped; a corpus-wide reset must not
    silently erase the file-level corrections the user made deliberately, and it must
    delete nothing."""
    _correction(db, correction_scope="file", correction_subject="S", explanation="keep me")
    _correction(db, correction_scope="corpus", correction_subject="S", explanation="clear me")
    before = db.execute("SELECT COUNT(*) c FROM events").fetchone()["c"]

    reset_preferences(db, "corpus", "S", author="P13", component_version="p13-1", user_id="u1")

    assert [r["explanation"] for r in learning_records(db, "file", "S")] == ["keep me"]
    assert learning_records(db, "corpus", "S") == []
    after = db.execute("SELECT COUNT(*) c FROM events").fetchone()["c"]
    assert after == before + 1, "reset appends and deletes nothing (R6)"
    assert db.execute(
        "SELECT COUNT(*) c FROM events WHERE correction_subject = 'S'"
    ).fetchone()["c"] == 3, "the pre-reset records stay readable in the log"


def test_resets_interleaved_with_corrections_honour_only_the_newest_cutoff(db):
    """PINS — Contract out §7. Reset is a cutoff, not a delete, so the sequence
    correct / reset / correct / reset must leave nothing visible, and
    correct / reset / correct must leave exactly the last one. This is the arithmetic
    that decides what P9 and P11 are allowed to remember, and an off-by-one in the
    `> cutoff` comparison would either resurrect reset preferences or swallow the
    correction a user made immediately after resetting."""
    kw = dict(correction_scope="domain", correction_subject="D")
    _correction(db, explanation="before first reset", **kw)
    reset_preferences(db, "domain", "D", author="P13", component_version="v", user_id="u1")
    _correction(db, explanation="between resets", **kw)
    assert [r["explanation"] for r in learning_records(db, "domain", "D")] == ["between resets"]

    reset_preferences(db, "domain", "D", author="P13", component_version="v", user_id="u1")
    assert learning_records(db, "domain", "D") == []
    _correction(db, explanation="after second reset", **kw)
    assert [r["explanation"] for r in learning_records(db, "domain", "D")] == ["after second reset"]


def test_the_reset_event_is_not_returned_as_a_correction(db):
    """PINS — Contract out §7. `reset_preferences` appends a `review action routed`
    event carrying the same scope, subject and a user_id, which is exactly the shape
    `learning_records` selects on. It must not come back as a correction, or every
    reset would teach the engine one more thing."""
    _correction(db, correction_scope="template", correction_subject="T")
    reset_preferences(db, "template", "T", author="P13", component_version="v", user_id="u1")
    assert learning_records(db, "template", "T") == []


# ═════════════════════════════════════════════════════════════════════════════
# 5. Fixity (V1–V4) — "budget pressure must never weaken a fixity check"
# ═════════════════════════════════════════════════════════════════════════════

def test_verification_of_a_vanished_file_reports_mismatch_not_an_exception(db, tmp_path):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     Cross-cutting answers → Budgets: "An absent hash must never read as a
    hash match anywhere in the system; V1–V4 return *mismatch* on an unknown hash,
    never *match*."

    `verify_content` reads `current_path` off the row and hashes it unconditionally.
    When the file is gone it raises FileNotFoundError out of P1, and — worse — it
    raises BEFORE `append_event`, so the attempted verification leaves no row in the
    log at all.

    V1's entire purpose is to notice that the file a plan was built against is no
    longer what it was. The commonest form of that is the file being gone, and it is
    precisely the form that crashes. §8.3's staleness rule ("if its content hash
    differs ... the action should be marked stale") is evaluated against V1/V2, so
    P12 gets an unhandled exception where it needed the word "mismatch", and
    11-ops-runtime's crash-mid-apply recovery has no event to recover from.
    """
    p = tmp_path / "doc.txt"
    p.write_bytes(b"content")
    file_id = observe_path(db, p, **scan(p))
    expected = get_file(db, file_id)["content_hash"]
    before = db.execute("SELECT COUNT(*) c FROM events").fetchone()["c"]
    p.unlink()

    result = verify_content(db, file_id, expected, point=VerificationPoint.V1,
                            author="P12", component_version="p12-1", materialized=True)

    assert result == "mismatch"
    assert db.execute("SELECT COUNT(*) c FROM events").fetchone()["c"] == before + 1, (
        "P1 performs and records; a verification that could not complete is still a "
        "verification that happened"
    )


def test_verification_of_a_path_replaced_by_a_directory_reports_mismatch(db, tmp_path):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     same clause. §8.3 names cloud sync agents "renaming and replacing
    files"; a path that is now a directory is the same class of external change V1
    exists to catch. `hash_file` raises IsADirectoryError instead."""
    p = tmp_path / "doc.txt"
    p.write_bytes(b"content")
    file_id = observe_path(db, p, **scan(p))
    expected = get_file(db, file_id)["content_hash"]
    p.unlink()
    p.mkdir()

    assert verify_content(db, file_id, expected, point=VerificationPoint.V2,
                          author="P12", component_version="p12-1",
                          materialized=True) == "mismatch"


def test_verification_of_an_unknown_file_id_does_not_fail_as_a_type_error(db):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     Contract out §5, `verify_content(file_id, expected_hash) -> match |
    mismatch`. `get_file` returns None for an unknown id and the next line subscripts
    it, so the caller gets `TypeError: 'NoneType' object is not subscriptable` from
    inside the substrate. P12 cannot distinguish that from a bug in its own code, and
    the published signature promises two possible answers, neither of which is a
    crash."""
    with pytest.raises(KeyError):
        verify_content(db, "no-such-file-id", "0" * 64, point=VerificationPoint.V1,
                       author="P12", component_version="p12-1", materialized=True)


def test_v4_refuses_a_destination_that_is_a_directory(db, tmp_path):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     V4: "the destination copy is hashed and confirmed before the source
    may be removed". `confirm_cross_volume_copy` gates on `destination.exists()`,
    which is true for a directory, then hashes it and raises IsADirectoryError.

    V4 is the last check standing between a cross-volume copy and `rm` on the source.
    It must answer False for every destination it cannot confirm, and it must record
    the refusal — this is the one verification whose failure mode is data loss.
    """
    source = tmp_path / "src.bin"
    source.write_bytes(b"payload")
    destination = tmp_path / "dst"
    destination.mkdir()
    before = db.execute("SELECT COUNT(*) c FROM events").fetchone()["c"]

    confirmed = confirm_cross_volume_copy(
        db, source=source, destination=destination, expected_hash="0" * 64,
        author="P12", component_version="p12-1", materialized=True)

    assert confirmed is False
    assert db.execute("SELECT COUNT(*) c FROM events").fetchone()["c"] == before + 1


def test_v4_refuses_a_destination_that_exists_but_is_empty(db, tmp_path):
    """PINS — V4. A truncated destination is the classic half-finished copy: it
    exists, so a naive existence check passes, and it holds none of the bytes. V4
    must refuse and record the refusal before the source may be removed."""
    source = tmp_path / "src.bin"
    source.write_bytes(b"payload that matters")
    destination = tmp_path / "dst.bin"
    destination.write_bytes(b"")
    expected = get_file(db, observe_path(db, source, **scan(source)))["content_hash"]

    assert confirm_cross_volume_copy(
        db, source=source, destination=destination, expected_hash=expected,
        author="P12", component_version="p12-1", materialized=True) is False
    refusal = db.execute(
        "SELECT explanation FROM events WHERE subsystem = 'P1' ORDER BY event_id DESC LIMIT 1"
    ).fetchone()["explanation"]
    assert '"result": "refused"' in refusal


def test_v4_refuses_a_destination_that_does_not_exist_yet(db, tmp_path):
    """PINS — V4. The copy never landed. Refuse, and leave a row saying so."""
    source = tmp_path / "src.bin"
    source.write_bytes(b"payload")
    assert confirm_cross_volume_copy(
        db, source=source, destination=tmp_path / "never-written.bin",
        expected_hash="0" * 64, author="P12", component_version="p12-1",
        materialized=True) is False


def test_a_verification_records_the_hash_it_actually_read(db, tmp_path):
    """PINS — Contract out §5 and §8.2. The event must carry the hash P1 observed,
    not the hash the caller expected, or a mismatch would be indistinguishable from a
    match in the log and §8.3's undo precondition could not be reconstructed."""
    p = tmp_path / "doc.txt"
    p.write_bytes(b"real content")
    file_id = observe_path(db, p, **scan(p))
    actual = get_file(db, file_id)["content_hash"]

    assert verify_content(db, file_id, "0" * 64, point=VerificationPoint.V3,
                          author="P12", component_version="p12-1",
                          materialized=True) == "mismatch"
    row = db.execute(
        "SELECT * FROM events WHERE subsystem = 'P1' ORDER BY event_id DESC LIMIT 1"
    ).fetchone()
    assert row["content_hash"] == actual, "the log records what was read, not what was hoped for"


# ═════════════════════════════════════════════════════════════════════════════
# 6. Budget, vectors, scan usage
# ═════════════════════════════════════════════════════════════════════════════

def test_a_ceiling_value_that_is_not_a_number_is_rejected(db):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     Contract out §8 and Contract in ("P1 validates the *shape* of what it
    is given"). `budget_ceilings.value` has INTEGER affinity, and SQLite affinity
    stores a non-numeric string unchanged. `set_ceiling` type-checks nothing, so
    `get_ceiling` hands back a `str`.

    Downstream: every enforcing part compares a count against the ceiling it reads.
    `pages > "no limit"` raises TypeError deep inside P5's OCR loop or P8's call
    budget, at the moment the ceiling was supposed to protect the scan. §8.6's
    closing constraint — "cost exhaustion must never turn into lower-quality
    automatic classification" — cannot hold if reading the ceiling is itself the
    failure. P1 holds these values precisely so that no consumer has to re-validate.
    """
    with pytest.raises((TypeError, ValueError)):
        set_ceiling(db, "ocr.max_pages_per_file", "no limit")
    assert not isinstance(get_ceiling(db, "ocr.max_pages_per_file"), str)


def test_all_ceilings_never_returns_a_key_outside_the_closed_set(db):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     Contract out §8: the key set is closed at fifteen. `set_ceiling` and
    `get_ceiling` both call `_check`, but `all_ceilings` does a bare `SELECT key,
    value` and the table carries no CHECK constraint, so any row that reached the
    table by another route is published as a ceiling.

    Downstream: a consumer iterating `all_ceilings` to build its enforcement map picks
    up a key no part owns and no part enforces, which reads as a configured limit
    that silently does nothing. Either the DDL should constrain `key` or the reader
    should filter to `CEILING_KEYS`.
    """
    db.execute("INSERT INTO budget_ceilings (key, value) VALUES ('ocr.unlimited', 1)")
    assert "ocr.unlimited" not in all_ceilings(db)


def test_grouping_and_placement_ceilings_stay_independent(db):
    """PINS — O10. The three namespaced pairs exist because P9's grouping
    neighbourhood (§4.2) and P11's node-local graph (§6.4) are not the same graph.
    A shared row, or a prefix-stripping read, would make one number wrong in one of
    the two places."""
    for pair in ("max_retrieved_neighbors", "max_local_graph_neighborhood",
                 "max_candidate_cluster_size"):
        set_ceiling(db, f"grouping.{pair}", 10)
        set_ceiling(db, f"placement.{pair}", 99)
        assert get_ceiling(db, f"grouping.{pair}") == 10
        assert get_ceiling(db, f"placement.{pair}") == 99


def test_an_embedding_that_is_not_bytes_is_rejected_rather_than_corrupted(db):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     Contract out §9: `get_embedding(subject_key)` "return it unchanged".

    `put_embedding` passes its argument straight to a BLOB column, which has no
    affinity conversion, and `get_embedding` wraps whatever comes back in `bytes()`.
    Hand it the integer 5 and it stores 5 and returns `b'\\x00\\x00\\x00\\x00\\x00'`
    — five zero bytes — with no error at either end. Hand it a `str` and the read
    raises TypeError long after the write that caused it.

    Downstream: P9 computes the arrays and P11 retrieves over them (§4.2, §6.3).
    Silent substitution of a zero vector is the worst possible corruption for a
    similarity search: it does not fail, it just quietly makes a file equidistant
    from everything. This is the one store whose entire contract is byte fidelity.
    """
    with pytest.raises((TypeError, ValueError)):
        put_embedding(db, "k", 5, producer_version="p9-1")
    with pytest.raises((TypeError, ValueError)):
        put_embedding(db, "k2", "not bytes", producer_version="p9-1")


def test_arrays_round_trip_through_null_bytes_and_large_payloads(db):
    """PINS — Contract out §9, "store an opaque compact local array ... return it
    unchanged". Embeddings are packed floats, so NUL bytes are not an edge case, they
    are most of the payload; a TEXT column or any str round-trip would truncate at
    the first one."""
    tricky = b"\x00\x01\x00\xff\x00\x00" + bytes(range(256)) + b"\x00"
    put_embedding(db, "nul", tricky, producer_version="p9-1")
    assert get_embedding(db, "nul") == tricky

    large = bytes(range(256)) * 40_000  # ~10 MB
    put_embedding(db, "large", large, producer_version="p9-1")
    assert get_embedding(db, "large") == large

    put_embedding(db, "empty", b"", producer_version="p9-1")
    assert get_embedding(db, "empty") == b""


def test_no_vector_reaches_files_or_events(db, tmp_path):
    """PINS — §0 and Done-means 9: vectors are "stored separately as compact local
    arrays", never a vector database, and `files` and `events` hold no vectors."""
    p = tmp_path / "doc.txt"
    p.write_bytes(b"bytes")
    file_id = observe_path(db, p, **scan(p))
    put_embedding(db, file_id, b"\x00\x01", producer_version="p9-1")

    for table in ("files", "events"):
        columns = {r["name"] for r in db.execute(f"PRAGMA table_info({table})")}
        assert not any("vector" in c or "embedding" in c or "array" in c for c in columns)


def test_llm_cost_for_an_unknown_scan_is_not_silently_dropped(db):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     Contract out §10: `llm_cost` is "supplied by P8, the single egress
    point (O9)" and P8 is the only part that can know it. `record_llm_cost` issues a
    bare UPDATE, so a wrong or stale `scan_id` matches no row, changes nothing, and
    returns None exactly as a success does.

    Downstream: the one number in the whole product that measures money spent
    disappears with no error, and the scan renders in P13 with `llm_cost` NULL — which
    §10 defines as "could not be sampled". An unmeasured scan and a scan whose
    measurement was misrouted become indistinguishable, which is the precise failure
    §8.6's "absence reads as unknown" rule exists to prevent.
    """
    with pytest.raises(KeyError):
        record_llm_cost(db, "no-such-scan", {"usd": 9.99}, author="P8")


def test_unsampleable_counters_read_as_null_never_as_zero(db):
    """PINS — Contract out §10: "Absence reads as unknown, never as zero. A counter
    that could not be sampled is recorded as unavailable. §8.6's whole purpose is that
    deferred and unmeasured work stay visible as such rather than reading as work that
    completed cheaply." """
    import json

    scan_id = start_scan(db, scan_run_id="p3-scan-fixture")
    sample_scan_resources(db, scan_id)
    row = scan_resource_usage(db, scan_id)

    assert row["network"] is None, "there is no portable byte counter; that is unknown, not 0"
    assert row["llm_cost"] is None, "P8 has not written yet; that is unknown, not 0"
    assert json.loads(row["memory"])["current_bytes"] is None
    assert json.loads(row["cpu_accelerator"])["accelerator_seconds"] is None
    assert json.loads(row["storage"])["log_bytes"] is None


def test_storage_reads_as_unknown_when_the_database_has_no_file(db):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     Contract out §10, same clause. `_database_bytes` returns the literal
    `0` when `PRAGMA database_list` yields no file — the in-memory case, and the case
    of any connection whose main database is not on disk. Zero bytes of storage is a
    measurable, plausible-looking value, and §10 says an unsampleable counter must
    read as unavailable instead."""
    import json

    memory_db = sqlite3.connect(":memory:")
    memory_db.row_factory = sqlite3.Row
    try:
        create_schema(memory_db)
        scan_id = start_scan(memory_db, scan_run_id="p3-scan-fixture")
        sample_scan_resources(memory_db, scan_id)
        storage = json.loads(scan_resource_usage(memory_db, scan_id)["storage"])
        assert storage["database_bytes"] is None, (
            f"unsampleable storage recorded as {storage['database_bytes']!r}, "
            "which reads as a scan that used no storage"
        )
    finally:
        memory_db.close()


def test_recording_resources_imposes_no_ceiling(db, tmp_path):
    """PINS — Contract out §10 negative test: "P1 rejects no operation and defers no
    work for any value of any of the six — there is no threshold to hit." Holding
    §8.6's twelve ceilings must not leak into the six observability counters."""
    scan_id = start_scan(db, scan_run_id="p3-scan-fixture")
    for key in ("model.max_cost_per_scan", "ocr.max_time_per_scan"):
        set_ceiling(db, key, 0)
    record_llm_cost(db, scan_id, {"usd": 1_000_000}, author="P8")
    sample_scan_resources(db, scan_id)

    p = tmp_path / "doc.txt"
    p.write_bytes(b"bytes")
    assert observe_path(db, p, **scan(p)), "a zero ceiling must not stop the substrate working"


def test_scan_id_is_not_a_column_on_events(db):
    """PINS — Contract out §10 and MINOR 1: "It is **not** added to `events` — §8.2's
    event record keeps its eleven fields ... and Done-means 7 still tests exactly
    eleven." """
    columns = {r["name"] for r in db.execute("PRAGMA table_info(events)")}
    assert "scan_id" not in columns


# ═════════════════════════════════════════════════════════════════════════════
# 7. Transactions and supersede-never-overwrite
# ═════════════════════════════════════════════════════════════════════════════

def _facts_table(conn):
    """A minimal table adopting P1's shared supersede columns, as P4/P6/P9/P11 do."""
    from database_agent.supersede import supersede_ddl

    conn.execute(f"CREATE TABLE facts (record_id TEXT PRIMARY KEY, value TEXT, "
                 f"{supersede_ddl('facts')})")
    for name in ("first_ocr", "second_ocr", "third_ocr"):
        conn.execute("INSERT INTO facts (record_id, value) VALUES (?, ?)", (name, name))


def test_superseding_a_row_twice_does_not_destroy_the_first_reason(db):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     Contract out §4 and §8.2: a superseding result must retain "the old
    observation" AND "the reason it was superseded". `mark_superseded` issues a bare
    `UPDATE ... SET superseded_by = ?, supersede_reason = ?`, so a second supersede
    of the same row overwrites both. The first reason is gone, and `chain()` now
    walks straight past the intermediate record as if it had never existed.

    This is an overwrite inside the module whose entire name is
    supersede-never-overwrite. §8.2's worked case is normative: a first OCR pass that
    produced unreadable text and a later engine that recovered a university name must
    BOTH remain available. After a third pass, the second is unreachable.

    Downstream: P6 (§3.12), P4 (§2.8), P9 (§4) and P11 (§6.11) all adopt these
    columns and all read the chain to show a user why a placement was concluded. The
    substrate has to either refuse the second link or model the fork; it must not
    silently drop the middle of the chain.
    """
    _facts_table(db)
    mark_superseded(db, "facts", old_id="first_ocr", new_id="second_ocr",
                    reason="OCR produced unreadable text")
    with pytest.raises(ValueError, match="already superseded"):
        mark_superseded(db, "facts", old_id="first_ocr", new_id="third_ocr",
                        reason="re-run on a better engine")

    row = db.execute("SELECT * FROM facts WHERE record_id = 'first_ocr'").fetchone()
    assert row["supersede_reason"] == "OCR produced unreadable text"
    assert "second_ocr" in {r["record_id"] for r in chain(db, "facts", "first_ocr")}


def test_a_supersede_chain_cannot_be_made_to_loop_forever(db):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     Contract out §4. `mark_superseded` accepts any pair of ids, and
    `chain()` walks `superseded_by` with no visited-set and no depth bound. A
    resolver that reverts — supersede A with B, later supersede B back with A, which
    §8.2 explicitly permits since "the newest record is not automatically preferred"
    — produces a two-cycle, and `chain()` then never returns.

    Downstream: `chain` is a published read surface. P13 calls it to render why a
    placement was concluded, so the failure mode is the review UI hanging on a file
    the user is trying to inspect, with the process accumulating rows until it is
    killed. Either `mark_superseded` must reject a link that closes a cycle, or
    `chain` must carry a visited set.
    """
    _facts_table(db)
    mark_superseded(db, "facts", old_id="first_ocr", new_id="second_ocr", reason="r1")
    try:
        mark_superseded(db, "facts", old_id="second_ocr", new_id="first_ocr",
                        reason="reverted to the original reading")
    except (ValueError, sqlite3.DatabaseError):
        return  # guarded at write time, which is an equally good answer

    steps = 0

    def budget():
        nonlocal steps
        steps += 1
        return 1 if steps > 2000 else 0

    db.set_progress_handler(budget, 200)
    try:
        walked = chain(db, "facts", "first_ocr")
    except sqlite3.OperationalError:  # the step budget aborted a runaway walk
        pytest.fail("chain() does not terminate on a supersede cycle")
    finally:
        db.set_progress_handler(None, 0)
    assert len(walked) <= 3


def test_supersede_reason_is_required_and_the_old_row_stays_readable(db):
    """PINS — Contract out §4 and Done-means 5. The old row is never deleted and
    never mutated in its own columns; only the link is added. The reason is
    mandatory, because §8.2 requires it recorded."""
    _facts_table(db)
    with pytest.raises(ValueError):
        mark_superseded(db, "facts", old_id="first_ocr", new_id="second_ocr", reason="")

    mark_superseded(db, "facts", old_id="first_ocr", new_id="second_ocr", reason="why")
    old = db.execute("SELECT * FROM facts WHERE record_id = 'first_ocr'").fetchone()
    assert old["value"] == "first_ocr", "the superseded row's own value is untouched"
    assert old["superseded_by"] == "second_ocr"
    assert [r["record_id"] for r in chain(db, "facts", "first_ocr")] == \
        ["first_ocr", "second_ocr"]


def test_p1_publishes_no_preferred_column(db):
    """PINS — M1: "`preferred` sits on the resolver's record, not on the observation".
    P1 publishes three shared columns; the fourth belongs to P6's `file_facts` alone.
    A `preferred` appearing in P1's shared set would put the resolver's decision on
    the observation layer, which §3.2 places it after."""
    from database_agent.supersede import SUPERSEDE_COLUMNS, supersede_ddl

    assert "preferred" not in SUPERSEDE_COLUMNS
    assert "preferred" not in supersede_ddl("anything")
    for table in ("files", "events"):
        columns = {r["name"] for r in db.execute(f"PRAGMA table_info({table})")}
        assert "preferred" not in columns
    assert "supersession_reason" not in supersede_ddl("anything"), "M1: not an alias"


def test_rollback_leaves_files_and_events_consistent_with_each_other(db, tmp_path):
    """PINS — Contract out §6, "transactional, durably committed". `observe_path`
    writes a `files` row and an `events` row for one act. A rollback must take both
    or neither: a `files` row with no provenance is a file nothing can explain, and an
    event naming a file_id that does not exist breaks every consumer's foreign key."""
    p = tmp_path / "doc.txt"
    p.write_bytes(b"bytes")

    with pytest.raises(RuntimeError):
        with transaction(db):
            observe_path(db, p, **scan(p))
            raise RuntimeError("the caller failed after writing")

    assert db.execute("SELECT COUNT(*) c FROM files").fetchone()["c"] == 0
    assert db.execute("SELECT COUNT(*) c FROM events").fetchone()["c"] == 0

    with transaction(db):
        file_id = observe_path(db, p, **scan(p))
    orphans = db.execute(
        "SELECT COUNT(*) c FROM events WHERE file_id IS NOT NULL AND file_id NOT IN "
        "(SELECT file_id FROM files)"
    ).fetchone()["c"]
    assert orphans == 0
    assert get_file(db, file_id) is not None


def test_committed_event_ids_are_strictly_increasing_across_a_rollback(db):
    """PINS — Contract out §3, `event_id` is the "monotonic ordering key". Every
    consumer that reads history in order (P2's replay, `learning_records`' cutoff
    arithmetic, `file_path_history`) depends on committed ids ordering the same way
    the appends happened, including when an aborted transaction sits between them.

    Note: a rolled-back id IS handed out again, because AUTOINCREMENT's sequence
    counter is itself transactional. That is deliberately not asserted either way —
    §3 marks `event_id` "(mechanics)" and monotonicity across *committed* rows is
    what the contract names. Recorded as an ambiguity, not claimed as a defect.
    """
    first = _event(db, explanation="committed")
    with pytest.raises(RuntimeError):
        with transaction(db):
            _event(db, explanation="rolled back")
            raise RuntimeError("abort")
    second = _event(db, explanation="after the rollback")
    third = _event(db, explanation="later still")

    assert first < second < third
    assert [r["explanation"] for r in db.execute(
        "SELECT explanation FROM events ORDER BY event_id")] == [
        "committed", "after the rollback", "later still"]


def test_a_nested_transaction_does_not_discard_the_outer_one(db):
    """WAS-FAILING — this defect was live when the test was written and has
    since been fixed. Retained as a regression pin. Original finding:

     Contract out §6: P1 "publishes the handle and the transaction
    boundary" for every part, and §0 requires that "no part may hold a long
    transaction". Parts therefore compose: P12's apply calls into P3's re-scan, and
    both reach for P1's published boundary.

    `transaction()` issues a bare `BEGIN`. The inner call raises OperationalError
    from `__enter__`, which propagates through the outer `with`, whose `except`
    rolls the OUTER transaction back. Everything the outer scope had written is
    discarded, and the only diagnostic is "cannot start a transaction within a
    transaction" — a SQLite message that names neither part.

    Downstream: silent loss of committed-looking work, surfacing as a P1 error at a
    call site that did nothing wrong. A SAVEPOINT-based reentrant boundary, or an
    explicit refusal that leaves the outer transaction intact, are both defensible;
    rolling the caller's work back and blaming SQLite is not.
    """
    outer_event = None
    try:
        with transaction(db):
            outer_event = _event(db, explanation="written by the outer scope")
            with transaction(db):
                _event(db, explanation="written by the inner scope")
    except sqlite3.OperationalError:
        pass  # "cannot start a transaction within a transaction"

    survived = db.execute(
        "SELECT COUNT(*) c FROM events WHERE event_id = ?", (outer_event,)
    ).fetchone()["c"]
    assert survived == 1, (
        "the outer scope's committed-looking work was silently rolled back by a "
        "nested use of P1's own published transaction boundary"
    )


def test_an_append_blocked_by_the_trigger_does_not_abort_the_whole_transaction(db):
    """PINS — R6 and Contract out §6. `RAISE(ABORT)` unwinds the statement, not the
    transaction. A part that tries an illegal UPDATE, catches the IntegrityError and
    carries on must still have its earlier appends when it commits — otherwise
    enforcing append-only would itself become a way to lose committed work."""
    with transaction(db):
        kept = _event(db, explanation="appended before the illegal write")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("UPDATE events SET explanation = 'x' WHERE event_id = ?", (kept,))
        after = _event(db, explanation="appended after the illegal write")

    rows = {r["event_id"] for r in db.execute("SELECT event_id FROM events")}
    assert rows == {kept, after}
    assert db.execute(
        "SELECT explanation FROM events WHERE event_id = ?", (kept,)
    ).fetchone()["explanation"] == "appended before the illegal write"


# ═════════════════════════════════════════════════════════════════════════════
# 8. Path spelling — one file on disk must not become two file versions
# ═════════════════════════════════════════════════════════════════════════════

def test_nfc_and_nfd_spellings_of_one_path_are_one_file_version(db, tmp_path):
    """FAILS — R1/R4 and SPEC OQ2. OQ2 makes two `files` rows legitimate only for two
    *simultaneously live copies*. NFC and NFD spellings of one name are not two
    copies; on APFS and HFS+ they open the same inode.

    `observe_path` resolves identity by comparing `current_path` as an exact Python
    string, so the second spelling matches no row and mints a new file version. The
    two rows then share a content hash AND a `normalized_filename`, and neither is
    ever treated as dead, because `Path(...).exists()` resolves both to the same real
    file. They coexist permanently.

    This is not hypothetical on the target platform: a path read from a directory
    listing arrives decomposed, while the same path typed by a user, stored in JSON,
    or round-tripped through another tool arrives composed. P3 legitimately produces
    both within one scan.

    Downstream: §2.9 reports a duplicate family whose two members are one file.
    §8.3's collision policy — two files whose "hashes prove the files are identical" —
    offers to delete one of them, which deletes both. P12 moves the file under one
    row and V1 then fails for the other, which now points at a path that no longer
    exists. `files_table` already normalises `filename` to NFC; the path it resolves
    identity on is not normalised at all.
    """
    import unicodedata

    composed = tmp_path / unicodedata.normalize("NFC", "café.txt")
    decomposed = tmp_path / unicodedata.normalize("NFD", "café.txt")
    composed.write_bytes(b"one file, two spellings")
    if not (decomposed.exists() and decomposed.read_bytes() == composed.read_bytes()):
        pytest.skip("filesystem does not fold NFC/NFD; here the two names are two files")

    first = observe_path(db, composed, **scan(composed))
    second = observe_path(db, decomposed, **scan(decomposed))

    assert first == second, (
        "one file on disk was recorded as two file versions because its path was "
        "spelled two ways"
    )


def test_a_symlink_and_its_target_are_recorded_as_two_file_versions(db, tmp_path):
    """CHARACTERISES — deliberately pins current behaviour; does NOT assert a fix.

    P1 has no symlink handling: `hash_file` and `stat()` both follow links, so a
    symlink and its target become two `files` rows with one content hash, one size,
    and nothing recorded that distinguishes a link from a copy — no realpath, no flag.

    `files` gained `st_dev`/`st_ino` when the duplicate-family quadratic was fixed, so
    the two rows now differ in one more column. It does not settle this: the columns
    hold what `lstat` said about each row's OWN path, so the link's row carries the
    link's inode and the target's row carries the target's, exactly as two unrelated
    copies would. Nothing in the row says one of these paths points at the other, and
    a reader still cannot tell a link from a copy.

    Whose defect this is, is genuinely unsettled in the SPEC. Contract in gives P3
    "a path, its stat result, ... its bytes to hash" and P3 owns scan traversal
    (§1.1), so excluding or resolving links may well be P3's. But OQ2 — the ruling
    that makes two rows correct — is written about "two simultaneously live copies",
    and a symlink is one file with two names, not a copy.

    The consequence is real either way and is recorded here so whoever settles it
    sees it: §8.3's collision policy acts on files whose "hashes prove the files are
    identical", and deleting the target of a symlink pair destroys both members. This
    test pins today's behaviour so that a deliberate change is visible in the diff.
    """
    target = tmp_path / "real.txt"
    target.write_bytes(b"payload")
    link = tmp_path / "link.txt"
    link.symlink_to(target)

    target_id = observe_path(db, target, **scan(target))
    link_id = observe_path(db, link, **scan(link))

    assert target_id != link_id, "current behaviour: two independent file versions"
    rows = {r["file_id"]: r for r in db.execute("SELECT * FROM files")}
    assert rows[target_id]["content_hash"] == rows[link_id]["content_hash"]
    assert rows[target_id]["observed_size"] == rows[link_id]["observed_size"]
    columns = {r["name"] for r in db.execute("PRAGMA table_info(files)")}
    assert not {"real_path", "is_symlink", "link_target"} & columns, (
        "no column distinguishes a link from a copy; see the SPEC ambiguity above"
    )
    assert rows[target_id]["st_ino"] != rows[link_id]["st_ino"], (
        "the identity columns hold each row's own inode, which is what makes them two "
        "rows here; they say nothing about one path pointing at the other"
    )


def test_path_history_shows_both_ends_of_a_move_in_order(db, tmp_path):
    """PINS — Contract out §2, `file_path_history(file_id) -> ordered (path,
    volume_id, observed_at, event_id)`, and Done-means 2. A rename must leave the old
    path readable: §8.2 separates identity from pathname precisely so a file the user
    reorganised outside the product is still the same file, and P12's undo needs the
    path it came from."""
    from database_agent.files_table import file_path_history

    original = tmp_path / "before.txt"
    original.write_bytes(b"movable bytes")
    file_id = observe_path(db, original, **scan(original))
    moved = tmp_path / "after.txt"
    original.rename(moved)
    assert observe_path(db, moved, **scan(moved)) == file_id, "a move is not a new version (R2)"

    history = file_path_history(db, file_id)
    assert [Path(r["path"]).name for r in history] == ["before.txt", "after.txt"]
    assert [r["event_id"] for r in history] == sorted(r["event_id"] for r in history)
    assert all(r["volume_id"] is None for r in history), (
        "OQ9 is open; the column is published as unknown, never as a value a consumer "
        "could mistake for the volume this path was observed on"
    )
    assert get_file(db, file_id)["current_path"] == str(moved)
