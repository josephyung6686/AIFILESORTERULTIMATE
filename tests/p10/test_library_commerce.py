"""The wave-2 commerce library: career, logistics and retail_hospitality.

`51-LAUNCH-TEMPLATE-DRAFT.md` section 4.8 named the hole this file closes for one
of these three schemas in so many words -- *"Career is in the launch wave and it
cannot produce a folder ... the product ships recognising resumes, offer letters
and recruiter threads, and has nowhere to put any of them."* The other two are
the same defect without the launch-wave urgency: `logistics` and
`retail_hospitality` are recognised by 23-schema `SCHEMA_IDS`, declare fields
under `60` section 5, and had no applicability row anywhere.

**What these tests are for.** Not that the JSON parses. They exist to pin the
things this data can silently lose, and every refusal below is mutated from a
REAL shipped record and raised by the real callee, so a test that only proved
good input loads cannot pass by accident.

1. **LOADED, not authored.** Every assertion runs against
   `src/tree_design/library/wave2_commerce.json` read from disk and driven
   through the real `tree_design.catalogue.load_catalogue`, merged with the
   shipped `fragments.json` and `definitions.json` -- the latter because career's
   three-of-three rows reference D30 `def.career-search-and-tenure@1`, which
   ships there and which this wave deliberately does not re-author.
2. **Every `field_ref` is a key its own schema declares**, checked against
   `facts.fields.DOMAIN_FIELDS` and never against a copy of `60` section 5. `60`
   section 9.6 is the reason: `active_field_allowlist` once walked DECLARATION
   scopes and five schemas reference keys they do not declare, so a hard-coded
   list is the exact defect that bug was.
3. **`60` section 8.3's ruling is data, not prose.** Career's default order is
   employer-first and the cycle-first order is present as the offered
   alternative; `test_career_defaults_to_employer_first_with_cycle_first_offered`
   is what fails if either half is quietly dropped.
4. **`60` B2's reversal survives contact with the templates.** No logistics
   recipe may produce `event > event`, and none may bind `consignment` and
   `record_type` to one role -- the fold `49` proposed and `60` reversed, which
   `00`:97's validator forbids by name.
5. **A label is not its key.** `59` section 5c measured the failure state on the
   neighbouring surface: 19 of 37 `display_name` slots byte-identical to the key
   and the other 18 the key with a space for the underscore. Wave 1 shipped 123
   bindings with zero identical; this wave holds that bar.
"""
from __future__ import annotations

import copy
import json
import pathlib

import pytest

import tree_design
from facts.fields import DOMAIN_FIELDS, FIELD_ROWS
from tree_design.catalogue import load_catalogue
from tree_design.templates import (
    CompositionConflict,
    MalformedTemplateRecord,
    merge_fragment_constraints,
)

#: Addressed through the package rather than through the working directory: this
#: is shipped data, and a test that only found it from the repository root would
#: pass on a tree where the file was never installed.
LIBRARY = pathlib.Path(tree_design.__file__).parent / "library"
COMMERCE_PATH = LIBRARY / "wave2_commerce.json"
FRAGMENTS_PATH = LIBRARY / "fragments.json"
DEFINITIONS_PATH = LIBRARY / "definitions.json"

REPO = pathlib.Path(__file__).resolve().parents[2]

#: `51`'s appendix writes the placeholder floor symbol `baseline` and assigns no
#: handling class; P7 injects the real vocabulary per deployment.
RANK = {"baseline": 0, "protected": 1}.__getitem__

SCHEMAS = ("career", "logistics", "retail_hospitality")

#: One row per bindable node row in the three schemas. The counts are the census
#: this wave owes: 6 career template rows, 7 logistics, 14 retail_hospitality,
#: minus the six refusals named in `REFUSED`.
EXPECTED_PER_SCHEMA = {"career": 3, "logistics": 6, "retail_hospitality": 12}

#: The refusals, each with the sentence from its own node row that earned it. A
#: refusal recorded only in a report is a refusal the next author re-litigates;
#: recorded here it turns red the moment somebody authors the row anyway without
#: the key that was missing.
REFUSED = {
    "career.consulting-client-engagement":
        "THE RECOMMENDATION: client first, then the engagement (a value of "
        "`project`), then document type",
    "career.credentials-licenses":
        "Recommended, once the career field rows exist: the ISSUING AUTHORITY "
        "first, then the CREDENTIAL, then the DOCUMENT TYPE",
    "career.portfolio-work-samples":
        "the piece of work first, then the artefact role (source file / export "
        "/ case study / cover)",
    "logistics.route-dispatch":
        "Held recommendation: WORKING DATE first, then route/run, then document "
        "function",
    "retail_hospitality.menu-recipe-costing":
        "What this row recommends in its place is a STANDING PRODUCT-LINE level "
        "- the menu, range or season the specification belongs to",
    "retail_hospitality.product-catalogue":
        "Its organising anchor is instead the RANGE OR SEASON, and beneath it "
        "the EFFECTIVE VERSION, and beneath that the FUNCTION",
}

