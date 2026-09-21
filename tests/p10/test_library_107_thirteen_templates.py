# tests/p10/test_library_107_thirteen_templates.py
"""`107`'s thirteen branch templates, measured against the shipped library.

`107` §Branch templates is a table of THIRTEEN rows, each naming a default split
order the product promises -- *"a library of branch templates whose split
dimensions, labels, privacy behavior, and maximum useful depth can be
customized."* Twelve of the thirteen are answered by an applicability row over a
shipped situation; one is answered by machinery that is not the library at all.
This file is the census of which, so that the day a row lands or regresses the
suite says so instead of a later reader re-deriving it.

**THIS FILE EXISTS BECAUSE A PROBE OVER FIELD KEYS ANSWERED THREE ROWS WRONG.**
Three rows -- Travel, Reference, Residual -- were carried as UNVERIFIED because
the probe that measured them searched `facts/fields.py` for `trip`, `topic` and
`residual_state`. **None of the three is a field key**, and neither are `program`,
`rendition` or `person`, the other words `107` uses for a level. Asserted below
against the live 59-row vocabulary. The library does not spell `107`'s words as
KEYS; it spells them as LABELS on generic keys, and the label is the half a
key-only probe cannot see:

    107 says            the library binds         and labels it
    trip                event                     "Trip"        (travel.trip-photos)
    topic               project                   "Topic"       (research.reading-library)
    function            record_type               "What it is for"  (draft)
    rendition           media_type                "Photos or videos"
    residual state      -- not a field at all --  a residual TEMPLATE NAME

So a key-only probe returns nothing for a row that is fully built, and the
correct response to nothing is to look at what the row DOES bind rather than to
report the row absent. `folder_levels_for` answers with both halves and is what
this census reads.

**THE VERDICTS AND WHAT EACH ONE MEANS.**

* `BUILT` -- some shipped situation builds `107`'s order. Pinned by NAME and by
  the exact field order, for the reason
  `test_library_year_is_bound_nowhere_else.py` gives: a count cannot say WHICH,
  and a build that moved the order to a different row while retiring this one
  would satisfy a count exactly.
* `PARTIAL` -- some levels build and named ones do not. The missing level is
  named here, and so is the reason it is missing, because the two kinds are not
  the same repair: a level with no field in the vocabulary is the owner's to mint
  (`00` amendment 31: a row is refused *"because a key is missing, not by
  taste"*), and a level whose field exists but is not referenced at this schema
  is a declaration.
* `DELIVERED_ELSEWHERE` -- the row is real and no library row answers it. Exactly
  one row is this, and finding out which was the point of the exercise.

**NO ROW IS `ABSENT`.** The fourth verdict is defined and unused, and that is
itself the census's headline: every one of `107`'s thirteen is reachable today in
some measure.
"""
from __future__ import annotations

import json
import pathlib

import pytest

import tree_design
from facts.fields import DOMAIN_FIELDS, FIELD_ROWS
from production import (
    LIBRARY_FILES, folder_levels_for, load_shipped_catalogue,
    read_packaged_library_file, shipped_situations,
)
from tree_design.vocabulary import RESIDUAL_TEMPLATE_NAMES, REVIEW_AND_UNSORTED

LIBRARY = pathlib.Path(tree_design.__file__).parent / "library"

BUILT = "BUILT"
PARTIAL = "PARTIAL"
DELIVERED_ELSEWHERE = "DELIVERED_ELSEWHERE"
ABSENT = "ABSENT"

