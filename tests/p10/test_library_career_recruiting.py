# tests/p10/test_library_career_recruiting.py
"""`00` amendment 33's second half: the `year` level on Career applications.

`107`'s branch-template table gives Career applications as *Year -> organization
and role -> application stage*, and until this row `year` was bound in NO shipped
row anywhere in the library (`00` amendment 22: "it is wired in NO shipped row").
The producer half shipped first and was measured alone (`cli.year_facts`, repaired
at `fc48b96c`, 47 of 47 real `creation_date` facts); this is the level built on top
of it.

WHY THIS IS A REPLACEMENT AND NOT AN ADDITION -- `00` amendment 31, the same
argument `ap.academic.teaching` v2 was authorised under. `folder_levels_for`,
`life_of` and `template_id_for_situation` resolve a situation by scanning every
applicability row for its `recognition:` signal and REFUSE when two rows carry it,
while `shipped_situations` -- the cloud-bound menu -- collects rows with
`setdefault((schema, name), ...)` and would silently keep serving v1's four labels.
So the row is REPLACED in place at `applicability_version` 2 and there is only ever
one row for `recognition:career.recruiting`.

WHY A DIMENSION AND NOT A BINDING ALONE. `production.folder_levels_for` iterates
`definition.default_order.dimensions` and skips a role the row does not bind -- so a
`role_bindings` entry whose role is not a DIMENSION of the definition is silently
dropped and builds nothing. `def.career-search-and-tenure` therefore gains the
dimension, and because `TemplateDefinition._check_orders` requires every candidate
order of a definition to cover the SAME role set, BOTH of D30's orders gain it or
the record refuses at load.

WHICH ROLE, AND WHY NO ROLE WAS MINTED. `capture_time` is one of `43` §2.1's
fifteen launch roles -- "the year a capture was taken, from capture metadata" --
and `facts/fields.py` authored `year` "patterned on `capture_date -> capture_year`"
off the same kind of source, the artifact's own metadata timestamp. A role is a
cross-schema SLOT realised per schema (`holder_institution` binds `school` on
academic rows and `lab` on research ones), so binding it to `year` here mints
nothing. The two rejected alternatives are asserted below rather than argued:
`cycle_period` is already taken on this very row by `recruiting_cycle`, and
`scope_period` is the period a record COVERS -- the role `tax_year` binds, which
`00` amendment 23 keeps deliberately apart from `year`.

WHAT `ap.career.employment-records` DOES NOT GET. `107`'s Current work wants
`project` and `stage`, which no career row has and which nobody may mint here, so
the tenure row is untouched -- and the test below measures that the definition
gaining a dimension changed none of its levels.
"""
from __future__ import annotations

import pytest

from facts.fields import DOMAIN_FIELDS, FIELD_ROWS, UNIVERSAL_FIELDS
from production import (
    folder_levels_for, group_level_fields_for, life_of, load_shipped_catalogue,
    read_packaged_library_file, schema_for_situation, shipped_situations,
    template_id_for_situation,
)

SITUATION = "career.recruiting"
TENURE = "career.employment-records"
ROW = "ap.career.recruiting"
D30 = "def.career-search-and-tenure"
EMPLOYER_FIRST = "ord.employer-role-cycle-kind"
CYCLE_FIRST = "ord.cycle-kind-employer-role"

#: The label the row already shipped, and the ONE new word this change authors.
#: `00` amendment 31's second condition is that the four a person has already been
#: shown keep their exact words and their relative order; the tuple may grow.
OLD_LABELS = ("Company I applied to", "Job I went for", "My search",
              "What I sent them")
YEAR_LABEL = "Year"

#: `107`: *Year -> organization and role -> application stage*, as the wired row now
#: answers it. `target_employer` + `job_title` ARE "organization and role" and
#: `work_type` IS the "application stage"; the cycle keeps the place it already had.
EXPECTED_LEVELS = (
    ("year", YEAR_LABEL, "optional"),
    ("target_employer", "Company I applied to", "required"),
    ("job_title", "Job I went for", "optional"),
    ("recruiting_cycle", "My search", "optional"),
    ("work_type", "What I sent them", "required"),
)

#: What the tenure row built before this change and must still build after it.
TENURE_LEVELS = (
    ("employer", "Where I worked", "required"),
    ("job_title", "Job I held", "optional"),
    ("record_type", "Kind of job paperwork", "required"),
)

#: The commit this test is committed on top of -- the last one before the row was
#: wired. A FIXED SHA and not `HEAD` for `test_a_teaching_syllabus_lands_under_its_
#: school`'s reason: `HEAD` at the time anyone runs this is already the AFTER state,
#: and diffing a commit against itself passes for the wrong reason.
BEFORE_SHA = "67968264"

