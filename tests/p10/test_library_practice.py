"""Wave 2, the practice slice: `law_practice`, `creative`, `clinical_practice`.

`51-LAUNCH-TEMPLATE-DRAFT.md` §4.8 named the hole for one schema — *"the product
ships recognising résumés, offer letters and recruiter threads, and has nowhere
to put any of them… a hole in the wave the owner has already declared full."*
`60-VOCABULARY-RULINGS.md` §5 closes the half of it that was a vocabulary
problem: it declares `project · work_type · client · record_period` on
`law_practice` and `project · artifact_type · stage · client · venue` on
`creative`, so under `PR-6` — a dimension may only branch on a field the schema
declares — these two schemas can carry a folder proposal for the first time.

Every node row in both families carries `template.dimension_order: []`, and every
one of them says the emptiness is by CONTRACT rather than by refusal, then states
the recommendation in prose in `template.why`. `src/tree_design/library/
wave2_practice.json` is that prose turned structural. This file drives it through
the real `load_catalogue` and the real `merge_fragment_constraints`, because a
JSON file that parses proves nothing.

Three things this file freezes, each of which the data can silently lose:

1. **`clinical_practice` ships NO template, and that is the ruling rather than an
   omission.** `60` §2 / J-5a makes it a PROTECTION schema and exempts it by name
   from `00`:48's 3–6 floor; `60` B1 leaves it exactly one field,
   `subject_of_record`, which §4 makes non-destination *"on the key, never per
   template"*. Its rows agree in their own words: `clinical_practice.patient-chart`
   — *"the one dimension this situation obviously wants is THE PATIENT, and a
   folder named for a patient publishes a third person's identity and the fact of
   their care in the filesystem namespace."* A schema whose only declared key can
   never be a level has no folder proposal to make, and inventing a level for it
   is the one thing this wave must not do.

2. **`law_practice` binds no `client`, deliberately.** `60` §5 makes the key
   destination-eligible and `law_practice.json` still seeds the LEVEL ineligible:
   *"in a single-client corpus it is 'use an author or organization merely as a
   collector' and would 'create meaningless one-child levels', and in any corpus
   it is a disclosure."* No record shape here can express *"ineligible until the
   user explicitly approves it"* — a bound optional role is an OFFERED level — so
   the honest encoding is that `client` stays a searchable fact and never a
   folder. Eligibility is a permission, not an obligation.

3. **The two-order floor is exited three times, by attestation and never by
   invention.** `law_practice`'s corpus reverses no pair of its own roles: every
   departure it records SUBTRACTS a level or asks for a level with no declared
   key. Authoring a second order to satisfy the record would be *"an invented
   alternative shown beside a real one"*, which the record itself calls worse
   than none.

Six rows earned a refusal and carry no template. They are named in
`REFUSED_WITH_REASON` with the sentence that justifies each, because an honest
gap is a deliverable and a silent one is a defect.
"""
from __future__ import annotations

import copy
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

#: Addressed through the package rather than the working directory: this is
#: shipped data, and a test that only found it from the repository root would
#: pass on a tree where the file was never installed.
LIBRARY = pathlib.Path(tree_design.__file__).parent / "library"
PRACTICE_JSON = LIBRARY / "wave2_practice.json"
FRAGMENTS_JSON = LIBRARY / "fragments.json"

REPO = pathlib.Path(__file__).resolve().parents[2]
NODES = REPO / "planning/domains/nodes"

#: `51`'s appendix writes the placeholder floor symbol `baseline` and assigns no
#: handling class; P7 injects the real vocabulary per deployment.
RANK = {"baseline": 0, "protected": 1}.__getitem__

HOLDER_OWN = "sp.holder-own-record@1"
THIRD_PARTY = "sp.third-party-confidential@1"

#: The six recipes this file ships, the schema each serves, and the policy ref it
#: declares. All six refs are from `51` §4.0's seven; this wave mints none.
DEFINITIONS = {
    "def.matter-file": ("law_practice", THIRD_PARTY),
    "def.matter-only-packet": ("law_practice", THIRD_PARTY),
    "def.practice-register": ("law_practice", THIRD_PARTY),
    "def.know-how-bank": ("law_practice", HOLDER_OWN),
    "def.making-record": ("creative", HOLDER_OWN),
    "def.shown-work-run": ("creative", THIRD_PARTY),
}

DEFAULT_ORDER_IDS = {
    "def.matter-file": "ord.matter-function-period",
    "def.matter-only-packet": "ord.matter-only",
    "def.practice-register": "ord.function-then-period",
    "def.know-how-bank": "ord.instrument-function-only",
    "def.making-record": "ord.client-work-stage-kind",
    "def.shown-work-run": "ord.show-venue-stage-kind",
}

