# tests/p6/test_p6_vocabulary_adoption.py
"""`planning/60-VOCABULARY-RULINGS.md`, adopted into `src/facts`.

`60` is the contract. It widens `SCHEMA_IDS` 10 -> 23 (J-1), mints 18 canonical keys
(§4), declares the per-schema field sets for all 23 (§5), fixes two alias collisions
(§3 H7), writes six reciprocal `role_split` pairs, and requires five `notes`
discriminators (H6, M10, M12, B3, J-2).

Every guard here has its negative twin, because the positive half of a property cannot
detect substitution: "reciprocity holds" is satisfied by a table with no pairs in it.
"""
import dataclasses

import pytest

from evidence_shape.vocabulary import NotInVocabulary

from facts.domains import (
    FIELD_LESS_SCHEMA_IDS, SCHEMA_IDS, UNIVERSAL_SCOPE, ActivationSignal,
    ActivationSignals, UnknownSchema, active_field_allowlist, schema_fields,
)
from facts.fields import (
    DOMAIN_FIELDS, FIELD_ROWS, FIELD_SCOPES, FieldRow, create_fields,
    fields_in_scope, get_field,
)
from facts.states import STATES

BY_KEY = {row.field_key: row for row in FIELD_ROWS}

#: `60` §4's mint list, verbatim: key -> (scope declared, destination_eligible, ceiling).
MINTED = {
    "site": ("manufacturing", True, "possible"),
    "asset": ("manufacturing", True, "possible"),
    "product": ("manufacturing", True, "possible"),
    "supplier": ("business_operations", True, "possible"),
    "organization": ("business_operations", False, "possible"),
    "issuing_body": ("business_operations", True, "possible"),
    "record_period": ("business_operations", True, "validated"),
    "property": ("construction_property", True, "possible"),
    "design_item": ("engineering", True, "possible"),
    "subject_of_record": ("law_practice", False, "possible"),
    "authorization": ("resource_operations", True, "possible"),
    "consignment": ("logistics", True, "validated"),
    "people_cycle": ("hr", True, "possible"),
    "workforce_unit": ("hr", False, "possible"),
    "recruiting_cycle": ("career", True, "possible"),
    "employer": ("career", True, "possible"),
    "target_employer": ("career", True, "possible"),
    "account_holder": ("finance", False, "possible"),
    "job_title": ("career", True, "possible"),
}

#: `60` §5's table, one row per schema that declares a field set. The three safety
#: domains are field-less by PR-6 and are absent by construction, not by an empty entry.
SIXTY_FIVE = {
    "academic": {"school", "term", "subject", "work_type", "instructor"},
    "college_applications": {"target_university", "application_cycle",
                             "application_document_type", "purpose"},
    "research": {"project", "stage", "artifact_type", "lab", "venue", "institution"},
    "finance": {"institution", "account_type", "tax_year", "record_type",
                "account_holder"},
    "photos": {"capture_year", "event", "location", "media_type", "people",
               "camera_information", "capture_date"},
    "code": {"project", "repository", "programming_language", "artifact_type"},
    "career": {"employer", "target_employer", "recruiting_cycle", "work_type",
               "record_type", "job_title"},
    "business_operations": {"organization", "record_period", "project", "client",
                            "supplier", "record_type", "issuing_body"},
    "law_practice": {"project", "work_type", "client", "record_period", "our_firm",
                     "subject_of_record"},
    "creative": {"project", "artifact_type", "stage", "client", "venue"},
    "construction_property": {"property", "project", "work_type", "client", "our_firm"},
    "engineering": {"design_item", "artifact_type", "asset", "project", "stage"},
    "manufacturing": {"site", "product", "asset", "event", "record_period",
                      "record_type"},
    "retail_hospitality": {"site", "event", "record_type", "record_period", "product"},
    "resource_operations": {"site", "asset", "authorization", "product",
                            "record_period", "record_type"},
    "logistics": {"consignment", "record_type", "site", "asset", "supplier"},
    "government": {"project"},
    "nonprofit": {"organization", "record_period", "subject_of_record", "institution"},
    "hr": {"people_cycle", "workforce_unit", "subject_of_record", "event"},
    "clinical_practice": {"subject_of_record"},
}


