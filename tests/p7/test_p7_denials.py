"""Done-means 6 -- all eight reasons, and the one that is the ordinary case.

The detector is unwritten (D2), so on a real corpus every file resolves to
`Denied(unclassified)`. This file is written for that: `unclassified` gets the
longest section, and the audit-record tests run against an unclassified file
because that is what the log will actually be full of.

SPEC §6's eight: protected_cloud_target | unclassified | policy_revoked |
protected_records_template | whole_document_requested | dossier_over_budget |
always_local_item | mode_forbids_target.
"""
import json

import pytest

from database_agent.budget import CEILING_KEYS, set_ceiling
from database_agent.events import append_event
from database_agent.files_table import get_file, record_file

from privacy.audit import AUDIT_FIELDS, audit_record
from privacy.authorship import CONSENT_REVOKED, MODEL_RELEASE_DENIED, SUBSYSTEM
from privacy.classification import ClassificationRecord
from privacy.denial import (
    DECIDABLE_FROM_REQUEST, DENIAL_ORDER, PROTECTED_RECORDS_TEMPLATE,
    REVOKED_SCOPE_KEY, MalformedDenial, RemedyOption, deny,
    deny_always_local_item, deny_dossier_over_budget, deny_mode_forbids_target,
    deny_policy_revoked, deny_protected_cloud_target,
    deny_protected_records_template, deny_unclassified,
    deny_whole_document_requested, first_reason, is_protected_records,
    mode_forbids, over_dossier_ceiling, policy_revoked_for,
    protected_cloud_denies, record_denial, unclassified_denies,
)
from privacy.items import AlwaysLocalRequested, CandidateLabel, WholeDocumentRequested
from privacy.policy import Policy
from privacy.release import REQUEST_FIELDS, Denied, ModelCallRequest, ModelTarget, Target
from privacy.vocabulary import DENIAL_REASONS, OutOfVocabulary

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"
CEILING_KEY = "model.max_dossier_tokens_per_call"
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
LOCAL = ModelTarget(locality="local", model_id="llama-3-8b", provider="local")
DETECTOR_KEYS = (
    "sha256:ba9777bcba0096decc525198035644949d2357bf7f9a9cb3492c948c86c0fcbd",
)

_REQUEST_DEFAULTS = {
    "stage": "grouping",
    "target": Target(file_ids=("file-1",), group_id=None),
    "model_target": CLOUD,
    "requested_items": (CandidateLabel(label="fixture"),),
    "prompt_template_id": "template-1",
    "prompt_fingerprint": "fp-1",
    "max_dossier_tokens": 4000,
}


def a_request(**over) -> ModelCallRequest:
    """Built from `REQUEST_FIELDS`; Task 11 owns SPEC §6's seven names."""
    missing = [name for name in REQUEST_FIELDS if name not in _REQUEST_DEFAULTS]
    assert not missing, (
        f"REQUEST_FIELDS names {missing} and this test has no value for them; "
        "SPEC §6 changed and Task 13 needs a value, not a default")
    values = {name: _REQUEST_DEFAULTS[name] for name in REQUEST_FIELDS}
    values.update(over)
    return ModelCallRequest(**values)


