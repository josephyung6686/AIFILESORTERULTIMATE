"""Done-means 8, and I6 held open under D3.

`retraction_limit` and the derived enumeration are the two halves of this task. The
first is a `must` whose wording is deferred, so the test asserts PRESENCE and refuses
to assert words. The second is D3's literal list, so the test asserts the list, the
refusal on both sides of it, and that no tombstone column was built.

Three departures from the PLAN's test text, each forced by the live substrate and each
reported rather than absorbed:

1. Task 5's `policy.revoke_consent` calls `_require_in_force`, so a `Policy` literal
   built in this file is `StalePolicyVersion` on arrival. Every revocation here derives
   from the snapshot `current_policy` returns, which is what a real caller does.
2. `test_a_group_release_covering_a_file_in_scope_is_listed` is a LIVE assertion, not
   an xfail: `audit.audit_records_for` matches `json_each(explanation, '$.file_ids')`
   today (`src/privacy/audit.py:216-221`), which is the fix the plan's CONTRADICTION
   callout records as landed.
3. Thirteen tables refused a delete before P7 existed. P7's own two tables added two
   more, so the count on a P7 connection is fifteen. Both halves are asserted by name.
"""
from __future__ import annotations

import inspect
import json
import sqlite3

import pytest

from privacy.audit import AUDIT_FIELDS, AuditRecord, append_audit
from privacy.authorship import CONSENT_REVOKED, SUBSYSTEM
from privacy.gate import Gate
from privacy.policy import (
    REDACTED, UNSET_POLICY_VERSION, Policy, current_policy, grant_consent,
    policy_at, set_policy,
)
from privacy.revocation import (
    DERIVED_PROJECTIONS, NOT_DERIVED, RELEASED, DeleteDerivedRefused, DerivedScope,
    MissingRetractionLimit, PriorRelease, RevocationResult, ScopeNotDerived,
    UnratifiedResolution, delete_derived, revoke,
)
from privacy.vocabulary import AUDIT_OUTCOMES, DISPLAY_FACETS

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"
PLAN = "plan-1"
SCOPE = "Academics"

#: §8.4's obligation is the product's; the words are P13's. The test supplies them the
#: way P13 will, so nothing in `src/privacy/` has to hold a sentence.
RETRACTION_LIMIT = (
    "Revoking this policy stops future calls. It cannot retract the excerpts already "
    "sent to Acme, listed above."
)

#: The thirteen tables that already refused a delete before P7 created a table.
#: P1's `events`, P4's two, P5's `extraction_runs`, P3's `exclusion_verdicts`, and
#: P2's eight `bundle_*`. Counted from the substrate rather than remembered.
SUBSTRATE_GUARDED: frozenset[str] = frozenset({
    "events", "evidence", "text_units", "extraction_runs", "exclusion_verdicts",
    "bundle_accepted_group", "bundle_expectation", "bundle_extraction_output",
    "bundle_extraction_run", "bundle_file_entry", "bundle_learning_record",
    "bundle_manifest", "bundle_text_unit",
})

#: P7's own two, from `privacy.schema`. Both supersede-bearing records, and neither is
#: the release ledger. See `test_the_release_ledger_takes_no_before_delete_trigger`.
P7_GUARDED: frozenset[str] = frozenset({"classifications", "privacy_policies"})

_TYPED_DEFAULTS = {
    "audit_id": None,
    "release_id": "release-1",
    "policy_version": "policy-1",
    "plan_version": PLAN,
    "stage": "grouping",
    "outcome": RELEASED,
    "operation_mode": "cloud_assisted",
    "authorizing_policy": "policy-1",
    "file_sensitivity": "personal_non_sensitive",
    "excerpts_included": (("obs-key-1", "0-19"),),
    "redaction_applied": False,
    "redaction_manifest": (),
    "model": {"locality": "cloud", "model_id": "acme-large", "provider": "Acme"},
    "content_hashes": ("sha256:abc",),
    "content_hash": "sha256:abc",
    "prompt_fingerprint": "fp-1",
    "file_id": "file-1",
    "file_ids": ("file-1",),
    "group_id": None,
    "consent_request_id": None,
    "user_id": None,
    "observed_at": FIXED_CLOCK,
    "appended_at": FIXED_CLOCK,
}


