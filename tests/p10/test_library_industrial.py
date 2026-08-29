"""The wave-2 industrial catalogue: engineering, manufacturing, construction_property,
resource_operations.

`51-LAUNCH-TEMPLATE-DRAFT.md` section 4.8 named the hole for one schema — the product
"ships recognising resumes, offer letters and recruiter threads, and has nowhere to put
any of them". The same sentence was true of seventeen schemas. These four are the
industrial quarter of it: recognition covers all 23 schemas, `60-VOCABULARY-RULINGS.md`
section 5 declares fields for 20, and until this file existed an engineer, a plant
manager, a builder and a well operator were all recognised and unfileable.

**These rows were buildable the whole time and nobody built them.** Every node row in
these four schemas carries `template.dimension_order: []`, which reads like a refusal and
is not one: `PR-6` says a dimension may only branch on a field its schema DECLARES, and
these schemas declared none. `60` section 5 now declares them. The recommendation was
never lost — it sits in prose in each row's `template.why`. This wave is that prose turned
into `dimension_order`s, and nothing else. Where the prose leads with a level `60` did not
mint, the row is REFUSED rather than approximated; the eight refusals are pinned below
with the sentence that earned each one.

**What these tests are for.** Not that the JSON parses. They exist to pin the four things
this data can silently lose:

1. **LOADED, not authored.** Every assertion below runs against records that came back
   from the real `tree_design.catalogue.load_catalogue`, merged with the shipped fragment
   library and a release id, through the real `__post_init__`. A record the live product
   would reject cannot pass here.
2. **A label that is its own key is the failure state.** `59` section 5c measured the
   neighbouring surface: of 37 `display_name` slots, 19 are byte-identical to the key and
   the other 18 are the key with the underscore replaced by a space. Wave 1 shipped 123
   bindings with zero identical. `test_no_label_is_the_key_it_replaces` keeps that at zero
   here, checked case- and underscore-insensitively because "Site" for `site` is the same
   failure wearing a capital.
3. **`design_item` is not `product`.** `60` section 3 M10: *"design_item is the controlled
   design configuration whose definition a file governs — never a saleable or sold
   article, which is product."* `engineering`'s own elimination checked `project`,
   `subject`, `property` and `repository` and never checked `product`. The line is drawn
   here and `test_no_role_binds_both_design_item_and_product` keeps it drawn.
4. **`asset` is a type-versus-instance trap.** `manufacturing.asset-register`: *"A
   multi-asset register export has no single asset value and must sit at the site level as
   that site's population document; forcing it under an asset level would require
   inventing an asset fact the file does not carry."*

Each discriminating test has a negative twin that builds the malformed record and asserts
the loader refuses it, because a test that only ever sees good data proves the data is
good and not that the check works.
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter, defaultdict

import pytest

import tree_design
from facts.fields import DOMAIN_FIELDS, FIELD_ROWS
from tree_design.catalogue import load_catalogue
from tree_design.templates import (
    CompositionConflict,
    MalformedTemplateRecord,
    merge_fragment_constraints,
)

#: Addressed through the package rather than through the working directory: this is
#: shipped data, and a test that only found it from the repository root would pass on a
#: tree where the file was never installed.
LIBRARY = pathlib.Path(tree_design.__file__).parent / "library"
WAVE2 = LIBRARY / "wave2_industrial.json"
FRAGMENTS = LIBRARY / "fragments.json"

REPO = pathlib.Path(__file__).resolve().parents[2]
NODES = REPO / "planning" / "domains" / "nodes"

SCHEMAS = ("engineering", "manufacturing", "construction_property", "resource_operations")

#: What this wave authored, per schema. A number rather than a shrug: a row quietly
#: dropped or a definition quietly collapsed is visible here before it is visible as a
#: reference error much later in the composition path.
EXPECTED_PER_SCHEMA = {
    "engineering": 15,
    "manufacturing": 15,
    "construction_property": 22,
    "resource_operations": 8,
}

#: The eight kept node rows this wave DELIBERATELY did not author, each with the sentence
#: from its own prose that earned the refusal. `44` of the `358` research rows earned a
#: refusal at their own stage; these eight earn one here, for one reason in every case —
#: the level the row LEADS with has no key, and approximating it would ship a recipe the
#: row never recommended. An honest gap beats an invented recipe.
REFUSED = {
    "engineering.aerospace-airworthiness":
        "its order leads with an approval instrument - 'for type-design and approval data, "
        "approval_instrument then engineering_artifact_type' - and 60 section 4 minted no "
        "approval key; its second branch needs a per-article key which NJ-AERO-2 leaves as "
        "'three answers with three different products'",
    "engineering.invention-disclosure":
        "'the researched order is invention_family -> prosecution status -> artifact role, "
        "which differs in kind from the schema default' - no key carries an invention family "
        "and NJ-IDF-1 asks whether project should be widened to cover it",
    "engineering.prototype-build":
        "the row states its own condition: without build_event 'this row's recommended order "
        "collapses to design_item alone, becomes indistinguishable from engineering."
        "cad-model's order, and the second leg of its node test fails - a genuine path to a "
        "later refusal, stated rather than hidden'",
    "engineering.standards-library":
        "NJ-SL-4: 'this row can fill none of the engineering schema's four proposed levels, "
        "and both keys it needs are its own proposals. Either R1c ratifies issuing_body and "
        "standard_designation, or the honest conclusion is that a reference library is not an "
        "engineering-schema situation at all'",
    "manufacturing.environmental-compliance":
        "'the recommendation held as prose is authorisation, then emission point, then "
        "reporting period, then record type - with site above authorisation only in a "
        "genuinely multi-site corpus'. 60 section 5 declares authorization on "
        "resource_operations and NOT on manufacturing, and manufacturing is the one schema at "
        "00 line 48's six-candidate ceiling with no room to add it",
    "manufacturing.field-service-report":
        "'The natural top level is the canonical client key ... which the manufacturing schema "
        "does not currently carry', and the asset level cannot stand alone in its place "
        "because 'one customer's unit serials are only unique within that customer'",
    "manufacturing.spare-parts":
        "'Record type is the leaf and never sits above part' - no key carries a stocked part, "
        "and folding it into product would break 60 section 3 M10 from the other side, since "
        "a bearing held in a storeroom is not a saleable article this holder sells",
    "manufacturing.supplier-qualification":
        "'The parent dimension is the supplier because a parent dimension should provide the "
        "context required to understand the child' - supplier is minted at scope "
        "business_operations and manufacturing does not declare it",
}


def _manifest() -> str:
    wave2 = json.loads(WAVE2.read_text())
    fragments = json.loads(FRAGMENTS.read_text())
    return json.dumps({
        "release_id": "wave2-industrial-test",
        "fragments": fragments["fragments"],
        "definitions": wave2["definitions"],
        "applicabilities": wave2["applicabilities"],
    })


@pytest.fixture(scope="module")
def catalogue():
    """The real loader, over the real file on disk, merged with the shipped fragments."""
    return load_catalogue(_manifest)


@pytest.fixture(scope="module")
def rows(catalogue):
    return tuple(catalogue.applicabilities.values())


@pytest.fixture(scope="module")
def definitions(catalogue):
    return tuple(catalogue.definitions.values())


# ---------------------------------------------------------------- it loads at all

def test_the_file_is_a_loadable_release(catalogue, rows, definitions):
    assert catalogue.release_id
    assert len(rows) == sum(EXPECTED_PER_SCHEMA.values()) == 60
    assert len(definitions) == 12
    assert Counter(row.uses_schema for row in rows) == EXPECTED_PER_SCHEMA


def test_every_row_names_a_definition_this_file_publishes(catalogue, rows):
    missing = sorted({(row.template_id, row.template_version) for row in rows}
                     - set(catalogue.definitions))
    assert missing == []
    assert all(row.template_id.startswith("def.") for row in rows)
    assert all(row.applicability_id.startswith("ap.") for row in rows)


def test_this_wave_touches_only_its_four_schemas(rows):
    assert {row.uses_schema for row in rows} == set(SCHEMAS)


# ------------------------------------------------- every field_ref is a LIVE key

def test_every_field_ref_is_a_live_key_for_that_schema(rows):
    """`DOMAIN_FIELDS` is imported, never restated. A copied field list in a test is a
    second source of truth that drifts, and the drift is invisible because both copies
    agree with each other."""
    dead = []
    for row in rows:
        live = set(DOMAIN_FIELDS[row.uses_schema])
        for binding in row.role_bindings:
            if binding.field_ref not in live:
                dead.append((row.applicability_id, binding.role_ref, binding.field_ref))
        for field_ref in row.allowed_fields:
            if field_ref not in live:
                dead.append((row.applicability_id, "allowed_fields", field_ref))
    assert dead == []


def test_no_row_binds_a_globally_non_destination_key(rows):
    """`60` section 9.1: *"Destination eligibility is a property of the KEY, not of the
    schema that references it."* `construction_property` declares `our_firm`, and
    `our_firm` is `destination_eligible: false` on the key, so no folder level may ever
    resolve to it — and `00` line 97 independently forbids "an author or organization
    merely as a collector"."""
    ineligible = {r.field_key for r in FIELD_ROWS if not r.destination_eligible}
    assert "our_firm" in ineligible, "the fixture this test depends on has moved"
    bound = {b.field_ref for row in rows for b in row.role_bindings}
    assert bound & ineligible == set()


