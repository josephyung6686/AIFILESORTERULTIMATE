"""§8.4's four operation modes, its consent options, its five configurable redaction
facets, and the `policy_version` the gate mints.

W1 is NOT here. This file never asserts what the resolved default is, because
`policy.py` holds no default: `current_policy` returns `None` when nothing has been
set and Task 6 is what turns that into §8.4's local-first floor. A default living in
two modules is a default that can disagree with itself, and the one it would disagree
about is whether content leaves the device.
"""
from __future__ import annotations

import inspect
import json
import sqlite3

import pytest

from database_agent.events import MalformedEvent
from database_agent.supersede import SUPERSEDE_COLUMNS

from extractors.dispatch import extract

from privacy.authorship import CONSENT_GRANTED, POLICY_SET, SUBSYSTEM
from privacy.classification_store import ClassificationStore
from privacy.policy import (
    NO_MODEL_USE,
    REDACTED,
    REDACTION_VALUES,
    SHOWN,
    UNSET_POLICY_VERSION,
    AmbiguousCurrentPolicy,
    CallerSuppliedPolicyVersion,
    Policy,
    StalePolicyVersion,
    TranscriptionAuthorization,
    UnknownPolicyVersion,
    current_policy,
    grant_consent,
    policy_at,
    revoke_consent,
    set_policy,
    transcription_authorized_for,
)
from privacy.schema import POLICIES_TABLE
import privacy.vocabulary as vocabulary
from privacy.vocabulary import (
    CONSENT_OPTIONS,
    DISPLAY_FACETS,
    OPERATION_MODES,
    OutOfVocabulary,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"
PLAN = "plan-1"

ALL_REDACTED = {facet: REDACTED for facet in DISPLAY_FACETS}


def a_policy(**over) -> Policy:
    base = dict(policy_version=UNSET_POLICY_VERSION, operation_mode="local_model",
                consent_grants=(), redaction_settings=dict(ALL_REDACTED),
                automatic_move_permissions={}, plan_version=PLAN, set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


def store(conn, **over) -> str:
    return set_policy(conn, a_policy(**over), component_version=COMPONENT,
                      user_id="joseph", reason="the user chose local-model mode")


# --- the table -------------------------------------------------------------

def test_the_policy_table_carries_p1s_three_supersede_columns(p7_conn):
    columns = {row["name"] for row in p7_conn.execute(
        f"PRAGMA table_info({POLICIES_TABLE})")}
    assert set(SUPERSEDE_COLUMNS) <= columns


def test_a_policy_row_cannot_be_deleted(p7_conn):
    version = store(p7_conn)
    with pytest.raises(sqlite3.IntegrityError, match="superseded"):
        p7_conn.execute(f"DELETE FROM {POLICIES_TABLE} WHERE policy_version = ?",
                        (version,))


def test_a_policy_row_cannot_be_overwritten(p7_conn):
    # §8.8's diff needs both sides. A mutated policy row is a diff with one side.
    version = store(p7_conn)
    with pytest.raises(sqlite3.IntegrityError, match="superseded"):
        p7_conn.execute(
            f"UPDATE {POLICIES_TABLE} SET operation_mode = ? WHERE policy_version = ?",
            ("cloud_assisted", version))


# --- the gate mints the version --------------------------------------------

def test_the_gate_mints_the_policy_version(p7_conn):
    # SPEC §6: "the gate owns the policy, so the caller does not supply this value,
    # it echoes it."
    version = store(p7_conn)
    assert isinstance(version, str) and version != UNSET_POLICY_VERSION


def test_a_caller_supplied_policy_version_is_refused(p7_conn):
    with pytest.raises(CallerSuppliedPolicyVersion):
        set_policy(p7_conn, a_policy(policy_version="policy-i-picked"),
                   component_version=COMPONENT, user_id="joseph", reason="because")


def test_two_policies_never_share_a_version(p7_conn):
    first = store(p7_conn)
    second = store(p7_conn, operation_mode="offline", set_at=LATER)
    assert first != second


def test_policy_at_returns_the_policy_that_was_set(p7_conn):
    version = store(p7_conn, operation_mode="offline")
    loaded = policy_at(p7_conn, version)
    assert loaded.policy_version == version
    assert loaded.operation_mode == "offline"
    assert loaded.redaction_settings == ALL_REDACTED
    assert loaded.plan_version == PLAN


def test_an_unknown_policy_version_raises(p7_conn):
    with pytest.raises(UnknownPolicyVersion):
        policy_at(p7_conn, "policy-never-minted")


def test_current_policy_is_none_before_anything_is_set(p7_conn):
    # A6. "No policy has been set" is a fact, and it is Task 6's input, not an
    # occasion for `policy.py` to invent one.
    assert current_policy(p7_conn, plan_version=PLAN) is None


# --- supersede, never mutate -----------------------------------------------

def test_a_policy_change_supersedes_the_prior_policy(p7_conn):
    first = store(p7_conn)
    second = store(p7_conn, operation_mode="offline", set_at=LATER)
    row = p7_conn.execute(
        f"SELECT * FROM {POLICIES_TABLE} WHERE policy_version = ?", (first,)).fetchone()
    assert row["superseded_by"] == second
    assert row["supersede_reason"]
    assert current_policy(p7_conn, plan_version=PLAN).policy_version == second


def test_the_prior_policy_remains_readable(p7_conn):
    first = store(p7_conn)
    store(p7_conn, operation_mode="offline", set_at=LATER)
    # §8.5 replay reproduces "the policy in force at each call", so a superseded
    # policy version must stay loadable by name forever.
    assert policy_at(p7_conn, first).operation_mode == "local_model"


def test_a_policy_change_appends_policy_set_once(p7_conn):
    store(p7_conn)
    rows = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                           (POLICY_SET,)).fetchall()
    assert len(rows) == 1
    assert rows[0]["subsystem"] == SUBSYSTEM == "P7"
    assert rows[0]["user_id"] == "joseph"


def test_the_policy_set_explanation_carries_a_diffable_policy(p7_conn):
    # §8.8 requires a privacy-policy change to appear as a first-class diff line.
    # The explanation carries both sides and the reason, so the diff is a read of
    # the log rather than a recomputation from two snapshots.
    store(p7_conn)
    second = store(p7_conn, operation_mode="offline", set_at=LATER,
                   consent_grants=(("Academics", "cloud_model"),))
    payload = json.loads(p7_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ? ORDER BY event_id DESC",
        (POLICY_SET,)).fetchone()["explanation"])
    assert payload["policy_version"] == second
    assert payload["operation_mode"] == "offline"
    assert payload["superseded_policy_version"]
    assert payload["consent_grants"] == [["Academics", "cloud_model"]]
    assert payload["reason"]


