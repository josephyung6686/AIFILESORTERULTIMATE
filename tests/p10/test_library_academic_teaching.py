# tests/p10/test_library_academic_teaching.py
"""`111`: the Teaching branch's institution level, drafted and NOT installed.

`107`'s branch-template table gives Teaching as *Institution -> term -> course ->
teaching function*, and `107`'s own tree draws the institution explicitly
(`Teaching/City Learning Center/2026 Fall/...`). The shipped row
`ap.academic.teaching@1` binds `term`, `subject` and `work_type` and binds NO
institution, although `def.subject-work-record.third-party` already declares
`holder_institution` as an OPTIONAL dimension at `order_index` 0. `school` is a
live, destination-eligible field DECLARED at `academic`, so the level needs no
new field and no new situation name -- only the binding.

WHY THE DRAFT CANNOT SIMPLY BE APPENDED TO `production.LIBRARY_FILES`.
`folder_levels_for` and `schema_for_situation` resolve a situation by scanning
every applicability row for its `recognition:` signal and REFUSE when two rows
carry it -- "picking between two rows would be this module deciding what kind of
material somebody's files are". A v2 row therefore does not supersede v1; the two
coexist and `academic.teaching` stops resolving at all. `test_adding_the_draft_
beside_v1_breaks_the_situation` pins that, so the cost of wiring is measured
rather than assumed: it is an EDIT to a shipped row, which `111` refers to the
owner.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import production
from facts.fields import DOMAIN_FIELDS, FIELD_ROWS, UNIVERSAL_FIELDS
from production import (
    LIBRARY_FILES, folder_levels_for, life_of, load_shipped_catalogue,
    read_packaged_library_file, schema_for_situation, shipped_situations,
    template_id_for_situation,
)
from tree_design.config import ConfigurationRequired

LIBRARY = Path(__file__).resolve().parents[2] / "src" / "tree_design" / "library"
DRAFT = "drafts/academic_teaching_institution.json"
SITUATION = "academic.teaching"

#: The levels `107` asks of Teaching, as the drafted row would answer them.
EXPECTED_LEVELS = (
    ("school", "School I taught at", "optional"),
    ("term", "Semester I taught", "optional"),
    ("subject", "Course I taught", "required"),
    ("work_type", "Kind of teaching material", "required"),
)

#: What the SHIPPED row answers today: the institution level is missing.
SHIPPED_LEVELS = (
    ("term", "Semester I taught", "optional"),
    ("subject", "Course I taught", "required"),
    ("work_type", "Kind of teaching material", "required"),
)

#: Keys that name a person and may never be a Teaching level (`107` line 120,
#: and `107`'s 'Student Administration/ # protected; no student-name folders').
PERSON_NAMING_KEYS = frozenset(
    {"people", "subject_of_record", "account_holder", "client", "instructor"})


@pytest.fixture
def shipped():
    return load_shipped_catalogue(read_packaged_library_file)


@pytest.fixture
def extended(monkeypatch):
    """The shipped release PLUS the draft. Both `read_packaged_library_file` and
    `shipped_catalogue_manifest` look the file list up at call time, so widening
    the module attribute is enough."""
    monkeypatch.setattr(production, "LIBRARY_FILES", (*LIBRARY_FILES, DRAFT))
    return load_shipped_catalogue(read_packaged_library_file)


@pytest.fixture
def draft():
    return json.loads((LIBRARY / DRAFT).read_text(encoding="utf-8"))


# --- the draft is in the library's own shape --------------------------------

def test_the_draft_parses_through_the_real_loader(extended, draft):
    assert set(draft) - {"_"} == {"fragments", "definitions", "applicabilities"}
    assert draft["fragments"] == [] and draft["definitions"] == []
    (row,) = draft["applicabilities"]
    assert set(row["allowed_fields"]) == {
        b["field_ref"] for b in row["role_bindings"]}
    assert len(row["allowed_fields"]) == len(set(row["allowed_fields"]))
    assert row["privacy_floor"] is None
    assert (row["applicability_id"], 2) in extended.applicabilities


def test_the_draft_reuses_a_shipped_template_and_mints_no_name(shipped, draft):
    """No new fragment, no new definition, and no new situation name: the only
    drafted vocabulary is one label."""
    (row,) = draft["applicabilities"]
    assert (row["template_id"], row["template_version"]) in shipped.definitions
    assert row["detection_signal_refs"] == [f"recognition:{SITUATION}"]
    assert SITUATION in {r.name for r in shipped_situations(shipped)}


def test_the_draft_carries_the_shipped_bindings_forward_unchanged(shipped, draft):
    """v2 ADDS the institution level and changes nothing else."""
    v1 = shipped.applicabilities[("ap.academic.teaching", 1)]
    (row,) = draft["applicabilities"]
    drafted = {b["role_ref"]: (b["field_ref"], b["label"])
               for b in row["role_bindings"]}
    for binding in v1.role_bindings:
        assert drafted[binding.role_ref] == (binding.field_ref, binding.label)
    assert set(drafted) - {b.role_ref for b in v1.role_bindings} == {
        "holder_institution"}
    for key in ("uses_schema", "template_id", "life"):
        assert row[key] == getattr(v1, key if key != "life" else "life")


# --- what the level would be worth ------------------------------------------

def test_the_drafted_row_builds_107s_teaching_order(draft, shipped):
    """`107`: Institution -> term -> course -> teaching function. Read off the
    SHIPPED definition's own dimension order, so the draft cannot assert it."""
    (row,) = draft["applicabilities"]
    definition = shipped.definitions[("def.subject-work-record.third-party", 1)]
    bound = {b["role_ref"]: b for b in row["role_bindings"]}
    answered = tuple(
        (bound[d.role_ref]["field_ref"], bound[d.role_ref]["label"],
         d.requirement)
        for d in sorted(definition.default_order.dimensions,
                        key=lambda d: d.order_index)
        if d.role_ref in bound)
    assert answered == EXPECTED_LEVELS