# -------------------------------------------------------------- the label half

def _degenerate(label: str) -> str:
    return label.strip().lower().replace(" ", "_")


def test_no_label_is_the_key_it_replaces(rows):
    """The measured failure state, made unreachable. Checked case- and
    underscore-insensitively, so `"Record Type"` for `record_type` fails exactly as
    `"record_type"` does."""
    identical = [
        (row.applicability_id, binding.role_ref, binding.label, binding.field_ref)
        for row in rows for binding in row.role_bindings
        if _degenerate(binding.label) == binding.field_ref.lower()
    ]
    assert identical == []


def test_no_label_is_the_shipped_display_name_either(rows):
    """`facts/fields.py`'s own `display_name` slots are the key with the underscore
    replaced by a space — `"design item"`, `"record period"`. Reusing one here would pass
    the test above and still ship the internal vocabulary."""
    display = {r.field_key: r.display_name for r in FIELD_ROWS}
    echoes = [
        (row.applicability_id, binding.label, binding.field_ref)
        for row in rows for binding in row.role_bindings
        if _degenerate(binding.label) == _degenerate(display.get(binding.field_ref, ""))
    ]
    assert echoes == []


def test_the_label_lives_on_the_row_because_one_role_reads_per_audience(rows):
    """`RoleBinding`'s own docstring, and `00` section 5.1's ask that labels *"reflect the
    user's vocabulary rather than a universal corporate taxonomy"*. If the labels had been
    hoisted onto the definition, one role reaching thirteen rows would carry one string.
    A builder says "Site" or "The job", never "property"; a plant manager says "Line" or
    "Plant", never "site"; and the thirteen rows on the design-definition recipe call
    `design_item` a top assembly, a board, a structure, a process unit and a product
    model."""
    per_role = defaultdict(set)
    for row in rows:
        for binding in row.role_bindings:
            per_role[binding.role_ref].add(binding.label)
    assert len(per_role["design_item_anchor"]) >= 9
    assert len(per_role["operating_site"]) >= 6
    assert len(per_role["property_anchor"]) >= 5
    assert len(per_role["tracked_asset"]) >= 7


