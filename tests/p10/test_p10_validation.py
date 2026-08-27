"""P10 Task 9 — one failing fixture per §5.7 check, over a materialised branch.

These are P10's V1-V6. P1's V1-V4 are §8.2's checksum verification points and
share nothing with these but the letter.

The checks run over a candidate MATERIALISED against the branch's real values,
which is why they are P10's and not P8's: §5.7 places them on "the engine" that
validates a generated template against the accepted group, and the accepted
group is material only P10 holds.
"""
from __future__ import annotations

import pytest

from database_agent.budget import set_ceiling
from tree_design.config import ConfigurationRequired, tree_limits
from tree_design.validation import (
    MaterialisedCandidate,
    MaterialisedLevel,
    run_checks,
)


@pytest.fixture()
def limits(conn):
    set_ceiling(conn, "tree.max_folder_proposals_and_depth", 4)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    return tree_limits(
        conn, excessive_depth_warning=3, tiny_folder_max_files=2,
        tiny_folder_count_warning=8,
        materially_improves_retrieval=lambda preview: None)


def _level(role, field, index, values, counts=None, classes=None,
           metadata_only=False):
    return MaterialisedLevel(
        dimension_role=role, field_ref=field, order_index=index,
        values=tuple(values), metadata_only=metadata_only,
        members_by_value=dict(counts or {v: len(values) + 1 for v in values}),
        handling_classes_by_value=dict(
            classes or {v: frozenset({"personal_non_sensitive"}) for v in values}),
    )


def _candidate(levels, *, ancestors=(), depth=0, members=("f1", "f2", "f3")):
    return MaterialisedCandidate(
        branch_node_id="n_branch", ancestor_field_refs=tuple(ancestors),
        ancestor_depth=depth, levels=tuple(levels),
        member_file_ids=frozenset(members),
    )


CHECK_ARGS = dict(
    collector_field_keys=frozenset({"target_school", "client", "authored_by"}),
    protected_handling_classes=frozenset({
        "sensitive_personal", "highly_sensitive_credential_bearing"}),
)