def test_the_shipped_row_is_missing_exactly_the_institution_level(shipped):
    """The gap `111` measured, pinned so that closing it changes this test."""
    answered = tuple((lvl.field, lvl.label, lvl.requirement)
                     for lvl in folder_levels_for(shipped, SITUATION))
    assert answered == SHIPPED_LEVELS
    assert "school" not in {lvl.field for lvl in folder_levels_for(
        shipped, SITUATION)}


def test_the_institution_level_needs_no_new_field(draft):
    """`school` is live, destination-eligible and declared at `academic`, so
    unlike the Health and Travel drafts this row carries NO dependency gap."""
    live = {r.field_key for r in FIELD_ROWS}
    eligible = {r.field_key for r in FIELD_ROWS if r.destination_eligible}
    (row,) = draft["applicabilities"]
    for field in row["allowed_fields"]:
        assert field in live, field
        assert field in eligible, field
        assert (field in DOMAIN_FIELDS["academic"]
                or field in UNIVERSAL_FIELDS), field


def test_no_teaching_level_names_a_person(draft):
    """`107` line 120, and `107`'s Teaching branch: 'Student Administration/
    # protected; no student-name folders'."""
    (row,) = draft["applicabilities"]
    assert not {b["field_ref"] for b in row["role_bindings"]} & PERSON_NAMING_KEYS
    assert row["exclusions"]


# --- the ratification gate ---------------------------------------------------

def test_the_draft_is_not_in_the_shipped_release(shipped):
    """DELETE THIS TEST when the owner rules on `111`'s packet. Until then the
    shipped answer for `academic.teaching` is v1's three levels and the draft is
    unreachable through the one filesystem touch."""
    assert DRAFT not in LIBRARY_FILES
    with pytest.raises(ConfigurationRequired):
        read_packaged_library_file(DRAFT)
    assert ("ap.academic.teaching", 2) not in shipped.applicabilities
    assert schema_for_situation(shipped, SITUATION) == "academic"
    assert life_of(shipped, SITUATION) == "Teaching"


def test_adding_the_draft_beside_v1_breaks_the_situation(extended):
    """THE MEASURED COST OF WIRING, and the reason `111` sends this to the owner
    rather than appending a file name.

    `folder_levels_for`, `life_of` and `template_id_for_situation` resolve a
    situation by scanning every row for its `recognition:` signal and REFUSE when
    two carry it. A v2 row does NOT supersede v1 -- the loader keys rows by
    `(id, version)`, so the two coexist and `academic.teaching` stops resolving.
    Wiring this row therefore means REPLACING the shipped v1 row, which is an
    edit to a shipped row and the owner's alone to authorise."""
    assert ("ap.academic.teaching", 1) in extended.applicabilities
    assert ("ap.academic.teaching", 2) in extended.applicabilities
    for call in (folder_levels_for, life_of, template_id_for_situation):
        with pytest.raises(ConfigurationRequired) as caught:
            call(extended, SITUATION)
        assert "2 applicability rows" in str(caught.value), call.__name__


def test_the_domain_still_resolves_because_both_rows_agree_on_it(extended):
    """`schema_for_situation` is the one that does NOT refuse: it collects
    `uses_schema` across the carrying rows and refuses only when they DISAGREE.
    Both rows say `academic`, so the domain survives while the folders do not.
    Recorded so `111`'s claim is the measurement and not a guess."""
    assert schema_for_situation(extended, SITUATION) == "academic"


def test_the_cloud_bound_menu_silently_keeps_the_old_levels(shipped, extended):
    """THE FINDING `111` REPORTS, and the sharpest reason not to wire by addition.

    `shipped_situations` -- the menu `cli.py` builds for the model -- collects
    rows with `setdefault((schema, name), ...)`, so the FIRST row carrying the
    signal wins and the release still reports 208 situations. The menu would go
    on advertising v1's three labels, with no institution level, while
    `folder_levels_for` refuses to build anything at all. The person is shown one
    answer and the product holds another, and nothing raises."""
    assert len(shipped_situations(extended)) == len(shipped_situations(shipped))
    listed = {row.name: row for row in shipped_situations(extended)}
    assert listed[SITUATION].folder_levels == tuple(
        level[1] for level in SHIPPED_LEVELS)
    assert "School I taught at" not in listed[SITUATION].folder_levels
    with pytest.raises(ConfigurationRequired):
        folder_levels_for(extended, SITUATION)


def test_no_other_situation_is_disturbed_by_the_draft(shipped, extended):
    """Only `academic.teaching` changes; every other shipped answer is identical."""
    before = {row.name for row in shipped_situations(shipped)}
    after = {row.name for row in shipped_situations(extended)}
    assert before == after
    for situation in sorted(before - {SITUATION}):
        assert folder_levels_for(shipped, situation) == folder_levels_for(
            extended, situation), situation
        assert schema_for_situation(shipped, situation) == schema_for_situation(
            extended, situation), situation
        assert life_of(shipped, situation) == life_of(extended, situation), situation
