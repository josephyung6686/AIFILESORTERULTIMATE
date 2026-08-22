# tests/p7/test_p7_defaults.py
"""Done-means 12 — §8.4's local-first `must` (W1), and the negative half that matters
more than the positive one.

The positive half: with no user configuration present, the resolved mode is one of
the two under which no content leaves the device, and every configurable redaction
setting resolves to its more redacting value.

The negative half: no code path, build flag, packaged configuration file or first-run
flow produces a starting mode of `hybrid` or `cloud_assisted`. Asserted by calling
the resolver over every reachable stored state and by walking the package's
module-level namespaces at run time -- not by grepping source text, because both mode
names appear legitimately in `vocabulary.py`, in docstrings and in denial messages,
and a text scan would either pass vacuously or fail on a comment.

What this file must NOT assert: which of `offline` and `local_model` ships. That is
SPEC Open question 11 and P7 will not guess it.
"""
from __future__ import annotations

import importlib
import pkgutil

import pytest

import privacy
import privacy.vocabulary as vocab
from privacy.defaults import (
    LOCAL_FIRST_MODES,
    LOCAL_MODEL,
    MORE_REDACTING,
    OFFLINE,
    DefaultPostureViolation,
    assert_local_first,
    effective_policy,
    resolve_default_policy,
)
from privacy.policy import (
    REDACTED,
    SHOWN,
    UNSET_POLICY_VERSION,
    Policy,
    set_policy,
)
from privacy.vocabulary import DISPLAY_FACETS, OPERATION_MODES, OutOfVocabulary

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
COMPONENT = "0.1.0"
PLAN = "plan-1"

#: The two names §8.4 forbids as a DEFAULT. Both remain modes a user may choose.
CLOUD_MODES = ("hybrid", "cloud_assisted")


def resolved(stored=None, *, install_mode=OFFLINE) -> Policy:
    return resolve_default_policy(stored, install_mode=install_mode,
                                  plan_version=PLAN, set_at=FIXED_CLOCK)


