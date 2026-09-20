# tests/p10/test_library_career_current_work.py
"""`00` amendment 42: `107`'s Current work gets a situation of its own.

`107`'s branch-template table gives Current work as *Employer -> year -> project or
activity -> stage*, and `00` amendment 22 named it as one of the two places `year`
is bound. Career applications shipped first (`ap.career.recruiting` v2, amendment
33). This is the other half, and it was blocked twice by two different things that
the owner has now ruled on:

* **THE KEYS.** `60` J-3 gives `career` six fields and neither `project` nor `stage`
  is among them, so the order could not be SPELLED --
  `tests/p10/test_library_year_is_bound_nowhere_else.py` measured that no schema in
  the release declares `employer`, `project` and `stage` together. Amendment 41
  declares the two at `career` and records the schema as a NAMED EXEMPTION from
  `00`:48's six-key ceiling, because `107` asks one schema to hold both a job search
  and the work itself.
* **THE SITUATION.** A row is keyed on a `detection_signal_ref` that must name a
  compiled `recognition` row, so the set of situations a row may cite is CLOSED.
  `career` compiled seven and all seven were spoken for -- three filed, three
  refused on keys amendment 41 does not declare, and the bare kind anchor.
  Amendment 42 declined the anchor route, because `cli.signals_for_branch` gives an
  UNSETTLED branch one signal per situation its files were judged to hold and
  amendment 30 has the judge name the KIND, so an anchor row becomes the recipe for
  every unsettled career branch -- and 218 of 257 situation facts carry only a kind.
  A new researched node was ruled instead, and this is the row that cites it.

**WHY A NEW DEFINITION AND NOT A THIRD ORDER ON D30.**
`production.folder_levels_for` reads `definition.default_order.dimensions` -- the
DEFAULT order and only that. Every row on one definition therefore builds in ONE
order, and `def.career-search-and-tenure`'s default is `capture_time`-first for the
recruiting half (amendment 33, ratified 20 Sep). A non-default candidate order
builds nothing at all, so Current work's `employer`-first order needs a definition
of its own. `_check_orders` would also refuse D30 gaining two roles that its
cycle-first order does not carry, because every candidate order of a definition
must cover the SAME role set.

**WHY THE FIELDS AND THE ROW ARE ONE COMMIT.** Amendment 42, verbatim: *"half this
ruling is worse than none."* `facts.domains.active_field_allowlist` is built from
`DOMAIN_FIELDS`, so declaring `project` and `stage` alone makes a `project` fact
proposable on every career file, and `model_template.file_fits_its_situation` makes
a proposal-eligible fact with no level in the file's situation UNFIT at site E --
one template call per file for a fact with nowhere to live, which is precisely the
cost amendment 22 argued binding `year` REMOVES.

**THIS IS AN ADDITION AND NOT A REPLACEMENT**, so amendment 31's second condition is
satisfied trivially on this row and NOT trivially on the release: the test at the
bottom reads the whole cloud-bound menu before and after and requires that exactly
one `(schema, name)` pair appears and that no existing row changes shape -- with
`career.recruiting`'s five labels asserted byte-identical, because it is the row
this one sits closest to and the one a shape-matching edit would reach for.

**THE NAMES AND THE LABELS AWAIT THE OWNER'S RATIFICATION.** `career.current-work`
is a new member of a closed vocabulary and the owner's ruling offered it as
*"`career.current-work` (or your name)"*; the four labels and the node's `name` and
`one_line` -- which the compiler carries into the situation menu a cloud judge is
shown -- are authored here and are owed the owner's word.
"""
from __future__ import annotations

import pytest

from facts.fields import DOMAIN_FIELDS, FIELD_ROWS, UNIVERSAL_FIELDS
from production import (
    folder_levels_for, group_level_fields_for, life_of, load_shipped_catalogue,
    read_packaged_library_file, schema_for_situation, shipped_situations,
    template_id_for_situation,
)

BY_KEY = {row.field_key: row for row in FIELD_ROWS}

SITUATION = "career.current-work"
ROW = "ap.career.current-work"
DEFINITION = "def.employer-project-record"
ORDER = "ord.employer-year-project-stage"

RECRUITING = "career.recruiting"
TENURE = "career.employment-records"

#: `107`, verbatim: *Employer -> year -> project or activity -> stage*. The field
#: keys, the labels this row authors for them, and what each level is worth to a
#: file that has no fact for it.
#:
#: ONLY `employer` IS REQUIRED. A required level with no fact makes the file UNFIT
#: at site E (`model_template.file_fits_its_situation`), and amendment 22's whole
#: argument for binding `year` is that it REMOVES a template call rather than
#: buying one -- so a level `107` asks for optionally is optional here. The
#: employer is the one level the situation is not intelligible without: a status
#: report with no employer is not "current work at an employer", it is a file.
EXPECTED_LEVELS = (
    ("employer", "Where I work", "required"),
    ("year", "Work year", "optional"),
    ("project", "Project or activity", "optional"),
    ("stage", "How far the work got", "optional"),
)