def an_audit_record(**over) -> AuditRecord:
    """Built from `AUDIT_FIELDS`, never from a literal keyword list.

    Task 10 owns SPEC §7's nineteen names and asserts they match §7 name for name.
    Constructing from the published tuple means a field this task never reads can be
    respelled without breaking it, while a field it DOES read disappearing fails here,
    loudly, at the seam that cares.
    """
    missing = [name for name in AUDIT_FIELDS if name not in _TYPED_DEFAULTS]
    assert not missing, (
        f"AUDIT_FIELDS names {missing} and this test has no value for them; SPEC §7 "
        "moved and Task 15 needs a value, not a default")
    values = {name: _TYPED_DEFAULTS[name] for name in AUDIT_FIELDS}
    values.update(over)
    return AuditRecord(**values)


@pytest.fixture()
def in_force(p7_conn) -> Policy:
    """A real, live, cloud-assisted policy carrying one grant at `SCOPE`.

    Task 5's `revoke_consent` derives the next snapshot from the one handed in and
    refuses a superseded one inside the same transaction as the write, so a `Policy`
    built from literals in this file is `StalePolicyVersion` on arrival. The gate mints
    the version (SPEC §6); this fixture reads back what it minted.
    """
    version = set_policy(
        p7_conn,
        Policy(policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
               consent_grants=(), plan_version=PLAN, set_at=FIXED_CLOCK,
               redaction_settings={facet: REDACTED for facet in DISPLAY_FACETS},
               automatic_move_permissions={}),
        component_version=COMPONENT, user_id="joseph",
        reason="the user chose cloud-assisted mode")
    granted = grant_consent(p7_conn, policy_at(p7_conn, version), SCOPE,
                            "cloud_model", user_id="joseph",
                            component_version=COMPONENT, observed_at=FIXED_CLOCK)
    return policy_at(p7_conn, granted)


@pytest.fixture()
def released(p7_conn, in_force) -> int:
    """One prior release, in the log, under the policy about to be revoked."""
    return append_audit(p7_conn, an_audit_record(), author=SUBSYSTEM,
                        component_version=COMPONENT)


def go(conn, **over) -> RevocationResult:
    """Revoke from the snapshot in force, the way P13 will."""
    base = dict(user_id="joseph", component_version=COMPONENT, observed_at=LATER,
                retraction_limit=RETRACTION_LIMIT,
                files_in_scope=lambda scope: ("file-1",))
    base.update(over)
    return revoke(conn, current_policy(conn, plan_version=PLAN), SCOPE, **base)


# --- forward-only -----------------------------------------------------------

def test_effective_from_is_the_moment_of_revocation(p7_conn, released):
    # SPEC §8: "effective_from  future gate calls only."
    assert go(p7_conn).effective_from == LATER


def test_a_revocation_mints_a_new_policy_version(p7_conn, released):
    # The forward-only property is carried by a BINDING TERM, not by a flag. A release
    # minted under the old version still consumes against it (Task 12's ledger records
    # the version it was minted under), and a request made after this revocation is
    # decided against the new version, which is what makes Task 13's `policy_revoked`
    # reachable. Those two halves are asserted in Tasks 12 and 13 against signatures
    # this task cannot see; the seam that makes both true is asserted here.
    before = current_policy(p7_conn, plan_version=PLAN).policy_version
    go(p7_conn)
    row = p7_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ? ORDER BY event_id DESC",
        (CONSENT_REVOKED,)).fetchone()
    payload = json.loads(row["explanation"])
    assert payload["revoked_policy_version"] == before
    assert payload["policy_version"] != before
    assert payload["effective_from"] == LATER
    assert current_policy(p7_conn, plan_version=PLAN).policy_version == \
        payload["policy_version"]