def test_a_label_holding_a_path_separator_is_rejected():
    """The negative twin. `P12` alone composes paths (resolution B3), so a level's display
    name may not carry one."""
    manifest = json.loads(_manifest())
    manifest["applicabilities"][0]["role_bindings"][0]["label"] = "Plant/Line"
    with pytest.raises(MalformedTemplateRecord, match="path separator"):
        load_catalogue(lambda: json.dumps(manifest))


def test_an_empty_label_is_rejected():
    """`RoleBinding.label` is required, *"not optional. An optional label is a label nobody
    authors."*"""
    manifest = json.loads(_manifest())
    manifest["applicabilities"][0]["role_bindings"][0]["label"] = "   "
    with pytest.raises(MalformedTemplateRecord):
        load_catalogue(lambda: json.dumps(manifest))


# --------------------------------------------- design_item is never product

def test_no_role_binds_both_design_item_and_product(rows):
    """`60` section 3 M10, written on both keys. `engineering`'s elimination *"checked
    project, subject, property and repository and never checked product, because product
    was minted in a different adjudication. A chiller model is a product model."* The line
    holds in two directions here: no role_ref resolves to both keys anywhere in the wave,
    and no single row allows both keys at once."""
    per_role = defaultdict(set)
    for row in rows:
        for binding in row.role_bindings:
            per_role[binding.role_ref].add(binding.field_ref)
    both = {role for role, fields in per_role.items()
            if {"design_item", "product"} <= fields}
    assert both == set()
    mixed = [row.applicability_id for row in rows
             if {"design_item", "product"} <= set(row.allowed_fields)]
    assert mixed == []


