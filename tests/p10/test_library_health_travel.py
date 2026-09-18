# tests/p10/test_library_health_travel.py
"""`00` amendment 21: situations are authored for `medical` and `travel`.

`104` §18.112 measured the shipped library: `medical` has ZERO situations and
`travel`'s two resolve to `finance` and `photos`, so Health and Travel -- two of
the owner's sixteen lives and two branches of `107` -- could never receive a
folder level. `drafts/health_travel.json` is the DRAFT that closes it, to `107`'s split
orders: Health as year -> record type (the person level is the person's own, see
the definition's constraints), Travel as year -> trip -> function.

THE FILE IS NOT IN `production.LIBRARY_FILES` AND SITS UNDER `library/drafts/`,
which no shipped-vocabulary pin globs. Every name and label in it is the
owner's vocabulary awaiting ratification, and `cli.py` builds the situation menu
that goes to a cloud model from `shipped_situations(catalogue)`; an unratified
text must never cross the internet. These tests therefore build an EXTENDED
catalogue by widening the file list for the test alone, and one test guards that
the shipped release does not carry the names yet.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import production
from facts.domains import FIELD_LESS_SCHEMA_IDS
from facts.fields import DOMAIN_FIELDS, FIELD_ROWS
from production import (
    LIBRARY_FILES, folder_levels_for, life_of, load_shipped_catalogue,
    read_packaged_library_file, schema_for_situation, shipped_situations,
)
from tree_design.config import ConfigurationRequired
from tree_design.templates import merge_fragment_constraints

LIBRARY = Path(__file__).resolve().parents[2] / "src" / "tree_design" / "library"
DRAFT = "drafts/health_travel.json"

#: `51`'s appendix writes the placeholder floor symbol `baseline`; P7 injects the
#: real vocabulary per deployment. Same rank `test_library_definitions.py` uses.
RANK = {"baseline": 0, "protected": 1}.__getitem__

#: Every situation the draft carries: its schema, its life, and the ordered
#: levels `folder_levels_for` must answer -- (field, label, requirement).
EXPECTED = {
    "medical.personal-health-records": (
        "medical", "Health",
        (("year", "Year", "required"),
         ("record_type", "Kind of health record", "required"))),
    "medical.dependant-child-health": (
        "medical", "Health",
        (("year", "Year", "required"),
         ("record_type", "Kind of health record", "required"))),
    "travel.trip-records": (
        "finance", "Travel",
        (("year", "Year", "required"),
         ("event", "Trip", "required"),
         ("record_type", "What it is for", "required"))),
}

#: Keys that name a person and may never be a Health level (`107` line 120).
PERSON_NAMING_KEYS = frozenset(
    {"people", "subject_of_record", "account_holder", "client", "authored_by"})


@pytest.fixture
def shipped():
    return load_shipped_catalogue(read_packaged_library_file)


@pytest.fixture
def extended(monkeypatch):
    """The shipped release plus the draft, for this test alone. Both
    `read_packaged_library_file` and `shipped_catalogue_manifest` look the
    file list up at call time, so widening the module attribute is enough."""
    monkeypatch.setattr(production, "LIBRARY_FILES", (*LIBRARY_FILES, DRAFT))
    return load_shipped_catalogue(read_packaged_library_file)


@pytest.fixture
def draft():
    return json.loads((LIBRARY / DRAFT).read_text(encoding="utf-8"))


# --- the draft is in the library's own shape --------------------------------

def test_the_draft_parses_through_the_real_loader(extended, draft):
    assert set(draft) - {"_"} == {"fragments", "definitions", "applicabilities"}
    for row in draft["applicabilities"]:
        assert set(row["allowed_fields"]) == {
            b["field_ref"] for b in row["role_bindings"]}, row["applicability_id"]
        assert len(row["allowed_fields"]) == len(set(row["allowed_fields"]))
        assert row["privacy_floor"] is None
        assert (row["applicability_id"], 1) in extended.applicabilities
    for definition in draft["definitions"]:
        assert definition["publication_state"] == "draft"
        assert (definition["template_id"], 1) in extended.definitions


def test_each_new_definition_composes_into_the_order_it_recommends(extended, draft):
    """`51` §3.4's closing rule, as `test_library_definitions.py` checks it for
    the shipped recipes: the default order equals the order the fragments derive."""
    for raw in draft["definitions"]:
        record = extended.definitions[(raw["template_id"], 1)]
        fragments = [extended.fragment(ref) for ref in record.fragment_refs]
        recommended = [d.role_ref for d in sorted(record.default_order.dimensions,
                                                  key=lambda d: d.order_index)]
        merged = merge_fragment_constraints(
            fragments, privacy_rank=RANK, preferred_order=recommended,
            definition=record)
        assert list(merged.ordered_roles) == recommended, record.template_id
        assert merged.privacy_floor == "baseline", record.template_id


# --- the library answers for Health and Travel -------------------------------

@pytest.mark.parametrize("situation", sorted(EXPECTED))
def test_folder_levels_for_answers_the_owners_split_order(extended, situation):
    _, _, levels = EXPECTED[situation]
    answered = tuple((level.field, level.label, level.requirement)
                     for level in folder_levels_for(extended, situation))
    assert answered == levels


@pytest.mark.parametrize("situation", sorted(EXPECTED))
def test_schema_and_life_resolve(extended, situation):
    schema, life, _ = EXPECTED[situation]
    assert schema_for_situation(extended, situation) == schema
    assert life_of(extended, situation) == life


def test_health_files_the_kind_and_the_situation_into_one_life(extended):
    """`00` amendment 18: a life is answerable for a kind, not only a situation.
    `medical` -> Health in `lives.json` already; the rows must agree with it."""
    assert production.life_of_kind(extended, "medical") == "Health"
    for situation in ("medical.personal-health-records",
                      "medical.dependant-child-health"):
        assert life_of(extended, situation) == "Health"


def test_the_menu_lists_the_new_situations_under_their_own_domain(extended):
    listed = {row.name: row for row in shipped_situations(extended)}
    for situation, (schema, _, levels) in EXPECTED.items():
        assert listed[situation].schema == schema
        assert listed[situation].folder_levels == tuple(l[1] for l in levels)


# --- nothing that was previously answerable changed --------------------------

def test_every_shipped_answer_is_unchanged_by_the_draft(shipped, extended):
    before = {row.name for row in shipped_situations(shipped)}
    after = {row.name for row in shipped_situations(extended)}
    assert before <= after
    assert after - before == set(EXPECTED)
    for situation in sorted(before):
        assert folder_levels_for(shipped, situation) == folder_levels_for(
            extended, situation), situation
        assert schema_for_situation(shipped, situation) == schema_for_situation(
            extended, situation), situation
        assert life_of(shipped, situation) == life_of(extended, situation), situation


# --- the ratification gate ---------------------------------------------------

def test_the_names_are_not_in_the_shipped_menu_until_the_owner_ratifies(shipped):
    """DELETE THIS TEST when the owner ratifies the names and the lead appends
    the draft to `src/tree_design/library/` and its name to
    `production.LIBRARY_FILES`. Until then it is the
    check that no drafted name can reach the cloud menu `cli.py` builds."""
    assert DRAFT not in LIBRARY_FILES
    shipped_names = {row.name for row in shipped_situations(shipped)}
    for situation in EXPECTED:
        assert situation not in shipped_names
        with pytest.raises(ConfigurationRequired):
            schema_for_situation(shipped, situation)
    with pytest.raises(ConfigurationRequired):
        read_packaged_library_file(DRAFT)


# --- Health's protection, and the person level -------------------------------

def test_no_health_level_names_a_person(extended):
    """`107` line 120: 'client, patient, employee, and candidate names should not
    be generated as folder levels by default'. The ruled order is person -> year
    -> record type; the person level is the person's own to add and is not
    shipped."""
    for situation in ("medical.personal-health-records",
                      "medical.dependant-child-health"):
        bound = {level.field for level in folder_levels_for(extended, situation)}
        assert not bound & PERSON_NAMING_KEYS, situation
    definition = extended.definitions[("def.health-year-record", 1)]
    assert any("PERSON LEVEL IS NOT SHIPPED" in c
               for c in definition.validation_constraints)
    assert definition.sensitivity_policy_ref == "sp.safety-domain-protected@1"


# --- the fields the levels need, stated exactly ------------------------------

def test_the_dependencies_are_exactly_the_ones_the_draft_declares(extended):
    """Three gaps, named so the day one closes this test says so:
    `year` is not a live key (`00` amendment 20 rules it added);
    `medical` is field-less, so `record_type` is not referenced there;
    `finance` does not reference `event`. Nothing else is missing, and no
    substitute key is bound in any gap's place."""
    live = {row.field_key for row in FIELD_ROWS}
    eligible = {row.field_key for row in FIELD_ROWS if row.destination_eligible}
    assert "year" not in live
    assert "medical" in FIELD_LESS_SCHEMA_IDS
    gaps = {}
    for situation, (schema, _, _) in EXPECTED.items():
        for level in folder_levels_for(extended, situation):
            if level.field not in live:
                gaps.setdefault(situation, set()).add(f"missing key {level.field}")
                continue
            assert level.field in eligible, (situation, level.field)
            if level.field not in DOMAIN_FIELDS.get(schema, ()):
                gaps.setdefault(situation, set()).add(
                    f"{level.field} not referenced at {schema}")
    assert gaps == {
        "medical.personal-health-records": {
            "missing key year", "record_type not referenced at medical"},
        "medical.dependant-child-health": {
            "missing key year", "record_type not referenced at medical"},
        "travel.trip-records": {
            "missing key year", "event not referenced at finance"},
    }
