"""Wave 2, the organisational schemas: `business_operations`, `hr`, `nonprofit`,
`government`.

**The hole this file's data closes.** Recognition compiles 358 rows across all 23
schemas and `60` §5 declares fields for 20 of them, but the shipped template
catalogue covered 6. `51` §4.8 named the consequence for one schema — *"the
product ships recognising résumés, offer letters and recruiter threads, and has
nowhere to put any of them"* — and it was true of seventeen. An HR manager, a
charity administrator and a civil servant were each recognised and unfileable.

**What these tests are for.** Not that the JSON parses. They exist to pin the
five things this particular wave can silently lose:

1. **The records must survive the REAL loader.** `wave2_organisational.json` is
   merged with the shipped `fragments.json` and a release id and driven through
   `tree_design.catalogue.load_catalogue`, so every definition has passed
   `TemplateDefinition.__post_init__` and every row `TemplateApplicability`'s.
   A record the live product would reject cannot pass here.
2. **A label that is its own key is the failure state, not a placeholder.**
   `59` §5c measured it next door: of `facts/fields.py`'s 37 `display_name`
   slots, 19 are byte-identical to the key and the other 18 are the key with the
   underscore opened out. `facts.fields` still ships `record period`,
   `people cycle` and `issuing body` as display names; nothing here may.
3. **`relative_order` must actually order every role.** The shipped bug it
   exists to prevent: roles no fragment constrained were absent from the merged
   order and `routing` sorted them LAST — *"a definition asking for venue first
   got venue last."* Every definition in this file is fragment-less, so ALL of
   its roles are definition-local and every one of them is exposed to that bug.
   `test_every_definition_resolves_to_one_determinate_nesting` drives the real
   `merge_fragment_constraints` and fails if a nesting is under-determined.
4. **`hr` is a PROTECTION schema and that is a safety property.** `60` J-5 ships
   it on the argument that *"employee-identifying content is protected before any
   cloud step"*, and its two folded keys are non-destination for a stated reason:
   *"Even a pseudonymous case reference can disclose that a person has a
   grievance, capability, disciplinary, health, or injury file."* Safety
   properties need tests, not intentions, so
   `test_no_hr_level_can_be_built_from_a_person_identifying_key` asserts it
   against the LIVE `facts.fields` catalogue rather than against a list retyped
   here — a key later promoted to destination-eligible turns it red.
5. **A refusal is a deliverable and must be as traceable as a row.** 48 of the
   66 live rows in these four schemas earned no template, almost always because
   the level their own prose puts first has no declared key. That is a fact
   about the vocabulary, and a wave that recorded only its successes would look
   identical to a wave that quietly skipped the hard rows.
   `test_every_live_row_is_either_covered_or_refused_by_name` closes it.
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter

import pytest

import tree_design
from facts.fields import DOMAIN_FIELDS, FIELD_ROWS
from tree_design.catalogue import load_catalogue
from tree_design.templates import (
    CompositionConflict,
    MalformedTemplateRecord,
    merge_fragment_constraints,
)

LIBRARY = pathlib.Path(tree_design.__file__).parent / "library"
WAVE_PATH = LIBRARY / "wave2_organisational.json"
FRAGMENTS_PATH = LIBRARY / "fragments.json"

REPO = pathlib.Path(__file__).resolve().parents[2]
NODES = REPO / "planning" / "domains" / "nodes"

SCHEMAS = ("business_operations", "hr", "nonprofit", "government")

#: `60` §5 as adopted, and the counts this wave could reach. `government`
#: declares one field by B1 and `hr` two by J-5, so a thin wave there is the
#: vocabulary working rather than an unfinished pass.
EXPECTED_ROWS_PER_SCHEMA = {
    "business_operations": 8, "hr": 6, "nonprofit": 2, "government": 3,
}


# --------------------------------------------------------------------------
# Load. The real loader, over the real file, merged with the shipped fragments.
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def raw() -> dict:
    return json.loads(WAVE_PATH.read_text())


@pytest.fixture(scope="module")
def fragments_raw() -> list[dict]:
    return json.loads(FRAGMENTS_PATH.read_text())["fragments"]


def _manifest(wave: dict, fragments: list[dict]) -> str:
    """One release carrying this wave beside the 22 published fragments.

    The fragments are included even though no definition here composes one:
    a release that dropped them would let a definition silently reference a
    fragment that does not exist, and C1 would then be passing on an absence.
    """
    return json.dumps({
        "release_id": "rel-wave2-organisational",
        "fragments": fragments,
        "definitions": wave["definitions"],
        "applicabilities": wave["applicabilities"],
    })


@pytest.fixture(scope="module")
def catalogue(raw, fragments_raw):
    return load_catalogue(lambda: _manifest(raw, fragments_raw))


@pytest.fixture(scope="module")
def definitions(catalogue):
    return tuple(catalogue.definitions.values())


@pytest.fixture(scope="module")
def rows(catalogue):
    return tuple(catalogue.applicabilities.values())


def test_the_wave_loads_through_the_real_loader(catalogue, definitions, rows):
    """Not "the JSON is well-formed". Every definition has passed
    `_check_orders` — which is what refuses an unset default, a duplicated order
    id, and a multi-dimension recipe offering one order with nothing said about
    why — and every row has passed the binding-outside-its-own-allow-list and
    empty-provenance guards."""
    assert catalogue.release_id == "rel-wave2-organisational"
    assert len(definitions) == 8
    assert len(rows) == 19


def test_each_schema_carries_the_rows_its_vocabulary_can_reach(rows):
    assert Counter(r.uses_schema for r in rows) == EXPECTED_ROWS_PER_SCHEMA


def test_a_record_is_identified_once(raw):
    d = [(x["template_id"], x["template_version"]) for x in raw["definitions"]]
    a = [(x["applicability_id"], x["applicability_version"])
         for x in raw["applicabilities"]]
    assert len(set(d)) == len(d) and len(set(a)) == len(a)


def test_this_wave_reuses_no_identifier_the_launch_library_already_shipped(raw):
    """The compiler merges wave files into one release keyed by
    `(id, version)`. A collision would not raise — it would REPLACE, and one of
    the two recipes would vanish from the catalogue with nothing said."""
    shipped_defs = {
        (x["template_id"], x["template_version"])
        for x in json.loads((LIBRARY / "definitions.json").read_text())["definitions"]
    }
    shipped_rows = {
        (x["applicability_id"], x["applicability_version"])
        for x in json.loads(
            (LIBRARY / "applicabilities.json").read_text())["applicabilities"]
    }
    mine_defs = {(x["template_id"], x["template_version"])
                 for x in raw["definitions"]}
    mine_rows = {(x["applicability_id"], x["applicability_version"])
                 for x in raw["applicabilities"]}
    assert shipped_defs & mine_defs == set()
    assert shipped_rows & mine_rows == set()


# --------------------------------------------------------------------------
# Every field_ref is a live key THIS schema declares, read from the catalogue.
# --------------------------------------------------------------------------

def test_every_bound_field_is_live_and_destination_eligible_for_its_schema(rows):
    """`DOMAIN_FIELDS` is imported rather than retyped, so `60` §5 moving under
    this file turns it red instead of leaving a row bound to a key its schema
    stopped declaring. Destination eligibility is checked from `FIELD_ROWS` for
    the same reason and because §9.1 settled that it is a property of the KEY:
    a schema cannot make an eligible key ineligible for itself, and a template
    certainly cannot make an ineligible one eligible."""
    destination_eligible = {r.field_key for r in FIELD_ROWS
                            if r.destination_eligible}
    for row in rows:
        declared = DOMAIN_FIELDS[row.uses_schema]
        for field in row.allowed_fields:
            assert field in declared, (row.applicability_id, field)
            assert field in destination_eligible, (row.applicability_id, field)
        for binding in row.role_bindings:
            assert binding.field_ref in declared, (
                row.applicability_id, binding.field_ref)


def test_government_reaches_exactly_the_one_key_B1_left_it(rows):
    """`60` B1 struck `record_type`, `record_period`, `property` and
    `subject_of_record` from `government` because *"the schema's own
    open_question asks to stay field-less and to adjudicate centrally rather
    than in children"*. A template is a child; this is what stops one putting
    them back through a role binding."""
    gov = [r for r in rows if r.uses_schema == "government"]
    assert {b.field_ref for r in gov for b in r.role_bindings} == {"project"}
    assert DOMAIN_FIELDS["government"] == ("project",)


# --------------------------------------------------------------------------
# The labels. This is the deliverable.
# --------------------------------------------------------------------------

def _normalise(value: str) -> str:
    return value.strip().casefold().replace("_", " ")


def test_no_label_is_the_field_key_it_replaces(rows):
    """Both halves of the measured failure: the key itself, and the key with its
    underscores opened out. Case-folded, because `"Project"` for `project` is the
    same failure wearing a capital."""
    identical = [(r.applicability_id, b.field_ref, b.label)
                 for r in rows for b in r.role_bindings
                 if b.label == b.field_ref]
    assert identical == []
    despaced = [(r.applicability_id, b.field_ref, b.label)
                for r in rows for b in r.role_bindings
                if _normalise(b.label) == _normalise(b.field_ref)]
    assert despaced == []


def test_no_label_is_its_role_name_either(rows):
    """A role is a cross-schema abstraction and must never reach the interface —
    `53` §4b failed eleven of fifteen roles on the name-out-loud test, *"Nobody
    says 'occasion anchor.'"* This caught a real one in this wave: `"Reporting
    period"` bound to `reporting_period`, which reads as English and is the
    internal key spelled out."""
    leaked = [(r.applicability_id, b.role_ref, b.label)
              for r in rows for b in r.role_bindings
              if _normalise(b.label) == _normalise(b.role_ref)]
    assert leaked == []


def test_no_label_is_the_field_catalogues_own_display_name(rows):
    """`facts/fields.py` ships `record period`, `people cycle` and `issuing
    body` as `display_name`s. Copying one here would satisfy both tests above
    while changing nothing a person reads, because those display names ARE the
    key with a space."""
    display = {r.field_key: r.display_name for r in FIELD_ROWS}
    copied = [(r.applicability_id, b.field_ref, b.label)
              for r in rows for b in r.role_bindings
              if _normalise(b.label) == _normalise(display.get(b.field_ref, ""))]
    assert copied == []


def test_every_binding_carries_a_label_and_the_labels_are_audience_specific(rows):
    """`00` §5.1 asks labels to *"reflect the user's vocabulary rather than a
    universal corporate taxonomy"*, which is a statement about the AUDIENCE. Six
    `hr` rows share one definition and one field; a charity officer says
    "Funder", not "institution". One name per field would be
    `facts/fields.py`'s `display_name` with better words."""
    bindings = [b for r in rows for b in r.role_bindings]
    assert len(bindings) == 31
    assert all(b.label.strip() for b in bindings)

    hr_rounds = {r.applicability_id: b.label for r in rows
                 for b in r.role_bindings
                 if r.uses_schema == "hr" and b.field_ref == "people_cycle"}
    assert len(hr_rounds) == 6
    assert len(set(hr_rounds.values())) == 6, hr_rounds
    assert hr_rounds["ap.hr.payroll-benefits-administration"] != \
        hr_rounds["ap.hr.performance-cycle"]

    per_field: dict[str, set[str]] = {}
    for r in rows:
        for b in r.role_bindings:
            per_field.setdefault(b.field_ref, set()).add(b.label)
    assert len(per_field["record_type"]) >= 5
    assert len(per_field["project"]) >= 5
    assert len(per_field["record_period"]) >= 4