#: The nesting each recipe RECOMMENDS, which is also the nesting its fragments
#: plus its own `relative_order` must derive with no hint supplied.
RECOMMENDED = {
    "def.matter-file": ("subject_anchor", "artifact_kind", "scope_period"),
    "def.matter-only-packet": ("subject_anchor",),
    "def.practice-register": ("artifact_kind", "scope_period"),
    "def.know-how-bank": ("artifact_kind",),
    "def.making-record": ("client_org", "subject_anchor", "lifecycle_stage",
                          "artifact_kind"),
    "def.shown-work-run": ("subject_anchor", "addressed_org", "lifecycle_stage",
                           "artifact_kind"),
}

EXPECTED_PER_SCHEMA = {"law_practice": 26, "creative": 28}

#: Every kept node row that earned NO template, and the sentence that earned it.
#: Two are `law_practice`, four are `creative`; `clinical_practice` refuses as a
#: whole schema and is asserted separately.
REFUSED_WITH_REASON = {
    "law_practice.client-intake":
        "NEITHER of its first two levels exists here. There is no matter, and "
        "there is no client - there is a person who asked",
    "law_practice.contract-negotiation":
        "HERE THE FIRST ORGANISING TOKEN IS THE INSTRUMENT STEM, then the ISSUE "
        "or CLAUSE THREAD, then the version or turn",
    "creative.raw-photo-catalogue":
        "a capture moment exists for every single one. A dimension that is "
        "missing on half an archive cannot be its top level",
    "creative.shoot-day-media":
        "A later schema pass may decide whether project, stage, artifact_type, "
        "event, capture_year or media_type are legal destination fields; this "
        "node must not mint them",
    "creative.stock-asset-library":
        "this row still should not default to project-first because the defining "
        "asset belongs to no one project",
    "creative.submission-query":
        "THE ADDRESSEE HAS NO KEY, AND `client` IS THE WRONG ONE",
}


# --------------------------------------------------------------------------
# Loading, through the real loader and nothing else.
# --------------------------------------------------------------------------

def _raw() -> dict:
    return json.loads(PRACTICE_JSON.read_text())


def _fragments() -> list[dict]:
    return json.loads(FRAGMENTS_JSON.read_text())["fragments"]


def _manifest(definitions=None, applicabilities=None, fragments=None) -> str:
    """One release: this file's records merged with the SHIPPED fragments.

    The fragments come from `fragments.json` untouched — this wave adds none, so
    a `fragment_refs` entry that does not resolve there is a recipe that cannot
    be composed at all, and the failure would otherwise surface at placement
    time far from the record that caused it.
    """
    raw = _raw()
    return json.dumps({
        "release_id": "rel-wave2-practice",
        "fragments": _fragments() if fragments is None else fragments,
        "definitions": raw["definitions"] if definitions is None else definitions,
        "applicabilities": (raw["applicabilities"] if applicabilities is None
                            else applicabilities),
    })


def _catalogue(**kwargs):
    return load_catalogue(lambda: _manifest(**kwargs))


@pytest.fixture(scope="module")
def catalogue():
    return _catalogue()


@pytest.fixture(scope="module")
def rows(catalogue):
    return tuple(catalogue.applicabilities.values())


def _shipped_definition(template_id: str) -> dict:
    return copy.deepcopy(
        next(d for d in _raw()["definitions"]
             if d["template_id"] == template_id))


def _shipped_row(applicability_id: str) -> dict:
    return copy.deepcopy(
        next(r for r in _raw()["applicabilities"]
             if r["applicability_id"] == applicability_id))


def test_the_top_level_shape_is_the_one_a_merge_step_can_read():
    """`load_catalogue` reads `manifest["definitions"]` and
    `manifest["applicabilities"]`, so this file's own top-level keys are the
    seam. A file that nests its records anywhere else merges as an empty
    release, and an empty release makes C1 pass by having nothing to resolve."""
    doc = _raw()
    assert sorted(doc) == ["applicabilities", "definitions"]
    assert doc["definitions"] and doc["applicabilities"]


def test_the_practice_wave_loads_through_the_real_loader(catalogue, rows):
    """Six definitions and 54 rows RESOLVE — not "the JSON is well-formed".
    Every record has passed `TemplateDefinition.__post_init__` and
    `TemplateApplicability.__post_init__`, which is what rejects an unset
    default order, a single order on a multi-role recipe with no attestation, a
    row binding outside its own allow-list, and a row with no provenance."""
    assert catalogue.release_id == "rel-wave2-practice"
    assert {tid for tid, _ in catalogue.definitions} == set(DEFINITIONS)
    assert len(catalogue.definitions) == 6
    assert len(rows) == 54


def test_every_definition_declares_the_scope_state_and_policy_ref_it_should(
        catalogue):
    for template_id, (_, policy) in sorted(DEFINITIONS.items()):
        record = catalogue.definitions[(template_id, 1)]
        assert record.origin_kind == "built-in", template_id
        assert record.scope_kind == "domain-focused", template_id
        assert record.publication_state == "published", template_id
        assert record.sensitivity_policy_ref == policy, template_id


