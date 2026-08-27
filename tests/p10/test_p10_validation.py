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
    # V5 asks about the VALUE STRING. An account identifier as a folder name
    # discloses the account; a course code does not. The judgement is the
    # caller's because nothing upstream classifies a value.
    value_discloses_protected_material=lambda field_ref, value: (
        field_ref == "account_identifier"),
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
                   value_discloses_protected_material=CHECK_ARGS[
                       "value_discloses_protected_material"])


def test_v5_a_folder_level_built_from_protected_values_fails(limits):
    """The real V5: the VALUES themselves are the disclosure. An account number
    as a folder name publishes the account to the filesystem and to every prompt
    that names a destination — and it does so whether or not any file under it
    was classified sensitive."""
    candidate = _candidate([
        _level("subject", "subject", 0, ("PHYS1401", "CHEM1101")),
        _level("account", "account_identifier", 1, ("4471", "9920")),
    ])
    report = run_checks(candidate, report_id="vr_1", limits=limits, **CHECK_ARGS)
    assert [f.check for f in report.failures] == ["V5"]
    assert report.failures[0].affected == ("4471", "9920")


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


# --- V5 refuses on the wrong thing ------------------------------------------------

PROTECTED = frozenset({"highly_sensitive_credential_bearing"})


def test_one_protected_file_under_a_value_does_not_condemn_the_folder_name(limits):
    """THE DEFECT, and it fails in the most damaging direction: the user loses
    the ORGANISATION, not the protection.

    `materialise` builds `handling_classes_by_value` as the UNION of every member
    file's class, so ONE protected file under a value poisons the value STRING,
    and V5 then refuses the whole composition. A passport scan filed under
    `Columbia` makes the string "Columbia" carry a protected class and the branch
    is destroyed — with an explanation that blames the university's name.

    Verified over the real seeded corpus:
        every file ordinary -> V5 silent
        ONE protected file  -> V5: affected ('Columbia', 'BUSIB 4300')

    `00`:120 names passport scans and visas as material `Protected Records`
    represents, and `00`:101 asks tree health to show "where sensitive material
    has been ISOLATED". Isolate the FILE, build the BRANCH. These are exactly the
    cases the product owner asked about: a passport for a visa application, a
    medical letter for exam accommodations, a divorce decree in a mortgage
    bundle. Every one of them currently destroys the branch that needs it.
    """
    candidate = _candidate([
        _level("subject", "subject", 0, ("Columbia",),
               counts={"Columbia": 3},
               classes={"Columbia": frozenset({
                   "personal_non_sensitive",
                   "highly_sensitive_credential_bearing"})}),
    ])
    report = run_checks(
        candidate, report_id="vr", limits=limits,
        collector_field_keys=frozenset({"author"}),
        value_discloses_protected_material=lambda field_ref, value: False)
    v5 = [f for f in report.failures if f.check == "V5"]
    assert v5 == [], (
        "a protected FILE under the value refused the branch; the protected "
        "thing is the file, and 'Columbia' is a university's name")


def test_a_value_string_that_is_itself_protected_material_is_still_refused(limits):
    """The discriminator. Without this the fix above is a deletion.

    `00`:97 lists V5 among the STRUCTURAL faults a proposed template may have —
    "does not repeat a parent dimension, create meaningless one-child levels,
    exceed practical depth limits, use an author or organization merely as a
    collector, expose protected information, or produce empty branches". It is a
    claim about the DIMENSION, not about the files underneath it. A level built
    from a field whose values are themselves disclosing — a folder named after a
    medical condition — is the real V5, and it must stay refused.
    """
    candidate = _candidate([
        _level("diagnosis", "medical_condition", 0, ("Type 1 Diabetes",),
               counts={"Type 1 Diabetes": 2},
               classes={"Type 1 Diabetes": frozenset({"personal_non_sensitive"})}),
    ])
    report = run_checks(
        candidate, report_id="vr", limits=limits,
        collector_field_keys=frozenset({"author"}),
        value_discloses_protected_material=lambda field_ref, value: (
            field_ref == "medical_condition"))
    assert [f.check for f in report.failures if f.check == "V5"] == ["V5"]
    assert "Type 1 Diabetes" in report.failures[0].affected


def test_v5_refuses_to_guess_when_nothing_says_which_values_disclose(limits):
    """No upstream signal classifies a VALUE. P6 classifies FIELDS
    (`destination_eligible`) and P7 classifies FILES (`handling_class`); nothing
    classifies the string a folder would be named after. So the judgement is
    injected, like `collector_field_keys` and `protected_handling_classes`
    already are, and absent means refuse rather than guess — a wrong guess in
    this direction is the defect being fixed."""
    candidate = _candidate([_level("subject", "subject", 0, ("Columbia",))])
    with pytest.raises(ConfigurationRequired):
        run_checks(candidate, report_id="vr", limits=limits,
                   collector_field_keys=frozenset({"author"}),
                   value_discloses_protected_material=None)