#: The keys each refused row would have needed and its schema does not declare.
#: Kept beside `REFUSED` so the refusal is checkable rather than asserted.
REFUSED_MISSING_KEYS = {
    "career.consulting-client-engagement": ("client", "project"),
    "career.credentials-licenses": ("issuing_body",),
    "career.portfolio-work-samples": ("project", "artifact_type"),
    "logistics.route-dispatch": ("record_period",),
    "retail_hospitality.menu-recipe-costing": (),
    "retail_hospitality.product-catalogue": (),
}

CAREER_D30 = "def.career-search-and-tenure"
EMPLOYER_FIRST = "ord.employer-role-cycle-kind"
CYCLE_FIRST = "ord.cycle-kind-employer-role"


# --------------------------------------------------------------------------
# Fixtures -- the real loader, over the real files, merged as the product would.
# --------------------------------------------------------------------------

def _manifest(commerce: dict, *, fragments=None, definitions=None) -> str:
    """One release carrying this wave beside the two files it references.

    `definitions.json` is merged in and NOT stubbed, because career's rows point
    at D30 and a stub would let this file pass with the definition missing --
    which is the state `51` section 4.8 describes and this wave exists to end.
    """
    shipped_frags = json.loads(FRAGMENTS_PATH.read_text())["fragments"]
    shipped_defs = json.loads(DEFINITIONS_PATH.read_text())["definitions"]
    return json.dumps({
        "release_id": "rel-wave2-commerce",
        "fragments": shipped_frags if fragments is None else fragments,
        "definitions": (shipped_defs if definitions is None else definitions)
        + commerce["definitions"],
        "applicabilities": commerce["applicabilities"],
    })


@pytest.fixture(scope="module")
def raw() -> dict:
    return json.loads(COMMERCE_PATH.read_text())


@pytest.fixture(scope="module")
def catalogue(raw):
    return load_catalogue(lambda: _manifest(raw))


@pytest.fixture(scope="module")
def rows(catalogue):
    return tuple(
        row for row in catalogue.applicabilities.values()
        if row.uses_schema in SCHEMAS
    )


@pytest.fixture(scope="module")
def authored(raw, catalogue):
    """Only the definitions THIS file authors -- D30 and the wave-1 set are
    referenced, not owned, and asserting wave-1 invariants here would make this
    file fail for somebody else's edit."""
    ids = {d["template_id"] for d in raw["definitions"]}
    return tuple(d for d in catalogue.definitions.values()
                 if d.template_id in ids)


def _merged(catalogue, definition, row=None):
    """The REAL merge, run the way `routing.evaluate_composition` runs it."""
    fragments = [catalogue.fragment(ref) for ref in definition.fragment_refs]
    preferred = tuple(
        dimension.role_ref
        for dimension in sorted(definition.default_order.dimensions,
                                key=lambda d: d.order_index))
    return merge_fragment_constraints(
        fragments, privacy_rank=RANK, preferred_order=preferred,
        definition=definition,
        applicability_floors=(
            (row.privacy_floor,) if row is not None and row.privacy_floor else ()))


# --------------------------------------------------------------------------
# The rows load, and they are the census this wave owes.
# --------------------------------------------------------------------------

def test_the_wave_loads_through_the_real_loader(rows):
    """Every record has passed `TemplateApplicability.__post_init__`, which is
    what rejects a row binding outside its own allow-list and a row with no
    provenance. A JSON file that merely parses proves neither."""
    assert len(rows) == sum(EXPECTED_PER_SCHEMA.values()) == 21


def test_each_schema_carries_the_rows_its_node_census_supports(rows):
    counts = {schema: 0 for schema in SCHEMAS}
    for row in rows:
        counts[row.uses_schema] += 1
    assert counts == EXPECTED_PER_SCHEMA


def test_the_top_level_shape_is_the_one_the_loader_reads(raw):
    """`load_catalogue` reads `manifest["definitions"]` and
    `manifest["applicabilities"]`, so this file's own top-level keys are the
    seam. A file nesting them anywhere else compiles into an empty release, and
    an empty release makes C1 pass by having nothing to resolve."""
    assert list(raw) == ["definitions", "applicabilities"]
    assert raw["definitions"] and raw["applicabilities"]


def test_a_row_and_a_definition_are_each_identified_once(raw, catalogue):
    row_keys = [(r["applicability_id"], r["applicability_version"])
                for r in raw["applicabilities"]]
    assert len(set(row_keys)) == len(row_keys)
    def_keys = [(d["template_id"], d["template_version"])
                for d in raw["definitions"]]
    assert len(set(def_keys)) == len(def_keys)
    # And no id collides with something already shipped, which would silently
    # replace a wave-1 recipe when the two files are compiled into one release.
    shipped = {d["template_id"]
               for d in json.loads(DEFINITIONS_PATH.read_text())["definitions"]}
    assert not ({d["template_id"] for d in raw["definitions"]} & shipped)