# --------------------------------------------------------------------------
# Ordering. Every definition here is fragment-less, so every role is local.
# --------------------------------------------------------------------------

def _rank(floor: str) -> int:
    return {"baseline": 0}[floor]


def test_every_definition_resolves_to_one_determinate_nesting(definitions):
    """The shipped bug, closed for this wave.

    `merge_fragment_constraints` takes the definition's roles from its candidate
    orders and its edges from `relative_order`. With no fragments there is
    nothing else supplying either, so a definition whose `relative_order` leaves
    two roles unranked raises C5 at runtime — or, before the fallback was
    removed, silently sorted them last. Driven through the real merge with the
    real refusal, per definition."""
    for definition in definitions:
        merged = merge_fragment_constraints(
            (), privacy_rank=_rank, definition=definition)
        expected = tuple(
            d.role_ref for d in sorted(definition.default_order.dimensions,
                                       key=lambda d: d.order_index))
        assert merged.ordered_roles == expected, definition.template_id
        assert merged.privacy_floor == "baseline"


def test_a_cyclic_relative_order_is_refused_rather_than_silently_resolved(raw,
                                                                         fragments_raw):
    """Mutated from a REAL definition in this file, not a fixture, so it is this
    data that would be refused. The record loads — a cycle is not a malformed
    record — and the COMPOSER is what refuses it, which is the seam the
    definition-level `relative_order` was added to."""
    mutated = json.loads(json.dumps(raw))
    victim = next(d for d in mutated["definitions"]
                  if len(d.get("relative_order", [])) >= 2)
    before, after = victim["relative_order"][0]
    victim["relative_order"].append([after, before])
    catalogue = load_catalogue(lambda: _manifest(mutated, fragments_raw))
    definition = catalogue.definitions[
        (victim["template_id"], victim["template_version"])]
    with pytest.raises(CompositionConflict, match="cycle"):
        merge_fragment_constraints((), privacy_rank=_rank, definition=definition)


