from datetime import datetime, timezone
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.events import append_event
from database_agent.learning import SCOPES, learning_records, reset_preferences


def _correction(conn, scope, subject, explanation, **overrides):
    """A user-action event authored by the acting part (M8). `correction_subject`
    is the subject at `correction_scope`; it is not a file id unless scope=file."""
    fields = dict(
        event_type="user group decision", file_id=None, content_hash=None,
        subsystem="P9", component_version="p9-fixture",
        observed_at=datetime.now(timezone.utc).isoformat(),
        explanation=explanation, correction_scope=scope, correction_subject=subject,
        polarity="reject", proposal_class="group", basis_key="opaque-basis-1",
        user_id="u1",
    )
    fields.update(overrides)
    return append_event(conn, **fields)


def test_the_six_scopes():
    assert SCOPES == ("file", "group", "node", "template", "domain", "corpus")


def test_a_file_scoped_correction_is_not_returned_by_a_corpus_read(conn):
    # §8.7's worked case: one transcript belonging in a Columbia packet must not
    # teach the engine that all transcripts belong there.
    create_schema(conn)
    _correction(conn, "file", "f1", "this one belongs here")
    assert learning_records(conn, "corpus", "f1") == []
    assert len(learning_records(conn, "file", "f1")) == 1


def test_a_non_file_subject_is_addressable(conn):
    # 10-i4-learning-ops.md: P6/P7/P8/P9/P10/P11 query at group, node, template,
    # domain and corpus scope. None of those subjects is a file id.
    create_schema(conn)
    for scope, subject in (("group", "g1"), ("node", "n1"), ("template", "t1"),
                           ("domain", "d1"), ("corpus", "c1")):
        _correction(conn, scope, subject, f"rejected at {scope}")
        found = learning_records(conn, scope, subject)
        assert len(found) == 1, f"{scope} read missed its own record"
        assert found[0]["file_id"] is None
        assert found[0]["correction_subject"] == subject


def test_the_record_returns_its_proposal_class_and_basis_key(conn):
    # SPEC Contract out §7. Opaque to P1: stored and returned, never compared.
    create_schema(conn)
    _correction(conn, "group", "g1", "rejected",
                proposal_class="group", basis_key="sorted-anchor-facts")
    record = learning_records(conn, "group", "g1")[0]
    assert record["proposal_class"] == "group"
    assert record["basis_key"] == "sorted-anchor-facts"


def test_the_record_returns_its_polarity(conn):
    # SPEC Contract out §7: polarity ∈ accept | reject, supplied by the acting
    # part. 10-i4-learning-ops.md's query-before-propose rule fires on an unreset
    # reject, so a reader must be able to tell one from the other without parsing
    # explanation free text.
    create_schema(conn)
    _correction(conn, "group", "g1", "rejected here", polarity="reject")
    _correction(conn, "group", "g2", "accepted here", polarity="accept")
    assert learning_records(conn, "group", "g1")[0]["polarity"] == "reject"
    assert learning_records(conn, "group", "g2")[0]["polarity"] == "accept"


def test_p1_neither_infers_polarity_nor_filters_on_it(conn):
    # P1 stores and returns; it decides nothing from the value. An accept and a
    # reject at the same scope and subject both come back, in event order, and
    # P1 derives neither from the event type.
    create_schema(conn)
    _correction(conn, "group", "g1", "first", polarity="accept")
    _correction(conn, "group", "g1", "second", polarity="reject")
    returned = learning_records(conn, "group", "g1")
    assert [r["polarity"] for r in returned] == ["reject", "accept"]

    # A user-action event whose author supplied no polarity is stored as unknown,
    # never guessed from `event_type`.
    _correction(conn, "group", "g3", "no polarity supplied", polarity=None)
    assert learning_records(conn, "group", "g3")[0]["polarity"] is None

    import database_agent.learning as learning_module
    source = Path(learning_module.__file__).read_text(encoding="utf-8")
    assert "accept" not in source and "reject" not in source


def test_a_rejection_returns_with_its_evidence(conn):
    create_schema(conn)
    _correction(conn, "group", "g1", "rejected: evidence_ref=obs-key-123")
    records = learning_records(conn, "group", "g1")
    assert "obs-key-123" in records[0]["explanation"]


def test_reset_appends_and_deletes_nothing(conn):
    create_schema(conn)
    _correction(conn, "domain", "d1", "first preference")
    before = conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    reset_preferences(conn, "domain", "d1", author="P13",
                      component_version="p13-fixture", user_id="u1")
    after = conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    assert after == before + 1
    # pre-reset records stay readable in the log (R6) — reset deletes nothing
    surviving = conn.execute(
        "SELECT explanation FROM events WHERE correction_subject = 'd1'"
    ).fetchall()
    assert any("first preference" in r["explanation"] for r in surviving)


def test_later_reads_honour_the_reset(conn):
    # SPEC §7: "a scoped reset record that later reads honour". A reader that
    # queries before proposing must see an un-learned preference as un-learned.
    create_schema(conn)
    _correction(conn, "domain", "d1", "before the reset")
    assert len(learning_records(conn, "domain", "d1")) == 1

    reset_preferences(conn, "domain", "d1", author="P13",
                      component_version="p13-fixture", user_id="u1")
    assert learning_records(conn, "domain", "d1") == []

    _correction(conn, "domain", "d1", "after the reset")
    remaining = learning_records(conn, "domain", "d1")
    assert [r["explanation"] for r in remaining] == ["after the reset"]


def test_a_reset_is_scoped_and_does_not_clear_its_neighbours(conn):
    create_schema(conn)
    _correction(conn, "domain", "d1", "kept")
    _correction(conn, "domain", "d2", "also kept")
    _correction(conn, "group", "d1", "different scope, same subject id")
    reset_preferences(conn, "domain", "d1", author="P13",
                      component_version="p13-fixture", user_id="u1")
    assert learning_records(conn, "domain", "d1") == []
    assert len(learning_records(conn, "domain", "d2")) == 1
    assert len(learning_records(conn, "group", "d1")) == 1


def test_reset_appends_p13s_registered_type_and_mints_nothing(conn):
    # P13 SPEC §2: reset arrives as review_action, surface = learning,
    # action = reset_learning. The event P13 authors is `review action routed`.
    create_schema(conn)
    event_id = reset_preferences(conn, "domain", "d1", author="P13",
                                 component_version="p13-fixture", user_id="u1")
    row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    assert row["event_type"] == "review action routed"
    assert row["subsystem"] == "P13"
    assert row["user_id"] == "u1"


def test_unknown_scope_is_rejected(conn):
    create_schema(conn)
    with pytest.raises(ValueError):
        learning_records(conn, "everything", "x")