#: `107`'s thirteen rows, each against what the release actually builds.
#:
#: ``(verdict, situation, built_order)``. ``situation`` is the shipped situation
#: whose row answers `107`'s template, or `None` where no library row does.
#: ``built_order`` is `folder_levels_for`'s answer for it, field keys in order.
#:
#: A row is listed ONCE even where several situations build the same shape --
#: the named one is the closest reading of `107`'s own representative-files
#: column, and `test_the_named_situation_is_not_the_only_reading` keeps the
#: choice honest by refusing to let the census pass on a name that no longer
#: builds the shape while a sibling does.
THIRTEEN = {
    # ---- BUILT: a shipped situation builds `107`'s order --------------------
    # `Employer -> year -> project or activity -> stage`. `00` amendments 41 and
    # 42; pinned by name in `test_library_year_is_bound_nowhere_else.py`.
    "Current work": (
        BUILT, "career.current-work",
        ("employer", "year", "project", "stage")),
    # `Year -> organization and role -> application stage`. `00` amendment 33
    # wired it, 35 labelled it. CAVEAT recorded rather than hidden: `107` asks
    # 3-4 levels and this builds five, spelling "organization and role" as two
    # levels and "application stage" as `recruiting_cycle` ("My search") plus
    # `work_type` ("What I sent them"). The `stage` key exists and is NOT bound
    # here. The order is `107`'s; the arity is not.
    "Career applications": (
        BUILT, "career.recruiting",
        ("year", "target_employer", "job_title", "recruiting_cycle",
         "work_type")),
    # `Institution -> term -> course -> teaching function`, exactly.
    "Teaching": (
        BUILT, "academic.teaching",
        ("school", "term", "subject", "work_type")),
    # `Project -> stage or artifact class`. `107` allows 2-4; this builds both
    # of the alternatives the "or" offers, in three levels.
    "Projects": (
        BUILT, "research.thesis-dissertation",
        ("project", "artifact_type", "stage")),
    # `Tax year -> record class`, exactly, at `107`'s own depth of 2.
    "Taxes": (
        BUILT, "finance.tax-filings",
        ("tax_year", "record_type")),
    # `Year -> event -> rendition`. ONE of the nine `photos` rows reaches all
    # three; the other eight stop at two. CAVEAT: `media_type` is labelled
    # "Photos or videos" and `107`'s rendition column is HEIC/JPG/RAW/PNG/MOV --
    # the LEVEL is built and the vocabulary inside it is coarser than `107`'s.
    "Photos": (
        BUILT, "photos.social-media-export",
        ("capture_year", "event", "media_type")),
    # `Status or topic -> subtype`, at `107`'s own depth of 2, as the TOPIC
    # half: `project` labelled "Topic", `artifact_type` labelled "Kind of
    # reading". The STATUS half is the residual side -- `Reading Inbox` and
    # `Review Later` are two of the nine names below.
    "Reference": (
        BUILT, "research.reading-library",
        ("project", "artifact_type")),

    # ---- PARTIAL: some levels build, named ones do not ----------------------
    # `Institution -> program -> term -> course -> work type`. Four of five.
    # MISSING: `program`, which is not a field key anywhere -- asserted by
    # `test_107s_words_are_labels_and_not_keys`.
    "Coursework": (
        PARTIAL, "academic.coursework",
        ("school", "term", "subject", "work_type")),
    # `Person -> context -> year or cycle -> record type`. Three of four.
    # MISSING: the person level, and it is UNBUILDABLE rather than unbound --
    # every person-naming key in the vocabulary is `destination_eligible=False`,
    # asserted below. `107` line 120 is why.
    "Family records": (
        PARTIAL, "academic.k12-schooling",
        ("school", "term", "work_type")),
    # `Property -> function -> project or year`. One of three.
    # MISSING: the property level and the project-or-year level. `property` IS
    # destination-eligible, and is declared at `construction_property` alone --
    # a Career-life schema -- so no situation in the Home and Property life can
    # reach it. Asserted below.
    "Property": (
        PARTIAL, "finance.household-property",
        ("record_type",)),
    # `Person -> year or durable category -> record type`. One of three, and
    # the one row in the whole Health life is an INSURANCE row: `institution`
    # is "Health plan", which is not one of `107`'s three dimensions.
    # MISSING: person (unbuildable, as above) and year-or-durable-category.
    "Health": (
        PARTIAL, "finance.insurance-healthcare",
        ("institution", "record_type")),
    # `Year -> trip -> function`. One of three, and the one is the level the
    # key-only probe missed: `event` labelled "Trip".
    # MISSING: year (bound on NO travel row) and function.
    # The draft that closes it is measured in
    # `test_the_travel_draft_would_close_the_row_and_is_gated_twice`.
    "Travel": (
        PARTIAL, "travel.trip-photos",
        ("event", "location")),

    # ---- DELIVERED_ELSEWHERE -----------------------------------------------
    # `Residual state -> optional broad subtype`. NOT a library row and not a
    # situation: `107` §Residual structure is answered by `tree_design/
    # residuals.py` over the nine names of `00` §7.3, under `98 Review and
    # Unsorted`. Measured in `test_residual_is_not_a_library_row_at_all`.
    "Residual": (DELIVERED_ELSEWHERE, None, ()),
}