def test_the_two_keys_stay_on_their_own_schemas(rows):
    """The structural half of M10, and the reason the ruling is checkable rather than a
    convention: `60` section 5 declares `design_item` on `engineering` and nowhere else in
    this wave, and `product` on `manufacturing` and `resource_operations` and not on
    `engineering`. `engineering.product-certification` is where the temptation is
    strongest — its object is *"a marketing model or type designation placed on a
    market"* — and it binds `design_item`, because the file governs a controlled
    configuration rather than a sold article."""
    assert "product" not in DOMAIN_FIELDS["engineering"]
    assert "design_item" not in DOMAIN_FIELDS["manufacturing"]
    certification = next(r for r in rows
                         if r.applicability_id == "ap.engineering.product-certification")
    assert {b.field_ref for b in certification.role_bindings} == {"design_item",
                                                                 "artifact_type"}


def test_a_row_binding_outside_its_own_allow_list_is_rejected():
    """The negative twin for the field half. `TemplateApplicability` refuses it because
    *"a row that binds outside its own allow-list is how reuse turns a per-schema fact
    allow-list into a cross-domain union."*"""
    manifest = json.loads(_manifest())
    row = next(r for r in manifest["applicabilities"]
               if r["uses_schema"] == "engineering")
    row["role_bindings"][0]["field_ref"] = "product"
    with pytest.raises(MalformedTemplateRecord, match="which this row does not"):
        load_catalogue(lambda: json.dumps(manifest))


# ------------------------------------------------- asset is type versus instance

def test_no_recipe_forces_an_asset_level_on_a_multi_asset_document(catalogue, rows):
    """`manufacturing.asset-register` carries the restriction and `49` section 4.2(b)-(d)
    is the type-versus-instance rule behind it. Every candidate order of the recipe that
    row uses must mark the asset level OPTIONAL, because a register export naming forty
    machines has no single asset value and belongs at the site level as that site's
    population document."""
    register = next(r for r in rows
                    if r.applicability_id == "ap.manufacturing.asset-register")
    asset_roles = {b.role_ref for b in register.role_bindings if b.field_ref == "asset"}
    assert asset_roles == {"tracked_asset"}
    definition = catalogue.definitions[(register.template_id, register.template_version)]
    for order in definition.candidate_orders:
        asset_dims = [d for d in order.dimensions if d.role_ref == "tracked_asset"]
        assert asset_dims, order.order_id
        assert all(d.requirement == "optional" for d in asset_dims), order.order_id
    assert any("multi-asset register export" in text for text in register.exclusions)


def test_no_asset_level_is_ever_the_required_root_of_a_recipe(catalogue, rows):
    """The general form. An asset level may lead only where the file names ONE instance —
    `engineering.commissioning-handover`, whose whole anchor is *"an exact
    installed-instance identity (tag, loop, unit, skid or serial) shared between a test
    record, a punch item, an as-built sheet and an asset-schedule row"*. Everywhere else
    the asset sits beneath something that survives it."""
    leading_on_asset = set()
    for row in rows:
        definition = catalogue.definitions[(row.template_id, row.template_version)]
        bound = {b.role_ref: b.field_ref for b in row.role_bindings}
        for order in definition.candidate_orders:
            present = [d for d in order.dimensions if d.role_ref in bound]
            if present and bound[min(present, key=lambda d: d.order_index).role_ref] == "asset":
                leading_on_asset.add(row.applicability_id)
    assert leading_on_asset == {"ap.engineering.commissioning-handover"}


# ------------------------------------------------------------- the order half

def test_every_bound_role_resolves_to_a_position(catalogue, rows):
    """The shipped bug this wave had to avoid, in its own words: definition-local roles
    *"were absent from the merged order and routing sorted them LAST, silently inverting a
    recipe: a definition asking for venue first got venue last."* None of these
    definitions composes a fragment, so `relative_order` on the definition is the only
    thing that orders their roles. This runs the real merge and refuses to accept a role
    the merge does not place."""
    for row in rows:
        definition = catalogue.definitions[(row.template_id, row.template_version)]
        preferred = tuple(
            d.role_ref for d in sorted(definition.default_order.dimensions,
                                       key=lambda x: x.order_index))
        merged = merge_fragment_constraints(
            (), privacy_rank=lambda floor: {"baseline": 0}[floor],
            preferred_order=preferred, definition=definition)
        position = {role: i for i, role in enumerate(merged.ordered_roles)}
        unplaced = sorted({b.role_ref for b in row.role_bindings} - set(position))
        assert unplaced == [], (row.applicability_id, unplaced)