def test_the_revoked_grant_is_gone_from_the_new_version(p7_conn, in_force):
    # Forward-only means the NEXT gate call is decided against a policy with no grant
    # at this scope, and the prior version stays loadable for §8.5 replay.
    assert in_force.consent_grants == ((SCOPE, "cloud_model"),)
    go(p7_conn)
    assert current_policy(p7_conn, plan_version=PLAN).consent_grants == ()
    assert policy_at(p7_conn, in_force.policy_version).consent_grants == \
        ((SCOPE, "cloud_model"),)


def test_the_revocation_is_authored_by_p7(p7_conn, released):
    # M8: the acting part authors, P1 writes.
    go(p7_conn)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CONSENT_REVOKED,)).fetchone()
    assert row["subsystem"] == "P7"
    assert row["user_id"] == "joseph"
    assert row["observed_at"] == LATER


def test_one_act_appends_one_consent_revoked_event(p7_conn, in_force):
    # Task 5's `revoke_consent` appends nothing; this is the one append. Two would put
    # one act in the log twice, and §8.4's `prior_releases` is read back out of it.
    go(p7_conn)
    assert p7_conn.execute(
        "SELECT count(*) c FROM events WHERE event_type = ?",
        (CONSENT_REVOKED,)).fetchone()["c"] == 1


# --- the prior-release list -------------------------------------------------

def test_prior_releases_name_model_provider_time_and_excerpts(p7_conn, released):
    # SPEC §8: "prior_releases[]  from the audit log: model, provider, when, which
    # excerpts." The audit log is what makes the retraction limit specific rather than
    # a generic disclaimer.
    assert go(p7_conn).prior_releases == (
        PriorRelease(model="acme-large", provider="Acme", when=FIXED_CLOCK,
                     excerpts=(("obs-key-1", "0-19"),)),
    )


def test_the_released_outcome_is_the_published_one_and_not_a_second_spelling(p7_conn):
    # §3.1: a closed vocabulary is named, not retyped. `AUDIT_OUTCOMES` is Task 2's
    # home for the three; `RELEASED` must be a member of it, not a fourth spelling.
    assert RELEASED in AUDIT_OUTCOMES


def test_a_denied_record_is_not_a_prior_release(p7_conn, released):
    append_audit(p7_conn, an_audit_record(outcome="denied", release_id=None),
                 author=SUBSYSTEM, component_version=COMPONENT)
    assert len(go(p7_conn).prior_releases) == 1


def test_prior_releases_come_from_the_audit_log_and_not_a_second_store(p7_conn,
                                                                      in_force):
    # Nothing else in P7 records what left the device, and §8.4 forbids a second copy
    # of the text: "excerpts_included stores (observation_key, span) pairs ... not a
    # second copy of the text."
    assert go(p7_conn).prior_releases == ()
    append_audit(p7_conn, an_audit_record(), author=SUBSYSTEM,
                 component_version=COMPONENT)
    assert len(go(p7_conn).prior_releases) == 1


def test_a_file_outside_the_scope_is_not_listed(p7_conn, released):
    # Open question 3 is held by the injection: P7 defines no corpus area, so a
    # resolver returning nothing produces an empty list rather than everything.
    assert go(p7_conn, files_in_scope=lambda scope: ()).prior_releases == ()


def test_files_in_scope_is_required_and_p7_defines_no_area():
    # OQ3 is held open by the SIGNATURE, not by a comment: a default resolver would be
    # P7 answering "what is a corpus area?" in code.
    parameters = inspect.signature(revoke).parameters
    for name in ("files_in_scope", "retraction_limit"):
        assert parameters[name].default is inspect.Parameter.empty
        assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY


def test_prior_releases_are_ordered_oldest_first(p7_conn, released):
    append_audit(p7_conn, an_audit_record(release_id="release-2", observed_at=LATER),
                 author=SUBSYSTEM, component_version=COMPONENT)
    assert [r.when for r in go(p7_conn).prior_releases] == [FIXED_CLOCK, LATER]


def test_prior_releases_are_not_filtered_to_the_revoked_policy_version(p7_conn,
                                                                      released):
    # §8.4's purpose is to tell the user what has already left the device. A list
    # narrowed to one policy version answers a different question, and every record
    # carries `policy_version` for a reader who wants the narrower one.
    append_audit(p7_conn, an_audit_record(release_id="release-2",
                                          policy_version="policy-99",
                                          authorizing_policy="policy-99"),
                 author=SUBSYSTEM, component_version=COMPONENT)
    assert len(go(p7_conn).prior_releases) == 2