#: The words `107` uses for a level that are NOT field keys. The first three are
#: what the earlier probe searched for and found nothing; the other three are
#: the same failure waiting for the next reader. A key landing here is not a
#: regression -- it is the signal that this table needs re-measuring, which is
#: why the assertion carries that sentence rather than a bare equality.
WORDS_THAT_ARE_NOT_KEYS = ("trip", "topic", "residual_state", "program",
                           "rendition", "person")

#: Every key in the vocabulary that names a person. `107` line 120: *"client,
#: patient, employee, and candidate names should not be generated as folder
#: levels by default."* Family records and Health both ask for a person level
#: and neither can have one, because a level is built from a destination-
#: eligible key and none of these is one. `client` is the exception and is NOT
#: a person level -- `test_library_year_is_bound_nowhere_else.py` settles that
#: it is the counterparty of the `our_firm` split.
PERSON_NAMING_KEYS = ("people", "subject_of_record", "account_holder",
                      "authored_by")

TRAVEL_DRAFT = "drafts/health_travel.json"


@pytest.fixture()
def shipped():
    return load_shipped_catalogue(read_packaged_library_file)


@pytest.fixture()
def built(shipped):
    """Every shipped situation beside the field order it builds."""
    return {situation.name: tuple(
        level.field for level in folder_levels_for(shipped, situation.name))
        for situation in shipped_situations(shipped)}


def test_the_census_of_107s_thirteen_templates(built):
    """THE CENSUS. Every row of `107`'s table, against what the release builds.

    Read off `folder_levels_for` over the whole release rather than off the rows
    that were built, for the reason the year census gives: the point is the
    tree `107` promises a person, and a build that moved an order to a different
    row would still owe them the same folders. The NAME is pinned anyway,
    because a shape found anywhere is not the same claim as a shape found where
    the product will offer it.
    """
    for template, (verdict, situation, order) in sorted(THIRTEEN.items()):
        if verdict == DELIVERED_ELSEWHERE:
            assert situation is None and order == (), template
            continue
        assert verdict in (BUILT, PARTIAL, ABSENT), (template, verdict)
        assert situation in built, (
            f"107's {template} row is measured against {situation!r}, which the "
            f"release no longer ships; {len(built)} situations are shipped")
        assert built[situation] == order, (
            f"107's {template} row: {situation} builds {built[situation]} and "
            f"this census records {order}. A changed order is not a failure -- "
            "it is a verdict that needs re-measuring, and the verdict here is "
            f"{verdict}")


def test_no_107_row_is_absent_and_exactly_one_is_delivered_elsewhere():
    """The census's headline, asserted rather than left to be counted by eye.

    Thirteen rows; none absent; one answered by machinery that is not the
    library. If a fourteenth verdict class is ever needed the table above is
    wrong, and if `Residual` stops being the only `DELIVERED_ELSEWHERE` row then
    something else has left the library, which is a thing to notice.
    """
    assert len(THIRTEEN) == 13, sorted(THIRTEEN)
    verdicts = {name: v for name, (v, _, _) in THIRTEEN.items()}
    assert ABSENT not in verdicts.values(), (
        "a 107 row has become unreachable: " +
        str(sorted(n for n, v in verdicts.items() if v == ABSENT)))
    assert [n for n, v in verdicts.items() if v == DELIVERED_ELSEWHERE] == [
        "Residual"]


def test_107s_words_are_labels_and_not_keys():
    """THE TRIPWIRE, and the reason three rows were carried as UNVERIFIED.

    A probe that searches the field vocabulary for `107`'s WORDS finds nothing
    for a row that is fully built, because the library spells the word as a
    LABEL on a generic key. The day one of these words becomes a real key, this
    goes red -- and red here means *re-measure the table above*, not *something
    broke*. That is written into the assertion message so a later reader does
    not have to find this docstring to know it.
    """
    keys = {row.field_key for row in FIELD_ROWS}
    landed = [word for word in WORDS_THAT_ARE_NOT_KEYS if word in keys]
    assert landed == [], (
        f"{landed} are now field keys. 107 uses these words for LEVELS and the "
        "library has until now spelled every one of them as a label on a "
        "generic key -- so a row this census calls PARTIAL for want of the "
        "level may now be buildable. Re-measure THIRTEEN above.")

    # AND THE OTHER HALF: the labels are really there, so the census is not
    # reading its own table back. Each pair is (situation, key, label).
    labelled = {(row.applicability_id, binding.field_ref, binding.label)
                for row in load_shipped_catalogue(
                    read_packaged_library_file).applicabilities.values()
                for binding in row.role_bindings}
    assert ("ap.travel.trip-photos", "event", "Trip") in labelled
    assert ("ap.research.reading-library", "project", "Topic") in labelled


