"""P10 Task 11 — a small derived scaffold, then one branch at a time.

§5.1's nine example names — Academics, Applications, Research, Career, Personal
Records, Finance and Administration, Photos and Captures, Code and Projects,
Media or Miscellaneous Personal Material — are what "a typical initial canvas
might include". They are illustrative. Shipping them as a fixed set would be the
"universal corporate taxonomy" §5.1 says labels should NOT reflect, and this
suite asserts they are absent from the source.
"""
from __future__ import annotations

import pytest

from tree_design.candidates import (
    NO_SPLIT,
    BranchCandidate,
    horizontal_candidates,
    vertical_options,
)
from tree_design.provenance import branch_basis_key, record_tree_edit
from tree_design.routing import RoutingReport
from tree_design.upstream import AcceptedGroup, ExistingFolder, GroupMember
from tree_design.vocabulary import (
    ACCEPT,
    ACTION_SELECTED,
    DEFER,
    MERGE,
    RENAME,
    SCOPE_SCHEMA_FIELD,
)

T0 = "2026-08-27T00:00:00Z"


def _group(group_id, label, domain, files, classes=("personal_non_sensitive",)):
    return AcceptedGroup(
        group_id=group_id, label=label, domain=domain,
        members=tuple(GroupMember(f, f"h_{f}", "direct-anchor") for f in files),
        anchor_facts=(f"fact_{group_id}",), excluded_members=(),
    )


ACADEMIC = _group("g_phys", "PHYS 1401", "academic", ("lecture", "hw"))
APPS = _group("g_apps", "Columbia application", "college_applications",
              ("transcript", "essay"))
FOLDER = ExistingFolder(
    directory_path="/Users/jy/Documents/School", parent_directory="/Users/jy/Documents",
    file_count=31, curation_signal="curated")


def _call(conn, **overrides):
    kwargs = dict(
        accepted=(ACADEMIC, APPS), existing_folders=(FOLDER,), user_labels=(),
        active_domains=("academic", "college_applications"),
        sensitive_group_ids=frozenset(),
    )
    kwargs.update(overrides)
    return horizontal_candidates(conn, **kwargs)


def test_a_candidate_is_derived_from_a_group_and_names_its_evidence(conn):
    candidates = {c.display_label: c for c in _call(conn)}
    academic = candidates["PHYS 1401"]
    assert academic.accepted_group_ids == ("g_phys",)
    assert academic.supporting_file_count == 2
    assert "PHYS 1401" in academic.why_suggested
    assert academic.subject_id == "g_phys"


def test_no_candidate_carries_a_confidence_score(conn):
    """§5.2: a concise explanation "rather than a technical confidence score".
    Internal scores may exist (§3.13) but they are not this surface."""
    for candidate in _call(conn):
        assert not any(
            token in candidate.why_suggested.lower()
            for token in ("confidence", "score", "probability", "%")
        )
        assert not any(
            field.startswith(("score", "confidence"))
            for field in candidate.__dataclass_fields__
        )


def test_a_curated_existing_folder_becomes_its_own_candidate(conn):
    """§5.10: a curated folder "should be treated as a strong expression of user
    intent"."""
    candidates = {c.display_label: c for c in _call(conn)}
    assert "School" in candidates
    assert candidates["School"].source == "existing-folder"
    assert candidates["School"].resembling_existing_folders == (
        "/Users/jy/Documents/School",)


def test_an_undetermined_folder_is_not_promoted_to_curated(conn):
    """P3 returns `undetermined` for every directory today, and §8.6 requires
    leaving something in review rather than guessing. An undetermined folder is
    still shown, and it is not treated as a strong expression of intent."""
    undetermined = ExistingFolder(
        directory_path="/Users/jy/Downloads", parent_directory="/Users/jy",
        file_count=904, curation_signal="undetermined")
    candidates = {c.display_label: c for c in _call(conn, existing_folders=(undetermined,))}
    assert "Downloads" in candidates
    assert candidates["Downloads"].source == "existing-folder-undetermined"


