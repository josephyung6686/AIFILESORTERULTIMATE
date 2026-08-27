"""§6.8 one coherent plan; §6.9 never an arbitrary institution."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from grouping.vocabulary import (
    ENGINE_FLAGGED, MODEL_FLAGGED, NOT_FLAGGED, REJECTED, SUPPORTED,
    USER_ATTACHED, USER,
)
from grouping.records import GroupAcceptance

from placement import vocabulary as v
from placement.groups import (
    AskOrAbstainSelectorRequired, ExcludedOutlier, GroupNotAcceptedInVersion,
    GroupPlan, InstitutionalDestinationRefused, MANDATORY_REVIEW, PRIMARY_HOME,
    REFERENCE_OR_ALIAS, SHARED_BRANCH, SHARED_MATERIAL_POLICIES,
    SharedMaterialPolicyRequired, accepted_group_as_of, confirm_shared_parent,
    excluded_outlier_for, resolve_multi_home,
)
from p11.p9_fixtures import GROUP_ID, T0, seed_accepted_columbia
from p11.test_p11_records import _decision


@pytest.fixture()
def seeded(p11_conn):
    seed_accepted_columbia(p11_conn)
    return p11_conn


def _member(seeded, file_id):
    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")
    return next(m for m in accepted.memberships if m.file_id == file_id)


# --- acceptance, as of a plan version ---------------------------------------------

def test_acceptance_is_resolved_as_of_a_plan_version(seeded):
    # Through P9's OWN read. `accepted` is never stored on a group
    # (`grouping/vocabulary.py:31-32`), so asking `Group.state` would answer
    # `supported` in every version and P11 would place a group nobody accepted.
    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")
    assert accepted.state == "accepted"
    assert accepted.group_id == GROUP_ID
    assert accepted.plan_version == "plan-1"
    assert len(accepted.memberships) == 4
    # plan-2 holds no opinion, so P9 falls back to the SHARED state. It is not
    # an empty result and it is not `accepted`; P11 refuses rather than reading
    # the fallback as consent.
    with pytest.raises(GroupNotAcceptedInVersion) as raised:
        accepted_group_as_of(seeded, group_id=GROUP_ID, plan_version="plan-2")
    # The refusal names the state it actually saw, so a reader can tell "this
    # version said no" from "this version said nothing".
    assert SUPPORTED in str(raised.value)


def test_a_version_that_rejected_the_group_is_refused_and_says_so(seeded):
    # The negative twin of the fallback case. Without it, `GroupNotAccepted`
    # could be firing only on absence and every explicit rejection would place.
    from grouping.acceptance import record_acceptance

    record_acceptance(seeded, GroupAcceptance(
        acceptance_id="acc-2", plan_version_id="plan-3", group_id=GROUP_ID,
        membership_id=None, acceptance=REJECTED, review_state="user-rejected",
        user_edited_label=None, aliases=(), review_decision_ref=None,
        decided_by=USER, created_at=T0))
    with pytest.raises(GroupNotAcceptedInVersion) as raised:
        accepted_group_as_of(seeded, group_id=GROUP_ID, plan_version="plan-3")
    assert REJECTED in str(raised.value)


def test_the_shared_state_is_never_mistaken_for_acceptance(seeded):
    from grouping.acceptance import group_state_as_of

    assert group_state_as_of(seeded, group_id=GROUP_ID,
                             plan_version_id="plan-2") == SUPPORTED


# --- the shared parent, confirmed first --------------------------------------------

def test_the_shared_parent_is_confirmed_before_any_member_is_classified():
    # §6.8's ordering: confirm the parent, then classify beneath it. A member
    # placed first would be placed against no shared context at all.
    parent = confirm_shared_parent(
        {"f-essay": "n-columbia", "f-transcript": "n-columbia"},
        policy=SHARED_BRANCH)
    assert parent == "n-columbia"


def test_members_disagreeing_on_the_parent_confirm_none():
    assert confirm_shared_parent(
        {"f-essay": "n-columbia", "f-transcript": "n-duke"},
        policy=SHARED_BRANCH) is None


def test_a_majority_never_carries_the_parent():
    # Two against one is still disagreement. A majority vote would place the
    # minority member where its own evidence does not reach, which is §6.12's
    # "moved because it resembles a folder".
    assert confirm_shared_parent(
        {"a": "n-columbia", "b": "n-columbia", "c": "n-duke"},
        policy=SHARED_BRANCH) is None


def test_confirming_a_parent_under_no_policy_fails_closed():
    for absent in ("", None, "shared_branch"):
        with pytest.raises(SharedMaterialPolicyRequired):
            confirm_shared_parent({"a": "n-1"}, policy=absent)


# --- outliers, excluded and explained ---------------------------------------------

def test_a_conflicting_member_is_excluded_and_says_why(seeded):
    # Done-means 8: the conflicting-institution essay is an outlier with its
    # conflicting fact recorded, routed to a legal branch or the review queue.
    outlier = _member(seeded, "f-duke-essay")
    assert outlier.outlier_flag == ENGINE_FLAGGED
    assert outlier.conflicts
    assert outlier.conflicts[0].kind == "target_school"
    assert set(outlier.conflicts[0].competing_values) == {"Columbia", "Duke"}
    excluded = excluded_outlier_for(outlier, routed_node_id=None)
    assert excluded.file_id == "f-duke-essay"
    assert excluded.routed_to == v.ROUTED_TO_REVIEW_QUEUE
    assert excluded.node_id is None
    assert "Columbia" in excluded.conflicting_fact
    assert "Duke" in excluded.conflicting_fact
    assert excluded.evidence_ref == "obs-f-duke-essay"


def test_an_outlier_routed_to_a_node_names_it(seeded):
    # The negative twin of the review-queue case: without it `routed_to` could be
    # the constant `review_queue` and every assertion above would still pass.
    excluded = excluded_outlier_for(_member(seeded, "f-duke-essay"),
                                    routed_node_id="n-duke")
    assert excluded.routed_to == v.ROUTED_TO_NODE
    assert excluded.node_id == "n-duke"


def test_a_member_p9_did_not_flag_is_never_excluded_by_p11(seeded):
    # P9 owns the flag (`Membership.outlier_flag`). P11 records what P9 found and
    # does not re-decide belonging, so manufacturing an exclusion for an unflagged
    # member -- which would be reported as "flagged by P9" -- is refused.
    ordinary = _member(seeded, "f-essay")
    assert ordinary.outlier_flag == NOT_FLAGGED
    with pytest.raises(ValueError) as raised:
        excluded_outlier_for(ordinary, routed_node_id=None)
    assert "f-essay" in str(raised.value)


def test_a_flagged_member_with_no_conflict_is_still_excluded(seeded):
    # The negative twin of the guard above, and the case that proves the guard
    # keys on the FLAG and not on the conflicts: a `model-flagged` member carries
    # no engine conflict and must still reach an exclusion with a stated reason.
    import dataclasses

    flagged = dataclasses.replace(_member(seeded, "f-essay"),
                                  outlier_flag=MODEL_FLAGGED, conflicts=())
    excluded = excluded_outlier_for(flagged, routed_node_id=None)
    assert excluded.file_id == "f-essay"
    assert excluded.conflicting_fact


def test_an_outlier_record_cannot_disagree_with_itself():
    with pytest.raises(ValueError):
        ExcludedOutlier(file_id="f", conflicting_fact="c", evidence_ref="e",
                        routed_to=v.ROUTED_TO_NODE, node_id=None)
    with pytest.raises(ValueError):
        ExcludedOutlier(file_id="f", conflicting_fact="c", evidence_ref="e",
                        routed_to=v.ROUTED_TO_REVIEW_QUEUE, node_id="n-1")
    with pytest.raises(v.OutOfVocabulary):
        ExcludedOutlier(file_id="f", conflicting_fact="c", evidence_ref="e",
                        routed_to="somewhere_else", node_id=None)


def test_a_user_attached_member_still_reaches_group_placement(seeded):
    # M12 and P9 invariant 5: an unreadable file's ONLY basis is user-attached,
    # and those files reach §6.8. Dropping them here would lose them silently.
    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")
    bases = {m.basis for m in accepted.memberships}
    assert USER_ATTACHED in bases


# --- one plan, not several file moves ----------------------------------------------

def test_a_group_plan_binds_every_member_decision_to_one_id():
    plan = GroupPlan(
        group_plan_id="gp-1", plan_version="plan-1", group_id=GROUP_ID,
        shared_parent_node_id="n-columbia",
        member_decisions=(_decision(decision_id="d1", group_plan_id="gp-1"),
                          _decision(decision_id="d2", group_plan_id="gp-1")),
        excluded_outliers=())
    assert plan.shared_parent_node_id == "n-columbia"
    # The two refusals are pinned to their OWN messages. An empty plan also
    # fails the shared-id check, so without this each guard hides the other:
    # deleting either one alone would leave a bare `pytest.raises(ValueError)`
    # green and only one guard doing all the work.
    with pytest.raises(ValueError) as empty:
        GroupPlan(group_plan_id="gp-1", plan_version="plan-1", group_id=GROUP_ID,
                  shared_parent_node_id=None, member_decisions=(),
                  excluded_outliers=())
    assert "no member decisions" in str(empty.value)
    with pytest.raises(ValueError) as mismatched:
        GroupPlan(group_plan_id="gp-1", plan_version="plan-1", group_id=GROUP_ID,
                  shared_parent_node_id=None,
                  member_decisions=(_decision(group_plan_id="gp-other"),),
                  excluded_outliers=())
    assert "shares this plan's id" in str(mismatched.value)


def test_a_file_is_never_both_a_member_and_an_excluded_outlier():
    # One plan cannot say a file was placed with the group and left out of it.
    from placement.records import Subject

    member = _decision(decision_id="d1", group_plan_id="gp-1",
                       subject=Subject(kind=v.FILE, file_id="f-essay",
                                       content_hash="h", group_id=None,
                                       member_file_ids=()))
    outside = ExcludedOutlier(file_id="f-duke-essay", conflicting_fact="c",
                              evidence_ref="e",
                              routed_to=v.ROUTED_TO_REVIEW_QUEUE, node_id=None)
    inside = ExcludedOutlier(file_id="f-essay", conflicting_fact="c",
                             evidence_ref="e",
                             routed_to=v.ROUTED_TO_REVIEW_QUEUE, node_id=None)
    ok = GroupPlan(group_plan_id="gp-1", plan_version="plan-1", group_id=GROUP_ID,
                   shared_parent_node_id="n-columbia",
                   member_decisions=(member,), excluded_outliers=(outside,))
    assert ok.excluded_outliers[0].file_id == "f-duke-essay"
    with pytest.raises(ValueError):
        GroupPlan(group_plan_id="gp-1", plan_version="plan-1", group_id=GROUP_ID,
                  shared_parent_node_id="n-columbia",
                  member_decisions=(member,), excluded_outliers=(inside,))


# --- §6.9, the multi-home rule ------------------------------------------------------

def test_a_shared_branch_is_preferred_when_one_is_approved():
    outcome, payload = resolve_multi_home(
        candidate_node_ids=("n-columbia", "n-duke"),
        shared_material_policy=SHARED_BRANCH, shared_branch_node_id="n-apps",
        ask_or_abstain=None)
    assert outcome == v.PLACE
    assert payload == "n-apps"


def test_the_three_branch_bearing_policies_place_and_mandatory_review_does_not():
    # The discriminating twin for the branch-bearing set. With all four members
    # in it, every assertion above still passes and `mandatory-review` silently
    # stops being mandatory.
    for policy in (SHARED_BRANCH, PRIMARY_HOME, REFERENCE_OR_ALIAS):
        outcome, payload = resolve_multi_home(
            candidate_node_ids=("n-columbia", "n-duke"),
            shared_material_policy=policy, shared_branch_node_id="n-apps",
            ask_or_abstain=None)
        assert (outcome, payload) == (v.PLACE, "n-apps"), policy
    outcome, payload = resolve_multi_home(
        candidate_node_ids=("n-columbia", "n-duke"),
        shared_material_policy=MANDATORY_REVIEW, shared_branch_node_id="n-apps",
        ask_or_abstain=lambda ids: v.ASK_USER)
    assert outcome == v.ASK_USER


def test_with_no_shared_branch_the_selector_decides_and_is_injected():
    # SPEC Open question 6 is open: the design permits abstain OR ask and gives
    # no selector. Building one here would answer it in code.
    with pytest.raises(AskOrAbstainSelectorRequired):
        resolve_multi_home(candidate_node_ids=("n-columbia", "n-duke"),
                           shared_material_policy=MANDATORY_REVIEW,
                           shared_branch_node_id=None, ask_or_abstain=None)
    outcome, payload = resolve_multi_home(
        candidate_node_ids=("n-columbia", "n-duke"),
        shared_material_policy=MANDATORY_REVIEW, shared_branch_node_id=None,
        ask_or_abstain=lambda ids: v.ASK_USER)
    assert outcome == v.ASK_USER
    assert payload == ("n-columbia", "n-duke")


def test_abstaining_names_no_shared_branch_as_the_reason():
    outcome, payload = resolve_multi_home(
        candidate_node_ids=("n-columbia", "n-duke"),
        shared_material_policy=MANDATORY_REVIEW, shared_branch_node_id=None,
        ask_or_abstain=lambda ids: v.ABSTAIN)
    assert outcome == v.ABSTAIN
    assert payload == v.NO_SHARED_BRANCH


def test_a_selector_answering_anything_else_is_refused():
    # A third answer would be a placement wearing a selector's name.
    for answer in (v.PLACE, "n-columbia", None):
        with pytest.raises(AskOrAbstainSelectorRequired):
            resolve_multi_home(candidate_node_ids=("n-columbia", "n-duke"),
                               shared_material_policy=MANDATORY_REVIEW,
                               shared_branch_node_id=None,
                               ask_or_abstain=lambda ids, a=answer: a)


def test_one_institution_is_never_chosen_over_another():
    # Done-means 9, stated as the thing that must not be reachable: over every
    # policy, every selector answer and both branch states, no argument to
    # `resolve_multi_home` returns one of the competing institutions.
    candidates = ("n-columbia", "n-duke")
    for policy in SHARED_MATERIAL_POLICIES:
        for branch in (None, "n-apps"):
            for selector in (lambda ids: v.ASK_USER, lambda ids: v.ABSTAIN):
                outcome, payload = resolve_multi_home(
                    candidate_node_ids=candidates,
                    shared_material_policy=policy,
                    shared_branch_node_id=branch, ask_or_abstain=selector)
                assert payload not in candidates, (policy, branch, outcome)


def test_a_competing_institution_cannot_be_smuggled_in_as_the_shared_branch():
    # The one remaining way to return an institution: hand one in as the shared
    # branch. §6.9's rule is about the OUTCOME, so the refusal names the value.
    with pytest.raises(InstitutionalDestinationRefused) as raised:
        resolve_multi_home(candidate_node_ids=("n-columbia", "n-duke"),
                           shared_material_policy=SHARED_BRANCH,
                           shared_branch_node_id="n-duke", ask_or_abstain=None)
    assert "n-duke" in str(raised.value)


def test_a_single_candidate_is_not_a_multi_home_question():
    # Abstaining `no_shared_branch` over a file with exactly one home would
    # report a competition that never happened.
    for candidates in ((), ("n-columbia",)):
        with pytest.raises(ValueError):
            resolve_multi_home(candidate_node_ids=candidates,
                               shared_material_policy=MANDATORY_REVIEW,
                               shared_branch_node_id=None,
                               ask_or_abstain=lambda ids: v.ABSTAIN)


def test_a_missing_shared_material_policy_fails_closed():
    with pytest.raises(SharedMaterialPolicyRequired):
        resolve_multi_home(candidate_node_ids=("n-columbia", "n-duke"),
                           shared_material_policy="", shared_branch_node_id=None,
                           ask_or_abstain=lambda ids: v.ABSTAIN)


def test_an_underscored_policy_raises_rather_than_falling_through():
    # P10 spells its node vocabulary with hyphens. An underscored value would
    # match no branch, and without a raise every multi-home file would fall out
    # of the bottom of the function with nothing to say so. The refusal names
    # the value, so the hyphen is visible in the message.
    with pytest.raises(SharedMaterialPolicyRequired) as raised:
        resolve_multi_home(candidate_node_ids=("n-columbia", "n-duke"),
                           shared_material_policy="shared_branch",
                           shared_branch_node_id="n-apps", ask_or_abstain=None)
    assert "shared_branch" in str(raised.value)


def test_the_four_policies_are_69s_own_four():
    assert SHARED_MATERIAL_POLICIES == (
        "shared-branch", "primary-home", "reference-or-alias", "mandatory-review")


def test_the_alias_convention_is_not_a_filesystem_instruction():
    # SPEC Open question 7 is open and threatens P12's contract: if an alias
    # means a symlink it collides with §8.3's rule against following one during
    # mutation. P11 names a node either way and produces no link.
    outcome, payload = resolve_multi_home(
        candidate_node_ids=("n-columbia", "n-duke"),
        shared_material_policy=REFERENCE_OR_ALIAS,
        shared_branch_node_id="n-apps", ask_or_abstain=None)
    assert outcome == v.PLACE
    assert payload == "n-apps"
    import placement.groups as groups

    source = Path(groups.__file__).read_text(encoding="utf-8")
    for banned in ("symlink", "os.symlink", "hardlink", "shutil"):
        assert banned not in source


# --- the fixture stays in the tests -------------------------------------------------

def _fixture_imports(tree) -> list[str]:
    # `tests/` carries no top-level `__init__.py`, so pytest puts `tests/` on
    # `sys.path` and the fixture packages are importable as `p11.*`, never as
    # `tests.p11.*`. The guard names the live spelling, because a guard checking a
    # prefix nothing produces catches nothing.
    banned = ("p11", "p10", "p13", "tests")
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in banned:
                found.append(f"{node.lineno}: from {node.module}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in banned:
                    found.append(f"{node.lineno}: import {alias.name}")
    return found


def test_placement_never_imports_a_test_fixture():
    root = Path(__file__).resolve().parents[2] / "src" / "placement"
    paths = sorted(root.glob("*.py"))
    assert len(paths) > 1
    for path in paths:
        offences = _fixture_imports(ast.parse(path.read_text(encoding="utf-8")))
        assert not offences, f"{path.name}: {offences}"


def test_the_fixture_guard_can_actually_fire():
    # The negative twin. A guard whose predicate matches nothing passes over a
    # source tree that imports fixtures everywhere, and this proves it does not.
    offending = "from p11.p9_fixtures import GROUP_ID\nimport tests.p11.conftest\n"
    assert len(_fixture_imports(ast.parse(offending))) == 2


# --- the gap this task leaves open, tracked rather than described -------------------

def _placement_sources_calling(function_name: str) -> set[str]:
    """Modules in `src/placement/` that CALL `function_name`, by AST, not by grep.

    A reference is not a call and an import is not a use: the four concepts this
    codebase shipped fully-tested and connected to nothing all had references.
    """
    root = Path(__file__).resolve().parents[2] / "src" / "placement"
    callers = set()
    for path in sorted(root.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = (func.attr if isinstance(func, ast.Attribute)
                    else func.id if isinstance(func, ast.Name) else None)
            if name == function_name:
                callers.add(path.name)
    return callers


def test_the_group_plan_event_has_a_producer_somewhere_in_placement():
    """The one thing this task builds that nothing yet consumes.

    `GroupPlan`, `placement_events.group_plan_emitted` and the
    `placement_group_plans` table are all live and all unreachable: no module in
    `src/placement/` constructs a `GroupPlan`, writes that table or fires that
    event. The owed consumer is the phase pipeline's `place_group`, which is not
    built.

    This is marked `xfail(strict=True)` deliberately. It reports the gap on every
    run today, and the day `place_group` lands it XPASSes -- which under `strict`
    turns the suite RED and forces the marker off. A gap that announces its own
    closure is the opposite of the four concepts that passed a green suite for
    weeks while connected to nothing.
    """
    assert _placement_sources_calling("group_plan_emitted"), (
        "nothing in src/placement/ emits group_plan_emitted")
    assert _placement_sources_calling("GroupPlan") - {"groups.py"}, (
        "nothing outside groups.py constructs a GroupPlan")


test_the_group_plan_event_has_a_producer_somewhere_in_placement = pytest.mark.xfail(
    strict=True,
    reason="P11 Task 18's `place_group` is unbuilt; GroupPlan has no producer. "
           "This XPASSes and fails the suite the moment one appears.",
)(test_the_group_plan_event_has_a_producer_somewhere_in_placement)
