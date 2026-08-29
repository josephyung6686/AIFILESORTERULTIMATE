"""The 22 authored launch fragments, driven through the real loader and merge.

`51-LAUNCH-TEMPLATE-DRAFT.md` §3.1 ratifies 3 shared fragments and §3.3 ratifies
19 order-carriers. This file asserts the shipped `src/tree_design/library/
fragments.json` IS that set, and — the half that discriminates a correct library
from an empty one — that malformed and contradictory records are refused by the
real callees rather than by a schema this test invented.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tree_design.catalogue import load_catalogue
from tree_design.templates import (
    CompositionConflict,
    FragmentRef,
    merge_fragment_constraints,
)

LIBRARY = Path(__file__).resolve().parents[2] / "src" / "tree_design" / "library"
FRAGMENTS_JSON = LIBRARY / "fragments.json"

#: P7 injects the real floor vocabulary per deployment; `51`'s appendix note 4
#: writes the placeholder symbol `baseline` and assigns no handling class, so the
#: rank a caller supplies here has exactly one entry.
RANK = {"baseline": 0, "protected": 1}.__getitem__

#: `51` §3.1 — the three shared fragments, and the reach each one claims.
SHARED = {
    "frag.subject-then-artifact": ("academic", "research", "code"),
    "frag.holder-affiliation-prefix": ("academic", "research"),
    "frag.cycle-then-artifact": ("academic", "college_applications"),
}

#: `51` §3.3 — the 19 order-carriers and the edges each one exists to supply.
CARRIER_EDGES = {
    "frag.affiliation-prefix-to-cycle": ((
        "holder_institution", "cycle_period"),),
    "frag.issuer-then-record": (
        ("issuing_org", "account_kind"), ("account_kind", "artifact_kind")),
    "frag.issuer-then-period-then-record": (
        ("issuing_org", "scope_period"), ("scope_period", "artifact_kind")),
    "frag.period-then-record": (
        ("scope_period", "artifact_kind"), ("artifact_kind", "issuing_org")),
    "frag.loan-kind-then-record": (
        ("account_kind", "issuing_org"), ("issuing_org", "artifact_kind")),
    "frag.function-then-container": (("artifact_kind", "account_kind"),),
    "frag.function-then-issuer": (("artifact_kind", "issuing_org"),),
    "frag.record-kind-only": (),
    "frag.capture-time-then-occasion": (
        ("capture_time", "occasion_anchor"), ("occasion_anchor", "capture_kind")),
    "frag.capture-kind-then-time": (("capture_kind", "capture_time"),),
    "frag.occasion-then-place": (
        ("occasion_anchor", "place"), ("place", "capture_time")),
    "frag.addressee-prefix": (("addressed_org", "cycle_period"),),
    "frag.purpose-only": (),
    "frag.preserved-root": (),
    "frag.container-then-artifact": (("repository_instance", "artifact_kind"),),
    "frag.subject-then-stage": (("subject_anchor", "lifecycle_stage"),),
    "frag.artifact-then-stage": (("artifact_kind", "lifecycle_stage"),),
    "frag.venue-in-submission-chain": (
        ("subject_anchor", "addressed_org"), ("addressed_org", "lifecycle_stage")),
    "frag.venue-prefix": (("addressed_org", "subject_anchor"),),
}

#: `43` §6.1 / `51` §2 — the 15 launch roles. A 16th appearing in a fragment is a
#: role the applicability rows cannot bind, so it would compose to nothing.
LAUNCH_ROLES = frozenset({
    "artifact_kind", "subject_anchor", "holder_institution", "cycle_period",
    "addressed_org", "issuing_org", "account_kind", "scope_period",
    "capture_time", "occasion_anchor", "capture_kind", "place",
    "lifecycle_stage", "repository_instance", "purpose_anchor",
})


def _raw() -> list[dict]:
    return json.loads(FRAGMENTS_JSON.read_text())["fragments"]


def _release(fragments: list[dict], release_id: str = "rel-launch-fragments"):
    """The authored fragments as a minimal manifest the REAL loader accepts.

    `definitions` and `applicabilities` are empty because sibling files author
    them; this seam is the fragment half of the release and nothing else.
    """
    manifest = {
        "release_id": release_id,
        "fragments": fragments,
        "definitions": [],
        "applicabilities": [],
    }
    return load_catalogue(lambda: json.dumps(manifest))


@pytest.fixture(scope="module")
def catalogue():
    return _release(_raw())


def test_the_authored_file_loads_through_the_real_loader(catalogue):
    """Not "the JSON parses" — the shipped bytes reach `TemplateFragment`."""
    assert catalogue.release_id == "rel-launch-fragments"
    assert len(catalogue.fragments) == 22
    assert set(catalogue.fragments) == {
        (fragment_id, 1) for fragment_id in (*SHARED, *CARRIER_EDGES)
    }


def test_every_fragment_resolves_by_ref_at_its_exact_version(catalogue):
    """Reuse is by stable id AND exact version. `@2` must not resolve to `@1`."""
    for fragment_id in (*SHARED, *CARRIER_EDGES):
        assert catalogue.has_fragment(fragment_id, 1)
        assert not catalogue.has_fragment(fragment_id, 2)
        fragment = catalogue.fragment(FragmentRef(fragment_id, 1))
        assert fragment.fragment_id == fragment_id
        assert fragment.fragment_version == 1


def test_the_three_shared_fragments_carry_the_reach_they_claim(catalogue):
    """§3.1's bar is "at least two reviewed contexts". Provenance is the check."""
    for fragment_id, provenance in SHARED.items():
        fragment = catalogue.fragment(FragmentRef(fragment_id, 1))
        assert fragment.provenance == provenance
        assert len(fragment.provenance) >= 2


