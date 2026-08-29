# tests/p6/test_p6_fields.py
"""§3.12's closed catalogue: the LLM may create values, never fields.

Done-means 2 and the negative half of Done-means 3.
"""
import re

import pytest

from evidence_shape.vocabulary import NotInVocabulary

from facts.fields import (
    DOMAIN_FIELDS, FIELDS_COLUMNS, FIELD_ROWS, FIELD_SCOPES, ROLE_FIELDS,
    UNIVERSAL_FIELDS, VALUE_KINDS, FieldNotInCatalogue, create_fields,
    fields_in_scope, get_field,
)

KEYS = tuple(row.field_key for row in FIELD_ROWS)


def test_the_catalogue_is_fifty_six_rows_with_no_duplicate_key():
    # `60` §4: "37 live + 19 = 56." J-1 widened the recognised schemas 10 -> 23 and §4
    # minted nineteen keys for them; the live thirty-seven keep their positions.
    assert len(FIELD_ROWS) == 56
    assert len(set(KEYS)) == 56


def test_the_catalogue_is_exactly_these_keys_and_nothing_else():
    # §3.11's six sentences + §3.9's download session + §3.8's four roles +
    # capture_date (Done-means 2(b)), minus sensitivity_status (NEEDS-JOSEPH C5).
    assert set(KEYS) == {
        # universal (§3.11, five of six — see C5 below)
        "file_type", "creation_date", "language", "duplicate_family", "version_family",
        # universal (§3.9, P6's one recorded addition)
        "download_session",
        # academic (§3.11)
        "school", "term", "subject", "instructor", "work_type",
        # college applications (§3.11)
        "target_university", "application_cycle", "application_document_type", "purpose",
        # research (§3.11)
        "project", "stage", "artifact_type", "lab", "venue",
        # finance (§3.11)
        "institution", "account_type", "tax_year", "record_type",
        # photos (§3.11), plus §3.2's capture_date
        "capture_year", "event", "location", "people", "camera_information",
        "media_type", "capture_date",
        # code (§3.11) — project and artifact_type are declared under research
        "repository", "programming_language",
        # §3.8's four role fields
        "authored_by", "target_school", "our_firm", "client",
        # `60` §4's eighteen, grouped by the scope that DECLARES each
        "recruiting_cycle", "employer", "target_employer", "job_title",  # career (J-2,
                                                                    # J-3, §8.1)
        "organization", "record_period", "supplier", "issuing_body",  # business_ops
        "property",                                                # construction_property
        "design_item",                                             # engineering (M10)
        "site", "asset", "product",                                # manufacturing
        "authorization",                                           # resource_ops (H8)
        "consignment",                                             # logistics (B2)
        "people_cycle", "workforce_unit",                          # hr (J-2, J-5)
        "subject_of_record",                                       # law_practice
        "account_holder",                                          # finance (M13)
    }


def test_the_three_published_groups_partition_the_catalogue():
    referenced = {key for keys in DOMAIN_FIELDS.values() for key in keys}
    assert set(UNIVERSAL_FIELDS) | set(ROLE_FIELDS) | referenced == set(KEYS)
    assert not set(UNIVERSAL_FIELDS) & set(ROLE_FIELDS)


def test_every_key_is_snake_case():
    # D6: "every stored field key is snake_case".
    for key in KEYS:
        assert re.fullmatch(r"[a-z][a-z0-9_]*", key), key


def test_the_academic_key_is_subject_and_there_is_no_course_row():
    # D6, ratified 2026-08-21. §3.2: "the system can create facts such as
    # subject = BUSIB 4300". §3.11's word "course" is prose for the same field and
    # survives inside quotations only. Two spellings would be two join handles.
    assert "subject" in KEYS
    assert "course" not in KEYS
    assert "course_code" not in KEYS
    assert DOMAIN_FIELDS["academic"] == ("school", "term", "subject", "instructor",
                                         "work_type")
    assert all(row.display_name != "course" for row in FIELD_ROWS)