def test_this_wave_mints_no_sensitivity_policy_ref(catalogue):
    """`51` §4.0 names seven `sp.*@1` refs. Nothing in the codebase READS this
    column, which is exactly why the set is asserted: an unread column is the
    one place a typo survives every other test."""
    assert {d.sensitivity_policy_ref for d in catalogue.definitions.values()} \
        <= {HOLDER_OWN, THIRD_PARTY, "sp.household-member-record@1",
            "sp.not-holder-personal@1", "sp.safety-domain-protected@1",
            "sp.credential-bearing@1", "sp.document-reproduced-whole@1"}


def test_every_fragment_ref_resolves_in_the_shipped_fragment_library(catalogue):
    """This wave adds no fragment — a sibling owns that file — so every
    `fragment_refs` entry must already exist at the exact version it pins."""
    dangling = [
        (record.template_id, ref.fragment_id, ref.fragment_version)
        for record in catalogue.definitions.values()
        for ref in record.fragment_refs
        if not catalogue.has_fragment(ref.fragment_id, ref.fragment_version)
    ]
    assert dangling == []
    assert all(record.fragment_refs for record in catalogue.definitions.values()), (
        "every recipe in this wave composes at least one published fragment; a "
        "fragmentless one would have to restate a privacy floor for the "
        "fragments' to drift from")


# --------------------------------------------------------------------------
# The recipes compose, and compose into what they recommend.
# --------------------------------------------------------------------------

def test_every_recipe_composes_through_the_real_merge(catalogue):
    for template_id, (_, _) in sorted(DEFINITIONS.items()):
        record = catalogue.definitions[(template_id, 1)]
        fragments = [catalogue.fragment(ref) for ref in record.fragment_refs]
        recommended = [d.role_ref for d in sorted(record.default_order.dimensions,
                                                  key=lambda d: d.order_index)]
        assert tuple(recommended) == RECOMMENDED[template_id], template_id
        merged = merge_fragment_constraints(
            fragments, privacy_rank=RANK, preferred_order=recommended,
            definition=record)
        assert list(merged.ordered_roles) == recommended, template_id
        assert merged.privacy_floor == "baseline", template_id


def test_each_recipe_states_the_nesting_its_fragments_cannot(catalogue):
    """The bug this guards against is a shipped one: a role no fragment
    constrains was absent from the merged order and `routing` sorted it LAST,
    *"a definition asking for venue first got venue last."*

    Every recipe here has such a role — `scope_period` and `client_org` appear in
    no published fragment, and no fragment carries `lifecycle_stage ->
    artifact_kind` — so each states its own `relative_order`. Called with NO
    recommendation supplied, the merge must still derive the recipe's own
    nesting rather than refusing it as under-determined.
    """
    for template_id in sorted(DEFINITIONS):
        record = catalogue.definitions[(template_id, 1)]
        fragments = [catalogue.fragment(ref) for ref in record.fragment_refs]
        merged = merge_fragment_constraints(
            fragments, privacy_rank=RANK, definition=record)
        assert tuple(merged.ordered_roles) == RECOMMENDED[template_id], template_id


def test_dropping_a_definitions_own_edges_leaves_the_merge_undetermined():
    """The discriminating half of the test above, on a REAL record.

    `def.matter-file` pins `artifact_kind -> scope_period` itself because no
    fragment does. Remove the pin and the merge must refuse BY NAME rather than
    sorting the unconstrained role to the leaf with a silent tie-break — which
    is the failure the amendment removed.
    """
    unpinned = _shipped_definition("def.matter-file")
    unpinned.pop("relative_order")
    record = _catalogue(definitions=[unpinned]).definitions[
        ("def.matter-file", 1)]
    assert record.relative_order == ()

    catalogue = _catalogue()
    fragments = [catalogue.fragment(ref) for ref in record.fragment_refs]
    with pytest.raises(CompositionConflict) as raised:
        merge_fragment_constraints(fragments, privacy_rank=RANK, definition=record)
    assert "unordered relative to each other" in str(raised.value)


def test_a_cyclic_relative_order_is_refused(catalogue):
    """C5 on a mutated copy of a shipped record. `def.matter-file` recommends
    matter -> function -> period; add the closing edge and the combined graph
    has a cycle, which no ordering the user chooses can resolve."""
    cyclic = _shipped_definition("def.matter-file")
    cyclic["relative_order"].append(["scope_period", "subject_anchor"])
    record = _catalogue(definitions=[cyclic]).definitions[("def.matter-file", 1)]
    fragments = [catalogue.fragment(ref) for ref in record.fragment_refs]

    with pytest.raises(CompositionConflict) as raised:
        merge_fragment_constraints(fragments, privacy_rank=RANK, definition=record)
    assert "cycle" in str(raised.value)