def test_two_live_policies_at_one_plan_version_raise_rather_than_pick(p7_conn):
    store(p7_conn)
    p7_conn.execute(
        f"INSERT INTO {POLICIES_TABLE} (policy_version, plan_version, operation_mode,"
        " consent_grants, redaction_settings, automatic_move_permissions, set_at)"
        " VALUES (?,?,?,?,?,?,?)",
        ("policy-smuggled", PLAN, "cloud_assisted", "[]", "{}", "{}", LATER))
    with pytest.raises(AmbiguousCurrentPolicy):
        current_policy(p7_conn, plan_version=PLAN)


# --- plan scoping ----------------------------------------------------------

def test_policy_is_plan_scoped(p7_conn):
    store(p7_conn)
    assert current_policy(p7_conn, plan_version="plan-2") is None


def test_each_plan_version_carries_its_own_current_policy(p7_conn):
    store(p7_conn, operation_mode="offline")
    store(p7_conn, operation_mode="local_model", plan_version="plan-2", set_at=LATER)
    assert current_policy(p7_conn, plan_version=PLAN).operation_mode == "offline"
    assert current_policy(p7_conn, plan_version="plan-2").operation_mode == "local_model"


def test_classifications_are_not_plan_scoped(p7_conn):
    # §8.8: "The evidence database remains shared across plan versions." Asserted by
    # signature, so a later plan_version parameter on the store is a failing test.
    assert "plan_version" not in inspect.signature(ClassificationStore.current).parameters
    assert "plan_version" in inspect.signature(current_policy).parameters


# --- the four modes --------------------------------------------------------

