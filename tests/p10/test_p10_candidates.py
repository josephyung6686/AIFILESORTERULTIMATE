"""P10 Task 11 — a small derived scaffold, then one branch at a time.

§5.1's nine example names — Academics, Applications, Research, Career, Personal
Records, Finance and Administration, Photos and Captures, Code and Projects,
Media or Miscellaneous Personal Material — are what "a typical initial canvas
might include". They are illustrative. Shipping them as a fixed set would be the
"universal corporate taxonomy" §5.1 says labels should NOT reflect, and this
suite asserts they are absent from the source.
"""
from __future__ import annotations

import dataclasses

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


def test_the_vertical_pass_always_offers_the_no_split_option(conn):
    """§5.3: a candidate may be "a complete reusable template, a compatible
    composition of reusable fragments, or NO SPLIT." Keeping the branch shallow
    is a first-class answer, not a refusal to answer."""
    report = RoutingReport(candidates=(), conflicts=(), deferred=0)
    options = vertical_options(
        report, branch_members=("f1", "f2"),
        materialise=lambda candidate: None, validate=lambda materialised: None,
        limits=_limits(conn), preview=_preview_binding())
    assert [o.kind for o in options] == [NO_SPLIT]
    assert options[0].total_child_branches == 0
    assert options[0].unresolved_file_ids == ()


def test_a_whole_option_preview_states_what_each_option_would_create(conn):
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

    # Real level evidence now, because the picker must be able to preview the
    # tree it would build in order to warn about it (`00`:99).
    evidence = _evidence(
        _level("school", "school", 0,
               {f"S{i}": {f"f{i}"} for i in range(3)}),
        _level("term", "term", 1, {f"T{i}": {f"f{i}"} for i in range(3)}),
    )

    def materialise(_candidate):
        return evidence

    def validate(_materialised):
        return ValidationReport(report_id="vr_1",
                                passed=("V1", "V2", "V3", "V4", "V5", "V6"),
                                failures=())

    options = vertical_options(report, branch_members=("f1", "f2", "f3"),
                               materialise=materialise, validate=validate,
                               limits=_limits(conn), preview=_preview_binding())
    split = options[0]
    assert split.resulting_child_counts == {"school": 3, "term": 3}
    assert "3 school" in split.summary and "3 term" in split.summary
    assert split.unresolved_file_ids == ("f3",)
    assert options[-1].kind == NO_SPLIT


def test_a_conflicted_route_yields_no_option_and_no_invented_branch(conn):
    from tree_design.templates import CompositionConflict

    conflict = CompositionConflict("C3", ["finance"], "no row is eligible")
    report = RoutingReport(candidates=(), conflicts=(conflict,), deferred=0)
    options = vertical_options(
        report, branch_members=("f1",), materialise=lambda c: None,
        validate=lambda m: None, limits=_limits(conn), preview=_preview_binding())
    assert [o.kind for o in options] == [NO_SPLIT]
    assert "no applicable recipe" in options[0].summary


def test_a_failed_validation_keeps_the_option_visible_and_unusable(conn):
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
        report, branch_members=("f1",),
        materialise=lambda c: _evidence(
            _level("subject", "subject", 0, {"PHYS1401": {"f1"}})),
        validate=lambda m: failing, limits=_limits(conn),
        preview=_preview_binding())
    assert options[0].validation.failures
    assert "V2" in options[0].summary


# --- 00:99 — the live structural feedback that must arrive BEFORE the choice ----

from tree_design.materialise import BranchEvidence, LevelEvidence  # noqa: E402


def _level(role, field, index, values):
    return LevelEvidence(
        dimension_role=role, field_ref=field, order_index=index,
        metadata_only=False, display_labels={},
        members_by_value={v: frozenset(f) for v, f in values.items()},
        handling_classes_by_value={
            v: frozenset({"personal_non_sensitive"}) for v in values})


