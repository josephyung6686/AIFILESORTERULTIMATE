"""§8.7's query-before-classify, and reclassification as supersession.

The three assertions 10-i4-learning-ops.md's Done-means names, in its own words:
"a fixture with one unresected reject at the stated `basis_key` produces zero
re-emissions of that proposal ... A different `basis_key` at the same scope still
emits. A reset at that scope+subject allows emission again."
"""
import json

import pytest

from database_agent.events import CORRECTION_FIELDS, CORRECTION_SCOPES, append_event
from database_agent.files_table import get_file, record_file
from database_agent.learning import SCOPES, learning_records, reset_preferences

from privacy.authorship import (
    CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, SUBSYSTEM,
)
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.learning_seam import (
    ACCEPT, FILE_SCOPE, PROPOSAL_CLASS, RECORDED_ACTIONS, RECORDED_ACTION_SOURCES,
    REJECT, UnknownRecordedAction, assign, basis_key_for, check_recorded_action,
    reclassify, suppressed,
)
from privacy.vocabulary import USER, USER_CONFIRMED

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"
DETECTOR_KEYS = (
    "sha256:ba9777bcba0096decc525198035644949d2357bf7f9a9cb3492c948c86c0fcbd",
    "sha256:65534918f6abecf79fd8b5f58ab1e4721d1a8ea2b75b79d6a05cc47523260c42",
)
# Task 3's `_is_observation_key` requires "sha256:" + EXACTLY 64 hex; the second
# key in this plan section carried 65 and is rejected by the shipped record.
assert all(len(k) == 71 for k in DETECTOR_KEYS)