def test_each_carrier_names_one_context_and_supplies_its_stated_edges(catalogue):
    """§3.3: a carrier is not a reuse claim, and must not pad its provenance."""
    for fragment_id, edges in CARRIER_EDGES.items():
        fragment = catalogue.fragment(FragmentRef(fragment_id, 1))
        assert fragment.relative_order == edges, fragment_id
        assert len(fragment.provenance) == 1, fragment_id


def test_no_fragment_uses_a_role_outside_the_launch_vocabulary(catalogue):
    for fragment in catalogue.fragments.values():
        assert set(fragment.roles) <= LAUNCH_ROLES, fragment.fragment_id
        assert set(fragment.optional_roles) <= set(fragment.roles)
        for before, after in fragment.relative_order:
            assert {before, after} <= set(fragment.roles), fragment.fragment_id


def test_every_floor_is_the_placeholder_so_none_silently_raises_another(catalogue):
    """`merge_fragment_constraints` takes the MAXIMUM floor across the fragments
    a recipe includes. One fragment authored above `baseline` would raise every
    recipe that imports it, invisibly — `51` §4.1 refuses exactly that, which is
    why exposure lives on the definition's `sensitivity_policy_ref` instead."""
    assert {f.privacy_floor for f in catalogue.fragments.values()} == {"baseline"}
    merged = merge_fragment_constraints(
        list(catalogue.fragments.values())[:1], privacy_rank=RANK)
    assert merged.privacy_floor == "baseline"


def test_the_refused_fourth_shared_fragment_was_not_re_added(catalogue):
    """§3.2 tested four near-misses and refused all four. Two are 00's forbidden
    merge and are detectable structurally: no fragment may put an issuer and an
    addressee under one role, nor a named container and an account category."""
    for fragment in catalogue.fragments.values():
        roles = set(fragment.roles)
        assert not {"issuing_org", "addressed_org"} <= roles, fragment.fragment_id
        assert not {"repository_instance", "account_kind"} <= roles, (
            fragment.fragment_id)
    assert not any("counterparty" in f.roles or "container" in f.roles
                   for f in catalogue.fragments.values())


def test_the_three_shared_fragments_plus_the_carrier_derive_00s_academic_order(
        catalogue):
    """§3.4(c), as REPAIRED by `56` D-a: the three shared fragments alone admit
    three orders (`cycle_period` and `subject_anchor` are unordered), so the
    merge refuses rather than picking. The recipe's own recommended nesting is
    what decides it — which is why this is `preferred_order`, not a fourth edge
    welded into a fragment seven definitions import."""
    family_a = [
        catalogue.fragment(FragmentRef(fragment_id, 1)) for fragment_id in (
            "frag.subject-then-artifact",
            "frag.holder-affiliation-prefix",
            "frag.cycle-then-artifact",
            "frag.affiliation-prefix-to-cycle",
        )
    ]
    with pytest.raises(CompositionConflict) as undecided:
        merge_fragment_constraints(family_a, privacy_rank=RANK)
    assert undecided.value.gate == "C5"
    assert "cycle_period" in str(undecided.value)
    assert "subject_anchor" in str(undecided.value)

    merged = merge_fragment_constraints(
        family_a, privacy_rank=RANK,
        preferred_order=("holder_institution", "cycle_period",
                         "subject_anchor", "artifact_kind"))
    assert merged.ordered_roles == (
        "holder_institution", "cycle_period", "subject_anchor", "artifact_kind")
    assert merged.optional_roles == frozenset(
        {"holder_institution", "cycle_period"})