# --------------------------------------------------------------------------
# Career: D30 ships, and this wave is the rows it had none of.
# --------------------------------------------------------------------------

def test_career_rows_bind_the_shipped_d30_and_this_wave_re_authors_none(
        raw, rows, catalogue):
    """`60` section 8.2: *"D30 ships, because J-3 giving career six fields is
    meaningless if career cannot produce a folder."* It ships in
    `definitions.json`; what career lacked was applicability rows, and `51`
    section 5 has no `uses_schema: career` section at all."""
    career = [row for row in rows if row.uses_schema == "career"]
    assert {row.template_id for row in career} == {
        CAREER_D30, "def.requisition-record"}
    on_d30 = [row for row in career if row.template_id == CAREER_D30]
    assert {row.applicability_id for row in on_d30} == {
        "ap.career.recruiting", "ap.career.employment-records"}
    for row in on_d30:
        assert (row.template_id, row.template_version) in catalogue.definitions
    # D30 is REFERENCED, never re-authored here.
    assert CAREER_D30 not in {d["template_id"] for d in raw["definitions"]}


def test_career_defaults_to_employer_first_with_cycle_first_offered(catalogue):
    """`60` section 8.3, the ruling the whole career question turned on. The
    default is not the better order, it is the one that FAILS better:
    employer-first on a job-seeker yields many small folders, which `00`'s canvas
    already warns about and offers to flatten; cycle-first on someone with ten
    years at two employers asserts a recruiting cycle that does not exist, and
    there is no warning for that and nothing to flatten."""
    d30 = catalogue.definitions[(CAREER_D30, 1)]
    assert d30.default_order.order_id == EMPLOYER_FIRST
    offered = {order.order_id for order in d30.candidate_orders}
    assert CYCLE_FIRST in offered
    assert len(offered) == 2, "J-WIDE-2 offers both and this wave adds none"
    employer_first = [dimension.role_ref for dimension in
                      sorted(d30.default_order.dimensions,
                             key=lambda d: d.order_index)]
    assert employer_first[0] == "employer_org"
    cycle = next(o for o in d30.candidate_orders if o.order_id == CYCLE_FIRST)
    assert sorted(cycle.dimensions, key=lambda d: d.order_index)[0].role_ref == \
        "cycle_period"
    # The merge is what actually orders a composition, so the recommendation has
    # to survive it rather than only sit in the record.
    assert _merged(catalogue, d30).ordered_roles[0] == "employer_org"


def test_career_files_both_halves_of_its_own_corpus(rows):
    """`60` J-3 splits career in half and section 8.3 names which key each half
    files by: *"the search (resumes, cover letters, portfolio) -- work_type"* and
    *"the tenure (contracts, payslips, reviews) -- record_type"*. A wave that
    shipped one half would leave the other exactly where `51` section 4.8 found
    it, so this is the assertion that says both arrived."""
    by_id = {row.applicability_id: row for row in rows}
    search = by_id["ap.career.recruiting"]
    tenure = by_id["ap.career.employment-records"]

    def field(row, role):
        return next(b.field_ref for b in row.role_bindings if b.role_ref == role)

    assert field(search, "artifact_kind") == "work_type"
    assert field(tenure, "artifact_kind") == "record_type"
    # And the two halves address two different organizations, which is `00`:44's
    # rule and D30's own validation constraint: the employer the holder WORKS FOR
    # and the employer the holder APPLIED TO are never one key.
    assert field(search, "employer_org") == "target_employer"
    assert field(tenure, "employer_org") == "employer"
    # The tenure half opens no recruiting-cycle level: "a job held has no
    # recruiting cycle -- the tenure is bounded by an agreement and a
    # separation, not by an application season".
    assert "cycle_period" not in {b.role_ref for b in tenure.role_bindings}
    assert any("recruiting_cycle" in x for x in tenure.exclusions)


def test_employer_side_hiring_opens_no_employer_and_no_candidate_level(rows):
    """`career.employer-side-hiring` is the one career row `00`'s recorded order
    does not fit: *"every file in an employer-side hiring corpus names the SAME
    employer, so a company level proposes exactly the branch 00 tells the
    interface to warn about."* It gets its own recipe, and the level it must
    never open is a person."""
    row = next(r for r in rows
               if r.applicability_id == "ap.career.employer-side-hiring")
    fields = {b.field_ref for b in row.role_bindings}
    assert fields == {"job_title", "recruiting_cycle", "record_type"}
    assert "employer" not in fields and "target_employer" not in fields
    assert any("candidate" in x for x in row.exclusions)


# --------------------------------------------------------------------------
# Logistics: `60` B2's reversal, held by the templates rather than only by the key.
# --------------------------------------------------------------------------

