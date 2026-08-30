"""§8.7 correction learning: the query-before-propose guard, and what P6 may author.

The read half is live today. The write half is P13's stand-in -- P13 does not exist,
so these tests drive `record_correction` directly, which is how every P13 surface is
exercised in this plan.
"""
from __future__ import annotations

import inspect
import json
import sqlite3

import pytest

from database_agent.events import (
    CORRECTION_FIELDS,
    CORRECTION_SCOPES,
    RESERVED_EVENT_TYPES,
    MalformedEvent,
    append_event,
)
from database_agent.learning import learning_records, reset_cutoff, reset_preferences

from facts import learning as learning_module
from facts.authorship import AUTHORED_EVENT_TYPES
from facts.learning import (
    POLARITIES,
    PROPOSAL_CLASS,
    MalformedCorrection,
    basis_key,
    is_suppressed,
    record_correction,
)

CLOCK = "2026-08-22T09:00:00+00:00"
REF = "sha256:" + "e" * 64
OTHER_REF = "sha256:" + "d" * 64


def a_rejection(connection, **overrides) -> int:
    """The walking case: the user rejects `subject = BUSIB 4300` on one file."""
    fields = dict(
        action="reject_fact",
        scope="file",
        subject="file-1",
        polarity="reject",
        file_id="file-1",
        field_key="subject",
        value_id="value-busib-4300",
        evidence_refs=(REF,),
        user_id="user-1",
        observed_at=CLOCK,
    )
    fields.update(overrides)
    return record_correction(connection, **fields)


def event_count(connection) -> int:
    return connection.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]


# --- what P6 identifies a correction by -------------------------------------------


def test_the_proposal_class_is_the_claim_and_p6_mints_no_event_type():
    # I4's equivalence table: P6 owns proposal_class `fact`, basis (file_id, field, value_id).
    assert PROPOSAL_CLASS == "fact"
    # The two names this module writes are P6's own authored pair, and both are already
    # among §8.2's reserved nineteen -- so P6 registers nothing and mints nothing.
    assert AUTHORED_EVENT_TYPES == ("fact creation", "fact rejection")
    for name in AUTHORED_EVENT_TYPES:
        assert name in RESERVED_EVENT_TYPES
    assert POLARITIES == ("accept", "reject")


def test_the_basis_key_is_i4s_triple_serialized_once_and_readably():
    key = basis_key(file_id="file-1", field_key="subject", value_id="value-busib-4300")
    parsed = json.loads(key)
    # Exactly I4's three parts, and nothing else: no plan version, no dossier hash,
    # no display label, no member set.
    assert set(parsed) == {"file_id", "field_key", "value_id"}
    assert parsed["file_id"] == "file-1"
    assert parsed["field_key"] == "subject"
    assert parsed["value_id"] == "value-busib-4300"


def test_the_basis_key_is_deterministic_and_independent_of_argument_order():
    first = basis_key(file_id="f", field_key="subject", value_id="v")
    second = basis_key(value_id="v", file_id="f", field_key="subject")
    assert first == second


def test_the_basis_key_is_injective_over_its_three_parts():
    # A delimiter-joined key would collide these two, and a collision silently
    # suppresses a proposal the user never rejected.
    left = basis_key(file_id="a|b", field_key="subject", value_id="v")
    right = basis_key(file_id="a", field_key="b|subject", value_id="v")
    assert left != right
    assert basis_key(file_id="", field_key="x", value_id="y") != \
        basis_key(file_id="x", field_key="", value_id="y")


# --- the guard --------------------------------------------------------------------


