# tests/p7/test_p7_display.py
"""Done-means 10, and the display half of Done-means 12.

§8.4's UI paragraph, entire: "Privacy also applies to the user interface. A summary
such as '11 protected identity records' may be safe to show, while a visible list of
passport filenames on a shared screen may not be. Protected branches should have
configurable redaction in the canvas and review screens. The user can choose whether
names, previews, thumbnails, OCR text, or location data are shown."
"""
from __future__ import annotations

import dataclasses
import inspect
import json
from collections.abc import Mapping
from typing import get_type_hints

import pytest

from database_agent.files_table import get_file, record_file

import privacy.display as display_module
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.display import (
    ProtectedSummary, RedactionSettings, UnknownDisplaySetting, display_policy,
    summarize_protected,
)
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.vocabulary import (
    DISPLAY_FACETS, HANDLING_CLASSES, REDACTED, REDACTION_VALUES, SHOWN, USER,
    USER_CONFIRMED, OutOfVocabulary,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
COMPONENT = "0.1.0"
IDENTITY = "Identity"

ALL_SHOWN = {facet: SHOWN for facet in DISPLAY_FACETS}


@pytest.fixture()
def store(p7_conn):
    return ClassificationStore(p7_conn)


@pytest.fixture()
def corpus(p7_conn, tmp_path):
    """Eleven passport scans and two ordinary files, so §8.4's own example number is
    the number the summary produces."""
    root = tmp_path / "corpus"
    root.mkdir()
    file_ids = []
    for index in range(11):
        document = root / f"passport-scan-{index}.pdf"
        document.write_bytes(f"%PDF-1.4 passport {index}".encode())
        file_ids.append(_record(p7_conn, root, document))
    for name in ("syllabus.pdf", "notes.md"):
        document = root / name
        document.write_bytes(f"plain {name}".encode())
        file_ids.append(_record(p7_conn, root, document))
    return file_ids


def _record(conn, root, document):
    return record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=document.suffix,
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(root), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


def classify(conn, store, file_id, *, handling_class, protected):
    store.write(ClassificationRecord(
        file_id=file_id, content_hash=get_file(conn, file_id)["content_hash"],
        handling_class=handling_class, protected=protected, basis=USER,
        evidence_refs=(), reliability_state=USER_CONFIRMED,
        observed_at=FIXED_CLOCK))


def install(conn, *, plan_version="plan-1", redaction_settings=None) -> str:
    policy = Policy(policy_version=UNSET_POLICY_VERSION, operation_mode="local_model",
                    consent_grants=(),
                    redaction_settings=dict(redaction_settings or {}),
                    automatic_move_permissions={}, plan_version=plan_version,
                    set_at=FIXED_CLOCK)
    return set_policy(conn, policy, component_version=COMPONENT,
                      user_id="joseph",
                      reason="the fixture's starting policy")


def summarize(conn, store, file_ids):
    return summarize_protected(conn, IDENTITY, store=store,
                               files_in_scope=lambda scope: tuple(file_ids))


class _StoredPolicyStub:
    """Whatever `current_policy` hands back, seen through the one attribute
    `display_policy` reads. Used to reach `display_policy`'s own load-error guard,
    which the shipped `Policy.__post_init__` makes unreachable through the database."""

    def __init__(self, redaction_settings):
        self.redaction_settings = redaction_settings


# --- the five facets --------------------------------------------------------

def test_the_five_facets_are_8_4s_own_list_in_8_4s_order():
    # "whether names, previews, thumbnails, OCR text, or location data are shown."
    assert [field.name for field in dataclasses.fields(RedactionSettings)] == [
        "names", "previews", "thumbnails", "ocr_text", "location_data"]
    assert tuple(DISPLAY_FACETS) == tuple(
        field.name for field in dataclasses.fields(RedactionSettings))


def test_there_is_no_sixth_facet():
    assert len(dataclasses.fields(RedactionSettings)) == 5


def test_each_facet_takes_one_of_two_values(p7_conn):
    # SPEC §10: "each shown | redacted". The two values are TASK 2's -- one home, one
    # name -- and this file imports them rather than publishing a third spelling.
    assert REDACTION_VALUES == (SHOWN, REDACTED) == ("shown", "redacted")
    assert not hasattr(display_module, "SETTING_VALUES")
    assert not hasattr(display_module, "FACET_VALUES")
    install(p7_conn, redaction_settings=ALL_SHOWN)
    settings = display_policy(p7_conn, plan_version="plan-1")
    for facet in DISPLAY_FACETS:
        assert settings.facet(facet) in REDACTION_VALUES


def test_facet_refuses_a_name_outside_the_five(p7_conn):
    install(p7_conn, redaction_settings=ALL_SHOWN)
    settings = display_policy(p7_conn, plan_version="plan-1")
    with pytest.raises(UnknownDisplaySetting):
        settings.facet("audio")


def test_the_policy_type_already_refuses_a_third_value_and_a_sixth_facet():
    """The load error the plan put on `display_policy` is already the SHIPPED
    `Policy.__post_init__`'s, so a bad setting cannot reach the database at all --
    which is why the two tests the plan wrote against `display_policy` are written
    against the guard that actually fires. Recorded rather than deleted: this is the
    assertion that fails the day the upstream guard is relaxed, at which point
    `display_policy`'s own guard below becomes the reachable one."""
    with pytest.raises(OutOfVocabulary):
        Policy(policy_version=UNSET_POLICY_VERSION, operation_mode="local_model",
               consent_grants=(), redaction_settings={"names": "blurred"},
               automatic_move_permissions={}, plan_version="plan-1",
               set_at=FIXED_CLOCK)
    with pytest.raises(OutOfVocabulary):
        Policy(policy_version=UNSET_POLICY_VERSION, operation_mode="local_model",
               consent_grants=(), redaction_settings={"audio": REDACTED},
               automatic_move_permissions={}, plan_version="plan-1",
               set_at=FIXED_CLOCK)


def test_a_third_value_read_back_is_a_load_error_not_a_fallback(p7_conn, monkeypatch):
    # "A value outside this set is a load error, not a fallback" (SPEC §1's rule,
    # applied to the setting values §10 states). `display_policy` validates what it
    # READS rather than trusting the row, so relaxing the upstream constructor cannot
    # silently turn a stored `"blurred"` into a shown facet.
    monkeypatch.setattr(display_module, "current_policy",
                        lambda conn, *, plan_version: _StoredPolicyStub(
                            {**ALL_SHOWN, "names": "blurred"}))
    with pytest.raises(UnknownDisplaySetting):
        display_policy(p7_conn, plan_version="plan-1")


def test_an_unknown_facet_read_back_is_a_load_error(p7_conn, monkeypatch):
    monkeypatch.setattr(display_module, "current_policy",
                        lambda conn, *, plan_version: _StoredPolicyStub(
                            {**ALL_SHOWN, "audio": REDACTED}))
    with pytest.raises(UnknownDisplaySetting):
        display_policy(p7_conn, plan_version="plan-1")


# --- the default is the more redacting one ----------------------------------

def test_an_empty_policy_resolves_every_facet_to_its_more_redacting_value(p7_conn):
    # Done-means 12's display half: "every redaction setting the design leaves
    # configurable resolves to its more redacting value".
    install(p7_conn)
    settings = display_policy(p7_conn, plan_version="plan-1")
    for facet in DISPLAY_FACETS:
        assert settings.facet(facet) == MORE_REDACTING[facet] == REDACTED


def test_no_policy_at_all_resolves_to_the_floor_rather_than_raising(p7_conn):
    # `current_policy` returns None when nothing has been set -- "a fact, not a gap".
    # W1's `resolve_default_policy(None, ...)` fills `redaction_settings` from
    # `MORE_REDACTING`, and this reads it the same way: no policy is every facet
    # absent, and an absent facet is never `shown`.
    settings = display_policy(p7_conn, plan_version="plan-nothing-was-ever-set")
    for facet in DISPLAY_FACETS:
        assert settings.facet(facet) == REDACTED


def test_a_partial_policy_fills_the_missing_facets_from_the_more_redacting_rule(
        p7_conn):
    install(p7_conn, redaction_settings={"names": SHOWN})
    settings = display_policy(p7_conn, plan_version="plan-1")
    assert settings.names == SHOWN
    for facet in ("previews", "thumbnails", "ocr_text", "location_data"):
        assert settings.facet(facet) == REDACTED


def test_the_user_can_still_choose_shown(p7_conn):
    # §8.4: "The user can choose whether names, previews, thumbnails, OCR text, or
    # location data are shown." The floor is on the DEFAULT, never on the choice.
    install(p7_conn, redaction_settings=ALL_SHOWN)
    settings = display_policy(p7_conn, plan_version="plan-1")
    assert all(settings.facet(facet) == SHOWN for facet in DISPLAY_FACETS)


def test_settings_are_plan_scoped(p7_conn):
    # §8.8 lists "Privacy and model-consent policies" inside the plan version.
    install(p7_conn, plan_version="plan-1")
    install(p7_conn, plan_version="plan-2", redaction_settings=ALL_SHOWN)
    assert display_policy(p7_conn, plan_version="plan-1").names == REDACTED
    assert display_policy(p7_conn, plan_version="plan-2").names == SHOWN


# --- the aggregate-safe summary ---------------------------------------------

def test_the_summary_has_three_fields_and_none_can_hold_a_filename():
    """Done-means 10: the summary "returns counts and class breakdown and cannot
    return filenames or content."

    Asserted at the TYPE level, with resolved annotations. A runtime filter is
    something a future caller can route around; a string scan matches the docstring
    that explains the rule; and comparing field NAMES against a forbidden list is
    weaker than both, because it passes any new field whose name nobody thought to
    ban. A record whose every field is an `int` or a `Mapping[str, int]` cannot carry
    a filename at all.

    D11 added `scope_total` and this assertion moved WITH it, in one change. The
    skeleton's constraint read "two fields, and deliberately no third", which made the
    field COUNT the safety property; it never was. The property is that no field has a
    type a filename could occupy, and that is what is asserted here.
    """
    hints = get_type_hints(ProtectedSummary)
    assert [field.name for field in dataclasses.fields(ProtectedSummary)] == [
        "count", "scope_total", "class_breakdown"]
    assert hints == {"count": int, "scope_total": int,
                     "class_breakdown": Mapping[str, int]}
    for forbidden in ("filename", "filenames", "path", "paths", "examples",
                      "members", "file_ids", "raw_value", "text", "preview",
                      "thumbnail"):
        assert forbidden not in hints


def test_eleven_protected_identity_records(p7_conn, store, corpus):
    # §8.4's own example, as the acceptance criterion: "A summary such as '11
    # protected identity records' may be safe to show."
    for file_id in corpus[:11]:
        classify(p7_conn, store, file_id,
                 handling_class="highly_sensitive_credential_bearing",
                 protected=True)
    for file_id in corpus[11:]:
        classify(p7_conn, store, file_id, handling_class="public_low",
                 protected=False)
    summary = summarize(p7_conn, store, corpus)
    assert summary.count == 11
    # D11: the breakdown is a census of the WHOLE SCOPE, so its denominator is the
    # thirteen files in scope and not the eleven protected ones.
    assert summary.scope_total == 13
    assert summary.class_breakdown["highly_sensitive_credential_bearing"] == 11
    assert summary.class_breakdown["public_low"] == 2
    assert sum(summary.class_breakdown.values()) == 13


def test_the_breakdown_covers_every_handling_class_zero_filled(
        p7_conn, store, corpus):
    for file_id in corpus:
        classify(p7_conn, store, file_id, handling_class="public_low",
                 protected=False)
    summary = summarize(p7_conn, store, corpus)
    assert set(summary.class_breakdown) == set(HANDLING_CLASSES)
    assert summary.class_breakdown["sensitive_personal"] == 0


def test_the_breakdown_is_ordered_by_the_closed_vocabulary(p7_conn, store, corpus):
    # A deterministic key order, taken from HANDLING_CLASSES rather than from
    # insertion, so two runs over the same corpus render the same screen and a
    # reviewer comparing two summaries is comparing rows and not orderings.
    classify(p7_conn, store, corpus[0],
             handling_class="highly_sensitive_credential_bearing", protected=True)
    classify(p7_conn, store, corpus[1], handling_class="sensitive_personal",
             protected=True)
    summary = summarize(p7_conn, store, corpus[:2])
    assert list(summary.class_breakdown) == list(HANDLING_CLASSES)


def test_the_breakdown_is_a_census_of_the_scope_and_never_of_the_protected_set(
        p7_conn, store, corpus):
    # D11, and the bug it exists to keep out. Two files of the same class, one
    # protected and one not. `count` is 1, the breakdown says 2, and `scope_total`
    # is the breakdown's stated denominator -- so a UI rendering §8.4's "11 protected
    # identity records" off the breakdown cannot describe an UNPROTECTED file as
    # protected, which is what one denominator for two questions would let it do.
    classify(p7_conn, store, corpus[0],
             handling_class="highly_sensitive_credential_bearing", protected=True)
    classify(p7_conn, store, corpus[1],
             handling_class="highly_sensitive_credential_bearing", protected=False)
    summary = summarize(p7_conn, store, corpus[:2])
    assert summary.count == 1
    assert summary.scope_total == 2
    assert sum(summary.class_breakdown.values()) == summary.scope_total
    assert summary.class_breakdown["highly_sensitive_credential_bearing"] == 2
    assert sum(summary.class_breakdown.values()) != summary.count


def test_the_count_follows_the_flag_and_not_the_class(p7_conn, store, corpus):
    # SPEC §2, and Open question 1 again: a `public_low` file the user marked
    # protected is counted, and a top-class file that is not marked is not.
    classify(p7_conn, store, corpus[0], handling_class="public_low", protected=True)
    classify(p7_conn, store, corpus[1],
             handling_class="highly_sensitive_credential_bearing", protected=False)
    summary = summarize(p7_conn, store, corpus[:2])
    assert summary.count == 1
    assert summary.scope_total == 2
    assert summary.class_breakdown["public_low"] == 1
    assert summary.class_breakdown["highly_sensitive_credential_bearing"] == 1


def test_a_file_outside_the_scope_is_not_counted(p7_conn, store, corpus):
    classify(p7_conn, store, corpus[0],
             handling_class="highly_sensitive_credential_bearing", protected=True)
    empty = summarize(p7_conn, store, ())
    assert empty.count == 0
    assert empty.scope_total == 0
    assert sum(empty.class_breakdown.values()) == 0
    assert set(empty.class_breakdown) == set(HANDLING_CLASSES)
    assert summarize(p7_conn, store, corpus[:1]).count == 1


def test_with_no_detector_the_summary_reads_zero_and_the_breakdown_says_why(
        p7_conn, store, corpus):
    # D2 leaves the detector unwritten, so this is the summary a real corpus produces
    # today. "0 protected records" means NOTHING HAS LOOKED, not "nothing is
    # protected" -- which is precisely why D2 keeps `unreadable_unclassified` off
    # `files.sensitivity_state` and on the gate outcome instead.
    summary = summarize(p7_conn, store, corpus)
    assert summary.count == 0
    assert summary.class_breakdown["unreadable_unclassified"] == len(corpus)
    # D11's whole point in one line: the two denominators disagree, and they should.
    assert summary.scope_total == len(corpus)
    assert sum(summary.class_breakdown.values()) == summary.scope_total
    assert summary.scope_total != summary.count


def test_the_breakdown_is_not_mutable_by_a_caller(p7_conn, store, corpus):
    summary = summarize(p7_conn, store, corpus)
    with pytest.raises(TypeError):
        summary.class_breakdown["public_low"] = 99


# --- C4: both surfaces are reads --------------------------------------------

def test_neither_surface_writes_anything(p7_conn, store, corpus):
    # C4: "the gate still raises and writes nothing -- a gate that also wrote would be
    # doing two jobs." Both of these are predicates over stored state: they append no
    # event, mint no policy version and issue no `UPDATE files`. Asserted rather than
    # assumed, because "this function is a read" is the kind of claim that stays in a
    # docstring after it stops being true.
    install(p7_conn)
    classify(p7_conn, store, corpus[0], handling_class="sensitive_personal",
             protected=True)
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    policies = p7_conn.execute(
        "SELECT count(*) c FROM privacy_policies").fetchone()["c"]
    mirror = get_file(p7_conn, corpus[0])["sensitivity_state"]
    display_policy(p7_conn, plan_version="plan-1")
    summarize(p7_conn, store, corpus)
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before
    assert p7_conn.execute(
        "SELECT count(*) c FROM privacy_policies").fetchone()["c"] == policies
    assert get_file(p7_conn, corpus[0])["sensitivity_state"] == mirror


# --- what is not resolved here ----------------------------------------------

def test_p13s_per_branch_question_is_recorded_and_not_answered(p7_conn):
    """P13 Open question 7, quoted and not resolved.

        "**Does the user's redaction setting have a scope?** §8.4 says 'Protected
        branches should have configurable redaction', which reads per-branch, while
        P7's `Gate.display_policy()` takes no scope argument and reads global.
        *Threatens P7.*"

    `display_policy` therefore takes a plan version and no branch, node or scope. This
    test fails the day someone adds one, which is the point: adding it would answer
    P13's question in an implementation rather than in a SPEC, and the answer changes
    what P13's canvas and review screens have to render.
    """
    parameters = set(inspect.signature(display_policy).parameters)
    assert parameters == {"conn", "plan_version"}
    assert "branch" not in parameters and "node_id" not in parameters


def test_files_in_scope_has_no_default(p7_conn):
    # Open question 3 once more: P7 defines no corpus area.
    parameter = inspect.signature(summarize_protected).parameters["files_in_scope"]
    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY


def test_the_summary_takes_the_store_as_a_keyword_and_scope_stays_opaque():
    # `summarize_protected(conn, scope, *, store, files_in_scope)` -- the two
    # widenings the task reports, pinned so a later edit cannot quietly drop the
    # injection and read a store of its own.
    signature = inspect.signature(summarize_protected)
    assert list(signature.parameters) == [
        "conn", "scope", "store", "files_in_scope"]
    assert signature.parameters["scope"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert signature.parameters["store"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["store"].default is inspect.Parameter.empty


def test_this_module_publishes_no_value_vocabulary_of_its_own():
    # §3.1: one home, one name. `SHOWN`/`REDACTED`/`REDACTION_VALUES` are Task 2's
    # and are imported, never re-published under a second spelling.
    for banned in ("SETTING_VALUES", "FACET_VALUES", "SHOWN", "REDACTED",
                   "DISPLAY_VALUES"):
        assert not hasattr(display_module, banned), (
            f"{banned} is a second home for a vocabulary privacy.vocabulary owns")
