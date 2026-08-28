"""The launch template definitions, driven through the real loader and merge.

`51-LAUNCH-TEMPLATE-DRAFT.md` §4 ratifies 29 definitions across families A–G
(§4.1–§4.7) and drafts a thirtieth for career (§4.8). This file asserts the
shipped `src/tree_design/library/definitions.json` IS that set.

The half that discriminates a correct library from an empty one is below the id
list: every refusal here is mutated from a REAL shipped record and raised by the
real callee, so a test that only proved good input loads cannot pass by accident.

Three things `51` settles that this file freezes:

1. **Career is the only definition with no fragment**, because §3.3's carrier
   table has no career entry. It is therefore the only one that must state its own
   `privacy_floor` (there is no fragment floor to take a maximum of) and the only
   one whose roles are all definition-local, so it is the only one that authors
   `relative_order`.
2. **The two-order floor is never exited.** `51` ships exactly three single-order
   recipes and all three are SINGLE-ROLE, so the floor does not apply to them and
   no `sole_order_attestation` is authored anywhere in the launch set.
3. **The default order is the order the fragments derive** (§3.4's closing rule),
   with one recorded exception named in the test that checks it.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tree_design.catalogue import load_catalogue
from tree_design.templates import (
    CompositionConflict,
    MalformedTemplateRecord,
    merge_fragment_constraints,
)

LIBRARY = Path(__file__).resolve().parents[2] / "src" / "tree_design" / "library"
DEFINITIONS_JSON = LIBRARY / "definitions.json"
FRAGMENTS_JSON = LIBRARY / "fragments.json"

#: `51`'s appendix writes the placeholder floor symbol `baseline` and assigns no
#: handling class; P7 injects the real vocabulary per deployment.
RANK = {"baseline": 0, "protected": 1}.__getitem__

HOLDER_OWN = "sp.holder-own-record@1"
THIRD_PARTY = "sp.third-party-confidential@1"
HOUSEHOLD = "sp.household-member-record@1"
NOT_PERSONAL = "sp.not-holder-personal@1"
SAFETY = "sp.safety-domain-protected@1"
CREDENTIAL = "sp.credential-bearing@1"
WHOLE_DOC = "sp.document-reproduced-whole@1"

#: `51` §4, definition by definition: the draft's own D-number, the scope it
#: declares, and the policy ref its heading carries. §4.7's three research
#: definitions state no ref in their headings; `sp.holder-own-record@1` is forced
#: by §4.0's own tally, which assigns that ref exactly 22 rows and reaches 22 only
#: with D27, D28 and D29 counted in.
LAUNCH_SET = {
    # §4.1 Family A — subject then kind (academic + research + code)
    "def.subject-work-record": ("D01", "cross-domain", HOLDER_OWN),
    "def.subject-work-record.third-party": ("D02", "cross-domain", THIRD_PARTY),
    "def.subject-work-record.household": ("D03", "domain-focused", HOUSEHOLD),
    "def.reading-shelf": ("D04", "domain-focused", NOT_PERSONAL),
    # §4.2 Family B — an institution-issued record with no subject
    "def.institution-issued-record": ("D05", "domain-focused", HOLDER_OWN),
    "def.household-school-record": ("D06", "domain-focused", HOUSEHOLD),
    "def.evaluative-letters": ("D07", "domain-focused", THIRD_PARTY),
    "def.protected-plan-record": ("D08", "domain-focused", HOUSEHOLD),
    # §4.3 Family C — code
    "def.preserved-root": ("D09", "domain-focused", HOLDER_OWN),
    "def.container-artifact": ("D10", "domain-focused", CREDENTIAL),
    # §4.4 Family D — college applications
    "def.addressee-packet": ("D11", "domain-focused", HOLDER_OWN),
    "def.addressee-packet.household": ("D12", "domain-focused", HOUSEHOLD),
    "def.purpose-packet": ("D13", "purpose-focused", HOLDER_OWN),
    # §4.5 Family E — finance, all `sp.safety-domain-protected@1`
    "def.issuer-record": ("D14", "domain-focused", SAFETY),
    "def.issuer-period-record": ("D15", "domain-focused", SAFETY),
    "def.period-scoped-filing": ("D16", "domain-focused", SAFETY),
    "def.loan-kind-record": ("D17", "domain-focused", SAFETY),
    "def.function-first-book": ("D18", "domain-focused", SAFETY),
    "def.function-then-issuer": ("D19", "domain-focused", SAFETY),
    "def.group-scoped-record": ("D20", "domain-focused", SAFETY),
    # §4.6 Family F — photos
    "def.capture-time-events": ("D21", "domain-focused", HOLDER_OWN),
    "def.capture-time-events.third-party": ("D22", "domain-focused", THIRD_PARTY),
    "def.capture-kind-led": ("D23", "domain-focused", HOLDER_OWN),
    "def.capture-kind-led.document": ("D24", "domain-focused", WHOLE_DOC),
    "def.occasion-place": ("D25", "domain-focused", HOLDER_OWN),
    # §4.7 Family G — research beyond Family A
    "def.research-lineage": ("D26", "domain-focused", HOLDER_OWN),
    "def.research-workflow-split": ("D27", "domain-focused", HOLDER_OWN),
    "def.submission-to-venue": ("D28", "domain-focused", HOLDER_OWN),
    "def.venue-bundle": ("D29", "domain-focused", HOLDER_OWN),
    # §4.8 career — the thirtieth, which `51` states is "not counted in the 29"
    # because career declared no field. `60` J-3 declares six, so it ships.
    "def.career-search-and-tenure": ("D30", "domain-focused", HOLDER_OWN),
}

#: `51` §4 gives the default candidate order of every definition an id. A
#: recommendation nobody can name is a recommendation the branch binding cannot
#: record, so the ids are part of the transcription and not decoration.
DEFAULT_ORDER_IDS = {
    "def.subject-work-record": "ord.affiliation-period-subject-kind",
    "def.subject-work-record.third-party": "ord.affiliation-period-subject-kind",
    "def.subject-work-record.household": "ord.affiliation-period-subject-kind",
    "def.reading-shelf": "ord.project-then-kind",
    "def.institution-issued-record": "ord.issuer-period-kind",
    "def.household-school-record": "ord.school-year-kind",
    "def.evaluative-letters": "ord.cycle-then-kind",
    "def.protected-plan-record": "ord.school-then-year",
    "def.preserved-root": "ord.project-only",
    "def.container-artifact": "ord.collection-then-kind",
    "def.addressee-packet": "ord.addressee-cycle-kind",
    "def.addressee-packet.household": "ord.addressee-cycle-kind",
    "def.purpose-packet": "ord.purpose-only",
    "def.issuer-record": "ord.issuer-account-kind",
    "def.issuer-period-record": "ord.issuer-year-kind",
    "def.period-scoped-filing": "ord.year-kind-issuer",
    "def.loan-kind-record": "ord.loan-kind-issuer-record",
    "def.function-first-book": "ord.function-then-account",
    "def.function-then-issuer": "ord.function-then-issuer",
    "def.group-scoped-record": "ord.kind-only",
    "def.capture-time-events": "ord.year-then-event",
    "def.capture-time-events.third-party": "ord.year-event-kind",
    "def.capture-kind-led": "ord.kind-then-year",
    "def.capture-kind-led.document": "ord.kind-then-year",
    "def.occasion-place": "ord.trip-place-year",
    "def.research-lineage": "ord.project-kind-stage",
    "def.research-workflow-split": "ord.project-then-stage",
    "def.submission-to-venue": "ord.project-venue-stage",
    "def.venue-bundle": "ord.venue-project-kind",
    "def.career-search-and-tenure": "ord.employer-role-cycle-kind",
}

#: `51` §4.9. Ten definitions whose corpus attests exactly one order, so the
#: second was AUTHORED. They are listed here because §4.9 makes them a cost the
#: owner is asked to see, not a detail: an authored alternative is offered to a
#: user with a rationale nobody argued from a real corpus.
AUTHORED_ALTERNATIVE = (
    "def.subject-work-record.household",     # D03
    "def.institution-issued-record",         # D05
    "def.household-school-record",           # D06
    "def.protected-plan-record",             # D08
    "def.container-artifact",                # D10
    "def.addressee-packet.household",        # D12
    "def.issuer-period-record",              # D15
    "def.loan-kind-record",                  # D17
    "def.function-first-book",               # D18
    "def.research-workflow-split",           # D27
)

#: `51` §4.3, §4.4 and §4.5: the only three recipes that ship one candidate order.
SINGLE_ORDER = (
    "def.preserved-root",       # D09, role: subject_anchor
    "def.purpose-packet",       # D13, role: purpose_anchor
    "def.group-scoped-record",  # D20, role: artifact_kind
)


def _raw_definitions() -> list[dict]:
    payload = json.loads(DEFINITIONS_JSON.read_text())
    assert set(payload) == {"definitions"}, (
        "a later step merges three files into one manifest; this one carries "
        "definitions and nothing else")
    return payload["definitions"]


def _raw_fragments() -> list[dict]:
    return json.loads(FRAGMENTS_JSON.read_text())["fragments"]


def _catalogue(definitions=None, fragments=None):
    """The REAL loader, over a minimal one-release manifest.

    A hand-built `TemplateCatalogue` would prove the ids were typed correctly and
    nothing else. Everything that refuses a malformed definition lives in
    `TemplateDefinition.__post_init__`, which only runs on this path.
    """
    manifest = {
        "release_id": "rel-launch-test",
        "fragments": _raw_fragments() if fragments is None else fragments,
        "definitions": _raw_definitions() if definitions is None else definitions,
        "applicabilities": [],
    }
    return load_catalogue(lambda: json.dumps(manifest))


def _shipped(template_id: str) -> dict:
    return copy.deepcopy(
        next(d for d in _raw_definitions() if d["template_id"] == template_id))


# --- the launch set is present, and it is `51`'s -------------------------------

def test_the_launch_definitions_load_through_the_real_loader():
    catalogue = _catalogue()
    assert catalogue.release_id == "rel-launch-test"
    loaded = {template_id for template_id, _ in catalogue.definitions}
    assert loaded == set(LAUNCH_SET), (
        "the shipped library is not `51` §4's set: "
        f"missing {sorted(set(LAUNCH_SET) - loaded)}, "
        f"unexpected {sorted(loaded - set(LAUNCH_SET))}")
    assert len(catalogue.definitions) == 30


def test_every_definition_declares_the_scope_and_policy_ref_51_states():
    catalogue = _catalogue()
    for template_id, (number, scope, policy) in sorted(LAUNCH_SET.items()):
        record = catalogue.definitions[(template_id, 1)]
        assert record.scope_kind == scope, f"{number} {template_id}"
        assert record.sensitivity_policy_ref == policy, f"{number} {template_id}"
        assert record.origin_kind == "built-in", f"{number} {template_id}"


def test_the_policy_refs_are_the_seven_51_s_four_point_zero_table_names():
    """§4.0 names seven `sp.*@1` refs and no others.

    Nothing in the codebase reads `sensitivity_policy_ref` — it is a required
    column with no reader. That is exactly why the SET is asserted here: an
    unread column is the one place a typo survives every other test.
    """
    catalogue = _catalogue()
    assert {d.sensitivity_policy_ref for d in catalogue.definitions.values()} == {
        HOLDER_OWN, SAFETY, THIRD_PARTY, HOUSEHOLD, NOT_PERSONAL, CREDENTIAL,
        WHOLE_DOC,
    }


def test_the_finance_family_is_protected_as_a_whole():
    """§4.5: all 18 finance rows sit under `sp.safety-domain-protected@1`."""
    catalogue = _catalogue()
    finance = [
        "def.issuer-record", "def.issuer-period-record", "def.period-scoped-filing",
        "def.loan-kind-record", "def.function-first-book",
        "def.function-then-issuer", "def.group-scoped-record",
    ]
    for template_id in finance:
        assert catalogue.definitions[(template_id, 1)].sensitivity_policy_ref == SAFETY


def test_every_definition_names_the_default_order_51_marks_with_a_star():
    catalogue = _catalogue()
    for template_id, order_id in sorted(DEFAULT_ORDER_IDS.items()):
        record = catalogue.definitions[(template_id, 1)]
        assert record.default_order.order_id == order_id, template_id
        assert sum(o.is_default for o in record.candidate_orders) == 1, template_id


def test_every_fragment_ref_resolves_in_the_shipped_fragment_library():
    """A definition pins EXACT fragment versions, so a ref that resolves to
    nothing is a recipe that cannot be composed at all — and the failure would
    otherwise surface at placement time, far from the record that caused it."""
    catalogue = _catalogue()
    dangling = [
        (record.template_id, ref.fragment_id, ref.fragment_version)
        for record in catalogue.definitions.values()
        for ref in record.fragment_refs
        if not catalogue.has_fragment(ref.fragment_id, ref.fragment_version)
    ]
    assert dangling == []


def test_ten_definitions_carry_an_authored_second_order():
    """§4.9's list, frozen. It is a cost the owner is asked to accept knowingly
    (Judgment Call 3), so it must not be able to grow without this test failing."""
    catalogue = _catalogue()
    for template_id in AUTHORED_ALTERNATIVE:
        record = catalogue.definitions[(template_id, 1)]
        assert len(record.candidate_orders) == 2, template_id
        alternative = next(o for o in record.candidate_orders if not o.is_default)
        assert "AUTHORED" in alternative.rationale, (
            f"{template_id}'s second order is one of §4.9's ten and must say so "
            "in its own rationale; an authored alternative shown beside a real "
            "one is worse than none when the user cannot tell which is which")


# --- the two-order floor, and the exit it does not use -------------------------

def test_only_single_role_recipes_ship_a_single_candidate_order():
    """`51` ships three, and all three nest ONE role, so the floor never applies
    and nothing in the launch set needs `sole_order_attestation`."""
    catalogue = _catalogue()
    single = sorted(
        record.template_id for record in catalogue.definitions.values()
        if len(record.candidate_orders) == 1)
    assert single == sorted(SINGLE_ORDER)
    for template_id in SINGLE_ORDER:
        record = catalogue.definitions[(template_id, 1)]
        assert len(record.default_order.role_set()) == 1, template_id
        assert record.sole_order_attestation is None, template_id


def test_no_definition_in_the_launch_set_claims_the_attestation_exit():
    catalogue = _catalogue()
    assert [d.template_id for d in catalogue.definitions.values()
            if d.sole_order_attestation] == []


def test_a_shipped_recipe_stripped_to_one_order_is_refused():
    """The discriminating half. `def.addressee-packet` is `51`'s own example of a
    recipe whose two orders are both argued — two rows landed with opposite
    orders over the same three roles. Drop one and the record must refuse, or the
    library could ship a `dimensions` tuple wearing a new field name."""
    stripped = _shipped("def.addressee-packet")
    stripped["candidate_orders"] = [
        o for o in stripped["candidate_orders"] if o["is_default"]]
    assert len(stripped["candidate_orders"]) == 1

    with pytest.raises(MalformedTemplateRecord) as raised:
        _catalogue(definitions=[stripped])
    assert "at least two candidate orders" in str(raised.value)


def test_the_same_stripped_recipe_loads_once_it_attests_its_sole_order():
    """Amendment D's exit, on the same record. The difference between refusal and
    acceptance is a SENTENCE, which is the point: a flag records that somebody
    wanted the exception and a sentence records why anyone should believe it."""
    stripped = _shipped("def.addressee-packet")
    stripped["candidate_orders"] = [
        o for o in stripped["candidate_orders"] if o["is_default"]]
    stripped["sole_order_attestation"] = (
        "The applications corpora attest exactly one nesting for this recipe.")

    catalogue = _catalogue(definitions=[stripped])
    record = catalogue.definitions[("def.addressee-packet", 1)]
    assert len(record.candidate_orders) == 1
    assert record.sole_order_attestation


def test_a_blank_attestation_does_not_open_the_exit():
    stripped = _shipped("def.addressee-packet")
    stripped["candidate_orders"] = [
        o for o in stripped["candidate_orders"] if o["is_default"]]
    stripped["sole_order_attestation"] = "   "

    with pytest.raises(MalformedTemplateRecord):
        _catalogue(definitions=[stripped])


def test_an_attestation_beside_the_two_orders_a_recipe_actually_ships_is_refused():
    """The reverse contradiction: a record that attests one nesting and then
    offers two says one of the two things falsely and cannot tell which."""
    attested = _shipped("def.addressee-packet")
    attested["sole_order_attestation"] = (
        "The applications corpora attest exactly one nesting for this recipe.")

    with pytest.raises(MalformedTemplateRecord) as raised:
        _catalogue(definitions=[attested])
    assert "attests that only one order is supported" in str(raised.value)


# --- career: the one definition with no fragment -------------------------------

def test_career_is_the_only_definition_that_composes_no_fragment():
    """§3.3's carrier table has no career entry, and `51` §4.8 names no fragment
    for D30. Everything else in the launch set is fragment-backed."""
    catalogue = _catalogue()
    fragmentless = sorted(
        record.template_id for record in catalogue.definitions.values()
        if not record.fragment_refs)
    assert fragmentless == ["def.career-search-and-tenure"]


def test_career_states_its_own_privacy_floor_because_nothing_else_can():
    catalogue = _catalogue()
    career = catalogue.definitions[("def.career-search-and-tenure", 1)]
    assert career.privacy_floor == "baseline"
    assert [d.template_id for d in catalogue.definitions.values()
            if d.privacy_floor] == ["def.career-search-and-tenure"], (
        "a definition WITH fragments takes the strongest floor among them; a "
        "floor restated on the record is a copy for the fragments' to drift from")


def test_career_without_its_own_floor_is_refused():
    """C7 keeps the strongest floor among the included fragments. With no
    fragment AND no floor there is nothing to take a maximum of, so the record
    refuses rather than letting the composer fail far from the cause."""
    floorless = _shipped("def.career-search-and-tenure")
    floorless.pop("privacy_floor")

    with pytest.raises(MalformedTemplateRecord) as raised:
        _catalogue(definitions=[floorless])
    assert "composes no fragment and states no" in str(raised.value)


def test_career_authors_the_relative_order_its_definition_local_roles_need():
    """All four of career's roles are definition-local, so `51` §3.4(b) applies to
    every one of them: a role the merge never saw carries no ordering constraint.

    With the recipe's own edges the merge derives the authored nesting from
    nothing else. Without them — and with no tiebreak supplied — the merge
    refuses BY NAME rather than sorting four roles to the leaf with ties, which
    is the failure the amendment removed.
    """
    catalogue = _catalogue()
    career = catalogue.definitions[("def.career-search-and-tenure", 1)]
    recommended = tuple(
        d.role_ref for d in sorted(career.default_order.dimensions,
                                   key=lambda d: d.order_index))
    assert career.relative_order == (
        ("employer_org", "role_title"),
        ("role_title", "cycle_period"),
        ("cycle_period", "artifact_kind"),
    )
    merged = merge_fragment_constraints([], privacy_rank=RANK, definition=career)
    assert merged.ordered_roles == recommended
    assert merged.privacy_floor == "baseline"

    unpinned = _shipped("def.career-search-and-tenure")
    unpinned.pop("relative_order")
    loose = _catalogue(definitions=[unpinned]).definitions[
        ("def.career-search-and-tenure", 1)]
    assert loose.relative_order == ()
    with pytest.raises(CompositionConflict) as raised:
        merge_fragment_constraints([], privacy_rank=RANK, definition=loose)
    assert "unordered relative to each other" in str(raised.value)


def test_career_defaults_to_the_order_that_fails_legibly():
    """`51` §4.8 left D30's default deliberately unset, deferring to another lane;
    the record refuses an unset default, so `60` §8.3 rules it.

    The ruling is `employer_org` first, and the reason is DEGRADATION rather than
    preference — which is why it is asserted here rather than left to the field
    value alone. Employer-first applied to a job-seeker yields many small folders
    and `00` already handles that: the canvas warns about "a large number of tiny
    folders" and offers flatten. Cycle-first applied to someone with ten years at
    two employers asserts a recruiting cycle THAT DOES NOT EXIST — nothing to warn
    about and nothing to flatten, because the level is not wrong, it is empty. A
    default runs before the product knows who it is talking to, so it must be the
    one whose failure is legible.

    The record must also say the tie-break is not evidence it does not have.
    """
    catalogue = _catalogue()
    career = catalogue.definitions[("def.career-search-and-tenure", 1)]
    assert {o.order_id for o in career.candidate_orders} == {
        "ord.employer-role-cycle-kind", "ord.cycle-kind-employer-role"}
    assert career.default_order.order_id == "ord.employer-role-cycle-kind"
    assert "RECOMMENDATION-PENDING" in career.default_order.rationale, (
        "60 §8.3 rules the default and rules it unratified in the same breath; a "
        "record carrying the choice without the caveat turns a tie-break into a "
        "finding")


def test_career_ships_published_because_j3_gave_it_fields_to_bind():
    """`51` §4.8 marks D30 "DRAFTED, NOT BINDABLE" for one reason — career
    declared no field. `60` J-3 declares six and §8.1 makes `job_title`
    destination-eligible, so `role_title` binds a real level and both halves of
    that reason are gone. §8.2: D30 ships, because J-3 is meaningless if career
    cannot produce a folder.

    A `draft` state would mean the opposite: a saved definition that is NOT
    activated. Career has no applicability row yet, so nothing selects it — that
    is the honest brake, and it lives on the rows rather than on this record.
    """
    catalogue = _catalogue()
    assert [record.template_id for record in catalogue.definitions.values()
            if record.publication_state != "published"] == []


def test_career_binds_the_role_as_a_folder_level_because_00_does():
    """`60` §8.1 corrects §5's unsourced `job_title†`. `00`:70 puts the role in a
    template order in so many words — "a Career template may define company ->
    ROLE or recruiting cycle -> document type" — and a key `00` puts in a template
    order cannot be non-destination. So `role_title` is a DIMENSION here, in both
    candidate orders, and not a search fact."""
    catalogue = _catalogue()
    career = catalogue.definitions[("def.career-search-and-tenure", 1)]
    for candidate in career.candidate_orders:
        assert "role_title" in candidate.role_set(), candidate.order_id
    role = next(d for d in career.default_order.dimensions
                if d.role_ref == "role_title")
    assert role.order_index == 1, "00's own career order puts the role SECOND"
    assert not role.metadata_only
    assert not any("destination-ineligible" in constraint
                   for constraint in career.validation_constraints)


# --- the recipes compose, and compose into what they recommend -----------------

def test_every_definition_composes_through_the_real_merge():
    catalogue = _catalogue()
    for record in sorted(catalogue.definitions.values(),
                         key=lambda r: r.template_id):
        fragments = [catalogue.fragment(ref) for ref in record.fragment_refs]
        recommended = [d.role_ref for d in sorted(record.default_order.dimensions,
                                                  key=lambda d: d.order_index)]
        merged = merge_fragment_constraints(
            fragments, privacy_rank=RANK, preferred_order=recommended,
            definition=record)
        assert merged.privacy_floor == "baseline", record.template_id


def test_the_composer_derives_the_nesting_each_recipe_recommends():
    """`51` §3.4's closing rule: "for every definition, the default candidate
    order equals the order the fragments derive." A user who takes the default
    then needs no override.

    ONE definition departs, and it departs in `51` itself rather than here:
    `def.capture-time-events` (D21) nests two roles while the fragment it shares
    with D22 defines three, so the merge sees `capture_kind` and the recipe does
    not nest it. The extra role is optional on the fragment and appears last, so
    the recommended prefix survives intact — recorded rather than smoothed over.
    """
    catalogue = _catalogue()
    for record in sorted(catalogue.definitions.values(),
                         key=lambda r: r.template_id):
        fragments = [catalogue.fragment(ref) for ref in record.fragment_refs]
        recommended = [d.role_ref for d in sorted(record.default_order.dimensions,
                                                  key=lambda d: d.order_index)]
        merged = merge_fragment_constraints(
            fragments, privacy_rank=RANK, preferred_order=recommended,
            definition=record)
        if record.template_id == "def.capture-time-events":
            assert list(merged.ordered_roles) == [*recommended, "capture_kind"]
            continue
        assert list(merged.ordered_roles) == recommended, record.template_id


def test_family_as_default_order_is_what_orders_cycle_against_subject():
    """The Family-A recipes' own recommendation is load-bearing, not decoration.

    `frag.affiliation-prefix-to-cycle@1` ships `holder_institution ->
    cycle_period` and nothing else, so across D01/D02/D03's four fragments
    `cycle_period` and `subject_anchor` are unconstrained relative to each other.
    With no recommendation supplied the merge REFUSES them by name rather than
    letting Kahn's queue discipline pick — the fix `56` §4.2 found missing.

    Supply the recipe's default and it derives `00`'s Academic order exactly:
    school -> term -> course -> work type. Nobody wrote that order into a
    fragment; three independently-argued pairwise constraints plus the
    definition's own recommendation produce it (§3.4c).
    """
    catalogue = _catalogue()
    academic_order = ("holder_institution", "cycle_period", "subject_anchor",
                      "artifact_kind")
    for template_id in ("def.subject-work-record",
                       "def.subject-work-record.third-party",
                       "def.subject-work-record.household"):
        record = catalogue.definitions[(template_id, 1)]
        fragments = [catalogue.fragment(ref) for ref in record.fragment_refs]
        recommended = [d.role_ref for d in sorted(record.default_order.dimensions,
                                                  key=lambda d: d.order_index)]
        assert tuple(recommended) == academic_order, template_id

        with pytest.raises(CompositionConflict) as raised:
            merge_fragment_constraints(
                fragments, privacy_rank=RANK, definition=record)
        assert "cycle_period, subject_anchor unordered" in str(raised.value)

        merged = merge_fragment_constraints(
            fragments, privacy_rank=RANK, preferred_order=recommended,
            definition=record)
        assert merged.ordered_roles == academic_order, template_id


def test_no_example_label_chain_is_a_path():
    """Example chains are nested display labels used to review a recipe. P12
    alone composes paths, so a separator in one is a destination smuggled into a
    review artefact."""
    catalogue = _catalogue()
    chains = [chain for record in catalogue.definitions.values()
              for chain in record.example_label_chains]
    assert chains, "§4 and §7 publish worked chains; shipping none loses them"
    for chain in chains:
        for label in chain:
            assert "/" not in label and "\\" not in label