def test_a_definition_with_no_fragment_states_its_own_floor_and_its_own_order(definitions):
    """`TemplateDefinition` refuses a fragment-less definition with no `privacy_floor`
    because `C7` keeps the strongest floor among the included fragments and with none
    there is nothing to keep. `relative_order` is the same requirement one gate later."""
    for definition in definitions:
        assert definition.fragment_refs == ()
        assert definition.privacy_floor == "baseline"
        assert definition.relative_order, definition.template_id


def test_a_cyclic_relative_order_is_refused_by_the_merge(catalogue):
    """The negative twin for the order half. A definition whose own pairs contradict each
    other produces a cycle, and `C5` refuses rather than picking one — *"There is no hidden
    precedence rule and no last-writer-wins."*"""
    manifest = json.loads(_manifest())
    record = next(d for d in manifest["definitions"]
                  if d["template_id"] == "def.design-definition-record")
    record["relative_order"] = [["programme_anchor", "design_item_anchor"],
                                ["design_item_anchor", "artifact_kind"],
                                ["artifact_kind", "programme_anchor"]]
    broken = load_catalogue(
        lambda: json.dumps(manifest)).definitions[("def.design-definition-record", 1)]
    with pytest.raises(CompositionConflict, match="cycle"):
        merge_fragment_constraints(
            (), privacy_rank=lambda floor: {"baseline": 0}[floor],
            preferred_order=(), definition=broken)


def test_a_definition_missing_a_required_key_is_refused():
    """The negative twin for the record shape. `catalogue._definition` reads the keys by
    name; a record missing one is a `KeyError` at load, not a definition with a hole."""
    manifest = json.loads(_manifest())
    del manifest["definitions"][0]["sensitivity_policy_ref"]
    with pytest.raises(KeyError):
        load_catalogue(lambda: json.dumps(manifest))


def test_one_default_order_per_definition_and_no_invented_alternative(definitions):
    """`51`'s two-order floor has exactly one exit: `sole_order_attestation`, prose
    attesting that the corpora show one nesting. *"An invented alternative is worse than
    an absent one, because the user cannot tell it is invented."* Every multi-role recipe
    here either offers two orders that two different node rows argue, or attests in prose
    that its own corpora record one."""
    for definition in definitions:
        defaults = [o for o in definition.candidate_orders if o.is_default]
        assert len(defaults) == 1, definition.template_id
        roles = definition.candidate_orders[0].role_set()
        assert all(o.role_set() == roles for o in definition.candidate_orders)
        if len(roles) > 1 and len(definition.candidate_orders) == 1:
            assert definition.sole_order_attestation, definition.template_id
            assert len(definition.sole_order_attestation) > 200, definition.template_id
        if len(definition.candidate_orders) > 1:
            assert not definition.sole_order_attestation, definition.template_id


def test_the_period_never_leads_a_recipe(catalogue, rows):
    """`00`, quoted by all four schema rows: *"For document and record domains, project,
    function, or subject usually comes before time because putting year first scatters
    related work across calendar folders."* `record_period` is declared on `manufacturing`
    and `resource_operations` and leads nothing."""
    for row in rows:
        definition = catalogue.definitions[(row.template_id, row.template_version)]
        bound = {b.role_ref: b.field_ref for b in row.role_bindings}
        for order in definition.candidate_orders:
            present = [d for d in order.dimensions if d.role_ref in bound]
            if not present:
                continue
            first = min(present, key=lambda d: d.order_index)
            assert bound[first.role_ref] != "record_period", (
                row.applicability_id, order.order_id)