def test_no_logistics_recipe_can_produce_event_over_event(rows, catalogue):
    """`60` B2 reverses `49`'s fold of `consignment` into `event` because
    `logistics.last-mile-pod`'s own recorded order is *"consignment/parcel ->
    delivery event"* and folded that reads `event > event`, *"which `00`:97's
    validator forbids by name"*. `60` section 7 then drops `event` from
    `logistics` outright: *"event is the Photos capture-occasion."*

    Two ways the defect could come back and both are closed here: a row binding
    `event` on logistics at all, and one recipe carrying two levels that resolve
    to the same field.
    """
    assert "event" not in DOMAIN_FIELDS["logistics"]
    for row in rows:
        if row.uses_schema != "logistics":
            continue
        assert "event" not in row.allowed_fields, row.applicability_id
        assert "event" not in {b.field_ref for b in row.role_bindings}
        fields = [b.field_ref for b in row.role_bindings]
        assert len(fields) == len(set(fields)), (
            row.applicability_id,
            "two levels resolving to one field is the same defect the fold was")


def test_no_logistics_row_binds_the_consignment_and_the_record_to_one_role(rows):
    """The other half of B2. `consignment` is a THING -- *"one described quantity
    of goods travelling under one carrier's undertaking"* -- and `record_type` is
    what the document IS. A recipe that put them on one role would have folded
    them back by hand after the ruling unfolded them."""
    for row in rows:
        if row.uses_schema != "logistics":
            continue
        by_role = {}
        for binding in row.role_bindings:
            by_role.setdefault(binding.role_ref, set()).add(binding.field_ref)
        for role, fields in by_role.items():
            assert len(fields) == 1, (row.applicability_id, role, fields)
            assert fields != {"consignment", "record_type"}
        if "consignment" in row.allowed_fields:
            subject = next(b.role_ref for b in row.role_bindings
                           if b.field_ref == "consignment")
            kind = next(b.role_ref for b in row.role_bindings
                        if b.field_ref == "record_type")
            assert subject != kind


def test_the_carrier_level_is_optional_and_the_two_rows_that_refuse_it_say_so(
        rows, catalogue):
    """`60` B3 folds `carrier` into `supplier` with a condition: the notes must
    carry the labelled-slot rule, because *"a consignment note routinely names
    consignor, consignee and carrier in three different roles on one page"*.
    `logistics.customs-export` refuses the level outright -- *"a carrier name
    must not collect unrelated customs cases"* -- and this asserts the refusal is
    recorded on the row rather than inferable from an absence."""
    custody = catalogue.definitions[("def.custody-subject-record", 1)]
    carrier = next(d for d in custody.default_order.dimensions
                   if d.role_ref == "counterparty_org")
    assert carrier.requirement == "optional"
    assert carrier.order_index == 0
    for applicability_id in ("ap.logistics.customs-export",
                             "ap.logistics.last-mile-pod"):
        row = next(r for r in rows if r.applicability_id == applicability_id)
        assert "supplier" not in row.allowed_fields
        assert any("carrier" in x for x in row.exclusions), applicability_id


# --------------------------------------------------------------------------
# Retail and hospitality: the key that is declared and is never a level.
# --------------------------------------------------------------------------

def test_product_is_declared_and_never_becomes_a_folder_level(rows):
    """`60` section 5 declares `product` on `retail_hospitality`, and the
    schema's own anchor forbids it as a dimension in the same breath as a guest
    name: *"A product or a guest name must NEVER become a dimension: the first
    produces a branch per SKU, the second publishes a member of the public's name
    into the directory tree."* A declared key is not an invitation to level on
    it, and four of the fourteen rows say so individually."""
    assert "product" in DOMAIN_FIELDS["retail_hospitality"]
    for row in rows:
        assert "product" not in row.allowed_fields, row.applicability_id
        assert "product" not in {b.field_ref for b in row.role_bindings}


def test_no_retail_recipe_puts_a_period_above_the_occasion_or_the_site(catalogue):
    """`retail_hospitality.json`: *"Trading period sits INSIDE the occasion
    level, never above the site."* All fourteen rows refuse time-first in the
    same words, and `event`'s own note settles why they may: *"Time-primacy
    belongs to `00`:70's Photos template order, not to the key, so a non-photo
    schema does not inherit it."*"""
    occasion = catalogue.definitions[("def.trading-occasion-record", 1)]
    order = [d.role_ref for d in sorted(occasion.default_order.dimensions,
                                        key=lambda d: d.order_index)]
    assert order == ["operating_site", "occasion_anchor", "artifact_kind"]
    period = catalogue.definitions[("def.trading-period-record", 1)]
    period_order = [d.role_ref for d in sorted(period.default_order.dimensions,
                                               key=lambda d: d.order_index)]
    assert period_order.index("operating_site") < period_order.index("scope_period")
    # And the merge agrees, which is what a composition actually uses.
    assert _merged(catalogue, occasion).ordered_roles == tuple(order)
    assert _merged(catalogue, period).ordered_roles == tuple(period_order)


# --------------------------------------------------------------------------
# Fields: live keys of the row's own schema, checked against the live catalogue.
# --------------------------------------------------------------------------