def test_a_rejected_branch_does_not_resurface(conn):
    """§8.7 and §4.9. The query is P1's `learning_records`, keyed on the parent
    and the label, and it runs BEFORE the candidate reaches the canvas."""
    key = branch_basis_key(parent_node_id=None, dimension_or_label="PHYS 1401")
    record_tree_edit(
        conn, action="delete", node_id="n_phys",
        plan_version_id="plan_1", before={"display_label": "PHYS 1401"}, after={},
        explanation="User deleted the suggested PHYS 1401 area.",
        observed_at=T0, user_id="jy", component_version="p10-1",
        correction_scope="node", correction_subject="__root__",
        polarity="reject", basis_key=key)
    labels = {c.display_label for c in _call(conn)}
    assert "PHYS 1401" not in labels
    assert "Columbia application" in labels


def test_the_nine_51_example_names_are_not_shipped_as_a_fixed_set(conn):
    import ast
    from pathlib import Path

    source = (Path(__file__).resolve().parents[2]
              / "src" / "tree_design" / "candidates.py").read_text()
    literals = {
        node.value for node in ast.walk(ast.parse(source))
        if isinstance(node.__class__, type) and isinstance(node, ast.Constant)
        and isinstance(node.value, str)
    }
    for illustration in ("Academics", "Applications", "Research", "Career",
                         "Personal Records", "Finance and Administration",
                         "Photos and Captures", "Code and Projects",
                         "Media or Miscellaneous Personal Material"):
        assert illustration not in literals
    # And the derived candidates come only from the evidence supplied.
    assert {c.display_label for c in _call(conn)} == {
        "PHYS 1401", "Columbia application", "School"}


def test_a_user_label_is_a_candidate_source_in_its_own_right(conn):
    candidates = {c.display_label: c for c in _call(conn, user_labels=("Taxes",))}
    assert candidates["Taxes"].source == "user-label"
    assert candidates["Taxes"].accepted_group_ids == ()


def test_a_sensitive_group_is_flagged_without_naming_a_file(conn):
    """§5.2: a Finance or Identity proposal "may be visible as a protected area,
    but the product should avoid showing sensitive filenames"."""
    candidates = {c.display_label: c for c in _call(
        conn, sensitive_group_ids=frozenset({"g_apps"}))}
    assert candidates["Columbia application"].sensitive_content_present is True
    text = candidates["Columbia application"].why_suggested
    assert "transcript" not in text and "essay" not in text


def test_every_candidate_offers_52s_actions(conn):
    for candidate in _call(conn):
        assert {ACCEPT, RENAME, MERGE, DEFER} <= set(candidate.available_actions)


def test_a_purpose_packet_stays_one_candidate_and_is_not_split_by_institution(conn):
    """§5.6: the canvas must be able to present a purpose-coherent,
    content-incoherent packet "as a preserved or proposed branch alongside
    institution-based organization"."""
    packet = _group("g_packet", "Grad school packet", "college_applications",
                    ("transcript", "id", "statement", "resume", "certificate"))
    candidates = {c.display_label: c for c in _call(conn, accepted=(packet,))}
    assert set(candidates) >= {"Grad school packet"}
    assert candidates["Grad school packet"].supporting_file_count == 5


def test_the_vertical_pass_always_offers_the_no_split_option():
    """§5.3: a candidate may be "a complete reusable template, a compatible
    composition of reusable fragments, or NO SPLIT." Keeping the branch shallow
    is a first-class answer, not a refusal to answer."""
    report = RoutingReport(candidates=(), conflicts=(), deferred=0)
    options = vertical_options(
        report, branch_members=("f1", "f2"),
        materialise=lambda candidate: None, validate=lambda materialised: None)
    assert [o.kind for o in options] == [NO_SPLIT]
    assert options[0].total_child_branches == 0
    assert options[0].unresolved_file_ids == ()


