# tests/p7/test_p7_audit.py
"""§8.4's consent-aware audit record, as one events row plus canonical JSON.

The two properties that matter: the field list IS SPEC §7's, name for name, so a
dropped field is a red test rather than a quiet omission; and the record can
reconstruct what left the device, proved by re-running the resolver over the stored
pairs rather than by asserting that a string was kept.
"""
import dataclasses
import json

import pytest

from database_agent.events import EVENT_FIELDS, MalformedEvent, append_event
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.locator import parse_locator, serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run, record_text_unit
from evidence_shape.text_units import TextUnit

from privacy.audit import (
    AUDIT_FIELDS, CARRIED_FIELDS, COLUMN_FIELDS, EXPLANATION_FIELDS,
    OUTCOME_EVENT_TYPES, AuditRecord, MalformedAudit, append_audit, audit_extra,
    audit_record, audit_records_for,
)
from privacy.authorship import (
    CONSENT_REQUESTED, MODEL_RELEASE, MODEL_RELEASE_DENIED, SUBSYSTEM,
)
from privacy.resolve import materialise
from privacy.vocabulary import AUDIT_OUTCOMES

COMPONENT = "0.1.0"
FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
CONTENT_HASH = "a" * 64
PAGE = (Segment(kind="page", index=2),)
BODY = "Passport number 992-33-1188 issued 2019."
LOCATION = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
SPAN = serialize_locator(LOCATION)
KEY = observation_key(content_hash=CONTENT_HASH, extractor_name="pdf_text",
                      locator=SPAN, raw_value="992-33-1188")
CLOUD = {"locality": "cloud", "model_id": "acme-large", "provider": "Acme"}
LOCAL = {"locality": "local", "model_id": "llama-local", "provider": "self-hosted"}


def a_record(**over) -> AuditRecord:
    base = dict(
        authorizing_policy="policy-1", file_sensitivity="sensitive_personal",
        excerpts_included=((KEY, SPAN),), redaction_applied=True, model=CLOUD,
        prompt_fingerprint="fp-1", audit_id=None, release_id="release-1",
        observed_at=FIXED_CLOCK, stage="grouping", file_ids=("file-1",),
        group_id=None, content_hashes=(CONTENT_HASH,), operation_mode="cloud_assisted",
        policy_version="policy-1", plan_version="plan-1", outcome="released",
        file_id="file-1", content_hash=CONTENT_HASH)
    base.update(over)
    return AuditRecord(**base)


def go(conn, **over) -> int:
    return append_audit(conn, a_record(**over), author=SUBSYSTEM,
                        component_version=COMPONENT)


class Item:
    """Task 7's item shape, as Task 9 reads it."""

    def __init__(self, observation_key, span):
        self.observation_key = observation_key
        self.span = span