def test_sensitivity_status_has_no_row_because_C5_is_open():
    # NEEDS-JOSEPH C5. P7's SPEC Contract-in wants `sensitivity` as a first-class
    # universal field; D2 makes P7's ClassificationRecord authoritative and
    # `files.sensitivity_state` its projection; round 1 F-2 found the field has no
    # producer. The brief: "Create no such row either way."
    #
    # This is knowingly at odds with SPEC Done-means 2 ("all six universal fields").
    # Do not close it by adding the row.
    for spelling in ("sensitivity_status", "sensitivity", "sensitivity_state"):
        assert spelling not in KEYS
    assert len([k for k in UNIVERSAL_FIELDS if k != "download_session"]) == 5


def test_document_type_is_never_a_key():
    # The design's generic word (twelve uses) for whichever field the active domain
    # declares. The specific ones are keys; the generic one is not.
    assert "document_type" not in KEYS
    assert "document type" not in KEYS
    assert "application_document_type" in KEYS
    assert "artifact_type" in KEYS


def test_jurisdiction_is_a_value_and_never_a_field_name():
    # D4: "jurisdiction is a value, never a field name and never a destination
    # dimension."
    assert not [k for k in KEYS if "jurisdiction" in k]


def test_identity_medical_and_legal_still_have_no_field_rows_and_career_now_does():
    # THE REVERSAL THIS TEST ANTICIPATED. Its own words: "this asserts the catalogue's
    # contents today. It does NOT assert that the contents can never change — a later
    # deliberate reversal of S3 is a decision, not a regression." `60` J-1 and J-3 are
    # that decision, and D1's deferral said so too: "Career is owed before P10."
    #
    # `00`:70's Career template words are "company → role or recruiting cycle →
    # document type". `recruiting_cycle` is now a key, on the `00` spelling (J-2).
    # `role` is now a key too, under its stored spelling `job_title` (`60` §8.1:
    # "`role` is the middle level of `00`'s own career template"), so `role` survives
    # as an alias and never as a second key. `company` is still not a key: it folds to
    # `employer` / `target_employer` / `organization` by role.
    for present in ("recruiting_cycle", "employer", "target_employer", "job_title"):
        assert present in KEYS
    for absent in ("company", "role",
                   "resume_version", "passport_number", "identity_document_type",
                   "patient", "diagnosis", "medical_record_type",
                   "matter", "case_number", "counterparty"):
        assert absent not in KEYS
    # The three §3.15 safety domains are still field-less, which is what keeps
    # "field-less" a live category rather than an emptied one.
    assert not [key for key in KEYS
                if get_row(key).scope in ("identity", "medical", "legal")]


def test_the_four_3_8_role_fields_exist_and_d9_splits_destination_eligibility():
    # §3.8: "distinct facets, such as authored_by and target_school, or our_firm and
    # client" — the design's own spelling, underscores included.
    #
    # D9: authorship is never destination-eligible; target_school and client ARE.
    # Round 1's F-1: Done-means 13 and 22 both require `authored_by` to exist, so a
    # catalogue without these four made two of the SPEC's own Done-means unwritable.
    assert ROLE_FIELDS == ("authored_by", "target_school", "our_firm", "client")
    for key in ROLE_FIELDS:
        row = next(r for r in FIELD_ROWS if r.field_key == key)
        assert row.scope == "universal", key
    assert get_row("authored_by").destination_eligible is False
    assert get_row("our_firm").destination_eligible is False
    assert get_row("target_school").destination_eligible is True
    assert get_row("client").destination_eligible is True


def test_the_application_target_is_destination_eligible_under_its_3_11_spelling():
    # §3.11's College-applications row names "target university" as a dimension, so
    # target_university IS eligible. target_school is §3.8's spelling of the same
    # concept, held as a key referenced by no domain until the ROSTER NEEDS-JOSEPH
    # about folding the two is answered.
    assert get_row("target_university").destination_eligible is True
    assert "target_school" not in DOMAIN_FIELDS["college_applications"]


def test_capture_date_capture_year_and_creation_date_are_three_fields():
    # Brief, field-naming rulings: capture_date is §3.2's EXIF-derived fact
    # ("capture date = 2026-07-17 is the file fact derived from it"); capture_year is
    # §3.11's Photos destination dimension; creation_date is what §3.2 separates both
    # from by name.
    assert {"capture_date", "capture_year", "creation_date"} <= set(KEYS)
    assert get_row("capture_date").value_kind == "date"
    assert get_row("capture_date").destination_eligible is False
    assert get_row("capture_year").destination_eligible is True
    assert get_row("creation_date").scope == "universal"
    assert get_row("capture_date").scope == "photos"