def test_a_group_release_covering_a_file_in_scope_is_listed(p7_conn, in_force):
    # §8.4 requires the retraction limit be specific about what already left the
    # device. Excerpts from `file-1` that went to Acme inside a two-file prompt left
    # exactly as surely as excerpts sent alone, and a list that omits them tells the
    # user less than the truth about what revocation cannot take back.
    append_audit(p7_conn, an_audit_record(
        release_id="release-2", file_id=None, content_hash=None,
        file_ids=("file-1", "file-2"),
        content_hashes=("sha256:abc", "sha256:def")),
        author=SUBSYSTEM, component_version=COMPONENT)
    assert len(go(p7_conn).prior_releases) == 1


# --- the retraction limit ---------------------------------------------------

def test_the_retraction_limit_is_always_present(p7_conn, released):
    assert go(p7_conn).retraction_limit == RETRACTION_LIMIT


def test_an_empty_retraction_limit_is_refused(p7_conn, released):
    # §8.4 is a `must`: the product "must communicate that distinction clearly".
    # Presence is enforced; wording is P13's (SPEC Deferred).
    for empty in ("", "   "):
        with pytest.raises(MissingRetractionLimit):
            go(p7_conn, retraction_limit=empty)


def test_a_refused_retraction_limit_revokes_nothing(p7_conn, in_force):
    # The check runs BEFORE the policy write. A revocation that minted a version and
    # then refused would leave consent withdrawn with nothing said about what left.
    with pytest.raises(MissingRetractionLimit):
        go(p7_conn, retraction_limit="")
    assert current_policy(p7_conn, plan_version=PLAN).policy_version == \
        in_force.policy_version


def test_the_wording_is_the_callers_and_not_the_modules():
    # SPEC Deferred: "Consent-prompt and retraction-limit wording ... UX copy."
    import privacy.revocation as module
    held = [value for name, value in vars(module).items()
            if not name.startswith("__") and isinstance(value, str)]
    assert not [text for text in held if "retract" in text.lower()]


# --- the substrate proves Done-means 8, not P7's restraint -------------------

def test_deleting_an_audit_record_aborts(p7_conn, released):
    # P1's `events_no_delete`. Done-means 8: revoke "never deletes an audit record",
    # and the proof is the database refusing, not P7 declining to try.
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        p7_conn.execute("DELETE FROM events WHERE event_id = ?", (released,))


def test_updating_an_audit_record_aborts(p7_conn, released):
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        p7_conn.execute("UPDATE events SET subsystem = 'P8' WHERE event_id = ?",
                        (released,))


def test_the_append_only_triggers_cannot_be_dropped(p7_conn):
    # `db._deny_events_history_loss`, installed by `open_database` as a
    # `set_authorizer` hook: SQLITE_DROP_TRIGGER on the three names, and DROP TABLE
    # events, both return SQLITE_DENY.
    for statement in ("DROP TRIGGER events_no_delete",
                      "DROP TRIGGER events_no_update",
                      "DROP TRIGGER events_no_replace",
                      "DROP TABLE events"):
        with pytest.raises(sqlite3.DatabaseError, match="not authorized"):
            p7_conn.execute(statement)


def test_a_revocation_adds_a_row_and_removes_none(p7_conn, released):
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    go(p7_conn)
    after = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    assert after == before + 1
    assert p7_conn.execute("SELECT count(*) c FROM events WHERE event_id = ?",
                           (released,)).fetchone()["c"] == 1


# --- D3: the enumeration, and delete_derived refusing on both sides ----------

def test_delete_derived_refuses_an_enumerated_scope_and_names_i6():
    # D3 ratified the DIRECTION and built nothing: "No tombstone column is built until
    # P13 drives it." The surface exists; the semantics do not.
    with pytest.raises(UnratifiedResolution) as caught:
        delete_derived(DerivedScope("text_units", "text"))
    assert "I6" in str(caught.value)
    assert "D3" in str(caught.value)