# --- J-1: SCHEMA_IDS widens 10 -> 23 ----------------------------------------

def test_the_twenty_three_roster_schemas_are_the_recognised_schemas():
    assert len(SCHEMA_IDS) == 23
    assert len(set(SCHEMA_IDS)) == 23
    assert set(SCHEMA_IDS) == {
        "academic", "business_operations", "career", "clinical_practice", "code",
        "college_applications", "construction_property", "creative", "engineering",
        "finance", "government", "hr", "identity", "law_practice", "legal",
        "logistics", "manufacturing", "medical", "nonprofit", "photos", "research",
        "resource_operations", "retail_hospitality"}
    # The live ten stay in their live order; widening appends, it does not reshuffle.
    assert SCHEMA_IDS[:10] == ("academic", "college_applications", "research", "career",
                               "photos", "code", "finance", "identity", "medical",
                               "legal")


def test_a_schema_outside_the_twenty_three_is_still_refused():
    # The negative twin of the widening. A closed vocabulary that has grown is still
    # closed; if it were not, "recognised" would mean nothing.
    for absent in ("astrology", "travel", "Academic", "hr ", ""):
        with pytest.raises(UnknownSchema):
            ActivationSignal(schema_id=absent, activates=lambda rows: True)
        with pytest.raises(UnknownSchema):
            schema_fields(absent)


def test_the_roster_file_and_schema_ids_are_the_same_twenty_three():
    import json
    from pathlib import Path
    roster = json.loads(
        (Path(__file__).resolve().parents[2] / "planning" / "domains" / "roster.json")
        .read_text(encoding="utf-8"))
    assert set(roster["schemas"]) == set(SCHEMA_IDS)


# --- the derived halves: scopes, field-less ids, the universal scope ---------

def test_field_scopes_covers_every_schema_that_declares_a_field_set():
    assert set(FIELD_SCOPES) - {UNIVERSAL_SCOPE} == set(SIXTY_FIVE)
    assert len(FIELD_SCOPES) == 21
    # The live seven are a prefix: adoption appends.
    assert FIELD_SCOPES[:7] == ("universal", "academic", "college_applications",
                                "research", "finance", "photos", "code")


def test_only_the_three_safety_domains_are_field_less_now():
    # Derived, not authored. `career` leaves this tuple because J-3 declares its
    # fields; D1's deferral said "Career is owed before P10" and `60` §5 pays it.
    assert FIELD_LESS_SCHEMA_IDS == ("identity", "medical", "legal")
    for schema_id in FIELD_LESS_SCHEMA_IDS:
        assert schema_fields(schema_id) == ()
        assert schema_id not in DOMAIN_FIELDS
        assert schema_id not in FIELD_SCOPES


def test_exactly_one_scope_is_not_a_schema_and_it_is_universal():
    # `UNIVERSAL_SCOPE` is derived by `next(... not in SCHEMA_IDS)`. With 21 scopes
    # that derivation is only honest if exactly one scope qualifies.
    outside = [scope for scope in FIELD_SCOPES if scope not in SCHEMA_IDS]
    assert outside == ["universal"]
    assert UNIVERSAL_SCOPE == "universal"


# --- §4: the eighteen minted keys -------------------------------------------

def test_the_catalogue_is_fifty_six_rows():
    # `60` §4: "37 live + 19 = 56."
    assert len(FIELD_ROWS) == 56
    assert len(BY_KEY) == 56


def test_each_minted_key_carries_its_ruling_scope_eligibility_and_ceiling():
    for key, (scope, eligible, ceiling) in MINTED.items():
        row = BY_KEY[key]
        assert row.scope == scope, key
        assert row.destination_eligible is eligible, key
        assert row.reliability_ceiling == ceiling, key


def test_the_two_keys_sixty_refuses_to_mint_are_absent():
    # `60` §4: "`workforce_member` and `personnel_case` are NOT minted." Each of the
    # others is an ALIAS or a merge path, never a key: `carrier` -> `supplier` (B3),
    # `authorisation` -> `authorization` (H8), `sponsor` -> `institution` (`48` §2),
    # `programme` -> `project` (`49` §4.2(h)), `role` -> `job_title` (§8.1).
    for absent in ("workforce_member", "personnel_case", "carrier",
                   "authorisation", "sponsor", "programme", "role"):
        assert absent not in BY_KEY