def test_the_photos_scope_carries_seven_rows_and_the_reason_is_recorded():
    # §3.11 names six. capture_date is the seventh: the design gives it no scope,
    # FIELD_SCOPES is closed at seven members, and its only producer is an EXIF
    # DateTimeOriginal observation (Done-means 5), which arrives only for an image.
    assert DOMAIN_FIELDS["photos"] == ("capture_year", "event", "location", "people",
                                       "camera_information", "media_type",
                                       "capture_date")


def test_download_session_is_universal_and_never_a_folder_level():
    # §3.9: "It may be supported more weakly by a tightly bounded download session."
    # A session is a purpose clue and a review aid, never proof of topic.
    row = get_row("download_session")
    assert row.scope == "universal"
    assert row.destination_eligible is False
    assert "download_session" in UNIVERSAL_FIELDS


def test_the_twenty_one_scopes_open_with_the_specs_seven_and_every_row_uses_one():
    # `60` J-1: adoption APPENDS. The SPEC's seven are still the first seven members,
    # in the SPEC's order, so nothing that read this tuple positionally changed meaning.
    assert FIELD_SCOPES[:7] == ("universal", "academic", "college_applications",
                                "research", "finance", "photos", "code")
    assert len(FIELD_SCOPES) == 21
    for row in FIELD_ROWS:
        assert row.scope in FIELD_SCOPES, row.field_key
        assert row.value_kind in VALUE_KINDS, row.field_key


def test_project_and_artifact_type_are_one_row_each_referenced_by_two_domains():
    # canonical_fields.json's own model: "One global table: schemas REFERENCE these
    # keys and declare no private spellings." Two rows would be two join handles for
    # one concept — the tie-break rule's exact failure.
    # `research` gains `institution` under `60` H9 (per `48` §2): nonprofit's row
    # warned that without a funder role its strongest node — restricted money with
    # strings — has no key "and a template author will mint one", and `48`'s answer was
    # to declare the canonical key on `research` and `nonprofit` rather than mint
    # `sponsor`. It is one row, declared at `finance`, now referenced by three schemas.
    assert DOMAIN_FIELDS["research"] == ("project", "stage", "artifact_type", "lab",
                                         "venue", "institution")
    assert DOMAIN_FIELDS["code"] == ("project", "repository", "programming_language",
                                     "artifact_type")
    assert get_row("institution").scope == "finance"
    assert len([r for r in FIELD_ROWS if r.field_key == "institution"]) == 1
    assert get_row("project").scope == "research"
    assert get_row("artifact_type").scope == "research"
    assert len([r for r in FIELD_ROWS if r.field_key == "project"]) == 1


def test_no_normalizer_and_no_multiplicity_is_answered_anywhere():
    # Per-field normalizers are a Deferred SPEC row, and round 4's C-5 has P6 and P8
    # each handing `normalize(field, raw_value)` to the other. OQ6 (multiplicity) is
    # Joseph's. Both columns exist so an answer has somewhere to land.
    assert all(row.normalizer_id is None for row in FIELD_ROWS)
    assert all(row.multiplicity is None for row in FIELD_ROWS)


def test_the_module_publishes_no_way_to_add_a_field_at_runtime(p6_conn):
    # §3.12: "The system may create new values when it sees a new course, project,
    # company, university, or event, but it should not invent new fields
    # automatically." §3.5: "The LLM is not allowed to invent a new fact schema,
    # create an unsupported field, or make a free-form filing decision."
    #
    # Runtime introspection of the module namespace, not a source-text search: a text
    # search matches comments and docstrings.
    import facts.fields as module
    forbidden = ("add_field", "create_field", "register_field", "new_field",
                 "ensure_field", "upsert_field")
    assert not [n for n in vars(module) if n in forbidden]
    assert not [n for n, v in vars(module).items()
                if callable(v) and n.lower().endswith("_field")
                and n not in ("get_field",)]


def test_an_unknown_field_key_raises_rather_than_creating_a_row(p6_conn):
    before = p6_conn.execute("SELECT count(*) FROM fields").fetchone()[0]
    with pytest.raises(FieldNotInCatalogue):
        get_field(p6_conn, "vibe")
    with pytest.raises(FieldNotInCatalogue):
        get_field(p6_conn, "course")          # D6: prose, not a key
    with pytest.raises(FieldNotInCatalogue):
        get_field(p6_conn, "sensitivity_status")   # C5: open, so no row
    assert p6_conn.execute("SELECT count(*) FROM fields").fetchone()[0] == before