def test_every_definition_names_exactly_one_default_order(catalogue):
    for template_id, order_id in sorted(DEFAULT_ORDER_IDS.items()):
        record = catalogue.definitions[(template_id, 1)]
        assert record.default_order.order_id == order_id, template_id
        assert sum(o.is_default for o in record.candidate_orders) == 1, template_id


# --------------------------------------------------------------------------
# The two-order floor, and the exit this wave DOES use.
# --------------------------------------------------------------------------

#: The three multi-role recipes whose corpora attest exactly one nesting. Each
#: exits Amendment D's floor by a SENTENCE, and each sentence names the reversal
#: the corpus refuses in its own words.
ATTESTED = {
    "def.matter-file": "NOT TIME-FIRST, and no sibling may claim otherwise",
    "def.practice-register": "the function level must come first",
    "def.shown-work-run": "venue first, which scatters one show across "
                          "institutions",
}

#: The two single-ROLE recipes. The floor does not apply to them at all, so an
#: attestation on either would be an exception claimed where none was needed.
SINGLE_ROLE = ("def.matter-only-packet", "def.know-how-bank")


def test_the_attested_recipes_are_the_three_whose_corpora_attest_one_nesting(
        catalogue):
    attested = sorted(record.template_id
                      for record in catalogue.definitions.values()
                      if record.sole_order_attestation)
    assert attested == sorted(ATTESTED)
    for template_id, phrase in sorted(ATTESTED.items()):
        record = catalogue.definitions[(template_id, 1)]
        assert len(record.candidate_orders) == 1, template_id
        assert len(record.default_order.role_set()) > 1, template_id
        assert phrase in record.sole_order_attestation, (
            f"{template_id}'s attestation must quote the corpus that REFUSES the "
            "second order; an attestation that only asserts one nesting is a "
            "flag wearing a sentence's clothes")


def test_the_single_role_recipes_claim_no_exception_they_do_not_need(catalogue):
    for template_id in SINGLE_ROLE:
        record = catalogue.definitions[(template_id, 1)]
        assert len(record.candidate_orders) == 1, template_id
        assert len(record.default_order.role_set()) == 1, template_id
        assert record.sole_order_attestation is None, template_id


def test_the_one_recipe_with_two_orders_argues_both_from_a_corpus(catalogue):
    """`def.making-record` is the only recipe here that ships an alternative,
    and it ships one because three creative rows argue for it independently —
    `creative.printmaking-editions` (*"An edition does not move through stages;
    it passes through ONE-WAY TERMINAL EVENTS"*), `creative.short-form-writing`
    (*"a stage level would collapse one piece's AGNI rejection and its
    Ploughshares acceptance into a single folder named 'submitted'"*) and
    `creative.ad-campaign` (*"a stage level scatters one idea across three
    branches"*).

    `51` §4.9 marks an alternative nobody argued from a corpus with the word
    AUTHORED. Nothing in this wave carries it, and this asserts that rather than
    assuming it.
    """
    record = catalogue.definitions[("def.making-record", 1)]
    assert len(record.candidate_orders) == 2
    alternative = next(o for o in record.candidate_orders if not o.is_default)
    assert alternative.order_id == "ord.client-work-kind-stage"
    for phrase in ("printmaking-editions", "short-form-writing", "ad-campaign"):
        assert phrase in alternative.rationale
    assert [o.order_id for record in catalogue.definitions.values()
            for o in record.candidate_orders if "AUTHORED" in o.rationale] == []


def test_stripping_the_attestation_from_a_real_recipe_is_refused():
    """The record's own floor, exercised on shipped data. Drop the sentence and
    `def.matter-file` is a three-dimension recipe offering one order with nothing
    said about why — *"a single `dimensions` tuple wearing a new field name."*"""
    stripped = _shipped_definition("def.matter-file")
    stripped.pop("sole_order_attestation")
    with pytest.raises(MalformedTemplateRecord) as raised:
        _catalogue(definitions=[stripped])
    assert "at least two candidate orders" in str(raised.value)


def test_a_blank_attestation_does_not_open_the_exit():
    blank = _shipped_definition("def.matter-file")
    blank["sole_order_attestation"] = "   "
    with pytest.raises(MalformedTemplateRecord):
        _catalogue(definitions=[blank])


# --------------------------------------------------------------------------
# The labels. This is the deliverable a person reads.
# --------------------------------------------------------------------------

def _normalise(value: str) -> str:
    """Fold the two ways a key gets shipped as a label: the key itself, and the
    key with its underscores opened out. `59` §5c measured that those two
    account for 37 of 37 `display_name` values in `facts/fields.py` — *"Zero of
    37 differ from the key by anything else."*"""
    return value.strip().casefold().replace("_", " ")