#: Keys that name a person and may never be a level here. `00` §3.8 forbids
#: authorship as a destination dimension, and D30's own constraint keeps the
#: candidate out: "a folder named for a person is a personnel file about a third
#: party".
PERSON_NAMING_KEYS = frozenset(
    {"people", "subject_of_record", "account_holder", "client", "instructor",
     "authored_by", "our_firm"})


@pytest.fixture()
def shipped():
    return load_shipped_catalogue(read_packaged_library_file)


# --- the wired row's own shape ------------------------------------------------

def test_the_row_is_shipped_at_version_2(shipped):
    """THE GATE. A later edit that reverts the row to v1, or that adds a second
    row beside it instead of replacing this one, turns this red."""
    row = shipped.applicabilities[(ROW, 2)]
    assert row.detection_signal_refs == (f"recognition:{SITUATION}",)
    assert (ROW, 1) not in shipped.applicabilities, (
        "v1 must be REPLACED, not left beside v2 -- two rows for one recognition "
        "signal make the situation unresolvable and leave the menu serving v1")


def test_the_row_carries_v1s_four_bindings_forward_unchanged(shipped):
    """`00` amendment 31's second condition, read off the row itself: the labels a
    person has already been shown are not renamed, dropped or reordered. v2 ADDS
    the year level and changes nothing else about the other four."""
    row = shipped.applicabilities[(ROW, 2)]
    bound = {b.role_ref: (b.field_ref, b.label) for b in row.role_bindings}
    assert bound["employer_org"] == ("target_employer", "Company I applied to")
    assert bound["role_title"] == ("job_title", "Job I went for")
    assert bound["cycle_period"] == ("recruiting_cycle", "My search")
    assert bound["artifact_kind"] == ("work_type", "What I sent them")
    assert set(bound) - {"capture_time"} == {
        "employer_org", "role_title", "cycle_period", "artifact_kind"}
    assert bound["capture_time"] == ("year", YEAR_LABEL)
    # And the four old labels keep their RELATIVE order in the tuple the menu
    # serves, which is `role_bindings` order and not the built order.
    served = tuple(b.label for b in row.role_bindings)
    assert tuple(label for label in served if label in OLD_LABELS) == OLD_LABELS


def test_the_year_level_mints_no_new_role_and_no_new_field(shipped):
    """`year` is a live, destination-eligible field (`00` amendment 20) and
    `capture_time` is one of `43` §2.1's fifteen launch roles, so this row carried
    no vocabulary dependency: only the binding and the dimension are new."""
    live = {r.field_key for r in FIELD_ROWS}
    eligible = {r.field_key for r in FIELD_ROWS if r.destination_eligible}
    row = shipped.applicabilities[(ROW, 2)]
    for field in row.allowed_fields:
        assert field in live, field
        assert field in eligible, field
        assert (field in DOMAIN_FIELDS["career"]
                or field in UNIVERSAL_FIELDS), field
    assert "year" in UNIVERSAL_FIELDS and "year" not in DOMAIN_FIELDS["career"], (
        "`year` is universal ON PURPOSE -- `creation_date` is §3.11's universal "
        "set, so no schema declares the field derived from it")


def test_the_two_rejected_period_roles_stay_rejected(shipped):
    """`year` gets its OWN role. `cycle_period` is taken on this very row by
    `recruiting_cycle`, and `scope_period` is the period a record COVERS -- the
    role `tax_year` binds, which `00` amendment 23 rules is NOT `year`: a 2024
    return saved in January 2025 carries `creation_date` 2025."""
    row = shipped.applicabilities[(ROW, 2)]
    bound = {b.role_ref: b.field_ref for b in row.role_bindings}
    assert bound["cycle_period"] == "recruiting_cycle"
    assert "scope_period" not in bound
    assert "tax_year" not in row.allowed_fields
    # And nowhere in the release does a `scope_period` binding pick up `year`.
    for other in shipped.applicabilities.values():
        for binding in other.role_bindings:
            if binding.field_ref == "year":
                assert binding.role_ref == "capture_time", other.applicability_id


def test_no_recruiting_level_names_a_person(shipped):
    row = shipped.applicabilities[(ROW, 2)]
    assert not {b.field_ref for b in row.role_bindings} & PERSON_NAMING_KEYS
    assert row.exclusions


# --- the definition the level actually comes from -----------------------------

