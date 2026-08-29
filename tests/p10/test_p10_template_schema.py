"""P10 Task 8 — the strict Site-E response schema, and the fragment boundary.

P8 owns the harness: structured-output enforcement, the citation check, the
verdict. P10 owns what "the required template shape" MEANS, and hands P8 the
callable that decides it. Everything below is P10's half.

The load-bearing rule: a model proposal may reference a published fragment by
exact id and version, and may add template-LOCAL semantic dimensions, but it may
not publish or propose a new canonical fragment. Repeated local dimensions become
fragment candidates only in a later human-reviewed synthesis pass.

`planning/46-NOVEL-DOMAIN-HANDLING.md` supersedes `43 §9`, which asked for the
closure itself to be widened and was withdrawn as wrong: `allowed_vocabulary` is
one field on a `Dossier` shared by five call sites, so a role name added here
would be offered as a placement destination at Site C and a target node id at
Site D.

Contract W1 therefore keeps the closure EXACTLY as it was — one schema's
`allowed_fields`, never unioned, never extended. What changes is Contract W2:
Site E's gate stops being a rejection and becomes a CLASSIFIER. A name inside the
closure is a `schema-field`; a name outside it that is a live P6 field key is a
borrowed field and a REJECT; a name outside it that is no P6 field at all is
`template-local` — a display label with a semantic role and a citation, which is
how a group from an unresearched domain still gets a reviewable branch design.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from llm_harness.records import EvidenceItem
from tree_design.catalogue import load_catalogue
from tree_design.template_schema import (
    FORBIDDEN_PUBLISHING_KEYS,
    TEMPLATE_PAYLOAD_KEYS,
    allowed_vocabulary_for,
    build_template_request,
    published_fragment_authority,
    template_dependencies,
    template_schema_validator,
)
from tree_design.templates import RoleBinding, TemplateApplicability, TemplateFragment

PUBLISHED_FRAGMENT = TemplateFragment(
    fragment_id="event-capture-time", fragment_version=1,
    roles=("event", "capture_time"),
    relative_order=(("event", "capture_time"),), imports=(),
    optional_roles=(), metadata_only_roles=(), allowed_values={},
    privacy_floor="policy.public", provenance=("row:photos-01",),
)
ROW = TemplateApplicability(
    applicability_id="photos--photos", applicability_version=1,
    template_id="photo-event", template_version=1, uses_schema="photos",
    purpose_profile_ref=None, allowed_fields=("event", "capture_year"),
    detection_signal_refs=("signal.exif",),
    role_bindings=(RoleBinding("event", "event", "Occasion"),
                   RoleBinding("capture_time", "capture_year", "Year taken")),
    exclusions=(), provenance=("row:photos-01",),
)
CATALOGUE = load_catalogue(lambda: json.dumps({
    "release_id": "rel-1",
    "fragments": [dataclasses.asdict(PUBLISHED_FRAGMENT)],
    "definitions": [],
    "applicabilities": [dataclasses.asdict(ROW)],
}))


def _evidence(ref: str = "obs-1") -> EvidenceItem:
    return EvidenceItem(
        evidence_ref=ref, kind="excerpt", location="body",
        excerpt_span=(0, 8), reliability_state="validated", basis="direct-anchor",
    )


def _payload(**overrides) -> dict:
    payload = {
        "domain": "photos",
        "allowed_fields": ["event", "capture_year"],
        "fragment_refs": [
            {"fragment_id": "event-capture-time", "fragment_version": 1}],
        "dimensions": [
            {"name": "event", "evidence_ref": "obs-1", "requirement": "required",
             "metadata_only": False, "order_index": 0, "scope": "schema-field"},
            {"name": "capture_year", "evidence_ref": "obs-1",
             "requirement": "optional", "metadata_only": False, "order_index": 1,
             "scope": "schema-field"},
        ],
        "levels": [
            {"dimension": "event",
             "retrieval_justification": "Users look for a trip, not a date."},
            {"dimension": "capture_year",
             "retrieval_justification": "Capture date defines this material."},
        ],
        "sensitivity_policy_ref": "policy.public",
        "example_label_chains": [["Photos", "Iceland 2026"]],
    }
    payload.update(overrides)
    return payload


def test_a_well_formed_proposal_referencing_a_published_fragment_passes():
    validator = template_schema_validator(CATALOGUE)
    assert validator(_payload()) is True


def test_a_proposal_naming_an_unpublished_fragment_is_refused_by_the_authority():
    """NOT by `schema_validator`. `planning/33-P8-COMPLETION-AUDIT.md:116-120`
    asked for a published-fragment AUTHORITY on `TemplateDependencies`, so that a
    caller who supplies no authority gets `ValidationUnavailable` instead of
    silence. A check folded into the schema validator can only be silent, and it
    would report `SCHEMA_INVALID` for a defect that is not a shape defect."""
    published = published_fragment_authority(CATALOGUE)
    assert published("event-capture-time", 1) is True
    assert published("counterpart-cycle", 1) is False


def test_the_authority_matches_the_exact_version_and_not_just_the_id():
    """"Exact id AND exact version" is the whole point: version 2 of a fragment
    is a different recipe, and accepting it because the id is familiar would let
    a model activate logic nobody reviewed."""
    published = published_fragment_authority(CATALOGUE)
    assert published("event-capture-time", 2) is False
    assert published("", 1) is False


def test_the_schema_validator_no_longer_decides_the_fragment_question():
    """The separation, asserted rather than assumed. A payload whose SHAPE is
    legal but whose fragment reference is unpublished passes the schema and
    fails the authority — two defects, two reason codes at P8
    (`SCHEMA_INVALID` versus `FRAGMENT_NOT_PUBLISHED`), which is the pair Site C
    already keeps apart as `INVENTED_NODE` versus `NODE_NOT_IN_FROZEN_TREE`."""
    validator = template_schema_validator(CATALOGUE)
    published = published_fragment_authority(CATALOGUE)
    payload = _payload(fragment_refs=[
        {"fragment_id": "counterpart-cycle", "fragment_version": 1}])
    assert validator(payload) is True
    assert published("counterpart-cycle", 1) is False


def test_a_payload_publishing_a_fragment_carries_a_forbidden_key():
    """P8 scans the response for these and returns
    `FRAGMENT_PUBLICATION_ATTEMPTED`. P10 does not read a model response, so the
    scan is not P10's; the list lives beside the reason code that reports it and
    P10 IMPORTS it, the same way it imports every other P8 vocabulary. What P10
    asserts here is the invariant that makes the list correct: no forbidden key
    is also a legal payload key."""
    assert "fragment_definitions" in FORBIDDEN_PUBLISHING_KEYS
    for key in FORBIDDEN_PUBLISHING_KEYS:
        assert key not in TEMPLATE_PAYLOAD_KEYS


def test_template_local_dimensions_are_allowed_and_are_not_fragments():
    """A local dimension is the model saying "this branch also splits by lens".
    That is a proposal about ONE branch. It becomes a canonical fragment only in
    the later human-reviewed synthesis pass, never here."""
    validator = template_schema_validator(CATALOGUE)
    payload = _payload()
    payload["dimensions"].append({
        "name": "lens", "evidence_ref": "obs-1", "requirement": "optional",
        "metadata_only": True, "order_index": 2, "scope": "template-local",
    })
    payload["levels"].append({
        "dimension": "lens",
        "retrieval_justification": "Two shoots differ only by lens.",
    })
    payload["allowed_fields"].append("lens")
    assert validator(payload) is True


def test_a_payload_missing_any_required_key_is_rejected():
    validator = template_schema_validator(CATALOGUE)
    for key in TEMPLATE_PAYLOAD_KEYS:
        payload = _payload()
        del payload[key]
        assert validator(payload) is False, key


def test_a_dimension_that_is_not_in_allowed_fields_is_rejected():
    """E2: the payload must be internally consistent — every dimension it
    proposes must appear in the `allowed_fields` it declared. This is NOT the
    dossier closure and NOT the minting check; minting a field belonging to
    another schema is caught by Contract W3's borrowed-field guard."""
    validator = template_schema_validator(CATALOGUE)
    payload = _payload()
    payload["dimensions"][0]["name"] = "mood"
    assert validator(payload) is False