def test_the_two_partial_rows_that_ask_for_a_person_cannot_have_one():
    """Family records and Health, and why their missing level is not a bug.

    `107` gives both a person level and `107` line 120 forbids generating person
    names as folder levels by default. The library implements the prohibition
    where it counts: every person-naming key is live and NOT
    destination-eligible, and a level cannot be built from a key that is not.
    So the person level is UNBUILDABLE, not merely unbound -- which is a
    different repair from the other three PARTIAL rows and is recorded as one.
    """
    eligible = {row.field_key for row in FIELD_ROWS if row.destination_eligible}
    live = {row.field_key for row in FIELD_ROWS}
    for key in PERSON_NAMING_KEYS:
        assert key in live, key
        assert key not in eligible, (
            f"{key} names a person and has become destination-eligible; 107 "
            "line 120 says person names are not generated as folder levels by "
            "default, and Family records' and Health's missing person level is "
            "recorded as unbuildable on the strength of this")


def test_propertys_missing_level_is_a_declaration_and_not_a_missing_key(built):
    """Property, and the difference between the two kinds of missing level.

    `property` is a real, destination-eligible key -- so `107`'s Property row is
    NOT blocked the way Coursework's `program` is. It is declared at
    `construction_property` and nowhere else, and `construction_property` is a
    Career-life schema, so the thirteen rows that build a property level are all
    somebody's job and none of them is the person's home. That is a declaration
    the owner can make, not a vocabulary the owner must mint.
    """
    eligible = {row.field_key for row in FIELD_ROWS if row.destination_eligible}
    assert "property" in eligible
    assert [s for s, f in DOMAIN_FIELDS.items() if "property" in f] == [
        "construction_property"]
    assert "property" not in built["finance.household-property"]
    assert "property" not in built["finance.hoa-residents-association"]


def test_travels_year_is_bound_on_no_travel_row(shipped):
    """Travel's OTHER missing level, and why it is not `107`'s year problem.

    `00` amendment 22 binds `year` in exactly two rows and nowhere else --
    `test_library_year_is_bound_nowhere_else.py` is that sentence. So Travel's
    year is not a row that forgot to bind an available key; it is a level
    amendment 22 does not currently license, and the draft below is the request
    to widen it. Recorded here so the two facts are read together.

    `capture_time` is the role a `photos` row uses for its year, and
    `travel.trip-photos` -- a `photos`-schema row -- does not bind it at all.
    Read off `role_bindings` and not off the built levels, because an unbound
    role and a bound-but-unbuilt one are different states and only the binding
    says which this is.
    """
    travel = {row.applicability_id: row
              for row in shipped.applicabilities.values()
              if row.applicability_id.startswith("ap.travel.")}
    assert sorted(travel) == ["ap.travel.bookings-confirmations",
                              "ap.travel.trip-photos"], sorted(travel)
    for row in travel.values():
        bound = {binding.field_ref for binding in row.role_bindings}
        assert "year" not in bound, row.applicability_id
        assert "capture_year" not in bound, row.applicability_id
        roles = {binding.role_ref for binding in row.role_bindings}
        assert "capture_time" not in roles, row.applicability_id