def test_policy_holds_no_second_list_of_modes(p7_conn):
    import privacy.policy as module
    held = [value for name, value in vars(module).items()
            if not name.startswith("_") and isinstance(value, str)]
    assert not [text for text in held if text in OPERATION_MODES]


def test_every_mode_in_the_vocabulary_is_settable(p7_conn):
    for index, mode in enumerate(OPERATION_MODES):
        version = store(p7_conn, operation_mode=mode, plan_version=f"plan-{index}")
        assert policy_at(p7_conn, version).operation_mode == mode


def test_a_mode_outside_the_vocabulary_is_a_load_error(p7_conn):
    # SPEC §1: "A value outside this set is a load error, not a fallback."
    with pytest.raises(OutOfVocabulary):
        a_policy(operation_mode="mostly_offline")


# --- redaction settings ----------------------------------------------------

def test_the_two_redaction_values_are_the_specs_own(p7_conn):
    # SPEC §10: "names | previews | thumbnails | ocr_text | location_data
    #            each shown | redacted".
    assert REDACTION_VALUES == ("shown", "redacted") == (SHOWN, REDACTED)


def test_policy_re_exports_task_2s_values_and_defines_none_of_its_own(p7_conn):
    # A7, resolved: `privacy.vocabulary` owns the pair and `policy.py` re-exports it.
    # `is`, not `==`: a second tuple with the same two strings passes equality and is
    # exactly the second home the re-export exists to remove. Before this, the pair
    # had three homes -- REDACTION_VALUES here, REDACTION_VALUES in Task 18,
    # REDACTION_VALUES in a third section.
    assert SHOWN is vocabulary.SHOWN
    assert REDACTED is vocabulary.REDACTED
    assert REDACTION_VALUES is vocabulary.REDACTION_VALUES


def test_an_unknown_facet_is_a_load_error(p7_conn):
    with pytest.raises(OutOfVocabulary):
        a_policy(redaction_settings={"filenames": REDACTED})


def test_an_unknown_redaction_value_is_a_load_error(p7_conn):
    with pytest.raises(OutOfVocabulary):
        a_policy(redaction_settings={DISPLAY_FACETS[0]: "blurred"})


def test_a_partial_redaction_map_is_accepted_and_left_to_task_6(p7_conn):
    # The migrated-from-nothing case. Refusing it here would make W1 unreachable:
    # Task 6's job is to fill an absent facet with its more redacting value, and it
    # cannot fill what `Policy` refuses to hold.
    partial = a_policy(redaction_settings={DISPLAY_FACETS[0]: SHOWN})
    assert set(partial.redaction_settings) == {DISPLAY_FACETS[0]}


def test_the_five_facets_are_task_2s_and_policy_names_no_sixth(p7_conn):
    assert len(DISPLAY_FACETS) == 5
    version = store(p7_conn, redaction_settings=dict(ALL_REDACTED))
    assert set(policy_at(p7_conn, version).redaction_settings) == set(DISPLAY_FACETS)


# --- consent grants --------------------------------------------------------

def test_grant_consent_mints_a_new_version_carrying_the_grant(p7_conn):
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    second = grant_consent(p7_conn, first, "Academics", "cloud_model",
                           user_id="joseph", component_version=COMPONENT,
                           observed_at=LATER)
    assert second != first.policy_version
    assert policy_at(p7_conn, second).consent_grants == (("Academics", "cloud_model"),)
    # The grant is why the version changes: a release minted under `first` must not
    # survive into a policy it was not authorized under (B2's binding tuple).
    assert policy_at(p7_conn, first.policy_version).consent_grants == ()