def _evidence(*levels):
    members = frozenset().union(
        *[frozenset().union(*level.members_by_value.values())
          for level in levels]) if levels else frozenset()
    return BranchEvidence(branch_node_id="n_branch", levels=tuple(levels),
                          member_file_ids=members, unresolved_by_field={})


def _branch_parent(dimension=None, role=None):
    from tree_design.records import Node

    return Node(
        node_id="n_branch", plan_version_id="plan_1", node_type="proposed",
        display_label="Academics", parent_node_id=None,
        root_anchor="root_documents", ordinal=0, associated_group_ids=(),
        explanation="The accepted groups beneath it produced this area.",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id="n_branch",
        dimension=dimension, dimension_role=role)


def _preview_binding(parent_dimension=None):
    from tree_design.materialise import project_branch_preview
    from tree_design.validation import ValidationReport

    counter = iter(range(500))
    accepted = ValidationReport(report_id="vr_preview", passed=("V1",), failures=())

    def preview(_candidate, evidence):
        return project_branch_preview(
            evidence, accepted, parent=_branch_parent(parent_dimension,
                                                      parent_dimension),
            plan_version_id="plan_1",
            mint_node_id=lambda: f"n_prev_{next(counter)}",
            handling_class_for=lambda classes: "personal_non_sensitive",
            template_context_for=lambda field_ref, order_index: None)
    return preview


def _limits(conn, **over):
    from database_agent.budget import set_ceiling
    from tree_design.config import tree_limits

    set_ceiling(conn, "tree.max_folder_proposals_and_depth", 6)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    kwargs = dict(excessive_depth_warning=3, tiny_folder_max_files=2,
                  tiny_folder_count_warning=3,
                  materially_improves_retrieval=lambda preview: None)
    kwargs.update(over)
    return tree_limits(conn, **kwargs)


def _one_candidate(*roles, covered=frozenset({"f1", "f2"})):
    from tree_design.routing import CompositionCandidate
    from tree_design.templates import ApplicabilityRef, ResolvedDimension

    return CompositionCandidate(
        applicability_refs=(ApplicabilityRef("a1", 1),),
        resolved_dimensions=tuple(
            ResolvedDimension(role, role, ACTION_SELECTED, index, None,
                              SCOPE_SCHEMA_FIELD)
            for index, role in enumerate(roles)),
        privacy_floor="policy.public", covered_file_ids=frozenset(covered),
        gates_passed=("C1",), overridden_gates=(),
        explanation="one row resolves these dimensions")


def _options(conn, evidence, *roles, parent_dimension=None, **limit_over):
    # A routed candidate covers the branch's own files (C6). Hard-coding a
    # narrower set would make every extra file read as "routing missed it".
    report = RoutingReport(
        candidates=(_one_candidate(*roles, covered=evidence.member_file_ids),),
        conflicts=(), deferred=0)
    return vertical_options(
        report, branch_members=tuple(sorted(evidence.member_file_ids)),
        materialise=lambda candidate: evidence,
        validate=lambda candidate: None,
        limits=_limits(conn, **limit_over),
        preview=_preview_binding(parent_dimension))


def test_a_level_that_would_produce_one_child_warns_before_the_choice(conn):
    """`00`:99 is imperative and it is explicit about the timing: "Before the
    user chooses a split ... It should warn when a level produces only one
    child."

    `warnings_for` had NO production caller — the §5.9 safety net was not
    connected to the thing that proposes trees. An unwarned picker is how the
    product proposes a bad tree with a straight face.
    """
    from tree_design.vocabulary import WARN_ONE_CHILD

    evidence = _evidence(
        _level("school", "school", 0, {"Columbia": {"f1", "f2", "f3"}}),
        _level("term", "term", 1, {"2026": {"f1"}, "2025": {"f2", "f3"}}))
    option = _options(conn, evidence, "school", "term")[0]
    assert WARN_ONE_CHILD in {w.kind for w in option.warnings}
    assert any(w.evidence for w in option.warnings)