def test_no_shipped_label_is_the_field_key_it_replaces(rows):
    """The measured failure state, made unreachable. Byte-identity is checked
    because that is 19 of the 37; the normalised form because the other 18 are
    the key with a space for the underscore, and because `"Project"` for
    `project` would otherwise slip through as new work while changing nothing a
    person reads."""
    identical = [(row.applicability_id, b.field_ref, b.label)
                 for row in rows for b in row.role_bindings
                 if b.label == b.field_ref]
    assert identical == []
    despaced = [(row.applicability_id, b.field_ref, b.label)
                for row in rows for b in row.role_bindings
                if _normalise(b.label) == _normalise(b.field_ref)]
    assert despaced == []


def test_no_shipped_label_is_the_role_name_either(rows):
    """`53` §4b failed eleven of fifteen roles on the name-out-loud test —
    *"Nobody says 'occasion anchor.'"* A role is a cross-schema abstraction and
    must never be shown, so leaking it into a label is the same defect as
    leaking the field key."""
    leaked = [(row.applicability_id, b.role_ref, b.label)
              for row in rows for b in row.role_bindings
              if _normalise(b.label) == _normalise(b.role_ref)]
    assert leaked == []


def test_every_binding_carries_a_label(rows):
    """`RoleBinding.label` is required rather than optional, deliberately: *"An
    optional label is a label nobody authors."* The record enforces it; this
    asserts the shipped data actually exercised the requirement, which a file of
    zero rows would also satisfy."""
    bindings = [b for row in rows for b in row.role_bindings]
    assert len(bindings) == 136
    assert all(b.label.strip() for b in bindings)


def test_a_label_holding_a_path_separator_is_rejected_by_the_loader():
    """P12 alone composes paths (resolution B3). Asserted through
    `load_catalogue` on a mutated copy of a REAL row rather than on a fixture,
    so it is this file's own data that would be refused."""
    for separator in ("/", "\\"):
        mutated = _shipped_row("ap.law_practice.appeals")
        mutated["role_bindings"][0]["label"] = f"Matter{separator}Appeal"
        with pytest.raises(MalformedTemplateRecord, match="path separator"):
            _catalogue(applicabilities=[mutated])


def test_a_binding_outside_the_rows_own_allow_list_is_rejected():
    """The guard that keeps reuse from turning a per-schema fact allow-list into
    a cross-domain union, exercised on shipped data."""
    mutated = _shipped_row("ap.law_practice.appeals")
    mutated["role_bindings"][0]["field_ref"] = "our_firm"
    with pytest.raises(MalformedTemplateRecord, match="does not"):
        _catalogue(applicabilities=[mutated])


def test_a_row_stripped_of_its_provenance_is_rejected():
    """*"A compiled row nobody can trace back to the domain research that
    justified it cannot be reviewed or retired."*"""
    mutated = _shipped_row("ap.creative.exhibition")
    mutated["provenance"] = []
    with pytest.raises(MalformedTemplateRecord, match="provenance"):
        _catalogue(applicabilities=[mutated])


def test_a_definition_missing_a_required_key_never_loads():
    """The loader reads `sensitivity_policy_ref` positionally. A record that
    omits it must fail AT LOAD rather than resolving to `None` and travelling to
    a reader that cannot tell an unset policy from an absent one."""
    mutated = _shipped_definition("def.making-record")
    del mutated["sensitivity_policy_ref"]
    with pytest.raises((KeyError, MalformedTemplateRecord)):
        _catalogue(definitions=[mutated])

    blanked = _shipped_definition("def.making-record")
    blanked["sensitivity_policy_ref"] = ""
    with pytest.raises(MalformedTemplateRecord):
        _catalogue(definitions=[blanked])


def test_the_labels_are_not_one_name_per_field(rows):
    """The regression this whole wave could produce is a library that authors one
    label per field key and calls the job done — which is `facts/fields.py`'s
    `display_name` with better words, and still one name for every audience.

    A lawyer says *"Matter"*, not `project`; a printmaker says *"The work"*; an
    ad agency says *"Campaign"*; a registrar says *"The show"*. All four are
    `project`.
    """
    per_field = defaultdict(set)
    for row in rows:
        for b in row.role_bindings:
            per_field[b.field_ref].add(b.label)
    assert len(per_field["project"]) >= 30
    assert len(per_field["artifact_type"]) >= 20
    assert len(per_field["work_type"]) >= 15
    assert len(per_field["stage"]) >= 15
    assert len(per_field["record_period"]) >= 8
    assert sum(len(v) for v in per_field.values()) > 15 * len(per_field)


def test_one_role_reads_differently_in_the_two_schemas_this_wave_serves(rows):
    """`RoleBinding`'s own docstring is the argument for where the label lives:
    *"one role reads differently per schema."* `subject_anchor` resolves to
    `project` in both families here and the two audiences do not say the same
    word about it — a solicitor's matter reference and a photographer's shoot are
    the same role and not the same noun. A label on the DEFINITION would be one
    name for both; these assertions are what would fail if it moved there.
    """
    by_schema = defaultdict(set)
    for row in rows:
        for b in row.role_bindings:
            if b.role_ref == "subject_anchor":
                by_schema[row.uses_schema].add(b.label)
    assert set(by_schema) == {"law_practice", "creative"}
    assert not (by_schema["law_practice"] & by_schema["creative"]), (
        "the two audiences share a label for one role, which is the universal "
        "corporate taxonomy 00 §5.1 asks labels not to be")