#: The two keys amendment 41 declares at `career`. Neither is minted: `project` is
#: declared at `research` and referenced by seven schemas already, `stage` by three.
DECLARED_BY_41 = ("project", "stage")

#: `ap.career.recruiting`'s five labels, in the order the menu serves them.
#: Amendment 31's second condition, pinned by value rather than by diff so that a
#: rename is caught even if someone re-runs the diff at a later SHA.
RECRUITING_LABELS = ("Year", "Company I applied to", "Job I went for", "My search",
                     "What I sent them")

#: The tenure row's three, for the same reason: it is the other row on the same
#: schema and the one whose `employer` binding this row sits beside.
TENURE_LABELS = ("Where I worked", "Job I held", "Kind of job paperwork")

#: The commit this test is committed on top of -- the last one before the row was
#: wired, and the one that carries amendments 41 and 42 themselves. A FIXED SHA and
#: not `HEAD`, for `test_library_career_recruiting`'s reason: `HEAD` at the time
#: anyone runs this is already the AFTER state, and diffing a commit against itself
#: reports zero change and passes for the wrong reason.
BEFORE_SHA = "2fc672f0"

#: Keys that name a person and may never be a level here. `00` §3.8 forbids
#: authorship as a destination dimension. `client` is the one this row must refuse
#: by name: five Career-life rows carry `client -> project -> stage`, which is
#: `107`'s SHAPE, and `client` is the counterparty of the `our_firm` split rather
#: than an employer of record.
PERSON_NAMING_KEYS = frozenset(
    {"people", "subject_of_record", "account_holder", "client", "instructor",
     "our_firm"})


@pytest.fixture()
def shipped():
    return load_shipped_catalogue(read_packaged_library_file)


# --- the two keys amendment 41 declares ---------------------------------------

def test_the_two_keys_are_declared_at_career_and_minted_nowhere(shipped):
    """Amendment 41 declares EXISTING fields at one more schema. A key that had to
    be minted would be a different ruling, and `109` already drew that line:
    *"it is extending an EXISTING field to one more schema, which is a smaller act
    with a different rule over it."*"""
    for key in DECLARED_BY_41:
        assert key in DOMAIN_FIELDS["career"], key
        assert BY_KEY[key].destination_eligible, key
        # Declared elsewhere, referenced here: the scope is untouched.
        assert BY_KEY[key].scope != "career", key
    # And `year` is still universal, declared by no schema and reachable by all.
    assert "year" in UNIVERSAL_FIELDS
    assert "year" not in DOMAIN_FIELDS["career"]


# --- the row's own shape ------------------------------------------------------

def test_the_row_is_shipped_once_at_version_1(shipped):
    """THE GATE, amendment 31's third condition. This is an ADDITION, so the row
    ships at v1 and there is exactly one row for the signal -- two would make
    `folder_levels_for`, `life_of` and `template_id_for_situation` all refuse."""
    row = shipped.applicabilities[(ROW, 1)]
    assert row.detection_signal_refs == (f"recognition:{SITUATION}",)
    carrying = [r.applicability_id for r in shipped.applicabilities.values()
                if f"recognition:{SITUATION}" in r.detection_signal_refs]
    assert carrying == [ROW], carrying


def test_the_shipped_situation_answers_107s_current_work_order(shipped):
    """`107`: *Employer -> year -> project or activity -> stage*, read through
    `folder_levels_for` -- which is the DEFINITION's order and not the row's, so
    this is the assertion that says the two agree."""
    built = tuple((level.field, level.label, level.requirement)
                  for level in folder_levels_for(shipped, SITUATION))
    assert built == EXPECTED_LEVELS, built


def test_the_row_binds_no_role_the_definition_has_no_dimension_for(shipped):
    """A binding whose role is not a DIMENSION of the definition is silently
    DROPPED by `folder_levels_for` and builds nothing. The row would load, pass
    every shape test, and file nothing -- so the two sides are compared here
    rather than trusted."""
    row = shipped.applicabilities[(ROW, 1)]
    definition = shipped.definitions[(DEFINITION, 1)]
    dimensions = {d.role_ref for d in definition.default_order.dimensions}
    assert {b.role_ref for b in row.role_bindings} == dimensions
    assert len(row.role_bindings) == len(EXPECTED_LEVELS)