def test_a_list_of_domains_is_rejected_because_a_model_may_not_create_one():
    """§5.7: a generated template may not "silently create new high-level
    domains". One proposal, one schema context."""
    validator = template_schema_validator(CATALOGUE)
    assert validator(_payload(domain=["photos", "travel"])) is False
    assert validator(_payload(domain="")) is False


def test_an_example_label_chain_holding_a_separator_is_rejected():
    validator = template_schema_validator(CATALOGUE)
    assert validator(_payload(
        example_label_chains=[["Photos/Iceland 2026"]])) is False


def test_two_dimensions_claiming_one_order_index_are_rejected():
    validator = template_schema_validator(CATALOGUE)
    payload = _payload()
    payload["dimensions"][1]["order_index"] = 0
    assert validator(payload) is False


def test_a_non_mapping_payload_is_rejected_without_raising():
    validator = template_schema_validator(CATALOGUE)
    for value in (None, [], "dimensions", 0):
        assert validator(value) is False


def test_a_malformed_fragment_reference_is_still_a_shape_defect():
    """The AUTHORITY answers "does this fragment exist". Whether `fragment_refs`
    is a list of `{id, version}` objects at all is a shape question, so it stays
    with the schema validator — otherwise a string where a mapping belongs would
    reach the authority and raise instead of returning a verdict."""
    validator = template_schema_validator(CATALOGUE)
    assert validator(_payload(fragment_refs="event-capture-time")) is False
    assert validator(_payload(fragment_refs=[{"fragment_id": "x"}])) is False
    assert validator(_payload(fragment_refs=[
        {"fragment_id": "x", "fragment_version": "1"}])) is False