def test_a_reliability_ceiling_is_one_of_3_13_s_six_states_or_absent():
    # `domains/_CONTRACT.md` rule 4: "`reliability_ceiling` uses §3.13's states only".
    for row in FIELD_ROWS:
        assert row.reliability_ceiling is None or row.reliability_ceiling in STATES
    # Negative twin: the live 37 carry no ceiling, so "all rows pass" is not vacuous.
    assert {row.reliability_ceiling for row in FIELD_ROWS} == {
        None, "possible", "validated"}
    assert BY_KEY["consignment"].reliability_ceiling == "validated"
    assert BY_KEY["record_period"].reliability_ceiling == "validated"


# --- §5: the per-schema declarations ----------------------------------------

def test_domain_fields_is_sixty_five_s_table():
    assert set(DOMAIN_FIELDS) == set(SIXTY_FIVE)
    for schema_id, expected in SIXTY_FIVE.items():
        assert set(DOMAIN_FIELDS[schema_id]) == expected, schema_id
        assert len(DOMAIN_FIELDS[schema_id]) == len(expected), schema_id


def test_code_keeps_00_s_four_because_no_ruling_drops_them():
    # `60` §5's `code` row counts only the keys DECLARED at scope `code`; `00` §3.11
    # names four for Code -- "project, repository, programming language, and artifact
    # type" -- and `60` drops nothing (contrast B1, which drops by name). `00` wins.
    assert DOMAIN_FIELDS["code"] == ("project", "repository", "programming_language",
                                     "artifact_type")


def test_every_referenced_key_is_a_real_catalogue_row(p6_conn):
    for schema_id, keys in DOMAIN_FIELDS.items():
        for field_key in keys:
            assert get_field(p6_conn, field_key)["field_key"] == field_key


def test_five_schemas_declare_a_field_set_and_mint_nothing(p6_conn):
    # The declared/referenced split, at scale: `creative`, `retail_hospitality`,
    # `government`, `nonprofit` and `clinical_practice` are real scopes with zero rows
    # DECLARED at them. A consumer that reads declarations instead of the field set
    # sees an empty answer for these five.
    minting_nothing = {"creative", "retail_hospitality", "government", "nonprofit",
                       "clinical_practice"}
    for schema_id in minting_nothing:
        assert fields_in_scope(p6_conn, schema_id) == []
        assert DOMAIN_FIELDS[schema_id]
    # Negative twin: a schema that DOES mint returns its rows.
    assert {row["field_key"] for row in fields_in_scope(p6_conn, "manufacturing")} == {
        "site", "asset", "product"}
    assert {row["field_key"] for row in fields_in_scope(p6_conn, "career")} == {
        "employer", "target_employer", "recruiting_cycle", "job_title"}


# --- the allowlist, rebuilt on the field set --------------------------------

def _allowlist(conn, *schema_ids):
    return active_field_allowlist(
        conn, file_id="file-1", content_hash="0" * 64,
        activation_signals=ActivationSignals(tuple(
            ActivationSignal(schema_id, lambda rows: True)
            for schema_id in schema_ids)))


def test_an_active_schema_reaches_its_whole_field_set_not_only_its_declarations(
        p6_conn):
    # §3.5: the model "can only propose facts that belong to the active domain
    # schema". Under `60` §5 five schemas declare nothing, so an allowlist built on
    # declaration scopes would let an active `creative` propose nothing at all.
    for schema_id, expected in SIXTY_FIVE.items():
        assert expected <= set(_allowlist(p6_conn, schema_id)), schema_id


def test_a_field_less_schema_still_activates_and_contributes_nothing(p6_conn):
    # The branch that skips a recognised schema with no field set stays REACHABLE
    # after the widening -- identity, medical and legal are what keep it live.
    universal = {row["field_key"] for row in fields_in_scope(p6_conn, UNIVERSAL_SCOPE)}
    for schema_id in FIELD_LESS_SCHEMA_IDS:
        assert set(_allowlist(p6_conn, schema_id)) == universal