def test_the_definition_offers_one_order_and_argues_why(shipped):
    """`TemplateDefinition._check_orders` admits a single candidate order for a
    multi-role recipe only where `sole_order_attestation` records that the corpora
    attest exactly one nesting, *"because an invented alternative is worse than an
    absent one -- the user cannot tell it is invented."* `107` states one nesting
    for Current work and offers no reversal, so the attestation is the honest exit
    and a second order would be the invention the rule exists to stop."""
    definition = shipped.definitions[(DEFINITION, 1)]
    assert [order.order_id for order in definition.candidate_orders] == [ORDER]
    assert definition.default_order.order_id == ORDER
    attestation = definition.sole_order_attestation or ""
    assert len(attestation) > 200
    assert "107" in attestation


def test_the_relative_order_carries_the_nesting_and_not_only_the_order(shipped):
    """`relative_order` is a THIRD required piece and is not a restatement of the
    candidate order. `merge_fragment_constraints` unions it with the fragments'
    edges into one graph and REFUSES with *"unordered relative to each other"*
    rather than falling back -- and a role at the head of the candidate order but
    absent from `relative_order` was *"sorted LAST, silently"*. This recipe carries
    no fragment, so everything it knows about its own nesting is here."""
    from tree_design.templates import merge_fragment_constraints

    definition = shipped.definitions[(DEFINITION, 1)]
    merged = merge_fragment_constraints(
        [], privacy_rank={"baseline": 0, "protected": 1}.__getitem__,
        preferred_order=(), definition=definition)
    assert merged.ordered_roles == tuple(
        d.role_ref for d in sorted(definition.default_order.dimensions,
                                   key=lambda item: item.order_index))


def test_no_current_work_level_names_a_person_or_the_other_side_of_a_split(
        shipped):
    """`00` §3.8 forbids authorship as a destination, and `client` is the refusal
    this row exists closest to: five Career-life rows carry `client -> project ->
    stage`, which is `107`'s shape with the wrong organisation at the top.
    `60` M12: *"for an employee the employer IS the holder's own organization."*"""
    row = shipped.applicabilities[(ROW, 1)]
    bound = {b.field_ref for b in row.role_bindings}
    assert bound & PERSON_NAMING_KEYS == set()
    assert "target_employer" not in bound, (
        "the employer a holder WORKS FOR and the one they APPLIED TO are never "
        "one key -- 00:44, and D30's own validation constraint")
    assert any("client" in exclusion for exclusion in row.exclusions)


def test_the_level_is_the_files_own_and_never_the_groups(shipped):
    """`GROUP_LEVEL_ROLES` names `holder_institution` on `academic` and nothing on
    `career`, so every level here is read once per FILE. One accepted group under
    one label can therefore still divide by year and by project, which is what the
    integration measurement rests on."""
    assert group_level_fields_for(shipped, SITUATION) == frozenset()


def test_the_domain_life_and_template_resolve(shipped):
    assert schema_for_situation(shipped, SITUATION) == "career"
    assert life_of(shipped, SITUATION) == "Career"
    assert template_id_for_situation(shipped, SITUATION) == DEFINITION


# --- amendment 31's second condition, over the whole menu ---------------------

def test_the_release_gains_exactly_one_situation_and_renames_nothing(shipped):
    """`00` amendment 31's second condition, checked against the release as it
    shipped before this change rather than against a retyped fixture.

    An ADDITION still has to prove it is one. `shipped_situations` is the
    cloud-bound menu, collected with `setdefault((schema, name), ...)`, so a row
    added on a signal another row already carried would leave the menu serving the
    older row's labels while `folder_levels_for` refused -- the person shown one
    answer while the product held another. The three files this change touches are
    all read at the before-SHA, because reading only one would compare a
    half-state against itself.
    """
    import subprocess

    def at_before(path):
        return subprocess.run(
            ["git", "show", f"{BEFORE_SHA}:src/tree_design/library/{path}"],
            capture_output=True, text=True, check=True).stdout

    before_files = {name: at_before(name)
                    for name in ("wave2_commerce.json", "definitions.json",
                                 "applicabilities.json")}

    def read_before(name):
        if name in before_files:
            return before_files[name]
        return read_packaged_library_file(name)

    before = {(row.schema, row.name): row
              for row in shipped_situations(load_shipped_catalogue(read_before))}
    after = {(row.schema, row.name): row for row in shipped_situations(shipped)}

    assert len(before) == 208
    assert len(after) == 209
    assert set(after) - set(before) == {("career", SITUATION)}, sorted(
        set(after) - set(before))
    assert set(before) - set(after) == set(), "a situation left the menu"

    changed = {key for key in before if before[key] != after[key]}
    assert changed == set(), (
        "a row that was already shipped changed shape; this ruling ADDS one and "
        f"renames nothing: {sorted(changed)}")

    # The two rows a shape-matching edit would have reached for, pinned by value.
    assert after[("career", RECRUITING)].folder_levels == RECRUITING_LABELS
    assert after[("career", TENURE)].folder_levels == TENURE_LABELS
    assert after[("career", SITUATION)].folder_levels == tuple(
        level[1] for level in EXPECTED_LEVELS)