def a_stored_policy(**over) -> Policy:
    base = dict(policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
                consent_grants=(("Academics", "cloud_model"),),
                redaction_settings={facet: REDACTED for facet in DISPLAY_FACETS},
                automatic_move_permissions={"Academics": True}, plan_version=PLAN,
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


# --- the two modes under which nothing leaves the device --------------------

def test_the_two_local_first_modes_are_the_two_that_send_nothing(p7_conn):
    # §8.4: "Fully offline mode: No content leaves the device; only local rules and
    # local models may run." / "Local-model mode: Local extraction plus a
    # user-installed local LLM for eligible dossiers." The other two both permit a
    # cloud model, which is the posture §8.4 forbids as a DEFAULT.
    assert LOCAL_FIRST_MODES == (OFFLINE, LOCAL_MODEL) == ("offline", "local_model")
    assert set(LOCAL_FIRST_MODES) < set(OPERATION_MODES)
    assert set(OPERATION_MODES) - set(LOCAL_FIRST_MODES) == set(CLOUD_MODES)


def test_the_local_mode_names_are_task_2s_and_not_a_second_spelling(p7_conn):
    for mode in LOCAL_FIRST_MODES:
        assert vocab.check_mode(mode) == mode


def test_more_redacting_covers_every_facet(p7_conn):
    # §8.4's five configurable facets: "names, previews, thumbnails, OCR text, or
    # location data".
    assert set(MORE_REDACTING) == set(DISPLAY_FACETS)
    assert set(MORE_REDACTING.values()) == {REDACTED}
    assert SHOWN not in MORE_REDACTING.values()


# --- fresh install ----------------------------------------------------------

def test_a_fresh_install_resolves_to_the_named_local_mode(p7_conn):
    assert resolved(None, install_mode=OFFLINE).operation_mode == OFFLINE
    assert resolved(None, install_mode=LOCAL_MODEL).operation_mode == LOCAL_MODEL


def test_a_fresh_install_redacts_every_facet(p7_conn):
    assert resolved(None).redaction_settings == dict(MORE_REDACTING)


def test_a_fresh_install_grants_nothing_and_permits_no_automatic_move(p7_conn):
    # §8.4: protected material "should not be moved automatically without a user
    # policy that explicitly permits it." An empty map permits nothing explicitly.
    fresh = resolved(None)
    assert fresh.consent_grants == ()
    assert fresh.automatic_move_permissions == {}


def test_the_resolved_default_is_unpersisted(p7_conn):
    # A default nobody chose has no policy version. `set_policy` is what mints one,
    # and it is a user act with a reason (§8.8's meaningful diff).
    assert resolved(None).policy_version == UNSET_POLICY_VERSION


def test_the_resolved_default_passes_its_own_assertion(p7_conn):
    for mode in LOCAL_FIRST_MODES:
        assert_local_first(resolved(None, install_mode=mode))


# --- migrated from nothing --------------------------------------------------

def test_a_migrated_install_fills_every_absent_facet(p7_conn):
    # A policy row exists with a mode and no redaction settings -- the state a build
    # that predates §8.4's facets leaves behind.
    migrated = a_stored_policy(operation_mode=LOCAL_MODEL, redaction_settings={})
    assert resolved(migrated).redaction_settings == dict(MORE_REDACTING)


def test_a_partial_facet_map_is_completed_and_the_users_setting_survives(p7_conn):
    # Filling an absent facet is the default; overwriting a facet the user set would
    # be the product changing a choice behind their back (§8.8).
    partial = a_stored_policy(operation_mode=LOCAL_MODEL,
                              redaction_settings={DISPLAY_FACETS[0]: SHOWN})
    filled = resolved(partial).redaction_settings
    assert filled[DISPLAY_FACETS[0]] == SHOWN
    assert all(filled[facet] == REDACTED for facet in DISPLAY_FACETS[1:])


def test_every_reachable_stored_state_resolves_to_a_complete_facet_map(p7_conn):
    for stored in (None,
                   a_stored_policy(redaction_settings={}),
                   a_stored_policy(redaction_settings={DISPLAY_FACETS[2]: REDACTED}),
                   a_stored_policy()):
        assert set(resolved(stored).redaction_settings) == set(DISPLAY_FACETS)


# --- the floor is on the INSTALL, not on the user's choice ------------------

def test_a_user_chosen_cloud_mode_is_returned_unchanged(p7_conn):
    # §8.4: "Either remains a legitimate mode the user may choose; neither may be
    # what they find on install." W1 binds the default, never the choice.
    chosen = a_stored_policy(operation_mode="cloud_assisted")
    assert resolved(chosen).operation_mode == "cloud_assisted"
    assert resolved(chosen).consent_grants == (("Academics", "cloud_model"),)


def test_the_two_questions_are_different_and_the_test_proves_it(p7_conn):
    # `resolve_default_policy` answers "what is in force". `assert_local_first`
    # answers "is this a posture a user may arrive at without choosing it".
    # Collapsing them would either forbid a mode §8.4 offers or ship one it forbids.
    chosen = a_stored_policy(operation_mode="hybrid")
    assert resolved(chosen).operation_mode == "hybrid"
    with pytest.raises(DefaultPostureViolation):
        assert_local_first(resolved(chosen))


# --- the negative half ------------------------------------------------------

@pytest.mark.parametrize("mode", CLOUD_MODES)
def test_a_cloud_mode_cannot_be_the_install_mode(p7_conn, mode):
    with pytest.raises(DefaultPostureViolation):
        resolved(None, install_mode=mode)


@pytest.mark.parametrize("mode", CLOUD_MODES)
def test_a_cloud_mode_cannot_be_the_install_mode_over_a_stored_policy(p7_conn, mode):
    with pytest.raises(DefaultPostureViolation):
        resolved(a_stored_policy(redaction_settings={}), install_mode=mode)


def test_an_unknown_install_mode_is_a_load_error_and_not_a_posture_violation(p7_conn):
    # Two different failures. "A value outside this set is a load error, not a
    # fallback" is Task 2's; being a known mode that §8.4 forbids as a default is
    # W1's. A caller that catches one must not silently absorb the other.
    with pytest.raises(OutOfVocabulary):
        resolved(None, install_mode="mostly_offline")


def test_assert_local_first_rejects_a_shown_facet(p7_conn):
    # Data-minimizing is the second half of the same `must`, and §8.4's own example
    # settles the direction: the aggregate is safe to show, the expansion is not.
    almost = resolved(None)
    from dataclasses import replace
    loosened = replace(almost, redaction_settings={
        **almost.redaction_settings, DISPLAY_FACETS[0]: SHOWN})
    with pytest.raises(DefaultPostureViolation):
        assert_local_first(loosened)


def test_assert_local_first_rejects_an_incomplete_facet_map(p7_conn):
    from dataclasses import replace
    with pytest.raises(DefaultPostureViolation):
        assert_local_first(replace(resolved(None), redaction_settings={}))


def test_no_module_under_privacy_names_a_cloud_mode_at_module_level(p7_conn):
    # Runtime introspection of every module's namespace, the way
    # `tests/p3/test_p3_no_invention.py` established. Objects that ARE
    # `vocabulary.py`'s own are skipped by IDENTITY, not by name, so a legitimate
    # re-export of `OPERATION_MODES` or `MODE_SEMANTICS` is not a false positive
    # while a second private copy of either is a failure.
    vocabulary_objects = {id(value) for value in vars(vocab).values()}
    forbidden = set(CLOUD_MODES)
    offenders: list[str] = []
    for info in pkgutil.iter_modules(privacy.__path__):
        module = importlib.import_module(f"privacy.{info.name}")
        if module is vocab:
            continue
        for name, value in vars(module).items():
            if name.startswith("_") or id(value) in vocabulary_objects:
                continue
            found: set[str] = set()
            if isinstance(value, str):
                found = forbidden & {value}
            elif isinstance(value, (tuple, list, set, frozenset)):
                found = forbidden & {v for v in value if isinstance(v, str)}
            elif isinstance(value, dict):
                found = forbidden & (
                    {k for k in value if isinstance(k, str)}
                    | {v for v in value.values() if isinstance(v, str)})
            if found:
                offenders.append(f"privacy.{info.name}.{name} -> {sorted(found)}")
    assert not offenders


def test_defaults_reads_no_configuration_at_all(p7_conn):
    # "No build flag, packaged configuration file, or first-run flow." A module that
    # cannot reach a file or an environment variable cannot be handed a mode by one.
    import privacy.defaults as module
    readers = {"os", "sys", "pathlib", "Path", "json", "tomllib", "configparser",
               "environ", "getenv", "open", "importlib", "pkgutil"}
    assert not (readers & set(vars(module)))


def test_the_resolver_is_deterministic(p7_conn):
    assert resolved(None) == resolved(None)


def test_p7_names_no_winner_between_the_two_local_modes(p7_conn):
    # SPEC Open question 11, held open BY CONSTRUCTION: there is no default mode in
    # `src/privacy/` for a later reader to mistake for an answer. `install_mode` has
    # no default, so a build that forgets to name one does not start; it fails.
    import inspect
    parameter = inspect.signature(resolve_default_policy).parameters["install_mode"]
    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    import privacy.defaults as module
    held = [value for name, value in vars(module).items()
            if not name.startswith("_") and isinstance(value, str)]
    assert sorted(text for text in held if text in OPERATION_MODES) == \
        sorted(LOCAL_FIRST_MODES)


# --- what the gate actually calls -------------------------------------------

def test_effective_policy_falls_back_to_the_floor_when_nothing_is_set(p7_conn):
    policy = effective_policy(p7_conn, plan_version=PLAN, install_mode=OFFLINE,
                              set_at=FIXED_CLOCK)
    assert policy.operation_mode == OFFLINE
    assert policy.policy_version == UNSET_POLICY_VERSION
    assert_local_first(policy)


def test_effective_policy_reads_the_stored_policy_when_there_is_one(p7_conn):
    version = set_policy(
        p7_conn,
        a_stored_policy(operation_mode="cloud_assisted", redaction_settings={}),
        component_version=COMPONENT, user_id="joseph",
        reason="the user turned on cloud assistance for Academics")
    policy = effective_policy(p7_conn, plan_version=PLAN, install_mode=OFFLINE,
                              set_at=FIXED_CLOCK)
    assert policy.policy_version == version
    assert policy.operation_mode == "cloud_assisted"
    # The absent facets are still filled with the more redacting value: a stored
    # policy that never named a facet has not chosen `shown` for it.
    assert policy.redaction_settings == dict(MORE_REDACTING)