@pytest.fixture()
def file_id(p7_conn, tmp_path):
    """A real P1 row: the classification is keyed on (file_id, content_hash) and a
    synthesized id would not exercise the projection onto `files`."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    document = corpus / "passport-scan.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    return record_file(
        p7_conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


@pytest.fixture()
def content_hash(p7_conn, file_id):
    return get_file(p7_conn, file_id)["content_hash"]


@pytest.fixture()
def store(p7_conn):
    return ClassificationStore(p7_conn)


def a_record(file_id, content_hash, handling_class="sensitive_personal", **over):
    base = dict(file_id=file_id, content_hash=content_hash,
                handling_class=handling_class, protected=True, basis="detector",
                evidence_refs=DETECTOR_KEYS, reliability_state="validated",
                observed_at=FIXED_CLOCK)
    base.update(over)
    return ClassificationRecord(**base)


def a_user_rejection(conn, file_id, content_hash, *, store):
    """The user downgrading `sensitive_personal`, which is what leaves the reject."""
    return reclassify(conn, file_id, "personal_non_sensitive",
                      "these are my own notes, not an identity record",
                      store=store, content_hash=content_hash, protected=False,
                      evidence_refs=DETECTOR_KEYS, user_id="joseph",
                      component_version=COMPONENT, observed_at=LATER)


# --- the vocabulary ---------------------------------------------------------

def test_the_proposal_class_is_the_one_10_i4_assigns_p7():
    # 10-i4-learning-ops.md's table: `privacy` | `(file_id, handling_class)` | P7.
    assert PROPOSAL_CLASS == "privacy"


def test_the_basis_key_is_file_id_and_handling_class_and_nothing_else():
    key = basis_key_for("file-1", "sensitive_personal")
    assert json.loads(key) == ["file-1", "sensitive_personal"]
    assert basis_key_for("file-1", "sensitive_personal") == key
    assert basis_key_for("file-1", "public_low") != key


def test_the_six_recorded_actions_carry_the_specs_own_words():
    # SPEC Correction learning, "Recorded actions". A paraphrase is a failing test and
    # not an editorial choice -- Task 2's MODE_SEMANTICS discipline, applied here.
    assert len(RECORDED_ACTIONS) == 6
    assert set(RECORDED_ACTION_SOURCES) == set(RECORDED_ACTIONS)
    assert RECORDED_ACTION_SOURCES["reclassify_private"] == (
        "reclassifying a file as private")
    assert RECORDED_ACTION_SOURCES["mark_private_residual_review"] == (
        "mark it as private")
    assert RECORDED_ACTION_SOURCES["downgrade_classification"] == (
        "downgrading a classification")
    assert RECORDED_ACTION_SOURCES["set_policy"] == (
        "granting, changing, or revoking a policy")
    assert RECORDED_ACTION_SOURCES["change_redaction_setting"] == (
        "changing a redaction setting")
    assert RECORDED_ACTION_SOURCES["set_automatic_move_permission"] == (
        "granting or withdrawing an automatic-move permission for protected material")


def test_a_seventh_recorded_action_is_a_load_error():
    assert check_recorded_action("downgrade_classification") == (
        "downgrade_classification")
    with pytest.raises(UnknownRecordedAction):
        check_recorded_action("delete_the_file")


def test_the_default_scope_is_file_and_it_is_one_of_p1s_six():
    # §8.7's worked warning: one transcript belonging in one packet "should not teach
    # the engine that all transcripts belong there."
    assert FILE_SCOPE == "file"
    assert FILE_SCOPE in SCOPES and FILE_SCOPE in CORRECTION_SCOPES


# --- query before classify --------------------------------------------------

def test_an_unrejected_class_is_not_suppressed(p7_conn, file_id):
    assert suppressed(p7_conn, file_id, "sensitive_personal") is False


def test_an_unreset_reject_produces_zero_re_emissions(
        p7_conn, file_id, content_hash, store):
    # `a_user_rejection` is a DOWNGRADE, so it needs something to downgrade from:
    # over nothing, `reclassify` accepts the new class instead of rejecting a prior
    # one, and leaves no reject at `sensitive_personal` for `suppressed` to find.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    assert suppressed(p7_conn, file_id, "sensitive_personal") is True

    before = p7_conn.execute(
        "SELECT count(*) c FROM events WHERE event_type = ?",
        (CLASSIFICATION_ASSIGNED,)).fetchone()["c"]
    again = assign(p7_conn, a_record(file_id, content_hash), store=store,
                   component_version=COMPONENT)
    after = p7_conn.execute(
        "SELECT count(*) c FROM events WHERE event_type = ?",
        (CLASSIFICATION_ASSIGNED,)).fetchone()["c"]

    assert again is None
    assert after == before


def test_a_different_basis_key_at_the_same_scope_still_emits(
        p7_conn, file_id, content_hash, store):
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    emitted = assign(
        p7_conn,
        a_record(file_id, content_hash,
                 handling_class="highly_sensitive_credential_bearing"),
        store=store, component_version=COMPONENT)
    assert emitted is not None
    assert emitted.handling_class == "highly_sensitive_credential_bearing"


def test_a_reset_restores_emission(p7_conn, file_id, content_hash, store):
    # `a_user_rejection` is a DOWNGRADE, so it needs something to downgrade from:
    # over nothing, `reclassify` accepts the new class instead of rejecting a prior
    # one, and leaves no reject at `sensitive_personal` for `suppressed` to find.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    assert suppressed(p7_conn, file_id, "sensitive_personal") is True
    reset_preferences(p7_conn, FILE_SCOPE, file_id, author=SUBSYSTEM,
                      component_version=COMPONENT, user_id="joseph")
    assert suppressed(p7_conn, file_id, "sensitive_personal") is False
    assert assign(p7_conn, a_record(file_id, content_hash), store=store,
                  component_version=COMPONENT) is not None


def test_p7_does_the_filtering_because_p1s_reader_does_not(
        p7_conn, file_id, content_hash, store):
    # `learning_records(conn, scope, subject_id)` filters on correction_scope,
    # correction_subject and `user_id IS NOT NULL` only. 10-i4 assigns proposal_class
    # and basis_key filtering to the acting part: "Ignores records at the wrong
    # `proposal_class`. Ignores records whose `basis_key` does not match."
    # `a_user_rejection` is a DOWNGRADE, so it needs something to downgrade from:
    # over nothing, `reclassify` accepts the new class instead of rejecting a prior
    # one, and leaves no reject at `sensitive_personal` for `suppressed` to find.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    rows = learning_records(p7_conn, FILE_SCOPE, file_id)
    assert len(rows) == 1
    assert rows[0]["proposal_class"] == PROPOSAL_CLASS
    assert rows[0]["basis_key"] == basis_key_for(file_id, "sensitive_personal")
    assert rows[0]["polarity"] == REJECT
    # Another part's rejection, at a basis key P7 has NOT rejected. This placement is
    # deliberate and it is the whole test: P13's row must be the ONLY record at
    # `public_low`, because a foreign row sitting BESIDE a P7 row at the same key
    # proves nothing -- delete the `proposal_class` guard from `suppressed` and the
    # P7 row still answers True, so the assertion passes either way. Here the guard is
    # load-bearing in both directions: without it `public_low` reads as suppressed
    # (P13's rejection is honoured as P7's), and without the `basis_key` guard it
    # reads as suppressed too (P7's `sensitive_personal` rejection is honoured at the
    # wrong key). 10-i4: "Ignores records at the wrong `proposal_class`. Ignores
    # records whose `basis_key` does not match."
    append_event(p7_conn, event_type="review action routed", subsystem="P13",
                 component_version=COMPONENT, observed_at=LATER,
                 explanation='{"note":"another part"}', user_id="joseph",
                 correction_scope=FILE_SCOPE, correction_subject=file_id,
                 polarity=REJECT, proposal_class="placement",
                 basis_key=basis_key_for(file_id, "public_low"))
    assert len(learning_records(p7_conn, FILE_SCOPE, file_id)) == 2
    assert suppressed(p7_conn, file_id, "sensitive_personal") is True
    assert suppressed(p7_conn, file_id, "public_low") is False


def test_a_system_assignment_can_never_become_a_learning_record(
        p7_conn, file_id, content_hash, store):
    # P1's reader requires `user_id IS NOT NULL`. A detector's assignment carries no
    # user, so it is structurally incapable of suppressing the next one.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    assert learning_records(p7_conn, FILE_SCOPE, file_id) == []
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CLASSIFICATION_ASSIGNED,)).fetchone()
    for field in CORRECTION_FIELDS:
        assert row[field] is None
    assert row["user_id"] is None


def test_suppression_guards_assign_and_never_the_users_own_correction(
        p7_conn, file_id, content_hash, store):
    # Task 16's own rule, and it has no test in the plan: "What is suppressed is the
    # product re-proposing, not the user acting. A `reclassify` that consulted the
    # suppression store would refuse the user's own correction on the grounds that
    # they had already made it." The user downgrades, then changes their mind back to
    # the very class they rejected -- `suppressed` says True at that key throughout.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    assert suppressed(p7_conn, file_id, "sensitive_personal") is True
    restored = reclassify(p7_conn, file_id, "sensitive_personal",
                          "I was wrong, this is my passport after all", store=store,
                          content_hash=content_hash, protected=True,
                          evidence_refs=DETECTOR_KEYS, user_id="joseph",
                          component_version=COMPONENT, observed_at=LATER)
    assert restored.handling_class == "sensitive_personal"
    assert store.current(file_id, content_hash) == restored


# --- reclassification is supersession, never overwrite ----------------------

def test_reclassify_writes_a_new_user_confirmed_fact(
        p7_conn, file_id, content_hash, store):
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    revised = a_user_rejection(p7_conn, file_id, content_hash, store=store)
    # Task 2 owns the literal spelling of both (brief §11); this is the one place in
    # the file that pins it, and everything else consumes the named constant.
    assert revised.reliability_state == USER_CONFIRMED == "user_confirmed"
    assert revised.basis == USER == "user"
    assert revised.handling_class == "personal_non_sensitive"
    assert store.current(file_id, content_hash) == revised


def test_both_records_remain_inspectable(p7_conn, file_id, content_hash, store):
    # §8.2's explicit rule, and §8.4's "can be revised by the user" -- a revision
    # supersedes and both remain available.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    history = store.history(file_id)
    assert [r.handling_class for r in history] == [
        "sensitive_personal", "personal_non_sensitive"]
    assert [r.basis for r in history] == ["detector", USER]


def test_reclassify_appends_classification_superseded_and_not_an_overwrite(
        p7_conn, file_id, content_hash, store):
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CLASSIFICATION_SUPERSEDED,)).fetchone()
    assert row["subsystem"] == "P7"
    assert row["user_id"] == "joseph"
    assert row["polarity"] == REJECT
    assert row["correction_scope"] == FILE_SCOPE
    assert row["correction_subject"] == file_id
    assert row["basis_key"] == basis_key_for(file_id, "sensitive_personal")


def test_a_first_classification_by_the_user_accepts_rather_than_rejects(
        p7_conn, file_id, content_hash, store):
    # Nothing was classified, so there is nothing to reject. One event, and it is an
    # assignment: 10-i4 rule 4 makes an accept-and-reject pair a row that changes
    # nothing plus a second place for the two to disagree.
    reclassify(p7_conn, file_id, "highly_sensitive_credential_bearing",
               "this is my passport", store=store, content_hash=content_hash,
               protected=True, evidence_refs=(), user_id="joseph",
               component_version=COMPONENT, observed_at=LATER)
    assert p7_conn.execute("SELECT count(*) c FROM events WHERE event_type = ?",
                           (CLASSIFICATION_SUPERSEDED,)).fetchone()["c"] == 0
    row = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (CLASSIFICATION_ASSIGNED,)).fetchone()
    assert row["polarity"] == ACCEPT
    assert row["basis_key"] == basis_key_for(
        file_id, "highly_sensitive_credential_bearing")


def test_a_downgrade_stores_the_observation_keys_the_detector_fired_on(
        p7_conn, file_id, content_hash, store):
    # §8.7 and M14: "The key, not the id, is what makes that durable" -- a per-row
    # `observation_id` dies when the extractor is upgraded and the same false
    # protection returns.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    row = p7_conn.execute("SELECT explanation FROM events WHERE event_type = ?",
                          (CLASSIFICATION_SUPERSEDED,)).fetchone()
    payload = json.loads(row["explanation"])
    assert tuple(payload["rejected_evidence_refs"]) == DETECTOR_KEYS
    assert all(ref.startswith("sha256:") for ref in payload["rejected_evidence_refs"])
    assert payload["superseded_handling_class"] == "sensitive_personal"


def test_protected_is_carried_and_never_derived_from_the_class(
        p7_conn, file_id, content_hash, store):
    # SPEC §2, and Open question 1. A caller may mark a `public_low` file protected and
    # this module does not argue.
    record = reclassify(p7_conn, file_id, "public_low", "a scan of my own poster",
                        store=store, content_hash=content_hash, protected=True,
                        evidence_refs=(), user_id="joseph",
                        component_version=COMPONENT, observed_at=LATER)
    assert record.handling_class == "public_low"
    assert record.protected is True


def test_a_reason_is_required(p7_conn, file_id, content_hash, store):
    with pytest.raises(ValueError):
        reclassify(p7_conn, file_id, "public_low", "   ", store=store,
                   content_hash=content_hash, protected=False, evidence_refs=(),
                   user_id="joseph", component_version=COMPONENT, observed_at=LATER)


def test_a_scope_outside_8_7s_six_is_refused(p7_conn, file_id, content_hash, store):
    with pytest.raises(ValueError):
        reclassify(p7_conn, file_id, "public_low", "because", store=store,
                   content_hash=content_hash, protected=False, evidence_refs=(),
                   user_id="joseph", component_version=COMPONENT, observed_at=LATER,
                   correction_scope="everything")


def test_a_refused_call_writes_nothing_at_all(p7_conn, file_id, content_hash, store):
    # §3.6's fourth kind: a `ValueError` here is about the CALL, and a refusal that
    # had already written the record or the event would leave the log describing a
    # correction that did not happen.
    for bad in (dict(reason="   "), dict(correction_scope="everything"),
                dict(handling_class="not_a_class")):
        kwargs = dict(handling_class="public_low", reason="because",
                      correction_scope=FILE_SCOPE)
        kwargs.update(bad)
        with pytest.raises(ValueError):
            reclassify(p7_conn, file_id, kwargs["handling_class"], kwargs["reason"],
                       store=store, content_hash=content_hash, protected=False,
                       evidence_refs=(), user_id="joseph",
                       component_version=COMPONENT, observed_at=LATER,
                       correction_scope=kwargs["correction_scope"])
    assert store.history(file_id) == []
    # P1's `record_file` appends no event of its own (M8), so the log is empty and a
    # single leaked row from a refused call would be visible here.
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == 0
    assert get_file(p7_conn, file_id)["sensitivity_state"] is None


def test_a_broader_correction_scope_is_stored_and_suppresses_nothing(
        p7_conn, file_id, content_hash, store):
    # See the CONTRADICTION callout above. This pins the SHIPPED behaviour, not the
    # intended one: a corpus-scoped rejection is recorded honestly and `suppressed`
    # -- which reads FILE_SCOPE only -- does not see it, so the next `assign` at this
    # file re-proposes the class the user rejected. Making this test go the other way
    # would answer Open question 7, which is Joseph's and not this task's.
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    reclassify(p7_conn, file_id, "personal_non_sensitive", "not an identity record",
               store=store, content_hash=content_hash, protected=False,
               evidence_refs=DETECTOR_KEYS, user_id="joseph",
               component_version=COMPONENT, observed_at=LATER,
               correction_scope="corpus")
    assert len(learning_records(p7_conn, "corpus", file_id)) == 1
    assert learning_records(p7_conn, FILE_SCOPE, file_id) == []
    assert suppressed(p7_conn, file_id, "sensitive_personal") is False


def test_the_projection_onto_files_goes_through_p1s_setter(
        p7_conn, file_id, content_hash, store):
    # D2: `files.sensitivity_state` is the projection of the authoritative record,
    # written through P1's published `set_sensitivity_state`. Task 21 asserts
    # `src/privacy/` issues no `UPDATE files` of its own.
    assert get_file(p7_conn, file_id)["sensitivity_state"] is None
    assign(p7_conn, a_record(file_id, content_hash), store=store,
           component_version=COMPONENT)
    state = json.loads(get_file(p7_conn, file_id)["sensitivity_state"])
    assert state["handling_class"] == "sensitive_personal"
    a_user_rejection(p7_conn, file_id, content_hash, store=store)
    state = json.loads(get_file(p7_conn, file_id)["sensitivity_state"])
    assert state["handling_class"] == "personal_non_sensitive"


def test_the_projection_is_the_store_s_own_helper_and_not_a_private_copy():
    # The preamble's §3.4 lesson, applied: "if another module already owns a helper,
    # IMPORT IT." `classification_store.mirror` is D2's write-through and this module
    # holds no second spelling of it. Identity, not source text.
    import privacy.classification_store as store_module
    import privacy.learning_seam as module
    assert module.mirror is store_module.mirror
    assert not hasattr(module, "set_sensitivity_state")


def test_open_question_7_is_not_answered_here(p7_conn, file_id, content_hash, store):
    # OQ7: "§8.7 allows a repeated residual destination to become a corpus-level
    # preference; it does not say whether repeated privacy corrections may raise a
    # sensitivity floor for a class of files." Two rejections stay two file-scoped
    # records; nothing counts them and nothing widens.
    for _ in range(2):
        assign(p7_conn, a_record(file_id, content_hash), store=store,
               component_version=COMPONENT)
        a_user_rejection(p7_conn, file_id, content_hash, store=store)
    for scope in ("corpus", "domain", "group", "node", "template"):
        assert learning_records(p7_conn, scope, file_id) == []
    import privacy.learning_seam as module
    assert not [name for name, value in vars(module).items()
                if not name.startswith("__")
                and isinstance(value, (int, float)) and not isinstance(value, bool)]
