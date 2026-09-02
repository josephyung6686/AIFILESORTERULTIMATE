# tests/p7/test_p7_suspension_in_the_policy.py
"""What authorised the one send that cannot be taken back.

The owner was asked whether the `80` §8 suspension should live in the stored
`Policy` rather than in a gate constructor argument, and answered *"just do it in
the best interest of the north star"*. The judgement below is the lead's under that
instruction rather than a detailed ruling, and it is recorded that way.

**The reasoning, so a later reader can check it rather than take it.** §8.4's audit
record names the authorizing policy. Until this, the fact that authorised a
self-description to be released lived in an argument passed to `Gate.__init__` and
reached no record at all — so the ONE irreversible act in the product was also the
one least explainable afterwards. `80` §1.1 already says revocation cannot retract
what has left the device; that is survivable while the record can still answer *what
left, and under what authority*, and unsurvivable when it cannot.

Three constraints came with the instruction and each is a test here.

1. **Do not widen what the flag means on the way in.** It is not a "cloud was
   allowed" bit. The column holds WHICH always-local kinds this policy suspends the
   rule for, and its vocabulary is `items.SUSPENDED_ITEM_KINDS` — one member, owner
   approved, scoped to the self-description reference. A second suspension would
   need a second type and a second approval before it could be named here.
2. **The audit must answer the question a person would actually ask** — *what was
   sent, when, and what said that was permitted* — from the stored record, not by
   re-deriving it from code. So the test below follows the audit row to its policy
   version and answers all three, rather than asserting that a column exists.
3. **A policy stored before this change has no such flag, and must not read as
   permitted.** Absent means refuse, never guess. Both shapes of absent are tested:
   a row inserted without the value, and a database whose table predates the column
   entirely — `CREATE TABLE IF NOT EXISTS` means that second one is real.

**It is not the cloud-consent record and must never be confused with it.**
`database_agent/cloud_consent.py` answers "may this FOLDER's files reach a cloud
model", is keyed to a corpus root, and is append-only with a person and a time. This
answers "did the policy in force suspend the always-local rule for one item kind".
Two records of one run that disagree is the failure that module found in its own
work and fixed; the last test here is the seam from this side.
"""
from __future__ import annotations

import inspect
import sqlite3

import pytest

from privacy.gate import Gate
from privacy.items import SUSPENDED_ITEM_KINDS, SelfDescription
from privacy.policy import (
    UNSET_POLICY_VERSION, Policy, current_policy, policy_at, set_policy,
)
from privacy.schema import POLICIES_TABLE
from privacy.vocabulary import OutOfVocabulary

PLAN = "plan-1"
AT = "2026-09-02T12:00:00+00:00"
COMPONENT = "p7-test"


def _draft(**overrides) -> Policy:
    fields = dict(
        policy_version=UNSET_POLICY_VERSION, operation_mode="offline",
        consent_grants=(), redaction_settings={}, automatic_move_permissions={},
        plan_version=PLAN, set_at=AT,
    )
    fields.update(overrides)
    return Policy(**fields)


def _store(conn, **overrides) -> str:
    return set_policy(conn, _draft(**overrides), component_version=COMPONENT,
                      user_id="joseph", reason="a test set this policy")


# --- constraint 1: it records WHICH kind, and cannot widen ---------------------------


def test_the_policy_records_which_kind_was_suspended_and_not_that_cloud_was_allowed(
        p7_conn):
    """A boolean would read as "cloud was on for this run" the first time somebody
    skim-read it. A list of KINDS cannot: it names the one thing the owner opened a
    door for, and says nothing about anything else."""
    version = _store(p7_conn, suspended_item_kinds=("self_description",))

    assert policy_at(p7_conn, version).suspended_item_kinds == ("self_description",)


def test_it_cannot_name_a_kind_nobody_approved_a_door_for(p7_conn):
    """The scoping, enforced where the value is written rather than where it is read.
    `80` §8.1: "this suspension reaches nothing but the self-description." A second
    kind would need a second type in `items.py` and a second approval recorded at a
    second member before it could be spelled here at all."""
    for forbidden in ("ocr_output", "user_edits", "paths", "excerpt", "filename", ""):
        with pytest.raises(OutOfVocabulary):
            _draft(suspended_item_kinds=(forbidden,))