def test_an_empty_store_suppresses_nothing(p6_conn):
    assert is_suppressed(
        p6_conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is False


def test_an_unreset_reject_suppresses_the_same_claim(p6_conn):
    a_rejection(p6_conn)
    assert is_suppressed(
        p6_conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is True


def test_the_guard_writes_nothing(p6_conn):
    a_rejection(p6_conn)
    before = event_count(p6_conn)
    is_suppressed(
        p6_conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    )
    is_suppressed(
        p6_conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-other",
    )
    assert event_count(p6_conn) == before
    # Nor does it invent a reset: the cutoff is exactly where it was.
    assert reset_cutoff(p6_conn, "file", "file-1") is None


def test_a_different_basis_key_at_the_same_scope_still_emits(p6_conn):
    a_rejection(p6_conn)
    # A different value under the same field is a different claim (I4: "A different
    # value is a different proposal").
    assert is_suppressed(
        p6_conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4400",
    ) is False
    # A different field on the same file is a different claim.
    assert is_suppressed(
        p6_conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="term", value_id="value-busib-4300",
    ) is False


def test_a_record_at_the_wrong_proposal_class_is_ignored(p6_conn):
    key = basis_key(file_id="file-1", field_key="subject", value_id="value-busib-4300")
    # P11's `placement` class, same scope, same subject, same basis string. P6 must
    # not read another part's rejection as its own.
    append_event(
        p6_conn, event_type="placement recommendation", subsystem="P11",
        component_version="0.0.0", observed_at=CLOCK, explanation="{}",
        correction_scope="file", correction_subject="file-1", polarity="reject",
        proposal_class="placement", basis_key=key, user_id="user-1",
    )
    assert is_suppressed(
        p6_conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is False


def test_an_accept_is_not_a_suppression(p6_conn):
    a_rejection(p6_conn, action="confirm_fact", polarity="accept", evidence_refs=())
    assert is_suppressed(
        p6_conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is False


def test_a_reset_at_that_scope_and_subject_allows_emission_again(p6_conn):
    rejection_id = a_rejection(p6_conn)
    reset_id = reset_preferences(
        p6_conn, "file", "file-1",
        author="P13", component_version="0.0.0", user_id="user-1",
    )
    # The mechanism, not a docstring: the reset's event_id IS the cutoff, and the
    # rejection sits below it, so `learning_records` stops returning it.
    assert reset_cutoff(p6_conn, "file", "file-1") == reset_id
    assert rejection_id < reset_id
    assert learning_records(p6_conn, "file", "file-1") == []
    assert is_suppressed(
        p6_conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is False
    # R6: the reset deleted nothing. The rejection is still in the append-only log.
    surviving = p6_conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE event_id = ?", (rejection_id,)
    ).fetchone()["n"]
    assert surviving == 1


def test_a_rejection_after_a_reset_suppresses_again(p6_conn):
    # The cutoff is a floor, not an off switch: a fresh rejection above it binds.
    a_rejection(p6_conn)
    reset_preferences(
        p6_conn, "file", "file-1",
        author="P13", component_version="0.0.0", user_id="user-1",
    )
    a_rejection(p6_conn)
    assert is_suppressed(
        p6_conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is True


def test_the_guard_stops_the_write_a_resolver_would_have_made(p6_conn):
    """Task 20's resolver shape, four lines of it, so the composition is proved here."""
    a_rejection(p6_conn)
    claims = [
        ("file-1", "subject", "value-busib-4300"),   # the rejected one
        ("file-1", "subject", "value-busib-4400"),   # a different value
        ("file-2", "subject", "value-busib-4300"),   # a different file
    ]
    written = []
    for file_id, field_key, value_id in claims:
        if is_suppressed(
            p6_conn, scope="file", subject_id=file_id,
            file_id=file_id, field_key=field_key, value_id=value_id,
        ):
            continue
        written.append((file_id, field_key, value_id))
    assert written == [
        ("file-1", "subject", "value-busib-4400"),
        ("file-2", "subject", "value-busib-4300"),
    ]


# --- §8.7's scopes, and the two worked examples ------------------------------------


def test_every_scope_p1_accepts_p6_can_record(p6_conn):
    assert CORRECTION_SCOPES == ("file", "group", "node", "template", "domain", "corpus")
    for index, scope in enumerate(CORRECTION_SCOPES):
        a_rejection(p6_conn, scope=scope, subject=f"subject-{index}")
    assert event_count(p6_conn) == len(CORRECTION_SCOPES)


def test_a_seventh_scope_is_refused_by_p1_and_p6_does_not_respell_the_six(p6_conn):
    with pytest.raises(MalformedEvent):
        a_rejection(p6_conn, scope="semester")
    # P6 holds no copy of the six: the refusal came from P1's writer, which is the
    # single place they are spelled.
    assert "semester" not in CORRECTION_SCOPES
    assert not any(
        isinstance(value, tuple) and set(value) == set(CORRECTION_SCOPES)
        for value in vars(learning_module).values()
    )


def test_one_transcript_does_not_teach_the_engine_that_all_transcripts_belong_there(p6_conn):
    # §8.7's own worked case: "a user may say that one particular transcript belongs in
    # a Columbia packet but should not teach the engine that all transcripts belong there."
    a_rejection(
        p6_conn, scope="file", subject="transcript-1", file_id="transcript-1",
        field_key="institution", value_id="value-columbia",
    )
    assert is_suppressed(
        p6_conn, scope="file", subject_id="transcript-1",
        file_id="transcript-1", field_key="institution", value_id="value-columbia",
    ) is True
    # A second transcript is untouched -- scope is exact, and the basis names the file.
    assert is_suppressed(
        p6_conn, scope="file", subject_id="transcript-2",
        file_id="transcript-2", field_key="institution", value_id="value-columbia",
    ) is False
    # And the file-scoped record is invisible to a corpus-scoped read (P1's rule).
    assert learning_records(p6_conn, "corpus", "transcript-1") == []


def test_a_repeated_corpus_scoped_rejection_is_readable_at_corpus_scope(p6_conn):
    # §8.7's other worked case: "if the user repeatedly rejects an association between
    # their authoring school and application documents, the product can lower the role
    # or weight of author-affiliation evidence across that corpus."
    for index, file_id in enumerate(("app-1", "app-2", "app-3")):
        a_rejection(
            p6_conn, scope="corpus", subject="corpus", file_id=file_id,
            field_key="authored_by", value_id="value-columbia",
            observed_at=f"2026-08-2{index}T09:00:00+00:00",
        )
    records = learning_records(p6_conn, "corpus", "corpus")
    assert len(records) == 3
    assert {row["proposal_class"] for row in records} == {PROPOSAL_CLASS}
    assert {row["polarity"] for row in records} == {"reject"}
    # The three are distinguishable from one another by basis, so "repeatedly" is
    # countable by the consumer that weights. P6 weights nothing: §3.7's weights are
    # injected (Task 11) and this module publishes none.
    assert len({row["basis_key"] for row in records}) == 3
    # The corpus record is not a file-scoped one, and the file-scoped read is empty.
    assert learning_records(p6_conn, "file", "app-1") == []


# --- what a correction record must carry ------------------------------------------


def test_a_correction_writes_all_five_of_p1s_correction_fields(p6_conn):
    a_rejection(p6_conn)
    row = p6_conn.execute("SELECT * FROM events").fetchone()
    for column in CORRECTION_FIELDS:
        assert row[column] is not None and row[column] != ""
    assert row["proposal_class"] == PROPOSAL_CLASS
    assert row["polarity"] == "reject"
    assert row["correction_scope"] == "file"
    assert row["correction_subject"] == "file-1"
    assert row["basis_key"] == basis_key(
        file_id="file-1", field_key="subject", value_id="value-busib-4300"
    )


def test_the_subject_is_not_derived_from_the_file(p6_conn):
    # Five of §8.7's six scopes have no file, so the subject is always the caller's.
    a_rejection(p6_conn, scope="corpus", subject="corpus", file_id="app-1")
    row = p6_conn.execute("SELECT * FROM events").fetchone()
    assert row["correction_subject"] == "corpus"
    assert row["file_id"] == "app-1"


def test_the_polarity_chooses_p6s_own_event_type_and_no_other(p6_conn):
    a_rejection(p6_conn)
    a_rejection(p6_conn, action="confirm_fact", polarity="accept", evidence_refs=())
    types = [row["event_type"] for row in p6_conn.execute(
        "SELECT event_type FROM events ORDER BY event_id"
    )]
    assert types == ["fact rejection", "fact creation"]


def test_the_rejection_is_stored_with_the_evidence_that_produced_it(p6_conn):
    a_rejection(p6_conn, evidence_refs=(REF, OTHER_REF))
    row = p6_conn.execute("SELECT explanation FROM events").fetchone()
    explanation = json.loads(row["explanation"])
    # §8.7: "Rejected groups, rejected destination matches, rejected labels, and
    # rejected residual recommendations must be stored with the evidence that
    # produced them."
    assert explanation["evidence_refs"] == [REF, OTHER_REF]
    assert explanation["proposal_class"] == PROPOSAL_CLASS
    assert explanation["action"] == "reject_fact"


def test_a_rejection_without_evidence_is_refused(p6_conn):
    with pytest.raises(MalformedCorrection):
        a_rejection(p6_conn, evidence_refs=())
    assert event_count(p6_conn) == 0


def test_a_correction_with_no_user_is_refused(p6_conn):
    # `learning_records` filters `user_id IS NOT NULL`. A correction stored without one
    # is storable and permanently unreadable -- a silently lost user gesture.
    with pytest.raises(MalformedCorrection):
        a_rejection(p6_conn, user_id="")
    assert event_count(p6_conn) == 0


def test_an_unknown_polarity_is_refused(p6_conn):
    with pytest.raises(MalformedCorrection):
        a_rejection(p6_conn, polarity="maybe")
    assert event_count(p6_conn) == 0


def test_an_unnamed_action_is_refused(p6_conn):
    with pytest.raises(MalformedCorrection):
        a_rejection(p6_conn, action="")
    assert event_count(p6_conn) == 0


def test_p6_does_not_branch_on_the_action_it_is_handed(p6_conn):
    # P13 owns the action vocabulary. P6 stores the string and branches on polarity.
    a_rejection(p6_conn, action="disable_suggestion_type")
    assert is_suppressed(
        p6_conn, scope="file", subject_id="file-1",
        file_id="file-1", field_key="subject", value_id="value-busib-4300",
    ) is True


# --- the negatives §8.7 turns on ---------------------------------------------------


def test_the_correction_and_its_evidence_can_never_be_removed(p6_conn):
    a_rejection(p6_conn)
    # P1 enforces R6 by trigger, not by convention -- verified live: both raise
    # IntegrityError("events is append-only (R6, §8.2)").
    with pytest.raises(sqlite3.IntegrityError):
        p6_conn.execute("DELETE FROM events")
    with pytest.raises(sqlite3.IntegrityError):
        p6_conn.execute("UPDATE events SET explanation = '{}'")
    assert event_count(p6_conn) == 1


def test_suppression_is_versionless_and_survives_a_new_plan_version(p6_conn):
    # I4: "a rejection in plan v2 has to stop the same proposal in v3. That is why
    # the store is a versionless projection over `events`".
    columns = {row[1] for row in p6_conn.execute("PRAGMA table_info(events)")}
    assert "plan_version" not in columns
    assert "plan_id" not in columns
    parameters = inspect.signature(is_suppressed).parameters
    assert "plan_version" not in parameters
    assert set(parameters) == {
        "conn", "scope", "subject_id", "file_id", "field_key", "value_id"
    }
    assert "plan_version" not in inspect.signature(basis_key).parameters


def test_p6_performs_no_global_training_on_the_users_corpus(p6_conn):
    # §8.7: "The product should not silently train a global model on a user's private
    # corpus." An accumulator at module scope is what that would look like, so there
    # is none -- checked by introspection, not by reading the source text.
    for name, value in vars(learning_module).items():
        if name.startswith("__"):
            continue
        assert not isinstance(value, (dict, list, set, bytearray)), name


def test_the_subsystem_is_named_in_exactly_one_module_and_it_is_not_this_one(p6_conn):
    # M8: `subsystem = "P6"` is written once, in `facts.authorship`. This module gets
    # it from `event_defaults` and never spells it. Exact equality, not substring:
    # the module docstring may name P6; no module-level VALUE may be it.
    literals = {v for v in vars(learning_module).values() if isinstance(v, str)}
    assert "P6" not in literals
    a_rejection(p6_conn)
    assert p6_conn.execute("SELECT subsystem FROM events").fetchone()["subsystem"] == "P6"


def test_the_write_half_has_no_caller_inside_facts():
    # The split this task turns on: P13 routes the gesture, and until P13 exists no
    # module in `src/facts/` may invent a correction. Checked by import graph, not by
    # grepping prose: `facts.learning` is the only module that binds the writer.
    import importlib
    import pkgutil

    import facts

    binders = []
    for info in pkgutil.iter_modules(facts.__path__):
        module = importlib.import_module(f"facts.{info.name}")
        if getattr(module, "record_correction", None) is record_correction:
            binders.append(info.name)
    assert binders == ["learning"]


def test_the_i4_guard_has_a_caller_and_it_is_the_one_producer_that_runs():
    """I4 is enforced, and the module names where. THIS TEST WAS INVERTED.

    It used to read `test_the_i4_guard_still_has_no_caller_and_says_so` and assert
    `callers == []` — an OWED marker, deliberately written to fail on the day the
    guard was wired so the docstring could not go on saying it was owed. That day is
    this one, so the marker becomes its opposite: `is_suppressed` must have a caller,
    and the caller must be the producer that a person's run actually reaches.

    `facts.direct` is that producer: `src/cli.py`'s `_resolver` binds `rule` and `llm`
    to `None`, so `direct_facts` is the whole of this deployment's fact production. A
    guard wired into `facts.rules` instead would be as unreachable as no guard at all,
    which is the failure this whole file exists to make visible.

    `tests/p6/test_p6_learning_guard_wiring.py` drives the behaviour end to end. This
    one is only about reachability, and it counts CALLS rather than mentions. A
    substring scan was written first and it was worthless: deleting the guard while
    leaving `from facts.learning import is_suppressed` behind kept it green, which is
    the exact shape of unreachable-but-looks-wired that this file is about.
    """
    import ast
    import pathlib
    import facts.learning as learning

    def calls_the_guard(tree: ast.Module) -> bool:
        aliases = {"is_suppressed"}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "facts.learning":
                aliases.update(alias.asname or alias.name for alias in node.names
                               if alias.name == "is_suppressed")
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = (func.id if isinstance(func, ast.Name)
                    else func.attr if isinstance(func, ast.Attribute) else None)
            if name in aliases:
                return True
        return False

    callers = sorted(
        str(path) for path in pathlib.Path("src").rglob("*.py")
        if path.name != "learning.py"
        and calls_the_guard(ast.parse(path.read_text(encoding="utf-8")))
    )
    assert callers == ["src/facts/direct.py"], (
        "I4's guard is enforced by `facts.direct.direct_facts` and by nothing else. "
        "If a second producer now writes facts it owes the same three lines; if this "
        "list is empty the guard has gone dark again and every rejection a person "
        "makes is forgotten on their next run.")
    # The docstring must name that call site rather than describe a debt.
    assert "ITS CALL SITE IS `facts.direct.direct_facts`" in learning.__doc__
    assert "enforced by nothing" in learning.__doc__  # only in the past tense, below
    assert "while it stood" in learning.__doc__