def test_the_travel_draft_would_close_the_row_and_is_gated_twice(shipped):
    """Travel's answer in full: a draft exists, builds `107`'s order exactly,
    and is wired to nothing behind TWO gates rather than one.

    `tests/p10/test_library_health_travel.py` is the draft's own file and its
    gate test reads: *"DELETE THIS TEST when the owner ratifies the names and
    the lead appends the draft to `src/tree_design/library/` and its name to
    `production.LIBRARY_FILES`. Until then it is the check that no drafted name
    can reach the cloud menu `cli.py` builds."* That gate is pinned there and is
    NOT duplicated here.

    WHAT IS PINNED HERE is the second blocker, because a reader of the census
    above will ask what ratification costs and the answer is not "one signature".
    The draft's own `travel.trip-records` binds `event` at the `finance` schema,
    which does not reference it -- `test_the_dependencies_are_exactly_the_ones_
    the_draft_declares` asserts that gap by name. And the draft binds `year` three
    MORE times -- taking the release from two bindings to FIVE -- where `00`
    amendment 22 licenses two and no more. So ratifying the names does not ship
    the row, and this census says so rather than implying that Travel is one
    decision away.
    """
    draft = json.loads((LIBRARY / TRAVEL_DRAFT).read_text(encoding="utf-8"))
    trip = next(row for row in draft["applicabilities"]
                if row["applicability_id"] == "ap.travel.trip-records")
    order = tuple(binding["field_ref"] for binding in trip["role_bindings"])
    assert order == ("year", "event", "record_type"), order
    assert [binding["label"] for binding in trip["role_bindings"]] == [
        "Year", "Trip", "What it is for"]

    # Blocker one: `event` is not referenced at the schema the row files under.
    assert "event" not in DOMAIN_FIELDS["finance"]

    # Blocker two: the draft binds `year` on three rows, which would take the
    # release from two bindings to FIVE where amendment 22 licenses two.
    # Counted over the DRAFT and over the release separately, so the shipped
    # census next door stays the authority on what is bound today.
    drafted_years = [row["applicability_id"] for row in draft["applicabilities"]
                     for binding in row["role_bindings"]
                     if binding["field_ref"] == "year"]
    assert len(drafted_years) == 3, drafted_years
    shipped_years = {row.applicability_id
                     for row in shipped.applicabilities.values()
                     for binding in row.role_bindings
                     if binding.field_ref == "year"}
    assert len(shipped_years) == 2, sorted(shipped_years)


def test_residual_is_not_a_library_row_at_all(shipped, built):
    """`107`'s Residual row, and the finding that it is not the library's.

    The census above measures twelve rows against applicability rows because
    that is what the other twelve ARE. Residual is not: `107` §Residual
    structure is answered by `tree_design/residuals.py` over the nine names `00`
    §7.3 fixes, projected into the tree by `project_residual_nodes` under
    `98 Review and Unsorted`, and enabled one at a time by the person. No
    situation, no applicability row, no schema.

    **`residuals.json` IS NOT IN THE PACKAGED LIBRARY**, which is the mechanical
    proof rather than the argument: `production.read_packaged_library_file`
    refuses it by name, so nothing that reads the template library can reach the
    residual library at all. They are two libraries in one directory.

    **AND `107`'s SECOND LEVEL IS AUTHORED AND UNREACHABLE.** `107` promises
    *"Residual state -> optional broad subtype"* at depth 1-2. Level one is the
    template name. Level two is `optional_shallow_subfolders`, which exactly ONE
    of the nine authors -- `Reference Clips`, with six -- and which
    `ResidualTemplate` carries and nothing in `src/` reads after construction.
    That is named here and not fixed here.
    """
    # Nothing in the template library answers it.
    assert not [name for name in built if name.startswith("residual")]
    assert REVIEW_AND_UNSORTED == "98 Review and Unsorted"
    assert len(RESIDUAL_TEMPLATE_NAMES) == 9, RESIDUAL_TEMPLATE_NAMES

    # The two libraries are separate, and the loader says so out loud.
    assert "residuals.json" not in LIBRARY_FILES
    assert (LIBRARY / "residuals.json").is_file()

    # Level two: authored on one of the nine, and on no other.
    raw = json.loads((LIBRARY / "residuals.json").read_text(encoding="utf-8"))
    authored = sorted(name for name in RESIDUAL_TEMPLATE_NAMES
                      if raw[name]["optional_shallow_subfolders"])
    assert authored == ["Reference Clips"], (
        "107's optional broad subtype is authored per residual template; a "
        f"second template authoring one changes the Residual verdict: {authored}")
    assert len(raw["Reference Clips"]["optional_shallow_subfolders"]) == 6

    # `107` §Residual structure names SEVEN states and `00` §7.3 ships NINE.
    # They are different ratified vocabularies rather than a shortfall, and the
    # overlap is measured so that a later reader does not treat one as the
    # other's census.
    hundred_and_seven = {"Ambiguous Documents", "Standalone PDFs",
                         "One-Off Images", "Unclear Spreadsheets",
                         "Possible Duplicates and Versions",
                         "Unsupported or Encrypted", "Deferred Decisions"}
    assert len(hundred_and_seven) == 7
    assert hundred_and_seven & set(RESIDUAL_TEMPLATE_NAMES) == {
        "One-Off Images", "Unsupported or Encrypted"}