def test_no_variant_inverts_the_recommendation_of_a_row_it_carries(catalogue, rows):
    """Why two `.product-led` and `.job-led` variants exist at all rather than one record
    with a chosen default. `manufacturing.work-instruction` records the product above the
    station and `manufacturing.production-planning` records the site above the product;
    `construction_property.construction-project` reverses the family default explicitly and
    `construction_property.snagging-defects` puts a development's plots BELOW its scheme.
    A single record would have given one of each pair a preview that inverts its own
    recorded order — which is `51`'s venue-first-got-venue-last bug arriving as a shared
    default."""
    def default_sequence(row):
        definition = catalogue.definitions[(row.template_id, row.template_version)]
        bound = {b.role_ref for b in row.role_bindings}
        return tuple(d.role_ref for d in sorted(definition.default_order.dimensions,
                                                key=lambda x: x.order_index)
                     if d.role_ref in bound)
    by_id = {row.applicability_id: row for row in rows}
    assert default_sequence(by_id["ap.manufacturing.work-instruction"]) == (
        "output_product", "operating_site", "record_function")
    assert default_sequence(by_id["ap.manufacturing.production-planning"]) == (
        "operating_site", "output_product", "record_function")
    assert default_sequence(by_id["ap.construction_property.snagging-defects"]) == (
        "job_anchor", "property_anchor", "work_function")
    assert default_sequence(by_id["ap.construction_property.agency-listing"]) == (
        "property_anchor", "job_anchor", "work_function")


# ------------------------------------------------------------------ provenance

def test_every_row_traces_back_to_a_ratified_node_row(rows):
    """`TemplateApplicability` requires it: *"a compiled row nobody can trace back to the
    domain research that justified it cannot be reviewed or retired."* Placeholders would
    satisfy the record and defeat the point, so the shape is checked: a `row:` pointer
    whose id is this row's own id, and a `memo:` pointer at the research file behind it."""
    for row in rows:
        node_id = row.applicability_id[len("ap."):]
        assert ("row:" + node_id) in row.provenance, row.applicability_id
        assert any(p.startswith("memo:") and node_id in p for p in row.provenance)
        assert any("60-VOCABULARY-RULINGS" in p for p in row.provenance)
        assert any("53-HUMAN-SENSE-CHECK" in p for p in row.provenance)
        assert all(p.strip() and "TODO" not in p and "TBD" not in p
                   for p in row.provenance)


def test_a_row_with_no_provenance_is_rejected():
    """The negative twin."""
    manifest = json.loads(_manifest())
    manifest["applicabilities"][0]["provenance"] = []
    with pytest.raises(MalformedTemplateRecord, match="provenance"):
        load_catalogue(lambda: json.dumps(manifest))


def test_every_row_carries_the_detection_signal_of_its_own_node(rows):
    for row in rows:
        node_id = row.applicability_id[len("ap."):]
        assert row.detection_signal_refs == ("recognition:" + node_id,)


def test_no_row_states_a_floor_the_injected_ranking_would_not_know(rows):
    """`51` section 9.4: the floor vocabulary is `P7`'s, injected per deployment. `None` is
    the record's marker for *"this row adds no floor of its own"*, and a row naming a
    symbol the injected `privacy_rank` does not know would fail at `C7`."""
    assert {row.privacy_floor for row in rows} == {None}


# ------------------------------------------------------------------- refusals

def test_the_refusals_are_recorded_and_none_of_them_was_quietly_authored(rows):
    """Refusing is a valid outcome and it has to be visible, or a gap is
    indistinguishable from an oversight. Each entry in `REFUSED` carries the sentence from
    the row's own prose that earned it, and every one of them says the same thing: the
    level the row LEADS with has no declared key."""
    authored = {row.applicability_id[len("ap."):] for row in rows}
    assert authored & set(REFUSED) == set()
    for node_id, reason in REFUSED.items():
        assert node_id.split(".")[0] in SCHEMAS
        assert len(reason) > 120, node_id


def test_every_authored_row_names_a_node_that_exists_and_was_not_refused():
    """The reverse check, against the research surface itself. It SKIPS when
    `planning/domains/` is absent rather than passing, because a green test that checked
    nothing is the failure this suite is about."""
    if not NODES.is_dir():
        pytest.skip("planning/domains/nodes is a research surface; nothing to check")
    wave2 = json.loads(WAVE2.read_text())
    for record in wave2["applicabilities"]:
        node_id = record["applicability_id"][len("ap."):]
        path = NODES / (node_id + ".json")
        assert path.is_file(), node_id
        node = json.loads(path.read_text())
        assert node.get("refuse_node") is not True, node_id
        assert node["kind"] == "template", node_id