def test_delete_derived_refuses_an_unenumerated_scope_by_name():
    # The point of a LITERAL enumeration: a table nobody listed is a red test, not a
    # silent miss. `ScopeNotDerived` is a different failure from "not built yet" and
    # the two must not be readable as one.
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("extraction_runs", "completeness"))
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("evidence", "reliability"))


def test_both_refusals_share_one_base_so_delete_derived_never_succeeds():
    for scope in (DerivedScope("text_units", "text"),
                  DerivedScope("nowhere", "nothing")):
        with pytest.raises(DeleteDerivedRefused):
            delete_derived(scope)


def test_events_is_named_as_outside_the_enumeration():
    # D3's first clause. `events` is not merely absent from DERIVED_PROJECTIONS; the
    # reason is written down, because absence and oversight look identical.
    assert "events" not in DERIVED_PROJECTIONS
    assert "events" in NOT_DERIVED
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("events", "explanation"))


def test_sensitivity_state_is_reclassified_and_never_deleted():
    # D2: the column is a PROJECTION of P7's authoritative record. The supported user
    # act is Task 16's reclassification, which supersedes; deleting a projection would
    # leave the authoritative record and its mirror disagreeing.
    assert "files" not in DERIVED_PROJECTIONS
    assert "files" in NOT_DERIVED
    with pytest.raises(ScopeNotDerived):
        delete_derived(DerivedScope("files", "sensitivity_state"))


def test_the_enumeration_names_only_live_tables_and_live_columns(p7_conn):
    # An enumeration that drifts from the schema is worse than none: it would refuse a
    # real column and accept a name that no longer exists.
    for table, columns in DERIVED_PROJECTIONS.items():
        live = {row[1] for row in p7_conn.execute(f"PRAGMA table_xinfo({table})")}
        assert live, table
        assert set(columns) <= live, (table, sorted(set(columns) - live))
    for table in NOT_DERIVED:
        assert {row[1] for row in p7_conn.execute(f"PRAGMA table_xinfo({table})")}


def test_the_enumerated_columns_are_where_ocr_text_actually_lives():
    # I6's own worked case: "The product cannot ship unable to forget a scanned
    # passport's OCR text." That text is `text_units.text` and `evidence.raw_value`
    # with M5's two context fields; nothing else in the schema holds it.
    assert DERIVED_PROJECTIONS["text_units"] == ("text",)
    assert DERIVED_PROJECTIONS["evidence"] == (
        "raw_value", "normalized_value", "context_before", "context_after")


def test_no_tombstone_column_was_built(p7_conn):
    # D3's second clause, and the whole reason it is a clause:
    # `files.sensitivity_state` spent this project as a column nothing wrote and
    # produced a second wrong value one column away. A migration later is cheaper.
    for table in DERIVED_PROJECTIONS:
        columns = {row[1] for row in p7_conn.execute(f"PRAGMA table_xinfo({table})")}
        for token in ("tombstone", "tombstoned", "deleted", "deleted_at",
                      "redacted_at", "forgotten"):
            assert token not in columns, (table, token)


def _delete_guarded(conn) -> set[str]:
    return {row["tbl_name"] for row in conn.execute(
        "SELECT tbl_name, sql FROM sqlite_master WHERE type = 'trigger'")
        if "BEFORE DELETE" in (row["sql"] or "")}


def test_thirteen_substrate_tables_already_refuse_a_delete(p7_conn):
    # The substrate D3 lands on top of, counted rather than remembered: events,
    # evidence, text_units, extraction_runs, exclusion_verdicts and P2's eight
    # bundle_* tables. "Deletion later is always available; un-deletion never is" is a
    # posture the schema already holds.
    from eval_harness.store import create_eval_schema
    from scan_agent.schema import create_scan_schema
    create_scan_schema(p7_conn)
    create_eval_schema(p7_conn)
    guarded = _delete_guarded(p7_conn)
    assert len(SUBSTRATE_GUARDED) == 13
    assert SUBSTRATE_GUARDED <= guarded