def a_policy(**over) -> Policy:
    base = dict(policy_version="policy-1", operation_mode="cloud_assisted",
                consent_grants=(("Academics", "cloud_model"),),
                redaction_settings={"names": "redacted", "previews": "redacted",
                                    "thumbnails": "redacted", "ocr_text": "redacted",
                                    "location_data": "redacted"},
                automatic_move_permissions={}, plan_version="plan-1",
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


@pytest.fixture()
def file_id(p7_conn, tmp_path) -> str:
    """A real P1 row, because the denial must be shown NOT to write to it."""
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


def all_eight() -> dict[str, Denied]:
    """One built `Denied` per reason, so the audit test can parameterise over them."""
    return {
        "mode_forbids_target": deny_mode_forbids_target(
            operation_mode="offline", model_target=CLOUD, file_ids=("file-1",)),
        "policy_revoked": deny_policy_revoked(
            scope="Academics", policy=a_policy(consent_grants=()),
            file_ids=("file-1",)),
        "always_local_item": deny_always_local_item(
            AlwaysLocalRequested("GPS"), file_ids=("file-1",)),
        "unclassified": deny_unclassified(
            file_ids=("file-1",), locality="cloud", completeness=None),
        "protected_records_template": deny_protected_records_template(
            file_ids=("file-1",), model_target=LOCAL),
        "protected_cloud_target": deny_protected_cloud_target(
            file_ids=("file-1",), operation_mode="hybrid", scope="Academics",
            evidence_refs=DETECTOR_KEYS),
        "whole_document_requested": deny_whole_document_requested(
            WholeDocumentRequested("span 0-4096 covers the whole unit"),
            file_ids=("file-1",)),
        "dossier_over_budget": deny_dossier_over_budget(
            measured_tokens=9000, ceiling=4000, file_ids=("file-1",)),
    }


# --- the order, and the principle behind it ---------------------------------

def test_denial_order_is_a_permutation_of_the_vocabulary():
    assert set(DENIAL_ORDER) == set(DENIAL_REASONS)
    assert len(DENIAL_ORDER) == len(DENIAL_REASONS) == 8


def test_nothing_that_needs_content_is_decided_before_something_that_does_not():
    # The principle: a gate that materialised an excerpt and THEN discovered the mode
    # forbade the call has read a sensitive file for a call that was never going to
    # happen. Six reasons are decidable from the request; two need the resolved text.
    assert DECIDABLE_FROM_REQUEST < set(DENIAL_REASONS)
    needs_content = set(DENIAL_REASONS) - DECIDABLE_FROM_REQUEST
    assert needs_content == {"whole_document_requested", "dossier_over_budget"}
    last_cheap = max(DENIAL_ORDER.index(r) for r in DECIDABLE_FROM_REQUEST)
    first_costly = min(DENIAL_ORDER.index(r) for r in needs_content)
    assert last_cheap < first_costly


def test_dossier_over_budget_is_last():
    # M9: P8 measures and runs §8.6's ladder BEFORE calling. The gate is "the last
    # place to catch a caller that skipped its ladder", so it is checked last.
    assert DENIAL_ORDER[-1] == "dossier_over_budget"


def test_first_reason_returns_none_when_nothing_triggered():
    assert first_reason(()) is None
    assert first_reason(set()) is None


def test_mode_outranks_protected_cloud_target():
    # The negative-tests table: protected + cloud under `offline` or `local_model` is
    # `mode_forbids_target`, not `protected_cloud_target`. The mode is outermost.
    assert first_reason({"protected_cloud_target", "mode_forbids_target"}) == \
        "mode_forbids_target"


def test_unclassified_outranks_protected_cloud_target():
    # §8.4 makes classification "a precondition of escalation". With no record there
    # is no `protected` flag to read, so the rule below is literally unevaluable.
    assert first_reason({"protected_cloud_target", "unclassified"}) == "unclassified"


def test_protected_records_template_outranks_protected_cloud_target():
    # §7.3 binds local calls too, so it must precede the cloud-only rule.
    assert first_reason({"protected_cloud_target", "protected_records_template"}) == \
        "protected_records_template"


# --- 1. mode_forbids_target -------------------------------------------------

def test_mode_forbids_target_under_offline_and_local_model():
    # §8.4: "Fully offline mode: No content leaves the device; only local rules and
    # local models may run." A local model is permitted under both; a cloud one is not.
    assert mode_forbids("offline", "cloud") is True
    assert mode_forbids("local_model", "cloud") is True
    assert mode_forbids("offline", "local") is False
    assert mode_forbids("local_model", "local") is False
    assert mode_forbids("hybrid", "cloud") is False
    assert mode_forbids("cloud_assisted", "cloud") is False
    assert deny_mode_forbids_target(operation_mode="offline", model_target=CLOUD,
                                    file_ids=("file-1",)).reason == "mode_forbids_target"


# --- 2. policy_revoked ------------------------------------------------------

def test_policy_revoked_after_a_scope_is_withdrawn(p7_conn):
    # Task 15's `revoke` appends this event with `canonical_json({"scope": scope, ...})`.
    # "Granted and then withdrawn" is a different fact from "never granted": the user
    # has already said no once, so §8.7's negative feedback applies to the remedy.
    granted = a_policy()
    assert policy_revoked_for(p7_conn, granted, "Academics") is False
    append_event(p7_conn, event_type=CONSENT_REVOKED, subsystem=SUBSYSTEM,
                 component_version=COMPONENT, observed_at=LATER,
                 explanation=json.dumps({REVOKED_SCOPE_KEY: "Academics"}))
    withdrawn = a_policy(consent_grants=(), policy_version="policy-2")
    assert policy_revoked_for(p7_conn, withdrawn, "Academics") is True
    assert deny_policy_revoked(scope="Academics", policy=withdrawn,
                               file_ids=("file-1",)).reason == "policy_revoked"


def test_a_re_granted_scope_stops_denying(p7_conn):
    # Revocation is forward-only, not permanent: a new grant puts the scope back and
    # the denial stops. The ledger half -- a token minted before the revocation still
    # consuming -- is Task 12's.
    append_event(p7_conn, event_type=CONSENT_REVOKED, subsystem=SUBSYSTEM,
                 component_version=COMPONENT, observed_at=LATER,
                 explanation=json.dumps({REVOKED_SCOPE_KEY: "Academics"}))
    assert policy_revoked_for(p7_conn, a_policy(), "Academics") is False


# --- 3. always_local_item ---------------------------------------------------

def test_always_local_item_translates_task_sevens_refusal():
    # §8.4: "Nothing in this set can be named as a releasable item kind." Task 7
    # refuses at construction; this builder turns that refusal into the gate's answer
    # rather than re-deciding which of the nine names are always-local.
    caught = AlwaysLocalRequested("GPS")
    denied = deny_always_local_item(caught, file_ids=("file-1",))
    assert denied.reason == "always_local_item"
    assert "GPS" in denied.explanation


# --- 4. unclassified -- the ordinary case -----------------------------------

def test_unclassified_is_the_ordinary_denial():
    # D2: no detector exists, so every real file lands here. §8.4: "classify data into
    # handling classes before LLM escalation" makes classification a PRECONDITION.
    assert unclassified_denies(locality="cloud",
                               local_calls_on_unclassified=True) is True
    denied = deny_unclassified(file_ids=("file-1",), locality="cloud",
                               completeness=None)
    assert denied.reason == "unclassified"


def test_absence_of_a_classification_never_resolves_to_public_low():
    # SPEC §1: "Absence of a classification resolves to `unreadable_unclassified`,
    # never to `public_low`." §8.6's rule it applies: "Cost exhaustion must never turn
    # into lower-quality automatic classification."
    denied = deny_unclassified(file_ids=("file-1",), locality="cloud",
                               completeness=None)
    assert "unreadable_unclassified" in denied.explanation
    assert "public_low" not in denied.explanation


def test_a_local_call_on_an_unclassified_file_has_no_default():
    # Open question 5, unanswered: "Does `unreadable_unclassified` permit a LOCAL
    # model call? ... which may block exactly the OCR-opaque screenshots §2.7 and §7.8
    # want a model to interpret." The parameter is required; P7 names no winner.
    with pytest.raises(TypeError):
        unclassified_denies(locality="local")
    assert unclassified_denies(locality="local",
                               local_calls_on_unclassified=True) is False
    assert unclassified_denies(locality="local",
                               local_calls_on_unclassified=False) is True


def test_unclassified_offers_a_remedy_the_user_can_actually_take():
    # §8.6 requires the UI to show "what has been deferred, and why", and §8.6's own
    # answer to an exhausted budget is to "leave the file or group in review rather
    # than guessing". A denial nobody can act on is a dead end.
    denied = deny_unclassified(file_ids=("file-1",), locality="cloud",
                               completeness=None)
    actions = {option.action for option in denied.remedy_options}
    assert "classify" in actions
    assert "defer" in actions


# --- 5. protected_records_template ------------------------------------------

def test_protected_records_template_denies_local_targets_too():
    # §7.3: Protected Records "should normally remain local-only and must not cause
    # filenames or content to be exposed in model prompts." No locality qualifier --
    # which is why this reason must outrank the cloud-only one.
    assert is_protected_records(PROTECTED_RECORDS_TEMPLATE) is True
    assert is_protected_records("Reading Inbox") is False
    for target in (LOCAL, CLOUD):
        denied = deny_protected_records_template(file_ids=("file-1",),
                                                 model_target=target)
        assert denied.reason == "protected_records_template"


def test_the_template_name_is_section_seven_threes_literal():
    assert PROTECTED_RECORDS_TEMPLATE == "Protected Records"


# --- 6. protected_cloud_target ----------------------------------------------

def test_protected_cloud_target_under_hybrid():
    # §8.4: "Hybrid mode: Sensitive files remain local". And SPEC §2's first protected
    # consequence: "not included in cloud-model prompts BY DEFAULT" -- the carve-out
    # that `cloud_assisted` plus an explicit grant satisfies.
    assert protected_cloud_denies(protected=True, locality="cloud",
                                  operation_mode="hybrid", scope="Academics",
                                  granted_scopes=("Academics",)) is True
    assert protected_cloud_denies(protected=True, locality="cloud",
                                  operation_mode="cloud_assisted", scope="Academics",
                                  granted_scopes=("Academics",)) is False
    assert protected_cloud_denies(protected=True, locality="cloud",
                                  operation_mode="cloud_assisted", scope="Taxes",
                                  granted_scopes=("Academics",)) is True
    assert protected_cloud_denies(protected=False, locality="cloud",
                                  operation_mode="hybrid", scope="Academics",
                                  granted_scopes=()) is False
    assert protected_cloud_denies(protected=True, locality="local",
                                  operation_mode="hybrid", scope="Academics",
                                  granted_scopes=()) is False
    denied = deny_protected_cloud_target(file_ids=("file-1",),
                                         operation_mode="hybrid", scope="Academics",
                                         evidence_refs=DETECTOR_KEYS)
    assert denied.reason == "protected_cloud_target"
    assert denied.evidence_refs == DETECTOR_KEYS


def test_the_corpus_area_is_the_callers_and_p7_defines_none():
    # Open question 3: "What is a 'corpus area'? ... Consent grants cannot be scoped
    # until this is named." The scope is a string the caller supplies; P7 compares it
    # and never resolves it.
    assert protected_cloud_denies(protected=True, locality="cloud",
                                  operation_mode="cloud_assisted",
                                  scope="whatever-the-caller-calls-it",
                                  granted_scopes=("whatever-the-caller-calls-it",)) \
        is False


# --- 7. whole_document_requested --------------------------------------------

def test_whole_document_requested_translates_task_sevens_refusal():
    # §8.4: "It should not send full documents where a short heading or OCR excerpt is
    # enough to resolve the question."
    caught = WholeDocumentRequested("span 0-4096 covers the whole unit")
    denied = deny_whole_document_requested(caught, file_ids=("file-1",))
    assert denied.reason == "whole_document_requested"
    assert "narrow_span" in {option.action for option in denied.remedy_options}


# --- 8. dossier_over_budget -- the backstop ---------------------------------

def test_dossier_over_budget_is_a_backstop_that_should_never_fire(p7_conn):
    """M9: P8 measures against the ceiling and runs §8.6's four-rung ladder BEFORE it
    calls the gate. A `dossier_over_budget` denial in a running pipeline is a P8
    defect to fix, not a normal outcome -- and the check stays because §8.6 forbids a
    prompt that "truncate[s] silently in a way that removes the decisive evidence"
    and the gate is the last place to catch a caller that skipped its ladder.
    Reachable in test; not reachable in a correct pipeline. Do not delete it.
    """
    assert CEILING_KEY in CEILING_KEYS
    set_ceiling(p7_conn, CEILING_KEY, 4000)
    assert over_dossier_ceiling(p7_conn, measured_tokens=9000) is True
    assert over_dossier_ceiling(p7_conn, measured_tokens=4000) is False
    denied = deny_dossier_over_budget(measured_tokens=9000, ceiling=4000,
                                      file_ids=("file-1",))
    assert denied.reason == "dossier_over_budget"
    ladder = {option.action for option in denied.remedy_options}
    assert ladder == {"summarize_deterministic_facts", "preserve_anchor_excerpts",
                      "split_the_task", "defer_the_decision"}


def test_an_unset_ceiling_cannot_deny(p7_conn):
    # `get_ceiling` returns None when nothing set it, which is the ordinary state.
    # P7 owns no number: SPEC Deferred puts "Numeric values for every ceiling"
    # outside this contract, and Task 21 asserts none appears in `src/privacy/`.
    assert over_dossier_ceiling(p7_conn, measured_tokens=10 ** 9) is False


def test_a_caller_cannot_raise_its_own_ceiling_by_echoing_a_larger_one(p7_conn):
    # `ModelCallRequest.max_dossier_tokens` is "the caller's echo of it (M9)". The
    # check reads P1's stored ceiling and never the echo.
    set_ceiling(p7_conn, CEILING_KEY, 4000)
    request = a_request(max_dossier_tokens=10 ** 6)
    assert request.max_dossier_tokens > 4000
    assert over_dossier_ceiling(p7_conn, measured_tokens=9000) is True


def test_the_measurement_is_the_callers_and_has_no_default(p7_conn):
    # P7 has no tokenizer and inventing one would invent a number -- the same
    # discipline as Task 8's injected redaction transform with no default.
    with pytest.raises(TypeError):
        over_dossier_ceiling(p7_conn)


# --- what every denial carries ----------------------------------------------

def test_every_denial_carries_a_non_empty_explanation():
    for reason, denied in all_eight().items():
        assert denied.reason == reason
        assert denied.explanation.strip(), reason


def test_every_denial_carries_at_least_one_remedy_option():
    # §8.6: the UI must show "what has been deferred, and why". A denial with no
    # legitimate alternative is a dead end the user cannot act on.
    for reason, denied in all_eight().items():
        assert denied.remedy_options, reason
        assert all(isinstance(option, RemedyOption)
                   for option in denied.remedy_options), reason


def test_a_denial_with_no_remedy_is_refused():
    with pytest.raises(MalformedDenial):
        deny("unclassified", explanation="nothing classified this file",
             remedy_options=(), evidence_refs=())


def test_a_denial_with_an_empty_explanation_is_refused():
    for blank in ("", "   "):
        with pytest.raises(MalformedDenial):
            deny("unclassified", explanation=blank,
                 remedy_options=(RemedyOption("defer", "leave it in review"),),
                 evidence_refs=())


def test_a_denial_with_an_out_of_vocabulary_reason_is_refused():
    # SPEC §1: "A value outside this set is a load error, not a fallback."
    with pytest.raises(OutOfVocabulary):
        deny("too_sensitive", explanation="made up",
             remedy_options=(RemedyOption("defer", "leave it in review"),),
             evidence_refs=())


def test_denied_carries_no_audit_id_and_no_content():
    # `Denied` is the gate's answer, not its record. The audit_id is reachable through
    # `audit_records_for`; putting it on the branch would invite a caller to treat the
    # answer as the log.
    from dataclasses import fields
    names = {field.name for field in fields(Denied)}
    assert names == {"reason", "explanation", "remedy_options", "evidence_refs"}


def test_no_two_reasons_share_one_remedy_list():
    # Proof that the remedies were authored per reason rather than defaulted from one
    # list. There is no REMEDY_ACTIONS vocabulary: §8.6 names four ladder rungs for one
    # situation and §8.4 names four consent options for another, and one enumeration
    # over both would invent a fifth thing no section states.
    lists = [tuple(sorted(option.action for option in denied.remedy_options))
             for denied in all_eight().values()]
    assert len(set(lists)) == len(lists)


# --- the audit record every denial appends ----------------------------------

def a_denial_record(conn, file_id, denied, *, classification=None, **over) -> int:
    base = dict(request=a_request(target=Target(file_ids=(file_id,), group_id=None)),
                policy=a_policy(), classification=classification,
                content_hashes=(get_file(conn, file_id)["content_hash"],),
                user_id=None, component_version=COMPONENT, observed_at=FIXED_CLOCK)
    base.update(over)
    return record_denial(conn, denied, **base)


def test_every_denial_appends_a_model_release_denied_event(p7_conn, file_id):
    # SPEC §7: "Denials and consent requests are also appended", on the strength of
    # §8.2's "Every significant event affecting a file".
    for reason, denied in all_eight().items():
        audit_id = a_denial_record(p7_conn, file_id, denied)
        row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                              (audit_id,)).fetchone()
        assert row["event_type"] == MODEL_RELEASE_DENIED, reason
        assert row["subsystem"] == "P7", reason
        assert json.loads(row["explanation"])["reason"] == reason