def test_every_bound_field_is_one_its_own_schema_declares(rows):
    """Checked against `facts.fields.DOMAIN_FIELDS` and never against a copy of
    `60` section 5. `60` section 9.6 is the reason: `active_field_allowlist` once
    walked DECLARATION scopes while five schemas REFERENCE keys they do not
    declare, and a hard-coded list here would be that same bug transplanted."""
    destination_eligible = {row.field_key for row in FIELD_ROWS
                            if row.destination_eligible}
    for row in rows:
        referenced = DOMAIN_FIELDS[row.uses_schema]
        for field in row.allowed_fields:
            assert field in referenced, (row.applicability_id, field)
            assert field in destination_eligible, (row.applicability_id, field)


def test_a_row_allows_exactly_what_it_binds(rows):
    """`allowed_vocabulary_for` unions `allowed_fields` across a schema's rows
    and hands the result to P8 as `Dossier.allowed_vocabulary`, so a field
    allowed here and bound nowhere widens five call sites for every row of the
    schema."""
    for row in rows:
        assert set(row.allowed_fields) == {b.field_ref for b in row.role_bindings}
        assert len(row.allowed_fields) == len(set(row.allowed_fields))


def test_a_role_binds_one_field_per_schema_except_where_a_ruling_splits_it(rows):
    """C4 refuses to pick when one role resolves two ways in one branch, and that
    is correct rather than avoidable for career: `60` J-3 splits the schema in
    half and section 8.3 names the two keys. The split is asserted rather than
    tolerated, so a third divergence would fail."""
    seen = {}
    for row in rows:
        for binding in row.role_bindings:
            seen.setdefault((binding.role_ref, row.uses_schema), set()).add(
                binding.field_ref)
    split = {key: fields for key, fields in seen.items() if len(fields) > 1}
    assert split == {
        ("employer_org", "career"): {"employer", "target_employer"},
        ("artifact_kind", "career"): {"record_type", "work_type"},
    }
    assert seen[("custody_subject", "logistics")] == {"consignment"}
    assert seen[("occasion_anchor", "retail_hospitality")] == {"event"}
    assert seen[("operating_site", "logistics")] == {"site"}
    assert seen[("operating_site", "retail_hospitality")] == {"site"}


# --------------------------------------------------------------------------
# The labels. This is the deliverable.
# --------------------------------------------------------------------------

def _normalise(value: str) -> str:
    """Fold the two ways a key gets shipped as a label: the key itself, and the
    key with its underscores opened out. `59` section 5c measured that those two
    account for 37 of 37 `display_name` values in `facts/fields.py`."""
    return value.strip().casefold().replace("_", " ")


def test_no_label_is_the_field_key_it_replaces(rows):
    identical = [(row.applicability_id, b.field_ref, b.label)
                 for row in rows for b in row.role_bindings
                 if b.label == b.field_ref]
    assert identical == []
    despaced = [(row.applicability_id, b.field_ref, b.label)
                for row in rows for b in row.role_bindings
                if _normalise(b.label) == _normalise(b.field_ref)]
    assert despaced == []


def test_no_label_is_the_role_name_either(rows):
    """`53` section 4b failed eleven of fifteen roles on the name-out-loud test
    -- *"Nobody says 'occasion anchor.'"* A role is a cross-schema abstraction and
    must never reach a person."""
    leaked = [(row.applicability_id, b.role_ref, b.label)
              for row in rows for b in row.role_bindings
              if _normalise(b.label) == _normalise(b.role_ref)]
    assert leaked == []


def test_every_binding_carries_a_label_and_the_reuse_is_named_per_audience(rows):
    """The whole argument for where the label lives. `def.trading-occasion-record`
    is one recipe reaching six retail situations, and a booking, a till session,
    a stock count, a trading day, a return case and a supplier order are not one
    word to the person who reads them -- `00` section 5.1 asks labels to *"reflect
    the user's vocabulary rather than a universal corporate taxonomy."*"""
    bindings = [b for row in rows for b in row.role_bindings]
    assert all(b.label.strip() for b in bindings)
    occasion = {row.applicability_id: b.label
                for row in rows for b in row.role_bindings
                if row.template_id == "def.trading-occasion-record"
                and b.role_ref == "occasion_anchor"}
    assert len(occasion) == 8
    assert len(set(occasion.values())) == 8, occasion
    # And the same for the leaf, which is one field key across all three schemas.
    kinds = {b.label for row in rows for b in row.role_bindings
             if b.field_ref == "record_type"}
    assert len(kinds) >= 15, sorted(kinds)


def test_the_labels_are_not_one_name_per_field(rows):
    """The regression this file guards against is a library that authors one
    label per field key and calls the job done -- which is `facts/fields.py`'s
    `display_name` with better words, and still one name for every audience."""
    per_field = {}
    for row in rows:
        for binding in row.role_bindings:
            per_field.setdefault(binding.field_ref, set()).add(binding.label)
    assert len(per_field["record_type"]) >= 15
    assert len(per_field["site"]) >= 7
    assert len(per_field["event"]) >= 8
    assert sum(len(v) for v in per_field.values()) > 3 * len(per_field)