def test_a_multi_dimension_recipe_offers_two_orders_or_attests_why_it_cannot(
        definitions):
    """Amendment D's floor and its one exit. The exit is prose rather than a
    boolean because *"a flag records that somebody wanted the exception, and a
    sentence records why anyone should believe it"* — and an invented
    alternative is worse than an absent one, *"because the user cannot tell it
    is invented."*"""
    for definition in definitions:
        roles = definition.candidate_orders[0].role_set()
        if len(roles) <= 1:
            assert len(definition.candidate_orders) == 1, definition.template_id
            assert definition.sole_order_attestation is None, definition.template_id
            continue
        if len(definition.candidate_orders) == 1:
            attestation = (definition.sole_order_attestation or "").strip()
            assert len(attestation) > 200, definition.template_id
        else:
            assert definition.sole_order_attestation is None, definition.template_id
        assert sum(o.is_default for o in definition.candidate_orders) == 1


def test_a_row_truncates_a_recipe_from_the_leaf_end_and_never_from_the_middle(
        catalogue, rows):
    """A row may bind fewer roles than its recipe defines — most rows in this
    wave do, because the level their prose wants next has no declared key. What
    it may NOT do is delete a middle level and leave the user nesting the recipe
    never argued.

    So every row's bindings must be a PREFIX of some candidate order the
    definition actually offers. `ap.business_operations.compliance-audit` is the
    case that gives the rule its teeth: it binds the scheme and then the
    evidence kind, skipping the period — which is a hole in the DEFAULT order
    and a clean prefix of the second one, the order the row argued for when it
    said the fiscal period 'must drop below the control-or-finding level or fall
    out entirely'. A row that matched no order would be filing against a shape
    nobody wrote down.
    """
    for row in rows:
        definition = catalogue.definitions[(row.template_id, row.template_version)]
        bound = [b.role_ref for b in row.role_bindings]
        matched = [
            order.order_id for order in definition.candidate_orders
            if [d.role_ref for d in sorted(order.dimensions,
                                           key=lambda d: d.order_index)
                ][:len(bound)] == bound
        ]
        assert matched, (row.applicability_id, bound)