def test_the_only_additions_are_p7s_own_two_supersede_bearing_tables(p7_conn):
    # PLAN-PREAMBLE §3.11 counts thirteen on a P7 connection. Tasks 4 and 5 create two
    # tables of their own that refuse a delete, so the live count is fifteen. Both the
    # substrate thirteen and P7's two are asserted BY NAME, so a fourteenth table
    # arriving from anywhere still fails here. Reported, not absorbed.
    from eval_harness.store import create_eval_schema
    from scan_agent.schema import create_scan_schema
    create_scan_schema(p7_conn)
    create_eval_schema(p7_conn)
    assert _delete_guarded(p7_conn) == SUBSTRATE_GUARDED | P7_GUARDED
    assert len(SUBSTRATE_GUARDED | P7_GUARDED) == 15


def test_the_release_ledger_takes_no_before_delete_trigger(p7_conn):
    # §3.11's load-bearing half: "The release ledger is a capability record, not a
    # provenance record." §8.2's R6 binds `events`, and P7 does not extend it by
    # imitation.
    assert "release_ledger" not in _delete_guarded(p7_conn)


def test_p7_creates_no_trigger_of_its_own_on_events(p7_conn):
    # P1 owns R6. A second set of triggers under a second set of names is the
    # duplication that has cost this project most.
    names = {row["name"] for row in p7_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'trigger' "
        "AND tbl_name = 'events'")}
    assert names == {"events_no_update", "events_no_delete", "events_no_replace"}


# --- the facade (D13 kept CUT 4) --------------------------------------------

def test_the_gate_publishes_revoke_and_delete_derived(p7_conn):
    # SPEC §8 publishes both on the facade. D13 kept CUT 4, so this is certain rather
    # than provisional. `Gate` published exactly one public method before this task.
    published = {name for name in vars(Gate) if not name.startswith("_")}
    assert published == {"release", "revoke", "delete_derived"}


def test_gate_revoke_delegates_and_carries_constructor_state(p7_conn, in_force,
                                                             released):
    # Every parameter `revocation.revoke` needs beyond the scope and the wording is
    # already constructor state -- `files_in_scope` was held for exactly this since
    # Task 11 -- so `Gate.revoke` invents nothing and reads nothing twice.
    gate = a_gate(p7_conn)
    result = gate.revoke(SCOPE, retraction_limit=RETRACTION_LIMIT)
    assert result.effective_from == LATER
    assert result.retraction_limit == RETRACTION_LIMIT
    assert result.prior_releases == (
        PriorRelease(model="acme-large", provider="Acme", when=FIXED_CLOCK,
                     excerpts=(("obs-key-1", "0-19"),)),
    )
    assert current_policy(p7_conn, plan_version=PLAN).consent_grants == ()


def test_gate_revoke_refuses_when_no_policy_is_in_force(p7_conn):
    from privacy.release import NoPolicyInForce

    with pytest.raises(NoPolicyInForce):
        a_gate(p7_conn).revoke(SCOPE, retraction_limit=RETRACTION_LIMIT)


def test_gate_delete_derived_refuses_on_both_sides_too(p7_conn):
    gate = a_gate(p7_conn)
    with pytest.raises(UnratifiedResolution):
        gate.delete_derived(DerivedScope("evidence", "raw_value"))
    with pytest.raises(ScopeNotDerived):
        gate.delete_derived(DerivedScope("events", "explanation"))


def test_gate_delete_derived_writes_nothing(p7_conn):
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    with pytest.raises(DeleteDerivedRefused):
        a_gate(p7_conn).delete_derived(DerivedScope("text_units", "text"))
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before


def a_gate(conn) -> Gate:
    """The twelve keyword-only constructor parameters, none of them guessed.

    Task 20 owns pinning them; this file constructs one only to prove the two new
    methods are on the facade and delegate. Nothing here reaches `release`, so the
    injections `release` needs are the identity-shaped ones.
    """
    return Gate(conn, store=None, plan_version=PLAN, classifier=lambda text: (),
                transform=lambda value: value, unclassified_permits_local=False,
                scope_for=lambda file_id: SCOPE,
                files_in_scope=lambda scope: ("file-1",),
                component_version=COMPONENT, now=lambda: LATER, user_id="joseph")