#: Every OTHER shipped situation that builds the same field order as the row the
#: census names, measured over the release. Several rows reaching one shape is
#: the library doing its job and is recorded rather than forbidden -- but it is
#: recorded, because a shape reached by eight rows and a shape reached by one are
#: different claims about `107`, and only one of them survives a row being
#: retired.
SIBLING_SHAPES = {
    "Career applications": (),
    "Coursework": ("academic.teaching",),
    "Current work": (),
    "Family records": (),
    "Health": ("finance.cap-table-equity", "finance.crypto-assets",
               "finance.hoa-residents-association", "finance.insurance-personal",
               "finance.receipts-expenses", "finance.student-financial-aid",
               "finance.subscriptions-utilities"),
    "Photos": (),
    "Projects": ("research.dataset-analysis",),
    "Property": ("finance.vehicle-records", "logistics.driver-compliance"),
    "Reference": ("code.notebooks-experiments", "creative.printmaking-editions",
                  "creative.short-form-writing", "research.ethics-compliance"),
    "Taxes": (),
    "Teaching": ("academic.coursework",),
    "Travel": (),
}


def test_how_many_rows_reach_each_107_shape(built):
    """The way round the census: name a situation whose shape a sibling also
    builds, then let the named one drift while a levels-only reader assumes the
    row is still there. Closed by pinning the siblings rather than counting them.

    **AND IT MEASURES THE ONE SENTENCE `107` WRITES ABOUT TWO OF ITS OWN ROWS.**
    `107` §What "perfect" means: *"Coursework and teaching are visibly different
    even when they mention the same institution and course vocabulary."* They
    are each other's ONLY sibling here -- `school -> term -> subject ->
    work_type`, the same four keys in the same order -- so the whole of that
    sentence is carried by the LABELS and by nothing else: "My school" against
    "School I taught at", "Semester" against "Semester I taught", "Course"
    against "Course I taught", "Kind of work" against "Kind of teaching
    material". A build that normalised those labels would satisfy every
    field-order assertion in this file and break `107`'s sentence, so the labels
    are asserted here and not left to the census above.

    Health's seven siblings are the other end of the same measurement and are
    the reason its PARTIAL is a coverage verdict: `institution -> record_type`
    is the generic `finance` shape, and the Health row reaches `107`'s depth by
    being an ordinary financial record rather than a health one.
    """
    for template, (verdict, situation, order) in sorted(THIRTEEN.items()):
        if verdict == DELIVERED_ELSEWHERE:
            continue
        siblings = tuple(sorted(name for name, shape in built.items()
                                if shape == order and name != situation))
        assert siblings == SIBLING_SHAPES[template], (
            f"107's {template} row is built by {situation} and by "
            f"{siblings}; this census recorded {SIBLING_SHAPES[template]}. A "
            "changed sibling set is not a failure -- it is the library gaining "
            "or losing a second way to reach one of 107's shapes")

    # `107`'s own sentence about the two that share a shape, carried by labels.
    labels = {}
    for situation in ("academic.coursework", "academic.teaching"):
        catalogue = load_shipped_catalogue(read_packaged_library_file)
        labels[situation] = tuple(level.label for level in
                                  folder_levels_for(catalogue, situation))
    assert labels["academic.coursework"] == (
        "My school", "Semester", "Course", "Kind of work")
    assert labels["academic.teaching"] == (
        "School I taught at", "Semester I taught", "Course I taught",
        "Kind of teaching material")
    assert not set(labels["academic.coursework"]) & set(
        labels["academic.teaching"]), (
        "Coursework and Teaching build the same four keys in the same order, so "
        "107's 'visibly different' is carried entirely by these labels and a "
        "shared one is that sentence half-broken: " + str(labels))