def test_grant_consent_appends_consent_granted_once_and_no_policy_set(p7_conn):
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    grant_consent(p7_conn, first, "Academics", "cloud_model", user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    granted = p7_conn.execute("SELECT count(*) c FROM events WHERE event_type = ?",
                              (CONSENT_GRANTED,)).fetchone()["c"]
    policies = p7_conn.execute("SELECT count(*) c FROM events WHERE event_type = ?",
                               (POLICY_SET,)).fetchone()["c"]
    assert (granted, policies) == (1, 1)      # the 1 policy_set is the initial set


def test_an_option_outside_the_four_is_a_load_error(p7_conn):
    first = policy_at(p7_conn, store(p7_conn))
    with pytest.raises(OutOfVocabulary):
        grant_consent(p7_conn, first, "Academics", "cloud_model_but_only_tuesdays",
                      user_id="joseph", component_version=COMPONENT, observed_at=LATER)


def test_the_four_options_are_84s_own(p7_conn):
    # §8.4: the user should "choose whether to allow a local model, a cloud model, a
    # redacted prompt, or no model use."
    assert CONSENT_OPTIONS == ("local_model", "cloud_model", "redacted_prompt",
                               "no_model_use")


def test_revoke_consent_removes_the_grant_and_mints_a_version(p7_conn):
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    granted = policy_at(p7_conn, grant_consent(
        p7_conn, first, "Academics", "cloud_model", user_id="joseph",
        component_version=COMPONENT, observed_at=LATER))
    revoked = revoke_consent(p7_conn, granted, "Academics", user_id="joseph",
                             component_version=COMPONENT, observed_at=LATER)
    assert policy_at(p7_conn, revoked).consent_grants == ()
    assert policy_at(p7_conn, granted.policy_version).consent_grants == \
        (("Academics", "cloud_model"),)


def test_revoke_consent_appends_no_event(p7_conn):
    # Sibling Task 15 pins this: `consent_revoked` is appended once, by `revoke`,
    # which is where §8.4's prior-release list and retraction limit are assembled.
    # Two appends would put one act in the log twice and §8.4's `prior_releases` is
    # read back out of that log.
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    revoke_consent(p7_conn, first, "Academics", user_id="joseph",
                   component_version=COMPONENT, observed_at=LATER)
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before


def test_the_scope_is_opaque_and_p7_defines_no_corpus_area(p7_conn):
    # SPEC Open question 3, held: "Consent grants cannot be scoped until this is
    # named." A scan root, a frozen node, an accepted group and a domain are all
    # accepted, unparsed, because P7 has no basis to prefer one.
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    for scope in ("/Users/j/Corpus", "node-17", "group-4", "Finance"):
        first = policy_at(p7_conn, grant_consent(
            p7_conn, first, scope, "cloud_model", user_id="joseph",
            component_version=COMPONENT, observed_at=LATER))
    assert [grant[0] for grant in first.consent_grants] == \
        ["/Users/j/Corpus", "node-17", "group-4", "Finance"]


# --- a stale snapshot is refused, never merged -----------------------------

def test_a_grant_derived_from_a_stale_snapshot_is_refused(p7_conn):
    # One policy version is the WHOLE snapshot, so a writer that derived its
    # revision from a superseded snapshot would silently drop every change made
    # since it read. The version is the concurrency token: it has to still be the
    # live one at the moment of the write.
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    grant_consent(p7_conn, first, "Academics", "cloud_model", user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    with pytest.raises(StalePolicyVersion):
        grant_consent(p7_conn, first, "Finance", "cloud_model", user_id="joseph",
                      component_version=COMPONENT, observed_at=LATER)
    assert current_policy(p7_conn, plan_version=PLAN).consent_grants == \
        (("Academics", "cloud_model"),)


def test_a_revoke_derived_from_a_stale_snapshot_cannot_resurrect_a_grant(p7_conn):
    # The worst case of the same defect, and the reason it is a refusal rather
    # than a merge: revoking Academics leaves a snapshot holding Finance, and
    # revoking Finance from the ACADEMICS+FINANCE snapshot would mint a live
    # policy carrying Academics again -- a withdrawn consent back in force.
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    with_academics = policy_at(p7_conn, grant_consent(
        p7_conn, first, "Academics", "cloud_model", user_id="joseph",
        component_version=COMPONENT, observed_at=LATER))
    with_both = policy_at(p7_conn, grant_consent(
        p7_conn, with_academics, "Finance", "cloud_model", user_id="joseph",
        component_version=COMPONENT, observed_at=LATER))
    revoke_consent(p7_conn, with_both, "Academics", user_id="joseph",
                   component_version=COMPONENT, observed_at=LATER)
    with pytest.raises(StalePolicyVersion):
        revoke_consent(p7_conn, with_both, "Finance", user_id="joseph",
                       component_version=COMPONENT, observed_at=LATER)
    live = current_policy(p7_conn, plan_version=PLAN)
    assert [scope for scope, _ in live.consent_grants] == ["Finance"]


def test_two_grants_each_read_from_the_policy_in_force_both_land(p7_conn):
    # The refusal is not a lock: re-reading is all a second writer has to do.
    store(p7_conn, operation_mode="cloud_assisted")
    grant_consent(p7_conn, current_policy(p7_conn, plan_version=PLAN),
                  "Academics", "cloud_model", user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    second = grant_consent(p7_conn, current_policy(p7_conn, plan_version=PLAN),
                           "Finance", "local_model", user_id="joseph",
                           component_version=COMPONENT, observed_at=LATER)
    assert dict(policy_at(p7_conn, second).consent_grants) == \
        {"Academics": "cloud_model", "Finance": "local_model"}


# --- one act, one commit ---------------------------------------------------

def test_a_failed_policy_set_event_leaves_no_policy_row(p7_conn):
    # §8.2 reconstructs a transition from the log. A committed policy row whose
    # `policy_set` event never landed is a transition the log cannot account for,
    # so the row and its event share one commit.
    with pytest.raises(MalformedEvent):
        set_policy(p7_conn, a_policy(), component_version="", user_id="joseph",
                   reason="the user chose local-model mode")
    assert current_policy(p7_conn, plan_version=PLAN) is None
    assert p7_conn.execute(
        f"SELECT count(*) c FROM {POLICIES_TABLE}").fetchone()["c"] == 0
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == 0


def test_a_failed_consent_granted_event_leaves_the_prior_policy_in_force(p7_conn):
    # And the rollback restores the PRIOR row too: a supersede that outlived the
    # act that caused it would leave the plan with no live policy at all.
    stored = store(p7_conn, operation_mode="cloud_assisted")
    with pytest.raises(MalformedEvent):
        grant_consent(p7_conn, policy_at(p7_conn, stored), "Academics",
                      "cloud_model", user_id="joseph", component_version="",
                      observed_at=LATER)
    live = current_policy(p7_conn, plan_version=PLAN)
    assert live.policy_version == stored
    assert live.consent_grants == ()
    assert p7_conn.execute(
        f"SELECT count(*) c FROM {POLICIES_TABLE}").fetchone()["c"] == 1
    for event_type, expected in ((POLICY_SET, 1), (CONSENT_GRANTED, 0)):
        assert p7_conn.execute(
            "SELECT count(*) c FROM events WHERE event_type = ?",
            (event_type,)).fetchone()["c"] == expected


# --- the P5 back-edge (M10) ------------------------------------------------

def test_the_adapter_satisfies_p5s_zero_argument_predicate(p7_conn):
    predicate = transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)
    assert isinstance(predicate, TranscriptionAuthorization)
    assert inspect.signature(predicate).parameters == {}
    assert predicate() is False


def test_the_adapter_carries_the_scope_p5_cannot_pass(p7_conn):
    # The mismatch is REPORTED, not patched: P5's call site is
    # `transcription_authorized()` with no arguments, so the scope has to live on
    # the object. A lambda would hide it.
    predicate = transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)
    assert predicate.scope == "Academics"


def test_p5s_call_site_takes_no_scope(p7_conn):
    # Asserted against P5 as shipped, so the day P5's signature widens this test
    # fails and the adapter can be deleted rather than quietly kept.
    parameter = inspect.signature(extract).parameters["transcription_authorized"]
    assert "Callable[[], bool]" in str(parameter.annotation)


def test_an_explicit_grant_authorizes_and_absence_does_not(p7_conn):
    # §2.9: speech-to-text runs "only under an explicit privacy and compute policy".
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    assert transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)() \
        is False
    grant_consent(p7_conn, first, "Academics", "local_model", user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    assert transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)() \
        is True
    assert transcription_authorized_for(p7_conn, "Finance", plan_version=PLAN)() \
        is False


def test_no_model_use_does_not_authorize(p7_conn):
    assert NO_MODEL_USE in CONSENT_OPTIONS
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    grant_consent(p7_conn, first, "Academics", NO_MODEL_USE, user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    assert transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)() \
        is False


def test_the_adapter_reads_the_policy_in_force_and_caches_nothing(p7_conn):
    predicate = transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)
    assert predicate() is False
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    grant_consent(p7_conn, first, "Academics", "cloud_model", user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    assert predicate() is True