# --------------------------------------------------------------------------
# The definitions this wave authors.
# --------------------------------------------------------------------------

def test_a_fragmentless_definition_states_its_own_floor_and_its_own_order(
        authored, catalogue):
    """`TemplateDefinition.__post_init__` refuses a definition that composes no
    fragment and states no floor, because C7 keeps the STRONGEST floor among the
    included fragments and with none there is nothing to keep. The second half is
    the shipped bug this repeats the fix for: a definition-local role that no
    `relative_order` places *"was absent from the merged order and `routing`
    sorted them LAST ... a definition asking for venue first got venue last."*"""
    for definition in authored:
        roles = {d.role_ref for order in definition.candidate_orders
                 for d in order.dimensions}
        if not definition.fragment_refs:
            assert definition.privacy_floor, definition.template_id
            ordered = _merged(catalogue, definition).ordered_roles
            assert set(ordered) == roles, definition.template_id
            assert len(ordered) == len(roles)
        merged = _merged(catalogue, definition)
        assert merged.privacy_floor in ("baseline", "protected")


def test_the_two_order_floor_is_exited_only_by_an_argued_attestation(authored):
    """`TemplateDefinition` allows one candidate order for a multi-role recipe
    only where `sole_order_attestation` records that the corpora attest exactly
    one nesting, and the reason the exit is prose rather than a flag is that *"an
    invented alternative is worse than an absent one, because the user cannot
    tell it is invented."* Every attestation here must therefore quote the row it
    rests on, which is what a bare boolean could not be asked for."""
    for definition in authored:
        roles = {d.role_ref for order in definition.candidate_orders
                 for d in order.dimensions}
        if len(roles) <= 1:
            assert definition.sole_order_attestation is None, definition.template_id
            continue
        assert len(definition.candidate_orders) == 1
        attestation = definition.sole_order_attestation or ""
        assert len(attestation) > 200, definition.template_id
        assert "'" in attestation, (
            definition.template_id,
            "an attestation quotes the corpus it rests on")


def test_every_definition_names_exactly_one_default_and_a_reason_per_order(
        authored):
    for definition in authored:
        defaults = [o for o in definition.candidate_orders if o.is_default]
        assert len(defaults) == 1, definition.template_id
        for order in definition.candidate_orders:
            assert order.rationale.strip()
            for dimension in order.dimensions:
                assert dimension.retrieval_rationale.strip()


def test_every_definition_states_a_sensitivity_policy_and_its_prohibitions(
        authored):
    """Wave 1's seven policy refs are the closed set this wave draws from; a
    novel one here would be a policy nobody wrote. And every recipe in these
    three schemas carries at least one constraint naming a level it will not
    build, because `00`:97 forbids *"an author or organization merely as a
    collector"* and all three worlds are full of tempting collectors -- a
    carrier, a guest, a driver, a candidate."""
    known = {
        "sp.holder-own-record@1", "sp.third-party-confidential@1",
        "sp.safety-domain-protected@1", "sp.household-member-record@1",
        "sp.not-holder-personal@1", "sp.credential-bearing@1",
        "sp.document-reproduced-whole@1",
    }
    for definition in authored:
        assert definition.sensitivity_policy_ref in known, definition.template_id
        assert definition.validation_constraints, definition.template_id
        assert any("never" in c.lower() or "no level" in c.lower()
                   or "must not" in c.lower() or "no " in c.lower()
                   for c in definition.validation_constraints)


# --------------------------------------------------------------------------
# Provenance and detection: a trace, not a placeholder string.
# --------------------------------------------------------------------------

def test_every_row_traces_back_to_the_node_row_that_justified_it(rows):
    """The record only requires provenance to be non-empty; this requires it to
    RESOLVE. *"A compiled row nobody can trace back to the domain research that
    justified it cannot be reviewed or retired."*"""
    for row in rows:
        cites = {c.split(":", 1)[0]: c.split(":", 1)[1]
                 for c in row.provenance if ":" in c}
        node_id = cites["row"]
        assert node_id.split(".")[0] == row.uses_schema, row.applicability_id
        assert (REPO / "planning/domains/nodes" / f"{node_id}.json").is_file()
        assert (REPO / cites["memo"]).is_file()
        assert any("60-VOCABULARY-RULINGS.md" in c for c in row.provenance)
    assert len({row.provenance[0] for row in rows}) == len(rows)


def test_detection_signals_are_references_to_a_live_node_and_never_patterns(rows):
    """`51` section 9.5: *"R2 owns the regexes and gazetteers. No pattern is
    written here."* And the node must be one the product may actually recognise:
    a `refuse_node: true` row has no recognition to point at."""
    for row in rows:
        assert len(row.detection_signal_refs) == 1
        ref = row.detection_signal_refs[0]
        assert ref.startswith("recognition:")
        node_id = ref.removeprefix("recognition:")
        node = json.loads(
            (REPO / "planning/domains/nodes" / f"{node_id}.json").read_text())
        assert node["recognition"]["deterministic"]
        assert node["refuse_node"] is False