# --------------------------------------------------------------------------
# The rest of the row: schema, fields, provenance, detection.
# --------------------------------------------------------------------------

def test_every_schema_carries_the_row_count_this_wave_ratified(rows):
    assert Counter(row.uses_schema for row in rows) == EXPECTED_PER_SCHEMA


def test_a_row_is_identified_once_and_names_exactly_one_schema(rows):
    keys = [(r.applicability_id, r.applicability_version) for r in rows]
    assert len(set(keys)) == len(keys) == 54
    assert {row.uses_schema for row in rows} == set(EXPECTED_PER_SCHEMA)


def test_every_bound_field_is_one_its_schema_actually_declares(rows):
    """`60` §5 is the field contract and `facts.fields` is where it lives, so the
    rows are checked against the LIVE catalogue and never against a copy of `60`
    transcribed here — a transcription would go stale the first time a key moved
    and would keep passing."""
    destination_eligible = {row.field_key for row in FIELD_ROWS
                            if row.destination_eligible}
    for row in rows:
        declared = DOMAIN_FIELDS[row.uses_schema]
        for field in row.allowed_fields:
            assert field in declared, (row.applicability_id, field)
            assert field in destination_eligible, (row.applicability_id, field)


def test_a_row_allows_exactly_what_it_binds(rows):
    """`allowed_vocabulary_for` unions `allowed_fields` across the rows of one
    schema and hands the result to P8 as `Dossier.allowed_vocabulary`, which is
    also the placement-destination and target-node closure — so a field allowed
    here and bound nowhere widens five call sites for every row of the schema."""
    for row in rows:
        assert set(row.allowed_fields) == {b.field_ref for b in row.role_bindings}
        assert len(row.allowed_fields) == len(set(row.allowed_fields))


def test_every_required_role_of_the_chosen_recipe_is_bound(catalogue, rows):
    """C4 refuses a composition where a required role does not resolve, and the
    resolution comes from the ROW's bindings. A row that leaves a required role
    unbound is therefore a recipe that can never compose, and it would fail at
    placement time rather than here."""
    for row in rows:
        record = catalogue.definitions[(row.template_id, row.template_version)]
        required = {d.role_ref for d in record.default_order.dimensions
                    if d.requirement == "required"}
        offered = {d.role_ref for o in record.candidate_orders
                   for d in o.dimensions}
        bound = {b.role_ref for b in row.role_bindings}
        assert required <= bound, (row.applicability_id, required - bound)
        assert bound <= offered, (row.applicability_id, bound - offered)


def test_a_role_binds_one_field_per_schema(rows):
    """`00`: *"The system must separate roles that happen to contain the same
    entity type."* `client_org` (the party that commissioned the work) and
    `addressed_org` (the institution that showed it) are separate roles here for
    exactly that reason — an exhibiting gallery *"is not a commissioning
    counterparty; it shows work it did not order."*"""
    seen = defaultdict(set)
    for row in rows:
        for b in row.role_bindings:
            seen[(b.role_ref, row.uses_schema)].add(b.field_ref)
    assert all(len(fields) == 1 for fields in seen.values()), seen
    assert seen[("subject_anchor", "law_practice")] == {"project"}
    assert seen[("subject_anchor", "creative")] == {"project"}
    assert seen[("artifact_kind", "law_practice")] == {"work_type"}
    assert seen[("artifact_kind", "creative")] == {"artifact_type"}
    assert seen[("client_org", "creative")] == {"client"}
    assert seen[("addressed_org", "creative")] == {"venue"}


def test_every_row_traces_back_to_the_domain_row_that_justified_it(rows):
    """The record only requires provenance to be non-empty; this requires it to
    RESOLVE — the cited node file and research memo must exist on disk, which is
    what makes it a trace rather than a placeholder string."""
    for row in rows:
        cites = {c.split(":", 1)[0]: c.split(":", 1)[1]
                 for c in row.provenance if ":" in c}
        assert (NODES / f"{cites['row']}.json").is_file(), row.applicability_id
        assert (REPO / cites["memo"]).is_file(), row.applicability_id
        assert any("60-VOCABULARY-RULINGS.md" in c for c in row.provenance)
        assert any("51-LAUNCH-TEMPLATE-DRAFT.md" in c for c in row.provenance)
        assert any("53-HUMAN-SENSE-CHECK.md" in c for c in row.provenance)
    assert len({row.provenance[0] for row in rows}) == 54, (
        "one node row, one applicability row: a second row on one node id would "
        "offer two recipes for one situation and nothing records which is meant")