def test_a_healthy_candidate_passes_all_six(limits):
    candidate = _candidate([
        _level("subject", "subject", 0, ("PHYS1401", "CHEM1101")),
        _level("artifact_kind", "work_type", 1, ("Homework", "Exam")),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert report.accepted
    assert report.passed == ("V1", "V2", "V3", "V4", "V5", "V6")


def test_v1_a_level_repeating_a_parent_dimension_fails(limits):
    candidate = _candidate(
        [_level("subject", "subject", 0, ("PHYS1401", "CHEM1101"))],
        ancestors=("subject",), depth=1)
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert not report.accepted
    assert [f.check for f in report.failures] == ["V1"]
    assert "subject" in report.failures[0].affected


def test_v1_also_catches_a_repeat_within_the_candidate_itself(limits):
    candidate = _candidate([
        _level("subject", "subject", 0, ("PHYS1401", "CHEM1101")),
        _level("course", "subject", 1, ("PHYS1401", "CHEM1101")),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V1"]


def test_v2_a_level_producing_exactly_one_child_is_meaningless(limits):
    candidate = _candidate([_level("subject", "subject", 0, ("PHYS1401",))])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V2"]
    assert "PHYS1401" in report.failures[0].reason


def test_v3_depth_is_measured_against_configuration_never_a_constant(limits):
    levels = [_level(f"r{i}", f"f{i}", i, (f"a{i}", f"b{i}")) for i in range(4)]
    candidate = _candidate(levels, ancestors=("root",), depth=2)
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V3"]
    assert str(limits.max_folder_proposals_and_depth) in report.failures[0].reason


def test_v3_cannot_run_without_a_configured_depth(conn):
    """SPEC open question 1: §5.7 forbids exceeding "practical depth limits" and
    no value is given. The check is unimplementable until one is set, and this
    is what "unimplementable" looks like — a refusal, not a guess."""
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    with pytest.raises(ConfigurationRequired):
        tree_limits(conn, excessive_depth_warning=3, tiny_folder_max_files=2,
                    tiny_folder_count_warning=8,
                    materially_improves_retrieval=lambda p: None)


def test_v4_an_organization_used_merely_as_a_collector_fails(limits):
    """§3.8: "A folder should not become a collection point for everything
    produced by the same person or organization." A branch whose only level is
    such a role is exactly that collection point."""
    candidate = _candidate(
        [_level("counterpart", "target_school", 0, ("Columbia", "Duke"))])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V4"]


def test_v4_permits_a_collector_role_that_is_not_the_whole_branch(limits):
    candidate = _candidate([
        _level("counterpart", "target_school", 0, ("Columbia", "Duke")),
        _level("document_kind", "application_document_type", 1,
               ("Essay", "Transcript")),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert report.accepted


def test_v4_needs_the_collector_set_and_invents_none(limits):
    candidate = _candidate(
        [_level("counterpart", "target_school", 0, ("Columbia", "Duke"))])
    with pytest.raises(ConfigurationRequired):
        run_checks(candidate, report_id="vr_1", limits=limits,
                   collector_field_keys=frozenset(),
                   protected_handling_classes=CHECK_ARGS["protected_handling_classes"])


def test_v5_a_folder_level_built_from_protected_values_fails(limits):
    candidate = _candidate([
        _level("subject", "subject", 0, ("PHYS1401", "CHEM1101")),
        _level("account", "account_identifier", 1, ("4471", "9920"), classes={
            "4471": frozenset({"highly_sensitive_credential_bearing"}),
            "9920": frozenset({"personal_non_sensitive"}),
        }),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V5"]
    assert "4471" in report.failures[0].affected


def test_v5_permits_a_metadata_only_role_over_the_same_values(limits):
    """§5.4: a metadata-only role never becomes a folder level, so it cannot put
    a protected value in a folder name."""
    candidate = _candidate([
        _level("subject", "subject", 0, ("PHYS1401", "CHEM1101")),
        _level("account", "account_identifier", 1, ("4471",), metadata_only=True,
               classes={"4471": frozenset({"highly_sensitive_credential_bearing"})}),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert report.accepted


def test_v6_a_value_with_no_member_is_an_empty_branch(limits):
    candidate = _candidate([
        _level("subject", "subject", 0, ("PHYS1401", "CHEM1101", "BIOL2000"),
               counts={"PHYS1401": 4, "CHEM1101": 2, "BIOL2000": 0}),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V6"]
    assert report.failures[0].affected == ("BIOL2000",)


def test_uneven_depth_is_never_a_failure(limits):
    """§5.8: no validation rule may require sibling subtrees to have equal
    depth, and no branch is required to realise every dimension of its
    template."""
    shallow = _candidate([_level("subject", "subject", 0, ("PHYS1401", "CHEM1101"))])
    deep = _candidate([
        _level("subject", "subject", 0, ("PHYS1401", "CHEM1101")),
        _level("artifact_kind", "work_type", 1, ("Homework", "Exam")),
    ])
    assert run_checks(shallow, report_id="a", limits=limits, **CHECK_ARGS).accepted
    assert run_checks(deep, report_id="b", limits=limits, **CHECK_ARGS).accepted


def test_internal_heterogeneity_alone_is_never_a_rejection(limits):
    """§5.6: "The template is a recommendation mechanism, not a rule that erases
    purposeful heterogeneity." A purpose packet holding a transcript, an ID, an
    essay and a certificate is a valid branch."""
    candidate = _candidate([
        _level("document_kind", "application_document_type", 0,
               ("Transcript", "ID", "Personal statement", "Certificate")),
    ], members=("t", "i", "p", "c"))
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert report.accepted


def test_every_failure_names_its_evidence_and_carries_no_score(limits):
    candidate = _candidate([_level("subject", "subject", 0, ("PHYS1401",))])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    failure = report.failures[0]
    assert failure.reason and failure.affected
    assert not any(
        token in failure.reason.lower()
        for token in ("confidence", "score", "probability", "%")
    )


def test_v1_does_not_mistake_two_template_local_levels_for_a_repeat(limits):
    """Contract W5 gave a template-local level `field_ref = None`, and V1 compared
    levels by `field_ref`. Two DIFFERENT local roles both read as None, so the
    second one looked like a repeat of the first and every two-level novel-domain
    branch failed V1 — a check firing on a difference it could not see.

    A level's identity is its field when it has one and its ROLE when it does
    not, which is exactly the pairing `ResolvedDimension` already enforces.
    """
    candidate = _candidate([
        _level("matter", None, 0, ("Matter A", "Matter B")),
        _level("stage", None, 1, ("Filed", "Served")),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert report.accepted, [f.reason for f in report.failures]


def test_v1_still_catches_two_local_levels_that_repeat_one_role(limits):
    """The guard must keep working for the case it exists for."""
    candidate = _candidate([
        _level("matter", None, 0, ("Matter A", "Matter B")),
        _level("matter", None, 1, ("Matter A", "Matter B")),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V1"]
    assert "matter" in report.failures[0].affected