def test_dependencies_are_p8s_record_with_both_of_p10s_authorities():
    """`TemplateDependencies` gains a second field, and P10 fills both. A
    dependencies object carrying only `schema_validator` is what
    `validate_template_response` must report as
    `ValidationUnavailable(missing=("published_fragment",))` — the same way it
    already reports a missing `schema_validator`.
    """
    from llm_harness.template_validation import TemplateDependencies

    deps = template_dependencies(CATALOGUE)
    assert isinstance(deps, TemplateDependencies)
    assert deps.schema_validator(_payload()) is True
    assert deps.published_fragment("event-capture-time", 1) is True
    assert deps.published_fragment("counterpart-cycle", 1) is False


# --- Contract W1/W2/W3: the classifier, not a wider closure --------------------


def test_the_allowed_vocabulary_is_the_rows_fields_and_nothing_wider():
    """P8's Site E CLASSIFIES each dimension by whether its `name` is inside
    `Dossier.allowed_vocabulary` (Contract W2). P10 populates that closure, so a
    union across schemas here would widen a P6 allow-list at the dossier
    boundary — and worse, `allowed_vocabulary` is one field on a `Dossier`
    shared by five call sites, so anything added here is also offered as a
    placement destination at Site C and a target node id at Site D."""
    assert allowed_vocabulary_for(CATALOGUE, uses_schema="photos") == (
        "capture_year", "event")
    assert allowed_vocabulary_for(CATALOGUE, uses_schema="academic") == ()


def test_the_closure_takes_no_widening_argument_at_all():
    """43 §9 asked for template-local names to be added to the closure. That is
    withdrawn (Contract W1), and the refusal is structural: there is no parameter
    through which a caller could widen it."""
    import inspect

    parameters = set(inspect.signature(allowed_vocabulary_for).parameters)
    assert parameters == {"catalogue", "uses_schema"}


def test_a_schema_with_no_declared_fields_still_admits_a_template_local_dimension():
    """The companion to the closure test, and the owner's ruling stated as a
    check: a field-less schema must still produce a reviewable branch design.

    The closure is empty and stays empty. What makes the branch designable is
    that a name outside it is no longer a rejection — it is a `template-local`
    label, carrying a semantic role and a citation and nothing P6 has to define.
    """
    assert allowed_vocabulary_for(CATALOGUE, uses_schema="academic") == ()
    validator = template_schema_validator(CATALOGUE)
    payload = _payload(
        domain="legal",
        allowed_fields=["matter_number"],
        fragment_refs=[],
        dimensions=[{"name": "matter_number", "evidence_ref": "obs-1",
                     "requirement": "required", "metadata_only": False,
                     "order_index": 0, "scope": "template-local"}],
        levels=[{"dimension": "matter_number",
                 "retrieval_justification": "Every filing for one matter is one folder."}],
        example_label_chains=[["Legal", "M-2026-014"]],
    )
    assert validator(payload) is True


def test_a_template_local_dimension_naming_a_live_p6_field_key_is_refused():
    """Contract W3 — the borrowed-field guard, and the real attack.

    `target_school` is a live P6 field key belonging to another schema. Calling
    it "template-local" inside a `photos` proposal is not a novel label; it is
    the one-row-one-schema rule being evaded by relabelling. The check lives in
    P10's own `schema_validator`, which already holds the catalogue, so it adds
    no field to `Dossier` and no change to P8's frozen record.
    """
    from facts.fields import FIELD_ROWS

    assert "target_school" in {row.field_key for row in FIELD_ROWS}
    validator = template_schema_validator(CATALOGUE)
    payload = _payload(
        allowed_fields=["event", "capture_year", "target_school"],
        dimensions=[{"name": "target_school", "evidence_ref": "obs-1",
                     "requirement": "required", "metadata_only": False,
                     "order_index": 0, "scope": "template-local"}],
        levels=[{"dimension": "target_school",
                 "retrieval_justification": "borrowed from another schema"}],
    )
    assert validator(payload) is False