def test_a_fragment_less_definition_states_its_own_privacy_floor(definitions):
    """C7 keeps the strongest floor among the INCLUDED fragments, and with none
    included there is nothing to take a maximum of. Every definition in this
    wave is fragment-less, so every one must carry the floor itself — the same
    thing career's D30 does for the same reason."""
    for definition in definitions:
        assert definition.fragment_refs == ()
        assert definition.privacy_floor == "baseline", definition.template_id


# --------------------------------------------------------------------------
# `hr` is a protection schema. This is the safety property.
# --------------------------------------------------------------------------

#: Read from the live catalogue, never retyped: the keys whose whole reason for
#: being non-destination is that a PATH built from one discloses something about
#: a person. `60` J-5 on `workforce_member`: *"A folder bearing an employee's
#: name discloses personnel-record membership."* On `personnel_case`: *"Even a
#: pseudonymous case reference can disclose that a person has a grievance,
#: capability, disciplinary, health, or injury file."* Neither was minted; both
#: fold — to `subject_of_record` and to `event` respectively.
def _hr_person_identifying_keys() -> set[str]:
    return {"subject_of_record", "workforce_unit", "workforce_member",
            "personnel_case", "people", "authored_by", "account_holder"}


def test_no_hr_level_can_be_built_from_a_person_identifying_key(rows):
    """Asserted, not intended.

    Every `hr` row in this wave opens exactly one level and binds it to
    `people_cycle` — the one key in the schema that names a PROCESS the holder
    runs rather than a person it runs it on. Nothing else may be bound, and the
    test says so directly rather than inferring it from the row count."""
    hr_rows = [r for r in rows if r.uses_schema == "hr"]
    assert hr_rows, "the schema whose safety property this is must have rows"
    forbidden = _hr_person_identifying_keys()
    for row in hr_rows:
        assert set(row.allowed_fields) == {"people_cycle"}, row.applicability_id
        for binding in row.role_bindings:
            assert binding.field_ref == "people_cycle", row.applicability_id
            assert binding.field_ref not in forbidden, row.applicability_id


