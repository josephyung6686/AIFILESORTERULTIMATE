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

---

**20 SEP: THE OWNER LIFTED THAT BLOCK, AND A SECOND ONE WAS FOUND UNDER IT.** The
ruling is *"Declare `project` and `stage` at `career`. Career gains two EXISTING
fields, then a career row builds `employer -> year -> project -> stage`. Mints no
vocabulary."* Applied as a measurement and reverted, it turns the tripwire above
red exactly as written -- *"a schema now declares employer, project and stage
together ... `['career']`"* -- and `107`'s Current work is STILL not buildable,
because a row needs a second thing the ruling does not supply: **a situation to
recognise.**

`src/recognition/` compiled seven `career` rows. Three are filed by shipped rows,
three are refused on a key the ruling does NOT declare, and the seventh is the kind
anchor. A second row on a filed situation is refused by `folder_levels_for`, and
minting `career.<something>` is a new member of a closed vocabulary -- the one thing
the ruling says it does not do. **THE ANCHOR IS THE EXCEPTION AND IT IS LEFT OPEN**:
filing it would mint nothing, it passes every test, and one row in the release
already does it (`ap.nonprofit.restricted-fund` cites `recognition:nonprofit`). What
it costs is a product decision and not this file's to take -- see the last test.

So the LAST three tests in this file were added: the census that makes the second
blocker checkable, the mutation that closes the way round it, and the TARGET as a
strict xfail that flips to passing the day the row ships. **The field half of the
ruling is deliberately NOT built here.** Declaring two destination-eligible keys
with no row that binds them is not neutral: `facts.domains.active_field_allowlist`
is built on `DOMAIN_FIELDS`, so a `project` fact becomes proposable on every career
file, and `model_template.file_fits_its_situation` makes *"a fact with no level"*
UNFIT at site E. That is the cost `00` amendment 22 argued binding `year` REMOVES,
bought back on every career file, and it buys it for as long as the row is owed.
"""
from __future__ import annotations

import copy
import json
import pathlib

import pytest

import tree_design
from facts.domains import SCHEMA_IDS
from facts.fields import DOMAIN_FIELDS, FIELD_ROWS
from production import (
    folder_levels_for, load_shipped_catalogue, read_packaged_library_file,
    shipped_situations,
)
from tree_design.config import ConfigurationRequired

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


#: `107`'s Current work, as an order of P6 field keys. The year is universal; the
#: other three are what the owner's 20 Sep ruling declares at `career`.
CURRENT_WORK_ORDER = ("employer", "year", "project", "stage")

#: The three `career` situations the release RECOGNISES and files nowhere, each
#: beside the key its own recommendation needs and `career` still does not declare
#: once `project` and `stage` are added. The refusal SENTENCES live in
#: `tests/p10/test_library_commerce.py::REFUSED`; what is kept here is the key,
#: because a key is checkable against the live catalogue and a sentence is not.
#:
#: `00` amendment 31's first use is the precedent for why this matters: a refused
#: row is refused *"because a key is missing, not by taste"*, so declaring the key
#: is what asks for the row. The 20 Sep ruling declares two keys and frees NONE of
#: these three -- which is the finding this table exists to make checkable.
REFUSED_CAREER_SITUATIONS = {
    "career.consulting-client-engagement": "client",
    "career.credentials-licenses": "issuing_body",
    "career.portfolio-work-samples": "artifact_type",
}


def compiled_career_rows() -> frozenset[str]:
    """Every `career` row `src/recognition/` compiled, read through the file.

    Read rather than restated, for `test_p10_pipeline`'s reason: the point of the
    census below is that the recognition vocabulary and the template library are
    ONE and cannot drift, and a transcription here would drift first.
    """
    manifest = json.loads(
        (pathlib.Path(tree_design.__file__).parent.parent / "recognition" /
         "library" / "recognition.json").read_text(encoding="utf-8"))
    return frozenset(manifest["schemas"]["career"]["rows"])


def test_the_20_sep_ruling_frees_no_career_situation_to_carry_current_work(shipped):
    """WHY THE TARGET ABOVE CANNOT BE TURNED GREEN BY AUTHORING A ROW.

    The owner's 20 Sep ruling settles the KEYS -- *"Declare `project` and `stage`
    at `career`"* -- and a row needs one thing more that the ruling does not
    supply: a SITUATION to recognise. `folder_levels_for` and `shipped_situations`
    are both keyed on `detection_signal_refs`, and
    `test_library_commerce.py::test_every_detection_signal_names_a_compiled_recognition_row`
    requires that signal to name a row `src/recognition/` compiled. So the set of
    situations a new row may cite is closed, and this is that set, enumerated.

    **ALL SEVEN ARE SPOKEN FOR AND NONE OF THEM IS `107`'s CURRENT WORK.** Three
    are already filed, and a second row on a filed situation makes
    `folder_levels_for` refuse outright -- asserted below by mutation. Three are
    refused, and each is refused on a key the ruling does NOT declare, so the
    ruling frees none of them. The seventh is the kind anchor.

    **THE ANCHOR IS THE ONE SIGNAL THAT WOULD MINT NOTHING, AND IT IS LEFT OPEN
    RATHER THAN CLOSED.** It passes every mechanical test -- the node exists, is
    `refuse_node: false`, carries a deterministic block and compiled -- and filing
    a bare kind anchor is not unprecedented: `ap.nonprofit.restricted-fund` cites
    `recognition:nonprofit`, asserted below so the precedent is measured and not
    remembered. What the anchor declares of its own is nothing (`dimension_order:
    []`); its recommendation is held as prose and is a DIFFERENT shape from
    `107`'s -- *"company first ... then role or recruiting cycle ... then document
    type"*, three levels with no project, no stage and no year.

    **WHAT IT WOULD COST IS A PRODUCT DECISION, WHICH IS WHY THIS FILE DOES NOT
    TAKE IT.** `cli.signals_for_branch` gives a SETTLED branch exactly one signal,
    `recognition:{branch.situation}`, so filing the anchor would not hand
    `career.recruiting` a second row and C4 would not refuse -- the route is
    mechanically clean. An UNSETTLED branch offers one signal per situation its
    FILES were judged to hold, and `00` amendment 30 rules that the judge names
    the KIND: *"the judge names the KIND, and which situation within it remains
    the person's answer."* So the anchor row would become the recipe for every
    career branch nobody has settled -- and 218 of 257 situation facts carry only
    the kind. Résumés and offer letters would be offered `employer -> year ->
    project -> stage` by default. That may be what the owner wants and it is not
    for this file to decide.

    **SO THE REMAINING ACT IS A NAME OR A DEFAULT, AND BOTH ARE THE OWNER'S.**
    Either a new `career.*` situation -- a researched node with its own recognition
    block, compiled into `recognition.json`, which is a new member of a closed
    vocabulary -- or the ruling that the kind anchor may carry Current work. The
    ruling says it *"mints no vocabulary"*, and on the field half that is exactly
    true. On the row half it is true only under the second route. Recorded in `00`
    amendment 35a's shape: the rule and the ruling disagree, it was not known when
    the ruling was given, and the owner is told rather than the disagreement being
    resolved by whoever noticed it.
    """
    compiled = compiled_career_rows()
    filed = {situation.name for situation in shipped_situations(shipped)
             if situation.schema == "career"}
    assert filed == {"career.employer-side-hiring", "career.employment-records",
                     "career.recruiting"}, sorted(filed)
    assert compiled == {"career"} | filed | set(REFUSED_CAREER_SITUATIONS), (
        "the career situations a row may cite have moved. A name that is neither "
        "filed nor refused is a free situation, and 107's Current work is owed "
        f"one: {sorted(compiled)}")

    # THE RULING'S OWN KEYS, applied. None of the three refusals is freed by them,
    # so none becomes available to carry Current work.
    ruled = set(DOMAIN_FIELDS["career"]) | {"project", "stage"}
    for node_id, still_missing in REFUSED_CAREER_SITUATIONS.items():
        assert still_missing not in ruled, (node_id, still_missing)

    # The anchor declares no dimensions of its own, so a row filing it would be
    # supplying the whole recipe rather than restoring one the research recorded.
    anchor = json.loads(
        (pathlib.Path(__file__).resolve().parents[2] / "planning" / "domains" /
         "nodes" / "career.json").read_text(encoding="utf-8"))
    assert anchor["refuse_node"] is False
    assert anchor["template"]["dimension_order"] == []

    # AND FILING A BARE KIND ANCHOR HAS A PRECEDENT, measured across the release
    # rather than remembered. It is one row, and it is not career's -- so the
    # route is open and untravelled here, which is what makes it a decision.
    anchors = sorted(
        (row.applicability_id, signal.removeprefix("recognition:"))
        for row in shipped.applicabilities.values()
        for signal in row.detection_signal_refs
        if signal.removeprefix("recognition:") in set(SCHEMA_IDS))
    assert anchors == [("ap.nonprofit.restricted-fund", "nonprofit")], anchors


def test_a_second_row_on_a_filed_situation_is_refused_rather_than_ranked():
    """The discriminating half, mutated from a REAL shipped record.

    The tempting way round the census above is to leave the situation alone and
    add a SECOND applicability row citing it -- `recognition:career.employment-
    records` carrying Current work's order beside the tenure row's. The library
    refuses it, and refuses it for the reason that makes the refusal right rather
    than merely strict: *"which folders these files should be filed under is the
    person's answer to give rather than this module's to pick."*
    """
    original = json.loads(read_packaged_library_file("wave2_commerce.json"))
    tenure = next(row for row in original["applicabilities"]
                  if row["applicability_id"] == "ap.career.employment-records")
    twin = copy.deepcopy(tenure)
    twin["applicability_id"] = "ap.career.current-work"

    def read(name: str) -> str:
        if name != "wave2_commerce.json":
            return read_packaged_library_file(name)
        mutated = copy.deepcopy(original)
        mutated["applicabilities"].append(twin)
        return json.dumps(mutated)

    catalogue = load_shipped_catalogue(read)
    with pytest.raises(ConfigurationRequired) as excinfo:
        folder_levels_for(catalogue, "career.employment-records")
    assert "2 applicability rows" in str(excinfo.value)


@pytest.mark.xfail(strict=True, reason=(
    "107's Current work has no situation to be a row FOR. The owner's 20 Sep "
    "ruling settles the keys and the name is still owed -- see "
    "test_the_20_sep_ruling_frees_no_career_situation_to_carry_current_work. "
    "STRICT: this flips to passing the day the row ships, and the suite goes red "
    "if it ships without this file being read."))
def test_107s_current_work_is_a_shipped_situation(shipped):
    """THE TARGET. Some shipped situation builds `107`'s Current work order."""
    built = {situation.name: tuple(
        level.field for level in folder_levels_for(shipped, situation.name))
        for situation in shipped_situations(shipped)}
    carrying = sorted(name for name, order in built.items()
                      if order == CURRENT_WORK_ORDER)
    assert carrying, (
        "no shipped situation builds employer -> year -> project -> stage; the "
        f"release carries {len(built)} situations and career's are "
        + str(sorted(n for n in built if n.startswith("career"))))