def test_every_detection_signal_names_a_compiled_recognition_row(rows):
    """A recipe pointed at a recognition that never compiled is a recipe nothing
    can reach, which is `51` section 4.8's defect with the halves swapped."""
    manifest = json.loads(
        (pathlib.Path(tree_design.__file__).parents[1]
         / "recognition" / "library" / "recognition.json").read_text())
    compiled = {row for schema in manifest["schemas"].values()
                for row in schema["rows"]}
    for row in rows:
        for signal in row.detection_signal_refs:
            assert signal.removeprefix("recognition:") in compiled, (
                row.applicability_id, signal)


def test_every_recognisable_row_in_these_schemas_is_filed_or_named_as_refused(
        rows):
    """The census that closes the gap, stated as the gap itself.

    `51` section 4.8's charge is that the product *"ships recognising resumes,
    offer letters and recruiter threads, and has nowhere to put any of them."*
    The check is therefore not how many rows this wave authored but whether any
    compiled recognition in these three schemas still has nowhere to go: every
    one is either bound to a recipe here or named in `REFUSED` with the sentence
    from its own node row that earned the refusal. A row in neither set is a
    silent hole, which is the exact state this wave exists to end.
    """
    manifest = json.loads(
        (pathlib.Path(tree_design.__file__).parents[1]
         / "recognition" / "library" / "recognition.json").read_text())
    filed = {c.removeprefix("recognition:")
             for row in rows for c in row.detection_signal_refs}
    for schema in SCHEMAS:
        compiled = set(manifest["schemas"][schema]["rows"])
        # The schema's own anchor row is recognition, not a filing situation;
        # the launch library authors no anchor rows either.
        templates = {row for row in compiled if row != schema}
        unaccounted = templates - filed - set(REFUSED)
        assert unaccounted == set(), (schema, sorted(unaccounted))
    assert set(REFUSED) & filed == set()
    assert len(REFUSED) == 6


def test_the_refused_rows_are_refused_because_a_key_is_missing_not_by_taste(
        rows):
    """44 of the 358 researched rows earned a refusal, and *"an honest gap beats
    an invented recipe."* Each refusal here is a row whose own recommendation
    names a level its schema declares no key for -- checked against the live
    catalogue, so a later ruling that declares the key turns this red and asks
    for the row rather than leaving the gap unexamined."""
    authored_nodes = {c.removeprefix("recognition:")
                      for row in rows for c in row.detection_signal_refs}
    for node_id, missing in REFUSED_MISSING_KEYS.items():
        assert node_id not in authored_nodes, node_id
        assert (REPO / "planning/domains/nodes" / f"{node_id}.json").is_file()
        schema = node_id.split(".")[0]
        for key in missing:
            assert key not in DOMAIN_FIELDS[schema], (node_id, key)
        assert REFUSED[node_id].strip()


# --------------------------------------------------------------------------
# The discriminating half: malformed records are REJECTED, on this file's data.
# --------------------------------------------------------------------------

def test_a_cyclic_relative_order_is_refused_by_the_real_merge(raw, catalogue):
    """A definition's `relative_order` *"cannot reorder what a fragment
    constrains. A pair contradicting a fragment edge makes the combined graph
    cyclic and C5 refuses it."* Here the contradiction is the definition's own,
    which C5 must refuse identically -- a recipe that could quietly win over
    itself is a recipe with two nestings and no way to say which."""
    mutated = copy.deepcopy(raw)
    definition = next(d for d in mutated["definitions"]
                      if d["template_id"] == "def.custody-subject-record")
    definition["relative_order"].append(["artifact_kind", "custody_subject"])
    catalogue2 = load_catalogue(lambda: _manifest(mutated))
    record = catalogue2.definitions[("def.custody-subject-record", 1)]
    with pytest.raises(CompositionConflict, match="cycle"):
        _merged(catalogue2, record)


def test_relative_order_carries_the_nesting_without_the_recommendation(
        raw, catalogue):
    """`relative_order` is load-bearing on its own and is not a restatement of
    the candidate order.

    `routing` supplies `preferred_order` from `_recommended_order`, which returns
    NOTHING as soon as the recipes in a branch disagree. Everything these
    fragmentless recipes know about their own nesting then has to come from
    `relative_order` -- and this is the shipped bug that says why: a role no
    ordering placed *"was absent from the merged order and `routing` sorted them
    LAST, silently and with ties ... a definition asking for venue first got
    venue last."* Run with the recommendation withheld, the record still orders
    all three levels; strip `relative_order` and the roles are named and refused
    rather than falling back to a sequence nobody authored.
    """
    record = catalogue.definitions[("def.trading-occasion-record", 1)]
    without_recommendation = merge_fragment_constraints(
        [], privacy_rank=RANK, preferred_order=(), definition=record)
    assert without_recommendation.ordered_roles == (
        "operating_site", "occasion_anchor", "artifact_kind")

    mutated = copy.deepcopy(raw)
    definition = next(d for d in mutated["definitions"]
                      if d["template_id"] == "def.trading-occasion-record")
    definition["relative_order"] = []
    catalogue2 = load_catalogue(lambda: _manifest(mutated))
    stripped = catalogue2.definitions[("def.trading-occasion-record", 1)]
    with pytest.raises(CompositionConflict, match="unordered"):
        merge_fragment_constraints(
            [], privacy_rank=RANK, preferred_order=(), definition=stripped)