def test_the_hr_keys_that_disclose_a_person_are_non_destination_in_the_catalogue(
        rows):
    """The structural half. A row cannot bind these today because `resolve_role_
    to_field` refuses a non-destination key at C2 — but eligibility lives in
    `facts.fields`, not here, so this pins the fact rather than assuming it. If
    `subject_of_record` or `workforce_unit` is ever promoted, this turns red and
    the promotion gets read against J-5 before an hr template can use it."""
    eligible = {r.field_key for r in FIELD_ROWS if r.destination_eligible}
    for key in ("subject_of_record", "workforce_unit"):
        assert key in DOMAIN_FIELDS["hr"]
        assert key not in eligible, key
    # `event` IS eligible — §9.1 corrected `60` §5's `hr · event†`, because
    # marking it ineligible would have broken photos' `year -> event` template.
    # hr's protection is carried by the two keys above, and this wave binds
    # `event` on no hr row: the only hr material that is event-shaped is an
    # incident or a personnel case, and both disclose.
    assert "event" in eligible
    assert not [b for r in rows if r.uses_schema == "hr"
                for b in r.role_bindings if b.field_ref == "event"]


def test_no_label_anywhere_in_this_wave_reads_as_a_person(rows):
    """`00` §3.8: *"It should avoid using authorship or creator identity as a
    destination dimension."* The field guard above stops the DESTINATION; this
    stops the NAME, because a level called "Employee" or "Donor" invites the
    user to fill it with one even where the recipe bound a process."""
    banned = {"employee", "employee name", "staff member", "person", "donor",
              "member", "beneficiary", "patient", "applicant", "candidate",
              "registrant", "requester", "respondent", "complainant"}
    offenders = [(r.applicability_id, b.label) for r in rows
                 for b in r.role_bindings if _normalise(b.label) in banned]
    assert offenders == []


# --------------------------------------------------------------------------
# The malformed-record guards, exercised on THIS file's data.
# --------------------------------------------------------------------------

def test_a_label_holding_a_path_separator_is_rejected_by_the_loader(raw,
                                                                    fragments_raw):
    """P12 alone composes paths (resolution B3)."""
    for separator in ("/", "\\"):
        mutated = json.loads(json.dumps(raw))
        mutated["applicabilities"][0]["role_bindings"][0]["label"] = \
            f"Charter{separator}Closure"
        with pytest.raises(MalformedTemplateRecord, match="path separator"):
            load_catalogue(lambda: _manifest(mutated, fragments_raw))


def test_a_row_missing_its_provenance_is_rejected_by_the_loader(raw,
                                                               fragments_raw):
    """*"A compiled row nobody can trace back to the domain research that
    justified it cannot be reviewed or retired."*"""
    mutated = json.loads(json.dumps(raw))
    mutated["applicabilities"][0]["provenance"] = []
    with pytest.raises(MalformedTemplateRecord, match="provenance"):
        load_catalogue(lambda: _manifest(mutated, fragments_raw))


def test_a_record_missing_a_required_key_is_rejected_by_the_loader(raw,
                                                                  fragments_raw):
    """`_definition` and `_applicability` read required keys by subscript, so a
    dropped key is a `KeyError` at load rather than a `None` that survives into
    a frozen tree."""
    mutated = json.loads(json.dumps(raw))
    del mutated["definitions"][0]["sensitivity_policy_ref"]
    with pytest.raises(KeyError):
        load_catalogue(lambda: _manifest(mutated, fragments_raw))


def test_a_binding_outside_the_rows_own_allow_list_is_rejected(raw,
                                                              fragments_raw):
    """The guard that keeps reuse from turning a per-schema allow-list into a
    cross-domain union — exercised with `subject_of_record`, the exact key `hr`
    must never reach."""
    mutated = json.loads(json.dumps(raw))
    row = next(r for r in mutated["applicabilities"] if r["uses_schema"] == "hr")
    row["role_bindings"][0]["field_ref"] = "subject_of_record"
    with pytest.raises(MalformedTemplateRecord, match="does not"):
        load_catalogue(lambda: _manifest(mutated, fragments_raw))


