# tests/p10/test_library_academic_teaching.py
"""`111`: the Teaching branch's institution level, WIRED by `00` amendment 31.

`107`'s branch-template table gives Teaching as *Institution -> term -> course ->
teaching function*, and `107`'s own tree draws the institution explicitly
(`Teaching/City Learning Center/2026 Fall/...`). The shipped row
`ap.academic.teaching` bound `term`, `subject` and `work_type` and bound NO
institution, although `def.subject-work-record.third-party` already declares
`holder_institution` as an OPTIONAL dimension at `order_index` 0. `school` is a
live, destination-eligible field DECLARED at `academic`, so the level needed no
new field and no new situation name -- only the binding.

WHY THIS WAS AN EDIT AND NOT AN ADDITION. `folder_levels_for`, `life_of` and
`template_id_for_situation` resolve a situation by scanning every applicability
row for its `recognition:` signal and REFUSE when two rows carry it -- "picking
between two rows would be this module deciding what kind of material somebody's
files are". A v2 row therefore does not supersede a v1 row left in place beside
it; the two coexist and `academic.teaching` stops resolving at all, and
`shipped_situations` -- the cloud-bound menu, which collects rows with
`setdefault((schema, name), ...)` -- silently keeps serving v1's three labels
while `folder_levels_for` refuses outright. `00` amendment 31's own words: "the
person would be shown one answer while the product held another, with nothing
raising." So the row was measured, then REPLACED in place -- the shipped
`ap.academic.teaching` row now carries `applicability_version` 2 and the
`holder_institution` binding, and there is only ever one row for the signal.

THIS FILE USED TO GATE THE DRAFT'S ABSENCE. Until amendment 31, wiring by
addition was refused and untested here on purpose: `test_the_draft_is_not_in_
the_shipped_release` pinned that the shipped answer for `academic.teaching` was
v1's three levels and that the drafted row
(`src/tree_design/library/drafts/academic_teaching_institution.json`, since
deleted -- its content now lives in the shipped row directly) was unreachable.
That assertion was right when written: nothing had authorised the replacement
yet, and a gate that let the fourth level in by a file rename would have shipped
an edit to a frozen row with no one having ruled on it. The amendment is that
ruling, so the gate now asserts the row's PRESENCE and SHAPE instead, and a
later edit that quietly drops the institution binding -- or renames one of the
three labels the person has already been shown -- turns it red.
"""
from __future__ import annotations

import pytest

from facts.fields import DOMAIN_FIELDS, FIELD_ROWS, UNIVERSAL_FIELDS
from production import (
    folder_levels_for, life_of, load_shipped_catalogue,
    read_packaged_library_file, schema_for_situation, shipped_situations,
    template_id_for_situation,
)

SITUATION = "academic.teaching"

#: `107`'s own order for Teaching -- Institution -> term -> course -> teaching
#: function -- as the wired row now answers it. The three non-institution
#: labels are v1's OWN LABELS, carried forward unchanged (`00` amendment 31's
#: second condition): a person who has already been shown "Semester I taught"
#: must keep finding it under that name.
EXPECTED_LEVELS = (
    ("school", "School I taught at", "optional"),
    ("term", "Semester I taught", "optional"),
    ("subject", "Course I taught", "required"),
    ("work_type", "Kind of teaching material", "required"),
)

#: Keys that name a person and may never be a Teaching level (`107` line 120,
#: and `107`'s 'Student Administration/ # protected; no student-name folders').
PERSON_NAMING_KEYS = frozenset(
    {"people", "subject_of_record", "account_holder", "client", "instructor"})


@pytest.fixture()
def shipped():
    return load_shipped_catalogue(read_packaged_library_file)


# --- the wired row's own shape ------------------------------------------------

def test_the_row_is_shipped_at_version_2(shipped):
    """THE GATE. A later edit that reverts the row to v1, or that adds a second
    row beside it instead of replacing this one, turns this red."""
    row = shipped.applicabilities[("ap.academic.teaching", 2)]
    assert row.detection_signal_refs == (f"recognition:{SITUATION}",)
    assert ("ap.academic.teaching", 1) not in shipped.applicabilities, (
        "v1 must be REPLACED, not left beside v2 -- two rows for one "
        "recognition signal make the situation unresolvable")


def test_the_row_mints_no_new_situation_name_and_reuses_the_shipped_template(
        shipped):
    """No new fragment, no new definition, and no new situation name: the only
    drafted vocabulary was one label, `'School I taught at'`."""
    row = shipped.applicabilities[("ap.academic.teaching", 2)]
    assert (row.template_id, row.template_version) in shipped.definitions
    assert SITUATION in {r.name for r in shipped_situations(shipped)}


def test_the_row_carries_v1s_three_bindings_forward_unchanged(shipped):
    """`00` amendment 31's second condition, read off the row itself: the
    labels a person has already been shown are not renamed. v2 ADDS the
    institution level and changes nothing else about the other three."""
    row = shipped.applicabilities[("ap.academic.teaching", 2)]
    bound = {b.role_ref: (b.field_ref, b.label) for b in row.role_bindings}
    assert bound["cycle_period"] == ("term", "Semester I taught")
    assert bound["subject_anchor"] == ("subject", "Course I taught")
    assert bound["artifact_kind"] == ("work_type", "Kind of teaching material")
    assert set(bound) - {"holder_institution"} == {
        "cycle_period", "subject_anchor", "artifact_kind"}
    assert bound["holder_institution"] == ("school", "School I taught at")