@pytest.fixture()
def excerpt(p7_conn):
    """A real observation, so the reconstruction test resolves against real storage."""
    create_evidence_schema(p7_conn)
    record_run(p7_conn, ExtractionRun(
        run_id="run-1", file_id="file-1", content_hash=CONTENT_HASH,
        extractor_name="pdf_text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=FIXED_CLOCK, observation_count=1))
    record_text_unit(p7_conn, TextUnit(run_id="run-1", container_path=PAGE, text=BODY))
    record_observation(p7_conn, Observation(
        file_id="file-1", content_hash=CONTENT_HASH, extractor_name="pdf_text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value="992-33-1188", location=LOCATION, occurrence_count=1,
        observed_at=FIXED_CLOCK, reliability="direct", run_id="run-1",
        context_before="Passport number ", context_after=" issued 2019.",
        context_truncated=False))
    return p7_conn


# --- SPEC §7's field list ------------------------------------------------------

def test_audit_fields_are_spec_7s_nineteen_name_for_name():
    # §8.4's six required, then §7's carried block, then §8.2's two per-file columns.
    assert AUDIT_FIELDS == (
        "authorizing_policy", "file_sensitivity", "excerpts_included",
        "redaction_applied", "model", "prompt_fingerprint",
        "audit_id", "release_id", "observed_at", "stage", "file_ids", "group_id",
        "content_hashes", "operation_mode", "policy_version", "plan_version",
        "outcome", "file_id", "content_hash")
    assert len(AUDIT_FIELDS) == 19


def test_the_six_84_requires_are_all_present():
    # "what policy authorized the call, whether the file was sensitive, which
    # excerpts were included, whether values were redacted, which model received the
    # data, and the prompt fingerprint."
    assert set(AUDIT_FIELDS[:6]) == {
        "authorizing_policy", "file_sensitivity", "excerpts_included",
        "redaction_applied", "model", "prompt_fingerprint"}


def test_the_three_carried_fields_are_outside_the_nineteen():
    assert CARRIED_FIELDS == ("user_id", "consent_request_id", "redaction_manifest")
    assert not set(CARRIED_FIELDS) & set(AUDIT_FIELDS)


def test_the_record_is_exactly_the_nineteen_plus_the_three():
    names = tuple(field.name for field in dataclasses.fields(AuditRecord))
    assert names == AUDIT_FIELDS + CARRIED_FIELDS


def test_the_split_between_column_and_explanation_is_total_and_disjoint():
    assert COLUMN_FIELDS == ("file_id", "content_hash", "prompt_fingerprint",
                             "observed_at", "user_id")
    assert set(COLUMN_FIELDS) <= set(EVENT_FIELDS), (
        "P7 adds no column to `events` and does not ask P1 to")
    assert not set(COLUMN_FIELDS) & set(EXPLANATION_FIELDS)
    assert set(COLUMN_FIELDS) | set(EXPLANATION_FIELDS) | {"audit_id"} == set(
        AUDIT_FIELDS + CARRIED_FIELDS)
    assert len(EXPLANATION_FIELDS) == 16


def test_the_record_is_frozen(p7_conn):
    with pytest.raises(dataclasses.FrozenInstanceError):
        a_record().outcome = "denied"


# --- one events row, and the JSON explanation ----------------------------------

def test_the_five_column_fields_land_in_their_columns(p7_conn):
    audit_id = go(p7_conn)
    row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["file_id"] == "file-1"
    assert row["content_hash"] == CONTENT_HASH
    assert row["prompt_fingerprint"] == "fp-1"
    assert row["observed_at"] == FIXED_CLOCK
    assert row["user_id"] is None


def test_the_rest_land_in_explanation_as_canonical_json(p7_conn):
    audit_id = go(p7_conn)
    row = p7_conn.execute("SELECT explanation FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    payload = json.loads(row["explanation"])
    assert set(payload) == set(EXPLANATION_FIELDS)
    assert payload["authorizing_policy"] == "policy-1"
    assert payload["model"] == CLOUD
    # canonical: sorted keys, so two identical records serialise identically.
    assert row["explanation"] == json.dumps(payload, sort_keys=True,
                                            separators=(",", ":"), ensure_ascii=False)


def test_p7_authors_and_p1_writes(p7_conn):
    audit_id = go(p7_conn)
    row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["subsystem"] == "P7"
    assert row["component_version"] == COMPONENT


def test_a_foreign_author_is_refused(p7_conn):
    # M8: the acting part authors. `privacy` writes "P7" in exactly one place and
    # this entry point is not a second one.
    with pytest.raises(MalformedAudit):
        append_audit(p7_conn, a_record(), author="P8", component_version=COMPONENT)


def test_p1_would_reject_an_eighteenth_column(p7_conn):
    # The constraint the JSON shape exists to satisfy, asserted against P1 rather
    # than quoted: none of §7's own field names is a column.
    with pytest.raises(MalformedEvent):
        append_event(p7_conn, event_type=MODEL_RELEASE, subsystem="P7",
                     component_version=COMPONENT, observed_at=FIXED_CLOCK,
                     explanation="{}", release_id="release-1")


# --- the round trip ------------------------------------------------------------

def test_the_record_round_trips(p7_conn):
    audit_id = go(p7_conn)
    assert audit_record(p7_conn, audit_id) == a_record(audit_id=audit_id)


def test_tuples_come_back_as_tuples(p7_conn):
    # JSON has one sequence type; the record has frozen fields that get compared.
    recovered = audit_record(p7_conn, go(p7_conn))
    assert recovered.excerpts_included == ((KEY, SPAN),)
    assert recovered.content_hashes == (CONTENT_HASH,)
    assert recovered.file_ids == ("file-1",)


def test_an_unknown_audit_id_raises(p7_conn):
    with pytest.raises(KeyError):
        audit_record(p7_conn, 999999)


# --- the ordering guarantee ----------------------------------------------------

def test_the_returned_id_is_already_selectable(p7_conn):
    # SPEC §6: "the audit record is appended ... BEFORE `Released` is returned."
    # `append_event` returns `cursor.lastrowid`, so an `audit_id` cannot exist
    # before its row does. There is no interval in which content is releasable and
    # unaudited, and the property is structural rather than a discipline.
    audit_id = go(p7_conn)
    (count,) = p7_conn.execute("SELECT count(*) FROM events WHERE event_id = ?",
                               (audit_id,)).fetchone()
    assert count == 1


def test_the_returned_id_is_the_rows_event_id(p7_conn):
    audit_id = go(p7_conn)
    row = p7_conn.execute("SELECT event_id FROM events ORDER BY event_id DESC "
                          "LIMIT 1").fetchone()
    assert row["event_id"] == audit_id


def test_audit_ids_are_monotonic(p7_conn):
    first, second = go(p7_conn), go(p7_conn, release_id="release-2")
    assert second > first


# --- outcomes, and what each one appends ---------------------------------------

def test_each_outcome_maps_to_its_own_p7_event_type(p7_conn):
    assert OUTCOME_EVENT_TYPES == {
        "released": MODEL_RELEASE,
        "denied": MODEL_RELEASE_DENIED,
        "consent_requested": CONSENT_REQUESTED}
    assert tuple(OUTCOME_EVENT_TYPES) == AUDIT_OUTCOMES


def test_a_denial_is_recorded_too(p7_conn):
    # §8.2: "Every significant event affecting a file"; §8.6: the UI must show "what
    # has been deferred, and why".
    audit_id = go(p7_conn, outcome="denied", release_id=None)
    row = p7_conn.execute("SELECT event_type FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["event_type"] == MODEL_RELEASE_DENIED


def test_a_consent_request_is_recorded_with_its_id(p7_conn):
    # Done-means 7's join key. Task 14 adds the field; the record carries it.
    audit_id = go(p7_conn, outcome="consent_requested", release_id=None,
                  consent_request_id="consent-1", user_id="joseph")
    row = p7_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (audit_id,)).fetchone()
    assert row["event_type"] == CONSENT_REQUESTED
    assert row["user_id"] == "joseph"
    assert json.loads(row["explanation"])["consent_request_id"] == "consent-1"


def test_a_local_model_call_is_audited(p7_conn):
    # §8.4: "Every model call should be recorded" -- no exemption is named, and
    # Open question 6 (is a local call also a CONSENT event?) stays open.
    audit_id = go(p7_conn, model=LOCAL, operation_mode="local_model")
    assert audit_record(p7_conn, audit_id).model == LOCAL


def test_an_outcome_outside_the_vocabulary_is_refused(p7_conn):
    with pytest.raises(MalformedAudit):
        go(p7_conn, outcome="probably_fine")


def test_an_empty_stage_is_refused(p7_conn):
    # §8.5 requires per-stage decomposition; an unattributed call cannot be
    # decomposed later.
    with pytest.raises(MalformedAudit):
        go(p7_conn, stage="")


# --- the readers ---------------------------------------------------------------

def test_records_are_found_by_file_by_release_and_by_consent_request(p7_conn):
    first = go(p7_conn)
    second = go(p7_conn, release_id="release-2", file_id="file-2",
                file_ids=("file-2",))
    third = go(p7_conn, outcome="consent_requested", release_id=None,
               consent_request_id="consent-1")
    assert [r.audit_id for r in audit_records_for(p7_conn, file_id="file-1")] == [
        first, third]
    assert [r.audit_id for r in audit_records_for(p7_conn, release_id="release-2")] == [
        second]
    assert [r.audit_id for r in
            audit_records_for(p7_conn, consent_request_id="consent-1")] == [third]


def test_the_readers_return_records_in_append_order(p7_conn):
    ids = [go(p7_conn), go(p7_conn, release_id="release-2"),
           go(p7_conn, release_id="release-3")]
    assert [r.audit_id for r in audit_records_for(p7_conn, file_id="file-1")] == ids


def test_the_readers_see_only_p7s_three_event_types(p7_conn):
    # The log is shared (B5). A `discovery` event on the same file is not an audit
    # record and must not appear in one.
    go(p7_conn)
    append_event(p7_conn, event_type="discovery", subsystem="P3",
                 component_version="0.1.0", observed_at=FIXED_CLOCK,
                 explanation="a scan saw it", file_id="file-1")
    assert len(audit_records_for(p7_conn, file_id="file-1")) == 1


def test_no_filter_at_all_is_refused(p7_conn):
    # Returning the whole log for a call that named nothing is how a "show me the
    # releases for this file" screen quietly becomes "show me every release".
    go(p7_conn)
    with pytest.raises(MalformedAudit):
        audit_records_for(p7_conn)


def test_extra_carries_what_spec_7_has_no_field_for(p7_conn):
    # §8.6: the product must show "what has been deferred, and why". A denial's
    # reason has no §7 field, and Tasks 13 and 14 write theirs through here.
    audit_id = append_audit(
        p7_conn, a_record(outcome="denied", release_id=None), author=SUBSYSTEM,
        component_version=COMPONENT,
        extra={"reason": "unclassified", "remedy_options": ["classify and retry"]})
    assert audit_extra(p7_conn, audit_id) == {
        "reason": "unclassified", "remedy_options": ["classify and retry"]}
    # and the nineteen are untouched by it
    assert audit_record(p7_conn, audit_id).outcome == "denied"


def test_extra_may_not_shadow_a_spec_7_field(p7_conn):
    # A second value under one name is how a record starts disagreeing with itself,
    # in a log nothing may ever update.
    with pytest.raises(MalformedAudit):
        append_audit(p7_conn, a_record(), author=SUBSYSTEM,
                     component_version=COMPONENT,
                     extra={"outcome": "not really released"})


# --- what left the device ------------------------------------------------------

def test_excerpts_included_holds_pairs_and_not_a_second_copy_of_the_text(excerpt):
    audit_id = go(excerpt)
    payload = json.loads(excerpt.execute(
        "SELECT explanation FROM events WHERE event_id = ?",
        (audit_id,)).fetchone()["explanation"])
    assert payload["excerpts_included"] == [[KEY, SPAN]]
    assert "992-33-1188" not in json.dumps(payload)
    assert BODY not in json.dumps(payload)


def test_the_stored_pairs_reconstruct_what_left_the_device(excerpt):
    # SPEC §7: "a record that cannot reconstruct the released payload from local
    # storage fails §8.4's stated purpose." Proved by re-running the resolver over
    # the stored pairs, which is why Task 9's `span` is P4's canonical locator and
    # not an opaque offset.
    recovered = audit_record(excerpt, go(excerpt))
    for key, span in recovered.excerpts_included:
        again = materialise(excerpt, Item(key, parse_locator(span).text_span))
        assert again.value == "992-33-1188"
        assert again.span == span
