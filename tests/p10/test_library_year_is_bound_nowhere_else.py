# tests/p10/test_library_year_is_bound_nowhere_else.py
"""`00` amendment 22's LAST clause, and the half of it that is not buildable.

Amendment 22 reads: *"`year` IS BOUND AS A FOLDER LEVEL WHERE `107` ALREADY SAYS IT
GOES -- Current work (`employer -> year -> project -> stage`) and Career
applications (`year -> organization and role -> application stage`), **and nowhere
else for now**."* Career applications shipped as `ap.career.recruiting` v2 under
amendment 33. This file is the other two-thirds of that sentence: the prohibition,
and the reason the first half has no row to land in.

**`107`'s CURRENT WORK IS NOT A SHIPPED ROW, AND NOT FOR WANT OF AUTHORING.** It is
mechanically unreachable, because its order needs three keys that no one schema
declares:

    employer  declared by  career                               -- and only career
    project   declared by  research code business_operations law_practice
                           creative construction_property engineering government
    stage     declared by  research creative engineering
    ALL THREE declared by  -- nothing

`60` H6.2 settles what that costs: a file whose key is not declared by the active
schema returns unknown and is never re-routed. So `employer -> year -> project ->
stage` cannot be spelled by any of the 208 rows, and no row can be edited into
`107`'s Current work without first REFERENCING `project` and `stage` at `career`.
`109` already ruled who that belongs to -- *"it is extending an EXISTING field to
one more schema, which is a smaller act with a different rule over it ... **It is
still the owner's**"*.

**AND `client` IS NOT THE EMPLOYER WEARING ANOTHER NAME**, which is the reading this
test exists to refuse. Five Career-life rows carry `client -> project -> stage ->
artifact_type`, which is `107`'s SHAPE, and putting `year` after the client would
make one of them look like Current work. It is not:

* `client` is the counterparty of the `our_firm` split, not an employer of record --
  `ap.career.recruiting`'s own exclusions say so in those words, and `facts/fields.py`
  gives `client` `role_split=("our_firm",)`. `60` M12, quoted by
  `ap.career.employment-records`: *"for an employee the employer IS the holder's own
  organization"*. So the holder's employer is the `our_firm` SIDE of that split, and
  `our_firm` is not destination-eligible -- asserted below, because it is the only
  other key that could have carried an employer level.
* `def.making-record`'s own default order records the refusal: *"Not time-first: the
  anchor grants the capture exception to `creative.shoot-day-media` and
  `creative.raw-photo-catalogue` by name and to nobody else."*
* `creative.client-engagement`'s memo requires commissioner-boundary evidence and
  says the client level *"must flatten in an in-house or single-client corpus"* --
  and `107`'s Current work corpus IS in-house: Jordan Lee is an EMPLOYEE, and `107`
  hangs Employment Administration off the same Northstar Health node.
* `107` itself separates them, listing *"enable Freelance"* as a template to turn on
  and *"Combine Career and Work"* as a merge.

**WHAT EACH TEST BELOW CATCHES.** The first goes red the moment `year` is bound in a
second row -- which is the prohibition, and the one thing a shape-matching build
would trip. The second goes red when the block is LIFTED, so the owner extending
`career` is announced to whoever runs the suite next instead of being noticed years
later; its message is an instruction, not a defect.
"""
from __future__ import annotations

import pytest

from facts.fields import DOMAIN_FIELDS, FIELD_ROWS
from production import (
    folder_levels_for, load_shipped_catalogue, read_packaged_library_file,
    shipped_situations,
)

#: The one place amendment 22 has actually been wired, ratified as amendment 33 and
#: labelled by amendment 35. The role is `capture_time` and the label is `Year`,
#: which is amendment 35a's single carved-out tuple in
#: `tests/p10/test_library_commerce.py::_RATIFIED_KEY_LABELS`.
THE_ONE_BINDING = ("ap.career.recruiting", "capture_time", "year", "Year")

#: `107`'s Current work: *Employer -> year -> project or activity -> stage*. The
#: year is universal and needs no schema; these three are what a schema must declare
#: before any row can spell that order.
CURRENT_WORK_KEYS = frozenset({"employer", "project", "stage"})


@pytest.fixture()
def shipped():
    return load_shipped_catalogue(read_packaged_library_file)


def test_year_is_bound_in_exactly_one_row_and_it_is_career_recruiting(shipped):
    """Amendment 22's *"and nowhere else for now"*, read off every row in the
    release rather than off the one row that was built.

    READ OFF `role_bindings` AND NOT ONLY OFF `folder_levels_for`, because those two
    disagree on a half-finished build: `folder_levels_for` skips a role the
    definition has no dimension for, so a second row could bind `year`, build no
    folder, and pass a levels-only assertion while sitting in the library waiting
    for a dimension. The binding is the thing amendment 22 forbids; the level is
    only what the binding does once the recipe agrees.
    """
    bound = tuple(
        (row.applicability_id, binding.role_ref, binding.field_ref, binding.label)
        for row in shipped.applicabilities.values()
        for binding in row.role_bindings
        if binding.field_ref == "year")
    assert bound == (THE_ONE_BINDING,), bound

    built = tuple(
        situation.name for situation in shipped_situations(shipped)
        if any(level.field == "year"
               for level in folder_levels_for(shipped, situation.name)))
    assert built == ("career.recruiting",), built


def test_107s_current_work_cannot_be_spelled_by_any_schema():
    """THE TRIPWIRE. `107`'s Current work is owed a row and has none, and this is
    the sentence that says why in a form the suite can check.

    When this goes red it means the owner has referenced the missing keys at
    `career` and the Current work row is finally buildable -- `109`: *"Reaching
    `107`'s Current work is not minting new closed vocabulary -- it is extending an
    EXISTING field to one more schema ... It is still the owner's, and it is no
    longer a phase."* Build the row then, and delete this test with it.

    THE SECOND ASSERTION CLOSES THE ONLY DOOR ROUND IT. If `employer` is out of
    reach, the next thing a build reaches for is another key meaning "the
    organisation I work for" -- and there are exactly two: `client`, which is the
    OTHER side of the split and is excluded by name, and `our_firm`, which
    `60` calls "the authorship-side identity that is never a destination". A level
    cannot be built from a key that is not destination-eligible, so there is no
    employer level available outside `career` at all.
    """
    able = sorted(schema for schema, fields in DOMAIN_FIELDS.items()
                  if CURRENT_WORK_KEYS <= set(fields))
    assert able == [], (
        "a schema now declares employer, project and stage together, so 107's "
        "Current work -- 'Employer -> year -> project or activity -> stage' -- is "
        f"buildable and amendment 22's first half is owed a row: {able}")

    eligible = {row.field_key for row in FIELD_ROWS if row.destination_eligible}
    assert "our_firm" not in eligible
    assert "employer" in eligible
    assert [s for s, f in DOMAIN_FIELDS.items() if "employer" in f] == ["career"]