def test_detection_signals_are_references_and_never_patterns(rows):
    """`51` §5: they point at the node's own `recognition` block, and §9.5: *"R2
    owns the regexes and gazetteers. No pattern is written here."*"""
    for row in rows:
        assert len(row.detection_signal_refs) == 1
        ref = row.detection_signal_refs[0]
        assert ref.startswith("recognition:")
        node = json.loads(
            (NODES / f"{ref.removeprefix('recognition:')}.json").read_text())
        assert node["recognition"]["deterministic"]
        assert node["refuse_node"] is False


def test_rows_for_schema_returns_that_schemas_rows_and_no_others(catalogue):
    assert len(catalogue.rows_for_schema("law_practice")) == 26
    assert len(catalogue.rows_for_schema("creative")) == 28
    assert catalogue.rows_for_schema("clinical_practice") == ()


# --------------------------------------------------------------------------
# `law_practice` binds no client, and that is the family's own ruling.
# --------------------------------------------------------------------------

def test_law_practice_never_makes_the_client_a_folder_level(catalogue, rows):
    """`60` §5 makes `client` destination-ELIGIBLE on `law_practice`, and
    eligibility is a permission rather than an obligation. `law_practice.json`
    seeds the LEVEL ineligible — *"in a single-client corpus it is 'use an author
    or organization merely as a collector' and would 'create meaningless
    one-child levels', and in any corpus it is a disclosure"* — and no record
    shape here can express *"ineligible until the user explicitly approves it"*,
    because a bound optional role is an OFFERED level.

    Every one of `law_practice`'s 26 rows either inherits that or hardens it:
    `criminal-defence` makes it *"INELIGIBLE OUTRIGHT AND NOT UNLOCKABLE"*,
    `family-law` *"INELIGIBLE FULL STOP"*, `estates-administration` strikes it,
    and `transactional-deal` replaces it with a codename that *"names nobody"*.
    So `client` stays a searchable fact and reaches no dimension.
    """
    assert "client" in DOMAIN_FIELDS["law_practice"]
    law = [row for row in rows if row.uses_schema == "law_practice"]
    assert law, "no law_practice rows loaded, so this proves nothing"
    assert "client" not in {f for row in law for f in row.allowed_fields}
    assert "client" not in {b.field_ref for row in law for b in row.role_bindings}
    for record in catalogue.definitions.values():
        if DEFINITIONS[record.template_id][0] != "law_practice":
            continue
        assert "client_org" not in {d.role_ref for o in record.candidate_orders
                                    for d in o.dimensions}, record.template_id


def test_the_law_family_never_levels_on_a_non_destination_key(rows):
    """`our_firm` and `subject_of_record` are non-destination ON THE KEY (`60`
    §4, §9.1). `our_firm` is the practitioner half of the pair and exists *"in
    order to be read, not in order to be written into a path"*; a folder bearing
    a `subject_of_record` *"discloses membership of a matter, personnel, grant or
    clinical file."*"""
    everything = {f for row in rows for f in row.allowed_fields} | \
        {b.field_ref for row in rows for b in row.role_bindings}
    assert "our_firm" not in everything
    assert "subject_of_record" not in everything


# --------------------------------------------------------------------------
# `clinical_practice`: no folder proposal, protected disposition only.
# --------------------------------------------------------------------------

def test_clinical_practice_ships_no_template_and_the_field_catalogue_says_why(
        rows):
    """The whole schema refuses, and the refusal is DERIVED here rather than
    asserted: `clinical_practice` declares exactly one field and that field is
    non-destination, so under `PR-6` — a dimension may only branch on a field the
    schema declares — there is no dimension it could legally take.

    `60` §2 / J-5a rules it a PROTECTION schema and exempts it by name from
    `00`:48's three-to-six floor: *"A schema whose job is to keep a grievance
    file out of a named folder has fewer destination-eligible keys by design…
    The same reasoning covers `clinical_practice` at one."*
    """
    declared = DOMAIN_FIELDS["clinical_practice"]
    assert declared == ("subject_of_record",)
    eligible = {row.field_key for row in FIELD_ROWS if row.destination_eligible}
    assert not set(declared) & eligible, (
        "clinical_practice has acquired a destination-eligible field; the "
        "refusal in this file was argued from its NOT having one and must be "
        "re-argued rather than left standing")
    assert [row.applicability_id for row in rows
            if row.uses_schema == "clinical_practice"] == []