def test_the_row_builds_107s_teaching_order(shipped):
    """`107`: Institution -> term -> course -> teaching function. Read off the
    shipped DEFINITION's own dimension order, so this test cannot assert an
    order the template does not actually carry."""
    row = shipped.applicabilities[("ap.academic.teaching", 2)]
    definition = shipped.definitions[(row.template_id, row.template_version)]
    bound = {b.role_ref: b for b in row.role_bindings}
    answered = tuple(
        (bound[d.role_ref].field_ref, bound[d.role_ref].label, d.requirement)
        for d in sorted(definition.default_order.dimensions,
                        key=lambda d: d.order_index)
        if d.role_ref in bound)
    assert answered == EXPECTED_LEVELS


def test_the_shipped_situation_now_answers_all_four_levels(shipped):
    """The gap `111` measured is closed: `folder_levels_for` now returns the
    institution level alongside the three it always returned."""
    answered = tuple((lvl.field, lvl.label, lvl.requirement)
                     for lvl in folder_levels_for(shipped, SITUATION))
    assert answered == EXPECTED_LEVELS


def test_the_institution_level_needed_no_new_field(shipped):
    """`school` is live, destination-eligible and declared at `academic`, so
    unlike the Health and Travel drafts this row carried NO dependency gap."""
    live = {r.field_key for r in FIELD_ROWS}
    eligible = {r.field_key for r in FIELD_ROWS if r.destination_eligible}
    row = shipped.applicabilities[("ap.academic.teaching", 2)]
    for field in row.allowed_fields:
        assert field in live, field
        assert field in eligible, field
        assert (field in DOMAIN_FIELDS["academic"]
                or field in UNIVERSAL_FIELDS), field


def test_no_teaching_level_names_a_person(shipped):
    """`107` line 120, and `107`'s Teaching branch: 'Student Administration/
    # protected; no student-name folders'."""
    row = shipped.applicabilities[("ap.academic.teaching", 2)]
    assert not {b.field_ref for b in row.role_bindings} & PERSON_NAMING_KEYS
    assert row.exclusions


# --- the replacement disturbed nothing else -----------------------------------

def test_the_domain_and_life_are_unchanged(shipped):
    assert schema_for_situation(shipped, SITUATION) == "academic"
    assert life_of(shipped, SITUATION) == "Teaching"
    assert template_id_for_situation(shipped, SITUATION) == (
        "def.subject-work-record.third-party")


def test_the_shipped_release_still_reports_208_situations_and_only_teaching_moved(
        shipped):
    """`00` amendment 31's own worry, checked directly against the release as it
    shipped before this wave: a replacement must not silently widen or narrow
    the menu, or touch any row but the one it was authorised to replace.

    Compared against `git show b47940db:...applicabilities.json` -- the
    amendment's own commit, the last one before this row was wired -- rather
    than a hand-written "the other 207 look like this" fixture, because 208
    rows is too many to retype and a retyped copy could drift from the release
    without this test noticing. A FIXED SHA and not `HEAD`: this test is
    committed alongside the wiring it measures, so `HEAD` at the time anyone
    runs it is already the AFTER state, and diffing a commit against itself
    would report zero change and pass for the wrong reason. `shipped_situations`
    lists a name once per DOMAIN that carries it (its own docstring: "a
    situation carried by rows in two domains is listed under each"), so the
    comparison is over its full output, by `(schema, name)`, not by name alone.
    """
    import subprocess

    import production

    before_json = subprocess.run(
        ["git", "show", "b47940db:src/tree_design/library/applicabilities.json"],
        capture_output=True, text=True, check=True).stdout

    def read_before(name):
        if name == "applicabilities.json":
            return before_json
        return read_packaged_library_file(name)

    before_catalogue = load_shipped_catalogue(read_before)
    before = {(row.schema, row.name): row
             for row in shipped_situations(before_catalogue)}
    after = {(row.schema, row.name): row for row in shipped_situations(shipped)}

    # 209 since `00` amendment 42 added `career.current-work`. `read_before` swaps
    # only `applicabilities.json`, so the added row is in BOTH sides here and the
    # set equality below is untouched by it -- this count is the only line it moves.
    assert len(after) == 209
    assert set(before) == set(after), "the set of (schema, situation) rows moved"

    changed = {key for key in before if before[key] != after[key]}
    assert changed == {("academic", SITUATION)}, (
        "a row other than academic.teaching changed shape")
    assert after[("academic", SITUATION)].folder_levels == tuple(
        level[1] for level in EXPECTED_LEVELS)
    # the three old labels are a PREFIX-preserving subset, in their old order --
    # `00` amendment 31's second condition, checked on the exact tuple the
    # cloud-bound menu serves rather than on the row alone.
    assert before[("academic", SITUATION)].folder_levels == (
        "Semester I taught", "Course I taught", "Kind of teaching material")
    assert after[("academic", SITUATION)].folder_levels == (
        "School I taught at", "Semester I taught", "Course I taught",
        "Kind of teaching material")