def test_the_vocabulary_is_the_one_items_publishes_and_not_a_second_list(p7_conn):
    """Spelled once. A list retyped here would drift from the type table the moment
    a kind was added or renamed, and the drift would open a door rather than close
    one."""
    assert SUSPENDED_ITEM_KINDS == ("self_description",)
    version = _store(p7_conn, suspended_item_kinds=SUSPENDED_ITEM_KINDS)

    assert policy_at(p7_conn, version).suspended_item_kinds == SUSPENDED_ITEM_KINDS


# --- constraint 3: absent is the safe answer, in both of its shapes -----------------


def test_a_policy_that_says_nothing_suspends_nothing(p7_conn):
    version = _store(p7_conn)

    assert policy_at(p7_conn, version).suspended_item_kinds == ()
    assert current_policy(p7_conn, plan_version=PLAN).suspended_item_kinds == ()


def test_a_row_written_before_this_change_does_not_read_as_permitted(p7_conn):
    """The first shape of absent: a row whose value was never set. It must come back
    as "nothing suspended" rather than as anything a caller could act on."""
    p7_conn.execute(
        f"INSERT INTO {POLICIES_TABLE} (policy_version, plan_version, "
        "operation_mode, consent_grants, redaction_settings, "
        "automatic_move_permissions, set_at) VALUES (?,?,?,?,?,?,?)",
        ("policy-old", PLAN, "offline", "[]", "{}", "{}", AT))

    assert policy_at(p7_conn, "policy-old").suspended_item_kinds == ()


def test_a_database_whose_table_predates_the_column_does_not_read_as_permitted():
    """The second shape, and the one that is easy to forget. The DDL is `CREATE
    TABLE IF NOT EXISTS`, so a database created before this change keeps its old
    table and the column is not there at all. Reading it must answer "nothing
    suspended" rather than raising -- and it must certainly not answer "permitted"
    -- because a person's existing plan is exactly where an old table lives."""
    old = sqlite3.connect(":memory:")
    old.row_factory = sqlite3.Row
    old.execute(
        f"CREATE TABLE {POLICIES_TABLE} ("
        "policy_version TEXT PRIMARY KEY, plan_version TEXT NOT NULL, "
        "operation_mode TEXT NOT NULL, consent_grants TEXT NOT NULL, "
        "redaction_settings TEXT NOT NULL, automatic_move_permissions TEXT NOT NULL, "
        "set_at TEXT NOT NULL, supersedes TEXT, superseded_by TEXT, "
        "supersede_reason TEXT)")
    old.execute(
        f"INSERT INTO {POLICIES_TABLE} (policy_version, plan_version, "
        "operation_mode, consent_grants, redaction_settings, "
        "automatic_move_permissions, set_at) VALUES (?,?,?,?,?,?,?)",
        ("policy-ancient", PLAN, "offline", "[]", "{}", "{}", AT))

    assert policy_at(old, "policy-ancient").suspended_item_kinds == ()
    old.close()


# --- constraint 2: the record answers the question, end to end ----------------------


def test_the_stored_record_answers_what_was_sent_when_and_what_permitted_it(p7_conn):
    """Read from the database and answered by joining, not by asking the code.

    A person whose sentence has gone somewhere it cannot be recalled from asks three
    things, and every one of them is answered here out of stored rows: WHAT left,
    WHEN, and WHAT SAID IT WAS ALLOWED. The third is the one that did not exist
    before this change -- the authority lived in a constructor argument, so the
    honest answer was "nothing in the record says".
    """
    version = _store(p7_conn, suspended_item_kinds=("self_description",))

    # WHAT SAID IT WAS PERMITTED -- followed from the policy version the audit
    # record carries, which is the only handle a reader has.
    authorising = policy_at(p7_conn, version)
    assert "self_description" in authorising.suspended_item_kinds, (
        "the record cannot say what permitted the send, which is the whole defect "
        "this change exists to fix")

    # WHEN the authority was given, from the same row.
    assert authorising.set_at == AT

    # AND THE ACT IS IN THE LOG. §8.2's reconstruction question is answered by
    # `policy_set`, which `set_policy` appends inside the same transaction as the
    # row -- so a policy that authorised a send cannot exist without an event
    # saying it was set.
    logged = [row[0] for row in p7_conn.execute(
        "SELECT event_type FROM events ORDER BY event_id")]
    assert "policy_set" in logged


