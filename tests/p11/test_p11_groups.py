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

from tree_design.vocabulary import (
    BRANCH_BEARING_SHARED_POLICIES, MANDATORY_REVIEW, PRIMARY_HOME,
    REFERENCE_OR_ALIAS, SHARED_BRANCH, SHARED_MATERIAL_POLICIES,
)

from placement import vocabulary as v
from placement.groups import (
    AskOrAbstainSelectorRequired, ExcludedOutlier, GroupNotAcceptedInVersion,
    GroupPlan, InstitutionalDestinationRefused,
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


# --- the P10 -> P11 join: what makes an acceptance visible here -------------------
#
# §8.8 mints a NEW plan version for every recorded edit, so the version P11 is
# given -- P10's FROZEN one -- is never the version the review screen wrote into,
# and P10's chain does not descend from it. `accepted_group_as_of` asks as of the
# frozen version, so until something carried the acceptance across, §6.8's group
# pass refused every group: every file was placed alone, with no shared context and
# no explanation a user could act on.
#
# The carry is a DECISION and not a wider lookup. Approving the frozen plan IS the
# user accepting the groups in it, and `production.CorpusDecisions.approve_plan`
# is where that decision arrives. P11's read stays a read of ONE version -- looking
# at both would place files against groups the user never approved, which is the
# defect and not the fix.

def _p10_chain(conn, *versions: str) -> None:
    """P10's minted line of descent, root first, through P10's own writer.

    A hand-rolled `CREATE TABLE plan_versions` would be a copy that can drift from
    the schema the acceptance read actually walks. Written from the root down
    because `predecessor_id` carries a foreign key.
    """
    from tree_design.records import PlanVersion
    from tree_design.schema import create_tree_schema
    from tree_design.store import write_plan_version

    create_tree_schema(conn)
    predecessor = None
    for version in versions:
        write_plan_version(conn, PlanVersion(
            plan_version_id=version, predecessor_id=predecessor, state="draft",
            created_at=T0, cross_folder_moves=False, selection_id="sel-1"))
        predecessor = version


def test_an_acceptance_only_the_review_recorded_does_not_reach_p11(seeded):
    """The negative half, and the one that decides whether the fix is safe.

    `seed_accepted_columbia` records the acceptance at `plan-1`, which is the
    review's version. The frozen version below is on P10's own chain and descends
    from nothing the review touched, so the lineage walk `1d5063e` added inherits
    nothing -- correctly. A group the user has not approved in THIS plan is not a
    group P11 may place files against, however clearly they accepted it somewhere
    else.
    """
    _p10_chain(seeded, "plan-frozen-0", "plan-frozen-1")
    with pytest.raises(GroupNotAcceptedInVersion) as raised:
        accepted_group_as_of(seeded, group_id=GROUP_ID,
                             plan_version="plan-frozen-1")
    # And it says what it saw: the shared lifecycle state, which is what the group
    # IS and not what this version decided about it.
    assert SUPPORTED in str(raised.value)
    # The review's own record is untouched by any of this. §5.12: the accepted
    # groups stay separate from the tree, so editing the tree destroys nothing.
    assert accepted_group_as_of(seeded, group_id=GROUP_ID,
                                plan_version="plan-1").state == "accepted"


def test_the_acceptance_the_user_approved_is_the_one_p11_reads(seeded):
    """The positive half. Approving the frozen plan is what carries it across.

    Recorded through P9's own writer against the FROZEN version, because that is
    the version P11 asks about -- and it exists there because somebody decided it,
    not because the read was widened until it found one.
    """
    from grouping.acceptance import record_acceptance

    _p10_chain(seeded, "plan-frozen-0", "plan-frozen-1")
    record_acceptance(seeded, GroupAcceptance(
        acceptance_id="acc:plan-frozen-1:g-columbia",
        plan_version_id="plan-frozen-1", group_id=GROUP_ID, membership_id=None,
        acceptance="accepted", review_state="pending-review",
        user_edited_label="Columbia application", aliases=(),
        review_decision_ref=None, decided_by=USER, created_at=T0))

    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-frozen-1")
    assert accepted.state == "accepted"
    assert accepted.plan_version == "plan-frozen-1"
    # With its members, which is the whole point: §6.8 confirms one shared parent
    # and classifies beneath it, and a group with no memberships is four unrelated
    # file moves wearing one name.
    assert len(accepted.memberships) == 4
    # An earlier version of P10's own chain still has no opinion. The walk goes to
    # ancestors and never to descendants, so approving the frozen plan does not
    # retroactively approve the drafts it replaced.
    with pytest.raises(GroupNotAcceptedInVersion):
        accepted_group_as_of(seeded, group_id=GROUP_ID,
                             plan_version="plan-frozen-0")


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
    assert set(BRANCH_BEARING_SHARED_POLICIES) == {
        SHARED_BRANCH, PRIMARY_HOME, REFERENCE_OR_ALIAS}
    for policy in BRANCH_BEARING_SHARED_POLICIES:
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
    # The one place a literal spelling belongs: pinning P10's tuple against
    # §6.9's own words. Everywhere else P11 imports it.
    assert SHARED_MATERIAL_POLICIES == (
        "shared-branch", "primary-home", "reference-or-alias", "mandatory-review")


def test_p11_holds_no_second_copy_of_69s_policy_sets():
    """MINOR 6, by IDENTITY rather than by equality.

    "P10 owns the tree, so P10 names its node kinds. P11 carries these verbatim
    and publishes no parallel vocabulary." A local copy with the same four
    members passes every `==` in this file and every behavioural test above --
    and then drifts the day P10 adds a fifth policy or respells one, at which
    point a multi-home file matches no branch in `resolve_multi_home`. `is` is
    what separates carrying a set from re-deriving it.

    This set in particular decides whether a file that belongs in two places
    gets a home or gets asked about, which makes a silent disagreement between
    the two parts a wrong answer to the product's most-repeated question.
    """
    import placement.groups as groups
    from tree_design import vocabulary as p10

    assert groups.SHARED_MATERIAL_POLICIES is p10.SHARED_MATERIAL_POLICIES
    assert groups._BRANCH_BEARING is p10.BRANCH_BEARING_SHARED_POLICIES
    for name in ("SHARED_BRANCH", "PRIMARY_HOME", "REFERENCE_OR_ALIAS",
                 "MANDATORY_REVIEW"):
        assert getattr(groups, name) is getattr(p10, name), name


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

    It was marked `xfail(strict=True)` deliberately: it reported the gap on every
    run, and the day `place_group` landed it XPASSed -- which under `strict`
    turned the suite RED and forced the marker off. That is what happened. A gap
    that announces its own closure is the opposite of the four concepts that
    passed a green suite for weeks while connected to nothing.
    """
    assert _placement_sources_calling("group_plan_emitted"), (
        "nothing in src/placement/ emits group_plan_emitted")
    assert _placement_sources_calling("GroupPlan") - {"groups.py"}, (
        "nothing outside groups.py constructs a GroupPlan")


# The marker is gone because `pipeline.place_group` is the producer. It also
# WRITES `placement_group_plans`, which had no writer at all until it landed.
assert "pipeline.py" in _placement_sources_calling("group_plan_emitted")