def test_a_whole_option_preview_states_what_each_option_would_create():
    """§5.5 wants the comparison, not just the per-level counts: Option A "would
    create three schools, five terms, and twelve course branches"; Option C "is
    shallower but leaves more files together"."""
    from tree_design.routing import CompositionCandidate
    from tree_design.templates import ApplicabilityRef, ResolvedDimension
    from tree_design.validation import ValidationReport
    
    candidate = CompositionCandidate(
        applicability_refs=(ApplicabilityRef("a1", 1),),
        resolved_dimensions=(
            ResolvedDimension("school", "school", ACTION_SELECTED, 0, None, SCOPE_SCHEMA_FIELD),
            ResolvedDimension("term", "term", ACTION_SELECTED, 1, None, SCOPE_SCHEMA_FIELD),
            ResolvedDimension("subject", "subject", ACTION_SELECTED, 2, None, SCOPE_SCHEMA_FIELD),
        ),
        privacy_floor="policy.public",
        covered_file_ids=frozenset({"f1", "f2"}),
        gates_passed=("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"),
        overridden_gates=(),
        explanation="one row resolves three dimensions",
    )
    report = RoutingReport(candidates=(candidate,), conflicts=(), deferred=0)

    def materialise(_candidate):
        return {"school": 3, "term": 5, "subject": 12}

    def validate(_materialised):
        return ValidationReport(report_id="vr_1",
                                passed=("V1", "V2", "V3", "V4", "V5", "V6"),
                                failures=())

    options = vertical_options(report, branch_members=("f1", "f2", "f3"),
                               materialise=materialise, validate=validate)
    split = options[0]
    assert split.resulting_child_counts == {"school": 3, "term": 5, "subject": 12}
    assert split.total_child_branches == 12
    assert "3 school" in split.summary and "12 subject" in split.summary
    assert split.unresolved_file_ids == ("f3",)
    assert options[-1].kind == NO_SPLIT


def test_a_conflicted_route_yields_no_option_and_no_invented_branch():
    from tree_design.templates import CompositionConflict

    conflict = CompositionConflict("C3", ["finance"], "no row is eligible")
    report = RoutingReport(candidates=(), conflicts=(conflict,), deferred=0)
    options = vertical_options(
        report, branch_members=("f1",), materialise=lambda c: None,
        validate=lambda m: None)
    assert [o.kind for o in options] == [NO_SPLIT]
    assert "no applicable recipe" in options[0].summary


def test_a_failed_validation_keeps_the_option_visible_and_unusable():
    """§8.6 requires showing "the difference between completed work and deferred
    work". An option that failed V1-V6 is shown with its reason, not hidden —
    hiding it teaches the user the product simply had no idea."""
    from tree_design.routing import CompositionCandidate
    from tree_design.templates import ApplicabilityRef, ResolvedDimension
    from tree_design.validation import CheckFailure, ValidationReport
    
    candidate = CompositionCandidate(
        applicability_refs=(ApplicabilityRef("a1", 1),),
        resolved_dimensions=(
            ResolvedDimension("subject", "subject", ACTION_SELECTED, 0, None, SCOPE_SCHEMA_FIELD),),
        privacy_floor="policy.public", covered_file_ids=frozenset({"f1"}),
        gates_passed=("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"),
        overridden_gates=(),
        explanation="one row resolves one dimension",
    )
    report = RoutingReport(candidates=(candidate,), conflicts=(), deferred=0)
    failing = ValidationReport(
        report_id="vr_1", passed=("V1", "V3", "V4", "V5", "V6"),
        failures=(CheckFailure("V2", "one child, PHYS1401", ("PHYS1401",)),))
    options = vertical_options(
        report, branch_members=("f1",), materialise=lambda c: {"subject": 1},
        validate=lambda m: failing)
    assert options[0].validation.failures
    assert "V2" in options[0].summary