def test_a_dimension_must_declare_which_tier_it_claims():
    """Contract W2: "The payload must carry the tier explicitly, per dimension."
    An undeclared tier would have to be inferred, and the inference is exactly
    the assertion the classifier exists to make the model state out loud."""
    validator = template_schema_validator(CATALOGUE)
    payload = _payload()
    del payload["dimensions"][0]["scope"]
    assert validator(payload) is False
    payload = _payload()
    payload["dimensions"][0]["scope"] = "whatever"
    assert validator(payload) is False


def test_a_template_local_dimension_can_carry_no_expected_values():
    """Contract W4.3 and W5, enforced at the record P10 owns.

    A template-local level has no `field`, so there is nothing to read values
    from: its children are accepted group labels, not fact values. The record
    makes the pairing structural — `field_ref = None` is reachable ONLY through
    the declared template-local path, and a schema-field dimension must name a
    field. Neither shape can produce an `expected_values` entry, because
    `ResolvedDimension` has no such attribute to produce one from.
    """
    import dataclasses

    from tree_design.templates import MalformedTemplateRecord, ResolvedDimension
    from tree_design.vocabulary import (
        ACTION_SELECTED, SCOPE_SCHEMA_FIELD, SCOPE_TEMPLATE_LOCAL,
    )

    local = ResolvedDimension(
        role_ref="matter_number", field_ref=None, action=ACTION_SELECTED,
        order_index=0, display_label=None, scope=SCOPE_TEMPLATE_LOCAL)
    assert local.field_ref is None
    assert "expected_values" not in {
        f.name for f in dataclasses.fields(ResolvedDimension)}

    with pytest.raises(MalformedTemplateRecord):
        ResolvedDimension(role_ref="subject", field_ref=None,
                          action=ACTION_SELECTED, order_index=0,
                          display_label=None, scope=SCOPE_SCHEMA_FIELD)
    with pytest.raises(MalformedTemplateRecord):
        ResolvedDimension(role_ref="matter_number", field_ref="subject",
                          action=ACTION_SELECTED, order_index=0,
                          display_label=None, scope=SCOPE_TEMPLATE_LOCAL)


def test_nothing_promotes_a_local_dimension_into_the_canonical_vocabulary():
    """T17. Promotion is a human-reviewed pass, never automatic and never a
    model's decision. Asserted by ABSENCE, three ways, because one alone would
    be a comment."""
    import ast
    from pathlib import Path

    # 1. The closure for a field-less schema is empty and no call can change it.
    assert allowed_vocabulary_for(CATALOGUE, uses_schema="academic") == ()
    assert set(CATALOGUE.fragments) == {("event-capture-time", 1)}
    assert set(CATALOGUE.applicabilities) == {("photos--photos", 1)}

    # 2. There is no writer. `catalogue.py` loads a compiled manifest, and P10
    #    publishes nothing that adds a fragment, a row, or a P6 field.
    src = Path(__file__).resolve().parents[2] / "src" / "tree_design"
    functions = set()
    for path in sorted(src.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.add(node.name)
    assert not {"publish_fragment", "promote_dimension", "add_fragment",
                "register_fragment", "create_fields"} & functions

    # 3. A template-local name is not a P6 field, and P6 is where a folder level
    #    comes from. C2 still refuses it — the gate that keeps an accepted
    #    PROPOSAL from silently becoming a canonical branch level.
    import tempfile
    from pathlib import Path as _Path

    from database_agent.db import open_database
    from facts.fields import create_fields
    from tree_design.upstream import UpstreamUnavailable, resolve_role_to_field

    conn = open_database(_Path(tempfile.mkdtemp()) / "a.sqlite")
    create_fields(conn)
    with pytest.raises(UpstreamUnavailable):
        resolve_role_to_field(conn, role_ref="matter_number",
                              field_ref="matter_number")
    conn.close()


def test_a_site_e_request_without_a_plan_version_is_refused_by_p8s_own_record():
    """§8.8 captures template versions and ordering choices per plan version, and
    `E_template` is in P8's `SITES_REQUIRING_PLAN_VERSION`. P10 adds no check of
    its own; it passes the field and P8's record refuses the absence."""
    from llm_harness.records import MalformedRecord

    with pytest.raises(MalformedRecord):
        build_template_request(
            subject_ref="group-1", plan_version="", evidence_items=(),
            conflicts=(), model_call_request=None)