def test_a_definition_with_no_default_order_is_rejected(raw, fragments_raw):
    """*"None means nothing can be previewed, and two means the recommendation
    is undefined."*"""
    mutated = json.loads(json.dumps(raw))
    mutated["definitions"][0]["candidate_orders"][0]["is_default"] = False
    with pytest.raises(MalformedTemplateRecord, match="default"):
        load_catalogue(lambda: _manifest(mutated, fragments_raw))


# --------------------------------------------------------------------------
# Refusals are a deliverable, and they are traceable.
# --------------------------------------------------------------------------

def _live_rows(schema: str) -> set[str]:
    live = set()
    for path in NODES.glob(f"{schema}.*.json"):
        node = json.loads(path.read_text())
        if node.get("kind") == "template" and not node.get("refuse_node"):
            live.add(node["id"])
    return live


@pytest.mark.skipif(not NODES.exists(), reason="domain research surface absent")
def test_every_live_row_is_either_covered_or_refused_by_name(raw):
    """No row may be silently skipped.

    `planning/domains/` is the authorship surface and is not importable at
    runtime, so this skips rather than passes where it is absent — the one thing
    it must not do is look like it checked something it could not.
    """
    covered = {p[len("row:"):] for r in raw["applicabilities"]
               for p in r["provenance"] if p.startswith("row:")}
    refused = {x["row_id"] for x in raw["refusals"]}
    assert covered & refused == set(), "a row cannot be both built and refused"
    for schema in SCHEMAS:
        live = _live_rows(schema)
        assert live, schema
        assert live - covered - refused == set(), schema


@pytest.mark.skipif(not NODES.exists(), reason="domain research surface absent")
def test_no_refusal_names_a_row_that_does_not_exist_or_was_already_refused(raw):
    """A refusal for a row the research surface already carries `refuse_node:
    true` for would be this wave taking credit for somebody else's decision."""
    for entry in raw["refusals"]:
        path = NODES / f"{entry['row_id']}.json"
        assert path.exists(), entry["row_id"]
        node = json.loads(path.read_text())
        assert node.get("refuse_node") is False, entry["row_id"]
        assert node["schema_id"] == entry["uses_schema"], entry["row_id"]


def test_every_refusal_quotes_the_sentence_behind_it(raw):
    """*"An honest gap beats an invented recipe"* — but only if the gap is
    legible. A refusal whose reason is a shrug is indistinguishable from a row
    nobody read."""
    assert len(raw["refusals"]) == 48
    assert Counter(x["uses_schema"] for x in raw["refusals"]) == {
        "government": 26, "business_operations": 14, "hr": 5, "nonprofit": 3}
    for entry in raw["refusals"]:
        assert len(entry["row_sentence"]) > 40, entry["row_id"]
        assert len(entry["why_no_template"]) > 120, entry["row_id"]


@pytest.mark.skipif(not NODES.exists(), reason="domain research surface absent")
def test_every_row_this_wave_builds_traces_to_a_real_node_file(raw):
    """Provenance is only traceable if the `row:` prefix resolves. One entry in
    this file previously carried a paragraph of prose after the id, which made
    it unresolvable while still looking like a reference."""
    for row in raw["applicabilities"]:
        refs = [p[len("row:"):] for p in row["provenance"]
                if p.startswith("row:")]
        assert refs, row["applicability_id"]
        for ref in refs:
            assert (NODES / f"{ref}.json").exists(), (row["applicability_id"], ref)
        memos = [p[len("memo:"):] for p in row["provenance"]
                 if p.startswith("memo:")]
        for memo in memos:
            assert (REPO / memo).exists(), (row["applicability_id"], memo)


def test_every_detection_signal_names_a_compiled_recognition_row(raw):
    """A recipe pointed at a signal recognition never compiled is a recipe
    nothing can reach. `nonprofit`'s restricted-grant row deliberately names the
    SCHEMA's own compiled row rather than a child, because
    `nonprofit.grant-reporting` was refused on the finding that *"Coverage
    routes through the schema, not through a padded row."*"""
    manifest = json.loads(
        (pathlib.Path(tree_design.__file__).parents[1]
         / "recognition" / "library" / "recognition.json").read_text())
    compiled = {row for schema in manifest["schemas"].values()
                for row in schema["rows"]}
    for row in raw["applicabilities"]:
        for signal in row["detection_signal_refs"]:
            assert signal.startswith("recognition:"), row["applicability_id"]
            assert signal[len("recognition:"):] in compiled, (
                row["applicability_id"], signal)