def test_the_denial_record_says_unreadable_unclassified(p7_conn, file_id):
    # D2: `Unreadable or unclassified` is a GATE OUTCOME. This is the field it lives
    # in -- `AuditRecord.file_sensitivity`, on the release decision.
    audit_id = a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    assert audit_record(p7_conn, audit_id).file_sensitivity == "unreadable_unclassified"


def test_a_denial_writes_no_classification(p7_conn, file_id):
    # C4: "a gate that also wrote would be doing two jobs." D2: the outcome "lives on
    # the release decision and never in that column, so 'nothing has looked' can never
    # be read as 'this file carries nothing'." One assertion, both rulings.
    before = get_file(p7_conn, file_id)["sensitivity_state"]
    a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    assert get_file(p7_conn, file_id)["sensitivity_state"] == before


def test_a_denial_records_the_class_a_classified_file_actually_has(p7_conn, file_id):
    classified = ClassificationRecord(
        file_id=file_id, content_hash=get_file(p7_conn, file_id)["content_hash"],
        handling_class="sensitive_personal", protected=True, basis="detector",
        evidence_refs=DETECTOR_KEYS, reliability_state="validated",
        observed_at=FIXED_CLOCK)
    audit_id = a_denial_record(p7_conn, file_id,
                               all_eight()["protected_cloud_target"],
                               classification=classified)
    assert audit_record(p7_conn, audit_id).file_sensitivity == "sensitive_personal"