def test_two_authored_fragments_with_opposite_edges_are_refused_as_a_cycle(
        catalogue):
    """The discriminating case, run on the SHIPPED records rather than a fixture.

    `frag.issuer-then-record` says `issuing_org -> ... -> artifact_kind`;
    `frag.function-then-issuer` says `artifact_kind -> issuing_org`. Both are
    ratified, both serve different recipes, and a definition that referenced both
    would compose a cyclic graph. C5 refuses the whole composition — which is the
    proof that `relative_order` is a constraint and not a preference.
    """
    opposed = [
        catalogue.fragment(FragmentRef("frag.issuer-then-record", 1)),
        catalogue.fragment(FragmentRef("frag.function-then-issuer", 1)),
    ]
    with pytest.raises(CompositionConflict) as refused:
        merge_fragment_constraints(opposed, privacy_rank=RANK)
    assert refused.value.gate == "C5"
    assert "cycle" in str(refused.value)


def test_the_photos_carriers_are_mutually_exclusive_by_construction(catalogue):
    """The same proof on the second opposed pair, because it is the one a future
    photos recipe is most likely to reach for: `capture_time -> occasion_anchor`
    against `occasion_anchor -> place -> capture_time`."""
    with pytest.raises(CompositionConflict) as refused:
        merge_fragment_constraints(
            [catalogue.fragment(FragmentRef("frag.capture-time-then-occasion", 1)),
             catalogue.fragment(FragmentRef("frag.occasion-then-place", 1))],
            privacy_rank=RANK)
    assert refused.value.gate == "C5"


def test_a_fragment_missing_a_required_key_is_refused_by_the_loader():
    """Every key `_fragment` reads is required. Dropping one must not load as a
    default — a fragment silently missing `relative_order` would organize by
    accident."""
    for key in ("fragment_id", "fragment_version", "roles", "relative_order",
                "imports", "optional_roles", "metadata_only_roles",
                "allowed_values", "privacy_floor", "provenance"):
        broken = _raw()
        del broken[0][key]
        with pytest.raises(KeyError):
            _release(broken)


def test_a_fragment_with_no_role_or_no_provenance_is_refused(catalogue):
    from tree_design.templates import MalformedTemplateRecord

    roleless = _raw()
    roleless[0]["roles"] = []
    with pytest.raises(MalformedTemplateRecord):
        _release(roleless)

    unattributed = _raw()
    unattributed[0]["provenance"] = []
    with pytest.raises(MalformedTemplateRecord):
        _release(unattributed)

    stray = _raw()
    stray[0]["optional_roles"] = ["a_role_this_fragment_does_not_define"]
    with pytest.raises(MalformedTemplateRecord):
        _release(stray)


def test_a_cyclic_relative_order_authored_into_one_fragment_is_refused():
    """The loader accepts it — `TemplateFragment` validates records, not graphs.
    The refusal is C5's, at composition, and that is where this asserts it, so a
    future edit that reverses one authored pair cannot pass by loading."""
    cyclic = _raw()
    cyclic[0]["relative_order"] = [["subject_anchor", "artifact_kind"],
                                   ["artifact_kind", "subject_anchor"]]
    poisoned = _release(cyclic)
    with pytest.raises(CompositionConflict) as refused:
        merge_fragment_constraints(
            [poisoned.fragment(FragmentRef("frag.subject-then-artifact", 1))],
            privacy_rank=RANK)
    assert refused.value.gate == "C5"
    assert "cycle" in str(refused.value)


def test_a_release_without_an_identity_is_refused():
    from tree_design.config import ConfigurationRequired

    with pytest.raises(ConfigurationRequired):
        _release(_raw(), release_id="")