def test_an_inactive_schemas_fields_stay_out(p6_conn):
    allowlist = set(_allowlist(p6_conn, "logistics"))
    assert "consignment" in allowlist
    assert "design_item" not in allowlist
    assert "people_cycle" not in allowlist
    assert "capture_year" not in allowlist


def test_a_shared_key_is_listed_once_across_many_active_schemas(p6_conn):
    # `record_type` belongs to seven schemas and `record_period` to six. Ten active
    # schemas must list each exactly once and lose neither.

    allowlist = _allowlist(p6_conn, "manufacturing", "logistics", "retail_hospitality",
                           "resource_operations", "business_operations", "finance",
                           "career", "law_practice", "nonprofit", "hr")
    assert len(allowlist) == len(set(allowlist))
    assert allowlist.count("record_type") == 1
    assert allowlist.count("record_period") == 1
    assert allowlist.count("subject_of_record") == 1


# --- §3 H7: the alias fixes, and the alias namespace ------------------------

def _alias_index(rows):
    """alias -> the keys claiming it. A plain dict would COLLAPSE a double claim into
    one entry and report nothing, which is the bug `materialise.py` shipped."""
    index = {}
    for row in rows:
        for alias in row.aliases:
            index.setdefault(alias, []).append(row.field_key)
    return index


def _alias_defects(rows):
    """Every way the alias namespace can lie, as a list of strings."""
    defects = []
    keys = {row.field_key for row in rows}
    for alias, claimants in sorted(_alias_index(rows).items()):
        if len(claimants) > 1:
            defects.append(f"{alias!r} claimed by {sorted(claimants)}")
        if alias in keys:
            defects.append(f"{alias!r} is also a field key")
    return defects


def test_tax_year_drops_fiscal_year_and_application_cycle_drops_bare_cycle():
    # H7: `fiscal_year -> tax_year` beside `fiscal_period -> record_period` puts two
    # genuinely different objects one character apart. And a bare "cycle" now resolves
    # across `application_cycle`, `recruiting_cycle` and `people_cycle`.
    assert "fiscal_year" not in BY_KEY["tax_year"].aliases
    assert "cycle" not in BY_KEY["application_cycle"].aliases
    assert "fiscal_year" not in _alias_index(FIELD_ROWS)
    assert "cycle" not in _alias_index(FIELD_ROWS)
    # Negative twin: the drop is surgical, not an emptying. The rest of each row's
    # aliases survive, and `record_period` still carries the alias H7 kept.
    assert BY_KEY["tax_year"].aliases == ("tax year",)
    assert BY_KEY["application_cycle"].aliases == ("application cycle",
                                                   "admissions cycle")
    assert "fiscal_period" in BY_KEY["record_period"].aliases


def test_no_alias_is_claimed_twice_and_no_alias_is_also_a_key():
    assert _alias_defects(FIELD_ROWS) == []


def test_the_alias_guard_fails_on_a_deliberately_broken_namespace():
    # Without this, the guard above is satisfied by a catalogue with no aliases.
    assert any(row.aliases for row in FIELD_ROWS)
    doubled = FIELD_ROWS + (dataclasses.replace(
        BY_KEY["venue"], field_key="stadium", aliases=("conference",)),)
    assert _alias_defects(doubled) == ["'conference' claimed by ['stadium', 'venue']"]
    shadowing = FIELD_ROWS + (dataclasses.replace(
        BY_KEY["venue"], field_key="stadium", aliases=("project",)),)
    assert _alias_defects(shadowing) == ["'project' is also a field key"]


# --- §4: the reciprocal role_split pairs ------------------------------------

#: `60` §4's list, plus `authored_by` <-> `target_school`, which §3.8 names verbatim
#: ("distinct facets, such as authored_by and target_school") and which
#: `canonical_fields.json` already carries. `60` §4 does not enumerate it; dropping a
#: live §3.8 pair to match an omission would be a silent loss.
EXPECTED_PAIRS = {
    frozenset({"recruiting_cycle", "people_cycle"}),
    frozenset({"employer", "our_firm"}),
    frozenset({"account_holder", "institution"}),
    frozenset({"client", "our_firm"}),
    frozenset({"school", "target_university"}),
    frozenset({"employer", "target_employer"}),
    frozenset({"authored_by", "target_school"}),
}