def test_an_option_that_would_scatter_files_into_tiny_folders_warns(conn):
    """`00`:99's fourth warning. It cannot fire without files-per-child, which is
    why the wiring and the missing count are one job: `child_counts` returns how
    many BRANCHES a level makes, never how many FILES sit under each."""
    from tree_design.vocabulary import WARN_TINY_FOLDERS

    evidence = _evidence(_level("vendor", "vendor", 0, {
        "Acme": {"f1"}, "Beta": {"f2"}, "Gamma": {"f3"}, "Delta": {"f4"}}))
    option = _options(conn, evidence, "vendor")[0]
    assert WARN_TINY_FOLDERS in {w.kind for w in option.warnings}


def test_every_option_reports_the_files_under_each_child(conn):
    """`00`:99 asks for "the resulting number of child branches, THE NUMBER OF
    FILES UNDER EACH CHILD, example members, unresolved files". Only the first,
    third and fourth were published."""
    evidence = _evidence(_level("subject", "subject", 0, {
        "PHYS1401": {"f1", "f2"}, "CHEM1101": {"f3"}}))
    option = _options(conn, evidence, "subject")[0]
    by_label = {child.label_chain[-1]: child.file_count
                for child in option.children}
    assert by_label == {"PHYS1401": 2, "CHEM1101": 1}
    assert all(child.label_chain[0] == "Academics" for child in option.children)


def test_the_no_split_option_carries_no_warning_and_no_child(conn):
    """Keeping the branch as it is creates no level, so §5.9 has nothing to warn
    about. An empty tuple, not a `None` the caller has to test for."""
    option = _options(conn, _evidence(), "subject")[-1]
    assert option.kind == NO_SPLIT
    assert option.warnings == ()
    assert option.children == ()


def test_the_flatten_recommendation_reaches_the_picker_when_the_test_says_no(conn):
    """§5.9's recommendation is the one the ratified `career` decision leans on:
    both orders ship with neither marked recommended, so the steer has to arrive
    live, at the moment of choice, against the user's real corpus."""
    from tree_design.vocabulary import RECOMMEND_FLATTEN

    evidence = _evidence(
        _level("subject", "subject", 0, {"PHYS1401": {"f1", "f2"}}),
        _level("term", "term", 1, {"2026": {"f1"}, "2025": {"f2"}}))
    option = _options(conn, evidence, "subject", "term",
                      materially_improves_retrieval=lambda preview: False)[0]
    assert RECOMMEND_FLATTEN in {w.kind for w in option.warnings}