def test_the_year_role_is_a_dimension_of_both_of_d30s_orders(shipped):
    """A binding alone builds nothing: `folder_levels_for` iterates
    `default_order.dimensions` and skips a role it does not find there. And
    `_check_orders` refuses a definition whose candidate orders cover different
    role sets, so the alternative order carries it too or the record will not
    load."""
    definition = shipped.definitions[(D30, 1)]
    assert {o.order_id for o in definition.candidate_orders} == {
        EMPLOYER_FIRST, CYCLE_FIRST}
    for order in definition.candidate_orders:
        assert "capture_time" in order.role_set(), order.order_id
        leading = sorted(order.dimensions, key=lambda d: d.order_index)[0]
        assert leading.role_ref == "capture_time", order.order_id
        assert leading.requirement == "optional", (
            "a required level with no fact makes the file UNFIT at site E "
            "(`model_template.file_fits_its_situation`), which is the cost "
            "`00` amendment 22 binds `year` to REMOVE")
        assert not leading.metadata_only


def test_the_ruling_the_default_order_actually_carries_is_untouched(shipped):
    """`60` §8.3 ruled EMPLOYER-first over CYCLE-first, and that ruling is about
    which of the two the middle of `00`:70's disjunction takes -- not about what
    sits above both. `year` leading changes neither side of it."""
    definition = shipped.definitions[(D30, 1)]
    assert definition.default_order.order_id == EMPLOYER_FIRST
    order = {d.role_ref: d.order_index
             for d in definition.default_order.dimensions}
    assert order["employer_org"] < order["cycle_period"]
    assert order["employer_org"] < order["role_title"] < order["cycle_period"], (
        "`00`:70 puts the role straight after the company")
    alternative = next(o for o in definition.candidate_orders
                       if o.order_id == CYCLE_FIRST)
    other = {d.role_ref: d.order_index for d in alternative.dimensions}
    assert other["cycle_period"] < other["employer_org"]


# --- what the situation now builds, and what it did not disturb ---------------

def test_the_shipped_situation_answers_107s_career_application_order(shipped):
    answered = tuple((lvl.field, lvl.label, lvl.requirement)
                     for lvl in folder_levels_for(shipped, SITUATION))
    assert answered == EXPECTED_LEVELS


def test_the_year_level_is_the_files_own_and_never_the_groups(shipped):
    """`production.GROUP_LEVEL_ROLES` names `holder_institution` under `academic`
    and nothing under `career`, so `year` resolves once per FILE. That is what
    lets a corpus spanning two years divide the level at all."""
    assert group_level_fields_for(shipped, SITUATION) == frozenset()


def test_the_tenure_row_is_untouched_by_the_definition_gaining_a_dimension(
        shipped):
    """`107`'s Current work wants `project` and `stage`, which career declares
    neither of and which are the owner's alone to mint -- so this change stops at
    the recruiting row. `folder_levels_for` skips a dimension the row does not
    bind, and this is that skip measured rather than assumed."""
    row = shipped.applicabilities[("ap.career.employment-records", 1)]
    assert "capture_time" not in {b.role_ref for b in row.role_bindings}
    assert "year" not in row.allowed_fields
    answered = tuple((lvl.field, lvl.label, lvl.requirement)
                     for lvl in folder_levels_for(shipped, TENURE))
    assert answered == TENURE_LEVELS


def test_the_domain_life_and_template_are_unchanged(shipped):
    assert schema_for_situation(shipped, SITUATION) == "career"
    assert life_of(shipped, SITUATION) == "Career"
    assert template_id_for_situation(shipped, SITUATION) == D30


def test_the_release_still_reports_208_situations_and_only_recruiting_moved(
        shipped):
    """`00` amendment 31's own worry, checked against the release as it shipped
    before this change: a replacement must not silently widen or narrow the
    cloud-bound menu, or touch any row but the one it was authorised to replace.

    BOTH changed files are read at the before-SHA, because the dimension lives in
    `definitions.json` and the binding in `wave2_commerce.json`; reading only one
    would compare a half-state against itself.
    """
    import subprocess

    import production

    def at_before(path):
        return subprocess.run(
            ["git", "show", f"{BEFORE_SHA}:src/tree_design/library/{path}"],
            capture_output=True, text=True, check=True).stdout

    before_files = {name: at_before(name)
                    for name in ("wave2_commerce.json", "definitions.json")}

    def read_before(name):
        if name in before_files:
            return before_files[name]
        return read_packaged_library_file(name)

    before_catalogue = load_shipped_catalogue(read_before)
    before = {(row.schema, row.name): row
              for row in shipped_situations(before_catalogue)}
    after = {(row.schema, row.name): row for row in shipped_situations(shipped)}

    assert len(after) == 208
    assert set(before) == set(after), "the set of (schema, situation) rows moved"

    changed = {key for key in before if before[key] != after[key]}
    assert changed == {("career", SITUATION)}, (
        "a row other than career.recruiting changed shape")
    assert before[("career", SITUATION)].folder_levels == OLD_LABELS
    assert after[("career", SITUATION)].folder_levels == (
        YEAR_LABEL, *OLD_LABELS)