def test_the_join_an_auditor_makes_is_the_one_the_record_supports(p7_conn):
    """The handle, pinned. `AuditRecord.policy_version` is the ONLY thing a reader
    holds after the fact, so the two halves of the answer meet there or not at all:
    without this, the audit could name a policy and the policy could carry the
    suspension and nothing would connect them.

    Named for what it proves. It does not replay a release -- the door is sealed and
    nothing walks through it yet -- so what it pins is that the field a later join
    needs exists under that name and resolves to a policy that answers.
    """
    import dataclasses

    from privacy.audit import AuditRecord

    version = _store(p7_conn, suspended_item_kinds=("self_description",))
    names = {field.name for field in dataclasses.fields(AuditRecord)}

    assert {"policy_version", "authorizing_policy", "observed_at"} <= names, (
        "the audit record no longer carries the handle a reader follows to the "
        "authority, so 'what said this was permitted' has become unanswerable "
        "again -- which is the defect this whole change exists to fix")
    resolved = policy_at(p7_conn, version)
    assert resolved.policy_version == version
    assert resolved.suspended_item_kinds == ("self_description",)


# --- the gate reads the record, not an argument -------------------------------------


def test_the_gate_takes_no_argument_for_this_any_more(p7_conn):
    """The point of the change. A constructor argument is a fact about a run that
    survives only as long as the process; the whole defect was that §8.4's audit
    named a policy which did not carry it."""
    parameters = inspect.signature(Gate.__init__).parameters

    assert "suspension_permits_self_description" not in parameters
    for name in parameters:
        assert "self_description" not in name, (
            f"{name!r} puts the suspension back on the constructor, where it "
            "reaches no record")


def test_the_gate_refuses_a_self_description_under_a_policy_that_permits_none(
        p7_conn):
    from privacy.items import SelfDescriptionNotAdmitted, check_item

    _store(p7_conn)
    policy = current_policy(p7_conn, plan_version=PLAN)

    with pytest.raises(SelfDescriptionNotAdmitted):
        check_item(SelfDescription(question_id="role:me"), unit_length=None,
                   zone=None, protected=False, sensitive_keys=frozenset(),
                   allow_unratified=True,
                   suspension_permits_self_description=(
                       "self_description" in policy.suspended_item_kinds))


def test_the_gate_admits_one_under_a_policy_that_permits_it(p7_conn):
    from privacy.items import check_item

    _store(p7_conn, suspended_item_kinds=("self_description",))
    policy = current_policy(p7_conn, plan_version=PLAN)

    assert check_item(
        SelfDescription(question_id="role:me"), unit_length=None, zone=None,
        protected=False, sensitive_keys=frozenset(), allow_unratified=False,
        suspension_permits_self_description=(
            "self_description" in policy.suspended_item_kinds)) is None


# --- the seam with the OTHER record of one run --------------------------------------


def test_this_is_not_the_cloud_consent_record_and_neither_implies_the_other(p7_conn):
    """`b098af8` added `database_agent/cloud_consent.py` for a different question:
    may this FOLDER's files reach a cloud model, keyed to a corpus root, append-only,
    carrying who decided and when. This one says whether the policy in force
    suspended the always-local rule for one item kind.

    Two records of one run that disagree is the failure that module found in its own
    work and fixed. They cannot disagree here because they answer different
    questions -- but only while nothing reads one as the other, which is what this
    pins from this side."""
    from database_agent import cloud_consent

    suspended = _store(p7_conn, suspended_item_kinds=("self_description",))
    policy = policy_at(p7_conn, suspended)

    # A policy that suspends the always-local rule says NOTHING about the operation
    # mode, and does not turn a cloud one on.
    assert policy.operation_mode == "offline"
    # And the consent module holds no opinion about item kinds: its vocabulary is a
    # decision about a folder, not about what may be released.
    assert set(cloud_consent.DECISIONS) == {"enabled", "disabled"}
    assert not any("self_description" in decision
                   for decision in cloud_consent.DECISIONS)