def _role_split_defects(rows):
    by_key = {row.field_key: row for row in rows}
    defects = []
    for row in rows:
        for partner in row.role_split:
            if partner not in by_key:
                defects.append(f"{row.field_key} -> {partner}: not a catalogue key")
            elif row.field_key not in by_key[partner].role_split:
                defects.append(f"{row.field_key} -> {partner}: not returned")
            elif partner == row.field_key:
                defects.append(f"{row.field_key} -> itself")
    return sorted(defects)


def test_every_role_split_is_reciprocal():
    assert _role_split_defects(FIELD_ROWS) == []


def test_the_declared_pairs_are_exactly_sixty_s_list():
    pairs = {frozenset({row.field_key, partner})
             for row in FIELD_ROWS for partner in row.role_split}
    assert pairs == EXPECTED_PAIRS
    # §3.8: "It should avoid using authorship or creator identity as a destination
    # dimension." Each pair splits a role; it does not duplicate eligibility.
    assert BY_KEY["employer"].destination_eligible is True
    assert BY_KEY["our_firm"].destination_eligible is False
    assert BY_KEY["account_holder"].destination_eligible is False
    assert BY_KEY["institution"].destination_eligible is True


def test_the_reciprocity_guard_fails_on_a_deliberately_broken_pair():
    # The positive half cannot detect substitution: a table with no pairs passes it.
    one_way = tuple(dataclasses.replace(row, role_split=())
                    if row.field_key == "people_cycle" else row
                    for row in FIELD_ROWS)
    assert _role_split_defects(one_way) == [
        "recruiting_cycle -> people_cycle: not returned"]
    dangling = tuple(dataclasses.replace(row, role_split=("ghost",))
                     if row.field_key == "client" else row for row in FIELD_ROWS)
    assert "client -> ghost: not a catalogue key" in _role_split_defects(dangling)
    self_paired = tuple(dataclasses.replace(row, role_split=("client",))
                        if row.field_key == "client" else row for row in FIELD_ROWS)
    assert _role_split_defects(self_paired) == [
        "client -> itself", "our_firm -> client: not returned"]


# --- the notes discriminators `60` requires ---------------------------------

def test_record_type_carries_all_three_halves_of_h6():
    notes = BY_KEY["record_type"].notes
    assert notes
    # 1. the negative discriminator, naming both keys it is NOT
    assert "work_type" in notes and "artifact_type" in notes
    assert "abstention" in notes
    # 2. the undeclared-route clause
    assert "not declared by the active schema" in notes
    assert "never re-routed" in notes
    # 3. the value-side scope
    assert "schema-qualified" in notes
    assert "production return" in notes


def test_design_item_and_product_both_carry_m10_s_sentence():
    sentence = ("the controlled design configuration whose definition a file governs"
                " -- never a saleable or sold article, which is `product`")
    assert sentence in BY_KEY["design_item"].notes
    assert sentence in BY_KEY["product"].notes


def test_employer_and_our_firm_both_carry_m12_s_discriminator():
    for key in ("employer", "our_firm"):
        notes = BY_KEY[key].notes
        assert notes and "employer" in notes and "our_firm" in notes
        assert "one letterhead" in notes


def test_supplier_carries_b3_s_three_role_warning():
    notes = BY_KEY["supplier"].notes
    assert notes
    for label in ("Carrier", "Haulier", "Forwarder", "Shipping Line", "Airline"):
        assert label in notes
    assert "consignor, consignee and carrier" in notes


def test_recruiting_cycle_and_people_cycle_carry_j_2_s_discriminator_reciprocally():
    career = BY_KEY["recruiting_cycle"].notes.lower()
    hr = BY_KEY["people_cycle"].notes.lower()
    assert career and hr
    assert "participant" in career and "runs the cycle" in career
    assert "runs the cycle" in hr and "participant" in hr
    assert "people_cycle" in career and "recruiting_cycle" in hr


def test_every_minted_key_says_why_it_exists():
    for key in MINTED:
        assert BY_KEY[key].notes, key


# --- the table still loads, and still refuses ------------------------------