def test_a_fragmentless_definition_with_no_floor_is_refused_at_load(raw):
    """C7 keeps the strongest floor among the included fragments, so a definition
    with neither leaves nothing to keep. Refused at the RECORD, because *"a record
    that accepts what the composer refuses moves the failure far away from its
    cause."*"""
    mutated = copy.deepcopy(raw)
    definition = next(d for d in mutated["definitions"]
                      if d["template_id"] == "def.site-kept-record")
    definition["privacy_floor"] = None
    with pytest.raises(MalformedTemplateRecord, match="privacy floor"):
        load_catalogue(lambda: _manifest(mutated))


def test_a_sole_order_attestation_beside_two_orders_is_refused(raw):
    """The attestation is the exit from the two-order floor, and it means
    something only where there is one order: *"One of the two statements is false
    and the record cannot tell which."*"""
    mutated = copy.deepcopy(raw)
    definition = next(d for d in mutated["definitions"]
                      if d["template_id"] == "def.trading-period-record")
    second = copy.deepcopy(definition["candidate_orders"][0])
    second["order_id"] = "ord.invented-alternative"
    second["is_default"] = False
    definition["candidate_orders"].append(second)
    with pytest.raises(MalformedTemplateRecord, match="attests"):
        load_catalogue(lambda: _manifest(mutated))


def test_dropping_the_attestation_from_a_single_order_recipe_is_refused(raw):
    """The floor itself, from the other side. Without the attestation a
    multi-dimension recipe offering one order is *"a single `dimensions` tuple
    wearing a new field name."*"""
    mutated = copy.deepcopy(raw)
    definition = next(d for d in mutated["definitions"]
                      if d["template_id"] == "def.requisition-record")
    definition["sole_order_attestation"] = None
    with pytest.raises(MalformedTemplateRecord, match="at least two"):
        load_catalogue(lambda: _manifest(mutated))


def test_a_label_holding_a_path_separator_is_refused_at_load(raw):
    """P12 alone composes paths (resolution B3), asserted on a mutated copy of a
    REAL row rather than a fixture, so it is this file's data that is refused."""
    for separator in ("/", "\\"):
        mutated = copy.deepcopy(raw)
        mutated["applicabilities"][0]["role_bindings"][0]["label"] = \
            f"Stripe{separator}Offer"
        with pytest.raises(MalformedTemplateRecord, match="path separator"):
            load_catalogue(lambda: _manifest(mutated))


def test_a_binding_outside_the_rows_own_allow_list_is_refused(raw):
    """The guard that keeps reuse from turning a per-schema fact allow-list into
    a cross-domain union: `retail_hospitality` may not reach `supplier` by
    binding it while allowing something else."""
    mutated = copy.deepcopy(raw)
    row = next(r for r in mutated["applicabilities"]
               if r["applicability_id"] == "ap.retail_hospitality.supplier-order")
    row["role_bindings"][0]["field_ref"] = "supplier"
    with pytest.raises(MalformedTemplateRecord, match="does not"):
        load_catalogue(lambda: _manifest(mutated))


def test_a_row_with_no_provenance_is_refused(raw):
    """*"A row with none cannot be reviewed or retired."*"""
    mutated = copy.deepcopy(raw)
    mutated["applicabilities"][0]["provenance"] = []
    with pytest.raises(MalformedTemplateRecord, match="provenance"):
        load_catalogue(lambda: _manifest(mutated))


def test_a_record_missing_a_required_key_does_not_load(raw):
    """The loader reads by key and does not default. A missing `role_bindings`
    is a row that binds nothing, and a release that accepted it would resolve to
    a recipe with no levels rather than refusing."""
    mutated = copy.deepcopy(raw)
    del mutated["applicabilities"][0]["role_bindings"]
    with pytest.raises(KeyError):
        load_catalogue(lambda: _manifest(mutated))
    mutated = copy.deepcopy(raw)
    del mutated["definitions"][0]["candidate_orders"]
    with pytest.raises(KeyError):
        load_catalogue(lambda: _manifest(mutated))


def test_a_release_with_no_id_is_refused(raw):
    """*"A compiled catalogue carries a release identity; without one, two
    different libraries are indistinguishable in a frozen tree."*"""
    from tree_design.config import ConfigurationRequired
    manifest = json.loads(_manifest(raw))
    del manifest["release_id"]
    with pytest.raises(ConfigurationRequired):
        load_catalogue(lambda: json.dumps(manifest))
