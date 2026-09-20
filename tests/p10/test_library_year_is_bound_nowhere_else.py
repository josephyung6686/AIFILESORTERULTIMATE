# tests/p10/test_library_year_is_bound_nowhere_else.py
"""`00` amendment 22's LAST clause, now that both halves of it are built.

Amendment 22 reads: *"`year` IS BOUND AS A FOLDER LEVEL WHERE `107` ALREADY SAYS IT
GOES -- Current work (`employer -> year -> project -> stage`) and Career
applications (`year -> organization and role -> application stage`), **and nowhere
else for now**."* Career applications shipped as `ap.career.recruiting` v2 under
amendment 33. Current work shipped as `ap.career.current-work` under amendments 41
and 42. This file is the sentence's THIRD clause: the prohibition, which is the one
thing a shape-matching build would trip.

**IT NAMES TWO TREES, SO TWO ROWS ARE PINNED BY NAME AND A THIRD IS STILL REFUSED.**
Until 20 Sep this file pinned ONE row and carried the second as a strict xfail,
because `107`'s Current work was mechanically unreachable: its order needs three
keys that no one schema declared.

    employer  declared by  career                               -- and only career
    project   declared by  research code business_operations law_practice
                           creative construction_property engineering government
    stage     declared by  research creative engineering
    ALL THREE declared by  -- nothing

`60` H6.2 settles what that cost: a file whose key is not declared by the active
schema returns unknown and is never re-routed, so `employer -> year -> project ->
stage` could not be spelled by any of the 208 rows. **`00` amendment 41 declared
`project` and `stage` at `career`**, and recorded the schema as a NAMED EXEMPTION
from `00`:48's six-key ceiling rather than widening the band for everyone --
`107` asks one schema to hold both a job search and the work itself.

**AND A SECOND BLOCKER SAT UNDER THE FIRST.** A row is keyed on a
`detection_signal_ref` that must name a compiled `recognition` row, so the set of
situations a row may cite is CLOSED, and `career`'s seven were all spoken for:
three filed, three refused on keys amendment 41 does not declare, one bare kind
anchor. **`00` amendment 42 minted an eighth** -- `career.current-work`, a
researched node with its own deterministic block -- rather than filing the anchor,
because `cli.signals_for_branch` gives an UNSETTLED branch one signal per situation
its files were judged to hold and amendment 30 has the judge name the KIND, so an
anchor row would have become the recipe for every career branch nobody has settled.
218 of 257 situation facts carry only a kind; résumés and offer letters would have
been offered `employer -> year -> project -> stage` by default. The owner declined
that. The census below is what keeps the eight readable.

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

**WHAT EACH TEST BELOW CATCHES, AFTER THE RE-AIM.** The first pins the two rows
amendment 22 names, by name, and goes red on a third. The second was a TRIPWIRE
announcing that the owner had acted on the keys; it has fired, and it is re-aimed
rather than deleted, because its SECOND half is a live guard that the ruling did
not touch -- `our_firm` is still not destination-eligible and `employer` is still
career's alone, so there is still no employer level available outside `career`. The
third is the census, updated to eight. The fourth closes the way round the census by
mutation. The fifth was the target held as a strict xfail; the xfail is removed and
it is now an ordinary assertion that the release builds `107`'s order.
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

#: THE TWO TREES `00` AMENDMENT 22 NAMES, and the only two places `year` is bound.
#: Career applications was wired as amendment 33 and labelled by amendment 35 --
#: `Year` is amendment 35a's single carved-out tuple in
#: `tests/p10/test_library_commerce.py::_RATIFIED_KEY_LABELS`. Current work was
#: wired as amendments 41 and 42, and its label is deliberately NOT `Year`: 35a
#: says a second row wanting that licence has to come back to the owner, and
#: `Work year` needs no exception while keeping the plain-folder-word preference
#: the owner chose over "The year I applied".
THE_TWO_BINDINGS = (
    ("ap.career.current-work", "capture_time", "year", "Work year"),
    ("ap.career.recruiting", "capture_time", "year", "Year"),
)

#: `107`'s Current work: *Employer -> year -> project or activity -> stage*. The
#: year is universal and needs no schema; these three are what a schema must declare
#: before any row can spell that order, and amendment 41 declares them at `career`.
CURRENT_WORK_KEYS = frozenset({"employer", "project", "stage"})


@pytest.fixture()
def shipped():
    return load_shipped_catalogue(read_packaged_library_file)


def test_year_is_bound_in_exactly_the_two_rows_amendment_22_names(shipped):
    """Amendment 22's *"and nowhere else for now"*, read off every row in the
    release rather than off the rows that were built.

    READ OFF `role_bindings` AND NOT ONLY OFF `folder_levels_for`, because those two
    disagree on a half-finished build: `folder_levels_for` skips a role the
    definition has no dimension for, so a third row could bind `year`, build no
    folder, and pass a levels-only assertion while sitting in the library waiting
    for a dimension. The binding is the thing amendment 22 forbids; the level is
    only what the binding does once the recipe agrees.

    PINNED BY NAME AND NOT BY COUNT. Two rows is what amendment 22 licenses; WHICH
    two is the half a count cannot say, and a build that moved the year onto a
    third tree while retiring one of these would satisfy a count exactly.
    """
    bound = tuple(sorted(
        (row.applicability_id, binding.role_ref, binding.field_ref, binding.label)
        for row in shipped.applicabilities.values()
        for binding in row.role_bindings
        if binding.field_ref == "year"))
    assert bound == THE_TWO_BINDINGS, bound

    built = tuple(sorted(
        situation.name for situation in shipped_situations(shipped)
        if any(level.field == "year"
               for level in folder_levels_for(shipped, situation.name))))
    assert built == ("career.current-work", "career.recruiting"), built


def test_only_career_can_spell_107s_current_work_and_only_through_employer():
    """THE TRIPWIRE THAT FIRED, RE-AIMED RATHER THAN DELETED.

    It was written to go red the day the owner referenced the missing keys at
    `career` -- `109`: *"Reaching `107`'s Current work is not minting new closed
    vocabulary -- it is extending an EXISTING field to one more schema ... It is
    still the owner's, and it is no longer a phase."* `00` amendment 41 is that
    ruling and the test fired exactly as written. What it said when it was written
    was true and is worth keeping: no schema could spell the order, and the row was
    owed.

    IT IS RE-AIMED AND NOT RETIRED BECAUSE THE SECOND HALF IS UNTOUCHED BY THE
    RULING. The ruling declares two keys at one schema; it says nothing about which
    keys may carry an employer, and that is the door this test closes. If `employer`
    is out of reach, the next thing a build reaches for is another key meaning "the
    organisation I work for" -- and there are exactly two: `client`, which is the
    OTHER side of the split and is excluded by name, and `our_firm`, which `60`
    calls "the authorship-side identity that is never a destination". A level cannot
    be built from a key that is not destination-eligible, so there is still no
    employer level available outside `career` at all.

    AND THE FIRST HALF IS NOW A NARROWNESS ASSERTION. `career` is the ONE schema
    that may spell the order, so a second schema gaining all three would be a second
    home for `107`'s Current work and a second recipe to keep in step -- which is
    this project's named defect, not a widening.
    """
    able = sorted(schema for schema, fields in DOMAIN_FIELDS.items()
                  if CURRENT_WORK_KEYS <= set(fields))
    assert able == ["career"], (
        "107's Current work -- 'Employer -> year -> project or activity -> stage' "
        "-- is spelled by `career` under 00 amendment 41 and by no other schema; a "
        f"second one here is a second home for one template: {able}")

    eligible = {row.field_key for row in FIELD_ROWS if row.destination_eligible}
    assert "our_firm" not in eligible
    assert "employer" in eligible
    assert [s for s, f in DOMAIN_FIELDS.items() if "employer" in f] == ["career"]


#: `107`'s Current work, as an order of P6 field keys. The year is universal; the
#: other three are what `00` amendment 41 declares at `career`.
CURRENT_WORK_ORDER = ("employer", "year", "project", "stage")

#: The three `career` situations the release RECOGNISES and files nowhere, each
#: beside the key its own recommendation needs and `career` still does not declare
#: after amendment 41. The refusal SENTENCES live in
#: `tests/p10/test_library_commerce.py::REFUSED`; what is kept here is the key,
#: because a key is checkable against the live catalogue and a sentence is not.
#:
#: `00` amendment 31's first use is the precedent for why this matters: a refused
#: row is refused *"because a key is missing, not by taste"*, so declaring the key
#: is what asks for the row. Amendment 41 declares `project` and `stage` and frees
#: NONE of these three -- each was refused on a key it does not name, which is why
#: `107`'s Current work needed a situation minted for it rather than one of these.
REFUSED_CAREER_SITUATIONS = {
    "career.consulting-client-engagement": "client",
    "career.credentials-licenses": "issuing_body",
    "career.portfolio-work-samples": "artifact_type",
}

#: The four `career` situations a shipped row files, after amendment 42 added the
#: fourth. Named rather than counted: a census that only counted would pass while
#: one row was swapped for another.
FILED_CAREER_SITUATIONS = frozenset({
    "career.current-work", "career.employer-side-hiring",
    "career.employment-records", "career.recruiting",
})


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


def test_amendment_42_mints_one_situation_and_frees_none_of_the_three_refusals(
        shipped):
    """THE CENSUS, and what amendment 42 actually cost.

    `folder_levels_for` and `shipped_situations` are both keyed on
    `detection_signal_refs`, and
    `test_library_commerce.py::test_every_detection_signal_names_a_compiled_recognition_row`
    requires that signal to name a row `src/recognition/` compiled. So the set of
    situations a row may cite is CLOSED, and this is that set, enumerated.

    **BEFORE AMENDMENT 42 ALL SEVEN WERE SPOKEN FOR AND NONE OF THEM WAS `107`'s
    CURRENT WORK.** Three were filed, and a second row on a filed situation makes
    `folder_levels_for` refuse outright -- asserted below by mutation. Three were
    refused, and each is refused on a key amendment 41 does NOT declare, so the
    ruling frees none of them -- re-asserted here after the declaration, which is
    the check that says the two rulings did not accidentally overlap. The seventh
    is the kind anchor.

    **THE ANCHOR WAS THE ONE SIGNAL THAT WOULD HAVE MINTED NOTHING, AND THE OWNER
    DECLINED IT.** It passes every mechanical test -- the node exists, is
    `refuse_node: false`, carries a deterministic block and compiled -- and filing
    a bare kind anchor is not unprecedented: `ap.nonprofit.restricted-fund` cites
    `recognition:nonprofit`, asserted below so the precedent stays measured. What
    stopped it is a product cost and not a mechanical one: `cli.signals_for_branch`
    gives a SETTLED branch exactly one signal, `recognition:{branch.situation}`, so
    filing the anchor would not have handed `career.recruiting` a second row and C4
    would not have refused -- the route is mechanically clean. An UNSETTLED branch
    offers one signal per situation its FILES were judged to hold, and `00`
    amendment 30 rules that the judge names the KIND: *"the judge names the KIND,
    and which situation within it remains the person's answer."* So the anchor row
    would have become the recipe for every career branch nobody has settled, and
    218 of 257 situation facts carry only the kind. Résumés and offer letters would
    be offered `employer -> year -> project -> stage` by default.

    **THE ANCHOR IS THEREFORE STILL UNFILED, AND THAT IS ASSERTED.** The route was
    left open when this file was written and the owner closed it by choosing the
    other one; a later build filing it would be re-taking a decision the owner has
    already taken, so the census below names it as compiled-and-unfiled rather than
    leaving its absence implicit.
    """
    compiled = compiled_career_rows()
    filed = {situation.name for situation in shipped_situations(shipped)
             if situation.schema == "career"}
    assert filed == set(FILED_CAREER_SITUATIONS), sorted(filed)
    assert compiled == {"career"} | filed | set(REFUSED_CAREER_SITUATIONS), (
        "the career situations a row may cite have moved. A name that is neither "
        "filed nor refused is a free situation, and minting one is the owner's "
        f"under 00 amendment 42: {sorted(compiled)}")
    # The kind anchor stays unfiled: amendment 42 chose the other route by name.
    assert "career" not in filed

    # AMENDMENT 41'S OWN KEYS, applied. None of the three refusals is freed by
    # them, so amendment 42's new situation is not one of these wearing a new name.
    ruled = set(DOMAIN_FIELDS["career"])
    assert {"project", "stage"} <= ruled
    for node_id, still_missing in REFUSED_CAREER_SITUATIONS.items():
        assert still_missing not in ruled, (node_id, still_missing)

    # The anchor declares no dimensions of its own, so a row filing it would have
    # supplied the whole recipe rather than restoring one the research recorded.
    anchor = json.loads(
        (pathlib.Path(__file__).resolve().parents[2] / "planning" / "domains" /
         "nodes" / "career.json").read_text(encoding="utf-8"))
    assert anchor["refuse_node"] is False
    assert anchor["template"]["dimension_order"] == []

    # AND FILING A BARE KIND ANCHOR HAS A PRECEDENT, measured across the release
    # rather than remembered. It is one row, and it is not career's -- so the
    # route stays open and untravelled here, which is what made it a decision.
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

    THIS IS WHY AMENDMENT 42 COST A SITUATION. The cheap route was never available:
    the only thing a second row on a filed signal produces is a refusal at the
    point of use, with the cloud-bound menu still serving the first row's labels.
    """
    original = json.loads(read_packaged_library_file("wave2_commerce.json"))
    tenure = next(row for row in original["applicabilities"]
                  if row["applicability_id"] == "ap.career.employment-records")
    twin = copy.deepcopy(tenure)
    twin["applicability_id"] = "ap.career.employment-records-twin"

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


def test_107s_current_work_is_a_shipped_situation(shipped):
    """THE TARGET. Some shipped situation builds `107`'s Current work order.

    HELD AS A STRICT XFAIL UNTIL 20 SEP, with the reason *"107's Current work has
    no situation to be a row FOR."* `00` amendments 41 and 42 supplied the keys and
    the situation, the xfail is removed, and this is now an ordinary assertion. It
    is deliberately written to find the order ANYWHERE in the release rather than
    on a named row: what amendment 22 owes `107` is the tree, and a build that
    moved it to a different row would still owe the person the same folders.
    """
    built = {situation.name: tuple(
        level.field for level in folder_levels_for(shipped, situation.name))
        for situation in shipped_situations(shipped)}
    carrying = sorted(name for name, order in built.items()
                      if order == CURRENT_WORK_ORDER)
    assert carrying == ["career.current-work"], (
        "no shipped situation builds employer -> year -> project -> stage; the "
        f"release carries {len(built)} situations and career's are "
        + str(sorted(n for n in built if n.startswith("career"))))