def test_all_fifty_six_rows_load_and_the_stored_columns_are_unchanged(p6_conn):
    create_fields(p6_conn)
    stored = p6_conn.execute("SELECT COUNT(*) FROM fields").fetchone()[0]
    assert stored == 56
    columns = [row[1] for row in p6_conn.execute("PRAGMA table_info(fields)")]
    assert columns == ["field_key", "display_name", "scope", "value_kind",
                       "normalizer_id", "destination_eligible", "multiplicity"]
    # The adopted metadata is authored, not stored: `60` asks for no new column and
    # nothing in P6 reads one.
    assert {"aliases", "role_split", "notes", "reliability_ceiling"} <= {
        field.name for field in dataclasses.fields(FieldRow)}
    assert not {"aliases", "role_split", "notes", "reliability_ceiling"} & set(columns)


def test_a_scope_outside_the_twenty_one_is_still_refused(p6_conn):
    for absent in ("identity", "medical", "legal", "Universal", "travel"):
        with pytest.raises(NotInVocabulary):
            fields_in_scope(p6_conn, absent)


# --- J-4's 3-6 band, and the three places `60` §5's own arithmetic diverges ---

#: `60` §5's `dest` column, which J-4's 3-6 band measures. `hr` is written "1-2" there
#: (`workforce_unit` is seeded false and template-time promotable); the live number is
#: the upper end.
SIXTY_FIVE_DEST = {
    "academic": 4, "college_applications": 4, "research": 6, "finance": 4, "photos": 4,
    "code": 1, "career": 6, "business_operations": 6, "law_practice": 4, "creative": 5,
    "construction_property": 4, "engineering": 5, "manufacturing": 6,
    "retail_hospitality": 5, "resource_operations": 6, "logistics": 4, "government": 1,
    "nonprofit": 2, "hr": 2, "clinical_practice": 0,
}

#: Where the shipped count is NOT `60` §5's, with the reason. Both are cases where §5's
#: table and §4's mint list disagree and §4 (or `00`) governs. Named rather than left to
#: be discovered, which is the discipline J-5a itself applies to the schemas under the
#: band's floor.
DIVERGENCES = {
    # §5's `code` row ("repository · programming_language", dest 1) counts the keys
    # DECLARED at scope `code`. `00` §3.11 names four for Code and `60` drops nothing.
    "code": 3,
    # §5 marks `supplier` dagger on `logistics` only. Destination eligibility is a
    # property of the KEY -- `60` §4 says so on `subject_of_record`, "on the key, never
    # per-template" -- and §4 mints `supplier` eligible, which `business_operations`
    # needs to reach §5's own dest count of 6.
    "logistics": 5,
}


def test_the_dest_counts_are_sixty_five_s_except_where_sixty_contradicts_itself():
    live = {schema_id: sum(1 for key in keys if BY_KEY[key].destination_eligible)
            for schema_id, keys in DOMAIN_FIELDS.items()}
    assert live == {**SIXTY_FIVE_DEST, **DIVERGENCES}
    # The negative twin: the divergences are REAL, not a copy of the table. If someone
    # later reconciles them, this fails and the reconciliation gets read.
    assert all(live[schema_id] != SIXTY_FIVE_DEST[schema_id]
               for schema_id in DIVERGENCES)


def test_the_schemas_under_j_4_s_floor_are_exactly_the_named_exemptions():
    # J-5a: `00`:48's "three to six that may help build a future folder proposal"
    # describes schemas whose job is to propose folders. A schema whose job is to keep
    # a grievance file out of a named folder has fewer by design. Recorded as a named
    # exemption rather than letting a schema sit under a floor nobody restated.
    under = {schema_id for schema_id, keys in DOMAIN_FIELDS.items()
             if sum(1 for key in keys if BY_KEY[key].destination_eligible) < 3}
    assert under == {"government", "nonprofit", "hr", "clinical_practice"}
    # `code` is under the band on §5's own count and over it on `00`'s; the divergence
    # above is what moves it, so it is asserted from the same place and not twice.
    assert SIXTY_FIVE_DEST["code"] < 3 <= DIVERGENCES["code"]
    # Nothing exceeds six.
    assert max(sum(1 for key in keys if BY_KEY[key].destination_eligible)
               for keys in DOMAIN_FIELDS.values()) == 6