def test_create_fields_loads_the_authored_table_and_is_idempotent(p6_conn):
    # `p6_conn` has already called it once.
    assert p6_conn.execute("SELECT count(*) FROM fields").fetchone()[0] == 56
    create_fields(p6_conn)
    create_fields(p6_conn)
    assert p6_conn.execute("SELECT count(*) FROM fields").fetchone()[0] == 56


def test_the_stored_row_carries_exactly_the_specs_columns(p6_conn):
    # Read from the database, so a future column fails the test the day it is added.
    # NOTE for Task 4: `destination_eligible` contains the substring "destination".
    # §3.14's forbidden-substring guard is for `file_facts` and `unresolved`; running
    # it against `fields` would fail on a column §3.8 requires.
    stored = tuple(r[1] for r in p6_conn.execute("PRAGMA table_info(fields)"))
    assert stored == FIELDS_COLUMNS
    assert FIELDS_COLUMNS == ("field_key", "display_name", "scope",
                              "value_kind", "normalizer_id", "destination_eligible",
                              "multiplicity")
    # brief §17: one concept, one name. A second identifier column holding the same
    # string is the defect this rule exists to stop, so its ABSENCE is asserted --
    # not the equality of two columns, which is what an earlier draft tested.
    assert "field_id" not in stored, (
        "`field_id` was the skeleton's name for the field key; brief §17 ruled the "
        "column is `field_key` and holds the key. Two columns is not the fix.")


def test_the_row_identity_is_the_field_key(p6_conn):
    # SPEC: "field_key — stable identifier". Task 3's `values.field_key` joins on it.
    # One identity, one name.
    row = get_field(p6_conn, "subject")
    assert row["field_key"] == "subject"
    assert row["display_name"] == "subject"
    assert row["scope"] == "academic"
    assert row["value_kind"] == "string"
    assert row["normalizer_id"] is None
    assert row["multiplicity"] is None
    assert row["destination_eligible"] == 1


def test_fields_in_scope_returns_the_rows_declared_at_that_scope(p6_conn):
    # `fields_in_scope` answers "declared here"; `DOMAIN_FIELDS` answers "referenced
    # by this §3.11 sentence". They differ for exactly the two shared keys.
    assert [r["field_key"] for r in fields_in_scope(p6_conn, "code")] == [
        "repository", "programming_language"]
    assert [r["field_key"] for r in fields_in_scope(p6_conn, "career")] == [
        "employer", "target_employer", "recruiting_cycle", "job_title"]
    # `account_holder` is the fifth: `60` M13 / `49` §4.1. It was moved out of
    # `finance.fields[]` mid-session and fell through, and `finance` is a live schema,
    # so the omission was a SHIPPING schema losing a field with no replacement.
    assert [r["field_key"] for r in fields_in_scope(p6_conn, "finance")] == [
        "institution", "account_type", "tax_year", "record_type", "account_holder"]
    assert [r["field_key"] for r in fields_in_scope(p6_conn, "universal")] == [
        "file_type", "creation_date", "language", "duplicate_family",
        "version_family", "download_session",
        "authored_by", "target_school", "our_firm", "client"]
    assert len(fields_in_scope(p6_conn, "photos")) == 7


def test_fields_in_scope_refuses_a_scope_outside_the_twenty_one(p6_conn):
    # `career` has LEFT this list (J-3 declares its fields). The three §3.15 safety
    # domains have not: `60` §5 keeps them field-less by PR-6, so asking for their rows
    # is still a refusal and not an empty list.
    for absent in ("identity", "medical", "legal", "Universal", "travel", "astrology"):
        with pytest.raises(NotInVocabulary):
            fields_in_scope(p6_conn, absent)
    assert fields_in_scope(p6_conn, "career")


def test_every_destination_eligible_flag_round_trips_as_a_boolean(p6_conn):
    for row in FIELD_ROWS:
        stored = get_field(p6_conn, row.field_key)
        assert bool(stored["destination_eligible"]) is row.destination_eligible


def get_row(field_key):
    return next(r for r in FIELD_ROWS if r.field_key == field_key)