def test_every_5_9_warning_kind_has_a_production_caller(conn):
    """The durable guard, so this cannot silently regress.

    `warnings_for` was defined in `health.py` and called from `tests/` and
    nowhere else. §5.9's four warnings and its flattening recommendation were
    computed by a function no production code invoked. This asserts the module
    that proposes splits is the module that imports the warnings, by AST — the
    same technique as `health.py`'s own import guard, inverted.
    """
    import ast
    from pathlib import Path

    from tree_design.vocabulary import WARNING_KINDS

    source = (Path(__file__).resolve().parents[2]
              / "src" / "tree_design" / "candidates.py").read_text()
    imported = {
        alias.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module == "tree_design.health"
        for alias in node.names
    }
    assert {"warnings_for", "branch_counts", "parent_concepts_for"} <= imported

    called = {
        node.func.id for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "warnings_for" in called, "§5.9 is imported but never invoked"

    # And every kind the vocabulary publishes is reachable from this one call.
    assert len(WARNING_KINDS) == 5


def test_children_that_are_not_tiny_produce_no_tiny_folder_warning(conn):
    """The other half of the tiny-folder guard, and the half that makes the
    files-per-child wiring load-bearing.

    Asserting only that the warning FIRES is satisfied by feeding zero files per
    child: zero is `<= tiny_folder_max_files` too, so a preview that dropped the
    counts entirely warned about every split. This is the case that separates
    "the counts arrived" from "the counts were the right shape".
    """
    from tree_design.vocabulary import WARN_TINY_FOLDERS

    evidence = _evidence(_level("vendor", "vendor", 0, {
        "Acme": {"a1", "a2", "a3", "a4", "a5"},
        "Beta": {"b1", "b2", "b3", "b4", "b5"},
        "Gamma": {"g1", "g2", "g3", "g4", "g5"},
        "Delta": {"d1", "d2", "d3", "d4", "d5"}}))
    option = _options(conn, evidence, "vendor")[0]
    assert all(child.file_count == 5 for child in option.children)
    assert WARN_TINY_FOLDERS not in {w.kind for w in option.warnings}


def test_a_split_that_repeats_the_branchs_own_concept_warns(conn):
    """§5.9's second warning, at the picker: a level that "repeats a concept
    already expressed in the parent".

    The branch is already a subject. Splitting it by subject again says nothing
    new, and the warning can only be computed if the preview passes the parent
    chain to `warnings_for` — which is what `parent_concepts_for` is for.
    """
    from tree_design.vocabulary import WARN_REPEATED_PARENT

    evidence = _evidence(_level("subject", "subject", 0,
                                {"PHYS1401": {"f1"}, "CHEM1101": {"f2"}}))
    option = _options(conn, evidence, "subject", parent_dimension="subject")[0]
    assert WARN_REPEATED_PARENT in {w.kind for w in option.warnings}


# --- the owner's standing rule: marked and counted, never opened ----------------


def _area(path, label="Numbers.app"):
    from tree_design.upstream import ProtectedArea

    return ProtectedArea(
        path=path, display_label=label, rule_subject="protected_container",
        applies_to="scan", label="untouched_protected",
        observed_at="2026-08-27T00:00:00Z")


def _protected(*areas, **over):
    from tree_design.candidates import protected_area_nodes

    counter = iter(range(50))
    kwargs = dict(plan_version_id="plan_1", root_anchor="root_documents",
                  mint_node_id=lambda: f"n_prot_{next(counter)}",
                  handling_class_for=lambda area: "personal_non_sensitive")
    kwargs.update(over)
    return protected_area_nodes(areas, **kwargs)


def test_a_protected_area_becomes_a_node_that_is_present_and_untouched():
    """`node_type=PROTECTED` is in `NODE_TYPES` (§5.12's five) and
    `derive_accepts_placement` already encodes the rule — but NOTHING in src/ ever
    constructed one. A reserved name with no producer, and the consequence is the
    outcome the owner explicitly forbade: the area is silently omitted.
    """
    node, = _protected(_area("/Users/jy/Applications/Numbers.app"))
    assert node.node_type == "protected"
    assert node.display_label == "Numbers.app"
    assert node.protected_movement_permitted is False
    assert node.accepts_placement is False


def test_a_protected_node_carries_an_explanation_naming_the_area():
    """"Never described as 'understood and found unimportant'." A generic
    explanation fails the requirement as surely as an absent one, so the node has
    to name the thing it is declining to open."""
    node, = _protected(_area("/Users/jy/Applications/Numbers.app"))
    assert "Numbers.app" in node.explanation
    lowered = node.explanation.lower()
    assert "unimportant" not in lowered
    assert "never opened" in lowered or "not opened" in lowered
    assert len(node.explanation) > 40


def test_the_handling_class_for_a_protected_node_is_injected_never_guessed():
    """Same discipline as `materialise.project_branch_nodes`: P7 owns
    `HANDLING_CLASSES` and has published no ordering, so P10 picks none."""
    from tree_design.config import ConfigurationRequired

    with pytest.raises(ConfigurationRequired):
        _protected(_area("/Users/jy/Applications/Numbers.app"),
                   handling_class_for=None)


def test_nothing_here_grants_movement_permission_by_itself():
    """§8.4: protected material "should not be moved automatically without a user
    policy that explicitly permits it". P3's rule is stronger still — its own
    docstring says no policy, approval, or user gesture makes an application
    movable — so this producer takes no argument that could turn it on.
    """
    import inspect

    from tree_design.candidates import protected_area_nodes

    parameters = inspect.signature(protected_area_nodes).parameters
    assert "protected_movement_permitted" not in parameters
    for node in _protected(_area("/a/X.app", "X.app"), _area("/b/Y.app", "Y.app")):
        assert node.protected_movement_permitted is False
        assert node.accepts_placement is False


def test_every_protected_area_gets_its_own_node_and_none_is_dropped():
    nodes = _protected(_area("/a/X.app", "X.app"), _area("/b/Y.app", "Y.app"),
                       _area("/c/Z.app", "Z.app"))
    assert [n.display_label for n in nodes] == ["X.app", "Y.app", "Z.app"]
    assert len({n.node_id for n in nodes}) == 3
    assert all(n.origin_node_id == n.node_id for n in nodes)


def test_total_child_branches_counts_the_branches_the_option_would_create(conn):
    """`max(counts.values())` is the WIDEST SINGLE LEVEL's branch count — neither
    the immediate children nor the total. `00`:99 puts this number in front of the
    user before they choose a split, so a value meaning something other than its
    name is read as fact and acted on.

    Three schools, each with two terms, is 3 + 6 = 9 branches. The old number
    said 6, which is not a count of anything the user can see.
    """
    evidence = _evidence(
        _level("school", "school", 0,
               {"Columbia": {"f1", "f2"}, "NYU": {"f3", "f4"}, "MIT": {"f5", "f6"}}),
        _level("term", "term", 1,
               {"2026": {"f1", "f3", "f5"}, "2025": {"f2", "f4", "f6"}}))
    option = _options(conn, evidence, "school", "term")[0]
    assert option.resulting_child_counts == {"school": 3, "term": 2}
    assert len(option.children) == 9
    assert option.total_child_branches == 9


def test_a_protected_file_is_marked_on_the_branch_that_holds_it(conn):
    """The standing rule reaches the picker: marked and counted, never opened,
    NEVER SILENTLY OMITTED.

    The file stays COUNTED — it is a member of the branch and of its value — and
    it is NAMED, so the interface can say the branch holds it and it will not be
    moved. `unresolved_file_ids` cannot carry it: unresolved means "no settled
    value", and this file has one. It is a third thing and it says so.
    """
    evidence = _evidence(_level("subject", "subject", 0, {
        "PHYS1401": {"f1", "passport"}, "CHEM1101": {"f3"}}))
    evidence = dataclasses.replace(
        evidence, protected_file_ids=frozenset({"passport"}))
    option = _options(conn, evidence, "subject")[0]
    assert option.protected_file_ids == ("passport",)
    assert "passport" not in option.unresolved_file_ids
    # Counted: three files across two children, the passport among them.
    assert sum(child.file_count for child in option.children) == 3


def test_a_branch_with_no_protected_file_marks_nothing(conn):
    """The discriminating half: always reporting something would be as useless
    as never reporting anything."""
    evidence = _evidence(_level("subject", "subject", 0, {"PHYS1401": {"f1"}}))
    option = _options(conn, evidence, "subject")[0]
    assert option.protected_file_ids == ()


def test_the_node_holding_protected_material_is_marked_sensitive(conn):
    """`sensitive_node_ids` was hard-wired to `frozenset()` in the call that
    feeds §5.9, so `BranchCounts.sensitive_isolated` could never be true for any
    node — a field that existed, was carried, and could not be reached.

    `00`:101 asks tree health to show "where sensitive material has been
    isolated". That is per NODE, so the node holding the passport is marked and
    the one beside it is not.
    """
    from tree_design.health import branch_counts, parent_concepts_for

    evidence = _evidence(_level("subject", "subject", 0, {
        "PHYS1401": {"f1", "passport"}, "CHEM1101": {"f3"}}))
    evidence = dataclasses.replace(
        evidence, protected_file_ids=frozenset({"passport"}))
    built = _preview_binding()(None, evidence)
    counts = _branch_counts_for(built, evidence)
    by_label = {n.display_label: n.node_id for n in built.nodes}
    assert counts[by_label["PHYS1401"]].sensitive_isolated is True
    assert counts[by_label["CHEM1101"]].sensitive_isolated is False


def test_a_file_that_reaches_no_folder_is_reported_as_unresolved(conn):
    """`00`:99 requires the picker to show "unresolved files". The call feeding
    §5.9 hard-wired `unresolved_by_node={}`, so a file that two branches both
    wanted, or that settled no value, vanished with no trace on screen."""
    evidence = _evidence(_level("subject", "subject", 0, {"PHYS1401": {"f1"}}))
    evidence = dataclasses.replace(
        evidence, member_file_ids=frozenset({"f1", "orphan"}))
    option = _options(conn, evidence, "subject")[0]
    assert "orphan" in option.unresolved_file_ids
    assert "f1" not in option.unresolved_file_ids


def test_a_branch_where_every_file_lands_reports_nothing_unresolved(conn):
    """The discriminating half."""
    evidence = _evidence(_level("subject", "subject", 0, {
        "PHYS1401": {"f1"}, "CHEM1101": {"f2"}}))
    option = _options(conn, evidence, "subject")[0]
    assert option.unresolved_file_ids == ()


def _branch_counts_for(built, evidence):
    from tree_design.candidates import _counts_for_preview

    return _counts_for_preview(built, evidence)


def test_the_branch_counts_carry_the_unresolved_files_for_the_branch_node(conn):
    """`00`:99 lists what the picker must show BEFORE the user chooses: "the
    resulting number of child branches, the number of files under each child,
    example members, unresolved files, and any evidence gaps". Those are
    `BranchCounts` fields, and `unresolved_by_node` was hard-wired empty in the
    call that builds them — so `BranchCounts.unresolved_file_ids` was zero for
    every node no matter what the evidence said.

    The unresolved files belong to the BRANCH being split, which is the node the
    user is looking at when they read the number.
    """
    evidence = _evidence(_level("subject", "subject", 0, {"PHYS1401": {"f1"}}))
    evidence = dataclasses.replace(
        evidence, member_file_ids=frozenset({"f1", "orphan"}))
    built = _preview_binding()(None, evidence)
    counts = _branch_counts_for(built, evidence)
    branch = counts[built.parent.node_id]
    assert branch.unresolved_file_ids == ("orphan",)
    # And a child that placed its file reports none of its own.
    child = counts[built.nodes[0].node_id]
    assert child.unresolved_file_ids == ()


def test_evidence_gaps_stay_empty_because_nothing_produces_one(conn):
    """`BranchCounts.evidence_gap_file_ids` is `00`:99's third item and it has NO
    PRODUCER anywhere in `src/` — it is only ever fed `{}` here and literals in
    tests. Filling it from something that is not an evidence gap would be worse
    than leaving it: the user would read a number that means something else.

    This records the gap so it is known rather than silent, and it FAILS the day
    a producer appears without this call being updated.
    """
    evidence = _evidence(_level("subject", "subject", 0, {"PHYS1401": {"f1"}}))
    built = _preview_binding()(None, evidence)
    counts = _branch_counts_for(built, evidence)
    assert all(c.evidence_gap_file_ids == () for c in counts.values())

    from pathlib import Path

    src = Path(__file__).resolve().parents[2] / "src"
    naming_it = {
        module.name for module in src.rglob("*.py")
        if "evidence_gap" in module.read_text()
    }
    assert naming_it == {"health.py", "candidates.py"}, (
        "a producer for evidence gaps appeared; wire it into _counts_for_preview")