def test_the_denial_record_names_no_released_content(p7_conn, file_id):
    # Nothing left the device, so `excerpts_included` is empty and
    # `redaction_applied` is false. A denial that listed excerpts would be a record of
    # a release that did not happen.
    audit_id = a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    record = audit_record(p7_conn, audit_id)
    assert record.outcome == "denied"
    assert record.release_id is None
    assert record.excerpts_included == ()
    assert record.redaction_applied is False


def test_the_denial_record_carries_every_audit_field(p7_conn, file_id):
    # SPEC §7's nineteen names are Task 10's; this asserts the denial path fills the
    # published tuple rather than a subset a later reader would have to guess at.
    audit_id = a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    record = audit_record(p7_conn, audit_id)
    for name in AUDIT_FIELDS:
        assert hasattr(record, name), name


def test_a_group_scoped_denial_names_all_its_files(p7_conn, file_id):
    # `events` has one `file_id` column. The column carries the id only when the call
    # is about exactly one file, so `WHERE file_id = ?` never over-reports; the full
    # tuple is always in the explanation. Task 10's `audit_records_for(file_id=...)`
    # must read the explanation too, or Task 15's `prior_releases` under-reports.
    request = a_request(target=Target(file_ids=(file_id, "file-2"), group_id="group-1"))
    audit_id = a_denial_record(p7_conn, file_id, all_eight()["unclassified"],
                               request=request)
    row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["file_id"] is None
    assert json.loads(row["explanation"])["file_ids"] == [file_id, "file-2"]


def test_a_denial_appends_exactly_one_event(p7_conn, file_id):
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    a_denial_record(p7_conn, file_id, all_eight()["unclassified"])
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before + 1