def test_no_clinical_practice_template_could_produce_a_level_naming_a_person():
    """The negative twin, so the assertion above is not vacuous.

    A `clinical_practice` row is hand-built here exactly as one would have to be
    — its only declarable field is `subject_of_record`, which is a PERSON — and
    the same eligibility check every real row in this file passes must reject it.
    That check is what stands between the product and the folder
    `clinical_practice.patient-chart` describes: *"a folder named for a patient
    publishes a third person's identity and the fact of their care in the
    filesystem namespace — for someone who is not the user, did not choose this
    product, and cannot review or correct it."*
    """
    invented = {
        "applicability_id": "ap.clinical_practice.patient-chart",
        "applicability_version": 1,
        "template_id": "def.matter-file",
        "template_version": 1,
        "uses_schema": "clinical_practice",
        "purpose_profile_ref": None,
        "allowed_fields": ["subject_of_record"],
        "detection_signal_refs": ["recognition:clinical_practice.patient-chart"],
        "role_bindings": [{"role_ref": "subject_anchor",
                           "field_ref": "subject_of_record",
                           "label": "Patient"}],
        "exclusions": [],
        "provenance": ["row:clinical_practice.patient-chart"],
        "privacy_floor": None,
    }
    # The RECORD accepts it — nothing in `TemplateApplicability` knows what a
    # person is — which is precisely why the check below is the one that matters
    # and why it is run over the shipped rows too.
    row = _catalogue(applicabilities=[invented]).applicabilities[
        ("ap.clinical_practice.patient-chart", 1)]
    assert row.role_bindings[0].field_ref == "subject_of_record"

    eligible = {r.field_key for r in FIELD_ROWS if r.destination_eligible}
    declared = DOMAIN_FIELDS[row.uses_schema]
    offending = [b.field_ref for b in row.role_bindings
                 if b.field_ref not in eligible or b.field_ref not in declared]
    assert offending == ["subject_of_record"], (
        "the check that refuses a person-named level has stopped refusing one")


# --------------------------------------------------------------------------
# The refusals. An honest gap is a deliverable; a silent one is a defect.
# --------------------------------------------------------------------------

def test_the_refused_rows_carry_no_template_and_are_the_named_six(rows):
    """44 of the 358 research rows earned a refusal, and these six earn one for
    the same reason: the level each row actually recommends maps to no key its
    schema declares, and each row states in its own words that the family default
    is NOT its recommendation. Filing them on the family recipe would ship a
    recipe nobody argued for."""
    covered = {c.removeprefix("row:") for row in rows for c in row.provenance
               if c.startswith("row:")}
    assert covered.isdisjoint(REFUSED_WITH_REASON)
    for node_id, sentence in sorted(REFUSED_WITH_REASON.items()):
        node = json.loads((NODES / f"{node_id}.json").read_text())
        assert node["refuse_node"] is False, (
            f"{node_id} is refused a TEMPLATE by this wave, not refused as a "
            "node; if the roster later refuses the node the reason here is "
            "redundant and should be removed rather than doubled")
        prose = node["template"]["why"] + " " + (node.get("open_question") or "")
        assert sentence in prose, (
            f"{node_id}'s refusal must quote the row that justified it; a "
            "refusal nobody can trace is indistinguishable from an omission")


def test_every_kept_node_row_in_these_families_is_covered_or_refused(rows):
    """The coverage arithmetic, computed from the node files rather than
    transcribed. A row that is neither templated nor named as a refusal is the
    silent gap this whole wave exists to close."""
    covered = {c.removeprefix("row:") for row in rows for c in row.provenance
               if c.startswith("row:")}
    for schema in ("law_practice", "creative"):
        kept = set()
        for path in NODES.glob(f"{schema}.*.json"):
            node = json.loads(path.read_text())
            if node["kind"] == "template" and not node["refuse_node"]:
                kept.add(node["id"])
        unaccounted = kept - covered - set(REFUSED_WITH_REASON)
        assert unaccounted == set(), (schema, sorted(unaccounted))
        assert covered & kept, schema

    clinical = {json.loads(p.read_text())["id"] for p in
                NODES.glob("clinical_practice.*.json")
                if json.loads(p.read_text())["kind"] == "template"
                and not json.loads(p.read_text())["refuse_node"]}
    assert clinical, "clinical_practice has no kept rows, so its refusal is moot"
    assert covered.isdisjoint(clinical)


def test_no_row_is_written_for_a_schema_anchor(rows):
    """An anchor is the schema speaking for itself, not a situation a file lands
    in. The shipped 54 hold no anchor row and neither does this wave."""
    covered = {c.removeprefix("row:") for row in rows for c in row.provenance
               if c.startswith("row:")}
    assert covered.isdisjoint({"law_practice", "creative", "clinical_practice"})


# --------------------------------------------------------------------------
# Exclusions: the levels these families refuse, kept where a reviewer sees them.
# --------------------------------------------------------------------------

def test_every_row_that_suppresses_a_level_says_which_and_why(rows):
    """`exclusions` is where a row records a level it will NOT propose, and it is
    load-bearing in these two families: almost every departure the corpora record
    is a subtraction. A row with no exclusion is a row that inherited its
    family's recipe unchanged, and there should be very few of them."""
    without = [row.applicability_id for row in rows if not row.exclusions]
    assert without == [], without
    for row in rows:
        for exclusion in row.exclusions:
            assert len(exclusion) > 40, (row.applicability_id, exclusion)
